#!/usr/bin/env python3
"""Dependency-free checks for this repository's simple SKILL.md frontmatter."""

from __future__ import annotations

import re
import sys
from pathlib import Path


NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def fail(message: str) -> None:
    raise SystemExit(message)


def main() -> None:
    if len(sys.argv) != 2:
        fail("Usage: validate_skill.py <skill-directory>")

    skill_dir = Path(sys.argv[1])
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        fail(f"Missing {skill_file}")

    content = skill_file.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
    if not match:
        fail(f"Invalid frontmatter in {skill_file}")

    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if not separator:
            fail(f"Invalid frontmatter line in {skill_file}: {line}")
        fields[key.strip()] = value.strip().strip('"')

    if set(fields) != {"name", "description"}:
        fail(f"Expected only name and description in {skill_file}")
    if fields["name"] != skill_dir.name:
        fail(f"Skill name does not match directory: {skill_dir}")
    if not NAME_PATTERN.fullmatch(fields["name"]) or len(fields["name"]) > 64:
        fail(f"Invalid skill name: {fields['name']}")
    if not fields["description"] or len(fields["description"]) > 1024:
        fail(f"Invalid description in {skill_file}")
    if "[TODO:" in content:
        fail(f"Unfinished placeholder in {skill_file}")

    print(f"Valid: {skill_dir.name}")


if __name__ == "__main__":
    main()
