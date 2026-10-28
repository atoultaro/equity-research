"""Offline PR8B capture projection and real observed-contract pilot; no provider connection."""

import argparse
import json
from pathlib import Path
import socket

from equity_research.ingestion.storage import encode
from equity_research.research_outputs.observed_universe import capture_inputs, freeze_pilot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="operation", required=True)
    capture = sub.add_parser("capture-inputs")
    capture.add_argument("--config", type=Path, required=True)
    study = sub.add_parser("study")
    study.add_argument("--inputs", type=Path, required=True)
    for command in (capture, study):
        command.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    def denied(*args, **kwargs):
        raise AssertionError("PR8B existing-source pilot prohibits network connections")
    socket.socket.connect = denied
    socket.socket.connect_ex = denied
    socket.create_connection = denied
    if args.operation == "capture-inputs":
        result = capture_inputs(json.loads(args.config.read_bytes()), args.output)
    else:
        result = freeze_pilot(args.inputs, args.output)
    print(encode(result).decode(), end="")


if __name__ == "__main__":
    main()
