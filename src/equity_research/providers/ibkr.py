"""Bounded daily US equity acquisition. Optional ib_async is imported only on use."""

import asyncio
from collections import deque
from datetime import date, datetime, time, timedelta, UTC
import importlib.metadata
import logging
from pathlib import Path
import time as monotonic_time

from ..history.contracts import interval, now_utc
from ..history.normalize import read_acquisition
from ..ingestion.frames import capture_frame, pack
from ..ingestion.storage import digest, encode, seal

CLIENT_VERSION = "2.1.0"
PERMISSION_CODES = {354, 10089, 10090, 10167, 10168, 10186}
INFORMATION_CODES = {2104, 2106, 2107, 2108, 2158}


def error_code(exc):
    # ib_async.wrapper.RequestError uses .code, not the TWS callback's
    # errorCode spelling. Retain numeric codes only, never arbitrary attributes.
    value = getattr(exc, "code", getattr(exc, "errorCode", None))
    return value if type(value) is int else None


def classify(code, message=""):
    text = message.lower()
    if code in PERMISSION_CODES or (code == 162 and any(
            word in text for word in ("permission", "subscription", "not subscribed"))):
        return "DATA_PERMISSION"
    if code == 420 or (code == 162 and "pacing" in text):
        return "PACING"
    if code in {165, 166} or (code == 162 and "no data" in text):
        return "NO_DATA"
    if code in {1100, 1101, 1102, 502, 504}:
        return "CONNECTION"
    return "INFORMATION" if code in INFORMATION_CODES else "PROVIDER_ERROR"


class Pacer:
    """Serial requests: 60/600s, at least 2s apart, identical requests 15s apart.

    Shared across all symbols handled by one adapter instance. No random jitter,
    concurrency or retry amplification. Other processes/sessions are outside scope.
    """

    def __init__(self, *, clock=monotonic_time.monotonic, sleep=asyncio.sleep):
        self.clock, self.sleep = clock, sleep
        self.events, self.identical = deque(), {}

    async def wait(self, signature):
        while True:
            now = self.clock()
            while self.events and self.events[0] <= now - 600:
                self.events.popleft()
            delay = max(0, self.events[-1] + 2 - now if self.events else 0,
                        self.events[0] + 600 - now if len(self.events) >= 60 else 0,
                        self.identical.get(signature, now - 15) + 15 - now)
            if delay <= 0:
                self.events.append(now)
                self.identical[signature] = now
                return
            await self.sleep(min(delay, 60))


def make_backend():
    """Use the low-level handshake, avoiding IB.connectAsync's account sync.

    In 2.1.0 positions may be requested even with StartupFetchNONE. The default
    IB._onError also requests an account summary on code 1102. Neither behavior
    belongs in a market-data adapter. The pinned subclass suppresses that callback.
    No application calls to account/order/position APIs are exposed here.
    """
    if importlib.metadata.version("ib_async") != CLIENT_VERSION:
        raise ValueError(f"ib_async=={CLIENT_VERSION} required")
    from ib_async import IB, Stock

    class HistoricalIB(IB):
        def _onError(self, reqId, errorCode, errorString, contract):
            pass  # Deliberately no automatic account-summary resubscription.

    class Backend:
        client_version = CLIENT_VERSION

        def __init__(self):
            self.ib = HistoricalIB()
            self.ib.RaiseRequestErrors = True
            self.errors = []
            errors = self.errors

            class ClientErrors(logging.Handler):
                def emit(self, record):
                    text = record.getMessage().lower()
                    if record.levelno >= logging.ERROR or (record.levelno >= logging.WARNING and "timeout" in text):
                        errors.append({"code": None, "category": "TIMEOUT" if "timeout" in text else "CLIENT_REPORTED_ERROR"})

            self._logger = logging.getLogger("ib_async.ib")
            self._handler = ClientErrors()
            self._logger.addHandler(self._handler)

            def on_error(req_id, code, text, contract=None):
                self.errors.append({"code": int(code), "category": classify(code, text)})
            self.ib.errorEvent += on_error

        async def connect(self, host, port, client_id):
            self.ib.wrapper.clientId = client_id
            # A local TWS/Gateway must already be running/authenticated. This
            # handshake receives account identifiers from TWS but requests no data
            # about accounts, positions, executions or orders and stores none.
            await self.ib.client.connectAsync(host, port, client_id, timeout=10)

        async def qualify(self, security):
            contract = Stock(symbol=security.ibkr_symbol, exchange="SMART", currency=security.currency,
                             primaryExchange=security.primary_exchange, conId=security.con_id or 0)
            details = await asyncio.wait_for(self.ib.reqContractDetailsAsync(contract), 15)
            return [d.contract for d in details]

        async def historical(self, contract, params):
            return await self.ib.reqHistoricalDataAsync(contract, **params)

        def disconnect(self):
            try:
                self.ib.disconnect()
            finally:
                self._logger.removeHandler(self._handler)

    return Backend()


def contract_record(contract):
    return {name: getattr(contract, name, None) for name in
            ("conId", "symbol", "secType", "exchange", "primaryExchange", "currency", "localSymbol", "tradingClass")}


class IBKRDailyProvider:
    name = "ibkr"

    def __init__(self, *, host="127.0.0.1", port=None, client_id=None, backend_factory=make_backend,
                 clock=now_utc, pacer=None, sleep=asyncio.sleep, max_attempts=3, origin="ibkr_client"):
        if host not in {"127.0.0.1", "::1", "localhost"}:
            raise ValueError("a local TWS/Gateway endpoint is required")
        if type(port) is not int or not 1 <= port <= 65535 or type(client_id) is not int or client_id <= 0:
            raise ValueError("explicit port and positive nonzero client_id are required")
        if type(max_attempts) is not int or not 1 <= max_attempts <= 3:
            raise ValueError("max_attempts must be 1..3")
        if origin not in {"ibkr_client", "synthetic"} or (origin == "synthetic" and backend_factory is make_backend):
            raise ValueError("synthetic origin requires an injected offline backend")
        self.origin = origin
        self.host, self.port, self.client_id = host, port, client_id
        self.backend_factory, self.clock = backend_factory, clock
        self.pacer, self.sleep, self.max_attempts = pacer or Pacer(), sleep, max_attempts

    def fetch_daily(self, security, start, end, output):
        interval(start, end)
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.mkdir(exist_ok=False)  # Before connection, including failed attempts.
        return asyncio.run(self._fetch(security, start, end, output))

    async def _fetch(self, security, start, end, output):
        import pandas as pd

        request = {"schema_version": "ibkr_request_v1", "provider": "ibkr", "origin": self.origin,
                   "research_symbol": security.symbol, "provider_symbol": security.ibkr_symbol,
                   "security": security.record(), "start": start, "end": end,
                   "parameters": {"exchange": "SMART", "whatToShow": "TRADES", "useRTH": True,
                                  "barSizeSetting": "1 day", "formatDate": 1, "keepUpToDate": False,
                                  "market_data_type_requested": "historical_TRADES",
                                  "streaming_market_data_type_observed": "unknown_not_requested",
                                  "chunk_calendar_days": 30, "timeout": 30,
                                  "max_attempts": self.max_attempts, "port": self.port,
                                  "client_id": self.client_id, "local_endpoint": True,
                                  "startup_account_sync": False}}
        begun = self.clock().astimezone(UTC)
        acq = {"schema_version": "ibkr_acquisition_v1", "started_at": begun.isoformat(),
               "client": "synthetic_ibkr_backend" if self.origin == "synthetic" else "ib_async",
               "client_version": None, "expected_client_version": CLIENT_VERSION,
               "status": "REQUEST_FAILED", "errors": [], "requests": [], "qualification": [],
               "qualified_contract": None, "historical_availability": "unknown",
               "capture_level": "client_return_native_plus_bounded_daily_frame", "coverage": None,
               "frame_selection": "per_chunk_requested_interval", "excluded_native_rows": []}
        records, native_bars, backend = [], [], None
        try:
            backend = self.backend_factory()
            acq["client_version"] = getattr(backend, "client_version", None)
            await backend.connect(self.host, self.port, self.client_id)
            matches = await backend.qualify(security)
            acq["qualification"] = [contract_record(c) for c in matches]
            if len(matches) != 1:
                raise ValueError("AMBIGUOUS_OR_EMPTY_QUALIFICATION")
            contract = matches[0]
            qualified = acq["qualification"][0]
            if (qualified["secType"] != "STK" or type(qualified["conId"]) is not int or qualified["conId"] <= 0 or
                    qualified["exchange"] != "SMART" or
                    qualified["symbol"] != security.ibkr_symbol or qualified["currency"] != security.currency or
                    qualified["primaryExchange"] != security.primary_exchange or
                    (security.con_id is not None and qualified["conId"] != security.con_id)):
                raise ValueError("QUALIFIED_IDENTITY_MISMATCH")
            acq["qualified_contract"] = qualified
            first, last = interval(start, end)
            cursor = first
            chunks_failed = 0
            while cursor <= last:
                final = min(last, cursor + timedelta(days=29))
                anchor = datetime.combine(final + timedelta(days=1), time(), UTC)
                params = {"endDateTime": anchor.strftime("%Y%m%d-%H:%M:%S"),
                          "durationStr": f"{(final - cursor).days + 1} D", "barSizeSetting": "1 day",
                          "whatToShow": "TRADES", "useRTH": True, "formatDate": 1,
                          "keepUpToDate": False, "timeout": 30}
                success = False
                for attempt in range(1, self.max_attempts + 1):
                    await self.pacer.wait(digest(encode({"conId": qualified["conId"], **params})))
                    mark = len(backend.errors)
                    entry = {"start": cursor.isoformat(), "end": final.isoformat(),
                             "attempt": attempt, "parameters": params, "status": "REQUEST_FAILED"}
                    acq["requests"].append(entry)
                    try:
                        bars = await asyncio.wait_for(backend.historical(contract, params), 35)
                        errors = backend.errors[mark:]
                        if any(e["category"] != "INFORMATION" for e in errors):
                            category = next(e["category"] for e in errors if e["category"] != "INFORMATION")
                            entry.update(errors=errors, category=category)
                        else:
                            for bar in bars:
                                native_bars.append({"chunk_start": cursor.isoformat(), "chunk_end": final.isoformat(),
                                                    "fields": {name: pack(getattr(bar, name, None)) for name in
                                                               ("date", "open", "high", "low", "close", "volume", "average", "barCount")}})
                                raw = bar.date
                                if type(raw) is date:
                                    day = raw.isoformat()
                                elif isinstance(raw, str) and len(raw) == 8 and raw.isdigit():
                                    day = datetime.strptime(raw, "%Y%m%d").date().isoformat()
                                else:
                                    day = str(raw)  # Invalid timestamps remain diagnostics.
                                # IBKR can return a longer lookback than the
                                # requested calendar chunk. Keep every native bar
                                # above, but explicitly bound the analysis frame.
                                # Do not deduplicate conflicting in-window rows.
                                try:
                                    valid_day = date.fromisoformat(day).isoformat() == day
                                except ValueError:
                                    valid_day = False
                                native_index = len(native_bars) - 1
                                if valid_day and not cursor.isoformat() <= day <= final.isoformat():
                                    acq["excluded_native_rows"].append({"native_row": native_index,
                                        "session_date": day, "chunk_start": cursor.isoformat(),
                                        "chunk_end": final.isoformat(), "reason": "OUTSIDE_REQUESTED_CHUNK"})
                                    continue
                                records.append({"Date": day, **{name.title(): getattr(bar, name, None)
                                                                for name in ("open", "high", "low", "close", "volume")},
                                                "_chunk_start": cursor.isoformat(), "_chunk_end": final.isoformat(),
                                                "_native_row": native_index})
                            entry.update(status="SUCCESS" if bars else "EMPTY_RESPONSE", rows=len(bars))
                            success = True
                            break
                    except Exception as exc:
                        code = error_code(exc)
                        category = classify(code, str(exc)) if code is not None else (
                            "TIMEOUT" if isinstance(exc, TimeoutError) else "REQUEST_ERROR")
                        entry.update(category=category, error_code=code, exception_type=type(exc).__name__)
                    acq["errors"].append({"code": entry.get("error_code"), "category": category,
                                           "chunk_start": cursor.isoformat(), "attempt": attempt})
                    if category not in {"PACING", "TIMEOUT", "CONNECTION"}:
                        break
                    if attempt < self.max_attempts:
                        await self.sleep(min(60, 15 * 2 ** (attempt - 1)))
                if not success:
                    chunks_failed += 1
                    if entry.get("category") == "DATA_PERMISSION":
                        break  # No subscription workaround or retries.
                cursor = final + timedelta(days=1)
            acq["status"] = "PARTIAL_RESPONSE" if chunks_failed else ("SUCCESS" if records else "EMPTY_RESPONSE")
        except Exception as exc:
            code = error_code(exc)
            category = classify(code, str(exc)) if code is not None else "ACQUISITION_ERROR"
            # Persist controlled identity reasons; never arbitrary diagnostic text.
            reason = str(exc) if isinstance(exc, ValueError) and str(exc) in {
                "AMBIGUOUS_OR_EMPTY_QUALIFICATION", "QUALIFIED_IDENTITY_MISMATCH"} else category
            acq["errors"].append({"code": code, "category": reason, "exception_type": type(exc).__name__})
        finally:
            if backend is not None:
                acq["errors"].extend(backend.errors)
                try:
                    backend.disconnect()
                except Exception as exc:
                    acq["errors"].append({"category": "DISCONNECT_ERROR", "exception_type": type(exc).__name__})
        # Chunk bounds are retained in native rows sidecar; no boundary dedup.
        acq["native_row_chunks"] = [{"start": r.pop("_chunk_start"), "end": r.pop("_chunk_end")} for r in records]
        acq["native_row_indices"] = [r.pop("_native_row") for r in records]
        frame = pd.DataFrame(records, columns=["Date", "Open", "High", "Low", "Close", "Volume"]).set_index("Date")
        acq["completed_at"] = self.clock().astimezone(UTC).isoformat()
        files = {"request.json": encode(request), "returned_frame.json": capture_frame(frame),
                 "returned_bars.json": encode({"schema_version": "ibkr_native_daily_v1", "bars": native_bars})}
        acq["content_sha256"] = digest(encode({k: digest(v) for k, v in sorted(files.items())}))
        # Reconcile the client-return before sealing final status/coverage.
        from ..ingestion.canonical import convert
        from ..ingestion.calendar import schedule
        canonical = convert(frame, security_id=security.security_id, provider_symbol=security.ibkr_symbol,
                            frame_sha256="pending", snapshot_sha256="pending")
        dates = [r["session_date"] for r in canonical["rows"] if r["session_date"]]
        expected = schedule(start, end)["sessions"]
        acq["coverage"] = {"rows": len(records), "first": min(dates) if dates else None,
                           "last": max(dates) if dates else None, "native_rows": len(native_bars)}
        if acq["status"] == "SUCCESS" and (any(i["status"] == "FAIL" for i in canonical["issues"]) or
                set(dates) != {s["session_date"] for s in expected} or
                any(datetime.fromisoformat(s["closes_at"]) > begun for s in expected)):
            acq["status"] = "PARTIAL_RESPONSE"
        files["acquisition.json"] = encode(acq)
        seal(output, files)
        return read_acquisition(output, security)
