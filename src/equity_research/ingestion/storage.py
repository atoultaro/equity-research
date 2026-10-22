"""Small immutable bundles and byte-level integrity; no optional dependencies."""

import hashlib
import json
from pathlib import Path


def encode(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def seal(directory: Path, files: dict[str, bytes]) -> dict:
    """Write into an already exclusively claimed, empty directory, then commit hashes."""
    for name, content in files.items():
        if Path(name).name != name or name == "hashes.json":
            raise ValueError("bundle requires safe flat filenames")
        with (directory / name).open("xb") as handle:
            handle.write(content)
    hashes = {name: digest(content) for name, content in sorted(files.items())}
    record = {"schema_version": "artifact_hashes_v1", "algorithm": "sha256", "files": hashes,
              "bundle_sha256": digest(encode(hashes))}
    with (directory / "hashes.json").open("xb") as handle:
        handle.write(encode(record))
    return record


def write_bundle(directory: Path, files: dict[str, bytes]) -> dict:
    directory = Path(directory)
    directory.parent.mkdir(parents=True, exist_ok=True)
    directory.mkdir(exist_ok=False)
    return seal(directory, files)


def read_bundle(directory: Path) -> tuple[dict[str, bytes], dict]:
    directory = Path(directory)
    meta = json.loads((directory / "hashes.json").read_bytes())
    hashes = meta["files"]
    if (meta.get("schema_version") != "artifact_hashes_v1" or meta.get("algorithm") != "sha256"
            or meta.get("bundle_sha256") != digest(encode(hashes))):
        raise ValueError("invalid bundle hash/schema")
    if set(p.name for p in directory.iterdir()) != set(hashes) | {"hashes.json"}:
        raise ValueError("bundle contains unrecorded or missing files")
    files = {}
    for name, expected in hashes.items():
        path = directory / name
        if Path(name).name != name or path.is_symlink() or not path.is_file():
            raise ValueError("invalid bundle member")
        content = path.read_bytes()
        if digest(content) != expected:
            raise ValueError(f"content hash mismatch: {name}")
        files[name] = content
    return files, meta
