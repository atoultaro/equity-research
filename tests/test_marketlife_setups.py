"""Synthetic source/price fixtures; no subscriber or broker connection."""
from copy import deepcopy
from datetime import UTC,datetime
import json
from pathlib import Path
import subprocess
import sys

import pytest

from test_prospective_predictions import archive,alert
from equity_research.ingestion.storage import encode,read_bundle,write_bundle
from equity_research.marketlife_setups import source_inputs,timing_scenarios,opportunity_ledger,eligible_at
from equity_research.marketlife_research import candidate,subscriber_path,snapshot
from equity_research.marketlife_workflow import audit,alert_manifest,registration_payload,load_registration,freeze_study,load_study
from equity_research.reconstruction.admission import Evidence


def additions(*alerts):
    return {'schema_version':'marketlife_operator_alerts_v1','captured_at':'2026-10-26T23:00:00+00:00',
        'alerts':[{**a,'source_date':a['published_at'][:10] if a['published_at'] else '2026-10-20'} for a in alerts]}


def ledger(archive,operator=None,variant='LATE'):
    e,m,_=source_inputs(archive,operator);c=next(c for c in timing_scenarios(m,archive['calendar']) if c['name']==variant)
    return opportunity_ledger(e,m,c)


def evidence(archive):return Evidence(archive['prices'],archive['coverage'],archive['calendar'],'2026-10-26T23:00:00+00:00')


def test_enterable_revision_creates_immutable_new_opportunity_after_prior_stopout(archive):
    l=ledger(archive);first,second=l['opportunities']
    assert first['published_stop']=='95.00' and second['published_stop']=='90.00'
    assert first['superseded_by']==second['opportunity_id'] and first['effective_until']==second['effective_from']
    assert [o['opportunity_version'] for o in l['opportunities']]==[1,2]
    ev=evidence(archive)
    path=subscriber_path(first,candidate(first,ev,archive['calendar'],'2026-10-26'),ev,archive['calendar'],'2026-10-26','HARD')
    assert path['first_stop_session']=='2026-10-19' and path['published_stop_fixed']=='95.00'
    assert eligible_at(l,'AAPL-001',second['effective_from'])==[second]
    assert second['observed_execution']=='UNKNOWN' and second['actual_entry'] is None
    path2=subscriber_path(second,candidate(second,ev,archive['calendar'],'2026-10-26'),ev,archive['calendar'],'2026-10-26','HARD')
    assert path2['published_stop_fixed']=='90.00' and path2['state']=='HYPOTHETICALLY_REMAINS_PROTECTED_AT_DATA_END'
    assert l['setups'][0]['setup_status']=='ACTIVE'


def test_underway_suspends_eligibility_without_exit_and_return_uses_latest_stop(archive):
    o=additions(alert('c',0,'2026-10-20T18:00:00-04:00',stops='AAPL stop moved to 91.00 from 90.00',setups='AAPL setup changed to long (underway) from long'),
        alert('d',1,'2026-10-21T18:00:00-04:00',stops='AAPL stop moved to 92.00 from 91.00'),
        alert('e',2,'2026-10-22T18:00:00-04:00',setups='AAPL setup changed to long from long (underway)'))
    l=ledger(archive,o);opps=l['opportunities']
    assert len(opps)==4
    assert not opps[2]['entry_eligible'] and opps[2]['effective_from']==opps[2]['effective_until']
    assert not eligible_at(l,'AAPL-001','2026-10-21T23:00:00+00:00')
    assert opps[-1]['published_stop']=='92.00' and opps[-1]['entry_eligible']
    assert l['setups'][0]['entry_state']=='ENTERABLE' and l['setups'][0]['observed_execution']=='UNKNOWN'
    assert opps[2]['observed_execution']=='UNKNOWN'


def test_dropped_is_not_executed_sale_and_later_added_begins_new_episode(archive):
    archive['alerts']['alerts']=archive['alerts']['alerts'][:1]
    archive['alerts']['alerts'][0]['text']=archive['alerts']['alerts'][0]['text'].replace('95.00','90.00')
    o=additions(alert('c',0,'2026-10-20T18:00:00-04:00',dropped='AAPL dropped from long'),
        alert('d',1,'2026-10-21T18:00:00-04:00',added='AAPL added long with stop 95.00'))
    l=ledger(archive,o);assert [s['setup_id'] for s in l['setups']]==['AAPL-001','AAPL-002']
    assert l['setups'][0]['setup_status']=='DROPPED' and l['setups'][0]['observed_execution']=='UNKNOWN'
    op=l['opportunities'][0];ev=evidence(archive)
    p=subscriber_path(op,candidate(op,ev,archive['calendar'],'2026-10-26'),ev,archive['calendar'],'2026-10-26','HARD')
    assert p['state']=='HYPOTHETICALLY_REMAINS_PROTECTED_AT_DATA_END' and p['actual_exit'] is None
    assert not eligible_at(l,'AAPL-001','2026-10-21T23:00:00+00:00')
    assert eligible_at(l,'AAPL-002','2026-10-21T23:00:00+00:00')


def test_opportunities_respect_date_bounds_and_do_not_claim_publication_times(archive):
    a=alert('date-only',0,None,stops='AAPL stop moved to 91.00 from 90.00');a['publication_precision']='DATE'
    o=additions(a)
    e,m,_=source_inputs(archive,o)
    for c in timing_scenarios(m,archive['calendar']):
        l=opportunity_ledger(e,m,c);op=l['opportunities'][-1]
        assert op['source_published_at'] is None
        assert m[-1]['lower']<=op['effective_from'] # same zone in DATE cases
        assert op['publication_bounds']['bound_kind'].startswith('OPERATOR_DATE')
        construct=candidate(op,evidence(archive),archive['calendar'],'2026-10-26')
        if construct['next_open']:assert datetime.fromisoformat(construct['next_open']['at'])>datetime.fromisoformat(op['effective_from'])


def test_atr_and_close_only_use_completed_available_sessions(archive):
    ev=evidence(archive)
    before=snapshot(ev,'AAPL','2026-10-19T20:30:00+00:00','95','LONG')
    after=snapshot(ev,'AAPL','2026-10-19T21:01:00+00:00','95','LONG')
    assert before['feature_session']=='2026-10-16' and after['feature_session']=='2026-10-19'
    assert before['atr14']!=after['atr14']
    poisoned=deepcopy(archive)
    for r in poisoned['prices']['AAPL']:
        if r['session_date']>='2026-10-19':r.update(open='200',high='210',low='190',close='205')
    assert snapshot(evidence(poisoned),'AAPL','2026-10-19T20:30:00+00:00','95','LONG')==before
    missing=deepcopy(archive);missing['prices']['AAPL']=[r for r in missing['prices']['AAPL'] if r['session_date']!='2026-10-19']
    assert snapshot(evidence(missing),'AAPL','2026-10-19T21:01:00+00:00','95','LONG')['status']!='AVAILABLE'


def assurance(archive,o=None):
    _,m,_=source_inputs(archive,o)
    return {'complete':True,'complete_through':'REGISTRATION','alert_manifest_sha256':alert_manifest(m),'source_reference':'SYNTHETIC operator completeness fixture'}


def test_completeness_gate_rejects_missing_market_source_and_mismatched_assurance(archive):
    asof='2026-10-26T23:00:00+00:00'
    assert not audit(archive,None,None,asof)['passed']
    assert audit(archive,None,assurance(archive),asof)['passed']
    stale=assurance(archive);stale['complete_through']='2026-10-19T23:00:00+00:00'
    assert not audit(archive,None,stale,asof)['passed']
    missing=deepcopy(archive);missing['prices']['AAPL']=[r for r in missing['prices']['AAPL'] if r['session_date']!='2026-10-23']
    result=audit(missing,None,assurance(missing),asof)
    assert not result['passed'] and any(p['code']=='MISSING_REQUIRED_COMPLETED_SESSIONS' for p in result['problems'])
    assert not audit(archive,None,assurance(archive),'2026-10-27T23:00:00+00:00')['passed']
    bad=assurance(archive);bad['alert_manifest_sha256']='wrong';assert not audit(archive,None,bad,asof)['passed']


def test_primary_forecast_targets_eligibility_and_never_maps_stopout_to_drop(archive):
    result=registration_payload(archive,None,assurance(archive),'2026-10-26T23:00:00+00:00')
    assert result['evidence_origin']=='SYNTHETIC_TEST_ONLY'
    assert all(r['source_setup_status']=='ACTIVE' and not r['execution_stopout_used_to_predict_setup_drop'] for r in result['forecasts'])
    assert all(r['primary_targets']['setup_removal']=='ABSTAIN_NO_IDENTIFIED_REMOVAL_RULE' for r in result['forecasts'])
    with pytest.raises(ValueError,match='completeness gate failed'):
        registration_payload(archive,None,None,'2026-10-26T23:00:00+00:00')


def test_legacy_cli_cannot_register_a_new_stale_forward_forecast(tmp_path):
    root=Path(__file__).parents[1]
    import os
    env={**os.environ,'PYTHONPATH':str(root/'src')}
    result=subprocess.run([sys.executable,str(root/'scripts/grimes_predictions.py'),'predict','--view','missing',
        '--mode','FORWARD_REGISTERED','--output',str(tmp_path/'no-output')],capture_output=True,text=True,env=env)
    assert result.returncode!=0 and 'non-operational' in result.stderr and not (tmp_path/'no-output').exists()
    with pytest.raises(ValueError,match='non-operational'):
        load_registration(root/'docs/evidence/pr9c-next-alert-v1')


def test_source_opportunity_ledger_does_not_read_or_mutate_market_prices(archive):
    original=deepcopy(archive);before=ledger(archive)
    altered=deepcopy(archive);altered['prices']={};altered['coverage']={}
    assert ledger(altered)==before and archive==original


def test_failed_current_registration_writes_no_prediction_and_legacy_stays_unchanged(tmp_path,archive):
    from equity_research.marketlife_workflow import register
    archive['alerts']['origin']='operator' # mock a real intake shape; incomplete-source gate must still reject
    a=tmp_path/'archive';write_bundle(a,{'archive.json':encode(archive)})
    o=tmp_path/'source';write_bundle(o,{'operator-alerts.json':encode(additions()),'guidance.json':encode({'origin':'synthetic fixture'})})
    proof=tmp_path/'assurance.json';proof.write_bytes(encode({}))
    with pytest.raises(ValueError,match='completeness gate failed'):
        register(a,o,proof,tmp_path/'not-created',now=datetime(2026,10,26,23,tzinfo=UTC))
    assert not (tmp_path/'not-created').exists()
    parent=Path(__file__).parents[1]/'docs/evidence/pr9c-next-alert-v1'
    before=read_bundle(parent)
    assert json.loads(before[0]['prediction.json'])['outcome']=='UNRESOLVED_NO_LATER_ALERT_IMPORTED'
    assert read_bundle(parent)==before


def test_atomic_added_and_stop_change_have_no_intermediate_entry_window(archive):
    archive['alerts']['alerts']=archive['alerts']['alerts'][:1]
    a=archive['alerts']['alerts'][0]
    a['text']=a['text'].replace('Stop Changed____\nNone','Stop Changed____\nAAPL stop moved to 94.00 from 95.00')
    l=ledger(archive)
    assert len(l['opportunities'])==2 and not l['opportunities'][0]['entry_eligible']
    assert eligible_at(l,'AAPL-001',l['opportunities'][1]['effective_from'])==[l['opportunities'][1]]


def test_study_replay_rejects_hash_consistent_changed_opportunity(tmp_path,archive):
    a=tmp_path/'archive';write_bundle(a,{'archive.json':encode(archive)})
    o=tmp_path/'source';write_bundle(o,{'operator-alerts.json':encode(additions()),'guidance.json':encode({'quote':'synthetic eligibility fixture'})})
    seal=freeze_study(a,o,tmp_path/'study','2026-10-26T23:00:00+00:00')
    files,h=load_study(tmp_path/'study');assert h==seal
    assert write_bundle(tmp_path/'replay',files)==seal
    changed=deepcopy(files);r=json.loads(changed['research.json'])
    r['scenarios'][-1]['ledger']['opportunities'][0]['published_stop']='1.00'
    changed['research.json']=encode(r);write_bundle(tmp_path/'resealed',changed)
    with pytest.raises(ValueError,match='semantic output mismatch'):load_study(tmp_path/'resealed')


def test_current_gate_requires_benchmark_and_rejects_partial_future_bars(archive):
    asof='2026-10-26T23:00:00+00:00'
    missing=deepcopy(archive);missing['prices']['SPY']=[r for r in missing['prices']['SPY'] if r['session_date']!='2026-10-26']
    result=audit(missing,None,assurance(missing),asof)
    assert not result['passed'] and any(p.get('symbol')=='SPY' for p in result['problems'])
    future=deepcopy(archive);r=deepcopy(future['prices']['AAPL'][-1]);r['session_date']='2026-10-27';future['prices']['AAPL'].append(r)
    assert any(p['code']=='FUTURE_OR_INCOMPLETE_MARKET_OBSERVATION' for p in audit(future,None,assurance(future),asof)['problems'])
    absent=deepcopy(archive);absent['prices'].pop('SPY');absent['coverage'].pop('SPY')
    assert not audit(absent,None,assurance(absent),asof)['passed']


def test_committed_source_opportunities_and_current_registration_blocker():
    root=Path(__file__).parents[1]
    files,_=read_bundle(root/'docs/evidence/pr9c-setup-opportunities-v1')
    ledgers=json.loads(files['opportunity-ledger.json'])
    for l in ledgers.values():
        assert len(l['setups'])==34 and len(l['opportunities'])==72
        assert sum(o['entry_eligible'] for o in l['opportunities'])==58
        assert all(o['observed_execution']=='UNKNOWN' and o['actual_entry'] is None for o in l['opportunities'])
        active=[s for s in l['setups'] if s['setup_status']=='ACTIVE']
        assert len(active)==10 and sum(s['entry_state']=='ENTERABLE' for s in active)==5
        sail=[o for o in l['opportunities'] if o['symbol']=='SAIL']
        assert [o['published_stop'] for o in sail]==['20.90','21.30','20.70']
        assert not sail[1]['entry_eligible'] and sail[2]['entry_eligible']
    source=json.loads(files['source-evidence.json'])
    assert len(source['source_alerts'])==10
    assert all(a['published_at'] is None and a['publication_precision']=='DATE' for a in source['source_alerts'][-3:])
    gate=json.loads(files['registration-audit.json'])
    assert not gate['passed'] and gate['required_latest_completed_session']=='2026-10-29'
    assert not gate['superseded_registration']['operational_baseline']
    assert any(p['code']=='SOURCE_HISTORY_NOT_VERIFIED_THROUGH_REGISTRATION' for p in gate['problems'])
    assert {tuple(p['sessions']) for p in gate['problems'] if p['code']=='MISSING_REQUIRED_COMPLETED_SESSIONS'}=={('2026-10-27','2026-10-28','2026-10-29')}


def test_committed_transitions_do_not_use_copublished_opportunity_as_prior_anchor():
    root=Path(__file__).parents[1]
    files,_=read_bundle(root/'docs/evidence/pr9c-setup-opportunities-v1')
    transitions=json.loads(files['underway-transitions.json'])['LATE']
    assert len(transitions)==14 and len({t['source_alert_id'] for t in transitions})==5
    measured=[t for t in transitions if t['measurements']['measurement_status']=='AVAILABLE_DAILY_REFERENCE_MOVEMENT']
    assert len(measured)==7 and sum(t['direction']=='LONG' for t in measured)==1
    assert len({t['source_alert_id'] for t in measured})==2
    ledger=json.loads(files['opportunity-ledger.json'])['LATE'];ops={o['opportunity_id']:o for o in ledger['opportunities']}
    for t in transitions:
        assert ops[t['last_eligible_opportunity_id']]['source_alert_id']!=t['source_alert_id']
        assert t['last_enterable_assessment']['source_alert_id']!=t['source_alert_id']
        assert all(c['direction']==t['direction'] and c['source_state']=='REMAINED_ENTERABLE' for c in t['controls'])
    cases=json.loads(files['forensic-comparison.json'])['LATE']
    assert {c['symbol']:c['A_continuous_reference']['first_model_exit']['session'] for c in cases}=={
        'CLMT':'2026-10-19','TEVA':'2026-10-21','GME':'2026-10-22','EBAY':'2026-10-26'}
    ebay=next(c for c in cases if c['symbol']=='EBAY')
    assert ebay['B_independent_hard_opportunities'][-1]['construction']['status']=='NEXT_OPEN_UNOBSERVED'


def test_committed_markdown_is_reproducible_offline(tmp_path):
    import os
    root=Path(__file__).parents[1]
    env={**os.environ,'PYTHONPATH':str(root/'src')}
    result=subprocess.run([sys.executable,str(root/'scripts/report_marketlife_setups.py'),'report',
        '--evidence',str(root/'docs/evidence/pr9c-setup-opportunities-v1'),'--output',str(tmp_path/'report')],
        capture_output=True,text=True,env=env)
    assert result.returncode==0,result.stderr
    files,_=read_bundle(tmp_path/'report')
    assert len(files)==2
    for name,content in files.items():assert content==(root/'docs/reports'/name).read_bytes()
