"""Deterministic, source-first explanations of conditional reconstructions."""


def number(value):
    return "unavailable" if value is None else f"{value:.3f}"


def interval(values):
    return "unavailable" if values is None else "–".join(number(v) for v in values)


def leading_table(episodes):
    lines = ["| Symbol | Reported direction/status/setup/stop | Leading late-bound reference | Compatibility vector | Other clocks |",
             "|---|---|---|---|---|"]
    for e in episodes:
        source = e["source"]
        late = next(c for c in e["clock_comparisons"] if c["clock_variant"] == "LATE_EMAIL_BOUND")
        leaders = late["leading"]
        text = "; ".join(f"{p['hypothesis']} {p['entry_session']} @{number(p['entry_price'])}, {p['policy']}" for p in leaders) or "No observed comparable entry"
        other = "; ".join(f"{c['clock_variant']}: " + (", ".join(sorted({p['hypothesis']+"/"+p['policy'] for p in c['leading']})) or "unranked")
                          for c in e["clock_comparisons"] if c is not late)
        vectors = "; ".join(str(p["evaluation_vector"]) for p in leaders)
        lines.append(f"| {e['symbol']} | {e['direction']} / {source['position_state']} / {source['setup_availability']} / {source['current_stop']} | {text} | {vectors or 'censored'} | {other} |")
    return "\n".join(lines)+"\n"


def markdown(result):
    episodes, summary = result["episodes.json"], result["summary.json"]
    cde = next(e for e in episodes if e["symbol"] == "CDE")
    cde_h1 = cde["clock_comparisons"][1]["candidates"][0]
    cde_reference = (f"The H1 reference is {number(cde_h1['entry_price'])} against opening stop {cde['source']['initial_stop']}; "
        f"activation R is {number(cde_h1['geometry']['reference_risk'])}, with +1R price {number(cde_h1['management'][0]['reference_target_1R'])}. "
        if cde_h1["status"] == "CONSTRUCTED" else "H1 has no geometrically valid observed entry in these inputs. ")
    lines = ["# Grimes reconstruction: October 18–26, 2026", "",
        "Conditional system identification over 26 source episodes, not observed execution or a strategy backtest. "
        "The source ledger remains authoritative: 14 OPEN, 12 CLOSED. Exact fills, sizes and realized P&L are unknown. "
        "Daily OHLC paths describe possibilities, not probabilities. All references assume native price/nominal stop compatibility except bounded corroborating quote anchors.", "",
        "## Leading explanations", "",
        "Rank vectors minimize continuation-conflict alert clusters, then maximize compatible later alert clusters, "
        "then prefer fewer extra management conventions, then construction support. Final source OPEN counts as a continuation constraint, "
        "not an independent later alert. Co-published actions count once. A leading scenario can still conflict with evidence; no score is a probability. "
        "Right-censored or untriggered entries cannot win through absence of evidence. Equal observation signatures remain equivalent even when simplicity breaks a ranking tie.", "",
        leading_table(episodes),
        "## Timing and interpretation", "",
        "Known alerts use their displayed minute bounds; their earlier RTH Close cannot be an execution after publication. "
        "The weekly source publication remains UNKNOWN. Conditional source-order/email bounds span Thursday evening through Sunday morning. "
        "EARLY_BEFORE_FIRST_OPEN tests Friday entry, LATE_EMAIL_BOUND tests Monday entry, and FIRST_SESSION_CLOSE_COMPATIBLE tests a Friday-close reference. "
        "These boundary clocks do not exhaust every possible intraday publication. The four Monday-evening additions require Tuesday bars absent from this fixed study.", "",
        "## Stop geometry and decision patterns", "",
        "All diagnostic definitions are agent-specified hypotheses, not documented Grimes entry rules. Twenty-session extrema, SMA distances, "
        "confirmed pivots and range ratios use only completed, available bars. ATR comes from the project's pinned shared mathematics. "
        "Reference risk uses the stop reported before hypothetical activation; the opening stop is also retained. It never resets after entry. "
        "Intraday candidate risk ranges span compatible OHLC references, without asserting executable slippage bounds.", ""]
    for direction, row in summary["direction_comparison"].items():
        lines.append(f"- {direction}: {row['source_episodes']} episodes; {row['usable_risk_episodes']} with conditional risk references; median episode midrange {number(row['median_episode_midrange_reference_risk_ATR'])} ATR; stop changes {row['stop_change_counts']}. This mixes setups and is not a matched causal comparison.")
    lines += ["", "Same-opening-alert H1 comparisons (shared information clock, not matched volatility/structure):", ""]
    for alert, directions in summary["same_opening_alert_risk_comparisons"].items():
        lines.append(f"- {alert}: "+"; ".join(d+": "+(", ".join(r['symbol']+" "+number(r['reference_risk_ATR'])+" ATR" for r in rows) or "unavailable") for d, rows in directions.items()))
    patterns = summary["opening_pattern_diagnostics"]
    for title, key, predicate, direction in (
        ("Long price near SMA20/50 (within 1 ATR)", "pullback_to_MA_within_1ATR", bool, "LONG"),
        ("Long range10/previous20 below 1", "range10_over_previous20", lambda x: x < 1, "LONG"),
        ("Short established downtrend", "trend_aligned", bool, "SHORT"),
        ("Short failed 20-session breakout", "failed_breakout20", bool, "SHORT"),
        ("Short 20-session breakdown", "breakdown20", bool, "SHORT"),
        ("Short bounce within downtrend", "bounce_in_downtrend", bool, "SHORT")):
        group = [p for p in patterns if p["direction"] == direction]
        usable = [p for p in group if p[key] is not None]
        yes = [p["symbol"] for p in usable if predicate(p[key])]
        no = [p["symbol"] for p in usable if not predicate(p[key])]
        lines.append(f"- {title}: {len(yes)}/{len(usable)} usable ({len(group)-len(usable)} unavailable). Support: {', '.join(yes) or 'none'}; counterexamples: {', '.join(no) or 'none'}. Descriptive overlap cannot identify the entry rule.")
    lines += ["", "Tight-risk/immediate-movement checks (H1, late clock):", ""]
    for e, pattern in zip(episodes, patterns):
        h1 = next(c for c in e["clock_comparisons"] if c["clock_variant"] == "LATE_EMAIL_BOUND")["candidates"][0]
        lines.append(f"- {e['symbol']}: risk {number(h1.get('geometry', {}).get('reference_risk_ATR'))} ATR; first-session directional Open-to-Close quote change {number(pattern['H1_first_session_reference_price_progress_ATR'])} ATR. Quote change includes any hypothetical exit and is not held-position P&L.")
    lines += ["", "Widening/tightening challenges to PR17 (late clock, all constructed entry references):", ""]
    for challenge in summary["pr17_challenges"]:
        lines.append(f"- {challenge['stop_change']}: {challenge['total']} changes; {challenge['usable']} with entry references; favorable across references {len(challenge['robust_favorable'])}; adverse/entry-sensitive {len(challenge['counterexamples_or_entry_sensitive'])}; unavailable {len(challenge['unavailable'])}. Event identifiers: favorable {challenge['robust_favorable']}; counterexamples {challenge['counterexamples_or_entry_sensitive']}; unavailable {challenge['unavailable']}.")
    lines += ["", "These comparisons test whether widening gives an adverse trade more room and tightening follows progress; exceptions prevent universal rules. "
        "MA/pivot distances, old-stop clearance and market-relative returns at each revision are retained in management_decisions.json. "
        "Their proximity alone cannot prove a causal stop-placement rule or regime motivation.", "",
        "## ENTERABLE, UNDERWAY and DROPPED", "",
        "UNDERWAY is an observed source classification, not a fill timestamp or proof of a particular trigger. "
        "Seven transitions are compared with pre-alert prices and all candidate paths below. Twelve DROPPED episodes remain in the inventory. "
        "An earlier model exit is an assumption conflict, not the source's closure cause. A DROP with a still-active path establishes only that "
        "Grimes stopped reporting the episode, not an exact execution, profit, time stop or discretionary rationale.", "",
        "UNDERWAY transitions with quote progress across the available entry references:", ""]
    for r in summary["underway_inventory"]:
        lines.append(f"- {r['symbol']}: {interval(r['counterfactual_price_progress_range'])} native price units, observed at {r['feature_session']} under the late clock.")
    lines += ["", "Favorable quote progress at these transitions is consistent with an established move; it does not identify an entry or prove +1R, "
        "partial realization, confirmation or a universal UNDERWAY threshold. ENTERABLE can coexist with exposure or later stop changes in the source; "
        "the labels alone do not encode execution size.", "", "## CDE and EBAY", "",
        "CDE remains SHORT / OPEN / UNDERWAY / 13.90. " + cde_reference +
        "Compare full-exit, partial-runner and continued-holding terminal paths below: a +1R touch alone does not establish a full source exit. "
        "The illustrative 50% fraction is not observed Grimes sizing.", "",
        "EBAY remains LONG / OPEN / ENTERABLE / 117.50. Compare the Friday/Monday entry cases, the old hard-stop paths and the deferred-review alternative below. "
        "An after-session revision cannot rescue a prior hard stop. Any independent quote anchors constrain price-only rescaling (see adjustment diagnostics). "
        "Untriggered confirmation is possible but is not evidence that no trade existed. Neither a leading alternative nor a pending review establishes Grimes' actual policy. "
        "A later intraday entry can differ; finer timing is needed to distinguish it.", "",
        "## Episode comparisons", ""]
    for e in episodes:
        lines += [f"### {e['symbol']} — {e['direction']}", "",
            f"Reported final state: {e['source']['position_state']} / {e['source']['setup_availability']}; opening stop {e['source']['initial_stop']}; latest {e['source']['current_stop']}. Actual entry, exit cause and P&L unknown.", "",
            "Source sequence (UNKNOWN remains a source fact):", ""]
        for a in e["source"]["events"]:
            lines.append(f"- {a['published_at'] or 'UNKNOWN'} {a['type']}" + (f" stop {a['stop']}" if a.get("stop") else "") + (f" from {a['previous_stop']}" if a.get("previous_stop") else "") + (f" setup {a['setup_after']}" if a.get("setup_after") else ""))
        late = next(c for c in e["clock_comparisons"] if c["clock_variant"] == "LATE_EMAIL_BOUND")
        construction = late["candidates"][0]["construction"]
        distances = construction["opening_stop_distance_to_levels_ATR"]
        lines += ["", "Opening-stop minus pre-alert structural level, in ATR (signed native price distance): " +
            (", ".join(k+" "+number(v) for k, v in distances.items()) or "unavailable")+". Proximity does not establish why that stop was chosen.", "",
            "Later decisions under the late/email clock (price progress is counterfactual, including after a hypothetical exit):", "",
            "| Action / source publication | Available price session | Directional quote progress range | Stop change / prior-stop clearance ATR | Stop minus MA20/50 ATR | Market relative 20-session price return |",
            "|---|---|---|---|---|---|"]
        for r in result["management_decisions.json"]:
            if r["symbol"] != e["symbol"] or r["clock_variant"] != "LATE_EMAIL_BOUND":
                continue
            levels = r["new_stop_distance_to_levels_ATR"]
            market = "; ".join(k+" "+number(v.get("value") if v else None) for k, v in r["market"].items())
            lines.append(f"| {r['action']} / {r['source_published_at'] or 'UNKNOWN'} | {r['feature_session']} | {interval(r['counterfactual_price_progress_range'])} | {r['stop_change'] or 'n/a'} / {number(r['old_stop_clearance_ATR'])} | {number(levels.get('sma20'))} / {number(levels.get('sma50'))} | {market} |")
        for clock in e["clock_comparisons"]:
            lines += ["", f"**{clock['clock_variant']}** — {clock['confidence']}", "",
                "| Entry hypothesis | State/reference | Risk ATR range | Construction rationale | Management comparison (conflicts / support / rank) |",
                "|---|---|---|---|---|"]
            for p in clock["candidates"]:
                management = "; ".join(f"{s['policy']}: {len(s.get('conflict_alert_clusters', []))}/{len(s.get('compatible_alert_clusters', []))}/{s['rank'] or 'unranked'} " +
                    ",".join(sorted({(t['closed_reason'] or ('REVIEW_PENDING' if t['review_pending'] else 'ACTIVE'))+':remaining='+str(t['remaining']) for t in s['terminal_possibilities']})) for s in p["management"])
                reference = f"{p['status']} {p['entry_session'] or ''} @{number(p['entry_price'])} [{interval(p['entry_price_range'])}]"
                rationale = p["rationale"] + ("; "+p["reason"] if p.get("reason") else "")
                geometry = p.get('geometry', {})
                risk_range = interval(geometry.get('positive_protective_risk_ATR_range')) + (' (zero excluded)' if geometry.get('zero_lower_bound_is_excluded') else '')
                lines.append(f"| {p['hypothesis']} | {reference} | {risk_range} | {rationale} | {management} |")
            lines += ["", f"Observational-equivalence groups: {len(clock['observational_equivalence_classes'])}. Full memberships, terminal paths, causal activation evidence, timing bounds and compatibility observations are in episodes.json."]
        lines += ["", "Unresolved: "+"; ".join(e["questions"])+".", ""]
    lines += ["## Limits", "",
        "No inference of historical screening membership, population performance or trading edge. The sample is source-selected and tiny. "
        "Ranks are conditional diagnostic ordering, not estimated likelihoods. Two canonical daily extrema orders expose ambiguity but do not exhaust every "
        "intraday oscillation or gap; no execution-cost/size/P&L simulator is introduced. MFE/MAE fields are upper envelopes over merged compatible paths, "
        "not simultaneous realized excursions. No new market data were acquired. Native volume units and dollar-volume eligibility remain unverified. "
        "The preserved public source-status CSV is not regenerated by this study.", ""]
    return "\n".join(lines)


def adjustment_markdown(result):
    lines = ["# Price and volume diagnostics", "",
        "Native captures remain immutable. Existing independently documented split assertions are retrospective corroboration, "
        "not newly acquired prices or historically available screening evidence. Derived views undo one known split component only; they are never labeled verified raw OHLC. "
        "Volume is unchanged in every derived view.", "",
        "| Symbol/effective split | Native post-Open/pre-Close | Ratio after undoing known component | Median native volume after/before |",
        "|---|---|---|---|"]
    for r in result["split_diagnostics.json"]:
        if r["status"] == "OBSERVED_KNOWN_SPLIT_WINDOW":
            lines.append(f"| {r['symbol']} {r['effective_date']} {r['ratio_new_over_old']}:1 | {number(r['native_post_open_over_pre_close'])} | {number(r['known_component_undone_post_open_over_pre_close'])} | {number(r['observed_after_over_before_median_native_volume'])} |")
    lines += ["", "Near-continuous native prices across these splits corroborate split adjustment. Neither these two examples nor a volume ratio "
        "establish exhaustive corporate-action coverage, raw nominal prices, shares-vs-lots settings, dividend adjustment, or split-adjusted volume. "
        "Technical indicators can be conditional on a consistent native scale; stop simulation additionally needs nominal-stop compatibility. "
        "Absolute dollar volume requires documented contemporaneous price and share units and is not admitted here.", "",
        "Uniformly scaling prices, stops and ATR preserves risk/ATR and barrier ordering. A price-only scale can change those conclusions and "
        "therefore needs independent evidence; no factor is fitted to make a trade succeed. EXPLORATORY_RECONSTRUCTION supports explicitly labeled "
        "uniform sensitivity views with unchanged native volume, never a claim of raw reconstruction.", ""]
    for r in result["price_scale_diagnostics.json"]:
        lines.append(f"- {r['symbol']} conId {r['con_id']}: {r['scale']}; volume {r['volume_basis']}.")
        if r["symbol"] == "EBAY":
            lines.append(f"  Avoiding the 119.20 hard-stop touch through price-only scaling would require a factor strictly greater than {r['minimum_price_only_scale_to_avoid_old_stop_touch']}. This conflicts with the retained matching 117.87 nominal Low anchor; no such rescaling is supported.")
    return "\n".join(lines)+"\n"
