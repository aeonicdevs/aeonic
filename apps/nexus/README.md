# Aeonic Nexus

Vue + Vuetify starter for the authenticated Aeonic Nexus experience.

This app will serve the `nexus` subdomain where invited end users access their
Aeonic experience. The initial scaffold is based on the client-provided
`app-connect-v2 (1).html` reference and focuses on the portal functionality that
maps cleanly to Vue components and Vuetify primitives.

## Local development

```sh
npm install
npm run dev
```

For Cloudflare Tunnel development, use a per-developer Nexus hostname instead
of a shared local hostname. Example:

```sh
VITE_API_BASE_URL=https://api.nathan.local.aeonichealthsystems.com \
VITE_ALLOWED_HOSTS=nexus.nathan.local.aeonichealthsystems.com \
npm run dev
```

Per-developer hostnames prevent Cloudflare from routing a shared local hostname
to another developer's laptop when multiple tunnel connectors are running.

## Build

```sh
npm run build
```

## Reference Notes

See `docs/reference-assessment.md` for notes on which parts of the provided HTML
are straightforward in Vuetify and which pieces need product/backend decisions
before implementation.
