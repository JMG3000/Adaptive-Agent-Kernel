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

The ADK in-memory runner is local execution state, not the authoritative AAK
Session or persistent-memory implementation.

Live Vertex execution, managed Agent Platform Sessions, Memory Bank,
provider-backed memory gates, Retrieval Gate behavior, correction/adaptation,
Cloud Run, and the complete Option B kernel remain **not verified**.

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

These tests do not authenticate to Google Cloud or prove a live Vertex AI
response. No Google Cloud project or Vertex location is defaulted by the
application.
