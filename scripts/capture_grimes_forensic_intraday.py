"""Four fixed PR9B historical requests; never imported by automated acquisition."""

import argparse
import asyncio
from datetime import UTC, date, datetime, timedelta
import logging
from pathlib import Path

from equity_research.history.contracts import Security
from equity_research.ingestion.frames import pack
from equity_research.ingestion.storage import digest, encode, seal
from equity_research.providers.ibkr import Pacer, contract_record, error_code, make_backend

WINDOWS = (("CLMT", 715002751, "NASDAQ", "2026-10-19"),
           ("TEVA", 922990633, "NYSE", "2026-10-21"),
           ("GME", 36285627, "NYSE", "2026-10-22"),
           ("GME", 36285627, "NYSE", "2026-10-23"))


async def capture(backend, *, port, client_id, pacer):
    result = {"schema_version": "pr9b_intraday_v1", "provider": "ibkr",
              "started_at": datetime.now(UTC).isoformat(), "port": port,
              "client_id": client_id, "host": "127.0.0.1", "windows": [],
              "startup_account_sync": False, "volume_units": "UNVERIFIED"}
    try:
        await backend.connect("127.0.0.1", port, client_id)
        for symbol, con_id, exchange, day in WINDOWS:
            entry = {"symbol": symbol, "con_id": con_id, "session": day,
                     "started_at": datetime.now(UTC).isoformat(), "status": "REQUEST_FAILED",
                     "native_bars": []}
            result["windows"].append(entry)
            security = Security(symbol, f"grimes-lifecycle-20261026:{symbol}",
                                "PR19 retained qualified identity", symbol, symbol, exchange,
                                exchange, con_id=con_id)
            params = {"endDateTime": (date.fromisoformat(day) + timedelta(days=1)).strftime("%Y%m%d-00:00:00"),
                      "durationStr": "1 D", "barSizeSetting": "5 mins", "whatToShow": "TRADES",
                      "useRTH": True, "formatDate": 2, "keepUpToDate": False, "timeout": 30}
            entry["parameters"] = params
            mark = len(backend.errors)
            try:
                matches = await backend.qualify(security)
                entry["qualification"] = [contract_record(c) for c in matches]
                expected = {"conId": con_id, "symbol": symbol, "secType": "STK",
                            "exchange": "SMART", "primaryExchange": exchange, "currency": "USD"}
                if len(matches) != 1 or any(entry["qualification"][0][k] != v for k, v in expected.items()):
                    entry["status"] = "IDENTITY_REJECTED"
                    continue
                await pacer.wait(digest(encode({"conId": con_id, **params})))
                bars = await asyncio.wait_for(backend.historical(matches[0], params), 35)
                entry["native_bars"] = [{name: pack(getattr(bar, name, None)) for name in
                                         ("date", "open", "high", "low", "close", "volume", "average", "barCount")}
                                        for bar in bars]
                errors = backend.errors[mark:]
                entry["status"] = ("REQUEST_FAILED" if any(e["category"] != "INFORMATION" for e in errors)
                                   else "SUCCESS" if bars else "EMPTY_RESPONSE")
            except Exception as exc:
                entry.update(status="TIMEOUT" if isinstance(exc, TimeoutError) else "REQUEST_FAILED",
                             error_code=error_code(exc), exception_type=type(exc).__name__)
            finally:
                entry["errors"] = backend.errors[mark:]
                entry["completed_at"] = datetime.now(UTC).isoformat()
    except Exception as exc:
        result["connection_error"] = {"code": error_code(exc), "exception_type": type(exc).__name__}
    finally:
        backend.disconnect()
        result["completed_at"] = datetime.now(UTC).isoformat()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--connect", action="store_true")
    parser.add_argument("--read-only-api-confirmed", action="store_true")
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--client-id", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.connect or not args.read_only_api_confirmed:
        parser.error("explicit connection and current read-only confirmation required")
    if not 1 <= args.port <= 65535 or not 0 < args.client_id < 2**31:
        parser.error("invalid endpoint")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.mkdir(exist_ok=False)
    # Suppress propagation of arbitrary broker diagnostics but preserve the
    # backend's sanitized timeout/error handler. Globally disabling logging
    # would also disable that handler and could mislabel a timeout as empty.
    logger = logging.getLogger('ib_async')
    previous = logger.level, logger.propagate, logger.handlers[:]
    logger.setLevel(logging.WARNING)
    logger.propagate = False
    logger.handlers = [logging.NullHandler()]
    try:
        result = asyncio.run(capture(make_backend(), port=args.port, client_id=args.client_id, pacer=Pacer()))
    finally:
        logger.setLevel(previous[0])
        logger.propagate, logger.handlers = previous[1:]
    hashes = seal(args.output, {"capture.json": encode(result)})
    print({"bundle_sha256": hashes["bundle_sha256"],
           "windows": [(w["symbol"], w["session"], w["status"], len(w["native_bars"])) for w in result["windows"]],
           "connection_error": result.get("connection_error")})


if __name__ == "__main__":
    main()
