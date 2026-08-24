---
name: ai-sdlc-skills-implement
description: Implement an approved feature specification in an existing repository with minimal compatible changes and requirement traceability. Use only after analysis, impact, and specification gates have passed.
---

# Specification-Driven Implementation

Confirm the specification is `READY` and the impact gate is not blocked. Follow repository-local instructions and preserve unrelated changes.

Implement only the approved scope. Keep old and new versions able to coexist during rollout. For risky behavior, prefer feature flags, idempotent operations, bounded retries, explicit timeouts, and reversible steps when supported by the system.

For database changes use an expand/migrate/contract sequence: add backward-compatible structures, deploy code that tolerates both forms, migrate safely, and defer destructive cleanup until old code is gone and rollback is no longer needed. Never combine an irreversible contract step with the first feature deployment.

Add or update tests for each applicable `AC-*` in a **separate test-authoring pass** from the product-code pass — when the host supports subagents, delegate it to one that has read the spec but not the implementation diff, so tests encode the acceptance criteria rather than the code as written. One test function per `AC-*`/`TC-*`, named after its ID; deterministic (no wall-clock or randomness; external dependencies stubbed); in the repository's existing test framework and style. The test pass must not modify product code, and the product-code pass must not weaken or delete tests to pass. Run focused checks during implementation; the full suite and lint belong to `ai-sdlc-skills-verify`. Record `.ai-sdlc/runs/<run>/implementation-report.md` with changed files, design choices, `AC-*` mapping, migrations/flags, commands run, deviations, and remaining work.

Stop if implementation reveals a material specification or impact error. Update the earlier artifact and re-pass its gate instead of silently changing behavior.
