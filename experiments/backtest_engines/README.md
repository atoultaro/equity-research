# Isolated LEAN / NautilusTrader evaluation

Authoritative task: Framework Evaluation Spike, October 23, 2026. This experiment
branches from reviewed PR8A fix `2b6ffa0daf2becdb5d2616d2bb1e82a3bb134f5c`.
Core PR4/7B/7C/8A code and original frozen inputs are read-only. Everything here
is experimental; no strategy edge or execution admission is implied.

Use the project's existing `.venv` only to read/validate artifacts and orchestrate
child processes. Framework packages belong to separate venvs; .NET and NuGet have
an experiment-local installation/cache. Do not install either framework into the
core environment. Network is needed for software setup; backtests below deny it.
No account, subscription, broker application or cloud backtest is used.

## Pinned setup used on this Mac

NautilusTrader **stable 1.231.0**, Python **3.13.3**, macOS **26.6.2 arm64**.
The website's latest documentation currently describes **2.x release candidates**;
those APIs are not used. `requirements-nautilus.txt` pins the actual installed
stable stack, including PyArrow 26.0.0; core research retains PyArrow 23.0.1.

```sh
/opt/homebrew/bin/python3.13 -m venv runs/backtest-engine-spike-v1/nt-env
runs/backtest-engine-spike-v1/nt-env/bin/python -m pip install -r experiments/backtest_engines/requirements-nautilus.txt
```

LEAN source **f3d841e60dfd010ee5fc293ea893e56952484108**, engine assembly
**2.5.0.0**, .NET SDK **10.0.402**, QuantConnect.pythonnet **2.0.66**, Python
**3.11.6**. Python 3.12.9 was also tried as a diagnostic. Both Python runtimes
completed computational backtests but exposed the same GIL finalizer abort during
launcher shutdown. Do not mistake a result file for a clean process exit.
No engine or Pythonnet sources were patched to suppress this failure.

```sh
git clone https://github.com/QuantConnect/Lean.git runs/backtest-engine-spike-v1/toolchain/Lean
git -C runs/backtest-engine-spike-v1/toolchain/Lean checkout f3d841e60dfd010ee5fc293ea893e56952484108
curl -fLsS https://dot.net/v1/dotnet-install.sh -o runs/backtest-engine-spike-v1/toolchain/dotnet-install.sh
# Inspect the official installer. The evaluated script's SHA256 is recorded in the environment evidence.
bash runs/backtest-engine-spike-v1/toolchain/dotnet-install.sh --version 10.0.402 --install-dir "$PWD/runs/backtest-engine-spike-v1/toolchain/dotnet" --no-path
DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_CLI_HOME="$PWD/runs/backtest-engine-spike-v1/toolchain/dotnet-home" NUGET_PACKAGES="$PWD/runs/backtest-engine-spike-v1/toolchain/nuget" runs/backtest-engine-spike-v1/toolchain/dotnet/dotnet build runs/backtest-engine-spike-v1/toolchain/Lean/Launcher/QuantConnect.Lean.Launcher.csproj -c Release
/Library/Frameworks/Python.framework/Versions/3.11/bin/python3.11 -m venv runs/backtest-engine-spike-v1/lean-python-env
runs/backtest-engine-spike-v1/lean-python-env/bin/python -m pip install -r experiments/backtest_engines/requirements-lean-python.txt
```

The runner defaults to the evaluated framework Python dylib. Other machines must
set `SPIKE_PYDLL` to their matching runtime. No shell profile is modified. The
source build directly invokes the open-source launcher, bypassing the separately
licensed/operated LEAN CLI and hosted platform. Docker Desktop is installed but
its daemon is unavailable here; it was not started or used. Upstream package audit
warnings remain recorded; this is not a production dependency recommendation.

## Immutable shared inputs

The existing generated PR8A artifacts may be supplied directly. In a fresh clone,
first reproduce them with `scripts/pilot_historical_universe.py`, using **new**
output paths; see the PR8A guide and pinned core dependencies. Then:

```sh
PYTHONPATH=src:. .venv/bin/python -m experiments.backtest_engines.common \
  --pilot-root data/research_datasets/pr8a-pilot-8xc4tbfk-v1 \
  --universe-root data/research_datasets/pr8a-scale1000-8xc4tbfk-v1 \
  --output NEW_INPUT_BUNDLE
```

`cases.json` contains the unchanged PR4 source history plus named post-signal
variations, its native reference results, common precommitted intents and one
original frozen PR7B signal. `portfolio.json` captures PR8A's validated 1,000-ID
panel/membership plus source hashes. `compatibility.json` adds an explicitly
synthetic controlled split/dividend/rename/delisting/missing/halt scenario using
PR8A's calendar and contracts. It does not claim that those invented controls
are original provider observations. Original data, master, signals and outcomes
are never rewritten. Every child verifies bundle bytes before using them.

The common order quantity uses risk budget / (planned trigger + slippage - stop)
before the next unknown Open. PR4 retains its native actual-fill sizing, so gap
quantities can differ. Engine targets use actual entry risk. Native stop/limit
fills are never overridden. Common-cost configuration and engine-default cost
sensitivity runs are separate. LEAN's callback cancellation is not atomic OCO;
the ambiguous-bar control exposes a reverse position in this prototype. Failed
or incomplete paths must not be summarized as valid one-trade P&L/R.

## Run the actual frameworks

Inspect `--help` first. Substitute unused output directories for each run.

```sh
PYTHONPATH=. .venv/bin/python -m experiments.backtest_engines.run_evaluation \
  --inputs NEW_INPUT_BUNDLE --output NEW_CASE_RUNS \
  --toolchain runs/backtest-engine-spike-v1/toolchain \
  --nt-python runs/backtest-engine-spike-v1/nt-env/bin/python \
  --lean-python-env runs/backtest-engine-spike-v1/lean-python-env \
  --part cases --deny-network
```

Repeat with `--part compatibility` and `--part scale`, each into a new directory.
Scale mode runs fresh sequential subprocesses for 10/100/1,000 selected stocks,
two repetitions each, with orders and paired feed-only controls. It intentionally
continues after a failed launcher to retain raw diagnostics; `run-index.json`
records each return code and distinguishes failed processes with/without results.
The final index is not an assertion that every child succeeded.

`--deny-network` uses macOS `sandbox-exec` with `(deny network*)`. A restricted
parent sandbox may require running the orchestrator outside that parent so it can
apply the stricter child profile. Other operating systems require their own
network-isolation mechanism; they were not evaluated. Use a venv executable's
absolute path without resolving its symlink to the base interpreter.

The comparative analysis and results are in `docs/BACKTEST_ENGINE_EVALUATION.md`.
Raw execution results, costs, repetitions, environment manifests and hashes are
published with the report. This is an evaluation adapter, not a production engine
migration or an alteration of PR7C signal-outcome analysis.

## Additional identity probe and publication

The identity probe projects the actual PR8A pilot master at three historical
cutoffs, separately from the invented lifecycle control. Use unused paths:

```sh
PYTHONPATH=src:. .venv/bin/python -m experiments.backtest_engines.identity_probe \
  --master data/research_datasets/pr8a-pilot-8xc4tbfk-v1/security_master \
  --output NEW_IDENTITY_INPUTS
/usr/bin/sandbox-exec -p '(version 1)(allow default)(deny network*)' \
  runs/backtest-engine-spike-v1/nt-env/bin/python -m experiments.backtest_engines.identity_probe \
  --inputs NEW_IDENTITY_INPUTS --output NEW_NT_IDENTITY_RESULT.json
```

For LEAN, reuse the **configuration and synthetic BANCH input files** produced by
the compatibility run; change only the algorithm and output paths. This is the
zero-order identity control used to isolate the shutdown failure:

```python
# Execute with core Python from the repository root, after the compatibility run.
import json, os, pathlib, subprocess
root = pathlib.Path.cwd()
work = root / 'NEW_LEAN_IDENTITY_RUN'
work.mkdir(exist_ok=False)
config = json.loads((root / 'NEW_COMPATIBILITY_RUNS/lean-compatibility/config.json').read_text())
config.update({
    'algorithm-type-name': 'SpikeIdentity',
    'algorithm-location': str(root / 'experiments/backtest_engines/lean_identity_algorithm.py'),
    'results-destination-folder': str(work / 'native-results'),
    'object-store-root': str(work / 'object-store'),
})
(work / 'config.json').write_text(json.dumps(config))
toolchain = root / 'runs/backtest-engine-spike-v1/toolchain'
binary = toolchain / 'Lean/Launcher/bin/Release/QuantConnect.Lean.Launcher.dll'
env = dict(os.environ, SPIKE_CODE_ROOT=str(root),
           SPIKE_IDENTITY_INPUTS=str(root / 'NEW_IDENTITY_INPUTS'),
           SPIKE_OUTPUT=str(work / 'result.json'), DOTNET_CLI_TELEMETRY_OPTOUT='1',
           PYTHONNET_PYDLL='/Library/Frameworks/Python.framework/Versions/3.11/lib/libpython3.11.dylib')
with (work / 'launcher.log').open('x') as log:
    run = subprocess.run(['/usr/bin/sandbox-exec', '-p', '(version 1)(allow default)(deny network*)',
        str(toolchain / 'dotnet/dotnet'), str(binary), '--config', str(work / 'config.json')],
        env=env, cwd=binary.parent, stdout=log, stderr=subprocess.STDOUT, timeout=120)
(work / 'process.json').write_text(json.dumps({'returncode': run.returncode,
                                            'network_denied': True, 'orders': 0}))
```

An output file does not override that process return code. These probes test
native identifiers; they do not claim trading across a venue transfer or reused
ticker has been validated.

`publish.py --help` describes freezing all three main run groups. The publisher
used for the checked-in evidence also expects the recorded toolchain installation
reports, original preservation inventory, core-regression log and identity results
under the evaluated run root. It is an audit of that recorded run layout, rather
than an installer. Analysis can be inspected directly in `analyze.py`; no native
engine is imported by the core offline tests. Never regenerate the committed
evidence in place; use a new version and report its new hash.
