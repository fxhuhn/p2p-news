#!/usr/bin/env bash
set -euo pipefail

# Resolve physical script directory even through symlinks
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
REPO_ROOT="$(cd -P "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

VENV="$REPO_ROOT/.venv/bin"

# If stdout is redirected (e.g. Antigravity lifecycle hook capture), stream output to stderr and emit {} on stdout
IS_HOOK=false
if [ ! -t 1 ]; then
  IS_HOOK=true
fi

run_step() {
  if [ "$IS_HOOK" = true ]; then
    "$@" >&2
  else
    "$@"
  fi
}

log_msg() {
  if [ "$IS_HOOK" = true ]; then
    echo "$@" >&2
  else
    echo "$@"
  fi
}

log_msg "=== [1/5] Ruff Format Check ==="
run_step "$VENV/ruff" format --check .

log_msg "=== [2/5] Ruff Lint Check ==="
run_step "$VENV/ruff" check .

log_msg "=== [3/5] MyPy Static Type Check ==="
run_step "$VENV/mypy" .

log_msg "=== [4/5] Pre-Commit Run ==="
run_step "$VENV/pre-commit" run --all-files

log_msg "=== [5/5] Pytest Test Suite ==="
run_step "$VENV/pytest"

log_msg "=== ALL CHECKS PASSED ==="

if [ "$IS_HOOK" = true ]; then
  echo "{}"
fi
