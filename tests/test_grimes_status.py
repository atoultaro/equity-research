"""Readable source facts, with no price or simulated outcome dependency."""

import csv
from io import StringIO
import json
from pathlib import Path

import pytest

from equity_research.ingestion.storage import digest, encode, read_bundle, write_bundle
from equity_research.research_outputs.grimes_status import COLUMNS, alert_date, generate, load_source, render_csv

ROOT = Path(__file__).parents[1]
SOURCE = ROOT / "reports/inputs/grimes-source-ledger-v1"


def rows():
    return list(csv.DictReader(StringIO(render_csv(SOURCE).decode())))


def test_complete_source_episode_inventory_and_columns():
    data = rows()
    assert len(data) == len({r["symbol"] for r in data}) == 26
    assert tuple(data[0]) == COLUMNS == (
        "symbol", "direction", "opened_alert_date", "initial_stop", "latest_reported_stop", "setup_status",
        "reported_position_status", "last_alert_date", "last_reported_action", "dropped_alert_date", "notes")
    assert not {r["symbol"] for r in data} & {"PLTR", "PEP"}
    assert sum(r["reported_position_status"] == "CLOSED" for r in data) == 12
    assert sum(r["reported_position_status"] == "OPEN" for r in data) == 14
    assert all(not any(k.startswith("modeled") for k in r) for r in data)


@pytest.mark.parametrize("symbol,direction,setup,stop", [
    ("CDE", "SHORT", "UNDERWAY", "13.90"), ("EBAY", "LONG", "ENTERABLE", "117.50")])
def test_authoritative_source_open_status_and_latest_stop(symbol, direction, setup, stop):
    r = next(r for r in rows() if r["symbol"] == symbol)
    assert (r["direction"], r["reported_position_status"], r["setup_status"], r["latest_reported_stop"]) == (direction, "OPEN", setup, stop)
    assert r["dropped_alert_date"] == "" and r["last_reported_action"] == "STOP_CHANGED"


def test_unresolved_weekly_dates_are_not_email_or_global_study_dates():
    data = {r["symbol"]: r for r in rows()}
    assert data["CDE"]["last_alert_date"] == "UNKNOWN"
    assert data["EBAY"]["opened_alert_date"] == "UNKNOWN"
    assert data["EBAY"]["last_alert_date"] == "2026-10-26"
    assert data["TEVA"]["dropped_alert_date"] == data["TEVA"]["last_alert_date"] == "UNKNOWN"
    assert data["AAPL"]["dropped_alert_date"] == "2026-10-26"
    assert alert_date("2026-10-27T00:10:00Z") == "2026-10-26"


def test_committed_csv_reproduces_exactly_and_never_overwrites(tmp_path):
    a, b = tmp_path / "a.csv", tmp_path / "b.csv"
    first, second = generate(SOURCE, a), generate(SOURCE, b)
    assert first["sha256"] == second["sha256"]
    assert a.read_bytes() == b.read_bytes() == (ROOT / "reports/grimes_trade_status.csv").read_bytes()
    assert a.read_bytes().count(b"\r\n") == 27
    with pytest.raises(FileExistsError):
        generate(SOURCE, a)


def test_source_projection_retains_provenance_without_subscriber_bodies_or_models():
    episodes, provenance, _ = load_source(SOURCE)
    assert provenance["modeled_results_included"] is False
    assert len(episodes) == 26
    assert all("source_text" not in e["source"] for t in episodes for e in t["events"])
    assert all(len(e["source"]["alert_text_sha256"]) == 64 for t in episodes for e in t["events"])


@pytest.mark.parametrize("change", ["order", "previous_stop", "modeled_field"])
def test_resealed_invalid_action_inventory_is_rejected(tmp_path, change):
    files, _ = read_bundle(SOURCE)
    events = json.loads(files["source-events.json"])
    if change == "order":
        events[0]["source_order"] = 99
    elif change == "previous_stop":
        next(e for e in events if e["type"] == "STOP_CHANGED")["previous_stop"] = "1.00"
    else:
        events[0]["modeled_state"] = "CLOSED"
    files["source-events.json"] = encode(events)
    provenance = json.loads(files["provenance.json"])
    provenance["projected_events_sha256"] = digest(files["source-events.json"])
    files["provenance.json"] = encode(provenance)
    write_bundle(tmp_path / "changed", files)
    with pytest.raises(ValueError):
        render_csv(tmp_path / "changed")
