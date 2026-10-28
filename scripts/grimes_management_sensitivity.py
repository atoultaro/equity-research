"""Offline policy sensitivity over immutable PR19 scenarios; never overwrite."""

import argparse
from pathlib import Path
import socket

from equity_research.ingestion.storage import encode, write_bundle
from equity_research.reconstruction_sensitivity import freeze, load


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="operation", required=True)
    create = sub.add_parser("freeze")
    create.add_argument("--study", type=Path, required=True)
    replay = sub.add_parser("replay")
    replay.add_argument("--study", type=Path, required=True)
    for command in (create, replay):
        command.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    def denied(*args, **kwargs):
        raise AssertionError("policy sensitivity prohibits network connections")
    socket.socket.connect = socket.socket.connect_ex = socket.create_connection = denied
    result = freeze(args.study, args.output) if args.operation == "freeze" else write_bundle(args.output, load(args.study)["files"])
    print(encode(result).decode(), end="")


if __name__ == "__main__":
    main()
