"""Single-request yfinance boundary. No client import until fetch is explicitly called."""

from datetime import UTC, date, datetime, timedelta
import importlib.metadata
import logging
from pathlib import Path
import re
from uuid import uuid4

from ..ingestion.storage import seal
from ..ingestion.snapshots import snapshot_files

CLIENT_VERSION = "0.2.66"


def provider_symbol(symbol: str) -> str:
    if not isinstance(symbol, str) or not re.fullmatch(r"[A-Za-z0-9^][A-Za-z0-9^./=-]{0,31}", symbol):
        raise ValueError("invalid single research symbol")
    return symbol.upper().replace(".", "-").replace("/", "-")


def request_record(symbol: str, start: str, end: str) -> dict:
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    if first.isoformat() != start or last.isoformat() != end:
        raise ValueError("dates must use YYYY-MM-DD")
    if first > last:
        raise ValueError("start must not follow end")
    mapped = provider_symbol(symbol)
    return {"schema_version": "yahoo_request_v1", "provider": "yahoo", "origin": "yahoo_client",
            "research_symbol": symbol.upper(), "provider_symbol": mapped, "start": start, "end": end,
            "parameters": {"tickers": [mapped], "start": start, "end": (last + timedelta(days=1)).isoformat(),
                           "interval": "1d", "auto_adjust": False, "back_adjust": False,
                           "actions": True, "repair": False, "keepna": True, "rounding": False,
                           "prepost": False, "group_by": "ticker", "threads": False,
                           "ignore_tz": False, "multi_level_index": True, "progress": False,
                           "period": None, "timeout": 15.0}}


def now_utc():
    return datetime.now(UTC)


def fetch(symbol: str, start: str, end: str, output: Path, *, clock=now_utc) -> dict:
    request = request_record(symbol, start, end)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir(exist_ok=False)  # Reject overwrite before any network side effect.
    begun = clock().astimezone(UTC)
    acquisition = {"attempt_id": str(uuid4()), "started_at": begun.isoformat(), "client": "yfinance",
                   "client_version": None, "historical_availability": "unknown",
                   "status": "REQUEST_FAILED", "errors": [], "coverage": None,
                   "wire_capture": "not_available_through_public_download_interface"}
    frame = None
    # Logs may contain URLs, local paths or credentials. Keep safe categories only.
    class Errors(logging.Handler):
        def emit(self, record):
            if record.levelno >= logging.ERROR:
                text = record.getMessage().lower()
                category = "TIMEOUT" if "timeout" in text or "timed out" in text else (
                    "RATE_LIMIT" if "429" in text or "rate limit" in text else "CLIENT_REPORTED_ERROR")
                acquisition["errors"].append({"code": category, "source": "client_log"})

    logger, handler = logging.getLogger("yfinance"), Errors()
    logger.addHandler(handler)
    try:
        version = importlib.metadata.version("yfinance")
        acquisition["client_version"] = version
        if version != CLIENT_VERSION:
            raise ValueError("unsupported client version")
        import yfinance as yf
        frame = yf.download(**request["parameters"])
        from ..ingestion.frames import capture_frame
        from ..ingestion.canonical import convert
        from ..ingestion.calendar import schedule
        capture_frame(frame)  # Explicit failure if return is not a supported frame.
        if frame.empty:
            acquisition["status"] = "REQUEST_FAILED" if acquisition["errors"] else "EMPTY_RESPONSE"
        else:
            converted = convert(frame, security_id=None, provider_symbol=request["provider_symbol"],
                                frame_sha256="pending", snapshot_sha256="pending")
            dates = [r["session_date"] for r in converted["rows"] if r["session_date"]]
            expected = schedule(start, end)["sessions"]
            acquisition["coverage"] = {"rows": len(frame), "first": min(dates) if dates else None,
                                        "last": max(dates) if dates else None}
            schema_errors = {"COLUMN_SCHEMA_INVALID", "MISSING_COLUMN", "INVALID_SESSION_DATE"}
            if any(i["code"] in schema_errors for i in converted["issues"]):
                acquisition["status"] = "SCHEMA_FAILURE"
            elif (acquisition["errors"] or set(dates) != {s["session_date"] for s in expected}
                  or any(datetime.fromisoformat(s["closes_at"]) > begun for s in expected)):
                acquisition["status"] = "PARTIAL_RESPONSE"
            else:
                acquisition["status"] = "SUCCESS"
    except Exception as exc:
        acquisition["errors"].append({"code": "TIMEOUT" if isinstance(exc, TimeoutError) else "ACQUISITION_ERROR",
                                       "exception_type": type(exc).__name__})
        # Never persist arbitrary exception text, URLs or filesystem paths.
    finally:
        logger.removeHandler(handler)
    acquisition["completed_at"] = clock().astimezone(UTC).isoformat()
    try:
        files = snapshot_files(request, acquisition, frame)
    except (ValueError, TypeError):
        acquisition["status"] = "SCHEMA_FAILURE"
        acquisition["errors"].append({"code": "UNSUPPORTED_CLIENT_RETURN"})
        files = snapshot_files(request, acquisition)
    seal(output, files)
    return acquisition
