"""Daily-depth tests are entirely offline, including the broker boundary."""

import asyncio
from copy import deepcopy
from datetime import UTC, date, datetime, timedelta
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from equity_research.cli import main
from equity_research.history.contracts import Security
from equity_research.history.depth import DepthAudit, config_record
from equity_research.history.depth_store import Journal, freeze_report, summarize
from equity_research.ingestion.calendar import schedule
from equity_research.ingestion.storage import read_bundle
from equity_research.providers.ibkr import Pacer
from test_history import VirtualTime

NOW = datetime(2024, 12, 7, 12, tzinfo=UTC)
SECURITY = Security("SPY", "synthetic:SPY", "synthetic:depth-test", "SPY", "SPY", "ARCA", "ARCX")


def config(**changes):
    return {"schema_version": "ibkr_depth_config_v1", "start": "2024-11-01", "end": "2024-12-06",
        "window_days": 14, "overlap_days": 2, "max_attempts": 2,
        "instruments": [{"kind": "market_etf", "security": SECURITY.record()}], **changes}


class BrokerError(Exception):
    def __init__(self, code, text="private account secret must not be stored"):
        self.code = code
        super().__init__(text)


class Fake:
    client_version = "synthetic-depth-v1"

    def __init__(self, *, failures=(), head="2020-01-02", transform=lambda bars: bars):
        self.errors, self.calls, self.failures = [], [], list(failures)
        self.head, self.transform = head, transform
        self.con_id, self.ambiguous, self.disconnected = 123, False, False

    async def connect(self, host, port, client_id):
        self.calls.append(("connect", host, port, client_id))

    async def qualify(self, security):
        self.calls.append(("qualify", security.symbol))
        result = SimpleNamespace(conId=self.con_id, symbol=security.ibkr_symbol, secType="STK", exchange="SMART",
            primaryExchange=security.primary_exchange, currency="USD", localSymbol=security.ibkr_symbol, tradingClass=security.ibkr_symbol)
        return [result, result] if self.ambiguous else [result]

    async def head_timestamp(self, contract):
        self.calls.append(("head", contract.conId))
        if self.head is None:
            raise TimeoutError("private head error")
        return datetime.fromisoformat(self.head + "T14:30:00+00:00")

    async def historical(self, contract, params):
        self.calls.append(("historical", contract.conId, params))
        if self.failures:
            exc = self.failures.pop(0)
            if exc is not None:
                raise exc
        end = datetime.strptime(params["endDateTime"], "%Y%m%d-%H:%M:%S").date() - timedelta(days=1)
        count, unit = params["durationStr"].split()
        start = end - timedelta(days=int(count) * (366 if unit == "Y" else 1) - 1)
        rows = [SimpleNamespace(date=date.fromisoformat(s["session_date"]), open=100, high=102, low=99,
                close=101, volume=1000) for s in schedule(start.isoformat(), end.isoformat())["sessions"]
                if self.head is None or s["session_date"] >= self.head]
        return self.transform(rows)

    def disconnect(self):
        self.calls.append(("disconnect",))
        self.disconnected = True


def auditor(fake, *, virtual=None, clock=lambda: NOW):
    virtual = virtual or VirtualTime()
    return DepthAudit(port=7496, client_id=91, backend_factory=lambda: fake, origin="synthetic", clock=clock,
        pacer=Pacer(clock=virtual.now, sleep=virtual.sleep), sleep=virtual.sleep)


def report(root):
    return summarize(Journal(root))[0][0]


def test_backward_overlapping_windows_deduplicate_and_exclude_holiday(tmp_path):
    fake = Fake()
    result = auditor(fake).run(config(), tmp_path / "audit")
    r = result["instruments"][0]
    assert r["status"] == "complete" and r["actual_earliest_bar"] == "2024-11-01"
    assert r["actual_latest_bar"] == "2024-12-06" and not r["missing_sessions"]
    assert r["overlaps"] and all(v["classification"] == "IDENTICAL" for v in r["overlaps"])
    params = [c[2] for c in fake.calls if c[0] == "historical"]
    assert [p["endDateTime"] for p in params] == sorted([p["endDateTime"] for p in params], reverse=True)
    assert all(p["whatToShow"] == "TRADES" and p["useRTH"] and p["barSizeSetting"] == "1 day" and not p["keepUpToDate"] for p in params)
    assert r["observed_sessions"] == len(schedule("2024-11-01", "2024-12-06")["sessions"])
    assert "2024-11-28" not in r["all_missing_sessions"]  # Thanksgiving.
    assert fake.disconnected and all(c[0] in {"connect", "qualify", "head", "historical", "disconnect"} for c in fake.calls)


def test_internal_gap_truncated_response_and_conflicting_overlap(tmp_path):
    def missing(rows):
        return [r for r in rows if r.date.isoformat() != "2024-11-20"]
    auditor(Fake(transform=missing)).run(config(), tmp_path / "gap")
    assert report(tmp_path / "gap")["internal_gaps"] == ["2024-11-20"]
    assert report(tmp_path / "gap")["status"] == "partial"
    auditor(Fake(transform=lambda rows: rows[-3:])).run(config(), tmp_path / "truncated")
    assert report(tmp_path / "truncated")["status"] == "complete"  # Cursor follows actual first return, not requested start.
    counter = 0
    def revised(rows):
        nonlocal counter
        counter += 1
        return [SimpleNamespace(**{**vars(r), "close": 100 if counter > 1 else 101}) for r in rows]
    auditor(Fake(transform=revised)).run(config(), tmp_path / "revision")
    r = report(tmp_path / "revision")
    assert r["conflicting_sessions"] and r["status"] == "partial"
    assert any(v["classification"] == "CONFLICT" for v in r["overlaps"])


@pytest.mark.parametrize("transform", [lambda rows: rows[::-1], lambda rows: rows + rows[:1],
    lambda rows: [SimpleNamespace(**{**vars(r), "high": 1}) for r in rows]])
def test_order_duplicate_and_numeric_failures_remain_visible(tmp_path, transform):
    auditor(Fake(transform=transform)).run(config(), tmp_path / "audit")
    r = report(tmp_path / "audit")
    assert r["status"] == "partial" and any(v["status"] == "FAIL" for v in r["issues"])


def test_empty_windows_are_retried_and_never_prove_exhaustion(tmp_path):
    fake, virtual = Fake(transform=lambda rows: []), VirtualTime()
    result = auditor(fake, virtual=virtual).run(config(), tmp_path / "audit")
    r = result["instruments"][0]
    assert r["status"] == "inconclusive" and r["exhaustion_evidence"] is None
    assert r["request_status_counts"]["EMPTY_RESPONSE"] == 6
    assert len([c for c in fake.calls if c[0] == "historical"]) == 6
    assert sum(virtual.waits) >= 45 and max(virtual.waits) <= 60


@pytest.mark.parametrize("exc,status,attempts", [(BrokerError(162), "failed", 1),
    (BrokerError(354), "failed", 1), (TimeoutError(), "failed", 2),
    (BrokerError(165), "inconclusive", 6)])
def test_failures_and_no_data_are_not_historical_exhaustion(tmp_path, exc, status, attempts):
    fake = Fake(failures=[exc] * 20)
    auditor(fake).run(config(), tmp_path / "audit")
    r = report(tmp_path / "audit")
    assert r["status"] == status and r["exhaustion_evidence"] is None
    assert len([c for c in fake.calls if c[0] == "historical"]) == attempts
    serialized = b"".join(c for i in Journal(tmp_path / "audit").events for c in i["files"].values())
    assert b"private" not in serialized and b"secret" not in serialized


def test_exhaustion_requires_head_and_matching_observed_complete_boundary(tmp_path):
    auditor(Fake(head="2024-11-12")).run(config(), tmp_path / "head")
    r = report(tmp_path / "head")
    assert r["status"] == "exhausted" and r["actual_earliest_bar"] == "2024-11-12"
    assert r["exhaustion_evidence"] == "HEAD_TIMESTAMP_AND_MATCHING_OBSERVED_BOUNDARY"
    auditor(Fake(head="2024-11-12")).run(config(head_timestamp=False), tmp_path / "no-head")
    assert report(tmp_path / "no-head")["status"] == "partial"
    assert report(tmp_path / "no-head")["exhaustion_evidence"] is None


def test_head_failure_does_not_prevent_successful_bar_audit(tmp_path):
    auditor(Fake(head=None)).run(config(), tmp_path / "audit")
    assert report(tmp_path / "audit")["status"] == "complete"
    assert report(tmp_path / "audit")["provider_head_timestamp"] is None


def test_resource_checkpoint_resume_is_immutable_and_rechecks_contract(tmp_path):
    root = tmp_path / "audit"
    settings = config(max_windows_per_instrument=1)
    fake = Fake()
    auditor(fake).run(settings, root)
    before = {i["path"]: i["files"] for i in Journal(root).events}
    assert report(root)["status"] == "partial"
    for _ in range(5):
        auditor(Fake()).run(settings, root, resume=True)
    assert report(root)["status"] == "complete"
    assert all(i["files"] == before[i["path"]] for i in Journal(root).events if i["path"] in before)
    with pytest.raises(FileExistsError):
        auditor(Fake()).run(settings, root)
    with pytest.raises(ValueError, match="differs"):
        auditor(Fake()).run(config(), root, resume=True)


def test_ambiguous_or_changed_contract_never_requests_bars(tmp_path):
    fake = Fake(); fake.ambiguous = True
    auditor(fake).run(config(), tmp_path / "ambiguous")
    assert report(tmp_path / "ambiguous")["status"] == "failed"
    assert not any(c[0] == "historical" for c in fake.calls)
    settings = config(max_windows_per_instrument=1)
    auditor(Fake()).run(settings, tmp_path / "changed")
    fake = Fake(); fake.con_id = 456
    auditor(fake).run(settings, tmp_path / "changed", resume=True)
    assert report(tmp_path / "changed")["status"] == "partial"
    assert not any(c[0] == "historical" for c in fake.calls)


def test_cancellation_keeps_checkpoint_and_disconnects_then_resume(tmp_path):
    fake = Fake(failures=[asyncio.CancelledError()])
    result = auditor(fake).run(config(), tmp_path / "audit")
    assert result["status"] == "CANCELLED" and fake.disconnected
    assert report(tmp_path / "audit")["status"] == "inconclusive"
    assert any(i["event"].get("status") == "CANCELLED" for i in Journal(tmp_path / "audit").events)
    auditor(Fake()).run(config(), tmp_path / "audit", resume=True)
    assert report(tmp_path / "audit")["status"] == "complete"


def test_request_and_time_limits_are_checkpointed_not_exhaustion(tmp_path):
    result = auditor(Fake()).run(config(max_requests=2), tmp_path / "requests")
    assert result["status"] == "RESOURCE_LIMIT"
    assert report(tmp_path / "requests")["status"] == "inconclusive"
    result = auditor(Fake()).run(config(max_runtime_seconds=1), tmp_path / "time")
    assert result["status"] == "RESOURCE_LIMIT"


def test_completed_session_early_close_and_multi_year_parameters(tmp_path):
    now = datetime(2024, 11, 29, 17, 59, tzinfo=UTC)
    auditor(Fake(), clock=lambda: now).run(config(end="2024-11-29"), tmp_path / "early")
    assert Journal(tmp_path / "early").plan["end"] == "2024-11-27"
    fake = Fake()
    auditor(fake).run(config(start="2020-01-01", window_days=1825), tmp_path / "years")
    assert next(c[2]["durationStr"] for c in fake.calls if c[0] == "historical") == "5 Y"


def test_offline_report_recomputes_from_frozen_frames_and_is_deterministic(tmp_path, monkeypatch):
    auditor(Fake()).run(config(), tmp_path / "audit")
    import equity_research.providers.ibkr_depth as backend
    monkeypatch.setattr(backend, "make_depth_backend", lambda: pytest.fail("offline report connected"))
    assert main(["data", "ibkr-depth-report", "--audit", str(tmp_path / "audit"), "--output", str(tmp_path / "r1")]) == 0
    first = read_bundle(tmp_path / "r1")
    freeze_report(tmp_path / "audit", tmp_path / "r2")
    assert first == read_bundle(tmp_path / "r2")
    freeze_report(tmp_path / "r1", tmp_path / "replayed")
    assert first == read_bundle(tmp_path / "replayed")
    assert any(k.endswith("returned_bars.json") for k in first[0])
    with pytest.raises(FileExistsError):
        freeze_report(tmp_path / "audit", tmp_path / "r1")
    entry = next(i for i in Journal(tmp_path / "audit").events if "returned_frame.json" in i["files"])
    path = tmp_path / "audit/events" / entry["path"] / "returned_frame.json"
    path.write_bytes(b"{}")
    with pytest.raises(ValueError, match="hash mismatch"):
        freeze_report(tmp_path / "audit", tmp_path / "bad")


def test_operator_guards_and_config_validation_precede_connection(tmp_path):
    calls = []
    audit = DepthAudit(port=7496, client_id=91, backend_factory=lambda: calls.append("connect"))
    with pytest.raises(ValueError, match="explicit"):
        audit.run(config(), tmp_path / "audit")
    assert not calls and not (tmp_path / "audit").exists()
    for change in ({"max_attempts": 4}, {"overlap_days": 14}, {"max_requests": True}):
        with pytest.raises(ValueError):
            config_record(config(**change))
    duplicated = config(); duplicated["instruments"] *= 2
    with pytest.raises(ValueError):
        config_record(duplicated)


def test_native_backend_cancels_historical_and_head_requests(monkeypatch):
    from equity_research.providers import ibkr_depth
    import sys
    monkeypatch.setitem(sys.modules, "ib_async", SimpleNamespace(BarDataList=type("Bars", (list,), {}),
        util=SimpleNamespace(formatIBDatetime=lambda value: value)))
    calls = []
    async def exercise():
        def start(req_id, contract, **kwargs):
            return asyncio.get_running_loop().create_future()
        client = SimpleNamespace(getReqId=lambda: len(calls) + 1,
            reqHistoricalData=lambda *a: calls.append(("history", a)),
            cancelHistoricalData=lambda req_id: calls.append(("cancel_history", req_id)),
            reqHeadTimeStamp=lambda *a: calls.append(("head", a)),
            cancelHeadTimeStamp=lambda req_id: calls.append(("cancel_head", req_id)))
        base = SimpleNamespace(client_version="2.1.0", errors=[], connect=None, qualify=None, disconnect=None,
            ib=SimpleNamespace(client=client, wrapper=SimpleNamespace(startReq=start)))
        monkeypatch.setattr(ibkr_depth, "make_backend", lambda: base)
        backend = ibkr_depth.make_depth_backend()
        params = {"endDateTime": "20241207-00:00:00", "durationStr": "1 D", "barSizeSetting": "1 day",
                  "whatToShow": "TRADES", "useRTH": True, "formatDate": 1, "timeout": .001}
        with pytest.raises(TimeoutError):
            await backend.historical(SimpleNamespace(), params)
        task = asyncio.create_task(backend.historical(SimpleNamespace(), {**params, "timeout": 30}))
        await asyncio.sleep(0); task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        task = asyncio.create_task(backend.head_timestamp(SimpleNamespace()))
        await asyncio.sleep(0); task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    asyncio.run(exercise())
    assert [c[0] for c in calls] == ["history", "cancel_history", "history", "cancel_history", "head", "cancel_head"]


def test_synthetic_example_and_offline_report_replay(tmp_path):
    import runpy
    example = runpy.run_path(str(Path(__file__).parents[1] / "scripts/make_ibkr_depth_example.py"))
    result = example["demonstrate"](tmp_path / "example")
    assert result["results"] == [{"symbol": "COMPLETE", "status": "complete"}, {"symbol": "GAPPED", "status": "partial"}]
    files, hashes = read_bundle(tmp_path / "example/report")
    assert b"2024-11-26" in files["coverage.json"]
    freeze_report(tmp_path / "example/report", tmp_path / "replayed")
    assert read_bundle(tmp_path / "replayed")[1] == hashes


def test_resume_uses_saved_pacing_and_preserves_unsealed_checkpoint(tmp_path):
    settings = config(max_windows_per_instrument=1)
    auditor(Fake()).run(settings, tmp_path / "audit")
    journal = Journal(tmp_path / "audit")
    abandoned = tmp_path / "audit/events" / f"{journal.sequence:08d}"
    abandoned.mkdir(); (abandoned / "partial.txt").write_text("interrupted write")
    virtual = VirtualTime()
    auditor(Fake(), virtual=virtual).run(settings, tmp_path / "audit", resume=True)
    assert virtual.value >= 15  # Repeated qualification/head/request signatures are paced across processes.
    assert abandoned.name in Journal(tmp_path / "audit").abandoned
    assert (abandoned / "partial.txt").read_text() == "interrupted write"


def test_failed_connection_is_reported_and_resource_pause_can_resume(tmp_path):
    class Down(Fake):
        async def connect(self, *args):
            raise ConnectionError("private account text")
    auditor(Down()).run(config(), tmp_path / "down")
    assert report(tmp_path / "down")["status"] == "failed"
    assert report(tmp_path / "down")["stop_reason"] == "CONNECTION_FAILED"
    settings = config(max_requests=4)
    result = auditor(Fake()).run(settings, tmp_path / "limited")
    assert result["status"] == "RESOURCE_LIMIT"
    for _ in range(5):
        auditor(Fake()).run(settings, tmp_path / "limited", resume=True)
    assert report(tmp_path / "limited")["status"] == "complete"


def test_head_metadata_earlier_than_observed_bars_does_not_confirm_exhaustion(tmp_path):
    fake = Fake(head="2024-11-04", transform=lambda rows: [r for r in rows if r.date.isoformat() >= "2024-11-12"])
    auditor(fake).run(config(), tmp_path / "audit")
    r = report(tmp_path / "audit")
    assert r["actual_earliest_bar"] == "2024-11-12"
    assert r["provider_reported_earliest_date"] == "2024-11-04"
    assert r["status"] == "partial" and r["exhaustion_evidence"] is None


def test_restored_pacing_counts_all_prior_requests_even_with_tied_timestamps():
    virtual = VirtualTime()
    audit = auditor(Fake(), virtual=virtual)
    audit.journal = SimpleNamespace(events=[{"event": {"kind": "request_started", "signature": str(i),
        "started_at": NOW.isoformat()}} for i in range(60)])
    audit.restore_pacing()
    assert len(audit.pacer.events) == 60
    asyncio.run(audit.pacer.wait("new request"))
    assert virtual.value == 600 and max(virtual.waits) <= 60


def test_committed_offline_fixture_replays_without_ibkr_package(tmp_path, monkeypatch):
    import builtins
    original = builtins.__import__
    def restricted(name, *args, **kwargs):
        if name == "ib_async" or name.startswith("ib_async."):
            raise AssertionError("offline report imported IBKR")
        return original(name, *args, **kwargs)
    monkeypatch.setattr(builtins, "__import__", restricted)
    fixture = Path(__file__).parents[1] / "docs/evidence/ibkr-depth-offline-v1"
    freeze_report(fixture, tmp_path / "replayed")
    assert read_bundle(fixture) == read_bundle(tmp_path / "replayed")
