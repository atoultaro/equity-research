"""Operator-reported conventions and optional arithmetic, never executable exits."""

from copy import deepcopy
from decimal import Decimal


def validate_methodology(record):
    if (record.get("schema_version") != "expert_methodology_v1" or not record.get("methodology_id")
            or record.get("expert") != "Adam Grimes" or record.get("source_status") != "OPERATOR_REPORTED"
            or record.get("independently_verified") is not False or not record.get("source_reference")
            or not record.get("application")):
        raise ValueError("explicit operator-reported Grimes methodology required")
    for direction in ("LONG", "SHORT"):
        row = record[direction]
        expected = {"trigger": "PLUS_1_ORIGINAL_R", "minimum_exit_fraction_of_original": "1/3" if direction == "LONG" else "1",
            "exact_exit_fraction_of_original": None if direction == "LONG" else "1",
            "remaining_fraction": None if direction == "LONG" else "0",
            "runner_policy": "ALLOW_REMAINING_POSITION_TO_RUN" if direction == "LONG" else "NO_RUNNER",
            "subsequent_stop_adjustments": None, "final_exit_rules": None, "remaining_exit_timing": None}
        if row != expected:
            raise ValueError("preserve minimum-one-third LONG / full SHORT convention and unknown management details")
    return deepcopy(record)


def one_r(direction, entry, stop):
    """E and S must share units. None entry leaves actual R and target unknown."""
    if direction not in {"LONG", "SHORT"}:
        raise ValueError("LONG or SHORT required")
    s = Decimal(str(stop))
    if not s.is_finite() or s <= 0:
        raise ValueError("positive finite stop required")
    if entry is None:
        return {"original_per_share_risk": None, "target_1R": None}
    e = Decimal(str(entry))
    if not e.is_finite() or e <= 0:
        raise ValueError("positive finite entry required")
    risk = e-s if direction == "LONG" else s-e
    if risk <= 0:
        raise ValueError("original per-share R must be positive")
    target = e+risk if direction == "LONG" else e-risk
    return {"original_per_share_risk": str(risk), "target_1R": str(target)}


def management(observation, reference_close, methodology, *, scenario=False):
    convention = deepcopy(methodology[observation["direction"]]) if methodology else None
    result = {"methodology_id": methodology["methodology_id"] if methodology else None,
        "source_status": "OPERATOR_REPORTED" if methodology else "UNKNOWN_OR_MISSING",
        "application": "CURRENT_OPERATOR_STATED_CONVENTION_NOT_OBSERVED_TRADE_SPECIFIC_EXIT_INSTRUCTION",
        "actual_entry": observation["entry_price"], "actual_target": None,
        "actual_execution_timestamp": observation["execution_timestamp"], "actual_quantity": observation["quantity"],
        "observed_trade_specific_exit_instruction": None, "executed_exits": None,
        "profit_taking_convention": convention, "reference_scenario": None}
    if scenario:
        hypothetical = {"attribution": "RESEARCH_HYPOTHESIS", "reference_entry_basis": "OCT_26_CLOSE",
            "is_actual_execution": False, "hypothetical_entry": reference_close, "actual_target": None,
            "profit_taking_convention": convention, "status": "UNAVAILABLE", "reason": None,
            "hypothetical_original_per_share_risk": None, "hypothetical_1R_target": None,
            "price_basis_compatibility": "ASSUMED_FOR_ARITHMETIC_ONLY; reported-stop adjustment basis is unverified"}
        if reference_close is None:
            hypothetical["reason"] = "MISSING_REFERENCE_CLOSE"
        else:
            try:
                arithmetic = one_r(observation["direction"], reference_close, observation["reported_stop"])
            except ValueError:
                hypothetical["reason"] = "NONPOSITIVE_REFERENCE_R_OR_INVALID_PRICE"
            else:
                hypothetical.update(status="AVAILABLE", hypothetical_original_per_share_risk=arithmetic["original_per_share_risk"],
                    hypothetical_1R_target=arithmetic["target_1R"])
        result["reference_scenario"] = hypothetical
    return result
