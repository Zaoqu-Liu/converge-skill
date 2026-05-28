# Execution

## Milestones

| Milestone | Scope |
|---|---|
| M1 | Upload Markdown/PDF, parse text, store source metadata. |
| M2 | Chunk, embed, index, and permission-filter retrieval. |
| M3 | Chat answer flow with citations and unresolved-question logging. |
| M4 | Admin review queue and basic quality dashboard. |

## Suggested Stack

- Backend: FastAPI.
- Database: PostgreSQL with pgvector.
- Frontend: Next.js.
- Auth: existing SSO integration through session user id.

## Validation

- Unit test permission filter.
- Integration test upload to cited answer.
- Manual test that a user cannot retrieve restricted document chunks.
