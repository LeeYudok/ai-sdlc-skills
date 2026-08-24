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


def check(args: argparse.Namespace) -> None:
    path = handoff_path(Path(args.root), args.run)
    if not path.is_file():
        raise SystemExit(f"handoff not found: {path}")
    content = path.read_text(encoding="utf-8")
    problems: list[str] = []
    fill_count = content.count(FILL)
    if fill_count:
        problems.append(f"{fill_count} unfilled '{FILL}' marker(s)")
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
        if not content[start + len(heading) : end].strip():
            problems.append(f"empty section: {heading}")
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
