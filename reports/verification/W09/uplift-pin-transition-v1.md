# W09 Package A pin-transition evidence

## Single authorised cascade

Exactly one production tier-2 cascade was performed: matrix → index → W09 evaluation → affected
W10-derived technical authority. Canonical artifacts were not rebuilt and scorer code was not
changed.

| Authority | Pre-uplift | Post-uplift |
|---|---|---|
| Dataset version | `2d018b617d870579be1acfa76a22ae1d6d184071feaa658f353b162e421bee6e` | unchanged |
| Canonical-build digest | `0105267ae0f107a63fad33b24adecdb3c4bb2e900bdf79a505e9ad4af6264b43` | unchanged |
| Feature registry digest | `bafccabfb64c347b72f5c9766b129baeac20784c0a577143552cf7259925623b` | `f026ae50ed361790f52d4b5a3a73595c2a9f2b23e5164b2ffd19860fca7464d3` |
| Matrix version | `w09-historical-player-window-v1-ad74298cf718d6f6` | `w09-historical-player-window-v1-a9f7cc2d5fc12ea0` |
| Matrix digest | `49bf6f72d2e564fa5c421c2eb36f70ceb57810a44c1442da9e14a3db6b799bb9` | `20752d615978eb908a313dff346bff258a255602dff639c520e3dc45cb29bb42` |
| Matrix manifest digest | `45e122d2a8a06ecdf6c7d0cf35c48e8866a96b2c8e124b2f164ad3892a1c9aa3` | `41e5c6d767d64f510718df912e71c26e55509ad8f9f1799ba0270837ee637f6a` |
| Index ID | `97ed622c-3806-5095-9a3a-e32e457f6ba7` | `ff55b286-935c-55c4-bb8e-814a95962b41` |
| Index manifest digest | `f4a9e692336d152938319193a5f5c7cf28cb406da4aa71ca881eae5e0c8fe7c0` | `b805bd66db988d2db79128c1700ef1134191a717980a4a87af8ea3a779e6e580` |
| Catalogue digest | `07e976fd70bd773bafc143ae59f193e60f4a38be5b0dfb80397e77d64861e3a1` | `6f1973ec54c643dc6437c0b3e7670c3d9bea7aaf5671b1583008215f74694003` |
| Scorer digest | `535e244720b7abd46ac25e7de6f3ac387247d4213a00b4857e08acc19e19fc1c` | unchanged |
| W09 frozen suite | `786ac9e7b1161965d8c5f0680f5096e4ff0c08453cdda19806e10e406d0432a2` | `6a2630c3766d4762c12fc5ebf74e1fbfd43b4c2aa11b55847615c3c34e896a84` |
| W09 frozen result | `2c58d59abc0f1f0ac4b3495a5aa682bea637cfaf4e400300f0b5c5d43b3c3e47` | `5dd3cf9bd0cf20ae689c121fdf05471b930836c09b2a4bea4b8bb43729ae7e90` |
| W10 v2 policy digest | `e2ee046a037eaed710e41796ed247897d4c8810443d84b73f8ef4607704756af` | `867ea773892b4bfb8dc33b0ccc3f141ae1c04027d19b6ebe2fad8e0f47468a9d` |

The W09 frozen evaluation result file SHA-256 is
`dff2d6568797474b7e05a0ee05b25d0d1b237342d7e1f9fb10696c66bf6f3747` and was byte-identical
to a clean temporary evaluation output.

The previous matrix manifests and index remain under explicit `archive/` paths; they were not
rewritten. No canonical tier was rebuilt and no unaffected W10 v1 or mechanics-pilot authority
was reissued.

## W10-derived technical authority

The current presentation-v2 policy was re-pinned only to the new matrix version/digest and its
self-digest. The threshold object SHA-256 remained
`b916567afa00a941353030f753a08d7bcde9c57810b52870d48ec68db9aa983c`; the complete threshold
policy projection SHA-256 remained
`a4e2d6d6392de6e2721e303507b7c20db8eaa99c1e255918a6ebdc4320d0fb23`.

Two clean temporary W10 v2 comparison bundles were byte-identical:

- file SHA-256: `77308b431a0d9cdf55aea9151e3b8509401b9cd7fae13030feb8425ca20faf23`
- comparison digest: `1dbd32798121bc2d27907f4620507c6b14a0099ec2fb80b4c77f70e020098a12`
- policy digest: `867ea773892b4bfb8dc33b0ccc3f141ae1c04027d19b6ebe2fad8e0f47468a9d`
- claim boundary: `football_relevance_only_not_recruitment_advice`

No participant record, formal response, acceptance state, threshold, freeze or W10 checkpoint was
created by this reproduction.

## Saved experiments

Saved experiments were not migrated, deleted or re-pinned. Replaying all four pre-uplift records
against the live post-uplift authority appended these honest receipts:

| Experiment | Prior relation | Post-uplift status | Receipt digest |
|---|---|---|---|
| `66372ff5-d444-4813-a260-76d4df2dda63` | older authority | `INCOMPATIBLE_PINS` | `f1dac962eaa78e365e889a46708adc6ce2aba80087cb2f46d81896c132636bbb` |
| `afb756da-be21-418b-9cfd-e3faca183e32` | older authority | `INCOMPATIBLE_PINS` | `a61213213df4c2854560391623a70af2dc39b3adf2af990db4df5814ef8d320d` |
| `3eabecfb-1848-4afa-abfe-33796aa2de98` | older authority | `INCOMPATIBLE_PINS` | `09deff9b3ca7911dc2ba935a9d66c10836516064cddb635edb3ea22775a9d243` |
| `e6a8a280-423c-8248-ac40-037a34b99cf7` | accepted pre-uplift authority; previously reproduced | `INCOMPATIBLE_PINS` | `f6e8ff038facde6faed429f291c4d35a0a8bbe1b5ee9085b8a51293e9c258814` |

The clearly labelled post-uplift experiment
`7b406aa1-f2f5-506a-89e2-9be868a2cfd1` reproduced with receipt digest
`2688f87407d6c765acdaa2354fc9bd6f76eb1e7a787b4bb421f3d1e99ca5bfa5`.

## Governance boundary

The transition is a non-acceptance technical checkpoint only. W09 remains closed, W10 remains
`REWORK`, G-RW4 remains `INSUFFICIENT_EVIDENCE`, and formal W10 collection, 08E, 08F and W10
acceptance remain unstarted. The authorised checkpoint name is
`checkpoint/w10-prestudy-uplift-reviewed`; it cannot be interpreted as `checkpoint/w10-accepted`.
