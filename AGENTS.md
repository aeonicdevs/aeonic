# Agent Instructions

## Arora Integration

Before changing Arora-related backend, mock-client, live-client, admin, partner,
or Nexus functionality, read the local Arora reference docs in
`docs/arora/README.md`.

Treat the copied Arora reference in `docs/arora/api-reference.md` as the source
of truth for endpoint paths, payload fields, response shapes, and enum values.
Do not infer Arora response fields from existing mock data or frontend types
when the docs disagree or are more specific.

When implementing a new Arora endpoint or UI surface:

- Add or update focused tests around the documented request and response shape.
- Keep FastAPI route code behind the shared boundary in
  `backend/app/arora_client.py`.
- Keep outbound HTTP behavior in `backend/app/arora_live_client.py`.
- Keep local simulation behavior in `backend/app/arora_mock_client.py`.
- If docs are incomplete, add the observed copied example to the matching
  endpoint section in `docs/arora/api-reference.md` before coding against it.
