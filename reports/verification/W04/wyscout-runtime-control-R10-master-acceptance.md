# W04 Wyscout runtime-control R10 master acceptance

- Date: `2026-08-03`
- Producer task: `W04-WYSCOUT-RUNTIME-CONTROL-01-R10`
- Independent review: `W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R10`
- Decision: **MASTER_ACCEPTED**
- Independent findings: `P0/P1/P2 = 0/0/0`

## Accepted bounded correction

R10 is accepted under the standing bounded-correction authority dated
`2026-08-02`. It closes the retained first-real-root rebuild-child failure without
changing a logical field, key, value, order, root roster, product population,
projection/invocation inverse, build-ID formula, digest meaning, dependency,
source authority, data-rights authority, or local-only boundary.

The rebuild child now requires one exact ordered 25-key built-in JSON object and
exact built-in arrays for `authority_rows` and `dependency_rows`. It creates one
new ordered mapping in which only those two outer arrays become tuples, then calls
`RebuildInvocation.model_validate(..., strict=True)`. Every nested object and each
of the other 23 values is retained by identity. Strict validation and enclosing
build equality occur before `_publication_roots` and every product, manifest, or
receipt writer.

The exact canonical transport round trip reproduces the five accepted authority
rows, five accepted dependency rows, strict projection/invocation inverse, sole
projection hash, and original logical JSON bytes with no rounding, coercion,
filtering, defaulting, reordering, or copy of nested values.

## Frozen accepted bindings

| Artifact | SHA-256 |
| --- | --- |
| R10 producer packet | `d6c0872b86928dc1a53ed0476f26be7ae9ace500bdaae3e25c8a535e5356748f` |
| R10 independent-review packet | `4a52523b41263f115de8195b55feb5b60ff8001a63050458b10469bc56e5c8bb` |
| accepted admission child | `f6dbce7ffd48320155ab0562ef27a4f79c99e80aa1b122e5f0b039c493048f05` |
| accepted launcher | `6211ff1cd0b51bdd3ab24fe26358077f46f1ad0526ff60126776606ca01243eb` |
| accepted rebuild child | `fff279d4d4a6a1c76ea6ee2cc9c7a88a4d5fd2c56ca677984a1dcce765ef9339` |
| accepted runtime-control tests | `12924b9905a8334c4a6f83bb00b170059be0bb965a1d3d6b4f0c09d364a95abf` |
| accepted security tests | `5907b945fa61855ff1104a2e03dd13057a76863251258b8a53088e322b44d18d` |
| producer return | `56004852a1868b89579d65ee781b5ef9a26b922451f25dbbe61f1b94aaa55854` |
| independent review | `331082c9482cabae5957e950e0b61683194138e979c6cff07eff06cf51ae80d6` |
| independent-review return | `9da5ec8e400561459b1c2aba3a4fb8828ec4622c8e7d9e9f908313bc46ba95d0` |
| retained unaccepted pre-R10 code manifest | `fb1bcca5772d71a0de2c116cd2539d1d2cd757554df8791dad8e0d952cf67083` |
| disclosed operational launcher PYC | `b1c8fbd8e5de10d6251995b9dc0fbbcb7457ba0bdaffd669e6e58c86d280b52e` |
| shell PYC census helper | `2702b38453c95e428e9289cfc0bd6a9d0f1a748aeb33f1bad1e1c7033eaf4a6d` |
| master boundary audit | `7ecc95fd63fc441c0f09bbfdd0050694163bd5edcd939e988a9ab09158240998` |
| master gate script | `6bb60adc3f6cba1a3878b20b4fc053e84816af8604ac8997e0e676c0d6054aee` |

## Producer and independent-review evidence

- Producer retained gate session `75016`, shell PID `21627`, pytest uv PID
  `21654`: `286 passed in 1493.76s`; Ruff, mypy, Bandit, import-linter and
  local-only checks passed.
- Fresh independent boundary harness
  `/private/tmp/w04-r10-review-boundary.py`, SHA-256
  `d1fdd0e4d85a9f50d0d67b2021ac84a435708d949bc111e9d6d805f5d33ad60d`,
  passed 41 distinct rejection attacks plus positive transport, identity,
  inverse, build-formula, logical-byte, and source-order proofs.
- Independent authoritative gate session `45530`, shell PID `76704`, pytest uv
  PID `76731`: `286 passed in 1494.82s`; all named static/security/import/local
  checks passed. Decision: **PASS**, `P0/P1/P2 = 0/0/0`.
- The review's first boundary harness omitted its review-local import path and
  exited before importing producer code. Its first full-gate shell then exported
  an empty noncanonical temporary `UV_CACHE_DIR`; retained session `43103`
  completed `246 passed, 40 failed in 1443.64s`. Every traceback was the absent
  temporary archive or sandbox denial of the accepted local cache. Both events
  are retained reviewer-harness procedural rework, not producer findings. Fresh
  inventories were unchanged, and the corrected fresh authoritative run passed.

## Fresh master reproduction

The master independently ran retained session `2919`, gate shell PID `94433`,
pytest uv PID `3808`, Python worker PID `3809`. The initial sandboxed boundary-
audit command was denied read access to the already admitted local uv-cache
`.git` entry and performed no audit; the approved read-only locked/offline rerun
passed. No network, dependency, lock, PYC, product, manifest, data, run, staging,
or publication mutation occurred.

| Master check | Result |
| --- | --- |
| `uv sync --locked --all-groups --offline` | exit `0`; `83` resolved, `82` audited |
| independent master boundary audit | exit `0`; exact roster/model order, positive/inverse/bytes, subclass and semantic attacks passed |
| Ruff format/check | exit `0`; two candidate files formatted and lint-clean |
| mypy | exit `0`; no issues in two candidate files |
| exact six-file pytest population | exit `0`; `286 passed in 1508.71s` |
| Bandit over admission/launcher/rebuild | exit `0`; no findings |
| import-linter | exit `0`; `3 kept, 0 broken` |
| local Git guard | exit `0`; executable pre-push guard simulated exit `1` |
| local-only verifier | exit `0`; 25 checks, zero failures, `main`, zero remotes |
| W04 phase verifier, pending checkpoint | exit `0`; READY, all declared gates PASS |
| `git diff --check` | exit `0`; empty output |
| `git remote` | exit `0`; empty output |

Every Python-backed master command used locked/no-sync offline uv,
`PYTHONDONTWRITEBYTECODE=1`, `python -B` where applicable, disabled pytest cache
output, and cache prefixes outside the repository.

## Master retained-root and PYC postflight

The complete master pre/post inventories were byte-identical:

- complete `data/**` and `runs/**`: `81` rows, SHA-256
  `e62878d96c76cc67a0fc0690fed674c1c61c2b82981a472b21649ffd981a686b`;
- selected site-packages: `1,087` PYC files plus `131` cache directories,
  `1,218` rows, SHA-256
  `ad6397ba9131fc7684bf9dbfdef4e3ae69ef9a7d9662f561948bef16868f835e`;
- repository excluding `.venv`: `111` PYC files plus `21` cache directories,
  `132` rows, SHA-256
  `9b1407d4f9d5adae170014b9a4852bc1e62331efd57c99d04e69df14ac8719a2`.

The retained failed-attempt manifest and all control/admission/rebuild prefixes
remain present and unchanged. Nothing was deleted, restored, rewritten, stashed,
reset, cleaned, published, or retried during acceptance.

## Residual and disposition

The accepted R9 PYC residual is unchanged: a hypothetical replace-and-restore
event preserving every Python-observed metadata field between shell inventory
endpoints remains outside Python authority. Complete shell header/hash inventories
bind both endpoints, and unconditional Python PYC denial remains controlling.

The next accepted code manifest and build ID will change mechanically because the
R10 rebuild source and security-test bytes are content-addressed. The pre-R10
manifest remains retained as explicitly unaccepted failed-attempt evidence. This
does not change the logical model or any digest meaning/formula.

R10 is **MASTER_ACCEPTED**. The corrected master-owned real-root packet may now
execute exactly two new complete invocations while preserving every failed-attempt
artifact.
