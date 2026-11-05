"""Reconciled source facts, distinct pattern structures and non-inverted risk."""
from copy import deepcopy
from datetime import date,timedelta
from decimal import Decimal
import inspect
import json
from pathlib import Path

import pytest

from test_prospective_predictions import archive
from equity_research.ingestion.storage import encode,read_bundle,write_bundle
from equity_research.initial_stop_log import parse_log,reconcile
from equity_research.initial_pattern_candidates import pattern_candidates,local_pivots
from equity_research import initial_pattern_study as study

ROOT = Path(__file__).resolve().parents[1]


def proof(path):
    f,h=read_bundle(path);return {'files':{k:v.decode() for k,v in f.items()},'hashes':h}


@pytest.fixture
def actual_source():
    return {'parent_source':json.loads((ROOT/'docs/evidence/pr9e-structural-stops-v1/source.json').read_bytes()),
        'expanded_log_proof':proof(ROOT/'docs/evidence/pr9f-expanded-source-20261103-v1'),
        'earlier_observation_proof':proof(ROOT/'docs/evidence/pr9f-operator-source-20261103-v1'),
        'risk_guidance_proof':proof(ROOT/'docs/evidence/pr9f-risk-guidance-20261103-v1')}


def make_rows(closes,ranges=None):
    ranges=ranges or [1]*len(closes)
    return [{'session_date':(date(2026,1,1)+timedelta(days=i)).isoformat(),
        'open':str(c),'close':str(c),'high':str(Decimal(str(c))+Decimal(str(r))/2),
        'low':str(Decimal(str(c))-Decimal(str(r))/2)} for i,(c,r) in enumerate(zip(closes,ranges))]


def test_full_118_log_reconciles_42_initials_not_triggers_or_current_stops(actual_source):
    r=reconcile(actual_source)
    assert r['summary']['visible_rows']==118 and r['summary']['reconciled_initial_stops']==42
    assert r['summary']['overlapping_new_setup_rows']==28 and r['summary']['additional_opening_episodes']==8
    assert r['summary']['directions']=={'LONG':22,'SHORT':20}
    assert r['summary']['event_types']=={'NEW_SETUP':36,'TRIGGERED':15,'STOP_MOVED':33,'STOPPED_OUT':5,'DROPPED':29}
    assert r['unmatched_event_ids']==[] and len({d['setup_id'] for d in r['inventory']})==42
    ids={d['setup_id']:d for d in r['inventory']}
    assert ids['SLB-001']['published_stop']=='51.10' and ids['SLB-002']['published_stop']=='51.90'
    assert ids['GME-001']['direction']=='LONG' and ids['GME-002']['direction']=='SHORT'
    assert ids['DUK-001']['published_stop']=='122.90' and ids['CRWV-001']['published_stop']=='66.20'
    assert len([a for a in r['aliases'] if a['kind']=='EARLIER_SUMMARY_DATE_ROLE_DIFFERENCE'])==3
    assert ids['SLB-002']['reported_log_date']=='2026-11-02'
    slb=[e for e in r['events'] if e['symbol']=='SLB']
    assert {e['setup_id'] for e in slb if e['kind']=='STOPPED_OUT'}=={'SLB-001'}
    assert all(e['actual_subscriber_execution']=='UNKNOWN' for e in r['events'])
    assert sum(d['marketlife_type']!='UNKNOWN' for d in r['inventory'])==8


def test_old_cutoffs_preserved_and_snapshot_hour_not_backfilled(actual_source):
    from equity_research.initial_stops import initial_inventory
    r=reconcile(actual_source);old=initial_inventory(actual_source['parent_source'])
    assert [d['cutoffs'] for d in r['inventory'][:34]]==[d['cutoffs'] for d in old]
    oct30=next(d for d in r['inventory'] if d['symbol']=='AXGN')
    assert '00:00:00' in oct30['cutoffs']['EARLY'] and oct30['publication']['published_at'] is None
    nov2=next(d for d in r['inventory'] if d['setup_id']=='SLB-002')
    assert nov2['publication']['intended_trading_session']=='2026-11-03'
    assert nov2['cutoffs']['EARLY']=='2026-11-02T22:00:00+00:00'
    assert nov2['publication']['publication_precision']=='OPERATOR_REPORTED_LATEST_BATCH_PUBLICATION_HOUR'


def test_log_parser_fails_on_unparsed_rows_duplicate_or_wrong_heading():
    valid='Last 14 days · 1 changes\nDay\tTicker\tChange\nMon Nov 2\tABC\ttriggered long; stop 10.00\n'
    assert parse_log(valid.encode())[0]['kind']=='TRIGGERED'
    with pytest.raises(ValueError,match='row count'):parse_log(valid.replace('1 changes','2 changes').encode())
    with pytest.raises(ValueError,match='unparsed'):parse_log(valid.replace('triggered long; stop 10.00','made something up').encode())
    duplicate=valid.replace('1 changes','2 changes')+'Mon Nov 2\tABC\ttriggered long; stop 10.00\n'
    with pytest.raises(ValueError,match='duplicate'):parse_log(duplicate.encode())


def test_complex_second_leg_and_first_leg_have_different_invalidation():
    rows=make_rows([100]*20+[103,110,104,90,96,105,98,85,89])
    cs=pattern_candidates(rows,'LONG')
    full=next(c for c in cs if c['role']=='FULL_TWO_LEG_CORRECTION')
    first=next(c for c in cs if c['role']=='FIRST_LEG_ONLY')
    assert full['level']=='84.5' and first['level']=='89.5'
    assert [p['kind'] for p in full['ordered_pivots']]==['HIGH','LOW','HIGH']
    assert Decimal(full['ordered_pivots'][-1]['level'])<Decimal(full['ordered_pivots'][0]['level'])
    assert 'PROVISIONAL' in full['second_leg_completion']


def test_nested_drive_and_small_consolidation_are_not_complex_correction():
    rows=make_rows([100]*20+[103,105,105,105],[2]*20+[4,5,3,2])
    cs=pattern_candidates(rows,'LONG')
    local=next(c for c in cs if c['family']=='COMPRESSION' and c['primary'])
    assert local['pattern_status']=='NESTED_CONTEXT_PROXY'
    assert local['driver']['session']==rows[20]['session_date']
    assert next(c for c in cs if c['family']=='COMPLEX_PULLBACK' and c['primary'])['level'] is None
    assert any(c['role']=='LARGER_PRE_DRIVER_BASE' for c in cs)


def test_failure_test_boundary_exists_before_probe_and_uses_test_extreme():
    rows=make_rows([100]*3+[101],[12,9,6,10]);rows[-1].update(open='100',low='92',high='102')
    c=next(c for c in pattern_candidates(rows,'LONG') if c['role']=='FAILURE_TEST_COMPRESSION')
    assert c['tested_boundary']=='94' and c['level']=='92'
    assert c['boundary_known_on']<c['confirmation_session']


def test_local_pivot_requires_right_confirmation_and_generator_has_no_risk_or_stop_input():
    rows=make_rows([100,110,105])
    assert not local_pivots(rows[:2]) and local_pivots(rows)[0]['confirmed_session']==rows[2]['session_date']
    assert list(inspect.signature(pattern_candidates).parameters)==['rows','direction']


@pytest.mark.parametrize('number,band',[(None,'UNKNOWN'),(.79,'BELOW_0_8'),(.8,'0_8_THROUGH_1_4'),
    (1.4,'0_8_THROUGH_1_4'),(1.41,'ABOVE_1_4_THROUGH_2'),(2,'ABOVE_1_4_THROUGH_2'),(2.01,'ABOVE_2')])
def test_risk_bands_are_descriptive(number,band):
    assert study.risk_band(number)==band


@pytest.fixture
def small_inputs(tmp_path,archive):
    parent={'original_alerts':archive['alerts'],'batches':[],'calendar':archive['calendar'],
        'source_asof':'2026-10-26T23:00:00+00:00','native_archive_sha256':'synthetic'}
    f,h=read_bundle(ROOT/'docs/evidence/pr9f-expanded-source-20261103-v1')
    tiny='Last 14 days · 3 changes\nDay\tTicker\tChange\nTue Oct 20\tAAPL\tdropped from potential longs\nFri Oct 30\tMSFT\tnew long pullback setup, stop 100.00\nMon Nov 2\tBA\tnew short tight pullback setup, stop 177.30\n'
    f['change-log-20261102.txt']=tiny.encode()
    meta=json.loads(f['provenance.json']);meta['source_log_label']='Last 14 days · 3 changes';f['provenance.json']=encode(meta)
    eh=write_bundle(tmp_path/'tiny-log',f)
    earlier={'observation.json':encode({'actions':[],'dashboard_observations':[]})}
    oh=write_bundle(tmp_path/'tiny-earlier',earlier)
    source={'parent_source':parent,'expanded_log_proof':{'files':{k:v.decode() for k,v in f.items()},'hashes':eh},
        'earlier_observation_proof':{'files':{k:v.decode() for k,v in earlier.items()},'hashes':oh},
        'risk_guidance_proof':proof(ROOT/'docs/evidence/pr9f-risk-guidance-20261103-v1')}
    market={k:archive[k] for k in ('prices','coverage','calendar')}
    from equity_research.initial_stops import stubs
    market['decisions']=stubs(study.inventory(source))
    return market,source


def test_pattern_semantic_replay_and_resealed_candidate_rejected(tmp_path,small_inputs):
    market,source=small_inputs
    af=study.annotation_files(market);ah=write_bundle(tmp_path/'ann',af)
    files=study.study_files(af,ah,encode(source));h=write_bundle(tmp_path/'study',files)
    assert study.load_study(tmp_path/'study')==(files,h)
    assert write_bundle(tmp_path/'replay',study.load_study(tmp_path/'study')[0])==h
    changed=deepcopy(files);x=json.loads(changed['study.json']);x['matrix'][0]['published_initial_stop']='1.00';changed['study.json']=encode(x)
    write_bundle(tmp_path/'resealed',changed)
    with pytest.raises(ValueError,match='semantic replay'):study.load_study(tmp_path/'resealed')
    altered_af=deepcopy(af);x=json.loads(altered_af['annotations.json'])
    x['views'][0]['candidates'][0]['level']='1.00';altered_af['annotations.json']=encode(x)
    bad_hashes=write_bundle(tmp_path/'resealed-annotations',altered_af)
    with pytest.raises(ValueError,match='annotation semantic'):
        study.study_files(altered_af,bad_hashes,encode(source))
    assert len(json.loads(files['study.json'])['inventory'])==3
    assert len(json.loads(files['risk-context.json'])['observations'])==0


def test_future_poison_source_type_and_preferred_risk_cannot_select_candidates(small_inputs):
    market,source=small_inputs
    market['decisions']=market['decisions'][:1];before=study.annotate(market)
    for rows in market['prices'].values():
        for r in rows:
            if r['session_date']>'2026-10-16':r.update(high='POISON',close='-1')
    assert study.annotate(market)==before
    poisoned=deepcopy(market);poisoned['decisions'][0]['desired_risk_atr']=1
    with pytest.raises(ValueError,match='stop-masked'):study.annotate(poisoned)


def test_new_unknown_prices_cannot_reuse_an_older_episode_chart(actual_source):
    # Source scope validation is independent of price availability.
    r=reconcile(actual_source)
    new=[d for d in r['inventory'] if d['cohort']=='EXPANDED_LOG_NEW']
    assert len(new)==8 and all(d['entry_to_initial_stop_risk']=='UNKNOWN' for d in new)
    assert all(d['marketlife_type']!='UNKNOWN' for d in new)


def test_committed_reconciled_population_and_risk_provenance(actual_source):
    import csv,io
    files,_=read_bundle(ROOT/'docs/evidence/pr9f-initial-patterns-v2')
    old,_=read_bundle(ROOT/'docs/evidence/pr9f-original34-patterns-v2')
    rows=list(csv.DictReader(io.StringIO(files['inventory.csv'].decode())))
    observations=list(csv.DictReader(io.StringIO(files['initial-observations.csv'].decode())))
    expected=reconcile(actual_source)['inventory']
    assert len(rows)==len(observations)==len(expected)==42
    assert [(r['setup_id'],r['published_stop'],r['marketlife_type']) for r in rows]==[
        (d['setup_id'],d['published_stop'],d['marketlife_type']) for d in expected]
    assert len({r['decision_id'] for r in observations})==42
    matrix=list(csv.DictReader(io.StringIO(files['matrix.csv'].decode())))
    old_matrix=list(csv.DictReader(io.StringIO(old['matrix.csv'].decode())))
    assert [r for r in matrix if r['cohort']=='PR9E_INITIAL_34']==old_matrix
    for d in expected:
        for clock in ('EARLY','CLOSE_BOUNDARY','LATE'):
            subset=[r for r in matrix if r['decision_id']==d['decision_id'] and clock in json.loads(r['scenarios']) and r['primary']=='True']
            assert len(subset)==6 and {r['family'] for r in subset}==set(study.FAMILIES)
            if d['cohort']=='EXPANDED_LOG_NEW':assert all(r['level']=='' for r in subset)
    risk=json.loads(files['risk-context.json'])
    assert risk['fully_timed_valid_observations']==0 and risk['triggered_log_rows']==15
    assert risk['guidance']['attribution'].startswith('USER_REPORTED_')
    refs={r['symbol']:r for r in risk['observations']}
    assert refs['DUK']['conditional_ATR_session']=='2026-10-28'
    assert refs['CRWV']['conditional_ATR_session']=='2026-10-29'
    for symbol,distance in [('DUK','2.22'),('CRWV','10.08')]:
        r=refs[symbol]
        assert r['retrospective_reference_to_first_stop_distance']==distance
        assert r['observed_risk_band']=='UNKNOWN' and not r['valid_fully_timed_entry_risk_observation']
        assert not r['LAST_used_as_entry'] and not r['entry_reference_observed_at_initial_decision']
        assert r['conditional_reference_risk_ATR14']==pytest.approx(float(distance)/r['conditional_ATR14'])
