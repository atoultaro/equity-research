"""Create a tiny *synthetic* acquisition and affirmative test evidence, offline.

This never establishes any real Yahoo basis, identity, action coverage or latency.
Run after installing the optional data extra. Existing output paths are rejected.
"""

import argparse
from pathlib import Path

import pandas as pd

from equity_research.ingestion.calendar import schedule
from equity_research.ingestion.snapshots import read_snapshot, write_snapshot
from equity_research.ingestion.storage import encode
from equity_research.providers.yahoo import request_record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    output = parser.parse_args().output
    output.mkdir(parents=True, exist_ok=False)
    req = request_record("SYNTH", "2024-11-27", "2024-11-29")
    req["origin"] = "synthetic"
    frame = pd.DataFrame({"Open": [100.0, 101.0], "High": [102.0, 103.0], "Low": [99.0, 100.0],
                          "Close": [101.0, 102.0], "Volume": [1000, 1100], "Adj Close": [101.0, 102.0],
                          "Dividends": [0.0, 0.0], "Stock Splits": [0.0, 0.0]},
                         index=pd.to_datetime(["2024-11-27", "2024-11-29"]))
    write_snapshot(output / "snapshot", req, {"status": "SUCCESS", "started_at": "2025-02-01T12:00:00Z",
                   "completed_at": "2025-02-01T12:00:00Z", "client": "synthetic", "client_version": "fixture_v1",
                   "historical_availability": "unknown", "errors": []}, frame)
    reference = {"status": "VERIFIED", "reference": "synthetic:gate-mechanics-only"}
    horizon = {"coverage_start": req["start"], "coverage_end": "2025-02-01"}
    evidence = {"schema_version": "research_evidence_v1", "kind": "synthetic",
                "snapshot_content_sha256": read_snapshot(output / "snapshot")["acquisition"]["content_sha256"],
                "identity": {**reference, "security_id": "synthetic-security-1", "research_symbol": "SYNTH",
                             "provider_symbol": "SYNTH", "listing_venue": "XNYS", "currency": "USD",
                             "known_at": "2024-01-01T00:00:00Z", "valid_from": "2000-01-01", "valid_through": "2030-01-01"},
                "basis": {**reference, **horizon, "price_basis": "RAW_VERIFIED",
                          "split_adjustment": {**reference, "convention": "unadjusted"},
                          "dividend_adjustment": {**reference, "convention": "unadjusted"},
                          "volume": {**reference, "units": "contemporaneous_shares"}},
                "actions": {**reference, **horizon, "events": []},
                "availability": {**reference, "historical_availability": "verified", "sessions": {
                    s["session_date"]: s["closes_at"] for s in schedule(req["start"], req["end"])["sessions"]}}}
    (output / "evidence.json").write_bytes(encode(evidence))
    print(output)


if __name__ == "__main__":
    main()
