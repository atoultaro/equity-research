"""Practical acquisition/cache/freeze/diagnostic commands, all imports deferred."""

import json
from pathlib import Path
from types import SimpleNamespace


def register(operations):
    for name in ("history", "freeze"):
        command = operations.add_parser(name)
        command.add_argument("--provider", choices=("yahoo", "ibkr"), required=True)
        command.add_argument("--symbols", required=True, help="comma-separated research symbols; maximum 20")
        command.add_argument("--mappings", type=Path, required=True, help="JSON array of explicit security identities")
        command.add_argument("--start", required=True)
        command.add_argument("--end", required=True, help="inclusive")
        command.add_argument("--cache", type=Path, default=Path("data/history_cache"))
        if name == "history":
            command.add_argument("--mode", choices=("auto", "incremental", "full", "offline"), default="auto")
            command.add_argument("--overlap-days", type=int, default=7)
            command.add_argument("--permission-reference", help="user-supplied basis for permitted acquisition/retention")
            command.add_argument("--ibkr-port", type=int)
            command.add_argument("--ibkr-client-id", type=int)
        else:
            command.add_argument("--output", type=Path, required=True)
            command.add_argument("--allow-incomplete", action="store_true", help="diagnostic dataset; indicators still fail on gaps")
    compare = operations.add_parser("compare-providers")
    for name in ("symbol", "start", "end"):
        compare.add_argument("--" + name, required=True)
    for name in ("yahoo-dataset", "ibkr-dataset", "output"):
        compare.add_argument("--" + name, type=Path, required=True)
    for name, default in (("price-absolute", "0.01"), ("price-percent", "0.01"),
                          ("volume-absolute", "0"), ("volume-percent", "1")):
        compare.add_argument("--" + name, default=default)


def dispatch(args):
    from ..ingestion.storage import encode, write_bundle
    if args.operation == "compare-providers":
        from .comparison import compare_providers
        from .dataset import load_research_dataset
        report = compare_providers(load_research_dataset(args.yahoo_dataset), load_research_dataset(args.ibkr_dataset),
                                   args.symbol, args.start, args.end, price_absolute=args.price_absolute,
                                   price_percent=args.price_percent, volume_absolute=args.volume_absolute,
                                   volume_percent=args.volume_percent)
        write_bundle(args.output, {"comparison.json": encode(report)})
        print(encode({"interpretation": report["interpretation"], "source_selection": "NONE"}).decode(), end="")
        return 0
    from .cache import HistoryCache, history
    from .contracts import select_securities
    selected = select_securities(json.loads(args.mappings.read_bytes()), args.symbols.split(","), args.provider)
    cache = HistoryCache(args.cache)
    if args.operation == "freeze":
        from .dataset import freeze
        hashes = freeze(cache, args.provider, selected, args.start, args.end, args.output,
                        allow_incomplete=args.allow_incomplete)
        print(encode({"dataset": str(args.output), "sha256": hashes["bundle_sha256"]}).decode(), end="")
        return 0
    if args.mode == "offline":
        provider = SimpleNamespace(name=args.provider)
    else:
        if not args.permission_reference or not args.permission_reference.strip():
            raise ValueError("acquisition requires --permission-reference; this attestation does not establish a license")
        if args.provider == "yahoo":
            from ..providers.yahoo import YahooDailyProvider
            provider = YahooDailyProvider()
        else:
            from ..providers.ibkr import IBKRDailyProvider
            provider = IBKRDailyProvider(port=args.ibkr_port, client_id=args.ibkr_client_id)
    report = history(cache, provider, selected, args.start, args.end, mode=args.mode,
                     overlap_days=args.overlap_days, permission_reference=args.permission_reference)
    print(encode(report).decode(), end="")
    return 0 if report["status"] == "SUCCESS" else 3
