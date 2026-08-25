#!/usr/bin/env python3
"""Generate and validate HANDOFF.md snapshots for an AI SDLC run."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

FILL = "<!-- FILL -->"
RUN_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REQUIRED_SECTIONS = [
    "## 1. Goal (do not change)",
    "## 2. Current state",
    "## 3. Decisions (do not reopen)",
    "## 4. Remaining work (in order)",
    "## 5. Traps",
    "## 6. Resume procedure",
    "## 7. Files to load (only these)",
]
SECRET_PATTERN = re.compile(
    r"(?i)(api[_-]?key|secret|token|password)\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{12,}"
)
PLACEHOLDER_FRAGMENTS = (
    "original request",
    "mark each",
    "only what was actually executed",
    "next concrete action",
    "approach tried and failed",
    "files not to touch",
    "one verification command",
    "dependency / server start command",
    "environment specifics",
    "main change site",
    "verifies ac",
)
PLACEHOLDER_EXACT = {
    "",
    "ac-1",
    "ac-n",
    "tbd",
    "todo",
    "n/a",
    "na",
    "…",
    "...",
    "path — why",
    "path - why",
}
EXPLICIT_NONE = {"없음", "none", "no decisions", "결정 없음", "해당 없음"}
ANGLE_PLACEHOLDER = re.compile(r"<[^<>]{2,}>")
LIST_PREFIX = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s*")
CHECKBOX_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s*\[[ xX]\]\s*(?P<text>.*)$")
UNRESOLVED_BRANCH = re.compile(r"\bgit\s+(?:switch|checkout)\s+(?:unknown|none)\b")


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args], check=False, capture_output=True, text=True
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def handoff_path(root: Path, run: str | None) -> Path:
    base = root.resolve() / ".ai-sdlc"
    if run is None:
        return base / "HANDOFF.md"
    if not RUN_PATTERN.fullmatch(run):
        raise SystemExit("run must be lowercase kebab-case")
    return base / "runs" / run / "HANDOFF.md"


def load_state(root: Path, run: str | None) -> tuple[dict, str]:
    if run is None:
        return {}, ""
    run_dir = root.resolve() / ".ai-sdlc" / "runs" / run
    state_file = run_dir / "state.json"
    if not state_file.is_file():
        raise SystemExit(f"state not found: {state_file}")
    state = json.loads(state_file.read_text(encoding="utf-8"))
    request_file = run_dir / "request.md"
    request = ""
    if request_file.is_file():
        lines = request_file.read_text(encoding="utf-8").splitlines()
        request = "\n".join(line for line in lines if not line.startswith("# ")).strip()
    return state, request


def render(root: Path, run: str | None) -> str:
    state, request = load_state(root, run)
    branch = git(root, "rev-parse", "--abbrev-ref", "HEAD") or "unknown"
    head = git(root, "rev-parse", "--short", "HEAD") or "none"
    subject = git(root, "log", "-1", "--format=%s") or "(no commits)"
    dirty = git(root, "status", "--porcelain")
    dirty_block = (
        "\n".join(f"  - `{line[2:].lstrip()}`" for line in dirty.splitlines()) if dirty else "  none"
    )
    stage = state.get("stage", "n/a")
    completed = " → ".join(state.get("completed_stages", [])) or "n/a"
    status = state.get("status", "n/a")
    block = state.get("block_reason")
    block_line = f"\n- Blocked: {block}" if block else ""
    title = run or "ad-hoc"
    written = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    request_block = request or f"{FILL} original request"

    return f"""# HANDOFF — {title}

Written: {written} | Branch: `{branch}` | HEAD: `{head}`

## 1. Goal (do not change)
- Request: {request_block}
- Pipeline stage: `{stage}` ({status}; completed: {completed}){block_line}
- Acceptance criteria:
  - [ ] {FILL} AC-1

## 2. Current state
- Last commit: `{head}` {subject}
- Uncommitted changes:
{dirty_block}
- Verification status: {FILL} typecheck / unit / e2e — mark each ✅ or ❌ (not run)
- Confirmed working: {FILL} only what was actually executed

## 3. Decisions (do not reopen)
| Decision | Reason | Rejected alternative and why |
|---|---|---|
| {FILL} | | |

## 4. Remaining work (in order)
1. {FILL} next concrete action — file path and symbol
2. Final: verification command → PR → `Closes #N`

## 5. Traps
- {FILL} approach tried and failed, and why
- {FILL} files not to touch / environment specifics (ports, env vars, mocks)

## 6. Resume procedure
```bash
git switch {branch}
{FILL} one verification command   # passing proves section 2 is accurate
```

## 7. Files to load (only these)
- {FILL} `path` — why
"""


def write(args: argparse.Namespace) -> None:
    root = Path(args.root)
    path = handoff_path(root, args.run)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(root, args.run), encoding="utf-8")
    print(path)


def normalize(text: str) -> str:
    """Lowercase and strip list/checkbox/markdown decoration for matching."""
    value = LIST_PREFIX.sub("", text.strip())
    value = re.sub(r"^\[[ xX]\]\s*", "", value)
    value = value.replace("`", "").replace("*", "").replace("#", "")
    value = re.sub(r"\s+", " ", value).strip()
    return value.strip(" .:;—-").lower()


def is_placeholder(text: str) -> bool:
    """True when the text is template guidance rather than a real value."""
    if FILL in text:
        return True
    value = normalize(text)
    if value in PLACEHOLDER_EXACT:
        return True
    if ANGLE_PLACEHOLDER.search(value):
        return True
    return any(fragment in value for fragment in PLACEHOLDER_FRAGMENTS)


def is_explicit_none(text: str) -> bool:
    return normalize(text) in EXPLICIT_NONE


def split_sections(content: str, problems: list[str]) -> dict[str, str]:
    """Return heading -> body, recording missing and empty sections as problems."""
    sections: dict[str, str] = {}
    for index, heading in enumerate(REQUIRED_SECTIONS):
        start = content.find(heading)
        if start < 0:
            problems.append(f"missing section: {heading}")
            continue
        end = (
            content.find(REQUIRED_SECTIONS[index + 1])
            if index + 1 < len(REQUIRED_SECTIONS)
            else len(content)
        )
        body = content[start + len(heading) : end]
        if not body.strip():
            problems.append(f"empty section: {heading}")
            continue
        sections[heading] = body
    return sections


def field(body: str, label: str) -> str | None:
    """Value of a '- <label>: <value>' line, or None when the line is absent."""
    for line in body.splitlines():
        stripped = LIST_PREFIX.sub("", line.strip())
        if stripped.lower().startswith(f"{label.lower()}:"):
            return stripped[len(label) + 1 :].strip()
    return None


def require_field(body: str, label: str, section: str, problems: list[str]) -> None:
    value = field(body, label)
    if value is None:
        problems.append(f"{section}: missing '{label}' line")
    elif is_placeholder(value):
        problems.append(f"{section}: '{label}' still holds placeholder text")


def bullets(body: str) -> list[str]:
    """Top-level list items of a section body, code blocks and tables excluded."""
    items: list[str] = []
    in_code = False
    for line in body.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code or line.strip().startswith("|"):
            continue
        if LIST_PREFIX.match(line):
            items.append(LIST_PREFIX.sub("", line.strip()))
    return items


def code_block(body: str) -> list[str]:
    """Non-empty, non-comment command lines inside the section's fenced block."""
    lines: list[str] = []
    in_code = False
    for line in body.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if not in_code:
            continue
        command = line.split("#", 1)[0].strip()
        if command:
            lines.append(command)
    return lines


def check_goal(sections: dict[str, str], problems: list[str]) -> None:
    body = sections.get(REQUIRED_SECTIONS[0])
    if body is None:
        return
    section = "goal"
    require_field(body, "Request", section, problems)
    criteria = [
        match.group("text")
        for line in body.splitlines()
        if (match := CHECKBOX_ITEM.match(line))
    ]
    if not criteria:
        problems.append(f"{section}: no acceptance criteria listed")
    elif all(is_placeholder(item) for item in criteria):
        problems.append(f"{section}: acceptance criteria are still placeholders")


def check_current_state(sections: dict[str, str], problems: list[str]) -> None:
    body = sections.get(REQUIRED_SECTIONS[1])
    if body is None:
        return
    require_field(body, "Verification status", "current state", problems)
    require_field(body, "Confirmed working", "current state", problems)


def check_decisions(sections: dict[str, str], problems: list[str]) -> None:
    body = sections.get(REQUIRED_SECTIONS[2])
    if body is None:
        return
    rows: list[list[str]] = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            if is_explicit_none(stripped):
                return
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if all(set(cell) <= set("-: ") for cell in cells):
            continue
        if cells[:1] == ["Decision"]:
            continue
        if cells and is_explicit_none(cells[0]):
            return
        rows.append(cells)
    filled = [
        row
        for row in rows
        if len(row) >= 3 and all(cell and not is_placeholder(cell) for cell in row[:3])
    ]
    if not filled:
        problems.append(
            "decisions: no completed row (state each decision, reason and rejected "
            "alternative, or write '없음' when there is none)"
        )


def check_remaining_work(sections: dict[str, str], problems: list[str]) -> None:
    body = sections.get(REQUIRED_SECTIONS[3])
    if body is None:
        return
    actionable = [
        item
        for item in bullets(body)
        if not is_placeholder(item) and not normalize(item).startswith("final:")
    ]
    if not actionable:
        problems.append("remaining work: no concrete next action")


def check_traps(sections: dict[str, str], problems: list[str]) -> None:
    body = sections.get(REQUIRED_SECTIONS[4])
    if body is None:
        return
    items = bullets(body)
    if any(is_explicit_none(item) for item in items):
        return
    if not [item for item in items if not is_placeholder(item)]:
        problems.append("traps: only placeholder text (write '없음' when there is none)")


def check_resume(sections: dict[str, str], problems: list[str]) -> None:
    body = sections.get(REQUIRED_SECTIONS[5])
    if body is None:
        return
    commands = code_block(body)
    if not commands:
        problems.append("resume procedure: no command to run")
        return
    if any(is_placeholder(command) for command in commands):
        problems.append("resume procedure: still holds placeholder text")
    unresolved = [command for command in commands if UNRESOLVED_BRANCH.search(command)]
    if unresolved:
        problems.append(
            f"resume procedure: unexecutable default `{unresolved[0]}` "
            "(record the real branch)"
        )
    verification = [
        command
        for command in commands
        if not re.match(r"^git\s+(?:switch|checkout)\b", command)
        and not is_placeholder(command)
    ]
    if not verification:
        problems.append(
            "resume procedure: no verification command after the branch switch"
        )


def check_files(sections: dict[str, str], problems: list[str]) -> None:
    body = sections.get(REQUIRED_SECTIONS[6])
    if body is None:
        return
    if not [item for item in bullets(body) if not is_placeholder(item)]:
        problems.append("files to load: no file listed")


def check(args: argparse.Namespace) -> None:
    path = handoff_path(Path(args.root), args.run)
    if not path.is_file():
        raise SystemExit(f"handoff not found: {path}")
    content = path.read_text(encoding="utf-8")
    problems: list[str] = []
    fill_count = content.count(FILL)
    if fill_count:
        problems.append(f"{fill_count} unfilled '{FILL}' marker(s)")
    sections = split_sections(content, problems)
    check_goal(sections, problems)
    check_current_state(sections, problems)
    check_decisions(sections, problems)
    check_remaining_work(sections, problems)
    check_traps(sections, problems)
    check_resume(sections, problems)
    check_files(sections, problems)
    if SECRET_PATTERN.search(content):
        problems.append("possible secret value in handoff")
    if problems:
        raise SystemExit("HANDOFF.md is not ready:\n- " + "\n- ".join(problems))
    print(f"ready: {path}")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    subparsers = result.add_subparsers(required=True)
    for command in ("write", "check"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("--root", required=True)
        command_parser.add_argument("--run", default=None)
        command_parser.set_defaults(handler=globals()[command])
    return result


if __name__ == "__main__":
    arguments = parser().parse_args()
    arguments.handler(arguments)
