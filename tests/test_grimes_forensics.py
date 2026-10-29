"""Small deterministic offline fixtures for PR9B's new diagnostics only."""
from copy import deepcopy
from datetime import datetime, timedelta
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from equity_research import grimes_forensics as f
from equity_research.grimes_forensic_reports import public_comparison
from equity_research.ingestion.frames import pack
from equity_research.ingestion.storage import encode, read_bundle, write_bundle


def fixture(direction='LONG'):
    sessions = [{'session_date': f'2026-10-{d}', 'opens_at': f'2026-10-{d}T13:30:00+00:00',
                 'closes_at': f'2026-10-{d}T20:00:00+00:00'} for d in range(19, 23)]
    clock = {'name': 'test', 'assumed_action_clocks': {'a': '2026-10-18T19:21:00+00:00',
             'b': '2026-10-19T22:20:00+00:00'}}
    events = [{'event_id': 'a:add', 'type': 'OPEN_NEW_POSITION', 'source': {'alert_id': 'a'},
               'published_at': '2026-10-18T19:20:00+00:00', 'stop': '95', 'setup_after': 'ENTERABLE'},
              {'event_id': 'b:stop', 'type': 'STOP_CHANGED', 'source': {'alert_id': 'b'},
               'published_at': '2026-10-19T22:19:00+00:00', 'stop': '90', 'previous_stop': '95', 'setup_after': 'ENTERABLE'}]
    trade = {'trade_id': 'TEST-001', 'symbol': 'TEST', 'direction': direction, 'initial_stop': '95',
             'position_state': 'OPEN', 'setup_availability': 'ENTERABLE', 'events': events}
    rows = {s['session_date']: {'open': '100', 'high': '102', 'low': '94', 'close': '96', 'volume': '10'} for s in sessions}
    h1 = {'status': 'CONSTRUCTED', 'entry_session': '2026-10-19', 'entry_at': sessions[0]['opens_at'],
          'entry_kind': 'OPEN', 'entry_price': 100, 'geometry': {'reference_risk': 5}, 'construction_support': 0}
    evidence = SimpleNamespace(features=lambda *args: ('2026-10-16', {'atr14': {'value': 2}}))
    return trade, clock, rows, {'sessions': sessions}, '2026-10-21T22:00:00+00:00', h1, evidence


def test_recovered_touch_does_not_become_a_closing_violation_or_retroactive_stop():
    t,c,r,cal,end,h1,_ = fixture(); before = deepcopy((t,c,r,cal,h1))
    bars = f.scan(t,c,r,cal,end,h1['entry_session'])
    assert bars[0]['range_breach'] and not bars[0]['close_breach']
    assert bars[0]['known_stop_at_open'] == 95 and bars[1]['known_stop_at_open'] == 90
    assert bars[0]['post_last_touch_entry_price_bound'] == [95,102]
    assert bars[0]['stop_endpoint_excluded']
    close = f.close_diagnostic(t,h1,c,r,cal,end,'CLOSE_CONFIRMATION')
    assert close['first_close_violation'] is None
    assert close['assessment']['category'] == 'FULLY_COMPATIBLE'
    assert (t,c,r,cal,h1) == before


def test_adverse_close_rules_out_every_positive_risk_entry_at_old_stop():
    t,c,r,cal,end,h1,_ = fixture();r['2026-10-19']['close']='94.5'
    scan = f.scan(t,c,r,cal,end,h1['entry_session'])
    assert scan[0]['close_breach'] and scan[0]['post_last_touch_entry_price_bound'] is None
    p=f.close_diagnostic(t,h1,c,r,cal,end,'CLOSE_CONFIRMATION')
    assert p['assessment']['category']=='ROBUST_CONFLICT'
    assert p['exposure_end_bound']=='2026-10-19T20:00:00+00:00'


def test_unconditional_next_open_commitment_cannot_be_cancelled_by_evening_revision():
    t,c,r,cal,end,h1,_ = fixture();r['2026-10-19']['close']='94.5'
    # New90 stop is protective at Tuesday100 Open; strict exit still happens.
    p=f.close_diagnostic(t,h1,c,r,cal,end,'NEXT_OPEN_AFTER_CLOSE')
    assert p['exposure_end_bound']=='2026-10-20T13:30:00+00:00'
    assert p['observations'][0]['status']=='ACTIVE_COMPATIBLE'
    assert p['observations'][-1]['status']=='CONTINUATION_CONFLICT'
    assert not p['committed_exit_pending']
    pending=f.close_diagnostic(t,h1,c,r,cal,'2026-10-19T23:00:00+00:00','NEXT_OPEN_AFTER_CLOSE')
    assert pending['committed_exit_pending']
    assert pending['assessment']['category']=='FULLY_COMPATIBLE'


def test_drop_after_hypothetical_exit_remains_unresolved_not_a_new_conflict():
    t,c,r,cal,end,h1,_ = fixture();r['2026-10-19']['close']='94.5'
    t['events'][1]['type']='DROPPED';t['position_state']='CLOSED'
    p=f.close_diagnostic(t,h1,c,r,cal,end,'CLOSE_CONFIRMATION')
    assert p['assessment']['category']=='UNRESOLVED'
    assert p['observations'][0]['status']=='DROP_AFTER_MODEL_EXIT_CAUSE_UNRESOLVED'


def test_short_direction_uses_high_and_reverse_close_sign():
    t,c,r,cal,end,h1,_ = fixture('SHORT');t['initial_stop']='105';t['events']=t['events'][:1]
    h1['geometry']['reference_risk']=5
    r['2026-10-19'].update(high='106',close='104')
    b=f.scan(t,c,r,cal,end,h1['entry_session'])[0]
    assert b['range_breach'] and not b['close_breach']
    assert b['post_last_touch_entry_price_bound']==[94,105]


def test_missing_required_session_fails_instead_of_compressing_or_filling():
    t,c,r,cal,end,h1,_ = fixture();del r['2026-10-20']
    with pytest.raises(ValueError,match='missing required'):
        f.close_diagnostic(t,h1,c,r,cal,end,'CLOSE_CONFIRMATION')


def test_delayed_reclaim_waits_for_bar_availability_and_uses_known_activation_stop():
    t,c,r,cal,end,h1,e = fixture()
    p=f.delayed_candidate(t,c,h1,r,cal,end,e,f.RULES[0])
    assert p['trigger_available_after']=='2026-10-19T21:00:00+00:00'
    assert p['entry_at']=='2026-10-20T13:30:00+00:00'
    assert p['reported_stop_at_entry']==90 and p['geometry']['reference_risk']==10
    assert p['source_actions_before_activation']==['b:stop']
    assert p['management'][0]['assessment']['category']=='UNRESOLVED'
    assert p['post_activation_assessment']['category']=='NO_LATER_SOURCE_ALERTS'


def test_delayed_entry_rejects_nonpositive_risk_without_later_repair():
    t,c,r,cal,end,h1,e = fixture();r['2026-10-20']['open']='89'
    p=f.delayed_candidate(t,c,h1,r,cal,end,e,f.RULES[0])
    assert p['status']=='REJECTED_NONPROTECTIVE_ENTRY' and not p['management']
    h1['geometry']['reference_risk']=0
    with pytest.raises(ValueError,match='positive protected'):
        f.close_diagnostic(t,h1,c,r,cal,end,'CLOSE_CONFIRMATION')


def test_trigger_horizon_is_three_completed_sessions_and_censoring_is_not_no_trade():
    t,c,r,cal,end,h1,e = fixture();t['events']=t['events'][:1]
    for row in r.values():row['low']='96'
    r['2026-10-22']['low']='94'
    assert f.delayed_candidate(t,c,h1,r,cal,'2026-10-22T22:00:00+00:00',e,f.RULES[0])['status']=='NO_OBSERVED_TRIGGER'
    r['2026-10-21']['low']='94'
    p=f.delayed_candidate(t,c,h1,r,cal,end,e,f.RULES[0])
    assert p['status']=='TRIGGER_OBSERVED_ENTRY_RIGHT_CENSORED'


def intraday_fixture():
    windows=[];prices={};sessions=[]
    for symbol,day,stop in [('CLMT','2026-10-19',55.25),('TEVA','2026-10-21',40.4),('GME','2026-10-22',25.01),('GME','2026-10-23',24.78)]:
        start=datetime.fromisoformat(day+'T13:30:00+00:00')
        bars=[{'date':pack(start+timedelta(minutes=5*i)),**{k:pack(v) for k,v in
            {'open':stop+1,'high':stop+2,'low':stop-1 if i==10 else stop+.5,'close':stop+1,'volume':1}.items()}} for i in range(78)]
        windows.append({'symbol':symbol,'session':day,'con_id':1,'status':'SUCCESS','native_bars':bars,'started_at':'2026-10-28T00:00:00+00:00',
            'completed_at':'2026-10-28T00:00:01+00:00','parameters':{'barSizeSetting':'5 mins','whatToShow':'TRADES','useRTH':True,'keepUpToDate':False},'errors':[]})
        prices.setdefault(symbol,[]).append({'session_date':day,'open':str(stop+1),'high':str(stop+2),'low':str(stop-1),'close':str(stop+1)})
        sessions.append({'session_date':day,'opens_at':start.isoformat(),'closes_at':(start+timedelta(hours=6,minutes=30)).isoformat()})
    return {'windows':windows},prices,{'sessions':sessions}


def test_intraday_last_touch_is_a_bar_bound_not_a_fill_or_precise_second():
    cap,prices,cal=intraday_fixture()
    r=f.intraday_observations(cap,prices,cal)
    assert len(r)==4 and r[0]['full_protected_bars_after_last_touch']==67
    assert not r[0]['actual_entry_identified'] and r[0]['intrabar_order_unresolved']
    cap['windows'][0]['native_bars'].pop(1)
    with pytest.raises(ValueError,match='incomplete or nonchronological'):
        f.intraday_observations(cap,prices,cal)


def test_intraday_failure_is_retained_and_cannot_be_promoted_to_observed_tail():
    cap,prices,cal=intraday_fixture();cap['windows'][0].update(status='TIMEOUT',native_bars=[])
    out=f.intraday_observations(cap,prices,cal)[0]
    assert out['status']=='TIMEOUT' and 'protected_tail_price_range' not in out


def test_offline_loader_rejects_resealed_derived_output_and_replay_is_identical(tmp_path,monkeypatch):
    parent={'evidence.json':encode({'source':'immutable'})};ph=write_bundle(tmp_path/'parent',parent)
    intraday={'capture.json':encode({'windows':[]})};ih=write_bundle(tmp_path/'capture',intraday)
    expected={'parent-evidence.json':parent['evidence.json'],'parent-hashes.json':encode(ph),
              'intraday-capture.json':intraday['capture.json'],'intraday-hashes.json':encode(ih),
              'documentary.json':encode([]),'forensics.json':encode({'compatible':False})}
    def derive(p,h,i,j,d):
        assert p==parent and h==ph and i==intraday and j==ih and d==[]
        return expected
    monkeypatch.setattr(f,'_files',derive)
    seal=write_bundle(tmp_path/'study',expected)
    files,hashes=f.load(tmp_path/'study')
    assert write_bundle(tmp_path/'replay',files)==seal==hashes
    changed=deepcopy(files);changed['forensics.json']=encode({'compatible':True})
    write_bundle(tmp_path/'resealed',changed)
    with pytest.raises(ValueError,match='semantic output mismatch'):
        f.load(tmp_path/'resealed')
    assert read_bundle(tmp_path/'parent')==(parent,ph)


def test_live_capture_only_uses_four_fixed_windows_and_disconnects_with_mock_backend():
    import asyncio
    path=Path(__file__).parents[1]/'scripts/capture_grimes_forensic_intraday.py'
    spec=importlib.util.spec_from_file_location('forensic_capture',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    calls=[]
    class Backend:
        errors=[]
        async def connect(self,*args):calls.append(('connect',args))
        async def qualify(self,security):
            calls.append(('qualify',security.con_id))
            return [SimpleNamespace(conId=security.con_id,symbol=security.symbol,secType='STK',exchange='SMART',primaryExchange=security.primary_exchange,currency='USD')]
        async def historical(self,contract,params):calls.append(('historical',params));return []
        def disconnect(self):calls.append(('disconnect',))
    class Pacer:
        async def wait(self,*args):pass
    result=asyncio.run(m.capture(Backend(),port=7496,client_id=17,pacer=Pacer()))
    assert len(result['windows'])==4 and all(w['status']=='EMPTY_RESPONSE' for w in result['windows'])
    assert calls[-1]==('disconnect',) and sum(c[0]=='historical' for c in calls)==4
    assert all(c[1]['whatToShow']=='TRADES' and c[1]['useRTH'] for c in calls if c[0]=='historical')


def test_ambiguous_qualification_does_not_request_history():
    import asyncio
    path=Path(__file__).parents[1]/'scripts/capture_grimes_forensic_intraday.py'
    spec=importlib.util.spec_from_file_location('forensic_capture2',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    class Backend:
        errors=[]
        disconnected=False
        async def connect(self,*args):pass
        async def qualify(self,*args):return []
        async def historical(self,*args):raise AssertionError('must not request ambiguous contract')
        def disconnect(self):self.disconnected=True
    b=Backend();r=asyncio.run(m.capture(b,port=7496,client_id=17,pacer=None))
    assert b.disconnected and all(w['status']=='IDENTITY_REJECTED' for w in r['windows'])


def test_public_pilot_recomputes_close_diagnostics_for_all_26_without_native_or_network():
    from equity_research.ingestion.calendar import schedule
    from equity_research.grimes_forensic_reports import four_report, cross_report
    root=Path(__file__).parents[1]
    public=json.loads((root/'docs/evidence/pr9b-forensics-v1/forensic_comparison.json').read_bytes())
    before=deepcopy(public)
    old=json.loads((root/'docs/evidence/pr9a-reconstruction-v1/episodes.json').read_bytes())
    assert len(public['episodes'])==26
    assert {e['symbol']:e['source'] for e in public['episodes']}=={e['symbol']:e['source'] for e in old}
    calendar=schedule('2026-10-15','2026-11-09')
    for e in public['episodes']:
        rows={r['session_date']:r for r in e['market_window']}
        for c in e['clocks']:
            clocks={ev['source']['alert_id']: d['assumed_clock'] for ev,d in zip(e['source']['events'],c['source_decisions'])}
            clock={'assumed_action_clocks':clocks}
            h1=next(p for p in c['original_candidates'] if p['hypothesis']=='H1_NEXT_OPEN')
            for policy in ('CLOSE_CONFIRMATION','NEXT_OPEN_AFTER_CLOSE'):
                if not c['stop_diagnostics']:continue
                expected=next(p for p in c['stop_diagnostics'] if p['policy']==policy)
                assert f.close_diagnostic(e['source'],h1,clock,rows,calendar,public['cutoff'],policy)==expected
    assert four_report(public).encode()==(root/'docs/reports/GRIMES_FOUR_TRADE_FORENSICS.md').read_bytes()
    assert cross_report(public).encode()==(root/'docs/reports/GRIMES_CROSS_TRADE_INFERENCE.md').read_bytes()
    assert before==public
    assert encode(public)==encode(public_comparison(public))


def test_real_pilot_failure_types_intraday_bounds_and_source_model_separation():
    import hashlib
    root=Path(__file__).parents[1]
    r=json.loads((root/'docs/evidence/pr9b-forensics-v1/forensic_comparison.json').read_bytes())
    cases={e['symbol']:e for e in r['episodes']}
    cde,ebay=cases['CDE']['source'],cases['EBAY']['source']
    assert (cde['direction'],cde['position_state'],cde['setup_availability'],cde['current_stop'])==('SHORT','OPEN','UNDERWAY','13.90')
    assert (ebay['direction'],ebay['position_state'],ebay['setup_availability'],ebay['current_stop'])==('LONG','OPEN','ENTERABLE','117.50')
    assert cases['CDE']['model_failure_type']=='TARGET_EXIT_CONVENTION_CONFLICT'
    assert all(cases[s]['model_failure_type']=='PROTECTIVE_STOP_CONFLICT' for s in ('CLMT','TEVA','GME','EBAY'))
    assert [w['full_protected_bars_after_last_touch'] for w in r['intraday']]==[0,9,5,0]
    assert [w['post_last_touch_price_outer_bound'] for w in r['intraday']]==[[55.25,55.61],[40.4,40.62],[25.01,25.38],[24.78,24.9]]
    for s in r['summaries']:
        assert s['right_censored']==['SAIL','SLB','GE','SCCO']
        assert s['policies']['INTRADAY_HARD_STOP']['ROBUST_CONFLICT']==['CLMT','TEVA','GME','EBAY']
        assert s['policies']['CLOSE_CONFIRMATION']['ROBUST_CONFLICT']==['EBAY']
        assert len(s['policies']['CLOSE_CONFIRMATION']['FULLY_COMPATIBLE'])==11
        assert len(s['policies']['NEXT_OPEN_AFTER_CLOSE']['FULLY_COMPATIBLE'])==19
        assert all(sum(len(v) for v in cats.values())==22 for cats in s['policies'].values())
    for e in r['episodes']:
        for ev in e['source']['events']:
            if ev['source']['alert_id']=='alert-6':assert ev['published_at'] is None
    assert hashlib.sha256((root/'reports/grimes_trade_status.csv').read_bytes()).hexdigest()=='a32c812f95a51a56dc90fd8f49634b4976cd7f175fb1b326faf773ff22e4c527'


def test_wrong_parent_or_intraday_pin_rejected_before_expensive_derivation(tmp_path,monkeypatch):
    p={'source.json':encode({})};ph=write_bundle(tmp_path/'parent',p)
    i={'capture.json':encode({})};ih=write_bundle(tmp_path/'intraday',i)
    with pytest.raises(ValueError,match='PR19 sensitivity parent'):
        f._files(p,ph,i,ih,[])
    monkeypatch.setattr(f,'PARENT_SHA256',ph['bundle_sha256'])
    with pytest.raises(ValueError,match='four-window PR9B capture'):
        f._files(p,ph,i,ih,[])


def test_new_close_diagnostic_clusters_co_published_actions_once():
    t,c,r,cal,end,h1,_=fixture();r['2026-10-19']['close']='94.5'
    setup=deepcopy(t['events'][1]);setup.update(type='SETUP_CHANGED',event_id='b:underway',setup_after='UNDERWAY')
    t['events'].append(setup)
    out=f.close_diagnostic(t,h1,c,r,cal,end,'CLOSE_CONFIRMATION')
    assert out['assessment']['robust_conflict_alert_clusters']==1
    assert out['assessment']['later_alert_clusters']==1
    assert out['assessment']['final_source_state_conflict']
    assert len(out['assessment']['clusters'])==2


def test_capture_timeout_and_permission_failures_retain_safe_diagnostics_and_disconnect():
    import asyncio
    path=Path(__file__).parents[1]/'scripts/capture_grimes_forensic_intraday.py'
    spec=importlib.util.spec_from_file_location('forensic_capture3',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    class Pacer:
        async def wait(self,*args):pass
    class Backend:
        def __init__(self):self.errors=[];self.count=0;self.disconnected=False
        async def connect(self,*args):pass
        async def qualify(self,s):
            return [SimpleNamespace(conId=s.con_id,symbol=s.symbol,secType='STK',exchange='SMART',primaryExchange=s.primary_exchange,currency='USD')]
        async def historical(self,*args):
            self.count+=1
            if self.count==1:raise TimeoutError('arbitrary broker text must not be stored')
            self.errors.append({'code':354,'category':'DATA_PERMISSION'})
            return []
        def disconnect(self):self.disconnected=True
    b=Backend();out=asyncio.run(m.capture(b,port=7496,client_id=17,pacer=Pacer()))
    assert b.disconnected and out['windows'][0]['status']=='TIMEOUT'
    assert all(w['status']=='REQUEST_FAILED' for w in out['windows'][1:])
    assert 'arbitrary broker text' not in json.dumps(out)
