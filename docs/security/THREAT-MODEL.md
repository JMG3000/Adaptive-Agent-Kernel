# Adaptive Agent Kernel — Threat Model

**Status:** DECIDED baseline / implementation not yet verified\
**Date:** 2026-08-24\
**Scope:** Option B reference kernel only.

## Purpose

Define the security assets, attackers, trust boundaries, abuse cases, and
invariants that AAK implementation and tests must preserve.

This document is architecture/security authority for Option B. Evidence and
source provenance live in `docs/research/FINDINGS_REGISTER.md` and
`docs/research/security/SECURITY_SOURCE_REGISTER.md`.

## Protected assets

- authenticated user identity and its binding to `session.user_id`;
- Session data, event ordering, invocation state, and confirmation state;
- Memory Bank scope, memories, structured profiles, and revisions;
- explicit user corrections and supersession state;
- system/developer instructions and other control-plane policy;
- tool registration, tool arguments, approval state, and invocation identity;
- secrets, credentials, service identities, and cloud permissions;
- model/tool outputs before egress;
- Audit/Decision Ledger integrity and redaction;
- dependency/build provenance and deployed artifact integrity.

## Attacker and failure classes

1. unauthenticated remote caller;
2. authenticated malicious user attempting cross-user access;
3. malicious or compromised content introduced through user/session data;
4. poisoned persistent memory or malicious retrieved memory;
5. manipulated Session-history/confirmation events;
6. malicious or compromised tool/external-system data;
7. synthetic or remote-agent event misrepresented as human authority;
8. dependency/supply-chain compromise;
9. implementation/configuration defects that collapse scope, identity, or
   approval boundaries;
10. operator/model error that accidentally leaks secrets or over-authorizes a
    consequential action.

## Primary trust boundaries

### TB-01 — Authenticated user / application ingress

Authentication establishes the user authority used to create/bind Session
identity. Prompt data, model output, retrieved memory, and caller-supplied fields
must not redefine that authority.

### TB-02 — Input trust boundary

User-controlled content is classified/validated as data. It cannot become
system/developer policy because of wording, placement, or model interpretation.

### TB-03 — Session Service

Session events/history are persistent interaction records, not a trusted
control plane. Invocation/confirmation state must be validated rather than
trusted merely because it exists in history.

### TB-04 — Memory Write Gate

All AAK-supported persistent-memory writes pass through one policy boundary.

Option B reference:
`Session events -> Memory Write Gate -> add_events_to_memory() -> Memory Bank`.

The gate binds scope/provenance, applies policy/sensitivity checks, preserves
correction/supersession semantics, and fails closed on ambiguous authority.

Direct model-controlled `CreateMemory` and uncontrolled continuous-ingestion
paths are not exposed in v0.1.

### TB-05 — Retrieval Gate

Retrieved memory must satisfy authenticated scope, current correction/
supersession state, and the approved retrieval policy before active context
construction.

Retrieved memory is context data, not an instruction/authorization source.

### TB-06 — Context Builder

System/developer policy remains structurally and semantically distinct from
untrusted user, Session, retrieved-memory, and tool/event data.

### TB-07 — Tool Policy Broker

Gemini may propose a tool call; Gemini does not authorize it.

The broker validates:
- tool registration;
- whether confirmation is required;
- current pending invocation;
- approval authority/provenance;
- call identity;
- tool name;
- complete material argument binding;
- freshness/one-time use of approval.

Ambiguous, stale, replayed, synthetic, mismatched, or unauthorized approval
fails closed.

### TB-08 — Output / egress security boundary

Before content reaches the user or an external system, apply applicable
sensitive-data/policy checks. Security tooling such as Model Armor is
defense-in-depth, not the authorization authority.

### TB-09 — Audit / Decision Ledger

Record security decision metadata needed for reproducibility and investigation
without turning the ledger into a raw prompt, memory, or secret archive.

### TB-10 — Dependency / deployment boundary

Dependencies, OCI artifacts, service identities, Cloud Run ingress, and cloud
permissions must be explicit, least-privilege, reproducible, and scanned.

## Principal abuse cases

| ID | Abuse case | Required protection |
|---|---|---|
| TM-01 | attacker substitutes another user's identity/scope | authenticated identity -> Session binding; IAM/scope checks |
| TM-02 | malicious Session event becomes long-term memory | Memory Write Gate + provenance/scope/policy |
| TM-03 | memory survives dormant and later steers behavior | Retrieval Gate + sleeper/adversarial tests |
| TM-04 | Session history forges tool confirmation | Tool Policy Broker + exact-call validation |
| TM-05 | approval is replayed or arguments change after approval | one-time/current approval + full material-argument binding |
| TM-06 | A2A/synthetic `user` event impersonates human approval | authenticated human approval provenance; A2A deferred |
| TM-07 | prompt/retrieved content becomes control-plane instruction | Input boundary + Context Builder separation |
| TM-08 | model/tool output leaks secrets/cross-user data | egress checks + scope controls + logging minimization |
| TM-09 | unauthenticated ADK/Cloud Run surface permits execution | authenticated ingress + patched dependency + least privilege |
| TM-10 | dependency/plugin compromise reaches developer/runtime secrets | minimal dependencies + lock/SBOM/scanning + secret isolation |
| TM-11 | direct memory API bypasses AAK policy | all enabled memory writes behind Memory Write Gate |
| TM-12 | audit logging captures sensitive payloads | metadata-first/redacted ledger and logging policy |

## Security invariants

1. `session.user_id` is derived from authenticated application identity, not
   model/prompt/retrieved content.
2. User A cannot read/write user B Session or Memory scope through supported AAK
   interfaces.
3. Session history, Memory Bank content, and tool/event data are untrusted data.
4. Every supported persistent-memory mutation passes the Memory Write Gate.
5. Explicit correction supersedes stale/inferred memory.
6. Retrieved memory cannot become authorization or control-plane policy.
7. Tool availability is not authorization.
8. High-risk authorization is current, one-time, human-origin, and bound to the
   exact current material call.
9. Authorization/identity ambiguity fails closed.
10. A2A/multi-agent approval relay is outside Option B.
11. Model Armor or other classifiers are defense-in-depth, not authority.
12. Secrets are not persisted into ordinary prompts, Session history, memory,
    audit logs, or reports.
13. Security controls cannot be bypassed to make functional tests pass.

## Out of scope for Option B

- A2A/remote-agent delegation;
- multi-agent/fleet orchestration;
- MCP runtime integration;
- arbitrary external high-risk production tools;
- Agent Gateway as an architectural dependency unless separately adopted;
- a second memory/database authority;
- generalized enterprise policy infrastructure.

## Review trigger

Update this threat model when:
- a new trust boundary or external service is adopted;
- A2A/MCP/multi-agent scope is introduced;
- a finding invalidates an invariant;
- implementation demonstrates a material architectural difference;
- a security incident or regression exposes an unmodeled attack path.
