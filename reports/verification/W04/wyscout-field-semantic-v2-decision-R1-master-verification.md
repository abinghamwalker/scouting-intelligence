# W04 field semantic v2 decision R1 — master rework verification

## Decision

`REWORK`. The producer correctly stopped, but R1 created two draft artifacts
outside the packet's project-root ownership. No R1 implementation is accepted.

## Defect

Relative patch paths resolved against:

```text
/Users/adrian/Documents/personal_repos/investigation_v2
```

instead of:

```text
/Users/adrian/Documents/personal_repos/investigation_v2/scouting-intelligence
```

The exact accidental artifacts were:

```text
reports/reviews/W04/authorities/wyscout-field-semantic-decisions-v2.json
bytes: 66640
lines: 1
SHA-256:
9c2e75de3050736b722983d950492a97076ef28c7ef7da2825a08bc726680ed0

configs/schema/wyscout-v5-field-registry-v2.yaml
bytes: 66221
lines: 1365
SHA-256:
4943f5be9ac5a640c185536fcfc0191bcb277b8df4dbc6d08e819cd91791f41c
```

All intended in-repository output paths remained absent. No focused test,
return, terminal inventory, review, acceptance, possession, feature,
cross-authority, product, Git, dependency, network, cloud, container,
endpoint, hosted-CI, or deployment action followed the defect.

## Preservation and cleanup

The master first enumerated both accidental directory trees and confirmed they
contained only the two files above. Every directory in both chains had the same
creation/mtime epoch as the files. The master then moved the exact files,
without rewriting them, to:

```text
/private/tmp/W04-FIELD-SEMANTIC-V2-DECISION-01-R1-accidental/
```

Their hashes remain unchanged there. The now-empty accidental directory chains
were removed with explicit `rmdir` calls. Parent-workspace `reports` and
`configs` are absent again. No unrelated user-owned work was touched.

## Rework boundary

R2 must use absolute project-root patch paths, recreate all four required
outputs under `scouting-intelligence`, and rerun the complete bounded packet.
No R21 semantic, architectural, dependency, storage, rights, local-only, or
product decision changes.
