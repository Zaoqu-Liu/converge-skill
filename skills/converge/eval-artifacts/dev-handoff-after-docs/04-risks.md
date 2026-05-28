# Risks

## Known Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Permission leakage | High | Filter before generation and test denied access. |
| Weak citations | High | Require citation ids from retrieved chunks. |
| PDF parsing errors | Medium | Add extraction warnings and review queue. |
| SSO group sync missing | Medium | Use document owner allowlists in v1. |

## Handoff Notes

- Do not invent group sync behavior for v1.
- Do not add autonomous write-back features.
- Treat citations and permission filtering as release-blocking acceptance criteria.
