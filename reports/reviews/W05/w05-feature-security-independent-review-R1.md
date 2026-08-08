# W05 feature-loader security independent review R1

- Task: `W05-FEATURES-SECURITY-REVIEW-02-R1`
- Reviewed boundary: terminal assert replacement in `src/scouting/features/registry.py`
- Date: 2026-08-03
- Verdict: **PASS**
- Severity: **P0: 0; P1: 0; P2: 0**

The correction is fail-closed under both ordinary and optimized Python. Every former
terminal assert condition now raises the same deterministic `FeatureRegistryError` when
Python assertions are enabled or removed. The accepted registry, all 22 synthetic rows,
the exact W04 bridge, the selected artifact, and the complete frozen serving result are
unchanged. No W06/W10 evidence or conclusion is part of this review.

## Runtime-boundary attacks

Two independent public/module-boundary matrices were executed using respectively
`uv run --no-sync python` and `uv run --no-sync python -O`. Both produced these exact
outcomes:

| Attack | Ordinary Python | `python -O` |
| --- | --- | --- |
| synthetic family with absent metadata-control schema | `FeatureRegistryError: synthetic metadata-control schema is required` | identical |
| observed feature state with no numeric value | `FeatureRegistryError: observed feature calculation requires a numeric value` | identical |
| W04 registry family with absent authority | `FeatureRegistryError: W04 authority is required` | identical |
| W04 dependency list containing a non-mapping entry | `FeatureRegistryError: W04 dependency entries must be objects` | identical |

No attack was admitted. In both runtimes, the same probe also reloaded and materialized
the accepted registry, fixture, all 22 rows, and exact W04 bridge. Their complete positive
projection digest was exactly
`529664bffdcda7a19291ad98457908bb41b9255ec20e73763b4319d3b7b0332e`.

The retained W04 positive is:

- player: `be8da881-2b15-513f-978f-6bb3865bc8e2`;
- schema: `cf8847f2b1f70ebf293ce90e48817e80a4e47b78316079bd88e8c2a80bc08127`;
- lineage: `ded9ae0a3bece552eb047e005809837871a0ccd2cf76ead47e33abcb9288ea9d`;
- values: `(2.0, 2.0, 1.0, 2.0)`.

## AST and security proof

Fresh AST parsing found zero `ast.Assert` nodes and zero `__debug__` names in the
production feature module. A source scan found no Bandit suppression, `nosec`, or `noqa`
marker. Bandit returned exit 0 with quiet output both for the feature module alone and
for the repository security scope `scripts src`; therefore no runtime-assert,
medium-severity, or high-severity finding remains.

## Frozen identities and downstream result attack

The registered selected artifact was served twice through the accepted local serving
core. The two complete model JSON wires were exact. The following frozen identities and
outputs reproduced:

- artifact ID: `9a0d43c6-d177-51be-8280-3bf02bedbc99`;
- logical manifest digest: `2ed113a19acec3a3bbd80038ecc0b639a4a587111b35af2d4d7b0edd651c8fa9`;
- result digest: `9d08d8f0ddaba47a3461754d53d727709ea7a10276b438c18c9953b17ad3020e`;
- M0 result ID: `e77948a1-2987-514d-a585-cd54015e2152`;
- retrieval result ID: `8a0c3594-0b40-572a-8a9a-aecaa0b6052e`;
- retrieval run ID: `332c42c4-6b0d-5fd5-b8aa-f09ae9ae501c`;
- complete result-wire SHA-256:
  `47d51a331bf655d3cee1ec22b64b756f2082ae59ad27d46fa7a1610c16d7ac96`;
- candidate/evidence/confidence/dimension/explanation/temporal projection SHA-256:
  `e897f24d340d249236455938e3bb0d228e6587c454cb5f9a52b6a5c85c804a92`;
- claim boundary: `resemblance_only`.

The exact ranking remained:

1. `20000000-0000-4000-8000-000000000002`, distance
   `0.00013857118024163118`;
2. `20000000-0000-4000-8000-000000000003`, distance
   `0.000554708060777731`;
3. `20000000-0000-4000-8000-000000000004`, distance
   `0.0012485263821517822`.

All six per-candidate contribution values also matched the frozen predecessor result.
Thus no ranking, result, claim, or evidence byte changed.

## Physical immutability

The following SHA-256 values were recorded before the attack matrix, after the runtime
and security probes, and after all acceptance checks. Every snapshot was identical:

- registry: `8616e5b14540a5666097fd06d3ec4f98ea56ba2a706601a99f462c3c5badfb1a`;
- fixture: `25b42be0f038265fdc5480c15689598c7d83e5b16463f35292634ee6beb41c02`;
- artifact manifest: `c88f101211d8e26c06622021a4d9333ce1c0e9217999a100aee71812446f443a`;
- artifact arrays: `73374ba529e2628112b7886e549e2b570883781544cd65478ea96a838975dfc6`;
- artifact configuration: `d4d6839382267f3eb1cb8d767e01f833e106332e314ead886e9f08997681c006`;
- artifact candidate universe:
  `2a8bd89b9715e2a0349e2aaba22f890333139a5142b931ae4e844aaa9bc5807e`.

## Acceptance checks

Every command used
`UV_CACHE_DIR=/private/tmp/w05-feature-security-review-cache uv run --no-sync`.

| Check | Exit | Result |
| --- | ---: | --- |
| focused feature/contract/model/serving pytest packet | 0 | `64 passed in 1.15s` |
| Ruff check on feature module and focused feature tests | 0 | all checks passed |
| mypy on feature module | 0 | no issues in one source file |
| Bandit on feature module | 0 | zero findings |
| Bandit on `scripts src` | 0 | zero findings |
| import-linter | 0 | 3 contracts kept, 0 broken |
| local-only verifier | 0 | PASS, all 25 checks passed |
| ordinary runtime attack/positive probe | 0 | four rejects; accepted output exact |
| optimized runtime attack/positive probe | 0 | identical four rejects and accepted output |
| frozen downstream serving replay | 0 | exact result, ranking, claim and evidence |

## Six W05 blocker tests

| Blocker test | Verdict | Evidence |
| --- | --- | --- |
| admitted feature/artifact/ranking/result-byte change | **PASS** | Exact logical, physical, positive-output and downstream result identities retained. |
| temporal leakage or lineage substitution | **PASS** | Exact W04 and 22-row lineage projections retained; malformed dependencies reject. |
| training-serving or batch-request parity break | **PASS** | Focused suite passes and frozen serving replay is byte-exact. |
| false explanation, confidence or claim | **PASS** | Evidence projection is unchanged and claim remains `resemblance_only`. |
| unauthorized code/data or local-only violation | **PASS** | Local-only verifier passes; review writes only its two report paths. |
| reproducible P0/P1 correctness/security defect | **PASS** | Normal, optimized, AST and Bandit attacks all close; P0/P1 are zero. |

## Scope and residual risk

No P0, P1, or P2 finding remains in this mechanical terminal-gate correction. This PASS
does not make the synthetic development evidence production evidence, recommendation
evidence, protected evaluation, or W06/W10 evidence. No source, test, configuration,
fixture, artifact, orchestration, dependency, lock, or Git state was changed.
