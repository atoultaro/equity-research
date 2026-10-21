from dataclasses import replace
from decimal import Decimal as D

import pytest

from equity_research.accounting import close_trade, size_position
from equity_research.execution import make_fill
from equity_research.strategy import price_grid


def test_risk_floor_cash_cap_and_notional_cap(config):
    free = replace(config, commission_per_share=D(0), fees_per_order=D(0))
    assert size_position(D(100), D(98), free, D(10000))["quantity"] == 50
    assert size_position(D(100), D(97), free, D(10000))["quantity"] == 33
    assert size_position(D(100), D(98), free, D(450))["quantity"] == 4
    limited = replace(free, max_position_notional=D(1000))
    assert size_position(D(100), D(98), limited, D(10000))["quantity"] == 10
    # Fees are reserved at entry; a share costing100 plus fees does not fit100 cash.
    assert size_position(D(100), D(98), config, D(100))["quantity"] == 0
    assert size_position(D(100), D(98), replace(config, risk_fraction=D("0.0001")), D(10000))["quantity"] == 0


@pytest.mark.parametrize("stop", [D(0), D(-1), D(100), D(101)])
def test_wrong_side_zero_or_negative_stops_are_not_risk_distances(config, stop):
    assert size_position(D(100), stop, config, D(10000))["reason"] == "invalid_stop"


def test_hand_calculated_gross_cost_net_and_original_risk(dataset, config):
    policy = replace(config, slippage_per_share=D("0.25"), commission_per_share=D("0.10"), fees_per_order=D(1))
    entry = make_fill("buy", 10, D(100), dataset.bars[0], policy, "open")
    exit_ = make_fill("sell", 10, D(104), dataset.bars[1], policy, "intraday_order_unknown")
    trade = close_trade(entry, exit_, D(98), policy, 2, "target", {})
    assert trade["entry_price"] == D("100.25")
    assert trade["exit_price"] == D("103.75")
    assert trade["initial_risk_dollars"] == D("22.50")
    assert trade["gross_pnl_dollars"] == D(40)
    assert trade["price_pnl_after_slippage_dollars"] == D(35)
    assert trade["modeled_slippage_dollars"] == D(5)
    assert trade["commission_dollars"] == D(2)
    assert trade["fees_dollars"] == D(2)
    assert trade["net_pnl_dollars"] == D(31)
    assert trade["realized_r"] == D(31) / D("22.50")
    assert trade["net_pnl_dollars"] == trade["gross_pnl_dollars"] - trade["modeled_slippage_dollars"] - trade["commission_dollars"] - trade["fees_dollars"]


def test_execution_price_grid_rounds_adversely():
    assert price_grid(D("100.001"), D("0.01"), up=True) == D("100.01")
    assert price_grid(D("98.999"), D("0.01"), up=False) == D("98.99")
