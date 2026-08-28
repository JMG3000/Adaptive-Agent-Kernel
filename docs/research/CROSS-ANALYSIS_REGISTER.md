# AAK Cross-Analysis Register

**Status:** Canonical cross-source / cross-execution reconciliation record  
**Initialized:** 2026-08-28

## Purpose

Use this register for material conflicts, drift, compatibility conclusions, and decision-support findings that span repository state, provider behavior, execution evidence, or research sources.

Do not use this register as a second `PROJECT-STATE.md` or `FINDINGS_REGISTER.md`.

## Register

| ID | Date | Subject | Evidence compared | Reconciliation | State | Consequence |
|---|---|---|---|---|---|---|
| CA-001 | 2026-08-28 | `uv` lifecycle defect | Earlier transient `/tmp` installation evidence vs later persistent user-level `uv 0.12.5` verification | Historical defect remains valid, but durable remediation is now verified. | SUPERSEDED AS ACTIVE BLOCKER | Keep `uv 0.12.5`; do not reopen lifecycle remediation without new evidence. |
| CA-002 | 2026-08-28 | Remote vs local Git truth | GitHub `main` at `90f5d106…` vs Codex evidence for local `427c5085…` and `34115d3…` | Remote is stale relative to validated local engineering evidence. Remote docs may record local evidence but must not claim unpublished SHAs are present remotely. | UNRESOLVED PUBLICATION DELTA | Publish documentation separately; workstation/Codex must transport validated local commits or later reconciled descendants. |
| CA-003 | 2026-08-28 | Memory Bank provider namespace | AAK authenticated authority `(scope,user_id)` vs ADK convenience wrapper namespace behavior | ADK wrapper validation of scope is insufficient when provider Memory Bank identity collapses to raw `user_id`; this risks same-user cross-scope convergence. | VALIDATED COMPATIBILITY DEFECT AT CHECKPOINT | Do not use wrapper namespace as AAK's final security boundary. |
| CA-004 | 2026-08-28 | Native Memory Bank scope capability | Current Cloud AI Platform client signatures + live read-only provider retrieval | Native API accepts explicit `dict[str,str]` scope; live retrieval with `{aak_scope,user_id}` authenticated and routed successfully. | VALIDATED PREREQUISITE | Native/direct adapter is feasible without new SDK/service/database. |
| CA-005 | 2026-08-28 | Native vs synthetic scope design | Synthetic/hashed provider-user projection vs direct multi-key provider scope | Native scope preserves AAK's authority dimensions, reduces translation debt, improves auditability, and aligns generation/retrieval domain with authenticated authority. | DECIDED | Synthetic/hashed provider-user design is SUPERSEDED unless a verified platform blocker forces reconsideration. |
| CA-006 | 2026-08-28 | Infrastructure baseline | Python 3.14.4/ADK 2.7.1 baseline vs isolated compatibility matrices and committed local baseline | Python 3.14.7 and ADK 2.8.0 independently and jointly passed accepted regressions; ADK lock delta had no transitive version churn. | VALIDATED | Local infrastructure checkpoint `34115d3…` is the accepted implementation baseline. |
| CA-007 | 2026-08-28 | Git branching vs deployment environments | Earlier `dev → test → main` idea vs approved engineering methodology and current remote branch topology | Test/Production are environments, not required permanent branches. Remote currently contains only `main`. | DECIDED / DEFERRED | Use short-lived `feat/*`, `fix/*`, `docs/*`, `build/*`; integrate reviewed changes to `main`; persistent promotion branches remain deferred. |
| CA-008 | 2026-08-28 | Package/release pipeline | Desire for production `main` and built packages vs current absence of CI/package implementation | `main` is the production/release branch; package/OCI automation should be introduced only from validated local build commands and should build the reviewed revision once. | DECIDED DIRECTION / IMPLEMENTATION DEFERRED | Do not create ceremonial CI. Add package/OCI workflow when a real distributable artifact and reproducible build command exist. |

## Current decision map

```text
REMOTE main: 90f5d106…
        │
        ├── docs/evidence-reconciliation-2026-08-28
        │       └── documentation publication
        │
LOCAL validated engineering line
feat/memory-bank-provider
        ├── 427c5085…
        │     provider-backed Memory Bank ingestion
        └── 34115d3…
              infrastructure baseline
              │
              ▼
        NEXT BEHAVIORAL SLICE
      native Memory Bank adapter
              │
              ▼
       generated-memory proof
```

## Update rules

1. Preserve historical evidence; supersede the active conclusion when newer evidence invalidates it.
2. Link back to canonical technical truth rather than restating large architecture sections here.
3. Do not promote assistant recommendations to `DECIDED` without Bossman adoption.
4. Repository/provider executable evidence outranks plans, prompts, and historical reports for implementation state.
5. Remote and local Git state must be named separately until the exact SHA relationship is verified.
