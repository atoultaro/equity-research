"""Integer-share sizing and a single full-exit ledger; no minimum quantity."""

from decimal import Decimal, ROUND_FLOOR

from .models import Config


def size_position(entry: Decimal, stop: Decimal, config: Config, cash: Decimal) -> dict:
    budget = config.initial_equity * config.risk_fraction
    if not entry.is_finite() or not stop.is_finite() or not 0 < stop < entry:
        return {"quantity": 0, "reason": "invalid_stop", "risk_budget_dollars": budget}
    floor = lambda x: int(x.to_integral_value(rounding=ROUND_FLOOR))
    quantity = min(floor(budget / (entry - stop)),
                   max(0, floor((cash - config.fees_per_order) / (entry + config.commission_per_share))))
    if config.max_position_notional is not None:
        quantity = min(quantity, floor(config.max_position_notional / entry))
    return {"quantity": quantity, "reason": "sized" if quantity > 0 else "zero_affordable_quantity",
            "risk_budget_dollars": budget}


def close_trade(entry: dict, exit_: dict, initial_stop: Decimal, config: Config,
                holding_sessions: int, exit_reason: str, ambiguity: dict) -> dict:
    quantity = entry["quantity"]
    initial_risk = (entry["price"] - initial_stop) * quantity
    gross = (exit_["reference_price"] - entry["reference_price"]) * quantity
    commission = entry["commission_dollars"] + exit_["commission_dollars"]
    fees = entry["fees_dollars"] + exit_["fees_dollars"]
    slippage = entry["slippage_dollars"] + exit_["slippage_dollars"]
    price_pnl = (exit_["price"] - entry["price"]) * quantity
    net = price_pnl - commission - fees
    assert net == gross - slippage - commission - fees
    return {"quantity": quantity, "entry_price": entry["price"], "exit_price": exit_["price"],
            "initial_stop": initial_stop, "initial_risk_dollars": initial_risk,
            "gross_pnl_dollars": gross, "price_pnl_after_slippage_dollars": price_pnl,
            "commission_dollars": commission, "fees_dollars": fees,
            "modeled_slippage_dollars": slippage, "net_pnl_dollars": net,
            "realized_r": net / initial_risk, "gross_price_r": price_pnl / initial_risk,
            "entry_session": entry["session_date"], "exit_session": exit_["session_date"],
            "holding_sessions": holding_sessions, "exit_reason": exit_reason,
            "final_cash_dollars": config.initial_equity + net, **ambiguity}
