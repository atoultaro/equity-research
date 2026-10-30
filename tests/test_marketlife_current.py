"""PR9D synthetic current evidence; broker access is never required."""
import asyncio
from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pandas as pd
import pytest

from test_prospective_predictions import archive,alert
from test_history import MockIB,ib_provider,VirtualTime
from equity_research.history.contracts import Security
from equity_research.ingestion.storage import encode,read_bundle,write_bundle
from equity_research.marketlife_intake import (completed_window,source_state,append_source,
    validate_contract,merge_evidence,proof_record)
from equity_research.marketlife_readiness import (archive_files,load_archive,readiness,conditional_view,
    prediction_files,load_prediction,register_current)
from equity_research.marketlife_acquire import acquire,qualify
from equity_research.marketlife_workflow import registration_payload
from equity_research.providers.ibkr import Pacer

NOW='2026-10-26T23:00:00+00:00'


@pytest.fixture
def current(archive):
    for n,symbol in enumerate(('AAPL','SPY'),1):
        venue='NASDAQ' if symbol=='AAPL' else 'ARCA'
        security=Security(symbol,f'test:{symbol}','synthetic fixture',symbol,symbol,venue,venue,con_id=n)
        archive['coverage'][symbol]['security']=security.record()
        archive['coverage'][symbol]['contract']={'conId':n,'symbol':symbol,'currency':'USD','exchange':'SMART',
            'primaryExchange':venue,'secType':'STK','localSymbol':symbol,'tradingClass':symbol}
    return archive


def batch(*alerts,receipt=NOW):
    return {'schema_version':'marketlife_operator_alerts_v1','captured_at':receipt,
        'alerts':[{**a,'source_date':(a['published_at'] or '2026-10-20')[:10]} for a in alerts]}


def source_proof(tmp_path,record):
    path=tmp_path/f'source-{len(list(tmp_path.glob("source-*")))}'
    files={'operator-alerts.json':encode(record),'guidance.json':encode({'quote':'synthetic'})}
    h=write_bundle(path,files)
    return {'files':{k:v.decode() for k,v in files.items()},'hashes':h}


def assurance(current,batches):
    s=source_state(current,batches,NOW)
    return {'complete':True,'complete_through':'REGISTRATION','source_reference':'synthetic operator assertion',
        'asserted_at':NOW,'operator_statement':'Synthetic operator confirms complete history through registration.',
        'alert_manifest_sha256':s['source_alert_manifest_sha256']}


def sealed_current(tmp_path,current,*,record=None,proofs=(),attested=True):
    record=record or batch();sp=source_proof(tmp_path,record)
    parent={'archive.json':encode(current)};ph=write_bundle(tmp_path/'parent',parent)
    a=assurance(current,[record]) if attested else None
    files=archive_files(parent,ph,[sp],list(proofs),NOW,a,[])
    path=tmp_path/'current';h=write_bundle(path,files)
    return path,files,h


def native_proof(tmp_path,current,*,symbol='AAPL',transform=lambda r:r):
    security=Security(**current['coverage'][symbol]['security'])
    row=transform(deepcopy(current['prices'][symbol][-1]))
    frame=pd.DataFrame([{k.title():float(row[k]) for k in ('open','high','low','close','volume')}],
        index=pd.DatetimeIndex([row['session_date']]))
    provider=ib_provider(MockIB(frame=frame),clock=lambda:datetime.fromisoformat(NOW))
    path=tmp_path/'native';provider.fetch_daily(security,row['session_date'],row['session_date'],path)
    return proof_record(path)


def test_window_uses_dynamic_cutoff_weekends_holiday_early_close_and_dst():
    assert completed_window('2026-10-30T16:59:00-04:00')[1][-1]=='2026-10-29'
    assert completed_window('2026-10-30T17:00:00-04:00')[1][-1]=='2026-10-29'
    assert completed_window('2026-10-30T17:00:01-04:00')[1][-1]=='2026-10-30'
    assert completed_window('2026-11-01T12:00:00-05:00')[1][-1]=='2026-10-30'
    assert completed_window('2026-11-02T16:30:00-05:00')[1][-1]=='2026-10-30'
    assert completed_window('2026-11-02T17:01:00-05:00')[1][-1]=='2026-11-02'
    assert completed_window('2026-11-26T20:00:00-05:00')[1][-1]=='2026-11-25'
    assert completed_window('2026-11-27T14:00:00-05:00')[1][-1]=='2026-11-25'
    assert completed_window('2026-11-27T14:00:01-05:00')[1][-1]=='2026-11-27'


def test_contract_validation_rejects_wrong_symbol_exchange_type_currency_and_conid(current):
    c=current['coverage']['AAPL']['contract'];validate_contract('AAPL',c,c)
    for field,bad in [('symbol','OTHER'),('conId',0),('currency','CAD'),('secType','OPT'),('exchange','OTHER'),('primaryExchange','')]:
        with pytest.raises(ValueError):validate_contract('AAPL',{**c,field:bad},c)
    with pytest.raises(ValueError,match='changed'):validate_contract('AAPL',{**c,'conId':999},c)


def test_source_batches_preserve_prior_receipt_and_unknown_publication_bounds(current):
    a=alert('date',0,None,stops='AAPL stop moved to 91.00 from 90.00');a['publication_precision']='DATE'
    early=batch(a,receipt='2026-10-20T18:00:00-04:00')
    b=batch(alert('return',0,'2026-10-21T18:00:00-04:00',stops='AAPL stop moved to 92.00 from 91.00'))
    before=source_state(current,[early],NOW);after=source_state(current,[early,b],NOW)
    assert before['metadata']==after['metadata'][:-1]
    assert datetime.fromisoformat(before['metadata'][-1]['upper'])==datetime.fromisoformat('2026-10-20T18:00:00-04:00')
    assert before['metadata'][-1]['published_at'] is None
    assert len(after['ledgers'][-1]['opportunities'])==4


def test_source_intake_rejects_duplicates_inconsistent_chain_and_eligibility(current):
    first=batch(alert('c',0,'2026-10-20T18:00:00-04:00',stops='AAPL stop moved to 91.00 from 90.00'))
    append_source(current,[],first,NOW)
    with pytest.raises(ValueError,match='duplicate'):append_source(current,[first],first,NOW)
    bad=batch(alert('d',0,'2026-10-21T18:00:00-04:00',stops='AAPL stop moved to 92.00 from 95.00'))
    with pytest.raises(ValueError,match='chain mismatch'):append_source(current,[first],bad,NOW)
    bad=batch(alert('d',0,'2026-10-21T18:00:00-04:00',setups='AAPL setup changed to long from long (underway)'))
    with pytest.raises(ValueError,match='eligibility mismatch'):append_source(current,[first],bad,NOW)
    bad=batch(alert('d',0,'2026-10-21T18:00:00-04:00',dropped='AAPL dropped from long (underway)'))
    with pytest.raises(ValueError,match='eligibility mismatch'):append_source(current,[first],bad,NOW)


def test_new_source_state_return_and_reopening_stays_separate_from_execution(current):
    records=[batch(alert('c',0,'2026-10-20T18:00:00-04:00',setups='AAPL setup changed to long (underway) from long')),
        batch(alert('d',0,'2026-10-21T18:00:00-04:00',stops='AAPL stop moved to 91.00 from 90.00')),
        batch(alert('e',0,'2026-10-22T18:00:00-04:00',setups='AAPL setup changed to long from long (underway)')),
        batch(alert('f',0,'2026-10-23T18:00:00-04:00',dropped='AAPL dropped from long')),
        batch(alert('g',0,'2026-10-26T18:00:00-04:00',added='AAPL added long with stop 92.00'))]
    l=source_state(current,records,NOW)['ledgers'][-1]
    assert [s['setup_id'] for s in l['setups']]==['AAPL-001','AAPL-002']
    assert l['opportunities'][-2]['published_stop']=='91.00'
    assert all(o['observed_execution']=='UNKNOWN' for o in l['opportunities'])


def test_append_native_data_keeps_all_existing_canonical_bytes(tmp_path,current):
    proof=native_proof(tmp_path,current)
    before=deepcopy(current);missing=deepcopy(current);missing['prices']['AAPL'].pop()
    merged,findings=merge_evidence(missing,[batch()],[proof],NOW)
    assert not findings and current==before
    assert merged['prices']['AAPL'][:-1]==missing['prices']['AAPL']
    assert merged['prices']['AAPL'][-1]['source_snapshot_sha256']==proof['hashes']['bundle_sha256']


def test_conflicting_overlap_is_not_replaced_and_blocks_registration(tmp_path,current):
    proof=native_proof(tmp_path,current,transform=lambda r:{**r,'volume':'999'})
    merged,findings=merge_evidence(current,[batch()],[proof],NOW)
    assert merged['prices']==current['prices']
    assert findings[0]['code']=='CONFLICTING_RETAINED_NATIVE_VINTAGES'
    assert not readiness(merged,[batch()],assurance(current,[batch()]),NOW,findings)['passed']


def test_incompatible_native_mapping_is_rejected(tmp_path,current):
    proof=native_proof(tmp_path,current);old=current['coverage']['AAPL']['contract']['conId']
    current['coverage']['AAPL']['contract']['conId']=old+100
    with pytest.raises(ValueError,match='changed'):merge_evidence(current,[batch()],[proof],NOW)


def test_current_gate_detects_missing_session_and_source_manifest_mismatch(current):
    b=[batch()];a=assurance(current,b)
    assert readiness(current,b,a,NOW)['passed']
    missing=deepcopy(current);missing['prices']['AAPL'].pop()
    assert not readiness(missing,b,a,NOW)['passed']
    assert not readiness(current,b,None,NOW)['passed']
    assert not readiness(current,b,{**a,'alert_manifest_sha256':'wrong'},NOW)['passed']
    bad=deepcopy(current);r=deepcopy(bad['prices']['AAPL'][-1]);r['session_date']='2026-10-25';bad['prices']['AAPL'].append(r)
    assert any(p['code']=='OFF_CALENDAR_PRICE_HISTORY' for p in readiness(bad,b,a,NOW)['problems'])


def test_atr_current_features_are_causal_and_report_underlying_session(current):
    b=[batch(receipt='2026-10-26T16:00:00-04:00')];a=assurance(current,b)
    before=readiness(current,b,a,'2026-10-26T16:30:00-04:00')['features']['AAPL']
    after=readiness(current,b,a,NOW)['features']['AAPL']
    assert before['feature_session']=='2026-10-23' and after['feature_session']=='2026-10-26'
    assert after['atr14']>0 and after['sma10']['value'] and after['features']['sma50']['value']
    changed=deepcopy(current);changed['prices']['AAPL'][-1].update(open='999',high='1001',low='998',close='1000')
    assert readiness(changed,b,a,'2026-10-26T16:30:00-04:00')['features']['AAPL']==before


def test_forecast_model_output_matches_unchanged_pr9c_model(current):
    b=[batch()];a=assurance(current,b);s=source_state(current,b,NOW)
    old=registration_payload(current,None,a,NOW)
    for clock in s['clocks']:
        view,operator=conditional_view(current,b,s,clock)
        r=registration_payload(view,operator,a,NOW)
        expected=[p for p in old['forecasts'] if p['timing_scenario']==clock['name']]
        actual=[{**p,'timing_scenario':clock['name']} for p in r['forecasts'] if p['timing_scenario']=='LATE']
        assert actual==expected
    assert current['alerts']['alerts'][0]['publication_precision']=='MINUTE'


def test_complete_synthetic_forward_registration_and_semantic_replay(tmp_path,current):
    path,files,h=sealed_current(tmp_path,current)
    assert load_archive(path)==(files,h)
    predicted=prediction_files(files,h,NOW);ph=write_bundle(tmp_path/'prediction',predicted)
    assert load_prediction(tmp_path/'prediction')==(predicted,ph)
    p=json.loads(predicted['prediction.json'])
    assert p['evidence_origin']=='SYNTHETIC_TEST_ONLY' and p['gate']['passed']
    assert p['registered_at']==NOW and p['outcome']=='UNRESOLVED_NO_LATER_SOURCE_ASSESSMENT'
    assert p['original_PR9C_forecast_rules_unchanged']
    with pytest.raises(ValueError,match='synthetic'):register_current(path,tmp_path/'operational')
    assert not (tmp_path/'operational').exists()


def test_resealed_changed_archive_and_prediction_are_rejected(tmp_path,current):
    path,files,h=sealed_current(tmp_path,current)
    changed=deepcopy(files);a=json.loads(changed['archive.json']);a['prices']['AAPL'][-1]['volume']='999'
    changed['archive.json']=encode(a);write_bundle(tmp_path/'altered',changed)
    with pytest.raises(ValueError,match='semantic replay mismatch'):load_archive(tmp_path/'altered')
    predicted=prediction_files(files,h,NOW);p=json.loads(predicted['prediction.json'])
    p['forecasts'][0]['primary_targets']['entry_eligibility']='FAKE';predicted['prediction.json']=encode(p)
    write_bundle(tmp_path/'changed-prediction',predicted)
    with pytest.raises(ValueError,match='semantic replay mismatch'):load_prediction(tmp_path/'changed-prediction')


def test_registration_failure_has_no_output_and_cli_has_no_backdate(tmp_path,current):
    path,files,h=sealed_current(tmp_path,current,attested=False)
    with pytest.raises(ValueError,match='readiness FAIL'):prediction_files(files,h,NOW)
    result=subprocess.run([sys.executable,'scripts/marketlife_current.py','register','--help'],capture_output=True,text=True,
        env={'PATH':'/usr/bin:/bin','PYTHONPATH':'src'})
    assert result.returncode==0 and '--asof' not in result.stdout
    with pytest.raises(TypeError):register_current(path,tmp_path/'forbidden',now=datetime.fromisoformat(NOW))
    assert not (tmp_path/'forbidden').exists()


def test_acquisition_rejects_missing_operator_confirmations_before_connection(tmp_path,current):
    with pytest.raises(ValueError,match='paper authentication'):
        acquire(current,[batch()],tmp_path/'unused',tmp_path/'out',port=7497,client_id=999,
            connect=True,read_only=True,paper=False,reference='synthetic')
    assert not (tmp_path/'out').exists()


def test_qualification_uses_only_market_operations_and_rejects_ambiguity(current):
    fake=MockIB();v=VirtualTime()
    records=asyncio.run(qualify([{'symbol':'AAPL','contract':current['coverage']['AAPL']['contract']}],
        '127.0.0.1',7497,999,backend_factory=lambda:fake,pacer=Pacer(clock=v.now,sleep=v.sleep)))
    assert records[0]['status']=='SUCCESS' and fake.disconnected
    assert [c[0] for c in fake.calls]==['connect','qualify','disconnect']
    c=SimpleNamespace(**current['coverage']['AAPL']['contract']);fake=MockIB(qualification=[c,c])
    records=asyncio.run(qualify([{'symbol':'AAPL','contract':current['coverage']['AAPL']['contract']}],
        '127.0.0.1',7497,999,backend_factory=lambda:fake,pacer=Pacer(clock=v.now,sleep=v.sleep)))
    assert records[0]['status']=='FAILED'


def test_conditional_date_projection_preserves_unchanged_model_with_reopened_episode(current):
    dropped=alert('drop',0,'2026-10-20T18:00:00-04:00',dropped='AAPL dropped from long')
    added=alert('reopen',1,None,added='AAPL added long with stop 95.00');added['publication_precision']='DATE'
    record=batch(dropped,added);record['alerts'][1]['source_date']='2026-10-21'
    a=assurance(current,[record]);state=source_state(current,[record],NOW)
    old=registration_payload(current,record,a,NOW)
    for clock in state['clocks']:
        view,operator=conditional_view(current,[record],state,clock)
        proposed=registration_payload(view,operator,a,NOW)
        assert [{**p,'timing_scenario':clock['name']} for p in proposed['forecasts'] if p['timing_scenario']=='LATE']==[
            p for p in old['forecasts'] if p['timing_scenario']==clock['name']]
    assert record['alerts'][1]['published_at'] is None


def test_native_failure_and_incompatible_basis_cannot_be_promoted(tmp_path,current):
    proof=native_proof(tmp_path,current,transform=lambda r:{**r,'high':'1'})
    merged,findings=merge_evidence(current,[batch()],[proof],NOW)
    assert merged['prices']==current['prices'] and findings[0]['code']=='NATIVE_REQUEST_OR_NORMALIZATION_FAILED'
    bad=deepcopy(current);bad['coverage']['AAPL']['price_basis']='RAW_UNPROVEN'
    assert not readiness(bad,[batch()],assurance(current,[batch()]),NOW)['passed']


def test_synthetic_native_updates_cannot_enter_an_operational_archive(tmp_path,current):
    proof=native_proof(tmp_path,current)
    current['alerts']['origin']='operator'
    with pytest.raises(ValueError,match='synthetic market updates'):
        merge_evidence(current,[batch()],[proof],NOW)
    gate=readiness(current,[batch()],assurance(current,[batch()]),NOW)
    assert not gate['passed'] and any(p['code']=='NON_NATIVE_MARKET_EVIDENCE_IN_OPERATIONAL_ARCHIVE' for p in gate['problems'])


def test_unattested_future_assertion_and_future_source_capture_fail(current):
    records=[batch()];a=assurance(current,records)
    assert not readiness(current,records,{**a,'asserted_at':'2026-10-27T23:00:00+00:00'},NOW)['passed']
    assert not readiness(current,records,{**a,'operator_statement':''},NOW)['passed']
    with pytest.raises(ValueError,match='capture is after'):
        source_state(current,[batch(receipt='2026-10-27T23:00:00+00:00')],NOW)


def test_stale_pre_acquisition_plan_fails_without_broker_or_output(tmp_path,current):
    from equity_research.marketlife_intake import coverage_audit
    report=coverage_audit(current,[batch()],NOW)
    report['required_latest_completed_session']='1900-01-01'
    plan=tmp_path/'plan';write_bundle(plan,{'coverage-audit.json':encode(report)})
    with pytest.raises(ValueError,match='stale or differs'):
        acquire(current,[batch()],plan,tmp_path/'out',port=7497,client_id=999,
            connect=True,read_only=True,paper=True,reference='synthetic')
    assert not (tmp_path/'out').exists()


def test_committed_blocked_evidence_is_honest_and_reports_reproduce(tmp_path):
    import os
    root=Path(__file__).parents[1]
    path=root/'docs/evidence/pr9d-current-readiness-v1';files,h=read_bundle(path)
    coverage=json.loads(files['market-coverage.json']);gate=json.loads(files['registration-audit.json'])
    assert coverage['required_latest_completed_session']=='2026-10-29'
    assert len(coverage['instruments'])==11 and not gate['passed']
    assert sum(r['identity_status']=='QUALIFIED_RECORDED' for r in coverage['instruments'])==6
    assert all(r['missing_sessions'] for r in coverage['instruments'])
    assert not any('prediction.json'==name for name in files)
    assert json.loads(files['forecast-status.json'])['status']=='NOT_REGISTERED_READINESS_FAIL'
    assert not json.loads(files['access-status.json'])['qualification_attempts']
    assert json.loads(files['source-completeness.json'])['status']=='FAIL'
    state=json.loads(files['source-manifest.json'])
    assert len(state['alerts'])==10 and state['captured_setup_episodes']==34
    result=subprocess.run([sys.executable,str(root/'scripts/report_marketlife_current.py'),'report',
        '--evidence',str(path),'--output',str(tmp_path/'report')],capture_output=True,text=True,
        env={**os.environ,'PYTHONPATH':str(root/'src')})
    assert result.returncode==0,result.stderr
    for name,content in read_bundle(tmp_path/'report')[0].items():assert content==(root/'docs/reports'/name).read_bytes()
