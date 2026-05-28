# Solution

## Recommended Route

Ship a retrieval-first assistant with a narrow agent workflow:

1. Ingest documents.
2. Chunk and index content with permission metadata.
3. Retrieve permitted chunks for the current user.
4. Generate an answer with citations.
5. Record unresolved questions for review.

## Core Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Permission model | Document ACL copied into chunk metadata | Retrieval must filter before generation. |
| Answer policy | No citation, no answer | Prevents unsupported claims. |
| Review loop | Store low-confidence and unanswered questions | Improves corpus and prompts over time. |

## Open Assumptions

- Existing SSO can provide a stable user id.
- Group membership will be added after v1.
- PDF extraction quality is acceptable for the initial corpus.
