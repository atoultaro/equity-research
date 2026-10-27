"""Stable NautilusTrader 1.231.0 experiment. No live adapters or custom fill rules."""

import argparse
from decimal import Decimal, ROUND_CEILING
import json
from pathlib import Path
from time import perf_counter

started=perf_counter()
from experiments.backtest_engines.protocol import dt,ns,iso_ns,load_frozen,rss_bytes,write_result,reconcile,portfolio_schedule
import nautilus_trader
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.backtest.models import FillModel,FeeModel
from nautilus_trader.config import BacktestEngineConfig,LoggingConfig,StrategyConfig,RiskEngineConfig
from nautilus_trader.model.currencies import USD
from nautilus_trader.model.data import Bar,BarType
from nautilus_trader.model.enums import AccountType,OmsType,OrderSide,TimeInForce
from nautilus_trader.model.identifiers import InstrumentId,Symbol,Venue,ClientOrderId,TraderId
from nautilus_trader.model.instruments import Equity
from nautilus_trader.model.objects import Price,Quantity,Money
from nautilus_trader.trading.strategy import Strategy
imports_done=perf_counter()
assert nautilus_trader.__version__=='1.231.0', 'This experiment uses stable 1.x APIs only'


class Costs(FeeModel):
    def get_commission(self,order,fill_qty,fill_px,instrument):
        return Money(Decimal('0.50')+Decimal('0.005')*fill_qty.as_decimal(),USD)


def instrument(sid,symbol,permanent_id=None):
    # Synthetic engine ID is an opaque alias for permanent security_id, not a
    # historical ticker join. raw_symbol is separate provenance/display metadata.
    return Equity(instrument_id=InstrumentId(Symbol(sid),Venue('XNAS')),raw_symbol=Symbol(symbol),currency=USD,
                  price_precision=2,price_increment=Price.from_str('0.01'),lot_size=Quantity.from_int(1),ts_event=0,ts_init=0,
                  info={'security_id':permanent_id or sid,'origin':'SYNTHETIC','price_basis':'RAW_TRADED','volume_basis':'RAW_SHARES'})


def make_bars(inst,rows,calendar=None):
    sessions={s['session_date']:s for s in (calendar or {}).get('sessions',[])}
    bt=BarType.from_str(f'{inst.id}-1-DAY-LAST-EXTERNAL')
    return [Bar(bar_type=bt,open=Price.from_str(f"{Decimal(r['open']):.2f}"),high=Price.from_str(f"{Decimal(r['high']):.2f}"),
                low=Price.from_str(f"{Decimal(r['low']):.2f}"),close=Price.from_str(f"{Decimal(r['close']):.2f}"),
                volume=Quantity.from_int(int(Decimal(r['volume']))),ts_event=ns(r.get('closes_at') or sessions[r['session_date']]['closes_at']),
                ts_init=ns(r.get('closes_at') or sessions[r['session_date']]['closes_at'])) for r in rows]


class Breakout(Strategy):
    def __init__(self,case,inst):
        super().__init__(StrategyConfig())
        self.case,self.inst,self.intent=case,inst,case['intent']
        self.records=[];self.fills=[];self.entry=None;self.children=[];self.bars_seen=0

    def note(self,kind,**values):
        self.records.append({'kind':kind,'at':iso_ns(self.clock.timestamp_ns()),**values})

    def on_start(self):
        self.subscribe_bars(BarType.from_str(f'{self.inst.id}-1-DAY-LAST-EXTERNAL'))
        self.clock.set_time_alert('signal',dt(self.intent['signal_available_at']),self.signal)

    def signal(self,event):
        self.note('signal_available',source_timestamp=self.intent['signal_available_at'])
        # Submit at the first eligible session's Open, not at a potentially
        # intraday publication instant that cannot use that day's earlier range.
        self.clock.set_time_alert('activate',dt(self.intent['activation_at']),self.activate)

    def activate(self,event):
        self.note('order_submitted',trigger=self.intent['trigger'],quantity=self.intent['quantity'])
        self.entry=self.order_factory.stop_market(self.inst.id,OrderSide.BUY,Quantity.from_int(self.intent['quantity']),
            Price.from_str(f"{Decimal(self.intent['trigger']):.2f}"),client_order_id=ClientOrderId('ENTRY'))
        self.submit_order(self.entry)

    def expire(self,event):
        if self.entry and self.entry.is_open and not self.fills:
            self.note('expiry_requested')
            self.cancel_order(self.entry)

    def on_bar(self,bar):
        self.bars_seen+=1
        if self.intent['expires_at'] and bar.ts_event>=ns(self.intent['expires_at']):self.expire(None)

    def on_order_filled(self,event):
        self.fills.append({'side':event.order_side.name,'quantity':str(event.last_qty.as_decimal()),'price':str(event.last_px.as_decimal()),
                           'total_fee':str(event.commission.as_decimal()),'at':iso_ns(event.ts_event),'order_id':str(event.client_order_id)})
        if event.order_side==OrderSide.BUY:
            stop=self.order_factory.stop_market(self.inst.id,OrderSide.SELL,event.last_qty,Price.from_str(f"{Decimal(self.intent['stop']):.2f}"),
                                               reduce_only=True,client_order_id=ClientOrderId('STOP'))
            price=event.last_px.as_decimal()
            target=(price+2*(price-Decimal(self.intent['stop']))).quantize(Decimal('0.01'),rounding=ROUND_CEILING)
            take=self.order_factory.limit(self.inst.id,OrderSide.SELL,event.last_qty,Price.from_str(str(target)),
                                          reduce_only=True,client_order_id=ClientOrderId('TARGET'))
            self.children=[stop,take]
            self.submit_order(stop);self.submit_order(take)
            self.note('protective_orders',stop=self.intent['stop'],target=str(target),relationship='STRATEGY_CANCELS_SIBLING_ON_FILL; native reduce_only')
        else:
            for order in self.children:
                if order.client_order_id!=event.client_order_id and order.is_open:self.cancel_order(order)

    def on_event(self,event):
        self.records.append({'kind':type(event).__name__,'at':iso_ns(event.ts_event),
            'order_id':str(getattr(event,'client_order_id','')),'native':str(event).split('event_id=')[0]})


def engine(cash,native_costs=False):
    result=BacktestEngine(BacktestEngineConfig(trader_id=TraderId('SPIKE-001'),logging=LoggingConfig(log_level='ERROR'),risk_engine=RiskEngineConfig(max_order_submit_rate='10000/00:00:01')))
    result.add_venue(Venue('XNAS'),oms_type=OmsType.NETTING,account_type=AccountType.CASH,base_currency=USD,
        starting_balances=[Money(cash,USD)],fill_model=FillModel(prob_slippage=0.0 if native_costs else 1.0,random_seed=17),fee_model=None if native_costs else Costs(),
        bar_adaptive_high_low_ordering=False)
    return result


def run_case(case,native_costs=False):
    e=engine(Decimal(case['intent']['initial_cash']),native_costs)
    inst=instrument('ONE',case['symbol'],case['security_id']);e.add_instrument(inst)
    bars=make_bars(inst,case['rows']);e.add_data(bars)
    strategy=Breakout(case,inst);e.add_strategy(strategy)
    e.run()
    account=e.cache.account_for_venue(Venue('XNAS'))
    cash=str(account.balance_total(USD).as_decimal())
    result={'source_security_id':case['security_id'],'source_signal_id':case.get('source_signal_id'),'case':case['case'],'events':strategy.records,'fills':strategy.fills,'bars_seen':strategy.bars_seen,
        'final_cash':cash,'final_equity':str(Decimal(cash)+sum((v.as_decimal() for v in e.portfolio.net_exposures(Venue('XNAS')).values()),Decimal(0))),'open_positions':len(e.cache.positions_open()),
        'trade':reconcile(strategy.fills,case['intent']['stop'],case['intent']['initial_cash']),
        'native_settings':{'cost_mode':'ENGINE_DEFAULT' if native_costs else 'COMMON_COST_CONFIGURATION','bar_path':'OPEN_HIGH_LOW_CLOSE (adaptive disabled)','slippage':'native probability=0' if native_costs else 'native probability=1, one tick',
                           'fees':'native maker/taker, zero instrument fee rates' if native_costs else '0.50 + 0.005/share via FeeModel, rounded by Money precision','fills':'UNMODIFIED'}}
    e.dispose()
    return result


class Portfolio(Strategy):
    def __init__(self,instruments,batches,feed_only=False):
        super().__init__(StrategyConfig())
        self.instruments=instruments;self.batches=batches;self.feed_only=feed_only
        self.fills=[];self.records=[];self.bars_seen=0;self.rejected=[]

    def on_start(self):
        for inst in self.instruments.values():self.subscribe_bars(BarType.from_str(f'{inst.id}-1-DAY-LAST-EXTERNAL'))
        for i,batch in enumerate(self.batches):
            self.clock.set_time_alert(f'signal-{i}',dt(batch['source_signal_timestamp']),self.action)
            self.clock.set_time_alert(f'entry-{i}',dt(batch['activation_timestamp']),self.action)
            self.clock.set_time_alert(f'exit-{i}',dt(batch['exit_timestamp']),self.action)

    def action(self,event):
        kind,index=event.name.split('-');batch=self.batches[int(index)]
        self.records.append({'kind':kind,'at':iso_ns(event.ts_event),'source_signal_timestamp':batch['source_signal_timestamp'],
                             'selection_date':batch['selection_date'],'count':len(batch['orders'])})
        if kind=='signal' or self.feed_only:return
        for request in batch['orders']:
            inst=self.instruments[request['security_id']]
            if kind=='entry':
                order=self.order_factory.stop_market(inst.id,OrderSide.BUY,Quantity.from_int(1),Price.from_str(f"{Decimal(request['trigger']):.2f}"))
            else:
                if not self.cache.positions_open(instrument_id=inst.id):continue
                order=self.order_factory.market(inst.id,OrderSide.SELL,Quantity.from_int(1),reduce_only=True)
            self.submit_order(order)

    def on_bar(self,bar):self.bars_seen+=1

    def on_order_filled(self,event):
        self.fills.append({'instrument_id':str(event.instrument_id),'side':event.order_side.name,'quantity':str(event.last_qty.as_decimal()),
            'price':str(event.last_px.as_decimal()),'total_fee':str(event.commission.as_decimal()),'at':iso_ns(event.ts_event)})

    def on_order_rejected(self,event):self.rejected.append(str(event))


def run_portfolio(panel,count,feed_only=False):
    loading=perf_counter()
    stocks,batches=portfolio_schedule(panel,count)
    e=engine(Decimal(panel['initial_cash']));instruments={}
    initialized=perf_counter()
    expected_bars=0;all_bars=[]
    for i,stock in enumerate(stocks):
        inst=instrument(f'E{i:05d}',stock['symbol'],stock['security_id']);instruments[stock['security_id']]=inst
        e.add_instrument(inst);bars=make_bars(inst,stock['rows'],panel['calendar']);all_bars.extend(bars)
        expected_bars+=len(bars)
    e.add_data(all_bars)  # One global stable sort, rather than re-sorting per ID.
    strategy=Portfolio(instruments,batches,feed_only);e.add_strategy(strategy)
    loaded=perf_counter();e.run();finished=perf_counter()
    result={'feed_only':feed_only,'active_members':count,'distinct_security_ids':len(stocks),'expected_bars':expected_bars,'bars_seen':strategy.bars_seen,
        'fills':strategy.fills,'actions':strategy.records,'rejected':strategy.rejected,
        'final_cash':str(e.cache.account_for_venue(Venue('XNAS')).balance_total(USD).as_decimal()),
        'final_equity':str(e.cache.account_for_venue(Venue('XNAS')).balance_total(USD).as_decimal()+sum((v.as_decimal() for v in e.portfolio.net_exposures(Venue('XNAS')).values()),Decimal(0))),'open_positions':len(e.cache.positions_open()),'source_universe_sha256':panel['source_universe_sha256'],
        'identity_map':{sid:str(inst.id) for sid,inst in instruments.items()},
        'stage_seconds':{'initialization':initialized-loading,'data_loading':loaded-initialized,'simulation_and_accounting':finished-loaded},
        'bars_per_simulation_second':strategy.bars_seen/(finished-loaded)}
    e.dispose();return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--case');p.add_argument('--count',type=int,choices=(10,100,1000));p.add_argument('--feed-only',action='store_true');p.add_argument('--native-costs',action='store_true');args=p.parse_args()
    data,input_sha=load_frozen(args.inputs,'portfolio.json' if args.count else 'cases.json')
    load_done=perf_counter()
    results=[run_portfolio(data,args.count,args.feed_only)] if args.count else [run_case(c,args.native_costs) for c in data if args.case is None or c['case']==args.case]
    done=perf_counter()
    write_result(args.output,{'engine':'nautilus','version':nautilus_trader.__version__,'input_bundle_sha256':input_sha,
        'results':results,'timings':{'imports_seconds':imports_done-started,'input_loading_seconds':load_done-imports_done,
                                  'engine_seconds':done-load_done,'total_seconds':done-started},'peak_rss_bytes':rss_bytes()})


if __name__=='__main__':main()
