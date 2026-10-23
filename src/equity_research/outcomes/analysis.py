"""Dependence diagnostics and descriptive summaries; no fitted thresholds or tests."""

from collections import Counter, defaultdict
from decimal import Context, localcontext
from statistics import mean, median

from .model import CLOSE, OPEN
from ..ingestion.storage import digest, encode
from ..models import number, timestamp


def context_descriptor(link):
    if link['status'] == 'UNAVAILABLE': return 'UNAVAILABLE'
    return link.get('context', {}).get('descriptive_state') or 'UNDESCRIBED'


def cluster_signals(inputs, config):
    observations = []
    for source in inputs:
        days = [r["session_date"] for r in source.calendar["sessions"]]
        for s in source.signals:
            start = days.index(s["trigger"]["session_date"])
            eligible = next((i for i in range(start+1,len(days)) if timestamp(source.calendar["sessions"][i]["opens_at"]) > timestamp(s["trigger"]["available_at"])), None)
            ends = [start+h for h in config.close_horizons]
            if config.open_horizons and eligible is not None: ends += [eligible+h for h in config.open_horizons]
            end = min(max([start]+ends),len(days)-1)
            observations.append({"signal_id":s["signal_id"],"security_id":s["security_id"],"symbol":s["symbol"],
                "strategy_id":s["strategy_id"],"signal_session":days[start],"observation_window_end":days[end],
                "calendar_coverage_truncated":bool(ends and max(ends)>=len(days)),
                "setup_id":s["setup"]["setup_id"],"setup_type":s["setup"]["setup_type"],
                "attempt_session":s["setup"]["session_date"],"boundary":s["setup"]["boundary"],
                "same_session_cluster_id":"session:"+digest(encode([s["security_id"],days[start]]))})
    grouped=defaultdict(list)
    for r in observations:grouped[r["security_id"]].append(r)
    for security,rows in grouped.items():
        rows.sort(key=lambda r:(r["signal_session"],r["signal_id"]))
        components=[]
        for r in rows:
            if not components or r["signal_session"]>max(x["observation_window_end"] for x in components[-1]):components.append([])
            components[-1].append(r)
        for component in components:
            cid="event:"+digest(encode([security,sorted(r["signal_id"] for r in component)]))
            for r in component:
                r["event_cluster_id"]=cid
                r["overlapping_signal_ids"]=sorted(o["signal_id"] for o in rows if o is not r and
                    o["signal_session"]<=r["observation_window_end"] and r["signal_session"]<=o["observation_window_end"])
    return sorted(observations,key=lambda r:r["signal_id"])


def _stats(values):
    if not values:return {"count":0,"mean":None,"median":None,"population_stddev":None,"positive":0,"negative":0,"zero":0}
    values=list(map(number,values));average=mean(values)
    return {"count":len(values),"mean":str(average),"median":str(median(values)),
            "population_stddev":str(mean((v-average)**2 for v in values).sqrt()),
            "positive":sum(v>0 for v in values),"negative":sum(v<0 for v in values),"zero":sum(v==0 for v in values)}


def _group(rows, clusters, minimum):
    valid=[r for r in rows if r["forward_return_pct"] is not None]
    clean=[r for r in valid if not r["corporate_action_uncertainty"]["comparability_review_required"]]
    eventids={clusters[r["signal_id"]]["event_cluster_id"] for r in rows}
    availableids={clusters[r["signal_id"]]["event_cluster_id"] for r in valid}
    return {"sample_count":len(rows),"available_outcome_count":len(valid),"missing_outcome_count":len(rows)-len(valid),
        "fully_available_outcome_count":sum(r["outcome_status"]=="AVAILABLE" for r in rows),
        "partial_atr_count":sum(r["outcome_status"]=="PARTIAL" for r in rows),
        "raw_return_pct":_stats([r["forward_return_pct"] for r in valid]),
        "direction_normalized_return_pct":_stats([r["direction_normalized_return_pct"] for r in valid]),
        **{key+"_median":str(median([number(r[key]) for r in valid if r[key] is not None])) if any(r[key] is not None for r in valid) else None
           for key in ("mfe_pct","mae_pct","mfe_atr","mae_atr")},
        "signal_cluster_count":len(eventids),"available_cluster_count":len(availableids),
        "same_session_cluster_count":len({clusters[r["signal_id"]]["same_session_cluster_id"] for r in rows}),
        "missing_reason_counts":dict(sorted(Counter(reason for r in rows for reason in r["unavailable_reasons"]).items())),
        "known_action_overlap_count":sum(bool(r["corporate_action_uncertainty"]["known_effective_actions"]) for r in rows),
        "bounded_action_uncertainty_count":sum(bool(r["corporate_action_uncertainty"]["bounded_overlap_uncertainty"]) for r in rows),
        "sensitivity_excluding_known_or_bounded_actions":{"available_count":len(clean),
            "direction_normalized_return_pct":_stats([r["direction_normalized_return_pct"] for r in clean])},
        "warnings":["DEPENDENT_SIGNALS_NOT_INDEPENDENT_TRIALS","NATIVE_PRICE_AND_EVENT_ARCHIVE_LIMITATIONS"]+
            (["INSUFFICIENT_EVENT_CLUSTERS"] if len(availableids)<minimum else [])}


def summarize(outcomes,links,clusters,comparisons,config):
    with localcontext(Context(prec=28)):
        return _summarize(outcomes,links,clusters,comparisons,config)


def _summarize(outcomes,links,clusters,comparisons,config):
    bylink={r["link_sha256"]:r for r in links};bycluster={r["signal_id"]:r for r in clusters}
    keys=("strategy_id","symbol","security_id","direction","reference_type","horizon")
    summaries={}
    for mode in ("by_stock_strategy","by_context"):
        groups=defaultdict(list)
        for row in outcomes:
            link=bylink[row["market_context_link_sha256"]]
            key=tuple(row[k] for k in keys)
            if mode=="by_context":key+=(context_descriptor(link),link["status"])
            groups[key].append(row)
        names=keys+(("context_descriptor","context_availability_status") if mode=="by_context" else ())
        summaries[mode]=[{**dict(zip(names,k)),**_group(rows,bycluster,config.minimum_clusters)} for k,rows in sorted(groups.items())]
    grouped=defaultdict(list)
    for r in comparisons:grouped[(r["strategy_id"],r["symbol"],r["direction"],r["signal_close_horizon"])].append(r)
    summaries["same_signal_same_endpoint_reference_comparisons"]=[{
        **dict(zip(("strategy_id","symbol","direction","signal_close_horizon"),k)),"sample_count":len(rows),
        "paired_available_count":sum(r["status"]=="AVAILABLE" for r in rows),
        "entry_gap_pct_on_paired_set":_stats([r["entry_gap_pct"] for r in rows if r["status"]=="AVAILABLE"]),
        "close_reference_return_pct_on_paired_set":_stats([r["close_reference_return_pct"] for r in rows if r["status"]=="AVAILABLE"]),
        "open_reference_return_pct_on_paired_set":_stats([r["open_reference_return_pct"] for r in rows if r["status"]=="AVAILABLE"]),
        "direction_normalized_close_minus_open_pct":_stats([r["direction_normalized_difference_pct"] for r in rows if r["status"]=="AVAILABLE"]),
        "interpretation":"SAME_SIGNALS_AND_ENDPOINTS; open offsets explicit in comparison rows; no fill claim"}
        for k,rows in sorted(grouped.items())]
    # Strategy contrasts share horizons/references/security, not purported paired
    # signal dates or directions. Keep both direction labels and sample counts.
    contrasts=defaultdict(list)
    for r in summaries["by_stock_strategy"]:contrasts[(r["symbol"],r["reference_type"],r["horizon"])].append({
        k:r[k] for k in ("strategy_id","direction","sample_count","available_outcome_count","available_cluster_count","direction_normalized_return_pct")})
    summaries["unpaired_strategy_comparisons"]=[{"symbol":k[0],"reference_type":k[1],"horizon":k[2],"groups":v,
        "interpretation":"UNPAIRED_POPULATIONS_AT_MATCHED_REFERENCE_AND_HORIZON; no significance or causal interpretation"} for k,v in sorted(contrasts.items())]
    summaries["dependence"]={"raw_signal_count":len(clusters),"event_cluster_count":len({r["event_cluster_id"] for r in clusters}),
        "same_session_cluster_count":len({r["same_session_cluster_id"] for r in clusters}),
        "signals_with_overlaps":sum(bool(r["overlapping_signal_ids"]) for r in clusters),
        "minimum_clusters_warning_threshold":config.minimum_clusters,
        "interpretation":"Closed-window connected components per security, across strategies; clusters may still share market/time dependence"}
    return summaries
