# Adaptive Agent Kernel

Adaptive Agent Kernel (AAK) is a Track 2 — Collaborative Partner project for
the All Things Agentic Hackathon. The approved implementation direction is the
Option B reference kernel, developed as small, secure, testable vertical
slices.

## Current local checkpoint

The repository currently contains locally verified foundations for:

- authenticated identity and Session isolation;
- the SEC-MW-001–004 Memory Write Gate around a fake incremental-memory sink;
- a Google ADK `Agent` and `App` configured for `gemini-3.5-flash` through
  explicit Vertex AI project and model-location inputs;
- deterministic ADK execution through `InMemoryRunner`, with a fake `BaseLlm`
  only at the model/network boundary.

One separately authorized live smoke test also exercised the existing AAK ADK
application seam through Vertex AI with `gemini-3.5-flash` in the decided `us`
model location and received a successful model response. The Agent Platform
location is independently decided as `us`; the Cloud Run region is unresolved.

The local ADK in-memory runner remains temporary execution state, not the
authoritative AAK Session or persistent-memory implementation. Managed Agent
Platform Sessions, Memory Bank and provider-backed memory, Recall, Relevance,
Adaptation, Correction, Cloud Run deployment, and the complete Option B kernel
remain **not verified**.

See [`docs/codex/PROJECT-STATE.md`](docs/codex/PROJECT-STATE.md) for the current
implementation boundary and [`docs/security/`](docs/security/) for the approved
security contract.

## Local setup and verification

AAK v0.1 supports Python 3.14. The current checkpoint was tested with Python
3.14.4 and pins its dependency graph in `uv.lock`.

Prerequisites:

- Python 3.14;
- `uv`.

Create the project-local environment from the lockfile:

```bash
uv sync --locked --python 3.14
```

Run the accepted local regression tests:

```bash
.venv/bin/python -m unittest \
  tests.test_identity_session \
  tests.test_memory_write_gate \
  tests.test_adk_foundation \
  -v
```

These local regression tests do not authenticate to Google Cloud and do not by
themselves prove live Vertex AI execution. No Google Cloud project or Vertex
location is defaulted by the application.
