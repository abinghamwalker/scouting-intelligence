# W04 Wyscout runtime-control independent review R10

Date: 2026-08-03

## Decision

**PASS.** Findings are `P0=0`, `P1=0`, `P2=0`.

R10 closes the retained first-real-root canonical-JSON tuple reconstruction
failure without changing a logical field, value, key order, product population,
projection/invocation inverse, build-ID formula, digest meaning, dependency,
runtime-control predicate, or local-only boundary. The child accepts only the
exact ordered 25-key built-in JSON object and exact built-in JSON arrays for the
two declared tuple fields, reconstructs only those outer arrays as tuples, and
then invokes strict `RebuildInvocation` validation before publication-root
construction or any product, manifest, or receipt writer.

The exact required six-file population passed `286` tests. All named static,
security, import-boundary, and local-only checks passed. Fresh shell-only PYC
and complete `data/**`/`runs/**` pre/post inventories are byte-identical.

## Frozen bindings and read-only chain of custody

Every fixed binding matched before merits work and again after the complete
gate:

| Binding | Independently observed SHA-256 |
| --- | --- |
| R10 review packet | `4a52523b41263f115de8195b55feb5b60ff8001a63050458b10469bc56e5c8bb` |
| R10 producer packet | `d6c0872b86928dc1a53ed0476f26be7ae9ace500bdaae3e25c8a535e5356748f` |
| prior accepted rebuild child | `82d7a22cc9d48bca19e0f4a6d05f60995f7486df829585fa7bf0b9ab7434ba99` |
| candidate rebuild child | `fff279d4d4a6a1c76ea6ee2cc9c7a88a4d5fd2c56ca677984a1dcce765ef9339` |
| candidate security tests | `5907b945fa61855ff1104a2e03dd13057a76863251258b8a53088e322b44d18d` |
| producer return | `56004852a1868b89579d65ee781b5ef9a26b922451f25dbbe61f1b94aaa55854` |
| R9 admission child | `f6dbce7ffd48320155ab0562ef27a4f79c99e80aa1b122e5f0b039c493048f05` |
| R9 launcher | `6211ff1cd0b51bdd3ab24fe26358077f46f1ad0526ff60126776606ca01243eb` |
| R9 runtime-control tests | `12924b9905a8334c4a6f83bb00b170059be0bb965a1d3d6b4f0c09d364a95abf` |
| R9 master acceptance | `b120ad2b0c942d939cef10b8a914187c85b1a2647ac37c328296c1152fe4d618` |
| retained unaccepted code manifest | `fb1bcca5772d71a0de2c116cd2539d1d2cd757554df8791dad8e0d952cf67083` |
| retained complete `data/**` and `runs/**` census | `e62878d96c76cc67a0fc0690fed674c1c61c2b82981a472b21649ffd981a686b` |
| disclosed launcher PYC | `b1c8fbd8e5de10d6251995b9dc0fbbcb7457ba0bdaffd669e6e58c86d280b52e` |
| shell PYC census helper | `2702b38453c95e428e9289cfc0bd6a9d0f1a748aeb33f1bad1e1c7033eaf4a6d` |

The prior rebuild digest remains bound by the accepted vertical-slice evidence
and the R10 packet; it is the replaced source authority, not a second current
file. The candidate source is the sole current rebuild child and has the exact
candidate digest above.

No producer, source, test, contract, dependency, lock, PYC, product, manifest,
receipt, staging, real-root, data, run, configuration, or orchestration byte was
edited by this review. Only this review and its mandatory return were written in
the repository. Review harnesses, caches, and inventories remained under
`/private/tmp` or `/tmp`.

## Exact reconstruction boundary

The candidate child declares the exact ordered 25-key roster at
`scripts/rebuild_wyscout_v5.py:32`. `_reconstruct_rebuild_invocation_json` at
line 61 requires `type(value) is dict`, exact key order equality, and exact
built-in `list` instances for `authority_rows` and `dependency_rows`. It builds
a new dict in the frozen roster order. Only the two outer arrays become tuples;
every nested row object and each of the other 23 values is reused by identity.
The input object is neither mutated nor filtered, copied, sorted, defaulted, or
coerced.

The helper roster equals both `POST_HASH_INVOCATION_KEYS` and
`tuple(RebuildInvocation.model_fields)`. The accepted transport round trip uses
the same `admission._decode_input` canonical base64url/JSON decoder called by
the child. It produces exact built-in containers, reconstructs five ordered
authority rows and five ordered dependency rows, and validates with
`RebuildInvocation.model_validate(..., strict=True)`.

The validated invocation equals the accepted value. Both
`projection_from_invocation` and `invocation_from_projection` reproduce their
strict inverses; SHA-256 of the canonical pre-build projection equals the sole
`build_id`; and the validated invocation's canonical logical JSON bytes equal
the original pre-reconstruction bytes exactly.

## Independent adversarial merits

The final independent harness is
`/tmp/w04-r10-review-boundary.py`, SHA-256
`d1fdd0e4d85a9f50d0d67b2021ac84a435708d949bc111e9d6d805f5d33ad60d`.
It passed 41 distinct rejection attacks plus the positive transport,
identity/inverse, and source-order proofs:

- top-level null, list, tuple, string, integer, boolean, and dict-subclass
  substitutions;
- a tuple, dict, string, integer, null, or list subclass in either individual
  declared tuple field while the other field remains a built-in JSON list;
- one missing key, one extra key, and one reordered exact key roster;
- add, remove, reorder, digest/value mutation, and whole-row type mutation for
  each of the authority and dependency populations;
- nested extra authority data, nested mistyped dependency data, top-level type
  drift, invalid build identity, code-manifest identity substitution,
  placeholder product/schema digests, tenant type drift, and window drift.

Every structural container attack fails in the reconstruction helper. Every
semantic attack reaches strict Pydantic validation and fails there. The
positive case proves a new ordered dict, exact preservation of all other object
identities, exact preservation of every nested row identity, and no mutation of
the decoded input.

An AST/source trace proves the call order in `run_rebuild`: transport decode and
input validation, reconstruction at line 361, strict model validation at line
362, explicit enclosing build equality at lines 363-366, publication-root
construction at line 367, and the sole rebuild writer beginning at line 401.
The strict call has literal `strict=True`; validation exceptions are not caught
inside `run_rebuild`. Thus every attacked invocation rejects before
`_publication_roots` and every product, layer-manifest, boundary-receipt, and
rebuild-receipt write.

The producer's direct tests at
`tests/security/test_w04_wyscout_vertical_slice_publication.py:134` retain the
same positive logical-byte/inverse proof and the bounded missing, extra,
reordered, tuple, non-array, row-order/cardinality/value, nested, and top-level
rejection cases. The complete gate retained every R9 runtime-control test.

## Gate evidence

| Command/evidence | Exit | Result |
| --- | ---: | --- |
| locked/no-sync Ruff format check over candidate child/security tests | 0 | `2 files already formatted` |
| locked/no-sync Ruff check with cache disabled | 0 | `All checks passed!` |
| locked/no-sync mypy with review-only cache | 0 | no issues in two source files |
| final independent canonical-boundary harness | 0 | 41 rejection attacks plus all positive proofs passed |
| exact required six-file pytest population, retained session `45530`, shell PID `76704`, pytest uv PID `76731` | 0 | `286 passed in 1494.82s (0:24:54)` |
| locked/no-sync Bandit over admission, launcher, and rebuild child | 0 | no findings |
| locked/no-sync import-linter with cache disabled | 0 | `3 kept, 0 broken` |
| locked/no-sync local-only verifier | 0 | PASS, 25 checks, zero failures, `main`, zero remotes |
| complete shell PYC and retained-root preflight/postflight | 0 | all three inventory pairs byte-identical |
| final fixed-binding SHA-256 recheck | 0 | every binding exact |

Every Python-backed successful merits command used locked/no-sync offline uv,
`PYTHONDONTWRITEBYTECODE=1`, `python -B` where applicable, disabled pytest cache
output, and review-only cache prefixes. The exact gate used read-only access to
the already admitted local uv cache; network access remained disabled.

The packet also lists direct `git diff --check` and `git remote`, while governing
subagent authority and the master instruction prohibit this reviewer from
running Git commands. No direct Git command was run. The local-only verifier
performed its embedded read-only branch, remote, and guard checks and reported
`main`, zero configured remotes, and all 25 checks passing. Direct Git evidence
remains master-owned.

## Shell-only PYC and retained-root closure

The final shell-only inventories were byte-identical before and after the
successful harness and complete gate:

- selected site-packages: `1,087` PYC files plus `131` cache directories,
  `1,218` rows, SHA-256
  `ad6397ba9131fc7684bf9dbfdef4e3ae69ef9a7d9662f561948bef16868f835e`;
- repository excluding `.venv`: `111` PYC files plus `21` cache directories,
  `132` rows, SHA-256
  `9b1407d4f9d5adae170014b9a4852bc1e62331efd57c99d04e69df14ac8719a2`;
- complete `data/**` and `runs/**`: `81` rows, SHA-256
  `e62878d96c76cc67a0fc0690fed674c1c61c2b82981a472b21649ffd981a686b`.

All three final `cmp` operations returned zero. The disclosed launcher PYC
remained the frozen row and digest above. Python did not read its bytes; the
complete byte/header/hash authority remained exclusively in shell inventories.
The retained failed-attempt code manifest and every control, admission, rebuild,
staging, product, manifest, receipt, data, and run artifact remained read-only.

## Review-harness procedural rework

The first `/tmp` boundary harness omitted the repository root from `sys.path`
and exited before importing the reviewed module. Adding only that review-local
path bootstrap produced the final harness above, which passed under the accepted
environment and changed no repository byte.

The first full-gate shell, SHA-256
`89e82c077fb972eddc7a525c1df2937838096461b3325e5e293467a7b401cb03`,
incorrectly exported `UV_CACHE_DIR=/tmp/w04-r10-review-gate-uv`. Retained
session `43103` (shell PID `50667`, pytest uv PID `50706`) completed with
`246 passed, 40 failed in 1443.64s`. Every traceback was either the absent
noncanonical `/tmp` cache archive or sandbox denial while an exact-uv subprocess
attempted the accepted `/Users/adrian/.cache/uv` path. No failure reached an R10
producer predicate.

This was bounded reviewer-harness procedural rework, not a producer finding.
Fresh postflight inventories after that failed attempt were byte-identical to
its preflight. A new preflight then opened a separate evidence window. The
corrected gate shell, SHA-256
`ee07ea9a08e25333b95fa101a8b5b9d17be25950e6f335b401b96a919796de5e`,
removed the cache override, used locked/no-sync offline uv with read-only local-
cache access, and passed the complete gate in fresh session `45530`.

## Residual risk and disposition

The future accepted code manifest and build ID will mechanically change when
derived from the corrected rebuild-child source. R10 intentionally preserves
the retained unaccepted prior manifest and performs no derivation, cleanup,
publication, or real-root retry. This is an expected consequence of source-byte
identity, not a logical or digest-formula change.

The accepted operational PYC residual is unchanged from R9: a hypothetical
replace-and-restore event preserving every Python-observed metadata field
between shell inventory endpoints remains outside Python authority. Complete
shell header/hash inventories bind both endpoints, and unconditional Python PYC
denial remains controlling.

No P0, P1, or P2 defect remains in the reviewed R10 canonical-JSON tuple
reconstruction, strict invocation validation, inverse/build binding, tests,
retained evidence, or local-only gate.

Decision: **PASS — `P0/P1/P2 = 0/0/0`.**
