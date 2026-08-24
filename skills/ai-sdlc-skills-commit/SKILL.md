---
name: ai-sdlc-skills-commit
description: Stage and commit the working tree as one or more logical, conventional commits. Local-only — never pushes. Use after verification passes and the user wants the change committed.
---

# Conventional Commit

Run `git status` and `git diff` first. Never stage with `git add -A`/`.`; stage explicit files so another session's or the user's unrelated in-progress work is not absorbed. Never stage `.env` or other secret-bearing files.

Follow the repository's own commit convention if one is documented (`CONTRIBUTING.md`, a commit template, or an existing pattern in `git log`). Otherwise use Conventional Commits (`type(scope): summary`, imperative mood, summary line under ~72 characters).

Split the diff into separate commits when it spans unrelated concerns; keep a single logical change per commit. Reference the run slug and any issue/ticket number the repository's convention requires in the commit body or trailer.

If a pre-commit hook fails, fix the underlying issue and recommit — never bypass with `--no-verify`, `--no-gpg-sign`, or similar unless the user explicitly asked for it.

Never amend an existing commit unless the user explicitly asks. Never push, force-push, or rewrite history.

Report the created commit SHAs and messages. If the working tree has nothing to commit, or contains only changes the user did not ask to include, stop and say so instead of committing unrelated content.
