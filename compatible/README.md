# Converge-Compatible Artifacts

This directory contains third-party-style examples and validation fixtures for artifacts that claim Converge Protocol compatibility.

A compatible artifact is not merely "inspired by Converge." It must declare:

- the Converge Protocol version it targets
- the artifact entrypoint and supporting docs
- the intent surfaces it handles
- host support claims with H0-H4 proof tiers
- eval cases that protect the claim
- proof policies for no-overclaim, current-source requirements, host evidence, H3 native proof, and context trust boundaries

Validate all bundled examples:

```bash
python3 scripts/check_converge_compatible.py compatible/examples
```

Or through the reference CLI:

```bash
python3 -m converge compatible compatible/examples
```

The validator checks manifest structure, referenced files, eval case sections, required failure-tag coverage, host evidence references, and proof-policy strictness.
