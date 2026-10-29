"""Deterministic PR9B findings; evidence verdicts concern explanations, not fills."""
import json
import re
from datetime import datetime
from zoneinfo import ZoneInfo

EXPLANATIONS = {
 'CLMT': [
  {'hypothesis': 'Closing confirmation, no mandatory full +1R exit', 'support': 'October19 Low53.83 breached55.25 but Close55.54 recovered; October20 Low54.33 stayed above revised53.40.', 'contradiction': 'October21 Close52.59 breached53.02 before evening DROP; closure cause remains unobserved.', 'missing': 'Actual entry, stop convention and execution record.', 'verdict': 'SUPPORTED', 'scope': 'Conditional compatibility of continued stop management; not actual policy identification.'},
  {'hypothesis': 'One late post-breach entry under an intraday hard stop', 'support': 'Daily Close recovered; a positive-risk protected entry after the last55.25 visit is possible.', 'contradiction': 'The last touching five-minute bar starts15:55ET; no complete protected bar remains. Existing H4 at55.781 still conflicts.', 'missing': 'Within-final-bar path and fill time; source does not report this entry.', 'verdict': 'PLAUSIBLE', 'scope': 'Existential timing explanation, not an executable identified fill.'},
  {'hypothesis': 'Pending plan activated after completed reclaim, at next Open', 'support': 'Fixed reclaim rule observes Monday Close, then activates Tuesday Open56.20 against known53.40.', 'contradiction': 'Monday stop revision precedes activation; Wednesday stop-out precedes source DROP. Source ADDED is not proof of a pending plan.', 'missing': 'Whether ENTERABLE carried an actual position and activation instruction.', 'verdict': 'NOT_IDENTIFIABLE', 'scope': 'Requires intended-plan interpretation and leaves DROP attribution unresolved.'}],
 'TEVA': [
  {'hypothesis': 'Closing confirmation, no mandatory full +1R exit', 'support': 'October21 Open40.10 and Low39.50 breached40.40 but Close40.62 recovered. Later Lows39.58 and39.10 exceeded the known revised stops39.35 and39.05.', 'contradiction': 'None in observed later source constraints; this does not establish the actual convention.', 'missing': 'Actual position/order record; weekly publication time.', 'verdict': 'SUPPORTED', 'scope': 'Conditional price/source compatibility only.'},
  {'hypothesis': 'One entry after the Wednesday gap-and-reclaim', 'support': 'Last40.40 touching bar starts15:10ET; nine complete later bars span40.44–40.62 and remain protected. Later daily Lows respect revised stops.', 'contradiction': 'No fill report establishes that the trade waited until Wednesday.', 'missing': 'Execution time, executable quotes and treatment of earlier ENTERABLE status.', 'verdict': 'PLAUSIBLE', 'scope': 'Market permits a delayed single entry; the source does not identify one.'},
  {'hypothesis': 'Pending reclaim plan, activated Thursday Open', 'support': 'Fixed reclaim then next-Open rule enters October22 at40.20 after Wednesday stop39.35 was available.', 'contradiction': 'October21 stop revision occurs before activation, so it is not compatible evidence of an already-held position.', 'missing': 'Whether the stop revision managed a pending instruction or actual exposure.', 'verdict': 'NOT_IDENTIFIABLE', 'scope': 'Causal trigger but extra semantic assumption.'}],
 'GME': [
  {'hypothesis': 'Closing confirmation, no mandatory full +1R exit', 'support': 'Thursday Close25.39 exceeded25.01; Friday Close24.82 exceeded24.78 even under the late weekly clock.', 'contradiction': 'Monday Close23.90 breached24.40 before evening DROP, leaving closure attribution unresolved.', 'missing': 'Actual closing instruction, entry and DROP execution.', 'verdict': 'SUPPORTED', 'scope': 'Explains continued revisions under all three clocks, not the actual exit cause.'},
  {'hypothesis': 'One Thursday entry after last old-stop visit', 'support': 'Five complete protected bars after15:30ET span25.05–25.38; early weekly24.40 then protects Friday Low24.68.', 'contradiction': 'Late or Friday-Close weekly clocks leave24.78 active during Friday Low24.68, stopping that same position before continued management.', 'missing': 'Weekly publication clock, fill and intrabar order.', 'verdict': 'PLAUSIBLE', 'scope': 'Survives only the early weekly clock; contradicted for late/Friday-Close clocks.'},
  {'hypothesis': 'Pending plan after two protective Closes, next-Open activation', 'support': 'Thursday and Friday close above stops already known at their Opens; fixed rule activates Monday Open24.82 against24.40.', 'contradiction': 'Thursday and weekly stop revisions precede activation; Monday hard stop triggers before DROP. This explains no earlier held exposure.', 'missing': 'Plan activation evidence and source DROP cause.', 'verdict': 'NOT_IDENTIFIABLE', 'scope': 'Availability-respecting delayed entry; source remains OPEN from original ADD.'}],
 'EBAY': [
  {'hypothesis': 'Unconditional next-session exit after a closing violation', 'support': 'Monday Close118.62 breaches119.20; queued Tuesday exit is outside fixed cutoff, permitting Monday evening source OPEN.', 'contradiction': 'No next-session execution is observed; later117.50 revision cannot cancel this queued exit under the tested rule.', 'missing': 'October27 fill and next source alert; evidence here ends October26.', 'verdict': 'PLAUSIBLE', 'scope': 'Right-censored commitment, not demonstrated survival after the next Open.'},
  {'hypothesis': 'ENTERABLE pending plan with no entry yet', 'support': 'Source never reports UNDERWAY; an unfilled plan could receive an evening stop revision.', 'contradiction': 'Source says ADDED and remains OPEN. Neither tested fixed delayed rule activates EBAY; absence of a trigger is not evidence of no actual trade.', 'missing': 'Actual fill/activation instruction and meaning of ENTERABLE in this episode.', 'verdict': 'NOT_IDENTIFIABLE', 'scope': 'Competing explanation; never replaces source status.'},
  {'hypothesis': 'Bounded discretionary next-Open review', 'support': 'Existing PR19 CLOSE_REVIEW_NEXT_OPEN retains exposure through the Monday evening revision.', 'contradiction': 'Requires ignoring intraday/closing stop breaches; flexibility improves fit without identifying practice.', 'missing': 'Actual review policy, execution and following Open.', 'verdict': 'NOT_IDENTIFIABLE', 'scope': 'Fixed cost2 exploratory rule, no per-trade override or unlimited discretion.'}],
 'CDE': [
  {'hypothesis': 'Hold with reported protective stops', 'support': 'After next-Open short15.46, daily Highs remain below the stop known at each Open; source later reports UNDERWAY and OPEN.', 'contradiction': 'No protective-stop contradiction in retained path.', 'missing': 'Actual fill, size and stop order type.', 'verdict': 'SUPPORTED', 'scope': 'Compatible conditional hard-stop explanation.'},
  {'hypothesis': 'Partial +1R realization with protected residual runner', 'support': 'First target14.52 is reached October22; residual remains protected and compatible with continued source management.', 'contradiction': 'The illustrative50% fraction is not observed.', 'missing': 'Any sizing or partial-fill evidence.', 'verdict': 'PLAUSIBLE', 'scope': 'Observationally equivalent source-status explanation to holding.'},
  {'hypothesis': 'Mandatory full exit at +1R', 'support': 'The hypothetical next-Open entry reaches+1R.', 'contradiction': 'Full exit before the October22 UNDERWAY/stop cluster conflicts with later weekly management and final OPEN.', 'missing': 'An alternative actual entry could change initialR; none is established.', 'verdict': 'CONTRADICTED', 'scope': 'Fixed-entry target convention, not evidence against hard protective stops.'}]
}


def baseline(episode):
    return next(c for c in episode['clocks'] if c['clock_variant'] == 'LATE_EMAIL_BOUND')


def number(v):
    if v is None:
        return 'UNAVAILABLE'
    if isinstance(v, float):
        return f'{v:.6f}'.rstrip('0').rstrip('.')
    if isinstance(v, dict):
        return f"{v['price']} ({v['session_date']}; confirmed {v['confirmed_session']})"
    return str(v)


def table(headers, rows):
    return ['| '+' | '.join(headers)+' |', '| '+' | '.join('---' for _ in headers)+' |'] + [
        '| '+' | '.join(str(v).replace('|', '/') for v in r)+' |' for r in rows]


def readable(text):
    # Space numerical quantities in narrative templates without touching URLs,
    # inline code, identifiers such as H1/ATR14, or immutable values in JSON.
    parts = re.split(r'(`[^`]*`|https?://[^\s)]+)', text)
    words = ('all All including and those the The among from to in has fits cost comprise across '
             'are is of before after stop Close Low High Open above below at with short '
             'October September Monday Tuesday Wednesday Thursday Friday known revised only contains '
             'span level original and first each final through remaining port Costs versus')
    pattern = r'\b('+ '|'.join(words.split()) +r')(?=\d)'
    for i in range(0, len(parts), 2):
        parts[i] = re.sub(pattern, r'\1 ', parts[i])
        parts[i] = re.sub(r'(?<=\d)(minutes|member|ET)\b', r' \1', parts[i])
        parts[i] = parts[i].replace('5m55.57', '5m 55.57').replace('are(0', 'are (0').replace('],(', '], (')
    return ''.join(parts)


def public_comparison(result):
    """Compact projection; retain source facts and all scenario outcomes, no raw subscriber bodies."""
    out = {k: v for k, v in result.items() if k != 'episodes'}
    out['episodes'] = []
    for e in result['episodes']:
        row = {k: v for k, v in e.items() if k not in {'clocks', 'market_identity'}}
        row['market_identity'] = {k: e['market_identity'][k] for k in
            ('contract', 'source_bundle_sha256', 'origin', 'price_basis', 'volume_basis', 'corporate_action_completeness')}
        row['clocks'] = []
        for c in e['clocks']:
            cc = {k: v for k, v in c.items() if k != 'original_candidates'}
            cc['original_candidates'] = []
            for p in c['original_candidates']:
                q = {k: p.get(k) for k in ('hypothesis', 'status', 'entry_session', 'entry_price', 'entry_kind',
                    'entry_at', 'reported_stop_at_entry', 'geometry', 'rationale')}
                q['management'] = [{k: s.get(k) for k in ('policy', 'rank_eligible', 'evaluation_vector',
                    'terminal_possibilities', 'conflict_alert_clusters', 'observations')} for s in p['management']]
                cc['original_candidates'].append(q)
            row['clocks'].append(cc)
        out['episodes'].append(row)
    return out


def four_report(result):
    lines = ['# Grimes four-trade forensics — PR9B', '',
        'CLMT, TEVA and GME admit a simpler closing-confirmation explanation for their continued source management. '
        'EBAY does not: its Close was below the old stop before the evening revision. '
        'These are conditional explanations, not identification of Grimes’ fills or stop orders. '
        'CDE is a target-exit convention conflict, distinct from a protective-stop conflict.', '',
        'SOURCE is the unchanged expert ledger. MARKET is retained IBKR TRADES/RTH evidence. '
        'HYPOTHESIS is an explicitly assumed entry or management convention. INFERENCE compares them. '
        'All four cases remain source ENTERABLE throughout; only control CDE transitions UNDERWAY. '
        'The weekly alert’s publication remains **UNKNOWN**; no calendar date is inferred from its display. '
        'Late-email-bound, early-before-Friday-Open and Friday-Close clocks are conditional schedules, not three observations.', '',
        '## Evidence and conventions', '',
        'Base main: `8be6c8ec10b98870c273964ac5dbaa7a6757e9d6`; merged PR19 head: '
        '`71877971466621382129f864fa39952c17ce1a7d`. '
        f"Pinned PR19 sensitivity parent: `{result['parent_sha256']}`. Analysis cutoff: `{result['cutoff']}`. "
        'No later bars are used to explain earlier decisions. Actual prices, quantities, orders, realized P&L and fees remain unknown.', '',
        'Native daily prices retain the inherited split-adjusted declaration and conditional nominal-stop comparison. '
        'Native volume units are unverified, so the V column is not asserted to be shares. No arbitrary rescaling, '
        'Yahoo replacement or historical identity splice is applied. Source hashes and qualified conIds are in '
        '[forensic_comparison.json](../evidence/pr9b-forensics-v1/forensic_comparison.json). '
        'PR19’s embedded native proofs supply the admitted daily IBKR case evidence. The separate local request-manifest inventory '
        'found no case Yahoo or five-minute request; it does not unpack native requests embedded inside source-proof JSON. '
        'The scope is repository runs/data, not all disks or all possible existing datasets.', '',
        'New requests used the existing pinned ib_async==2.1.0 low-level backend, a confirmed read-only local TWS on port7496, '
        'and exactly four RTH five-minute windows. No account, position, execution or order queries were made. '
        'Raw native returns and timestamps are retained in a new local immutable bundle; derived diagnostics are versioned here.', '',
        '## Focused intraday evidence', '']
    lines += table(['Instrument/session', 'Stop', 'First/last touching bar (ET)', 'Complete protected bars after last touch', 'Protected tail range', 'Daily / final5m Close'], [
        [w['symbol']+' '+w['session'], w.get('comparison_stop'),
         ' / '.join(datetime.fromisoformat(w[k]).astimezone(ZoneInfo('America/New_York')).strftime('%H:%M') for k in ('first_touch_bar','last_touch_bar')) if w.get('last_touch_bar') else w['status'],
         w.get('full_protected_bars_after_last_touch'), w.get('protected_tail_price_range'),
         str(w.get('frozen_daily',{}).get('close'))+' / '+str(w.get('aggregate',{}).get('close'))] for w in result['intraday']])
    lines += ['', 'Each successful window contains78 consecutive five-minute bar starts from09:30 through15:55ET. '
        'A touching bar locates a possible breach within its five minutes; it does not reveal the last-touch second, '
        'quotes, liquidity or an actual entry. CLMT daily Close55.54 versus final5m55.57, GME Thursday25.39 versus25.37, '
        'and GME Friday24.82 versus24.83 are retained as differences, not reconciled away. '
        'All remain on the same side of the relevant stop. TEVA’s Closes agree at40.62.', '',
        'Including the final touching bar, five-minute Highs tighten the daily post-last-touch price outer bounds to '
        '**(55.25,55.61]** for CLMT, **(40.40,40.62]** for TEVA, **(25.01,25.38]** for Thursday GME and '
        '**(24.78,24.90]** for Friday GME. The lower stop endpoint is excluded. The corresponding positive per-share '
        'risk outer bounds are(0,0.36],(0,0.22],(0,0.37] and(0,0.12], using the stop known before each entry. '
        'These are bounds on possibilities, not executable quotes: the touching bar’s High might precede its last stop visit.', '',
        '## Fixed tests and interpretation', '',
        'The original four entry hypotheses and four management policies remain unchanged. '
        'Two additional diagnostic exposure bounds hold H1’s entry fixed: CLOSE_CONFIRMATION exits at the first violating Close '
        '(an idealized boundary, not a guaranteed executable fill); NEXT_OPEN_AFTER_CLOSE commits unconditionally to the following Open. '
        'A new evening stop cannot cancel that commitment. Costs0/1/2 for hard/Close/next-Open and cost2 for the existing review '
        'are explicit ordinal extra-convention counts, not fitted likelihoods or probabilities.', '',
        'Two fixed delayed-entry rules are tested across all26 episodes within the first three eligible completed sessions: '
        '(D1) a touch of the stop known at Open followed by a protective Close; (D2) two consecutive protective Closes. '
        'A trigger becomes available only after Close+60minutes, then activates at the next eligible Open with positive risk '
        'against the stop known then. No same-Close fill, favorable hindsight price, re-entry or restart after failure is invented. '
        'D1 is a concrete stop-defined pullback/reclaim; D2 is a stop-defined recovery confirmation. '
        'Original H3/H4 supply pre-known breakout/pivot/MA alternatives. These diagnostics were defined by this repository analysis, '
        'not reported by Grimes. Pre-activation source actions stay unresolved; UNDERWAY before activation is an explicit counterexample.', '']
    for symbol in ('CLMT', 'TEVA', 'GME', 'EBAY', 'CDE'):
        e = next(e for e in result['episodes'] if e['symbol'] == symbol)
        c = baseline(e)
        source = e['source']
        lines += [f'## {symbol}', '',
            f"**SOURCE:** `{symbol} added {source['direction'].lower()} with stop {source['initial_stop']}`. "
            f"Final reported state: **{source['direction']} / {source['position_state']} / {source['setup_availability']}**, "
            f"latest stop **{source['current_stop']}**. Qualified conId `{e['market_identity']['contract']['conId']}` "
            f"on {e['market_identity']['contract']['primaryExchange']}, SMART/USD/STK.", '',
            '### Chronology', '']
        lines += table(['Label', 'Publication (ET) / session', 'Observation'], [
            ['SOURCE', ev['published_at'] or 'UNKNOWN', ev['type'] + ((' '+str(ev['previous_stop'])+' → '+str(ev['stop'])) if ev['type']=='STOP_CHANGED' else (' stop '+str(ev['stop']) if 'stop' in ev else ''))+
             '; '+ev['setup_after']+'; '+ev['event_id']] for ev in source['events']])
        lines += ['', '**MARKET:** daily OHLCV surrounding the source decisions. Prices after source DROP remain contextual observations, not continued exposure.', '']
        lines += table(['Session', 'Open', 'High', 'Low', 'Close', 'Native V'], [[r['session_date']]+[r[k] for k in ('open','high','low','close','volume')] for r in e['market_window']])
        lines += ['', '**MARKET:** indicators available strictly before each assumed action clock under the late-email-bound schedule. '
            'Pivots show price, pivot date and later confirmation date; unavailable TEVA warmup remains unavailable. '
            'All clocks and feature-status reasons are retained in JSON.', '']
        lines += table(['Event', 'Available session', 'ATR14', 'SMA20', 'SMA50', 'Swing high', 'Swing low', 'SPY/QQQ20-session return'], [
            [d['event_id'], d['available_feature_session']]+[number(d['features'][k]['value']) for k in ('atr14','sma20','sma50','confirmed_swing_high','confirmed_swing_low')]+[
                number(d['SPY_return20'])+' / '+number(d['QQQ_return20'])] for d in c['source_decisions']])
        lines += ['', '**HYPOTHESIS:** unchanged PR19 candidate entries and source-conflict clusters (final OPEN is a separate constraint).', '']
        lines += table(['Entry hypothesis', 'Status / session / price', 'Full1R; partial1R; hold; review conflict clusters'], [
            [p['hypothesis'],p['status']+' / '+str(p.get('entry_session'))+' / '+str(p.get('entry_price')),
             '; '.join('/'.join(s.get('conflict_alert_clusters', [])) or 'none' if s.get('rank_eligible') else 'unobserved' for s in p['management'])]
            for p in c['original_candidates']])
        lines += ['', '**HYPOTHESIS:** stop application at the unchanged next-Open entry.', '']
        h1 = next(p for p in c['original_candidates'] if p['hypothesis'] == 'H1_NEXT_OPEN')
        sign = 1 if source['direction'] == 'LONG' else -1
        risk = h1['geometry']['reference_risk']
        first_touch = next((r for r in c['counterfactual_daily_stop_scan'] if r['range_breach']), None)
        lines += [f"H1 entry {number(h1['entry_price'])}; stop known at activation {number(h1['reported_stop_at_entry'])}; "
            f"fixed reference risk {number(risk)} per share ({number(h1['geometry']['reference_risk_ATR'])} pre-entry ATR); "
            f"+1R reference {number(h1['entry_price']+sign*risk)}. "
            + (f"First counterfactual protective breach: {first_touch['session']} against {number(first_touch['known_stop_at_open'])}, "
               f"Open {first_touch['ohlcv']['open']}, Low {first_touch['ohlcv']['low']}, High {first_touch['ohlcv']['high']}, "
               f"Close {first_touch['ohlcv']['close']}." if first_touch else 'No protective-stop breach in the retained exposure window.'), '']
        lines += table(['Convention', 'Source compatibility', 'First Close violation', 'Exposure end bound / pending'], [
            [p['policy'],p['assessment']['category'],p.get('first_close_violation','see original paths'),
             str(p.get('exposure_end_bound','see original paths'))+' / '+str(p.get('committed_exit_pending','n/a'))] for p in c['stop_diagnostics']])
        lines += ['', '**HYPOTHESIS:** availability-respecting delayed entries.', '']
        lines += table(['Fixed rule', 'Trigger / next-Open entry', 'Whole history / after activation', 'Earlier source actions'], [
            [p['hypothesis'],p['status']+' / '+str(p.get('trigger_session'))+' / '+str(p.get('entry_session')),
             (p['management'][0]['assessment']['category']+' / '+p['post_activation_assessment']['category']) if p['management'] else 'not comparable',
             ', '.join(p.get('source_actions_before_activation', [])) or 'none'] for p in c['delayed_entries']])
        lines += ['', '**INFERENCE:** the three prioritized explanations below distinguish conditional market support from identification of actual practice.', '']
        lines += table(['Hypothesis', 'Supporting evidence', 'Contradicting evidence', 'Missing evidence', 'Verdict / scope'], [
            [p['hypothesis'],p['support'],p['contradiction'],p['missing'],p['verdict']+' — '+p['scope']] for p in EXPLANATIONS[symbol]])
        if symbol == 'CLMT':
            lines += ['', 'For an entry after Monday’s last55.25 visit, daily OHLC only bounds positive-risk prices to **(55.25,58.25]**. '
                'The intraday capture narrows last-touch timing to15:55–16:00ET, leaving no complete protected bar afterward; '
                'neither the daily High nor the final Close is a demonstrated entry. Wednesday’s51.99 Low below53.02 invalidates '
                'continued hard-stop exposure after that session, but only a source DROP follows. '
                '**Conditionally explained continuation; actual entry and exit cause unresolved.**']
        elif symbol == 'TEVA':
            lines += ['', 'A post-Wednesday-last-touch entry has the daily existential price bound **(40.40,41.09]**; '
                'the nine fully protected later five-minute bars actually span **40.44–40.62**. Thursday and Friday remain protected '
                'after the respective known revisions. This is stronger timing evidence than CLMT, but still no fill.', '',
                'TEVA has only31 admitted daily sessions, September14–October26. '
                'The [issuer’s September14 release](https://ir.tevapharm.com/news-and-events/press-releases/press-release-details/2026/Teva-Begins-Trading-Ordinary-Shares-Directly-on-the-NYSE-Marking-a-Milestone-in-its-Pivot-to-Growth-Strategy/default.aspx) '
                'dates the direct NYSE ordinary-share listing to that day. '
                'The [September14 SEC8-K, item8.01](https://www.sec.gov/Archives/edgar/data/818686/000119312526390562/d503082d8k.htm) '
                'states each prior ADS exchanged for one ordinary share with the same ticker. '
                'Alignment with the retained contract’s first bar supports an identity-boundary explanation for limited warmup, '
                'not proof of IBKR’s truncation mechanism. The one-for-one conversion provides no price rescaling remedy for the October21 stop breach. '
                'No old ADS contract is inferred or spliced; SMA50 and long-window pivots remain missing. '
                '**Conditionally explained continuation; actual entry/convention unidentifiable.**']
        elif symbol == 'GME':
            lines += ['', 'Thursday’s post-last-touch daily bound is **(25.01,26.25]**, with five complete protected bars spanning **25.05–25.38** '
                'after15:30–15:35ET. This alone fails under late/Friday-Close weekly publication: Friday Low24.68 crosses the still-active24.78. '
                'Friday’s post-last-touch daily bound is **(24.78,25.61]**, but its last touch also extends into15:55–16:00ET and '
                'requires treating Thursday’s revision as a pre-entry plan update. '
                '**Closing confirmation conditionally explains continuation under all clocks; a Thursday late-entry-only explanation is clock-dependent.**']
        elif symbol == 'EBAY':
            lines += ['', '**No positive-risk entry before Monday Close can survive that Close under the unchanged119.20 hard stop:** '
                'Close118.62 is already adverse. Intraday ordering cannot rescue an already-held long, and closing confirmation also exits '
                'before the evening revision. Applying117.50 to earlier prices would be hindsight. '
                'The independent operator Low117.87 anchor matches the native session but is not a complete basis audit. '
                'NEXT_OPEN_AFTER_CLOSE has a pending October27 exit; fixed cutoff supplies neither that fill nor a later source constraint. '
                '**Hard-stop contradiction remains for already-held exposure; deferred exit or pending-plan interpretations are conditional and unidentifiable.**']
        else:
            lines += ['', 'At H1 short15.46 with initial stop16.40, initial reference risk is0.94 and +1R level14.52. '
                'October22 Open14.51 reaches that target before the evening stop/UNDERWAY cluster. '
                'All intervening Highs remain below the contemporaneously known protective stops. '
                'Full realization therefore causes a **TARGET_EXIT_CONVENTION_CONFLICT**, not a protective-stop failure. '
                'A partial runner and a full hold are both compatible; no observed sizing distinguishes them. '
                'Source remains **SHORT / OPEN / UNDERWAY /13.90**.']
        lines += ['']
    lines += ['## Falsified shortcuts and what remains unresolved', '',
        'For all four H1 entries, the first protective-stop breach precedes any +1R reach. '
        'A residual runner with the same hard protective stop cannot survive that breach. Unreported partial sizing alone '
        'therefore does not fix these contradictions; it would also require a different entry or stop convention. '
        'CDE supplies a genuine partial/hold versus full-target distinction.', '',
        'Price-only multiplication large enough to remove the first breaches would require factors greater than '
        '55.25/53.83≈1.02638 for CLMT, 40.40/39.50≈1.02278 for TEVA, 25.01/24.61≈1.01625 for GME '
        'and119.20/117.87≈1.01128 for EBAY. These are counterfactual inequalities, not corrections; no such factor is applied. '
        'The nominal EBAY anchor and TEVA’s one-for-one identity evidence argue against arbitrary scale repairs. '
        'Corporate-action completeness remains limited for the other cases.', '',
        'ENTERABLE’s source meaning is not identified as either unfilled plan or executed position by these alerts alone. '
        'The ledger’s OPEN facts remain authoritative. A stop may be a risk reference, a closing threshold or a broker order; '
        'fit to the same sparse alerts cannot choose between all of these. '
        '**CLOSE_REVIEW_NEXT_OPEN is an exploratory explanation, not evidence of Grimes’ actual stop-order convention.** '
        'The findings improve failure diagnosis and bound the remaining questions; they do not establish a universal profitable strategy.', '',
        'See [cross-trade tests and reproduction](GRIMES_CROSS_TRADE_INFERENCE.md).', '']
    return readable('\n'.join(lines))


def cross_report(result):
    lines = ['# Grimes cross-trade inference — PR9B', '',
        'The new evidence separates three stop-touch recoveries from EBAY’s adverse Close, while CDE isolates a mandatory-target failure. '
        'These distinctions improve interpretation without identifying an operational policy. '
        'A rule fitting every observed alert may owe its fit to sparse or censored observations.', '',
        '## Fixed cohort and clustered comparisons', '',
        'All26 source episodes are retained, including12 source CLOSED and14 OPEN. '
        'The22 observed next-Open entries exclude right-censored SAIL, SLB, GE and SCCO. '
        'After removing CLMT, TEVA, GME, EBAY and control CDE, the remaining21 comprise17 observed episodes and those4 censored episodes. '
        'Rows below count episode compatibility, not independent experiments: co-published actions are one alert cluster per episode, '
        'and cross-trade evidence is grouped by shared alert IDs in JSON. '
        'Final source OPEN is a separate constraint, not a new alert. '
        'Fully compatible requires at least one later source alert and no unresolved check. '
        'UNRESOLVED includes a source DROP after a hypothetical earlier exit: matching final CLOSED does not establish matching closure cause.', '']
    rows = []
    for s in result['summaries']:
        for policy in ('INTRADAY_HARD_STOP', 'CLOSE_CONFIRMATION', 'NEXT_OPEN_AFTER_CLOSE', 'CLOSE_REVIEW_NEXT_OPEN'):
            counts = s['policies'][policy]
            rows.append([s['clock_variant'],policy]+[len(counts[k]) for k in ('FULLY_COMPATIBLE','ROBUST_CONFLICT','PATH_DEPENDENT','UNRESOLVED','NO_LATER_SOURCE_ALERTS')])
    lines += table(['Weekly clock', 'H1 management convention', 'Fully compatible', 'Robust conflict', 'Path-dependent', 'Unresolved', 'No later alerts'],rows)
    late = next(s for s in result['summaries'] if s['clock_variant']=='LATE_EMAIL_BOUND')
    lines += ['', 'Hard-stop H1 under the late clock has7 fully compatible episodes,4 robust protective conflicts,8 unresolved DROP cases '
        'and3 without later alerts. Removing four cases and CDE leaves **6 fully compatible,0 robust conflicts,8 unresolved and3 no-later-alert** '
        'among17 observed comparison episodes. Absence of a robust contradiction in18/22 overall is weaker than positive support for a stop rule. '
        'The early clock changes AAOI, AMD and SNDK from unresolved DROP-after-exit cases to compatible source closure before that price path. '
        'This is publication sensitivity, not three additional independent confirmations.', '',
        'Closing confirmation reduces robust H1 conflicts from4 to1 under every weekly clock. '
        'CLMT and GME move to unresolved DROP attribution, TEVA becomes fully compatible, and EBAY still conflicts. '
        'The additional rise from7 to11 fully compatible under the late clock also includes AAOI, AMD and SNDK; inspect their source/Close timings in JSON. '
        'An unconditional next-Open exit after a closing breach fits19 later-alert cases and3 final-state-only cases, just like the existing review '
        'at the source-status level. This is **observational equivalence at this cutoff**, not equivalent future exits: '
        'the unconditional rule must execute a queued exit even after an evening stop revision, whereas review may retain exposure. '
        'EBAY’s queued October27 exit is unobserved. No policy is inferred from that censoring.', '',
        '## Delayed-entry falsification across26 episodes', '',
        'D1 uses a reported-stop touch/recovery, D2 two protective Closes, with the first trigger only, three completed eligible sessions, '
        'Close+60minute availability and next-Open execution reference. The stop level must already be known at that day’s Open. '
        'These rules are explicit competing explanations, not reported Grimes rules, and are not optimized.', '']
    rows=[]
    for s in result['summaries']:
        for rule, trades in s['delayed_entries'].items():
            statuses={k:sum(v['status']==k for v in trades.values()) for k in sorted({v['status'] for v in trades.values()})}
            rows.append([s['clock_variant'],rule,'; '.join(f'{k}: {v}' for k,v in statuses.items())])
    lines += table(['Weekly clock', 'Fixed rule', '26-episode outcomes'],rows)
    lines += ['', 'At the late clock, D1 constructs CLMT Tuesday, TEVA Thursday and GME Friday. '
        'All require at least one earlier source revision to be interpreted as management of an intended plan. '
        'GME’s Friday entry still breaches24.78 before the late weekly revision. '
        'D2 rejects TEVA at Wednesday Open40.10 because its then-known40.40 stop gives nonpositive long risk; '
        'it never buys first and repairs the stop retroactively. D2 cannot enter CAT before source DROP. '
        'It also leaves AAPL/CLMT/CDE/T/ELF/HUM/OMER/ANET pre-entry source actions unresolved. '
        'T’s already-reported UNDERWAY before D2 activation specifically weakens a universal pending-plan reading. '
        'Neither D1 nor D2 produces a trigger for EBAY. No trigger does not establish that Grimes had no actual trade. '
        'Thus delayed activation can explain some exposure histories only conditionally; it does not uniformly outperform next-Open without added semantic assumptions.', '',
        '## Stop revisions, market context and dependence', '']
    revisions=[]
    for e in result['episodes']:
        for r in baseline(e)['stop_revisions']:
            revisions.append((e,r))
    clusters={r['alert_id'] for _,r in revisions}
    tight=[(e,r) for e,r in revisions if r['risk_tightening']]
    wide=[(e,r) for e,r in revisions if not r['risk_tightening']]
    lines += [f"The27 stop changes comprise{len(tight)} directional tightenings and{len(wide)} loosenings across{len(clusters)} shared alert clusters. "
        'They are not27 independent behavioral observations. Signed direction accounts for short stops.', '']
    lines += table(['Shared alert', 'Loosenings (symbol old→new)', 'Tightenings (symbols)'],[
        [a, '; '.join(f"{e['symbol']} {r['old_stop']}→{r['new_stop']}" for e,r in wide if r['alert_id']==a) or 'none',
         ', '.join(e['symbol'] for e,r in tight if r['alert_id']==a) or 'none'] for a in sorted(clusters)])
    lines += ['', 'The four protective-conflict cases are all LONG/ENTERABLE and all their disputed continuation clusters occur in '
        'the same seven-alert market episode. CLMT and TEVA are loosened following intraday breaches that recovered by the Close; '
        'GME is similarly loosened after Thursday’s recovery and again in the weekly alert. '
        'EBAY is loosened even after an adverse Close. Counterexample OMER also widens17.20→17.35 as a SHORT/ENTERABLE '
        'without the same hard-stop continuation failure. A stop adjustment alone cannot distinguish intended risk from an order.', '',
        'The per-decision tables retain ATR14, SMA20/50, pre-known confirmed pivots, SPY/QQQ20-session returns and relative SPY strength. '
        'CLMT, GME and EBAY have longer native histories; TEVA lacks SMA50/pivot warmup. '
        'Three outliers exhibit stop-touch recoveries during shared QQQ weakness and a mixed SPY path; that concentration is descriptive. '
        'We cannot separate regime, side, setup type and alert-date effects with this selected sample. '
        'Other source ENTERABLE trades do not force the same contradiction, while CDE UNDERWAY remains hard-stop compatible. '
        'ENTERABLE may mix intended and active exposure, but this data does not demonstrate that interpretation.', '',
        '## What survives and what cannot be identified', '',
        '- Supported conditional finding: closing confirmation explains the three recovered-close continuations with less discretion than next-Open review.',
        '- Robust counterexample: EBAY already-held exposure fails both intraday and Close-confirmed stops; a late entry cannot repair an adverse final Close.',
        '- CDE shows that full+1R realization can be too restrictive even when ordinary protective stops are compatible. Partial runners are plausible, quantities unidentified.',
        '- Late intraday entry is particularly feasible for TEVA; GME depends on weekly publication timing; CLMT’s final-bar breach remains unresolved.',
        '- No rule identifies actual fills, position size, stop-order type or discretionary intent. No predictive model, historical universe inference or profitability claim follows.', '',
        '**CLOSE_REVIEW_NEXT_OPEN is an exploratory explanation, not evidence of Grimes’ actual stop-order convention.** '
        'Its fixed complexity cost2 does not turn compatibility into identification. The new unconditional next-Open diagnostic '
        'is less discretionary but remains a censored alternative at this cutoff.', '',
        '## Provenance, preservation and offline reproduction', '',
        'The local immutable study embeds the139-member PR19 sensitivity parent and the four-window native capture, '
        'revalidating PR19’s semantic chain before deriving these outputs. The new layer lives outside the pinned reconstruction/lifecycle '
        'implementation directories. No execution simulator, original source ledger, frozen result or trade-status CSV is changed. '
        'Public derived evidence includes original source event IDs/hashes, qualified identities, all three clocks, '
        'old candidate/policy outcomes, new diagnostic outcomes and explicit hypothesis verdicts. Native provider returns and complete subscriber inputs remain local.', '',
        '```sh',
        'PYTHONPATH=src .venv/bin/python scripts/grimes_forensics.py --help',
        'PYTHONPATH=src .venv/bin/python scripts/grimes_forensics.py freeze --parent runs/grimes-management-sensitivity-20261028-v1/study-v1 --intraday runs/grimes-forensics-20261018-26-v1/intraday-v1 --documentary docs/evidence/pr9b-forensics-v1/documentary.json --output runs/grimes-forensics-20261018-26-v1/study-NEW',
        'PYTHONPATH=src .venv/bin/python scripts/grimes_forensics.py replay --study runs/grimes-forensics-20261018-26-v1/study-NEW --output runs/grimes-forensics-20261018-26-v1/replay-NEW',
        '.venv/bin/python -m pytest -q', '```', '',
        'Use unused output paths. Offline freeze/replay denies network connections. The separate capture script requires explicit '
        '`--connect --read-only-api-confirmed`, local port and client ID; it is never invoked by tests or offline research commands. '
        'Retrieval windows are fixed to CLMT October19, TEVA October21 and GME October22–23; no further acquisition is needed to replay. '
        'Public-only readers can inspect derived evidence; full native semantic replay requires retained local parent/capture bundles.', '',
        'See [verification record](../evidence/pr9b-forensics-v1/validation.json) for exact hashes, regression results and preservation checks.', '']
    return readable('\n'.join(lines))
