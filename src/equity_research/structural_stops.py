"""PR9E: stop-masked structural annotations and descriptive residuals, offline."""
from collections import Counter,defaultdict
from copy import deepcopy
from decimal import Decimal
import csv
import io
import json
from pathlib import Path
from statistics import median

from .ingestion.storage import digest,encode,read_bundle,write_bundle
from .marketlife_intake import source_state
from .marketlife_readiness import load_archive,batches_from_proofs
from .reconstruction.admission import Evidence,value
from .models import timestamp
from datetime import timedelta

PROTOCOL={'schema_version':'structural_stop_protocol_v1','chart_sessions':60,'minimum_chart_sessions':20,
    'pivot_left_right':3,'pullback_origin_sessions':20,'range_sessions':10,'breakout_prior_sessions':20,
    'signal_search_sessions':20,'research_tick':'0.01','verified_contract_min_tick':False,
    'candidate_selection_uses_published_stops':False,'buffers_fitted':False,'residual_match_threshold':None,
    'primary_aggregate_clock':'LATE','expert_setup_family':'UNKNOWN','actual_executions':'UNKNOWN'}


def identity():
    root=Path(__file__).parent
    from .marketlife_workflow import identity as inherited
    return {**inherited(),**{n:digest((root/n).read_bytes()) for n in
        ('structural_stops.py','marketlife_intake.py','marketlife_readiness.py')}}


def inventory(state):
    """One source event, once; clocks are fields rather than duplicate decisions."""
    raw={e['event_id']:e for e in state['events']};meta={a['alert_id']:a for a in state['metadata']}
    decisions=[]
    for setup in state['ledgers'][-1]['setups']:
        for event in setup['events']:
            kind=event['legacy_source_type']
            if kind not in {'OPEN_NEW_POSITION','STOP_CHANGED'}:continue
            e=raw[event['source_event_id']];aid=event['source_alert_id']
            final=next(a for a in state['ledgers'][-1]['assessments'] if a['setup_id']==setup['setup_id'] and a['source_alert_id']==aid)
            decisions.append({'decision_id':e['event_id'],'setup_id':setup['setup_id'],'symbol':setup['symbol'],
                'direction':setup['direction'],'source_alert_id':aid,'source_order':e['source_order'],
                'decision_type':'INITIAL' if kind=='OPEN_NEW_POSITION' else 'REVISION',
                'revision_role':None if kind=='OPEN_NEW_POSITION' else 'MONITORED_UNDERWAY' if event['entry_state_before']=='UNDERWAY' else 'ENTERABLE_REVISION',
                'eligibility_before':event['entry_state_before'],'atomic_assessment_eligibility':final['entry_state'],
                'copublished_underway':event['entry_state_before']=='ENTERABLE' and final['entry_state']=='UNDERWAY',
                'published_stop':event['published_stop'],'previous_stop':e.get('previous_stop'),
                'source_text':event['source_text'],'source_text_sha256':meta[aid]['text_sha256'],
                'observed_publication':meta[aid].get('published_at') or 'UNKNOWN',
                'publication_display':meta[aid]['original_publication_display'],
                'publication':meta[aid],'cutoffs':{c['name']:c['actions'][aid] for c in state['clocks']},
                'expert_setup_family':'UNKNOWN','observed_execution':'UNKNOWN'})
    return sorted(decisions,key=lambda d:d['source_order'])


def prepare(path):
    f,h=load_archive(path);a=json.loads(f['archive.json']);b=batches_from_proofs(json.loads(f['source-proofs.json']))
    state=source_state(a,b,json.loads(f['manifest.json'])['asof']);decisions=inventory(state)
    symbols=sorted({d['symbol'] for d in decisions}|{'SPY','QQQ'})
    coverage={s:{k:v for k,v in a['coverage'][s].items() if k in
        {'security','contract','price_basis','volume_basis','origin','source_bundle_sha256'}} for s in symbols if s in a['coverage']}
    market={'schema_version':'structural_market_inputs_v1','calendar':a['calendar'],'coverage':coverage,
        'prices':{s:a['prices'][s] for s in symbols if s in a['prices']},
        'decisions':[{k:d[k] for k in ('decision_id','symbol','direction','cutoffs')} for d in decisions]}
    source={'original_alerts':a['alerts'],'batches':b,'calendar':a['calendar'],
        'source_asof':json.loads(f['manifest.json'])['asof'],'native_archive_sha256':h['bundle_sha256']}
    from .marketlife_intake import checked_acquisition
    from .history.contracts import Security
    vintages=[]
    for proof in json.loads(f['market-proofs.json']):
        result=checked_acquisition({k:v.encode() for k,v in proof['files'].items()},proof['hashes'],Security(**proof['security']))
        symbol=proof['security']['symbol'];retained={r['session_date']:r for r in market['prices'].get(symbol,[])}
        for row in result['rows']:
            old=retained.get(row['session_date'])
            fields=[k for k in ('open','high','low','close','volume') if old and Decimal(old[k])!=Decimal(row[k])]
            if fields:vintages.append({'symbol':symbol,'session':row['session_date'],'changed_fields':fields,
                'retained':old,'fresh':row,'fresh_capture_sha256':proof['hashes']['bundle_sha256']})
    return {'market.json':encode(market),'source.json':encode(source),'protocol.json':encode(PROTOCOL),
        'vintages.json':encode(vintages),
        'provenance.json':encode({'parent_sha256':h['bundle_sha256'],'parent_file_registry':h,
            'parent_native_semantically_verified_at_export':True,'subsequent_replay_scope':'exported inputs and study semantics',
            'native_price_vintage':'RETAINED_PARENT; later capture does not prove historical dissemination'})}


def pivots(rows):
    result=[]
    for i in range(3,len(rows)-3):
        for kind,field in (('HIGH','high'),('LOW','low')):
            neighbors=rows[i-3:i]+rows[i+1:i+4];v=float(rows[i][field])
            if all(v>float(r[field]) if kind=='HIGH' else v<float(r[field]) for r in neighbors):
                result.append({'kind':kind,'session':rows[i]['session_date'],'confirmed_session':rows[i+3]['session_date'],'level':rows[i][field]})
    return result


def structures(rows,direction):
    """Only admitted bars and direction enter this function; no source stop input."""
    ps=pivots(rows);sign=1 if direction=='LONG' else -1;opposite='low' if sign==1 else 'high'
    swings=[p for p in ps if p['kind']==('LOW' if sign==1 else 'HIGH')]
    h1={'family':'H1','level':swings[-1]['level'] if swings else None,'anchor_session':swings[-1]['session'] if swings else None,
        'confirmation_session':swings[-1]['confirmed_session'] if swings else None,
        'reason':'Most recent strict 3-left/3-right directional swing; significance is a hypothesis, not selected by stop proximity.',
        'expected_invalidation':'A renewed breach of the selected swing challenges support/resistance; reclaim remains an alternative.'}
    h2={'family':'H2','level':None,'anchor_session':None,
        'reason':'Opposite extreme after the latest favorable extreme in the last 20 bars; requires two subsequent bars and an adverse Close move.',
        'expected_invalidation':'A breach of the current retracement extreme challenges the proposed pullback thesis.'}
    recent=rows[-20:]
    favorable='high' if sign==1 else 'low'
    peak=max(range(len(recent)),key=lambda i:(sign*float(recent[i][favorable]),i)) if recent else None
    if peak is not None and len(recent)-peak-1>=2:
        after=recent[peak+1:]
        adverse=any(sign*(float(b['close'])-float(a['close']))<0 for a,b in zip(recent[peak:],recent[peak+1:]))
        if adverse and sign*(float(rows[-1]['close'])-float(recent[peak][favorable]))<0:
            low=min(range(len(after)),key=lambda i:(sign*float(after[i][opposite]),-i))
            h2.update(level=after[low][opposite],anchor_session=after[low]['session_date'],origin_session=recent[peak]['session_date'],
                confirmation_session=rows[-1]['session_date'],provisional_not_a_confirmed_pivot=True)
    h3={'family':'H3','level':None,'anchor_session':None,'reason':'Fixed last-10-bar boundary; a descriptive range proxy, not proof of consolidation.',
        'expected_invalidation':'A breach would leave this bounded range; whether it was the relevant trading range is unidentified.'}
    if len(rows)>=10:
        box=rows[-10:];idx=min(range(10),key=lambda i:(sign*float(box[i][opposite]),-i))
        path=sum(abs(float(b['close'])-float(a['close'])) for a,b in zip(box,box[1:]))
        h3.update(level=box[idx][opposite],anchor_session=box[idx]['session_date'],confirmation_session=rows[-1]['session_date'],
            range_start=box[0]['session_date'],range_end=box[-1]['session_date'],
            close_path_efficiency=abs(float(box[-1]['close'])-float(box[0]['close']))/path if path else 0,
            range_low=min(float(r['low']) for r in box),range_high=max(float(r['high']) for r in box))
    signals=[]
    for i in range(max(20,len(rows)-20),len(rows)):
        prior=rows[i-20:i]
        for side,field,op in (('LONG','high',max),('SHORT','low',min)):
            level=op(float(r[field]) for r in prior)
            if (1 if side=='LONG' else -1)*(float(rows[i]['close'])-level)>0:
                signals.append({'direction':side,'session':rows[i]['session_date'],'prior_boundary':level,
                    'level':rows[i]['low' if side=='LONG' else 'high']})
    selected=[s for s in signals if s['direction']==direction]
    h4={'family':'H4','level':selected[-1]['level'] if selected else None,'anchor_session':selected[-1]['session'] if selected else None,
        'confirmation_session':selected[-1]['session'] if selected else None,
        'reason':'Opposite extreme of the latest directional Close beyond the previous 20 bars, searched only in the last 20 available bars.',
        'expected_invalidation':'Loss of the signal-bar extreme challenges immediate continuation; older signals may no longer govern the setup.'}
    h5={'family':'H5','level':None,'anchor_session':None,'reason':'Volatility-only alternative has no identified entry, multiplier or structural anchor; no stop is manufactured.',
        'expected_invalidation':'Requires an independently specified volatility rule on another case; unconstrained alternatives cannot be falsified here.'}
    return {'candidates':[h1,h2,h3,h4,h5],'pivots':ps,'signals':signals,
        'observable_family_proxy':'BREAKOUT_PROXY' if selected and selected[-1]['session']==rows[-1]['session_date'] else
            'PULLBACK_PROXY' if h2['level'] is not None else 'UNKNOWN',
        'expert_setup_family':'UNKNOWN'}


def chart_view(market,symbol,direction,cutoff):
    cal=market['calendar'];eligible=[s['session_date'] for s in cal['sessions'] if timestamp(s['closes_at'])+timedelta(minutes=60)<timestamp(cutoff)]
    dates=eligible[-60:];expected=dates[-1] if dates else None
    selected={s:[r for r in market['prices'].get(s,[]) if r['session_date'] in dates] for s in (symbol,'SPY','QQQ') if s in market['coverage']}
    rows=selected.get(symbol,[]);observed=[r['session_date'] for r in rows]
    if len(set(observed))!=len(observed) or observed!=sorted(observed):raise ValueError('duplicate or nonchronological chart observations')
    required=[d for d in dates if observed and d>=observed[0]]
    gaps=[d for d in required if d not in observed]
    status='AVAILABLE' if len(rows)==60 else 'AVAILABLE_SHORT_HISTORY'
    if not rows:status='UNAVAILABLE_NO_MARKET_EVIDENCE'
    elif gaps:status='UNAVAILABLE_MISSING_REQUIRED_SESSION'
    elif len(rows)<20:status='UNAVAILABLE_FEWER_THAN_20_BARS'
    evidence=Evidence(selected,{s:market['coverage'][s] for s in selected},cal,cutoff)
    features=evidence.features(symbol,cutoff)[1] if rows else {}
    context={s:{k:value(evidence.features(s,cutoff)[1],k) for k in ('close','atr14','return5','return20','close_sma20','close_sma50')}
        if s in selected else {'status':'UNAVAILABLE'} for s in ('SPY','QQQ')}
    annotations=structures(rows,direction) if status.startswith('AVAILABLE') else {'candidates':[], 'pivots':[],'signals':[],
        'observable_family_proxy':'UNKNOWN','expert_setup_family':'UNKNOWN'}
    return {'symbol':symbol,'direction':direction,'expected_session':expected,'chart_sessions':dates,'rows':rows,
        'status':status,'missing_sessions':gaps,'available_bars':len(rows),'prefix_unavailable_sessions':[d for d in dates if not observed or d<observed[0]],
        'features':{k:features.get(k,{'value':None,'status':'UNAVAILABLE'}) for k in ('close','atr14','sma20','sma50','return5','return20','realized_volatility20','range_contraction10_previous20')},
        'market_context':context,**annotations}


def annotate(market):
    views=[]
    for d in market['decisions']:
        if set(d)!={'decision_id','symbol','direction','cutoffs'}:raise ValueError('only stop-masked decision identities/clocks admitted')
        groups={}
        for clock,cutoff in d['cutoffs'].items():
            view=chart_view(market,d['symbol'],d['direction'],cutoff)
            token=digest(encode(view))
            if token not in groups:groups[token]={**view,'view_id':f"v{len(views)+len(groups):03d}",'decision_id':d['decision_id'],'scenarios':{},'published_stop_visible':False}
            groups[token]['scenarios'][clock]=cutoff
        views.extend(groups.values())
    return {'schema_version':'structural_annotations_v1','protocol':PROTOCOL,'views':views,
        'masking':'Programmatic stop masking only; historical cases were known to the analyst. Not a genuinely blind or held-out study.'}


def compare(annotations,decisions):
    by_id={d['decision_id']:d for d in decisions};matrix=[];views=[]
    for view in annotations['views']:
        d=by_id[view['decision_id']];stop=Decimal(d['published_stop']);sign=1 if d['direction']=='LONG' else -1
        atr=value(view['features'],'atr14');close=value(view['features'],'close')
        cs=view['candidates'] or [{'family':f'H{i}','level':None,'anchor_session':None,'reason':view['status'],'expected_invalidation':'UNKNOWN'} for i in range(1,6)]
        surviving=[]
        for c in cs:
            level=Decimal(str(c['level'])) if c['level'] is not None else None
            beyond=sign*(level-stop) if level is not None else None
            side=sign*(Decimal(str(close))-level)>0 if close is not None and level is not None else None
            breaches=[r['session_date'] for r in view['rows'] if level is not None and c.get('confirmation_session')
                and r['session_date']>c['confirmation_session']
                and sign*(Decimal(r['low' if sign==1 else 'high'])-level)<0]
            status='UNKNOWN' if level is None else 'RANGE_PROXY_ONLY' if c['family']=='H3' else 'STOP_INSIDE_ANCHOR' if beyond<0 else 'ANCHOR_NOT_PROTECTIVE_TO_CLOSE' if not side else 'GEOMETRICALLY_COMPATIBLE'
            if status=='GEOMETRICALLY_COMPATIBLE':surviving.append(c['family'])
            matrix.append({'decision_id':d['decision_id'],'view_id':view['view_id'],'symbol':d['symbol'],'direction':d['direction'],
                'decision_type':d['decision_type'],'revision_role':d['revision_role'],'eligibility_before':d['eligibility_before'],
                'scenarios':list(view['scenarios']),'expected_session':view['expected_session'],'data_status':view['status'],
                'observable_family_proxy':view['observable_family_proxy'],'expert_setup_family':'UNKNOWN',**c,
                'published_stop':str(stop),'previous_stop':d['previous_stop'],'buffer_price':str(beyond) if beyond is not None else None,
                'buffer_research_ticks':str(beyond/Decimal(PROTOCOL['research_tick'])) if beyond is not None else None,
                'buffer_ATR':float(beyond)/atr if beyond is not None and atr else None,
                'absolute_residual_ATR':abs(float(beyond)/atr) if beyond is not None and atr else None,
                'observable_at_assumed_cutoff':level is not None and view['status'].startswith('AVAILABLE'),
                'boundary_relation':'UNKNOWN' if beyond is None else 'BEYOND' if beyond>0 else 'AT' if beyond==0 else 'INSIDE',
                'predecision_anchor_breaches':breaches,
                'atr14':atr,'atr_session':view['expected_session'],'current_close_reference':close,
                'close_reference_risk_ATR':sign*(float(close)-float(stop))/atr if close is not None and atr else None,
                'verdict':status,'support':'Observable candidate with published stop on/beyond its boundary; geometry is not identification.' if status=='GEOMETRICALLY_COMPATIBLE' else 'No independent support assigned.',
                'contradiction':'Published stop lies inside the candidate boundary.' if status=='STOP_INSIDE_ANCHOR' else
                    'The candidate is not protective to the current Close; entry/timeframe remain unknown.' if status=='ANCHOR_NOT_PROTECTIVE_TO_CLOSE' else
                    'A fixed box is not evidence of consolidation.' if status=='RANGE_PROXY_ONLY' else
                    'Anchor/market evidence is unidentified.' if status=='UNKNOWN' else
                    f'Anchor was already breached after confirmation on {breaches}; recovery or a different thesis is needed.' if breaches else
                    'Unknown buffer and discretionary significance remain; proximity alone cannot validate the mechanism.'})
        views.append({'decision_id':d['decision_id'],'view_id':view['view_id'],'scenarios':list(view['scenarios']),
            'status':view['status'],'geometrically_compatible_families':surviving,
            'resolution':'UNAVAILABLE' if not view['status'].startswith('AVAILABLE') else 'UNKNOWN' if not surviving else
                'MULTIPLE_CANDIDATES' if len(surviving)>1 else 'SINGLE_GEOMETRIC_PROXY_NOT_IDENTIFIED'})
    for d in decisions:
        dv=[v for v in views if v['decision_id']==d['decision_id']]
        d['timing_sensitive']=len(dv)>1
        d['view_ids']=[v['view_id'] for v in dv]
    revisions=[];previous={}
    for d in decisions:
        prior=previous.get(d['setup_id']);previous[d['setup_id']]=d
        if prior is None:continue
        for clock in ('EARLY','CLOSE_BOUNDARY','LATE'):
            for h in ('H1','H2','H3','H4','H5'):
                old=next(r for r in matrix if r['decision_id']==prior['decision_id'] and clock in r['scenarios'] and r['family']==h)
                new=next(r for r in matrix if r['decision_id']==d['decision_id'] and clock in r['scenarios'] and r['family']==h)
                revisions.append({'decision_id':d['decision_id'],'previous_decision_id':prior['decision_id'],
                    'symbol':d['symbol'],'direction':d['direction'],'scenario':clock,'family':h,
                    'old_stop':prior['published_stop'],'new_stop':d['published_stop'],
                    'stop_change':str(Decimal(d['published_stop'])-Decimal(prior['published_stop'])),
                    'old_anchor_session':old['anchor_session'],'new_anchor_session':new['anchor_session'],
                    'old_level':old['level'],'new_level':new['level'],
                    'level_change':float(new['level'])-float(old['level']) if old['level'] is not None and new['level'] is not None else None,
                    'anchor_changed':(old['anchor_session'],old['level'])!=(new['anchor_session'],new['level']),
                    'old_expected_session':old['expected_session'],'new_expected_session':new['expected_session'],
                    'old_data_status':old['data_status'],'new_data_status':new['data_status'],
                    'revision_role':d['revision_role'],'atomic_assessment_eligibility':d['atomic_assessment_eligibility'],
                    'copublished_underway':d['copublished_underway'],
                    'interpretation':'Reported setup assessment; no observed execution or order modification established.'})
    return {'schema_version':'structural_stop_study_v1','inventory':decisions,'matrix':matrix,'revision_comparisons':revisions,
        'view_verdicts':views,'protocol':PROTOCOL}


def csv_bytes(rows):
    keys=list(dict.fromkeys(k for r in rows for k in r));stream=io.StringIO(newline='')
    writer=csv.DictWriter(stream,fieldnames=keys,lineterminator='\n');writer.writeheader()
    writer.writerows({k:json.dumps(v,sort_keys=True) if isinstance(v,(list,dict)) else v for k,v in r.items()} for r in rows)
    return stream.getvalue().encode()


def summarize(result):
    inventory=result['inventory'];matrix=result['matrix'];out={}
    for clock in ('EARLY','CLOSE_BOUNDARY','LATE'):
        rows=[r for r in matrix if clock in r['scenarios']];verdicts=[r for r in result['view_verdicts'] if clock in r['scenarios']]
        families={}
        for h in ('H1','H2','H3','H4','H5'):
            subset=[r for r in rows if r['family']==h];dist=[r['absolute_residual_ATR'] for r in subset if r['absolute_residual_ATR'] is not None]
            families[h]={'candidate_available':sum(r['level'] is not None for r in subset),
                'verdicts':dict(Counter(r['verdict'] for r in subset)),
                'boundary_relations':dict(Counter(r['boundary_relation'] for r in subset)),
                'median_absolute_residual_ATR':median(dist) if dist else None,
                'min_absolute_residual_ATR':min(dist) if dist else None,'max_absolute_residual_ATR':max(dist) if dist else None}
        strata=[]
        for column in ('direction','decision_type','revision_role','eligibility_before','observable_family_proxy'):
            keys=sorted({str(d.get(column)) for d in rows})
            for key in keys:
                rs=[r for r in rows if str(r.get(column))==key]
                strata.append({'dimension':column,'value':key,'decisions':len(rs)//5,
                    'families':{h:dict(Counter(r['verdict'] for r in rs if r['family']==h)) for h in families}})
        out[clock]={'decisions':len(verdicts),'availability':dict(Counter(v['status'] for v in verdicts)),
            'resolution':dict(Counter(v['resolution'] for v in verdicts)),'families':families,'strata':strata}
    return {'distinct_setup_episodes':len({d['setup_id'] for d in inventory}),'distinct_decisions':len(inventory),
        'initial_stops':sum(d['decision_type']=='INITIAL' for d in inventory),'revisions':sum(d['decision_type']=='REVISION' for d in inventory),
        'monitored_underway_revisions':sum(d['revision_role']=='MONITORED_UNDERWAY' for d in inventory),
        'copublished_underway':sum(d['copublished_underway'] for d in inventory),
        'source_alert_clusters':len({d['source_alert_id'] for d in inventory}),'timing_sensitive_decisions':sum(d['timing_sensitive'] for d in inventory),
        'unique_chart_views':len(result['view_verdicts']),'clocks':out,'inference':'Descriptive fixed proxies only; no closest-residual winner, optimized buffer or identified expert rule.'}


def source_inventory(source):
    a={'alerts':source['original_alerts'],'calendar':source['calendar']}
    return inventory(source_state(a,source['batches'],source['source_asof']))


def study_files(annotation_files,annotation_hashes,source_bytes):
    from .comprehension.inputs import _check_hashes
    _check_hashes(annotation_files,annotation_hashes)
    market=json.loads(annotation_files['market.json']);expected=annotation_files_for(market)
    if expected!=annotation_files:raise ValueError('structural annotation semantic mismatch')
    decisions=source_inventory(json.loads(source_bytes))
    stubs=[{k:d[k] for k in ('decision_id','symbol','direction','cutoffs')} for d in decisions]
    if market['decisions']!=stubs:raise ValueError('market decision identities/clocks disagree with source')
    result=compare(json.loads(annotation_files['annotations.json']),decisions)
    return {**annotation_files,'source.json':source_bytes,'annotation-hashes.json':encode(annotation_hashes),
        'inventory.csv':csv_bytes(result['inventory']),'matrix.csv':csv_bytes(result['matrix']),
        'revision-comparisons.csv':csv_bytes(result['revision_comparisons']),
        'study.json':encode(result),'summary.json':encode(summarize(result)),
        'study-manifest.json':encode({'schema_version':'structural_study_manifest_v1','annotation_sha256':annotation_hashes['bundle_sha256'],
            'source_sha256':digest(source_bytes),'implementation':identity()})}


def annotation_files_for(market):
    return {'market.json':encode(market),'annotations.json':encode(annotate(market)),
        'annotation-manifest.json':encode({'schema_version':'masked_structural_annotations_v1','implementation':identity(),
            'published_stops_received':False,'protocol':PROTOCOL})}


def load_study(path):
    files,hashes=read_bundle(Path(path));a={k:files[k] for k in ('market.json','annotations.json','annotation-manifest.json')}
    expected=study_files(a,json.loads(files['annotation-hashes.json']),files['source.json'])
    if files!=expected:raise ValueError('structural study semantic replay mismatch')
    return files,hashes


def materiality(files,vintages_bytes):
    """Derived alternative to assess known revisions, never overwrite the retained parent."""
    market=json.loads(files['market.json']);vintages=json.loads(vintages_bytes)
    alternate=deepcopy(market)
    for v in vintages:
        rows=alternate['prices'][v['symbol']]
        i=next(i for i,r in enumerate(rows) if r['session_date']==v['session'])
        if rows[i]!=v['retained']:raise ValueError('retained vintage mismatch')
        rows[i]=v['fresh']
    result=compare(annotate(alternate),source_inventory(json.loads(files['source.json'])))
    baseline=json.loads(files['study.json']);changed=[]
    fields=('level','anchor_session','confirmation_session','atr14','buffer_ATR','boundary_relation','verdict','data_status')
    lookup={(r['decision_id'],clock,r['family']):r for r in result['matrix'] for clock in r['scenarios']}
    for r in baseline['matrix']:
        for clock in r['scenarios']:
            alt=lookup[(r['decision_id'],clock,r['family'])]
            differences={k:{'retained':r.get(k),'fresh':alt.get(k)} for k in fields if r.get(k)!=alt.get(k)}
            if differences:changed.append({'decision_id':r['decision_id'],'symbol':r['symbol'],
                'family':r['family'],'scenario':clock,'differences':differences})
    return {'vintages.json':vintages_bytes,'materiality.json':encode({'schema_version':'structural_vintage_materiality_v1',
        'study_sha256':digest(files['study.json']),'vintage_count':len(vintages),'changed_comparisons':changed,
        'changed_verdicts':sum('verdict' in r['differences'] for r in changed),
        'changed_anchors':sum('level' in r['differences'] or 'anchor_session' in r['differences'] for r in changed),
        'alternate_is_not_canonical':True,'forecast_gate_changed':False})}
