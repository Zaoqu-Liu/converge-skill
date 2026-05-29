# Gallery

The Gallery shows before/after examples that make Converge's value legible in seconds.

Machine-readable examples live in `gallery/examples.json`. The static docs site at `site/index.html` renders those examples.

Current sections:

- vague idea / low-expression intent
- current technical route
- instruction-bearing artifact review
- proof-overclaim correction
- host adapter realism
- native question UI boundary
- architecture handoff
- high-risk decision boundary

Each example includes user input, weak response pattern, Converge response pattern, why the Converge response is better, and proof boundary.

The gallery is intentionally separate from the core skill so examples can be expanded without bloating the skill context.

Validate:

```bash
python3 scripts/check_gallery_site.py
```
