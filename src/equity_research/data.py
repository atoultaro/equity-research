"""Raw daily CSV plus an explicit, versioned session schedule; no inferred sessions."""

import csv
from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from .models import number, timestamp

ET = ZoneInfo("America/New_York")
CSV_FIELDS = {"symbol", "session_date", "open", "high", "low", "close", "volume"}


@dataclass(frozen=True)
class Session:
    session_date: date
    opens_at: datetime
    closes_at: datetime
    available_at: datetime


@dataclass(frozen=True)
class DailyBar:
    symbol: str
    session: Session
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal


@dataclass(frozen=True)
class Dataset:
    bars: tuple[DailyBar, ...]
    manifest: dict
    data_sha256: str


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_dataset(csv_path: Path, manifest_path: Path) -> Dataset:
    raw_bytes = csv_path.read_bytes()
    manifest = json.loads(manifest_path.read_text())
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be an object")
    required = {"symbol", "source", "source_revision", "dataset_version", "created_at",
                "adjustment", "corporate_actions", "availability_convention", "exchange",
                "timezone", "calendar_version", "sessions", "data_sha256"}
    if not required <= manifest.keys():
        raise ValueError(f"manifest missing fields: {sorted(required - manifest.keys())}")
    if any(not manifest[k] for k in ("symbol", "source", "source_revision", "dataset_version",
                                    "availability_convention", "calendar_version")):
        raise ValueError("manifest identity/provenance must be nonempty")
    if manifest["created_at"] is not None:
        timestamp(manifest["created_at"])
    if manifest["adjustment"] != "raw" or manifest["corporate_actions"] != []:
        raise ValueError("only raw prices with no declared corporate actions are supported")
    if manifest["exchange"] != "XNYS" or manifest["timezone"] != "America/New_York":
        raise ValueError("only supplied XNYS/ET session schedules are supported")
    if sha256(raw_bytes) != manifest["data_sha256"]:
        raise ValueError("data content hash mismatch")
    sessions = []
    for row in manifest["sessions"]:
        session = Session(date.fromisoformat(row["session_date"]), timestamp(row["opens_at"]),
                          timestamp(row["closes_at"]), timestamp(row["available_at"]))
        if not session.opens_at < session.closes_at <= session.available_at:
            raise ValueError("session completion/availability order is invalid")
        local_open, local_close = session.opens_at.astimezone(ET), session.closes_at.astimezone(ET)
        if (local_open.date() != session.session_date or local_close.date() != session.session_date
                or session.session_date.weekday() >= 5 or local_open.time() != time(9, 30)
                or local_close.time() not in {time(13), time(16)}):
            raise ValueError("unsupported session date/RTH hours")
        if sessions and (session.session_date <= sessions[-1].session_date
                         or session.opens_at <= sessions[-1].available_at):
            raise ValueError("session schedule must be unique, ascending and available before next open")
        sessions.append(session)
    with csv_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        if set(reader.fieldnames or []) != CSV_FIELDS or len(reader.fieldnames or []) != len(CSV_FIELDS):
            raise ValueError("CSV fields must be exactly symbol,session_date,open,high,low,close,volume")
        rows = list(reader)
    if len(rows) != len(sessions):
        raise ValueError("missing or extra sessions; prices are never forward filled")
    bars = []
    for row, session in zip(rows, sessions):
        if row["symbol"] != manifest["symbol"] or date.fromisoformat(row["session_date"]) != session.session_date:
            raise ValueError("security/session keys must match the unique ascending schedule")
        prices = [number(row[k]) for k in ("open", "high", "low", "close")]
        open_, high, low, close = prices
        volume = number(row["volume"])
        if min(prices) <= 0 or volume < 0:
            raise ValueError("tradable prices must be positive and volume nonnegative")
        if high < max(open_, close, low) or low > min(open_, close, high):
            raise ValueError("inconsistent OHLC range")
        bars.append(DailyBar(row["symbol"], session, open_, high, low, close, volume))
    return Dataset(tuple(bars), manifest, sha256(raw_bytes))
