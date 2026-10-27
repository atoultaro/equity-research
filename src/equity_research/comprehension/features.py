"""Causal daily diagnostics and explicit heuristic taxonomy, never trade signals."""

from decimal import Decimal
from statistics import mean

from ..events.model import timestamp
from ..market_context.model import _measure
from .inputs import PRICE_BASIS, VOLUME_BASIS

VERSION = "expert_daily_features_v2"
DIAGNOSTIC_DEFINITIONS = {
    "breakout20": "Current Close > maximum High of previous 20 completed sessions (21 observations including current)",
    "breakdown20": "Current Close < minimum Low of previous 20 completed sessions (21 observations including current)",
    "failed_breakout20": "Current High > maximum previous 20 Highs > current Close; a single-bar rejection diagnostic",
    "support_rejection": "Current Low <= pre-existing confirmed 3-bar swing Low < current Close; pivot confirmation strictly before current session",
    "resistance_rejection": "Current High >= pre-existing confirmed 3-bar swing High > current Close; pivot confirmation strictly before current session",
}


def metric(value=None, reason=None, sessions=()):
    return {"value": round(value, 12) if isinstance(value, float) else value,
            "attribution": "MARKET_OBSERVED",
            "status": "UNAVAILABLE" if value is None else "AVAILABLE", "reason": reason,
            "first_session": sessions[0] if sessions else None, "last_session": sessions[-1] if sessions else None}


class Panel:
    def __init__(self, prices, coverage, calendar, cutoff):
        from datetime import timedelta
        self.coverage, self.prices = coverage, {}
        # The only assumed historical availability: US cash close + 60 minutes.
        # Capture timestamps are retained separately and never become publication clocks.
        self.days = [r["session_date"] for r in calendar["sessions"]
                     if timestamp(r["closes_at"]) + timedelta(minutes=60) <= timestamp(cutoff)]
        for symbol, rows in prices.items():
            if coverage[symbol]["price_basis"] != PRICE_BASIS or coverage[symbol]["volume_basis"] != VOLUME_BASIS:
                raise ValueError("panel data-basis incompatibility")
            by_day = {}
            for r in rows:
                d = r["session_date"]
                if d not in self.days:
                    continue  # Future data cannot affect either validation or features.
                if d in by_day:
                    raise ValueError("duplicate panel session")
                if (r["price_basis"] != PRICE_BASIS or r["volume_basis"] != VOLUME_BASIS
                        or r["provider"] != "ibkr" or r["symbol"] != symbol
                        or r["security_id"] != coverage[symbol]["security"]["security_id"]):
                    raise ValueError("panel identity or data-basis incompatibility")
                v = {k: Decimal(r[k]) for k in ("open", "high", "low", "close", "volume")}
                if (any(not n.is_finite() for n in v.values()) or any(v[k] <= 0 for k in ("open", "high", "low", "close"))
                        or v["volume"] < 0 or v["high"] < max(v["open"], v["close"], v["low"])
                        or v["low"] > min(v["open"], v["close"], v["high"])):
                    raise ValueError("invalid panel OHLCV")
                by_day[d] = {k: float(n) for k, n in v.items()}
            self.prices[symbol] = by_day

    def window(self, symbol, end, n):
        if end not in self.days:
            return None, [], "SESSION_NOT_YET_AVAILABLE"
        i = self.days.index(end)
        days = self.days[max(0, i-n+1):i+1]
        if symbol not in self.prices:
            return None, days, "PROXY_OR_SECURITY_NOT_AVAILABLE"
        missing = [d for d in days if d not in self.prices[symbol]]
        if len(days) != n or missing:
            return None, days, "MISSING_EXPECTED_SESSIONS_OR_WARMUP"
        return [self.prices[symbol][d] for d in days], days, None

    def relative(self, symbol, proxy, end, n):
        a, days, reason = self.window(symbol, end, n+1)
        b, _, other = self.window(proxy, end, n+1)
        if a is None or b is None:
            return metric(reason=reason or other, sessions=days)
        # Same ordered XNYS dates, same native provider price basis. Price return,
        # not total return; differing dividend yields remain a limitation.
        return metric(_measure({"operation": "ratio_change", "parameters": [n]}, [a, b]), sessions=days)

    def features(self, symbol, end):
        out = {}

        def calc(name, n, function):
            rows, days, reason = self.window(symbol, end, n)
            value = function(rows) if rows is not None else None
            out[name] = metric(value, reason or ("ZERO_DENOMINATOR" if value is None else None), days)

        def operation(name, n, op, parameters):
            calc(name, n, lambda rows: _measure({"operation": op, "parameters": parameters}, [rows]))

        calc("close", 1, lambda r: r[-1]["close"])
        calc("volume_native", 1, lambda r: r[-1]["volume"])
        for n in (20, 50, 150, 200):
            calc(f"sma{n}", n, lambda r: mean(x["close"] for x in r))
            operation(f"close_sma{n}", n, "close_sma", [n])
            for lag in (5, 20):
                operation(f"sma{n}_slope{lag}", n+lag, "slope", [n, lag])
        for fast, slow in ((20, 50), (50, 150), (150, 200), (50, 200)):
            operation(f"sma{fast}_sma{slow}", slow, "sma_ratio", [fast, slow])
        for n in (1, 5, 20, 60):
            operation(f"return{n}", n+1, "return", [n])
            name = "daily_return" if n == 1 else f"return_{n}d"
            out[name] = {**out[f"return{n}"], "horizon_sessions": n, "required_observations": n+1,
                "unit": "fraction", "definition": "Close(t)/Close(t-n completed trading sessions)-1"}
        operation("realized_volatility20", 21, "volatility", [20])
        operation("atr14_fraction", 15, "atr", [14])
        # Reuse pinned shared ATR through MarketContext's measure, in price units.
        calc("atr14", 15, lambda r: _measure({"operation": "atr", "parameters": [14]}, [r])*r[-1]["close"])
        for n in (20, 60, 252):
            calc(f"high{n}", n, lambda r: max(x["high"] for x in r))
            calc(f"low{n}", n, lambda r: min(x["low"] for x in r))
            calc(f"drawdown_high{n}", n, lambda r: r[-1]["close"]/max(x["high"] for x in r)-1)
            calc(f"distance_low{n}", n, lambda r: r[-1]["close"]/min(x["low"] for x in r)-1)
            operation(f"range{n}_fraction", n, "range", [n])
        calc("prior20_high", 21, lambda r: max(x["high"] for x in r[:-1]))
        calc("prior20_low", 21, lambda r: min(x["low"] for x in r[:-1]))
        calc("breakout20", 21, lambda r: r[-1]["close"] > max(x["high"] for x in r[:-1]))
        calc("breakdown20", 21, lambda r: r[-1]["close"] < min(x["low"] for x in r[:-1]))
        calc("failed_breakout20", 21, lambda r: r[-1]["high"] > max(x["high"] for x in r[:-1]) > r[-1]["close"])
        calc("volume_vs_prior20", 21, lambda r: r[-1]["volume"]/mean(x["volume"] for x in r[:-1])
             if any(x["volume"] for x in r[:-1]) else None)
        calc("mean_dollar_volume20_native", 20, lambda r: mean(x["close"]*x["volume"] for x in r))
        calc("range_contraction20_60", 60, lambda r: (max(x["high"] for x in r[-20:])-min(x["low"] for x in r[-20:])) /
             (max(x["high"] for x in r)-min(x["low"] for x in r)) if max(x["high"] for x in r) > min(x["low"] for x in r) else None)
        calc("range_contraction10_previous20", 30, lambda r: (max(x["high"] for x in r[-10:])-min(x["low"] for x in r[-10:])) /
             (max(x["high"] for x in r[:-10])-min(x["low"] for x in r[:-10])) if max(x["high"] for x in r[:-10]) > min(x["low"] for x in r[:-10]) else None)
        rows, days, reason = self.window(symbol, end, 60)
        for kind, field in (("high", "high"), ("low", "low")):
            pivots = []
            if rows is not None:
                # Three bars on either side; the latest candidate is confirmed
                # only after three completed sessions, all <= this snapshot.
                for i in range(3, len(rows)-3):
                    neighbors = rows[i-3:i]+rows[i+1:i+4]
                    if all(rows[i][field] > x[field] if kind == "high" else rows[i][field] < x[field] for x in neighbors):
                        pivots.append({"session_date": days[i], "confirmed_session": days[i+3], "price": rows[i][field]})
            out[f"confirmed_swing_{kind}"] = metric(pivots[-1] if pivots else None, reason or "NO_STRICT_3_BAR_PIVOT" if not pivots else None, days)
        current, days, missing = self.window(symbol, end, 1)
        for name, kind, field in (("support_rejection", "low", "low"), ("resistance_rejection", "high", "high")):
            pivot = out[f"confirmed_swing_{kind}"]["value"]
            if current is None or pivot is None or pivot["confirmed_session"] >= end:
                out[name] = metric(reason=missing or "NO_PREEXISTING_CONFIRMED_PIVOT", sessions=days)
            else:
                level, bar = pivot["price"], current[0]
                flag = bar[field] <= level < bar["close"] if kind == "low" else bar[field] >= level > bar["close"]
                out[name] = metric(flag, sessions=days)
                out[name]["level_evidence"] = pivot
        for name, definition in DIAGNOSTIC_DEFINITIONS.items():
            out[name].update(definition=definition, definition_provenance="RESEARCHER_DEFINED_DIAGNOSTIC_V2_NOT_A_GRIMES_RULE")
        return out


def setup(features):
    """Competing hypotheses; never assign the expert's intended setup."""
    v = {k: m["value"] for k, m in features.items()}

    def check(names, predicate):
        return None if any(v.get(k) is None for k in names) else bool(predicate())

    diagnostics = {
        "legacy_bullish_breakout": check(("breakout20", "close_sma50"), lambda: v["breakout20"] and v["close_sma50"] > 0),
        "legacy_pullback_proximity": check(("close_sma200", "sma50_sma200", "close", "sma20", "sma50", "atr14"),
            lambda: v["close_sma200"] > 0 and v["sma50_sma200"] > 0 and min(abs(v["close"]-v["sma20"]), abs(v["close"]-v["sma50"])) <= v["atr14"]),
        "legacy_bearish_breakdown": check(("breakdown20", "close_sma50"), lambda: v["breakdown20"] and v["close_sma50"] < 0),
        "bullish_trend": check(("close_sma50", "sma50_slope20", "return20"), lambda: all(v[k] > 0 for k in ("close_sma50", "sma50_slope20", "return20"))),
        "bearish_trend": check(("close_sma50", "sma50_slope20", "return20"), lambda: all(v[k] < 0 for k in ("close_sma50", "sma50_slope20", "return20"))),
        **{k: v.get(k) for k in ("failed_breakout20", "support_rejection", "resistance_rejection")}}
    hypotheses = []
    for name, keys, limitation in (
        ("TREND_CONTINUATION", ("bullish_trend", "bearish_trend"), "Trend alignment does not require a fresh 20-session closing breakout or breakdown"),
        ("PULLBACK_WITHIN_TREND_OR_RECOVERY", ("legacy_pullback_proximity",), "MA proximity in an upward trend is compatible with a pullback/recovery; it does not prove the preceding price path"),
        ("FAILED_RALLY_OR_FAILED_BREAKOUT", ("failed_breakout20", "resistance_rejection"), "A rejection can coexist with a larger upward trend; failed rally requires more than two down moves"),
        ("SUPPORT_OR_RESISTANCE_REJECTION", ("support_rejection", "resistance_rejection"), "Uses only confirmed, pre-existing pivots; measured levels need not be levels the expert used"),
        ("POTENTIAL_SECOND_LEG_AFTER_IMPULSE", (), "Unresolved: no validated ordered impulse/pullback/renewal diagnostic is implemented; two declines alone are insufficient"),
        ("OTHER_OR_UNCERTAIN", (), "Unobserved discretionary context and other explanations remain possible")):
        evidence = [k for k in keys if diagnostics[k] is True]
        hypotheses.append({"interpretation": name, "attribution": "RESEARCH_HYPOTHESIS",
            "status": "CONSISTENT_WITH_DIAGNOSTIC" if evidence else "UNRESOLVED", "supporting_diagnostics": evidence,
            "limitation": limitation})
    return {"attribution": "RESEARCH_HYPOTHESIS", "intended_expert_setup": None,
        "resolution": "UNRESOLVED_EXPERT_INTENT", "hypotheses": hypotheses,
        "researcher_diagnostics": diagnostics, "definition_provenance": "RESEARCHER_DEFINED_V2_NOT_DOCUMENTED_GRIMES_REQUIREMENTS",
        "diagnostic_definitions": {**DIAGNOSTIC_DEFINITIONS,
            "legacy_bullish_breakout": "breakout20 and Close > SMA50",
            "legacy_bearish_breakdown": "breakdown20 and Close < SMA50; NOT a documented Grimes requirement",
            "legacy_pullback_proximity": "Close > SMA200, SMA50 > SMA200, min(abs(Close-SMA20), abs(Close-SMA50)) <= ATR14",
            "bullish_trend": "Close/SMA50-1, SMA50 slope20 and return_20d all strictly positive",
            "bearish_trend": "Close/SMA50-1, SMA50 slope20 and return_20d all strictly negative"}}


def alignment(features, direction):
    sign = 1 if direction == "LONG" else -1
    values = {k: features[k]["value"] for k in ("close_sma50", "return20", "sma50_slope20")}
    if any(v is None for v in values.values()):
        return {"status": "UNAVAILABLE", "direction": direction, "support_count": None, "attribution": "RESEARCH_HYPOTHESIS"}
    support = sum(sign*v > 0 for v in values.values())
    return {"status": "ALIGNED" if support == 3 else "COUNTERTREND" if support == 0 else "MIXED",
            "attribution": "RESEARCH_HYPOTHESIS",
            "direction": direction, "support_count": support, "dimensions": values}


def stop_analysis(observation, features):
    close = features["close"]["value"]
    result = {"reported_stop": observation["reported_stop"], "direction": observation["direction"],
        "reported_stop_attribution": "EXPERT_REPORTED", "measurements_attribution": "MARKET_OBSERVED",
        "reference_close": close, "reference_is_actual_entry": False,
        "actual_entry": None, "actual_initial_risk": None, "quantity": None, "profit_targets": None}
    if close is None:
        return {**result, "status": "UNAVAILABLE", "reason": "REFERENCE_SESSION_MISSING"}
    c, stop = Decimal(str(close)), Decimal(observation["reported_stop"])
    signed = c-stop if observation["direction"] == "LONG" else stop-c
    absolute = abs(c-stop)
    atr = features["atr14"]["value"]
    result.update(status="AVAILABLE", signed_protective_distance=str(signed), absolute_distance=str(absolute),
        fraction_of_reference_close=str(absolute/c),
        atr_normalized_distance=str(absolute/Decimal(str(atr))) if atr else None,
        side_assessment="CONVENTIONAL_SIDE_OF_REFERENCE" if signed > 0 else "UNEXPECTED_SIDE_OF_REFERENCE_INVESTIGATE",
        warning="Actual entry unknown; native split-adjusted close is not a verified contemporaneous execution price. Reported-stop basis unverified.",
        technical_level_distances={})
    for name in ("prior20_high", "prior20_low", "sma20", "sma50", "sma200", "confirmed_swing_high", "confirmed_swing_low"):
        level = features[name]["value"]
        if isinstance(level, dict):
            level = level["price"]
        result["technical_level_distances"][name] = {"level": level,
            "stop_minus_level": str(stop-Decimal(str(level))) if level is not None else None,
            "absolute_price_distance": str(abs(stop-Decimal(str(level)))) if level is not None else None,
            "absolute_atr_distance": str(abs(stop-Decimal(str(level)))/Decimal(str(atr))) if level is not None and atr else None}
    levels = [(name, item) for name, item in result["technical_level_distances"].items() if item["level"] is not None]
    nearest = min(levels, key=lambda pair: (Decimal(pair[1]["absolute_price_distance"]), pair[0])) if levels else None
    result["nearest_numerical_technical_level"] = {"name": nearest[0], **nearest[1]} if nearest else None
    result["directional_invalidation_candidates"] = []
    direction = observation["direction"]
    for name, item in levels:
        level = Decimal(str(item["level"]))
        if direction == "LONG":
            relevant = name in {"prior20_low", "confirmed_swing_low", "sma20", "sma50", "sma200"} and level < c
            protective = stop < level
        else:
            relevant = name in {"prior20_high", "confirmed_swing_high", "sma20", "sma50", "sma200"} and level > c
            protective = stop > level
        if relevant:
            result["directional_invalidation_candidates"].append({"name": name, **item, "attribution": "RESEARCH_HYPOTHESIS",
                "candidate_role": "SUPPORT" if direction == "LONG" else "RESISTANCE",
                "stop_on_expected_protective_side": protective,
                "expected_stop_side": "STRICTLY_BELOW_LEVEL" if direction == "LONG" else "STRICTLY_ABOVE_LEVEL"})
    result["level_interpretation"] = "Candidate support/resistance proxies selected by direction and side of reference Close; proximity alone does not establish trade invalidation or expert rationale"
    return result
