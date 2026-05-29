# Converge Protocol v1

Converge Protocol v1 is the stable interface between an agent host and Converge behavior.

It separates the model's capability from the protocol obligations that make collaboration reliable:

- reconstruct intent before committing to an output
- inspect accessible context before asking the user to restate it
- verify drift-prone facts before making technical or market claims
- keep host interaction realistic
- label support and completion claims by proof tier
- produce artifacts that are usable, reviewable, and bounded

## Core Objects

Protocol schemas live in `protocol/schemas/`.

| Schema | Purpose |
|---|---|
| `converge-run.schema.json` | Standard shape for a Converge run: intent, context, decision, evidence, interaction, output, and proof |
| `host-capability.schema.json` | Standard host capability contract for instruction, install, interaction, fallback, claim, eval, and H3 boundary |
| `host-adapter-registry.schema.json` | Machine-readable host adapter registry for install surfaces, bridges, interaction boundaries, proof tiers, and eval hooks |
| `native-interaction-proof.schema.json` | H3 proof artifact for real native question UI/tool runs, including interaction checks and transcript/screenshot/log evidence |
| `eval-result.schema.json` | Standard response-eval result shape |
| `converge-compatible-manifest.schema.json` | Manifest for third-party skills or workflows that claim Converge compatibility |

Example instances live in `protocol/examples/`.

## Proof Tiers

Converge Protocol uses H0-H4 support tiers:

| Tier | Meaning |
|---|---|
| H0 | documented rule coverage |
| H1 | installed or bridged |
| H2 | fallback behavior tested |
| H3 | native interactive behavior tested |
| H4 | production-like workflow tested |

The protocol requires evidence to match the claim. A host can be H1 installed and still have H3 native interaction unproven.

## Host Adapter Registry

The runtime registry lives at `skills/converge/host-adapters.json`. It is intentionally more specific than the generic host capability schema: it includes install target keys, bridge files such as the Cursor rule bridge, native question tool names only when a tool is actually claimed, and the eval case that protects each support boundary.

`host-capability-contract.tsv` remains a reviewer-friendly table, but validators treat it as derived from the registry. If a host claim, install anchor, interaction surface, eval case, or H3 boundary drifts between those files, `converge validate --protocol-only` fails.

## Native Interaction Proof

H3 proof requires a real interactive run where the native question surface is visible and used correctly. Build proof packets with:

```bash
python3 -m converge native-proof --out /tmp/converge-native-proof
```

After collecting the host response and evidence artifacts, validate the filled JSON:

```bash
python3 -m converge native-proof --proofs /tmp/converge-native-proof/proofs --require-real-artifacts
```

This proof sits beside response-eval results. Response-eval checks whether the answer satisfies Converge behavior; native proof checks whether the host-native interaction path itself was real.

## Validate Protocol Files

```bash
python3 -m converge validate --protocol-only
```

Repository verification also runs protocol validation:

```bash
python3 scripts/verify.py
```

## Compatible Skills

A third-party skill or workflow can declare Converge compatibility with `converge-compatible-manifest.schema.json`.

Minimum expectations:

- declare supported intent surfaces
- declare host support with H0-H4 tiers
- provide eval case coverage
- enforce no-overclaim and source-required policies for current claims

This is the start of the Converge-compatible ecosystem contract.
