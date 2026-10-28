"""Policy sensitivity over PR19's unchanged, semantically verified reconstruction.

This is a read-only analysis of frozen scenarios, not another path simulator.
Keep this module outside reconstruction/ so its pinned v4 implementation identity
and historical replay remain unchanged.
"""

from collections import defaultdict
from copy import deepcopy
import json
from pathlib import Path

from .comprehension.inputs import _check_hashes
from .ingestion.storage import digest, encode, read_bundle, write_bundle
from .reconstruction.analysis import rank
from .reconstruction.management import POLICIES
from .reconstruction.study import _files as reconstruction_files

PARENT_SHA256 = "a1524b3f07d04bce4e5165ad3d6b3eccfa72ce32d41ca80ebbbf051725310315"
BASELINE = "LATE_EMAIL_BOUND"
HARD_STOP_POLICIES = POLICIES[:3]
CATEGORIES = ("FULLY_COMPATIBLE", "ROBUST_CONFLICT_ALL_ENTRIES", "PATH_DEPENDENT_ONLY",
              "OTHER_UNRESOLVED", "NO_LATER_SOURCE_ALERTS")
STATUSES = {"ACTIVE_COMPATIBLE", "CONTINUATION_CONFLICT", "PATH_DEPENDENT_COMPATIBILITY",
            "DROP_AFTER_MODEL_EXIT_CAUSE_UNRESOLVED", "ENTRY_NOT_YET_OBSERVED_NOT_PROOF_NO_TRADE",
            "UNRESOLVED_MISSING_PRICE_PATH"}


def clusters(scenario):
    grouped = defaultdict(lambda: {"statuses": set(), "event_ids": set()})
    for observation in scenario["observations"]:
        status = observation["status"]
        if status not in STATUSES:
            raise ValueError("unknown source-compatibility classification")
        key = observation["final_source_state_check"], observation["alert_id"]
        grouped[key]["statuses"].add(status)
        grouped[key]["event_ids"].add(observation["event_id"])
    return [{"alert_id": alert, "final_source_state_check": final,
        "statuses": sorted(values["statuses"]), "event_ids": sorted(values["event_ids"])}
        for (final, alert), values in sorted(grouped.items())]


def signature(grouped):
    # Multiple co-published actions never create multiple independent checks.
    return tuple((r["final_source_state_check"], r["alert_id"], tuple(r["statuses"])) for r in grouped)


def assess(scenario):
    grouped = clusters(scenario)
    statuses = {s for r in grouped for s in r["statuses"]}
    actual = [r for r in grouped if not r["final_source_state_check"]]
    conflict = "CONTINUATION_CONFLICT" in statuses
    path = "PATH_DEPENDENT_COMPATIBILITY" in statuses
    if conflict:
        category = "ROBUST_CONFLICT"
    elif path and statuses <= {"ACTIVE_COMPATIBLE", "PATH_DEPENDENT_COMPATIBILITY"}:
        category = "PATH_DEPENDENT"
    elif statuses == {"ACTIVE_COMPATIBLE"}:
        category = "FULLY_COMPATIBLE" if actual else "NO_LATER_SOURCE_ALERTS"
    else:
        category = "UNRESOLVED"
    return {"category": category, "clusters": grouped, "later_alert_clusters": len(actual),
        "robust_conflict_alert_clusters": sum("CONTINUATION_CONFLICT" in r["statuses"] for r in actual),
        "final_source_state_conflict": any(r["final_source_state_check"] and "CONTINUATION_CONFLICT" in r["statuses"] for r in grouped),
        "has_path_dependent_check": path}


def _plans(clock, policies):
    plans = deepcopy(clock["candidates"])
    for p in plans:
        p["management"] = [s for s in p["management"] if s["policy"] in policies]
    return plans


def rerank(clock, policies):
    plans = _plans(clock, policies)
    result = rank(plans)
    result["entry_ranks"] = [{"candidate_id": p["candidate_id"], "hypothesis": p["hypothesis"],
        "best_vector": min((s["evaluation_vector"] for s in p["management"] if s["rank_eligible"]), default=None)} for p in plans]
    # Rank entries against other entries' BEST policies. Ranking all scenario
    # vectors would let a discarded, nonleading policy create spurious rank gaps.
    vectors = sorted({tuple(p["best_vector"]) for p in result["entry_ranks"] if p["best_vector"] is not None})
    for p in result["entry_ranks"]:
        p["rank"] = 1+vectors.index(tuple(p["best_vector"])) if p["best_vector"] is not None else None
    return result


def episode_comparison(episode, clock):
    paths = [{"candidate_id": p["candidate_id"], "hypothesis": p["hypothesis"], "policy": s["policy"],
        **assess(s)} for p in clock["candidates"] for s in p["management"] if s["rank_eligible"]]
    equivalent = defaultdict(list)
    for p in paths:
        equivalent[signature(p["clusters"])].append(p)
    groups = [members for members in equivalent.values() if len({p["policy"] for p in members}) > 1]
    policies = {}
    for policy in POLICIES:
        selected = [p for p in paths if p["policy"] == policy]
        if not selected:
            raise ValueError("observed cohort must have comparable entries for every policy")
        categories = {p["category"] for p in selected}
        if "FULLY_COMPATIBLE" in categories:
            category = "FULLY_COMPATIBLE"
        elif categories == {"ROBUST_CONFLICT"}:
            category = "ROBUST_CONFLICT_ALL_ENTRIES"
        elif "PATH_DEPENDENT" in categories:
            category = "PATH_DEPENDENT_ONLY"
        elif categories == {"NO_LATER_SOURCE_ALERTS"}:
            category = "NO_LATER_SOURCE_ALERTS"
        else:
            category = "OTHER_UNRESOLVED"
        matched = [g for g in groups if any(p["policy"] == policy for p in g)]
        policies[policy] = {"category": category, "observed_entry_count": len(selected),
            "any_robust_conflicting_entry": "ROBUST_CONFLICT" in categories,
            "any_path_dependent_entry": any(p["has_path_dependent_check"] for p in selected),
            "cross_policy_equivalent_with_later_alerts": any(g[0]["later_alert_clusters"] > 0 for g in matched),
            "cross_policy_equivalent_fully_compatible": any(g[0]["category"] == "FULLY_COMPATIBLE" for g in matched),
            "cross_policy_equivalent_final_state_only": any(g[0]["later_alert_clusters"] == 0 for g in matched)}
    all_ranks, hard_ranks = rerank(clock, POLICIES), rerank(clock, HARD_STOP_POLICIES)
    if all_ranks["leading"] != clock["leading"]:
        raise ValueError("all-policy ranking differs from frozen reconstruction")
    all_ids = sorted({p["candidate_id"] for p in all_ranks["leading"]})
    hard_ids = sorted({p["candidate_id"] for p in hard_ranks["leading"]})
    return {"trade_id": episode["trade_id"], "symbol": episode["symbol"],
        "source_status": {k: episode["source"][k] for k in ("direction", "position_state", "setup_availability", "current_stop")},
        "policies": policies, "entry_policy_assessments": paths,
        "clustered_cross_policy_equivalence_classes": [[{k: p[k] for k in ("candidate_id", "policy")} for p in g] for g in groups],
        "all_policy_ranking": all_ranks, "hard_stop_only_ranking": hard_ranks,
        "leading_entry_set_changed": all_ids != hard_ids,
        "entry_ranks_changed": [(p["candidate_id"], p["rank"]) for p in all_ranks["entry_ranks"]] !=
            [(p["candidate_id"], p["rank"]) for p in hard_ranks["entry_ranks"]],
        "entry_vectors_changed": all_ranks["entry_ranks"] != hard_ranks["entry_ranks"],
        "leading_scenario_set_changed": all_ranks["leading"] != hard_ranks["leading"],
        "best_hard_stop_still_conflicts": bool(hard_ranks["leading"] and hard_ranks["leading"][0]["evaluation_vector"][0] > 0)}


def analyze(episodes):
    def baseline(e):
        return next(c for c in e["clock_comparisons"] if c["clock_variant"] == BASELINE)
    observed = [e for e in episodes if any(s["rank_eligible"] for p in baseline(e)["candidates"] for s in p["management"])]
    versions = []
    for name in [c["clock_variant"] for c in episodes[0]["clock_comparisons"]]:
        rows = [episode_comparison(e, next(c for c in e["clock_comparisons"] if c["clock_variant"] == name)) for e in observed]
        summary = {}
        for policy in POLICIES:
            summary[policy] = {category: [r["symbol"] for r in rows if r["policies"][policy]["category"] == category] for category in CATEGORIES}
            for flag in ("any_robust_conflicting_entry", "any_path_dependent_entry", "cross_policy_equivalent_with_later_alerts", "cross_policy_equivalent_fully_compatible", "cross_policy_equivalent_final_state_only"):
                summary[policy][flag] = [r["symbol"] for r in rows if r["policies"][policy][flag]]
        versions.append({"clock_variant": name, "denominator": len(observed), "policy_summary": summary,
            "changed_leading_entries": [r["symbol"] for r in rows if r["leading_entry_set_changed"]],
            "changed_entry_ranks": [r["symbol"] for r in rows if r["entry_ranks_changed"]],
            "changed_entry_vectors": [r["symbol"] for r in rows if r["entry_vectors_changed"]],
            "changed_leading_scenarios": [r["symbol"] for r in rows if r["leading_scenario_set_changed"]],
            "best_hard_stop_still_conflicts": [r["symbol"] for r in rows if r["best_hard_stop_still_conflicts"]],
            "episodes": rows})
    return {"schema_version": "grimes_management_sensitivity_v1", "baseline_clock": BASELINE,
        "source_episode_count": len(episodes), "observed_episode_count": len(observed),
        "excluded_right_censored_symbols": [e["symbol"] for e in episodes if e not in observed],
        "hard_stop_policies": list(HARD_STOP_POLICIES), "clocks": versions,
        "source_status_is_authoritative": True, "actual_stop_order_convention_identified": False}


def markdown(result):
    lines = ["## Management-policy sensitivity amendment", "",
        "CLOSE_REVIEW_NEXT_OPEN is an exploratory explanation, not evidence of Grimes' actual stop-order convention. "
        "Its additional flexibility can improve source compatibility without identifying the policy that generated the alerts. "
        "This comparison reuses unchanged frozen entries, daily paths, source facts and ranking vectors; it does not refit a simulator.", "",
        f"The fixed cohort contains {result['observed_episode_count']} episodes with observed, complete candidate paths under {BASELINE}. "
        f"Excluded right-censored episodes: {', '.join(result['excluded_right_censored_symbols'])}. Clocks are evaluated separately; they are not pooled as independent trades.", "",
        "Each co-published alert is one cluster. Final reported OPEN is a separate constraint, never another alert. "
        "The inherited ranking vector counts that final constraint once: EBAY's two conflicts mean one actual alert plus final OPEN, not two alerts. "
        "A fully compatible entry must be ACTIVE_COMPATIBLE at every later source cluster and final-state check, with at least one later alert. "
        "DROP after an earlier hypothetical exit has unresolved cause, not automatic agreement or robust conflict. "
        "The first five count columns partition the cohort: at least one fully compatible entry; otherwise every observed entry has a robust conflict; "
        "otherwise at least one path-dependent entry whose other checks are compatible; otherwise unresolved; or no later alerts. "
        "Robust conflict means all modeled extrema-order possibilities are closed before a continued source-management constraint. "
        "The last two columns overlap: any path-dependent check, and any clustered compatibility signature shared with a different policy, possibly at another observed entry. "
        "Equivalence is shown as all matching signatures / fully compatible matching signatures: two models can be equivalently wrong. "
        "It excludes final-state-only cases and means equivalent source-status explanations, not identical exits, sizes or P&L. "
        "Candidate-level details and symbols behind every count are in sensitivity.json.", ""]
    ordered = sorted(result["clocks"], key=lambda c: c["clock_variant"] != BASELINE)
    for clock in ordered:
        lines += [f"### {clock['clock_variant']}", "",
            "| Policy | ≥1 fully compatible | All entries conflict | Path-dependent only | Other unresolved | No later alerts | Any path check | Equivalent (all / compatible) |",
            "|---|---:|---:|---:|---:|---:|---:|---:|"]
        for policy, counts in clock["policy_summary"].items():
            columns = [str(len(counts[c])) for c in CATEGORIES]+[str(len(counts["any_path_dependent_entry"])),
                f"{len(counts['cross_policy_equivalent_with_later_alerts'])} / {len(counts['cross_policy_equivalent_fully_compatible'])}"]
            lines.append("| "+policy+" | "+" | ".join(columns)+" |")
        lines += ["", "Hard-stop-only re-ranking preserves the original lexicographic evidence score and simplicity weights, "
            "filtering out deferred review. It can select a least-conflicting explanation that still fails a source constraint. "
            "Entry ranks minimize each entry's best eligible policy vector; no profit, target or threshold is optimized.", "",
            f"Changed leading entry sets: {', '.join(clock['changed_leading_entries']) or 'none'}. "
            f"Changed ordinal entry ranks: {', '.join(clock['changed_entry_ranks']) or 'none'}. "
            f"Changed best entry vectors: {', '.join(clock['changed_entry_vectors']) or 'none'}. "
            f"Best hard-stop explanation still conflicts: {', '.join(clock['best_hard_stop_still_conflicts']) or 'none'}.", "",
            "| Episode | All-policy leaders | Hard-stop-only leaders | Best hard-stop vector |",
            "|---|---|---|---|"]
        for r in clock["episodes"]:
            def labels(key):
                return "; ".join(p["hypothesis"]+"/"+p["policy"] for p in r[key]["leading"])
            leaders = r["hard_stop_only_ranking"]["leading"]
            lines.append(f"| {r['symbol']} | {labels('all_policy_ranking')} | {labels('hard_stop_only_ranking')} | {leaders[0]['evaluation_vector'] if leaders else 'unranked'} |")
        lines += [""]
    lines += ["These counts quantify sensitivity within a fixed source-selected sample and finite entry/policy menu. "
        "They cannot identify actual fills, partial-exit fractions, stop-order type or discretionary intent, nor resolve all intraday paths. "
        "No later-alert cases supply only a final source constraint; equivalent policies and uncertain DROP causes must not be promoted to policy identification. "
        "Removing deferred review leaves stop geometry, quote progress and source-reported statuses unchanged. "
        "A better-fitting deferred-review explanation establishes sensitivity to assumptions, not evidence that Grimes used deferred review. "
        "Zero path-dependent source-compatibility checks does not resolve all intraday outcomes: ASST can have different stop/target exit causes "
        "while both paths are already closed before the same unresolved source DROP.", "",
        "### Offline reproduction", "",
        "Use unused output directories. The parent is the existing immutable PR19 study-v4; its full native/source proof stays local. "
        "The new layer verifies and rederives that parent before aggregating or replaying the sensitivity results. "
        "It lives outside the original reconstruction package so historical implementation identities and v4 replay remain valid.", "",
        "```sh", "PYTHONPATH=src .venv/bin/python scripts/grimes_management_sensitivity.py --help",
        "PYTHONPATH=src .venv/bin/python scripts/grimes_management_sensitivity.py freeze --study runs/grimes-reconstruction-20261018-26-v1/study-v4 --output runs/grimes-management-sensitivity-20261028-v1/study-NEW",
        "PYTHONPATH=src .venv/bin/python scripts/grimes_management_sensitivity.py replay --study runs/grimes-management-sensitivity-20261028-v1/study-NEW --output runs/grimes-management-sensitivity-20261028-v1/replay-NEW",
        ".venv/bin/python -m pytest -q", "```", ""]
    return "\n".join(lines)


def _parent(files, hashes):
    _check_hashes(files, hashes)
    if hashes["bundle_sha256"] != PARENT_SHA256:
        raise ValueError("sensitivity requires the declared immutable PR19 v4 parent")
    inputs = {k[len("input-"):]: v for k, v in files.items() if k.startswith("input-") and k != "input-hashes.json"}
    seals = json.loads(files["input-hashes.json"])
    _check_hashes(inputs, seals)
    if files != reconstruction_files(inputs, seals):
        raise ValueError("PR19 semantic parent mismatch")
    return json.loads(files["episodes.json"])


def _files(parent, hashes):
    result = analyze(_parent(parent, hashes))
    return {"sensitivity.json": encode(result), "report.md": markdown(result).encode(),
        "manifest.json": encode({"schema_version": "grimes_management_sensitivity_bundle_v1",
            "parent_bundle_sha256": hashes["bundle_sha256"], "implementation_sha256": digest(Path(__file__).read_bytes()),
            "source_or_path_simulator_changed": False}),
        "parent-hashes.json": encode(hashes), **{"parent-"+k: v for k, v in parent.items()}}


def freeze(parent, output):
    files, hashes = read_bundle(parent)
    return write_bundle(output, _files(files, hashes))


def load(path):
    files, hashes = read_bundle(path)
    parent = {k[len("parent-"):]: v for k, v in files.items() if k.startswith("parent-") and k != "parent-hashes.json"}
    seals = json.loads(files["parent-hashes.json"])
    if files != _files(parent, seals):
        raise ValueError("management sensitivity semantic output mismatch")
    return {"files": files, "hashes": hashes}
