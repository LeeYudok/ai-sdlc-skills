#!/usr/bin/env python3
"""Maintain a small, deterministic state file for an AI SDLC run."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


STAGES = [
    "initialized",
    "analyzed",
    "evidence_collected",
    "ba_ready",
    "impact_assessed",
    "specified",
    "implemented",
    "verified",
    "local_deployed",
    "release_ready",
    "complete",
]
RUN_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REQUIRED_ARTIFACTS = {
    "analyzed": ["repository-analysis.md"],
    "evidence_collected": ["evidence-ledger.md"],
    "ba_ready": ["ba.md"],
    "impact_assessed": ["impact-analysis.md"],
    "specified": ["feature-spec.md", "implementation-plan.md"],
    "implemented": ["implementation-report.md"],
    "verified": ["qa-report.md"],
    "local_deployed": ["local-deploy-report.md"],
    "release_ready": ["release-plan.md"],
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def git_head(root: Path) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def run_dir(root: Path, run: str) -> Path:
    if not RUN_PATTERN.fullmatch(run):
        raise SystemExit("run must be lowercase kebab-case")
    return root.resolve() / ".ai-sdlc" / "runs" / run


def state_path(root: Path, run: str) -> Path:
    return run_dir(root, run) / "state.json"


def load(root: Path, run: str) -> dict:
    path = state_path(root, run)
    if not path.is_file():
        raise SystemExit(f"state not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def save(root: Path, run: str, state: dict) -> None:
    path = state_path(root, run)
    payload = json.dumps(state, ensure_ascii=False, indent=2) + "\n"
    temp_path = path.with_name(path.name + ".tmp")
    with temp_path.open("w", encoding="utf-8") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp_path, path)


def init(args: argparse.Namespace) -> None:
    root = Path(args.root)
    directory = run_dir(root, args.run)
    directory.mkdir(parents=True, exist_ok=False)
    (directory / "request.md").write_text(
        f"# Original request\n\n{args.request}\n",
        encoding="utf-8",
    )
    timestamp = now()
    state = {
        "run": args.run,
        "status": "running",
        "stage": "initialized",
        "completed_stages": ["initialized"],
        "created_at": timestamp,
        "updated_at": timestamp,
        "repository_head_at_init": git_head(root),
        "block_reason": None,
        "history": [
            {
                "event": "initialized",
                "at": timestamp,
                "repository_head": git_head(root),
            }
        ],
    }
    save(root, args.run, state)
    print(json.dumps(state, ensure_ascii=False, indent=2))


def advance(args: argparse.Namespace) -> None:
    root = Path(args.root)
    state = load(root, args.run)
    if state["status"] == "blocked":
        raise SystemExit("run is blocked; resume it before advancing")
    current = STAGES.index(state["stage"])
    expected = STAGES[current + 1] if current + 1 < len(STAGES) else None
    if args.stage != expected:
        raise SystemExit(
            f"invalid transition: {state['stage']} -> {args.stage}; expected {expected}"
        )
    missing = [
        artifact
        for artifact in REQUIRED_ARTIFACTS.get(args.stage, [])
        if not (run_dir(root, args.run) / artifact).is_file()
        or (run_dir(root, args.run) / artifact).stat().st_size == 0
    ]
    if missing:
        raise SystemExit(
            f"cannot advance to {args.stage}; missing or empty artifacts: {', '.join(missing)}"
        )
    timestamp = now()
    state["stage"] = args.stage
    state["completed_stages"].append(args.stage)
    state["status"] = "complete" if args.stage == "complete" else "running"
    state["updated_at"] = timestamp
    state["repository_head"] = git_head(root)
    state["history"].append(
        {
            "event": f"advanced:{args.stage}",
            "at": timestamp,
            "repository_head": state["repository_head"],
        }
    )
    save(root, args.run, state)
    print(json.dumps(state, ensure_ascii=False, indent=2))


def block(args: argparse.Namespace) -> None:
    root = Path(args.root)
    state = load(root, args.run)
    state["status"] = "blocked"
    state["block_reason"] = args.reason
    timestamp = now()
    state["updated_at"] = timestamp
    state["history"].append(
        {"event": "blocked", "at": timestamp, "reason": args.reason}
    )
    save(root, args.run, state)
    print(json.dumps(state, ensure_ascii=False, indent=2))


def resume(args: argparse.Namespace) -> None:
    root = Path(args.root)
    state = load(root, args.run)
    if state["status"] != "blocked":
        raise SystemExit("only a blocked run can be resumed")
    state["status"] = "running"
    state["block_reason"] = None
    timestamp = now()
    state["updated_at"] = timestamp
    state["history"].append({"event": "resumed", "at": timestamp})
    save(root, args.run, state)
    print(json.dumps(state, ensure_ascii=False, indent=2))


def show(args: argparse.Namespace) -> None:
    print(json.dumps(load(Path(args.root), args.run), ensure_ascii=False, indent=2))


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    subparsers = result.add_subparsers(required=True)
    for command in ("init", "advance", "block", "resume", "show"):
        command_parser = subparsers.add_parser(command)
        command_parser.add_argument("--root", required=True)
        command_parser.add_argument("--run", required=True)
        command_parser.set_defaults(handler=globals()[command])
        if command == "init":
            command_parser.add_argument("--request", required=True)
        elif command == "advance":
            command_parser.add_argument("--stage", choices=STAGES[1:], required=True)
        elif command == "block":
            command_parser.add_argument("--reason", required=True)
    return result


if __name__ == "__main__":
    arguments = parser().parse_args()
    arguments.handler(arguments)
