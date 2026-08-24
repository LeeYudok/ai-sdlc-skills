#!/usr/bin/env bash
# PreToolUse(Bash) hook. Runs only when the command is a `git commit`;
# blocks (exit 2) if a .env-type file is staged. Wired in .claude/settings.json.
set -euo pipefail

input=$(cat 2>/dev/null || true)
case "$input" in
  *"git commit"*|*"git -C"*commit*) ;;
  *) exit 0 ;;
esac

repo="${CLAUDE_PROJECT_DIR:-$PWD}"
staged=$(git -C "$repo" diff --cached --name-only 2>/dev/null || true)
if printf '%s\n' "$staged" | grep -qE '(^|/)\.env($|\.)'; then
  echo "Blocked: a .env-type file is staged. Commit is not allowed." >&2
  exit 2
fi
exit 0
