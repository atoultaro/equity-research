"""Explicit offline-only event evidence and composition commands."""

import json
from pathlib import Path


def register(operations):
    event = operations.add_parser("events-freeze", help="freeze manually reviewed local event/source JSON")
    event.add_argument("--events", type=Path, required=True, help="corporate_events_v1 JSON")
    event.add_argument("--sources", type=Path, required=True, help="event_sources_v1 JSON")
    event.add_argument("--output", type=Path, required=True)
    study = operations.add_parser("event-study", help="compose immutable prices and events, entirely offline")
    study.add_argument("--prices", type=Path, required=True)
    study.add_argument("--events", type=Path, required=True)
    study.add_argument("--symbol", required=True)
    study.add_argument("--output", type=Path, required=True)


def dispatch(args):
    from .model import EVENT_SCHEMA, freeze_events
    from .dataset import freeze_study
    from ..ingestion.storage import encode
    if args.operation == "events-freeze":
        events, sources = json.loads(args.events.read_bytes()), json.loads(args.sources.read_bytes())
        if events["schema_version"] != EVENT_SCHEMA or sources["schema_version"] != "event_sources_v1":
            raise ValueError("unsupported event/source input schema")
        hashes = freeze_events(events["events"], sources["sources"], args.output)
    else:
        hashes = freeze_study(args.prices, args.events, args.symbol, args.output)
    print(encode({"output": str(args.output), "sha256": hashes["bundle_sha256"]}).decode(), end="")
    return 0
