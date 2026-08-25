# Adaptive Agent Kernel — Security Test Plan

**Status:** DECIDED acceptance contract / tests not yet implemented\
**Date:** 2026-08-24\
**Method:** TDD + ATDD, smallest complete vertical slices.

## Purpose

Convert the approved threat model and security architecture into executable
behavior. These tests are requirements, not claims that implementation exists.

Every production behavior protected here begins with RED, verifies the expected
failure, then proceeds to the minimum GREEN implementation and refactor from a
green baseline.

## Priority convention

- **P0:** must pass before the protected capability is usable.
- **P1:** must pass before Option B is considered functionally/security complete.
- **P2:** deployment/defense-in-depth validation before public/runtime exposure.

## Slice 1 — Authenticated identity and Session integrity

| ID | Pri | Acceptance behavior |
|---|---:|---|
| SEC-ID-001 | P0 | authenticated user A creates/uses only Session state bound to user A |
| SEC-ID-002 | P0 | user B cannot read/write user A Session through supported AAK interfaces |
| SEC-ID-003 | P0 | prompt/model/retrieved memory cannot redefine `session.user_id` |
| SEC-ID-004 | P0 | caller-supplied mismatched identity/scope fails closed |
| SEC-SES-001 | P0 | Session-history content is never treated as authorization merely because it exists in history |

## Slice 2 — Memory Write Gate

| ID | Pri | Acceptance behavior |
|---|---:|---|
| SEC-MW-001 | P0 | selected authorized Session event can reach incremental Memory Bank ingestion |
| SEC-MW-002 | P0 | cross-user/mismatched-scope memory write is rejected |
| SEC-MW-003 | P0 | model-controlled `CreateMemory` is unavailable through the v0.1 agent/tool surface |
| SEC-MW-004 | P0 | all enabled persistent-memory mutation paths invoke the AAK write policy |
| SEC-MW-005 | P1 | explicit correction is recorded so stale/inferred memory no longer governs current behavior |
| SEC-MW-006 | P1 | origin/provenance authority is not upgraded merely by model summarization or semantic confidence |
| SEC-MW-007 | P1 | configured sensitive-data policy prevents prohibited secret material from ordinary memory persistence |

## Slice 3 — Retrieval Gate

| ID | Pri | Acceptance behavior |
|---|---:|---|
| SEC-MR-001 | P0 | retrieval is constrained to the authenticated user's approved scope |
| SEC-MR-002 | P1 | unrelated memory is not inserted into active context |
| SEC-MR-003 | P1 | superseded/stale memory is excluded or loses precedence to explicit correction |
| SEC-MR-004 | P1 | retrieved memory cannot authorize a tool or replace system/developer policy |
| SEC-MR-005 | P1 | delayed/sleeper poisoned-memory scenario is detected by regression behavior rather than silently trusted |

## Slice 4 — Context Builder

| ID | Pri | Acceptance behavior |
|---|---:|---|
| SEC-CTX-001 | P0 | user/Session/memory content claiming to be a system instruction remains untrusted data |
| SEC-CTX-002 | P1 | provenance/source class remains available for security decisions |
| SEC-CTX-003 | P1 | internal tool/error data does not silently become control-plane policy |

## Slice 5 — Tool Policy Broker

Use mocked/test tools first.

| ID | Pri | Acceptance behavior |
|---|---:|---|
| SEC-TP-001 | P0 | unregistered tool call is denied |
| SEC-TP-002 | P0 | registered tool not requiring/meeting its confirmation policy is denied when policy requires approval |
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
| SEC-EG-002 | P1 | prohibited secret material is blocked/redacted from ordinary egress according to policy |
| SEC-AUD-001 | P1 | allow/deny decisions produce audit metadata with stable reason/reference fields |
| SEC-AUD-002 | P1 | audit records do not contain raw configured test secrets or complete prompt/memory payloads by default |
| SEC-AUD-003 | P1 | approval/tool/memory decisions can be correlated by non-secret identifiers |

## Slice 7 — Functional regression + security companions

Pair the original behavioral families with security properties:

| Functional family | Security companion |
|---|---|
| Cold Start | no fabricated identity, authority, or retained user context |
| Recall | authorized same-scope recall only |
| Relevance | malicious/irrelevant memory does not steer behavior |
| Adaptation | adaptation cannot silently promote poisoned data to authority |
| Correction | explicit correction survives stale-memory influence and later retrieval |

Dedicated adversarial regressions:

1. memory poisoning;
2. cross-user scope isolation;
3. indirect prompt injection;
4. Session-history authority/confirmation injection;
5. secret persistence/egress prevention;
6. unauthorized tool invocation;
7. identity/scope substitution;
8. malformed memory/event data;
9. approval replay/argument substitution;
10. delayed/sleeper memory activation.

## Slice 8 — Dependency/deployment hardening

| ID | Pri | Acceptance behavior |
|---|---:|---|
| SEC-DEP-001 | P2 | resolved ADK version is outside known vulnerable ranges relevant to deployment |
| SEC-DEP-002 | P2 | dependency lock is reproducible and uses only required extras |
| SEC-DEP-003 | P2 | SBOM/security scan evidence exists for the candidate OCI artifact |
| SEC-RUN-001 | P2 | Cloud Run ingress requires the approved authentication boundary |
| SEC-RUN-002 | P2 | runtime service identity has only reviewed required permissions |
| SEC-RUN-003 | P2 | Memory Bank/Sessions access is constrained to reviewed IAM/scope policy |
| SEC-RUN-004 | P2 | Model Armor behavior/coverage is tested where enabled and no test treats it as authorization |
| SEC-RUN-005 | P2 | logging/observability validation proves configured secrets are not dumped into ordinary logs |

## Test evidence requirements

For each TDD behavior record the narrowest applicable evidence:
- test ID and requirement;
- RED command/output demonstrating expected missing behavior;
- GREEN command/output;
- relevant surrounding suite;
- security/adversarial result;
- changed files/diff;
- unresolved assumptions;
- provider/emulator/mock boundary used.

Do not use mocked success as proof of live Google IAM/Memory Bank/Cloud Run
behavior. Live/provider tests must be separately identified.

## Stop conditions

Stop and return to Bossman before implementation expansion if:
- a primary source contradicts the approved architecture;
- a required Google API forces a material new service/authority;
- a security invariant cannot be enforced with the approved stack;
- a vulnerability affects the chosen dependency version and no safe compatible
  version is available;
- a test requires A2A, MCP runtime integration, or another currently deferred
  boundary.
