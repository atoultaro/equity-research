"""Causal setup/trigger/plan research. No provider, mutable cache or fill engine."""

from collections import Counter
from dataclasses import asdict
from datetime import timedelta
from decimal import Context, localcontext
from statistics import mean

from market_shared import atr_simple_last, true_range

from .model import (CONTINUATION, FAILED, Setup, Signal, build_plan,
                    evaluate_trigger, identity, prior_boundary)
from ..ingestion.storage import digest, encode
from ..models import number, timestamp
from ..reporting import shared_identity


def validate_history(rows, calendar, symbol, security_id):
    sessions = calendar["sessions"]
    days = [s["session_date"] for s in sessions]
    if not days or days != sorted(set(days)):
        raise ValueError("calendar must be unique ascending expected sessions")
    for session in sessions:
        if timestamp(session["opens_at"]) >= timestamp(session["closes_at"]):
            raise ValueError("invalid session times")
    observed = [r["session_date"] for r in rows]
    if not observed or observed != sorted(set(observed)) or not set(observed) <= set(days):
        raise ValueError("empty/duplicate/off-calendar history")
    expected = [d for d in days if observed[0] <= d <= observed[-1]]
    if observed != expected:
        raise ValueError("missing expected sessions; never forward fill")
    positions = {day: i for i, day in enumerate(days)}
    for row in rows:
        if row["symbol"] != symbol or row["security_id"] != security_id:
            raise ValueError("source dataset identity mismatch")
        v = {k: number(row[k]) for k in ("open", "high", "low", "close", "volume")}
        if (min(v[k] for k in ("open", "high", "low", "close")) <= 0 or v["volume"] < 0 or
                v["high"] < max(v["open"], v["close"], v["low"]) or v["low"] > min(v["open"], v["close"], v["high"])):
            raise ValueError("invalid OHLCV")
        if row.get("available_at") is not None:
            index = positions[row["session_date"]]
            available = timestamp(row["available_at"])
            if (available < timestamp(sessions[index]["closes_at"]) or
                    index + 1 < len(sessions) and available >= timestamp(sessions[index+1]["opens_at"])):
                raise ValueError("bar availability must follow completion and precede next open")
    return {s["session_date"]: s for s in sessions}


def features(history):
    closes = [number(r["close"]) for r in history]
    atr = None
    if len(history) >= 15:
        window = history[-15:]
        ranges = [true_range(float(b["high"]), float(b["low"]), float(a["close"])) for a, b in zip(window, window[1:])]
        atr = str(atr_simple_last(ranges, 14))
    return {"sma50": str(mean(closes[-50:])) if len(closes) >= 50 else None,
            "sma200": str(mean(closes[-200:])) if len(closes) >= 200 else None, "atr14": atr}


def evaluate(rows, calendar, symbol, security_id, price_sha, config, *, start, end, context=None, events=None):
    """Pure deterministic evaluation on explicit complete expected sessions.

    Optional event evidence affects detection only if historically public strictly
    before the decision. Retrospective unknown ex-dates never become overlap flags.
    MarketContext is attached after detection and never gates it.
    """
    with localcontext(Context(prec=28)):
        return _evaluate(rows, calendar, symbol, security_id, price_sha, config,
                         start=start, end=end, context=context, events=events)


def _evaluate(rows, calendar, symbol, security_id, price_sha, config, *, start, end, context, events):
    shared_identity()
    if not rows or start > end or not rows[0]["session_date"] <= start <= end <= rows[-1]["session_date"]:
        raise ValueError("evaluation must stay inside frozen price coverage")
    by_day = validate_history(rows, calendar, symbol, security_id)
    setups, triggers, signals, plans, links, exclusions, lifecycle = [], [], [], [], [], [], []
    active = []
    evaluable = attempts = 0
    for i, row in enumerate(rows):
        day = row["session_date"]
        if not start <= day <= end:
            continue
        completed = timestamp(by_day[day]["closes_at"])
        available = completed + timedelta(minutes=config.delay_minutes)
        if row.get("available_at") is not None:
            available = max(available, timestamp(row["available_at"]))
        available_at = available.isoformat()
        future = [s["session_date"] for s in calendar["sessions"] if s["session_date"] > day and timestamp(s["opens_at"]) >= available]
        history = rows[:i+1]
        f = features(history)
        boundary = prior_boundary(rows[:i], config, price_sha)
        known = events.as_known(available_at)["events"] if events is not None else []
        known_actions = [e for e in known if e["event_type"] in {"SPLIT", "DIVIDEND"} and e["effective_date"] is not None]
        def discontinuity(first):
            return [e["event_id"] for e in known_actions if first <= e["effective_date"] <= day]

        def emit(setup, trigger):
            sid = identity("signal", setup.setup_id, asdict(trigger))
            link = context.context_as_of(available_at) if context is not None else {
                "status": "UNAVAILABLE", "reason": "NO_CONTEXT_BUNDLE", "decision_timestamp": available_at,
                "historical_dissemination_verified": False}
            link = {"signal_id": sid, "context_bundle_sha256": context.content_sha256 if context else None, **link}
            linkid = digest(encode(link))
            links.append({"link_sha256": linkid, **link})
            signal = Signal(sid, config.strategy_id, "1", config.sha256, security_id, symbol, setup, trigger,
                            {"boundary": setup.boundary.latest_input_session, "sma50": day if f["sma50"] else None,
                             "sma200": day if f["sma200"] else None, "atr14": day if f["atr14"] else None,
                             "latest_price_input": day}, f, linkid, price_sha,
                            {"availability": "RECONSTRUCTED_NOT_VERIFIED_HISTORICAL_DISSEMINATION",
                             "price_basis": "RESEARCH_ONLY_UNLESS_SEPARATELY_ADMITTED",
                             "corporate_action_archive": "INCOMPLETE; unknown ex-dates global, never presumed overlaps"})
            triggers.append(asdict(trigger)); signals.append(asdict(signal))
            plans.append(asdict(build_plan(signal, row["close"], f["atr14"], future, config)))

        # Confirm old attempts against their original boundary, before adding new
        # ones. Each independent attempt gets exactly one terminal outcome.
        remaining = []
        for attempt_index, setup in active:
            age = i-attempt_index
            action_ids = discontinuity(setup.boundary.window_start)
            trigger = evaluate_trigger(setup, row, available_at, failed=True)
            outcome = "INVALIDATED_CORPORATE_ACTION" if action_ids else "CONFIRMED" if trigger else "EXPIRED" if age >= config.failure_sessions else None
            if outcome:
                lifecycle.append({"setup_id": setup.setup_id, "session_date": day, "available_at": available_at,
                                  "outcome": outcome, "following_sessions_seen": age, "action_event_ids": action_ids})
                if outcome == "CONFIRMED": emit(setup, trigger)
            else: remaining.append((attempt_index, setup))
        active = remaining
        reasons = []
        if boundary is None: reasons.append("BOUNDARY_WARMUP")
        if f["atr14"] is None: reasons.append("ATR14_WARMUP")
        if config.strategy_id == CONTINUATION:
            if f["sma50"] is None: reasons.append("SMA50_WARMUP")
            if f["sma200"] is None: reasons.append("SMA200_WARMUP")
        length = max(config.lookback_sessions+1, 200 if config.strategy_id == CONTINUATION else 15)
        action_ids = discontinuity(history[max(0, len(history)-length)]["session_date"])
        if action_ids: reasons.append("KNOWN_CORPORATE_ACTION_IN_FEATURE_WINDOW")
        if reasons:
            exclusions.append({"session_date": day, "available_at": available_at, "reasons": reasons, "action_event_ids": action_ids})
            continue
        evaluable += 1
        attempt = number(row["high"]) > number(boundary.value)
        attempts += int(attempt)
        if config.strategy_id == CONTINUATION:
            if not number(row["close"]) > number(f["sma50"]) > number(f["sma200"]):
                exclusions.append({"session_date": day, "available_at": available_at, "reasons": ["TREND_GATE_FAILED"], "action_event_ids": []})
                continue
        elif not attempt:
            continue
        setup = Setup(identity("setup", config.sha256, security_id, price_sha, day, asdict(boundary)),
                      config.strategy_id, day, available_at, boundary)
        setups.append(asdict(setup))
        if config.strategy_id == CONTINUATION:
            trigger = evaluate_trigger(setup, row, available_at)
            if trigger: emit(setup, trigger)
        elif number(row["close"]) < number(boundary.value):
            lifecycle.append({"setup_id": setup.setup_id, "session_date": day, "available_at": available_at,
                              "outcome": "IMMEDIATE_FAILURE_OBSERVATION_ONLY", "following_sessions_seen": 0, "action_event_ids": []})
        else:
            active.append((i, setup))
    for _, setup in active:
        lifecycle.append({"setup_id": setup.setup_id, "session_date": end,
                          "outcome": "PENDING_END_OF_EVALUATION", "available_at": None, "action_event_ids": []})
    states = Counter(link.get("context", {}).get("descriptive_state") or "UNAVAILABLE" for link in links)
    incomplete = sum(any(r != "TREND_GATE_FAILED" for r in e["reasons"]) for e in exclusions)
    quality = {"evaluation_sessions": sum(start <= r["session_date"] <= end for r in rows),
               "evaluable_sessions": evaluable, "setup_observations": len(setups), "breakout_attempts": attempts,
               "confirmed_triggers": len(signals), "failed_break_confirmations": len(signals) if config.strategy_id == FAILED else 0,
               "incomplete_unavailable_observations": incomplete, "excluded_observations": len(exclusions),
               "context_available": sum(link["status"] != "UNAVAILABLE" for link in links),
               "context_unavailable": sum(link["status"] == "UNAVAILABLE" for link in links),
               "context_state_counts": dict(sorted(states.items())), "lifecycle_outcomes": dict(Counter(r["outcome"] for r in lifecycle)),
               "fills": "NOT_COMPUTED_RESEARCH_MODE", "performance": "NOT_COMPUTED"}
    return {"setup_observations": setups, "triggers": triggers, "signals": signals, "trade_plans": plans,
            "market_context_links": links, "exclusions": exclusions, "setup_outcomes": lifecycle, "quality_report": quality}
