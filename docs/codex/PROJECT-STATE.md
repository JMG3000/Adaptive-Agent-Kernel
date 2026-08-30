# Adaptive Agent Kernel — Current Project State

**Status date:** 2026-08-30\
**Purpose:** Mutable source for the current AAK implementation state, approved
reference architecture, MVP boundary, and immediate engineering objective.

## Authority

This file is subordinate to:
1. explicit current Bossman instructions;
2. root `AGENTS.md` for durable Codex operating rules;
3. newer verified repository/provider evidence.

Historical chats, deleted files, prompts, Jira/Confluence records, and prior
assistant statements are provenance, not automatic current implementation
truth.

Update this file when verified project state materially changes.

## Current repository baseline

Approved documentation baseline for this reconciliation:

- `AGENTS.md`
- `docs/architecture/MEMORY-BANK-NATIVE-SCOPE.md`
- `docs/codex/PROJECT-STATE.md`
- `docs/research/CROSS-ANALYSIS_REGISTER.md`
- `docs/research/FINDINGS_REGISTER.md`
- `docs/research/security/SECURITY_SOURCE_REGISTER.md`
- `docs/engineering/DEVELOPMENT-PRACTICES.md`
- `docs/security/THREAT-MODEL.md`
- `docs/security/SECURITY-ARCHITECTURE.md`
- `docs/security/SECURITY-TEST-PLAN.md`

Codex must still verify that these files and the implementation-state evidence
below are present in the actual worktree. No CI, deployment configuration, or
external provider integration should be assumed to exist until Codex verifies
it directly.

## Current Git checkpoint

- active branch: **VERIFIED — `main`**
- verified implementation checkpoint: **VERIFIED — `3eae2cacd6d80958c0326b0e766a8637b0bb1841` (`feat: add private cloud run composition`); this checkpoint is contained in the current local and remote `main` lineage. Later documentation-only successors do not redefine the verified implementation checkpoint; current Git refs remain authoritative for the publication head**
- parent checkpoint: **VERIFIED — `6483f69481c345186f8e1df236cb5cef792d2d9d`**
- upstream branch: **VERIFIED — `origin/main`**
- publication head: **AUTHORITATIVE IN CURRENT GIT REFS — inspect the local and upstream refs directly; do not infer the current publication head from the verified implementation checkpoint**
- remote recovery/publication: **VERIFIED — the interrupted slice was recovered, completed, committed, and published to its corresponding remote feature branch**
- documentation-only successors: **DO NOT CHANGE THE VERIFIED IMPLEMENTATION CHECKPOINT — current Git refs are authoritative for their publication status**
- pull request: **NOT PERFORMED / pending authorization**
- `main` integration: **VERIFIED — after a normal fetch and fast-forward reconciliation, local `main` and `origin/main` both contained `f2e85babba7d940dcacb4694c04f9b1c69548186` and the private Cloud Run implementation checkpoint; current Git refs remain authoritative after later documentation-only successors**
- artifact/build provenance: **VERIFIED FOR THE CONTROLLED DEPLOYMENT — published source checkpoint `3eae2cacd6d80958c0326b0e766a8637b0bb1841` produced `us-central1-docker.pkg.dev/adaptive-agent-kernel-v1-hack/cloud-run-source-deploy/aak-mvp@sha256:8bd7af7ccde583045c6ddb9f1c409cd013b2910eac8b792d654c2ca645975e40`; a retained local CycloneDX 1.5 SBOM and current dependency audit cover the locked deployment dependency set**
- deployment provenance: **VERIFIED FOR ONE CONTROLLED BOUNDED PRIVATE CLOUD RUN DEPLOYMENT — service `aak-mvp`, region `us-central1`, final proof revision `aak-mvp-restore1`; this does not establish production readiness**

The local and remote default branch contain the published private Cloud Run
composition implementation and bounded evidence checkpoints. Git history
preserves historical state while this file records current truth. Durable Git
methodology remains in
`docs/engineering/DEVELOPMENT-PRACTICES.md`.

## Project identity and Devpost direction

- **Project:** Adaptive Agent Kernel (AAK)
- **Hackathon:** All Things Agentic
- **Current track:** Track 2 — Collaborative Partner
- **Implementation strategy:** smallest complete vertical slice first
- **Approved first implementation boundary:** Option B — scaffold + runnable
  reference kernel

The MVP must demonstrate an adaptive collaborative agent, not a generic chat
wrapper.

The product should:
1. guide the user and ask useful clarifying questions;
2. retain relevant information across sessions;
3. use retained information only when appropriate;
4. adapt behavior based on learned user context;
5. accept explicit correction and supersede stale/incorrect beliefs;
6. produce evidence showing that adaptation actually occurred.

## Approved reference architecture

Current reference path:

`gemini-3.5-flash`
→ Vertex AI
→ Google ADK for Python
→ Agent Platform Sessions
→ explicit AAK memory-ingestion policy
→ native incremental/event-subset ingestion with provider scope derived from
  authenticated AAK `{aak_scope, user_id}` authority
→ Vertex AI Memory Bank
→ structured-profile baseline
→ on-demand episodic retrieval
→ explicit correction precedence
→ agent response

Current location decisions:

- `VERTEX_MODEL_LOCATION = us` — **DECIDED**
- `AGENT_PLATFORM_LOCATION = us` — **DECIDED**
- `CLOUD_RUN_REGION = us-central1` — **DECIDED / DEPLOYED FOR THE CONTROLLED PRIVATE MVP PROOF**

These are separate configuration decisions. Do not infer a Cloud Run region
from either approved `us` location.

Preserve these conceptual boundaries:

- **Session state:** current/resumable interaction state.
- **Episodic memory:** relevant persisted information available across sessions.
- **Structured profile:** typed current representation of selected evolving
  user preferences/context.
- **Correction state:** explicit user corrections and supersession of stale
  beliefs.
- **Application data:** authoritative non-memory records if later required.

Do not introduce a second memory/database authority without an approved,
demonstrated need.

## Memory behavior

For the Option B reference path:

- memory persistence must be explicit and testable;
- prefer incremental/event-subset ingestion;
- do not assume persistence occurs merely because a memory service is
  configured;
- retrieve episodic memory on demand rather than globally preloading memory;
- explicit correction must take precedence over stale or inferred memory;
- ingestion, retrieval, adaptation, and correction must be observable in
  tests/evidence.

Whole-session ingestion remains a controlled comparison/fallback path when
justified; it is not the default reference mechanism.

## Behavioral acceptance criteria

The first runnable reference kernel must produce reproducible pass/fail
evidence for five regression families:

1. **Cold Start** — asks useful questions rather than inventing user context.
2. **Recall** — retrieves appropriate retained information in a later session.
3. **Relevance** — does not apply unrelated memory.
4. **Adaptation** — retained information changes behavior observably.
5. **Correction** — explicit correction supersedes stale or incorrect beliefs.

Import success, server startup, or HTTP 200 alone does not satisfy the MVP
definition of done.

## Development methodology

The following engineering practices are **DECIDED** for AAK:

- pair programming / human-in-the-loop development;
- TDD using Red → Green → Refactor;
- ATDD for user-visible and cross-component acceptance behavior;
- smallest complete vertical slices;
- Simple Design / YAGNI;
- continuous refactoring from a green baseline;
- continuous integration when CI is introduced;
- secure-by-design testing;
- short retrospectives after meaningful slices;
- evidence-based completion.

Detailed engineering workflow:
`docs/engineering/DEVELOPMENT-PRACTICES.md`

Current approved environment/delivery path:

native Linux development
→ rootless Podman clean-room build/test validation
→ OCI artifact
→ CI/CD when authorized
→ Cloud Run deployment

### Hackathon delivery strategy

Through the hackathon deadline, AAK uses short-lived feature/slice branches
integrated into reviewed `main`.

- Development → Test → Production remains the approved environment
  progression.
- Test and Production are environments; they do not require persistent Git
  branches.
- The previously considered persistent `dev` → `test` → `main` branch topology
  is **DEFERRED**, not rejected, until promotion automation becomes an
  immediate demonstrated need.
- Promotion and deployment remain explicitly Bossman-authorized initially.
- CodeQL, Dependabot, automated AI/code review, automated remediation, GitHub
  Issues, autonomous promotion, and autonomous deployment are excluded from
  the initial pipeline.

This decision prioritizes deadline discipline, YAGNI, reduced branch/merge/state
overhead, and promotion of the exact tested revision or artifact.

Do not introduce a Dev Container as the primary workflow.

Do not add Docker-specific assumptions without a verified compatibility
requirement.

## Approved security baseline

The AAK runtime security architecture is **DECIDED** as of 2026-08-24.

Authoritative security documents for implementation are:

- `docs/security/THREAT-MODEL.md`
- `docs/security/SECURITY-ARCHITECTURE.md`
- `docs/security/SECURITY-TEST-PLAN.md`

Research provenance is maintained in:

- `docs/research/FINDINGS_REGISTER.md`
- `docs/research/security/SECURITY_SOURCE_REGISTER.md`

The approved security path preserves these boundaries:

authenticated user with identity bound to `session.user_id`
→ input trust boundary
→ Session Service with untrusted event/history semantics
→ Context Builder and Memory Write Gate
→ Memory Bank
→ Retrieval Gate
→ Gemini
→ deterministic Tool Policy Broker
→ scoped read-only or approval-gated high-risk tools
→ Session event/context continuation
→ output/egress security gate
→ user

Security-relevant decisions flow to a metadata-first, redacted Audit/Decision
Ledger.

For Option B:

- persistent memory writes must pass the AAK Memory Write Gate;
- `add_events_to_memory()` is the reference incremental ingestion path;
- whole-session ingestion is a controlled fallback/comparison path;
- model-directed `CreateMemory` and continuous-ingestion paths that bypass AAK
  policy are not exposed in v0.1;
- retrieved memory and Session history are data, not control-plane authority;
- explicit user correction must supersede stale/inferred memory;
- consequential tool execution must validate the registered tool, confirmation
  requirement, current invocation, approval authority, call identity/name, and
  exact material arguments;
- approval must originate from the authenticated authorized human, not merely an
  event represented as `user`;
- Model Armor is defense-in-depth and does not replace AAK authorization,
  memory-integrity, or approval controls;
- A2A/multi-agent behavior remains deferred and outside Option B.

Security architecture approval is documentation/decision evidence only.
No security control is considered implemented until tests and repository/runtime
evidence prove it.

## Current MVP exclusions

Unless Bossman explicitly expands scope, do not add:

- multi-agent/fleet orchestration;
- A2A/remote-agent delegation or approval relay;
- Agent Registry or Agent Gateway architecture;
- Taskmaster/autonomous document-intake functionality;
- Firestore as a second memory authority;
- Cloud SQL;
- Pub/Sub;
- GKE/Kubernetes;
- custom vector databases;
- generalized enterprise-policy infrastructure;
- speculative platform integrations;
- unrelated feature work.

Judge-facing UI work may follow a working kernel, but it must not displace the
reference kernel and behavioral evidence as the critical path.

## Current implementation state

As of this state record:

- root Codex operating instructions: **PRESENT — owner reported**
- project-state record: **PRESENT — owner reported**
- Python runtime support: **DECIDED — AAK v0.1 supports Python 3.14.x; the project-managed baseline and current tested interpreter are Python 3.14.7, pinned by `.python-version`, and the project constraint remains `>=3.14,<3.15`**
- Python dependency manifest and lock: **LOCALLY VERIFIED — Python 3.14.7, persistent `uv==0.12.5`, `google-adk==2.8.0`, `google-cloud-aiplatform[agent-engines]==1.165.1`, `pyproject.toml`, and `uv.lock`; all 85 lock records were inspected and 82 packages synchronize without conflicts**
- dependency vulnerability checks: **LOCALLY VERIFIED — pinned `pip-audit==2.10.1` reported no known findings for the exact locked deployment dependency export on 2026-08-30; a CycloneDX 1.5 SBOM recorded 84 dependency components. This is point-in-time evidence, not a permanent safety guarantee**
- application scaffold: **PARTIAL — accepted local identity/session and Memory Write Gate seams plus a minimal Google ADK Agent/App, managed-Sessions adapter, native Memory Bank adapter, bounded Retrieval Gate, minimal Context Builder, typed explicit-Correction boundary, and private Cloud Run HTTP composition are present**
- runnable ADK agent: **LOCALLY VERIFIED — the actual ADK Agent/App executes through `InMemoryRunner` with a fake `BaseLlm` only at the nondeterministic model boundary**
- Gemini/Vertex invocation: **VERIFIED — on 2026-08-26, one real interaction exercised the existing AAK ADK application seam through Vertex AI using `gemini-3.5-flash` in the decided `us` model location and returned a non-empty response with no provider, authentication, or configuration error**
- Agent Platform Runtime: **VERIFIED — one lightweight Runtime named `AAK Managed Sessions` with resource ID `3642145461147533312` exists in the decided `us` Agent Platform location; no agent code was deployed by its creation**
- Agent Platform Sessions integration: **VERIFIED — on 2026-08-27, the AAK adapter created exactly one synthetic managed Session with the provider-minimum `86400s` TTL, retrieved it for the authenticated AAK identity, and denied cross-user and same-user/wrong-scope reads before provider access. On 2026-08-30, one controlled bounded proof created an AAK-scoped managed Session through the real provider in Process A, then Process B began with a fresh empty `SessionService`, denied wrong-scope and wrong-user requests before provider access, made exactly one provider `get_session` call for the original identity, and reconstructed the exact local user/scope/Session authority**
- native Memory Bank adapter: **VERIFIED — the adapter uses `agentplatform.Client(...).aio.agent_engines.memories`, derives the exact provider scope as `{"aak_scope": authenticated_scope, "user_id": authenticated_user_id}`, and exposes no supported direct persistent-mutation method outside the Memory Write Gate**
- Memory Bank ingestion/generation: **VERIFIED — on 2026-08-28, one bounded live proof passed one synthetic selected Session event through the AAK Memory Write Gate to native `ingest_events`; one request used force-flush generation, completed, and produced a generated Memory against Runtime `3642145461147533312` in `us`**
- native Memory Bank exact-scope isolation: **VERIFIED FOR THE BOUNDED PROVIDER PROOF — the generated Memory was retrieved under its authenticated `{aak_scope, user_id}` scope; separate provider requests using the same user/wrong scope and wrong user/same scope returned no memories**
- native Memory Bank similarity retrieval: **VERIFIED FOR THE BOUNDED ADAPTIVE-RECALL PROOF — the current request queried only the authenticated `{"aak_scope": authenticated_scope, "user_id": authenticated_user_id}` scope with `top_k=2`; provider ordering and available distance evidence were preserved without inventing a distance threshold**
- Memory Write Gate: **VERIFIED FOR THE CURRENT WRITE SEAM — SEC-MW-001–004 and native provider-boundary tests pass locally, and the typed explicit-Correction path persists its fixed-shape authorized Session event only through the same gate; provider-returned data, model data, and Session history do not authorize writes**
- legacy Memory Bank namespace: **SUPERSEDED / MIGRATION DEBT — the 2026-08-27 `VertexAiMemoryBankService` proof used the old `app_name + raw user_id` projection; AAK does not dual-read, migrate, delete, or use that namespace as native-adapter acceptance evidence**
- Retrieval Gate / minimal Context Builder: **VERIFIED FOR THE CONTROLLED BOUNDED PROOF — locally, ambiguous identity and malformed rank-1 provider data fail closed; only the provider-ranked structurally valid rank-1 result is admitted, while application control, current request, and retrieved memory/provenance remain structurally separate and memory remains untrusted data**
- authenticated identity/session binding: **PARTIAL — Slice 1 and the managed-Sessions adapter are locally verified. Restart-safe managed Session authority binding is LOCALLY VERIFIED WITH FAKE PROVIDER UNDER THE TRUSTED-PROVIDER-CREATION ASSUMPTION: AAK generates a 62-character `aak1-<24 hex nonce>-<32 hex binding>` Session ID. The 128-bit truncated SHA-256 binding covers version, the 96-bit `secrets` nonce, authenticated `user_id`, and authenticated scope, so separate Sessions for one authority do not expose a stable binding value. The ID is neither a signature nor a bearer authorization token. A fresh local `SessionService` restores authority only with authenticated identity, a matching scoped ID, exact provider-record existence, and an exact returned provider user and Session ID. Wrong-user, wrong-scope, malformed, wrong-version, binding-mismatch, provider-create failure, provider-substitution, and existing-conflict cases fail closed. Legacy non-AAK scoped Session IDs fail closed for authority restoration after process loss. LIVE AGENT PLATFORM FRESH-PROCESS SESSION AUTHORITY RESTORATION: VERIFIED FOR ONE CONTROLLED BOUNDED SYNTHETIC PROOF. LIVE CLOUD RUN FRESH-INSTANCE MANAGED SESSION RESTORATION: VERIFIED FOR ONE CONTROLLED BOUNDED SYNTHETIC PROOF — revision `aak-mvp-aud1` created the Session, distinct revision `aak-mvp-restore1` handled the continuation on a different logged instance, and the exact Session ID was restored without carrying process-local authority. Production human ingress, universal restart behavior, and production readiness remain unverified**
- deterministic Tool Policy Broker: **NOT VERIFIED**
- output/egress security gate: **NOT VERIFIED**
- Audit/Decision Ledger: **NOT VERIFIED**
- security regression plan implementation: **PARTIAL — Slice 1 SEC-ID/SEC-SES, Slice 2 SEC-MW-001–004, COR-001–007 local Correction coverage, and the bounded Retrieval Gate/Context Builder security tests pass locally; independent provider evidence covers the behaviors registered as SEC-MB-001–005, and SEC-MW-005 plus SEC-MR-003 now have bounded live provider/new-Session evidence. Dedicated SEC-MB requirement-to-test mapping, Tool Policy Broker, egress, and audit coverage remain incomplete**
- structured-profile implementation: **NOT VERIFIED**
- episodic retrieval: **PARTIAL — bounded exact-scope native similarity retrieval and rank-1 admission are verified; generalized relevance policy and broader retrieval behavior are not verified**
- correction precedence: **VERIFIED FOR THE CONTROLLED BOUNDED LIVE PROOF — `ExplicitCorrection(statement)` is accepted only through the typed trusted application boundary. In a clean synthetic exact provider scope, WRITE 1 generated stale state, then the fixed-shape explicit-Correction event persisted through `CorrectionService` → `MemoryWriteGate` → native Memory Bank. A new local recall Session contained neither X nor Y, `current_correction` was `None`, and one exact authenticated-scope `top_k=2` request returned provider rank 1 with corrected Y as current and X as previous. Only rank 1 entered active context as `UNTRUSTED_DATA`, and one application interaction visibly followed Y. Execution/output provenance was independently reconciled to durable Codex `CommandExecution` `exec-d78693b8-4a40-40f6-816c-3db8dfbe1ce2` with exit code 0 and complete stdout. This proves SEC-MW-005 and SEC-MR-003 only for the controlled scenario, not universal Correction behavior**
- five regression families: **VERIFIED FOR BOUNDED EXECUTABLE SCENARIOS — Cold Start, Recall, provider-ranked Relevance, visible Adaptation, and Correction now each have bounded executable evidence. This does not establish universal semantic relevance, universal Correction behavior, broad Cloud Run workload correctness, or production readiness**
- rootless Podman/OCI project validation: **LOCALLY VERIFIED — the repository-owned Cloud Run image built successfully with rootless Podman; two credential-free container instances honored `PORT`, served `/healthz`, rejected unauthenticated `/v1/interactions`, and the second instance reproduced health after restart. This is not a live Cloud Run deployment proof**
- CI/CD: **NOT VERIFIED**
- Cloud Run deployment: **VERIFIED FOR ONE CONTROLLED BOUNDED PRIVATE MVP PROOF — `aak-mvp` in `us-central1` is Ready with IAM-authenticated invocation, one CPU, 1 GiB, service-level min/max 0/1, concurrency 1, request-based billing, no GPU, no VPC, and dedicated runtime identity `aak-cloud-run-runtime@adaptive-agent-kernel-v1-hack.iam.gserviceaccount.com`. No public invoker binding exists**
- private Cloud Run HTTP composition: **VERIFIED FOR ONE CONTROLLED BOUNDED LIVE DEPLOYMENT — a keyless audience-bound proof caller passed Cloud Run IAM and AAK token verification, server scope remained `aak-mvp`, managed Session creation and exact-scope retrieval ran through the deployed composition, and the provider-backed ADK Runner returned a non-empty Gemini response. A successor revision and different logged instance restored the same Session ID. Correction persistence was not re-exercised. Production human ingress, universal restart/provider behavior, and production readiness remain unverified**
- final Devpost submission evidence: **NOT VERIFIED**

Do not promote any item based only on historical artifacts or plans.

## Freshness-sensitive implementation facts

Before consequential implementation, dependency locking, or deployment,
revalidate current primary/provider documentation when the task depends on:

- exact Gemini model availability/model ID;
- Google ADK interfaces/package versions;
- Agent Platform Sessions interfaces;
- Memory Bank ingestion/retrieval/profile APIs;
- Google Cloud supported locations/regions;
- Cloud Run deployment requirements;
- current Devpost rules/submission requirements.

Do not silently substitute a newer model, API, library, or service merely
because it exists.

## Immediate engineering objective

The bounded live later/new-Session Correction evidence boundary, restart-safe
managed Session authority-binding slice, private Cloud Run composition, one
controlled live deployment, and one controlled fresh-revision restoration proof
are complete. No successor slice is selected by this state update.

**NEXT IMPLEMENTATION OBJECTIVE: PENDING CURRENT BOSSMAN PLANNING
CONFIRMATION.**

Tool Policy Broker, egress/audit, generalized relevance, production human
ingress, broader workload/restart behavior, and judge-facing demo readiness
remain incomplete or unverified.

## Documentation architecture

Follow progressive disclosure:

- `AGENTS.md` = durable Codex operating map and invariants.
- `docs/codex/PROJECT-STATE.md` = current mutable state and active architecture
  boundary.
- `README.md` = human/setup/submission entry point when created.
- `docs/requirements/` = binding requirements when created.
- `docs/architecture/` = durable architecture decisions when they become
  stable enough to separate from this state file.
- `docs/research/` = validated external/platform findings and provenance.
- `docs/research/security/` = security-specific source catalog and research provenance.
- `docs/engineering/` = approved development methodology and engineering
  workflow.
- `docs/security/` = approved threat model, security architecture, and security
  acceptance/test requirements.
- `docs/evaluation/` = broader regression definitions/evidence when created.
- immediate Codex prompt = one bounded task.

Do not duplicate the same detailed rule across these layers.

## Update rule

When implementation evidence changes:
- update the relevant implementation-state entry;
- move stable architectural knowledge into `docs/architecture/` when useful;
- keep this file focused on current state and immediate execution direction;
- remove stale statements rather than preserving them for historical
  continuity.

Git history should preserve the history; this file should describe the current
state.
