import json
import re
import sqlite3
import uuid
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any


class AroraClientError(Exception):
    pass


class AroraValidationError(AroraClientError):
    pass


class AroraConflictError(AroraClientError):
    pass


class AroraNotFoundError(AroraClientError):
    pass


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

    def list_products(
        self,
        item_type: str | None = None,
        include_inactive: bool = True,
    ) -> list[dict[str, Any]]:
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

        self.db.execute(
            "DELETE FROM arora_mock_products WHERE client_product_id = ?",
            (client_product_id,),
        )
        return {"deleted": True, "clientProductId": client_product_id}

    def _get_product(self, client_product_id: str, failure_message: str) -> dict[str, Any]:
        product = self.db.execute(
            "SELECT * FROM arora_mock_products WHERE client_product_id = ?",
            (client_product_id,),
        ).fetchone()
        if product is None:
            raise AroraClientError(failure_message)
        return self._public_product(product)

    def _product_exists(self, client_product_id: str) -> bool:
        return (
            self.db.execute(
                "SELECT 1 FROM arora_mock_products WHERE client_product_id = ?",
                (client_product_id,),
            ).fetchone()
            is not None
        )

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
        if isinstance(value, list):
            return value
        try:
            parsed = json.loads(str(value or "[]"))
        except json.JSONDecodeError:
            return []
        return parsed if isinstance(parsed, list) else []

    @staticmethod
    def _public_product(product: sqlite3.Row) -> dict[str, Any]:
        return {
            "clientProductId": product["client_product_id"],
            "name": product["name"],
            "displayName": product["display_name"],
            "customerPrice": product["customer_price"],
            "itemType": product["item_type"],
            "includedProducts": MockAroraClient._json_list(product["included_products"]),
            "status": product["status"],
            "showPatient": bool(product["show_patient"]),
            "displayCategoryIds": MockAroraClient._json_list(product["display_category_ids"]),
            "description": product["description"],
            "displayDescription": product["display_description"],
            "createdAt": product["created_at"],
            "updatedAt": product["updated_at"],
        }
