# W04 source temporal contract review — R1

## Review decision

**Recommendation to master: ACCEPT.**

This is an independent-verifier recommendation, not phase approval. The master retains
gate authority.

## Scope and method

The review challenged the implemented `SourceSnapshotManifest` temporal correction
without modifying its producer implementation, producer tests, configuration, source
data, orchestration, or dependencies. The additive review suite exercises the public
contract as a consumer would and verifies its downstream interaction with
`TemporalEvidence`.

Reviewed controls:

- factual separation of local receipt (`acquired_at`) from upstream source/fact
  availability (`available_at`);
- all three legitimate orderings of those instants;
- required-field, strict-UTC, frozen/strict-model, and canonical JSON behaviour;
- content digest, source-object identity, rights, and unknown-field rejection;
- strict downstream observed/available cutoff exclusion at equality and later;
- compatibility with the W03 `TemporalEvidence` consumer boundary.

## Temporal ordering evidence

| Scenario | `acquired_at` | `available_at` | Result |
|---|---:|---:|---|
| Wyscout-like release before local acquisition | 2026-07-29 14:00:00Z | 2020-01-28 14:24:27Z | accepted; supplied instants preserved |
| Equal receipt and availability | 2026-07-29 10:00:00Z | 2026-07-29 10:00:00Z | accepted; equality preserved |
| Embargo after receipt | 2026-07-29 10:00:00Z | 2026-07-29 11:00:00Z | accepted; supplied instants preserved |

The contract does not derive either clock from the other and does not impose a false
ordering. Its field descriptions and model documentation assign the two clocks
different meanings.

## Adversarial evidence

The independent suite proves:

- both clocks are required;
- naive Python and JSON datetimes are rejected;
- non-UTC Python and JSON datetimes are rejected rather than normalised;
- canonical JSON contains both UTC clocks and round-trips to the same immutable model;
- duplicate `object_path` identities reject even when their digests differ;
- unknown manifest fields reject;
- short, uppercase, and non-hex SHA-256 values reject;
- a prohibited source classification cannot grant derived, review, or export rights;
- `TemporalEvidence` rejects `observed_at` equal to or later than cutoff;
- `TemporalEvidence` rejects `available_at` equal to or later than cutoff;
- receipt before an embargo cutoff cannot bypass the availability rule;
- a pre-cutoff upstream release remains represented truthfully after later local
  acquisition.

## Findings

No P0, P1, or P2 temporal, lineage, serialization, identity, rights, or compatibility
defect was reproduced.

The correction remains narrow: it removes only an invalid relationship between two
source-manifest facts. It does not weaken the strict downstream cutoff rule, which
continues to require both dependency observation and availability to be strictly
earlier than the feature cutoff.

## Verification

All packet acceptance checks passed:

- `uv run pytest -q tests/contracts/test_foundation_contracts.py tests/contracts/test_w04_source_temporal_review.py`
  - `68 passed in 0.20s`
- `uv run ruff format --check tests/contracts/test_w04_source_temporal_review.py`
  - `1 file already formatted`
- `uv run ruff check tests/contracts/test_w04_source_temporal_review.py`
  - `All checks passed!`
- `uv run mypy tests/contracts/test_w04_source_temporal_review.py`
  - `Success: no issues found in 1 source file`

## Residual risk

The model can enforce shape and coherence but cannot independently establish whether a
caller supplied the historically truthful source availability instant. That
provenance responsibility remains with the source-admission workflow and is not a
defect in this bounded contract correction.
