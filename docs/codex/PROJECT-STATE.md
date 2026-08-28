# Adaptive Agent Kernel — Current Project State

**Status date:** 2026-08-28  
**Purpose:** Mutable source for current AAK implementation truth, approved architecture, delivery boundary, and immediate engineering objective.

## Authority

This file is subordinate to:
1. current explicit Bossman instructions;
2. root `AGENTS.md` for durable operating rules;
3. newer verified repository/provider evidence.

Historical chats, prompts, reports, Jira/Confluence records, and assistant recommendations are provenance, not automatic current truth.

## Repository and publication state

The connected GitHub repository is `JMG3000/Adaptive-Agent-Kernel` and its default/production branch is `main`.

Current directly verified remote state before this documentation publication:

```text
GitHub
└── main
    └── 90f5d10650066d095e170c74e66642bae998b049
        docs: record verified Vertex provider state
```

Newer reproducible Codex evidence establishes a separate validated local engineering line:

```text
feat/memory-bank-provider
├── 427c5085aaf7e05f79d94d5ca47b87b0263c9a06
│   └── provider-backed Memory Bank ingestion checkpoint
└── 34115d3b3815adeacbae921675eae0c9ef96484c
    └── updated infrastructure baseline
        ├── Python 3.14.7
        ├── uv 0.12.5
        ├── google-adk 2.8.0
        └── google-cloud-aiplatform[agent-engines] 1.165.1
```

At the end of the infrastructure-baseline task the local branch/worktree was reported clean and the accepted regressions were `20/20 PASS`.

**Important:** documentation published from the connected GitHub surface does not itself transport or prove the presence of local commits `427c5085…` or `34115d3…` on the remote. Remote publication of those implementation commits remains a separate Git action from the workstation/Codex repository surface.

## Project identity and hackathon direction

- **Project:** Adaptive Agent Kernel (AAK)
- **Hackathon:** All Things Agentic
- **Track:** Track 2 — Collaborative Partner
- **Strategy:** smallest complete vertical slices with provider-backed evidence
- **Reference kernel:** Option B — scaffold + runnable adaptive-memory kernel

The MVP must demonstrate persistent feedback/memory that changes later behavior, not merely a generic chat wrapper.

## Current architecture decision

Google ADK remains the application framework. Agent Platform Sessions remains the managed Session provider. Memory Bank remains the single persistent adaptive-memory authority.

For AAK's security-sensitive persistent-memory boundary, Bossman has **DECIDED** to use the native/direct Google Memory Bank API rather than making `VertexAiMemoryBankService` define AAK's provider authorization namespace.

Canonical direction:

```text
AUTHENTICATED AAK AUTHORITY
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
                 ▼
        GOOGLE MEMORY BANK
     native exact scope dictionary
       {aak_scope, user_id}
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

Provider scope must be constructed from authenticated AAK authority. Prompt/model/memory/tool content cannot supply or replace those authority fields.

The previously proposed synthetic/hashed provider-`user_id` projection is **SUPERSEDED** by the native-scope decision unless a verified platform blocker forces a new Bossman decision.

## Location decisions

- `VERTEX_MODEL_LOCATION = us` — **DECIDED**
- `AGENT_PLATFORM_LOCATION = us` — **DECIDED**
- `CLOUD_RUN_REGION` — **UNRESOLVED**

Do not infer Cloud Run region from the other two locations.

## Current verified implementation/evidence

| Capability | State | Evidence boundary |
|---|---|---|
| Root repository/Codex guidance | PRESENT | repository evidence |
| Gemini/Vertex invocation | VERIFIED | live provider interaction |
| Managed Agent Platform Sessions | VERIFIED | provider-backed |
| Authenticated cross-user Session isolation | VERIFIED | bounded provider seam |
| Authenticated wrong-scope Session isolation | VERIFIED | bounded provider seam |
| Memory Write Gate | VERIFIED | provider-backed write seam |
| Managed Memory Bank incremental ingestion | VERIFIED | live provider ingestion |
| Persistent `uv` | VERIFIED | `0.12.5` |
| Project Python baseline | VERIFIED | `3.14.7`, `.python-version` in local checkpoint |
| Google ADK baseline | VERIFIED | `2.8.0` in local checkpoint |
| Cloud AI Platform client | VERIFIED | `1.165.1` in local checkpoint |
| Dependency consistency | VERIFIED | 85 lock records / 82 compatible installed packages |
| Accepted regressions | VERIFIED | 20/20 PASS at local infrastructure checkpoint |
| Point-in-time dependency audits | VERIFIED WITH QUALIFICATION | no known PyPI/OSV findings on 2026-08-28 |
| Native Memory Bank client methods | VERIFIED | `ingest_events`, `generate`, `retrieve` with explicit scope |
| Native explicit-scope read capability | VERIFIED | live empty retrieval using `{aak_scope, user_id}` |
| Native adapter production implementation | NOT VERIFIED | next slice |
| Generated Memory Bank memory | NOT VERIFIED | next slice |
| Generated-memory retrieval isolation | NOT VERIFIED | next slice |
| Retrieval Gate | NOT VERIFIED | later slice |
| Recall | NOT VERIFIED | later slice |
| Relevance | NOT VERIFIED | later slice |
| Visible Adaptation | NOT VERIFIED | later slice |
| Correction/supersession | NOT VERIFIED | later slice |
| Restart-safe authority restoration | NOT VERIFIED | later slice |
| Cloud Run deployment | NOT VERIFIED | later slice |

A successful ingestion call is not proof that a generated memory exists or is retrievable.

## Infrastructure baseline

Validated local target baseline:

```text
Python                                  3.14.7
uv                                      0.12.5
google-adk                              2.8.0
google-cloud-aiplatform[agent-engines]  1.165.1
```

The infrastructure update intentionally did not:
- replace system `/usr/bin/python3`;
- upgrade `uv`;
- upgrade `google-cloud-aiplatform`;
- add another SDK/database/vector store;
- create another Runtime or Memory Bank;
- change IAM or Cloud Run;
- implement the native adapter.

## Development and DevSecOps delivery model

AAK separates Git branches from deployment environments.

```text
short-lived task branch
   feat/* | fix/* | docs/* | build/*
                │
                ▼
       validation + review
                │
                ▼
      main  ← production/release branch
                │
                ▼
      build one reviewed artifact
                │
          ┌─────┴─────┐
          ▼           ▼
     Test environment  package/OCI evidence
          │
          ▼
   Bossman promotion approval
          │
          ▼
   Production environment
```

Decisions:
- `main` is the production/release branch and should receive reviewed, validated changes rather than routine direct development.
- Use short-lived feature/slice branches for implementation and documentation work.
- Test and Production are environments; persistent `dev` and `test` Git branches remain **DEFERRED** until an operational need is demonstrated.
- Promote the exact tested SHA/artifact whenever practical; do not rebuild different source between stages.
- Package/OCI builds should be introduced from validated local build commands once a real distributable artifact exists. CI must reproduce the repository's actual development contract rather than exist for ceremony.
- Push, merge, deployment, IAM, and external-state mutations remain Bossman-authorized consequential actions.

## Security boundary

Authoritative security sources:
- `docs/security/THREAT-MODEL.md`
- `docs/security/SECURITY-ARCHITECTURE.md`
- `docs/security/SECURITY-TEST-PLAN.md`
- `docs/research/security/SECURITY_SOURCE_REGISTER.md`

Current persistent-memory security rule:

```text
authenticated (aak_scope, user_id)
        │
        ▼
Memory Write Gate
        │
        ▼
native Memory Bank scope
        │
        ▼
provider generation / storage / retrieval
        │
        ▼
Retrieval Gate before active context
```

Memory Bank/provider scope is defense in depth, not a replacement for AAK authorization. Retrieved memory remains untrusted data.

## Immediate engineering objective

The next bounded behavioral slice is:

```text
34115d3… green infrastructure baseline
        │
        ▼
AAK native Memory Bank adapter
        │
        ▼
explicit {aak_scope, user_id}
        │
        ▼
incremental authorized ingestion
        │
        ▼
bounded generation completion
        │
        ▼
actual generated-memory retrieval
        │
        ├── same authority → retrievable
        ├── same user / wrong scope → not retrievable
        └── same scope / wrong user → not retrievable
```

Do not expand this next slice into the full Retrieval Gate, Context Builder, Adaptation, Correction, Cloud Run, IAM Conditions, structured profiles, another datastore, or unrelated refactoring.

## Documentation architecture

- `AGENTS.md` — durable Codex operating map
- `docs/codex/PROJECT-STATE.md` — mutable implementation truth and immediate objective
- `docs/engineering/DEVELOPMENT-PRACTICES.md` — engineering/DevSecOps method
- `docs/research/FINDINGS_REGISTER.md` — claim-level research evidence and decisions
- `docs/research/CROSS-ANALYSIS_REGISTER.md` — reconciliation/drift/decision-support record
- `docs/research/security/SECURITY_SOURCE_REGISTER.md` — security provenance
- `docs/security/*` — approved security requirements and architecture

Do not maintain independently edited competing copies of the same technical truth.

## Update rule

When executable evidence changes:
1. update the relevant current-state claim;
2. reconcile claim-level research when platform facts changed;
3. update security architecture/tests if a trust-boundary design changed;
4. record cross-source conflicts/drift in the Cross-Analysis Register;
5. keep historical execution evidence in Git history/provenance rather than preserving stale current-state prose.
