"""Independent pinned XNYS schedule. No schedule is inferred from price rows."""

from datetime import date, timedelta
from functools import lru_cache
import importlib.metadata
import json

from .storage import digest, encode

CALENDAR_VERSION = "4.13.1"


def schedule(start: str, end: str) -> dict:
    version = importlib.metadata.version("exchange-calendars")
    if version != CALENDAR_VERSION:
        raise ValueError(f"exchange-calendars=={CALENDAR_VERSION} is required")
    return json.loads(_schedule_bytes(start, end, version))


@lru_cache(maxsize=128)
def _schedule_bytes(start: str, end: str, version: str) -> bytes:
    import exchange_calendars as xcals

    first, last = date.fromisoformat(start), date.fromisoformat(end)
    if first > last:
        raise ValueError("start must not follow end")
    # Explicit bounds avoid the library's current-date-dependent default span.
    cal = xcals.get_calendar("XNYS", start=first - timedelta(days=7), end=last + timedelta(days=7))
    rows = [{"session_date": ts.date().isoformat(), "opens_at": row.open.isoformat(),
             "closes_at": row.close.isoformat()}
            for ts, row in cal.schedule.loc[start:end].iterrows()]
    record = {"schema_version": "exchange_schedule_v1", "calendar": "XNYS", "version": version,
              "timezone": "America/New_York", "start": start, "end": end, "overrides": [],
              "sessions": rows}
    return encode(dict(record, schedule_sha256=digest(encode(record))))
