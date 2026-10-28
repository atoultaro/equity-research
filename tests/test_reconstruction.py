"""Small synthetic inference fixtures. No broker, fetching or actual fills."""

from copy import deepcopy
import json

import pytest

from equity_research.comprehension.inputs import PRICE_BASIS, VOLUME_BASIS
from equity_research.events.model import freeze_events
from equity_research.ingestion.calendar import schedule
from equity_research.ingestion.storage import encode, read_bundle, write_bundle
from equity_research.management.study import freeze_study as freeze_management
from equity_research.reconstruction.admission import Evidence, admit, risk_geometry
from equity_research.reconstruction.analysis import derive, rank
from equity_research.reconstruction.basis import split_diagnostics, undo_known_split_component
from equity_research.reconstruction.entries import candidates
from equity_research.reconstruction.management import trajectory
from equity_research.reconstruction.study import freeze_inputs, freeze_study, load_study
from equity_research.reconstruction.timing import bounds, clock_variants
from test_events import event, source
from test_lifecycle import alerts_fixture, frozen as lifecycle_inputs
from test_management import captured


def toy(direction="LONG", stop=95, extra=()):
    added = {"event_id": "open", "type": "OPEN_NEW_POSITION", "stop": str(stop),
        "published_at": "2026-10-18T15:20:00-04:00", "source": {"alert_id": "a"}}
    trade = {"trade_id": "TOY-001", "symbol": "TOY", "direction": direction,
        "initial_stop": str(stop), "position_state": "OPEN", "setup_availability": "ENTERABLE",
        "events": [added]+list(extra)}
    clock = {"assumed_action_clocks": {"a": added["published_at"],
        **{e["source"]["alert_id"]: e["published_at"] for e in extra}}}
    return trade, clock


def plan(kind="OPEN", entry=100, stop=95, direction="LONG"):
    cal = schedule("2026-10-19", "2026-10-20")
    return {"candidate_id": "hypothesis", "status": "CONSTRUCTED", "hypothesis": "TEST",
        "entry_price": entry, "geometry": risk_geometry(direction, entry, stop, 2),
        "entry_kind": kind, "entry_at": cal["sessions"][0]["opens_at"] if kind == "OPEN" else
            cal["sessions"][0]["closes_at"] if kind == "CLOSE" else None,
        "entry_session": "2026-10-19", "construction_support": 2,
        "entry_time_interval": [cal["sessions"][0]["opens_at"], cal["sessions"][0]["closes_at"]]}


def run_path(bars, *, direction="LONG", stop=95, kind="OPEN", policy="HOLD_WITH_REPORTED_STOPS", extra=(), entry=100):
    trade, clock = toy(direction, stop, extra)
    rows = {d: dict(zip(("open", "high", "low", "close"), (str(v) for v in prices))) for d, prices in bars}
    return trajectory(trade, plan(kind, entry, stop, direction), clock, rows,
        schedule("2026-10-19", bars[-1][0]), bars[-1][0]+"T18:30:00-04:00", policy)


def revision(new, old, when="2026-10-19T18:00:00-04:00", kind="STOP_CHANGED"):
    return {"event_id": "revision", "type": kind, "stop": str(new), "previous_stop": str(old),
        "published_at": when, "source": {"alert_id": "b"}}


def test_publication_bracket_unknown_is_not_replaced():
    alerts = alerts_fixture()["alerts"]
    original = deepcopy(alerts)
    b = bounds(alerts)["alert-6"]
    assert b["published_at"] is None and b["lower"].startswith("2026-10-22T22:28")
    assert b["upper"].startswith("2026-10-25T12:57:45")
    clocks = clock_variants(alerts, schedule("2026-10-01", "2026-10-30"))
    assert {c["weekly_first_session"] for c in clocks} == {"2026-10-23"}
    assert {c["weekly_late_session"] for c in clocks} == {"2026-10-26"}
    assert alerts == original
    alerts[5]["email_received_at"] = "2026-10-21T12:00:00Z"
    with pytest.raises(ValueError, match="inconsistent publication"):
        bounds(alerts)


@pytest.mark.parametrize("direction,stop,bar", [("LONG", 95, (100, 107, 94, 101)), ("SHORT", 105, (100, 106, 93, 99))])
def test_stop_target_ordering_retains_both_outcomes(direction, stop, bar):
    r = run_path([("2026-10-19", bar)], direction=direction, stop=stop, policy="FULL_EXIT_AT_1R")
    assert {s["closed_reason"] for s in r["terminal_possibilities"]} == {"HYPOTHETICAL_STOP_TOUCH", "HYPOTHETICAL_FULL_1R"}
    assert r["actual_fills"] is r["actual_realized_pnl"] is None


def test_close_entry_cannot_use_earlier_stop_or_target_extrema():
    r = run_path([("2026-10-19", (100, 110, 90, 100))], kind="CLOSE", policy="FULL_EXIT_AT_1R")
    assert all(s["remaining"] == 1 and not s["target_seen"] for s in r["terminal_possibilities"])


def test_confirmation_entry_ignores_pre_entry_low_but_retains_ordering_uncertainty():
    r = run_path([("2026-10-19", (98, 102, 94, 101))], kind="CONFIRMATION")
    assert {s["remaining"] for s in r["terminal_possibilities"]} == {0, 1}
    assert r["observations"][-1]["status"] == "PATH_DEPENDENT_COMPATIBILITY"


def test_later_revision_never_rescues_hard_stop_or_infers_reentry():
    r = run_path([("2026-10-19", (121.24, 121.61, 117.87, 118.62)),
                  ("2026-10-20", (122, 130, 121, 129))], stop=119.2, entry=121.24, extra=[revision(117.5, 119.2)])
    assert len(r["terminal_possibilities"]) == 1
    assert r["terminal_possibilities"][0]["closed_session"] == "2026-10-19"
    assert r["terminal_possibilities"][0]["remaining"] == 0
    assert r["active_source_stop_at_cutoff"] == 117.5
    assert r["original_reference_R"] == pytest.approx(2.04) and r["no_reentry"]
    assert all(o["status"] == "CONTINUATION_CONFLICT" for o in r["observations"])


def test_deferred_review_is_separate_pending_convention_not_retroactive_hard_stop():
    r = run_path([("2026-10-19", (121.24, 121.61, 117.87, 118.62))], stop=119.2,
        entry=121.24, extra=[revision(117.5, 119.2)], policy="CLOSE_REVIEW_NEXT_OPEN")
    assert r["pending_review_at_end"] and r["terminal_possibilities"][0]["remaining"] == 1
    assert r["conflict_alert_clusters"] == [] and r["active_source_stop_at_cutoff"] == 117.5


def test_cde_1r_full_exit_conflicts_partial_and_hold_preserve_runner():
    bars = [("2026-10-19", (15.46, 15.59, 15.265, 15.33)), ("2026-10-20", (14.51, 14.51, 13.78, 13.88))]
    event = revision(14.3, 16.4, "2026-10-20T18:00:00-04:00")
    for policy, remaining in (("FULL_EXIT_AT_1R", 0), ("PARTIAL_50_AT_1R", .5), ("HOLD_WITH_REPORTED_STOPS", 1)):
        r = run_path(bars, direction="SHORT", stop=16.4, entry=15.46, extra=[event], policy=policy)
        assert {s["remaining"] for s in r["terminal_possibilities"]} == {remaining}
        assert bool(r["conflict_alert_clusters"]) == (remaining == 0)
        assert r["source_position_status"] == "OPEN"


def test_missing_required_session_is_unresolved_and_cannot_rank():
    r = run_path([("2026-10-19", (100, 102, 98, 101)), ("2026-10-21", (101, 103, 99, 102))])
    assert r["missing_sessions"] == ["2026-10-20"] and not r["rank_eligible"]
    assert r["observations"][-1]["status"] == "UNRESOLVED_MISSING_PRICE_PATH"


def test_source_drop_before_candidate_entry_prevents_fictitious_fill():
    event = revision(95, 95, "2026-10-18T18:00:00-04:00", "DROPPED")
    r = run_path([("2026-10-19", (100, 102, 98, 101))], extra=[event])
    assert not r["rank_eligible"] and not r["terminal_possibilities"][0]["entered"]


def test_entry_construction_causal_and_known_close_before_publication_rejected(captured):
    parent, inputs = captured[2], deepcopy(captured[3])
    trade = next(t for t in parent["source_trade_lifecycles.json"] if t["symbol"] == "AAPL")
    clock = clock_variants(inputs[1]["alerts"], inputs[4])[1]
    evidence = Evidence(inputs[2], inputs[3], inputs[4], inputs[0]["analysis_cutoff"])
    before = candidates(trade, evidence, clock)
    assert before[1]["status"] == "REJECTED"
    assert before[0]["entry_session"] == "2026-10-19"
    for row in inputs[2]["AAPL"]:
        if row["session_date"] >= "2026-10-19":
            row.update(open="500", high="510", low="490", close="505")
    changed = candidates(trade, Evidence(inputs[2], inputs[3], inputs[4], inputs[0]["analysis_cutoff"]), clock)
    assert [p["construction"] for p in before] == [p["construction"] for p in changed]
    assert all(p["construction"]["subsequent_actions_used"] is False for p in before)
    invalid = deepcopy(trade);invalid["initial_stop"] = "99999"
    assert candidates(invalid, evidence, clock)[0]["status"] == "REJECTED"


def test_activation_stop_and_atr_known_before_entry_not_later_revisions(captured):
    inputs = captured[3]
    trade = deepcopy(captured[2]["source_trade_lifecycles.json"][0])
    clock = clock_variants(inputs[1]["alerts"], inputs[4])[1]
    ev = Evidence(inputs[2], inputs[3], inputs[4], inputs[0]["analysis_cutoff"])
    h1 = candidates(trade, ev, clock)[0]
    assert h1["reported_stop_at_entry"] == float(trade["initial_stop"])
    assert h1["entry_activation_evidence"]["known_stop_revision_ids"] == []
    assert h1["entry_activation_evidence"]["last_available_session"] == "2026-10-16"
    assert h1["geometry"]["reference_risk"] == float(h1["entry_price"])-float(trade["initial_stop"])


def test_future_bars_excluded_before_validation_and_trigger_search(captured):
    inputs = deepcopy(captured[3]); symbol = "SAIL"
    row = deepcopy(inputs[2][symbol][-1]);row.update(session_date="2026-10-27", open="invalid", high="nan")
    inputs[2][symbol].append(row)
    ev = Evidence(inputs[2], inputs[3], inputs[4], inputs[0]["analysis_cutoff"])
    assert "2026-10-27" not in ev.rows(symbol)
    trade = next(t for t in captured[2]["source_trade_lifecycles.json"] if t["symbol"] == symbol)
    plans = candidates(trade, ev, clock_variants(inputs[1]["alerts"], inputs[4])[1])
    assert all(p["status"] != "CONSTRUCTED" for p in plans)


@pytest.mark.parametrize("corruption", ["identity", "duplicate_identity", "ohlc", "duplicate_session"])
def test_exploratory_does_not_admit_inconsistent_data(captured, corruption):
    inputs = deepcopy(captured[3])
    if corruption == "identity":
        inputs[3]["AAPL"]["contract"]["conId"] = "unknown"
    elif corruption == "duplicate_identity":
        inputs[3]["AAPL"]["contract"]["conId"] = inputs[3]["CLMT"]["contract"]["conId"]
    elif corruption == "ohlc":
        inputs[2]["AAPL"][0]["high"] = "1"
    else:
        inputs[2]["AAPL"].append(deepcopy(inputs[2]["AAPL"][0]))
    with pytest.raises(ValueError):
        Evidence(inputs[2], inputs[3], inputs[4], inputs[0]["analysis_cutoff"])


def test_scale_sensitivity_validates_provenance_preserves_volume_and_shared_atr(captured):
    inputs = captured[3]; original = deepcopy(inputs[2])
    ev = Evidence(inputs[2], inputs[3], inputs[4], inputs[0]["analysis_cutoff"])
    scale = {"AAPL": {"factor": "2", "evidence_reference": "Synthetic uniform sensitivity", "status": "ASSUMED_RELATIVE_SCALE", "raw_price_claim": False}}
    scaled = Evidence(inputs[2], inputs[3], inputs[4], inputs[0]["analysis_cutoff"], scale)
    cutoff = "2026-10-18T15:20:00-04:00"
    f, g = ev.features("AAPL", cutoff)[1], scaled.features("AAPL", cutoff)[1]
    assert g["atr14"]["value"] == pytest.approx(2*f["atr14"]["value"])
    assert g["volume_native"]["value"] == f["volume_native"]["value"]
    assert g["atr14"]["attribution"] == "CONDITIONAL_DERIVED_PRICE_VIEW"
    t = deepcopy(captured[2]["source_trade_lifecycles.json"][0])
    clock = clock_variants(inputs[1]["alerts"], inputs[4])[1]
    p = candidates(t, scaled, clock)[0]
    assert p["price_basis"] == "EXPLICIT_DERIVED_UNVERIFIED" and p["construction"]["native_ATR14"] is None
    a = risk_geometry("LONG", 110, 100, f["atr14"]["value"])
    b = risk_geometry("LONG", 220, 200, g["atr14"]["value"])
    assert a["reference_risk_ATR"] == b["reference_risk_ATR"]
    assert inputs[2] == original and scaled.admission["historical_population_eligibility"] == "NOT_CLAIMED"
    scale["AAPL"]["raw_price_claim"] = True
    with pytest.raises(ValueError, match="uncertainty provenance"):
        Evidence(inputs[2], inputs[3], inputs[4], inputs[0]["analysis_cutoff"], scale)
    scale["AAPL"].update(raw_price_claim=False, factor="1e10000")
    with pytest.raises(ValueError, match="uncertainty provenance"):
        Evidence(inputs[2], inputs[3], inputs[4], inputs[0]["analysis_cutoff"], scale)
    with pytest.raises(ValueError, match="explicit EXPLORATORY"):
        admit(inputs[2], inputs[3], inputs[4], inputs[0]["analysis_cutoff"], mode="STRICT_UNIVERSE")


def test_split_component_is_not_fabricated_raw_volume_or_nominal_history():
    calendar = schedule("2020-08-20", "2020-09-09")
    rows = [{"session_date": s["session_date"], "open": "100", "high": "102", "low": "99", "close": "100",
        "volume": "2000", "price_basis": PRICE_BASIS, "volume_basis": VOLUME_BASIS} for s in calendar["sessions"]]
    original = deepcopy(rows)
    e = event("SPLIT", day="2020-08-20", effective="2020-08-31")
    r = split_diagnostics({"AAPL": rows}, [{"symbol": "AAPL", "event": e}], calendar)[0]
    assert r["native_post_open_over_pre_close"] == 1
    assert r["known_component_undone_post_open_over_pre_close"] == .25
    assert not r["raw_price_claim"] and not r["raw_volume_claim"]
    assert {x["volume"] for x in r["derived_view"]} == {"2000"} and rows == original
    with pytest.raises(ValueError, match="positive documented"):
        undo_known_split_component(rows, "2020-08-31", "NaN")


def test_ohlc_entry_range_does_not_promote_nonprotective_risk_to_admissible_fill():
    r = risk_geometry("LONG", 100, 95, 2, [90, 100])
    assert r["ohlc_compatible_risk_range"] == [-5, 5]
    assert r["positive_protective_risk_ATR_range"] == [0, 2.5]
    assert r["zero_lower_bound_is_excluded"] and r["nonpositive_risk_price_references_rejected"]
    assert risk_geometry("SHORT", 110, 105, 2, [108, 112])["positive_protective_risk_range"] is None


def test_ranking_uses_behavior_and_simplicity_not_profit_and_retains_equivalence():
    p = plan();p["hypothesis"] = "H1"
    def s(policy, vector, pnl):
        return {"policy": policy, "evaluation_vector": vector, "rank_eligible": True,
            "observations": [{"event_id": "later", "status": "ACTIVE_COMPATIBLE"}],
            "pending_review_at_end": False, "compatible_alert_clusters": ["later"], "conflict_alert_clusters": [],
            "irrelevant_profit": pnl}
    p["management"] = [s("SIMPLE", [0, -1, 0, -2], -999), s("COMPLEX", [0, -1, 2, -2], 999)]
    result = rank([p])
    assert [s["policy"] for s in result["leading"]] == ["SIMPLE"]
    assert len(result["observational_equivalence_classes"]) == 1
    assert result["ranking_identifies_actual_execution"] is False


def test_full_inventory_source_separation_and_determinism(captured):
    parent, inputs = deepcopy(captured[2]), captured[3]
    original = deepcopy(parent)
    config = {"trigger_valid_sessions": 3}
    first = derive(parent, inputs, config)
    assert encode(first) == encode(derive(parent, inputs, config))
    assert len(first["episodes.json"]) == 26 and parent == original
    cde = next(e["source"] for e in first["episodes.json"] if e["symbol"] == "CDE")
    ebay = next(e["source"] for e in first["episodes.json"] if e["symbol"] == "EBAY")
    assert (cde["direction"], cde["position_state"], cde["setup_availability"], cde["current_stop"]) == ("SHORT", "OPEN", "UNDERWAY", "13.90")
    assert (ebay["direction"], ebay["position_state"], ebay["setup_availability"], ebay["current_stop"]) == ("LONG", "OPEN", "ENTERABLE", "117.50")
    assert all(e["actual_entry_price"] is e["actual_exit_reason"] is e["actual_realized_pnl"] is None for e in first["episodes.json"])


def test_frozen_replay_semantics_rejects_resealed_tamper_offline(captured, lifecycle_inputs, tmp_path, monkeypatch):
    import socket
    monkeypatch.setattr(socket.socket, "connect", lambda *a, **k: pytest.fail("network attempted"))
    parent = tmp_path / "pr17"
    seal = freeze_management(captured[0] / "parent", captured[4], parent)
    split = event("SPLIT", day="2020-08-20", effective="2020-08-31")
    event_seal = freeze_events([split], [source([split])], tmp_path / "split")
    report = lifecycle_inputs[0] / "audit-report-0"
    config = {"schema_version": "grimes_reconstruction_config_v1", "mode": "EXPLORATORY_RECONSTRUCTION",
        "parent_pr17_sha256": seal["bundle_sha256"], "trigger_valid_sessions": 3, "fit_parameters_to_profit": False,
        "inspected_main_commit": "0"*40, "split_price_source": str(report),
        "split_price_source_sha256": read_bundle(report)[1]["bundle_sha256"],
        "split_events": {"AAPL": {"path": str(tmp_path / "split"), "bundle_sha256": event_seal["bundle_sha256"], "event_id": split["event_id"]}}}
    freeze_inputs(parent, config, tmp_path / "inputs")
    before = read_bundle(parent)
    frozen = freeze_study(tmp_path / "inputs", tmp_path / "study")
    replayed = load_study(tmp_path / "study")
    assert frozen == replayed["hashes"] and read_bundle(parent) == before
    files = replayed["files"]
    episodes = json.loads(files["episodes.json"]);episodes[0]["actual_entry_price"] = 123
    files["episodes.json"] = encode(episodes)
    write_bundle(tmp_path / "forged", files)
    with pytest.raises(ValueError, match="semantic output mismatch"):
        load_study(tmp_path / "forged")
    with pytest.raises(FileExistsError):
        freeze_study(tmp_path / "inputs", tmp_path / "study")
