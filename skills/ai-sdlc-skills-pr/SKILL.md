---
name: ai-sdlc-skills-pr
description: Open a pull or merge request for the current branch by analyzing its commit range and drafting a title and body, pushing the branch if needed. Use after the change is committed and the user wants it opened for review.
---

# Open Pull/Merge Request

Confirm the current branch is not the repository's default or protected branch (e.g. `main`, `master`, `develop`) — a PR from a protected branch onto itself is never valid. Confirm the repository's forge convention for issue linkage (e.g. a project rule requiring `Closes #N`); if one is required and no issue number is available, stop and ask instead of opening an untracked PR.

Determine the forge from the repository's remotes and any project-local convention (GitHub → `gh`, GitLab → `glab`, or other). Diff the branch against its base (commit list and file stat), and draft:

- a concise title;
- a body describing what changed and why, referencing `.ai-sdlc/runs/<run>/qa-report.md` and `release-plan.md` evidence when the run exists;
- the required issue-closing keyword per the repository's forge convention.

Push the branch only if it has unpushed commits or does not yet exist on the remote. Never force-push. If the remote branch already carries commits this session did not create, stop and ask before pushing — they may belong to another session or the user's own work.

Open the PR/MR in draft or ready state per the user's request and report the resulting URL. Never merge, never bypass required reviews or status checks, and never approve your own PR.
