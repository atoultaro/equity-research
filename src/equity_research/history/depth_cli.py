"""Explicit live audit and separate offline report commands."""

import json
from pathlib import Path


def register(operations):
    audit = operations.add_parser("ibkr-depth-audit", help="operator-started, read-only local IBKR depth audit")
    audit.add_argument("--config", type=Path, required=True)
    audit.add_argument("--output", type=Path, required=True, help="new audit journal, or existing journal with --resume")
    audit.add_argument("--resume", action="store_true")
    audit.add_argument("--connect", action="store_true", help="explicitly initiate the configured local historical connection")
    audit.add_argument("--read-only-api-confirmed", action="store_true", help="operator confirms socket clients and Read-Only API enabled")
    audit.add_argument("--permission-reference", required=True)
    audit.add_argument("--ibkr-host", default="127.0.0.1", choices=("127.0.0.1", "::1", "localhost"))
    audit.add_argument("--ibkr-port", type=int, required=True)
    audit.add_argument("--ibkr-client-id", type=int, required=True)
    report = operations.add_parser("ibkr-depth-report", help="freeze a self-contained offline report from audit checkpoints")
    report.add_argument("--audit", type=Path, required=True)
    report.add_argument("--output", type=Path, required=True)


def dispatch(args):
    from ..ingestion.storage import encode
    if args.operation == "ibkr-depth-report":
        from .depth_store import freeze_report
        hashes = freeze_report(args.audit, args.output)
        print(encode({"report": str(args.output), "sha256": hashes["bundle_sha256"]}).decode(), end="")
        return 0
    from .depth import DepthAudit
    audit = DepthAudit(host=args.ibkr_host, port=args.ibkr_port, client_id=args.ibkr_client_id)
    result = audit.run(json.loads(args.config.read_bytes()), args.output, resume=args.resume,
        connect=args.connect, read_only_confirmed=args.read_only_api_confirmed,
        permission_reference=args.permission_reference)
    summary = {k: result[k] for k in ("status", "plan_sha256", "journal_tip_sha256")}
    summary["instruments"] = [{k: r[k] for k in ("symbol", "status", "observed_sessions", "actual_earliest_bar",
        "actual_latest_bar", "resume_cursor", "stop_reason")} for r in result["instruments"]]
    print(encode(summary).decode(), end="")
    return 0 if result["status"] == "FINISHED" and all(r["status"] in {"complete", "exhausted"}
        for r in result["instruments"]) else 130 if result["status"] == "CANCELLED" else 3
