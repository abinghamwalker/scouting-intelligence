# W04 Wyscout schema design R18 — master verification

## Decision

`ACCEPT` as the corrected master candidate for independent review. The master
read all 4,260 R18 design lines, the complete 89-line return, and the complete
252-line R17-to-R18 delta after a fresh locked all-groups sync. R18 closes all
three master-reproduced R17 defects without changing the accepted architecture
or the previously passing launch/build authority. Implementation and provider
acquisition remain blocked pending separate independent acceptance and master
reproduction of that verdict.

## Integrity and scope

- R18 design: `228,182` bytes; SHA-256
  `d6f81a663a6e7db46e1059f2fee11521f0afde81a79cca3ec9d003d5954f8396`.
- R18 return: `4,204` bytes; SHA-256
  `1120c272130966ede848f3e6b50c3ecb57c52353cc8ccdad586eac7a5c0574f3`.
- R17 remains unchanged at SHA-256
  `f8dcfead8bef0fa36719e643f5c3d61f116b361603ca2d3d4af7e46848e16195`.
- Master base: `8eab3d5488735379817800be4b463f046f5d6e69`.
- Producer ownership remained limited to the two exact R18 report paths.
- The parent-workspace report hierarchy and all three future implementation
  scripts remain absent.

## Closed R17 defects

The common semantic-authority protocol now uses the existing repository
contract exactly:

```text
ActorId = StrictUuid
```

The master constructively reproduced that Pydantic rejects `"master.agent"` and
accepts canonical UUID JSON as `uuid.UUID`. Every FIELD, POSSESSION,
SUPPORTED_FEATURE, and IDENTITY actor is covered by the common strict-UUID rule,
with accepted-by/decided-by equality and independent-reviewer distinctness
retained.

The possession predicate row parses to exactly 12 fields:

```text
closes_control
contested_attachment
control_team_source
dead_ball_attachment
decided_by
decision
event_id
forbidden_tag_ids
opens_control
rationale
required_tag_ids
subevent_id
```

The complete union has exactly `CONTROL`, `RESTART`, `DEAD_BALL`, `CONTESTED`,
`NON_CONTROL_ADMIN`, and `UNMAPPED`. Every field is required; row actors equal
the top-level decision actor; `UNMAPPED` has explicit control, attachment,
rationale, and actor values; taxonomy rows must be canonical byte-for-byte
restatements; and missing/defaulted/invalid combinations fail closed.

The field decision packet now owns only the approved contract-test path
`tests/contracts/test_wyscout_field_registry_authority.py`. The unauthorized
alternate is absent.

## Retained standalone and build closures

The normative field roster is byte-for-byte equal to the accepted profile's
measured tables in the same order: 119 unique pairs across
`10/11/26/47/18/4/3`.

R17 and R18 Sections 8 and 9 are byte-identical. Stable versions remain
`w04-local-control-bootstrap-v4`,
`w04-outer-environment-bootstrap-v2`,
`w04-child-environment-input-v2`, and
`w04-code-environment-admission-v14`. Exact schema cardinalities remain
`16/8/10/25/25/20`. The invocation and stable projection share 24 keys and
differ only by invocation `build_id` versus projection `schema_version`.

The exact H1/H2 host-spelling perturbation still requires equality of normalized
environment authority, `environment_digest`, canonical code-manifest bytes and
digest, projection bytes, and `build_id`. Actual uv paths remain operational
only; the exact current-host admission remains fail-closed.

## Checks

- Fresh `uv sync --locked --all-groups`: PASS; 83 resolved, 82 audited.
- Complete design/return/delta readback: PASS; 4,260/89/252 lines.
- Artifact size/digest reproduction: PASS.
- Profile/roster equality: PASS; exact ordered 119 pairs and
  10/11/26/47/18/4/3 counts.
- Existing `ActorId` contract: PASS; canonical UUID accepted, arbitrary ASCII
  rejected.
- Possession row/union: PASS; 12 exact fields, six exact decisions, explicit
  `UNMAPPED`, row/top-level actor equality, and fail-closed tests.
- Field contract-test ownership: PASS; approved path only.
- Stable launch/build body: PASS; R17/R18 Sections 8 and 9 byte-identical.
- Projection acyclicity: PASS; 25/25 keys, 24 common, exact one-key
  substitution.
- Versions/schema cardinalities: PASS; v4/v2/v2/v14 and
  16/8/10/25/25/20.
- Host-spelling perturbation: PASS; all five downstream identity equalities
  retained.
- Orchestration/config YAML before this review: PASS; 141 plus 5 documents, 23
  registry tasks, zero duplicate registry task IDs.
- Local-only verification: PASS; 25 checks, zero failures.
- `git diff --check`: PASS.
- `git remote`: PASS; empty.

No provider acquisition or network access occurred. No product implementation,
cloud resource, hosted CI, public endpoint, Git remote, container, or deployment
was created.
