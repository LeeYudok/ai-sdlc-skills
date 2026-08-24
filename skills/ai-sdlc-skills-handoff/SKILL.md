---
name: ai-sdlc-skills-handoff
description: Write a HANDOFF.md state snapshot so a fresh session can resume the current run without re-deriving context, and resume from an existing HANDOFF.md. Use when context usage approaches ~40-50%, before a deliberate session break, or when the user asks to hand off / resume work.
---

# Session Handoff

A long pipeline rarely fits one context window. Once usage passes roughly half the window, earlier instructions dilute and the model starts citing its own mistakes. Compaction hides what was lost; an explicit handoff document does not. This skill writes that document and defines how the next session picks it up.

## Write a handoff

1. Generate the skeleton. It pre-fills the goal, git state, and pipeline stage from `state.json` and `git`; it never invents the rest:

   ```bash
   python3 scripts/handoff.py write --root <repo> --run <run-slug>
   ```

   Output: `.ai-sdlc/runs/<run-slug>/HANDOFF.md`. Without `--run`, it writes `.ai-sdlc/HANDOFF.md` for work outside the stage machine.

2. Fill every `<!-- FILL -->` marker by hand, following [references/handoff-template.md](references/handoff-template.md). The sections that matter most are the ones only this session knows:
   - **Decisions** — what was chosen, why, and which alternative was rejected. Without this the next session "improves" the design back to a rejected option.
   - **Traps** — approaches tried and failed, files not to touch, environment quirks. This is the first thing compaction loses and the most expensive to rediscover.
   - **Resume procedure** — one verification command whose success proves the recorded state is real.
   - **Files to load** — the minimal set the next session should read instead of exploring.

3. Validate before ending the session:

   ```bash
   python3 scripts/handoff.py check --root <repo> --run <run-slug>
   ```

   The check fails on any remaining `<!-- FILL -->` marker or an empty required section. Do not end the session on a failing check.

4. Report only verified facts under "Current state". If something was not actually run, say so — the next session will run the resume command and catch a false claim, but only after wasting its time.

## Resume from a handoff

1. Read `HANDOFF.md` and only the files listed under "Files to load". Do not explore the repository first.
2. Run the resume procedure. If the verification command fails, the recorded state is stale: stop, report the discrepancy, and fix state before continuing.
3. Treat "Goal" and "Decisions" as fixed. Do not reinterpret scope or reopen a recorded decision unless the user asks.
4. Start at the first unchecked item under "Remaining work".
5. Once the run is complete or the handoff is superseded, regenerate it or delete it so a stale snapshot never outlives the state it describes.

## Rules

- Never paste secrets, tokens, or production payloads into the handoff. It is committed with the feature branch.
- The handoff is a snapshot, not a log. Replace it; do not append conversation history.
- Keep it short enough to read in a few minutes. If a section grows past a screen, it is carrying exploration that belongs in the run artifacts.
