# W04 bounded season-and-lineup correction authorization R1

Date: 2026-08-01

The user explicitly authorizes one additive W04 product-binding correction and
requires every previously frozen authority byte to remain unchanged.

## Exact authorized season binding

- source field/value: strict integer `seasonId=181150` from the exact selected
  match row `matches_England.json#379`;
- source namespace: UUIDv5 of `NAMESPACE_URL` and
  `urn:scouting-intelligence:source:wyscout-soccer-match-events-figshare-v5`;
- season namespace: UUIDv5 of that source namespace and `season`;
- canonical name: `figshare-v5:181150`;
- canonical season UUID: `4696aa1f-b512-5d18-af79-33cf031455cf`.

This is a bounded product binding. It does not add a season identity-bundle
kind, identity row, schema root or second derivation.

## Exact authorized lineup population

Emit exactly one Silver lineup stint for:

- match source ID / UUID: `2499719` /
  `bad97950-6fac-5cf0-a93c-094f91abbb9b`;
- team source ID / UUID: `1631` /
  `5b353635-819b-5bd1-8ca2-5a7364042a96`;
- player source ID / UUID: `285508` /
  `be8da881-2b15-513f-978f-6bb3865bc8e2`;
- zero-based stint ordinal: `0`;
- ruleset version: `w04-wyscout-lineup-stint-v1`;
- deterministic lineup-stint UUID: `591cdf5b-2281-53c4-8225-150313ca2c01`;
- start interval: `[82,83)`;
- terminal/end interval: absent;
- right-censored: `true`;
- lower/upper/elapsed minutes: absent;
- per-90 eligible: `false`;
- suppression reason: `suppressed_unsupported_denominator`.

The lineup-stint UUID is UUIDv5 of the documented Wyscout match namespace and
`stint:1631:285508:0:w04-wyscout-lineup-stint-v1`.

## Boundary

The correction must add no identity-bundle kind, schema root, supported feature,
Gold row, match, player, team, season, action or possession population beyond the
values above. It grants no provider access, dependency, remote, cloud, container,
hosted CI, endpoint, deployment or publication permission.

The future product may bind the accepted correction digest only through the
already-frozen `authority_rows` member of the 25-key build projection. The
projection roster and single build hash remain unchanged.

Fresh independent review and master acceptance are mandatory before downstream
implementation resumes. Stop if any implementation requires a wider semantic,
population, schema, feature, identity, architecture or local-only change.
