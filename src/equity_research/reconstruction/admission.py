"""Conditional observed-price admission, with no historical-population claims."""

from datetime import timedelta
from decimal import Decimal
from math import isfinite
from ..comprehension.features import Panel
from ..comprehension.inputs import PRICE_BASIS, VOLUME_BASIS
from ..models import timestamp

MODE = "EXPLORATORY_RECONSTRUCTION"


def admit(prices, coverage, calendar, cutoff, mode=MODE, scale_views=None):
    if mode != MODE:
        raise ValueError("explicit EXPLORATORY_RECONSTRUCTION mode required")
    # Existing validation checks identity, basis, positive consistent OHLC and
    # finite nonnegative volume. Future bars are excluded before validation.
    panel = Panel(prices, coverage, calendar, cutoff)
    identities = []
    for symbol, info in coverage.items():
        con_id = info.get("contract", {}).get("conId")
        if type(con_id) is not int or con_id <= 0:
            raise ValueError("qualified contract identity required")
        identities.append(con_id)
        if info["price_basis"] != PRICE_BASIS or info["volume_basis"] != VOLUME_BASIS:
            raise ValueError("undeclared native price/volume convention")
    if len(set(identities)) != len(identities):
        raise ValueError("ambiguous duplicate contract identities")
    for symbol, view in (scale_views or {}).items():
        factor = Decimal(str(view["factor"]))
        if (symbol not in prices or not factor.is_finite() or factor <= 0 or not isfinite(float(factor)) or not view.get("evidence_reference")
                or view.get("status") not in {"ASSUMED_RELATIVE_SCALE", "DOCUMENTED_COMPONENT"}
                or view.get("raw_price_claim") is not False):
            raise ValueError("explicit positive derived scale and uncertainty provenance required")
        panel.prices[symbol] = {day: {k: v*float(factor) if k in {"open", "high", "low", "close"} else v
            for k, v in row.items()} for day, row in panel.prices[symbol].items()}
        if any(not isfinite(v) or v <= 0 for row in panel.prices[symbol].values()
               for k, v in row.items() if k in {"open", "high", "low", "close"}):
            raise ValueError("derived OHLC scale must remain finite and positive")
    return panel, {"mode": MODE, "price_scale": "EXPLICIT_DERIVED_UNVERIFIED" if scale_views else "CONDITIONAL_NATIVE_STOP_COMPATIBILITY",
        "derived_price_views": scale_views or {}, "raw_price_or_volume_promoted": False,
        "availability": "ASSUMED_CASH_CLOSE_PLUS_60_MINUTES", "volume": "NATIVE_UNITS_UNVERIFIED",
        "historical_population_eligibility": "NOT_CLAIMED", "actual_fills": None,
        "actual_position_sizes": None, "actual_realized_pnl": None,
        "missing_sessions": "Unavailable; never forward filled or skipped in required windows"}


class Evidence:
    def __init__(self, prices, coverage, calendar, cutoff, scale_views=None):
        self.prices, self.coverage, self.calendar = prices, coverage, calendar
        self.scale_views = scale_views or {}
        self.panel, self.admission = admit(prices, coverage, calendar, cutoff, scale_views=scale_views)
        self.cache = {}

    def features(self, symbol, cutoff):
        available = [s["session_date"] for s in self.calendar["sessions"]
                     if s["session_date"] in self.panel.days and timestamp(s["closes_at"])+timedelta(minutes=60) < timestamp(cutoff)]
        day = available[-1] if available else None
        key = symbol, day
        if key not in self.cache:
            self.cache[key] = self.panel.features(symbol, day) if day else {}
            if symbol in self.scale_views:
                for measurement in self.cache[key].values():
                    measurement["attribution"] = "CONDITIONAL_DERIVED_PRICE_VIEW"
                    measurement["analysis_view"] = self.scale_views[symbol]
        return day, self.cache[key]

    def rows(self, symbol):
        admitted = [r for r in self.prices[symbol] if r["session_date"] in self.panel.days]
        if symbol not in self.scale_views:
            return {r["session_date"]: r for r in admitted}
        view = self.scale_views[symbol]
        factor = Decimal(str(view["factor"]))
        return {r["session_date"]: {**r, **{k: str(Decimal(r[k])*factor) for k in ("open", "high", "low", "close")},
            "price_basis": "DERIVED_EXPLORATORY_NOT_RAW", "native_price_basis": r["price_basis"], "analysis_view": view}
            for r in admitted}


def value(features, name):
    return features.get(name, {}).get("value")


def risk_geometry(direction, entry, stop, atr, entry_range=None):
    sign = 1 if direction == "LONG" else -1
    risk = sign*(float(entry)-float(stop))
    bounds = sorted(sign*(float(x)-float(stop)) for x in (entry_range or [entry, entry]))
    protective_bounds = [max(0, bounds[0]), bounds[1]] if bounds[1] > 0 else None
    return {"reference_risk": risk, "reference_risk_ATR": risk/atr if atr else None,
        "ohlc_compatible_risk_range": bounds,
        "ohlc_compatible_risk_ATR_range": [x/atr for x in bounds] if atr else None,
        "positive_protective_risk_range": protective_bounds,
        "positive_protective_risk_ATR_range": [x/atr for x in protective_bounds] if atr and protective_bounds else None,
        "zero_lower_bound_is_excluded": protective_bounds is not None and protective_bounds[0] == 0,
        "nonpositive_risk_price_references_rejected": bounds[0] <= 0,
        "actual_initial_risk": None, "unit": "hypothetical_per_share_native_price_units"}
