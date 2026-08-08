# W04 R21 cross-authority test R3 — master verification

## Decision

`ACCEPTED_FOR_INDEPENDENT_REVIEW`.

The master read every final R3 change and rejected two earlier producer attempts:

- R1 incorrectly required the fixed review, gate, and product paths to remain
  permanently absent.
- R2 corrected progression but bound the changed test to a superseded handback.
- R3 closes the lineage acyclically: the test names the final R3 return path,
  the R3 return records the final test digest, and the later independent review
  binds the complete physical bytes of both.

## Reproduced evidence

```text
final test SHA-256:
31574e6d1919455c0d358e1f11758049d55dcc568c8c622e94aaed0fc438a749

final R3 return SHA-256:
33fa1d3982643cc32e7b2f51b0436799d4de94d81dd3ab3fa2d52cea5be3ec4b

preserved R1 return SHA-256:
24a92563e9f2eae23a66f1da70e7ac1b7647f23a2be4e791024a033be7f60e95

preserved R2 return SHA-256:
7d77910ab3caa2ed612186760a3d9e3c64153c79bc84141631bab18657c0e2ba
```

Master commands and results:

```text
PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q \
  tests/contracts/test_w04_r21_cross_authority_composability.py \
  tests/contracts/test_w04_supported_feature_authority.py \
  tests/contracts/test_w04_possession_semantic_v2_authority.py \
  tests/contracts/test_w04_field_semantic_v2_authority.py \
  tests/contracts/test_w04_r21_control_preimages.py
478 passed in 38.76s

PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff format --check \
  tests/contracts/test_w04_r21_cross_authority_composability.py
PASS

PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff check \
  tests/contracts/test_w04_r21_cross_authority_composability.py
PASS

PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B \
  scripts/verify_local_only.py
25/25 PASS

git diff --check
PASS

git remote
PASS: no output
```

Retained inventory remained exact:

```text
*.pyc: 1150
sorted-path SHA-256:
7953ff36ecd0721d414d637085d0f2331dac35cafc160745e9bf35280f8a4f44

__pycache__: 150
sorted-path SHA-256:
79250878e3cfb60a3b0131857ca7b0dc79878c5165725132223d95e32f7f9fd6
```

No review, gate, product, dependency, Git, network, cloud, container, endpoint,
hosted-CI, or deployment operation occurred.
