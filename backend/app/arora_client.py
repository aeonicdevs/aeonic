import sqlite3
from typing import Literal


# Keep this module as the only import boundary for Arora behavior in FastAPI
# routes. Route handlers should ask for a client here instead of importing the
# mock or live implementation directly; that prevents local simulation details
# from bleeding into code that must also work against the real Arora API.
class AroraClientError(Exception):
    pass


class AroraValidationError(AroraClientError):
    pass


class AroraConflictError(AroraClientError):
    pass


class AroraNotFoundError(AroraClientError):
    pass


def build_arora_client(mode: Literal["mock", "dry_run", "live"], db: sqlite3.Connection):
    # dry_run still uses the local client for catalog/conversation reads and
    # simulated writes, while order submission is short-circuited by main.py.
    # Only live mode should create outbound HTTP requests to Arora.
    if mode in {"mock", "dry_run"}:
        from app.arora_mock_client import MockAroraClient

        return MockAroraClient(db)

    from app.arora_live_client import LiveAroraClient

    return LiveAroraClient()


def initialize_arora_storage(db: sqlite3.Connection) -> None:
    # The mock client owns its SQLite schema. This wrapper lets app startup
    # initialize local storage without importing mock-specific code elsewhere.
    from app.arora_mock_client import initialize_mock_arora_schema

    initialize_mock_arora_schema(db)
