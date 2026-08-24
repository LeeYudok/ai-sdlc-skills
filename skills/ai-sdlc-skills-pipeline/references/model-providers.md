# Model provider contract

Model-backed optional tools use an OpenAI-compatible boundary. The pipeline itself must still function without this provider by using local inspection and deterministic checks.

## Doksam vLLM

Set these in the user's shell or secret manager:

```bash
export AI_SDLC_LLM_PROVIDER=vllm
export AI_SDLC_LLM_BASE_URL=<doksam-vllm-openai-compatible-url>
export AI_SDLC_LLM_MODEL=<served-model-name>
# Only when the server requires authentication:
export AI_SDLC_LLM_API_KEY=<secret>
```

Do not commit the internal URL, model credential, or shell export file.

## OpenAI

```bash
export AI_SDLC_LLM_PROVIDER=openai
export OPENAI_API_KEY=<secret>
export AI_SDLC_LLM_MODEL=<approved-model-name>
```

The model name stays explicit because cost, availability, and organization policy differ. Never choose or upgrade it silently.

## Tool adaptation

- Pass credentials only in the child process environment.
- For OpenAI-compatible tools, map the selected base URL, key, and model to that tool's documented variables or provider configuration.
- Never print resolved credentials or the internal base URL.
- Do not persist secrets in `.ai-sdlc/`, `AGENTS.md`, tool config committed to Git, logs, or generated reports.
- Confirm external data-transfer policy before using OpenAI or another hosted provider with proprietary code.
- A missing model provider disables model-backed optional evidence; it does not disable source analysis, deterministic review, tests, or local deployment.

Check readiness without revealing values:

```bash
python3 <pipeline-skill-dir>/scripts/provider_config.py --require-ready
```
