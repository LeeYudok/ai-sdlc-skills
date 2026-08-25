#!/usr/bin/env bash
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

"$ROOT/tests/test_harness.sh"

for skill in "$ROOT"/skills/ai-sdlc-skills-*; do
  python3 "$ROOT/tests/validate_skill.py" "$skill"
done

python3 -m py_compile "$ROOT/skills/ai-sdlc-skills-pipeline/scripts/pipeline_state.py"
python3 -m py_compile "$ROOT/skills/ai-sdlc-skills-pipeline/scripts/provider_config.py"
python3 -m py_compile "$ROOT/skills/ai-sdlc-skills-evidence/scripts/detect_tools.py"
python3 -m py_compile "$ROOT/skills/ai-sdlc-skills-handoff/scripts/handoff.py"

SANDBOX="$(mktemp -d /tmp/ai-sdlc-skills-test.XXXXXX)"
trap 'rm -rf "$SANDBOX"' EXIT
git -C "$SANDBOX" init -q

"$ROOT/bin/install.sh" "$SANDBOX" --mode copy >/dev/null
expected="$(find "$ROOT/skills" -mindepth 1 -maxdepth 1 -type d -name 'ai-sdlc-skills-*' | wc -l | tr -d ' ')"
actual="$(find "$SANDBOX/.agents/skills" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')"
[ "$actual" = "$expected" ] || {
  echo "Expected $expected copied skills, found $actual" >&2
  exit 1
}

PYCACHE_SKILL="$(find "$ROOT/skills" -mindepth 1 -maxdepth 1 -type d -name 'ai-sdlc-skills-*' | head -n 1)"
mkdir -p "$PYCACHE_SKILL/__pycache__"
printf 'bytecode' > "$PYCACHE_SKILL/__pycache__/example.cpython-311.pyc"
printf 'bytecode' > "$PYCACHE_SKILL/example.pyc"
cleanup_pycache_fixture() {
  rm -rf "$PYCACHE_SKILL/__pycache__" "$PYCACHE_SKILL/example.pyc"
}
trap 'cleanup_pycache_fixture; rm -rf "$SANDBOX"' EXIT

PYCACHE_SANDBOX="$(mktemp -d /tmp/ai-sdlc-skills-pycache-test.XXXXXX)"
git -C "$PYCACHE_SANDBOX" init -q
"$ROOT/bin/install.sh" "$PYCACHE_SANDBOX" --mode copy >/dev/null
installed_pycache_skill="$PYCACHE_SANDBOX/.agents/skills/$(basename "$PYCACHE_SKILL")"
if [ -e "$installed_pycache_skill/__pycache__" ]; then
  echo "install.sh copied a __pycache__ directory into the target repository" >&2
  exit 1
fi
if find "$installed_pycache_skill" -name '*.pyc' | grep -q .; then
  echo "install.sh copied a .pyc file into the target repository" >&2
  exit 1
fi
cleanup_pycache_fixture
rm -rf "$PYCACHE_SANDBOX"
trap 'rm -rf "$SANDBOX"' EXIT

STATE_SCRIPT="$ROOT/skills/ai-sdlc-skills-pipeline/scripts/pipeline_state.py"
python3 "$STATE_SCRIPT" init --root "$SANDBOX" --run stock-auto-trading --request "주식자동매매 만들어줘" >/dev/null

if python3 "$STATE_SCRIPT" advance --root "$SANDBOX" --run stock-auto-trading --stage analyzed >/dev/null 2>&1; then
  echo "State machine advanced without the required artifact" >&2
  exit 1
fi

if python3 "$STATE_SCRIPT" advance --root "$SANDBOX" --run stock-auto-trading --stage specified >/dev/null 2>&1; then
  echo "State machine accepted an out-of-order transition" >&2
  exit 1
fi

for artifact in repository-analysis.md evidence-ledger.md ba.md impact-analysis.md feature-spec.md implementation-plan.md implementation-report.md qa-report.md local-deploy-report.md release-plan.md; do
  printf '%s\n' "test evidence" > "$SANDBOX/.ai-sdlc/runs/stock-auto-trading/$artifact"
done

for stage in analyzed evidence_collected ba_ready impact_assessed specified implemented verified local_deployed release_ready complete; do
  python3 "$STATE_SCRIPT" advance --root "$SANDBOX" --run stock-auto-trading --stage "$stage" >/dev/null
done

python3 - "$SANDBOX/.ai-sdlc/runs/stock-auto-trading/state.json" <<'PY'
import json
import sys
from pathlib import Path

state = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert state["status"] == "complete"
assert state["stage"] == "complete"
assert len(state["completed_stages"]) == 11
PY

if "$ROOT/bin/install.sh" "$SANDBOX" --mode copy >/dev/null 2>&1; then
  echo "Installer unexpectedly overwrote existing skills" >&2
  exit 1
fi

LINK_REPO="$SANDBOX/link-repo"
mkdir -p "$LINK_REPO"
git -C "$LINK_REPO" init -q
"$ROOT/bin/install.sh" "$LINK_REPO" --mode link >/dev/null
link_count="$(find "$LINK_REPO/.agents/skills" -mindepth 1 -maxdepth 1 -type l | wc -l | tr -d ' ')"
[ "$link_count" = "$expected" ] || {
  echo "Expected $expected linked skills, found $link_count" >&2
  exit 1
}

python3 "$STATE_SCRIPT" init --root "$SANDBOX" --run blocked-flow --request "blocked flow" >/dev/null
python3 "$STATE_SCRIPT" block --root "$SANDBOX" --run blocked-flow --reason "decision required" >/dev/null
if python3 "$STATE_SCRIPT" advance --root "$SANDBOX" --run blocked-flow --stage analyzed >/dev/null 2>&1; then
  echo "Blocked run unexpectedly advanced" >&2
  exit 1
fi
python3 "$STATE_SCRIPT" resume --root "$SANDBOX" --run blocked-flow >/dev/null

DETECT_SCRIPT="$ROOT/skills/ai-sdlc-skills-evidence/scripts/detect_tools.py"
python3 "$DETECT_SCRIPT" --root "$SANDBOX" > "$SANDBOX/tools.json"
python3 - "$SANDBOX/tools.json" <<'PY'
import json
import sys
from pathlib import Path

tools = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["tools"]
assert set(tools) == {"codegraph", "graphify", "code_graph_rag", "open_code_review"}
PY

PROVIDER_SCRIPT="$ROOT/skills/ai-sdlc-skills-pipeline/scripts/provider_config.py"
openai_report="$(AI_SDLC_LLM_PROVIDER=openai AI_SDLC_LLM_MODEL=test-model OPENAI_API_KEY=test-secret python3 "$PROVIDER_SCRIPT" --require-ready)"
case "$openai_report" in
  *test-secret*)
    echo "Provider resolver exposed an API key" >&2
    exit 1
    ;;
esac

vllm_report="$(AI_SDLC_LLM_PROVIDER=vllm AI_SDLC_LLM_MODEL=test-model AI_SDLC_LLM_BASE_URL=https://internal.invalid python3 "$PROVIDER_SCRIPT" --require-ready)"
case "$vllm_report" in
  *internal.invalid*)
    echo "Provider resolver exposed an internal base URL" >&2
    exit 1
    ;;
esac

HANDOFF_SCRIPT="$ROOT/skills/ai-sdlc-skills-handoff/scripts/handoff.py"
handoff_file="$(python3 "$HANDOFF_SCRIPT" write --root "$SANDBOX" --run stock-auto-trading)"
[ "$handoff_file" = "$(cd "$SANDBOX" && pwd -P)/.ai-sdlc/runs/stock-auto-trading/HANDOFF.md" ] || {
  echo "Handoff written to unexpected path: $handoff_file" >&2
  exit 1
}
grep -q '주식자동매매 만들어줘' "$handoff_file" || { echo "Handoff did not carry the original request" >&2; exit 1; }
grep -q 'Pipeline stage: `complete`' "$handoff_file" || { echo "Handoff did not carry the pipeline stage" >&2; exit 1; }
if python3 "$HANDOFF_SCRIPT" check --root "$SANDBOX" --run stock-auto-trading >/dev/null 2>&1; then
  echo "Handoff check passed with unfilled markers" >&2
  exit 1
fi
sed -i.bak 's/<!-- FILL -->//g' "$handoff_file" && rm -f "$handoff_file.bak"
python3 "$HANDOFF_SCRIPT" check --root "$SANDBOX" --run stock-auto-trading >/dev/null
printf '%s
' 'api_key = abcdefghijklmnop1234' >> "$handoff_file"
if python3 "$HANDOFF_SCRIPT" check --root "$SANDBOX" --run stock-auto-trading >/dev/null 2>&1; then
  echo "Handoff check accepted a secret-looking value" >&2
  exit 1
fi
adhoc_file="$(python3 "$HANDOFF_SCRIPT" write --root "$SANDBOX")"
[ "$adhoc_file" = "$(cd "$SANDBOX" && pwd -P)/.ai-sdlc/HANDOFF.md" ] || { echo "Ad-hoc handoff path wrong: $adhoc_file" >&2; exit 1; }

echo "All tests passed"
