---
name: ai-sdlc-skills-verify
description: Verify an implemented change against acceptance criteria and repository quality gates, including regressions, failure behavior, compatibility, and operational signals. Use after implementation and before release readiness.
---

# Verification

Build a verification matrix from every `AC-*`, business rule, and material impact item. Run the repository's real commands; do not substitute file inspection for executable checks when checks are available.

When OpenCodeReview or another approved independent reviewer is available, review the feature diff and reconcile its findings with the verification matrix. Never let an LLM review replace deterministic build, test, security, or migration checks.

Detect the repository's primary language from its manifest (`go.mod`, `pyproject.toml`/`requirements.txt`/`setup.py`, `package.json` with TypeScript, or `Cargo.toml`) and read the matching guide under [references/reviews/](references/reviews/) before finalizing the matrix; a polyglot repository loads every guide whose manifest is present. Check its criteria in addition to the acceptance criteria.

When the change alters a user-facing interface, also read [references/reviews/ui.md](references/reviews/ui.md).

Independence: perform verification in a fresh context or session separate from the one that implemented the change whenever that is available to you. When the same session did both, record in `qa-report.md` that verification was self-reviewed rather than independent — this is weaker evidence and is a residual risk, not a gap to silently accept.

Cover as applicable:

- focused unit/component tests and the relevant regression suite;
- integration, contract, migration, event, batch, and end-to-end behavior;
- contract tests at the boundaries the change crosses, asserting the agreed shape rather than the implementation behind it;
- characterization tests pinning current behavior where the change touches legacy code with no coverage, prioritized by risk rather than applied everywhere;
- authorization and misuse cases;
- concurrency, idempotency, retry, timeout, partial failure, and recovery;
- old/new version coexistence and backward compatibility;
- build, type, lint, static/security checks, and performance thresholds;
- logs, metrics, traces, health checks, and alert signals required for rollout.

Write `.ai-sdlc/runs/<run>/qa-report.md`. For every `AC-*` record command or procedure, result, and evidence. Distinguish `PASS`, `FAIL`, and `NOT_RUN`; a skipped or unavailable check is never a pass. Include environment limitations and residual risks.

Return a `PASS` verdict only when all required checks pass. A failure may be fixed and re-run when the change remains in scope; otherwise return `BLOCKED` with the shortest actionable explanation. A narrowed, dependency-derived test selection is acceptable only when the dependency evidence is trustworthy for the changed area; a change to a shared module or contract runs the full regression suite. A green CI run is one piece of evidence, not a completion criterion.

Record the overall QA verdict as a machine-readable gate line at the end of `qa-report.md` — `Verdict: PASS`, `Verdict: FAIL`, `Verdict: NOT_RUN`, or `Verdict: BLOCKED`. `pipeline_state.py` reads this line to allow or block the `verified` transition, and only `PASS` passes; the last such line in the file wins.
