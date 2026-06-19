from fastapi.testclient import TestClient
from uuid import uuid4

import app.main as main
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

    stored = client.get(
        "/partners/domain/cloudflare-custom-hostname",
        headers={"Authorization": f"Bearer {partner_token}"},
    )
    assert stored.status_code == 200
    assert stored.json()["cloudflare"]["id"] == "023e105f4ecef8ad9ca31a8372d0c353"
    assert stored.json()["cloudflare"]["sslStatus"] == "pending_validation"


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
