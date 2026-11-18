"""Run qskill eval cases against recorded responses.

Usage:
    python evals/run.py [--cases PATH] [--skill ID] [--list]

Cases are YAML files under ``<cases>/<skill-id>/*.yaml``. The runner grades the
recorded ``response`` (or ``response_file``); it never calls a model and never
uses the network. See evals/schema.md.

Exit codes:
    0  every case passed, or --list was used
    1  at least one check failed
    2  usage error, such as a missing cases directory or malformed case
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES_DIR = REPOSITORY_ROOT / "evals" / "cases"

sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))
from snippet_lib import extract_snippets, run_snippet  # noqa: E402

FALLBACK_NUMBER = re.compile(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")


class CaseError(ValueError):
    """A case file that cannot be executed."""


def iter_case_files(cases_dir: Path, skill_filter: str | None) -> list[tuple[str, Path]]:
    if not cases_dir.is_dir():
        raise CaseError(f"cases directory not found: {cases_dir}")
    found: list[tuple[str, Path]] = []
    for skill_dir in sorted(path for path in cases_dir.iterdir() if path.is_dir()):
        if skill_filter and skill_dir.name != skill_filter:
            continue
        for case_file in sorted(skill_dir.glob("*.yaml")):
            found.append((skill_dir.name, case_file))
    return found


def load_case(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise CaseError(f"{path}: invalid YAML: {error}") from error
    if not isinstance(data, dict):
        raise CaseError(f"{path}: case must be a mapping")

    for key in ("id", "skill", "prompt", "checks"):
        if key not in data:
            raise CaseError(f"{path}: missing required field '{key}'")

    has_response = "response" in data
    has_response_file = "response_file" in data
    if has_response == has_response_file:
        raise CaseError(
            f"{path}: exactly one of 'response' or 'response_file' is required"
        )

    if has_response_file:
        response_path = (path.parent / str(data["response_file"])).resolve()
        if not response_path.is_file():
            raise CaseError(f"{path}: response_file not found: {response_path}")
        data["response"] = response_path.read_text(encoding="utf-8")

    if not isinstance(data["checks"], list) or not data["checks"]:
        raise CaseError(f"{path}: 'checks' must be a non-empty list")

    return data


def extract_number(text: str, pattern: str | None) -> float | None:
    if pattern:
        match = re.search(pattern, text)
        if not match:
            return None
        value = match.group(1) if match.groups() else match.group(0)
        try:
            return float(value)
        except ValueError:
            # Tolerate trailing punctuation captured by a loose pattern.
            fallback = FALLBACK_NUMBER.search(value)
            return float(fallback.group(0)) if fallback else None
    match = FALLBACK_NUMBER.search(text)
    return float(match.group(0)) if match else None


def check_required_patterns(response: str, check: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for pattern in check.get("patterns", []):
        try:
            if not re.search(pattern, response):
                failures.append(f"missing pattern '{pattern}'")
        except re.error as error:
            failures.append(f"invalid pattern '{pattern}': {error}")
    return failures


def check_forbidden_patterns(response: str, check: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    for pattern in check.get("patterns", []):
        try:
            if re.search(pattern, response):
                failures.append(f"forbidden pattern '{pattern}' found")
        except re.error as error:
            failures.append(f"invalid pattern '{pattern}': {error}")
    return failures


def check_numeric_close(response: str, check: dict[str, Any]) -> list[str]:
    if "target" not in check or "tolerance" not in check:
        return ["numeric_close requires 'target' and 'tolerance'"]
    value = extract_number(response, check.get("pattern"))
    if value is None:
        return ["no number found in response"]
    target = float(check["target"])
    tolerance = float(check["tolerance"])
    if abs(value - target) > tolerance:
        return [f"value {value} is not within {tolerance} of {target}"]
    return []


def check_snippet_runs(response: str) -> list[str]:
    snippets = extract_snippets(response)
    runnable = [snippet for snippet in snippets if not snippet.skipped]
    if not runnable:
        return ["no python blocks found in response"]
    failures: list[str] = []
    for snippet in runnable:
        result = run_snippet(snippet.code, REPOSITORY_ROOT)
        if not result.passed:
            failures.append(f"block {snippet.order} failed: {result.detail}")
    return failures


CHECK_HANDLERS = {
    "required_patterns": lambda response, check: check_required_patterns(
        response, check
    ),
    "forbidden_patterns": lambda response, check: check_forbidden_patterns(
        response, check
    ),
    "numeric_close": lambda response, check: check_numeric_close(response, check),
    "snippet_runs": lambda response, _check: check_snippet_runs(response),
}


def evaluate_case(case: dict[str, Any]) -> list[str]:
    response = str(case["response"])
    failures: list[str] = []
    for check in case["checks"]:
        if not isinstance(check, dict) or "kind" not in check:
            failures.append("check entry is not a mapping with a 'kind'")
            continue
        kind = check["kind"]
        handler = CHECK_HANDLERS.get(kind)
        if handler is None:
            failures.append(f"unknown check kind '{kind}'")
            continue
        for failure in handler(response, check):
            failures.append(f"{kind}: {failure}")
    return failures


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run.py",
        description="Run qskill eval cases against recorded responses.",
    )
    parser.add_argument(
        "--cases",
        default=str(DEFAULT_CASES_DIR),
        help=f"cases root directory (default: {DEFAULT_CASES_DIR})",
    )
    parser.add_argument("--skill", help="only run cases for this skill ID")
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_only",
        help="list discovered cases without executing them",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    cases_dir = Path(args.cases)

    try:
        case_files = iter_case_files(cases_dir, args.skill)
    except CaseError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if args.list_only:
        for skill_id, path in case_files:
            print(f"{skill_id}/{path.name}")
        print(f"{len(case_files)} cases found")
        return 0

    if not case_files:
        print("Summary: 0 cases, 0 passed, 0 failed")
        return 0

    passed = failed = 0
    for skill_id, path in case_files:
        try:
            case = load_case(path)
        except CaseError as error:
            print(f"{skill_id}/{path.name}: ERROR")
            print(f"  {error}")
            failed += 1
            continue

        failures = evaluate_case(case)
        label = f"{skill_id}/{case.get('id', path.stem)}"
        if failures:
            failed += 1
            print(f"{label}: FAIL")
            for failure in failures:
                print(f"  {failure}")
        else:
            passed += 1
            print(f"{label}: PASS")

    print()
    print(f"Summary: {passed + failed} cases, {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
