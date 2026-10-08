#!/usr/bin/env bash
set -e

# ==============================================================================
# Container Entrypoint für P2P-News
# ==============================================================================
# Führt beim Starten oder Neustarten des Containers stets den Auto-Seed Check
# für Plattform-Profile aus, sodass gemountete Daten-Volumes stets mit den
# neuesten Seed-Profilen synchronisiert sind.
# ==============================================================================

if [ -f ".venv/bin/python" ]; then
    PYTHON_BIN=".venv/bin/python"
elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
else
    PYTHON_BIN="python"
fi

echo "=== [CONTAINER STARTUP] Starte Auto-Seed Check für Plattform-Profile ==="
$PYTHON_BIN -c "
from run_audit_scoring import ensure_platform_profiles
ensure_platform_profiles('data')
" || echo "[ENTRYPOINT] Warnung: Auto-Seed Check konnte nicht vollständig ausgeführt werden."

# Wenn das erste Argument ein Python-Skript, ein Flag (-*) oder explizit python ist, mit PYTHON_BIN ausführen
if [[ "$1" == *.py* ]] || [[ "$1" == -* ]] || [ "$1" = "python" ] || [ "$1" = "python3" ]; then
    if [ "$1" = "python" ] || [ "$1" = "python3" ]; then
        shift
    fi
    exec $PYTHON_BIN "$@"
elif [ -z "$1" ]; then
    exec $PYTHON_BIN scheduler.py
else
    exec "$@"
fi

