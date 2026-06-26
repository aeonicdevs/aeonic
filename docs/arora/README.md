# Arora API Docs

This directory is the local source of truth for the Arora API while building the
Aeonic integration.

## Files

- `api-reference.md` - pasted Arora endpoint documentation.
- `response-examples.md` - pasted code examples and observed response payloads.

## How To Capture The Docs

The hosted Arora docs appear to render much of their content through
JavaScript, so saving the page HTML may only preserve script references instead
of the actual endpoint text. Plain Markdown copied from the rendered page is
usually better for Codex context.

Recommended workflow:

1. Open the Arora docs in a browser.
2. Select the rendered endpoint content and copy it.
3. Paste it into `api-reference.md` under the matching section.
4. Copy each code example that defines return values.
5. Paste those examples into `response-examples.md` with the endpoint path as a
   heading.
6. Include the source URL and capture date at the top of each file when known.

## Integration Rule

Future Arora work should read this directory before editing:

- `backend/app/arora_client.py`
- `backend/app/arora_live_client.py`
- `backend/app/arora_mock_client.py`
- `backend/app/main.py`
- `apps/admin/`
- `apps/nexus/`
- `apps/partner/`

When a copied example is the only place a response shape is defined, the example
wins over guesses from existing code.
