# W04 Wyscout real-root invocation independent review R3

- Date: `2026-08-03`
- Task: `W04-WYSCOUT-REAL-ROOT-INVOCATION-REVIEW-01-R3`
- Reviewed producer task: `W04-WYSCOUT-REAL-ROOT-INVOCATION-01-R3`
- Decision: **PASS**
- Severity counts: **P0/P1/P2 = 0/0/0**

## Binding and scope closure

I read the complete packet-directed input set and independently verified every
fixed binding before adjudication. The corrected orchestration chain is exact:

- retained R2 packet:
  `207886a6c14bdb7415d96d532c073b1565d94f5188e8046a69f980f5619ac757`
- R3 producer packet:
  `836fdbf323a725adf11f24a47198a1789c37a9c2cb093465db71e10c72c6c831`
- R3 master acceptance:
  `738e9852e17b9a5233fa34373ede01805aff14383200f9b9c8c7ccb796aed63e`
- R3 producer return:
  `13687bb55cc6594cd432102f3f031ecfa714e51405e5a0df485ad4d5178f07a3`
- R3 review packet:
  `9b31cc19cf818606b5695b8cb968b490f5222fb5448fba2c4db4c4c8046a54cc`

The code and external readback artifacts also reproduce their frozen hashes:

- admission child:
  `f6dbce7ffd48320155ab0562ef27a4f79c99e80aa1b122e5f0b039c493048f05`
- launcher:
  `6211ff1cd0b51bdd3ab24fe26358077f46f1ad0526ff60126776606ca01243eb`
- rebuild child:
  `fff279d4d4a6a1c76ea6ee2cc9c7a88a4d5fd2c56ca677984a1dcce765ef9339`
- corrected wrapper:
  `e5b557790d02c41f457c683d59756509c48df2b15854c4c6d6914feec875d537`
- master readback:
  `760840e8113113db60c6228e6aacb90d0351bb7b5f0f793dd1002ece23b25e4b`

All producer, retained-root, code, product, manifest, receipt, and staging bytes
were kept read-only. Review caches and bytecode were directed outside the
repository with bytecode writing disabled. I performed no launch, cleanup,
dependency change, publication, producer edit, or Git operation.

## Independent wrapper and receipt adjudication

The corrected wrapper constructs the exact post-uv 30-key transport environment
from the unchanged accepted launch inputs. It includes the venv-prefixed `PATH`,
`UV_RUN_RECURSION_DEPTH=1`, the fresh control prefix, and the inherited source
descriptor, then compares only the returned dynamic transport digest to the
digest of those canonical JSON bytes. The pre-uv environment remains recursion
depth `0`; the normalized fixed environment authority remains independently
bound as
`d832fe0a0e8249465b1c77f135a5b8da07c100fee0586127cdf8a4099133eaf1`.
The accepted inherited launcher descriptor was independently located on file
descriptor `12` for both R3 launch families. No accepted command, launch input,
environment value, or digest formula changed.

Strict no-follow receipt readback reproduced all three successful families:

| Family | Rebuild receipt SHA-256 | Boundary receipt SHA-256 |
| --- | --- | --- |
| retained R2 | `a70a977f76f775e31f0ae3d9d7c28c51df99490733ebe76f20972107402d31cb` | `521581b50ca008a6c6e5ef6a7886018337ea904e896b85d9980d35a42f204f53` |
| R3 run 1 | `63b645423ca72edcb2055814293a0024d549bd01e45005136ff3730416530f10` | `a077a8a5385c633d1a6911717b843e2b7d60f5a6ac025136057ae810d9c595c2` |
| R3 run 2 | `db8501cf9c644644ca5ba614e87fea43d3d3c0568fcad405e028fb6d2ceace18` | `16488eb7ad9d6021e4f442455427a6c2d16e3db21a336a60f515cfbd5b08ab00` |

Each receipt has one exact canonical 25-key projection, strict
projection/invocation inverse, the fixed code manifest
`c94e650146a982174820ba694a2dcd1b20dc6648426527213bf2e6de09861c2c`,
and the sole build
`b1f1a9135e307b115fd1d00f19dae7951993765ee5ac1fb5d5afeb245fdc7b79`.
The R2 and two R3 run/boundary paths are distinct UUIDv4-scoped families. R2 is
correctly retained as core-complete/wrapper-unverified negative evidence and is
not counted as either of the two wrapper-verified R3 runs.

## Product, manifest, and Decimal closure

I independently reopened the three manifests and all seven Parquet products,
validated every field through the accepted root-owned descriptor, reconstructed
every physical row to canonical logical JSON bytes, and recomputed the physical,
semantic, and reconstructed logical-byte hashes.

| Product role | Rows | Physical SHA-256 | Semantic SHA-256 | Logical-byte SHA-256 |
| --- | ---: | --- | --- | --- |
| `BRONZE_KNOWN_RECORD` | 1768 | `e48b203df0d2b83d53af9340cc76ec42a0bb138b5e9608284718d9f6854e9aaf` | `4186f51a8694be1ca4699baf0f3c77e24b2206cc63f18bb7954074cc186d76ca` | `749e51f850372dfd610ffaf2037c8520e94282bca2eeac20f7ef582181cc7faa` |
| `BRONZE_REJECTED_FIELD` | 3544 | `b2dc4e9265edb79402b19b739be2167dd2bdcaea9afdf9c1b9304953d9f2278e` | `2d0d05c88e00aa2484215f691f9ce7233324e8f0dbd9ea98e86e16e385c08825` | `7f0a9a567ee81cbfe652422d09208679de8bc2a2f80a699b198a920c0d979384` |
| `SILVER_ACTION` | 13 | `89e9645d9715fc155f09a5dae14ac261233aa7599b8266cbcef6a0b5eb86f53a` | `9d98a59a82a45bf077e72dfdb26545d24f3e718d3c8266b085ec95a03bba22d3` | `e6d7e2d1abcd6cc4595b0453797ccd5bb22577c3ed384231eacc5aface27f3b9` |
| `SILVER_LINEUP_STINT` | 1 | `b05e1573cfee6cb3d2a44b675e72917dac70562af17e85494e2948934d15bda2` | `d5a83d1a820ec5197e18709b2ed966824c6edf836926cd8faddeab8617145c08` | `dbfb8c0befb5633d00191fd7680d90bd7af28c9df617ba1cc76442c2c0baac7b` |
| `SILVER_POSSESSION` | 2 | `a65461738eb21211cb9695af5bbdad9a28ea5f1280de2a3ae79559a555978878` | `bf1114a1d1b2b6325e3656aed297d5f3f7ec872b1485b47c65cb5c47a617417a` | `681f027ed5406f0e39b7c80bf25d5f093c64e111ef0df1fd62e4a717f30d9d5f` |
| `SILVER_PLAYER_MATCH_FACT` | 1 | `5b8bb0d0dcc1caf9709a1706041110ebadfd3ac14a590fefc4622cc5c41fa1da` | `a8db5735a2f0ec1ee37d46e9dc2985bb4d20b2ef08fc70acfc4e4eec38af5a0f` | `bd7c92d470bfb036a44057e014acd79d55aef4ed430086edb654e767327fb913` |
| `GOLD_PLAYER_WINDOW` | 1 | `6e49b4322c766352fdc427b8d35d73ddaed036d0bd19f1d65435fe3a72edcd17` | `f1751b4f1ff7911ad339fa1954cd5c88483fc09c733547dba87d7aa301c1bffa` | `ef6a57e33a9702f48496570a05fba7f70b7478eb25a30902b75bc9ad4b594cc6` |

The ordered row population is exactly `[1768, 3544, 13, 1, 2, 1, 1]`.
Physical schemas, uniqueness predicates, parent paths, temporal proof, and all
manifest entries passed. Layer manifests reproduce Bronze
`abdc5d89fdac08638f4877f9a44dceb9356d789741bd93981cce4a9b6825d9c1`,
Silver `089673ff01edd7de7b6e5777958d19cbaffaa9f429b042ab4986746d80a7c36a`,
and Gold `08de1349a532c3f455d792ee56aafc3d8c587828bc9934dc7f77a58a71c90068`.

The descriptor census contains exactly 30 non-coverage Decimal struct paths and
30 corresponding `decimal128(22,18)` value paths. Every struct has the ordered
physical layout `value`, `exponent`, `negative_zero`; inverse reconstruction
preserves exponent and signed zero and rejects `negative_zero=true` on nonzero
values. No forward case rounds, and exact logical JSON bytes are reproduced.
All six coverage Decimal paths remain canonical UTF-8, not Decimal structs.

## Retained evidence, PYC, and adversarial checks

Independent shell postflight censuses reproduced the frozen snapshots exactly:

| Scope | Rows | SHA-256 |
| --- | ---: | --- |
| `data/**` and `runs/**` | 272 | `c7edcc0341628b7224069cf4fc3cf3f1ef3bce4994f5bcf2ece904c313b1627c` |
| site-packages PYC | 1218 | `ad6397ba9131fc7684bf9dbfdef4e3ae69ef9a7d9662f561948bef16868f835e` |
| repository PYC | 132 | `9b1407d4f9d5adae170014b9a4852bc1e62331efd57c99d04e69df14ac8719a2` |

All 14 retained runtime-prefix directories exist and are empty, including the
failed pre-admission/control evidence. The retained unaccepted code manifest
`fb1bcca5772d71a0de2c116cd2539d1d2cd757554df8791dad8e0d952cf67083`
remains present and exact.

Twenty independent in-memory adversarial mutations were rejected. They covered
receipt run/build/invocation identity, layer order/hash, boundary path,
noncanonical receipt bytes, manifest build/entry hashes, product physical and
logical semantics, cross-run invocation substitution, duplicate runs, nonempty
runtime prefixes, Decimal nonzero negative-zero and rounding cases, reordered
Decimal struct members, coverage non-UTF-8 representation, and boundary
run/product substitutions. No adversarial check wrote retained or producer bytes.

## Verification gate

- Ruff format: PASS
- Ruff check: PASS
- mypy, three runtime scripts: PASS
- exact six-file pytest population: PASS, `286 passed in 1586.84s (0:26:26)`
- Bandit: PASS
- import-linter: PASS, 3 contracts kept and 0 broken
- local Git guard: PASS, executable and simulated rejection exit `1`
- local-only: PASS, 25 checks and 0 failures, including `main` and zero remotes
- independent postflight retained/PYC censuses: PASS, byte-identical

The review packet forbids all Git operations, so I did not directly invoke the
listed `git diff --check` or `git remote` commands. The independent local-only
validator performed the permitted zero-remotes and branch checks; the fixed-hash
master acceptance records a post-correction diff-check PASS and empty remotes.

The first producer gate correctly found two absolute current-host uv path values
in the retained R2 structured packet. The master used bounded orchestration
authority to replace exactly those values with digest-bound identity tokens and
mechanically rebound the R3 chain. Fresh review confirmed the corrected packet
hashes and local-only 25/25 PASS. This was an evidence-configuration correction,
not a remaining product or runtime finding.

Two review-harness mistakes were procedural only: an initial manifest helper
looked for an attribute not present on `LayerManifest`, and an initial descriptor
assertion assumed four coverage paths rather than the correct six. The corrected
independent checks passed without changing a repository or retained-root byte.
An initial sandboxed local-only invocation also lacked read access to the
existing offline uv cache; the identical command passed after receiving only
that read access.

## Findings and disposition

- P0 findings: `0`
- P1 findings: `0`
- P2 findings: `0`

The corrected R3 real-root invocation evidence satisfies the packet's wrapper,
receipt, product, Decimal, retained-root, adversarial, test, and local-only
predicates. This review returns **PASS** for fresh master adjudication. No
producer rework or user-boundary decision is required.
