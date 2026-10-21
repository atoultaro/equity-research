"""Immutable inputs, deterministic artifacts, explicit source and dependency identity."""

import csv
from dataclasses import asdict
from datetime import date, datetime
from decimal import Decimal
import importlib.metadata
import io
import json
from pathlib import Path
import platform
import re
import subprocess
import tempfile

import market_shared.indicators

from . import _shared_pin
from .data import load_dataset, sha256
from .execution import simulate
from .models import Candidate, Config


def canonical(value) -> bytes:
    def encode(item):
        if isinstance(item, Decimal):
            return format(item, "f")
        if isinstance(item, (datetime, date)):
            return item.isoformat()
        raise TypeError(f"cannot encode {type(item).__name__}")
    return (json.dumps(value, default=encode, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False, allow_nan=False) + "\n").encode()


def code_identity(source_commit: str | None) -> dict:
    source = Path(__file__).parent
    code_hashes = {p.name: sha256(p.read_bytes()) for p in sorted(source.glob("*.py"))}
    identity = {"source_tree_sha256": sha256(canonical(code_hashes))}
    if source_commit is not None:
        if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
            raise ValueError("source commit must be a full lowercase Git SHA")
        return dict(identity, source_commit=source_commit, revision_origin="user_supplied")
    try:
        root = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True,
                                            stderr=subprocess.DEVNULL).strip())
        # A wheel executed from an unrelated Git checkout must not inherit that SHA.
        if not (root / "pyproject.toml").exists() or 'name = "equity-research"' not in (root / "pyproject.toml").read_text():
            raise ValueError("not the equity-research checkout")
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip())
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError) as exc:
        raise ValueError("run from the equity-research checkout or supply --source-commit") from exc
    return dict(identity, source_commit=commit, revision_origin="checkout", source_dirty=dirty)


def shared_identity() -> dict:
    version = importlib.metadata.version("market-shared")
    content = sha256(Path(market_shared.indicators.__file__).read_bytes())
    if version != _shared_pin.VERSION or content != _shared_pin.INDICATORS_SHA256:
        raise ValueError("installed market_shared differs from the pinned wheel; install requirements-shared.txt")
    return {"version": version, "source_commit": _shared_pin.SOURCE_COMMIT,
            "wheel_sha256": _shared_pin.WHEEL_SHA256, "indicators_sha256": content}


def run_experiment(data: Path, candidate: Path, config: Path, manifest: Path, output: Path,
                   *, source_commit: str | None = None) -> dict:
    # Capture bytes once. Subsequent parsing/replay cannot read revised live inputs.
    inputs = {"data.csv": data.read_bytes(), "candidate.json": candidate.read_bytes(),
              "config.json": config.read_bytes(), "data_manifest.json": manifest.read_bytes()}
    observation = Candidate.from_dict(json.loads(inputs["candidate.json"]))
    policy = Config.from_dict(json.loads(inputs["config.json"]))
    with tempfile.TemporaryDirectory(prefix="equity-input-") as tmp:
        snapshot = Path(tmp)
        for name, content in inputs.items():
            (snapshot / name).write_bytes(content)
        dataset = load_dataset(snapshot / "data.csv", snapshot / "data_manifest.json")
    result = simulate(dataset, observation, policy)
    metadata = {
        "schema_version": "research_run_v1", "code": code_identity(source_commit),
        "runtime": {"python": platform.python_version(), "decimal_precision": 28},
        "shared_dependency": shared_identity(), "policy": asdict(policy),
        "candidate": asdict(observation), "data_manifest": dataset.manifest,
        "input_sha256": {k: sha256(v) for k, v in inputs.items()},
        "indicator_conventions": "SMA full window; gap-aware TR; shared simple ATR after full history",
        "timing_convention": "explicit XNYS/ET schedule; signal-session features available by candidate availability; next eligible open",
        "fill_convention": "gap-aware opens; conservative stop-first intraday; same-day ambiguity flagged; terminal full exit",
        "cost_convention": "absolute per-share adverse slippage both sides; per-share commission and per-order fees",
        "gross_convention": "before fees and modeled slippage; price PnL also reported after slippage",
        "risk_convention": "actual entry minus initial stop times shares, before fees; fixed denominator for net realized R",
        "result_sha256": sha256(canonical(result)),
    }
    artifacts = {"result.json": canonical(result), "run_manifest.json": canonical(metadata)}
    artifacts.update({"inputs/" + k: v for k, v in inputs.items()})
    trade = result["trade"]
    columns = ["quantity", "entry_session", "exit_session", "entry_price", "exit_price", "initial_stop",
               "initial_risk_dollars", "gross_pnl_dollars", "commission_dollars", "fees_dollars",
               "modeled_slippage_dollars", "net_pnl_dollars", "realized_r", "exit_reason",
               "stop_target_ambiguous", "entry_exit_order_ambiguous"]
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    if trade:
        writer.writerow(trade)
    artifacts["trade_ledger.csv"] = stream.getvalue().encode()
    lines = ["# Local single-candidate research run", "", f"Security: {observation.symbol}",
             f"Signal session: {observation.candidate_session}", f"Data source: {dataset.manifest['source']}",
             f"Candidate evidence: {result['qualification']['membership_evidence']}",
             f"Status: {result['status']}",
             f"Reasons: {', '.join(result['reason_codes'])}", "Trade count: " + str(int(trade is not None))]
    if trade:
        lines += [f"{key}: {trade[key]}" for key in ("quantity", "initial_risk_dollars", "gross_pnl_dollars",
                  "commission_dollars", "fees_dollars", "modeled_slippage_dollars", "net_pnl_dollars", "realized_r")]
    lines += ["", "One-trade engineering evidence; no portfolio statistics or strategy-edge conclusion."]
    artifacts["summary.md"] = ("\n".join(lines) + "\n").encode()
    hashes = {k: sha256(v) for k, v in sorted(artifacts.items())}
    artifacts["artifact_hashes.json"] = canonical({"algorithm": "sha256", "files": hashes,
                                                 "canonical_bundle_sha256": sha256(canonical(hashes))})
    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir(exist_ok=False)  # exclusive directory claim; never silently overwrite
    for name, content in artifacts.items():
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    return result
