# Context

## Objective

Build a private team knowledge assistant that lets employees search policy, project, and support documents, then ask follow-up questions with cited answers.

## Users

- Admin: manages sources, permissions, and audit settings.
- Employee: asks questions and saves useful answers.
- Team lead: reviews answer quality and unresolved questions.

## Constraints

- Must respect document-level permissions.
- Must show source citations for every answer.
- First release supports Markdown and PDF uploads only.
- SSO exists but group sync is not implemented yet.

## Non-Goals

- No autonomous write-back into source systems in v1.
- No customer-facing deployment in v1.
