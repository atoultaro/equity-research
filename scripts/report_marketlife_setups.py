"""Project verified local evidence or render offline reports into a NEW bundle."""
import argparse
import json
from pathlib import Path
import socket

from equity_research.ingestion.storage import encode,read_bundle,write_bundle
from equity_research.marketlife_reports import reports
from equity_research.marketlife_workflow import load_study


def research_from_projection(files):
    result=json.loads(files['source-evidence.json'])
    parts={'ledger':'opportunity-ledger.json','candidate_references':'risk-references.json',
        'four_case_comparison':'forensic-comparison.json','underway_comparison':'underway-transitions.json'}
    data={key:json.loads(files[name]) for key,name in parts.items()}
    result['scenarios']=[{'timing_scenario':clock,**{key:records[clock] for key,records in data.items()}}
        for clock in ('EARLY','CLOSE_BOUNDARY','LATE')]
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='operation',required=True)
    project=sub.add_parser('project');project.add_argument('--study',type=Path,required=True)
    project.add_argument('--archival-method',type=Path,required=True)
    render=sub.add_parser('report');render.add_argument('--evidence',type=Path,required=True)
    for p in (project,render):p.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    def deny(*args,**kwargs):raise AssertionError('reporting prohibits network connections')
    socket.socket.connect=socket.socket.connect_ex=socket.create_connection=deny
    if args.operation=='project':
        native,h=load_study(args.study);r=json.loads(native['research.json'])
        files={'source-evidence.json':encode({k:v for k,v in r.items() if k!='scenarios'}),
            'registration-audit.json':native['registration-audit.json'],
            'historical-method.md':args.archival_method.read_bytes(),
            'manifest.json':encode({'schema_version':'marketlife_derived_public_projection_v1',
                'native_study_sha256':h['bundle_sha256'],'native_manifest':json.loads(native['manifest.json']),
                'native_file_registry':h,'raw_full_alerts_or_provider_frames_included':False,
                'semantic_replay_requires_local_native_inputs':True})}
        parts={'ledger':'opportunity-ledger.json','candidate_references':'risk-references.json',
            'four_case_comparison':'forensic-comparison.json','underway_comparison':'underway-transitions.json'}
        for key,name in parts.items():files[name]=encode({s['timing_scenario']:s[key] for s in r['scenarios']})
    else:
        files,h=read_bundle(args.evidence)
        manifest=json.loads(files['manifest.json'])
        files=reports(research_from_projection(files),json.loads(files['registration-audit.json']),
            {'native_study':manifest['native_study_sha256'],'public_evidence':h['bundle_sha256']})
    h=write_bundle(args.output,files)
    print(json.dumps({'bundle_sha256':h['bundle_sha256'],'members':len(h['files'])}))


if __name__=='__main__':main()
