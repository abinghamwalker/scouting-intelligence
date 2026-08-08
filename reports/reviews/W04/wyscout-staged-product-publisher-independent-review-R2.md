# W04 staged immutable publisher independent review R2

Date: 2026-08-01

Review ID: `w04-wyscout-staged-product-publisher-independent-review-R2`

Candidate: corrected R3 `WyscoutStagedPublisher`

Recommendation: **PASS**

Finding counts: **P0=0, P1=0, P2=0**

## Scope and independence

This review was performed under packet
`W04-STAGED-IMMUTABLE-PUBLISHER-REVIEW-01-R2`. The reviewer did not produce the
candidate, did not delegate, and changed no implementation, test, dependency,
product, authority, orchestration, verification or Git state. All executable
publisher probes used retained isolated roots beneath `/private/tmp`; no real W04
product, manifest, receipt, rebuild-run or staged path was created.

## Fixed bindings

Every packet-fixed byte matched before candidate analysis:

| Artifact | Expected and reproduced SHA-256 |
| --- | --- |
| R2 review packet | `203c9418422e1ff6dc5ecd1f3235433eae9202cabaf07907e71c129ca309b3eb` |
| R3 producer packet | `8253d13832db1eb0fdb4d8cedb7829768524ebe9028ed2964591ec53068fa2cf` |
| R3 publisher | `01b56c0400af0a4fba1adbf06b53b4e94a8571be66c7e0770ca6d72b4c740c13` |
| R3 publisher tests | `639503018a5528ad8463d21e68fbfd0133e09c9884838a2422daf911173f709e` |
| R3 producer return | `e218ad99c9323aef57f2dfa50fef219afff6686f0bc89c2d84fe3d0f1aaab69a` |
| failed R1 review | `6e574fde38eefba002db7568596f10346beb7d6e16c7149bdda2af6cb402a7d3` |
| failed R1 reviewer return | `bdb9826137d6b094b8e19d79e6480c5f2fcfb792df51534e5ab9f022b453ceb7` |
| R2 producer packet | `bab41bf6e8d7e9b01c2820f3f288ae92559d30cd4d8f0d3d290119afe0ed1a50` |
| R2 producer return | `916a5b7cffdb668eb0326b33290bcab4f4e3de2457b6ca86d0aede0069303cbe` |
| complete repository gate | `22b0b73078d4d2f0cc7e5eed3920a5401fd3d0e02d9ee3c66d9c7af02f76f469` |
| R4 build/receipt audit | `a6f8f3321dcfdb0c04d231d3e07d06497441ce703716d6e509f3f45b8829c222` |
| R20 design | `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047` |
| R21 correction | `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020` |
| GuardedStorage | `62a026560c4821d123d42afcd3438be18572ec0fef03f1747a0cbcfa97f030ef` |
| accepted Parquet encoder | `bd849dda61b570378697ce703719c2058fc9c450e298a88a9f1e5f95ad0a7ff4` |

## R3 correction reproduction

The former R1 fail-open sequence was independently repeated through the public
publisher API:

1. publish exact bytes to an immutable final;
2. replay those exact bytes;
3. create the exact serializer-owned `.partial` as a safe regular `0600`,
   one-link file during `final_recheck`; and
4. observe the outcome and both retained names.

R3 raised `PublicationRaceError`, returned no result, preserved the exact final
bytes/device/inode/mode/link count, and retained the raced staged bytes unchanged.
This directly closes `W04-PUBLISHER-R2-P1-REPLAY-STAGED-APPEARANCE-RACE`.

The same independent probe attacked the final replay checkpoint with every required
state:

| Staged or parent state at final checkpoint | Required and observed result |
| --- | --- |
| safe regular file (the failed R1 race) | `PublicationRaceError`; final and evidence retained |
| symlink | `PublicationPathSecurityError`; link and target retained |
| hardlink / unsafe link count | `PublicationPathSecurityError`; both two-link names retained |
| FIFO | `PublicationPathSecurityError`; FIFO retained without blocking |
| directory | `PublicationPathSecurityError`; directory retained |
| regular file with mode `0640` | `PublicationPathSecurityError`; mode and bytes retained |
| disappeared original staging parent | `PublicationRaceError`; moved parent/evidence retained |
| same-path replacement staging parent | `PublicationRaceError`; original moved evidence and empty replacement retained |

The retained probe root is
`/private/tmp/w04-publisher-r2-review-lzbuqugu`. The probe printed
`R1_RACE_AND_R3_FINAL_CHECKPOINTS_PASS` and exited `0`.

Source readback confirms replay success is possible only after validator,
final code/environment/resource recheck and a fresh immutable-final readback. The
new check then reopens the originally declared staging root descriptor-relatively,
requires the stored root identity, traverses without following links, requires the
original staging-parent identity and checks only the exact serializer-owned staged
name. It never removes, repairs, chmods, replaces or reinterprets raced evidence.

## Retained R1/R2 closure

A second independent probe established all three exact root names as the complete
constructor/selection vocabulary and rejected nine canonical-looking aliases plus
representative non-string selections before write. It also injected each accepted
post-link durability boundary:

- final-parent fsync after hard-link creation raised with the final and staged
  names on one exact `0600`, two-link inode;
- staging-parent fsync after staged-name unlink raised with staged absent and the
  exact `0600`, one-link final retained; and
- an unrelated pre-existing final remained byte- and inode-identical in both cases.

The retained probe root is
`/private/tmp/w04-publisher-r2-boundaries-myyfyhod`. The probe printed
`ROOT_VOCABULARY_AND_POST_LINK_FSYNC_PASS` and exited `0`.

Line-by-line readback plus the complete bounded suite re-established every original
R2 invariant: bounded normalized POSIX tails; descriptor-relative no-follow
root/parent traversal; `0700` directories and `0600` files; exact staged name;
full-byte write/fsync/reopen/readback; stable regular-file identity/mode/link/size;
validator then recheck order; immutable equal replay; unequal-final conflict;
same-filesystem hard-link/no-replace promotion; target/link/parent/root races;
EXDEV failure; retained failure evidence; post-unlink one-link final; final
physical-digest readback; no sidecars; and no unrelated-final damage.

Static inspection found no GuardedStorage or Parquet-encoder import/wrapper, chmod,
rename/replace primitive, sidecar construction, provider/network client, subprocess,
cloud/container/CI/endpoint or deployment behavior. The packet-fixed
GuardedStorage and encoder hashes remain unchanged.

## No-write and local-only evidence

The site and repository bytecode inventories were captured before Python review
execution and repeated after the last review command. Both complete path/content
and path/mode/link/size digests were identical:

| Inventory | Count | Content/path digest | Metadata/path digest |
| --- | ---: | --- | --- |
| site packages | 1,086 | `a58b6915d692b5871b2d4aa807ee88523277b46b7e5fd1b99e80a63c6d3c0f46` | `d88df304c5bf0cf265f0c7f7e9ade0cdaaf6ceb28c579e1a7daeb18988d5faf9` |
| repository, excluding `.venv` | 86 | `e472fd71a9a1b44372692159133a23a8accfe99fead7aca8da3b96fc16298e68` | `141e84f43af3d0982fe7e9a70841c3f535502e39534134a36064f4453fbfbdb6` |

No real `.partial` exists. The real W04 Bronze, Silver, Gold and `.staging` roots,
all three generated layer-manifest roots, and `runs/w04/wyscout-rebuild` are absent.
The local-only verifier passed all 25 checks, including empty remotes, active local
push guard, one root uv project, no cloud/container/hosted-CI/deployment surface and
no external service dependency.

## Checks

Every Python-based review command set `PYTHONDONTWRITEBYTECODE=1`, used locked,
no-sync uv, and disabled pytest's cache provider. The first sandboxed independent
probe exited `2` because read-only access to the existing external uv cache was
denied before Python or repository code ran; the approved read-only rerun produced
the evidence below.

| Command | Exit | Result |
| --- | ---: | --- |
| `uv run --locked --no-sync ruff format --check src/scouting/storage/wyscout_publication.py tests/unit/test_w04_staged_product_publisher.py` | 0 | 2 files already formatted |
| `uv run --locked --no-sync ruff check src/scouting/storage/wyscout_publication.py tests/unit/test_w04_staged_product_publisher.py` | 0 | all checks passed |
| `uv run --locked --no-sync mypy src/scouting/storage/wyscout_publication.py tests/unit/test_w04_staged_product_publisher.py` | 0 | no issues in 2 source files |
| `uv run --locked --no-sync pytest -q -p no:cacheprovider tests/unit/test_w04_staged_product_publisher.py tests/unit/test_w04_wyscout_product_formats.py tests/unit/test_guarded_storage.py` | 0 | 155 passed in 2.16s |
| `uv run --locked --no-sync bandit -q -r src/scouting/storage/wyscout_publication.py` | 0 | no finding |
| `uv run --locked --no-sync python -B scripts/verify_local_only.py` | 0 | PASS, 25/25 checks |
| independent R1-race and eight-state R3 final-checkpoint probe | 0 | all states failed closed with exact retained evidence |
| independent exact-root and two-boundary fsync probe | 0 | root closure and both post-link evidence states passed |

## Accepted residual

The accepted same-trust-domain residual remains exact and bounded: a staged name
that appears and disappears wholly between filesystem checkpoints is not
cryptographically excluded. This review does not claim otherwise. Any artifact
present at the final identity-bound checkpoint is never reported as replay success.
Removing that residual would require a different execution primitive or trust
boundary and is outside this correction.

## Verdict

`PASS`. P0/P1/P2 are `0/0/0`. The R3 correction closes the independently
reproduced R1 race without weakening the retained publication contract or expanding
architecture, product or trust scope. This review is independent evidence only;
master readback and acceptance remain required before downstream publication.
