"""Offline PR9B freeze/replay; all outputs exclusively created, no network."""
import argparse
from pathlib import Path
import socket

from equity_research.grimes_forensics import freeze, load
from equity_research.ingestion.storage import write_bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    create = sub.add_parser('freeze')
    create.add_argument('--parent', type=Path, required=True)
    create.add_argument('--intraday', type=Path, required=True)
    create.add_argument('--documentary', type=Path, required=True)
    replay = sub.add_parser('replay')
    replay.add_argument('--study', type=Path, required=True)
    for p in (create, replay):
        p.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()

    def denied(*args, **kwargs):
        raise AssertionError('forensics freeze/replay prohibits network connections')
    socket.socket.connect = socket.socket.connect_ex = socket.create_connection = denied
    if args.operation == 'freeze':
        result = freeze(args.parent, args.intraday, args.documentary, args.output)
    else:
        files, _ = load(args.study)
        result = write_bundle(args.output, files)
    print({'bundle_sha256': result['bundle_sha256'], 'members': len(result['files'])})


if __name__ == '__main__':
    main()
