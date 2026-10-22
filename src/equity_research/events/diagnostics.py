"""Descriptive native-basis outcomes, never signals, execution or causal claims."""

from decimal import Decimal
from statistics import mean

from .model import revision_key


def diagnostics(dataset, symbol, event_dataset, alignments, calendar):
    from market_shared import atr_simple_series, true_range
    from ..reporting import shared_identity

    manifest = dataset.manifest
    if manifest["shared_dependency"] != shared_identity():
        raise ValueError("shared mathematics differs from frozen price dataset")
    entry = manifest["securities"][symbol]
    rows = dataset.bars(symbol)
    by_day = {r["session_date"]: r for r in rows}
    if len(by_day) != len(rows):
        raise ValueError("duplicate price sessions")
    security_id, basis = entry["security"]["security_id"], entry["basis"]
    days = [s["session_date"] for s in calendar["sessions"]]
    indices = {d: i for i, d in enumerate(days)}
    events = event_dataset.events
    if any(e["security_id"] != security_id for e in events):
        raise ValueError("event/price security identity mismatch; no symbol-only joins")
    if any(r["provider"] != manifest["provider"] or r["price_basis"] != basis["price_basis"] or
           r["volume_basis"] != basis["volume_basis"] for r in rows):
        raise ValueError("mixed provider/price/share basis")
    for row in rows:
        values = {k: Decimal(row[k]) for k in ("open", "high", "low", "close", "volume")}
        if (any(not v.is_finite() for v in values.values()) or
                any(values[k] <= 0 for k in ("open", "high", "low", "close")) or
                values["volume"] < 0 or values["volume"] != values["volume"].to_integral_value() or
                values["high"] < max(values["open"], values["close"], values["low"]) or
                values["low"] > min(values["open"], values["close"], values["high"])):
            raise ValueError("invalid OHLCV input")
    if dataset.quality(symbol)["status"] not in {"PASS", "FAIL"}:
        raise ValueError("unknown price quality status")
    # Invalid OHLCV/off-calendar/duplicate input must not become usable merely
    # because a caller allowed an incomplete freeze. Only missing sessions can
    # yield partial diagnostics with individual unavailable outcomes.
    from ..history.contracts import Security
    from ..history.normalize import reconcile
    checked = reconcile(rows, Security(**entry["security"]), manifest["start"], manifest["end"])
    if any(checked.get(k) for k in ("duplicate_sessions", "off_calendar_sessions", "outside_listing_sessions")):
        raise ValueError("invalid price rows")
    aligned = {a["revision_key"]: a for a in alignments}
    conflicts = set(event_dataset.quality["conflicting_event_ids"])
    results = []
    for event in events:
        a = aligned[revision_key(event)]
        record = {"revision_key": revision_key(event), "event_type": event["event_type"],
                  "reaction_session": a["reaction_session"], "status": "UNAVAILABLE", "issues": [],
                  "price_basis": basis["price_basis"], "volume_basis": basis["volume_basis"],
                  "basis_verified": basis["verified"], "potential_corporate_action_effects": [],
                  "previous_close": None, "first_post_open": None, "overnight_gap_pct": None,
                  "session_high_low": None, "volume_relative20": None, "pre_event_atr14": None,
                  "subsequent_close_returns_pct": {str(h): None for h in (1, 5, 10)}}
        results.append(record)
        if event["event_id"] in conflicts:
            record["issues"].append("CONFLICTING_EVENT_REVISIONS")
            continue
        if event["evidence_status"] == "UNVERIFIED" or a["issues"]:
            record["issues"].append("UNVERIFIED_OR_CONFLICTING_EVENT_TIMING")
            continue
        if event["event_type"] == "DIVIDEND" and a["reaction_session"] is None:
            record["issues"].append("EX_DATE_UNKNOWN")
            continue
        if event["event_type"] == "SPLIT" and not basis["verified"]:
            record["issues"].append("SPLIT_PRICE_AND_VOLUME_BASIS_UNVERIFIED")
            continue
        if a["timing_ambiguous"] and event["event_type"] == "EARNINGS":
            record["issues"].append("AMBIGUOUS_ANNOUNCEMENT_TIMING")
            continue
        if a["intraday_daily_bar_contaminated"] and event["event_type"] == "EARNINGS":
            record["issues"].append("INTRADAY_EVENT_REQUIRES_INTRADAY_BARS")
            continue
        reaction = a["reaction_session"]
        if reaction is None or reaction not in indices:
            record["issues"].append("NO_VERIFIED_REACTION_SESSION")
            continue
        i = indices[reaction]
        previous = days[i - 1] if i else None
        if previous not in by_day or reaction not in by_day:
            record["issues"].append("MISSING_PREVIOUS_OR_REACTION_SESSION")
            continue
        pre, post = by_day[previous], by_day[reaction]
        pc, po = float(pre["close"]), float(post["open"])
        record.update(status="PARTIAL", previous_session=previous, previous_close=pc, first_post_open=po,
                      overnight_gap_pct=(po / pc - 1) * 100,
                      session_high_low=float(post["high"]) - float(post["low"]))
        volume_days = days[max(0, i - 20):i]
        atr_days = days[max(0, i - 15):i]
        if len(volume_days) == 20 and all(d in by_day for d in volume_days):
            average = mean(float(by_day[d]["volume"]) for d in volume_days)
            if average > 0:
                record["volume_relative20"] = float(post["volume"]) / average
            else:
                record["issues"].append("ZERO_PRE_EVENT_VOLUME_AVERAGE")
        else:
            record["issues"].append("MISSING_VOLUME_WARMUP")
        if len(atr_days) == 15 and all(d in by_day for d in atr_days):
            ranges = [true_range(float(by_day[d]["high"]), float(by_day[d]["low"]),
                                 float(by_day[p]["close"])) for p, d in zip(atr_days, atr_days[1:])]
            record["pre_event_atr14"] = atr_simple_series(ranges, 14)[-1]
        else:
            record["issues"].append("MISSING_ATR_WARMUP")
        for horizon in (1, 5, 10):
            outcome_days = days[i:i + horizon + 1]
            if len(outcome_days) != horizon + 1 or any(d not in by_day for d in outcome_days):
                record["issues"].append(f"MISSING_OUTCOME_{horizon}_SESSIONS")
            else:
                record["subsequent_close_returns_pct"][str(horizon)] = (
                    float(by_day[outcome_days[-1]]["close"]) / float(post["close"]) - 1) * 100
        for corporate in events:
            if corporate["event_type"] in {"DIVIDEND", "SPLIT"}:
                effective = corporate["effective_date"]
                if effective is None or previous < effective <= days[min(len(days) - 1, i + 10)]:
                    record["potential_corporate_action_effects"].append({
                        "event_id": corporate["event_id"], "type": corporate["event_type"],
                        "effective_date": effective, "interpretation": "POSSIBLE_NOT_CAUSALLY_ATTRIBUTED"})
        if event["event_type"] == "DIVIDEND":
            record["cash_per_share_source_quote"] = event["payload"]["cash_per_share"]
            record["close_change_dollars"] = float(post["close"]) - pc
            record["interpretation"] = "NATIVE_REPORTED_CLOSE_COMPARISON_NOT_MECHANICAL_DIVIDEND_ADJUSTMENT"
        if not record["issues"]:
            record["status"] = "AVAILABLE"
    # Distribution checks examine every consecutive expected session, not only
    # earnings windows. Thresholds are fixed descriptive review flags, not fitted.
    gaps, volumes, missing_pairs = [], [], []
    price_days = [d for d in days if manifest["start"] <= d <= manifest["end"]]
    for before, after in zip(price_days, price_days[1:]):
        if before not in by_day or after not in by_day:
            missing_pairs.append([before, after])
            continue
        gap = (float(by_day[after]["open"]) / float(by_day[before]["close"]) - 1) * 100
        if abs(gap) >= 5:
            matches = [r["event_id"] for r in events if aligned[revision_key(r)]["reaction_session"] == after]
            gaps.append({"session_date": after, "gap_pct": gap, "aligned_events": matches,
                         "causal_attribution": "UNKNOWN"})
        i = indices[after]
        preceding = days[max(0, i - 20):i]
        if len(preceding) == 20 and all(d in by_day for d in preceding):
            avg = mean(float(by_day[d]["volume"]) for d in preceding)
            ratio = float(by_day[after]["volume"]) / avg if avg else None
            if ratio is not None and (ratio >= 3 or ratio <= 0.25):
                volumes.append({"session_date": after, "relative20": ratio, "units_verified": basis["verified"]})
    return {"schema_version": "event_diagnostics_v1", "interpretation": "RETROSPECTIVE_DESCRIPTIVE_ONLY",
            "return_definition": "reaction_session_close_to_close_at_1_5_10_subsequent_exchange_sessions",
            "pre_features_cutoff": "previous_completed_regular_session_close",
            "dividend_treatment": "native_prices_not_total_return_no_adjustment_applied",
            "basis": basis, "events": results, "price_quality": checked,
            "discontinuity_review": {"absolute_gap_threshold_pct": 5, "gaps": gaps,
                                     "missing_session_pairs": missing_pairs, "causal_attribution": "UNKNOWN"},
            "volume_review": {"high_threshold": 3, "low_threshold": 0.25, "observations": volumes}}
