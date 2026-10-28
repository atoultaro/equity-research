"""Twenty-six episode comparisons and challenges to earlier management hypotheses."""

from collections import Counter, defaultdict
from statistics import median

from ..models import timestamp
from .admission import Evidence, value
from .entries import candidates
from .management import POLICIES, trajectory
from .timing import clock_variants
from .basis import stop_scale_diagnostics


def rank(plans):
    comparable = [s for p in plans for s in p["management"] if s["rank_eligible"]]
    vectors = sorted({tuple(s["evaluation_vector"]) for s in comparable})
    for p in plans:
        for s in p["management"]:
            s["rank"] = 1+vectors.index(tuple(s["evaluation_vector"])) if s["rank_eligible"] else None
    leading = [{"candidate_id": p["candidate_id"], "hypothesis": p["hypothesis"], "policy": s["policy"],
        "entry_session": p["entry_session"], "entry_price": p["entry_price"], "entry_kind": p["entry_kind"],
        "reference_risk_ATR": p.get("geometry", {}).get("reference_risk_ATR"),
        "evaluation_vector": s["evaluation_vector"], "pending_review": s["pending_review_at_end"]}
        for p in plans for s in p["management"] if s["rank"] == 1]
    equivalence = defaultdict(list)
    for p in plans:
        for s in p["management"]:
            if s["rank_eligible"]:
                signature = tuple((o["event_id"], o["status"]) for o in s["observations"])
                equivalence[signature].append({"candidate_id": p["candidate_id"], "policy": s["policy"]})
    return {"leading": leading, "observational_equivalence_classes": [v for v in equivalence.values() if len(v) > 1],
        "ranking_identifies_actual_execution": False,
        "confidence": "NO_OBSERVED_ENTRY_TO_RANK" if not comparable else
                      "CONSTRUCTION_ONLY_NO_LATER_SOURCE_ACTIONS" if not any(s["compatible_alert_clusters"] or s["conflict_alert_clusters"] for s in comparable) else
                      "CONDITIONAL_COMPATIBILITY_MULTIPLE_EXECUTIONS_UNIDENTIFIED",
        "unranked_does_not_mean_no_actual_trade": True}


def revision_rows(trade, plans, evidence, clock):
    output = []
    sign = 1 if trade["direction"] == "LONG" else -1
    for event in trade["events"]:
        if event["type"] not in {"STOP_CHANGED", "SETUP_CHANGED", "DROPPED"}:
            continue
        cutoff = clock["assumed_action_clocks"][event["source"]["alert_id"]]
        day, f = evidence.features(trade["symbol"], cutoff)
        c, atr = value(f, "close"), value(f, "atr14")
        prior = [p for p in plans if p["status"] == "CONSTRUCTED" and p["entry_session"] and
            timestamp(p["entry_time_interval"][1]) < timestamp(cutoff)]
        progress = [sign*(c-p["entry_price"]) for p in prior] if c is not None else []
        output.append({"trade_id": trade["trade_id"], "symbol": trade["symbol"], "direction": trade["direction"],
            "event_id": event["event_id"], "action": event["type"], "source_published_at": event["published_at"],
            "clock_variant": clock["name"], "assumed_cutoff": cutoff, "feature_session": day,
            "counterfactual_price_progress_range": [min(progress), max(progress)] if progress else None,
            "progress_interpretation": "Quote difference from constructed entry references, including after hypothetical closure; never current held-position PnL",
            "candidate_entry_count": len(prior), "favorable_for_all_constructed_entries": min(progress) > 0 if progress else None,
            "old_stop": event.get("previous_stop"), "new_stop": event.get("stop"),
            "stop_change": ("TIGHTENING" if sign*(float(event["stop"])-float(event["previous_stop"])) > 0 else "WIDENING") if event["type"] == "STOP_CHANGED" else None,
            "old_stop_clearance_ATR": sign*(c-float(event["previous_stop"]))/atr if c is not None and atr and event.get("previous_stop") else None,
            "new_stop_distance_to_levels_ATR": {k: (float(event["stop"])-(v["price"] if isinstance(v, dict) else v))/atr
                for k in ("sma20", "sma50", "confirmed_swing_low", "confirmed_swing_high")
                if (v := value(f, k)) is not None and atr} if event.get("stop") else {},
            "market": {p: evidence.panel.relative(trade["symbol"], p, day, 20) if day else None for p in ("SPY", "QQQ", "RSP", "IWM")},
            "native_features": {k: f.get(k) for k in ("close_sma20", "close_sma50", "return20", "breakout20", "breakdown20", "range_contraction10_previous20", "atr14")}})
    return output


def source_projection(trade):
    return {k: v for k, v in trade.items() if k != "events"} | {"events": [
        {k: ({sk: sv for sk, sv in v.items() if sk != "source_text"} if k == "source" else v)
         for k, v in e.items()} for e in trade["events"]]}


def derive(parent, inputs, config):
    spec, alerts, prices, coverage, calendar, _ = inputs
    evidence = Evidence(prices, coverage, calendar, spec["analysis_cutoff"])
    clocks = clock_variants(alerts["alerts"], calendar)
    trades = parent["source_trade_lifecycles.json"]
    all_revisions, episodes = [], []
    for trade in trades:
        versions = []
        risk_points = []
        for clock in clocks:
            plans = candidates(trade, evidence, clock, trigger_sessions=config["trigger_valid_sessions"])
            for p in plans:
                p["management"] = [trajectory(trade, p, clock, evidence.rows(trade["symbol"]), calendar,
                    spec["analysis_cutoff"], policy) for policy in POLICIES]
                if p["status"] == "CONSTRUCTED" and p["geometry"]["reference_risk_ATR"] is not None:
                    risk_points.append(p["geometry"]["reference_risk_ATR"])
            ranking = rank(plans)
            all_revisions.extend(revision_rows(trade, plans, evidence, clock))
            versions.append({"clock_variant": clock["name"], "candidates": plans, **ranking})
        episodes.append({"trade_id": trade["trade_id"], "symbol": trade["symbol"], "direction": trade["direction"],
            "source": source_projection(trade), "clock_comparisons": versions,
            "conditional_entry_risk_ATR_reference_range": [min(risk_points), max(risk_points)] if risk_points else None,
            "actual_entry_price": None, "actual_exit_reason": None, "actual_realized_pnl": None,
            "questions": ["Actual entry/activation convention and timing unknown", "Native/nominal stop-scale compatibility assumed unless session quote-anchored",
                "Daily extrema do not identify intraday ordering", "Reported stop may be hard, closing or discretionary; testable alternatives are not observed policies"]})
    baseline = [r for r in all_revisions if r["clock_variant"] == "LATE_EMAIL_BOUND"]
    stop_changes = [r for r in baseline if r["action"] == "STOP_CHANGED"]
    comparisons = {}
    for direction in ("LONG", "SHORT"):
        group = [e for e in episodes if e["direction"] == direction]
        risks = [median(e["conditional_entry_risk_ATR_reference_range"]) for e in group if e["conditional_entry_risk_ATR_reference_range"]]
        comparisons[direction] = {"source_episodes": len(group), "usable_risk_episodes": len(risks),
            "median_episode_midrange_reference_risk_ATR": median(risks) if risks else None,
            "risk_interpretation": "Per-episode midrange of conditional candidate reference risks, not actual risk or independent fills",
            "stop_change_counts": dict(Counter(r["stop_change"] for r in stop_changes if r["direction"] == direction))}
    same_alert = defaultdict(lambda: {"LONG": [], "SHORT": []})
    pattern_rows = []
    for episode in episodes:
        late = next(c for c in episode["clock_comparisons"] if c["clock_variant"] == "LATE_EMAIL_BOUND")
        plan = late["candidates"][0]
        f = plan["construction"]["features"]
        atr, close = value(f, "atr14"), value(f, "close")
        if plan["status"] == "CONSTRUCTED" and plan["geometry"]["reference_risk_ATR"] is not None:
            same_alert[episode["source"]["events"][0]["source"]["alert_id"]][episode["direction"]].append(
                {"symbol": episode["symbol"], "reference_risk_ATR": plan["geometry"]["reference_risk_ATR"]})
        price = evidence.rows(episode["symbol"]).get(plan["entry_session"])
        sign = 1 if episode["direction"] == "LONG" else -1
        first_progress = sign*(float(price["close"])-plan["entry_price"])/atr if price and atr and plan["entry_price"] is not None else None
        pattern_rows.append({"symbol": episode["symbol"], "direction": episode["direction"],
            "trend_aligned": plan["construction"]["directional_trend_aligned"],
            "range10_over_previous20": value(f, "range_contraction10_previous20"),
            "native_ATR_over_close": atr/close if atr and close else None,
            "pullback_to_MA_within_1ATR": min(abs(close-v) for k in ("sma20", "sma50") if (v := value(f, k)) is not None) <= atr
                if close is not None and atr and any(value(f, k) is not None for k in ("sma20", "sma50")) else None,
            "failed_breakout20": value(f, "failed_breakout20"), "breakdown20": value(f, "breakdown20"),
            "bounce_in_downtrend": value(f, "return20") < 0 and value(f, "return5") > 0 and value(f, "close_sma50") < 0
                if all(value(f, k) is not None for k in ("return20", "return5", "close_sma50")) else None,
            "H1_first_session_reference_price_progress_ATR": first_progress,
            "progress_is_not_current_exposure_or_realized_pnl": True,
            "diagnostics_attribution": "AGENT_PREDECLARED_TESTABLE_DESCRIPTIONS_NOT_DOCUMENTED_GRIMES_RULES"})
    challenges = []
    for kind in ("TIGHTENING", "WIDENING"):
        group = [r for r in stop_changes if r["stop_change"] == kind]
        usable = [r for r in group if r["counterfactual_price_progress_range"]]
        challenges.append({"stop_change": kind, "total": len(group), "usable": len(usable),
            "robust_favorable": [r["event_id"] for r in usable if r["counterfactual_price_progress_range"][0] > 0],
            "counterexamples_or_entry_sensitive": [r["event_id"] for r in usable if r["counterfactual_price_progress_range"][0] <= 0],
            "unavailable": [r["event_id"] for r in group if r not in usable],
            "comparison_to_pr17": "Includes explicit alternative entry references; quote progress is not censored or relabeled current exposure after hypothetical exits"})
    all_plans = [p for e in episodes for c in e["clock_comparisons"] for p in c["candidates"]]
    for p in all_plans:
        # Keep the machine-readable comparison compact without dropping the
        # construction measurements actually used by these fixed hypotheses.
        features = p["construction"]["features"]
        p["construction"]["features"] = {k: features[k] for k in (
            "close", "atr14", "sma20", "sma50", "sma200", "close_sma50", "sma50_slope20", "return20", "prior20_high", "prior20_low",
            "confirmed_swing_low", "confirmed_swing_high", "breakout20", "breakdown20", "failed_breakout20", "return5", "range_contraction10_previous20") if k in features}
    summary = {"episodes": len(episodes), "source_actions": sum(len(t["events"]) for t in trades),
        "entry_candidate_status_counts": dict(Counter(p["status"] for p in all_plans)),
        "clock_variants_are_not_independent_trades": True, "direction_comparison": comparisons,
        "pr17_challenges": challenges, "underway_inventory": [r for r in baseline if r["action"] == "SETUP_CHANGED"],
        "drop_inventory": [r for r in baseline if r["action"] == "DROPPED"],
        "same_opening_alert_risk_comparisons": dict(same_alert), "opening_pattern_diagnostics": pattern_rows,
        "no_realized_profit_or_edge_claim": True}
    return {"episodes.json": episodes, "management_decisions.json": all_revisions, "summary.json": summary,
        "timing_bounds.json": clocks, "price_scale_diagnostics.json": stop_scale_diagnostics(trades, prices, coverage, spec["basis_evidence"]),
        "admission.json": evidence.admission}
