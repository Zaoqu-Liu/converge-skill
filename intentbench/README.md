# IntentBench

IntentBench is the planned public benchmark layer for Converge Protocol.

It will evaluate whether an agent can:

- reconstruct low-expression intent
- avoid over-questioning
- choose the right output profile
- inspect available context
- handle instruction-bearing artifacts safely
- verify current technical claims
- preserve high-risk boundaries
- avoid proof overclaim
- hand off architecture work correctly
- adapt to host capabilities without hallucinating tools

The current seed data is the Converge eval suite in `skills/converge/eval-cases/` plus `skills/converge/eval-coverage.tsv`.

Future benchmark releases should publish:

- blind prompt packets
- review packets
- result schemas
- baseline runs
- host-specific assumptions
- pass/fail summaries by failure tag
