"""Execute every fenced Python block in one or more SKILL.md files.

Usage:
    python scripts/run_snippets.py [path ...]

Each path may be a SKILL.md file or a directory searched recursively for
SKILL.md. Defaults to ``.agents/skills``.

Blocks are executed one per subprocess, with the repository root as working
directory and a 120 second timeout. A block whose first line is
``# qskill: skip`` is reported as skipped and never executed.

Exit codes:
    0  no failing blocks
    1  at least one failing block
    2  usage error
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from snippet_lib import DEFAULT_TIMEOUT, extract_snippets, run_snippet

SKILL_FILE = "SKILL.md"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def discover_skill_files(targets: list[str]) -> list[Path]:
    files: list[Path] = []
    for raw in targets:
        target = Path(raw)
        if not target.exists():
            raise FileNotFoundError(f"path not found: {raw}")
        if target.is_file():
            files.append(target)
            continue
        for candidate in sorted(target.rglob(SKILL_FILE)):
            relative = candidate.relative_to(target)
            hidden = any(
                part.startswith(".") or part == "node_modules"
                for part in relative.parts[:-1]
            )
            if not hidden:
                files.append(candidate)
    return files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_snippets.py",
        description="Execute every fenced Python block in SKILL.md files.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=[".agents/skills"],
        help="SKILL.md files or directories to scan (default: .agents/skills)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"per-block timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        files = discover_skill_files(args.paths)
    except FileNotFoundError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if not files:
        print("error: no SKILL.md found in the given paths", file=sys.stderr)
        return 2

    total = passed = failed = skipped = 0

    for path in files:
        snippets = extract_snippets(path.read_text(encoding="utf-8"))
        print(f"{path}")
        if not snippets:
            print("  (no python blocks)")
            continue
        for snippet in snippets:
            total += 1
            label = f"  block {snippet.order} (line {snippet.line})"
            if snippet.skipped:
                skipped += 1
                print(f"{label}: skipped")
                continue
            result = run_snippet(snippet.code, REPOSITORY_ROOT, args.timeout)
            if result.passed:
                passed += 1
                print(f"{label}: ok")
            else:
                failed += 1
                print(f"{label}: FAILED")
                print(f"    {result.detail}")

    print()
    print(
        f"Summary: {total} blocks, {passed} passed, {failed} failed, "
        f"{skipped} skipped"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
