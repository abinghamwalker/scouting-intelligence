# W04 loaded-runtime subset and completion-evidence correction authorization R1

- Date: `2026-08-03`
- Governing authority: standing bounded-correction authority dated `2026-08-02`
- Effective design: R20 with R21's declared replacements
- Decision: **AUTHORIZED_FOR_SERIAL_PRODUCER_REVIEW_MASTER_REWORK**

## Defect

The accepted logical runtime rule is `R subset-of L`, where `R` is the actual
post-execution set of normalized loaded owners. The current admission helper
validates a partial `sys.modules` view but returns no observation, while the
rebuild child populates `FinalRecheckResult.runtime_subset_digest` with the stable
`installed_record_runtime_digest`. That value represents the complete installed
closure `I`/selected closure `L`, not actual loaded `R`. The existing final field
therefore has the accepted name and intended meaning but the wrong value.

The current outer completion also discards child-private observations already
validated inside the launcher: entrypoint descriptors, child input/result
bindings, result-frame/EOF state, diagnostics, timeout/exit state, and child
prefix checkpoints. R20 Section 10 requires these observations and exact
two-root comparison, so a truthful health artifact cannot infer them later from
another process.

## Smallest sound physical correction

`PreBuildAdmissionResult`, the pre-build projection, rebuild invocation, published
invocation receipt, build-ID formula, logical W04 schemas, 23-root roster, product
population, source authority, data-rights authority, and digest meanings remain
unchanged. Actual loaded `R` remains operational post-execution evidence and must
never become an admission, environment-manifest, projection, build, or product
input.

The serial R12 correction is authorized to:

1. create one nested non-root `RuntimeSubsetObservation` contract with exact
   ordered fields `observation_kind`, `owner_name`, `owner_version`,
   `site_relative_path`, and `subject_name`;
2. collect one terminal, sorted, unique, bounded observation tuple over admitted
   site-package module sources, native extensions, valid namespace contributors,
   and RECORD-owned loaded site shared images;
3. bind the tuple by
   `SHA256(canonical_json({"algorithm":"w04-normalized-runtime-subset-observations-v1","rows":rows}))`;
4. require the unique `(owner_name, owner_version)` projection to be a nonempty
   subset of the frozen selected closure, with no retry, selection expansion, or
   rescan that could grant authority;
5. add `runtime_subset_rows` to final recheck immediately after the existing
   `runtime_subset_digest`, preserve that digest's intended meaning, and require
   independent launcher validation of every owner/path/version and current file
   against frozen RECORD authority;
6. retain exact child-private process observations plus the byte-identical final
   R rows/digest in canonical outer completion status for master retention and
   health/two-root review; and
7. regenerate only mechanically derived physical result descriptors, predicate
   ledgers, tests, code/environment schema literals and unaccepted derived
   digests required by that corrected wire.

The fixed physical versions are:

```text
installed runtime-subset policy:
  operational-R-subset-L-normalized-observation-v2
FinalRecheckResult:
  w04-rebuild-final-recheck-v2
ChildResultEnvelope:
  w04-child-result-v3
code/environment manifest:
  w04-code-environment-admission-v16
outer completion:
  w04-local-control-completion-v2
```

Frame magic/version, child-input v1, pre-build projection v1, rebuild invocation
v1, and published rebuild-invocation receipt v1 remain unchanged. The stable
child-result contract component binds the new physical schema and algorithm, but
actual R rows stay outside stable identity.

## Required rejection and positive proof

Fresh producer and independent-review packets must cover omission, insertion,
reorder, duplicate, digest-only drift, coherent row-plus-digest substitution,
unknown/null/mistyped kind, absolute/unsafe/non-NFC/symlink/PYC origin, external
origin, invalid namespace ownership, unowned or mutated shared image, duplicate,
lock-only, installed-only and version-mismatched owner, stale physical schema
literals, completion-row order/binding mutations, and two-root R mismatch.

Positive live evidence must bind `pydantic_core` to `pydantic-core` and
`_polars_runtime_32` to `polars-runtime-32` whenever those native modules are
loaded. A changed R may change only terminal completion evidence; it must not
change the stable manifest, projection, build ID, logical product population or
digest formula.

## Progression

R11 first closes R21's exact ordered 30-resource authority. Only after R11 fresh
independent review and master acceptance may R12 implement this correction. R12
then requires its own fresh independent review and master acceptance, followed by
two new real-root runs, fresh independent raw-to-Gold/runtime review, master
acceptance, and health/card/gate/checkpoint progression. Existing R2/R3 runs and
their independent PASS remain immutable retained superseded evidence.

This correction supersedes an accepted physical result descriptor because doing
so is necessary to satisfy the stronger already-accepted logical R meaning and
evidence guarantees. It does not cross a user-boundary condition.
