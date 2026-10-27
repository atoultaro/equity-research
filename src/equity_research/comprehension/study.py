"""Immutable descriptive dossiers, independently recomputed on every bundle load."""

from copy import deepcopy
from datetime import date, timedelta
import json
from pathlib import Path
import platform

from ..events.model import timestamp, day
from ..ingestion.storage import digest, encode, read_bundle, write_bundle
from ..reporting import shared_identity
from .features import Panel, VERSION, alignment, metric, setup, stop_analysis
from .inputs import read_inputs

MARKETS = ("SPY", "QQQ", "RSP", "IWM")
OFFSETS = (0, 5, 20, 60, 120)
VECTOR = ("close_sma20", "close_sma50", "close_sma150", "close_sma200", "sma50_slope20",
          "return20", "return60", "atr14_fraction", "realized_volatility20", "drawdown_high252",
          "range_contraction20_60", "volume_vs_prior20", "mean_dollar_volume20_native")


def implementation_identity():
    base = Path(__file__).parent
    paths = sorted(base.glob("*.py")) + [base.parent / "market_context/model.py", base.parent / "history/depth_store.py",
        base.parent / "events/model.py", base.parent / "ingestion/canonical.py", base.parent / "ingestion/frames.py",
        base.parent / "ingestion/calendar.py", base.parent / "ingestion/storage.py"]
    return {"files": {str(p.relative_to(base.parent)): digest(p.read_bytes()) for p in paths},
            "shared_dependency": shared_identity(), "python": platform.python_version()}


def classify_event(event, cutoff):
    """Reuse event-research's aware clock and conservative minute upper bound."""
    value = deepcopy(event)
    known = event.get("published_at")
    precision = event.get("publication_precision", "UNKNOWN")
    if event.get("publication_evidence_status") != "VERIFIED" or not known or precision not in {"SECOND", "MINUTE"} or not event.get("publication_evidence"):
        category = "UNKNOWN_OR_MISSING"
    else:
        published = timestamp(known)
        if precision == "MINUTE":
            published = published.replace(second=0, microsecond=0) + timedelta(minutes=1)
        if event.get("captured_at") and timestamp(known) > timestamp(event["captured_at"]):
            raise ValueError("event publication after evidence capture")
        category = "VERIFIED_PRE_DECISION" if published < timestamp(cutoff) else "RETROSPECTIVE_ONLY"
    value["availability_category"] = category
    return value


def classification(spec, symbol, coverage):
    records = [r for r in spec["classifications"] if r["symbol"] == symbol]
    if len(records) != 1:
        return {"status": "UNKNOWN_OR_AMBIGUOUS", "records": records}
    row = records[0]
    native = coverage.get(symbol)
    if (not native or row.get("con_id") != native["contract"]["conId"] or not row.get("issuer_identity")
            or not row.get("source_url") or not row.get("evidence") or not row.get("source_document_date")
            or day(row["source_document_date"]) > spec["observations"]["recommendation_date"]
            or (row.get("effective_date") and day(row["effective_date"]) > spec["observations"]["recommendation_date"])):
        return {"status": "UNKNOWN_OR_AMBIGUOUS", "records": records}
    # This is an evidenced analyst mapping, not reconstructed licensed GICS or
    # a claim that the stock belonged to the proxy ETF on any historical date.
    return {**deepcopy(row), "status": "DATED_BUSINESS_EVIDENCE_ANALYST_PROXY"}


def interpretation(stock, contexts, stop, direction):
    """Explicit sign tests supporting competing hypotheses, not expert motives."""
    support, opposition, missing = [], [], []
    sign = 1 if direction == "LONG" else -1
    for name in ("close_sma50", "sma50_slope20", "return20", "return60"):
        value = stock["features"][name]["value"]
        if value is None:
            missing.append(name)
        elif sign*value > 0:
            support.append(f"{name}={value:.6f} supports the reported {direction} direction")
        elif sign*value < 0:
            opposition.append(f"{name}={value:.6f} opposes the reported {direction} direction")
    for proxy in ("SPY", "QQQ"):
        value = stock["relative_strength"][proxy]["20"]["value"]
        if value is None:
            missing.append(f"relative_to_{proxy}20")
        elif sign*value > 0:
            support.append(f"20-session ratio change vs {proxy}={value:.6f} supports directional relative strength")
        elif sign*value < 0:
            opposition.append(f"20-session ratio change vs {proxy}={value:.6f} opposes directional relative strength")
    failed = stock["features"]["failed_breakout20"]["value"]
    if failed:
        (opposition if direction == "LONG" else support).append("Current High exceeded the prior 20-session High, but Close returned below that boundary")
    for kind, context in contexts.items():
        status = context.get("direction_alignment", {}).get("status", "UNAVAILABLE")
        if status == "ALIGNED":
            support.append(f"{kind} proxy {context['proxy']} aligns on all three disclosed trend dimensions")
        elif status == "COUNTERTREND":
            opposition.append(f"{kind} proxy {context['proxy']} opposes all three disclosed trend dimensions")
        else:
            missing.append(f"{kind} alignment {status}; no unqualified contextual confirmation")
    distances = stop.get("technical_level_distances", {})
    available = [(k, v) for k, v in distances.items() if v["absolute_atr_distance"] is not None]
    nearest = min(available, key=lambda p: (float(p[1]["absolute_atr_distance"]), p[0])) if available else None
    return {"supporting_evidence": support, "opposing_evidence": opposition, "unresolved_or_mixed": missing,
        "nearest_tested_stop_level": {"name": nearest[0], **nearest[1]} if nearest else None,
        "scope": "Sign tests and geometric proximity only; no calibrated score, causality or attribution of private rationale"}


def derive(spec, prices, coverage, calendar):
    observations = spec["observations"]
    cutoff, end = observations["analysis_cutoff"], observations["recommendation_date"]
    panel = Panel(prices, coverage, calendar, cutoff)
    if not panel.days or panel.days[-1] != end:
        raise ValueError("recommendation session unavailable under close-plus-60-minute assumption")
    snapshots = {}

    def evolution(symbol):
        if symbol not in snapshots:
            snapshots[symbol] = {str(offset): {"session_date": panel.days[-1-offset],
                "features": panel.features(symbol, panel.days[-1-offset]),
                "relative_to_spy20": panel.relative(symbol, "SPY", panel.days[-1-offset], 20),
                "relative_to_spy60": panel.relative(symbol, "SPY", panel.days[-1-offset], 60)}
                for offset in OFFSETS if offset < len(panel.days)}
        return snapshots[symbol]

    coverage = deepcopy(coverage)
    expected = set(panel.days)
    end_date = date.fromisoformat(end)
    # Calendar-year boundary, with Feb 29 conservatively mapped to Feb 28.
    try:
        target = end_date.replace(year=end_date.year-3).isoformat()
    except ValueError:
        target = end_date.replace(year=end_date.year-3, day=28).isoformat()
    for symbol, info in coverage.items():
        rows = panel.prices.get(symbol, {})
        ordered = sorted(rows)
        first, last = (ordered[0], ordered[-1]) if ordered else (None, None)
        first_listing = info["security"].get("first_session")
        excluded = sorted(d for d in expected if first_listing and d < first_listing)
        missing = sorted(expected - set(rows) - set(excluded))
        info.update(requested_start=spec["analysis_start"], requested_end=end, first_observed=first,
            last_observed=last, observed_sessions=len(rows), missing_expected_sessions=missing,
            listing_excluded_sessions=excluded, three_year_target_met=bool(first and first <= target and not any(d >= target for d in missing)),
            status="COMPLETE_WITHIN_DECLARED_LISTING" if not missing else "INCOMPLETE",
            complete_three_year_history_not_implied_by_status=True)
    market = {"proxies": {s: evolution(s) for s in MARKETS}, "transition_deltas": {},
        "breadth": "NOT_AVAILABLE: RSP/SPY is an equal/cap-weight participation proxy, not constituent breadth",
        "es_context": deepcopy(spec.get("es_context", {"status": "NOT_AVAILABLE", "reason": "NO_VERIFIED_ES_INPUT"}))}
    for s in MARKETS:
        current = evolution(s)["0"]["features"]
        market["transition_deltas"][s] = {}
        for offset in OFFSETS[1:]:
            old = evolution(s).get(str(offset))
            market["transition_deltas"][s][str(offset)] = {k: (
                round(current[k]["value"]-old["features"][k]["value"], 12)
                if old and current[k]["value"] is not None and old["features"][k]["value"] is not None else None)
                for k in ("close_sma200", "sma50_slope20", "return20", "realized_volatility20", "drawdown_high252")}
    sectors, stocks, stops, events, vectors = {}, {}, {}, {}, {}
    for obs in observations["recommendations"]:
        symbol, direction = obs["symbol"], obs["direction"]
        f = panel.features(symbol, end)
        stocks[symbol] = {"session_date": end, "features": f, "inferred_setup": setup(f),
            "stock_trend_alignment": alignment(f, direction), "relative_strength": {},
            "market_alignment": {m: alignment(evolution(m)["0"]["features"], direction) for m in MARKETS}}
        label = stocks[symbol]["inferred_setup"]["classification"]
        inferred_direction = "LONG" if label.startswith("BULLISH") else "SHORT" if label.startswith(("BEARISH", "FAILED_BREAKOUT")) else None
        stocks[symbol]["inferred_setup"]["direction_consistency"] = (
            "UNDETERMINED" if inferred_direction is None else "SUPPORTS_REPORTED_DIRECTION" if inferred_direction == direction else "OPPOSES_REPORTED_DIRECTION")
        mapping = classification(spec, symbol, coverage)
        contexts = {}
        for kind in ("sector", "industry"):
            proxy = mapping.get(f"{kind}_proxy")
            if mapping["status"] != "DATED_BUSINESS_EVIDENCE_ANALYST_PROXY" or proxy not in coverage:
                contexts[kind] = {"status": "NOT_AVAILABLE", "reason": "MISSING_PROXY_OR_AMBIGUOUS_CLASSIFICATION"}
                stocks[symbol]["relative_strength"][kind] = {str(n): metric(reason="MISSING_PROXY_OR_AMBIGUOUS_CLASSIFICATION") for n in (20, 60)}
            else:
                # Bind proxy selection to its separately qualified native identity.
                if mapping.get(f"{kind}_proxy_con_id") != coverage[proxy]["contract"]["conId"]:
                    raise ValueError("proxy contract identity mismatch")
                contexts[kind] = {"status": "AVAILABLE", "proxy": proxy, "contract": coverage[proxy]["contract"],
                    "evolution": evolution(proxy), "direction_alignment": alignment(evolution(proxy)["0"]["features"], direction)}
                stocks[symbol]["relative_strength"][kind] = {str(n): panel.relative(symbol, proxy, end, n) for n in (20, 60)}
        for m in ("SPY", "QQQ"):
            stocks[symbol]["relative_strength"][m] = {str(n): panel.relative(symbol, m, end, n) for n in (20, 60)}
        sectors[symbol] = {"classification": mapping, "contexts": contexts}
        stops[symbol] = stop_analysis(obs, f)
        stocks[symbol]["interpretation"] = interpretation(stocks[symbol], contexts, stops[symbol], direction)
        inventory = [e for e in spec.get("event_evidence", []) if e.get("symbol") in {symbol, "MARKET", "INDUSTRY"}]
        events[symbol] = {"events": [classify_event(e, cutoff) for e in inventory],
            "coverage": "PARTIAL_DOCUMENTED_INVENTORY_NOT_AN_EVENT_COMPLETENESS_ATTESTATION",
            "unknowns": ["Exact recommendation publication and execution times", "Complete earnings/action calendar",
                "Comprehensive company, industry and macro news; no catalyst inferred from OHLCV", "Expert's private rationale"]}
        vectors[symbol] = {"direction": direction, "action": obs["action"], "units": "dimensionless fractions except explicitly named native dollar-volume proxy",
            "features": {k: f[k]["value"] for k in VECTOR}, "setup": stocks[symbol]["inferred_setup"],
            "relative_strength": stocks[symbol]["relative_strength"],
            "stop_atr_distance": stops[symbol].get("atr_normalized_distance"),
            "sector_alignment": contexts["sector"].get("direction_alignment"),
            "market_alignment": stocks[symbol]["market_alignment"]}
    # Fixed, disclosed proxy list; ranks never imply a screened historical universe.
    leadership = {}
    proxies = sorted({c["proxy"] for s in sectors.values() for c in s["contexts"].values() if c["status"] == "AVAILABLE"})
    for offset in OFFSETS:
        values = [(s, evolution(s).get(str(offset), {}).get("relative_to_spy20", {}).get("value")) for s in proxies]
        leadership[str(offset)] = [{"proxy": s, "relative_to_spy20": v} for s, v in sorted(values, key=lambda p: (p[1] is None, -(p[1] or 0), p[0]))]
    comparison = {"standardized_vectors": vectors, "sector_leadership_fixed_proxy_set": leadership,
        "groups": {d: [s for s, v in vectors.items() if v["direction"] == d] for d in ("LONG", "SHORT")},
        "pairwise_feature_differences": [], "interpretation": "Descriptive vectors, not z-scores, trained similarity weights or a screened opportunity set",
        "future_reference_class_dimensions": ["setup type and geometry", "market state and trajectory", "sector trend and strength",
            "stock relative strength", "volatility and liquidity with verified volume units", "dated catalyst/event category"]}
    names = list(vectors)
    for i, a in enumerate(names):
        for b in names[i+1:]:
            comparison["pairwise_feature_differences"].append({"left": a, "right": b,
                "left_minus_right": {k: round(vectors[a]["features"][k]-vectors[b]["features"][k], 12)
                    if vectors[a]["features"][k] is not None and vectors[b]["features"][k] is not None else None for k in VECTOR}})
    manifest = {"schema_version": "expert_comprehension_v1", "feature_version": VERSION,
        "source_origins": {s: c["origin"] for s, c in coverage.items()},
        "analysis_cutoff": cutoff, "price_session": end, "availability_assumption": "RECONSTRUCTED_US_CASH_CLOSE_PLUS_60_MINUTES",
        "exact_historical_bar_publication_times": "UNKNOWN", "retrieved_vintage_may_include_later_revisions": True,
        "reference_close_is_actual_entry": False, "stop_basis_compatibility": "UNVERIFIED_OPERATOR_STOP_VS_NATIVE_IBKR_SPLIT_ADJUSTED_PRICE",
        "feature_conventions": {"returns": "simple price ratios; not total returns", "realized_volatility20": "population SD of 20 simple daily returns, not annualized",
            "slopes": "SMA(t)/SMA(t-lag)-1", "drawdown": "close/trailing maximum daily HIGH-1",
            "atr": "pinned market_shared simple ATR14 over 14 true ranges, requires previous close",
            "volume": "relative within native capture; dollar-volume proxy unverified units, not execution liquidity",
            "swings": "strict 3-neighbor pivots, confirmed with 3 later completed sessions within each snapshot",
            "missingness": "each calculation requires its full ordered calendar window; never forward filled"},
        "taxonomy": {"breakout": "close > previous 20 highs and close > SMA50", "pullback": "close > SMA200, SMA50 > SMA200, within 1 ATR of SMA20 or SMA50",
            "breakdown": "close < previous 20 lows and close < SMA50", "failed_breakout": "current high > previous 20 highs > current close",
            "ambiguity": "zero or multiple matches -> OTHER_OR_UNCERTAIN; hypotheses do not assert expert motive"}}
    result = {"expert_recommendations.json": observations, "data_coverage.json": coverage, "market_context.json": market,
        "sector_context.json": sectors, "stock_features.json": stocks, "stop_analysis.json": stops,
        "event_context.json": events, "comparison.json": comparison, "manifest.json": manifest}
    return result


def _fmt(value, percent=False):
    if value is None:
        return "UNKNOWN / unavailable"
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, (int, float)):
        return f"{value*100:.2f}%" if percent else f"{value:.4f}"
    return str(value)


def markdown(result, only=None):
    observations = result["expert_recommendations.json"]
    lines = ["# Expert trade comprehension — Adam Grimes", "", f"Observation: {observations['recommendation_date']}; assumed cutoff {observations['analysis_cutoff']}.", "",
        "All four actions mean OPEN_NEW_POSITION. Closing prices are research references; execution, entry, size, targets and exact publication time are UNKNOWN.", "",
        "Native IBKR TRADES is documented split-adjusted, not dividend-adjusted. Stop/price contemporaneous basis compatibility is unverified. No fills, risk budgets, outcomes or profitability are computed.", "",
        "## Market evolution", "", "Rows compare only completed sessions available at each historical snapshot. Volatility is unannualized daily population SD; drawdown uses trailing 252-session High.", "",
        "| Proxy | Sessions before cutoff | Session | Close/SMA200 − 1 | 20-session momentum | Daily RV20 | Drawdown |", "| --- | ---: | --- | ---: | ---: | ---: | ---: |"]
    for proxy, snapshots in result["market_context.json"]["proxies"].items():
        for offset, snap in snapshots.items():
            f = snap["features"]
            lines.append(f"| {proxy} | {offset} | {snap['session_date']} | " + " | ".join(_fmt(f[k]["value"], True) for k in ("close_sma200", "return20", "realized_volatility20", "drawdown_high252")) + " |")
    lines += ["", "Transitions are numerical deltas in market_context.json; no year-wide bull/bear label. RSP/SPY measures participation, not constituent breadth.",
        f"ES: {result['market_context.json']['es_context']['status']}. {result['market_context.json']['es_context'].get('reason', '')}", ""]
    origins = sorted(set(result["manifest.json"]["source_origins"].values()))
    lines += [f"Source origins: {', '.join(origins)}. Synthetic fixtures demonstrate arithmetic and reproducibility only.", "",
        "| Current market proxy | Close/SMA20 − 1 | Close/SMA50 − 1 | Close/SMA150 − 1 | Close/SMA200 − 1 | SMA50 slope20 |",
        "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for proxy, snapshots in result["market_context.json"]["proxies"].items():
        f = snapshots["0"]["features"]
        lines.append(f"| {proxy} | " + " | ".join(_fmt(f[k]["value"], True) for k in ("close_sma20", "close_sma50", "close_sma150", "close_sma200", "sma50_slope20")) + " |")
    lines.append("")
    for obs in observations["recommendations"]:
        s = obs["symbol"]
        if only and only != s:
            continue
        stock, stop, sector = (result[k][s] for k in ("stock_features.json", "stop_analysis.json", "sector_context.json"))
        f, coverage = stock["features"], result["data_coverage.json"].get(s)
        lines += [f"## {s} — {obs['direction']} / OPEN_NEW_POSITION", "", f"> {obs['original_recommendation']}", "",
            f"Original source: {observations['source_reference']}. Expert's private motives remain unknown.", ""]
        if coverage:
            lines += [f"IBKR conId {coverage['contract']['conId']}, {coverage['contract']['primaryExchange']}; observed {coverage['first_observed']} through {coverage['last_observed']}, {coverage['observed_sessions']} sessions. "
                f"Missing expected: {len(coverage['missing_expected_sessions'])}; excluded before documented listing: {len(coverage['listing_excluded_sessions'])}; three-year target met: {coverage['three_year_target_met']}.", ""]
        else:
            lines += ["Stock price capture NOT_AVAILABLE; all dependent features remain unavailable.", ""]
        lines += ["### Objective price structure", "", "| Measurement | Value |", "| --- | ---: |"]
        for k in ("close", "sma20", "sma50", "sma150", "sma200", "sma50_slope20", "return20", "return60", "atr14", "atr14_fraction", "realized_volatility20", "high20", "low20", "high60", "low60", "drawdown_high252", "range_contraction20_60", "range_contraction10_previous20", "volume_vs_prior20", "breakout20", "breakdown20", "failed_breakout20"):
            lines.append(f"| {k} | {_fmt(f[k]['value'])} |")
        lines += ["", f"Inferred setup: **{stock['inferred_setup']['classification']}**; {stock['inferred_setup']['reason']}. "
            f"Candidates: {stock['inferred_setup']['candidates']}; {stock['inferred_setup']['direction_consistency']}. "
            "These are fixed geometric heuristics, not a claim about Grimes' intended setup. A pattern opposing the reported direction belongs in the antithesis, not the expert's presumed rationale.", "",
            "### Sector and relative strength", "", f"Classification status: {sector['classification']['status']}.", ""]
        if sector["classification"].get("source_url"):
            c = sector["classification"]
            lines += [f"Analyst mapping: {c['sector']} / {c['industry']}, based on [{c['issuer_identity']}]({c['source_url']}) dated {c['source_document_date']}. Effective classification date: {c.get('effective_date') or 'UNKNOWN'}. "
                f"{c['proxy_limitations']} Historical ETF membership is UNKNOWN.", ""]
        for kind, context in sector["contexts"].items():
            if context["status"] != "AVAILABLE":
                lines += [f"{kind}: NOT_AVAILABLE ({context['reason']}).", ""]
            else:
                relative = stock["relative_strength"][kind]
                lines += [f"{kind}: {context['proxy']}, direction alignment **{context['direction_alignment']['status']}**; stock/proxy ratio change20 {_fmt(relative['20']['value'], True)}, 60 {_fmt(relative['60']['value'], True)}. "
                    "Proxy trends, SPY-relative momentum and their 5/20/60/120-session evolution are preserved in sector_context.json.", ""]
                lines += ["| Sessions before cutoff | Session | Proxy/SMA50 − 1 | Proxy momentum20 | Proxy/SPY change20 |",
                    "| ---: | --- | ---: | ---: | ---: |"]
                for offset, snapshot in context["evolution"].items():
                    lines.append(f"| {offset} | {snapshot['session_date']} | {_fmt(snapshot['features']['close_sma50']['value'], True)} | "
                        f"{_fmt(snapshot['features']['return20']['value'], True)} | {_fmt(snapshot['relative_to_spy20']['value'], True)} |")
                lines.append("")
        for proxy in ("SPY", "QQQ"):
            rs = stock["relative_strength"][proxy]
            lines += [f"Relative to {proxy}: 20-session ratio change {_fmt(rs['20']['value'], True)}, 60-session {_fmt(rs['60']['value'], True)}; market direction alignment {stock['market_alignment'][proxy]['status']}.", ""]
        lines += ["### Reported stop assessment", "", f"Reported stop {stop['reported_stop']}; reference close {_fmt(stop['reference_close'])}; "
            f"absolute distance {stop.get('absolute_distance', 'UNKNOWN')}, fraction of reference {stop.get('fraction_of_reference_close', 'UNKNOWN')}, "
            f"ATR units {stop.get('atr_normalized_distance', 'UNKNOWN')}. {stop.get('side_assessment', 'UNAVAILABLE')}.", "",
            "The stop's proximity to independently computed levels is descriptive. It does not establish why the expert chose it. Unexpected side merits investigation because entry and stop adjustment basis are unknown.", "",
            "| Technical level | Price | Stop minus level | Absolute ATR distance |", "| --- | ---: | ---: | ---: |"]
        for name, v in stop.get("technical_level_distances", {}).items():
            lines.append(f"| {name} | {_fmt(v['level'])} | {v['stop_minus_level']} | {v['absolute_atr_distance']} |")
        nearest = stock["interpretation"]["nearest_tested_stop_level"]
        if nearest:
            lines += ["", f"Nearest of the disclosed tested levels: {nearest['name']} at {_fmt(nearest['level'])}, "
                f"{float(nearest['absolute_atr_distance']):.3f} ATR from the reported stop. Proximity is a candidate technical reference, not proof of intended invalidation logic."]
        align = stock["market_alignment"]["SPY"]["status"]
        sector_align = sector["contexts"]["sector"].get("direction_alignment", {}).get("status", "UNAVAILABLE")
        lines += ["", "### Thesis and antithesis hypotheses", "",
            f"Potential thesis for the reported {obs['direction']}: the directionally supporting trend, momentum and relative-strength observations listed below "
            f"may explain part of the selection, alongside unknown discretionary information. SPY alignment is {align}; sector alignment is {sector_align}. "
            "These observations motivate a hypothesis to test; they do not establish a selection rule.", "",
            "Potential antithesis: mixed or opposing context, a non-unique taxonomy match, recent event risk, proxy mismatch, and subsequent data revisions can undermine a purely technical explanation. "
            "Even aligned context cannot establish entry timing or expected return. No selection universe or unchosen opportunities were observed.", "",
            "### Events and remaining uncertainty", ""]
        # Insert the individual evidence before the event section, keeping both
        # favorable and unfavorable observations visible for every recommendation.
        evidence = []
        for title, key in (("Supporting observations", "supporting_evidence"), ("Opposing observations", "opposing_evidence"),
                           ("Mixed or unresolved", "unresolved_or_mixed")):
            evidence += [title + ":", ""] + [f"- {v}" for v in stock["interpretation"][key]] + [""]
            if not stock["interpretation"][key]:
                evidence += ["No qualifying observation under these disclosed sign tests; this does not establish absence of risk.", ""]
        lines[-2:-2] = evidence
        for event in result["event_context.json"][s]["events"]:
            lines += [f"- {event['availability_category']}: {event['description']} ([source]({event['source_url']})); "
                f"published_at={event.get('published_at') or 'UNKNOWN'}, source date={event.get('source_date') or 'UNKNOWN'}. {event.get('publication_evidence', '')}"]
        lines += ["", "Company/news inventory is partial. Date-only evidence and SEC acceptance clocks alone are not promoted to verified publication timestamps. "
            "Industry and macro catalysts, complete corporate actions, historical bar dissemination clocks, entry/quantity/targets and private rationale remain unknown. No news is inferred from volume or gaps.", ""]
    lines += ["## Comparison and next reference classes", "", "| Symbol | Direction | Setup hypothesis | Stop / ATR | SPY alignment | Sector alignment |", "| --- | --- | --- | ---: | --- | --- |"]
    for s, v in result["comparison.json"]["standardized_vectors"].items():
        lines.append(f"| {s} | {v['direction']} | {v['setup']['classification']} | {v['stop_atr_distance'] or 'UNKNOWN'} | "
            f"{v['market_alignment']['SPY']['status']} | {(v['sector_alignment'] or {}).get('status', 'UNAVAILABLE')} |")
    lines += ["", "The LONG pair and SHORT pair use the same features, timing and side-aware stop formula. Six pairwise vectors and sector-leadership trajectories are in comparison.json. "
        "Future reference classes should separate setup geometry, market trajectory, sector strength, relative strength, volatility/liquidity and dated catalyst category. No full-universe search, screening-membership inference or statistical edge claim is made.", ""]
    return "\n".join(lines)


def _files(inputs, hashes, identity):
    spec, prices, coverage, calendar = read_inputs(inputs)
    result = derive(spec, prices, coverage, calendar)
    result["manifest.json"].update(inputs_sha256=hashes["bundle_sha256"], implementation=identity)
    files = {name: encode(value) for name, value in result.items()}
    files["report.md"] = markdown(result).encode()
    for r in spec["observations"]["recommendations"]:
        files[f"dossier-{r['symbol']}.md"] = markdown(result, only=r["symbol"]).encode()
    files.update({f"input-{name}": value for name, value in inputs.items()})
    files["input-hashes.json"] = encode(hashes)
    return files


def freeze_study(inputs, output):
    files, hashes = read_bundle(inputs)
    return write_bundle(Path(output), _files(files, hashes, implementation_identity()))


def load_study(path):
    files, hashes = read_bundle(path)
    inputs = {k[len("input-"):]: v for k, v in files.items() if k.startswith("input-") and k != "input-hashes.json"}
    input_hashes = json.loads(files["input-hashes.json"])
    from .inputs import _check_hashes
    _check_hashes(inputs, input_hashes)
    manifest = json.loads(files["manifest.json"])
    identity = implementation_identity()
    if manifest["implementation"] != identity:
        raise ValueError("comprehension implementation/shared dependency differs from frozen study")
    if files != _files(inputs, input_hashes, identity):
        raise ValueError("comprehension semantic output mismatch")
    return {"files": files, "hashes": hashes, "manifest": manifest}
