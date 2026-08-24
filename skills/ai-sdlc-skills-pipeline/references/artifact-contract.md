# Pipeline artifact contract

All paths are relative to the consumer repository.

```text
.ai-sdlc/
├── context/
│   └── repository.md
└── runs/<run-slug>/
    ├── state.json
    ├── request.md
    ├── repository-analysis.md
    ├── evidence-ledger.md
    ├── ba.md
    ├── impact-analysis.md
    ├── feature-spec.md
    ├── implementation-plan.md
    ├── implementation-report.md
    ├── qa-report.md
    ├── local-deploy-report.md
    ├── release-plan.md
    └── HANDOFF.md          (optional; ai-sdlc-skills-handoff)
```

## Invariants

- `request.md` preserves the user's original request verbatim and records later clarifications separately.
- Material claims cite repository paths, symbols, commands, or observable runtime evidence.
- Facts, inferences, assumptions, unknowns, and accepted risks are visibly distinct.
- Requirements use stable `BR-*` and `AC-*` identifiers from specification through verification.
- A missing artifact or non-passing gate blocks later phases.
- Artifacts may be updated when new evidence invalidates them, but the change and reason must be recorded.
- Generated documentation belongs to the feature branch. Do not include credentials, personal data, or production payloads.

## Resume rule

If `HANDOFF.md` exists in the run directory, read it first and follow its resume procedure before anything else.
Read `state.json`, verify the current commit and dirty worktree, and revalidate any completed phase affected by code changes since its recorded update. Resume at the first incomplete or invalidated phase.
