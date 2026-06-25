# Aeonic

This repo is split into:

- `backend/` - FastAPI application
- `apps/marketing/` - public marketing site
- `apps/partner/` - partner app for clinic-owner signup, login, dashboard, and domain configuration
- `apps/admin/` - internal admin app for operations testing and manual Arora workflow simulation
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

The public marketing site lives in `apps/marketing/`. Configure its Netlify site with:

- Base directory: `apps/marketing`
- Build command: `npm run build`
- Publish directory: `.output/public`

Configure the Nexus Netlify site separately:

- Base directory: `apps/nexus`
- Build command: `npm run build`
- Publish directory: `dist`

Configure the Admin Netlify site separately:

- Base directory: `apps/admin`
- Build command: `npm run build`
- Publish directory: `dist`
- Environment variable: `VITE_API_BASE_URL=https://api.aeonichealthsystems.com`
- Domain: `admin.aeonichealthsystems.com`

That Netlify setup is only suitable for Aeonic-owned hostnames explicitly added
to the Netlify site. Tenant custom hostnames managed through Cloudflare For SaaS
should route to the production Docker/Caddy stack instead, because that origin
accepts arbitrary tenant Host headers.

Run the same static build locally:

```sh
cd apps/marketing
npm run generate:netlify
```

## Partner And Nexus Skeleton

Run the API, Admin app, Partner app, and Nexus app in separate terminals:

```sh
cd backend
uvicorn app.main:app --reload
```

```sh
cd apps/partner
npm run dev
```

```sh
cd apps/admin
npm run dev
```

```sh
cd apps/nexus
npm run dev
```

Local URLs:

- Marketing site: `http://127.0.0.1:3000`
- Partner app: `http://127.0.0.1:5174`
- Admin app: `http://127.0.0.1:5175`
- Nexus patient app: `http://127.0.0.1:5173`

For local host simulation, save the real or simulated patient domain in the Partner app, then open Nexus with:

```text
http://127.0.0.1:5173/?clinicHost=app.viper.guru
```

That lets you exercise the same API domain mapping without waiting for a production deploy or changing DNS. In production, the clinic's patient-facing DNS record should point at the Nexus deployment. Nexus sends the browser host to the API, and the API resolves that host to the configured partner.

To test the patient-to-admin order loop locally:

1. In Partner, save a patient-facing domain such as `app.viper.guru`.
2. Open Nexus at `http://127.0.0.1:5173/?clinicHost=app.viper.guru`.
3. Sign up or log in as a patient and place an order.
4. Open Admin at `http://127.0.0.1:5175`, refresh the queue, and advance the order through the Arora stage menu.
5. Back in Nexus, use Refresh status to see the latest simulated stage.

Admin also includes a mock Arora product catalog. Use the Products tab at
`http://127.0.0.1:5175` to create, edit, deactivate, or delete local products
and packages using the Arora-shaped fields: `name`, `displayName`,
`customerPrice`, optional `itemType: "package"`, `includedProducts`,
`status`, `showPatient`, `description`, and `displayDescription`.
The backend mock also preserves `displayCategoryIds` for API compatibility,
but the admin UI does not currently expose it while the category model is
unclear. Those records are served through backend
`/admin/arora/products` endpoints so the admin UI can keep the same
Aeonic-facing contract. The endpoints delegate to the Arora client adapter in
`backend/app/arora_client.py`, which currently uses the mock SQLite store and
can later be swapped to a real Arora HTTP implementation.

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

- `api-<AEONIC_DEV_SUBDOMAIN>-local.<AEONIC_TEST_DOMAIN>` -> `http://127.0.0.1:8000`
- `nexus-<AEONIC_DEV_SUBDOMAIN>-local.<AEONIC_TEST_DOMAIN>` -> `http://127.0.0.1:5173`
- `partner-<AEONIC_DEV_SUBDOMAIN>-local.<AEONIC_TEST_DOMAIN>` -> `http://127.0.0.1:5174`
- `admin-<AEONIC_DEV_SUBDOMAIN>-local.<AEONIC_TEST_DOMAIN>` -> `http://127.0.0.1:5175`
- `www-<AEONIC_DEV_SUBDOMAIN>-local.<AEONIC_TEST_DOMAIN>` -> `http://127.0.0.1:3000`

Use per-developer hostnames instead of one shared `nexus-local.<domain>` because multiple laptops running the same shared tunnel can cause Cloudflare to route requests to the wrong developer's local frontend, backend, or database. Per-developer hostnames keep each developer's browser, API calls, logs, and local data isolated.

The tmux startup script sets:

- `VITE_API_BASE_URL=https://api-<AEONIC_DEV_SUBDOMAIN>-local.<AEONIC_TEST_DOMAIN>` for Nexus
- `VITE_ALLOWED_HOSTS=nexus-<AEONIC_DEV_SUBDOMAIN>-local.<AEONIC_TEST_DOMAIN>` for Nexus Vite
- `VITE_ALLOWED_HOSTS=partner-<AEONIC_DEV_SUBDOMAIN>-local.<AEONIC_TEST_DOMAIN>` for Partner Vite
- `VITE_ALLOWED_HOSTS=admin-<AEONIC_DEV_SUBDOMAIN>-local.<AEONIC_TEST_DOMAIN>` for Admin Vite
- `NEXUS_DNS_TARGET=nexus-<AEONIC_DEV_SUBDOMAIN>-local.<AEONIC_TEST_DOMAIN>` for the backend CNAME instructions
- `AEONIC_DEV_DOMAIN_ALIASES=nexus-<AEONIC_DEV_SUBDOMAIN>-local.<AEONIC_TEST_DOMAIN>=<AEONIC_PATIENT_DOMAIN_ALIAS_TARGET>` for the backend

Daily startup:

```sh
scripts/dev-tmux.sh
```

This opens one tmux session with separate windows for the marketing site, Cloudflare tunnel, backend, Partner app, and Nexus app. Re-running it attaches to the existing session if it is already active.

## Deployment

Pushing to `main` runs `.github/workflows/deploy-backend.yml`, which tests the FastAPI app and deploys the backend, Nexus, and Caddy stack to a DigitalOcean Droplet over SSH.

Add these GitHub repository secrets:

- `DO_SSH_HOST` - Droplet hostname or IP address
- `DO_SSH_USER` - SSH user, for example `root` or `deploy`
- `DO_SSH_KEY` - private SSH key with access to the Droplet
- `DO_SSH_PORT` - optional SSH port; defaults to `22`
- `DEPLOY_PATH` - optional remote path; defaults to `/home/<DO_SSH_USER>/aeonic`

The Droplet needs Docker and the Docker Compose plugin installed.

If you need production environment variables, create a `.env` file at the remote deploy path, for example `/home/deploy/aeonic/.env`. The deploy workflow preserves that file.

For scalable tenant custom domains:

- Keep `NEXUS_DNS_TARGET=nexus.aeonichealthsystems.com`.
- Point Cloudflare For SaaS fallback/custom-hostname traffic at the Droplet/Caddy Nexus origin, not Netlify.
- Use `NEXUS_API_BASE_URL=https://api.aeonichealthsystems.com` unless the API host changes.
- The Caddy HTTPS listener uses the Cloudflare Origin CA certificate, routes `api.aeonichealthsystems.com` to the backend, and routes all other HTTPS hostnames to Nexus. This lets tenant custom hostnames complete origin TLS without requiring Cloudflare custom origin SNI. If the Cloudflare account is provisioned for custom origin SNI, set `CLOUDFLARE_CUSTOM_HOSTNAME_ORIGIN_SNI=nexus.aeonichealthsystems.com`.
- Tenant domains still need to be saved in the Partner app. The API allows CORS from saved HTTPS patient domains dynamically.

Caddy expects the Cloudflare Origin CA certificate for Nexus on the droplet at:

```text
/home/deploy/.aeonic-secrets/caddy/cloudflare-origin.pem
/home/deploy/.aeonic-secrets/caddy/cloudflare-origin.key
```

The deploy workflow writes these files from the `CLOUDFLARE_ORIGIN_CERT` and
`CLOUDFLARE_ORIGIN_KEY` GitHub environment secrets. Set `CADDY_CERTS_PATH` in
the droplet `.env` only if the deploy user or secret directory changes.
