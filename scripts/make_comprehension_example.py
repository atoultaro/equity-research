#!/usr/bin/env python3
"""Deterministic offline example. Synthetic prices are NOT historical evidence."""

import argparse
from datetime import UTC, date, datetime, timedelta
import json
from pathlib import Path
from types import SimpleNamespace

from equity_research.comprehension.inputs import freeze_inputs
from equity_research.comprehension.study import freeze_study
from equity_research.history.depth import DepthAudit
from equity_research.history.depth_store import freeze_report
from equity_research.ingestion.calendar import schedule
from equity_research.providers.ibkr import Pacer

SYMBOLS = ("SAIL", "SLB", "GE", "SCCO", "SPY", "QQQ", "RSP", "IWM", "XLK")


class SyntheticBroker:
    client_version = "synthetic-offline-example"

    def __init__(self):
        self.errors = []

    async def connect(self, *args):
        pass  # No socket or brokerage library exists in this example.

    async def qualify(self, security):
        return [SimpleNamespace(conId=1000+SYMBOLS.index(security.symbol), symbol=security.symbol,
            secType="STK", currency="USD", exchange="SMART", primaryExchange="ARCA",
            localSymbol=security.symbol, tradingClass=security.symbol)]

    async def head_timestamp(self, contract):
        return datetime(2020, 1, 2, 14, 30, tzinfo=UTC)

    async def historical(self, contract, params):
        end = datetime.strptime(params["endDateTime"], "%Y%m%d-%H:%M:%S").date()-timedelta(days=1)
        first = end-timedelta(days=366*int(params["durationStr"].split()[0])-1)
        rows = []
        for s in schedule(first.isoformat(), end.isoformat())["sessions"]:
            i = (date.fromisoformat(s["session_date"])-date(2020, 1, 1)).days
            close = 30+(contract.conId-1000)*10+i/100
            rows.append(SimpleNamespace(date=date.fromisoformat(s["session_date"]), open=close-.1,
                high=close+1, low=close-1, close=close, volume=10000))
        return rows

    def disconnect(self):
        pass


def make(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    virtual = [0.0]

    async def sleep(seconds):
        virtual[0] += seconds

    instruments = [{"kind": "stock" if s in SYMBOLS[:4] else "market_etf", "security": {
        "symbol": s, "security_id": f"synthetic:{s}", "reference": "Synthetic demonstration, not actual issuer history",
        "yahoo_symbol": s, "ibkr_symbol": s, "primary_exchange": "ARCA", "listing_venue": "ARCX"}} for s in SYMBOLS]
    config = {"schema_version": "ibkr_depth_config_v1", "start": "2025-01-02", "end": "2026-10-26",
        "window_days": 1825, "instruments": instruments}
    DepthAudit(port=7496, client_id=1, origin="synthetic", backend_factory=SyntheticBroker,
        clock=lambda: datetime(2026, 10, 27, 1, tzinfo=UTC),
        pacer=Pacer(clock=lambda: virtual[0], sleep=sleep), sleep=sleep).run(config, output / "audit")
    freeze_report(output / "audit", output / "audit-report")
    observations = json.loads((Path(__file__).parents[1] / "experiments/grimes-20261026-observations-v1.json").read_bytes())
    spec = {"schema_version": "expert_research_inputs_v1", "analysis_start": config["start"],
        "observations": observations, "classifications": [], "event_evidence": [],
        "es_context": {"status": "NOT_AVAILABLE", "reason": "Synthetic fixture has no futures"}}
    freeze_inputs(spec, [(output / "audit-report", list(SYMBOLS))], output / "inputs")
    return freeze_study(output / "inputs", output / "study")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    print(json.dumps({"bundle_sha256": make(parser.parse_args().output)["bundle_sha256"]}, sort_keys=True))
