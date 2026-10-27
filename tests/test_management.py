"""Offline empirical analysis: synthetic source/price evidence, no broker or network."""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from equity_research.cli import main
from equity_research.ingestion.storage import digest, encode, read_bundle, write_bundle
from equity_research.lifecycle.study import derive as lifecycle_derive, freeze_study as freeze_parent
from equity_research.lifecycle.study import read_inputs
from equity_research.management.analysis import Evidence, derive, excursions, validate_inventory
from equity_research.management.study import freeze_study, load_study
from test_lifecycle import frozen as lifecycle_inputs


@pytest.mark.parametrize("direction,rows,mfe,mae", [("LONG", [(105, 98, 102), (107, 99, 106)], 7, 2),
    ("SHORT", [(103, 95, 98), (101, 93, 94)], 7, 3)])
def test_directional_excursions_hand_calculated(direction, rows, mfe, mae):
    bars = [{"session_date": f"2026-10-{19+i}", "high": str(h), "low": str(l), "close": str(c)} for i, (h, l, c) in enumerate(rows)]
    r = excursions(bars, "100", direction, atr=2, original_r=5)
    assert r["mfe_price"] == mfe and r["mae_price"] == mae
    assert r["progress_price"] == r["progress_percent"] == 6
    assert r["progress_ATR"] == 3 and r["progress_original_R"] == 1.2
    scaled = [{**b, **{k: str(2*float(b[k])) for k in ("high", "low", "close")}} for b in bars]
    doubled = excursions(scaled, "200", direction, atr=4, original_r=10)
    assert doubled["progress_price"] == 12 and doubled["progress_percent"] == r["progress_percent"]
    assert doubled["mfe_price"] == 2*mfe and doubled["mae_price"] == 2*mae
    assert doubled["progress_original_R"] == r["progress_original_R"]
    assert excursions([], "100", direction) is None


@pytest.fixture(scope="module")
def captured(lifecycle_inputs, tmp_path_factory):
    root = tmp_path_factory.mktemp("management-parent")
    freeze_parent(lifecycle_inputs[0] / "inputs", root / "parent")
    files, seals = read_bundle(root / "parent")
    parsed = {k: json.loads(v) for k, v in files.items() if k.endswith(".json")}
    config = {"schema_version": "grimes_management_config_v1", "parent_bundle_sha256": seals["bundle_sha256"],
        "inspected_main_commit": "1"*40, "inspected_pr16_commit": "2"*40,
        "commentary_synopses": [{"alert_id": a["alert_id"], "synopsis": "Synthetic test commentary; no actual expert text"}
            for a in parsed["alerts.json"]["alerts"]]}
    return root, files, parsed, lifecycle_inputs[2], config


@pytest.fixture(scope="module")
def derived(captured):
    return derive(captured[2], captured[3])


def test_exact_universe_counts_and_every_observation_retained(derived):
    m = derived["manifest.json"]
    assert m["stock_count"] == len(derived["positions.json"]) == 26 and m["alert_count"] == 7
    assert m["source_event_counts"] == {"OPEN_NEW_POSITION": 26, "STOP_CHANGED": 27, "SETUP_CHANGED": 7, "DROPPED": 12}
    assert len(derived["decision_features.json"]) == 72
    assert {p["symbol"] for p in derived["positions.json"]}.isdisjoint({"PLTR", "PEP"})
    assert m["source_final_states"] == {"CLOSED": 12, "OPEN": 14}
    for r in derived["long_short.json"].values():
        assert r["reported_closure_rate"]["denominator"] == r["positions"]
        assert r["source_widening_revision_rate"]["denominator"] == r["source_stop_revisions"]


def test_direction_aware_stop_classification_source_facts(derived):
    stop = derived["stop_revisions.json"]
    assert sum(r["stop_change"] == "TIGHTENING" for r in stop) == 16
    assert sum(r["stop_change"] == "WIDENING" for r in stop) == 11
    assert [r["source_stop_change_percent"] for r in stop if r["symbol"] == "OMER"] == [pytest.approx(100*.15/17.2)]
    assert derived["long_short.json"]["LONG"]["source_widening_revision_rate"]["numerator"] == 10
    assert derived["long_short.json"]["SHORT"]["source_widening_revision_rate"]["numerator"] == 1


def test_same_alert_stop_is_not_known_before_underway(derived):
    aaoi = next(r for r in derived["underway_transitions.json"] if r["symbol"] == "AAOI")
    assert aaoi["stop_known_before_alert"] == "89.82"
    assert aaoi["latest_stop_in_source_sequence"] == "70.70"
    assert aaoi["source_setup_before"] == "ENTERABLE" and aaoi["source_setup_after"] == "UNDERWAY"


def test_intraday_price_availability_future_poison_and_no_future_exit_leak(captured):
    parent, inputs = deepcopy(captured[2]), deepcopy(captured[3])
    t = next(t for t in parent["source_trade_lifecycles.json"] if t["symbol"] == "CLMT")
    event = deepcopy(t["events"][1]);event["effective_at"] = "2026-10-19T12:00:00-04:00"
    before = Evidence(parent, inputs).row(t, event)
    assert before["last_available_session"] == "2026-10-16"
    for r in inputs[2]["CLMT"]:
        if r["session_date"] >= "2026-10-19":
            r.update(open="999", high="1001", low="900", close="1000")
    after = Evidence(parent, inputs).row(t, event)
    assert before == after
    # A final modeled exit after this historical cutoff is not current knowledge.
    model = next(m for m in parent["conditional_basis_trade_lifecycles.json"] if m["symbol"] == "CLMT")
    model["events"].append({"type": "MODELED_CLOSED", "session_date": "2026-10-26", "cause": "ASSUMED_STOP_TRIGGERED"})
    assert Evidence(parent, inputs).row(t, event) == after


def test_strict_before_clock_not_equal_bar_availability(captured):
    parent, inputs = captured[2], captured[3]
    t = next(t for t in parent["source_trade_lifecycles.json"] if t["symbol"] == "CLMT")
    event = deepcopy(t["events"][1]);event["effective_at"] = "2026-10-19T17:00:00-04:00"
    assert Evidence(parent, inputs).row(t, event)["last_available_session"] == "2026-10-16"


def test_opening_feature_cannot_contain_the_future_scenario_entry_or_risk(captured):
    parent, inputs = deepcopy(captured[2]), deepcopy(captured[3])
    trade = next(t for t in parent["source_trade_lifecycles.json"] if t["symbol"] == "CLMT")
    before = Evidence(parent, inputs).row(trade, trade["events"][0])
    assert before["conditional_path"]["entry"] is None and before["conditional_path"]["original_R"] is None
    for row in inputs[2]["CLMT"]:
        if row["session_date"] >= "2026-10-19":
            row.update(open="200", high="205", low="195", close="201")
    changed_parent = lifecycle_derive(*inputs)
    changed_trade = next(t for t in changed_parent["source_trade_lifecycles.json"] if t["symbol"] == "CLMT")
    assert Evidence(changed_parent, inputs).row(changed_trade, changed_trade["events"][0]) == before


def test_original_r_is_invariant_to_revision(derived):
    rows = [r for r in derived["stop_revisions.json"] if r["symbol"] == "CLMT"]
    assert len(rows) == 2
    assert {r["conditional_path"]["original_R"] for r in rows} == {"44.75"}
    assert all(r["conditional_path"]["current_progress"]["progress_original_R"] == pytest.approx(1/44.75) for r in rows)


def test_unverified_basis_keeps_primary_unavailable_conditional_explicit(captured):
    parent, inputs = deepcopy(captured[2]), deepcopy(captured[3])
    inputs[0]["basis_evidence"] = []
    r = next(r for r in derive(parent, inputs)["stop_revisions.json"] if r["symbol"] == "CLMT")
    assert r["primary_stop_comparison"] is None and r["primary_path"]["status"] == "UNVERIFIED_BASIS"
    assert r["conditional_stop_comparison"] is not None
    assert r["conditional_path"]["basis_interpretation"] == "CONDITIONAL_UNVERIFIED_STOP_UNITS"


def test_missing_active_session_never_forward_filled(captured):
    parent, inputs = deepcopy(captured[2]), deepcopy(captured[3])
    inputs[2]["CLMT"] = [r for r in inputs[2]["CLMT"] if r["session_date"] != "2026-10-19"]
    trade = next(t for t in parent["source_trade_lifecycles.json"] if t["symbol"] == "CLMT")
    path = Evidence(parent, inputs).path(trade, trade["events"][2]["effective_at"], conditional=True)
    assert path["status"] == "MISSING_EXPECTED_ENTRY_SESSION" and path["current_progress"] is None


def test_exit_day_prices_not_attributed_as_post_exit_progress(captured):
    inputs = deepcopy(captured[3])
    for r in inputs[2]["CLMT"]:
        if r["session_date"] == "2026-10-19":
            r.update(open="110", high="112", low="105", close="111")
        if r["session_date"] == "2026-10-20":
            r.update(open="110", high="150", low="50", close="140")
    parent = lifecycle_derive(*inputs)
    context = Evidence(parent, inputs)
    trade = next(t for t in parent["source_trade_lifecycles.json"] if t["symbol"] == "CLMT")
    row = context.row(trade, trade["events"][2])
    path = row["conditional_path"]
    assert path["status"] == "MODELED_CLOSED_BEFORE_DECISION" and path["current_progress"] is None
    assert path["pre_exit_or_active_path"]["last_session"] == "2026-10-19"
    assert path["pre_exit_or_active_path"]["mfe_price"] == 2


def test_ebay_conflict_has_no_complete_pre_exit_bar_or_reentry(captured):
    inputs = deepcopy(captured[3])
    for r in inputs[2]["EBAY"]:
        if r["session_date"] == "2026-10-26":
            r.update(open="121.24", high="121.61", low="117.87", close="118.62")
    parent = lifecycle_derive(*inputs)
    r = next(r for r in derive(parent, inputs)["stop_revisions.json"] if r["symbol"] == "EBAY")
    assert r["source_action"]["previous_stop"] == "119.20" and r["source_action"]["stop"] == "117.50"
    assert r["modeled_closed_before_source_decision"]["primary"] is True
    assert r["conditional_path"]["current_progress"] is None and r["conditional_path"]["pre_exit_or_active_path"] is None
    assert len([t for t in parent["source_trade_lifecycles.json"] if t["symbol"] == "EBAY"]) == 1


def test_source_closure_cutoff_not_final_study_and_no_reason_invention(captured, derived):
    inputs = deepcopy(captured[3])
    before = derived["closure_hypotheses.json"]
    # Prices after the CLMT source DROP cannot change that closure's feature row.
    for r in inputs[2]["CLMT"]:
        if r["session_date"] > "2026-10-21":
            r.update(open="500", high="550", low="450", close="510")
    after = derive(captured[2], inputs)["closure_hypotheses.json"]
    a, b = (next(r for r in seq if r["symbol"] == "CLMT") for seq in (before, after))
    assert a == b
    assert all(r["actual_exit_reason"] == "EXIT_REASON_UNRESOLVED" and r["actual_realized_PnL"] is None for r in before)


def test_weekly_date_remains_unresolved_and_duration_bracket_explicit(derived):
    snow = next(p for p in derived["positions.json"] if p["symbol"] == "SNOW")
    d = snow["duration"]
    assert d["source_open_publication"] is None and d["publication_based_session_range"] is None
    assert d["email_bound_scenario_eligible_sessions"] == 1
    assert d["conditional_ordered_publication_bracket_sessions"] == [1, 2]
    assert d["actual_holding_duration"] is None


def test_missing_weekly_clock_not_replaced_with_an_invented_date(captured):
    inputs = deepcopy(captured[3]);inputs[0]["allow_email_availability_bound"] = False
    parent = lifecycle_derive(*inputs)
    result = derive(parent, inputs)
    unknown = [r for r in result["decision_features.json"] if r["source_locator"]["alert_id"] == "alert-6"]
    assert all(r["source_published_at"] is None and r["decision_bound"] is None and r["native_features"] is None for r in unknown)
    ebay = next(r for r in result["stop_revisions.json"] if r["symbol"] == "EBAY")
    assert ebay["conditional_path"]["current_progress"] is None


def test_earlier_time_flags_are_not_promoted_to_post_exit_terminal_explanations(derived):
    for row in derived["closure_hypotheses.json"]:
        if row["conditional_path"]["current_progress"] is None:
            assert row["possible_time_stop"] is None
            assert row["terminal_time_hypothesis_status"] == "MODEL_CLOSED_OR_AMBIGUOUS_NO_TERMINAL_EXPOSURE"


def test_preexisting_pivot_excludes_level_only_confirmed_on_current_session(captured):
    from equity_research.ingestion.calendar import schedule
    inputs = list(deepcopy(captured[3]));inputs[4] = schedule("2026-06-01", "2026-11-09")
    for symbol, rows in inputs[2].items():
        template = rows[0]
        prefix = [{**template, "session_date": s["session_date"]} for s in inputs[4]["sessions"] if s["session_date"] < "2026-09-01"]
        inputs[2][symbol] = prefix+rows
    for row in inputs[2]["CLMT"]:
        if row["session_date"] == "2026-10-15":
            row["low"] = "80"
    context = Evidence(captured[2], inputs)
    trade = next(t for t in captured[2]["source_trade_lifecycles.json"] if t["symbol"] == "CLMT")
    result = context.row(trade, trade["events"][2])
    current_pivot = result["native_features"]["confirmed_swing_low"]["value"]
    assert current_pivot["confirmed_session"] == "2026-10-20"
    assert result["native_swing_distances"]["low"]["close_minus_level_price"] == 21
    assert result["native_swing_distances"]["low"]["close_vs_level_percent"] == pytest.approx(26.25)
    assert "high" in result["native_swing_distances"]
    assert result["conditional_stop_comparison"]["preexisting_protective_swing"] is None


def test_relationship_denominators_retain_every_counterexample_and_unusable_row(derived):
    for r in derived["relationships.json"]:
        assert len(r["support"])+len(r["counterexamples"])+len(r["unusable"]) == r["total_events"]
        assert r["support_rate"]["denominator"] == len(r["support"])+len(r["counterexamples"])


def test_matched_controls_use_only_available_source_states_and_no_post_exit_path(derived):
    for match in derived["matched_enterable_controls.json"]:
        target = next(r for r in derived["underway_transitions.json"] if r["event_id"] == match["transition_event_id"])
        assert match["candidate_count"] == 25
        for c in match["controls"]:
            if c["status"] == "ELIGIBLE_CONDITIONAL_COMPARATOR":
                from equity_research.events.model import timestamp
                assert timestamp(c["matched_bound"]) <= timestamp(target["decision_bound"])
                assert c["setup_at_matched_bound"] == "ENTERABLE" and not c["source_closed_at_matched_bound"]
                assert c["features"]["current_progress"] is not None
    # A later DROP does not retroactively exclude a valid earlier ENTERABLE observation.
    assert any(c["symbol"] == "CLMT" and c["status"] == "ELIGIBLE_CONDITIONAL_COMPARATOR"
        for r in derived["matched_enterable_controls.json"] for c in r["controls"])


def test_source_records_unchanged_and_inventory_rejects_scope_change(captured):
    parent = deepcopy(captured[2]);original = deepcopy(parent)
    derive(parent, captured[3])
    assert parent == original
    parent["source_trade_lifecycles.json"][0]["symbol"] = "PLTR"
    with pytest.raises(ValueError, match="exact frozen"):
        validate_inventory(parent)


def test_frozen_replay_offline_and_parent_bytes_preserved(captured, tmp_path, monkeypatch):
    import socket
    monkeypatch.setattr(socket.socket, "connect", lambda *a, **k: pytest.fail("network attempted"))
    parent = captured[0] / "parent"
    before = {p.name: digest(p.read_bytes()) for p in parent.iterdir()}
    seal = freeze_study(parent, captured[4], tmp_path / "study")
    assert load_study(tmp_path / "study")["hashes"] == seal
    assert main(["management", "replay", "--study", str(tmp_path / "study"), "--output", str(tmp_path / "replay")]) == 0
    assert read_bundle(tmp_path / "replay")[1] == seal
    assert {p.name: digest(p.read_bytes()) for p in parent.iterdir()} == before
    assert len(list((tmp_path / "study").glob("summary-*.md"))) == 26
    with pytest.raises(FileExistsError):
        freeze_study(parent, captured[4], tmp_path / "study")


@pytest.mark.parametrize("name", ["decision_features.json", "stop_revisions.json", "long_short.json"])
def test_resealed_inconsistent_outputs_rejected(captured, tmp_path, name):
    freeze_study(captured[0] / "parent", captured[4], tmp_path / "original")
    files, _ = read_bundle(tmp_path / "original")
    value = json.loads(files[name]);(value[0] if isinstance(value, list) else value)["invented"] = 999
    files[name] = encode(value)
    write_bundle(tmp_path / "resealed", files)
    with pytest.raises(ValueError, match="semantic output mismatch"):
        load_study(tmp_path / "resealed")


def test_resealed_parent_outputs_are_semantically_revalidated(captured, tmp_path):
    freeze_study(captured[0] / "parent", captured[4], tmp_path / "original")
    files, _ = read_bundle(tmp_path / "original")
    source = {k[7:]: v for k, v in files.items() if k.startswith("parent-") and k != "parent-hashes.json"}
    changed = json.loads(source["source_stop_history.json"]);changed[0]["reported_stop"] = "1.00"
    source["source_stop_history.json"] = encode(changed)
    forged = write_bundle(tmp_path / "forged-parent", source)
    files.update({"parent-"+k: v for k, v in source.items()})
    files["parent-hashes.json"] = encode(forged)
    config = json.loads(files["config.json"]);config["parent_bundle_sha256"] = forged["bundle_sha256"]
    files["config.json"] = encode(config)
    write_bundle(tmp_path / "resealed", files)
    with pytest.raises(ValueError, match="PR16 semantic parent mismatch"):
        load_study(tmp_path / "resealed")
