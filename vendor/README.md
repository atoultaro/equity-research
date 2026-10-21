# Pinned shared indicator artifact

`market_shared-0.2.0-py3-none-any.whl` is built from the existing private repository
https://github.com/atoultaro/finwhaling at full Git revision
`57fc6c30836d13a7fcfc3c1a9b6b496fe472d555`, subdirectory `packages/market_shared`.
That revision is included in merged main `98034e009ac2c062e5a23aad1ba1cf56f2c94001`.
No upstream source or production code was changed for this repository.

The committed small wheel is the installation source; no PyPI availability is
assumed. `requirements-shared.txt` enforces its SHA256. `SHARED_SOURCE.json` records
the source/filename/hash, and the runtime independently verifies the installed
indicator-module content against `_shared_pin.py`. Version alone is insufficient.
No optional plotting or third-party library is required by this artifact.

Build provenance: exported the above commit's `packages/market_shared` tree with
`git archive`, then ran Python3.12.9/setuptools81.0.0:

```bash
python -m pip wheel --no-index --no-deps --no-build-isolation \
  --wheel-dir vendor /path/to/exported/packages/market_shared
python -m pip hash vendor/market_shared-0.2.0-py3-none-any.whl
```

Rebuilding at a different time may alter ZIP timestamps/wheel bytes. The committed
wheel and its hash, plus source commit and installed indicator content hash, are
the reproducible installation contract. Do not regenerate/update it without a
separate dependency review. No finwhaling source checkout is needed at runtime.
