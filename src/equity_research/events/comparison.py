"""Compare evidence completeness, with no company-specific rules or performance ranking."""

from collections import Counter


def compare_event_studies(studies):
    """Require the same definitions/calendar/window and return observed quality counts.

    Calendar bounds may differ because older documented splits differ. Actual
    sessions inside the common price interval must match exactly. Original sealed
    studies are read only; callers re-freeze under new names after code changes.
    """
    if len(studies) < 2:
        raise ValueError("comparison requires at least two studies")
    reference, companies = None, {}
    for label, study in studies.items():
        manifest, prices, report = study.manifest, study.prices.manifest, study.diagnostics
        symbol = manifest["symbol"]
        price_quality = study.prices.quality(symbol)
        signature = {"start": prices["start"], "end": prices["end"], "calendar": prices["calendar"],
                     "alignment_version": manifest["alignment_version"], "event_schema": manifest["event_schema"],
                     "return_definition": report["return_definition"], "pre_features_cutoff": report["pre_features_cutoff"],
                     "dividend_treatment": report["dividend_treatment"],
                     "diagnostics_sha256": manifest["implementation_sha256"]["diagnostics.py"],
                     "expected_sessions": price_quality["calendar"]["sessions"]}
        if reference is None:
            reference = signature
        elif signature != reference:
            raise ValueError("comparison requires identical window, calendar, definitions and diagnostic implementation")
        events, annotations = study.event_dataset.events, study.retrospective["alignment"]["events"]
        counts = Counter(e["event_type"] for e in events)
        dividends = [e for e in events if e["event_type"] == "DIVIDEND"]
        results = report["events"]
        companies[label] = {
            "symbol": symbol, "security_id": manifest["security_id"],
            "qualified_contract": prices["securities"][symbol]["qualified_contract"],
            "study_sha256": study.content_sha256, "price_dataset_sha256": study.prices.content_sha256,
            "event_dataset_sha256": study.event_dataset.content_sha256,
            "provider": prices["provider"], "start": prices["start"], "end": prices["end"],
            "expected_sessions": len(price_quality["calendar"]["sessions"]), "price_rows": len(study.bars()),
            "calendar_status": price_quality["status"], "missing_sessions": price_quality["missing_sessions"],
            "duplicate_sessions": price_quality["duplicate_sessions"], "off_calendar_sessions": price_quality["off_calendar_sessions"],
            "basis": report["basis"], "event_counts": {k: counts[k] for k in ("EARNINGS", "DIVIDEND", "SPLIT")},
            "verified_ex_dates": sum(e["effective_date"] is not None and e["payload"]["ex_date_status"] == "VERIFIED" for e in dividends),
            "unknown_ex_dates": sum(e["effective_date"] is None for e in dividends),
            "announcement_precision_counts": dict(Counter(e["announced_time_precision"] for e in events)),
            "ambiguous_earnings_timing": sum(a["timing_ambiguous"] for e, a in zip(events, annotations, strict=True)
                                            if e["event_type"] == "EARNINGS"),
            "available_diagnostics": {kind: sum(r["event_type"] == kind and r["status"] == "AVAILABLE" for r in results)
                                      for kind in ("EARNINGS", "DIVIDEND", "SPLIT")},
            "diagnostic_issue_counts": dict(Counter(issue for r in results for issue in r["issues"])),
            "split_events_outside_price_interval": sum(e["event_type"] == "SPLIT" and not prices["start"] <= e["effective_date"] <= prices["end"] for e in events),
            "event_quality": study.event_dataset.quality,
            "source_references_sha256": manifest["source_references_sha256"],
            "point_in_time_archive_completeness": "UNKNOWN"}
    return {"schema_version": "event_study_evidence_comparison_v1", "interpretation": "EVIDENCE_COMPLETENESS_NOT_TRADING_PERFORMANCE",
            "configuration": {k: v for k, v in reference.items() if k != "expected_sessions"}, "studies": companies}
