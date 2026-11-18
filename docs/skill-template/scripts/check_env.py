"""Report the environment this skill depends on.

Replace the version checks with the SDK imports the skill needs, and keep the
exit code contract: 0 when the environment is usable, 1 with a fix hint when it
is not.
"""

from __future__ import annotations

import sys

SKILL_ID = "{{skill-id}}"


def main() -> int:
    print(f"skill {SKILL_ID}")
    print(f"python {sys.version.split()[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
