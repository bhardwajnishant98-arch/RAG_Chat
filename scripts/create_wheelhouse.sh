#!/usr/bin/env bash
set -euo pipefail

# Build an offline wheelhouse on a machine with internet access.
# Usage:
#   scripts/create_wheelhouse.sh [output_dir]
#   scripts/create_wheelhouse.sh --help

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  cat <<USAGE
Usage: scripts/create_wheelhouse.sh [output_dir]

Arguments:
  output_dir   Destination folder for downloaded wheels (default: wheelhouse)

Environment:
  PYTHON_BIN   Python executable (default: python3)
USAGE
  exit 0
fi

OUTPUT_DIR="${1:-wheelhouse}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "Creating wheelhouse in: ${OUTPUT_DIR}"
mkdir -p "${OUTPUT_DIR}"

"${PYTHON_BIN}" -m pip download -r requirements.txt -d "${OUTPUT_DIR}"

echo "Done. Copy '${OUTPUT_DIR}' to your target environment and run:"
echo "  scripts/bootstrap.sh --wheelhouse ${OUTPUT_DIR}"
