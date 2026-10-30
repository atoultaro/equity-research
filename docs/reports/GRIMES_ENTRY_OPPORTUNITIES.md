# Grimes setup and entry-opportunity reassessment

MarketLife reports setup selection and fresh-entry eligibility. ADDED, stop revisions, UNDERWAY and DROPPED do not establish personal positions or executions. This interpretation supersedes execution inferences in the preserved PR16–PR20 and original PR9C reports; their frozen results remain historical conditional experiments.

Native semantic study SHA256: `fbeed403c844c47ff11824d8c9977e7be7d43689a04c10e0addf267cfe77bce7`. Public evidence SHA256: `1138634f02be7b1921e7cc395d3fef0a4d7eb596a672e702e5cb53bbd5c2627e`. [Derived evidence and input registry](../evidence/pr9c-setup-opportunities-v1/manifest.json); [validation](../evidence/pr9c-setup-validation-v1/validation.json).

Ten operator-supplied alerts through October 29 produce 34 captured setup episodes (26 original plus eight newly reported additions), 72 version records, and 58 nonempty eligible windows. The other 14 versions coincide with UNDERWAY and have no entry window. These counts do not multiply across the three publication scenarios. No newly added symbol has acquired prices in this amendment.

The original weekly publication remains UNKNOWN. October 27–29 have operator-supplied dates, no exact publication times. EARLY uses the date’s start, CLOSE_BOUNDARY uses its cash Close, and LATE uses the date’s end capped by capture time. These are conditional timing bounds in America/New_York, not discovered timestamps. The weekly scenarios retain the prior metadata bracket. Completed daily evidence requires Close + 60 minutes strictly before the decision cutoff.

## Source state after the October 29 supplied alert

| Symbol | Direction | Setup | Fresh entry | Published stop |
| --- | --- | --- | --- | --- |
| SIG | LONG | ACTIVE | UNDERWAY | 116.60 |
| CNQ | LONG | ACTIVE | ENTERABLE | 53.30 |
| MMM | LONG | ACTIVE | UNDERWAY | 173.80 |
| SAIL | LONG | ACTIVE | ENTERABLE | 20.70 |
| SLB | LONG | ACTIVE | UNDERWAY | 52.60 |
| DUK | LONG | ACTIVE | UNDERWAY | 124.70 |
| PAA | LONG | ACTIVE | UNDERWAY | 26.66 |
| FCX | SHORT | ACTIVE | ENTERABLE | 67.50 |
| CRWV | SHORT | ACTIVE | ENTERABLE | 66.20 |
| NBIS | SHORT | ACTIVE | ENTERABLE | 185.80 |

SAIL’s October 27 stop/UNDERWAY assessment blocks fresh entry. Its October 28 stop is monitored only. On October 29 the stop becomes 20.70 while still UNDERWAY; the explicitly reported return to ENTERABLE then creates version 3 at 20.70. None of these actions supplies a subscriber fill. The original 26-row trade-status CSV remains an unchanged October 26 historical view, not the current setup book.

## Causal references and hypothetical behavior

Each nonempty opportunity records the available Close, completed shared ATR14, signed stop distance, SMA10/20/50, confirmed swings, prior-20 extremes, volatility/compression and relative SPY strength where supported. An available Close is a technical reference, never a fill retroactively assigned to an already-past Close. A candidate Open must occur strictly after the assumed publication and before supersession/suspension/removal. Unobserved, nonprotective and missing-session candidates remain unavailable.

A is the preserved continuous next-Open hard-stop reference with causal reported stop updates and no re-entry. B and C are independent candidate executions for each eligible version, using that version’s fixed stop: B checks Open gaps and daily extremes; C checks closing confirmation. Source supersession, UNDERWAY and DROPPED end future-entry eligibility, not a subscriber holding. These alternatives do not reconstruct a sequential re-entry portfolio. No stop revision changes an earlier candidate retroactively. Closing confirmation is an exploratory convention, not evidence of MarketLife’s or Grimes’ actual order policy. No quantities, actual initial R, costs, fills or P&L are inferred.

## Four prior apparent contradictions

| Case | A: first hard-stop condition | New opportunities and remaining uncertainty |
| --- | --- | --- |
| CLMT | October 19 | 53.40 → October 20 Open; 53.02 → October 21 Open. Both later hard-stop candidates touch on October 21. Continuing ENTERABLE after the first stop is coherent; no actual re-entry is observed. |
| TEVA | October 21 Open gap | 39.35 → October 22 Open, hard condition October 23. 39.05 → October 23 Open only if the unknown weekly DROP had not yet ended eligibility; this fixed-stop candidate remains protected through October 26. |
| GME | October 22 | 24.78 and weekly 24.40 create distinct windows. An EARLY weekly update supersedes 24.78 before Friday Open; other clocks permit it. The 24.40 candidate touches October 26. No executed sequence is identified. |
| EBAY | October 26 | The old 119.20 candidate crosses on October 26. After-hours 117.50 creates a fresh opportunity; available Close 118.62 is a reference, not a fill. October 27 prices are missing, and its date-only DROP can precede the next Open. Fresh execution is unverified. |

The corrected semantics remove the apparent source/execution contradiction in all four cases. They do not rescue a continuously held hard-stop execution after its first breach or prove which subscriber traded. New opportunities make later source revisions coherent without requiring deferred review, stop cancellation, price rescaling or inferred actual re-entry. CDE’s UNDERWAY label likewise cannot establish a held runner or disprove a subscriber’s full +1R exit. Original numerical forensic results and Model E failures remain preserved, not retuned.

## Candidate and path comparison by conditional publication schedule

| Clock | Symbol | Version | Stop | Candidate session | Open reference | Feasibility | B: hard | C: Close |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EARLY | CLMT | 1 | 55.25 | 2026-10-19 | 57.470 | CAUSALLY_FEASIBLE_REFERENCE | stop condition 2026-10-19 | stop condition 2026-10-21 |
| EARLY | CLMT | 2 | 53.40 | 2026-10-20 | 56.200 | CAUSALLY_FEASIBLE_REFERENCE | stop condition 2026-10-21 | stop condition 2026-10-21 |
| EARLY | CLMT | 3 | 53.02 | 2026-10-21 | 56.400 | CAUSALLY_FEASIBLE_REFERENCE | stop condition 2026-10-21 | stop condition 2026-10-21 |
| EARLY | TEVA | 1 | 40.40 | 2026-10-19 | 41.420 | CAUSALLY_FEASIBLE_REFERENCE | stop condition 2026-10-21 | stop condition 2026-10-22 |
| EARLY | TEVA | 2 | 39.35 | 2026-10-22 | 40.200 | CAUSALLY_FEASIBLE_REFERENCE | stop condition 2026-10-23 | protected through data end |
| EARLY | TEVA | 3 | 39.05 | 2026-10-23 | UNAVAILABLE | SUPERSEDED_OR_SUSPENDED_BEFORE_CANDIDATE_OPEN | NO_COMPARABLE_REFERENCE | NO_COMPARABLE_REFERENCE |
| EARLY | GME | 1 | 25.01 | 2026-10-22 | 26.000 | CAUSALLY_FEASIBLE_REFERENCE | stop condition 2026-10-22 | stop condition 2026-10-23 |
| EARLY | GME | 2 | 24.78 | 2026-10-23 | UNAVAILABLE | SUPERSEDED_OR_SUSPENDED_BEFORE_CANDIDATE_OPEN | NO_COMPARABLE_REFERENCE | NO_COMPARABLE_REFERENCE |
| EARLY | GME | 3 | 24.40 | 2026-10-23 | 25.340 | CAUSALLY_FEASIBLE_REFERENCE | stop condition 2026-10-26 | stop condition 2026-10-26 |
| EARLY | EBAY | 1 | 119.20 | 2026-10-23 | 120.840 | CAUSALLY_FEASIBLE_REFERENCE | stop condition 2026-10-26 | stop condition 2026-10-26 |
| EARLY | EBAY | 2 | 117.50 | 2026-10-27 | UNAVAILABLE | SUPERSEDED_OR_SUSPENDED_BEFORE_CANDIDATE_OPEN | NO_COMPARABLE_REFERENCE | NO_COMPARABLE_REFERENCE |
| CLOSE_BOUNDARY | CLMT | 1 | 55.25 | 2026-10-19 | 57.470 | CAUSALLY_FEASIBLE_REFERENCE | stop condition 2026-10-19 | stop condition 2026-10-21 |
| CLOSE_BOUNDARY | CLMT | 2 | 53.40 | 2026-10-20 | 56.200 | CAUSALLY_FEASIBLE_REFERENCE | stop condition 2026-10-21 | stop condition 2026-10-21 |
| CLOSE_BOUNDARY | CLMT | 3 | 53.02 | 2026-10-21 | 56.400 | CAUSALLY_FEASIBLE_REFERENCE | stop condition 2026-10-21 | stop condition 2026-10-21 |
| CLOSE_BOUNDARY | TEVA | 1 | 40.40 | 2026-10-19 | 41.420 | CAUSALLY_FEASIBLE_REFERENCE | stop condition 2026-10-21 | stop condition 2026-10-22 |
| CLOSE_BOUNDARY | TEVA | 2 | 39.35 | 2026-10-22 | 40.200 | CAUSALLY_FEASIBLE_REFERENCE | stop condition 2026-10-23 | protected through data end |
| CLOSE_BOUNDARY | TEVA | 3 | 39.05 | 2026-10-23 | 39.750 | CAUSALLY_FEASIBLE_REFERENCE | protected through data end | protected through data end |
| CLOSE_BOUNDARY | GME | 1 | 25.01 | 2026-10-22 | 26.000 | CAUSALLY_FEASIBLE_REFERENCE | stop condition 2026-10-22 | stop condition 2026-10-23 |
| CLOSE_BOUNDARY | GME | 2 | 24.78 | 2026-10-23 | 25.340 | CAUSALLY_FEASIBLE_REFERENCE | stop condition 2026-10-23 | stop condition 2026-10-26 |
| CLOSE_BOUNDARY | GME | 3 | 24.40 | 2026-10-26 | 24.820 | CAUSALLY_FEASIBLE_REFERENCE | stop condition 2026-10-26 | stop condition 2026-10-26 |
| CLOSE_BOUNDARY | EBAY | 1 | 119.20 | 2026-10-26 | 121.240 | CAUSALLY_FEASIBLE_REFERENCE | stop condition 2026-10-26 | stop condition 2026-10-26 |
| CLOSE_BOUNDARY | EBAY | 2 | 117.50 | 2026-10-27 | UNAVAILABLE | NEXT_OPEN_UNOBSERVED | NO_COMPARABLE_REFERENCE | NO_COMPARABLE_REFERENCE |
| LATE | CLMT | 1 | 55.25 | 2026-10-19 | 57.470 | CAUSALLY_FEASIBLE_REFERENCE | stop condition 2026-10-19 | stop condition 2026-10-21 |
| LATE | CLMT | 2 | 53.40 | 2026-10-20 | 56.200 | CAUSALLY_FEASIBLE_REFERENCE | stop condition 2026-10-21 | stop condition 2026-10-21 |
| LATE | CLMT | 3 | 53.02 | 2026-10-21 | 56.400 | CAUSALLY_FEASIBLE_REFERENCE | stop condition 2026-10-21 | stop condition 2026-10-21 |
| LATE | TEVA | 1 | 40.40 | 2026-10-19 | 41.420 | CAUSALLY_FEASIBLE_REFERENCE | stop condition 2026-10-21 | stop condition 2026-10-22 |
| LATE | TEVA | 2 | 39.35 | 2026-10-22 | 40.200 | CAUSALLY_FEASIBLE_REFERENCE | stop condition 2026-10-23 | protected through data end |
| LATE | TEVA | 3 | 39.05 | 2026-10-23 | 39.750 | CAUSALLY_FEASIBLE_REFERENCE | protected through data end | protected through data end |
| LATE | GME | 1 | 25.01 | 2026-10-22 | 26.000 | CAUSALLY_FEASIBLE_REFERENCE | stop condition 2026-10-22 | stop condition 2026-10-23 |
| LATE | GME | 2 | 24.78 | 2026-10-23 | 25.340 | CAUSALLY_FEASIBLE_REFERENCE | stop condition 2026-10-23 | stop condition 2026-10-26 |
| LATE | GME | 3 | 24.40 | 2026-10-26 | 24.820 | CAUSALLY_FEASIBLE_REFERENCE | stop condition 2026-10-26 | stop condition 2026-10-26 |
| LATE | EBAY | 1 | 119.20 | 2026-10-26 | 121.240 | CAUSALLY_FEASIBLE_REFERENCE | stop condition 2026-10-26 | stop condition 2026-10-26 |
| LATE | EBAY | 2 | 117.50 | 2026-10-27 | UNAVAILABLE | NEXT_OPEN_UNOBSERVED | NO_COMPARABLE_REFERENCE | NO_COMPARABLE_REFERENCE |

## Replacement forward registration

Status: **PENDING_CURRENT_SOURCE_AND_MARKET_EVIDENCE** at 2026-10-29T23:37:00-04:00. Required latest eligible session: 2026-10-29; available market observations end 2026-10-26. No replacement forecast was registered.

Known active symbols SIG, CNQ, MMM, SAIL, SLB and benchmark SPY lack October 27–29 bars. Active DUK, PAA, FCX, CRWV and NBIS have no qualified market identities/history in the archive. All ten active setups lack current technical evidence. The supplied alert bodies have not been attested complete through registration. The gate requires consecutive completed feature sessions and a matching ordered alert-manifest attestation; it never fetches an automatic subscriber feed or fills gaps.

The sealed original forward forecast `36b732cdb82e74a9c90f8add9d6e66015f31bcf9da156cb6213a858bf7676135` remains byte-identical and unevaluated, but is **non-operational**. October 27–29 backfill is not fresh validation of that stale forecast. New forecasts target eligibility and setup removal, with removal abstention until a defensible rule exists; hypothetical stop-out is never mapped to source DROP.
