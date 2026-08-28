# Adaptive Agent Kernel

Adaptive Agent Kernel (AAK) is a Track 2 — Collaborative Partner project for the All Things Agentic Hackathon. AAK is being developed as small, secure, evidence-backed vertical slices.

## Current state

The connected GitHub `main` branch is the production/release line. Newer validated engineering evidence exists on the local `feat/memory-bank-provider` line and is being reconciled into repository documentation without falsely claiming unpublished commits are already on GitHub.

Latest validated local engineering checkpoint:

```text
feat/memory-bank-provider
├── 427c5085…  provider-backed Memory Bank ingestion checkpoint
└── 34115d3…  updated infrastructure baseline
    ├── Python 3.14.7
    ├── uv 0.12.5
    ├── google-adk 2.8.0
    └── google-cloud-aiplatform[agent-engines] 1.165.1
```

At `34115d3…`, the accepted regression suite was `20/20 PASS`, dependency/lock consistency passed, and the worktree was reported clean.

Validated provider progress includes:
- real Gemini/Vertex execution;
- managed Agent Platform Sessions;
- bounded cross-user and wrong-scope Session isolation;
- provider-backed Memory Write Gate behavior;
- managed Memory Bank incremental ingestion;
- live native Memory Bank retrieval capability using explicit `{aak_scope, user_id}` scope.

Still not verified:
- the production native Memory Bank adapter;
- generated-memory retrieval/isolation;
- Retrieval Gate;
- Recall, Relevance, visible Adaptation, and Correction;
- restart-safe authority restoration;
- Cloud Run deployment.

See [`docs/codex/PROJECT-STATE.md`](docs/codex/PROJECT-STATE.md) for current implementation truth and [`docs/security/`](docs/security/) for the approved security contract.

## Current memory architecture direction

Bossman has decided that AAK will use the native/direct Google Memory Bank API for its security-sensitive persistent-memory boundary so AAK authority remains explicit:

```text
authenticated (aak_scope, user_id)
        │
        ▼
Memory Write Gate
        │
        ▼
AAK native Memory Bank adapter
        │
        ▼
Google Memory Bank exact native scope
        │
        ▼
Retrieval Gate
        │
        ▼
Gemini
```

The native adapter must not accept authority fields from prompt/model/memory/tool content.

## Local setup

AAK v0.1 supports Python 3.14.x. The latest validated local baseline uses Python 3.14.7 and a project `.python-version` pin.

Prerequisites:
- `uv`;
- access to the repository's configured Python version through `uv`.

Create/synchronize the project environment from the lockfile:

```bash
uv sync --locked
```

Run the repository's accepted tests according to `AGENTS.md` and `docs/engineering/DEVELOPMENT-PRACTICES.md`. Provider-backed tests must be reported separately from local/mock tests.

## Delivery model

```text
short-lived feat/* | fix/* | docs/* | build/*
                    │
                    ▼
             validate + review
                    │
                    ▼
                  main
             production/release
                    │
                    ▼
        build one reviewed artifact
                    │
             Test environment
                    │
          Bossman promotion approval
                    │
                    ▼
          Production environment
```

Test and Production are environments, not permanent Git branches. Persistent `dev`/`test` branches remain deferred until there is a demonstrated operational need.
