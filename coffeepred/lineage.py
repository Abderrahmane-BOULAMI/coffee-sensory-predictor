"""Run manifest: what data, code and settings produced a set of results."""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

PACKAGES = ["numpy", "pandas", "scipy", "scikit-learn", "lightgbm", "matplotlib"]


def sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _git_commit() -> str | None:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5,
                             cwd=Path(__file__).resolve().parent)
        return out.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def manifest(data_path: str | Path, config: dict, steps: list[dict]) -> dict:
    versions = {}
    for p in PACKAGES:
        try:
            versions[p] = version(p)
        except PackageNotFoundError:
            versions[p] = None
    return {
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "data_file": Path(data_path).name,
        "data_sha256": sha256(data_path),
        "git_commit": _git_commit(),
        "python": platform.python_version(),
        "packages": versions,
        "config": config,
        "cleaning_steps": steps,
    }


def write(m: dict, path: str | Path) -> None:
    Path(path).write_text(json.dumps(m, indent=2, default=str))
