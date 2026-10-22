"""Versioned daily measurements under an explicit reconstructed availability model."""

from collections import Counter
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from math import isfinite
from statistics import mean, pstdev

SCHEMA = "market_context_v1"
DEFINITION_VERSION = "market_features_v1"
ROLES = ("SPY", "QQQ", "RSP")
GROUPS = ("trend_features", "volatility_features", "participation_proxies",
          "breadth_features", "leadership_features")


def timestamp(value):
    result = datetime.fromisoformat(value) if isinstance(value, str) else value
    if not isinstance(result, datetime) or result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("an offset-aware timestamp is required")
    return result.astimezone(UTC)


@dataclass(frozen=True)
class Configuration:
    availability: str = "RECONSTRUCTED_CLOSE_PLUS_DELAY"
    delay_minutes: int = 60
    describe_state: bool = True

    def __post_init__(self):
        if self.availability not in {"RECONSTRUCTED_CLOSE_PLUS_DELAY", "UNKNOWN"}:
            raise ValueError("verified historical dissemination is not supported")
        if type(self.delay_minutes) is not int or not 1 <= self.delay_minutes <= 1440:
            raise ValueError("availability delay must be 1..1440 minutes")
        if type(self.describe_state) is not bool:
            raise ValueError("describe_state must be boolean")

    def record(self):
        return {**asdict(self), "version": "market_configuration_v1",
                "descriptor_version": "spy_qqq_long_trend_v1",
                "descriptor_rule": "Both SPY/QQQ close_sma200 and sma200_slope20 positive: UPTREND; all negative: DOWNTREND; otherwise MIXED; missing inputs: UNCLASSIFIED",
                "availability_interpretation": "MODEL_ASSUMPTION_NOT_VERIFIED_VENDOR_PUBLICATION",
                "trading_permission_rule": "NONE"}


def feature_definitions():
    definitions = {}

    def add(name, group, inputs, observations, operation, formula, *parameters):
        definitions[name] = {"group": group, "inputs": list(inputs), "observations": observations,
                             "operation": operation, "parameters": list(parameters), "formula": formula,
                             "units": "fraction", "version": DEFINITION_VERSION,
                             "window": "consecutive_expected_sessions_including_current_completed_session",
                             "availability": "inherits_row_available_at_and_interpretation"}

    for symbol, periods in (("SPY", (50, 150, 200)), ("QQQ", (50, 200)), ("RSP", (50, 200))):
        for n in periods:
            add(f"{symbol}.close_sma{n}", "trend_features", [symbol], n, "close_sma", f"Close[t]/mean(Close[t-{n-1}:t])-1", n)
        pairs = ((50, 200), (50, 150), (150, 200)) if symbol == "SPY" else ((50, 200),) if symbol == "QQQ" else ()
        for a, b in pairs:
            add(f"{symbol}.sma{a}_sma{b}", "trend_features", [symbol], b, "sma_ratio", f"SMA{a}[t]/SMA{b}[t]-1", a, b)
        if symbol != "RSP":
            add(f"{symbol}.sma200_slope20", "trend_features", [symbol], 220, "slope", "SMA200[t]/SMA200[t-20]-1", 200, 20)
        for n in ((20,) if symbol == "RSP" else (20, 60)):
            add(f"{symbol}.return{n}", "trend_features", [symbol], n + 1, "return", f"Close[t]/Close[t-{n}]-1", n)
        if symbol != "RSP":
            add(f"{symbol}.atr14_close", "volatility_features", [symbol], 15, "atr", "shared simple ATR14[t]/Close[t]; 14 true ranges, 15 bars")
            add(f"{symbol}.realized_volatility20", "volatility_features", [symbol], 21, "volatility", "population stddev of 20 simple Close[d]/Close[d-1]-1 returns; not annualized")
    add("SPY.range20_close", "volatility_features", ["SPY"], 20, "range", "(max(High[t-19:t])-min(Low[t-19:t]))/Close[t]")
    add("RSP_SPY.level", "participation_proxies", ["RSP", "SPY"], 1, "ratio", "RSP_Close[t]/SPY_Close[t]")
    definitions["RSP_SPY.level"]["units"] = "native_price_ratio"
    add("RSP_SPY.change20", "participation_proxies", ["RSP", "SPY"], 21, "ratio_change", "Ratio[t]/Ratio[t-20]-1")
    add("RSP_SPY.relative_sma50", "participation_proxies", ["RSP", "SPY"], 50, "ratio_sma", "Ratio[t]/mean(Ratio[t-49:t])-1")
    for name in ("above_sma50", "above_sma200", "new_high52w", "new_low52w", "advance_decline", "trend_template"):
        add(f"historical_constituents.{name}", "breadth_features", [], 0, "unavailable", "Not calculated without PIT universe, constituent prices and explicit inclusion rules")
    add("historical_universe.valid_setup_share", "leadership_features", [], 0, "unavailable", "Not calculated without PIT universe and versioned setup definition")
    return definitions


def required_history_sessions():
    """220 observations including evaluation session, hence 219 preceding sessions."""
    return max(d["observations"] for d in feature_definitions().values())


def _validate_inputs(datasets, calendar):
    if set(datasets) != set(ROLES):
        raise ValueError("exactly SPY, QQQ and RSP reference datasets are required")
    expected = {s["session_date"] for s in calendar["sessions"]}
    result, ids, bases, providers, contracts = {}, [], [], [], []
    for role in ROLES:
        ds = datasets[role]
        m = ds.manifest
        entry = m["securities"][role]
        ids.append(entry["security"]["security_id"])
        providers.append(m["provider"])
        bases.append(entry["basis"])
        if m["calendar"] != {"name": "XNYS", "version": "4.13.1", "overrides": []}:
            raise ValueError("unsupported reference calendar")
        if entry["security"]["symbol"] != role or entry["security"]["currency"] != "USD":
            raise ValueError("reference identity/currency mismatch")
        if m["provider"] == "ibkr":
            q = entry["qualified_contract"]
            if (not q or q["symbol"] != role or q["secType"] != "STK" or q["currency"] != "USD" or
                    q["exchange"] != "SMART" or q["primaryExchange"] != entry["security"]["primary_exchange"] or
                    type(q["conId"]) is not int or q["conId"] <= 0 or
                    (entry["security"]["con_id"] is not None and entry["security"]["con_id"] != q["conId"])):
                raise ValueError("qualified reference contract mismatch")
            contracts.append(q["conId"])
        quality = ds.quality(role)
        if (quality["issues"] or any(quality[k] for k in ("duplicate_sessions", "off_calendar_sessions", "outside_listing_sessions"))
                or any(i.get("status") == "FAIL" for i in quality["source_capture_issues"])):
            raise ValueError("invalid/conflicting source observations")
        by_day = {}
        for r in ds.bars(role):
            day = r["session_date"]
            # Bars after evaluation end can remain embedded but never enter features.
            if day > calendar["end"]:
                continue
            if day in by_day or day not in expected or not m["start"] <= day <= m["end"]:
                raise ValueError("duplicate/off-calendar/out-of-interval reference observation")
            v = {k: Decimal(r[k]) for k in ("open", "high", "low", "close", "volume")}
            if (any(not x.is_finite() for x in v.values()) or any(v[k] <= 0 for k in ("open", "high", "low", "close"))
                    or v["volume"] < 0 or v["volume"] != v["volume"].to_integral_value()
                    or v["high"] < max(v["open"], v["close"], v["low"])
                    or v["low"] > min(v["open"], v["close"], v["high"])):
                raise ValueError("invalid/nonfinite reference OHLCV")
            if (r["security_id"] != ids[-1] or r["symbol"] != role or r["provider"] != m["provider"]
                    or r["price_basis"] != entry["basis"]["price_basis"] or r["volume_basis"] != entry["basis"]["volume_basis"]):
                raise ValueError("reference provenance/basis mismatch")
            by_day[day] = {k: float(v[k]) for k in v}
        result[role] = by_day
    if (len(set(ids)) != 3 or len(set(providers)) != 1 or any(b != bases[0] for b in bases)
            or (contracts and len(set(contracts)) != 3)):
        raise ValueError("distinct identities and identical provider/native bases required")
    if bases[0]["price_basis"] not in {"IBKR_TRADES_SPLIT_ADJUSTED_DOCUMENTED", "YAHOO_NATIVE_UNVERIFIED"}:
        raise ValueError("unsupported native price basis")
    return result


def _measure(definition, values):
    from market_shared import atr_simple_series, true_range

    op, args = definition["operation"], definition["parameters"]
    rows = values[0]
    c = [r["close"] for r in rows]
    if op == "close_sma": return c[-1] / mean(c) - 1
    if op == "sma_ratio": return mean(c[-args[0]:]) / mean(c[-args[1]:]) - 1
    if op == "slope": return mean(c[-args[0]:]) / mean(c[:args[0]]) - 1
    if op == "return": return c[-1] / c[0] - 1
    if op == "atr":
        ranges = [true_range(r["high"], r["low"], previous["close"]) for previous, r in zip(rows, rows[1:])]
        return atr_simple_series(ranges, 14)[-1] / c[-1]
    if op == "volatility": return pstdev(b / a - 1 for a, b in zip(c, c[1:]))
    if op == "range": return (max(r["high"] for r in rows) - min(r["low"] for r in rows)) / c[-1]
    ratios = [r["close"] / s["close"] for r, s in zip(rows, values[1], strict=True)]
    if op == "ratio": return ratios[-1]
    if op == "ratio_change": return ratios[-1] / ratios[0] - 1
    if op == "ratio_sma": return ratios[-1] / mean(ratios) - 1
    raise ValueError("unknown feature operation")


def build_rows(datasets, calendar, start, end, configuration):
    from ..reporting import shared_identity

    if any(ds.manifest["shared_dependency"] != shared_identity() for ds in datasets.values()):
        raise ValueError("reference shared mathematics differs from installed pin")
    prices = _validate_inputs(datasets, calendar)
    definitions = feature_definitions()
    sessions = calendar["sessions"]
    days = [s["session_date"] for s in sessions]
    output = []
    for i, session in enumerate(sessions):
        day = days[i]
        if not start <= day <= end:
            continue
        available = (timestamp(session["closes_at"]) + timedelta(minutes=configuration.delay_minutes)).isoformat()
        row = {"schema_version": SCHEMA, "session_date": day,
               "available_at": available if configuration.availability != "UNKNOWN" else None,
               "availability_status": configuration.availability,
               "availability_interpretation": "RECONSTRUCTED_NOT_VERIFIED_HISTORICAL_DISSEMINATION",
               "last_included_observation": day, **{g: {} for g in GROUPS}, "missing_features": []}
        for name, definition in definitions.items():
            n = definition["observations"]
            window = days[max(0, i - n + 1):i + 1]
            value, reason = None, None
            if not definition["inputs"]:
                reason = "HISTORICAL_CONSTITUENT_DATA_NOT_PROVIDED"
            elif len(window) < n:
                reason = "INSUFFICIENT_WARMUP"
            elif any(d not in prices[role] for role in definition["inputs"] for d in window):
                reason = "MISSING_EXPECTED_SESSION"
            else:
                value = _measure(definition, [[prices[role][d] for d in window] for role in definition["inputs"]])
                if not isfinite(value):
                    raise ValueError("nonfinite derived feature")
            row[definition["group"]][name] = {"value": value, "status": "AVAILABLE" if reason is None else "UNAVAILABLE",
                                              "reason": reason, "last_included_observation": day if reason is None else None}
            if reason:
                row["missing_features"].append(name)
        row["feature_quality"] = {g: dict(Counter(v["status"] for v in row[g].values())) for g in GROUPS}
        row["descriptive_state"] = None
        if configuration.describe_state:
            terms = [row["trend_features"][f"{s}.{k}"]["value"] for s in ("SPY", "QQQ") for k in ("close_sma200", "sma200_slope20")]
            row["descriptive_state"] = ("UNCLASSIFIED" if any(v is None for v in terms) else
                                        "UPTREND" if all(v > 0 for v in terms) else
                                        "DOWNTREND" if all(v < 0 for v in terms) else "MIXED")
        output.append(row)
    return output
