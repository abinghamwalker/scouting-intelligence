# W04 source-completion-index R3 capability/security independent review R1

## Disposition

- Packet: `W04-SOURCE-COMPLETION-INDEX-REVIEW-02-R1`
- Role: independent capability/security reviewer
- Disposition: **REWORK**
- Open findings: P0 `0`, P1 `1`, P2 `0`
- Acceptance rule: PASS requires zero open P0-P2 findings.

The ordinary checked-builder route closes the R2 direct-constructor bypass, but the
R3 identity-only capability design is not an authority boundary against an ordinary
Python caller. Standard callable introspection exposes the retained completion and
product issuer callables, while retained getter closures expose both backing
registries. The lower-level issuer accepts caller-supplied records without executing
the accepted completion-reader comparison. A raw semantic value can therefore be
registered as an authentic checked product and accepted by `require_checked_product`.

This is a practical checked-authority forgery, not a naming or documentation concern.
Product implementation must remain blocked.

## Fixed candidate identity

Every packet binding was recomputed before analysis and matched exactly:

| Material | Expected and observed SHA-256 | Result |
|---|---|---|
| `src/scouting/sources/wyscout_completion_index.py` | `22d825631af0d27d1583a79ce4bb8adb10643bb32fe139630871727f814f1415` | match |
| `src/scouting/contracts/wyscout_data.py` | `154f1ae9934615a2ce9a24a4f8e373cd640a4c3246df93f0e35e6bed28517932` | match |
| `tests/unit/test_wyscout_source_completion_index.py` | `5beb37ee5fffadcab1d7355b879fcb65b76816b969c5581a943b1096afd98580` | match |
| `tests/contracts/test_wyscout_data_contracts.py` | `7ef542d5ed65437683063e2980e08a94b260771405147a860ca5d4541f1c004b` | match |
| immutable completion index | `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df` | match |
| R3 producer return | `e9ff75d989e605f70aeed77d85913092a95bbe98d5fc83852ec51651671a8ce9` | match |

No drift stop condition was reached.

## Independently confirmed closed routes

The focused suite passed and the implementation inspection confirms the following
ordinary documented routes fail closed:

- Direct `CheckedCompletionPopulation()` and `CheckedProduct()` construction is
  rejected.
- An unregistered `object.__new__` handle, subclass/type substitution, and a raw
  contract object are rejected by the exact-type and registry-identity checks.
- `copy`, `deepcopy`, and pickle serialization/replay of issued handles are rejected.
- Direct Pydantic construction, `model_validate`, dump-copy, an arbitrary membership
  digest, and a copied real membership digest remain
  `semantic_only_unchecked`; passing those raw values to `require_checked_product`
  fails.
- The public `validate_checked_period_population` and
  `validate_checked_match_population` routes call the exact accepted population
  validators before normal issuance. The normal Fact boundary requires the
  `complete_match` state, and normal Action, Possession, Fact, Gold and manifest
  builders retain completion identity through their checked handles.
- A detached raw `.value` is not itself accepted by checked builders or
  `require_checked_product`. Consequently, any future serializer must accept an
  authentic checked handle and call `require_checked_product` immediately before
  serialization; accepting a detached value would recreate the original bypass.

These controls are necessary, but they do not close issuance-state extraction.

## Open finding

### W04SCIIDXR3CAPR1-P1-001 — introspectable issuance state permits checked-authority forgery

`_capability_registries` creates completion and product issuer/getter closures over
two `WeakKeyDictionary` registries at
`src/scouting/sources/wyscout_completion_index.py:260-309`. The module then binds the
completion issuer into the public checked-validation callables at lines `1060-1087`
and binds the product issuer behind the public checked builders at lines `1415-1524`.
Deleting the two module-global issuer names at lines `1526-1527` does not remove the
issuer objects retained by those callable closures.

The getters remain module attributes and retain direct references to both backing
registries at lines `314-327`. The accepted handle classes and record types are
ordinary Python objects at lines `190-245`. The public
`require_checked_product` boundary at lines `1113-1124` trusts the product record
returned by the registry and then returns its raw value; it does not independently
re-execute or verify the accepted population comparison.

A bounded in-process inspection, with no provider or network access and no product
write, observed exactly:

```text
validate_checked_match_population freevars=('issuer',) contents=('function',)
build_checked_gold_player_window freevars=('issue',) contents=('function',)
_get_checked_completion freevars=('completion_records',)
contents=('WeakKeyDictionary',)
_get_checked_product freevars=('product_records',)
contents=('WeakKeyDictionary',)
```

This state is reachable through standard Python callable introspection. The retained
completion issuer accepts a caller-supplied `_CheckedCompletionRecord`, including its
caller-selected `complete_match` Boolean, sequences and period keys, without calling
`validate_match_period_population` or `validate_match_population`. The retained raw
product issuer accepts a caller-supplied value and completion tuple without applying
the checked-builder wrapper's non-empty and authentic-completion checks. Direct
registry insertion is a second route to the same result.

The security consequences cover all required challenge classes:

- A singleton period can be labelled as complete-match authority, bypassing the
  period-versus-match distinction.
- Raw Action, Fact, Gold or manifest values can receive checked registry membership
  without exact reader comparison.
- Checked Action/Fact/Gold scope binding can be substituted or mixed by selecting the
  record's completion identities and period keys.
- A detached raw `.value`, dump-copy, replayed semantic model, or copied real digest
  can be reissued as accepted authority; handle copy/pickle protections do not help.
- `require_checked_product` and a correctly written future serializer would accept
  the forged registered handle, so the prescribed serializer rule is insufficient
  until issuance itself is closed.

The prescribed tests at
`tests/unit/test_wyscout_source_completion_index.py:349-375` and
`tests/contracts/test_wyscout_data_contracts.py:2843-3259` cover direct construction,
unregistered substitution, normal checked issuance, copy/deepcopy/pickle, raw-value
reuse, copied digest and cross-scope checks. They do not challenge callable closure
state or registry extraction, which is why all focused tests pass despite this P1.

Required bounded correction:

1. Replace identity-only acceptance with evidence that
   `require_checked_product` can independently verify as bound to the exact accepted
   index, compared population and exact product scope; an introspectable issuer or
   mutable registry must not be the sole source of authority.
2. Do not treat a deleted or underscore-prefixed module name as access control.
3. Ensure no retained public callable, getter, closure or registry permits ordinary
   callers to register arbitrary completion or product records.
4. Add regressions that inspect callable closure state and registry reachability, then
   prove raw value registration, false complete-match state, detached-value reissue
   and cross-scope substitution all fail.

No provider, dependency, product, data, frozen authority or architecture change is
required merely to identify this defect. The correction itself needs fresh bounded
design review because ordinary Python reflection defeats the current process-local
identity assumption.

## Prescribed-check results

| Command | Result |
|---|---|
| `shasum -a 256` over the four fixed implementation/test files and R3 producer return | exit `0`; all five fixed digests matched |
| `shasum -a 256 data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json` | exit `0`; immutable index digest matched |
| `uv run pytest -q tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_wyscout_data_contracts.py -k 'checked or completion_reader or copied_real_membership'` | exit `0`; `6 passed, 259 deselected in 18.98s` |
| `uv run bandit -q -r src/scouting/sources/wyscout_completion_index.py src/scouting/contracts/wyscout_data.py` | initial sandbox attempt exit `2` because existing shared uv-cache metadata was unreadable; unchanged cache-read rerun exit `0`, no findings |
| `uv run python scripts/verify_local_only.py` | exit `0`; PASS, 25/25 controls and zero failures |
| bounded callable/registry state inspection | exit `0`; issuer callables and both weak registries were present in retained closure state as shown above |

No `model_construct` was used. No dependency, product byte, provider/network, Git,
cloud, container, hosted CI, endpoint, remote or deployment action occurred.

## Recommendation and scope

Recommendation: **REWORK** with P0 `0`, P1 `1`, P2 `0`. Return only
`W04SCIIDXR3CAPR1-P1-001` for bounded correction and obtain fresh independent
capability/security review before the complete repository gate or product work.

- No implementation, test, data, source, manifest, index, frozen authority,
  orchestration, verification, dependency, lock or product byte was edited.
- Only this independent review and its mandatory return were written.
- No Git operation, delegation, self-approval, provider/network access, external
  service, cloud, container, hosted CI, public endpoint, remote, deployment or
  product materialization occurred.
