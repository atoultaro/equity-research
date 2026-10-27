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
from .methodology import management, validate_methodology
from .amendment import es_context, return_verification

MARKETS = ("SPY", "QQQ", "RSP", "IWM")
OFFSETS = (0, 5, 20, 60, 120)
VECTOR = ("close_sma20", "close_sma50", "close_sma150", "close_sma200", "sma50_slope20",
          "daily_return", "return_5d", "return_20d", "return_60d", "atr14_fraction", "realized_volatility20", "drawdown_high252",
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
            label = {"return20": "20-session price return", "return60": "60-session price return"}.get(name, name)
            support.append(f"{label}={value*100:.2f}% supports the reported {direction} direction")
        elif sign*value < 0:
            label = {"return20": "20-session price return", "return60": "60-session price return"}.get(name, name)
            opposition.append(f"{label}={value*100:.2f}% opposes the reported {direction} direction")
    for proxy in ("SPY", "QQQ"):
        value = stock["relative_strength"][proxy]["20"]["value"]
        if value is None:
            missing.append(f"relative_to_{proxy}20")
        elif sign*value > 0:
            support.append(f"20-session price ratio change vs {proxy}={value*100:.2f}% supports directional relative strength")
        elif sign*value < 0:
            opposition.append(f"20-session price ratio change vs {proxy}={value*100:.2f}% opposes directional relative strength")
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
    return {"attribution": "RESEARCH_HYPOTHESIS", "supporting_evidence": support, "opposing_evidence": opposition, "unresolved_or_mixed": missing,
        "scope": "Sign tests and geometric proximity only; no calibrated score, causality or attribution of private rationale"}


def derive(spec, prices, coverage, calendar, *, methodology=None, amendment=None, close_reference_1r=False):
    if type(close_reference_1r) is not bool:
        raise ValueError("closing reference scenario option must be boolean")
    observations = deepcopy(spec["observations"])
    observations["attribution"] = "EXPERT_REPORTED"
    for row in observations["recommendations"]:
        row.update(attribution="EXPERT_REPORTED", intended_setup=None)
    if methodology:
        methodology = validate_methodology(methodology)
    if close_reference_1r and (not methodology or observations["recommendation_date"] != "2026-10-26"):
        raise ValueError("October 26 reference scenario requires an explicit operator methodology")
    if amendment and amendment.get("schema_version") != "expert_amendment_v1":
        raise ValueError("unsupported expert amendment evidence schema")
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
        "attribution": "MARKET_OBSERVED",
        "es_context": es_context(spec.get("es_context", {"status": "NOT_AVAILABLE", "reason": "NO_VERIFIED_ES_INPUT"}), amendment, calendar, end)}
    for s in MARKETS:
        current = evolution(s)["0"]["features"]
        market["transition_deltas"][s] = {}
        for offset in OFFSETS[1:]:
            old = evolution(s).get(str(offset))
            market["transition_deltas"][s][str(offset)] = {k: (
                round(current[k]["value"]-old["features"][k]["value"], 12)
                if old and current[k]["value"] is not None and old["features"][k]["value"] is not None else None)
                for k in ("close_sma200", "sma50_slope20", "return20", "realized_volatility20", "drawdown_high252")}
    sectors, stocks, stops, events, vectors, trade_management = {}, {}, {}, {}, {}, {}
    for obs in observations["recommendations"]:
        symbol, direction = obs["symbol"], obs["direction"]
        f = panel.features(symbol, end)
        stocks[symbol] = {"session_date": end, "attribution": "MARKET_OBSERVED", "features": f, "research_setup_hypotheses": setup(f),
            "stock_trend_alignment": alignment(f, direction), "relative_strength": {},
            "market_alignment": {m: alignment(evolution(m)["0"]["features"], direction) for m in MARKETS}}
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
        sectors[symbol] = {"classification_attribution": "RESEARCH_HYPOTHESIS", "context_price_attribution": "MARKET_OBSERVED",
            "classification": mapping, "contexts": contexts}
        stops[symbol] = stop_analysis(obs, f)
        stocks[symbol]["interpretation"] = interpretation(stocks[symbol], contexts, stops[symbol], direction)
        trade_management[symbol] = management(obs, f["close"]["value"], methodology, scenario=close_reference_1r)
        inventory = [e for e in spec.get("event_evidence", []) if e.get("symbol") in {symbol, "MARKET", "INDUSTRY"}]
        events[symbol] = {"events": [classify_event(e, cutoff) for e in inventory],
            "coverage": "PARTIAL_DOCUMENTED_INVENTORY_NOT_AN_EVENT_COMPLETENESS_ATTESTATION",
            "unknowns": ["Exact recommendation publication and execution times", "Complete earnings/action calendar",
                "Comprehensive company, industry and macro news; no catalyst inferred from OHLCV", "Expert's private rationale"]}
        vectors[symbol] = {"direction": direction, "action": obs["action"], "units": "dimensionless fractions except explicitly named native dollar-volume proxy",
            "reported_fields_attribution": "EXPERT_REPORTED", "features_attribution": "MARKET_OBSERVED",
            "features": {k: f[k]["value"] for k in VECTOR}, "research_setup_hypotheses": stocks[symbol]["research_setup_hypotheses"],
            "intended_expert_setup": None,
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
    manifest = {"schema_version": "expert_comprehension_v2", "feature_version": VERSION,
        "attribution_classes": {"EXPERT_REPORTED": "Operator-provided recommendation facts, not independently verified",
            "MARKET_OBSERVED": "Computed from frozen provider observations under stated basis/timing assumptions",
            "RESEARCH_HYPOTHESIS": "Researcher interpretation or reference scenario; never an intended expert setup or actual fill"},
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
        "setup_policy": "No automatic intended-setup classification. Retain multiple competing research hypotheses; 20-session diagnostics are not documented Grimes requirements",
        "closing_reference_1r_scenario_enabled": close_reference_1r,
        "legacy_return_aliases": {"return1": "daily_return", "return5": "return_5d", "return20": "return_20d", "return60": "return_60d"},
        "methodology_id": methodology["methodology_id"] if methodology else None}
    result = {"expert_recommendations.json": observations, "data_coverage.json": coverage, "market_context.json": market,
        "sector_context.json": sectors, "stock_features.json": stocks, "stop_analysis.json": stops,
        "event_context.json": events, "comparison.json": comparison, "manifest.json": manifest,
        "expert_methodology.json": methodology or {"source_status": "UNKNOWN_OR_MISSING"},
        "trade_management.json": trade_management,
        "return_validation.json": return_verification(panel, prices, end, coverage, amendment)}
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
    observations = result['expert_recommendations.json']
    market = result['market_context.json']
    lines = ['# Expert trade comprehension — Adam Grimes', '',
        f"Observation {observations['recommendation_date']}; assumed after-close cutoff {observations['analysis_cutoff']}.", '',
        '**EXPERT_REPORTED**: operator-provided direction, OPEN_NEW_POSITION action and reported stop. Actual entry, execution time, quantity and trade-specific targets/exits remain UNKNOWN.', '',
        '**MARKET_OBSERVED**: calculations from frozen IBKR completed-session OHLCV. Price availability is reconstructed as cash close +60 minutes; later retrieval can contain revisions.', '',
        '**RESEARCH_HYPOTHESIS**: competing technical explanations, candidate invalidation levels and optional closing-reference arithmetic. These do not identify Grimes\' intended setup or verified execution.', '',
        'The separate methodology specification is OPERATOR_REPORTED, not independently verified. No simulated fills, exits, realized P&L or portfolio performance are produced.', '',
        'Native TRADES prices are documented split-adjusted, not dividend-adjusted; volume units and reported-stop adjustment compatibility remain unverified.', '',
        '## MARKET_OBSERVED — October 26 closing-price returns by horizon', '',
        'Every return is Close(t)/Close(t−n completed trading sessions)−1 and requires n+1 consecutive calendar observations. Daily means previous completed session to current, not a trailing 20-session return.', '',
        '| Market proxy | Daily return (1 session) | Trailing 5-session return | Trailing 20-session return | Trailing 60-session return |',
        '| --- | ---: | ---: | ---: | ---: |']
    for proxy, snapshots in market['proxies'].items():
        f = snapshots['0']['features']
        lines.append(f'| {proxy} | ' + ' | '.join(_fmt(f[k]['value'], True) for k in ('daily_return', 'return_5d', 'return_20d', 'return_60d')) + ' |')
    lines += ['', '### Independent QQQ reconciliation from frozen closes', '']
    for name, check in result['return_validation.json']['QQQ'].items():
        horizon = 'daily (1 session)' if name == 'daily_return' else 'trailing 20 sessions'
        if check['status'] == 'UNAVAILABLE':
            lines += [f"QQQ {horizon}: UNAVAILABLE ({check['reason']}).", '']
        else:
            value = float(check['calculated_percent'])
            claim = check['comparison_approximation_percent']
            lines += [f"QQQ **{horizon}**: {check['first_session']} Close {check['first_close']} → {check['last_session']} Close {check['last_close']} = **{value:+.6f}%**. "
                f"Comparison approximation ({check['comparison_source']}): {claim if claim is not None else 'not supplied'}%; difference {check['difference_percentage_points'] or 'not compared'} percentage points; "
                f"tolerance {check['rounding_tolerance_percentage_points']} percentage points. {check['status']}.", '']
    lines += ['The calculations use original frozen decimal closes and retain both source-row locators and native price basis in return_validation.json. Daily and trailing 20-session returns have distinct horizons and can have opposite signs. Operator approximations are comparison evidence, never replacements for provider values.', '',
        '## MARKET_OBSERVED — market-regime evolution', '',
        '| Proxy | Sessions before cutoff | Snapshot session | Close/SMA200 − 1 | Trailing 20-session return | Daily RV over 20 sessions | Drawdown from trailing 252-session High |',
        '| --- | ---: | --- | ---: | ---: | ---: | ---: |']
    for proxy, snapshots in market['proxies'].items():
        for offset, snap in snapshots.items():
            f = snap['features']
            lines.append(f"| {proxy} | {offset} | {snap['session_date']} | " + ' | '.join(_fmt(f[k]['value'], True) for k in ('close_sma200', 'return_20d', 'realized_volatility20', 'drawdown_high252')) + ' |')
    lines += ['', 'Volatility is unannualized population SD of 20 daily price returns. Snapshot deltas preserve 5/20/60/120-session evolution; no year-wide regime label. RSP/SPY is a participation proxy, not constituent breadth.', '',
        '| Current market proxy | Close/SMA20 − 1 | Close/SMA50 − 1 | Close/SMA150 − 1 | Close/SMA200 − 1 | SMA50 change over 20 sessions |',
        '| --- | ---: | ---: | ---: | ---: | ---: |']
    for proxy, snapshots in market['proxies'].items():
        f = snapshots['0']['features']
        lines.append(f'| {proxy} | ' + ' | '.join(_fmt(f[k]['value'], True) for k in ('close_sma20', 'close_sma50', 'close_sma150', 'close_sma200', 'sma50_slope20')) + ' |')
    es = market['es_context']
    lines += ['', '### ES historical coverage', '', f"ES for October 26: **{es['status']}**. {es.get('reason', '')}", '',
        f"Last verified locally available ES session: {es.get('last_verified_available_session') or 'UNKNOWN'}. {es['historical_research_role']}", '']
    missing = es.get('missing_interval')
    if missing:
        lines += [f"Missing recent interval: {missing['first_missing_cash_session']} through {missing['last_missing_cash_session']} ({missing['missing_cash_session_count']} XNYS cash-session reference dates). "
            'This is not a futures ETH completeness claim. Existing metadata and source hashes remain embedded; no ES extrapolation, new download or automatic replacement with recent IBKR futures.', '']
    origins = ', '.join(sorted(set(result['manifest.json']['source_origins'].values())))
    lines += [f'Source origins: {origins}. Synthetic fixtures demonstrate arithmetic only.', '']
    for obs in observations['recommendations']:
        symbol = obs['symbol']
        if only and only != symbol:
            continue
        stock, stop, sector = (result[k][symbol] for k in ('stock_features.json', 'stop_analysis.json', 'sector_context.json'))
        f, coverage = stock['features'], result['data_coverage.json'].get(symbol)
        lines += [f"## {symbol} — {obs['direction']} / OPEN_NEW_POSITION", '', '### EXPERT_REPORTED — original recommendation', '',
            f"> {obs['original_recommendation']}", '', f"Source: {observations['source_reference']}. Reported stop: **{obs['reported_stop']}**. "
            'Added means a newly opened position, never an increase to existing holdings. Actual entry, execution time, size, profit target and observed trade-specific exit instruction are UNKNOWN.', '',
            '### MARKET_OBSERVED — stock price structure', '']
        if coverage:
            lines += [f"Qualified conId {coverage['contract']['conId']}, {coverage['contract']['primaryExchange']}; {coverage['first_observed']}–{coverage['last_observed']}, {coverage['observed_sessions']} sessions. "
                f"Missing expected: {len(coverage['missing_expected_sessions'])}; pre-listing exclusions: {len(coverage['listing_excluded_sessions'])}; three-year target met: {coverage['three_year_target_met']}.", '']
        else:
            lines += ['Stock capture NOT_AVAILABLE; dependent measurements remain unavailable.', '']
        lines += ['| Stock measurement | Value |', '| --- | ---: |']
        fields = [('close', 'Reference Close', False)] + [(f'sma{n}', f'SMA{n} price', False) for n in (20, 50, 150, 200)] + [
            ('sma50_slope20', 'SMA50 change over 20 sessions', True), ('daily_return', 'Daily price return (1 session)', True),
            ('return_5d', 'Trailing 5-session price return', True), ('return_20d', 'Trailing 20-session price return', True),
            ('return_60d', 'Trailing 60-session price return', True), ('atr14', 'Simple ATR14 price units', False),
            ('atr14_fraction', 'ATR14 / Close', True), ('realized_volatility20', 'Daily RV over 20 sessions', True),
            ('high20', 'High over 20 sessions', False), ('low20', 'Low over 20 sessions', False),
            ('high60', 'High over 60 sessions', False), ('low60', 'Low over 60 sessions', False),
            ('drawdown_high252', 'Drawdown from trailing 252-session High', True),
            ('range_contraction20_60', '20-session / 60-session range ratio', False),
            ('range_contraction10_previous20', 'Latest 10-session / preceding 20-session range ratio', False),
            ('volume_vs_prior20', 'Current native volume / prior 20-session mean', False)]
        for key, label, pct in fields:
            lines.append(f"| {label} | {_fmt(f[key]['value'], pct)} |")
        hypotheses = stock['research_setup_hypotheses']
        lines += ['', '### RESEARCH_HYPOTHESIS — competing explanations, expert intent unresolved', '',
            '**Intended expert setup: UNKNOWN.** No diagnostic result assigns Grimes\' setup or his rules. A fresh closing 20-session breakdown is not a documented Grimes requirement.', '',
            '| Researcher-defined descriptive diagnostic | Observed value | Precise causal definition |', '| --- | --- | --- |']
        for name in ('breakout20', 'breakdown20', 'failed_breakout20', 'support_rejection', 'resistance_rejection'):
            lines.append(f"| {name} | {_fmt(f[name]['value'])} | {hypotheses['diagnostic_definitions'][name]} |")
        lines += ['', 'The legacy composite bearish diagnostic additionally requires Close < SMA50. Legacy bullish MA-proximity requires Close > SMA200, SMA50 > SMA200 and distance within one ATR of SMA20 or SMA50. These are researcher-defined parameters, not independently documented Grimes methodology.', '',
            '| Competing interpretation | Evidence status | Supporting diagnostics | Limitation |', '| --- | --- | --- | --- |']
        for hypothesis in hypotheses['hypotheses']:
            lines.append(f"| {hypothesis['interpretation']} | {hypothesis['status']} | {', '.join(hypothesis['supporting_diagnostics']) or 'Unresolved'} | {hypothesis['limitation']} |")
        lines += ['', 'Multiple compatible interpretations remain represented. Two declines alone never establish a second leg.', '',
            '### Sector context — observed prices and researcher proxy mapping', '']
        classification = sector['classification']
        lines += [f"Mapping status: {classification['status']}. Classification/proxy choices are RESEARCH_HYPOTHESIS; ETF OHLCV measurements are MARKET_OBSERVED.", '']
        if classification.get('source_url'):
            lines += [f"Dated business evidence: [{classification['issuer_identity']}]({classification['source_url']}), {classification['source_document_date']}; "
                f"effective date {classification.get('effective_date') or 'UNKNOWN'}. {classification['proxy_limitations']} Historical membership is UNKNOWN.", '']
        for kind, context in sector['contexts'].items():
            if context['status'] != 'AVAILABLE':
                lines += [f"{kind}: NOT_AVAILABLE ({context['reason']}).", '']
                continue
            relative = stock['relative_strength'][kind]
            lines += [f"{kind}: **{context['proxy']}**; direction alignment {context['direction_alignment']['status']} under disclosed researcher sign tests. "
                f"Stock/proxy price ratio change: trailing 20 sessions {_fmt(relative['20']['value'], True)}, trailing 60 sessions {_fmt(relative['60']['value'], True)}.", '',
                '| Sessions before cutoff | Snapshot session | Proxy/SMA50 − 1 | Proxy trailing 20-session return | Proxy/SPY trailing 20-session ratio change |',
                '| ---: | --- | ---: | ---: | ---: |']
            for offset, snap in context['evolution'].items():
                lines.append(f"| {offset} | {snap['session_date']} | {_fmt(snap['features']['close_sma50']['value'], True)} | "
                    f"{_fmt(snap['features']['return_20d']['value'], True)} | {_fmt(snap['relative_to_spy20']['value'], True)} |")
            lines.append('')
        for proxy in ('SPY', 'QQQ'):
            rs = stock['relative_strength'][proxy]
            lines += [f"Stock/{proxy} trailing price-ratio changes: 20 sessions {_fmt(rs['20']['value'], True)}, 60 sessions {_fmt(rs['60']['value'], True)}. "
                f"Directional market alignment: {stock['market_alignment'][proxy]['status']} (researcher interpretation).", '']
        lines += ['### Stop — reported fact, observed distances, candidate invalidation hypotheses', '',
            f"EXPERT_REPORTED stop {stop['reported_stop']}; reference Close {_fmt(stop['reference_close'])}. Absolute distance {stop.get('absolute_distance', 'UNKNOWN')}; "
            f"percentage of reference Close {_fmt(float(stop['fraction_of_reference_close']) if stop.get('fraction_of_reference_close') else None, True)}; "
            f"ATR distance {stop.get('atr_normalized_distance', 'UNKNOWN')}. {stop.get('side_assessment', 'UNAVAILABLE')}.", '']
        nearest = stop.get('nearest_numerical_technical_level')
        if nearest:
            lines += [f"Nearest **numerical** tested level: {nearest['name']} at {_fmt(nearest['level'])}, absolute price distance {nearest['absolute_price_distance']}, "
                f"ATR distance {nearest['absolute_atr_distance'] or 'UNKNOWN'}. Numerical proximity does not establish a meaningful invalidation level.", '']
        lines += ['| All tested numerical levels | Price | Stop minus level | Absolute ATR distance |', '| --- | ---: | ---: | ---: |']
        for name, value in stop.get('technical_level_distances', {}).items():
            lines.append(f"| {name} | {_fmt(value['level'])} | {value['stop_minus_level']} | {value['absolute_atr_distance']} |")
        lines += ['', 'Candidate directionally relevant levels (RESEARCH_HYPOTHESIS): support below reference Close for LONG, resistance above it for SHORT. Expected protective stop is strictly below support or strictly above resistance, respectively.', '',
            '| Candidate | Role | Price | Stop/level absolute ATR distance | Stop on expected protective side? |', '| --- | --- | ---: | ---: | --- |']
        for candidate in stop.get('directional_invalidation_candidates', []):
            lines.append(f"| {candidate['name']} | {candidate['candidate_role']} | {_fmt(candidate['level'])} | {candidate['absolute_atr_distance']} | {candidate['stop_on_expected_protective_side']} |")
        if not stop.get('directional_invalidation_candidates'):
            lines += ['| Unresolved / no eligible measured level | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |']
        lines += ['', 'These are candidate proxies, not independently documented expert stop logic. Entry, original stop units and actual invalidation rationale remain unknown.', '',
            '### Operator-reported current 1R methodology and optional reference scenario', '']
        manage = result['trade_management.json'][symbol]
        convention = manage['profit_taking_convention']
        if convention:
            policy = 'SHORT: close 100% at +1 original R; no runner.' if obs['direction'] == 'SHORT' else 'LONG: close at least one-third of the original position at +1 original R; exact fraction is UNKNOWN; allow the remainder to run.'
            lines += [f"**OPERATOR_REPORTED**, not independently verified: {policy} The operator applies this current convention to this new-position observation; it is not an independently observed exit instruction for this individual trade.", '',
                'Subsequent stop changes, final exit rules and remaining-exit timing are UNKNOWN. Actual entry and actual 1R target remain UNKNOWN.', '']
        else:
            lines += ['Methodology not supplied for this input: UNKNOWN_OR_MISSING.', '']
        scenario = manage['reference_scenario']
        if scenario:
            lines += ['**RESEARCH_HYPOTHESIS — hypothetical closing-reference arithmetic only.** reference_entry_basis=OCT_26_CLOSE; is_actual_execution=false; actual_target=null.', '',
                '| Hypothetical entry (October 26 Close) | Reported stop | Hypothetical original per-share R | Hypothetical +1R target | Actual target |',
                '| ---: | ---: | ---: | ---: | --- |',
                f"| {_fmt(scenario['hypothetical_entry'])} | {obs['reported_stop']} | {scenario['hypothetical_original_per_share_risk'] or 'UNKNOWN'} | {scenario['hypothetical_1R_target'] or 'UNKNOWN'} | UNKNOWN |", '',
                f"Scenario status: {scenario['status']}; {scenario['reason'] or 'arithmetic available under assumed common price units'}. No entry, target fill or exit event is created.", '']
        else:
            lines += ['Closing-reference 1R scenario disabled. No hypothetical target supplied.', '']
        lines += ['### RESEARCH_HYPOTHESIS — thesis, antithesis and unresolved questions', '']
        for title, key in (('Potential thesis — supporting observations', 'supporting_evidence'),
                           ('Potential antithesis — opposing observations', 'opposing_evidence'), ('Mixed or unresolved context', 'unresolved_or_mixed')):
            lines += [title + ':', ''] + [f'- {value}' for value in stock['interpretation'][key]] + ['']
            if not stock['interpretation'][key]:
                lines += ['No qualifying observation under these disclosed sign tests; other evidence can still matter.', '']
        questions = {
            'SAIL': 'A LONG can be consistent with larger-trend strength and relative performance despite an intraday rejection of the previous 20-session High. That rejection remains contrary short-term evidence; it does not uniquely determine expert intent or invalidate the recommendation. The actual entry/path and discretionary information needed to choose between explanations remain unknown.',
            'SLB': 'Recovery or pullback within a trend is a competing interpretation of MA proximity and recent momentum. Compare the measured stock/sector ratio changes before claiming sector leadership; a stock can recover while lagging its energy proxy. Entry timing and a complete preceding pullback structure remain unverified.',
            'GE': 'Continuation of weakness does not require a new 20-session closing low. A failed-rally or resistance-rejection interpretation requires the separately defined rejection evidence; if unavailable it remains unresolved. No second leg is asserted without a validated ordered impulse/pullback/renewal structure.',
            'SCCO': 'Negative broad-market relative strength can coexist with positive copper-peer relative strength. This mixed comparison leaves several explanations possible, including different peer weights and individual price structure; it does not establish why the expert shorted. The peer contradiction remains visible rather than being turned into a unique setup.'}
        lines += [questions.get(symbol, 'Expert intent remains unresolved; measured conditions support competing interpretations.'), '',
            '### Event evidence and remaining unknowns', '']
        for event in result['event_context.json'][symbol]['events']:
            lines += [f"- {event['availability_category']}: {event['description']} ([source]({event['source_url']})); publication {event.get('published_at') or 'UNKNOWN'}, source date {event.get('source_date') or 'UNKNOWN'}."]
        lines += ['', 'Publication clocks, complete action/news inventories and expert motives are unknown. Research retrieval dates, price gaps and volume do not establish contemporaneously known news. All actual entry/exit instructions and executed exits remain unknown.', '']
    lines += ['## Comparison — stock returns by horizon and unresolved expert setups', '',
        '| Stock | Reported direction | Daily return (1 session) | Trailing 5-session return | Trailing 20-session return | Trailing 60-session return | Intended expert setup | Reference stop / ATR |',
        '| --- | --- | ---: | ---: | ---: | ---: | --- | ---: |']
    for symbol, vector in result['comparison.json']['standardized_vectors'].items():
        values = vector['features']
        lines.append(f"| {symbol} | {vector['direction']} | " + ' | '.join(_fmt(values[k], True) for k in ('daily_return', 'return_5d', 'return_20d', 'return_60d')) + f" | UNKNOWN | {vector['stop_atr_distance'] or 'UNKNOWN'} |")
    lines += ['', 'Six pairwise observed-feature differences and fixed-proxy leadership trajectories remain in comparison.json. Multiple research hypotheses are retained; no screened opportunity universe, expert rule reconstruction, prediction model or profitability inference is made.', '']
    return '\n'.join(lines)


def _files(inputs, hashes, identity):
    spec, prices, coverage, calendar = read_inputs(inputs)
    options = json.loads(inputs.get("study-options.json", b"{}"))
    if "parent_input_hashes" in options:
        from .inputs import _check_hashes
        parent = options["parent_input_hashes"]
        _check_hashes({name: inputs[name] for name in parent["files"]}, parent)
    result = derive(spec, prices, coverage, calendar,
        methodology=json.loads(inputs["expert-methodology.json"]) if "expert-methodology.json" in inputs else None,
        amendment=json.loads(inputs["amendment-evidence.json"]) if "amendment-evidence.json" in inputs else None,
        close_reference_1r=options.get("close_reference_1r", False))
    result["manifest.json"].update(inputs_sha256=hashes["bundle_sha256"], implementation=identity)
    if "parent_input_hashes" in options:
        result["manifest.json"]["original_source_inputs_sha256"] = options["parent_input_hashes"]["bundle_sha256"]
    files = {name: encode(value) for name, value in result.items()}
    files["report.md"] = markdown(result).encode()
    for r in spec["observations"]["recommendations"]:
        files[f"dossier-{r['symbol']}.md"] = markdown(result, only=r["symbol"]).encode()
    files.update({f"input-{name}": value for name, value in inputs.items()})
    files["input-hashes.json"] = encode(hashes)
    return files


def freeze_study(inputs, output, *, methodology=None, amendment=None, close_reference_1r=False):
    files, hashes = read_bundle(inputs)
    if methodology or amendment or close_reference_1r:
        files["study-options.json"] = encode({"parent_input_hashes": hashes, "close_reference_1r": close_reference_1r})
        if methodology:
            files["expert-methodology.json"] = Path(methodology).read_bytes()
        if amendment:
            files["amendment-evidence.json"] = Path(amendment).read_bytes()
        mapping = {k: digest(v) for k, v in sorted(files.items())}
        hashes = {"schema_version": "artifact_hashes_v1", "algorithm": "sha256", "files": mapping, "bundle_sha256": digest(encode(mapping))}
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
