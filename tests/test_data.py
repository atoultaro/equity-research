import csv
import hashlib
import json
from pathlib import Path

import pytest

from equity_research.data import load_dataset
from equity_research.models import Candidate, Config

FIXTURES = Path(__file__).parent / "fixtures"


def inputs(tmp_path, mutate_rows=None, mutate_manifest=None):
    rows = list(csv.DictReader((FIXTURES / "synthetic_daily.csv").open()))
    if mutate_rows:
        mutate_rows(rows)
    path = tmp_path / "data.csv"
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    manifest = json.loads((FIXTURES / "data_manifest.json").read_text())
    manifest["data_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    if mutate_manifest:
        mutate_manifest(manifest)
    meta = tmp_path / "manifest.json"
    meta.write_text(json.dumps(manifest))
    return path, meta


def test_fixture_validates_and_schedule_is_aware(dataset):
    assert len(dataset.bars) == 64
    assert dataset.bars[59].session.session_date.isoformat() == "2026-03-10"
    assert dataset.bars[0].session.opens_at.utcoffset().total_seconds() == 0
    assert dataset.manifest["adjustment"] == "raw"


@pytest.mark.parametrize("field,value", [("close", "nan"), ("high", "inf"), ("volume", "-1"),
                                          ("open", "0"), ("high", "50"), ("low", "999")])
def test_nonfinite_nonpositive_volume_and_inconsistent_prices_fail(tmp_path, field, value):
    data, manifest = inputs(tmp_path, lambda rows: rows[0].update({field: value}))
    with pytest.raises(ValueError):
        load_dataset(data, manifest)


@pytest.mark.parametrize("kind", ["missing", "duplicate", "unordered", "other_symbol"])
def test_security_and_session_completeness_are_not_inferred(tmp_path, kind):
    def mutate(rows):
        if kind == "missing":
            rows.pop(2)
        elif kind == "duplicate":
            rows[2] = dict(rows[1])
        elif kind == "unordered":
            rows[1], rows[2] = rows[2], rows[1]
        else:
            rows[2]["symbol"] = "OTHER"
    data, manifest = inputs(tmp_path, mutate)
    with pytest.raises(ValueError, match="session|security"):
        load_dataset(data, manifest)


@pytest.mark.parametrize("key,value", [("adjustment", "split_adjusted"), ("corporate_actions", [{"type": "split"}]),
                                        ("data_sha256", "0" * 64), ("exchange", "UNKNOWN")])
def test_unsupported_adjustments_actions_and_bad_provenance_fail(tmp_path, key, value):
    data, manifest = inputs(tmp_path, mutate_manifest=lambda m: m.update({key: value}))
    with pytest.raises(ValueError):
        load_dataset(data, manifest)


def test_calendar_early_close_and_availability_order(tmp_path):
    def early_close(meta):
        meta["sessions"][0]["closes_at"] = meta["sessions"][0]["closes_at"].replace("16:00", "13:00")
    data, manifest = inputs(tmp_path, mutate_manifest=early_close)
    assert load_dataset(data, manifest).bars[0].session.closes_at.hour == 18  # winter 13 ET
    meta = json.loads(manifest.read_text())
    meta["sessions"][0]["available_at"] = meta["sessions"][0]["opens_at"]
    manifest.write_text(json.dumps(meta))
    with pytest.raises(ValueError, match="availability"):
        load_dataset(data, manifest)


def test_naive_and_backdated_candidate_times_fail():
    raw = json.loads((FIXTURES / "candidate.json").read_text())
    with pytest.raises(ValueError, match="timezone"):
        Candidate.from_dict(dict(raw, observed_at="2026-03-10T20:15:00"))
    with pytest.raises(ValueError, match="precedes"):
        Candidate.from_dict(dict(raw, available_at="2026-03-10T20:00:00Z"))
    with pytest.raises(ValueError, match="after its observation"):
        Candidate.from_dict(dict(raw, candidate_session="2026-03-11"))


@pytest.mark.parametrize("changes", [{"risk_fraction": 0}, {"sma_period": True}, {"target_r": -1},
                                       {"fees_per_order": -1}, {"initial_equity": "nan"}, {"unknown": 1}])
def test_invalid_policy_inputs_fail(changes):
    with pytest.raises(ValueError):
        Config.from_dict(changes)
