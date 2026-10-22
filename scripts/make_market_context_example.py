"""Offline synthetic engineering example. No actual market observations or edge."""

import argparse
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

from equity_research.history.cache import HistoryCache, history
from equity_research.history.contracts import Security
from equity_research.history.dataset import freeze
from equity_research.ingestion.calendar import schedule
from equity_research.ingestion.storage import encode
from equity_research.market_context import freeze_market_context, load_market_context
from equity_research.providers.ibkr import IBKRDailyProvider, Pacer

FIXED = datetime(2026, 10, 22, tzinfo=UTC)
ACQUIRED_START, START, END = "2022-11-01", "2024-01-02", "2026-10-20"


class SyntheticBackend:
    client_version = "synthetic-v1"

    def __init__(self):
        self.errors = []

    async def connect(self, *args): pass
    def disconnect(self): pass

    async def qualify(self, security):
        return [SimpleNamespace(conId=security.con_id, symbol=security.symbol, secType="STK",
                                exchange="SMART", primaryExchange=security.primary_exchange,
                                currency="USD", localSymbol=security.symbol, tradingClass=security.symbol)]

    async def historical(self, contract, params):
        end = datetime.strptime(params["endDateTime"], "%Y%m%d-%H:%M:%S").date() - timedelta(days=1)
        start = end - timedelta(days=int(params["durationStr"].split()[0]) - 1)
        days = [r["session_date"] for r in schedule(ACQUIRED_START, END)["sessions"]]
        result = []
        for i, day in enumerate(days):
            if start.isoformat() <= day <= end.isoformat():
                close = 100 + contract.conId + i / 10 + (i % 7) / 20
                result.append(SimpleNamespace(date=day.replace("-", ""), open=close-.2, high=close+2,
                                              low=close-2, close=close, volume=1000000, average=close, barCount=100))
        return result


class VirtualTime:
    def __init__(self): self.value = 0.0
    def now(self): return self.value
    async def sleep(self, seconds): self.value += seconds


def demonstrate(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    selected = [Security(s, f"synthetic:{s}:ETF", "synthetic identity, no live qualification", s, s,
                         "NASDAQ" if s == "QQQ" else "ARCA", "XNAS" if s == "QQQ" else "ARCX", con_id=i)
                for i, s in enumerate(("SPY", "QQQ", "RSP"), 1)]
    virtual = VirtualTime()
    provider = IBKRDailyProvider(port=7497, client_id=17, backend_factory=SyntheticBackend,
                                origin="synthetic", clock=lambda: FIXED,
                                pacer=Pacer(clock=virtual.now, sleep=virtual.sleep), sleep=virtual.sleep)
    cache = HistoryCache(output / "cache")
    report = history(cache, provider, selected, ACQUIRED_START, END, clock=lambda: FIXED,
                     permission_reference="Synthetic-only injected backend; no network/broker")
    if report["status"] != "SUCCESS":
        raise ValueError("synthetic fixture acquisition failed")
    freeze(cache, "ibkr", selected, ACQUIRED_START, END, output / "prices", clock=lambda: FIXED)
    hashes = freeze_market_context({s.symbol: output / "prices" for s in selected}, START, END, output / "context")
    context = load_market_context(output / "context")
    summary = {"origin": "SYNTHETIC_ONLY", "live_requests": 0, "context_sha256": hashes["bundle_sha256"],
               "quality": context.quality, "strategy_edge_claim": False}
    (output / "synthetic-summary.json").write_bytes(encode(summary))
    return summary


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    print(encode(demonstrate(p.parse_args().output)).decode())
