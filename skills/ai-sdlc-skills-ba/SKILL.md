---
name: ai-sdlc-skills-ba
description: Produce a concise business-analysis document for a bug fix or feature request in an existing system, grounded in repository and user evidence. Use before technical specification and coding.
---

# Business Analysis

Classify the request as `BUG_FIX`, `FEATURE`, or `CHANGE`, then read the request, repository analysis, and evidence ledger. Use [references/ba-template.md](references/ba-template.md) and write `.ai-sdlc/runs/<run>/ba.md`.

For a bug, establish reproducible actual behavior, expected behavior, affected users/processes, severity, frequency, trigger conditions, workaround, likely regression range, and root-cause evidence. Do not present an unverified hypothesis as the cause.

For a feature or change, document actors, business outcome, current and target process, business rules, input/output, exceptions, authorization, audit needs, and operational constraints.

For every type, define scope, exclusions, assumptions, dependencies, data effects, availability expectations, numbered business rules (`BR-*`), and objectively testable acceptance criteria (`AC-*`). Link each material statement to user input or repository evidence.

Mark the document `READY` only when implementation can proceed without inventing a product decision. Mark it `BLOCKED` and ask a focused question when behavior, money movement, data ownership, authorization, or compatibility is materially ambiguous. Ask only where interpretations would diverge in data, security, or operational outcome. Anything decidable from code, documentation, schema, configuration, or history is investigated, not asked — an avoidable question spends the user's attention on evidence you could have collected.

Record that decision as a machine-readable gate verdict line at the end of `ba.md` — `Verdict: READY` or `Verdict: BLOCKED`. `pipeline_state.py` reads this line to allow or block the `ba_ready` transition; the last such line in the file wins.
