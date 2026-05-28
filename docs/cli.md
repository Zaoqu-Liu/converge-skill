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

### install

Install the canonical skill into supported local host directories:

```bash
python3 -m converge install --targets all
python3 -m converge install --targets claude,cursor,opencode --dry-run
```

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

### release-check

Run the release gate:

```bash
python3 -m converge release-check --skip-installs
python3 -m converge release-check --targets all
```

## Design Boundary

The CLI delegates existing skill validators and install scripts where they are already deterministic. It does not bypass host permissions, create native host tools, or promote proof tiers.
