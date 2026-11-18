"""Shared snippet extraction and execution used by qskill tooling.

The rules live here so ``scripts/run_snippets.py`` and ``evals/run.py`` cannot
drift apart. See design §D4 and docs/conventions.md.
"""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

SKIP_MARKER = "# qskill: skip"
DEFAULT_TIMEOUT = 120

FENCE_PATTERN = re.compile(
    r"^```[ \t]*(?:python|py)[ \t]*\n(.*?)^```[ \t]*$",
    re.MULTILINE | re.DOTALL,
)


@dataclass(frozen=True)
class Snippet:
    order: int
    line: int
    code: str

    @property
    def skipped(self) -> bool:
        lines = self.code.splitlines()
        return bool(lines) and lines[0].strip() == SKIP_MARKER


@dataclass(frozen=True)
class SnippetResult:
    passed: bool
    detail: str


def extract_snippets(text: str) -> list[Snippet]:
    """Return every fenced python block, in document order."""
    normalized = text.replace("\r\n", "\n")
    snippets: list[Snippet] = []
    for order, match in enumerate(FENCE_PATTERN.finditer(normalized), start=1):
        line = normalized.count("\n", 0, match.start()) + 2
        snippets.append(Snippet(order=order, line=line, code=match.group(1)))
    return snippets


def run_snippet(
    code: str,
    repository_root: Path,
    timeout: int = DEFAULT_TIMEOUT,
) -> SnippetResult:
    """Execute one block in an isolated interpreter with captured output."""
    try:
        completed = subprocess.run(
            [sys.executable, "-"],
            input=code,
            text=True,
            capture_output=True,
            timeout=timeout,
            cwd=repository_root,
        )
    except subprocess.TimeoutExpired:
        return SnippetResult(False, f"timed out after {timeout}s")
    except OSError as error:
        return SnippetResult(False, f"could not start interpreter: {error}")

    if completed.returncode == 0:
        return SnippetResult(True, "")

    detail = (completed.stderr or completed.stdout).strip()
    first_line = detail.splitlines()[-1] if detail else "no error output"
    return SnippetResult(False, f"exit {completed.returncode}: {first_line}")
