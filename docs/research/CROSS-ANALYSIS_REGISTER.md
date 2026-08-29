# AAK Cross-Analysis Register

**Status:** Historical cross-source reconciliation record
**Initialized:** 2026-08-28

## Purpose

Record material conflicts, drift, compatibility conclusions, and decision
support that span repository state, provider behavior, execution evidence, or
research sources. This is not a second `PROJECT-STATE.md` or
`FINDINGS_REGISTER.md`; current implementation truth remains in
`docs/codex/PROJECT-STATE.md`.

## Register

| ID | Date | Subject | Evidence compared | Reconciliation | State | Consequence |
|---|---|---|---|---|---|---|
| CA-001 | 2026-08-28 | `uv` lifecycle defect | Earlier transient `/tmp` installation evidence vs later persistent user-level `uv 0.12.5` verification | Historical defect remains valid; persistent installation and project verification remediated the active tooling blocker. The exact deletion event is not reconstructable from current metadata. | REMEDIATED / EXACT EVENT UNRESOLVED | Keep persistent `uv 0.12.5`; do not reopen without new evidence. |
| CA-002 | 2026-08-28 | Remote vs local Git truth | Earlier GitHub `main` at `90f5d106…` and unpublished local implementation checkpoints vs later verified publication of their descendants on `feat/memory-bank-provider` | The historical publication delta was valid when observed. The verified implementation checkpoint and documentation successors were later published to the feature branch; integration into `main` remains separate. | RESOLVED AS FEATURE-BRANCH PUBLICATION DELTA / MAIN INTEGRATION PENDING | Do not repeat “implementation commits absent from GitHub” as current truth. Consult Git refs and `PROJECT-STATE.md`. |
| CA-003 | 2026-08-28 | Memory Bank provider namespace | AAK authenticated authority `(scope, user_id)` vs ADK convenience-wrapper namespace behavior | Wrapper validation of scope is insufficient when the provider identity collapses to raw `user_id`; the wrapper namespace is not AAK's final security boundary. | VALIDATED COMPATIBILITY DEFECT AT CHECKPOINT / SUPERSEDED DESIGN | Use the native exact-scope adapter. |
| CA-004 | 2026-08-28 | Native Memory Bank scope capability | Cloud AI Platform client signatures and live provider retrieval | Native API accepts explicit `dict[str, str]` scope; authenticated retrieval with `{aak_scope, user_id}` routed successfully. | VALIDATED PREREQUISITE | Native/direct adapter requires no additional SDK, service, or database. |
| CA-005 | 2026-08-28 | Native vs synthetic scope design | Synthetic/hashed provider-user projection vs direct multi-key provider scope | Native scope preserves AAK authority dimensions, reduces translation debt, and aligns generation/retrieval with authenticated authority. | DECIDED | Synthetic/hashed provider-user design is SUPERSEDED absent a newly verified blocker. |
| CA-006 | 2026-08-28 | Infrastructure baseline | Python 3.14.4/ADK 2.7.1 baseline vs isolated compatibility evidence and committed updated baseline | Python 3.14.7 and ADK 2.8.0 independently and jointly passed accepted regressions; the ADK lock delta introduced no transitive version churn. | VALIDATED | `34115d3…` remains the accepted infrastructure baseline in the current implementation ancestry. |
| CA-007 | 2026-08-28 | Git branches vs deployment environments | Earlier `dev → test → main` idea vs approved engineering methodology and later feature/docs branch publication | Test and Production are environments, not required permanent branches. Short-lived work branches integrate into reviewed `main`; persistent promotion branches remain deferred. | DECIDED / DEFERRED | Use the simplest reviewable topology; consult `DEVELOPMENT-PRACTICES.md` for GitPath methodology. |
| CA-008 | 2026-08-28 | Package/release pipeline | Desired reviewed release line and artifacts vs absent CI/package implementation | Package/OCI automation should grow only from validated build commands and should preserve exact source/artifact provenance. | DECIDED DIRECTION / IMPLEMENTATION DEFERRED | Do not create ceremonial CI; artifact and deployment provenance remain unverified until executed. |

## Reconciliation relationship

```text
historical evidence branch
        │
        ▼
selective evidence reconciliation
        │
        ▼
current feature lineage
        │
        ▼
separately authorized main integration / artifact / deployment
```

## Update rules

1. Preserve historical evidence and supersede stale active conclusions.
2. Link to canonical technical truth rather than restating current state.
3. Do not promote recommendations to `DECIDED` without Bossman adoption.
4. Executable repository/provider evidence outranks plans and reports.
5. Use authoritative Git refs for current publication state.
