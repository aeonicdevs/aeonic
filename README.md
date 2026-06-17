# Aeonic

This repo is split into:

- `backend/` - FastAPI application
- `apps/site/` - public marketing site
- `apps/partner/` - partner app for clinic-owner signup, login, dashboard, and domain configuration
- `apps/nexus/` - patient-facing Aeonic Nexus app that resolves the partner from the request host

Shared frontend packages can be added under `packages/` when there is enough
shared UI, configuration, or API client code to justify them.

## Backend

Run locally:

```sh
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload
```

Health check:

```sh
curl http://127.0.0.1:8000/health
```

## Marketing Site

The public marketing site lives in `apps/site/` and is configured for Netlify in
`netlify.toml`.

Netlify build settings:

- Base directory: `apps/site`
- Build command: `npm run generate:netlify`
- Publish directory: `dist`

Run the same static build locally:

```sh
cd apps/site
npm run generate:netlify
```

## Partner And Nexus Skeleton

Run the API, Partner app, and Nexus app in separate terminals:

```sh
cd backend
uvicorn app.main:app --reload
```

```sh
cd apps/partner
npm run dev
```

```sh
cd apps/nexus
npm run dev
```

Local URLs:

- Marketing site: `http://127.0.0.1:3000`
- Partner app: `http://127.0.0.1:5174`
- Nexus patient app: `http://127.0.0.1:5173`

For local host simulation, save the real or simulated patient domain in the Partner app, then open Nexus with:

```text
http://127.0.0.1:5173/?clinicHost=app.viper.guru
```

That lets you exercise the same API domain mapping without waiting for a production deploy or changing DNS. In production, the clinic's patient-facing DNS record should point at the Nexus deployment. Nexus sends the browser host to the API, and the API resolves that host to the configured partner.

For Cloudflare Tunnel testing, keep saving the real or simulated patient-facing domain in the Partner app, for example `app.viper.guru`. Do not save the local tunnel hostname as partner data. Instead, set `AEONIC_DEV_DOMAIN_ALIASES` so the API treats your local tunnel hostname as an alias for that patient domain.

In development, the API allows localhost origins on any port so Vite can auto-select a free port without breaking API calls.

## Local Development With Cloudflare And tmux

The local Cloudflare and tmux scripts share settings from:

```sh
scripts/dev-local.env
```

Create that file from the example, then update `AEONIC_TEST_DOMAIN`, `AEONIC_DEV_SUBDOMAIN`, and `AEONIC_TUNNEL_NAME`:

```sh
cp scripts/dev-local.example.env scripts/dev-local.env
$EDITOR scripts/dev-local.env
```

One-time Cloudflare setup:

```sh
scripts/setup-cloudflare-local-tunnel.sh
```

This creates or updates the `~/.cloudflared/<AEONIC_TUNNEL_NAME>.yml` ingress rules and DNS routes for per-developer tunnel hostnames:

- `api.<AEONIC_DEV_SUBDOMAIN>.local.<AEONIC_TEST_DOMAIN>` -> `http://127.0.0.1:8000`
- `nexus.<AEONIC_DEV_SUBDOMAIN>.local.<AEONIC_TEST_DOMAIN>` -> `http://127.0.0.1:5173`
- `partner.<AEONIC_DEV_SUBDOMAIN>.local.<AEONIC_TEST_DOMAIN>` -> `http://127.0.0.1:5174`
- `www.<AEONIC_DEV_SUBDOMAIN>.local.<AEONIC_TEST_DOMAIN>` -> `http://127.0.0.1:3000`

Use per-developer hostnames instead of one shared `nexus-local.<domain>` because multiple laptops running the same shared tunnel can cause Cloudflare to route requests to the wrong developer's local frontend, backend, or database. Per-developer hostnames keep each developer's browser, API calls, logs, and local data isolated.

The tmux startup script sets:

- `VITE_API_BASE_URL=https://api.<AEONIC_DEV_SUBDOMAIN>.local.<AEONIC_TEST_DOMAIN>` for Nexus
- `VITE_ALLOWED_HOSTS=nexus.<AEONIC_DEV_SUBDOMAIN>.local.<AEONIC_TEST_DOMAIN>` for Vite
- `AEONIC_DEV_DOMAIN_ALIASES=nexus.<AEONIC_DEV_SUBDOMAIN>.local.<AEONIC_TEST_DOMAIN>=<AEONIC_PATIENT_DOMAIN_ALIAS_TARGET>` for the backend

Daily startup:

```sh
scripts/dev-tmux.sh
```

This opens one tmux session with separate windows for the marketing site, Cloudflare tunnel, backend, Partner app, and Nexus app. Re-running it attaches to the existing session if it is already active.

## Deployment

Pushing to `main` runs `.github/workflows/deploy-backend.yml`, which tests the FastAPI app and deploys it to a DigitalOcean Droplet over SSH.

Add these GitHub repository secrets:

- `DO_SSH_HOST` - Droplet hostname or IP address
- `DO_SSH_USER` - SSH user, for example `root` or `deploy`
- `DO_SSH_KEY` - private SSH key with access to the Droplet
- `DO_SSH_PORT` - optional SSH port; defaults to `22`
- `DEPLOY_PATH` - optional remote path; defaults to `/home/<DO_SSH_USER>/aeonic`

The Droplet needs Docker and the Docker Compose plugin installed.

If you need production environment variables, create a `.env` file at the remote deploy path, for example `/home/deploy/aeonic/.env`. The deploy workflow preserves that file.
