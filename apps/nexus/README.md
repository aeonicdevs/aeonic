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

## Production

Nexus is served by the production Docker/Caddy stack for Cloudflare For SaaS
tenant domains. The image builds the static Vite app and serves it with Nginx,
while Caddy routes `nexus.aeonichealthsystems.com` and arbitrary non-API
hostnames to that container.

```sh
docker compose up -d --build nexus caddy
```

Set `NEXUS_API_BASE_URL` in the root `.env` if the production API URL is not
`https://api.aeonichealthsystems.com`.

## Reference Notes

See `docs/reference-assessment.md` for notes on which parts of the provided HTML
are straightforward in Vuetify and which pieces need product/backend decisions
before implementation.
