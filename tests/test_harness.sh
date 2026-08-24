#!/usr/bin/env bash
# 하네스 구성 불변식 — "동작하는 최소" 상태가 유지되는지 검사한다 (#20).
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
fail() { echo "harness: $*" >&2; exit 1; }

# 1. CLAUDE.md 는 AGENTS.md 로의 위임 한 줄
[ "$(grep -c '' "$ROOT/CLAUDE.md")" = "1" ] && grep -qx '@AGENTS.md' "$ROOT/CLAUDE.md" \
  || fail "CLAUDE.md must be exactly '@AGENTS.md'"

# 2. AGENTS.md 는 자체 완결 — 하네스 전용 import·템플릿 플레이스홀더 금지
grep -nE '^@' "$ROOT/AGENTS.md" && fail "AGENTS.md contains an @ import"
grep -nE '<!--\s*[A-Z_ ]+\s*-->' "$ROOT/AGENTS.md" && fail "AGENTS.md contains a template placeholder"

# 3. hooks: 존재하는 훅은 전부 settings.json 에 배선되고 실행 가능
SETTINGS="$ROOT/.claude/settings.json"
for hook in "$ROOT"/.claude/hooks/*; do
  [ -e "$hook" ] || continue
  [ -x "$hook" ] || fail "$(basename "$hook") is not executable"
  grep -q "hooks/$(basename "$hook")" "$SETTINGS" || fail "$(basename "$hook") is not wired in settings.json"
done
python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$SETTINGS" || fail "settings.json is not valid JSON"

# 4. rules: 항상 로드되는 common/forge 외에는 paths 스코프 필수
for rule in "$ROOT"/.claude/rules/*.md; do
  case "$(basename "$rule")" in common.md|forge.md) continue ;; esac
  head -1 "$rule" | grep -qx -- '---' && sed -n '2,/^---$/p' "$rule" | grep -q '^paths:' \
    || fail "$(basename "$rule") lacks a paths: frontmatter scope"
done

# 5. memory: 타입 접두 + frontmatter + 인덱스 양방향 일치
MEM="$ROOT/.claude/memory"
for f in "$MEM"/*.md; do
  b="$(basename "$f")"
  case "$b" in MEMORY.md|README.md) continue ;; esac
  echo "$b" | grep -qE '^(project|feedback|reference|user)_' || fail "memory $b lacks a type prefix"
  head -1 "$f" | grep -qx -- '---' || fail "memory $b lacks frontmatter"
  grep -q "($b)" "$MEM/MEMORY.md" || fail "memory $b is not indexed in MEMORY.md"
done
{ grep -oE '\([a-z_]+\.md\)' "$MEM/MEMORY.md" || true; } | tr -d '()' | while read -r linked; do
  [ -f "$MEM/$linked" ] || fail "MEMORY.md indexes missing file $linked"
done

echo "harness invariants ok"
