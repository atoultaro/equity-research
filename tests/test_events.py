"""Deterministic synthetic evidence and prices; no web/TWS needed."""

from copy import deepcopy
from datetime import UTC, datetime
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from equity_research.cli import main
from equity_research.events.alignment import align_event, event_schedule
from equity_research.events.dataset import freeze_study, load_event_study
from equity_research.events.diagnostics import diagnostics
from equity_research.events.model import claim, freeze_events, load_events, revision_key, validate
from equity_research.history.cache import HistoryCache, history
from equity_research.history.contracts import Security
from equity_research.history.dataset import freeze, load_research_dataset
from equity_research.ingestion.calendar import schedule
from equity_research.ingestion.storage import encode, read_bundle, write_bundle
from test_history import FIXED, FixtureYahoo, bars, MockIB, ib_provider

CAPTURE = "2025-02-01T12:00:00+00:00"


def event(kind="EARNINGS", day="2024-11-25", *, announced=None, relation="UNKNOWN", precision="DATE", effective=None):
    payload = {"eps_diluted_gaap": "1.25", "revenue_usd": "1000000"}
    period = {"year": 2024, "quarter": 4, "period_end": "2024-09-30"}
    if kind == "DIVIDEND":
        period = None
        payload = {"cash_per_share": "0.25", "ex_date": effective,
                   "ex_date_status": "VERIFIED" if effective else "UNKNOWN",
                   "record_date": "2024-12-02", "payment_date": "2024-12-05"}
    elif kind == "SPLIT":
        period = None
        payload = {"new_shares": "4", "old_shares": "1", "record_date": "2024-11-26", "distribution_date": None}
    return {"event_id": "synthetic-" + kind, "revision": 1, "security_id": "synthetic-AAPL",
            "event_type": kind, "event_date": day, "announced_at": announced,
            "announced_time_precision": precision, "announced_session_relation": relation,
            "relation_evidence_status": "UNKNOWN" if relation == "UNKNOWN" else "VERIFIED",
            "effective_date": effective, "fiscal_period": period, "payload": payload, "currency": "USD",
            "source_ids": ["synthetic-source"], "captured_at": CAPTURE,
            "evidence_status": "VERIFIED", "unresolved_fields": []}


def source(events, *, published=None, precision="UNKNOWN", sid="synthetic-source"):
    return {"source_id": sid, "url": "https://example.invalid/issuer-release", "source_document_id": "synthetic-doc",
            "published_at": published, "publication_precision": precision,
            "publication_evidence_status": "VERIFIED" if published else "UNKNOWN", "captured_at": CAPTURE,
            "evidence_note": "Synthetic fixture, no real event or archive claim",
            "assertions": {revision_key(e): claim(e) for e in events}}


@pytest.mark.parametrize("kind,effective", [("EARNINGS", None), ("DIVIDEND", "2024-11-29"), ("SPLIT", "2024-11-29")])
def test_event_types_and_distinct_dates_round_trip(tmp_path, kind, effective):
    e = event(kind, effective=effective)
    quality = validate([e], [source([e])])
    assert quality["event_count"] == 1
    freeze_events([e], [source([e])], tmp_path / "events")
    loaded = load_events(tmp_path / "events")
    assert loaded.events == [e]
    assert loaded.events[0]["event_date"] == "2024-11-25"
    assert loaded.events[0]["effective_date"] == effective
    assert loaded.events[0]["announced_at"] is None
    changed = loaded.events
    changed[0]["payload"].clear()
    assert loaded.events == [e]


@pytest.mark.parametrize("changes", [
    {"announced_at": "2024-11-25T00:00:00", "announced_time_precision": "SECOND"},
    {"announced_at": "2024-11-25T00:00:00-05:00"},
    {"announced_time_precision": "MINUTE"}, {"event_type": "OTHER"}, {"currency": "EUR"},
    {"revision": 0}, {"source_ids": []}, {"source_ids": ["synthetic-source", "synthetic-source"]},
    {"event_date": "2024-11-26", "announced_at": "2024-11-25T12:00:00-05:00", "announced_time_precision": "SECOND"},
])
def test_invalid_evidence_is_rejected(changes):
    e = event()
    e.update(changes)
    with pytest.raises((ValueError, KeyError)):
        validate([e], [source([e])])


def test_dividend_does_not_substitute_payment_or_record_date():
    e = event("DIVIDEND")
    e["effective_date"] = e["payload"]["payment_date"]
    with pytest.raises(ValueError, match="ex-date"):
        validate([e], [source([e])])


def test_source_assertion_and_provenance_must_match():
    e = event()
    s = source([e])
    e["payload"]["eps_diluted_gaap"] = "2.00"
    with pytest.raises(ValueError, match="assertion"):
        validate([e], [s])


def test_duplicate_sources_are_reported_and_not_silently_merged():
    e = event()
    s = source([e]); other = deepcopy(s); other["source_id"] = "second"
    assert validate([e], [s, other])["duplicate_source_ids"] == ["second"]
    with pytest.raises(ValueError, match="source_id"):
        validate([e], [s, s])


def test_conflicting_revisions_remain_retrospective_but_are_not_historically_usable(tmp_path):
    a = event()
    b = deepcopy(a); b["revision"] = 2; b["payload"]["eps_diluted_gaap"] = "9"
    freeze_events([a, b], [source([a, b], published="2024-11-25T16:30:00-05:00", precision="MINUTE")], tmp_path / "events")
    ds = load_events(tmp_path / "events")
    assert len(ds.events) == 2
    assert ds.quality["conflicting_event_ids"] == [a["event_id"]]
    assert ds.as_known(CAPTURE)["events"] == []
    assert len(ds.as_known(CAPTURE)["knowledge_unknown"]) == 2


def test_immutable_event_corrections_and_hash_tampering(tmp_path):
    e = event(); s = source([e])
    original = freeze_events([e], [s], tmp_path / "v1")
    with pytest.raises(FileExistsError):
        freeze_events([e], [s], tmp_path / "v1")
    revised = deepcopy(e); revised["revision"] = 2; revised["payload"]["eps_diluted_gaap"] = "2"
    assert freeze_events([revised], [source([revised])], tmp_path / "v2") != original
    assert load_events(tmp_path / "v1").events == [e]
    (tmp_path / "v1/event_sources.json").write_bytes(b"{}")
    with pytest.raises(ValueError, match="hash"):
        load_events(tmp_path / "v1")


@pytest.mark.parametrize("day,announced,relation,precision,reaction,measured", [
    ("2024-11-25", "2024-11-25T08:00:00-05:00", "UNKNOWN", "SECOND", "2024-11-25", "BEFORE_OPEN"),
    ("2024-11-25", "2024-11-25T21:30:00+00:00", "AFTER_CLOSE", "MINUTE", "2024-11-26", "AFTER_CLOSE"),
    ("2024-11-25", "2024-11-25T12:00:00-05:00", "UNKNOWN", "SECOND", "2024-11-25", "DURING_SESSION"),
    ("2024-11-23", None, "UNKNOWN", "DATE", "2024-11-25", "NONTRADING_DAY"),
    ("2024-11-28", None, "UNKNOWN", "DATE", "2024-11-29", "NONTRADING_DAY"),
    ("2024-11-29", "2024-11-29T13:30:00-05:00", "UNKNOWN", "SECOND", "2024-12-02", "AFTER_CLOSE"),
    ("2024-11-29", None, "AFTER_CLOSE", "DATE", "2024-12-02", "AFTER_CLOSE"),
    ("2024-03-11", "2024-03-11T13:00:00+00:00", "UNKNOWN", "SECOND", "2024-03-11", "BEFORE_OPEN"),
    ("2024-11-04", "2024-11-04T14:00:00+00:00", "UNKNOWN", "SECOND", "2024-11-04", "BEFORE_OPEN"),
])
def test_calendar_alignment_includes_dst_holidays_and_early_close(day, announced, relation, precision, reaction, measured):
    e = event(day=day, announced=announced, relation=relation, precision=precision)
    a = align_event(e, schedule("2024-03-01", "2024-12-10"))
    assert a["reaction_session"] == reaction
    assert a["announcement_relation"] == measured
    assert not a["timing_ambiguous"]


def test_unknown_time_keeps_both_possible_sessions_and_unknown_relation_is_not_verified():
    e = event(relation="AFTER_CLOSE"); e["relation_evidence_status"] = "UNKNOWN"
    a = align_event(e, schedule("2024-11-20", "2024-12-05"))
    assert a["reaction_session"] is None
    assert a["announcement_possible_sessions"] == ["2024-11-25", "2024-11-26"]
    assert a["timing_ambiguous"]


def test_precision_crossing_close_and_conflicting_relation_remain_ambiguous():
    e = event(announced="2024-11-25T15:59:30-05:00", precision="MINUTE")
    cal = schedule("2024-11-20", "2024-12-05")
    assert align_event(e, cal)["reaction_session"] is None
    e = event(announced="2024-11-25T08:00:00-05:00", precision="SECOND", relation="AFTER_CLOSE")
    assert "TIMING_EVIDENCE_CONFLICT" in align_event(e, cal)["issues"]


def test_effective_session_is_not_declaration_and_nontrading_effective_not_shifted():
    e = event("DIVIDEND", effective="2024-11-29")
    cal = schedule("2024-11-20", "2024-12-05")
    a = align_event(e, cal)
    assert a["announcement_date"] == "2024-11-25"
    assert a["reaction_session"] == "2024-11-29"
    e["effective_date"] = "2024-11-28"
    a = align_event(e, cal)
    assert a["reaction_session"] is None
    assert "EFFECTIVE_DATE_NOT_AN_EXCHANGE_SESSION" in a["issues"]


def test_as_known_uses_strict_publication_upper_bound_not_capture_or_retrospective_time(tmp_path):
    e = event(announced="2024-11-25T16:30:00-05:00", precision="MINUTE", relation="AFTER_CLOSE")
    freeze_events([e], [source([e])], tmp_path / "no-proof")
    assert load_events(tmp_path / "no-proof").as_known(CAPTURE)["events"] == []
    s = source([e], published="2024-11-25T16:30:00-05:00", precision="MINUTE")
    freeze_events([e], [s], tmp_path / "proof")
    ds = load_events(tmp_path / "proof")
    for cutoff in ("2024-11-25T16:00:00-05:00", "2024-11-25T16:30:59-05:00", "2024-11-25T16:31:00-05:00"):
        assert ds.as_known(cutoff)["events"] == []
    assert ds.as_known("2024-11-25T21:31:01+00:00")["events"] == [e]
    assert ds.as_known(CAPTURE)["archive_completeness"] == "UNKNOWN"
    with pytest.raises(ValueError, match="offset"):
        ds.as_known("2024-11-26T00:00:00")


@pytest.fixture
def price_bundle(tmp_path):
    security = Security("AAPL", "synthetic-AAPL", "synthetic identity", "AAPL", "AAPL", "NASDAQ", "XNAS")
    start, end = "2024-10-01", "2024-12-20"
    frame = bars(start, end, adjusted=False)
    # Deterministic drift distinguishes the anchor/horizon and gap denominator.
    for i, day in enumerate(frame.index):
        value = 100 + i
        frame.loc[day, ["Open", "High", "Low", "Close", "Volume"]] = [value, value + 3, value - 2, value + 1, 1000 + i * 10]
    provider = ib_provider(MockIB(frame=frame))
    cache = HistoryCache(tmp_path / "cache")
    report = history(cache, provider, [security], start, end, clock=lambda: FIXED)
    assert report["status"] == "SUCCESS"
    output = tmp_path / "prices"
    freeze(cache, "ibkr", [security], start, end, output, clock=lambda: FIXED)
    return output, security


def run_diag(tmp_path, price_bundle, events=None, mutate=None):
    price_path, _ = price_bundle
    prices = load_research_dataset(price_path)
    if mutate:
        files, _ = read_bundle(price_path)
        entry = prices.manifest["securities"]["AAPL"]
        record = json.loads(files[entry["bars_file"]]); mutate(record["rows"])
        files[entry["bars_file"]] = encode(record)
        write_bundle(tmp_path / "changed-prices", files)
        prices = load_research_dataset(tmp_path / "changed-prices")
    events = events or [event(relation="AFTER_CLOSE")]
    freeze_events(events, [source(events)], tmp_path / "events")
    ds = load_events(tmp_path / "events")
    cal = event_schedule(events, prices.manifest["start"], prices.manifest["end"])
    aligned = [align_event(e, cal) for e in events]
    return diagnostics(prices, "AAPL", ds, aligned, cal), prices, ds, cal, aligned


def test_diagnostic_gap_volume_atr_and_post_close_returns(tmp_path, price_bundle):
    report, prices, _, _, _ = run_diag(tmp_path, price_bundle)
    r = report["events"][0]
    rows = list(prices.bars("AAPL")); i = next(i for i, b in enumerate(rows) if b["session_date"] == "2024-11-26")
    pre, post = rows[i - 1], rows[i]
    assert r["status"] == "AVAILABLE"
    assert r["overnight_gap_pct"] == pytest.approx((float(post["open"]) / float(pre["close"]) - 1) * 100)
    average = sum(float(b["volume"]) for b in rows[i - 20:i]) / 20
    assert r["volume_relative20"] == pytest.approx(float(post["volume"]) / average)
    assert r["pre_event_atr14"] == 5
    for h in (1, 5, 10):
        assert r["subsequent_close_returns_pct"][str(h)] == pytest.approx((float(rows[i + h]["close"]) / float(post["close"]) - 1) * 100)
    assert r["price_basis"] == "IBKR_TRADES_SPLIT_ADJUSTED_DOCUMENTED"
    assert not r["basis_verified"]


def test_event_and_future_prices_cannot_change_pre_event_features(tmp_path, price_bundle):
    baseline, _, _, _, _ = run_diag(tmp_path / "before", price_bundle)
    def mutate(rows):
        for row in rows:
            if row["session_date"] >= "2024-11-26":
                for key in ("open", "high", "low", "close"):
                    row[key] = str(float(row[key]) * 3)
                row["volume"] = "999999"
    after, _, _, _, _ = run_diag(tmp_path / "after", price_bundle, mutate=mutate)
    assert baseline["events"][0]["pre_event_atr14"] == after["events"][0]["pre_event_atr14"]
    assert baseline["events"][0]["volume_relative20"] != after["events"][0]["volume_relative20"]
    assert baseline["events"][0]["previous_close"] == after["events"][0]["previous_close"]


@pytest.mark.parametrize("missing,issue,field", [
    ("2024-11-25", "MISSING_PREVIOUS_OR_REACTION_SESSION", "previous_close"),
    ("2024-11-26", "MISSING_PREVIOUS_OR_REACTION_SESSION", "overnight_gap_pct"),
    ("2024-11-01", "MISSING_VOLUME_WARMUP", "volume_relative20"),
    ("2024-11-20", "MISSING_ATR_WARMUP", "pre_event_atr14"),
    ("2024-11-27", "MISSING_OUTCOME_5_SESSIONS", "subsequent_close_returns_pct"),
])
def test_missing_sessions_never_shift_windows_or_fill(tmp_path, price_bundle, missing, issue, field):
    report, _, _, _, _ = run_diag(tmp_path, price_bundle, mutate=lambda rows: rows.__setitem__(slice(None), [r for r in rows if r["session_date"] != missing]))
    r = report["events"][0]
    assert issue in r["issues"]
    assert r[field]["5"] is None if field == "subsequent_close_returns_pct" else r[field] is None
    assert r["status"] != "AVAILABLE"


def test_missing_initial_warmup_and_end_outcomes_are_separate(tmp_path, price_bundle):
    early = event(day="2024-10-01", relation="BEFORE_OPEN")
    report, _, _, _, _ = run_diag(tmp_path / "early", price_bundle, [early])
    assert report["events"][0]["previous_close"] is None
    late = event(day="2024-12-19", relation="AFTER_CLOSE")
    report, _, _, _, _ = run_diag(tmp_path / "late", price_bundle, [late])
    assert report["events"][0]["overnight_gap_pct"] is not None
    assert report["events"][0]["subsequent_close_returns_pct"] == {"1": None, "5": None, "10": None}


def test_intraday_and_unknown_earnings_do_not_use_overnight_windows(tmp_path, price_bundle):
    for index, e in enumerate([event(), event(announced="2024-11-25T12:00:00-05:00", precision="SECOND")]):
        report, _, _, _, _ = run_diag(tmp_path / str(index), price_bundle, [e])
        assert report["events"][0]["overnight_gap_pct"] is None
        assert report["events"][0]["status"] == "UNAVAILABLE"


def test_dividend_and_split_diagnostics_preserve_unverified_basis(tmp_path, price_bundle):
    dividend = event("DIVIDEND", effective="2024-11-29")
    split = event("SPLIT", effective="2024-11-29")
    report, prices, _, _, _ = run_diag(tmp_path, price_bundle, [dividend, split])
    d, s = report["events"]
    assert d["cash_per_share_source_quote"] == "0.25"
    assert "NOT_MECHANICAL" in d["interpretation"]
    assert s["status"] == "UNAVAILABLE"
    assert s["issues"] == ["SPLIT_PRICE_AND_VOLUME_BASIS_UNVERIFIED"]
    assert prices.manifest["securities"]["AAPL"]["basis"]["verified"] is False


def test_unknown_ex_date_has_no_fabricated_price_diagnostic(tmp_path, price_bundle):
    report, _, _, _, _ = run_diag(tmp_path, price_bundle, [event("DIVIDEND")])
    assert report["events"][0]["issues"] == ["EX_DATE_UNKNOWN"]
    assert report["events"][0]["first_post_open"] is None


def test_no_source_mixing_or_invalid_prices_in_diagnostics(tmp_path, price_bundle):
    with pytest.raises(ValueError, match="provenance"):
        run_diag(tmp_path / "mixed", price_bundle, mutate=lambda rows: rows[1].update(provider="yahoo"))
    with pytest.raises(ValueError, match="OHLCV"):
        run_diag(tmp_path / "invalid", price_bundle, mutate=lambda rows: rows[1].update(high="1"))
    with pytest.raises(ValueError, match="identity"):
        e = event(); e["security_id"] = "other-security"
        run_diag(tmp_path / "identity", price_bundle, [e])


def test_composition_is_self_contained_offline_and_does_not_change_price_schema(tmp_path, price_bundle):
    path, _ = price_bundle
    e = event(relation="AFTER_CLOSE")
    freeze_events([e], [source([e])], tmp_path / "event-input")
    hashes = freeze_study(path, tmp_path / "event-input", "AAPL", tmp_path / "study")
    assert load_research_dataset(path).manifest["schema_version"] == "research_dataset_v1"
    shutil.rmtree(path); shutil.rmtree(tmp_path / "event-input"); shutil.rmtree(tmp_path / "cache")
    study = load_event_study(tmp_path / "study")
    assert study.content_sha256 == hashes["bundle_sha256"]
    assert study.retrospective["events"] == [e]
    assert study.as_known(CAPTURE)["events"] == []
    assert "diagnostics" not in study.as_known(CAPTURE)
    assert study.diagnostics["events"][0]["status"] == "AVAILABLE"
    code = """
import importlib.abc, sys
class Block(importlib.abc.MetaPathFinder):
 def find_spec(self, name, path=None, target=None):
  if name.split('.')[0] in {'pandas','numpy','exchange_calendars','ib_async','yfinance','pyarrow'} or '.providers' in name:
   raise AssertionError('optional or network provider imported: '+name)
sys.meta_path.insert(0,Block())
from equity_research.events import load_event_study
s=load_event_study(sys.argv[1]); assert len(s.bars())>40; assert s.diagnostics['events']
"""
    proc = subprocess.run([sys.executable, "-c", code, str(tmp_path / "study")], env={"PYTHONPATH": str(Path("src").resolve())}, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    with pytest.raises(FileExistsError):
        freeze_study("missing", "missing", "AAPL", tmp_path / "study")
    (tmp_path / "study/calendar.json").write_text("{}")
    with pytest.raises(ValueError, match="hash"):
        load_event_study(tmp_path / "study")


def test_offline_cli_event_freeze_and_composition(tmp_path, price_bundle, capsys):
    path, _ = price_bundle
    e = event(relation="AFTER_CLOSE")
    events, sources = tmp_path / "input-events.json", tmp_path / "input-sources.json"
    events.write_bytes(encode({"schema_version": "corporate_events_v1", "events": [e]}))
    sources.write_bytes(encode({"schema_version": "event_sources_v1", "sources": [source([e])]}))
    assert main(["data", "events-freeze", "--events", str(events), "--sources", str(sources), "--output", str(tmp_path / "events")]) == 0
    assert main(["data", "event-study", "--prices", str(path), "--events", str(tmp_path / "events"), "--symbol", "AAPL", "--output", str(tmp_path / "study")]) == 0
    assert len(capsys.readouterr().out.splitlines()) == 2
    assert load_event_study(tmp_path / "study").manifest["execution_admission"] == "UNCHANGED_NOT_GRANTED"


def test_unverified_event_with_a_publication_stamp_is_not_as_known_evidence(tmp_path):
    e = event(); e["evidence_status"] = "UNVERIFIED"
    freeze_events([e], [source([e], published="2024-11-25T16:30:00-05:00", precision="MINUTE")], tmp_path / "events")
    result = load_events(tmp_path / "events").as_known(CAPTURE)
    assert result["events"] == []
    assert result["knowledge_unknown"] == [revision_key(e)]


def test_resealing_outer_study_cannot_hide_embedded_evidence_change(tmp_path, price_bundle):
    prices, _ = price_bundle
    e = event(relation="AFTER_CLOSE")
    freeze_events([e], [source([e])], tmp_path / "events")
    freeze_study(prices, tmp_path / "events", "AAPL", tmp_path / "study")
    files, _ = read_bundle(tmp_path / "study")
    files["events-event_sources.json"] = encode({"schema_version": "event_sources_v1", "sources": []})
    write_bundle(tmp_path / "resealed", files)
    with pytest.raises(ValueError, match="lineage"):
        load_event_study(tmp_path / "resealed")
