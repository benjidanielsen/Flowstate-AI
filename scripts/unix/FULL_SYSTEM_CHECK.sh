#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

announce() {
  echo
  echo "===== $1 ====="
}

ensure_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "[WARN] Skipping $2 because '$1' is not installed." >&2
    return 1
  fi
  return 0
}

announce "Python compile check"
python -m compileall \
  ai-gods/error_handling.py \
  ai-gods/project_manager_config.py \
  ai-gods/project_manager_enhanced.py \
  ai-gods/godmode_brain.py

announce "Python unit tests"
python -m unittest discover -s tests -p 'test_*.py'

announce "GODMODE health checks"
python ai-gods/project_manager_enhanced.py --health-check
python ai-gods/project_manager_enhanced.py --demo
python ai-gods/godmode_brain.py --show-plan >/dev/null

if ensure_command npm "workspace lint + build"; then
  announce "Node.js lint"
  npm run lint

  announce "Node.js build"
  npm run build
fi

if ensure_command playwright "end-to-end tests"; then
  announce "E2E smoke tests"
  npx playwright test --config=playwright.config.ts --reporter=list
fi

announce "System check completed"
