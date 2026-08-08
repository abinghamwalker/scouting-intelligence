# Scouting Intelligence agent instructions

These instructions apply to the entire repository. The controlling specifications are
`../scouting-ml-production-blueprint.html` and
`../scouting-ml-agent-implementation-workflow.html`. If this file and either approved
plan disagree, stop and return the conflict to the master.

## Mission and current boundary

Build a local, provider-neutral ML research workbench for governed football data. The
core product lets a researcher select a real player or weighted football profile,
retrieve and compare candidates from the full eligible population, evaluate the method,
and save a reproducible experiment. It supplies traceable resemblance evidence and
uncertainty; it does not make a recruitment decision.

W01 and W02 established the accepted local foundation and agent control plane. W03 and
later approved phases may proceed continuously only through master-issued, phase-bounded
packets and the acceptance loop defined below. A later phase must not start until its
declared dependency is independently verified and checkpointed, except for the explicit
research-workbench pivot authority below. That authority makes accepted W07 the dependency
for the redesigned W09 and freezes W08 as a dormant optional module.

The repository, environments, data, models, services, reports, and checkpoints remain
local. No cloud resource, public endpoint, hosted CI, remote repository, external model
call, or deployment is authorised.

## Authority

The master is the only integration and evidence authority. The master:

- owns the plan, phase registry, dependency graph, task packets, and path assignments;
- classifies existing changes before dispatch;
- reviews every changed file and artifact;
- independently reruns required checks;
- accepts, rejects, narrows, or returns work with concrete evidence;
- owns dependency changes, migrations, model promotion, and every Git operation;
- writes gate reports and creates local checkpoint commits and tags.

A subagent implements only one bounded packet. A subagent:

- reads this file and every `read_first` path in its packet before editing;
- changes only `allowed_paths` and treats all other paths as forbidden;
- does not delegate unless the packet explicitly permits it;
- does not run any Git command and never stages, commits, tags, branches, stashes,
  resets, checks out, rebases, cleans, or edits `.git`;
- does not modify `pyproject.toml`, `uv.lock`, migrations, shared contracts, registry
  aliases, or orchestration integration files unless the packet expressly owns them;
- does not self-approve or expand scope;
- runs the packet's bounded checks through `uv`;
- returns the mandatory handback and stops.

Subagent work is not accepted until the master reproduces its evidence. “Mostly works”
is `REWORK`, not acceptance.

## Continuous phased execution

The user authorised continuous execution from W03 through the remaining approved
workflow on 2026-07-29. The root agent in this task remains the logical master
orchestrator across every phase. Conversation compaction or a new subagent must not
transfer master authority; durable continuity lives in this file, the master plan,
phase registry, packets, reviews, reports, commits, and local tags.

For each phase, the master:

1. verifies the declared accepted dependency and creates the next local start tag; W09
   depends on accepted W07 under the research-workbench pivot authority below and does not
   depend on a W08 pilot result; W10 depends on the accepted, Unicode-corrected W09 authority;
2. decomposes the phase into bounded packets with exact path ownership;
3. delegates implementation by default when a task is independently testable and
   delegation is more efficient than direct master implementation;
4. keeps shared contracts and migrations serial under explicit master allocation and
   second-review requirements, while dependency/lock state, orchestration integration,
   phase evidence, commits, and tags remain master-owned;
5. reads every returned change and artifact, independently reruns the named checks, and
   issues bounded rework for anything incomplete, incorrect, unsafe, or insufficiently
   evidenced;
6. integrates only accepted work, runs the complete phase gate, and creates the local
   checkpoint commit and annotated accepted tag;
7. advances to the next approved phase without waiting for routine checkpoint review.

Never delegate an open-ended phase or allow a subagent to self-approve. Pause continuous
execution only when a genuine blocker requires user clarification or a change to the
approved architecture, project root, dependency policy, local-only boundary, data-rights
authority, or product decision that the controlling specifications do not resolve.

## Research-workbench pivot authority

The user authorised a product pivot on 2026-08-05 after directly attempting the W08 pilot.
This authority supersedes the former W08 staged-progression rule:

- Stop the W08 pilot. Do not recruit more participants or require T7, G-W08A or G-W08B to
  progress the ML research product. Retain the partial capture as an honest product-direction
  finding, not representative-user acceptance or expert relevance evidence.
- Freeze the W08 authentication, workflow, audit, export and study surfaces as a dormant
  optional collaboration module. Preserve their code and tests; do not delete or weaken their
  security boundaries. Do not expose them in the core research journey.
- W09 is the accepted and CLOSED `Historical-player ML research workbench` phase. It depended on
  W07 plus this explicit user authority, not on W08 closure or pilot evidence. W10 now consumes
  the accepted, Unicode-corrected W09 authority.
- The current historical Wyscout population is the authorised end-to-end demonstration
  source. W09 must replace the one-row Gold proof and synthetic demonstration catalogue with
  a versioned feature matrix and retrieval index over the full eligible player population.
- Synthetic data is test-fixture material only. It must not appear as the interactive product
  candidate universe or be used to imply retrieval quality.
- A future licensed current-data source must enter through a separately authorised provider
  adapter with rights, credential/network, mapping, capability, identity, rebuild and parity
  validation. This authority does not grant external access.
- Automatic experiment provenance replaces manual audit form-filling in the core journey.
  Every run still binds source, canonical data, feature, model/index, query, filter, output,
  metric, code and checksum versions.
- W06 remains `NO_GO` for positive expert-relevance or recruitment recommendation claims.
  Missing expert labels block those claims, not honest engineering and evaluation of the
  historical research workbench.
- Reactivating W08 as a user-facing collaboration workflow, conducting representative-user
  acceptance, or starting a shadow recruitment pilot requires a separate product decision
  after the real-data research vertical slice is useful and independently reviewed.
- W09 is CLOSED. W10 is the active rework phase for a frozen-query football-expert relevance
  assessment; the deferred W04 runtime host-state hardening is already retained. Its authority is
  `docs/architecture/w10-expert-relevance-validation.md` plus the active v2 addendum.
- W10 engineering may proceed to an independently reviewed engineering-ready milestone. The formal
  study requires user approval of its digest-bound protocol and real eligible human evidence.
  Mechanics pilots, synthetic fixtures and the user's informal W09 walkthrough do not count toward
  G-RW4.
- On 2026-08-06 the first W10 mechanics pilot established that participant presentation v1 exposed
  minutes and identity context but no substantive playing evidence. The user withdrew v1 for
  formal collection before any formal response. W10 is in rework under
  `docs/architecture/w10-expert-evidence-presentation-v2-addendum.md`; the retained v1 approval and
  incomplete pilot cannot unlock v2, and no formal study may start before fresh v2 approval.
- G-RW4 returns PASS, FAIL or INSUFFICIENT_EVIDENCE under preregistered rules. W10 cannot close and
  W11 cannot begin merely because the study software or a mechanics pilot works.

## Standing bounded-correction authority

The user authorised the master on 2026-08-02 to decide and progress the smallest sound
implementation correction without a user approval pause when it preserves the approved
logical semantics, product scope, local-only boundary, and evidence strength. This
authority includes serialization and Arrow projections, physical schema descriptors,
predicate operands and constants, test completeness, mechanical derivations from accepted
algorithms, implementation defects, and refactors.

Producer failures and reviewer findings automatically enter bounded rework, fresh
independent review, and master acceptance. Necessary changes to unaccepted or derived
schema descriptors, root-content bytes, digests, tests, and reports are authorised; the
meaning and formula of an accepted digest are not. A repeated bounded blocker requires the
master to reframe, narrow, or split the packet and add adversarial evidence, not pause for
user approval merely because three correction attempts have occurred.

User approval is still required when a correction would change a logical model, root
roster, feature, product population, intended output, accepted source/data-rights
authority, or digest meaning; weaken reversibility, validation, completeness, temporal
safety, or evidence guarantees; introduce a dependency, provider/network access, external
service, cloud resource, deployment, publication, secret, credential, or cost; require a
destructive action; or choose between materially different product behaviours.

## Local Git safety

- The only branch is `main`.
- `git remote` must print nothing at every gate.
- `.git/hooks/pre-push` must print the local-only policy and exit `1`.
- Only the master may operate Git.
- Never hide or discard changes with stash, reset, checkout, clean, rebase, or history
  rewriting.
- Generated data and run artifacts remain ignored; reviewed manifests and gate reports
  are committed.

Any remote, missing guard, unexplained dirty path, or Git operation by a subagent stops
the task.

## Python and dependency authority

- Python is exactly 3.12 as constrained by `.python-version` and
  `requires-python = ">=3.12,<3.13"`.
- `uv` owns the single root `pyproject.toml`, `uv.lock`, and `.venv`.
- Run every Python command through `uv run`; do not use bare `python` or `pip`.
- Begin every master review with `uv sync --locked --all-groups`.
- Do not create requirements files, alternate lockfiles, nested environments, or Node
  package-manager manifests.
- Git/direct URL dependencies are forbidden. Python-index resolution is allowed by the
  approved plans.
- Only a master-issued dependency packet may change `pyproject.toml` or `uv.lock`.

## Container-free runtime authority

- ADR 0004 is programme-wide and supersedes the former PostgreSQL/pgvector and Redis
  Compose topology.
- The application, worker, migrations, modelling, evaluation and tests run only from
  the root `uv` environment.
- Embedded SQLite is the operational store; guarded Parquet plus DuckDB/Polars is the
  analytical store; vector retrieval uses versioned local artifacts and in-process
  Python.
- Dockerfiles, Compose files, development containers, container SDKs, external
  databases, Redis, queue/cache services and mandatory service processes are
  forbidden.
- No task or later wave may reintroduce one of those components without retained
  necessity evidence, explicit user approval, a new accepted ADR, amendments to both
  controlling plans and an updated governance gate.
- If a packet or plan appears to require a container or external service, stop and
  return the conflict rather than implementing it.

## Task lifecycle

The phase state machine is:

`PLANNED → READY → DISPATCHED → IMPLEMENTED → MASTER_REVIEW → REWORK → VERIFIED → CHECKPOINTED → CLOSED`

A packet must name:

- task and phase IDs, objective, dependencies, assigned role, and risk;
- `read_first`, `allowed_paths`, and `forbidden_paths`;
- deliverables and definition of done;
- exact acceptance checks and stop conditions;
- the mandatory return template;
- whether further delegation is forbidden.

Parallel dispatch is exceptional. It is allowed only when all write scopes are
path-disjoint and none touches shared contracts, migrations, dependency/lock files,
phase registries, aliases, or integration surfaces. Shared paths are always serial.

## Mandatory return

Use `orchestration/templates/subagent_return.md`. Every handback includes:

- task ID and one-sentence objective;
- exact changed-file list;
- behaviour implemented and key choices;
- exact commands, exit statuses, and concise results;
- artifact/evidence paths and identifiers;
- residual risks;
- concrete follow-ups or `none`;
- confirmation of no Git operations, no unauthorised dependency/lock changes, and no
  edits outside `allowed_paths`.

An incomplete handback is rejected before implementation review.

## Module routing

- `src/scouting/contracts/`: strict cross-boundary payloads; imports no other project
  module.
- `sources/` and `identity/`: provider parsing and canonical identities.
- `data_products/`: Bronze, Silver, Gold, and temporal products.
- `features/` and `roles/`: deterministic feature state and role taxonomy.
- `modeling/` and `evaluation/`: artifacts, experiments, metrics, and gates.
- `serving/`: the single retrieval/explanation path; never training or provider reads.
- `policy/`, `workflow/`, and `observations/`: post-model constraints and human work.
- `storage/`: guarded local persistence.
- `operations/`: jobs, observability, failure handling, and recovery.
- `web/`, `apps/web/`, and `services/`: presentation and composition only.
- `audit/`: immutable material-action records; depends only on contracts.

Do not create parallel `backend/`, `frontend/`, `notebooks/`, `utils/`, nested project,
or nested environment roots without a master-approved ADR.

## Verification

The shared master suite is:

```text
uv sync --locked --all-groups
uv run ruff format --check .
uv run ruff check .
uv run mypy src/scouting scripts
uv run lint-imports
uv run pytest -q
uv run bandit -q -r scripts src
uv run python scripts/install_local_git_guards.py --check
uv run python scripts/verify_local_only.py
uv run python scripts/verify_phase.py --phase <Wxx>
git status --short
git remote
```

Subagents run only the narrower checks named in their packets. Risk-specific checks are
additive; they never replace the shared suite.

## Stop conditions

Stop and report rather than improvising when:

- approval, dependency state, ownership, or allowed paths cannot be resolved by the master
  within the standing bounded-correction authority;
- a task needs a new licence, credential, external account, remote service, or
  deployment;
- user-owned work overlaps the packet or unexpected paths change;
- a destructive action or history rewrite appears necessary;
- the lock/environment is not reproducible;
- a secret or restricted datum appears in tracked files or output;
- a high-severity security, leakage, temporal, identity, or data-rights issue remains;
- a required correction crosses the standing bounded-correction boundary described above.

Routine implementation defects, serialization contradictions, physical representation
choices, schema-descriptor corrections, invalid predicate operands/constants, incomplete
tests, failed reviews, changed derived digests, and repeated bounded rework are not user
stop conditions. The master records them, issues bounded rework, obtains fresh review, and
continues.

The return must state the exact blocker, safe checks attempted, evidence, and smallest
decision required.
