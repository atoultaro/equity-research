# IBKR daily historical-depth audit

Origin: **ibkr_client**. Frozen as-of: 2026-10-26T22:26:18.495574+00:00. Data: completed daily TRADES, RTH.

Coverage describes this endpoint/contract/retrieval, not survivorship-free or point-in-time research readiness.

| Symbol / conId | Kind | Requested start | Observed first | Observed last | Sessions | Unexpected missing | Status |
| --- | --- | --- | --- | --- | ---: | ---: | --- |
| AAPL / 265598 | stock | 1980-01-01 | 1980-12-12 | 2026-10-26 | 11559 | 3 | partial |
| MSFT / 272093 | stock | 1980-01-01 | 1986-03-13 | 2026-10-26 | 10235 | 0 | partial |
| GOOG / 208813720 | stock | 1980-01-01 | 2014-03-27 | 2026-10-26 | 3165 | 0 | partial |
| NVDA / 4815747 | stock | 1980-01-01 | 1999-01-22 | 2026-10-26 | 6984 | 0 | partial |
| AMZN / 3691937 | stock | 1980-01-01 | 1997-05-15 | 2026-10-26 | 7409 | 0 | partial |
| META / 107113386 | stock | 1980-01-01 | 2012-05-18 | 2026-10-26 | 3630 | 0 | exhausted |
| SPY / 756733 | market_etf | 1980-01-01 | 1993-01-29 | 2026-10-26 | 8491 | 2 | partial |
| QQQ / 320227571 | market_etf | 1980-01-01 | 1999-03-10 | 2026-10-26 | 6951 | 0 | exhausted |
| IWM / 9579970 | market_etf | 1980-01-01 | 2000-05-26 | 2026-10-26 | 6642 | 1 | partial |
| RSP / 319359375 | market_etf | 1980-01-01 | 2003-04-30 | 2026-10-26 | 5909 | 2 | partial |
| XLK / 4215230 | sector_etf | 1980-01-01 | 1998-12-22 | 2026-10-26 | 7001 | 2 | partial |
| XLF / 4215220 | sector_etf | 1980-01-01 | 1998-12-22 | 2026-10-26 | 7001 | 2 | partial |
| XLE / 4215217 | sector_etf | 1980-01-01 | 1998-12-22 | 2026-10-26 | 7001 | 2 | partial |
| XLI / 4215227 | sector_etf | 1980-01-01 | 1998-12-22 | 2026-10-26 | 7000 | 3 | partial |
| XLV / 4215205 | sector_etf | 1980-01-01 | 1998-12-22 | 2026-10-26 | 7001 | 2 | partial |
| SMH / 229725622 | industry_etf | 1980-01-01 | 2011-12-21 | 2026-10-26 | 3732 | 0 | exhausted |
| XBI / 45540828 | industry_etf | 1980-01-01 | 2006-02-06 | 2026-10-26 | 5212 | 1 | partial |

Leading unobserved sessions are reported separately; they are not automatically internal gaps or pre-IPO history.
Exhausted requires a provider head timestamp matched by an observed boundary with complete coverage above it.
An empty response or a failed request alone never proves historical exhaustion.
TRADES retains IBKR's documented split-adjusted convention, not verified raw execution prices; volume units remain unverified.
No forward filling, action inference, trade reconstruction or account query is performed.

## AAPL

Stop: OBSERVED_SEARCH_BOUNDARY; provider head: 1980-12-12T14:30:00+00:00; leading unobserved: 240; conflicting sessions: 0.

- LEADING_COVERAGE_UNOBSERVED; listing history or provider boundary may limit depth
- UNEXPECTED_MISSING_SESSIONS; not holidays and not forward filled
- QUALITY_OR_IDENTITY_FAILURE; no automatic repair or revision choice

## MSFT

Stop: OBSERVED_SEARCH_BOUNDARY; provider head: 1986-03-13T14:30:00+00:00; leading unobserved: 1566; conflicting sessions: 0.

- LEADING_COVERAGE_UNOBSERVED; listing history or provider boundary may limit depth
- QUALITY_OR_IDENTITY_FAILURE; no automatic repair or revision choice

## GOOG

Stop: EMPTY_LIMIT_OR_UNCONFIRMED_BOUNDARY; provider head: 2014-01-13T09:00:00+00:00; leading unobserved: 8635; conflicting sessions: 0.

- LEADING_COVERAGE_UNOBSERVED; listing history or provider boundary may limit depth
- EMPTY_OR_NO_DATA_IS_NOT_EXHAUSTION
- REQUEST_FAILURES_RETAINED; inspect request diagnostics

## NVDA

Stop: OBSERVED_SEARCH_BOUNDARY; provider head: 1999-01-22T14:30:00+00:00; leading unobserved: 4817; conflicting sessions: 0.

- LEADING_COVERAGE_UNOBSERVED; listing history or provider boundary may limit depth
- QUALITY_OR_IDENTITY_FAILURE; no automatic repair or revision choice

## AMZN

Stop: OBSERVED_SEARCH_BOUNDARY; provider head: 1997-05-15T13:30:00+00:00; leading unobserved: 4392; conflicting sessions: 0.

- LEADING_COVERAGE_UNOBSERVED; listing history or provider boundary may limit depth
- QUALITY_OR_IDENTITY_FAILURE; no automatic repair or revision choice

## META

Stop: OBSERVED_SEARCH_BOUNDARY; provider head: 2012-05-18T08:00:00+00:00; leading unobserved: 8170; conflicting sessions: 0.

- LEADING_COVERAGE_UNOBSERVED; listing history or provider boundary may limit depth

## SPY

Stop: OBSERVED_SEARCH_BOUNDARY; provider head: 1993-01-29T14:30:00+00:00; leading unobserved: 3307; conflicting sessions: 0.

- LEADING_COVERAGE_UNOBSERVED; listing history or provider boundary may limit depth
- UNEXPECTED_MISSING_SESSIONS; not holidays and not forward filled

## QQQ

Stop: OBSERVED_SEARCH_BOUNDARY; provider head: 1999-03-10T14:30:00+00:00; leading unobserved: 4849; conflicting sessions: 0.

- LEADING_COVERAGE_UNOBSERVED; listing history or provider boundary may limit depth

## IWM

Stop: OBSERVED_SEARCH_BOUNDARY; provider head: 2000-05-26T08:00:00+00:00; leading unobserved: 5157; conflicting sessions: 0.

- LEADING_COVERAGE_UNOBSERVED; listing history or provider boundary may limit depth
- UNEXPECTED_MISSING_SESSIONS; not holidays and not forward filled

## RSP

Stop: OBSERVED_SEARCH_BOUNDARY; provider head: 2003-04-30T08:00:00+00:00; leading unobserved: 5889; conflicting sessions: 0.

- LEADING_COVERAGE_UNOBSERVED; listing history or provider boundary may limit depth
- UNEXPECTED_MISSING_SESSIONS; not holidays and not forward filled

## XLK

Stop: OBSERVED_SEARCH_BOUNDARY; provider head: 1998-12-22T09:00:00+00:00; leading unobserved: 4797; conflicting sessions: 0.

- LEADING_COVERAGE_UNOBSERVED; listing history or provider boundary may limit depth
- UNEXPECTED_MISSING_SESSIONS; not holidays and not forward filled

## XLF

Stop: OBSERVED_SEARCH_BOUNDARY; provider head: 1998-12-22T09:00:00+00:00; leading unobserved: 4797; conflicting sessions: 0.

- LEADING_COVERAGE_UNOBSERVED; listing history or provider boundary may limit depth
- UNEXPECTED_MISSING_SESSIONS; not holidays and not forward filled

## XLE

Stop: OBSERVED_SEARCH_BOUNDARY; provider head: 1998-12-22T09:00:00+00:00; leading unobserved: 4797; conflicting sessions: 0.

- LEADING_COVERAGE_UNOBSERVED; listing history or provider boundary may limit depth
- UNEXPECTED_MISSING_SESSIONS; not holidays and not forward filled

## XLI

Stop: OBSERVED_SEARCH_BOUNDARY; provider head: 1998-12-22T09:00:00+00:00; leading unobserved: 4797; conflicting sessions: 0.

- LEADING_COVERAGE_UNOBSERVED; listing history or provider boundary may limit depth
- UNEXPECTED_MISSING_SESSIONS; not holidays and not forward filled

## XLV

Stop: OBSERVED_SEARCH_BOUNDARY; provider head: 1998-12-22T09:00:00+00:00; leading unobserved: 4797; conflicting sessions: 0.

- LEADING_COVERAGE_UNOBSERVED; listing history or provider boundary may limit depth
- UNEXPECTED_MISSING_SESSIONS; not holidays and not forward filled

## SMH

Stop: OBSERVED_SEARCH_BOUNDARY; provider head: 2011-12-21T09:00:00+00:00; leading unobserved: 8068; conflicting sessions: 0.

- LEADING_COVERAGE_UNOBSERVED; listing history or provider boundary may limit depth

## XBI

Stop: OBSERVED_SEARCH_BOUNDARY; provider head: 2006-02-06T09:00:00+00:00; leading unobserved: 6587; conflicting sessions: 0.

- LEADING_COVERAGE_UNOBSERVED; listing history or provider boundary may limit depth
- UNEXPECTED_MISSING_SESSIONS; not holidays and not forward filled
