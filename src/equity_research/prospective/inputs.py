"""Causal prefix views and a narrow adapter around the unchanged source parser."""
from copy import deepcopy
from datetime import timedelta
import re

from ..ingestion.storage import digest
from ..lifecycle.source import PATTERNS, SECTIONS, UNIVERSE, EXCLUDED, parse_alerts, reconstruct
from ..models import timestamp
from ..reconstruction.timing import bounds


def upper(alert):
    if alert['published_at']:
        moment=timestamp(alert['published_at'])
        if alert['publication_precision'] not in {'MINUTE','SECOND'}:raise ValueError('explicit publication precision required')
        return moment.replace(second=0,microsecond=0)+timedelta(minutes=1) if alert['publication_precision']=='MINUTE' else moment
    if not alert.get('email_received_at'):
        raise ValueError('unknown publication requires an availability upper bound')
    return timestamp(alert['email_received_at'])


def parse_known(record):
    """Quarantine foreign actions without changing any original body or line offset.

    The inherited parser is intentionally frozen to26 stocks. Blank only foreign
    action lines in a separate parsing projection, then restore original source
    hashes. All original text remains in private input/reveal bundles.
    """
    projected=deepcopy(record); foreign=[]
    for alert in projected['alerts']:
        lines=[];section=None
        for number,line in enumerate(alert['text'].splitlines(keepends=True),1):
            name=next((n for n in SECTIONS if re.fullmatch(re.escape(n)+r'_+',line.strip())),None)
            if name:section=SECTIONS[name]
            match=re.fullmatch(PATTERNS[section],line.strip()) if section else None
            if match and match[1] not in set(UNIVERSE)|set(EXCLUDED):
                foreign.append({'alert_id':alert['alert_id'],'line':number,'symbol':match[1],
                    'source_text_sha256':digest(line.strip().encode()),'reason':'OUTSIDE_INITIAL_26_STOCK_COHORT'})
                line=''.join(ch if ch in '\r\n' else ' ' for ch in line)
            lines.append(line)
        alert['text']=''.join(lines)
    events,excluded,_=parse_alerts(projected,allow_email_bound=True,require_seven=False)
    originals={a['alert_id']:a for a in record['alerts']}
    for event in events:
        event['source']['alert_text_sha256']=digest(originals[event['source']['alert_id']]['text'].encode())
    return events,excluded+foreign


def metadata(alert):
    return {k:v for k,v in alert.items() if k not in {'text','html'}} | {'text_sha256':digest(alert['text'].encode())}


def make_view(archive, archive_sha, cutoff, count=None):
    cutoff_ts=timestamp(cutoff)
    available=[]
    # Inspect availability metadata before selecting/parsing any action body.
    for alert in archive['alerts']['alerts']:
        if upper(alert)>cutoff_ts:break
        available.append(alert)
    if count is not None:
        if not 1<=count<=len(available):raise ValueError('requested source prefix is not available at cutoff')
        if count!=len(available):raise ValueError('prefix omits already-available source history')
        available=available[:count]
    if not available:raise ValueError('no source prefix available')
    source={**archive['alerts'],'alerts':available}
    events,excluded=parse_known(source)
    reconstruct(events,validate_pilot=False)
    known_symbols={e['symbol'] for e in events}|{'SPY','QQQ'}
    schedule=archive['calendar']
    market_end=min(archive['market_observation_end'],cutoff_ts.date().isoformat())
    days={s['session_date'] for s in schedule['sessions'] if s['session_date']<=market_end
          and timestamp(s['closes_at'])+timedelta(minutes=60)<cutoff_ts}
    prices={symbol:[deepcopy(r) for r in rows if r['session_date'] in days] for symbol,rows in archive['prices'].items() if symbol in known_symbols}
    coverage={s:{k:v for k,v in c.items() if k in {'security','contract','price_basis','volume_basis','origin','source_bundle_sha256'}}
              for s,c in archive['coverage'].items() if s in known_symbols}
    return {'schema_version':'grimes_prediction_view_v1','information_cutoff':cutoff,
        'market_observation_end':max(days) if days else None,'archive_sha256':archive_sha,
        'alerts':[metadata(a) for a in available],'events':events,'excluded_actions':excluded,
        'prices':prices,'coverage':coverage,'calendar':schedule,
        'provenance':archive['provenance'],
        'availability_assumption':'XNYS completed Close plus60 minutes; native captures are not publication proof'}


def validate_view(view):
    if view.get('schema_version')!='grimes_prediction_view_v1':raise ValueError('unsupported causal view')
    cutoff=timestamp(view['information_cutoff'])
    alerts=view['alerts'];by_id={a['alert_id']:a for a in alerts}
    if len(by_id)!=len(alerts) or any(a['source_sequence']!=i or upper(a)>cutoff for i,a in enumerate(alerts)):
        raise ValueError('future, duplicate or non-prefix source metadata in view')
    if [e['source_order'] for e in view['events']]!=list(range(len(view['events']))):
        raise ValueError('non-prefix event order')
    for event in view['events']:
        a=by_id.get(event['source']['alert_id'])
        if a is None or a['published_at']!=event['published_at'] or a['text_sha256']!=event['source']['alert_text_sha256']:
            raise ValueError('event/source provenance mismatch')
        if event.get('effective_at') and timestamp(event['effective_at'])>cutoff:
            raise ValueError('future event availability in view')
    from ..ingestion.calendar import schedule
    calendar=view['calendar']
    if calendar!=schedule(calendar['start'],calendar['end']):raise ValueError('calendar differs from pinned XNYS schedule')
    days={s['session_date']:s for s in view['calendar']['sessions']}
    for rows in view['prices'].values():
        ordered=[r['session_date'] for r in rows]
        if ordered!=sorted(set(ordered)):raise ValueError('duplicate or nonchronological market observations')
        for row in rows:
            day=row['session_date']
            if (day not in days or day>view['market_observation_end'] or
                    timestamp(days[day]['closes_at'])+timedelta(minutes=60)>=cutoff):
                raise ValueError('future or undeclared market observation in view')
    return reconstruct(view['events'],validate_pilot=False)[0]


def clocks(view):
    intervals=bounds(view['alerts'])
    variants=[]
    for name in ('EARLY','CLOSE_BOUNDARY','LATE'):
        actions={};previous=None
        for alert in view['alerts']:
            b=intervals[alert['alert_id']];lower,latest=timestamp(b['lower']),timestamp(b['upper'])
            moment=latest
            if b['published_at'] is None and name!='LATE':
                field='opens_at' if name=='EARLY' else 'closes_at'
                candidate=next((timestamp(s[field]) for s in view['calendar']['sessions'] if lower<timestamp(s[field])<=latest),latest)
                moment=max(candidate,previous) if previous else candidate
            if previous and moment<previous:raise ValueError('scenario chronology conflict')
            actions[alert['alert_id']]=moment.isoformat();previous=moment
        variants.append({'name':name,'actions':actions,'publication_bounds':intervals,
            'attribution':'CONDITIONAL_TIMING_SCENARIO_NOT_A_SOURCE_PUBLICATION_FACT'})
    return variants
