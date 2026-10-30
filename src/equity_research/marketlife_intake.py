"""Append-only source intake and qualified native daily evidence for PR9D."""
from copy import deepcopy
from datetime import timedelta
from decimal import Decimal
import json
from pathlib import Path
import tempfile

from .comprehension.inputs import _check_hashes,PRICE_BASIS,VOLUME_BASIS
from .history.contracts import Security
from .history.normalize import read_acquisition
from .ingestion.calendar import schedule
from .ingestion.storage import digest,encode,read_bundle,write_bundle
from .marketlife_setups import source_inputs,timing_scenarios,opportunity_ledger
from .marketlife_workflow import alert_manifest
from .models import timestamp


def completed_window(asof,start='2025-01-02'):
    t=timestamp(asof)
    cal=schedule(start,(t.date()+timedelta(days=15)).isoformat())
    days=[s['session_date'] for s in cal['sessions'] if timestamp(s['closes_at'])+timedelta(minutes=60)<t]
    if not days:raise ValueError('no eligible completed session')
    return cal,days[-60:]


def source_state(archive,batches,asof):
    """Reuse the source parser per immutable batch: never widen earlier receipt bounds."""
    events,metadata,excluded=source_inputs(archive,None)
    original_count=len(events);original_alerts=len(metadata)
    seen={a['alert_id'] for a in metadata}
    def body_time(item,sha):
        return sha,timestamp(item['published_at']).isoformat() if item.get('published_at') else item.get('source_date',item.get('lower'))
    body_times={body_time(a,a['text_sha256']) for a in metadata}
    for batch in batches:
        receipt=timestamp(batch['captured_at'])
        if receipt>timestamp(asof):raise ValueError('source capture is after observation cutoff')
        for a in batch['alerts']:
            if not a.get('text') or not a.get('source_reference') or not a.get('alert_id'):
                raise ValueError('original complete body, source reference and alert ID required')
            if a.get('publication_precision') not in {'DATE','MINUTE','SECOND'}:
                raise ValueError('explicit operator publication precision required')
            if bool(a.get('published_at'))!=(a['publication_precision']!='DATE'):
                raise ValueError('publication precision disagrees with original timestamp')
            if a.get('published_at') and timestamp(a['published_at'])>receipt:
                raise ValueError('publication is after receipt')
            key=body_time(a,digest(a['text'].encode()))
            if a['alert_id'] in seen or key in body_times:
                raise ValueError('duplicate source alert identity or body')
            seen.add(a['alert_id']);body_times.add(key)
        e,m,_=source_inputs(archive,batch)
        additions=e[original_count:]
        for event in additions:event['source_order']=len(events);events.append(event)
        metadata.extend(m[original_alerts:])
    originals={a['alert_id']:a for a in archive['alerts']['alerts']}
    receipts={a['alert_id']:a.get('email_received_at') for a in archive['alerts']['alerts']}
    for batch in batches:
        originals.update({a['alert_id']:a for a in batch['alerts']})
        receipts.update({a['alert_id']:batch['captured_at'] for a in batch['alerts']})
    for item in metadata:
        raw=originals[item['alert_id']]
        item.update(source_reference=raw.get('source_reference'),capture_or_receipt_at=receipts[item['alert_id']],
            original_publication_display=raw.get('original_publication_display',raw.get('source_date','UNKNOWN')))
    if any(timestamp(a['upper'])>timestamp(asof) for a in metadata):raise ValueError('future source availability')
    cal,required=completed_window(asof,archive['calendar']['start'])
    clocks=timing_scenarios(metadata,cal)
    ledgers=[opportunity_ledger(events,metadata,clock) for clock in clocks]
    by_event={e['event_id']:e for e in events}
    for setup in ledgers[-1]['setups']:
        for action in setup['events']:
            event=by_event[action['source_event_id']]
            if event['type']=='DROPPED' and event.get('reported_underway',False)!=(action['entry_state_before']=='UNDERWAY'):
                raise ValueError('source DROP previous eligibility mismatch')
    return {'events':events,'metadata':metadata,'excluded':excluded,'clocks':clocks,'ledgers':ledgers,
        'source_alert_manifest_sha256':alert_manifest(metadata),'calendar':cal,'required_sessions':required,
        'receipt_timestamps':[b['captured_at'] for b in batches]}


def append_source(parent_archive,prior_batches,incoming,asof):
    """Validate a new operator batch before sealing it; original bodies stay exact."""
    if incoming.get('schema_version')!='marketlife_operator_alerts_v1' or not incoming.get('alerts'):
        raise ValueError('versioned nonempty operator alert batch required')
    batches=[*prior_batches,deepcopy(incoming)]
    source_state(parent_archive,batches,asof)
    return batches


def source_manifest(state):
    return {'schema_version':'marketlife_source_history_v1','alert_manifest_sha256':state['source_alert_manifest_sha256'],
        'alerts':state['metadata'],'receipt_timestamps':state['receipt_timestamps'],
        'source_actions':len(state['events']),'captured_setup_episodes':len(state['ledgers'][-1]['setups']),
        'completeness_is_not_proved_by_hashes':True,'actual_executions':'UNKNOWN'}


def required_symbols(state):
    return sorted({s['symbol'] for s in state['ledgers'][-1]['setups'] if s['setup_status']=='ACTIVE'}|{'SPY'})


def validate_contract(symbol,contract,previous=None):
    if (contract.get('symbol')!=symbol or contract.get('secType')!='STK' or contract.get('currency')!='USD'
            or contract.get('exchange')!='SMART' or not contract.get('primaryExchange')
            or type(contract.get('conId')) is not int or contract['conId']<=0):
        raise ValueError('incompatible qualified contract identity')
    if previous and any(contract.get(k)!=previous.get(k) for k in
            ('conId','symbol','secType','currency','exchange','primaryExchange','localSymbol','tradingClass')):
        raise ValueError('qualified identity changed; no ticker or historical-series splice')


def coverage_audit(archive,batches,asof):
    state=source_state(archive,batches,asof);required=state['required_sessions'];rows=[]
    from .reconstruction.admission import Evidence
    from .marketlife_research import snapshot
    try:evidence=Evidence(archive['prices'],archive['coverage'],state['calendar'],asof)
    except (ValueError,KeyError,TypeError):evidence=None
    sessions={s['session_date']:s for s in state['calendar']['sessions']}
    for symbol in required_symbols(state):
        info=archive['coverage'].get(symbol,{});prices=archive['prices'].get(symbol,[])
        dates=[r['session_date'] for r in prices];contract=info.get('contract')
        identity='MISSING'
        if contract:
            try:validate_contract(symbol,contract);identity='QUALIFIED_RECORDED'
            except ValueError:identity='INCOMPATIBLE'
        last=max((d for d in dates if d in sessions and d<=required[-1]),default=None)
        diagnostic={}
        if evidence and last:
            cutoff=min(timestamp(asof),timestamp(sessions[last]['closes_at'])+timedelta(minutes=61)).isoformat()
            s=snapshot(evidence,symbol,cutoff,'0','LONG')
            diagnostic={'session':s['feature_session'],'atr14':s.get('atr14'),'close':s.get('close_reference'),
                'stale':last!=required[-1],'used_for_registration_in_place_of_current':False}
        rows.append({'symbol':symbol,'contract':contract,'identity_status':identity,
            'observed_sessions':len(dates),'earliest':min(dates) if dates else None,'latest':max(dates) if dates else None,
            'required_start':required[0],'required_end':required[-1],'required_sessions':len(required),
            'missing_sessions':[d for d in required if d not in dates],
            'duplicate_sessions':sorted({d for d in dates if dates.count(d)>1}),
            'nonchronological':dates!=sorted(dates),'price_basis':info.get('price_basis'),
            'last_observed_feature_diagnostic':diagnostic,
            'volume_basis':info.get('volume_basis'),'corporate_action_completeness':info.get('corporate_action_completeness','UNKNOWN'),
            'identity_uncertainty':'Qualified contract is observed identity, not complete historical ticker/listing proof',
            'adjustment_uncertainty':'IBKR TRADES split-adjusted, not raw execution prices; corporate-action completeness UNKNOWN'})
    return {'schema_version':'marketlife_current_coverage_v1','asof':asof,'required_latest_completed_session':required[-1],
        'feature_warmup_sessions':60,'instruments':rows,'universe_basis':'LATEST_SUPPLIED_RECONCILED_SOURCE_NOT_ASSUMED_CURRENT_FEED',
        'source_manifest':source_manifest(state)}


def checked_acquisition(files,hashes,security):
    """Replay existing normalization from the exact sealed native return, offline."""
    _check_hashes(files,hashes)
    with tempfile.TemporaryDirectory(prefix='marketlife-native-') as temporary:
        path=Path(temporary)/'capture';write_bundle(path,files)
        result=read_acquisition(path,security)
    return result


def merge_evidence(parent,batches,proofs,asof):
    """Append only. Conflicting overlap is retained as a blocker, never replaced."""
    archive=deepcopy(parent);state=source_state(parent,batches,asof);required=set(required_symbols(state))
    completed=set(s['session_date'] for s in state['calendar']['sessions']
        if timestamp(s['closes_at'])+timedelta(minutes=60)<timestamp(asof))
    findings=[];identities=[]
    for proof in proofs:
        security=Security(**proof['security']);symbol=security.symbol
        if symbol not in required:raise ValueError('market intake outside the current source universe and SPY')
        native={k:v.encode() for k,v in proof['files'].items()}
        result=checked_acquisition(native,proof['hashes'],security)
        req,acq=result['request'],result['acquisition'];contract=acq['qualified_contract']
        if req['provider']!='ibkr':raise ValueError('current intake requires IBKR native TRADES')
        if parent['alerts']['origin']!='synthetic' and req.get('origin')!='ibkr_client':
            raise ValueError('synthetic market updates cannot enter an operational archive')
        params=req['parameters']
        if not (params['whatToShow']=='TRADES' and params['useRTH'] is True and params['barSizeSetting']=='1 day'
                and params['keepUpToDate'] is False):raise ValueError('incompatible native data request')
        if acq['status']!='SUCCESS' or any(i['status']=='FAIL' for i in result['issues']):
            findings.append({'symbol':symbol,'code':'NATIVE_REQUEST_OR_NORMALIZATION_FAILED','status':acq['status']});continue
        validate_contract(symbol,contract,archive['coverage'].get(symbol,{}).get('contract'))
        if security.con_id!=contract['conId'] or security.ibkr_symbol!=symbol or security.primary_exchange!=contract['primaryExchange']:
            raise ValueError('acquisition mapping not pinned to the qualified identity')
        if archive['coverage'].get(symbol,{}).get('security',{}).get('security_id',security.security_id)!=security.security_id:
            raise ValueError('stable security identity changed')
        if (result['basis']['price_basis']!=PRICE_BASIS or result['basis']['volume_basis']!=VOLUME_BASIS):
            raise ValueError('incompatible acquisition price or volume basis')
        incoming=result['rows'];dates=[r['session_date'] for r in incoming]
        if len(set(dates))!=len(dates) or dates!=sorted(dates) or any(d not in completed for d in dates):
            raise ValueError('duplicate, nonchronological, future or off-calendar market observations')
        if timestamp(acq['completed_at'])>timestamp(asof):raise ValueError('native capture after archive cutoff')
        sessions={s['session_date']:s for s in state['calendar']['sessions']}
        if any(timestamp(sessions[d]['closes_at'])+timedelta(minutes=60)>=timestamp(acq['started_at']) for d in dates):
            raise ValueError('native request started before selected daily observations were eligible')
        previous={r['session_date']:r for r in archive['prices'].get(symbol,[])}
        for row in incoming:
            old=previous.get(row['session_date'])
            if old and any(Decimal(old[k])!=Decimal(row[k]) for k in ('open','high','low','close','volume')):
                findings.append({'symbol':symbol,'code':'CONFLICTING_RETAINED_NATIVE_VINTAGES','session':row['session_date'],
                    'differing_fields':[k for k in ('open','high','low','close','volume') if Decimal(old[k])!=Decimal(row[k])]})
            elif old is None:previous[row['session_date']]=row
        archive['prices'][symbol]=[r for _,r in sorted(previous.items())]
        old_info=archive['coverage'].get(symbol,{})
        archive['coverage'][symbol]={**old_info,'security':security.record(),'contract':contract,
            'price_basis':PRICE_BASIS,'volume_basis':VOLUME_BASIS,'corporate_action_completeness':'UNKNOWN',
            'origin':req['origin'],'source_bundle_sha256':proof['hashes']['bundle_sha256']}
        identities.append(contract['conId'])
    if len(identities)!=len(set(identities)):raise ValueError('ambiguous duplicate intake contract identity')
    archive['calendar']=state['calendar']
    archive['market_observation_end']=max((r['session_date'] for rows in archive['prices'].values() for r in rows
        if r['session_date'] in completed),default=parent['market_observation_end'])
    archive['source_cutoff']=state['metadata'][-1]['upper']
    return archive,findings


def proof_record(path):
    files,hashes=read_bundle(Path(path));req=json.loads(files['request.json'])
    return {'security':req['security'],'files':{k:v.decode() for k,v in files.items()},'hashes':hashes}
