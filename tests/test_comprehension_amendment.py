"""PR15 amendment: attribution, horizon arithmetic and non-executable 1R policy."""

from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path

import pytest

from equity_research.comprehension.amendment import es_context, return_verification
from equity_research.comprehension.features import Panel, metric, setup, stop_analysis
from equity_research.comprehension.inputs import PRICE_BASIS, VOLUME_BASIS
from equity_research.comprehension.methodology import management, one_r, validate_methodology
from equity_research.comprehension.study import derive, freeze_study, load_study
from equity_research.ingestion.calendar import schedule
from equity_research.ingestion.storage import encode, read_bundle, write_bundle
from test_comprehension import captured, OBSERVATIONS

ROOT = Path(__file__).parents[1]
METHOD = ROOT / "experiments/grimes-current-methodology-v1.json"
AMENDMENT = ROOT / "experiments/grimes-20261026-amendment-v1.json"


def return_fixture():
    calendar = schedule("2026-09-28", "2026-10-27")
    prices = []
    # Synthetic intervening observations. Three endpoints are frozen IBKR
    # arithmetic anchors; this is NOT a replacement real-price dataset.
    anchors = {"2026-09-28": "736.53", "2026-10-23": "704.40", "2026-10-26": "712.20"}
    for i, session in enumerate(calendar["sessions"]):
        d = session["session_date"]
        close = anchors.get(d, str(720+i))
        prices.append(dict(session_date=d, open=close, high=str(Decimal(close)+1), low=str(Decimal(close)-1),
            close=close, volume="1000", price_basis=PRICE_BASIS, volume_basis=VOLUME_BASIS,
            provider="ibkr", symbol="QQQ", security_id="synthetic:QQQ", source_row={"file": "synthetic", "row": i}))
    info = {"QQQ": {"security": {"security_id": "synthetic:QQQ"}, "price_basis": PRICE_BASIS,
        "volume_basis": VOLUME_BASIS, "source_bundle_sha256": "0"*64}}
    return {"QQQ": prices}, info, calendar


def test_daily_and_trailing_returns_have_distinct_horizons_and_weekend_alignment():
    prices, info, calendar = return_fixture()
    panel = Panel(prices, info, calendar, "2026-10-26T17:00:00-04:00")
    features = panel.features("QQQ", "2026-10-26")
    assert features["daily_return"]["first_session"] == "2026-10-23"
    assert features["daily_return"]["last_session"] == "2026-10-26"
    assert features["daily_return"]["value"] == pytest.approx(712.2/704.4-1)
    assert features["return_20d"]["first_session"] == "2026-09-28"
    assert features["return_20d"]["value"] == pytest.approx(712.2/736.53-1)
    assert features["daily_return"]["value"] > 0 > features["return_20d"]["value"]
    for key, n in (("daily_return", 1), ("return_5d", 5), ("return_20d", 20), ("return_60d", 60)):
        assert features[key]["horizon_sessions"] == n
        assert features[key]["required_observations"] == n+1
    assert features["return_60d"]["status"] == "UNAVAILABLE"
    evidence = json.loads(AMENDMENT.read_bytes())
    checks = return_verification(panel, prices, "2026-10-26", info, evidence)["QQQ"]
    assert all(v["status"] == "APPROXIMATION_CONSISTENT" for v in checks.values())
    assert Decimal(checks["daily_return"]["calculated_percent"]) == (Decimal("712.20")/Decimal("704.40")-1)*100
    assert checks["daily_return"]["first_close"] == "704.40"
    assert checks["return_20d"]["first_close"] == "736.53"


def test_return_discrepancy_never_replaces_frozen_prices():
    prices, info, calendar = return_fixture()
    panel = Panel(prices, info, calendar, "2026-10-26T17:00:00-04:00")
    evidence = json.loads(AMENDMENT.read_bytes())
    evidence["QQQ_return_observations"]["daily_return_percent"] = "99"
    check = return_verification(panel, prices, "2026-10-26", info, evidence)["QQQ"]["daily_return"]
    assert check["status"] == "DISCREPANCY_REQUIRES_REVIEW"
    assert check["last_close"] == "712.20"
    assert float(check["calculated_percent"]) == pytest.approx(1.1073253833)


def test_missing_daily_bar_and_future_poisoning():
    prices, info, calendar = return_fixture()
    future = prices["QQQ"][-1]
    future.update(close="FUTURE_POISON", price_basis="FUTURE_POISON")
    panel = Panel(prices, info, calendar, "2026-10-26T17:00:00-04:00")
    expected = panel.features("QQQ", "2026-10-26")
    assert expected["daily_return"]["value"] == pytest.approx(712.2/704.4-1)
    prices["QQQ"] = [r for r in prices["QQQ"] if r["session_date"] != "2026-10-23"]
    f = Panel(prices, info, calendar, "2026-10-26T17:00:00-04:00").features("QQQ", "2026-10-26")
    assert f["daily_return"]["status"] == "UNAVAILABLE"
    assert f["return_5d"]["status"] == "UNAVAILABLE"
    assert f["return_20d"]["status"] == "UNAVAILABLE"
    assert f["close"]["value"] == 712.2


@pytest.mark.parametrize("direction,entry,stop,target", [("LONG", "21.75", "20.90", "22.60"),
    ("LONG", "53.08", "51.10", "55.06"), ("SHORT", "288.43", "295.80", "281.06"),
    ("SHORT", "186.01", "191.70", "180.32")])
def test_hypothetical_1r_targets_hand_checked(direction, entry, stop, target):
    assert one_r(direction, entry, stop)["target_1R"] == target
    assert one_r(direction, None, stop) == {"original_per_share_risk": None, "target_1R": None}
    obs = dict(direction=direction, entry_price=None, execution_timestamp=None, quantity=None, reported_stop=stop)
    result = management(obs, float(entry), json.loads(METHOD.read_bytes()), scenario=True)
    assert result["actual_target"] is None and result["actual_entry"] is None
    scenario = result["reference_scenario"]
    assert scenario["hypothetical_1R_target"] == target
    assert scenario["reference_entry_basis"] == "OCT_26_CLOSE"
    assert scenario["is_actual_execution"] is False and scenario["actual_target"] is None
    assert result["observed_trade_specific_exit_instruction"] is None and result["executed_exits"] is None


@pytest.mark.parametrize("direction,entry,stop", [("LONG", "95", "100"), ("LONG", "100", "100"),
    ("SHORT", "105", "100"), ("SHORT", "100", "100")])
def test_nonpositive_reference_r_is_refused(direction, entry, stop):
    with pytest.raises(ValueError, match="must be positive"):
        one_r(direction, entry, stop)


def test_operator_methodology_preserves_full_short_and_minimum_long_unknowns():
    method = validate_methodology(json.loads(METHOD.read_bytes()))
    assert method["source_status"] == "OPERATOR_REPORTED" and method["independently_verified"] is False
    assert method["SHORT"]["exact_exit_fraction_of_original"] == "1"
    assert method["SHORT"]["remaining_fraction"] == "0" and method["SHORT"]["runner_policy"] == "NO_RUNNER"
    assert method["LONG"]["minimum_exit_fraction_of_original"] == "1/3"
    assert method["LONG"]["exact_exit_fraction_of_original"] is None
    assert method["LONG"]["remaining_fraction"] is None
    assert all(method["LONG"][k] is None for k in ("subsequent_stop_adjustments", "final_exit_rules", "remaining_exit_timing"))
    method["LONG"]["exact_exit_fraction_of_original"] = "1/3"
    with pytest.raises(ValueError, match="unknown management"):
        validate_methodology(method)


@pytest.mark.parametrize("direction,stop,nearest,include,exclude", [("SHORT", "106", "confirmed_swing_low", "confirmed_swing_high", "confirmed_swing_low"),
    ("LONG", "95", "confirmed_swing_high", "confirmed_swing_low", "confirmed_swing_high")])
def test_numerically_nearest_is_not_automatically_directional_invalidation(direction, stop, nearest, include, exclude):
    numbers = dict(close=100, atr14=2, prior20_high=112, prior20_low=90, sma20=97, sma50=104, sma200=108,
        confirmed_swing_high=110 if direction == "SHORT" else 94.9,
        confirmed_swing_low=105.9 if direction == "SHORT" else 92)
    f = {k: metric(float(v)) for k, v in numbers.items()}
    analysis = stop_analysis({"direction": direction, "reported_stop": stop}, f)
    assert analysis["nearest_numerical_technical_level"]["name"] == nearest
    candidates = {v["name"]: v for v in analysis["directional_invalidation_candidates"]}
    assert include in candidates and exclude not in candidates
    assert candidates[include]["stop_on_expected_protective_side"] is False
    assert all(c["candidate_role"] == ("SUPPORT" if direction == "LONG" else "RESISTANCE") for c in candidates.values())
    assert all(c["attribution"] == "RESEARCH_HYPOTHESIS" for c in candidates.values())


def test_continuation_without_fresh_20_session_breakdown_and_second_leg_unresolved(captured):
    spec, prices, info, calendar = deepcopy(captured[3])
    f = Panel(prices, info, calendar, spec["observations"]["analysis_cutoff"]).features("GE", "2026-10-26")
    for name in ("close_sma50", "sma50_slope20", "return20"):
        f[name]["value"] = -.1
    f["breakdown20"]["value"] = False
    hypotheses = setup(f)
    assert hypotheses["intended_expert_setup"] is None
    assert hypotheses["researcher_diagnostics"]["legacy_bearish_breakdown"] is False
    by_name = {h["interpretation"]: h for h in hypotheses["hypotheses"]}
    assert by_name["TREND_CONTINUATION"]["status"] == "CONSISTENT_WITH_DIAGNOSTIC"
    assert by_name["POTENTIAL_SECOND_LEG_AFTER_IMPULSE"]["status"] == "UNRESOLVED"
    assert by_name["FAILED_RALLY_OR_FAILED_BREAKOUT"]["status"] == "UNRESOLVED"


@pytest.mark.parametrize("kind,field,pivot,extreme", [("resistance_rejection", "high", "110", "111"),
    ("support_rejection", "low", "90", "89")])
def test_rejection_requires_a_preexisting_confirmed_pivot(captured, kind, field, pivot, extreme):
    spec, prices, info, calendar = deepcopy(captured[3])
    prices["SAIL"][-8][field] = pivot
    prices["SAIL"][-1][field] = extreme
    f = Panel(prices, info, calendar, spec["observations"]["analysis_cutoff"]).features("SAIL", "2026-10-26")
    assert f[kind]["value"] is True
    assert f[kind]["level_evidence"]["confirmed_session"] < "2026-10-26"
    spec, prices, info, calendar = deepcopy(captured[3])
    prices["SAIL"][-4][field] = pivot
    f = Panel(prices, info, calendar, spec["observations"]["analysis_cutoff"]).features("SAIL", "2026-10-26")
    assert f[kind]["value"] is None
    assert f[kind]["reason"] == "NO_PREEXISTING_CONFIRMED_PIVOT"


def test_explicit_attribution_and_multiple_hypotheses(captured):
    spec, prices, info, calendar = deepcopy(captured[3])
    result = derive(spec, prices, info, calendar, methodology=json.loads(METHOD.read_bytes()), close_reference_1r=True)
    assert result["expert_recommendations.json"]["attribution"] == "EXPERT_REPORTED"
    for symbol, stock in result["stock_features.json"].items():
        assert stock["attribution"] == "MARKET_OBSERVED"
        assert stock["features"]["daily_return"]["attribution"] == "MARKET_OBSERVED"
        assert stock["research_setup_hypotheses"]["attribution"] == "RESEARCH_HYPOTHESIS"
        assert stock["research_setup_hypotheses"]["intended_expert_setup"] is None
        assert result["trade_management.json"][symbol]["actual_target"] is None
    f = result["stock_features.json"]["SAIL"]["features"]
    for name in ("close_sma50", "sma50_slope20", "return20", "close_sma200", "sma50_sma200"):
        f[name]["value"] = .1
    f["failed_breakout20"]["value"] = True
    candidates = [h for h in setup(f)["hypotheses"] if h["status"] == "CONSISTENT_WITH_DIAGNOSTIC"]
    assert len(candidates) >= 3


def test_stale_es_coverage_retained_without_extrapolation_or_substitution():
    evidence = json.loads(AMENDMENT.read_bytes())
    original = {"status": "NOT_AVAILABLE", "raw_metadata": {"symbols": ["ES.FUT"]}, "inspected_aggregated_csv_sha256": evidence["es_coverage"]["source_sha256"]}
    saved = deepcopy(original)
    result = es_context(original, evidence, schedule("2026-05-01", "2026-10-26"), "2026-10-26")
    assert original == saved and result["raw_metadata"] == original["raw_metadata"]
    assert result["last_verified_available_session"] == "2026-05-04"
    assert result["missing_interval"]["first_missing_cash_session"] == "2026-05-05"
    assert result["missing_interval"]["last_missing_cash_session"] == "2026-10-26"
    assert result["missing_interval"]["missing_cash_session_count"] == 121
    assert result["status"] == "NOT_AVAILABLE"
    assert result["coverage_evidence"]["recent_IBKR_futures_replacement_validated"] is False


def test_amended_report_reproduces_and_resealed_target_is_rejected(captured, tmp_path):
    first = freeze_study(captured[0] / "inputs", tmp_path / "amended", methodology=METHOD, amendment=AMENDMENT, close_reference_1r=True)
    study = load_study(tmp_path / "amended")
    second = freeze_study(captured[0] / "inputs", tmp_path / "again", methodology=METHOD, amendment=AMENDMENT, close_reference_1r=True)
    assert first == second == study["hashes"]
    for name in ("expert_methodology.json", "trade_management.json", "return_validation.json"):
        assert name in study["files"]
    text = study["files"]["report.md"].decode()
    assert 'Daily return (1 session)' in text and 'Trailing 20-session return' in text
    assert 'Intended expert setup: UNKNOWN' in text and 'is_actual_execution=false' in text
    files = dict(study["files"])
    data = json.loads(files["trade_management.json"])
    data["SAIL"]["actual_target"] = "22.60"
    files["trade_management.json"] = encode(data)
    write_bundle(tmp_path / "tampered", files)
    with pytest.raises(ValueError, match="semantic output mismatch"):
        load_study(tmp_path / "tampered")
