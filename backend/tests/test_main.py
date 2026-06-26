from fastapi.testclient import TestClient
from uuid import uuid4

import app.main as main
from app.arora_live_client import LiveAroraClient
from app.main import create_app


def test_health() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root() -> None:
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["name"] == "Aeonic API"


def test_partner_configures_domain_and_patient_authenticates() -> None:
    client = TestClient(create_app())
    suffix = uuid4().hex[:8]
    clinic_domain = f"smile-{suffix}.example.com"

    partner_signup = client.post(
        "/partners/signup",
        json={
            "owner_name": "Dr. Avery Lane",
            "email": f"avery-{suffix}@example.com",
            "password": "secret123",
            "clinic_name": "Avery Dental",
        },
    )
    assert partner_signup.status_code == 200
    partner_token = partner_signup.json()["token"]

    settings = client.patch(
        "/partners/settings",
        headers={"Authorization": f"Bearer {partner_token}"},
        json={"clinic_domain": clinic_domain},
    )
    assert settings.status_code == 200
    assert settings.json()["partner"]["clinicDomain"] == clinic_domain

    context = client.get("/nexus/context", params={"host": clinic_domain})
    assert context.status_code == 200
    assert context.json()["partner"]["clinicName"] == "Avery Dental"

    preflight = client.options(
        "/nexus/context",
        headers={
            "Origin": f"https://{clinic_domain}",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )
    assert preflight.status_code == 200
    assert preflight.headers["access-control-allow-origin"] == f"https://{clinic_domain}"

    patient_signup = client.post(
        "/patients/signup",
        json={
            "host": clinic_domain,
            "name": "Mira Chen",
            "email": f"mira-{suffix}@example.com",
            "password": "secret123",
        },
    )
    assert patient_signup.status_code == 200
    assert patient_signup.json()["partner"]["clinicDomain"] == clinic_domain

    patient_login = client.post(
        "/patients/login",
        json={
            "host": clinic_domain,
            "email": f"mira-{suffix}@example.com",
            "password": "secret123",
        },
    )
    assert patient_login.status_code == 200
    patient_token = patient_login.json()["token"]

    me = client.get("/patients/me", headers={"Authorization": f"Bearer {patient_token}"})
    assert me.status_code == 200
    assert me.json()["patient"]["name"] == "Mira Chen"


def _create_patient_session(client: TestClient, suffix: str) -> tuple[str, str]:
    clinic_domain = f"care-{suffix}.example.com"
    partner_signup = client.post(
        "/partners/signup",
        json={
            "owner_name": "Dr. Care",
            "email": f"care-{suffix}@example.com",
            "password": "secret123",
            "clinic_name": "Care Clinic",
        },
    )
    assert partner_signup.status_code == 200

    settings = client.patch(
        "/partners/settings",
        headers={"Authorization": f"Bearer {partner_signup.json()['token']}"},
        json={"clinic_domain": clinic_domain},
    )
    assert settings.status_code == 200

    patient_signup = client.post(
        "/patients/signup",
        json={
            "host": clinic_domain,
            "name": "Mira Chen",
            "email": f"mira-care-{suffix}@example.com",
            "password": "secret123",
        },
    )
    assert patient_signup.status_code == 200
    return patient_signup.json()["token"], patient_signup.json()["patient"]["id"]


def test_patient_medication_shipment_defaults_to_mock_order(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("ARORA_API_MODE", raising=False)
    monkeypatch.delenv("ARORA_API_KEY", raising=False)
    monkeypatch.delenv("ARORA_DRY_RUN", raising=False)
    client = TestClient(create_app(tmp_path / "aeonic.sqlite3"))
    suffix = uuid4().hex[:8]
    patient_token, patient_id = _create_patient_session(client, suffix)

    products = client.get(
        "/patients/arora/products",
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert products.status_code == 200
    assert products.json()["mode"] == "mock"
    assert any(
        product["clientProductId"] == "mock_client_product_order"
        for product in products.json()["products"]
    )

    empty_response = client.post(
        "/patients/medication-shipments",
        headers={"Authorization": f"Bearer {patient_token}"},
        json={},
    )
    assert empty_response.status_code == 422

    response = client.post(
        "/patients/medication-shipments",
        headers={"Authorization": f"Bearer {patient_token}"},
        json={"client_product_id": "mock_client_product_order", "amount": "199.00"},
    )

    assert response.status_code == 200
    shipment = response.json()["medicationShipment"]
    assert shipment["dryRun"] is False
    assert shipment["status"] == "pending_review"
    assert shipment["patientId"] == patient_id
    assert shipment["aroraPatientId"] == f"mock_patient_{patient_id}"
    assert shipment["aroraOrderId"].startswith("mock_order_")
    assert shipment["clientProductId"] == "mock_client_product_order"
    assert shipment["request"]["patientEndpoint"] == "POST /v2/client/patients"
    assert shipment["request"]["orderEndpoint"] == "POST /v2/client/orders"
    assert shipment["request"]["patient"]["patient"]["partnerPatientId"] == patient_id
    assert shipment["request"]["patient"]["patient"]["phone"] == "5551234567"
    assert shipment["request"]["patient"]["patient"]["dateOfBirth"] == "1990-01-01"
    assert shipment["request"]["order"]["order"]["payment_status"] == "paid"
    assert shipment["request"]["order"]["order"]["amount"] == "199.00"
    assert shipment["request"]["product"]["clientProductId"] == "mock_client_product_order"
    assert shipment["response"]["order"]["data"]["orderStatus"] == "pending_review"
    assert shipment["response"]["order"]["data"]["requiredActions"] == []

    orders = client.get(
        "/patients/arora/orders",
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert orders.status_code == 200
    order = orders.json()["orders"][0]
    assert order["orderId"] == shipment["aroraOrderId"]
    assert order["clientProductId"] == "mock_client_product_order"
    assert order["paymentStatus"] == "paid"
    assert order["amount"] == 19900

    forms = client.get(
        f"/patients/arora/orders/{shipment['aroraOrderId']}/forms",
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert forms.status_code == 200
    assert forms.json()["order"]["orderId"] == shipment["aroraOrderId"]
    assert forms.json()["forms"][0]["formKey"] == "provider_network:mock:intake"

    labs = client.get(
        "/patients/arora/labs",
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert labs.status_code == 200
    assert any(lab["clientProductId"] == "mock_lab_foundation_panel" for lab in labs.json()["labs"])

    visits = client.get(
        "/patients/arora/visits",
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert visits.status_code == 200
    assert visits.json()["visits"][0]["orderId"] == shipment["aroraOrderId"]

    conversations = client.get(
        "/patients/arora/conversations",
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert conversations.status_code == 200
    assert conversations.json()["conversations"] == []

    prescriptions = client.get(
        "/patients/arora/prescriptions",
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert prescriptions.status_code == 200
    assert prescriptions.json()["prescriptions"][0]["orderId"] == shipment["aroraOrderId"]

    payments = client.get(
        "/patients/arora/payments",
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert payments.status_code == 200
    assert payments.json()["payments"][0]["amount"] == 19900


def test_patient_medication_shipment_creates_arora_patient_and_order(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("ARORA_API_MODE", "live")
    monkeypatch.setenv("ARORA_API_KEY", "test-arora-key")
    client = TestClient(create_app(tmp_path / "aeonic.sqlite3"))
    suffix = uuid4().hex[:8]
    patient_token, patient_id = _create_patient_session(client, suffix)
    calls = []

    def fake_arora_api_request(self, method, path, payload=None, query=None):
        calls.append({"method": method, "path": path, "payload": payload, "query": query})
        if path == "/v2/client/products/mock_client_product_order":
            return {
                "data": {
                    "clientProductId": "mock_client_product_order",
                    "name": "Weight Optimization Program",
                    "displayName": "Weight Optimization Program",
                    "customerPrice": 199.00,
                    "itemType": None,
                    "status": "active",
                    "showPatient": True,
                }
            }
        if path == "/v2/client/patients":
            return {"success": True, "data": {"patientId": "arora_patient_123"}}
        if path == "/v2/client/orders":
            return {
                "success": True,
                "data": {
                    "orderId": "order456",
                    "patientId": "arora_patient_123",
                    "clientProductId": payload["order"]["clientProductId"],
                    "orderStatus": "pending_review",
                    "paymentStatus": "paid",
                    "requiredActions": [],
                },
            }
        raise AssertionError(f"Unexpected Arora path {path}")

    monkeypatch.setattr(LiveAroraClient, "_request", fake_arora_api_request)

    response = client.post(
        "/patients/medication-shipments",
        headers={"Authorization": f"Bearer {patient_token}"},
        json={
            "phone": "5551234567",
            "date_of_birth": "1990-05-15",
            "sex_at_birth": "female",
            "address": {
                "street1": "123 Main Street",
                "city": "Austin",
                "state": "TX",
                "zip": "78701",
            },
            "client_product_id": "mock_client_product_order",
            "amount": "199.00",
        },
    )

    assert response.status_code == 200
    shipment = response.json()["medicationShipment"]
    assert shipment["dryRun"] is False
    assert shipment["status"] == "pending_review"
    assert shipment["aroraPatientId"] == "arora_patient_123"
    assert shipment["aroraOrderId"] == "order456"
    assert calls == [
        {
            "method": "GET",
            "path": "/v2/client/products/mock_client_product_order",
            "payload": None,
            "query": None,
        },
        {
            "method": "POST",
            "path": "/v2/client/patients",
            "payload": {
                "patient": {
                    "email": f"mira-care-{suffix}@example.com",
                    "firstName": "Mira",
                    "lastName": "Chen",
                    "phone": "5551234567",
                    "partnerPatientId": patient_id,
                    "dateOfBirth": "1990-05-15",
                    "address": {
                        "street1": "123 Main Street",
                        "city": "Austin",
                        "state": "TX",
                        "zip": "78701",
                    },
                    "sexAtBirth": "female",
                },
                "send_email": False,
            },
            "query": None,
        },
        {
            "method": "POST",
            "path": "/v2/client/orders",
            "payload": {
                "patient_id": "arora_patient_123",
                "order": {
                    "clientProductId": "mock_client_product_order",
                    "payment_status": "paid",
                    "amount": "199.00",
                },
            },
            "query": None,
        },
    ]


def test_admin_can_list_and_advance_patient_orders(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("ARORA_API_MODE", raising=False)
    monkeypatch.delenv("ARORA_API_KEY", raising=False)
    monkeypatch.delenv("ARORA_DRY_RUN", raising=False)
    client = TestClient(create_app(tmp_path / "aeonic.sqlite3"))
    suffix = uuid4().hex[:8]
    patient_token, patient_id = _create_patient_session(client, suffix)

    created = client.post(
        "/patients/medication-shipments",
        headers={"Authorization": f"Bearer {patient_token}"},
        json={"client_product_id": "mock_client_product_order"},
    )
    assert created.status_code == 200
    shipment_id = created.json()["medicationShipment"]["id"]

    admin_list = client.get("/admin/medication-shipments")
    assert admin_list.status_code == 200
    admin_body = admin_list.json()
    assert admin_body["stages"][0]["value"] == "pending_review"
    assert len(admin_body["medicationShipments"]) == 1
    admin_shipment = admin_body["medicationShipments"][0]
    assert admin_shipment["id"] == shipment_id
    assert admin_shipment["patientId"] == patient_id
    assert admin_shipment["patientName"] == "Mira Chen"
    assert admin_shipment["partnerName"] == "Care Clinic"
    assert admin_shipment["status"] == "pending_review"

    updated = client.patch(
        f"/admin/medication-shipments/{shipment_id}",
        json={"status": "pharmacy_submitted"},
    )
    assert updated.status_code == 200
    assert updated.json()["medicationShipment"]["status"] == "pharmacy_submitted"

    patient_list = client.get(
        "/patients/medication-shipments",
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert patient_list.status_code == 200
    assert patient_list.json()["medicationShipments"][0]["status"] == "pharmacy_submitted"

    invalid = client.patch(
        f"/admin/medication-shipments/{shipment_id}",
        json={"status": "not_an_arora_stage"},
    )
    assert invalid.status_code == 422


def test_admin_can_manage_mock_arora_products(tmp_path) -> None:
    client = TestClient(create_app(tmp_path / "aeonic.sqlite3"))

    initial = client.get("/admin/arora/products")
    assert initial.status_code == 200
    assert initial.json()["mode"] == "mock"
    assert any(
        product["clientProductId"] == "mock_client_product_order"
        for product in initial.json()["products"]
    )

    created = client.post(
        "/admin/arora/products",
        json={
            "name": "Longevity Consult",
            "displayName": "Longevity Consult",
            "customerPrice": 249.0,
            "status": "active",
            "showPatient": True,
            "displayCategoryIds": ["longevity"],
            "description": "Internal mock consult product",
            "displayDescription": "Patient-facing longevity consult",
        },
    )
    assert created.status_code == 200
    product = created.json()["product"]
    assert product["clientProductId"] == "mock_product_longevity_consult"
    assert product["itemType"] is None
    assert product["customerPrice"] == 249.0
    assert product["showPatient"] is True
    assert product["displayCategoryIds"] == ["longevity"]

    invalid_package = client.post(
        "/admin/arora/products",
        json={
            "name": "Too Small Package",
            "customerPrice": 299.0,
            "itemType": "package",
            "includedProducts": [{"clientProductId": "mock_client_product_order"}],
        },
    )
    assert invalid_package.status_code == 422

    package = client.post(
        "/admin/arora/products",
        json={
            "name": "Longevity Starter Package",
            "displayName": "Longevity Starter Package",
            "customerPrice": 349.0,
            "itemType": "package",
            "includedProducts": [
                {"clientProductId": "mock_client_product_order"},
                {"clientProductId": "mock_lab_foundation_panel"},
            ],
            "status": "active",
            "showPatient": False,
            "displayCategoryIds": ["longevity", "labs"],
            "description": "Internal mock package",
            "displayDescription": "Patient-facing package",
        },
    )
    assert package.status_code == 200
    assert package.json()["product"]["itemType"] == "package"
    assert len(package.json()["product"]["includedProducts"]) == 2
    assert package.json()["product"]["showPatient"] is False

    updated = client.patch(
        "/admin/arora/products/mock_product_longevity_consult",
        json={
            "displayName": "Longevity Program",
            "status": "inactive",
            "customerPrice": 299.0,
            "showPatient": False,
            "displayDescription": "Updated patient-facing copy",
        },
    )
    assert updated.status_code == 200
    assert updated.json()["product"]["displayName"] == "Longevity Program"
    assert updated.json()["product"]["status"] == "inactive"
    assert updated.json()["product"]["customerPrice"] == 299.0
    assert updated.json()["product"]["showPatient"] is False

    active_products = client.get("/admin/arora/products", params={"include_inactive": False})
    assert active_products.status_code == 200
    assert all(product["status"] == "active" for product in active_products.json()["products"])

    deleted = client.delete("/admin/arora/products/mock_product_longevity_consult")
    assert deleted.status_code == 200
    assert deleted.json()["deleted"] is True

    missing = client.patch("/admin/arora/products/mock_product_longevity_consult", json={"name": "Gone"})
    assert missing.status_code == 404


def test_admin_can_simulate_mock_arora_conversations(tmp_path) -> None:
    client = TestClient(create_app(tmp_path / "aeonic.sqlite3"))
    suffix = uuid4().hex[:8]
    patient_token, patient_id = _create_patient_session(client, suffix)

    created = client.post(
        "/admin/mock/arora/conversations",
        json={
            "patient_id": patient_id,
            "text": "Hello from the care team.",
            "author": "client",
            "sender_name": "Care Team",
        },
    )
    assert created.status_code == 200
    conversation = created.json()["conversation"]
    assert conversation["patientId"] == patient_id
    assert conversation["patientName"] == "Mira Chen"
    assert "subject" not in conversation
    assert conversation["messageCount"] == 1
    assert conversation["lastMessageText"] == "Hello from the care team."

    listed = client.get("/admin/mock/arora/conversations")
    assert listed.status_code == 200
    assert listed.json()["conversations"][0]["conversationId"] == conversation["conversationId"]

    messages = client.get(f"/admin/mock/arora/conversations/{conversation['conversationId']}/messages")
    assert messages.status_code == 200
    initial_message = messages.json()["messages"][0]
    assert initial_message["text"] == "Hello from the care team."
    assert initial_message["attachments"] == []

    reply = client.post(
        f"/admin/mock/arora/conversations/{conversation['conversationId']}/messages",
        json={
            "author": "patient",
            "sender_name": "Mira Chen",
            "text": "Thanks, I can do that.",
        },
    )
    assert reply.status_code == 200
    assert reply.json()["conversation"]["lastMessageText"] == "Thanks, I can do that."
    assert reply.json()["conversation"]["messageCount"] == 2
    reply_message_id = reply.json()["message"]["messageId"]

    updated_status = client.patch(
        f"/admin/mock/arora/conversations/{conversation['conversationId']}",
        json={"status": "closed"},
    )
    assert updated_status.status_code == 200
    assert updated_status.json()["conversation"]["status"] == "closed"

    escalation = client.post(
        f"/admin/mock/arora/conversations/{conversation['conversationId']}/escalations",
        json={"reason": "Provider review requested"},
    )
    assert escalation.status_code == 200
    assert escalation.json()["conversation"]["escalationReason"] == "Provider review requested"
    assert escalation.json()["conversation"]["escalatedAt"] is not None

    single_message = client.get(
        f"/admin/mock/arora/conversations/{conversation['conversationId']}/messages/{reply_message_id}"
    )
    assert single_message.status_code == 200
    assert single_message.json()["message"]["messageId"] == reply_message_id

    edited_message = client.patch(
        f"/admin/mock/arora/conversations/{conversation['conversationId']}/messages/{reply_message_id}",
        json={"text": "Thanks, I can do that today."},
    )
    assert edited_message.status_code == 200
    assert edited_message.json()["message"]["text"] == "Thanks, I can do that today."

    patient_conversations = client.get(
        "/patients/arora/conversations",
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert patient_conversations.status_code == 200
    patient_conversation = patient_conversations.json()["conversations"][0]
    assert patient_conversation["conversationId"] == conversation["conversationId"]
    assert patient_conversation["lastMessageText"] == "Thanks, I can do that today."
    assert patient_conversation["messageCount"] == 2

    patient_messages = client.get(
        f"/patients/arora/conversations/{conversation['conversationId']}/messages",
        headers={"Authorization": f"Bearer {patient_token}"},
    )
    assert patient_messages.status_code == 200
    assert patient_messages.json()["messages"][1]["author"] == "patient"

    patient_reply = client.post(
        f"/patients/arora/conversations/{conversation['conversationId']}/messages",
        headers={"Authorization": f"Bearer {patient_token}"},
        json={
            "text": "Patient-authored follow-up.",
            "attachments": [{"url": "https://example.com/lab.pdf", "name": "Lab PDF"}],
        },
    )
    assert patient_reply.status_code == 200
    assert patient_reply.json()["message"]["author"] == "patient"
    assert patient_reply.json()["message"]["attachments"][0]["name"] == "Lab PDF"

    deleted_message = client.delete(
        f"/admin/mock/arora/conversations/{conversation['conversationId']}/messages/{reply_message_id}"
    )
    assert deleted_message.status_code == 200
    assert deleted_message.json()["deleted"] is True
    assert deleted_message.json()["conversation"]["messageCount"] == 2

    archived = client.delete(f"/admin/mock/arora/conversations/{conversation['conversationId']}")
    assert archived.status_code == 200
    assert archived.json()["conversation"]["status"] == "archived"

    patient_created = client.post(
        "/patients/arora/conversations",
        headers={"Authorization": f"Bearer {patient_token}"},
        json={"text": "Can you confirm this order?"},
    )
    assert patient_created.status_code == 200
    assert "subject" not in patient_created.json()["conversation"]

    unsupported_subject = client.post(
        "/patients/arora/conversations",
        headers={"Authorization": f"Bearer {patient_token}"},
        json={"subject": "Billing question", "text": "Can you confirm this order?"},
    )
    assert unsupported_subject.status_code == 422

    admin_unsupported_subject = client.post(
        "/admin/mock/arora/conversations",
        json={
            "patient_id": patient_id,
            "subject": "Care follow-up",
            "text": "Hello from the care team.",
        },
    )
    assert admin_unsupported_subject.status_code == 422


def test_live_arora_conversation_create_uses_documented_payload(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("ARORA_API_MODE", "live")
    monkeypatch.setenv("ARORA_API_KEY", "test-arora-key")
    client = TestClient(create_app(tmp_path / "aeonic.sqlite3"))
    suffix = uuid4().hex[:8]
    patient_token, patient_id = _create_patient_session(client, suffix)
    calls = []

    def fake_arora_api_request(self, method, path, payload=None, query=None):
        calls.append({"method": method, "path": path, "payload": payload, "query": query})
        if method == "POST" and path == "/v2/client/conversations":
            return {"conversation": {"conversationId": "conv_123", "patientId": patient_id, "status": "active"}}
        if method == "POST" and path == "/v2/client/conversations/conv_123/messages":
            return {"message": {"messageId": "msg_123", "conversationId": "conv_123", "text": payload["text"]}}
        if method == "GET" and path == "/v2/client/conversations/conv_123":
            return {"conversation": {"conversationId": "conv_123", "patientId": patient_id, "status": "active"}}
        raise AssertionError(f"Unexpected Arora call {method} {path}")

    monkeypatch.setattr(LiveAroraClient, "_request", fake_arora_api_request)

    response = client.post(
        "/patients/arora/conversations",
        headers={"Authorization": f"Bearer {patient_token}"},
        json={"text": "Can you confirm this order?"},
    )

    assert response.status_code == 200
    assert calls[0] == {
        "method": "POST",
        "path": "/v2/client/conversations",
        "payload": {"patientId": patient_id},
        "query": None,
    }
    assert "subject" not in calls[0]["payload"]
    assert calls[1]["payload"] == {
        "author": "patient",
        "patientId": patient_id,
        "text": "Can you confirm this order?",
    }


def test_partner_domain_verification_includes_dns_record(tmp_path) -> None:
    client = TestClient(create_app(tmp_path / "aeonic.sqlite3"))
    suffix = uuid4().hex[:8]

    partner_signup = client.post(
        "/partners/signup",
        json={
            "owner_name": "Dr. Domain Owner",
            "email": f"domain-{suffix}@example.com",
            "password": "secret123",
            "clinic_name": "Domain Clinic",
        },
    )
    assert partner_signup.status_code == 200
    partner_token = partner_signup.json()["token"]

    empty_verification = client.post(
        "/partners/domain/verify",
        headers={"Authorization": f"Bearer {partner_token}"},
    )
    assert empty_verification.status_code == 200
    assert empty_verification.json()["verification"]["status"] == "not_configured"

    settings = client.patch(
        "/partners/settings",
        headers={"Authorization": f"Bearer {partner_token}"},
        json={"clinic_domain": f"app-{suffix}.localhost"},
    )
    assert settings.status_code == 200

    verification = client.post(
        "/partners/domain/verify",
        headers={"Authorization": f"Bearer {partner_token}"},
    )

    assert verification.status_code == 200
    body = verification.json()["verification"]
    assert body["domain"] == f"app-{suffix}.localhost"
    assert body["recordType"] == "CNAME"
    assert body["recordName"] == f"app-{suffix}.localhost"
    assert body["recordValue"] == "nexus.aeonichealthsystems.com"
    assert body["status"] == "connected"


def test_partner_domain_setup_uses_configured_dns_target(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("NEXUS_DNS_TARGET", "nexus-local.example.test")
    client = TestClient(create_app(tmp_path / "aeonic.sqlite3"))
    suffix = uuid4().hex[:8]

    partner_signup = client.post(
        "/partners/signup",
        json={
            "owner_name": "Dr. Configured Target",
            "email": f"configured-target-{suffix}@example.com",
            "password": "secret123",
            "clinic_name": "Configured Target Clinic",
        },
    )
    assert partner_signup.status_code == 200

    setup = client.get(
        "/partners/domain/setup",
        headers={"Authorization": f"Bearer {partner_signup.json()['token']}"},
    )

    assert setup.status_code == 200
    assert setup.json()["dns"] == {
        "recordType": "CNAME",
        "recordValue": "nexus-local.example.test",
    }


def test_partner_domain_verification_accepts_matching_cname(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("NEXUS_DNS_TARGET", "nexus-local.example.test")
    monkeypatch.setattr(
        main,
        "_resolve_cname_chain",
        lambda host: ["nexus-local.example.test"] if host == "app.example.test" else [],
    )
    client = TestClient(create_app(tmp_path / "aeonic.sqlite3"))
    suffix = uuid4().hex[:8]

    partner_signup = client.post(
        "/partners/signup",
        json={
            "owner_name": "Dr. CNAME",
            "email": f"cname-{suffix}@example.com",
            "password": "secret123",
            "clinic_name": "CNAME Clinic",
        },
    )
    assert partner_signup.status_code == 200
    partner_token = partner_signup.json()["token"]

    settings = client.patch(
        "/partners/settings",
        headers={"Authorization": f"Bearer {partner_token}"},
        json={"clinic_domain": "app.example.test"},
    )
    assert settings.status_code == 200

    verification = client.post(
        "/partners/domain/verify",
        headers={"Authorization": f"Bearer {partner_token}"},
    )

    assert verification.status_code == 200
    body = verification.json()["verification"]
    assert body["status"] == "connected"
    assert body["message"] == "DNS CNAME points to the Nexus target."


def test_local_partner_domain_skips_cloudflare_custom_hostname(tmp_path) -> None:
    client = TestClient(create_app(tmp_path / "aeonic.sqlite3"))
    suffix = uuid4().hex[:8]

    partner_signup = client.post(
        "/partners/signup",
        json={
            "owner_name": "Dr. Local Domain",
            "email": f"local-domain-{suffix}@example.com",
            "password": "secret123",
            "clinic_name": "Local Domain Clinic",
        },
    )
    assert partner_signup.status_code == 200
    partner_token = partner_signup.json()["token"]

    settings = client.patch(
        "/partners/settings",
        headers={"Authorization": f"Bearer {partner_token}"},
        json={"clinic_domain": f"app-{suffix}.localhost"},
    )
    assert settings.status_code == 200

    cloudflare = client.post(
        "/partners/domain/cloudflare-custom-hostname",
        headers={"Authorization": f"Bearer {partner_token}"},
    )

    assert cloudflare.status_code == 200
    body = cloudflare.json()
    assert body["verification"]["status"] == "connected"
    assert body["cloudflare"]["status"] == "skipped"


def test_partner_can_create_cloudflare_custom_hostname(monkeypatch, tmp_path) -> None:
    client = TestClient(create_app(tmp_path / "aeonic.sqlite3"))
    suffix = uuid4().hex[:8]
    clinic_domain = f"app-{suffix}.example.com"
    calls = []

    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test-token")
    monkeypatch.setenv("CLOUDFLARE_ZONE_ID", "test-zone")
    monkeypatch.setattr(main, "_resolve_ipv4", lambda host: {"203.0.113.42"})

    def fake_cloudflare_api_request(method, path, payload=None, query=None):
        calls.append({"method": method, "path": path, "payload": payload, "query": query})
        if method == "GET" and query:
            return {"success": True, "result": []}
        if method == "PATCH":
            return {
                "success": True,
                "result": {
                    "id": "023e105f4ecef8ad9ca31a8372d0c353",
                    "hostname": clinic_domain,
                    "status": "active",
                    "ssl": {
                        "method": payload["ssl"]["method"],
                        "type": payload["ssl"]["type"],
                        "status": "active",
                    },
                },
            }
        return {
            "success": True,
            "result": {
                "id": "023e105f4ecef8ad9ca31a8372d0c353",
                "hostname": clinic_domain,
                "status": "pending",
                "ssl": {
                    "method": "http",
                    "status": "pending_validation",
                    "validation_records": [
                        {
                            "http_url": f"http://{clinic_domain}/.well-known/cf-custom-hostname-challenge/test",
                            "http_body": "token",
                        }
                    ],
                },
            },
        }

    monkeypatch.setattr(main, "_cloudflare_api_request", fake_cloudflare_api_request)

    partner_signup = client.post(
        "/partners/signup",
        json={
            "owner_name": "Dr. Cloudflare Domain",
            "email": f"cloudflare-domain-{suffix}@example.com",
            "password": "secret123",
            "clinic_name": "Cloudflare Domain Clinic",
        },
    )
    assert partner_signup.status_code == 200
    partner_token = partner_signup.json()["token"]

    settings = client.patch(
        "/partners/settings",
        headers={"Authorization": f"Bearer {partner_token}"},
        json={"clinic_domain": clinic_domain},
    )
    assert settings.status_code == 200

    cloudflare = client.post(
        "/partners/domain/cloudflare-custom-hostname",
        headers={"Authorization": f"Bearer {partner_token}"},
    )

    assert cloudflare.status_code == 200
    body = cloudflare.json()
    assert body["verification"]["status"] == "connected"
    assert body["cloudflare"]["id"] == "023e105f4ecef8ad9ca31a8372d0c353"
    assert body["cloudflare"]["status"] == "pending"
    assert calls[1]["method"] == "POST"
    assert calls[1]["path"] == "/zones/test-zone/custom_hostnames"
    assert calls[1]["payload"]["hostname"] == clinic_domain
    assert "custom_metadata" not in calls[1]["payload"]
    assert calls[1]["payload"]["ssl"]["method"] == "http"
    assert calls[1]["payload"]["ssl"]["type"] == "dv"
    assert calls[1]["payload"]["custom_origin_server"] == "nexus.aeonichealthsystems.com"
    assert "custom_origin_sni" not in calls[1]["payload"]

    stored = client.get(
        "/partners/domain/cloudflare-custom-hostname",
        headers={"Authorization": f"Bearer {partner_token}"},
    )
    assert stored.status_code == 200
    assert stored.json()["cloudflare"]["id"] == "023e105f4ecef8ad9ca31a8372d0c353"
    assert stored.json()["cloudflare"]["sslStatus"] == "pending_validation"
    assert stored.json()["cloudflare"]["validationRecords"] == [
        {
            "http_url": f"http://{clinic_domain}/.well-known/cf-custom-hostname-challenge/test",
            "http_body": "token",
        }
    ]

    refreshed = client.post(
        "/partners/domain/cloudflare-custom-hostname",
        headers={"Authorization": f"Bearer {partner_token}"},
    )
    assert refreshed.status_code == 200
    assert refreshed.json()["cloudflare"]["status"] == "active"
    assert calls[-1]["method"] == "PATCH"
    assert calls[-1]["path"] == "/zones/test-zone/custom_hostnames/023e105f4ecef8ad9ca31a8372d0c353"
    assert calls[-1]["payload"] == {
        "ssl": {"method": "http", "type": "dv"},
        "custom_origin_server": "nexus.aeonichealthsystems.com",
    }


def test_partner_recreates_stale_cloudflare_custom_hostname(monkeypatch, tmp_path) -> None:
    client = TestClient(create_app(tmp_path / "aeonic.sqlite3"))
    suffix = uuid4().hex[:8]
    clinic_domain = f"stale-{suffix}.example.com"
    calls = []

    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test-token")
    monkeypatch.setenv("CLOUDFLARE_ZONE_ID", "test-zone")
    monkeypatch.setattr(main, "_resolve_ipv4", lambda host: {"203.0.113.42"})

    def result(custom_hostname_id: str) -> dict:
        return {
            "success": True,
            "result": {
                "id": custom_hostname_id,
                "hostname": clinic_domain,
                "status": "pending",
                "ssl": {
                    "method": "http",
                    "status": "pending_validation",
                },
            },
        }

    def fake_cloudflare_api_request(method, path, payload=None, query=None):
        calls.append({"method": method, "path": path, "payload": payload, "query": query})
        if method == "GET" and query:
            return {"success": True, "result": []}
        if method == "GET" and path.endswith("/stale-id"):
            raise main.HTTPException(status_code=502, detail="The custom hostname was not found.")
        if method == "POST":
            post_count = len([call for call in calls if call["method"] == "POST"])
            return result("stale-id" if post_count == 1 else "fresh-id")
        return result("fresh-id")

    monkeypatch.setattr(main, "_cloudflare_api_request", fake_cloudflare_api_request)

    partner_signup = client.post(
        "/partners/signup",
        json={
            "owner_name": "Dr. Stale Hostname",
            "email": f"stale-hostname-{suffix}@example.com",
            "password": "secret123",
            "clinic_name": "Stale Hostname Clinic",
        },
    )
    assert partner_signup.status_code == 200
    partner_token = partner_signup.json()["token"]

    settings = client.patch(
        "/partners/settings",
        headers={"Authorization": f"Bearer {partner_token}"},
        json={"clinic_domain": clinic_domain},
    )
    assert settings.status_code == 200

    created = client.post(
        "/partners/domain/cloudflare-custom-hostname",
        headers={"Authorization": f"Bearer {partner_token}"},
    )
    assert created.status_code == 200
    assert created.json()["cloudflare"]["id"] == "stale-id"

    recreated = client.post(
        "/partners/domain/cloudflare-custom-hostname",
        headers={"Authorization": f"Bearer {partner_token}"},
    )

    assert recreated.status_code == 200
    assert recreated.json()["cloudflare"]["id"] == "fresh-id"
    assert [call["method"] for call in calls] == ["GET", "POST", "GET", "GET", "POST"]


def test_partner_cloudflare_validation_errors_are_visible(monkeypatch, tmp_path) -> None:
    client = TestClient(create_app(tmp_path / "aeonic.sqlite3"))
    suffix = uuid4().hex[:8]
    clinic_domain = f"validation-{suffix}.example.com"
    diagnostics = [
        "Certificate authority was unable to verify domain ownership from multiple geographic locations (MPIC failure). Please ensure your DNS records are reachable from all geographic perspectives and try again.",
        "zone does not have a fallback origin set.",
    ]

    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test-token")
    monkeypatch.setenv("CLOUDFLARE_ZONE_ID", "test-zone")
    monkeypatch.setattr(main, "_resolve_ipv4", lambda host: {"203.0.113.42"})

    def fake_cloudflare_api_request(method, path, payload=None, query=None):
        if method == "GET" and query:
            return {"success": True, "result": []}
        return {
            "success": True,
            "result": {
                "id": "validation-errors-id",
                "hostname": clinic_domain,
                "status": "pending",
                "verification_errors": diagnostics,
                "ssl": {
                    "method": "http",
                    "status": "pending_validation",
                },
            },
        }

    monkeypatch.setattr(main, "_cloudflare_api_request", fake_cloudflare_api_request)

    partner_signup = client.post(
        "/partners/signup",
        json={
            "owner_name": "Dr. Validation",
            "email": f"validation-{suffix}@example.com",
            "password": "secret123",
            "clinic_name": "Validation Clinic",
        },
    )
    assert partner_signup.status_code == 200
    partner_token = partner_signup.json()["token"]

    settings = client.patch(
        "/partners/settings",
        headers={"Authorization": f"Bearer {partner_token}"},
        json={"clinic_domain": clinic_domain},
    )
    assert settings.status_code == 200

    cloudflare = client.post(
        "/partners/domain/cloudflare-custom-hostname",
        headers={"Authorization": f"Bearer {partner_token}"},
    )

    assert cloudflare.status_code == 200
    body = cloudflare.json()["cloudflare"]
    assert body["status"] == "needs_attention"
    assert body["message"] == diagnostics[0]
    assert body["diagnostics"] == diagnostics


def test_transient_cloudflare_ca_error_stays_pending(monkeypatch, tmp_path) -> None:
    client = TestClient(create_app(tmp_path / "aeonic.sqlite3"))
    suffix = uuid4().hex[:8]
    clinic_domain = f"ca-retry-{suffix}.example.com"
    diagnostic = "Internal error with Certificate Authority. Please check later."

    monkeypatch.setenv("CLOUDFLARE_API_TOKEN", "test-token")
    monkeypatch.setenv("CLOUDFLARE_ZONE_ID", "test-zone")
    monkeypatch.setattr(main, "_resolve_ipv4", lambda host: {"203.0.113.42"})

    def fake_cloudflare_api_request(method, path, payload=None, query=None):
        if method == "GET" and query:
            return {"success": True, "result": []}
        return {
            "success": True,
            "result": {
                "id": "ca-retry-id",
                "hostname": clinic_domain,
                "status": "active",
                "ssl": {
                    "method": "txt",
                    "status": "pending_validation",
                    "validation_errors": [diagnostic],
                    "validation_records": [
                        {
                            "status": "pending",
                            "txt_name": f"_acme-challenge.{clinic_domain}",
                            "txt_value": "token",
                        }
                    ],
                },
            },
        }

    monkeypatch.setattr(main, "_cloudflare_api_request", fake_cloudflare_api_request)

    partner_signup = client.post(
        "/partners/signup",
        json={
            "owner_name": "Dr. CA Retry",
            "email": f"ca-retry-{suffix}@example.com",
            "password": "secret123",
            "clinic_name": "CA Retry Clinic",
        },
    )
    assert partner_signup.status_code == 200
    partner_token = partner_signup.json()["token"]

    settings = client.patch(
        "/partners/settings",
        headers={"Authorization": f"Bearer {partner_token}"},
        json={"clinic_domain": clinic_domain},
    )
    assert settings.status_code == 200

    cloudflare = client.post(
        "/partners/domain/cloudflare-custom-hostname",
        headers={"Authorization": f"Bearer {partner_token}"},
    )

    assert cloudflare.status_code == 200
    body = cloudflare.json()["cloudflare"]
    assert body["status"] == "pending"
    assert body["message"] == "Cloudflare accepted the hostname and is provisioning SSL."
    assert body["diagnostics"] == [diagnostic]


def test_partner_account_persists_across_app_instances(tmp_path) -> None:
    database_path = tmp_path / "aeonic.sqlite3"
    suffix = uuid4().hex[:8]
    email = f"owner-{suffix}@example.com"

    first_client = TestClient(create_app(database_path))
    signup = first_client.post(
        "/partners/signup",
        json={
            "owner_name": "Jordan Vale",
            "email": email,
            "password": "secret123",
            "clinic_name": "Vale Longevity",
        },
    )
    assert signup.status_code == 200

    second_client = TestClient(create_app(database_path))
    login = second_client.post(
        "/partners/login",
        json={"email": email, "password": "secret123"},
    )
    assert login.status_code == 200
    assert login.json()["partner"]["clinicName"] == "Vale Longevity"


def test_partner_email_must_be_unique(tmp_path) -> None:
    client = TestClient(create_app(tmp_path / "aeonic.sqlite3"))
    email = f"owner-{uuid4().hex[:8]}@example.com"
    payload = {
        "owner_name": "Riley Moss",
        "email": email,
        "password": "secret123",
        "clinic_name": "Moss Health",
    }

    first_signup = client.post("/partners/signup", json=payload)
    duplicate_signup = client.post("/partners/signup", json=payload)

    assert first_signup.status_code == 200
    assert duplicate_signup.status_code == 409


def test_patient_email_is_scoped_to_partner_domain(tmp_path) -> None:
    client = TestClient(create_app(tmp_path / "aeonic.sqlite3"))
    suffix = uuid4().hex[:8]
    shared_patient_email = f"patient-{suffix}@example.com"

    partner_domains = []
    for clinic_name in ["North Clinic", "South Clinic"]:
        partner_signup = client.post(
            "/partners/signup",
            json={
                "owner_name": f"{clinic_name} Owner",
                "email": f"{clinic_name.lower().replace(' ', '-')}-{suffix}@example.com",
                "password": "secret123",
                "clinic_name": clinic_name,
            },
        )
        assert partner_signup.status_code == 200
        partner_token = partner_signup.json()["token"]
        clinic_domain = f"{clinic_name.lower().replace(' ', '-')}-{suffix}.example.com"
        settings = client.patch(
            "/partners/settings",
            headers={"Authorization": f"Bearer {partner_token}"},
            json={"clinic_domain": clinic_domain},
        )
        assert settings.status_code == 200
        partner_domains.append(clinic_domain)

    first_patient = client.post(
        "/patients/signup",
        json={
            "host": partner_domains[0],
            "name": "Same Email",
            "email": shared_patient_email,
            "password": "secret123",
        },
    )
    second_patient = client.post(
        "/patients/signup",
        json={
            "host": partner_domains[1],
            "name": "Same Email",
            "email": shared_patient_email,
            "password": "secret123",
        },
    )
    duplicate_patient = client.post(
        "/patients/signup",
        json={
            "host": partner_domains[0],
            "name": "Same Email",
            "email": shared_patient_email,
            "password": "secret123",
        },
    )

    assert first_patient.status_code == 200
    assert second_patient.status_code == 200
    assert duplicate_patient.status_code == 409


def test_partner_domains_must_be_unique(tmp_path) -> None:
    client = TestClient(create_app(tmp_path / "aeonic.sqlite3"))
    suffix = uuid4().hex[:8]
    shared_domain = f"shared-{suffix}.example.com"

    first_signup = client.post(
        "/partners/signup",
        json={
            "owner_name": "First Owner",
            "email": f"first-{suffix}@example.com",
            "password": "secret123",
            "clinic_name": "First Clinic",
        },
    )
    assert first_signup.status_code == 200
    first_settings = client.patch(
        "/partners/settings",
        headers={"Authorization": f"Bearer {first_signup.json()['token']}"},
        json={"clinic_domain": shared_domain},
    )
    assert first_settings.status_code == 200

    second_signup = client.post(
        "/partners/signup",
        json={
            "owner_name": "Second Owner",
            "email": f"second-{suffix}@example.com",
            "password": "secret123",
            "clinic_name": "Second Clinic",
        },
    )
    assert second_signup.status_code == 200
    second_settings = client.patch(
        "/partners/settings",
        headers={"Authorization": f"Bearer {second_signup.json()['token']}"},
        json={"clinic_domain": shared_domain},
    )

    assert second_settings.status_code == 409
