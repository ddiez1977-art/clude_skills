#!/usr/bin/env python3
"""
verify_runtime.py — Verificación de RUNTIME de una página con Playwright (caja negra).

Ejecuta de verdad la página en Chromium headless y comprueba lo que el análisis
estático NO puede ver. Está pensado para encadenarse DESPUÉS de:
  · debug-html-monolito  → tras pasar node --check / div balance / IDs huérfanos
  · clonar-proyecto (F3) → smoke test post-deploy, checks marcados 🤖 automática

QUÉ COMPRUEBA
────────────────────────────────────────────────────────────────────────────
  1. Errores de consola        (console.error / console.warning)
  2. Excepciones no capturadas (pageerror → "función no definida", "Cannot set … null")
  3. Colisión de clases CSS    elementos con display≠none pero offsetHeight=0 (invisibles)
  4. Smoke test de clicks      pulsa botones y comprueba que no revientan la consola
  5. Screenshot full-page      para inspección visual

Funciona con archivos LOCALES (file://) — ideal para monolitos HTML — o con una URL.

USO
────────────────────────────────────────────────────────────────────────────
Monolito local (lo más habitual en tus portales):
  python scripts/verify_runtime.py ./index.html

Con URL (app ya servida, p.ej. tras with_server.py):
  python scripts/verify_runtime.py http://localhost:5173

Comprobar clases concretas que acabas de añadir (detecta colisión CSS al insertar HTML):
  python scripts/verify_runtime.py ./index.html --classes ".ctx-body,.dc-body,.mod-body"

Smoke test: pulsar todos los botones visibles y ver si algo peta:
  python scripts/verify_runtime.py ./index.html --click-buttons

Pulsar selectores concretos en orden:
  python scripts/verify_runtime.py ./index.html --click "text=Empezar" --click "#btn-quiz"

OPCIONES
────────────────────────────────────────────────────────────────────────────
  target               Ruta a un .html local o URL http(s):// (posicional, obligatorio)
  --out DIR            Carpeta de salida para report.json, console.log y screenshot.png
                       (default: ./verify_out — en el workspace, NO /mnt/user-data)
  --wait ESTADO        Estado de carga a esperar: load | domcontentloaded | networkidle
                       (default: networkidle — imprescindible en apps dinámicas)
  --classes LISTA      Clases CSS separadas por coma a auditar específicamente por colisión
  --click-buttons      Pulsa TODOS los botones visibles (smoke test) y observa la consola
  --click SEL          Pulsa un selector concreto (repetible, en orden)
  --settle MS          Espera tras cada acción/carga en ms (default: 800)
  --viewport WxH       Tamaño de viewport (default: 390x844, móvil — Mobile First)
  --no-screenshot      No guardar screenshot

CÓDIGO DE SALIDA
────────────────────────────────────────────────────────────────────────────
  0  → sin errores de consola, sin excepciones, sin colisiones CSS
  1  → se detectó al menos un problema (revisa el resumen y report.json)
  2  → error de uso / no se pudo cargar la página
"""
import argparse
import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).parent))
from browser_launcher import launch


def to_url(target):
    if target.startswith(("http://", "https://", "file://")):
        return target
    p = Path(target).resolve()
    if not p.exists():
        print(f"[verify] ❌ No existe el archivo: {p}", file=sys.stderr)
        sys.exit(2)
    return p.as_uri()


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("target", help="Ruta a .html local o URL http(s)://")
    ap.add_argument("--out", default="./verify_out")
    ap.add_argument("--wait", default="networkidle",
                    choices=["load", "domcontentloaded", "networkidle"])
    ap.add_argument("--classes", default="")
    ap.add_argument("--click-buttons", action="store_true")
    ap.add_argument("--click", action="append", default=[])
    ap.add_argument("--settle", type=int, default=800)
    ap.add_argument("--viewport", default="390x844")
    ap.add_argument("--no-screenshot", action="store_true")
    ap.add_argument("--browser", default="chromium", choices=["chromium", "firefox", "webkit"],
                    help="Motor preferido (cross-browser); con fallback automático")
    args = ap.parse_args()

    url = to_url(args.target)
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    try:
        vw, vh = (int(x) for x in args.viewport.lower().split("x"))
    except ValueError:
        print("[verify] ❌ --viewport debe ser WxH, p.ej. 390x844", file=sys.stderr)
        sys.exit(2)

    console_msgs = []   # {type, text}
    page_errors = []    # str

    with sync_playwright() as p:
        browser, binfo = launch(p, args.browser)
        print(f"[verify] 🌐 Navegador: {binfo}")
        page = browser.new_page(viewport={"width": vw, "height": vh})

        page.on("console", lambda m: console_msgs.append({"type": m.type, "text": m.text}))
        page.on("pageerror", lambda e: page_errors.append(str(e)))

        print(f"[verify] ▶ Cargando {url}")
        try:
            page.goto(url, wait_until="load", timeout=30000)
            page.wait_for_load_state(args.wait, timeout=30000)
        except Exception as e:
            print(f"[verify] ⚠ Aviso al esperar '{args.wait}': {e}")
        page.wait_for_timeout(args.settle)

        # ── 3. Colisión CSS: visible por estilo pero altura 0 ────────────────
        target_classes = [c.strip() for c in args.classes.split(",") if c.strip()]
        collisions = page.evaluate(
            """(classes) => {
                const bad = [];
                const targeted = classes.length > 0;
                const scope = targeted
                    ? classes.flatMap(c => Array.from(document.querySelectorAll(c)))
                    : Array.from(document.querySelectorAll('body *'));
                for (const el of scope) {
                    const cs = getComputedStyle(el);
                    const hasText = (el.textContent || '').trim().length > 0;
                    if (!hasText) continue;
                    let reason = null;
                    if (targeted && (cs.display === 'none' || cs.visibility === 'hidden')) {
                        // Clase que TÚ afirmas que debe verse, pero está oculta (clase reservada).
                        reason = 'oculto (' + cs.display + '/' + cs.visibility + ')';
                    } else if (cs.display !== 'none' && cs.visibility !== 'hidden'
                               && el.offsetHeight === 0 && el.offsetWidth > 0) {
                        // Visible por estilo pero altura 0 → colisión clásica (offsetHeight=0, display:block).
                        reason = 'offsetHeight=0 con display:' + cs.display;
                    }
                    if (reason) {
                        bad.push({
                            tag: el.tagName.toLowerCase(),
                            id: el.id || null,
                            cls: el.className && el.className.toString ? el.className.toString().slice(0,80) : '',
                            display: cs.display,
                            reason: reason,
                            text: (el.textContent || '').trim().slice(0, 50)
                        });
                    }
                }
                // Deduplicar por (tag,id,cls)
                const seen = new Set(), uniq = [];
                for (const b of bad) {
                    const k = b.tag + '|' + b.id + '|' + b.cls;
                    if (!seen.has(k)) { seen.add(k); uniq.push(b); }
                }
                return uniq.slice(0, 40);
            }""",
            target_classes,
        )

        # ── 4. Smoke test de clicks ──────────────────────────────────────────
        clicks_report = []

        def do_click(desc, locator):
            before = len(page_errors)
            try:
                locator.click(timeout=3000)
                page.wait_for_timeout(args.settle)
                new_errs = page_errors[before:]
                clicks_report.append({"target": desc, "ok": not new_errs, "errors": new_errs})
            except Exception as e:
                clicks_report.append({"target": desc, "ok": False, "errors": [f"click falló: {e}"]})

        for sel in args.click:
            do_click(sel, page.locator(sel).first)

        if args.click_buttons:
            buttons = page.locator("button:visible").all()
            print(f"[verify] ▶ Smoke test: {len(buttons)} botones visibles")
            for i, btn in enumerate(buttons[:25]):  # cap de seguridad
                try:
                    label = (btn.inner_text() or f"button[{i}]").strip()[:40] or f"button[{i}]"
                except Exception:
                    label = f"button[{i}]"
                do_click(label, btn)

        # ── 5. Screenshot ────────────────────────────────────────────────────
        shot = None
        if not args.no_screenshot:
            shot = out / "screenshot.png"
            try:
                page.screenshot(path=str(shot), full_page=True)
            except Exception as e:
                print(f"[verify] ⚠ No se pudo capturar screenshot: {e}")
                shot = None

        browser.close()

    # ── Salida ───────────────────────────────────────────────────────────────
    errors = [m for m in console_msgs if m["type"] == "error"]
    warnings = [m for m in console_msgs if m["type"] in ("warning", "warn")]
    failed_clicks = [c for c in clicks_report if not c["ok"]]

    with open(out / "console.log", "w", encoding="utf-8") as f:
        for m in console_msgs:
            f.write(f"[{m['type']}] {m['text']}\n")

    report = {
        "url": url,
        "console_errors": errors,
        "console_warnings": warnings,
        "page_errors": page_errors,
        "css_collisions": collisions,
        "clicks": clicks_report,
        "screenshot": str(shot) if shot else None,
    }
    with open(out / "report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("\n" + "─" * 60)
    print(f"  RESUMEN DE VERIFICACIÓN — {url}")
    print("─" * 60)
    print(f"  {'✗' if errors else '✓'} Errores de consola:        {len(errors)}")
    print(f"  {'✗' if page_errors else '✓'} Excepciones no capturadas: {len(page_errors)}")
    print(f"  {'✗' if collisions else '✓'} Colisiones CSS (offsetH=0): {len(collisions)}")
    print(f"  {'✗' if failed_clicks else '✓'} Clicks que rompieron algo:  {len(failed_clicks)}/{len(clicks_report)}")
    print(f"  ⚠ Warnings de consola:      {len(warnings)}")
    print("─" * 60)

    def show(title, items, fmt):
        if items:
            print(f"\n  {title}:")
            for it in items[:10]:
                print(f"    • {fmt(it)}")

    show("EXCEPCIONES", page_errors, lambda e: e.splitlines()[0][:110])
    show("ERRORES DE CONSOLA", errors, lambda m: m["text"][:110])
    show("COLISIONES CSS", collisions,
         lambda c: f"<{c['tag']} id={c['id']} class='{c['cls']}'> {c['reason']} — \"{c['text']}\"")
    show("CLICKS FALLIDOS", failed_clicks,
         lambda c: f"{c['target']} → {'; '.join(c['errors'])[:90]}")

    print(f"\n  📂 Report completo: {out}/report.json")
    if shot:
        print(f"  🖼  Screenshot:      {shot}")
    print()

    problems = bool(errors or page_errors or collisions or failed_clicks)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
