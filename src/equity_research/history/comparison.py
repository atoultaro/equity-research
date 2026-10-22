"""Diagnostic differences between two explicit, independently retained sources."""

from decimal import Decimal, InvalidOperation

from .contracts import interval


def compare_providers(yahoo, ibkr, symbol, start, end, *, price_absolute="0.01", price_percent="0.01",
                      volume_absolute="0", volume_percent="1"):
    interval(start, end)
    try:
        limits = [Decimal(str(v)) for v in (price_absolute, price_percent, volume_absolute, volume_percent)]
    except InvalidOperation:
        raise ValueError("comparison tolerances must be decimal numbers") from None
    if any(not v.is_finite() or v < 0 for v in limits):
        raise ValueError("comparison tolerances must be finite and nonnegative")
    left, right = yahoo.manifest, ibkr.manifest
    if left["provider"] != "yahoo" or right["provider"] != "ibkr":
        raise ValueError("explicit Yahoo and IBKR datasets are required")
    a, b = left["securities"][symbol], right["securities"][symbol]
    if (a["security"]["security_id"] != b["security"]["security_id"] or
            a["security"]["currency"] != b["security"]["currency"]):
        raise ValueError("different identified securities/currencies cannot be compared")
    if not all(m["start"] <= start <= end <= m["end"] for m in (left, right)):
        raise ValueError("comparison interval must lie within both frozen intervals")
    def keyed(dataset):
        rows = [r for r in dataset.bars(symbol) if start <= r["session_date"] <= end]
        if len({r["session_date"] for r in rows}) != len(rows):
            raise ValueError("ambiguous duplicate session keys")
        return {r["session_date"]: r for r in rows}
    x, y = keyed(yahoo), keyed(ibkr)
    basis_ok = (a["basis"] == b["basis"] and a["basis"].get("verified") is True and
                not any("UNKNOWN" in str(a["basis"].get(k, "UNKNOWN")).upper() for k in ("price_basis", "volume_basis")))
    changes, adjustment, close_ratios = [], [], []
    for day in sorted(x.keys() & y.keys()):
        for field in ("open", "high", "low", "close", "volume", "adj_close"):
            before, after = x[day].get(field), y[day].get(field)
            try:
                v, w = Decimal(before), Decimal(after)
                if not v.is_finite() or not w.is_finite():
                    raise InvalidOperation
            except (InvalidOperation, TypeError, ValueError):
                changes.append({"session_date": day, "field": field, "yahoo": before, "ibkr": after,
                                "status": "MISSING_OR_INVALID", "absolute_difference": None,
                                "percent_difference": None, "ratio_ibkr_to_yahoo": None,
                                "exceeds_tolerance": None})
                continue
            absolute = abs(w - v)
            percent = absolute / abs(v) * 100 if v else (Decimal(0) if not w else None)
            absolute_limit, percent_limit = limits[2:] if field == "volume" else limits[:2]
            # Exceed only if outside both allowances. A nonzero change from zero
            # uses the absolute limit, with percent explicitly undefined.
            exceeds = absolute > absolute_limit and (percent is None or percent > percent_limit)
            changes.append({"session_date": day, "field": field, "yahoo": before, "ibkr": after,
                            "status": "DIAGNOSTIC_ONLY" if not basis_ok else "COMPARABLE",
                            "absolute_difference": str(absolute), "signed_difference_ibkr_minus_yahoo": str(w - v),
                            "percent_difference": str(percent) if percent is not None else None,
                            "ratio_ibkr_to_yahoo": str(w / v) if v else None,
                            "exceeds_tolerance": exceeds})
            if field == "close" and v:
                close_ratios.append({"session_date": day, "ratio_ibkr_to_yahoo": str(w / v)})
        for provider, row in (("yahoo", x[day]), ("ibkr", y[day])):
            if row.get("adj_close") is not None and row["adj_close"] != row["close"]:
                adjustment.append({"session_date": day, "provider": provider,
                                   "code": "ADJUSTED_CLOSE_DIFFERS_NOT_PROOF_OF_SPECIFIC_EVENT"})
    qualities = {"yahoo": yahoo.quality(symbol), "ibkr": ibkr.quality(symbol)}
    expected = {name: {s["session_date"] for s in quality["calendar"]["sessions"] if start <= s["session_date"] <= end}
                - set(quality["listing_exclusions"]) for name, quality in qualities.items()}
    actions = {name: [event for event in quality.get("provider_events", []) if start <= event["session_date"] <= end]
               for name, quality in qualities.items()}
    ratio_changes = [{"session_date": current["session_date"], "previous_ratio": previous["ratio_ibkr_to_yahoo"],
                      "current_ratio": current["ratio_ibkr_to_yahoo"]}
                     for previous, current in zip(close_ratios, close_ratios[1:])
                     if current["ratio_ibkr_to_yahoo"] != previous["ratio_ibkr_to_yahoo"]]
    return {"schema_version": "provider_comparison_v1", "symbol": symbol,
            "security_id": a["security"]["security_id"], "identity_reference": [a["security"]["reference"], b["security"]["reference"]],
            "start": start, "end": end, "yahoo_dataset_sha256": yahoo.content_sha256,
            "ibkr_dataset_sha256": ibkr.content_sha256,
            "interpretation": "COMPARABLE" if basis_ok else "DIAGNOSTIC_ONLY_BASIS_UNRESOLVED",
            "bases": {"yahoo": a["basis"], "ibkr": b["basis"]}, "common_sessions": sorted(x.keys() & y.keys()),
            "missing_sessions": {"yahoo": sorted(expected["yahoo"] - x.keys()), "ibkr": sorted(expected["ibkr"] - y.keys())},
            "listing_exclusions": {name: [day for day in quality["listing_exclusions"] if start <= day <= end]
                                   for name, quality in qualities.items()},
            "only_yahoo_sessions": sorted(x.keys() - y.keys()), "only_ibkr_sessions": sorted(y.keys() - x.keys()),
            "tolerances": {"price_absolute": str(limits[0]), "price_percent": str(limits[1]),
                           "volume_absolute": str(limits[2]), "volume_percent": str(limits[3])},
            "differences": changes, "adjustment_diagnostics": adjustment,
            "close_ratio_changes": ratio_changes,
            "provider_action_observations": actions,
            "action_coverage": "unknown_native_observations_not_completeness_no_IBKR_action_feed",
            "corporate_action_interpretation": "unresolved_no_action_completeness_or_transformation_inferred",
            "source_selection": "NONE", "transformation": "NONE"}
