"""Offline expert-study CLI. All live acquisition remains in PR14's command."""

import json
from pathlib import Path


def register(commands):
    command = commands.add_parser("expert", help="offline descriptive expert-trade dossiers")
    operations = command.add_subparsers(dest="expert_operation", required=True)
    capture = operations.add_parser("freeze-inputs")
    for name in ("research", "audits", "output"):
        capture.add_argument("--" + name, required=True, type=Path)
    study = operations.add_parser("study")
    study.add_argument("--inputs", required=True, type=Path)
    study.add_argument("--output", required=True, type=Path)
    replay = operations.add_parser("replay")
    replay.add_argument("--study", required=True, type=Path)
    replay.add_argument("--output", required=True, type=Path)
    futures = operations.add_parser("import-es", help="optional verified local ES 5-minute CSV import; never connects")
    for name in ("csv", "metadata", "calendar", "output"):
        futures.add_argument("--" + name, required=True, type=Path)


def dispatch(args):
    from ..ingestion.storage import encode, write_bundle
    from .inputs import freeze_inputs
    from .study import freeze_study, load_study
    if args.expert_operation == "freeze-inputs":
        config = json.loads(args.audits.read_bytes())
        result = freeze_inputs(json.loads(args.research.read_bytes()), [(r["path"], r["symbols"]) for r in config], args.output)
    elif args.expert_operation == "study":
        result = freeze_study(args.inputs, args.output)
    elif args.expert_operation == "replay":
        study = load_study(args.study)
        result = write_bundle(args.output, study["files"])
    else:
        from .futures import import_es
        result = import_es(args.csv, args.metadata, args.calendar, args.output)
    print(encode({"output": str(args.output), "bundle_sha256": result["bundle_sha256"]}).decode(), end="")
    return 0
