"""Explicit offline research and strict replay commands; never fetches data."""

import json
from pathlib import Path

from .model import Configuration


def register(commands):
    root = commands.add_parser("swing", help="offline setup/trigger research and strict long replay")
    ops = root.add_subparsers(dest="swing_operation", required=True)
    research = ops.add_parser("research")
    research.add_argument("--study", type=Path, required=True)
    research.add_argument("--context", type=Path)
    research.add_argument("--start", default="2024-01-02")
    research.add_argument("--end", default="2026-10-20")
    replay = ops.add_parser("replay")
    replay.add_argument("--data", type=Path, required=True)
    replay.add_argument("--manifest", type=Path, required=True)
    replay.add_argument("--execution-config", type=Path)
    replay.add_argument("--signal-id", action="append")
    for command in (research, replay):
        command.add_argument("--strategy-config", type=Path, help="exact swing_strategy_config_v1 record; default continuation v1")
        command.add_argument("--output", type=Path, required=True)


def dispatch(args):
    from ..ingestion.storage import encode
    config = Configuration.from_record(json.loads(args.strategy_config.read_bytes())) if args.strategy_config else Configuration()
    if args.swing_operation == "research":
        from .dataset import freeze_strategy
        result = freeze_strategy(args.study, args.context, args.output, configuration=config, start=args.start, end=args.end)
    else:
        from .execution import freeze_replay
        from ..models import Config
        execution = Config.from_dict(json.loads(args.execution_config.read_bytes())) if args.execution_config else None
        result = freeze_replay(args.data, args.manifest, args.output, configuration=config,
                               execution_configuration=execution, signal_ids=args.signal_id)
    print(encode({"output": str(args.output), "bundle_sha256": result["bundle_sha256"]}).decode(), end="")
    return 0
