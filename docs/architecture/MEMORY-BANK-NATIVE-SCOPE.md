# AAK Native Memory Bank Scope Architecture

**Status:** DECIDED / implementation evidence tracked separately
**Date:** 2026-08-28
**Scope:** Option B persistent-memory provider boundary.

## Decision

AAK uses the native Google Memory Bank API for its security-sensitive
persistent-memory adapter rather than treating ADK
`VertexAiMemoryBankService` as the final provider namespace abstraction.

AAK authority remains the authenticated tuple:

```text
(aak_scope, user_id)
```

The provider scope preserves both authority dimensions explicitly:

```text
{
  "aak_scope": authenticated_scope,
  "user_id": authenticated_user_id
}
```

No prompt, model output, retrieved memory, tool output, Session-history text,
or caller-controlled substitute may create or replace these fields.

## Provider boundary

The native adapter uses:

```text
agentplatform.Client(...).aio.agent_engines.memories
```

The authenticated scope is used consistently for native ingestion,
generation, and retrieval. AAK does not hash or collapse the two authority
dimensions into one synthetic provider user identifier.

```text
AUTHENTICATED AAK AUTHORITY
       (aak_scope, user_id)
                 │
                 ▼
        MEMORY WRITE GATE
                 │
                 ▼
      AAK NATIVE MEMORY ADAPTER
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

The previously considered compatibility design encoded `(aak_scope, user_id)`
into one synthetic provider `user_id`. That can preserve uniqueness, but it
collapses AAK's semantic authority dimensions before the provider boundary.

Native scope:

- preserves both AAK authority dimensions explicitly;
- keeps generation and retrieval in the same authenticated namespace;
- reduces namespace-projection and reverse-mapping debt;
- improves audit and debugging visibility;
- leaves room for provider/IAM enforcement as defense in depth;
- aligns provider isolation with AAK's fail-closed authorization model.

The synthetic/hashed provider-user projection is **SUPERSEDED** unless a
verified platform blocker requires a new Bossman decision.

## Security invariants

1. Provider scope is constructed only from authenticated AAK authority.
2. Same user in different AAK scopes resolves to different provider scope.
3. Different users in the same AAK scope resolve to different provider scope.
4. Every supported persistent mutation remains behind the Memory Write Gate.
5. Native provider isolation does not replace the Retrieval Gate.
6. Retrieved memory remains untrusted data and cannot authorize tools or
   replace system/developer policy.
7. Provider timeout/backend failure is not converted into an ordinary no-match
   result when that distinction matters.
8. No second persistent memory/database authority is introduced.
9. The legacy raw-user namespace is not silently dual-read, merged, migrated,
   or deleted without a separately reviewed migration decision.

## Current evidence boundary

Current executable evidence is tracked in
`docs/codex/PROJECT-STATE.md`, not inferred from this architecture decision.
That evidence currently verifies:

- the native adapter and deterministic two-key scope construction;
- bounded generated-memory observation in the intended scope;
- bounded real-provider wrong-scope and wrong-user isolation results;
- bounded similarity retrieval and a controlled rank-1 Retrieval Gate /
  minimal Context Builder path;
- typed explicit-Correction precedence and fixed-shape gated persistence; and
- one bounded live path from explicit Correction through the Memory Write Gate
  and native Memory Bank to a later/new local Session, one exact authenticated-
  scope similarity retrieval, rank-1 Retrieval Gate admission as untrusted
  data, and visibly corrected application behavior.

The controlled retrieval proof does not establish universal semantic
relevance, and the controlled Correction proof does not establish provider-wide
Correction behavior across arbitrary facts or workloads. Restart-safe managed
Session authority restoration, Cloud Run runtime composition/deployment, and a
same-origin authenticated browser interaction have separate bounded live
evidence in `docs/codex/PROJECT-STATE.md`; that evidence does not universalize
Memory Bank behavior. Generalized relevance, Memory Bank/Session IAM Conditions,
broader workload behavior, and production readiness remain unverified or
deferred.

## Legacy namespace

Memory written through the earlier `VertexAiMemoryBankService` raw-user
projection is legacy evidence. AAK does not use that namespace as acceptance
evidence for the native adapter and does not silently dual-read it.
