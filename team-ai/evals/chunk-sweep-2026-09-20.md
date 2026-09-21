# Chunk-size sweep: 2026-09-20

The committed 37-question Arcwright set was reindexed and evaluated at each
target chunk size. The gates were not changed during the sweep.

| target_tokens | hitRate | coverage |
|---:|---:|---:|
| 400 | 0.485 | 0.970 |
| 800 | 0.485 | 0.970 |
| 1200 | 0.485 | 0.970 |

All three sizes tied on the measured metrics. The existing 800-token default
is retained as the confirmed choice, and `team-ai/index.lock` is reindexed at
800 tokens.
