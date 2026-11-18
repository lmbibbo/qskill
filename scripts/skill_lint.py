"""Validate qskill skill packages against docs/conventions.md.

Usage:
    python scripts/skill_lint.py [path ...]

Each path may be a skill directory, a directory containing skills, or a
SKILL.md file. Directories are searched recursively for SKILL.md. Defaults to
``.agents/skills``.

Exit codes:
    0  no errors (warnings allowed)
    1  at least one error
    2  usage error, such as a path that does not exist
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

SKILL_FILE = "SKILL.md"
MAX_LINES = 500
DESCRIPTION_MIN = 60
DESCRIPTION_MAX = 500
COLLISION_THRESHOLD = 4

ID_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
PLACEHOLDER_PATTERN = re.compile(r"\b(TODO|FIXME|XXX)\b")
LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
IGNORED_LINK_PREFIXES = ("http://", "https://", "mailto:", "#", "/")

# Words that carry no routing signal. Kept next to the rule so it can be tuned
# in one place; see docs/conventions.md.
STOPWORDS = frozenset(
    """
    about after again against all also and any are before being below between
    both but can could did does doing done down during each every few for from
    further had has have here how into its itself just more most not off once
    only other our out over own same should some such than that the their them
    then there these they this those through too under until very was were what
    when where which while who whom why will with within without would your
    you yours
    """.split()
)

SEVERITY_ERROR = "error"
SEVERITY_WARNING = "warning"


@dataclass(frozen=True)
class Issue:
    rule: str
    severity: str
    path: Path
    message: str


@dataclass
class Skill:
    directory: Path
    skill_id: str
    text: str
    frontmatter: dict
    description: str


def normalize_name(value: str) -> str:
    return " ".join(value.replace("_", " ").replace("-", " ").lower().split())


def discover_skill_files(targets: list[str]) -> list[Path]:
    files: list[Path] = []
    for raw in targets:
        target = Path(raw)
        if not target.exists():
            raise FileNotFoundError(f"path not found: {raw}")
        if target.is_file():
            if target.name != SKILL_FILE:
                raise ValueError(f"not a {SKILL_FILE}: {raw}")
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


def split_frontmatter(text: str) -> tuple[str | None, int]:
    """Return the frontmatter block (or None) and the line index where it ends."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, 0
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[1:index]), index + 1
    return None, 0


def check_layout(directory: Path) -> list[Issue]:
    if ID_PATTERN.match(directory.name):
        return []
    return [
        Issue(
            "layout",
            SEVERITY_ERROR,
            directory / SKILL_FILE,
            f"skill directory '{directory.name}' is not kebab-case "
            "(expected ^[a-z0-9]+(-[a-z0-9]+)*$)",
        )
    ]


def check_frontmatter(
    path: Path, block: str | None, directory: Path
) -> tuple[list[Issue], dict, str]:
    issues: list[Issue] = []
    if block is None:
        issues.append(
            Issue("frontmatter", SEVERITY_ERROR, path, "missing frontmatter block")
        )
        return issues, {}, ""
    try:
        data = yaml.safe_load(block)
    except yaml.YAMLError as error:
        issues.append(
            Issue("frontmatter", SEVERITY_ERROR, path, f"invalid YAML: {error}")
        )
        return issues, {}, ""
    if not isinstance(data, dict):
        issues.append(
            Issue("frontmatter", SEVERITY_ERROR, path, "frontmatter is not a mapping")
        )
        return issues, {}, ""

    missing = [key for key in ("name", "description") if not data.get(key)]
    if missing:
        issues.append(
            Issue(
                "frontmatter",
                SEVERITY_ERROR,
                path,
                f"missing required key(s): {', '.join(missing)}",
            )
        )

    name = data.get("name")
    if isinstance(name, str) and name:
        if normalize_name(name) != normalize_name(directory.name):
            issues.append(
                Issue(
                    "frontmatter",
                    SEVERITY_ERROR,
                    path,
                    f"name '{name}' does not match directory '{directory.name}'",
                )
            )

    description = data.get("description")
    description_text = description.strip() if isinstance(description, str) else ""
    return issues, data, description_text


def check_description(path: Path, description: str) -> list[Issue]:
    if not description:
        return []
    length = len(description)
    if DESCRIPTION_MIN <= length <= DESCRIPTION_MAX:
        return []
    return [
        Issue(
            "description-length",
            SEVERITY_ERROR,
            path,
            f"description is {length} characters, expected "
            f"{DESCRIPTION_MIN}-{DESCRIPTION_MAX}",
        )
    ]


def check_size(path: Path, text: str) -> list[Issue]:
    line_count = len(text.splitlines())
    if line_count <= MAX_LINES:
        return []
    return [
        Issue(
            "size",
            SEVERITY_ERROR,
            path,
            f"{SKILL_FILE} has {line_count} lines, maximum is {MAX_LINES}",
        )
    ]


def check_links(path: Path, text: str, directory: Path) -> list[Issue]:
    issues: list[Issue] = []
    for raw_target in LINK_PATTERN.findall(text):
        target = raw_target.strip()
        if not target or target.startswith(IGNORED_LINK_PREFIXES):
            continue
        target = target.split("#", 1)[0].split("?", 1)[0]
        if not target:
            continue
        resolved = (directory / target).resolve()
        if not resolved.exists():
            issues.append(
                Issue("link", SEVERITY_ERROR, path, f"broken local link '{target}'")
            )
    return issues


def check_placeholders(path: Path, text: str) -> list[Issue]:
    issues: list[Issue] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for marker in PLACEHOLDER_PATTERN.findall(line):
            issues.append(
                Issue(
                    "placeholder",
                    SEVERITY_ERROR,
                    path,
                    f"unfinished marker '{marker}' at line {line_number}",
                )
            )
    return issues


def keywords(description: str) -> set[str]:
    tokens = re.findall(r"[a-z0-9]+", description.lower())
    return {token for token in tokens if len(token) >= 4 and token not in STOPWORDS}


def check_collisions(skills: list[Skill]) -> list[Issue]:
    issues: list[Issue] = []
    for index, first in enumerate(skills):
        if not first.description:
            continue
        first_keywords = keywords(first.description)
        for second in skills[index + 1 :]:
            if not second.description:
                continue
            shared = first_keywords & keywords(second.description)
            if len(shared) >= COLLISION_THRESHOLD:
                issues.append(
                    Issue(
                        "trigger-collision",
                        SEVERITY_WARNING,
                        second.directory / SKILL_FILE,
                        f"'{first.skill_id}' and '{second.skill_id}' share "
                        f"{len(shared)} significant keywords: "
                        f"{', '.join(sorted(shared))}",
                    )
                )
    return issues


def lint(files: list[Path]) -> tuple[list[Skill], list[Issue]]:
    skills: list[Skill] = []
    issues: list[Issue] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        directory = path.parent
        issues.extend(check_layout(directory))
        block, _ = split_frontmatter(text)
        frontmatter_issues, data, description = check_frontmatter(path, block, directory)
        issues.extend(frontmatter_issues)
        issues.extend(check_description(path, description))
        issues.extend(check_size(path, text))
        issues.extend(check_links(path, text, directory))
        issues.extend(check_placeholders(path, text))
        skills.append(
            Skill(
                directory=directory,
                skill_id=directory.name,
                text=text,
                frontmatter=data,
                description=description,
            )
        )
    issues.extend(check_collisions(skills))
    return skills, issues


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        prog="skill_lint.py",
        description="Validate qskill skills against docs/conventions.md.",
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    parser.add_argument(
        "paths",
        nargs="*",
        default=[".agents/skills"],
        help="skill files or directories to check (default: .agents/skills)",
    )
    args = parser.parse_args(argv)

    try:
        files = discover_skill_files(args.paths)
    except (FileNotFoundError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if not files:
        print("error: no SKILL.md found in the given paths", file=sys.stderr)
        return 2

    skills, issues = lint(files)

    for skill in skills:
        own = [issue for issue in issues if issue.path.parent == skill.directory]
        errors = sum(1 for issue in own if issue.severity == SEVERITY_ERROR)
        warnings = sum(1 for issue in own if issue.severity == SEVERITY_WARNING)
        status = "ok" if errors == 0 else "FAIL"
        print(f"{skill.skill_id:<32} {status}  ({errors} errors, {warnings} warnings)")

    for issue in issues:
        try:
            location = issue.path.relative_to(Path.cwd())
        except ValueError:
            location = issue.path
        print(f"{location}: {issue.severity}: [{issue.rule}] {issue.message}")

    errors = sum(1 for issue in issues if issue.severity == SEVERITY_ERROR)
    warnings = sum(1 for issue in issues if issue.severity == SEVERITY_WARNING)
    print()
    print(
        f"Summary: {len(skills)} skills, {errors} errors, {warnings} warnings",
        file=sys.stderr if errors else sys.stdout,
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
