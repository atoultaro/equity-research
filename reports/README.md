# Readable research outputs

[grimes_trade_status.csv](grimes_trade_status.csv) contains one row per source-reported
trade episode: all 26 stocks in the October 18–26, 2026 MarketLife study, including
the 12 reported closed episodes. PLTR and PEP are outside that study. The table is
UTF-8 CSV with standard quoting, a header and CRLF row endings, readable in Excel,
Numbers and text editors. Stops preserve the source's decimal text.

Reported OPEN/CLOSED and ENTERABLE/UNDERWAY are authoritative **source facts**.
OPEN means no DROPPED action was observed by the study end; it does not establish
an actual fill, holding or current live position. UNDERWAY is the source's setup
label, not a simulated trigger. The latest source stop survives regardless of
what any model did. The table is fixed at this study's cutoff, not a live tracker.

In particular, CDE is **SHORT / OPEN / UNDERWAY**, latest reported stop **13.90**.
EBAY is **LONG / OPEN / ENTERABLE**, latest reported stop **117.50**.
The separately documented PR16 primary model stopped out EBAY under its declared
assumptions. That result does not close the source episode. CDE also has a distinct
conditional model history that assumes unverified stop/native-bar compatibility.
See [PR16 source/model reconciliation](../docs/GRIMES_TRADE_LIFECYCLES.md) and its
[full research report](../docs/reports/GRIMES_LIFECYCLES_20261018_26.md). Actual
execution outcomes remain unknown.

Following the revised PR8B request, this is a **source-only table**. The earlier
proposed modeled-status, modeled-exit and source/model-conflict columns are kept
out of this table; modeled histories remain in the separate frozen PR16 outputs.
The source columns retain the earlier agreed order, followed by notes.

`opened_alert_date`, `last_alert_date` and `dropped_alert_date` use only the
source's known publication timestamp, converted to New York calendar dates.
`last_alert_date` is the last alert **mentioning that episode**, not the study's
last global alert. The weekly alert's unresolved calendar date stays `UNKNOWN`;
its email arrival/effective bound is never substituted. A blank dropped date
means no source closure; `UNKNOWN` means a closure was reported with an unresolved
publication date. `last_reported_action` is the original parsed action type.

## Deterministic generation

The immutable [source-fact projection](inputs/grimes-source-ledger-v1/provenance.json)
retains all 72 parsed action records, source locators and original alert-body
hashes from PR16 `study-v5`, bundle
`4ce1b1f021d666bb870983cf894628c665992f97186e6e2740ccd2f4e69b2604`.
Original subscriber bodies and modeled results are excluded. This public projection
is a hash-bound reproducibility input, not an independent signature or replacement
for the private original source capture. The generator reuses PR16's unchanged
source interpreter instead of maintaining a second lifecycle state machine.

```sh
PYTHONPATH=src .venv/bin/python scripts/report_grimes_trade_status.py generate --source reports/inputs/grimes-source-ledger-v1 --output NEW_UNUSED_PATH.csv
PYTHONPATH=src .venv/bin/python scripts/report_grimes_trade_status.py verify --source reports/inputs/grimes-source-ledger-v1 --csv reports/grimes_trade_status.csv
```

Generation refuses to overwrite an existing output. The current CSV is versioned
and verified byte-for-byte by automated tests; it is not maintained manually.
To independently reproduce the source projection from the original local study,
use `capture-source --study runs/grimes-lifecycle-20261018-26-v1/study-v5 --output
NEW_UNUSED_DIRECTORY`. That command validates PR16's complete frozen study first.
No local price data is needed to regenerate the CSV from the committed projection.
