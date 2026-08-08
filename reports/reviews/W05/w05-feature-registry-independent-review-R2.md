# W05 feature registry independent review R2

- Task: `W05-FEATURES-REVIEW-01-R2`
- Reviewed bytes: current R2 registry, loader/materializers, fixture and focused tests against the unchanged accepted W04 Gold manifest and dataset card
- Date: 2026-08-03
- Verdict: **REWORK**
- Severity: **P0: 0; P1: 1; P2: 0**

R2 closes the R1 trust-root and false-claim defects: every fully re-signed root, family,
schema, descriptor, fixture and claim substitution independently replayed below rejects;
both families are non-production and non-protected; and fabricated W04 product, manifest,
player, feature value, clock, applicability and five-dependency substitutions reject.

One strict accepted-Gold identity blocker remains. `gold_row_count` is compared with the
integer pin through ordinary Python equality. JSON `true` and JSON `1.0` therefore both
compare equal to integer `1` and are admitted. The packet expressly requires the exact
one-row count and rejection of count substitutions, so R2 remains `REWORK`.

## P1 finding

### P1-01 — W04 `gold_row_count` admits boolean and float identity substitutions

`materialize_w04_real_row` currently uses:

```text
if any(row[key] != value for key, value in _W04_GOLD_PROJECTION.items()): ...
```

The accepted pin is integer `1`, but in Python `True == 1` and `1.0 == 1`. There is no
separate strict type check for `gold_row_count`. Both substitutions therefore cross the
public W04 admission boundary and materialize the accepted vector.

The independent `/tmp/w05_features_review_r2_adversarial.py` probe constructed the full
accepted row, changed only `gold_row_count`, and called the public materializer. It exited
0 and printed:

```text
ACCEPTED_ATTACK w04_row_count_bool
ACCEPTED_ATTACK w04_row_count_float
```

These are JSON-representable values (`true` and `1.0`), not custom Python objects. The
accepted manifest contains the integer row count `1`; the physical manifest SHA-256
reproduces as `08de1349a532c3f455d792ee56aafc3d8c587828bc9934dc7f77a58a71c90068`.

Smallest bounded correction: require `gold_row_count` to be a non-boolean exact integer
equal to `1` before generic identity comparison (or use an equivalent strict typed
projection validator), and add direct `true`, `1.0` and ordinary integer `1` boundary
tests. No registry, fixture, accepted W04 or digest meaning needs changing.

## R1 attack replay

The independent probe recomputed every affected schema, family, registry or fixture
digest and exact canonical bytes. All R1 substitutions now reject:

```text
REJECTED registry_id registry accepted-identity mismatch
REJECTED registry_version registry accepted-identity mismatch
REJECTED family_crosswire registry accepted-identity mismatch
REJECTED w04_family_version registry accepted-identity mismatch
REJECTED synthetic_family_version registry accepted-identity mismatch
REJECTED w04_schema_id registry accepted-identity mismatch
REJECTED synthetic_schema_version registry accepted-identity mismatch
REJECTED control_schema_id registry accepted-identity mismatch
REJECTED w04_descriptor_unit registry accepted-identity mismatch
REJECTED synthetic_provider_claim registry accepted-identity mismatch
REJECTED w04_production_claim registry accepted-identity mismatch
REJECTED w04_protected_claim registry accepted-identity mismatch
REJECTED fixture_id fixture accepted-identity mismatch
REJECTED fixture_version fixture accepted-identity mismatch
REJECTED fixture_registry fixture accepted-identity mismatch
```

The previously fabricated W04 Gold attack and expanded field attacks also reject. Every
mutated dependency envelope was re-hashed using the accepted lineage formula before
admission:

```text
REJECTED w04_product_build_id W04 accepted Gold projection identity mismatch
REJECTED w04_gold_manifest_relative_path W04 accepted Gold projection identity mismatch
REJECTED w04_gold_manifest_physical_sha256 W04 accepted Gold projection identity mismatch
REJECTED w04_gold_product_relative_path W04 accepted Gold projection identity mismatch
REJECTED w04_gold_product_physical_sha256 W04 accepted Gold projection identity mismatch
REJECTED w04_gold_product_semantic_sha256 W04 accepted Gold projection identity mismatch
REJECTED w04_gold_row_count W04 accepted Gold projection identity mismatch
REJECTED w04_feature_schema_hash W04 accepted Gold projection identity mismatch
REJECTED w04_player_id W04 accepted Gold projection identity mismatch
REJECTED w04_competition_id W04 accepted Gold projection identity mismatch
REJECTED w04_season_id W04 accepted Gold projection identity mismatch
REJECTED w04_window_definition_id W04 accepted Gold projection identity mismatch
REJECTED w04_snapshot_as_of_ts W04 accepted Gold projection identity mismatch
REJECTED w04_available_at_watermark W04 accepted Gold projection identity mismatch
REJECTED w04_feature_cutoff_ts W04 accepted Gold projection identity mismatch
REJECTED w04_applicability W04 accepted Gold projection identity mismatch
REJECTED w04_count_action_count W04 counts must equal the accepted one-row feature vector
REJECTED w04_count_coordinate_known_action_count W04 counts must equal the accepted one-row feature vector
REJECTED w04_count_match_count W04 counts must equal the accepted one-row feature vector
REJECTED w04_count_resolved_possession_action_count W04 counts must equal the accepted one-row feature vector
REJECTED dependency_reorder W04 dependency envelope does not match accepted Gold lineage
REJECTED dependency_kind W04 dependency envelope does not match accepted Gold lineage
REJECTED dependency_uuid W04 dependency envelope does not match accepted Gold lineage
REJECTED dependency_digest W04 dependency envelope does not match accepted Gold lineage
REJECTED dependency_digest_malformed W04 dependency envelope does not match accepted Gold lineage
REJECTED dependency_observed_clock W04 dependency envelope does not match accepted Gold lineage
REJECTED dependency_available_clock W04 dependency envelope does not match accepted Gold lineage
REJECTED evidence_class W04 evidence-class substitution is forbidden
REJECTED authority W04 authority substitution is forbidden
REJECTED extra_rate W04 count inputs must use the exact accepted four-feature order
```

## Accepted positives

The independently loaded current identities are:

```text
registry c12217c2daeec97059928f9085d397b2cf56433c8eb66185ab28926f95646644
W04 family b3854c5fe1c120233475e3b8224c3f3592d06d656447dedd4f764fe45da36d9b
synthetic family 8c0845ab46a71d5cd6542b3e80c568b6a678ab5a9dffbe543e894d6d78eca047
fixture 7abd569366caa439cc28563a53c51a0c7ecdd1dfb622bee49d69957f444b9545
```

The accepted manifest bindings reproduce exactly:

```text
build b1f1a9135e307b115fd1d00f19dae7951993765ee5ac1fb5d5afeb245fdc7b79
Gold manifest 08de1349a532c3f455d792ee56aafc3d8c587828bc9934dc7f77a58a71c90068
Gold product physical 6e49b4322c766352fdc427b8d35d73ddaed036d0bd19f1d65435fe3a72edcd17
Gold product semantic f1751b4f1ff7911ad339fa1954cd5c88483fc09c733547dba87d7aa301c1bffa
lineage ded9ae0a3bece552eb047e005809837871a0ccd2cf76ead47e33abcb9288ea9d
row count 1
```

The exact W04 positive materializes player
`be8da881-2b15-513f-978f-6bb3865bc8e2`, lineage
`ded9ae0a3bece552eb047e005809837871a0ccd2cf76ead47e33abcb9288ea9d`
and values `(2.0, 2.0, 1.0, 2.0)`. The synthetic fixture retains 22 rows, deterministic
repeated materialization and the distinct state union `missing`, `suppressed`,
`unavailable`, `value`, `zero`.

Both W04 flags and both synthetic flags are `false`. The W04 claim is exactly
`accepted_W04_four_count_resemblance_only_research_only`; no validation, expert or
recruitment-fitness claim was found.

## Review-question answers

1. **Fully re-signed W05 substitutions:** every replayed root/family/schema/fixture and
   semantic substitution rejects against independently coded pins. **Yes.**
2. **Sole accepted W04 Gold row:** product, manifest, player, vector, clock,
   applicability and complete-lineage substitutions reject, but boolean and float row
   counts admit. **No.**
3. **Dependency exactness:** all five accepted dependencies, kinds, UUIDs, lowercase
   digests, clocks, order and lineage reproduce; each mutated/re-hashed envelope rejects;
   no runtime product/provider read occurs. **Yes.**
4. **Claim boundary:** both families are explicitly non-production and
   non-protected-evaluation; W04 is resemblance-only/research-only and synthetic remains
   constructed-development-only. **Yes.**
5. **Feature positives:** exact-four closure, formulas, state distinctions,
   no-imputation, synthetic separation, canonical bytes and deterministic fixture all
   remain green. **Yes.**

## Six W05 blocker tests

| Blocker test | Verdict | Evidence |
| --- | --- | --- |
| 1. Admitted feature/artifact/ranking/result-byte change | **FAIL — P1** | Boolean/float `gold_row_count` replaces the accepted integer identity and admits. |
| 2. Temporal leakage or lineage substitution | **PASS** | Every mutated clock and fully re-hashed dependency envelope rejects. |
| 3. Training-serving or batch-request parity break | **PASS in packet scope** | Repeated synthetic materialization is equal; one public W04 bridge uses the exact vector. |
| 4. False explanation, confidence or claim | **PASS** | Both production/protected flags are false and all claim substitutions reject. |
| 5. Unauthorized code/data or local-only violation | **PASS** | Local-only verifier passes; review writes only two authorized reports. |
| 6. Reproducible P0/P1 correctness/security defect | **FAIL — P1** | Two JSON-representable row-count substitutions reproduce through the public materializer. |

## Acceptance checks

| Command | Status | Result |
| --- | ---: | --- |
| `uv run pytest -q tests/unit/test_w05_features.py tests/contracts/test_w05_m0_contracts.py tests/contracts/test_w04_supported_feature_authority.py` | 0 | 187 passed in 10.01s |
| `uv run ruff check src/scouting/features tests/unit/test_w05_features.py` | 0 | all checks passed |
| `uv run mypy src/scouting/features` | 0 | no issues in 2 source files |
| `uv run lint-imports` | 2 | shared uv cache denied `/Users/adrian/.cache/uv/sdists-v9/.git` before analysis |
| `UV_CACHE_DIR=/tmp/w05-features-review-01-r2-uv-cache uv run --no-sync lint-imports` | 0 | 3 kept, 0 broken; 42 files and 81 dependencies |
| `uv run python scripts/verify_local_only.py` | 0 | PASS; all 25 checks passed |
| `UV_CACHE_DIR=/tmp/w05-features-review-01-r2-uv-cache uv run --no-sync python /tmp/w05_features_review_r2_adversarial.py` | 0 | all retained attacks rejected except the two recorded strict row-count substitutions |

## Scope and residual risk

No P0 or P2 finding is asserted. No W10-only host-state observation was promoted. No
implementation, config, fixture, test, dependency, orchestration, accepted W04, Git,
provider, network, data or run byte was changed. Review artifacts are limited to the two
packet-authorized R2 report paths.
