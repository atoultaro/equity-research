"""One-security inputs for existing pure swing/outcome interfaces, never execution."""

from ..ingestion.storage import digest, encode
from ..models import timestamp


def single_security_inputs(universe, security_id, membership_date, decision_timestamp, *,
                           price_cutoff_timestamp, strategy_configuration_sha256,
                           outcome_configuration_sha256, market_context_bundle=None, history_start=None):
    membership = universe.members_as_of(membership_date, decision_timestamp=decision_timestamp)
    selected = next((m for m in membership["members"] if m["security_id"] == security_id), None)
    if selected is None:
        raise ValueError("security is not admitted by the requested historical universe")
    rows = universe.panel.rows_as_of(security_id, price_cutoff_timestamp)
    if history_start is not None:
        rows = [r for r in rows if r["session_date"] >= history_start]
    if not rows:
        raise ValueError("no historically available price observations")
    for row in rows:
        if (row["known_at"] is None or row["available_at"] is None or row["revision"] != 1 or
                timestamp(row["known_at"]) > timestamp(row["available_at"])):
            raise ValueError("single-vintage adapter cannot replay late revisions; use a causal vintage replay")
        if row["price_basis"] != "RAW_TRADED" or row["volume_basis"] != "RAW_SHARES" or row["quality_status"] != "VALID":
            raise ValueError("unadmitted single-security research prices")
    # Symbol here is a presentation alias for the already resolved security ID;
    # historical joins and dataset hashes continue to use permanent identity.
    symbol = selected["identity"]["symbol"]
    rows = [{**r, "symbol": symbol} for r in rows]
    from ..swing.engine import validate_history
    validate_history(rows, universe.panel.calendar, symbol, security_id)
    context_sha = market_context_bundle.content_sha256 if market_context_bundle is not None else None
    manifest = {"schema_version": "universe_research_manifest_v1", "universe_bundle_sha256": universe.content_sha256,
                "universe_definition_sha256": universe.manifest["universe_definition_sha256"],
                "selection_date": membership["selection_date"], "security_id": security_id,
                "historical_price_dataset_sha256": universe.panel.content_sha256,
                "materialized_security_rows_sha256": digest(encode(rows)),
                "market_context_bundle_sha256": context_sha, "market_context_status": "FROZEN" if context_sha else "UNAVAILABLE",
                "strategy_configuration_sha256": strategy_configuration_sha256,
                "outcome_configuration_sha256": outcome_configuration_sha256,
                "membership_decision_timestamp": decision_timestamp, "history_start": history_start, "price_cutoff_timestamp": price_cutoff_timestamp,
                "admission": {"universe_selection": membership["pit_quality"], "signal_research": "ILLUSTRATIVE_RESEARCH_ONLY",
                              "forward_price_outcomes": "REQUIRES_COMPLETE_PATH_AND_ACTION_DIAGNOSTICS",
                              "strict_execution_simulation": "NOT_ADMITTED"},
                "corporate_action_evidence": universe.master.quality["corporate_action_completeness"]}
    return rows, universe.panel.calendar, manifest
