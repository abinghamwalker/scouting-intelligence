# W05 feature registry independent review R1

- Task: `W05-FEATURES-REVIEW-01-R1`
- Reviewed bytes: current W05 feature registry, loader/materializers, synthetic fixture and focused tests against the accepted W04 feature authority and dataset card
- Date: 2026-08-03
- Verdict: **REWORK**
- Severity: **P0: 0; P1: 3; P2: 0**

The current canonical files reproduce their declared hashes, exact-four order, formulas,
state distinctions and strict cutoff behavior. They do not meet the required fail-closed
identity, accepted-Gold lineage or claim boundaries. A fully re-signed replacement
registry can cross-wire the W04 and synthetic family IDs, change a W04 descriptor unit,
and insert a Wyscout/production/expert assertion into a synthetic description while the
loader returns success. A fully re-signed fixture identity also loads. Separately, the
W04 materializer accepts arbitrary counts and a fabricated dependency digest merely
because the caller supplies the string `accepted`. Finally, the canonical W04 bridge
itself declares and the loader hard-requires `production_evidence=true` and
`protected_evaluation=true`, contrary to the accepted W04 research-only boundary and
the governing rule that W05 makes no validation claim before W06.

## P1 findings

### P1-01 — Accepted W05 root identities are not pinned; re-signed cross-wires and semantic substitutions load

`load_feature_registry` verifies only hashes supplied inside the candidate document.
It does not require the accepted registry ID/version/digest, family IDs/versions/digests,
or schema IDs/versions/hashes. `load_synthetic_development_fixture` similarly does not
pin the accepted fixture ID/version/digest. The nested hashes therefore prove internal
consistency, not identity against an external authority.

The independent `/tmp/w05_features_review_adversarial.py` probe recomputed every hash
affected by each mutation and wrote canonical compact JSON. It exited 0 and printed:

```text
ACCEPTED_RESIGNED_ROOT attacker-resigned-registry 9e5930409aaa6a4289326f19b7f8c7b0d8fc1a8852f98e732dd4d1bbeca2ca46
ACCEPTED_CROSS_WIRE w05-synthetic-development-v1 w05-w04-real-governed-bridge-v1
ACCEPTED_W04_DESCRIPTOR_SUBSTITUTION goals
ACCEPTED_SYNTHETIC_PROVIDER_CLAIM Wyscout production expert recruitment label
ACCEPTED_RESIGNED_FIXTURE attacker-resigned-fixture 22
```

This directly defeats the packet requirements that real and synthetic identities be
impossible to cross-wire, every descriptor remain exact, substituted manifests reject,
and synthetic descriptions carry no provider, production, expert or W06 claim.

Smallest bounded correction: introduce immutable accepted W05 identity pins at the load
boundary (root, both families, all three schemas, and fixture), validate exact IDs and
versions as well as digests, and add attacks that recompute all affected nested hashes.
The current clean root bytes can remain unchanged except where P1-03 requires correcting
the claim flags.

### P1-02 — The W04 bridge does not authenticate an accepted Gold row or accepted source lineage

`materialize_w04_real_row` checks an untrusted `gold_row_state == "accepted"`, equality
to the feature-authority mapping, an internally self-hashed arbitrary dependency list,
and four integer names. It pins no accepted W04 product build, Gold manifest, Gold row
identity or accepted dependency manifest. Dependency `digest` is only required to be a
non-empty string, not a SHA-256 digest or an accepted W04 identity.

The same independent probe supplied a new player, invented values `(999, 998, 997, 996)`,
and dependency digest `not-a-sha256-or-accepted-gold-manifest`; it exited 0 and printed:

```text
ACCEPTED_UNAUTHENTICATED_W04_GOLD 90000000-0000-4000-8000-000000000002 d2b5579de9dcd0eee88af739acef88764be1d914fe258e7a9e57b43bcff2fa1d (999.0, 998.0, 997.0, 996.0)
```

The exact-four structural closure is sound, but arbitrary data can be relabelled as
accepted W04 Gold. That violates the accepted-Gold and strict source/dependency-lineage
admission rule.

Smallest bounded correction: require an exact accepted W04 Gold/product lineage envelope
whose product build, Gold manifest and row/dependency identities are pinned to existing
accepted W04 authorities; validate all digest fields as SHA-256; then derive/admit the
four counts only from that authenticated projection. No accepted W04 byte needs changing.

### P1-03 — The canonical W04 bridge makes production and protected-evaluation claims reserved beyond W05

The canonical W04 family contains:

```text
production_evidence=true
protected_evaluation=true
```

`_validate_w04_bridge` requires both values to be true, so this is an executable semantic
hard-pin, not dormant metadata. The accepted W04 dataset card says the proof is local
research-only, is not suitable for live recruitment, and that complete coverage does not
mean production fitness. The governing workflow defines G-W05 as synthetic/frozen
development readiness with **“no validation claim yet”**; W06 separately freezes the
expert evaluation set and performs the protected comparison/evidence gate. The accepted
M0 contract-truth requirement likewise says synthetic development gains no production or
expert-validation claim and describes `M0EvidenceClass` as not an evaluation partition.

Thus `protected_evaluation=true` falsely claims a W06 state, and
`production_evidence=true` contradicts the accepted W04 research-only applicability.
The adjacent resemblance-only `claim` string does not cure the contradictory booleans.

Smallest bounded correction: set both W05 family claim flags false (or replace them with
unambiguous non-claim provenance fields if later packets need to distinguish governed
real bytes from synthetic bytes), update the loader expectation and derived W05 digests,
and directly test that neither W04 nor synthetic W05 families claim production evidence,
protected evaluation, validation or expert endorsement.

## Six W05 blocker tests

| Blocker test | Verdict | Exact evidence |
| --- | --- | --- |
| 1. Admitted feature/artifact/ranking/result-byte change | **FAIL — P1** | Re-signed root, crossed family IDs, changed W04 unit and changed synthetic description all loaded. |
| 2. Temporal leakage or lineage substitution | **FAIL — P1** | Row/dependency equality correctly rejected, but fabricated W04 dependency and Gold identity admitted. |
| 3. Training-serving or batch-request parity break | **PASS in packet scope** | Deterministic repeated synthetic materialization returned equality; no second feature path is introduced here. |
| 4. False explanation, confidence or claim | **FAIL — P1** | Canonical bridge hard-requires production/protected flags; re-signed synthetic provider/expert claim also loaded. |
| 5. Unauthorized code/data or local-only violation | **PASS** | Local-only verifier passed all 25 checks; review wrote only its two allowed reports. |
| 6. Reproducible P0/P1 correctness/security defect | **FAIL — P1** | P1-01 through P1-03 reproduce under the normal public loaders/materializers with exit 0. |

## Packet review questions

1. **Cryptographic W04/synthetic separation:** current IDs and six reviewed digests are
   pairwise distinct, but identity cross-wiring succeeds after complete re-signing.
   **No.**
2. **W04 exact-four and suppression:** the exact ordered four are admitted; an expanded
   counts mapping and cutoff-equal row reject; no minutes/rate/per-90 value is materialized.
   Accepted-Gold authenticity is nevertheless absent under P1-02. **No overall.**
3. **Descriptor completeness:** all 13 current descriptors contain type, unit, order,
   numerator, denominator/formula, no-imputation, state, as-of and lineage policies. A
   fully re-signed descriptor substitution (`action_count.unit = goals`) loads. **No.**
4. **Canonical bytes and substitution:** current registry logical digest
   `5cf2864f763d4670a2baa882c1db32c88cf194f3da0b573b148be50641edd946`
   and fixture logical digest
   `cd5de08b648a94b0c8d3f2c8e5e84d330887381621492641a5e1514bbf8fc8a7`
   reproduce; physical SHA-256 values are respectively
   `c9c970a9209451679c471326719df30826dfabbbe62f8cb91897b89f494a105d`
   and `ff0a10ca4c093f8959b6319ee72bfbc12362e426f59c7f412e6c53b03b1196a1`.
   Re-signed root and fixture identities load. **No.**
5. **Synthetic states and formulas:** 22 rows load; the edge union is exactly inclusive
   of `missing`, `suppressed`, `unavailable`, `value` and observed `zero`; repeated row
   materialization is equal; invalid zero denominators do not become numeric values.
   **Yes.**
6. **Time, lineage, identity and manifest attacks:** row observed/available cutoff
   equality and dependency cutoff equality reject. Re-signed manifests and unauthenticated
   W04 lineage admit. **No.**
7. **Development-only labels and claims:** current peer-group notice correctly disclaims
   recruitment outcomes, external expert labels and W06 evidence, but the canonical W04
   flags make forbidden production/protected claims and a re-signed synthetic expert claim
   loads. **No.**

## Positive evidence and required checks

The independent positive probe printed:

```text
CURRENT_DESCRIPTOR_COMPLETENESS True 13
CURRENT_IDENTITY_DIGESTS_DISTINCT True 6
CURRENT_FIXTURE_STATES ['missing', 'suppressed', 'unavailable', 'value', 'zero']
CURRENT_DETERMINISM True
REJECTED_SYNTHETIC_CUTOFF_EQUALITY observed_at synthetic row observed_at and available_at must be strictly before cutoff
REJECTED_SYNTHETIC_CUTOFF_EQUALITY available_at synthetic row observed_at and available_at must be strictly before cutoff
REJECTED_DEPENDENCY_CUTOFF_EQUALITY every dependency must be strictly before feature_cutoff_ts
```

| Command | Status | Result |
| --- | ---: | --- |
| `uv run pytest -q tests/unit/test_w05_features.py tests/contracts/test_w05_m0_contracts.py tests/contracts/test_w04_supported_feature_authority.py` | 0 | 183 passed in 9.68s |
| `uv run ruff check src/scouting/features tests/unit/test_w05_features.py` | 0 | all checks passed |
| `uv run mypy src/scouting/features` | 0 | no issues in 2 source files |
| `uv run lint-imports` | 2 | shared uv cache denied `/Users/adrian/.cache/uv/sdists-v9/.git` before analysis |
| `UV_CACHE_DIR=/tmp/w05-features-review-01-r1-uv-cache uv run --no-sync lint-imports` | 0 | 3 kept, 0 broken; 42 files and 81 dependencies |
| `uv run python scripts/verify_local_only.py` | 0 | PASS; all 25 checks passed |
| `UV_CACHE_DIR=/tmp/w05-features-review-01-r1-uv-cache uv run --no-sync python /tmp/w05_features_review_adversarial.py` | 0 | positive boundaries and every P1 attack reproduced as recorded above |

Passing focused tests do not close the P1 attacks because those tests drift a digest or
mutate structure without recomputing all nested trust identities; the independent attacks
re-sign every affected layer.

## Scope and residual risk

No P0 or P2 finding is asserted. No W10-only host-state observation was promoted. No
implementation, config, fixture, test, dependency, orchestration, accepted W04, Git,
provider, network, data or run byte was changed. Review artifacts are limited to the two
packet-authorized report paths.
