"""Project current readiness evidence or reproduce its Markdown offline."""
import argparse
import json
from pathlib import Path
import socket

from equity_research.ingestion.storage import encode,read_bundle,write_bundle
from equity_research.marketlife_readiness import load_archive,load_prediction
from equity_research.marketlife_intake import checked_acquisition
from equity_research.history.contracts import Security
from decimal import Decimal
from equity_research.marketlife_current_reports import render


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='operation',required=True)
    project=sub.add_parser('project');project.add_argument('--archive',type=Path,required=True)
    project.add_argument('--supersedes',type=Path,help='earlier immutable public evidence, retained unchanged')
    project.add_argument('--operator-context',type=Path,help='immutable operator clarification; not a completeness assertion')
    project.add_argument('--pre-audit',type=Path,required=True);project.add_argument('--prediction',type=Path)
    report=sub.add_parser('report');report.add_argument('--evidence',type=Path,required=True)
    for command in (project,report):command.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    def deny(*args,**kwargs):raise AssertionError('reporting prohibits network connections')
    socket.socket.connect=socket.socket.connect_ex=socket.create_connection=deny
    if args.operation=='report':
        files,h=read_bundle(args.evidence);files=render(files,h['bundle_sha256'])
    else:
        native,h=load_archive(args.archive);pre,preh=read_bundle(args.pre_audit)
        coverage=json.loads(native['market-coverage.json']);gate=json.loads(native['readiness.json'])
        captures=json.loads(native['market-proofs.json']);qualification=json.loads(native['qualification-attempts.json'])
        attempts=qualification.get('attempts',[]) if isinstance(qualification,dict) else qualification
        assertion=json.loads(native['source-assurance.json'])
        failures=[p for p in gate['problems'] if 'SOURCE_HISTORY' in p['code'] or 'COMPLETENESS_ASSERTION' in p['code']]
        files={'market-coverage.json':native['market-coverage.json'],'source-manifest.json':native['source-manifest.json'],
            'source-ledgers.json':native['source-ledgers.json'],'registration-audit.json':native['readiness.json'],
            'contract-identities.json':encode([{'symbol':r['symbol'],'status':r['identity_status'],'contract':r['contract']} for r in coverage['instruments']]),
            'pre-acquisition-audit.json':pre['coverage-audit.json'],
            'access-status.json':encode({'acquisition_status':'ATTEMPTS_RETAINED' if captures or attempts else 'NOT_ATTEMPTED_CURRENT_PAPER_CONFIGURATION_UNCONFIRMED',
                'reason':'See retained native status/error diagnostics.' if captures or attempts else 'Current paper-authenticated local TWS with socket clients and Read-Only API has not been confirmed for PR9D; previous confirmation was non-paper 7496.',
                'qualification_attempts':attempts,'daily_capture_statuses':[{'symbol':p['security']['symbol'],
                    'capture_sha256':p['hashes']['bundle_sha256'],'status':json.loads(p['files']['acquisition.json'])['status'],
                    'errors':json.loads(p['files']['acquisition.json'])['errors']} for p in captures],
                'broker_orders_positions_balances_executions_requested':False}),
            'source-completeness.json':encode({'status':'FAIL' if failures else 'OPERATOR_ATTESTED',
                'interpretation':'No complete-through-registration assertion with matching hashes and an auditable operator statement.' if failures else 'Explicit source-manifest-bound operator completeness assertion retained in the local archive.',
                'asserted_at':assertion.get('asserted_at') if assertion else None,'failed_checks':failures,
                'independent_subscriber_feed_verification':False}),
            'forecast-status.json':encode({'status':'NOT_REGISTERED_READINESS_FAIL' if not gate['passed'] else 'NOT_REGISTERED_REQUIRES_ACTUAL_CLOCK_GATE'}),
            'manifest.json':encode({'schema_version':'marketlife_current_public_projection_v1','native_archive_sha256':h['bundle_sha256'],
                'public_evidence_directory':args.output.name,
                'native_archive_file_registry':h,'pre_acquisition_audit_sha256':preh['bundle_sha256'],
                'market_observation_end':json.loads(native['archive.json'])['market_observation_end'],
                'native_manifest':json.loads(native['manifest.json']),'large_native_frames_or_full_commentaries_published':False,
                'full_semantic_replay_requires_local_inputs':True})}
        if args.operator_context:
            context,ch=read_bundle(args.operator_context)
            files['operator-context.json']=context['context.json']
            access=json.loads(files['access-status.json'])
            access.update(operator_reported_account_mode=qualification.get('operator_reported_account_mode'),
                host=qualification.get('host'),port=qualification.get('port'),
                read_only_operator_confirmed=qualification.get('socket_and_read_only_operator_confirmed',False),
                paper_authenticated_operator_confirmed=qualification.get('paper_authenticated_operator_confirmed',False))
            acquisitions=[json.loads(p['files']['acquisition.json']) for p in captures]
            requests=[json.loads(p['files']['request.json']) for p in captures]
            access['capture_summary']={'instruments':len(captures),'selected_rows':sum(a['coverage']['rows'] for a in acquisitions),
                'native_rows':sum(a['coverage']['native_rows'] for a in acquisitions),
                'historical_requests':sum(len(a['requests']) for a in acquisitions),
                'requested_start':min(r['start'] for r in requests) if requests else None,
                'requested_end':max(r['end'] for r in requests) if requests else None}
            files['access-status.json']=encode(access)
            complete=json.loads(files['source-completeness.json'])
            if failures:complete['interpretation']='The operator supplied all material available to them; external source-history completeness remains unverified. No stronger assertion is inferred.'
            files['source-completeness.json']=encode(complete)
            parent=json.loads(native['parent-archive.json']);current=json.loads(native['archive.json']);revisions=[]
            for proof in captures:
                security=Security(**proof['security']);symbol=security.symbol
                old={r['session_date']:r for r in parent['prices'].get(symbol,[])}
                retained={r['session_date']:r for r in current['prices'].get(symbol,[])}
                replayed=checked_acquisition({k:v.encode() for k,v in proof['files'].items()},proof['hashes'],security)
                for row in replayed['rows']:
                    day=row['session_date']
                    if day not in old:continue
                    for field in ('open','high','low','close','volume'):
                        if Decimal(old[day][field])!=Decimal(row[field]):
                            revisions.append({'symbol':symbol,'session':day,'field':field,'earlier':old[day][field],
                                'fresh':row[field],'retained':retained[day][field],
                                'fresh_native_capture_sha256':proof['hashes']['bundle_sha256'],
                                'earlier_source_snapshot_sha256':old[day]['source_snapshot_sha256']})
            files['revision-audit.json']=encode({'schema_version':'marketlife_native_revision_audit_v1',
                'differences':revisions,'earlier_canonical_rows_replaced':False,'revision_conflicts_waived':False})
            m=json.loads(files['manifest.json']);m['operator_context_sha256']=ch['bundle_sha256']
            files['manifest.json']=encode(m)
        if args.prediction:
            pred,ph=load_prediction(args.prediction);payload=json.loads(pred['prediction.json'])
            if payload['current_archive_sha256']!=h['bundle_sha256']:raise ValueError('prediction/current archive mismatch')
            files['forecast-status.json']=encode({'status':'REGISTERED_UNRESOLVED','sha256':ph['bundle_sha256'],
                'registered_at':payload['registered_at'],'outcome':payload['outcome']})
            files['prediction.json']=pred['prediction.json']
        if args.supersedes:
            m=json.loads(files['manifest.json']);m['supersedes_public_projection_sha256']=read_bundle(args.supersedes)[1]['bundle_sha256']
            files['manifest.json']=encode(m)
    h=write_bundle(args.output,files)
    print(json.dumps({'bundle_sha256':h['bundle_sha256'],'members':len(h['files'])}))


if __name__=='__main__':main()
