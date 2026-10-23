"""Versioned descriptive price paths; no entries, orders, fills or realized R."""

from dataclasses import dataclass
from decimal import Context, Decimal, localcontext

from ..models import number, timestamp
from ..events.diagnostics import _corporate_action_window, _effective_date_bounds
from ..ingestion.storage import digest, encode

CLOSE, OPEN = "SIGNAL_CLOSE", "NEXT_ELIGIBLE_OPEN"
VERSION = "signal_outcome_v1"


@dataclass(frozen=True)
class Configuration:
    close_horizons: tuple = (1, 5, 10, 20)
    open_horizons: tuple = (0, 1, 5, 10, 20)
    minimum_clusters: int = 10

    def __post_init__(self):
        for key, lower in (("close_horizons", 1), ("open_horizons", 0)):
            values = tuple(getattr(self, key))
            if any(type(x) is not int or not lower <= x <= 252 for x in values) or len(set(values)) != len(values):
                raise ValueError("unique integer horizons required (Close 1..252, Open 0..252)")
            object.__setattr__(self, key, tuple(sorted(values)))
        if not self.close_horizons and not self.open_horizons:
            raise ValueError("at least one reference/horizon required")
        if type(self.minimum_clusters) is not int or self.minimum_clusters < 1:
            raise ValueError("minimum_clusters must be positive")

    def record(self):
        return {"schema_version": "outcome_definitions_v1", "outcome_schema": VERSION,
                "close_horizons": list(self.close_horizons), "open_horizons": list(self.open_horizons),
                "minimum_clusters": self.minimum_clusters,
                "reference_close": "signal Close; endpoint t+h; excursions t+1 through t+h",
                "reference_open": "first expected RTH Open strictly after signal availability; endpoint reference+h; excursions reference through endpoint",
                "returns": "100*(endpoint Close/reference-1); SHORT normalized by sign inversion, not short-sale return",
                "excursions": "nonnegative favorable/adverse price magnitudes divided by reference for percent; by original signal ATR14 for ATR units",
                "atr": "original signal features.atr14 only; missing/nonpositive gives PARTIAL with raw path retained",
                "gap": "100*(eligible Open/signal Close-1), not slippage",
                "path": "all expected reference-through-end sessions required; no compression or forward fill",
                "corporate_actions": "retrospective PR6 annotations; known effects and sourced bounds separate from global unknown ex-dates; sensitivity excludes known/bounded overlaps",
                "clusters": "per-security connected components of closed signal-to-longest-requested-endpoint intervals, including unavailable paths; cross-strategy bridges retained",
                "dispersion": "population standard deviation of available observations; descriptive, no independent-sample inference",
                "execution": "NONE; no costs, borrow, stop sequence, PnL or realized R"}

    @classmethod
    def from_record(cls, raw):
        result = cls(tuple(raw["close_horizons"]), tuple(raw["open_horizons"]), raw["minimum_clusters"])
        if result.record() != raw: raise ValueError("unsupported outcome definition")
        return result

    @property
    def sha256(self): return digest(encode(self.record()))


def valid_bar(row):
    if row is None: return False
    try:
        v = {k: number(row[k]) for k in ("open", "high", "low", "close", "volume")}
        return (min(v[k] for k in ("open", "high", "low", "close")) > 0 and v["volume"] >= 0
                and v["volume"] == v["volume"].to_integral_value()
                and v["high"] >= max(v["open"], v["low"], v["close"])
                and v["low"] <= min(v["open"], v["high"], v["close"]))
    except (KeyError, ValueError, TypeError):
        return False


def index_prices(rows, calendar, symbol, security_id):
    sessions = calendar["sessions"]
    days = [r["session_date"] for r in sessions]
    if not days or days != sorted(set(days)):
        raise ValueError("unique ascending expected calendar required")
    for i, s in enumerate(sessions):
        if timestamp(s["opens_at"]) >= timestamp(s["closes_at"]): raise ValueError("invalid session times")
        if i and timestamp(s["opens_at"]) <= timestamp(sessions[i-1]["closes_at"]): raise ValueError("overlapping calendar sessions")
    by_day = {}
    for row in rows:
        day = row["session_date"]
        if day not in days or day in by_day: raise ValueError("duplicate/off-calendar prices")
        if row["symbol"] != symbol or row["security_id"] != security_id:
            raise ValueError("SIGNAL_SECURITY_IDENTITY_MISMATCH")
        by_day[day] = row
    if [r["session_date"] for r in rows] != sorted(by_day): raise ValueError("price rows must be ascending")
    return days, by_day


def measure(signal, rows, calendar, *, price_sha, strategy_sha, basis, configuration=None,
            actions=(), alignments=(), conflicting_events=()):
    """Measure original signal records without detection, context lookup or ATR recomputation."""
    config = configuration or Configuration()
    with localcontext(Context(prec=28)):
        days, prices = index_prices(rows, calendar, signal["symbol"], signal["security_id"])
        if signal["price_dataset_sha256"] != price_sha: raise ValueError("PRICE_DATASET_MISMATCH")
        day = signal["trigger"]["session_date"]
        if day not in days: raise ValueError("signal session absent from expected calendar")
        index = days.index(day)
        available = timestamp(signal["trigger"]["available_at"])
        if available < timestamp(calendar["sessions"][index]["closes_at"]):
            raise ValueError("signal available before completed session")
        if signal["trigger"]["direction"] not in {"LONG", "SHORT"}: raise ValueError("unsupported direction")
        cutoff = signal.get('feature_observation_cutoffs', {}).get('atr14')
        if cutoff is not None and cutoff > day:
            raise ValueError('signal ATR observation follows signal session')
        first = next((i for i in range(index+1, len(days)) if timestamp(calendar["sessions"][i]["opens_at"]) > available), None)
        aligned = {a["revision_key"]: a for a in alignments}
        args = (signal, days, prices, index, first, price_sha, strategy_sha, basis, actions, aligned, set(conflicting_events))
        outcomes = [_outcome(*args, reference=reference, horizon=h, definitions_sha=config.sha256)
                    for reference, horizons in ((CLOSE, config.close_horizons), (OPEN, config.open_horizons)) for h in horizons]
        comparisons = []
        if config.close_horizons and config.open_horizons:
            for h in config.close_horizons:
                a = next(r for r in outcomes if r["reference_type"] == CLOSE and r["horizon"] == h)
                offset = index+h-first if first is not None else None
                b = _outcome(*args, reference=OPEN, horizon=offset, definitions_sha=config.sha256) if offset is not None and offset >= 0 else None
                ok = b is not None and a["forward_return_pct"] is not None and b["forward_return_pct"] is not None
                comparisons.append({"signal_id": signal["signal_id"], "symbol": signal["symbol"], "security_id": signal["security_id"],
                    "strategy_id": signal["strategy_id"], "direction": signal["trigger"]["direction"],
                    "signal_close_horizon": h, "next_open_horizon": offset, "horizon_end_session": a["horizon_end_session"],
                    "status": "AVAILABLE" if ok else "UNAVAILABLE",
                    "unavailable_reasons": sorted(set(a["unavailable_reasons"] + (b["unavailable_reasons"] if b else ["ENDPOINT_BEFORE_OPEN_REFERENCE"]))),
                    "entry_gap_pct": a["entry_gap_pct"], "close_reference_return_pct": a["forward_return_pct"] if ok else None,
                    "open_reference_return_pct": b["forward_return_pct"] if ok else None,
                    "direction_normalized_difference_pct": str(number(a["direction_normalized_return_pct"])-number(b["direction_normalized_return_pct"])) if ok else None})
        return outcomes, comparisons


def _outcome(signal, days, prices, index, first, price_sha, strategy_sha, basis, actions, aligned, conflicts, *, reference, horizon, definitions_sha):
    refindex = index if reference == CLOSE else first
    endindex = refindex+horizon if refindex is not None else None
    endday = days[endindex] if endindex is not None and endindex < len(days) else None
    refday = days[refindex] if refindex is not None else None
    signalbar = prices.get(days[index]); refbar = prices.get(refday)
    signalclose = number(signalbar["close"]) if valid_bar(signalbar) else None
    refprice = number(refbar["close" if reference == CLOSE else "open"]) if valid_bar(refbar) else None
    nextbar = prices.get(days[first]) if first is not None else None
    gap = (number(nextbar["open"])/signalclose-1)*100 if valid_bar(nextbar) and signalclose else None
    base = {"schema_version": VERSION, "outcome_definitions_sha256": definitions_sha,
        **{k: signal[k] for k in ("signal_id", "strategy_id", "strategy_version", "security_id", "symbol")},
        "setup_id": signal["setup"]["setup_id"], "setup_type": signal["setup"]["setup_type"],
        "direction": signal["trigger"]["direction"], "signal_session": days[index],
        "signal_available_at": signal["trigger"]["available_at"], "price_dataset_sha256": price_sha,
        "strategy_bundle_sha256": strategy_sha, "market_context_link_sha256": signal["market_context_reference"],
        "reference_type": reference, "reference_session": refday, "reference_price": str(refprice) if refprice else None,
        "first_eligible_session": days[first] if first is not None else None, "horizon": horizon,
        "horizon_end_session": endday, "entry_gap_pct": str(gap) if gap is not None else None,
        "measurement_first_session": days[index+1] if reference == CLOSE and index+1 < len(days) else refday if reference == OPEN else None,
        "forward_return_pct": None, "direction_normalized_return_pct": None, "mfe_pct": None, "mae_pct": None,
        "mfe_atr": None, "mae_atr": None, "max_high": None, "min_low": None,
        "atr14_at_signal": signal["features"].get("atr14"), "outcome_status": "UNAVAILABLE", "unavailable_reasons": [],
        "price_basis": basis, "daily_high_low_order": "UNKNOWN",
        "corporate_action_uncertainty": {"evidence_view": "RETROSPECTIVE_OUTCOME_ANNOTATION_ONLY",
            "inventory_completeness": "UNKNOWN", "known_effective_actions": [], "bounded_overlap_uncertainty": [],
            "global_unknown_effective_dates": [{"event_id": a["event_id"], "source_ids": a["source_ids"],
                "unresolved_fields": a["unresolved_fields"], "effective_date_bounds": _effective_date_bounds(a)} for a in actions if a["effective_date"] is None],
            "comparability_review_required": False}}
    reasons = base["unavailable_reasons"]
    if signalclose is None:
        reasons.extend(["INVALID_REFERENCE", "MISSING_EXPECTED_SESSION" if signalbar is None else "INVALID_PRICE"])
    if reference == OPEN and (refindex is None or refbar is None): reasons.append("NO_ELIGIBLE_REFERENCE_SESSION")
    if refprice is None: reasons.append("INVALID_REFERENCE")
    if endday is None or not prices or endday > max(prices): reasons.append("INSUFFICIENT_FUTURE_COVERAGE")
    through = min(endindex+1, len(days)) if endindex is not None else len(days)
    window = days[refindex:through] if refindex is not None else []
    if any(d not in prices and prices and d <= max(prices) for d in window): reasons.append("MISSING_EXPECTED_SESSION")
    if any(d in prices and not valid_bar(prices[d]) for d in window): reasons.append("INVALID_PRICE")
    # Conservative annotations use the excursion window, including an Open
    # reference's session; they do not assert a mechanical adjustment effect.
    action_days = days[index+1:through] if reference == CLOSE else window
    effects, uncertain = _corporate_action_window(actions, aligned, conflicts, action_days) if action_days else ([], [])
    ca = base["corporate_action_uncertainty"]
    ca.update(known_effective_actions=effects, bounded_overlap_uncertainty=uncertain,
              comparability_review_required=bool(effects or uncertain), expected_effective_date_sessions=action_days)
    if reasons:
        base["unavailable_reasons"] = sorted(set(reasons))
        return base
    excursion_days = days[index+1:endindex+1] if reference == CLOSE else window
    high = max(number(prices[d]["high"]) for d in excursion_days)
    low = min(number(prices[d]["low"]) for d in excursion_days)
    raw = (number(prices[endday]["close"])/refprice-1)*100
    up, down = max(Decimal(0), high-refprice), max(Decimal(0), refprice-low)
    favorable, adverse = (up, down) if base["direction"] == "LONG" else (down, up)
    base.update(forward_return_pct=str(raw), direction_normalized_return_pct=str(raw if base["direction"] == "LONG" else -raw),
                mfe_pct=str(favorable/refprice*100), mae_pct=str(adverse/refprice*100), max_high=str(high), min_low=str(low), outcome_status="AVAILABLE")
    try:
        atr = number(base["atr14_at_signal"])
        if atr <= 0 or signal.get('feature_observation_cutoffs', {}).get('atr14') is None:
            raise ValueError("nonpositive or unbound ATR")
    except (ValueError, TypeError):
        base.update(outcome_status="PARTIAL", unavailable_reasons=["MISSING_SIGNAL_ATR"])
    else:
        base.update(mfe_atr=str(favorable/atr), mae_atr=str(adverse/atr))
    return base
