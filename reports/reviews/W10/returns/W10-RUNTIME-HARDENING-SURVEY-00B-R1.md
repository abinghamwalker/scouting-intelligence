# Subagent return

## Task

- task_id: `W10-RUNTIME-HARDENING-SURVEY-00B`
- objective: Locate the smallest W04 runtime-authority seams that can separate
  incidental host/cache metadata from security-relevant source, executable and
  product substitution while preserving all accepted W04 fail-closed and
  zero-read/use witnesses.

## Files changed

- `reports/reviews/W10/returns/W10-RUNTIME-HARDENING-SURVEY-00B-R1.md`

## Summary

- Survey result: **a narrow hardening packet is available, but it must not treat
  all filesystem identity as interchangeable**. The smallest sound seam is the
  dual PYC/cache inventory path. W04 already excludes the raw PYC inventory from
  its 20 stable component digests and from the build/product projection; the
  remaining reopening path is the use of the complete host-specific inventory
  tuple in repeated equality checks and in the outer health digest.
- The packet acceptance test reproduced that path without any mutation by this
  survey: `src/scouting/contracts/__pycache__/evaluation.cpython-312.pyc` is a
  later-wave same-interpreter cache row whose source is outside the frozen W04
  source roster. Three tests stopped in the launcher metadata collector with
  `PYC lacks stable source or exact inert-orphan authority`; the final result was
  `3 failed, 284 passed`. No source byte, executable, product byte, rights,
  temporal, identity, or completion substitution was reported.
- No cache was cleaned, rewritten, opened, hashed, or concealed by this survey.
  The failure is retained as the concrete W10 host-state reproduction.
- Recommended implementation is split into `05A` and `05B`. `05A` is the
  immediately dispatchable PYC/cache boundary below. `05B` may later generalize
  host temporary-path spelling only after equivalent no-follow directory and
  executable-resolution proofs exist. Combining path generalization with the
  PYC change would be unnecessarily broad.

### Exact stable-authority and audit flows

The current launcher and child collectors are intentionally independent. That
independence must remain; neither collector may call or import the other.

#### Stable security/product projection

1. Child `scripts/admit_wyscout_v5_runtime.py::_pyc_policy_source_map` and
   launcher `scripts/launch_wyscout_v5.py::_independent_pyc_detail` construct
   the stable PYC **policy**, not a discovered PYC byte inventory.
2. The policy is the detail behind component key
   `pyc_policy_source_map_digest`. It binds:
   - algorithm `w04-preexisting-pyc-enumerate-deny-v4`;
   - active cache tag `cpython-312` and magic `cb0d0d0a`;
   - exact normal and pytest cache-name grammars;
   - source rows derived from selected distribution RECORD rows, the explicit
     repository code manifest and the uv bootstrap source;
   - four exact inert-orphan predicates;
   - the exact R12 foreign-cache denial predicate; and
   - `no_cleanup`, `zero_in_place_pyc_change` and
     `zero_python_role_pyc_read`.
3. Child `_collect_stable_authority_with_pyc` and launcher
   `_admission_authority_with_pyc` SHA-256 that policy detail into the ordered
   20-component map. The discovered `pyc_before` inventory is returned beside
   the stable triple and is not one of the 20 components.
4. The stable component map is hashed as `environment_digest`, placed in the
   canonical code manifest, and bound through `PreBuildProjection` to the code
   manifest, local resources, selected lock closure, schema and product
   contract. `build_id_for_projection` is therefore downstream of stable
   policy/source/executable/product facts, not raw PYC inode or clock values.
5. `process_launch_contract_digest` explicitly describes child-process
   observations as `operational-build-excluded-closed-v1`. Raw PID, descriptor,
   absolute prefix and physical identity observations are completion evidence,
   not build/product inputs.

This means the digest boundary is already mostly correct. An implementation
must not move raw inventory rows into `components`, `environment_digest`, the
code-manifest digest, `PreBuildProjection`, `build_id`, schema/product digests,
layer manifests or rebuild receipts.

#### Current host-state reopening path

The following exact functions compare or expose the raw inventory after it has
correctly been excluded from stable components:

| File/function | Current use | Required W10 disposition |
| --- | --- | --- |
| `scripts/admit_wyscout_v5_runtime.py::_operational_pyc_inventory` | Produces the child raw no-follow PYC/cache metadata tuple. | Retain full raw audit rows and unsafe-kind/mode/link/path rejection; add only bounded audit-only classifications. |
| `scripts/admit_wyscout_v5_runtime.py::_collect_stable_authority_with_pyc` | Takes two full inventories and requires raw equality. | Compare a separate security projection for admission; retain both raw observations for audit. |
| `scripts/admit_wyscout_v5_runtime.py::run_admission` | Reconstructs the five-tuple twice and compares `final_pyc_inventory == pyc_inventory`. | Compare stable authority plus the security projection; do not suppress collector errors or source/executable drift. |
| `scripts/launch_wyscout_v5.py::_independent_pyc_inventory` | Produces the independent launcher raw tuple with the same row semantics. | Make the same policy outcome independently; do not share implementation with the child. |
| `scripts/launch_wyscout_v5.py::_admission_authority_with_pyc` | Rechecks raw inventory equality around retained reconstruction. | Retain raw audit capture, but use an independently implemented security projection for the equality boundary. |
| `scripts/launch_wyscout_v5.py::_require_outer_authority_snapshot` | Compares the complete four-tuple, including every raw inventory field, across the whole launch. | Recollect and validate every row, then compare stable authority plus protected security facts rather than absolute host metadata. |
| `scripts/launch_wyscout_v5.py::_pyc_inventory_health` | SHA-256 hashes the complete raw tuple and emits counts in completion status. | Keep an explicitly labelled raw audit digest/counts; add a portable security-policy digest. Neither becomes product authority. |
| `scripts/launch_wyscout_v5.py::_execute_outer_control` | Retains the initial raw tuple, invokes repeated outer snapshots, and places health in `w04-local-control-completion-v2`. | Preserve truthful completion and all repeated recollection. A safe audit-only row may vary without changing stable/product authority; an unsafe row or protected predicate failure still aborts. |

### Exact implicated metadata rows

`CACHE_DIRECTORY` rows currently contain:

- `ctime_ns`, `device`, `entry_kind`, `inode`, `link_count`, `mode`,
  `mtime_ns`, `path`, `role`, `size_bytes`.

`PYC` rows currently contain:

- `authority_class`, `entry_kind`, `mode`, `path`, `role`, `device`, `inode`,
  `mtime_ns`, `ctime_ns`, `size_bytes`, `source_path`, `source_authority`.

The exact protected foreign-cache row additionally contains:

- `denial_policy=FOREIGN_INTERPRETER_TAG_DENIED_ZERO_READ`;
- `foreign_cache_tag=cpython-314`; and
- `source_authority_required=REPOSITORY_CODE_MANIFEST`.

The protected policy predicate for that row is exactly:

- path `scripts/__pycache__/admit_wyscout_v5_runtime.cpython-314.pyc`;
- role `WHOLE_REPOSITORY`;
- class `REPOSITORY_FOREIGN_CACHE_TAG_DENIED`;
- tag `cpython-314`;
- mode `0644`;
- size `190312`;
- source prerequisite `scripts/admit_wyscout_v5_runtime.py`; and
- no digest, owner, source authority, read, open, hash, import or execution
  authority for the PYC itself.

### Security-authoritative versus audit-only facts

| Fact | Classification and fail-closed rule |
| --- | --- |
| Repository and installed source path, owner/version, regular no-follow kind, mode, singular-link constraint, size and SHA-256 | **Security authoritative.** These feed repository/source/RECORD components. Any substitution remains a rejection. |
| Interpreter, libpython, loader, uv, wrapper, selected-wheel and installed-RECORD bytes/topology | **Security authoritative.** No change is proposed to executable census, resolution, bytes, ABI, selected closure or runtime-subset checks. |
| Schema/product preimage bytes and logical/physical digests, local resources, rights and temporal authorities | **Security/product authoritative.** No change is proposed to their functions, constants, rosters or validation. |
| Exact R12 foreign-cache predicate and its stable source prerequisite | **Protected denial authority.** The predicate must remain exact and singular. Missing/substituted predicate, source, path, class, tag, mode, size, link or role remains a rejection. The PYC never gains positive authority. |
| PYC/cache path containment, `__pycache__` placement, regular/directory no-follow kind, non-symlink state, safe mode, PYC singular link, `.pyo` prohibition and zero-read/use policy | **Security admissibility facts.** An unsafe entry still aborts before projection. |
| Absolute `device` and `inode` numbers on a safely classified cache row | **Audit-only across independent hosts/runs.** Same-object equality remains security relevant while a guarded authoritative file/descriptor is being opened or read; that is a different seam and must remain unchanged. |
| Absolute `mtime_ns` and `ctime_ns` on a zero-read/use PYC or cache directory | **Audit-only.** Retain in raw inventory, but do not let the absolute values enter a product or portable security digest. |
| Cache-directory `link_count` and `size_bytes` after directory/no-symlink/mode/path checks | **Audit-only across filesystems.** Entry enumeration remains explicit. This does not apply to W04 child runtime prefixes, whose exact retained identity and empty-before/after evidence remain protected. |
| Generic safe PYC `size_bytes` | **Audit-only**, except where an accepted exact predicate (the R12 foreign row or inert-orphan predicate) binds size. PYC bytes remain unread and unhashed. |
| Newly appearing safe foreign-interpreter cache rows | **Audit-only denied-zero-read rows.** They receive no owner, digest, source, executable, component, environment, build, schema, product, roster or runtime authority. |
| Newly appearing same-tag rows for explicitly identified accepted post-W04 source paths | **Audit-only denied-zero-read rows.** They may be allowed only through an exact W09/W10 non-authority path roster. Arbitrary unmanifested same-tag rows remain rejected so the existing unmanifested-source witness is preserved. |
| Raw audit inventory digest and counts | **Audit evidence only.** They may vary and remain visible. A second portable security-policy digest should bind policy/classification, not raw host values. |
| Runtime-prefix `device`/`inode` equality, exact empty-before/after state, mode `0700`, no symlink, child argv/environment/nonce/frame/exit/diagnostic bindings | **Truthful-completion/security evidence.** Do not alter in `05A`. |
| Absolute TMPDIR spelling | Already **excluded from stable product authority** by `<W04_TMPDIR>` normalization, but still an exact operational transport input. Do not broaden it in `05A`; see `05B` below. |

The key distinction is contextual: an absolute inode value is not portable, but
descriptor/path identity equality during a protected source read is a security
witness. W10 must de-authorize only the former, not remove the latter.

### Portable fixtures to use

Retain and extend the existing `tmp_path` fixtures rather than checking in PYC
bytes or relying on one host's inode, clocks or directory link count:

1. `_minimal_pyc_policy`: keep as the exact R12 protected-denial fixture.
2. `_manifested_pyc_fixture`: keep as the active-tag source-associated metadata
   fixture and raw-drift witness.
3. `_empty_cache_directory_fixture`: keep as the cache-directory host-metadata
   fixture.
4. Add `_accepted_later_wave_pyc_fixture`: create a regular mode-`0644` PYC in
   `__pycache__` for an exact path in a frozen W09/W10 audit-only source roster;
   prove that child and launcher classify it identically, never open it, and do
   not change the stable security projection.
5. Add `_foreign_audit_only_pyc_fixture`: create two safe non-`cpython-312` tags
   under both traversal roles; prove tag/path/class retention, zero read/use and
   no positive authority.
6. Add `_host_metadata_variant_pair`: construct equivalent directory/PYC trees
   in two separate temporary roots, deliberately vary timestamps and recreate
   directories to vary inode/device where the host permits; assert raw audit
   inventories differ while portable security projections match. Never assert
   a universal numeric inode, timestamp, directory size or directory link count.
7. Keep `_synthetic_process_evidence` with directory link count `2` for the
   accepted Darwin W04 runtime-prefix witness. It is not the portable cache-row
   fixture and must not be relaxed by `05A`.

### W04 protected witnesses that must remain

The complete existing
`tests/unit/test_w04_wyscout_runtime_control.py` is the non-negotiable regression
boundary: no deletion, weakening, `xfail`, skip, narrowed parametrization or
message-only replacement is permitted. In particular, retain all cases in these
backlog-sensitive witnesses:

- `test_foreign_cache_tag_has_one_exact_denied_zero_read_classification`;
- `test_foreign_cache_tag_rejects_every_predicate_substitution`;
- `test_foreign_cache_tag_rejects_duplicate_predicate`;
- `test_foreign_cache_tag_rejects_missing_predicate`;
- `test_foreign_cache_tag_rejects_missing_or_wrong_stable_source`;
- `test_foreign_cache_tag_rejects_every_retained_path_or_lstat_drift`;
- `test_foreign_cache_tag_collector_never_opens_reads_or_hashes_pyc`;
- `test_unmanifested_source_pytest_pyc_is_rejected_by_child_and_launcher`;
- `test_child_and_launcher_pyc_snapshots_detect_inventory_drift`;
- `test_child_and_launcher_pyc_census_rejects_mode_and_link_drift`;
- `test_cache_directory_row_binds_one_complete_no_follow_lstat_snapshot`;
- `test_cache_directory_inventory_detects_same_path_mode_0755_replacement`;
- `test_cache_directory_inventory_detects_same_inode_clock_drift`;
- `test_cache_directory_inventory_detects_link_count_size_and_entry_drift`;
- `test_cache_directory_inventory_rejects_link_and_mode_attacks`;
- `test_child_pyc_census_is_lstat_only_and_does_not_share_launcher_collector`;
- `test_launcher_pyc_census_has_exact_child_rows_and_zero_pyc_open_events`;
- `test_exact_uv_outer_present_pyc_metadata_census_survives_unconditional_denial`.

Also retain the broader source/executable/product/truthful-completion witnesses
that prevent an audit projection from becoming an authority bypass:

- `test_v2_aggregate_guard_rejects_terminal_byte_drift`;
- `test_guard_read_rejects_symlink_hardlink_and_unsafe_mode` and
  `test_guard_read_rejects_unsafe_paths_before_open`;
- `test_interpreter_alias_census_rejects_a_fourth_alias`;
- `test_bootstrap_byte_mutation_is_rejected`;
- `test_site_pth_census_rejects_a_fourth_file`;
- `test_editable_metadata_relation_drift_is_rejected`;
- every `test_runtime_subset_rejects_*` case;
- every `test_launcher_runtime_subset_rejects_*` case;
- `test_child_process_evidence_rejects_file_style_link_count_for_empty_directory`;
- `test_child_process_evidence_rejects_coherent_cross_field_attacks`;
- `test_child_process_evidence_rejects_whole_valid_runtime_row_envelope_substitution`;
- `test_synthetic_two_root_runtime_subset_mismatch_is_rejected`;
- `test_outer_completion_rejects_stale_v1_at_status_boundary` and
  `test_outer_completion_rejects_swapped_or_omitted_process_rows`;
- `test_closed_admission_environment_rejects_missing_additional_and_absent_names`;
- `test_child_collector_substitution_cannot_change_retained_oracle`;
- `test_actual_admission_rejects_repository_identity_substitution`;
- `test_immutable_existing_manifest_conflict_is_not_repaired`;
- `test_retained_outer_descriptor_and_control_prefix_reject_drift`;
- `test_outer_control_child_failure_emits_no_completion`;
- every outer encoding, resident-module, inherited-descriptor and bootstrap
  substitution parametrization at the end of the file.

The full-file command is the authoritative way to ensure every parameterized
mutation remains present.

### Proposed bounded implementation packet

- proposed task_id: `W10-RUNTIME-HOST-STATE-HARDENING-05A-R1`
- objective: Add dual independent portable PYC/cache security projections and
  bounded audit-only classifications for foreign tags and frozen accepted
  post-W04 source paths, while preserving the complete raw inventory and all
  W04 denial, source, executable, product and completion controls.
- suggested allowed paths:
  - `scripts/admit_wyscout_v5_runtime.py`
  - `scripts/launch_wyscout_v5.py`
  - `tests/unit/test_w04_wyscout_runtime_control.py`
  - one task return under `reports/reviews/W10/returns/`
- dependency/lock changes: forbidden.
- migrations/contracts/schema/product preimages: forbidden.
- delegation: forbidden for the producer because the two collectors and their
  equality semantics must be changed and reviewed as one bounded unit.

Required implementation properties:

1. Keep the exact R12 foreign predicate as a special case evaluated before any
   generic audit-only classifier. All current predicate/source/path/tag/mode/
   size/link/symlink and zero-read/use tests must continue to reject attacks.
2. Keep unknown `.pyo`, PYC outside an exact `__pycache__`, directory symlinks,
   nonregular PYC, unsafe modes and PYC hardlinks fail closed.
3. Classify a non-active interpreter tag only after strict contained-path and
   no-follow metadata validation. Emit an explicit audit-only/zero-read class
   with `source_authority=None` and no owner or digest.
4. Do **not** broadly allow arbitrary same-tag unmanifested PYC. Build an exact,
   frozen audit-only path roster from accepted post-W04/W09 source paths (the
   current concrete reproduction includes
   `src/scouting/contracts/evaluation.py`). A same-tag row outside both stable
   source authority and that roster must still fail the existing unmanifested
   source test.
5. Add independent child and launcher security-projection functions. Collection
   still emits the complete raw rows and still fails immediately on unsafe
   metadata. Repeated authority checks compare stable components and the
   protected projection; raw host clocks/inodes/cache-directory size/link count
   remain visible audit evidence but do not decide build/product identity.
6. Keep source/executable reads and their same-open descriptor/path identity
   checks byte-for-byte fail closed. Do not reuse the cache-row projection for
   `_guard_read_relative`, `_absolute_regular`, stdlib/encoding traversal,
   `_entrypoint_source`, runtime subset validation, or executable resolution.
7. Keep the runtime prefix identity/emptiness and process evidence schema
   unchanged in `05A`, including the R12 link-count-`2` witness.
8. Keep the raw health digest, label it audit-only inside the health object, and
   add a distinct portable security-policy digest. Neither is added to stable
   components or build/product projections.
9. The child and launcher must produce byte-identical classifications and
   projections from independently implemented code. Add source inspection tests
   proving neither calls the other and neither PYC collector opens, reads,
   hashes, imports, executes, repairs, renames or deletes a PYC.
10. Retain negative evidence. Do not delete current cache rows to obtain a pass.

Suggested `05B` follow-up, not part of `05A`:

- Survey and then normalize safe operational TMPDIR spelling in
  launcher `_w04_early_bootstrap`, `outer_bootstrap_transport`,
  `_closed_child_environment`, `_normal_environment_object` and child
  `normalized_child_environment`.
- Preserve the closed environment key roster, required-absent injection list,
  exact uv/interpreter resolution, project/venv/cache containment, and raw
  transport evidence. Accepting an arbitrary TMPDIR, HOME, PATH, UV or cache
  root without descriptor/ownership/containment proof would weaken W04 and is
  expressly not recommended.

### Focused verification commands for the implementation packet

Run through the root `uv` environment:

```text
uv run pytest -q tests/unit/test_w04_wyscout_runtime_control.py -k 'foreign_cache_tag or pyc or cache_directory or present_pyc_metadata'
uv run pytest -q tests/unit/test_w04_wyscout_runtime_control.py -k 'guard_read or interpreter or runtime_subset or child_process_evidence or outer_completion or repository_identity or immutable_existing_manifest or outer_argv'
uv run pytest -q tests/unit/test_w04_wyscout_runtime_control.py
uv run pytest -q tests/contracts/test_w04_wyscout_v2_aggregates.py tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_w04_wyscout_schema_closure.py
uv run pytest -q tests/security/test_w04_wyscout_vertical_slice_publication.py tests/e2e/test_w04_wyscout_vertical_slice.py
uv run ruff format --check scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py
uv run ruff check scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py
uv run mypy scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py
```

The implementation return must record both of these explicit invariants:

- host-variant fixtures may change raw audit rows but leave the stable component
  map and portable security projection unchanged; and
- every source/executable/product/process substitution and every PYC zero-read/
  use witness still fails or passes exactly according to its accepted W04 role.

## Tests run

- command: `uv run pytest -q tests/unit/test_w04_wyscout_runtime_control.py`
  - exit status: `1`
  - result: `3 failed, 284 passed in 48.96s`. The three failures were
    `test_child_collector_substitution_cannot_change_retained_oracle`,
    `test_actual_admission_is_two_run_deterministic_idempotent_and_no_rebuild`,
    and `test_immutable_existing_manifest_conflict_is_not_repaired`. Each failed
    at launcher `_independent_pyc_inventory` on the same retained later-wave row
    `src/scouting/contracts/__pycache__/evaluation.cpython-312.pyc`, mapped to
    source `src/scouting/contracts/evaluation.py` outside the frozen W04 source
    roster. This is the backlog condition, not a proposed control weakening.
- command: `test -s reports/reviews/W10/returns/W10-RUNTIME-HARDENING-SURVEY-00B-R1.md`
  - exit status: `0`
  - result: the required return exists and is nonempty (`379` lines before this
    final result correction).

## Artifacts/evidence

- `reports/reviews/W10/returns/W10-RUNTIME-HARDENING-SURVEY-00B-R1.md`
- `reports/verification/W04/w10-deferred-runtime-host-state-hardening-backlog-R1.md`
- `reports/verification/W04/wyscout-runtime-control-R12-terminal-gate-blocker-correction-master-acceptance.md`
- `reports/reviews/W04/wyscout-runtime-control-independent-review-R12.md`
- `reports/verification/W04/wyscout-terminal-complete-repository-gate-R2-master-verification.md`
- Reproduced audit-only later-wave cache row:
  `src/scouting/contracts/__pycache__/evaluation.cpython-312.pyc` (identified by
  no-follow metadata traversal in the failing W04 collector; not read or hashed
  by this survey).

## Risks

- The current W04 unit acceptance command is not green in the evolved W09/W10
  tree because the retained launcher treats a later-wave PYC metadata row as an
  unclassified authority failure. Cleaning it would conceal rather than solve
  the backlog and is not authorised.
- A generic allow rule for all same-tag unmanifested PYC would weaken
  `test_unmanifested_source_pytest_pyc_is_rejected_by_child_and_launcher` and
  could blur source authority. The proposed exact accepted-later-wave audit
  roster avoids that weakening.
- Removing device/inode checks from guarded source, executable, entrypoint or
  runtime-prefix operations would create a substitution window. The proposed
  projection is limited to already zero-read/use cache inventory rows.
- Raw audit inventories and completion receipts remain host-specific. That is
  acceptable only while they are explicitly non-product evidence and their
  security-policy projection is separately deterministic.
- TMPDIR/HOME/PATH/UV/cache-root portability is not solved by `05A`. It requires
  a separately bounded proof; arbitrary environment-path acceptance is unsafe.

## Follow-up items

- Dispatch `W10-RUNTIME-HOST-STATE-HARDENING-05A-R1` with the exact scope and
  checks above.
- After `05A` passes independent review, decide whether a separate `05B` is
  needed for the pilot host matrix. Do not fold broad environment-path changes
  into `05A`.
- Master must independently rerun the full W04 unit file and the companion
  contract/security/e2e checks; this survey does not self-approve.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; `pyproject.toml`
  and `uv.lock` were not edited.
- no edits outside `allowed_paths`: confirmed; only this return file was added.
