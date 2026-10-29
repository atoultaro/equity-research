# Grimes walk-forward evaluation — PR9C

**This is a retrospective dry run, with zero fresh out-of-sample observations.** The original seven alerts informed the hypotheses in PR16–PR20. Enforced feature cutoffs do not undo that hypothesis-selection contamination. These results validate the forecasting workflow and expose counterexamples; they do not establish prospective skill.

Each forecaster subprocess receives only a frozen prefix view. The preparer seals its prediction before releasing the next original alert into a separate reveal bundle. Known dated alerts use a pre-alert completed-bar cutoff; publication metadata is used retrospectively to define that experimental schedule. For the unknown weekly publication, the cutoff is the prior alert’s upper availability bound, with no Friday market bars admitted. Those are explicit historical design choices, not a claim that the researcher scheduled live forecasts before these alerts.

## Fixed decision hypotheses

| Model | Frozen decision rule | Important limit |
| --- | --- | --- |
| A | Intraday stop touch → hypothetical exit; next relevant source action predicted DROP | Next-Open activation assumption and exit→newsletter-DROP bridge are unverified |
| B | Closing violation → idealized closing decision/exit | A recovered intraday touch is insufficient; exact closing execution is not guaranteed |
| C | Closing violation → irrevocable next-Open exit commitment | A source alert before that Open can still continue management; an evening revision cannot cancel the commitment |
| D | One next-Open review; retain only if Open protects against then-known stop | Only one discretionary retention per episode; second violation queues unconditional exit |
| E | Fixed ATR/structure stop proposals and directional-progress UNDERWAY condition | Opening-reference ATR progress is not actual initial risk or +1R; no fitted probabilities |

A–D predict a broad continuation set when still hypothetically active. Set coverage is reported separately from point-category correctness; a three-category set is not credited as a correct exact action. None predicts stop levels. Pending C/D forecasts include predeclared publication-time branches. Evaluation resolves those branches from timing metadata, never by choosing the action or clock that fits. D stays unresolved when the required next Open is absent.

## Descriptive comparisons

All rows within one alert share a cluster. The three timing schedules are sensitivity cases, never independent samples. The tables show trade-level descriptives and six shared-alert-cluster outcomes. A cluster with both compatible and contradictory trade forecasts is a contradiction for the strict all-trades cluster check. Discriminating wins/losses use disjoint forecast sets selected without inspecting actual action categories; conditional branches use only publication metadata. Mixed distinguishing clusters are retained as mixed.

| Clock | Model | Exact action correct | Action-set coverage | Stop direction | Direction on actual stop revisions | Mean abs stop error / forecast ATR | Interval hits | Abstain/unresolved |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EARLY | A_HARD_STOP | 8/15 | 50/61 | 0/0 | 0/0 | — | 0/0 | 0 |
| EARLY | B_CLOSE_CONFIRMATION | 7/8 | 55/61 | 0/0 | 0/0 | — | 0/0 | 0 |
| EARLY | C_NEXT_OPEN | 0/0 | 49/61 | 0/0 | 0/0 | — | 0/0 | 0 |
| EARLY | D_BOUNDED_REVIEW | 0/0 | 49/61 | 0/0 | 0/0 | — | 0/0 | 0 |
| EARLY | E_PRICE_STRUCTURE | 37/61 | 37/61 | 31/53 | 4/26 | 0.6559 | 3/26 | 0 |
| CLOSE_BOUNDARY | A_HARD_STOP | 8/15 | 50/61 | 0/0 | 0/0 | — | 0/0 | 0 |
| CLOSE_BOUNDARY | B_CLOSE_CONFIRMATION | 7/8 | 55/61 | 0/0 | 0/0 | — | 0/0 | 0 |
| CLOSE_BOUNDARY | C_NEXT_OPEN | 0/0 | 49/61 | 0/0 | 0/0 | — | 0/0 | 0 |
| CLOSE_BOUNDARY | D_BOUNDED_REVIEW | 0/0 | 49/61 | 0/0 | 0/0 | — | 0/0 | 0 |
| CLOSE_BOUNDARY | E_PRICE_STRUCTURE | 37/61 | 37/61 | 31/53 | 4/26 | 0.6559 | 3/26 | 0 |
| LATE | A_HARD_STOP | 8/15 | 50/61 | 0/0 | 0/0 | — | 0/0 | 0 |
| LATE | B_CLOSE_CONFIRMATION | 7/8 | 55/61 | 0/0 | 0/0 | — | 0/0 | 0 |
| LATE | C_NEXT_OPEN | 0/0 | 49/61 | 0/0 | 0/0 | — | 0/0 | 0 |
| LATE | D_BOUNDED_REVIEW | 0/0 | 49/61 | 0/0 | 0/0 | — | 0/0 | 0 |
| LATE | E_PRICE_STRUCTURE | 37/61 | 37/61 | 31/53 | 4/26 | 0.6559 | 3/26 | 0 |

The 61 trade/alert observations contain 20 CONTINUED_MANAGEMENT, 12 DROPPED, 22 NOT_MENTIONED, 7 UNDERWAY; there are 27 actual stop revisions. These observations share only 6 alerts. Class frequencies matter: a no-mention forecast can be correct without reproducing a management decision.


Stop errors use the ATR frozen at prediction, and include wrong-direction predictions where a numeric level was offered. Missing levels remain abstentions, not zero error. Direction accuracy includes NO_ADJUSTMENT, so the actual-revision-only denominator is shown separately. No significance tests or calibrated probabilities are reported.

| Clock | Model | Shared clusters: compatible / contradiction / unresolved | Discriminating trade wins / losses | Discriminating clusters: support / contradict / mixed / none |
| --- | --- | --- | --- | --- |
| EARLY | A_HARD_STOP | 0 / 6 / 0 | 8 / 7 | 0 / 2 / 4 / 0 |
| EARLY | B_CLOSE_CONFIRMATION | 3 / 3 / 0 | 13 / 2 | 4 / 0 / 2 / 0 |
| EARLY | C_NEXT_OPEN | 1 / 5 / 0 | 7 / 8 | 2 / 0 / 4 / 0 |
| EARLY | D_BOUNDED_REVIEW | 1 / 5 / 0 | 7 / 8 | 2 / 0 / 4 / 0 |
| EARLY | E_PRICE_STRUCTURE | 0 / 6 / 0 | 11 / 4 | 2 / 1 / 3 / 0 |
| CLOSE_BOUNDARY | A_HARD_STOP | 0 / 6 / 0 | 8 / 7 | 0 / 2 / 4 / 0 |
| CLOSE_BOUNDARY | B_CLOSE_CONFIRMATION | 3 / 3 / 0 | 13 / 2 | 4 / 0 / 2 / 0 |
| CLOSE_BOUNDARY | C_NEXT_OPEN | 1 / 5 / 0 | 7 / 8 | 2 / 0 / 4 / 0 |
| CLOSE_BOUNDARY | D_BOUNDED_REVIEW | 1 / 5 / 0 | 7 / 8 | 2 / 0 / 4 / 0 |
| CLOSE_BOUNDARY | E_PRICE_STRUCTURE | 0 / 6 / 0 | 11 / 4 | 2 / 1 / 3 / 0 |
| LATE | A_HARD_STOP | 0 / 6 / 0 | 8 / 7 | 0 / 2 / 4 / 0 |
| LATE | B_CLOSE_CONFIRMATION | 3 / 3 / 0 | 13 / 2 | 4 / 0 / 2 / 0 |
| LATE | C_NEXT_OPEN | 1 / 5 / 0 | 7 / 8 | 2 / 0 / 4 / 0 |
| LATE | D_BOUNDED_REVIEW | 1 / 5 / 0 | 7 / 8 | 2 / 0 / 4 / 0 |
| LATE | E_PRICE_STRUCTURE | 0 / 6 / 0 | 11 / 4 | 2 / 1 / 3 / 0 |

## Every historical prediction (LATE timing sensitivity)

S = supports that frozen source-action prediction; C = contradicts it; U = abstained or unresolved. These labels test the **combined entry assumption, price rule and newsletter-reporting bridge**, not verified broker execution. In the A–D columns, CONTINUATION covers continued stop management, UNDERWAY and omission; it excludes explicit DROP. A conditional ABSTAIN→action annotation reflects the publication-time branch sealed before reveal.

### case-01 → alert-2

Information cutoff: **2026-10-19T17:01:00-04:00**. Available source prefix: alert-1. Market end: **2026-10-19**. Expected window ends 2026-10-26T23:59:59.999999-04:00. Actual source publication: **2026-10-19T18:19:00-04:00**; eligibility `ELIGIBLE_RETROSPECTIVE_SEQUENCE`. Sealed prediction `81380adf94759c989e1c0044dfe7d1e9d07cb000a7f8a19817a56c228681f084`; evaluation `a7441d1919f3fbe341d84f345d5968f5567f9155a5118bd98ea867a9aea4ec0b`.

| Episode | Source setup / stop at cutoff | A | B | C | D | E: action; stop direction; point; interval | Next source observation | A/B/C/D/E |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AAPL | ENTERABLE / 339.00 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 339.0000; [339.0, 339.0] | CONTINUED_MANAGEMENT; WIDENING 337.8000 | S/S/S/S/C |
| CLMT | ENTERABLE / 55.25 | DROPPED | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUED_MANAGEMENT; WIDENING; 53.2800; [52.733393, 53.826607] | CONTINUED_MANAGEMENT; WIDENING 53.4000 | C/S/S/S/S |
| TEVA | ENTERABLE / 40.40 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 40.4000; [40.4, 40.4] | NOT_MENTIONED; NO_ADJUSTMENT — | S/S/S/S/S |
| CAT | ENTERABLE / 748.75 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 748.7500; [748.75, 748.75] | NOT_MENTIONED; NO_ADJUSTMENT — | S/S/S/S/S |
| CDE | ENTERABLE / 16.40 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 16.4000; [16.4, 16.4] | CONTINUED_MANAGEMENT; TIGHTENING 16.2400 | S/S/S/S/C |
| T | ENTERABLE / 24.00 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 24.0000; [24.0, 24.0] | UNDERWAY; TIGHTENING 23.8000 | S/S/S/S/C |

### case-02 → alert-3

Information cutoff: **2026-10-20T17:01:00-04:00**. Available source prefix: alert-1, alert-2. Market end: **2026-10-20**. Expected window ends 2026-10-27T23:59:59.999999-04:00. Actual source publication: **2026-10-20T18:25:00-04:00**; eligibility `ELIGIBLE_RETROSPECTIVE_SEQUENCE`. Sealed prediction `7abc3c403ec4ed8870d98d8f00f75396b4bf8f0aba552816195de944e1c85d51`; evaluation `17fff716628815003626997a6507b84c8dfe33a39fc77cf3d6f7cf6d9f3c87ae`.

| Episode | Source setup / stop at cutoff | A | B | C | D | E: action; stop direction; point; interval | Next source observation | A/B/C/D/E |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AAPL | ENTERABLE / 337.80 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 337.8000; [337.8, 337.8] | CONTINUED_MANAGEMENT; WIDENING 336.2500 | S/S/S/S/C |
| CLMT | ENTERABLE / 53.40 | DROPPED | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 53.4000; [53.4, 53.4] | CONTINUED_MANAGEMENT; WIDENING 53.0200 | C/S/S/S/C |
| TEVA | ENTERABLE / 40.40 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 40.4000; [40.4, 40.4] | NOT_MENTIONED; NO_ADJUSTMENT — | S/S/S/S/S |
| CAT | ENTERABLE / 748.75 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 748.7500; [748.75, 748.75] | DROPPED; NO_ADJUSTMENT — | C/C/C/C/C |
| CDE | ENTERABLE / 16.24 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 16.2400; [16.24, 16.24] | NOT_MENTIONED; NO_ADJUSTMENT — | S/S/S/S/S |
| T | UNDERWAY / 23.80 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 23.8000; [23.8, 23.8] | NOT_MENTIONED; NO_ADJUSTMENT — | S/S/S/S/S |

### case-03 → alert-4

Information cutoff: **2026-10-21T17:01:00-04:00**. Available source prefix: alert-1, alert-2, alert-3. Market end: **2026-10-21**. Expected window ends 2026-10-28T23:59:59.999999-04:00. Actual source publication: **2026-10-21T18:50:00-04:00**; eligibility `ELIGIBLE_RETROSPECTIVE_SEQUENCE`. Sealed prediction `80ea38e68a63c99d0b521dc4032f4bda2b11e251eb327ac690d00cd1170f0d6b`; evaluation `ca0c00ab1b724f2a76f56fb6d25385f68247b725f7da12672527d29429116998`.

| Episode | Source setup / stop at cutoff | A | B | C | D | E: action; stop direction; point; interval | Next source observation | A/B/C/D/E |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AAPL | ENTERABLE / 336.25 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 336.2500; [336.25, 336.25] | NOT_MENTIONED; NO_ADJUSTMENT — | S/S/S/S/S |
| CLMT | ENTERABLE / 53.02 | DROPPED | DROPPED | ABSTAIN→CONTINUATION (time branch) | ABSTAIN→CONTINUATION (time branch) | DROPPED; ABSTAIN; —; None | DROPPED; NO_ADJUSTMENT — | S/S/C/C/S |
| TEVA | ENTERABLE / 40.40 | DROPPED | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUED_MANAGEMENT; WIDENING; 39.2200; [38.949821, 39.490179] | CONTINUED_MANAGEMENT; WIDENING 39.3500 | C/S/S/S/S |
| CDE | ENTERABLE / 16.24 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 16.2400; [16.24, 16.24] | NOT_MENTIONED; NO_ADJUSTMENT — | S/S/S/S/S |
| T | UNDERWAY / 23.80 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 23.8000; [23.8, 23.8] | CONTINUED_MANAGEMENT; TIGHTENING 22.2000 | S/S/S/S/C |
| ELF | ENTERABLE / 110.50 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 110.5000; [110.5, 110.5] | NOT_MENTIONED; NO_ADJUSTMENT — | S/S/S/S/S |
| HUM | ENTERABLE / 404.00 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 404.0000; [404.0, 404.0] | NOT_MENTIONED; NO_ADJUSTMENT — | S/S/S/S/S |
| SIG | ENTERABLE / 111.80 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 111.8000; [111.8, 111.8] | NOT_MENTIONED; NO_ADJUSTMENT — | S/S/S/S/S |
| ASST | ENTERABLE / 28.45 | DROPPED | DROPPED | ABSTAIN→CONTINUATION (time branch) | ABSTAIN→CONTINUATION (time branch) | DROPPED; ABSTAIN; —; None | DROPPED; NO_ADJUSTMENT — | S/S/C/C/S |
| OMER | ENTERABLE / 17.20 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 17.2000; [17.2, 17.2] | NOT_MENTIONED; NO_ADJUSTMENT — | S/S/S/S/S |

### case-04 → alert-5

Information cutoff: **2026-10-22T17:01:00-04:00**. Available source prefix: alert-1, alert-2, alert-3, alert-4. Market end: **2026-10-22**. Expected window ends 2026-10-29T23:59:59.999999-04:00. Actual source publication: **2026-10-22T18:27:00-04:00**; eligibility `ELIGIBLE_RETROSPECTIVE_SEQUENCE`. Sealed prediction `ca4820fb01211f23787a27c7c423e0f45a1fd36945aa5a7f5d6e4446e485e8e6`; evaluation `9563be1b843462efc08dc3c4618a357686d56579baeb9de4f729c05250a10bd9`.

| Episode | Source setup / stop at cutoff | A | B | C | D | E: action; stop direction; point; interval | Next source observation | A/B/C/D/E |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AAPL | ENTERABLE / 336.25 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 336.2500; [336.25, 336.25] | UNDERWAY; TIGHTENING 343.5000 | S/S/S/S/C |
| TEVA | ENTERABLE / 39.35 | DROPPED | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 39.3500; [39.35, 39.35] | CONTINUED_MANAGEMENT; WIDENING 39.0500 | C/S/S/S/C |
| CDE | ENTERABLE / 16.24 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | UNDERWAY; NO_ADJUSTMENT; 16.2400; [16.24, 16.24] | UNDERWAY; TIGHTENING 14.3000 | S/S/S/S/S |
| T | UNDERWAY / 22.20 | DROPPED | DROPPED | ABSTAIN→CONTINUATION (time branch) | ABSTAIN→CONTINUATION (time branch) | DROPPED; ABSTAIN; —; None | DROPPED; NO_ADJUSTMENT — | S/S/C/C/S |
| ELF | ENTERABLE / 110.50 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 110.5000; [110.5, 110.5] | CONTINUED_MANAGEMENT; WIDENING 108.6000 | S/S/S/S/C |
| HUM | ENTERABLE / 404.00 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 404.0000; [404.0, 404.0] | CONTINUED_MANAGEMENT; TIGHTENING 408.1000 | S/S/S/S/C |
| SIG | ENTERABLE / 111.80 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 111.8000; [111.8, 111.8] | NOT_MENTIONED; NO_ADJUSTMENT — | S/S/S/S/S |
| OMER | ENTERABLE / 17.20 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 17.2000; [17.2, 17.2] | CONTINUED_MANAGEMENT; WIDENING 17.3500 | S/S/S/S/C |
| GME | ENTERABLE / 25.01 | DROPPED | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUED_MANAGEMENT; WIDENING; 24.2900; [23.978929, 24.601071] | CONTINUED_MANAGEMENT; WIDENING 24.7800 | C/S/S/S/S |
| AAOI | ENTERABLE / 89.82 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 89.8200; [89.82, 89.82] | UNDERWAY; TIGHTENING 70.7000 | S/S/S/S/C |
| AMD | ENTERABLE / 569.90 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | UNDERWAY; NO_ADJUSTMENT; 569.9000; [569.9, 569.9] | UNDERWAY; TIGHTENING 519.3500 | S/S/S/S/S |
| ANET | ENTERABLE / 191.25 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | UNDERWAY; NO_ADJUSTMENT; 191.2500; [191.25, 191.25] | UNDERWAY; TIGHTENING 176.8000 | S/S/S/S/S |
| SNDK | ENTERABLE / 1458.00 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | UNDERWAY; NO_ADJUSTMENT; 1458.0000; [1458.0, 1458.0] | UNDERWAY; TIGHTENING 1296.0000 | S/S/S/S/S |

### case-05 → alert-6

Information cutoff: **2026-10-22T18:28:00-04:00**. Available source prefix: alert-1, alert-2, alert-3, alert-4, alert-5. Market end: **2026-10-22**. Expected window ends 2026-10-29T23:59:59.999999-04:00. Actual source publication: **UNKNOWN**; eligibility `ELIGIBLE_RETROSPECTIVE_SEQUENCE`. Sealed prediction `296b0d288accac6547b8a2a150b3efa51c873da8b5063720a58e6b7fdc92c4ba`; evaluation `ad5d6eacd2e483427d15c2de41d9805575b7b715758a954e3e5d54e8d3ca2b63`.

| Episode | Source setup / stop at cutoff | A | B | C | D | E: action; stop direction; point; interval | Next source observation | A/B/C/D/E |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AAPL | UNDERWAY / 343.50 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 343.5000; [343.5, 343.5] | CONTINUED_MANAGEMENT; TIGHTENING 344.7000 | S/S/S/S/C |
| TEVA | ENTERABLE / 39.05 | DROPPED | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 39.0500; [39.05, 39.05] | DROPPED; NO_ADJUSTMENT — | S/C/C/C/C |
| CDE | UNDERWAY / 14.30 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 14.3000; [14.3, 14.3] | CONTINUED_MANAGEMENT; TIGHTENING 13.9000 | S/S/S/S/C |
| ELF | ENTERABLE / 108.60 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 108.6000; [108.6, 108.6] | CONTINUED_MANAGEMENT; TIGHTENING 109.2000 | S/S/S/S/C |
| HUM | ENTERABLE / 408.10 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 408.1000; [408.1, 408.1] | NOT_MENTIONED; NO_ADJUSTMENT — | S/S/S/S/S |
| SIG | ENTERABLE / 111.80 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 111.8000; [111.8, 111.8] | CONTINUED_MANAGEMENT; TIGHTENING 112.5000 | S/S/S/S/C |
| OMER | ENTERABLE / 17.35 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 17.3500; [17.35, 17.35] | NOT_MENTIONED; NO_ADJUSTMENT — | S/S/S/S/S |
| GME | ENTERABLE / 24.78 | DROPPED | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUED_MANAGEMENT; WIDENING; 24.2900; [23.978929, 24.601071] | CONTINUED_MANAGEMENT; WIDENING 24.4000 | C/S/S/S/S |
| AAOI | UNDERWAY / 70.70 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 70.7000; [70.7, 70.7] | DROPPED; NO_ADJUSTMENT — | C/C/C/C/C |
| AMD | UNDERWAY / 519.35 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 519.3500; [519.35, 519.35] | DROPPED; NO_ADJUSTMENT — | C/C/C/C/C |
| ANET | UNDERWAY / 176.80 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 176.8000; [176.8, 176.8] | CONTINUED_MANAGEMENT; TIGHTENING 175.2000 | S/S/S/S/C |
| SNDK | UNDERWAY / 1296.00 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 1296.0000; [1296.0, 1296.0] | DROPPED; NO_ADJUSTMENT — | C/C/C/C/C |

### case-06 → alert-7

Information cutoff: **2026-10-26T17:01:00-04:00**. Available source prefix: alert-1, alert-2, alert-3, alert-4, alert-5, alert-6. Market end: **2026-10-26**. Expected window ends 2026-11-02T23:59:59.999999-05:00. Actual source publication: **2026-10-26T18:10:00-04:00**; eligibility `ELIGIBLE_RETROSPECTIVE_SEQUENCE`. Sealed prediction `16b7c13d5cbb0c73bb53619b30d472f4f9a19b54b6588898a805d76dfdf767f8`; evaluation `6e5bb77af0944491d5c58568afacdf061c0a881b0130fa9be009a60391458d58`.

| Episode | Source setup / stop at cutoff | A | B | C | D | E: action; stop direction; point; interval | Next source observation | A/B/C/D/E |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AAPL | UNDERWAY / 344.70 | DROPPED | DROPPED | ABSTAIN→CONTINUATION (time branch) | ABSTAIN→CONTINUATION (time branch) | DROPPED; ABSTAIN; —; None | DROPPED; NO_ADJUSTMENT — | S/S/C/C/S |
| CDE | UNDERWAY / 13.90 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 13.9000; [13.9, 13.9] | NOT_MENTIONED; NO_ADJUSTMENT — | S/S/S/S/S |
| ELF | ENTERABLE / 109.20 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 109.2000; [109.2, 109.2] | NOT_MENTIONED; NO_ADJUSTMENT — | S/S/S/S/S |
| HUM | ENTERABLE / 408.10 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 408.1000; [408.1, 408.1] | NOT_MENTIONED; NO_ADJUSTMENT — | S/S/S/S/S |
| SIG | ENTERABLE / 112.50 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 112.5000; [112.5, 112.5] | NOT_MENTIONED; NO_ADJUSTMENT — | S/S/S/S/S |
| OMER | ENTERABLE / 17.35 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 17.3500; [17.35, 17.35] | NOT_MENTIONED; NO_ADJUSTMENT — | S/S/S/S/S |
| GME | ENTERABLE / 24.40 | DROPPED | DROPPED | ABSTAIN→CONTINUATION (time branch) | ABSTAIN→CONTINUATION (time branch) | DROPPED; ABSTAIN; —; None | DROPPED; NO_ADJUSTMENT — | S/S/C/C/S |
| ANET | UNDERWAY / 175.20 | DROPPED | DROPPED | ABSTAIN→CONTINUATION (time branch) | ABSTAIN→CONTINUATION (time branch) | DROPPED; ABSTAIN; —; None | DROPPED; NO_ADJUSTMENT — | S/S/C/C/S |
| ABBV | ENTERABLE / 276.30 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 276.3000; [276.3, 276.3] | NOT_MENTIONED; NO_ADJUSTMENT — | S/S/S/S/S |
| CNQ | ENTERABLE / 53.30 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 53.3000; [53.3, 53.3] | NOT_MENTIONED; NO_ADJUSTMENT — | S/S/S/S/S |
| EBAY | ENTERABLE / 119.20 | DROPPED | DROPPED | ABSTAIN→CONTINUATION (time branch) | ABSTAIN→CONTINUATION (time branch) | DROPPED; ABSTAIN; —; None | CONTINUED_MANAGEMENT; WIDENING 117.5000 | C/C/S/S/C |
| GTLB | ENTERABLE / 51.60 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 51.6000; [51.6, 51.6] | CONTINUED_MANAGEMENT; TIGHTENING 52.1000 | S/S/S/S/C |
| MMM | ENTERABLE / 169.90 | CONTINUATION | CONTINUATION | CONTINUATION | CONTINUATION | NOT_MENTIONED; NO_ADJUSTMENT; 169.9000; [169.9, 169.9] | NOT_MENTIONED; NO_ADJUSTMENT — | S/S/S/S/S |
| SNOW | ENTERABLE / 330.70 | DROPPED | DROPPED | ABSTAIN→CONTINUATION (time branch) | ABSTAIN→CONTINUATION (time branch) | DROPPED; ABSTAIN; —; None | DROPPED; NO_ADJUSTMENT — | S/S/C/C/S |

## Interpretation and falsification

Under LATE timing, B covers 55/61 source-action outcomes, but 3 shared alerts still contain counterexamples. This supports some conditional closing-confirmation explanations while rejecting a claim that this fixed model reproduces the whole source process.

E correctly predicts only 4/26 offered directions on actual revisions; its numerical intervals cover 3/26 offered levels. The simple structure rule therefore fails to reproduce most numeric stop-management decisions, despite some correct action calls. A correct CDE UNDERWAY call does not repair its stop forecast.

C and D produce identical resolved source-action forecasts on these historical observations. They remain indistinguishable here; their future next-Open obligations still differ. Equal scores do not identify the actual stop convention.

CLMT, TEVA and GME are diagnostic repetitions of known intraday-touch/recovery cases. The pre-alert forecasts can distinguish A’s DROP expectation from recovered-close continuation under B–D, but this is not new independent evidence because those cases motivated the rules. EBAY’s already-known adverse Close remains the important counterexample: A/B expect DROP under the assumed active exposure, while pending C/D can still permit a same-evening revision before the next Open. Calling that earlier revision a failed committed exit would be a chronology error.

CDE is a target-management control. The models impose no mandatory full +1R exit; this historical replay cannot retest a target policy they do not contain. E uses directional movement from a pre-alert reference Close divided by its then-known ATR, not an inferred entry or actual initial risk. Its UNDERWAY result and any stop-level misses are evaluated separately.

Model E is deliberately small and falsifiable: a confirmed pivot can be too remote to reproduce a rapid stop ratchet. A correct UNDERWAY call does not excuse a wrong stop direction/level, and a broad continuation set is not exact prediction of a particular stop revision. We do not revise thresholds after seeing these dry-run scores.

For future discrimination, retain the next Open and the stop known before that Open. A protective Open after an evening revision, followed by continued source management, distinguishes C’s irrevocable commitment from D’s one permitted review. An intraday recovery with continued management separates A from B conditional on the entry/reporting bridge. If every model predicts continuation, that alert supplies no discriminating test.

See [method and CLI](../GRIMES_PROSPECTIVE_PREDICTION_METHOD.md), [sealed next-alert forecast](GRIMES_NEXT_ALERT_PREDICTIONS.md), and [machine-readable evaluations](../evidence/pr9c-walk-forward-v1/walk-forward.json).
