"""Synthetic provider-like fixtures. No test establishes actual Yahoo quality."""

from datetime import UTC, datetime
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pandas as pd
from pandas.testing import assert_frame_equal
import pytest

from equity_research.cli import main
from equity_research.data import load_dataset
from equity_research.ingestion.calendar import schedule
from equity_research.ingestion.canonical import convert
from equity_research.ingestion.export import export, validate
from equity_research.ingestion.frames import capture_frame, restore_frame
from equity_research.ingestion.quality import analyze
from equity_research.ingestion.snapshots import compare, read_snapshot, write_snapshot
from equity_research.ingestion.storage import encode, read_bundle
from equity_research.providers.yahoo import CLIENT_VERSION, fetch, request_record
from equity_research.reporting import run_experiment

FIXED = datetime(2025, 2, 1, 12, tzinfo=UTC)


@pytest.fixture
def bars():
    # Thursday Nov 28 is Thanksgiving; Friday Nov 29 closes at 13:00 ET.
    return pd.DataFrame({"Open": [100.0, 101.0], "High": [102.0, 103.0], "Low": [99.0, 100.0],
                         "Close": [101.0, 102.0], "Volume": [1000, 1100], "Adj Close": [101.0, 102.0],
                         "Dividends": [0.0, 0.0], "Stock Splits": [0.0, 0.0]},
                        index=pd.DatetimeIndex(["2024-11-27", "2024-11-29"], name="Date"))


@pytest.fixture
def snapshot(tmp_path, bars):
    def make(frame=None, name="snapshot", start="2024-11-27", end="2024-11-29", **acquisition):
        request = request_record("SYNTH", start, end)
        request["origin"] = "synthetic"
        acq = {"status": "SUCCESS", "started_at": FIXED.isoformat(), "completed_at": FIXED.isoformat(),
               "client": "synthetic", "client_version": "fixture_v1", "historical_availability": "unknown",
               "errors": [], **acquisition}
        path = tmp_path / name
        write_snapshot(path, request, acq, bars if frame is None else frame)
        return path
    return make


@pytest.fixture
def evidence():
    def make(path):
        saved = read_snapshot(path)
        req = saved["request"]
        ref = {"status": "VERIFIED", "reference": "synthetic:gate-mechanics-only"}
        return {"schema_version": "research_evidence_v1", "kind": "synthetic",
                "snapshot_content_sha256": saved["acquisition"]["content_sha256"],
                "identity": {**ref, "security_id": "synthetic-security-1", "research_symbol": "SYNTH",
                             "provider_symbol": "SYNTH", "listing_venue": "XNYS", "currency": "USD",
                             "known_at": "2024-01-01T00:00:00Z", "valid_from": "2000-01-01", "valid_through": "2030-01-01"},
                "basis": {**ref, "price_basis": "RAW_VERIFIED", "coverage_start": req["start"],
                          "coverage_end": "2025-02-01",
                          "split_adjustment": {**ref, "convention": "unadjusted"},
                          "dividend_adjustment": {**ref, "convention": "unadjusted"},
                          "volume": {**ref, "units": "contemporaneous_shares"}},
                "actions": {**ref, "coverage_start": req["start"], "coverage_end": "2025-02-01", "events": []},
                "availability": {**ref, "historical_availability": "verified",
                                 "sessions": {s["session_date"]: s["closes_at"] for s in schedule(req["start"], req["end"])["sessions"]}}}
    return make


@pytest.fixture
def fake_client(monkeypatch):
    original = importlib.metadata.version
    monkeypatch.setattr(importlib.metadata, "version", lambda name: CLIENT_VERSION if name == "yfinance" else original(name))
    def install(function):
        monkeypatch.setitem(sys.modules, "yfinance", SimpleNamespace(download=function))
    return install


@pytest.mark.parametrize("orientation", [None, 0, 1])
def test_fetch_exact_request_and_complete_capture(tmp_path, bars, fake_client, orientation):
    frame = bars if orientation is None else pd.concat({"BRK-B": bars}, axis=1)
    if orientation == 1:
        frame = frame.swaplevel(axis=1)
    calls = []
    fake_client(lambda **kw: calls.append(kw) or frame)
    path = tmp_path / "attempt"
    outcome = fetch("BRK.B", "2024-11-27", "2024-11-29", path, clock=lambda: FIXED)
    assert outcome["status"] == "SUCCESS"
    saved = read_snapshot(path)
    assert_frame_equal(saved["frame"], frame)
    assert calls == [saved["request"]["parameters"]]
    assert calls[0] == {"tickers": ["BRK-B"], "start": "2024-11-27", "end": "2024-11-30",
                        "interval": "1d", "auto_adjust": False, "back_adjust": False, "actions": True,
                        "repair": False, "keepna": True, "rounding": False, "prepost": False,
                        "group_by": "ticker", "threads": False, "ignore_tz": False,
                        "multi_level_index": True, "progress": False, "period": None, "timeout": 15.0}
    assert saved["acquisition"]["capture_level"] == "client_return"
    assert saved["acquisition"]["client_version"] == CLIENT_VERSION
    assert saved["acquisition"]["historical_availability"] == "unknown"
    with pytest.raises(FileExistsError):
        fetch("BRK.B", "2024-11-27", "2024-11-29", path, clock=lambda: FIXED)
    assert len(calls) == 1


@pytest.mark.parametrize("kind,status", [("empty", "EMPTY_RESPONSE"), ("partial", "PARTIAL_RESPONSE"),
                                         ("schema", "SCHEMA_FAILURE"), ("timeout", "REQUEST_FAILED"),
                                         ("failed", "REQUEST_FAILED")])
def test_failed_or_partial_attempts_are_immutable_records(tmp_path, bars, fake_client, kind, status):
    def download(**kwargs):
        if kind in {"timeout", "failed"}:
            raise (TimeoutError if kind == "timeout" else RuntimeError)("secret-token /private/path https://secret")
        return {"empty": bars.iloc[:0], "partial": bars.iloc[:1], "schema": bars.drop(columns="Open")}[kind]
    fake_client(download)
    path = tmp_path / kind
    assert fetch("SYNTH", "2024-11-27", "2024-11-29", path, clock=lambda: FIXED)["status"] == status
    saved = read_snapshot(path)
    assert saved["acquisition"]["status"] == status
    assert "secret" not in saved["files"]["acquisition.json"].decode()
    if kind in {"timeout", "failed"}:
        assert saved["frame"] is None
    quality = validate(path, tmp_path / (kind + "-quality"))
    assert quality["gates"]["acquisition"] == "FAIL"
    assert quality["export_decision"] == "BLOCKED"


def test_yfinance_logged_failure_is_not_success(tmp_path, bars, fake_client):
    import logging
    def download(**kw):
        logging.getLogger("yfinance").error("timeout with secret token")
        return bars
    fake_client(download)
    result = fetch("SYNTH", "2024-11-27", "2024-11-29", tmp_path / "attempt", clock=lambda: FIXED)
    assert result["status"] == "PARTIAL_RESPONSE"
    assert result["errors"] == [{"code": "TIMEOUT", "source": "client_log"}]


def test_frame_serialization_preserves_precision_axes_missingness_and_dtypes(bars):
    frame = bars.iloc[[1, 0, 0]].copy()
    frame.index = pd.DatetimeIndex(frame.index, tz="America/New_York")
    frame["Open"] = [float("nan"), float("inf"), -0.0]
    frame["nullable"] = pd.array([None, 2, 3], dtype="Int64")
    frame["category"] = pd.Categorical(["b", "a", None], categories=["a", "b", "unused"], ordered=True)
    frame = pd.concat({"SYNTH": frame}, axis=1)
    frame.columns.names = ["Ticker", "Price"]
    assert_frame_equal(restore_frame(capture_frame(frame)), frame)
    assert capture_frame(frame) == capture_frame(restore_frame(capture_frame(frame)))
    duplicated_columns = pd.concat([bars, bars], axis=1)
    assert_frame_equal(restore_frame(capture_frame(duplicated_columns)), duplicated_columns)


def test_hash_corruption_and_overwrite_fail(snapshot, tmp_path):
    path = snapshot()
    old = (path / "hashes.json").read_bytes()
    with pytest.raises(FileExistsError):
        snapshot()
    assert (path / "hashes.json").read_bytes() == old
    with (path / "returned_frame.json").open("ab") as f:
        f.write(b" ")
    with pytest.raises(ValueError, match="hash"):
        read_snapshot(path)


@pytest.mark.parametrize("mutation,code", [
    (lambda f: f.drop(columns="High"), "MISSING_COLUMN"),
    (lambda f: f.assign(Open=[float("nan"), 1]), "MISSING_OR_NONFINITE_NUMBER"),
    (lambda f: f.assign(Close=[float("inf"), 1]), "MISSING_OR_NONFINITE_NUMBER"),
    (lambda f: pd.concat([f, f.iloc[[0]].assign(Close=99)]), "DUPLICATE_SESSION"),
    (lambda f: f.assign(Volume=[0, 100]), "ZERO_VOLUME"),
    (lambda f: f.assign(Volume=[-1, 100]), "NEGATIVE_VOLUME"),
    (lambda f: f.assign(Volume=[1.5, 100]), "NONINTEGRAL_VOLUME"),
    (lambda f: f.assign(High=[1, 2]), "INVALID_OHLC_RANGE"),
    (lambda f: f.assign(Low=[0, 2]), "NONPOSITIVE_PRICE"),
    (lambda f: f.iloc[::-1], "OUT_OF_ORDER"),
    (lambda f: f.set_axis(["bad", "2024-11-29"]), "INVALID_SESSION_DATE"),
    (lambda f: f.assign(Unexpected=3), "UNEXPECTED_COLUMN"),
    (lambda f: f.assign(Close=[1, 100]), "PRICE_DISCONTINUITY_REVIEW"),
])
def test_canonical_anomalies_are_preserved_and_block_export(snapshot, evidence, bars, mutation, code, tmp_path):
    path = snapshot(mutation(bars.copy()))
    before = read_snapshot(path)["hashes"]
    quality = export(path, tmp_path / "export", evidence(path))
    assert code in {i["code"] for i in quality["issues"]}
    assert quality["export_decision"] == "BLOCKED"
    assert not (tmp_path / "export/data_manifest.json").exists()
    report = read_bundle(tmp_path / "export")[0]
    assert len(json.loads(report["canonical.json"])["rows"]) == len(mutation(bars.copy()))
    assert read_snapshot(path)["hashes"] == before


def test_missing_adjusted_close_is_not_fabricated(snapshot, bars):
    path = snapshot(bars.drop(columns="Adj Close"))
    result = analyze(path)
    assert all(r["adj_close"] is None for r in result["canonical"]["rows"])
    assert result["quality"]["gates"]["price_basis"] == "UNKNOWN"


def test_calendar_holiday_early_close_dst_and_exceptional_closure():
    days = schedule("2024-11-27", "2024-11-29")["sessions"]
    assert [d["session_date"] for d in days] == ["2024-11-27", "2024-11-29"]
    assert days[1]["closes_at"] == "2024-11-29T18:00:00+00:00"
    assert [d["session_date"] for d in schedule("2025-01-08", "2025-01-10")["sessions"]] == ["2025-01-08", "2025-01-10"]
    dst = schedule("2025-03-07", "2025-03-10")["sessions"]
    assert dst[0]["opens_at"] == "2025-03-07T14:30:00+00:00"
    assert dst[1]["opens_at"] == "2025-03-10T13:30:00+00:00"


def test_missing_bar_cannot_be_excused_by_missing_manifest_or_unknown_ipo(snapshot, bars, evidence):
    path = snapshot(bars.iloc[:1])
    ev = evidence(path)
    del ev["availability"]["sessions"]["2024-11-29"]
    q = analyze(path, ev)["quality"]
    assert q["gates"]["calendar"] == "FAIL"
    assert q["calendar_counts"]["UNKNOWN_SECURITY_SPECIFIC_GAP"] == 1
    assert q["calendar_counts"]["VALID_MARKET_CLOSURE"] == 1
    ev["identity"]["listing_boundaries"] = {"status": "VERIFIED", "reference": "synthetic:independent-delisting", "last_session": "2024-11-27"}
    q = analyze(path, ev)["quality"]
    assert q["calendar_counts"]["KNOWN_OUTSIDE_LISTING_PERIOD"] == 1
    assert q["gates"]["calendar"] == "FAIL"  # requires a narrower explicit request
    ev["identity"]["listing_boundaries"] = {"status": "VERIFIED", "reference": "synthetic:listed-through-range", "first_session": "2020-01-01", "last_session": "2030-01-01"}
    assert analyze(path, ev)["quality"]["calendar_counts"]["EXPECTED_SESSION_MISSING"] == 1


def test_off_calendar_bar_and_incomplete_session_are_not_removed(snapshot, bars):
    off = pd.concat([bars.iloc[:1], bars.iloc[:1].set_axis(pd.to_datetime(["2024-11-28"])), bars.iloc[1:]])
    q = analyze(snapshot(off))["quality"]
    assert q["calendar_counts"]["OFF_CALENDAR_OBSERVATION"] == 1
    path = snapshot(name="incomplete", completed_at="2024-11-29T17:00:00Z")
    q = analyze(path)["quality"]
    assert q["calendar_counts"]["INCOMPLETE_SESSION"] == 1


@pytest.mark.parametrize("kind", ["split", "dividend", "rename", "later_split"])
def test_events_block_raw_export_including_later_adjustment_horizon(snapshot, bars, evidence, kind):
    frame = bars.copy()
    if kind == "split":
        frame.loc[frame.index[0], "Stock Splits"] = 4.0
    if kind == "dividend":
        frame.loc[frame.index[0], "Dividends"] = 0.25
    path = snapshot(frame)
    ev = evidence(path)
    if kind in {"rename", "later_split"}:
        ev["actions"]["events"] = [{"type": kind, "session_date": "2025-01-15", "reference": "synthetic:independent-action"}]
    result = analyze(path, ev)
    assert result["quality"]["gates"]["corporate_actions"] == "FAIL"
    if kind == "split":
        assert result["canonical"]["events"][0]["value"] == "4.0"


@pytest.mark.parametrize("section", ["identity", "basis", "actions", "availability"])
def test_missing_evidence_never_passes(snapshot, evidence, section):
    path = snapshot()
    ev = evidence(path)
    del ev[section]
    assert analyze(path, ev)["quality"]["export_decision"] == "BLOCKED"


@pytest.mark.parametrize("basis", ["UNKNOWN", "SPLIT_ADJUSTED", "OTHER_ADJUSTED"])
def test_unsupported_price_basis_blocks_even_with_other_claims(snapshot, evidence, basis):
    path = snapshot()
    ev = evidence(path)
    ev["basis"]["price_basis"] = basis
    assert analyze(path, ev)["quality"]["gates"]["price_basis"] != "PASS"


def test_snapshot_bound_evidence_and_full_horizon_required(snapshot, evidence):
    path = snapshot()
    ev = evidence(path)
    ev["actions"]["coverage_end"] = "2024-11-29"
    assert analyze(path, ev)["quality"]["gates"]["corporate_actions"] == "UNKNOWN"
    ev = evidence(path)
    ev["basis"]["volume"]["status"] = "UNKNOWN"
    assert analyze(path, ev)["quality"]["gates"]["price_basis"] == "UNKNOWN"
    ev = evidence(path)
    ev["snapshot_content_sha256"] = "0" * 64
    assert analyze(path, ev)["quality"]["evidence_binding"] == "UNKNOWN"
    ev = evidence(path)
    ev["availability"]["historical_availability"] = "modeled"
    assert analyze(path, ev)["quality"]["historical_availability"] == "unknown"


def test_revision_diff_records_old_correction_adjustment_null_schema_and_dates(snapshot, bars):
    a = snapshot()
    changed = bars.copy()
    changed.iloc[0, changed.columns.get_loc("Close")] = 100.75
    changed.iloc[0, changed.columns.get_loc("Adj Close")] = float("nan")
    changed = pd.concat([changed.iloc[:1], changed.iloc[1:].set_axis(pd.to_datetime(["2024-11-28"]))])
    changed["Extra"] = 3
    b = snapshot(changed, name="revised")
    prior = read_snapshot(a)["hashes"]
    diff = compare(a, b)
    assert diff["stored_bytes_changed"] and diff["frame_bytes_changed"] and diff["schema_changed"]
    assert "returned_frame.json" in {r["file"] for r in diff["stored_file_changes"]}
    assert diff["removed_dates"] == ["2024-11-29"] and diff["new_dates"] == ["2024-11-28"]
    assert {v["field"] for v in diff["changes"]} >= {"Close", "Adj Close", "Extra"}
    assert read_snapshot(a)["hashes"] == prior


def test_repeat_conversion_export_and_downstream_artifacts_stay_identical(snapshot, evidence, bars, tmp_path):
    path = snapshot()
    ev = evidence(path)
    first = tmp_path / "exported"
    assert export(path, first, ev)["export_decision"] == "EXPORT_READY"
    dataset = load_dataset(first / "data.csv", first / "data_manifest.json")
    assert len(dataset.bars) == 2 and dataset.manifest["adjustment"] == "raw"
    candidate = tmp_path / "candidate.json"
    candidate.write_bytes(encode({"symbol": "SYNTH", "source": "manual", "candidate_session": "2024-11-29",
                                 "observed_at": "2024-11-29T20:00:00Z", "available_at": "2024-11-29T20:00:00Z",
                                 "setup_family": "breakout", "provenance": {"kind": "synthetic", "reference": "synthetic:export-test"}}))
    config = Path(__file__).parent / "fixtures/swing_config.json"
    def run(name):
        run_experiment(first / "data.csv", candidate, config, first / "data_manifest.json", tmp_path / name,
                       source_commit="a" * 40)
        return {str(p.relative_to(tmp_path / name)): p.read_bytes() for p in (tmp_path / name).rglob("*") if p.is_file()}
    before = run("before")
    snapshot(bars.assign(Close=[101.25, 102.5]), name="new-provider-vintage")
    assert run("after") == before
    second = tmp_path / "second-export"
    export(path, second, ev)
    assert read_bundle(first)[0] == read_bundle(second)[0]
    with pytest.raises(FileExistsError):
        export(path, first, ev)


def test_cli_validation_comparison_and_blocked_export(snapshot, tmp_path, capsys):
    path = snapshot()
    assert main(["data", "validate", "--snapshot", str(path), "--output", str(tmp_path / "quality")]) == 0
    assert "BLOCKED" in capsys.readouterr().out
    assert main(["data", "export", "--snapshot", str(path), "--output", str(tmp_path / "export")]) == 3
    assert not (tmp_path / "export/data.csv").exists()
    assert main(["data", "compare", "--before", str(path), "--after", str(path), "--output", str(tmp_path / "comparison")]) == 0
    assert json.loads((tmp_path / "comparison/comparison.json").read_bytes())["changes"] == []


def test_imports_and_replay_do_not_import_network_client(tmp_path):
    # A fresh process denies the optional network client import, not just sockets.
    script = """
import builtins
original = builtins.__import__
def guarded(name, *args, **kwargs):
    if name.split('.')[0] in {'yfinance', 'curl_cffi'}:
        raise AssertionError('network client imported by offline path')
    return original(name, *args, **kwargs)
builtins.__import__ = guarded
import equity_research.providers.yahoo
from equity_research.cli import main
assert main(['run','--data','tests/fixtures/synthetic_daily.csv','--manifest','tests/fixtures/data_manifest.json',
             '--candidate','tests/fixtures/candidate.json','--config','tests/fixtures/swing_config.json',
             '--output',OUTPUT,'--source-commit','a'*40]) == 0
""".replace("OUTPUT", repr(str(tmp_path / "offline")))
    import os
    result = subprocess.run([sys.executable, "-c", script], env=dict(os.environ, PYTHONPATH="src"),
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr


def test_same_content_new_attempt_has_separate_byte_and_semantic_identity(snapshot):
    a = snapshot()
    b = snapshot(name="another-attempt", completed_at="2025-02-01T12:00:01Z")
    assert read_snapshot(a)["acquisition"]["content_sha256"] == read_snapshot(b)["acquisition"]["content_sha256"]
    diff = compare(a, b)
    assert diff["stored_bytes_changed"] and not diff["frame_bytes_changed"]
    assert not diff["changes"] and not diff["schema_changed"]


def test_ambiguous_duplicate_revision_keys_do_not_get_deduplicated(snapshot, bars):
    a = snapshot()
    b = snapshot(pd.concat([bars, bars.iloc[[0]]]), name="duplicates")
    assert compare(a, b)["reason"] == "AMBIGUOUS_SCHEMA_OR_SESSION_KEYS"


def test_mismatched_multisymbol_response_retained_as_schema_failure(tmp_path, bars, fake_client):
    frame = pd.concat({"SYNTH": bars, "OTHER": bars}, axis=1)
    fake_client(lambda **kw: frame)
    path = tmp_path / "multi"
    assert fetch("SYNTH", "2024-11-27", "2024-11-29", path, clock=lambda: FIXED)["status"] == "SCHEMA_FAILURE"
    assert_frame_equal(read_snapshot(path)["frame"], frame)


def test_current_incomplete_response_is_partial_not_filtered(tmp_path, bars, fake_client):
    fake_client(lambda **kw: bars)
    path = tmp_path / "incomplete"
    clock = lambda: datetime(2024, 11, 29, 17, tzinfo=UTC)
    assert fetch("SYNTH", "2024-11-27", "2024-11-29", path, clock=clock)["status"] == "PARTIAL_RESPONSE"
    assert_frame_equal(read_snapshot(path)["frame"], bars)


def test_actual_pinned_yfinance_signature_accepts_explicit_parameters():
    # Optional Yahoo extra is used only for this compatibility check; no fetch.
    import inspect
    import yfinance
    assert yfinance.__version__ == CLIENT_VERSION
    assert set(request_record("SYNTH", "2024-11-27", "2024-11-29")["parameters"]) <= set(inspect.signature(yfinance.download).parameters)


def test_unsupported_client_version_records_failure_before_download(tmp_path, monkeypatch):
    original = importlib.metadata.version
    monkeypatch.setattr(importlib.metadata, "version", lambda name: "0.0" if name == "yfinance" else original(name))
    monkeypatch.setitem(sys.modules, "yfinance", SimpleNamespace(download=lambda **kw: pytest.fail("must not fetch")))
    path = tmp_path / "unsupported"
    assert fetch("SYNTH", "2024-11-27", "2024-11-29", path, clock=lambda: FIXED)["status"] == "REQUEST_FAILED"
    assert read_snapshot(path)["acquisition"]["client_version"] == "0.0"


def test_synthetic_evidence_cannot_authorize_real_snapshot(tmp_path, bars, fake_client, evidence):
    fake_client(lambda **kw: bars)
    path = tmp_path / "actual-origin"
    fetch("SYNTH", "2024-11-27", "2024-11-29", path, clock=lambda: FIXED)
    q = analyze(path, evidence(path))["quality"]
    assert q["evidence_binding"] == "UNKNOWN" and q["export_decision"] == "BLOCKED"


def test_non_nyse_listing_needs_explicit_schedule_alignment(snapshot, evidence):
    path = snapshot()
    ev = evidence(path)
    ev["identity"]["listing_venue"] = "XNAS"
    assert analyze(path, ev)["quality"]["gates"]["calendar"] == "UNKNOWN"
    ev["identity"]["xnys_alignment"] = {"status": "VERIFIED", "reference": "synthetic:date-specific-session-comparison"}
    assert analyze(path, ev)["quality"]["gates"]["calendar"] == "PASS"


def test_adjusted_close_disagreement_is_diagnostic_not_action_inference(snapshot, bars, evidence):
    path = snapshot(bars.assign(**{"Adj Close": [90.0, 91.0]}))
    result = analyze(path, evidence(path))
    assert result["canonical"]["events"] == []
    assert {i["code"] for i in result["canonical"]["issues"]} == {"ADJUSTED_CLOSE_DIFFERS_REVIEW"}
    assert result["quality"]["gates"]["data_quality"] == "FAIL"


def test_synthetic_readme_workflow(tmp_path):
    import os
    output = tmp_path / "example"
    result = subprocess.run([sys.executable, "scripts/make_yahoo_synthetic_example.py", "--output", str(output)],
                            env=dict(os.environ, PYTHONPATH="src"), capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert main(["data", "export", "--snapshot", str(output / "snapshot"), "--evidence", str(output / "evidence.json"),
                 "--output", str(tmp_path / "research")]) == 0
    assert len(load_dataset(tmp_path / "research/data.csv", tmp_path / "research/data_manifest.json").bars) == 2
