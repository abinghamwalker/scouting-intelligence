# W04 repository progression guard independent review R1

Date: 2026-08-01

Decision: `REWORK`

Finding counts: `P0=0`, `P1=1`, `P2=0`.

Reviewer actor: `dc583a8b-015b-51a2-922c-84c76dac3564`.

## Candidate and fixed bindings

Every packet-fixed physical SHA-256 reproduced before analysis:

- field fixture: `c254430b6bafcb378896636d2c22c51080c69f83c666b0e79fb0162afd84f99d`
- possession fixture: `eb56aaa34838f2d28eeb7d6a1f1e8f5cc56ab5a52eeab44fd82ebfd5e2158a94`
- R2 producer return: `9a25ea7f4b849a48a8d9eaecee8a92df7baf39aa20a9f8c336f523c325ac542e`
- master verification: `9145d6db017976eb03ca2e629a48bffddcc5f4dd667fa350aff83171ffb5591a`
- accepted gate report: `656769e7e9fe894421056230344ed9e976d583895cabe42600d1a2294042e14e`
- accepted gate return: `8f45128b4609b2a575a9f7da5e147dd95c5ef83f203812d27ac97e6fbd9eb051`

The exact present four-path evidence succeeds in both helpers. Both fixtures retain
their lower-authority candidate, review, acceptance, clock, actor, digest and
progression validators. Their governed path tuples remain present. The central R21
lifecycle continues to own the complete pre-gate/product boundary and remains in the
focused suite.

## P1 finding: paired review and gate-record substitution is accepted

Code: `PROGRESSION_GATE_PAIRED_REVIEW_RECORD_SUBSTITUTION`

Both `_validate_exact_r21_gate_evidence` helpers bind the report and return to their
accepted physical digests, but bind the review only to the caller-supplied gate record.
They do not bind either the review or gate record to its accepted physical digest.
Consequently, a caller can replace the complete review bytes, recompute
`review_physical_sha256` in a new canonical five-key gate record, replay the accepted
report and return bytes, and obtain acceptance. This violates the review requirement
that changed or stale evidence cannot make either helper accept; it also leaves the
fixed report's claimed review digest unreconciled with the supplied review.

Independent executable attack, run against each module:

```python
evidence = module["_present_r21_gate_evidence"]()
evidence[review_path] += b"forged replacement review bytes\n"
gate = module["_load_canonical_json"](evidence[record_path])
gate["review_physical_sha256"] = sha256(evidence[review_path]).hexdigest()
evidence[record_path] = module["_canonical_json_bytes"](gate)
module["_validate_exact_r21_gate_evidence"](evidence)
```

Observed result:

```text
field:combined-review-record-substitution:ACCEPT_UNEXPECTED
possession:combined-review-record-substitution:ACCEPT_UNEXPECTED
```

Cross-wired report/return values, duplicate gate-record keys and an additional copied
gate-record path were independently rejected in both modules. All 15 declared
mutations in each fixture also rejected individually, so the defect is specifically a
missing combined-substitution invariant rather than a failure of those single attacks.

## Bounded rework required

In both authorized fixtures, bind the supplied complete review to the already-accepted
physical SHA-256
`e9eca309986140ddfe40c66645a3f640777ff700e6a7187d43f020060d35c070`.
Because the gate JSON is strict canonical JSON and its other four values are exact,
requiring that digest also fixes its exact accepted content. Binding the exact accepted
gate-record physical SHA-256
`980303642f5c58876ed157698a5ea8f25ee79acef3c9faeaf015266cf547f168`
is acceptable additive defence. Add the paired review-plus-record substitution as a
direct adversarial case in each module and preserve every existing 15-case attack.
No production, authority, gate, data, dependency or product byte needs to change.

## Reproduced checks

- Ruff format: PASS, two files already formatted.
- Ruff check: PASS.
- focused three-module suite: PASS, `357 passed in 23.14s`.
- explicit 15-case roster in both fixtures: PASS, `30 passed in 0.07s`.
- local-only verifier: PASS, 25/25 controls; zero configured remotes.
- fixed candidate hashes after execution: unchanged.

The passing prescribed suite does not close the paired substitution demonstrated
above. The exact R2 candidate therefore receives `REWORK`, not acceptance.

## Machine record

```w04-repository-progression-guard-review-v1
{"finding_counts":{"P0":0,"P1":1,"P2":0},"recommendation":"REWORK","review_id":"w04-wyscout-repository-progression-guard-independent-review-R1","review_path":"reports/reviews/W04/wyscout-repository-progression-guard-independent-review-R1.md","reviewed_by":"dc583a8b-015b-51a2-922c-84c76dac3564"}
```
