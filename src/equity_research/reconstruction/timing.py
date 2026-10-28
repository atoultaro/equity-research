"""Publication facts stay immutable; candidate execution clocks are hypotheses."""

from datetime import timedelta

from ..models import timestamp


def bounds(alerts):
    result = {}
    for i, alert in enumerate(alerts):
        if alert["published_at"]:
            lower = timestamp(alert["published_at"])
            upper = lower+timedelta(minutes=1) if alert["publication_precision"] == "MINUTE" else lower
            result[alert["alert_id"]] = {"published_at": alert["published_at"],
                "lower": lower.isoformat(), "upper": upper.isoformat(), "kind": "KNOWN_PUBLICATION_PRECISION",
                "assumptions": ["Minute precision uses end-of-minute availability"]}
        else:
            previous = next((a for a in reversed(alerts[:i]) if a["published_at"]), None)
            following = next((a for a in alerts[i+1:] if a["published_at"]), None)
            if not previous or not alert.get("email_received_at"):
                raise ValueError("unknown publication requires a prior dated alert and independent email upper bound")
            lower = timestamp(previous["published_at"])+timedelta(minutes=1)
            upper = timestamp(alert["email_received_at"])
            if following:
                upper = min(upper, timestamp(following["published_at"]))
            if lower >= upper:
                raise ValueError("inconsistent publication interval")
            result[alert["alert_id"]] = {"published_at": None, "lower": lower.isoformat(), "upper": upper.isoformat(),
                "kind": "CONDITIONAL_CHRONOLOGICAL_PUBLICATION_BRACKET",
                "original_display": alert["original_publication_display"],
                "assumptions": ["Source sequence follows chronological publication", "Email receipt bounds content availability, not exact publication"]}
    return result


def clock_variants(alerts, calendar):
    intervals = bounds(alerts)
    unknown = [k for k, v in intervals.items() if v["published_at"] is None]
    if len(unknown) != 1:
        raise ValueError("this bounded pilot requires exactly one unresolved weekly alert")
    weekly = intervals[unknown[0]]
    lower, upper = timestamp(weekly["lower"]), timestamp(weekly["upper"])
    sessions = calendar["sessions"]
    early = next(s for s in sessions if timestamp(s["opens_at"]) > lower)
    late = next(s for s in sessions if timestamp(s["opens_at"]) > upper)
    if timestamp(early["closes_at"]) >= upper:
        raise ValueError("weekly bracket must contain a full candidate session")
    variants = []
    for name, assumed, construction in (
        ("EARLY_BEFORE_FIRST_OPEN", early["opens_at"], weekly["lower"]),
        ("LATE_EMAIL_BOUND", weekly["upper"], weekly["upper"]),
        ("FIRST_SESSION_CLOSE_COMPATIBLE", early["closes_at"], early["opens_at"]),
    ):
        clocks = {k: v["upper"] for k, v in intervals.items()}
        clocks[unknown[0]] = assumed
        variants.append({"name": name, "assumed_action_clocks": clocks,
            "weekly_alert_id": unknown[0], "weekly_construction_cutoff": construction,
            "weekly_first_session": early["session_date"], "weekly_late_session": late["session_date"],
            "publication_bounds": intervals,
            "warning": "Boundary schedules are explicit hypotheses, not inferred precise source timestamps; intraday placement remains unresolved"})
    return variants
