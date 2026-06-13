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

For local subdomain simulation, save a clinic domain in the Partner app, then open Nexus with:

```text
http://127.0.0.1:5173/?clinicHost=patients.yourclinic.test
```

In production, the clinic's patient-facing DNS record should point at the Nexus deployment. Nexus sends the browser host to the API, and the API resolves that host to the configured partner.

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
