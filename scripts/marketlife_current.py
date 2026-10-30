"""PR9D source intake, audited IBKR acquisition and current forecast readiness."""
import argparse
from datetime import UTC,datetime
import json
from pathlib import Path
import socket

from equity_research.ingestion.storage import encode,read_bundle,write_bundle
from equity_research.marketlife_intake import append_source,coverage_audit,proof_record
from equity_research.marketlife_readiness import (batches_from_proofs,archive_files,load_archive,
    register_current,load_prediction)


def source_proof(path):
    files,hashes=read_bundle(path)
    return {'files':{k:v.decode() for k,v in files.items()},'hashes':hashes}


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='operation',required=True)
    plan=sub.add_parser('plan');source=sub.add_parser('source');acquire=sub.add_parser('acquire');freeze=sub.add_parser('archive')
    for command in (plan,source,acquire,freeze):
        command.add_argument('--parent-archive',type=Path,required=True)
        command.add_argument('--source',type=Path,action='append',required=True,help='ordered immutable operator source bundles')
    for command in (plan,source,freeze):command.add_argument('--asof',help='offline audit only; never operational registration')
    source.add_argument('--incoming',type=Path,required=True)
    for name in ('ibkr-port','ibkr-client-id'):acquire.add_argument('--'+name,type=int,required=True)
    for name in ('connect','read-only-api-confirmed','paper-authenticated-confirmed'):acquire.add_argument('--'+name,action='store_true')
    acquire.add_argument('--pre-audit',type=Path,required=True);acquire.add_argument('--permission-reference',required=True)
    freeze.add_argument('--acquisition',type=Path,action='append',default=[])
    freeze.add_argument('--acquisition-root',type=Path,help='directory produced by acquire')
    freeze.add_argument('--source-assurance',type=Path)
    register=sub.add_parser('register');register.add_argument('--archive',type=Path,required=True)
    replay=sub.add_parser('replay');replay.add_argument('--archive',type=Path);replay.add_argument('--prediction',type=Path)
    for command in (plan,source,acquire,freeze,register,replay):command.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.operation!='acquire':
        def deny(*args,**kwargs):raise AssertionError('offline current research prohibits network connections')
        socket.socket.connect=socket.socket.connect_ex=socket.create_connection=deny
    if args.operation=='replay':
        if bool(args.archive)==bool(args.prediction):p.error('select exactly one archive or prediction')
        files,_=load_archive(args.archive) if args.archive else load_prediction(args.prediction)
        result=write_bundle(args.output,files)
    elif args.operation=='register':result=register_current(args.archive,args.output)
    else:
        parent,ph=read_bundle(args.parent_archive);archive=json.loads(parent['archive.json'])
        proofs=[source_proof(path) for path in args.source];batches=batches_from_proofs(proofs)
        asof=getattr(args,'asof',None) or datetime.now(UTC).isoformat()
        if args.operation=='plan':result=write_bundle(args.output,{'coverage-audit.json':encode(coverage_audit(archive,batches,asof))})
        elif args.operation=='source':
            incoming=json.loads(args.incoming.read_bytes());append_source(archive,batches,incoming,asof)
            files={'operator-alerts.json':encode(incoming),'guidance.json':proofs[0]['files']['guidance.json'].encode()}
            result=write_bundle(args.output,files)
        elif args.operation=='acquire':
            from equity_research.marketlife_acquire import acquire as fetch
            paths=fetch(archive,batches,args.pre_audit,args.output,port=args.ibkr_port,client_id=args.ibkr_client_id,
                connect=args.connect,read_only=args.read_only_api_confirmed,paper=args.paper_authenticated_confirmed,
                reference=args.permission_reference)
            print(json.dumps({'acquisitions':paths}));return
        else:
            qualification=[];paths=args.acquisition
            if args.acquisition_root:
                index,_=read_bundle(args.acquisition_root/'acquisition-index-v1')
                paths=[*paths,*[Path(s) for s in json.loads(index['index.json'])['acquisitions']]]
                q,_=read_bundle(args.acquisition_root/'qualification-v1');qualification=json.loads(q['qualification.json'])
            assurance=json.loads(args.source_assurance.read_bytes()) if args.source_assurance else None
            files=archive_files(parent,ph,proofs,[proof_record(path) for path in paths],asof,assurance,qualification)
            result=write_bundle(args.output,files)
            gate=json.loads(files['readiness.json']);print(json.dumps({'readiness':gate['status'],'problems':len(gate['problems'])}))
    print(json.dumps({'bundle_sha256':result['bundle_sha256'],'members':len(result['files'])}))


if __name__=='__main__':main()
