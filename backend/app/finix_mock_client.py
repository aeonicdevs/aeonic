import secrets
import sqlite3
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

from app.finix_client import FinixNotFoundError, FinixValidationError


MockFinixOnboardingStatus = Literal["IN_PROGRESS", "COMPLETED", "UPDATE_REQUESTED", "REJECTED"]


def initialize_mock_finix_schema(db: sqlite3.Connection) -> None:
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS mock_finix_onboarding_forms (
            id TEXT PRIMARY KEY,
            partner_id TEXT NOT NULL,
            status TEXT NOT NULL,
            token TEXT NOT NULL UNIQUE,
            link_url TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            identity_id TEXT,
            merchant_id TEXT,
            merchant_status TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )


class MockFinixClient:
    def __init__(self, db: sqlite3.Connection):
        self.db = db

    def create_onboarding_form(
        self,
        *,
        partner_id: str,
        clinic_name: str,
        owner_name: str,
        email: str,
        return_url: str,
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        form_id = f"mock_onboarding_form_{uuid.uuid4().hex[:16]}"
        token = secrets.token_urlsafe(24)
        link_url = f"{return_url.rstrip('/')}/mock/finix/onboarding-forms/{form_id}?token={token}"
        expires_at = (now + timedelta(days=7)).isoformat()
        self.db.execute(
            """
            INSERT INTO mock_finix_onboarding_forms (
                id, partner_id, status, token, link_url, expires_at, updated_at
            )
            VALUES (?, ?, 'IN_PROGRESS', ?, ?, ?, ?)
            """,
            (form_id, partner_id, token, link_url, expires_at, now.isoformat()),
        )
        return self._public_form(self._get_form(form_id))

    def get_onboarding_form(self, form_id: str) -> dict[str, Any]:
        return self._public_form(self._get_form(form_id))

    def complete_onboarding_form(
        self,
        form_id: str,
        *,
        token: str,
        outcome: MockFinixOnboardingStatus = "COMPLETED",
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        if outcome not in {"COMPLETED", "UPDATE_REQUESTED", "REJECTED"}:
            raise FinixValidationError("Unsupported mock Finix onboarding outcome")

        form = self._get_form(form_id)
        if not secrets.compare_digest(form["token"], token):
            raise FinixNotFoundError("Mock Finix onboarding form not found")

        now = datetime.now(UTC)
        identity_id = form["identity_id"]
        merchant_id = form["merchant_id"]
        merchant_status = form["merchant_status"]
        if outcome == "COMPLETED":
            identity_id = identity_id or f"mock_identity_{form['partner_id']}"
            merchant_id = merchant_id or f"mock_merchant_{form['partner_id']}"
            merchant_status = "APPROVED"
        elif outcome == "UPDATE_REQUESTED":
            merchant_status = "UPDATE_REQUESTED"
        else:
            merchant_status = "REJECTED"

        self.db.execute(
            """
            UPDATE mock_finix_onboarding_forms
            SET status = ?,
                identity_id = ?,
                merchant_id = ?,
                merchant_status = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (outcome, identity_id, merchant_id, merchant_status, now.isoformat(), form_id),
        )
        updated_form = self._public_form(self._get_form(form_id))
        return updated_form, self._webhook_event(updated_form)

    def _get_form(self, form_id: str) -> sqlite3.Row:
        form = self.db.execute(
            "SELECT * FROM mock_finix_onboarding_forms WHERE id = ?",
            (form_id,),
        ).fetchone()
        if form is None:
            raise FinixNotFoundError("Mock Finix onboarding form not found")
        return form

    def _public_form(self, form: sqlite3.Row) -> dict[str, Any]:
        onboarding_link = {
            "link_url": form["link_url"],
            "expires_at": form["expires_at"],
        }
        return {
            "id": form["id"],
            "partner_id": form["partner_id"],
            "status": form["status"],
            "identity_id": form["identity_id"],
            "merchant_id": form["merchant_id"],
            "merchant_status": form["merchant_status"],
            "onboarding_link": onboarding_link,
            "created_at": form["created_at"],
            "updated_at": form["updated_at"],
        }

    def _webhook_event(self, form: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": f"mock_finix_event_{uuid.uuid4().hex[:16]}",
            "type": "onboarding_form.updated",
            "entity": "onboarding_form",
            "occurred_at": datetime.now(UTC).isoformat(),
            "data": {
                "id": form["id"],
                "partner_id": form["partner_id"],
                "status": form["status"],
                "identity_id": form["identity_id"],
                "merchant_id": form["merchant_id"],
                "merchant_status": form["merchant_status"],
            },
        }
