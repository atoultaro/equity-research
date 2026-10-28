"""Focused aggregation/ranking tests; inherited paths are never redesigned."""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from equity_research.ingestion.storage import encode, read_bundle, write_bundle
from equity_research.reconstruction.analysis import rank
from equity_research.reconstruction.management import COMPLEXITY, POLICIES
import equity_research.reconstruction_sensitivity as sensitivity


def scenario(policy, statuses, *, eligible=True):
    observations = [{"event_id": f"event-{i}", "alert_id": alert, "status": status,
        "final_source_state_check": final} for i, (alert, status, final) in enumerate(statuses)]
    conflicts = sorted({a for a, s, _ in statuses if s == "CONTINUATION_CONFLICT"})
    support = sorted({a for a, s, final in statuses if s == "ACTIVE_COMPATIBLE" and not final})
    return {"policy": policy, "rank_eligible": eligible, "observations": observations,
        "evaluation_vector": [len(conflicts), -len(support), COMPLEXITY[policy], -2],
        "conflict_alert_clusters": conflicts, "compatible_alert_clusters": support, "pending_review_at_end": False}


def episode(symbol="TEST", statuses=(("alert", "ACTIVE_COMPATIBLE", False),), *, eligible=True):
    plan = {"candidate_id": symbol+":H1", "hypothesis": "H1_NEXT_OPEN", "entry_session": "2026-10-19",
        "entry_price": 100, "entry_kind": "OPEN", "geometry": {"reference_risk_ATR": 1},
        "management": [scenario(p, statuses, eligible=eligible) for p in POLICIES]}
    clock = {"clock_variant": sensitivity.BASELINE, "candidates": [plan]}
    clock.update(rank(clock["candidates"]))
    return {"trade_id": symbol+"-001", "symbol": symbol, "clock_comparisons": [clock],
        "source": {"direction": "LONG", "position_state": "OPEN", "setup_availability": "ENTERABLE", "current_stop": "95"}}


def test_co_published_actions_are_one_cluster_and_final_open_is_not_an_alert():
    s = scenario(POLICIES[0], [("same-alert", "CONTINUATION_CONFLICT", False),
        ("same-alert", "CONTINUATION_CONFLICT", False), ("FINAL_SOURCE_OPEN", "CONTINUATION_CONFLICT", True)])
    r = sensitivity.assess(s)
    assert r["later_alert_clusters"] == r["robust_conflict_alert_clusters"] == 1
    assert r["final_source_state_conflict"] and len(r["clusters"]) == 2
    s["observations"].pop(1)
    assert sensitivity.signature(sensitivity.clusters(s)) == sensitivity.signature(r["clusters"])


@pytest.mark.parametrize("status,expected", [("ACTIVE_COMPATIBLE", "FULLY_COMPATIBLE"),
    ("CONTINUATION_CONFLICT", "ROBUST_CONFLICT"), ("PATH_DEPENDENT_COMPATIBILITY", "PATH_DEPENDENT"),
    ("DROP_AFTER_MODEL_EXIT_CAUSE_UNRESOLVED", "UNRESOLVED"),
    ("ENTRY_NOT_YET_OBSERVED_NOT_PROOF_NO_TRADE", "UNRESOLVED")])
def test_distinguish_compatibility_conflict_paths_and_unresolved_drop(status, expected):
    assert sensitivity.assess(scenario(POLICIES[0], [("alert", status, False)]))["category"] == expected


def test_no_later_alerts_are_not_management_confirmation_or_full_equivalence():
    e = episode(statuses=[("FINAL_SOURCE_OPEN", "ACTIVE_COMPATIBLE", True)])
    r = sensitivity.analyze([e])["clocks"][0]["episodes"][0]
    for policy in r["policies"].values():
        assert policy["category"] == "NO_LATER_SOURCE_ALERTS"
        assert policy["cross_policy_equivalent_final_state_only"]
        assert not policy["cross_policy_equivalent_with_later_alerts"]


def test_same_conflict_signature_can_be_equivalently_wrong():
    e = episode(statuses=[("alert", "CONTINUATION_CONFLICT", False)])
    r = sensitivity.analyze([e])["clocks"][0]["episodes"][0]
    for policy in r["policies"].values():
        assert policy["category"] == "ROBUST_CONFLICT_ALL_ENTRIES"
        assert policy["cross_policy_equivalent_with_later_alerts"]
        assert not policy["cross_policy_equivalent_fully_compatible"]


def test_any_fit_and_all_conflict_are_not_cherry_picked_or_double_counted():
    e = episode(statuses=[("alert", "CONTINUATION_CONFLICT", False)])
    clock = e["clock_comparisons"][0]
    p = deepcopy(clock["candidates"][0]);p.update(candidate_id="TEST:H3", hypothesis="H3_CONFIRMATION")
    p["management"] = [scenario(policy, [("alert", "PATH_DEPENDENT_COMPATIBILITY", False)]) for policy in POLICIES]
    clock["candidates"].append(p);clock.update(rank(clock["candidates"]))
    r = sensitivity.analyze([e])["clocks"][0]["episodes"][0]
    assert all(v["category"] == "PATH_DEPENDENT_ONLY" and v["any_robust_conflicting_entry"] for v in r["policies"].values())
    p["management"] = [scenario(policy, [("alert", "ACTIVE_COMPATIBLE", False)]) for policy in POLICIES]
    clock.update(rank(clock["candidates"]))
    r = sensitivity.analyze([e])["clocks"][0]["episodes"][0]
    assert all(v["category"] == "FULLY_COMPATIBLE" for v in r["policies"].values())


def test_re_ranking_really_filters_deferred_review_and_preserves_input():
    e = episode();clock = e["clock_comparisons"][0]
    for s in clock["candidates"][0]["management"]:
        if s["policy"] != "CLOSE_REVIEW_NEXT_OPEN":
            s["evaluation_vector"] = [2, 0, COMPLEXITY[s["policy"]], -2]
    alt = deepcopy(clock["candidates"][0]);alt.update(candidate_id="TEST:H3", hypothesis="H3_CONFIRMATION")
    for s in alt["management"]:
        s["evaluation_vector"] = [0, 0, COMPLEXITY[s["policy"]], -1]
    clock["candidates"].append(alt);clock.update(rank(clock["candidates"]))
    before = deepcopy(e)
    r = sensitivity.analyze([e])["clocks"][0]["episodes"][0]
    assert r["leading_entry_set_changed"]
    assert {p["hypothesis"] for p in r["hard_stop_only_ranking"]["leading"]} == {"H3_CONFIRMATION"}
    assert all(p["policy"] != "CLOSE_REVIEW_NEXT_OPEN" for p in r["hard_stop_only_ranking"]["leading"])
    assert e == before


def test_public_frozen_26_episode_regression_and_source_status_separation():
    files, _ = read_bundle(Path(__file__).parents[1] / "docs/evidence/pr9a-reconstruction-v1")
    episodes = json.loads(files["episodes.json"]);original = deepcopy(episodes)
    r = sensitivity.analyze(episodes)
    assert r["observed_episode_count"] == 22 and r["source_episode_count"] == 26
    assert r["excluded_right_censored_symbols"] == ["SAIL", "SLB", "GE", "SCCO"]
    for c in r["clocks"]:
        assert c["changed_leading_entries"] == [] and c["changed_entry_ranks"] == []
        assert c["best_hard_stop_still_conflicts"] == ["CLMT", "TEVA", "GME", "EBAY"]
        for counts in c["policy_summary"].values():
            assert sum(len(counts[k]) for k in sensitivity.CATEGORIES) == 22
            assert counts["NO_LATER_SOURCE_ALERTS"] == ["ABBV", "CNQ", "MMM"]
        cde, ebay = (next(e for e in c["episodes"] if e["symbol"] == s) for s in ("CDE", "EBAY"))
        assert cde["source_status"] == {"direction": "SHORT", "position_state": "OPEN", "setup_availability": "UNDERWAY", "current_stop": "13.90"}
        assert ebay["source_status"] == {"direction": "LONG", "position_state": "OPEN", "setup_availability": "ENTERABLE", "current_stop": "117.50"}
        assert cde["policies"]["FULL_EXIT_AT_1R"]["category"] == "ROBUST_CONFLICT_ALL_ENTRIES"
        assert cde["policies"]["HOLD_WITH_REPORTED_STOPS"]["category"] == "FULLY_COMPATIBLE"
    late = next(c for c in r["clocks"] if c["clock_variant"] == sensitivity.BASELINE)
    assert [len(late["policy_summary"][p]["FULLY_COMPATIBLE"]) for p in POLICIES] == [6, 7, 7, 19]
    assert [len(late["policy_summary"][p]["ROBUST_CONFLICT_ALL_ENTRIES"]) for p in POLICIES] == [6, 4, 4, 0]
    assert encode(r) == encode(sensitivity.analyze(episodes)) and original == episodes


def test_frozen_new_layer_reproducible_and_resealed_tamper_rejected(tmp_path, monkeypatch):
    # Isolate the NEW reader/derivation here; the inherited PR19 semantic reader
    # has its own regressions and is exercised on actual frozen data by CLI replay.
    monkeypatch.setattr(sensitivity, "_parent", lambda files, hashes: json.loads(files["episodes.json"]))
    parent = tmp_path / "parent"
    write_bundle(parent, {"episodes.json": encode([episode()])})
    before = read_bundle(parent)
    seal = sensitivity.freeze(parent, tmp_path / "study")
    result = sensitivity.load(tmp_path / "study")
    assert result["hashes"] == seal and read_bundle(parent) == before
    assert write_bundle(tmp_path / "replay", result["files"]) == seal
    files = result["files"];r = json.loads(files["sensitivity.json"]);r["observed_episode_count"] = 999
    files["sensitivity.json"] = encode(r)
    write_bundle(tmp_path / "resealed", files)
    with pytest.raises(ValueError, match="semantic output mismatch"):
        sensitivity.load(tmp_path / "resealed")
    with pytest.raises(FileExistsError):
        sensitivity.freeze(parent, tmp_path / "study")


def test_undeclared_parent_and_unknown_status_rejected(tmp_path):
    files = {"episodes.json": encode([episode()])}
    seal = write_bundle(tmp_path / "parent", files)
    with pytest.raises(ValueError, match="declared immutable PR19"):
        sensitivity._parent(files, seal)
    with pytest.raises(ValueError, match="unknown source"):
        sensitivity.assess(scenario(POLICIES[0], [("alert", "INVENTED", False)]))
