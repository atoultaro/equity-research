"""Deterministic, diagnostic conversion. Every returned row retains a locator."""

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo

from .storage import digest, encode

FIELDS = {"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"}
ACTION_FIELDS = {"Stock Splits": "split", "Dividends": "dividend", "Capital Gains": "capital_gain"}


def session_date(value) -> str | None:
    import pandas as pd

    if value is pd.NaT or value is pd.NA or value is None:
        return None
    if isinstance(value, str):
        try:
            return date.fromisoformat(value).isoformat()
        except ValueError:
            return None
    if isinstance(value, datetime):
        local = value.astimezone(ZoneInfo("America/New_York")) if value.tzinfo else value
        if (local.hour, local.minute, local.second, local.microsecond) != (0, 0, 0, 0):
            return None
        return local.date().isoformat()
    return value.isoformat() if isinstance(value, date) else None


def price_columns(frame, symbol: str):
    """Accept flat or either orientation of a single-symbol, two-level frame."""
    import pandas as pd

    if isinstance(frame.columns, pd.MultiIndex):
        if frame.columns.nlevels != 2:
            raise ValueError("unsupported column hierarchy")
        choices = [level for level in (0, 1)
                   if set(frame.columns.get_level_values(level)) == {symbol}]
        if len(choices) != 1:
            raise ValueError("ambiguous or mismatched response symbol")
        names = list(frame.columns.get_level_values(1 - choices[0]))
    else:
        names = list(frame.columns)
    if len(set(names)) != len(names) or any(not isinstance(v, str) for v in names):
        raise ValueError("duplicate or invalid column names")
    return {name: i for i, name in enumerate(names)}


def convert(frame, *, security_id: str | None, provider_symbol: str, frame_sha256: str,
            snapshot_sha256: str, discontinuity_fraction: str = "0.5") -> dict:
    issues, rows, events = [], [], []

    def issue(code, row=None, session=None, severity="FAIL", field=None):
        issues.append({"code": code, "status": severity, "row": row, "session_date": session,
                       "field": field, "source": {"file": "returned_frame.json", "sha256": frame_sha256,
                                                  "row": row}})

    try:
        columns = price_columns(frame, provider_symbol)
    except ValueError:
        columns = {}
        issue("COLUMN_SCHEMA_INVALID")
    for name in FIELDS:
        if name not in columns:
            issue("MISSING_COLUMN", field=name)
    for name in columns:
        if name not in FIELDS.keys() | ACTION_FIELDS.keys() | {"Adj Close"}:
            issue("UNEXPECTED_COLUMN", field=name)
    seen, previous = {}, None
    previous_close = None
    threshold = Decimal(discontinuity_fraction)
    if not threshold.is_finite() or threshold <= 0:
        raise ValueError("discontinuity threshold must be finite and positive")
    for i, raw_date in enumerate(frame.index):
        day = session_date(raw_date)
        prior_index = seen.get(day)
        if day is None:
            issue("INVALID_SESSION_DATE", i)
        elif day in seen:
            issue("DUPLICATE_SESSION", i, day)
            # Do not choose between even identical duplicate observations.
        elif previous is not None and day < previous:
            issue("OUT_OF_ORDER", i, day)
        if day is not None:
            seen[day] = i
            previous = day

        def numeric(name):
            if name not in columns:
                return None
            value = frame.iloc[i, columns[name]]
            try:
                if isinstance(value, bool):
                    raise InvalidOperation
                result = Decimal(str(value))
                if not result.is_finite():
                    raise InvalidOperation
                return result
            except (InvalidOperation, ValueError, TypeError):
                issue("MISSING_OR_NONFINITE_NUMBER", i, day, field=name)
                return None

        numbers = {key: numeric(name) for name, key in FIELDS.items()}
        adjusted = numeric("Adj Close")
        if adjusted is not None and numbers["close"] is not None and adjusted != numbers["close"]:
            issue("ADJUSTED_CLOSE_DIFFERS_REVIEW", i, day, "WARNING", field="Adj Close")
        if prior_index is not None:
            values = {**{k: str(v) if v is not None else None for k, v in numbers.items()},
                      "adj_close": str(adjusted) if adjusted is not None else None}
            if any(rows[prior_index][k] != v for k, v in values.items()):
                issue("CONFLICTING_SESSION", i, day)
        prices = [numbers[k] for k in ("open", "high", "low", "close")]
        if any(v is not None and v <= 0 for v in prices):
            issue("NONPOSITIVE_PRICE", i, day)
        if all(v is not None for v in prices):
            o, h, l, c = prices
            if h < max(o, c, l) or l > min(o, c, h):
                issue("INVALID_OHLC_RANGE", i, day)
        volume = numbers["volume"]
        if volume is not None:
            if volume < 0:
                issue("NEGATIVE_VOLUME", i, day)
            elif volume == 0:
                issue("ZERO_VOLUME", i, day, "WARNING")
            if volume != volume.to_integral_value():
                issue("NONINTEGRAL_VOLUME", i, day)
        close = numbers["close"]
        if close is not None and previous_close is not None and previous_close > 0:
            if abs(close / previous_close - 1) > threshold:
                issue("PRICE_DISCONTINUITY_REVIEW", i, day, "WARNING")
        previous_close = close
        locator = {"file": "returned_frame.json", "sha256": frame_sha256, "row": i}
        rows.append({"security_id": security_id, "provider_symbol": provider_symbol, "session_date": day,
                     **{k: str(v) if v is not None else None for k, v in numbers.items()},
                     "adj_close": str(adjusted) if adjusted is not None else None,
                     "source_snapshot_sha256": snapshot_sha256, "source_row": locator})
        for name, kind in ACTION_FIELDS.items():
            value = numeric(name)
            if value is not None and value != 0:
                if value < 0:
                    issue("INVALID_ACTION_VALUE", i, day, field=name)
                events.append({"type": kind, "session_date": day, "value": str(value),
                               "source": locator, "coverage": "returned_interval_only_not_complete"})
    result = {"schema_version": "canonical_daily_v1", "rows": rows, "issues": issues,
              "events": events, "configuration": {"discontinuity_fraction": discontinuity_fraction}}
    return dict(result, content_sha256=digest(encode(result)))
