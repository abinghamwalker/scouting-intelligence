# W04 Wyscout v5 archive-directory preflight

Status: **PASS — authority scope corrected before ingestion**

Date: 2026-07-29

The master fetched the two exact, user-authorised Figshare archive objects to temporary
local storage and inspected their ZIP directory entries only. No JSON member was
extracted or parsed during this preflight.

## Events object

- URL: `https://ndownloader.figshare.com/files/14464685`
- Configured size: `77323413`
- Observed size: `77323413`
- Configured/observed MD5: `7c20e8647e7eda58d7838a0c7b1ec6ab`
- Observed SHA-256:
  `877e015b716ffdeea18f04418e3f24fed307ed03c37ff305cabe1f47c4822a45`
- Directory entries:
  - `events_England.json`
  - `events_European_Championship.json`
  - `events_France.json`
  - `events_Germany.json`
  - `events_Italy.json`
  - `events_Spain.json`
  - `events_World_Cup.json`

## Matches object

- URL: `https://ndownloader.figshare.com/files/14464622`
- Configured size: `645097`
- Observed size: `645097`
- Configured/observed MD5: `51d80beb17480919f69a53a0152c2d71`
- Observed SHA-256:
  `c8f92bb7533e5c127e043cee764c991b5c25b4f5e70a65be931baae0b1765ce9`
- Directory entries:
  - `matches_England.json`
  - `matches_European_Championship.json`
  - `matches_France.json`
  - `matches_Germany.json`
  - `matches_Italy.json`
  - `matches_Spain.json`
  - `matches_World_Cup.json`

## Decision

The five domestic members in each archive remain admitted. The two tournament members
in each archive are now explicitly classified as known `scope_excluded` directory
entries. Their compressed payloads must not be opened, extracted, or admitted during
the first pass. Any eighth or otherwise undeclared entry remains an unknown-member
failure.

This correction narrows extraction to the approved first pass; it does not add a
competition or expand the licence, product claim, local-only boundary, or export
authority.

No credential, account, remote repository, cloud resource, hosted service, public
endpoint, or deployment was created.

