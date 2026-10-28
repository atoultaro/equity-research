"""Synthetic source proofs exercise real-pilot mechanics, never historical claims."""

from datetime import UTC, datetime
import json

import pytest

from equity_research.history.depth_store import freeze_report
from equity_research.ingestion.storage import read_bundle
from equity_research.research_outputs.observed_universe import capture_inputs, freeze_pilot, read_inputs, observed_snapshots
from equity_research.universe import SecurityMaster, ResearchPanel
from test_ibkr_depth import Fake, auditor


@pytest.fixture(scope="module")
def captured(tmp_path_factory):
    root = tmp_path_factory.mktemp("observed-universe-synthetic")

    class Broker(Fake):
        async def qualify(self, security):
            self.con_id = {"AAPL": 101, "META": 102}[security.symbol]
            return await super().qualify(security)

        async def historical(self, contract, params):
            rows = await super().historical(contract, params)
            return [r for r in rows if not (contract.conId == 102 and str(r.date) == "2024-05-14")]

    instruments = [{"kind": "stock", "security": {"symbol": symbol, "security_id": f"synthetic:{symbol}",
        "reference": "synthetic fixture only", "ibkr_symbol": symbol, "yahoo_symbol": symbol,
        "primary_exchange": "NASDAQ", "listing_venue": "XNAS"}} for symbol in ("AAPL", "META")]
    cfg = {"schema_version": "ibkr_depth_config_v1", "start": "2024-01-02", "end": "2024-06-28",
           "window_days": 365, "instruments": instruments}
    auditor(Broker(head="2024-01-02"), clock=lambda: datetime(2024, 7, 2, tzinfo=UTC)).run(cfg, root / "audit")
    seal = freeze_report(root / "audit", root / "audit-report")
    config = {"schema_version": "observed_universe_config_v1", "origin": "SYNTHETIC", "base_commit": "0"*40,
        "inventory_start": "2024-01-02", "pilot_start": "2024-01-02", "end": "2024-06-28", "calendar_end": "2024-07-03",
        "selection_months": ["2024-04", "2024-05"], "top_n": 1,
        "cycles": [{"label": "fixture", "start": "2024-01-02", "end": "2024-06-28"}],
        "sources": [{"path": str(root / "audit-report"), "bundle_sha256": seal["bundle_sha256"], "symbols": ["AAPL", "META"]}]}
    capture_inputs(config, root / "inputs")
    freeze_pilot(root / "inputs", root / "pilot")
    return root


def test_observed_windows_are_not_strictly_admitted_members(captured):
    files, _ = read_bundle(captured / "pilot/report")
    r = json.loads(files["report.json"])
    assert r["origin"] == "SYNTHETIC" and r["survivorship_bias_free"] is False
    assert r["pilot_stock_count"] == 2
    assert r["missing_historical_securities_count"] is None
    assert r["observed_snapshots"][1]["observed_contracts"] == 2
    assert all(s["members"] == 0 and s["pit_quality"] == "PIT_UNVERIFIED" for group in r["universe_admission"].values() for s in group)
    assert all("UNADMITTED_LIQUIDITY_BASIS" in s["exclusion_counts"] for s in r["universe_admission"]["reconstruction"])
    inventory = json.loads(files["coverage.json"])
    meta = next(r for r in inventory if r["capture_symbol"] == "META")
    assert meta["missing_internal_count"] == 1 and meta["missing_internal_sessions"] == ["2024-05-14"]
    assert meta["cycles"][0]["observed_sessions"] == meta["cycles"][0]["expected_sessions"] - 1


def test_missing_expected_sessions_remain_missing_and_identity_fields_unknown(captured):
    root = captured / "pilot"
    master, panel = SecurityMaster(root / "security_master"), ResearchPanel(root / "research_panel")
    snapshots = observed_snapshots(master, panel, ["2024-05"])
    meta = next(r for r in snapshots[0]["records"] if r["capture_symbol"] == "META")
    assert meta["observed_window_sessions"] == 59 and meta["missing_window_sessions"] == ["2024-05-14"]
    assert meta["complete_60_session_native_window"] is False and meta["historical_symbol"] is None
    fact = master.by_id["ibkr:conid:102"][0]
    assert all(fact[k] is None for k in ("symbol", "issuer_id", "share_class_id", "listing_start", "known_at", "exchange", "security_type"))
    rows = panel.observations("ibkr:conid:102")
    assert all(r["price_basis"] == "SPLIT_ADJUSTED" and r["volume_basis"] == "VENDOR_UNVERIFIED" for r in rows)
    assert all(r["known_at"] is None and r["available_at"] is None for r in rows)
    assert panel.rows_as_of("ibkr:conid:102", "2024-06-01T00:00:00Z") == []


def test_frozen_inputs_replay_to_identical_bundles_and_output_is_exclusive(captured, tmp_path):
    seal = freeze_pilot(captured / "inputs", tmp_path / "replay")
    assert seal == read_bundle(captured / "pilot/report")[1]
    for component in ["security_master", "research_panel", "strict_universe", "reconstruction_universe"]:
        assert (tmp_path / "replay" / component / "hashes.json").read_bytes() == (captured / "pilot" / component / "hashes.json").read_bytes()
    with pytest.raises(FileExistsError):
        freeze_pilot(captured / "inputs", tmp_path / "replay")


def test_synthetic_proofs_cannot_be_relabelled_real_and_native_tampering_fails(captured):
    files, _ = read_bundle(captured / "inputs")
    config = json.loads(files["config.json"])
    config["origin"] = "RECORDED"
    files["config.json"] = json.dumps(config).encode()
    with pytest.raises(ValueError, match="must not be mixed"):
        read_inputs(files)
    files, _ = read_bundle(captured / "inputs")
    proofs = json.loads(files["source-proofs.json"])
    name = next(k for k in proofs[0]["files"] if k.endswith("returned_frame.json"))
    proofs[0]["files"][name] = "{}"
    files["source-proofs.json"] = json.dumps(proofs).encode()
    with pytest.raises(ValueError, match="hash mismatch"):
        read_inputs(files)


def test_overlapping_source_versions_are_not_silently_spliced(captured):
    files, _ = read_bundle(captured / "inputs")
    config, proofs = json.loads(files["config.json"]), json.loads(files["source-proofs.json"])
    config["sources"] *= 2
    proofs *= 2
    files["config.json"], files["source-proofs.json"] = json.dumps(config).encode(), json.dumps(proofs).encode()
    with pytest.raises(ValueError, match="revisions must not be silently combined"):
        read_inputs(files)
