# Code review — scouting-intelligence (W10 excluded)

**Scope reviewed:** `src/scouting/**`, `services/**`, `apps/web/static/w09/**`, plus the storage/audit/policy
foundation. **Excluded per instruction:** everything W10 — `web/w10_expert_study.py`,
`contracts/expert_relevance.py`, `evaluation/expert_relevance.py`, `storage/expert_study.py`,
`data_products/wyscout/expert_evidence.py`, `services/api/w10_study_main.py`,
`apps/web/{static,templates}/w10*`, `scripts/*w10*`.

**Baseline:** `uv run ruff check .` → clean. `uv run mypy src/scouting` → clean (95 files).
`uv run pytest -q` → **4 failed, 3080 passed** in 34m17s (see M-7; the failures are in an in-scope
W04 module). Nothing else below is a lint or typing defect; these are design, performance, and
semantic findings.

---

## 1. Complexity

### C1 — W09 matrix/index validation is implemented twice, in full
`serving/research.py:173-476` (`_validate_matrix_authority`, `_validate_index_authority`) vs
`modeling/research.py:396-575, 909-1059` (`load_feature_matrix`, `load_research_index`).
~300 lines re-implement the same invariants: canonical row ordering, grain uniqueness,
player/competition/season uniqueness, eligibility-to-row binding, pin drift, feature-name order,
catalogue↔matrix zip comparison, and the `(raw - center) / scale` vector reproduction.
**Why it matters:** two copies of a safety-critical invariant set will drift; a fix applied to one
is silently absent from the other. It also doubles the cost of every service construction (see P-5).
**P1** → Extract one `verify_matrix_authority(...)` / `verify_index_authority(...)` in `modeling`
and have `serving` call it, or make `ResearchServingService` accept only objects that
`load_*` already produced and drop the re-validation.

### C2 — `_construct_ledgers` is a 272-line function with six responsibilities
`features/historical.py:840-1109`. It builds the competition index, team index, player index +
catalogue, match index, appearance grouping, then eligibility decisions, matrix rows, and the
population ledger.
**Why it matters:** nothing in it is independently testable, and the eligibility-reason precedence
(lines 977-984) is buried 140 lines from the function head. **P2** → split into
`_index_entities`, `_group_appearances`, `_decide_eligibility`, `_build_matrix_rows`.

### C3 — `load_wyscout_source_config` is ~460 lines
`sources/wyscout.py:349-809`, one top-level function. **P2** → decompose per config section.

### C4 — `build_historical_canonical` is ~388 lines
`data_products/wyscout/historical.py:1488-1876`. **P2** → same treatment.

### C5 — `M0ServingCore._result` is ~270 lines with 11 keyword parameters
`serving/m0.py:642`. Eleven required kwargs is a sign the surrounding class is holding state that
should be passed as one object. **P2** → introduce a `_ResultContext` dataclass.

### C6 — Five copies of the "dump then re-validate" idiom
`api/research.py:132` `_fresh_model`, `serving/research.py:89` `_fresh_model`,
`evaluation/research.py:532` `_fresh`, `storage/research.py:85,94`
`_validated_experiment`/`_validated_receipt`, `reporting/research.py:48,57`
`_validated_result`/`_validated_comparison`. Same body, five error types.
**Why it matters:** a new engineer cannot tell whether the differences are meaningful. **P2** →
one generic helper parameterised by the exception type.

### C7 — `_replay_receipt` writes the same 15-field literal three times
`api/research.py:556-620` constructs `identity_draft`, `digest_draft`, and the final receipt from
the same field set. A field added to two of the three silently changes identity semantics.
**P2** → build one `dict` and splat it.

### C8 — Fake path threaded through a validator
`modeling/research.py:376`: `manifest_path=manifest_root / "placeholder"` exists only to satisfy
`_require_mode_paths`, which then takes `.parent`. **P3** → give `_require_mode_paths` a
`manifest_root` parameter.

### C9 — `invalid_grains` mutated as an out-parameter
`features/historical.py:696-770`. `_stream_action_aggregates` returns aggregates but *also*
mutates a caller-owned set. **P3** → return it alongside the aggregates.

### C10 — Function-local `import json` inside a hot helper
`storage/guarded.py:101`, in `_metadata`, called on every artifact write. **P3** → move to
module scope with the other imports.

### C11 — `_code_digest` duplicated
`features/historical.py:828` and `data_products/wyscout/historical.py:473` are the same algorithm
over different file pairs. **P3** → one shared helper taking the paths.

### C12 — ~780 lines of module-level corpus construction
`contracts/wyscout_schema.py:337+` runs `model_dump` list comprehensions at import.
Measured: 335 ms self-time, 507 ms cumulative for `import scouting.contracts.wyscout_schema`.
Every script pays it. **P3** → move behind `functools.cache`d accessors.

---

## 2. Performance

### P-1 — `AuditLedger.append` re-verifies the whole chain on every append → O(n²)
`audit/ledger.py:145`. `append()` calls `self.verify(...)`, which `SELECT`s **all** receipts for
the tenant (`.all()`, line 227-240) and recomputes every event digest and receipt digest.
Appending receipt *n* costs *n* SHA-256 rounds; a 10k-entry ledger costs 50M hash operations to fill.
**Why it matters:** an append-only audit ledger is exactly the structure that grows without bound;
this makes write latency grow linearly forever and memory grow with the tenant's full history.
(W08 is dormant, which is the only reason this is not already biting.)
**P1** → verify only the tail (last receipt digest + sequence) on append; keep the full-chain
verify as an explicit maintenance/audit operation.

### P-2 — Per-action-row work in the feature build is quadratic in appearances
`features/historical.py:736-800`, the innermost loop over every canonical action row:
- line 760-764 rebuilds `appearances_in_match` from scratch **per action row**, iterating that
  player's whole appearance list and constructing a `UUID` per appearance → O(actions × appearances/grain);
- lines 740-747 construct four `UUID`s per row;
- lines 782-798 call `canonical_json_bytes` per row, which runs `unicodedata.normalize("NFC", ...)`
  on every key and string value.

On a full Wyscout season (~3M actions, ~30 appearances/grain) that is tens of millions of redundant
UUID constructions and ~30M NFC normalizations. **P1** → precompute
`{(grain, match_id): frozenset[team_id]}` once before the scan; hash the lineage key with a fixed
struct-packed layout instead of canonical JSON; hoist UUID parsing.

### P-3 — `compare()` re-runs the entire population scoring to prove reproduction
`serving/research.py:706-713`. Every comparison request calls `execute_query` again on the full
admitted population purely to assert `reproduced == validated_result`. The result was already
digest-verified by the contract validator and cached by `ResearchApiRuntime`.
**P1** → compare `result_digest` against the cached authority instead of recomputing.

### P-4 — `score_vector_rows` is a pure-Python per-row loop
`m0/scoring.py:122-177`. For each admitted candidate it slices a numpy row, does a small numpy
subtract, then drops to Python: `tuple(_canonical_finite_float(item) for item in ...)`,
`stable_finite_sum(...)` (`math.fsum`), and for cosine `tuple(map(float, candidate))` +
`stable_weighted_unit_components` — all at Python speed, per candidate.
**Why it matters:** the module docstring and the W09 UI both promise "score the entire admitted
population"; that promise is what makes this the hot path. Vectorized numpy would be 2-3 orders of
magnitude faster. **P1** → compute distances with a single `(V - q)` broadcast and `np.einsum`,
and reserve the exact `fsum` path for the `limit` rows that are actually returned and explained.

### P-5 — Per-request O(N) rebuilds of immutable index data
`serving/research.py:616-623` on **every** query: a full `(N × k)` copy of the vector matrix, a
fresh N-element tuple of `VectorCandidateKey` dataclasses, then `score_vector_rows:74` builds
`set(candidate_keys)` (N UUID+str hashes) to check uniqueness. All three inputs are immutable and
already validated at construction.
Compounding this, `api/research.py:222-225` runs `_fresh_model` (a full pydantic
dump→re-validate) over **every** matrix row at runtime construction, duplicating the validation
already done in `load_feature_matrix` and again in `_validate_matrix_authority` (C1).
**P1** → cache `keys` on the service; cache the per-active-index vector slice keyed by
`active_indices`; skip the uniqueness re-check when keys came from the validated catalogue.

### P-6 — `list_experiments` is an N+1 with disk I/O per row
`storage/research.py:252-269` → `_verified_experiment_from_row` (line 474) per row, which
(a) re-decodes and canonicalises four JSON blobs, (b) re-validates the full `SavedResearchExperiment`
including every candidate and contribution, (c) calls `_read_report` → a **disk read + SHA-256 of the
entire report payload**, and (d) re-serializes everything via `_experiment_parameters` to compare.
`api/research.py:419-423` then runs `_fresh_model` over each result a second time.
So `GET /api/w09/experiments` does N full report reads and ~6N canonical serializations.
**P1** → make the list endpoint return a projection from the indexed columns; move full report
verification to `GET /experiments/{id}` and `/report`.

### P-10 — Raw event JSON is fully re-parsed per partition
`sources/wyscout_historical.py:689-703`. The aggregate at line 678-682 already scans all partition
paths; the loop then runs `SELECT DISTINCT matchId FROM read_json_auto(?)` per partition, re-parsing
each raw events file, plus `load_partition_matches(partition)`. **P1** → obtain per-partition match
ids from the single grouped aggregate query (`GROUP BY` the partition column).

### P-11 — Whole source objects buffered in memory and hashed twice
`sources/wyscout.py:1700-1727`. `storage.read_bytes("source", object_path)` loads each figshare
object entirely into memory, then computes MD5 and SHA-256 over the full buffer and passes it to
`admit_archive`. The Wyscout v5 objects are multi-hundred-MB archives. **P1** → stream and hash
incrementally.

### P-7 — Unbounded in-process result caches
`api/research.py:239-240`. `_results` and `_comparisons` are plain dicts that are only ever written
to; every query result (with its full candidate list and per-feature contributions) is retained for
the process lifetime. **P2** → bounded LRU with an explicit, documented eviction policy.

### P-8 — `search_players` full-scans and full-sorts on every request
`api/research.py:270-288`. Filters the whole matrix, then sorts the entire filtered set
(calling `.casefold()` inside both the filter predicate and the sort key, per row, per request),
then slices one page. **P2** → precompute a casefolded, pre-sorted index at construction and
bisect into it; the row set is immutable.

### P-9 — `RLock` held across report rendering, disk I/O, and full re-scoring
`api/research.py:363-410` holds `self._lock` while rendering the HTML/JSON report and calling
`self._store.save_experiment` (SQLite + guarded artifact write); `api/research.py:436-496` holds it
while `execute_query` scores the whole population and while listing replay receipts. FastAPI runs
these `def` endpoints in a threadpool, so concurrent users serialize behind the slowest operation.
**P2** → hold the lock only around the cache mutations.

### P-12 — N+1 SELECT per link
`web/w08.py:1019-1035` and `web/w08.py:1510-1525`: one `SELECT … WHERE role_brief_id=? AND version=?`
per link inside a loop. **P2** → one query with an `IN`/`VALUES` join.

### P-13 — Double serialization per row on the Parquet artifact path
`modeling/research.py:310-322`. `table.to_pylist()` materialises every row as Python dicts, then each
row is re-serialized with `canonical_json_bytes` and parsed again by `model_validate_json`.
**P2** → validate from the dict via `model_validate` and canonicalise only for the digest.

### P-14 — Query normalization recomputed per candidate
`serving/research.py:851-854`. `stable_weighted_unit_components(query_scaled, weights)` is
identical for every candidate in the loop. **P3** → hoist above the loop.

### P-15 — `pool_pre_ping=True` on SQLite
`storage/embedded.py:129`. Issues a probe query on every pool checkout for an embedded file
database that cannot go stale. **P3** → remove.

---

## 3. Logic issues

### L-1 — A player with two seasons in one competition breaks *every* query for that competition
`serving/research.py:801-804`. `_filter_population` raises
`"selected competition resolves multiple admitted grains for one player"` when a player has more than
one admitted grain. But the matrix invariant (enforced at `serving/research.py:270`, and identically
in `modeling/research.py:526-530`) is uniqueness on **(player_id, competition_id, season_id)** — so
`(p, c, 2017/18)` and `(p, c, 2018/19)` are both legal matrix rows, both survive the competition
filter, and the second one raises.
**Why it matters:** this is a data-shaped landmine, not a bug in today's single-season corpus. The
moment a second season is admitted the entire retrieval endpoint fails closed for that competition,
with an error message that points at the query rather than at the ingest.
**P1** → decide the intended semantics explicitly: either add `season_id` to
`ResearchQueryFilters` and filter on it, or pick the newest grain per player deterministically and
record the choice in the population accounting.

### L-2 — Zero-vector cosine silently returns an arbitrary ranking
`m0/scoring.py:146-151`. When `query_is_zero or candidate_is_zero`, `distance = 1.0` and all
contributions are zeroed. If the *query* is the zero vector, every candidate ties at 1.0 and the
final sort key (`m0/scoring.py:181`) falls through to `player_id.bytes` — the "most similar players"
list is really the lowest UUIDs, presented with no warning and with an all-zero contribution table
that looks like a legitimate explanation.
Reachability: a weighted-profile query whose values equal the population median on every active
feature scales to zero. Narrow, but the UI defaults every profile field to `0` and every weight to
`1`, so users do land near degenerate inputs.
**Why it matters:** this project's stated discipline is never to imply retrieval quality it cannot
support. A silently arbitrary ranking is the exact failure mode that discipline exists to prevent.
**P1** → raise, or return a first-class `degenerate_query` status and surface it in
`ResearchQueryResult.warnings`.

### L-3 — Audit-chain verification depends on a process-global side effect
`storage/embedded.py:123-124` calls `sqlite3.register_adapter(UUID, str)` and
`sqlite3.register_adapter(datetime, lambda v: v.isoformat())` as a side effect of
`create_embedded_engine`. `audit/ledger.py:111-116` `_stored_timestamp` requires
`parsed.isoformat() == encoded`.
Verified: with an engine built any other way, SQLAlchemy binds the datetime as
`'2026-08-06 10:29:00.305023+00:00'` (space separator); `fromisoformat(...).isoformat()` returns a
`T` separator, the equality fails, and **every `AuditLedger.verify` raises `AuditIntegrityError`**.
```
'2026-08-06 10:29:00.305023+00:00'
roundtrip equal: False
```
**Why it matters:** the ledger's integrity check is coupled to an unrelated constructor having run
first, process-wide. A script or test that builds its own engine gets a "tampered chain" verdict on
a pristine ledger. **P1** → store `occurred_at`/`recorded_at` as explicitly formatted strings at the
call site, or register the adapters at module import in `audit/`, not as an engine side effect.

### L-4 — HTTP status chosen by substring-matching an exception message
`api/research.py:645-654`:
```python
message = str(exc).casefold()
code = (
    409
    if any(m in message for m in ("stale", "incompatible", "drift", "tamper", "reproduce"))
    else 422
)
```
**Why it matters:** rewording a `ResearchServingError` message silently flips the response between
409 and 422, which the client branches on (`workbench.js:108-113`). **P2** → give
`ResearchServingError` a typed subclass or a `conflict: bool` attribute.

### L-5 — Lineup coverage is a tautology
`features/historical.py:1061-1065`:
```python
lineup_matches_observed = (len(played_match_ids),)
lineup_matches_expected = (len(played_match_ids),)
```
Observed and expected are the same expression, so lineup coverage always reads *N/N* and can never
detect a gap — yet `workbench.js:480` renders it to the user as coverage evidence.
**P2** → derive `expected` from the squad/fixture ledger, or delete the field rather than ship a
metric that cannot fail.

### L-6 — Hardcoded coverage and confidence in M0 serving
`serving/m0.py:665-680`: `DataCoverage(overall=1.0, …)` with literal
`observed_count=6, expected_count=6` for `feature_completeness`, and
`ConfidenceAssessment(score=1.0, …)`. Twelve lines above, the code validates against
`len(manifest.feature_names)` — so if the registry ever moves off 6 features, the coverage evidence
silently lies while the validation passes.
**P2** → compute from `manifest.feature_names` and the actual row, or mark the field as not-computed.

### L-7 — Ownership enforcement keyed on an action-name suffix, plus a hardcoded policy exemption
`policy/authorization.py:158`: `if request.action.endswith("_owned") and …` — object-ownership is
enforced only for actions whose *name* ends in `_owned`. Line 165 hardcodes
`request.action not in {"role_brief.approve"}` as an `OWNER_ONLY` visibility exemption.
**Why it matters:** the class docstring calls this a "frozen policy" loaded from YAML, but two
authorization rules live in Python and are invisible to anyone auditing the policy file. A future
owner-scoped action named without the suffix gets no ownership check at all. **P2** → move both into
the policy document as explicit per-action `requires_owner` / `visibility_exempt` flags.

### L-9 — Lineage digest depends on undocumented ordering
`features/historical.py:731-800`. `aggregate.lineage_hasher` is order-sensitive; the order is
(manifest artifact listing order) × (Parquet row order). Neither is asserted anywhere.
**Why it matters:** the whole replay-receipt mechanism rests on this digest. A rebuild that emits
partitions in a different manifest order produces a different `source_lineage_digest` → different
matrix digest → `INCOMPATIBLE_PINS` on every saved experiment, with no diagnostic pointing at the
cause. **P2** → sort `action_paths` explicitly and assert the ordering, or make the digest
order-independent (sort the per-grain action keys before hashing).

### L-10 — Non-atomic index write poisons the output directory on crash
`modeling/research.py:677-704`. `_preflight_and_write` opens the target with `O_EXCL` and writes in
place. A crash mid-write leaves a short file; every subsequent run then hits
`"immutable index artifact conflicts at …"` forever, because the preflight compares bytes.
Note the sibling code in `storage/guarded.py:280-311` does this correctly (temp file + `os.link`).
**P2** → reuse the guarded write-temp-then-link pattern.

### L-8 — Internal exception text is surfaced to the browser
`api/research.py:664` puts `str(exc)` in `HTTPException.detail`; `workbench.js:92` reads
`payload.detail` and renders it. Messages include artifact paths and internal role names.
Local-only by ADR, so exposure is bounded. **P3** → map to stable reason codes.

### L-11 — Plain `sum()` where the codebase otherwise mandates stable summation
`features/historical.py:498`: `total = float(sum(minutes for _, minutes in played))`. Every other
aggregation path uses `stable_finite_sum` / `math.fsum`. Deterministic here only because the input
order is fixed. **P3** → use `math.fsum` for consistency with the stated numeric discipline.

### L-12 — `finally: os.fsync(parent_fd)` can mask the original exception
`storage/guarded.py:320`. If `fsync` raises during unwinding it replaces the real
`ArtifactConflictError`/`OSError`. **P3** → wrap in `try/except OSError` or move outside the
error path.

### L-13 — Dead defensive branch
`policy/authentication.py:75`: `self._records or ((_DUMMY_DIGEST, None),)` — the constructor
(line 54-55) already rejects an empty mapping, so the dummy-comparison fallback is unreachable.
**P3** → remove, or drop the constructor check if the fallback is the intended behaviour.

### L-14 — Permission check makes externally-written artifacts permanently unreadable
`storage/guarded.py:345`: any file with group/other bits set raises
`"artifact target has unsafe permissions"`. A file written by a script under a default `umask 022`
(mode 0644) can never be read back, and the error points at security rather than at the umask.
**P3** → keep the check but say what to do about it in the message.

### L-15 — Unknown replay status renders as "undefined"
`workbench.js:562-567`: `messages[receipt.status]` with three hardcoded keys; a fourth status from
the server yields `"undefined Receipt …"`. **P3** → default branch.

### L-16 — Telemetry redaction accepts bools and unbounded strings
`operations/telemetry.py:122`: `isinstance(value, (str, int))` — `bool` is an `int` subclass, and
string attributes (e.g. `path`) have no length bound while only the record *count* is capped.
**P3** → bound value length; handle `bool` explicitly.

---

## 4. Missing / incomplete implementation

### M-1 — Search pagination is implemented server-side and unreachable client-side
`api/research.py:691-698` exposes `offset` (up to 100 000) and returns `total_matches`.
`workbench.js:253` hardcodes `limit: "50"`, never sends `offset`, and there is no paging control —
yet line 247 reports `"${payload.total_matches} eligible player row(s) match the governed search."`
**Why it matters:** over a full-population matrix the UI tells the user there are N matches while
making N−50 of them unreachable. **P2** → add paging controls, or say "showing first 50 of N".

### M-2 — The idempotent-save path cannot be reached from the UI
`workbench.js:535` mints a fresh `crypto.randomUUID()` for `experiment_id` on every save click.
`api/research.py:517-537` (`_existing_experiment`) and `storage/research.py:170-177,605-622`
(insert-race resolution) implement careful save idempotency that no client can ever exercise;
meanwhile a double-click creates two identical experiments under different ids.
**P2** → derive `experiment_id` deterministically from `(result_digest, comparison_digest, name,
note, report_format)`, which also makes the server-side conflict checks meaningful.

### M-6 — The entire missing-feature reporting surface is inert
`serving/research.py:818` hardcodes `missing_feature_exclusions=0`; line 907 hardcodes
`missing_features=()`. Matrix rows are validated to have *no* missing features
(`serving/research.py:303-311`, `modeling/research.py:563-568`), so nothing can ever be missing.
Yet `_MISSINGNESS_LIMITATION` ("an absent active value is excluded visibly") is emitted on every
result and every candidate, and `workbench.js:423` always renders "Missing active features: none".
**Why it matters:** this is a documented guarantee with no executable behaviour behind it — the
gap between the claim and the code is exactly what a reviewer of this product would be asked to
certify. **P2** → either remove the fields and the limitation string, or admit rows with missing
features and make the exclusion counting real.

### M-5 — Asymmetric fixture-mode guard
`modeling/research.py:353-354`: `_require_mode_paths` returns immediately for `TEST_FIXTURE`, with
no check that fixture roots differ from the production roots. The sibling builder
`features/historical.py:1177-1179` *does* assert that fixture roots are not the production roots.
**Why it matters:** a fixture-mode index build can be pointed at
`runs/w09/historical-player-workbench-v1` and write into the governed output. **P2** → mirror the
`features/historical.py` guard.

### M-7 — The W04 runtime-control gate uses a hand-maintained source roster, and it is out of date (suite is red)
`scripts/launch_wyscout_v5.py:1521` `_POST_W04_AUDIT_ONLY_PYC_SOURCE_PATHS` is a hardcoded 102-entry
tuple of source paths. `_independent_pyc_inventory` (line 3406) walks every `__pycache__` entry in the
repository, derives the `.py` it came from, and raises if that path is in neither the code manifest
nor this roster (line 3665).

`src/scouting/data_products/wyscout/expert_evidence.py` is **absent from the roster** — while 13 of its
W10 siblings are present (`contracts/expert_relevance.py`, `storage/expert_study.py`,
`web/w10_expert_study.py`, `services/api/w10_study_main.py`, …). So as soon as Python compiled that
module, four W04 tests began failing:
```
FAILED tests/unit/test_w04_wyscout_runtime_control.py::test_admission_authority_reconstructs_exact_twenty_positive_proofs
FAILED tests/unit/test_w04_wyscout_runtime_control.py::test_child_collector_substitution_cannot_change_retained_oracle
FAILED tests/unit/test_w04_wyscout_runtime_control.py::test_actual_admission_is_two_run_deterministic_idempotent_and_no_rebuild
FAILED tests/unit/test_w04_wyscout_runtime_control.py::test_immutable_existing_manifest_conflict_is_not_repaired
RuntimeControlError: PYC lacks stable source or exact inert-orphan authority:
  WHOLE_REPOSITORY:src/scouting/data_products/wyscout/__pycache__/expert_evidence.cpython-312.pyc
  ->src/scouting/data_products/wyscout/expert_evidence.py
```
Reproduced in isolation in 21s, so it is not a mid-run edit artifact.

**Why it matters** — three separate problems, and the roster entry is only the first:
1. The project's own acceptance gate (`uv run pytest -q`, README "Local verification") is red right
   now, and `AGENTS.md` makes reproducing these checks the condition for accepting any phase.
2. A hand-maintained roster of *every source file in the repository* guarantees this recurs on every
   new module — during precisely the "continuous phased execution" the process mandates. The gate
   fails **open on process** (someone must remember) and **closed on tests** (everything unrelated
   goes red).
3. The verdict depends on gitignored, machine-local `__pycache__` state. Whether the suite passes
   depends on which modules Python happened to compile, so the failure is not reproducible across
   machines and the error names a build artifact rather than the missing roster entry.

I have deliberately not touched the roster or deleted any `__pycache__`, since W04 admission
evidence is master-owned per `AGENTS.md`.
**P1** → add the missing entry to unblock; then derive the roster from the code manifest at runtime
instead of hardcoding it, and make the error message name the roster and the required entry.

### M-3 — Competition filter unused in search
`api/research.py:695` accepts `competition_id`; `workbench.js:250-259` never sends it, so searching
a multi-competition matrix by name cannot be narrowed. **P3**

### M-4 — Docstring overstates what the property does
`serving/research.py:566-570`: `matrix_rows` is documented as "Freshly validated frozen rows" but
returns `self._matrix.rows` unchanged. The freshness actually comes from
`api/research.py:222-225`, in a different module. **P3** → correct the docstring.

---

## Summary

| Priority | Count |
|---|---|
| **P0 — Critical** | **0** |
| **P1 — High** | **13** |
| **P2 — Medium** | **21** |
| **P3 — Low** | **16** |
| **Total** | **50** |

**P1 findings:** C1, P-1, P-2, P-3, P-4, P-5, P-6, P-10, P-11, L-1, L-2, L-3, M-7.

No P0. I looked specifically for data loss, injection, authentication bypass, and unbounded
resource exhaustion reachable from the local API, and did not find one. The security posture of the
storage layer (`guarded.py`, `wyscout_publication.py`) is genuinely careful — `O_NOFOLLOW`,
`dir_fd`-relative traversal, `fstat` identity re-checks after open, and link-based atomic promotion
are all correct. Jinja autoescaping, the W09 CSP, the loopback host check, and the constant-time
token comparison are all sound.

**What I would fix first:** L-1, L-2 and L-3 are the three findings where the system produces a
*wrong or silently arbitrary answer* rather than a slow one — and this product's entire value
proposition is traceable, honest evidence. Then P-4/P-5/P-3 as one piece of work, since they share
a cause: the retrieval hot path treats immutable, already-validated data as if it were untrusted
input on every request.

**Two verification notes:**
- `workbench.js:59` `pythonFloat` re-implements Python's float repr in JavaScript so the
  browser-computed `query_digest` matches the server's canonical JSON (which
  `contracts/research.py:675` enforces with a hard equality check). I differential-tested it
  against `json.dumps` over 200 000 random doubles plus the boundary cases (`1e-4`, `9.999…e-5`,
  `1e16`, `9999999999999998`, `5e-324`, `1e21`, `1e100`): **zero mismatches**. It is correct today.
  The residual concern is maintenance, not correctness: `floatKeys` (line 12) selects float
  rendering by *field name*, and array elements are canonicalised with `key = null`
  (line 54), so adding one float field under a new name silently breaks every digest with an
  unactionable 422. **P3** → generate the float-key set from the contract schema, or have the
  server accept and echo the digest it computes.
- `uv run pytest -q` completed at **4 failed, 3080 passed in 34m17s**. The four failures are M-7
  above — a stale hardcoded roster in the in-scope W04 runtime control, triggered by a W10 file.
  I fixed nothing, since W04 admission evidence is master-owned. The 34-minute suite runtime is
  itself worth a look: it makes the mandated per-phase re-verification loop expensive. **P3**

---

# Remediation plan — single-pass, post-W10

Added 2026-08-06 after the decision to complete W10 first and apply every correction in one pass.

## The constraint that dictates ordering

Several source files are SHA-256'd into the artifacts they produce, and those digests are re-checked
on load. Editing one **by a single byte** invalidates the artifact and everything downstream of it.
Verified call sites:

| Tier | Source file(s) | Hashed into | Verified at |
|---|---|---|---|
| 3 | `data_products/wyscout/historical.py`, `sources/wyscout_historical.py` | canonical build `code_digest` | `data_products/wyscout/historical.py:473,948,1298,1522` |
| 2 | `features/historical.py` (+ feature registry JSON) | feature-matrix build `code_digest` | `features/historical.py:828,1201` |
| 1 | `m0/scoring.py` | index manifest `scorer_code_digest` | `modeling/research.py:644,808,841,977`; `serving/research.py:72,164,385` |
| 0 | everything else | — | — |

Cascade: **canonical → feature matrix → research index → saved experiments → W10 v2 evidence.**
The index pins the matrix (`modeling/research.py:929-956`); saved experiments pin all of it via
`ResearchVersionPins` and replay as `INCOMPATIBLE_PINS` on drift;
`configs/evaluation/w10-expert-evidence-presentation-v2.json` pins `canonical_build_id`,
`matrix_version`, and `matrix_digest` as literals.

The superseded v1 W10 protocol, frozen query pack, and presentation bundle remain historical,
self-verifying authorities pinned to their original W09 build. They are not re-issued by this
cascade. The contract suite must therefore distinguish their continued internal validity from
reproduction by the current accepted W09 service, whose pins are intentionally incompatible after
the rebuild.

**Rule: touch a tier → rebuild that tier and every tier above it. Do the deepest tier you intend to
touch exactly once, and land every fix for that tier in the same pass.**

Rebuild entry points, in order:
```
scripts/build_w09_historical_canonical.py     # tier 3
scripts/build_w09_feature_matrix.py           # tier 2
scripts/build_w09_research_index.py           # tier 1
scripts/build_w10_expert_evidence_v2.py       # W10 v2 evidence
```

## L-5 cascade consequence (corrected after W10 v2 revalidation)

L-5 (`features/historical.py:1061-1065`, `lineup_matches_observed == lineup_matches_expected` by
construction) is tier 2. W10 v2 retains and digests the value at
`data_products/wyscout/expert_evidence.py:1262-1266`, but the participant template renders only
governed minutes and minute state. The constant 1.0 value is therefore not participant-visible.

The cascade cost still applies:

- fixing L-5 rebuilds the matrix digest that the frozen v2 config pins as a literal;
- the v2 config declares `"stability_validation_required_before_formal_freeze": true` and
  `"threshold_status": "…not_scientifically_validated"`, so the thresholds are tied to the frozen
  matrix;
- therefore this pass must **re-issue the v2 config pins and re-run threshold/stability validation**.
  The preregistered pre-pilot thresholds must not be silently re-derived: report any threshold
  deltas and stop for an explicit decision if a threshold would move.

The pre-08E remediation decision is to fix L-5 and rebuild/re-pin the evidence, without starting or
freezing 08E. Before re-pinning, diff old and new matrix rows and require that only the intended
`coverage.lineup_matches_expected` field changes, plus `source_lineage_digest` if L-9 changes
partition ordering. Any other matrix-row change halts the cascade.

## Suggested batches

**Batch A — tier 0, no artifact impact.** Land and verify first; nothing here can invalidate a digest.
M-7 derivation (the four missing rows themselves are already fixed), L-3, P-1, P-5's tier-0 cache
work, P-6, P-7, P-8, P-9, P-12, P-13, P-15, L-4, L-7, L-8, L-10, L-12, L-13, L-14, L-15,
L-16, M-1, M-2, M-3, M-4, C6, C7, C8, C10, C12.
Confirm `serving/m0.py` (L-6, C5) is not digested by `modeling/baselines.py::fit_m0_artifact`
before treating it as tier 0.

**Batch B — tier 1, one index rebuild.** P-4, L-2, and P-5's trusted-scorer uniqueness-skip work
in `m0/scoring.py`. Run a fixture-mode index build for attribution; defer the production rebuild to
the single post-D cascade.

**Batch C — tier 2, one matrix + index rebuild.** C2, C9, the feature-matrix caller portion of C11,
P-2, L-5, L-9, and L-11 only if `math.fsum()` is proved bit-exact on the retained population first.
Run a fixture-mode matrix build for attribution; defer the production rebuild to the single post-D
cascade.

**Batch D — tier 3, full rebuild from raw source.** C4, the canonical caller portion of C11, P-10,
P-11. Run a fixture-mode canonical build for attribution, then perform one production cascade in
the verified order: canonical, matrix, index, W10 v2 evidence.

**Batch E — remaining tier-0 refactors, after the rebuilds are green.** C1, C3, C5, and L-6. C2/C9
belong in Batch C and C4 belongs in Batch D because those source files are digested. Never interleave
Batch E with a rebuild: a refactor that changes behaviour during an artifact rebuild is unreviewable.

**Standalone — M-6, L-1.** Keep the eligibility enum and full manifest roster intact for
backward-compatible reads, but remove M-6's inert serving/reporting surface and document why a future
ratio-feature registry must revisit missingness. L-1 requires an explicit `season_id` in both the
server contract and the client-side canonical filter object. Both change result semantics rather
than artifact digests. The three currently reproduced saved experiments are pre-authorised to
transition to `INCOMPATIBLE_PINS`; do not migrate or re-pin them.

## Verification

Per README "Local verification" plus the phase gate:
```
uv run ruff format --check . && uv run ruff check .
uv run mypy src/scouting
uv run pytest -q
uv run python scripts/verify_local_only.py
uv run python scripts/install_local_git_guards.py --check
```
Baseline at review time: ruff clean, mypy clean, `pytest` **4 failed / 3080 passed in 34m17s**
(the 4 are M-7). Anything beyond those four is a regression from this work.

After any rebuild, additionally confirm: `scripts/evaluate_w09_retrieval.py` still passes, and saved
experiments either replay `REPRODUCED` or are knowingly accepted as `INCOMPATIBLE_PINS`.

---

# Revalidation after W10 v2 landed — 2026-08-06 (later same day)

Re-checked against the working tree after the W10 v2 engineering work landed
(HEAD still `879b03d`; 3,485 insertions across 26 tracked files plus 27 untracked).

## Status changes to existing findings

**M-7 — FIXED, but the design flaw it names is unfixed and has already recurred.**
`src/scouting/data_products/wyscout/expert_evidence.py` is now roster entry
`scripts/launch_wyscout_v5.py:1541`, alongside `scripts/build_w10_expert_evidence_v2.py` and two new
test files. The same four entries had to be hand-added to **three** files
(`launch_wyscout_v5.py`, `admit_wyscout_v5_runtime.py`, `tests/unit/test_w04_wyscout_runtime_control.py`,
`4 +` lines each). That is the predicted recurrence, inside one working session. The remediation
(derive the roster from the code manifest) still stands.

**L-5 — corrected downward; the earlier characterisation was too strong.**
I previously reported that experts would see a coverage figure that could not vary. Now verified
against the rendered template: `apps/web/templates/w10_expert_study/v2_participant.html:18` renders
only `quantity.governed_minutes` and `quantity.minute_state`. `lineup_match_coverage` is **not
rendered to participants**. Per-metric `coverage.definition` and family opportunity denominators
are rendered, and those come from W10's own `_coverage(observed, expected, …)`, which is real.

L-5 therefore reduces to: the vacuous 1.0 field is still constructed at
`data_products/wyscout/expert_evidence.py:1262-1266` and still lands inside the digested,
retained `ParticipantExpertEvidenceBundleV2` evidence bytes. It misrepresents nothing to a
participant; it does put an uninformative constant into the permanent evidence record.
**Revised priority: P2, and no longer a pre-freeze blocker.** It can move to the normal tier-2 batch.

**Tier table — still valid.** `m0/scoring.py` unchanged (193 lines);
`features/historical.py:1061-1065` unchanged and still the exact L-5 site; the v2 config still pins
`matrix_digest: 428d25ed…`. Every rebuild-cascade consequence in the remediation plan holds.

## New findings — W10 (previously out of scope)

### W10-1 — Reference population rebuilt per metric in the independent-descriptor percentiles
`data_products/wyscout/expert_evidence.py:1165-1200`. For every metric of every family of every
player, the code re-iterates the entire within-position reference population, calls
`_position_family(...)` again per reference row, and then does a linear `next(...)` scan over that
reference's metrics to find the matching `metric_id`.

Cost ≈ players × families × metrics × position_population × metrics. The W09-input path 240 lines
earlier (line 922) already does this correctly — it hoists a `references` dict once and reuses it.
The independent-descriptor path just does not.
**Why it matters:** the pilot uses a handful of comparisons so this is invisible today; the formal
study over a larger query pack multiplies it directly, and evidence-build time sits on the critical
path of every protocol rebuild. **P1** → precompute
`{(position, family_id, metric_id): [values]}` once before the bundle loop.

### W10-2 — v2 has no participant-keyed presentation schedule; v1 did
`storage/expert_study.py:2277`: `for ordinal, comparison in enumerate(self.comparisons, 1)`. The v2
presentation order is the authority file's array order, identical for every participant.

The v1 formal path is materially stronger: `contracts/expert_relevance.py:1386-1492`
(`build_formal_candidate_presentations`) applies a SHA-256 participant-digest-keyed permutation
(`_schedule_order`, line 1376), places repeat anchors in keyed delayed slots, and enforces
nonterminal and nonadjacent repeats. The frozen bundle also declares
`candidate_order_rule = "participant-digest-and-query-keyed deterministic permutation"` and
`schedule_rule = "w10-participant-keyed-interleaved-v1"`.

Note that the query pack builds `candidates=(*retrieved, *frozen_controls)`
(`scripts/build_w10_expert_protocol.py:490`) — retrieved first, controls second. In v1 the keyed
permutation destroys that correlation. In v2 nothing does; whether provenance leaks by position
depends entirely on how the authority file's `comparisons` array happens to be ordered, which is
currently unconstrained and untested.

For a mechanics pilot testing presentation this is defensible. For the formal study it is not:
order effects would be perfectly confounded with specific candidates, and retrieved/control
position may be inferable.
**Why it matters:** this is a v1 capability that did not carry forward into the v2 rework, and
`W10-V2-PROTOCOL-FREEZE-08E` is the moment it becomes permanent. **P2 now, P0 if promoted to formal
collection unchanged** → decide explicitly at 08E whether the v2 formal path inherits
`build_formal_candidate_presentations`, and add a contract test asserting that provenance does not
correlate with presentation ordinal.

### W10-3 — Participant template is effectively unauditable line-by-line
`apps/web/templates/w10_expert_study/v2_participant.html:20-21` are single Jinja lines of roughly
1,000+ characters each, carrying table structure, conditionals, accessibility attributes and
per-metric rendering logic.
**Why it matters:** this template *is* the scientific instrument — what an expert sees is the
experiment. An independent reviewer at 08F has to certify it, and a 1,000-character line cannot be
diffed or reviewed meaningfully. **P3** → reformat; no behaviour change.

### W10-4 — Nothing asserts that constructed evidence is either rendered or explicitly internal
There is no test tying `ParticipantExpertEvidenceBundleV2` fields to the rendered template. That
gap is exactly how L-5's `lineup_match_coverage` came to be computed, digested and retained while
never being shown. **P3** → add a contract test enumerating bundle fields as
rendered / internal-only, so a field cannot silently become evidence-of-nothing.

## W10 remediation outcome — pre-08E

The owner selected W10-2 option (a): v2 formal collection inherits participant-keyed candidate
ordering. No 08E freeze or formal collection was started by this remediation pass.

- **W10-1 — FIXED.** `build_expert_evidence_bundles_v2` now normalizes each
  `(matrix row, independent family)` once and constructs each
  `(position, family_id, metric_id)` reference population once, retaining matrix-row order. The
  contract fixture bounds `_position_family` to exactly six calls per matrix row and checks the
  resulting percentiles.
- **W10-2 — FIXED pre-freeze.** The v1 formal builder and v2 store share
  `participant_keyed_candidate_order`. The v2 participant-safe authority deliberately contains no
  protected `candidate_id`; its unique `comparison_digest` is therefore the protected candidate
  identity supplied to the same SHA-256 ordering primitive. The primitive accepts only
  `(participant_digest, candidate_ids)` and cannot read provenance. Deterministic contract tests
  prove different participant digests yield different orders, assert the exact retrieved-by-
  ordinal counts over 200 fixed synthetic participant digests, and intercept every permutation-key
  call to prove it receives only the participant digest and candidate identity. The frozen v1
  presentation bytes and digest remain unchanged.
- **W10-3 — FIXED.** The participant Jinja instrument is reformatted into reviewable structural
  blocks without changing field references, labels, routes, option values or conditions.
- **W10-4 — FIXED.** An exhaustive contract registry covers every Pydantic field in the bundle and
  each nested evidence model. Every field must be classified as directly rendered or internal-only;
  every rendered field must also name a concrete reference present in the participant template.

## What is genuinely strong

Stated for balance, and because these should not be refactored away:

- The SQLite trigger layer (`storage/expert_study.py:2169-2171`) enforces sealed schedules,
  sequential ordinals, exact-answered completion, and revision-to-command binding *in the database*
  rather than in application code. That is the right place for it.
- `_participant_safe_bytes_v2` (line 1383) recurses over both keys **and** string values against
  separate forbidden rosters, applied before serialization.
- Unsupported evidence resolves to `not_captured` / `not_applicable` rather than zero-imputation.
- The v1→v2 rework itself: a construct-validity defect was caught by the team's own mechanics pilot
  *before* formal collection, and v1 approval was superseded rather than rewritten. That is the
  process working as intended.

## Master integration revalidation — 2026-08-07

### L-17 — Pre-L-1 saved experiments could not reach `INCOMPATIBLE_PINS`

**P1 — found and fixed during master integration.** L-1 made `ResearchFilters.season_id` optional
for retained reads, but normal Pydantic serialization inserted `"season_id": null` into a legacy
request that originally had no such field. That changed the canonical query projection, so all
three retained experiments failed contract validation during load instead of reaching the
pre-authorised `INCOMPATIBLE_PINS` replay result.

The optional field now excludes itself from serialization only when absent. New serving requests
still fail closed unless `season_id` is explicit, while the exact historical request, result,
experiment and report bytes retain their original digests. A contract assertion covers the absent
serialization. Production replay was independently reproduced for all three retained experiment
IDs; each now returns `INCOMPATIBLE_PINS` against the replacement matrix without migration or
re-pinning.
