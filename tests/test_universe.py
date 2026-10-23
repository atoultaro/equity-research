"""Offline historical identity, knowledge boundaries, immutable panels and integration."""

from copy import deepcopy
from datetime import timedelta
from decimal import Decimal
import json
from pathlib import Path

import pytest

from equity_research.ingestion.calendar import schedule
from equity_research.ingestion.storage import digest, encode, read_bundle, write_bundle
from equity_research.models import timestamp
from equity_research.universe import (SecurityMaster, import_master, ResearchPanel, freeze_panel,
                                      HistoricalUniverse, build_universe, default_definition)
from equity_research.universe.master import source_quality
from equity_research.universe.synthetic import master_capture, price_rows, synthetic_source


@pytest.fixture(scope="module")
def calendar():
    return schedule("2022-01-01", "2022-08-31")


@pytest.fixture
def inputs(calendar):
    master = master_capture(4, hard_cases=False)
    rows = [r for i in range(4) for r in price_rows(i, calendar["sessions"])]
    # Identical liquidity and prices ensure stable ID ties, independent of input order.
    for row in rows:
        row.update(open="10", high="11", low="9", close="10", volume="1000")
    return master, rows


def capture(path, rows, **source):
    path.write_bytes(encode({"schema_version": "daily_panel_capture_v1",
                            "source": {**synthetic_source(), "status": "SUCCESS", "failure_codes": [], **source}, "rows": rows}))
    return path


def freeze(tmp_path, calendar, inputs, *, months=("2022-04",), decisions=None, definition=None, name="run"):
    root = tmp_path / name
    root.mkdir()
    master, rows = inputs
    source = root / "master.json"
    source.write_bytes(encode(master))
    import_master(source, root / "master")
    freeze_panel([capture(root / "prices.json", rows)], calendar, root / "panel")
    build_universe(root / "master", root / "panel", definition or default_definition(2), list(months), root / "universe", decisions=decisions)
    return HistoricalUniverse(root / "universe", master=root / "master", panel=root / "panel")


def candidate(universe, sid=0, index=0):
    return next(c for c in universe.snapshots[index]["candidates"] if c["security_id"] == f"synthetic:{sid:05d}")


def query(u, date="2022-05-02", cutoff="2022-05-02T09:20:00-04:00"):
    return u.members_as_of(date, decision_timestamp=cutoff)


def master_fixture(tmp_path):
    path = tmp_path / "source.json"
    path.write_bytes(encode(master_capture(100)))
    import_master(path, tmp_path / "master")
    return SecurityMaster(tmp_path / "master")


def test_stable_identity_ticker_change_and_reuse(tmp_path):
    m = master_fixture(tmp_path)
    before = m.as_of("synthetic:00002", "2008-06-01", "2008-06-02T12:00:00Z")
    after = m.as_of("synthetic:00002", "2015-06-01", "2015-06-02T12:00:00Z")
    assert before["symbol"] != after["symbol"] and before["provider_security_id"] == after["provider_security_id"]
    assert m.resolve_symbol("REUSED", "2008-06-01", "2008-06-02T12:00:00Z")["security_id"] == "synthetic:00003"
    assert m.resolve_symbol("REUSED", "2016-06-01", "2016-06-02T12:00:00Z")["security_id"] == "synthetic:00004"
    with pytest.raises(ValueError, match="missing or ambiguous"):
        m.resolve_symbol("REUSED", "2013-06-01", "2013-06-02T12:00:00Z")


def test_dual_classes_reorganization_ipo_exchange_transfer(tmp_path):
    m = master_fixture(tmp_path)
    a = m.as_of("synthetic:00005", "2022-04-29", "2022-05-01T12:00:00Z")
    b = m.as_of("synthetic:00006", "2022-04-29", "2022-05-01T12:00:00Z")
    assert a["issuer_id"] == b["issuer_id"] and a["share_class_id"] != b["share_class_id"]
    assert m.as_of("synthetic:00008", "2010-06-01", "2026-01-01T00:00:00Z") is None
    assert m.as_of("synthetic:00010", "2010-06-01", "2010-06-02T12:00:00Z") is None
    assert m.as_of("synthetic:00007", "2022-04-29", "2022-05-01T00:00:00Z")["trading_status"] == "DELISTED"
    assert m.as_of("synthetic:00009", "2017-06-01", "2017-06-02T12:00:00Z")["exchange"] == "XNAS"
    assert m.as_of("synthetic:00009", "2019-06-01", "2019-06-02T12:00:00Z")["exchange"] == "XNYS"


def test_unknown_knowledge_remains_unknown_and_reconstruction_explicit(tmp_path):
    m = master_fixture(tmp_path)
    assert m.as_of("synthetic:00019", "2022-04-29", "2022-05-01T00:00:00Z") is None
    assert m.as_of("synthetic:00019", "2022-04-29", "2022-05-01T00:00:00Z", reconstruct_unknown=True)["known_at"] is None
    assert m.quality["unknown_knowledge_assertions"] == 1


def test_lifecycle_cash_halt_terminal_and_unknown_exdate_preserved(tmp_path):
    m = master_fixture(tmp_path)
    merger = next(e for e in m.events if e["event_type"] == "MERGER")
    assert merger["cash_consideration"] == "25" and merger["terminal_value"] is None
    assert not m.lifecycle_as_of("synthetic:00000", "2010-01-01T00:00:00Z")
    assert len(m.quality["unresolved_terminal_events"]) == 4
    unknown = next(e for e in m.events if e["event_type"] == "DIVIDEND" and e["effective_date"] is None)
    assert unknown["payment_date"] == "2020-06-15" and unknown["ex_date_status"] == "UNRESOLVED"
    assert any(e["event_type"] == "HALT" for e in m.events)
    assert any(e["event_type"] == "SPLIT" and e["price_adjustments_applied"] is False for e in m.events)


def test_rank_ties_monthly_boundaries_and_formula(tmp_path, calendar, inputs):
    u = freeze(tmp_path, calendar, inputs, months=("2022-04", "2022-05"))
    assert [r["security_id"] for r in query(u)["members"]] == ["synthetic:00000", "synthetic:00001"]
    assert candidate(u)["liquidity_score"] == "10000"
    assert u.snapshots[0]["effective_start"] == "2022-05-02" and u.snapshots[0]["effective_end"] == "2022-06-01"
    assert query(u, "2022-04-29", "2022-04-29T23:00:00Z")["status"] == "UNAVAILABLE"
    assert u.changes[1]["entrants"] == [] and len(u.changes[1]["persisting"]) == 2
    assert query(u) == query(u)
    assert query(u)["pit_quality"] == "PIT_RECONSTRUCTED"


def test_median_not_mean_uses_exact_last_60_sessions(tmp_path, calendar, inputs):
    for r in inputs[1]:
        if r["security_id"] == "synthetic:00001": r["volume"] = "2000"
        if r["security_id"] == "synthetic:00000" and r["session_date"] == "2022-04-29": r["volume"] = "999999999"
    u = freeze(tmp_path, calendar, inputs)
    assert candidate(u)["liquidity_score"] == "10000"
    assert candidate(u, 1)["rank"] == 1


@pytest.mark.parametrize("field", ["close", "volume"])
def test_future_observations_do_not_change_earlier_membership(tmp_path, calendar, inputs, field):
    a = freeze(tmp_path, calendar, inputs, name="a")
    for row in inputs[1]:
        if row["session_date"] >= "2022-05-02":
            row[field] = "9999999"
            if field == "close": row["high"] = "99999999"
    b = freeze(tmp_path, calendar, inputs, name="b")
    def decisions(u):
        return [{k: c[k] for k in ("security_id", "liquidity_score", "rank", "selected", "rejection_reasons", "observation_cutoff")}
                for c in u.snapshots[0]["candidates"]]
    # Whole-capture provenance changes, but no future price or volume affects the decision.
    assert decisions(a) == decisions(b)


@pytest.mark.parametrize("value,eligible", [("4.99", False), ("5", True), ("5.01", True)])
def test_minimum_price_boundary(tmp_path, calendar, inputs, value, eligible):
    for r in inputs[1]:
        if r["security_id"] == "synthetic:00000": r.update(open=value, low=value, close=value)
    u = freeze(tmp_path, calendar, inputs)
    assert (not candidate(u)["rejection_reasons"]) == eligible


@pytest.mark.parametrize("security_type,eligible", [("COMMON", True), ("REIT_COMMON", True), ("ADR", False), ("BDC", False), ("SPAC_COMMON", False), ("SPAC_UNIT", False), ("ETF", False), ("PREFERRED", False)])
def test_explicit_type_policies(tmp_path, calendar, inputs, security_type, eligible):
    inputs[0]["records"][0]["security_type"] = security_type
    u = freeze(tmp_path, calendar, inputs)
    assert ("INELIGIBLE_SECURITY_TYPE" not in candidate(u)["rejection_reasons"]) == eligible


def test_missing_session_no_compressed_lookback_or_forward_fill(tmp_path, calendar, inputs):
    inputs[1][:] = [r for r in inputs[1] if not (r["security_id"] == "synthetic:00000" and r["session_date"] == "2022-03-01")]
    u = freeze(tmp_path, calendar, inputs)
    assert "MISSING_OR_UNAVAILABLE_EXPECTED_SESSIONS" in candidate(u)["rejection_reasons"]
    assert "2022-03-01" in u.panel.quality["securities"]["synthetic:00000"]["missing_sessions_within_materialized_span"]
    assert not any(r["session_date"] == "2022-03-01" for r in u.panel.observations("synthetic:00000"))


def test_recent_ipo_and_less_than_60_sessions(tmp_path, calendar, inputs):
    inputs[0]["records"][0].update(listing_start="2022-04-01", effective_from="2022-04-01", known_at="2022-04-01T00:00:00Z")
    u = freeze(tmp_path, calendar, inputs)
    assert "INSUFFICIENT_LISTED_HISTORY" in candidate(u)["rejection_reasons"]


def test_delayed_availability_and_reconstitution(tmp_path, calendar, inputs):
    for r in inputs[1]:
        if r["security_id"] == "synthetic:00000" and r["session_date"] == "2022-04-29":
            r.update(available_at="2022-05-02T15:00:00Z", known_at="2022-05-02T15:00:00Z")
    early = freeze(tmp_path, calendar, inputs, name="early")
    assert "MISSING_OR_UNAVAILABLE_EXPECTED_SESSIONS" in candidate(early)["rejection_reasons"]
    late = freeze(tmp_path, calendar, inputs, decisions={"2022-04": "2022-05-02T16:00:00Z"}, name="late")
    assert not candidate(late)["rejection_reasons"]
    assert late.snapshots[0]["effective_start"] == "2022-05-03"
    assert query(late)["status"] == "UNAVAILABLE"


def test_revised_historical_volume_retains_original_vintage(tmp_path, calendar, inputs):
    original = next(r for r in inputs[1] if r["security_id"] == "synthetic:00000" and r["session_date"] == "2022-04-29")
    inputs[1].append({**original, "revision": 2, "volume": "99999999", "known_at": "2022-06-10T12:00:00Z"})
    u = freeze(tmp_path, calendar, inputs)
    assert candidate(u)["liquidity_score"] == "10000"
    early = u.panel.rows_as_of("synthetic:00000", "2022-05-01T00:00:00Z")
    late = u.panel.rows_as_of("synthetic:00000", "2022-07-01T00:00:00Z")
    assert early[-1]["revision"] == 1
    assert next(r for r in late if r["session_date"] == "2022-04-29")["revision"] == 2
    assert u.panel.quality["securities"]["synthetic:00000"]["revised_sessions"] == 1


def test_unknown_bar_timing_is_not_invented(tmp_path, calendar, inputs):
    original = next(r for r in inputs[1] if r["security_id"] == "synthetic:00000" and r["session_date"] == "2022-04-29")
    original.update(available_at=None, known_at=None, availability_status="UNKNOWN")
    strict = freeze(tmp_path, calendar, inputs, name="strict")
    assert "MISSING_OR_UNAVAILABLE_EXPECTED_SESSIONS" in candidate(strict)["rejection_reasons"]
    definition = default_definition(2); definition["unknown_knowledge_policy"] = "RECONSTRUCT_EXPLICITLY"
    reconstructed = freeze(tmp_path, calendar, inputs, name="reconstructed", definition=definition)
    assert candidate(reconstructed)["selected"] and candidate(reconstructed)["pit_quality"] == "PIT_UNVERIFIED"
    assert next(r for r in reconstructed.panel.observations("synthetic:00000") if r["session_date"] == "2022-04-29")["known_at"] is None


def test_future_delisting_and_retrospective_index_or_action_do_not_rewrite_membership(tmp_path, calendar, inputs):
    a = freeze(tmp_path, calendar, inputs, name="a")
    initial = inputs[0]["records"][0]
    inputs[0]["records"].extend([{**initial, "revision": 2, "known_at": "2022-06-10T00:00:00Z", "effective_to": "2022-06-01"},
                                 {**initial, "fact_id": "delisted", "known_at": "2022-06-10T00:00:00Z", "effective_from": "2022-06-01", "listing_end": "2022-05-31", "trading_status": "DELISTED"}])
    inputs[0]["lifecycle_events"].extend([{"event_id": kind, "security_id": initial["security_id"], "event_type": kind,
        "known_at": "2022-06-10T00:00:00Z", "effective_date": "2022-03-01", "evidence_reference": "retrospective fixture", "terminal_value": None} for kind in ("INDEX_ADDITION", "SPLIT_CORRECTION", "DELISTING")])
    b = freeze(tmp_path, calendar, inputs, name="b")
    # Source hash changes, decisions and membership do not.
    assert [m["security_id"] for m in a.snapshots[0]["members"]] == [m["security_id"] for m in b.snapshots[0]["members"]]
    assert candidate(b)["selected"]
    assert not b.master.lifecycle_as_of(initial["security_id"], "2022-05-01T00:00:00Z")
    assert len(b.master.lifecycle_as_of(initial["security_id"], "2022-07-01T00:00:00Z")) == 3


@pytest.mark.parametrize("basis", ["SPLIT_ADJUSTED", "DIVIDEND_ADJUSTED", "TOTAL_RETURN", "VENDOR_UNVERIFIED"])
def test_adjusted_prices_preserved_without_execution_or_raw_liquidity_promotion(tmp_path, calendar, inputs, basis):
    for row in inputs[1]:
        if row["security_id"] == "synthetic:00000": row["price_basis"] = basis
    u = freeze(tmp_path, calendar, inputs)
    assert "UNADMITTED_LIQUIDITY_BASIS" in candidate(u)["rejection_reasons"]
    assert u.panel.observations("synthetic:00000")[0]["price_basis"] == basis
    assert u.manifest["execution_admission"] == "NOT_GRANTED"


@pytest.mark.parametrize("value,reason", [(None, "MISSING_VOLUME"), ("0", "NONPOSITIVE_VOLUME")])
def test_missing_or_zero_volume_reported(tmp_path, calendar, inputs, value, reason):
    next(r for r in inputs[1] if r["security_id"] == "synthetic:00000" and r["session_date"] == "2022-04-29")["volume"] = value
    u = freeze(tmp_path, calendar, inputs)
    assert reason in candidate(u)["rejection_reasons"]


@pytest.mark.parametrize("update", [{"high": "1"}, {"low": "99"}, {"close": "NaN"}, {"volume": "-1"}, {"volume": "1.2"}, {"available_at": "2022-01-01T00:00:00Z"}])
def test_invalid_ohlcv_or_completion_rejected(tmp_path, calendar, inputs, update):
    inputs[1][0].update(update)
    with pytest.raises(ValueError):
        freeze_panel([capture(tmp_path / "bad.json", inputs[1])], calendar, tmp_path / "panel")
    assert not (tmp_path / "panel" / "hashes.json").exists()


def test_duplicate_observations_and_unknown_correction_times_rejected(tmp_path, calendar, inputs):
    for revision, known_at, name in ((1, inputs[1][0]["known_at"], "duplicate"), (2, None, "unknown")):
        rows = inputs[1] + [{**inputs[1][0], "revision": revision, "known_at": known_at}]
        with pytest.raises(ValueError, match="duplicate source|unknown publication"):
            freeze_panel([capture(tmp_path / f"{name}.json", rows)], calendar, tmp_path / name)


def test_discontinuity_is_audit_not_synthetic_adjustment(tmp_path, calendar, inputs):
    inputs[1][1]["volume"] = "1000000"
    u = freeze(tmp_path, calendar, inputs)
    assert u.panel.quality["securities"]["synthetic:00000"]["volume_discontinuities"]
    assert u.panel.observations("synthetic:00000")[1]["volume"] == "1000000"


def test_immutable_reproducible_bundle_and_tampering(tmp_path, calendar, inputs):
    a = freeze(tmp_path, calendar, inputs, name="a")
    b = freeze(tmp_path, calendar, inputs, name="b")
    assert a.content_sha256 == b.content_sha256
    assert a.panel.content_sha256 == b.panel.content_sha256
    with pytest.raises(FileExistsError):
        build_universe(a.master.path, a.panel.path, a.definition, ["2022-04"], tmp_path / "a" / "universe")
    p = tmp_path / "a" / "universe" / "universe_manifest.json"
    p.write_bytes(p.read_bytes()+b" ")
    with pytest.raises(ValueError, match="hash mismatch"):
        HistoricalUniverse(p.parent, master=a.master.path, panel=a.panel.path)


def test_dependency_mismatch_and_declared_source_hash_mismatch(tmp_path, calendar, inputs):
    a = freeze(tmp_path, calendar, inputs, name="a")
    inputs[1][0]["volume"] = "2000"
    b = freeze(tmp_path, calendar, inputs, name="b")
    with pytest.raises(ValueError, match="dependency hash"):
        HistoricalUniverse(tmp_path / "a" / "universe", master=a.master.path, panel=b.panel.path)
    files, _ = read_bundle(a.master.path)
    manifest = json.loads(files["security_master_manifest.json"]); manifest["source_snapshot_sha256"] = "f"*64
    files["security_master_manifest.json"] = encode(manifest)
    write_bundle(tmp_path / "mismatch", files)
    with pytest.raises(ValueError, match="source hash"):
        SecurityMaster(tmp_path / "mismatch")


def test_partial_acquisition_immutable_resume_and_interruption(tmp_path, calendar, inputs):
    first, rest = inputs[1][:100], inputs[1][100:]
    accepted = capture(tmp_path / "accepted.json", first, status="PARTIAL", failure_codes=["BOUNDED_SYNTHETIC_INTERRUPTION"])
    freeze_panel([accepted], calendar, tmp_path / "v1")
    before = ResearchPanel(tmp_path / "v1")
    freeze_panel([capture(tmp_path / "rest.json", rest)], calendar, tmp_path / "v2", base=before.path)
    after = ResearchPanel(tmp_path / "v2")
    assert after.manifest["parent_panel_sha256"] == before.content_sha256
    for name, sha in before.hashes["files"].items():
        if name.startswith(("part-", "source-")): assert after.hashes["files"][name] == sha
    assert sum(q["observations"] for q in after.quality["securities"].values()) == len(inputs[1])
    assert after.quality["acquisition_failures"][0]["failure_codes"] == ["BOUNDED_SYNTHETIC_INTERRUPTION"]
    with pytest.raises(ValueError, match="already accepted"):
        freeze_panel([accepted], calendar, tmp_path / "duplicate", base=before.path)
    interrupted = tmp_path / "interrupted"; interrupted.mkdir(); (interrupted / "part-orphan").write_text("unfinished")
    with pytest.raises(FileNotFoundError): ResearchPanel(interrupted)
    with pytest.raises(FileExistsError): freeze_panel([], calendar, interrupted)


def test_failed_acquisition_retained_without_observations(tmp_path, calendar):
    freeze_panel([capture(tmp_path / "failed.json", [], status="FAILED", failure_codes=["NO_AUTHORIZED_PROVIDER"])], calendar, tmp_path / "panel")
    panel = ResearchPanel(tmp_path / "panel")
    assert panel.quality["row_count"] == 0 and panel.quality["acquisition_failures"]


def test_pit_verified_requires_documented_review_and_never_synthetic():
    source = {**synthetic_source(), "reviewed_pit_attestation": True, "vintage_evidence": "review", "availability_evidence": "pubclock"}
    assert source_quality(source) == "PIT_RECONSTRUCTED"
    source["origin"] = "RECORDED"
    assert source_quality(source) == "PIT_VERIFIED"
    del source["vintage_evidence"]
    assert source_quality(source) == "PIT_RECONSTRUCTED"
    del source["coverage_evidence"]
    assert source_quality(source) == "PIT_UNVERIFIED"


def test_absent_monthly_snapshot_expires_instead_of_carrying_forward(tmp_path, calendar, inputs):
    u = freeze(tmp_path, calendar, inputs, months=("2022-04", "2022-06"))
    assert query(u, "2022-06-15", "2022-06-15T09:20:00-04:00")["status"] == "UNAVAILABLE"


def test_full_month_and_next_open_must_be_in_frozen_calendar(tmp_path, calendar, inputs):
    with pytest.raises(ValueError, match="next eligible open"):
        freeze(tmp_path, calendar, inputs, months=("2022-08",))


def test_cli_offline_lifecycle(tmp_path, calendar, inputs, capsys):
    from equity_research.cli import main
    u = freeze(tmp_path, calendar, inputs)
    base = ["--bundle", str(tmp_path / "run" / "universe"), "--master", str(u.master.path), "--panel", str(u.panel.path)]
    assert main(["universe", "validate", *base]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "VALID"
    assert main(["universe", "members", *base, "--date", "2022-05-02", "--decision-timestamp", "2022-05-02T09:20:00-04:00"]) == 0
    assert len(json.loads(capsys.readouterr().out)["members"]) == 2
    assert main(["universe", "changes", *base]) == 0
    assert json.loads(capsys.readouterr().out)[0]["entrants"]
    assert main(["universe", "audit-master", "--master", str(u.master.path)]) == 0
    assert json.loads(capsys.readouterr().out)["security_count"] == 4


def test_single_security_existing_swing_and_outcomes_interfaces(tmp_path):
    from equity_research.universe.integration import single_security_inputs
    from equity_research.swing.engine import evaluate
    from equity_research.swing.model import Configuration as SwingConfig
    from equity_research.outcomes.model import Configuration as OutcomeConfig, measure
    cal = schedule("2021-06-01", "2022-08-31")
    inputs = (master_capture(2, hard_cases=False), [r for i in range(2) for r in price_rows(i, cal["sessions"])])
    u = freeze(tmp_path, cal, inputs)
    config, outcomes = SwingConfig(), OutcomeConfig()
    rows, schedule_, manifest = single_security_inputs(u, "synthetic:00001", "2022-05-02", "2022-05-02T09:20:00-04:00",
        price_cutoff_timestamp="2022-06-01T00:00:00Z", strategy_configuration_sha256=config.sha256,
        outcome_configuration_sha256=outcomes.sha256)
    result = evaluate(rows, schedule_, "S00001", "synthetic:00001", u.panel.content_sha256, config, start="2022-05-02", end="2022-05-31")
    assert result["signals"]
    signal = result["signals"][0]
    paths, _ = measure(signal, rows, schedule_, price_sha=u.panel.content_sha256, strategy_sha=config.sha256,
                       basis={"price_basis": "SYNTHETIC_RAW", "verified": False}, configuration=outcomes)
    assert len(paths) == 9 and manifest["admission"]["strict_execution_simulation"] == "NOT_ADMITTED"
    assert manifest["market_context_bundle_sha256"] is None


def test_bounded_batch_size(tmp_path, calendar, inputs):
    from equity_research.universe.panel import MAX_BATCH_ROWS
    with pytest.raises(ValueError, match="oversized"):
        freeze_panel([capture(tmp_path / "oversized.json", [inputs[1][0]]*(MAX_BATCH_ROWS+1))], calendar, tmp_path / "panel")


def test_delisting_does_not_remove_existing_membership_or_fabricate_prices(tmp_path, calendar, inputs):
    first = inputs[0]["records"][0]
    inputs[0]["records"].extend([{**first, "revision": 2, "effective_to": "2022-05-10", "known_at": "2022-05-10T12:00:00Z"},
        {**first, "fact_id": "ended", "effective_from": "2022-05-10", "known_at": "2022-05-10T12:00:00Z", "listing_end": "2022-05-09", "trading_status": "DELISTED"}])
    inputs[0]["lifecycle_events"] = [{"event_id": "end", "event_type": "DELISTING", "security_id": first["security_id"],
        "known_at": "2022-05-10T12:00:00Z", "effective_date": "2022-05-10", "evidence_reference": "synthetic", "terminal_value": None}]
    inputs[1][:] = [r for r in inputs[1] if r["security_id"] != first["security_id"] or r["session_date"] <= "2022-05-09"]
    u = freeze(tmp_path, calendar, inputs, months=("2022-04", "2022-05"))
    result = query(u, "2022-05-16", "2022-05-16T09:20:00-04:00")
    assert first["security_id"] in [m["security_id"] for m in result["members"]]
    assert result["lifecycle_diagnostics"][first["security_id"]][0]["terminal_value"] is None
    assert u.panel.observations(first["security_id"])[-1]["session_date"] == "2022-05-09"
    assert first["security_id"] in u.changes[1]["exits"]
    assert "LISTING_ENDED_AS_KNOWN" in candidate(u, index=1)["rejection_reasons"]


def test_partial_catalogue_or_unknown_candidate_evidence_cannot_verify_top_n(tmp_path, calendar, inputs):
    inputs[0]["records"][3]["known_at"] = None
    u = freeze(tmp_path, calendar, inputs)
    assert u.snapshots[0]["pit_quality"] == "PIT_UNVERIFIED"
    assert u.snapshots[0]["summary"]["incomplete_candidate_ranking_evidence"]


def test_conflicting_master_identity_requires_resolution(tmp_path):
    value = master_capture(2, hard_cases=False)
    value["records"].append({**value["records"][0], "fact_id": "conflict", "symbol": "OTHER"})
    path = tmp_path / "source.json"; path.write_bytes(encode(value))
    import_master(path, tmp_path / "master")
    with pytest.raises(ValueError, match="ambiguous effective"):
        SecurityMaster(tmp_path / "master").as_of("synthetic:00000", "2022-01-03", "2022-01-04T00:00:00Z")


def test_large_panel_1000_stable_id_partitions_and_projection(tmp_path):
    from equity_research.universe.synthetic import write_fixture_inputs
    cal = schedule("2022-01-01", "2022-07-31")
    master, captures = write_fixture_inputs(tmp_path / "inputs", cal, 1000, windows=[("2022-01-01", "2022-04-29")], hard_cases=False)
    import_master(master, tmp_path / "master")
    freeze_panel(captures, cal, tmp_path / "panel")
    panel = ResearchPanel(tmp_path / "panel")
    assert panel.quality["security_count"] == 1000
    build_universe(tmp_path / "master", panel.path, default_definition(1000), ["2022-04"], tmp_path / "universe")
    u = HistoricalUniverse(tmp_path / "universe", master=tmp_path / "master", panel=panel.path)
    assert len(query(u)["members"]) == 1000
    assert len(panel.observations("synthetic:00999", start="2022-04-28", end="2022-04-29")) == 2
    assert len(panel.index) == 1000


def test_unknown_master_fields_retained_in_inventory_and_excluded(tmp_path, calendar, inputs):
    inputs[0]["records"][0].update(issuer_id=None, provider_security_id=None, listing_start=None, security_type=None, identity_evidence=None)
    u = freeze(tmp_path, calendar, inputs)
    assert u.master.quality["security_count"] == 4 and u.master.quality["incomplete_identity_assertions"] == 1
    assert "INCOMPLETE_IDENTITY_OR_CLASSIFICATION" in candidate(u)["rejection_reasons"]
    assert u.snapshots[0]["pit_quality"] == "PIT_UNVERIFIED"


def test_recent_transfer_from_otc_does_not_invent_60_eligible_sessions(tmp_path, calendar, inputs):
    initial = inputs[0]["records"][0]
    initial.update(exchange="OTC", effective_to="2022-04-01")
    inputs[0]["records"].append({**initial, "fact_id": "transfer", "effective_from": "2022-04-01", "effective_to": None,
                                  "known_at": "2022-03-31T00:00:00Z", "exchange": "XNYS"})
    u = freeze(tmp_path, calendar, inputs)
    assert "INSUFFICIENT_ELIGIBLE_SESSION_HISTORY" in candidate(u)["rejection_reasons"]


def test_exact_clock_cutoff_and_very_late_monthly_decision(tmp_path, calendar, inputs):
    row = next(r for r in inputs[1] if r["security_id"] == "synthetic:00000" and r["session_date"] == "2022-04-29")
    row.update(available_at="2022-04-29T22:00:00Z", known_at="2022-04-29T22:00:00Z")
    u = freeze(tmp_path, calendar, inputs)
    assert "MISSING_OR_UNAVAILABLE_EXPECTED_SESSIONS" in candidate(u)["rejection_reasons"]
    assert query(u, "2023-01-03", "2023-01-03T09:20:00-05:00")["reason"] == "OUTSIDE_FROZEN_CALENDAR"
    with pytest.raises(ValueError, match="after next scheduled"):
        freeze(tmp_path, calendar, inputs, name="too_late", decisions={"2022-04": "2022-06-10T12:00:00Z"})
