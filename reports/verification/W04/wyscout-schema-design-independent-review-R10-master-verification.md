# W04 Wyscout schema design independent review R10 — master verification

## Decision

`REWORK`. The master read the complete 776-line independent R10 review and
132-line return after a fresh locked all-groups sync, then independently
reproduced both P1 findings. R16's logical `uv` launch correction is sound, but
its stable/operational classification conflicts with its own host-path
invariant, and its claimed standalone authority design cannot yet drive the
first field-semantics packets without superseded prose or invention.

## Artifact integrity and scope

- Independent review: `33,579` bytes; SHA-256
  `41d484e17425ad5230c4c4f89e1f672b9ef1e915f453bfde8b9a0a658a42d811`.
- Return: `6,888` bytes; SHA-256
  `dc145d52c1ba88c8e5f44dbe0ab2be2f01ccc8f932af9d444d1ca89ad3a61518`.
- Master base: `8eab3d5488735379817800be4b463f046f5d6e69`.
- Reviewer ownership remained limited to the two exact R10 report paths.
- The three future implementation scripts and the parent-workspace report
  hierarchy remain absent.

## Reproduced P1-01 — stable absolute uv host paths

R16 invariant 7 forbids host paths from stable environment identity and semantic
proofs. The same document nevertheless puts both exact absolute values below
into its stable bootstrap/target/manifest authority:

```text
/opt/homebrew/bin/uv
/opt/homebrew/Cellar/uv/0.9.21/bin/uv
```

Those values transitively enter `local_launcher_control_digest`,
`process_launch_contract_digest`, `environment_digest`,
`code_manifest_sha256`, the stable pre-build projection, and `build_id`.
Normalizing only the `UV` environment-map value does not remove the separately
stable bootstrap and target-record paths. An implementer therefore cannot obey
both sides of R16.

The correction will preserve the exact actual current-host paths as operational
admission evidence. Stable identity will instead bind normalized path roles,
one-hop/symlink/containment policy, final executable class, exact uv
version/mode/size/bytes digest, and the deterministic normalization. A
host-spelling-only relocation with otherwise identical admitted authority must
not change stable environment, code-manifest, or build identity.

## Reproduced P1-02 — incomplete standalone semantic authority

R16 names four field-authority paths and the three high-level decisions, but it
does not contain the closed decision, registry, independent-review, or
acceptance schemas. Mechanical search confirmed the absence of the prior exact
contract markers, including the fixed decision ID, decision actor, unknown-kind
policy field, canonical-field row member, source-support row member, and
accepting actor.

The accepted profile mechanically contains exactly 119 measured record/path
pairs:

```text
competition:      10
team:             11
player:           26
match:            47
action:           18
event-taxonomy:    4
tag-taxonomy:      3
```

Without exact artifact keys/types, ID and digest preimages, canonicalization,
clock/dependency rules, cross-equalities, and packet owners, a field candidate
cannot prove exhaustive coverage and a reviewer cannot verify the intended
authority. The same standalone standard must be explicit for later possession,
identity, and supported-feature routes so the defect does not merely move to the
next required authority.

## Passing evidence retained

The master had already reproduced the R16 logical launch on the outer and both
child roles: exact 29/32/32 names, logical
`UV=/opt/homebrew/bin/uv`, recursion depth `1`, and exactly one venv prefix.
The exact symlink/raw target/one-hop/final physical bytes evidence also matches,
and direct physical execution remains forbidden. R10 found no other P0-P2
defect in the projection, dependency, descriptor/result, packaging, installed
closure, executable, alias, bytecode, source, rights, identity, product,
coverage, quarantine, publication, ownership, gate, two-root, or ledger design.

## Checks

- Fresh `uv sync --locked --all-groups`: PASS; 83 resolved, 82 audited.
- Complete review/return readback: PASS; 776/132 lines.
- Artifact size/digest reproduction: PASS.
- Stable host-path contradiction: FAIL as designed review evidence; two absolute
  uv paths are explicitly stable and transitive to build identity.
- Standalone field protocol: FAIL as designed review evidence; exact closed
  artifact and authority markers are absent.
- Accepted profile field enumeration: PASS; 119 total across 10/11/26/47/18/4/3.
- Local-only verification: PASS; 25 checks, zero failures.
- `git diff --check`: PASS.
- `git remote`: PASS; empty.

No provider acquisition, provider/network access, product implementation, cloud
resource, hosted CI, public endpoint, Git remote, container, or deployment was
created.
