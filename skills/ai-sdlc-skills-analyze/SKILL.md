---
name: ai-sdlc-skills-analyze
description: Analyze an existing repository as evidence for a requested feature, including architecture, conventions, runtime paths, data flows, tests, delivery tooling, and relevant constraints. Use before specifying or implementing a non-trivial change.
---

# Repository Analysis

Inspect before editing. Read all applicable repository instructions, then locate the feature's entry points using fast search and follow the runtime path through interfaces, domain logic, persistence, integrations, and tests.

Write `.ai-sdlc/runs/<run>/repository-analysis.md` with:

- analyzed commit and dirty-worktree status;
- languages, frameworks, package/build tools, and deploy topology evidenced by files;
- relevant components and their responsibilities;
- module/domain boundaries, their public interfaces, and the contracts (API, event, schema) crossing them, with owners where the repository records them;
- boundary weaknesses found while tracing: cyclic dependencies, hidden shared state, and modules that everything depends on;
- request-specific call/data flow with exact file paths and symbols;
- persistence, external services, queues, schedules, flags, configuration, and secrets boundaries;
- existing tests and executable verification commands;
- repository conventions and constraints that affect the change;
- facts, inferences, unknowns, and blocking unknowns clearly separated — every unknown states how it would be verified, and is never replaced by a plausible guess.

Also update `.ai-sdlc/context/repository.md` only with reusable facts, stamped with the generation time, the revision it was derived from, and who maintains it. Do not copy transient feature assumptions into shared context. Record evidence paths for every material conclusion. If the repository state changed since a prior analysis, revalidate affected facts instead of trusting stale documentation. A file that exists is not a file that is current — before relying on a shared context document, check its stamp against the current revision and re-derive the parts the change touches.

Where boundaries are weak, do not open with a restructuring proposal. Pin the current behavior with tests or observability first, so a later change has something to be judged against.

This phase is read-only except for its analysis artifacts. Do not implement the feature.
