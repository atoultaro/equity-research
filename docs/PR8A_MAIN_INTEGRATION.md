# PR #12 integration and regression verification

This amendment updates the existing PR8A branch against current `main`. It adds
no research feature and changes no historical-universe selection policy.

## Inspected revisions and conflict resolution

| Revision | Exact commit |
|---|---|
| Previous PR #12 head | `733bf7e9ab67115183fe58b0d2e0f3b48468c954` |
| Latest inspected `origin/main`, including merged PR #17 and PR #16 | `6ead08793a41edd78513749c49032a04fdd69ae2` |
| Tested integration merge | `156b9a99c1746f4dc2558368c907298fc7904818` |

The merge retains both parents without rebasing or rewriting PR history. The
only conflict was in `src/equity_research/cli.py`: both branches added command
registration and dispatch at the same location. The resolution keeps `universe`
alongside `expert`, `lifecycle`, `management`, `outcomes`, `swing`, `data` and `run`.
Relative to current main, the CLI change is exactly the five lines registering
and dispatching `universe`. README additions merged automatically and retain the
existing Grimes documentation.

All **259 other files already on main** were independently compared against
their committed bytes and are unchanged. PR8A's complete universe package,
`tests/test_universe.py` and original pilot runner are unchanged from the previous
PR head. In particular, the bitemporal security master, stable identities,
60-session liquidity ranking, publication cutoffs, membership activation and
expiry rules, exclusion/quality classifications and semantic-load safeguard are
preserved. Semantic validation still recomputes once on load; member queries
reuse the validated inventory.

The previously committed isolated framework evaluation remains unchanged on this
branch. This amendment does not run either external engine, change its adapters
or add dependencies.

## Full regression

Command: `.venv/bin/python -m pytest -q`

**620 passed in 272.86s (0:04:32)**, exit 0, no skips or failures. This includes
all 533 regressions from current main, all 80 universe cases (including resealed
semantic-output mutations and once-per-load validation), and the seven existing
isolated framework transport tests. Test sockets are blocked by the existing
autouse fixture. No brokerage connection is required. CLI help checks retain
every command family. `git diff --check` also passes.

See [exact test output](evidence/pr8a-main-integration-v1/pytest.txt) and
[source preservation checks](evidence/pr8a-main-integration-v1/source_preservation.json).

## Synthetic pilot and replay

The unchanged pilot runner was rerun in fresh processes and new directories for
all three original cases. Every generated source-capture hash, master hash,
panel hash, universe hash and available integration hash matches its original
frozen case. Selection summaries and membership changes also match exactly.

In addition, each universe was independently rebuilt using its **original frozen
master and panel**, original definition, selection months and decision clocks.
The rebuilt files and seals are byte-identical to the original universes. Both
original and replayed universes pass the semantic loader, and queries at every
snapshot's activation date agree.

| Case | Daily rows | Snapshots | Members per snapshot | Unchanged universe SHA256 |
|---|---:|---:|---|---|
| Pilot | 67,249 | 10 | 50 | `a1cfec4dc56f68fb2052d9277feb1fcd4ccad42f78edb360c3b25fbfccf6900e` |
| Scale 100 | 12,400 | 2 | 100 | `66c983bf0029aad5fbb32024aef257f5ef9f1d36e2214ab2f57f5ad86beb1a24` |
| Scale 1,000 | 124,000 | 2 | 1,000 | `3d7b6c00e1b0a152f5fb1866fa3210d3cf56e83c8e4505ca2ec45799ecb839f3` |

The pilot's existing swing/outcome integration also retains SHA256
`e95ebacf441515cd808f6b78889e4c83506fffda20251802e759b86272149394`:
five illustrative signals, nine first-signal path rows, unavailable context and
strict execution `NOT_ADMITTED`. These remain synthetic engineering observations.

The [validation inventory](evidence/pr8a-main-integration-v1/universe_validation.json)
records all dependency hashes and comparisons. Fresh report bytes and their
seals are retained in the same evidence directory. Timings are incidental to
this integration run, which overlapped regression and preservation work; they
are not new performance benchmarks. Arrow emitted the retained sandbox sysctl
warnings while continuing successfully.

## Merged trade research remains unchanged

The resolved CLI dispatched actual offline `lifecycle replay` and `management
replay` commands against their existing frozen studies. Their unchanged loaders
recomputed semantic outputs before writing fresh replay directories. Both the
files and complete seals match their originals:

| Research | Files excluding seal | Original and replay SHA256 |
|---|---:|---|
| PR #16 lifecycle `study-v5` | 67 | `4ce1b1f021d666bb870983cf894628c665992f97186e6e2740ccd2f4e69b2604` |
| PR #17 management `study-v2` | 112 | `fb2fd81dc3eeef6b10a185057930776a1534230a3534d63793d72d3e257342ca` |

Their implementation, source facts, modeled results, publication uncertainty,
reports and embedded inputs therefore remain unchanged. See
[replay evidence](evidence/pr8a-main-integration-v1/lifecycle_replay.json).
Network sockets were explicitly denied in both replay verification and the
synthetic validation harness, including its pilot subprocesses.

## Preservation, reproduction and limits

All **65,347 pre-existing files** under `runs/` and `data/` retain their original
SHA256 values; none is missing. The before-inventory SHA256 is
`e1cff81e57c1a02e2c077a21e5cc94030b550a5ae9d562861e93e882fa847842`.
The full inventory is retained locally at
`runs/pr12-integration-20261027-v1/preservation-before.json`; the committed
[preservation summary](evidence/pr8a-main-integration-v1/preservation.json)
records its scope. Existing committed evidence bundles were also left unchanged.
All new research verification artifacts use the new
`runs/pr12-integration-20261027-v1/` directory.

To reproduce the synthetic checks, retain the original three fixture directories
listed in [the original pilot record](PR8A_PILOT_EVIDENCE.md), use the project's
existing pinned environment and a clean checkout, then run:

```sh
PYTHONPATH=src .venv/bin/python docs/evidence/pr8a-main-integration-v1/validate.py --output NEW_UNUSED_DIRECTORY
.venv/bin/python -m pytest -q
```

The validation script exclusively creates its output directory. It runs the
existing deterministic fixture runner, verifies the original frozen dependencies,
rebuilds their universes and checks hashes and queries. It is a verification
harness, not an acquisition path or new research interface. Reproduce the Grimes
checks with `lifecycle replay` and `management replay`, using the original study
paths above and a separate unused output directory for each command.

Local frozen studies are not distributed in Git; reproducing their actual-data
replays requires those existing local inputs. All automated tests remain offline
and self-contained. No real historical-universe coverage, licensed source access,
PIT verification of synthetic observations or trading edge is established.
No broker/vendor request, account operation, execution-policy change, frozen
artifact migration, new vendor or infrastructure expansion occurred. PR #12
remains a draft for review; it must not be merged automatically.
