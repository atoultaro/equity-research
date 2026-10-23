"""Native identity, raw corporate-action gap and halted/stale-price controls."""

from decimal import Decimal
import argparse
from pathlib import Path
from experiments.backtest_engines.nautilus_runner import *
from nautilus_trader.model.data import InstrumentStatus
from nautilus_trader.model.enums import MarketStatusAction


class Probe(Strategy):
    def __init__(self,inst):
        super().__init__(StrategyConfig());self.inst=inst;self.rows=[];self.fills=[];self.rejected=[]
    def on_start(self):
        self.subscribe_bars(BarType.from_str(f'{self.inst.id}-1-DAY-LAST-EXTERNAL'))
        for stamp,tag in [('2022-04-12T13:30:00Z','BUY'),('2022-04-19T15:00:00Z','HALTED_BUY'),('2022-04-20T15:00:00Z','MOO')]:
            self.clock.set_time_alert(tag,dt(stamp),self.order)
    def order(self,event):
        order=self.order_factory.market(self.inst.id,OrderSide.BUY,Quantity.from_int(2 if event.name=='BUY' else 1),
                                       time_in_force=TimeInForce.AT_THE_OPEN if event.name=='MOO' else TimeInForce.GTC,
                                       client_order_id=ClientOrderId(event.name))
        self.submit_order(order)
    def on_bar(self,bar):self.rows.append({'at':iso_ns(bar.ts_event),'close':str(bar.close.as_decimal())})
    def on_order_filled(self,event):self.fills.append({'at':iso_ns(event.ts_event),'order':str(event.client_order_id),'price':str(event.last_px.as_decimal()),'quantity':str(event.last_qty.as_decimal())})
    def on_order_rejected(self,event):self.rejected.append(str(event))


def main():
    p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--split-adjusted',action='store_true');args=p.parse_args()
    control,sha=load_frozen(args.inputs,'compatibility.json')
    e=engine(Decimal('10000'));inst=instrument('PERMANENT_A','ALPHA');e.add_instrument(inst)
    # Same permanent ID can change its raw display symbol without changing the ID;
    # distinct IDs can carry the same raw ticker and remain separate in the cache.
    renamed=instrument('PERMANENT_A','BETA');e.add_instrument(renamed)
    for identity in ['OLD_ISSUER','NEW_ISSUER','CLASS_A','CLASS_B']:
        e.add_instrument(instrument(identity,'REUSED' if 'ISSUER' in identity else 'DUAL'))
    rows=control['rows']
    if args.split_adjusted:
        rows=[{**r,**({k:str(Decimal(r[k])*Decimal('0.5')) for k in ('open','high','low','close')} if r['session_date']<control['split_date'] else {})} for r in rows]
    e.add_data(make_bars(inst,rows))
    status=InstrumentStatus(inst.id,MarketStatusAction.HALT,ns('2022-04-19T13:30:00Z'),ns('2022-04-19T13:30:00Z'),reason='SYNTHETIC_HALT',is_trading=False)
    e.add_data([status]);strategy=Probe(inst);e.add_strategy(strategy);e.run()
    result={'split_adjusted_view':args.split_adjusted,'engine':'nautilus','version':nautilus_trader.__version__,'input_bundle_sha256':sha,'control':control,
        'identity_count':len(e.cache.instruments()),'identity_map':{str(i.id):str(i.raw_symbol) for i in e.cache.instruments()},
        'native_bars':strategy.rows,'fills':strategy.fills,'rejected':strategy.rejected,
        'positions':[{'instrument':str(p.instrument_id),'quantity':str(p.quantity.as_decimal()),'unrealized_pnl_at_49':str(p.unrealized_pnl(Price.from_str('49.00')).as_decimal())} for p in e.cache.positions_open()],
        'final_cash':str(e.cache.account_for_venue(Venue('XNAS')).balance_total(USD).as_decimal()),
        'actions':'Native Equity + OHLC has no configured split/dividend ledger; omitted terminal value is never mapped to a synthetic InstrumentClose',
        'pit':'External immutable master and membership clocks required; metadata overwrite above is an explicit cache capability probe, not automatic PIT history'}
    write_result(args.output,result);e.dispose()


if __name__=='__main__':main()
