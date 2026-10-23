"""Native equity portfolio workload with precomputed PIT membership/order intents."""

from AlgorithmImports import *
import os
import sys
from datetime import timezone
from pathlib import Path
from time import perf_counter
sys.path.insert(0,os.environ['SPIKE_CODE_ROOT'])
from experiments.backtest_engines.protocol import dt,load_frozen,portfolio_schedule,write_result,rss_bytes
from experiments.backtest_engines.lean_algorithm import CommonFee,FixedAdverseSlippage


class SpikePortfolio(QCAlgorithm):
    def initialize(self):
        start=perf_counter()
        panel,self.input_sha=load_frozen(os.environ['SPIKE_INPUTS'],'portfolio.json')
        self.count=int(os.environ['SPIKE_COUNT']);self.stocks,self.batches=portfolio_schedule(panel,self.count)
        self.set_brokerage_model(DefaultBrokerageModel(AccountType.CASH))
        self.set_start_date(2022,1,3);self.set_end_date(2022,6,30);self.set_time_zone(TimeZones.UTC)
        self.set_cash(float(panel['initial_cash']));self.settings.daily_precise_end_time=True
        self.settings.minimum_order_margin_portfolio_percentage=0
        self.universe_settings.resolution=Resolution.DAILY;self.universe_settings.fill_forward=False
        self.universe_settings.data_normalization_mode=DataNormalizationMode.RAW
        self.symbols={};self.fills=[];self.actions=[];self.rejected=[];self.selections=[];self.bars_seen=0
        self.feed_only=os.environ.get('SPIKE_FEED_ONLY')=='1'
        self.simulation_started=None
        self.native_universe=os.environ.get('SPIKE_NATIVE_UNIVERSE')=='1'
        self.set_security_initializer(self.initialize_security)
        for i,stock in enumerate(self.stocks):
            alias=f'E{i:05d}'
            self.symbols[stock['security_id']]=(Symbol.create(alias,SecurityType.EQUITY,Market.USA) if self.native_universe else
                self.add_equity(alias,Resolution.DAILY,Market.USA,False,1,False,DataNormalizationMode.RAW).symbol)
        self.set_benchmark(next(iter(self.symbols.values())))
        if self.native_universe:
            self.add_universe(ScheduledUniverse(self.date_rules.every_day(),self.time_rules.at(0,1),self.select))
        for batch in self.batches:
            self.schedule_at(batch['source_signal_timestamp'],lambda b=batch:self.action('signal',b))
            self.schedule_at(batch['activation_timestamp'],lambda b=batch:self.action('entry',b))
            self.schedule_at(batch['exit_timestamp'],lambda b=batch:self.action('exit',b))
        self.initialization_seconds=perf_counter()-start

    def initialize_security(self,security):
        security.set_fee_model(CommonFee());security.set_slippage_model(FixedAdverseSlippage())

    def select(self,time):
        stamp=self.utc_time.replace(tzinfo=timezone.utc)
        selected=None
        for batch in self.batches:
            if dt(batch['source_signal_timestamp'])<stamp and dt(batch['activation_timestamp']).date()<=stamp.date():selected=batch
        ids=[x['security_id'] for x in selected['orders']] if selected else []
        self.selections.append({'at':stamp.isoformat(),'members':ids})
        return [self.symbols[sid] for sid in ids]

    def schedule_at(self,stamp,callback):
        t=dt(stamp)
        self.schedule.on(self.date_rules.on(t.year,t.month,t.day),self.time_rules.at(t.hour,t.minute,t.second),callback)

    def action(self,kind,batch):
        self.actions.append({'kind':kind,'at':self.utc_time.replace(tzinfo=timezone.utc).isoformat(),
            'source_signal_timestamp':batch['source_signal_timestamp'],'selection_date':batch['selection_date'],'count':len(batch['orders'])})
        if kind=='signal' or self.feed_only:return
        for request in batch['orders']:
            symbol=self.symbols[request['security_id']]
            if kind=='entry':self.stop_market_order(symbol,1,float(request['trigger']),tag='ENTRY')
            elif self.portfolio[symbol].invested:self.market_order(symbol,-self.portfolio[symbol].quantity,tag='EXIT')

    def on_data(self,data):
        if self.simulation_started is None:self.simulation_started=perf_counter()
        self.bars_seen+=len(data.bars)

    def on_order_event(self,event):
        if event.status==OrderStatus.INVALID:self.rejected.append(str(event))
        if event.status!=OrderStatus.FILLED:return
        self.fills.append({'instrument_id':str(event.symbol),'side':'BUY' if event.fill_quantity>0 else 'SELL',
            'quantity':str(abs(event.fill_quantity)),'price':str(event.fill_price),'total_fee':str(event.order_fee.value.amount),
            'at':event.utc_time.replace(tzinfo=timezone.utc).isoformat()})

    def on_end_of_algorithm(self):
        write_result(os.environ['SPIKE_OUTPUT'],{'engine':'lean','active_members':self.count,'distinct_security_ids':len(self.stocks),
            'input_bundle_sha256':self.input_sha,'fills':self.fills,'actions':self.actions,'bars_seen':self.bars_seen,
            'expected_bars':sum(len(s['rows']) for s in self.stocks),'feed_only':self.feed_only,'simulation_and_accounting_seconds':perf_counter()-self.simulation_started if self.simulation_started else None,'native_universe_probe':self.native_universe,'native_selections':self.selections,
            'rejected':self.rejected,'final_cash':str(self.portfolio.cash),'final_equity':str(self.portfolio.total_portfolio_value),
            'account_type':str(self.brokerage_model.account_type),'unsettled_cash':str(self.portfolio.unsettled_cash_book.total_value),'open_positions':sum(1 for security in self.securities.values() if security.holdings.invested),
            'identity_map':{sid:str(symbol.id) for sid,symbol in self.symbols.items()},
            'initialization_seconds':self.initialization_seconds,'peak_rss_bytes':rss_bytes()})
