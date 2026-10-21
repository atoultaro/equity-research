"""Rebuild the small canonical example; no real prices, current clock, or network."""

import csv
from datetime import date, datetime, time, timedelta
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo


def main():
    root = Path(__file__).resolve().parents[1] / "tests/fixtures"
    signal = date(2026, 3, 10)
    # Explicit fixture schedule, not a general exchange calendar implementation.
    excluded = {date(2025, 12, 25), date(2026, 1, 1), date(2026, 1, 19), date(2026, 2, 16)}
    history = []
    day = signal
    while len(history) < 60:
        if day.weekday() < 5 and day not in excluded:
            history.append(day)
        day -= timedelta(days=1)
    days = sorted(history) + [date(2026, 3, 11), date(2026, 3, 12), date(2026, 3, 13), date(2026, 3, 16)]
    rows = []
    for i, day in enumerate(days[:60]):
        close = 100 + 0.5 * i
        rows.append(["SYNTH", day.isoformat(), close - .25, close + 1, close - 1, close, 1000000])
    for day, prices in zip(days[60:], [(132, 134, 131, 133), (134, 137, 133, 136),
                                     (136, 146, 135, 145), (145, 147, 144, 146)]):
        rows.append(["SYNTH", day.isoformat(), *prices, 1000000])
    data = root / "synthetic_daily.csv"
    with data.open("w", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["symbol", "session_date", "open", "high", "low", "close", "volume"])
        writer.writerows(rows)
    zone = ZoneInfo("America/New_York")
    sessions = [{"session_date": d.isoformat(), "opens_at": datetime.combine(d, time(9, 30), zone).isoformat(),
                 "closes_at": datetime.combine(d, time(16), zone).isoformat(),
                 "available_at": datetime.combine(d, time(16), zone).isoformat()} for d in days]
    manifest = {"symbol": "SYNTH", "source": "deterministic_synthetic_fixture",
                "source_revision": "synthetic_daily_v1", "dataset_version": "1",
                "created_at": None, "created_on": "2026-10-21", "adjustment": "raw", "corporate_actions": [],
                "availability_convention": "at supplied session close; fixed synthetic inputs",
                "exchange": "XNYS", "timezone": "America/New_York", "calendar_version": "explicit_fixture_v1",
                "sessions": sessions, "data_sha256": hashlib.sha256(data.read_bytes()).hexdigest()}
    candidate = {"symbol": "SYNTH", "source": "manual", "candidate_session": signal.isoformat(),
                 "observed_at": "2026-03-10T20:15:00Z", "available_at": "2026-03-10T20:15:00Z",
                 "setup_family": "breakout", "provenance": {"kind": "synthetic", "reference": "synthetic_daily_v1"}}
    for name, value in [("data_manifest.json", manifest), ("candidate.json", candidate), ("swing_config.json", {})]:
        (root / name).write_text(json.dumps(value, indent=2) + "\n")


if __name__ == "__main__":
    main()
