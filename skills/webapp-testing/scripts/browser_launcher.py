#!/usr/bin/env python3
"""
browser_launcher.py — lanzador de navegador headless con cadena de fallback.

Uso en un script Playwright:
    from browser_launcher import launch
    with sync_playwright() as p:
        browser, info = launch(p)            # chromium → binario cacheado → sistema → firefox → webkit
        browser, info = launch(p, "firefox") # preferir otro motor (cross-browser)

Comprobación rápida:  python browser_launcher.py --check [chromium|firefox|webkit]
"""
import glob
import os
import shutil
import sys

SYSTEM_BINARIES = ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable", "chrome")


def _cached_chromium():
    """Binario de Chromium ya descargado, aunque la versión no case con la de playwright."""
    root = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", os.path.expanduser("~/.cache/ms-playwright"))
    pats = ("chromium-*/chrome-linux*/chrome", "chromium_headless_shell-*/chrome-linux*/headless_shell",
            "chromium/chrome-linux*/chrome", "chromium-*/chrome-mac*/**/Chromium", "chromium-*/chrome-win*/chrome.exe")
    for pat in pats:
        hits = sorted(glob.glob(os.path.join(root, pat), recursive=True))
        if hits:
            return hits[-1]
    return None


def launch(p, engine="chromium", **kw):
    """Devuelve (browser, descripcion). Lanza siempre headless. Lanza RuntimeError si nada funciona."""
    kw.setdefault("headless", True)
    # --no-sandbox: necesario al ejecutar como root en contenedores
    chromium_args = ["--no-sandbox", "--disable-dev-shm-usage"]
    attempts = []
    if engine != "chromium":
        attempts.append((engine, lambda: getattr(p, engine).launch(**kw)))
    attempts.append(("chromium (playwright)", lambda: p.chromium.launch(args=chromium_args, **kw)))
    cached = _cached_chromium()
    if cached:
        attempts.append((f"chromium cacheado {cached}",
                         lambda: p.chromium.launch(executable_path=cached, args=chromium_args, **kw)))
    for name in SYSTEM_BINARIES:
        path = shutil.which(name)
        if path:
            attempts.append((f"navegador del sistema {path}",
                             lambda path=path: p.chromium.launch(executable_path=path, args=chromium_args, **kw)))
            break
    if engine == "chromium":
        attempts += [("firefox (fallback)", lambda: p.firefox.launch(**kw)),
                     ("webkit (fallback)", lambda: p.webkit.launch(**kw))]

    errors = []
    for desc, fn in attempts:
        try:
            return fn(), desc
        except Exception as e:  # noqa: BLE001
            errors.append(f"  · {desc}: {str(e).splitlines()[0]}")
    raise RuntimeError("No se pudo lanzar ningún navegador:\n" + "\n".join(errors) +
                       "\n→ ejecuta: bash scripts/ensure_browser.sh")


if __name__ == "__main__":
    engine = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "--check" else "chromium"
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b, info = launch(pw, engine)
        pg = b.new_page()
        pg.goto("about:blank")
        print(f"[ensure] ✅ navegador operativo: {info} (v{b.version})")
        b.close()
