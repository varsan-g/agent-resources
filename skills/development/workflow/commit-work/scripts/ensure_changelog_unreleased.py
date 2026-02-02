#!/usr/bin/env python3
import sys
from pathlib import Path


def main() -> int:
    changelog = Path("CHANGELOG.md")
    if not changelog.exists():
        print("CHANGELOG.md not found. Create it before committing.", file=sys.stderr)
        return 1

    lines = changelog.read_text(encoding="utf-8").splitlines()
    unreleased_index = None
    for i, line in enumerate(lines):
        if line.strip() == "## [Unreleased]":
            unreleased_index = i
            break

    if unreleased_index is None:
        print("Missing '## [Unreleased]' section in CHANGELOG.md.", file=sys.stderr)
        return 1

    content_lines = []
    for line in lines[unreleased_index + 1 :]:
        if line.startswith("## "):
            break
        content_lines.append(line)

    has_bullets = any(line.strip().startswith(("- ", "* ")) for line in content_lines)
    if not has_bullets:
        print(
            "'## [Unreleased]' has no bullet entries. Add changes before committing.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
