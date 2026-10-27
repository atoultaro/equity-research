"""Independent Decimal return reconciliation and explicit stale ES coverage."""

from copy import deepcopy
from decimal import Decimal

from ..events.model import day


def return_verification(panel, prices, end, coverage, evidence):
    """Independently divide original canonical closes; don't reuse _measure."""
    raw = {r["session_date"]: r for r in prices.get("QQQ", []) if r["session_date"] <= end}
    observations = evidence.get("QQQ_return_observations", {}) if evidence else {}
    tolerance = Decimal(observations.get("rounding_tolerance_percentage_points", "0.01"))
    if not tolerance.is_finite() or tolerance < 0 or tolerance > Decimal("0.01"):
        raise ValueError("explicit rounding tolerance must be 0..0.01 percentage points")
    checks = {}
    for name, n, reference in (("daily_return", 1, "daily_return_percent"), ("return_20d", 20, "return_20d_percent")):
        rows, days, reason = panel.window("QQQ", end, n+1)
        claim = observations.get(reference)
        check = {"attribution": "MARKET_OBSERVED", "horizon_sessions": n, "required_observations": n+1,
            "formula": "Frozen Close(t)/Frozen Close(t-n completed sessions)-1",
            "comparison_source": observations.get(f"{name}_source", "NOT_PROVIDED"),
            "comparison_approximation_percent": claim, "rounding_tolerance_percentage_points": str(tolerance)}
        if rows is None:
            check.update(status="UNAVAILABLE", reason=reason, calculated_percent=None)
        else:
            before, current = raw[days[0]], raw[days[-1]]
            fraction = Decimal(current["close"])/Decimal(before["close"])-1
            measured = panel.features("QQQ", end)[name]["value"]
            if abs(fraction-Decimal(str(measured))) > Decimal("0.00000000001"):
                raise ValueError("independent return calculation disagrees with feature output")
            pct = fraction*100
            difference = pct-Decimal(claim) if claim is not None else None
            check.update(status="APPROXIMATION_CONSISTENT" if difference is not None and abs(difference) <= tolerance
                else "DISCREPANCY_REQUIRES_REVIEW" if difference is not None else "CALCULATED_NO_OPERATOR_COMPARISON",
                first_session=days[0], last_session=days[-1], first_close=before["close"], last_close=current["close"],
                first_source=before["source_row"], last_source=current["source_row"], calculated_fraction=str(fraction),
                calculated_percent=str(pct), difference_percentage_points=str(difference) if difference is not None else None,
                price_basis=coverage["QQQ"]["price_basis"], source_bundle_sha256=coverage["QQQ"]["source_bundle_sha256"],
                interpretation="Distinct completed-session horizons; frozen prices are never replaced by operator percentages")
        checks[name] = check
    return {"QQQ": checks}


def es_context(original, evidence, calendar, end):
    result = deepcopy(original)
    result["primary_current_context"] = ["SPY", "QQQ", "RSP", "IWM"]
    result["historical_research_role"] = "Important future source for historical market-regime evolution; no extrapolation or automatic IBKR-futures substitution"
    boundary = evidence.get("es_coverage") if evidence else None
    if not boundary:
        result.update(last_verified_available_session=None, missing_interval=None)
        return result
    last = day(boundary["last_verified_available_session"])
    if (original.get("inspected_aggregated_csv_sha256") and
            boundary.get("source_sha256") != original["inspected_aggregated_csv_sha256"]):
        raise ValueError("ES boundary evidence must match the preserved original source hash")
    result["coverage_evidence"] = deepcopy(boundary)
    result["last_verified_available_session"] = last
    missing = [s["session_date"] for s in calendar["sessions"] if last < s["session_date"] <= end]
    result["missing_interval"] = {"first_missing_cash_session": missing[0] if missing else None,
        "last_missing_cash_session": missing[-1] if missing else None, "missing_cash_session_count": len(missing),
        "calendar": "XNYS cash-session reference for ETF comparison, not a futures ETH completeness claim"}
    # A dated local boundary is evidence of stale coverage, not a verified roll chain.
    result["status"] = "NOT_AVAILABLE"
    result["reason"] = f"Local Databento ES boundary {last} does not cover {end}; historical files retained, no recent months synthesized or substituted"
    return result
