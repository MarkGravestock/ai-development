#!/usr/bin/env python3
"""Install skills from this repo to Claude Code, Tabnine and opencode locations.

Every directory under skills/ containing a SKILL.md is installed under the
name given by that file's `name:` frontmatter field (e.g. skills/design/cupid/
python/ installs as cupid-python) — no per-family list of skill names to keep
in sync with the frontmatter.

A few skills also need a small canonical file copied in alongside their
SKILL.md, because an installed skill only ever sees its own directory — see
COMPANION_FILES below.

Usage:
    uv run poe sync                    # copy every skill (default)
    uv run poe sync-link               # symlink every skill instead

    python tooling/sync.py [copy|link] [SUBDIR]

    SUBDIR narrows the install to one topic or skill, relative to skills/:
        python tooling/sync.py copy design
        python tooling/sync.py link design/cupid
        python tooling/sync.py design/cupid       # mode defaults to copy

Overridable via env: CLAUDE_SKILLS_DIR, TABNINE_SKILLS_DIR, OPENCODE_SKILLS_DIR,
NOTES_ROOT
"""

from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = REPO_ROOT / "skills"
NOTES_DIR = SKILLS_ROOT / "writing" / "notes"
NAME_RE = re.compile(r"^name:\s*(\S+)\s*$", re.MULTILINE)

# (canonical file, directories that need a copy of it, name to copy it as).
# Composition metadata belongs with the skills that need it, but an installed
# skill can only see its own directory, so the canonical doc gets duplicated
# in at sync time rather than referenced.
COMPANION_FILES = [
    (
        SKILLS_ROOT / "design/cupid/properties/SKILL.md",
        [SKILLS_ROOT / "design/cupid/python", SKILLS_ROOT / "design/cupid/java-spring-boot"],
        "cupid-properties.md",
    ),
    (
        SKILLS_ROOT / "writing/notes/references/writing-style.md",
        [
            SKILLS_ROOT / "writing/notes/session-wrap",
            SKILLS_ROOT / "writing/notes/notes-lint",
            SKILLS_ROOT / "writing/notes/ingest",
        ],
        "writing-style.md",
    ),
    (
        REPO_ROOT / "practices/growing-guardrails.md",
        [SKILLS_ROOT / "promote-to-guardrail"],
        "growing-guardrails.md",
    ),
]


def opencode_default() -> Path:
    # opencode reads its global config from XDG_CONFIG_HOME when that is set,
    # falling back to ~/.config, and scans {skill,skills}/**/SKILL.md under it.
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / "opencode" / "skills"


def targets() -> list[Path]:
    home = Path.home()
    return [
        Path(os.environ.get("CLAUDE_SKILLS_DIR", home / ".claude" / "skills")),
        Path(os.environ.get("TABNINE_SKILLS_DIR", home / ".tabnine" / "agent" / "skills")),
        Path(os.environ.get("OPENCODE_SKILLS_DIR", opencode_default())),
    ]


def remove(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def link(source: Path, dest: Path) -> None:
    if dest.is_symlink() or dest.exists():
        remove(dest)
    try:
        dest.symlink_to(source, target_is_directory=True)
    except OSError as exc:
        raise SystemExit(
            f"Could not create symlink at {dest}: {exc}\n"
            "On Windows, symlinks need Developer Mode enabled (Settings > "
            "Privacy & security > For developers) or an elevated shell."
        ) from exc


def skill_name(skill_md: Path) -> str:
    match = NAME_RE.search(skill_md.read_text(encoding="utf-8"))
    if not match:
        raise SystemExit(f"{skill_md}: no `name:` field in frontmatter")
    return match.group(1)


def discover_skills(root: Path) -> list[tuple[str, Path]]:
    return [(skill_name(md), md.parent) for md in sorted(root.rglob("SKILL.md"))]


def write_companions() -> None:
    for source, dest_dirs, filename in COMPANION_FILES:
        for dest_dir in dest_dirs:
            shutil.copy2(source, dest_dir / filename)


def sync_notes_tools() -> None:
    notes_root = Path(os.environ.get("NOTES_ROOT", Path.home() / "notes"))
    (notes_root / "tools").mkdir(parents=True, exist_ok=True)
    (notes_root / "raw").mkdir(parents=True, exist_ok=True)
    shutil.copy2(NOTES_DIR / "tools" / "notes_tools.py", notes_root / "tools" / "notes_tools.py")
    print(f"  copy  tools/notes_tools.py -> {notes_root / 'tools'}")


def install(mode: str, root: Path) -> None:
    write_companions()

    skills = discover_skills(root)
    if not skills:
        raise SystemExit(f"No SKILL.md found under {root}")

    for name, skill_dir in skills:
        for target in targets():
            target.mkdir(parents=True, exist_ok=True)
            dest = target / name
            if mode == "link":
                link(skill_dir, dest)
            else:
                if dest.exists():
                    remove(dest)
                shutil.copytree(skill_dir, dest)
            print(f"  {mode}  {name} -> {dest}")

    if NOTES_DIR.is_relative_to(root) or root.is_relative_to(NOTES_DIR):
        sync_notes_tools()


def resolve_root(subdir: str | None) -> Path:
    if not subdir:
        return SKILLS_ROOT
    parts = Path(subdir).parts
    if parts and parts[0] == "skills":
        parts = parts[1:]
    root = SKILLS_ROOT.joinpath(*parts)
    if not root.is_dir():
        raise SystemExit(f"No such skills directory: {root}")
    return root


def parse_args(argv: list[str]) -> tuple[str, Path]:
    args = [a for a in argv[1:] if a != "--"]
    mode = "copy"
    if args and args[0] in ("copy", "link"):
        mode, *args = args
    if len(args) > 1:
        print(f"usage: {argv[0]} [copy|link] [subdir]", file=sys.stderr)
        raise SystemExit(2)
    subdir = args[0] if args else None
    return mode, resolve_root(subdir)


def main(argv: list[str]) -> int:
    mode, root = parse_args(argv)
    install(mode, root)
    print()
    print("Done. Reload to pick up changes:")
    print("  Claude Code: restart session (or /skills if available)")
    print("  Tabnine CLI: /skills reload")
    print("  opencode:    restart session; verify with `opencode debug skill`")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
