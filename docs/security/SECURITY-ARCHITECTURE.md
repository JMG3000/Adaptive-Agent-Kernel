# Adaptive Agent Kernel — Security Architecture

**Status:** DECIDED baseline / implementation evidence tracked separately  
**Date:** 2026-08-28  
**Scope:** Option B reference kernel.

## Approved conceptual architecture

```text
AUTHENTICATED USER
 identity → (aak_scope, user_id)
          │
          ▼
INPUT TRUST BOUNDARY
          │
          ▼
   SESSION SERVICE
 history/events untrusted
          │
     ┌────┴───────────────┐
     ▼                    ▼
CONTEXT BUILDER     MEMORY WRITE GATE
     ▲                    │
     │                    ▼
     │          AAK NATIVE MEMORY ADAPTER
     │                    │
     │                    ▼
     │             MEMORY BANK
     │          exact native scope
     │          {aak_scope,user_id}
     │                    │
     │              RETRIEVAL GATE
     │                    │
     └──────────┬─────────┘
                ▼
             GEMINI
                │
                ▼
       TOOL POLICY BROKER
                │
       ┌────────┴────────┐
       ▼                 ▼
 READ-ONLY TOOL     HIGH-RISK TOOL
       │                 │
       └────────┬────────┘
                ▼
          SESSION EVENT
                │
                ▼
          CONTEXT BUILDER
                │
                ▼
              GEMINI
                │
                ▼
     OUTPUT / EGRESS GATE
                │
                ▼
               USER

security decisions / confirmations / denials / provenance
                │
                ▼
       AUDIT / DECISION LEDGER
       metadata-first • redacted
```

## Authority and identity

The application authenticates the user and deterministically establishes AAK authority as `(aak_scope, user_id)`. Prompt content, model output, retrieved memory, tool data, Session-history text, A2A data, or caller-controlled substitute identifiers cannot create or replace that authority.

Ambiguous or contradictory identity/scope fails closed.

## Session Service

Managed Agent Platform Sessions persist interaction events. Session history remains untrusted data.

Authorization logic must not trust a confirmation, identity, or scope merely because it appears in Session history.

## Memory Write Gate

Every AAK-supported persistent-memory mutation passes one application policy boundary.

Current reference path:

```text
selected authenticated Session events
        │
        ▼
Memory Write Gate
        │
        ▼
AAK native Memory Bank adapter
        │
        ▼
Google Memory Bank
```

Rules:
- selected/incremental Session events remain the default source material;
- whole-session ingestion is a controlled comparison/fallback path only when separately justified;
- model-directed direct memory creation is not exposed as a bypass in v0.1;
- provenance/origin, authenticated authority, sensitivity policy, and later correction/supersession state remain outside model trust judgments;
- cross-user or cross-scope ambiguity fails closed.

## Native Memory Bank provider boundary

AAK has **DECIDED** to use the native/direct Google Memory Bank API for the security-sensitive provider adapter rather than making ADK `VertexAiMemoryBankService` define AAK's persistent-memory namespace.

Canonical provider scope:

```text
{
  "aak_scope": authenticated_scope,
  "user_id": authenticated_user_id
}
```

Provider scope is constructed only from authenticated AAK authority.

The prior synthetic/hashed provider-`user_id` projection is **SUPERSEDED** unless a verified platform blocker requires a new Bossman decision.

Memory Bank remains the single persistent adaptive-memory authority for Option B. No second vector store/database memory authority is introduced.

Native provider scope is defense in depth and does not replace AAK's Memory Write Gate or Retrieval Gate.

## Generated-memory evidence rule

Keep these states distinct:

```text
write gate accepted
≠ ingestion accepted
≠ generation completed
≠ generated memory exists
≠ generated memory is retrievable by intended authority
```

Provider generation/retrieval checks must be bounded. Timeout/backend failure must not be silently converted to an ordinary no-match result when that would hide a security or reliability failure.

## Retrieval Gate

Use authenticated `(aak_scope, user_id)` and on-demand relevant retrieval.

Before active context construction:
- authorize before querying;
- retrieve only under the provider scope constructed from authenticated authority;
- exclude/deprioritize superseded or stale memory according to correction policy when implemented;
- treat retrieved memory as untrusted data;
- never allow memory to authorize tools or replace system/developer policy.

The provider's exact-scope isolation is not sufficient by itself; application retrieval policy remains a separate security boundary.

## Context Builder

Keep control-plane instructions structurally and semantically separate from:
- user input;
- Session history;
- retrieved memory;
- tool results/events;
- external data.

Preserve provenance/authority labels required for policy decisions.

## Gemini

Gemini performs model reasoning and may propose memory/tool behavior. Gemini is not an authentication, authorization, approval, or provenance oracle.

## Tool Policy Broker

Consequential tool execution must deterministically validate:
1. tool registration;
2. applicable confirmation requirement;
3. original/current pending invocation;
4. authenticated human approval authority;
5. call identity/name;
6. exact material argument binding;
7. approval freshness and one-time use.

Fail closed on mismatch. A2A/multi-agent approval relay remains outside Option B.

## Output / egress gate

Apply applicable sensitive-data and policy controls before external release. Prevent cross-user data/secret leakage. Model Armor may be used as defense in depth but does not replace AAK authorization or memory integrity controls.

## Audit / Decision Ledger

Record metadata sufficient for reproducibility and investigation without becoming a raw-prompt, raw-memory, or secret archive:
- event/decision ID;
- timestamp;
- authenticated principal/scope reference;
- gate/control invoked;
- allow/deny/error reason;
- memory/tool operation identity;
- approval/provenance reference;
- anomaly/security signal references.

## Deployment hardening requirements

Before Cloud Run production exposure:
- use the reviewed dependency lock and required extras only;
- validate the real built OCI artifact in a clean/rootless environment;
- retain SBOM/security-scan/provenance evidence;
- use a dedicated least-privilege runtime service account;
- authenticate ingress;
- review Memory Bank/Sessions IAM boundaries and applicable IAM Conditions;
- ensure logging does not default to raw secrets/prompts/memory payloads;
- promote the same reviewed artifact between Test and Production whenever practical.

## Explicit exclusions

Option B does not include:
- A2A/multi-agent/fleet orchestration;
- MCP runtime integration;
- Agent Gateway as a required component;
- uncontrolled/direct model-owned persistent-memory mutation;
- a second persistent memory/database authority;
- generalized enterprise policy infrastructure;
- production destructive/high-risk tools before Tool Policy Broker tests pass.

## Evidence rule

This file is design authority, not implementation evidence. Each control remains unverified until executable repository/provider evidence demonstrates the behavior. See `docs/codex/PROJECT-STATE.md` for current implementation status and `docs/architecture/MEMORY-BANK-NATIVE-SCOPE.md` for the current native-scope provider decision.
