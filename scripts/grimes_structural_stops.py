"""Full-population PR9E experiment; existing frozen inputs only, no network."""
import argparse
import json
from pathlib import Path
import socket

from equity_research.ingestion.storage import encode,read_bundle,write_bundle,digest
from equity_research.structural_stops import prepare,annotation_files_for,study_files,load_study,materiality


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='operation',required=True)
    export=sub.add_parser('prepare');export.add_argument('--archive',type=Path,required=True)
    annotate=sub.add_parser('annotate');annotate.add_argument('--market',type=Path,required=True)
    annotate.add_argument('--market-sha256',required=True)
    compare=sub.add_parser('compare');compare.add_argument('--annotations',type=Path,required=True)
    compare.add_argument('--source',type=Path,required=True)
    replay=sub.add_parser('replay');replay.add_argument('--study',type=Path,required=True)
    vintage=sub.add_parser('materiality');vintage.add_argument('--study',type=Path,required=True)
    vintage.add_argument('--vintages',type=Path,required=True)
    evidence=sub.add_parser('evidence');evidence.add_argument('--study',type=Path,required=True)
    evidence.add_argument('--inputs',type=Path,required=True)
    charts=sub.add_parser('charts');charts.add_argument('--study',type=Path,required=True)
    charts.add_argument('--masked',action='store_true');charts.add_argument('--selection',type=Path)
    for c in (export,annotate,compare,replay,charts,vintage,evidence):c.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    def deny(*a,**k):raise AssertionError('PR9E is offline; acquisition prohibited')
    socket.socket.connect=socket.socket.connect_ex=socket.create_connection=deny
    if args.operation=='prepare':files=prepare(args.archive)
    elif args.operation=='annotate':
        content=args.market.read_bytes()
        if digest(content)!=args.market_sha256:raise ValueError('market-only input hash differs')
        files=annotation_files_for(json.loads(content))
    elif args.operation=='compare':
        a,ah=read_bundle(args.annotations);files=study_files(a,ah,args.source.read_bytes())
    elif args.operation=='charts':
        from equity_research.structural_stop_charts import charts
        s,h=load_study(args.study)
        selection=json.loads(args.selection.read_bytes()) if args.selection else None
        files=charts(s,h,masked=args.masked,selection=selection)
    elif args.operation=='materiality':files=materiality(load_study(args.study)[0],args.vintages.read_bytes())
    elif args.operation=='evidence':
        from equity_research.structural_stop_charts import public_evidence
        s,h=load_study(args.study);i,ih=read_bundle(args.inputs);files=public_evidence(s,h,i,ih)
    else:files=load_study(args.study)[0]
    h=write_bundle(args.output,files)
    print(json.dumps({'sha256':h['bundle_sha256'],'members':len(h['files'])}))


if __name__=='__main__':main()
