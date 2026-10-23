"""Streaming verification using the existing artifact_hashes_v1 convention."""

import hashlib
import json
from pathlib import Path
import shutil

from ..ingestion.storage import digest, encode


def file_digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


class Writer:
    """An interrupted directory is deliberately unsealed and cannot be loaded/reused."""

    def __init__(self, directory):
        self.path = Path(directory)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.mkdir(exist_ok=False)
        self.files = {}

    def _target(self, name):
        if Path(name).name != name or name in {"hashes.json", "", ".", ".."} or name in self.files:
            raise ValueError("unsafe or duplicate bundle member")
        return self.path / name

    def put(self, name, content):
        with self._target(name).open("xb") as stream:
            stream.write(content)
        self.files[name] = digest(content)

    def copy(self, name, path):
        target = self._target(name)
        with Path(path).open("rb") as source, target.open("xb") as dest:
            shutil.copyfileobj(source, dest, 1024 * 1024)
        self.files[name] = file_digest(target)

    def finish(self):
        hashes = dict(sorted(self.files.items()))
        meta = {"schema_version": "artifact_hashes_v1", "algorithm": "sha256", "files": hashes,
                "bundle_sha256": digest(encode(hashes))}
        with (self.path / "hashes.json").open("xb") as stream:
            stream.write(encode(meta))
        return meta


def verify(directory):
    directory = Path(directory)
    if directory.is_symlink():
        raise ValueError("bundle directory must not be a symlink")
    meta = json.loads((directory / "hashes.json").read_bytes())
    hashes = meta["files"]
    if (meta.get("schema_version") != "artifact_hashes_v1" or meta.get("algorithm") != "sha256"
            or digest(encode(hashes)) != meta.get("bundle_sha256")):
        raise ValueError("invalid bundle hash/schema")
    if set(p.name for p in directory.iterdir()) != set(hashes) | {"hashes.json"}:
        raise ValueError("missing or unrecorded bundle member")
    for name, expected in hashes.items():
        p = directory / name
        if Path(name).name != name or p.is_symlink() or not p.is_file() or file_digest(p) != expected:
            raise ValueError(f"bundle content hash mismatch: {name}")
    return meta
