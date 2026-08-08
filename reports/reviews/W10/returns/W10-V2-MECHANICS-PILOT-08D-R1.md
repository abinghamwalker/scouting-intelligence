# W10-V2-MECHANICS-PILOT-08D-R1 preparation return

## Status

- Packet state: **READY FOR HUMAN EXECUTION**
- Pilot execution: **NOT STARTED**
- Eligible reviewers: **0**
- Human sessions/judgements/completions: **0 / 0 / 0**
- Decision: **PENDING HUMAN EVIDENCE**

This is a preparation handoff, not the packet's final implementation return. It does not satisfy
08D's definition of done and cannot authorise 08E.

## Prepared files

- `data/working/w10/study/v2/pilot/mechanics-pilot-authority-v1.json`
- `data/working/w10/study/v2/pilot/pilot-pack-separation-v1.json`
- `reports/verification/W10/v2-mechanics-pilot.md`
- `reports/reviews/W10/returns/W10-V2-MECHANICS-PILOT-08D-R1.md`

The five participant tasks cover GK, DF, MD defensive, MD shooting and FW. The participant
authority contains no protected retrieval provenance. The separate operator-only manifest reserves
all ten pilot grains and canonical players out of the future formal pack and must never enter
browser bytes.

## Preparation verification

- Participant authority: 1,604,378 canonical bytes; SHA-256
  `33684b88c683b8e565757972ab78e558a0e29dfad7ddcb94fd659dfb631a4791`.
- Separation authority: 5,714 canonical bytes; SHA-256
  `559a40c5adc7f803dfb017e26ec35d3cfdcd7f3c3de4ba4dd3e4b04c5f31c1e4`.
- Five comparison contracts validated under the exact accepted policy; all comparison digests are
  unique.
- Forbidden participant key/value scan: empty.
- Pilot/v1 frozen-pack grain intersection: empty.
- Ten pilot grains and ten canonical players are explicitly excluded from every future formal
  pack.
- Both prepared files are non-symlinked, single-link regular files with mode `0444`.
- A production-equivalent store loaded the authority; `/w10/v2` rendered, formal/approval routes
  returned 404, and no SQLite database was created.
- The complete repository gate passed **3,091 tests** with one upstream TestClient deprecation
  warning before this human handoff.

## Human blocker and continuation

At least two distinct eligible football-domain reviewers must each complete all five tasks and the
required debrief. Start locally from the repository root with:

```text
caffeinate -d uv run --no-sync python services/api/w10_study_main.py
```

Open `http://127.0.0.1:8771/w10/v2`.

The complete eligibility, operating, debrief, denominator and GO/REWORK rules are in
`reports/verification/W10/v2-mechanics-pilot.md`. No human response has been fabricated or
automated. Formal v2 remains disabled, v1 approval is not reused, and this return claims neither
08D acceptance nor W10 acceptance.

## Remaining risks

- Authentic reviewer availability is outside engineering control.
- Opportunity thresholds remain preregistered pre-pilot measurement rules and require the retained
  stability validation before any formal freeze.
- The future formal pack does not exist. A6 must prove an empty grain and canonical-player
  intersection with the protected pilot separation authority before freeze.
