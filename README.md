# Adaptive Agent Kernel

Adaptive Agent Kernel (AAK) is a bounded single-agent adaptive collaboration
and memory kernel built for Track 2 — Collaborative Partner of the All Things
Agentic Hackathon. It uses Google ADK and Gemini 3.5 Flash through Vertex AI,
managed Agent Platform Sessions, native Memory Bank, and a private Cloud Run
browser interface protected by direct Identity-Aware Proxy (IAP).

AAK is not a multi-agent fleet, A2A system, central orchestration hub, or
generalized autonomous workflow engine.

## Completed MVP

The current `main` lineage contains the completed judge-facing MVP:

- Google/IAP-authenticated browser ingress with verified IAP assertion subject
  mapped to AAK `user_id` and server-controlled `AAK_SCOPE`;
- a strict same-origin `POST /v1/interactions` contract that does not accept
  caller-selected identity, scope, or provider coordinates;
- a Google ADK `Agent`/`App` using `gemini-3.5-flash` through Vertex AI;
- provider-backed ADK execution through `Runner` and
  `VertexAiSessionService`;
- managed Sessions with nonce-dependent AAK v1 identity/scope bindings and
  bounded fresh-process/fresh-instance restoration evidence;
- a Memory Write Gate around supported persistent-memory writes;
- native Memory Bank scope derived exactly from authenticated
  `{aak_scope, user_id}` authority;
- bounded on-demand retrieval (`top_k=2`) that admits only a structurally valid
  provider-ranked rank-1 memory as `UNTRUSTED_DATA`;
- separated current request, optional typed explicit Correction, and retrieved
  memory context;
- bounded executable evidence for Cold Start, Recall, a controlled Relevance
  case, Adaptation, and Correction; and
- a minimal server-rendered browser UI with Session continuation and New
  Session controls.

The evidence is deliberately bounded. It does not establish generalized
semantic relevance, universal Memory Bank correction behavior, universal
restart behavior, a deterministic Tool Policy Broker, a complete output/egress
gate, an Audit/Decision Ledger, A2A/fleet behavior, or broad production
readiness.

## Hosted judge UI

Hosted service:

`https://aak-mvp-okccsm7rca-uc.a.run.app`

The deployed `aak-mvp` service in `us-central1` requires Google authentication
through direct Cloud Run IAP. A controlled browser proof verified UI access,
one successful ADK/Gemini interaction, continuation with the exact same managed
Session ID, and New Session creation with a different managed Session ID. The
AAK page JavaScript never receives or constructs Google credentials.

Current read-only Google Cloud evidence confirms Custom OAuth, direct IAP, and
`allAuthenticatedUsers` with `roles/iap.httpsResourceAccessor`. The Google Auth
Platform **publishing status could not be established through the available
read-only CLI/IAP surfaces**. The controlled Bossman browser proof is verified,
but unrestricted OAuth eligibility for an arbitrary external judge is not.
Before promising universal judge access, the submission team must inspect
Google Auth Platform → Audience and confirm whether Publishing status is **In
production**; if it remains **Testing**, that limitation must be resolved or
disclosed without sharing OAuth credentials.

When external judge eligibility is confirmed, the intended workflow is:

1. Open the hosted project URL.
2. Complete Google authentication when prompted.
3. Enter a request and select **Send**.
4. Submit a follow-up to continue the same managed Session.
5. Select **New Session** to start a different managed Session.
6. Use **Optional explicit Correction** to correct a remembered preference or
   fact when relevant.

No API key, OAuth secret, pasted token, or Google Cloud project membership is
part of the browser workflow.

## Local setup and verification

AAK v0.1 supports Python 3.14.x. The current checkpoint uses Python 3.14.7,
pins the project interpreter in `.python-version`, and locks dependencies in
`uv.lock`.

Prerequisites:

- Python 3.14;
- `uv` 0.12.5.

Locked direct runtime dependencies are `fastapi==0.141.1`,
`google-adk==2.8.0`, `google-auth==2.57.0`,
`google-cloud-aiplatform[agent-engines]==1.165.1`, and `uvicorn==0.52.4`.

Install the tested `uv` release without changing shell profiles:

```bash
curl -LsSf https://astral.sh/uv/0.12.5/install.sh |
  env UV_INSTALL_DIR="$HOME/.local/bin" UV_NO_MODIFY_PATH=1 sh
uv --version
```

Create the project-local environment from the lockfile:

```bash
uv sync --locked
```

Run the accepted local regression suite:

```bash
.venv/bin/python -m unittest \
  tests.test_identity_session \
  tests.test_memory_write_gate \
  tests.test_adk_foundation \
  tests.test_managed_sessions \
  tests.test_memory_bank_provider \
  tests.test_adaptive_recall \
  tests.test_correction \
  tests.test_cloud_run \
  -v
```

The expected result at this checkpoint is **68 tests passed**. These tests fake
network/model boundaries and do not by themselves prove live Google Cloud
behavior; the separate bounded live evidence is summarized in
[`docs/codex/PROJECT-STATE.md`](docs/codex/PROJECT-STATE.md).

## Local HTTP startup

The repository-owned ASGI entrypoint is `aak.cloud_run:app`. These configuration
values are required before an interaction; `/healthz` and `/` are intentionally
lazy and do not initialize provider clients:

```text
GOOGLE_CLOUD_PROJECT
VERTEX_MODEL_LOCATION
AGENT_PLATFORM_LOCATION
AGENT_RUNTIME_ID
AAK_OIDC_AUDIENCE
AAK_IAP_AUDIENCE
AAK_SCOPE
```

Start the local server with:

```bash
PORT=8080 .venv/bin/python -m aak.cloud_run
```

Then open `http://127.0.0.1:8080/` or check
`http://127.0.0.1:8080/healthz`. Local startup is not an authentication bypass:
successful interactions still require a cryptographically verified Google
identity and valid provider configuration/credentials.

## Current deployed configuration

The non-secret deployed coordinates are:

```text
Google Cloud project:       adaptive-agent-kernel-v1-hack
Cloud Run service/region:   aak-mvp / us-central1
Vertex model location:      us
Agent Platform location:    us
Agent Platform Runtime ID:  3642145461147533312
AAK server scope:           aak-mvp
Gemini model:               gemini-3.5-flash
```

See [`docs/architecture/CLOUD-RUN-IAP-COMPOSITION.md`](docs/architecture/CLOUD-RUN-IAP-COMPOSITION.md)
for the implemented request path,
[`docs/architecture/MEMORY-BANK-NATIVE-SCOPE.md`](docs/architecture/MEMORY-BANK-NATIVE-SCOPE.md)
for the persistent-memory boundary, and [`docs/security/`](docs/security/) for
the approved security contract and remaining controls.
