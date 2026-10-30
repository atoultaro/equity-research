"""Current evidence gate around the unchanged PR9C forecast implementation."""
from copy import deepcopy
from datetime import UTC,datetime
import json
from pathlib import Path

from .comprehension.inputs import _check_hashes
from .ingestion.storage import digest,encode,read_bundle,write_bundle
from .marketlife_intake import (source_state,source_manifest,required_symbols,coverage_audit,
    merge_evidence,validate_contract)
from . import marketlife_workflow as original
from .marketlife_research import snapshot
from .reconstruction.admission import Evidence,value
from .models import timestamp


def implementation():
    root=Path(__file__).parent
    names=('marketlife_intake.py','marketlife_readiness.py','marketlife_acquire.py',
        'history/normalize.py','history/contracts.py','providers/ibkr.py')
    return {**original.identity(),**{n:digest((root/n).read_bytes()) for n in names}}


def batches_from_proofs(proofs):
    batches=[]
    for proof in proofs:
        files={k:v.encode() for k,v in proof['files'].items()};_check_hashes(files,proof['hashes'])
        if set(files)!={'operator-alerts.json','guidance.json'}:raise ValueError('complete operator source bundle required')
        batches.append(json.loads(files['operator-alerts.json']))
    return batches


def conditional_view(archive,batches,state,clock):
    """Internal model clock projection only; original publication facts stay sealed.

    The PR9C gate/predictor accept a single receipt bound. Independently retained
    batches need different bounds. Project each selected conditional clock to the
    old numerical interface, never to the original source record or manifest.
    This reuses the exact unchanged model code, including its abstentions.
    """
    view=deepcopy(archive);operator={'captured_at':max((b['captured_at'] for b in batches),key=timestamp),'alerts':[]}
    alerts=[*view['alerts']['alerts']]
    for batch in batches:operator['alerts'].extend(deepcopy(batch['alerts']))
    for alert in [*alerts,*operator['alerts']]:
        alert['published_at']=clock['actions'][alert['alert_id']]
        alert['publication_precision']='SECOND'
        alert['internal_conditional_information_time_not_original_publication']=True
    view['alerts']['alerts']=alerts
    return view,operator


def readiness(archive,batches,assurance,asof,findings=()):
    state=source_state(archive,batches,asof)
    view,operator=conditional_view(archive,batches,state,state['clocks'][-1])
    # The ordered ID/body manifest is unchanged by this internal clock adapter.
    gate=original.audit(view,operator,assurance,asof)
    assert gate['source_alert_manifest_sha256']==state['source_alert_manifest_sha256']
    problems=list(gate['problems']);features={};ids=[]
    calendar_dates={s['session_date'] for s in state['calendar']['sessions']}
    try:
        if (not assurance or not assurance.get('operator_statement')
                or timestamp(assurance['asserted_at'])>timestamp(asof)):
            raise ValueError('auditable operator assertion required')
    except (KeyError,TypeError,ValueError):
        problems.append({'code':'MISSING_OR_FUTURE_DATED_SOURCE_COMPLETENESS_ASSERTION'})
    if findings:problems.extend(findings)
    for symbol in required_symbols(state):
        info=archive['coverage'].get(symbol,{})
        if archive['alerts']['origin']!='synthetic' and info.get('origin')!='ibkr_client':
            problems.append({'code':'NON_NATIVE_MARKET_EVIDENCE_IN_OPERATIONAL_ARCHIVE','symbol':symbol})
        try:
            validate_contract(symbol,info.get('contract') or {})
            ids.append(info['contract']['conId'])
            security=info['security']
            if (security['symbol']!=symbol or security['ibkr_symbol']!=symbol or security['currency']!='USD'
                    or security['primary_exchange']!=info['contract']['primaryExchange']
                    or security.get('con_id') not in {None,info['contract']['conId']}):
                raise ValueError('security mapping and qualified contract disagree')
        except (ValueError,KeyError):problems.append({'code':'INVALID_QUALIFIED_IDENTITY_OR_MAPPING','symbol':symbol})
        if any(r['session_date'] not in calendar_dates for r in archive['prices'].get(symbol,[])):
            problems.append({'code':'OFF_CALENDAR_PRICE_HISTORY','symbol':symbol})
    if len(ids)!=len(set(ids)):problems.append({'code':'DUPLICATE_REQUIRED_CONTRACT_IDENTITIES'})
    try:
        evidence=Evidence(archive['prices'],archive['coverage'],state['calendar'],asof)
        active={s['symbol']:s for s in state['ledgers'][-1]['setups'] if s['setup_status']=='ACTIVE'}
        for symbol in required_symbols(state):
            setup=active.get(symbol,{'direction':'LONG','published_stop':'0'})
            snap=snapshot(evidence,symbol,asof,setup['published_stop'],setup['direction']);features[symbol]=snap
            if symbol not in active:
                snap.update(feature_role='BENCHMARK_NO_SOURCE_SETUP',published_stop=None,
                    entry_to_stop_distance=None,entry_to_stop_ATR=None)
            required=('close','atr14','sma20','sma50','prior20_high','prior20_low',
                'realized_volatility20','range_contraction10_previous20')
            if (snap['status']!='AVAILABLE' or snap['feature_session']!=state['required_sessions'][-1]
                    or any(value(snap['features'],name) is None for name in required)
                    or snap['sma10']['value'] is None):
                problems.append({'code':'CURRENT_REQUIRED_TECHNICAL_FEATURES_UNAVAILABLE','symbol':symbol})
    except (ValueError,KeyError,TypeError,ArithmeticError):
        problems.append({'code':'INVALID_CURRENT_PRICE_FEATURE_EVIDENCE'})
    return {**gate,'schema_version':'marketlife_current_readiness_v1','passed':not problems,
        'status':'PASS' if not problems else 'FAIL','problems':problems,'features':features,
        'original_PR9C_gate_executed':True,'original_PR9C_gate_passed':gate['passed'],
        'source_manifest':source_manifest(state),'model_implementation_changed':False,
        'conditional_information_time_projection_is_not_source_publication':True}


def archive_files(parent_files,parent_hashes,source_proofs,market_proofs,asof,assurance,qualification):
    _check_hashes(parent_files,parent_hashes)
    if set(parent_files)!={'archive.json'}:raise ValueError('declared PR9C parent archive required')
    parent=json.loads(parent_files['archive.json']);batches=batches_from_proofs(source_proofs)
    archive,findings=merge_evidence(parent,batches,market_proofs,asof)
    gate=readiness(archive,batches,assurance,asof,findings)
    state=source_state(archive,batches,asof)
    return {'archive.json':encode(archive),'parent-archive.json':parent_files['archive.json'],
        'parent-hashes.json':encode(parent_hashes),'source-proofs.json':encode(source_proofs),
        'market-proofs.json':encode(market_proofs),'source-assurance.json':encode(assurance),
        'qualification-attempts.json':encode(qualification),'source-manifest.json':encode(source_manifest(state)),
        'source-ledgers.json':encode(state['ledgers']),'market-coverage.json':encode(coverage_audit(archive,batches,asof)),
        'readiness.json':encode(gate),'findings.json':encode(findings),
        'manifest.json':encode({'schema_version':'marketlife_current_archive_v1','asof':asof,
            'parent_sha256':parent_hashes['bundle_sha256'],'implementation':implementation(),
            'canonical_rows_policy':'APPEND_ONLY_NO_REPLACEMENT; conflicting revisions block registration',
            'source_receipts_preserved_by_batch':True,'synthetic_only':parent['alerts']['origin']=='synthetic'})}


def load_archive(path):
    files,hashes=read_bundle(Path(path));validate_archive_files(files)
    return files,hashes


def validate_archive_files(files):
    m=json.loads(files['manifest.json'])
    if m['schema_version']!='marketlife_current_archive_v1':raise ValueError('current archive schema required')
    expected=archive_files({'archive.json':files['parent-archive.json']},json.loads(files['parent-hashes.json']),
        json.loads(files['source-proofs.json']),json.loads(files['market-proofs.json']),m['asof'],
        json.loads(files['source-assurance.json']),json.loads(files['qualification-attempts.json']))
    if expected!=files:raise ValueError('current archive semantic replay mismatch')


def prediction_files(current,current_hashes,asof):
    _check_hashes(current,current_hashes)
    validate_archive_files(current)
    archive=json.loads(current['archive.json']);batches=batches_from_proofs(json.loads(current['source-proofs.json']))
    assurance=json.loads(current['source-assurance.json']);findings=json.loads(current['findings.json'])
    gate=readiness(archive,batches,assurance,asof,findings)
    if not gate['passed']:raise ValueError('current source/market readiness FAIL; no forecast written')
    state=source_state(archive,batches,asof);forecasts=[];template=None
    for clock in state['clocks']:
        view,operator=conditional_view(archive,batches,state,clock)
        payload=original.registration_payload(view,operator,assurance,asof)
        if template is None:template=payload
        # In a fully projected clock all three legacy schedules coincide. Keep
        # one output per original conditional schedule, without tripling evidence.
        for row in payload['forecasts']:
            if row['timing_scenario']=='LATE':forecasts.append({**row,'timing_scenario':clock['name']})
    prediction={**template,'schema_version':'marketlife_current_forecast_v1','gate':gate,'forecasts':forecasts,
        'source_manifest':source_manifest(state),'original_source_publication_facts_unchanged':True,
        'conditional_clocks':state['clocks'],'current_archive_sha256':current_hashes['bundle_sha256'],
        'original_PR9C_forecast_rules_unchanged':True}
    return {**{'input-'+k:v for k,v in current.items()},'input-hashes.json':encode(current_hashes),
        'prediction.json':encode(prediction),'manifest.json':encode({'schema_version':'marketlife_current_registration_v1',
            'registered_at':asof,'current_archive_sha256':current_hashes['bundle_sha256'],'implementation':implementation()})}


def register_current(archive_path,output):
    current,hashes=load_archive(archive_path)
    if json.loads(current['manifest.json'])['synthetic_only']:
        raise ValueError('synthetic fixtures cannot be operationally registered')
    # No caller-supplied date/clock. Test pure prediction_files for fixed fixtures.
    asof=datetime.now(UTC).isoformat()
    return write_bundle(Path(output),prediction_files(current,hashes,asof))


def load_prediction(path):
    files,hashes=read_bundle(Path(path));m=json.loads(files['manifest.json'])
    if m['schema_version']!='marketlife_current_registration_v1':raise ValueError('current registration schema required')
    current={k[6:]:v for k,v in files.items() if k.startswith('input-') and k!='input-hashes.json'}
    expected=prediction_files(current,json.loads(files['input-hashes.json']),m['registered_at'])
    if expected!=files:raise ValueError('current prediction semantic replay mismatch')
    return files,hashes
