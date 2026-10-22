"""Certified synthetic raw fixture: post-close signals, gap and PR4 replay.

Explicit synthetic weekday schedule, not an exchange holiday/calendar assertion.
No acquisition, current clock, randomness or historical price claim.
"""

import argparse
import csv
from datetime import date, datetime, time, timedelta
import io
from pathlib import Path
from zoneinfo import ZoneInfo

from equity_research.ingestion.storage import digest, encode, write_bundle
from equity_research.swing import Configuration


def make_fixture(output):
    rows, sessions = [], []
    day, zone = date(2025, 5, 1), ZoneInfo("America/New_York")
    while len(rows) < 205:
        if day.weekday() < 5:
            i = len(rows)
            close = 100 + i / 5
            prices = (close-.25, close+1, close-1, close)
            if i == 199: prices = (139, 144, 139, 143)
            if i >= 200: prices = (146, 160, 145, 150)
            rows.append(["SYNTH", day.isoformat(), *prices, 1000000])
            sessions.append({"session_date": day.isoformat(),
                "opens_at": datetime.combine(day, time(9, 30), zone).isoformat(),
                "closes_at": datetime.combine(day, time(16), zone).isoformat(),
                "available_at": datetime.combine(day, time(16), zone).isoformat()})
        day += timedelta(days=1)
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(["symbol", "session_date", "open", "high", "low", "close", "volume"])
    writer.writerows(rows)
    data = stream.getvalue().encode()
    manifest = {"symbol": "SYNTH", "source": "deterministic_synthetic_fixture", "source_revision": "swing_fixture_v1",
        "dataset_version": "swing_fixture_v1", "created_at": None, "adjustment": "raw", "corporate_actions": [],
        "availability_convention": "explicit synthetic close; strategy adds declared delay", "exchange": "XNYS",
        "timezone": "America/New_York", "calendar_version": "explicit_synthetic_weekdays_v1", "sessions": sessions,
        "data_sha256": digest(data), "certification": "SYNTHETIC_AUTHORED_RAW_NO_ACTIONS_NOT_REAL_MARKET_EVIDENCE"}
    return write_bundle(Path(output), {"data.csv": data, "manifest.json": encode(manifest),
                                     "strategy-config.json": encode(Configuration().record())})


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    print(encode(make_fixture(args.output)).decode(), end="")
