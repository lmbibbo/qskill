"""Create a new skill from docs/skill-template.

Usage:
    python scripts/new_skill.py <skill-id> [--dest PATH]

The skill ID must be kebab-case. The generated skill contains a valid
``SKILL.md``, a ``references/api-map.md`` stub and a ``scripts/check_env.py``
stub, and passes ``scripts/skill_lint.py`` without edits.

Exit codes:
    0  skill created
    1  target already exists or template is missing
    2  invalid skill ID
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

ID_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
REPO_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = REPO_ROOT / "docs" / "skill-template"
DEFAULT_DEST = REPO_ROOT / ".agents" / "skills"
TEXT_SUFFIXES = {".md", ".py"}


def display_name(skill_id: str) -> str:
    return " ".join(part.capitalize() for part in skill_id.split("-"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="new_skill.py",
        description="Create a skill from docs/skill-template.",
    )
    parser.add_argument("skill_id", help="kebab-case skill ID, e.g. qiskit-workflow")
    parser.add_argument(
        "--dest",
        default=str(DEFAULT_DEST),
        help=f"directory that will hold the skill (default: {DEFAULT_DEST})",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if not ID_PATTERN.match(args.skill_id):
        print(
            "error: skill ID must match ^[a-z0-9]+(-[a-z0-9]+)*$, "
            f"got '{args.skill_id}'",
            file=sys.stderr,
        )
        return 2

    if not TEMPLATE_DIR.is_dir():
        print(f"error: template directory not found: {TEMPLATE_DIR}", file=sys.stderr)
        return 1

    dest_root = Path(args.dest)
    target = dest_root / args.skill_id
    if target.exists():
        print(f"error: skill already exists: {target}", file=sys.stderr)
        return 1

    dest_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(TEMPLATE_DIR, target)

    replacements = {
        "{{skill-id}}": args.skill_id,
        "{{Skill Name}}": display_name(args.skill_id),
    }
    for path in target.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        for placeholder, value in replacements.items():
            text = text.replace(placeholder, value)
        path.write_text(text, encoding="utf-8")

    print(f"created {target}")
    for path in sorted(target.rglob("*")):
        if path.is_file():
            print(f"  {path.relative_to(target)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
