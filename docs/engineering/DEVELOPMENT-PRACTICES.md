# Adaptive Agent Kernel — Development Practices

**Status:** DECIDED\
**Purpose:** Durable engineering-development methodology for Adaptive Agent Kernel.

This document defines how implementation work is performed. It complements
the root `AGENTS.md` and does not replace the current architecture or project
state recorded in `docs/codex/PROJECT-STATE.md`.

## Pair-programming model

AAK uses a human-in-the-loop pair-programming model.

- **Bossman** is the human pair, product/architecture authority, and acceptance
  boundary.
- **ChatGPT** acts as navigator/research/review support: requirements analysis,
  acceptance-criteria framing, architecture analysis, reconciliation, and
  review.
- **Codex CLI** acts as the implementation driver: repository inspection,
  tests, code changes, debugging, local validation, Git evidence, and bounded
  engineering execution.

The objective is continuous collaboration and review, not unsupervised batch
code generation.

## Core development loop

For behavioral implementation work:

Requirement
→ acceptance criterion
→ smallest complete vertical slice
→ RED
→ verify RED
→ GREEN
→ verify GREEN
→ REFACTOR
→ verify GREEN
→ security/acceptance validation
→ evidence review
→ integrate
→ retrospective when useful
→ next smallest slice

## Test-driven development

For production behavior changes, use Red → Green → Refactor.

### RED

1. Define one behavior.
2. Write the smallest test that expresses that behavior.
3. Run the test.
4. Verify that it fails for the expected reason.

A test that passes immediately does not demonstrate the intended missing
behavior. A test that errors for an unrelated reason must be corrected until
it fails for the intended reason.

### GREEN

1. Write only the production code required to make the failing test pass.
2. Do not add speculative features, abstractions, or generalization.
3. Run the targeted test.
4. Run relevant surrounding tests.

### REFACTOR

Refactor only after the relevant tests are green.

Refactoring may improve names, structure, duplication, or maintainability, but
must not introduce unrequested behavior. Keep the suite green throughout.

### TDD exceptions

TDD may be inappropriate for some non-behavioral work, such as certain
generated artifacts, documentation-only edits, or configuration changes where
a failing executable test has no meaningful interpretation.

When an exception is necessary:
- keep it narrow;
- state why test-first behavior is not meaningful;
- perform the narrowest appropriate validation;
- do not use the exception to bypass behavioral tests.

## Acceptance-test driven development

Use ATDD for user-visible and cross-component behavior.

Translate important requirements into observable scenarios before or alongside
implementation.

For example:

Given a retained belief exists\
When the user explicitly corrects that belief\
Then later behavior uses the corrected value\
And the superseded belief no longer controls current behavior

Acceptance tests should connect requirements to executable evidence wherever
practical.

For the Option B reference kernel, the primary acceptance families are:

1. Cold Start
2. Recall
3. Relevance
4. Adaptation
5. Correction

Detailed acceptance definitions may move to
`docs/evaluation/ACCEPTANCE-TESTS.md` when implementation makes that document
necessary.

## Small complete vertical slices

Prefer one independently demonstrable capability at a time.

A slice should cross the minimum layers necessary to prove useful behavior
without building unrelated infrastructure.

Avoid large horizontal batches such as implementing all persistence,
interfaces, deployment, UI, and observability before any end-to-end behavior
can be demonstrated.

Each completed slice should leave the repository in a working, testable state.

## Simple Design and YAGNI

Implement only what the current approved behavior requires.

Do not add:
- speculative abstractions;
- unused extensibility;
- unapproved services;
- duplicate authorities;
- premature generalization;
- future-track functionality;
- infrastructure that the current slice does not require.

Prefer the simplest design that satisfies the current tested behavior while
preserving approved architectural boundaries.

## Continuous refactoring

Refactor continuously in small increments after behavior is protected by
tests.

Do not combine an unrelated cleanup campaign with a bounded feature or bug fix.

If a larger refactor becomes necessary, treat it as a separate bounded task
with its own tests, evidence, and review.

## Continuous integration

When CI is introduced, it should enforce the repository's real development
contract rather than create a second development process.

CI should grow from validated local commands and may include, as appropriate:

- formatting/lint checks;
- unit tests;
- integration tests;
- acceptance/regression tests;
- security checks;
- dependency/supply-chain checks;
- OCI clean-room build validation;
- artifact/SBOM/provenance checks.

Do not create CI merely for appearance. Introduce it when it can reliably
reproduce validated local behavior.

## Source control and deployment environments

Deployment environments and Git branches are separate concerns. Prefer the
simplest source-control topology that preserves review and reproducibility.
Introduce persistent promotion branches only when their operational need is
demonstrated. Promote the same tested revision or artifact between environments
whenever practical.

## Secure-by-design testing

Treat security properties as behavior where practical.

For AAK security-sensitive work, `docs/security/SECURITY-TEST-PLAN.md` is the
acceptance-level security contract. Implement or update its applicable failing
tests before changing protected behavior. `docs/security/THREAT-MODEL.md` and
`docs/security/SECURITY-ARCHITECTURE.md` define the threats and invariants those
tests protect.

For each meaningful trust boundary, consider:
- what enters the boundary;
- what is trusted or untrusted;
- what authority the component has;
- how malformed or malicious input is handled;
- how secrets are protected;
- how failure, correction, and rollback work.

Convert material security invariants into tests when they can be observed
reliably.

Examples include:
- explicit correction must outrank stale memory;
- malformed persistent data must fail safely;
- untrusted model/tool output must not gain unauthorized authority;
- secret material must not be persisted into ordinary logs or memory records.

Security controls must not be weakened merely to make tests pass.

Authorization, identity/scope binding, memory-write/retrieval policy, and egress
controls must fail closed when required provenance or authority is absent or
ambiguous. Model output is never sufficient evidence of authorization.

## Evidence-based completion

A task is not complete because code was written or a process returned success.

Completion evidence should include the narrowest applicable set of:

- the failing test observed before implementation;
- passing targeted tests;
- relevant broader test results;
- acceptance/security validation;
- changed files;
- Git diff/status evidence;
- unresolved assumptions or defects;
- explicitly unverified areas.

For AAK behavioral work, import success, process startup, or HTTP 200 alone is
not sufficient evidence.

## Retrospectives and process correction

After a meaningful vertical slice, incident, or repeated workflow problem,
briefly evaluate:

- what worked;
- what failed;
- what caused human/agent friction;
- what test caught useful behavior;
- what escaped testing;
- whether an instruction was unclear or redundant;
- whether architecture or research assumptions changed.

Update only the narrowest appropriate source:

- durable Codex operating rule → `AGENTS.md`;
- current implementation state → `docs/codex/PROJECT-STATE.md`;
- engineering methodology → this document;
- external/platform research claim → `docs/research/FINDINGS_REGISTER.md`;
- security research source/provenance → `docs/research/security/SECURITY_SOURCE_REGISTER.md`;
- security architecture/test contract → `docs/security/`;
- one-off task detail → immediate task prompt.

Do not turn every retrospective observation into a permanent rule.

## Scope discipline

The methodology does not authorize implementation by itself.

Bossman remains the authorization boundary. Current approved architecture,
scope, exclusions, and immediate objective are defined by current owner
instructions and `docs/codex/PROJECT-STATE.md`.

When methodology and a task-specific owner instruction conflict, stop and
surface the conflict rather than silently choosing one.
