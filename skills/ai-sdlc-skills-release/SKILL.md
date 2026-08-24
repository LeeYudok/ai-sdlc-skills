---
name: ai-sdlc-skills-release
description: Assess and document production release readiness for a verified change, emphasizing availability, compatibility, progressive rollout, observability, abort criteria, and rollback. Use before deploying a change to an operating system.
---

# Production Release Readiness

This skill prepares and validates a release plan. It does not authorize or execute deployment.

Read the impact, specification, implementation, and verification artifacts. Inspect the repository's actual delivery configuration and write `.ai-sdlc/runs/<run>/release-plan.md` containing:

- prerequisites, artifacts, configuration, secrets, migrations, and dependency ordering;
- backward/forward compatibility across mixed application versions;
- pre-deploy checks and a baseline of current service health;
- progressive rollout steps such as disabled flag, canary, small cohort, then expansion;
- health checks and user-visible synthetic checks at every step;
- metrics, logs, traces, dashboards, alert owners, and observation windows;
- numeric abort thresholds where the system provides usable baselines;
- rollback procedure, rollback time objective, data reconciliation, and verification;
- post-deploy checks, ownership, communication, and deferred cleanup.

Block release readiness when any applicable condition holds:

- destructive or locking migration can make the service unavailable;
- old and new versions cannot coexist during rolling deployment;
- rollback is untested, impossible, or would corrupt/lose accepted data;
- the feature cannot be disabled or isolated despite material risk;
- health cannot be observed before users detect failure;
- capacity, third-party limits, or failure amplification remain unbounded;
- required verification is failed or not run.

Use `READY`, `READY_WITH_EXPLICIT_RISK_ACCEPTANCE`, or `BLOCKED`. Never describe deployment as risk-free or guaranteed. `READY_WITH_EXPLICIT_RISK_ACCEPTANCE` requires the user or accountable operator to accept the listed residual risk before deployment.
