"""Causal candidate construction; subsequent source actions never select a level."""

from ..models import timestamp
from .admission import value, risk_geometry


def candidates(trade, evidence, clock, *, trigger_sessions=3):
    opening = trade["events"][0]
    alert_id = opening["source"]["alert_id"]
    bound = clock["publication_bounds"][alert_id]
    weekly = alert_id == clock["weekly_alert_id"]
    cutoff = clock["weekly_construction_cutoff"] if weekly else bound["upper"]
    day, features = evidence.features(trade["symbol"], cutoff)
    close, atr = value(features, "close"), value(features, "atr14")
    stop = float(trade["initial_stop"])
    sign = 1 if trade["direction"] == "LONG" else -1
    aligned = all(value(features, k) is not None and sign*value(features, k) > 0
                  for k in ("close_sma50", "sma50_slope20", "return20"))
    effective = timestamp(clock["assumed_action_clocks"][alert_id])
    sessions = evidence.calendar["sessions"]
    # EARLY boundary represents publication before this Open, not at the Open.
    eligible = [s for s in sessions if timestamp(s["opens_at"]) >= effective]
    rows = evidence.rows(trade["symbol"])
    plans = []
    for name in ("H1_NEXT_OPEN", "H2_ALERT_SESSION_CLOSE", "H3_CONFIRMATION", "H4_PULLBACK"):
        base = {"candidate_id": f"{trade['trade_id']}:{clock['name']}:{name}", "hypothesis": name,
            "clock_variant": clock["name"], "source_publication": bound,
            "construction": {"cutoff": cutoff, "last_available_session": day,
                "source_open_event_id": opening["event_id"], "initial_reported_stop": trade["initial_stop"],
                "native_ATR14": atr, "native_reference_close": close, "directional_trend_aligned": aligned,
                "opening_stop_distance_to_levels_ATR": {k: (stop-(v["price"] if isinstance(v, dict) else v))/atr
                    for k in ("sma20", "sma50", "prior20_high", "prior20_low", "confirmed_swing_low", "confirmed_swing_high")
                    if (v := value(features, k)) is not None and atr},
                "features": features, "subsequent_actions_used": False},
            "entry_session": None, "entry_at": None, "entry_price": None, "entry_price_range": None,
            "entry_kind": None, "entry_level": None, "status": "PENDING_RIGHT_CENSORED", "construction_support": 0,
            "actual_entry": None, "price_basis": "CONDITIONAL_NATIVE_STOP_SCALE", "not_a_documented_grimes_rule": True}
        target_session = None
        if name == "H1_NEXT_OPEN":
            base.update(rationale="Conventional next eligible Open; initial stop known from opening alert", construction_support=2)
            target_session = eligible[0] if eligible else None
            base["entry_kind"] = "OPEN"
        elif name == "H2_ALERT_SESSION_CLOSE":
            base.update(rationale="Near-close reference only if publication can precede that Close; no current-bar setup information", construction_support=0)
            if weekly and clock["name"] == "FIRST_SESSION_CLOSE_COMPATIBLE":
                target_session = next(s for s in sessions if s["session_date"] == clock["weekly_first_session"])
                base["entry_kind"] = "CLOSE"
            else:
                base.update(status="REJECTED", reason="Alert-session Close before known publication boundary, no RTH session, or incompatible weekly schedule")
        elif name == "H3_CONFIRMATION":
            base.update(rationale="Predeclared follow-through extreme for aligned trend, otherwise previous20-session boundary",
                        construction_support=2 if aligned and sign < 0 else 1)
            raw = rows.get(day, {})
            level = float(raw["high" if sign > 0 else "low"]) if aligned and raw else value(features, "prior20_high" if sign > 0 else "prior20_low")
            base.update(entry_kind="CONFIRMATION", entry_level=level,
                        level_definition="LAST_AVAILABLE_BAR_EXTREME" if aligned else "PREVIOUS20_BOUNDARY")
        else:
            levels = [("SMA20", value(features, "sma20")), ("SMA50", value(features, "sma50"))]
            pivot = value(features, "confirmed_swing_low" if sign > 0 else "confirmed_swing_high")
            if pivot:
                levels.append(("CONFIRMED_PROTECTIVE_SWING", pivot["price"]))
            valid = [(label, level) for label, level in levels if close is not None and level is not None
                     and sign*(close-level) > 0 and sign*(level-stop) > 0]
            label, level = valid[0] if valid else (None, None)
            base.update(rationale="First predeclared SMA20, SMA50 or confirmed protective pivot between current Close and initial stop",
                construction_support=2 if aligned and sign > 0 else 0,
                entry_kind="PULLBACK", entry_level=level, level_definition=label)
        if name in {"H3_CONFIRMATION", "H4_PULLBACK"}:
            if base["entry_level"] is None:
                base.update(status="REJECTED", reason="No causal, geometrically valid predeclared level")
            else:
                for session in eligible[:trigger_sessions]:
                    row = rows.get(session["session_date"])
                    if row is None:
                        base.update(status="MISSING_OR_FUTURE_TRIGGER_SESSION", missing_session=session["session_date"])
                        break
                    level = base["entry_level"]
                    hit = float(row["high"]) >= level if (sign > 0) == (name == "H3_CONFIRMATION") else float(row["low"]) <= level
                    if hit:
                        target_session = session
                        break
                if target_session is None and base["status"] == "PENDING_RIGHT_CENSORED":
                    base.update(status="NOT_TRIGGERED_IN_FIXED_WINDOW", reason="Not observed within three eligible sessions; not proof of no actual trade")
        if target_session is not None and base["status"] != "REJECTED":
            row = rows.get(target_session["session_date"])
            if row is None:
                base.update(status="MISSING_OR_FUTURE_ENTRY_SESSION", entry_session=target_session["session_date"])
            else:
                o, hi, lo = (float(row[k]) for k in ("open", "high", "low"))
                kind, level = base["entry_kind"], base["entry_level"]
                if kind == "OPEN":
                    price, price_range, at = o, [o, o], target_session["opens_at"]
                elif kind == "CLOSE":
                    price = float(row["close"])
                    price_range, at = [price, price], target_session["closes_at"]
                else:
                    open_hit = (o >= level if sign > 0 else o <= level) if kind == "CONFIRMATION" else (o <= level if sign > 0 else o >= level)
                    price = o if open_hit else level
                    price_range = [price, price] if open_hit else ([level, hi] if (sign > 0) == (kind == "CONFIRMATION") else [lo, level])
                    at = target_session["opens_at"] if open_hit else None
                base.update(entry_session=target_session["session_date"], entry_at=at, entry_price=price,
                    entry_price_range=price_range, entry_attribution="HYPOTHETICAL_REFERENCE_NOT_OBSERVED_FILL",
                    entry_time_interval=[target_session["opens_at"], target_session["closes_at"]] if at is None else [at, at],
                    geometry=risk_geometry(trade["direction"], price, stop, atr, price_range), status="CONSTRUCTED")
                # Existing source stops already reported before this entry must
                # also admit positive placed risk. Later revisions never reset R.
                prior = [e for e in trade["events"][1:] if e["type"] == "STOP_CHANGED"
                    and timestamp(clock["assumed_action_clocks"][e["source"]["alert_id"]]) <= timestamp(target_session["opens_at"])]
                if prior:
                    active_stop = float(prior[-1]["stop"])
                    base["reported_stop_at_entry"] = active_stop
                    if sign*(price-active_stop) <= 0:
                        base.update(status="REJECTED", reason="Source stop already breached before hypothesized entry")
                else:
                    base["reported_stop_at_entry"] = stop
                active_stop = base["reported_stop_at_entry"]
                activation_day, activation_features = evidence.features(trade["symbol"], target_session["opens_at"])
                activation_atr = value(activation_features, "atr14")
                base["opening_stop_geometry"] = risk_geometry(trade["direction"], price, stop, activation_atr, price_range)
                base["geometry"] = risk_geometry(trade["direction"], price, active_stop, activation_atr, price_range)
                base["entry_activation_evidence"] = {"known_stop_revision_ids": [e["event_id"] for e in prior],
                    "availability_cutoff": target_session["opens_at"], "last_available_session": activation_day,
                    "pre_entry_ATR14": activation_atr, "subsequent_to_construction_but_known_before_entry": True}
                if sign*(price-active_stop) <= 0:
                    base.update(status="REJECTED", reason="Nonpositive protective risk at hypothesized entry")
                base["original_risk_basis"] = "Stop known at candidate activation; fixed after entry, never rebased by later revisions; opening stop retained separately"
        plans.append(base)
        if trade["symbol"] in evidence.scale_views:
            base["analysis_price_view"] = evidence.scale_views[trade["symbol"]]
            base["price_basis"] = "EXPLICIT_DERIVED_UNVERIFIED"
            base["construction"].update(analysis_ATR14=atr, analysis_reference_close=close,
                native_ATR14=None, native_reference_close=None)
    return plans
