# AAK Cloud Run and Direct-IAP Composition

**Status:** IMPLEMENTED / bounded live evidence tracked in project state
**Date:** 2026-08-31
**Scope:** Judge-facing Option B MVP runtime.

## Implemented request path

```text
Google-authenticated browser
        │
        ▼
direct Cloud Run IAP
  - Google OAuth
  - Cloud Run service IAM
        │
        ▼
Cloud Run: aak-mvp (us-central1)
        │
        ├── GET /                 minimal server-rendered UI
        ├── GET /healthz          credential/provider-independent health
        └── POST /v1/interactions
                │
                ▼
AAK HTTP identity boundary
  - verify X-Goog-IAP-JWT-Assertion signature
  - require exact IAP audience and issuer
  - verified sub -> AuthenticatedIdentity.user_id
  - server AAK_SCOPE -> AuthenticatedIdentity.scope
                │
                ▼
ManagedSessionAdapter
  - create or authorize/restore AAK v1 managed Session
  - VertexAiSessionService
                │
                ├── optional ExplicitCorrection
                │       -> CorrectionService
                │       -> MemoryWriteGate
                │       -> native Memory Bank ingestion
                │
                ▼
RetrievalGate -> ContextBuilder
  - exact authenticated native Memory Bank scope
  - provider-ranked top_k=2 retrieval
  - structurally valid rank 1 admitted as UNTRUSTED_DATA
                │
                ▼
Google ADK Runner + App
                │
                ▼
gemini-3.5-flash through Vertex AI
                │
                ▼
minimal {session_id, response} JSON -> same-origin browser UI
```

## Authentication and authority

The browser does not construct, display, or store OAuth credentials for AAK.
Direct IAP performs Google authentication and forwards a signed
`X-Goog-IAP-JWT-Assertion`. Production verification uses
`google.oauth2.id_token.verify_token` with Google's IAP public-key endpoint and
requires:

```text
issuer   = https://cloud.google.com/iap
audience = /projects/491899793855/locations/us-central1/services/aak-mvp
```

Only the verified `sub` becomes `AuthenticatedIdentity.user_id`. The scope is
the required server configuration `AAK_SCOPE`; the deployed value is `aak-mvp`.
The strict request body permits only `request`, optional `session_id`, and
optional `correction`. It cannot supply identity, scope, authenticated claims,
project, Runtime ID, or provider coordinates.

The retained Bearer verifier supports local/controlled proof compatibility. It
is not the judge-facing ingress architecture after direct IAP was enabled.

## State and memory composition

The HTTP composition reuses the existing AAK authority seams:

- `ManagedSessionAdapter` creates or restores managed Sessions;
- restart restoration validates the AAK v1 identity/scope binding before
  provider access, then requires exact provider user and Session ID matches;
- the process-local `SessionService` reconstructed by that adapter backs the
  Correction, Memory Write, and adaptive-interaction path;
- `CorrectionService` is the only HTTP path from typed Correction to persistent
  memory and remains behind `MemoryWriteGate`;
- `NativeMemoryBankAdapter` derives exact provider scope only from authenticated
  AAK authority;
- `RetrievalGate` and `ContextBuilder` preserve untrusted-memory provenance and
  control/data separation; and
- `ProviderBackedInteractionExecutor` uses the public ADK `Runner` with
  `VertexAiSessionService`, not `InMemoryRunner`, in the deployed path.

No second database, memory authority, caller-selected provider identity, or
direct Memory Bank mutation path was introduced.

## Deployed bounded evidence

Read-only state on 2026-08-31 verified:

```text
project:          adaptive-agent-kernel-v1-hack
service:          aak-mvp
region:           us-central1
URL:              https://aak-mvp-okccsm7rca-uc.a.run.app
revision:         aak-mvp-iap8abe06a
image digest:     sha256:c23e1f34ecf90ccba521328c4017b497782296458196fccfa4f8885678ff59b2
source checkpoint: 8abe06a976609b2e5b3cfec62dde4a746b23f3bd
runtime identity: aak-cloud-run-runtime@adaptive-agent-kernel-v1-hack.iam.gserviceaccount.com
runtime project role: roles/aiplatform.user
```

The service is Ready with direct IAP enabled. Cloud Run service IAM contains no
`allUsers` or `allAuthenticatedUsers` invoker. The IAP resource policy grants
`roles/iap.httpsResourceAccessor` to `allAuthenticatedUsers`.

One controlled authenticated CDP-browser proof verified:

- the IAP-protected UI loaded after interactive Google authentication;
- the first same-origin interaction returned HTTP 200 and a non-empty
  ADK/Gemini response;
- continuation returned the exact same AAK managed Session ID;
- New Session returned a different valid AAK managed Session ID; and
- the same authenticated Google/IAP browser session was retained throughout.

No password, MFA value, cookie, OAuth token, raw IAP assertion, browser
credential storage, or downloaded OAuth credential was inspected or recorded.
The initial Playwright-launched sign-in path returned Google HTTP 400; its cause
was not established. The approved dedicated-Brave loopback-CDP fallback
completed the proof.

## Evidence limits

This architecture and its controlled proof do not establish:

- arbitrary external judge OAuth eligibility: Google Auth Platform publishing
  status was not available from the current read-only CLI/IAP evidence;
- universal Session/provider restart correctness;
- generalized semantic relevance or provider-wide Correction behavior;
- a deterministic Tool Policy Broker, complete output/egress gate, or
  Audit/Decision Ledger;
- multi-agent/A2A/fleet behavior; or
- broad production readiness.

The current implementation/evidence ledger is
`docs/codex/PROJECT-STATE.md`. The Memory Bank authority decision remains in
`docs/architecture/MEMORY-BANK-NATIVE-SCOPE.md`.
