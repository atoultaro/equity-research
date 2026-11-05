"""Price-only PR9F hypotheses. These fixed proxies are not Grimes classifiers."""
from decimal import Decimal

from .initial_stops import compression_runs
from .structural_stops import pivots, structures

FAMILIES = ('SWING', 'PULLBACK', 'COMPLEX_PULLBACK', 'SIGNAL_BAR', 'COMPRESSION', 'VOLATILITY')
PROTOCOL = {
    'schema_version': 'initial_pattern_protocol_v3', 'families': FAMILIES,
    'chart_sessions': 60, 'minimum_chart_sessions': 20,
    'strict_swing_left_right': 3, 'local_segmentation_left_right': 1,
    'local_origin_search_sessions': 20, 'breakout_prior_sessions': 20,
    'compression': 'Retain v2 maximal strict High-Low contractions of >=3 bars ending in last20; primary by recency.',
    'complex': 'Latest distinct local favorable/adverse/favorable pivots; failed recovery below origin (inverse SHORT), then another adverse leg. No future resolution required.',
    'nested': 'Local contraction and separately identified preceding directional20 closing breakout; do not equate with complex correction.',
    'failure_test': 'Latest daily probe/reclaim of an already confirmed strict swing or already established compression boundary; select by date, never residual.',
    'larger_nested_boundaries': 'Driver candle and prior20 base opposing extremes, distinct from local contraction.',
    'primary_clock': 'LATE', 'candidate_inputs': ['admitted_OHLCV', 'direction'],
    'stops_entries_source_TYPE_and_risk_bands_used_to_select_levels': False,
    'buffers_or_ATR_multipliers_fitted': False, 'residual_match_threshold': None,
    'protective_room_is_not_invalidation': True,
    'causal_order': ['pattern_and_context', 'structural_entry_latent_not_predicted', 'protective_stop', 'risk_normalization', 'decision_filter'],
    'risk_guidance': 'User-reported preference is a downstream descriptive filter; never an entry or stop constructor.',
    'retrospective_protocol_revision': 'Local scale and pattern alternatives follow known baseline failures; not blind or prospectively validated.',
}


def missing(family, reason):
    return {'family': family, 'candidate_id': family, 'role': 'UNKNOWN', 'level': None,
        'anchor_session': None, 'confirmation_session': None, 'primary': True,
        'pattern_status': 'UNKNOWN', 'reason': reason, 'expected_invalidation': 'UNKNOWN'}


def candidate(family, role, level, session, confirmed, *, primary=False, **evidence):
    return {'family': family, 'candidate_id': role, 'role': role,
        'level': str(level), 'anchor_session': session, 'confirmation_session': confirmed,
        'primary': primary, 'pattern_status': 'OBSERVABLE_PROXY_NOT_IDENTIFIED_EXPERT_PATTERN',
        'reason': evidence.pop('reason', role),
        'expected_invalidation': 'Violation challenges this proposed structure; protective stop can allow additional room or a reclaim thesis.', **evidence}


def local_pivots(rows):
    result = []
    for i in range(1, len(rows) - 1):
        for kind, field in (('HIGH', 'high'), ('LOW', 'low')):
            v = Decimal(rows[i][field]); a = Decimal(rows[i-1][field]); b = Decimal(rows[i+1][field])
            if (v > a and v > b) if kind == 'HIGH' else (v < a and v < b):
                result.append({'kind': kind, 'index': i, 'session': rows[i]['session_date'],
                    'confirmed_session': rows[i+1]['session_date'], 'level': str(v)})
    return result


def opposing(rows, direction):
    field = 'low' if direction == 'LONG' else 'high'
    level = (min if direction == 'LONG' else max)(Decimal(r[field]) for r in rows)
    return level, [r['session_date'] for r in rows if Decimal(r[field]) == level][-1]


def pattern_candidates(rows, direction):
    if not rows: return [missing(f, 'NO_ADMITTED_PRICE_EVIDENCE') for f in FAMILIES]
    base = structures(rows, direction); strict = pivots(rows); local = local_pivots(rows)
    adverse = 'LOW' if direction == 'LONG' else 'HIGH'; favorable = 'HIGH' if direction == 'LONG' else 'LOW'
    sign = 1 if direction == 'LONG' else -1; result = []
    original = base['candidates']
    result.append({**original[0], 'family': 'SWING', 'candidate_id': 'STRICT_3_BAR_SWING',
        'role': 'STRICT_3_BAR_SWING', 'primary': True, 'pattern_status': 'CONFIRMED_PIVOT_SIGNIFICANCE_UNVERIFIED'})
    small = [p for p in local if p['kind'] == adverse]
    if small:
        p = small[-1]
        result.append(candidate('SWING', 'LOCAL_1_BAR_SWING', p['level'], p['session'], p['confirmed_session']))
    # Relevant local correction versus the preserved broad 20-bar baseline.
    origins = [p for p in local if p['kind'] == favorable and p['index'] >= len(rows) - 20]
    if origins:
        p = origins[-1]; after = rows[p['index']+1:]; level, day = opposing(after, direction)
        prior_drive = [q for q in local if q['kind'] == adverse and q['index'] < p['index']]
        result.append(candidate('PULLBACK', 'LOCAL_COUNTERLEG', level, day, rows[-1]['session_date'], primary=True,
            origin=p, prior_driving_pivot=prior_drive[-1] if prior_drive else None,
            established_trend='UNVERIFIED; use independent chart/context evidence',
            provisional_extreme=True, reason='Most recent confirmed local favorable pivot, then the full opposing extreme through the cutoff; not chosen by stop proximity.'))
    else: result.append(missing('PULLBACK', 'NO_RECENT_LOCAL_CORRECTION_ORIGIN'))
    result.append({**original[1], 'family': 'PULLBACK', 'candidate_id': 'LEGACY_20_BAR_PULLBACK',
        'role': 'LEGACY_20_BAR_PULLBACK', 'primary': False, 'pattern_status': 'DESCRIPTIVE_BASELINE'})
    # Ordered failed resumption, distinct from a pause within a driving pattern.
    triples = []
    for i in range(len(local) - 2):
        p, q, r = local[i:i+3]
        if ([x['kind'] for x in (p,q,r)] == [favorable, adverse, favorable]
                and p['index'] < q['index'] < r['index'] < len(rows)-1
                and p['index'] >= len(rows)-20 and sign*(Decimal(r['level'])-Decimal(p['level'])) < 0):
            after = rows[r['index']+1:]
            if any(sign*(Decimal(b['close'])-Decimal(a['close'])) < 0 for a,b in zip(rows[r['index']:], after)):
                triples.append((p,q,r))
    if triples:
        p,q,r = triples[-1]; correction = rows[p['index']+1:]; level, day = opposing(correction, direction)
        second_level, second_day = opposing(rows[r['index']+1:], direction)
        evidence = {'ordered_pivots': [p,q,r], 'first_leg_extreme': q['level'],
            'second_leg_extreme': str(second_level), 'second_leg_session': second_day,
            'second_leg_completion': 'PROVISIONAL; no future resolution inferred',
            'established_trend': 'UNVERIFIED; sequence alone is not expert intent'}
        result.append(candidate('COMPLEX_PULLBACK', 'FULL_TWO_LEG_CORRECTION', level, day,
            rows[-1]['session_date'], primary=True, **evidence))
        result.append(candidate('COMPLEX_PULLBACK', 'FIRST_LEG_ONLY', q['level'], q['session'],
            q['confirmed_session'], **evidence))
    else: result.append(missing('COMPLEX_PULLBACK', 'NO_ORDERED_FAILED_RESUMPTION_AND_SECOND_COUNTERLEG'))
    signals = [s for s in base['signals'] if s['direction'] == direction]
    result.append({**original[3], 'family': 'SIGNAL_BAR', 'candidate_id': 'SIGNAL_CANDLE',
        'role': 'SIGNAL_CANDLE', 'primary': True, 'pattern_status': 'CLOSING_20_BAR_BREAKOUT_PROXY'})
    if signals:
        s = signals[-1]; idx = next(i for i,r in enumerate(rows) if r['session_date'] == s['session'])
        prior = rows[idx-20:idx]; level, day = opposing(prior, direction)
        result.append(candidate('SIGNAL_BAR', 'PRE_SIGNAL_BASE', level, day, s['session'],
            interval_start=prior[0]['session_date'], interval_end=prior[-1]['session_date'],
            breakout_threshold=s['prior_boundary']))
    contractions = compression_runs(rows, direction)
    # A failure test's tested boundary must already exist before its test bar.
    anchors = [('STRICT_SWING', p['level'], p['confirmed_session']) for p in strict if p['kind'] == adverse]
    anchors += [('COMPRESSION', c['level'], c['interval_end']) for c in contractions]
    for anchor_kind in ('STRICT_SWING', 'COMPRESSION'):
        tests = []
        for bar in rows[-20:]:
            for kind, raw, known in anchors:
                level = Decimal(raw)
                if kind != anchor_kind or known >= bar['session_date']: continue
                probe = Decimal(bar['low' if direction == 'LONG' else 'high'])
                if sign*(probe-level) < 0 < sign*(Decimal(bar['close'])-level):
                    tests.append((bar['session_date'], known, probe, level))
        if tests:
            day, known, extreme, tested = max(tests, key=lambda x:(x[0],x[1]))
            result.append(candidate('SIGNAL_BAR', f'FAILURE_TEST_{anchor_kind}', extreme, day, day,
                tested_boundary=str(tested), boundary_known_on=known,
                reason='Daily probe beyond a pre-existing boundary and Close back through it; no intraday entry path inferred.'))
    # Local and larger invalidation are separate candidates, not a fitted buffer.
    for c in contractions:
        driver = [s for s in signals if s['session'] < c['interval_start']]
        context = driver[-1] if driver else None
        driver_tests = [r['session_date'] for r in rows if context and r['session_date']>context['session'] and
            sign*(Decimal(r['low' if direction=='LONG' else 'high'])-Decimal(str(context['level'])))<0]
        result.append({**c, 'role': 'LOCAL_COMPRESSION', 'pattern_status':
            'NESTED_CONTEXT_PROXY' if context and c['common_price_overlap'] and not driver_tests else
            'DRIVER_TESTED_NESTING_UNVERIFIED' if context and driver_tests else 'CONTRACTION_ONLY_NESTING_UNIDENTIFIED',
            'driver': context, 'larger_pattern_identified': context is not None,
            'driver_boundary_tests_before_cutoff':driver_tests,
            'anticipated_volatility_expansion': 'HYPOTHESIS_NOT_OBSERVED'})
        if context and c['primary']:
            idx = next(i for i,r in enumerate(rows) if r['session_date'] == context['session'])
            prior = rows[idx-20:idx]; level, day = opposing(prior, direction)
            result.append(candidate('COMPRESSION', 'LARGER_PRE_DRIVER_BASE', level, day, context['session'],
                driver=context, local_boundary=c['level'], pattern_status='NESTED_CONTEXT_PROXY'))
            result.append(candidate('COMPRESSION', 'DRIVER_CANDLE_EXTREME', context['level'], context['session'],
                context['session'], driver=context, local_boundary=c['level'], pattern_status='NESTED_CONTEXT_PROXY'))
    if not contractions: result.append(missing('COMPRESSION', 'NO_QUALIFYING_LOCAL_CONTRACTION'))
    # Fixed ten-bar range is retained only as an explicitly descriptive baseline.
    result.append({**original[2], 'family': 'COMPRESSION', 'candidate_id': 'LEGACY_TEN_BAR_BOX',
        'role': 'LEGACY_TEN_BAR_BOX', 'primary': False, 'pattern_status': 'BOX_NOT_PROOF_OF_CONSOLIDATION'})
    result.append(missing('VOLATILITY', 'No independently specified entry/anchor/multiplier; do not manufacture a volatility stop.'))
    return result
