"""Offline MarketLife setup research and completeness-gated current registration."""
import argparse
from datetime import UTC,datetime
import json
from pathlib import Path
import socket
from equity_research.ingestion.storage import read_bundle,write_bundle,encode
from equity_research.marketlife_workflow import audit,freeze_study,load_study,register


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='operation',required=True)
    study=sub.add_parser('study');check=sub.add_parser('audit');forecast=sub.add_parser('register')
    for command in (study,check,forecast):
        command.add_argument('--archive',type=Path,required=True);command.add_argument('--operator-source',type=Path,required=True)
        command.add_argument('--source-assurance',type=Path)
    study.add_argument('--asof');check.add_argument('--asof')
    replay=sub.add_parser('replay');replay.add_argument('--study',type=Path,required=True)
    for command in (study,check,forecast,replay):command.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    def deny(*args,**kwargs):raise AssertionError('MarketLife research prohibits network connections')
    socket.socket.connect=socket.socket.connect_ex=socket.create_connection=deny
    if args.operation=='replay':result=write_bundle(args.output,load_study(args.study)[0])
    elif args.operation=='register':
        if args.source_assurance is None:p.error('current-data registration requires source completeness assurance')
        result=register(args.archive,args.operator_source,args.source_assurance,args.output)
    else:
        assurance=json.loads(args.source_assurance.read_bytes()) if args.source_assurance else None
        asof=args.asof or datetime.now(UTC).isoformat()
        if args.operation=='study':result=freeze_study(args.archive,args.operator_source,args.output,asof,assurance)
        else:
            a,_=read_bundle(args.archive);o,_=read_bundle(args.operator_source)
            result=write_bundle(args.output,{'registration-audit.json':encode(audit(json.loads(a['archive.json']),json.loads(o['operator-alerts.json']),assurance,asof))})
    print(json.dumps({'bundle_sha256':result['bundle_sha256'],'members':len(result['files'])}))


if __name__=='__main__':main()
