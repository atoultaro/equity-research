"""Descriptive measurements only; source records and modeled exits are inputs."""

from collections import Counter
from datetime import timedelta
from decimal import Decimal
from statistics import mean, median

from ..comprehension.features import Panel
from ..events.model import timestamp
from ..lifecycle.model import compatible
from ..lifecycle.source import UNIVERSE

DEFINITIONS = {
    "decision_clock": "Immediately before PR16 effective_at: subtract one microsecond; original publication and email bound remain separate",
    "price_availability": "PR16 XNYS cash close +60 minutes strictly before decision bound; no current intraday candle",
    "entry": "Unchanged PR16 next eligible RTH Open scenario; actual fills and size unknown",
    "progress": "s*(Close-E), percent=100*s*(Close-E)/E; s=+1 LONG,-1 SHORT",
    "mfe": "max(0,max(High-E)) LONG; max(0,max(E-Low)) SHORT, over complete eligible active-session bars",
    "mae": "max(0,max(E-Low)) LONG; max(0,max(High-E)) SHORT; reported as a nonnegative adverse excursion",
    "risk": "Unchanged PR16 hypothetical original R: E-initial_stop LONG, initial_stop-E SHORT; revisions never reset R",
    "atr": "Existing Panel/shared-wheel simple ATR14; progress/excursions use pre-entry ATR, stop adjustments use pre-decision ATR",
    "exit_censoring": "Exclude all price-trigger/ambiguous exit-day OHLC: daily extrema/Close may follow exit; earlier full-session path is a separate pre-exit summary",
    "source_drop_censoring": "Source DROP only known when its own bound is strictly before cutoff; after-hours modeled source closure may retain earlier completed RTH bar",
    "stop_change_percent": "100*(new-old)/old, source-only; direction-aware tightening sign=s*(new-old)",
    "stop_adjustment_atr": "s*(new-old)/pre-decision ATR14; conditional unless nominal stop/native units corroborated",
    "previous_stop_clearance": "s*(Close-old_stop), divided by Close for percent or pre-decision ATR; this is a price observation, not post-exit exposure",
    "near_stop": "abs(Close-old_stop)/ATR14 <=1; fixed agent-defined descriptive cut, not fitted or a Grimes rule",
    "sma10": "Arithmetic mean of exactly10 available completed Closes; Close/SMA10-1; SMA20/50 reused from Panel",
    "swing": "Most recent Panel strict3-bar pivot confirmed by the previous available session; protective Low for LONG, High for SHORT; never choose pivot after seeing revised stop",
    "recent_swing_distances": "For both currently confirmed High/Low: Close-level, 100*(Close/level-1), and (Close-level)/pre-decision ATR; currently confirmed levels are distinct from the stricter previous-session protective-pivot hypothesis",
    "toward_swing": "abs(new_stop-preexisting_protective_pivot) < abs(old_stop-pivot); equality is not toward",
    "relative_strength": "Panel ratio_change: (stock_t/proxy_t)/(stock_t-n/proxy_t-n)-1 on matching calendar sessions, n=1,5,20,60",
    "market_weakness": "SPY daily price return <0; rebound proxy=positive SPY day with negative trailing5-session return; not a causal regime classification",
    "volatility_expansion": "SPY realized_volatility20 now / prior available session value >1; continuous ratio retained",
    "elapsed_sessions": "Count eligible calendar sessions since scenario entry with cash-close+60 minutes before bound, never count rows after skipping gaps",
    "duration": "Publication-based eligible completed-session count/range, not actual holding duration; unknown weekly publication stays null; email-bound scenario separately labeled",
    "matched_controls": "Other source-OPEN ENTERABLE episodes at their first alert opportunity after the same Hth eligible session, before H+1 session and no later than target transition bound; evaluate whole co-published alert; no future final-state filtering",
    "time_stop": "Reuse PR16 available 2/3/5-session nonpositive-progress exploratory flags known before source closure; no definitive time exit",
    "inference": "Selected discovery sample; report observations, counterexamples and usable denominators; no optimization, significance, realized P&L or causal identification",
}


def number(value):
    return None if value is None else round(float(value), 12)


def rate(numerator, denominator, definition):
    return {"numerator": numerator, "denominator": denominator,
        "fraction": numerator/denominator if denominator else None, "denominator_definition": definition}


def distribution(values, total):
    values = sorted(float(v) for v in values if v is not None)
    return {"usable": len(values), "total": total, "missing": total-len(values),
        "min": values[0] if values else None, "median": median(values) if values else None,
        "max": values[-1] if values else None, "values": values}


def excursions(rows, entry, direction, atr=None, original_r=None):
    """Caller supplies a complete, already censored path. No stop/target simulation."""
    if not rows:
        return None
    e, sign = Decimal(str(entry)), 1 if direction == "LONG" else -1
    progress = (Decimal(rows[-1]["close"])-e)*sign
    mfe = max([Decimal(0)]+[(Decimal(r["high" if sign == 1 else "low"])-e)*sign for r in rows])
    mae = max([Decimal(0)]+[(e-Decimal(r["low" if sign == 1 else "high"]))*sign for r in rows])
    out = {"first_session": rows[0]["session_date"], "last_session": rows[-1]["session_date"], "observed_sessions": len(rows)}
    for name, value in (("progress", progress), ("mfe", mfe), ("mae", mae)):
        out[name+"_price"] = number(value)
        out[name+"_percent"] = number(100*value/e)
        out[name+"_ATR"] = number(value/Decimal(str(atr))) if atr else None
        out[name+"_original_R"] = number(value/Decimal(str(original_r))) if original_r else None
    return out


class Evidence:
    def __init__(self, parent, inputs):
        self.parent = parent
        self.spec, _, self.prices, self.coverage, self.calendar, _ = inputs
        self.sessions = self.calendar["sessions"]
        self.session = {s["session_date"]: s for s in self.sessions}
        self.panels, self.features_cache, self.entry_atr_cache = {}, {}, {}
        self.basis = {r["symbol"]: r for r in self.spec["basis_evidence"]}
        self.proxies = {r["symbol"]: r for r in self.spec["sector_proxies"]}
        self.trades = parent["source_trade_lifecycles.json"]
        self.primary = {m["trade_id"]: m for m in parent["modeled_trade_lifecycles.json"]}
        self.conditional = {m["trade_id"]: m for m in parent["conditional_basis_trade_lifecycles.json"]}

    def panel(self, bound):
        if not bound:
            return None
        if bound not in self.panels:
            self.panels[bound] = Panel(self.prices, self.coverage, self.calendar,
                (timestamp(bound)-timedelta(microseconds=1)).isoformat())
        return self.panels[bound]

    def features(self, panel, symbol, end=None):
        end = end or (panel.days[-1] if panel.days else None)
        key = symbol, end
        if key not in self.features_cache:
            self.features_cache[key] = panel.features(symbol, end)
        return self.features_cache[key]

    def quote_basis(self, symbol, days):
        rows = {r["session_date"]: r for r in self.prices[symbol]}
        c = self.coverage[symbol]
        return bool(days) and compatible(self.basis.get(symbol), c["contract"], rows, days, c["origin"])

    def known_model_events(self, model, bound):
        known = []
        if not bound:
            return known
        for event in model["events"]:
            d = event["session_date"]
            if event["type"] not in {"MODELED_CLOSED", "ASSUMED_STOP_TRIGGERED", "HYPOTHETICAL_TARGET_REACHED"}:
                continue
            clock = event.get("source_closure_effective_bound")
            if clock is None and d in self.session:
                clock = (timestamp(self.session[d]["closes_at"])+timedelta(minutes=60)).isoformat()
            if clock and timestamp(clock) < timestamp(bound):
                known.append(event)
        return known

    def path(self, trade, bound, *, conditional):
        model = (self.conditional if conditional else self.primary)[trade["trade_id"]]
        panel = self.panel(bound)
        result = {"status": "UNRESOLVED_TIME", "attribution": "HYPOTHETICAL_ENTRY_NOT_VERIFIED_EXPOSURE",
            "basis_interpretation": "CONDITIONAL_UNVERIFIED_STOP_UNITS" if conditional else "PRIMARY_CORROBORATED_STOP_UNITS_ONLY",
            "actual_entry": None, "entry": None, "original_R": None,
            "entry_rule": model["entry_rule"], "first_eligible_at": model["first_eligible_at"],
            "current_progress": None, "pre_exit_or_active_path": None, "known_exit_events": [], "elapsed_eligible_sessions": None}
        if not panel or not model["first_eligible_at"]:
            return result
        known_order = max((e["source_order"] for e in self.parent["source_events.json"]
            if e["effective_at"] and timestamp(e["effective_at"]) <= timestamp(bound)), default=-1)
        if any(e["effective_at"] is None and e["source_order"] <= known_order for e in trade["events"]):
            result["status"] = "UNRESOLVED_PRIOR_SOURCE_TIMING"
            return result
        entry_day = timestamp(model["first_eligible_at"]).date().isoformat()
        days = [d for d in panel.days if d >= entry_day]
        result["elapsed_eligible_sessions"] = len(days)
        if not model["modeled_entry"] or not days:
            result["status"] = "NO_ELIGIBLE_COMPLETED_ENTRY_SESSION"
            return result
        if not any(r["session_date"] == entry_day for r in self.prices[trade["symbol"]]):
            result["status"] = "MISSING_EXPECTED_ENTRY_SESSION"
            return result
        result["entry"] = model["modeled_entry"]
        if not conditional and not self.quote_basis(trade["symbol"], days):
            result["status"] = "UNVERIFIED_BASIS"
            return result
        result["original_R"] = model["original_per_share_risk"]
        known = self.known_model_events(model, bound)
        result["known_exit_events"] = known
        result["resolved_target_excursion_lower_bound_R"] = 1 if any(
            e["type"] == "HYPOTHETICAL_TARGET_REACHED" and e.get("status") != "CANDIDATE_ORDER_UNKNOWN" for e in known) else None
        price_boundaries = [e["session_date"] for e in known if e["type"] == "MODELED_CLOSED"
            and e["cause"] != "SOURCE_REPORTED_DROPPED_PRICE_AND_EXECUTION_UNKNOWN"]
        price_boundaries += [e["session_date"] for e in known if e.get("status") == "CANDIDATE_ORDER_UNKNOWN"]
        excluded = min(price_boundaries) if price_boundaries else None
        safe = [d for d in days if not excluded or d < excluded]
        closes = [e for e in known if e["type"] == "MODELED_CLOSED"]
        for event in closes:
            if event["cause"] == "SOURCE_REPORTED_DROPPED_PRICE_AND_EXECUTION_UNKNOWN":
                closure = timestamp(event["source_closure_effective_bound"])
                safe = [d for d in safe if timestamp(self.session[d]["closes_at"])+timedelta(minutes=60) < closure]
        result["excluded_exit_or_ambiguous_session"] = excluded
        rows = {r["session_date"]: r for r in self.prices[trade["symbol"]] if r["session_date"] in safe}
        if any(d not in rows for d in safe):
            result["status"] = "MISSING_EXPECTED_ACTIVE_SESSION"
            return result
        key = trade["trade_id"]
        if key not in self.entry_atr_cache:
            pre = self.panel(model["first_eligible_at"])
            self.entry_atr_cache[key] = self.features(pre, trade["symbol"])["atr14"]["value"]
        metrics = excursions([rows[d] for d in safe], model["modeled_entry"], trade["direction"],
            self.entry_atr_cache[key], result["original_R"])
        result["pre_entry_ATR"] = self.entry_atr_cache[key]
        result["pre_exit_or_active_path"] = metrics
        if closes or excluded:
            result["status"] = "MODELED_CLOSED_BEFORE_DECISION" if closes else "AMBIGUOUS_EXIT_PATH"
        elif not metrics:
            result["status"] = "NO_COMPLETE_ACTIVE_BAR"
        else:
            result["status"] = "AVAILABLE_AT_LAST_OBSERVABLE_SESSION"
            result["current_progress"] = metrics
        return result

    def row(self, trade, event):
        bound, symbol = event["effective_at"], trade["symbol"]
        earlier = [e for e in trade["events"] if e["effective_at"] and bound
            and timestamp(e["effective_at"]) < timestamp(bound)]
        previous = next((e["stop"] for e in reversed(earlier) if "stop" in e), None)
        in_sequence = [e for e in trade["events"] if e["source_order"] <= event["source_order"] and "stop" in e]
        latest = in_sequence[-1]["stop"] if in_sequence else None
        r = {"event_id": event["event_id"], "trade_id": trade["trade_id"], "symbol": symbol, "direction": trade["direction"],
            "type": event["type"], "source_order": event["source_order"], "source_published_at": event["published_at"],
            "decision_bound": bound, "effective_clock": event["effective_clock"], "source_setup_before": event["setup_before"],
            "source_setup_after": event["setup_after"], "initial_stop": trade["initial_stop"],
            "stop_known_before_alert": previous, "latest_stop_in_source_sequence": latest,
            "source_action": {k: event[k] for k in ("type", "stop", "previous_stop", "setup_availability") if k in event},
            "source_locator": {k: v for k, v in event.get("source", {}).items() if k != "source_text"},
            "primary_path": self.path(trade, bound, conditional=False), "conditional_path": self.path(trade, bound, conditional=True)}
        r["modeled_closed_before_source_decision"] = {label: (
            None if r[key]["status"] == "UNVERIFIED_BASIS" else any(e["type"] == "MODELED_CLOSED"
                and e["cause"] != "SOURCE_REPORTED_DROPPED_PRICE_AND_EXECUTION_UNKNOWN" for e in r[key]["known_exit_events"]))
            for label, key in (("primary", "primary_path"), ("conditional", "conditional_path"))}
        panel = self.panel(bound)
        if not panel:
            return {**r, "last_available_session": None, "native_features": None, "relative_strength": {},
                "native_swing_distances": None,
                "primary_stop_comparison": None, "conditional_stop_comparison": None,
                "primary_stop_comparison_status": "UNRESOLVED_DECISION_TIME"}
        end = panel.days[-1] if panel.days else None
        f = self.features(panel, symbol)
        prev = self.features(panel, symbol, panel.days[-2]) if len(panel.days) > 1 else None
        bars10, days10, why = panel.window(symbol, end, 10)
        sma10 = mean(b["close"] for b in bars10) if bars10 else None
        f = {**f, "sma10": {"value": sma10, "reason": why},
            "close_sma10": {"value": f["close"]["value"]/sma10-1 if f["close"]["value"] is not None and sma10 else None, "reason": why}}
        p = self.proxies[symbol]["proxy"]
        relative = {proxy: {str(n): panel.relative(symbol, proxy, end, n) for n in (1, 5, 20, 60)}
            for proxy in ("SPY", "QQQ", "RSP", "IWM")+( (p,) if p else ())}
        kind = "low" if trade["direction"] == "LONG" else "high"
        pivot = prev[f"confirmed_swing_{kind}"]["value"] if prev else None
        c, atr = f["close"]["value"], f["atr14"]["value"]
        swing_distances = {}
        for side in ("high", "low"):
            level = f[f"confirmed_swing_{side}"]["value"]
            price = level["price"] if level else None
            swing_distances[side] = {"pivot": level, "attribution": "NATIVE_PRICE_OBSERVED_ASOF_NO_EXPERT_LEVEL_CLAIM",
                "close_minus_level_price": number(c-price) if c is not None and price is not None else None,
                "close_vs_level_percent": number(100*(c/price-1)) if c is not None and price else None,
                "close_minus_level_ATR": number((c-price)/atr) if c is not None and price is not None and atr else None}
        comparison = None
        old = event.get("previous_stop", previous)
        new = event.get("stop", latest)
        if old is not None and c is not None:
            old, new, close = Decimal(old), Decimal(new) if new is not None else None, Decimal(str(c))
            sign = 1 if trade["direction"] == "LONG" else -1
            clearance = (close-old)*sign
            comparison = {"attribution": "PRICE_OBSERVATION_NOT_POST_EXIT_POSITION_PROGRESS", "old_stop": str(old),
                "stop_clearance_price": number(clearance), "stop_clearance_percent": number(100*clearance/close),
                "stop_clearance_ATR": number(clearance/Decimal(str(atr))) if atr else None,
                "near_previous_stop_1ATR": abs(clearance)/Decimal(str(atr)) <= 1 if atr else None,
                "price_on_or_beyond_old_stop": clearance <= 0,
                "initial_stop_distance_ATR": number((close-Decimal(trade["initial_stop"]))*sign/Decimal(str(atr))) if atr else None,
                "latest_source_stop_distance_ATR": number((close-Decimal(latest))*sign/Decimal(str(atr))) if atr and latest else None,
                "adjustment_ATR": number((new-old)*sign/Decimal(str(atr))) if new is not None and atr else None,
                "preexisting_protective_swing": pivot,
                "close_to_swing_ATR": number((close-Decimal(str(pivot["price"])))/Decimal(str(atr))) if pivot and atr else None,
                "old_stop_to_swing_ATR": number(abs(old-Decimal(str(pivot["price"])))/Decimal(str(atr))) if pivot and atr else None,
                "new_stop_to_swing_ATR": number(abs(new-Decimal(str(pivot["price"])))/Decimal(str(atr))) if pivot and atr and new is not None else None,
                "moves_toward_preexisting_swing": abs(new-Decimal(str(pivot["price"]))) < abs(old-Decimal(str(pivot["price"]))) if pivot and new is not None else None}
        primary_ok = self.quote_basis(symbol, [end])
        return {**r, "last_available_session": end, "native_features": f, "relative_strength": relative,
            "native_swing_distances": swing_distances,
            "sector_proxy": self.proxies[symbol], "primary_stop_comparison": comparison if primary_ok else None,
            "primary_stop_comparison_status": "BOUNDED_PR16_QUOTE_SCALE" if primary_ok else "UNVERIFIED_STOP_NATIVE_BASIS",
            "conditional_stop_comparison": comparison, "stop_comparison_basis": "CONDITIONAL_UNVERIFIED_STOP_UNITS_UNLESS_PRIMARY_PRESENT"}


def duration(trade, context):
    op = trade["events"][0]
    close = trade["events"][-1] if trade["position_state"] == "CLOSED" else None
    end = close["effective_at"] if close else context.spec["analysis_cutoff"]
    start = op["effective_at"]
    count = lambda a, b: sum(timestamp(a) <= timestamp(s["opens_at"])
        and timestamp(s["closes_at"])+timedelta(minutes=60) < timestamp(b) for s in context.sessions)
    chosen = count(start, end) if start and end else None
    known = bool(op["published_at"] and (not close or close["published_at"]))
    exact_range = [count(start, close["published_at"] if close else end),
        count(op["published_at"], end)] if known else None
    # A sequence bracket is explicitly conditional; it does not resolve the weekly date.
    alerts = context.parent["alerts.json"]["alerts"]

    def bounds(event):
        if event["published_at"]:
            return event["published_at"], event["effective_at"]
        aid = event.get("source", {}).get("alert_id")
        i = next((i for i, a in enumerate(alerts) if a["alert_id"] == aid), None)
        previous = next((a["published_at"] for a in reversed(alerts[:i]) if a["published_at"]), None) if i is not None else None
        return previous, event["effective_at"]

    lo_open, hi_open = bounds(op)
    lo_close, hi_close = bounds(close) if close else (end, end)
    bracket = [count(hi_open, lo_close), count(lo_open, hi_close)] if all((lo_open, hi_open, lo_close, hi_close)) else None
    return {"actual_holding_duration": None, "actual_duration_status": "UNKNOWN_FILL_AND_EXECUTION_TIMES",
        "source_publication_elapsed_eligible_sessions": chosen if known else None,
        "publication_based_session_range": exact_range,
        "conditional_ordered_publication_bracket_sessions": bracket,
        "bracket_assumption": "Publication sequence is chronological; prior dated alert supplies lower bound, email availability supplies upper bound; neither is exact weekly publication",
        "email_bound_scenario_eligible_sessions": chosen,
        "uncertainty": None if known else "WEEKLY_ABSOLUTE_PUBLICATION_UNRESOLVED_EMAIL_BOUND_IS_SEPARATE_SCENARIO",
        "source_right_censored": close is None, "source_open_publication": op["published_at"],
        "source_close_publication": close["published_at"] if close else None,
        "open_effective_clock": op["effective_clock"], "end_effective_clock": close["effective_clock"] if close else "FIXED_STUDY_CUTOFF"}


def validate_inventory(parent):
    trades, events = parent["source_trade_lifecycles.json"], parent["source_events.json"]
    counts = Counter(e["type"] for e in events)
    if (len(trades) != 26 or {t["symbol"] for t in trades} != set(UNIVERSE)
            or len(parent["alerts.json"]["alerts"]) != 7
            or counts != {"OPEN_NEW_POSITION": 26, "STOP_CHANGED": 27, "SETUP_CHANGED": 7, "DROPPED": 12}
            or Counter(t["position_state"] for t in trades) != {"CLOSED": 12, "OPEN": 14}
            or Counter(t["direction"] for t in trades) != {"LONG": 14, "SHORT": 12}):
        raise ValueError("PR17 requires the exact frozen PR16 universe, events and final source states")


def matched_controls(context, transitions, rows):
    alerts = sorted({e["effective_at"] for t in context.trades for e in t["events"] if e["effective_at"]}, key=timestamp)
    out = []
    for target in transitions:
        h = target["conditional_path"]["elapsed_eligible_sessions"]
        candidates = []
        for trade in context.trades:
            if trade["trade_id"] == target["trade_id"]:
                continue
            candidate = {"trade_id": trade["trade_id"], "symbol": trade["symbol"], "status": "NO_COMPARABLE_OBSERVATION", "features": None}
            model = context.conditional[trade["trade_id"]]
            if not h or not model["first_eligible_at"]:
                candidates.append(candidate); continue
            eligible = [s for s in context.sessions if timestamp(s["opens_at"]) >= timestamp(model["first_eligible_at"])]
            if len(eligible) < h:
                candidates.append(candidate); continue
            available = timestamp(eligible[h-1]["closes_at"])+timedelta(minutes=60)
            next_open = timestamp(eligible[h]["opens_at"]) if len(eligible) > h else None
            bound = next((a for a in alerts if available < timestamp(a) and timestamp(a) <= timestamp(target["decision_bound"])
                and (next_open is None or timestamp(a) < next_open)), None)
            if not bound:
                candidates.append(candidate); continue
            at = [e for e in trade["events"] if e["effective_at"] and timestamp(e["effective_at"]) <= timestamp(bound)]
            closed = any(e["type"] == "DROPPED" for e in at)
            setup = next((e["setup_availability"] for e in reversed(at) if e["type"] == "SETUP_CHANGED"), "ENTERABLE")
            candidate.update(matched_bound=bound, matched_session=eligible[h-1]["session_date"], setup_at_matched_bound=setup,
                source_closed_at_matched_bound=closed)
            if closed or setup != "ENTERABLE":
                candidate["status"] = "SOURCE_NOT_OPEN_ENTERABLE_AT_MATCH"
            else:
                # Add a tiny epsilon to include all co-published source decisions in model-state screening.
                path = context.path(trade, (timestamp(bound)+timedelta(microseconds=1)).isoformat(), conditional=True)
                candidate["status"] = "ELIGIBLE_CONDITIONAL_COMPARATOR" if path["current_progress"] is not None else path["status"]
                candidate["features"] = path
            candidates.append(candidate)
        chosen = [c for c in candidates if c["status"] == "ELIGIBLE_CONDITIONAL_COMPARATOR"]
        out.append({"transition_event_id": target["event_id"], "symbol": target["symbol"], "horizon_sessions": h,
            "target_progress": target["conditional_path"]["current_progress"], "candidate_count": len(candidates),
            "usable_controls": len(chosen), "controls": candidates,
            "favorable_control_rate": rate(sum(c["features"]["current_progress"]["progress_percent"] > 0 for c in chosen),
                len(chosen), "Eligible conditional controls with current progress, shared across transitions"),
            "control_progress_percent": distribution([c["features"]["current_progress"]["progress_percent"] for c in chosen], len(candidates)),
            "limitations": "Conditional units; different entry/market dates, sectors and directions; overlapping controls; publication opportunities and model-survival censoring; no causal or significance test"})
    return out


def market_snapshots(context, event_rows):
    out = []
    for bound in sorted({r["decision_bound"] for r in event_rows if r["decision_bound"]}, key=timestamp):
        panel = context.panel(bound)
        end = panel.days[-1] if panel.days else None
        f = context.features(panel, "SPY")
        prev = context.features(panel, "SPY", panel.days[-2]) if len(panel.days) > 1 else None
        vol, old = f["realized_volatility20"]["value"], prev["realized_volatility20"]["value"] if prev else None
        ratio = vol/old if vol is not None and old else None
        daily, recent = f["daily_return"]["value"], f["return_5d"]["value"]
        related = [r for r in event_rows if r["decision_bound"] == bound]
        out.append({"decision_bound": bound, "last_available_session": end,
            "alert_ids": sorted({r["source_locator"]["alert_id"] for r in related if "alert_id" in r["source_locator"]}),
            "event_ids": [r["event_id"] for r in related], "decision_counts": dict(Counter(r["type"] for r in related)),
            "event_weighted_counts_not_independent_samples": True,
            "market_observed": {s: context.features(panel, s) for s in ("SPY", "QQQ", "RSP", "IWM")},
            "participation_proxies": {s+"_vs_SPY_20": panel.relative(s, "SPY", end, 20) for s in ("RSP", "QQQ", "IWM")},
            "true_market_breadth": {"value": None, "status": "NOT_AVAILABLE_NO_ADDITIONAL_DATA"},
            "agent_descriptive_labels": {"SPY_negative_day": daily < 0 if daily is not None else None,
                "positive_day_negative_5d": daily > 0 and recent < 0 if daily is not None and recent is not None else None,
                "SPY_volatility20_ratio_previous": number(ratio), "SPY_volatility_expansion": ratio > 1 if ratio is not None else None}})
    return out


def relationship(name, hypothesis, rows, extract, predicate, *, limitation, additional_data):
    observed, missing = [], []
    for row in rows:
        value = extract(row)
        item = {"event_id": row["event_id"], "symbol": row["symbol"], "value": value}
        (missing if value is None else observed).append(item)
    support = [r for r in observed if predicate(r["value"])]
    counters = [r for r in observed if not predicate(r["value"]) ]
    return {"id": name, "hypothesis": hypothesis, "support": support, "counterexamples": counters, "unusable": missing,
        "support_rate": rate(len(support), len(observed), "Events with the specified feature available; unavailable events separately retained"),
        "total_events": len(rows), "interpretation": "DESCRIPTIVE_ASSOCIATION_NOT_CAUSAL_OR_VERIFIED_GRIMES_RULE",
        "confounders": limitation, "additional_validation_data": additional_data}


def derive(parent, inputs):
    validate_inventory(parent)
    context = Evidence(parent, inputs)
    rows = sorted([context.row(t, e) for t in context.trades for e in t["events"]], key=lambda r: r["source_order"])
    stops = [r for r in rows if r["type"] == "STOP_CHANGED"]
    history = {r["event_id"]: r for r in parent["source_stop_history.json"]}
    for r in stops:
        h = history[r["event_id"]]
        r.update(stop_change=h["change"], source_stop_change_percent=number(
            100*(Decimal(h["reported_stop"])-Decimal(h["previous_stop"]))/Decimal(h["previous_stop"])))
    transitions = [r for r in rows if r["type"] == "SETUP_CHANGED"]
    closures = []
    for row in (r for r in rows if r["type"] == "DROPPED"):
        trade = next(t for t in context.trades if t["trade_id"] == row["trade_id"])

        def exit_evidence(model):
            events = context.known_model_events(model, row["decision_bound"])
            return {"stop_touch": [e for e in events if e["type"] == "ASSUMED_STOP_TRIGGERED"],
                "hypothetical_target_touch": [e for e in events if e["type"] == "HYPOTHETICAL_TARGET_REACHED"],
                "definitive_actual_exit_reason": "EXIT_REASON_UNRESOLVED",
                "long_target_does_not_establish_full_closure": trade["direction"] == "LONG"}

        windows = [w for w in parent["exit_hypotheses.json"]["conditional_unverified_basis_scenario"]
            if w["trade_id"] == trade["trade_id"] and w["status"] == "AVAILABLE" and w["sessions"]
            and row["last_available_session"] and w["sessions"][-1] <= row["last_available_session"]]
        active_at_drop = row["conditional_path"]["current_progress"] is not None
        terminal_windows = [w for w in windows if w["sessions"][-1] == row["last_available_session"]]
        closures.append({**row, "source_closure": "SOURCE_REPORTED_DROPPED", "opening_event_id": trade["opening_event_id"],
            "closing_event_id": trade["closing_event_id"], "duration": duration(trade, context),
            "stop_revision_ids": [e["event_id"] for e in trade["events"] if e["type"] == "STOP_CHANGED"],
            "primary_exit_evidence": exit_evidence(context.primary[trade["trade_id"]]),
            "conditional_exit_evidence": exit_evidence(context.conditional[trade["trade_id"]]),
            "conditional_time_windows_known_before_drop": windows,
            "earlier_nonprogress_flags_exist": any(w["possible_time_stop"] is True for w in windows),
            "possible_time_stop": any(w["possible_time_stop"] is True for w in terminal_windows) if active_at_drop else None,
            "terminal_time_hypothesis_status": "EXPLORATORY_ONLY" if active_at_drop else "MODEL_CLOSED_OR_AMBIGUOUS_NO_TERMINAL_EXPOSURE",
            "actual_exit_reason": "EXIT_REASON_UNRESOLVED", "actual_realized_PnL": None})
    positions = []
    final = (timestamp(context.spec["analysis_cutoff"])+timedelta(microseconds=1)).isoformat()
    for trade in context.trades:
        event = trade["events"][-1] if trade["position_state"] == "CLOSED" else {
            **trade["events"][-1], "effective_at": final, "event_id": f"{trade['trade_id']}:right-censored-summary"}
        # Source closure summaries use the last instant before the DROP bound, not later bars.
        positions.append({"symbol": trade["symbol"], "trade_id": trade["trade_id"], "direction": trade["direction"],
            "source_position_state": trade["position_state"], "source_setup": trade["setup_availability"],
            "opening_event_id": trade["opening_event_id"], "closing_event_id": trade["closing_event_id"],
            "duration": duration(trade, context), "initial_stop": trade["initial_stop"], "latest_source_stop": trade["current_stop"],
            "stop_revisions": [r for r in stops if r["trade_id"] == trade["trade_id"]],
            "event_ids": [e["event_id"] for e in trade["events"]],
            "primary_path": context.path(trade, event["effective_at"], conditional=False),
            "conditional_path": context.path(trade, event["effective_at"], conditional=True),
            "actual_realized_PnL": None})
    comparisons = {}
    for direction in ("LONG", "SHORT"):
        group = [p for p in positions if p["direction"] == direction]
        revisions = [r for r in stops if r["direction"] == direction]
        counts = Counter(r["stop_change"] for r in revisions)
        paths = [p["conditional_path"]["pre_exit_or_active_path"] for p in group]
        comparisons[direction] = {"positions": len(group), "source_stop_revisions": len(revisions),
            "source_tightening_revision_rate": rate(counts["TIGHTENING"], len(revisions), "All source revisions for direction"),
            "source_widening_revision_rate": rate(counts["WIDENING"], len(revisions), "All source revisions for direction"),
            "positions_with_widening": rate(len({r["trade_id"] for r in revisions if r["stop_change"] == "WIDENING"}), len(group), "All source positions for direction"),
            "underway_rate": rate(sum(p["source_setup"] == "UNDERWAY" for p in group), len(group), "All source positions for direction"),
            "reported_closure_rate": rate(sum(p["source_position_state"] == "CLOSED" for p in group), len(group), "All source positions for direction, including right-censored opens"),
            "email_bound_scenario_duration_sessions": distribution([p["duration"]["email_bound_scenario_eligible_sessions"] for p in group], len(group)),
            "conditional_pre_exit_path_distributions": {k: distribution([v[k] if v else None for v in paths], len(group))
                for k in ("mfe_percent", "mae_percent", "progress_original_R")}}
    progress = lambda r: r["conditional_path"]["current_progress"]["progress_percent"] if r["conditional_path"]["current_progress"] else None
    stops_by_change = {kind: [r for r in stops if r["stop_change"] == kind] for kind in ("TIGHTENING", "WIDENING")}
    near = lambda r: r["conditional_stop_comparison"]["near_previous_stop_1ATR"] if r.get("conditional_stop_comparison") else None
    toward = lambda r: r["conditional_stop_comparison"]["moves_toward_preexisting_swing"] if r.get("conditional_stop_comparison") else None
    relationships = [
        relationship("tightening_after_favorable_progress", "Tightening revisions follow favorable current conditional price progress", stops_by_change["TIGHTENING"], progress, lambda v: v > 0,
            limitation="Hypothetical entry; post-exit observations excluded; direction/sector and co-published decisions confound association", additional_data="Independent alert sample with exact entries, publication and revision clocks and compatible units"),
        relationship("widening_after_favorable_progress", "Widening can also follow favorable progress, challenging a profit-tightening-only interpretation", stops_by_change["WIDENING"], progress, lambda v: v > 0,
            limitation="Conditional basis and model-survival censoring; source-open conflicts are retained but current progress unavailable", additional_data="Independent source/entry records including adverse and favorable examples"),
        relationship("widening_near_previous_stop", "Widening coincides with Close within one ATR of the previous stop", stops_by_change["WIDENING"], near, bool,
            limitation="Fixed descriptive one-ATR cut; stop/native units unverified except bounded EBAY; price proximity is not held-position progress or causation", additional_data="Compatible quotes and intraday revision/stop activation evidence on a separate sample"),
        relationship("revision_toward_preexisting_swing", "Revisions move toward the pre-existing direction-selected protective swing", stops, toward, bool,
            limitation="Confirmed pivots are agent-selected diagnostics, not expert levels; missing warmup; direction and widening/tightening confound association", additional_data="Independent dated annotations identifying levels actually used by the expert"),
        relationship("underway_after_favorable_progress", "Underway transitions follow favorable conditional price progress", transitions, progress, lambda v: v > 0,
            limitation="Seven transitions, four in one technology cluster; source/model conflict and hypothetical entries; matching does not identify causation", additional_data="Independent alerts with setup descriptions, exact entry/underway clocks, and unselected comparison opportunities")]
    markets = market_snapshots(context, rows)
    market_by_bound = {m["decision_bound"]: m for m in markets}
    clusters = {}
    for kind in ("OPEN_NEW_POSITION", "STOP_CHANGED", "SETUP_CHANGED", "DROPPED"):
        selected = [r for r in rows if r["type"] == kind]
        usable = [r for r in selected if r["decision_bound"] in market_by_bound]
        clusters[kind] = {"source_events": len(selected), "market_context_usable": len(usable),
            "distinct_alert_bounds": len({r["decision_bound"] for r in usable}),
            **{label: rate(sum(market_by_bound[r["decision_bound"]]["agent_descriptive_labels"][label] is True for r in usable),
                sum(market_by_bound[r["decision_bound"]]["agent_descriptive_labels"][label] is not None for r in usable),
                "Events with market label available; repeated alert snapshots are dependent")
                for label in ("SPY_negative_day", "positive_day_negative_5d", "SPY_volatility_expansion")}}
    stop_comparison = {kind: {"events": len(group), "current_progress_percent": distribution([progress(r) for r in group], len(group)),
        "clearance_ATR": distribution([r["conditional_stop_comparison"]["stop_clearance_ATR"] if r.get("conditional_stop_comparison") else None for r in group], len(group)),
        "SPY_volatility20": distribution([market_by_bound[r["decision_bound"]]["market_observed"]["SPY"]["realized_volatility20"]["value"]
            if r["decision_bound"] in market_by_bound else None for r in group], len(group)),
        "unique_publication_bounds": len({r["decision_bound"] for r in group}),
        "setup_counts": dict(Counter(r["source_setup_before"] for r in group))} for kind, group in stops_by_change.items()}
    quartet = [r for r in transitions if r["symbol"] in {"AAOI", "AMD", "ANET", "SNDK"}]
    grouped = {"symbols": [r["symbol"] for r in quartet], "event_ids": [r["event_id"] for r in quartet],
        "decision_bounds": sorted({r["decision_bound"] for r in quartet if r["decision_bound"]}),
        "elapsed_sessions": [r["conditional_path"]["elapsed_eligible_sessions"] for r in quartet],
        "current_progress": {k: distribution([r["conditional_path"]["current_progress"][k]
            if r["conditional_path"]["current_progress"] else None for r in quartet], len(quartet))
            for k in ("progress_percent", "progress_ATR", "progress_original_R", "mfe_percent", "mae_percent")},
        "native_geometry": [{"symbol": r["symbol"], **{k: r["native_features"][k]["value"] if r["native_features"] else None
            for k in ("breakdown20", "close_sma20", "close_sma50", "range_contraction10_previous20")},
            "relative_20": {p: r.get("relative_strength", {}).get(p, {}).get("20", {}).get("value")
                for p in ("SPY", "QQQ", "RSP", "IWM")}} for r in quartet],
        "common_context_is_not_independent_evidence": True}
    return {"decision_features.json": rows, "stop_revisions.json": stops, "stop_comparison.json": stop_comparison,
        "grouped_oct22_transitions.json": grouped,
        "underway_transitions.json": transitions, "matched_enterable_controls.json": matched_controls(context, transitions, rows),
        "closure_hypotheses.json": closures, "positions.json": positions, "long_short.json": comparisons,
        "market_context.json": markets, "market_decision_clusters.json": clusters,
        "relationships.json": relationships, "methodology.json": DEFINITIONS,
        "expert_commentary.json": parent["expert_market_commentary.json"],
        "manifest.json": {"schema_version": "grimes_management_study_v1", "source_event_counts": dict(Counter(r["type"] for r in rows)),
            "stocks": list(UNIVERSE), "stock_count": 26, "alert_count": 7,
            "source_final_states": dict(Counter(p["source_position_state"] for p in positions)),
            "all_source_exit_reasons_unresolved": True, "actual_execution_accounting": False,
            "prior_frozen_source_records_reinterpreted": False, "new_market_data_acquired": False,
            "strict_pre_decision_price_availability": True, "weekly_publication_timestamp": None,
            "scope": "Discovery sample; 72 dependent source actions, not72 independent trades or independent decisions"}}
