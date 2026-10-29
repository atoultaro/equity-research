# Grimes four-trade forensics — PR9B

CLMT, TEVA and GME admit a simpler closing-confirmation explanation for their continued source management. EBAY does not: its Close was below the old stop before the evening revision. These are conditional explanations, not identification of Grimes’ fills or stop orders. CDE is a target-exit convention conflict, distinct from a protective-stop conflict.

SOURCE is the unchanged expert ledger. MARKET is retained IBKR TRADES/RTH evidence. HYPOTHESIS is an explicitly assumed entry or management convention. INFERENCE compares them. All four cases remain source ENTERABLE throughout; only control CDE transitions UNDERWAY. The weekly alert’s publication remains **UNKNOWN**; no calendar date is inferred from its display. Late-email-bound, early-before-Friday-Open and Friday-Close clocks are conditional schedules, not three observations.

## Evidence and conventions

Base main: `8be6c8ec10b98870c273964ac5dbaa7a6757e9d6`; merged PR19 head: `71877971466621382129f864fa39952c17ce1a7d`. Pinned PR19 sensitivity parent: `484ecf07fcb22467178fe1aaf3cdbcd175bf273bd62854aa40b26444860ce263`. Analysis cutoff: `2026-10-26T18:11:00-04:00`. No later bars are used to explain earlier decisions. Actual prices, quantities, orders, realized P&L and fees remain unknown.

Native daily prices retain the inherited split-adjusted declaration and conditional nominal-stop comparison. Native volume units are unverified, so the V column is not asserted to be shares. No arbitrary rescaling, Yahoo replacement or historical identity splice is applied. Source hashes and qualified conIds are in [forensic_comparison.json](../evidence/pr9b-forensics-v1/forensic_comparison.json). PR19’s embedded native proofs supply the admitted daily IBKR case evidence. The separate local request-manifest inventory found no case Yahoo or five-minute request; it does not unpack native requests embedded inside source-proof JSON. The scope is repository runs/data, not all disks or all possible existing datasets.

New requests used the existing pinned ib_async==2.1.0 low-level backend, a confirmed read-only local TWS on port 7496, and exactly four RTH five-minute windows. No account, position, execution or order queries were made. Raw native returns and timestamps are retained in a new local immutable bundle; derived diagnostics are versioned here.

## Focused intraday evidence

| Instrument/session | Stop | First/last touching bar (ET) | Complete protected bars after last touch | Protected tail range | Daily / final 5m Close |
| --- | --- | --- | --- | --- | --- |
| CLMT 2026-10-19 | 55.25 | 12:00 / 15:55 | 0 | None | 55.54 / 55.57 |
| TEVA 2026-10-21 | 40.4 | 09:30 / 15:10 | 9 | [40.44, 40.62] | 40.62 / 40.62 |
| GME 2026-10-22 | 25.01 | 13:00 / 15:30 | 5 | [25.05, 25.38] | 25.39 / 25.37 |
| GME 2026-10-23 | 24.78 | 15:45 / 15:55 | 0 | None | 24.82 / 24.83 |

Each successful window contains 78 consecutive five-minute bar starts from 09:30 through 15:55 ET. A touching bar locates a possible breach within its five minutes; it does not reveal the last-touch second, quotes, liquidity or an actual entry. CLMT daily Close 55.54 versus final 5m 55.57, GME Thursday 25.39 versus 25.37, and GME Friday 24.82 versus 24.83 are retained as differences, not reconciled away. All remain on the same side of the relevant stop. TEVA’s Closes agree at 40.62.

Including the final touching bar, five-minute Highs tighten the daily post-last-touch price outer bounds to **(55.25,55.61]** for CLMT, **(40.40,40.62]** for TEVA, **(25.01,25.38]** for Thursday GME and **(24.78,24.90]** for Friday GME. The lower stop endpoint is excluded. The corresponding positive per-share risk outer bounds are (0,0.36], (0,0.22], (0,0.37] and(0,0.12], using the stop known before each entry. These are bounds on possibilities, not executable quotes: the touching bar’s High might precede its last stop visit.

## Fixed tests and interpretation

The original four entry hypotheses and four management policies remain unchanged. Two additional diagnostic exposure bounds hold H1’s entry fixed: CLOSE_CONFIRMATION exits at the first violating Close (an idealized boundary, not a guaranteed executable fill); NEXT_OPEN_AFTER_CLOSE commits unconditionally to the following Open. A new evening stop cannot cancel that commitment. Costs 0/1/2 for hard/Close/next-Open and cost 2 for the existing review are explicit ordinal extra-convention counts, not fitted likelihoods or probabilities.

Two fixed delayed-entry rules are tested across all 26 episodes within the first three eligible completed sessions: (D1) a touch of the stop known at Open followed by a protective Close; (D2) two consecutive protective Closes. A trigger becomes available only after Close+60 minutes, then activates at the next eligible Open with positive risk against the stop known then. No same-Close fill, favorable hindsight price, re-entry or restart after failure is invented. D1 is a concrete stop-defined pullback/reclaim; D2 is a stop-defined recovery confirmation. Original H3/H4 supply pre-known breakout/pivot/MA alternatives. These diagnostics were defined by this repository analysis, not reported by Grimes. Pre-activation source actions stay unresolved; UNDERWAY before activation is an explicit counterexample.

## CLMT

**SOURCE:** `CLMT added long with stop 55.25`. Final reported state: **LONG / CLOSED / ENTERABLE**, latest stop **53.02**. Qualified conId `715002751` on NASDAQ, SMART/USD/STK.

### Chronology

| Label | Publication (ET) / session | Observation |
| --- | --- | --- |
| SOURCE | 2026-10-18T15:20:00-04:00 | OPEN_NEW_POSITION stop 55.25; ENTERABLE; alert-1:line-8 |
| SOURCE | 2026-10-19T18:19:00-04:00 | STOP_CHANGED 55.25 → 53.40; ENTERABLE; alert-2:line-11 |
| SOURCE | 2026-10-20T18:25:00-04:00 | STOP_CHANGED 53.40 → 53.02; ENTERABLE; alert-3:line-15 |
| SOURCE | 2026-10-21T18:50:00-04:00 | DROPPED; ENTERABLE; alert-4:line-21 |

**MARKET:** daily OHLCV surrounding the source decisions. Prices after source DROP remain contextual observations, not continued exposure.

| Session | Open | High | Low | Close | Native V |
| --- | --- | --- | --- | --- | --- |
| 2026-10-15 | 57.41 | 58.69 | 57.2 | 58.24 | 7036.0 |
| 2026-10-16 | 58.33 | 58.74 | 56.34 | 57.75 | 8185.0 |
| 2026-10-19 | 57.47 | 58.25 | 53.83 | 55.54 | 10322.0 |
| 2026-10-20 | 56.2 | 56.28 | 54.33 | 56.05 | 5086.0 |
| 2026-10-21 | 56.4 | 56.43 | 51.99 | 52.59 | 12797.0 |
| 2026-10-22 | 53.19 | 53.73 | 48.25 | 49.32 | 16659.0 |
| 2026-10-23 | 49.65 | 50.0 | 48.32 | 49.3 | 7196.0 |
| 2026-10-26 | 48.83 | 53.09 | 48.25 | 52.17 | 11177.0 |

**MARKET:** indicators available strictly before each assumed action clock under the late-email-bound schedule. Pivots show price, pivot date and later confirmation date; unavailable TEVA warmup remains unavailable. All clocks and feature-status reasons are retained in JSON.

| Event | Available session | ATR14 | SMA20 | SMA50 | Swing high | Swing low | SPY/QQQ20-session return |
| --- | --- | --- | --- | --- | --- | --- | --- |
| alert-1:line-8 | 2026-10-16 | 2.023571 | 55.781 | 52.9114 | 59.87 (2026-09-21; confirmed 2026-09-24) | 51.33 (2026-09-29; confirmed 2026-10-02) | 0.002048 / -0.016148 |
| alert-2:line-11 | 2026-10-19 | 2.186429 | 55.652 | 53.2326 | 59.16 (2026-10-14; confirmed 2026-10-19) | 51.33 (2026-09-29; confirmed 2026-10-02) | -0.009076 / -0.031168 |
| alert-3:line-15 | 2026-10-20 | 2.168571 | 55.6335 | 53.4442 | 59.16 (2026-10-14; confirmed 2026-10-19) | 51.33 (2026-09-29; confirmed 2026-10-02) | -0.005599 / -0.039908 |
| alert-4:line-21 | 2026-10-21 | 2.342143 | 55.544 | 53.5752 | 59.16 (2026-10-14; confirmed 2026-10-19) | 51.33 (2026-09-29; confirmed 2026-10-02) | 0.006877 / -0.0216 |

**HYPOTHESIS:** unchanged PR19 candidate entries and source-conflict clusters (final OPEN is a separate constraint).

| Entry hypothesis | Status / session / price | Full1R; partial1R; hold; review conflict clusters |
| --- | --- | --- |
| H1_NEXT_OPEN | CONSTRUCTED / 2026-10-19 / 57.47 | alert-2/alert-3; alert-2/alert-3; alert-2/alert-3; none |
| H2_ALERT_SESSION_CLOSE | REJECTED / None / None | unobserved; unobserved; unobserved; unobserved |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW / None / None | unobserved; unobserved; unobserved; unobserved |
| H4_PULLBACK | CONSTRUCTED / 2026-10-19 / 55.781 | alert-2/alert-3; alert-2/alert-3; alert-2/alert-3; none |

**HYPOTHESIS:** stop application at the unchanged next-Open entry.

H1 entry 57.47; stop known at activation 55.25; fixed reference risk 2.22 per share (1.09707 pre-entry ATR); +1R reference 59.69. First counterfactual protective breach: 2026-10-19 against 55.25, Open 57.47, Low 53.83, High 58.25, Close 55.54.

| Convention | Source compatibility | First Close violation | Exposure end bound / pending |
| --- | --- | --- | --- |
| INTRADAY_HARD_STOP | ROBUST_CONFLICT | see original paths | see original paths / n/a |
| CLOSE_REVIEW_NEXT_OPEN | FULLY_COMPATIBLE | see original paths | see original paths / n/a |
| CLOSE_CONFIRMATION | UNRESOLVED | 2026-10-21 | 2026-10-21T20:00:00+00:00 / False |
| NEXT_OPEN_AFTER_CLOSE | FULLY_COMPATIBLE | 2026-10-21 | 2026-10-22T13:30:00+00:00 / False |

**HYPOTHESIS:** availability-respecting delayed entries.

| Fixed rule | Trigger / next-Open entry | Whole history / after activation | Earlier source actions |
| --- | --- | --- | --- |
| RECLAIM_THEN_NEXT_OPEN | CONSTRUCTED / 2026-10-19 / 2026-10-20 | UNRESOLVED / UNRESOLVED | alert-2:line-11 |
| TWO_PROTECTIVE_CLOSES_THEN_NEXT_OPEN | CONSTRUCTED / 2026-10-20 / 2026-10-21 | UNRESOLVED / UNRESOLVED | alert-2:line-11, alert-3:line-15 |

**INFERENCE:** the three prioritized explanations below distinguish conditional market support from identification of actual practice.

| Hypothesis | Supporting evidence | Contradicting evidence | Missing evidence | Verdict / scope |
| --- | --- | --- | --- | --- |
| Closing confirmation, no mandatory full +1R exit | October 19 Low 53.83 breached55.25 but Close 55.54 recovered; October 20 Low 54.33 stayed above revised 53.40. | October 21 Close 52.59 breached53.02 before evening DROP; closure cause remains unobserved. | Actual entry, stop convention and execution record. | SUPPORTED — Conditional compatibility of continued stop management; not actual policy identification. |
| One late post-breach entry under an intraday hard stop | Daily Close recovered; a positive-risk protected entry after the last55.25 visit is possible. | The last touching five-minute bar starts15:55 ET; no complete protected bar remains. Existing H4 at 55.781 still conflicts. | Within-final-bar path and fill time; source does not report this entry. | PLAUSIBLE — Existential timing explanation, not an executable identified fill. |
| Pending plan activated after completed reclaim, at next Open | Fixed reclaim rule observes Monday Close, then activates Tuesday Open 56.20 against known 53.40. | Monday stop revision precedes activation; Wednesday stop-out precedes source DROP. Source ADDED is not proof of a pending plan. | Whether ENTERABLE carried an actual position and activation instruction. | NOT_IDENTIFIABLE — Requires intended-plan interpretation and leaves DROP attribution unresolved. |

For an entry after Monday’s last55.25 visit, daily OHLC only bounds positive-risk prices to **(55.25,58.25]**. The intraday capture narrows last-touch timing to 15:55–16:00 ET, leaving no complete protected bar afterward; neither the daily High nor the final Close is a demonstrated entry. Wednesday’s51.99 Low below 53.02 invalidates continued hard-stop exposure after that session, but only a source DROP follows. **Conditionally explained continuation; actual entry and exit cause unresolved.**

## TEVA

**SOURCE:** `TEVA added long with stop 40.40`. Final reported state: **LONG / CLOSED / ENTERABLE**, latest stop **39.05**. Qualified conId `922990633` on NYSE, SMART/USD/STK.

### Chronology

| Label | Publication (ET) / session | Observation |
| --- | --- | --- |
| SOURCE | 2026-10-18T15:20:00-04:00 | OPEN_NEW_POSITION stop 40.40; ENTERABLE; alert-1:line-9 |
| SOURCE | 2026-10-21T18:50:00-04:00 | STOP_CHANGED 40.40 → 39.35; ENTERABLE; alert-4:line-14 |
| SOURCE | 2026-10-22T18:27:00-04:00 | STOP_CHANGED 39.35 → 39.05; ENTERABLE; alert-5:line-13 |
| SOURCE | UNKNOWN | DROPPED; ENTERABLE; alert-6:line-26 |

**MARKET:** daily OHLCV surrounding the source decisions. Prices after source DROP remain contextual observations, not continued exposure.

| Session | Open | High | Low | Close | Native V |
| --- | --- | --- | --- | --- | --- |
| 2026-10-15 | 41.3 | 41.85 | 41.03 | 41.11 | 59163.0 |
| 2026-10-16 | 41.26 | 41.7 | 40.96 | 41.5 | 43903.0 |
| 2026-10-19 | 41.42 | 41.88 | 41.25 | 41.31 | 19679.0 |
| 2026-10-20 | 41.48 | 41.59 | 40.8 | 40.85 | 31938.0 |
| 2026-10-21 | 40.1 | 41.09 | 39.5 | 40.62 | 33617.0 |
| 2026-10-22 | 40.2 | 40.45 | 39.58 | 40.21 | 28782.0 |
| 2026-10-23 | 39.75 | 39.84 | 39.1 | 39.41 | 28332.0 |
| 2026-10-26 | 39.22 | 40.12 | 39.15 | 39.95 | 39078.0 |

**MARKET:** indicators available strictly before each assumed action clock under the late-email-bound schedule. Pivots show price, pivot date and later confirmation date; unavailable TEVA warmup remains unavailable. All clocks and feature-status reasons are retained in JSON.

| Event | Available session | ATR14 | SMA20 | SMA50 | Swing high | Swing low | SPY/QQQ20-session return |
| --- | --- | --- | --- | --- | --- | --- | --- |
| alert-1:line-9 | 2026-10-16 | 1.131429 | 39.96 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | 0.002048 / -0.016148 |
| alert-4:line-14 | 2026-10-21 | 1.080714 | 40.1695 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | 0.006877 / -0.0216 |
| alert-5:line-13 | 2026-10-22 | 1.100714 | 40.169 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | -0.004197 / -0.049427 |
| alert-6:line-26 | 2026-10-23 | 1.125714 | 40.18 | UNAVAILABLE | UNAVAILABLE | UNAVAILABLE | -0.014753 / -0.053862 |

**HYPOTHESIS:** unchanged PR19 candidate entries and source-conflict clusters (final OPEN is a separate constraint).

| Entry hypothesis | Status / session / price | Full1R; partial1R; hold; review conflict clusters |
| --- | --- | --- |
| H1_NEXT_OPEN | CONSTRUCTED / 2026-10-19 / 41.42 | alert-4/alert-5; alert-4/alert-5; alert-4/alert-5; none |
| H2_ALERT_SESSION_CLOSE | REJECTED / None / None | unobserved; unobserved; unobserved; unobserved |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW / None / None | unobserved; unobserved; unobserved; unobserved |
| H4_PULLBACK | REJECTED / None / None | unobserved; unobserved; unobserved; unobserved |

**HYPOTHESIS:** stop application at the unchanged next-Open entry.

H1 entry 41.42; stop known at activation 40.4; fixed reference risk 1.02 per share (0.901515 pre-entry ATR); +1R reference 42.44. First counterfactual protective breach: 2026-10-21 against 40.4, Open 40.1, Low 39.5, High 41.09, Close 40.62.

| Convention | Source compatibility | First Close violation | Exposure end bound / pending |
| --- | --- | --- | --- |
| INTRADAY_HARD_STOP | ROBUST_CONFLICT | see original paths | see original paths / n/a |
| CLOSE_REVIEW_NEXT_OPEN | FULLY_COMPATIBLE | see original paths | see original paths / n/a |
| CLOSE_CONFIRMATION | FULLY_COMPATIBLE | None | None / False |
| NEXT_OPEN_AFTER_CLOSE | FULLY_COMPATIBLE | None | None / False |

**HYPOTHESIS:** availability-respecting delayed entries.

| Fixed rule | Trigger / next-Open entry | Whole history / after activation | Earlier source actions |
| --- | --- | --- | --- |
| RECLAIM_THEN_NEXT_OPEN | CONSTRUCTED / 2026-10-21 / 2026-10-22 | UNRESOLVED / FULLY_COMPATIBLE | alert-4:line-14 |
| TWO_PROTECTIVE_CLOSES_THEN_NEXT_OPEN | REJECTED_NONPROTECTIVE_ENTRY / 2026-10-20 / None | not comparable | none |

**INFERENCE:** the three prioritized explanations below distinguish conditional market support from identification of actual practice.

| Hypothesis | Supporting evidence | Contradicting evidence | Missing evidence | Verdict / scope |
| --- | --- | --- | --- | --- |
| Closing confirmation, no mandatory full +1R exit | October 21 Open 40.10 and Low 39.50 breached40.40 but Close 40.62 recovered. Later Lows39.58 and 39.10 exceeded the known revised stops39.35 and 39.05. | None in observed later source constraints; this does not establish the actual convention. | Actual position/order record; weekly publication time. | SUPPORTED — Conditional price/source compatibility only. |
| One entry after the Wednesday gap-and-reclaim | Last40.40 touching bar starts15:10 ET; nine complete later bars span 40.44–40.62 and remain protected. Later daily Lows respect revised stops. | No fill report establishes that the trade waited until Wednesday. | Execution time, executable quotes and treatment of earlier ENTERABLE status. | PLAUSIBLE — Market permits a delayed single entry; the source does not identify one. |
| Pending reclaim plan, activated Thursday Open | Fixed reclaim then next-Open rule enters October 22 at 40.20 after Wednesday stop 39.35 was available. | October 21 stop revision occurs before activation, so it is not compatible evidence of an already-held position. | Whether the stop revision managed a pending instruction or actual exposure. | NOT_IDENTIFIABLE — Causal trigger but extra semantic assumption. |

A post-Wednesday-last-touch entry has the daily existential price bound **(40.40,41.09]**; the nine fully protected later five-minute bars actually span **40.44–40.62**. Thursday and Friday remain protected after the respective known revisions. This is stronger timing evidence than CLMT, but still no fill.

TEVA has only 31 admitted daily sessions, September 14–October 26. The [issuer’s September 14 release](https://ir.tevapharm.com/news-and-events/press-releases/press-release-details/2026/Teva-Begins-Trading-Ordinary-Shares-Directly-on-the-NYSE-Marking-a-Milestone-in-its-Pivot-to-Growth-Strategy/default.aspx) dates the direct NYSE ordinary-share listing to that day. The [September 14 SEC8-K, item8.01](https://www.sec.gov/Archives/edgar/data/818686/000119312526390562/d503082d8k.htm) states each prior ADS exchanged for one ordinary share with the same ticker. Alignment with the retained contract’s first bar supports an identity-boundary explanation for limited warmup, not proof of IBKR’s truncation mechanism. The one-for-one conversion provides no price rescaling remedy for the October 21 stop breach. No old ADS contract is inferred or spliced; SMA50 and long-window pivots remain missing. **Conditionally explained continuation; actual entry/convention unidentifiable.**

## GME

**SOURCE:** `GME added long with stop 25.01`. Final reported state: **LONG / CLOSED / ENTERABLE**, latest stop **24.40**. Qualified conId `36285627` on NYSE, SMART/USD/STK.

### Chronology

| Label | Publication (ET) / session | Observation |
| --- | --- | --- |
| SOURCE | 2026-10-21T18:50:00-04:00 | OPEN_NEW_POSITION stop 25.01; ENTERABLE; alert-4:line-7 |
| SOURCE | 2026-10-22T18:27:00-04:00 | STOP_CHANGED 25.01 → 24.78; ENTERABLE; alert-5:line-11 |
| SOURCE | UNKNOWN | STOP_CHANGED 24.78 → 24.40; ENTERABLE; alert-6:line-16 |
| SOURCE | 2026-10-26T18:10:00-04:00 | DROPPED; ENTERABLE; alert-7:line-20 |

**MARKET:** daily OHLCV surrounding the source decisions. Prices after source DROP remain contextual observations, not continued exposure.

| Session | Open | High | Low | Close | Native V |
| --- | --- | --- | --- | --- | --- |
| 2026-10-15 | 26.75 | 28.3 | 26.58 | 28.02 | 87588.0 |
| 2026-10-16 | 28.04 | 28.09 | 26.72 | 26.81 | 82178.0 |
| 2026-10-19 | 26.65 | 27.16 | 26.15 | 26.44 | 45902.0 |
| 2026-10-20 | 25.73 | 26.48 | 25.3 | 26.47 | 59744.0 |
| 2026-10-21 | 26.39 | 26.86 | 25.95 | 26.29 | 46549.0 |
| 2026-10-22 | 26.0 | 26.25 | 24.61 | 25.39 | 79404.0 |
| 2026-10-23 | 25.34 | 25.61 | 24.68 | 24.82 | 44235.0 |
| 2026-10-26 | 24.82 | 24.99 | 23.78 | 23.9 | 58036.0 |

**MARKET:** indicators available strictly before each assumed action clock under the late-email-bound schedule. Pivots show price, pivot date and later confirmation date; unavailable TEVA warmup remains unavailable. All clocks and feature-status reasons are retained in JSON.

| Event | Available session | ATR14 | SMA20 | SMA50 | Swing high | Swing low | SPY/QQQ20-session return |
| --- | --- | --- | --- | --- | --- | --- | --- |
| alert-4:line-7 | 2026-10-21 | 1.183571 | 25.582 | 22.0914 | 28.3 (2026-10-15; confirmed 2026-10-20) | 24.04 (2026-10-08; confirmed 2026-10-13) | 0.006877 / -0.0216 |
| alert-5:line-11 | 2026-10-22 | 1.244286 | 25.6005 | 22.2284 | 28.3 (2026-10-15; confirmed 2026-10-20) | 24.04 (2026-10-08; confirmed 2026-10-13) | -0.004197 / -0.049427 |
| alert-6:line-16 | 2026-10-23 | 1.233571 | 25.672 | 22.3534 | 28.3 (2026-10-15; confirmed 2026-10-20) | 24.04 (2026-10-08; confirmed 2026-10-13) | -0.014753 / -0.053862 |
| alert-7:line-20 | 2026-10-26 | 1.265 | 25.669 | 22.4582 | 28.3 (2026-10-15; confirmed 2026-10-20) | 24.04 (2026-10-08; confirmed 2026-10-13) | -0.000313 / -0.033033 |

**HYPOTHESIS:** unchanged PR19 candidate entries and source-conflict clusters (final OPEN is a separate constraint).

| Entry hypothesis | Status / session / price | Full1R; partial1R; hold; review conflict clusters |
| --- | --- | --- |
| H1_NEXT_OPEN | CONSTRUCTED / 2026-10-22 / 26.0 | alert-5/alert-6; alert-5/alert-6; alert-5/alert-6; none |
| H2_ALERT_SESSION_CLOSE | REJECTED / None / None | unobserved; unobserved; unobserved; unobserved |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW / None / None | unobserved; unobserved; unobserved; unobserved |
| H4_PULLBACK | CONSTRUCTED / 2026-10-22 / 25.582 | alert-5/alert-6; alert-5/alert-6; alert-5/alert-6; none |

**HYPOTHESIS:** stop application at the unchanged next-Open entry.

H1 entry 26; stop known at activation 25.01; fixed reference risk 0.99 per share (0.836451 pre-entry ATR); +1R reference 26.99. First counterfactual protective breach: 2026-10-22 against 25.01, Open 26.0, Low 24.61, High 26.25, Close 25.39.

| Convention | Source compatibility | First Close violation | Exposure end bound / pending |
| --- | --- | --- | --- |
| INTRADAY_HARD_STOP | ROBUST_CONFLICT | see original paths | see original paths / n/a |
| CLOSE_REVIEW_NEXT_OPEN | FULLY_COMPATIBLE | see original paths | see original paths / n/a |
| CLOSE_CONFIRMATION | UNRESOLVED | 2026-10-26 | 2026-10-26T20:00:00+00:00 / False |
| NEXT_OPEN_AFTER_CLOSE | FULLY_COMPATIBLE | 2026-10-26 | 2026-10-27T13:30:00+00:00 / True |

**HYPOTHESIS:** availability-respecting delayed entries.

| Fixed rule | Trigger / next-Open entry | Whole history / after activation | Earlier source actions |
| --- | --- | --- | --- |
| RECLAIM_THEN_NEXT_OPEN | CONSTRUCTED / 2026-10-22 / 2026-10-23 | ROBUST_CONFLICT / ROBUST_CONFLICT | alert-5:line-11 |
| TWO_PROTECTIVE_CLOSES_THEN_NEXT_OPEN | CONSTRUCTED / 2026-10-23 / 2026-10-26 | UNRESOLVED / UNRESOLVED | alert-5:line-11, alert-6:line-16 |

**INFERENCE:** the three prioritized explanations below distinguish conditional market support from identification of actual practice.

| Hypothesis | Supporting evidence | Contradicting evidence | Missing evidence | Verdict / scope |
| --- | --- | --- | --- | --- |
| Closing confirmation, no mandatory full +1R exit | Thursday Close 25.39 exceeded25.01; Friday Close 24.82 exceeded24.78 even under the late weekly clock. | Monday Close 23.90 breached24.40 before evening DROP, leaving closure attribution unresolved. | Actual closing instruction, entry and DROP execution. | SUPPORTED — Explains continued revisions under all three clocks, not the actual exit cause. |
| One Thursday entry after last old-stop visit | Five complete protected bars after 15:30 ET span 25.05–25.38; early weekly24.40 then protects Friday Low 24.68. | Late or Friday-Close weekly clocks leave24.78 active during Friday Low 24.68, stopping that same position before continued management. | Weekly publication clock, fill and intrabar order. | PLAUSIBLE — Survives only the early weekly clock; contradicted for late/Friday-Close clocks. |
| Pending plan after two protective Closes, next-Open activation | Thursday and Friday close above stops already known at their Opens; fixed rule activates Monday Open 24.82 against24.40. | Thursday and weekly stop revisions precede activation; Monday hard stop triggers before DROP. This explains no earlier held exposure. | Plan activation evidence and source DROP cause. | NOT_IDENTIFIABLE — Availability-respecting delayed entry; source remains OPEN from original ADD. |

Thursday’s post-last-touch daily bound is **(25.01,26.25]**, with five complete protected bars spanning **25.05–25.38** after 15:30–15:35 ET. This alone fails under late/Friday-Close weekly publication: Friday Low 24.68 crosses the still-active24.78. Friday’s post-last-touch daily bound is **(24.78,25.61]**, but its last touch also extends into15:55–16:00 ET and requires treating Thursday’s revision as a pre-entry plan update. **Closing confirmation conditionally explains continuation under all clocks; a Thursday late-entry-only explanation is clock-dependent.**

## EBAY

**SOURCE:** `EBAY added long with stop 119.20`. Final reported state: **LONG / OPEN / ENTERABLE**, latest stop **117.50**. Qualified conId `4347086` on NASDAQ, SMART/USD/STK.

### Chronology

| Label | Publication (ET) / session | Observation |
| --- | --- | --- |
| SOURCE | UNKNOWN | OPEN_NEW_POSITION stop 119.20; ENTERABLE; alert-6:line-9 |
| SOURCE | 2026-10-26T18:10:00-04:00 | STOP_CHANGED 119.20 → 117.50; ENTERABLE; alert-7:line-13 |

**MARKET:** daily OHLCV surrounding the source decisions. Prices after source DROP remain contextual observations, not continued exposure.

| Session | Open | High | Low | Close | Native V |
| --- | --- | --- | --- | --- | --- |
| 2026-10-15 | 118.14 | 124.59 | 118.04 | 122.91 | 41369.0 |
| 2026-10-16 | 123.82 | 124.09 | 119.2 | 120.28 | 20457.0 |
| 2026-10-19 | 119.79 | 121.15 | 119.23 | 120.47 | 18479.0 |
| 2026-10-20 | 121.46 | 122.16 | 119.9 | 121.19 | 17839.0 |
| 2026-10-21 | 119.46 | 123.75 | 119.21 | 122.9 | 16366.0 |
| 2026-10-22 | 122.53 | 123.03 | 120.37 | 122.04 | 14791.0 |
| 2026-10-23 | 120.84 | 122.19 | 120.32 | 121.41 | 12578.0 |
| 2026-10-26 | 121.24 | 121.61 | 117.87 | 118.62 | 19764.0 |

**MARKET:** indicators available strictly before each assumed action clock under the late-email-bound schedule. Pivots show price, pivot date and later confirmation date; unavailable TEVA warmup remains unavailable. All clocks and feature-status reasons are retained in JSON.

| Event | Available session | ATR14 | SMA20 | SMA50 | Swing high | Swing low | SPY/QQQ20-session return |
| --- | --- | --- | --- | --- | --- | --- | --- |
| alert-6:line-9 | 2026-10-23 | 3.503571 | 113.799 | 109.152 | 124.59 (2026-10-15; confirmed 2026-10-20) | 104.61 (2026-09-30; confirmed 2026-10-05) | -0.014753 / -0.053862 |
| alert-7:line-13 | 2026-10-26 | 3.589286 | 114.364 | 109.4616 | 124.59 (2026-10-15; confirmed 2026-10-20) | 104.61 (2026-09-30; confirmed 2026-10-05) | -0.000313 / -0.033033 |

**HYPOTHESIS:** unchanged PR19 candidate entries and source-conflict clusters (final OPEN is a separate constraint).

| Entry hypothesis | Status / session / price | Full1R; partial1R; hold; review conflict clusters |
| --- | --- | --- |
| H1_NEXT_OPEN | CONSTRUCTED / 2026-10-26 / 121.24 | FINAL_SOURCE_OPEN/alert-7; FINAL_SOURCE_OPEN/alert-7; FINAL_SOURCE_OPEN/alert-7; none |
| H2_ALERT_SESSION_CLOSE | REJECTED / None / None | unobserved; unobserved; unobserved; unobserved |
| H3_CONFIRMATION | MISSING_OR_FUTURE_TRIGGER_SESSION / None / None | unobserved; unobserved; unobserved; unobserved |
| H4_PULLBACK | REJECTED / None / None | unobserved; unobserved; unobserved; unobserved |

**HYPOTHESIS:** stop application at the unchanged next-Open entry.

H1 entry 121.24; stop known at activation 119.2; fixed reference risk 2.04 per share (0.582263 pre-entry ATR); +1R reference 123.28. First counterfactual protective breach: 2026-10-26 against 119.2, Open 121.24, Low 117.87, High 121.61, Close 118.62.

| Convention | Source compatibility | First Close violation | Exposure end bound / pending |
| --- | --- | --- | --- |
| INTRADAY_HARD_STOP | ROBUST_CONFLICT | see original paths | see original paths / n/a |
| CLOSE_REVIEW_NEXT_OPEN | FULLY_COMPATIBLE | see original paths | see original paths / n/a |
| CLOSE_CONFIRMATION | ROBUST_CONFLICT | 2026-10-26 | 2026-10-26T20:00:00+00:00 / False |
| NEXT_OPEN_AFTER_CLOSE | FULLY_COMPATIBLE | 2026-10-26 | 2026-10-27T13:30:00+00:00 / True |

**HYPOTHESIS:** availability-respecting delayed entries.

| Fixed rule | Trigger / next-Open entry | Whole history / after activation | Earlier source actions |
| --- | --- | --- | --- |
| RECLAIM_THEN_NEXT_OPEN | NO_OBSERVED_TRIGGER / None / None | not comparable | none |
| TWO_PROTECTIVE_CLOSES_THEN_NEXT_OPEN | NO_OBSERVED_TRIGGER / None / None | not comparable | none |

**INFERENCE:** the three prioritized explanations below distinguish conditional market support from identification of actual practice.

| Hypothesis | Supporting evidence | Contradicting evidence | Missing evidence | Verdict / scope |
| --- | --- | --- | --- | --- |
| Unconditional next-session exit after a closing violation | Monday Close 118.62 breaches119.20; queued Tuesday exit is outside fixed cutoff, permitting Monday evening source OPEN. | No next-session execution is observed; later117.50 revision cannot cancel this queued exit under the tested rule. | October 27 fill and next source alert; evidence here ends October 26. | PLAUSIBLE — Right-censored commitment, not demonstrated survival after the next Open. |
| ENTERABLE pending plan with no entry yet | Source never reports UNDERWAY; an unfilled plan could receive an evening stop revision. | Source says ADDED and remains OPEN. Neither tested fixed delayed rule activates EBAY; absence of a trigger is not evidence of no actual trade. | Actual fill/activation instruction and meaning of ENTERABLE in this episode. | NOT_IDENTIFIABLE — Competing explanation; never replaces source status. |
| Bounded discretionary next-Open review | Existing PR19 CLOSE_REVIEW_NEXT_OPEN retains exposure through the Monday evening revision. | Requires ignoring intraday/closing stop breaches; flexibility improves fit without identifying practice. | Actual review policy, execution and following Open. | NOT_IDENTIFIABLE — Fixed cost 2 exploratory rule, no per-trade override or unlimited discretion. |

**No positive-risk entry before Monday Close can survive that Close under the unchanged119.20 hard stop:** Close 118.62 is already adverse. Intraday ordering cannot rescue an already-held long, and closing confirmation also exits before the evening revision. Applying117.50 to earlier prices would be hindsight. The independent operator Low 117.87 anchor matches the native session but is not a complete basis audit. NEXT_OPEN_AFTER_CLOSE has a pending October 27 exit; fixed cutoff supplies neither that fill nor a later source constraint. **Hard-stop contradiction remains for already-held exposure; deferred exit or pending-plan interpretations are conditional and unidentifiable.**

## CDE

**SOURCE:** `CDE added short with stop 16.40`. Final reported state: **SHORT / OPEN / UNDERWAY**, latest stop **13.90**. Qualified conId `60532895` on NYSE, SMART/USD/STK.

### Chronology

| Label | Publication (ET) / session | Observation |
| --- | --- | --- |
| SOURCE | 2026-10-18T15:20:00-04:00 | OPEN_NEW_POSITION stop 16.40; ENTERABLE; alert-1:line-11 |
| SOURCE | 2026-10-19T18:19:00-04:00 | STOP_CHANGED 16.40 → 16.24; ENTERABLE; alert-2:line-12 |
| SOURCE | 2026-10-22T18:27:00-04:00 | STOP_CHANGED 16.24 → 14.30; ENTERABLE; alert-5:line-19 |
| SOURCE | 2026-10-22T18:27:00-04:00 | SETUP_CHANGED; UNDERWAY; alert-5:line-27 |
| SOURCE | UNKNOWN | STOP_CHANGED 14.30 → 13.90; UNDERWAY; alert-6:line-20 |

**MARKET:** daily OHLCV surrounding the source decisions. Prices after source DROP remain contextual observations, not continued exposure.

| Session | Open | High | Low | Close | Native V |
| --- | --- | --- | --- | --- | --- |
| 2026-10-15 | 15.11 | 15.435 | 14.675 | 15.41 | 237071.0 |
| 2026-10-16 | 15.29 | 16.07 | 15.16 | 15.47 | 289517.0 |
| 2026-10-19 | 15.46 | 15.59 | 15.265 | 15.33 | 291500.0 |
| 2026-10-20 | 15.12 | 15.89 | 14.98 | 15.13 | 271325.0 |
| 2026-10-21 | 15.295 | 15.4473 | 14.855 | 15.13 | 318090.0 |
| 2026-10-22 | 14.51 | 14.51 | 13.78 | 13.88 | 356812.0 |
| 2026-10-23 | 13.745 | 13.765 | 13.155 | 13.45 | 350574.0 |
| 2026-10-26 | 13.51 | 13.785 | 13.12 | 13.64 | 334269.0 |

**MARKET:** indicators available strictly before each assumed action clock under the late-email-bound schedule. Pivots show price, pivot date and later confirmation date; unavailable TEVA warmup remains unavailable. All clocks and feature-status reasons are retained in JSON.

| Event | Available session | ATR14 | SMA20 | SMA50 | Swing high | Swing low | SPY/QQQ20-session return |
| --- | --- | --- | --- | --- | --- | --- | --- |
| alert-1:line-11 | 2026-10-16 | 0.7725 | 17.481 | 19.0852 | 17.495 (2026-10-09; confirmed 2026-10-14) | 16.23 (2026-10-07; confirmed 2026-10-12) | 0.002048 / -0.016148 |
| alert-2:line-12 | 2026-10-19 | 0.737857 | 17.2715 | 19.044 | 17.495 (2026-10-09; confirmed 2026-10-14) | 16.23 (2026-10-07; confirmed 2026-10-12) | -0.009076 / -0.031168 |
| alert-5:line-19 | 2026-10-22 | 0.822307 | 16.541 | 18.8162 | 17.495 (2026-10-09; confirmed 2026-10-14) | 14.675 (2026-10-15; confirmed 2026-10-20) | -0.004197 / -0.049427 |
| alert-5:line-27 | 2026-10-22 | 0.822307 | 16.541 | 18.8162 | 17.495 (2026-10-09; confirmed 2026-10-14) | 14.675 (2026-10-15; confirmed 2026-10-20) | -0.004197 / -0.049427 |
| alert-6:line-20 | 2026-10-23 | 0.798379 | 16.2525 | 18.7162 | 17.495 (2026-10-09; confirmed 2026-10-14) | 14.675 (2026-10-15; confirmed 2026-10-20) | -0.014753 / -0.053862 |

**HYPOTHESIS:** unchanged PR19 candidate entries and source-conflict clusters (final OPEN is a separate constraint).

| Entry hypothesis | Status / session / price | Full1R; partial1R; hold; review conflict clusters |
| --- | --- | --- |
| H1_NEXT_OPEN | CONSTRUCTED / 2026-10-19 / 15.46 | FINAL_SOURCE_OPEN/alert-5/alert-6; none; none; none |
| H2_ALERT_SESSION_CLOSE | REJECTED / None / None | unobserved; unobserved; unobserved; unobserved |
| H3_CONFIRMATION | NOT_TRIGGERED_IN_FIXED_WINDOW / None / None | unobserved; unobserved; unobserved; unobserved |
| H4_PULLBACK | REJECTED / None / None | unobserved; unobserved; unobserved; unobserved |

**HYPOTHESIS:** stop application at the unchanged next-Open entry.

H1 entry 15.46; stop known at activation 16.4; fixed reference risk 0.94 per share (1.216828 pre-entry ATR); +1R reference 14.52. No protective-stop breach in the retained exposure window.

| Convention | Source compatibility | First Close violation | Exposure end bound / pending |
| --- | --- | --- | --- |
| INTRADAY_HARD_STOP | FULLY_COMPATIBLE | see original paths | see original paths / n/a |
| CLOSE_REVIEW_NEXT_OPEN | FULLY_COMPATIBLE | see original paths | see original paths / n/a |
| CLOSE_CONFIRMATION | FULLY_COMPATIBLE | None | None / False |
| NEXT_OPEN_AFTER_CLOSE | FULLY_COMPATIBLE | None | None / False |

**HYPOTHESIS:** availability-respecting delayed entries.

| Fixed rule | Trigger / next-Open entry | Whole history / after activation | Earlier source actions |
| --- | --- | --- | --- |
| RECLAIM_THEN_NEXT_OPEN | NO_OBSERVED_TRIGGER / None / None | not comparable | none |
| TWO_PROTECTIVE_CLOSES_THEN_NEXT_OPEN | CONSTRUCTED / 2026-10-20 / 2026-10-21 | UNRESOLVED / FULLY_COMPATIBLE | alert-2:line-12 |

**INFERENCE:** the three prioritized explanations below distinguish conditional market support from identification of actual practice.

| Hypothesis | Supporting evidence | Contradicting evidence | Missing evidence | Verdict / scope |
| --- | --- | --- | --- | --- |
| Hold with reported protective stops | After next-Open short 15.46, daily Highs remain below the stop known at each Open; source later reports UNDERWAY and OPEN. | No protective-stop contradiction in retained path. | Actual fill, size and stop order type. | SUPPORTED — Compatible conditional hard-stop explanation. |
| Partial +1R realization with protected residual runner | First target14.52 is reached October 22; residual remains protected and compatible with continued source management. | The illustrative50% fraction is not observed. | Any sizing or partial-fill evidence. | PLAUSIBLE — Observationally equivalent source-status explanation to holding. |
| Mandatory full exit at +1R | The hypothetical next-Open entry reaches+1R. | Full exit before the October 22 UNDERWAY/stop cluster conflicts with later weekly management and final OPEN. | An alternative actual entry could change initialR; none is established. | CONTRADICTED — Fixed-entry target convention, not evidence against hard protective stops. |

At H1 short 15.46 with initial stop 16.40, initial reference risk is 0.94 and +1R level 14.52. October 22 Open 14.51 reaches that target before the evening stop/UNDERWAY cluster. All intervening Highs remain below the contemporaneously known protective stops. Full realization therefore causes a **TARGET_EXIT_CONVENTION_CONFLICT**, not a protective-stop failure. A partial runner and a full hold are both compatible; no observed sizing distinguishes them. Source remains **SHORT / OPEN / UNDERWAY /13.90**.

## Falsified shortcuts and what remains unresolved

For all four H1 entries, the first protective-stop breach precedes any +1R reach. A residual runner with the same hard protective stop cannot survive that breach. Unreported partial sizing alone therefore does not fix these contradictions; it would also require a different entry or stop convention. CDE supplies a genuine partial/hold versus full-target distinction.

Price-only multiplication large enough to remove the first breaches would require factors greater than 55.25/53.83≈1.02638 for CLMT, 40.40/39.50≈1.02278 for TEVA, 25.01/24.61≈1.01625 for GME and 119.20/117.87≈1.01128 for EBAY. These are counterfactual inequalities, not corrections; no such factor is applied. The nominal EBAY anchor and TEVA’s one-for-one identity evidence argue against arbitrary scale repairs. Corporate-action completeness remains limited for the other cases.

ENTERABLE’s source meaning is not identified as either unfilled plan or executed position by these alerts alone. The ledger’s OPEN facts remain authoritative. A stop may be a risk reference, a closing threshold or a broker order; fit to the same sparse alerts cannot choose between all of these. **CLOSE_REVIEW_NEXT_OPEN is an exploratory explanation, not evidence of Grimes’ actual stop-order convention.** The findings improve failure diagnosis and bound the remaining questions; they do not establish a universal profitable strategy.

See [cross-trade tests and reproduction](GRIMES_CROSS_TRADE_INFERENCE.md).
