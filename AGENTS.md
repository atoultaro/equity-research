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

## Grimes research scope

Before Grimes-related research changes, read
[the research charter and roadmap](docs/research/GRIMES_RESEARCH_ROADMAP.md) and
[the setup/opportunity model](docs/MARKETLIFE_SETUP_AND_OPPORTUNITY_MODEL.md).
This research studies a partially observed latent trading decision policy.
Preserve the working causal order: structure → stop → risk → decision.
Prefer competing hypotheses, discriminating evidence and counterexamples over
speculative parameter fitting. Separate reported setup states and entry-opportunity
versions from hypothetical executions; alerts do not establish personal positions.
Do not impose exhaustive external-alert completeness as a universal prerequisite
for exploratory research. Mark missing evidence and assess vendor-revision materiality;
never invent observations or use information unavailable at a purported prediction time.
Existing operational forecast gates are not bypassed by this exploratory scope.
Do not turn a scientific question into an unrelated infrastructure project.
Attribute teachings, MarketLife statements, user interpretations and repository
hypotheses separately; do not claim Grimes endorses a hypothesis without direct
primary-source support. Every Grimes-related PR must describe the specific scientific
question it advances or preserves. Keep unrelated project and immutable-input rules above.
