"""The original six source transitions: retrospective, never fresh validation."""
from datetime import UTC,datetime,timedelta
import json
import os
from pathlib import Path
import subprocess
import sys

from ..ingestion.storage import encode,read_bundle,write_bundle
from ..models import timestamp
from .inputs import make_view, upper
from .models import MODELS
from . import workflow as w


def summary(cases):
    result=[]
    for timing in ('EARLY','CLOSE_BOUNDARY','LATE'):
        models={}
        for model in MODELS:
            stats=[next(s for s in c['evaluation']['summaries'] if s['timing_scenario']==timing)['models'][model] for c in cases]
            numeric=[k for k,v in stats[0].items() if isinstance(v,(int,float))]
            totals={k:sum(s[k] for s in stats) for k in numeric}
            totals['mean_absolute_stop_error_ATR']=totals['stop_error_ATR_sum']/totals['stop_level_denominator'] if totals['stop_level_denominator'] else None
            totals['shared_cluster_outcomes']={cat:sum(next(s for s in c['evaluation']['summaries'] if s['timing_scenario']==timing)['cluster_outcome'][model]==cat for c in cases)
                for cat in ('HAS_CONTRADICTION','NO_EVALUABLE_FORECAST','NO_CONTRADICTION_OBSERVED')}
            totals['distinguishing_cluster_outcomes']={cat:sum(s['distinguishing_cluster_outcome']==cat for s in stats)
                for cat in ('SUPPORTED_ONLY','CONTRADICTED_ONLY','MIXED','NO_DISTINGUISHING_RESULT')}
            models[model]=totals
        result.append({'timing_scenario':timing,'shared_alert_cluster_count':len(cases),'models':models})
    return {'schema_version':'grimes_walk_forward_v1','mode':'RETROSPECTIVE_DRY_RUN',
        'fresh_out_of_sample_observations':0,'hypotheses_informed_by_all_original_alerts':True,
        'cases':cases,'summaries':result,
        'cutoff_design':'For dated target alerts use last completed cash Close+61minutes before target publication, after the prior source availability bound. For unknown weekly publication use the previous source upper bound; no Friday bars are admitted to that forecast.',
        'cutoff_design_uses_historical_publication_metadata':True,
        'prediction_process_inputs':'Bounded view only; no archive or target path passed to predictor subprocess'}


def case_cutoff(data,i):
    previous=upper(data['alerts']['alerts'][i-1])
    target=data['alerts']['alerts'][i]
    if target['published_at']:
        candidates=[timestamp(s['closes_at'])+timedelta(minutes=61) for s in data['calendar']['sessions']
            if previous<=timestamp(s['closes_at'])+timedelta(minutes=61)<timestamp(target['published_at'])]
        if candidates:return candidates[-1]
    return previous


def dry_run(archive,output):
    data_files,ah=read_bundle(Path(archive));data=json.loads(data_files['archive.json'])
    root=Path(output);root.mkdir(parents=True,exist_ok=False)
    cases=[]
    alerts=data['alerts']['alerts']
    for i in range(1,len(alerts)):
        cutoff=case_cutoff(data,i)
        folder=root/f'case-{i:02d}';folder.mkdir()
        w.prepare(archive,cutoff.isoformat(),folder/'view',i)
        # Separate process receives only the frozen prefix view, not the archive
        # that the trusted experiment preparer uses to release later labels.
        script=Path(__file__).resolve().parents[3]/'scripts/grimes_predictions.py'
        task_env=dict(os.environ)
        task_env['PYTHONPATH']=str(script.parent.parent/'src')+(os.pathsep+task_env['PYTHONPATH'] if task_env.get('PYTHONPATH') else '')
        subprocess.run([sys.executable,str(script),'predict','--view',str(folder/'view'),
            '--mode','RETROSPECTIVE_DRY_RUN','--output',str(folder/'prediction')],check=True,capture_output=True,text=True,env=task_env)
        pf,ph=read_bundle(folder/'prediction') # Must exist/seal before target read.
        raw=folder/'authorized-later-alert.json'
        with raw.open('xb') as h:h.write(encode({'schema_version':'grimes_alerts_v1','origin':data['alerts']['origin'],'alerts':[alerts[i]]}))
        rh=w.reveal(folder/'prediction',raw,folder/'reveal')
        eh=w.evaluate(folder/'prediction',folder/'reveal',folder/'evaluation')
        ev=json.loads(read_bundle(folder/'evaluation')[0]['evaluation.json'])
        cases.append({'case_id':folder.name,'cutoff':cutoff.isoformat(),'known_alert_count':i,
            'prediction_sha256':ph['bundle_sha256'],'reveal_sha256':rh['bundle_sha256'],'evaluation_sha256':eh['bundle_sha256'],
            'prediction':json.loads(pf['prediction.json']),'evaluation':ev})
    result=summary(cases)
    return write_bundle(root/'study',{'walk-forward.json':encode(result),'archive.json':data_files['archive.json'],
        'archive-hashes.json':encode(ah),'manifest.json':encode({
        'archive_sha256':ah['bundle_sha256'],'implementation':w.implementation(),'experiment_implementation_sha256':__import__('hashlib').sha256(Path(__file__).read_bytes()).hexdigest(),
        'prediction_sealed_before_target_release':True,'case_directories':len(cases)})})


def replay_experiment(study,output):
    root=Path(study);files,hashes=read_bundle(root/'study')
    saved=json.loads(files['walk-forward.json']);cases=[]
    from ..comprehension.inputs import _check_hashes
    archive_hashes=json.loads(files['archive-hashes.json'])
    _check_hashes({'archive.json':files['archive.json']},archive_hashes)
    archive=json.loads(files['archive.json'])
    if len(saved['cases'])!=len(archive['alerts']['alerts'])-1:raise ValueError('walk-forward case inventory mismatch')
    dest=Path(output);dest.mkdir(parents=True,exist_ok=False)
    for i,case in enumerate(saved['cases'],1):
        if case['case_id']!=f'case-{i:02d}':raise ValueError('unsafe or nonsequential case identity')
        folder=root/case['case_id']
        p,ph=w.load_prediction(folder/'prediction')
        cutoff=case_cutoff(archive,i).isoformat()
        if case['cutoff']!=cutoff or case['known_alert_count']!=i:
            raise ValueError('walk-forward cutoff/prefix metadata mismatch')
        if p['input-view.json']!=encode(make_view(archive,archive_hashes['bundle_sha256'],cutoff,i)):
            raise ValueError('walk-forward view differs from declared archive prefix')
        # Replay seals each already-derived prediction before evaluating labels.
        target=dest/case['case_id'];target.mkdir()
        write_bundle(target/'prediction',p)
        r,rh=w.load_reveal(folder/'reveal',p,ph)
        expected_raw=encode({'schema_version':'grimes_alerts_v1','origin':archive['alerts']['origin'],'alerts':[archive['alerts']['alerts'][i]]})
        if r['original-alert.json']!=expected_raw:raise ValueError('walk-forward target differs from source sequence')
        evaluated=w.replay_evaluation(folder/'evaluation',folder/'prediction',folder/'reveal',target/'evaluation')
        if ph['bundle_sha256']!=case['prediction_sha256'] or rh['bundle_sha256']!=case['reveal_sha256'] or evaluated['bundle_sha256']!=case['evaluation_sha256']:
            raise ValueError('walk-forward component hash mismatch')
        rebuilt={**case,'prediction':json.loads(p['prediction.json']),
            'evaluation':json.loads(read_bundle(target/'evaluation')[0]['evaluation.json'])}
        cases.append(rebuilt)
    if encode(summary(cases))!=files['walk-forward.json']:raise ValueError('walk-forward semantic output mismatch')
    manifest=json.loads(files['manifest.json'])
    if (manifest['archive_sha256']!=archive_hashes['bundle_sha256'] or manifest['case_directories']!=len(cases)
            or manifest['implementation']!=w.implementation() or manifest['experiment_implementation_sha256']!=__import__('hashlib').sha256(Path(__file__).read_bytes()).hexdigest()):raise ValueError('walk-forward implementation mismatch')
    return write_bundle(dest/'study',files)
