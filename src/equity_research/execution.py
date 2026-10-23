"""Declared daily OHLC approximation: opening events, then conservative touches."""

from dataclasses import dataclass
from decimal import Context, Decimal, localcontext

from .accounting import close_trade, size_position
from .data import DailyBar, Dataset
from .models import Candidate, Config
from .qualification import qualify
from .strategy import plan_order, price_grid


@dataclass(frozen=True)
class Fill:
    side: str
    quantity: int
    session_date: object
    reference_price: Decimal
    price: Decimal
    commission_dollars: Decimal
    fees_dollars: Decimal
    slippage_dollars: Decimal
    timing: str
    window_start: object
    window_end: object


def make_fill(side: str, quantity: int, reference: Decimal, bar: DailyBar,
              config: Config, timing: str) -> dict:
    actual = reference + config.slippage_per_share if side == "buy" else reference - config.slippage_per_share
    if actual <= 0:
        raise ValueError("cost model produces a nonpositive executable price")
    return vars(Fill(
        side, quantity, bar.session.session_date, reference, actual,
        config.commission_per_share * quantity, config.fees_per_order,
        config.slippage_per_share * quantity, timing,
        bar.session.closes_at if timing == "close" else bar.session.opens_at,
        bar.session.opens_at if timing == "open" else bar.session.closes_at,
    ))


def simulate(dataset: Dataset, candidate: Candidate, config: Config) -> dict:
    # Caller Decimal settings must not change canonical sizing/PnL/R outputs.
    with localcontext(Context(prec=28)):
        return _simulate(dataset, candidate, config)


def _simulate(dataset: Dataset, candidate: Candidate, config: Config) -> dict:
    decision = qualify(dataset, candidate, config)
    result = {"status": "REJECTED" if decision["status"] == "REJECT" else decision["status"],
              "reason_codes": decision["reason_codes"],
              "qualification": decision, "order": None, "fills": [], "trade": None}
    if decision["status"] != "ELIGIBLE":
        return result
    order = plan_order(dataset, candidate, decision, config)
    return replay_order(dataset, order, config, result=result)


def replay_order(dataset: Dataset, order: dict, config: Config, *, result=None) -> dict:
    """Replay one already planned long stop using the original PR4 fill engine.

    Admission and causal order construction belong to the calling adapter. This
    primitive is also used by the unchanged legacy qualification/planning path.
    """
    from copy import deepcopy
    with localcontext(Context(prec=28)):
        return _replay_order(dataset, deepcopy(order), config, result=result)


def _replay_order(dataset, order, config, *, result=None):
    if order["side"] != "buy" or order["order_type"] != "stop":
        raise ValueError("only long buy-stop replay is supported")
    result = result if result is not None else {
        "status": "CREATED", "reason_codes": [], "fills": [], "trade": None}
    result["order"] = order
    if not 0 < order["initial_stop"] < order["trigger"]:
        order["status"] = result["status"] = "REJECTED"
        result["reason_codes"] = ["invalid_stop"]
        return result
    entry = None
    target = None
    holding = 0
    entry_order_ambiguity = False
    for i, bar in enumerate(dataset.bars):
        is_entry_bar = False
        if entry is None:
            if order["activation_at"] is None or bar.session.opens_at < order["activation_at"]:
                continue
            order["eligible_sessions_seen"] += 1
            if bar.high < order["trigger"]:
                if order["eligible_sessions_seen"] == config.order_valid_sessions:
                    order["status"] = result["status"] = "EXPIRED"
                    result["reason_codes"] = ["breakout_not_triggered"]
                    return result
                continue
            reference = max(bar.open, order["trigger"])
            sizing = size_position(reference + config.slippage_per_share, order["initial_stop"],
                                   config, config.initial_equity)
            order["sizing"] = sizing
            if sizing["quantity"] == 0:
                order["status"] = result["status"] = "REJECTED"
                result["reason_codes"] = [sizing["reason"]]
                return result
            timing = "open" if bar.open >= order["trigger"] else "intraday_order_unknown"
            entry = make_fill("buy", sizing["quantity"], reference, bar, config, timing)
            result["fills"].append(entry)
            order["status"] = "FILLED"
            if config.target_r is not None:
                target = price_grid(entry["price"] + config.target_r * (entry["price"] - order["initial_stop"]),
                                    config.price_increment, up=True)
            order["target_price"] = target
            is_entry_bar = True
        holding += 1
        stop_hit = bar.low <= order["initial_stop"]
        target_hit = target is not None and bar.high >= target
        # Only a pre-existing/open-filled position can exit at that session's open.
        opening_exit_allowed = not is_entry_bar or entry["timing"] == "open"
        reason, reference, timing = None, None, "intraday_order_unknown"
        collision = False
        if opening_exit_allowed and bar.open <= order["initial_stop"]:
            reason, reference, timing = "stop_gap", bar.open, "open"
        elif opening_exit_allowed and target is not None and bar.open >= target:
            reason, reference, timing = "target_gap", bar.open, "open"
        elif stop_hit:
            reason, reference = "stop", order["initial_stop"]
            collision = bool(target_hit)
            if is_entry_bar and entry["timing"] == "intraday_order_unknown":
                entry_order_ambiguity = True  # day's low could precede entry
        elif target_hit:
            reason, reference = "target", target
        elif holding >= config.max_holding_sessions:
            reason, reference, timing = "max_holding", bar.close, "close"
        elif i == len(dataset.bars) - 1:
            reason, reference, timing = "end_of_data", bar.close, "close"
        if reason is not None:
            exit_ = make_fill("sell", entry["quantity"], reference, bar, config, timing)
            result["fills"].append(exit_)
            result["trade"] = close_trade(entry, exit_, order["initial_stop"], config, holding, reason,
                                           {"stop_target_ambiguous": collision,
                                            "entry_exit_order_ambiguous": entry_order_ambiguity})
            result["status"] = "COMPLETED"
            result["reason_codes"] = [reason]
            return result
    order["status"] = result["status"] = "UNFILLED_END_OF_DATA"
    result["reason_codes"] = ["dataset_ended_before_order_expiry"]
    return result
