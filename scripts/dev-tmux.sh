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
# AEONIC_TEST_DOMAIN=example.com scripts/dev-tmux.sh
TEST_DOMAIN="${AEONIC_TEST_DOMAIN:-domain-you-own.com}"
TUNNEL_NAME="${AEONIC_TUNNEL_NAME:-aeonic-local}"
SESSION_NAME="${AEONIC_TMUX_SESSION:-aeonic-dev}"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CLOUDFLARED_DIR="${CLOUDFLARED_DIR:-$HOME/.cloudflared}"
CONFIG_FILE="${CLOUDFLARED_CONFIG:-$CLOUDFLARED_DIR/$TUNNEL_NAME.yml}"

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
  exec tmux attach-session -t "$SESSION_NAME"
fi

LOCAL_ORIGINS="http://127.0.0.1:3000,http://127.0.0.1:5174,http://127.0.0.1:5173,http://localhost:3000,http://localhost:5174,http://localhost:5173"
TUNNEL_ORIGINS="https://nexus-local.$TEST_DOMAIN,https://partner-local.$TEST_DOMAIN,https://site-local.$TEST_DOMAIN"
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

tmux new-session -d -s "$SESSION_NAME" -n site \
  "cd '$REPO_ROOT/apps/site' && npm run dev$HOLD"

tmux new-window -t "$SESSION_NAME" -n tunnel \
  "cloudflared --config '$CONFIG_FILE' tunnel run '$TUNNEL_NAME'$HOLD"

tmux new-window -t "$SESSION_NAME" -n backend \
  "cd '$REPO_ROOT/backend' && APP_ENV=development ALLOWED_ORIGINS='$ALLOWED_ORIGINS' .venv/bin/uvicorn app.main:app --reload$HOLD"

tmux new-window -t "$SESSION_NAME" -n partner \
  "cd '$REPO_ROOT/apps/partner' && VITE_API_BASE_URL=http://127.0.0.1:8000 npm run dev$HOLD"

tmux new-window -t "$SESSION_NAME" -n nexus \
  "cd '$REPO_ROOT/apps/nexus' && VITE_API_BASE_URL='https://api-local.$TEST_DOMAIN' VITE_ALLOWED_HOSTS='nexus-local.$TEST_DOMAIN' npm run dev -- --port 5173 --strictPort$HOLD"

tmux select-window -t "$SESSION_NAME:site"
tmux attach-session -t "$SESSION_NAME"
