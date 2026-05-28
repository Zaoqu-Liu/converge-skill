# Export Report PRD Excerpt

## Intended Behavior

- Users on an active Pro plan can export a workspace report.
- Users without a billable plan must see `Billing setup required`.
- The export request must include `workspace.billing.plan` and `workspace.id`.
- If billing data is missing, the UI must block export before calling `/api/reports/export`.

## Non-goals

- Do not show a generic `Unknown error` message for billing or entitlement failures.
- Do not ask the report renderer to infer billing state.
