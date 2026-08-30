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
  authenticated user/scope boundary, creates provider-compatible AAK v1
  Session IDs with nonce-dependent bindings over both authority dimensions,
  and fails closed before provider access on mismatched restoration attempts;
- an AAK native Memory Bank adapter that derives the exact provider scope
  `{aak_scope, user_id}` from authenticated AAK authority and keeps incremental
  provider writes behind the existing Memory Write Gate;
- a bounded Retrieval Gate and minimal Context Builder that query the current
  authenticated native scope with `top_k=2`, admit only the provider-ranked
  structurally valid rank-1 result, and keep memory/provenance as untrusted data
  separate from application control and the current request;
- a typed explicit-Correction boundary that keeps authenticated current-user
  correction data structurally separate, gives it active precedence over
  conflicting retrieved memory, and persists its fixed-shape Session event only
  through the existing Memory Write Gate.

One separately authorized live smoke test also exercised the existing AAK ADK
application seam through Vertex AI with `gemini-3.5-flash` in the decided `us`
model location and received a successful model response. The Agent Platform
location is independently decided as `us`; `us-central1` is the current
recommended Cloud Run region and remains a deployment decision for a later
authorized task.
One bounded live managed-Sessions proof also created and retrieved a synthetic
Session through the AAK adapter and verified that cross-user and wrong-scope
reads were denied before provider access. One bounded live native Memory Bank
proof also passed one synthetic Session event through the AAK Memory Write
Gate, completed provider generation, found the generated memory in the
intended exact scope, and observed no result from provider queries using the
corresponding wrong-scope and wrong-user scopes.
One bounded live adaptive-recall proof then used fresh synthetic memory and a
new Session to demonstrate Cold Start, Recall, and a visible recommendation
change. For that controlled Relevance case, the applicable memory ranked first,
only rank 1 entered active context, and the unrelated returned candidate did
not. This is not a universal semantic-relevance policy, and no similarity
distance threshold is used.

The local ADK in-memory runner remains temporary execution state. Managed
Session persistence is provider-backed for this bounded seam. AAK now encodes a
non-secret nonce-dependent identity/scope binding in generated AAK v1 managed
Session IDs and, with a fresh local `SessionService`, reconstructs local
authority only after authenticated identity, exact provider-record existence,
and the exact returned provider user and Session ID validate. The scoped ID is
neither a signature nor a bearer authorization token. Restart-safe managed
Session authority binding is **LOCALLY VERIFIED WITH FAKE PROVIDER UNDER THE
TRUSTED-PROVIDER-CREATION ASSUMPTION**. One controlled bounded live Agent
Platform proof then created an AAK-scoped managed Session and restored its
user/scope authority from a genuinely fresh process; wrong-user and wrong-scope
requests were denied before provider access. Production authenticated ingress,
Cloud Run restart behavior, and production readiness remain unverified. Legacy
non-AAK managed Session IDs still fail closed for restoration after local
authority is lost.
Memory Bank writes, bounded exact-scope similarity retrieval, rank-1 admission,
and minimal context construction are provider-backed for this bounded seam.
One separately authorized bounded live Correction proof persisted a stale
preference, persisted a typed explicit Correction through the native Memory
Bank write path, created a new empty local Session with no current typed
correction, retrieved the corrected provider-ranked memory in the exact scope,
admitted only rank 1 through the Retrieval Gate, and produced visibly corrected
application behavior. Generalized semantic relevance, Cloud Run restart and
deployment behavior, production readiness, and the complete Option B kernel
remain **not verified**.

The private Cloud Run HTTP composition is **LOCALLY VERIFIED WITH FAKE
EXTERNAL BOUNDARIES AND ROOTLESS CONTAINER**. It provides `/healthz` and a
strict authenticated `/v1/interactions` boundary, derives AAK identity from a
verified OIDC subject plus server-controlled scope, and uses the managed
Session, Memory Write, Retrieval, Correction, and provider-backed ADK runner
seams. Live Cloud Run deployment, Cloud Run IAM invocation, runtime
service-account/IAM, Cloud Run restart behavior, and production readiness
remain unverified.

See [`docs/codex/PROJECT-STATE.md`](docs/codex/PROJECT-STATE.md) for the current
implementation boundary and [`docs/security/`](docs/security/) for the approved
security contract.

## Local setup and verification

AAK v0.1 supports Python 3.14. The current checkpoint was tested with Python
3.14.7, pins the project interpreter in `.python-version`, and pins its
dependency graph in `uv.lock`.

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
uv sync --locked
```

Run the accepted local regression tests:

```bash
.venv/bin/python -m unittest \
  tests.test_identity_session \
  tests.test_memory_write_gate \
  tests.test_adk_foundation \
  tests.test_managed_sessions \
  tests.test_memory_bank_provider \
  tests.test_adaptive_recall \
  tests.test_correction \
  -v
```

These local regression tests do not authenticate to Google Cloud and do not by
themselves prove live Vertex AI, managed-Sessions, or Memory Bank execution. No
Google Cloud project or Vertex location is defaulted by the application.
