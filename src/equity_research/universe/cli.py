"""Explicit offline imports, snapshots, queries and audits."""

import json
from pathlib import Path

from ..ingestion.storage import encode


def register(commands):
    root = commands.add_parser("universe", help="offline historical-universe operations")
    sub = root.add_subparsers(dest="universe_command", required=True)
    master = sub.add_parser("import-master")
    master.add_argument("--capture", type=Path, required=True)
    master.add_argument("--output", type=Path, required=True)
    panel = sub.add_parser("freeze-panel")
    panel.add_argument("--capture", type=Path, action="append", required=True)
    panel.add_argument("--calendar", type=Path, required=True)
    panel.add_argument("--base", type=Path)
    panel.add_argument("--output", type=Path, required=True)
    build = sub.add_parser("build")
    build.add_argument("--master", type=Path, required=True)
    build.add_argument("--panel", type=Path, required=True)
    build.add_argument("--definition", type=Path, required=True)
    build.add_argument("--month", action="append", required=True)
    build.add_argument("--decisions", type=Path, help="optional month -> aware decision timestamp JSON")
    build.add_argument("--output", type=Path, required=True)
    for action in ("members", "changes", "validate"):
        query = sub.add_parser(action)
        query.add_argument("--bundle", type=Path, required=True)
        query.add_argument("--master", type=Path, required=True)
        query.add_argument("--panel", type=Path, required=True)
        if action == "members":
            query.add_argument("--date", required=True)
            query.add_argument("--decision-timestamp", required=True)
    audit = sub.add_parser("audit-master")
    audit.add_argument("--master", type=Path, required=True)


def dispatch(args):
    from .master import import_master, SecurityMaster
    from .panel import freeze_panel
    from .selection import build_universe, HistoricalUniverse
    action = args.universe_command
    if action == "import-master":
        result = import_master(args.capture, args.output)
    elif action == "audit-master":
        result = SecurityMaster(args.master).quality
    elif action == "freeze-panel":
        result = freeze_panel(args.capture, json.loads(args.calendar.read_bytes()), args.output, base=args.base)
    elif action == "build":
        result = build_universe(args.master, args.panel, json.loads(args.definition.read_bytes()), args.month,
                                args.output, decisions=json.loads(args.decisions.read_bytes()) if args.decisions else None)
    else:
        universe = HistoricalUniverse(args.bundle, master=args.master, panel=args.panel)
        if action == "members":
            result = universe.members_as_of(args.date, decision_timestamp=args.decision_timestamp)
        elif action == "changes":
            result = universe.changes
        else:
            result = {"status": "VALID", "bundle_sha256": universe.content_sha256, "quality": universe.quality}
    print(encode(result).decode(), end="")
    return 0
