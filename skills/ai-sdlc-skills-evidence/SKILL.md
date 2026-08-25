---
name: ai-sdlc-skills-evidence
description: Collect and reconcile independent codebase evidence using available code graphs, graph RAG, diff review, source inspection, and tests. Use after repository analysis when a change needs high-confidence blast-radius evidence without making third-party tools mandatory.
---

# Multi-source Change Evidence

Treat every tool result as evidence, not truth. Read [references/tool-strategy.md](references/tool-strategy.md), then detect available tools:

`python3 <this-skill-dir>/scripts/detect_tools.py --root <repo>`

Always retain a dependency-free baseline using Git, repository search, direct source inspection, manifests, schemas, delivery configuration, and existing tests. Add available specialized tools only where they improve coverage.

Write `.ai-sdlc/runs/<run>/evidence-ledger.md` with:

- tool name/version, index freshness, exact query or command, and analyzed commit;
- finding, affected symbols/components, source locations, and confidence;
- independent corroboration or contradiction;
- coverage gaps, unavailable tools, privacy constraints, and fallback used;
- unresolved disagreements that must block the impact gate.

Use at least two independent evidence lanes for high-risk claims. A second graph built from similar parsers is supporting evidence, not fully independent evidence. Confirm the final blast radius against exact source and executable tests.

Do not auto-install tools, change agent configuration, start Docker services, upload repository content, or rebuild a costly index without repository policy or user authorization. Never run destructive cleanup such as a shared graph database `--clean` operation.

End `evidence-ledger.md` with a machine-readable gate verdict line — `Verdict: PASS` when the blast radius is corroborated and every gap is recorded, otherwise `Verdict: BLOCKED` naming the unresolved disagreement. `pipeline_state.py` reads this line to allow or block the `evidence_collected` transition; the last such line in the file wins.
