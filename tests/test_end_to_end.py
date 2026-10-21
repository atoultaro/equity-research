import hashlib
import csv
import json
from pathlib import Path

import pytest

from equity_research.cli import main
from equity_research.reporting import canonical, run_experiment, shared_identity
from equity_research.reporting import code_identity

FIXTURES = Path(__file__).parent / "fixtures"
REVISION = "a" * 40  # explicitly labeled user-supplied test revision, never an observed Git SHA


def run(output, candidate=None, data=None, manifest=None):
    return run_experiment(data or FIXTURES / "synthetic_daily.csv", candidate or FIXTURES / "candidate.json",
                          FIXTURES / "swing_config.json", manifest or FIXTURES / "data_manifest.json", output,
                          source_commit=REVISION)


def test_identical_inputs_produce_byte_identical_artifacts_and_verified_hashes(tmp_path):
    run(tmp_path / "one")
    run(tmp_path / "two")
    first = {p.relative_to(tmp_path / "one"): p.read_bytes() for p in (tmp_path / "one").rglob("*") if p.is_file()}
    second = {p.relative_to(tmp_path / "two"): p.read_bytes() for p in (tmp_path / "two").rglob("*") if p.is_file()}
    assert first == second
    hashes = json.loads(first[Path("artifact_hashes.json")])
    for name, expected in hashes["files"].items():
        assert hashlib.sha256(first[Path(name)]).hexdigest() == expected
    assert hashes["canonical_bundle_sha256"] == hashlib.sha256(canonical(hashes["files"])).hexdigest()
    metadata = json.loads(first[Path("run_manifest.json")])
    assert metadata["shared_dependency"]["source_commit"] == "57fc6c30836d13a7fcfc3c1a9b6b496fe472d555"
    assert metadata["code"]["revision_origin"] == "user_supplied"
    assert first[Path("inputs/data.csv")] == (FIXTURES / "synthetic_daily.csv").read_bytes()


def test_existing_run_cannot_be_overwritten(tmp_path):
    target = tmp_path / "unique"
    run(target)
    original = (target / "result.json").read_bytes()
    with pytest.raises(FileExistsError):
        run(target)
    assert (target / "result.json").read_bytes() == original


def test_expired_candidate_has_machine_readable_no_trade_artifacts(tmp_path):
    with (FIXTURES / "synthetic_daily.csv").open() as handle:
        rows = list(csv.DictReader(handle))[:63]
    for row in rows[60:]:
        row.update(open="129", high="130", low="128", close="129")
    data = tmp_path / "unfilled.csv"
    with data.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    manifest = json.loads((FIXTURES / "data_manifest.json").read_text())
    manifest["sessions"] = manifest["sessions"][:63]
    manifest["data_sha256"] = hashlib.sha256(data.read_bytes()).hexdigest()
    meta = tmp_path / "unfilled_manifest.json"
    meta.write_text(json.dumps(manifest))
    result = run(tmp_path / "expired", data=data, manifest=meta)
    assert result["status"] == "EXPIRED"
    saved = json.loads((tmp_path / "expired/result.json").read_text())
    assert saved["trade"] is None and saved["fills"] == []
    assert saved["order"]["status"] == "EXPIRED"
    assert len((tmp_path / "expired/trade_ledger.csv").read_text().splitlines()) == 1


def test_rejected_and_empty_runs_still_write_research_records(tmp_path):
    raw = json.loads((FIXTURES / "candidate.json").read_text())
    raw["provenance"] = {}
    candidate = tmp_path / "unproven.json"
    candidate.write_text(json.dumps(raw))
    assert run(tmp_path / "rejected", candidate=candidate)["status"] == "REJECTED"
    assert len((tmp_path / "rejected/trade_ledger.csv").read_text().splitlines()) == 1
    data = tmp_path / "empty.csv"
    data.write_text("symbol,session_date,open,high,low,close,volume\n")
    meta = json.loads((FIXTURES / "data_manifest.json").read_text())
    meta["sessions"] = []
    meta["data_sha256"] = hashlib.sha256(data.read_bytes()).hexdigest()
    manifest = tmp_path / "empty_manifest.json"
    manifest.write_text(json.dumps(meta))
    assert run(tmp_path / "empty", data=data, manifest=manifest)["status"] == "WATCH"
    assert (tmp_path / "empty/artifact_hashes.json").is_file()


def test_shared_artifact_identity_is_pinned():
    pin = json.loads((FIXTURES.parents[1] / "vendor/SHARED_SOURCE.json").read_text())
    assert shared_identity()["wheel_sha256"] == pin["wheel_sha256"]
    wheel = FIXTURES.parents[1] / "vendor" / pin["wheel"]
    assert hashlib.sha256(wheel.read_bytes()).hexdigest() == pin["wheel_sha256"]


def test_offline_cli_and_repeat_output_error(tmp_path, capsys):
    args = ["run", "--data", str(FIXTURES / "synthetic_daily.csv"),
            "--candidate", str(FIXTURES / "candidate.json"), "--config", str(FIXTURES / "swing_config.json"),
            "--manifest", str(FIXTURES / "data_manifest.json"), "--output", str(tmp_path / "cli"),
            "--source-commit", REVISION]
    assert main(args) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "COMPLETED"
    assert main(args) == 2
    assert "exist" in capsys.readouterr().err.lower()


def test_revision_from_checkout_and_explicit_requirement_outside_git(tmp_path, monkeypatch):
    identity = code_identity(None)
    assert len(identity["source_commit"]) == 40
    assert identity["revision_origin"] == "checkout"
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ValueError, match="source-commit"):
        code_identity(None)
