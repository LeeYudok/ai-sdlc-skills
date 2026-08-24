---
name: ai-sdlc-skills-local-deploy
description: Build and deploy a verified change into an isolated local environment, then run health and user-flow smoke tests without touching shared or production systems. Use after QA passes.
---

# Isolated Local Deployment

Infer the supported local deployment path from repository documentation, manifests, containers, and scripts. Do not improvise a production command.

Before starting, verify that:

- the selected profile is local/test and does not reference production or shared infrastructure;
- secrets are supplied through approved environment mechanisms and will not be logged;
- databases, queues, buckets, callbacks, brokers, and third-party endpoints are disposable, mocked, sandboxed, or explicitly approved;
- ports and resource requirements are available;
- migrations are safe for the selected disposable data store.

Build the deployable artifact, start the local stack, wait with a bounded timeout, and execute health checks plus smoke tests for the changed user flow, one failure path, and an unaffected critical flow. Inspect logs for errors and verify required metrics or traces when supported.

Write `.ai-sdlc/runs/<run>/local-deploy-report.md` with environment, artifact identity, sanitized commands, startup time, health results, smoke evidence mapped to `AC-*`, logs checked, limitations, and verdict.

Use `PASS`, `FAIL`, or `BLOCKED`. Missing local infrastructure is `BLOCKED`, not a pass. Stop and clean up processes and disposable resources after verification unless the user explicitly asks to keep them running. Never deploy to shared development, staging, or production under the label “local”.
