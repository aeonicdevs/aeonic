# Aeonic

This repo is split into:

- `backend/` - FastAPI application
- `apps/site/` - public marketing site
- `apps/connect/` - business/operator platform for customer organizations
- `apps/nexus/` - end-user app for patients and members

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
