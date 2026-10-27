"""Offline replay and separately invoked optional data-preparation commands."""

import argparse
from pathlib import Path
import sys

from .reporting import canonical, run_experiment


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="equity-research")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run")
    for option in ("data", "candidate", "config", "manifest", "output"):
        run.add_argument("--" + option, type=Path, required=True)
    run.add_argument("--source-commit", help="full source SHA for installed-wheel use outside a checkout")
    from .ingestion.cli import register
    register(commands)
    from .swing.cli import register as register_swing
    register_swing(commands)
    from .outcomes.cli import register as register_outcomes
    register_outcomes(commands)
    from .comprehension.cli import register as register_expert
    register_expert(commands)
    args = parser.parse_args(argv)
    try:
        if args.command == "expert":
            from .comprehension.cli import dispatch as dispatch_expert
            return dispatch_expert(args)
        if args.command == "outcomes":
            from .outcomes.cli import dispatch as dispatch_outcomes
            return dispatch_outcomes(args)
        if args.command == "swing":
            from .swing.cli import dispatch as dispatch_swing
            return dispatch_swing(args)
        if args.command == "data":
            from .ingestion.cli import dispatch
            return dispatch(args)
        result = run_experiment(args.data, args.candidate, args.config, args.manifest, args.output,
                                source_commit=args.source_commit)
    except (ValueError, KeyError, TypeError, OSError, ImportError) as exc:
        print(f"equity-research: {exc}", file=sys.stderr)
        return 2
    print(canonical({"status": result["status"], "trade": result["trade"]}).decode(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
