"""Prepare native LEAN daily equity files and invoke the source-built launcher."""

import argparse
from datetime import datetime,timezone
from decimal import Decimal
import json
import os
from pathlib import Path
import shutil
import subprocess
from time import perf_counter
import zipfile

from experiments.backtest_engines.protocol import load_frozen,write_result,rss_bytes,reconcile,portfolio_schedule


def daily_zip(root,symbol,rows):
    target=root/'equity/usa/daily'/f'{symbol.lower()}.zip'
    target.parent.mkdir(parents=True,exist_ok=True)
    lines=[]
    for r in rows:
        prices=[str(int(Decimal(r[k])*10000)) for k in ('open','high','low','close')]
        lines.append(','.join([r['session_date'].replace('-','')+' 00:00',*prices,str(int(Decimal(r['volume']))) ]))
    with zipfile.ZipFile(target,'x',compression=zipfile.ZIP_DEFLATED) as z:
        info=zipfile.ZipInfo(symbol.lower()+'.csv',date_time=(2020,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
        z.writestr(info,'\n'.join(lines)+'\n')
    maps=root/'equity/usa/map_files';maps.mkdir(parents=True,exist_ok=True)
    (maps/f'{symbol.lower()}.csv').write_text(f"{rows[0]['session_date'].replace('-','')},{symbol.lower()}\n20501231,{symbol.lower()}\n")
    factors=root/'equity/usa/factor_files';factors.mkdir(parents=True,exist_ok=True)
    (factors/f'{symbol.lower()}.csv').write_text('19980101,1,1,0\n20501231,1,1,0\n')


def prepare(args,case):
    args.work.mkdir(parents=True,exist_ok=False)
    data=args.work/'data';data.mkdir()
    for folder in ('market-hours','symbol-properties'):
        shutil.copytree(args.lean/'Data'/folder,data/folder)
    if args.compatibility:
        daily_zip(data,'ALPHA',case['rows'])
        sentinel=[{**s,'open':'100','high':'100','low':'100','close':'100','volume':'10000'} for s in case['sessions']]
        daily_zip(data,'BANCH',sentinel)
        shutil.copyfile(data/'equity/usa/daily/alpha.zip',data/'equity/usa/daily/beta.zip')
        (data/'equity/usa/map_files/alpha.csv').write_text('20000103,alpha\n20220414,alpha\n20220421,beta\n')
        (data/'equity/usa/factor_files/alpha.csv').write_text('20000103,0.98,0.5,100\n20220414,0.98,0.5,100\n20220419,0.98,1,50\n20501231,1,1,49\n')
    elif args.count:
        stocks,_=portfolio_schedule(case,args.count)
        for i,stock in enumerate(stocks):daily_zip(data,f'E{i:05d}',stock['rows'])
    else:daily_zip(data,'SYNTH',case['rows'])
    rates=data/'alternative/interest-rate/usa';rates.mkdir(parents=True)
    (rates/'interest-rate.csv').write_text('2000-01-01,0\n2050-12-31,0\n')
    config={'environment':'backtesting','live-mode':False,'algorithm-type-name':'SpikeCompatibility' if args.compatibility else 'SpikePortfolio' if args.count else 'SpikeAlgorithm','algorithm-language':'Python',
        'algorithm-location':str(Path(__file__).with_name('lean_compatibility_algorithm.py' if args.compatibility else 'lean_portfolio_algorithm.py' if args.count else 'lean_algorithm.py').resolve()),'python-venv':str(args.python_env.resolve()),
        'data-folder':str(data.resolve()),'results-destination-folder':str((args.work/'native-results').resolve()),
        'object-store-root':str((args.work/'object-store').resolve()),'debugging':False,'close-automatically':True,
        'log-handler':'QuantConnect.Logging.CompositeLogHandler','messaging-handler':'QuantConnect.Messaging.Messaging',
        'job-queue-handler':'QuantConnect.Queues.JobQueue','api-handler':'QuantConnect.Api.Api',
        'map-file-provider':'QuantConnect.Data.Auxiliary.LocalDiskMapFileProvider',
        'factor-file-provider':'QuantConnect.Data.Auxiliary.LocalDiskFactorFileProvider',
        'data-provider':'QuantConnect.Lean.Engine.DataFeeds.DefaultDataProvider','data-channel-provider':'DataChannelProvider',
        'object-store':'QuantConnect.Lean.Engine.Storage.LocalObjectStore',
        'setup-handler':'QuantConnect.Lean.Engine.Setup.BacktestingSetupHandler',
        'result-handler':'QuantConnect.Lean.Engine.Results.BacktestingResultHandler',
        'data-feed-handler':'QuantConnect.Lean.Engine.DataFeeds.FileSystemDataFeed',
        'real-time-handler':'QuantConnect.Lean.Engine.RealTime.BacktestingRealTimeHandler',
        'history-provider':['QuantConnect.Lean.Engine.HistoricalData.SubscriptionDataReaderHistoryProvider'],
        'transaction-handler':'QuantConnect.Lean.Engine.TransactionHandlers.BacktestingTransactionHandler',
        'job-user-id':'0','api-access-token':'','job-organization-id':'','show-missing-data-logs':True,'log-level':'error',
        'python-additional-paths':[str((args.lean/'Common').resolve())]}
    path=args.work/'config.json';path.write_text(json.dumps(config,indent=2))
    return path


def main():
    p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,required=True);p.add_argument('--case');p.add_argument('--count',type=int,choices=(10,100,1000));p.add_argument('--native-universe',action='store_true');p.add_argument('--feed-only',action='store_true');p.add_argument('--compatibility',action='store_true');p.add_argument('--native-costs',action='store_true');p.add_argument('--split-adjusted',action='store_true')
    p.add_argument('--work',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--lean',type=Path,required=True);p.add_argument('--dotnet',type=Path,required=True);p.add_argument('--python-env',type=Path,required=True)
    args=p.parse_args();start=perf_counter()
    data,input_sha=load_frozen(args.inputs,'compatibility.json' if args.compatibility else 'portfolio.json' if args.count else 'cases.json')
    case=data if args.count or args.compatibility else next(c for c in data if c['case']==args.case)
    config=prepare(args,case);prepared=perf_counter()
    env={**os.environ,'DOTNET_CLI_TELEMETRY_OPTOUT':'1','PYTHONNET_PYDLL':os.environ.get('SPIKE_PYDLL','/Library/Frameworks/Python.framework/Versions/3.11/lib/libpython3.11.dylib'),
         'SPIKE_CODE_ROOT':str(Path(__file__).resolve().parents[2]),'SPIKE_INPUTS':str(args.inputs.resolve()),'SPIKE_CASE':args.case or '', 'SPIKE_FEED_ONLY':'1' if args.feed_only else '0','SPIKE_NATIVE_COSTS':'1' if args.native_costs else '0','SPIKE_SPLIT_ADJUSTED':'1' if args.split_adjusted else '0', 'SPIKE_COUNT':str(args.count or 0),'SPIKE_NATIVE_UNIVERSE':'1' if args.native_universe else '0',
         'SPIKE_OUTPUT':str((args.work/'algorithm-result.json').resolve())}
    binary=args.lean/'Launcher/bin/Release/QuantConnect.Lean.Launcher.dll'
    with (args.work/'launcher.log').open('x') as log:
        result=subprocess.run(['/usr/bin/time','-l','-o',str((args.work/'process-time.txt').resolve()),str(args.dotnet.resolve()),str(binary.resolve()),'--config',str(config.resolve())],
            cwd=binary.parent,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=180)
    done=perf_counter()
    payload={'engine':'lean','case':args.case,'input_bundle_sha256':input_sha,'returncode':result.returncode,
             'count':args.count,'timings':{'preparation_seconds':prepared-start,'launcher_seconds':done-prepared,'total_seconds':done-start}}
    import re
    rawtime=(args.work/'process-time.txt').read_text()
    match=re.search(r'(\d+)\s+maximum resident set size',rawtime)
    payload['process_peak_rss_bytes']=int(match.group(1)) if match else None
    resultfile=args.work/'algorithm-result.json'
    if resultfile.exists():
        payload['result']=json.loads(resultfile.read_bytes())
        if not args.count and not args.compatibility:payload['result']['trade']=reconcile(payload['result']['fills'],case['intent']['stop'],case['intent']['initial_cash'])
    else:payload['status']='FAILED_NO_ALGORITHM_RESULT'
    if result.returncode and resultfile.exists():payload['status']='RESULT_AVAILABLE_BUT_LAUNCHER_EXIT_FAILED'
    write_result(args.output,payload)
    if result.returncode or not resultfile.exists():raise SystemExit(2)


if __name__=='__main__':main()
