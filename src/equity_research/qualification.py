"""One long-trend hypothesis. Qualification has no order-routing behavior."""

from math import isfinite
from statistics import mean

from market_shared.indicators import atr_simple_last, true_range

from .data import Dataset
from .models import Candidate, Config


def sma(values: list[float], period: int) -> float | None:
    if isinstance(period, bool) or not isinstance(period, int) or period < 1:
        raise ValueError("SMA period must be a positive integer")
    if any(not isfinite(v) for v in values):
        raise ValueError("SMA values must be finite")
    return mean(values[-period:]) if len(values) >= period else None


def qualify(dataset: Dataset, candidate: Candidate, config: Config) -> dict:
    decision = {"status": "WATCH", "reason_codes": [], "decision_at": candidate.available_at,
                "last_completed_session": None, "feature_asof_ts": None, "features": {},
                "membership_evidence": "user_supplied_not_independently_verified"}

    def result(status, reason):
        return dict(decision, status=status, reason_codes=[reason])

    provenance = candidate.provenance
    if not provenance.get("reference") or provenance.get("kind") not in {"synthetic", "recorded_observation"}:
        return result("REJECT", "missing_source_provenance")
    if provenance["kind"] == "synthetic":
        decision["membership_evidence"] = "synthetic"
    if candidate.source != "manual":
        return result("REJECT", "source_not_supported")
    if candidate.setup_family != "breakout":
        return result("REJECT", "setup_family_not_supported")
    if candidate.symbol != dataset.manifest["symbol"]:
        return result("REJECT", "security_mismatch")
    signal = next((b for b in dataset.bars if b.session.session_date == candidate.candidate_session), None)
    if signal is None or signal.session.available_at > candidate.available_at:
        return result("WATCH", "signal_bar_unavailable")
    if candidate.observed_at < signal.session.closes_at:
        return result("WATCH", "candidate_before_signal_close")
    # Freeze the signal at candidate_session, even if its observation arrives later.
    history = [b for b in dataset.bars if b.session.session_date <= candidate.candidate_session
               and b.session.available_at <= candidate.available_at]
    decision.update(last_completed_session=history[-1].session.session_date,
                    feature_asof_ts=history[-1].session.available_at)
    needed = max(config.sma_period + config.sma_rising_lookback, config.atr_period + 1,
                 config.liquidity_lookback)
    if len(history) < needed:
        return result("WATCH", "insufficient_history")
    closes = [float(b.close) for b in history]
    latest = sma(closes, config.sma_period)
    prior = sma(closes[:-config.sma_rising_lookback], config.sma_period)
    ranges = [true_range(float(b.high), float(b.low), float(history[i - 1].close) if i else None)
              for i, b in enumerate(history)]
    atr = atr_simple_last(ranges, config.atr_period)
    liquidity = mean(b.volume for b in history[-config.liquidity_lookback:])
    decision["features"] = {"sma": latest, "prior_sma": prior, "atr": atr,
                            "average_volume": liquidity, "close": history[-1].close,
                            "history_bars": len(history)}
    if liquidity < config.min_average_volume:
        return result("REJECT", "insufficient_liquidity")
    if atr <= 0:
        return result("WATCH", "atr_not_positive")
    reasons = []
    if closes[-1] <= latest:
        reasons.append("close_not_above_sma")
    if latest <= prior:
        reasons.append("sma_not_rising")
    return dict(decision, status="WATCH" if reasons else "ELIGIBLE",
                reason_codes=reasons or ["long_trend_qualified"])
