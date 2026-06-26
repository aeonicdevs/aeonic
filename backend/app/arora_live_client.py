import json
import os
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from typing import Any, Literal

from app.arora_client import AroraClientError, AroraNotFoundError, AroraValidationError


# Real Arora HTTP integration lives here. Do not add SQLite-backed fallback
# behavior to this class; if a feature needs local simulation, implement the
# matching method in MockAroraClient and keep this class focused on /v2/client
# requests, payload translation, and Arora error mapping.
class LiveAroraClient:
    mode = "live"

    def __init__(self, *, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key if api_key is not None else os.getenv("ARORA_API_KEY")
        self.base_url = (base_url or os.getenv("ARORA_API_BASE_URL", "https://api.gen-health.app")).rstrip("/")

    def create_patient(self, patient_payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/v2/client/patients", patient_payload)

    def create_order(self, order_payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/v2/client/orders", order_payload)

    def list_products(self, item_type: str | None = None, include_inactive: bool = True) -> list[dict[str, Any]]:
        query: dict[str, str | int] = {}
        if item_type:
            query["itemType"] = item_type
        if include_inactive:
            query["includeInactive"] = 1
        response = self._request("GET", "/v2/client/products", query=query or None)
        return _collection(response, "products")

    def create_product(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        response = self._request("POST", "/v2/client/products", dict(payload))
        return _entity(response, "product")

    def update_product(self, client_product_id: str, payload: Mapping[str, Any]) -> dict[str, Any]:
        response = self._request("PATCH", f"/v2/client/products/{_quote(client_product_id)}", dict(payload))
        return _entity(response, "product")

    def delete_product(self, client_product_id: str) -> dict[str, Any]:
        response = self._request("DELETE", f"/v2/client/products/{_quote(client_product_id)}")
        if isinstance(response, dict) and response:
            return response
        return {"deleted": True, "clientProductId": client_product_id}

    def get_patient_visible_product(self, client_product_id: str) -> dict[str, Any] | None:
        try:
            response = self._request("GET", f"/v2/client/products/{_quote(client_product_id)}")
        except AroraNotFoundError:
            return None
        product = _entity(response, "product")
        if product.get("status") == "inactive" or product.get("showPatient") is False:
            return None
        return product

    def list_conversations(
        self,
        *,
        patient_id: str | None = None,
        status: str | None = None,
        updated_since: str | None = None,
        limit: int = 200,
        include_admin: bool = False,
    ) -> list[dict[str, Any]]:
        query: dict[str, str | int] = {"limit": limit}
        if patient_id:
            query["patientId"] = patient_id
        if status:
            query["status"] = status
        if updated_since:
            query["updatedSince"] = updated_since
        response = self._request("GET", "/v2/client/conversations", query=query)
        return _collection(response, "conversations")

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
        response = self._request("POST", "/v2/client/conversations", {"patientId": patient_id})
        conversation = _entity(response, "conversation")
        conversation_id = str(conversation.get("conversationId") or conversation.get("id") or "")
        if not conversation_id:
            raise AroraClientError("Arora did not return a conversation ID")
        if text is not None or attachments:
            self.create_message(
                conversation_id,
                author=author,
                sender_name=sender_name,
                sender_user_id=sender_user_id,
                text=text,
                attachments=attachments or [],
                patient_id=patient_id if author == "patient" else None,
                include_admin=include_admin,
            )
            return self.get_conversation(conversation_id)
        return conversation

    def get_conversation(
        self,
        conversation_id: str,
        *,
        patient_id: str | None = None,
        include_admin: bool = False,
    ) -> dict[str, Any]:
        conversation = _entity(
            self._request("GET", f"/v2/client/conversations/{_quote(conversation_id)}"),
            "conversation",
        )
        if patient_id and conversation.get("patientId") not in {patient_id, None}:
            raise AroraNotFoundError("Conversation not found")
        return conversation

    def update_conversation_status(self, conversation_id: str, status: str, *, include_admin: bool = False) -> dict[str, Any]:
        return _entity(
            self._request("PATCH", f"/v2/client/conversations/{_quote(conversation_id)}", {"status": status}),
            "conversation",
        )

    def archive_conversation(self, conversation_id: str, *, include_admin: bool = False) -> dict[str, Any]:
        response = self._request("DELETE", f"/v2/client/conversations/{_quote(conversation_id)}")
        return _entity(response, "conversation") if isinstance(response, dict) and response else {"conversationId": conversation_id, "status": "archived"}

    def escalate_conversation(
        self,
        conversation_id: str,
        *,
        reason: str | None = None,
        include_admin: bool = False,
    ) -> dict[str, Any]:
        return _entity(
            self._request(
                "POST",
                f"/v2/client/conversations/{_quote(conversation_id)}/escalations",
                {"reason": reason} if reason else {},
            ),
            "conversation",
        )

    def list_messages(self, conversation_id: str, *, patient_id: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        query: dict[str, int] = {"limit": limit}
        response = self._request("GET", f"/v2/client/conversations/{_quote(conversation_id)}/messages", query=query)
        return _collection(response, "messages")

    def get_message(self, conversation_id: str, message_id: str) -> dict[str, Any]:
        return _entity(
            self._request(
                "GET",
                f"/v2/client/conversations/{_quote(conversation_id)}/messages/{_quote(message_id)}",
            ),
            "message",
        )

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
        payload: dict[str, Any] = {
            "author": author,
            "text": text,
            "attachments": attachments,
        }
        if author == "patient":
            if patient_id:
                payload["patientId"] = patient_id
        else:
            if sender_user_id:
                payload["senderUserId"] = sender_user_id
            elif sender_name:
                payload["senderName"] = sender_name
        response = self._request("POST", f"/v2/client/conversations/{_quote(conversation_id)}/messages", _without_empty(payload))
        return {
            "message": _entity(response, "message"),
            "conversation": self.get_conversation(conversation_id),
        }

    def update_message(self, conversation_id: str, message_id: str, *, text: str, include_admin: bool = False) -> dict[str, Any]:
        response = self._request(
            "PATCH",
            f"/v2/client/conversations/{_quote(conversation_id)}/messages/{_quote(message_id)}",
            {"text": text},
        )
        return {
            "message": _entity(response, "message"),
            "conversation": self.get_conversation(conversation_id),
        }

    def delete_message(self, conversation_id: str, message_id: str, *, include_admin: bool = False) -> dict[str, Any]:
        self._request("DELETE", f"/v2/client/conversations/{_quote(conversation_id)}/messages/{_quote(message_id)}")
        return {
            "deleted": True,
            "messageId": message_id,
            "conversation": self.get_conversation(conversation_id),
        }

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        query: dict[str, str | int] | None = None,
    ) -> dict[str, Any]:
        if not self.api_key:
            raise AroraClientError("Arora API key is not configured")

        url = f"{self.base_url}{path}"
        if query:
            url = f"{url}?{urllib.parse.urlencode(query)}"

        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "X-API-Key": self.api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read().decode("utf-8")
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as error:
            detail = _error_detail(error)
            if error.code == 404:
                raise AroraNotFoundError(detail) from error
            if error.code in {400, 422}:
                raise AroraValidationError(detail) from error
            raise AroraClientError(detail) from error
        except urllib.error.URLError as error:
            raise AroraClientError(f"Arora request failed: {error.reason}") from error


def _quote(value: str) -> str:
    return urllib.parse.quote(value, safe="")


def _without_empty(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if value not in (None, "", [])}


def _entity(response: dict[str, Any], key: str) -> dict[str, Any]:
    if key in response and isinstance(response[key], dict):
        return response[key]
    data = response.get("data")
    if isinstance(data, dict):
        if key in data and isinstance(data[key], dict):
            return data[key]
        return data
    return response


def _collection(response: dict[str, Any], key: str) -> list[dict[str, Any]]:
    if key in response and isinstance(response[key], list):
        return response[key]
    data = response.get("data")
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get(key), list):
        return data[key]
    return []


def _error_detail(error: urllib.error.HTTPError) -> str:
    body = error.read().decode("utf-8", errors="replace")
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        return body or error.reason
    return str(parsed.get("detail") or parsed.get("message") or parsed.get("error") or parsed)
