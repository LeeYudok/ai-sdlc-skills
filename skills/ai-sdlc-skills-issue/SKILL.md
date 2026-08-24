---
name: ai-sdlc-skills-issue
description: Turn an issue number or a spec document into a tracked unit of work — resolve or create the forge issue, branch from a fresh default branch as <type>/issue-N-<slug>, and pin the pipeline run slug to that issue. Use at the very start of a change, before analysis, whenever the repository requires issue-first work.
---

# Issue Intake and Branch

Every change starts from a tracked issue. Accept either an issue number or a path to a spec/plan document; refuse to proceed with neither.

1. **Resolve the forge** from the repository's remotes and project-local convention (GitHub → `gh`, GitLab → `glab`, other → ask). Follow the repository's own issue rules (labels, templates, which repository owns the code — file the issue where the code lives, not in a tracking-only repository).
2. **Obtain the issue.**
   - Issue number given: read it (`gh issue view N` / `glab issue view N`). Confirm it is open and its scope is implementable; if the body is a one-liner, extract What/Why/acceptance criteria into the run request rather than guessing.
   - Spec path given: read the file, then create the issue with a title and a body summarizing scope, acceptance criteria, and exclusions. Write long bodies to a file first and pass it with `-F`/`--description "$(cat file)"` — inline composition breaks on fenced code and `ARG_MAX`. Never create a duplicate: search open issues by title first.
3. **Prepare the branch on a fresh base.** Verify the working tree is clean (`git status --porcelain` empty — if not, stop and ask; the changes may belong to another session). Update the default branch (`git pull --ff-only` on it) so the branch is not cut from a stale base. Name the branch `<type>/issue-N-<slug>` with `type` ∈ `feat|fix|chore|docs|refactor` derived from the issue. If the repository mandates worktree isolation for parallel sessions, create the branch with `git worktree add ../<repo>-<N> -b <branch>` instead of checking out in the shared clone.
4. **Pin the run.** Use `issue-N-<slug>` as the pipeline run slug and initialize it:
   `python3 <pipeline-skill-dir>/scripts/pipeline_state.py init --root <repo> --run issue-N-<slug> --request "<issue title + acceptance criteria>"`. If the run already exists, resume it instead of re-initializing.

Report the issue URL, branch name (and worktree path if created), and run slug. Do not write product code, commit, or push here — hand over to `ai-sdlc-skills-pipeline` (or the individual phase skills).
