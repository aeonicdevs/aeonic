#!/usr/bin/env bash
set -euo pipefail

# Surface failures in this launcher itself (which line failed and the exit code).
trap 'echo "[dev-tmux] failed at line $LINENO (exit code $?)" >&2' ERR

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
# AEONIC_TEST_DOMAIN=example.com AEONIC_DEV_SUBDOMAIN=nathan scripts/dev-tmux.sh
TEST_DOMAIN="${AEONIC_TEST_DOMAIN:-domain-you-own.com}"
DEV_SUBDOMAIN="${AEONIC_DEV_SUBDOMAIN:-$(whoami | tr '[:upper:]' '[:lower:]' | tr -cd 'a-z0-9-')}"
TUNNEL_NAME="${AEONIC_TUNNEL_NAME:-aeonic-local}"
SESSION_NAME="${AEONIC_TMUX_SESSION:-aeonic-dev}"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CLOUDFLARED_DIR="${CLOUDFLARED_DIR:-$HOME/.cloudflared}"
CONFIG_FILE="${CLOUDFLARED_CONFIG:-$CLOUDFLARED_DIR/$TUNNEL_NAME.yml}"
API_HOSTNAME="${AEONIC_API_TUNNEL_HOSTNAME:-api-$DEV_SUBDOMAIN-local.$TEST_DOMAIN}"
NEXUS_HOSTNAME="${AEONIC_NEXUS_TUNNEL_HOSTNAME:-nexus-$DEV_SUBDOMAIN-local.$TEST_DOMAIN}"
PARTNER_HOSTNAME="${AEONIC_PARTNER_TUNNEL_HOSTNAME:-partner-$DEV_SUBDOMAIN-local.$TEST_DOMAIN}"
WWW_HOSTNAME="${AEONIC_WWW_TUNNEL_HOSTNAME:-www-$DEV_SUBDOMAIN-local.$TEST_DOMAIN}"
PATIENT_DOMAIN_ALIAS_TARGET="${AEONIC_PATIENT_DOMAIN_ALIAS_TARGET:-app.nathansdentistry.com}"
NEXUS_DNS_TARGET="${NEXUS_DNS_TARGET:-$NEXUS_HOSTNAME}"
CLOUDFLARE_API_TOKEN="${CLOUDFLARE_API_TOKEN:-}"
CLOUDFLARE_ZONE_ID="${CLOUDFLARE_ZONE_ID:-}"
CLOUDFLARE_CUSTOM_HOSTNAME_SSL_METHOD="${CLOUDFLARE_CUSTOM_HOSTNAME_SSL_METHOD:-http}"
CLOUDFLARE_CUSTOM_HOSTNAME_CA="${CLOUDFLARE_CUSTOM_HOSTNAME_CA:-}"
CLOUDFLARE_CUSTOM_HOSTNAME_ORIGIN="${CLOUDFLARE_CUSTOM_HOSTNAME_ORIGIN:-}"
CLOUDFLARE_CUSTOM_HOSTNAME_ORIGIN_SNI="${CLOUDFLARE_CUSTOM_HOSTNAME_ORIGIN_SNI:-}"

required_commands=(tmux cloudflared npm)
for command_name in "${required_commands[@]}"; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    echo "Missing required command: $command_name" >&2
    exit 1
  fi
done

if [[ "$TEST_DOMAIN" == "domain-you-own.com" ]]; then
  echo "Set AEONIC_TEST_DOMAIN in scripts/dev-local.env to a domain you control before starting local services." >&2
  exit 1
fi

if [[ ! -x "$REPO_ROOT/backend/.venv/bin/uvicorn" ]]; then
  echo "Missing backend virtualenv command: $REPO_ROOT/backend/.venv/bin/uvicorn" >&2
  echo "Create it from backend/ first, then rerun this script." >&2
  exit 1
fi

if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
  echo "tmux session '$SESSION_NAME' already exists. Attaching..."
  if [[ "${AEONIC_TMUX_ATTACH:-1}" == "0" ]]; then
    tmux list-windows -t "$SESSION_NAME"
    exit 0
  fi
  exec tmux attach-session -t "$SESSION_NAME"
fi

LOCAL_ORIGINS="http://127.0.0.1:3000,http://127.0.0.1:5174,http://127.0.0.1:5173,http://localhost:3000,http://localhost:5174,http://localhost:5173"
TUNNEL_ORIGINS="https://$NEXUS_HOSTNAME,https://$PARTNER_HOSTNAME,https://$WWW_HOSTNAME"
ALLOWED_ORIGINS="$LOCAL_ORIGINS,$TUNNEL_ORIGINS"

# Appended to each tmux pane command: if the process exits/crashes, print its
# exit status and drop into a shell so the error output stays on screen instead
# of the window disappearing. Set KEEP_PANES=0 to restore the old behavior.
if [[ "${KEEP_PANES:-1}" == "0" ]]; then
  HOLD=""
else
  # NOTE: a bare interactive shell does not stay alive in a pane that has no
  # client attached yet (the windows are created before the final attach), so
  # block on `read` first to keep the pane open, then drop into a shell.
  # Use 'ec' (not 'status'): 'status' is a read-only special var in zsh and
  # assigning to it aborts the pane's `zsh -c` before it reaches `read`.
  HOLD='; ec=$?; echo; echo ">>> command exited with status $ec (see output above)"; echo ">>> press Enter to open a shell in this pane..."; read -r _; exec "${SHELL:-/bin/sh}"'
fi

tmux new-session -d -s "$SESSION_NAME" -n www \
  "cd '$REPO_ROOT/apps/marketing' && npm run dev$HOLD"

tmux new-window -t "$SESSION_NAME" -n tunnel \
  "cloudflared --config '$CONFIG_FILE' tunnel run '$TUNNEL_NAME'$HOLD"

tmux new-window -t "$SESSION_NAME" -n backend \
  "cd '$REPO_ROOT/backend' && APP_ENV=development ALLOWED_ORIGINS='$ALLOWED_ORIGINS' NEXUS_DNS_TARGET='$NEXUS_DNS_TARGET' AEONIC_DEV_DOMAIN_ALIASES='$NEXUS_HOSTNAME=$PATIENT_DOMAIN_ALIAS_TARGET' CLOUDFLARE_API_TOKEN='$CLOUDFLARE_API_TOKEN' CLOUDFLARE_ZONE_ID='$CLOUDFLARE_ZONE_ID' CLOUDFLARE_CUSTOM_HOSTNAME_SSL_METHOD='$CLOUDFLARE_CUSTOM_HOSTNAME_SSL_METHOD' CLOUDFLARE_CUSTOM_HOSTNAME_CA='$CLOUDFLARE_CUSTOM_HOSTNAME_CA' CLOUDFLARE_CUSTOM_HOSTNAME_ORIGIN='$CLOUDFLARE_CUSTOM_HOSTNAME_ORIGIN' CLOUDFLARE_CUSTOM_HOSTNAME_ORIGIN_SNI='$CLOUDFLARE_CUSTOM_HOSTNAME_ORIGIN_SNI' .venv/bin/uvicorn app.main:app --reload$HOLD"

tmux new-window -t "$SESSION_NAME" -n partner \
  "cd '$REPO_ROOT/apps/partner' && VITE_API_BASE_URL=http://127.0.0.1:8000 VITE_ALLOWED_HOSTS='$PARTNER_HOSTNAME' npm run dev$HOLD"

tmux new-window -t "$SESSION_NAME" -n nexus \
  "cd '$REPO_ROOT/apps/nexus' && VITE_API_BASE_URL='https://$API_HOSTNAME' VITE_ALLOWED_HOSTS='$NEXUS_HOSTNAME' npm run dev -- --port 5173 --strictPort$HOLD"

tmux select-window -t "$SESSION_NAME:www"
if [[ "${AEONIC_TMUX_ATTACH:-1}" == "0" ]]; then
  tmux list-windows -t "$SESSION_NAME"
  exit 0
fi
tmux attach-session -t "$SESSION_NAME"
