"""Source-reported status only; modeled lifecycle outputs are never read here."""

import csv
from io import StringIO
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from ..ingestion.storage import digest, encode, read_bundle, write_bundle
from ..lifecycle import source as source_interpreter
from ..models import number, timestamp

PR16_BUNDLE_SHA256 = "4ce1b1f021d666bb870983cf894628c665992f97186e6e2740ccd2f4e69b2604"
COLUMNS = (
    "symbol", "direction", "opened_alert_date", "initial_stop", "latest_reported_stop",
    "setup_status", "reported_position_status", "last_alert_date", "last_reported_action",
    "dropped_alert_date", "notes",
)


def capture_source(study, output):
    """Validate PR16 in full, then publish only the requested action facts."""
    from ..lifecycle.study import load_study
    checked = load_study(study)
    if checked["hashes"]["bundle_sha256"] != PR16_BUNDLE_SHA256:
        raise ValueError("the agreed frozen PR16 study-v5 is required")
    original = checked["files"]["source_events.json"]
    events = json.loads(original)
    for event in events:
        # Exact subscriber alert bodies remain private in the original study.
        del event["source"]["source_text"]
    provenance = {
        "schema_version": "grimes_source_status_input_v1",
        "source_study_bundle_sha256": PR16_BUNDLE_SHA256,
        "source_events_sha256": digest(original),
        "projected_events_sha256": digest(encode(events)),
        "source_interpreter_sha256": digest(Path(source_interpreter.__file__).read_bytes()),
        "projection": "Original parsed source events, omitting only source.source_text",
        "modeled_results_included": False,
        "expected_episodes": 26, "expected_actions": 72,
        "publication_date_policy": "Use published_at only; unknown stays UNKNOWN; never use email/effective clocks",
    }
    return write_bundle(output, {"source-events.json": encode(events), "provenance.json": encode(provenance)})


def load_source(path):
    files, hashes = read_bundle(path)
    provenance = json.loads(files["provenance.json"])
    if (set(files) != {"source-events.json", "provenance.json"}
            or provenance["schema_version"] != "grimes_source_status_input_v1"
            or provenance["source_study_bundle_sha256"] != PR16_BUNDLE_SHA256
            or provenance["source_interpreter_sha256"] != digest(Path(source_interpreter.__file__).read_bytes())
            or provenance["projected_events_sha256"] != digest(files["source-events.json"])
            or provenance["modeled_results_included"] is not False):
        raise ValueError("source projection provenance mismatch")
    events = json.loads(files["source-events.json"])
    if (len(events) != 72 or provenance["expected_actions"] != 72 or provenance["expected_episodes"] != 26
            or [e["source_order"] for e in events] != list(range(72))
            or len({e["event_id"] for e in events}) != 72):
        raise ValueError("complete ordered 72-action source inventory required")
    allowed = {"attribution", "direction", "effective_at", "effective_clock", "event_id", "publication_display",
               "published_at", "source", "source_order", "stop", "symbol", "type", "previous_stop",
               "setup_availability", "reported_underway"}
    for event in events:
        if set(event) - allowed or event["attribution"] != "EXPERT_REPORTED":
            raise ValueError("only parsed source facts are accepted")
        if event["type"] not in source_interpreter.SECTIONS.values():
            raise ValueError("unknown source action")
        if "stop" in event and number(event["stop"]) <= 0:
            raise ValueError("positive reported stop required")
        if event["published_at"] is not None:
            timestamp(event["published_at"])
    episodes, _, _ = source_interpreter.reconstruct(events)
    if len(episodes) != 26 or len({e["symbol"] for e in episodes}) != 26:
        raise ValueError("one episode per stock in this fixed study required")
    return episodes, provenance, hashes


def alert_date(published_at):
    if published_at is None:
        return "UNKNOWN"
    return timestamp(published_at).astimezone(ZoneInfo("America/New_York")).date().isoformat()


def render_csv(source):
    episodes, _, _ = load_source(source)
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=COLUMNS, lineterminator="\r\n")
    writer.writeheader()
    for episode in sorted(episodes, key=lambda e: e["trade_id"]):
        last = episode["events"][-1]
        notes = [f"Source episode {episode['trade_id']}; last action {last['event_id']}; actual fills unknown"]
        if last["published_at"] is None:
            notes.append(f"Unresolved source publication: {last['publication_display']}")
        if episode["position_state"] == "OPEN":
            notes.append("No source-reported DROPPED action by study end")
        writer.writerow({
            "symbol": episode["symbol"], "direction": episode["direction"],
            "opened_alert_date": alert_date(episode["opened_at"]),
            "initial_stop": episode["initial_stop"], "latest_reported_stop": episode["current_stop"],
            "setup_status": episode["setup_availability"], "reported_position_status": episode["position_state"],
            "last_alert_date": alert_date(last["published_at"]), "last_reported_action": last["type"],
            "dropped_alert_date": alert_date(episode["closed_at"]) if episode["position_state"] == "CLOSED" else "",
            "notes": "; ".join(notes),
        })
    return stream.getvalue().encode("utf-8")


def generate(source, output):
    content = render_csv(source)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as handle:
        handle.write(content)
    return {"rows": 26, "sha256": digest(content), "output": str(output)}
