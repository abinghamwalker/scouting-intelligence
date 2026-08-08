# W04 Wyscout schema design R19 — master verification

## Decision

`ACCEPT` as the corrected master candidate for a fresh independent merits
review. R19 preserves R18's accepted semantic and stable launch/build authority,
truthfully records the reviewer-created operational bytecode state, replaces
future hardcoded pyc cardinality with an exact per-run preflight/postflight
identity rule, and closes the independent-review no-write harness.

The master read the complete 98-line return and complete 286-line R18-to-R19
delta and evaluated every changed line against the already completely read
4,260-line R18 candidate. Implementation and provider acquisition remain blocked
pending independent R12 acceptance and master reproduction.

## Integrity and scope

- R19 design: 4,357 lines, `236,602` bytes; SHA-256
  `8792db725eb65265b6a68ed56ed0d5bae1f20d1704faa8925baeeba29db10ec7`.
- R19 return: 98 lines, `5,063` bytes; SHA-256
  `2cf151294f4530e2b15e7d9bb72aaa6e7541ad80d6bd073064930e475abef913`.
- R18 remains SHA-256
  `d6f81a663a6e7db46e1059f2fee11521f0afde81a79cca3ec9d003d5954f8396`.
- Master base: `8eab3d5488735379817800be4b463f046f5d6e69`.
- Producer ownership remained limited to the two exact R19 report paths.
- The parent-workspace report hierarchy and all three future implementation
  scripts remain absent.

## Truthful operational bytecode refresh

The master independently matched all eleven R19 incident rows to the preserved
filesystem state. Every path has the exact reported source sibling, byte size,
mode `0644`, link count one, CPython 3.12 magic `cb0d0d0a`, modification epoch
`1785412176`, and SHA-256. The files classify as mapped
`SITE_DISTRIBUTION_NORMAL` Packaging caches and grant no source, schema, semantic,
or stable build authority.

The current evidence decomposes exactly:

```text
site:       1,086 = 972 distribution normal
                    + 1 uv-bootstrap normal
                    + 112 pytest rewrite
                    + 1 optional-six orphan

repository: 58 in 19 cache directories
                    = 35 mapped normal
                    + 20 pytest rewrite
                    + 3 exact inert orphans
```

R19 removes all stale `1,075/962/961` claims. It correctly treats the snapshot
and later mapped-cache presence/count/path/bytes as operational. At every bounded
run, a shell-only preflight records the actual complete inventory; every file
must classify; the complete postflight must be byte-identical. Any write,
deletion, rename, metadata/content change, or unclassified file invalidates the
run, and cleanup cannot recover a pass.

## No-write master reproduction

Before any master Python helper, the master recorded:

```text
site count: 1086
site metadata inventory:
0424caf9281ece4665f090a4095454d29622d6eb748e65cbc0b21701f452a26c
site content inventory:
ea4e63c8e850193c8e7bd235575fe88d7389d902350dd38469737e8f41176bd8

repository count: 58
repository metadata inventory:
d948edffb4538de2936a188957cec504de1610bac06abf65eb1fea9a7a7946e3
repository content inventory:
39e0bf9c9e0570513cfb3fd707d10264326e546db6d7e9947999c440f77610eb
```

Every helper used locked/no-sync root uv with
`PYTHONDONTWRITEBYTECODE=1` and `python -B`; the standard-library-only incident
parser additionally used `-S`. Each helper asserted the no-write controls before
third-party imports. Postflight reproduced every count and digest above exactly.

## Retained R18 authority

The complete semantic body from Section 2 through the start of the operational
site-census refresh is byte-identical between R18 and R19. The complete stable
body from Section 8.7 through Section 9 is also byte-identical. The R19 delta
otherwise changes only introduction/traceability, operational census and incident
evidence, review harness, health/test wording, future-script revision labels, and
the final disposition.

The master constructively reproduced:

- exact accepted-profile equality for 119 ordered pairs with
  `10/11/26/47/18/4/3` counts;
- existing strict UUID `ActorId`, with arbitrary ASCII rejected;
- exactly 12 possession predicate fields and six closed decision combinations;
- only the approved field contract-test path;
- stable versions v4/v2/v2/v14;
- exact cardinalities 16/8/10/25/25/20 and the retained acyclic projection;
- valid orchestration/config YAML and unique registry task IDs;
- local-only 25/25; and
- empty Git remote output.

## Checks

- Fresh counted `uv sync --locked --all-groups`: PASS; 83 resolved, 82 audited,
  1,086/58 unchanged.
- Complete R19 return/delta readback: PASS; 98/286 lines.
- R19 artifact size/digest: PASS.
- Eleven incident rows: PASS; exact path/source/size/mode/link/magic/mtime/digest.
- Stale operational counts: PASS; absent.
- Dynamic preflight/postflight and no-cleanup rule: PASS.
- Closed independent-review no-write harness: PASS.
- R18 semantic/stable section equality: PASS.
- Profile/actor/possession/path/version/cardinality closures: PASS.
- Complete pyc inventory postflight: PASS; exact count/metadata/content equality.
- Orchestration/config YAML before this review: PASS; 145 plus 5 documents, 23
  tasks, zero duplicate task IDs.
- Local-only verification with bytecode denial: PASS; 25/25.
- `git diff --check`: PASS.
- `git remote`: PASS; empty.

No provider acquisition or network access occurred. No product implementation,
cloud resource, hosted CI, public endpoint, Git remote, container, or deployment
was created.
