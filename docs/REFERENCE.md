# Quick reference

One row per skill: when to invoke it, what it reads, and what it writes under `.ai-sdlc/runs/<run>/`. See [artifact-contract.md](../skills/ai-sdlc-skills-pipeline/references/artifact-contract.md) for the shared run-state conventions.

## Pipeline

| Skill | Use when | Writes |
|---|---|---|
| `ai-sdlc-skills-pipeline` | End-to-end request from a user, start to finish | drives the run state, delegates to every skill below |
| `ai-sdlc-skills-issue` | At the start of an issue-first change: issue number or spec path → forge issue, `<type>/issue-N-<slug>` branch, run slug | run `state.json` (init) — no artifact of its own |
| `ai-sdlc-skills-analyze` | Before specifying or implementing a non-trivial change | `repository-analysis.md` |
| `ai-sdlc-skills-evidence` | After analysis, to cross-check with graph/RAG/review tools | `evidence-ledger.md` |
| `ai-sdlc-skills-ba` | Before technical specification and coding | `ba.md` |
| `ai-sdlc-skills-impact` | Before approving a specification or release approach | `impact-analysis.md` |
| `ai-sdlc-skills-specify` | After analysis/impact, before product code changes | `feature-spec.md`, `implementation-plan.md` |
| `ai-sdlc-skills-implement` | After analysis, impact, and spec gates pass | `implementation-report.md` + code changes |
| `ai-sdlc-skills-verify` | After implementation, before release readiness | `qa-report.md` |
| `ai-sdlc-skills-local-deploy` | After QA passes | `local-deploy-report.md` |
| `ai-sdlc-skills-release` | Before deploying a verified change | `release-plan.md` |

## Delivery (optional, user-triggered, outside the gated stage machine)

| Skill | Use when | Effect |
|---|---|---|
| `ai-sdlc-skills-commit` | The user asks to commit the change | one or more local conventional commits; never pushes |
| `ai-sdlc-skills-pr` | The user asks to open the change for review | pushes the branch if needed, opens a PR/MR; never merges |
| `ai-sdlc-skills-handoff` | Context usage nears ~40–50%, or the user asks to hand off / resume | `HANDOFF.md` state snapshot (goal, state, decisions, remaining work, traps, resume command, files to load); `check` blocks on unfilled markers |

## Stage gate order

```text
initialized → analyzed → evidence_collected → ba_ready → impact_assessed →
specified → implemented → verified → local_deployed → release_ready → complete
```

Each transition is validated by `skills/ai-sdlc-skills-pipeline/scripts/pipeline_state.py` against the required artifact for that stage — see `REQUIRED_ARTIFACTS` in that script for the authoritative mapping.
