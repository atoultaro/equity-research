# Historical universe provider evaluation — PR 8A

Public documentation checked **2026-10-23**. This is a feasibility assessment,
not verification of delivered data or permission to acquire it. No subscription,
credentials, institutional affiliation or authorized broad-universe export was
supplied. PR 8A therefore uses only generated offline fixtures. Existing IBKR
captures are comparison evidence for five instruments, not a historical stock
universe. The current TWS port does not change that scope.

## Decision

**Prefer CRSP for the eventual canonical research source, conditional on legitimate
institutional or separately negotiated access.** Permanent security/company IDs,
name histories and explicit delisting-return/missing-return fields best address
this project's historical-validity requirements. Access, applicable license,
retention/output rights and actual delivery vintage remain blockers. No CRSP
account or entitlement is assumed.

For an individual budget, **Norgate US Platinum is the preferred alternative to
evaluate**, subject to an authorized Windows acquisition environment and acceptable
retention terms. It covers the target years and delisted stocks; Gold's 20-year
currently listed history is insufficient. Sharadar Full History Prices is a
credible macOS-friendly HTTP alternative to evaluate, especially if Windows is
unavailable. Its documented permaticker and action history are useful, but
historical publication vintages, classification reconstruction and native raw
OHLCV suitability still need an actual licensed sample audit. No provider is
silently selected as a fallback; none is certified by this recommendation.

## Decision matrix

“Documented” describes vendor documentation, not observations independently
verified here. “Unknown” means that the inspected material does not establish the
required property. Sources below apply to the corresponding columns.

| Requirement | Norgate US Platinum | CRSP US Stock | Sharadar / Nasdaq Data Link lineage |
|---|---|---|---|
| Historical period | Listed/delisted back to 1990; Diamond 1950 | Exchange-specific history: NYSE 1925/26, American 1962, Nasdaq 1972; product variants differ | Stocks December 1997; actions January 1998; metadata earlier |
| Listed and delisted | Both; formerly major-exchange OTC also included | Active and inactive securities documented | Both; vendor estimates incomplete residual coverage; no independent completeness claim |
| Delisting date/reason | Delisted database and security dates documented; completeness of reason taxonomy needs sample audit | Delisting dates/codes and security-status fields | Listing/delisting action types and reasons; last price date is not itself a delisting date |
| Terminal value/return | Last quotation and capital-event data are useful; complete recovery/terminal-return coverage unverified | Explicit delisting amount/price/return and missing-type fields; missing is not zero | Cash/stock/elective acquisition consideration documented, CVRs excluded; comprehensive bankruptcy terminal returns unverified |
| Permanent identity | Asset ID API, independent of current ticker | PERMNO security, PERMCO company | Permaticker; separate classes have distinct IDs |
| Ticker/exchange history | Historical listing indicators; exact dated symbol/venue reconstruction needs sample audit | Name/identifier histories and exchange/status fields | Rename and exchange-from/to actions; reused delisted tickers get a suffix |
| Common-stock eligibility | Security metadata, major-exchange and blank-check indicators; historical classification availability needs audit | Share/security classification codes, with dated history to map carefully | Category separates instrument/origin/class role; current category must not be treated as historical |
| Historical constituents | Included in Platinum/Diamond; never a substitute for all-market eligibility | Historical security histories and index products; required external index entitlements not presumed | S&P 500 table; no claim of complete all-index membership |
| Volume / dollar volume | OHLCV; compute dollar volume only after price/volume unit reconciliation | Daily prices/volume; exchange-era units and missing flags require mapping | Split-adjusted OHLCV; raw volume requires documented reconstruction; never mix adjusted Close and raw units blindly |
| Price conventions | Unadjusted/capital-adjusted/total-return modes; choose explicit mode and no padding | Prices, adjustment factors and return series are distinct; quote/missing flags must survive | OHLCV split-adjusted, CloseUnadj raw Close, CloseAdj also dividends/spinoffs; other raw OHLC fields are imputed, not native trades |
| Actions | Dividends and capital events; detailed merger/spinoff mapping needs audit | Distributions and corporate actions | Splits, dividends, spinoffs, ADR changes, mergers and consideration actions |
| Historical availability | Effective history does not prove original publication time; archive guarantee unknown | Release vintages and revisions exist; event effective dates do not by themselves prove trader knowledge | Last-updated dates and delivery clocks are not original publication archives; fundamentals AR dimensions do not certify stock-price/master vintages |
| Bulk delivery | Local proprietary updater database; price ASCII export, richer metadata through integrations | Licensed flat-file deliveries and authorized third-party access | Authenticated REST and prepared zipped CSV bulk tables, by purchased history tier |
| Python / macOS | Python wrapper requires Windows and running NDU; not native macOS | Product tooling lists Windows/Linux; licensed ASCII or authorized remote WRDS access can be processed on macOS | HTTP/CSV/JSON has no Windows updater dependency; credentials/license still required |
| License / outputs | Individual personal use; processing on other OS permitted while licensed; redistribution and retention restricted | Institutional/negotiated terms; no permission for raw-data publication inferred | Personal plan is individual nonprofessional; organizations need commercial arrangements; attribution/output restrictions apply |
| Cost / operations | Platinum USD630/year; Diamond USD787.50/year, as checked; Windows operations extra | Subscription quote / eligible institution plus actual CRSP entitlement; not a public free WRDS account | Full History Prices USD39/month or USD299/year as checked; Full History Bundle USD499/year; cheaper five-year plans do not cover 2007 |
| Revisions / reproducibility | Freeze licensed exports and update/source provenance; no original historical vintage guarantee established | Retain permitted release vintage and revision notes; do not confuse revised database with as-published archive | Preserve exact bulk snapshot and last-updated metadata; later corrections must be new snapshots |

| Requirement | IBKR comparison only | Yahoo supplemental only |
|---|---|---|
| Period | Contract-dependent; existing local captures cover limited recent intervals | Quote-dependent; help says prices usually no earlier than 1970 |
| Listed/delisted | Official limitations exclude securities no longer trading | No comprehensive listed/delisted historical population guarantee established |
| Delisting date/reason | No complete historical master established | Unknown |
| Terminal return | No dependable delisting recovery archive established | Unknown |
| Permanent IDs | Qualified contract/conId useful for selected contracts, not proof of complete historical identity | Ticker-oriented; permanent identity archive unverified |
| Ticker/venue history | Pre-transfer history may be unavailable | Historical ticker/venue archive unverified |
| Historical common-stock eligibility | Contract metadata alone does not reconstruct past all-market classifications | Current quote metadata cannot establish it |
| Historical constituents | Not supplied by existing adapter | Not established |
| Volume / dollar volume | Historical trade filtering and revisions affect comparability | OHLCV available for many quotes; precise source conventions require capture-level audit |
| Basis | Existing IBKR TRADES adapter records documented split-adjusted price caveats and unverified volume basis | Adjusted Close incorporates splits/dividends; retain exact native fields and adapter policy |
| Actions | Existing independent PR6 event sidecars remain necessary | Price/dividend/split histories can supplement evidence, not prove completeness |
| Availability / PIT | Retrieval time is not historical dissemination time | Same; no historical-vintage guarantee established |
| Bulk | Paced contract requests, unsuitable as the canonical delisted-universe archive | No authorized comprehensive listed/delisted bulk source established |
| Python / OS | Existing optional adapter; local authenticated TWS and entitlements | Existing optional yfinance wrapper; not an official Yahoo data license |
| License / outputs | Account/data terms and permissions; no redistribution rights inferred | Help notes download licensing restrictions; subscription download is not redistribution permission |
| Cost / operations | Existing account plus relevant data entitlements and TWS operations | Official download help currently specifies Gold subscription; no purchase or workaround |
| Revisions | IBKR explicitly warns historical requests can differ over time | Snapshot exact bytes; no complete revision archive established |

## Operational and licensing blockers

Norgate's Python requirements explicitly include Windows and Norgate Data Updater.
The vendor describes Windows virtual machines on a Mac; a separately authorized
Windows acquisition machine exporting licensed bytes to macOS is another possible
architecture. Neither was installed or provisioned. ASCII price export alone does
not establish export of constituent or classification history. Current personal
terms permit processing on other systems, including third-party processing for the
licensee under conditions, but do not grant independent sharing rights. The
2026-10-02 EULA and FAQ require deletion of retained Content after expiry, subject
to the stated renewal conditions; normalized histories and metadata remain
Content. Immutable research snapshots do not override that requirement. A future
acquisition decision must settle retention and published-artifact rights before
raw or normalized licensed data is frozen. Only independent permitted derived
outputs may qualify for different treatment; this PR makes no legal determination.

CRSP access through WRDS requires eligible institutional registration **and** the
institution's product entitlements; access to WRDS is not proof of access to CRSP.
No institutional membership or data-retention/publication permission was provided.
The official product distinguishes native Windows/Linux tooling from flat-file
and third-party delivery. macOS processing of authorized data is technically
possible without claiming a native CRSP desktop application.

Sharadar's current official documentation describes direct personal-use plans and
commercial arrangements, as well as the Nasdaq Data Link lineage. The precise
contract and endpoint must be checked for the purchased entitlement; older price
quotes and API assumptions are not authoritative. Its FAQ documents rewired ticker
history, stable permatickers, acquisition consideration and exchange actions.
Those facts improve feasibility but do not prove complete point-in-time
classification, unaltered historical publication vintages, or execution-admissible
raw OHLC. In particular, rescaling split-adjusted OHLC from CloseUnadj must remain
a derived representation, never silently relabeled native raw trades.

The source review did not establish a provider with both authorized access here
and verified field-level historical availability. **Real pilot blocked: no suitable
authorized source.** Synthetic testing exercises clocks and lifecycle behavior; it
cannot measure actual survivorship coverage, terminal proceeds or source quality.

## Primary documentation inspected

Norgate: [packages and current prices](https://norgatedata.com/stockmarketpackages.php),
[content tables](https://norgatedata.com/data-content-tables.php),
[Python API and requirements](https://pypi.org/project/norgatedata/),
[export/integrations](https://norgatedata.com/accessibility.php),
[updater/macOS FAQ](https://norgatedata.com/ndu-faq.php),
[subscription/retention FAQ](https://norgatedata.com/faq.php),
[2026-10-02 EULA](https://norgatedata.com/subscribe/eula.php).

CRSP: [current product, coverage and delivery](https://www.crsp.org/research/crsp-us-stock-databases-2025-layout/),
[flat-file guide and delisting tables](https://www.crsp.org/crsp_pdf/crsp-us-stock-indexes-databases-guide-flat-file-format-1-0/),
[CRSP10 fields including delisting missing types](https://www.crsp.org/wp-content/uploads/guides/CRSP10_Year_US_Stock_Database_Guide.pdf),
[WRDS description and identity/distribution histories](https://wrds-www.wharton.upenn.edu/demo/crsp/form/),
[institutional login constraints](https://support.wharton.upenn.edu/help/115002504226-how-can-i-log-into-wharton-research-data-services-wrds-).

Sharadar: [stocks](https://sharadar.com/docs/stocks),
[tickers](https://sharadar.com/docs/tickers), [actions](https://sharadar.com/docs/actions),
[FAQ](https://sharadar.com/docs/faqs), [plans/prices](https://sharadar.com/subscribe),
[personal-use terms](https://sharadar.com/terms),
[Nasdaq SEP documentation](https://data.nasdaq.com/databases/SEP/documentation?anchor=sample-data).

IBKR: [official historical availability, filtering and revision limitations](https://www.interactivebrokers.com/docs/tws-api/doc/md/introduction).
Yahoo: [historical download scope and restrictions](https://help.yahoo.com/kb/finance/certain-amounts-sln2311.html),
[adjusted Close](https://in.help.yahoo.com/kb/adjusted-close-sln28256.html).
These references establish assessment claims, not licenses or measured sample completeness.
