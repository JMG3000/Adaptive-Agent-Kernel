# Adaptive Agent Kernel

Adaptive Agent Kernel (AAK) is a Track 2 — Collaborative Partner project for
the All Things Agentic Hackathon. The approved implementation direction is the
Option B reference kernel, developed as small, secure, testable vertical
slices.

## Current local checkpoint

The repository currently contains locally verified foundations for:

- authenticated identity and Session isolation;
- the SEC-MW-001–004 Memory Write Gate around fake and provider-backed
  incremental-memory sinks;
- a Google ADK `Agent` and `App` configured for `gemini-3.5-flash` through
  explicit Vertex AI project and model-location inputs;
- deterministic ADK execution through `InMemoryRunner`, with a fake `BaseLlm`
  only at the model/network boundary;
- an AAK-authorized `VertexAiSessionService` adapter that preserves the
  authenticated user/scope boundary and fails closed before provider access;
- an AAK-authorized `VertexAiMemoryBankService` adapter that keeps incremental
  provider writes behind the existing Memory Write Gate.

One separately authorized live smoke test also exercised the existing AAK ADK
application seam through Vertex AI with `gemini-3.5-flash` in the decided `us`
model location and received a successful model response. The Agent Platform
location is independently decided as `us`; the Cloud Run region is unresolved.
One bounded live managed-Sessions proof also created and retrieved a synthetic
Session through the AAK adapter and verified that cross-user and wrong-scope
reads were denied before provider access. One bounded live Memory Bank proof
also passed one synthetic Session event through the AAK Memory Write Gate and
completed exactly one incremental provider ingestion request.

The local ADK in-memory runner remains temporary execution state. Managed
Session persistence is now provider-backed for this bounded seam, while AAK's
scope-authorization registry remains process-local and fail-closed rather than
a production authenticated-ingress or durable scope-restoration mechanism.
Memory Bank writes are provider-backed for the bounded ingestion seam. Memory
retrieval, Recall, Relevance, Adaptation, Correction, Cloud Run deployment, and
the complete Option B kernel remain **not verified**.

See [`docs/codex/PROJECT-STATE.md`](docs/codex/PROJECT-STATE.md) for the current
implementation boundary and [`docs/security/`](docs/security/) for the approved
security contract.

## Local setup and verification

AAK v0.1 supports Python 3.14. The current checkpoint was tested with Python
3.14.4 and pins its dependency graph in `uv.lock`.

Prerequisites:

- Python 3.14;
- `uv` 0.12.5.

Install the tested `uv` release into the persistent user executable directory
without changing shell profiles:

```bash
curl -LsSf https://astral.sh/uv/0.12.5/install.sh |
  env UV_INSTALL_DIR="$HOME/.local/bin" UV_NO_MODIFY_PATH=1 sh
command -v uv
command -v uvx
uv --version
```

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
  tests.test_managed_sessions \
  tests.test_memory_bank_provider \
  -v
```

These local regression tests do not authenticate to Google Cloud and do not by
themselves prove live Vertex AI, managed-Sessions, or Memory Bank execution. No
Google Cloud project or Vertex location is defaulted by the application.
