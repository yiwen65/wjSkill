#!/usr/bin/env python3
"""Locate the user's Obsidian wiki vault on macOS or Linux."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


MACOS_VAULT = Path("/Users/w/Library/Mobile Documents/iCloud~md~obsidian/Documents/wiki")
LINUX_VAULT = Path("/home/w/Documents/Obsidian")
REQUIRED_PATHS = (
    ".obsidian",
    "README.md",
    "_wiki/SCHEMA.md",
    "_meta/Agent Workflow.md",
)


class VaultDiscoveryError(RuntimeError):
    """Raised when the target vault cannot be resolved safely."""


@dataclass(frozen=True)
class Match:
    path: str
    source: str


def is_vault(path: Path) -> bool:
    return path.is_dir() and all((path / marker).exists() for marker in REQUIRED_PATHS)


def normalize(path: str | Path, base: Path | None = None) -> Path:
    value = Path(os.path.expandvars(str(path))).expanduser()
    if not value.is_absolute() and base is not None:
        value = base / value
    return value.resolve()


def ancestor_vault(start: Path) -> Path | None:
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if is_vault(candidate):
            return candidate
    return None


def platform_vault(platform_name: str | None = None) -> Path:
    platform_name = platform_name or sys.platform
    if platform_name == "darwin":
        return MACOS_VAULT
    if platform_name.startswith("linux"):
        return LINUX_VAULT
    raise VaultDiscoveryError(f"unsupported platform: {platform_name}")


def discover_vault(
    explicit: str | Path | None = None,
    start: str | Path | None = None,
) -> Match:
    if explicit is not None:
        candidate = normalize(explicit, Path.cwd())
        source = "explicit"
    elif env_path := os.environ.get("OBSIDIAN_VAULT_PATH"):
        candidate = normalize(env_path, Path.cwd())
        source = "OBSIDIAN_VAULT_PATH"
    elif found := ancestor_vault(normalize(start or Path.cwd(), Path.cwd())):
        return Match(str(found), "workspace-ancestor")
    else:
        candidate = platform_vault().resolve()
        source = "platform-default"

    if not is_vault(candidate):
        raise VaultDiscoveryError(f"{source} does not identify this wiki vault: {candidate}")
    return Match(str(candidate), source)


def find_vault(explicit: str | Path | None = None, start: str | Path | None = None) -> Path:
    return Path(discover_vault(explicit=explicit, start=start).path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", help="Explicit vault path; validated before use")
    parser.add_argument("--start", help="Workspace path whose ancestors should be inspected")
    parser.add_argument("--json", action="store_true", help="Include discovery source as JSON")
    args = parser.parse_args()
    try:
        match = discover_vault(args.vault, args.start)
    except VaultDiscoveryError as exc:
        parser.error(str(exc))
    print(json.dumps(asdict(match), ensure_ascii=False) if args.json else match.path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
