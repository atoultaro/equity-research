# Price and volume diagnostics

Native captures remain immutable. Existing independently documented split assertions are retrospective corroboration, not newly acquired prices or historically available screening evidence. Derived views undo one known split component only; they are never labeled verified raw OHLC. Volume is unchanged in every derived view.

| Symbol/effective split | Native post-Open/pre-Close | Ratio after undoing known component | Median native volume after/before |
|---|---|---|---|
| AAPL 2020-08-31 4:1 | 1.022 | 0.256 | 1.409 |
| GOOG 2022-07-18 20:1 | 1.006 | 0.050 | 1.822 |

Near-continuous native prices across these splits corroborate split adjustment. Neither these two examples nor a volume ratio establish exhaustive corporate-action coverage, raw nominal prices, shares-vs-lots settings, dividend adjustment, or split-adjusted volume. Technical indicators can be conditional on a consistent native scale; stop simulation additionally needs nominal-stop compatibility. Absolute dollar volume requires documented contemporaneous price and share units and is not admitted here.

Uniformly scaling prices, stops and ATR preserves risk/ATR and barrier ordering. A price-only scale can change those conclusions and therefore needs independent evidence; no factor is fitted to make a trade succeed. EXPLORATORY_RECONSTRUCTION supports explicitly labeled uniform sensitivity views with unchanged native volume, never a claim of raw reconstruction.

- AAPL conId 265598: NATIVE_NOMINAL_COMPATIBILITY_ASSUMED; volume IBKR_NATIVE_UNITS_UNVERIFIED.
- CLMT conId 715002751: NATIVE_NOMINAL_COMPATIBILITY_ASSUMED; volume IBKR_NATIVE_UNITS_UNVERIFIED.
- TEVA conId 922990633: NATIVE_NOMINAL_COMPATIBILITY_ASSUMED; volume IBKR_NATIVE_UNITS_UNVERIFIED.
- CAT conId 5437: NATIVE_NOMINAL_COMPATIBILITY_ASSUMED; volume IBKR_NATIVE_UNITS_UNVERIFIED.
- CDE conId 60532895: NATIVE_NOMINAL_COMPATIBILITY_ASSUMED; volume IBKR_NATIVE_UNITS_UNVERIFIED.
- T conId 37018770: NATIVE_NOMINAL_COMPATIBILITY_ASSUMED; volume IBKR_NATIVE_UNITS_UNVERIFIED.
- ELF conId 248682005: NATIVE_NOMINAL_COMPATIBILITY_ASSUMED; volume IBKR_NATIVE_UNITS_UNVERIFIED.
- HUM conId 8251: NATIVE_NOMINAL_COMPATIBILITY_ASSUMED; volume IBKR_NATIVE_UNITS_UNVERIFIED.
- SIG conId 53747825: NATIVE_NOMINAL_COMPATIBILITY_ASSUMED; volume IBKR_NATIVE_UNITS_UNVERIFIED.
- ASST conId 852120292: NATIVE_NOMINAL_COMPATIBILITY_ASSUMED; volume IBKR_NATIVE_UNITS_UNVERIFIED.
- OMER conId 69342644: NATIVE_NOMINAL_COMPATIBILITY_ASSUMED; volume IBKR_NATIVE_UNITS_UNVERIFIED.
- GME conId 36285627: NATIVE_NOMINAL_COMPATIBILITY_ASSUMED; volume IBKR_NATIVE_UNITS_UNVERIFIED.
- AAOI conId 135423662: NATIVE_NOMINAL_COMPATIBILITY_ASSUMED; volume IBKR_NATIVE_UNITS_UNVERIFIED.
- AMD conId 4391: NATIVE_NOMINAL_COMPATIBILITY_ASSUMED; volume IBKR_NATIVE_UNITS_UNVERIFIED.
- ANET conId 740948854: NATIVE_NOMINAL_COMPATIBILITY_ASSUMED; volume IBKR_NATIVE_UNITS_UNVERIFIED.
- SNDK conId 760250490: NATIVE_NOMINAL_COMPATIBILITY_ASSUMED; volume IBKR_NATIVE_UNITS_UNVERIFIED.
- ABBV conId 118089500: NATIVE_NOMINAL_COMPATIBILITY_ASSUMED; volume IBKR_NATIVE_UNITS_UNVERIFIED.
- CNQ conId 11926119: NATIVE_NOMINAL_COMPATIBILITY_ASSUMED; volume IBKR_NATIVE_UNITS_UNVERIFIED.
- EBAY conId 4347086: BOUNDED_QUOTE_ANCHOR; volume IBKR_NATIVE_UNITS_UNVERIFIED.
  Avoiding the 119.20 hard-stop touch through price-only scaling would require a factor strictly greater than 1.011283617544752693645541698. This conflicts with the retained matching 117.87 nominal Low anchor; no such rescaling is supported.
- GTLB conId 520512263: NATIVE_NOMINAL_COMPATIBILITY_ASSUMED; volume IBKR_NATIVE_UNITS_UNVERIFIED.
- MMM conId 9720: NATIVE_NOMINAL_COMPATIBILITY_ASSUMED; volume IBKR_NATIVE_UNITS_UNVERIFIED.
- SNOW conId 444884769: NATIVE_NOMINAL_COMPATIBILITY_ASSUMED; volume IBKR_NATIVE_UNITS_UNVERIFIED.
- SAIL conId 760966616: NATIVE_NOMINAL_COMPATIBILITY_ASSUMED; volume IBKR_NATIVE_UNITS_UNVERIFIED.
- SLB conId 12200: NATIVE_NOMINAL_COMPATIBILITY_ASSUMED; volume IBKR_NATIVE_UNITS_UNVERIFIED.
- GE conId 498843743: NATIVE_NOMINAL_COMPATIBILITY_ASSUMED; volume IBKR_NATIVE_UNITS_UNVERIFIED.
- SCCO conId 1812968: NATIVE_NOMINAL_COMPATIBILITY_ASSUMED; volume IBKR_NATIVE_UNITS_UNVERIFIED.
