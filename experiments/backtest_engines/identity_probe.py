"""Project actual PR8A identity assertions into native instrument identifiers."""

import argparse
from pathlib import Path

from .protocol import load_frozen,write_result


def capture(master,output):
    from equity_research.universe import SecurityMaster
    from equity_research.ingestion.storage import encode,write_bundle
    m=SecurityMaster(master)
    rows=[]
    for day in ['2008-05-15','2015-05-15','2022-05-16']:
        cutoff=day+'T13:20:00+00:00'
        facts=[m.as_of(sid,day,cutoff) for sid in sorted(m.by_id)[:24]]
        rows.append({'effective_date':day,'decision_timestamp':cutoff,'records':[f for f in facts if f is not None]})
    # A permanent ID-to-native-ID map is chosen from the earliest sourced identity;
    # ticker strings are never used as cross-issuer keys.
    keys={sid:min(records,key=lambda f:f['effective_from']) for sid,records in m.by_id.items()}
    return write_bundle(output,{'identity.json':encode({'master_sha256':m.content_sha256,'snapshots':rows,
        'native_identity_keys':{sid:{'first_symbol':r['symbol'],'listing_start':r['listing_start']} for sid,r in keys.items()}})})


def native_nt(inputs,output):
    from .nautilus_runner import engine,instrument
    from decimal import Decimal
    records,sha=load_frozen(inputs,'identity.json');snapshots=[]
    for snapshot in records['snapshots']:
        e=engine(Decimal('10000'))
        mapping=[]
        for f in snapshot['records']:
            inst=instrument('ID'+f['security_id'].split(':')[-1],f['symbol'],f['security_id']);e.add_instrument(inst)
            mapping.append({'security_id':f['security_id'],'native_id':str(inst.id),'native_raw_symbol':str(inst.raw_symbol),
                            'issuer_id':f['issuer_id'],'share_class_id':f['share_class_id'],'source_exchange':f['exchange'],
                            'source_trading_status':f['trading_status']})
        snapshots.append({'effective_date':snapshot['effective_date'],'decision_timestamp':snapshot['decision_timestamp'],'mapping':mapping})
        e.dispose()
    write_result(output,{'engine':'nautilus','input_bundle_sha256':sha,'master_sha256':records['master_sha256'],
        'snapshots':snapshots,'scope':'Native equity/cache identity projection only; trading across live exchange transfer and historical identifier reuse NOT_VERIFIED'})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--master',type=Path);p.add_argument('--inputs',type=Path);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.master:print(capture(args.master,args.output))
    else:native_nt(args.inputs,args.output)
