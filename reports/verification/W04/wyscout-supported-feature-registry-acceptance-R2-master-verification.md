# W04 supported feature registry acceptance R2 — master verification

## Decision

`ACCEPTED`.

The R1 acceptance attempt failed closed because it used the review return's
displayed canonical-record hash, which omitted the fenced record's terminal LF.
The focused acceptance contract hashes the exact fenced record bytes including
that LF.

The invalid R1 materialization is preserved exactly:

```text
path:
reports/reviews/W04/archive/
  wyscout-supported-feature-registry-acceptance-v1-invalid-a2227b9c.json
SHA-256:
a2227b9c22d9272e8a00e119db01f2d3a8e8702cf5696ff813d490443f82de6e
```

R2 binds the independently reconstructed values:

```text
review physical SHA-256:
a692cc4aaa002882f92209256f1bdecb96b3eb6bdba8a9bc3f645569daa31c73
exact fenced record SHA-256 including terminal LF:
1317dc7bd42c9de2284d640001d5497a7f883c09f2deb843f15e9f351a988f88
exact fenced record bytes:
752
```

All other acceptance values remain the frozen R21 values. No review or authority
byte was changed.

The corrected canonical acceptance physical SHA-256 is:

```text
d3b3c552784f4734f6b002569d9add1b4dd2d2eaaed57643a8ca4d5226fca78c
```

## Independent master verification

Executed after materialization:

```text
PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q \
  tests/contracts/test_w04_supported_feature_authority.py \
  tests/contracts/test_w04_possession_semantic_v2_authority.py \
  tests/contracts/test_w04_field_semantic_v2_authority.py \
  tests/contracts/test_w04_r21_control_preimages.py
371 passed in 32.91s

PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B \
  scripts/verify_local_only.py
25/25 checks PASS

runpy authority-state reconstruction
ACCEPTED
feature_schema_hash:
49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f

git diff --check
PASS

git remote
PASS: no output
```

The retained filesystem inventory remained exact:

```text
*.pyc: 1150
sorted-path SHA-256:
7953ff36ecd0721d414d637085d0f2331dac35cafc160745e9bf35280f8a4f44

__pycache__: 150
sorted-path SHA-256:
79250878e3cfb60a3b0131857ca7b0dc79878c5165725132223d95e32f7f9fd6
```

No cross-authority test or product path existed during acceptance validation.
The feature authority is accepted and may now be consumed only by the bounded
R21 cross-authority composability task.
