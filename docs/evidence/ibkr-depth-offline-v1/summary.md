# IBKR daily historical-depth audit

Origin: **synthetic**. Frozen as-of: 2024-11-30T00:00:00+00:00. Data: completed daily TRADES, RTH.

Coverage describes this endpoint/contract/retrieval, not survivorship-free or point-in-time research readiness.

| Symbol / conId | Kind | Requested start | Observed first | Observed last | Sessions | Unexpected missing | Status |
| --- | --- | --- | --- | --- | ---: | ---: | --- |
| COMPLETE / 101 | stock | 2024-11-25 | 2024-11-25 | 2024-11-29 | 4 | 0 | complete |
| GAPPED / 102 | stock | 2024-11-25 | 2024-11-25 | 2024-11-29 | 3 | 1 | partial |

Leading unobserved sessions are reported separately; they are not automatically internal gaps or pre-IPO history.
Exhausted requires a provider head timestamp matched by an observed boundary with complete coverage above it.
An empty response or a failed request alone never proves historical exhaustion.
TRADES retains IBKR's documented split-adjusted convention, not verified raw execution prices; volume units remain unverified.
No forward filling, action inference, trade reconstruction or account query is performed.

## COMPLETE

Stop: OBSERVED_SEARCH_BOUNDARY; provider head: 2024-11-25T14:30:00+00:00; leading unobserved: 0; conflicting sessions: 0.

- No detected coverage/quality warning in this bounded audit.

## GAPPED

Stop: OBSERVED_SEARCH_BOUNDARY; provider head: 2024-11-25T14:30:00+00:00; leading unobserved: 0; conflicting sessions: 0.

- UNEXPECTED_MISSING_SESSIONS; not holidays and not forward filled
