"""Five fixed, interpretable source-decision hypotheses, not a trading simulator."""
from datetime import datetime, time, timedelta
from decimal import Decimal, ROUND_FLOOR, ROUND_CEILING
from zoneinfo import ZoneInfo

from ..models import timestamp
from ..reconstruction.admission import Evidence, value
from .inputs import clocks, validate_view

MODELS=('A_HARD_STOP','B_CLOSE_CONFIRMATION','C_NEXT_OPEN','D_BOUNDED_REVIEW','E_PRICE_STRUCTURE')
RULES={'version':'grimes_decision_hypotheses_v1','models':list(MODELS),
 'complexity_costs':dict(zip(MODELS,[0,1,2,3,3])),
 'entry_assumption':'Next eligible regular Open; positive risk to stop known then; no actual entry or reentry inferred',
 'D':'At most one discretionary review per episode, at the very next Open; retain only if Open is protective to then-known stop. A second closing violation creates an unconditional next-Open exit commitment.',
 'E':{'progress_ATR_for_underway':1.0,'favorable_close_streak':2,'structure_buffer_ATR':0.25,
      'stop_interval_halfwidth_ATR':0.25,'progress_ATR_for_tightening':0.5,
      'level_priority':['confirmed_swing_directional','sma20','prior20_directional']},
 'next_alert_horizon_sessions':5,'confidence':'LOW_HEURISTIC_NOT_A_CALIBRATED_PROBABILITY',
 'no_full_exit_at_1R':True,'selection_contamination':'Hypotheses informed by full original7-alert baseline; historical dry run is not independent out-of-sample validation'}


def event_at(event,clock):return timestamp(clock['actions'][event['source']['alert_id']])


def stop_before(trade,clock,moment):
    stop=float(trade['initial_stop'])
    for e in trade['events'][1:]:
        if e['type']=='STOP_CHANGED' and event_at(e,clock)<=timestamp(moment):stop=float(e['stop'])
    return stop


def stop_state(trade,clock,view,policy):
    if policy not in MODELS[:4]:raise ValueError('not a stop hypothesis')
    sign=1 if trade['direction']=='LONG' else -1
    opened=event_at(trade['events'][0],clock)
    eligible=next((s for s in view['calendar']['sessions'] if timestamp(s['opens_at'])>=opened),None)
    rows={r['session_date']:r for r in view['prices'].get(trade['symbol'],[])}
    result={'hypothetical_state':'ENTRY_NOT_OBSERVED','actual_execution_state':'UNKNOWN',
        'violations':[],'entry_reference_session':eligible['session_date'] if eligible else None,
        'actual_entry':None,'review_count':0,'exit_commitment':None,'first_model_exit':None,
        'no_reentry':True,'source_position_state':trade['position_state']}
    if eligible is None:return result
    pending=None;active=False;closed=False
    for session in view['calendar']['sessions']:
        day=session['session_date']
        if day<eligible['session_date']:continue
        if day>view['market_observation_end'] or timestamp(session['closes_at'])+timedelta(minutes=60)>=timestamp(view['information_cutoff']):break
        row=rows.get(day)
        if row is None:
            result['hypothetical_state']='UNRESOLVED_MISSING_REQUIRED_SESSION';result['missing_session']=day
            return result
        o,hi,lo,cl=[float(row[k]) for k in ('open','high','low','close')]
        stop=stop_before(trade,clock,session['opens_at'])
        if day==eligible['session_date']:
            if sign*(o-stop)<=0:
                result['hypothetical_state']='REJECTED_NONPROTECTIVE_OPEN_REFERENCE';return result
            active=True;result['entry_reference_price']=o
        if closed:continue
        if pending:
            kind=pending
            if kind=='COMMITTED' or sign*(o-stop)<=0:
                closed=True;active=False;result['first_model_exit']={'session':day,'boundary':'OPEN','reason':kind}
            else:
                result['review_count']+=1
            pending=None
            result['exit_commitment']=None
            if closed:continue
        gap=sign*(o-stop)<=0;touch=sign*((lo if sign==1 else hi)-stop)<=0
        violation=sign*(cl-stop)<=0
        if touch:
            result['violations'].append({'session':day,'known_stop_at_open':stop,'open_gap':gap,
                'classification':'OPEN_GAP_BEYOND_STOP' if gap else 'INTRADAY_CLOSE_BEYOND_STOP' if violation else 'INTRADAY_TOUCH_RECOVERED',
                'close_beyond_stop':violation,'close':cl,'high':hi,'low':lo})
        if policy=='A_HARD_STOP' and touch:
            closed=True;active=False;result['first_model_exit']={'session':day,'boundary':'OPEN' if gap else 'INTRADAY_UNORDERED','reason':'PROTECTIVE_STOP'}
        elif policy=='B_CLOSE_CONFIRMATION' and violation:
            closed=True;active=False;result['first_model_exit']={'session':day,'boundary':'CLOSE_IDEALIZED','reason':'CLOSE_VIOLATION'}
        elif policy in {'C_NEXT_OPEN','D_BOUNDED_REVIEW'} and violation:
            pending='REVIEW' if policy=='D_BOUNDED_REVIEW' and result['review_count']==0 else 'COMMITTED'
            following=next((s for s in view['calendar']['sessions'] if timestamp(s['opens_at'])>timestamp(session['closes_at'])),None)
            result['exit_commitment']={'kind':pending,'trigger_session':day,'next_open':following['opens_at'] if following else None,
                                       'may_be_cancelled_by_revision_alone':False}
    result['hypothetical_state']='CLOSED_NO_REENTRY' if closed else ('PENDING_REVIEW' if pending=='REVIEW' else 'COMMITTED_NEXT_OPEN_EXIT' if pending else 'ACTIVE' if active else 'ENTRY_NOT_OBSERVED')
    return result


def structure(trade,clock,view,evidence):
    symbol=trade['symbol'];sign=1 if trade['direction']=='LONG' else -1
    cutoff=view['information_cutoff'];end,features=evidence.features(symbol,cutoff)
    opened=clock['actions'][trade['events'][0]['source']['alert_id']]
    anchor_day,anchor=evidence.features(symbol,opened)
    close,atr=value(features,'close'),value(features,'atr14')
    ref,ref_atr=value(anchor,'close'),value(anchor,'atr14')
    rows=evidence.rows(symbol);latest=rows.get(end)
    metrics={k:features.get(k) for k in ('close','atr14','sma20','sma50','prior20_high','prior20_low','confirmed_swing_high','confirmed_swing_low','breakout20','breakdown20')}
    out={'feature_session':end,'features':metrics,'opening_reference_session':anchor_day,'opening_reference_close':ref,
        'opening_reference_ATR':ref_atr,'actual_entry':None,'progress_is_not_R':True,
        'progress_ATR':sign*(close-ref)/ref_atr if close is not None and ref is not None and ref_atr else None,
        'stop_direction':'NO_ADJUSTMENT','stop_point':float(trade['current_stop']),'stop_interval':[float(trade['current_stop'])]*2,
        'action':'NOT_MENTIONED','reasons':[],'underway_prediction':None}
    if latest is None or close is None or not atr:
        return out|{'action':'ABSTAIN','stop_direction':'ABSTAIN','stop_point':None,'stop_interval':None,'reasons':['MISSING_FEATURES_OR_ATR']}
    session=next(s for s in view['calendar']['sessions'] if s['session_date']==end)
    after_open=timestamp(session['closes_at'])>timestamp(opened)
    if not after_open:
        out['reasons'].append('NO_POST_ALERT_COMPLETED_SESSION')
        return out
    current=float(trade['current_stop'])
    old_stop=stop_before(trade,clock,session['opens_at'])
    recovered=sign*((float(latest['low']) if sign==1 else float(latest['high']))-old_stop)<=0 and sign*(close-old_stop)>0
    if sign*(close-current)<=0:
        return out|{'action':'DROPPED','stop_direction':'ABSTAIN','stop_point':None,'stop_interval':None,'reasons':['ADVERSE_CLOSE_TO_CURRENT_REPORTED_STOP']}
    relative=evidence.panel.relative(symbol,'SPY',end,20)
    out['relative_SPY20']=relative
    sessions=[s['session_date'] for s in view['calendar']['sessions'] if s['session_date']<=end]
    tail=sessions[-3:]
    streak=len(tail)==3 and all(d in rows for d in tail) and all(sign*(float(rows[b]['close'])-float(rows[a]['close']))>0 for a,b in zip(tail,tail[1:]))
    out['two_favorable_closes']=streak
    breakout=value(features,'breakout20' if sign==1 else 'breakdown20') is True
    underway=(trade['setup_availability']=='ENTERABLE' and out['progress_ATR'] is not None and out['progress_ATR']>=1
              and (breakout or (streak and relative['value'] is not None and sign*relative['value']>0)))
    out['underway_prediction']=bool(underway)
    if underway:out['action']='UNDERWAY';out['reasons'].append('ONE_OPENING_REFERENCE_ATR_PROGRESS_AND_CONFIRMATION')
    level=None
    if recovered:
        level=float(latest['low'] if sign==1 else latest['high']);out['level_source']='LATEST_KNOWN_RECOVERY_BAR_EXTREME'
    else:
        names=('confirmed_swing_low','sma20','prior20_low') if sign==1 else ('confirmed_swing_high','sma20','prior20_high')
        for name in names:
            v=value(features,name);v=v['price'] if isinstance(v,dict) else v
            if v is not None and sign*(close-v)>0:
                level=v;out['level_source']=name;break
    if level is not None:
        candidate=Decimal(str(level-sign*.25*atr)).quantize(Decimal('.01'),rounding=ROUND_FLOOR if sign==1 else ROUND_CEILING)
        target=float(candidate);change=sign*(target-current)
        tighten=change>0 and out['progress_ATR'] is not None and out['progress_ATR']>=.5
        widen=change<0 and recovered
        if (tighten or widen) and target>0 and sign*(close-target)>0:
            out.update(stop_direction='TIGHTENING' if tighten else 'WIDENING',stop_point=target)
            # Entire interval must obey the predicted direction and be protective.
            lo,hi=max(.01,target-.25*atr),target+.25*atr
            if sign==1:
                hi=min(hi,close-.01)
                if tighten:lo=max(lo,current+.01)
                else:hi=min(hi,current-.01)
            else:
                lo=max(lo,close+.01)
                if tighten:hi=min(hi,current-.01)
                else:lo=max(lo,current+.01)
            out['stop_interval']=[round(lo,6),round(hi,6)] if lo<=hi else [target,target]
            if not underway:out['action']='CONTINUED_MANAGEMENT'
            out['reasons'].append('FIXED_STRUCTURE_LEVEL_MINUS_DIRECTIONAL_QUARTER_ATR')
    return out


def predict(view,registered_at,mode):
    if mode not in {'RETROSPECTIVE_DRY_RUN','FORWARD_REGISTERED'}:raise ValueError('explicit research mode required')
    episodes=validate_view(view);cutoff=view['information_cutoff']
    if timestamp(registered_at)<timestamp(cutoff):raise ValueError('registration precedes information cutoff')
    evidence=Evidence(view['prices'],view['coverage'],view['calendar'],cutoff)
    origin=registered_at if mode=='FORWARD_REGISTERED' else cutoff
    expected=[s for s in view['calendar']['sessions'] if timestamp(s['opens_at'])>timestamp(origin)][:5]
    if len(expected)!=5:raise ValueError('calendar must bound five future observation sessions')
    final_day=timestamp(expected[-1]['closes_at']).astimezone(ZoneInfo('America/New_York')).date()
    deadline=datetime.combine(final_day+timedelta(days=1),time(),ZoneInfo('America/New_York'))-timedelta(microseconds=1)
    predictions=[]
    for trade in episodes:
        if trade['position_state']!='OPEN':continue
        scenarios=[]
        for clock in clocks(view):
            hypotheses=[]
            for policy in MODELS[:4]:
                state=stop_state(trade,clock,view,policy)
                status=state['hypothetical_state']
                action='DROPPED' if status=='CLOSED_NO_REENTRY' else 'CONTINUATION' if status=='ACTIVE' else 'ABSTAIN'
                condition=None
                if status in {'COMMITTED_NEXT_OPEN_EXIT','PENDING_REVIEW'}:
                    commitment=state['exit_commitment']
                    condition={'next_open':commitment['next_open'],
                        'before_open_action':'CONTINUATION',
                        'after_open_action':'DROPPED' if commitment['kind']=='COMMITTED' else 'ABSTAIN',
                        'after_open_missing_evidence':'Review requires actual next Open versus stop known then; later source revision alone does not resolve it'}
                    if commitment['kind']=='COMMITTED' and commitment['next_open'] and timestamp(origin)>=timestamp(commitment['next_open']):action='DROPPED'
                hypotheses.append({'model':policy,'action':action,'conditional_publication_forecast':condition,
                    'allowed_source_categories':['CONTINUED_MANAGEMENT','UNDERWAY','NOT_MENTIONED'] if action=='CONTINUATION' else [action] if action!='ABSTAIN' else [],
                    'stop_direction':'ABSTAIN','stop_point':None,'stop_interval':None,'hypothetical_execution':state,
                    'assumption':'A hypothetical exit predicts an explicit source DROP, an unverified bridge from execution convention to newsletter reporting'})
            s=structure(trade,clock,view,evidence)
            hypotheses.append({'model':MODELS[4],**s,'allowed_source_categories':[s['action']] if s['action']!='ABSTAIN' else []})
            pairs=[]
            for i,a in enumerate(hypotheses):
                for b in hypotheses[i+1:]:
                    left,right=set(a['allowed_source_categories']),set(b['allowed_source_categories'])
                    if left and right and left.isdisjoint(right):pairs.append([a['model'],b['model']])
            scenarios.append({'timing_scenario':clock['name'],'models':hypotheses,
                'predeclared_disjoint_prediction_pairs':pairs,
                'observationally_equivalent_action_groups':[[p['model'] for p in hypotheses if p['allowed_source_categories']==q['allowed_source_categories']]
                    for i,q in enumerate(hypotheses) if q['allowed_source_categories'] and not any(p['allowed_source_categories']==q['allowed_source_categories'] for p in hypotheses[:i])]})
        stable={m:len({next(p['action'] for p in s['models'] if p['model']==m) for s in scenarios})==1 for m in MODELS}
        stop_stable={m:len({str((p['stop_direction'],p.get('stop_point'),p.get('stop_interval'))) for s in scenarios for p in s['models'] if p['model']==m})==1 for m in MODELS}
        predictions.append({'trade_id':trade['trade_id'],'symbol':trade['symbol'],
            'source_state':{k:trade[k] for k in ('direction','position_state','setup_availability','initial_stop','current_stop','opening_event_id')},
            'known_event_ids':[e['event_id'] for e in trade['events']], 'scenarios':scenarios,'action_stable_across_scenarios':stable,
            'stop_stable_across_scenarios':stop_stable,
            'confidence':RULES['confidence'],'actual_execution_state':'UNKNOWN'})
    stale=[s['session_date'] for s in view['calendar']['sessions'] if s['session_date']>view['market_observation_end'] and timestamp(s['closes_at'])+timedelta(minutes=60)<=timestamp(origin)]
    return {'schema_version':'grimes_prediction_v1','mode':mode,'registered_at':registered_at,'information_cutoff':cutoff,
        'market_observation_end':view['market_observation_end'],'known_alerts':view['alerts'],
        'target':{'kind':'FIRST_COMPLETE_SUPPLIED_ALERT','strictly_after':origin,'deadline':deadline.isoformat(),
                  'session_horizon':5,'not_mentioned_is_not_dropped':True},
        'unobserved_completed_sessions_since_market_end':stale,
        'historical_hypothesis_selection_is_out_of_sample':False,'predictions':predictions,
        'outcome':'UNRESOLVED_NO_LATER_ALERT_IMPORTED','source_status_authoritative':True,
        'timing_scenarios_are_independent_observations':False,'rules':RULES}
