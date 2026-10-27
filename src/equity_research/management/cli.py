"""Explicitly offline research; PR16's CLI and identity remain untouched."""

import json
from pathlib import Path


def register(commands):
    parser = commands.add_parser("management", help="offline PR17 empirical decision analysis")
    sub = parser.add_subparsers(dest="management_operation", required=True)
    study = sub.add_parser("study")
    study.add_argument("--parent", type=Path, required=True)
    study.add_argument("--config", type=Path, required=True)
    study.add_argument("--output", type=Path, required=True)
    replay = sub.add_parser("replay")
    replay.add_argument("--study", type=Path, required=True)
    replay.add_argument("--output", type=Path, required=True)


def dispatch(args):
    from ..ingestion.storage import encode, write_bundle
    from .study import freeze_study, load_study
    if args.management_operation == "study":
        hashes = freeze_study(args.parent, json.loads(args.config.read_bytes()), args.output)
    else:
        checked = load_study(args.study)
        hashes = write_bundle(args.output, checked["files"])
    print(encode({"output": str(args.output), "sha256": hashes["bundle_sha256"]}).decode(), end="")
    return 0
