# Grimes reconstruction under uncertainty

PR9A studies the 26 PR16 source-reported episodes using existing observations. It identifies explanations consistent with reported behavior; it does not estimate a universal strategy, actual fills, quantities, execution costs or realized P&L. All source OPEN/CLOSED and ENTERABLE/UNDERWAY states remain authoritative. The published `reports/grimes_trade_status.csv` is preserved byte for byte.

## Inputs and admission

The inspected merged main is `b03c2acb63614b1629e983e562fe94d21f460f65`. The configuration pins PR17 study-v2 (`fb2fd81dc3eeef6b10a185057930776a1534230a3534d63793d72d3e257342ca`), which embeds PR16 study-v5 (`4ce1b1f021d666bb870983cf894628c665992f97186e6e2740ccd2f4e69b2604`). The parent source ledger has 26 episodes and 72 actions. Subscriber bodies and native bars stay in ignored local bundles; public outputs contain derived diagnostics and source action facts without full commentary bodies.

A separate `EXPLORATORY_RECONSTRUCTION` mode validates qualified identities, native basis, finite positive consistent OHLC, nonnegative volume, duplicates and availability using the existing comprehension panel. Missing expected sessions make the corresponding indicator or path unavailable; they are never filled or skipped. Observed histories need not establish historical market-wide eligibility. PR8A's security master, universe rules and strict selection admission remain unchanged. No historical screening membership, unbiased population performance or trading edge is inferred.

Native data are retained. Optional uniform derived views require a positive factor, evidence reference, uncertainty status and explicit `raw_price_claim: false`. They leave volume unchanged. Such views permit sensitivity calculations without promoting assumed scales to verified raw prices. The actual study uses conditional native scales and bounded quote corroboration, not fitted scale factors.

## Information clocks and hypotheses

Price features require a completed cash session plus a declared 60-minute availability lag strictly before their construction or activation cutoff. Capture timestamps are provenance, not historical publication timestamps. ATR14 and other shared measurements use the existing panel and pinned `market-shared` implementation; no ATR formula is duplicated.

Known alert minutes use the end of the displayed minute as conservative availability. The weekly alert remains `published_at: null` / UNKNOWN. Conditional on chronological source order, its lower bound is October 22 at 18:28 ET; the independently retained email upper bound is October 25 at 12:57:45 UTC (08:57:45 ET). The label “Yesterday at 8:57 AM” is preserved, not converted to a date.

Three boundary schedules expose timing sensitivity:

- EARLY_BEFORE_FIRST_OPEN: weekly content is assumed available before Friday October 23 Open; construction uses the prior Thursday-evening bound.
- LATE_EMAIL_BOUND: content is assumed available at the Sunday email upper bound; next Open is Monday October 26.
- FIRST_SESSION_CLOSE_COMPATIBLE: publication is assumed compatible with Friday Close; construction uses information available before Friday Open. A closing entry uses no earlier Friday High/Low for its exposure.

These are hypotheses about intervals, not inferred exact timestamps. They do not exhaust every intraday placement. Other dated alerts retain their original bounds. The October 26 additions need October 27 data absent from the study and remain right-censored.

Each opening creates four fixed candidates, with a three-eligible-session trigger horizon:

1. H1 next eligible Open: a conventional reference with construction support 2, not proof of the actual fill.
2. H2 near alert-session Close: only the weekly Friday-close-compatible case is admissible here. Known after-hours alerts cannot execute earlier that same Close under this hypothesis. The exact closing price is a reference, not an inferred fill range.
3. H3 confirmation: when Close/SMA50, SMA50 slope20 and return20 all align with direction, use the last completed High (long) or Low (short). Otherwise use the prior 20-session extreme. Established short continuation receives support 2, other confirmation 1.
4. H4 pullback: choose the first available SMA20, SMA50 or confirmed protective pivot strictly between the pre-alert Close and opening stop. Aligned long pullbacks receive support 2, other pullbacks 0.

These diagnostic choices and ordinal support weights are specified by the coding/research agent to test the user's questions. They are not documented Grimes rules or probabilities. The source does not supply individual execution triggers. Direction and pre-alert structure prioritize candidates without fitting thresholds to later gains. Missing levels, untriggered entries and impossible geometry remain explicit outcomes.

Candidate construction excludes subsequent source decisions. At hypothetical activation, a stop revision already published before that session's Open can constrain placed risk; this separate activation evidence is recorded. Later revisions never reset original R. Positive protective risk is mandatory. Opening-stop geometry and activation-stop geometry are both retained. Intraday entry reference prices use a preselected threshold, or Open when already beyond it. Compatible daily price ranges are descriptive OHLC bounds, not executable spread/slippage estimates; unrestricted OHLC ranges are retained separately from positive protective-risk ranges. Nonpositive-risk price references are rejected; a displayed zero lower boundary on the positive range is open and excluded. No range becomes an asserted fill.

## Management and evidence ranking

Four bounded policies test different explanations:

- FULL_EXIT_AT_1R: exit all hypothetical exposure on the first +1R touch.
- PARTIAL_50_AT_1R: realize an illustrative 50%, retaining a runner with reported stops. The fraction is a fixed sensitivity assumption, not observed sizing.
- HOLD_WITH_REPORTED_STOPS: no automatic +1R realization; trail using causally reported stop changes.
- CLOSE_REVIEW_NEXT_OPEN: a separate discretionary convention: a Close beyond the known stop queues review at the next Open; exit only if that Open is still adverse to the latest then-known stop. This does not rescue or reopen a hard-stop path.

Daily paths branch through O-H-L-C and O-L-H-C. Intraday threshold entries occur only when a segment first reaches the entry; earlier extrema cannot be attributed to exposure. Open gaps and closing entries are treated separately. These two paths illustrate extrema-order uncertainty, not every possible intraday oscillation. Active, closed and unentered possibilities are retained. Counts are not probabilities. MFE/MAE values are upper envelopes over merged paths, not jointly realized excursions or money returns. No fees, slippage, sizing or execution-simulator policy changes are introduced.

STOP_CHANGED, SETUP_CHANGED and DROPPED are checked at their known/assumed clocks. A model already closed before continued source management creates a continuation conflict; it never closes the source record. DROP after a model exit has unresolved cause, rather than automatically confirming that model. Co-published decisions count once. Final source OPEN adds a continuation constraint without pretending to be another alert. No source reentry is inferred.

Only observed, complete candidate paths can rank. Lexicographic vectors minimize robust continuation-conflict clusters, then maximize compatible later alert clusters, then prefer management simplicity (hold 0, full/partial 1, deferred review 2), then prefer construction support. Profit is absent from the score. Extra convention penalties are explicit ordinal choices; changing them may break ties without identifying an actual fill. Observational equivalence is separately reported from identical source-action compatibility signatures even when simplicity ranks the explanations differently. Leading does not mean proven or conflict-free. Unknown future prices and untriggered entries are not favored because they avoid contradictions.

## Stop and decision analysis

For every episode, outputs retain entry price/time references and ranges, opening/activation stop distances, reference risk/ATR ranges, initial-stop distances to SMA20/50, confirmed pivots and prior20 boundaries. Per-revision diagnostics include directional widening/tightening, prior-stop clearance, distance to MAs/pivots, quote progress across alternative entry references, and 20-session relative price returns against SPY/QQQ/RSP/IWM.

Progress after a hypothetical exit is explicitly a counterfactual quote difference, never current exposure or realized profit. This allows competing management conventions to be compared without overwriting PR17's censored path outputs. Same-alert directional risk comparisons reduce clock differences but do not match volatility/structure, establish causality or prove a general short/long rule. Twenty-six selected episodes and correlated same-alert actions cannot justify calibrated confidence or significance tests.

## Adjustment evidence

Existing native TRADES/RTH captures retain their declared split-adjusted price interpretation and unverified volume units. A bounded replay around AAPL's documented 4:1 split on August 31, 2020 and Alphabet's 20:1 split on July 18, 2022 tests continuity versus undoing exactly one known component. The historical native report is pinned at `b2b8f5a15856a9ed4521b2c07f270e269501835b35ca3383305260c568b26043`. Existing PR6A/6B corporate-action bundles and their original issuer/SEC/OCC provenance are reused, not new provider subscriptions or fetched price feeds. Their original publication uncertainties remain. The derived ten-bar views are not exhaustive raw-price reconstruction.

The IBKR [API settings documentation](https://www.interactivebrokers.com/docs/tws-api/protobuf/api-settings-config) describes a US-stock shares/lots option, but does not establish which setting applied to these retained historical captures. IBKR's [legacy historical-bars documentation](https://interactivebrokers.github.io/tws-api/historical_bars.html) describes filtering that can make historical volume differ from unfiltered trades; that page is deprecated. Neither source verifies this capture's raw-volume convention. Empirical volume ratios are confounded by trading activity and filtering; no raw-share factor is invented.

Consistent price scaling can support technical analysis without validating nominal stop comparability. Uniformly scaling prices, stops and ATR preserves risk/ATR and barrier ordering; changing prices alone can change the result and needs independent corroboration. EBAY's exact retained Low quote anchor constrains that alternative. Dollar volume requires compatible contemporaneous nominal prices and verified share-volume units, so exploratory admission does not grant dollar-volume or strict historical-universe eligibility. Dividend adjustment, substantial reorganizations such as ASST's identity/scale history, exhaustive action coverage and raw volume remain unresolved.

## Reproduction

Run from the repository root with the existing virtual environment. Every output must be a new directory. The standalone command prohibits socket connections. Its only inputs are existing local bundles.

```sh
PYTHONPATH=src .venv/bin/python scripts/reconstruct_grimes_trades.py --help
PYTHONPATH=src .venv/bin/python scripts/reconstruct_grimes_trades.py freeze-inputs --parent runs/grimes-management-20261018-26-v1/study-v2 --config experiments/grimes-reconstruction-v1.json --output runs/grimes-reconstruction-20261018-26-v1/inputs-NEW
PYTHONPATH=src .venv/bin/python scripts/reconstruct_grimes_trades.py study --inputs runs/grimes-reconstruction-20261018-26-v1/inputs-NEW --output runs/grimes-reconstruction-20261018-26-v1/study-NEW
PYTHONPATH=src .venv/bin/python scripts/reconstruct_grimes_trades.py replay --study runs/grimes-reconstruction-20261018-26-v1/study-NEW --output runs/grimes-reconstruction-20261018-26-v1/replay-NEW
.venv/bin/python -m pytest -q
```

Replay verifies seals and semantically rederives the PR16/17 dependencies, canonical native capture windows, event assertions and all new outputs. Resealing altered derived records does not make them acceptable. Results are immutable and implementation-bound; edits require a new study version. Frozen inputs contain the complete required local proof, so study/replay needs no original vendor connection or provider installation. Private native inputs are intentionally not committed; the public scenario comparison and tests permit inspection without disclosing full subscriber material.
