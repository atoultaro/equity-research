"""Small validated inputs; prices/costs use Decimal, features use shared float math."""

from dataclasses import dataclass, fields
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any
from zoneinfo import ZoneInfo


def number(value: Any) -> Decimal:
    if isinstance(value, bool):
        raise ValueError("boolean is not a numeric input")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"invalid numeric input: {value!r}") from exc
    if not result.is_finite():
        raise ValueError("numeric inputs must be finite")
    return result


def timestamp(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("timestamps must be ISO strings")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("timestamps must be timezone-aware")
    return result.astimezone(UTC)


@dataclass(frozen=True)
class Candidate:
    symbol: str
    source: str
    observed_at: datetime
    available_at: datetime
    candidate_session: date
    setup_family: str
    provenance: dict

    @classmethod
    def from_dict(cls, raw: dict) -> "Candidate":
        allowed = {f.name for f in fields(cls)}
        if set(raw) - allowed:
            raise ValueError("unknown candidate fields")
        observed, available = timestamp(raw["observed_at"]), timestamp(raw["available_at"])
        if available < observed:
            raise ValueError("candidate availability precedes observation")
        session = date.fromisoformat(raw["candidate_session"])
        if session > observed.astimezone(ZoneInfo("America/New_York")).date():
            raise ValueError("candidate session is after its observation")
        if not raw["symbol"] or not raw["source"]:
            raise ValueError("candidate symbol/source must be nonempty")
        provenance = raw.get("provenance", {})
        if not isinstance(provenance, dict):
            raise ValueError("candidate provenance must be an object")
        return cls(raw["symbol"], raw["source"], observed, available,
                   session, raw["setup_family"], provenance)


@dataclass(frozen=True)
class Config:
    policy_version: str = "long_trend_breakout_v1"
    initial_equity: Decimal = Decimal("10000")
    risk_fraction: Decimal = Decimal("0.01")
    sma_period: int = 50
    sma_rising_lookback: int = 5
    atr_period: int = 14
    liquidity_lookback: int = 20
    min_average_volume: Decimal = Decimal("100000")
    entry_buffer: Decimal = Decimal("0.10")
    stop_atr_multiple: Decimal = Decimal("2")
    order_valid_sessions: int = 3
    target_r: Decimal | None = Decimal("2")
    max_holding_sessions: int = 10
    max_position_notional: Decimal | None = None
    price_increment: Decimal = Decimal("0.01")
    slippage_per_share: Decimal = Decimal("0.01")
    commission_per_share: Decimal = Decimal("0.005")
    fees_per_order: Decimal = Decimal("0.50")

    @classmethod
    def from_dict(cls, raw: dict) -> "Config":
        defaults = cls()
        if set(raw) - {f.name for f in fields(cls)}:
            raise ValueError("unknown configuration fields")
        values = {}
        for f in fields(cls):
            value = raw.get(f.name, getattr(defaults, f.name))
            default = getattr(defaults, f.name)
            if isinstance(default, Decimal) or f.name in {"target_r", "max_position_notional"}:
                if value is None and f.name in {"target_r", "max_position_notional"}:
                    values[f.name] = None
                else:
                    values[f.name] = number(value)
            elif isinstance(default, int):
                if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                    raise ValueError(f"{f.name} must be a positive integer")
                values[f.name] = value
            else:
                values[f.name] = value
        result = cls(**values)
        if result.policy_version != defaults.policy_version:
            raise ValueError("unsupported policy version")
        if result.initial_equity <= 0 or not 0 < result.risk_fraction <= 1:
            raise ValueError("invalid equity/risk budget")
        for name in ("price_increment", "stop_atr_multiple", "target_r", "max_position_notional"):
            value = getattr(result, name)
            if value is not None and value <= 0:
                raise ValueError(f"{name} must be positive")
        for name in ("entry_buffer", "min_average_volume", "slippage_per_share",
                     "commission_per_share", "fees_per_order"):
            if getattr(result, name) < 0:
                raise ValueError(f"{name} must be nonnegative")
        return result
