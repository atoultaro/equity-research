"""Analytical daily-bar episodes. No fills, quantities, orders or execution P&L."""

from decimal import Decimal

from ..comprehension.methodology import one_r, validate_methodology
from ..events.model import timestamp


def compatible(evidence, contract, rows, days, origin):
    """Validate narrow units evidence; a caller's bare 'verified' flag is insufficient."""
    if not evidence or evidence.get("con_id") != contract["conId"] or not evidence.get("source_reference"):
        return False
    if evidence.get("status") == "SYNTHETIC_COMPATIBLE":
        return evidence.get("origin") == "synthetic" and origin == "synthetic"
    if evidence.get("status") != "OPERATOR_QUOTE_ANCHORED_SESSION_SCALE":
        return False
    anchors = evidence.get("anchors", [])
    if not anchors or set(days) - {a["session_date"] for a in anchors}:
        return False
    for a in anchors:
        row = rows.get(a["session_date"])
        if (not row or a["field"] not in {"open", "high", "low", "close"}
                or Decimal(row[a["field"]]) != Decimal(a["nominal_quote"])
                or a.get("source_status") != "OPERATOR_PROVIDED_CONTEMPORANEOUS_QUOTE"):
            return False
    return True


def simulate(trades, prices, coverage, calendar, methodology, *, cutoff, basis_evidence, conditional=False):
    """Next eligible RTH Open is a scenario entry, never an observed Grimes fill.

    A partial activation/revision candle is unresolved without intraday evidence.
    Once stopped/target-closed, subsequent revisions only generate conflicts.
    """
    validate_methodology(methodology)
    sessions = calendar["sessions"]
    cutoff = timestamp(cutoff)
    evidence = {e["symbol"]: e for e in basis_evidence}
    if len(evidence) != len(basis_evidence):
        raise ValueError("ambiguous basis evidence")
    outcomes, all_events, hypotheses = [], [], []
    for trade in trades:
        events = trade["events"]
        opening = events[0]
        effective = timestamp(opening["effective_at"]) if opening["effective_at"] else None
        eligible = next((s for s in sessions if effective and timestamp(s["opens_at"]) >= effective), None)
        rows = {r["session_date"]: r for r in prices[trade["symbol"]] if timestamp(next(
            s["closes_at"] for s in sessions if s["session_date"] == r["session_date"])) <= cutoff}
        result = {"trade_id": trade["trade_id"], "symbol": trade["symbol"], "direction": trade["direction"],
            "attribution": "ANALYTICAL_ASSUMPTION_NOT_VERIFIED_EXECUTION", "conditional_basis_scenario": conditional,
            "source_position_state": trade["position_state"], "state": "UNRESOLVED_TIMING", "closure_reason": None,
            "entry_rule": "NEXT_ELIGIBLE_REGULAR_OPEN", "source_open_effective_at": opening["effective_at"],
            "effective_clock": opening["effective_clock"], "first_eligible_at": eligible["opens_at"] if eligible else None,
            "modeled_entry": None, "entry_price_source": None, "actual_entry": None, "actual_fill": None,
            "original_per_share_risk": None, "target_1R": None, "initial_stop": trade["initial_stop"],
            "risk_is_fixed_to_original_stop": True, "target_status": "NOT_OBSERVED", "closed_session": None,
            "minimum_long_exit_fraction": None, "exact_long_exit_fraction": None, "remaining_long_fraction": None,
            "events": [], "warnings": [], "basis_evidence": evidence.get(trade["symbol"]),
            "right_censored": trade["position_state"] == "OPEN"}

        def emit(kind, session=None, **details):
            item = {"modeled_event_id": f"{trade['trade_id']}:model-{len(result['events'])+1}",
                "trade_id": trade["trade_id"], "symbol": trade["symbol"], "type": kind,
                "attribution": "ANALYTICAL_ASSUMPTION_NOT_VERIFIED_EXECUTION", "session_date": session,
                "conditional_on_unverified_basis": conditional, **details}
            result["events"].append(item)
            all_events.append(item)

        def close(reason, session=None, **evidence):
            result.update(state="MODELED_CLOSED", closure_reason=reason, closed_session=session, right_censored=False)
            emit("MODELED_CLOSED", session, cause=reason, actual_fill=None, execution_costs=None, **evidence)

        def unavailable_windows(status):
            for n in (2, 3, 5):
                hypotheses.append({"trade_id": trade["trade_id"], "symbol": trade["symbol"], "horizon_sessions": n,
                    "attribution": "AGENT_DEFINED_EXPLORATORY_DIAGNOSTIC_NOT_A_GRIMES_RULE", "status": status,
                    "sessions": [], "progress_price_units": None, "mfe_price_units": None,
                    "progress_original_R": None, "mfe_original_R": None, "possible_time_stop": None,
                    "definitive_time_exit": False, "definition": "Unavailable; no inferred entry, fill or time exit"})

        if not effective or not eligible:
            unavailable_windows(result["state"])
            outcomes.append(result)
            continue
        if any(e["type"] == "DROPPED" and e["effective_at"]
                and timestamp(e["effective_at"]) <= timestamp(eligible["opens_at"]) for e in events):
            result.update(state="SOURCE_CLOSED_BEFORE_MODELED_ENTRY", right_censored=False)
            unavailable_windows(result["state"])
            outcomes.append(result)
            continue
        if timestamp(eligible["closes_at"]) > cutoff:
            result.update(state="NOT_YET_ACTIVE_RIGHT_CENSORED", right_censored=True)
            unavailable_windows(result["state"])
            outcomes.append(result)
            continue
        entry_day = eligible["session_date"]
        if entry_day not in rows:
            result.update(state="UNRESOLVED_MISSING_SESSION")
            unavailable_windows(result["state"])
            outcomes.append(result)
            continue
        stop = Decimal(trade["initial_stop"])
        stop_source = opening
        entry = Decimal(rows[entry_day]["open"])
        result.update(modeled_entry=str(entry), entry_price_source={"symbol": trade["symbol"],
            "con_id": coverage[trade["symbol"]]["contract"]["conId"], "session_date": entry_day,
            "field": "open", "source_bundle_sha256": coverage[trade["symbol"]]["source_bundle_sha256"]})
        try:
            result.update(one_r(trade["direction"], entry, stop))
        except ValueError:
            result["warnings"].append("NONPOSITIVE_ORIGINAL_R_TARGET_UNAVAILABLE")
        active_days = [s["session_date"] for s in sessions if entry_day <= s["session_date"]
            and timestamp(s["closes_at"]) <= cutoff
            and not any(e["type"] == "DROPPED" and e["effective_at"]
                and timestamp(e["effective_at"]) <= timestamp(s["opens_at"]) for e in events)]
        basis_ok = compatible(evidence.get(trade["symbol"]), coverage[trade["symbol"]]["contract"], rows, active_days,
            coverage[trade["symbol"]]["origin"])
        result["basis_status"] = "BOUNDED_QUOTE_SCALE_CORROBORATED" if basis_ok else "UNVERIFIED_OR_INCOMPATIBLE"
        if not basis_ok and not conditional:
            result.update(state="UNRESOLVED_BASIS")
            unavailable_windows(result["state"])
            outcomes.append(result)
            continue
        result["state"] = "MODELED_OPEN"
        target = Decimal(result["target_1R"]) if result["target_1R"] else None
        sign = 1 if trade["direction"] == "LONG" else -1
        pending = list(events[1:])
        unresolved = False

        def apply(event):
            nonlocal stop, stop_source, unresolved
            if result["state"] == "MODELED_CLOSED":
                if event["type"] != "DROPPED":
                    emit("SOURCE_MODEL_CONFLICT", event_id=event["event_id"],
                        reason="SOURCE_MANAGEMENT_AFTER_MODELED_CLOSURE_NO_REENTRY", reported_stop=event.get("stop"))
                return
            if event["effective_at"] is None:
                unresolved = True
                result["state"] = "UNRESOLVED_TIMING"
            elif event["type"] == "STOP_CHANGED":
                stop = Decimal(event["stop"])
                stop_source = event
            elif event["type"] == "DROPPED":
                started = [s["session_date"] for s in sessions if timestamp(s["opens_at"]) <= timestamp(event["effective_at"])]
                close("SOURCE_REPORTED_DROPPED_PRICE_AND_EXECUTION_UNKNOWN", started[-1] if started else None,
                    source_event_id=event["event_id"], source_closure_effective_bound=event["effective_at"])

        for session in sessions:
            day = session["session_date"]
            op, cl = timestamp(session["opens_at"]), timestamp(session["closes_at"])
            if day < entry_day or cl > cutoff:
                continue
            before = [e for e in pending if e["effective_at"] and timestamp(e["effective_at"]) <= op]
            for event in before:
                apply(event)
                pending.remove(event)
            if result["state"] == "MODELED_CLOSED":
                continue
            if any(e["effective_at"] is None for e in pending):
                # Source sequence provides no absolute boundary for this revision.
                result["state"] = "UNRESOLVED_TIMING"
                unresolved = True
            if unresolved:
                continue
            bar = rows.get(day)
            if not bar:
                result["state"] = "UNRESOLVED_MISSING_SESSION"
                unresolved = True
                continue
            intraday = [e for e in pending if e["effective_at"] and op < timestamp(e["effective_at"]) < cl
                and e["type"] in {"STOP_CHANGED", "DROPPED"}]
            o, hi, lo = (Decimal(bar[k]) for k in ("open", "high", "low"))
            stop_open = o <= stop if sign == 1 else o >= stop
            target_open = target is not None and (o >= target if sign == 1 else o <= target)
            touched_stop = lo <= stop if sign == 1 else hi >= stop
            touched_target = target is not None and (hi >= target if sign == 1 else lo <= target)
            if intraday and not stop_open and not (target_open and sign == -1):
                result["state"] = "TIMING_AMBIGUOUS"
                result["warnings"].append(f"{day}:DAILY_CANDLE_STRADDLES_SOURCE_REVISION_OR_CLOSURE")
                unresolved = True
                continue
            if touched_stop and touched_target and not stop_open and not target_open and result["target_status"] == "NOT_OBSERVED":
                result.update(state="TIMING_AMBIGUOUS", target_status="STOP_TARGET_ORDER_UNKNOWN")
                emit("ASSUMED_STOP_TRIGGERED", day, stop=str(stop), status="CANDIDATE_ORDER_UNKNOWN", actual_fill=None,
                    active_stop_source_event=stop_source["event_id"], active_stop_effective_bound=stop_source["effective_at"])
                emit("HYPOTHETICAL_TARGET_REACHED", day, target=str(target), status="CANDIDATE_ORDER_UNKNOWN")
                unresolved = True
                continue
            if stop_open or (touched_stop and (not target_open or result["target_status"] != "NOT_OBSERVED")):
                emit("ASSUMED_STOP_TRIGGERED", day, stop=str(stop), status="TRIGGER_OBSERVED_UNDER_ASSUMPTION",
                    gap_through_stop=(o < stop if sign == 1 else o > stop), actual_fill=None,
                    fill_and_slippage="UNKNOWN", active_stop_applied_to="FULL_ELIGIBLE_RTH_SESSION",
                    active_stop_source_event=stop_source["event_id"], active_stop_effective_bound=stop_source["effective_at"])
                close("ASSUMED_STOP_TRIGGERED", day)
                continue
            if touched_target and result["target_status"] == "NOT_OBSERVED":
                result["target_status"] = "HYPOTHETICAL_1R_REACHED"
                emit("HYPOTHETICAL_TARGET_REACHED", day, target=str(target), status="HYPOTHETICAL_ONLY_ACTUAL_ENTRY_UNKNOWN",
                    management=methodology[trade["direction"]], actual_fill=None)
                if sign == -1:
                    close("HYPOTHETICAL_SHORT_FULL_1R", day)
                else:
                    result.update(state="MODELED_OPEN_WITH_UNSPECIFIED_RUNNER", minimum_long_exit_fraction="1/3")
                    if touched_stop:  # target at Open precedes a later range crossing
                        emit("ASSUMED_STOP_TRIGGERED", day, stop=str(stop), status="RUNNER_TRIGGER_AFTER_OPEN_TARGET",
                            actual_fill=None, fill_and_slippage="UNKNOWN", active_stop_source_event=stop_source["event_id"],
                            active_stop_effective_bound=stop_source["effective_at"])
                        close("ASSUMED_RUNNER_STOP_TRIGGERED", day)
        for event in pending:
            if event["effective_at"] and timestamp(event["effective_at"]) <= cutoff:
                apply(event)
        if result["state"] == "MODELED_CLOSED" and trade["position_state"] == "OPEN":
            emit("SOURCE_MODEL_CONFLICT", reason="SOURCE_NOT_REPORTED_DROPPED_MODEL_CLOSED", source_state="OPEN")
        # Time horizons are calendar-based; never skip a missing day or use post-exit movement as held exposure.
        expected = [s["session_date"] for s in sessions if s["session_date"] >= entry_day]
        for n in (2, 3, 5):
            days = expected[:n]
            status = "AVAILABLE"
            if days and result["closed_session"] and result["closed_session"] <= days[-1]:
                status = "MODELED_CLOSED_BEFORE_OR_DURING_HORIZON"
            elif len(days) < n or any(d not in rows for d in days):
                status = "RIGHT_CENSORED_OR_MISSING_SESSION"
            item = {"trade_id": trade["trade_id"], "symbol": trade["symbol"], "horizon_sessions": n,
                "attribution": "AGENT_DEFINED_EXPLORATORY_DIAGNOSTIC_NOT_A_GRIMES_RULE", "status": status,
                "sessions": days, "progress_price_units": None, "mfe_price_units": None, "progress_original_R": None,
                "mfe_original_R": None, "possible_time_stop": None, "definitive_time_exit": False,
                "definition": "N sessions including scenario entry day; flag only if side-correct Close progress <= 0; never closes a position"}
            if status == "AVAILABLE":
                progress = (Decimal(rows[days[-1]]["close"])-entry)*sign
                mfe = max([Decimal(0)]+[(Decimal(rows[d]["high" if sign == 1 else "low"])-entry)*sign for d in days])
                risk = Decimal(result["original_per_share_risk"]) if result["original_per_share_risk"] else None
                item.update(progress_price_units=str(progress), mfe_price_units=str(mfe),
                    progress_original_R=str(progress/risk) if risk else None, mfe_original_R=str(mfe/risk) if risk else None,
                    possible_time_stop=progress <= 0)
                if progress <= 0:
                    emit("POSSIBLE_TIME_STOP", days[-1], horizon_sessions=n, definitive_time_exit=False,
                        rule_attribution="AGENT_DEFINED_EXPLORATORY_NOT_VERIFIED_GRIMES_PARAMETER")
            hypotheses.append(item)
        outcomes.append(result)
    return outcomes, all_events, hypotheses
