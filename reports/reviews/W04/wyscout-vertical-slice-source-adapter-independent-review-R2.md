# W04 vertical-slice source adapter independent review R2

Date: 2026-07-31

Verdict: `PASS`

Open findings: `P0=0`, `P1=0`, `P2=0`.

The exact R2 candidate closes R1's mutable `raw_tags` path without changing the
accepted action-frame, period-membership, source-member or completion-index bytes. The
adapter remains suitable for the bounded, memory-resident W04 vertical-slice source
boundary. This review does not authorize product construction or publication.

## Fixed-binding verification

Every packet binding was verified before candidate analysis.

| Binding | Expected SHA-256 | Observed SHA-256 | Result |
| --- | --- | --- | --- |
| implementation | `b1cdb309c3d81e7a3b0606987fdf6c456d61a66c393ca681d93e212e805ac43c` | same | PASS |
| source-adapter tests | `1acb8908bd2cbb11a4f9e1d3d25ed270e5781c11e0cc6fa0c94b97d486e064f4` | same | PASS |
| R2 producer return | `5b9fc93d2f9cd0d2e896a4fb55df3da2959b01c3b59515e65acd7d3aa48e1df9` | same | PASS |
| accepted completion index | `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df` | same | PASS |

The independently checked England member remains exactly `188888614` bytes with
SHA-256 `301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad`.

## R1 correction review

- `_raw_tags_and_projection` first admits only an exact list of exact dictionaries
  whose sole `id` value is a strict integer. Each admitted ID is then copied into a
  new dictionary exposed through `MappingProxyType`; the returned container is a
  tuple. It neither retains the source tag dictionary nor exposes a normal mutation
  method.
- `_canonical_value_text` accepts the proxy representation only for the sole-key
  `{"id": strict_int}` shape. All other proxy shapes or non-integer IDs fail closed,
  while the admitted representation emits the original canonical JSON bytes.
- A fresh public-boundary probe loaded the exact 1768-action match, selected an action
  with tag evidence, and attempted
  `tagged.evidence.raw_tags[0]["id"] = 999999`. It raised `TypeError`.
- The same authentic checked capability was used after that failed mutation. It
  independently revalidated exact periods `1H=901` and `2H=867`, with membership
  digests `473174accd75001471b64844afb2e49a88fee1c880c7e4818d26f02f1887b91b`
  and `b9b2ef109ffc68aca6c5f218e4c74269378c62ed44b2d9dcacc58eca04be8c16`.

R1's P1 is closed.

## Public-state immutability inspection

The reachable returned graph was inspected rather than relying only on the candidate
test:

- `VerifiedMatchPopulation`, `VerifiedMatchAction`, `CompletionActionEvidence`, the
  completion-index rows and their member/period rows are frozen slot dataclasses.
- Public collections in those values are tuples; canonical raw rows are bytes.
- `_immutable_json` recursively maps every source dictionary to a mapping proxy and
  every source list to a tuple, admitting only immutable JSON scalars. A direct nested
  mutation of the selected player's
  `raw_record["positions"][0]["x"]` raised `TypeError`.
- Evidence tag dictionaries are independently copied proxies, and projected tag IDs
  are a sorted tuple. No mutable source object remains reachable through the normal
  public raw/evidence path.
- `CheckedCompletionPopulation` exposes only reverified sequences; its registry record
  contains tuples, the sequence contracts inherit the frozen contract base, and their
  nested action collections are tuples.

No additional mutable public object path or open P0-P2 finding was identified in the
packet scope.

## Independent vector reproduction

The reviewer reconstructed the packet's representative source action independently,
including the string `subEventId`, duplicate raw tags and strict integer identities.
The observed values were:

- action-frame length: `595` bytes;
- action-frame SHA-256:
  `5b94fec338d67564aa16e37b8eb60ec70995182c8a7dc1bd5d02c1e32b83ca4e`;
- one-action membership SHA-256:
  `c245045382071ae38bf26557b2acb16282db1997e0fbaf50a9a9faafc8ba6d21`;
- accepted stored index SHA-256:
  `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`.

All are byte-identical to the packet bindings.

## Acceptance checks and evidence

- `shasum -a 256 src/scouting/sources/wyscout_completion_index.py tests/unit/test_wyscout_source_completion_index.py reports/reviews/W04/returns/W04-VERTICAL-SLICE-SOURCE-ADAPTER-01-R2.md`
  - exit `0`; all three fixed candidate hashes matched.
- `shasum -a 256 data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json`
  - exit `0`; the stored index rehashed to its accepted content address.
- `wc -c data/source/wyscout/v5/archive-members/events_England.json`
  - exit `0`; observed `188888614` bytes.
- `shasum -a 256 data/source/wyscout/v5/archive-members/events_England.json`
  - exit `0`; observed the accepted member digest.
- `uv run pytest -q tests/unit/test_wyscout_source_completion_index.py -k 'action_projection or verified_match_adapter or verified_member_reader'`
  - exit `0`; `17 passed, 36 deselected in 3.32s`.
- `uv run python scripts/verify_local_only.py`
  - exit `0`; `PASS`, 25 controls and zero failures.
- read-only inline `uv run python -c` public mutation/vector probe
  - exit `0`; both mutation attempts raised `TypeError`; capability reuse, exact
    period counts and digests, frame hash, membership hash, index hash and 1768-action
    cardinality all matched.

The first inline-probe composition attempt exited `1` with a local quoting
`SyntaxError`; the corrected invocation initially exited `2` because the sandbox could
not inspect the existing uv cache, then ran read-only with the required sandbox access
and exited `0`. Neither failed attempt imported the candidate or changed repository
state.

## Boundary confirmation

No implementation, test, data, authority, product, dependency or lock byte was edited.
No provider or network acquisition, Git mutation, cloud resource, container, hosted
CI, endpoint, remote or deployment action occurred. The local-only verifier reports
zero configured remotes and no prohibited local-boundary artifacts.

## Review conclusion

`PASS`. R2 has zero open P0-P2 findings. The exact candidate may return to the master
for independent master acceptance; only the master may authorize downstream use.
