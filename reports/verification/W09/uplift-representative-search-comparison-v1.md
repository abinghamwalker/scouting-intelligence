# W09 Package A representative-search comparison

## Scope

The same fixed five live scenarios were executed before and after the event-9 goal-semantic
repair. Candidate admission and full-population scoring counts are unchanged in every case.
Names below are historical resemblance outputs, not recommendations or player-quality rankings.

## Equal-weight results

| Scenario | Method | Scored | Before top five | After top five | Top-10 overlap |
|---|---|---:|---|---|---:|
| Sirigu → Italy GK | Euclidean | 23 | Perin; Strakosha; Donnarumma; Meret; Berisha | Pepe Reina; Donnarumma; Handanovič; Sportiello; Szczęsny | 5/10 |
| Sirigu → Italy GK | Cosine | 23 | Strakosha; Perin; Donnarumma; Meret; Berisha | Donnarumma; Pepe Reina; Handanovič; Buffon; Strakosha | 5/10 |
| Van Dijk → England DF | Euclidean | 123 | Koscielny; Vertonghen; Mustafi; Matip; Lovren | Koscielny; Vertonghen; Matip; Mustafi; Lovren | 10/10 |
| Van Dijk → England DF | Cosine | 123 | Koscielny; Vertonghen; Mustafi; Matip; Lovren | Koscielny; Vertonghen; Matip; Mustafi; Lovren | 10/10 |
| Kanté → England MD | Euclidean | 123 | Doucouré; Cook; Sissoko; Can; Gueye | Cook; Doucouré; Sissoko; Can; Gueye | 10/10 |
| Kanté → England MD | Cosine | 123 | Delph; Can; Gündoğan; Doucouré; Cook | Delph; Can; Gündoğan; Cook; Doucouré | 10/10 |
| Salah → England FW | Euclidean | 59 | Agüero; Kane; Aubameyang; Gabriel Jesus; Sterling | Agüero; Kane; Aubameyang; Gabriel Jesus; Sterling | 9/10 |
| Salah → England FW | Cosine | 59 | Agüero; Son; Welbeck; Kane; Lacazette | Agüero; Son; Welbeck; Kane; Gabriel Jesus | 9/10 |
| Messi → France FW | Euclidean | 72 | Thauvin; Neymar; Depay; Mbappé; Malcom | Thauvin; Neymar; Depay; Mbappé; Malcom | 9/10 |
| Messi → France FW | Cosine | 72 | Neymar; Thauvin; Depay; Malcom; Mbappé | Neymar; Thauvin; Depay; Malcom; Mbappé | 10/10 |

The goalkeeper changes are the intended response to removing a feature contaminant; no GK churn
threshold was preregistered. All non-GK cases exceeded the 8/10 rejection guard.

## Kanté defensive sensitivity

The defensive profile leaves attacking features at 0.5, defensive-event features at 1.5 and the
other declared inputs at their frozen values. Before and after the repair, Euclidean sensitivity
retains 8/10 with N. Matić and E. Dier entering; cosine retains 9/10 with Ander Herrera entering.
The repair did not silently change the weight profile.

## Live post-uplift experiment

- Experiment: `7b406aa1-f2f5-506a-89e2-9be868a2cfd1`
- Label: `Automated post-uplift representative check 2026-08-07`
- Scenario: Messi exemplar targeting French forwards, Euclidean, equal weights
- Experiment digest: `a41d30511336a44552de0666b87d7caf0b23bac2a15da4a1ef3be79dce13bf41`
- Result digest: `2a3cdbc85911e5e3614cb38784f701a2b17c19451278c3ba58bfc5bd3e176b2b`
- Comparison digest: `3456e33c1a61b2511431932245d00be2a608c4fc4b5db7227aa41fc524f4e4d5`
- Report digest: `4f24eb68880020db4625fac0a50caff947b62a843356fb843a0c7c417c2b31a3`
- Replay receipt: `2688f87407d6c765acdaa2354fc9bd6f76eb1e7a787b4bb421f3d1e99ca5bfa5`
- Replay status: `REPRODUCED`

The exact report bytes were loaded through the governed store and the saved query reproduced the
same result identity and digest. No synthetic row was exposed.

## Production browser witness

The one-command launcher was exercised at `127.0.0.1:8879` and then stopped with `Control-C`.
Headless Chrome verified the exact live matrix/index identities, the expanded raw-value/scaling/
distance explanation, and the Sirigu goalkeeper query under both methods. It observed 23 scored
rows with the same post-uplift top three shown above. Browser console warnings/errors, page errors
and non-loopback requests were all empty.

An initial witness found Chrome's automatic `/favicon.ico` request returning 404. A bounded 204
loopback favicon route and regression assertion closed that presentation defect; the repeated
production witness was clean.
