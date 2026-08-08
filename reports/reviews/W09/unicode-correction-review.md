# W09 provider Unicode correction — independent review

Decision: **ACCEPT**

Open findings: **P0/P1/P2/P3 = 0/0/0/0**

## Scope reviewed

The review covered the provider-text normalizer, fail-closed Unicode tests,
canonical-to-feature propagation, rebuilt canonical/matrix/index/evaluation authorities,
active gate evidence, local-only controls, and proof that scoring behaviour was unchanged.

Two rework rounds were completed. First, active evidence was rebound and already-decoded
surrogate code points were explicitly rejected and tested. Second, the complete authority chain
was rebuilt after surrogate hardening so the accepted canonical build binds the exact final
producer code. A final stale feature-code digest in the verification report was also corrected
before acceptance.

## Accepted authority

- Canonical build: `72969be11e9a13a3f2c87b92ccff0296e9ab026fdd531383ce67af074740fdb7`
- Canonical manifest SHA-256: `587f696996304c3aea888f12a486afa89e458c7cc68a2fafd5e85d38e004be59`
- Canonical code digest: `e2b6c9fa4f978563f67760527be790dc030a41ce5f310c2052ef1093e2a06725`
- Matrix: `w09-historical-player-window-v1-a31511705ac15a5d`
- Matrix digest: `428d25ed4f1fd5dec7df74f30905db875cd548270fc2824b431e1bc8a6447cc1`
- Matrix manifest digest: `dda2588f7ad81443aac614a359fbda1fcb60e533ca0d56db5d59e4669a754692`
- Index ID: `d362d87e-4d02-56a1-a5c8-446f5eaa72a3`
- Index manifest digest: `30c2b6c1e0d65c8214860131f690b8b6cac05fe317ffa208a2785e11160eb0bc`
- Evaluation suite digest: `1c922dafed2d7bdd773ad104ae2700330f0262da80a1e2e67327c5bcb6e8adc1`
- Evaluation result digest: `835e31f1eb2ba0e7dc0456c3dca9a5918fb82c278567f00247aa26bf8a5da9c0`

The manifest code digest exactly reproduces from the final producer implementation.

## Independent evidence

- Focused canonical, feature, index and evaluation suite: **60 passed**.
- Ruff formatting/lint and mypy: **PASS**.
- Local-only verifier: **25/25 PASS**.
- All 11 canonical artifact hashes and sizes reproduce from the final manifest.
- The 3,603-player catalogue contains zero literal Unicode escape sequences.
- `İ. Gündoğan`, `Ł. Fabiański` and `Ó. Duarte` are present as correct Unicode.
- Valid surrogate pairs decode; malformed, nested, escaped-unpaired and already-decoded high/low
  surrogates fail closed.
- Unicode survives canonical construction, feature catalogue loading and matrix loading.
- Index vectors and both scaler arrays are byte-identical to the original accepted build.
- Twenty-three stable feature fields are identical. Changed fields are limited to display/team
  text and content-addressed authority lineage.
- Frozen evaluation player IDs, candidate ordering, ranks, scores, explanation digests and score
  digests are unchanged.
- Active gate and verification reports use the final authority. Older IDs remain only in
  explicitly historical packets and reviews.

## Residual boundary

The correction restores provider-text fidelity only. It does not change eligibility, features,
scaling, retrieval behaviour, ranking quality or the accepted claim boundary. G-RW4 remains not
performed, and no football-relevance or recruitment recommendation claim is supported.

No repository files were edited and no Git mutations were performed during the independent
review.
