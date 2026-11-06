# PR9F source-event and opening-episode reconciliation

The supplied **Last 14 days · 118 changes** log contains exactly 118 visible rows. All are retained and linked to captured source episodes. This is reconciliation of the supplied observations, not certification of complete MarketLife history or private brokerage activity.

The [dated literal text](../evidence/pr9f-expanded-source-20261103-v1/change-log-20261102.txt), [provenance](../evidence/pr9f-expanded-source-20261103-v1/provenance.json), [parsed source rows](../evidence/pr9f-initial-patterns-v2/source-events.csv) and [machine reconciliation](../evidence/pr9f-initial-patterns-v2/reconciliation.json) provide the audit trail. The earlier November 3 operator summary and every PR9E source remain unchanged.

## Population accounting

| Quantity | Count |
| --- | ---: |
| Original PR9E initial episodes | 34 |
| NEW SETUP rows in the new log | 36 |
| Corroborating original openings | 28 |
| Newly captured opening episodes | 8 |
| Final initial-stop population | 42 |
| LONG / SHORT | 22 / 20 |
| Distinct symbols | 40 |
| Unmatched log events | 0 |

The six October 18 openings precede the visible log. They remain included from prior evidence. The 28 overlaps require a unique symbol/direction/initial-stop match **and compatible source date bounds**, together with episode chronology. Repeated reports are aliases, not additional samples. A tracked termination permits a new same-symbol episode; matching a stop price alone does not deduplicate separate episodes.

| Opening log date | Episode | Direction | Initial stop | Source TYPE |
| --- | --- | --- | ---: | --- |
| October 30 | AXGN-001 | LONG | 47.30 | Pullback |
| October 30 | BA-001 | SHORT | 177.30 | Tight pullback |
| October 30 | KSS-001 | LONG | 22.80 | Pullback |
| October 30 | NCLH-001 | LONG | 17.01 | Tight pullback |
| October 30 | XOP-001 | LONG | 194.90 | Pullback |
| November 2 | AVGO-001 | SHORT | 335.40 | Nested pullback |
| November 2 | GME-002 | SHORT | 24.90 | Nested pullback |
| November 2 | SLB-002 | LONG | 51.90 | Pullback |

## Dates retain their source roles

The user reports publication at **5 p.m. November 2, 2026**. That latest-batch/snapshot assertion is recorded at hour precision in America/New_York, with the session-timezone assumption disclosed. It does not assign 5 p.m. to all prior historical rows. Original per-alert bounds for PR9E's 34 episodes remain unchanged.

The earlier summary described the three latest setups under November 3 commentary/intended Tuesday trading. The log labels their NEW SETUP rows Monday, November 2. Three explicit aliases join AVGO, new GME and new SLB across these sources, retaining both dates. Neither source is rewritten. The earlier draft's 37-episode result remains a preserved provisional snapshot rather than the current population.

For new October 30 openings, EARLY/CLOSE_BOUNDARY/LATE are conditional information views based on the log date; original intraday publication is unknown. For the November 2 latest batch, the supplied 5 p.m. hour bounds are used. The inherited strict Close-plus-60-minute rule means that 17:00 exactly and a later time within the hour can admit different last sessions. This is a sensitivity analysis, not an assertion that the historical publication occurred at a manufactured instant.

## Important chains and exclusions

| Episode | Opening evidence | Later source facts retained | Initial-stop consequence |
| --- | --- | --- | --- |
| SLB-001 | Oct 26 NEW LONG, 51.10 | Oct 27 TRIGGERED with 52.60; Nov 2 STOPPED OUT | Initial remains 51.10 |
| SLB-002 | Nov 2 NEW LONG Pullback, 51.90 | Earlier termination distinguishes the new episode | Initial is 51.90; no subtraction from 52.60 used to explain it |
| CNQ-001 | Oct 23 log NEW LONG, 53.30; older weekly publication uncertain | Oct 30 TRIGGERED with 55.10; Nov 2 STOPPED OUT | Initial remains 53.30 |
| DUK-001 | Oct 28 NEW LONG, 122.90 | Oct 29 TRIGGERED 124.70; later STOP MOVED facts | Initial remains 122.90 |
| CRWV-001 | Oct 29 NEW SHORT, 66.20 | Oct 30 TRIGGERED 58.80; Nov 2 STOP MOVED to 55.00 | Initial remains 66.20 |
| GME-001 / GME-002 | Oct 21 LONG 25.01; Nov 2 SHORT 24.90 | Earlier LONG removal and later SHORT opening are distinct observations | Two episodes, not a revision or automatic direction reversal |

There are 15 TRIGGERED rows, 33 STOP MOVED rows, five STOPPED OUT rows and 29 DROPPED/TAKEN OFF rows. They preserve factual source chronology and episode identity but do not enter the initial-stop hypothesis sample. TRIGGERED is not silently equated with UNDERWAY. Where an older alert co-publishes a stop/state change and the log uses TRIGGERED, both wordings remain attributed source evidence. Earlier captured eligibility facts omitted from this log, such as SAIL's return to ENTERABLE, are not erased.

The row-to-episode reconciliation is not an execution simulator, an investigation of management rationale, or proof of a subscriber fill. It does not infer missing opening prices from previous-stop fields, infer stop-out prices from OHLC, or create episodes from triggers. All source-tracked outcomes remain separate from private execution, which is UNKNOWN.

## Setup-family evidence and limits

Eight NEW SETUP rows contain an explicit TYPE: four Pullback, two Tight pullback and two Nested pullback. The original 34 have no episode-specific dashboard TYPE supplied in the retained openings. The log associates the labels with its opening records, while the original per-alert publisher payload and intraday label timing remain unverified. Later dashboard TYPE is not backfilled. The word Breakout is part of the reported vocabulary but is not an observed TYPE for any captured episode here.

All eight newly labelled episodes lack complete eligible market evidence in the existing archive. Their source classifications remain facts attributed to the user-provided log; they do not license invented price structures. The [scientific report](GRIMES_INITIAL_STOP_INFERENCE.md) retains these cases as UNKNOWN and distinguishes publisher labels from proposed price-pattern explanations.
