"""Explicit, bounded, resumable daily IBKR historical-depth acquisition.

No strategy, account data or order API. Frozen checkpoints are never overwritten.
"""

import asyncio
from contextlib import contextmanager
from datetime import UTC, date, datetime, time, timedelta
import importlib.metadata
import json
from pathlib import Path
import platform

from .contracts import Security, now_utc, select_securities
from .depth_store import Journal, head_date, progress, summarize, window_rows
from ..ingestion.calendar import schedule
from ..ingestion.storage import digest, encode, write_bundle
from ..providers.ibkr import Pacer, classify, contract_record, error_code
from ..providers.ibkr_depth import make_depth_backend

KINDS = {"stock", "market_etf", "sector_etf", "industry_etf"}
LIMITS = {"window_days": (7, 1825, 365), "overlap_days": (1, 30, 5), "max_attempts": (1, 3, 3),
          "max_windows_per_instrument": (1, 500, 64), "max_requests": (1, 5000, 800),
          "max_runtime_seconds": (1, 14400, 3600), "max_consecutive_empty": (1, 10, 3)}


def config_record(config):
    if config.get("schema_version") != "ibkr_depth_config_v1" or set(config) - {
            "schema_version", "start", "end", "instruments", "head_timestamp", *LIMITS}:
        raise ValueError("unsupported depth config schema/fields")
    start = date.fromisoformat(config["start"])
    if start.isoformat() != config["start"]:
        raise ValueError("start must be YYYY-MM-DD")
    if config.get("end"):
        end = date.fromisoformat(config["end"])
        if end.isoformat() != config["end"] or end < start:
            raise ValueError("end must be an ordered YYYY-MM-DD")
    rows, kinds = [], []
    for item in config["instruments"]:
        if set(item) != {"kind", "security"} or item["kind"] not in KINDS:
            raise ValueError("each instrument requires kind and explicit security mapping")
        rows.append(item["security"])
        kinds.append(item["kind"])
    securities = select_securities(rows, [r["symbol"] for r in rows], "ibkr")
    result = {"schema_version": "ibkr_depth_config_v1", "start": config["start"], "end": config.get("end"),
        "instruments": [{"kind": k, "security": s.record()} for s, k in zip(securities, kinds)]}
    for name, (low, high, default) in LIMITS.items():
        value = config.get(name, default)
        if type(value) is not int or not low <= value <= high:
            raise ValueError(f"{name} must be {low}..{high}")
        result[name] = value
    if result["overlap_days"] >= result["window_days"]:
        raise ValueError("overlap_days must be smaller than window_days")
    result["head_timestamp"] = config.get("head_timestamp", True)
    if type(result["head_timestamp"]) is not bool:
        raise ValueError("head_timestamp must be boolean")
    return result


def capture_return(bars):
    import pandas as pd
    from ..ingestion.frames import capture_frame, pack
    native, records = [], []
    for bar in bars:
        native.append({k: pack(getattr(bar, k, None)) for k in
                       ("date", "open", "high", "low", "close", "volume", "average", "barCount")})
        raw = getattr(bar, "date", None)
        if isinstance(raw, str) and len(raw) == 8 and raw.isdigit():
            try:
                raw = datetime.strptime(raw, "%Y%m%d").date()
            except ValueError:
                pass
        records.append({"Date": raw, **{k.title(): getattr(bar, k, None) for k in
                        ("open", "high", "low", "close", "volume")}})
    frame = pd.DataFrame(records, columns=["Date", "Open", "High", "Low", "Close", "Volume"]).set_index("Date")
    return {"returned_bars.json": encode({"schema_version": "ibkr_native_daily_v1", "bars": native}),
            "returned_frame.json": capture_frame(frame)}


@contextmanager
def writer_lock(root):
    lock = Path(root) / ".lock"
    try:
        lock.mkdir()
    except FileExistsError:
        raise ValueError("AUDIT_BUSY: inspect another writer or stale lock before resuming") from None
    try:
        yield
    finally:
        lock.rmdir()


class ResourceLimit(Exception):
    pass


class DepthAudit:
    def __init__(self, *, port, client_id, host="127.0.0.1", backend_factory=make_depth_backend,
                 clock=now_utc, pacer=None, sleep=asyncio.sleep, origin="ibkr_client"):
        if host not in {"127.0.0.1", "::1", "localhost"}:
            raise ValueError("explicit local TWS/Gateway required")
        if type(port) is not int or not 1 <= port <= 65535 or type(client_id) is not int or client_id <= 0:
            raise ValueError("explicit port and positive nonzero client_id required")
        if origin not in {"synthetic", "ibkr_client"} or (origin == "synthetic" and backend_factory is make_depth_backend):
            raise ValueError("synthetic origin requires an injected backend")
        self.host, self.port, self.client_id = host, port, client_id
        self.backend_factory, self.clock, self.sleep = backend_factory, clock, sleep
        self.pacer, self.origin = pacer or Pacer(), origin

    def run(self, config, output, *, resume=False, connect=False, read_only_confirmed=False,
            permission_reference=None):
        config = config_record(config)
        if self.origin == "ibkr_client" and not (connect and read_only_confirmed and
                isinstance(permission_reference, str) and permission_reference.strip()):
            raise ValueError("live audit requires explicit --connect, --read-only-api-confirmed and --permission-reference")
        root = Path(output)
        if not resume:
            now = self.clock().astimezone(UTC)
            from zoneinfo import ZoneInfo
            today = now.astimezone(ZoneInfo("America/New_York")).date()
            until = date.fromisoformat(config["end"]) if config["end"] else today
            if until > today or (until - date.fromisoformat(config["start"])).days > 36525:
                raise ValueError("future end or greater than 100-year audit is unsupported")
            calendar = schedule(config["start"], until.isoformat())
            completed = [s for s in calendar["sessions"] if datetime.fromisoformat(s["closes_at"]) <= now]
            if not completed:
                raise ValueError("no completed session in requested interval")
            end = completed[-1]["session_date"]
            calendar = schedule(config["start"], end)
            modules = [Path(__file__), Path(__file__).with_name("depth_store.py"),
                Path(__file__).parents[1] / "providers/ibkr_depth.py", Path(__file__).parents[1] / "providers/ibkr.py"]
            versions = {}
            for package in ("exchange-calendars", "pandas", "numpy", "ib_async"):
                try:
                    versions[package] = importlib.metadata.version(package)
                except importlib.metadata.PackageNotFoundError:
                    versions[package] = "NOT_INSTALLED"
            plan = {"schema_version": "ibkr_depth_plan_v1", "config": config, "origin": self.origin,
                "start": config["start"], "end": end, "as_of": now.isoformat(),
                "runtime": {"python": platform.python_version(), "packages": versions},
                "source_sha256": {str(p.relative_to(Path(__file__).parents[1])): digest(p.read_bytes()) for p in modules},
                "calendar_convention": "Pinned XNYS US cash-session reference; venue alignment/listing history not independently verified",
                "basis": "IBKR TRADES documented split-adjusted, not dividend-adjusted; filtered historical feed; units unverified",
                "limits_scope": "per invocation; resume preserves fixed end, identity and observations"}
            root.mkdir(parents=True, exist_ok=False)
            write_bundle(root / "plan", {"plan.json": encode(plan), "calendar.json": encode(calendar)})
            (root / "events").mkdir()
        with writer_lock(root):
            journal = Journal(root)
            if journal.plan["config"] != config or journal.plan["origin"] != self.origin:
                raise ValueError("resume configuration/origin differs from frozen audit")
            return asyncio.run(self._run(journal, resume, permission_reference, read_only_confirmed))

    async def _run(self, journal, resume, permission_reference, read_only_confirmed):
        self.journal = journal
        self.config = journal.plan["config"]
        self.started = self.pacer.clock()
        self.requests = 0
        self.backend = None
        self.restore_pacing()
        journal.append({"kind": "invocation", "started_at": self.stamp(), "resume": resume,
            "host": self.host, "port": self.port, "client_id": self.client_id,
            "read_only_api_operator_confirmed": read_only_confirmed,
            "permission_reference": permission_reference, "startup_account_sync": False})
        reason = "FINISHED"
        try:
            # A fully completed resume does not reconnect just to report a cache hit.
            unfinished = [i for i in self.config["instruments"] if progress(journal, i["security"]["symbol"])[0] is not None]
            if unfinished:
                self.backend = self.backend_factory()
                await self.bounded(self.backend.connect(self.host, self.port, self.client_id), 12)
            for item in unfinished:
                await self.instrument(item)
        except ResourceLimit:
            reason = "RESOURCE_LIMIT"
        except asyncio.CancelledError:
            reason = "CANCELLED"
        except Exception as exc:
            reason = "CONNECTION_OR_CLIENT_FAILURE"
            journal.append({"kind": "run_error", "at": self.stamp(), **self.failure(exc)})
        finally:
            if self.backend is not None:
                try:
                    self.backend.disconnect()
                except Exception as exc:
                    journal.append({"kind": "disconnect_error", "at": self.stamp(), **self.failure(exc)})
            journal.append({"kind": "invocation_finished", "completed_at": self.stamp(),
                "reason": reason, "requests": self.requests})
        reports, _ = summarize(journal)
        return {"status": reason, "plan_sha256": journal.plan_hashes["bundle_sha256"],
                "journal_tip_sha256": journal.tip, "instruments": reports}

    def stamp(self):
        return self.clock().astimezone(UTC).isoformat()

    def failure(self, exc):
        code = error_code(exc)
        category = classify(code, str(exc)) if code is not None else "TIMEOUT" if isinstance(exc, TimeoutError) else "REQUEST_ERROR"
        return {"code": code, "category": category, "exception_type": type(exc).__name__}

    def restore_pacing(self):
        now, mono = self.clock().astimezone(UTC), self.pacer.clock()
        self.pacer.events.clear()
        self.pacer.identical.clear()
        for item in self.journal.events:
            event = item["event"]
            if event["kind"] == "request_started":
                age = max(0, (now - datetime.fromisoformat(event["started_at"])).total_seconds())
                if age < 600:
                    when = mono - age
                    self.pacer.events.append(when)
                    self.pacer.identical[event["signature"]] = when
        self.pacer.events = type(self.pacer.events)(sorted(self.pacer.events))

    async def bounded(self, operation, timeout):
        remaining = self.config["max_runtime_seconds"] - (self.pacer.clock() - self.started)
        if remaining <= 0:
            operation.close()
            raise ResourceLimit()
        try:
            return await asyncio.wait_for(operation, min(remaining, timeout))
        except TimeoutError:
            if self.pacer.clock() - self.started >= self.config["max_runtime_seconds"]:
                raise ResourceLimit() from None
            raise

    async def request_start(self, symbol, operation, parameters):
        if self.requests >= self.config["max_requests"]:
            raise ResourceLimit()
        signature = digest(encode({"symbol": symbol, "operation": operation, **parameters}))
        await self.bounded(self.pacer.wait(signature), self.config["max_runtime_seconds"])
        self.requests += 1
        return self.journal.append({"kind": "request_started", "symbol": symbol,
            "operation": operation, "parameters": parameters, "signature": signature, "started_at": self.stamp()})

    def stop(self, symbol, reason):
        self.journal.append({"kind": "instrument_stop", "symbol": symbol, "reason": reason, "at": self.stamp()})

    async def instrument(self, instrument):
        security = Security(**instrument["security"])
        symbol = security.symbol
        cursor, consecutive_empty = progress(self.journal, symbol)
        await self.request_start(symbol, "qualification", security.record())
        mark = len(self.backend.errors)
        try:
            matches = await self.bounded(self.backend.qualify(security), 20)
            records = [contract_record(c) for c in matches]
            if len(records) != 1:
                raise ValueError("AMBIGUOUS_OR_EMPTY_QUALIFICATION")
            qualified = records[0]
            if (qualified["secType"] != "STK" or type(qualified["conId"]) is not int or qualified["conId"] <= 0 or
                qualified["exchange"] != "SMART" or qualified["symbol"] != security.ibkr_symbol or
                qualified["currency"] != security.currency or qualified["primaryExchange"] != security.primary_exchange or
                (security.con_id is not None and qualified["conId"] != security.con_id)):
                raise ValueError("QUALIFIED_IDENTITY_MISMATCH")
            old = [i["event"]["contract"] for i in self.journal.events if i["event"]["kind"] == "qualification"
                and i["event"].get("symbol") == symbol and i["event"]["status"] == "SUCCESS"]
            if old and old[0] != qualified:
                raise ValueError("QUALIFIED_IDENTITY_CHANGED")
            errors = self.backend.errors[mark:]
            if any(e["category"] != "INFORMATION" for e in errors):
                raise ValueError("QUALIFICATION_CALLBACK_ERROR")
        except (ResourceLimit, asyncio.CancelledError):
            raise
        except Exception as exc:
            allowed = {"AMBIGUOUS_OR_EMPTY_QUALIFICATION", "QUALIFIED_IDENTITY_MISMATCH", "QUALIFIED_IDENTITY_CHANGED", "QUALIFICATION_CALLBACK_ERROR"}
            self.journal.append({"kind": "qualification", "symbol": symbol, "status": "FAILED", "at": self.stamp(),
                "reason": str(exc) if isinstance(exc, ValueError) and str(exc) in allowed else "QUALIFICATION_FAILED",
                "matches": locals().get("records", []), "errors": self.backend.errors[mark:], **self.failure(exc)})
            self.stop(symbol, "QUALIFICATION_FAILED")
            return
        self.journal.append({"kind": "qualification", "symbol": symbol, "status": "SUCCESS", "at": self.stamp(), "contract": qualified})
        contract = matches[0]
        heads = [i["event"] for i in self.journal.events if i["event"]["kind"] == "head"
                 and i["event"].get("symbol") == symbol and i["event"]["status"] == "SUCCESS"]
        head = head_date(heads[0]["timestamp"]) if heads else None
        if self.config["head_timestamp"] and head is None:
            await self.request_start(symbol, "head_timestamp", {"conId": qualified["conId"], "whatToShow": "TRADES", "useRTH": True, "formatDate": 2})
            mark = len(self.backend.errors)
            try:
                stamp = await self.bounded(self.backend.head_timestamp(contract), 35)
                if not isinstance(stamp, datetime) or stamp.tzinfo is None:
                    raise ValueError("invalid head timestamp")
                head = head_date(stamp.isoformat())
                if head > self.journal.plan["end"] or any(e["category"] != "INFORMATION" for e in self.backend.errors[mark:]):
                    raise ValueError("unusable head timestamp")
                self.journal.append({"kind": "head", "symbol": symbol, "status": "SUCCESS", "timestamp": stamp.isoformat(), "at": self.stamp()})
            except (ResourceLimit, asyncio.CancelledError):
                raise
            except Exception as exc:
                head = None
                self.journal.append({"kind": "head", "symbol": symbol, "status": "FAILED", "at": self.stamp(),
                                     "errors": self.backend.errors[mark:], **self.failure(exc)})
        floor = max(self.journal.plan["start"], head or self.journal.plan["start"])
        expected = [s["session_date"] for s in self.journal.calendar["sessions"] if floor <= s["session_date"] <= self.journal.plan["end"]]
        first_expected = expected[0] if expected else floor
        for _ in range(self.config["max_windows_per_instrument"]):
            start = max(floor, (date.fromisoformat(cursor) - timedelta(days=self.config["window_days"] - 1)).isoformat())
            anchor = datetime.combine(date.fromisoformat(cursor) + timedelta(days=1), time(), UTC)
            duration = (date.fromisoformat(cursor) - date.fromisoformat(start)).days + 1
            # IB requires year units for durations above 365 days. Preserve the
            # exact audit bounds separately and retain any extra native rows.
            duration_str = f"{duration} D" if duration <= 365 else f"{(duration + 364) // 365} Y"
            params = {"endDateTime": anchor.strftime("%Y%m%d-%H:%M:%S"), "durationStr": duration_str,
                "barSizeSetting": "1 day", "whatToShow": "TRADES", "useRTH": True, "formatDate": 1, "keepUpToDate": False, "timeout": 30}
            for attempt in range(1, self.config["max_attempts"] + 1):
                requested = await self.request_start(symbol, "historical", {"conId": qualified["conId"], **params})
                entry = {"kind": "window", "symbol": symbol, "start": start, "end": cursor,
                    "attempt": attempt, "parameters": params, "request_checkpoint_sha256": requested["hashes"]["bundle_sha256"],
                    "started_at": requested["event"]["started_at"], "status": "REQUEST_FAILED", "decision": "STOP", "next_cursor": cursor}
                mark = len(self.backend.errors)
                extra, rows = {}, []
                try:
                    returned = await self.bounded(self.backend.historical(contract, params), 35)
                    extra = capture_return(returned)
                    entry["errors"] = self.backend.errors[mark:]
                    error = next((e for e in entry["errors"] if e["category"] != "INFORMATION"), None)
                    if error:
                        entry.update(status=error["category"], category=error["category"], code=error.get("code"))
                    else:
                        entry["status"] = "SUCCESS" if returned else "EMPTY_RESPONSE"
                except (ResourceLimit, asyncio.CancelledError) as exc:
                    entry.update(status="CANCELLED", category=type(exc).__name__, completed_at=self.stamp())
                    self.journal.append(entry)
                    raise
                except Exception as exc:
                    entry.update(self.failure(exc))
                    entry["status"] = entry["category"]
                    if hasattr(exc, "bars"):
                        extra = capture_return(exc.bars)
                entry["completed_at"] = self.stamp()
                if entry["status"] == "SUCCESS":
                    provisional = {"event": entry, "files": extra, "path": "pending",
                        "hashes": {"files": {k: digest(v) for k, v in extra.items()}, "bundle_sha256": "pending"}}
                    rows, _, _ = window_rows(provisional, security.record())
                    if rows:
                        earliest = min(r["session_date"] for r in rows)
                        entry["decision"] = "BOUNDARY" if earliest <= first_expected else "ADVANCE"
                        entry["next_cursor"] = None if entry["decision"] == "BOUNDARY" else min(
                            (date.fromisoformat(cursor) - timedelta(days=1)).isoformat(),
                            (date.fromisoformat(earliest) + timedelta(days=self.config["overlap_days"] - 1)).isoformat())
                        consecutive_empty = 0
                    else:
                        entry["status"] = "OUTSIDE_WINDOW_ONLY"
                retryable = entry["status"] in {"EMPTY_RESPONSE", "NO_DATA", "PACING", "TIMEOUT", "CONNECTION"}
                if entry["status"] != "SUCCESS" and retryable and attempt < self.config["max_attempts"]:
                    entry["decision"] = "RETRY"
                elif entry["status"] in {"EMPTY_RESPONSE", "NO_DATA"}:
                    consecutive_empty += 1
                    if start > floor and consecutive_empty < self.config["max_consecutive_empty"]:
                        entry.update(decision="ADVANCE", next_cursor=min(
                            (date.fromisoformat(cursor)-timedelta(days=1)).isoformat(),
                            (date.fromisoformat(start)+timedelta(days=self.config["overlap_days"]-1)).isoformat()))
                self.journal.append(entry, extra)
                if entry["decision"] == "RETRY":
                    await self.bounded(self.sleep(min(60, 15 * 2 ** (attempt - 1))), 65)
                    continue
                break
            if entry["decision"] == "STOP":
                self.stop(symbol, "EMPTY_LIMIT_OR_UNCONFIRMED_BOUNDARY" if entry["status"] in {"EMPTY_RESPONSE", "NO_DATA"}
                          else "DATA_PERMISSION" if entry["status"] == "DATA_PERMISSION" else "REQUEST_FAILED")
                return
            cursor = entry["next_cursor"]
            if cursor is None:
                self.stop(symbol, "OBSERVED_SEARCH_BOUNDARY")
                return
        self.stop(symbol, "WINDOW_LIMIT")
