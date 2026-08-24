---
name: ai-sdlc-skills-implement
description: Implement an approved feature specification in an existing repository with minimal compatible changes and requirement traceability. Use only after analysis, impact, and specification gates have passed.
---

# Specification-Driven Implementation

Confirm the specification is `READY` and the impact gate is not blocked. Follow repository-local instructions and preserve unrelated changes.

Implement only the approved scope. Keep old and new versions able to coexist during rollout. For risky behavior, prefer feature flags, idempotent operations, bounded retries, explicit timeouts, and reversible steps when supported by the system.

For database changes use an expand/migrate/contract sequence: add backward-compatible structures, deploy code that tolerates both forms, migrate safely, and defer destructive cleanup until old code is gone and rollback is no longer needed. Never combine an irreversible contract step with the first feature deployment.

Add or update tests for each applicable `AC-*`. Run focused checks during implementation. Record `.ai-sdlc/runs/<run>/implementation-report.md` with changed files, design choices, `AC-*` mapping, migrations/flags, commands run, deviations, and remaining work.

Stop if implementation reveals a material specification or impact error. Update the earlier artifact and re-pass its gate instead of silently changing behavior.
