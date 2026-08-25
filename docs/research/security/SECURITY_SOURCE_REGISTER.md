# Adaptive Agent Kernel — Security Research Source Register

**Baseline date:** 2026-08-24\
**Repository path:** `docs/research/security/SECURITY_SOURCE_REGISTER.md`\
**Status:** Canonical security source catalog / research provenance\
**Origin:** Renamed from `AAK_SECURITY_RESEARCH_SOURCE_REGISTER_2026-08-24.md`; Git history should preserve subsequent changes.\
**Purpose:** Preserve the primary security sources and current academic literature supporting the approved Adaptive Agent Kernel security architecture baseline.

## Evidence discipline

This register distinguishes:

- **PRIMARY_PLATFORM** — Google/Google Cloud/Google ADK documentation or source.
- **PRIMARY_VULNERABILITY** — NVD/CVE record or vendor patch for a disclosed vulnerability.
- **VENDOR_SECURITY_RESEARCH** — Google/Mandiant security research.
- **VENDOR_ISSUE_REPORT** — public Google ADK issue; useful evidence but not equivalent to a CVE.
- **ACADEMIC_PREPRINT** — publicly indexed research preprint; not assumed peer-reviewed unless independently verified.

Research findings do not become implementation decisions without Bossman adoption.

---

## 1. Google Memory Bank / Sessions architecture

### Memory Bank quickstart with ADK
**Class:** PRIMARY_PLATFORM\
https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank/adk-quickstart

Supports:
- `VertexAiMemoryBankService` as the ADK Memory Bank wrapper.
- `add_events_to_memory()` for selected/incremental Session events.
- `add_session_to_memory()` for full-session ingestion.
- incremental event ingestion is the documented recommended option.
- `search_memory()` retrieves memories for the current `user_id` and `app_name`.

Architecture relevance:
`SESSION SERVICE -> MEMORY WRITE GATE -> MEMORY BANK`.

### Memory Bank API quickstart
**Class:** PRIMARY_PLATFORM\
https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank/api-quickstart

Supports:
- ordered Session events as source material for memory generation.
- events may include user, agent, and tool interactions.
- default generated-memory scope is `{"user_id": session.user_id}` unless explicitly overridden.

Architecture relevance:
identity/session binding and Memory Bank scope integrity.

### Memory Bank security / governance
**Class:** PRIMARY_PLATFORM\
https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank

Supports:
- Google explicitly identifies prompt injection and memory poisoning as long-term-memory risks.
- recommended mitigations include Model Armor, adversarial testing, sandboxing, strict access control, and human review.

Architecture relevance:
MEMORY WRITE GATE, RETRIEVAL GATE, secure-by-design adversarial tests.

### Memory Bank IAM Conditions
**Class:** PRIMARY_PLATFORM\
https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank/iam-conditions

Architecture relevance:
least privilege and memory-scope authorization.

### Sessions IAM Conditions
**Class:** PRIMARY_PLATFORM\
https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/sessions/iam-conditions

Architecture relevance:
authenticated-user/session authorization and `userId` controls.

### Memory Bank troubleshooting
**Class:** PRIMARY_PLATFORM\
https://docs.cloud.google.com/gemini-enterprise-agent-platform/troubleshooting/memory-bank

Supports:
- Memory generation is not automatically triggered merely by configuring `VertexAiMemoryBankService`.
- Session events must be populated and an explicit memory-generation operation must occur.

---

## 2. Google ADK disclosed vulnerabilities and patches

### CVE-2026-18236 — continuation forgery in tool confirmations
**Class:** PRIMARY_VULNERABILITY\
https://nvd.nist.gov/vuln/detail/CVE-2026-18236

Google patch:
https://github.com/google/adk-python/commit/c03f333769feaeaa9fe8910fbe95cb9f2d513f54

Supports:
- manipulated/injected Session-history events could forge a tool-confirmation continuation.
- authorization must verify the registered tool, confirmation requirement, original call, call identity/name, and exact arguments.

Architecture relevance:
TOOL POLICY BROKER; current approval; exact-call binding; fail-closed continuation validation.

### CVE-2026-4810 — unauthenticated remote code execution
**Class:** PRIMARY_VULNERABILITY\
https://nvd.nist.gov/vuln/detail/CVE-2026-4810

Supports:
- affected ADK versions could permit unauthenticated remote code execution on Python OSS, Cloud Run, and GKE deployments.
- patched versions require upgrade and redeployment.

Architecture relevance:
authenticated ingress is a distinct security boundary; HITL confirmation does not replace network authentication.

---

## 3. Google/Mandiant security research

### AI risk and resilience: A Mandiant special report
**Class:** VENDOR_SECURITY_RESEARCH\
https://cloud.google.com/security/resources/ai-risk-and-resilience

Supports:
- persistent malicious prompts can amplify ordinary access-control flaws.
- Mandiant reported changing a user ID to write a malicious prompt into another user's profile, causing repeated future exfiltration by the victim's agent.
- prompt injection can be hidden in multimodal content.
- monitoring agent tool-execution sequences and behavioral anomalies is recommended.

Architecture relevance:
authenticated user/session binding, persistent-memory integrity, INPUT TRUST BOUNDARY, OUTPUT/EGRESS SECURITY GATE, AUDIT/DECISION LEDGER.

---

## 4. Google ADK public issue reports requiring tracking

These are evidence-bearing reports, but they are **not treated as published CVEs unless separately disclosed as such**.

### Issue #6461 — A2A peer can forge HITL approval
**Class:** VENDOR_ISSUE_REPORT\
https://github.com/google/adk-python/issues/6461

Architecture relevance:
approval provenance must identify the authorized human; `author == "user"` is not sufficient authority.

### Issue #6831 — A2A task response poisons later delegation state
**Class:** VENDOR_ISSUE_REPORT\
https://github.com/google/adk-python/issues/6831

Architecture relevance:
A2A/session-event role integrity; reinforces deferring A2A from Option B until separately threat-modeled.

### Issue #6410 — A2A session-history limiting ignored
**Class:** VENDOR_ISSUE_REPORT\
https://github.com/google/adk-python/issues/6410

Architecture relevance:
full history may be loaded despite configured limits; relevant to data minimization, context exposure, and A2A attack surface.

### Issue #4309 — failed A2A task errors leak into conversation history
**Class:** VENDOR_ISSUE_REPORT\
https://github.com/google/adk-python/issues/4309

Architecture relevance:
Session history is untrusted data; internal errors/stack traces must not silently become ordinary model context.

### Issue #6115 — GCS artifact path validation / cross-user access
**Class:** VENDOR_ISSUE_REPORT\
https://github.com/google/adk-python/issues/6115

Architecture relevance:
validate `user_id`, `app_name`, `session_id`, and other resource identifiers before using them as authorization or storage-path components.

---

## 5. Academic literature discovered in the 2026-08-24 refresh

**Elicit status:** attempted, but the connected Elicit plan returned `api_access_denied`; its API/MCP requires a plan with API access. No paper below is falsely represented as Elicit-validated.\
**Consensus status:** attempted as a fallback, but the connected account had exhausted its monthly search allowance.\
**Discovery method for papers below:** public scholarly/web indexes. Treat as ACADEMIC_PREPRINT unless peer-review status is independently verified.

### Securing LLM-Agent Long-Term Memory Against Poisoning: Non-Malleable, Origin-Bound Authority with Machine-Checked Guarantees
**Class:** ACADEMIC_PREPRINT\
https://arxiv.org/abs/2606.24322

Key relevance:
- models a memory write-retrieve-act pipeline.
- argues that content-only trust scoring and ordinary lineage can be laundered.
- finds write-time origin binding necessary in its formal model.
- directly strengthens the `MEMORY WRITE GATE` requirement to preserve non-malleable origin/authority information.

### Hidden in Memory: Sleeper Memory Poisoning in LLM Agents
**Class:** ACADEMIC_PREPRINT\
https://arxiv.org/abs/2605.15338

Key relevance:
- studies delayed, cross-session memory poisoning.
- poisoned state can remain dormant and later trigger attacker-intended behavior.
- supports dedicated write, retrieval, and delayed-activation security tests.

### When Agents Remember Too Much: Memory Poisoning Attacks on Large Language Model Agents
**Class:** ACADEMIC_PREPRINT\
https://arxiv.org/abs/2607.06595

Key relevance:
- introduces GhostWriter memory poisoning against tool-using personal agents.
- proposes both a memory-saving policy and a retrieval screen.
- directly supports retaining separate `MEMORY WRITE GATE` and `RETRIEVAL GATE` controls.

### MemMorph: Tool Hijacking in LLM Agents via Memory Poisoning
**Class:** ACADEMIC_PREPRINT\
https://arxiv.org/abs/2605.26154

Key relevance:
- poisoned long-term memory biases agent tool selection.
- connects memory integrity directly to the Tool Policy Broker threat model.

### Memory poisoning and secure multi-agent systems
**Class:** ACADEMIC_PREPRINT\
https://arxiv.org/abs/2603.20357

Key relevance:
- examines poisoning across semantic, episodic, short-term, and multi-agent memory systems.
- highlights additional risk from agent-to-agent interaction.
- supports keeping A2A/multi-agent functionality deferred until separately threat-modeled.

### Capability Gates Are Not Authorization: Confused-Deputy Failures in LLM Agent Frameworks
**Class:** ACADEMIC_PREPRINT\
https://arxiv.org/abs/2606.28679

Key relevance:
- distinguishes tool availability/capability from per-call authorization.
- evaluates deterministic per-call value authorization.
- independently supports AAK's `TOOL POLICY BROKER`, fail-closed authorization, and exact-call/argument binding.

### NetInjectBench: Benchmarking Indirect Prompt Injection in Tool-Using Large Language Model Agents for Network Operations
**Class:** ACADEMIC_PREPRINT\
https://arxiv.org/abs/2607.10490

Key relevance:
- evaluates execution-time controls for tool-using agents under indirect prompt injection.
- supports separating trusted policy metadata from untrusted artifact content and applying an execution-time policy gate.

### AgentDyn: A Dynamic Open-Ended Benchmark for Evaluating Prompt Injection Attacks of Real-World Agent Security System
**Class:** ACADEMIC_PREPRINT\
https://arxiv.org/abs/2602.03117

Key relevance:
- demonstrates that real-world indirect prompt-injection defenses remain fragile or over-defensive.
- supports adversarial testing rather than assuming prompt-level filtering is sufficient.

### Indirect Prompt Injections: Are Firewalls All You Need, or Stronger Benchmarks?
**Class:** ACADEMIC_PREPRINT\
https://arxiv.org/abs/2510.05244

Key relevance:
- studies modular tool-input and tool-output firewalls.
- also shows benchmark weaknesses and practical bypasses.
- useful as defense-in-depth evidence, but does not displace AAK's authorization broker or Session/Memory controls.

---

## 6. Final pre-implementation validation delta — 2026-08-24

### Additional Memory Bank write surfaces
**Class:** PRIMARY_PLATFORM\
https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank\
https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank/api-quickstart\
https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank/revisions

Supports:
- Memory Bank supports `GenerateMemories` from conversation/session data.
- Memory Bank also supports direct `CreateMemory` / direct-memory upload paths.
- memory revisions are created for direct and generated mutation paths.

Architecture consequence:
- every AAK-supported persistent-memory mutation path must remain behind the
  AAK Memory Write Gate;
- Option B exposes incremental Session-event ingestion as the reference path;
- direct model-controlled `CreateMemory` is not exposed in v0.1;
- whole-session or other write modes are controlled paths, not bypasses.

### Model Armor integration overview
**Class:** PRIMARY_PLATFORM\
https://docs.cloud.google.com/model-armor/integrations\
https://docs.cloud.google.com/model-armor/model-armor-mcp-google-cloud-integration

Supports:
- Model Armor can inspect and, for supported integrations, block content on
  Agent Platform interactions.
- REST API use is detector-style: the application consumes the verdict and
  decides what action to take.
- supported Google/Google Cloud MCP integration sanitizes selected MCP payloads,
  including `tools/call`, `prompts/get`, and tool execution errors.
- coverage is integration- and payload-specific; it is not a universal
  authorization mechanism.

Architecture consequence:
Model Armor is defense-in-depth. It does not replace the Memory Write Gate,
Retrieval Gate, Tool Policy Broker, authenticated approval, or egress policy.

### Issue #6721 — relayed A2A human-input/approval resume failure
**Class:** VENDOR_ISSUE_REPORT\
https://github.com/google/adk-python/issues/6721

Architecture relevance:
- reinforces keeping A2A outside Option B;
- approval/human-input state must be bound to the correct invocation and relay
  path;
- failure to resume a gated operation must fail visibly rather than fabricate
  successful tool execution.

## 7. Current assessment after the refresh

The refreshed evidence **supports rather than overturns** the approved AAK security architecture baseline.

Strongest reinforced controls:

1. `SESSION SERVICE -> MEMORY WRITE GATE -> MEMORY BANK` is consistent with Google's actual ADK/Memory Bank event-ingestion contract.
2. The Memory Write Gate should preserve origin/provenance and must not rely only on semantic trust scoring.
3. A distinct Retrieval Gate remains justified because poisoned memories can be benign-looking at write time and harmful when activated later.
4. `TOOL POLICY BROKER` remains critical: tool exposure is not authorization; approval must be bound to the exact current call and material arguments.
5. Session-history events are not automatically authoritative; CVE-2026-18236 demonstrates direct exploitation of confirmation state carried through Session history.
6. A2A remains appropriately deferred for Option B because current ADK reports show unresolved role/authority and state-contamination risks.
7. The Audit/Decision Ledger should log decision metadata, provenance, denials, approvals, and anomaly indicators without becoming a raw-secret or raw-prompt archive.

## 8. Recommended next evidence actions

- Security claims approved for implementation are mirrored at claim level in `docs/research/FINDINGS_REGISTER.md` with stable IDs.
- `docs/security/THREAT-MODEL.md`, `docs/security/SECURITY-ARCHITECTURE.md`, and `docs/security/SECURITY-TEST-PLAN.md` are the approved implementation-facing security documents.
- Convert the strongest invariants into TDD/ATDD security regressions before production behavior.
- Re-run Elicit when API access is available; do not retroactively label web-discovered preprints as Elicit results.
