"""Optional offline ES import. No symbol-prefix merging or inferred roll policy."""

import csv
from datetime import timedelta
from decimal import Decimal
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from ..events.model import timestamp
from ..ingestion.storage import digest, encode, write_bundle


def import_es(csv_path, metadata_path, calendar_path, output):
    """Aggregate explicitly identified 5-minute bars to NY cash-session context.

    This is a separate research artifact; never substitute it into stock features.
    The operator supplies vetted identity/roll/session metadata and an explicit
    cash-session schedule. Contract changes inside a cash session are rejected.
    """
    raw, meta_raw, cal_raw = (Path(p).read_bytes() for p in (csv_path, metadata_path, calendar_path))
    meta, calendar = json.loads(meta_raw), json.loads(cal_raw)
    if (meta.get("schema_version") != "verified_es_import_v1" or meta.get("verified") is not True
            or meta.get("source_sha256") != digest(raw) or meta.get("bar_minutes") != 5
            or not meta.get("contract_identities") or any(not meta.get(k) for k in
                ("identity_evidence", "roll_methodology", "roll_evidence", "session_hours", "timezone", "price_adjustment", "adjustment_evidence"))):
        raise ValueError("ES requires verified identities, roll, session, timezone, adjustment and source hash")
    if meta["timezone"] != "America/New_York" or meta["price_adjustment"] != "UNADJUSTED_CONTRACT_PRICES":
        raise ValueError("optional importer supports unadjusted identified contracts and NY cash-session context only")
    ids = meta["contract_identities"]
    if any(not isinstance(c, dict) or c.get("root") != "ES" or not c.get("expiry") or c.get("exchange") != "CME" for c in ids.values()):
        raise ValueError("explicit ES/CME expiry identities required")
    cutoff = timestamp(meta["analysis_cutoff"])
    sessions = {s["session_date"]: s for s in calendar["sessions"] if timestamp(s["closes_at"]) <= cutoff}
    selected, seen = {}, set()
    reader = csv.DictReader(raw.decode("utf-8").splitlines())
    if set(reader.fieldnames or ()) != {"timestamp", "contract_id", "open", "high", "low", "close", "volume"}:
        raise ValueError("identified five-minute ES CSV schema required; no prefix/expiry inference")
    for row in reader:
        t = timestamp(row["timestamp"])
        if t + timedelta(minutes=5) > cutoff:
            continue
        local = t.astimezone(ZoneInfo(meta["timezone"]))
        day = local.date().isoformat()
        if day not in sessions:
            continue
        s = sessions[day]
        if not timestamp(s["opens_at"]) <= t < timestamp(s["closes_at"]):
            continue
        if t in seen or row["contract_id"] not in ids:
            raise ValueError("duplicate time or unresolved ES contract")
        seen.add(t)
        nums = {k: Decimal(row[k]) for k in ("open", "high", "low", "close", "volume")}
        if (any(not n.is_finite() for n in nums.values()) or nums["volume"] < 0
                or any(nums[k] <= 0 for k in ("open", "high", "low", "close"))
                or nums["high"] < max(nums["open"], nums["close"], nums["low"])
                or nums["low"] > min(nums["open"], nums["close"], nums["high"])):
            raise ValueError("invalid ES OHLCV")
        selected.setdefault(day, []).append((t, row["contract_id"], nums))
    bars, missing = [], []
    for day, s in sessions.items():
        rows = sorted(selected.get(day, []))
        times, t = [], timestamp(s["opens_at"])
        while t < timestamp(s["closes_at"]):
            times.append(t)
            t += timedelta(minutes=5)
        if [r[0] for r in rows] != times:
            missing.append(day)
            continue
        if len({r[1] for r in rows}) != 1:
            raise ValueError("intra-session contract splice forbidden")
        bars.append({"session_date": day, "contract_id": rows[0][1], "open": str(rows[0][2]["open"]),
            "high": str(max(r[2]["high"] for r in rows)), "low": str(min(r[2]["low"] for r in rows)),
            "close": str(rows[-1][2]["close"]), "volume": str(sum(r[2]["volume"] for r in rows))})
    return write_bundle(Path(output), {"source.csv": raw, "metadata.json": meta_raw, "calendar.json": cal_raw,
        "daily_cash_context.json": encode(bars), "quality.json": encode({"missing_or_incomplete_sessions": missing,
        "status": "COMPLETE" if bars and not missing else "INCOMPLETE", "returns_computed": False,
        "scope": "NY cash-session ES context, not a continuous futures return series; rolls remain explicit"})})
