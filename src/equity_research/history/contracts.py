"""Small explicit security mappings and acquisition boundary; no client imports."""

from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime
from pathlib import Path
import re
from typing import Protocol


def now_utc():
    return datetime.now(UTC)


def interval(start, end):
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    if first.isoformat() != start or last.isoformat() != end or first > last:
        raise ValueError("expected an ordered, inclusive YYYY-MM-DD interval")
    if (last - first).days > 3660:
        raise ValueError("one acquisition is limited to 3661 calendar days")
    return first, last


@dataclass(frozen=True)
class Security:
    symbol: str
    security_id: str
    reference: str
    yahoo_symbol: str
    ibkr_symbol: str
    primary_exchange: str
    listing_venue: str
    currency: str = "USD"
    con_id: int | None = None
    first_session: str | None = None
    last_session: str | None = None
    listing_reference: str | None = None

    def __post_init__(self):
        for name in ("symbol", "security_id", "reference", "yahoo_symbol", "ibkr_symbol",
                     "primary_exchange", "listing_venue"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"explicit {name} is required")
        for name in ("symbol", "yahoo_symbol", "ibkr_symbol", "primary_exchange"):
            if not re.fullmatch(r"[A-Z0-9^][A-Z0-9^ ./=-]{0,31}", getattr(self, name)):
                raise ValueError(f"invalid uppercase {name}")
        if self.currency != "USD":
            raise ValueError("v1 supports USD US stocks/ETFs only")
        if self.con_id is not None and (type(self.con_id) is not int or self.con_id <= 0):
            raise ValueError("con_id must be a positive integer")
        if self.listing_reference is not None and (not isinstance(self.listing_reference, str) or not self.listing_reference.strip()):
            raise ValueError("listing_reference must be a nonempty string")
        for value in (self.first_session, self.last_session):
            if value is not None and date.fromisoformat(value).isoformat() != value:
                raise ValueError("listing boundaries require ISO dates")
        if self.first_session and self.last_session and self.first_session > self.last_session:
            raise ValueError("reversed listing boundaries")
        if (self.first_session or self.last_session) and not self.listing_reference:
            raise ValueError("listing boundaries require an explicit source reference")

    def record(self):
        return asdict(self)

    def provider_key(self, provider):
        if provider == "yahoo":
            from ..providers.yahoo import provider_symbol
            if provider_symbol(self.yahoo_symbol) != self.yahoo_symbol:
                raise ValueError("mapping must specify the exact Yahoo symbol")
            return self.yahoo_symbol
        if provider == "ibkr":
            return f"{self.ibkr_symbol}|{self.primary_exchange}|{self.currency}"
        raise ValueError("unsupported provider")


def select_securities(records, symbols, provider):
    if not 1 <= len(symbols) <= 20 or len(set(symbols)) != len(symbols):
        raise ValueError("request 1..20 distinct symbols")
    securities = [Security(**row) for row in records]
    if len({s.symbol for s in securities}) != len(securities):
        raise ValueError("duplicate research symbol in mappings")
    keyed = {s.symbol: s for s in securities}
    selected = [keyed[s] for s in symbols]
    keys = [s.provider_key(provider) for s in selected]
    if len(set(keys)) != len(keys) or len({s.security_id for s in selected}) != len(selected):
        raise ValueError("symbol alias/security identity collision")
    return selected


class DailyProvider(Protocol):
    name: str

    def fetch_daily(self, security: Security, start: str, end: str, output: Path) -> dict:
        """Explicit acquisition, persisting one immutable attempt before returning."""
