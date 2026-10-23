"""Explicit deterministic engineering fixtures. These are never historical evidence."""

from datetime import timedelta
from decimal import Decimal
from pathlib import Path

from ..ingestion.storage import encode
from ..models import timestamp


def synthetic_source():
    return {"provider": "LOCAL_SYNTHETIC_V1", "origin": "SYNTHETIC", "permission_reference": "repository-generated fixture",
            "coverage_evidence": "Complete generated catalogue only; no claim about actual US securities",
            "corporate_action_completeness": "ILLUSTRATIVE_INCOMPLETE", "vintage_evidence": None,
            "availability_evidence": "Synthetic completed-session clock", "identity_evidence": "Invented stable IDs"}


def master_capture(count=100, *, hard_cases=True):
    records, events = [], []
    for i in range(count):
        sid = f"synthetic:{i:05d}"
        listing = "2018-01-02" if hard_cases and i == 10 else "2000-01-03"
        fact = {"fact_id": f"{sid}/initial", "revision": 1, "security_id": sid, "issuer_id": f"issuer:{i:05d}",
                "share_class_id": f"class:{i:05d}", "symbol": f"S{i:05d}", "exchange": "XNAS", "security_type": "COMMON",
                "currency": "USD", "trading_status": "ACTIVE", "listing_start": listing, "listing_end": None,
                "provider_security_id": f"fixture-permanent-{i}", "identity_evidence": f"synthetic identity {i}",
                "identity_confidence": "ASSERTED", "effective_from": listing, "effective_to": None,
                "known_at": listing + "T00:00:00+00:00", "delisting_reason": None}
        if hard_cases:
            fact["security_type"] = {11: "ETF", 12: "ADR", 13: "SPAC_COMMON", 14: "REIT_COMMON", 15: "BDC", 16: "PREFERRED"}.get(i, "COMMON")
            if i in {5, 6}: fact["issuer_id"] = "issuer:dual-class"
            if i == 3: fact["symbol"] = "REUSED"
            if i == 4:
                fact.update(symbol="REUSED", listing_start="2015-01-02", effective_from="2015-01-02", known_at="2015-01-02T00:00:00+00:00")
            if i == 8:
                fact.update(issuer_id="issuer:reorganization", listing_start="2022-01-03", effective_from="2022-01-03", known_at="2022-01-03T00:00:00+00:00")
            if i == 7: fact["issuer_id"] = "issuer:reorganization"
            if i == 18: fact["identity_confidence"] = "WEAK"
            if i == 19: fact["known_at"] = None
        records.append(fact)

    def transition(i, effective, published, **updates):
        sid = f"synthetic:{i:05d}"
        original = next(r for r in reversed(records) if r["security_id"] == sid)
        closed = {**original, "revision": original["revision"]+1, "effective_to": effective, "known_at": published}
        records.append(closed)
        records.append({**original, **updates, "fact_id": f"{sid}/{effective}", "revision": 1,
                        "effective_from": effective, "effective_to": None, "known_at": published})

    def event(i, kind, effective, **fields):
        events.append({"event_id": f"synthetic:{i:05d}/{kind}/{effective or 'unknown'}", "security_id": f"synthetic:{i:05d}",
                       "event_type": kind, "effective_date": effective, "known_at": effective+"T22:00:00+00:00" if effective else None,
                       "evidence_reference": "synthetic lifecycle assertion", "terminal_value": None, **fields})

    if hard_cases and count >= 24:
        transition(0, "2012-06-01", "2012-06-02T00:00:00+00:00", trading_status="DELISTED", listing_end="2012-05-31", delisting_reason="BANKRUPTCY")
        event(0, "BANKRUPTCY", "2012-06-01", delisting_reason="BANKRUPTCY")
        transition(1, "2020-06-01", "2020-06-02T00:00:00+00:00", trading_status="DELISTED", listing_end="2020-05-29", delisting_reason="CASH_MERGER")
        event(1, "MERGER", "2020-06-01", cash_consideration="25", counterparty_security_id="synthetic:00030", consideration_status="SOURCE_ASSERTION_NOT_EXECUTION")
        transition(2, "2015-01-02", "2014-12-29T00:00:00+00:00", symbol="RENAMED")
        event(2, "TICKER_CHANGE", "2015-01-02", old_symbol="S00002", new_symbol="RENAMED")
        transition(3, "2010-01-04", "2010-01-05T00:00:00+00:00", trading_status="DELISTED", listing_end="2009-12-31", delisting_reason="FAILED")
        event(3, "DELISTING", "2010-01-04")
        transition(7, "2020-01-02", "2020-01-03T00:00:00+00:00", trading_status="DELISTED", listing_end="2019-12-31", delisting_reason="REORGANIZATION")
        event(7, "DELISTING", "2020-01-02", successor_security_id="synthetic:00008")
        transition(9, "2018-01-02", "2017-12-28T00:00:00+00:00", exchange="XNYS")
        event(9, "EXCHANGE_TRANSFER", "2018-01-02")
        transition(17, "2022-05-02", "2022-05-02T12:00:00+00:00", trading_status="HALTED")
        event(17, "HALT", "2022-05-02")
        event(20, "SPLIT", "2020-04-15", ratio="2", price_adjustments_applied=False)
        event(21, "DIVIDEND", None, ex_date_status="UNRESOLVED", payment_date="2020-06-15", amount="0.25")
        event(22, "DIVIDEND", "2022-04-15", amount="0.50", known_at="2022-04-16T00:00:00+00:00")
    return {"schema_version": "security_master_capture_v1", "source": synthetic_source(), "records": records, "lifecycle_events": events}


def price_rows(i, sessions, *, phase=0):
    """Liquidity rotates mechanically by ID/phase, never by future performance."""
    sid = f"synthetic:{i:05d}"
    rows = []
    for j, session in enumerate(sessions):
        close = Decimal(10 + i % 11) + Decimal(j) / 10
        available = (timestamp(session["closes_at"]) + timedelta(minutes=60)).isoformat()
        rows.append({"security_id": sid, "session_date": session["session_date"], "open": str(close-Decimal("0.1")),
                     "high": str(close+Decimal("0.05")), "low": str(close-Decimal("0.2")), "close": str(close),
                     "volume": str(1000 + ((i + phase*17) % 100)*100), "currency": "USD",
                     "price_basis": "RAW_TRADED", "volume_basis": "RAW_SHARES", "revision": 1,
                     "available_at": available, "known_at": available, "availability_status": "RECONSTRUCTED",
                     "quality_status": "VALID", "original_observation_reference": f"generated/{sid}/{session['session_date']}"})
    return rows


def write_fixture_inputs(directory, calendar, count=100, *, windows=None, hard_cases=True):
    """Return bounded capture paths. Windows are explicit materialization segments."""
    directory = Path(directory)
    directory.mkdir(exist_ok=False, parents=True)
    master = master_capture(count, hard_cases=hard_cases)
    masterpath = directory / "master_capture.json"
    masterpath.write_bytes(encode(master))
    windows = windows or [(calendar["start"], calendar["end"])]
    paths, batch, batchno = [], [], 0
    for phase, (first, last) in enumerate(windows):
        sessions = [s for s in calendar["sessions"] if first <= s["session_date"] <= last]
        for i in range(count):
            rows = price_rows(i, sessions, phase=phase)
            if hard_cases:
                # Actual *synthetic* lifecycle coverage ends. Never extend Close.
                end = {0: "2012-05-31", 1: "2020-05-29", 3: "2009-12-31", 7: "2019-12-31"}.get(i, "9999-12-31")
                start = {4: "2015-01-02", 8: "2022-01-03", 10: "2018-01-02"}.get(i, "2000-01-03")
                rows = [r for r in rows if start <= r["session_date"] <= end and not (i == 17 and r["session_date"] >= "2022-05-02")]
            for row in rows:
                batch.append(row)
                if len(batch) >= 10000:
                    path = directory / f"price_capture_{batchno:04d}.json"
                    path.write_bytes(encode({"schema_version": "daily_panel_capture_v1", "source": {**synthetic_source(), "status": "SUCCESS", "failure_codes": []}, "rows": batch}))
                    paths.append(path); batch, batchno = [], batchno+1
    if batch:
        path = directory / f"price_capture_{batchno:04d}.json"
        path.write_bytes(encode({"schema_version": "daily_panel_capture_v1", "source": {**synthetic_source(), "status": "SUCCESS", "failure_codes": []}, "rows": batch}))
        paths.append(path)
    return masterpath, paths
