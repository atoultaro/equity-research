"""Deterministic Markdown from sealed derived setup evidence, without acquisition."""
from collections import Counter


def number(value):
    return 'UNAVAILABLE' if value is None else f'{value:.3f}'


def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join('---' for _ in headers)+' |']+
        ['| '+' | '.join(str(v) for v in row)+' |' for row in rows])


def path_label(path):
    if path.get('first_stop_session'):return 'stop condition '+path['first_stop_session']
    if path['state']=='HYPOTHETICALLY_REMAINS_PROTECTED_AT_DATA_END':return 'protected through data end'
    return path['state']


def reports(research,gate,hashes):
    """Publication schedules are alternatives, never pooled as extra observations."""
    late=research['scenarios'][-1];ledger=late['ledger']
    active=[s for s in ledger['setups'] if s['setup_status']=='ACTIVE']
    eligible=sum(o['entry_eligible'] for o in ledger['opportunities'])
    provenance=f"Native semantic study SHA256: `{hashes['native_study']}`. Public evidence SHA256: `{hashes['public_evidence']}`. "
    provenance+='[Derived evidence and input registry](../evidence/pr9c-setup-opportunities-v1/manifest.json); [validation](../evidence/pr9c-setup-validation-v1/validation.json).'
    entry=[
        '# Grimes setup and entry-opportunity reassessment',
        'MarketLife reports setup selection and fresh-entry eligibility. ADDED, stop revisions, UNDERWAY and DROPPED do not establish personal positions or executions. This interpretation supersedes execution inferences in the preserved PR16–PR20 and original PR9C reports; their frozen results remain historical conditional experiments.',
        provenance,
        f"Ten operator-supplied alerts through October 29 produce {len(ledger['setups'])} captured setup episodes (26 original plus eight newly reported additions), {len(ledger['opportunities'])} version records, and {eligible} nonempty eligible windows. The other {len(ledger['opportunities'])-eligible} versions coincide with UNDERWAY and have no entry window. These counts do not multiply across the three publication scenarios. No newly added symbol has acquired prices in this amendment.",
        'The original weekly publication remains UNKNOWN. October 27–29 have operator-supplied dates, no exact publication times. EARLY uses the date’s start, CLOSE_BOUNDARY uses its cash Close, and LATE uses the date’s end capped by capture time. These are conditional timing bounds in America/New_York, not discovered timestamps. The weekly scenarios retain the prior metadata bracket. Completed daily evidence requires Close + 60 minutes strictly before the decision cutoff.',
        '## Source state after the October 29 supplied alert',
        table(['Symbol','Direction','Setup','Fresh entry','Published stop'],[(s['symbol'],s['direction'],s['setup_status'],s['entry_state'],s['published_stop']) for s in active]),
        'SAIL’s October 27 stop/UNDERWAY assessment blocks fresh entry. Its October 28 stop is monitored only. On October 29 the stop becomes 20.70 while still UNDERWAY; the explicitly reported return to ENTERABLE then creates version 3 at 20.70. None of these actions supplies a subscriber fill. The original 26-row trade-status CSV remains an unchanged October 26 historical view, not the current setup book.',
        '## Causal references and hypothetical behavior',
        'Each nonempty opportunity records the available Close, completed shared ATR14, signed stop distance, SMA10/20/50, confirmed swings, prior-20 extremes, volatility/compression and relative SPY strength where supported. An available Close is a technical reference, never a fill retroactively assigned to an already-past Close. A candidate Open must occur strictly after the assumed publication and before supersession/suspension/removal. Unobserved, nonprotective and missing-session candidates remain unavailable.',
        'A is the preserved continuous next-Open hard-stop reference with causal reported stop updates and no re-entry. B and C are independent candidate executions for each eligible version, using that version’s fixed stop: B checks Open gaps and daily extremes; C checks closing confirmation. Source supersession, UNDERWAY and DROPPED end future-entry eligibility, not a subscriber holding. These alternatives do not reconstruct a sequential re-entry portfolio. No stop revision changes an earlier candidate retroactively. Closing confirmation is an exploratory convention, not evidence of MarketLife’s or Grimes’ actual order policy. No quantities, actual initial R, costs, fills or P&L are inferred.',
        '## Four prior apparent contradictions',
        table(['Case','A: first hard-stop condition','New opportunities and remaining uncertainty'],[
            ('CLMT','October 19','53.40 → October 20 Open; 53.02 → October 21 Open. Both later hard-stop candidates touch on October 21. Continuing ENTERABLE after the first stop is coherent; no actual re-entry is observed.'),
            ('TEVA','October 21 Open gap','39.35 → October 22 Open, hard condition October 23. 39.05 → October 23 Open only if the unknown weekly DROP had not yet ended eligibility; this fixed-stop candidate remains protected through October 26.'),
            ('GME','October 22','24.78 and weekly 24.40 create distinct windows. An EARLY weekly update supersedes 24.78 before Friday Open; other clocks permit it. The 24.40 candidate touches October 26. No executed sequence is identified.'),
            ('EBAY','October 26','The old 119.20 candidate crosses on October 26. After-hours 117.50 creates a fresh opportunity; available Close 118.62 is a reference, not a fill. October 27 prices are missing, and its date-only DROP can precede the next Open. Fresh execution is unverified.')]),
        'The corrected semantics remove the apparent source/execution contradiction in all four cases. They do not rescue a continuously held hard-stop execution after its first breach or prove which subscriber traded. New opportunities make later source revisions coherent without requiring deferred review, stop cancellation, price rescaling or inferred actual re-entry. CDE’s UNDERWAY label likewise cannot establish a held runner or disprove a subscriber’s full +1R exit. Original numerical forensic results and Model E failures remain preserved, not retuned.',
        '## Candidate and path comparison by conditional publication schedule',
    ]
    rows=[]
    for s in research['scenarios']:
        for case in s['four_case_comparison']:
            for b,c in zip(case['B_independent_hard_opportunities'],case['C_independent_close_opportunities']):
                o=b['opportunity'];k=b['construction'];opening=k['next_open'] or {}
                rows.append((s['timing_scenario'],case['symbol'],o['opportunity_version'],o['published_stop'],
                    opening.get('session','—'),number(opening.get('price')),k['status'],path_label(b['subscriber_path']),path_label(c)))
    entry.append(table(['Clock','Symbol','Version','Stop','Candidate session','Open reference','Feasibility','B: hard','C: Close'],rows))
    entry += [
        '## Replacement forward registration',
        f"Status: **{gate['status']}** at {gate['asof']}. Required latest eligible session: {gate['required_latest_completed_session']}; available market observations end {research['market_observation_end']}. No replacement forecast was registered.",
        'Known active symbols SIG, CNQ, MMM, SAIL, SLB and benchmark SPY lack October 27–29 bars. Active DUK, PAA, FCX, CRWV and NBIS have no qualified market identities/history in the archive. All ten active setups lack current technical evidence. The supplied alert bodies have not been attested complete through registration. The gate requires consecutive completed feature sessions and a matching ordered alert-manifest attestation; it never fetches an automatic subscriber feed or fills gaps.',
        'The sealed original forward forecast `36b732cdb82e74a9c90f8add9d6e66015f31bcf9da156cb6213a858bf7676135` remains byte-identical and unevaluated, but is **non-operational**. October 27–29 backfill is not fresh validation of that stale forecast. New forecasts target eligibility and setup removal, with removal abstention until a defensible rule exists; hypothetical stop-out is never mapped to source DROP.',
    ]
    transitions=late['underway_comparison']
    measured=[t for t in transitions if t['measurements']['measurement_status']=='AVAILABLE_DAILY_REFERENCE_MOVEMENT']
    directions=Counter(t['direction'] for t in measured)
    underway=[
        '# Grimes ENTERABLE → UNDERWAY transitions',
        'UNDERWAY means the source judges a setup too extended for attractive fresh entry. It establishes neither a profitable held position nor an executed entry. This study describes the observable boundary without fitting a threshold or assuming universal +1R.',
        provenance,
        f"There are {len(transitions)} source transitions across {len({t['source_alert_id'] for t in transitions})} shared alert clusters. Only {len(measured)} have new completed daily reference movement: {directions['LONG']} LONG and {directions['SHORT']} SHORT across {len({t['source_alert_id'] for t in measured})} clusters. The additional seven reports lack October 27–29 daily evidence. Scenarios are conditional timing sensitivity, not replicated observations.",
        '## Predeclared measurements',
        'Directional movement is sign × (available Close − anchor price), normalized separately by anchor completed ATR14 and current completed ATR14. Anchors are ADDED’s available Close, the latest eligible opportunity Close before the assessment, the last explicit ENTERABLE assessment Close, and the first eligible regular Open after ADDED when its full daily bar is already available by the transition. None is an observed entry; ATR distance is not initial R. Co-published revisions are outcomes of one atomic assessment and cannot become prior predictors of that same transition.',
        'The machine evidence retains each anchor session/price/ATR, previous and newly published stops, favorable-session counts, signed SMA10/20 extension, SMA50, confirmed swing/prior-20 distances, volatility, compression and relative SPY movement. Missing features stay unavailable; TEVA’s inherited short history remains insufficient for SMA50. Date-only EARLY/CLOSE clocks can have no newly completed observation, which is not evidence of no intraday movement.',
        '## LATE conditional schedule: all transitions',
    ]
    rows=[]
    for t in transitions:
        m=t['measurements'];v=m['current_snapshot'];refs=m['references']
        rows.append((t['symbol'],t['direction'],t['source_alert_id'],
            (t['last_enterable_assessment'] or {}).get('source_alert_id','UNKNOWN'),
            v.get('feature_session') if v['status']=='AVAILABLE' else 'UNAVAILABLE',
            number(refs['ADDED_CLOSE']['advance_anchor_ATR']),number(refs['LATEST_ELIGIBLE_OPPORTUNITY_CLOSE']['advance_anchor_ATR']),
            number(refs['FIRST_OPPORTUNITY_OPEN']['advance_anchor_ATR']),number(v.get('entry_to_stop_ATR')),
            m['favorable_sessions_since_last_enterable'] if m['favorable_sessions_since_last_enterable'] is not None else 'UNAVAILABLE'))
    underway.append(table(['Symbol','Direction','UNDERWAY alert','Last explicit E alert','Available session','Added Close ATR','Prior opportunity Close ATR','First Open ATR','Close-to-new-stop ATR','Favorable sessions'],rows))
    underway += [
        '## Same-direction setups remaining ENTERABLE',
        'Controls were ENTERABLE before the same alert and remain so afterward. Newly ADDED setups are not controls. An omitted control carries its last reported eligibility; omission is not a new explicit attractiveness assessment. Repeated OMER comparisons in one alert are a single shared control observation, not independent corroboration. The table deduplicates controls by alert and setup.',
    ]
    controls={}
    for t in transitions:
        for c in t['controls']:controls[(t['source_alert_id'],c['setup_id'])]=c
    underway.append(table(['Alert','Control','Direction','Assessment','Added Close ATR','Prior opportunity Close ATR','Close-to-stop ATR'],[
        (aid,c['symbol'],c['direction'],c['assessment_kind'],number(c['measurements']['references']['ADDED_CLOSE']['advance_anchor_ATR']),
         number(c['measurements']['references']['LATEST_ELIGIBLE_OPPORTUNITY_CLOSE']['advance_anchor_ATR']),
         number(c['measurements']['current_snapshot'].get('entry_to_stop_ATR')))
        for (aid,_),c in controls.items()]))
    underway += [
        '## What the evidence can identify',
        'At the October 22 cluster, five SHORT transitions have positive directional extension from ADDED (roughly 0.98–2.06 anchor ATR), while the available SHORT control OMER moves adversely (about −0.35 ATR). AAPL advances about 0.71 ATR from ADDED but 1.45 ATR from its prior opportunity assessment; the chosen causal reference matters. T becomes UNDERWAY after about 0.37 ATR from ADDED, while CAT/CDE controls advance about 0.17/0.18 ATR. These are descriptive associations, not independent threshold validation.',
        'A single universal one-ATR rule cannot explain these reports across anchors and directions. The measurable LONG sample is one transition; six SHORT transitions share only two alerts. No balanced classification accuracy, fitted cutoff, causal decision rule or trading edge follows. Current volatility/structure may help formulate future hypotheses, but cannot establish why the source changed state. Newer mostly LONG reports cannot close this gap without their missing daily observations.',
        'SAIL explicitly returns from UNDERWAY to ENTERABLE on October 29 using stop 20.70. This is direct source evidence that eligibility can reopen; absent October 27–29 prices, the price condition motivating the return is unidentified. Actual entries, exits, sizing, execution convention and returns remain unknown.',
        'The original Model E results (4/26 revision directions and 3/26 intervals) remain exploratory failures. This amendment neither changes those targets nor treats source backfill as new prospective success. Future held-out eligibility observations, complete contemporaneous price evidence and explicit forecast registration are needed before evaluating an explanatory rule.',
    ]
    return {'GRIMES_ENTRY_OPPORTUNITIES.md':('\n\n'.join(entry)+'\n').encode(),
            'GRIMES_UNDERWAY_TRANSITIONS.md':('\n\n'.join(underway)+'\n').encode()}
