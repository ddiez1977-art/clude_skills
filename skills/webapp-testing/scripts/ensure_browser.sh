#!/usr/bin/env bash
# ensure_browser.sh — deja Playwright + un navegador headless listos, de forma idempotente.
# Uso:  bash scripts/ensure_browser.sh [chromium|firefox|webkit]   (por defecto chromium)
# Orden: (1) paquete python playwright  (2) navegador ya presente  (3) playwright install
#        (4) navegador del sistema (apt) como último recurso.
set -u
ENGINE="${1:-chromium}"
BROWSERS="${PLAYWRIGHT_BROWSERS_PATH:-$HOME/.cache/ms-playwright}"

# 1) Paquete Python
python3 -c "import playwright" 2>/dev/null || {
  echo "[ensure] instalando paquete playwright (pip)…"
  pip install -q playwright 2>&1 | grep -v "running pip as the 'root'" -i
}

# 2) ¿Ya hay binario del motor? (cloud: suele venir preinstalado en /opt/pw-browsers)
if ls -d "$BROWSERS"/${ENGINE}* >/dev/null 2>&1 || ls -d "$BROWSERS"/chromium_headless_shell* >/dev/null 2>&1 && [ "$ENGINE" = chromium ]; then
  echo "[ensure] ✅ $ENGINE ya presente en $BROWSERS (no se descarga nada)"
else
  # 3) Descarga oficial (con deps del SO). En cloud NO usar si el entorno la bloquea.
  echo "[ensure] descargando $ENGINE…"
  if ! python3 -m playwright install --with-deps "$ENGINE" 2>&1 | tail -3; then
    # 4) Fallback: navegador del sistema (lo localiza browser_launcher.py)
    echo "[ensure] ⚠️ playwright install falló → intento navegador del sistema"
    (apt-get install -y -q chromium || apt-get install -y -q chromium-browser) 2>&1 | tail -2
  fi
fi

# Verificación real: lanzar y abrir about:blank
python3 "$(dirname "$0")/browser_launcher.py" --check "$ENGINE"
