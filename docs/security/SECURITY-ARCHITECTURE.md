# Adaptive Agent Kernel — Security Architecture

**Status:** DECIDED baseline / implementation evidence tracked separately\
**Date:** 2026-08-28\
**Scope:** Option B reference kernel.

## Approved conceptual architecture

```text
                        ┌────────────────────┐
                        │ AUTHENTICATED USER │
                        │ identity bound to  │
                        │ session.user_id    │
                        └─────────┬──────────┘
                                  │
                                  ▼
                      ┌──────────────────────┐
                      │ INPUT TRUST BOUNDARY │
                      │ classify / validate  │
                      └──────────┬───────────┘
                                 │
                                 ▼
                         SESSION SERVICE
                    events/history are untrusted
                                 │
                    ┌────────────┴─────────────┐
                    │                          │
                    ▼                          ▼
              CONTEXT BUILDER           MEMORY WRITE GATE
        instructions ≠ untrusted data    selected session events
        provenance / authority           trust / provenance
                    ▲                    scope / screening
                    │                          │
                    │                          ▼
                    │              AAK NATIVE MEMORY ADAPTER
                    │                          │
                    │                    MEMORY BANK
                    │                 exact native scope
                    │                          │
                    │                    RETRIEVAL GATE
                    │                          │
                    └────────────┬─────────────┘
                                 ▼
                              GEMINI
                                 │
                                 ▼
                       TOOL POLICY BROKER
            registered tool • confirmation requirement
             current invocation • approval authority
             call ID • name • exact arguments binding
                                 │
                   ┌─────────────┴─────────────┐
                   ▼                           ▼
             READ-ONLY TOOL              HIGH-RISK TOOL
             scoped authority            authenticated
                                         human approval
                                         exact-call binding
                                         one-time/current
                   │                           │
                   └──────────────┬────────────┘
                                  │
                                  ▼
                           SESSION EVENT
                        tool result recorded
                                  │
                                  └────→ CONTEXT BUILDER
                                           │
                                           ▼
                                         GEMINI
                                           │
                                           ▼
                              OUTPUT / EGRESS SECURITY GATE
                                           │
                                           ▼
                                          USER


      security decisions / confirmations / denials / provenance
                                │
                                ▼
                       AUDIT / DECISION LEDGER
                       metadata-first • redacted
```

## Architectural rules

### Authenticated user and Session identity

The application authenticates the user and deterministically establishes AAK
authority as `(aak_scope, user_id)`. Prompt content, memory, model output, tool
data, A2A data, Session history, or caller-controlled identifiers cannot create
or replace that authority.

### Input trust boundary

Validate structure/size/expected types and classify content as untrusted data.
Security screening may add signals but does not convert content into trusted
instructions.

### Session Service

Sessions persist conversation/invocation events. History remains untrusted.

Authorization logic must not trust a confirmation merely because it appears in
Session history.

### Memory Write Gate

The gate is located on the real ADK/Memory Bank write seam.

Reference v0.1 path:

`Session events -> Memory Write Gate -> native Memory Bank adapter -> Memory Bank`

Rules:
- selected/incremental Session events are the default;
- whole-session ingestion is a controlled comparison/fallback path;
- any enabled direct/pre-extracted memory upload must pass the same gate;
- model-directed `CreateMemory` is not exposed in v0.1;
- provenance/origin, authenticated scope, sensitivity policy, and correction/
  supersession state are preserved outside model trust judgments;
- ambiguous authority or cross-user scope fails closed.

### Memory Bank

Memory Bank remains the single persistent adaptive-memory authority for Option
B. No second database/vector-memory authority is introduced.

Memory revisions are useful for investigation/rollback but do not replace the
AAK policy that decides whether a write is permitted.

### Native Memory Bank provider boundary

AAK uses the native Google Memory Bank API for the security-sensitive provider
adapter. Provider scope is constructed only from authenticated AAK authority:

```text
{
  "aak_scope": authenticated_scope,
  "user_id": authenticated_user_id
}
```

The earlier synthetic/hashed provider-user projection is **SUPERSEDED** absent
a newly verified platform blocker. Native provider scope is defense in depth;
it does not replace the Memory Write Gate or Retrieval Gate. The legacy
raw-user namespace is not silently dual-read or merged into native scope.

### Generated-memory evidence rule

Keep these states distinct:

```text
write gate accepted
≠ ingestion accepted
≠ generation completed
≠ generated memory exists
≠ generated memory is retrievable by intended authority
```

Generation and retrieval checks used as security evidence must be bounded.
Timeout or backend failure must not be converted to ordinary no-match when that
would hide a security or reliability failure.

### Retrieval Gate

Use authenticated `(aak_scope, user_id)` and on-demand relevant retrieval.
Exclude or deprioritize superseded/stale memory according to correction policy.

Retrieved memory is data. It cannot authorize tools or replace system/developer
policy.

Provider exact-scope isolation is not sufficient by itself; application
retrieval policy remains a separate security boundary.

### Context Builder

Keep control-plane instructions separate from:
- user input;
- Session history;
- retrieved memory;
- tool results/events;
- external data.

Preserve provenance/authority labels needed for security decisions.

### Gemini

Gemini performs model reasoning and may propose memory/tool behavior.
Gemini is not an authentication, authorization, approval, or provenance oracle.

### Tool Policy Broker

The broker is deterministic application policy around tool execution.

For approval-gated/high-risk calls validate:
1. the tool is registered to the executing agent;
2. the call actually requires the applicable confirmation policy;
3. the original pending invocation exists/current;
4. approval comes from the authenticated authorized human;
5. call identity/name matches;
6. all material arguments match the approved call;
7. approval is current and not replayed/previously consumed.

Fail closed on mismatch.

Use mocked/test tools until these properties are executable regressions.

### Read-only tools

Read-only does not mean universally safe. Apply scope/resource allowlists,
least privilege, data minimization, and normal result handling.

### High-risk tools

Require authenticated human approval and exact-call binding. Approval for one
operation does not authorize a different target, tool, or material argument.

### Tool results

Tool results are recorded as Session events and re-enter reasoning through the
Context Builder. They remain untrusted data; there is no separate authorization
authority on the return path.

### Output / egress gate

Apply applicable sensitive-data and policy checks before external release.
Prevent cross-user data/secret leakage.

### Audit / Decision Ledger

Record:
- decision/event ID;
- timestamp;
- authenticated principal/scope reference;
- control/gate invoked;
- allow/deny/error reason code;
- memory/tool operation identity;
- approval reference/provenance;
- anomaly/security signal references.

Do not store raw secrets or complete prompts/memory payloads by default.

## Model Armor position

Model Armor is approved as defense-in-depth when applicable.

It may inspect/block supported Agent Platform or MCP traffic, but:
- API use may be detector-only and require application policy decisions;
- coverage varies by integration/payload;
- it does not replace authenticated identity/session binding;
- it does not replace Memory Write/Retrieval Gates;
- it does not replace Tool Policy Broker authorization;
- it does not replace human approval provenance.

## Deployment hardening requirements

Before Cloud Run deployment:
- resolve a current non-vulnerable ADK/dependency graph;
- use only required extras;
- lock dependencies;
- generate/retain SBOM evidence;
- perform dependency/security scanning;
- validate OCI artifact using rootless Podman;
- use a dedicated least-privilege runtime service account;
- authenticate runtime ingress;
- configure Memory Bank/Sessions IAM boundaries;
- configure Model Armor only with explicitly reviewed coverage/enforcement;
- ensure observability does not default to raw secret/prompt/memory payloads.

## Explicit exclusions

Option B does not include:
- A2A;
- multi-agent/fleet orchestration;
- MCP runtime integrations;
- Agent Gateway as a required component;
- model-directed direct Memory Bank creation;
- uncontrolled continuous memory ingestion;
- production destructive/high-risk tools before Tool Policy Broker tests pass.

## Evidence rule

This architecture is DECIDED design authority.

It is not implementation evidence.

Implementation status belongs in `docs/codex/PROJECT-STATE.md`. Each security
control remains unverified until test and runtime/repository evidence
demonstrates that behavior.
