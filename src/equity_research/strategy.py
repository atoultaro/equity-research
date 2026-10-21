"""One post-close buy-stop plan, fixed once from the signal session."""

from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR

from .data import Dataset
from .models import Candidate, Config


def price_grid(value: Decimal, increment: Decimal, *, up: bool) -> Decimal:
    return (value / increment).to_integral_value(rounding=ROUND_CEILING if up else ROUND_FLOOR) * increment


def plan_order(dataset: Dataset, candidate: Candidate, decision: dict, config: Config) -> dict:
    signal = next(b for b in dataset.bars if b.session.session_date == candidate.candidate_session)
    trigger = price_grid(signal.high + config.entry_buffer, config.price_increment, up=True)
    stop = price_grid(signal.close - config.stop_atr_multiple * Decimal(str(decision["features"]["atr"])),
                      config.price_increment, up=False)
    future = [b for b in dataset.bars if b.session.session_date > candidate.candidate_session
              and b.session.opens_at >= candidate.available_at]
    expires = future[config.order_valid_sessions - 1].session.closes_at if len(future) >= config.order_valid_sessions else None
    return {"side": "buy", "order_type": "stop", "trigger": trigger, "initial_stop": stop,
            "created_at": candidate.available_at,
            "activation_at": future[0].session.opens_at if future else None,
            "expires_at": expires, "valid_sessions": config.order_valid_sessions,
            "status": "CREATED", "eligible_sessions_seen": 0}
