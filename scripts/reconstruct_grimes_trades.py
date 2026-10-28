"""Explicitly offline PR9A inference; output directories must be unused."""

import argparse
import json
from pathlib import Path
import socket

from equity_research.ingestion.storage import encode, write_bundle
from equity_research.reconstruction.study import freeze_inputs, freeze_study, load_study


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="operation", required=True)
    capture = sub.add_parser("freeze-inputs")
    capture.add_argument("--parent", type=Path, required=True)
    capture.add_argument("--config", type=Path, required=True)
    study = sub.add_parser("study")
    study.add_argument("--inputs", type=Path, required=True)
    replay = sub.add_parser("replay")
    replay.add_argument("--study", type=Path, required=True)
    for command in (capture, study, replay):
        command.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    def denied(*args, **kwargs):
        raise AssertionError("PR9A inference prohibits network connections")
    socket.socket.connect = denied
    socket.socket.connect_ex = denied
    socket.create_connection = denied
    if args.operation == "freeze-inputs":
        result = freeze_inputs(args.parent, json.loads(args.config.read_bytes()), args.output)
    elif args.operation == "study":
        result = freeze_study(args.inputs, args.output)
    else:
        result = write_bundle(args.output, load_study(args.study)["files"])
    print(encode(result).decode(), end="")


if __name__ == "__main__":
    main()
