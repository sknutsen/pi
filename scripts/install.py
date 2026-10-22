#!/usr/bin/env python3
"""Install this Pi user-config repo into the live agent directory."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HOME = Path.home()
AUTH_NAMES = {"auth.json"}
MANAGED_FILES = (
    "settings.json",
    "keybindings.json",
    "mcp.json",
    "models.json",
    "APPEND_SYSTEM.md",
    "AGENTS.md",
)
MANAGED_DIRS = (
    "extensions",
    "prompts",
    "themes",
)
MANAGED = MANAGED_FILES + MANAGED_DIRS


def resolve_repo(explicit: str | None) -> Path:
    raw = explicit or os.environ.get("PI_CONFIG_REPO")
    if raw:
        return Path(raw).expanduser().resolve()
    return Path(__file__).resolve().parent.parent


def set_repo(path: Path) -> None:
    global REPO
    if not (path / "settings.json").is_file() or not (path / "scripts" / "install.py").is_file():
        raise SystemExit(
            f"Not a Pi user-config checkout: {path}\n"
            "Run from a clone of this repo, pass --repo, or set PI_CONFIG_REPO."
        )
    REPO = path


def agent_dir() -> Path:
    override = os.environ.get("PI_CODING_AGENT_DIR")
    if override:
        return Path(override).expanduser()
    return HOME / ".pi" / "agent"


def state_path(dest_root: Path) -> Path:
    return dest_root.parent / "pi-config-install-state.json"


def load_state(dest_root: Path) -> dict:
    path = state_path(dest_root)
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"managed_copies": {}}
        if isinstance(data, dict):
            data.setdefault("managed_copies", {})
            return data
    return {"managed_copies": {}}


def save_state(dest_root: Path, state: dict) -> None:
    path = state_path(dest_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def mark_managed_copy(dest_root: Path, dest: Path) -> None:
    state = load_state(dest_root)
    state["managed_copies"][str(dest.resolve())] = {"kind": "copy"}
    save_state(dest_root, state)


def unmark_managed_copy(dest_root: Path, dest: Path) -> None:
    state = load_state(dest_root)
    try:
        key = str(dest.resolve())
    except OSError:
        key = str(dest)
    state["managed_copies"].pop(key, None)
    save_state(dest_root, state)


def is_managed_copy(dest_root: Path, dest: Path) -> bool:
    try:
        key = str(dest.resolve())
    except OSError:
        key = str(dest)
    return key in load_state(dest_root).get("managed_copies", {})


def expected_src(name: str) -> Path:
    return (REPO / name).resolve()


def points_at_repo(dest: Path, name: str) -> bool:
    if not dest.exists() and not dest.is_symlink():
        return False
    try:
        return dest.resolve() == expected_src(name)
    except OSError:
        return False


def is_owned(dest_root: Path, dest: Path, name: str) -> bool:
    if dest.is_symlink() or dest.exists():
        if points_at_repo(dest, name):
            return True
    return dest.exists() and not dest.is_symlink() and dest.is_file() and is_managed_copy(
        dest_root, dest
    )


def exists(dest: Path) -> bool:
    return dest.exists() or dest.is_symlink()


def remove_dest(dest_root: Path, dest: Path) -> None:
    if dest.name in AUTH_NAMES:
        raise SystemExit(f"Refusing to touch {dest}")
    if dest.is_symlink():
        dest.unlink()
        return
    if dest.is_file():
        dest.unlink()
        unmark_managed_copy(dest_root, dest)
        return
    if dest.is_dir():
        if os.name == "nt":
            dest.rmdir()
            return
        if not any(dest.iterdir()):
            dest.rmdir()
            return
        raise SystemExit(f"Refusing to replace non-empty directory: {dest}")
    if dest.exists():
        raise SystemExit(f"Refusing to replace: {dest}")


def link_path(dest_root: Path, src: Path, dest: Path, name: str) -> str:
    if dest.name in AUTH_NAMES or name in AUTH_NAMES:
        raise SystemExit(f"Refusing to touch {dest}")
    src = src.resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)
    if exists(dest):
        if is_owned(dest_root, dest, name) or (
            dest.is_dir() and not dest.is_symlink() and not any(dest.iterdir())
        ):
            remove_dest(dest_root, dest)
        else:
            return "skip"
    if os.name == "nt":
        if src.is_dir():
            subprocess.check_call(["cmd", "/c", "mklink", "/J", str(dest), str(src)])
        else:
            try:
                dest.symlink_to(src)
            except OSError:
                shutil.copy2(src, dest)
                mark_managed_copy(dest_root, dest)
                print(f"copied {dest} (Windows file symlink unavailable)")
                return "copy"
    else:
        dest.symlink_to(src, target_is_directory=src.is_dir())
    print(f"linked {dest} -> {src}")
    return "link"


def skip_message(dest: Path, name: str) -> str:
    kind = "directory" if dest.is_dir() and not dest.is_symlink() else "file"
    target = ""
    if dest.is_symlink():
        try:
            target = f" -> {dest.readlink()}"
        except OSError:
            target = " (broken symlink)"
    return (
        f"SKIP {dest}{target} (existing {kind} is not a link to this repo's {name}). "
        "Merge by hand, then re-run. Never copy auth.json into git."
    )


def install() -> int:
    dest_root = agent_dir()
    skipped: list[str] = []
    dest_root.mkdir(parents=True, exist_ok=True)
    print(f"repo: {REPO}")
    print(f"agent dir: {dest_root}")
    if os.environ.get("PI_CODING_AGENT_DIR"):
        print("using PI_CODING_AGENT_DIR")
    for name in MANAGED:
        src = REPO / name
        dest = dest_root / name
        if not src.exists():
            print(f"missing source {src}", file=sys.stderr)
            return 1
        result = link_path(dest_root, src, dest, name)
        if result == "skip":
            msg = skip_message(dest, name)
            skipped.append(msg)
            print(msg)
    print()
    if skipped:
        print("Merge plan: left foreign files in place. Inspect the SKIP lines above.")
        print("This installer owns only:")
        for name in MANAGED:
            print(f"  {name}")
        print("It never writes, overwrites, or deletes auth.json.")
        print()
    print("Install complete for managed paths.")
    print("Restart Pi, or run /reload in an existing session.")
    return 1 if skipped else 0


def uninstall() -> int:
    dest_root = agent_dir()
    for name in MANAGED:
        dest = dest_root / name
        if dest.name in AUTH_NAMES:
            print(f"skip {dest} (never touch auth.json)")
            continue
        if exists(dest):
            if is_owned(dest_root, dest, name):
                remove_dest(dest_root, dest)
                print(f"removed {dest}")
            else:
                print(f"skip {dest} (not a link from this repo)")
    print("uninstall complete")
    print("Left auth.json, sessions, and any foreign files in place.")
    return 0


def describe(dest_root: Path, dest: Path, name: str) -> tuple[str, bool]:
    if dest.name in AUTH_NAMES:
        if exists(dest):
            return f"OK  {dest} present (unmanaged, never touched)", True
        return f"--  {dest} absent (created by Pi /login, not this repo)", True
    if dest.is_symlink():
        try:
            target = dest.readlink()
        except OSError:
            return f"??  {dest} broken symlink", False
        if points_at_repo(dest, name):
            return f"OK  {dest} -> {target}", True
        return f"??  {dest} -> {target} (not this repo)", False
    if dest.exists() and dest.is_file() and is_managed_copy(dest_root, dest):
        return f"OK  {dest} (managed copy)", True
    if dest.exists() and points_at_repo(dest, name):
        return f"OK  {dest} -> {dest.resolve()}", True
    if exists(dest):
        return f"??  {dest} exists (foreign; not replaced)", False
    return f"NO  {dest} missing", False


def status() -> int:
    dest_root = agent_dir()
    print(f"repo: {REPO}")
    print(f"home: {HOME}")
    print(f"agent dir: {dest_root}")
    if os.environ.get("PI_CODING_AGENT_DIR"):
        print("using PI_CODING_AGENT_DIR")
    print()
    healthy = True
    if not dest_root.exists():
        print(f"NO  {dest_root} missing")
        healthy = False
    for name in MANAGED:
        dest = dest_root / name
        line, ok = describe(dest_root, dest, name)
        print(line)
        if not ok:
            healthy = False
    auth = dest_root / "auth.json"
    line, _ok = describe(dest_root, auth, "auth.json")
    print(line)
    skills = HOME / ".agents" / "skills"
    if skills.exists() or skills.is_symlink():
        try:
            print(f"OK  {skills} -> {skills.resolve()}")
        except OSError:
            print(f"??  {skills} (unreadable)")
    else:
        print(f"--  {skills} missing (install agent-kit with agents_compat)")
    return 0 if healthy else 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo",
        help="Checkout of this config repo (default: this script's parent, or PI_CONFIG_REPO)",
    )
    parser.add_argument("--uninstall", action="store_true")
    parser.add_argument("--status", action="store_true")
    args = parser.parse_args()
    set_repo(resolve_repo(args.repo))
    if args.status:
        raise SystemExit(status())
    if args.uninstall:
        raise SystemExit(uninstall())
    raise SystemExit(install())


if __name__ == "__main__":
    main()
