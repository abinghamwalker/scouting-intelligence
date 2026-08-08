# W04 R21 cross-authority gate R1 — master verification

## Decision

`ACCEPT`.

The master accepts the bounded progression-fixture correction after executable
failure demonstrated that the prior perpetual absence assertion contradicted the
future identity route expressly required by R21. This is a test progression
correction, not an architecture or semantic revision.

## Exact corrected surface

Only `test_exact_resource_roster_preserves_v1_prefix_without_identity_overclaim`
changed. The exact identity-resource lifecycle is now:

```text
1. all four fixed identity authority paths absent
2. decision and candidate present together
3. independent review added
4. master acceptance added
```

Every candidate half, review-before-candidate, and
acceptance-before-review state remains rejected. The exact 30-resource roster,
path order, and path-list digest remain unchanged, as do all R21 field v2,
possession v2, four-feature, preimage, dependency, product, and serializer
contracts.

## Bound evidence

```text
superseded test SHA-256:
fffb71d4d382816f3572b575cbcd9e951309f92239ca540327cdb02304c4f9b0

corrected test SHA-256:
c51d16e1de99c28cfe5cde2feeeb8cbfc908516a59edc47cd53b08e955e75b26

unchanged R4 test-return SHA-256:
9f45ccd44c9f27c53b72331609dd040fc1ca9211c630181117ad34f17ca5efb5

fresh independent review SHA-256:
e9eca309986140ddfe40c66645a3f640777ff700e6a7187d43f020060d35c070

progression-review return SHA-256:
011617e907df280989fdb24a7ff938dd0a49849ead7e19766eeff44d351f3a6f
```

The prior accepted review and gate evidence remain byte-identical under explicit
archive paths. No evidence was deleted.

## Independent review

The fresh independent reviewer returned `PASS` with zero findings and a new
canonical actor distinct from every master, producer, authority reviewer, and
the superseded cross-authority reviewer. The exact six-key machine record binds
the corrected test and unchanged R4 test return.

The reviewer edited only the fixed review and its return, performed no Git
operation, and created no gate, identity-runtime, or product path.

## Master-reproduced focused checks

```text
uv run ruff format --check \
  tests/contracts/test_w04_r21_cross_authority_composability.py
PASS

uv run ruff check \
  tests/contracts/test_w04_r21_cross_authority_composability.py
PASS

uv run pytest -q \
  tests/contracts/test_w04_r21_cross_authority_composability.py \
  tests/contracts/test_w04_identity_ruleset_authority.py \
  tests/contracts/test_w04_supported_feature_authority.py \
  tests/contracts/test_w04_possession_semantic_v2_authority.py \
  tests/contracts/test_w04_field_semantic_v2_authority.py \
  tests/contracts/test_w04_r21_control_preimages.py
PASS — 508 passed in 40.32s
```

## Complete repository master gate

After the serial identity authority reached independently reviewed master
acceptance, the master reran the exact complete repository gate from the
beginning:

```text
uv sync --locked --all-groups
PASS — 83 resolved, 82 audited

uv run ruff format --check .
PASS — 395 files already formatted

uv run ruff check .
PASS

uv run mypy src/scouting scripts
PASS — no issues in 41 source files

uv run lint-imports
PASS — 29 files, 44 dependencies, 3 contracts kept

uv run pytest -q
PASS — 1326 passed, 1 known Starlette warning in 226.86s

uv run bandit -q -r scripts src
PASS

uv run python scripts/install_local_git_guards.py --check
PASS — executable pre-push hook; simulated exit 1

uv run python scripts/verify_local_only.py
PASS — 25/25 checks

uv run python scripts/verify_phase.py --phase W04
PASS — all tasks accepted and evidenced; zero remotes

git status --short
PASS — expected reviewed local changes only

git remote
PASS — empty
```

The stale `credential_separator_encoding` security fixture is included in the
passing 1,326-test repository suite.

## Boundary

The complete pre-product repository gate is now satisfied. The next serial
authority is the bounded W04 data-contract implementation. Runtime, Bronze,
Silver, Gold, build, model, endpoint, hosted CI, cloud, and deployment work
remain subject to their own exact packets and master verification.
