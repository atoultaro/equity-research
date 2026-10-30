"""Explicit local paper-TWS market intake using the existing IBKR daily adapter."""
import asyncio
from dataclasses import replace
from datetime import UTC,datetime
import json
from pathlib import Path
from types import SimpleNamespace

from .history.contracts import Security
from .ingestion.storage import encode,read_bundle,write_bundle
from .marketlife_intake import coverage_audit,completed_window,validate_contract
from .providers.ibkr import IBKRDailyProvider,make_backend,Pacer,contract_record,error_code,classify


async def qualify(selections,host,port,client_id,*,backend_factory=make_backend,pacer=None):
    """Resolve only selected securities; no account, order or position operations."""
    backend=None;records=[];pacer=pacer or Pacer()
    try:
        backend=backend_factory();await backend.connect(host,port,client_id)
        for selection in selections:
            symbol=selection['symbol'];old=selection.get('contract')
            query=SimpleNamespace(symbol=symbol,ibkr_symbol=symbol,currency='USD',
                primary_exchange=old['primaryExchange'] if old else '',con_id=old['conId'] if old else None)
            await pacer.wait('qualify:'+symbol)
            mark=len(backend.errors)
            native=[]
            try:
                matches=await asyncio.wait_for(backend.qualify(query),20)
                native=[contract_record(c) for c in matches]
                if any(e['category']!='INFORMATION' for e in backend.errors[mark:]):raise ValueError('qualification provider error')
                if len(native)!=1:raise ValueError('ambiguous or empty qualification')
                validate_contract(symbol,native[0],old)
                records.append({'symbol':symbol,'status':'SUCCESS','contracts':native,'diagnostics':backend.errors[mark:]})
            except Exception as exc:
                records.append({'symbol':symbol,'status':'FAILED','contracts':native,
                    'error_type':type(exc).__name__,'error_code':error_code(exc),'diagnostics':backend.errors[mark:]})
    except Exception as exc:
        records.append({'symbol':None,'status':'CONNECTION_FAILED','error_type':type(exc).__name__,'error_code':error_code(exc),
            'diagnostics':list(backend.errors) if backend is not None else []})
    finally:
        if backend is not None:
            try:backend.disconnect()
            except Exception as exc:records.append({'symbol':None,'status':'DISCONNECT_ERROR','error_type':type(exc).__name__})
    return records


def acquire(archive,batches,plan_path,output,*,port,client_id,connect=False,read_only=False,paper=False,reference=None):
    if not (connect and read_only and paper and reference):
        raise ValueError('explicit connection, paper authentication, socket/Read-Only API and permission reference required')
    if type(port) is not int or not 1<=port<=65535 or type(client_id) is not int or client_id<=0:
        raise ValueError('explicit local port and positive unique client ID required')
    plan_files,plan_hash=read_bundle(Path(plan_path));planned=json.loads(plan_files['coverage-audit.json'])
    asof=datetime.now(UTC).isoformat();current=coverage_audit(archive,batches,asof)
    if (planned['source_manifest']['alert_manifest_sha256']!=current['source_manifest']['alert_manifest_sha256']
            or planned['required_latest_completed_session']!=current['required_latest_completed_session']
            or [i['symbol'] for i in planned['instruments']]!=[i['symbol'] for i in current['instruments']]
            or [i['contract'] for i in planned['instruments']]!=[i['contract'] for i in current['instruments']]):
        raise ValueError('pre-acquisition audit is stale or differs; produce a new audit before connecting')
    root=Path(output);root.mkdir(parents=True,exist_ok=False)
    pacer=Pacer()
    attempts=asyncio.run(qualify(current['instruments'],'127.0.0.1',port,client_id,pacer=pacer))
    hashes=write_bundle(root/'qualification-v1',{'qualification.json':encode({'schema_version':'marketlife_qualification_v1',
        'started_at':asof,'completed_at':datetime.now(UTC).isoformat(),'attempts':attempts,'pre_audit_sha256':plan_hash['bundle_sha256'],
        'host':'127.0.0.1','port':port,'client_id':client_id,'paper_authenticated_operator_confirmed':True,
        'socket_and_read_only_operator_confirmed':True,'reference':reference,'account_details_requested':False})})
    provider=IBKRDailyProvider(port=port,client_id=client_id,pacer=pacer,max_attempts=2)
    paths=[];cal,required=completed_window(asof,archive['calendar']['start'])
    completed=[s['session_date'] for s in cal['sessions'] if s['session_date']<=required[-1]]
    start=completed[max(0,completed.index(required[0])-5)]
    for attempt in attempts:
        if attempt['status']!='SUCCESS':continue
        symbol=attempt['symbol'];contract=attempt['contracts'][0]
        if symbol in archive['coverage']:
            security=replace(Security(**archive['coverage'][symbol]['security']),con_id=contract['conId'])
        else:
            security=Security(symbol,f'ibkr-conid:{contract["conId"]}',reference,symbol,symbol,
                contract['primaryExchange'],contract['primaryExchange'],con_id=contract['conId'])
        path=root/f'{symbol}-daily-v1'
        provider.fetch_daily(security,start,required[-1],path);paths.append(str(path))
    write_bundle(root/'acquisition-index-v1',{'index.json':encode({'schema_version':'marketlife_acquisition_index_v1',
        'qualification_bundle_sha256':hashes['bundle_sha256'],'acquisitions':paths,'requested_start':start,
        'requested_end':required[-1],'required_latest_at_start':required[-1],'completed_at':datetime.now(UTC).isoformat()})})
    return paths
