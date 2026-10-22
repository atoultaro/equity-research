"""Synthetic generalization contracts; no live acquisitions, account APIs or real price rows."""

from copy import deepcopy
from dataclasses import replace
import json
from types import SimpleNamespace

import pytest

from equity_research.events.alignment import align_event, event_schedule
from equity_research.events.comparison import compare_event_studies
from equity_research.events.dataset import freeze_study, load_event_study
from equity_research.events.model import freeze_events
from equity_research.history.cache import HistoryCache, history
from equity_research.history.contracts import Security
from equity_research.history.dataset import freeze
from equity_research.ingestion.storage import read_bundle, encode, write_bundle
from test_events import event, source
from test_history import FIXED, MockIB, bars, ib_provider

START, END = '2024-10-01', '2024-12-20'


def mapping(symbol='GOOG'):
    return Security(symbol, 'synthetic:'+symbol+':class:C' if symbol=='GOOG' else 'synthetic:'+symbol,
                    'synthetic reviewed identity', symbol, symbol, 'NASDAQ', 'XNAS')


def projected_event(security, *, kind='EARNINGS', effective=None):
    e=event(kind, relation='AFTER_CLOSE', effective=effective)
    e['event_id']='synthetic-issuer-event-'+kind
    e['security_id']=security.security_id
    e['payload'].update(issuer_id='synthetic-issuer', issuer_event_id=e['event_id'],
                        event_scope='ISSUER', applicable_share_classes=['A','C'])
    return e


def study(tmp_path, security, *, value=100, drop=(), events=None):
    frame=bars(START,END,value=value,adjusted=False,drop=drop)
    provider=ib_provider(MockIB(frame=frame))
    cache=HistoryCache(tmp_path/'cache')
    result=history(cache,provider,[security],START,END,clock=lambda:FIXED)
    freeze(cache,'ibkr',[security],START,END,tmp_path/'prices',allow_incomplete=bool(drop),clock=lambda:FIXED)
    events=events or [projected_event(security)]
    freeze_events(events,[source(events)],tmp_path/'events')
    freeze_study(tmp_path/'prices',tmp_path/'events',security.symbol,tmp_path/'study')
    return load_event_study(tmp_path/'study'),result


def test_goog_class_c_contract_and_native_bounded_capture(tmp_path):
    s=mapping()
    backend=MockIB(frame=bars('2024-11-21','2024-12-02',adjusted=False))
    result=ib_provider(backend).fetch_daily(s,'2024-11-25','2024-11-29',tmp_path/'capture')
    a=result['acquisition']
    assert a['qualified_contract']['symbol']=='GOOG'
    assert a['qualified_contract']['primaryExchange']=='NASDAQ'
    assert a['qualified_contract']['currency']=='USD'
    assert a['status']=='SUCCESS'
    assert len(result['rows'])==4
    assert a['coverage']['native_rows']==7
    assert len(a['excluded_native_rows'])==3
    assert len(json.loads(read_bundle(tmp_path/'capture')[0]['returned_bars.json'])['bars'])==7
    assert all(r['security_id']==s.security_id and r['provider']=='ibkr' for r in result['rows'])
    assert [c[0] for c in backend.calls]==['connect','qualify','historical','disconnect']


def test_goog_request_rejects_googl_substitution_before_historical_data(tmp_path):
    s=mapping()
    q=SimpleNamespace(conId=777,secType='STK',symbol='GOOGL',exchange='SMART',currency='USD',
                      primaryExchange='NASDAQ',localSymbol='GOOGL',tradingClass='NMS')
    backend=MockIB(qualification=[q])
    result=ib_provider(backend).fetch_daily(s,START,END,tmp_path/'capture')
    assert result['acquisition']['qualified_contract'] is None
    assert any(e['category']=='QUALIFIED_IDENTITY_MISMATCH' for e in result['acquisition']['errors'])
    assert not any(c[0]=='historical' for c in backend.calls)
    assert backend.disconnected


def test_partial_goog_history_keeps_gaps_and_does_not_fallback(tmp_path, monkeypatch):
    def forbidden(*args,**kwargs): raise AssertionError('no Yahoo fallback')
    monkeypatch.setattr('equity_research.providers.yahoo.YahooDailyProvider',forbidden)
    s=mapping()
    ds,report=study(tmp_path,s,drop=('2024-11-27',))
    assert report['status']=='PARTIAL_OR_FAILED'
    assert ds.prices.quality('GOOG')['missing_sessions']==['2024-11-27']
    r=ds.diagnostics['events'][0]
    assert r['status']=='PARTIAL'
    assert r['subsequent_close_returns_pct']=={'1':None,'5':None,'10':None}
    assert r['pre_event_atr14']==4
    assert all(row['provider']=='ibkr' for row in ds.bars())


def test_shared_issuer_release_preserves_distinct_security_prices_and_single_publication(tmp_path):
    c,a=mapping(),mapping('GOOGL')
    first,_=study(tmp_path/'c',c,value=100)
    second,_=study(tmp_path/'a',a,value=200)
    ce,ae=first.event_dataset.events[0],second.event_dataset.events[0]
    assert ce['event_id']==ae['event_id']
    assert ce['payload']['issuer_id']==ae['payload']['issuer_id']
    assert ce['security_id']!=ae['security_id']
    assert len(first.event_dataset.events)==len(second.event_dataset.events)==1
    assert first.event_dataset.sources[0]['source_document_id']==second.event_dataset.sources[0]['source_document_id']
    assert first.diagnostics['events'][0]['previous_close']==101
    assert second.diagnostics['events'][0]['previous_close']==201
    wrong=projected_event(a)
    freeze_events([wrong],[source([wrong])],tmp_path/'wrong-events')
    with pytest.raises(ValueError,match='identity'):
        freeze_study(tmp_path/'c/prices',tmp_path/'wrong-events','GOOG',tmp_path/'wrong-study')


@pytest.mark.parametrize('relation,announced,precision,reaction',[
    ('BEFORE_OPEN','2024-11-25T08:00:00-05:00','MINUTE','2024-11-25'),
    ('AFTER_CLOSE','2024-11-25T16:01:35-05:00','SECOND','2024-11-26'),
    ('UNKNOWN',None,'DATE',None),
])
def test_issuer_release_precision_uses_shared_alignment(tmp_path,relation,announced,precision,reaction):
    e=projected_event(mapping())
    e.update(announced_session_relation=relation,announced_at=announced,announced_time_precision=precision,
             relation_evidence_status='UNKNOWN' if relation=='UNKNOWN' else 'VERIFIED')
    cal=event_schedule([e],START,END)
    assert align_event(e,cal)['reaction_session']==reaction


def test_dividend_known_and_unknown_ex_dates_share_pipeline_without_contamination(tmp_path):
    s=mapping()
    earnings=projected_event(s)
    known=projected_event(s,kind='DIVIDEND',effective='2024-11-29')
    unknown=projected_event(s,kind='DIVIDEND');unknown['event_id']+='-unknown'
    unknown['payload']['record_date']='2024-12-02'
    ds,_=study(tmp_path,s,events=[earnings,known,unknown])
    r,d,u=ds.diagnostics['events']
    assert [x['event_id'] for x in r['potential_corporate_action_effects']]==[known['event_id']]
    assert len(ds.diagnostics['corporate_action_evidence']['unknown_effective_dates'])==1
    assert d['reaction_session']=='2024-11-29'
    assert d['first_post_close']==101
    assert d['previous_close']==101 and d['first_post_open']==100
    assert d['open_change_dollars']==-1 and d['close_change_dollars']==0
    assert d['cash_per_share_source_quote']=='0.25' and d['basis_verified'] is False
    assert u['issues']==['EX_DATE_UNKNOWN']


def test_sourced_bounds_remain_uncertainty_and_do_not_invent_ex_date(tmp_path):
    s=mapping()
    d=projected_event(s,kind='DIVIDEND')
    d['payload']['effective_date_bounds']={'not_before':'2024-11-29','not_after':'2024-12-02',
        'evidence_status':'VERIFIED','source_ids':['synthetic-source']}
    ds,_=study(tmp_path,s,events=[projected_event(s),d])
    r=ds.diagnostics['events'][0]
    assert r['potential_corporate_action_effects']==[]
    assert r['corporate_action_overlap_uncertainty'][0]['effective_date'] is None
    assert ds.event_dataset.events[1]['payload']['ex_date'] is None


def test_split_chronology_is_distinct_from_announcement_and_price_coverage(tmp_path):
    s=mapping();e=projected_event(s,kind='SPLIT',effective='2022-07-18')
    e.update(event_date='2022-02-01',announced_session_relation='UNKNOWN',relation_evidence_status='UNKNOWN')
    e['payload'].update(new_shares='20',old_shares='1',record_date='2022-07-01',distribution_date='2022-07-15',
                        distribution_session_relation='AFTER_CLOSE')
    ds,_=study(tmp_path,s,events=[e])
    a=ds.retrospective['alignment']['events'][0]
    assert a['announcement_date']=='2022-02-01' and a['effective_session']=='2022-07-18'
    assert ds.event_dataset.events[0]['payload']['distribution_date']=='2022-07-15'
    assert ds.diagnostics['events'][0]['issues']==['SPLIT_PRICE_AND_VOLUME_BASIS_UNVERIFIED']
    assert all(r['session_date']>='2024-10-01' for r in ds.bars())


def test_cross_company_evidence_comparison_uses_identical_definitions(tmp_path):
    a,g=mapping('AAPL'),mapping()
    first,_=study(tmp_path/'a',a)
    d=projected_event(g,kind='DIVIDEND',effective='2024-11-29')
    second,_=study(tmp_path/'g',g,events=[projected_event(g),d])
    r=compare_event_studies({'first':first,'second':second})
    x,y=r['studies']['first'],r['studies']['second']
    assert x['price_rows']==y['price_rows']==x['expected_sessions']
    assert x['available_diagnostics']['EARNINGS']==y['available_diagnostics']['EARNINGS']==1
    assert x['verified_ex_dates']==0 and y['verified_ex_dates']==1
    assert x['basis']==y['basis']
    assert x['price_dataset_sha256']!=y['price_dataset_sha256']
    assert r['interpretation']=='EVIDENCE_COMPLETENESS_NOT_TRADING_PERFORMANCE'
    with pytest.raises(ValueError,match='at least two'):
        compare_event_studies({'only':first})
    bad=deepcopy(second.manifest);bad['implementation_sha256']['diagnostics.py']='different'
    class DifferentCode:
        manifest=bad
        prices=second.prices
        diagnostics=second.diagnostics
    with pytest.raises(ValueError,match='identical'):
        compare_event_studies({'first':first,'other':DifferentCode()})


def test_new_study_version_preserves_original_snapshot_and_loads_without_providers(tmp_path):
    s=mapping();old,_=study(tmp_path,s)
    original=read_bundle(tmp_path/'study')
    freeze_study(tmp_path/'prices',tmp_path/'events','GOOG',tmp_path/'study-v2')
    assert read_bundle(tmp_path/'study')==original
    assert load_event_study(tmp_path/'study-v2').content_sha256==old.content_sha256
    with pytest.raises(FileExistsError):
        freeze_study(tmp_path/'prices',tmp_path/'events','GOOG',tmp_path/'study')
