"""Additive MarketLife studies and fail-closed operational registration."""
from datetime import UTC,datetime,timedelta
import json
from pathlib import Path
from datetime import time
from zoneinfo import ZoneInfo

from .ingestion.calendar import schedule
from .ingestion.storage import digest,encode,read_bundle,write_bundle
from .models import timestamp
from .marketlife_setups import source_inputs,timing_scenarios,opportunity_ledger
from .marketlife_research import analyze,snapshot
from .reconstruction.admission import Evidence,value

DEPRECATED_PREDICTION='36b732cdb82e74a9c90f8add9d6e66015f31bcf9da156cb6213a858bf7676135'


def identity():
    root=Path(__file__).parent
    modules=('marketlife_setups.py','marketlife_research.py','marketlife_workflow.py',
        'reconstruction/admission.py','reconstruction/timing.py','prospective/inputs.py',
        'prospective/models.py','comprehension/features.py','lifecycle/source.py',
        'comprehension/inputs.py','market_context/model.py','events/model.py',
        'lifecycle/model.py','models.py','ingestion/calendar.py','ingestion/storage.py')
    return {n:digest((root/n).read_bytes()) for n in modules}


def alert_manifest(metadata):
    return digest(encode([{k:a[k] for k in ('alert_id','text_sha256')} for a in metadata]))


def current_calendar(archive,asof):
    return schedule(archive['calendar']['start'],(timestamp(asof).date()+timedelta(days=15)).isoformat())


def audit(archive,operator,assurance,asof):
    events,metadata,_=source_inputs(archive,operator)
    t=timestamp(asof);cal=current_calendar(archive,asof)
    completed=[s['session_date'] for s in cal['sessions'] if timestamp(s['closes_at'])+timedelta(minutes=60)<t]
    if not completed:raise ValueError('no completed session at registration')
    latest=completed[-1];required=completed[-60:];problems=[]
    manifest=alert_manifest(metadata)
    if (not assurance or assurance.get('complete') is not True or assurance.get('complete_through')!='REGISTRATION'
            or assurance.get('alert_manifest_sha256')!=manifest or not assurance.get('source_reference')):
        problems.append({'code':'SOURCE_HISTORY_NOT_VERIFIED_THROUGH_REGISTRATION','required_alert_manifest_sha256':manifest,
                         'confirmation_is_operator_attestation_not_automatic_feed_verification':True})
    if any(timestamp(a['upper'])>t for a in metadata):problems.append({'code':'SOURCE_AVAILABILITY_AFTER_REGISTRATION'})
    clock=timing_scenarios(metadata,cal)[-1]
    ledger=opportunity_ledger(events,metadata,clock)
    active=[s for s in ledger['setups'] if s['setup_status']=='ACTIVE']
    identities=[]
    required_symbols=[s['symbol'] for s in active]
    if 'SPY' not in required_symbols:required_symbols.append('SPY')
    for symbol in required_symbols:
        info=archive['coverage'].get(symbol)
        if not info or type(info.get('contract',{}).get('conId')) is not int or info['contract']['conId']<=0:
            problems.append({'code':'UNVERIFIED_MARKET_CONTRACT_IDENTITY','symbol':symbol});continue
        identities.append(info['contract']['conId'])
        dates=[r['session_date'] for r in archive['prices'].get(symbol,[])]
        if len(dates)!=len(set(dates)) or dates!=sorted(dates):problems.append({'code':'DUPLICATE_OR_NONCHRONOLOGICAL_MARKET_ROWS','symbol':symbol})
        missing=[d for d in required if d not in dates]
        if missing:problems.append({'code':'MISSING_REQUIRED_COMPLETED_SESSIONS','symbol':symbol,'sessions':missing})
    if len(identities)!=len(set(identities)):problems.append({'code':'AMBIGUOUS_DUPLICATE_CONTRACT_IDENTITIES'})
    if archive['market_observation_end']!=latest:problems.append({'code':'MARKET_CUTOFF_NOT_LATEST_COMPLETED_SESSION','declared':archive['market_observation_end'],'required':latest})
    if len(required)!=60:problems.append({'code':'INSUFFICIENT_DECLARED_CALENDAR_WARMUP'})
    for rows in archive['prices'].values():
        for row in rows:
            if row['session_date']>latest:
                problems.append({'code':'FUTURE_OR_INCOMPLETE_MARKET_OBSERVATION','session':row['session_date']});break
    try:
        evidence=Evidence(archive['prices'],archive['coverage'],cal,asof)
        for setup in active:
            snap=snapshot(evidence,setup['symbol'],asof,setup['published_stop'],setup['direction'])
            if snap['status']!='AVAILABLE' or snap['feature_session']!=latest or not snap['features'].get('sma50',{}).get('value'):
                problems.append({'code':'CURRENT_ATR_OR_TECHNICAL_FEATURES_UNAVAILABLE','symbol':setup['symbol']})
            elif (snap.get('relative_SPY20') or {}).get('value') is None:
                problems.append({'code':'CURRENT_MARKET_RELATIVE_FEATURES_UNAVAILABLE','symbol':setup['symbol']})
    except (ValueError,KeyError,TypeError,ArithmeticError):
        problems.append({'code':'INVALID_MARKET_IDENTITY_BASIS_OR_OHLCV'})
    return {'schema_version':'marketlife_registration_gate_v1','asof':asof,'passed':not problems,
        'status':'READY' if not problems else 'PENDING_CURRENT_SOURCE_AND_MARKET_EVIDENCE',
        'required_latest_completed_session':latest,'required_consecutive_feature_sessions':60,
        'active_setups':len(active),'enterable_setups':sum(s['entry_state']=='ENTERABLE' for s in active),
        'source_alert_manifest_sha256':manifest,'problems':problems,'independent_subscriber_feed_access':False,
        'superseded_registration':{'sha256':DEPRECATED_PREDICTION,'operational_baseline':False,'original_artifact_changed':False,
            'reason':'STALE_MARKET_HISTORY_AND_SUPERSEDED_SETUP_EXECUTION_SEMANTICS'}}


def registration_payload(archive,operator,assurance,asof):
    gate=audit(archive,operator,assurance,asof)
    if not gate['passed']:raise ValueError('current-data registration blocked: source or market completeness gate failed')
    events,metadata,_=source_inputs(archive,operator)
    cal=current_calendar(archive,asof)
    evidence=Evidence(archive['prices'],archive['coverage'],cal,asof)
    forecasts=[]
    for clock in timing_scenarios(metadata,cal):
        ledger=opportunity_ledger(events,metadata,clock)
        for setup in ledger['setups']:
            if setup['setup_status']!='ACTIVE':continue
            snap=snapshot(evidence,setup['symbol'],asof,setup['published_stop'],setup['direction'])
            anchor=snapshot(evidence,setup['symbol'],setup['events'][0]['assumed_at'],setup['initial_published_stop'],setup['direction'])
            sign=1 if setup['direction']=='LONG' else -1
            progress=sign*(snap['close_reference']-anchor['close_reference'])/anchor['atr14'] if anchor.get('atr14') and anchor.get('close_reference') is not None else None
            features=snap['features'];directional_level=features['prior20_high' if sign==1 else 'prior20_low']['value']
            breakout=directional_level is not None and sign*(snap['close_reference']-directional_level)>0
            predicted='UNDERWAY' if setup['entry_state']=='UNDERWAY' or progress is not None and progress>=1 and breakout else 'ENTERABLE'
            forecasts.append({'setup_id':setup['setup_id'],'symbol':setup['symbol'],'timing_scenario':clock['name'],
                'source_setup_status':setup['setup_status'],'source_entry_state':setup['entry_state'],
                'persistence_eligibility_baseline':setup['entry_state'],
                'primary_targets':{'entry_eligibility':predicted,'setup_removal':'ABSTAIN_NO_IDENTIFIED_REMOVAL_RULE',
                    'new_entry_opportunity':'NONE_IN_PERSISTENCE_BASELINE'},
                'opportunity_conditionals':{'ENTERABLE_STOP_CHANGED':'NEW_VERSION_USING_NEW_STOP',
                    'CO_PUBLISHED_UNDERWAY':'NO_NONEMPTY_ENTRY_WINDOW','UNDERWAY_STOP_CHANGED':'MONITOR_ONLY',
                    'EXPLICIT_RETURN_TO_ENTERABLE':'NEW_ELIGIBLE_VERSION','DROPPED':'END_SETUP_ELIGIBILITY_NOT_EXECUTION'},
                'published_stop':setup['published_stop'],'numeric_stop_forecast':'ABSTAIN_SECONDARY_DIAGNOSTIC_NOT_OPTIMIZED',
                'progress_reference_ATR':progress,'price_features':snap,'observed_execution':'UNKNOWN',
                'execution_stopout_used_to_predict_setup_drop':False,'confidence':'LOW_EXPLORATORY_NOT_CALIBRATED'})
    future=[s for s in cal['sessions'] if timestamp(s['opens_at'])>timestamp(asof)][:5]
    if len(future)!=5:raise ValueError('five-session future observation window required')
    final_day=datetime.fromisoformat(future[-1]['session_date']).date()
    deadline=datetime.combine(final_day+timedelta(days=1),time(),ZoneInfo('America/New_York'))-timedelta(microseconds=1)
    return {'schema_version':'marketlife_setup_forecast_v1','registered_at':asof,'gate':gate,'forecasts':forecasts,
        'expected_observation_window':{'strictly_after':asof,'through':deadline.isoformat(),'subsequent_session_dates':5},
        'evidence_origin':'SYNTHETIC_TEST_ONLY' if archive['alerts']['origin']=='synthetic' else 'USER_AUTHORIZED_RESEARCH',
        'prediction_target':'SOURCE_SETUP_SELECTION_AND_FRESH_ENTRY_ELIGIBILITY','outcome':'UNRESOLVED_NO_LATER_SOURCE_ASSESSMENT',
        'rules':'Persistence plus predeclared exploratory one-reference-ATR directional breakout extension flag; no threshold fitting and no execution-closure-to-DROP bridge'}


def register(archive_path,operator_path,assurance_path,output,*,now=None):
    a,ah=read_bundle(Path(archive_path));o,oh=read_bundle(Path(operator_path))
    archive=json.loads(a['archive.json']);operator=json.loads(o['operator-alerts.json'])
    if archive['alerts']['origin']=='synthetic':raise ValueError('synthetic fixtures cannot become operational registrations')
    assurance=json.loads(Path(assurance_path).read_bytes())
    asof=(now or datetime.now(UTC)).isoformat()
    return write_bundle(Path(output),registration_files(a,ah,o,oh,assurance,asof))


def registration_files(a,ah,o,oh,assurance,asof):
    from .comprehension.inputs import _check_hashes
    _check_hashes(a,ah);_check_hashes(o,oh)
    result=registration_payload(json.loads(a['archive.json']),json.loads(o['operator-alerts.json']),assurance,asof)
    return {'prediction.json':encode(result),'archive.json':a['archive.json'],'archive-hashes.json':encode(ah),
        'operator-alerts.json':o['operator-alerts.json'],'guidance.json':o['guidance.json'],'operator-hashes.json':encode(oh),
        'assurance.json':encode(assurance),'manifest.json':encode({'schema_version':'marketlife_setup_registration_v1',
            'archive_sha256':ah['bundle_sha256'],'operator_sha256':oh['bundle_sha256'],'implementation':identity()})}


def load_registration(path):
    files,hashes=read_bundle(Path(path))
    if json.loads(files.get('prediction.json',b'{}')).get('schema_version')!='marketlife_setup_forecast_v1':
        raise ValueError('legacy prediction schema is non-operational under amended setup semantics')
    result=json.loads(files['prediction.json'])
    expected=registration_files({'archive.json':files['archive.json']},json.loads(files['archive-hashes.json']),
        {'operator-alerts.json':files['operator-alerts.json'],'guidance.json':files['guidance.json']},
        json.loads(files['operator-hashes.json']),json.loads(files['assurance.json']),result['registered_at'])
    if files!=expected:raise ValueError('setup registration semantic output mismatch')
    return files,hashes


def study_files(archive_files,archive_hashes,operator_files,operator_hashes,asof,assurance):
    from .comprehension.inputs import _check_hashes
    _check_hashes(archive_files,archive_hashes);_check_hashes(operator_files,operator_hashes)
    archive=json.loads(archive_files['archive.json']);operator=json.loads(operator_files['operator-alerts.json'])
    result=analyze(archive,operator,json.loads(operator_files['guidance.json']))
    gate=audit(archive,operator,assurance,asof)
    return {'research.json':encode(result),'registration-audit.json':encode(gate),'source-assurance.json':encode(assurance),
        'manifest.json':encode({'schema_version':'marketlife_opportunity_study_v1','implementation':identity(),
            'archive_sha256':archive_hashes['bundle_sha256'],'operator_sha256':operator_hashes['bundle_sha256'],'asof':asof}),
        'input-archive.json':archive_files['archive.json'],'input-archive-hashes.json':encode(archive_hashes),
        'input-operator-alerts.json':operator_files['operator-alerts.json'],'input-guidance.json':operator_files['guidance.json'],
        'input-operator-hashes.json':encode(operator_hashes)}


def freeze_study(archive,operator,output,asof,assurance=None):
    a,ah=read_bundle(Path(archive));o,oh=read_bundle(Path(operator))
    return write_bundle(Path(output),study_files(a,ah,o,oh,asof,assurance))


def load_study(path):
    files,hashes=read_bundle(Path(path));m=json.loads(files['manifest.json'])
    expected=study_files({'archive.json':files['input-archive.json']},json.loads(files['input-archive-hashes.json']),
        {'operator-alerts.json':files['input-operator-alerts.json'],'guidance.json':files['input-guidance.json']},
        json.loads(files['input-operator-hashes.json']),m['asof'],json.loads(files['source-assurance.json']))
    if files!=expected:raise ValueError('MarketLife study semantic output mismatch')
    return files,hashes
