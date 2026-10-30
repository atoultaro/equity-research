"""Source setup eligibility and versioned opportunities; executions stay unknown."""
from collections import defaultdict
from copy import deepcopy
from datetime import datetime,time,timedelta
from decimal import Decimal
import re
from zoneinfo import ZoneInfo

from .ingestion.storage import digest
from .lifecycle.source import PATTERNS,SECTIONS
from .models import timestamp
from .prospective.inputs import parse_known,upper
from .reconstruction.timing import bounds

ET=ZoneInfo('America/New_York')


def supplied_events(record,offset):
    events=[]
    for alert in record['alerts']:
        section=None;headers=[];position=0
        for line_number,raw in enumerate(alert['text'].splitlines(keepends=True),1):
            line=raw.strip()
            header=next((name for name in SECTIONS if re.fullmatch(re.escape(name)+r'_+',line)),None)
            if header:section=SECTIONS[header];headers.append(header)
            elif section and line and line!='None':
                m=re.fullmatch(PATTERNS[section],line)
                if not m:raise ValueError('unparsed operator setup action')
                event={'event_id':f"{alert['alert_id']}:line-{line_number}",'source_order':offset+len(events),
                    'symbol':m[1],'type':section,'published_at':alert.get('published_at'),
                    'source_date':alert['source_date'],'attribution':'EXPERT_REPORTED_OPERATOR_SUPPLIED',
                    'source':{'alert_id':alert['alert_id'],'line':line_number,'character_offset':position,
                              'alert_text_sha256':digest(alert['text'].encode()),'source_text':line}}
                if section=='OPEN_NEW_POSITION':event.update(direction=m[2].upper(),stop=m[3])
                elif section=='STOP_CHANGED':event.update(stop=m[2],previous_stop=m[3])
                elif section=='SETUP_CHANGED':
                    if m[2]!=m[4]:raise ValueError('setup direction cannot silently reverse')
                    event.update(direction=m[2].upper(),setup_availability='UNDERWAY' if m[3] else 'ENTERABLE',
                                 reported_previous_eligibility='UNDERWAY' if m[5] else 'ENTERABLE')
                else:event.update(direction=m[2].upper(),reported_underway=bool(m[3]))
                if 'stop' in event and Decimal(event['stop'])<=0:raise ValueError('positive published stop required')
                events.append(event)
            position+=len(raw)
        if headers!=list(SECTIONS):raise ValueError('all four source sections required in order')
    return events


def source_inputs(archive,operator):
    events,excluded=parse_known(archive['alerts'])
    metadata=[]
    original_bounds=bounds(archive['alerts']['alerts'])
    for a in archive['alerts']['alerts']:
        b=original_bounds[a['alert_id']]
        metadata.append({'alert_id':a['alert_id'],'published_at':a['published_at'],
            'publication_precision':a['publication_precision'],'lower':b['lower'],'upper':b['upper'],
            'text_sha256':digest(a['text'].encode()),'bound_kind':b['kind']})
    if operator:
        captured=timestamp(operator['captured_at'])
        for a in operator['alerts']:
            if a['alert_id'] in {m['alert_id'] for m in metadata}:raise ValueError('duplicate source alert identity')
            if a.get('published_at'):
                lower=timestamp(a['published_at']);latest=upper(a)
            else:
                day=datetime.fromisoformat(a['source_date']).date()
                lower=datetime.combine(day,time(),ET)
                latest=min(datetime.combine(day+timedelta(days=1),time(),ET)-timedelta(microseconds=1),captured)
            if lower>latest:raise ValueError('operator source date is after capture')
            metadata.append({'alert_id':a['alert_id'],'published_at':a.get('published_at'),
                'publication_precision':a['publication_precision'],'source_date':a['source_date'],
                'lower':lower.isoformat(),'upper':latest.isoformat(),'text_sha256':digest(a['text'].encode()),
                'bound_kind':'OPERATOR_DATE_IN_CLIENT_TIMEZONE_AND_RECEIPT_BOUND_NOT_EXACT_PUBLICATION'})
        events+=supplied_events(operator,len(events))
    return events,metadata,excluded


def timing_scenarios(metadata,calendar):
    output=[]
    for name in ('EARLY','CLOSE_BOUNDARY','LATE'):
        actions={};previous=None
        for a in metadata:
            lo,hi=timestamp(a['lower']),timestamp(a['upper']);moment=hi
            if a['published_at'] is None and name!='LATE':
                if a['publication_precision']=='DATE' and name=='EARLY':moment=lo
                else:
                    field='opens_at' if name=='EARLY' else 'closes_at'
                    candidates=[timestamp(s[field])-(timedelta(microseconds=1) if name=='EARLY' else timedelta())
                        for s in calendar['sessions'] if lo<timestamp(s[field])<=hi]
                    moment=candidates[0] if candidates else lo
                if previous:moment=max(moment,previous)
            if previous and moment<previous or moment>hi or moment<lo:raise ValueError('inconsistent publication bounds/order')
            actions[a['alert_id']]=moment.isoformat();previous=moment
        output.append({'name':name,'actions':actions,'attribution':'CONDITIONAL_PUBLICATION_SCENARIO_NOT_SOURCE_FACT'})
    return output


def opportunity_ledger(events,metadata,clock):
    """Source-only construction. Price paths never alter eligibility or episodes."""
    by_alert=defaultdict(list)
    for e in events:by_alert[e['source']['alert_id']].append(e)
    bound={a['alert_id']:a for a in metadata}
    current={};numbered=defaultdict(int);setups=[];opps=[];transitions=[];assessments=[]
    last_op={};active_op={}

    def end_op(setup_id,at,reason):
        old=active_op.pop(setup_id,None)
        if old is not None and old['effective_until'] is None:
            old.update(effective_until=at,eligibility_end_reason=reason)
            if old['effective_from']==at:
                old.update(entry_eligible=False,eligibility_end_reason='CO_PUBLISHED_SUPERSESSION_NO_ENTRY_WINDOW')

    for a in metadata:
        aid=a['alert_id'];at=clock['actions'][aid]
        grouped=defaultdict(list)
        for e in by_alert[aid]:grouped[e['symbol']].append(e)
        for symbol,actions in grouped.items():
            prior=deepcopy(current.get(symbol))
            state=prior['entry_state'] if prior else None
            for e in actions:
                if e['type']=='OPEN_NEW_POSITION':state='ENTERABLE'
                elif e['type']=='SETUP_CHANGED':state=e['setup_availability']
                elif e['type']=='DROPPED':state='DROPPED'
            final_state=state
            for e in actions:
                kind=e['type'];setup=current.get(symbol)
                if kind=='OPEN_NEW_POSITION':
                    if setup and setup['setup_status']=='ACTIVE':raise ValueError('ADDED while setup already active')
                    numbered[symbol]+=1;sid=f'{symbol}-{numbered[symbol]:03d}'
                    setup={'setup_id':sid,'symbol':symbol,'direction':e['direction'],'setup_status':'ACTIVE',
                        'entry_state':'ENTERABLE','published_stop':e['stop'],'initial_published_stop':e['stop'],
                        'events':[],'observed_execution':'UNKNOWN','last_enterable_assessment':None,
                        'opened_source_event_id':e['event_id'],'dropped_source_event_id':None}
                    current[symbol]=setup;setups.append(setup)
                elif not setup or setup['setup_status']!='ACTIVE':raise ValueError('source action has no active setup')
                sid=setup['setup_id'];before=setup['entry_state']
                if e.get('direction',setup['direction'])!=setup['direction']:raise ValueError('setup direction mismatch')
                if kind=='STOP_CHANGED':
                    if Decimal(e['previous_stop'])!=Decimal(setup['published_stop']):raise ValueError('published-stop source chain mismatch')
                    setup['published_stop']=e['stop']
                if kind=='SETUP_CHANGED':
                    if e.get('reported_previous_eligibility',before)!=before:raise ValueError('reported prior eligibility mismatch')
                    setup['entry_state']=e['setup_availability']
                    if before=='ENTERABLE' and setup['entry_state']=='UNDERWAY':
                        transitions.append({'setup_id':sid,'symbol':symbol,'direction':setup['direction'],
                            'source_event_id':e['event_id'],'source_alert_id':aid,'assumed_at':at,
                            'published_at':e['published_at'],'publication_bounds':bound[aid],
                            'last_enterable_assessment':deepcopy(prior['last_enterable_assessment']) if prior else None,
                            'last_eligible_opportunity_id':prior.get('latest_eligible_opportunity_id') if prior else None,
                            'previous_published_stop':prior['published_stop'] if prior else None,
                            'latest_published_stop_at_assessment':setup['published_stop'],'observed_execution':'UNKNOWN'})
                    if setup['entry_state']=='UNDERWAY':end_op(sid,at,'UNDERWAY_SUSPENDS_FRESH_ENTRY_NOT_AN_EXIT')
                if kind=='DROPPED':
                    setup.update(setup_status='DROPPED',entry_state='DROPPED',dropped_source_event_id=e['event_id'])
                    end_op(sid,at,'DROPPED_FROM_SETUP_LIST_NOT_AN_EXECUTED_EXIT')
                create=(kind=='OPEN_NEW_POSITION' or kind=='STOP_CHANGED' and before=='ENTERABLE' or
                        kind=='SETUP_CHANGED' and before=='UNDERWAY' and setup['entry_state']=='ENTERABLE')
                if create:
                    previous=last_op.get(sid)
                    end_op(sid,at,'SUPERSEDED_FOR_FUTURE_ENTRIES_ONLY')
                    version=1+(previous['opportunity_version'] if previous else 0)
                    oid=f'{sid}:opportunity-{version:03d}'
                    eligible=final_state=='ENTERABLE'
                    row={'setup_id':sid,'opportunity_id':oid,'symbol':symbol,'direction':setup['direction'],
                        'source_alert_id':aid,'source_event_id':e['event_id'],'opportunity_version':version,
                        'published_stop':setup['published_stop'],'effective_from':at,'effective_until':None if eligible else at,
                        'source_published_at':e['published_at'],'publication_bounds':bound[aid],
                        'source_setup_state':final_state,'entry_eligible':eligible,'superseded_by':None,
                        'observed_execution':'UNKNOWN','actual_entry':None,'actual_quantity':None,
                        'eligibility_end_reason':None if eligible else 'CO_PUBLISHED_SUSPENSION_NO_ENTRY_WINDOW',
                        'assessment_is_atomic':True}
                    if previous:previous['superseded_by']=oid
                    opps.append(row);last_op[sid]=row
                    if eligible:
                        active_op[sid]=row;setup['latest_eligible_opportunity_id']=oid
                setup['events'].append({'source_event_id':e['event_id'],'source_alert_id':aid,'legacy_source_type':kind,
                    'setup_action':'ADDED' if kind=='OPEN_NEW_POSITION' else kind,'source_text':e['source']['source_text'],
                    'source_text_sha256':e['source']['alert_text_sha256'],'published_at':e['published_at'],
                    'assumed_at':at,'entry_state_before':before,'entry_state_after':setup['entry_state'],
                    'published_stop':setup['published_stop'],'observed_execution':'UNKNOWN'})
            if final_state=='ENTERABLE':
                last=actions[-1]
                current[symbol]['last_enterable_assessment']={'source_alert_id':aid,'source_event_id':last['event_id'],'assumed_at':at,
                    'published_at':last['published_at'],'published_stop':current[symbol]['published_stop']}
            assessments.append({'setup_id':sid,'symbol':symbol,'source_alert_id':aid,'assumed_at':at,
                'entry_state':current[symbol]['entry_state'],'published_stop':current[symbol]['published_stop'],
                'setup_status':current[symbol]['setup_status']})
    return {'timing_scenario':clock['name'],'setups':setups,'opportunities':opps,'underway_transitions':transitions,
        'assessments':assessments,'semantics':'SOURCE_SETUP_LIFECYCLE_AND_FRESH_ENTRY_ELIGIBILITY_NOT_PERSONAL_POSITIONS',
        'source_actions_do_not_establish_executions':True}


def eligible_at(ledger,setup_id,at):
    t=timestamp(at)
    return [o for o in ledger['opportunities'] if o['setup_id']==setup_id and o['entry_eligible']
            and timestamp(o['effective_from'])<=t and (o['effective_until'] is None or t<timestamp(o['effective_until']))]
