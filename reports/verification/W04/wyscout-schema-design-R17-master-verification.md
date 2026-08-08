# W04 Wyscout schema design R17 — master verification

## Decision

`REWORK`. The master read all 4,177 R17 design lines, the complete 53-line
return, and the complete 1,412-line R16-to-R17 delta after a fresh locked
all-groups sync. R17 correctly closes the independent R10 host-path and
standalone-authority findings, but it introduces three regressions against
existing contract and approved design authority. The correction is bounded and
does not change the approved architecture.

## Integrity and scope

- R17 design: `223,111` bytes; SHA-256
  `f8dcfead8bef0fa36719e643f5c3d61f116b361603ca2d3d4af7e46848e16195`.
- R17 return: `3,851` bytes; SHA-256
  `e2885f32c9fd22fb06272538c5f048293cb01ff019b30b6d8ca88d24b3bb41a4`.
- Master base: `8eab3d5488735379817800be4b463f046f5d6e69`.
- Producer ownership remained limited to the two exact R17 report paths.
- The parent-workspace report hierarchy and all three future implementation
  scripts remain absent.

## Reproduced P1 — ActorId contract conflict

R17 line 305 redefines every actor as an arbitrary NFC ASCII identifier matching
`[A-Za-z0-9][A-Za-z0-9._:@/-]{0,127}`. The existing authoritative contract at
`src/scouting/contracts/primitives.py` defines `ActorId = StrictUuid`.

The master constructively checked the current contract through Pydantic:
`"master.agent"` is rejected, while canonical UUID JSON is accepted and
materialises as `uuid.UUID`. R17 invariant 6 says existing contracts are
unchanged, so every decision, review, and acceptance actor must use the existing
strict UUID `ActorId`, with canonical lowercase UUID JSON spelling. Existing
actor equality and reviewer-distinctness rules remain required.

## Reproduced P1 — possession predicate closure regression

The retained R4/R5 design requires each non-`UNMAPPED` predicate to state
`control_team_source`, `opens_control`, `closes_control`,
`dead_ball_attachment`, `contested_attachment`, rationale, and accountable
`decided_by`.

R17's exact predicate row contains `control_team_source`, `opens_control`, and
rationale, but mechanically omits:

```text
closes_control
contested_attachment
dead_ball_attachment
decided_by
```

A global dead-ball policy is not a substitute for the required row-level
attachment decision. R18 must restore the complete row schema, define exact
literal/null behavior for `UNMAPPED`, bind each row actor to the top-level
decision actor, and reject inconsistent combinations.

## Reproduced P2 — field contract-test ownership path

The approved R4/R5 packet ownership freezes:

```text
tests/contracts/test_wyscout_field_registry_authority.py
```

R17 removes that path and substitutes
`tests/contracts/test_w04_field_semantic_authority.py`. No path change was
approved. R18 must restore the frozen path everywhere and eliminate the
alternate.

## Passing R17 closures retained

R17 correctly classifies the actual logical uv path, physical path, and raw link
target as operational evidence only. Stable identity uses root-independent
tokens, roles, relationship policy, and admitted executable bytes. The H1/H2
host-spelling perturbation leaves normalized environment bytes,
`environment_digest`, code-manifest bytes/digest, projection bytes, and
`build_id` equal.

The master also reproduced:

- exactly 119 field pairs in accepted profile order, with counts
  `10/11/26/47/18/4/3`;
- schema versions `v4/v2/v2/v14`;
- exact schema cardinalities `16/8/10/25/25/20`;
- a 25-key projection and invocation with their retained 24-key intersection;
- local-only verification with 25 passing checks; and
- no remote, provider acquisition, implementation entry point, parent report
  hierarchy, cloud resource, hosted CI, public endpoint, container, or
  deployment.

## Checks

- Fresh `uv sync --locked --all-groups`: PASS; 83 resolved, 82 audited.
- Complete design/return/delta readback: PASS; 4,177/53/1,412 lines.
- Artifact size/digest reproduction: PASS.
- Existing `ActorId` reproduction: FAIL as review evidence; R17 conflicts with
  the strict UUID contract.
- Possession predicate schema comparison: FAIL as review evidence; four required
  row fields are missing.
- Field test ownership comparison: FAIL as review evidence; the approved path is
  absent and an unauthorized alternate is present.
- Stable uv host-spelling exclusion and perturbation proof: PASS.
- Accepted field roster: PASS; 119 total across 10/11/26/47/18/4/3.
- Schema cardinalities: PASS; 16/8/10/25/25/20.
- Orchestration/config YAML before this review: PASS; 139 plus 5 documents, 23
  registry tasks, zero duplicate registry task IDs.
- Local-only verification: PASS; 25 checks, zero failures.
- `git diff --check`: PASS.
- `git remote`: PASS; empty.

No provider acquisition or network access occurred. No product implementation,
cloud resource, hosted CI, public endpoint, Git remote, container, or deployment
was created.
