"""Freeze observed raw results, environment identities and comparison audits."""

import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import platform
import re
from statistics import mean
import subprocess

from equity_research.ingestion.storage import encode,digest,write_bundle
from .protocol import load_frozen
from .analyze import cost_audit,repeat_summary,weighted_scores


def file_sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def payload(path,engine):
    raw=json.loads(Path(path).read_bytes())
    return raw['results'][0] if engine=='nautilus' else raw['result']


def environment(root):
    packages={}
    for label,file in [('nautilus','nt-install-report.json'),('lean_python','lean-python-install-report.json')]:
        report=json.loads((root/file).read_bytes())
        packages[label]=[{'name':p['metadata']['name'],'version':p['metadata']['version'],
            'wheel_url':p['download_info']['url'],'hashes':p['download_info']['archive_info'].get('hashes',{})} for p in report['install']]
    assets=json.loads((root/'toolchain/Lean/Launcher/obj/project.assets.json').read_bytes())
    nuget={k:{'sha512':v.get('sha512')} for k,v in assets['libraries'].items() if v['type']=='package'}
    assembly=root/'toolchain/Lean/Launcher/bin/Release'
    binaries={p.name:file_sha(p) for p in sorted(assembly.glob('*.dll'))}
    build=(root/'lean-build.log').read_text()
    audits=sorted(set(re.findall(r"Package '[^']+' [^\n]+https://github.com/advisories/[^\s]+",build)))
    return {'observed_date':'2026-10-23','os':platform.platform(),'architecture':platform.machine(),
        'hardware':{'cpu':'Apple M1','physical_cores':8,'logical_cores':8,'ram_bytes':17179869184},
        'nautilus':{'version':'1.231.0','line':'STABLE_1_X','python':'3.13.3',
            'tag':json.loads((root/'nt-release-ref.json').read_bytes()),'source_tag_object':json.loads((root/'nt-release-tag.json').read_bytes()),
            'license':'LGPL-3.0','requirements':(root/'nt-freeze.txt').read_text()},
        'lean':{'engine_assembly_version':'2.5.0.0','source_commit':'f3d841e60dfd010ee5fc293ea893e56952484108',
            'python':'3.11.6','diagnostic_python':'3.12.9','pythonnet':'2.0.66','dotnet_sdk':'10.0.402','license':'Apache-2.0',
            'python_requirements':(root/'lean-python-freeze.txt').read_text(),'nuget_libraries':nuget,'native_assembly_sha256':binaries,
            'nuget_audit_warnings':audits,'dotnet_installer_sha256':file_sha(root/'toolchain/dotnet-install.sh')},
        'packages':packages,'network':'OS sandbox-exec deny network* on each evaluated child; software installation was online',
        'docker':'Client 20.10.12 installed; daemon unavailable; not started or used',
        'accounts':'No credentials, subscription, cloud service or brokerage connection used',
        'engine_adapter_commit':subprocess.check_output(['git','rev-parse','01692c8'],text=True).strip(),
        'core_base_commit':'2b6ffa0daf2becdb5d2616d2bb1e82a3bb134f5c'}


def summarize_scale(directory):
    rows=[];repeats=[]
    for count in (10,100,1000):
        for engine,prefix in [('nautilus','nt'),('lean','lean')]:
            modes={}
            for mode in ('orders','feed'):
                observed=[]
                for repeat in (1,2):
                    path=directory/f'{prefix}-{count}-{mode}-r{repeat}.json'
                    raw=json.loads(path.read_bytes());r=payload(path,engine)
                    if r['bars_seen']!=r['expected_bars']:raise ValueError(f'incomplete price loop: {path}')
                    elapsed=(r['stage_seconds']['simulation_and_accounting'] if engine=='nautilus' else r['simulation_and_accounting_seconds'])
                    index=json.loads((directory/'run-index.json').read_bytes())
                    process=next(p for p in index['processes'] if p['result_file']==path.name)
                    observed.append({'repeat':repeat,'bars_seen':r['bars_seen'],'expected_bars':r['expected_bars'],
                        'active_members':count,'distinct_ids':r['distinct_security_ids'],'fill_count':len(r['fills']),
                        'final_cash':r['final_cash'],'final_equity':r['final_equity'],'open_positions':r['open_positions'],
                        'wall_seconds':process['wall_seconds'],'loop_seconds':elapsed,
                        'end_to_end_bars_per_second':r['bars_seen']/process['wall_seconds'],
                        'loop_bars_per_second':r['bars_seen']/elapsed,
                        'peak_rss_bytes':raw['peak_rss_bytes'] if engine=='nautilus' else raw['process_peak_rss_bytes'],
                        'stages':r.get('stage_seconds',{'initialization':r.get('initialization_seconds')}),
                        'process_status':process['status'],'native_returncode':raw.get('returncode',0)})
                comparison=repeat_summary(payload(directory/f'{prefix}-{count}-{mode}-r1.json',engine),payload(directory/f'{prefix}-{count}-{mode}-r2.json',engine))
                repeats.append({'engine':engine,'count':count,'mode':mode,**comparison})
                if not comparison['economic_content_equal']:raise ValueError(f'economic repeatability failed: {engine}/{count}/{mode}')
                modes[mode]=observed
            rows.append({'engine':engine,'count':count,'orders':modes['orders'],'feed_only':modes['feed'],
                'incremental_order_accounting_callback_seconds':[a['loop_seconds']-b['loop_seconds'] for a,b in zip(modes['orders'],modes['feed'])],
                'overhead_interpretation':'Paired loop difference includes order handling, portfolio/accounting and strategy callbacks; not an isolated ledger profiler. Negative differences can reflect run noise.'})
    return rows,repeats


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--inputs',type=Path,required=True)
    p.add_argument('--cases',type=Path,required=True);p.add_argument('--scale',type=Path,required=True);p.add_argument('--compatibility',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    cases,input_sha=load_frozen(args.inputs,'cases.json');files={};indices={}
    for part,directory in [('cases',args.cases),('scale',args.scale),('compatibility',args.compatibility)]:
        index=json.loads((directory/'run-index.json').read_bytes())
        if not index['network_denied'] or index['input_bundle_sha256']!=input_sha:raise ValueError('evaluation input/isolation mismatch')
        indices[part]=index
        files[f'{part}-run-index.json']=encode(index)
        for record in index['processes']:
            path=directory/record['result_file']
            if not path.exists():raise ValueError(f'missing native result: {path}')
            files[f'{part}-{path.name}']=path.read_bytes()
            # Preserve full launcher diagnostics after removing local repo/host identifiers.
            log=directory/record['name']/'launcher.log'
            if log.exists():
                text=log.read_text().replace(str(Path.cwd()),'<REPO>').replace(platform.node(),'<HOST>')
                import gzip
                files[f'{part}-{record["name"]}-launcher.log.gz']=gzip.compress(text.encode(),mtime=0)
    comparisons=[]
    for mode in ('common','native'):
        nt=json.loads((args.cases/f'nt-cases-{mode}.json').read_bytes())
        nts={r['case']:r for r in nt['results']}
        for case in cases:
            leanfile=args.cases/f'lean-{case["case"]}-{mode}.json'
            lean=json.loads(leanfile.read_bytes())
            entry={'case':case['case'],'mode':mode,'intent':case['intent'],'source_signal_id':case.get('source_signal_id'),
                   'reference':case['reference'],'nautilus':cost_audit(case,nts[case['case']],'nautilus',mode),
                   'lean':cost_audit(case,lean['result'],'lean',mode),'lean_process_status':lean.get('status')}
            for engine,result in [('lean',lean['result']),('nautilus',nts[case['case']])]:
                available=[e for e in result['events'] if e['kind']=='signal_available']
                submitted=[e for e in result['events'] if e['kind']=='order_submitted']
                if available[0]['source_timestamp']!=case['intent']['signal_available_at'] or submitted[0]['at']!=case['intent']['activation_at']:
                    raise ValueError(f'signal/activation shifted: {engine}/{case["case"]}')
            comparisons.append(entry)
    scale,repeats=summarize_scale(args.scale)
    files.update({'comparison.json':encode(comparisons),'scale-summary.json':encode(scale),'repeatability.json':encode(repeats),
                  'scores.json':encode(weighted_scores()),'environment.json':encode(environment(args.root)),
                  'fixture-cases.json':(args.inputs/'cases.json').read_bytes(),'input-hashes.json':(args.inputs/'hashes.json').read_bytes(),
                  'compatibility-input.json':(args.inputs/'compatibility.json').read_bytes(),
                  'core-regression.txt':(args.root/'core-regression-v2.txt').read_bytes()})
    if (args.root/'identity-results').exists():
        for path in sorted((args.root/'identity-results').iterdir()):
            if path.name in {'lean.json','nautilus.json','lean-process.json'}:files['identity-'+path.name]=path.read_bytes()
            elif path.suffix=='.log':
                import gzip
                text=path.read_text().replace(str(Path.cwd()),'<REPO>').replace(platform.node(),'<HOST>')
                files['identity-'+path.name+'.gz']=gzip.compress(text.encode(),mtime=0)
        files['identity-input.json']=(args.root/'identity-inputs-v1/identity.json').read_bytes()
        files['identity-input-hashes.json']=(args.root/'identity-inputs-v1/hashes.json').read_bytes()
    before=json.loads((args.root/'preservation-before.json').read_bytes())
    changed=[name for name,expected in before.items() if not Path(name).is_file() or file_sha(name)!=expected]
    if changed:raise ValueError(f'original frozen inputs changed: {changed}')
    files['preservation.json']=encode({'files_checked':len(before),'changed_files':changed,'status':'UNCHANGED',
        'inventory_sha256':digest(encode(before)),'scope':['data/history_cache','data/research_datasets','tests/fixtures']})
    files['source-code-hashes.json']=encode({str(path):file_sha(path) for path in sorted(Path('experiments/backtest_engines').glob('*.py'))})
    files['scope.json']=encode({'origin':'SYNTHETIC','real_stock_edge_claim':False,'broker_connections':0,'live_or_paper_orders':0,
        'paid_subscription_or_infrastructure':False,'core_source_modified':False,'base':'2b6ffa0daf2becdb5d2616d2bb1e82a3bb134f5c',
        'input_bundle_sha256':input_sha,'statistics':'Descriptive execution/performance controls only; no PR7C outcomes merged with execution PnL',
        'readiness':'Neither prototype is ready as primary engine; retain PR4 temporarily',
        'raw_log_redaction':'Repo absolute path and hostname replaced in published launcher logs; numeric/event results unchanged'})
    sealed=write_bundle(args.output,files)
    print(json.dumps({'bundle_sha256':sealed['bundle_sha256'],'files':len(files),'input_bundle_sha256':input_sha},indent=2))


if __name__=='__main__':main()
