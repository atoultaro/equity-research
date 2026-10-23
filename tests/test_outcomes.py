"""Hand-calculated descriptive paths, captured-signal lineage and no execution."""
from copy import deepcopy
from datetime import timedelta
from decimal import Decimal,localcontext
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from equity_research.ingestion.calendar import schedule
from equity_research.ingestion.storage import encode,digest,read_bundle,write_bundle
from equity_research.models import timestamp
from equity_research.outcomes import Configuration,measure,freeze_outcomes,load_outcomes,CLOSE,OPEN
from equity_research.outcomes.analysis import cluster_signals,summarize
from equity_research.outcomes.dataset import FrozenSignals


@pytest.fixture
def sample():
    calendar=schedule('2024-11-25','2025-02-07')
    rows=[{'symbol':'SYNTH','security_id':'synthetic:SYNTH','session_date':s['session_date'],
        'open':str(100+i-.5),'close':str(100+i),'high':str(102+i),'low':str(98+i),'volume':'1000'} for i,s in enumerate(calendar['sessions'])]
    rows[0].update(high='1000',low='1',open='100')
    rows[1].update(open='110',high='120',low='90',close='115')
    signal={'schema_version':'swing_signal_v1','signal_id':'original-signal','strategy_id':'synthetic-breakout','strategy_version':'1',
        'security_id':'synthetic:SYNTH','symbol':'SYNTH','price_dataset_sha256':'a'*64,'market_context_reference':'captured-link',
        'features':{'atr14':'2'},'feature_observation_cutoffs':{'atr14':rows[0]['session_date']},
        'setup':{'setup_id':'original-setup','setup_type':'synthetic-breakout','session_date':rows[0]['session_date'],'boundary':{'value':'99'}},
        'trigger':{'direction':'LONG','session_date':rows[0]['session_date'],'available_at':(timestamp(calendar['sessions'][0]['closes_at'])+timedelta(minutes=60)).isoformat()}}
    return signal,rows,calendar


def calc(sample,**kwargs):
    s,rows,cal=sample
    return measure(s,rows,cal,price_sha='a'*64,strategy_sha='b'*64,basis={'price_basis':'NATIVE_UNVERIFIED','verified':False},**kwargs)


def select(rows,ref,h):return next(r for r in rows if r['reference_type']==ref and r['horizon']==h)


@pytest.mark.parametrize('h,expected',[(1,15),(5,5),(10,10),(20,20)])
def test_signal_close_horizons_and_calendar_endpoints(sample,h,expected):
    rows,_=calc(sample);r=select(rows,CLOSE,h)
    assert Decimal(r['forward_return_pct'])==expected
    assert r['horizon_end_session']==sample[1][h]['session_date']
    assert r['reference_session']=='2024-11-25' and r['reference_price']=='100'
    assert r['outcome_status']=='AVAILABLE' and r['signal_id']=='original-signal'


@pytest.mark.parametrize('h,close',[(0,115),(1,102),(5,106),(10,111),(20,121)])
def test_next_open_offset_zero_and_following_horizons(sample,h,close):
    rows,_=calc(sample);r=select(rows,OPEN,h)
    assert Decimal(r['forward_return_pct'])==pytest.approx((Decimal(close)/110-1)*100)
    assert r['horizon_end_session']==sample[1][1+h]['session_date']
    assert r['reference_price']=='110' and Decimal(r['entry_gap_pct'])==10


def test_nontrading_days_early_close_and_strict_open_availability(sample):
    s,rows,cal=sample
    assert rows[3]['session_date']=='2024-11-29' # Thanksgiving is absent.
    assert timestamp(cal['sessions'][3]['closes_at']).hour==18
    s['trigger'].update(session_date=rows[3]['session_date'],available_at='2024-11-29T19:00:00+00:00')
    result,_=calc(sample)
    assert select(result,OPEN,0)['reference_session']=='2024-12-02'
    s['trigger']['available_at']=cal['sessions'][4]['opens_at']
    assert select(calc(sample)[0],OPEN,0)['reference_session']=='2024-12-03'


@pytest.mark.parametrize('direction,fav,adv,mfeatr,maeatr',[('LONG',20,10,10,5),('SHORT',10,20,5,10)])
def test_excursions_exclude_signal_extremes_and_use_signal_atr(sample,direction,fav,adv,mfeatr,maeatr):
    sample[0]['trigger']['direction']=direction
    r=select(calc(sample)[0],CLOSE,1)
    assert Decimal(r['mfe_pct'])==fav and Decimal(r['mae_pct'])==adv
    assert Decimal(r['mfe_atr'])==mfeatr and Decimal(r['mae_atr'])==maeatr
    assert Decimal(r['max_high'])==120 and Decimal(r['min_low'])==90
    assert r['daily_high_low_order']=='UNKNOWN'
    assert Decimal(r['direction_normalized_return_pct'])==(15 if direction=='LONG' else -15)
    assert 'realized_r' not in r and 'fills' not in r


def test_open_includes_reference_day_range_and_fixed_signal_atr(sample):
    r=select(calc(sample)[0],OPEN,0)
    assert Decimal(r['mfe_atr'])==5 and Decimal(r['mae_atr'])==10
    assert Decimal(r['mfe_pct'])==pytest.approx(Decimal(100)/11)
    assert Decimal(r['mae_pct'])==pytest.approx(Decimal(200)/11)
    sample[1][1]['atr14']='999999'
    assert r==select(calc(sample)[0],OPEN,0)


@pytest.mark.parametrize('direction,zero_key',[('LONG','mfe_pct'),('SHORT','mae_pct')])
def test_nonnegative_excursions_clamp_unreached_reference_to_zero(sample,direction,zero_key):
    sample[0]['trigger']['direction']=direction
    sample[1][1].update(open='98',high='99',low='97',close='98')
    r=select(calc(sample)[0],CLOSE,1)
    assert Decimal(r[zero_key])==0


@pytest.mark.parametrize('value',[None,'0','-1','NaN'])
def test_missing_invalid_atr_retains_raw_path_as_partial(sample,value):
    sample[0]['features']['atr14']=value
    r=select(calc(sample)[0],CLOSE,1)
    assert r['outcome_status']=='PARTIAL' and r['unavailable_reasons']==['MISSING_SIGNAL_ATR']
    assert Decimal(r['forward_return_pct'])==15 and r['mfe_atr'] is None


def test_missing_intermediate_and_endpoint_never_compress_calendar(sample):
    s,rows,cal=sample
    missing=rows.pop(3)
    result,_=calc(sample)
    assert select(result,CLOSE,1)['outcome_status']=='AVAILABLE'
    r=select(result,CLOSE,5)
    assert r['horizon_end_session']==cal['sessions'][5]['session_date']
    assert r['forward_return_pct'] is None and 'MISSING_EXPECTED_SESSION' in r['unavailable_reasons']
    rows.insert(3,missing);rows.pop(5)
    assert 'MISSING_EXPECTED_SESSION' in select(calc(sample)[0],CLOSE,5)['unavailable_reasons']


def test_shorter_horizons_survive_insufficient_endpoint_coverage(sample):
    del sample[1][11:]
    result,_=calc(sample)
    assert select(result,CLOSE,10)['outcome_status']=='AVAILABLE'
    assert select(result,CLOSE,20)['unavailable_reasons']==['INSUFFICIENT_FUTURE_COVERAGE']


def test_last_session_signal_retained_with_all_outcomes_unavailable(sample):
    s,rows,cal=sample;s['trigger'].update(session_date=rows[-1]['session_date'],available_at=(timestamp(cal['sessions'][-1]['closes_at'])+timedelta(hours=1)).isoformat())
    result,_=calc(sample)
    assert len(result)==9 and all(r['signal_id']=='original-signal' for r in result)
    assert all(r['outcome_status']=='UNAVAILABLE' for r in result)
    assert 'NO_ELIGIBLE_REFERENCE_SESSION' in select(result,OPEN,0)['unavailable_reasons']


@pytest.mark.parametrize('problem',['price','identity','duplicate','off_calendar','direction','premature'])
def test_incompatible_inputs_fail_explicitly(sample,problem):
    s,rows,cal=sample
    if problem=='price':s['price_dataset_sha256']='foreign'
    if problem=='identity':rows[3]['security_id']='GOOGL'
    if problem=='duplicate':rows.insert(3,deepcopy(rows[2]))
    if problem=='off_calendar':rows[3]['session_date']='2024-11-28'
    if problem=='direction':s['trigger']['direction']='UNDEFINED'
    if problem=='premature':s['trigger']['available_at']=cal['sessions'][0]['opens_at']
    with pytest.raises(ValueError):calc(sample)


def test_invalid_price_only_invalidates_windows_that_use_it(sample):
    sample[1][5]['close']='NaN'
    result,_=calc(sample)
    assert select(result,CLOSE,1)['outcome_status']=='AVAILABLE'
    assert 'INVALID_PRICE' in select(result,CLOSE,5)['unavailable_reasons']


def test_same_signal_same_endpoint_reference_comparisons(sample):
    _,paired=calc(sample)
    r=next(r for r in paired if r['signal_close_horizon']==5)
    assert r['next_open_horizon']==4
    assert r['horizon_end_session']==sample[1][5]['session_date']
    close,opened=map(Decimal,(r['close_reference_return_pct'],r['open_reference_return_pct']))
    assert close==5 and opened==pytest.approx((Decimal(105)/110-1)*100)
    assert (1+close/100)==pytest.approx(Decimal('1.1')*(1+opened/100))
    assert r['direction_normalized_difference_pct'] is not None


def test_delayed_reference_does_not_compare_endpoint_before_reference(sample):
    sample[0]['trigger']['available_at']=sample[2]['sessions'][4]['closes_at']
    _,paired=calc(sample)
    assert paired[0]['status']=='UNAVAILABLE' and 'ENDPOINT_BEFORE_OPEN_REFERENCE' in paired[0]['unavailable_reasons']


def test_decimal_context_cannot_change_measurements(sample):
    expected=calc(sample)
    with localcontext() as ctx:
        ctx.prec=6
        assert calc(sample)==expected


def test_source_supported_corporate_actions_bounds_and_global_unknown_dates(sample):
    from test_events import event
    from equity_research.events.alignment import align_event
    s,rows,cal=sample
    known=event('DIVIDEND',effective=rows[1]['session_date']);known['event_id']='known'
    unknown=event('DIVIDEND');unknown['event_id']='unknown'
    bounded=deepcopy(unknown);bounded['event_id']='bounded'
    bounded['payload']['effective_date_bounds']={'not_before':rows[2]['session_date'],'not_after':rows[4]['session_date'],
        'evidence_status':'VERIFIED','source_ids':['synthetic-source']}
    unrelated=deepcopy(bounded);unrelated['event_id']='unrelated'
    unrelated['payload']['effective_date_bounds'].update(not_before=rows[30]['session_date'],not_after=rows[35]['session_date'])
    actions=[known,unknown,bounded,unrelated]
    measured,_=calc(sample,actions=actions,alignments=[align_event(e,cal) for e in actions])
    one=select(measured,CLOSE,1)['corporate_action_uncertainty'];five=select(measured,CLOSE,5)['corporate_action_uncertainty']
    assert [e['event_id'] for e in one['known_effective_actions']]==['known']
    assert one['bounded_overlap_uncertainty']==[]
    assert [e['event_id'] for e in five['bounded_overlap_uncertainty']]==['bounded']
    assert len(one['global_unknown_effective_dates'])==3
    assert all(e['event_id']!='unknown' for e in five['known_effective_actions']+five['bounded_overlap_uncertainty'])
    assert one['comparability_review_required'] and one['inventory_completeness']=='UNKNOWN'


def sources_for(sample,signals):
    return [SimpleNamespace(signals=signals,calendar=sample[2])]


def test_overlapping_attempts_retain_unique_signals_and_cluster_dependence(sample):
    s,rows,cal=sample
    other=deepcopy(s);other['signal_id']='overlap';other['setup']['setup_id']='second-attempt'
    later=deepcopy(s);later['signal_id']='later';later['trigger'].update(session_date=rows[35]['session_date'],available_at=cal['sessions'][35]['closes_at'])
    clusters=cluster_signals(sources_for(sample,[s,other,later]),Configuration())
    assert len(clusters)==3 and len({r['event_cluster_id'] for r in clusters})==2
    assert len({r['same_session_cluster_id'] for r in clusters})==2
    assert next(c for c in clusters if c['signal_id']==s['signal_id'])['overlapping_signal_ids']==['overlap']


def test_conditional_stats_warnings_and_all_unavailable_rows_stay_visible(sample):
    s,_,_=sample
    outcomes,paired=calc(sample);clusters=cluster_signals(sources_for(sample,[s]),Configuration())
    link={'link_sha256':'captured-link','status':'UNAVAILABLE','reason':'ORIGINAL_UNKNOWN'}
    summary=summarize(outcomes,[link],clusters,paired,Configuration())
    r=next(r for r in summary['by_context'] if r['reference_type']==CLOSE and r['horizon']==1)
    assert r['context_descriptor']=='UNAVAILABLE' and r['sample_count']==1
    assert Decimal(r['direction_normalized_return_pct']['mean'])==15
    assert r['signal_cluster_count']==1 and 'INSUFFICIENT_EVENT_CLUSTERS' in r['warnings']
    for r in outcomes:r.update(outcome_status='UNAVAILABLE',forward_return_pct=None,direction_normalized_return_pct=None,unavailable_reasons=['MISSING_EXPECTED_SESSION'])
    result=summarize(outcomes,[link],clusters,[],Configuration())['by_stock_strategy'][0]
    assert result['sample_count']==result['missing_outcome_count']==1 and result['available_outcome_count']==0
    assert result['raw_return_pct']['mean'] is None


def test_zero_signals_have_zero_counts_not_fabricated_results():
    summary=summarize([],[],[],[],Configuration())
    assert summary['by_stock_strategy']==[] and summary['dependence']['raw_signal_count']==0


@pytest.mark.parametrize('kwargs',[{'close_horizons':(0,)},{'open_horizons':(-1,)},{'close_horizons':(1,1)},
    {'open_horizons':(True,)},{'close_horizons':(),'open_horizons':()},{'minimum_clusters':0}])
def test_invalid_definitions(kwargs):
    with pytest.raises(ValueError):Configuration(**kwargs)


@pytest.fixture(scope='module')
def strategy_inputs(tmp_path_factory):
    from test_history import MockIB,ib_provider,bars,FIXED
    from equity_research.history.contracts import Security
    from equity_research.history.cache import HistoryCache,history
    from equity_research.history.dataset import freeze
    from equity_research.events.model import freeze_events
    from equity_research.events.dataset import freeze_study
    from equity_research.swing import Configuration as StrategyConfig,FAILED,freeze_strategy
    root=tmp_path_factory.mktemp('outcome-source')
    security=Security('AAPL','synthetic-AAPL','synthetic identity','AAPL','AAPL','NASDAQ','XNAS')
    start,end='2024-10-01','2024-12-20'
    frame=bars(start,end,adjusted=False).astype(float)
    for i,day in enumerate(frame.index):
        close=100+i
        frame.loc[day,['Open','High','Low','Close','Volume']]=[close-.25,close+1,close-1,close,1000000]
    frame.iloc[25,frame.columns.get_indexer(['Open','High','Low','Close'])]=[125,129,124,128]
    frame.iloc[26,frame.columns.get_indexer(['Open','High','Low','Close'])]=[126,127,122,123]
    cache=HistoryCache(root/'cache')
    assert history(cache,ib_provider(MockIB(frame=frame)),[security],start,end,clock=lambda:FIXED)['status']=='SUCCESS'
    freeze(cache,'ibkr',[security],start,end,root/'prices',clock=lambda:FIXED)
    freeze_events([],[],root/'events');freeze_study(root/'prices',root/'events','AAPL',root/'study')
    freeze_strategy(root/'study',None,root/'signals',configuration=StrategyConfig(FAILED),start=start,end=end)
    freeze_strategy(root/'study',None,root/'zero',start=start,end=end)
    assert FrozenSignals(*read_bundle(root/'signals')).signals
    return root


def forbid_regeneration(monkeypatch):
    import equity_research.swing.engine as engine
    import equity_research.swing.dataset as dataset
    from equity_research.market_context import MarketContext
    def forbidden(*args,**kwargs):raise AssertionError('signal regeneration/future context lookup forbidden')
    monkeypatch.setattr(engine,'evaluate',forbidden)
    monkeypatch.setattr(dataset,'_results',forbidden)
    monkeypatch.setattr(MarketContext,'context_as_of',forbidden)


def test_immutable_bundle_preserves_original_signals_context_and_no_regeneration(strategy_inputs,tmp_path,monkeypatch):
    forbid_regeneration(monkeypatch)
    source=FrozenSignals(*read_bundle(strategy_inputs/'signals'))
    original=read_bundle(strategy_inputs/'signals')
    a=freeze_outcomes([strategy_inputs/'signals'],tmp_path/'a')
    b=freeze_outcomes([strategy_inputs/'signals'],tmp_path/'b')
    assert a==b
    loaded=load_outcomes(tmp_path/'a')
    assert loaded.content_sha256==a['bundle_sha256']
    assert {s['signal_id'] for s in loaded.results['signal_inventory.json']}=={s['signal_id'] for s in source.signals}
    assert loaded.results['context_links.json']==sorted(source.links,key=lambda r:r['signal_id'])
    assert read_bundle(strategy_inputs/'signals')==original
    assert loaded.results['quality_report.json']['signal_generation']=='NOT_RUN'
    assert all(r['price_basis']['price_basis']=='IBKR_TRADES_SPLIT_ADJUSTED_DOCUMENTED' and not r['price_basis']['verified'] for r in loaded.results['outcomes.json'])
    with pytest.raises(FileExistsError):freeze_outcomes([strategy_inputs/'signals'],tmp_path/'a')
    changed=loaded.results;changed['signal_inventory.json'].clear()
    assert loaded.results['signal_inventory.json']


@pytest.mark.parametrize('component',['outcomes.json','signal_inventory.json','dependency_clusters.json','context_links.json','outcome_definitions.json','outcome_manifest.json'])
def test_resealed_outcome_tampering_rejected(strategy_inputs,tmp_path,component):
    freeze_outcomes([strategy_inputs/'signals'],tmp_path/'good')
    files,_=read_bundle(tmp_path/'good');raw=json.loads(files[component])
    if component=='outcome_definitions.json':raw['close_horizons']=[1]
    elif component=='outcome_manifest.json':raw['definition_sha256']='0'*64
    else:raw[0]['forged']='value'
    files[component]=encode(raw);write_bundle(tmp_path/'bad',files)
    with pytest.raises(ValueError):load_outcomes(tmp_path/'bad')


def test_source_signal_or_price_identity_mismatch_rejected(strategy_inputs,tmp_path):
    files,_=read_bundle(strategy_inputs/'signals')
    original=json.loads(files['signals.json']);original[0]['security_id']='GOOGL'
    files['signals.json']=encode(original);write_bundle(tmp_path/'wrong',files)
    with pytest.raises(ValueError,match='signal identity'):freeze_outcomes([tmp_path/'wrong'],tmp_path/'out')
    assert not (tmp_path/'out').exists()


def test_zero_inventory_and_duplicate_source_contract(strategy_inputs,tmp_path):
    freeze_outcomes([strategy_inputs/'zero'],tmp_path/'zero')
    r=load_outcomes(tmp_path/'zero').results
    assert r['signal_inventory.json']==[] and r['outcomes.json']==[]
    assert r['quality_report.json']['original_signal_count']==0
    with pytest.raises(ValueError,match='duplicate strategy bundle'):
        freeze_outcomes([strategy_inputs/'signals',strategy_inputs/'signals'],tmp_path/'dup')


def test_cli_requested_references_horizons_and_offline_reader_without_sdks(strategy_inputs,tmp_path,monkeypatch):
    from equity_research.cli import main
    forbid_regeneration(monkeypatch)
    assert main(['outcomes','--strategy',str(strategy_inputs/'signals'),'--references','open','--horizons','0','5','--output',str(tmp_path/'output')])==0
    loaded=load_outcomes(tmp_path/'output')
    assert {r['reference_type'] for r in loaded.results['outcomes.json']}=={OPEN}
    assert {r['horizon'] for r in loaded.results['outcomes.json']}=={0,5}
    import os,subprocess,sys
    code='''
import importlib.abc,sys,socket
class Deny(importlib.abc.MetaPathFinder):
 def find_spec(self,name,*args):
  if name.split('.')[0] in {'ib_async','yfinance','pandas','numpy','pyarrow','exchange_calendars'} or name.startswith('equity_research.providers') or name.startswith('equity_research.swing'):
   raise AssertionError('forbidden import: '+name)
sys.meta_path.insert(0,Deny())
def forbidden(*a,**k):raise AssertionError('network forbidden')
socket.socket.connect=forbidden
socket.socket.connect_ex=forbidden
socket.create_connection=forbidden
from equity_research.outcomes import load_outcomes
print(load_outcomes(sys.argv[1]).content_sha256)
'''
    result=subprocess.run([sys.executable,'-c',code,str(tmp_path/'output')],env={**os.environ,'PYTHONPATH':str(Path(__file__).parents[1]/'src')},capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    assert loaded.content_sha256 in result.stdout


def test_missing_source_does_not_fetch_or_create_output(tmp_path):
    from equity_research.cli import main
    assert main(['outcomes','--strategy',str(tmp_path/'missing'),'--output',str(tmp_path/'output')])==2
    assert not (tmp_path/'output').exists()


def test_atr_requires_original_signal_time_cutoff(sample):
    sample[0]['feature_observation_cutoffs']['atr14']=sample[1][3]['session_date']
    with pytest.raises(ValueError,match='ATR observation'):calc(sample)
    sample[0]['feature_observation_cutoffs']['atr14']=None
    assert select(calc(sample)[0],CLOSE,1)['outcome_status']=='PARTIAL'


@pytest.mark.parametrize('state',['UPTREND','DOWNTREND','MIXED','UNCLASSIFIED',None])
def test_context_states_are_preserved_without_gates(sample,state):
    s,_,_=sample
    outcomes,paired=calc(sample);clusters=cluster_signals(sources_for(sample,[s]),Configuration())
    link={'link_sha256':'captured-link','status':'AVAILABLE_UNDER_RECONSTRUCTED_ASSUMPTION','context':{'descriptive_state':state}}
    summary=summarize(outcomes,[link],clusters,paired,Configuration())
    assert len(outcomes)==9
    assert {r['context_descriptor'] for r in summary['by_context']}=={state or 'UNDESCRIBED'}


from test_market_context import inputs as context_prices


def test_original_available_context_embedded_and_preserved(strategy_inputs,context_prices,tmp_path,monkeypatch):
    from equity_research.market_context import freeze_market_context
    from equity_research.swing import freeze_strategy,Configuration as StrategyConfig,FAILED
    freeze_market_context({s:context_prices for s in ('SPY','QQQ','RSP')},'2024-10-01','2024-12-03',tmp_path/'context')
    freeze_strategy(strategy_inputs/'study',tmp_path/'context',tmp_path/'signals',configuration=StrategyConfig(FAILED),start='2024-10-01',end='2024-12-20')
    captured=FrozenSignals(*read_bundle(tmp_path/'signals'))
    assert any(l['status']!='UNAVAILABLE' for l in captured.links)
    forbid_regeneration(monkeypatch)
    freeze_outcomes([tmp_path/'signals'],tmp_path/'outcomes')
    import shutil
    shutil.rmtree(tmp_path/'signals');shutil.rmtree(tmp_path/'context')
    assert load_outcomes(tmp_path/'outcomes').results['context_links.json']==sorted(captured.links,key=lambda r:r['signal_id'])


def test_hand_summary_dispersion_and_cluster_counts_are_separate(sample):
    s,_,_=sample
    outcomes,_=calc(sample)
    a=select(outcomes,CLOSE,1);b=deepcopy(a);b.update(signal_id='second',forward_return_pct='-5',direction_normalized_return_pct='-5')
    other=deepcopy(s);other['signal_id']='second'
    clusters=cluster_signals(sources_for(sample,[s,other]),Configuration())
    result=summarize([a,b],[{'link_sha256':'captured-link','status':'UNAVAILABLE'}],clusters,[],Configuration())['by_stock_strategy'][0]
    metrics=result['direction_normalized_return_pct']
    assert {k:Decimal(metrics[k]) for k in ('mean','median','population_stddev')}=={
        'mean':Decimal(5),'median':Decimal(5),'population_stddev':Decimal(10)}
    assert {k:metrics[k] for k in ('count','positive','negative','zero')}=={'count':2,'positive':1,'negative':1,'zero':0}
    assert result['sample_count']==2 and result['available_cluster_count']==1


@pytest.mark.parametrize('flag,clean_count',[(True,0),(False,1)])
def test_sensitivity_counts_do_not_delete_raw_unknown_date_inventory(sample,flag,clean_count):
    rows,_=calc(sample);r=select(rows,CLOSE,1)
    r['corporate_action_uncertainty']['comparability_review_required']=flag
    r['corporate_action_uncertainty']['global_unknown_effective_dates']=[{'event_id':'unknown-ex-date'}]
    clusters=cluster_signals(sources_for(sample,[sample[0]]),Configuration())
    result=summarize([r],[{'link_sha256':'captured-link','status':'UNAVAILABLE'}],clusters,[],Configuration())['by_stock_strategy'][0]
    assert result['sample_count']==result['available_outcome_count']==1
    assert result['sensitivity_excluding_known_or_bounded_actions']['available_count']==clean_count


def test_multiple_bundle_input_order_does_not_change_hash(strategy_inputs,tmp_path):
    paths=[strategy_inputs/'signals',strategy_inputs/'zero']
    a=freeze_outcomes(paths,tmp_path/'a');b=freeze_outcomes(paths[::-1],tmp_path/'b')
    assert a==b
