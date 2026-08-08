# W04 Wyscout data contracts independent review R2

## Review identity

- Task: `W04-DATA-CONTRACTS-REVIEW-01`, revision `R2`
- Role: fresh independent reviewer
- Disposition: **REWORK**
- Open findings: P0 `0`, P1 `7`, P2 `0`
- Acceptance rule: PASS requires zero open P0-P2 findings.

The R2 correction closes the original adversarial examples and every prescribed
check passes. Fresh direct-constructor probes nevertheless found seven ways to
construct proof-bearing records that disagree with the accepted R20/R21
authorities. All seven are bounded contract/test corrections. No executable
evidence supports another architecture revision.

## Reviewed bytes and digest reproduction

Every input listed by the R2 review packet was read in full, including all 4,007
implementation/test lines. Fixed identities were recomputed before review:

| Material | SHA-256 | Result |
|---|---:|---|
| `src/scouting/contracts/wyscout_data.py` | `87dc13ada636e018ff9dfc17b548942a1d93132db8a615248cc8be3b23ebe99d` | match |
| `tests/contracts/test_wyscout_data_contracts.py` | `1b5aafbd127cda6703dce8de358b10c6f4c467de0821601b6b358564a5dabd47` | match |
| `reports/reviews/W04/returns/W04-DATA-CONTRACTS-01-R2.md` | `b855798a3be49093e0ceff78122bde3b2dcd893d99a1cafef43275f6138ad34c` | match |
| `reports/reviews/W04/wyscout-data-contracts-independent-review-R1.md` | `862fa5513cd261fd95bcd921fb52631c90af56ff930ce968682059879761dee2` | match |
| `reports/reviews/W04/wyscout-schema-design-R20.md` | `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047` | unchanged |
| `reports/reviews/W04/wyscout-schema-design-R21.md` | `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020` | unchanged |
| identity acceptance v1 | `37764392cdaf9626ffaff26e119fb142218d36489e87a8b1d55402e3e2dc7f86` | match |
| source snapshot manifest | `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd` | match |
| field acceptance v2 | `beb66d3a8f07e41fe0fa5fe82fee06e3602f3c3045f48d2a11ca6fa9f20cc436` | match |
| possession acceptance v2 | `2438fb0255641b02c0631b6a42e727a033fbe58e759bdf4c61e0e09692eda0a1` | match |
| supported-feature acceptance v1 | `d3b3c552784f4734f6b002569d9add1b4dd2d2eaaed57643a8ca4d5226fca78c` | match |
| product-contract preimage v1 | `0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293` | match |
| schema-bundle preimage v1 | `a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f` | match |

## Exact verification results

| Command | Result |
|---|---|
| `uv run ruff format --check src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py` | PASS; 2 files already formatted |
| `uv run ruff check src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py` | PASS |
| `uv run mypy src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py` | PASS; no issues in 2 files |
| `uv run lint-imports` | PASS; 30 files, 46 dependencies, 3 contracts kept, 0 broken |
| `uv run pytest -q tests/contracts/test_wyscout_data_contracts.py tests/contracts/test_foundation_contracts.py tests/contracts/test_w04_identity_ruleset_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/unit/test_wyscout_source_manifest.py` | PASS; 370 passed in 77.84s |
| `uv run bandit -q -r src/scouting/contracts/wyscout_data.py` | PASS |
| `uv run python scripts/verify_local_only.py` | PASS; 25/25 and zero Git remotes |

The original R1 constructor matrix was also rerun independently with:

```text
uv run pytest -q tests/contracts/test_wyscout_data_contracts.py -k \
'raw_kind_direct_constructor or silver_action_direct_constructor or rejected_subevent or canonical_source_uuid or every_public_entity_action_constructor or action_decimal128 or every_authority_clock or every_dependency_clock or recomputed_lineage or optional_zero_coverage or coverage_failure_states or manifest_direct_constructors or manifest_rejects_cross_layer or gold_recomputes or gold_rejects_arbitrary or source_ordinal or bronze_requires_exact or source_authority_and_silver_source_family'
```

Result: `95 passed, 45 deselected in 0.23s`.

## R1 finding-by-finding reproduction

### W04DC-P1-001 — raw-kind evidence

**Closed for the R1 probes.** Safe unknown, unsafe, known-token, digest, type,
and state mutations are rejected by the public constructor. No new raw-kind
failure was found.

### W04DC-P1-002 — strict event/subevent handling

**The R1 examples close, but the authority boundary remains open.** `SilverAction`
rejects non-admitted integer pairs and `BronzeRejectedField` rejects path/type/
decision drift. New probes show that the exported `ActionSubeventOutcome` can
still emit arbitrary integers and that an admitted but possession-ineligible
pair can be marked resolved. See R2 findings 001 and 002.

### W04DC-P1-003 — positive source IDs

**Closed.** Zero, negative, and Boolean identifiers are rejected by
`canonical_source_uuid` and every exported entity/action constructor.

### W04DC-P1-004 — decimal128(22,18)

**Closed.** Exponent capacity, declared-scale drift, NaN, infinity, and exact
positive/negative capacity boundaries were reproduced.

### W04DC-P1-005 — accepted authority clocks

**Clock portion closed; dependency identity remains open.** Every authority and
dependency clock mutation is rejected. An identity dependency with substituted
ID and digest is accepted after canonical reordering and lineage rehashing. See
R2 finding 004.

### W04DC-P1-006 — lineage equality and recomputation

**Original hash/equality probes closed; authority alias remains open.** Hash,
row/proof, manifest, and cross-boundary lineage mutations are rejected, but the
identity dependency is validated only by clocks. See R2 finding 004.

### W04DC-P1-007 — coverage and applicability

**Original state matrix closes; derivation remains open.** Optional-zero proof,
authority-missing, failed, suppressed, and research-only states are now
representable and fail closed. Coverage totals and applicability reasons are
not derived from their evidence. See R2 findings 005 and 006.

### W04DC-P1-008 — layer manifests

**Original build/parent/schema/partition probes close; empty materialization
remains open.** Unsafe paths, wrong build names, empty layer manifests,
cross-layer parents, schema roles, rights, tenant, feature, and lineage drift
are rejected. A zero-row, zero-byte Parquet entry is still accepted. See R2
finding 007.

### W04DC-P1-009 — Gold reconciliation

**Four-feature reconciliation closes; coverage reconciliation remains open.**
Gold rejects mutations to each of the exact four supported counts and to
contributing fact identity/window selection. It accepts coverage counts that
cannot be produced by the contributing facts. See R2 finding 005.

### W04DC-P1-010 — source/provenance/rights closure

**Rights, family, admission, measurement, and ordinal-bound probes close; row
identity remains open.** Exact tenant/rights/source-family and manifested row
bounds are enforced. Duplicate physical row locations, ambiguous action
ordinals, and match partition/lineage disagreement are accepted. See R2
finding 003.

## New open findings

### W04DCR2-P1-001 — exported subevent outcome permits forged canonical values

`ActionSubeventOutcome` at `wyscout_data.py:1870-1882` validates only that an
emitting and a rejected state are disjoint. Direct construction with
`canonical_value=999` is accepted without an event ID or membership in the
frozen pair taxonomy. The factory at `wyscout_data.py:1885-1899` is stricter,
so the public constructor and factory disagree.

Require emitted outcomes to bind the canonical event and exact admitted pair,
or make the outcome an internal/non-forgeable factory result. Add direct
constructor parity tests for admitted and non-admitted integers and every
non-integer raw type.

### W04DCR2-P1-002 — possession eligibility is not derived from possession v2

`SilverAction` checks admitted field pairs at `wyscout_data.py:1122-1132`, but
its resolved-state check at `wyscout_data.py:1133-1138` only requires event,
subevent, and team values to be present. A row with pair `(9, 90)` and
`ELIGIBLE_RESOLVED` is accepted. The accepted possession v2 and supported-
feature authority classify `(9, 90)` as `UNMAPPED` and structurally ineligible;
the same issue applies to the exact ineligible roster `(2,23)`, `(2,24)`,
`(2,25)`, `(2,26)`, `(4,40)`, `(5,51)`, `(9,90)`, `(9,91)`.

Derive possession eligibility from the accepted v2 selector/sequence contract
and reject every forged state across the full admitted-pair matrix.

### W04DCR2-P1-003 — physical source-row identity and partition binding are ambiguous

`WyscoutRowLineage` defines uniqueness as path + ordinal + raw digest at
`wyscout_data.py:738-747`. Consequently, the same path and ordinal can occur
twice when the raw digest differs. `SilverAction` then selects an action row by
bare ordinal with `any()` at `wyscout_data.py:1106-1111`; the ambiguous source
is accepted. `SilverMatch` declares `source_partition` at
`wyscout_data.py:1002-1012` but never derives it from its selected source row,
so a France partition is accepted with England-only match lineage.

Make path + zero-based ordinal the unique physical row key, make each Silver
row select exactly one source-row reference, and derive the match partition
from that reference. Test digest disagreement at a duplicate location,
same-ordinal rows across paths, and country-partition mutation.

### W04DCR2-P1-004 — identity dependency ID/digest substitution is accepted

`_validate_exact_dependency_lineage` validates source and feature dependency
identities exactly, but validates the identity dependency only by clocks at
`wyscout_data.py:1510-1513`. Replacing both the identity dependency UUID and
digest, restoring canonical sort order, and recomputing `lineage_hash` is
accepted.

Enforce the frozen R20 identity dependency preimage contract: the dependency
ID must equal the specified UUIDv5 of `identity_bundle:` plus its digest, with
the exact accepted clocks. Add independent ID-only, digest-only, paired-
substitution, ordering, and rehash tests.

### W04DCR2-P1-005 — Gold coverage is not reconciled to contributing facts

`GoldPlayerWindow` recomputes all four supported feature values at
`wyscout_data.py:1774-1783` but does not recompute its six coverage dimensions.
A Gold row with one contributing fact whose dimension counts are 1/1 accepts
Gold dimension counts of 2/2 and overall coverage 1.

Define and enforce the exact R20 player-window aggregation of the selected
facts' six coverage dimensions. Test numerator, denominator, state, reason,
missing-dimension, and overall-coverage mutations. This does not expand the
four-feature roster.

### W04DCR2-P1-006 — applicability reason codes are arbitrary rather than derived

`W04ApplicabilityAssessment` at `wyscout_data.py:1384-1396` enforces only
ordering, uniqueness, and ready/non-ready emptiness. `_expected_applicability_state`
at `wyscout_data.py:1407-1424` derives only the enum state. A partial LINEUP
fact is accepted as `RESEARCH_ONLY` with the unrelated reason
`UNRELATED_REASON`.

Derive the exact sorted reason set from failed/partial/authority-missing
coverage dimensions and uncertainty evidence, and compare both state and
reasons at Silver fact and Gold boundaries.

### W04DCR2-P1-007 — zero-row, zero-byte Parquet entries are materializable

`LayerManifestEntry` uses non-negative rather than positive counts at
`wyscout_data.py:2072-2080`. A Bronze known-record Parquet entry with
`row_count=0` and `size_bytes=0` passes all entry validation. R20 requires empty
quarantine partitions to be represented without zero-row Parquet files; an
actual manifest entry therefore must describe a non-empty materialization.

Require every materialized Parquet entry to have positive row count and byte
size, while retaining the existing non-empty layer-manifest rule. Add the
zero-row/zero-byte direct-constructor matrix across Bronze, Silver, and Gold.

## Independent adversarial result

The new probe constructed models through their validated public boundaries,
not through `model_construct` or `model_copy(update=...)`. It produced:

```text
forged_outcome: ACCEPTED
unmapped_pair_eligible: ACCEPTED
absent_event_rejected_evidence: ValidationError
duplicate_physical_source_row: ACCEPTED
ambiguous_action_ordinal: ACCEPTED
forged_identity_dependency: ACCEPTED
gold_coverage_not_reconciled: ACCEPTED
applicability_reason_drift: ACCEPTED
match_partition_lineage_drift: ACCEPTED
zero_row_zero_byte_parquet_entry: ACCEPTED
```

The `absent_event_rejected_evidence` failure is a further symptom of finding
001's event/subevent evidence shape: `BronzeRejectedField` requires a positive
event ID at `wyscout_data.py:842-854`, although R21's unknown-integer route also
covers an absent canonical event. The bounded correction must make that
authority-required quarantine state representable without inventing an event
ID.

## Required bounded rework and recommendation

Return the R2 implementation for a bounded R3 correction limited to
`wyscout_data.py`, its focused tests, and producer evidence. Close the seven
findings above, rerun the complete packet suite, and obtain a new independent
review. Do not start Bronze, Silver, Gold, or product implementation on this
contract revision.

Recommendation: **REWORK**. The findings are executable contract gaps, not a
contradiction in R20/R21 and not authority to expand scope.

## Scope and independence confirmation

- The implementation, tests, authorities, preimages, R20/R21, and prior
  evidence were not modified.
- The accepted feature roster remains exactly `action_count`,
  `coordinate_known_action_count`, `match_count`, and
  `resolved_possession_action_count`; no rate, outcome, role, or model feature
  was introduced.
- No serializer, product byte, manifest file, receipt, runtime build, provider
  access, dependency, network, cloud, container, hosted CI, endpoint, or
  deployment was created or changed.
- No Git operation, delegation, implementation change, or self-approval was
  performed.
