"""Reconcile the one supplied MarketLife change log; source facts, no trade model."""
from collections import Counter
from copy import deepcopy
import csv
from datetime import datetime, time, timedelta
from decimal import Decimal
import io
import json
import re
from zoneinfo import ZoneInfo

from .comprehension.inputs import _check_hashes
from .ingestion.storage import digest, encode
from .initial_stops import initial_inventory
from .models import timestamp

ET = ZoneInfo('America/New_York')


def parse_log(content):
    lines = content.decode().splitlines()
    label = re.fullmatch(r'Last 14 days · (\d+) changes', lines[0])
    if not label: raise ValueError('unrecognized supplied log heading')
    events = []; seen = set()
    for index, row in enumerate(csv.DictReader(io.StringIO('\n'.join(lines[1:])), delimiter='\t'), 1):
        if set(row) != {'Day', 'Ticker', 'Change'} or None in row.values():
            raise ValueError('malformed supplied log row')
        day = datetime.strptime(row['Day'] + ' 2026', '%a %b %d %Y').date()
        if day.strftime('%a') != row['Day'][:3]: raise ValueError('log weekday/date mismatch')
        text = row['Change']; key = (day.isoformat(), row['Ticker'], text)
        if key in seen: raise ValueError('duplicate source log row needs explicit reconciliation')
        seen.add(key)
        event = {'event_id': f'log-20261102:row-{index:03d}', 'source_row': index,
            'reported_day': row['Day'], 'log_date': day.isoformat(), 'symbol': row['Ticker'],
            'source_text': text, 'source_line_sha256': digest((f"{row['Day']}\t{row['Ticker']}\t{text}").encode()),
            'publication_at': None, 'publication_precision': 'UNKNOWN_INTRADAY',
            'actual_subscriber_execution': 'UNKNOWN'}
        m = re.fullmatch(r'new (long|short) (?:(nested pullback|tight pullback|pullback|breakout) )?setup, stop (\d+\.\d+)', text)
        if m:
            event.update(kind='NEW_SETUP', direction=m[1].upper(), initial_stop=m[3],
                marketlife_type=m[2].capitalize() if m[2] else 'UNKNOWN')
        elif m := re.fullmatch(r'triggered (long|short); stop (\d+\.\d+)', text):
            event.update(kind='TRIGGERED', direction=m[1].upper(), reported_current_stop=m[2])
        elif m := re.fullmatch(r'stop moved to (\d+\.\d+) \(from (\d+\.\d+)\)', text):
            event.update(kind='STOP_MOVED', direction=None, reported_current_stop=m[1], previous_reported_stop=m[2])
        elif m := re.fullmatch(r'stopped out \((long|short)\)', text):
            event.update(kind='STOPPED_OUT', direction=m[1].upper())
        elif m := re.fullmatch(r'dropped from potential (longs|shorts)', text):
            event.update(kind='DROPPED', direction='LONG' if m[1] == 'longs' else 'SHORT', source_removal_kind='DROPPED')
        elif m := re.fullmatch(r'taken off the (long|short) (setups|trades underway)', text):
            event.update(kind='DROPPED', direction=m[1].upper(), source_removal_kind='TAKEN_OFF',
                reported_prior_state='UNDERWAY' if m[2] == 'trades underway' else 'SETUP')
        else: raise ValueError(f"unparsed supplied log row {index}: {text}")
        events.append(event)
    if len(events) != int(label[1]): raise ValueError('visible log row count differs from supplied heading')
    return events


def checked_proof(proof):
    files = {k: v.encode() for k, v in proof['files'].items()}
    _check_hashes(files, proof['hashes'])
    if set(files) != {'change-log-20261102.txt', 'book-excerpts.txt', 'provenance.json'}:
        raise ValueError('complete expanded source proof required')
    metadata = json.loads(files['provenance.json'])
    if metadata.get('source_log_label') != files['change-log-20261102.txt'].decode().splitlines()[0]:
        raise ValueError('source provenance heading disagrees with supplied log')
    return files


def date_compatible(decision, log_date):
    p = decision['publication']; day = datetime.fromisoformat(log_date).date()
    return timestamp(p['lower']).astimezone(ET).date() <= day <= timestamp(p['upper']).astimezone(ET).date()


def new_cutoffs(event, provenance, calendar):
    day = datetime.fromisoformat(event['log_date']).date()
    lower = datetime.combine(day, time(), ET); upper = lower + timedelta(days=1) - timedelta(microseconds=1)
    precision = 'LOG_DATE_ONLY_NOT_VERIFIED_PUBLICATION_DATE'
    if event['log_date'] == '2026-11-02':
        lower = timestamp(provenance['snapshot_publication_lower']); upper = timestamp(provenance['snapshot_publication_upper'])
        precision = 'OPERATOR_REPORTED_LATEST_BATCH_PUBLICATION_HOUR'
    close = next((timestamp(s['closes_at']) for s in calendar['sessions'] if s['session_date'] == event['log_date']), lower)
    cutoffs = {'EARLY': lower.isoformat(), 'CLOSE_BOUNDARY': min(upper, max(lower, close)).isoformat(), 'LATE': upper.isoformat()}
    return cutoffs, {'published_at': None, 'publication_precision': precision,
        'lower': lower.isoformat(), 'upper': upper.isoformat(), 'log_date': event['log_date'],
        'intended_trading_session': '2026-11-03' if event['log_date'] == '2026-11-02' else 'UNKNOWN',
        'timezone_basis': provenance['timezone_basis'],
        'bound_kind': 'CONDITIONAL_INFORMATION_VIEW_NOT_INVENTED_EXACT_PUBLICATION'}


def reconcile(source):
    files = checked_proof(source['expanded_log_proof']); provenance = json.loads(files['provenance.json'])
    events = parse_log(files['change-log-20261102.txt'])
    originals = initial_inventory(source['parent_source']); decisions = deepcopy(originals)
    by_id = {d['setup_id']: d for d in decisions}; used = set(); aliases = []; warnings = []
    # Source episodes whose openings precede the visible log can remain active.
    log_openings = [e for e in events if e['kind'] == 'NEW_SETUP']
    overlapping = {d['setup_id'] for d in decisions if any(e['symbol'] == d['symbol'] and
        e['direction'] == d['direction'] and Decimal(e['initial_stop']) == Decimal(d['published_stop']) and
        date_compatible(d, e['log_date']) for e in log_openings)}
    active = {d['symbol']: d['setup_id'] for d in decisions if d['setup_id'] not in overlapping}
    for d in decisions: d.update(log_event_ids=[], reported_log_date=None)
    episode_events = {d['setup_id']: [] for d in decisions}; unmatched = []
    for event in sorted(events, key=lambda e: (e['log_date'], e['source_row'])):
        symbol = event['symbol']
        if event['kind'] == 'NEW_SETUP':
            matches = [d for d in originals if d['setup_id'] not in used and d['symbol'] == symbol and
                d['direction'] == event['direction'] and Decimal(d['published_stop']) == Decimal(event['initial_stop']) and date_compatible(d, event['log_date'])]
            if len(matches) > 1: raise ValueError('ambiguous opening overlap requires source review')
            if symbol in active: raise ValueError(f'NEW SETUP while prior tracked episode remains open: {symbol}')
            if matches:
                decision = by_id[matches[0]['setup_id']]; used.add(decision['setup_id'])
                aliases.append({'kind': 'OVERLAPPING_NEW_SETUP', 'log_event_id': event['event_id'],
                    'setup_id': decision['setup_id'], 'original_decision_id': decision['decision_id'],
                    'evidence': 'Matching symbol/direction/initial stop and compatible source date bounds; no price-only deduplication.'})
            else:
                number = max((int(d['setup_id'].rsplit('-', 1)[1]) for d in decisions if d['symbol'] == symbol), default=0) + 1
                cutoffs, publication = new_cutoffs(event, provenance, source['parent_source']['calendar'])
                decision = {'decision_id': event['event_id'], 'setup_id': f'{symbol}-{number:03d}',
                    'symbol': symbol, 'direction': event['direction'], 'source_alert_id': f"log-batch:{event['log_date']}",
                    'source_order': max(d['source_order'] for d in decisions) + 1, 'decision_type': 'INITIAL',
                    'published_stop': event['initial_stop'], 'initial_published_stop': event['initial_stop'],
                    'source_text': event['source_text'], 'source_text_sha256': digest(files['change-log-20261102.txt']),
                    'observed_publication': 'UNKNOWN_EXACT_TIME', 'publication_display': event['reported_day'],
                    'publication': publication, 'cutoffs': cutoffs, 'cohort': 'EXPANDED_LOG_NEW',
                    'marketlife_type': event['marketlife_type'], 'entry_reference_at_initial_decision': None,
                    'entry_reference_type_at_initial_decision': 'UNKNOWN', 'entry_to_initial_stop_risk': 'UNKNOWN',
                    'actual_subscriber_execution': 'UNKNOWN', 'log_event_ids': [], 'reported_log_date': event['log_date']}
                decisions.append(decision); by_id[decision['setup_id']] = decision; episode_events[decision['setup_id']] = []
            decision['log_event_ids'].append(event['event_id']); decision['reported_log_date'] = event['log_date']
            if event['marketlife_type'] != 'UNKNOWN': decision['marketlife_type'] = event['marketlife_type']
            active[symbol] = decision['setup_id']; event['opening_reconciliation'] = 'ORIGINAL_OVERLAP' if matches else 'ADDITIONAL_EPISODE'
        sid = active.get(symbol)
        if sid is None:
            event['setup_id'] = None; unmatched.append(event['event_id']); continue
        d = by_id[sid]
        if event['direction'] is not None and event['direction'] != d['direction']:
            raise ValueError('log action direction disagrees with tracked episode')
        event.update(setup_id=sid, resolved_direction=d['direction'])
        episode_events[sid].append(event['event_id'])
        # Only reported source removal changes episode identity; no fill or exit model.
        if event['kind'] in {'STOPPED_OUT', 'DROPPED'}: active.pop(symbol)
    if len(used) != len(overlapping): raise ValueError('not all overlapping original openings reconciled')
    # Retain the older operator summary as a distinct source, not another opening.
    older = source.get('earlier_observation_proof')
    if older:
        prior_files = {k: v.encode() for k, v in older['files'].items()}; _check_hashes(prior_files, older['hashes'])
        prior = json.loads(prior_files['observation.json'])
        for action in prior['actions']:
            if action['kind'] != 'NEW_SETUP': continue
            matches = [d for d in decisions if d['cohort'] == 'EXPANDED_LOG_NEW' and d['symbol'] == action['symbol'] and
                d['direction'] == action['direction'] and Decimal(d['published_stop']) == Decimal(action['initial_stop'])]
            if len(matches) != 1: raise ValueError('earlier operator summary alias is ambiguous')
            aliases.append({'kind': 'EARLIER_SUMMARY_DATE_ROLE_DIFFERENCE', 'setup_id': matches[0]['setup_id'],
                'earlier_action_id': action['action_id'], 'earlier_source_date': prior['source_date'],
                'log_event_date': matches[0]['reported_log_date'], 'intended_trading_session': '2026-11-03',
                'interpretation': 'Preserve November 3 commentary/intended-session and November 2 log date separately; one opening episode.'})
    warnings.extend([
        {'kind': 'SOURCE_SEMANTICS_DIFFER', 'detail': 'TRIGGERED is not automatically UNDERWAY or a subscriber fill; older co-published stop/state reports remain separate source evidence.'},
        {'kind': 'LOG_NOT_EXHAUSTIVE_HISTORY', 'detail': '118 visible rows match the supplied heading; this does not certify all MarketLife history. Earlier captured eligibility facts such as SAIL return remain preserved.'},
        {'kind': 'PUBLICATION_CLOCKS_CONDITIONAL', 'detail': 'Earlier row dates are log dates, not exact publication times. Original 34 cutoffs are unchanged; latest November 2 batch uses operator-supplied 5pm hour bounds.'},
    ])
    return {'schema_version': 'pr9f_source_reconciliation_v2', 'inventory': decisions, 'events': events,
        'episode_events': episode_events, 'aliases': aliases, 'warnings': warnings, 'unmatched_event_ids': unmatched,
        'summary': {'visible_rows': len(events), 'event_types': dict(Counter(e['kind'] for e in events)),
            'original_episodes': len(originals), 'overlapping_new_setup_rows': len(used),
            'additional_opening_episodes': len(decisions) - len(originals), 'reconciled_initial_stops': len(decisions),
            'directions': dict(Counter(d['direction'] for d in decisions)),
            'observed_types': dict(Counter(d['marketlife_type'] for d in decisions)),
            'unmatched_events': len(unmatched), 'management_mechanisms_investigated': False}}
