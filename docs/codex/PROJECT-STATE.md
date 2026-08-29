# Adaptive Agent Kernel — Current Project State

**Status date:** 2026-08-28\
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
- `docs/codex/PROJECT-STATE.md`
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

- active feature branch: **VERIFIED — `feat/memory-bank-provider`**
- source checkpoint: **VERIFIED — `c8f7535874010cc7317eee62bf3df0ad2061200e` (`feat: add gated adaptive memory recall`)**
- parent checkpoint: **VERIFIED — `ebf6ddf007153b9b3eb44f29f3652f1a09e65292`**
- upstream branch: **VERIFIED — `origin/feat/memory-bank-provider`**
- published implementation checkpoint equality: **VERIFIED — the local implementation commit object and authoritative remote feature ref both resolve to `c8f7535874010cc7317eee62bf3df0ad2061200e`**
- worktree before this documentation mutation: **VERIFIED CLEAN**
- remote recovery/publication: **VERIFIED — the interrupted slice was recovered, completed, committed, and published to its corresponding remote feature branch**
- current documentation reconciliation: **LOCAL CHECKPOINT ONLY — publication is not authorized by this task**
- pull request: **NOT PERFORMED / pending authorization**
- `main` integration: **NOT PERFORMED / pending authorization — local and remote `main` remain at `90f5d10650066d095e170c74e66642bae998b049` and do not contain the feature checkpoint**
- artifact/build provenance: **NOT VERIFIED**
- deployment provenance: **NOT VERIFIED**

The remote feature branch contains the newest verified AAK implementation
checkpoint; this must not be confused with integration into the repository
default branch. Git history preserves historical state while this file records
current truth. Durable Git methodology remains in
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
- `CLOUD_RUN_REGION` — **UNRESOLVED**

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
- dependency vulnerability checks: **LOCALLY VERIFIED — pinned `pip-audit==2.10.1` reported no known findings from both PyPI and OSV for the complete synchronized environment on 2026-08-28; this is point-in-time evidence, not a permanent safety guarantee**
- application scaffold: **PARTIAL — accepted local identity/session and Memory Write Gate seams plus a minimal Google ADK Agent/App, managed-Sessions adapter, native Memory Bank adapter, bounded Retrieval Gate, and minimal Context Builder are present**
- runnable ADK agent: **LOCALLY VERIFIED — the actual ADK Agent/App executes through `InMemoryRunner` with a fake `BaseLlm` only at the nondeterministic model boundary**
- Gemini/Vertex invocation: **VERIFIED — on 2026-08-26, one real interaction exercised the existing AAK ADK application seam through Vertex AI using `gemini-3.5-flash` in the decided `us` model location and returned a non-empty response with no provider, authentication, or configuration error**
- Agent Platform Runtime: **VERIFIED — one lightweight Runtime named `AAK Managed Sessions` with resource ID `3642145461147533312` exists in the decided `us` Agent Platform location; no agent code was deployed by its creation**
- Agent Platform Sessions integration: **VERIFIED — on 2026-08-27, the AAK adapter created exactly one synthetic managed Session with the provider-minimum `86400s` TTL, retrieved it for the authenticated AAK identity, and denied cross-user and same-user/wrong-scope reads before provider access**
- native Memory Bank adapter: **VERIFIED — the adapter uses `agentplatform.Client(...).aio.agent_engines.memories`, derives the exact provider scope as `{"aak_scope": authenticated_scope, "user_id": authenticated_user_id}`, and exposes no supported direct persistent-mutation method outside the Memory Write Gate**
- Memory Bank ingestion/generation: **VERIFIED — on 2026-08-28, one bounded live proof passed one synthetic selected Session event through the AAK Memory Write Gate to native `ingest_events`; one request used force-flush generation, completed, and produced a generated Memory against Runtime `3642145461147533312` in `us`**
- native Memory Bank exact-scope isolation: **VERIFIED FOR THE BOUNDED PROVIDER PROOF — the generated Memory was retrieved under its authenticated `{aak_scope, user_id}` scope; separate provider requests using the same user/wrong scope and wrong user/same scope returned no memories**
- native Memory Bank similarity retrieval: **VERIFIED FOR THE BOUNDED ADAPTIVE-RECALL PROOF — the current request queried only the authenticated `{"aak_scope": authenticated_scope, "user_id": authenticated_user_id}` scope with `top_k=2`; provider ordering and available distance evidence were preserved without inventing a distance threshold**
- Memory Write Gate: **VERIFIED FOR THE CURRENT WRITE SEAM — SEC-MW-001–004 and native provider-boundary tests pass locally, and the same gated path completed the bounded live ingestion/generation proof; provider-returned data, model data, and Session history do not authorize writes**
- legacy Memory Bank namespace: **SUPERSEDED / MIGRATION DEBT — the 2026-08-27 `VertexAiMemoryBankService` proof used the old `app_name + raw user_id` projection; AAK does not dual-read, migrate, delete, or use that namespace as native-adapter acceptance evidence**
- Retrieval Gate / minimal Context Builder: **VERIFIED FOR THE CONTROLLED BOUNDED PROOF — locally, ambiguous identity and malformed rank-1 provider data fail closed; only the provider-ranked structurally valid rank-1 result is admitted, while application control, current request, and retrieved memory/provenance remain structurally separate and memory remains untrusted data**
- authenticated identity/session binding: **PARTIAL — Slice 1 and the managed-Sessions adapter are locally verified, including one bounded live synthetic-identity proof; production authenticated ingress and durable AAK scope-authority restoration remain unverified**
- deterministic Tool Policy Broker: **NOT VERIFIED**
- output/egress security gate: **NOT VERIFIED**
- Audit/Decision Ledger: **NOT VERIFIED**
- security regression plan implementation: **PARTIAL — Slice 1 SEC-ID/SEC-SES, Slice 2 SEC-MW-001–004, and the bounded Retrieval Gate/Context Builder security tests pass locally; Tool Policy Broker, egress, audit, and Correction coverage remain incomplete**
- structured-profile implementation: **NOT VERIFIED**
- episodic retrieval: **PARTIAL — bounded exact-scope native similarity retrieval and rank-1 admission are verified; generalized relevance policy and broader retrieval behavior are not verified**
- correction precedence: **NOT VERIFIED**
- five regression families: **PARTIAL — one controlled live scenario verified Cold Start, new-Session Recall, provider-ranked top-1 Relevance, exclusion of the unrelated returned rank-2 candidate from active context, and a visible decision-relevant recommendation change; this does not prove universal semantic relevance, and Correction remains not verified**
- rootless Podman/OCI project validation: **NOT VERIFIED**
- CI/CD: **NOT VERIFIED**
- Cloud Run deployment: **NOT VERIFIED**
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

The current goal remains a verified adaptive-memory reference kernel, not a
polished full product. Authenticated identity/Session binding, gated native
Memory Bank writes, bounded rank-1 retrieval/context construction, and the
controlled Cold Start/Recall/Relevance/Adaptation path now have executable
evidence. The next implementation slice requires owner authorization and must
remain narrow; Correction/supersession, Tool Policy Broker, egress/audit,
generalized relevance, and Cloud Run remain incomplete or unverified.

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
