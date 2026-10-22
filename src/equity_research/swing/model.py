"""Small versioned research records. No order or fill is a strategy signal."""

from dataclasses import dataclass
from decimal import Context, localcontext

from ..ingestion.storage import digest, encode
from ..models import number

CONTINUATION = "breakout_continuation_v1"
FAILED = "failed_breakout_v1"


@dataclass(frozen=True)
class Configuration:
    strategy_id: str = CONTINUATION
    lookback_sessions: int = 20
    failure_sessions: int = 3
    stop_atr_multiple: str = "1.5"
    signal_expiry_sessions: int = 3
    delay_minutes: int = 60

    def __post_init__(self):
        if self.strategy_id not in {CONTINUATION, FAILED}:
            raise ValueError("unsupported strategy")
        for key in ("lookback_sessions", "failure_sessions", "signal_expiry_sessions", "delay_minutes"):
            if type(getattr(self, key)) is not int or getattr(self, key) < 1:
                raise ValueError(f"{key} must be a positive integer")
        if self.delay_minutes > 360 or number(self.stop_atr_multiple) <= 0:
            raise ValueError("invalid availability delay or ATR multiple")
        with localcontext(Context(prec=28)):
            object.__setattr__(self, "stop_atr_multiple", str(number(self.stop_atr_multiple).normalize()))

    def record(self):
        return {"schema_version": "swing_strategy_config_v1", "strategy_id": self.strategy_id,
                "strategy_version": "1", "boundary": {"type": "prior_n_session_high", "lookback_sessions": self.lookback_sessions},
                "trend": {"close_above_sma50": self.strategy_id == CONTINUATION,
                          "sma50_above_sma200": self.strategy_id == CONTINUATION},
                "trigger": {"type": "close_above_boundary" if self.strategy_id == CONTINUATION else "high_above_then_following_close_below_original_boundary",
                            "comparison": "STRICT"},
                "risk": {"atr_period": 14, "stop_atr_multiple": self.stop_atr_multiple},
                "failure_sessions": self.failure_sessions, "signal_expiry_sessions": self.signal_expiry_sessions,
                "availability": {"type": "RECONSTRUCTED_CLOSE_PLUS_DELAY", "delay_minutes": self.delay_minutes},
                "lifecycle": "independent_overlapping_attempts_fixed_boundary; immediate_failure_observation_only; expiry_at_Kth_following_close; no_reset_on_higher_attempt",
                "corporate_actions": "invalidate_known_effective_discontinuities_only; unknown_dates_global_uncertainty; no_date_inference",
                "entry_policy": "next_session_buy_stop_at_rounded_planning_close_for_LONG; SHORT_NOT_SUPPORTED"}

    @property
    def sha256(self): return digest(encode(self.record()))

    @classmethod
    def from_record(cls, raw):
        result = cls(raw["strategy_id"], raw["boundary"]["lookback_sessions"], raw["failure_sessions"],
                     raw["risk"]["stop_atr_multiple"], raw["signal_expiry_sessions"], raw["availability"]["delay_minutes"])
        if result.record() != raw:
            raise ValueError("unsupported strategy configuration")
        return result


@dataclass(frozen=True)
class Boundary:
    value: str
    construction_rule: str
    window_start: str
    window_end: str
    latest_input_session: str
    price_dataset_sha256: str
    configuration_sha256: str
    boundary_type: str = "prior_n_session_high"


@dataclass(frozen=True)
class Setup:
    setup_id: str
    setup_type: str
    session_date: str
    observed_at: str
    boundary: Boundary


@dataclass(frozen=True)
class Trigger:
    setup_id: str
    session_date: str
    available_at: str
    direction: str
    reason: str


@dataclass(frozen=True)
class Signal:
    signal_id: str
    strategy_id: str
    strategy_version: str
    configuration_sha256: str
    security_id: str
    symbol: str
    setup: Setup
    trigger: Trigger
    feature_observation_cutoffs: dict
    features: dict
    market_context_reference: str
    price_dataset_sha256: str
    signal_quality: dict
    schema_version: str = "swing_signal_v1"


@dataclass(frozen=True)
class TradePlan:
    signal_id: str
    direction: str
    planned_entry_reference: str
    earliest_entry_session: str | None
    entry_order_type: str
    entry_trigger: str
    initial_stop_reference: str | None
    planned_risk_per_share: str | None
    expiry_session: str | None
    invalidation_reason: str | None
    execution_eligibility_status: str
    planned_position_size: int | None = None
    planned_risk_dollars: str | None = None
    sizing_status: str = "PROVISIONAL_REQUIRES_ACTUAL_FILL"
    outcome_link: dict | None = None
    schema_version: str = "swing_trade_plan_v1"


def identity(kind, *parts):
    return kind + ":" + digest(encode(parts))


def prior_boundary(history, config, price_sha):
    """History excludes the candidate bar; boundary detectors have no order logic."""
    if len(history) < config.lookback_sessions:
        return None
    window = history[-config.lookback_sessions:]
    return Boundary(str(max(number(r["high"]) for r in window)),
                    "max(high[t-N],...,high[t-1]); current session excluded",
                    window[0]["session_date"], window[-1]["session_date"], window[-1]["session_date"], price_sha, config.sha256)


def evaluate_trigger(setup, row, available_at, *, failed=False):
    close, boundary = number(row["close"]), number(setup.boundary.value)
    if (close < boundary) if failed else (close > boundary):
        return Trigger(setup.setup_id, row["session_date"], available_at,
                       "SHORT" if failed else "LONG", "following_close_below_original_boundary" if failed else "close_strictly_above_prior_boundary")
    return None


def build_plan(signal, close, atr, future_sessions, config):
    reference = number(close)
    risk = None if atr is None else number(atr) * number(config.stop_atr_multiple)
    stop = None if risk is None else reference + (risk if signal.trigger.direction == "SHORT" else -risk)
    invalid = "ATR_WARMUP_OR_NONPOSITIVE_RISK" if risk is None or risk <= 0 else "NONPOSITIVE_STOP" if stop <= 0 else None
    return TradePlan(signal.signal_id, signal.trigger.direction, str(reference),
                     future_sessions[0] if future_sessions else None,
                     "BUY_STOP" if signal.trigger.direction == "LONG" else "UNSUPPORTED_SHORT",
                     str(reference), str(stop) if stop is not None else None,
                     str(risk) if risk is not None else None,
                     future_sessions[config.signal_expiry_sessions-1] if len(future_sessions) >= config.signal_expiry_sessions else None,
                     invalid, "INVALID_PLAN" if invalid else "SHORT_EXECUTION_UNSUPPORTED" if signal.trigger.direction == "SHORT" else "REQUIRES_STRICT_DATA_ADMISSION",
                     outcome_link={"signal_id": signal.signal_id, "return_horizons": None, "mfe": None, "mae": None,
                                   "entry_context": None, "holding_context_transitions": None, "realized_r": None,
                                   "execution_rejection_or_expiry": None})
