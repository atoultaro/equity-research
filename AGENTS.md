# Equity research boundaries

Read README.md, docs/MVP_SPEC.md and docs/RESEARCH_CONVENTIONS.md first.
Task type is strategy development. State branch and authoritative task before edits.
One candidate, one symbol, one long swing policy; preserve point-in-time semantics.
No broker connections, vendor fetching, live/paper orders, optimization or deployment.
Use small deterministic local fixtures. Run `python -m pytest -q` after changes.
Do not claim an edge from synthetic data. Do not infer historical screening membership.
Separate fees/slippage, actual initial risk and gross/net dollars. Fail on missing
sessions; never forward fill. Do not overwrite run directories or revise immutable inputs.
Shared mathematics comes from the pinned vendor wheel; do not duplicate ATR.
Do not change finwhaling as a side effect. No canonical lint command is configured.
