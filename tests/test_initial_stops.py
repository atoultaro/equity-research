"""PR9F: initial-only scope, causal compression and semantic offline replay."""
from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path

import pytest

from test_prospective_predictions import archive
from equity_research.ingestion.storage import encode, read_bundle, write_bundle
from equity_research.initial_stops import (PROTOCOL, FAMILIES, initial_inventory, project, prepare,
    compression_runs, annotate, compare, summarize, annotation_files, study_files, load_study)
from equity_research.initial_stops import family_register, reference_observations


def bars(ranges, centers=None):
    centers = centers or [100] * len(ranges)
    return [{'session_date': f'2026-01-{i + 1:02d}', 'open': str(c), 'close': str(c),
        'high': str(Decimal(str(c)) + Decimal(str(r)) / 2),
        'low': str(Decimal(str(c)) - Decimal(str(r)) / 2)} for i, (r, c) in enumerate(zip(ranges, centers))]


@pytest.fixture
def inputs(archive, tmp_path):
    parent = {'market.json': encode({k: archive[k] for k in ('prices', 'coverage', 'calendar')}),
        'source.json': encode({'original_alerts': archive['alerts'], 'batches': [],
            'calendar': archive['calendar'], 'source_asof': '2026-10-26T23:00:00+00:00',
            'native_archive_sha256': 'synthetic'})}
    ph = write_bundle(tmp_path / 'parent', parent)
    projected = project(parent, ph)
    return projected, json.loads(projected['market.json']), json.loads(projected['source.json']), ph


def test_initial_projection_excludes_revisions_but_preserves_parent_bytes(inputs, tmp_path):
    files, market, source, ph = inputs
    ds = initial_inventory(source)
    assert len(ds) == len(market['decisions']) == 1
    assert ds[0]['decision_type'] == 'INITIAL' and ds[0]['published_stop'] == '95.00'
    assert 'previous_stop' not in ds[0] and 'revision_role' not in ds[0]
    assert 'published_stop' not in json.dumps(market)
    assert files == prepare(tmp_path / 'parent', ph['bundle_sha256'])
    assert read_bundle(tmp_path / 'parent')[0]['source.json'] == files['source.json']
    with pytest.raises(ValueError, match='parent hash'):
        prepare(tmp_path / 'parent', 'not the parent')


@pytest.mark.parametrize('direction,levels', [('LONG', ['94', '96.5']), ('SHORT', ['106', '103.5'])])
def test_maximal_contractions_use_whole_interval_boundary_and_recency(direction, levels):
    rows = bars([12, 9, 6, 7, 5, 3, 8])
    runs = compression_runs(rows, direction)
    assert [r['level'] for r in runs] == levels
    assert [r['interval_sessions'] for r in runs] == [
        ['2026-01-01', '2026-01-02', '2026-01-03'],
        ['2026-01-04', '2026-01-05', '2026-01-06']]
    assert [r['primary'] for r in runs] == [False, True]
    assert [[Decimal(x) for x in r['daily_ranges']] for r in runs] == [[12, 9, 6], [7, 5, 3]]
    assert all(r['common_price_overlap'] for r in runs)
    assert runs[-1]['sessions_since_end'] == 1 and not runs[-1]['ending_at_latest_bar']


def test_equal_ranges_break_runs_and_nested_suffixes_do_not_inflate_evidence():
    assert [r['bars'] for r in compression_runs(bars([12, 9, 6, 3]), 'LONG')] == [4]
    assert [r['bars'] for r in compression_runs(bars([12, 9, 6, 6, 4, 2]), 'LONG')] == [3, 3]
    assert compression_runs(bars([4, 4, 4, 4]), 'LONG') == []
    assert compression_runs(bars([9, 6]), 'LONG') == []


def test_range_contraction_is_not_automatically_shared_price_support():
    row = compression_runs(bars([12, 9, 6], [100, 120, 140]), 'LONG')[0]
    assert list(map(Decimal, row['daily_ranges'])) == [12, 9, 6]
    assert row['common_price_overlap'] is False and row['box_width_mean_range'] > 4


def test_runs_ending_outside_the_declared_search_window_are_not_candidates():
    rows = bars([12, 9, 6] + [8] * 21)
    assert compression_runs(rows, 'SHORT') == []


def test_atr_is_not_a_constructor_input_and_stops_cannot_enter_annotations(inputs):
    _, market, source, _ = inputs
    a = annotate(market); ds = initial_inventory(source)
    changed = deepcopy(ds); changed[0]['published_stop'] = '1.00'
    assert compare(a, ds)['matrix'] != compare(a, changed)['matrix']
    assert a == annotate(market)
    poisoned = deepcopy(market); poisoned['decisions'][0]['published_stop'] = '1.00'
    with pytest.raises(ValueError, match='stop-masked INITIAL'):
        annotate(poisoned)
    poisoned = deepcopy(market); poisoned['decisions'][0]['decision_type'] = 'REVISION'
    with pytest.raises(ValueError, match='INITIAL'):
        annotate(poisoned)
    changed[0]['decision_type'] = 'REVISION'
    with pytest.raises(ValueError, match='revisions'):
        compare(a, changed)
    assert not PROTOCOL['risk_evaluation_performed']


def test_future_prices_and_atr_poison_cannot_change_earlier_candidates(inputs):
    _, market, _, _ = inputs
    before = annotate(market)
    for rows in market['prices'].values():
        for row in rows:
            if row['session_date'] > '2026-10-16':
                row.update(high='POISON', close='-1', volume=None)
    assert annotate(market) == before
    view = before['views'][0]
    candidate_copy = deepcopy(view['candidates'])
    view['features']['atr14']['value'] = 9999
    from equity_research.initial_stops import candidates
    # Recompute from the existing price-only admission, using inherited base candidates.
    from equity_research.structural_stops import chart_view
    v = chart_view(market, 'AAPL', 'LONG', market['decisions'][0]['cutoffs']['LATE'])
    v['features']['atr14']['value'] = 9999
    assert candidates(v) == candidate_copy


@pytest.mark.parametrize('direction,stop,level,expected', [
    ('LONG', '93.90', '94', '0.10'), ('SHORT', '106.10', '106', '0.10'),
    ('LONG', '94.10', '94', '-0.10')])
def test_signed_structural_residual_is_not_entry_risk(direction, stop, level, expected, inputs):
    _, market, source, _ = inputs
    ann = annotate(market); ds = initial_inventory(source)
    ds[0].update(direction=direction, published_stop=stop)
    ann['views'][0]['candidates'] = [{'family': 'SWING', 'candidate_id': 'test',
        'level': level, 'primary': True, 'anchor_session': '2026-10-01'}]
    row = compare(ann, ds)['matrix'][0]
    assert row['buffer_price'] == expected
    assert Decimal(row['buffer_research_ticks']) == Decimal(expected) * 100
    assert row['buffer_ATR14'] == float(expected) / row['atr14_normalization']
    assert 'risk' not in json.dumps(row)


def test_already_breached_compression_is_not_unbroken_support(inputs):
    _, market, source, _ = inputs
    ann = annotate(market); v = ann['views'][0]
    rows = bars([12, 9, 6, 8], [100, 100, 100, 95])
    c = compression_runs(rows, 'LONG')[0]
    v.update(rows=rows, candidates=[c], features={'close': {'value': 95}, 'atr14': {'value': 2}})
    ds = initial_inventory(source); ds[0]['published_stop'] = '93.00'
    row = compare(ann, ds)['matrix'][0]
    assert row['weak_geometry'] and not row['structural_proxy_compatible']
    assert row['anchor_breaches_after_confirmation'] == ['2026-01-04']
    assert row['verdict'] == 'ALREADY_BREACHED_ANCHOR'


def test_nonoverlapping_contraction_is_not_a_supported_boundary(inputs):
    _, market, source, _ = inputs
    ann = annotate(market); v = ann['views'][0]
    rows = bars([12, 9, 6], [100, 120, 140]); c = compression_runs(rows, 'LONG')[0]
    v.update(rows=rows, candidates=[c], features={'close': {'value': 140}, 'atr14': {'value': 2}})
    ds = initial_inventory(source); ds[0]['published_stop'] = '93.00'
    row = compare(ann, ds)['matrix'][0]
    assert row['weak_geometry'] and not row['structural_proxy_compatible']
    assert row['verdict'] == 'NO_SHARED_COMPRESSION_PRICE_REGION'


def test_breakout_signal_candle_and_preceding_base_are_distinct(inputs):
    from equity_research.structural_stops import chart_view, structures
    from equity_research.initial_stops import candidates
    _, market, _, _ = inputs
    v = chart_view(market, 'AAPL', 'LONG', market['decisions'][0]['cutoffs']['LATE'])
    v['rows'][-10]['low'] = '95.00'
    v['rows'][-1].update(open='109', high='111', low='107', close='110')
    v.update(structures(v['rows'], 'LONG'))
    rows = [c for c in candidates(v) if c['family'] == 'SIGNAL_BAR']
    assert len(rows) == 2
    assert rows[0]['structure_role'] == 'SIGNAL_CANDLE' and rows[0]['level'] == '107'
    assert rows[1]['structure_role'] == 'PRE_SIGNAL_20_BAR_BASE' and rows[1]['level'] == '95.00'
    assert rows[0]['primary'] and not rows[1]['primary']


def test_missing_required_session_yields_all_families_unknown_and_short_history_remains(inputs):
    _, market, _, _ = inputs
    first = annotate(market)['views'][0]
    market['prices']['AAPL'] = [r for r in market['prices']['AAPL'] if r['session_date'] != '2026-10-15']
    bad = annotate(market)['views'][0]
    assert bad['status'] == 'UNAVAILABLE_MISSING_REQUIRED_SESSION'
    assert {r['family'] for r in bad['candidates']} == set(FAMILIES)
    assert all(r['level'] is None for r in bad['candidates'])
    market['prices']['AAPL'] = first['rows'][-25:]
    short = annotate(market)['views'][0]
    assert short['status'] == 'AVAILABLE_SHORT_HISTORY'
    assert short['features']['atr14'] == first['features']['atr14']


def test_semantic_replay_rejects_resealed_derived_candidates_and_results(tmp_path, inputs):
    files, market, source, _ = inputs
    af = annotation_files(market); ah = write_bundle(tmp_path / 'annotations', af)
    result = study_files(af, ah, encode(source)); h = write_bundle(tmp_path / 'study', result)
    assert load_study(tmp_path / 'study') == (result, h)
    assert write_bundle(tmp_path / 'replay', load_study(tmp_path / 'study')[0]) == h
    with pytest.raises(FileExistsError): write_bundle(tmp_path / 'study', result)
    altered = deepcopy(result); x = json.loads(altered['study.json'])
    x['matrix'][0]['published_initial_stop'] = '1.00'; altered['study.json'] = encode(x)
    write_bundle(tmp_path / 'bad-study', altered)
    with pytest.raises(ValueError, match='semantic replay'):
        load_study(tmp_path / 'bad-study')
    a = json.loads(af['annotations.json']); a['views'][0]['candidates'][0]['level'] = '1.00'
    af['annotations.json'] = encode(a); bh = write_bundle(tmp_path / 'bad-annotations', af)
    with pytest.raises(ValueError, match='annotation semantic'):
        study_files(af, bh, encode(source))


def test_primary_summary_counts_decisions_not_alternative_intervals(inputs):
    _, market, source, _ = inputs
    ann = annotate(market); ds = initial_inventory(source)
    c = compression_runs(bars([12, 9, 6, 7, 5, 3, 8]), 'LONG')
    v = ann['views'][0]; v['candidates'] = [r for r in v['candidates'] if r['family'] != 'COMPRESSION'] + c
    s = summarize(compare(ann, ds))
    assert s['initial_decisions'] == s['episodes'] == 1
    assert s['subsequent_stop_decisions_analyzed'] == 0
    for clock in s['clocks'].values():
        assert clock['decisions'] == 1
        assert all(r['decisions'] == 1 for r in clock['primary_comparison'] if r['direction'] == 'ALL')


@pytest.fixture
def november_source():
    root = Path(__file__).resolve().parents[1]
    evidence, hashes = read_bundle(root / 'docs/evidence/pr9f-operator-source-20261103-v1')
    return {'parent_source': json.loads((root / 'docs/evidence/pr9e-structural-stops-v1/source.json').read_bytes()),
        'november_observation_proof': {'files': {k: v.decode() for k, v in evidence.items()}, 'hashes': hashes}}


def test_observed_population_37_distinct_episodes_and_34_unchanged(november_source):
    before = initial_inventory(november_source['parent_source']); after = initial_inventory(november_source)
    assert len(before) == 34 and after[:34] == before and len(after) == 37
    assert len({r['setup_id'] for r in after}) == len({r['decision_id'] for r in after}) == 37
    assert sum(r['direction'] == 'LONG' for r in after) == 18
    assert sum(r['direction'] == 'SHORT' for r in after) == 19
    new = {r['symbol']: r for r in after[34:]}
    assert new['GME']['setup_id'] == 'GME-002' and new['SLB']['setup_id'] == 'SLB-002'
    assert new['AVGO']['published_stop'] == '335.40'
    assert new['GME']['published_stop'] == '24.90'
    assert new['SLB']['published_stop'] == '51.90'
    assert all(r['observed_publication'] == 'UNKNOWN' and r['publication']['publication_precision'] == 'DATE' for r in after[34:])
    assert all('2026-11-03T21' not in t for r in after[34:] for t in r['cutoffs'].values())
    assert all(r['actual_subscriber_execution'] == r['entry_to_initial_stop_risk'] == 'UNKNOWN' for r in after)


def test_all_thirteen_source_actions_preserved_but_only_three_enter_analysis(november_source):
    from equity_research.initial_stops import observation
    o = observation(november_source)
    assert len(o['actions']) == 13
    assert len([a for a in o['actions'] if a['kind'] == 'SOURCE_TRACKED_STOP_OUT']) == 2
    assert len([a for a in o['actions'] if a['kind'] == 'STOP_REVISION']) == 5
    assert len([a for a in o['actions'] if a['kind'] == 'DROPPED']) == 3
    assert [r['symbol'] for r in initial_inventory(november_source)[34:]] == ['AVGO', 'GME', 'SLB']
    assert o['market_context']['verified_market_observation'] is False
    assert o['actual_subscriber_executions'] == 'UNKNOWN'


def test_family_evidence_does_not_backfill_old_episodes_or_dashboard_entries(november_source):
    ds = initial_inventory(november_source); register = family_register(ds, november_source)
    assert len(register) == 37 and all(r['observed_marketlife_type'] == 'UNKNOWN' for r in register[:34])
    assert [r['observed_marketlife_type'] for r in register[34:]] == ['Nested pullback', 'Nested pullback', 'Pullback']
    assert all(r['source_snapshot_date'] == '2026-11-03' and r['observed_alongside_initial_setup'] for r in register[34:])
    references = {r['symbol']: r for r in reference_observations(ds, november_source)}
    assert references['DUK']['initial_published_stop'] == '122.90'
    assert references['DUK']['current_published_stop'] == '126.60'
    assert references['DUK']['conditional_later_reference_to_initial_stop_distance'] == '2.22'
    assert references['CRWV']['initial_published_stop'] == '66.20'
    assert references['CRWV']['conditional_later_reference_to_initial_stop_distance'] == '10.08'
    assert all(r['entry_reference_type'] == 'AHE' and r['actual_original_risk'] == 'UNKNOWN' and
        not r['LAST_used_as_entry'] and not r['entry_reference_observed_at_initial_decision'] for r in references.values())


def test_november_proof_integrity_and_prior_stopout_reconciliation(tmp_path, november_source):
    bad = deepcopy(november_source)
    bad['november_observation_proof']['files']['observation.json'] += ' '
    with pytest.raises(ValueError): initial_inventory(bad)
    bad = deepcopy(november_source); proof = bad['november_observation_proof']
    o = json.loads(proof['files']['observation.json'])
    o['actions'] = [a for a in o['actions'] if not (a['symbol'] == 'SLB' and a['kind'] == 'SOURCE_TRACKED_STOP_OUT')]
    files = {k: v.encode() for k, v in proof['files'].items()}; files['observation.json'] = encode(o)
    proof['files'] = {k: v.decode() for k, v in files.items()}; proof['hashes'] = write_bundle(tmp_path / 'changed', files)
    with pytest.raises(ValueError, match='termination evidence'): initial_inventory(bad)


def test_initial_renderer_is_reproducible_and_masked(tmp_path, inputs):
    pytest.importorskip('matplotlib')
    from equity_research.initial_stop_charts import charts
    _, market, source, _ = inputs
    af = annotation_files(market); ah = write_bundle(tmp_path / 'render-annotations', af)
    files = study_files(af, ah, encode(source)); h = write_bundle(tmp_path / 'render-study', files)
    first = charts(files, h)
    assert first == charts(files, h)
    assert b'initial stop 95.00' in first['i000-AAPL.svg']
    masked = charts(files, h, masked=True)['i000-AAPL-masked.svg']
    assert b'STOP MASKED' in masked and b'initial stop 95.00' not in masked
    assert all(line == line.rstrip() for line in first['i000-AAPL.svg'].splitlines())
