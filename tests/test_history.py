"""Offline acquisition/cache/dataset contracts; all prices and identities synthetic."""

import asyncio
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
import importlib.metadata
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
from types import SimpleNamespace

import pandas as pd
import pytest

from equity_research.cli import main
from equity_research.history.cache import HistoryCache, history
from equity_research.history.comparison import compare_providers
from equity_research.history.contracts import Security, interval, select_securities
from equity_research.history.dataset import freeze, load_research_dataset
from equity_research.history.normalize import read_acquisition, reconcile
from equity_research.ingestion.calendar import schedule
from equity_research.ingestion.snapshots import read_snapshot, write_snapshot
from equity_research.ingestion.storage import digest, encode, read_bundle, write_bundle
from equity_research.providers.ibkr import IBKRDailyProvider, Pacer, classify, make_backend
from equity_research.providers.yahoo import YahooDailyProvider, request_record

FIXED = datetime(2025, 2, 1, tzinfo=UTC)
START, END = "2024-11-25", "2024-11-29"


@pytest.fixture
def security():
    return Security("SPY", "synthetic-SPY", "synthetic:identity", "SPY", "SPY", "ARCA", "ARCX")


def bars(start=START, end=END, *, drop=(), value=100, adjusted=True):
    days = [s["session_date"] for s in schedule(start, end)["sessions"] if s["session_date"] not in drop]
    values = {"Open": [value] * len(days), "High": [value + 2] * len(days),
              "Low": [value - 2] * len(days), "Close": [value + 1] * len(days), "Volume": [1000] * len(days)}
    if adjusted:
        values["Adj Close"] = [value + 1] * len(days)
    return pd.DataFrame(values, index=pd.DatetimeIndex(days))


class FixtureYahoo:
    name = "yahoo"

    def __init__(self, transform=lambda frame: frame):
        self.calls = []
        self.transform = transform

    def fetch_daily(self, security, start, end, output):
        self.calls.append((security.symbol, start, end))
        req = request_record(security.symbol, start, end)
        req["origin"] = "synthetic"
        frame = self.transform(bars(start, end))
        write_snapshot(output, req, {"status": "SUCCESS", "errors": [], "started_at": FIXED.isoformat(),
                                    "completed_at": FIXED.isoformat(), "client": "synthetic", "client_version": "v1"}, frame)
        return read_acquisition(output, security)


class VirtualTime:
    def __init__(self):
        self.value = 0.0
        self.waits = []

    def now(self):
        return self.value

    async def sleep(self, seconds):
        self.waits.append(seconds)
        self.value += seconds


class MockIB:
    """No account, order, execution or position API exists on this fake."""

    client_version = "synthetic-v1"

    def __init__(self, *, frame=None, qualification=None, failures=(), event_errors=()):
        self.errors, self.calls = [], []
        self.frame = bars(adjusted=False) if frame is None else frame
        self.qualification = qualification
        self.failures, self.event_errors = list(failures), list(event_errors)
        self.disconnected = False

    async def connect(self, host, port, client_id):
        self.calls.append(("connect", host, port, client_id))

    async def qualify(self, security):
        self.calls.append(("qualify", security))
        if self.qualification is not None:
            return self.qualification
        return [SimpleNamespace(conId=security.con_id or 123, secType="STK", symbol=security.ibkr_symbol,
                                exchange="SMART", currency=security.currency, primaryExchange=security.primary_exchange,
                                localSymbol=security.ibkr_symbol, tradingClass=security.ibkr_symbol)]

    async def historical(self, contract, params):
        self.calls.append(("historical", contract, params))
        if self.failures:
            raise self.failures.pop(0)
        if self.event_errors:
            self.errors.append(self.event_errors.pop(0))
        return [SimpleNamespace(date=d.date(), **{k.lower(): v for k, v in row.items()})
                for d, row in self.frame.iterrows()]

    def disconnect(self):
        self.calls.append(("disconnect",))
        self.disconnected = True


def ib_provider(backend, *, clock=lambda: FIXED, virtual=None):
    virtual = virtual or VirtualTime()
    return IBKRDailyProvider(port=7497, client_id=17, backend_factory=lambda: backend, clock=clock,
                             pacer=Pacer(clock=virtual.now, sleep=virtual.sleep), sleep=virtual.sleep, origin="synthetic")


def populate(tmp_path, security, provider=None, *, start=START, end=END):
    provider = provider or FixtureYahoo()
    cache = HistoryCache(tmp_path / (provider.name + "-cache"))
    report = history(cache, provider, [security], start, end, clock=lambda: FIXED)
    return cache, report


def datasets(tmp_path, security, yahoo_frame=None, ib_frame=None, *, allow_incomplete=False):
    yahoo = FixtureYahoo(lambda f: yahoo_frame if yahoo_frame is not None else f)
    ib = ib_provider(MockIB(frame=ib_frame))
    out = []
    for provider in (yahoo, ib):
        cache, _ = populate(tmp_path, security, provider)
        path = tmp_path / (provider.name + "-dataset")
        freeze(cache, provider.name, [security], START, END, path, allow_incomplete=allow_incomplete, clock=lambda: FIXED)
        out.append(load_research_dataset(path))
    return out


def test_yahoo_real_adapter_reuses_capture_and_exact_parameters(tmp_path, security, monkeypatch):
    calls = []
    original = importlib.metadata.version
    monkeypatch.setattr(importlib.metadata, "version", lambda n: "0.2.66" if n == "yfinance" else original(n))
    monkeypatch.setitem(sys.modules, "yfinance", SimpleNamespace(download=lambda **kw: calls.append(kw) or bars()))
    cache, report = populate(tmp_path, security, YahooDailyProvider(clock=lambda: FIXED))
    assert report["status"] == "SUCCESS"
    assert calls == [request_record("SPY", START, END)["parameters"]]
    saved = cache.load_cached_daily("yahoo", security, START, END)
    assert saved["cache_status"] == "HIT"
    assert all(r["price_basis"] == "YAHOO_NATIVE_UNVERIFIED" for r in saved["rows"])
    assert saved["metadata"]["basis"]["verified"] is False


def test_cache_miss_population_and_offline_hit_never_call_provider(tmp_path, security):
    provider = FixtureYahoo()
    cache = HistoryCache(tmp_path / "cache")
    assert cache.load_cached_daily("yahoo", security, START, END)["cache_status"] == "MISS"
    assert history(cache, provider, [security], START, END)["status"] == "SUCCESS"
    first_version = cache.load_cached_daily("yahoo", security, START, END)["metadata"]["version"]
    for mode in ("auto", "offline"):
        report = history(cache, provider, [security], START, END, mode=mode)
        assert report["results"][0]["acquisition_status"] == "NOT_REQUESTED"
    assert len(provider.calls) == 1
    assert cache.load_cached_daily("yahoo", security, START, END)["metadata"]["version"] == first_version


def test_incremental_overlap_correction_and_snapshot_immutability(tmp_path, security):
    provider = FixtureYahoo()
    cache, first = populate(tmp_path, security, provider, end="2024-11-26")
    snapshot = Path(first["results"][0]["snapshot_reference"])
    snapshot_files, hashes = read_bundle(snapshot)
    provider.transform = lambda f: f.assign(Close=102)
    report = history(cache, provider, [security], START, END, overlap_days=0)
    assert provider.calls == [("SPY", START, "2024-11-26"), ("SPY", "2024-11-26", END)]
    changes = report["results"][0]["corrections"]
    assert changes == [{"session_date": "2024-11-26", "field": "close", "before": "101", "after": "102"}]
    assert read_bundle(snapshot) == (snapshot_files, hashes)
    cached = cache.load_cached_daily("yahoo", security, START, END)
    assert len(cached["metadata"]["sources"]) == 2
    assert cached["rows"][0]["close"] == "101"  # Outside the explicitly refreshed interval.
    assert cached["rows"][1]["close"] == "102"


def test_explicit_full_refresh_and_removed_session_not_masked(tmp_path, security):
    provider = FixtureYahoo()
    cache, _ = populate(tmp_path, security, provider)
    provider.transform = lambda f: f.drop(pd.Timestamp("2024-11-26"))
    report = history(cache, provider, [security], START, END, mode="full")
    result = report["results"][0]
    assert provider.calls[-1] == ("SPY", START, END)
    assert result["removed_sessions"] == ["2024-11-26"]
    assert result["cache_status"] == "INCOMPLETE"
    assert result["quality"]["missing_sessions"] == ["2024-11-26"]


def test_interior_gap_is_detected_and_incremental_request_backfills_it(tmp_path, security):
    provider = FixtureYahoo(lambda f: f.drop(pd.Timestamp("2024-11-26")))
    cache, report = populate(tmp_path, security, provider)
    assert report["status"] == "PARTIAL_OR_FAILED"
    assert report["results"][0]["quality"]["missing_sessions"] == ["2024-11-26"]
    provider.transform = lambda f: f
    report = history(cache, provider, [security], START, END, overlap_days=0)
    assert provider.calls[-1] == ("SPY", "2024-11-26", END)
    assert report["status"] == "SUCCESS"


def test_incremental_force_refreshes_complete_hit(tmp_path, security):
    provider = FixtureYahoo()
    cache, _ = populate(tmp_path, security, provider)
    report = history(cache, provider, [security], START, END, mode="incremental", overlap_days=1)
    assert provider.calls[-1] == ("SPY", "2024-11-28", END)
    assert report["results"][0]["previous_cache_status"] == "HIT"


@pytest.mark.parametrize("bad", ["duplicate", "conflict", "off-calendar", "missing-value", "bad-range", "wrong-symbol"])
def test_bad_return_is_preserved_but_never_promoted(tmp_path, security, bad):
    def change(f):
        if bad == "duplicate":
            return pd.concat([f, f.iloc[:1]])
        if bad == "conflict":
            return pd.concat([f, f.iloc[:1].assign(Close=999)])
        if bad == "off-calendar":
            f.index = [pd.Timestamp("2024-11-28"), *f.index[1:]]
        if bad == "missing-value":
            f.loc[f.index[0], "Open"] = None
        if bad == "bad-range":
            f.loc[f.index[0], "High"] = 1
        if bad == "wrong-symbol":
            f = pd.concat({"QQQ": f}, axis=1)
        return f
    cache, report = populate(tmp_path, security, FixtureYahoo(change))
    assert report["results"][0]["cache_status"] == "NOT_PROMOTED"
    path = Path(report["results"][0]["snapshot_reference"])
    assert "returned_frame.json" in read_bundle(path)[0]
    assert cache.load_cached_daily("yahoo", security, START, END)["cache_status"] == "MISS"


def test_multisymbol_partial_failure_and_alias_collision(tmp_path, security):
    qqq = replace(security, symbol="QQQ", security_id="synthetic-QQQ", yahoo_symbol="QQQ", ibkr_symbol="QQQ")
    class Provider(FixtureYahoo):
        def fetch_daily(self, s, start, end, output):
            if s.symbol == "SPY":
                raise TimeoutError("do not log secrets /private/path")
            return super().fetch_daily(s, start, end, output)
    cache = HistoryCache(tmp_path / "cache")
    report = history(cache, Provider(), [security, qqq], START, END)
    assert [r["cache_status"] for r in report["results"]] == ["FAILED", "HIT"]
    assert "secrets" not in json.dumps(report)
    assert cache.load_cached_daily("yahoo", qqq, START, END)["cache_status"] == "HIT"
    alias = replace(qqq, symbol="ALIAS", security_id="different-identity")
    with pytest.raises(ValueError, match="collision"):
        history(cache, Provider(), [qqq, alias], START, END)
    assert history(cache, Provider(), [alias], START, END)["results"][0]["errors"][0]["code"] == "CACHE_IDENTITY_MISMATCH"


@pytest.mark.parametrize("member", ["bars.parquet", "metadata.json", "current.json"])
def test_cache_corruption_offline_detection_and_explicit_recovery(tmp_path, security, member):
    provider = FixtureYahoo()
    cache, _ = populate(tmp_path, security, provider)
    entry = cache.entry("yahoo", security)
    version = json.loads((entry / "current.json").read_bytes())["version"]
    target = entry / member if member == "current.json" else entry / "versions" / version / member
    target.write_bytes(b"corrupted")
    assert cache.load_cached_daily("yahoo", security, START, END)["cache_status"] == "CORRUPT"
    assert history(cache, provider, [security], START, END)["status"] == "PARTIAL_OR_FAILED"
    assert len(provider.calls) == 1
    report = history(cache, provider, [security], START, END, mode="full")
    assert report["results"][0]["recovered_corrupt_cache"] is True
    if member != "current.json":
        assert target.read_bytes() == b"corrupted"
    assert cache.load_cached_daily("yahoo", security, START, END)["cache_status"] == "HIT"


def test_cache_lock_and_incomplete_generation_do_not_change_published_version(tmp_path, security):
    cache, _ = populate(tmp_path, security)
    before = cache.load_cached_daily("yahoo", security, START, END)["metadata"]["version"]
    (cache.entry("yahoo", security) / "versions" / ("a" * 32)).mkdir()
    assert cache.load_cached_daily("yahoo", security, START, END)["metadata"]["version"] == before
    with cache.lock("yahoo", security):
        report = history(cache, FixtureYahoo(), [security], START, END, mode="full")
        assert report["results"][0]["cache_status"] == "FAILED"


def test_completed_filter_keeps_native_capture_and_marks_unknown_availability(tmp_path, security):
    provider = YahooDailyProvider(clock=lambda: datetime(2024, 11, 29, 17, tzinfo=UTC))
    # Synthetic capture directly tests the common filter, including 13:00 ET close.
    request = request_record("SPY", START, END)
    request["origin"] = "synthetic"
    output = tmp_path / "snapshot"
    write_snapshot(output, request, {"status": "PARTIAL_RESPONSE", "errors": [],
                                    "started_at": provider.clock().isoformat(), "completed_at": provider.clock().isoformat()}, bars())
    fresh = read_acquisition(output, security)
    assert fresh["excluded_incomplete_sessions"] == ["2024-11-29"]
    assert len(fresh["rows"]) == 3
    assert len(read_snapshot(output)["frame"]) == 4
    assert fresh["historical_availability"] == "unknown"


def test_ibkr_equity_qualification_daily_parameters_identity_and_missing_adjusted_close(tmp_path, security):
    backend = MockIB()
    provider = ib_provider(backend)
    result = provider.fetch_daily(replace(security, con_id=123), START, END, tmp_path / "snapshot")
    assert result["acquisition"]["status"] == "SUCCESS"
    assert backend.disconnected
    request = [c for c in backend.calls if c[0] == "historical"][0]
    assert request[1].secType == "STK" and request[1].conId == 123
    assert request[2] == {"endDateTime": "20241130-00:00:00", "durationStr": "5 D", "barSizeSetting": "1 day",
                          "whatToShow": "TRADES", "useRTH": True, "formatDate": 1, "keepUpToDate": False, "timeout": 30}
    assert all(r["adj_close"] is None for r in result["rows"])
    assert {r["price_basis"] for r in result["rows"]} == {"IBKR_TRADES_SPLIT_ADJUSTED_DOCUMENTED"}
    assert {r["volume_basis"] for r in result["rows"]} == {"IBKR_NATIVE_UNITS_UNVERIFIED"}
    assert result["acquisition"]["qualified_contract"]["conId"] == 123
    assert result["request"]["parameters"]["streaming_market_data_type_observed"].startswith("unknown")
    assert [c[0] for c in backend.calls] == ["connect", "qualify", "historical", "disconnect"]
    with pytest.raises(FileExistsError):
        provider.fetch_daily(security, START, END, tmp_path / "snapshot")
    assert len(backend.calls) == 4


@pytest.mark.parametrize("kind", ["empty", "ambiguous", "symbol", "conid", "currency", "secType", "primaryExchange", "exchange"])
def test_ibkr_rejects_ambiguous_or_changed_identity_before_bars(tmp_path, security, kind):
    contract = SimpleNamespace(conId=123, secType="STK", symbol="SPY", currency="USD", primaryExchange="ARCA", exchange="SMART")
    if kind not in {"empty", "ambiguous"}:
        setattr(contract, {"conid": "conId", "symbol": "symbol", "currency": "currency"}.get(kind, kind),
                456 if kind == "conid" else "WRONG")
    matches = [] if kind == "empty" else [contract] * (2 if kind == "ambiguous" else 1)
    backend = MockIB(qualification=matches)
    fresh = ib_provider(backend).fetch_daily(replace(security, con_id=123), START, END, tmp_path / "snapshot")
    assert fresh["acquisition"]["status"] == "REQUEST_FAILED"
    assert not any(c[0] == "historical" for c in backend.calls)
    assert fresh["acquisition"]["errors"][0]["category"] in {"QUALIFIED_IDENTITY_MISMATCH", "AMBIGUOUS_OR_EMPTY_QUALIFICATION"}


@pytest.mark.parametrize("kind,status", [("empty", "EMPTY_RESPONSE"), ("partial", "PARTIAL_RESPONSE"), ("duplicate", "PARTIAL_RESPONSE")])
def test_ibkr_partial_empty_and_duplicate_responses(tmp_path, security, kind, status):
    frame = bars(adjusted=False)
    if kind == "empty":
        frame = frame.iloc[:0]
    elif kind == "partial":
        frame = frame.drop(pd.Timestamp("2024-11-26"))
    else:
        frame = pd.concat([frame, frame.iloc[:1]])
    fresh = ib_provider(MockIB(frame=frame)).fetch_daily(security, START, END, tmp_path / "snapshot")
    assert fresh["acquisition"]["status"] == status
    assert len(fresh["rows"]) == len(frame)


@pytest.mark.parametrize("category,retries", [("TIMEOUT", 3), ("PACING", 3), ("DATA_PERMISSION", 1), ("NO_DATA", 1)])
def test_ibkr_bounded_retry_permission_errors_and_safe_diagnostics(tmp_path, security, category, retries):
    class Error(Exception):
        code = {"PACING": 162, "DATA_PERMISSION": 354, "NO_DATA": 165}.get(category, None)
    failure = TimeoutError("secret") if category == "TIMEOUT" else Error(f"{category.lower()} secret /private/path")
    backend = MockIB(failures=[failure] * 3)
    virtual = VirtualTime()
    fresh = ib_provider(backend, virtual=virtual).fetch_daily(security, START, END, tmp_path / "snapshot")
    assert len([c for c in backend.calls if c[0] == "historical"]) == retries
    assert "secret" not in json.dumps(fresh["acquisition"])
    assert fresh["acquisition"]["requests"][0]["category"] == category
    assert backend.disconnected


def test_ibkr_event_error_is_not_silent_empty_and_retry_can_succeed(tmp_path, security):
    backend = MockIB(event_errors=[{"code": 162, "category": "PACING"}])
    fresh = ib_provider(backend).fetch_daily(security, START, END, tmp_path / "snapshot")
    assert len(fresh["acquisition"]["requests"]) == 2
    assert fresh["acquisition"]["requests"][0]["category"] == "PACING"
    assert fresh["acquisition"]["status"] == "SUCCESS"
    backend = MockIB(event_errors=[{"code": 354, "category": "DATA_PERMISSION"}])
    fresh = ib_provider(backend).fetch_daily(security, START, END, tmp_path / "denied")
    assert len(fresh["acquisition"]["requests"]) == 1
    assert fresh["rows"] == []


def test_ibkr_completed_session_filter_uses_early_close(tmp_path, security):
    fresh = ib_provider(MockIB(), clock=lambda: datetime(2024, 11, 29, 17, 59, tzinfo=UTC)).fetch_daily(
        security, START, END, tmp_path / "before-close")
    assert fresh["excluded_incomplete_sessions"] == ["2024-11-29"]
    assert fresh["acquisition"]["status"] == "PARTIAL_RESPONSE"
    after = ib_provider(MockIB(), clock=lambda: datetime(2024, 11, 29, 18, 1, tzinfo=UTC)).fetch_daily(
        security, START, END, tmp_path / "after-close")
    assert after["excluded_incomplete_sessions"] == []


def test_ibkr_cache_refuses_qualified_contract_change(tmp_path, security):
    backend = MockIB()
    cache, _ = populate(tmp_path, security, ib_provider(backend))
    contract = SimpleNamespace(conId=456, secType="STK", symbol="SPY", currency="USD", primaryExchange="ARCA", exchange="SMART")
    backend.qualification = [contract]
    report = history(cache, ib_provider(backend), [security], START, END, mode="full")
    assert report["results"][0]["cache_status"] == "FAILED"
    assert cache.load_cached_daily("ibkr", security, START, END)["metadata"]["qualified_contract"]["conId"] == 123


def test_pacing_identical_serial_and_global_windows_are_shared():
    virtual = VirtualTime()
    pacer = Pacer(clock=virtual.now, sleep=virtual.sleep)
    async def exercise():
        await pacer.wait("first")
        await pacer.wait("first")
        assert virtual.value == 15
        for i in range(58):
            await pacer.wait(str(i))
        assert virtual.value == 131
        await pacer.wait("global-61st")
        assert virtual.value == 600
    asyncio.run(exercise())
    assert max(virtual.waits) <= 60


def test_backend_stock_construction_low_level_connect_and_recovery_do_not_sync_accounts(monkeypatch, security):
    calls = []
    class Event:
        def __init__(self):
            self.handlers = []
        def __iadd__(self, fn):
            self.handlers.append(fn)
            return self
        def emit(self, *args):
            for handler in self.handlers:
                handler(*args)
    class IB:
        def __init__(self):
            async def connect(*args, **kwargs):
                calls.append(("handshake", args, kwargs))
            self.client = SimpleNamespace(connectAsync=connect)
            self.wrapper = SimpleNamespace()
            self.errorEvent = Event()
        async def reqContractDetailsAsync(self, contract):
            calls.append(("contract", contract))
            return [SimpleNamespace(contract=contract)]
        async def reqHistoricalDataAsync(self, contract, **params):
            import logging
            logging.getLogger("ib_async.ib").warning("reqHistoricalData: Timeout secret/path")
            return []
        def disconnect(self):
            calls.append(("disconnect",))
        def __getattr__(self, name):
            raise AssertionError(f"forbidden operation: {name}")
    def stock(**kwargs):
        calls.append(("stock", kwargs))
        return SimpleNamespace(**kwargs)
    original = importlib.metadata.version
    monkeypatch.setattr(importlib.metadata, "version", lambda n: "2.1.0" if n == "ib_async" else original(n))
    monkeypatch.setitem(sys.modules, "ib_async", SimpleNamespace(IB=IB, Stock=stock))
    backend = make_backend()
    async def exercise():
        await backend.connect("127.0.0.1", 7497, 17)
        await backend.qualify(replace(security, con_id=123))
        backend.ib._onError(0, 1102, "reconnected", None)
        await backend.historical(SimpleNamespace(), {})
        backend.ib.errorEvent.emit(1, 354, "secret account/subscription", None)
        backend.disconnect()
    asyncio.run(exercise())
    assert calls[0] == ("handshake", ("127.0.0.1", 7497, 17), {"timeout": 10})
    assert calls[1] == ("stock", {"symbol": "SPY", "exchange": "SMART", "currency": "USD", "primaryExchange": "ARCA", "conId": 123})
    assert backend.ib.RaiseRequestErrors is True
    assert backend.errors == [{"code": None, "category": "TIMEOUT"}, {"code": 354, "category": "DATA_PERMISSION"}]
    assert "secret" not in json.dumps(backend.errors)


@pytest.mark.parametrize("code,message,category", [(162, "No market data permissions", "DATA_PERMISSION"),
                                                   (162, "pacing violation", "PACING"), (162, "query returned no data", "NO_DATA"),
                                                   (2106, "farm connected", "INFORMATION"), (1102, "restored", "CONNECTION")])
def test_ibkr_error_classification(code, message, category):
    assert classify(code, message) == category


def test_ibkr_operational_configuration_is_explicit_and_bounded():
    for kwargs in ({}, {"port": 7497, "client_id": 0}, {"port": 7497, "client_id": 1, "host": "example.com"},
                   {"port": 7497, "client_id": 1, "max_attempts": 4},
                   {"port": 7497, "client_id": 1, "origin": "synthetic"}):
        with pytest.raises(ValueError):
            IBKRDailyProvider(**kwargs)
    with pytest.raises(ValueError):
        interval("2000-01-01", "2024-01-01")


def test_frozen_dataset_is_immutable_and_independent_of_refresh_and_source_removal(tmp_path, security):
    provider = FixtureYahoo()
    cache, _ = populate(tmp_path, security, provider)
    target = tmp_path / "dataset"
    freeze(cache, "yahoo", [security], START, END, target, clock=lambda: FIXED)
    before, hashes = read_bundle(target)
    provider.transform = lambda f: f.assign(Close=102)
    history(cache, provider, [security], START, END, mode="full")
    assert read_bundle(target) == (before, hashes)
    with pytest.raises(FileExistsError):
        freeze(cache, "yahoo", [security], START, END, target)
    shutil.rmtree(cache.root)
    dataset = load_research_dataset(target)
    assert all(row["close"] == "101" for row in dataset.bars("SPY"))
    rows = dataset.bars("SPY")
    rows[0]["close"] = "999"
    assert dataset.bars("SPY")[0]["close"] == "101"
    assert dataset.manifest["purpose"] == "offline_technical_research_not_execution_admission"


def test_deterministic_freeze_and_canonical_hashes(tmp_path, security):
    cache, _ = populate(tmp_path, security)
    for name in ("one", "two"):
        freeze(cache, "yahoo", [security], START, END, tmp_path / name, clock=lambda: FIXED)
    assert read_bundle(tmp_path / "one") == read_bundle(tmp_path / "two")
    loaded = cache.load_cached_daily("yahoo", security, START, END)
    assert loaded["metadata"]["rows_sha256"] == digest(encode(loaded["rows"]))
    first_source = next(iter(loaded["metadata"]["sources"].values()))
    assert read_acquisition(first_source, security)["rows"] == read_acquisition(first_source, security)["rows"]


def test_freeze_gaps_fail_closed_and_explicit_diagnostic_dataset_blocks_indicators(tmp_path, security):
    cache, _ = populate(tmp_path, security, FixtureYahoo(lambda f: f.iloc[[0, 2, 3]]))
    with pytest.raises(ValueError, match="missing"):
        freeze(cache, "yahoo", [security], START, END, tmp_path / "rejected")
    assert not (tmp_path / "rejected").exists()
    freeze(cache, "yahoo", [security], START, END, tmp_path / "diagnostic", allow_incomplete=True)
    dataset = load_research_dataset(tmp_path / "diagnostic")
    assert len(dataset.bars("SPY")) == 3
    assert dataset.quality("SPY")["missing_sessions"] == ["2024-11-26"]
    with pytest.raises(ValueError, match="no forward fill"):
        dataset.indicators("SPY")


def test_frozen_integrity_and_missing_source_are_detected(tmp_path, security):
    cache, _ = populate(tmp_path, security)
    source = next(iter(cache.load_cached_daily("yahoo", security, START, END)["metadata"]["sources"].values()))
    freeze(cache, "yahoo", [security], START, END, tmp_path / "dataset")
    file = next((tmp_path / "dataset").glob("bars-*.json"))
    file.write_bytes(file.read_bytes().replace(b'"101"', b'"999"'))
    with pytest.raises(ValueError, match="hash mismatch"):
        load_research_dataset(tmp_path / "dataset")
    shutil.rmtree(source)
    with pytest.raises(OSError):
        freeze(cache, "yahoo", [security], START, END, tmp_path / "missing-source")
    assert not (tmp_path / "missing-source").exists()


def test_calendar_holidays_exceptional_closure_dst_early_close_listing_boundaries(security):
    early = reconcile([], security, START, END)
    sessions = early["calendar"]["sessions"]
    assert "2024-11-28" not in [r["session_date"] for r in sessions]
    assert sessions[-1]["closes_at"].endswith("18:00:00+00:00")
    closure = reconcile([], security, "2025-01-08", "2025-01-10")
    assert "2025-01-09" not in closure["missing_sessions"]
    dst = reconcile([], security, "2024-03-08", "2024-03-11")["calendar"]["sessions"]
    assert "14:30" in dst[0]["opens_at"] and "13:30" in dst[1]["opens_at"]
    listed = replace(security, first_session="2024-11-26", last_session="2024-11-27", listing_reference="synthetic:listing")
    rows = [{"session_date": day} for day in ("2024-11-26", "2024-11-27")]
    assert reconcile(rows, listed, START, END)["status"] == "PASS"
    assert reconcile(rows, security, START, END)["status"] == "FAIL"
    assert reconcile(rows, listed, START, END)["listing_venue"] == "ARCX"


@pytest.mark.parametrize("change", ["identical", "OHLC", "volume", "zero", "missing", "adjusted"])
def test_provider_comparison_reports_values_ratios_and_missing_sessions(tmp_path, security, change):
    yf, ib = bars(), bars(adjusted=False)
    if change == "OHLC":
        ib["High"] = 103
        ib["Close"] = 102
    if change == "volume":
        ib["Volume"] = 1200
    if change == "zero":
        yf["Volume"] = 0
        ib["Volume"] = 1
    if change == "missing":
        ib = ib.iloc[[0, 2, 3]]
    if change == "adjusted":
        yf["Adj Close"] = 50.5
    a, b = datasets(tmp_path, security, yf, ib, allow_incomplete=change == "missing")
    report = compare_providers(a, b, "SPY", START, END)
    assert report["interpretation"] == "DIAGNOSTIC_ONLY_BASIS_UNRESOLVED"
    assert report["source_selection"] == "NONE" and report["transformation"] == "NONE"
    if change == "identical":
        assert all(r["absolute_difference"] in {"0", None} for r in report["differences"])
    if change == "OHLC":
        row = next(r for r in report["differences"] if r["field"] == "close")
        assert row["absolute_difference"] == "1" and row["exceeds_tolerance"] is True
        assert Decimal(row["ratio_ibkr_to_yahoo"]) == Decimal(102) / Decimal(101)
    if change == "volume":
        assert next(r for r in report["differences"] if r["field"] == "volume")["percent_difference"] == "20.0"
    if change == "zero":
        row = next(r for r in report["differences"] if r["field"] == "volume")
        assert row["percent_difference"] is None and row["ratio_ibkr_to_yahoo"] is None
        assert row["exceeds_tolerance"] is True
    if change == "missing":
        assert report["missing_sessions"]["ibkr"] == ["2024-11-26"]
    if change == "adjusted":
        assert len(report["adjustment_diagnostics"]) == 4
    assert all(r["status"] == "MISSING_OR_INVALID" for r in report["differences"] if r["field"] == "adj_close")


def test_comparison_tolerances_identity_and_interval_validation(tmp_path, security):
    a, b = datasets(tmp_path, security, ib_frame=bars(adjusted=False).assign(Close=102))
    report = compare_providers(a, b, "SPY", START, END, price_absolute="2")
    assert not any(r["exceeds_tolerance"] for r in report["differences"])
    report = compare_providers(a, b, "SPY", START, END, price_percent="2")
    assert not any(r["exceeds_tolerance"] for r in report["differences"])
    for kw in ({"price_absolute": "-1"}, {"volume_percent": "NaN"}, {"price_percent": "bad-number"}):
        with pytest.raises(ValueError):
            compare_providers(a, b, "SPY", START, END, **kw)
    with pytest.raises(ValueError, match="interval"):
        compare_providers(a, b, "SPY", "2024-11-01", END)
    b._manifest["securities"]["SPY"]["security"]["security_id"] = "other-security"
    with pytest.raises(ValueError, match="different identified"):
        compare_providers(a, b, "SPY", START, END)


def test_unknown_or_different_bases_are_not_interchangeable(tmp_path, security):
    a, b = datasets(tmp_path, security)
    for dataset in (a, b):
        dataset._manifest["securities"]["SPY"]["basis"] = {"price_basis": "UNKNOWN", "volume_basis": "UNKNOWN", "verified": True}
    assert compare_providers(a, b, "SPY", START, END)["interpretation"] == "DIAGNOSTIC_ONLY_BASIS_UNRESOLVED"


def test_cli_offline_history_freeze_compare_and_permission_boundary(tmp_path, security, capsys):
    mapping = tmp_path / "mappings.json"
    mapping.write_bytes(encode([security.record()]))
    a, b = datasets(tmp_path, security)
    base = ["--symbols", "SPY", "--mappings", str(mapping), "--start", START, "--end", END]
    assert main(["data", "history", "--provider", "yahoo", *base, "--cache", str(tmp_path / "yahoo-cache"), "--mode", "offline"]) == 0
    assert main(["data", "freeze", "--provider", "yahoo", *base, "--cache", str(tmp_path / "yahoo-cache"), "--output", str(tmp_path / "cli-dataset")]) == 0
    assert main(["data", "compare-providers", "--symbol", "SPY", "--start", START, "--end", END,
                 "--yahoo-dataset", str(tmp_path / "yahoo-dataset"), "--ibkr-dataset", str(tmp_path / "ibkr-dataset"),
                 "--output", str(tmp_path / "comparison")]) == 0
    assert main(["data", "history", "--provider", "ibkr", *base]) == 2
    assert "permission-reference" in capsys.readouterr().err


def test_full_synthetic_demo_multisymbol_indicators_and_fresh_process_offline_loading(tmp_path):
    script = Path(__file__).resolve().parents[1] / "scripts/make_historical_equity_example.py"
    demo = runpy.run_path(str(script))["demonstrate"]
    summary = demo(tmp_path / "example")
    assert summary["origin"] == "SYNTHETIC_ONLY" and summary["live_requests"] == 0
    spy = summary["indicators"]["yahoo"]["SPY"]
    assert spy["sma50"] == 157.125 and spy["sma200"] == 138.375 and spy["atr14"] == 2
    dataset = load_research_dataset(tmp_path / "example/yahoo-dataset")
    indicator = dataset.indicators("SPY")["rows"]
    assert all(r["sma50"] is None for r in indicator[:49])
    assert indicator[49]["sma50"] == 106.625
    assert all(r["sma200"] is None for r in indicator[:199])
    assert indicator[199]["sma200"] == 125.375
    assert all(r["atr14"] is None for r in indicator[:14])
    assert indicator[14]["atr14"] == 2
    assert indicator[0]["ema50"] == 100.5
    assert len(dataset.manifest["securities"]) == 3
    report = json.loads((tmp_path / "example/comparison-AAPL/comparison.json").read_bytes())
    assert report["interpretation"] == "DIAGNOSTIC_ONLY_BASIS_UNRESOLVED"
    close = next(r for r in report["differences"] if r["field"] == "close")
    assert close["ratio_ibkr_to_yahoo"] == "0.5" and close["percent_difference"] == "50.0"
    shutil.rmtree(tmp_path / "example/yahoo-cache")
    subprocess.run([sys.executable, "-c", """
import sys, socket
class Deny:
    def find_spec(self, name, *args):
        if name.split('.')[0] in {'ib_async', 'yfinance', 'pandas', 'numpy', 'pyarrow', 'exchange_calendars'}:
            raise AssertionError('unexpected optional import: ' + name)
sys.meta_path.insert(0, Deny())
socket.create_connection = lambda *a, **k: (_ for _ in ()).throw(AssertionError('network'))
from equity_research.history import load_research_dataset
dataset = load_research_dataset(sys.argv[1])
assert dataset.indicators('SPY')['rows'][-1]['sma200'] == 138.375
assert dataset.relative_strength('SPY', 'QQQ')['rows'][-1]['ratio'] == '1'
""", str(tmp_path / "example/yahoo-dataset")], check=True, timeout=30,
        env={**__import__("os").environ, "PYTHONPATH": str(script.parents[1] / "src")})
    with pytest.raises(FileExistsError):
        demo(tmp_path / "example")


def test_ibkr_chunks_explicit_native_values_and_daily_date_normalization(tmp_path, security):
    class Backend(MockIB):
        async def historical(self, contract, params):
            self.calls.append(("historical", contract, params))
            last = datetime.strptime(params["endDateTime"], "%Y%m%d-%H:%M:%S").date() - timedelta(days=1)
            first = last - timedelta(days=int(params["durationStr"].split()[0]) - 1)
            return [SimpleNamespace(date=d.strftime("%Y%m%d"), open=Decimal("100.125"), high=Decimal("102"),
                                    low=Decimal("98"), close=Decimal("101.25"), volume=Decimal("123.5"),
                                    average=Decimal("100.75"), barCount=9)
                    for d in [date.fromisoformat(s["session_date"]) for s in schedule(first.isoformat(), last.isoformat())["sessions"]]]
    backend = Backend()
    path = tmp_path / "snapshot"
    fresh = ib_provider(backend).fetch_daily(security, "2024-10-01", END, path)
    requests = fresh["acquisition"]["requests"]
    assert len(requests) == 2
    assert requests[0]["start"] == "2024-10-01" and requests[0]["end"] == "2024-10-30"
    assert requests[1]["start"] == "2024-10-31" and requests[1]["end"] == END
    assert fresh["rows"][0]["open"] == "100.125"
    assert fresh["rows"][0]["volume"] == "123.5"  # No lot/share conversion or rounding.
    native = json.loads(read_bundle(path)[0]["returned_bars.json"])["bars"][0]["fields"]
    assert native["date"] == ["value", "20241001"]
    assert native["average"] == ["decimal", "100.75"] and native["barCount"] == ["value", 9]
    assert any(i["code"] == "NONINTEGRAL_VOLUME" for i in fresh["issues"])


def test_ibkr_connect_failure_and_missing_optional_client_are_recorded(tmp_path, security, monkeypatch):
    class Backend(MockIB):
        async def connect(self, *args):
            raise ConnectionError("secret/path")
    backend = Backend()
    fresh = ib_provider(backend).fetch_daily(security, START, END, tmp_path / "connection")
    assert fresh["acquisition"]["status"] == "REQUEST_FAILED"
    assert backend.disconnected
    assert "secret" not in json.dumps(fresh["acquisition"])
    original = importlib.metadata.version
    def missing(name):
        if name == "ib_async":
            raise importlib.metadata.PackageNotFoundError(name)
        return original(name)
    monkeypatch.setattr(importlib.metadata, "version", missing)
    fresh = IBKRDailyProvider(port=7497, client_id=17, clock=lambda: FIXED).fetch_daily(
        security, START, END, tmp_path / "no-client")
    assert fresh["acquisition"]["status"] == "REQUEST_FAILED"
    assert fresh["acquisition"]["client_version"] is None
    assert fresh["acquisition"]["errors"][0]["exception_type"] == "PackageNotFoundError"


def test_failed_refresh_keeps_published_cache_and_failure_snapshot(tmp_path, security, monkeypatch):
    provider = YahooDailyProvider(clock=lambda: FIXED)
    original = importlib.metadata.version
    monkeypatch.setattr(importlib.metadata, "version", lambda n: "0.2.66" if n == "yfinance" else original(n))
    monkeypatch.setitem(sys.modules, "yfinance", SimpleNamespace(download=lambda **kw: bars()))
    cache, _ = populate(tmp_path, security, provider)
    version = cache.load_cached_daily("yahoo", security, START, END)["metadata"]["version"]
    def failed(**kw):
        raise TimeoutError("secret")
    monkeypatch.setitem(sys.modules, "yfinance", SimpleNamespace(download=failed))
    report = history(cache, provider, [security], START, END, mode="full")
    assert report["results"][0]["acquisition_status"] == "REQUEST_FAILED"
    assert report["results"][0]["cache_status"] == "NOT_PROMOTED"
    assert read_snapshot(Path(report["results"][0]["snapshot_reference"]))["acquisition"]["status"] == "REQUEST_FAILED"
    assert cache.load_cached_daily("yahoo", security, START, END)["metadata"]["version"] == version


def test_yahoo_class_alias_is_explicit_and_unrelated_symbol_is_rejected(tmp_path, security, monkeypatch):
    original = importlib.metadata.version
    monkeypatch.setattr(importlib.metadata, "version", lambda n: "0.2.66" if n == "yfinance" else original(n))
    calls = []
    monkeypatch.setitem(sys.modules, "yfinance", SimpleNamespace(download=lambda **kw: calls.append(kw) or pd.concat({"BRK-B": bars()}, axis=1)))
    mapped = replace(security, symbol="BRK.B", yahoo_symbol="BRK-B", ibkr_symbol="BRK B")
    provider = YahooDailyProvider(clock=lambda: FIXED)
    fresh = provider.fetch_daily(mapped, START, END, tmp_path / "class")
    assert fresh["request"]["research_symbol"] == "BRK.B"
    assert fresh["request"]["provider_symbol"] == "BRK-B"
    assert calls[0]["tickers"] == ["BRK-B"]
    with pytest.raises(ValueError, match="substitution"):
        provider.fetch_daily(replace(security, yahoo_symbol="QQQ"), START, END, tmp_path / "wrong")
    assert not (tmp_path / "wrong").exists() and len(calls) == 1
    with pytest.raises(ValueError, match="collision"):
        select_securities([mapped.record(), replace(mapped, symbol="BRK-B", security_id="other").record()], ["BRK.B", "BRK-B"], "yahoo")


def test_yahoo_missing_adjusted_close_stays_missing_and_actions_remain_unknown(tmp_path, security):
    provider = FixtureYahoo(lambda f: f.drop(columns="Adj Close").assign(Dividends=[0, 0, 1, 0]))
    cache, _ = populate(tmp_path, security, provider)
    freeze(cache, "yahoo", [security], START, END, tmp_path / "dataset", clock=lambda: FIXED)
    dataset = load_research_dataset(tmp_path / "dataset")
    assert all(r["adj_close"] is None for r in dataset.bars("SPY"))
    quality = dataset.quality("SPY")
    assert quality["provider_events"][0]["type"] == "dividend"
    assert quality["corporate_action_completeness"] == "unknown"
    assert quality["execution_export"] == "NOT_EVALUATED_USE_EXISTING_EXPORT_GATES"
    assert dataset.manifest["synthetic_only"] is True


def test_gap_aware_atr_uses_shared_math_without_future_values(tmp_path, security):
    start, end = "2024-10-01", "2024-10-21"  # Fifteen sessions, fourteen prior-close ranges.
    def gap(f):
        f.iloc[-1, f.columns.get_indexer(["Open", "High", "Low", "Close", "Adj Close"])] = [110, 112, 108, 111, 111]
        return f
    cache, _ = populate(tmp_path, security, FixtureYahoo(gap), start=start, end=end)
    freeze(cache, "yahoo", [security], start, end, tmp_path / "dataset", clock=lambda: FIXED)
    indicator = load_research_dataset(tmp_path / "dataset").indicators("SPY")["rows"]
    assert len(indicator) == 15
    assert indicator[-1]["atr14"] == 4.5  # (13 * 4 + 11) / 14, not Wilder smoothing.
    assert indicator[0]["ema50"] == 101
    assert all(row["atr14"] is None for row in indicator[:-1])


def test_listing_boundary_requires_reference_and_actual_session(security):
    with pytest.raises(ValueError, match="reference"):
        replace(security, first_session="2024-11-26")
    with pytest.raises(ValueError, match="actual"):
        reconcile([], replace(security, first_session="2024-11-28", listing_reference="synthetic"), START, END)


def test_misrouted_provider_capture_cannot_populate_another_provider_cache(tmp_path, security):
    cache = HistoryCache(tmp_path / "cache")
    fresh = ib_provider(MockIB()).fetch_daily(security, START, END, tmp_path / "ibkr-snapshot")
    with pytest.raises(ValueError, match="source provider"):
        cache.update("yahoo", security, START, END, fresh)
    assert cache.load_cached_daily("yahoo", security, START, END)["cache_status"] == "MISS"


def test_ibkr_aapl_overreturned_bars_are_captured_but_frame_is_explicitly_bounded(tmp_path):
    aapl = Security("AAPL", "synthetic-AAPL", "synthetic reviewed common stock", "AAPL", "AAPL", "NASDAQ", "XNAS")
    native = bars("2024-11-21", "2024-12-02", adjusted=False)
    provider = ib_provider(MockIB(frame=native))
    result = provider.fetch_daily(aapl, START, END, tmp_path / "snapshot")
    acq = result["acquisition"]
    assert acq["qualified_contract"]["primaryExchange"] == "NASDAQ"
    assert acq["qualified_contract"]["symbol"] == "AAPL"
    assert acq["status"] == "SUCCESS"
    assert [r["session_date"] for r in result["rows"]] == [r["session_date"] for r in schedule(START, END)["sessions"]]
    assert acq["native_row_indices"] == [2, 3, 4, 5]
    assert [r["native_row"] for r in acq["excluded_native_rows"]] == [0, 1, 6]
    files, hashes = read_bundle(tmp_path / "snapshot")
    assert len(json.loads(files["returned_bars.json"])["bars"]) == 7
    assert [r["source_row"]["native_row"] for r in result["rows"]] == [2, 3, 4, 5]
    assert all(r["source_row"]["native_sha256"] == hashes["files"]["returned_bars.json"] for r in result["rows"])


def test_ibkr_overreturned_chunks_keep_only_each_requested_interval(tmp_path, security):
    class ChunkIB(MockIB):
        async def historical(self, contract, params):
            self.calls.append(("historical", contract, params))
            # Deliberately return the whole interval on every chunk. Interior
            # duplicates from distinct lookbacks must not contaminate the frame.
            return [SimpleNamespace(date=d.date(), **{k.lower(): v for k, v in row.items()})
                    for d, row in self.frame.iterrows()]
    frame = bars("2024-10-01", "2024-12-02", adjusted=False)
    result = ib_provider(ChunkIB(frame=frame)).fetch_daily(security, "2024-10-01", "2024-12-02", tmp_path / "capture")
    assert len(result["acquisition"]["requests"]) == 3
    assert result["acquisition"]["status"] == "SUCCESS"
    assert len(result["rows"]) == len(frame)
    assert len(set(r["session_date"] for r in result["rows"])) == len(frame)
    assert len(result["acquisition"]["excluded_native_rows"]) == 2 * len(frame)
