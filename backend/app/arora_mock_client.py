import json
import re
import sqlite3
import uuid
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any, Literal

from app.arora_client import AroraClientError, AroraConflictError, AroraNotFoundError, AroraValidationError


# Local Arora simulation lives here on purpose. Keep SQLite table knowledge,
# seeded product data, fake patient/order responses, and mock conversation
# mutations out of main.py and out of the live client. When adding an Arora
# feature, add the same public method shape here and in LiveAroraClient so the
# route layer can remain implementation-agnostic.
def initialize_mock_arora_schema(db: sqlite3.Connection) -> None:
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS arora_mock_products (
            client_product_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            display_name TEXT NOT NULL,
            customer_price REAL NOT NULL DEFAULT 0,
            item_type TEXT,
            included_products TEXT NOT NULL DEFAULT '[]',
            description TEXT NOT NULL DEFAULT '',
            display_description TEXT NOT NULL DEFAULT '',
            show_patient INTEGER NOT NULL DEFAULT 1,
            display_category_ids TEXT NOT NULL DEFAULT '[]',
            status TEXT NOT NULL DEFAULT 'active',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS arora_mock_conversations (
            id TEXT PRIMARY KEY,
            partner_id TEXT NOT NULL REFERENCES partners(id) ON DELETE CASCADE,
            patient_id TEXT NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
            status TEXT NOT NULL DEFAULT 'active',
            subject TEXT NOT NULL DEFAULT 'Care team',
            escalation_reason TEXT,
            escalated_at TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS arora_mock_conversation_messages (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL REFERENCES arora_mock_conversations(id) ON DELETE CASCADE,
            author TEXT NOT NULL CHECK (author IN ('client', 'patient')),
            sender_user_id TEXT,
            sender_name TEXT NOT NULL,
            text TEXT NOT NULL,
            attachments TEXT NOT NULL DEFAULT '[]',
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    _ensure_mock_product_columns(db)
    _ensure_mock_conversation_columns(db)
    seed_mock_products(db)


def _ensure_mock_product_columns(db: sqlite3.Connection) -> None:
    columns = {row["name"] for row in db.execute("PRAGMA table_info(arora_mock_products)").fetchall()}
    migrations = {
        "customer_price": "ALTER TABLE arora_mock_products ADD COLUMN customer_price REAL NOT NULL DEFAULT 0",
        "item_type": "ALTER TABLE arora_mock_products ADD COLUMN item_type TEXT",
        "included_products": "ALTER TABLE arora_mock_products ADD COLUMN included_products TEXT NOT NULL DEFAULT '[]'",
        "display_description": "ALTER TABLE arora_mock_products ADD COLUMN display_description TEXT NOT NULL DEFAULT ''",
        "show_patient": "ALTER TABLE arora_mock_products ADD COLUMN show_patient INTEGER NOT NULL DEFAULT 1",
        "display_category_ids": "ALTER TABLE arora_mock_products ADD COLUMN display_category_ids TEXT NOT NULL DEFAULT '[]'",
    }
    for column, statement in migrations.items():
        if column not in columns:
            db.execute(statement)
    refreshed_columns = {row["name"] for row in db.execute("PRAGMA table_info(arora_mock_products)").fetchall()}
    if "price_cents" in refreshed_columns:
        db.execute(
            """
            UPDATE arora_mock_products
            SET customer_price = ROUND(COALESCE(price_cents, 0) / 100.0, 2)
            WHERE customer_price = 0 AND price_cents IS NOT NULL
            """
        )
    if "category" in refreshed_columns:
        rows = db.execute(
            """
            SELECT client_product_id, category
            FROM arora_mock_products
            WHERE display_category_ids = '[]' AND COALESCE(category, '') != ''
            """
        ).fetchall()
        for row in rows:
            db.execute(
                "UPDATE arora_mock_products SET display_category_ids = ? WHERE client_product_id = ?",
                (json.dumps([row["category"]]), row["client_product_id"]),
            )
    db.execute(
        """
        UPDATE arora_mock_products
        SET display_description = description
        WHERE display_description = '' AND COALESCE(description, '') != ''
        """
    )


def _ensure_mock_conversation_columns(db: sqlite3.Connection) -> None:
    conversation_columns = {row["name"] for row in db.execute("PRAGMA table_info(arora_mock_conversations)").fetchall()}
    conversation_migrations = {
        "escalation_reason": "ALTER TABLE arora_mock_conversations ADD COLUMN escalation_reason TEXT",
        "escalated_at": "ALTER TABLE arora_mock_conversations ADD COLUMN escalated_at TEXT",
    }
    for column, statement in conversation_migrations.items():
        if column not in conversation_columns:
            db.execute(statement)

    message_columns = {
        row["name"] for row in db.execute("PRAGMA table_info(arora_mock_conversation_messages)").fetchall()
    }
    message_migrations = {
        "sender_user_id": "ALTER TABLE arora_mock_conversation_messages ADD COLUMN sender_user_id TEXT",
        "attachments": "ALTER TABLE arora_mock_conversation_messages ADD COLUMN attachments TEXT NOT NULL DEFAULT '[]'",
        "updated_at": "ALTER TABLE arora_mock_conversation_messages ADD COLUMN updated_at TEXT",
    }
    for column, statement in message_migrations.items():
        if column not in message_columns:
            db.execute(statement)
    db.execute(
        """
        UPDATE arora_mock_conversation_messages
        SET updated_at = COALESCE(updated_at, created_at, CURRENT_TIMESTAMP)
        WHERE updated_at IS NULL
        """
    )


def seed_mock_products(db: sqlite3.Connection) -> None:
    existing = db.execute("SELECT 1 FROM arora_mock_products LIMIT 1").fetchone()
    if existing is not None:
        return

    now = datetime.now(UTC).isoformat()
    _insert_mock_product(
        db,
        {
            "client_product_id": "mock_client_product_order",
            "name": "Weight Optimization Program",
            "display_name": "Weight Optimization Program",
            "customer_price": 199.00,
            "item_type": None,
            "included_products": "[]",
            "description": "Mock consult product used for local medication shipment testing.",
            "display_description": "A simulated weight optimization consult.",
            "show_patient": 1,
            "display_category_ids": json.dumps(["metabolic"]),
            "status": "active",
            "created_at": now,
            "updated_at": now,
        },
    )
    _insert_mock_product(
        db,
        {
            "client_product_id": "mock_lab_foundation_panel",
            "name": "Foundational Biomarker Panel",
            "display_name": "Foundational Biomarker Panel",
            "customer_price": 149.00,
            "item_type": None,
            "included_products": "[]",
            "description": "Mock lab product for catalog and checkout testing.",
            "display_description": "A simulated foundational biomarker panel.",
            "show_patient": 1,
            "display_category_ids": json.dumps(["labs"]),
            "status": "active",
            "created_at": now,
            "updated_at": now,
        },
    )


def _insert_mock_product(db: sqlite3.Connection, product: dict[str, Any]) -> None:
    table_columns = {row["name"] for row in db.execute("PRAGMA table_info(arora_mock_products)").fetchall()}
    values = dict(product)
    if "product_id" in table_columns:
        values["product_id"] = product["client_product_id"]
    if "category" in table_columns:
        categories = MockAroraClient._json_list(product.get("display_category_ids"))
        values["category"] = categories[0] if categories else ""
    if "product_type" in table_columns:
        values["product_type"] = "consult"
    if "price_cents" in table_columns:
        values["price_cents"] = int(round(float(product["customer_price"]) * 100))

    columns = [column for column in values if column in table_columns]
    placeholders = ", ".join("?" for _ in columns)
    db.execute(
        f"INSERT INTO arora_mock_products ({', '.join(columns)}) VALUES ({placeholders})",
        tuple(values[column] for column in columns),
    )


class MockAroraClient:
    mode = "mock"

    def __init__(self, db: sqlite3.Connection):
        self.db = db

    def create_patient(self, patient_payload: dict[str, Any]) -> dict[str, Any]:
        patient = patient_payload["patient"]
        return {
            "success": True,
            "message": "Mock Arora patient created",
            "data": {
                "patientId": f"mock_patient_{patient['partnerPatientId']}",
                "partnerPatientId": patient["partnerPatientId"],
                "status": "pending",
                "emailSent": False,
                "magicLink": None,
            },
        }

    def create_order(self, order_payload: dict[str, Any]) -> dict[str, Any]:
        order_id = f"mock_order_{uuid.uuid4().hex[:12]}"
        order = order_payload["order"]
        return {
            "success": True,
            "data": {
                "orderId": order_id,
                "patientId": order_payload["patient_id"],
                "clientProductId": order["clientProductId"],
                "orderType": "product",
                "orderStatus": "pending_review",
                "paymentStatus": order["payment_status"],
                "paymentVerificationStatus": "not_required",
                "requiredActions": [],
                "reviewRequired": "async",
                "prescriptions": [],
            },
        }

    def list_products(self, item_type: str | None = None, include_inactive: bool = True) -> list[dict[str, Any]]:
        query = "SELECT * FROM arora_mock_products"
        conditions: list[str] = []
        params: list[str] = []

        if item_type:
            normalized_item_type = self._normalize_item_type(item_type)
            if normalized_item_type is None:
                conditions.append("item_type IS NULL")
            else:
                conditions.append("item_type = ?")
                params.append(normalized_item_type)

        if not include_inactive:
            conditions.append("status = ?")
            params.append("active")

        if conditions:
            query = f"{query} WHERE {' AND '.join(conditions)}"

        rows = self.db.execute(f"{query} ORDER BY display_name COLLATE NOCASE", params).fetchall()
        return [self._public_product(row) for row in rows]

    def create_product(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        item_type = self._normalize_item_type(payload.get("itemType"))
        status = self._normalize_product_status(payload.get("status"))
        name = self._required(payload.get("name"), "Product/package name")
        customer_price = self._normalize_customer_price(payload.get("customerPrice"), required=True)
        included_products = self._normalize_included_products(payload.get("includedProducts"), item_type)
        display_category_ids = self._normalize_string_list(payload.get("displayCategoryIds"), "displayCategoryIds")
        client_product_id = self._unique_client_product_id(item_type, name)
        if self._product_exists(client_product_id):
            raise AroraConflictError("clientProductId already exists")

        now = datetime.now(UTC).isoformat()
        display_name = str(payload.get("displayName") or "").strip() or name
        _insert_mock_product(
            self.db,
            {
                "client_product_id": client_product_id,
                "name": name,
                "display_name": display_name,
                "customer_price": customer_price,
                "item_type": item_type,
                "included_products": json.dumps(included_products, sort_keys=True),
                "description": str(payload.get("description") or "").strip(),
                "display_description": str(payload.get("displayDescription") or "").strip(),
                "show_patient": 1 if self._normalize_bool(payload.get("showPatient"), True) else 0,
                "display_category_ids": json.dumps(display_category_ids, sort_keys=True),
                "status": status,
                "created_at": now,
                "updated_at": now,
            },
        )
        return self._get_product(client_product_id, "Unable to create mock Arora product")

    def update_product(self, client_product_id: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        existing = self.db.execute(
            "SELECT * FROM arora_mock_products WHERE client_product_id = ?",
            (client_product_id,),
        ).fetchone()
        if existing is None:
            raise AroraNotFoundError("Mock Arora product not found")

        item_type = self._normalize_item_type(payload["itemType"] if "itemType" in payload else existing["item_type"])
        status = self._normalize_product_status(payload.get("status") or existing["status"])
        name = self._required(
            payload["name"] if "name" in payload and payload["name"] is not None else existing["name"],
            "Product/package name",
        )
        display_name = (
            payload["displayName"]
            if "displayName" in payload and payload["displayName"] is not None
            else existing["display_name"]
        ).strip() or name
        customer_price = (
            self._normalize_customer_price(payload["customerPrice"], required=True)
            if "customerPrice" in payload and payload["customerPrice"] is not None
            else float(existing["customer_price"])
        )
        included_products = self._normalize_included_products(
            payload["includedProducts"] if "includedProducts" in payload else self._json_list(existing["included_products"]),
            item_type,
        )
        display_category_ids = self._normalize_string_list(
            payload["displayCategoryIds"]
            if "displayCategoryIds" in payload
            else self._json_list(existing["display_category_ids"]),
            "displayCategoryIds",
        )

        self.db.execute(
            """
            UPDATE arora_mock_products
            SET
                name = ?,
                display_name = ?,
                customer_price = ?,
                item_type = ?,
                included_products = ?,
                description = ?,
                display_description = ?,
                show_patient = ?,
                display_category_ids = ?,
                status = ?,
                updated_at = ?
            WHERE client_product_id = ?
            """,
            (
                name,
                display_name,
                customer_price,
                item_type,
                json.dumps(included_products, sort_keys=True),
                (
                    payload["description"]
                    if "description" in payload and payload["description"] is not None
                    else existing["description"]
                ).strip(),
                (
                    payload["displayDescription"]
                    if "displayDescription" in payload and payload["displayDescription"] is not None
                    else existing["display_description"]
                ).strip(),
                1 if self._normalize_bool(
                    payload["showPatient"] if "showPatient" in payload else bool(existing["show_patient"]),
                    True,
                ) else 0,
                json.dumps(display_category_ids, sort_keys=True),
                status,
                datetime.now(UTC).isoformat(),
                client_product_id,
            ),
        )
        return self._get_product(client_product_id, "Unable to update mock Arora product")

    def delete_product(self, client_product_id: str) -> dict[str, Any]:
        if not self._product_exists(client_product_id):
            raise AroraNotFoundError("Mock Arora product not found")

        self.db.execute("DELETE FROM arora_mock_products WHERE client_product_id = ?", (client_product_id,))
        return {"deleted": True, "clientProductId": client_product_id}

    def get_patient_visible_product(self, client_product_id: str) -> dict[str, Any] | None:
        product = self.db.execute(
            """
            SELECT *
            FROM arora_mock_products
            WHERE client_product_id = ?
              AND status = 'active'
              AND show_patient = 1
            """,
            (client_product_id,),
        ).fetchone()
        return self._public_product(product) if product is not None else None

    def list_conversations(
        self,
        *,
        patient_id: str | None = None,
        status: str | None = None,
        updated_since: str | None = None,
        limit: int = 200,
        include_admin: bool = False,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: list[Any] = []
        if patient_id:
            conditions.append("conversations.patient_id = ?")
            params.append(patient_id)
        if status:
            conditions.append("conversations.status = ?")
            params.append(_normalize_conversation_status(status))
        if updated_since:
            conditions.append("conversations.updated_at >= ?")
            params.append(updated_since)
        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        rows = self.db.execute(f"{_conversation_list_query(where_clause)} LIMIT ?", (*params, limit)).fetchall()
        return [_public_conversation(row, include_admin=include_admin) for row in rows]

    def create_conversation(
        self,
        *,
        patient_id: str,
        subject: str = "Care team",
        author: Literal["client", "patient"] = "client",
        sender_name: str | None = None,
        sender_user_id: str | None = None,
        text: str | None = None,
        attachments: list[dict[str, Any]] | None = None,
        include_admin: bool = False,
    ) -> dict[str, Any]:
        patient = self.db.execute(
            """
            SELECT patients.*, partners.clinic_name AS partner_name
            FROM patients
            JOIN partners ON partners.id = patients.partner_id
            WHERE patients.id = ?
            """,
            (patient_id,),
        ).fetchone()
        if patient is None:
            raise AroraNotFoundError("Patient not found")

        now = datetime.now(UTC).isoformat()
        conversation_id = f"mock_conv_{uuid.uuid4().hex}"
        self.db.execute(
            """
            INSERT INTO arora_mock_conversations (
                id, partner_id, patient_id, status, subject, created_at, updated_at
            )
            VALUES (?, ?, ?, 'active', ?, ?, ?)
            """,
            (conversation_id, patient["partner_id"], patient["id"], subject.strip() or "Care team", now, now),
        )
        if text is not None or attachments:
            self.create_message(
                conversation_id,
                author=author,
                sender_name=sender_name,
                sender_user_id=sender_user_id,
                text=text,
                attachments=attachments or [],
                patient_id=patient["id"] if author == "patient" else None,
            )
        return self.get_conversation(conversation_id, patient_id=patient_id if not include_admin else None, include_admin=include_admin)

    def get_conversation(
        self,
        conversation_id: str,
        *,
        patient_id: str | None = None,
        include_admin: bool = False,
    ) -> dict[str, Any]:
        conditions = ["conversations.id = ?"]
        params: list[Any] = [conversation_id]
        if patient_id:
            conditions.append("conversations.patient_id = ?")
            params.append(patient_id)
        row = self.db.execute(_conversation_list_query(f"WHERE {' AND '.join(conditions)}"), params).fetchone()
        if row is None:
            raise AroraNotFoundError("Conversation not found")
        return _public_conversation(row, include_admin=include_admin)

    def update_conversation_status(self, conversation_id: str, status: str, *, include_admin: bool = False) -> dict[str, Any]:
        self.get_conversation(conversation_id)
        now = datetime.now(UTC).isoformat()
        self.db.execute(
            """
            UPDATE arora_mock_conversations
            SET status = ?, updated_at = ?
            WHERE id = ?
            """,
            (_normalize_conversation_status(status), now, conversation_id),
        )
        return self.get_conversation(conversation_id, include_admin=include_admin)

    def archive_conversation(self, conversation_id: str, *, include_admin: bool = False) -> dict[str, Any]:
        return self.update_conversation_status(conversation_id, "archived", include_admin=include_admin)

    def escalate_conversation(
        self,
        conversation_id: str,
        *,
        reason: str | None = None,
        include_admin: bool = False,
    ) -> dict[str, Any]:
        self.get_conversation(conversation_id)
        now = datetime.now(UTC).isoformat()
        self.db.execute(
            """
            UPDATE arora_mock_conversations
            SET escalation_reason = ?, escalated_at = ?, updated_at = ?
            WHERE id = ?
            """,
            ((reason or "").strip() or None, now, now, conversation_id),
        )
        return self.get_conversation(conversation_id, include_admin=include_admin)

    def list_messages(self, conversation_id: str, *, patient_id: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        self.get_conversation(conversation_id, patient_id=patient_id)
        rows = self.db.execute(
            """
            SELECT *
            FROM arora_mock_conversation_messages
            WHERE conversation_id = ?
            ORDER BY created_at ASC
            LIMIT ?
            """,
            (conversation_id, limit),
        ).fetchall()
        return [_public_message(row) for row in rows]

    def get_message(self, conversation_id: str, message_id: str) -> dict[str, Any]:
        return _public_message(self._get_message_row(conversation_id, message_id))

    def create_message(
        self,
        conversation_id: str,
        *,
        author: Literal["client", "patient"],
        sender_name: str | None,
        sender_user_id: str | None = None,
        text: str | None,
        attachments: list[dict[str, Any]],
        patient_id: str | None = None,
        include_admin: bool = False,
    ) -> dict[str, Any]:
        conversation = self.get_conversation(conversation_id)
        if patient_id is not None and conversation["patientId"] != patient_id:
            raise AroraValidationError("patientId does not match the conversation patient")

        normalized_attachments = _normalize_message_attachments(attachments)
        normalized_text = _normalize_message_text(text, normalized_attachments)
        normalized_sender_name = (sender_name or "").strip()
        if not normalized_sender_name:
            normalized_sender_name = "Patient" if author == "patient" else "Care Team"

        now = datetime.now(UTC).isoformat()
        message_id = f"mock_msg_{uuid.uuid4().hex}"
        self.db.execute(
            """
            INSERT INTO arora_mock_conversation_messages (
                id, conversation_id, author, sender_user_id, sender_name, text, attachments, updated_at, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                message_id,
                conversation_id,
                author,
                (sender_user_id or "").strip() or None,
                normalized_sender_name,
                normalized_text,
                json.dumps(normalized_attachments, sort_keys=True),
                now,
                now,
            ),
        )
        self.db.execute(
            """
            UPDATE arora_mock_conversations
            SET updated_at = ?
            WHERE id = ?
            """,
            (now, conversation_id),
        )
        return {
            "message": self.get_message(conversation_id, message_id),
            "conversation": self.get_conversation(conversation_id, include_admin=include_admin),
        }

    def update_message(self, conversation_id: str, message_id: str, *, text: str, include_admin: bool = False) -> dict[str, Any]:
        self._get_message_row(conversation_id, message_id)
        now = datetime.now(UTC).isoformat()
        self.db.execute(
            """
            UPDATE arora_mock_conversation_messages
            SET text = ?, updated_at = ?
            WHERE conversation_id = ? AND id = ?
            """,
            (_normalize_message_text(text, []), now, conversation_id, message_id),
        )
        self.db.execute(
            """
            UPDATE arora_mock_conversations
            SET updated_at = ?
            WHERE id = ?
            """,
            (now, conversation_id),
        )
        return {
            "message": self.get_message(conversation_id, message_id),
            "conversation": self.get_conversation(conversation_id, include_admin=include_admin),
        }

    def delete_message(self, conversation_id: str, message_id: str, *, include_admin: bool = False) -> dict[str, Any]:
        self._get_message_row(conversation_id, message_id)
        now = datetime.now(UTC).isoformat()
        self.db.execute(
            "DELETE FROM arora_mock_conversation_messages WHERE conversation_id = ? AND id = ?",
            (conversation_id, message_id),
        )
        self.db.execute(
            """
            UPDATE arora_mock_conversations
            SET updated_at = ?
            WHERE id = ?
            """,
            (now, conversation_id),
        )
        return {
            "deleted": True,
            "messageId": message_id,
            "conversation": self.get_conversation(conversation_id, include_admin=include_admin),
        }

    def _get_message_row(self, conversation_id: str, message_id: str) -> sqlite3.Row:
        row = self.db.execute(
            """
            SELECT *
            FROM arora_mock_conversation_messages
            WHERE conversation_id = ? AND id = ?
            """,
            (conversation_id, message_id),
        ).fetchone()
        if row is None:
            raise AroraNotFoundError("Message not found")
        return row

    def _get_product(self, client_product_id: str, failure_message: str) -> dict[str, Any]:
        product = self.db.execute("SELECT * FROM arora_mock_products WHERE client_product_id = ?", (client_product_id,)).fetchone()
        if product is None:
            raise AroraClientError(failure_message)
        return self._public_product(product)

    def _product_exists(self, client_product_id: str) -> bool:
        return self.db.execute("SELECT 1 FROM arora_mock_products WHERE client_product_id = ?", (client_product_id,)).fetchone() is not None

    def _unique_client_product_id(self, item_type: str | None, name: str) -> str:
        prefix = "package" if item_type == "package" else "product"
        base_id = f"mock_{prefix}_{self._slugify_identifier(name)}"
        candidate = base_id
        suffix = 2
        while self._product_exists(candidate):
            candidate = f"{base_id}_{suffix}"
            suffix += 1
        return candidate

    def _normalize_included_products(self, value: object, item_type: str | None) -> list[dict[str, str]]:
        raw_products = value or []
        if not isinstance(raw_products, list):
            raise AroraValidationError("includedProducts must be a list")

        included_products: list[dict[str, str]] = []
        for product in raw_products:
            client_product_id = ""
            if isinstance(product, Mapping):
                client_product_id = str(product.get("clientProductId") or "").strip()
            elif isinstance(product, str):
                client_product_id = product.strip()
            if not client_product_id:
                raise AroraValidationError("includedProducts entries require clientProductId")
            included_products.append({"clientProductId": client_product_id})

        if item_type != "package":
            return []

        unique_ids = {product["clientProductId"] for product in included_products}
        if len(unique_ids) < 2:
            raise AroraValidationError("Packages require at least 2 included active product clientProductIds")

        placeholders = ",".join("?" for _ in unique_ids)
        rows = self.db.execute(
            f"""
            SELECT client_product_id, item_type, status
            FROM arora_mock_products
            WHERE client_product_id IN ({placeholders})
            """,
            tuple(unique_ids),
        ).fetchall()
        valid_ids = {
            row["client_product_id"]
            for row in rows
            if row["status"] == "active" and row["item_type"] is None
        }
        if valid_ids != unique_ids:
            raise AroraValidationError("Packages can only include active, non-package clientProductIds")

        return included_products

    @staticmethod
    def _normalize_item_type(value: object) -> str | None:
        item_type = str(value or "").strip().lower()
        if not item_type:
            return None
        if item_type != "package":
            raise AroraValidationError("itemType must be package or omitted")
        return item_type

    @staticmethod
    def _normalize_product_status(value: object) -> str:
        status = str(value or "active").strip().lower()
        if status not in {"active", "inactive"}:
            raise AroraValidationError("Product status must be active or inactive")
        return status

    @staticmethod
    def _normalize_customer_price(value: object, required: bool) -> float:
        if value in (None, ""):
            if required:
                raise AroraValidationError("customerPrice is required")
            return 0
        try:
            price = float(value)
        except (TypeError, ValueError) as error:
            raise AroraValidationError("customerPrice must be a non-negative USD amount") from error
        if price < 0:
            raise AroraValidationError("customerPrice must be non-negative")
        return round(price, 2)

    @staticmethod
    def _normalize_string_list(value: object, label: str) -> list[str]:
        raw_values = value or []
        if isinstance(raw_values, str):
            raw_values = [part.strip() for part in raw_values.split(",")]
        if not isinstance(raw_values, list):
            raise AroraValidationError(f"{label} must be a list")
        return [str(item).strip() for item in raw_values if str(item).strip()]

    @staticmethod
    def _normalize_bool(value: object, fallback: bool) -> bool:
        if value is None:
            return fallback
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        normalized = str(value).strip().lower()
        if normalized in {"true", "1", "yes", "on"}:
            return True
        if normalized in {"false", "0", "no", "off"}:
            return False
        raise AroraValidationError("showPatient must be boolean")

    @staticmethod
    def _required(value: object, label: str) -> str:
        cleaned = str(value or "").strip()
        if not cleaned:
            raise AroraValidationError(f"{label} is required")
        return cleaned

    @staticmethod
    def _slugify_identifier(value: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")
        return slug or uuid.uuid4().hex[:8]

    @staticmethod
    def _json_list(value: object) -> list[Any]:
        return _json_list(value)

    @staticmethod
    def _public_product(product: sqlite3.Row) -> dict[str, Any]:
        return {
            "clientProductId": product["client_product_id"],
            "name": product["name"],
            "displayName": product["display_name"],
            "customerPrice": product["customer_price"],
            "itemType": product["item_type"],
            "includedProducts": _json_list(product["included_products"]),
            "status": product["status"],
            "showPatient": bool(product["show_patient"]),
            "displayCategoryIds": _json_list(product["display_category_ids"]),
            "description": product["description"],
            "displayDescription": product["display_description"],
            "createdAt": product["created_at"],
            "updatedAt": product["updated_at"],
        }


def _conversation_list_query(where_clause: str = "") -> str:
    return f"""
        SELECT
            conversations.*,
            patients.name AS patient_name,
            patients.email AS patient_email,
            partners.clinic_name AS partner_name,
            (
                SELECT COUNT(*)
                FROM arora_mock_conversation_messages messages
                WHERE messages.conversation_id = conversations.id
            ) AS message_count,
            (
                SELECT messages.text
                FROM arora_mock_conversation_messages messages
                WHERE messages.conversation_id = conversations.id
                ORDER BY messages.created_at DESC
                LIMIT 1
            ) AS last_message_text,
            (
                SELECT messages.created_at
                FROM arora_mock_conversation_messages messages
                WHERE messages.conversation_id = conversations.id
                ORDER BY messages.created_at DESC
                LIMIT 1
            ) AS last_message_at
        FROM arora_mock_conversations conversations
        JOIN patients ON patients.id = conversations.patient_id
        JOIN partners ON partners.id = conversations.partner_id
        {where_clause}
        ORDER BY conversations.updated_at DESC, conversations.created_at DESC
    """


def _public_conversation(conversation: sqlite3.Row, *, include_admin: bool = False) -> dict[str, Any]:
    public_conversation: dict[str, Any] = {
        "conversationId": conversation["id"],
        "patientId": conversation["patient_id"],
        "status": conversation["status"],
        "subject": conversation["subject"],
        "escalationReason": conversation["escalation_reason"],
        "escalatedAt": conversation["escalated_at"],
        "messageCount": conversation["message_count"],
        "lastMessageText": conversation["last_message_text"],
        "lastMessageAt": conversation["last_message_at"],
        "createdAt": conversation["created_at"],
        "updatedAt": conversation["updated_at"],
    }
    if include_admin:
        public_conversation.update(
            {
                "partnerId": conversation["partner_id"],
                "partnerName": conversation["partner_name"],
                "patientName": conversation["patient_name"],
                "patientEmail": conversation["patient_email"],
            }
        )
    return public_conversation


def _public_message(message: sqlite3.Row) -> dict[str, Any]:
    return {
        "messageId": message["id"],
        "conversationId": message["conversation_id"],
        "author": message["author"],
        "senderUserId": message["sender_user_id"],
        "senderName": message["sender_name"],
        "text": message["text"],
        "attachments": _json_list(message["attachments"]),
        "updatedAt": message["updated_at"],
        "createdAt": message["created_at"],
    }


def _json_list(value: object) -> list[Any]:
    if isinstance(value, list):
        return value
    try:
        parsed = json.loads(str(value or "[]"))
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else []


def _normalize_conversation_status(value: str) -> str:
    status = value.strip().lower()
    if status not in {"active", "closed", "archived"}:
        raise AroraValidationError("Conversation status must be active, closed, or archived")
    return status


def _normalize_message_attachments(attachments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(attachments) > 10:
        raise AroraValidationError("Messages support up to 10 attachments")

    normalized: list[dict[str, Any]] = []
    for attachment in attachments:
        url = str(attachment.get("url") or "").strip()
        if not url:
            raise AroraValidationError("Attachment URL is required")
        public_attachment: dict[str, Any] = {"url": url}
        for source_key, target_key in (
            ("name", "name"),
            ("mimeType", "mimeType"),
            ("mime_type", "mimeType"),
            ("size", "size"),
        ):
            if source_key in attachment and attachment[source_key] not in (None, ""):
                public_attachment[target_key] = attachment[source_key]
        normalized.append(public_attachment)
    return normalized


def _normalize_message_text(text: str | None, attachments: list[dict[str, Any]]) -> str:
    normalized_text = (text or "").strip()
    if len(normalized_text) > 5000:
        raise AroraValidationError("Message text must be 5000 characters or fewer")
    if not normalized_text and not attachments:
        raise AroraValidationError("Message text or attachments are required")
    return normalized_text
