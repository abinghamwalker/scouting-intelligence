# W04 23-root schema closure independent review R4

- Date: 2026-08-01
- Task: `W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-REVIEW-01-R4`
- Role: fresh report-only independent reviewer
- Candidate: `W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-01-R4`
- Verdict: **REWORK**
- Findings: **P0 0 / P1 2 / P2 0**

This review does not approve the candidate and makes no implementation repair. It
independently re-tests the four returned P1 families: runtime predicate closure,
frozen constants, valid/adversarial model evidence, and canonical-Decimal
serialization.

## Fixed binding readback

Every review-packet binding reproduced before analysis and again before return.

| Artifact | Required and observed SHA-256 |
| --- | --- |
| producer R4 packet | `cee64adaf94f540e17402dd1c8cc0dc0ec79b7d91c613fe90a7f9de94d518e20` |
| master R4 pre-review | `0c392d21c29d529e6545bcdadf4a4914c74b7e14b50d360215633662a2ca172a` |
| acceptance oracle | `de4a4119cf1a1158156d55f49f26bae8c1c08b46d36f93bb6c6afe102fdd145f` |
| R3 master rework | `8f123e5b23057155b8dd2e544c9284df0ba01da8a295882399f17052fefa305d` |
| `src/scouting/storage/formats.py` | `84c04be89c6d726ab9129326e7815dda2331bf30ade2f8d41852120e2b6d144c` |
| `tests/unit/test_w04_wyscout_product_formats.py` | `8e68548967293b28e694359509667106951bdc5ba8e1636a541f81f7c3773e1a` |
| `src/scouting/contracts/wyscout_schema.py` | `67b29d6f13228f8e9ba87468545457961c6fdf808831aa1d2ae08ef12d2b7c3b` |
| `tests/contracts/test_w04_wyscout_schema_closure.py` | `c6ae3c4c469c0fec819a18ee3d929ec9cd291f386ff8dae2fb44394173fa7c42` |
| producer return | `be45bfef87e8ad0429434ecef1315eea3db393417764369112eaf02275aeb95e` |

No fixed binding drifted.

## P1-01 — runtime predicate operands remain materially incomplete

The candidate's predicate count and owner/name roster are complete, but the emitted
predicate records do not contain all runtime operands used by their owning
validators. The review independently traversed annotations from the frozen 23 root
models, found 60 reachable Pydantic models, extracted the 56 emitted reachable
owner/validator bindings, parsed each actual validator body, and compared direct
`self.<model field>` reads with the top-level fields named by the emitted operands.

Exactly **26 reachable owner/validator bindings** omit at least one directly read
model field:

- `BronzeKnownRecord.raw_record_is_preserved_once` omits `source_row`, `lineage`,
  `tenant_context`, and `classification` (including the source-row digest,
  lineage-membership, source-authority tenant, and rights equalities).
- `BronzeRejectedRecord.rejected_record_is_closed` omits `tenant_context`,
  `classification`, and `lineage`.
- `BronzeRejectedField.rejected_value_is_exact` omits `record_kind`,
  `action_event_taxonomy_id`, `reason_code`, `field_authority`, `tenant_context`,
  `classification`, and `lineage`.
- `GoldCoverageDimension.coverage_is_exact` omits `name` and
  `zero_denominator_authority`, so its coordinate/FIELD and
  possession/POSSESSION zero-denominator branches are not represented.
- `SilverAction.action_is_strict_and_orderable` omits `source_rows`,
  `source_event_record_id`, `player_id`, `team_id`, event/subevent IDs,
  `event_sec_source_scale`, predicate/eligibility states, and `lineage`.
- `SilverPlayerMatchFact.player_match_key_and_state_are_exact` omits `build_id`,
  `tenant_context`, `source_rows`, `match_start_utc`, `match_team_id`,
  `lineup_evidence_present`, `right_censored_or_uncertain`, and `lineage`.
- `GoldPlayerWindow.gold_key_and_feature_state_are_exact` omits `build_id`,
  `tenant_context`, `source_rows`, `lineage`, role version/state, lineage/feature
  digests, `coverage`, and `applicability`.
- `LayerManifest.layer_order_and_entries_are_exact` omits the source/index, tenant,
  rights, clock, and feature-schema fields; `LayerManifestEntry` separately omits
  `schema_role`.
- `W04SemanticTemporalProof.proof_has_exact_five_strict_dependencies` omits
  `source_completion_index_sha256`, `source_manifest_ids`, `feature_schema_hash`,
  `source_authority`, and `authority_clocks`.
- `W04ApplicabilityAssessment.reasons_are_sorted_unique` omits `state`.
- All nine effective `WyscoutProductRow.tenant_is_the_fixed_poc_context` bindings
  omit `source_completion_index_sha256`, `source_rows`, and `lineage`.
- The entity/match/lineup/possession validators additionally omit source-row,
  partition, build, tenant, or lineage operands used in their bodies.

This is not a stylistic census issue. The frozen oracle requires the executable
cross-field predicates, and R4 explicitly requires every operation and operand used
by the owning validator. A consumer of the emitted record cannot reconstruct these
equalities from the advertised operands. Counting 56 records and proving that the
listed subset resolves therefore remains insufficient.

Bounded correction: expand the existing runtime predicate records to every material
runtime field/equality used by their validators, with the corresponding exact
constants, and add an independent expected-ledger test that fails on any omitted
direct or composed validator input. Do not add models, roots, fields, semantics, or
an alternate authority.

## P1-02 — the 29-row matrix does not exercise its frozen variant roster

The matrix has exactly 29 freshly strict-validated Pydantic instances over all
twelve Parquet roots; it does not use `model_construct` for acceptance and its
descriptor-led projection mechanics pass. Its row count, however, masks missing
required variants:

1. Both `BRONZE_KNOWN_RECORD` rows contain only object/integer arms. Their complete
   recursive kind sets are each exactly `{object, integer}`. Neither row contains
   all seven tagged JSON arms, a mixed nested array/object, or present null; neither
   supplies the required materially different empty/nested raw-object shape.
2. All five `BRONZE_REJECTED_RECORD` rows reuse the same raw-record object. They cover
   the five raw-kind states but provide only **one** unique raw-object shape, contrary
   to the required differing raw shapes.
3. The three `SILVER_ACTION` rows all retain non-null player/team and non-null
   event/subevent taxonomy IDs. The nominal empty-position row uses pair `(2,24)`,
   remains `PREDICATE_ADMITTED`, and therefore does not exercise the required-null
   identity/taxonomy plus unmapped-predicate arm. All three rows also use source
   scale 18 after `_scale18_action`; the required zero/maximum-scale coverage is not
   present in the acceptance matrix.

The other matrix families observed in execution—seven rejected-field union arms,
open/closed lineup, resolved/equal-clock possession, precision-38 `1/3` coverage,
and authority-proven zero denominators—are retained passing evidence. They do not
replace the missing variants above.

Bounded correction: replace only the deficient fixture rows while preserving the
exact 29-row per-root cardinalities, then assert the required variant properties
explicitly rather than only asserting counts.

## Passed disposition — frozen constants and composition

No finding was raised for the frozen constant family:

- all five build/product authority subobjects and all four season/lineup subobjects
  deep-equal their independently loaded accepted JSON values;
- `completion_index_binding` has exactly 13 keys and eight ordered requirements;
- the build preimage has 25 keys; the LayerManifest roster has 19 fields, ten
  validation-order tokens, and eight substitution failures;
- the accepted match raw-record digest occurs once and the stale R3 digest is absent;
- E1–E8 are distinct and every cited authority-source physical SHA-256 reproduces.

## Passed disposition — canonical Decimal serialization

No finding was raised for the bounded Decimal family:

- there are six reachable physical `CANONICAL_DECIMAL_UTF8` paths, all generated
  only by `GoldCoverageDimension.coverage` and `GoldCoverage.coverage_overall`;
- the remaining 30 Decimal paths are all `DECIMAL128(22,18)`, including event
  seconds, coordinate axes, sequence positions, and possession-order position 1;
- forward rendering is finite, fixed-point, no-rounding, no-exponent, no-LF and
  signed-zero canonical; inverse decoding strict-parses, rejects non-finite values,
  re-encodes and requires byte equality;
- alias, null misuse, invalid UTF-8 and non-string physical families execute as
  zero-write rejection proofs.

## Executed evidence

Reviewer-owned probes were run with `uv run python -c` and no filesystem writes:

- independent annotation traversal plus validator-source AST comparison:
  `reachable_models=60`, `predicates=56`, `bindings_with_missing_direct_fields=26`;
- independent authority JSON deep comparison and cited-file hashing: nine exact
  subobjects, E1–E8 exact, every cited SHA-256 `True`, stale digest count `0`;
- independent descriptor census: canonical Decimal paths `6`, decimal128 paths
  `30`, every decimal128 `(22,18)`, JSON-only roots `11`;
- executable matrix inspection: rows `29`, roles `12`, Bronze-known kind sets both
  `{integer,object}`, rejected-record unique raw shapes `1`, and the three exact
  Silver-action state tuples recorded in P1-02.

Packet-required commands and exact results:

| Command | Exit | Result |
| --- | ---: | --- |
| `uv run ruff format --check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py src/scouting/contracts/wyscout_schema.py tests/contracts/test_w04_wyscout_schema_closure.py` | 0 | 4 files already formatted |
| `uv run ruff check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py src/scouting/contracts/wyscout_schema.py tests/contracts/test_w04_wyscout_schema_closure.py` | 0 | all checks passed |
| `uv run mypy src/scouting/storage/formats.py src/scouting/contracts/wyscout_schema.py tests/unit/test_w04_wyscout_product_formats.py tests/contracts/test_w04_wyscout_schema_closure.py` | 0 | no issues in 4 files |
| `uv run pytest -q tests/contracts/test_w04_wyscout_schema_closure.py tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_wyscout_data_contracts.py tests/unit/test_w04_wyscout_product_formats.py` | 0 | `526 passed in 124.19s` |
| `uv run pytest -q tests/contracts/test_w04_logical_arrow_projection_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/contracts/test_w04_wyscout_build_product_authority.py tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py` | 0 | `179 passed in 3.99s` |
| `uv run python scripts/verify_local_only.py` | 0 | PASS, 25/25; branch `main`; zero remotes |

The green suites demonstrate regression stability, not acceptance completeness; the
two P1 findings are executable evidence that the current tests do not enforce the
full frozen acceptance oracle.

## Scope and handoff

No provider/network access, dependency or lock change, product/aggregate write,
publication, cloud, container, hosted CI, public endpoint, deployment, Git command,
or implementation edit occurred. Only this review and its allowed return report
were written. The two findings are bounded to the existing predicate corpus and
acceptance fixtures/tests; no architecture or product boundary change is required.

Verdict: **REWORK**. Return the two bounded P1 findings to the producer. Fresh
independent review and master acceptance remain mandatory before the 23-root
producer or downstream product work resumes.
