# AAK Native Memory Bank Scope Architecture

**Status:** DECIDED / implementation pending  
**Date:** 2026-08-28  
**Scope:** Option B persistent-memory provider boundary.

## Decision

AAK will use the native/direct Google Memory Bank API for its security-sensitive persistent-memory adapter instead of treating ADK `VertexAiMemoryBankService` as the final provider namespace abstraction.

AAK authority remains the authenticated tuple:

```text
(aak_scope, user_id)
```

The provider scope is represented explicitly with the same authority dimensions:

```text
{
  "aak_scope": authenticated_scope,
  "user_id": authenticated_user_id
}
```

No prompt, model output, retrieved memory, tool output, Session-history text, or caller-controlled substitute may create or replace these fields.

## Architecture

```text
AUTHENTICATED USER / TENANT AUTHORITY
              │
              ▼
     (aak_scope, user_id)
              │
              ▼
       MEMORY WRITE GATE
              │
              ▼
   AAK NATIVE MEMORY ADAPTER
   agentplatform.Client().aio
     .agent_engines.memories
              │
       ┌──────┼──────┐
       ▼      ▼      ▼
    ingest  generate retrieve
       │      │      │
       └──────┴──────┘
              │
              ▼
      GOOGLE MEMORY BANK
      exact native scope
              │
              ▼
        RETRIEVAL GATE
              │
              ▼
        CONTEXT BUILDER
              │
              ▼
            GEMINI
```

## Why this design

The previously considered compatibility approach encoded `(aak_scope, user_id)` into one synthetic provider `user_id`. That preserves uniqueness when implemented correctly, but collapses AAK's semantic authority dimensions before the provider boundary.

Native scope is preferred because it:
- preserves AAK authority dimensions explicitly;
- lets Memory Bank generation/consolidation/retrieval operate within the same exact scope;
- reduces custom namespace-projection logic and migration debt;
- improves audit/debug visibility;
- leaves room for provider/IAM scope enforcement as defense in depth;
- aligns provider isolation with AAK's existing fail-closed security model.

The synthetic/hashed provider-user projection is **SUPERSEDED** by this decision unless a verified platform blocker requires a new Bossman decision.

## Security invariants

1. Provider scope is constructed only from authenticated AAK authority.
2. Same user in different AAK scopes must resolve to different provider scopes.
3. Different users in the same AAK scope must resolve to different provider scopes.
4. Memory Write Gate remains mandatory for every supported persistent mutation path.
5. Provider scope does not replace the later Retrieval Gate.
6. Retrieved memories remain untrusted data and cannot authorize tools or replace system/developer policy.
7. Failure/timeout must not be converted into an ordinary no-match result when the distinction matters for security evidence.
8. No second persistent memory/database authority is introduced.
9. Existing old-namespace provider memories are not dual-read or silently migrated without a separately reviewed migration decision.

## Verified prerequisite evidence

A read-only preflight established that the currently selected Google Cloud client exposes the non-deprecated native async Memory Bank methods:

- `ingest_events(..., scope: dict[str, str], ...)`
- `generate(..., scope: dict[str, str] | None, ...)`
- `retrieve(..., scope: dict[str, str], ...)`

A live provider read against the existing AAK Runtime accepted explicit scope keys `aak_scope` and `user_id`, authenticated successfully, routed to the Runtime, and returned an empty first page without provider error.

This proves native API capability and permission only. It does **not** prove generated-memory isolation.

## Next acceptance slice

```text
existing authenticated Session authority
        │
        ▼
Memory Write Gate
        │
        ▼
native scoped ingestion
        │
        ▼
bounded memory generation
        │
        ▼
real provider retrieval
        │
   ┌────┼────────────┐
   ▼    ▼            ▼
correct wrong-scope wrong-user
FOUND   NOT FOUND    NOT FOUND
```

The negative cases must exercise the real provider, not only local Session denial.

## Deferred from this decision

- complete Retrieval Gate policy;
- Context Builder implementation;
- visible Recall/Relevance/Adaptation behavior;
- Correction/supersession behavior;
- IAM Conditions configuration;
- Cloud Run deployment;
- structured profiles;
- additional persistent stores;
- broad provider abstraction/generalization.
