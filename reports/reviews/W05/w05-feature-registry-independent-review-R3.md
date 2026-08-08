# W05 feature registry independent review R3

- Task: `W05-FEATURES-REVIEW-01-R3`
- Reviewed bytes: current R3 feature loader/materializer and focused tests, with retained R2 registry, fixture, Gold-lineage and claim identities
- Date: 2026-08-03
- Verdict: **PASS**
- Severity: **P0: 0; P1: 0; P2: 0**

The sole R2 blocker is closed. The public W04 bridge now requires
`gold_row_count` to be a non-boolean Python integer exactly equal to `1` before generic
projection equality. Independent direct probes show JSON `true`, `1.0`, `false`, `0`
and `2` all reject for the exact row-count type/value reason, while ordinary JSON integer
`1` returns the unchanged accepted player, five-dependency lineage and exact-four vector.

No retained R2 closure regressed: fully re-signed root, family cross-wire, W04 descriptor,
synthetic provider/evaluation-language, protected-evaluation and fixture replacements all
reject against accepted pins. Fabricated player, count, Gold manifest, dependency order
and cutoff watermark also reject. Both families remain non-production and
non-protected-evaluation; synthetic formulas, distinct states and deterministic reload
remain intact.

## Direct row-count boundary

The independent `/tmp/w05_features_review_r3_adversarial.py` probe called the public
materializer with each required JSON-representable scalar and printed:

```text
REJECTED gold_row_count_true W04 gold_row_count must be the non-boolean integer 1
REJECTED gold_row_count_float_1_0 W04 gold_row_count must be the non-boolean integer 1
REJECTED gold_row_count_false W04 gold_row_count must be the non-boolean integer 1
REJECTED gold_row_count_zero W04 gold_row_count must be the non-boolean integer 1
REJECTED gold_row_count_two W04 gold_row_count must be the non-boolean integer 1
ACCEPTED_INTEGER_ONE int be8da881-2b15-513f-978f-6bb3865bc8e2 ded9ae0a3bece552eb047e005809837871a0ccd2cf76ead47e33abcb9288ea9d (2.0, 2.0, 1.0, 2.0)
```

This proves both type and value closure without changing the accepted positive.

## Retained attack replay

Every selected R2 trust-root, Gold-lineage and claim attack rejected:

```text
REJECTED resigned_root registry accepted-identity mismatch
REJECTED resigned_family_crosswire registry accepted-identity mismatch
REJECTED resigned_w04_descriptor registry accepted-identity mismatch
REJECTED resigned_synthetic_claim registry accepted-identity mismatch
REJECTED resigned_protected_claim registry accepted-identity mismatch
REJECTED resigned_fixture fixture accepted-identity mismatch
REJECTED fabricated_player W04 accepted Gold projection identity mismatch
REJECTED fabricated_count W04 counts must equal the accepted one-row feature vector
REJECTED fabricated_manifest W04 accepted Gold projection identity mismatch
REJECTED reordered_dependency W04 dependency envelope does not match accepted Gold lineage
REJECTED post_cutoff_watermark W04 accepted Gold projection identity mismatch
```

Affected registry candidates and the fixture candidate were fully re-signed with all
nested hashes and canonical bytes before loading. The current retained positive printed:

```text
RETAINED_POSITIVES c12217c2daeec97059928f9085d397b2cf56433c8eb66185ab28926f95646644 False False False False 22 ['missing', 'suppressed', 'unavailable', 'value', 'zero'] True
```

The unchanged physical SHA-256 identities are registry
`8616e5b14540a5666097fd06d3ec4f98ea56ba2a706601a99f462c3c5badfb1a`,
fixture `25b42be0f038265fdc5480c15689598c7d83e5b16463f35292634ee6beb41c02`
and accepted Gold manifest
`08de1349a532c3f455d792ee56aafc3d8c587828bc9934dc7f77a58a71c90068`.

## Six W05 blocker tests

| Blocker test | Verdict | Evidence |
| --- | --- | --- |
| 1. Admitted feature/artifact/ranking/result-byte change | **PASS** | All six row-count boundaries are exact; re-signed identities and descriptor changes reject. |
| 2. Temporal leakage or lineage substitution | **PASS** | Reordered dependency envelope and cutoff-equal watermark reject. |
| 3. Training-serving or batch-request parity break | **PASS in packet scope** | Accepted public bridge returns the exact pinned vector; repeated synthetic materialization is equal. |
| 4. False explanation, confidence or claim | **PASS** | Both family flags remain false; re-signed synthetic/protected claims reject. |
| 5. Unauthorized code/data or local-only violation | **PASS** | Local-only verifier passes; review writes only its two authorized reports. |
| 6. Reproducible P0/P1 correctness/security defect | **PASS** | No retained or expanded R3 attack admits; P0/P1/P2 are all zero. |

## Acceptance checks

| Command | Status | Result |
| --- | ---: | --- |
| `uv run pytest -q tests/unit/test_w05_features.py tests/contracts/test_w05_m0_contracts.py tests/contracts/test_w04_supported_feature_authority.py` | 0 | 193 passed in 9.71s |
| `uv run ruff check src/scouting/features tests/unit/test_w05_features.py` | 0 | all checks passed |
| `uv run mypy src/scouting/features` | 0 | no issues in 2 source files |
| `uv run lint-imports` | 2 | shared uv cache denied `/Users/adrian/.cache/uv/sdists-v9/.git` before analysis |
| `UV_CACHE_DIR=/tmp/w05-features-review-01-r3-uv-cache uv run --no-sync lint-imports` | 0 | 3 kept, 0 broken; 42 files and 81 dependencies |
| `uv run python scripts/verify_local_only.py` | 0 | PASS; all 25 checks passed |
| `UV_CACHE_DIR=/tmp/w05-features-review-01-r3-uv-cache uv run --no-sync python /tmp/w05_features_review_r3_adversarial.py` | 0 | all five invalid scalars and all retained attacks rejected; integer `1` and retained positives passed |

## Scope and residual risk

No P0, P1 or P2 finding remains. The shared-cache permission condition is environmental;
the authorized isolated `--no-sync` execution passed. No implementation, config, fixture,
test, dependency, orchestration, accepted W04, Git, provider, network, data or run byte was
changed. Review artifacts are limited to the two packet-authorized R3 report paths.
