---
name: ai-sdlc-skills-impact
description: Determine the complete change impact of a proposed feature across code, data, interfaces, operations, security, performance, and dependent systems. Use before approving a specification or release approach in an existing system.
---

# Full Impact Assessment

Start from the repository analysis, evidence ledger, and BA document, then verify important claims in code. Resolve or explicitly block on contradictions between graph/RAG results, source inspection, and tests. Write `.ai-sdlc/runs/<run>/impact-analysis.md`.

Cover each applicable surface:

- callers, callees, shared libraries, UI, API, workers, batches, schedules, and admin paths;
- schema, existing rows, migrations, indexes, retention, backups, and rollback data needs;
- public/internal API and event compatibility, ordering, idempotency, retry, and version skew;
- authentication, authorization, secrets, audit trails, privacy, abuse, and financial risk;
- latency, throughput, concurrency, locks, resource usage, rate limits, and failure amplification;
- configuration, feature flags, environments, CI/CD, observability, alerts, runbooks, and support;
- dependent services, clients, teams, and deployment ordering.

When the change touches persistent data, also read [references/data-change.md](references/data-change.md).

For every impact item record evidence, severity, likelihood, affected component, mitigation, validation method, owner when known, and whether it blocks implementation or release. Include both “change” and “no impact, because …” conclusions for high-risk surfaces so omissions are visible.

End with an impact gate verdict: `PASS`, `BLOCKED`, or `PASS_WITH_RESIDUAL_RISK`. `BLOCKED` requires explicit unresolved questions or missing evidence. Do not reduce “whole-system impact” to a list of files.

Record that verdict as a machine-readable gate line at the end of `impact-analysis.md` — `Verdict: PASS`, `Verdict: PASS_WITH_RESIDUAL_RISK`, or `Verdict: BLOCKED`. `pipeline_state.py` reads this line to allow or block the `impact_assessed` transition; the last such line in the file wins.
