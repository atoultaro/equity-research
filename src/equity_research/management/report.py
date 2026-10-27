"""Empirical tables, counterexamples and explicit limits; no execution claims."""


def fmt(value, *, fraction=False):
    return "UNAVAILABLE" if value is None else f"{value*(100 if fraction else 1):.4f}"


def proportion(record):
    n, d = record["numerator"], record["denominator"]
    return f"{n}/{d}"+(f" ({100*n/d:.1f}%)" if d else " (undefined)")


def dist(record):
    return f"{fmt(record['median'])} [{fmt(record['min'])}, {fmt(record['max'])}]; usable {record['usable']}/{record['total']}"


def current(row, key):
    p = row["conditional_path"]["current_progress"]
    return p[key] if p else None


def references(items):
    return "; ".join(f"{r['symbol']} ({r['event_id']}, {r['value']})" for r in items) or "None among usable observations"


def exit_description(events):
    return "; ".join(
        f"{e['session_date']} {e.get('status', 'MODEL')}" for e in events) or "UNAVAILABLE / no supporting modeled observation"


def dossier(data, symbol):
    p = next(p for p in data["positions.json"] if p["symbol"] == symbol)
    rows = [r for r in data["decision_features.json"] if r["symbol"] == symbol]
    closure = next((r for r in data["closure_hypotheses.json"] if r["symbol"] == symbol), None)
    duration = p["duration"]
    path = p["conditional_path"]
    lines = [f"# {symbol}: reported management and decision evidence", "",
        f"Source {p['direction']}, final {p['source_position_state']}, setup {p['source_setup']}. Initial stop {p['initial_stop']}; latest source stop {p['latest_source_stop']}.", "",
        f"Source opening {p['opening_event_id']}; source closing {p['closing_event_id'] or 'not observed, right-censored'}. Actual entry, holding duration, fill prices, size and realized P&L are unknown.", "",
        f"Eligible sessions under the PR16 availability-bound entry scenario: {duration['email_bound_scenario_eligible_sessions']}. Publication-based range: {duration['publication_based_session_range'] or 'UNRESOLVED'}. Conditional ordered-publication bracket: {duration['conditional_ordered_publication_bracket_sessions']}. The weekly exact publication stays null; email availability is separate evidence.", "",
        "All price/ATR/R progress is hypothetical. Stop-native-unit comparisons below are conditional unless the primary column says corroborated. Source facts are not rewritten by modeled closure.", "",
        "| Action / source ID | Availability bound | Last price session | Prior known stop | New/source stop | Setup before | Conditional progress % | Model-path status |",
        "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['type']} / {r['event_id']} | {r['decision_bound'] or 'UNRESOLVED'} | {r['last_available_session']} | {r['stop_known_before_alert']} | {r['source_action'].get('stop', r['latest_stop_in_source_sequence'])} | {r['source_setup_before']} | {fmt(current(r, 'progress_percent'))} | {r['conditional_path']['status']} |")
    lines += ["", "## Stop decisions", "", "| Event | Old → new | Tighten / widen | Source change % | Conditional adjustment ATR | Conditional old-stop clearance ATR | Toward pre-existing protective swing | Primary stop comparison |", "|---|---|---|---|---|---|---|---|"]
    for r in p["stop_revisions"]:
        c = r["conditional_stop_comparison"] or {}
        lines.append(f"| {r['event_id']} | {r['source_action']['previous_stop']} → {r['source_action']['stop']} | {r['stop_change']} | {fmt(r['source_stop_change_percent'])} | {fmt(c.get('adjustment_ATR'))} | {fmt(c.get('stop_clearance_ATR'))} | {c.get('moves_toward_preexisting_swing')} | {r['primary_stop_comparison_status']} |")
    if not p["stop_revisions"]:
        lines.append("| No reported revision | — | — | — | — | — | — | — |")
    for r in rows:
        if r["type"] == "SETUP_CHANGED":
            lines += ["", f"Underway transition: {r['conditional_path']['elapsed_eligible_sessions']} eligible sessions; progress {fmt(current(r, 'progress_percent'))}%, {fmt(current(r, 'progress_ATR'))} initial ATR, {fmt(current(r, 'progress_original_R'))} original hypothetical R. The transition is reported source evidence, not inferred from movement."]
    metrics = path["pre_exit_or_active_path"]
    lines += ["", "## Exit and exposure interpretation", "",
        f"Primary analytical path: {p['primary_path']['status']}. Conditional analytical path: {path['status']}."]
    if metrics:
        lines += ["", f"Complete-session conditional path through {metrics['last_session']}: MFE {fmt(metrics['mfe_percent'])}%, MAE {fmt(metrics['mae_percent'])}%, signed progress {fmt(metrics['progress_percent'])}%. Original-R progress {fmt(metrics['progress_original_R'])}. This is a pre-exit summary when the modeled episode has closed; it is not progress at the later source decision."]
    else:
        lines += ["", "No complete eligible active-session path can be measured. An exit-day candle is not used to invent held-position excursions."]
    if closure:
        ce = closure["conditional_exit_evidence"]
        lines += ["", f"SOURCE_REPORTED_DROPPED: {closure['closing_event_id']}. Actual cause: EXIT_REASON_UNRESOLVED.", "",
            f"Conditional stop evidence: {exit_description(ce['stop_touch'])}.", "",
            f"Conditional target evidence: {exit_description(ce['hypothetical_target_touch'])}.", "",
            f"Earlier nonprogress-window flags: {closure['earlier_nonprogress_flags_exist']}; terminal time-stop hypothesis: {closure['possible_time_stop']} ({closure['terminal_time_hypothesis_status']}). Earlier flags do not establish the cause of a later DROP or an expert rule."]
    else:
        lines += ["", "No source DROP is observed; the source history is right-censored. A modeled closure does not close the source ledger."]
    if symbol == "EBAY":
        lines += ["", "EBAY: the PR16 original 119.20 stop is crossed by the corroborated October 26 low 117.87 under its email-availability/session-scale assumptions. The later source revision to 117.50 remains an OPEN-source fact and cannot rescue the closed model. Progress at that revision is unavailable, and the October 26 exit-day Close/High/Low are excluded from held-exposure metrics. No re-entry or intraday revision is inferred."]
    lines += ["", "## Context and alternative explanations", "",
        "Moving averages, confirmed swings and breakout/pullback diagnostics are descriptive choices made by the coding agent. They are not attributed Grimes rules. Native-price context remains available after modeled closure as a market observation, without position-exposure attribution.", "",
        "| Event | Close/SMA10−1 | Close/SMA20−1 | Close/SMA50−1 | ATR14 | Stock/SPY20 | Stock/sector20 |",
        "|---|---|---|---|---|---|---|"]
    for r in rows:
        f = r["native_features"]
        if not f:
            continue
        proxy = r["sector_proxy"]["proxy"]
        rel = r["relative_strength"]
        lines.append(f"| {r['event_id']} | {fmt(f['close_sma10']['value'])} | {fmt(f['close_sma20']['value'])} | {fmt(f['close_sma50']['value'])} | {fmt(f['atr14']['value'])} | {fmt(rel['SPY']['20']['value'])} | {fmt(rel[proxy]['20']['value']) if proxy else 'UNAVAILABLE'} |")
    lines += ["", "Native price distances to both recent confirmed swings; these can be known by the decision even if newly confirmed in the latest completed bar. The protective-swing hypothesis above uses the stricter previous-session confirmation rule.", "",
        "| Event | Confirmed High | Close−High / ATR | Confirmed Low | Close−Low / ATR |", "|---|---|---|---|---|"]
    for r in rows:
        s = r.get("native_swing_distances")
        if s:
            lines.append(f"| {r['event_id']} | {s['high']['pivot']['price'] if s['high']['pivot'] else 'UNAVAILABLE'} | {fmt(s['high']['close_minus_level_ATR'])} | {s['low']['pivot']['price'] if s['low']['pivot'] else 'UNAVAILABLE'} | {fmt(s['low']['close_minus_level_ATR'])} |")
    lines += ["", "Compatible units, exact entries/revision/exit clocks, intraday sequencing and independent setup annotations would be needed to distinguish competing management explanations. TEVA/ASST/SNDK identity caveats and earnings/publication incompleteness remain as recorded in PR16.", ""]
    return "\n".join(lines)


def markdown(data):
    ls = data["long_short.json"]
    rel = {r["id"]: r for r in data["relationships.json"]}
    lines = ["# Grimes trade management and decision analysis", "", "## Executive summary", "",
        "This discovery study includes all 26 source positions and 72 actions across seven October 18–26, 2026 alerts: 26 openings, 27 stop revisions, seven underway transitions and 12 source closures; 14 source positions remain right-censored. PLTR/PEP stay excluded. Actual fills, size, realized P&L and discretionary intent remain unknown.", "",
        f"The clearest source-only difference is stop direction: LONG widening {proportion(ls['LONG']['source_widening_revision_rate'])} versus SHORT widening {proportion(ls['SHORT']['source_widening_revision_rate'])}. This describes this alert sample, not a fitted or verified management algorithm.", "",
        f"Among conditional, still-active observations, tightening follows positive signed price progress in {proportion(rel['tightening_after_favorable_progress']['support_rate'])}; underway follows positive progress in {proportion(rel['underway_after_favorable_progress']['support_rate'])}. Unusable/post-exit observations remain in the tables. Co-publication and sector overlap prevent treating these decisions as independent evidence.", "",
        "Counterexamples to tightening-only-after-favorable-progress: "+references(rel["tightening_after_favorable_progress"]["counterexamples"])+". Favorable-progress widening observations: "+references(rel["widening_after_favorable_progress"]["support"])+". These are hypothetical reference-price comparisons, not realized trade profits.", "",
        "EBAY preserves the PR16 source/model contradiction: source remains OPEN with the 119.20→117.50 revision; the original modeled episode has already stopped under the inherited timing/scale assumptions. Its later decision has no current held-position progress. No model outcome identifies an actual source closure cause.", "",
        "## Stop management", "",
        "Source change percentages do not require native-bar compatibility. Price, ATR and original-R comparisons do; the full table is conditional, with primary corroboration recorded separately. New stops are reported outcomes, not pre-publication features. Pre-alert stops exclude all changes first published in the same alert.", "",
        "| Symbol / event | Direction / setup | Old → new | Change | Source % | Conditional ΔATR | Conditional progress % | Conditional MFE / MAE % | Conditional old-stop clearance ATR | Model-path status |",
        "|---|---|---|---|---|---|---|---|---|---|"]
    for r in data["stop_revisions.json"]:
        c = r["conditional_stop_comparison"] or {}
        lines.append(f"| {r['symbol']} / {r['event_id']} | {r['direction']} / {r['source_setup_before']} | {r['source_action']['previous_stop']} → {r['source_action']['stop']} | {r['stop_change']} | {fmt(r['source_stop_change_percent'])} | {fmt(c.get('adjustment_ATR'))} | {fmt(current(r, 'progress_percent'))} | {fmt(current(r, 'mfe_percent'))} / {fmt(current(r, 'mae_percent'))} | {fmt(c.get('stop_clearance_ATR'))} | {r['conditional_path']['status']} |")
    lines += ["", "| Revision kind | Source events | Current conditional progress median[min,max] | Old-stop clearance ATR median[min,max] | SPY vol20 median[min,max] | Distinct alert bounds | Setup counts |",
        "|---|---|---|---|---|---|---|"]
    for k, c in data["stop_comparison.json"].items():
        lines.append(f"| {k} | {c['events']} | {dist(c['current_progress_percent'])} | {dist(c['clearance_ATR'])} | {dist(c['SPY_volatility20'])} | {c['unique_publication_bounds']} | {c['setup_counts']} |")
    for item in data["relationships.json"][:4]:
        lines += ["", f"**{item['hypothesis']}** Supporting fraction: {proportion(item['support_rate'])}; total source events {item['total_events']}.", "",
            f"Supporting observations: {references(item['support'])}.", "", f"Counterexamples: {references(item['counterexamples'])}.", "",
            "Unavailable: "+(", ".join(f"{r['symbol']} ({r['event_id']})" for r in item["unusable"]) or "None")+".", "",
            f"Confounders: {item['confounders']}. Needed: {item['additional_validation_data']}."]
    lines += ["", "## Underway transitions", "",
        "The seven transitions are source facts. Progress does not create a transition. Current progress is unavailable when the model was already closed or its exit path became ambiguous; a separately retained pre-exit summary must not substitute for progress at the transition.", "",
        "| Symbol / event | H sessions | Conditional progress % / ATR / original R | Conditional MFE / MAE % | Initial / latest source stop | Model-path status |",
        "|---|---|---|---|---|---|"]
    for r in data["underway_transitions.json"]:
        lines.append(f"| {r['symbol']} / {r['event_id']} | {r['conditional_path']['elapsed_eligible_sessions']} | {fmt(current(r, 'progress_percent'))} / {fmt(current(r, 'progress_ATR'))} / {fmt(current(r, 'progress_original_R'))} | {fmt(current(r, 'mfe_percent'))} / {fmt(current(r, 'mae_percent'))} | {r['initial_stop']} / {r['latest_stop_in_source_sequence']} | {r['conditional_path']['status']} |")
    grouped = data["grouped_oct22_transitions.json"]
    lines += ["", "AAOI/AMD/ANET/SNDK share one October 22 publication opportunity and the fixed XLK context proxy. Their eligible-session horizons are "+str(grouped["elapsed_sessions"])+". Their common market snapshot is one observation, not four independent confirmations.", "",
        "| Grouped conditional measurement | Median[min,max], usable/4 |", "|---|---|"]
    for k, d in grouped["current_progress"].items():
        lines.append(f"| {k} | {dist(d)} |")
    lines += ["", "Existing native-price geometry and 20-session relative strength (fractions, not target returns):", "",
        "| Transition | Breakout20 | Breakdown20 | Close/SMA10−1 | Close/SMA20−1 | Close/SMA50−1 | Stock/SPY20 | Stock/QQQ20 | Stock/RSP20 | Stock/IWM20 | Stock/sector20 |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in data["underway_transitions.json"]:
        f = r["native_features"] or {}
        value = lambda key: f.get(key, {}).get("value")
        rs = r.get("relative_strength", {})
        p = r.get("sector_proxy", {}).get("proxy")
        relative = lambda proxy: rs.get(proxy, {}).get("20", {}).get("value")
        lines.append(f"| {r['symbol']} | {value('breakout20')} | {value('breakdown20')} | {fmt(value('close_sma10'))} | {fmt(value('close_sma20'))} | {fmt(value('close_sma50'))} | "+" | ".join(fmt(relative(proxy)) for proxy in ("SPY", "QQQ", "RSP", "IWM", p))+" |")
    lines += ["", "| October22 quartet | Breakdown20 | Close/SMA20−1 | Close/SMA50−1 | Range10/prior20 |", "|---|---|---|---|---|"]
    for r in grouped["native_geometry"]:
        lines.append(f"| {r['symbol']} | {r['breakdown20']} | {fmt(r['close_sma20'])} | {fmt(r['close_sma50'])} | {fmt(r['range_contraction10_previous20'])} |")
    lines += ["", "Matched ENTERABLE controls use the same elapsed eligible-session horizon at a source alert opportunity no later than the target transition. All co-published actions are included when checking source state. Later final outcomes do not select controls. Controls with closed/ambiguous conditional model episodes are retained as exclusions. Shared controls and different dates/directions/sectors confound comparison.", "",
        "| Transition | H | Conditional target progress % | Usable / candidate peers | Favorable controls / usable | Control median[min,max] progress % |",
        "|---|---|---|---|---|---|"]
    for c in data["matched_enterable_controls.json"]:
        target = c["target_progress"]
        lines.append(f"| {c['symbol']} | {c['horizon_sessions']} | {fmt(target['progress_percent'] if target else None)} | {c['usable_controls']} / {c['candidate_count']} | {proportion(c['favorable_control_rate'])} | {dist(c['control_progress_percent'])} |")
    positive_peers = {}
    for c in data["matched_enterable_controls.json"]:
        for p in c["controls"]:
            if p["status"] == "ELIGIBLE_CONDITIONAL_COMPARATOR" and p["features"]["current_progress"]["progress_percent"] > 0:
                positive_peers[(p["trade_id"], p["matched_bound"])] = p
    lines += ["", "Favorable movement is not sufficient to assign UNDERWAY. Still-ENTERABLE positive-progress counterexamples at matched horizons: "+(
        "; ".join(f"{p['symbol']} at {p['matched_bound']}, {fmt(p['features']['current_progress']['progress_percent'])}%" for p in positive_peers.values()) or "None among usable controls")+". Shared peers are listed once here; their repetition across transition comparisons is not additional independent evidence."]
    item = rel["underway_after_favorable_progress"]
    lines += ["", f"Favorable-progress evidence: {proportion(item['support_rate'])}. Support: {references(item['support'])}. Counterexamples: {references(item['counterexamples'])}. Unavailable: "+", ".join(r["symbol"] for r in item["unusable"])+".", "",
        "Completion of an entry setup or deterioration for new entrants cannot be established from movement alone. The existing breakout/pullback and confirmed-swing diagnostics are retained as competing geometry measurements, not expert setup labels.", "",
        "## Exit interpretation", "",
        "All 12 DROPs confirm source closure; the actual cause is EXIT_REASON_UNRESOLVED in every case. Stop, target and time hypotheses are nonexclusive price-based explanations. A LONG +1R touch removes at least one-third under the inherited convention and cannot establish a full exit. Intraday stop/target collisions preserve unknown order. Exit-day OHLC are excluded from exposure MFE/MAE; source closure-day candles are included only when fully available before the closure bound.", "",
        "| Source DROP | Direction | Availability-bound sessions / publication range | Primary stop observation | Conditional stop observation | Conditional +1R observation | Earlier nonprogress flag / terminal time hypothesis |",
        "|---|---|---|---|---|---|---|"]
    for c in data["closure_hypotheses.json"]:
        d = c["duration"]
        lines.append(f"| {c['symbol']} / {c['closing_event_id']} | {c['direction']} | {d['email_bound_scenario_eligible_sessions']} / {d['publication_based_session_range'] or 'UNKNOWN; bracket '+str(d['conditional_ordered_publication_bracket_sessions'])} | {exit_description(c['primary_exit_evidence']['stop_touch'])} | {exit_description(c['conditional_exit_evidence']['stop_touch'])} | {exit_description(c['conditional_exit_evidence']['hypothetical_target_touch'])} | {c['earlier_nonprogress_flags_exist']} / {c['possible_time_stop']} |")
    lines += ["", "| Source closure | Initial / latest source stop | Stop revisions | Source setup | Last complete active-path session | Conditional pre-exit MFE / MAE % |", "|---|---|---|---|---|---|"]
    for c in data["closure_hypotheses.json"]:
        path = c["conditional_path"]["pre_exit_or_active_path"]
        lines.append(f"| {c['symbol']} | {c['initial_stop']} / {c['latest_stop_in_source_sequence']} | {len(c['stop_revision_ids'])} | {c['source_setup_before']} | {path['last_session'] if path else 'UNAVAILABLE'} | {fmt(path['mfe_percent'] if path else None)} / {fmt(path['mae_percent'] if path else None)} |")
    lines += ["", "An earlier 2/3/5-session flag is not a terminal time-exit explanation when the model has already closed or its exit path is ambiguous. In those cases terminal exposure is unavailable, rather than assumed to continue until the source DROP."]
    lines += ["", "Actual holding duration is unknown without fills. Publication-based session ranges describe source reporting intervals; where weekly publication is unresolved, the separate ordered-publication/email bracket is explicitly conditional. Fourteen not-dropped histories are right-censored, and the four final additions lack an eligible completed modeled entry before cutoff.", "",
        "## Long versus short behavior", "", "| Source direction | Positions | Tightening revisions | Widening revisions | Positions widened | Underway | Source closed |",
        "|---|---|---|---|---|---|---|"]
    for direction, c in ls.items():
        lines.append(f"| {direction} | {c['positions']} | {proportion(c['source_tightening_revision_rate'])} | {proportion(c['source_widening_revision_rate'])} | {proportion(c['positions_with_widening'])} | {proportion(c['underway_rate'])} | {proportion(c['reported_closure_rate'])} |")
    lines += ["", "| Direction | Availability-bound eligible duration | Conditional pre-exit MFE % | Conditional pre-exit MAE % | Conditional pre-exit original-R progress |", "|---|---|---|---|---|"]
    for direction, c in ls.items():
        d = c["conditional_pre_exit_path_distributions"]
        lines.append(f"| {direction} | {dist(c['email_bound_scenario_duration_sessions'])} | {dist(d['mfe_percent'])} | {dist(d['mae_percent'])} | {dist(d['progress_original_R'])} |")
    lines += ["", "Duration mixes censored reporting histories and chosen availability bounds; it is not estimated mean holding time. Excursion distributions omit unavailable/ambiguous exit-day exposure but retain the full source-position denominator. None is realized trade performance.", "",
        "## Market context", "",
        "Original commentary, native-price measurements and interpretation are separate. Sector and style exposure, overlapping positions and common alert publication are confounders. RSP/SPY is a participation proxy; true market breadth is unavailable. No stale ES observations are used.", "",
        "| Bound / session | Source commentary synopsis | Decision counts | SPY daily / 5d / 20d / 60d % | QQQ daily % | SPY volatility expansion |",
        "|---|---|---|---|---|---|"]
    synopses = {s["alert_id"]: s for s in data["commentary_synopses.json"]}
    for m in data["market_context.json"]:
        synopsis = " / ".join(synopses[a]["synopsis"] for a in m["alert_ids"])
        f = m["market_observed"]["SPY"]
        returns = " / ".join(fmt(f[k]["value"], fraction=True) for k in ("daily_return", "return_5d", "return_20d", "return_60d"))
        lines.append(f"| {m['decision_bound']} / {m['last_available_session']} | {synopsis} | {m['decision_counts']} | {returns} | {fmt(m['market_observed']['QQQ']['daily_return']['value'], fraction=True)} | {m['agent_descriptive_labels']['SPY_volatility_expansion']} |")
    lines += ["", "| Decision type | Events | Usable context | Distinct alert bounds | SPY negative day | Positive day, negative 5d | SPY vol20 expansion |", "|---|---|---|---|---|---|---|"]
    for kind, c in data["market_decision_clusters.json"].items():
        lines.append(f"| {kind} | {c['source_events']} | {c['market_context_usable']} | {c['distinct_alert_bounds']} | {proportion(c['SPY_negative_day'])} | {proportion(c['positive_day_negative_5d'])} | {proportion(c['SPY_volatility_expansion'])} |")
    lines += ["", "All four ETF return/trend/volatility vectors, participation ratios, stock-to-market/sector strength and event links are retained in market_context.json and decision_features.json. Coincidence with a weak day, rebound proxy or volatility increase does not establish why a source action occurred.", "",
        "## Limitations", "",
        "The sample is 26 selected source positions in seven alerts, not an unselected opportunity universe. There are no actual entries, fills or sizes; stop/native-unit compatibility remains extensively unverified; missing intraday sequencing censors exposure; model-survival and source publication opportunities select usable comparisons. Four co-published technology transitions and repeated market snapshots are dependent observations. TEVA has limited history under its new ordinary-share contract; ASST has business/split and sector uncertainty; SNDK is its current separated identity. PR16's weekly publication remains unresolved, with the same separate email-availability assumption. Earnings/action completeness is unknown. No parameter fitting, significance, causal claim, predictive model, realized P&L or statistical-edge conclusion is justified.", "",
        "## Next research hypotheses", "",
        "Ranked by strength of evidence and practical relevance; test on a separate, independently selected historical alert sample with the same predeclared definitions:", "",
        f"1. **Direction and widening:** LONG revisions have a higher widening fraction than SHORT revisions. Discovery evidence is source-only: {proportion(ls['LONG']['source_widening_revision_rate'])} versus {proportion(ls['SHORT']['source_widening_revision_rate'])}. Test the sign of that difference across independent periods, reporting both revision and unique-position/alert denominators. This could identify management asymmetry; source selection and clustered shorts are confounders.", "",
        f"2. **Underway after favorable movement:** signed pre-transition progress is positive more often, or has a higher median, than at equivalent ENTERABLE opportunities. Discovery support {proportion(rel['underway_after_favorable_progress']['support_rate'])}; matched control tables retain exceptions and unavailable cases. Exact entries, publication clocks and compatible units are needed. Shared technology/context exposure is a competing explanation.", "",
        f"3. **Widening near the previous stop:** widening opportunities more often have absolute Close-to-old-stop distance <=1 ATR than matched unchanged/tightening opportunities. Discovery support among widening events is {proportion(rel['widening_near_previous_stop']['support_rate'])}. Keep one ATR fixed; do not tune it to these 26 positions. Stop-scale validation, intraday clocks and an independent no-change opportunity sample are required; observed proximity alone cannot establish causation.", "",
        "## Complete sample and individual summaries", "", "| Stock | Direction | Source final | Setup | Source event count | Conditional path status |", "|---|---|---|---|---|---|"]
    for p in data["positions.json"]:
        lines.append(f"| [{p['symbol']}](summary-{p['symbol']}.md) | {p['direction']} | {p['source_position_state']} | {p['source_setup']} | {len(p['event_ids'])} | {p['conditional_path']['status']} |")
    lines += ["", "## Measurement definitions and provenance", ""]
    for key, definition in data["methodology.json"].items():
        lines.append(f"- **{key}:** {definition}.")
    manifest = data["manifest.json"]
    lines += ["", f"Authoritative PR16 bundle: `{manifest['parent_bundle_sha256']}`. Inspected merged main: `{manifest['inspected_main_commit']}`; PR16 head: `{manifest['inspected_pr16_commit']}`. Original subscriber content and raw provider frames remain in the embedded local parent. Public reports contain derived facts and paraphrased commentary, not full subscriber originals.", ""]
    return "\n".join(lines)
