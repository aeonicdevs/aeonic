import os
import uuid
from typing import Literal

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


class PartnerSignup(BaseModel):
    owner_name: str = Field(min_length=1)
    email: str = Field(min_length=3)
    password: str = Field(min_length=6)
    clinic_name: str = Field(min_length=1)


class LoginRequest(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=1)


class PartnerSettingsUpdate(BaseModel):
    clinic_domain: str = Field(min_length=1)


class PatientSignup(BaseModel):
    host: str = Field(min_length=1)
    name: str = Field(min_length=1)
    email: str = Field(min_length=3)
    password: str = Field(min_length=6)


class PatientLogin(BaseModel):
    host: str = Field(min_length=1)
    email: str = Field(min_length=3)
    password: str = Field(min_length=1)


Partner = dict[str, str | None]
Patient = dict[str, str]

partners_by_id: dict[str, Partner] = {}
partner_ids_by_email: dict[str, str] = {}
partner_ids_by_domain: dict[str, str] = {}
patients_by_id: dict[str, Patient] = {}
patient_ids_by_partner_email: dict[tuple[str, str], str] = {}
tokens: dict[str, tuple[Literal["partner", "patient"], str]] = {}


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _normalize_host(host: str) -> str:
    value = host.strip().lower()
    if "://" in value:
        value = value.split("://", 1)[1]
    value = value.split("/", 1)[0]
    if ":" in value and not value.startswith("["):
        value = value.split(":", 1)[0]
    return value


def _public_partner(partner: Partner) -> dict[str, str | None]:
    return {
        "id": str(partner["id"]),
        "ownerName": str(partner["owner_name"]),
        "email": str(partner["email"]),
        "clinicName": str(partner["clinic_name"]),
        "clinicDomain": partner["clinic_domain"],
    }


def _public_patient(patient: Patient) -> dict[str, str]:
    return {
        "id": patient["id"],
        "partnerId": patient["partner_id"],
        "name": patient["name"],
        "email": patient["email"],
    }


def _issue_token(kind: Literal["partner", "patient"], entity_id: str) -> str:
    token = uuid.uuid4().hex
    tokens[token] = (kind, entity_id)
    return token


def _seed_demo_partner() -> None:
    if partners_by_id:
        return

    partner_id = "demo-partner"
    partner: Partner = {
        "id": partner_id,
        "owner_name": "Demo Partner",
        "email": "demo@aeonic.health",
        "password": "password",
        "clinic_name": "Demo Dental Studio",
        "clinic_domain": "demo.localhost",
    }
    partners_by_id[partner_id] = partner
    partner_ids_by_email["demo@aeonic.health"] = partner_id
    for domain in ["demo.localhost", "localhost", "127.0.0.1"]:
        partner_ids_by_domain[domain] = partner_id


def _allowed_origins() -> list[str]:
    raw_origins = os.getenv("ALLOWED_ORIGINS")
    if raw_origins is None and os.getenv("APP_ENV", "development") != "production":
        return [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
        ]

    raw_origins = raw_origins or ""
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


def _authenticated(
    expected_kind: Literal["partner", "patient"],
    authorization: str | None,
) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = authorization.split(" ", 1)[1].strip()
    session = tokens.get(token)
    if session is None or session[0] != expected_kind:
        raise HTTPException(status_code=401, detail="Invalid bearer token")

    return session[1]


def create_app() -> FastAPI:
    _seed_demo_partner()

    app = FastAPI(title="Aeonic API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_allowed_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/", tags=["system"])
    def root() -> dict[str, str]:
        return {"name": "Aeonic API", "status": "running"}

    @app.post("/partners/signup", tags=["partners"])
    def partner_signup(payload: PartnerSignup) -> dict[str, object]:
        email = _normalize_email(payload.email)
        if email in partner_ids_by_email:
            raise HTTPException(status_code=409, detail="Partner email already exists")

        partner_id = uuid.uuid4().hex
        partner: Partner = {
            "id": partner_id,
            "owner_name": payload.owner_name.strip(),
            "email": email,
            "password": payload.password,
            "clinic_name": payload.clinic_name.strip(),
            "clinic_domain": None,
        }
        partners_by_id[partner_id] = partner
        partner_ids_by_email[email] = partner_id

        return {"token": _issue_token("partner", partner_id), "partner": _public_partner(partner)}

    @app.post("/partners/login", tags=["partners"])
    def partner_login(payload: LoginRequest) -> dict[str, object]:
        email = _normalize_email(payload.email)
        partner_id = partner_ids_by_email.get(email)
        partner = partners_by_id.get(partner_id or "")
        if partner is None or partner["password"] != payload.password:
            raise HTTPException(status_code=401, detail="Invalid partner credentials")

        return {"token": _issue_token("partner", str(partner["id"])), "partner": _public_partner(partner)}

    @app.get("/partners/me", tags=["partners"])
    def partner_me(authorization: str | None = Header(default=None)) -> dict[str, object]:
        partner_id = _authenticated("partner", authorization)
        return {"partner": _public_partner(partners_by_id[partner_id])}

    @app.patch("/partners/settings", tags=["partners"])
    def partner_settings(
        payload: PartnerSettingsUpdate,
        authorization: str | None = Header(default=None),
    ) -> dict[str, object]:
        partner_id = _authenticated("partner", authorization)
        partner = partners_by_id[partner_id]
        previous_domain = partner["clinic_domain"]
        domain = _normalize_host(payload.clinic_domain)

        owner_id = partner_ids_by_domain.get(domain)
        if owner_id is not None and owner_id != partner_id:
            raise HTTPException(status_code=409, detail="Domain already belongs to another partner")

        if previous_domain:
            partner_ids_by_domain.pop(str(previous_domain), None)

        partner["clinic_domain"] = domain
        partner_ids_by_domain[domain] = partner_id

        return {"partner": _public_partner(partner)}

    @app.get("/nexus/context", tags=["nexus"])
    def nexus_context(host: str) -> dict[str, object]:
        domain = _normalize_host(host)
        partner_id = partner_ids_by_domain.get(domain)
        partner = partners_by_id.get(partner_id or "")

        return {
            "host": domain,
            "partner": _public_partner(partner) if partner is not None else None,
        }

    @app.post("/patients/signup", tags=["patients"])
    def patient_signup(payload: PatientSignup) -> dict[str, object]:
        domain = _normalize_host(payload.host)
        partner_id = partner_ids_by_domain.get(domain)
        if partner_id is None:
            raise HTTPException(status_code=404, detail="No partner is configured for this host")

        email = _normalize_email(payload.email)
        patient_key = (partner_id, email)
        if patient_key in patient_ids_by_partner_email:
            raise HTTPException(status_code=409, detail="Patient email already exists for this partner")

        patient_id = uuid.uuid4().hex
        patient: Patient = {
            "id": patient_id,
            "partner_id": partner_id,
            "name": payload.name.strip(),
            "email": email,
            "password": payload.password,
        }
        patients_by_id[patient_id] = patient
        patient_ids_by_partner_email[patient_key] = patient_id

        return {
            "token": _issue_token("patient", patient_id),
            "patient": _public_patient(patient),
            "partner": _public_partner(partners_by_id[partner_id]),
        }

    @app.post("/patients/login", tags=["patients"])
    def patient_login(payload: PatientLogin) -> dict[str, object]:
        domain = _normalize_host(payload.host)
        partner_id = partner_ids_by_domain.get(domain)
        if partner_id is None:
            raise HTTPException(status_code=404, detail="No partner is configured for this host")

        email = _normalize_email(payload.email)
        patient_id = patient_ids_by_partner_email.get((partner_id, email))
        patient = patients_by_id.get(patient_id or "")
        if patient is None or patient["password"] != payload.password:
            raise HTTPException(status_code=401, detail="Invalid patient credentials")

        return {
            "token": _issue_token("patient", patient_id),
            "patient": _public_patient(patient),
            "partner": _public_partner(partners_by_id[partner_id]),
        }

    @app.get("/patients/me", tags=["patients"])
    def patient_me(authorization: str | None = Header(default=None)) -> dict[str, object]:
        patient_id = _authenticated("patient", authorization)
        patient = patients_by_id[patient_id]

        return {
            "patient": _public_patient(patient),
            "partner": _public_partner(partners_by_id[patient["partner_id"]]),
        }

    return app


app = create_app()
