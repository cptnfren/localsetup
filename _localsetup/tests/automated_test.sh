#!/usr/bin/env bash
# Localsetup v2 - Minimal automated tests
set -euo pipefail
ENGINE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ENGINE_DIR"
PASS=0
FAIL=0

run_test() {
  if eval "$@" >/dev/null 2>&1; then
    echo "[PASS] $*"; ((PASS++)) || true; return 0
  else
    echo "[FAIL] $*"; ((FAIL++)) || true; return 1
  fi
}

echo "Localsetup v2 - Automated tests"
echo "==============================="
source "$ENGINE_DIR/lib/data_paths.sh"
run_test "[[ -n \"$(get_engine_dir)\" ]]"
run_test "[[ -n \"$(get_user_data_dir)\" ]]"
run_test "[[ -n \"$(get_project_root)\" ]]"
source "$ENGINE_DIR/discovery/core/os_detector.sh"
run_test "[[ -n \"$(detect_os)\" ]]"
run_test "[[ -f \"$ENGINE_DIR/lib/json_formatter.sh\" ]]"
run_test "[[ -f \"$ENGINE_DIR/tools/deploy\" ]]"
run_test "[[ -d \"$ENGINE_DIR/skills\" ]]"
run_test "[[ -d \"$ENGINE_DIR/templates\" ]]"
echo ""
echo "Result: $PASS passed, $FAIL failed"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
