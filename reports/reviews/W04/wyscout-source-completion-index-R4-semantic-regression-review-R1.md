# W04 source-completion-index R4 semantic regression review R1

Date: 2026-07-31

Disposition: `PASS`

Findings: `P0=0`, `P1=0`, `P2=0`

This is a fresh independent semantic-regression review of the exact R4 candidate.
It confirms that the R3 data-semantics, provenance, lineage, coverage, and bounded
manifest result remains true. It does not duplicate the parallel proof-graph
security review, self-approve the candidate, or authorize product materialization.

## Fixed candidate gate

Every packet binding matched before analysis:

| Binding | Reproduced SHA-256 |
| --- | --- |
| completion implementation | `e7778db8c977b8461bb590f7174e4b519d7a2ba0a4171d99aa1fd686a6cd5302` |
| Wyscout contract implementation | `154f1ae9934615a2ce9a24a4f8e373cd640a4c3246df93f0e35e6bed28517932` |
| completion-index unit test | `05593a0a0afda62af2b6a2c8753a4f83e78fcbd363b89788751dd2055ed6dfeb` |
| Wyscout contract test | `139683be6a9e6dc4d8be90cd81bb0827c1dbeea00b4ad01aebe3bdcaf9d5be9e` |
| accepted completion index | `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df` |
| prior R3 semantic review | `9d270746900394f2ae1abd3c145e278d61cf3cdef8c7e12165cde138d089c3fa` |

There was no hash drift and no stop condition was reached.

## Exact accepted-index reconciliation

The accepted index remained byte-exact at `644037` bytes. Independent parsing
reconciled exactly:

- five canonically ordered event members;
- `3,652` non-empty match-period rows;
- `3,071,395` actions;
- member indexed counts and frozen row counts of `643150`, `632807`, `519407`,
  `647372`, and `628659`.

The implementation continues to pin the accepted content address, exact source
bindings, member order, positive period rows, unique period identities, per-member
row reconciliation, aggregate count, canonical bytes, and recomputed SHA-256. The
focused index regression is at
`tests/unit/test_wyscout_source_completion_index.py:101`; the validation boundary
is at `src/scouting/sources/wyscout_completion_index.py:708`.

## Strict R21 mapping and causal semantics

R21 projection is unchanged and closed:

- `eventId` remains strict integer-only; independent probes rejected both `"1"`
  and `True` with `eventId must be a strict integer`;
- the raw subevent string `"10"` emitted no canonical subevent and raw tags stayed
  ordered while the possession tag projection remained sorted and unique;
- the exact R21 matrix passed all 27 explicit no-coercion, Boolean-as-integer,
  admitted-pair, non-strict-value, and unknown-integer cases;
- canonical subevents still require an exact admitted strict-integer event/subevent
  pair, and rejected raw strings retain
  `ACTION_SUBEVENT_STRING_PRESERVED_UNMAPPED`.

The source projection is at
`src/scouting/sources/wyscout_completion_index.py:489`; the contract R21 classifier
is at `src/scouting/contracts/wyscout_data.py:2795`.

Equal-clock resolution remains group-first. The executed regressions prove that
opposing same-clock CONTROL actions are wholly unassigned, a possession completed
strictly before an ambiguous clock remains intact, and an ambiguity discards the
dependent contested buffer. Resolution is implemented at
`src/scouting/contracts/wyscout_data.py:1397`, with regressions at
`tests/contracts/test_wyscout_data_contracts.py:2736`, `:2748`, and `:2763`.

Causal provenance also remains exact. Possession source rows cover the complete
period sequence; Fact source rows cover lineup evidence plus all causal action rows
from selected sequences; Gold source rows are the exact union of selected Fact
rows. The other-player causal-action regression at
`tests/contracts/test_wyscout_data_contracts.py:2776` passed.

## Four-feature, lineage, and six-coverage derivation

The exact Gold feature surface remains only:

```text
action_count
coordinate_known_action_count
match_count
resolved_possession_action_count
```

Fact recomputes its three component counts from checked actions, accepted position
evidence, and exact possession membership. Gold recomputes all four fields from its
selected Facts. The four parameterized feature-forgery regressions at
`tests/contracts/test_wyscout_data_contracts.py:1965` passed.

Dependency lineage remains exactly five canonically ordered dependencies: source
manifest, identity evidence, and three feature-schema authorities. Hashes are
recomputed over all ordered rows and the completion-index digest; source,
dependency, authority, watermark, snapshot, and match clocks remain strictly before
cutoff. Three explicit lineage/temporal regressions passed, including the
cross-boundary equality regression at
`tests/contracts/test_wyscout_data_contracts.py:1758`.

All six coverage dimensions remain fixed and derived in this order: identity,
lineup, action, coordinate, possession, temporal. Fact derives each numerator,
denominator, state, zero-denominator authority, and overall minimum from evidence;
Gold aggregates those exact Fact dimensions. All six independent `2/2` Gold
coverage forgeries at `tests/contracts/test_wyscout_data_contracts.py:2340` failed
closed as expected. The derivation boundaries are
`src/scouting/contracts/wyscout_data.py:2348` and `:2473`.

## Real match and bounded one-match manifest

The positive path remains exact for match `2499719`:

| Scope | Exact count |
| --- | ---: |
| indexed `1H` | `901` |
| indexed `2H` | `867` |
| checked full match | `1,768` |
| accepted index total periods | `3,652` |

The source reconstruction and the passing real-path test both use every action in
both indexed periods before issuing the checked match capability. The selected
player has exactly two actions, both in `2H`; the exact causal sequence therefore
contains `867` action source rows. The resulting Gold vector remains `(2, 0, 1, 2)`.
This preserves the required distinction between full-match construction authority
and exact causal feature provenance.

The positive manifest test at
`tests/contracts/test_wyscout_data_contracts.py:2980` passed and supplied exactly
one checked match completion scope and one checked Gold product. The manifest
boundary at `src/scouting/sources/wyscout_completion_index.py:1477` requires unique,
non-overlapping completion identities and exact equality between supplied scopes
and contributing-product scopes. It does not require all `3,652` index periods and
does not make an all-index completeness claim. The independently issued overlapping
scope regression also passed. Thus R4 preserves the bounded one-match scope: the
two periods for match `2499719`, no omitted contributing scope, no extra/different
match, and no global-index materialization claim.

## Executable evidence

- `shasum -a 256 src/scouting/sources/wyscout_completion_index.py src/scouting/contracts/wyscout_data.py tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_wyscout_data_contracts.py data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json reports/reviews/W04/wyscout-source-completion-index-semantic-independent-review-R1.md`
  - exit `0`; all six packet digests matched.
- `uv run pytest -q tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/contracts/test_wyscout_data_contracts.py -k 'integer or string_subevent or equal_clock or causal or completion_index or real_match_checked_path or gold or manifest'`
  - exit `0`; `98 passed, 279 deselected in 111.83s`.
- `uv run pytest -q tests/contracts/test_wyscout_data_contracts.py::test_recomputed_lineage_and_cross_boundary_equality_are_mandatory tests/contracts/test_wyscout_data_contracts.py::test_temporal_proof_has_exact_five_ordered_dependencies_and_valid_from tests/contracts/test_wyscout_data_contracts.py::test_temporal_proof_rejects_wrong_cardinality_duplicate_and_lineage_drift`
  - exit `0`; `3 passed in 0.20s`.
- `uv run pytest -q tests/contracts/test_wyscout_data_contracts.py::test_action_subevent_no_coercion_matrix tests/contracts/test_wyscout_data_contracts.py::test_action_subevent_emits_only_admitted_strict_integer_pair tests/contracts/test_w04_r21_cross_authority_composability.py::test_language_bool_as_int_is_explicitly_excluded tests/contracts/test_w04_r21_cross_authority_composability.py::test_non_strict_subevent_values_preserve_raw_evidence_without_coercion tests/contracts/test_w04_r21_cross_authority_composability.py::test_unknown_integers_never_emit_canonical_subevent`
  - exit `0`; `27 passed in 0.22s`.
- `uv run python scripts/verify_local_only.py`
  - exit `0`; `PASS`, all `25` controls passed.
- Read-only `uv run python -c` probes parsing the accepted index and reconstructing
  match `2499719` through `build_match_period_sequences`
  - exit `0`; reproduced `5` members, `3,652` periods, `3,071,395` actions,
    match `2499719` as `901 + 867 = 1,768`, two target actions in `2H`, and
    `867` causal source rows.
- Read-only `uv run python -c` probe calling `completion_action_evidence` with
  string-subevent and numeric-string/Boolean event-ID fixtures
  - exit `0`; string subevent stayed unmapped and both numeric-string and Boolean
    `eventId` values failed strict-integer admission.

No provider or network access, product write, dependency or lock change, cloud,
container, hosted CI, endpoint, remote, deployment, or Git operation was performed.
The only writes are this review and its packet-authorized return record.

## Recommendation

`PASS` with `P0=0`, `P1=0`, `P2=0`. R4 preserved the accepted R3 semantic and
provenance result for exact index reconciliation, strict R21 mapping, equal-clock
and causal behavior, exact four-feature/lineage/six-coverage derivation, and bounded
one-match manifest scope. Final acceptance remains master-only.
