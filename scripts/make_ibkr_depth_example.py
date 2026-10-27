"""Frozen offline audit example; no brokerage client or socket is created."""

import argparse
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

from equity_research.history.contracts import Security
from equity_research.history.depth import DepthAudit
from equity_research.history.depth_store import freeze_report
from equity_research.ingestion.calendar import schedule
from equity_research.ingestion.storage import encode
from equity_research.providers.ibkr import Pacer


class VirtualTime:
    value = 0

    def now(self):
        return self.value

    async def sleep(self, seconds):
        self.value += seconds


class FixtureBackend:
    client_version = "synthetic-depth-example-v1"

    def __init__(self):
        self.errors = []

    async def connect(self, host, port, client_id):
        pass

    async def qualify(self, security):
        return [SimpleNamespace(conId={"COMPLETE": 101, "GAPPED": 102}[security.symbol],
            symbol=security.symbol, secType="STK", exchange="SMART", primaryExchange="NASDAQ",
            currency="USD", localSymbol=security.symbol, tradingClass=security.symbol)]

    async def head_timestamp(self, contract):
        return datetime(2024, 11, 25, 14, 30, tzinfo=UTC)

    async def historical(self, contract, params):
        return [SimpleNamespace(date=date.fromisoformat(s["session_date"]), open=100, high=102, low=99,
            close=101, volume=1000) for s in schedule("2024-11-25", "2024-11-29")["sessions"]
            if not (contract.symbol == "GAPPED" and s["session_date"] == "2024-11-26")]

    def disconnect(self):
        pass


def demonstrate(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    config = {"schema_version": "ibkr_depth_config_v1", "start": "2024-11-25", "end": "2024-11-29",
        "instruments": [{"kind": "stock", "security": Security(s, "synthetic:" + s,
            "synthetic:depth-example", s, s, "NASDAQ", "XNAS").record()} for s in ("COMPLETE", "GAPPED")]}
    virtual = VirtualTime()
    audit = DepthAudit(port=7496, client_id=91, origin="synthetic", backend_factory=FixtureBackend,
        clock=lambda: datetime(2024, 11, 30, tzinfo=UTC),
        pacer=Pacer(clock=virtual.now, sleep=virtual.sleep), sleep=virtual.sleep)
    result = audit.run(config, output / "audit")
    hashes = freeze_report(output / "audit", output / "report")
    return {"report_sha256": hashes["bundle_sha256"],
        "results": [{"symbol": r["symbol"], "status": r["status"]} for r in result["instruments"]]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(encode(demonstrate(args.output)).decode(), end="")
