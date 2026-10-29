"""Append-only offline prediction/reveal/evaluation bundles."""
from copy import deepcopy
from datetime import UTC, datetime, timedelta
import json
from pathlib import Path

from ..ingestion.storage import digest, encode, read_bundle, write_bundle
from ..lifecycle.source import reconstruct
from ..models import timestamp
from .inputs import make_view, metadata, parse_known, upper, validate_view
from .models import MODELS, RULES, predict


def implementation():
    from ..comprehension.study import implementation_identity
    root=Path(__file__).parent.parent
    return {'prediction_files':{name:digest((Path(__file__).parent/name).read_bytes()) for name in ('inputs.py','models.py','workflow.py')},
        'inherited':{name:digest((root/name).read_bytes()) for name in ('lifecycle/source.py','reconstruction/admission.py','reconstruction/timing.py')},
        'feature_dependencies':implementation_identity()}


def baseline(parent,output):
    # One explicit native semantic import. Derived views do not repeatedly replay
    # the full historical chain or expose the archive to the predictor.
    from ..grimes_forensics import load
    from ..lifecycle.study import read_inputs
    files,hashes=load(Path(parent))
    if hashes['bundle_sha256']!='3431d2d8ad5c5c8f22268022c810d3e7871c42d07af271d2c7576cb7e83310af':
        raise ValueError('merged PR20 final study required')
    prefix='parent-parent-input-pr17-parent-input-'
    inputs={k[len(prefix):]:v for k,v in files.items() if k.startswith(prefix) and k!=prefix+'hashes.json'}
    spec,alerts,prices,coverage,calendar,_=read_inputs(inputs)
    symbols=set(__import__('equity_research.lifecycle.source',fromlist=['UNIVERSE']).UNIVERSE)|{'SPY','QQQ'}
    archive={'schema_version':'grimes_prediction_archive_v1','alerts':alerts,'prices':{s:prices[s] for s in sorted(symbols)},
        'coverage':{s:coverage[s] for s in sorted(symbols)},'calendar':calendar,
        'market_observation_end':spec['end'],'source_cutoff':spec['analysis_cutoff'],
        'provenance':{'native_parent_sha256':hashes['bundle_sha256'],'native_parent_semantically_verified':True,
                      'market_availability':'ASSUMED_CLOSE_PLUS_60_MINUTES'}}
    return write_bundle(Path(output),{'archive.json':encode(archive)})


def prepare(archive,cutoff,output,count=None):
    files,hashes=read_bundle(Path(archive))
    data=json.loads(files['archive.json'])
    if data.get('schema_version')!='grimes_prediction_archive_v1':raise ValueError('unsupported history archive')
    view=make_view(data,hashes['bundle_sha256'],cutoff,count)
    validate_view(view)
    return write_bundle(Path(output),{'view.json':encode(view)})


def prediction_files(view_files,view_hashes,registered_at,mode):
    from ..comprehension.inputs import _check_hashes
    _check_hashes(view_files,view_hashes)
    if set(view_files)!={'view.json'}:raise ValueError('predictor accepts only a bounded causal view')
    result=predict(json.loads(view_files['view.json']),registered_at,mode)
    return {'prediction.json':encode(result),'rules.json':encode(RULES),
        'input-view.json':view_files['view.json'],'input-view-hashes.json':encode(view_hashes),
        'manifest.json':encode({'schema_version':'grimes_prediction_manifest_v1','implementation':implementation(),
            'mode':mode,'registered_at':registered_at,'view_sha256':view_hashes['bundle_sha256'],
            'entry_and_execution_are_hypotheses':True,'evaluation_inputs_accessed':False})}


def freeze(view,output,mode,*,now=None):
    files,hashes=read_bundle(Path(view))
    registered=(now or datetime.now(UTC)).isoformat()
    return write_bundle(Path(output),prediction_files(files,hashes,registered,mode))


def load_prediction(path):
    files,hashes=read_bundle(Path(path));manifest=json.loads(files['manifest.json'])
    expected=prediction_files({'view.json':files['input-view.json']},json.loads(files['input-view-hashes.json']),
                               manifest['registered_at'],manifest['mode'])
    if files!=expected:raise ValueError('prediction semantic output mismatch')
    return files,hashes


def _reveal_files(pred_files,pred_hashes,raw,imported_at):
    prediction=json.loads(pred_files['prediction.json']);view=json.loads(pred_files['input-view.json'])
    record=json.loads(raw)
    supplied=record['alerts'] if 'alerts' in record else [record]
    if len(supplied)!=1:raise ValueError('reveal exactly one complete subsequent alert')
    alert=deepcopy(supplied[0]);alert['source_sequence']=0
    if alert['alert_id'] in {a['alert_id'] for a in view['alerts']}:raise ValueError('cannot reveal an already-known alert')
    if timestamp(imported_at)<timestamp(prediction['registered_at']):raise ValueError('import precedes sealed prediction')
    if upper(alert)>timestamp(imported_at):raise ValueError('source availability is later than import')
    # Source order must advance even if exact publication is unresolved.
    if upper(alert)<=max(upper(a) for a in view['alerts']):raise ValueError('source alert is not subsequent to known history')
    events,excluded=parse_known({'schema_version':'grimes_alerts_v1','origin':record.get('origin','operator'),'alerts':[alert]})
    offset=len(view['events'])
    for i,e in enumerate(events):e['source_order']=offset+i
    # Reconstruct source facts independently of every hypothetical execution.
    episodes,_,_=reconstruct(view['events']+events,validate_pilot=False)
    normalized={**metadata(alert),'source_sequence':len(view['alerts'])}
    normalized['next_complete_alert_attested']=record.get('sequence_attestation',{}).get('next_complete_alert_after_registration') is True
    normalized['complete_source_chain_attested']=record.get('sequence_attestation',{}).get('complete_since_known_history') is True
    return {'original-alert.json':raw,'normalized-alert.json':encode(normalized),'events.json':encode(events),
        'source-after.json':encode(episodes),'excluded-actions.json':encode(excluded),
        'manifest.json':encode({'schema_version':'grimes_reveal_v1','prediction_sha256':pred_hashes['bundle_sha256'],
            'imported_at':imported_at,'implementation':implementation(),'prediction_was_already_sealed':True})}


def reveal(prediction,alert,output,*,now=None):
    files,hashes=load_prediction(prediction)
    return write_bundle(Path(output),_reveal_files(files,hashes,Path(alert).read_bytes(),(now or datetime.now(UTC)).isoformat()))


def load_reveal(path,pred_files,pred_hashes):
    files,hashes=read_bundle(Path(path));manifest=json.loads(files['manifest.json'])
    if manifest['prediction_sha256']!=pred_hashes['bundle_sha256']:raise ValueError('reveal belongs to another prediction')
    if files!=_reveal_files(pred_files,pred_hashes,files['original-alert.json'],manifest['imported_at']):
        raise ValueError('reveal semantic output mismatch')
    return files,hashes


def observation(events,trade):
    selected=[e for e in events if e['symbol']==trade['symbol']]
    kinds={e['type'] for e in selected}
    category=('DROPPED' if 'DROPPED' in kinds else 'UNDERWAY' if any(e.get('setup_availability')=='UNDERWAY' for e in selected)
              else 'CONTINUED_MANAGEMENT' if selected else 'NOT_MENTIONED')
    stops=[e for e in selected if e['type']=='STOP_CHANGED']
    if len(stops)>1:raise ValueError('multiple stop revisions in one source cluster require separate source clarification')
    stop=stops[0] if stops else None
    sign=1 if trade['source_state']['direction']=='LONG' else -1
    delta=sign*(float(stop['stop'])-float(stop['previous_stop'])) if stop else 0
    return {'category':category,'stop_direction':'TIGHTENING' if delta>0 else 'WIDENING' if delta<0 else 'NO_ADJUSTMENT',
        'stop':float(stop['stop']) if stop else None,'event_ids':[e['event_id'] for e in selected],
        'omission_is_not_closure':category=='NOT_MENTIONED'}


def resolve_publication_condition(p,alert):
    p=deepcopy(p);condition=p.get('conditional_publication_forecast')
    if not condition or p['action']!='ABSTAIN':return p
    moment=condition['next_open']
    if moment is None:return p
    action='ABSTAIN'
    if alert['published_at']:
        if upper(alert)<timestamp(moment):action=condition['before_open_action']
        elif timestamp(alert['published_at'])>timestamp(moment):action=condition['after_open_action']
    p['action']=action
    p['allowed_source_categories']=['CONTINUED_MANAGEMENT','UNDERWAY','NOT_MENTIONED'] if action=='CONTINUATION' else [action] if action!='ABSTAIN' else []
    return p


def evaluate_data(prediction,events,alert):
    target=prediction['target'];origin=timestamp(target['strictly_after']);deadline=timestamp(target['deadline'])
    # An unknown publication's receipt time does not prove post-registration
    # publication. Dry runs may use ordered receipt bounds, explicitly conditional.
    if prediction['mode']=='FORWARD_REGISTERED':
        if not alert['published_at']:
            eligibility='UNRESOLVED_PUBLICATION_TIME'
        else:
            lower=timestamp(alert['published_at'])
            eligibility=('ELIGIBLE' if lower>origin and upper(alert)<=deadline else
                'OUTSIDE_PREREGISTERED_WINDOW' if upper(alert)<=origin or lower>deadline else 'UNRESOLVED_WINDOW_BOUNDARY')
    else:
        eligibility='ELIGIBLE_RETROSPECTIVE_SEQUENCE' if origin<upper(alert)<=deadline else 'OUTSIDE_DRY_RUN_WINDOW'
    if prediction['mode']=='FORWARD_REGISTERED' and eligibility=='ELIGIBLE' and not (
            alert.get('next_complete_alert_attested') and alert.get('complete_source_chain_attested')):
        eligibility='UNRESOLVED_ALERT_SEQUENCE'
    rows=[]
    for trade in prediction['predictions']:
        actual=observation(events,trade)
        scenarios=[]
        for scenario in trade['scenarios']:
            outcomes=[]
            resolved=[resolve_publication_condition(p,alert) for p in scenario['models']]
            for p in resolved:
                usable=eligibility.startswith('ELIGIBLE') and bool(p['allowed_source_categories'])
                verdict='SUPPORTS_PREDICTION' if usable and actual['category'] in p['allowed_source_categories'] else 'CONTRADICTS_PREDICTION' if usable else 'UNRESOLVED_OR_ABSTAINED'
                direction_usable=eligibility.startswith('ELIGIBLE') and p['stop_direction']!='ABSTAIN'
                level_usable=bool(direction_usable and actual['stop'] is not None and p.get('stop_point') is not None)
                atr=p.get('features',{}).get('atr14',{}).get('value')
                outcomes.append({'model':p['model'],'predicted_action':p['action'],'actual_category':actual['category'],
                    'verdict':verdict,'point_category_correct':actual['category']==p['action'] if usable and len(p['allowed_source_categories'])==1 else None,
                    'set_coverage_correct':actual['category'] in p['allowed_source_categories'] if usable else None,
                    'stop_direction_correct':actual['stop_direction']==p['stop_direction'] if direction_usable else None,
                    'stop_error_ATR':abs(actual['stop']-p['stop_point'])/atr if level_usable and atr else None,
                    'stop_interval_covered':p['stop_interval'][0]<=actual['stop']<=p['stop_interval'][1] if level_usable and p['stop_interval'] else None})
            # Conditional branches use publication metadata only, never actual
            # action/category. The branch rule was sealed before revealing it.
            pairs=[[a['model'],b['model']] for i,a in enumerate(resolved) for b in resolved[i+1:]
                   if a['allowed_source_categories'] and b['allowed_source_categories']
                   and set(a['allowed_source_categories']).isdisjoint(b['allowed_source_categories'])]
            scenarios.append({'timing_scenario':scenario['timing_scenario'],'models':outcomes,
                'predeclared_disjoint_prediction_pairs':pairs,
                'distinguishing_observation':bool(pairs),
                'distinguishes_protective_conventions':any('E_PRICE_STRUCTURE' not in pair for pair in pairs)})
        rows.append({'symbol':trade['symbol'],'trade_id':trade['trade_id'],'actual_source_observation':actual,'scenarios':scenarios})
    summaries=[]
    for timing in ('EARLY','CLOSE_BOUNDARY','LATE'):
        stats={}
        for model in MODELS:
            selected=[(s,next(p for p in s['models'] if p['model']==model)) for r in rows for s in r['scenarios'] if s['timing_scenario']==timing]
            points=[p['point_category_correct'] for _,p in selected if p['point_category_correct'] is not None]
            dirs=[p['stop_direction_correct'] for _,p in selected if p['stop_direction_correct'] is not None]
            errors=[p['stop_error_ATR'] for _,p in selected if p['stop_error_ATR'] is not None]
            intervals=[p['stop_interval_covered'] for _,p in selected if p['stop_interval_covered'] is not None]
            change_dirs=[p['stop_direction_correct'] for r in rows if r['actual_source_observation']['stop'] is not None
                for s in r['scenarios'] if s['timing_scenario']==timing for p in s['models'] if p['model']==model and p['stop_direction_correct'] is not None]
            stats[model]={'episodes':len(rows),'point_category_correct':sum(points),'point_category_denominator':len(points),
                'set_coverage_correct':sum(p['set_coverage_correct'] is True for _,p in selected),
                'set_coverage_denominator':sum(p['set_coverage_correct'] is not None for _,p in selected),
                'stop_direction_correct':sum(dirs),'stop_direction_denominator':len(dirs),
                'changed_stop_direction_correct':sum(change_dirs),'changed_stop_direction_denominator':len(change_dirs),
                'stop_error_ATR_sum':sum(errors),'stop_level_denominator':len(errors),
                'stop_interval_hits':sum(intervals),'stop_interval_denominator':len(intervals),
                'distinguishing_wins':sum(any(model in pair for pair in s['predeclared_disjoint_prediction_pairs']) and p['verdict']=='SUPPORTS_PREDICTION' for s,p in selected),
                'distinguishing_losses':sum(any(model in pair for pair in s['predeclared_disjoint_prediction_pairs']) and p['verdict']=='CONTRADICTS_PREDICTION' for s,p in selected),
                'abstentions_or_unresolved':sum(p['verdict']=='UNRESOLVED_OR_ABSTAINED' for _,p in selected)}
            wins,losses=stats[model]['distinguishing_wins'],stats[model]['distinguishing_losses']
            stats[model]['distinguishing_cluster_outcome']='MIXED' if wins and losses else 'SUPPORTED_ONLY' if wins else 'CONTRADICTED_ONLY' if losses else 'NO_DISTINGUISHING_RESULT'
        summaries.append({'timing_scenario':timing,'shared_alert_clusters':1,'models':stats,
            'cluster_outcome':{m:'HAS_CONTRADICTION' if any(p['model']==m and p['verdict']=='CONTRADICTS_PREDICTION' for r in rows for s in r['scenarios'] if s['timing_scenario']==timing for p in s['models'])
                else 'NO_EVALUABLE_FORECAST' if all(p['model']!=m or p['verdict']=='UNRESOLVED_OR_ABSTAINED' for r in rows for s in r['scenarios'] if s['timing_scenario']==timing for p in s['models']) else 'NO_CONTRADICTION_OBSERVED' for m in MODELS}})
    return {'schema_version':'grimes_prediction_evaluation_v1','mode':prediction['mode'],'eligibility':eligibility,
        'information_cutoff':prediction['information_cutoff'],'registered_at':prediction['registered_at'],
        'actual_alert':alert,'source_observations':rows,'summaries':summaries,
        'source_ledger_rewritten':False,'each_alert_is_one_shared_cluster':True,'fresh_out_of_sample':prediction['mode']=='FORWARD_REGISTERED' and eligibility=='ELIGIBLE'}


def evaluation_files(pred_files,pred_hashes,reveal_files,reveal_hashes):
    manifest=json.loads(reveal_files['manifest.json'])
    if manifest['prediction_sha256']!=pred_hashes['bundle_sha256']:raise ValueError('evaluation prediction/reveal mismatch')
    result=evaluate_data(json.loads(pred_files['prediction.json']),json.loads(reveal_files['events.json']),json.loads(reveal_files['normalized-alert.json']))
    return {'evaluation.json':encode(result),'manifest.json':encode({'schema_version':'grimes_evaluation_manifest_v1',
        'prediction_sha256':pred_hashes['bundle_sha256'],'reveal_sha256':reveal_hashes['bundle_sha256'],'implementation':implementation()}),
        'prediction-hashes.json':encode(pred_hashes),'reveal-hashes.json':encode(reveal_hashes)}


def evaluate(prediction,reveal_path,output):
    p,ph=load_prediction(prediction);r,rh=load_reveal(reveal_path,p,ph)
    return write_bundle(Path(output),evaluation_files(p,ph,r,rh))


def replay_evaluation(study,prediction,reveal_path,output):
    existing,hashes=read_bundle(Path(study));p,ph=load_prediction(prediction);r,rh=load_reveal(reveal_path,p,ph)
    expected=evaluation_files(p,ph,r,rh)
    if existing!=expected:raise ValueError('evaluation semantic output mismatch')
    return write_bundle(Path(output),expected)


def advance(archive,prediction,reveal_path,output,market=None,calendar=None):
    files,hashes=read_bundle(Path(archive));data=json.loads(files['archive.json'])
    p,ph=load_prediction(prediction);view=json.loads(p['input-view.json']);r,rh=load_reveal(reveal_path,p,ph)
    if view['archive_sha256']!=hashes['bundle_sha256'] or len(view['alerts'])!=len(data['alerts']['alerts']):
        raise ValueError('advance requires the latest complete archive prefix')
    raw=json.loads(r['original-alert.json']);a=(raw['alerts'] if 'alerts' in raw else [raw])[0]
    a=deepcopy(a);a['source_sequence']=len(data['alerts']['alerts']);a.setdefault('html','')
    data['alerts']['alerts'].append(a);data['source_cutoff']=upper(a).isoformat()
    if calendar:
        from ..ingestion.calendar import schedule
        supplied=json.loads(Path(calendar).read_bytes())
        if supplied!=schedule(supplied['start'],supplied['end']):raise ValueError('noncanonical extended calendar')
        if supplied['start']!=data['calendar']['start'] or supplied['end']<data['calendar']['end']:
            raise ValueError('extended calendar must preserve the existing historical schedule')
        data['calendar']=supplied
    if market:
        update=json.loads(Path(market).read_bytes())
        if update.get('schema_version')!='grimes_market_update_v1' or not update.get('source_reference') or not update.get('native_bundle_sha256'):
            raise ValueError('supplied canonical update requires explicit native provenance')
        if set(update['prices'])-set(data['prices']):raise ValueError('market update expands the fixed cohort')
        for symbol,rows in update['prices'].items():
            by_day={v['session_date']:v for v in data['prices'][symbol]}
            for row in rows:
                day=row['session_date']
                if day in by_day and by_day[day]!=row:raise ValueError('cannot overwrite an existing frozen market observation')
                by_day[day]=row
            data['prices'][symbol]=[by_day[d] for d in sorted(by_day)]
        if update['market_observation_end']<data['market_observation_end']:raise ValueError('market coverage cannot move backward')
        data['market_observation_end']=update['market_observation_end']
        data['provenance']['market_update']={k:update[k] for k in ('source_reference','native_bundle_sha256')}|{'native_proof_independently_replayed':False,'status':'OPERATOR_SUPPLIED_CANONICAL_UPDATE'}
    events,_=parse_known(data['alerts']);reconstruct(events,validate_pilot=False)
    data['provenance']['parent_archive_sha256']=hashes['bundle_sha256'];data['provenance']['reveal_sha256']=rh['bundle_sha256']
    # Existing price/identity validation is also used on the next bounded view.
    return write_bundle(Path(output),{'archive.json':encode(data)})
