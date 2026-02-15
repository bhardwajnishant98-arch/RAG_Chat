#!/usr/bin/env bash
set -euo pipefail

# knowledge-agent bootstrap helper
# Supports:
# - normal online install
# - proxy-based install
# - offline install from local wheelhouse

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"
WHEELHOUSE_DIR="${WHEELHOUSE_DIR:-}"
PROXY_URL="${PROXY_URL:-}"
INDEX_URL="${INDEX_URL:-https://pypi.org/simple}"

print_help() {
  cat <<USAGE
Usage: scripts/bootstrap.sh [options]

Options:
  --python <bin>         Python executable (default: python3)
  --venv <path>          Virtual environment path (default: .venv)
  --wheelhouse <path>    Install offline from wheel directory
  --proxy <url>          Proxy URL for pip, e.g. http://host:port
  --index-url <url>      pip index URL (default: https://pypi.org/simple)
  -h, --help             Show this help

Environment alternatives:
  PYTHON_BIN, VENV_DIR, WHEELHOUSE_DIR, PROXY_URL, INDEX_URL
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --python)
      PYTHON_BIN="$2"; shift 2 ;;
    --venv)
      VENV_DIR="$2"; shift 2 ;;
    --wheelhouse)
      WHEELHOUSE_DIR="$2"; shift 2 ;;
    --proxy)
      PROXY_URL="$2"; shift 2 ;;
    --index-url)
      INDEX_URL="$2"; shift 2 ;;
    -h|--help)
      print_help; exit 0 ;;
    *)
      echo "Unknown option: $1" >&2
      print_help
      exit 1 ;;
  esac
done

echo "[1/5] Creating virtual environment at ${VENV_DIR}"
"${PYTHON_BIN}" -m venv "${VENV_DIR}"

# shellcheck disable=SC1090
source "${VENV_DIR}/bin/activate"

echo "[2/5] Upgrading pip/setuptools/wheel"
python -m pip install --upgrade pip setuptools wheel

PIP_ARGS=()
if [[ -n "${PROXY_URL}" ]]; then
  echo "[3/5] Configuring proxy: ${PROXY_URL}"
  PIP_ARGS+=("--proxy" "${PROXY_URL}")
else
  echo "[3/5] No proxy configured"
fi

if [[ -n "${WHEELHOUSE_DIR}" ]]; then
  if [[ ! -d "${WHEELHOUSE_DIR}" ]]; then
    echo "Wheelhouse directory not found: ${WHEELHOUSE_DIR}" >&2
    exit 1
  fi
  echo "[4/5] Installing dependencies from local wheelhouse: ${WHEELHOUSE_DIR}"
  pip install --no-index --find-links "${WHEELHOUSE_DIR}" -r requirements.txt
else
  echo "[4/5] Installing dependencies from index: ${INDEX_URL}"
  pip install "${PIP_ARGS[@]}" --index-url "${INDEX_URL}" -r requirements.txt
fi

echo "[5/5] Bootstrap complete"
echo "Next steps:"
echo "  cp .env.example .env"
echo "  # add OPENAI_API_KEY to .env"
echo "  python app/gradio_app.py"
