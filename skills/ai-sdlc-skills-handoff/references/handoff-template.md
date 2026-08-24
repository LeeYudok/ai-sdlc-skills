# HANDOFF.md template

The generator writes this shape. Sections marked *auto* are pre-filled from `state.json` and `git`; the rest carry `<!-- FILL -->` markers that must be replaced by hand. A handoff should read as a state snapshot a stranger can act on in five minutes, not as a conversation summary.

```markdown
# HANDOFF — <run-slug>

Written: YYYY-MM-DD HH:MM:SS | Branch: `feature/issue-N` | HEAD: `<sha>`

## 1. Goal (do not change)                                  *auto from request.md*
- Request: <verbatim original request>
- Pipeline stage: `specified` (completed: initialized → … → specified)
- Acceptance criteria:
  - [ ] AC-1 …

## 2. Current state                                         *auto: git; manual: verification*
- Last commit: `<sha>` <subject>
- Uncommitted changes: <file list or "none">
- Verification status: typecheck ✅ / unit ✅ / e2e ❌ (not run)
- Confirmed working: <only what was actually executed; never inferred>

## 3. Decisions (do not reopen)
| Decision | Reason | Rejected alternative and why |
|---|---|---|
| … | … | … |

## 4. Remaining work (in order)
1. <next concrete action — file path and symbol>
2. …
3. Final: verification command → PR → `Closes #N`

## 5. Traps
- <approach tried and failed, and why>
- <files not to touch, and why>
- <environment specifics: ports, env vars, mocks in place>

## 6. Resume procedure
    git switch feature/issue-N
    <dependency / server start command>
    <one verification command>   # passing proves section 2 is accurate

## 7. Files to load (only these)
- `src/…` — main change site
- `src/….test.ts` — verifies AC
- `AGENTS.md` for the affected directory
```

## Why each section exists

| Section | Failure it prevents |
|---|---|
| Goal (do not change) | The next session reinterprets scope and drifts. |
| Current state | Work is redone or a false "done" is trusted. |
| Decisions | A rejected design is re-adopted as an "improvement". |
| Remaining work | The next session plans from scratch. |
| Traps | The same failed approach is repeated; this is what compaction drops first. |
| Resume procedure | A stale or optimistic snapshot goes undetected. |
| Files to load | The next session spends its first 20% of context exploring. |

## Operating rule

- At roughly 40–50% context usage, write the handoff, run `check`, then start a fresh session.
- The first prompt of the new session: "Read HANDOFF.md, run section 6, confirm section 2, then start section 4 item 1."
