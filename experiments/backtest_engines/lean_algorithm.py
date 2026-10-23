"""Python QCAlgorithm using native EquityFillModel and imported immutable intents."""

from AlgorithmImports import *
import json
import os
import sys
from pathlib import Path
from decimal import Decimal,ROUND_CEILING
from datetime import datetime,timezone

sys.path.insert(0,os.environ['SPIKE_CODE_ROOT'])
from experiments.backtest_engines.protocol import dt,load_frozen,write_result,rss_bytes


class CommonFee(FeeModel):
    def get_order_fee(self,parameters):
        value=0.50+0.005*abs(float(parameters.order.quantity))
        return OrderFee(CashAmount(value,'USD'))


class FixedAdverseSlippage:
    def get_slippage_approximation(self,asset,order):return 0.01


class SpikeAlgorithm(QCAlgorithm):
    def initialize(self):
        cases,self.input_sha=load_frozen(os.environ['SPIKE_INPUTS'],'cases.json')
        self.case=next(c for c in cases if c['case']==os.environ['SPIKE_CASE'])
        self.intent=self.case['intent'];rows=self.case['rows']
        first,last=rows[0]['session_date'],rows[-1]['session_date']
        self.set_start_date(*map(int,first.split('-')));self.set_end_date(*map(int,last.split('-')))
        self.set_brokerage_model(DefaultBrokerageModel(AccountType.CASH))
        self.set_time_zone(TimeZones.UTC);self.set_cash(float(self.intent['initial_cash']))
        self.settings.daily_precise_end_time=True
        self.settings.minimum_order_margin_portfolio_percentage=0
        equity=self.add_equity('SYNTH',Resolution.DAILY,Market.USA,False,1,False,DataNormalizationMode.RAW)
        self.symbol=equity.symbol
        self.set_benchmark(self.symbol)
        self.native_costs=os.environ.get('SPIKE_NATIVE_COSTS')=='1'
        if not self.native_costs:
            equity.set_fee_model(CommonFee());equity.set_slippage_model(FixedAdverseSlippage())
        self.records=[];self.fills=[];self.entry=None;self.children=[];self.bars_seen=0
        self.schedule_at(self.intent['signal_available_at'],self.signal)
        self.schedule_at(self.intent['activation_at'],self.activate)

    def schedule_at(self,stamp,callback):
        t=dt(stamp)
        self.schedule.on(self.date_rules.on(t.year,t.month,t.day),self.time_rules.at(t.hour,t.minute,t.second),callback)

    def note(self,kind,**values):
        self.records.append({'kind':kind,'at':self.utc_time.replace(tzinfo=timezone.utc).isoformat(),**values})

    def signal(self): self.note('signal_available',source_timestamp=self.intent['signal_available_at'])

    def activate(self):
        self.note('order_submitted',trigger=self.intent['trigger'],quantity=self.intent['quantity'])
        self.entry=self.stop_market_order(self.symbol,self.intent['quantity'],float(self.intent['trigger']),tag='ENTRY')

    def expire(self):
        if self.entry is not None and self.entry.status not in (OrderStatus.FILLED,OrderStatus.CANCELED) and not self.fills:
            self.note('expiry_requested');self.entry.cancel('third completed eligible session')

    def on_data(self,data):
        if data.bars.contains_key(self.symbol):
            self.bars_seen+=1
            if self.intent['expires_at'] and self.utc_time.replace(tzinfo=timezone.utc)>=dt(self.intent['expires_at']):self.expire()

    def on_order_event(self,event):
        order=self.transactions.get_order_by_id(event.order_id)
        self.records.append({'kind':str(event.status),'at':event.utc_time.replace(tzinfo=timezone.utc).isoformat(),
            'order_id':str(event.order_id),'tag':order.tag,'native':str(event)})
        if event.status!=OrderStatus.FILLED:return
        side='BUY' if event.fill_quantity>0 else 'SELL'
        self.fills.append({'side':side,'quantity':str(abs(event.fill_quantity)),'price':str(event.fill_price),
            'total_fee':str(event.order_fee.value.amount),'at':event.utc_time.replace(tzinfo=timezone.utc).isoformat(),
            'order_id':str(event.order_id),'tag':order.tag})
        if side=='BUY':
            stop=self.stop_market_order(self.symbol,-event.fill_quantity,float(self.intent['stop']),tag='STOP')
            entry=Decimal(str(event.fill_price));target=(entry+2*(entry-Decimal(self.intent['stop']))).quantize(Decimal('0.01'),rounding=ROUND_CEILING)
            take=self.limit_order(self.symbol,-event.fill_quantity,float(target),tag='TARGET')
            self.children=[stop,take];self.note('protective_orders',stop=self.intent['stop'],target=str(target))
        else:
            for child in self.children:
                if child.order_id!=event.order_id:child.cancel('sibling filled')

    def on_end_of_algorithm(self):
        result={'source_security_id':self.case['security_id'],'source_signal_id':self.case.get('source_signal_id'),'peak_rss_bytes':rss_bytes(),'engine':'lean','input_bundle_sha256':self.input_sha,'case':self.case['case'],'events':self.records,'fills':self.fills,
            'bars_seen':self.bars_seen,'final_cash':str(self.portfolio.cash),'unsettled_cash':str(self.portfolio.unsettled_cash_book.total_value),'final_equity':str(self.portfolio.total_portfolio_value),
            'holdings_quantity':str(self.portfolio[self.symbol].quantity),'account_type':str(self.brokerage_model.account_type),'open_positions':int(self.portfolio.invested),'native_security_identifier':str(self.symbol.id),
            'native_settings':{'cost_mode':'ENGINE_DEFAULT' if self.native_costs else 'COMMON_COST_CONFIGURATION','fills':'UNMODIFIED EquityFillModel','slippage':'engine default' if self.native_costs else 'fixed absolute 0.01 ISlippageModel cost configuration',
                'fees':'engine default' if self.native_costs else '0.50 + 0.005/share FeeModel','data':'native daily US equity RAW, fill_forward=False, precise_end_time=True'}}
        write_result(os.environ['SPIKE_OUTPUT'],result)
