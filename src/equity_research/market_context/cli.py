"""Explicit offline context freezing; no acquisition command or broker flags."""

from pathlib import Path


def register(operations):
    p = operations.add_parser("market-context")
    for role in ("spy", "qqq", "rsp"):
        p.add_argument("--" + role + "-dataset", type=Path, required=True)
    for name in ("start", "end"):
        p.add_argument("--" + name, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--availability", choices=("RECONSTRUCTED_CLOSE_PLUS_DELAY", "UNKNOWN"), default="RECONSTRUCTED_CLOSE_PLUS_DELAY")
    p.add_argument("--delay-minutes", type=int, default=60)
    p.add_argument("--no-state", action="store_true")


def dispatch(args):
    from . import Configuration, freeze_market_context
    from ..ingestion.storage import encode
    config = Configuration(args.availability, args.delay_minutes, not args.no_state)
    hashes = freeze_market_context({r.upper(): getattr(args, r + "_dataset") for r in ("spy", "qqq", "rsp")},
                                  args.start, args.end, args.output, configuration=config)
    print(encode({"output": str(args.output), "sha256": hashes["bundle_sha256"]}).decode(), end="")
    return 0
