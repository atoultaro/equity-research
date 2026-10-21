# Research conventions and acceptance record

Current task: project PR4, first end-to-end equity swing slice. Authoritative user
instructions override provisional milestone numbering. Related design sources at
https://github.com/atoultaro/finwhaling/tree/98034e009ac2c062e5a23aad1ba1cf56f2c94001/doc/equity_trading
are PRD.md, ARCHITECTURE.md, RESEARCH.md, AGENT_GUIDE.md, FINWHALING_REUSE_AUDIT.md,
REUSE_CHARACTERIZATION_REPORT.md and INDICATOR_EXTRACTION_REPORT.md. Root finwhaling
AGENTS.md was read for engineering/timing/friction safety; no MES research or runtime
behavior is changed. See MVP_SPEC.md for the concrete new equity contracts.

The canonical dataset and example are synthetic engineering evidence, not a
historical selection backtest or evidence of edge. Q2 qualification and Q3
execution are primary; position policies and benchmark/portfolio research are
later. External sources discover candidates; they do not become order engines.
No fundamentals, screening-membership reconstruction, external RS invention,
directional prediction, calendar tuning or parameter search occurs here.

## Hand reconciliation

The committed example's signal is2026-03-10, observed/available20:15Z, after its
20:00Z close. History is60 bars, ATR14=2, SMA50=117.25, prior SMA50=114.75,
signal close129.5, high130.5. The order triggers at130.60; initial stop125.50.

2026-03-11 opens132, so actual entry132.01. Risk/share6.51, budget100, quantity15,
original dollar risk97.65. The two-R target145.03 is touched on2026-03-13; modeled
exit145.02. Gross reference-price PnL195.45 −slippage.30 −commission.150 −fees1.00
=net194.000. Net realized R=194/97.65=1.986687147977470558115719406. All shares exit;
final cash10194.000. This is a fixture result, not a strategy verdict.

An independent ten-share hand case uses entry reference100, actual100.25, stop98,
exit reference104, actual103.75: original risk22.50, gross40, slippage5, commissions2,
fees2, net31, realized R31/22.50. The stop never moves and risk is never recomputed.

## Deterministic acceptance coverage

| Scenario | Evidence |
| --- | --- |
| Post-close and delayed availability | test_execution: same-day prohibited, midday arrival skips already-open session |
| Missing history/positive ATR/liquidity/trend | test_qualification: WATCH/REJECT reasons, no silent qualification |
| No future information | Future bars poisoned without changing decision; entry close changed without changing entry sizing/fill |
| Trigger expiry/unfilled endpoint | Three-session expiry with later breakout ignored; truncated/no-future data retains unfilled outcome |
| Entry gap | Uses132.01 instead of old trigger130.60; size reflects actual risk |
| Stop gap | Next open120 exits119.99, net−181.45, original risk97.65 retained |
| Daily collision | Stop first plus ambiguity flag; intraday entry cannot exit at preceding open |
| Cash/risk/quantity | Exact quotient floors, fees reserved, notional cap, zero/invalid stop rejected |
| Costs and R | Both hand cases reconcile gross-to-net, two-sided costs and immutable denominator |
| Max holding/end data | Full exit with reason; no hidden open positions |
| Empty/rejected results | Research files and header-only ledger still exist |
| Provenance/actions | Missing source evidence/unsupported vendors not treated as historical observations; adjusted/actions data rejected |
| Data | Hash, finite/positive/consistent OHLCV, security/date duplicates/order/completeness, aware session schedule/early close |
| Reproducibility | Repeated input/source/config bytes yield identical all artifacts and verified hashes; output overwrite fails |
| Environment | Clean venv installs two local wheels, executes CLI twice without monorepo or optional libraries; pip uses no-index/no-deps |

Tests use fixed data/times; network sockets are denied in pytest. Packaging subprocesses
use only local wheels and no-index. There is no production network client. The
final suite has58 passing tests including the clean installation test, with no skips.
Command: `.venv/bin/python -m pytest -q` from the repository root. The draft PR
records the final timing. Python/runtime identity is part of the experiment manifest.
No canonical lint/format command is configured. Source revision and dependency pin
are part of artifacts; fixture tests explicitly label their synthetic asserted SHAs.

## Limits and next review

The explicit schedule must itself be complete/authentic; OHLCV cannot detect a
holiday error or an undeclared corporate action. One policy, one symbol and one
candidate do not supply portfolio statistics. Missing intraday ordering, cash
dividends, splits/delistings, borrow/short mechanics, benchmark exposure, advanced
fee rules, vendor archival access and real fill calibration are not implemented.
No external historical dataset was fetched or tested. All tests are offline.

Do not implement the next milestone before review. The next useful diagnostic is
manual audit of point-in-time inputs and execution assumptions on this fixed slice,
not a profitability recommendation or a parameter grid.
