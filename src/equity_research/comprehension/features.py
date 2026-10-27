"""Causal daily diagnostics and explicit heuristic taxonomy, never trade signals."""

from decimal import Decimal
from statistics import mean

from ..events.model import timestamp
from ..market_context.model import _measure
from .inputs import PRICE_BASIS, VOLUME_BASIS

VERSION = "expert_daily_features_v1"


def metric(value=None, reason=None, sessions=()):
    return {"value": round(value, 12) if isinstance(value, float) else value,
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
        for n in (5, 20, 60):
            operation(f"return{n}", n+1, "return", [n])
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
        return out


def setup(features):
    v = {k: m["value"] for k, m in features.items()}
    required = ("breakout20", "breakdown20", "failed_breakout20", "close_sma50", "close_sma200", "sma50_sma200", "atr14", "close", "sma20", "sma50")
    if any(v.get(k) is None for k in required):
        return {"classification": "OTHER_OR_UNCERTAIN", "candidates": [], "reason": "MISSING_REQUIRED_FEATURES"}
    candidates = []
    if v["breakout20"] and v["close_sma50"] > 0:
        candidates.append("BULLISH_CONTINUATION_OR_BREAKOUT")
    if v["close_sma200"] > 0 and v["sma50_sma200"] > 0 and min(abs(v["close"]-v["sma20"]), abs(v["close"]-v["sma50"])) <= v["atr14"]:
        candidates.append("BULLISH_PULLBACK")
    if v["breakdown20"] and v["close_sma50"] < 0:
        candidates.append("BEARISH_CONTINUATION_OR_BREAKDOWN")
    if v["failed_breakout20"]:
        candidates.append("FAILED_BREAKOUT_OR_BEARISH_REVERSAL")
    return {"classification": candidates[0] if len(candidates) == 1 else "OTHER_OR_UNCERTAIN",
            "candidates": candidates, "reason": "EXPLICIT_HEURISTIC_HYPOTHESIS" if len(candidates) == 1 else "NO_UNIQUE_TAXONOMY_MATCH"}


def alignment(features, direction):
    sign = 1 if direction == "LONG" else -1
    values = {k: features[k]["value"] for k in ("close_sma50", "return20", "sma50_slope20")}
    if any(v is None for v in values.values()):
        return {"status": "UNAVAILABLE", "direction": direction, "support_count": None}
    support = sum(sign*v > 0 for v in values.values())
    return {"status": "ALIGNED" if support == 3 else "COUNTERTREND" if support == 0 else "MIXED",
            "direction": direction, "support_count": support, "dimensions": values}


def stop_analysis(observation, features):
    close = features["close"]["value"]
    result = {"reported_stop": observation["reported_stop"], "direction": observation["direction"],
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
            "absolute_atr_distance": str(abs(stop-Decimal(str(level)))/Decimal(str(atr))) if level is not None and atr else None}
    return result
