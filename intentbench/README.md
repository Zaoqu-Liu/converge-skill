# IntentBench

IntentBench is the public benchmark layer for Converge Protocol.

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

The benchmark contract is `intentbench/manifest.json`. The current case corpus is the Converge eval suite in `skills/converge/eval-cases/` plus `skills/converge/eval-coverage.tsv`.

Build a benchmark runpack:

```bash
python3 -m converge benchmark --out /tmp/intentbench
python3 -m converge benchmark --suite host --out /tmp/intentbench-host
```

Validate the benchmark manifest:

```bash
python3 -m converge benchmark --validate
```

Summarize filled real results:

```bash
python3 -m converge benchmark --results /tmp/intentbench/results --require-real-results
```

IntentBench reports pass/fail evidence and axis coverage. It deliberately does not use numeric quality scores.

Benchmark releases should publish:

- `manifest.json`
- blind prompt packets
- review packets
- result stubs or result schema references
- baseline runs when real host/model results exist
- host-specific assumptions
- pass/fail summaries by failure tag and coverage axis
