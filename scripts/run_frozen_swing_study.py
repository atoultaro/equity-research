"""PR7B fixed-window actual AAPL/GOOG inventory; frozen inputs only, no fetch.

Row-level licensed data and signals remain in the explicitly supplied local output.
The summary contains aggregates and hashes suitable for the PR evidence record.
"""

import argparse
from pathlib import Path

from equity_research.events import load_event_study
from equity_research.ingestion.storage import encode, write_bundle
from equity_research.market_context import load_market_context
from equity_research.swing import Configuration, CONTINUATION, FAILED, freeze_strategy, load_strategy

START, END = "2024-01-02", "2026-10-20"


def run_study(aapl_study, goog_study, context_path, output):
    context = load_market_context(context_path)
    studies = {"AAPL": aapl_study, "GOOG": goog_study}
    inspected = {}
    for symbol, path in studies.items():
        study = load_event_study(path)
        m = study.manifest
        if (m["symbol"] != symbol or study.prices.manifest["synthetic_only"] or
                study.prices.manifest["start"] != START or study.prices.manifest["end"] != END):
            raise ValueError("fixed actual symbol/window required; no substitution or extension")
        inspected[symbol] = {"study_path": str(path), "study_sha256": study.content_sha256,
                            "price_dataset_sha256": study.prices.content_sha256,
                            "security_id": m["security_id"], "sessions": len(study.bars()),
                            "basis": study.prices.manifest["securities"][symbol]["basis"]}
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    results = {}
    for symbol, path in studies.items():
        for strategy in (CONTINUATION, FAILED):
            target = output / f"{symbol.lower()}-{strategy}"
            config = Configuration(strategy)
            hashes = freeze_strategy(path, context_path, target, configuration=config, start=START, end=END)
            loaded = load_strategy(target)
            results[f"{symbol}:{strategy}"] = {"output_path": str(target), "bundle_sha256": hashes["bundle_sha256"],
                "configuration_sha256": config.sha256, "quality": loaded.results["quality_report"]}
    summary = {"schema_version": "pr7b_real_inventory_v1", "start": START, "end": END,
        "inputs": inspected, "context": {"path": str(context_path), "sha256": context.content_sha256,
        "historical_dissemination_verified": False, "quality": context.quality}, "inventories": results,
        "interpretation": "COUNTS_ONLY_NO_EDGE_OR_EXECUTION_CLAIM; correlated overlapping signals not independent samples"}
    write_bundle(output / "summary", {"summary.json": encode(summary)})
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("aapl-study", "goog-study", "context", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    print(encode(run_study(args.aapl_study, args.goog_study, args.context, args.output)).decode(), end="")
