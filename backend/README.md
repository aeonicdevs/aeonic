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
