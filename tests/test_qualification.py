from dataclasses import replace
from decimal import Decimal
import math

import pytest

from equity_research.qualification import qualify, sma
from equity_research.models import timestamp


def test_sma_full_window_empty_warmup_and_precision():
    assert sma([], 3) is None
    assert sma([1, 2], 3) is None
    assert sma([1, 2, 3, 4], 3) == 3
    assert sma([7] * 50, 50) == 7
    assert sma([.1, .2, .3], 3) == pytest.approx(.2, rel=0, abs=1e-15)
    with pytest.raises(ValueError):
        sma([math.nan], 1)
    with pytest.raises(ValueError):
        sma([1], 0)


def test_independent_long_trend_qualification(dataset, candidate, config):
    decision = qualify(dataset, candidate, config)
    assert decision["status"] == "ELIGIBLE"
    assert decision["features"]["sma"] == 117.25
    assert decision["features"]["prior_sma"] == 114.75
    assert decision["features"]["atr"] == 2.0
    assert decision["feature_asof_ts"] <= decision["decision_at"]
    assert decision["features"]["history_bars"] == 60
    assert decision["membership_evidence"] == "synthetic"


def test_insufficient_history_and_zero_volatility_stay_watch(dataset, candidate, config):
    assert qualify(replace(dataset, bars=dataset.bars[6:]), candidate, config)["reason_codes"] == ["insufficient_history"]
    flat = tuple(replace(b, open=Decimal(100), high=Decimal(100), low=Decimal(100), close=Decimal(100))
                 for b in dataset.bars)
    decision = qualify(replace(dataset, bars=flat), candidate, config)
    assert decision["status"] == "WATCH"
    assert decision["reason_codes"] == ["atr_not_positive"]


def test_future_bar_poisoning_cannot_change_qualification(dataset, future, candidate, config):
    modified = future(dataset, [(500, 1000, 1, 900)] * 4)
    assert qualify(modified, candidate, config) == qualify(dataset, candidate, config)


def test_preclose_observation_and_unavailable_signal_are_not_eligible(dataset, candidate, config):
    early = timestamp("2026-03-10T19:00:00Z")
    assert qualify(dataset, replace(candidate, observed_at=early), config)["reason_codes"] == ["candidate_before_signal_close"]
    assert qualify(dataset, replace(candidate, observed_at=early, available_at=early), config)["reason_codes"] == ["signal_bar_unavailable"]


def test_missing_candidate_provenance_is_never_historically_invented(dataset, candidate, config):
    decision = qualify(dataset, replace(candidate, provenance={}), config)
    assert decision["status"] == "REJECT"
    assert decision["reason_codes"] == ["missing_source_provenance"]
    assert decision["membership_evidence"] != "historically_observed"
    vendor = replace(candidate, source="deepvue", provenance={"kind": "recorded_observation", "reference": "unverified"})
    assert qualify(dataset, vendor, config)["reason_codes"] == ["source_not_supported"]


def test_low_liquidity_and_nonrising_trend_have_reasons(dataset, candidate, config):
    assert qualify(dataset, candidate, replace(config, min_average_volume=Decimal("2000000")))["reason_codes"] == ["insufficient_liquidity"]
    bars = list(dataset.bars)
    bars[59] = replace(bars[59], close=Decimal(100), low=Decimal(99))
    decision = qualify(replace(dataset, bars=tuple(bars)), candidate, config)
    assert decision["status"] == "WATCH"
    assert "close_not_above_sma" in decision["reason_codes"]
