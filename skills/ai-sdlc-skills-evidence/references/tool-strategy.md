# Analysis tool strategy

These integrations are optional. Pin versions in controlled environments and record the version used. Do not vendor or modify third-party code merely to invoke it.

## Routing matrix

| Tool | Best evidence | Preferred use | Operational constraints |
|---|---|---|---|
| CodeGraph | symbols, callers/callees, routes, impact radius | Primary local source graph when initialized | Local SQLite; check freshness with `codegraph status .`; telemetry can be disabled by policy |
| Graphify | code plus docs, SQL, manifests, configs, rationale | Cross-check architecture and non-code relationships | Code-only extraction is local; docs/media may use an LLM backend; building and Codex installation write repository files |
| Code-Graph-RAG | mixed-language monorepo semantic queries and data flow | Opt-in for very large or cross-language repositories | Requires Docker, Memgraph, Qdrant, cmake, and ripgrep; shared graph lifecycle needs operator control |
| OpenCodeReview | changed-line defects, security, concurrency, rule-based review | Post-implementation independent diff review | Configured mode may send changed code to an LLM; confirm data-residency policy first |

## When to adopt a tool

Repository size is not the trigger. Adopt when a bottleneck is observed and recorded:

- related files are missed and found only after a defect;
- the same exploration is repeated every session;
- context is exhausted before implementation starts;
- the full verification suite is too slow to run per change;
- a small change ripples farther than expected;
- ownership or approval for a change is unclear.

Record a baseline before adopting and re-measure after: how often a search fails to find the right
location, how long location takes, how long verification waits. Without the baseline there is no way
to tell whether the tool helped.

Semantic or vector search is a later stage, not a default. Reach for it only when the staged search
above measurably misses relevant code, compare it against keyword search and a hybrid of both on the
same questions, and measure recall, irrelevant context returned, latency, and index build/refresh
cost before making it part of the workflow.

## Safe command patterns

Use only commands supported by the installed version and capture concise results.

```bash
codegraph status .
codegraph explore "<request-specific flow>"
codegraph impact "<symbol>" --depth 3 --json

graphify query "<relationship question>"
graphify path "<source-symbol>" "<target-symbol>"
graphify explain "<symbol>"

ocr review --from <base-branch> --to HEAD
ocr scan --path <high-risk-path>
```

Graphify index creation is optional and must respect repository output and data policies:

```bash
graphify extract . --code-only
```

Use Code-Graph-RAG only when its services are already approved and available. Never use `--clean` in the pipeline because its graph can contain multiple projects.

## Evidence reconciliation

1. Establish the exact Git revision and index freshness.
2. Ask request-specific questions; avoid dumping an entire graph into context.
3. Normalize findings to symbols, files, interfaces, data stores, and operational components.
4. Confirm high-severity graph edges by opening the cited source.
5. Compare findings with Git diff, tests, schemas, manifests, and delivery configuration.
6. Record disagreements. A missing edge is not proof of no impact.
7. Block on unresolved contradictions involving availability, data integrity, authorization, money movement, or public compatibility.

## Data handling

- Prefer local-only modes for private repositories.
- Do not expose source, prompts, file paths, or graph contents to a new external provider without authorization.
- Disable optional telemetry and query logging when repository policy requires it.
- Do not store raw proprietary code in the evidence ledger; cite paths and symbols.
