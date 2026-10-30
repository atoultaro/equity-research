"""Bounded descriptive opportunity/extension research; no executed trades inferred."""
from collections import Counter
from copy import deepcopy
from datetime import timedelta
from statistics import mean

from .models import timestamp
from .reconstruction.admission import Evidence,value,risk_geometry
from .prospective.models import stop_state
from .marketlife_setups import opportunity_ledger,source_inputs,timing_scenarios

FEATURES=('close','atr14','sma20','sma50','confirmed_swing_high','confirmed_swing_low',
          'prior20_high','prior20_low','realized_volatility20','range_contraction10_previous20')


def snapshot(evidence,symbol,at,stop,direction):
    if symbol not in evidence.prices:
        return {'status':'UNAVAILABLE_NO_MARKET_IDENTITY_OR_DATA','feature_session':None,'features':{},'observed_execution':'UNKNOWN'}
    day,features=evidence.features(symbol,at)
    out={'feature_session':day,'features':{k:features.get(k) for k in FEATURES},'observed_execution':'UNKNOWN',
         'decision_cutoff':at,'price_basis':'INHERITED_CONDITIONAL_NATIVE_SPLIT_ADJUSTED','reference_is_execution':False}
    close,atr=value(features,'close'),value(features,'atr14')
    out['status']='AVAILABLE' if close is not None and atr else 'UNAVAILABLE_REQUIRED_COMPLETED_PRICE_OR_ATR'
    window,dates,reason=evidence.panel.window(symbol,day,10) if day else (None,[],None)
    sma10=mean(r['close'] for r in window) if window else None
    out['sma10']={'value':sma10,'status':'AVAILABLE' if window else 'UNAVAILABLE','sessions':dates,'reason':reason}
    sign=1 if direction=='LONG' else -1
    out.update(published_stop=stop,entry_to_stop_distance=sign*(close-float(stop)) if close is not None else None,
        entry_to_stop_ATR=sign*(close-float(stop))/atr if close is not None and atr else None,
        close_reference=close,atr14=atr,
        directional_SMA10_extension_pct=100*sign*(close/sma10-1) if close is not None and sma10 else None,
        directional_SMA20_extension_pct=100*sign*(close/value(features,'sma20')-1) if close is not None and value(features,'sma20') else None,
        relative_SPY20=evidence.panel.relative(symbol,'SPY',day,20) if day and 'SPY' in evidence.prices else None)
    out['swing_distances_ATR']={k:sign*(close-(v['price'] if isinstance(v,dict) else v))/atr if close is not None and atr and v is not None else None
        for k in ('confirmed_swing_high','confirmed_swing_low','prior20_high','prior20_low') for v in [value(features,k)]}
    return out


def candidate(op,evidence,calendar,market_end):
    snap=snapshot(evidence,op['symbol'],op['effective_from'],op['published_stop'],op['direction'])
    out={'opportunity_id':op['opportunity_id'],'decision_snapshot':snap,'candidate_is_source_opportunity':False,
         'observed_execution':'UNKNOWN','current_close_is_not_a_retroactive_fill':True,'next_open':None}
    if not op['entry_eligible']:
        return out|{'status':'NO_NONEMPTY_ELIGIBLE_INTERVAL'}
    session=next((s for s in calendar['sessions'] if timestamp(s['opens_at'])>timestamp(op['effective_from'])),None)
    if session is None:return out|{'status':'NO_CALENDAR_BOUND'}
    out['next_open']={'session':session['session_date'],'at':session['opens_at'],'observation_scope':'POST_DECISION_REFERENCE_NOT_A_KNOWN_FILL'}
    if op['effective_until'] and timestamp(session['opens_at'])>=timestamp(op['effective_until']):
        return out|{'status':'SUPERSEDED_OR_SUSPENDED_BEFORE_CANDIDATE_OPEN'}
    row=next((r for r in evidence.prices.get(op['symbol'],[]) if r['session_date']==session['session_date']),None)
    if session['session_date']>market_end or row is None:return out|{'status':'NEXT_OPEN_UNOBSERVED'}
    _,entry_features=evidence.features(op['symbol'],session['opens_at'])
    entry_atr=value(entry_features,'atr14');price=float(row['open'])
    geometry=risk_geometry(op['direction'],price,op['published_stop'],entry_atr)
    out['next_open'].update(price=price,published_stop=op['published_stop'],pre_entry_ATR14=entry_atr,geometry=geometry,
        distance_ATR_at_opportunity_decision=geometry['reference_risk']/snap['atr14'] if snap.get('atr14') else None)
    return out|{'status':'CAUSALLY_FEASIBLE_REFERENCE' if geometry['reference_risk']>0 else 'NONPROTECTIVE_REFERENCE_REJECTED'}


def subscriber_path(op,construction,evidence,calendar,market_end,policy):
    if policy not in {'HARD','CLOSE'}:raise ValueError('bounded policy required')
    out={'opportunity_id':op['opportunity_id'],'policy':policy,'published_stop_fixed':op['published_stop'],
         'observed_execution':'UNKNOWN','actual_entry':None,'actual_exit':None,
         'source_suspension_or_drop_does_not_liquidate_subscriber':True,'state':'NO_COMPARABLE_REFERENCE'}
    if construction['status']!='CAUSALLY_FEASIBLE_REFERENCE':return out
    sign=1 if op['direction']=='LONG' else -1;stop=float(op['published_stop'])
    rows=evidence.rows(op['symbol']);start=construction['next_open']['session']
    out['state']='HYPOTHETICALLY_REMAINS_PROTECTED_AT_DATA_END'
    for s in calendar['sessions']:
        day=s['session_date']
        if day<start:continue
        if day>market_end:break
        if day not in rows:return out|{'state':'UNRESOLVED_MISSING_REQUIRED_SESSION','missing_session':day}
        row=rows[day]
        price=float(row['close']) if policy=='CLOSE' else float(row['low' if sign==1 else 'high'])
        if sign*(price-stop)<=0:
            return out|{'state':'HYPOTHETICAL_STOP_CONDITION','first_stop_session':day,
                'boundary':'CLOSE_IDEALIZED_NOT_A_GUARANTEED_FILL' if policy=='CLOSE' else 'OPEN_GAP' if sign*(float(row['open'])-stop)<=0 else 'INTRADAY_ORDER_UNKNOWN'}
    return out


def extension(evidence,setup,op,at,last_assessment,stop):
    current=snapshot(evidence,setup['symbol'],at,stop,setup['direction'])
    sign=1 if setup['direction']=='LONG' else -1
    refs={}
    starts={'ADDED_CLOSE':setup['events'][0]['assumed_at'],
            'LATEST_ELIGIBLE_OPPORTUNITY_CLOSE':op['effective_from'] if op else None,
            'LAST_ENTERABLE_ASSESSMENT_CLOSE':last_assessment['assumed_at'] if last_assessment else None}
    for name,moment in starts.items():
        anchor=snapshot(evidence,setup['symbol'],moment,stop,setup['direction']) if moment else {}
        a,atr=anchor.get('close_reference'),anchor.get('atr14');c=current.get('close_reference')
        refs[name]={'anchor_cutoff':moment,'anchor_session':anchor.get('feature_session'),'price':a,'anchor_ATR14':atr,
            'advance_anchor_ATR':sign*(c-a)/atr if c is not None and a is not None and atr else None,
            'advance_current_ATR':sign*(c-a)/current['atr14'] if c is not None and a is not None and current.get('atr14') else None}
    first=next((s for s in evidence.calendar['sessions'] if timestamp(s['opens_at'])>timestamp(setup['events'][0]['assumed_at'])),None)
    row=next((r for r in evidence.prices.get(setup['symbol'],[]) if first and r['session_date']==first['session_date']),None)
    first_observed=bool(first and row and timestamp(first['closes_at'])+timedelta(minutes=60)<timestamp(at))
    _,f=evidence.features(setup['symbol'],first['opens_at']) if first and setup['symbol'] in evidence.prices else (None,{})
    atr=value(f,'atr14');c=current.get('close_reference');price=float(row['open']) if first_observed else None
    refs['FIRST_OPPORTUNITY_OPEN']={'anchor_session':first['session_date'] if first else None,'price':price,'anchor_ATR14':atr if first_observed else None,
        'advance_anchor_ATR':sign*(c-price)/atr if c is not None and price is not None and atr else None,
        'actual_entry':None,'admitted_only_after_daily_bar_completion':True}
    last=refs['LAST_ENTERABLE_ASSESSMENT_CLOSE'];end=current.get('feature_session');start=last['anchor_session']
    moved=bool(current['status']=='AVAILABLE' and start and end and end>start)
    days=[s['session_date'] for s in evidence.calendar['sessions'] if start and end and start<=s['session_date']<=end]
    rows=evidence.rows(setup['symbol']) if setup['symbol'] in evidence.prices else {}
    favorable=sum(sign*(float(rows[b]['close'])-float(rows[a]['close']))>0 for a,b in zip(days,days[1:])) if moved and all(d in rows for d in days) else None
    return {'current_snapshot':current,'references':refs,'new_completed_daily_observation_since_last_enterable':moved,
        'favorable_sessions_since_last_enterable':favorable,'direction':setup['direction'],
        'measurement_status':'AVAILABLE_DAILY_REFERENCE_MOVEMENT' if moved else 'UNAVAILABLE_OR_NO_NEW_COMPLETED_DAILY_OBSERVATION',
        'actual_entry_and_initial_R':'UNKNOWN','not_a_universal_1R_test':True}


def analyze(archive,operator,guidance):
    events,metadata,excluded=source_inputs(archive,operator)
    last=next(s for s in archive['calendar']['sessions'] if s['session_date']==archive['market_observation_end'])
    end=max(max(timestamp(a['upper']) for a in metadata),timestamp(last['closes_at'])+timedelta(minutes=60,microseconds=1)).isoformat()
    evidence=Evidence(archive['prices'],archive['coverage'],archive['calendar'],end)
    scenarios=[]
    for clock in timing_scenarios(metadata,archive['calendar']):
        ledger=opportunity_ledger(events,metadata,clock)
        by_id={s['setup_id']:s for s in ledger['setups']};op_by={o['opportunity_id']:o for o in ledger['opportunities']}
        constructions={o['opportunity_id']:candidate(o,evidence,archive['calendar'],archive['market_observation_end']) for o in ledger['opportunities']}
        comparisons=[]
        for symbol in ('CLMT','TEVA','GME','EBAY'):
            setup=next((s for s in ledger['setups'] if s['symbol']==symbol),None)
            if setup is None:continue
            selected=[o for o in ledger['opportunities'] if o['setup_id']==setup['setup_id']]
            source_ids={e['source_event_id'] for e in setup['events']}
            legacy={'symbol':symbol,'direction':setup['direction'],'initial_stop':setup['initial_published_stop'],
                'position_state':'LEGACY_SOURCE_LIST_LABEL_ONLY','events':[e for e in events if e['event_id'] in source_ids]}
            view={'prices':archive['prices'],'calendar':archive['calendar'],'market_observation_end':archive['market_observation_end'],'information_cutoff':archive['source_cutoff']}
            continuous=stop_state(legacy,clock,view,'A_HARD_STOP');continuous.pop('source_position_state',None)
            comparisons.append({'symbol':symbol,'setup_id':setup['setup_id'],'A_continuous_reference':continuous,
                'B_independent_hard_opportunities':[{'opportunity':o,'construction':constructions[o['opportunity_id']],
                    'subscriber_path':subscriber_path(o,constructions[o['opportunity_id']],evidence,archive['calendar'],archive['market_observation_end'],'HARD')} for o in selected],
                'C_independent_close_opportunities':[subscriber_path(o,constructions[o['opportunity_id']],evidence,archive['calendar'],archive['market_observation_end'],'CLOSE') for o in selected],
                'resolution':'APPARENT_SETUP_EXECUTION_CONTRADICTION_REMOVED_BY_CORRECTED_SEMANTICS; ACTUAL_SUBSCRIBER_BEHAVIOR_UNKNOWN'})
        transitions=[]
        order={a['alert_id']:i for i,a in enumerate(metadata)}
        for t in ledger['underway_transitions']:
            setup=by_id[t['setup_id']];op=op_by.get(t['last_eligible_opportunity_id'])
            result={**t,'measurements':extension(evidence,setup,op,t['assumed_at'],t['last_enterable_assessment'],t['latest_published_stop_at_assessment']),
                'controls':[],'alert_is_one_shared_cluster':True}
            for control in ledger['setups']:
                if control['setup_id']==setup['setup_id'] or control['direction']!=setup['direction']:continue
                before=[a for a in ledger['assessments'] if a['setup_id']==control['setup_id'] and order[a['source_alert_id']]<order[t['source_alert_id']]]
                after=[a for a in ledger['assessments'] if a['setup_id']==control['setup_id'] and order[a['source_alert_id']]<=order[t['source_alert_id']]]
                if not before or before[-1]['entry_state']!='ENTERABLE' or after[-1]['entry_state']!='ENTERABLE':continue
                prior_ops=[o for o in ledger['opportunities'] if o['setup_id']==control['setup_id'] and o['entry_eligible'] and order[o['source_alert_id']]<order[t['source_alert_id']]]
                prior=before[-1]
                result['controls'].append({'setup_id':control['setup_id'],'symbol':control['symbol'],'direction':control['direction'],
                    'source_state':'REMAINED_ENTERABLE','assessment_kind':'EXPLICIT_UPDATE' if after[-1]['source_alert_id']==t['source_alert_id'] else 'CARRIED_STATE_NOT_A_NEW_EXPLICIT_ASSESSMENT',
                    'measurements':extension(evidence,control,prior_ops[-1] if prior_ops else None,t['assumed_at'],prior,after[-1]['published_stop'])})
            transitions.append(result)
        scenarios.append({'timing_scenario':clock['name'],'ledger':ledger,'candidate_references':list(constructions.values()),
            'four_case_comparison':comparisons,'underway_comparison':transitions})
    return {'schema_version':'marketlife_opportunity_research_v1','guidance':guidance,'source_alerts':metadata,'source_events':events,
        'excluded_original_actions':excluded,'market_observation_end':archive['market_observation_end'],'scenarios':scenarios,
        'original_research_preserved':True,'new_operator_alerts_are_not_fresh_prediction_validation':True,
        'extension_threshold_identified':False,'observed_executions':'UNKNOWN'}
