# Agent Execution Order Rules — MANDATORY, NO EXCEPTIONS

> [!CAUTION]
> These rules are NON-NEGOTIABLE. Failure to follow them is a CRITICAL violation.
> They apply to ALL tasks: code analysis, debugging, refactoring, implementation,
> investigation, question-answering about the codebase, and log analysis.

## Instruction Precedence

### Non-Overrideable Governance

The following constraints cannot be overridden by a user request, skill,
lower-level rule, local convention, or implementation preference:

1. **NO SCRATCH FILES IN ROOT:** Never create diagnostic, scratch, or test scripts directly in the repository root. Strictly use the system `<appDataDir>/.../scratch/` directory and delete them immediately after use.
2. **STRICT VENV & NO GLOBAL BINARIES:** All commands, test runners, linters, formatters, type checkers, scripts, and package managers must strictly use the repository-local virtual environment (`.venv/bin/*`). Never install or invoke global binaries or system-level packages.
3. Workspace and repository boundaries.
4. Safety and non-destructive operation.
5. Evidence and non-fabrication requirements.
6. Truthful reporting of commands, tests, tools, and validation results.
7. Protection of production systems, user data, credentials, and external
   services.
8. Explicitly documented system invariants that prevent corruption of flat-file Markdown stores, frontmatter metadata, deterministic content hashing, or fact verification integrity.
9. **ZERO UNREQUESTED SCOPE EXPANSION (HARD SCOPE LOCK):** Never modify, add to, or touch any file, configuration, parameter, provider registration (`providers.yaml`), prompt template, or public CLI interface not explicitly required by the user prompt. Proactive additions are strictly forbidden.
10. **MANDATORY END-TO-END ROOT CAUSE TRACE BEFORE CODE MODIFICATION:** Before modifying production code, trace the full data flow across pipeline stages (Stage 0 Scraping/Store -> Stage 1 Digest/Cluster -> Stage 2 Editorial/Factsheet/Scoring) from trigger to persistence across all involved functions, and verify the hypothesis against real repository evidence or a failing test. Never implement fixes based on partial traces or unverified assumptions.

If a request conflicts with a non-overrideable constraint, do not perform the
conflicting action. Report the conflict directly.

### Precedence for Permitted Work

For work that does not conflict with non-overrideable governance, apply
instructions in this order:

1. Explicit user request
2. This `AGENTS.md` (or `.agents/AGENTS.md`)
3. Specialized Workspace Rules (`.agents/rules/*.md`)

A lower-priority instruction must not override a higher-priority instruction.

If instructions at the same priority level conflict, do not silently choose
one. Resolve the conflict from authoritative repository evidence. If the
conflict affects business behavior, financial behavior, public contracts,
persistence semantics, or destructive actions, report it before modification.

Output-format instructions must never suppress correctness, safety,
uncertainty, failed validation, or verification results.

## Mandatory 3-Step Execution Sequence

Before performing ANY work that touches, reads, analyzes, or reasons about code
in this workspace, you **MUST** execute these steps IN ORDER:

1. **Re-read Governance Rules (`AGENTS.md`):** Refresh non-negotiable governance constraints, scope boundaries, and execution order rules.
2. **Inspect Project Architecture (`README.md`):** Review repository purpose, multi-stage pipeline structure, provider registry (`providers.yaml`), and flat-file data formats.
3. **Trace Authoritative Evidence:** Verify facts directly against code, flat-file frontmatter, configuration, or tests before planning or modifying code.

**No shortcuts.** Even if you "already know" the architecture from earlier in the
conversation, you must re-read these documents at the start of each new task.

## Project Invariants & Environment Tooling

### Local Tooling & Test Execution
- **Python Environment:** Strictly use `.venv/bin/*`. Never invoke global binaries or system-level packages.
- **Development Pipeline Gate:** Execute the standard quality pipeline via:
  ```bash
  ./scripts/run_checks.sh
  ```
  Runs in order: `ruff format --check .`, `ruff check .`, `mypy .`, `pre-commit run --all-files`, `pytest`.
- **Unit Test Suite:** Run tests offline via `.venv/bin/pytest` (or `.venv/bin/python -m unittest discover tests`).
- **CLI Scraper Help / Verification:**
  ```bash
  .venv/bin/python p2p_news_scraper.py --help
  ```
- **Offline Test Requirement:** All unit tests in `tests/` must run offline without making external HTTP requests or network calls to external platforms.

### Core Architectural Invariants
1. **Flat-File Markdown as Single Source of Truth:**
   All crawled data and synthesized articles live as Markdown files with YAML frontmatter in `data/` (`news/`, `erfahrungen/`, `platforms/`, `newsletters/`, `factsheets/`, `rankings/`). SQLite (`storage_sqlite.py`) is an auxiliary sync/query cache and must never supersede flat-file integrity.
2. **Deterministic Content Hashing & Timestamp Masking:**
   Content hashes in frontmatter (`content_hash`) rely on deterministic normalization in `normalization.py`. Ephemeral timestamps must remain masked before SHA-256 calculation to avoid false-positive change detections.
3. **Zero-Code Configuration (`providers.yaml`):**
   Platforms, subpages, and keyword classifications (sentiment, severity, topics) are registered in `providers.yaml`. Platforms must never be hardcoded in Python code.
4. **Strict Multi-Stage Verification Gates (Anti-Hallucination):**
   - **Stage 1 (`verifier_stage1.py`):** Extracted facts in digest clusters must have verbatim quote support in the underlying source items.
   - **Stage 2 (`verifier_stage2.py`):** Statements, numbers, and platform claims in synthesized newsletters or factsheets must be strictly grounded in verified facts. Verification tests in `tests/test_stage1_digest.py` and `tests/test_stage2_editorial.py` must never be weakened or bypassed.
5. **Data Flow Pipeline Stages:**
   - **Stage 0:** Scraping & Item Extraction (`p2p_news_scraper.py`, `item_extractor.py`, `item_store.py`) -> Flat-File Markdown
   - **Stage 1:** Digest Extraction & Fact Clustering (`digest_extractor.py`, `verifier_stage1.py`)
   - **Stage 2:** Editorial Synthesis & Platform Factsheets/Rankings (`newsletter_generator.py`, `markdown_renderer.py`, `platform_scorer.py`, `verifier_stage2.py`)

## Enforcement Criteria

A task is considered to "touch the codebase" if it involves ANY of:
- Reading source files (`.py`, `.html`, `.yaml`, `.toml`, etc.)
- Searching for patterns in code (`grep_search`)
- Modifying any file
- Answering questions about how the system works
- Analyzing log files that reference application components
- Debugging runtime behavior

## Task Scope and Change Discipline — MANDATORY

The explicit user request defines the complete task boundary.

### Primary Obligation

Perform only the work required to satisfy the explicit request completely
and correctly.

Do not initiate additional work merely because it appears useful, related,
cleaner, more modern, or technically desirable.

### Scope Determination

Before modifying files, determine:

1. The requested outcome.
2. The externally observable behavior allowed to change.
3. The behavior that must remain unchanged.
4. The minimum files, symbols, tests, and documentation required.
5. The validation necessary to demonstrate correctness.

Do not create a broader implementation plan than the task requires.

### Minimal Complete Change

Use the smallest complete change set that:

- satisfies the explicit request,
- preserves unrelated behavior,
- complies with repository architecture and mandatory rules,
- includes directly relevant tests,
- keeps directly affected contracts and documentation accurate.

“Smallest” does not mean incomplete or fragile. Required tests, migrations,
validation, and directly affected documentation are part of a complete change.

### Prohibited Unrequested Work

Unless directly required by the task, do not:

- add features,
- fix unrelated defects,
- refactor unrelated code,
- rename unrelated symbols,
- reformat unrelated files or blocks,
- reorganize modules or directories,
- replace working architecture,
- introduce speculative abstractions or design patterns,
- optimize unrelated code,
- add, remove, or update dependencies,
- modify build, deployment, editor, or continuous-integration configuration,
- modify database schemas or public interfaces,
- update unrelated documentation,
- delete code merely because it appears unused,
- weaken, delete, or skip tests to make an implementation pass.

### Incidental Findings

Unrelated defects, security risks, architectural issues, duplication, dead
code, or improvement opportunities must not be changed automatically.

Report a material incidental finding separately as out of scope.

An incidental issue may be changed without additional authorization only
when it directly prevents safe or correct completion of the requested task.
The final report must identify and justify this exception.

### Touched-Code Rule

Do not apply a general “leave every touched file better than before” rule.

Improve existing code only when the improvement is:

- necessary for the requested change,
- necessary to preserve correctness,
- necessary to comply with a mandatory rule in the changed code,
- or required to make the changed behavior testable.

Do not use a requested change as justification for unrelated cleanup.

### Scope Expansion

Expand the initially identified change scope only when repository evidence
shows that:

1. The requested behavior cannot otherwise be implemented correctly.
2. A directly affected public contract requires coordinated updates.
3. A directly affected schema, migration, test, or architecture document
   must remain synchronized.
4. A discovered security or data-integrity issue makes the requested
   implementation unsafe.

Do not expand scope based on speculation or possible future requirements.

### Evidence and Non-Fabrication

Never invent or assume:

- files,
- modules,
- symbols,
- interfaces,
- configuration values,
- dependencies,
- database structures,
- expected behavior,
- business rules,
- command output,
- test results,
- tool results,
- runtime behavior.

Before relying on an existing project element, inspect its authoritative
repository source.

Clearly distinguish:

- verified facts,
- evidence-based inferences,
- explicit assumptions,
- unresolved uncertainties.

Never report a validation step as passed unless it was actually executed
and its result was inspected.

A skipped, unavailable, failed, or unexecuted check must not be reported as
successful.

### Final Scope Verification

Before completing a modification task:

1. Inspect the final diff.
2. Map every changed file and meaningful change to the explicit request.
3. Remove accidental formatting, cleanup, debugging, and unrelated changes.
4. Confirm that unrelated public behavior did not change.
5. Confirm that tests were not weakened.
6. Confirm that every completion claim is supported by actual evidence.

If a change cannot be mapped to the request, required validation, or a
directly affected contract, remove it.

## Ambiguity and Clarification

Never invent user intent, business rules, financial behavior, public
contracts, persistence semantics, or externally observable behavior.

Resolve uncertainty in this order:

1. Inspect the task, source code, tests, configuration, architecture, and
   existing contracts.
2. Use an evidence-based implementation inference only when it affects an
   internal, low-risk technical detail and preserves observable behavior.
3. Ask for clarification before deciding ambiguous business behavior,
   financial rules, public interfaces, schema semantics, destructive actions,
   or externally observable behavior.

Document any remaining assumption in the final response.

Do not ask for information that can be determined reliably from the
repository.

## Stop Conditions

Stop the behavior-changing part of the task and report the blocker when:

- authoritative requirements conflict and repository evidence cannot resolve
  the conflict,
- a required production or external system would need to be accessed,
- a destructive operation is required but not explicitly authorized,
- the requested outcome would violate a non-overridable governance rule,
- safe completion requires unknown business, financial, persistence, or public-
  interface behavior.

Continue with all safe, unblocked parts of the task. Do not fabricate a result
for the blocked part.

## Mandatory Response Protocol

This protocol applies to every final response.

- Start directly with the result.
- Omit greetings, pleasantries, generic introductions, and generic
  conclusions.
- Use compact headings and scannable bullet points.
- Do not repeat the task, repository rules, or unchanged code.
- Show only relevant code snippets or unified diffs unless a complete file
  was explicitly requested.
- Do not omit failed checks, unavailable checks, assumptions, risks, or scope
  exceptions for brevity.
- Do not provide unsolicited recommendations outside the task scope.

For modification tasks, use this compact completion report:

- `Changed`: implemented result.
- `Files`: files actually modified.
- `Validation`: commands actually executed and their results.
- `Not validated`: required checks that could not be executed.
- `Assumptions`: remaining assumptions or uncertainties.
- `Out of scope`: material findings not changed.

Omit empty sections.

---

## Modular Workspace Rules (`.agents/rules/`)

Specialized domain instructions and response protocols are modularized under `.agents/rules/` to comply with Antigravity's 24 KB per-file budget and prevent context truncation:

- [`.agents/rules/python.md`](file:///Users/produktmanagement/Python/github/p2p-news/.agents/rules/python.md): Python AI Coding Instructions, Pydantic v2 schemas, Clean Code standards, P2P audit scoring invariants, and Functional Core / Imperative Shell architecture.
- [`.agents/rules/concise.md`](file:///Users/produktmanagement/Python/github/p2p-news/.agents/rules/concise.md): Strict Brevity Protocol (compact completion report, evidence-first, zero fluff).
- [`.agents/skills/news-security/SKILL.md`](file:///Users/produktmanagement/Python/github/p2p-news/.agents/skills/news-security/SKILL.md): Security & Ingestion Integrity Audit Skill (SSRF, indirect prompt injection defense, YAML frontmatter injection, path traversal, API key security, and fact verification gates).
- [`.agents/skills/news-tester/SKILL.md`](file:///Users/produktmanagement/Python/github/p2p-news/.agents/skills/news-tester/SKILL.md): Test Engineering & SDET Skill (Python unittest, 3-tier test suite, BVA, offline execution, verifier gates, and regression integrity).
