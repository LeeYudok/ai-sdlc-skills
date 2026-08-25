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
- A missing artifact or non-passing gate blocks later phases; `pipeline_state.py advance` enforces this by reading each required artifact's verdict line (see **Gate verdicts**).
- Artifacts may be updated when new evidence invalidates them, but the change and reason must be recorded.
- Generated documentation belongs to the feature branch. Do not include credentials, personal data, or production payloads.

## Gate verdicts

Every required artifact carries one machine-readable verdict line so `pipeline_state.py advance`
can enforce the gate instead of trusting prose:

```text
Verdict: PASS
```

Rules:

- The line starts at column 1, is exactly `Verdict: <TOKEN>`, and the token is upper-case `A-Z_`.
- When an artifact contains several such lines, the **last** one is authoritative — a verdict may be
  restated after an update, and vocabulary quoted earlier in the document never wins.
- A required artifact with no verdict line is treated as `NOT_RUN` and blocks the transition.
- `BLOCKED`, `FAIL`, `NOT_RUN`, and any token outside the stage's allowed set block the transition.
  Use `pipeline_state.py block` to record why.

Allowed verdicts per stage (authoritative mapping: `ALLOWED_VERDICTS` in
`../scripts/pipeline_state.py`):

| Stage | Required artifact(s) | Allowed verdicts | Residual risk |
|---|---|---|---|
| `analyzed` | `repository-analysis.md` | `PASS` | not accepted — a blocking unknown is `BLOCKED` |
| `evidence_collected` | `evidence-ledger.md` | `PASS` | not accepted — an unresolved contradiction is `BLOCKED` |
| `ba_ready` | `ba.md` | `READY` | not accepted — an open product decision is `BLOCKED` |
| `impact_assessed` | `impact-analysis.md` | `PASS`, `PASS_WITH_RESIDUAL_RISK` | accepted when the risk is listed with mitigation and validation |
| `specified` | `feature-spec.md`, `implementation-plan.md` | `READY` (both) | not accepted — an unresolved blocking decision is `BLOCKED` |
| `implemented` | `implementation-report.md` | `PASS` | not accepted — out-of-scope work required is `BLOCKED` |
| `verified` | `qa-report.md` | `PASS` | not accepted — a skipped or unavailable check is `NOT_RUN`, never a pass |
| `local_deployed` | `local-deploy-report.md` | `PASS` | not accepted — missing local infrastructure is `BLOCKED` |
| `release_ready` | `release-plan.md` | `READY`, `READY_WITH_EXPLICIT_RISK_ACCEPTANCE` | accepted only with explicit user/operator acceptance of the listed risk |

`complete` has no required artifact of its own; it is reachable only because every earlier gate passed.
Each `advance` records the verdicts it read in `state.json` under `history[].artifact_verdicts`.

## Resume rule

If `HANDOFF.md` exists in the run directory, read it first and follow its resume procedure before anything else.
Read `state.json`, verify the current commit and dirty worktree, and revalidate any completed phase affected by code changes since its recorded update. Resume at the first incomplete or invalidated phase.
