"""Reconciled, pattern-conditioned initial-stop study; offline and immutable."""
from collections import Counter
from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path
from statistics import median

from .comprehension.inputs import _check_hashes
from .ingestion.storage import digest, encode, read_bundle
from .initial_stop_log import reconcile
from .initial_pattern_candidates import FAMILIES, PROTOCOL, missing, pattern_candidates
from .initial_stops import stubs, identity as inherited_identity
from .structural_stops import chart_view, csv_bytes
from .reconstruction.admission import value


def identity():
    root = Path(__file__).parent
    return {**inherited_identity(), **{name: digest((root/name).read_bytes()) for name in
        ('initial_stop_log.py', 'initial_pattern_candidates.py', 'initial_pattern_study.py')}}


def proof(path):
    files, hashes = read_bundle(path)
    return {'files': {k: v.decode() for k,v in files.items()}, 'hashes': hashes}


def inventory(source):
    result = reconcile(source)
    rows = result['inventory']
    if source.get('original_cohort_only'): rows = [d for d in rows if d['cohort'] == 'PR9E_INITIAL_34']
    return rows


def prepare(parent_path, expected_sha256, observation_path, earlier_path, guidance_path, original_only=False):
    files, h = read_bundle(parent_path)
    if h['bundle_sha256'] != expected_sha256: raise ValueError('declared frozen parent hash differs')
    source = {'parent_source': json.loads(files['source.json']), 'expanded_log_proof': proof(observation_path),
        'earlier_observation_proof': proof(earlier_path), 'risk_guidance_proof': proof(guidance_path),
        'original_cohort_only': original_only}
    market = json.loads(files['market.json']); market['decisions'] = stubs(inventory(source))
    return {'market.json': encode(market), 'source.json': encode(source), 'protocol.json': encode(PROTOCOL),
        'provenance.json': encode({'parent': h, 'native_archive_sha256': source['parent_source']['native_archive_sha256'],
            'expanded_source_sha256': source['expanded_log_proof']['hashes']['bundle_sha256'],
            'previous_drafts_preserved': True, 'original_cohort_only': original_only})}


def annotate(market):
    views = []; seen = set()
    for d in market['decisions']:
        if set(d) != {'decision_id','setup_id','symbol','direction','decision_type','cutoffs'} or d['decision_type'] != 'INITIAL':
            raise ValueError('only stop-masked initial decisions admitted')
        if d['setup_id'] in seen: raise ValueError('duplicate opening episode')
        seen.add(d['setup_id']); groups = {}
        for clock, cutoff in d['cutoffs'].items():
            v = chart_view(market, d['symbol'], d['direction'], cutoff)
            v['candidates'] = pattern_candidates(v['rows'], d['direction']) if v['status'].startswith('AVAILABLE') else [missing(f,v['status']) for f in FAMILIES]
            v['price_pattern_proxy'] = v.pop('observable_family_proxy')
            v['features'] = {k:v['features'][k] for k in ('close','atr14')}
            key = digest(encode(v))
            if key not in groups:
                groups[key] = {**v, 'view_id': f"p{len(views)+len(groups):03d}", 'decision_id': d['decision_id'], 'scenarios': {}}
            groups[key]['scenarios'][clock] = cutoff
        views.extend(groups.values())
    return {'schema_version':'initial_pattern_annotations_v3', 'protocol':PROTOCOL, 'views':views,
        'masking':'Programmatic only; historical failures informed these revised hypotheses, so not genuinely blind or held out.'}


def compare(annotations, decisions):
    if any(d['decision_type'] != 'INITIAL' for d in decisions): raise ValueError('only initial stops permitted')
    by_id = {d['decision_id']:d for d in decisions}; matrix = []; observations = []
    for v in annotations['views']:
        d = by_id[v['decision_id']]; stop = Decimal(d['published_stop']); sign = 1 if d['direction']=='LONG' else -1
        atr = value(v['features'],'atr14'); close = value(v['features'],'close')
        for c in v['candidates']:
            level = Decimal(str(c['level'])) if c['level'] is not None else None
            room = sign*(level-stop) if level is not None else None
            protective = level is not None and close is not None and sign*(Decimal(str(close))-level)>0
            tests = [r['session_date'] for r in v['rows'] if level is not None and c.get('confirmation_session')
                and r['session_date']>c['confirmation_session'] and sign*(Decimal(r['low' if sign==1 else 'high'])-level)<0]
            geometry = room is not None and room>=0 and protective
            test_state = 'UNKNOWN' if level is None else 'UNTESTED_AFTER_CONFIRMATION' if not tests else 'TESTED_AND_RECLAIMED' if protective else 'TESTED_WITHOUT_CURRENT_RECLAIM'
            against = []
            if room is not None and room<0: against.append('Stop is inside this proposed boundary; another scale or invalidation thesis is needed.')
            if tests: against.append('Untouched-boundary version contradicted before publication; reclaim or deeper protection remains a separate interpretation.')
            if c.get('common_price_overlap') is False: against.append('Contracting daily ranges have no common price region; nesting/consolidation is not established.')
            if level is not None and not protective: against.append('Boundary is not protective relative to the available Close; Close is not an assumed entry.')
            if c.get('established_trend'): against.append(c['established_trend'])
            matrix.append({'decision_id':d['decision_id'],'setup_id':d['setup_id'],'symbol':d['symbol'],'direction':d['direction'],
                'decision_type':'INITIAL','cohort':d['cohort'],'marketlife_type':d['marketlife_type'],
                'view_id':v['view_id'],'scenarios':list(v['scenarios']),'expected_session':v['expected_session'],'data_status':v['status'],
                **c,'published_initial_stop':str(stop),'buffer_price':str(room) if room is not None else None,
                'buffer_ATR14':float(room)/atr if room is not None and atr else None,
                'buffer_research_ticks':str(room/Decimal('.01')) if room is not None else None,
                'research_tick_not_verified_min_tick':True,'atr14_normalization':atr,
                'boundary_relation':'UNKNOWN' if room is None else 'BEYOND' if room>0 else 'AT' if room==0 else 'INSIDE',
                'weak_geometry':geometry,'current_close_reference':close,'candidate_protective_to_close':protective,
                'anchor_breaches_after_confirmation':tests,'prior_test_state':test_state,
                'pattern_relevance':'PROPOSED; not identified expert intent' if level is not None else 'UNKNOWN',
                'protective_room_rationale':'UNKNOWN; extra room may accommodate volatility or another scale, but is not established by distance alone.',
                'supporting_observations':c['reason'],'contradictory_observations':against,
                'latent_assumptions':['Expert-selected timeframe and pattern significance','Expected future volatility','Intended entry and protective-stop convention','Native adjustment compatibility'],
                'alternative_explanation':'Another structural scale, reclaim thesis, discretionary protection, or volatility construction; do not select by minimum residual.',
                'discriminating_observation':'Another case with separated local and larger boundaries and a published rationale, frozen before observing its stop.',
                'expert_intent':'UNKNOWN','actual_entry_risk':'UNKNOWN'})
        rows = [r for r in matrix if r['view_id']==v['view_id']]
        observations.append({'decision_id':d['decision_id'],'setup_id':d['setup_id'],'symbol':d['symbol'],
            'cohort':d['cohort'],'marketlife_type':d['marketlife_type'],'view_id':v['view_id'],
            'scenarios':list(v['scenarios']),'status':v['status'],
            'geometric_families':sorted({r['family'] for r in rows if r['weak_geometry']}),
            'untested_geometric_families':sorted({r['family'] for r in rows if r['weak_geometry'] and not r['anchor_breaches_after_confirmation'] and r.get('common_price_overlap') is not False}),
            'expert_rationale':'UNKNOWN; correspondence is not identification'})
    return {'schema_version':'initial_pattern_study_v3','inventory':decisions,'matrix':matrix,
        'view_observations':observations,'protocol':PROTOCOL}


def summary(study):
    clocks = {}
    for clock in ('EARLY','CLOSE_BOUNDARY','LATE'):
        views = [v for v in study['view_observations'] if clock in v['scenarios']]
        rows = [r for r in study['matrix'] if clock in r['scenarios']]
        groups = []
        for dimension, names in [('ALL',['ALL']),('direction',['LONG','SHORT']),
                ('cohort',sorted({d['cohort'] for d in study['inventory']})),
                ('marketlife_type',sorted({d['marketlife_type'] for d in study['inventory']}))]:
            for name in names:
                rs = rows if dimension=='ALL' else [r for r in rows if r[dimension]==name]
                families = {}
                for f in FAMILIES:
                    fs = [r for r in rs if r['family']==f]; primary = [r for r in fs if r['primary']]
                    distances = [abs(r['buffer_ATR14']) for r in primary if r['buffer_ATR14'] is not None]
                    families[f] = {'primary_candidate_available':sum(r['level'] is not None for r in primary),
                        'primary_geometry':sum(r['weak_geometry'] for r in primary),
                        'any_candidate_geometry_decisions':len({r['decision_id'] for r in fs if r['weak_geometry']}),
                        'primary_inside_boundary':sum(r['boundary_relation']=='INSIDE' for r in primary),
                        'primary_tested_before_decision':sum(bool(r['anchor_breaches_after_confirmation']) for r in primary),
                        'primary_median_absolute_distance_ATR14_all_available':median(distances) if distances else None}
                groups.append({'dimension':dimension,'value':name,'decisions':len({r['decision_id'] for r in rs}),'families':families})
        clocks[clock] = {'decisions':len(views),'availability':dict(Counter(v['status'] for v in views)),
            'no_geometric_candidate':sum(not v['geometric_families'] for v in views),
            'multiple_geometric_families':sum(len(v['geometric_families'])>1 for v in views),'groups':groups}
    return {'initial_decisions':len(study['inventory']),'directions':dict(Counter(d['direction'] for d in study['inventory'])),
        'cohorts':dict(Counter(d['cohort'] for d in study['inventory'])),
        'source_types':dict(Counter(d['marketlife_type'] for d in study['inventory'])),
        'chart_views':len(study['view_observations']),'candidate_rows':len(study['matrix']),
        'clocks':clocks,'identified_private_rationales':0,'subsequent_stop_rules_studied':False}


def risk_band(number):
    if number is None: return 'UNKNOWN'
    x = Decimal(str(number))
    return 'BELOW_0_8' if x<Decimal('.8') else '0_8_THROUGH_1_4' if x<=Decimal('1.4') else 'ABOVE_1_4_THROUGH_2' if x<=2 else 'ABOVE_2'


def risk_context(source, market, reconciliation):
    earlier = source['earlier_observation_proof']; f = {k:v.encode() for k,v in earlier['files'].items()}; _check_hashes(f,earlier['hashes'])
    given = json.loads(f['observation.json'])['dashboard_observations']
    g = source['risk_guidance_proof']; gf = {k:v.encode() for k,v in g['files'].items()}; _check_hashes(gf,g['hashes'])
    rows = []
    for record in given:
        d = next(d for d in reconciliation['inventory'] if d['symbol']==record['symbol'] and d['cohort']=='PR9E_INITIAL_34')
        triggers = [e for e in reconciliation['events'] if e.get('setup_id')==d['setup_id'] and e['kind']=='TRIGGERED']
        trigger_day = triggers[0]['log_date'] if len(triggers)==1 else None
        open_at = next((s['opens_at'] for s in market['calendar']['sessions'] if s['session_date']==trigger_day),None)
        v = chart_view(market,d['symbol'],d['direction'],open_at) if open_at else None
        atr = value(v['features'],'atr14') if v and v['status'].startswith('AVAILABLE') else None
        entry = Decimal(record['source_reported_entry_reference']); stop = Decimal(d['published_stop'])
        signed = (entry-stop) if d['direction']=='LONG' else (stop-entry)
        hypothetical = float(signed)/atr if signed>0 and atr else None
        rows.append({**record,'setup_id':d['setup_id'],'initial_published_stop':d['published_stop'],
            'published_TO_STOP':None,'initial_decision_entry_reference':None,'structural_entry_reference':None,
            'entry_reference_observed_at_initial_decision':False,'actual_subscriber_execution':'UNKNOWN',
            'retrospective_reference_to_first_stop_distance':str(signed),'source_trigger_log_date':trigger_day,
            'entry_decision_time':'UNKNOWN','valid_fully_timed_entry_risk_observation':False,
            'initial_risk_ATR14':'UNKNOWN','observed_risk_band':'UNKNOWN',
            'conditional_scenario':'If the later AHE reference describes entry during the reported trigger session, use only the prior completed daily ATR. Not a verified entry.',
            'conditional_ATR_session':v['expected_session'] if v else None,'conditional_ATR14':atr,
            'conditional_reference_risk_ATR14':hypothetical,'conditional_band':risk_band(hypothetical),
            'current_stop_not_used_as_initial':True,'LAST_used_as_entry':False,
            'price_basis_compatibility':'UNVERIFIED; native split-adjusted bars and reported entry may differ.'})
    return {'guidance':json.loads(gf['guidance.json']),'fully_timed_valid_observations':0,
        'triggered_log_rows':sum(e['kind']=='TRIGGERED' for e in reconciliation['events']),
        'trigger_rows_supply_entry_price':False,'observations':rows,'bands_used_to_select_candidates':False}


def annotation_files(market):
    return {'market.json':encode(market),'annotations.json':encode(annotate(market)),
        'annotation-manifest.json':encode({'implementation':identity(),'protocol':PROTOCOL,'published_stops_received':False})}


def study_files(af, ah, source_bytes):
    _check_hashes(af,ah); market = json.loads(af['market.json']); source = json.loads(source_bytes)
    if af != annotation_files(market): raise ValueError('pattern annotation semantic mismatch')
    decisions = inventory(source)
    if market['decisions'] != stubs(decisions): raise ValueError('reconciled initial identities/clocks differ')
    r = reconcile(source); study = compare(json.loads(af['annotations.json']),decisions)
    a = json.loads(af['annotations.json']); augmented = deepcopy(decisions)
    for d in augmented:
        vs = [v for v in a['views'] if v['decision_id']==d['decision_id']]
        d.update(decision_time_ATR14={clock:value(v['features'],'atr14') for v in vs for clock in v['scenarios']},
            published_TO_STOP=None,structural_entry_reference=None,initial_risk_status='UNKNOWN_ENTRY')
    return {**af,'source.json':source_bytes,'annotation-hashes.json':encode(ah),'study.json':encode(study),
        'inventory.csv':csv_bytes(augmented),'matrix.csv':csv_bytes(study['matrix']),
        'initial-observations.csv':csv_bytes([{'decision_id':d['decision_id'],'setup_id':d['setup_id'],
            'symbol':d['symbol'],'direction':d['direction'],'cohort':d['cohort'],'marketlife_type':d['marketlife_type'],
            'conditional_views':[v for v in study['view_observations'] if v['decision_id']==d['decision_id']],
            'identified_explanation':'UNKNOWN'} for d in decisions]),
        'compression.csv':csv_bytes([x for x in study['matrix'] if x['family']=='COMPRESSION']),
        'reconciliation.json':encode(r),'source-events.csv':csv_bytes(r['events']),
        'setup-family-evidence.csv':csv_bytes([{'setup_id':d['setup_id'],'symbol':d['symbol'],'direction':d['direction'],
            'observed_TYPE':d['marketlife_type'],'opening_log_date':d['reported_log_date'],
            'observation_source':'NEW_SETUP row in supplied historical log' if d['marketlife_type']!='UNKNOWN' else 'No episode-specific TYPE supplied',
            'snapshot_publication':'2026-11-02 5pm, user-reported; historical original alert payload unverified',
            'type_inferred_by_algorithm':False,'later_dashboard_type_backfilled':False,
            'historical_applicability':'Log attributes TYPE to NEW SETUP; original per-alert timing not independently verified.'} for d in decisions]),
        'risk-context.json':encode(risk_context(source,market,r)),'summary.json':encode(summary(study)),
        'manifest.json':encode({'implementation':identity(),'protocol':PROTOCOL,'source_sha256':digest(source_bytes),
            'annotation_sha256':ah['bundle_sha256'],'replay_scope':'Frozen source/price projections and semantic outputs, not original historical dissemination.'})}


def load_study(path):
    files,h = read_bundle(path); af = {k:files[k] for k in ('market.json','annotations.json','annotation-manifest.json')}
    if files != study_files(af,json.loads(files['annotation-hashes.json']),files['source.json']):
        raise ValueError('pattern study semantic replay mismatch')
    return files,h


def public_evidence(files,h,inputs,ih):
    if any(files[k]!=inputs[k] for k in ('market.json','source.json')): raise ValueError('inputs differ from study')
    a = json.loads(files['annotations.json'])
    for v in a['views']: v['rows_sha256'] = digest(encode(v.pop('rows')))
    names = ('inventory.csv','matrix.csv','initial-observations.csv','compression.csv','reconciliation.json',
        'source-events.csv','setup-family-evidence.csv','risk-context.json','summary.json')
    return {**{n:files[n] for n in names},'annotations-without-bars.json':encode(a),'protocol.json':inputs['protocol.json'],
        'provenance.json':inputs['provenance.json'],'lineage.json':encode({'study':h,'inputs':ih,'native_rows_committed':False})}
