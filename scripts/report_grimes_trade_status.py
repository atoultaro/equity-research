"""Deterministic source-only status export. All output paths must be unused."""

import argparse
from pathlib import Path

from equity_research.ingestion.storage import encode
from equity_research.research_outputs.grimes_status import capture_source, generate, render_csv


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="operation", required=True)
    capture = sub.add_parser("capture-source", help="validate frozen local PR16 and capture a public facts projection")
    capture.add_argument("--study", type=Path, required=True)
    capture.add_argument("--output", type=Path, required=True)
    for action in ("generate", "verify"):
        command = sub.add_parser(action)
        command.add_argument("--source", type=Path, required=True)
        command.add_argument("--output" if action == "generate" else "--csv", type=Path, required=True)
    args = parser.parse_args()
    if args.operation == "capture-source":
        result = capture_source(args.study, args.output)
    elif args.operation == "generate":
        result = generate(args.source, args.output)
    else:
        if args.csv.read_bytes() != render_csv(args.source):
            raise ValueError("CSV does not reproduce from the immutable source ledger")
        result = {"status": "REPRODUCIBLE", "csv": str(args.csv)}
    print(encode(result).decode(), end="")


if __name__ == "__main__":
    main()
