"""Deterministic offline boundary, state and append-only workflow regressions."""
from copy import deepcopy
from datetime import UTC,datetime
import json
from pathlib import Path

import pytest

from equity_research.comprehension.inputs import PRICE_BASIS,VOLUME_BASIS
from equity_research.ingestion.calendar import schedule
from equity_research.ingestion.storage import encode,read_bundle,write_bundle
from equity_research.prospective.inputs import make_view,validate_view,clocks,parse_known,upper
from equity_research.prospective.models import predict,stop_state,MODELS
from equity_research.prospective import workflow as w

NOW=datetime(2026,10,29,2,20,tzinfo=UTC)
CUTOFF='2026-10-19T21:01:00+00:00'


def alert(identity,seq,when,added='None',stops='None',setups='None',dropped='None'):
    return {'alert_id':identity,'source_sequence':seq,'published_at':when,'publication_precision':'MINUTE',
        'original_publication_display':when or 'UNKNOWN','source_reference':'synthetic offline source',
        'email_received_at':when,'text':f'Fixture\nAdded____\n{added}\nStop Changed____\n{stops}\nSetup Changed____\n{setups}\nDropped____\n{dropped}\n','html':''}


@pytest.fixture
def archive():
    cal=schedule('2026-07-01','2026-11-09')
    prices={};coverage={}
    for n,symbol in enumerate(('AAPL','SPY'),1):
        rows=[]
        for i,s in enumerate(cal['sessions']):
            if s['session_date']>'2026-10-26':break
            close=100+i*.02
            rows.append({'symbol':symbol,'security_id':f'test:{symbol}','session_date':s['session_date'],
                'open':str(close),'high':str(close+1),'low':str(close-1),'close':str(close),'volume':'100',
                'provider':'ibkr','price_basis':PRICE_BASIS,'volume_basis':VOLUME_BASIS})
        prices[symbol]=rows
        coverage[symbol]={'security':{'security_id':f'test:{symbol}'},'contract':{'conId':n},
            'origin':'synthetic','price_basis':PRICE_BASIS,'volume_basis':VOLUME_BASIS,'source_bundle_sha256':'synthetic'}
    row=next(r for r in prices['AAPL'] if r['session_date']=='2026-10-19');row.update(open='100',high='102',low='94',close='96')
    return {'schema_version':'grimes_prediction_archive_v1','alerts':{'schema_version':'grimes_alerts_v1','origin':'synthetic','alerts':[
        alert('a',0,'2026-10-18T15:20:00-04:00',added='AAPL added long with stop 95.00'),
        alert('b',1,'2026-10-19T18:19:00-04:00',stops='AAPL stop moved to 90.00 from 95.00')]},
        'calendar':cal,'prices':prices,'coverage':coverage,'market_observation_end':'2026-10-26',
        'source_cutoff':'2026-10-19T22:20:00+00:00','provenance':{'origin':'synthetic'}}


def test_future_alert_text_stop_and_prices_cannot_change_prediction(archive):
    original=deepcopy(archive)
    first=predict(make_view(archive,'original',CUTOFF,1),NOW.isoformat(),'RETROSPECTIVE_DRY_RUN')
    poisoned=deepcopy(archive);poisoned['alerts']['alerts'][1]['text']='UNPARSEABLE FUTURE ALERT stop 0.00'
    for rows in poisoned['prices'].values():
        for row in rows:
            if row['session_date']>'2026-10-19':row.update(open='FUTURE POISON',low='-1',close=None)
    second=predict(make_view(poisoned,'changed',CUTOFF,1),NOW.isoformat(),'RETROSPECTIVE_DRY_RUN')
    assert first==second and archive==original
    p=first['predictions'][0]
    assert p['source_state']['current_stop']=='95.00'
    assert p['source_state']['position_state']=='OPEN'
    late=p['scenarios'][-1]['models']
    assert late[0]['hypothetical_execution']['hypothetical_state']=='CLOSED_NO_REENTRY'
    assert late[1]['hypothetical_execution']['hypothetical_state']=='ACTIVE'
    assert first['historical_hypothesis_selection_is_out_of_sample'] is False


def test_predictor_rejects_future_source_or_market_inserted_in_its_view(archive):
    with pytest.raises(ValueError,match='prefix is not available'):
        make_view(archive,'x',CUTOFF,2)
    view=make_view(archive,'x',CUTOFF,1)
    row=next(r for r in archive['prices']['AAPL'] if r['session_date']=='2026-10-20')
    view['prices']['AAPL'].append(row)
    with pytest.raises(ValueError,match='future or undeclared market'):
        predict(view,NOW.isoformat(),'RETROSPECTIVE_DRY_RUN')
    view=make_view(archive,'x',CUTOFF,1);view['alerts'][0]['published_at']='2026-10-20T00:00:00+00:00'
    with pytest.raises(ValueError,match='future, duplicate'):
        validate_view(view)


def test_unknown_publication_stays_unknown_and_scenario_differences_propagate(archive):
    a=archive['alerts']['alerts'][1];a.update(published_at=None,email_received_at='2026-10-25T12:57:45+00:00',original_publication_display='Yesterday at8:57 AM')
    view=make_view(archive,'x','2026-10-25T13:00:00+00:00',2)
    result=predict(view,NOW.isoformat(),'RETROSPECTIVE_DRY_RUN')
    assert view['alerts'][1]['published_at'] is None
    trade=result['predictions'][0]
    assert trade['action_stable_across_scenarios']['A_HARD_STOP'] is False
    assert all(a['published_at'] is None for a in result['known_alerts'] if a['alert_id']=='b')


def test_unconditional_commitment_and_bounded_one_review_cannot_be_rescinded(archive):
    def change(day,**values):next(r for r in archive['prices']['AAPL'] if r['session_date']==day).update(values)
    change('2026-10-19',close='94.50')
    view=make_view(archive,'x','2026-10-20T21:01:00+00:00',2)
    trade=validate_view(view)[0];clock=clocks(view)[-1]
    c=stop_state(trade,clock,view,'C_NEXT_OPEN');d=stop_state(trade,clock,view,'D_BOUNDED_REVIEW')
    assert c['first_model_exit']['session']=='2026-10-20' and c['hypothetical_state']=='CLOSED_NO_REENTRY'
    assert d['hypothetical_state']=='ACTIVE' and d['review_count']==1
    change('2026-10-20',open='100',high='102',low='88',close='89')
    view=make_view(archive,'x','2026-10-21T21:01:00+00:00',2)
    d=stop_state(validate_view(view)[0],clocks(view)[-1],view,'D_BOUNDED_REVIEW')
    assert d['review_count']==1 and d['hypothetical_state']=='CLOSED_NO_REENTRY'
    assert d['first_model_exit']=={'session':'2026-10-21','boundary':'OPEN','reason':'COMMITTED'}


def test_missing_required_session_is_explicit_and_nonprotective_entry_is_rejected(archive):
    archive['prices']['AAPL']=[r for r in archive['prices']['AAPL'] if r['session_date']!='2026-10-19']
    view=make_view(archive,'x',CUTOFF,1)
    state=stop_state(validate_view(view)[0],clocks(view)[0],view,'A_HARD_STOP')
    assert state['hypothetical_state']=='UNRESOLVED_MISSING_REQUIRED_SESSION'
    assert state['missing_session']=='2026-10-19'


def test_forward_target_is_after_registration_not_the_old_market_cutoff(archive):
    result=predict(make_view(archive,'x',CUTOFF,1),NOW.isoformat(),'FORWARD_REGISTERED')
    assert result['target']['strictly_after']==NOW.isoformat()
    assert result['information_cutoff']==CUTOFF
    assert result['outcome']=='UNRESOLVED_NO_LATER_ALERT_IMPORTED'
    assert '2026-10-28' in result['unobserved_completed_sessions_since_market_end']


def test_prediction_reveal_evaluation_and_replay_are_append_only(tmp_path,archive):
    a=tmp_path/'archive';write_bundle(a,{'archive.json':encode(archive)})
    v=tmp_path/'view';w.prepare(a,CUTOFF,v,1)
    p=tmp_path/'prediction';ph=w.freeze(v,p,'RETROSPECTIVE_DRY_RUN',now=NOW)
    before=read_bundle(p)
    raw=tmp_path/'next.json';raw.write_bytes(encode(archive['alerts']['alerts'][1]))
    r=tmp_path/'reveal';w.reveal(p,raw,r,now=NOW)
    e=tmp_path/'evaluation';eh=w.evaluate(p,r,e)
    result=json.loads(read_bundle(e)[0]['evaluation.json'])
    assert result['source_observations'][0]['actual_source_observation']['category']=='CONTINUED_MANAGEMENT'
    models=result['source_observations'][0]['scenarios'][-1]['models']
    assert models[0]['verdict']=='CONTRADICTS_PREDICTION' and models[1]['verdict']=='SUPPORTS_PREDICTION'
    assert models[1]['point_category_correct'] is None # broad set coverage is not point accuracy
    assert read_bundle(p)==before
    assert write_bundle(tmp_path/'p-replay',w.load_prediction(p)[0])==ph
    assert w.replay_evaluation(e,p,r,tmp_path/'e-replay')==eh
    with pytest.raises(FileExistsError):w.freeze(v,p,'RETROSPECTIVE_DRY_RUN',now=NOW)
    altered=deepcopy(before[0]);x=json.loads(altered['prediction.json']);x['predictions'][0]['source_state']['position_state']='CLOSED';altered['prediction.json']=encode(x)
    write_bundle(tmp_path/'resealed',altered)
    with pytest.raises(ValueError,match='prediction semantic output mismatch'):w.load_prediction(tmp_path/'resealed')
    changed,eh=read_bundle(e);x=json.loads(changed['evaluation.json']);x['eligibility']='INVENTED';changed['evaluation.json']=encode(x)
    write_bundle(tmp_path/'bad-eval',changed)
    with pytest.raises(ValueError,match='evaluation semantic output mismatch'):w.replay_evaluation(tmp_path/'bad-eval',p,r,tmp_path/'reject')


def test_omission_does_not_close_source_and_foreign_actions_are_quarantined(archive):
    a=alert('later',0,'2026-10-20T18:00:00-04:00',added='TSLA added long with stop 100.00')
    events,excluded=parse_known({'schema_version':'grimes_alerts_v1','origin':'synthetic','alerts':[a]})
    assert not events and excluded[0]['symbol']=='TSLA'
    pred=predict(make_view(archive,'x',CUTOFF,1),NOW.isoformat(),'RETROSPECTIVE_DRY_RUN')
    actual=w.observation(events,pred['predictions'][0])
    assert actual['category']=='NOT_MENTIONED' and actual['omission_is_not_closure']
    assert pred['predictions'][0]['source_state']['position_state']=='OPEN'


def test_fresh_evaluation_rejects_old_targets_and_cannot_resolve_unknown_publication(archive):
    pred=predict(make_view(archive,'x',CUTOFF,1),NOW.isoformat(),'FORWARD_REGISTERED')
    events,_=parse_known({'schema_version':'grimes_alerts_v1','origin':'synthetic','alerts':[alert('later',0,'2026-10-20T18:00:00-04:00')]})
    old=alert('later',0,'2026-10-20T18:00:00-04:00')
    assert w.evaluate_data(pred,events,old)['eligibility']=='OUTSIDE_PREREGISTERED_WINDOW'
    unknown=alert('later',0,None);unknown['email_received_at']='2026-10-30T00:00:00+00:00'
    result=w.evaluate_data(pred,events,unknown)
    assert result['eligibility']=='UNRESOLVED_PUBLICATION_TIME' and not result['fresh_out_of_sample']
    assert all(p['verdict']=='UNRESOLVED_OR_ABSTAINED' for row in result['source_observations'] for s in row['scenarios'] for p in s['models'])


def test_pending_exit_does_not_predict_exit_before_next_open(archive):
    next(r for r in archive['prices']['AAPL'] if r['session_date']=='2026-10-19')['close']='94.5'
    pred=predict(make_view(archive,'x',CUTOFF,1),NOW.isoformat(),'RETROSPECTIVE_DRY_RUN')
    p=next(p for p in pred['predictions'][0]['scenarios'][-1]['models'] if p['model']=='C_NEXT_OPEN')
    assert p['action']=='ABSTAIN' and p['conditional_publication_forecast']['before_open_action']=='CONTINUATION'
    before=w.resolve_publication_condition(p,archive['alerts']['alerts'][1])
    after=w.resolve_publication_condition(p,alert('later',0,'2026-10-20T18:00:00-04:00'))
    assert before['action']=='CONTINUATION' and after['action']=='DROPPED'


def test_predict_only_accepts_bounded_view_bundle_not_an_archive(archive,tmp_path):
    files={'view.json':encode(make_view(archive,'x',CUTOFF,1)),'archive.json':encode(archive)}
    h=write_bundle(tmp_path/'invalid',files)
    with pytest.raises(ValueError,match='only a bounded causal view'):
        w.prediction_files(files,h,NOW.isoformat(),'RETROSPECTIVE_DRY_RUN')


def test_fresh_scores_require_next_alert_and_complete_chain_attestations(tmp_path,archive):
    from datetime import timedelta
    a=tmp_path/'archive';write_bundle(a,{'archive.json':encode(archive)})
    v=tmp_path/'view';w.prepare(a,CUTOFF,v,1)
    p=tmp_path/'prediction';w.freeze(v,p,'FORWARD_REGISTERED',now=NOW)
    original=read_bundle(p)
    raw=tmp_path/'future.json';body={'origin':'synthetic','alerts':[alert('future',0,'2026-10-29T18:00:00-04:00',stops='AAPL stop moved to 93.00 from 95.00')]}
    for i,attested in enumerate((False,True)):
        if attested:body['sequence_attestation']={'next_complete_alert_after_registration':True,'complete_since_known_history':True}
        raw.write_bytes(encode(body));w.reveal(p,raw,tmp_path/f'r{i}',now=NOW+timedelta(days=1));w.evaluate(p,tmp_path/f'r{i}',tmp_path/f'e{i}')
        result=json.loads(read_bundle(tmp_path/f'e{i}')[0]['evaluation.json'])
        assert result['eligibility']==('ELIGIBLE' if attested else 'UNRESOLVED_ALERT_SEQUENCE')
        assert result['fresh_out_of_sample']==attested
    assert read_bundle(p)==original


def test_narrow_boundary_overlap_is_unresolved_not_a_fresh_score(archive):
    registered=datetime(2026,10,29,22,0,30,tzinfo=UTC)
    p=predict(make_view(archive,'x',CUTOFF,1),registered.isoformat(),'FORWARD_REGISTERED')
    a=alert('future',0,'2026-10-29T18:00:00-04:00')
    a.update(next_complete_alert_attested=True,complete_source_chain_attested=True)
    assert w.evaluate_data(p,[],a)['eligibility']=='UNRESOLVED_WINDOW_BOUNDARY'


def test_nonprotective_entry_is_not_repaired_by_a_later_source_stop(archive):
    next(r for r in archive['prices']['AAPL'] if r['session_date']=='2026-10-19')['open']='94.5'
    view=make_view(archive,'x','2026-10-20T21:01:00+00:00',2)
    trade=validate_view(view)[0]
    assert trade['current_stop']=='90.00'
    state=stop_state(trade,clocks(view)[-1],view,'A_HARD_STOP')
    assert state['hypothetical_state']=='REJECTED_NONPROTECTIVE_OPEN_REFERENCE'
    assert state['actual_execution_state']=='UNKNOWN'


def test_discriminating_test_selection_does_not_depend_on_actual_action(archive):
    p=predict(make_view(archive,'x',CUTOFF,1),NOW.isoformat(),'RETROSPECTIVE_DRY_RUN')
    a=archive['alerts']['alerts'][1]
    stop_events,_=parse_known({'schema_version':'grimes_alerts_v1','origin':'synthetic','alerts':[dict(a,source_sequence=0)]})
    d=alert('b',0,a['published_at'],dropped='AAPL dropped from long')
    drop_events,_=parse_known({'schema_version':'grimes_alerts_v1','origin':'synthetic','alerts':[d]})
    left=w.evaluate_data(p,stop_events,a);right=w.evaluate_data(p,drop_events,a)
    assert [s['predeclared_disjoint_prediction_pairs'] for s in left['source_observations'][0]['scenarios']]==[s['predeclared_disjoint_prediction_pairs'] for s in right['source_observations'][0]['scenarios']]
    assert left['source_observations'][0]['scenarios'][-1]['models'][0]['verdict']!=right['source_observations'][0]['scenarios'][-1]['models'][0]['verdict']


def test_stop_level_error_uses_frozen_forecast_atr_and_intervals_stay_protective(archive):
    p=predict(make_view(archive,'x',CUTOFF,1),NOW.isoformat(),'RETROSPECTIVE_DRY_RUN')
    a=archive['alerts']['alerts'][1]
    events,_=parse_known({'schema_version':'grimes_alerts_v1','origin':'synthetic','alerts':[dict(a,source_sequence=0)]})
    e=p['predictions'][0]['scenarios'][-1]['models'][-1]
    score=w.evaluate_data(p,events,a)['source_observations'][0]['scenarios'][-1]['models'][-1]
    assert score['stop_error_ATR']==pytest.approx(abs(90-e['stop_point'])/e['features']['atr14']['value'])
    assert 0<e['stop_interval'][0]<=e['stop_interval'][1]<e['features']['close']['value']


def test_reveal_cannot_be_rebound_to_another_prediction(tmp_path,archive):
    from datetime import timedelta
    a=tmp_path/'archive';write_bundle(a,{'archive.json':encode(archive)})
    v=tmp_path/'view';w.prepare(a,CUTOFF,v,1)
    p=tmp_path/'p';w.freeze(v,p,'RETROSPECTIVE_DRY_RUN',now=NOW)
    raw=tmp_path/'next.json';raw.write_bytes(encode(archive['alerts']['alerts'][1]));w.reveal(p,raw,tmp_path/'r',now=NOW)
    q=tmp_path/'q';w.freeze(v,q,'RETROSPECTIVE_DRY_RUN',now=NOW+timedelta(seconds=1))
    qf,qh=w.load_prediction(q)
    with pytest.raises(ValueError,match='another prediction'):w.load_reveal(tmp_path/'r',qf,qh)


def test_forecast_artifact_round_trip_is_deterministic_for_fixed_registration(archive):
    view=make_view(archive,'x',CUTOFF,1)
    first=predict(view,NOW.isoformat(),'RETROSPECTIVE_DRY_RUN')
    assert encode(first)==encode(predict(json.loads(encode(view)),NOW.isoformat(),'RETROSPECTIVE_DRY_RUN'))
    assert first['source_status_authoritative'] and not first['timing_scenarios_are_independent_observations']


def test_view_cannot_omit_already_available_source_history(archive):
    with pytest.raises(ValueError,match='omits already-available'):
        make_view(archive,'x','2026-10-20T21:01:00+00:00',1)
    archive['prices']['GME']=[{'session_date':'2026-10-19','close':'UNRELATED FUTURE EPISODE'}]
    archive['coverage']['GME']={'not':'an admitted identity'}
    view=make_view(archive,'x',CUTOFF,1)
    assert 'GME' not in view['prices'] and 'GME' not in view['coverage']


def test_next_alert_can_advance_history_without_rewriting_prior_prediction(tmp_path,archive):
    from datetime import timedelta
    archive['alerts']['alerts']=archive['alerts']['alerts'][:1]
    a=tmp_path/'a';write_bundle(a,{'archive.json':encode(archive)})
    v=tmp_path/'v';w.prepare(a,CUTOFF,v)
    p=tmp_path/'p';w.freeze(v,p,'FORWARD_REGISTERED',now=NOW);before=read_bundle(p)
    body={'origin':'synthetic','alerts':[alert('future',0,'2026-10-29T18:00:00-04:00',stops='AAPL stop moved to 93.00 from 95.00')]}
    raw=tmp_path/'new.json';raw.write_bytes(encode(body));r=tmp_path/'r';w.reveal(p,raw,r,now=NOW+timedelta(days=1))
    w.advance(a,p,r,tmp_path/'next-a')
    w.prepare(tmp_path/'next-a','2026-10-29T22:01:00+00:00',tmp_path/'next-v')
    view=json.loads(read_bundle(tmp_path/'next-v')[0]['view.json']);source=validate_view(view)[0]
    assert source['position_state']=='OPEN' and source['current_stop']=='93.00'
    assert view['market_observation_end']=='2026-10-26' # no fabricated fresh bars
    w.freeze(tmp_path/'next-v',tmp_path/'next-p','FORWARD_REGISTERED',now=NOW+timedelta(days=1))
    assert read_bundle(p)==before
    original=deepcopy(archive['prices']['AAPL'][0]);changed={**original,'close':'200'}
    update=tmp_path/'update.json';update.write_bytes(encode({'schema_version':'grimes_market_update_v1','source_reference':'synthetic','native_bundle_sha256':'synthetic','market_observation_end':'2026-10-26','prices':{'AAPL':[changed]}}))
    with pytest.raises(ValueError,match='cannot overwrite'):
        w.advance(a,p,r,tmp_path/'bad-a',update)


def test_historical_replay_rebuilds_prefixes_and_rejects_resealed_cutoff_metadata(tmp_path,archive):
    from shutil import copytree
    from equity_research.prospective.experiment import dry_run,replay_experiment
    a=tmp_path/'archive';write_bundle(a,{'archive.json':encode(archive)})
    seal=dry_run(a,tmp_path/'experiment')
    assert replay_experiment(tmp_path/'experiment',tmp_path/'replay')==seal
    original,_=read_bundle(tmp_path/'experiment/study')
    for index,kind in enumerate(('cutoff','inventory','path')):
        dest=tmp_path/f'tamper-{index}';dest.mkdir();copytree(tmp_path/'experiment/case-01',dest/'case-01')
        files=deepcopy(original);data=json.loads(files['walk-forward.json'])
        if kind=='cutoff':data['cases'][0]['cutoff']='2026-10-18T19:21:00+00:00'
        elif kind=='inventory':data['cases']=[]
        else:data['cases'][0]['case_id']='../escape'
        files['walk-forward.json']=encode(data);write_bundle(dest/'study',files)
        with pytest.raises(ValueError,match='cutoff/prefix|inventory mismatch|unsafe or nonsequential'):
            replay_experiment(dest,tmp_path/f'rejected-{index}')
    assert not (tmp_path/'escape').exists()


def test_real_sealed_forecast_stays_unresolved_and_public_reports_are_reproducible():
    import hashlib
    from equity_research.prospective.reports import walk_report,next_report
    root=Path(__file__).parents[1]
    pf,_=read_bundle(root/'docs/evidence/pr9c-next-alert-v1')
    wf,_=read_bundle(root/'docs/evidence/pr9c-walk-forward-v1')
    p=json.loads(pf['prediction.json']);r=json.loads(wf['walk-forward.json'])
    assert p['mode']=='FORWARD_REGISTERED' and p['outcome']=='UNRESOLVED_NO_LATER_ALERT_IMPORTED'
    assert 'evaluation.json' not in pf
    assert p['registered_at']==p['target']['strictly_after']=='2026-10-29T03:02:03.944237+00:00'
    assert p['target']['deadline']=='2026-11-04T23:59:59.999999-05:00'
    assert p['unobserved_completed_sessions_since_market_end']==['2026-10-27','2026-10-28']
    trades={t['symbol']:t for t in p['predictions']}
    assert len(trades)==14 and all(t['source_state']['position_state']=='OPEN' for t in trades.values())
    assert trades['CDE']['source_state']['current_stop']=='13.90' and trades['CDE']['source_state']['setup_availability']=='UNDERWAY'
    assert trades['EBAY']['source_state']['current_stop']=='117.50' and trades['EBAY']['source_state']['setup_availability']=='ENTERABLE'
    assert next(m for m in trades['EBAY']['scenarios'][-1]['models'] if m['model']=='A_HARD_STOP')['hypothetical_execution']['hypothetical_state']=='CLOSED_NO_REENTRY'
    assert r['fresh_out_of_sample_observations']==0 and len(r['cases'])==6
    assert sum(len(c['prediction']['predictions']) for c in r['cases'])==61
    assert len({t['symbol'] for c in r['cases'] for t in c['prediction']['predictions']}|set(trades))==26
    first={t['symbol']:t for t in r['cases'][0]['prediction']['predictions']}
    assert first['AAPL']['source_state']['position_state']=='OPEN' and first['AAPL']['source_state']['current_stop']=='339.00'
    last={t['symbol']:t for t in r['cases'][-1]['prediction']['predictions']}
    assert last['EBAY']['source_state']['current_stop']=='119.20' # later117.50 not leaked
    assert p['known_alerts'][5]['published_at'] is None
    assert next_report(p,json.loads(pf['local-prediction-hashes.json'])).encode()==(root/'docs/reports/GRIMES_NEXT_ALERT_PREDICTIONS.md').read_bytes()
    assert walk_report(r).encode()==(root/'docs/reports/GRIMES_WALK_FORWARD_EVALUATION.md').read_bytes()
    assert hashlib.sha256((root/'reports/grimes_trade_status.csv').read_bytes()).hexdigest()=='a32c812f95a51a56dc90fd8f49634b4976cd7f175fb1b326faf773ff22e4c527'
