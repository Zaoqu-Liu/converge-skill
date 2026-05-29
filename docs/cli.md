# Converge CLI

The reference runtime is a Python module:

```bash
python3 -m converge --help
```

Install the console entry point locally:

```bash
python3 -m pip install -e .
converge --help
```

## Commands

### validate

Validate protocol schemas/examples and optionally the whole repository:

```bash
python3 -m converge validate --protocol-only
python3 -m converge validate
```

### doctor

Inspect host install and proof-tier state:

```bash
python3 -m converge doctor
python3 -m converge doctor --json
```

`doctor` reads `skills/converge/host-adapters.json`, checks declared skill anchors and required bridge files, and reports missing install evidence separately from proof-tier claims. It does not treat an installed copy as proof of native interactive behavior.

### install

Install the canonical skill into supported local host directories:

```bash
python3 -m converge install --targets all
python3 -m converge install --targets claude,cursor,opencode --dry-run
```

Install targets are derived from the adapter registry. Today the local copy targets are `claude`, `cursor`, `opencode`, `cline`, and `antigravity`; H0 rule-only hosts such as Gemini CLI, GitHub Copilot, Windsurf, Continue, and Aider stay documented until a real bridge and proof path exists.

### pack

Pack the canonical skill tree for a target host:

```bash
python3 -m converge pack --target cursor --out dist
python3 -m converge pack --target generic --out dist --dry-run
```

### eval

Build response-eval packets or validate result directories:

```bash
python3 -m converge eval --case low-expression-idea.md --out /tmp/converge-response-eval
python3 -m converge eval --results /tmp/converge-results --require-real-results
```

### native-proof

Build or validate H3 native interaction proof packets:

```bash
python3 -m converge native-proof --out /tmp/converge-native-proof
python3 -m converge native-proof --host-id cursor --out /tmp/converge-native-proof-cursor
python3 -m converge native-proof --proofs /tmp/converge-native-proof/proofs --require-real-artifacts
```

This command does not create H3 evidence by itself. It creates the proof packet and validates filled proof JSON plus real transcript, screenshot, log, or exported conversation evidence from an interactive host run.

### benchmark

Build or summarize IntentBench benchmark runpacks:

```bash
python3 -m converge benchmark --validate
python3 -m converge benchmark --out /tmp/intentbench
python3 -m converge benchmark --suite host --out /tmp/intentbench-host --with-result-stubs
python3 -m converge benchmark --results /tmp/intentbench/results --require-real-results
```

The benchmark command uses `intentbench/manifest.json`, `skills/converge/eval-cases/`, `skills/converge/eval-coverage.tsv`, and the response-eval result format. It reports pass/fail and axis coverage rather than numeric quality scores.

### release-check

Run the release gate:

```bash
python3 -m converge release-check --skip-installs
python3 -m converge release-check --targets all
```

## Design Boundary

The CLI delegates existing skill validators and install scripts where they are already deterministic. It does not bypass host permissions, create native host tools, or promote proof tiers.
