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
