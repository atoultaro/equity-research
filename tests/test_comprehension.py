"""Offline descriptive research: synthetic provider returns, no TWS or sockets."""

from copy import deepcopy
from datetime import UTC, datetime
from decimal import Decimal
import json
from pathlib import Path

import pytest

from equity_research.cli import main
from equity_research.comprehension.features import Panel, metric, setup, stop_analysis
from equity_research.comprehension.inputs import freeze_inputs, read_inputs, validate_observations
from equity_research.comprehension.study import classify_event, derive, freeze_study, load_study
from equity_research.comprehension.futures import import_es
from equity_research.history.depth_store import freeze_report
from equity_research.ingestion.storage import digest, encode, read_bundle, write_bundle
from test_ibkr_depth import Fake, auditor

OBSERVATIONS = Path(__file__).parents[1] / "experiments/grimes-20261026-observations-v1.json"
SYMBOLS = ("SAIL", "SLB", "GE", "SCCO", "SPY", "QQQ", "RSP", "IWM", "XLK")
IDS = {s: 1000+i for i, s in enumerate(SYMBOLS)}


@pytest.fixture(scope="module")
def captured(tmp_path_factory):
    root = tmp_path_factory.mktemp("expert-synthetic")

    class Broker(Fake):
        async def qualify(self, security):
            self.con_id = IDS[security.symbol]
            return await super().qualify(security)

    mappings = [{"kind": "stock" if s in SYMBOLS[:4] else "market_etf", "security": {
        "symbol": s, "security_id": f"synthetic:{s}", "reference": "synthetic expert test only",
        "ibkr_symbol": s, "yahoo_symbol": s, "primary_exchange": "ARCA", "listing_venue": "ARCX"}} for s in SYMBOLS]
    config = {"schema_version": "ibkr_depth_config_v1", "start": "2025-01-02", "end": "2026-10-26",
        "window_days": 1825, "instruments": mappings}
    broker = Broker(head="2020-01-02")
    auditor(broker, clock=lambda: datetime(2026, 10, 27, 1, tzinfo=UTC)).run(config, root / "audit")
    assert broker.disconnected
    freeze_report(root / "audit", root / "audit-report")
    spec = {"schema_version": "expert_research_inputs_v1", "analysis_start": "2025-01-02",
        "observations": json.loads(OBSERVATIONS.read_bytes()), "classifications": [], "event_evidence": [],
        "es_context": {"status": "NOT_AVAILABLE", "reason": "Synthetic fixture has no futures"}}
    for s in SYMBOLS[:4]:
        spec["classifications"].append({"symbol": s, "con_id": IDS[s], "issuer_identity": f"Synthetic {s}",
            "source_url": "https://example.org/synthetic-classification", "source_document_date": "2025-01-02",
            "effective_date": None, "evidence": "Synthetic test assertion only", "sector": "SYNTHETIC", "industry": "SYNTHETIC",
            "sector_proxy": "XLK", "sector_proxy_con_id": IDS["XLK"], "industry_proxy": None,
            "proxy_limitations": "Synthetic fixture; no real classification or historical membership"})
    freeze_inputs(spec, [(root / "audit-report", list(SYMBOLS))], root / "inputs")
    files, hashes = read_bundle(root / "inputs")
    return root, files, hashes, read_inputs(files)


def test_four_original_new_positions_and_unknown_execution():
    obs = json.loads(OBSERVATIONS.read_bytes())
    validate_observations(obs)
    assert [(r["symbol"], r["action"], r["direction"], r["reported_stop"]) for r in obs["recommendations"]] == [
        ("SAIL", "OPEN_NEW_POSITION", "LONG", "20.90"), ("SLB", "OPEN_NEW_POSITION", "LONG", "51.10"),
        ("GE", "OPEN_NEW_POSITION", "SHORT", "295.80"), ("SCCO", "OPEN_NEW_POSITION", "SHORT", "191.70")]
    assert " ".join(r["original_recommendation"] for r in obs["recommendations"]) == obs["original_source_text"]
    for action in ("ADDED", "INCREASE_EXISTING_POSITION"):
        changed = deepcopy(obs)
        changed["recommendations"][0]["action"] = action
        with pytest.raises(ValueError, match="new-position"):
            validate_observations(changed)
    changed = deepcopy(obs)
    changed["recommendations"][0]["entry_price"] = "21.00"
    with pytest.raises(ValueError, match="unknown execution"):
        validate_observations(changed)


@pytest.mark.parametrize("direction,stop,signed,side", [("LONG", "95", "5", "CONVENTIONAL"),
    ("SHORT", "106", "6", "CONVENTIONAL"), ("LONG", "105", "-5", "UNEXPECTED"), ("SHORT", "94", "-6", "UNEXPECTED")])
def test_stop_distances_hand_checked(direction, stop, signed, side):
    f = {k: metric(100.0) for k in ("close", "prior20_high", "prior20_low", "sma20", "sma50", "sma200", "confirmed_swing_high", "confirmed_swing_low")}
    f["atr14"] = metric(2.0)
    result = stop_analysis({"direction": direction, "reported_stop": stop}, f)
    assert Decimal(result["signed_protective_distance"]) == Decimal(signed)
    assert Decimal(result["absolute_distance"]) == abs(Decimal(signed))
    assert Decimal(result["fraction_of_reference_close"]) == abs(Decimal(signed))/100
    assert Decimal(result["atr_normalized_distance"]) == abs(Decimal(signed))/2
    assert result["side_assessment"].startswith(side)
    assert result["actual_entry"] is None and result["actual_initial_risk"] is None
    assert result["reference_is_actual_entry"] is False


def test_source_frames_replayed_and_reports_reproduced(captured, tmp_path):
    root, _, _, (spec, prices, coverage, calendar) = captured
    assert all(coverage[s]["origin"] == "synthetic" for s in SYMBOLS)
    assert all(prices[s][-1]["session_date"] == "2026-10-26" for s in SYMBOLS)
    first = freeze_study(root / "inputs", tmp_path / "study")
    loaded = load_study(tmp_path / "study")
    assert first == loaded["hashes"]
    assert main(["expert", "replay", "--study", str(tmp_path / "study"), "--output", str(tmp_path / "replay")]) == 0
    assert read_bundle(tmp_path / "replay")[1] == first
    assert all(f"dossier-{s}.md" in loaded["files"] for s in SYMBOLS[:4])
    with pytest.raises(FileExistsError):
        freeze_study(root / "inputs", tmp_path / "study")


def test_semantic_corruption_resealed_outputs_rejected(captured, tmp_path):
    freeze_study(captured[0] / "inputs", tmp_path / "original")
    files, _ = read_bundle(tmp_path / "original")
    data = json.loads(files["stock_features.json"])
    data["SAIL"]["features"]["close"]["value"] = 99999
    files["stock_features.json"] = encode(data)
    write_bundle(tmp_path / "resealed", files)
    with pytest.raises(ValueError, match="semantic output mismatch"):
        load_study(tmp_path / "resealed")


def test_resealed_input_cannot_change_native_frame_or_contract(captured):
    _, files, _, _ = captured
    for target in ("returned_frame.json", "event.json"):
        altered = deepcopy(files)
        proofs = json.loads(altered["source-proofs.json"])
        key = next(k for k in proofs[0]["files"] if k.endswith(target) and "checkpoint-" in k)
        proofs[0]["files"][key] += " "
        altered["source-proofs.json"] = encode(proofs)
        with pytest.raises(ValueError, match="source proof hash mismatch"):
            read_inputs(altered)


def test_future_poison_does_not_enter_cutoff(captured):
    spec, prices, info, calendar = deepcopy(captured[3])
    original = derive(spec, prices, info, calendar)
    for s in prices:
        row = deepcopy(prices[s][-1])
        row.update(session_date="2026-10-27", close="999999", price_basis="FUTURE_POISON")
        prices[s].append(row)
    assert derive(spec, prices, info, calendar) == original
    spec["observations"]["analysis_cutoff"] = "2026-10-26T16:30:00-04:00"
    with pytest.raises(ValueError, match="unavailable"):
        derive(spec, prices, info, calendar)


def test_missing_sessions_fail_features_never_forward_fill(captured):
    spec, prices, info, calendar = deepcopy(captured[3])
    del prices["SAIL"][-2]
    result = derive(spec, prices, info, calendar)
    f = result["stock_features.json"]["SAIL"]["features"]
    assert f["close"]["status"] == "AVAILABLE"
    assert f["return20"]["status"] == "UNAVAILABLE"
    assert f["atr14"]["status"] == "UNAVAILABLE"
    assert len(result["data_coverage.json"]["SAIL"]["missing_expected_sessions"]) == 1
    prices["SAIL"] = prices["SAIL"][:-1]
    result = derive(spec, prices, info, calendar)
    assert result["stop_analysis.json"]["SAIL"]["status"] == "UNAVAILABLE"


def test_historical_snapshots_use_their_own_cutoffs(captured):
    spec, prices, info, calendar = deepcopy(captured[3])
    before = derive(spec, prices, info, calendar)
    # A valid but extreme final bar changes the present; it must not change
    # any market snapshot from five or more sessions ago.
    prices["SPY"][-1].update(open="1000", high="1100", low="900", close="1001")
    after = derive(spec, prices, info, calendar)
    a, b = (r["market_context.json"]["proxies"]["SPY"] for r in (before, after))
    assert a["0"] != b["0"]
    assert all(a[str(n)] == b[str(n)] for n in (5, 20, 60, 120))


def test_source_contract_alias_collision_rejected(captured):
    # Change a source selection, rather than just a derived membership field.
    files = deepcopy(captured[1])
    proofs = json.loads(files["source-proofs.json"])
    proofs.append(deepcopy(proofs[0]))
    files["source-proofs.json"] = encode(proofs)
    with pytest.raises(ValueError, match="multiple source identities"):
        read_inputs(files)


@pytest.mark.parametrize("field,value", [("price_basis", "RAW"), ("volume_basis", "SHARES_VERIFIED"), ("security_id", "other-issuer")])
def test_basis_and_identity_incompatibility_rejected(captured, field, value):
    spec, prices, info, calendar = deepcopy(captured[3])
    prices["SAIL"][-1][field] = value
    with pytest.raises(ValueError, match="incompatibility"):
        derive(spec, prices, info, calendar)


@pytest.mark.parametrize("mutation", ["missing", "ambiguous", "wrong_identity", "future_evidence"])
def test_missing_or_ambiguous_classification_not_inferred(captured, mutation):
    spec, prices, info, calendar = deepcopy(captured[3])
    if mutation == "missing":
        spec["classifications"] = []
    elif mutation == "ambiguous":
        spec["classifications"].append(deepcopy(spec["classifications"][0]))
    elif mutation == "wrong_identity":
        spec["classifications"][0]["con_id"] += 1
    else:
        spec["classifications"][0]["source_document_date"] = "2026-10-27"
    result = derive(spec, prices, info, calendar)
    assert result["sector_context.json"]["SAIL"]["classification"]["status"] == "UNKNOWN_OR_AMBIGUOUS"
    assert result["stock_features.json"]["SAIL"]["relative_strength"]["sector"]["20"]["status"] == "UNAVAILABLE"


def test_missing_proxy_and_absent_es_are_explicit(captured):
    spec, prices, info, calendar = deepcopy(captured[3])
    del prices["XLK"], info["XLK"]
    result = derive(spec, prices, info, calendar)
    assert result["market_context.json"]["es_context"]["status"] == "NOT_AVAILABLE"
    assert result["sector_context.json"]["SAIL"]["contexts"]["sector"]["status"] == "NOT_AVAILABLE"
    assert result["stock_features.json"]["SAIL"]["features"]["close"]["value"] == 101


@pytest.mark.parametrize("stamp,precision,evidence,expected", [(None, "DATE", "VERIFIED", "UNKNOWN_OR_MISSING"),
    ("2026-10-26T16:00:00-04:00", "SECOND", "UNKNOWN", "UNKNOWN_OR_MISSING"),
    ("2026-10-26T16:59:00-04:00", "MINUTE", "VERIFIED", "RETROSPECTIVE_ONLY"),
    ("2026-10-26T16:58:00-04:00", "MINUTE", "VERIFIED", "VERIFIED_PRE_DECISION"),
    ("2026-10-27T08:00:00-04:00", "SECOND", "VERIFIED", "RETROSPECTIVE_ONLY")])
def test_publication_evidence_not_retrieval_clock(stamp, precision, evidence, expected):
    event = {"published_at": stamp, "publication_precision": precision, "publication_evidence_status": evidence,
        "captured_at": "2026-10-28T01:00:00Z", "publication_evidence": "Synthetic timestamp proof"}
    assert classify_event(event, "2026-10-26T17:00:00-04:00")["availability_category"] == expected


def test_heuristic_ambiguity_not_forced(captured):
    spec, prices, info, calendar = captured[3]
    f = Panel(prices, info, calendar, spec["observations"]["analysis_cutoff"]).features("SAIL", "2026-10-26")
    assert setup(f)["classification"] == "OTHER_OR_UNCERTAIN"
    f["breakout20"]["value"] = True
    f["close_sma50"]["value"] = .1
    f["close_sma200"]["value"] = .2
    f["sma50_sma200"]["value"] = .1
    assert len(setup(f)["candidates"]) == 2
    assert setup(f)["classification"] == "OTHER_OR_UNCERTAIN"


def test_opposing_setup_is_preserved_as_a_contradiction(captured):
    spec, prices, info, calendar = deepcopy(captured[3])
    # An isolated new High with a return below the prior boundary, against
    # a flat background, is bearish geometry even for a reported LONG.
    prices["SAIL"][-1]["high"] = "103"
    result = derive(spec, prices, info, calendar)
    inferred = result["stock_features.json"]["SAIL"]["inferred_setup"]
    assert inferred["classification"] == "FAILED_BREAKOUT_OR_BEARISH_REVERSAL"
    assert inferred["direction_consistency"] == "OPPOSES_REPORTED_DIRECTION"


def test_shared_math_and_calendar_windows_hand_checked(captured):
    spec, prices, info, calendar = captured[3]
    panel = Panel(prices, info, calendar, spec["observations"]["analysis_cutoff"])
    f = panel.features("SAIL", "2026-10-26")
    assert f["sma200"]["value"] == 101
    assert f["atr14"]["value"] == 3
    assert f["realized_volatility20"]["value"] == 0
    assert f["return20"]["value"] == 0
    assert panel.relative("SAIL", "SPY", "2026-10-26", 60)["value"] == 0
    assert f["atr14"]["last_session"] == "2026-10-26"
    assert len(panel.window("SAIL", "2026-10-26", 15)[0]) == 15


def test_trending_fixture_levels_slopes_and_momentum_hand_checked(captured):
    spec, prices, info, calendar = deepcopy(captured[3])
    for i, row in enumerate(prices["SAIL"][-250:]):
        close = 100+i
        row.update(open=str(close), high=str(close+2), low=str(close-1), close=str(close), volume="1000")
    f = Panel(prices, info, calendar, spec["observations"]["analysis_cutoff"]).features("SAIL", "2026-10-26")
    assert f["sma20"]["value"] == 339.5
    assert f["sma50"]["value"] == 324.5
    assert f["sma200"]["value"] == 249.5
    assert f["sma20_slope20"]["value"] == pytest.approx(339.5/319.5-1)
    assert f["return20"]["value"] == pytest.approx(349/329-1)
    assert f["return60"]["value"] == pytest.approx(349/289-1)
    assert f["atr14"]["value"] == 3
    assert f["range20_fraction"]["value"] == pytest.approx(22/349)
    assert f["mean_dollar_volume20_native"]["value"] == 339500


def test_optional_es_import_requires_verified_metadata_and_contracts(tmp_path):
    csv = b"timestamp,contract_id,open,high,low,close,volume\n2026-10-26T09:30:00-04:00,123,100,102,99,101,10\n"
    cal = {"sessions": [{"session_date": "2026-10-26", "opens_at": "2026-10-26T09:30:00-04:00", "closes_at": "2026-10-26T09:35:00-04:00"}]}
    meta = {"schema_version": "verified_es_import_v1", "verified": True, "source_sha256": digest(csv), "bar_minutes": 5,
        "contract_identities": {"123": {"root": "ES", "expiry": "202612", "exchange": "CME"}},
        "identity_evidence": "Synthetic proof", "roll_methodology": "one explicit contract", "roll_evidence": "Synthetic proof",
        "session_hours": "NY cash schedule", "timezone": "America/New_York", "price_adjustment": "UNADJUSTED_CONTRACT_PRICES",
        "adjustment_evidence": "Synthetic proof", "analysis_cutoff": "2026-10-26T17:00:00-04:00"}
    for path, data in ((tmp_path / "source.csv", csv), (tmp_path / "meta.json", encode(meta)), (tmp_path / "cal.json", encode(cal))):
        path.write_bytes(data)
    import_es(tmp_path / "source.csv", tmp_path / "meta.json", tmp_path / "cal.json", tmp_path / "import")
    files, _ = read_bundle(tmp_path / "import")
    assert json.loads(files["daily_cash_context.json"])[0]["contract_id"] == "123"
    assert json.loads(files["quality.json"])["returns_computed"] is False
    meta["verified"] = False
    (tmp_path / "meta.json").write_bytes(encode(meta))
    with pytest.raises(ValueError, match="requires verified"):
        import_es(tmp_path / "source.csv", tmp_path / "meta.json", tmp_path / "cal.json", tmp_path / "blocked")
    assert not (tmp_path / "blocked").exists()
