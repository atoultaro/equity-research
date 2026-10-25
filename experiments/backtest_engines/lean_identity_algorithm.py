"""Native LEAN SID projection of the same actual PR8A master evidence."""

from AlgorithmImports import *
import os
import sys
sys.path.insert(0,os.environ['SPIKE_CODE_ROOT'])
from experiments.backtest_engines.protocol import load_frozen,write_result


class SpikeIdentity(QCAlgorithm):
    def initialize(self):
        records,self.input_sha=load_frozen(os.environ['SPIKE_IDENTITY_INPUTS'],'identity.json')
        self.set_start_date(2022,4,11);self.set_end_date(2022,4,12);self.set_cash(10000)
        self.add_equity('BANCH',Resolution.DAILY,Market.USA,False)
        self.master_sha=records['master_sha256'];self.snapshots=[]
        for snapshot in records['snapshots']:
            mapping=[]
            for f in snapshot['records']:
                key=records['native_identity_keys'][f['security_id']]
                year,month,day=map(int,key['listing_start'].split('-'))
                sid=SecurityIdentifier.generate_equity(DateTime(year,month,day),key['first_symbol'],Market.USA)
                symbol=Symbol(sid,f['symbol'])
                mapping.append({'security_id':f['security_id'],'native_id':str(symbol.id),'native_raw_symbol':str(symbol.value),
                    'issuer_id':f['issuer_id'],'share_class_id':f['share_class_id'],'source_exchange':f['exchange'],
                    'source_trading_status':f['trading_status']})
            self.snapshots.append({'effective_date':snapshot['effective_date'],'decision_timestamp':snapshot['decision_timestamp'],'mapping':mapping})

    def on_end_of_algorithm(self):
        write_result(os.environ['SPIKE_OUTPUT'],{'engine':'lean','input_bundle_sha256':self.input_sha,'master_sha256':self.master_sha,
            'snapshots':self.snapshots,'scope':'Native SID projection only; trading across historical reuse/exchange transfer NOT_VERIFIED'})
