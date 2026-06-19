import hashlib
import json
import os
import re
import secrets
import socket
import sqlite3
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, Header, HTTPException, Request, Response
from pydantic import BaseModel, Field


PASSWORD_ITERATIONS = 390_000
PrincipalKind = Literal["partner", "patient"]
DomainStatus = Literal["not_configured", "pending_dns", "connected", "needs_attention"]
CloudflareProvisioningStatus = Literal[
    "not_configured",
    "dns_not_ready",
    "not_available",
    "skipped",
    "pending",
    "active",
    "needs_attention",
]


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
                cloudflare_custom_hostname_id TEXT,
                cloudflare_hostname_status TEXT,
                cloudflare_ssl_status TEXT,
                cloudflare_ssl_validation_method TEXT,
                cloudflare_error TEXT,
                cloudflare_synced_at TEXT,
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
        _ensure_partner_domain_cloudflare_columns(db)


def _ensure_partner_domain_cloudflare_columns(db: sqlite3.Connection) -> None:
    columns = {row["name"] for row in db.execute("PRAGMA table_info(partner_domains)").fetchall()}
    migrations = {
        "cloudflare_custom_hostname_id": "ALTER TABLE partner_domains ADD COLUMN cloudflare_custom_hostname_id TEXT",
        "cloudflare_hostname_status": "ALTER TABLE partner_domains ADD COLUMN cloudflare_hostname_status TEXT",
        "cloudflare_ssl_status": "ALTER TABLE partner_domains ADD COLUMN cloudflare_ssl_status TEXT",
        "cloudflare_ssl_validation_method": (
            "ALTER TABLE partner_domains ADD COLUMN cloudflare_ssl_validation_method TEXT"
        ),
        "cloudflare_error": "ALTER TABLE partner_domains ADD COLUMN cloudflare_error TEXT",
        "cloudflare_synced_at": "ALTER TABLE partner_domains ADD COLUMN cloudflare_synced_at TEXT",
    }
    for column, statement in migrations.items():
        if column not in columns:
            db.execute(statement)


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


def _normalize_dns_name(value: str) -> str:
    return _normalize_host(value).rstrip(".")


def _resolve_cname_chain(host: str) -> list[str]:
    try:
        import dns.exception
        import dns.resolver
    except ImportError:
        return []

    chain: list[str] = []
    current = _normalize_dns_name(host)
    resolver = dns.resolver.Resolver()
    resolver.lifetime = 5
    resolver.timeout = 2

    for _ in range(8):
        try:
            answers = resolver.resolve(current, "CNAME")
        except (
            dns.resolver.NoAnswer,
            dns.resolver.NXDOMAIN,
            dns.resolver.NoNameservers,
            dns.exception.Timeout,
        ):
            return chain

        next_host = None
        for answer in answers:
            next_host = _normalize_dns_name(answer.to_text())
            break

        if next_host is None or next_host in chain:
            return chain

        chain.append(next_host)
        current = next_host

    return chain


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


def _cloudflare_configured() -> bool:
    return bool(os.getenv("CLOUDFLARE_API_TOKEN") and os.getenv("CLOUDFLARE_ZONE_ID"))


def _cloudflare_base_url() -> str:
    return os.getenv("CLOUDFLARE_API_BASE_URL", "https://api.cloudflare.com/client/v4").rstrip("/")


def _cloudflare_api_request(
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    query: dict[str, str | int] | None = None,
) -> dict[str, Any]:
    token = os.getenv("CLOUDFLARE_API_TOKEN")
    if not token:
        raise HTTPException(status_code=503, detail="Cloudflare API token is not configured")

    url = f"{_cloudflare_base_url()}{path}"
    if query:
        url = f"{url}?{urllib.parse.urlencode(query)}"

    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = {"errors": [{"message": body or error.reason}]}
        messages = [
            item.get("message", "Cloudflare request failed")
            for item in parsed.get("errors", [])
            if isinstance(item, dict)
        ]
        raise HTTPException(
            status_code=502,
            detail="; ".join(messages) or f"Cloudflare request failed with HTTP {error.code}",
        ) from error
    except urllib.error.URLError as error:
        raise HTTPException(status_code=502, detail=f"Cloudflare request failed: {error.reason}") from error


def _cloudflare_zone_path(path: str = "") -> str:
    zone_id = os.getenv("CLOUDFLARE_ZONE_ID")
    if not zone_id:
        raise HTTPException(status_code=503, detail="Cloudflare zone ID is not configured")
    return f"/zones/{zone_id}/custom_hostnames{path}"


def _cloudflare_custom_hostname_payload(domain: str) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "hostname": domain,
        "ssl": {
            "method": os.getenv("CLOUDFLARE_CUSTOM_HOSTNAME_SSL_METHOD", "http"),
            "type": "dv",
            "settings": {
                "http2": "on",
                "min_tls_version": "1.2",
                "tls_1_3": "on",
            },
        },
    }

    certificate_authority = os.getenv("CLOUDFLARE_CUSTOM_HOSTNAME_CA")
    if certificate_authority:
        payload["ssl"]["certificate_authority"] = certificate_authority

    custom_origin_server = os.getenv("CLOUDFLARE_CUSTOM_HOSTNAME_ORIGIN")
    if custom_origin_server:
        payload["custom_origin_server"] = _normalize_host(custom_origin_server)

    custom_origin_sni = os.getenv("CLOUDFLARE_CUSTOM_HOSTNAME_ORIGIN_SNI")
    if custom_origin_sni:
        payload["custom_origin_sni"] = custom_origin_sni.strip()

    return payload


def _extract_cloudflare_result(response: dict[str, Any]) -> dict[str, Any]:
    if not response.get("success", False):
        errors = response.get("errors", [])
        messages = [item.get("message", "Cloudflare request failed") for item in errors if isinstance(item, dict)]
        raise HTTPException(status_code=502, detail="; ".join(messages) or "Cloudflare request failed")

    result = response.get("result")
    if not isinstance(result, dict):
        raise HTTPException(status_code=502, detail="Cloudflare response did not include a custom hostname")
    return result


def _find_cloudflare_custom_hostname(domain: str) -> dict[str, Any] | None:
    response = _cloudflare_api_request(
        "GET",
        _cloudflare_zone_path(),
        query={"hostname.exact": domain, "per_page": 5},
    )
    if not response.get("success", False):
        return None

    results = response.get("result", [])
    if not isinstance(results, list):
        return None
    for result in results:
        if isinstance(result, dict) and result.get("hostname") == domain:
            return result
    return None


def _get_cloudflare_custom_hostname(custom_hostname_id: str) -> dict[str, Any]:
    return _extract_cloudflare_result(
        _cloudflare_api_request("GET", _cloudflare_zone_path(f"/{custom_hostname_id}"))
    )


def _is_cloudflare_not_found_error(error: HTTPException) -> bool:
    detail = str(error.detail).lower()
    return "not found" in detail or "could not be found" in detail


def _create_cloudflare_custom_hostname(domain: str) -> dict[str, Any]:
    existing = _find_cloudflare_custom_hostname(domain)
    if existing is not None:
        return existing

    return _extract_cloudflare_result(
        _cloudflare_api_request(
            "POST",
            _cloudflare_zone_path(),
            payload=_cloudflare_custom_hostname_payload(domain),
        )
    )


def _stringify_cloudflare_detail(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for key in ("message", "error", "detail", "reason"):
            if value.get(key):
                return str(value[key])
        return json.dumps(value, sort_keys=True)
    return str(value)


def _cloudflare_diagnostics_from_result(result: dict[str, Any], error: str | None = None) -> list[str]:
    ssl = result.get("ssl") if isinstance(result.get("ssl"), dict) else {}
    diagnostic_values: list[Any] = []
    if error:
        diagnostic_values.append(error)

    for container in (result, ssl):
        for key in ("verification_errors", "validation_errors", "errors"):
            values = container.get(key)
            if isinstance(values, list):
                diagnostic_values.extend(values)
            elif values:
                diagnostic_values.append(values)

    diagnostics: list[str] = []
    for value in diagnostic_values:
        message = _stringify_cloudflare_detail(value)
        if message and message not in diagnostics:
            diagnostics.append(message)
    return diagnostics


def _cloudflare_status_from_result(result: dict[str, Any], error: str | None = None) -> CloudflareProvisioningStatus:
    hostname_status = result.get("status")
    ssl = result.get("ssl") if isinstance(result.get("ssl"), dict) else {}
    ssl_status = ssl.get("status")
    if _cloudflare_diagnostics_from_result(result, error):
        return "needs_attention"
    if hostname_status == "active" and ssl_status == "active":
        return "active"
    if hostname_status in {"blocked", "test_blocked", "test_failed"}:
        return "needs_attention"
    if isinstance(ssl_status, str) and ssl_status.endswith("_timed_out"):
        return "needs_attention"
    return "pending"


def _public_cloudflare_custom_hostname(
    domain: str | None,
    status: CloudflareProvisioningStatus,
    message: str,
    result: dict[str, Any] | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    result = result or {}
    ssl = result.get("ssl") if isinstance(result.get("ssl"), dict) else {}
    diagnostics = _cloudflare_diagnostics_from_result(result, error)
    return {
        "domain": domain,
        "status": status,
        "message": message,
        "id": result.get("id"),
        "hostname": result.get("hostname", domain),
        "hostnameStatus": result.get("status"),
        "sslStatus": ssl.get("status"),
        "sslValidationMethod": ssl.get("method"),
        "syncedAt": datetime.now(UTC).isoformat(),
        "ownershipVerification": result.get("ownership_verification"),
        "ownershipVerificationHttp": result.get("ownership_verification_http"),
        "validationRecords": ssl.get("validation_records"),
        "diagnostics": diagnostics,
        "error": error,
    }


def _persist_cloudflare_result(
    db: sqlite3.Connection,
    domain: str,
    result: dict[str, Any],
    error: str | None = None,
) -> None:
    ssl = result.get("ssl") if isinstance(result.get("ssl"), dict) else {}
    db.execute(
        """
        UPDATE partner_domains
        SET cloudflare_custom_hostname_id = ?,
            cloudflare_hostname_status = ?,
            cloudflare_ssl_status = ?,
            cloudflare_ssl_validation_method = ?,
            cloudflare_error = ?,
            cloudflare_synced_at = ?
        WHERE domain = ?
        """,
        (
            result.get("id"),
            result.get("status"),
            ssl.get("status"),
            ssl.get("method"),
            error,
            datetime.now(UTC).isoformat(),
            domain,
        ),
    )


def _persist_cloudflare_error(db: sqlite3.Connection, domain: str, error: str) -> None:
    db.execute(
        """
        UPDATE partner_domains
        SET cloudflare_error = ?,
            cloudflare_synced_at = ?
        WHERE domain = ?
        """,
        (error, datetime.now(UTC).isoformat(), domain),
    )


def _clear_cloudflare_custom_hostname(db: sqlite3.Connection, domain: str, error: str | None = None) -> None:
    db.execute(
        """
        UPDATE partner_domains
        SET cloudflare_custom_hostname_id = NULL,
            cloudflare_hostname_status = NULL,
            cloudflare_ssl_status = NULL,
            cloudflare_ssl_validation_method = NULL,
            cloudflare_error = ?,
            cloudflare_synced_at = ?
        WHERE domain = ?
        """,
        (error, datetime.now(UTC).isoformat(), domain),
    )


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
    target_cname_chain = _resolve_cname_chain(target)
    target_names = {target, *target_cname_chain}
    domain_cname_chain = _resolve_cname_chain(domain)
    if target_names & set(domain_cname_chain):
        return _domain_verification_payload(
            domain,
            "connected",
            "DNS CNAME points to the Nexus target.",
        )
    if domain_cname_chain:
        return _domain_verification_payload(
            domain,
            "needs_attention",
            f"DNS CNAME points to {domain_cname_chain[-1]}, not {target}.",
        )

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
        f"DNS is resolving, but no public CNAME to {target} is visible. If this record is in Cloudflare, set it to DNS only while verifying.",
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


def _get_partner_domain(db: sqlite3.Connection, domain: str) -> sqlite3.Row | None:
    return db.execute("SELECT * FROM partner_domains WHERE domain = ?", (domain,)).fetchone()


def _public_stored_cloudflare_custom_hostname(
    partner_domain: sqlite3.Row | None,
    domain: str | None,
) -> dict[str, Any]:
    if not domain:
        return _public_cloudflare_custom_hostname(
            None,
            "not_configured",
            "Save a patient-facing domain before creating a Cloudflare custom hostname.",
        )

    if _is_local_development_host(domain):
        return _public_cloudflare_custom_hostname(
            domain,
            "skipped",
            "Local development domains do not need Cloudflare custom hostnames.",
        )

    if not _cloudflare_configured():
        return _public_cloudflare_custom_hostname(
            domain,
            "not_available",
            "Cloudflare is not configured for this environment.",
        )

    if partner_domain is None or partner_domain["cloudflare_custom_hostname_id"] is None:
        return _public_cloudflare_custom_hostname(
            domain,
            "pending",
            "Cloudflare will be created after DNS is confirmed.",
        )

    result = {
        "id": partner_domain["cloudflare_custom_hostname_id"],
        "hostname": domain,
        "status": partner_domain["cloudflare_hostname_status"],
        "ssl": {
            "status": partner_domain["cloudflare_ssl_status"],
            "method": partner_domain["cloudflare_ssl_validation_method"],
        },
    }
    diagnostics = _cloudflare_diagnostics_from_result(result, partner_domain["cloudflare_error"])
    status = _cloudflare_status_from_result(result, partner_domain["cloudflare_error"])
    message = "Cloudflare hostname is active." if status == "active" else "Cloudflare is still provisioning SSL."
    if status == "needs_attention":
        message = diagnostics[0] if diagnostics else "Cloudflare needs attention before this hostname can go live."
    response = _public_cloudflare_custom_hostname(
        domain,
        status,
        message,
        result=result,
        error=partner_domain["cloudflare_error"],
    )
    response["syncedAt"] = partner_domain["cloudflare_synced_at"]
    return response


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


def _is_allowed_cors_origin(origin: str, database_path: str | Path) -> bool:
    if origin in _allowed_origins():
        return True

    allowed_regex = _allowed_origin_regex()
    if allowed_regex and re.fullmatch(allowed_regex, origin):
        return True

    parsed = urllib.parse.urlparse(origin)
    if parsed.scheme != "https" or not parsed.netloc:
        return False

    domain = _normalize_host(parsed.netloc)
    with _connect(database_path) as db:
        return _get_partner_domain(db, domain) is not None


def _add_cors_headers(response: Response, origin: str, request: Request) -> None:
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = request.headers.get(
        "access-control-request-method",
        "GET,POST,PATCH,OPTIONS",
    )
    response.headers["Access-Control-Allow-Headers"] = request.headers.get(
        "access-control-request-headers",
        "Authorization,Content-Type",
    )

    vary = response.headers.get("Vary")
    if vary:
        vary_values = {value.strip() for value in vary.split(",")}
        if "Origin" not in vary_values:
            response.headers["Vary"] = f"{vary}, Origin"
    else:
        response.headers["Vary"] = "Origin"


def create_app(database_path: str | Path | None = None) -> FastAPI:
    resolved_database_path = database_path or _default_database_path()
    _initialize_database(resolved_database_path)
    _seed_demo_partner(resolved_database_path)

    app = FastAPI(title="Aeonic API", version="0.1.0")

    @app.middleware("http")
    async def cors_for_static_and_partner_origins(request: Request, call_next):
        origin = request.headers.get("origin")
        is_preflight = request.method == "OPTIONS" and "access-control-request-method" in request.headers
        allowed_origin = bool(origin and _is_allowed_cors_origin(origin, resolved_database_path))

        if is_preflight:
            response = Response(status_code=200 if allowed_origin else 400)
        else:
            response = await call_next(request)

        if origin and allowed_origin:
            _add_cors_headers(response, origin, request)

        return response

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

    @app.get("/partners/domain/setup", tags=["partners"])
    def partner_domain_setup(authorization: str | None = Header(default=None)) -> dict[str, object]:
        with _connect(resolved_database_path) as db:
            partner_id = _authenticated(db, "partner", authorization)
            partner = _get_partner_by_id(db, partner_id)
            if partner is None:
                raise HTTPException(status_code=401, detail="Invalid bearer token")

            return {
                "dns": {
                    "recordType": "CNAME",
                    "recordValue": _nexus_dns_target(),
                }
            }

    @app.get("/partners/domain/cloudflare-custom-hostname", tags=["partners"])
    def partner_domain_cloudflare_status(authorization: str | None = Header(default=None)) -> dict[str, object]:
        with _connect(resolved_database_path) as db:
            partner_id = _authenticated(db, "partner", authorization)
            partner = _get_partner_by_id(db, partner_id)
            if partner is None:
                raise HTTPException(status_code=401, detail="Invalid bearer token")

            domain = partner["clinic_domain"]
            partner_domain = _get_partner_domain(db, domain) if domain else None
            if (
                domain
                and partner_domain is not None
                and partner_domain["cloudflare_custom_hostname_id"]
                and _cloudflare_configured()
                and not _is_local_development_host(domain)
            ):
                try:
                    result = _get_cloudflare_custom_hostname(partner_domain["cloudflare_custom_hostname_id"])
                    _persist_cloudflare_result(db, domain, result)
                    partner_domain = _get_partner_domain(db, domain)
                except HTTPException as error:
                    if _is_cloudflare_not_found_error(error):
                        existing = _find_cloudflare_custom_hostname(domain)
                        if existing is not None:
                            _persist_cloudflare_result(db, domain, existing)
                        else:
                            _clear_cloudflare_custom_hostname(db, domain, str(error.detail))
                    else:
                        _persist_cloudflare_error(db, domain, str(error.detail))
                    partner_domain = _get_partner_domain(db, domain)
            return {"cloudflare": _public_stored_cloudflare_custom_hostname(partner_domain, domain)}

    @app.post("/partners/domain/cloudflare-custom-hostname", tags=["partners"])
    def partner_domain_cloudflare_create(authorization: str | None = Header(default=None)) -> dict[str, object]:
        with _connect(resolved_database_path) as db:
            partner_id = _authenticated(db, "partner", authorization)
            partner = _get_partner_by_id(db, partner_id)
            if partner is None:
                raise HTTPException(status_code=401, detail="Invalid bearer token")

            domain = partner["clinic_domain"]
            if not domain:
                raise HTTPException(status_code=422, detail="Save a patient-facing domain first")

            verification = _verify_domain(domain)
            if verification["status"] != "connected":
                return {
                    "verification": verification,
                    "cloudflare": _public_cloudflare_custom_hostname(
                        domain,
                        "dns_not_ready",
                        "DNS must resolve to the Nexus target before Cloudflare can issue SSL.",
                    ),
                }

            if _is_local_development_host(domain):
                return {
                    "verification": verification,
                    "cloudflare": _public_cloudflare_custom_hostname(
                        domain,
                        "skipped",
                        "Local development domains do not need Cloudflare custom hostnames.",
                    ),
                }

            if not _cloudflare_configured():
                raise HTTPException(status_code=503, detail="Cloudflare is not configured for this environment")

            partner_domain = _get_partner_domain(db, domain)
            try:
                if partner_domain is not None and partner_domain["cloudflare_custom_hostname_id"]:
                    try:
                        result = _get_cloudflare_custom_hostname(partner_domain["cloudflare_custom_hostname_id"])
                    except HTTPException as error:
                        if not _is_cloudflare_not_found_error(error):
                            raise
                        _clear_cloudflare_custom_hostname(db, domain, str(error.detail))
                        result = _create_cloudflare_custom_hostname(domain)
                else:
                    result = _create_cloudflare_custom_hostname(domain)
                _persist_cloudflare_result(db, domain, result)
            except HTTPException as error:
                _persist_cloudflare_error(db, domain, str(error.detail))
                raise

            diagnostics = _cloudflare_diagnostics_from_result(result)
            status = _cloudflare_status_from_result(result)
            message = (
                "Cloudflare hostname is active."
                if status == "active"
                else "Cloudflare accepted the hostname and is provisioning SSL."
            )
            if status == "needs_attention":
                message = diagnostics[0] if diagnostics else "Cloudflare accepted the hostname, but it needs attention before it can go live."

            return {
                "verification": verification,
                "cloudflare": _public_cloudflare_custom_hostname(domain, status, message, result=result),
            }

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
