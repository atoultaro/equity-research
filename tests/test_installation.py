"""Clean-runtime installation and CLI verification; all pip commands are offline."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def test_clean_venv_install_runs_offline_example_without_monorepo_or_optional_libraries(tmp_path):
    root = Path(__file__).resolve().parents[1]
    source = tmp_path / "build-source"
    source.mkdir()
    shutil.copy2(root / "pyproject.toml", source)
    shutil.copytree(root / "src", source / "src", ignore=shutil.ignore_patterns("__pycache__", "*.egg-info"))
    env = dict(os.environ, PIP_NO_CACHE_DIR="1", PIP_DISABLE_PIP_VERSION_CHECK="1")
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)

    def run(*args):
        result = subprocess.run(args, cwd=tmp_path, env=env, text=True, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=60)
        assert result.returncode == 0, result.stdout
        return result.stdout

    run(sys.executable, "-m", "pip", "wheel", "--no-index", "--no-deps", "--no-build-isolation",
        "--wheel-dir", str(tmp_path / "wheels"), str(source))
    run(sys.executable, "-m", "venv", str(tmp_path / "clean"))
    python = str(tmp_path / "clean/bin/python")
    wheel, = (tmp_path / "wheels").glob("equity_research-*.whl")
    pin = json.loads((root / "vendor/SHARED_SOURCE.json").read_text())
    run(python, "-I", "-m", "pip", "install", "--no-index", "--no-deps", str(root / "vendor" / pin["wheel"]), str(wheel))
    run(python, "-I", "-c", """
import importlib.util
from equity_research.reporting import shared_identity
assert shared_identity()['version'] == '0.2.0'
for name in ('finwhaling', 'ibkr_data', 'numpy', 'pandas', 'ib_async', 'matplotlib', 'gymnasium'):
    assert importlib.util.find_spec(name) is None, name
""")
    fixture = root / "tests/fixtures"
    for name in ("one", "two"):
        run(str(tmp_path / "clean/bin/equity-research"), "run", "--data", str(fixture / "synthetic_daily.csv"),
            "--candidate", str(fixture / "candidate.json"), "--config", str(fixture / "swing_config.json"),
            "--manifest", str(fixture / "data_manifest.json"), "--output", str(tmp_path / name),
            "--source-commit", "b" * 40)
    first = json.loads((tmp_path / "one/result.json").read_text())
    assert first["status"] == "COMPLETED"
    assert first["trade"]["net_pnl_dollars"] == "194.000"
    assert (tmp_path / "one/artifact_hashes.json").read_bytes() == (tmp_path / "two/artifact_hashes.json").read_bytes()
