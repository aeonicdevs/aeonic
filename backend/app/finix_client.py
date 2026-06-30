import sqlite3
from typing import Any, Literal


class FinixClientError(Exception):
    pass


class FinixValidationError(FinixClientError):
    pass


class FinixNotFoundError(FinixClientError):
    pass


class FinixConfigurationError(FinixClientError):
    pass


def build_finix_client(mode: Literal["mock", "sandbox", "live"], db: sqlite3.Connection):
    if mode == "mock":
        from app.finix_mock_client import MockFinixClient

        return MockFinixClient(db)

    from app.finix_live_client import LiveFinixClient

    return LiveFinixClient(mode=mode)


def initialize_finix_storage(db: sqlite3.Connection) -> None:
    from app.finix_mock_client import initialize_mock_finix_schema

    initialize_mock_finix_schema(db)


FinixOnboardingForm = dict[str, Any]
