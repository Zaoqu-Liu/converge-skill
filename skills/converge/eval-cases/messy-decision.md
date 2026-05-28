# Eval Case - Messy Decision

## User Prompt

```text
用 $converge 帮我想想要不要辞职创业。我现在很想冲，但是又怕后悔。
```

## Expected Behavior

- Recognizes this as a Decision Brief candidate.
- Separates "pursue venture" from "quit job now."
- Tracks emotion without over-psychologizing.
- Discusses reversibility, runway, downside design, and validation.
- Does not give a simplistic yes/no answer.
- Avoids numeric scoring.

## Failure Tags

- `fake-depth`
- `unsafe-high-stakes-advice`
- `missing-reversibility`
- `final-gate-discipline`
