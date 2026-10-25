"""Stdlib-only transport across the isolated Python runtimes."""

from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import resource
import sys


def encode(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def load_frozen(directory, filename):
    directory=Path(directory)
    meta=json.loads((directory/'hashes.json').read_bytes())
    if meta['bundle_sha256']!=sha(encode(meta['files'])): raise ValueError('invalid input bundle seal')
    for name,expected in meta['files'].items():
        path=directory/name
        if path.name!=name or path.is_symlink(): raise ValueError('unsafe input member')
        with path.open('rb') as stream:
            if hashlib.file_digest(stream,'sha256').hexdigest()!=expected: raise ValueError('input content hash mismatch')
    return json.loads((directory/filename).read_bytes()),meta['bundle_sha256']


def dt(value):
    return datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(timezone.utc)


def ns(value):
    return int(dt(value).timestamp()*1_000_000_000)


def iso_ns(value):
    return datetime.fromtimestamp(value/1e9,timezone.utc).isoformat()


def rss_bytes():
    rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return rss if sys.platform=='darwin' else rss*1024


def write_result(output, result):
    path=Path(output)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as stream:stream.write(encode(result))


def reconcile(fills, stop, initial_cash):
    if len(fills)!=2: return None
    a,b=fills
    qty=Decimal(a['quantity'])
    if qty!=Decimal(b['quantity']):return None
    entry,exit_=Decimal(a['price']),Decimal(b['price'])
    fee=sum(Decimal(f['total_fee']) for f in fills)
    pnl=(exit_-entry)*qty
    risk=(entry-Decimal(stop))*qty
    return {'quantity':str(qty),'entry_price':str(entry),'exit_price':str(exit_),'actual_initial_risk_dollars':str(risk),
            'price_pnl_after_slippage_dollars':str(pnl),'total_fee_dollars':str(fee),'net_pnl_dollars':str(pnl-fee),
            'net_realized_r':str((pnl-fee)/risk) if risk>0 else None,'expected_final_cash':str(Decimal(initial_cash)+pnl-fee),
            'expected_final_equity':str(Decimal(initial_cash)+pnl-fee),'cash_assumption':'AFTER_SETTLEMENT; compare equity plus settlement buckets when needed','gross_before_slippage_dollars':None,'slippage_dollars':None,
            'gross_slippage_status':'Native price fills do not independently identify a pre-slippage counterfactual'}


def portfolio_schedule(panel, count):
    """Precompute identical intents from frozen ranked monthly membership only."""
    securities={s['security_id']:s for s in panel['securities']}
    sessions=panel['calendar']['sessions'];by_day={s['session_date']:i for i,s in enumerate(sessions)}
    batches=[];selected=set()
    for snapshot in panel['snapshots']:
        members=snapshot['members'][:count]
        ids=[m['security_id'] for m in members];selected.update(ids)
        first=by_day[snapshot['effective_start']]
        batches.append({'source_signal_timestamp':snapshot['decision_timestamp'],'activation_timestamp':sessions[first]['opens_at'],
            'exit_timestamp':sessions[first+4]['opens_at'],'selection_date':snapshot['selection_date'],
            'orders':[{'security_id':sid,'quantity':1,'trigger':str(Decimal(next(r for r in securities[sid]['rows'] if r['session_date']==snapshot['selection_date'])['close'])+Decimal('0.01'))} for sid in ids]})
    return [securities[sid] for sid in sorted(selected)],batches
