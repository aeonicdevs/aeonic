import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def _allowed_origins() -> list[str]:
    raw_origins = os.getenv("ALLOWED_ORIGINS")
    if raw_origins is None and os.getenv("APP_ENV", "development") != "production":
        return ["http://localhost:3000", "http://127.0.0.1:3000"]

    raw_origins = raw_origins or ""
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


def create_app() -> FastAPI:
    app = FastAPI(title="Aeonic API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_allowed_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/", tags=["system"])
    def root() -> dict[str, str]:
        return {"name": "Aeonic API", "status": "running"}

    return app


app = create_app()
