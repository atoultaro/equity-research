"""Four bounded management explanations over daily OHLC ordering possibilities.

No orders, position sizes, accounting or realized P&L. Two canonical extrema
orders expose stop/target/entry ambiguity; they are possibilities, not likelihoods.
"""

from copy import deepcopy

from ..models import timestamp

POLICIES = ("FULL_EXIT_AT_1R", "PARTIAL_50_AT_1R", "HOLD_WITH_REPORTED_STOPS", "CLOSE_REVIEW_NEXT_OPEN")
COMPLEXITY = {"HOLD_WITH_REPORTED_STOPS": 0, "FULL_EXIT_AT_1R": 1, "PARTIAL_50_AT_1R": 1, "CLOSE_REVIEW_NEXT_OPEN": 2}


def _merge(states):
    merged = {}
    for state in states:
        key = tuple(state[k] for k in ("entered", "remaining", "target_seen", "closed_reason", "closed_session", "review_pending"))
        if key in merged:
            old = merged[key]
            old["mfe_R"] = max(old["mfe_R"], state["mfe_R"])
            old["mae_R"] = max(old["mae_R"], state["mae_R"])
        else:
            merged[key] = state
    return list(merged.values())


def trajectory(trade, candidate, clock, rows, calendar, cutoff, policy):
    if policy not in POLICIES:
        raise ValueError("unknown bounded reconstruction management policy")
    result = {"policy": policy, "actual_fills": None, "actual_size": None, "actual_realized_pnl": None,
        "source_position_status": trade["position_state"], "source_setup_status": trade["setup_availability"],
        "observations": [], "terminal_possibilities": [], "no_reentry": True,
        "partial_fraction": 0.5 if policy == "PARTIAL_50_AT_1R" else None,
        "partial_fraction_attribution": "Illustrative fixed hypothesis, not observed Grimes sizing",
        "ordering_scope": "O-H-L-C and O-L-H-C possibilities; no inferred intraday timestamps or probabilities"}
    if candidate["status"] != "CONSTRUCTED":
        return result | {"status": "NO_COMPARABLE_OBSERVED_ENTRY", "rank_eligible": False}
    sign = 1 if trade["direction"] == "LONG" else -1
    entry = candidate["entry_price"]
    original_stop = float(trade["initial_stop"])
    risk = candidate["geometry"]["reference_risk"]
    if risk <= 0:
        raise ValueError("positive reference risk required")
    target = entry+sign*risk
    stop = original_stop
    states = [{"entered": False, "remaining": 0.0, "target_seen": False, "closed_reason": None,
               "closed_session": None, "review_pending": False, "mfe_R": 0.0, "mae_R": 0.0}]
    pending = list(trade["events"][1:])
    finished = False
    missing = []

    def observe(event, at, final=False):
        active = sum(s["remaining"] > 0 for s in states)
        closed = sum(s["entered"] and s["remaining"] == 0 for s in states)
        unentered = sum(not s["entered"] for s in states)
        kind = event["type"]
        if closed == len(states):
            status = "DROP_AFTER_MODEL_EXIT_CAUSE_UNRESOLVED" if kind == "DROPPED" else "CONTINUATION_CONFLICT"
        elif unentered == len(states):
            status = "ENTRY_NOT_YET_OBSERVED_NOT_PROOF_NO_TRADE"
        elif closed:
            status = "PATH_DEPENDENT_COMPATIBILITY"
        else:
            status = "ACTIVE_COMPATIBLE"
        if missing:
            status = "UNRESOLVED_MISSING_PRICE_PATH"
        result["observations"].append({"event_id": event["event_id"], "type": kind,
            "alert_id": event["source"]["alert_id"], "source_published_at": event["published_at"],
            "assumed_evaluation_clock": at, "status": status,
            "active_possibilities": active, "closed_possibilities": closed, "unentered_possibilities": unentered,
            "counts_are_not_probabilities": True, "final_source_state_check": final})

    def apply_until(at):
        nonlocal stop, states, finished
        for event in list(pending):
            moment = clock["assumed_action_clocks"][event["source"]["alert_id"]]
            if timestamp(moment) > timestamp(at):
                continue
            observe(event, moment)
            if event["type"] == "STOP_CHANGED":
                stop = float(event["stop"])
            if event["type"] == "DROPPED":
                for state in states:
                    if state["remaining"]:
                        state.update(remaining=0, closed_reason="SOURCE_DROPPED_EXECUTION_UNOBSERVED", closed_session=moment[:10])
                finished = True
            pending.remove(event)

    def mark(state, price):
        if state["remaining"]:
            r = sign*(price-entry)/risk
            state["mfe_R"] = max(state["mfe_R"], r, 0)
            state["mae_R"] = max(state["mae_R"], -r, 0)

    def close(state, cause, day):
        state.update(remaining=0, closed_reason=cause, closed_session=day, review_pending=False)

    def enter(state):
        state.update(entered=True, remaining=1.0)

    def segment(state, start, end, day):
        if state["entered"] and state["remaining"] == 0:
            return
        if not state["entered"]:
            level = candidate["entry_price"]
            if min(start, end) <= level <= max(start, end):
                enter(state)
                start = level
            else:
                return
        crossings = []
        if policy != "CLOSE_REVIEW_NEXT_OPEN" and min(start, end) <= stop <= max(start, end):
            crossings.append((abs(stop-start), "STOP", stop))
        if not state["target_seen"] and min(start, end) <= target <= max(start, end):
            crossings.append((abs(target-start), "TARGET", target))
        for _, kind, price in sorted(crossings):
            mark(state, price)
            if kind == "STOP":
                close(state, "HYPOTHETICAL_STOP_TOUCH", day)
                return
            state["target_seen"] = True
            if policy == "FULL_EXIT_AT_1R":
                close(state, "HYPOTHETICAL_FULL_1R", day)
                return
            if policy == "PARTIAL_50_AT_1R":
                state["remaining"] = 0.5
        mark(state, end)

    for session in calendar["sessions"]:
        day = session["session_date"]
        if timestamp(session["closes_at"]) > timestamp(cutoff):
            break
        apply_until(session["opens_at"])
        if finished:
            if not any(s["entered"] for s in states):
                result.update(status="SOURCE_DROPPED_BEFORE_CANDIDATE_ENTRY", rank_eligible=False)
            break
        if day < candidate["entry_session"]:
            apply_until(session["closes_at"])
            continue
        row = rows.get(day)
        if row is None:
            missing.append(day)
            break  # A gap never silently compresses an exposure path.
        o, hi, lo, cl = (float(row[k]) for k in ("open", "high", "low", "close"))
        is_entry_day = day == candidate["entry_session"]
        branches = []
        for previous in states:
            for vertices in ((o, hi, lo, cl), (o, lo, hi, cl)):
                state = deepcopy(previous)
                if is_entry_day and candidate["entry_kind"] == "CLOSE":
                    # Earlier High/Low cannot stop or target a closing entry.
                    enter(state)
                    branches.append(state)
                    continue
                if is_entry_day and candidate["entry_at"] == session["opens_at"]:
                    enter(state)
                if state["remaining"]:
                    if policy == "CLOSE_REVIEW_NEXT_OPEN" and state["review_pending"]:
                        if sign*(o-stop) <= 0:
                            mark(state, o)
                            close(state, "NEXT_OPEN_REVIEW_STILL_ADVERSE", day)
                        else:
                            state["review_pending"] = False
                    elif policy != "CLOSE_REVIEW_NEXT_OPEN" and sign*(o-stop) <= 0:
                        mark(state, o)
                        close(state, "HYPOTHETICAL_STOP_GAP", day)
                    if state["remaining"] and not state["target_seen"] and sign*(o-target) >= 0:
                        mark(state, o)
                        state["target_seen"] = True
                        if policy == "FULL_EXIT_AT_1R":
                            close(state, "HYPOTHETICAL_FULL_1R", day)
                        elif policy == "PARTIAL_50_AT_1R":
                            state["remaining"] = 0.5
                for start, end in zip(vertices, vertices[1:]):
                    segment(state, start, end, day)
                if state["remaining"] and policy == "CLOSE_REVIEW_NEXT_OPEN" and sign*(cl-stop) <= 0:
                    state["review_pending"] = True
                branches.append(state)
        states = _merge(branches)
        apply_until(session["closes_at"])
    apply_until(cutoff)
    if trade["position_state"] == "OPEN":
        observe({"event_id": trade["trade_id"]+":source-final", "type": "SOURCE_STILL_REPORTED_OPEN",
                 "source": {"alert_id": "FINAL_SOURCE_OPEN"}, "published_at": None}, cutoff, final=True)
    result["terminal_possibilities"] = states
    conflicts = {r["alert_id"] for r in result["observations"] if r["status"] == "CONTINUATION_CONFLICT"}
    compatible = {r["alert_id"] for r in result["observations"] if r["status"] == "ACTIVE_COMPATIBLE" and not r["final_source_state_check"]}
    result.update(status=result.get("status", "EXPLORATORY_PATHS_COMPLETE") if not missing else "INCOMPLETE_MISSING_SESSION",
        rank_eligible=result.get("rank_eligible", True) and not missing and any(s["entered"] for s in states),
        conflict_alert_clusters=sorted(conflicts), compatible_alert_clusters=sorted(compatible),
        missing_sessions=missing, original_reference_R=risk, reference_target_1R=target,
        active_source_stop_at_cutoff=stop,
        convention_cost=COMPLEXITY[policy],
        evaluation_vector=[len(conflicts), -len(compatible), COMPLEXITY[policy], -candidate["construction_support"]],
        vector_order="Minimise robust continuation-conflict clusters, maximise compatible later alert clusters, prefer fewer extra conventions, then construction support; no profit score",
        pending_review_at_end=any(s["review_pending"] for s in states),
        no_automatic_full_exit_at_1R=policy != "FULL_EXIT_AT_1R")
    return result
