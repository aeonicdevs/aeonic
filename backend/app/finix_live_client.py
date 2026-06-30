import base64
import json
import os
import urllib.error
import urllib.request
from typing import Any, Literal

from app.finix_client import FinixConfigurationError, FinixValidationError


class LiveFinixClient:
    def __init__(self, *, mode: Literal["sandbox", "live"]):
        self.mode = mode

    def create_onboarding_form(
        self,
        *,
        partner_id: str,
        clinic_name: str,
        owner_name: str,
        email: str,
        return_url: str,
    ) -> dict[str, Any]:
        processor = os.getenv("FINIX_MERCHANT_PROCESSOR", "DUMMY_V1" if self.mode == "sandbox" else "").strip()
        if not processor:
            raise FinixConfigurationError("FINIX_MERCHANT_PROCESSOR is required for live Finix onboarding")

        return_base_url = return_url.rstrip("/")
        payload = {
            "merchant_processors": [processor],
            "onboarding_data": {
                "entity": {
                    "title": clinic_name,
                    "email": email,
                    "tags": {
                        "aeonic_partner_id": partner_id,
                    },
                },
                "associated_entities": [
                    {
                        "title": owner_name,
                        "email": email,
                        "tags": {
                            "aeonic_partner_id": partner_id,
                            "aeonic_role": "owner",
                        },
                    }
                ],
            },
            "onboarding_link_details": {
                "return_url": f"{return_base_url}/partner-finix-return",
                "expired_session_url": f"{return_base_url}/partner-finix-return?expired=1",
                "terms_of_service_url": os.getenv(
                    "FINIX_TERMS_OF_SERVICE_URL",
                    "https://www.aeonichealthsystems.com/terms",
                ),
            },
            "tags": {
                "aeonic_partner_id": partner_id,
            },
        }
        return self._request("POST", "/onboarding_forms", payload)

    def get_onboarding_form(self, form_id: str) -> dict[str, Any]:
        return self._request("GET", f"/onboarding_forms/{form_id}")

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        username = os.getenv("FINIX_USERNAME", "").strip()
        password = os.getenv("FINIX_PASSWORD", "").strip()
        if not username or not password:
            raise FinixConfigurationError("FINIX_USERNAME and FINIX_PASSWORD are required")

        url = f"{self._base_url()}{path}"
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        basic = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("ascii")
        request = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Authorization": f"Basic {basic}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Finix-Version": os.getenv("FINIX_VERSION", "2022-02-01"),
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(body)
            except json.JSONDecodeError:
                parsed = {"message": body or error.reason}
            message = parsed.get("message") or parsed.get("error") or f"Finix request failed with HTTP {error.code}"
            raise FinixValidationError(str(message)) from error
        except urllib.error.URLError as error:
            raise FinixValidationError(f"Finix request failed: {error.reason}") from error

    def _base_url(self) -> str:
        configured = os.getenv("FINIX_API_BASE_URL", "").strip().rstrip("/")
        if configured:
            return configured
        if self.mode == "sandbox":
            return "https://finix.sandbox-payments-api.com"
        return "https://finix.live-payments-api.com"
