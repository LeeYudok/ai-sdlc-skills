---
name: ai-sdlc-skills-specify
description: Convert a feature request plus repository and impact evidence into an implementable, testable change specification. Use after repository analysis and before product code changes.
---

# Change Specification

Read the run's request, BA document, repository analysis, evidence ledger, and impact analysis. Write `.ai-sdlc/runs/<run>/feature-spec.md` and `.ai-sdlc/runs/<run>/implementation-plan.md`.

The feature specification must include:

- problem, user outcome, in-scope and out-of-scope behavior;
- numbered business rules (`BR-*`) and acceptance criteria (`AC-*`);
- normal, boundary, failure, recovery, authorization, and concurrency behavior;
- data/API/event changes and backward-compatibility requirements;
- non-functional requirements, including availability and observability;
- assumptions, resolved decisions, unresolved decisions, and residual risks.

The implementation plan maps each `AC-*` to affected components, intended changes, migration/flag strategy, and verification. Prefer incremental changes that remain safe while old and new versions coexist.

Do not invent a material product decision merely to keep the pipeline moving. Mark the specification `READY` only when all blocking decisions are resolved and every acceptance criterion is objectively verifiable; otherwise mark it `BLOCKED` and ask the smallest necessary question.
