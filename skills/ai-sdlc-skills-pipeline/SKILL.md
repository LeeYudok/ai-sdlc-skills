---
name: ai-sdlc-skills-pipeline
description: Run an evidence-based AI SDLC pipeline for bug fixes, features, and changes in an existing repository, from analysis and BA documentation through implementation, QA, local deployment, and production release readiness. Use when a user asks to fix or build something end to end.
---

# AI SDLC Pipeline

Turn the user's request into a traceable change in the current repository. Preserve the repository's own instructions and authorization boundaries. Do not deploy, merge, trade, send messages, or mutate production unless the user separately authorizes that action.

Read [references/artifact-contract.md](references/artifact-contract.md) before starting. When an optional model-backed analysis or review tool is needed, also read [references/model-providers.md](references/model-providers.md). Use the bundled state script so interrupted work can resume from recorded evidence.

## Pipeline

0. If the repository requires issue-first work, or the user hands over an issue number or a spec document, run `ai-sdlc-skills-issue` first. It yields the issue, the `<type>/issue-N-<slug>` branch, and the run slug `issue-N-<slug>` — use that slug in step 1 instead of inventing one.
1. Create a stable kebab-case run slug (skip if step 0 supplied one). If its state already exists, inspect and resume it; otherwise initialize the run:
   `python3 <this-skill-dir>/scripts/pipeline_state.py init --root <repo> --run <slug> --request <request>`.
2. Run `ai-sdlc-skills-analyze`. Advance to `analyzed` only when the repository evidence is current.
3. Run `ai-sdlc-skills-evidence` to cross-check source inspection with any approved graph, RAG, and review tools. Advance to `evidence_collected` only when gaps and contradictions are recorded.
4. Run `ai-sdlc-skills-ba`. Advance to `ba_ready` only when the bug/change behavior and business acceptance criteria are implementable.
5. Run `ai-sdlc-skills-impact`. Advance to `impact_assessed` only when direct, indirect, operational, and compatibility effects are covered. Feed material findings back into the BA document.
6. Run `ai-sdlc-skills-specify`. Advance to `specified` only when acceptance criteria are testable and no blocking decision remains.
7. Run `ai-sdlc-skills-implement`. Advance to `implemented` only when the implementation matches the approved scope and focused checks pass.
8. Run `ai-sdlc-skills-verify` as the QA gate. Fix and re-run failed checks up to two times when the fix stays within scope. Otherwise block the run with evidence. Advance to `verified` only on a passing verdict.
9. Run `ai-sdlc-skills-local-deploy`. Advance to `local_deployed` only after an isolated local build, health check, and changed-flow smoke test pass.
10. Run `ai-sdlc-skills-release`. Advance to `release_ready` only when backward compatibility, rollout, monitoring, abort thresholds, and rollback are evidenced. `release_ready` means a reviewed plan exists; it is not authorization to deploy.
11. Advance to `complete` and write the completion report. It states, or marks `N/A` with a reason: requirements delivered and explicitly excluded; impact on code, data, external services, and operational configuration; verifications run and the result of independent review; local deployment and live-check results; rollback/recovery procedure and residual risk; follow-up issues with their actual state in the tracker. If any required stage did not pass, do not report completion — report the stage that is stuck, the evidence that is missing, and the next action.

Invoke a named phase skill when available. If it is unavailable, perform that phase using the same artifact contract rather than silently skipping it.

After `complete`, `ai-sdlc-skills-commit` and `ai-sdlc-skills-pr` are optional, user-triggered delivery steps — not part of the gated stage machine. Run `ai-sdlc-skills-commit` only when the user asks to commit the change (local-only, never pushes on its own), and `ai-sdlc-skills-pr` only when the user asks to open it for review (pushes the branch and drafts the PR/MR, never merges).

## Session and parallel work

Treat the context budget as a signal, not a percentage: hand off when evidence already collected is
being lost, when the same content is read repeatedly, or when the room left is not enough to implement
and verify what remains. The ~40-50% mark is a reminder to check those signals, not the rule itself.
Read a small file whole; read a large one by symbol or line range. For a complex change, an exploration
session may end by recording target files, symbols, and unverified risks, leaving implementation to a
fresh session that starts from that record.

Split work across agents by what they would touch, not by what the modules are called: overlapping
files, shared contracts, generated artifacts, migrations, and deployment order all make two tasks
sequential even when they sit in different modules. Give each agent an explicit set of owned files,
isolate conflicting work in separate worktrees, and run contract and regression checks before
integrating. Whoever integrates should not be the agent that wrote the change.

## Gates

- Never write product code before analysis, impact, and specification artifacts pass their gates.
- Block and ask the user when a missing product decision materially changes behavior, safety, cost, or compatibility.
- Treat destructive migrations, incompatible APIs/events, unbounded jobs, absent rollback, and unobservable rollouts as release blockers.
- For money movement, automated trading, credentials, or production data, require explicit authorization immediately before the external or irreversible action.
- Do not claim zero downtime or production safety from unit tests alone. Base the release verdict on concrete architecture and operational evidence.

Use `pipeline_state.py block` with a concise reason whenever a gate cannot pass. Do not mark later stages complete to make the run appear successful.
