# W04 field semantic v2 independent review R1 — master rework verification

## Decision

`REWORK`. The authority merits and canonical record pass, but the review's
progression narrative contains one P2 evidence defect.

## Complete readback

The master read all 346 review lines and all 61 return lines.

```text
review
bytes: 25985
lines: 346
physical SHA-256:
b51660a1037c4340994653689f6057a73c22f7e1f0dad4bcd7991ff5066f7231
canonical fenced review-record SHA-256:
f4d1f95674b5ef82527b19ef4ad6da5890fe38e1b3c78eb2518ff0825bb43d9f

return
bytes: 3229
lines: 61
physical SHA-256:
b962a7a891e751237e1675b808c34d7c070fbd4eea14e3a72452bfb58f083cc5
```

The fenced body is strict canonical JSON, binds the exact candidate and
decision hashes, uses the fixed independent reviewer actor and a truthful
post-decision clock, and records `PASS` with `findings: []`.

## Passing evidence

A fresh locked sync resolved 83 packages and audited 82. With the review
present, the exact combined suite passes `271 passed in 37.54s`; all 25
local-only checks pass. The review independently reconstructs the 119-row
authority, sole delta at index 106, 36 taxonomy pairs, strict no-coercion
boundary, seven reasons, v1 immutability, canonical bytes, digest edges,
review/acceptance progression, and product absence.

## P2 defect

The progression section says R21 still requires separately reviewed and
accepted product-contract and schema-bundle authorities and describes their
bytes as later candidates. That is not the accepted R21 graph:

- both are inert sibling control preimages;
- their fresh independent review and master acceptance are already complete;
- R21 defines no later acceptance JSON packet for either; and
- the remaining serial work is field-v2 acceptance, possession-v2
  decision/review/acceptance, feature decision/review/acceptance,
  cross-authority test/review/master gate, and the complete repository gate.

The same section also refers to nonexistent future v3 review/acceptance paths.
Those claims must be removed so the evidence cannot redirect orchestration.

## Preservation

Before rework, the master copied the exact failed R1 review and return bytes to:

```text
/private/tmp/W04-FIELD-SEMANTIC-V2-REVIEW-01-R1-failed/
```

Their hashes match the values above. The repository R1 return and this master
decision remain durable historical evidence. No candidate, test, authority,
dependency, Git, downstream, or product state changes.

## Rework boundary

R2 corrects the progression narrative and canonical review clock only, reruns
the bounded checks, and writes an R2 return. Candidate and test bytes are frozen.
