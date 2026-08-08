# W04 R21 cross-authority composability independent review R1

## Decision

`PASS` with no findings.

I independently read the complete frozen R21 authority and every byte of the
final R4 cross-authority test. I also read the final R4 producer return and the
master's R4 reproduction, while treating the superseded R1 review only as
retained failure-lineage evidence. The final test and return physical SHA-256
bindings match the dispatched R2 packet exactly.

Reviewer actor `d9f63ab3-ea18-5fce-8507-a1a33e708aa7` is a fresh canonical
UUIDv5. It was absent from the repository actor corpus before this review and is
distinct from the master actor, all field-v2, possession-v2 and supported-feature
reviewers, the cross-authority producer token, and the superseded reviewer.

## Section 13.1 positive coverage

1. `test_all_strict_pairs_emit_canonical_subevents_and_preserve_v1_predicates`
   proves that every frozen admitted strict integer pair emits the unchanged
   canonical subevent integer.
2. The same test proves that all 36 possession-v2 predicates are
   byte-semantically equal to the v1 predicate array.
3. `test_canonical_field_action_composes_through_possession_and_feature` drives
   an accepted integer field-v2 action through exact same-period possession
   resolution.
4. `test_missing_canonical_subevent_fails_closed_in_possession` proves the exact
   `INELIGIBLE_UNMAPPED` result when the canonical subevent is absent.
5. The canonical composition test proves that only
   `resolved_possession_action_count` is applicable to the resolved fixture.
6. `test_feature_candidate_has_exact_ordered_closed_roster` proves the closed,
   sorted 15-row roster and exactly four supported features.
7. `test_preimages_are_reproducible_siblings_in_exact_acyclic_graph` proves
   reproducible canonical preimage bytes with exactly one terminal LF.
8. The same test proves the exact branch/convergence edges, no sibling edge,
   acyclicity, and both valid sibling presentation orders.
9. `test_exact_resource_roster_preserves_v1_prefix_without_identity_overclaim`
   proves the exact 30 unique paths, the unchanged 17-path v1 prefix, and the
   fixed roster digest without generated or product evidence.
10. `test_v2_supersession_and_digest_flow_into_feature_and_dependency_plan`
    proves both exact v1 supersession IDs.
11. That test also proves unchanged accepted v2 candidate and acceptance digest
    flow into the feature authority and exact five-dependency plan.
12. The closed review parser, binding validator, negative mutations, lifecycle
    tests, and actual-state test require the fixed ID/path, complete R4 test and
    R4 return byte digests, a canonical UUID reviewer, and reviewer separation.
13. The closed gate validator and lifecycle tests require the future gate to
    bind this review's complete physical digest and a `PASS` recommendation.
14. The four-state lifecycle and all nine governed product-path cases prove
    absence before the complete gate and separately prove permitted presence
    only after a complete gate.

## Section 13.2 negative coverage

- The parametrized field cases reject numeric and decorated strings, booleans,
  null, non-integer numbers, arrays and objects without coercion, while the
  dedicated bool, measured-string and unknown-integer cases preserve the exact
  7,821 count, reason code, raw type and raw value.
- Selector cases reject raw event/subevent fields and all names or labels,
  ignore conflicting runtime labels, and fail closed when canonical subevent
  evidence is missing.
- Hybrid dependency cases reject field-v1 with possession-v2 and possession-v1
  with the R21 feature route.
- Prior-authority cases reject wrong keys, values, digests, cardinality,
  supersession and noncanonical key order; the v1 physical-byte parametrization
  detects mutation of every present immutable v1 resource.
- Authority drift cases reject decision, candidate, review and acceptance
  physical or canonical changes across field, possession and feature routes.
- Preimage mutation cases reject own, sibling, descendant, feature, runtime,
  build, run, clock, root, host, product-byte and output observations; graph
  cases reject self, reverse, feature-reverse and cycle edges.
- Schema-preimage cases reject a concrete feature hash, any surface-kind
  overclaim, and treating a descriptor as an implemented row schema.
- Feature cases reject a sixteenth, missing, duplicate, unsorted, open or
  incomplete row; any fifth supported feature; unaccepted, name-only, guessed,
  possession-internal or unlisted inputs; and non-closed unsupported rows.
- Prerequisite and feature-hash cases reject use before both v2 acceptances and
  feature review/acceptance, and reject a feature hash before acceptance.
- Digest-substitution cases reject swapped preimages and physical candidate
  digests where canonical digests are required.
- Resource cases reject wrong cardinality, any v1-prefix change, duplicates,
  directory shorthand, product paths, returns and generated evidence.
- Review/gate cases reject absent, open, mutated, wrong-path, wrong-ID,
  non-`PASS`, self-authored or physically drifted evidence; incomplete gate
  evidence; combined write scopes; and a gate before a passing review.
- Product-boundary cases reject Bronze, Silver, Gold, manifest, receipt,
  serializer/rebuild and data-product paths before the complete gate.

## Independent execution evidence

- `uv run --locked --no-sync pytest -q`: 1,219 passed with one known Starlette
  deprecation warning in 166.46 seconds.
- Unsuppressed final cross-authority contract: 107 passed in 4.93 seconds.
- Exact five-file focused suite: 478 passed in 39.40 seconds.
- Both required Ruff commands passed.
- Local-only verification passed all 25 checks with zero configured remotes and
  no hosted CI, deployment, container or external-service configuration.
- Retained inventory remained exactly 1,151 pyc paths at
  `d9c0a14033a78398072b597944de104470cb69aa3df97ee47ecdde3f182d9a48`
  and 150 cache-directory paths at
  `79250878e3cfb60a3b0131857ca7b0dc79878c5165725132223d95e32f7f9fd6`.

## Machine record

```w04-r21-cross-authority-review-v1
{"recommendation":"PASS","review_id":"w04-wyscout-r21-cross-authority-composability-independent-review-R1","review_path":"reports/reviews/W04/wyscout-r21-cross-authority-composability-independent-review-R1.md","reviewed_by":"d9f63ab3-ea18-5fce-8507-a1a33e708aa7","test_artifact_physical_sha256":"fffb71d4d382816f3572b575cbcd9e951309f92239ca540327cdb02304c4f9b0","test_return_physical_sha256":"9f45ccd44c9f27c53b72331609dd040fc1ca9211c630181117ad34f17ca5efb5"}
```

No test, authority, candidate, acceptance, gate, product, orchestration,
dependency, lock or environment path was changed, and no Git operation was
performed by this review.
