"""Deterministic offline SPY/QQQ/AAPL engineering example, never actual market data."""

import argparse
from datetime import UTC, date, datetime, timedelta
import json
from pathlib import Path
from types import SimpleNamespace

from equity_research.history.cache import HistoryCache, history
from equity_research.history.comparison import compare_providers
from equity_research.history.contracts import Security
from equity_research.history.dataset import freeze, load_research_dataset
from equity_research.history.normalize import read_acquisition
from equity_research.ingestion.calendar import schedule
from equity_research.ingestion.snapshots import write_snapshot
from equity_research.ingestion.storage import encode, write_bundle
from equity_research.providers.ibkr import IBKRDailyProvider, Pacer
from equity_research.providers.yahoo import request_record

FIXED = datetime(2025, 2, 1, tzinfo=UTC)
START, END = "2024-01-02", "2024-12-31"


def securities():
    return [Security(symbol, f"synthetic-{symbol}", "synthetic:identity-only", symbol, symbol,
                     "NASDAQ" if symbol in {"QQQ", "AAPL"} else "ARCA",
                     "XNAS" if symbol in {"QQQ", "AAPL"} else "ARCX") for symbol in ("SPY", "QQQ", "AAPL")]


def frame(symbol, start, end, *, ibkr=False):
    import pandas as pd
    days = [s["session_date"] for s in schedule(START, END)["sessions"]]
    positions = {day: i for i, day in enumerate(days)}
    chosen = [day for day in days if start <= day <= end]
    values = [100 + positions[day] / 4 for day in chosen]
    # Intentional synthetic difference, not an observed AAPL split or correction.
    factor = 0.5 if symbol == "AAPL" and ibkr else 1
    data = {"Open": [v * factor for v in values], "High": [(v + 1) * factor for v in values],
            "Low": [(v - 1) * factor for v in values], "Close": [(v + 0.5) * factor for v in values],
            "Volume": [999900 if ibkr else 1000000] * len(chosen)}
    if not ibkr:
        data["Adj Close"] = [(v + 0.5) * 0.98 for v in values]
        data["Dividends"] = [0] * len(chosen)
        data["Stock Splits"] = [0] * len(chosen)
    return pd.DataFrame(data, index=pd.DatetimeIndex(chosen))


class SyntheticYahoo:
    name = "yahoo"

    def fetch_daily(self, security, start, end, output):
        request = request_record(security.symbol, start, end)
        request["origin"] = "synthetic"
        bars = frame(security.symbol, start, end)
        write_snapshot(output, request, {"started_at": FIXED.isoformat(), "completed_at": FIXED.isoformat(),
                                        "client": "synthetic_yahoo_fixture", "client_version": "v1",
                                        "status": "SUCCESS", "errors": [], "historical_availability": "unknown",
                                        "coverage": {"rows": len(bars)}}, bars)
        return read_acquisition(output, security)


class SyntheticIBBackend:
    """Only historical contract/data operations exist on this backend."""

    client_version = "synthetic-v1"

    def __init__(self):
        self.errors = []

    async def connect(self, host, port, client_id):
        pass

    async def qualify(self, security):
        return [SimpleNamespace(conId={"SPY": 1, "QQQ": 2, "AAPL": 3}[security.symbol],
                                secType="STK", symbol=security.ibkr_symbol, exchange="SMART",
                                primaryExchange=security.primary_exchange, currency="USD",
                                localSymbol=security.ibkr_symbol, tradingClass=security.ibkr_symbol)]

    async def historical(self, contract, params):
        end = datetime.strptime(params["endDateTime"], "%Y%m%d-%H:%M:%S").date() - timedelta(days=1)
        start = end - timedelta(days=int(params["durationStr"].split()[0]) - 1)
        bars = frame(contract.symbol, start.isoformat(), end.isoformat(), ibkr=True)
        return [SimpleNamespace(date=day.date(), **{name.lower(): value for name, value in row.items()})
                for day, row in bars.iterrows()]

    def disconnect(self):
        pass


class VirtualTime:
    value = 0.0

    def now(self):
        return self.value

    async def sleep(self, seconds):
        self.value += seconds


def demonstrate(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    selected = securities()
    (output / "mappings.json").write_bytes(encode([s.record() for s in selected]))
    virtual = VirtualTime()
    ibkr = IBKRDailyProvider(port=7497, client_id=17, backend_factory=SyntheticIBBackend,
                             clock=lambda: FIXED, pacer=Pacer(clock=virtual.now, sleep=virtual.sleep),
                             sleep=virtual.sleep, origin="synthetic")
    summaries = {}
    for provider in (SyntheticYahoo(), ibkr):
        cache = HistoryCache(output / f"{provider.name}-cache")
        report = history(cache, provider, selected, START, END, clock=lambda: FIXED,
                         permission_reference="synthetic:no_provider_access")
        if report["status"] != "SUCCESS":
            raise ValueError(f"synthetic example failed: {report}")
        dataset_path = output / f"{provider.name}-dataset"
        freeze(cache, provider.name, selected, START, END, dataset_path, clock=lambda: FIXED)
        dataset = load_research_dataset(dataset_path)
        summaries[provider.name] = {s.symbol: dataset.indicators(s.symbol)["rows"][-1] for s in selected}
        summaries[provider.name]["SPY_QQQ_ratio"] = dataset.relative_strength("SPY", "QQQ")["rows"][-1]
    yahoo = load_research_dataset(output / "yahoo-dataset")
    ib = load_research_dataset(output / "ibkr-dataset")
    for symbol in ("SPY", "QQQ", "AAPL"):
        write_bundle(output / f"comparison-{symbol}", {"comparison.json": encode(compare_providers(yahoo, ib, symbol, START, END))})
    summary = {"origin": "SYNTHETIC_ONLY", "live_requests": 0, "indicators": summaries,
               "comparison": "DIAGNOSTIC_ONLY_BASIS_UNRESOLVED", "strategy_edge_claim": False}
    (output / "synthetic-summary.json").write_bytes(encode(summary))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(demonstrate(args.output), indent=2))
