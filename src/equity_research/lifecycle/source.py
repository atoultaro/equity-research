"""Strict parsing of four alert sections; source order is never price-derived."""

from copy import deepcopy
from datetime import timedelta
from decimal import Decimal
import re

from ..events.model import timestamp
from ..ingestion.storage import digest

CLOSED = ("AAPL", "CLMT", "TEVA", "CAT", "T", "ASST", "AAOI", "AMD", "ANET", "SNDK", "GME", "SNOW")
OPEN = ("CDE", "ELF", "HUM", "SIG", "OMER", "ABBV", "CNQ", "EBAY", "GTLB", "MMM", "SAIL", "SLB", "GE", "SCCO")
UNIVERSE = CLOSED + OPEN
EXCLUDED = ("PLTR", "PEP")
SECTIONS = {"Added": "OPEN_NEW_POSITION", "Stop Changed": "STOP_CHANGED", "Setup Changed": "SETUP_CHANGED", "Dropped": "DROPPED"}
PATTERNS = {
    "OPEN_NEW_POSITION": r"([A-Z]+) added (long|short) with stop ([0-9]+\.[0-9]+)",
    "STOP_CHANGED": r"([A-Z]+) stop moved to ([0-9]+\.[0-9]+) from ([0-9]+\.[0-9]+)",
    "SETUP_CHANGED": r"([A-Z]+) setup changed to (long|short)( \(underway\))? from (long|short)( \(underway\))?",
    "DROPPED": r"([A-Z]+) dropped from (long|short)( \(underway\))?"}


def effective_time(alert, allow_email_bound=False):
    if alert["published_at"]:
        t = timestamp(alert["published_at"])
        precision = alert["publication_precision"]
        if precision == "MINUTE":
            t = t.replace(second=0, microsecond=0)+timedelta(minutes=1)
        elif precision != "SECOND":
            raise ValueError("explicit publication precision required")
        return t.isoformat(), "PUBLICATION_TIME_CONSERVATIVE_BOUND"
    if allow_email_bound and alert.get("email_received_at"):
        return timestamp(alert["email_received_at"]).isoformat(), "EMAIL_AVAILABILITY_BOUND_NOT_EXACT_PUBLICATION"
    return None, "UNRESOLVED_PUBLICATION_TIME"


def parse_alerts(record, *, allow_email_bound=False, require_seven=True):
    if record.get("schema_version") != "grimes_alerts_v1" or record.get("origin") not in {"connected_gmail", "operator", "synthetic"}:
        raise ValueError("versioned alert input and explicit origin required")
    alerts = record["alerts"]
    if require_seven and len(alerts) != 7:
        raise ValueError("all seven original alerts required")
    seen, events, excluded, commentary = set(), [], [], []
    previous = None
    for i, alert in enumerate(alerts):
        if (alert["alert_id"] in seen or alert["source_sequence"] != i or not alert["text"]
                or not alert["original_publication_display"] or not alert["source_reference"]):
            raise ValueError("unique, ordered, verbatim alert bodies and publication metadata required")
        seen.add(alert["alert_id"])
        effective, clock_kind = effective_time(alert, allow_email_bound)
        if effective:
            if previous and timestamp(effective) < previous:
                raise ValueError("source order conflicts with effective-time evidence")
            previous = timestamp(effective)
        section, found, before, offset = None, [], [], 0
        for number, raw in enumerate(alert["text"].splitlines(keepends=True), 1):
            line = raw.strip()
            header = next((name for name in SECTIONS if re.fullmatch(re.escape(name)+r"_+", line)), None)
            if header:
                section = SECTIONS[header]
                found.append(header)
            elif line == "---":
                break
            elif section is None:
                before.append(raw)
            elif line and line != "None":
                match = re.fullmatch(PATTERNS[section], line)
                if not match:
                    raise ValueError(f"unparsed source action at {alert['alert_id']} line {number}")
                symbol = match[1]
                loc = {"alert_id": alert["alert_id"], "line": number, "character_offset": offset,
                    "alert_text_sha256": digest(alert["text"].encode()), "source_text": line}
                if symbol in EXCLUDED:
                    excluded.append({"symbol": symbol, **loc, "reason": "EXPLICITLY_OUTSIDE_FROZEN_26_STOCK_UNIVERSE"})
                else:
                    if symbol not in UNIVERSE:
                        raise ValueError(f"symbol outside frozen universe: {symbol}")
                    event = {"event_id": f"{alert['alert_id']}:line-{number}", "source_order": len(events),
                        "type": section, "symbol": symbol, "attribution": "EXPERT_REPORTED",
                        "published_at": alert["published_at"], "publication_display": alert["original_publication_display"],
                        "effective_at": effective, "effective_clock": clock_kind, "source": loc}
                    if section == "OPEN_NEW_POSITION":
                        event.update(direction=match[2].upper(), stop=match[3])
                    elif section == "STOP_CHANGED":
                        event.update(stop=match[2], previous_stop=match[3])
                    elif section == "SETUP_CHANGED":
                        if match[2] != match[4]:
                            raise ValueError("setup change cannot silently reverse a position")
                        event.update(direction=match[2].upper(), setup_availability="UNDERWAY" if match[3] else "ENTERABLE")
                    else:
                        event.update(direction=match[2].upper(), reported_underway=bool(match[3]))
                    if "stop" in event and Decimal(event["stop"]) <= 0:
                        raise ValueError("positive source stop required")
                    events.append(event)
            offset += len(raw)
        if found != list(SECTIONS):
            raise ValueError("all four alert action sections required, in original order")
        commentary.append({"alert_id": alert["alert_id"], "attribution": "EXPERT_REPORTED",
            "verbatim_preamble": "".join(before), "published_at": alert["published_at"], "effective_at": effective})
    return events, excluded, commentary


def reconstruct(events, *, validate_pilot=True):
    """New IDs only on explicit OPEN; preserve even stop widening and source/model conflicts."""
    current, episodes, history, transitions = {}, [], [], []
    numbered = {}
    for original in events:
        event = deepcopy(original)
        symbol, kind = event["symbol"], event["type"]
        trade = current.get(symbol)
        if kind == "OPEN_NEW_POSITION":
            if trade and trade["position_state"] == "OPEN":
                raise ValueError("new opening conflicts with an already open source episode")
            numbered[symbol] = numbered.get(symbol, 0)+1
            trade = {"trade_id": f"{symbol}-{numbered[symbol]:03d}", "symbol": symbol, "direction": event["direction"],
                "position_state": "OPEN", "setup_availability": "ENTERABLE", "initial_stop": event["stop"],
                "current_stop": event["stop"], "opening_event_id": event["event_id"], "closing_event_id": None,
                "opened_at": event["published_at"], "closed_at": None, "actual_entry_price": None,
                "actual_quantity": None, "actual_execution_timestamp": None, "events": [], "source_warnings": []}
            current[symbol] = trade
            episodes.append(trade)
        elif not trade or trade["position_state"] != "OPEN":
            raise ValueError("source revision/closure without an open source episode")
        if event.get("direction", trade["direction"]) != trade["direction"]:
            raise ValueError("source direction mismatch")
        event["trade_id"] = trade["trade_id"]
        event["setup_before"] = trade["setup_availability"]
        if kind in {"OPEN_NEW_POSITION", "STOP_CHANGED"}:
            old = trade["current_stop"] if kind == "STOP_CHANGED" else None
            if old is not None and Decimal(old) != Decimal(event["previous_stop"]):
                raise ValueError("source stop history contradicts reported previous stop")
            delta = (Decimal(event["stop"])-Decimal(old)) if old is not None else None
            tightening = delta*(1 if trade["direction"] == "LONG" else -1) if delta is not None else None
            history.append({"trade_id": trade["trade_id"], "symbol": symbol, "event_id": event["event_id"],
                "source_order": event["source_order"], "published_at": event["published_at"], "effective_at": event["effective_at"],
                "direction": trade["direction"], "setup_availability": trade["setup_availability"],
                "previous_stop": old, "reported_stop": event["stop"], "change": "INITIAL" if delta is None else
                    "TIGHTENING" if tightening > 0 else "WIDENING" if tightening < 0 else "UNCHANGED"})
            trade["current_stop"] = event["stop"]
        if kind == "SETUP_CHANGED":
            trade["setup_availability"] = event["setup_availability"]
            transitions.append({"trade_id": trade["trade_id"], "symbol": symbol, "event_id": event["event_id"],
                "from": event["setup_before"], "to": trade["setup_availability"], "effective_at": event["effective_at"],
                "published_at": event["published_at"]})
        if kind == "DROPPED":
            if event["reported_underway"] and trade["setup_availability"] != "UNDERWAY":
                trade["source_warnings"].append("DROPPED_LABEL_UNDERWAY_WITHOUT_OBSERVED_TRANSITION")
            trade.update(position_state="CLOSED", closing_event_id=event["event_id"], closed_at=event["published_at"])
        event["setup_after"] = trade["setup_availability"]
        trade["events"].append(event)
    for trade in episodes:
        trade["lifecycle_completeness"] = "SOURCE_OPEN_AND_CLOSURE_OBSERVED" if trade["position_state"] == "CLOSED" else "RIGHT_CENSORED_SOURCE_OPEN"
    if validate_pilot:
        if set(current) != set(UNIVERSE):
            raise ValueError("source ledger must cover exactly the frozen 26 symbols")
        closed = {s for s, t in current.items() if t["position_state"] == "CLOSED"}
        if closed != set(CLOSED) or set(current)-closed != set(OPEN):
            raise ValueError("source final states disagree with the required 12 closed / 14 not-reported-dropped inventory")
    return episodes, history, transitions
