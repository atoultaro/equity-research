"""Self-contained lifecycle studies; every load independently derives all outputs."""

from collections import Counter
from copy import deepcopy
from datetime import date, timedelta
from decimal import Decimal
import json
from pathlib import Path

from ..comprehension.features import Panel
from ..comprehension.inputs import capture_proof, replay_proof, _check_hashes
from ..comprehension.methodology import validate_methodology
from ..comprehension.study import classify_event, implementation_identity as context_identity
from ..events.model import timestamp
from ..ingestion.calendar import schedule
from ..ingestion.storage import digest, encode, read_bundle, write_bundle
from .model import simulate
from .source import UNIVERSE, parse_alerts, reconstruct

MARKETS = ("SPY", "QQQ", "RSP", "IWM")


def identity():
    return {"context_dependencies": context_identity(), "lifecycle_files": {
        p.name: digest(p.read_bytes()) for p in sorted(Path(__file__).parent.glob("*.py"))}}


def freeze_alerts(source, output):
    original = Path(source).read_bytes()
    record = json.loads(original)
    for a in record["alerts"]:
        a.setdefault("html", "")  # Plain-text-only evidence is explicitly allowed.
    events, _, _ = parse_alerts(record)
    reconstruct(events)
    files = {"alerts.json": encode(record), "original-input.json": original,
        "capture_manifest.json": encode({"capture_level": "Operator-supplied original alert bodies and metadata",
            "publication_timestamps_inferred": False, "source_origin": record["origin"],
            "html_missing_for": [a["alert_id"] for a in record["alerts"] if not a["html"]]})}
    for a in record["alerts"]:
        files[a["alert_id"]+".txt"] = a["text"].encode()
        files[a["alert_id"]+".html"] = a["html"].encode()
    return write_bundle(Path(output), files)


def freeze_inputs(spec, alerts_bundle, audits, methodology, output):
    source, seal = read_bundle(alerts_bundle)
    files = {"spec.json": encode(spec), "methodology.json": Path(methodology).read_bytes(),
        "source-proofs.json": encode([capture_proof(p, symbols, spec["start"], spec["end"]) for p, symbols in audits]),
        "alert-capture-hashes.json": encode(seal),
        **{f"alert-capture-{k}": v for k, v in source.items()}}
    read_inputs(files)
    return write_bundle(Path(output), files)


def read_inputs(files):
    spec = json.loads(files["spec.json"])
    if spec.get("schema_version") != "grimes_lifecycle_inputs_v1" or spec.get("entry_rule") != "NEXT_ELIGIBLE_REGULAR_OPEN":
        raise ValueError("explicit versioned lifecycle inputs and entry assumption required")
    if type(spec["allow_email_availability_bound"]) is not bool:
        raise ValueError("explicit email-bound modeling decision required")
    if spec["end"] != timestamp(spec["analysis_cutoff"]).date().isoformat() or spec["start"] > spec["end"]:
        raise ValueError("fixed historical end/cutoff required")
    captured = {k[len("alert-capture-"):]: v for k, v in files.items()
        if k.startswith("alert-capture-") and k != "alert-capture-hashes.json"}
    _check_hashes(captured, json.loads(files["alert-capture-hashes.json"]))
    alerts = json.loads(captured["alerts.json"])
    for a in alerts["alerts"]:
        # Raw capture and normalized container must retain precisely the same body.
        if (captured[f"{a['alert_id']}.txt"] != a["text"].encode()
                or captured[f"{a['alert_id']}.html"] != a["html"].encode()):
            raise ValueError("alert raw body/container mismatch")
    events, _, _ = parse_alerts(alerts, allow_email_bound=spec["allow_email_availability_bound"])
    reconstruct(events)
    if any(e["effective_at"] and timestamp(e["effective_at"]) > timestamp(spec["analysis_cutoff"]) for e in events):
        raise ValueError("source action after study cutoff")
    methodology = validate_methodology(json.loads(files["methodology.json"]))
    prices, coverage, kinds = {}, {}, {}
    for proof in json.loads(files["source-proofs.json"]):
        rows, info = replay_proof(proof, spec["start"], spec["end"])
        if set(rows) & set(prices):
            raise ValueError("multiple native identities/revisions for one symbol")
        prices.update(rows)
        coverage.update(info)
        kinds.update({r["security"]["symbol"]: r["kind"] for r in json.loads(proof["files"]["plan.json"])["config"]["instruments"]})
    ids = [v["contract"]["conId"] for v in coverage.values()]
    stocks = {s for s, c in coverage.items() if c["security"]["symbol"] in UNIVERSE}
    if len(ids) != len(set(ids)) or stocks != set(UNIVERSE) or not set(MARKETS) <= set(prices):
        raise ValueError("exact 26 stocks, unique contracts and four market proxies required")
    for s, c in coverage.items():
        kind = kinds[s]
        if s not in UNIVERSE and kind == "stock":
            raise ValueError("additional stocks forbidden; only explicit ETF context proxies allowed")
    calendar = schedule(spec["start"], (date.fromisoformat(spec["end"])+timedelta(days=14)).isoformat())
    valid = {s["session_date"] for s in calendar["sessions"]}
    if any(r["session_date"] not in valid for rows in prices.values() for r in rows):
        raise ValueError("off-calendar source price")
    return spec, alerts, prices, coverage, calendar, methodology


def contexts(events, trades, prices, coverage, calendar, spec):
    market, stock, cache = [], [], {}
    direction = {t["symbol"]: t["direction"] for t in trades}
    proxy_records = {r["symbol"]: r for r in spec["sector_proxies"]}
    if len(proxy_records) != len(spec["sector_proxies"]) or set(proxy_records) != set(UNIVERSE):
        raise ValueError("explicit sector-proxy decision for every source stock required")
    active_stops = {}
    for event in events:
        s = event["symbol"]
        if "stop" in event:
            active_stops[s] = event["stop"]
        common = {"event_id": event["event_id"], "symbol": s, "source_published_at": event["published_at"],
            "context_cutoff": event["effective_at"], "clock_basis": event["effective_clock"],
            "feature_attribution": "AGENT_SELECTED_DESCRIPTIVE_MEASUREMENTS_NOT_GRIMES_RULES"}
        if not event["effective_at"]:
            market.append({**common, "status": "UNRESOLVED_PUBLICATION_TIME", "proxies": {}})
            stock.append({**common, "status": "UNRESOLVED_PUBLICATION_TIME", "features": None})
            continue
        cutoff = event["effective_at"]
        if cutoff not in cache:
            panel = Panel(prices, coverage, calendar, cutoff)
            cache[cutoff] = (panel, {})
        panel, features = cache[cutoff]
        end = panel.days[-1] if panel.days else None

        def get(symbol):
            if symbol not in features:
                features[symbol] = panel.features(symbol, end)
            return deepcopy(features[symbol])

        market.append({**common, "status": "COMPUTED", "last_available_session": end,
            "availability_rule": "COMPLETED_XNYS_RTH_CLOSE_PLUS_60_MINUTES",
            "proxies": {p: {"con_id": coverage[p]["contract"]["conId"], "features": get(p)} for p in MARKETS}})
        f = get(s)
        selection = proxy_records[s]
        p = selection.get("proxy")
        if p:
            if (selection["con_id"] != coverage[s]["contract"]["conId"] or p not in coverage
                    or selection["proxy_con_id"] != coverage[p]["contract"]["conId"]
                    or not selection.get("source_reference") or not selection.get("evidence")):
                raise ValueError("sector context requires qualified identities and explicit evidence")
            # Business mappings are retrospective analyst choices unless dated publication is proven.
        atr, close = f["atr14"]["value"], f["close"]["value"]
        stop = active_stops[s]
        distance = abs(Decimal(str(close))-Decimal(stop)) if close is not None else None
        evidence = [classify_event(e, cutoff) for e in spec.get("dated_events", []) if e["symbol"] == s]
        stock.append({**common, "status": "COMPUTED_WITH_EXPLICIT_UNAVAILABLE_FIELDS", "last_available_session": end,
            "con_id": coverage[s]["contract"]["conId"], "features": f, "reported_stop": stop,
            "stop_distance_ATR": str(distance/Decimal(str(atr))) if distance is not None and atr else None,
            "stop_distance_units_status": "CONDITIONAL_REPORTED_STOP_BASIS_UNVERIFIED",
            "relative_to_market": {p: {str(n): panel.relative(s, p, end, n) for n in (1, 5, 20, 60)} for p in MARKETS},
            "sector_proxy_decision": selection,
            "sector_features": get(p) if p else None,
            "relative_to_sector": {str(n): panel.relative(s, p, end, n) for n in (1, 5, 20, 60)} if p else None,
            "dated_event_evidence": evidence, "earnings_completeness": "UNKNOWN_NO_COMPLETE_PUBLICATION_EVIDENCE",
            "corporate_action_completeness": coverage[s]["corporate_action_completeness"],
            "direction": direction[s]})
    return market, stock


def derive(spec, alerts, prices, coverage, calendar, methodology):
    events, excluded, commentary = parse_alerts(alerts, allow_email_bound=spec["allow_email_availability_bound"])
    trades, stops, underway = reconstruct(events)
    models, modeled_events, exits = simulate(trades, prices, coverage, calendar, methodology,
        cutoff=spec["analysis_cutoff"], basis_evidence=spec["basis_evidence"])
    conditional, conditional_events, conditional_exits = simulate(trades, prices, coverage, calendar, methodology,
        cutoff=spec["analysis_cutoff"], basis_evidence=spec["basis_evidence"], conditional=True)
    market, stock = contexts(events, trades, prices, coverage, calendar, spec)
    # Original ATR is pre-entry, never recomputed after a stop revision.
    initial_atr = {}
    for rows in (exits, conditional_exits):
        for row in rows:
            model = next(m for m in models if m["trade_id"] == row["trade_id"])
            if model["trade_id"] not in initial_atr:
                if model["first_eligible_at"]:
                    panel = Panel(prices, coverage, calendar, model["first_eligible_at"])
                    f = panel.features(row["symbol"], panel.days[-1]) if panel.days else None
                    atr = f["atr14"]["value"] if f else None
                else:
                    atr = None
                initial_atr[model["trade_id"]] = atr
            atr = initial_atr[model["trade_id"]]
            row["initial_ATR"] = atr
            for field in ("progress", "mfe"):
                value = row[field+"_price_units"]
                row[field+"_initial_ATR"] = str(Decimal(value)/Decimal(str(atr))) if value is not None and atr else None
    reconciled = []
    for trade, model, scenario in zip(trades, models, conditional, strict=True):
        reconciled.append({"trade_id": trade["trade_id"], "symbol": trade["symbol"], "direction": trade["direction"],
            "source_state": trade["position_state"], "source_setup": trade["setup_availability"],
            "modeled_state": model["state"], "modeled_closure_reason": model["closure_reason"],
            "conditional_basis_state": scenario["state"], "conditional_basis_closure_reason": scenario["closure_reason"],
            "conflicts": [e for e in model["events"] if e["type"] == "SOURCE_MODEL_CONFLICT"],
            "conditional_conflicts": [e for e in scenario["events"] if e["type"] == "SOURCE_MODEL_CONFLICT"],
            "source_closure_cause": "UNKNOWN" if trade["position_state"] == "CLOSED" else None,
            "source_lifecycle_completeness": trade["lifecycle_completeness"],
            "actual_entry_fill_quantity_and_realized_return": None})

    def counts(rows, field):
        return dict(sorted(Counter(r[field] for r in rows).items()))

    comparison = {"source_direction": counts(trades, "direction"), "source_position_state": counts(trades, "position_state"),
        "source_setup_availability": counts(trades, "setup_availability"), "stop_changes": counts(stops, "change"),
        "stop_changes_by_setup": {k: counts([r for r in stops if r["setup_availability"] == k], "change") for k in ("ENTERABLE", "UNDERWAY")},
        "modeled_states": counts(models, "state"), "conditional_basis_modeled_states": counts(conditional, "state"),
        "modeled_events": counts(modeled_events, "type"), "conditional_basis_events": counts(conditional_events, "type"),
        "conditional_stop_evidence_status": dict(Counter(e["status"] for e in conditional_events if e["type"] == "ASSUMED_STOP_TRIGGERED")),
        "conditional_target_evidence_status": dict(Counter(e["status"] for e in conditional_events if e["type"] == "HYPOTHETICAL_TARGET_REACHED")),
        "by_direction": {d: {"source_states": counts([t for t in trades if t["direction"] == d], "position_state"),
            "modeled_states": counts([t for t in models if t["direction"] == d], "state"),
            "conditional_basis_states": counts([t for t in conditional if t["direction"] == d], "state"),
            "conditional_basis_closure_reasons": dict(Counter(t["closure_reason"] or t["state"] for t in conditional if t["direction"] == d))}
            for d in ("LONG", "SHORT")},
        "by_source_setup": {k: {"source_states": counts([t for t in trades if t["setup_availability"] == k], "position_state"),
            "conditional_basis_closure_reasons": dict(Counter(c["closure_reason"] or c["state"] for t, c in zip(trades, conditional, strict=True)
                if t["setup_availability"] == k))} for k in ("ENTERABLE", "UNDERWAY")},
        "source_model_state_matrix": dict(Counter(t["position_state"]+" / "+m["state"] for t, m in zip(trades, models, strict=True))),
        "time_windows": {str(n): {"status_counts": counts([e for e in conditional_exits if e["horizon_sessions"] == n], "status"),
            "conditional_candidate_count": sum(e["possible_time_stop"] is True for e in conditional_exits if e["horizon_sessions"] == n)} for n in (2, 3, 5)},
        "duration": [], "cohort_limitation": "Selected source alerts; right censoring, unknown fills and unverified units prevent strategy profitability inference"}
    for t in trades:
        op = t["events"][0]["effective_at"]
        cl = t["events"][-1]["effective_at"] if t["position_state"] == "CLOSED" else spec["analysis_cutoff"]
        days = [s["session_date"] for s in calendar["sessions"] if op and cl
            and timestamp(op) <= timestamp(s["opens_at"]) and timestamp(s["closes_at"]) <= timestamp(cl)]
        comparison["duration"].append({"trade_id": t["trade_id"], "symbol": t["symbol"], "eligible_full_sessions_observed": len(days) if op and cl else None,
            "sessions": days, "right_censored": t["position_state"] == "OPEN", "clock_basis": t["events"][0]["effective_clock"]})
    return {"alerts.json": alerts, "source_events.json": events, "source_trade_lifecycles.json": trades,
        "source_stop_history.json": stops, "underway_transitions.json": underway, "excluded_source_actions.json": excluded,
        "expert_market_commentary.json": commentary, "modeled_events.json": modeled_events,
        "modeled_trade_lifecycles.json": models, "source_model_reconciliation.json": reconciled,
        "conditional_basis_modeled_events.json": conditional_events, "conditional_basis_trade_lifecycles.json": conditional,
        "market_context_at_events.json": market, "stock_context_at_events.json": stock,
        "exit_hypotheses.json": {"basis_validated_model": exits, "conditional_unverified_basis_scenario": conditional_exits},
        "comparison.json": comparison, "data_coverage.json": coverage,
        "provenance.json": {"source_price_bundles": sorted({c["source_bundle_sha256"] for c in coverage.values()}),
            "operator_methodology": methodology, "spec": spec, "calendar": calendar,
            "source_originals": "Local exact MIME bodies; subscriber text excluded from public Git reports",
            "execution_accounting": "NOT_PERFORMED_NO_ACTUAL_FILLS_OR_POSITION_SIZES"},
        "manifest.json": {"schema_version": "grimes_lifecycle_study_v1", "stock_count": len(trades), "alert_count": len(alerts["alerts"]),
            "source_event_count": len(events), "analysis_cutoff": spec["analysis_cutoff"], "weekly_publication_date": None,
            "market_availability": "Cash close +60 minutes modeling bound, historical exact bar publication UNKNOWN",
            "source_status_counts": counts(trades, "position_state"), "es_prices_used": False,
            "basis_validation_scope": "Quote-anchored sessions only; independent complete corporate-action audit unavailable"}}


def markdown(result, only=None):
    trades = result["source_trade_lifecycles.json"]
    models = {m["symbol"]: m for m in result["modeled_trade_lifecycles.json"]}
    scenarios = {m["symbol"]: m for m in result["conditional_basis_trade_lifecycles.json"]}
    if only:
        trades = [t for t in trades if t["symbol"] == only]
    lines = [f"# Grimes lifecycle reconstruction{': '+only if only else ''}", "",
        "Seven alerts, October 18–26, 2026; exactly 26 stocks. ADDED opens a source position; UNDERWAY changes entry availability; only DROPPED closes it.", "",
        "Source facts and analytical assumptions are separate. Actual entry, fills, quantities and closure causes remain unknown. No execution P&L or portfolio curve is calculated.", "",
        "The weekly display remains ‘Yesterday at 8:57 AM’, with absolute publication UNKNOWN. Where explicitly enabled, the original email timestamp supplies a separate availability bound, not an inferred publication date.", "",
        "Model entry: next eligible RTH Open. Original R uses that hypothetical entry and initial stop, never revised stops. SHORT +1R fully closes; LONG +1R removes at least one-third with exact fraction/runner management unknown. Stop and target on the same daily bar preserve unknown order. Stop observations are triggers, not fills; gap slippage is unknown.", "",
        "Primary modeled outcomes require session-bounded price-unit evidence. Additional conditional outcomes assume stop/native-bar compatibility and are not validated executions. ETF/stock features use only completed sessions available by cash close +60 minutes; missing history stays unavailable. Historical exact publication and complete corporate-action evidence are unknown.", "",
        "| Symbol | Direction | Source | Setup | Primary model | Conditional on unverified units |",
        "|---|---|---|---|---|---|"]
    for t in trades:
        m, c = models[t["symbol"]], scenarios[t["symbol"]]
        lines.append(f"| {t['symbol']} | {t['direction']} | {t['position_state']} | {t['setup_availability']} | {m['state']} | {c['state']} / {c['closure_reason'] or '—'} |")
    for t in trades:
        m = models[t["symbol"]]
        lines += ["", f"## {t['symbol']} ({t['trade_id']})", "",
            f"Initial stop {t['initial_stop']}; latest source stop {t['current_stop']}. Source {t['position_state']}, setup {t['setup_availability']}; {t['lifecycle_completeness']}.", "",
            f"Scenario first eligible time: {m['first_eligible_at'] or 'UNKNOWN'}; modeled Open {m['modeled_entry'] or 'UNAVAILABLE'}; original per-share R {m['original_per_share_risk'] or 'UNAVAILABLE'}; hypothetical target {m['target_1R'] or 'UNAVAILABLE'}. Actual values remain unknown.", "",
            "| Source order | Action | Publication | Effective bound | Stop | Availability |",
            "|---|---|---|---|---|---|"]
        for e in t["events"]:
            lines.append(f"| {e['source_order']} | {e['type']} | {e['published_at'] or 'UNKNOWN'} | {e['effective_at'] or 'UNRESOLVED'} | {e.get('stop', '—')} | {e['setup_after']} |")
        lines += ["", "Primary modeled events:", ""]
        for e in m["events"]:
            lines.append(f"- {e['type']}: {e.get('session_date') or e.get('event_id') or 'final reconciliation'}; {e.get('cause') or e.get('reason') or e.get('status', '')}.")
        if not m["events"]:
            lines.append(f"- {m['state']}; no validated execution claim.")
        lines += ["", "Conditional scenario (assumes unverified stop/native-bar unit compatibility):", ""]
        for e in scenarios[t["symbol"]]["events"]:
            lines.append(f"- {e['type']}: {e.get('session_date') or e.get('event_id') or 'final reconciliation'}; {e.get('cause') or e.get('reason') or e.get('status', '')}.")
        if not scenarios[t["symbol"]]["events"]:
            lines.append(f"- {scenarios[t['symbol']]['state']}.")
        lines += ["", "| Stop event | Previous | Reported | Change | Availability at revision |",
            "|---|---|---|---|---|"]
        for h in result["source_stop_history.json"]:
            if h["symbol"] == t["symbol"]:
                lines.append(f"| {h['event_id']} | {h['previous_stop'] or '—'} | {h['reported_stop']} | {h['change']} | {h['setup_availability']} |")
        if t["symbol"] == "EBAY":
            lines += ["", "EBAY priority case: original 119.20 stop versus operator/native October 26 Low 117.87. Original email availability evidence precedes Monday RTH; exact weekly publication is still unknown. Under the explicitly documented session-scale corroboration, the 119.20 trigger closes the modeled episode. The evening source revision to 117.50 remains in the OPEN source episode and cannot rescue or re-enter the closed model. This is a source/model conflict; the actual discretionary execution history is unknown. Without email-bound or quote-basis evidence the result must remain unresolved."]
        context = [c for c in result["stock_context_at_events.json"] if c["symbol"] == t["symbol"]]
        lines += ["", "| Event | As-of session | Daily return | 5d | 20d | 60d | Stop / ATR distance |",
            "|---|---|---|---|---|---|---|"]
        for c in context:
            f = c["features"]
            values = [f[k]["value"] if f else None for k in ("daily_return", "return_5d", "return_20d", "return_60d")]
            lines.append(f"| {c['event_id']} | {c.get('last_available_session', 'UNKNOWN')} | "+" | ".join("UNKNOWN" if v is None else f"{v:.6%}" for v in values)+f" | {c.get('stop_distance_ATR') or 'UNKNOWN'} |")
        lines += ["", "Market context at every source event (price-return fractions rendered as percentages):", "",
            "| Event | Proxy | Session | Daily | 5d | 20d | 60d | ATR14 / Close |",
            "|---|---|---|---|---|---|---|---|"]
        for c in result["market_context_at_events.json"]:
            if c["symbol"] != t["symbol"]:
                continue
            for p, v in c["proxies"].items():
                values = [v["features"][k]["value"] for k in ("daily_return", "return_5d", "return_20d", "return_60d", "atr14_fraction")]
                lines.append(f"| {c['event_id']} | {p} | {c['last_available_session']} | "+" | ".join("UNKNOWN" if v is None else f"{v:.6%}" for v in values)+" |")
        lines += ["", "Exploratory scenario windows; never a definitive time exit:", "",
            "| Sessions | Status | Price progress | MFE | Progress / initial ATR | MFE / initial ATR | Possible time-stop flag |",
            "|---|---|---|---|---|---|---|"]
        for w in result["exit_hypotheses.json"]["conditional_unverified_basis_scenario"]:
            if w["symbol"] == t["symbol"]:
                lines.append(f"| {w['horizon_sessions']} | {w['status']} | {w['progress_price_units'] or 'UNKNOWN'} | {w['mfe_price_units'] or 'UNKNOWN'} | {w['progress_initial_ATR'] or 'UNKNOWN'} | {w['mfe_initial_ATR'] or 'UNKNOWN'} | {w['possible_time_stop']} |")
        if context and context[-1]["features"]:
            latest = context[-1]
            lines += ["", f"Sector context choice: {latest['sector_proxy_decision'].get('proxy') or 'UNRESOLVED'}. Fixed agent selection; no historical GICS or ETF membership assertion.", "",
                "Latest event stock structure and relative strength:", "", "| Measurement | Value | Status |", "|---|---|---|"]
            for k in ("close_sma20", "close_sma50", "close_sma150", "close_sma200", "sma50_slope20", "confirmed_swing_high", "confirmed_swing_low", "realized_volatility20"):
                metric = latest["features"][k]
                lines.append(f"| {k} | {metric['value'] if metric['value'] is not None else 'UNKNOWN'} | {metric['status']} |")
            for p, values in latest["relative_to_market"].items():
                lines.append(f"| Relative / {p}, 20 sessions | {values['20']['value']} | {values['20']['status']} |")
            if latest["relative_to_sector"]:
                v = latest["relative_to_sector"]["20"]
                lines.append(f"| Relative / sector, 20 sessions | {v['value']} | {v['status']} |")
        lines += ["", "Full MA, swing, volatility, sector and relative-strength measurements are retained in the event-context JSON. These are agent-selected diagnostics, not attributed Grimes entry/exit rules. Earnings completeness remains unknown. Exploratory 2/3/5-session progress/MFE flags never create a definitive time exit."]
    lines += ["", "## Comparison and limits", "", "```json", json.dumps(result["comparison.json"] if not only else {
        "source": next(t["position_state"] for t in trades), "model": models[only]["state"],
        "conditional_basis_model": scenarios[only]["state"]}, sort_keys=True, indent=2), "```", "",
        "Source closures do not establish which stop, target or time rule was executed. Right-censored positions and unresolved basis/timing are not successful trades. This selected, short observation period cannot establish a trading edge.", ""]
    return "\n".join(lines)


def _files(inputs, seals):
    result = derive(*read_inputs(inputs))
    result["manifest.json"].update(input_bundle_sha256=seals["bundle_sha256"], implementation=identity())
    files = {k: encode(v) for k, v in result.items()}
    files["report.md"] = markdown(result).encode()
    for s in UNIVERSE:
        files[f"dossier-{s}.md"] = markdown(result, only=s).encode()
    files.update({f"input-{k}": v for k, v in inputs.items()})
    files["input-hashes.json"] = encode(seals)
    return files


def freeze_study(inputs, output):
    files, seal = read_bundle(inputs)
    return write_bundle(Path(output), _files(files, seal))


def load_study(path):
    files, seal = read_bundle(path)
    inputs = {k[len("input-"):]: v for k, v in files.items() if k.startswith("input-") and k != "input-hashes.json"}
    seals = json.loads(files["input-hashes.json"])
    _check_hashes(inputs, seals)
    if json.loads(files["manifest.json"])["implementation"] != identity():
        raise ValueError("lifecycle implementation/shared dependency differs from frozen study")
    if files != _files(inputs, seals):
        raise ValueError("lifecycle semantic output mismatch")
    return {"files": files, "hashes": seal}
