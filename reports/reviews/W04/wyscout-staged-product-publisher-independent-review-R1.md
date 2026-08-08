# W04 staged immutable publisher independent review R1

Date: 2026-08-01

Review ID: `w04-wyscout-staged-product-publisher-independent-review-R1`

Candidate: corrected R2 `WyscoutStagedPublisher`

Recommendation: **REWORK**

Finding counts: **P0=0, P1=1, P2=0**

## Scope and independence

This review was performed against packet
`W04-STAGED-IMMUTABLE-PUBLISHER-REVIEW-01-R1` without implementation, test,
dependency, product, orchestration or Git changes. The reviewer did not produce the
candidate and did not delegate. Review execution used only isolated temporary roots;
the real W04 product, manifest and rebuild-run roots were not written.

## Fixed bindings

Every packet-fixed byte matched before candidate analysis:

| Artifact | Expected and reproduced SHA-256 |
| --- | --- |
| R1 producer packet | `99921ecc50e6a60bd5a482473cc1cdb051c0aced025f278decbff48e8a26d5fe` |
| R2 producer packet | `bab41bf6e8d7e9b01c2820f3f288ae92559d30cd4d8f0d3d290119afe0ed1a50` |
| R1 producer return | `31f8cfef9726b24d4cea0b3efbc9adf804c1d4110fa7a1178c54d81e8f9a883e` |
| R2 publisher | `9805dbad85cdcf7c49c50634e31eefda4c1eef7b3f22cc0d969e98f93b0c3a6f` |
| R2 publisher tests | `d509b04df48c9dfbeb6661e5bab9e32dd74ce9c8d2243b70b77f5a52b95681e5` |
| R2 producer return | `916a5b7cffdb668eb0326b33290bcab4f4e3de2457b6ca86d0aede0069303cbe` |
| complete repository gate | `22b0b73078d4d2f0cc7e5eed3920a5401fd3d0e02d9ee3c66d9c7af02f76f469` |
| R4 build/receipt audit | `a6f8f3321dcfdb0c04d231d3e07d06497441ce703716d6e509f3f45b8829c222` |
| R20 design | `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047` |
| R21 correction | `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020` |
| GuardedStorage | `62a026560c4821d123d42afcd3438be18572ec0fef03f1747a0cbcfa97f030ef` |
| accepted Parquet encoder | `bd849dda61b570378697ce703719c2058fc9c450e298a88a9f1e5f95ad0a7ff4` |

The review packet itself reproduced as
`92842b6c9fdbf433f84510e3be93d38efefa917284de5eb11b3e333ac0512108`.

## Finding

### W04-PUBLISHER-R2-P1-REPLAY-STAGED-APPEARANCE-RACE — P1

The equal-final replay branch checks that the serializer-owned staged name is absent
only once, before it reads the existing final. It then invokes the caller validator
and final code/environment/resource recheck and returns success after a fresh final
readback, but it never reopens the staging root to require that the exact `.partial`
name remained absent after those callbacks.

The affected sequence is
`src/scouting/storage/wyscout_publication.py:302` through `:328`. This is a
fail-open race against the frozen R1/R2 rule that races fail closed. A successful
`created=False` result can coexist with newly appeared staged evidence, leaving an
ambiguous failed-publication artifact after the caller has been told publication
succeeded.

Independent executable reproduction used an isolated temporary root:

```text
1. Publish exact bytes to artifact.parquet successfully.
2. Replay the same final bytes.
3. During final_recheck, create artifact.parquet.partial as a regular 0600 file.
4. Observe the method result and both names.

observed = {
  "final_unchanged": true,
  "outcome": "returned_success",
  "result_created": false,
  "staged_exists": true,
  "staged_mode": "0o600"
}
```

The probe exited `0`; its assertions and output demonstrate the defect rather than a
test-harness failure.

## Bounded executable rework

Change only the existing publisher module and its focused test file under a new
master-issued correction packet:

1. In the equal-final replay branch, after validator and final recheck, perform a
   fresh descriptor-relative, no-follow read of the exact named staging parent and
   require the serializer-owned `.partial` name to remain absent before returning a
   success result.
2. Bind that read to the originally fixed staging-root and staging-parent identities.
   A regular file, symlink, hardlink, FIFO, directory, unsafe mode/link state,
   disappeared/replaced parent or other non-absent state must raise and return no
   result. Do not unlink, repair, chmod or replace the raced evidence.
3. Add a focused replay-race test that creates the exact `.partial` during
   `final_recheck`, requires failure/no result, and proves the pre-existing final and
   newly appeared staged evidence are both retained unchanged. Parameterized
   nonregular/link variants may be added without widening production behavior.
4. Preserve the exact three-root vocabulary, all frozen inputs, both accepted
   post-link failure states, sidecar-free/no-replace behavior and real-root absence.

No architecture, schema, product, dependency or local-only decision is required.

## Passing independent evidence

- Closed root vocabulary: all three exact names were admitted; thirteen aliases and
  representative non-string values were rejected at both constructor and selection
  seams before write (`13/13` each, `no_write=true`).
- Post-link final-parent fsync failure: raised with final and staged names on the same
  validated inode, link count two, mode `0600`, exact bytes and unrelated final
  evidence unchanged.
- Post-unlink staging-parent fsync failure: raised with staged name absent, exact
  one-link `0600` final retained and unrelated final evidence unchanged.
- Static inspection found no GuardedStorage wrapping, digest sidecar, chmod repair,
  replacement/rename primitive, provider/network access, cloud/container/CI,
  endpoint or deployment behavior.
- The real W04 inventory contained only the previously accepted source/index and
  identity artifacts; no Bronze, Silver, Gold, layer manifest, receipt, rebuild run
  or `.partial` artifact was present.

## Checks

All checks were run with `PYTHONDONTWRITEBYTECODE=1`, locked/no-sync uv and no bare
Python. The first sandboxed uv-cache attempts exited `2` before a tool or repository
module ran; approved read-only reruns produced the results below.

| Command | Exit | Result |
| --- | ---: | --- |
| `uv run --locked --no-sync ruff format --check src/scouting/storage/wyscout_publication.py tests/unit/test_w04_staged_product_publisher.py` | 0 | 2 files already formatted |
| `uv run --locked --no-sync ruff check src/scouting/storage/wyscout_publication.py tests/unit/test_w04_staged_product_publisher.py` | 0 | all checks passed |
| `uv run --locked --no-sync mypy src/scouting/storage/wyscout_publication.py tests/unit/test_w04_staged_product_publisher.py` | 0 | no issues in 2 files |
| `uv run --locked --no-sync pytest -q -p no:cacheprovider tests/unit/test_w04_staged_product_publisher.py tests/unit/test_w04_wyscout_product_formats.py tests/unit/test_guarded_storage.py` | 0 | 147 passed in 2.13s |
| `uv run --locked --no-sync bandit -q -r src/scouting/storage/wyscout_publication.py` | 0 | no finding |
| `uv run --locked --no-sync python scripts/verify_local_only.py` | 0 | PASS, 25/25 checks |
| independent equal-final staged-appearance probe | 0 | reproduced P1 fail-open success |
| independent exact-root vocabulary probe | 0 | 3 admitted; 13/13 constructor and selection rejections; no write |
| independent two-boundary fsync probe | 0 | both exact retained states passed |

## Verdict

`REWORK`. The candidate is not accepted because P1 is nonzero. P0/P1/P2 are
`0/1/0`. Product publication remains prohibited.
