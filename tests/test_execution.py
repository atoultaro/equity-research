from dataclasses import replace
from decimal import Decimal as D
from decimal import localcontext

from equity_research.execution import simulate
from equity_research.models import timestamp


def test_postclose_candidate_cannot_fill_same_day(dataset, candidate, config):
    result = simulate(dataset, candidate, config)
    entry = result["fills"][0]
    assert result["status"] == "COMPLETED"
    assert entry["session_date"].isoformat() == "2026-03-11"
    assert entry["window_start"] >= result["order"]["activation_at"] > candidate.available_at
    assert result["qualification"]["feature_asof_ts"] <= candidate.available_at


def test_midday_availability_skips_that_sessions_open(dataset, candidate, config):
    delayed = replace(candidate, available_at=timestamp("2026-03-11T14:00:00Z"))
    result = simulate(dataset, delayed, config)
    assert result["fills"][0]["session_date"].isoformat() == "2026-03-12"
    assert result["order"]["activation_at"] >= delayed.available_at


def test_breakout_expiry_prevents_later_fill(dataset, future, candidate, config):
    data = future(dataset, [(129, 130, 128, 129)] * 3 + [(132, 160, 131, 150)])
    result = simulate(data, candidate, config)
    assert result["status"] == result["order"]["status"] == "EXPIRED"
    assert result["order"]["eligible_sessions_seen"] == 3
    assert result["order"]["expires_at"].isoformat() == "2026-03-13T20:00:00+00:00"
    assert result["trade"] is None and result["fills"] == []


def test_unfilled_end_of_data_is_not_mislabeled_expired(dataset, future, candidate, config):
    result = simulate(future(dataset, [(129, 130, 128, 129)] * 2), candidate, config)
    assert result["status"] == "UNFILLED_END_OF_DATA"
    assert result["order"]["expires_at"] is None
    assert result["trade"] is None


def test_gap_up_entry_and_fixed_initial_risk_hand_reference(dataset, candidate, config):
    result = simulate(dataset, candidate, config)
    trade, entry, exit_ = result["trade"], result["fills"][0], result["fills"][1]
    assert result["order"]["trigger"] == D("130.60")
    assert entry["reference_price"] == D(132)
    assert entry["price"] == D("132.01")
    assert entry["quantity"] == 15
    assert trade["initial_stop"] == D("125.50")
    assert trade["initial_risk_dollars"] == D("97.65")
    assert result["order"]["target_price"] == D("145.03")
    assert exit_["price"] == D("145.02")
    assert trade["gross_pnl_dollars"] == D("195.45")
    assert trade["commission_dollars"] == D("0.150")
    assert trade["fees_dollars"] == D("1.00")
    assert trade["modeled_slippage_dollars"] == D("0.30")
    assert trade["net_pnl_dollars"] == D("194.00")
    assert trade["realized_r"] == D("194") / D("97.65")
    assert trade["final_cash_dollars"] == D("10194.00")


def test_stop_gap_exits_at_open_not_guaranteed_stop(dataset, future, candidate, config):
    result = simulate(future(dataset, [(132, 134, 131, 133), (120, 122, 119, 121)]), candidate, config)
    trade, exit_ = result["trade"], result["fills"][1]
    assert trade["exit_reason"] == "stop_gap"
    assert exit_["reference_price"] == D(120)
    assert exit_["price"] == D("119.99") < trade["initial_stop"]
    assert trade["initial_risk_dollars"] == D("97.65")
    assert trade["net_pnl_dollars"] == D("-181.45")
    assert trade["realized_r"] == D("-181.45") / D("97.65")


def test_stop_target_collision_uses_stop_first_and_flags_ambiguity(dataset, future, candidate, config):
    result = simulate(future(dataset, [(132, 134, 131, 133), (133, 146, 124, 130)]), candidate, config)
    trade = result["trade"]
    assert trade["exit_reason"] == "stop"
    assert trade["stop_target_ambiguous"] is True
    assert trade["exit_price"] == D("125.49")
    assert trade["net_pnl_dollars"] == D("-98.95")


def test_intraday_entry_cannot_exit_at_that_days_earlier_open(dataset, future, candidate, config):
    result = simulate(future(dataset, [(124, 132, 123, 131)]), candidate, config)
    assert result["fills"][0]["reference_price"] == D("130.60")
    assert result["trade"]["exit_reason"] == "stop"  # not a pre-entry gap stop at124
    assert result["trade"]["exit_price"] == D("125.49")
    assert result["trade"]["entry_exit_order_ambiguous"] is True
    assert result["fills"][0]["timing"] == "intraday_order_unknown"


def test_entry_sizing_does_not_use_entry_days_close(dataset, future, candidate, config):
    a = simulate(future(dataset, [(132, 134, 131, 133)]), candidate, config)
    b = simulate(future(dataset, [(132, 134, 131, 131)]), candidate, config)
    assert a["fills"][0] == b["fills"][0]
    assert a["order"]["sizing"] == b["order"]["sizing"]


def test_terminal_and_holding_period_full_exits(dataset, future, candidate, config):
    terminal = simulate(future(dataset, [(132, 134, 131, 133)]), candidate, config)
    assert terminal["trade"]["exit_reason"] == "end_of_data"
    assert terminal["trade"]["net_pnl_dollars"] == D("13.55")
    holding = simulate(dataset, candidate, replace(config, max_holding_sessions=2))
    assert holding["trade"]["exit_reason"] == "max_holding"
    assert holding["trade"]["holding_sessions"] == 2
    assert holding["trade"]["net_pnl_dollars"] == D("58.55")
    disabled = simulate(dataset, candidate, replace(config, target_r=None))
    assert disabled["trade"]["exit_reason"] == "end_of_data"


def test_zero_quantity_and_invalid_stops_are_visible_rejections(dataset, candidate, config):
    rejected = simulate(dataset, candidate, replace(config, max_position_notional=D(100)))
    assert rejected["status"] == "REJECTED"
    assert rejected["reason_codes"] == ["zero_affordable_quantity"]
    assert rejected["trade"] is None and rejected["fills"] == []
    invalid = simulate(dataset, candidate, replace(config, stop_atr_multiple=D(1000)))
    assert invalid["reason_codes"] == ["invalid_stop"]


def test_candidate_available_after_dataset_has_no_fill(dataset, candidate, config):
    result = simulate(dataset, replace(candidate, available_at=timestamp("2026-03-20T20:15:00Z")), config)
    assert result["status"] == "UNFILLED_END_OF_DATA"
    assert result["order"]["activation_at"] is None
    assert result["fills"] == []


def test_caller_decimal_context_cannot_change_research_results(dataset, candidate, config):
    expected = simulate(dataset, candidate, config)
    with localcontext() as context:
        context.prec = 6
        assert simulate(dataset, candidate, config) == expected
