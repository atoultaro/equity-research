"""Known-component split views and volume uncertainty; never fabricate raw data."""

from decimal import Decimal
from statistics import median


def undo_known_split_component(rows, effective_date, ratio):
    ratio = Decimal(str(ratio))
    if not ratio.is_finite() or ratio <= 0:
        raise ValueError("positive documented split ratio required")
    return [{**r, **{k: str(Decimal(r[k])*ratio) if r["session_date"] < effective_date else r[k]
        for k in ("open", "high", "low", "close")},
        "derived_view": "UNDO_ONE_KNOWN_SPLIT_COMPONENT_NOT_VERIFIED_RAW",
        "native_price_basis": r["price_basis"], "price_basis": "DERIVED_KNOWN_COMPONENT_NOT_RAW",
        "volume": r["volume"], "volume_basis": r["volume_basis"]} for r in rows]


def split_diagnostics(prices, events, calendar):
    days = [s["session_date"] for s in calendar["sessions"]]
    result = []
    for item in events:
        symbol, event = item["symbol"], item["event"]
        effective = event["effective_date"]
        if event["event_type"] != "SPLIT" or event["evidence_status"] != "VERIFIED" or effective not in days:
            raise ValueError("verified dated split evidence required")
        ratio = Decimal(event["payload"]["new_shares"])/Decimal(event["payload"]["old_shares"])
        i = days.index(effective)
        before_days, after_days = days[i-5:i], days[i:i+5]
        by_day = {r["session_date"]: r for r in prices[symbol]}
        if len(before_days) != 5 or len(after_days) != 5 or any(d not in by_day for d in before_days+after_days):
            result.append({"symbol": symbol, "event_id": event["event_id"], "status": "MISSING_EXPECTED_SPLIT_WINDOW"})
            continue
        before, after = by_day[before_days[-1]], by_day[effective]
        view = undo_known_split_component([by_day[d] for d in before_days+after_days], effective, ratio)
        native_ratio = float(Decimal(after["open"])/Decimal(before["close"]))
        volume_ratio = float(median(Decimal(by_day[d]["volume"]) for d in after_days) /
                             median(Decimal(by_day[d]["volume"]) for d in before_days))
        result.append({"symbol": symbol, "event_id": event["event_id"], "effective_date": effective,
            "ratio_new_over_old": str(ratio), "status": "OBSERVED_KNOWN_SPLIT_WINDOW", "event_source_ids": event["source_ids"],
            "native_post_open_over_pre_close": native_ratio,
            "known_component_undone_post_open_over_pre_close": native_ratio/float(ratio),
            "observed_after_over_before_median_native_volume": volume_ratio,
            "interpretation": "Native prices lack the nominal split jump; undoing the known component introduces it. This corroborates the split-adjusted interpretation, not an exhaustive raw-price reconstruction.",
            "volume_interpretation": "Trading activity and filtering confound volume ratios; raw shares, lots and adjustment factors remain unverified",
            "derived_view": view, "raw_price_claim": False, "raw_volume_claim": False, "dollar_volume_admission": "NOT_GRANTED"})
    return result


def stop_scale_diagnostics(trades, prices, coverage, basis_evidence):
    anchors = {r["symbol"]: r for r in basis_evidence}
    result = []
    for trade in trades:
        symbol = trade["symbol"]
        rows = {r["session_date"]: r for r in prices[symbol]}
        corroborated = []
        evidence = anchors.get(symbol)
        if evidence and evidence["con_id"] == coverage[symbol]["contract"]["conId"]:
            for a in evidence.get("anchors", []):
                if a["session_date"] in rows and Decimal(rows[a["session_date"]][a["field"]]) == Decimal(a["nominal_quote"]):
                    corroborated.append(a)
        detail = {"symbol": symbol, "con_id": coverage[symbol]["contract"]["conId"],
            "scale": "BOUNDED_QUOTE_ANCHOR" if corroborated else "NATIVE_NOMINAL_COMPATIBILITY_ASSUMED",
            "anchors": corroborated, "factors_fitted_to_management_or_profit": False,
            "volume_basis": coverage[symbol]["volume_basis"], "native_data_rewritten": False,
            "uniform_price_and_stop_scaling": "Dimensionless risk/ATR and barrier ordering are invariant when both are scaled consistently"}
        if symbol == "EBAY" and "2026-10-26" in rows:
            row = rows["2026-10-26"]
            minimum = Decimal(trade["initial_stop"])/Decimal(row["low"])
            detail.update(minimum_price_only_scale_to_avoid_old_stop_touch=str(minimum),
                scale_would_require_strictly_greater_factor=True,
                price_only_rescaling_consistent_with_quote_anchor=False if corroborated else None,
                explanation="Any pre-session-entry hard-stop scenario using119.20 crosses the observed117.87 Low. A price-only factor above this threshold contradicts the matching nominal Low anchor; timing/stop conventions need separate hypotheses.")
        result.append(detail)
    return result
