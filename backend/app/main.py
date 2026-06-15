import hashlib
import os
import secrets
import socket
import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


PASSWORD_ITERATIONS = 390_000
PrincipalKind = Literal["partner", "patient"]
DomainStatus = Literal["not_configured", "pending_dns", "connected", "needs_attention"]


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


def _default_database_path() -> Path:
    configured_path = os.getenv("AEONIC_DATABASE_PATH")
    if configured_path:
        return Path(configured_path)

    return Path(__file__).resolve().parents[1] / ".data" / "aeonic.sqlite3"


def _connect(database_path: str | Path) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _initialize_database(database_path: str | Path) -> None:
    if database_path != ":memory:":
        Path(database_path).parent.mkdir(parents=True, exist_ok=True)

    with _connect(database_path) as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS partners (
                id TEXT PRIMARY KEY,
                owner_name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                clinic_name TEXT NOT NULL,
                clinic_domain TEXT UNIQUE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS partner_domains (
                domain TEXT PRIMARY KEY,
                partner_id TEXT NOT NULL REFERENCES partners(id) ON DELETE CASCADE,
                is_primary INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS patients (
                id TEXT PRIMARY KEY,
                partner_id TEXT NOT NULL REFERENCES partners(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (partner_id, email)
            );

            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                principal_type TEXT NOT NULL CHECK (principal_type IN ('partner', 'patient')),
                principal_id TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            """
        )


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


def _required(value: str, label: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise HTTPException(status_code=422, detail=f"{label} is required")
    return cleaned


def _public_partner(partner: sqlite3.Row) -> dict[str, str | None]:
    return {
        "id": partner["id"],
        "ownerName": partner["owner_name"],
        "email": partner["email"],
        "clinicName": partner["clinic_name"],
        "clinicDomain": partner["clinic_domain"],
    }


def _public_patient(patient: sqlite3.Row) -> dict[str, str]:
    return {
        "id": patient["id"],
        "partnerId": patient["partner_id"],
        "name": patient["name"],
        "email": patient["email"],
    }


def _nexus_dns_target() -> str:
    return _normalize_host(os.getenv("NEXUS_DNS_TARGET", "nexus.aeonichealthsystems.com"))


def _resolve_ipv4(host: str) -> set[str]:
    addresses = socket.getaddrinfo(host, None, family=socket.AF_INET, type=socket.SOCK_STREAM)
    return {address[4][0] for address in addresses}


def _is_local_development_host(host: str) -> bool:
    return host == "localhost" or host == "127.0.0.1" or host.endswith(".localhost")


def _domain_verification_payload(
    domain: str | None,
    status: DomainStatus,
    message: str,
) -> dict[str, str | None]:
    return {
        "domain": domain,
        "recordType": "CNAME",
        "recordName": domain,
        "recordValue": _nexus_dns_target(),
        "status": status,
        "message": message,
        "checkedAt": datetime.now(UTC).isoformat(),
    }


def _verify_domain(domain: str | None) -> dict[str, str | None]:
    if not domain:
        return _domain_verification_payload(
            None,
            "not_configured",
            "Add a patient-facing domain before checking DNS.",
        )

    if _is_local_development_host(domain):
        return _domain_verification_payload(
            domain,
            "connected",
            "Local development domains are ready for preview.",
        )

    target = _nexus_dns_target()
    try:
        domain_addresses = _resolve_ipv4(domain)
    except socket.gaierror:
        return _domain_verification_payload(
            domain,
            "pending_dns",
            "No DNS record was found for this host yet.",
        )

    try:
        target_addresses = _resolve_ipv4(target)
    except socket.gaierror:
        return _domain_verification_payload(
            domain,
            "needs_attention",
            f"The Nexus target {target} is not resolving.",
        )

    if domain_addresses & target_addresses:
        return _domain_verification_payload(
            domain,
            "connected",
            "DNS resolves to the Nexus target.",
        )

    return _domain_verification_payload(
        domain,
        "needs_attention",
        f"DNS is resolving, but not to {target}.",
    )


def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PASSWORD_ITERATIONS,
    ).hex()
    return f"pbkdf2_sha256${PASSWORD_ITERATIONS}${salt}${digest}"


def _verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt, expected_digest = stored_hash.split("$", 3)
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        int(iterations),
    ).hex()
    return secrets.compare_digest(digest, expected_digest)


def _get_partner_by_id(db: sqlite3.Connection, partner_id: str) -> sqlite3.Row | None:
    return db.execute("SELECT * FROM partners WHERE id = ?", (partner_id,)).fetchone()


def _get_partner_by_email(db: sqlite3.Connection, email: str) -> sqlite3.Row | None:
    return db.execute("SELECT * FROM partners WHERE email = ?", (email,)).fetchone()


def _get_partner_by_domain(db: sqlite3.Connection, domain: str) -> sqlite3.Row | None:
    return db.execute(
        """
        SELECT partners.*
        FROM partners
        JOIN partner_domains ON partner_domains.partner_id = partners.id
        WHERE partner_domains.domain = ?
        """,
        (domain,),
    ).fetchone()


def _is_development() -> bool:
    return os.getenv("APP_ENV", "development") != "production"


def _issue_token(db: sqlite3.Connection, kind: PrincipalKind, entity_id: str) -> str:
    token = secrets.token_urlsafe(32)
    db.execute(
        "INSERT INTO sessions (token, principal_type, principal_id) VALUES (?, ?, ?)",
        (token, kind, entity_id),
    )
    return token


def _authenticated(
    db: sqlite3.Connection,
    expected_kind: PrincipalKind,
    authorization: str | None,
) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = authorization.split(" ", 1)[1].strip()
    session = db.execute(
        "SELECT principal_type, principal_id FROM sessions WHERE token = ?",
        (token,),
    ).fetchone()
    if session is None or session["principal_type"] != expected_kind:
        raise HTTPException(status_code=401, detail="Invalid bearer token")

    return session["principal_id"]


def _seed_demo_partner(database_path: str | Path) -> None:
    with _connect(database_path) as db:
        existing_partner = _get_partner_by_email(db, "demo@aeonic.health")
        if existing_partner is not None:
            return

        partner_id = "demo-partner"
        db.execute(
            """
            INSERT INTO partners (
                id, owner_name, email, password_hash, clinic_name, clinic_domain
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                partner_id,
                "Demo Partner",
                "demo@aeonic.health",
                _hash_password("password"),
                "Demo Dental Studio",
                "app.demo.localhost",
            ),
        )
        db.executemany(
            """
            INSERT OR IGNORE INTO partner_domains (domain, partner_id, is_primary)
            VALUES (?, ?, ?)
            """,
            [
                ("app.demo.localhost", partner_id, 1),
                ("demo.localhost", partner_id, 0),
                ("localhost", partner_id, 0),
                ("127.0.0.1", partner_id, 0),
            ],
        )


def _allowed_origins() -> list[str]:
    raw_origins = os.getenv("ALLOWED_ORIGINS")
    if raw_origins is None and _is_development():
        return []

    raw_origins = raw_origins or ""
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


def _allowed_origin_regex() -> str | None:
    if os.getenv("ALLOWED_ORIGINS") is not None:
        return None
    if not _is_development():
        return None

    return r"^http://(localhost|127\.0\.0\.1):[0-9]+$"


def create_app(database_path: str | Path | None = None) -> FastAPI:
    resolved_database_path = database_path or _default_database_path()
    _initialize_database(resolved_database_path)
    _seed_demo_partner(resolved_database_path)

    app = FastAPI(title="Aeonic API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_allowed_origins(),
        allow_origin_regex=_allowed_origin_regex(),
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
        owner_name = _required(payload.owner_name, "Owner name")
        clinic_name = _required(payload.clinic_name, "Clinic name")
        email = _normalize_email(payload.email)

        with _connect(resolved_database_path) as db:
            if _get_partner_by_email(db, email) is not None:
                raise HTTPException(status_code=409, detail="Partner email already exists")

            partner_id = uuid.uuid4().hex
            db.execute(
                """
                INSERT INTO partners (
                    id, owner_name, email, password_hash, clinic_name, clinic_domain
                )
                VALUES (?, ?, ?, ?, ?, NULL)
                """,
                (partner_id, owner_name, email, _hash_password(payload.password), clinic_name),
            )
            partner = _get_partner_by_id(db, partner_id)
            if partner is None:
                raise HTTPException(status_code=500, detail="Unable to create partner")

            return {"token": _issue_token(db, "partner", partner_id), "partner": _public_partner(partner)}

    @app.post("/partners/login", tags=["partners"])
    def partner_login(payload: LoginRequest) -> dict[str, object]:
        email = _normalize_email(payload.email)

        with _connect(resolved_database_path) as db:
            partner = _get_partner_by_email(db, email)
            if partner is None or not _verify_password(payload.password, partner["password_hash"]):
                raise HTTPException(status_code=401, detail="Invalid partner credentials")

            return {"token": _issue_token(db, "partner", partner["id"]), "partner": _public_partner(partner)}

    @app.get("/partners/me", tags=["partners"])
    def partner_me(authorization: str | None = Header(default=None)) -> dict[str, object]:
        with _connect(resolved_database_path) as db:
            partner_id = _authenticated(db, "partner", authorization)
            partner = _get_partner_by_id(db, partner_id)
            if partner is None:
                raise HTTPException(status_code=401, detail="Invalid bearer token")

            return {"partner": _public_partner(partner)}

    @app.patch("/partners/settings", tags=["partners"])
    def partner_settings(
        payload: PartnerSettingsUpdate,
        authorization: str | None = Header(default=None),
    ) -> dict[str, object]:
        domain = _normalize_host(payload.clinic_domain)
        if not domain:
            raise HTTPException(status_code=422, detail="Clinic patient domain is required")

        with _connect(resolved_database_path) as db:
            partner_id = _authenticated(db, "partner", authorization)
            partner = _get_partner_by_id(db, partner_id)
            if partner is None:
                raise HTTPException(status_code=401, detail="Invalid bearer token")

            owner = db.execute(
                "SELECT partner_id FROM partner_domains WHERE domain = ?",
                (domain,),
            ).fetchone()
            if owner is not None and owner["partner_id"] != partner_id:
                raise HTTPException(status_code=409, detail="Domain already belongs to another partner")

            previous_domain = partner["clinic_domain"]
            if previous_domain:
                db.execute(
                    "DELETE FROM partner_domains WHERE domain = ? AND partner_id = ? AND is_primary = 1",
                    (previous_domain, partner_id),
                )

            db.execute(
                "UPDATE partners SET clinic_domain = ? WHERE id = ?",
                (domain, partner_id),
            )
            db.execute(
                """
                INSERT INTO partner_domains (domain, partner_id, is_primary)
                VALUES (?, ?, 1)
                ON CONFLICT(domain) DO UPDATE SET partner_id = excluded.partner_id, is_primary = 1
                """,
                (domain, partner_id),
            )
            updated_partner = _get_partner_by_id(db, partner_id)
            if updated_partner is None:
                raise HTTPException(status_code=500, detail="Unable to save partner settings")

            return {"partner": _public_partner(updated_partner)}

    @app.post("/partners/domain/verify", tags=["partners"])
    def partner_domain_verify(authorization: str | None = Header(default=None)) -> dict[str, object]:
        with _connect(resolved_database_path) as db:
            partner_id = _authenticated(db, "partner", authorization)
            partner = _get_partner_by_id(db, partner_id)
            if partner is None:
                raise HTTPException(status_code=401, detail="Invalid bearer token")

            return {"verification": _verify_domain(partner["clinic_domain"])}

    @app.get("/nexus/context", tags=["nexus"])
    def nexus_context(host: str) -> dict[str, object]:
        domain = _normalize_host(host)

        with _connect(resolved_database_path) as db:
            partner = _get_partner_by_domain(db, domain)
            return {
                "host": domain,
                "partner": _public_partner(partner) if partner is not None else None,
            }

    @app.post("/patients/signup", tags=["patients"])
    def patient_signup(payload: PatientSignup) -> dict[str, object]:
        domain = _normalize_host(payload.host)
        name = _required(payload.name, "Full name")
        email = _normalize_email(payload.email)

        with _connect(resolved_database_path) as db:
            partner = _get_partner_by_domain(db, domain)
            if partner is None:
                raise HTTPException(status_code=404, detail="No partner is configured for this host")

            existing_patient = db.execute(
                "SELECT id FROM patients WHERE partner_id = ? AND email = ?",
                (partner["id"], email),
            ).fetchone()
            if existing_patient is not None:
                raise HTTPException(status_code=409, detail="Patient email already exists for this partner")

            patient_id = uuid.uuid4().hex
            db.execute(
                """
                INSERT INTO patients (id, partner_id, name, email, password_hash)
                VALUES (?, ?, ?, ?, ?)
                """,
                (patient_id, partner["id"], name, email, _hash_password(payload.password)),
            )
            patient = db.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
            if patient is None:
                raise HTTPException(status_code=500, detail="Unable to create patient")

            return {
                "token": _issue_token(db, "patient", patient_id),
                "patient": _public_patient(patient),
                "partner": _public_partner(partner),
            }

    @app.post("/patients/login", tags=["patients"])
    def patient_login(payload: PatientLogin) -> dict[str, object]:
        domain = _normalize_host(payload.host)
        email = _normalize_email(payload.email)

        with _connect(resolved_database_path) as db:
            partner = _get_partner_by_domain(db, domain)
            if partner is None:
                raise HTTPException(status_code=404, detail="No partner is configured for this host")

            patient = db.execute(
                "SELECT * FROM patients WHERE partner_id = ? AND email = ?",
                (partner["id"], email),
            ).fetchone()
            if patient is None or not _verify_password(payload.password, patient["password_hash"]):
                raise HTTPException(status_code=401, detail="Invalid patient credentials")

            return {
                "token": _issue_token(db, "patient", patient["id"]),
                "patient": _public_patient(patient),
                "partner": _public_partner(partner),
            }

    @app.get("/patients/me", tags=["patients"])
    def patient_me(authorization: str | None = Header(default=None)) -> dict[str, object]:
        with _connect(resolved_database_path) as db:
            patient_id = _authenticated(db, "patient", authorization)
            patient = db.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
            if patient is None:
                raise HTTPException(status_code=401, detail="Invalid bearer token")

            partner = _get_partner_by_id(db, patient["partner_id"])
            if partner is None:
                raise HTTPException(status_code=401, detail="Invalid bearer token")

            return {
                "patient": _public_patient(patient),
                "partner": _public_partner(partner),
            }

    return app


app = create_app()
