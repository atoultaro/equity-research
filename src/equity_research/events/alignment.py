"""Regular-session alignment against an independent, frozen exchange schedule."""

from datetime import date, timedelta

from .model import timestamp, revision_key
from ..ingestion.calendar import schedule

ALIGNMENT_VERSION = "regular_session_events_v1"


def event_schedule(events, start, end):
    dates = [start, end] + [e["event_date"] for e in events] + [
        e["effective_date"] for e in events if e["effective_date"] is not None]
    return schedule((date.fromisoformat(min(dates)) - timedelta(days=40)).isoformat(),
                    (date.fromisoformat(max(dates)) + timedelta(days=40)).isoformat())


def align_event(event, calendar):
    rows = calendar["sessions"]
    by_day = {r["session_date"]: r for r in rows}
    day = event["event_date"]
    if not calendar["start"] <= day <= calendar["end"]:
        raise ValueError("event lies outside alignment calendar")
    later = [r["session_date"] for r in rows if r["session_date"] > day]
    if not later:
        raise ValueError("alignment requires a later exchange session")
    current, next_day = by_day.get(day), later[0]
    relation = event["announced_session_relation"]
    relation_verified = event["relation_evidence_status"] == "VERIFIED"
    issues = []
    if event["announced_at"] is not None:
        instant = timestamp(event["announced_at"])
        upper = instant + (timedelta(minutes=1) if event["announced_time_precision"] == "MINUTE" else timedelta())
        if current:
            opening, closing = timestamp(current["opens_at"]), timestamp(current["closes_at"])
            if upper <= opening:
                measured = "BEFORE_OPEN"
                possible = [day]
            elif instant >= closing:
                measured = "AFTER_CLOSE"
                possible = [next_day]
            elif instant >= opening and upper <= closing:
                measured = "DURING_SESSION"
                possible = [day]
            else:
                measured = "UNKNOWN"
                possible = [day, next_day] if upper > closing else [day]
                issues.append("TIMESTAMP_PRECISION_STRADDLES_SESSION_BOUNDARY")
            if relation_verified and relation != "UNKNOWN" and relation != measured:
                issues.append("TIMING_EVIDENCE_CONFLICT")
                possible = sorted(set(possible + [day, next_day]))
            relation = measured
        else:
            relation, possible = "NONTRADING_DAY", [next_day]
    elif not current:
        relation, possible = "NONTRADING_DAY", [next_day]
    elif relation_verified and relation != "UNKNOWN":
        possible = [next_day] if relation == "AFTER_CLOSE" else [day]
    else:
        relation, possible = "UNKNOWN", [day, next_day]
    effective = event["effective_date"]
    effective_session = None
    if effective is not None:
        if effective in by_day:
            effective_session = effective
        else:
            issues.append("EFFECTIVE_DATE_NOT_AN_EXCHANGE_SESSION")
    if event["evidence_status"] == "UNVERIFIED":
        issues.append("UNVERIFIED_EVENT")
    ambiguity = len(possible) != 1 or bool(issues)
    reaction = (possible[0] if not ambiguity else None) if event["event_type"] == "EARNINGS" else effective_session
    return {"revision_key": revision_key(event), "event_id": event["event_id"],
            "announcement_date": day, "announcement_relation": relation,
            "announcement_possible_sessions": possible, "timing_ambiguous": ambiguity,
            "effective_date": effective, "effective_session": effective_session,
            "reaction_session": reaction, "issues": issues,
            "intraday_daily_bar_contaminated": relation == "DURING_SESSION",
            "view": "RETROSPECTIVE_ANNOTATION_NOT_HISTORICAL_KNOWLEDGE"}
