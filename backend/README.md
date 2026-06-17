# Backend

FastAPI service for Aeonic.

## Local Development

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the generated API docs.

By default, local partner and patient accounts are stored in
`backend/.data/aeonic.sqlite3`. Set `AEONIC_DATABASE_PATH` to use a different
SQLite file.

## Cloudflare For SaaS

The partner domain flow can create Cloudflare Custom Hostnames after the
partner's CNAME resolves to `NEXUS_DNS_TARGET`.

Set these in production:

```sh
CLOUDFLARE_API_TOKEN=...
CLOUDFLARE_ZONE_ID=...
NEXUS_DNS_TARGET=nexus.aeonichealthsystems.com
```

The token needs `SSL and Certificates Write` for the zone. Optional knobs are
listed in `.env.example` for SSL validation method, certificate authority,
custom origin server, and custom origin SNI.
