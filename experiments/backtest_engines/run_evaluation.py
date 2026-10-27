"""Run isolated native engines sequentially; retain failures as evidence.

No library installation, source acquisition, broker connection or core mutation.
All paths and processes must already exist from the documented setup.
"""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from time import perf_counter

from experiments.backtest_engines.protocol import encode,load_frozen,sha,write_result


def main():
    p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--toolchain',type=Path,required=True);p.add_argument('--nt-python',type=Path,required=True);p.add_argument('--lean-python-env',type=Path,required=True)
    p.add_argument('--deny-network',action='store_true');p.add_argument('--part',choices=('cases','scale','compatibility'),required=True);args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    cases,input_sha=load_frozen(args.inputs,'cases.json')
    root=Path(__file__).resolve().parents[2]
    env={**os.environ,'PYTHONPATH':str(root)}
    common=['--inputs',str(args.inputs.resolve())]
    nt=[str(args.nt_python.absolute()),'-m','experiments.backtest_engines.nautilus_runner',*common]
    lean=[sys.executable,'-m','experiments.backtest_engines.lean_runner',*common,
        '--lean',str((args.toolchain/'Lean').resolve()),'--dotnet',str((args.toolchain/'dotnet/dotnet').resolve()),
        '--python-env',str(args.lean_python_env.resolve())]
    results=[]
    def execute(name,command,kind):
        output=args.output/(name+'.json')
        begin=perf_counter()
        with (args.output/(name+'.log')).open('x') as log:
            prefix=['/usr/bin/sandbox-exec','-p','(version 1)(allow default)(deny network*)'] if args.deny_network else []
            run=subprocess.run([*prefix,*command,'--output',str(output.resolve())],env=env,cwd=root,stdout=log,stderr=subprocess.STDOUT,timeout=240)
        elapsed=perf_counter()-begin
        result=json.loads(output.read_bytes()) if output.exists() else None
        record={'name':name,'kind':kind,'returncode':run.returncode,'wall_seconds':elapsed,'result_file':output.name,
                'result_sha256':sha(output.read_bytes()) if output.exists() else None,
                'status':'PROCESS_SUCCEEDED' if run.returncode==0 else 'PROCESS_FAILED_WITH_RESULT' if result is not None else 'PROCESS_FAILED_NO_RESULT'}
        results.append(record)
        print(json.dumps(record),flush=True)
    if args.part=='cases':
        for mode in ('common','native'):
            options=['--native-costs'] if mode=='native' else []
            execute('nt-cases-'+mode,[*nt,*options],mode)
            for case in cases:
                name='lean-'+case['case']+'-'+mode
                execute(name,[*lean,'--case',case['case'],'--work',str((args.output/name).resolve()),*options],mode)
    elif args.part=='scale':
        for count in (10,100,1000):
            for mode in ('orders','feed'):
                options=['--feed-only'] if mode=='feed' else []
                for repeat in (1,2):
                    name=f'nt-{count}-{mode}-r{repeat}'
                    execute(name,[*nt,'--count',str(count),*options],mode)
                    name=f'lean-{count}-{mode}-r{repeat}'
                    execute(name,[*lean,'--count',str(count),'--work',str((args.output/name).resolve()),*options],mode)
    else:
        command=[str(args.nt_python.absolute()),'-m','experiments.backtest_engines.nautilus_compatibility',*common]
        execute('nt-compatibility',command,'lifecycle')
        execute('nt-compatibility-adjusted',[*command,'--split-adjusted'],'adjusted-control')
        execute('lean-compatibility',[*lean,'--compatibility','--work',str((args.output/'lean-compatibility').resolve())],'lifecycle')
        execute('lean-compatibility-adjusted',[*lean,'--compatibility','--split-adjusted','--work',str((args.output/'lean-compatibility-adjusted').resolve())],'adjusted-control')
        execute('lean-native-universe',[*lean,'--count','10','--native-universe','--work',str((args.output/'lean-native-universe').resolve())],'native-universe')
    write_result(args.output/'run-index.json',{'input_bundle_sha256':input_sha,'part':args.part,'network_denied':args.deny_network,'processes':results})


if __name__=='__main__':main()
