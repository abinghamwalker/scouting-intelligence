# W04 Wyscout real acquisition — master candidate R1

Acquired at: `2026-07-29T15:51:08.598589Z`  
Master evidence recorded at: `2026-07-29T15:51:47Z`

## Candidate result

The one authorised acquisition of the exact frozen Wyscout Figshare v5 source
completed successfully under `data/source/wyscout/v5`.

- Completion manifest SHA-256:
  `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1`
- Completion state: `complete`
- Reviewed source objects: `7`
- Reviewed compressed object bytes: `79,737,225`
- Admitted archive members: `10`
- Admitted member bytes: `911,392,378`
- Directory-only scope exclusions: `4`
- Guarded local footprint: approximately `945 MiB`
- Remaining working files: `0`
- Durable signed-URL tokens: `0`

## Object reconciliation

| Object | Bytes | MD5 result |
| --- | ---: | --- |
| `competitions.json` | 1,209 | exact reviewed digest |
| `teams.json` | 27,404 | exact reviewed digest |
| `players.json` | 1,737,347 | exact reviewed digest |
| `matches.zip` | 645,097 | exact reviewed digest |
| `events.zip` | 77,323,413 | exact reviewed digest |
| `eventid2name.csv` | 1,001 | exact reviewed digest |
| `tags2name.csv` | 1,754 | exact reviewed digest |

The completion manifest records a computed SHA-256 for every object and every admitted
archive member. The acquisition implementation computed exact size, reviewed MD5, and
SHA-256 before persistence and wrote completion last.

## Archive boundary

Each source archive matched the reviewed seven-entry directory:

- five admitted domestic-league members;
- two exact tournament members retained only as central-directory evidence;
- no unknown, duplicate, unsafe, linked, encrypted, or over-expanding member.

Ten admitted payloads were persisted. The four scope-excluded payloads were not opened,
extracted, admitted, or persisted. Their completion records contain directory metadata
only.

## Temporal, rights, and transport evidence

- Frozen source availability: `2020-01-28T14:24:27Z`
- Actual acquisition: `2026-07-29T15:51:08.598589Z`
- Licence: `CC-BY-4.0`
- Source ID: `wyscout-soccer-match-events-figshare-v5`
- The only external operation was the authorised exact Figshare acquisition.
- No account, credential, cloud resource, public endpoint, remote repository, hosted
  CI, container, deployment, or external model call was used.
- The completion manifest contains stable reviewed Figshare source URLs only and no
  transient AWS signature query.

## Exact replay

A second invocation ran inside the network-restricted workspace sandbox and returned:

```json
{"manifest_created":false,"manifest_path":"completion-manifest.json","manifest_sha256":"69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1","source_id":"wyscout-soccer-match-events-figshare-v5"}
```

The replay re-read and reverified the completion document, all seven durable objects,
both archives, and all ten separately persisted admitted members. It created no new
manifest and left the working root empty.

## Acceptance boundary

This is a master implementation candidate, not self-approval. Independent durable-byte,
sidecar, exclusion, replay, temporal, rights, and local-only review is required before
`W04-SOURCE-ACQUIRE-01` becomes accepted or the source profile is used as authority.

