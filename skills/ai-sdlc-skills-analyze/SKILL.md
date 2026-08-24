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
- request-specific call/data flow with exact file paths and symbols;
- persistence, external services, queues, schedules, flags, configuration, and secrets boundaries;
- existing tests and executable verification commands;
- repository conventions and constraints that affect the change;
- facts, inferences, unknowns, and blocking unknowns clearly separated.

Also update `.ai-sdlc/context/repository.md` only with reusable facts. Do not copy transient feature assumptions into shared context. Record evidence paths for every material conclusion. If the repository state changed since a prior analysis, revalidate affected facts instead of trusting stale documentation.

This phase is read-only except for its analysis artifacts. Do not implement the feature.
