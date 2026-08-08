# W04 Wyscout schema design independent review R12 — master verification

## Decision

`REWORK`. R12 is a valid independent merits review and its sole P1 finding is
master-reproduced. R19 requires every Class-E wrapper to use the exact
`.venv/bin/python` shebang and explicitly rejects `python3`, but four current
singularly RECORD-owned Class-E wrappers use `.venv/bin/python3`.

The correction is design-only. The current wrappers are not to be rewritten,
resynced into a preferred shape, or treated as equivalent after resolution.

## Artifact integrity and readback

- Independent R12 review: 1,182 lines, `55,762` bytes; SHA-256
  `da1b03b5eabe4e41bdd959af94ab8267a14c8a090f29345bef9d382c8ae20b0e`.
- R12 return: 93 lines, `4,274` bytes; SHA-256
  `0e89c0f844d182447177b31c27645c902f9aaeef32f5562516109037c6d1363d`.
- Candidate R19 remains 4,357 lines, `236,602` bytes; SHA-256
  `8792db725eb65265b6a68ed56ed0d5bae1f20d1704faa8925baeeba29db10ec7`.
- The master read both R12 artifacts completely.
- The reviewer authored exactly its independent review and return paths.
- R12's terminal shell inventory exactly equals its preflight:
  1,086 site pycs, 58 repository pycs, and global combined digest
  `5a332924c77f4418cee2b1024cca2e235d0f3c837c077de9cc451b666ef92d96`.

## Master reproduction

A fresh `uv sync --locked --all-groups` resolved 83 packages and audited 82.
The master then enumerated every installed RECORD path beginning
`../../../bin/`, decoded and compared its digest and size, checked target kind,
mode and link count, and compared wrapper bytes with R19's deterministic
entry-point template.

The complete current census is:

```text
installed executable rows B: 35
Class E:                    33
Class P:                     1
Class W:                     1
owners:                     21
python shebang wrappers:    30
python3 shebang wrappers:     4
non-wrapper Ruff binary:      1
```

The four P1 rows are:

| Executable | Owner | Target | Bytes | SHA-256 |
| --- | --- | --- | ---: | --- |
| `detect-secrets` | `detect-secrets==1.5.0` | `detect_secrets.main:main` | 380 | `16c1dcee3bcc2078fc6d4df7c0c85db6d043ab3bff5b40f8a13eea19e28aff3f` |
| `detect-secrets-hook` | `detect-secrets==1.5.0` | `detect_secrets.pre_commit_hook:main` | 391 | `c3535b96dea57e7a88ab48961f74e51c07b019103b89a49c3f71da4cfbda5010` |
| `httpx` | `httpx==0.28.1` | `httpx:main` | 366 | `7f7d4f633504d3f62f33335a9630e5bb4240989c9fb777b4a57e9d5c98fa394d` |
| `pip-licenses` | `pip-licenses==5.5.5` | `piplicenses:main` | 372 | `b563dfd0133f2295a703e09a820fd4b133fd1d2c438150dc6c42ec7d62e8b52f` |

All four are regular, non-symlink, single-link, mode-`0755` files with singular
matching RECORD rows. Their bytes after the first LF exactly match the required
template. Their first line alone names the admitted `python3` alias where R19
requires and exclusively permits `python`.

R19's complete-census, canonical-alias, Class-E template, stable-normalization,
and negative clauses make that mismatch fatal. The separate fact that
`python3 -> python` is a safe exact admitted alias chain does not cure the
contradiction because R19 deliberately rejects it as a wrapper shebang.

## No-write chain

Every master Python helper started with
`PYTHONDONTWRITEBYTECODE=1`, used root
`uv run --locked --no-sync`, and invoked `python -B`; the stdlib-only executable
helper additionally used `-S`. Its first attempt contained an incorrect
dist-info spelling in the review helper and stopped on an assertion; the bounded
corrected helper passed and made no write.

The complete master shell inventories were identical before sync/helpers and
after all checks:

```text
site count:                 1,086
repository count:             58
site metadata SHA-256:
0424caf9281ece4665f090a4095454d29622d6eb748e65cbc0b21701f452a26c
site content SHA-256:
a58b6915d692b5871b2d4aa807ee88523277b46b7e5fd1b99e80a63c6d3c0f46
repository metadata SHA-256:
d948edffb4538de2936a188957cec504de1610bac06abf65eb1fea9a7a7946e3
repository content SHA-256:
0107d67c8a963e08893c52a3c4a60d2ae6f1df1c190de0e226618ce01b4337f5
```

No pyc was created, deleted, renamed, repaired, or mutated.

## R20 disposition

R20 must preserve every passing R19 semantic, source, rights, temporal,
packaging, result-frame, projection, build, ownership, and no-write closure while:

1. binding the exact four `python3` Class-E rows constructively;
2. keeping all other Class-E and the sole Class-P wrapper on exact `python`;
3. rejecting generic alias equivalence and every unlisted alias assignment;
4. giving the two exact shebang roles distinct root-independent stable tokens;
5. bumping the changed executable-census stable schema to v3; and
6. bumping the dependent code/environment manifest schema to v15.

The three-alias topology itself is unchanged. No dependency, lock, `.venv`,
architecture, project root, rights, provider, storage, Git, or local-only change
is required.

## Checks

- Complete R12 review/return readback: PASS; 1,182/93 lines.
- Artifact sizes/digests: PASS.
- Fresh locked sync: PASS; 83 resolved, 82 audited.
- Exact 35-row executable census: PASS.
- R19 canonical wrapper rule against current bytes: FAIL; exact four
  first-line-only `python3` mismatches.
- Exact four owner/target/size/digest/mode/link/template-body checks: PASS.
- Master pyc preflight/postflight: PASS; 1,086/58 and all inventory hashes equal.
- Local-only verification: PASS; 25/25.
- `git diff --check`: PASS.
- `git remote`: PASS; empty.

No provider acquisition, product implementation, network access, cloud resource,
hosted CI, public endpoint, Git remote, container, or deployment was created.
