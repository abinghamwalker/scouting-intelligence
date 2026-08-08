# W04 Wyscout data health

Status: **PASS**
Canonical evidence: `reports/phase-gates/W04/data-health.json`
Canonical JSON SHA-256: `ecbf0e52ec702a42b06a2b0a0528bd1716ee7c2922ab4924e468cca83fd9cfd5`

## Closure basis

The controlling 2026-08-03 closure steer uses accepted runtime R11 and retained
real-root R3 as the minimum W04 operational baseline. Terminal R12 is the final
runtime-hardening revision; it is verified by its independent review, focused
suites, and the complete repository gate. No R13 or additional real-root run is
claimed or required.

This distinction is explicit: R3 proves truthful execution and byte-identical
products from two complete local runs; R11/R12 prove the later resource-roster,
loaded-subset, admission, completion-evidence, and host-admission corrections by
accepted review and tests. R3 is not relabelled as having executed later code.

## Source, rights, and temporal health

| Measure | Value |
| --- | --- |
| source manifest | `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd` |
| source completion index | `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df` |
| admitted partitions | 5 |
| matches | 1,826 |
| actions | 3,071,395 |
| teams / players | 142 / 3,603 |
| duplicate action IDs | 0 |
| partition match-set equalities | 5 / 5 |
| licence / use | CC BY 4.0; restricted local internal review; attribution required |
| source availability floor | `2020-01-28T14:24:27Z` |
| feature cutoff | `2026-08-01T00:00:00Z` |
| temporal receipt state | `STRICT_BEFORE_CUTOFF_PASS` |
| export or external publication | forbidden / none |

All six source dimensions are complete: source objects `7/7`, admitted members
`10/10`, match partitions `5/5`, event partitions `5/5`, match-ID alignments
`5/5`, and directory-only scope exclusions `4/4`. Overall source coverage is
exactly `1`, with no missing dimension.

Measured source limitations remain visible: 226,038 zero-actor actions, 23
unresolved bench-player references, 8 unresolved substitution-in references,
7,821 unknown/invalid subevent references, and 3 out-of-range coordinate values.
There are zero match team-count violations, team-key conflicts, event-team/match
conflicts, partition conflicts, or reproduced identity collisions. Exact minutes
and per-90 denominators are unsupported.

## Product and digest health

Build `b1f1a9135e307b115fd1d00f19dae7951993765ee5ac1fb5d5afeb245fdc7b79`
binds code manifest
`c94e650146a982174820ba694a2dcd1b20dc6648426527213bf2e6de09861c2c`.
The layer manifests are Bronze `abdc5d89fdac08638f4877f9a44dceb9356d789741bd93981cce4a9b6825d9c1`,
Silver `089673ff01edd7de7b6e5777958d19cbaffaa9f429b042ab4986746d80a7c36a`,
and Gold `08de1349a532c3f455d792ee56aafc3d8c587828bc9934dc7f77a58a71c90068`.

| Role | Rows | Physical SHA-256 | Semantic SHA-256 | Reconstructed logical-byte SHA-256 |
| --- | ---: | --- | --- | --- |
| Bronze known record | 1,768 | `e48b203df0d2b83d53af9340cc76ec42a0bb138b5e9608284718d9f6854e9aaf` | `4186f51a8694be1ca4699baf0f3c77e24b2206cc63f18bb7954074cc186d76ca` | `749e51f850372dfd610ffaf2037c8520e94282bca2eeac20f7ef582181cc7faa` |
| Bronze rejected field | 3,544 | `b2dc4e9265edb79402b19b739be2167dd2bdcaea9afdf9c1b9304953d9f2278e` | `2d0d05c88e00aa2484215f691f9ce7233324e8f0dbd9ea98e86e16e385c08825` | `7f0a9a567ee81cbfe652422d09208679de8bc2a2f80a699b198a920c0d979384` |
| Silver action | 13 | `89e9645d9715fc155f09a5dae14ac261233aa7599b8266cbcef6a0b5eb86f53a` | `9d98a59a82a45bf077e72dfdb26545d24f3e718d3c8266b085ec95a03bba22d3` | `e6d7e2d1abcd6cc4595b0453797ccd5bb22577c3ed384231eacc5aface27f3b9` |
| Silver lineup stint | 1 | `b05e1573cfee6cb3d2a44b675e72917dac70562af17e85494e2948934d15bda2` | `d5a83d1a820ec5197e18709b2ed966824c6edf836926cd8faddeab8617145c08` | `dbfb8c0befb5633d00191fd7680d90bd7af28c9df617ba1cc76442c2c0baac7b` |
| Silver possession | 2 | `a65461738eb21211cb9695af5bbdad9a28ea5f1280de2a3ae79559a555978878` | `bf1114a1d1b2b6325e3656aed297d5f3f7ec872b1485b47c65cb5c47a617417a` | `681f027ed5406f0e39b7c80bf25d5f093c64e111ef0df1fd62e4a717f30d9d5f` |
| Silver player-match fact | 1 | `5b8bb0d0dcc1caf9709a1706041110ebadfd3ac14a590fefc4622cc5c41fa1da` | `a8db5735a2f0ec1ee37d46e9dc2985bb4d20b2ef08fc70acfc4e4eec38af5a0f` | `bd7c92d470bfb036a44057e014acd79d55aef4ed430086edb654e767327fb913` |
| Gold player window | 1 | `6e49b4322c766352fdc427b8d35d73ddaed036d0bd19f1d65435fe3a72edcd17` | `f1751b4f1ff7911ad339fa1954cd5c88483fc09c733547dba87d7aa301c1bffa` | `ef6a57e33a9702f48496570a05fba7f70b7478eb25a30902b75bc9ad4b594cc6` |

Thirty non-coverage Decimal paths use the exact ordered
`decimal128(22,18)` / `int8 exponent` / `bool negative_zero` struct. Projection
is lossless with no rounding; inverse reconstruction preserves the original
exponent and signed zero and rejects a nonzero value with `negative_zero=true`.
Six coverage Decimal paths remain canonical UTF-8. Real product readback exactly
reproduced every logical JSON-byte digest above.

## Gold health

Gold is deliberately one match, one player-window row, one contributing
player-match fact, and four supported count features: actions `2`, known-coordinate
actions `2`, matches `1`, and possession-resolved actions `2`. Its 868 source rows
do not represent the complete 3,071,395-action source population.

All six Gold dimensions are complete and distinct from source coverage:
identity `3/3`, lineup `1/1`, action `2/2`, coordinate `2/2`, possession `2/2`,
and temporal `8/8`. Overall Gold coverage is `1`, with no missing dimension. The
applicability remains `research_only` because the evidence is
`RIGHT_CENSORED_OR_UNCERTAIN`.

## Runtime and completion evidence

The retained R3 environment records Python `3.12.12`, the exact locked selection,
wheel-extraction and installed-record projections, the 35-row executable census,
three interpreter aliases, Packaging bootstrap and 1,230 ordered tags. Its key
digests are:

- selected lock closure: `71e19fea7a508cfe462c047775e494509813ce7612c16a98d46af57f254d8bfd`;
- extracted runtime `L`: `e785af59b5e1d364535b7205b4707d75e767b5b66241ee1a52514a3c04e2805b`;
- installed-record runtime `I`: `73c9aaea089238ea3fef228d075ad0adce9c8697467fdebb7b6d24139cd010ca`;
- executable census: `3378e7407967128fe37b8569f6e90ecb7b0a3762078fd6156f435f695f6debb3`;
- interpreter: `a1615a856f4eb624574467fb7678b0f87944e4483411e30fbe7e543bd76af1fb`; and
- PYC policy source map: `3fde9f2174c08d33c1b85f2f52337ce9e4da52ea55adcfa6507187f034deaffd`.

The accepted projection proves `L == I` semantically. R11 separately closes the
exact 30-resource roster at detail digest
`29d8a7cf4c4acab8a52d6008fc5f8975509cc445f5680e45e5974687e65c7bfb`.
R12 closes the normalized loaded-owner subset and strict completion-evidence
validators in the terminal test population. The older R3 full-installed digest is
not presented as an R12 subset observation.

Two R3 runs returned exact `COMPLETE`, exit `0`, and byte-identical products and
manifests. Their rebuild/boundary receipt pairs are
`63b645423ca72edcb2055814293a0024d549bd01e45005136ff3730416530f10` /
`a077a8a5385c633d1a6911717b843e2b7d60f5a6ac025136057ae810d9c595c2`
and `db8501cf9c644644ca5ba614e87fea43d3d3c0568fcad405e028fb6d2ceace18` /
`16488eb7ad9d6021e4f442455427a6c2d16e3db21a336a60f515cfbd5b08ab00`.

The retained post-gate inventories are 1,218 site-PYC rows, 133 repository-PYC
rows, and 272 `data/**`/`runs/**` rows. Host-specific PYC/cache tags, inode and
link counts, empty-directory metadata, temporary paths, timestamps, and equivalent
filesystem assurance are explicitly deferred to
`W10-RUNTIME-HOST-STATE-HARDENING-01`; they are not silently waived and do not
block W04 absent a controlling P0/P1 path.

## Complete gate and residuals

The terminal gate passed locked offline sync, formatting, lint, typing, import
boundaries, 2,618 tests, Bandit, local guard, 25 local-only checks, the W04 phase
verifier, whitespace integrity, main-branch, and zero-remotes checks. The one
test warning is a non-failing Starlette deprecation notice.

Remaining limitations are product limitations, not hidden gate failures: old male
senior-football source coverage, no current-value claim, unsupported exact minutes
and per-90, one-match/four-feature Gold scope, right-censoring uncertainty, and the
explicit W10 host-state backlog.
