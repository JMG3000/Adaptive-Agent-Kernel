# Adaptive Agent Kernel — Security Test Plan

**Status:** DECIDED acceptance contract / implementation evidence tracked separately  
**Date:** 2026-08-28  
**Method:** TDD + ATDD, smallest complete vertical slices.

## Purpose

Convert the approved threat model and security architecture into executable behavior. Tests are requirements, not claims that implementation exists.

For production behavior changes use RED → verify expected failure → GREEN minimum implementation → verify → REFACTOR from green.

## Priority convention

- **P0:** required before the protected capability is usable.
- **P1:** required before Option B is functionally/security complete.
- **P2:** deployment/defense-in-depth validation before production exposure.

## Slice 1 — Authenticated identity and Session integrity

| ID | Pri | Acceptance behavior |
|---|---:|---|
| SEC-ID-001 | P0 | authenticated user A creates/uses only Session state bound to user A |
| SEC-ID-002 | P0 | user B cannot read/write user A Session through supported AAK interfaces |
| SEC-ID-003 | P0 | prompt/model/retrieved memory cannot redefine Session identity |
| SEC-ID-004 | P0 | caller-supplied mismatched identity/scope fails closed |
| SEC-SES-001 | P0 | Session history is never treated as authorization merely because it exists |

## Slice 2 — Memory Write Gate

| ID | Pri | Acceptance behavior |
|---|---:|---|
| SEC-MW-001 | P0 | selected authorized Session event can reach incremental Memory Bank ingestion |
| SEC-MW-002 | P0 | cross-user/mismatched-scope memory write is rejected |
| SEC-MW-003 | P0 | model-controlled direct memory creation is unavailable as a v0.1 bypass |
| SEC-MW-004 | P0 | all enabled persistent-memory mutation paths invoke AAK write policy |
| SEC-MW-005 | P1 | explicit correction prevents stale/inferred memory from governing current behavior |
| SEC-MW-006 | P1 | model summarization/semantic confidence cannot upgrade origin authority |
| SEC-MW-007 | P1 | configured sensitive-data policy blocks prohibited secret persistence |

## Slice 2A — Native Memory Bank provider scope and generated-memory proof

This slice validates the newly decided native Memory Bank provider boundary before the full Retrieval Gate is implemented.

| ID | Pri | Acceptance behavior |
|---|---:|---|
| SEC-MB-001 | P0 | native provider write/read scope is constructed only from authenticated `{aak_scope, user_id}` |
| SEC-MB-002 | P0 | same user + intended scope can retrieve the generated memory produced from its authorized event |
| SEC-MB-003 | P0 | same user + different scope cannot retrieve the first scope's generated memory through the real provider |
| SEC-MB-004 | P0 | different user + same scope cannot retrieve the first user's generated memory through the real provider |
| SEC-MB-005 | P0 | ingestion success is not reported as generated-memory success until the generated memory is actually observed |
| SEC-MB-006 | P0 | bounded generation/retrieval timeout or backend failure is surfaced distinctly rather than converted to ordinary `NO_MATCH` |
| SEC-MB-007 | P1 | old raw-user/provider namespace is not silently dual-read or merged into the new native scope |

Required live-provider evidence path:

```text
authenticated (aak_scope,user_id)
        │
        ▼
Memory Write Gate
        │
        ▼
native scoped ingestion
        │
        ▼
bounded generation
        │
        ▼
actual generated-memory retrieval
        │
   ┌────┼────────────┐
   ▼    ▼            ▼
correct wrong-scope wrong-user
FOUND   NOT FOUND    NOT FOUND
```

Provider-backed negative cases cannot be replaced by local-only Session denials.

## Slice 3 — Retrieval Gate

| ID | Pri | Acceptance behavior |
|---|---:|---|
| SEC-MR-001 | P0 | retrieval is authorized and constrained to the authenticated AAK scope before lookup |
| SEC-MR-002 | P1 | unrelated memory is not inserted into active context |
| SEC-MR-003 | P1 | superseded/stale memory is excluded or loses precedence to explicit correction |
| SEC-MR-004 | P1 | retrieved memory cannot authorize a tool or replace system/developer policy |
| SEC-MR-005 | P1 | delayed/sleeper poisoned-memory scenario is detected by regression behavior rather than silently trusted |

## Slice 4 — Context Builder

| ID | Pri | Acceptance behavior |
|---|---:|---|
| SEC-CTX-001 | P0 | user/Session/memory content claiming to be system policy remains untrusted data |
| SEC-CTX-002 | P1 | provenance/source class remains available for security decisions |
| SEC-CTX-003 | P1 | internal tool/error data does not silently become control-plane policy |

## Slice 5 — Tool Policy Broker

Use mocked/test tools first.

| ID | Pri | Acceptance behavior |
|---|---:|---|
| SEC-TP-001 | P0 | unregistered tool call is denied |
| SEC-TP-002 | P0 | confirmation policy is enforced when required |
| SEC-TP-003 | P0 | missing/orphaned original pending invocation is denied |
| SEC-TP-004 | P0 | wrong call ID is denied |
| SEC-TP-005 | P0 | changed tool name is denied |
| SEC-TP-006 | P0 | changed material arguments after approval are denied |
| SEC-TP-007 | P0 | stale/replayed/consumed approval is denied |
| SEC-TP-008 | P0 | synthetic Session event represented as `user` is not sufficient approval authority |
| SEC-TP-009 | P0 | A2A/remote-agent-origin approval is unavailable in Option B |
| SEC-TP-010 | P0 | current authenticated-human approval bound to the exact pending call is allowed once |
| SEC-TP-011 | P1 | read-only tool still enforces resource/scope allowlist and least privilege |

## Slice 6 — Output/egress and audit

| ID | Pri | Acceptance behavior |
|---|---:|---|
| SEC-EG-001 | P0 | cross-user memory/session content is not emitted to another user |
| SEC-EG-002 | P1 | prohibited secret material is blocked/redacted according to policy |
| SEC-AUD-001 | P1 | allow/deny/error decisions produce audit metadata with stable reason/reference fields |
| SEC-AUD-002 | P1 | audit records do not contain raw configured test secrets or complete prompt/memory payloads by default |
| SEC-AUD-003 | P1 | approval/tool/memory decisions can be correlated by non-secret identifiers |

## Slice 7 — Functional regression + security companions

| Functional family | Security companion |
|---|---|
| Cold Start | no fabricated identity, authority, or retained user context |
| Recall | authorized same-scope recall only |
| Relevance | malicious/irrelevant memory does not steer behavior |
| Adaptation | adaptation cannot silently promote poisoned data to authority |
| Correction | explicit correction survives stale-memory influence and later retrieval |

Dedicated adversarial regressions include memory poisoning, cross-scope/cross-user isolation, indirect prompt injection, Session-history authority injection, secret persistence/egress, unauthorized tool invocation, identity/scope substitution, malformed memory/event data, approval replay/argument substitution, and delayed/sleeper memory activation.

## Slice 8 — Dependency/deployment hardening

| ID | Pri | Acceptance behavior |
|---|---:|---|
| SEC-DEP-001 | P2 | resolved ADK version is outside known vulnerable ranges relevant to deployment |
| SEC-DEP-002 | P2 | dependency lock is reproducible and uses only required extras |
| SEC-DEP-003 | P2 | SBOM/security-scan evidence exists for the candidate OCI artifact |
| SEC-RUN-001 | P2 | Cloud Run ingress requires the approved authentication boundary |
| SEC-RUN-002 | P2 | runtime service identity has only reviewed required permissions |
| SEC-RUN-003 | P2 | Memory Bank/Sessions access is constrained to reviewed IAM/scope policy |
| SEC-RUN-004 | P2 | Model Armor behavior/coverage is tested where enabled and no test treats it as authorization |
| SEC-RUN-005 | P2 | logging validation proves configured secrets are not dumped into ordinary logs |
| SEC-RUN-006 | P2 | Test and Production receive the same reviewed artifact/digest unless an explicitly reviewed rebuild is required |

## Evidence requirements

For each applicable behavior retain:
- test ID and requirement;
- RED command/output for the expected missing behavior;
- GREEN command/output;
- relevant surrounding tests;
- provider/emulator/mock boundary;
- security/adversarial result;
- changed files/diff;
- unresolved assumptions.

Do not use mocked success as proof of live Google IAM/Memory Bank/Cloud Run behavior. Do not use successful ingestion as proof that generated memory exists. Do not use an HTTP/process success alone as evidence that a security property holds.

## Stop conditions

Stop and return to Bossman before expansion if:
- primary/provider evidence contradicts the approved architecture;
- the native provider API forces a material new service/authority;
- a security invariant cannot be enforced with the approved stack;
- a vulnerability affects the chosen dependency baseline with no safe compatible path;
- tests require A2A, MCP runtime integration, or another deferred boundary;
- remote/local Git state cannot be reconciled for a consequential promotion.
