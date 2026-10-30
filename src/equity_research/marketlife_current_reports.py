"""Readable readiness evidence; stale diagnostics never become current features."""
import json
from .marketlife_reports import table,number


def render(files,public_hash):
    coverage=json.loads(files['market-coverage.json']);gate=json.loads(files['registration-audit.json'])
    source=json.loads(files['source-manifest.json']);manifest=json.loads(files['manifest.json'])
    access=json.loads(files['access-status.json']);ledgers=json.loads(files['source-ledgers.json'])
    latest=coverage['required_latest_completed_session'];rows=coverage['instruments']
    recorded=[r for r in rows if r['identity_status']=='QUALIFIED_RECORDED']
    missing=[r for r in rows if r['identity_status']!='QUALIFIED_RECORDED']
    stale=[r for r in rows if r['missing_sessions']]
    assertion=json.loads(files['source-completeness.json'])
    forecast=json.loads(files['forecast-status.json'])
    provenance=f"Audit as of {coverage['asof']}. Native current archive SHA256: `{manifest['native_archive_sha256']}`. Public evidence SHA256: `{public_hash}`. "
    provenance+='[Input registry](../evidence/pr9d-current-readiness-v1/manifest.json); [regression and replay record](../evidence/pr9d-validation-v1/validation.json).'
    market=[
        '# MarketLife current market-data audit',
        f"Latest eligible completed XNYS session: **{latest}**. This is derived from the actual audit clock using cash Close + 60 minutes, strictly before the cutoff; it is not a permanent October 29 end date. Sixty consecutive sessions are required for each active source setup and SPY.",
        provenance,
        'The required list comes from the latest supplied reconciled ledger, with SPY added as benchmark. It is a conditional source snapshot until completeness is confirmed, not an assumed current universe or complete historical stock population. Historical setup episodes and all opportunity versions remain retained.',
        table(['Symbol','Qualified conId','Primary exchange','Last observed session','Missing required sessions','Last observed ATR14 (stale if older)','ATR session'],[
            (r['symbol'],(r['contract'] or {}).get('conId','MISSING'),(r['contract'] or {}).get('primaryExchange','MISSING'),
             r['latest'] or 'NONE',len(r['missing_sessions']),number(r['last_observed_feature_diagnostic'].get('atr14')),
             r['last_observed_feature_diagnostic'].get('session','UNAVAILABLE')) for r in rows]),
        f"There are {len(recorded)} recorded qualified identities and {len(missing)} missing/incompatible identities. {len(stale)} instruments lack required completed sessions. The machine coverage audit lists every missing date. ATR values from a session older than {latest} are explicitly stale descriptive evidence; no current feature or forecast substitutes them for missing sessions.",
        f"Acquisition status: **{access['acquisition_status']}**. {access['reason']}",
        'The pre-acquisition audit is required before connecting. PR9D specifies a paper-authenticated local TWS with socket clients and Read-Only API enabled. The previous non-paper 7496 confirmation does not establish that current prerequisite. See the access-status record for actual attempts; a missing confirmation is an access/configuration blocker, not evidence that IBKR lacks the requested history.',
        'Existing declared research datasets additionally include a real SPY five-session smoke capture and the SPY market-context panel through October 20; they do not supply October 27–29. The PR9C archive is the broader selected-window baseline through October 26. Synthetic examples are excluded as real evidence. No newly usable current export or newly qualified identity was found in those inspected sources.',
        '## Basis and intake checks',
        'Existing prices use IBKR_TRADES_SPLIT_ADJUSTED_DOCUMENTED and IBKR_NATIVE_UNITS_UNVERIFIED. These are native research conventions, not raw execution prices or verified share volumes. Corporate-action completeness and full historical ticker/listing identity remain UNKNOWN. Qualified conId, STK, USD, SMART, primary exchange and symbol must reconcile; a changed instrument, ambiguous match or inconsistent basis fails.',
        'Native acquisition reuses the pinned ib_async 2.1.0 low-level market-only backend and IBKRDailyProvider. It requests bounded daily TRADES/RTH history, conservatively paces requests, retains raw client returns and safe error diagnostics, and disconnects. It does not request positions, balances, executions or orders. Every imported response is independently normalized from its frozen native bytes. Duplicate, off-calendar, future, malformed and incompatible rows cannot be promoted. Conflicting overlap is retained as a blocker; existing canonical rows are never replaced or rescaled.',
        'Current ATR14, SMA10/20/50, confirmed swings, previous-20 extremes, volatility, compression and relative SPY diagnostics are recomputed by the existing Evidence/Panel/shared-ATR implementation. The registration audit records actual per-symbol availability and feature sessions. A confirmed swing can legitimately be unavailable even with complete observations; absence of a pivot is not a missing-price substitution.',
    ]
    alerts=source['alerts']
    source_report=[
        '# MarketLife source-history completeness',
        provenance,
        f"The retained ledger has **{len(alerts)} alerts, {source['source_actions']} parsed actions and {source['captured_setup_episodes']} captured setup episodes**. No later alert was fabricated or fetched from subscriber-only content. Actual subscriber fills and positions remain UNKNOWN.",
        table(['Alert','Original publication','Precision','Availability lower bound','Availability upper bound'],[
            (a['alert_id'],a['published_at'] or 'UNKNOWN',a['publication_precision'],a['lower'],a['upper']) for a in alerts]),
        'The original weekly publication remains UNKNOWN. October 27–29 retain their operator dates without exact publication times. Source batches keep their original receipt timestamps: appending a later batch cannot widen an earlier date-only bound. The current source view is conditional on these bounds and the original ordering.',
        f"Ordered alert/body manifest SHA256: `{source['alert_manifest_sha256']}`. A matching hash proves agreement with the supplied records, **not completeness of an external MarketLife feed**.",
        f"Completeness assertion status: **{assertion['status']}**. {assertion['interpretation']} This is an operator declaration, not independent feed verification. A failed assertion blocks registration.",
        '## Explicit later-alert intake',
        'Supply a new JSON batch with schema marketlife_operator_alerts_v1, captured_at, and an ordered alerts array. Each alert retains its original complete text and four action sections, unique alert_id, source_reference, source_date, nullable published_at and publication_precision (DATE, MINUTE or SECOND). Original display metadata is retained when supplied. No source content is fetched automatically.',
        'The source command validates the entire chain before sealing a new bundle. It rejects duplicate IDs or duplicate bodies at the same publication evidence, inconsistent old stops, invalid previous eligibility, unsupported lines and reversed chronology. Identical ADDED wording on a later date can be a legitimate new episode after DROPPED; it is not deduplicated merely by text. UNDERWAY suspends entry; a monitored stop update does not reset eligibility; an explicit return creates a fresh version. DROPPED never establishes an executed exit.',
        'Completeness is a separate operator assertion containing complete=true, complete_through=REGISTRATION, the matching alert_manifest_sha256, source_reference, asserted_at and the operator_statement. An absent, future-dated or mismatched assertion blocks readiness. Retain the actual statement and assertion time; the program does not independently verify the subscriber feed. Renew this assertion for the registration being authorized, rather than treating old source captures as current feed completeness.',
    ]
    active=[s for s in ledgers[-1]['setups'] if s['setup_status']=='ACTIVE']
    readiness=[
        '# MarketLife prospective forecast readiness',
        f"Readiness: **{gate['status']}**. Forecast status: **{forecast['status']}**. Required completed session {latest}; declared observed market end {manifest['market_observation_end']}. Source-completeness status: {assertion['status']}; acquisition status: {access['acquisition_status']}.",
        provenance,
        table(['Setup','Direction','Source lifecycle','Entry eligibility','Latest stop'],[
            (s['symbol'],s['direction'],s['setup_status'],s['entry_state'],s['published_stop']) for s in active]),
        'This is the latest supplied source state, conditional on its completeness assertion, not personal brokerage positions. Historical dropped episodes and opportunity versions remain in the machine ledger. SAIL’s original October 29 return to ENTERABLE at 20.70 remains in its immutable opportunity history.',
        table(['Check','Result'],[
            ('Source stop/eligibility chain','PASS on supplied records'),
            ('Source completeness through registration',assertion['status']),
            ('Qualified required identities',f'{len(recorded)} recorded; {len(missing)} missing/incompatible'),
            ('60 consecutive completed current sessions','PASS' if not stale else 'FAIL'),
            ('Current ATR and technical features','FAIL' if any('FEATURE' in p['code'] for p in gate['problems']) else 'PASS'),
            ('Original PR9C gate executed',gate['original_PR9C_gate_executed']),
            ('Original PR9C gate passed',gate['original_PR9C_gate_passed']),
            ('Additional intake/readiness validation',gate['status']),
            ('Operational forecasts written',int(forecast['status']=='REGISTERED_UNRESOLVED'))]),
        'The exact typed failures and per-symbol feature availability are in [registration-audit.json](../evidence/pr9d-current-readiness-v1/registration-audit.json). Nothing weakens the original gate to obtain a forecast. Missing completed observations, incompatible identities/bases, invalid provenance, conflicting historical vintages and source-completeness failures block registration before a prediction directory is created.',
        'The eligibility-persistence baseline and exploratory one-reference-ATR directional-breakout hypothesis remain byte-identical PR9C code. Source-removal and numeric-stop abstentions remain unchanged. This wrapper uses separately labeled conditional information-time views to call that existing implementation for each publication scenario; it never rewrites original publication facts. Tests compare the resulting numerical forecasts with the original implementation, including a date-only reopening. No threshold optimization or new execution convention is introduced.',
        'Operational registration derives its clock internally after independently replaying the current archive. It has no --asof, date override or caller-supplied now argument. It recomputes the latest eligible session again, so a day rollover can invalidate an earlier audit. Complete synthetic fixtures test the successful sealing/replay path but cannot become operational forecasts. Outcomes remain unresolved; no already-available alert is used as a forward target or for retuning.',
        '## Reproduction and next action',
        'See [the PR9D intake commands](../MARKETLIFE_CURRENT_EVIDENCE.md). Current archive and forecast replay rederive semantic outputs from retained parent bytes, source batches and native market proofs; resealing changed derived prices or predictions with valid hashes is rejected. Public reports reproduce from the derived evidence bundle without network access. Full native replay needs the local immutable inputs, which are not published.',
        'A documented blocker is an acceptable result. Resolve the exact failed prerequisites, freeze a new pre-acquisition audit, run the explicitly confirmed bounded intake, then build a new immutable archive version. Only a PASS at the actual registration clock may create a forecast. Original PR9C artifacts, forecasts, source records and the October 26 CSV remain unchanged. There are no orders, account queries, new vendors, subscriptions, CI changes or automatic merge.',
    ]
    return dict(zip(('MARKETLIFE_CURRENT_DATA_AUDIT.md','MARKETLIFE_SOURCE_COMPLETENESS.md','MARKETLIFE_PROSPECTIVE_READINESS.md'),
        (('\n\n'.join(parts)+'\n').encode() for parts in (market,source_report,readiness))))
