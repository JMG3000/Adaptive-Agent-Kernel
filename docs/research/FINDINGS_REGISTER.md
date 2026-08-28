# Findings Register

Purpose: claim-level evidence register for Adaptive Agent Kernel.\
Baseline date: 2026-08-21.\
Last security reconciliation: 2026-08-24.

| ID | Finding | Classification | Status | Primary evidence |
|---|---|---|---|---|
| F-001 | Every track requires Gemini 3.5+ via Gemini API or Vertex AI. | Contest requirement | VALIDATED | S-DEVPOST-RULES |
| F-002 | Every track requires at least one Google Agent Framework. | Contest requirement | VALIDATED | S-DEVPOST-RULES |
| F-003 | Every track requires at least one Google Cloud infrastructure service. | Contest requirement | VALIDATED | S-DEVPOST-RULES |
| F-004 | Track 2 is named Collaborative Partner. | Contest requirement | VALIDATED | S-DEVPOST-RULES |
| F-005 | Track 2 should clarify, guide, capture feedback, and adapt to the user's way of thinking. | Track requirement | VALIDATED | S-DEVPOST-RULES |
| F-006 | Multiple submissions are allowed only when each is unique and substantially different. | Submission constraint | VALIDATED | S-DEVPOST-RULES |
| F-007 | Submitted work must be newly created during the submission period; incorporated pre-existing work must be disclosed. | Submission constraint | VALIDATED | S-DEVPOST-RULES |
| F-008 | Gemini 3.5 Flash model ID is `gemini-3.5-flash`. | Platform fact | VALIDATED | S-GCP-GEMINI-35-FLASH |
| F-009 | ADK supports persistent Memory Bank through `VertexAiMemoryBankService`. | Platform fact | VALIDATED | S-GCP-MEMORY-ADK |
| F-010 | ADK supports Agent Platform Sessions through `VertexAiSessionService`. | Platform fact | VALIDATED | S-GCP-SESSIONS-ADK |
| F-011 | Google documents deployment of ADK agents to Cloud Run. | Platform fact | VALIDATED | S-GCP-CLOUD-RUN-ADK |
| F-012 | Memory Bank can be used with ADK agents running on Cloud Run. | Platform fact | VALIDATED | S-GCP-MEMORY-ADK |
| F-013 | Memory Bank structured profiles use static schemas for evolving user/profile data. | Platform fact | VALIDATED | S-GCP-MEMORY-PROFILES |
| F-014 | Memory Bank maintains memory revisions that can be inspected as memories evolve. | Platform fact | VALIDATED | S-GCP-MEMORY-OVERVIEW |
| F-015 | Memory Bank generation is not automatically triggered just by configuring `VertexAiMemoryBankService`. | Implementation constraint | VALIDATED | S-GCP-MEMORY-TROUBLESHOOTING |
| F-016 | A qualifying memory-ingestion/generation path must explicitly invoke session-to-memory generation or equivalent event-ingestion logic. | Design consequence | VALIDATED / DECIDED | F-015; S-GCP-MEMORY-ADK |
| F-017 | New Memory Bank instances default to `gemini-3.5-flash` for memory generation effective 2026-06-29. | Platform default | VALIDATED | S-GCP-MEMORY-SETUP |
| F-018 | Memory Bank defaults similarity search to `text-embedding-005` when not configured. | Platform default | VALIDATED | S-GCP-MEMORY-SETUP |
| F-019 | Memory Bank defaults to no TTL when TTL is not configured. | Platform default | VALIDATED | S-GCP-MEMORY-SETUP |
| F-020 | `us-central1` currently supports Agent Platform Runtime, Sessions, and Memory Bank. | Platform fact | VALIDATED | S-GCP-AGENT-LOCATIONS |
| F-021 | Memory Bank and Sessions support `us`/`eu` multi-regional and global endpoints. | Platform fact | VALIDATED | S-GCP-AGENT-LOCATIONS |
| F-022 | Vertex AI is preferred over standalone Gemini API for this project. | Architecture choice | DECIDED | Internal architecture decision |
| F-023 | Cloud Run is the v0.1 qualifying Google Cloud infrastructure service. | Architecture choice | DECIDED | Internal architecture decision + S-GCP-CLOUD-RUN-ADK |
| F-024 | Firestore is not necessary to satisfy v0.1 requirements and is deferred until authoritative application data requires it. | Architecture choice | DEFERRED | Internal scope decision |
| F-025 | Adaptive Agent Kernel is the project name, not the official track name. | Naming / scope | DECIDED | Internal project decision + F-004 |
| F-026 | ADK Memory Bank supports incremental selected-event ingestion with `add_events_to_memory()` and whole-session ingestion with `add_session_to_memory()`; Google documents incremental processing as the recommended option. | Platform fact | VALIDATED | S-GCP-MEMORY-ADK |
| F-027 | Memories generated from Agent Platform Sessions are keyed by `session.user_id` by default unless an explicit scope is supplied. | Platform fact / security boundary | VALIDATED | S-GCP-MEMORY-API; S-GCP-MEMORY-IAM |
| F-028 | Memory Bank supports direct memory mutation paths including `CreateMemory` in addition to generated-memory paths. | Platform fact / security boundary | VALIDATED | S-GCP-MEMORY-API; S-GCP-MEMORY-REVISIONS |
| F-029 | Google explicitly identifies prompt injection and memory poisoning as risks for long-term Memory Bank and recommends layered mitigations including access control, adversarial testing, sandboxing, human review, and Model Armor. | Platform security fact | VALIDATED | S-GCP-MEMORY-OVERVIEW |
| F-030 | Memory Bank and Sessions expose IAM/condition mechanisms that can constrain access using user/session scope information. | Platform security fact | VALIDATED | S-GCP-MEMORY-IAM; S-GCP-SESSIONS-IAM |
| F-031 | CVE-2026-18236 demonstrates that manipulated Session-history confirmation state could authorize unintended ADK tool execution unless confirmation is bound to the registered tool and original call/arguments. | Vulnerability | VALIDATED | S-NVD-CVE-2026-18236; S-ADK-PATCH-18236 |
| F-032 | CVE-2026-4810 demonstrates that affected ADK deployments could expose unauthenticated remote code execution and require upgrade/redeployment. | Vulnerability | VALIDATED | S-NVD-CVE-2026-4810 |
| F-033 | Mandiant reported a persistent-agent compromise in which an access-control flaw allowed a user-ID change to plant a malicious persistent instruction in another user's profile and trigger repeated future exfiltration. | Vendor security research | VALIDATED | S-MANDIANT-AI-RISK |
| F-034 | ADK issue #6461 reports that an A2A peer can be represented as `user` in a way that can interact with HITL confirmation semantics; the report is open and is not treated as a published CVE. | Vendor issue report | VALIDATED / UNRESOLVED | S-ADK-ISSUE-6461 |
| F-035 | ADK issue #6721 reports a 2.7.0 A2A regression in relayed human-input/approval resume handling that can prevent the gated remote invocation from resuming and, under a legacy path, yield fabricated-result behavior. | Vendor issue report | VALIDATED / UNRESOLVED | S-ADK-ISSUE-6721 |
| F-036 | ADK issue #6831 reports A2A state contamination involving synthesized user-authored function-response state; it remains issue evidence rather than a published CVE. | Vendor issue report | VALIDATED / UNRESOLVED | S-ADK-ISSUE-6831 |
| F-037 | Model Armor supports inspection/blocking in supported Agent Platform integrations, while REST API use returns detections for application policy logic; Model Armor does not itself replace application authorization. | Platform security capability | VALIDATED | S-GCP-MODEL-ARMOR-INTEGRATIONS |
| F-038 | Model Armor's Google/Google Cloud MCP integration sanitizes selected payload classes such as `tools/call`, `prompts/get`, and tool execution errors; coverage is not universal across all MCP payloads. | Platform security capability | VALIDATED | S-GCP-MODEL-ARMOR-MCP |
| F-039 | Public preprint research formalizes long-term-memory poisoning as a write→retrieve→act security problem and argues for origin-bound/non-malleable authority at memory-write time. Peer-review status is not established by this register. | Academic preprint evidence | VALIDATED AS SOURCE | S-ARXIV-ORIGIN-BOUND-MEMORY |
| F-040 | Public preprint research distinguishes capability/tool availability from per-call authorization and supports deterministic value/call binding. Peer-review status is not established by this register. | Academic preprint evidence | VALIDATED AS SOURCE | S-ARXIV-CAPABILITY-GATES |
| F-041 | The corrected AAK security architecture baseline—identity/session binding, input trust boundary, untrusted Session history, Memory Write Gate, Retrieval Gate, Context Builder, Tool Policy Broker, egress gate, and Audit/Decision Ledger—is owner-approved. | Architecture choice | DECIDED | Bossman approval 2026-08-24 + F-026–F-040 |
| F-042 | A2A/multi-agent behavior is excluded from Option B until separately threat-modeled and validated. | Scope/security choice | DECIDED / DEFERRED | Bossman approval 2026-08-24 + F-034–F-036 |
| F-043 | Option B will expose incremental Session-event ingestion as the reference persistent-memory path; direct model-controlled `CreateMemory` or uncontrolled continuous-ingestion paths must not bypass the AAK Memory Write Gate. | Security architecture choice | DECIDED | Bossman approval 2026-08-24 + F-026, F-028 |
| F-044 | Model Armor is approved as defense-in-depth for applicable deployment paths but is not the authorization, memory-integrity, or approval authority. Exact deployment configuration remains implementation-time work. | Security architecture choice | DECIDED | Bossman approval 2026-08-24 + F-029, F-037, F-038 |
| F-045 | AAK's security-sensitive Memory Bank adapter uses the native API and constructs exact provider scope only as `{"aak_scope": authenticated_scope, "user_id": authenticated_user_id}`; the prior `app_name + raw user_id` projection is superseded and remains unmigrated legacy evidence. | Security architecture choice | DECIDED / VALIDATED | Bossman approval 2026-08-28; S-GCP-MEMORY-API; executable AAK tests/provider proof 2026-08-28 |
| F-046 | One bounded live native Memory Bank proof completed gated incremental ingestion/generation, retrieved the generated Memory in its exact two-key scope, and returned no Memory for separate same-user/wrong-scope and wrong-user/same-scope provider requests. | Implementation/provider evidence | VALIDATED | Executable AAK provider proof 2026-08-28 |
| F-047 | One bounded live adaptive-recall proof queried the authenticated native scope with `top_k=2`, admitted only the provider-ranked relevant rank-1 memory, excluded the unrelated returned candidate from active context, and visibly changed the new-Session recommendation from the Cold Start response. This is controlled-scenario evidence, not a universal semantic-relevance policy. | Implementation/provider evidence | VALIDATED | Executable AAK provider proof and regression tests 2026-08-28 |

## Source registry

### S-DEVPOST-OVERVIEW
https://allthingsagentichackathon.devpost.com/

### S-DEVPOST-RULES
https://allthingsagentichackathon.devpost.com/rules

### S-GCP-GEMINI-35-FLASH
https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-5-flash

### S-GCP-MEMORY-ADK
https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank/adk-quickstart

### S-GCP-MEMORY-API
https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank/api-quickstart

### S-GCP-MEMORY-OVERVIEW
https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank

### S-GCP-MEMORY-PROFILES
https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank/profiles

### S-GCP-MEMORY-SETUP
https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank/setup

### S-GCP-MEMORY-REVISIONS
https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank/revisions

### S-GCP-MEMORY-TROUBLESHOOTING
https://docs.cloud.google.com/gemini-enterprise-agent-platform/troubleshooting/memory-bank

### S-GCP-MEMORY-IAM
https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank/iam-conditions

### S-GCP-SESSIONS-ADK
https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/sessions/manage-with-adk

### S-GCP-SESSIONS-IAM
https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/sessions/iam-conditions

### S-GCP-AGENT-LOCATIONS
https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/agent-locations

### S-GCP-CLOUD-RUN-ADK
https://docs.cloud.google.com/run/docs/ai/build-and-deploy-ai-agents/deploy-adk-agent

### S-NVD-CVE-2026-18236
https://nvd.nist.gov/vuln/detail/CVE-2026-18236

### S-ADK-PATCH-18236
https://github.com/google/adk-python/commit/c03f333769feaeaa9fe8910fbe95cb9f2d513f54

### S-NVD-CVE-2026-4810
https://nvd.nist.gov/vuln/detail/CVE-2026-4810

### S-MANDIANT-AI-RISK
https://cloud.google.com/security/resources/ai-risk-and-resilience

### S-ADK-ISSUE-6461
https://github.com/google/adk-python/issues/6461

### S-ADK-ISSUE-6721
https://github.com/google/adk-python/issues/6721

### S-ADK-ISSUE-6831
https://github.com/google/adk-python/issues/6831

### S-GCP-MODEL-ARMOR-INTEGRATIONS
https://docs.cloud.google.com/model-armor/integrations

### S-GCP-MODEL-ARMOR-MCP
https://docs.cloud.google.com/model-armor/model-armor-mcp-google-cloud-integration

### S-ARXIV-ORIGIN-BOUND-MEMORY
https://arxiv.org/abs/2606.24322

### S-ARXIV-CAPABILITY-GATES
https://arxiv.org/abs/2606.28679

## Update protocol

When a source invalidates a finding:

1. preserve the existing row ID;
2. change its status to `SUPERSEDED` or `INVALIDATED`;
3. append a replacement finding with a new ID;
4. note the date and replacement source;
5. update dependent architecture/security documents.

Do not silently rewrite historical evidence.
