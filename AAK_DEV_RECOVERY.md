# Adaptive Agent Kernel — Development Recovery & Continuity Record

> **Purpose:** durable development continuity and recovery indexing for the private AAK repository.
>
> **Repository placement:** tracked repository-root file `AAK_DEV_RECOVERY.md`.
>
> **Authority:** this file is the canonical **recovery index**, but it is **not** the canonical implementation-state source and is **not** an authorization artifact. Current Git/executable/provider evidence and `docs/codex/PROJECT-STATE.md` remain authoritative for current implementation truth.
>
> **Consolidated:** 2026-08-29 America/Chicago

## 1. Recovery contract

Use this file to recover the current AAK development thread after a lost ChatGPT/Codex session, context reset, workstation restart, or handoff.

The earlier design required this record to be local-only and ignored. That design is **SUPERSEDED by explicit Bossman direction on 2026-08-29** because a local-only recovery artifact failed to survive the handoff path. This consolidated record is intentionally tracked in the private repository so that recovery does not depend on one workstation or one chat attachment.

After recovery, reconcile this index against the current repository before consequential work. Precedence remains:

1. current explicit Bossman instruction;
2. current repository source of record and executable evidence;
3. current provider/external-system evidence;
4. this private recovery record;
5. historical chats/extractions/research.

This file may contain non-secret development identifiers, branch names, commit SHAs, provider resource IDs, and thread IDs. It must **never** contain passwords, OAuth tokens, ADC contents, API keys, private keys, cookies, authorization codes, recovery codes, or other credentials.

## 2. Canonical development loop

```text
ChatGPT
  research / architecture / reconciliation / review
        ↓
Bossman
  human authorization boundary
        ↓
Codex CLI
  repository / shell / implementation / tests / Git
        ↓
Bossman
  review / approve / reject
        ↓
ChatGPT
  reconcile evidence / select next bounded step
```

States used by AAK:

`VALIDATED | DECIDED | PROPOSED | ASSUMED | UNRESOLVED | DEFERRED | SUPERSEDED`

## 3. Recovery identifiers

### ChatGPT project/thread

- Project: **All Things Agentic Hackathon**
- Product: **Adaptive Agent Kernel (AAK)**
- Originating implementation-lineage chat title: **Implement Session Integrity Slice**
- ChatGPT project identifier: `g-p-6a841097ab04819195447884167fa096`
- Originating ChatGPT conversation/thread identifier: `6a8c2ad4-f2dc-83ea-8dce-aa908786fe83`
- Originating chat URL:
  `https://chatgpt.com/g/g-p-6a841097ab04819195447884167fa096/c/6a8c2ad4-f2dc-83ea-8dce-aa908786fe83`

### Codex thread

- Canonical Codex execution thread title: **Complete blocked live proof**
- Canonical Codex execution thread ID:
  `01a02b81-abc5-7c21-97fb-1915dceabb68`
- This is the **only Codex thread used for AAK implementation to date**.
- Resume command:

```bash
codex resume 01a02b81-abc5-7c21-97fb-1915dceabb68
```

If Codex reports that this thread no longer exists, do **not** invent a replacement ID. Start a new Codex thread from the current repository and use this recovery record only as subordinate recovery context.

## 4. Repository and current Git checkpoint

- Repository: `JMG3000/Adaptive-Agent-Kernel`
- Repository URL: `https://github.com/JMG3000/Adaptive-Agent-Kernel`
- Repository visibility: **PRIVATE — revalidated 2026-08-29**
- Primary repository path: `~/repos/Adaptive-Agent-Kernel`
- Current development line: `feat/memory-bank-provider`
- Last independently revalidated pre-recovery publication checkpoint:
  `7eda888f424d790b1de756a0d4aa05baf00b6867`
  `docs: reconcile parallel evidence branches`
- Remote branch: `origin/feat/memory-bank-provider`
- The commit that contains this tracked recovery record is a later documentation/recovery successor and must be determined from Git rather than hard-coded into this file.
- At the `7eda888…` publication checkpoint, local and remote feature-branch SHAs matched; tracking was `0 ahead / 0 behind`; worktree was clean.
- No PR, merge, deployment, IAM, provider, or cloud mutation was performed by the mediation/publication sequence.
- `main` was revalidated on 2026-08-29 at:
  `90f5d10650066d095e170c74e66642bae998b049`
- Historical evidence branch was revalidated on 2026-08-29 at:
  `b42286f138ebb1a8f947c5e72d987e23e715d6a8`
  on `docs/evidence-reconciliation-2026-08-28`.

### Verified implementation checkpoint vs documentation successors

The newest **verified implementation checkpoint** remains:

`c8f7535874010cc7317eee62bf3df0ad2061200e`
`feat: add gated adaptive memory recall`

Later commits are documentation/recovery-state successors and do not redefine the implementation checkpoint:

| Purpose | Commit | Status |
|---|---|---|
| Gated adaptive memory recall | `c8f7535874010cc7317eee62bf3df0ad2061200e` | verified implementation checkpoint |
| Verified Source Checkpoint / GitPath model | `04ae9e2b7a5fc83e0936d3860b7eea5781b86231` | documentation successor |
| Stable Git checkpoint wording | `21c05ed4397af1ff7a0203047459822e42b7a78f` | documentation successor |
| Parallel evidence-branch reconciliation | `7eda888f424d790b1de756a0d4aa05baf00b6867` | current published branch tip |

### Important implementation lineage

| Purpose | Commit | Status at latest evidence |
|---|---|---|
| Foundation checkpoint | `5b017570285096563be08b69f2439d9391597140` | historical accepted checkpoint |
| Managed Sessions dependency | `a6a9b0bff401d7202e35d51913f279dffcf144f0` | historical slice commit |
| Managed Sessions implementation | `bd848b96b1104c51d7e81d53395810e1e7818164` | historical slice commit |
| Managed Memory Bank write seam | `427c5085aaf7e05f79d94d5ca47b87b0263c9a06` | completed lineage checkpoint |
| Updated infrastructure baseline | `34115d3b3815adeacbae921675eae0c9ef96484c` | accepted baseline checkpoint |
| Native scoped Memory Bank | `ebf6ddf007153b9b3eb44f29f3652f1a09e65292` | verified native provider checkpoint |
| Gated adaptive memory recall | `c8f7535874010cc7317eee62bf3df0ad2061200e` | verified implementation checkpoint |
| GitPath documentation | `04ae9e2b7a5fc83e0936d3860b7eea5781b86231` | published documentation successor |
| Stable Git-state documentation | `21c05ed4397af1ff7a0203047459822e42b7a78f` | published documentation successor |
| Parallel evidence reconciliation | `7eda888f424d790b1de756a0d4aa05baf00b6867` | **current published feature tip** |

## 5. Current tool/dependency baseline

Latest verified development baseline:

- Project Python: `3.14.7`
- System `/usr/bin/python3`: left unchanged at `3.14.4`
- `uv`: `0.12.5`
- Persistent executables:
  - `/home/bossman/.local/bin/uv`
  - `/home/bossman/.local/bin/uvx`
- `google-adk`: `2.8.0`
- `google-cloud-aiplatform[agent-engines]`: `1.165.1`
- Lock records: `85`
- Compatible synchronized environment packages: `82`

The old `/tmp/uv-bootstrap` arrangement is **SUPERSEDED**. Persistent user-managed `uv 0.12.5` is verified.

Last recorded baseline checks:

- `uv lock --check`: PASS
- `uv sync --check --locked`: PASS / no changes
- `uv pip check`: PASS
- PyPI audit: no known findings at check time
- OSV audit: no known findings at check time
- secret-pattern scan: no matches
- diff hygiene: PASS

## 6. Google Cloud/provider state

- Google Cloud project: `adaptive-agent-kernel-v1-hack`
- Project lifecycle: **ACTIVE**
- Billing: **LINKED**
- CLI user authentication: **VALIDATED**
- Local user ADC: **VALIDATED**
- ADC quota project: `adaptive-agent-kernel-v1-hack`
- Vertex AI API: **ENABLED**
- Model: `gemini-3.5-flash`
- Vertex model location: `us` — **DECIDED**
- Agent Platform location: `us` — **DECIDED**
- Cloud Run region: **UNRESOLVED**
- Real Vertex/Gemini application interaction: **VERIFIED**

### Managed Agent Platform resource

- Runtime display name: `AAK Managed Sessions`
- Runtime ID: `3642145461147533312`
- Runtime location: `us`
- Do not recreate this Runtime merely because a later operation fails.

### Historical bounded managed Session proof

- Synthetic Session ID: `3922508281846693888`
- TTL: `86400s`
- Same identity create/read: PASS
- Cross-user access: denied before provider access
- Same user / wrong AAK scope: denied before provider access

This Session ID is non-secret development evidence. Do not copy it into public/project-facing documentation without a concrete reason.

## 7. Current verified product/security boundaries

### VERIFIED / executable evidence exists

- Vertex/Gemini application seam.
- Authenticated identity binding and Session isolation for the bounded seam.
- Managed Agent Platform Session create/get.
- Cross-user denial before provider access.
- Same-user/wrong-scope denial before provider access.
- Memory Write Gate.
- Native scoped Memory Bank incremental ingestion.
- Generated Memory Bank memory observed.
- Canonical native Memory Bank provider scope preserves both authority dimensions:

```json
{
  "aak_scope": "<authenticated scope>",
  "user_id": "<authenticated user_id>"
}
```

- Intended exact-scope retrieval.
- Wrong-scope provider retrieval isolation.
- Wrong-user provider retrieval isolation.
- Bounded Retrieval Gate + minimal Context Builder.
- Controlled `top_k=2` retrieval with provider-ranked rank-1 admission.
- Unrelated rank-2 candidate excluded from active context in the controlled proof.
- Controlled behavioral proof for:
  - Cold Start
  - Recall
  - Relevance
  - Adaptation
- Focused adaptive-recall tests at the implementation checkpoint: `6/6 PASS`.
- Complete applicable suite at the implementation checkpoint: `31/31 PASS`.
- Parallel Git evidence mediation/reconciliation: **RESOLVED and published** at `7eda888…`.

### Qualification on Relevance

The verified Relevance result is a **controlled provider-ranked top-1 scenario**. It is not evidence of a universal semantic-relevance policy, and AAK currently does not claim a similarity-distance threshold.

### Native provider acceptance mapping

Current independent provider evidence covers the behaviors now registered as `SEC-MB-001–005`. Dedicated requirement-to-test mapping remains incomplete. Do not silently promote `SEC-MB-006/007` to verified merely because their requirements are documented.

## 8. Current incomplete / unresolved boundaries

Do not silently promote these:

- **Correction / supersession:** NOT VERIFIED — remaining fifth core Track 2 behavior.
- Generalized relevance policy: NOT VERIFIED; may not be required for MVP if bounded policy remains sufficient and honestly documented.
- Durable restart-safe AAK scope-authority restoration: UNRESOLVED.
- Production authenticated ingress: NOT VERIFIED.
- Cloud Run deployment: NOT VERIFIED.
- Cloud Run service identity / final runtime IAM: NOT VERIFIED.
- Tool Policy Broker: NOT VERIFIED; implement only if actual product/tool surface requires it.
- Egress/audit controls: incomplete; scope to actual runtime/tool needs.
- Final demo/submission evidence: incomplete.
- Cloud Run region: UNRESOLVED.
- PR/merge into `main`: not performed.

## 9. Latest accepted Codex objective — Git mediation/reconciliation

### Objective

Resolve two valid parallel Git/documentation lines without rewriting history, losing evidence, or allowing the older evidence branch to overwrite newer implementation truth.

The bounded sequence was:

1. preserve `docs/evidence-reconciliation-2026-08-28` at `b42286f…`;
2. preserve `feat/memory-bank-provider` as the current implementation line;
3. classify the six-path `b42286f…` documentation delta;
4. selectively port durable architecture/security material only;
5. keep current README and `PROJECT-STATE.md` authoritative where newer;
6. add native Memory Bank architecture and cross-analysis records;
7. reconcile `SEC-MB-001–007` as requirements without false implementation claims;
8. create one successor documentation commit;
9. publish it only by a verified normal fast-forward;
10. leave `main`, the historical evidence branch, provider/cloud state, and application code untouched.

### Result

**PASS / MEDIATION RESOLVED.**

- Reconciliation commit:
  `7eda888f424d790b1de756a0d4aa05baf00b6867`
- Commit message:
  `docs: reconcile parallel evidence branches`
- Remote branch:
  `origin/feat/memory-bank-provider`
- Local/remote SHAs after publication: MATCH at `7eda888…`
- Tracking: `0 ahead / 0 behind`
- Worktree: CLEAN
- `main`: unchanged at `90f5d106…`
- historical evidence branch: unchanged at `b42286f…`
- no PR/merge/deployment/IAM/provider/Memory Bank/cloud mutation
- no application/test/dependency/lockfile change in the mediation commit

## 10. Prompt / objective checkpoint history

This is a compact recovery ledger, not a transcript archive.

| Stage | Core objective | Outcome |
|---|---|---|
| Identity/Session seam | Bind authenticated `(user_id, scope)` and fail closed | PASS |
| Memory Write Gate | Gate selected Session events before persistent memory | PASS |
| Vertex provider proof | Prove real Gemini/Vertex application call | PASS |
| Managed Sessions | Add managed Sessions and live isolation proof | PASS |
| `uv` lifecycle repair | Replace `/tmp` bootstrap with persistent pinned `uv 0.12.5` | PASS |
| Managed Memory Bank writes | One gated incremental provider ingestion | PASS |
| Infrastructure baseline | Pin Python 3.14.7 + ADK 2.8.0 and revalidate graph | PASS |
| Native scoped Memory Bank | Preserve `aak_scope + user_id`, generate/retrieve, prove isolation | PASS |
| Retrieval + adaptive recall | Bounded gate/context + Cold Start/Recall/Relevance/Adaptation | PASS |
| GitPath documentation | Separate local checkpoint, publication, integration, artifact, deployment evidence | PASS |
| Parallel evidence mediation | Preserve both histories and selectively reconcile durable docs | **PASS / latest** |

## 11. Current next course of action

Do **not** restart Git mediation, architecture research, or completed live proofs.

Critical sequence:

```text
CURRENT PUBLISHED FEATURE TIP 7eda888...
VERIFIED IMPLEMENTATION CHECKPOINT c8f7535...
        ↓
Correction / supersession vertical slice
        ↓
durable restart-safe authority proof
        ↓
Cloud Run deployment + authenticated ingress/service identity
        ↓
final five-behavior + security evidence pass
        ↓
README / architecture diagram / demo / Devpost proof
```

### Immediate next slice

**Correction / supersession** is the next bounded product slice because it is the only remaining unverified member of the five committed Track 2 behavioral families.

Acceptance direction:

```text
existing remembered preference/fact
        ↓
authenticated user explicitly corrects it
        ↓
correction passes the approved persistence boundary
        ↓
later/new-session retrieval
        ↓
stale memory cannot govern behavior
        ↓
corrected value visibly governs the response
```

The implementation must satisfy the existing security requirements, especially:

- `SEC-MW-005`: explicit correction prevents stale/inferred memory from governing current behavior;
- `SEC-MR-003`: superseded/stale memory is excluded or loses precedence to explicit correction.

Do not bundle:

- generalized relevance work;
- Cloud Run;
- Tool Policy Broker unless strictly required by the correction path;
- broad egress/audit infrastructure;
- CI/CD;
- unrelated Git/documentation cleanup.

## 12. Restoration procedure after context/session loss

### A. Verify repository state first

```bash
cd ~/repos/Adaptive-Agent-Kernel
git status --short --branch
git rev-parse HEAD
git ls-remote origin refs/heads/feat/memory-bank-provider
```

Expected published feature checkpoint from this record:

```text
7eda888f424d790b1de756a0d4aa05baf00b6867
```

If current repository evidence is newer, **the newer repository wins**. Never reset backward merely to match this file.

To identify the newest verified implementation checkpoint, inspect current `docs/codex/PROJECT-STATE.md` and Git ancestry rather than assuming the branch tip is an implementation commit.

### B. Verify development tool availability

```bash
/home/bossman/.local/bin/uv --version
```

Expected baseline:

```text
uv 0.12.5
```

Do not reinstall automatically if the result differs. Inspect current repository/tooling state first.

### C. Resume Codex if available

```bash
codex resume 01a02b81-abc5-7c21-97fb-1915dceabb68
```

Then instruct Codex to inspect current repository truth first and continue only from the latest accepted checkpoint.

### D. If the Codex thread cannot be resumed

Start a new Codex thread in `~/repos/Adaptive-Agent-Kernel` and provide only:

1. current bounded objective;
2. this file's latest published branch checkpoint as recovery context;
3. instruction to read `AGENTS.md` and current repository sources of record first;
4. explicit Bossman-approved mutation boundary.

### E. If ChatGPT context is lost

Open the ChatGPT project and supply this private file plus the latest Codex result. Ask ChatGPT to reconcile it against the current repository and external evidence before recommending a consequential mutation.

## 13. Repository sources to read after recovery

This recovery file does not replace:

- `AGENTS.md`
- `docs/architecture/MEMORY-BANK-NATIVE-SCOPE.md`
- `docs/codex/PROJECT-STATE.md`
- `docs/engineering/DEVELOPMENT-PRACTICES.md`
- `docs/research/FINDINGS_REGISTER.md`
- `docs/research/CROSS-ANALYSIS_REGISTER.md`
- `docs/research/security/SECURITY_SOURCE_REGISTER.md`
- `docs/security/THREAT-MODEL.md`
- `docs/security/SECURITY-ARCHITECTURE.md`
- `docs/security/SECURITY-TEST-PLAN.md`

## 14. Consolidation provenance

This canonical record was consolidated from four recovered artifacts supplied on 2026-08-29:

- `AAK_DEV_RECOVERY(1).md` — SHA-256 `f960d93903515e2a2b21a6ad61abb5369a5ff8c5235cc3d589fd1aeeb4295821`
- `AAK_DEV_RECOVERY(2).md` — SHA-256 `f960d93903515e2a2b21a6ad61abb5369a5ff8c5235cc3d589fd1aeeb4295821`
- `AAK_DEV_RECOVERY_UPDATED.md` — SHA-256 `019ffd19b7da9cd1c1f62166ca5d2f19d603522f1caeb58fd7724335f695268e`
- `AAK_DEV_RECOVERY_RECOVERED.md` — SHA-256 `033c191bc03cac057a718cdb91beb521031b2fc94fb98e80b0c02ee912d14ca2`

Reconciliation findings:

- `(1)` and `(2)` are byte-identical and contain the strongest current recovery state.
- `UPDATED` is materially the same but describes the Codex thread more weakly as the last visible/verified thread; Bossman explicitly clarified that `01a02b81-abc5-7c21-97fb-1915dceabb68` is the canonical and only AAK Codex execution thread used to date.
- `RECOVERED` is an older valid checkpoint centered on `c8f7535…`; its `Visibility: PRIVATE` fact was retained because repository privacy was independently revalidated on 2026-08-29.
- Older claims superseded by the later `7eda888…` mediation/publication evidence were preserved only as history, not current state.
- No source artifact is silently discarded as false merely because it is older; later independently verified evidence controls current-state reconciliation.

## 15. Update rule for this recovery file

After each Bossman-accepted development checkpoint, refresh this file with only high-signal recovery information:

- current development branch and last meaningful verified checkpoint (do not hard-code this file's own commit as the branch tip);
- newest verified implementation checkpoint when different from branch tip;
- remote preservation state;
- latest accepted Codex objective and result;
- current verified boundaries;
- remaining blockers;
- next candidate slice;
- thread/resume identifiers if they change.

Do not turn this into a transcript dump, research register, issue tracker, or duplicate `PROJECT-STATE.md`.

**Important self-reference rule:** this tracked recovery index must never claim that its own hard-coded SHA is the current branch tip. Always verify current Git refs first. The file records durable recovery facts and meaningful checkpoints; Git determines the current publication head.

## 16. Tracked recovery-record policy

`AAK_DEV_RECOVERY.md` is intentionally tracked in the **private** repository.

The previously proposed root ignore rule:

```gitignore
/AAK_DEV_RECOVERY.md
```

is **SUPERSEDED** and must not be added for this canonical tracked record.

Rules:

1. Keep credentials and secret material out of this file.
2. Store only non-secret recovery identifiers, evidence checkpoints, current boundaries, and recovery procedures.
3. Current Git/executable/provider evidence outranks this file when newer.
4. `docs/codex/PROJECT-STATE.md` remains the canonical mutable current-state record.
5. This file remains the canonical recovery/continuity index for restoring lost development context.
6. Do not create competing `AAK_DEV_RECOVERY*.md` files in the repository. Consolidate future recovery updates into this one file.
