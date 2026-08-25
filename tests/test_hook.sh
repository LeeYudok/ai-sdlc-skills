#!/usr/bin/env bash
# .claude/hooks/pre-commit.sh 회귀 테스트 — 훅이 "실제 커밋 대상 저장소" 의
# index 를 검사하고, 대상을 안전하게 판별할 수 없으면 fail closed 하는지 검증한다 (#25).
set -uo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
HOOK="$ROOT/.claude/hooks/pre-commit.sh"
SANDBOX="$(mktemp -d /tmp/ai-sdlc-hook-test.XXXXXX)"
trap 'rm -rf "$SANDBOX"' EXIT

failures=0

new_repo() { # new_repo <name>
  local dir="$SANDBOX/$1"
  mkdir -p "$dir"
  git -C "$dir" init -q
  git -C "$dir" config user.email test@example.com
  git -C "$dir" config user.name test
  printf '%s\n' "$dir"
}

stage_env() { # stage_env <repo>
  printf 'SECRET=x\n' > "$1/.env"
  git -C "$1" add .env
}

stage_clean() { # stage_clean <repo>
  printf 'ok\n' > "$1/README.md"
  git -C "$1" add README.md
}

# run <expected-exit> <label> <command-line> [project-dir]
run() {
  local expected=$1 label=$2 command=$3 project="${4:-$SANDBOX}"
  local payload actual out
  payload="{\"tool_input\":{\"command\":\"$command\"}}"
  out=$(printf '%s' "$payload" | CLAUDE_PROJECT_DIR="$project" bash "$HOOK" 2>&1)
  actual=$?
  if [ "$actual" != "$expected" ]; then
    echo "hook test FAIL: $label — expected exit $expected, got $actual ${out:+($out)}" >&2
    failures=$((failures + 1))
  fi
}

# --- 형태 1: 일반 `git commit` (대상 = CLAUDE_PROJECT_DIR) -------------------
plain_dirty="$(new_repo plain-dirty)"; stage_env "$plain_dirty"
plain_clean="$(new_repo plain-clean)"; stage_clean "$plain_clean"
run 2 "plain git commit / .env staged" 'git commit -m test' "$plain_dirty"
run 0 "plain git commit / clean index" 'git commit -m test' "$plain_clean"

# --- 형태 2: `git -C <repo> commit` (대상 = -C 인자) -------------------------
c_dirty="$(new_repo c-dirty)"; stage_env "$c_dirty"
c_clean="$(new_repo c-clean)"; stage_clean "$c_clean"
run 2 "git -C dirty commit (project dir clean)" "git -C $c_dirty commit -m test" "$plain_clean"
run 0 "git -C clean commit (project dir dirty)" "git -C $c_clean commit -m test" "$plain_dirty"
run 2 "git -C<path> (sticky) dirty commit" "git -C$c_dirty commit -m test" "$plain_clean"
run 2 "git -C relative dirty commit" "git -C c-dirty commit -m test" "$SANDBOX"

# --- 형태 3: `cd <repo> && git commit` --------------------------------------
cd_dirty="$(new_repo cd-dirty)"; stage_env "$cd_dirty"
cd_clean="$(new_repo cd-clean)"; stage_clean "$cd_clean"
run 2 "cd dirty && git commit" "cd $cd_dirty && git commit -m test" "$plain_clean"
run 0 "cd clean && git commit" "cd $cd_clean && git commit -m test" "$plain_dirty"
run 2 "cd relative dirty && git commit" "cd cd-dirty && git commit -m test" "$SANDBOX"
run 2 "( cd dirty && git commit )" "( cd $cd_dirty && git commit -m test )" "$plain_clean"

# --- `-a` 는 tracked 수정본까지 스테이징한다 --------------------------------
amend_repo="$(new_repo auto-stage)"
printf 'SECRET=1\n' > "$amend_repo/.env"
git -C "$amend_repo" add .env
git -C "$amend_repo" commit -qm "seed"
printf 'SECRET=2\n' > "$amend_repo/.env"
run 2 "git commit -am (tracked .env modified)" 'git commit -am test' "$amend_repo"

# --- fail closed: 대상을 안전하게 판별할 수 없는 경우 -----------------------
run 2 "cd to a missing directory" "cd $SANDBOX/does-not-exist && git commit -m test" "$plain_clean"
run 2 "command substitution in -C" 'git -C $(cat /tmp/p) commit -m test' "$plain_clean"
run 2 "variable in cd target" 'cd $TARGET && git commit -m test' "$plain_clean"
run 2 "--git-dir relocates the index" "git --git-dir=$c_dirty/.git commit -m test" "$plain_clean"
run 2 "env prefix can relocate the index" "GIT_DIR=$c_dirty/.git git commit -m test" "$plain_clean"
run 2 "commit target is not a repository" "cd $SANDBOX && git commit -m test" "$plain_clean"
# 페이로드에 command 필드가 없으면(형식 변경·파싱 실패) 커밋으로 보이는 입력은 막는다.
out=$(printf '%s' '{"tool_input":{"cmd":"git commit -m x"}}' | CLAUDE_PROJECT_DIR="$plain_clean" bash "$HOOK" 2>&1)
if [ "$?" != 2 ]; then
  echo "hook test FAIL: payload without a command field must fail closed" >&2
  failures=$((failures + 1))
fi

# --- 커밋이 아닌 명령은 통과 -----------------------------------------------
run 0 "git status" 'git status' "$plain_dirty"
run 0 "quoted literal, not a commit" 'echo \"git commit\"' "$plain_dirty"
run 0 "unrelated command" 'ls -la' "$plain_dirty"
run 0 "payload without any command" 'echo hello' "$plain_dirty"

if [ "$failures" != 0 ]; then
  echo "hook tests failed: $failures" >&2
  exit 1
fi
echo "pre-commit hook tests ok"
