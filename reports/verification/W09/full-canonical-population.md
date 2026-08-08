# W09 full historical canonical population

- Verification date: 2026-08-05
- Status: **PASS — governed canonical input to the feature build**
- Canonical build ID: `72969be11e9a13a3f2c87b92ccff0296e9ab026fdd531383ce67af074740fdb7`
- Canonical manifest SHA-256: `587f696996304c3aea888f12a486afa89e458c7cc68a2fafd5e85d38e004be59`
- Builder: `w09-full-canonical-build-02b-r6-unicode`

This R6 authority supersedes R5 after the retained provider catalogue was found to
contain one textual Unicode-escape layer in player and team fields. R6 decodes exactly
one valid layer, normalises to NFC, and fails closed on malformed, nested or unpaired
surrogate input. It contains zero literal Unicode escape sequences in canonical player
text. The complete correction evidence is in `unicode-correction.md`.

## Reconciliation

The retained source and canonical population reconcile exactly for the product data
universe: 1,826 matches, 3,071,395 actions, 142 teams and 3,603 catalogued players.
The canonical projection also contains seven source competitions, 68,864 appearance
rows and 16 explicit identity-exclusion rows. The 16 exclusions are the 15
review-required non-catalogue lineup identities plus the rejected provider-zero actor;
they are not candidate identities.

The 3,603 catalogued players are the source/canonical identity universe, not the final
eligible matrix count. W09-02C must reconcile all 3,603 through population and
competition-window eligibility ledgers before reporting its eligible row/player counts.

## Physical artifacts

| Role | Rows | SHA-256 |
| --- | ---: | --- |
| competitions | 7 | `c224247a83ed62c519665e6963395ca5b027f0b5672fcda2161ea4424c36abd4` |
| teams | 142 | `02d4712a254736d6b6cbf2f0a0180d970ddf836785ba6e105f0b8d97ac75efe1` |
| players | 3,603 | `a12d0ee17e946ef3551489424284a1b89e4d84cf265a076e9c71e94ede5f0923` |
| matches | 1,826 | `09d4d2e2de8079925e0f00f5bd4d89d0763c7f4558dad92524493cf6eb1b81d5` |
| actions — England | 643,150 | `3602d8af4c59b6b6a49be9ad71a88da37876736f9d3c8b8c02feb11b0a8341fe` |
| actions — France | 632,807 | `aaa1d5ab439bb2051aba9efd63bfe0c16cec6419de7782ed96b5a32ed1a2dffd` |
| actions — Germany | 519,407 | `1b0e5f990e318de3bcd507ed3afa256bb49f257ae9c05e01f6f7d81e1e2d2799` |
| actions — Italy | 647,372 | `4b62f2aae796f6937c98bb7d56d121df47053f0ef42d027f2ec78f2be53e11b4` |
| actions — Spain | 628,659 | `3a0e9777c9c5ecabe6242ae2145876b5e718123adcbd6de613d2855919e8f4f9` |
| appearances | 68,864 | `ea47b6a5f05133e5e0b11151a5d34d2c4132f91be56b2c57f3464cb03d69baa2` |
| identity exclusions | 16 | `24b4f5966415f829d10e22f8ec4323f848c926ff33d102765d8738030438a3fc` |

Every named Parquet was opened through PyArrow, its row count and schema were read,
and its bytes, size and completion receipt were reproduced against the canonical
manifest. The 11 artifact entries contain five partitioned action files. The manifest
completion receipt reproduces the manifest hash above.

## Identity, missingness and temporal controls

- All 3,603 player-master identities are canonical and resolved.
- Fifteen non-catalogue lineup identities remain review-required and are excluded.
- Source player `0` remains rejected; its 226,038 action rows are retained as rejected
  source evidence and cannot become a candidate.
- All authorities are strictly before the `2026-08-05T00:00:00Z` feature cutoff.
- `currentTeamId` and action presence are not used for historical membership or minute
  inference.
- The exact 7,821 raw empty `subEventId` sentinels are normalised only to the declared
  optional integer-or-null contract.

## Minute evidence

The 68,864 appearance rows reconcile to 10,749 exact, 39,838 conservative-lower-bound
and 18,277 unusable rows. Six exact raw `"null"` substitution arrays are retained as
unavailable evidence: their starters receive only a zero-minute lower bound and their
bench entries remain unusable. Fourteen observed entries later than the event-terminal
fallback use the entry itself as a zero-minute lower-bound floor. Eight Italian
`playerIn=0` substitution occurrences are excluded individually while their eight
distinct nonzero player-out exits remain exact evidence. No silent 90-minute assumption
or action-based minute inference is made.

## Coordinate evidence

All coordinate-independent actions remain canonical. Coordinate coverage may count
only rows in state `valid`. Three raw out-of-range points are preserved and classified:
Germany actions `225765702` and `225765704` have `y=101`; Italy action `198907641`
has `x=-1`. No point or containing action was clamped, nulled or dropped.

## Failed-build disposition

Two earlier fail-closed attempts left content-addressed, unmanifested partial artifacts
under build IDs `0b63b7f...` and `dc65a70d...`. They are ignored local build evidence,
not accepted inputs, and were preserved rather than destructively removed. Only the
fully completed R6 build and manifest named above may be consumed by W09-02C.

## Claim boundary

This evidence closes the canonical source projection prerequisite only. It does not by
itself close G-RW1, which requires the reconciled eligible feature matrix, and it makes
no football-relevance, current-market, recruitment-usefulness or recommendation claim.
