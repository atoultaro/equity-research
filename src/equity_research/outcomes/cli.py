"""Explicit offline outcome command; does not acquire prices or regenerate signals."""
from pathlib import Path


def register(commands):
    p=commands.add_parser('outcomes',help='measure descriptive outcomes from frozen strategy bundles')
    p.add_argument('--strategy',type=Path,action='append',required=True,help='repeat for each immutable signal inventory')
    p.add_argument('--horizons',type=int,nargs='+',help='explicit horizons; zero applies only to Open; default Close 1/5/10/20 and Open 0/1/5/10/20')
    p.add_argument('--references',choices=('close','open'),nargs='+',default=['close','open'])
    p.add_argument('--minimum-clusters',type=int,default=10)
    p.add_argument('--output',type=Path,required=True)


def dispatch(args):
    from .model import Configuration
    from .dataset import freeze_outcomes
    from ..ingestion.storage import encode
    raw=tuple(args.horizons) if args.horizons is not None else None
    close=tuple(h for h in raw if h>0) if raw is not None else (1,5,10,20)
    opened=raw if raw is not None else (0,1,5,10,20)
    if raw is not None and any(h<0 for h in raw):raise ValueError('negative horizons unsupported')
    config=Configuration(close if 'close' in args.references else (),opened if 'open' in args.references else (),args.minimum_clusters)
    result=freeze_outcomes(args.strategy,args.output,configuration=config)
    print(encode({'output':str(args.output),'bundle_sha256':result['bundle_sha256']}).decode(),end='')
    return 0
