#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/dev-local.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$SCRIPT_DIR/dev-local.env"
  set +a
elif [[ -f "$SCRIPT_DIR/dev-local.example.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$SCRIPT_DIR/dev-local.example.env"
  set +a
fi

# Copy scripts/dev-local.example.env to scripts/dev-local.env and change it once,
# or override it when running:
# AEONIC_TEST_DOMAIN=example.com AEONIC_DEV_SUBDOMAIN=nathan scripts/setup-cloudflare-local-tunnel.sh
TEST_DOMAIN="${AEONIC_TEST_DOMAIN:-domain-you-own.com}"
DEV_SUBDOMAIN="${AEONIC_DEV_SUBDOMAIN:-$(whoami | tr '[:upper:]' '[:lower:]' | tr -cd 'a-z0-9-')}"
TUNNEL_NAME="${AEONIC_TUNNEL_NAME:-aeonic-local}"
CLOUDFLARED_DIR="${CLOUDFLARED_DIR:-$HOME/.cloudflared}"
CONFIG_FILE="${CLOUDFLARED_CONFIG:-$CLOUDFLARED_DIR/$TUNNEL_NAME.yml}"
API_HOSTNAME="${AEONIC_API_TUNNEL_HOSTNAME:-api.$DEV_SUBDOMAIN.local.$TEST_DOMAIN}"
NEXUS_HOSTNAME="${AEONIC_NEXUS_TUNNEL_HOSTNAME:-nexus.$DEV_SUBDOMAIN.local.$TEST_DOMAIN}"
PARTNER_HOSTNAME="${AEONIC_PARTNER_TUNNEL_HOSTNAME:-partner.$DEV_SUBDOMAIN.local.$TEST_DOMAIN}"
WWW_HOSTNAME="${AEONIC_WWW_TUNNEL_HOSTNAME:-www.$DEV_SUBDOMAIN.local.$TEST_DOMAIN}"

required_commands=(cloudflared)
for command_name in "${required_commands[@]}"; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Missing required command: $command_name" >&2
    exit 1
  fi
done

if [[ "$TEST_DOMAIN" == "domain-you-own.com" ]]; then
  echo "Set AEONIC_TEST_DOMAIN in scripts/dev-local.env to a domain you control before creating Cloudflare DNS routes." >&2
  exit 1
fi

mkdir -p "$CLOUDFLARED_DIR"

if [[ ! -f "$CLOUDFLARED_DIR/cert.pem" ]]; then
  echo "cloudflared is not logged in yet. A browser window will open."
  cloudflared tunnel login
fi

if ! cloudflared tunnel info "$TUNNEL_NAME" >/dev/null 2>&1; then
  cloudflared tunnel create "$TUNNEL_NAME"
fi

TUNNEL_ID="$(cloudflared tunnel info "$TUNNEL_NAME" 2>/dev/null | awk -F':' '/^[[:space:]]*ID:/ { gsub(/^[[:space:]]+|[[:space:]]+$/, "", $2); print $2; exit }')"
if [[ -z "$TUNNEL_ID" ]]; then
  echo "Unable to read tunnel ID for $TUNNEL_NAME. Run 'cloudflared tunnel info $TUNNEL_NAME' and update $CONFIG_FILE manually." >&2
  exit 1
fi

CREDENTIALS_FILE="$CLOUDFLARED_DIR/$TUNNEL_ID.json"
if [[ ! -f "$CREDENTIALS_FILE" ]]; then
  echo "Expected credentials file does not exist: $CREDENTIALS_FILE" >&2
  exit 1
fi

cat > "$CONFIG_FILE" <<YAML
tunnel: $TUNNEL_NAME
credentials-file: $CREDENTIALS_FILE

ingress:
  - hostname: $API_HOSTNAME
    service: http://127.0.0.1:8000

  - hostname: $NEXUS_HOSTNAME
    service: http://127.0.0.1:5173

  - hostname: $PARTNER_HOSTNAME
    service: http://127.0.0.1:5174

  - hostname: $WWW_HOSTNAME
    service: http://127.0.0.1:3000

  - service: http_status:404
YAML

route_dns() {
  local hostname="$1"
  local output
  if ! output="$(cloudflared tunnel route dns "$TUNNEL_NAME" "$hostname" 2>&1)"; then
    echo "$output" >&2
    echo "Unable to create DNS route for $hostname." >&2
    echo "Check whether that DNS record already exists in Cloudflare and points to another target." >&2
    exit 1
  fi
  echo "$output"
  if ! grep -Fq "$hostname " <<<"$output"; then
    echo "Cloudflare did not create the expected DNS route for $hostname." >&2
    echo "It may have created the record under a different zone. Re-run 'cloudflared tunnel login' and select $TEST_DOMAIN." >&2
    exit 1
  fi
}

route_dns "$API_HOSTNAME"
route_dns "$NEXUS_HOSTNAME"
route_dns "$PARTNER_HOSTNAME"
route_dns "$WWW_HOSTNAME"

cloudflared --config "$CONFIG_FILE" tunnel ingress validate

cat <<EOF

Cloudflare local tunnel setup complete.

Tunnel: $TUNNEL_NAME
Config: $CONFIG_FILE

Routes:
  https://$API_HOSTNAME
  https://$NEXUS_HOSTNAME
  https://$PARTNER_HOSTNAME
  https://$WWW_HOSTNAME

Daily startup:
  AEONIC_TEST_DOMAIN=$TEST_DOMAIN AEONIC_DEV_SUBDOMAIN=$DEV_SUBDOMAIN scripts/dev-tmux.sh
EOF
