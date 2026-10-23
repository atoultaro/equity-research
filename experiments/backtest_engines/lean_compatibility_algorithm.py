"""Native LEAN map/factor/delisting and missing-bar control, not admitted research."""

from AlgorithmImports import *
import os
import sys
from datetime import timezone
sys.path.insert(0,os.environ['SPIKE_CODE_ROOT'])
from experiments.backtest_engines.protocol import dt,load_frozen,write_result,rss_bytes


class SpikeCompatibility(QCAlgorithm):
    def initialize(self):
        self.control,self.input_sha=load_frozen(os.environ['SPIKE_INPUTS'],'compatibility.json')
        self.set_start_date(2022,4,11);self.set_end_date(2022,4,25);self.set_cash(10000);self.set_time_zone(TimeZones.UTC)
        self.settings.daily_precise_end_time=True
        self.split_adjusted=os.environ.get('SPIKE_SPLIT_ADJUSTED')=='1'
        self.equity=self.add_equity('ALPHA',Resolution.DAILY,Market.USA,False,1,False,DataNormalizationMode.SPLIT_ADJUSTED if self.split_adjusted else DataNormalizationMode.RAW)
        self.symbol=self.equity.symbol;self.initial_id=str(self.symbol.id)
        # Auxiliary BANCH has explicitly generated synthetic bars to keep the
        # clock running after ALPHA observations cease. It is not a market index.
        self.add_equity('BANCH',Resolution.DAILY,Market.USA,False,1,False,DataNormalizationMode.RAW)
        self.set_benchmark('BANCH')
        self.identity_probes={
            'reused_old':str(SecurityIdentifier.generate_equity(DateTime(2000,1,3),'REUSED',Market.USA)),
            'reused_new':str(SecurityIdentifier.generate_equity(DateTime(2015,1,2),'REUSED',Market.USA)),
            'class_a':str(SecurityIdentifier.generate_equity(DateTime(2000,1,3),'DUALA',Market.USA)),
            'class_b':str(SecurityIdentifier.generate_equity(DateTime(2000,1,3),'DUALB',Market.USA)),
            'relisted_old':str(SecurityIdentifier.generate_equity(DateTime(2000,1,3),'RELIST',Market.USA)),
            'relisted_new':str(SecurityIdentifier.generate_equity(DateTime(2022,1,3),'RELIST',Market.USA))}
        self.rows=[];self.events=[];self.fills=[]
        self.schedule.on(self.date_rules.on(2022,4,12),self.time_rules.at(13,30),self.buy)
        self.schedule.on(self.date_rules.on(2022,4,19),self.time_rules.at(15,0),self.halted_buy)

    def buy(self):self.market_order(self.symbol,2,tag='BUY')
    def halted_buy(self):self.market_order(self.symbol,1,tag='HALTED_BUY')

    def on_data(self,data):
        if data.bars.contains_key(self.symbol):
            self.rows.append({'at':self.utc_time.replace(tzinfo=timezone.utc).isoformat(),'close':str(data.bars[self.symbol].close),
                'symbol':str(self.symbol),'id':str(self.symbol.id),'shares':str(self.portfolio[self.symbol].quantity),'cash':str(self.portfolio.cash)})
        for kind,collection in [('split',data.splits),('dividend',data.dividends),('delisting',data.delistings),('symbol_change',data.symbol_changed_events)]:
            for event in collection.values():self.events.append({'kind':kind,'at':self.utc_time.replace(tzinfo=timezone.utc).isoformat(),
                'native':str(event),'shares':str(self.portfolio[self.symbol].quantity),'cash':str(self.portfolio.cash),'identity':str(self.symbol.id)})

    def on_order_event(self,event):
        if event.status==OrderStatus.FILLED:self.fills.append({'at':event.utc_time.replace(tzinfo=timezone.utc).isoformat(),
            'side':'BUY' if event.fill_quantity>0 else 'SELL','quantity':str(abs(event.fill_quantity)),'price':str(event.fill_price),
            'fee':str(event.order_fee.value.amount),'tag':self.transactions.get_order_by_id(event.order_id).tag})

    def on_end_of_algorithm(self):
        write_result(os.environ['SPIKE_OUTPUT'],{'engine':'lean','input_bundle_sha256':self.input_sha,'control':self.control,
            'split_adjusted_view':self.split_adjusted,'identity_probes':self.identity_probes,'native_bars':self.rows,'native_events':self.events,'fills':self.fills,'initial_sid':self.initial_id,'final_sid':str(self.symbol.id),
            'final_symbol':str(self.symbol),'final_cash':str(self.portfolio.cash),'final_equity':str(self.portfolio.total_portfolio_value),
            'shares':str(self.portfolio[self.symbol].quantity),'peak_rss_bytes':rss_bytes(),
            'terminal_admission':'UNRESOLVED_TERMINAL_VALUE; any engine automatic liquidation is unverified, never promoted to PR4'})
