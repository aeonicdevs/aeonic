from fastapi.testclient import TestClient
from uuid import uuid4

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
