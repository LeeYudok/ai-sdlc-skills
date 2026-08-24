#!/usr/bin/env python3
"""Detect optional analysis tools without installing or configuring them."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path


TOOLS = {
    "codegraph": {
        "executable": "codegraph",
        "markers": [".codegraph"],
        "mode": "local-symbol-graph",
    },
    "graphify": {
        "executable": "graphify",
        "markers": ["graphify-out/graph.json", "graph.json"],
        "mode": "code-and-document-graph",
    },
    "code_graph_rag": {
        "executable": "cgr",
        "markers": [],
        "mode": "graph-rag-services",
    },
    "open_code_review": {
        "executable": "ocr",
        "markers": [],
        "mode": "diff-review",
    },
}


def version(executable: str) -> dict[str, object]:
    path = shutil.which(executable)
    if path is None:
        return {"installed": False, "path": None, "version": None}
    environment = os.environ.copy()
    environment["NO_COLOR"] = "1"
    try:
        result = subprocess.run(
            [path, "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
            env=environment,
        )
        output = (result.stdout or result.stderr).strip().splitlines()
        value = output[0] if output else f"exit {result.returncode}"
    except (OSError, subprocess.TimeoutExpired) as error:
        value = f"unavailable: {type(error).__name__}"
    return {"installed": True, "path": path, "version": value}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if not root.is_dir():
        raise SystemExit(f"repository root not found: {root}")

    report: dict[str, object] = {"root": str(root), "tools": {}}
    for name, configuration in TOOLS.items():
        detected = version(str(configuration["executable"]))
        markers = [
            marker
            for marker in configuration["markers"]
            if (root / marker).exists()
        ]
        detected["mode"] = configuration["mode"]
        detected["repository_markers"] = markers
        detected["index_detected"] = bool(markers)
        report["tools"][name] = detected

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
