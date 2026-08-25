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
- assumptions, resolved decisions, unresolved decisions, and residual risks;
- for each risk-bearing `AC-*`, how failure would be detected early and how the change is rolled back or recovered — prevention alone is not a complete acceptance criterion.

The implementation plan maps each `AC-*` to affected components, intended changes, migration/flag strategy, and verification, and additionally states: the modules this change owns; the contracts and recorded decisions to read before starting; areas that must not change; the constraints that apply; and the executable command that demonstrates each acceptance criterion. If implementation turns out to require a change outside the owned modules, that is a stop-and-re-plan condition, not a judgement call at the keyboard. Prefer incremental changes that remain safe while old and new versions coexist.

For a request to modernize or improve an existing interface, the default interpretation is visual and usability change only: authentication methods, routes, API contracts, guards, and post-login redirects stay as they are. Adding or removing an authentication method, or changing who can reach a route, is a separate decision to raise, not part of a redesign.

Do not invent a material product decision merely to keep the pipeline moving. Mark the specification `READY` only when all blocking decisions are resolved and every acceptance criterion is objectively verifiable; otherwise mark it `BLOCKED` and ask the smallest necessary question.

Record that decision as a machine-readable gate verdict line at the end of **both** `feature-spec.md` and `implementation-plan.md` — `Verdict: READY` or `Verdict: BLOCKED`. `pipeline_state.py` reads these lines to allow or block the `specified` transition; the last such line in each file wins.
