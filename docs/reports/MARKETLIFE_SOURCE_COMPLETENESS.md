# MarketLife source-history completeness

Audit as of 2026-10-30T13:12:59.892784+00:00. Native current archive SHA256: `07882253d2207a3117a115d40e04f469b207eccfd99f8b67a0375377e4ec5184`. Public evidence SHA256: `97068d3bcf0d6216bf064f89765a12a9e72239129931022096be14e614d24080`. [Input registry](../evidence/pr9d-current-readiness-v3/manifest.json); [regression and replay record](../evidence/pr9d-validation-v2/validation.json).

The retained ledger has **10 alerts, 116 parsed actions and 34 captured setup episodes**. No later alert was fabricated or fetched from subscriber-only content. Actual subscriber fills and positions remain UNKNOWN.

| Alert | Original publication | Precision | Availability lower bound | Availability upper bound |
| --- | --- | --- | --- | --- |
| alert-1 | 2026-10-18T15:20:00-04:00 | MINUTE | 2026-10-18T19:20:00+00:00 | 2026-10-18T19:21:00+00:00 |
| alert-2 | 2026-10-19T18:19:00-04:00 | MINUTE | 2026-10-19T22:19:00+00:00 | 2026-10-19T22:20:00+00:00 |
| alert-3 | 2026-10-20T18:25:00-04:00 | MINUTE | 2026-10-20T22:25:00+00:00 | 2026-10-20T22:26:00+00:00 |
| alert-4 | 2026-10-21T18:50:00-04:00 | MINUTE | 2026-10-21T22:50:00+00:00 | 2026-10-21T22:51:00+00:00 |
| alert-5 | 2026-10-22T18:27:00-04:00 | MINUTE | 2026-10-22T22:27:00+00:00 | 2026-10-22T22:28:00+00:00 |
| alert-6 | UNKNOWN | UNKNOWN | 2026-10-22T22:28:00+00:00 | 2026-10-25T12:57:45+00:00 |
| alert-7 | 2026-10-26T18:10:00-04:00 | MINUTE | 2026-10-26T22:10:00+00:00 | 2026-10-26T22:11:00+00:00 |
| operator-20261027 | UNKNOWN | DATE | 2026-10-27T00:00:00-04:00 | 2026-10-27T23:59:59.999999-04:00 |
| operator-20261028 | UNKNOWN | DATE | 2026-10-28T00:00:00-04:00 | 2026-10-28T23:59:59.999999-04:00 |
| operator-20261029 | UNKNOWN | DATE | 2026-10-29T00:00:00-04:00 | 2026-10-30T02:16:14+00:00 |

The original weekly publication remains UNKNOWN. October 27–29 retain their operator dates without exact publication times. Source batches keep their original receipt timestamps: appending a later batch cannot widen an earlier date-only bound. The current source view is conditional on these bounds and the original ordering.

Ordered alert/body manifest SHA256: `3cefa799bfbdc16e1ec41803638a48cb1cd1a3290804de0125b80d391ec72b37`. A matching hash proves agreement with the supplied records, **not completeness of an external MarketLife feed**.

Completeness assertion status: **FAIL**. The operator supplied all material available to them; external source-history completeness remains unverified. No stronger assertion is inferred. This is an operator declaration, not independent feed verification. A failed assertion blocks registration.

The operator stated: “I gave you all I have.” That is recorded as availability of the supplied material, not a claim that the external feed has no omitted alerts. No further subscriber material was requested and no completeness assertion was invented.

## Explicit later-alert intake

Supply a new JSON batch with schema marketlife_operator_alerts_v1, captured_at, and an ordered alerts array. Each alert retains its original complete text and four action sections, unique alert_id, source_reference, source_date, nullable published_at and publication_precision (DATE, MINUTE or SECOND). Original display metadata is retained when supplied. No source content is fetched automatically.

The source command validates the entire chain before sealing a new bundle. It rejects duplicate IDs or duplicate bodies at the same publication evidence, inconsistent old stops, invalid previous eligibility, unsupported lines and reversed chronology. Identical ADDED wording on a later date can be a legitimate new episode after DROPPED; it is not deduplicated merely by text. UNDERWAY suspends entry; a monitored stop update does not reset eligibility; an explicit return creates a fresh version. DROPPED never establishes an executed exit.

Completeness is a separate operator assertion containing complete=true, complete_through=REGISTRATION, the matching alert_manifest_sha256, source_reference, asserted_at and the operator_statement. An absent, future-dated or mismatched assertion blocks readiness. Retain the actual statement and assertion time; the program does not independently verify the subscriber feed. Renew this assertion for the registration being authorized, rather than treating old source captures as current feed completeness.
