# Subagent return

## Task

- task_id: `W04-SCHEMA-DESIGN-REVIEW-01-R10`
- objective: Independently challenge the complete standalone R16 W04 schema and
  deterministic rebuild design, reproduce the corrected logical-launch to
  physical-uv authority and all other material claims, and accept only when all
  P0-P2 concerns are closed.

## Files changed

- `reports/reviews/W04/wyscout-schema-design-independent-review-R10.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-REVIEW-01-R10.md`

## Summary

- Decision: **REWORK**.
- Reproduced the R16 correction: normal literal `uv` resolution selects
  `/opt/homebrew/bin/uv`; its exact 26-byte raw symlink target takes one contained
  hop to the admitted physical uv 0.9.21 bytes; outer 29 and both child 32 maps
  retain the logical `UV`; direct physical execution produces the forbidden
  Cellar spelling.
- Found P1-01: invariant 7 forbids host paths in stable environment identity, but
  R16 explicitly places the absolute logical and physical Homebrew paths into the
  stable target record, code/environment manifest, component digests,
  code-manifest identity, and build-ID preimage.
- Found P1-02: despite its standalone replacement claim, R16 only names and
  high-level-describes the first field-semantics decision/registry/review/
  acceptance route. It omits the exact closed artifact schemas, ID/digest
  algorithms, canonicalization, clock/equality bindings, dependency construction,
  and exact task ownership needed to implement or independently verify rows 2–4
  without superseded prose or invention.
- Mechanically reproduced the 25/25 projection/invocation schemas, exactly 24
  common values, projection-only `schema_version`, invocation-only `build_id`,
  and unique 16/8/10/25 child/rebuild input cardinalities.
- Reproduced the accepted five-field `EvidenceDependency`, enum order, canonical
  JSON, and rejection of all three report-local aliases.
- Rechecked locked/no-sync no-site behavior, inherited descriptor preservation,
  Packaging 26.2 bootstrap basis, exact three `.pth` files, selected
  `L == I == 82`, 35 executable rows/21 owners/33 E/1 P/1 W, all three
  interpreter aliases, 1,075 site pycs, 58 repository pycs in 19 caches, three
  present source-absent repository orphans, 18 source rows, and 17 resources.
- Read back and challenged source/rights, record-kind envelope authority,
  identity, possession, supported features, product keys, serializers, separate
  source/Gold coverage, strict temporal rules, quarantine, publication, writers,
  gate, two-root, and two-local-commit ledger. No other P0-P2 defect was found.
- No candidate correction or implementation was performed.

## Tests run

- command: complete R15-to-R16 textual delta plus full R16 readback
  - exit status: `0`
  - result: PASS for correction scope and retained text; the two independent P1
    design findings remain.
- command: logical uv `command -v`/`lstat`/`readlink`/one-hop/stat/hash/version
  probes
  - exit status: `0`
  - result: PASS; exact logical link, raw 26-byte target, one contained hop, final
    regular `0o555`/41,617,552-byte file, admitted SHA-256, and uv 0.9.21 version.
- command: complete outer and two child closed `env -i` locked/no-sync probes
  - exit status: `0`
  - result: PASS; exact 29/32/32 counts, depth `1`, one venv prefix, and logical
    `UV=/opt/homebrew/bin/uv` in all three roles.
- command: direct physical uv exec-target negative control
  - exit status: `0`
  - result: PASS as rejection evidence; actual `UV` became the forbidden physical
    Cellar path.
- command: mechanical R16 projection, invocation, and child input table parser
  - exit status: `0`
  - result: PASS; unique 25/25 with 24 common keys, correct exclusive keys, plus
    unique 16/8/10 input cardinalities.
- command: `EvidenceDependency` JSON/model probe
  - exit status: `0`
  - result: PASS; exact five fields and enum order; `dependency_kind`,
    `manifest_id`, and `manifest_sha256` rejected.
- command: exact locked/no-sync `python -S -B` no-site and inherited-FD probes
  - exit status: `0`
  - result: PASS; site absent, no-site/bytecode flags active, descriptor regular
    and offset-zero/inheritable/`FD_CLOEXEC` clear through uv.
- command: lock/install, Packaging, `.pth`, executable RECORD/entry-point,
  interpreter-alias, and pyc inspections
  - exit status: `0`
  - result: PASS; selected/installed 82/82, Packaging 26.2, three `.pth`, 35
    rows/21 owners/33 E/1 P/1 W, three aliases, 1,075 site pycs, and 58 repository
    pycs in 19 caches with the three exact source-absent repository orphans.
- command: source completion/profile digests and R16 source/resource readback
  - exit status: `0`
  - result: PASS; completion/profile digests match, 18 source rows and 17 local
    resources retained.
- command: `uv run --locked --no-sync python -c "from pathlib import Path; p=Path('reports/reviews/W04/wyscout-schema-design-independent-review-R10.md'); assert p.is_file() and p.stat().st_size > 15000"`
  - exit status: `0`
  - result: PASS; the independent review is 33,579 bytes.
- command: `uv run --locked --no-sync python scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS; 25 checks, zero failures, zero configured remotes, active local
    push guard, one root uv project, Python 3.12.12, no hosted CI/deployment,
    container definition, or external-service dependency.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-schema-design-independent-review-R10.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-REVIEW-01-R10.md`
- `reports/reviews/W04/wyscout-schema-design-R16.md`
- `reports/reviews/W04/wyscout-schema-design-R15.md`
- `reports/verification/W04/wyscout-schema-design-R16-master-verification.md`
- `src/scouting/contracts/evidence.py`
- `reports/phase-gates/W04/source-schema-profile.md`
- current local uv, venv metadata, installed RECORD/entry-point, executable,
  interpreter, encoding-source, and bytecode evidence read in place

## Risks

- P1: the stable code/environment and build identity cannot simultaneously
  include the two absolute uv host paths and satisfy invariant 7's host-path ban.
- P1: the first field-semantics authority cannot be implemented or independently
  verified from R16 alone without importing superseded rules or inventing exact
  artifact, digest, clock, and ownership contracts.
- Both corrections are bounded to the standalone design and do not require
  provider, rights, dependency, lock, network, cloud, deployment, architecture,
  storage-root, Git, or local-only changes.

## Follow-up items

- Dispatch standalone R17 to close both P1 findings, then repeat master and
  independent review before any W04 implementation packet.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
