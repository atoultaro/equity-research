"""PR9F: initial structural stops only; price-only candidates, never risk fitting."""
from collections import Counter
from datetime import datetime, time, timedelta
from decimal import Decimal
import json
from pathlib import Path
from statistics import mean, median
from zoneinfo import ZoneInfo

from .comprehension.inputs import _check_hashes
from .ingestion.storage import digest, encode, read_bundle
from .reconstruction.admission import value
from .structural_stops import chart_view, csv_bytes, source_inventory
from .structural_stops import identity as inherited_identity
from .marketlife_setups import timing_scenarios
from .models import timestamp

FAMILIES = ('SWING', 'PULLBACK', 'RANGE', 'SIGNAL_BAR', 'COMPRESSION', 'VOLATILITY')
PROTOCOL = {
    'schema_version': 'initial_stop_protocol_v2', 'decision_type': 'INITIAL',
    'chart_sessions': 60, 'minimum_chart_sessions': 20,
    'inherited_proxies': {'swing_left_right': 3, 'pullback_origin_sessions': 20,
        'range_sessions': 10, 'signal_prior_sessions': 20, 'signal_search_sessions': 20,
        'secondary_signal_base': 'OPPOSING_EXTREME_OF_20_BARS_PRECEDING_LATEST_DIRECTIONAL_SIGNAL'},
    'compression': {'minimum_bars': 3, 'contraction': 'STRICTLY_DECREASING_HIGH_MINUS_LOW',
        'intervals': 'MAXIMAL_RUNS_IN_AVAILABLE_60_BARS_ENDING_IN_LAST_20',
        'primary': 'MOST_RECENT_END_NOT_NEAREST_STOP', 'retain_all_intervals': True,
        'boundary': 'ENTIRE_RUN_MIN_LOW_LONG_MAX_HIGH_SHORT',
        'shared_price_region': 'MAX_LOW_LE_MIN_HIGH', 'prior_range_reference_sessions': 10,
        'prior_range_ratio_threshold': None, 'maximum_age_threshold': None},
    'primary_clock': 'LATE', 'research_tick': '0.01', 'verified_contract_min_tick': False,
    'candidate_selection_receives_stops': False, 'buffers_fitted': False,
    'atr_multipliers_fitted': False, 'residual_match_threshold': None,
    'risk_evaluation_performed': False, 'subsequent_stop_revision_analysis': False,
    'expert_intent': 'UNKNOWN', 'actual_entries': 'UNKNOWN',
    'cohorts': ['PR9E_INITIAL_34', 'NOVEMBER_3_NEW'],
    'source_type_used_to_select_candidates': False,
}


def identity():
    return {**inherited_identity(), 'initial_stops.py': digest(Path(__file__).read_bytes())}


def observation(source):
    proof = source.get('november_observation_proof')
    if not proof: return None
    files = {k: v.encode() for k, v in proof['files'].items()}
    _check_hashes(files, proof['hashes'])
    if set(files) != {'operator-brief.txt', 'observation.json'}:
        raise ValueError('complete immutable November observation proof required')
    o = json.loads(files['observation.json'])
    if o['publication_precision'] != 'DATE' or o['published_at'] is not None:
        raise ValueError('November publication time must remain unknown')
    if o['source_date'] != '2026-11-03' or o['attribution'] != 'OPERATOR_SUPPLIED_TASK_BRIEF_NOT_ORIGINAL_PUBLISHER_PAYLOAD':
        raise ValueError('undeclared November observation provenance')
    if not o.get('observed_by_utc') or timestamp(o['observed_by_utc']).astimezone(ZoneInfo('America/New_York')).date().isoformat() < o['source_date']:
        raise ValueError('source date after observation bound')
    if len({a['action_id'] for a in o['actions']}) != len(o['actions']):
        raise ValueError('duplicate source observation action')
    added = [a['symbol'] for a in o['actions'] if a['kind'] == 'NEW_SETUP']
    if len(set(added)) != len(added):
        raise ValueError('duplicate newly added symbol within one source observation')
    for a in o['actions']:
        if a['kind'] not in {'NEW_SETUP', 'SOURCE_TRACKED_STOP_OUT', 'STOP_REVISION', 'DROPPED'}:
            raise ValueError('unrecognized preserved source action')
    return o


def initial_inventory(source):
    """Read source facts through the existing ledger; retain only first ADDED stops.

    Parsing source history is provenance validation, not analysis of later stops.
    No revision, return, execution or lifecycle outcome enters a candidate.
    """
    keys = ('decision_id', 'setup_id', 'symbol', 'direction', 'source_alert_id', 'source_order',
        'decision_type', 'published_stop', 'source_text', 'source_text_sha256',
        'observed_publication', 'publication_display', 'publication', 'cutoffs')
    parent = source.get('parent_source', source)
    rows = [{**{k: d[k] for k in keys}, 'cohort': 'PR9E_INITIAL_34', 'marketlife_type': 'UNKNOWN'}
            for d in source_inventory(parent) if d['decision_type'] == 'INITIAL']
    o = observation(source)
    if o:
        lower = datetime.combine(datetime.fromisoformat(o['source_date']).date(), time(), ZoneInfo('America/New_York'))
        upper = min(lower + timedelta(days=1) - timedelta(microseconds=1), timestamp(o['observed_by_utc']))
        meta = {'alert_id': o['observation_id'], 'published_at': None, 'publication_precision': 'DATE',
            'lower': lower.isoformat(), 'upper': upper.isoformat(),
            'source_reference': o['source_reference'], 'original_publication_display': o['source_date'],
            'text_sha256': source['november_observation_proof']['hashes']['files']['operator-brief.txt'],
            'bound_kind': 'OPERATOR_DATE_AND_OBSERVED_BY_UPPER_BOUND_NOT_EXACT_PUBLICATION'}
        clocks = timing_scenarios([meta], parent['calendar'])
        for a in o['actions']:
            if a['kind'] != 'NEW_SETUP': continue
            if (a['direction'] not in {'LONG', 'SHORT'} or a['marketlife_type'] not in o['observed_type_vocabulary']
                    or not Decimal(a['initial_stop']).is_finite() or Decimal(a['initial_stop']) <= 0):
                raise ValueError('invalid source initial setup')
            prior = [r for r in rows if r['symbol'] == a['symbol']]
            if prior and prior[-1]['direction'] == a['direction'] and not any(
                    p['kind'] == 'SOURCE_TRACKED_STOP_OUT' and p['symbol'] == a['symbol'] and p['direction'] == a['direction'] for p in o['actions']):
                raise ValueError('same-direction new episode needs supplied prior termination evidence')
            number = max((int(r['setup_id'].rsplit('-', 1)[1]) for r in prior), default=0) + 1
            rows.append({'decision_id': a['action_id'], 'setup_id': f"{a['symbol']}-{number:03d}",
                'symbol': a['symbol'], 'direction': a['direction'], 'source_alert_id': o['observation_id'],
                'source_order': max((r['source_order'] for r in rows), default=-1) + 1,
                'decision_type': 'INITIAL', 'published_stop': a['initial_stop'],
                'source_text': a['source_statement'], 'source_text_sha256': meta['text_sha256'],
                'observed_publication': 'UNKNOWN', 'publication_display': o['source_date'], 'publication': meta,
                'cutoffs': {c['name']: c['actions'][o['observation_id']] for c in clocks},
                'cohort': 'NOVEMBER_3_NEW', 'marketlife_type': a['marketlife_type'],
                'previous_observed_episode_ids': [r['setup_id'] for r in prior],
                'new_episode_evidence': 'Operator explicitly reports a fresh setup; same-direction SLB follows source-tracked stop-out. No fill/stop-out mechanics inferred.'})
    for d in rows:
        d.update(initial_published_stop=d['published_stop'], entry_reference_at_initial_decision=None,
            entry_reference_type_at_initial_decision='UNKNOWN', entry_to_initial_stop_risk='UNKNOWN',
            actual_subscriber_execution='UNKNOWN')
    if len({d['setup_id'] for d in rows}) != len(rows):
        raise ValueError('multiple initial decisions for one source setup')
    return rows


def stubs(decisions):
    return [{k: d[k] for k in ('decision_id', 'setup_id', 'symbol', 'direction', 'decision_type', 'cutoffs')}
            for d in decisions]


def project(parent_files, parent_hashes, observation_proof=None):
    _check_hashes(parent_files, parent_hashes)
    parent_source = json.loads(parent_files['source.json'])
    source = {'parent_source': parent_source, 'november_observation_proof': observation_proof} if observation_proof else parent_source
    decisions = initial_inventory(source)
    market = json.loads(parent_files['market.json'])
    market['decisions'] = stubs(decisions)
    # Native rows remain exact. Each view admits only its own pre-alert prefix.
    return {'market.json': encode(market), 'source.json': encode(source),
        'parent-hashes.json': encode(parent_hashes), 'protocol.json': encode(PROTOCOL),
        'provenance.json': encode({'schema_version': 'initial_stop_projection_v1',
            'parent_bundle_sha256': parent_hashes['bundle_sha256'],
            'parent_market_sha256': digest(parent_files['market.json']),
            'parent_source_sha256': digest(parent_files['source.json']),
            'initial_decisions': len(decisions), 'subsequent_decisions_analyzed': 0,
            'native_archive_sha256': parent_source.get('native_archive_sha256'),
            'november_observation_sha256': observation_proof['hashes']['bundle_sha256'] if observation_proof else None,
            'scope': 'Existing frozen export; no acquisition; historical dissemination remains unverified.'})}


def prepare(parent_path, expected_sha256, observation_path=None):
    files, hashes = read_bundle(parent_path)
    if hashes['bundle_sha256'] != expected_sha256:
        raise ValueError('declared frozen parent hash differs')
    proof = None
    if observation_path:
        evidence, eh = read_bundle(observation_path)
        proof = {'files': {k: v.decode() for k, v in evidence.items()}, 'hashes': eh}
    return project(files, hashes, proof)


def compression_runs(rows, direction):
    """Enumerate maximal strict range contractions without a stop or ATR input."""
    if not rows:
        return []
    ranges = [Decimal(r['high']) - Decimal(r['low']) for r in rows]
    intervals = []; start = 0
    for i in range(1, len(rows) + 1):
        if i < len(rows) and ranges[i] < ranges[i - 1]:
            continue
        end = i - 1
        if end - start + 1 >= 3 and end >= len(rows) - 20:
            run = rows[start:i]; low = min(Decimal(r['low']) for r in run)
            high = max(Decimal(r['high']) for r in run)
            level = low if direction == 'LONG' else high
            field = 'low' if direction == 'LONG' else 'high'
            anchor = [r['session_date'] for r in run if Decimal(r[field]) == level][-1]
            previous = ranges[max(0, start - 10):start]
            shared_low = max(Decimal(r['low']) for r in run)
            shared_high = min(Decimal(r['high']) for r in run)
            breakout = [r['session_date'] for r in rows[i:] if
                (Decimal(r['close']) > high if direction == 'LONG' else Decimal(r['close']) < low)]
            intervals.append({'family': 'COMPRESSION', 'candidate_id': f"compression:{run[0]['session_date']}:{run[-1]['session_date']}",
                'level': str(level), 'anchor_session': anchor, 'confirmation_session': run[-1]['session_date'],
                'interval_start': run[0]['session_date'], 'interval_end': run[-1]['session_date'],
                'interval_sessions': [r['session_date'] for r in run], 'bars': len(run),
                'daily_ranges': [str(x) for x in ranges[start:i]],
                'last_first_range_ratio': float(ranges[end] / ranges[start]) if ranges[start] else None,
                'mean_range_prior10_ratio': float(mean(ranges[start:i]) / mean(previous))
                    if len(previous) == 10 and mean(previous) else None,
                'box_low': str(low), 'box_high': str(high),
                'common_price_overlap': shared_low <= shared_high,
                'common_price_low': str(shared_low), 'common_price_high': str(shared_high),
                'box_width_mean_range': float((high - low) / mean(ranges[start:i])) if mean(ranges[start:i]) else None,
                'ending_at_latest_bar': end == len(rows) - 1, 'sessions_since_end': len(rows) - 1 - end,
                'left_censored': start == 0, 'directional_close_breakouts_after_end': breakout,
                'primary': False, 'reason': 'Maximal sequence of at least three strictly contracting daily High-Low ranges; full-run opposing boundary.',
                'expected_invalidation': 'Breach of the whole sequence boundary contradicts unbroken support/resistance; reclaim is a different explanation.'})
        start = i
    if intervals:
        intervals[-1]['primary'] = True
    return intervals


def candidates(view):
    if not view['status'].startswith('AVAILABLE'):
        return [{'family': f, 'candidate_id': f, 'level': None, 'anchor_session': None,
            'primary': True, 'reason': view['status'], 'expected_invalidation': 'UNKNOWN'} for f in FAMILIES]
    inherited = view['candidates']; result = []
    for family, old in zip(FAMILIES[:4], inherited[:4]):
        result.append({**old, 'family': family, 'candidate_id': family, 'primary': True})
    signals = [s for s in view['signals'] if s['direction'] == view['direction']]
    if signals:
        signal = signals[-1]; rows = view['rows']
        index = next(i for i, r in enumerate(rows) if r['session_date'] == signal['session'])
        base = rows[index - 20:index]; field = 'low' if view['direction'] == 'LONG' else 'high'
        level = (min if field == 'low' else max)(Decimal(r[field]) for r in base)
        result[3].update(structure_role='SIGNAL_CANDLE', breakout_trigger_boundary=signal['prior_boundary'])
        result.append({'family': 'SIGNAL_BAR', 'candidate_id': 'PRE_SIGNAL_BASE', 'primary': False,
            'structure_role': 'PRE_SIGNAL_20_BAR_BASE', 'level': str(level),
            'anchor_session': [r['session_date'] for r in base if Decimal(r[field]) == level][-1],
            'confirmation_session': signal['session'], 'interval_start': base[0]['session_date'],
            'interval_end': base[-1]['session_date'], 'breakout_trigger_boundary': signal['prior_boundary'],
            'reason': 'Opposing boundary of the entire prior-20-bar base, distinct from the signal candle and breakout trigger.',
            'expected_invalidation': 'Breach of the pre-signal base boundary contradicts an intact-base explanation.'})
    runs = compression_runs(view['rows'], view['direction'])
    result.extend(runs or [{'family': 'COMPRESSION', 'candidate_id': 'COMPRESSION', 'level': None,
        'anchor_session': None, 'primary': True, 'reason': 'NO_QUALIFYING_CONTRACTING_RANGE_SEQUENCE',
        'expected_invalidation': 'UNKNOWN'}])
    result.append({**inherited[-1], 'family': 'VOLATILITY', 'candidate_id': 'VOLATILITY', 'primary': True,
        'reason': 'No independently observed entry, volatility anchor or multiplier; no fitted volatility stop is manufactured.'})
    return result


def annotate(market):
    views = []; seen = set()
    for d in market['decisions']:
        if set(d) != {'decision_id', 'setup_id', 'symbol', 'direction', 'decision_type', 'cutoffs'} or d['decision_type'] != 'INITIAL':
            raise ValueError('only stop-masked INITIAL decisions admitted')
        if d['setup_id'] in seen:
            raise ValueError('duplicate initial setup')
        seen.add(d['setup_id']); groups = {}
        for clock, cutoff in d['cutoffs'].items():
            v = chart_view(market, d['symbol'], d['direction'], cutoff)
            v['candidates'] = candidates(v)
            # ATR remains a descriptive normalization, never a candidate constructor.
            v['features'] = {k: v['features'][k] for k in ('close', 'atr14')}
            v['price_pattern_proxy'] = v.pop('observable_family_proxy')
            token = digest(encode(v))
            if token not in groups:
                groups[token] = {**v, 'view_id': f"i{len(views) + len(groups):03d}",
                    'decision_id': d['decision_id'], 'decision_type': 'INITIAL', 'scenarios': {}}
            groups[token]['scenarios'][clock] = cutoff
        views.extend(groups.values())
    return {'schema_version': 'initial_structural_annotations_v1', 'protocol': PROTOCOL,
        'masking': 'Programmatic only; known historical cases are not genuinely blind or held out.', 'views': views}


def compare(annotations, decisions):
    if any(d['decision_type'] != 'INITIAL' for d in decisions):
        raise ValueError('stop revisions are outside PR9F')
    by_id = {d['decision_id']: d for d in decisions}; matrix = []; verdicts = []
    for v in annotations['views']:
        d = by_id[v['decision_id']]; stop = Decimal(d['published_stop'])
        sign = 1 if d['direction'] == 'LONG' else -1
        atr = value(v['features'], 'atr14'); close = value(v['features'], 'close')
        supported = []; weak = []
        for c in v['candidates']:
            level = Decimal(str(c['level'])) if c['level'] is not None else None
            buffer = sign * (level - stop) if level is not None else None
            protective = sign * (Decimal(str(close)) - level) > 0 if level is not None and close is not None else False
            breaches = [r['session_date'] for r in v['rows'] if level is not None and c.get('confirmation_session')
                and r['session_date'] > c['confirmation_session']
                and sign * (Decimal(r['low' if sign == 1 else 'high']) - level) < 0]
            geometry = buffer is not None and buffer >= 0 and protective
            common = c.get('common_price_overlap')
            compatible = geometry and not breaches and c['family'] not in {'RANGE', 'VOLATILITY'} and common is not False
            verdict = ('UNKNOWN' if level is None else 'STOP_INSIDE_BOUNDARY' if buffer < 0 else
                'NOT_PROTECTIVE_TO_CURRENT_CLOSE' if not protective else 'DESCRIPTIVE_RANGE_ONLY' if c['family'] == 'RANGE' else
                'NO_SHARED_COMPRESSION_PRICE_REGION' if common is False else 'ALREADY_BREACHED_ANCHOR' if breaches else
                'GEOMETRIC_PROXY_WITHOUT_RECORDED_CONTRADICTION')
            row = {'decision_id': d['decision_id'], 'setup_id': d['setup_id'], 'symbol': d['symbol'],
                'direction': d['direction'], 'decision_type': 'INITIAL', 'view_id': v['view_id'],
                'scenarios': list(v['scenarios']), 'expected_session': v['expected_session'], 'data_status': v['status'],
                'cohort': d.get('cohort', 'PR9E_INITIAL_34'), 'marketlife_type': d.get('marketlife_type', 'UNKNOWN'),
                'price_pattern_proxy': v['price_pattern_proxy'],
                **c, 'published_initial_stop': str(stop), 'buffer_price': str(buffer) if buffer is not None else None,
                'buffer_research_ticks': str(buffer / Decimal(PROTOCOL['research_tick'])) if buffer is not None else None,
                'buffer_ATR14': float(buffer) / atr if buffer is not None and atr else None,
                'atr14_normalization': atr, 'boundary_relation': 'UNKNOWN' if buffer is None else
                    'BEYOND' if buffer > 0 else 'AT' if buffer == 0 else 'INSIDE',
                'current_close_reference': close, 'candidate_protective_to_close': protective,
                'anchor_breaches_after_confirmation': breaches, 'weak_geometry': geometry,
                'structural_proxy_compatible': compatible, 'verdict': verdict, 'expert_intent': 'UNKNOWN'}
            matrix.append(row)
            if c['primary'] and compatible: supported.append(c['family'])
            if c['primary'] and geometry: weak.append(c['family'])
        verdicts.append({'decision_id': d['decision_id'], 'view_id': v['view_id'], 'scenarios': list(v['scenarios']),
            'cohort': d.get('cohort', 'PR9E_INITIAL_34'), 'marketlife_type': d.get('marketlife_type', 'UNKNOWN'),
            'status': v['status'], 'primary_compatible_families': supported, 'primary_weak_geometry_families': weak,
            'resolution': 'UNAVAILABLE' if not v['status'].startswith('AVAILABLE') else 'UNKNOWN' if not supported else
                'MULTIPLE_STRUCTURAL_PROXIES' if len(supported) > 1 else 'SINGLE_PROXY_NOT_IDENTIFIED'})
    return {'schema_version': 'initial_stop_study_v1', 'inventory': decisions,
        'matrix': matrix, 'view_verdicts': verdicts, 'protocol': PROTOCOL,
        'source_model_separation': 'First published setup stops; actual entries and private rationale UNKNOWN; no later-stop or risk evaluation.'}


def summarize(study):
    out = {}
    for clock in ('EARLY', 'CLOSE_BOUNDARY', 'LATE'):
        views = [v for v in study['view_verdicts'] if clock in v['scenarios']]
        primary = [r for r in study['matrix'] if clock in r['scenarios'] and r['primary']]
        strata = []
        for direction in ('ALL', 'LONG', 'SHORT'):
            for family in FAMILIES:
                rows = [r for r in primary if r['family'] == family and (direction == 'ALL' or r['direction'] == direction)]
                ds = [abs(r['buffer_ATR14']) for r in rows if r['buffer_ATR14'] is not None]
                strata.append({'direction': direction, 'family': family, 'decisions': len(rows),
                    'candidate_available': sum(r['level'] is not None for r in rows),
                    'weak_geometry': sum(r['weak_geometry'] for r in rows),
                    'structural_proxy_compatible': sum(r['structural_proxy_compatible'] for r in rows),
                    'inside_boundary': sum(r['boundary_relation'] == 'INSIDE' for r in rows),
                    'prior_boundary_breaches': sum(bool(r['anchor_breaches_after_confirmation']) for r in rows),
                    'no_shared_price_region': sum(r.get('common_price_overlap') is False for r in rows),
                    'median_absolute_residual_ATR14_all_available': median(ds) if ds else None,
                    'verdicts': dict(Counter(r['verdict'] for r in rows))})
        groups = []
        for dimension in ('cohort', 'marketlife_type', 'price_pattern_proxy'):
            for name in sorted({r[dimension] for r in primary}):
                rows = [r for r in primary if r[dimension] == name]
                groups.append({'dimension': dimension, 'value': name, 'decisions': len(rows) // 6,
                    'families': {f: {'candidate_available': sum(r['level'] is not None for r in rows if r['family'] == f),
                        'weak_geometry': sum(r['weak_geometry'] for r in rows if r['family'] == f),
                        'structural_proxy_compatible': sum(r['structural_proxy_compatible'] for r in rows if r['family'] == f)} for f in FAMILIES}})
        out[clock] = {'decisions': len(views), 'availability': dict(Counter(v['status'] for v in views)),
            'resolution': dict(Counter(v['resolution'] for v in views)), 'primary_comparison': strata,
            'cohort_and_setup_family_comparison': groups}
    return {'initial_decisions': len(study['inventory']), 'episodes': len({d['setup_id'] for d in study['inventory']}),
        'source_clusters': len({d['source_alert_id'] for d in study['inventory']}),
        'directions': dict(Counter(d['direction'] for d in study['inventory'])),
        'cohorts': dict(Counter(d.get('cohort', 'PR9E_INITIAL_34') for d in study['inventory'])),
        'source_type_coverage': dict(Counter(d.get('marketlife_type', 'UNKNOWN') for d in study['inventory'])),
        'chart_views': len(study['view_verdicts']), 'candidate_rows': len(study['matrix']),
        'clocks': out, 'subsequent_stop_decisions_analyzed': 0, 'risk_evaluation_performed': False,
        'interpretation': 'Descriptive proxies, not identified mechanisms. Secondary intervals are retained, not residual-ranked.'}


def annotation_files(market):
    return {'market.json': encode(market), 'annotations.json': encode(annotate(market)),
        'annotation-manifest.json': encode({'schema_version': 'masked_initial_stops_v1',
            'implementation': identity(), 'protocol': PROTOCOL, 'published_stops_received': False})}


def family_register(decisions, source):
    o = observation(source)
    return [{'symbol': d['symbol'], 'setup_id': d['setup_id'], 'decision_id': d['decision_id'],
        'direction': d['direction'], 'observed_marketlife_type': d['marketlife_type'],
        'source_snapshot_date': o['source_date'] if o and d['cohort'] == 'NOVEMBER_3_NEW' else None,
        'provenance': o['source_reference'] if o and d['cohort'] == 'NOVEMBER_3_NEW' else 'No episode-specific MarketLife TYPE supplied for initial decision.',
        'classification_source_sha256': d['source_text_sha256'] if d['marketlife_type'] != 'UNKNOWN' else None,
        'observed_alongside_initial_setup': True if d['marketlife_type'] != 'UNKNOWN' else None,
        'later_snapshot_assigned_retrospectively': False, 'algorithm_inferred_type': False,
        'historical_applicability': 'Explicit operator-reported initial TYPE, not independently verified publisher payload.'
            if d['marketlife_type'] != 'UNKNOWN' else 'UNKNOWN; narrative pattern descriptions are not a dashboard TYPE.'}
        for d in decisions]


def reference_observations(decisions, source):
    o = observation(source)
    if not o: return []
    rows = []
    for snapshot in o.get('dashboard_observations', []):
        prior = [d for d in decisions if d['symbol'] == snapshot['symbol'] and d['cohort'] == 'PR9E_INITIAL_34']
        initial = prior[-1]['published_stop'] if prior else None
        entry = snapshot.get('source_reported_entry_reference')
        sign = 1 if snapshot['direction'] == 'LONG' else -1
        geometry = str(sign * (Decimal(entry) - Decimal(initial))) if entry is not None and initial else None
        rows.append({**snapshot, 'setup_id': prior[-1]['setup_id'] if prior else 'UNKNOWN',
            'initial_published_stop': initial, 'conditional_later_reference_to_initial_stop_distance': geometry,
            'entry_reference_observed_at_initial_decision': False,
            'entry_time_and_price_basis_compatibility': 'UNKNOWN', 'actual_original_risk': 'UNKNOWN',
            'decision_time_risk_evaluation': 'NOT_PERFORMED; later AHE reference is not an observed initial-decision entry.',
            'atr_normalized_risk': None, 'LAST_used_as_entry': False, 'actual_subscriber_execution': 'UNKNOWN',
            'source_chronology_warning': 'November 2 displayed current stop equals November 3 revised-to value; preserve both supplied dates without inferring order or correcting either.'})
    return rows


def study_files(annotations, hashes, source_bytes):
    _check_hashes(annotations, hashes)
    market = json.loads(annotations['market.json'])
    if annotations != annotation_files(market):
        raise ValueError('initial annotation semantic mismatch')
    decisions = initial_inventory(json.loads(source_bytes))
    if market['decisions'] != stubs(decisions):
        raise ValueError('initial source identities or clocks differ')
    result = compare(json.loads(annotations['annotations.json']), decisions)
    source = json.loads(source_bytes)
    return {**annotations, 'source.json': source_bytes, 'annotation-hashes.json': encode(hashes),
        'inventory.csv': csv_bytes(result['inventory']), 'matrix.csv': csv_bytes(result['matrix']),
        'compression.csv': csv_bytes([r for r in result['matrix'] if r['family'] == 'COMPRESSION']),
        'setup-family-evidence.csv': csv_bytes(family_register(decisions, source)),
        'reference-observations.json': encode(reference_observations(decisions, source)),
        'study.json': encode(result), 'summary.json': encode(summarize(result)),
        'manifest.json': encode({'schema_version': 'initial_study_manifest_v1', 'implementation': identity(),
            'annotations_sha256': hashes['bundle_sha256'], 'source_sha256': digest(source_bytes),
            'subsequent_stops_analyzed': False, 'risk_evaluation_performed': False})}


def load_study(path):
    files, hashes = read_bundle(path)
    annotations = {k: files[k] for k in ('market.json', 'annotations.json', 'annotation-manifest.json')}
    if files != study_files(annotations, json.loads(files['annotation-hashes.json']), files['source.json']):
        raise ValueError('initial study semantic replay mismatch')
    return files, hashes


def public_evidence(files, hashes, inputs, input_hashes):
    if any(inputs[k] != files[k] for k in ('market.json', 'source.json')):
        raise ValueError('initial inputs and study differ')
    annotations = json.loads(files['annotations.json'])
    for v in annotations['views']:
        v['rows_sha256'] = digest(encode(v.pop('rows')))
    return {**{k: files[k] for k in ('inventory.csv', 'matrix.csv', 'compression.csv', 'summary.json',
            'setup-family-evidence.csv', 'reference-observations.json')},
        'annotations-without-bars.json': encode(annotations),
        'source-initials.json': encode(initial_inventory(json.loads(files['source.json']))),
        'protocol.json': inputs['protocol.json'], 'provenance.json': inputs['provenance.json'],
        'lineage.json': encode({'study': hashes, 'inputs': input_hashes,
            'native_rows_committed': False, 'parent_source_reference': 'docs/evidence/pr9e-structural-stops-v1/source.json',
            'parent_source_sha256': json.loads(inputs['provenance.json'])['parent_source_sha256'],
            'initial_study_source_sha256': digest(files['source.json'])})}
