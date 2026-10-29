"""Bounded PR9B forensic diagnostics over unchanged PR19 evidence.

No accounting, optimization, order interfaces or new general simulator. Existing
hard-stop trajectories are reused; close diagnostics test exposure constraints.
"""
from collections import Counter
from copy import deepcopy
from datetime import timedelta
import json
from math import isfinite
from pathlib import Path
from zoneinfo import ZoneInfo

from .comprehension.inputs import _check_hashes
from .ingestion.frames import unpack
from .ingestion.storage import digest, encode, read_bundle, write_bundle
from .lifecycle.study import read_inputs
from .models import timestamp
from .reconstruction.admission import Evidence, risk_geometry, value
from .reconstruction.management import trajectory
from .reconstruction.timing import clock_variants
from .reconstruction_sensitivity import _files as sensitivity_files, assess

PARENT_SHA256 = '484ecf07fcb22467178fe1aaf3cdbcd175bf273bd62854aa40b26444860ce263'
INTRADAY_SHA256 = 'ca29252ce33f46b6824ab5efab59a92c735206ee1d7e54b50e622957591b87fb'
BASELINE = 'LATE_EMAIL_BOUND'
CASES = ('CLMT', 'TEVA', 'GME', 'EBAY', 'CDE')
FEATURES = ('close', 'atr14', 'sma20', 'sma50', 'prior20_high', 'prior20_low',
            'confirmed_swing_high', 'confirmed_swing_low', 'return5', 'return20')
RULES = ('RECLAIM_THEN_NEXT_OPEN', 'TWO_PROTECTIVE_CLOSES_THEN_NEXT_OPEN')
STOP_COSTS = {'INTRADAY_HARD_STOP': 0, 'CLOSE_CONFIRMATION': 1,
              'NEXT_OPEN_AFTER_CLOSE': 2, 'CLOSE_REVIEW_NEXT_OPEN': 2}
ET = ZoneInfo('America/New_York')


def at(event, clock):
    return timestamp(clock['assumed_action_clocks'][event['source']['alert_id']])


def stop_at(trade, clock, moment):
    stop = float(trade['initial_stop'])
    for event in trade['events'][1:]:
        if event['type'] == 'STOP_CHANGED' and at(event, clock) <= timestamp(moment):
            stop = float(event['stop'])
    return stop


def drop_at(trade, clock):
    return next((at(e, clock) for e in trade['events'] if e['type'] == 'DROPPED'), None)


def scan(trade, clock, rows, calendar, cutoff, start):
    """Counterfactual stop-relative bars; includes prices after hypothetical exits."""
    sign = 1 if trade['direction'] == 'LONG' else -1
    dropped = drop_at(trade, clock)
    result = []
    for session in calendar['sessions']:
        day = session['session_date']
        if day < start or timestamp(session['closes_at']) > timestamp(cutoff):
            continue
        if dropped is not None and timestamp(session['opens_at']) >= dropped:
            break
        if day not in rows:
            raise ValueError(f'missing required forensic session: {day}')
        row = rows[day]
        stop = stop_at(trade, clock, session['opens_at'])
        o, hi, lo, cl = [float(row[k]) for k in ('open', 'high', 'low', 'close')]
        adverse = lo if sign == 1 else hi
        recovered = sign*(cl-stop) > 0
        # OHLC permits a last-touch followed by a protected entry. It does not
        # establish an executable fill, intrabar continuity or order placement.
        interval = ([stop, hi] if sign == 1 else [lo, stop]) if recovered else None
        result.append({'session': day, 'opens_at': session['opens_at'], 'closes_at': session['closes_at'],
            'ohlcv': {k: row[k] for k in ('open', 'high', 'low', 'close', 'volume')},
            'known_stop_at_open': stop, 'open_breach': sign*(o-stop) <= 0,
            'range_breach': sign*(adverse-stop) <= 0, 'close_breach': not recovered,
            'post_last_touch_entry_price_bound': interval, 'stop_endpoint_excluded': True,
            'bound_is_existential_not_an_observed_entry': True})
    return result


def close_diagnostic(trade, candidate, clock, rows, calendar, cutoff, policy):
    """First Close violation only: compare exposure end with source constraints.

    This is not a fill or P&L model. Next-open commitment is unconditional;
    subsequent stop revisions cannot rescind it. Close exits are idealized
    boundary conventions, not availability-respecting observed executions.
    """
    if policy not in {'CLOSE_CONFIRMATION', 'NEXT_OPEN_AFTER_CLOSE'}:
        raise ValueError('unsupported diagnostic')
    out = {'policy': policy, 'convention_cost': STOP_COSTS[policy], 'observations': [],
           'rank_eligible': candidate['status'] == 'CONSTRUCTED', 'actual_fills': None,
           'actual_size': None, 'actual_realized_pnl': None, 'no_reentry': True}
    if not out['rank_eligible']:
        return out | {'assessment': {'category': 'NO_OBSERVED_ENTRY'}}
    if candidate['geometry']['reference_risk'] <= 0:
        raise ValueError('positive protected entry risk required')
    bars = scan(trade, clock, rows, calendar, cutoff, candidate['entry_session'])
    violation = next((r for r in bars if r['close_breach']), None)
    exposure_end = None
    if violation:
        if policy == 'CLOSE_CONFIRMATION':
            exposure_end = timestamp(violation['closes_at'])
        else:
            exposure_end = next((timestamp(s['opens_at']) for s in calendar['sessions']
                                 if timestamp(s['opens_at']) > timestamp(violation['closes_at'])), None)
    out.update(first_close_violation=violation['session'] if violation else None,
        exposure_end_bound=exposure_end.isoformat() if exposure_end else None,
        committed_exit_pending=bool(violation and policy == 'NEXT_OPEN_AFTER_CLOSE' and
                                   (exposure_end is None or exposure_end > timestamp(cutoff))),
        close_execution_is_idealized=policy == 'CLOSE_CONFIRMATION',
        queued_exit_cannot_be_cancelled_by_revision=True)
    entry_at = timestamp(candidate['entry_at'])
    observations = [(e, at(e, clock), False) for e in trade['events'][1:]]
    if trade['position_state'] == 'OPEN':
        observations.append(({'event_id': trade['trade_id']+':source-final', 'type': 'SOURCE_STILL_REPORTED_OPEN',
            'source': {'alert_id': 'FINAL_SOURCE_OPEN'}, 'published_at': None}, timestamp(cutoff), True))
    for event, moment, final in observations:
        if moment > timestamp(cutoff):
            continue
        if moment < entry_at:
            status = 'ENTRY_NOT_YET_OBSERVED_NOT_PROOF_NO_TRADE'
        elif exposure_end is not None and moment >= exposure_end:
            status = 'DROP_AFTER_MODEL_EXIT_CAUSE_UNRESOLVED' if event['type'] == 'DROPPED' else 'CONTINUATION_CONFLICT'
        else:
            status = 'ACTIVE_COMPATIBLE'
        out['observations'].append({'event_id': event['event_id'], 'type': event['type'],
            'alert_id': event['source']['alert_id'], 'source_published_at': event['published_at'],
            'assumed_evaluation_clock': moment.isoformat(), 'status': status, 'final_source_state_check': final})
    out['assessment'] = assess(out)
    return out


def delayed_candidate(trade, clock, h1, rows, calendar, cutoff, evidence, rule):
    if rule not in RULES:
        raise ValueError('unknown causal trigger')
    candidate = {'hypothesis': rule, 'status': 'NO_OBSERVED_TRIGGER', 'management': [], 'actual_entry': None,
        'extra_assumptions': ['ENTERABLE may be a pending plan; ADDED remains authoritative source OPEN',
                              'One entry, first trigger only, three eligible completed sessions; no re-entry'],
        'trigger_level_basis': 'Reported stop already known at each Open; no later revision used retroactively'}
    if h1['status'] != 'CONSTRUCTED':
        return candidate | {'status': 'RIGHT_CENSORED_NO_H1_ENTRY'}
    bars = scan(trade, clock, rows, calendar, cutoff, h1['entry_session'])[:3]
    streak = 0
    trigger = None
    for row in bars:
        streak = streak+1 if not row['close_breach'] else 0
        hit = row['range_breach'] and not row['close_breach'] if rule == RULES[0] else streak >= 2
        if hit:
            trigger = row
            break
    if not trigger:
        return candidate
    available = timestamp(trigger['closes_at'])+timedelta(minutes=60)
    candidate.update(trigger_session=trigger['session'], trigger_available_after=available.isoformat())
    session = next((s for s in calendar['sessions'] if timestamp(s['opens_at']) > available), None)
    dropped = drop_at(trade, clock)
    if session is None or timestamp(session['closes_at']) > timestamp(cutoff):
        return candidate | {'status': 'TRIGGER_OBSERVED_ENTRY_RIGHT_CENSORED'}
    if dropped is not None and timestamp(session['opens_at']) >= dropped:
        return candidate | {'status': 'SOURCE_DROPPED_BEFORE_ACTIVATION'}
    day = session['session_date']
    if day not in rows:
        raise ValueError('missing delayed activation session')
    stop = stop_at(trade, clock, session['opens_at'])
    entry = float(rows[day]['open'])
    feature_day, features = evidence.features(trade['symbol'], session['opens_at'])
    geometry = risk_geometry(trade['direction'], entry, stop, value(features, 'atr14'))
    if geometry['reference_risk'] <= 0:
        return candidate | {'status': 'REJECTED_NONPROTECTIVE_ENTRY', 'geometry': geometry}
    candidate.update(status='CONSTRUCTED', candidate_id=trade['trade_id']+':'+clock['name']+':'+rule,
        entry_session=day, entry_at=session['opens_at'], entry_kind='OPEN', entry_price=entry,
        geometry=geometry, reported_stop_at_entry=stop, construction_support=0,
        pre_entry_features_session=feature_day,
        source_actions_before_activation=[e['event_id'] for e in trade['events'][1:] if at(e, clock) < timestamp(session['opens_at'])])
    scenario = trajectory(trade, candidate, clock, rows, calendar, cutoff, 'HOLD_WITH_REPORTED_STOPS')
    candidate['management'] = [scenario | {'assessment': assess(scenario)}]
    later = deepcopy(scenario)
    later['observations'] = [o for o in scenario['observations']
        if timestamp(o['assumed_evaluation_clock']) >= timestamp(candidate['entry_at'])]
    candidate['post_activation_assessment'] = assess(later)
    candidate['pre_activation_underway_events'] = [e['event_id'] for e in trade['events'][1:]
        if e.get('setup_after') == 'UNDERWAY' and at(e, clock) < timestamp(candidate['entry_at'])]
    return candidate


def intraday_observations(capture, prices, calendar):
    sessions = {s['session_date']: s for s in calendar['sessions']}
    result = []
    stops = {('CLMT', '2026-10-19'): 55.25, ('TEVA', '2026-10-21'): 40.4,
             ('GME', '2026-10-22'): 25.01, ('GME', '2026-10-23'): 24.78}
    seen = set()
    for w in capture['windows']:
        key = w['symbol'], w['session']
        if key not in stops or key in seen:
            raise ValueError('unexpected or duplicate forensic window')
        seen.add(key)
        record = {k: w[k] for k in ('symbol', 'session', 'con_id', 'status', 'started_at', 'completed_at', 'parameters', 'errors')}
        record['native_rows'] = len(w['native_bars'])
        params = w['parameters']
        if (params['barSizeSetting'] != '5 mins' or params['whatToShow'] != 'TRADES'
                or params['useRTH'] is not True or params['keepUpToDate'] is not False):
            raise ValueError('unexpected intraday request basis')
        if w['status'] != 'SUCCESS':
            result.append(record)
            continue
        bars = [{k: unpack(v) for k, v in b.items()} for b in w['native_bars']]
        s = sessions[w['session']]
        expected = [timestamp(s['opens_at'])+timedelta(minutes=5*i) for i in range(78)]
        if [b['date'] for b in bars] != expected:
            raise ValueError('incomplete or nonchronological five-minute session')
        for b in bars:
            vals = [float(b[k]) for k in ('open', 'high', 'low', 'close', 'volume')]
            if not all(isfinite(v) for v in vals) or min(vals[:4]) <= 0 or vals[4] < 0 or not vals[2] <= min(vals[0], vals[3]) <= max(vals[0], vals[3]) <= vals[1]:
                raise ValueError('invalid native intraday OHLCV')
        stop = stops[key]
        touching = [i for i, b in enumerate(bars) if b['low'] <= stop]
        last = touching[-1] if touching else None
        tail = bars[last+1:] if last is not None else bars
        aggregate = {'open': float(bars[0]['open']), 'high': max(float(b['high']) for b in bars),
                     'low': min(float(b['low']) for b in bars), 'close': float(bars[-1]['close'])}
        daily = next(r for r in prices[w['symbol']] if r['session_date'] == w['session'])
        record.update(comparison_stop=stop, aggregate=aggregate,
            frozen_daily={k: daily[k] for k in aggregate},
            differences={k: round(v-float(daily[k]), 8) for k, v in aggregate.items()},
            first_touch_bar=bars[touching[0]]['date'].isoformat() if touching else None,
            last_touch_bar=bars[last]['date'].isoformat() if last is not None else None,
            last_touch_bar_end=(bars[last]['date']+timedelta(minutes=5)).isoformat() if last is not None else None,
            full_protected_bars_after_last_touch=len(tail),
            protected_tail_price_range=[min(float(b['low']) for b in tail), max(float(b['high']) for b in tail)] if tail else None,
            post_last_touch_price_outer_bound=[stop, max(float(b['high']) for b in bars[last:])]
                if last is not None and float(bars[-1]['close']) > stop else None,
            lower_bound_excluded=True,
            actual_entry_identified=False, intrabar_order_unresolved=True,
            limitation='Five-minute bar starts; last touch lies inside that bar, not at a known second. No fills or quotes.')
        result.append(record)
    if seen != set(stops):
        raise ValueError('capture must record all four attempted windows')
    return result


def analyze(episodes, inputs, capture, documentary):
    spec, alerts, prices, coverage, calendar, methodology = inputs
    cutoff = spec['analysis_cutoff']
    evidence = Evidence(prices, coverage, calendar, cutoff)
    clocks = clock_variants(alerts['alerts'], calendar)
    results = []
    for episode in episodes:
        trade = episode['source']
        symbol = trade['symbol']
        row = {'symbol': symbol, 'trade_id': trade['trade_id'], 'source': trade,
               'market_identity': coverage[symbol], 'clocks': []}
        for clock in clocks:
            old = next(c for c in episode['clock_comparisons'] if c['clock_variant'] == clock['name'])
            h1 = next(p for p in old['candidates'] if p['hypothesis'] == 'H1_NEXT_OPEN')
            rows = evidence.rows(symbol)
            out = {'clock_variant': clock['name'], 'publication_bounds': clock['publication_bounds'],
                   'original_candidates': old['candidates'], 'original_leaders': old['leading'],
                   'stop_diagnostics': [], 'delayed_entries': [], 'counterfactual_daily_stop_scan': []}
            if h1['status'] == 'CONSTRUCTED':
                out['counterfactual_daily_stop_scan'] = scan(trade, clock, rows, calendar, cutoff, h1['entry_session'])
                for policy in ('HOLD_WITH_REPORTED_STOPS', 'CLOSE_REVIEW_NEXT_OPEN'):
                    sc = next(s for s in h1['management'] if s['policy'] == policy)
                    out['stop_diagnostics'].append({'policy': 'INTRADAY_HARD_STOP' if policy.startswith('HOLD') else policy,
                        'convention_cost': sc['convention_cost'], 'assessment': assess(sc),
                        'terminal_possibilities': sc['terminal_possibilities'], 'observations': sc['observations']})
                out['stop_diagnostics'] += [close_diagnostic(trade, h1, clock, rows, calendar, cutoff, p)
                    for p in ('CLOSE_CONFIRMATION', 'NEXT_OPEN_AFTER_CLOSE')]
            out['delayed_entries'] = [delayed_candidate(trade, clock, h1, rows, calendar, cutoff, evidence, rule) for rule in RULES]
            # Every source decision gets price-available indicators, not future
            # features chosen at the end of the whole study.
            out['source_decisions'] = []
            for event in trade['events']:
                moment = clock['assumed_action_clocks'][event['source']['alert_id']]
                day, features = evidence.features(symbol, moment)
                out['source_decisions'].append({'event_id': event['event_id'], 'assumed_clock': moment,
                    'available_feature_session': day, 'features': {k: features.get(k) for k in FEATURES},
                    'SPY_return20': value(evidence.panel.features('SPY', day), 'return20') if day else None,
                    'QQQ_return20': value(evidence.panel.features('QQQ', day), 'return20') if day else None,
                    'relative_SPY20': evidence.panel.relative(symbol, 'SPY', day, 20) if day else None})
            out['stop_revisions'] = []
            for event, decision in zip(trade['events'], out['source_decisions']):
                if event['type'] != 'STOP_CHANGED':
                    continue
                sign = 1 if trade['direction'] == 'LONG' else -1
                old_stop, new_stop = float(event['previous_stop']), float(event['stop'])
                day = decision['available_feature_session']
                close = float(rows[day]['close']) if day in rows else None
                out['stop_revisions'].append({'event_id': event['event_id'], 'alert_id': event['source']['alert_id'],
                    'old_stop': old_stop, 'new_stop': new_stop,
                    'risk_tightening': sign*(new_stop-old_stop) > 0,
                    'signed_tightening': round(sign*(new_stop-old_stop), 8),
                    'available_close_session': day, 'available_close': close,
                    'old_stop_breached_at_available_close': sign*(close-old_stop) <= 0 if close is not None else None})
            row['clocks'].append(out)
        row['market_window'] = [r for r in prices[symbol] if '2026-10-15' <= r['session_date'] <= '2026-10-26']
        baseline = next(c for c in row['clocks'] if c['clock_variant'] == BASELINE)
        h1 = next(p for p in baseline['original_candidates'] if p['hypothesis'] == 'H1_NEXT_OPEN')
        if h1['status'] != 'CONSTRUCTED':
            row['model_failure_type'] = 'RIGHT_CENSORED'
        else:
            full = assess(next(s for s in h1['management'] if s['policy'] == 'FULL_EXIT_AT_1R'))
            hold = assess(next(s for s in h1['management'] if s['policy'] == 'HOLD_WITH_REPORTED_STOPS'))
            row['model_failure_type'] = ('PROTECTIVE_STOP_CONFLICT' if hold['category'] == 'ROBUST_CONFLICT' else
                'TARGET_EXIT_CONVENTION_CONFLICT' if full['category'] == 'ROBUST_CONFLICT' else
                'UNRESOLVED_DROP_CAUSE' if hold['category'] == 'UNRESOLVED' else 'NO_ROBUST_CONTINUATION_CONFLICT')
        results.append(row)
    summaries = []
    for clock in clocks:
        per = [next(c for c in r['clocks'] if c['clock_variant'] == clock['name']) for r in results]
        summary = {'clock_variant': clock['name'], 'episode_count': len(results), 'policies': {}, 'delayed_entries': {}}
        for policy in STOP_COSTS:
            summary['policies'][policy] = {cat: [r['symbol'] for r, c in zip(results, per) for p in c['stop_diagnostics']
                if p['policy'] == policy and p['assessment']['category'] == cat]
                for cat in ('FULLY_COMPATIBLE', 'ROBUST_CONFLICT', 'PATH_DEPENDENT', 'UNRESOLVED', 'NO_LATER_SOURCE_ALERTS')}
        for rule in RULES:
            summary['delayed_entries'][rule] = {r['symbol']: {k: p.get(k) for k in ('status', 'trigger_session', 'entry_session', 'source_actions_before_activation')}
                | {'assessment': p['management'][0]['assessment']['category'] if p['management'] else None}
                for r, c in zip(results, per) for p in c['delayed_entries'] if p['hypothesis'] == rule}
        summary['right_censored'] = [r['symbol'] for r, c in zip(results, per) if not c['stop_diagnostics']]
        summary['alert_clusters'] = {}
        for policy in STOP_COSTS:
            clusters = {}
            for r, c in zip(results, per):
                for p in c['stop_diagnostics']:
                    if p['policy'] != policy:
                        continue
                    for o in p['observations']:
                        if not o['final_source_state_check']:
                            clusters.setdefault(o['alert_id'], {}).setdefault(r['symbol'], set()).add(o['status'])
            summary['alert_clusters'][policy] = {alert: {symbol: sorted(states) for symbol, states in trades.items()}
                                                for alert, trades in sorted(clusters.items())}
        summaries.append(summary)
    from .grimes_forensic_reports import EXPLANATIONS
    return {'schema_version': 'grimes_forensics_v1', 'baseline_clock': BASELINE,
        'parent_sha256': PARENT_SHA256, 'cutoff': cutoff, 'source_episode_count': len(results),
        'source_status_authoritative': True, 'actual_stop_convention_identified': False,
        'researcher': 'The repository analysis defines and tests these diagnostics; they are not attributed to Grimes',
        'costs_are_ordinal_assumption_counts_not_likelihoods': STOP_COSTS,
        'episodes': results, 'summaries': summaries,
        'explanations': EXPLANATIONS,
        'intraday': intraday_observations(capture, prices, calendar), 'documentary_evidence': documentary}


def _files(parent, hashes, capture_files, capture_hashes, documentary):
    _check_hashes(parent, hashes)
    _check_hashes(capture_files, capture_hashes)
    if hashes['bundle_sha256'] != PARENT_SHA256:
        raise ValueError('declared PR19 sensitivity parent required')
    if capture_hashes['bundle_sha256'] != INTRADAY_SHA256:
        raise ValueError('declared four-window PR9B capture required')
    original = {k[7:]: v for k, v in parent.items() if k.startswith('parent-') and k != 'parent-hashes.json'}
    original_hashes = json.loads(parent['parent-hashes.json'])
    if parent != sensitivity_files(original, original_hashes):
        raise ValueError('PR19 semantic parent mismatch')
    prefix = 'input-pr17-parent-input-'
    inputs = {k[len(prefix):]: v for k, v in original.items() if k.startswith(prefix) and k != prefix+'hashes.json'}
    result = analyze(json.loads(original['episodes.json']), read_inputs(inputs), json.loads(capture_files['capture.json']), documentary)
    from .grimes_forensic_reports import cross_report, four_report, public_comparison
    return {'forensics.json': encode(result), 'documentary.json': encode(documentary),
        'forensic_comparison.json': encode(public_comparison(result)),
        'four-trade-report.md': four_report(result).encode(), 'cross-trade-report.md': cross_report(result).encode(),
        'manifest.json': encode({'schema_version': 'grimes_forensics_bundle_v1',
            'parent_sha256': hashes['bundle_sha256'], 'intraday_sha256': capture_hashes['bundle_sha256'],
            'implementation_sha256': digest(Path(__file__).read_bytes()),
            'report_implementation_sha256': digest(Path(__file__).with_name('grimes_forensic_reports.py').read_bytes()),
            'source_state_changed': False, 'new_simulator': False}),
        'parent-hashes.json': encode(hashes), **{'parent-'+k: v for k, v in parent.items()},
        'intraday-hashes.json': encode(capture_hashes), **{'intraday-'+k: v for k, v in capture_files.items()}}


def freeze(parent, capture, documentary, output):
    files, hashes = read_bundle(parent)
    intraday, ih = read_bundle(capture)
    return write_bundle(output, _files(files, hashes, intraday, ih, json.loads(Path(documentary).read_bytes())))


def load(path):
    files, hashes = read_bundle(path)
    parent = {k[7:]: v for k, v in files.items() if k.startswith('parent-') and k != 'parent-hashes.json'}
    capture = {k[9:]: v for k, v in files.items() if k.startswith('intraday-') and k != 'intraday-hashes.json'}
    if files != _files(parent, json.loads(files['parent-hashes.json']), capture,
                       json.loads(files['intraday-hashes.json']), json.loads(files['documentary.json'])):
        raise ValueError('forensics semantic output mismatch')
    return files, hashes
