"""Strictly admitted long plans mapped to PR4's existing buy-stop replay."""

from dataclasses import replace
from decimal import Context, localcontext
from pathlib import Path
import json
import tempfile

from .engine import evaluate
from .model import Configuration, CONTINUATION
from ..data import load_dataset
from ..execution import replay_order
from ..ingestion.storage import digest, encode, write_bundle
from ..models import Config, number, timestamp
from ..reporting import canonical, shared_identity
from ..strategy import price_grid


def strict_inventory(data, manifest, configuration):
    # The existing loader remains the sole admission path; never re-label native
    # research bundles as raw or infer a no-actions certification from a sidecar.
    dataset = load_dataset(Path(data), Path(manifest))
    rows = [{"symbol": b.symbol, "security_id": "strict:" + b.symbol, "session_date": b.session.session_date.isoformat(),
             "available_at": b.session.available_at.isoformat(),
             **{k: str(getattr(b, k)) for k in ("open", "high", "low", "close", "volume")}} for b in dataset.bars]
    if not rows:
        raise ValueError("empty strict dataset")
    results = evaluate(rows, {"sessions": dataset.manifest["sessions"]}, dataset.manifest["symbol"],
                       rows[0]["security_id"], dataset.data_sha256, configuration,
                       start=rows[0]["session_date"], end=rows[-1]["session_date"])
    return dataset, results


def replay_plans(data, manifest, *, configuration=None, execution_configuration=None, signal_ids=None):
    with localcontext(Context(prec=28)):
        return _replay_plans(data, manifest, configuration=configuration,
                             execution_configuration=execution_configuration, signal_ids=signal_ids)


def _replay_plans(data, manifest, *, configuration, execution_configuration, signal_ids):
    configuration = configuration or Configuration()
    if configuration.strategy_id != CONTINUATION:
        raise ValueError("SHORT_EXECUTION_UNSUPPORTED: failed-breakout plans are research only")
    dataset, research = strict_inventory(data, manifest, configuration)
    cfg = Config.from_dict(vars(execution_configuration)) if execution_configuration is not None else Config.from_dict({})
    cfg = replace(cfg, order_valid_sessions=configuration.signal_expiry_sessions)
    available_ids = {s["signal_id"] for s in research["signals"]}
    if signal_ids is not None and not set(signal_ids) <= available_ids:
        raise ValueError("selected signal identity not present in admitted inputs/configuration")
    selected = set(signal_ids) if signal_ids is not None else available_ids
    records, reserved_until = [], None
    for signal, plan in zip(research["signals"], research["trade_plans"], strict=True):
        sid = signal["signal_id"]
        if sid not in selected: continue
        reason = plan["invalidation_reason"]
        if plan["earliest_entry_session"] is None: reason = reason or "NO_ELIGIBLE_FUTURE_SESSION"
        if reserved_until is not None and (plan["earliest_entry_session"] or "9999") <= reserved_until:
            reason = reason or "SECURITY_RESERVED_BY_PRIOR_SIGNAL"
        if reason:
            records.append({"signal_id": sid, "status": "REJECTED", "reason_codes": [reason], "fills": [], "trade": None})
            continue
        future = [b for b in dataset.bars if b.session.session_date.isoformat() > signal["trigger"]["session_date"]
                  and b.session.opens_at >= timestamp(signal["trigger"]["available_at"])]
        order = {"side": "buy", "order_type": "stop", "trigger": price_grid(number(plan["entry_trigger"]), cfg.price_increment, up=True),
                 "initial_stop": price_grid(number(plan["initial_stop_reference"]), cfg.price_increment, up=False),
                 "created_at": timestamp(signal["trigger"]["available_at"]), "activation_at": future[0].session.opens_at,
                 "expires_at": future[cfg.order_valid_sessions-1].session.closes_at if len(future) >= cfg.order_valid_sessions else None,
                 "valid_sessions": cfg.order_valid_sessions, "status": "CREATED", "eligible_sessions_seen": 0}
        result = replay_order(dataset, order, cfg)
        result["signal_id"] = sid
        records.append(result)
        # Conservative whole-session reservation: no re-entry on an exit's day.
        if result["trade"]:
            reserved_until = result["trade"]["exit_session"].isoformat()
        elif result["status"] in {"EXPIRED", "UNFILLED_END_OF_DATA"}:
            reserved_until = (order["expires_at"] or dataset.bars[-1].session.closes_at).date().isoformat()
    return {"schema_version": "swing_strict_replay_v1", "research": research, "executions": records,
            "selection": sorted(selected), "data_sha256": dataset.data_sha256,
            "execution_configuration": json.loads(canonical(vars(cfg))),
            "cancellation": "UNSUPPORTED_NO_EXTERNAL_CANCEL_EVENTS",
            "capital_policy": "FIXED_INITIAL_CAPITAL_PER_REPLAY; NO_COMPOUNDED_PORTFOLIO_NAV",
            "short_execution": "UNSUPPORTED", "one_position_policy": "reserve_security_through_exit_or_order_expiry_session"}


def freeze_replay(data, manifest, output, *, configuration=None, execution_configuration=None, signal_ids=None):
    if Path(output).exists(): raise FileExistsError(output)
    config = configuration or Configuration()
    inputs = {"input-data.csv": Path(data).read_bytes(), "input-manifest.json": Path(manifest).read_bytes()}
    with tempfile.TemporaryDirectory(prefix="swing-strict-input-") as tmp:
        root = Path(tmp)
        for name, content in inputs.items(): (root / name).write_bytes(content)
        result = replay_plans(root / "input-data.csv", root / "input-manifest.json", configuration=config,
                              execution_configuration=execution_configuration, signal_ids=signal_ids)
    files = {**inputs, "strategy_config.json": encode(config.record()), "replay.json": canonical(result),
             "provenance.json": encode({"schema_version": "swing_strict_provenance_v1", "shared_dependency": shared_identity(),
                 "input_hashes": {k: digest(v) for k, v in inputs.items()},
                 "implementation_sha256": {str(p.relative_to(Path(__file__).parents[1])): digest(p.read_bytes())
                     for p in [*sorted(Path(__file__).parent.glob("*.py")),
                               *[Path(__file__).parents[1] / n for n in ("execution.py", "accounting.py", "data.py", "strategy.py")]]}})}
    return write_bundle(Path(output), files)
