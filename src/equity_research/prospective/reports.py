"""Human-readable projections of sealed predictions and evaluations."""
from datetime import datetime
from collections import Counter
from zoneinfo import ZoneInfo
from .models import MODELS

ET=ZoneInfo('America/New_York')


def clock(value):
    return datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(ET).isoformat() if value else 'UNKNOWN'


def num(value):return '—' if value is None else f'{value:.4f}' if isinstance(value,(float,int)) else str(value)


def table(headers,rows):
    return ['| '+' | '.join(headers)+' |','| '+' | '.join('---' for _ in headers)+' |']+[
        '| '+' | '.join(str(v).replace('|','/') for v in row)+' |' for row in rows]


def walk_report(result):
    lines=['# Grimes walk-forward evaluation — PR9C','',
        '**This is a retrospective dry run, with zero fresh out-of-sample observations.** The original seven alerts informed '
        'the hypotheses in PR16–PR20. Enforced feature cutoffs do not undo that hypothesis-selection contamination. '
        'These results validate the forecasting workflow and expose counterexamples; they do not establish prospective skill.','',
        'Each forecaster subprocess receives only a frozen prefix view. The preparer seals its prediction before releasing the '
        'next original alert into a separate reveal bundle. Known dated alerts use a pre-alert completed-bar cutoff; '
        'publication metadata is used retrospectively to define that experimental schedule. For the unknown weekly publication, '
        'the cutoff is the prior alert’s upper availability bound, with no Friday market bars admitted. '
        'Those are explicit historical design choices, not a claim that the researcher scheduled live forecasts before these alerts.','',
        '## Fixed decision hypotheses','']
    lines+=table(['Model','Frozen decision rule','Important limit'],[
        ['A','Intraday stop touch → hypothetical exit; next relevant source action predicted DROP','Next-Open activation assumption and exit→newsletter-DROP bridge are unverified'],
        ['B','Closing violation → idealized closing decision/exit','A recovered intraday touch is insufficient; exact closing execution is not guaranteed'],
        ['C','Closing violation → irrevocable next-Open exit commitment','A source alert before that Open can still continue management; an evening revision cannot cancel the commitment'],
        ['D','One next-Open review; retain only if Open protects against then-known stop','Only one discretionary retention per episode; second violation queues unconditional exit'],
        ['E','Fixed ATR/structure stop proposals and directional-progress UNDERWAY condition','Opening-reference ATR progress is not actual initial risk or +1R; no fitted probabilities']])
    lines+=['','A–D predict a broad continuation set when still hypothetically active. Set coverage is reported separately from '
        'point-category correctness; a three-category set is not credited as a correct exact action. None predicts stop levels. '
        'Pending C/D forecasts include predeclared publication-time branches. Evaluation resolves those branches from timing '
        'metadata, never by choosing the action or clock that fits. D stays unresolved when the required next Open is absent.','',
        '## Descriptive comparisons','',
        'All rows within one alert share a cluster. The three timing schedules are sensitivity cases, never independent samples. '
        'The tables show trade-level descriptives and six shared-alert-cluster outcomes. A cluster with both compatible and '
        'contradictory trade forecasts is a contradiction for the strict all-trades cluster check. '
        'Discriminating wins/losses use disjoint forecast sets selected without inspecting actual action categories; '
        'conditional branches use only publication metadata. Mixed distinguishing clusters are retained as mixed.','']
    rows=[]
    for summary in result['summaries']:
        for model in MODELS:
            s=summary['models'][model]
            rows.append([summary['timing_scenario'],model,
                f"{s['point_category_correct']}/{s['point_category_denominator']}",
                f"{s['set_coverage_correct']}/{s['set_coverage_denominator']}",
                f"{s['stop_direction_correct']}/{s['stop_direction_denominator']}",
                f"{s['changed_stop_direction_correct']}/{s['changed_stop_direction_denominator']}",
                num(s['mean_absolute_stop_error_ATR']),f"{s['stop_interval_hits']}/{s['stop_interval_denominator']}",
                s['abstentions_or_unresolved']])
    lines+=table(['Clock','Model','Exact action correct','Action-set coverage','Stop direction','Direction on actual stop revisions','Mean abs stop error / forecast ATR','Interval hits','Abstain/unresolved'],rows)
    categories=Counter(r['actual_source_observation']['category'] for c in result['cases'] for r in c['evaluation']['source_observations'])
    revisions=sum(r['actual_source_observation']['stop'] is not None for c in result['cases'] for r in c['evaluation']['source_observations'])
    lines+=['',f"The {sum(categories.values())} trade/alert observations contain "+', '.join(f'{n} {k}' for k,n in sorted(categories.items()))+
        f"; there are {revisions} actual stop revisions. These observations share only {len(result['cases'])} alerts. "
        'Class frequencies matter: a no-mention forecast can be correct without reproducing a management decision.','']
    lines+=['','Stop errors use the ATR frozen at prediction, and include wrong-direction predictions where a numeric level was '
        'offered. Missing levels remain abstentions, not zero error. Direction accuracy includes NO_ADJUSTMENT, so the '
        'actual-revision-only denominator is shown separately. No significance tests or calibrated probabilities are reported.','']
    rows=[]
    for summary in result['summaries']:
        for model in MODELS:
            s=summary['models'][model];c=s['shared_cluster_outcomes'];d=s['distinguishing_cluster_outcomes']
            rows.append([summary['timing_scenario'],model,
                f"{c['NO_CONTRADICTION_OBSERVED']} / {c['HAS_CONTRADICTION']} / {c['NO_EVALUABLE_FORECAST']}",
                f"{s['distinguishing_wins']} / {s['distinguishing_losses']}",
                f"{d['SUPPORTED_ONLY']} / {d['CONTRADICTED_ONLY']} / {d['MIXED']} / {d['NO_DISTINGUISHING_RESULT']}"])
    lines+=table(['Clock','Model','Shared clusters: compatible / contradiction / unresolved','Discriminating trade wins / losses','Discriminating clusters: support / contradict / mixed / none'],rows)
    lines+=['','## Every historical prediction (LATE timing sensitivity)','',
        'S = supports that frozen source-action prediction; C = contradicts it; U = abstained or unresolved. '
        'These labels test the **combined entry assumption, price rule and newsletter-reporting bridge**, not verified broker execution. '
        'In the A–D columns, CONTINUATION covers continued stop management, UNDERWAY and omission; it excludes explicit DROP. '
        'A conditional ABSTAIN→action annotation reflects the publication-time branch sealed before reveal.','']
    for case in result['cases']:
        p,e=case['prediction'],case['evaluation']
        lines += [f"### {case['case_id']} → {e['actual_alert']['alert_id']}",'',
            f"Information cutoff: **{clock(case['cutoff'])}**. Available source prefix: {', '.join(a['alert_id'] for a in p['known_alerts'])}. "
            f"Market end: **{p['market_observation_end']}**. Expected window ends {clock(p['target']['deadline'])}. "
            f"Actual source publication: **{clock(e['actual_alert']['published_at'])}**; eligibility `{e['eligibility']}`. "
            f"Sealed prediction `{case['prediction_sha256']}`; evaluation `{case['evaluation_sha256']}`.",'']
        rows=[]
        for trade in p['predictions']:
            sc=next(s for s in trade['scenarios'] if s['timing_scenario']=='LATE')
            actual=next(r for r in e['source_observations'] if r['trade_id']==trade['trade_id'])
            evaluated=next(s for s in actual['scenarios'] if s['timing_scenario']=='LATE')
            labels=[]
            for model in MODELS:
                original=next(m for m in sc['models'] if m['model']==model)
                out=next(m for m in evaluated['models'] if m['model']==model)
                label=out['predicted_action']
                if original['action']!=label:label=original['action']+'→'+label+' (time branch)'
                labels.append(label)
            structure=sc['models'][-1]
            source=trade['source_state'];obs=actual['actual_source_observation']
            verdict='/'.join('S' if m['verdict']=='SUPPORTS_PREDICTION' else 'C' if m['verdict']=='CONTRADICTS_PREDICTION' else 'U' for m in evaluated['models'])
            rows.append([trade['symbol'],source['setup_availability']+' / '+source['current_stop'],*labels[:4],
                labels[-1]+f"; {structure['stop_direction']}; {num(structure['stop_point'])}; {structure['stop_interval']}",
                obs['category']+'; '+obs['stop_direction']+' '+num(obs['stop']),verdict])
        lines+=table(['Episode','Source setup / stop at cutoff','A','B','C','D','E: action; stop direction; point; interval','Next source observation','A/B/C/D/E'],rows)+['']
    lines += ['## Interpretation and falsification','',
        'CLMT, TEVA and GME are diagnostic repetitions of known intraday-touch/recovery cases. The pre-alert forecasts can '
        'distinguish A’s DROP expectation from recovered-close continuation under B–D, but this is not new independent evidence '
        'because those cases motivated the rules. EBAY’s already-known adverse Close remains the important counterexample: '
        'A/B expect DROP under the assumed active exposure, while pending C/D can still permit a same-evening revision before '
        'the next Open. Calling that earlier revision a failed committed exit would be a chronology error.','',
        'CDE is a target-management control. The models impose no mandatory full +1R exit; this historical replay cannot retest '
        'a target policy they do not contain. E uses directional movement from a pre-alert reference Close divided by its then-known '
        'ATR, not an inferred entry or actual initial risk. Its UNDERWAY result and any stop-level misses are evaluated separately.','',
        'Model E is deliberately small and falsifiable: a confirmed pivot can be too remote to reproduce a rapid stop ratchet. '
        'A correct UNDERWAY call does not excuse a wrong stop direction/level, and a broad continuation set is not exact prediction '
        'of a particular stop revision. We do not revise thresholds after seeing these dry-run scores.','',
        'For future discrimination, retain the next Open and the stop known before that Open. A protective Open after an evening '
        'revision, followed by continued source management, distinguishes C’s irrevocable commitment from D’s one permitted review. '
        'An intraday recovery with continued management separates A from B conditional on the entry/reporting bridge. '
        'If every model predicts continuation, that alert supplies no discriminating test.','',
        'See [method and CLI](../GRIMES_PROSPECTIVE_PREDICTION_METHOD.md), [sealed next-alert forecast](GRIMES_NEXT_ALERT_PREDICTIONS.md), '
        'and [machine-readable evaluations](../evidence/pr9c-walk-forward-v1/walk-forward.json).','']
    late=next(s for s in result['summaries'] if s['timing_scenario']=='LATE')['models']
    b,e=late['B_CLOSE_CONFIRMATION'],late['E_PRICE_STRUCTURE']
    findings=[
        f"Under LATE timing, B covers {b['set_coverage_correct']}/{b['set_coverage_denominator']} source-action outcomes, "
        f"but {b['shared_cluster_outcomes']['HAS_CONTRADICTION']} shared alerts still contain counterexamples. "
        'This supports some conditional closing-confirmation explanations while rejecting a claim that this fixed model reproduces the whole source process.',
        f"E correctly predicts only {e['changed_stop_direction_correct']}/{e['changed_stop_direction_denominator']} offered directions on actual revisions; "
        f"its numerical intervals cover {e['stop_interval_hits']}/{e['stop_interval_denominator']} offered levels. "
        'The simple structure rule therefore fails to reproduce most numeric stop-management decisions, despite some correct action calls. '
        'A correct CDE UNDERWAY call does not repair its stop forecast.']
    cd_same=all(next(m for m in s['models'] if m['model']=='C_NEXT_OPEN')['predicted_action']==next(m for m in s['models'] if m['model']=='D_BOUNDED_REVIEW')['predicted_action']
        for c in result['cases'] for r in c['evaluation']['source_observations'] for s in r['scenarios'])
    if cd_same:findings.append('C and D produce identical resolved source-action forecasts on these historical observations. '
        'They remain indistinguishable here; their future next-Open obligations still differ. Equal scores do not identify the actual stop convention.')
    position=lines.index('## Interpretation and falsification')+2
    lines[position:position]=sum(([text,''] for text in findings),[])
    return '\n'.join(lines)


def next_report(prediction,hashes):
    p=prediction
    lines=['# Grimes next-alert predictions — PR9C','',
        '**Unevaluated forward registration.** No genuine later source alert has been imported or scored. '
        'The target is a complete alert published strictly after registration, not an already-past October27 alert. '
        'The predictor uses the last verified seven-alert ledger and October26 market observations; these are stale inputs, '
        'not a claim about current broker positions or today’s market.','',
        f"Registered: **{clock(p['registered_at'])}**. Information cutoff: **{clock(p['information_cutoff'])}**. "
        f"Last admitted market session: **{p['market_observation_end']}**. Target deadline: **{clock(p['target']['deadline'])}** "
        '(five following XNYS sessions). All displayed clocks are America/New_York; machine artifacts retain aware timestamps.','',
        f"Prediction bundle SHA256: `{hashes['bundle_sha256']}`. "
        f"Unobserved completed sessions between market end and registration: {', '.join(p['unobserved_completed_sessions_since_market_end']) or 'none'}. "
        'No missing price is forward filled. All confidences are LOW_HEURISTIC_NOT_A_CALIBRATED_PROBABILITY.','',
        '## Predictions for every source-open episode','',
        'The source OPEN/ENTERABLE/UNDERWAY columns are authoritative as of the information cutoff. '
        'A predicted DROP is a hypothesis about a later report, never an alteration to that ledger. '
        'CONTINUATION is a broad set including omission, continued management or UNDERWAY. '
        'ABSTAIN can carry a predeclared time/next-Open condition; it is not a conveniently correct forecast.','']
    rows=[]
    for trade in p['predictions']:
        sc=next(s for s in trade['scenarios'] if s['timing_scenario']=='LATE');source=trade['source_state']
        labels=[next(m['action'] for m in sc['models'] if m['model']==model) for model in MODELS]
        e=sc['models'][-1]
        rows.append([trade['symbol'],source['direction'],source['position_state']+' / '+source['setup_availability'],
            source['current_stop'],*labels[:4],labels[-1]+'; '+e['stop_direction']+f"; {num(e['stop_point'])}; {e['stop_interval']}",
            'yes' if all(trade['action_stable_across_scenarios'].values()) else 'no; see JSON'])
    lines+=table(['Episode','Direction','Source status','Reported stop','A','B','C','D','E: action; direction; level; interval','All model actions timing-stable?'],rows)
    lines+=['','## Price-structure evidence and conditions','']
    rows=[]
    for trade in p['predictions']:
        e=next(s for s in trade['scenarios'] if s['timing_scenario']=='LATE')['models'][-1]
        features=e.get('features',{})
        rows.append([trade['symbol'],e.get('feature_session'),num(features.get('close',{}).get('value')),
            num(features.get('atr14',{}).get('value')),num(features.get('sma20',{}).get('value')),
            num(features.get('sma50',{}).get('value')),num(e.get('progress_ATR')),e.get('level_source','—'),'; '.join(e['reasons']) or 'Fixed no-change baseline'])
    lines+=table(['Episode','Feature session','Close','ATR14','SMA20','SMA50','Opening-reference progress / ATR','Stop anchor','Reason'],rows)
    lines+=['','CDE remains source **SHORT / OPEN / UNDERWAY /13.90** and EBAY remains source '
        '**LONG / OPEN / ENTERABLE /117.50**. Hypothetical A/B closure for EBAY never replaces those source facts. '
        'For EBAY, C’s prior Close-breach commitment survives a later stop revision. D needs the missing next Open versus the '
        'then-known stop to decide whether its one permitted review retains exposure. That absence is unresolved evidence, '
        'not proof that D is correct.','',
        'The newly added SAIL/SLB/GE/SCCO episodes have no observed post-alert entry session in these inputs. '
        'A–D abstain rather than fabricate entries or future stop touches. E’s no-change projection is a low-confidence '
        'source-management hypothesis from pre-alert structure.','',
        '## Reveal protocol','',
        'Supply the original complete later alert and displayed publication metadata through the offline reveal command. '
        'A fresh score also needs an explicit operator attestation that it is the next complete alert after registration '
        'and that the source chain since the known ledger is complete. Missing attestations, unknown publication, '
        'window-boundary ambiguity or an outside-window alert remain unresolved or ineligible. '
        'Earlier October27–28 alerts, if they exist, may be imported as non-scoring backfill and advanced into a new history '
        'before a new forecast is sealed. They cannot be relabeled as outcomes of this forward registration.','',
        'Append evaluation to a new immutable directory. Do not update this forecast, its outcome field, or prior source artifacts. '
        'A later evaluation references the original prediction hash; observations and model results remain separate. '
        'No subscriber fetch, broker connection, order placement, account query or scheduled monitor is part of this workflow.','',
        'See [method and CLI](../GRIMES_PROSPECTIVE_PREDICTION_METHOD.md), '
        '[sealed prediction](../evidence/pr9c-next-alert-v1/prediction.json) and '
        '[validation record](../evidence/pr9c-validation-v1/validation.json).','']
    return '\n'.join(lines)
