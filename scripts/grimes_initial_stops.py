"""PR9F initial-stop experiment using frozen evidence only; no acquisition."""
import argparse
import json
from pathlib import Path
import socket

from equity_research.ingestion.storage import digest, read_bundle, write_bundle
from equity_research import initial_stops as draft


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--method', choices=['draft_v2','patterns_v3'], default='draft_v2',
        help='Preserve draft replay; patterns_v3 is the reconciled pattern-conditioned study.')
    sub = parser.add_subparsers(dest='operation', required=True)
    p = sub.add_parser('prepare'); p.add_argument('--parent', type=Path, required=True)
    p.add_argument('--parent-sha256', required=True)
    p.add_argument('--observation', type=Path, help='Immutable operator observation bundle; preserve all actions, study only NEW_SETUP.')
    p.add_argument('--earlier-observation', type=Path)
    p.add_argument('--risk-guidance', type=Path)
    p.add_argument('--original-cohort-only', action='store_true')
    a = sub.add_parser('annotate'); a.add_argument('--market', type=Path, required=True)
    a.add_argument('--market-sha256', required=True)
    c = sub.add_parser('compare'); c.add_argument('--annotations', type=Path, required=True)
    c.add_argument('--source', type=Path, required=True)
    r = sub.add_parser('replay'); r.add_argument('--study', type=Path, required=True)
    e = sub.add_parser('evidence'); e.add_argument('--study', type=Path, required=True)
    e.add_argument('--inputs', type=Path, required=True)
    v = sub.add_parser('charts'); v.add_argument('--study', type=Path, required=True)
    v.add_argument('--selection', type=Path); v.add_argument('--masked', action='store_true')
    for command in (p, a, c, r, e, v):
        command.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    module = draft
    if args.method == 'patterns_v3':
        from equity_research import initial_pattern_study
        module = initial_pattern_study
    def deny(*a, **k):
        raise AssertionError('PR9F is offline; network acquisition prohibited')
    socket.socket.connect = socket.socket.connect_ex = socket.create_connection = deny
    if args.operation == 'prepare':
        if args.method == 'patterns_v3':
            if not all((args.observation,args.earlier_observation,args.risk_guidance)):
                parser.error('patterns_v3 requires expanded observation, earlier observation and risk guidance bundles')
            files = module.prepare(args.parent,args.parent_sha256,args.observation,args.earlier_observation,args.risk_guidance,args.original_cohort_only)
        else: files = module.prepare(args.parent, args.parent_sha256, args.observation)
    elif args.operation == 'annotate':
        market = args.market.read_bytes()
        if digest(market) != args.market_sha256: raise ValueError('masked market hash differs')
        files = module.annotation_files(json.loads(market))
    elif args.operation == 'compare':
        a, ah = read_bundle(args.annotations); files = module.study_files(a, ah, args.source.read_bytes())
    elif args.operation == 'charts':
        from equity_research.initial_stop_charts import charts
        f, h = module.load_study(args.study)
        selection = json.loads(args.selection.read_bytes()) if args.selection else None
        files = charts(f, h, selection=selection, masked=args.masked)
    elif args.operation == 'evidence':
        f, h = module.load_study(args.study); i, ih = read_bundle(args.inputs)
        files = module.public_evidence(f, h, i, ih)
    else: files = module.load_study(args.study)[0]
    h = write_bundle(args.output, files)
    print(json.dumps({'sha256': h['bundle_sha256'], 'members': len(h['files'])}))


if __name__ == '__main__':
    main()
