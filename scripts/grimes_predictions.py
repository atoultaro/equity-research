"""Offline PR9C views, sealed forecasts, authorized reveals and append-only evaluations."""
import argparse
import json
from pathlib import Path
import socket

from equity_research.ingestion.storage import read_bundle,write_bundle
from equity_research.prospective import workflow as w


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='operation',required=True)
    base=sub.add_parser('baseline');base.add_argument('--parent',type=Path,required=True)
    view=sub.add_parser('view');view.add_argument('--archive',type=Path,required=True);view.add_argument('--cutoff',required=True);view.add_argument('--known-count',type=int)
    pred=sub.add_parser('predict');pred.add_argument('--view',type=Path,required=True);pred.add_argument('--mode',choices=['FORWARD_REGISTERED','RETROSPECTIVE_DRY_RUN'],required=True)
    reveal=sub.add_parser('reveal');reveal.add_argument('--prediction',type=Path,required=True);reveal.add_argument('--alert',type=Path,required=True)
    evaluate=sub.add_parser('evaluate');evaluate.add_argument('--prediction',type=Path,required=True);evaluate.add_argument('--reveal',type=Path,required=True)
    replay=sub.add_parser('replay-prediction');replay.add_argument('--prediction',type=Path,required=True)
    reval=sub.add_parser('replay-evaluation');reval.add_argument('--evaluation',type=Path,required=True);reval.add_argument('--prediction',type=Path,required=True);reval.add_argument('--reveal',type=Path,required=True)
    advance=sub.add_parser('advance');advance.add_argument('--archive',type=Path,required=True);advance.add_argument('--prediction',type=Path,required=True);advance.add_argument('--reveal',type=Path,required=True);advance.add_argument('--market-observations',type=Path);advance.add_argument('--calendar',type=Path)
    dry=sub.add_parser('dry-run');dry.add_argument('--archive',type=Path,required=True)
    rdry=sub.add_parser('replay-dry-run');rdry.add_argument('--study',type=Path,required=True)
    for command in (base,view,pred,reveal,evaluate,replay,reval,advance,dry,rdry):command.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    def denied(*args,**kwargs):raise AssertionError('prospective research commands prohibit network connections')
    socket.socket.connect=socket.socket.connect_ex=socket.create_connection=denied
    op=args.operation
    if op=='baseline':result=w.baseline(args.parent,args.output)
    elif op=='view':result=w.prepare(args.archive,args.cutoff,args.output,args.known_count)
    elif op=='predict':result=w.freeze(args.view,args.output,args.mode)
    elif op=='reveal':result=w.reveal(args.prediction,args.alert,args.output)
    elif op=='evaluate':result=w.evaluate(args.prediction,args.reveal,args.output)
    elif op=='replay-prediction':result=write_bundle(args.output,w.load_prediction(args.prediction)[0])
    elif op=='replay-evaluation':result=w.replay_evaluation(args.evaluation,args.prediction,args.reveal,args.output)
    elif op=='advance':result=w.advance(args.archive,args.prediction,args.reveal,args.output,args.market_observations,args.calendar)
    else:
        from equity_research.prospective.experiment import dry_run,replay_experiment
        result=dry_run(args.archive,args.output) if op=='dry-run' else replay_experiment(args.study,args.output)
    print(json.dumps({'bundle_sha256':result['bundle_sha256'],'members':len(result['files'])}))


if __name__=='__main__':main()
