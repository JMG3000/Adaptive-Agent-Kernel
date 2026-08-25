# Adaptive Agent Kernel — Codex Instructions

## Purpose

Adaptive Agent Kernel (AAK) is the All Things Agentic Hackathon project.

Build the smallest complete, secure, testable MVP that satisfies the current
owner-approved product and Devpost direction.

Bossman is the human authorization boundary.

## Start here

For every non-trivial task:

1. Read this file.
2. Read `docs/codex/PROJECT-STATE.md` if it exists.
3. Inspect the actual worktree, branch, configuration, dependencies, and
   task-relevant documentation.
4. Read only the narrowest additional repository sources needed for the task.

Do not rely on chat history or historical plans when current repository or
provider evidence is available.

When present, use:
- `README.md` for setup, run, and human/submission entry points.
- `docs/requirements/` for binding project and Devpost requirements.
- `docs/architecture/` for durable approved architecture.
- `docs/research/` for validated platform findings and freshness constraints.
- `docs/evaluation/` for behavioral evaluation definitions and evidence.
- `docs/operations/` for environment, deployment, and external-state evidence.
- `docs/engineering/` for approved development practices and engineering workflow.
- `docs/security/` for the approved threat model, security architecture, and security test plan.
- `docs/codex/` for current project state and active execution guidance.

## Authority and scope

Within an explicitly assigned task, proceed independently and make the
smallest complete change required.

Escalate only when a real owner decision is required, including:
- material product-scope or architecture changes;
- new production services or dependencies that change the approved design;
- security or trust-boundary changes;
- contradictory authoritative requirements;
- consequential external actions that were not explicitly authorized.

Tool capability never implies authorization.

Do not silently expand scope.

## Evidence discipline

Inspect before editing and verify before claiming completion.

Preserve pre-existing human worktree changes. Do not revert, overwrite, or discard them unless Bossman explicitly authorizes it. If a human change conflicts with the current task, report the conflict rather than resolving it

Never assume that a file, dependency, plugin, skill, MCP server, cloud
resource, credential, configuration, or integration exists because it was
previously discussed.

Current repository/provider evidence outranks historical assumptions.

If evidence conflicts:
- identify the conflict;
- preserve both claims and their sources;
- do not invent a resolution.

Plans, prompts, tickets, documentation, and reported success are not
implementation evidence by themselves.

## Engineering invariants

- Prefer the smallest complete vertical slice.
- Follow `docs/engineering/DEVELOPMENT-PRACTICES.md` for the approved
  pair-programming, TDD/ATDD, refactoring, and evidence workflow.
- For production behavior changes, use TDD:
  RED → verify the expected failure → GREEN with the minimum implementation
  → verify → REFACTOR while remaining green.
- Do not write production behavior before its failing test unless Bossman
  explicitly approves a documented exception.
- Use acceptance criteria/ATDD for user-visible or cross-component behavior.
- Apply Simple Design / YAGNI; do not implement speculative capability.
- Refactor only from a green baseline and avoid unrelated refactoring.
- Preserve the current approved architecture and scope in
  `docs/codex/PROJECT-STATE.md` unless the task explicitly changes them.
- Keep state boundaries explicit; do not create competing authorities without
  a demonstrated and approved need.
- Add or change dependencies only when required by the task and verified
  against the interfaces actually used.
- Keep behavior observable and testable.
- Only run focused tests for verification, never run the full suite unless necessary for validation of the implementation
- Security-sensitive behavior must be implemented test-first against the approved
  security invariants and fail closed when authorization or provenance is ambiguous.

## Security invariants

- For security-sensitive work, read `docs/security/THREAT-MODEL.md`,
  `docs/security/SECURITY-ARCHITECTURE.md`, and the applicable tests in
  `docs/security/SECURITY-TEST-PLAN.md` before changing behavior.
- Preserve the approved security gates around authenticated identity/session binding,
  untrusted Session history, Memory Bank writes/retrieval, tool authorization,
  egress, and audit decisions. Do not bypass a gate for convenience.
- Treat model/tool choice as proposal, not authorization. Consequential tool calls
  must be authorized outside model reasoning and bound to the current exact call.
- Never commit, print, log, or place secrets or credential contents into model
  context or repository artifacts.
- Apply least privilege at external and cloud boundaries.
- Treat user input, persistent memory, structured profiles, model output, tool
  output, and external data as untrusted at trust boundaries.
- Validate data shapes and external responses instead of guessing.
- Preserve audit, correction, and rollback paths.
- Minimize dependency and supply-chain expansion.
- Do not weaken security controls merely to make a test pass.

Redact secret material if encountered.

## Change workflow

For each coding task:

1. Inspect current state and the applicable acceptance criteria.
2. Identify the smallest complete vertical slice.
3. Write the minimal failing test for the next behavior.
4. Run it and verify that it fails for the expected reason.
5. Write the minimum production change required to make it pass.
6. Run the targeted test and relevant surrounding suite.
7. Refactor only while the tests remain green.
8. Run applicable acceptance/security validation.
9. Inspect final Git diff/status.
10. Return concise reproducible evidence.

For non-behavioral changes where TDD is not meaningful, explain the exception
and run the narrowest appropriate validation instead.

## Git and external actions

Do not modify `main` directly unless Bossman explicitly instructs otherwise.

Use the authorized task/feature branch when branch work is part of the task.

Do not push, merge, open a pull request, deploy, create cloud resources,
alter Devpost/Jira/Confluence, or change account configuration unless
explicitly authorized.

Local implementation and validation do not imply authorization for external
publication or deployment.

## Documentation alignment

When setup, architecture, behavior, or validation changes, update the
appropriate repository documentation.

Keep implementation, tests, README instructions, architecture claims, and
Devpost-facing claims consistent with verified reality.

Use `AGENTS.md` as the durable operating map. Put changing project state,
current architecture selections, implementation progress, and immediate
milestones in `docs/codex/PROJECT-STATE.md` or narrower repository documents.

## Completion report

Return:
- what changed;
- files changed;
- tests/checks run and results;
- relevant Git status/diff evidence;
- unresolved defects or assumptions;
- scope/security concerns;
- the smallest logical next step, if evident.

Do not claim success without direct evidence.
