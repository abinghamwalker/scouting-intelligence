# Subagent return

## Task

- task_id: `W04-SCHEMA-DESIGN-01-R14`
- objective: Retain every accepted R13 closure while making the launcher
  environment/digest graph acyclic, closing both child input transports, and
  enforcing one manifest/build-ID/rebuild-prefix chronology.

## Files changed

- `reports/reviews/W04/wyscout-schema-design-R14.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R14.md`

## Summary

- Carried the complete R13 standalone design forward and retained its three-source
  encoding bootstrap, control prefix, inherited launcher/child descriptor model,
  honest same-trust-domain race residual, exhaustive `w04-child-result-v2`,
  unchanged outer/child argv, exact pyc/executable/alias/`.pth`/resource closures,
  and every earlier source-to-ledger contract.
- Defined `w04-outer-environment-bootstrap-v1`: the base digest excludes
  `W04_BOOTSTRAP_TUPLE_B64`, names the exact present map, exact required absences,
  nine operational substitutions, and the exact uv-input-to-Python transformation,
  then inserts one canonical completed `w04-local-control-bootstrap-v2` encoding.
  A separate operational digest covers the complete actual transport environment
  after insertion.
- Defined a closed child environment plus the sole value transport
  `W04_CHILD_INPUT_B64`. The canonical input contract has sixteen common keys,
  eight admission keys, ten rebuild keys, exact type/nullability/grammar/order
  rules, and fail-closed environment/envelope equality.
- Defined the closed twenty-five-key `w04-rebuild-invocation-v1`, including the
  immutable code-manifest identity, launcher-calculated build ID, run and prefix,
  four accepted authority rows, five strict dependency rows, stable schema/resource
  identities, exact receipt path, and ordered Bronze/Silver/Gold layer paths. The
  exact no-argument child argv remain unchanged; scanning, newest selection,
  generic config discovery, provider/resource acquisition, stdin, and argv value
  tokens remain forbidden.
- Replaced the conflicting chronology with one order everywhere: optional early
  UUID sampling; admission-prefix creation only; admission validation; immutable
  manifest write/confirm/readback; complete build-ID calculation; rebuild-prefix
  creation; rebuild envelope/environment construction; rebuild launch. Early
  prefixes, placeholders, and alternate orderings fail.
- Advanced the bound manifest/build-input algorithms to
  `w04-code-environment-admission-v11` and `w04-wyscout-build-id-v12` so the new
  stable input/environment construction is part of identity.

## Tests run

- command:
  `uv run --locked --no-sync python -c "from pathlib import Path; p=Path('reports/reviews/W04/wyscout-schema-design-R14.md'); assert p.is_file() and p.stat().st_size > 26000"`
  - exit status: `0`
  - result: PASS; the final design exists and is 169,853 bytes. The first
    sandboxed attempt exited `2` because the existing uv cache was outside the
    workspace read boundary; the identical approved rerun passed without sync or
    mutation.
- command: `uv run --locked --no-sync python scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS; validator status `PASS`, 25 checks passed, `failures: []`. The
    first sandboxed attempt exited `2` for the same uv-cache read restriction; the
    identical approved rerun passed.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-schema-design-R14.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R14.md`
- stable outer algorithm: `w04-outer-environment-bootstrap-v1`
- canonical child transport: `W04_CHILD_INPUT_B64` /
  `w04-child-input-v1`
- stable rebuild invocation: `w04-rebuild-invocation-v1`
- stable admitted-manifest algorithm: `w04-code-environment-admission-v11`
- stable build-input algorithm: `w04-wyscout-build-id-v12`

## Risks

- This is design evidence only. The three future scripts and their tests remain
  absent; feasibility and exact runtime observations still require the named
  implementation packets plus master and independent review.
- Complete actual outer/child transport-environment hashes, FD numbers, nonces,
  run IDs, absolute prefixes, and host paths remain operational evidence and are
  deliberately excluded from stable build identity.
- The same-trust-domain transient replacement residual accepted in R13 remains
  explicit and unchanged; R14 does not claim an unavailable stronger observation.

## Follow-up items

- Master and independent reviewer should verify the acyclic digest construction,
  exhaustive environment/input schemas, result/receipt/layer bindings, and unique
  chronology before accepting or dispatching implementation.

## Scope confirmation

- no Git operations: confirmed; no Git-mutating command or `.git/**` mutation was
  performed. The required local-only verifier made only its read-only Git checks.
- no unauthorised dependency or lockfile changes: confirmed; neither
  `pyproject.toml` nor `uv.lock` was modified, and both checks used
  `--locked --no-sync`.
- no edits outside `allowed_paths`: confirmed; exactly the two R14 report paths
  listed above were created/modified. No parent-workspace report path or directory
  was created, removed, or cleaned during R14.
