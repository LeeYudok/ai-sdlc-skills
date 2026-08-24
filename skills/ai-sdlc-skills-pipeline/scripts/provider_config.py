#!/usr/bin/env python3
"""Resolve AI SDLC model-provider readiness without exposing secrets or URLs."""

from __future__ import annotations

import argparse
import json
import os


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=("openai", "vllm"))
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()

    provider = args.provider or os.environ.get("AI_SDLC_LLM_PROVIDER")
    if provider is None:
        if os.environ.get("AI_SDLC_LLM_BASE_URL"):
            provider = "vllm"
        elif os.environ.get("OPENAI_API_KEY"):
            provider = "openai"

    model = os.environ.get("AI_SDLC_LLM_MODEL")
    missing: list[str] = []
    if provider not in {"openai", "vllm"}:
        missing.append("AI_SDLC_LLM_PROVIDER")
    if not model:
        missing.append("AI_SDLC_LLM_MODEL")

    key_set = False
    base_url_set = False
    if provider == "openai":
        key_set = bool(os.environ.get("OPENAI_API_KEY"))
        if not key_set:
            missing.append("OPENAI_API_KEY")
    elif provider == "vllm":
        base_url_set = bool(os.environ.get("AI_SDLC_LLM_BASE_URL"))
        key_set = bool(os.environ.get("AI_SDLC_LLM_API_KEY"))
        if not base_url_set:
            missing.append("AI_SDLC_LLM_BASE_URL")

    report = {
        "provider": provider,
        "ready": not missing,
        "model": model,
        "api_key_set": key_set,
        "base_url_set": base_url_set,
        "missing": missing,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.require_ready and missing:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
