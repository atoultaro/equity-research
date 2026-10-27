# PR8B existing-source historical equity pilot

Origin: **RECORDED**. Existing immutable captures only; no new acquisition.

Observed catalogue: 50 contracts; pilot: 31 stocks, 13,625 daily rows.

This is a retrospectively chosen observed-contract cohort. It is not a complete historical stock population, a historical screening list or survivorship-bias-free research. Capture symbols are display aliases; historical ticker/issuer/share-class continuity is unverified.

## Two dated observations and unchanged admission gates

| Date | Observed contracts | Complete 60-session native windows | Strict admitted | Reconstructed admitted |
|---|---:|---:|---:|---:|
| 2026-08-31 | 30 | 30 | 0 | 0 |
| 2026-09-30 | 31 | 30 | 0 | 0 |

A complete native window is a bar-presence measurement, not eligibility for PR8A liquidity ranking. The strict gate requires historically known identity; the explicit reconstruction gate additionally exposes missing classification/listing history and unadmitted split-adjusted price/unverified volume units. Both return PIT_UNVERIFIED. Source clocks remain null; Close +60 minutes is only the existing explicit reconstruction query assumption. No prices, listing dates, corporate actions or terminal returns are inferred.

## Observed coverage by contract

Gaps use the frozen XNYS session calendar within each observed first/last span. Unobserved periods outside that span cannot be distinguished as pre-listing versus unavailable data. ETFs are context instruments and do not enter the stock pilot.

| Capture alias | conId | Kind | First observed | Last observed | Sessions | Internal gaps |
|---|---:|---|---|---|---:|---:|
| AAOI | 135423662 | stock | 2025-01-02 | 2026-10-26 | 455 | 0 |
| AAPL | 265598 | stock | 1980-12-12 | 2026-10-26 | 11559 | 3 |
| ABBV | 118089500 | stock | 2025-01-02 | 2026-10-26 | 455 | 0 |
| AMD | 4391 | stock | 2025-01-02 | 2026-10-26 | 455 | 0 |
| AMZN | 3691937 | stock | 1997-05-15 | 2026-10-26 | 7409 | 0 |
| ANET | 740948854 | stock | 2025-01-02 | 2026-10-26 | 455 | 0 |
| ASST | 852120292 | stock | 2025-01-02 | 2026-10-26 | 455 | 0 |
| CAT | 5437 | stock | 2025-01-02 | 2026-10-26 | 455 | 0 |
| CDE | 60532895 | stock | 2025-01-02 | 2026-10-26 | 455 | 0 |
| CIBR | 199295926 | industry_etf | 2022-01-03 | 2026-10-26 | 1208 | 0 |
| CLMT | 715002751 | stock | 2025-01-02 | 2026-10-26 | 455 | 0 |
| CNQ | 11926119 | stock | 2025-01-02 | 2026-10-26 | 455 | 0 |
| COPX | 211651700 | industry_etf | 2022-01-03 | 2026-10-26 | 1208 | 0 |
| EBAY | 4347086 | stock | 2025-01-02 | 2026-10-26 | 455 | 0 |
| ELF | 248682005 | stock | 2025-01-02 | 2026-10-26 | 455 | 0 |
| GE | 498843743 | stock | 2022-01-03 | 2026-10-26 | 1208 | 0 |
| GME | 36285627 | stock | 2025-01-02 | 2026-10-26 | 455 | 0 |
| GOOG | 208813720 | stock | 2014-03-27 | 2026-10-26 | 3165 | 0 |
| GTLB | 520512263 | stock | 2025-01-02 | 2026-10-26 | 455 | 0 |
| HUM | 8251 | stock | 2025-01-02 | 2026-10-26 | 455 | 0 |
| ITA | 39046959 | industry_etf | 2022-01-03 | 2026-10-26 | 1208 | 0 |
| IWM | 9579970 | market_etf | 2000-05-26 | 2026-10-26 | 6642 | 1 |
| META | 107113386 | stock | 2012-05-18 | 2026-10-26 | 3630 | 0 |
| MMM | 9720 | stock | 2025-01-02 | 2026-10-26 | 455 | 0 |
| MSFT | 272093 | stock | 1986-03-13 | 2026-10-26 | 10235 | 0 |
| NVDA | 4815747 | stock | 1999-01-22 | 2026-10-26 | 6984 | 0 |
| OIH | 415578515 | industry_etf | 2022-01-03 | 2026-10-26 | 1208 | 0 |
| OMER | 69342644 | stock | 2025-01-02 | 2026-10-26 | 455 | 0 |
| QQQ | 320227571 | market_etf | 1999-03-10 | 2026-10-26 | 6951 | 0 |
| RSP | 319359375 | market_etf | 2003-04-30 | 2026-10-26 | 5909 | 2 |
| SAIL | 760966616 | stock | 2025-02-13 | 2026-10-26 | 427 | 0 |
| SCCO | 1812968 | stock | 2022-01-03 | 2026-10-26 | 1208 | 0 |
| SIG | 53747825 | stock | 2025-01-02 | 2026-10-26 | 455 | 0 |
| SLB | 12200 | stock | 2022-01-03 | 2026-10-26 | 1208 | 0 |
| SMH | 229725622 | industry_etf | 2011-12-21 | 2026-10-26 | 3732 | 0 |
| SNDK | 760250490 | stock | 2025-02-13 | 2026-10-26 | 427 | 0 |
| SNOW | 444884769 | stock | 2025-01-02 | 2026-10-26 | 455 | 0 |
| SPY | 756733 | market_etf | 1993-01-29 | 2026-10-26 | 8491 | 2 |
| T | 37018770 | stock | 2025-01-02 | 2026-10-26 | 455 | 0 |
| TEVA | 922990633 | stock | 2026-09-14 | 2026-10-26 | 31 | 0 |
| XBI | 45540828 | industry_etf | 2006-02-06 | 2026-10-26 | 5212 | 1 |
| XLB | 4215200 | sector_etf | 2022-01-03 | 2026-10-26 | 1208 | 0 |
| XLC | 322317077 | sector_etf | 2025-01-02 | 2026-10-26 | 455 | 0 |
| XLE | 4215217 | sector_etf | 1998-12-22 | 2026-10-26 | 7001 | 2 |
| XLF | 4215220 | sector_etf | 1998-12-22 | 2026-10-26 | 7001 | 2 |
| XLI | 4215227 | sector_etf | 1998-12-22 | 2026-10-26 | 7000 | 3 |
| XLK | 4215230 | sector_etf | 1998-12-22 | 2026-10-26 | 7001 | 2 |
| XLP | 4215210 | sector_etf | 2025-01-02 | 2026-10-26 | 455 | 0 |
| XLV | 4215205 | sector_etf | 1998-12-22 | 2026-10-26 | 7001 | 2 |
| XLY | 4215215 | sector_etf | 2025-01-02 | 2026-10-26 | 455 | 0 |

## Coverage across fixed market-cycle windows

Counts are contracts with any bars / all expected bars in that window, not the number of stocks that existed then. A later-chosen surviving or expert-mentioned sample cannot establish historical cross-sectional performance.

| Window | Stocks any / full | ETFs any / full |
|---|---:|---:|
| 2008 first half | 4 / 4 | 10 / 10 |
| 2015 first half | 6 / 6 | 11 / 11 |
| 2020 first half | 6 / 6 | 11 / 11 |
| 2022 first half | 9 / 9 | 16 / 16 |
| 2026 through October 26 | 31 / 30 | 19 / 19 |

## Remaining uncertainty

All included native histories retain documented IBKR split-adjusted prices and unverified volume units. Original historical dissemination times and corporate-action completeness are unknown for every instrument. Qualified conIds establish captured contract identity; they do not establish historic symbols, listing status or complete issuer histories. Zero verified delisted histories were imported; the count of omitted historical securities is UNKNOWN because no complete population denominator exists. An empty imported action inventory means not supplied, not no actions.

The 26-trade Grimes status CSV is a separate source-ledger projection, not this price cohort. No actual trade fills, source closure causes, strategy edge, returns from a tradable universe or execution admission are claimed.

## Immutable dependency hashes

- reconstruction: `0b9f59998c76e0c3173b9a299949c0fe85d4eb74f1103233392312734e55791b`
- research_panel: `5c74346b0c39d2a1f0173f45ad35af46a303c9a91b489d6e2368ee2f3c98fa61`
- security_master: `71928b7662275e8e6350bde07cac572ea5901f23d969e6c1a0fb31a0c2676d5e`
- strict: `e2f06f5b1c2913d57c43b43d662bb5ac97ea4167cb908d4d78b3698918203d2d`
- inputs: `64f26510e7e9e1fae5c8982fbf2c1ba3d093015996f5321ccf6a97931a39b08f`
