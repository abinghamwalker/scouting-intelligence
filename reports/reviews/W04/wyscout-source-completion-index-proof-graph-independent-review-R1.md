# W04 source-completion-index R4 proof-graph independent review R1

Date: 2026-07-31

## Disposition

- Packet: `W04-SOURCE-COMPLETION-INDEX-REVIEW-04-R1`
- Role: fresh independent W04 proof-graph reviewer
- Disposition: **PASS**
- Open findings: P0 `0`, P1 `0`, P2 `0`
- Acceptance rule: PASS requires zero open P0-P2 findings.

The R4 candidate closes `W04SCIIDXR3CAPR1-P1-001`. Exposed issuer callables and
mutable weak registries remain discoverable process-local lookup mechanisms, but they
no longer confer authority. Every checked consumption starts a fresh verification
context, re-executes exact retained completion evidence, recursively reconstructs the
exact product graph, and compares the reconstructed exact value and completion scopes
to the registry record. The completed inspection, prescribed suite and independent
bounded probes found no route by which incomplete, malformed, detached, cyclic,
nonaccepted or cross-scope evidence can pass checked consumption.

## Fixed candidate identity

Every fixed binding was recomputed before analysis and matched exactly:

| Material | Expected and observed SHA-256 | Result |
|---|---|---|
| `src/scouting/sources/wyscout_completion_index.py` | `e7778db8c977b8461bb590f7174e4b519d7a2ba0a4171d99aa1fd686a6cd5302` | match |
| `src/scouting/contracts/wyscout_data.py` | `154f1ae9934615a2ce9a24a4f8e373cd640a4c3246df93f0e35e6bed28517932` | match |
| `tests/unit/test_wyscout_source_completion_index.py` | `05593a0a0afda62af2b6a2c8753a4f83e78fcbd363b89788751dd2055ed6dfeb` | match |
| `tests/contracts/test_wyscout_data_contracts.py` | `139683be6a9e6dc4d8be90cd81bb0827c1dbeea00b4ad01aebe3bdcaf9d5be9e` | match |
| `reports/reviews/W04/returns/W04-SOURCE-COMPLETION-INDEX-01-R4.md` | `aa165fd8bc74d56e4e4e72da6d2cd7f11a2b65cc389f98efeafd3894b3c72a36` | match |
| immutable source-completion index | `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df` | match |

No drift stop condition was reached.

## Exact proof-graph review

### Completion evidence and registry exposure

`_CheckedCompletionRecord` retains the accepted `SourceCompletionIndex`, exact ordered
`CompletionActionEvidence` tuple and declared scope kind. `_checked_completion_record`
accepts only the exact record type and invokes `_verify_completion_evidence`; registry
membership is therefore only a lookup. Verification validates the accepted index and
re-executes either `validate_match_period_population` or `validate_match_population`,
then derives period sequences, period keys and `complete_match` from those results.
No caller-supplied Boolean, sequence, membership digest, period key or issuer identity
is credited.

Standard callable introspection still exposes the completion issuer retained by the
public checked validators, and the getter closure still exposes the weak registry.
Independent direct use of those surfaces showed:

- a single accepted period labelled as a match failed because an indexed period was
  omitted;
- an altered action population failed the accepted membership comparison;
- a full-match population labelled as one period failed for cross-period population;
- a malformed scope kind failed explicitly;
- replacing a previously valid registry record with false match evidence failed on the
  next public checked use because that use created a fresh context;
- a registry-issued complete match record passed only when its retained population
  rederived exactly the same two sequences as the public match path.

This independently reproduces the original exposed-issuer failure mode as closed.

### Product construction graph and checked boundary

`_CheckedProductRecord` retains construction kind, raw value, exact completion handles,
canonical payload items and typed dependency tuples. `_checked_product_record` accepts
only the exact record type, rejects active identities as cycles and invokes
`_verify_product_evidence`. That verifier validates canonical payload shape and exact
dependency tuple types, dispatches only an admitted construction kind, recursively
verifies every referenced product/completion, reconstructs the exact Action,
Possession, Fact, Gold or manifest, requires exact completion-handle sequence, and
requires exact reconstructed type and value equality.

`require_checked_product` creates one fresh top-level context, verifies the full product
graph, enforces the requested exact result type and reuses the same context only for
the final completion check. The public `.value` property also calls the verified record
boundary; it is not a raw registry read.

Direct issuer and registry probes showed:

- a detached raw manifest with no completion proof failed;
- unknown construction kind, malformed payload evidence and malformed dependency
  containers failed;
- a self-referential product graph failed at the active-product cycle guard;
- an outer product referencing a malformed inner record failed during recursive
  verification;
- a previously valid product failed after its registry record was replaced with
  detached evidence;
- requesting the wrong exact output type failed;
- a registry-issued copy of a valid product record passed only because its complete
  payload, scope and dependency evidence independently reconstructed the exact public
  result.

Thus an exposed issuer can reproduce public authorization only by presenting the full
evidence that the public checked path itself would authorize. It cannot turn an
arbitrary detached semantic model into checked authority.

### Memoization, identity and scope

The verification context exists only for one top-level graph. Completion and product
cache entries are populated only after successful exact verification. Product graph
records and their dependency tuples retain strong references to all live handles while
the context is active, so a verified identity cannot be collected and reused by a
different live dependency inside that graph. An independently issued second live
completion had a distinct identity; replacing its registry record with a malformed
record was not mistaken for the already verified first handle.

The independent top-level manifest probe counted exactly one
`_verify_completion_evidence` invocation for its shared completion population. The
accepted real-match regression independently asserts the same invariant across the
larger Action-to-Possession-to-Fact-to-Gold-to-manifest graph. Fresh public calls do not
retain the previous context, so stale registry mutation is rechecked rather than
accepted.

Two independently issued scopes covering the same indexed period were rejected. A
full-match scope combined with an overlapping period scope was also rejected with
`layer completion scopes cannot overlap one indexed period population`. Product
dependencies require the exact retained completion handles; Facts additionally require
freshly derived `complete_match=True`.

### Exact legitimate path and original bypass

The accepted index resolves match `2499719` to exact period populations `901` and
`867`, total `1768`. The prescribed real-source regression completed checked Action,
Possession, Fact, Gold and one-match Gold manifest construction. It retained the exact
Gold vector `(action_count=2, coordinate_known_action_count=0, match_count=1,
resolved_possession_action_count=2)` and one completion verification for final
top-level manifest consumption.

The fail-fast-reader regression patches the accepted reader/validation surfaces and
observes the checked match boundary fail immediately. A direct raw Gold remains
`semantic_only_unchecked` and fails `require_checked_product`. No `model_construct`
occurs in the reviewed implementation or credited tests/probes.

## Executable evidence

| Command or bounded check | Result |
|---|---|
| `shasum -a 256` over the four frozen implementation/test files and R4 producer return | exit `0`; all five fixed digests matched |
| `shasum -a 256 data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json` | exit `0`; immutable index digest matched |
| `uv run pytest -q tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_wyscout_data_contracts.py tests/contracts/test_foundation_contracts.py tests/contracts/test_w04_identity_ruleset_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/unit/test_wyscout_source_manifest.py` | exit `0`; `500 passed in 175.09s` |
| `uv run bandit -q -r src/scouting/sources/wyscout_completion_index.py src/scouting/contracts/wyscout_data.py` | first sandboxed attempt exit `2` because existing shared uv-cache metadata was unreadable; approved read-only rerun exit `0`, no findings |
| `uv run python scripts/verify_local_only.py` | exit `0`; PASS, 25/25 controls and zero failures |
| independent inline completion/product issuer, registry, recursion and memoization probe through `uv run python` | initial sandboxed cache-read attempt exit `2`; approved read-only rerun exit `0`; all intended false-match, nonaccepted, malformed, detached, stale, cyclic, recursive, type and exact-rederivation checks passed |
| corrected independent full-match/period overlap and exact-match probe through `uv run python` | exit `0`; overlap rejected; match `2499719`, periods `(901, 867)`, total `1768` confirmed |

The first overlap variant in the broad in-memory probe encountered an intentionally
malformed registry record before reaching the overlap check. It was not credited as
overlap evidence; the separate corrected probe used fresh valid scopes and reproduced
the explicit overlap rejection.

## Findings and recommendation

No P0, P1 or P2 finding remains within this packet. Recommendation: **PASS** with P0
`0`, P1 `0`, P2 `0`, subject to master reproduction and acceptance. This review does
not self-approve the phase or authorize product implementation.

No implementation, contract, test, data, index, frozen authority, orchestration,
verification, dependency, lock or product byte was edited. No Git operation,
delegation, provider/network access, external service, cloud, container, hosted CI,
endpoint, remote or deployment action occurred.
