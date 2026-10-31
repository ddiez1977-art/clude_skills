---
name: webapp-testing
description: "Toolkit de verificación runtime de webapps con Playwright: ejecuta la página en el navegador real y captura lo que el análisis estático no ve. Úsala SIEMPRE que: \"verifica que funciona de verdad\", \"el modal no abre\", \"comprueba en el navegador\", \"test de regresión antes del deploy\", \"screenshot del estado actual\", \"el botón no hace nada\", \"errores en consola\", \"la sección aparece en blanco aunque el HTML existe\", o cuando debug-html-monolito pasa limpio pero la página sigue rota. Complementa a debug-html-monolito (estático antes de guardar) y clonar-proyecto (smoke test F3 post-deploy). Esta skill es la capa de EJECUCIÓN real en el navegador. Ver references/INTEGRACION_SKILLS.md para los puntos exactos de handoff entre skills.\n"
license: Complete terms in LICENSE.txt
---

# Web Application Testing

To test local web applications, write native Python Playwright scripts, or use the
bundled black-box scripts below.

**Helper Scripts Available**:
- `scripts/verify_runtime.py` - **Runtime verification** of a page: console errors,
  uncaught exceptions, CSS collisions (elements visible-by-style but `offsetHeight=0`),
  click smoke test, screenshot. Exits non-zero on any problem. Works with local files
  (`file://`) or a URL. **This is the layer the static skills lack.**
- `scripts/with_server.py` - Manages server lifecycle (supports multiple servers). Only
  needed for **dynamic** apps (npm/vite/Supabase local); for static HTML monoliths use
  `file://` directly.

**Always run scripts with `--help` first** to see usage. DO NOT read the source until you
try running the script first and find that a customized solution is absolutely necessary.
These scripts exist to be called directly as black-box scripts rather than ingested into
your context window.

## When to reach for this skill

Use it AFTER the static checks of the sibling skills, to confirm the page actually runs:

```
debug-html-monolito (static)  →  webapp-testing (runtime)  →  feedback loop
  node --check, div balance         verify_runtime.py: console errors,
  IDs, body{}, duplicates           exceptions, CSS collisions, click smoke test

clonar-proyecto F3 (smoke test) →  webapp-testing runs the 🤖 automatic checks
```

**Rule of thumb:** static validates the CODE; runtime validates the EXECUTION. In that
order, always. See `references/INTEGRACION_SKILLS.md` for the exact insertion points in
`debug-html-monolito` (§3, §5, §10) and `clonar-proyecto` (F1C SPA detection, §0.1b
Arquetipo D, F3 smoke test, F4.6 CSS collision).

## Quick start: runtime verification

```bash
# Monolito HTML local (portales, academias) — no server needed:
python scripts/verify_runtime.py ./index.html --click-buttons

# Check specific classes you just added (detects reserved-class CSS collision):
python scripts/verify_runtime.py ./index.html --classes ".ctx-body,.sub-panel,.mod-body"

# A deployed app / SPA — renders it for real (web_fetch returns empty root on SPAs):
python scripts/verify_runtime.py https://mi-clon.netlify.app --wait networkidle

# Exit 0 = clean · Exit 1 = problems (read report.json) · Exit 2 = usage/load error
```

Output goes to `./verify_out/` by default (`report.json`, `console.log`, `screenshot.png`);
override with `--out`.

### 📱 Mobile viewport — paso OBLIGATORIO para monolitos con modales/detail panels

Cualquier cambio que afecte modales, detail panels, `openDetail()`, chip-nav o overlays
**debe verificarse también en viewport móvil** antes de dar por bueno:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    # Desktop
    page_d = browser.new_page(viewport={"width": 1280, "height": 800})
    page_d.goto(f"file://{archivo_html}")
    page_d.wait_for_load_state("networkidle")
    errs_d = []
    page_d.on("pageerror", lambda e: errs_d.append(str(e)))

    # Mobile (iPhone 14)
    page_m = browser.new_page(viewport={"width": 390, "height": 844})
    page_m.goto(f"file://{archivo_html}")
    page_m.wait_for_load_state("networkidle")
    errs_m = []
    page_m.on("pageerror", lambda e: errs_m.append(str(e)))

    # Verificar que openDetail/modal es accesible en móvil
    result = page_m.evaluate("""() => {
        // Simula apertura de primer detail disponible
        var btn = document.querySelector('[onclick*="openDetail"], [onclick*="openDetailTab"]');
        if (btn) btn.click();
        var detail = document.querySelector('#view-detail, .detail-panel, [id*="detail"]');
        return {
            found: !!detail,
            height: detail ? detail.offsetHeight : -1,
            display: detail ? getComputedStyle(detail).display : 'N/A'
        };
    }""")
    print(f"Mobile detail: {result}")
    # height == 0 con display != 'none' → openDetail hace return prematuro en lite-mode

    browser.close()
```

**Síntomas que solo aparecen en móvil:**
- `openDetail()` hace `return` prematuro en lite-mode → detail nunca abre
- Modal con `position:fixed` invisible dentro de `overflow:auto` del padre
- Chip-nav desbordado horizontalmente, botones fuera del viewport

Output goes to `./verify_out/` by default (`report.json`, `console.log`, `screenshot.png`);
override with `--out`.

## Decision Tree: Choosing Your Approach

```
User task → Is it static HTML?
    ├─ Yes → Read HTML file directly to identify selectors
    │         ├─ Success → Write Playwright script using selectors
    │         │            (or run: python scripts/verify_runtime.py ./file.html)
    │         └─ Fails/Incomplete → Treat as dynamic (below)
    │
    └─ No (dynamic webapp) → Is the server already running?
        ├─ No → Run: python scripts/with_server.py --help
        │        Then use the helper + write simplified Playwright script
        │
        └─ Yes → Reconnaissance-then-action:
            1. Navigate and wait for networkidle
            2. Take screenshot or inspect DOM
            3. Identify selectors from rendered state
            4. Execute actions with discovered selectors
```

## Example: Using with_server.py

To start a server, run `--help` first, then use the helper:

**Single server:**
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

**Multiple servers (e.g., backend + frontend):**
```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

**Compose with verify_runtime.py** (server managed automatically, then verify):
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 \
  -- python scripts/verify_runtime.py http://localhost:5173 --click-buttons
```

To create an automation script, include only Playwright logic (servers are managed automatically):
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True) # Always launch chromium in headless mode
    page = browser.new_page()
    page.goto('http://localhost:5173') # Server already running and ready
    page.wait_for_load_state('networkidle') # CRITICAL: Wait for JS to execute
    # ... your automation logic
    browser.close()
```

## Reconnaissance-Then-Action Pattern

1. **Inspect rendered DOM**:
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   page.locator('button').all()
   ```

2. **Identify selectors** from inspection results

3. **Execute actions** using discovered selectors

## Common Pitfall

❌ **Don't** inspect the DOM before waiting for `networkidle` on dynamic apps
✅ **Do** wait for `page.wait_for_load_state('networkidle')` before inspection

## Best Practices

- **Use bundled scripts as black boxes** - To accomplish a task, consider whether one of
  the scripts available in `scripts/` can help. Use `--help` to see usage, then invoke directly.
- Use `sync_playwright()` for synchronous scripts
- Always close the browser when done
- Use descriptive selectors: `text=`, `role=`, CSS selectors, or IDs
- Add appropriate waits: `page.wait_for_selector()` or `page.wait_for_timeout()`
- **Cloud/headless envs:** write outputs to the working directory, NOT `/mnt/user-data/...`.
  Chromium is preinstalled; always launch `headless=True`.

## Reference Files

- **references/INTEGRACION_SKILLS.md** - Exact hand-off points with `debug-html-monolito`
  and `clonar-proyecto`, and how to chain the runtime step automatically.
- **examples/** - Examples showing common patterns:
  - `element_discovery.py` - Discovering buttons, links, and inputs on a page
  - `static_html_automation.py` - Using file:// URLs for local HTML
  - `console_logging.py` - Capturing console logs during automation

---

## Configuraciones por tipo de proyecto

La mayoría de proyectos vanilla son `file://` directo — sin servidor. Solo los proyectos con bundler (Vite, Webpack) o con backend local (Supabase CLI, Firebase Emulator) necesitan `with_server.py`.

## Decision Tree: Choosing Your Approach

```
User task → Is it static HTML?
    ├─ Yes → Read HTML file directly to identify selectors
    │         ├─ Success → Write Playwright script using selectors
    │         │            (or run: python scripts/verify_runtime.py ./file.html)
    │         └─ Fails/Incomplete → Treat as dynamic (below)
    │
    └─ No (dynamic webapp) → Is the server already running?
        ├─ No → Run: python scripts/with_server.py --help
        │        Then use the helper + write simplified Playwright script
        │
        └─ Yes → Reconnaissance-then-action:
            1. Navigate and wait for networkidle
            2. Take screenshot or inspect DOM
            3. Identify selectors from rendered state
            4. Execute actions with discovered selectors
```

## Example: Using with_server.py

To start a server, run `--help` first, then use the helper:

**Single server:**
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

**Multiple servers (e.g., backend + frontend):**
```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

**Compose with verify_runtime.py** (server managed automatically, then verify):
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 \
  -- python scripts/verify_runtime.py http://localhost:5173 --click-buttons
```

To create an automation script, include only Playwright logic (servers are managed automatically):
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True) # Always launch chromium in headless mode
    page = browser.new_page()
    page.goto('http://localhost:5173') # Server already running and ready
    page.wait_for_load_state('networkidle') # CRITICAL: Wait for JS to execute
    # ... your automation logic
    browser.close()
```

## Reconnaissance-Then-Action Pattern

1. **Inspect rendered DOM**:
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   page.locator('button').all()
   ```

2. **Identify selectors** from inspection results

3. **Execute actions** using discovered selectors

## Common Pitfall

❌ **Don't** inspect the DOM before waiting for `networkidle` on dynamic apps
✅ **Do** wait for `page.wait_for_load_state('networkidle')` before inspection

## Best Practices

- **Use bundled scripts as black boxes** - To accomplish a task, consider whether one of
  the scripts available in `scripts/` can help. Use `--help` to see usage, then invoke directly.
- Use `sync_playwright()` for synchronous scripts
- Always close the browser when done
- Use descriptive selectors: `text=`, `role=`, CSS selectors, or IDs
- Add appropriate waits: `page.wait_for_selector()` or `page.wait_for_timeout()`
- **Cloud/headless envs:** write outputs to the working directory, NOT `/mnt/user-data/...`.
  Chromium is preinstalled; always launch `headless=True`.

## Reference Files

- **references/INTEGRACION_SKILLS.md** - Exact hand-off points with `debug-html-monolito`
  and `clonar-proyecto`, and how to chain the runtime step automatically.
- **examples/** - Examples showing common patterns:
  - `element_discovery.py` - Discovering buttons, links, and inputs on a page
  - `static_html_automation.py` - Using file:// URLs for local HTML
  - `console_logging.py` - Capturing console logs during automation

---

## Configuraciones por tipo de proyecto

La mayoría de proyectos vanilla son `file://` directo — sin servidor. Solo los proyectos con bundler (Vite, Webpack) o con backend local (Supabase CLI, Firebase Emulator) necesitan `with_server.py`.

### Monolito HTML estático (portales, dashboards, herramientas comerciales)

```bash
# Sin servidor — file:// directo:
python scripts/verify_runtime.py ./index.html --click-buttons

# Con check de clases CSS reservadas (crítico si el monolito tiene muchas clases con display:none):
python scripts/verify_runtime.py ./index.html \
  --classes ".ctx-body,.sub-panel,.mod-body,.script-full,.txt-acc-body"
```

**Checks adicionales recomendados antes del screenshot:**
- Verificar `h.count('</script>') == 1` (boundary JS/HTML)
- Verificar balance de divs fuera del contenedor principal
- Verificar que no hay base64 en el bloque `<style>`

### Portal multi-HTML (academias, portales con múltiples páginas)

```bash
# Testear index principal:
python scripts/verify_runtime.py ./index.html --click-buttons

# Testear una subpágina específica:
python scripts/verify_runtime.py ./modulo1/index.html --click-buttons

# Script de test transversal (todos los módulos):
for f in */index.html; do
  echo "--- $f ---"
  python scripts/verify_runtime.py "$f" 2>&1 | tail -5
done
```

**Checks específicos para portales multi-HTML:**
- Verificar que el array de módulos en el root `index.html` no tiene doble brace
- Verificar que cada subpágina carga su shared engine correctamente
- **Dos anchos siempre (JoGaSan, 25-sep)**: 390×844 Y 1400×900, con captura de
  cada uno y mirándola. Cuenta las filas de `.t3-mapa-paso` visibles (`top`
  distintos) y si `.t3-mapa` y `.t3-tabs` se ven a la vez. 36 módulos de 3º B/4º B
  llevaban el mapa en columna + pestañas duplicadas en escritorio: 0 errores JS y
  bien en móvil, así que ninguna prueba lo vio (síntoma 64 de clonar-academia).
- `pkill -f <script>` mata también tu propio shell si la línea lo menciona: usa el PID.

### App con Firebase (monolito con backend Firestore/Auth)

```bash
# En local con file://, Firebase funciona si la apiKey está directa en HTML:
python scripts/verify_runtime.py ./index.html --click-buttons

# Para Google Auth: necesita Netlify o servidor HTTPS real (no funciona en file://)
# Testear el deploy en Netlify:
python scripts/verify_runtime.py https://mi-app.netlify.app --wait networkidle
```

**Checks específicos Firebase:**
- Verificar que Firebase init es síncrona (apiKey directa, no fetch)
- Si hay Google Auth: verificar COOP header en Netlify → ver `clonar-proyecto/references/bugs-netlify-firebase.md`

---

## Snippets críticos — falsos positivos conocidos

### Modal: medir el interior, no el overlay

```python
# MAL — el overlay fullscreen siempre tiene height > 0:
height = page.evaluate("document.querySelector('#res-modal').offsetHeight")

# BIEN — medir el modal interior:
height = page.evaluate("document.querySelector('#res-modal .modal').offsetHeight")
# Si height == 0 → el modal existe pero no está visible
```

### Tab invisible vs tab fuera del DOM principal

```python
# Un tab puede tener height > 0 pero estar fuera del contenedor → el usuario no lo ve
result = page.evaluate("""() => {
  var tab = document.querySelector('#mi-tab');
  var main = document.querySelector('main, #app, .app-section');
  return {
    height: tab ? tab.offsetHeight : -1,
    estaEnMain: main ? main.contains(tab) : false
  };
}""")
# estaEnMain debe ser true — si es false, hay un div huérfano
```

### Contraste WCAG AA a nivel de píxel

```python
# Verificar ratio de contraste de un elemento crítico:
result = page.evaluate("""() => {
  var el = document.querySelector('.mi-texto-importante');
  var style = getComputedStyle(el);
  return {
    color: style.color,
    background: style.backgroundColor,
    fontSize: style.fontSize
  };
}""")
# Usar los valores para calcular ratio manualmente o con wcag-contrast npm
```

---

## Verificar que la ACCIÓN del usuario deja huella (sesión v224, JoGaSan Academy)

Cargar la página y no ver errores **no prueba nada**. Los fallos más caros
aparecen al interactuar: el alumno respondió 18 preguntas y no se guardó nada,
porque una línea lanzaba excepción por encima de la llamada que registraba.

### El patrón: espiar la función que debe llamarse

```javascript
await page.evaluate(() => {
  window.__reg = 0;
  const orig = AcademiaLogros.registrarQuiz;              // la fn que DEBE llegar a llamarse
  AcademiaLogros.registrarQuiz = function () {
    window.__reg++;
    return orig && orig.apply(this, arguments);
  };
});
// …completar el flujo de verdad…
const veces = await page.evaluate(() => window.__reg);    // 0 = el esfuerzo se perdió
```

Sirve para cualquier "esto debería guardarse": analítica, envío de formulario,
pago, sincronización.

### Cinco detalles sin los que la prueba miente

1. **Sesión de usuario antes de que corra ningún script.** Mucho código arranca
   con `if (!usuario) return;`: sin sesión ni siquiera instala lo que quieres
   probar. Va en `addInitScript`, no en `evaluate` tras el `goto`.
   ```javascript
   await page.addInitScript(() => {
     sessionStorage.setItem('sesion', JSON.stringify({ usuario: 'test' }));
   });
   ```
2. **`waitUntil: 'domcontentloaded'`, nunca `'load'`.** Si la página pide
   fuentes o scripts externos y no hay red, `load` no dispara jamás y el test
   muere por timeout haciendo creer que la página está rota.
   Corta además lo externo: `page.route('**://**', r => /127\.0\.0\.1/.test(r.request().url()) ? r.continue() : r.abort())`.
3. **Pulsar de UNA en UNA.** Los cuestionarios van pregunta a pregunta. Pulsar
   todas las opciones a la vez rompe el flujo y da un falso "no registra".
   Pulsa la primera disponible, espera ~200 ms, repite.
4. **Elementos ocultos no se pueden pulsar.** `offsetParent === null` los
   descarta. Si el panel no está activo, fuerza su visibilidad antes de medir o
   pulsar — o navega de verdad hasta él.
5. **Cubre TODAS las convenciones de marcado.** En un proyecto con años encima
   conviven varias: aquí `.qe-opt`, `.opt`, `.t3-opt`, `.mq-opt`, `.opcion`.
   Un selector incompleto reporta "sin opciones" en 68 de 94 módulos y parece
   que el test funciona.

### Grupo de control: obligatorio

Antes de dar por bueno un hallazgo **o un arreglo**, ejecuta el mismo test
contra la versión anterior del archivo, intercambiándolo en disco:

```bash
cp fichero.js /tmp/nuevo.js && cp /tmp/antes.js fichero.js
node test.js            # CONTROL
cp /tmp/nuevo.js fichero.js
node test.js            # DESPUÉS
```

En una sola sesión esto evitó tres conclusiones falsas: dos veces el test daba
"roto" y el control demostró que ya estaba así antes (no lo había causado el
cambio), y una tercera vez el roto **era el test**. Sin control habría reportado
regresiones inexistentes y me habría perdido las reales.

### Barrido estático que complementa: referencias a ids que no existen

Rápido y sin navegador. Caza el patrón que más daño hace cuando se clonan
plantillas y el HTML se reorganiza:

```javascript
// getElementById('X').loQueSea  donde id="X" no aparece en el HTML
[...html.matchAll(/document\.getElementById\('([^']+)'\)\.(addEventListener|innerHTML|classList|style|textContent)/g)]
  .filter(m => !new RegExp('id="' + m[1] + '"').test(html));
```

⚠️ Da falsos positivos con elementos creados en tiempo de ejecución (el id va
dentro de un `innerHTML`). Verifica antes de tocar: en una revisión, 16 de 31
coincidencias eran bugs reales y el resto, elementos dinámicos.

## Baseline + diff visual para editar monolitos sin romper nada (Fase 4)

Cuando insertas contenido (p.ej. una figura SVG) en un HTML monolítico hecho a
mano, el peligro es la **regresión silenciosa**: un `</div>` de más, un `id`
duplicado, un chunk que deja de avanzar. La defensa es **fotografiar antes y
comparar después**. Dos scripts del repo lo automatizan (protocolo completo en
`PLAN-REVISION-FASE4-VISUAL.md`):

```bash
node scripts/baseline-visual.js [academia]   # N0: guarda .baseline/ (screenshots + huella + consola)
# … editas …
node scripts/diff-visual.js academia N        # N2: compara contra el baseline; exit 1 si hay regresión
```

`diff-visual` da **veredicto de FALLO** solo ante: error de consola NUEVO,
un conteo estructural que BAJA o un `id` que DESAPARECE, overflow horizontal
nuevo, o cambio en la franja superior fija. Subidas de `svg`/`figure` son
esperadas (la figura). La compuerta por módulo antes de commitear: N1 estático
(`git diff` un bloque contiguo + `validar-dom-huerfano.js` 0) → N2 diff-visual →
N3 `probar-flujo-alumno.js` (el quiz sigue registrando) → N4 usabilidad → N5
`validar-academias.js` 0 errores + grupo de control.

### Cuatro trampas de entorno (resueltas, para no repetirlas)

1. **`require('playwright')` a secas NO resuelve la global** en este entorno.
   Los scripts del repo que la usan (`probar-flujo-alumno.js`,
   `auditar-modulos-navegador.js`) fallan con "Falta playwright". Solución:
   correr con `NODE_PATH=/opt/node22/lib/node_modules node scripts/...`. NO
   instales playwright local a lo loco: la versión de npm puede pedir un build
   de navegador (p.ej. 1243) que no está en `/opt/pw-browsers` (que tiene 1194)
   → `Executable doesn't exist`. La **global casa con los navegadores**; úsala.
2. **`probar-flujo-alumno.js` sirve por HTTP, no `file://`.** Antes de correrlo:
   `python3 -m http.server 8899 &` en la raíz del repo (BASE por defecto
   `http://127.0.0.1:8899`). Sin servidor: `net::ERR_CONNECTION_REFUSED`.
3. **Diff de página COMPLETA = falsos positivos.** Añadir una figura cambia la
   altura y todo lo de debajo se desplaza → un pixel-diff full-page lo marca
   todo. Compara solo señales estables: consola, huella (conteos + ids) y un
   **pixel-diff de la franja superior fija** (nav/hero, que ninguna figura
   toca). Los PNG completos se guardan para ojo humano.
4. **Ids volátiles rompen el diff de ids.** Elementos con id de timestamp
   (`med-bomb-1789286599056`) cambian en cada carga → salen como "id
   desaparecido". Normaliza las secuencias de 6+ dígitos a `#` en ambos lados
   (`id.replace(/\d{6,}/g,'#')`) antes de comparar.
---

## Ejecución en el entorno remoto (Claude Code en la nube) — mecánicas que tropiezan

Aprendido lanzando Playwright aquí (sesión v234). Lo que falla de formas poco
obvias:

### 1. Usa el binario `headless_shell`, NO el `chrome` normal
El Chromium empaquetado quitó el *headless viejo*; lanzar `chrome` con
`headless:true` peta con **"Old Headless mode has been removed from the Chrome
binary"** y el contexto se cierra. Apunta al shell independiente:
```js
const EXE = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell';
chromium.launch({ executablePath: EXE, headless: true, args:['--no-sandbox'] });
```
(Si el proyecto documenta un Playwright global —p.ej. `/opt/node22/lib/node_modules`
con `NODE_PATH`—, úsalo; si no, `npm i playwright-core` —ligero, ~1 paquete— en el
scratchpad y apunta al `headless_shell` ya presente. No hace falta `playwright install`.)

### 2. Corta la red externa o la página se cuelga
Las fuentes/CDN externas (Supabase, Google Fonts) quedan colgadas tras el proxy y
`waitUntil:'load'` nunca dispara. Usa `domcontentloaded` y aborta todo lo que no
sea localhost:
```js
await page.route('**://**', r => /127\.0\.0\.1/.test(r.request().url()) ? r.continue() : r.abort());
await page.goto(URL, { waitUntil: 'domcontentloaded' });
```

### 3. Siembra la sesión de alumno o el código arranca con `if(!alumno) return`
Muchos módulos/índices de JoGaSan no instalan nada (barras, puertas de lectura)
si no hay alumno. Siémbralo en `addInitScript` ANTES de navegar:
```js
await page.addInitScript(() => {
  sessionStorage.setItem('academia_sesion', JSON.stringify({ sesion_id:'t', alumno:'tester', inicio:new Date().toISOString(), modulos:{} }));
  localStorage.setItem('academia_ultimo_alumno', 'tester');
});
```
Para probar la zona de barras con progreso, stubea `AcademiaLogros.obtenerHistorial`
con un historial falso y dispara `window.dispatchEvent(new Event('academia:sesion-actualizada'))`.

### 4. Antes del navegador: simulación DOM en Node (más rápida y determinista)
Para verificar **lógica de render pura** (p.ej. `AcademiaLogrosUI.pintar`), no
hace falta navegador. Un stub mínimo de `document.getElementById` que capture
`innerHTML`/`style`, cargar los `.js` reales con `eval`, llamar a la función con
datos falsos y leer el nodo. Caza en segundos si el HTML que produce es el
esperado; deja para Playwright lo que depende de CSS/layout/eventos reales.
Regla aprendida: **render OK en Node ≠ el dato llega** — si las barras salen
siempre vacías, el fallo suele estar en la ATRIBUCIÓN del dato (aguas arriba),
no en el render.

---

## 🆕 Lecciones del 23-24 sep (familias 3º B / 4º B, cuadernos) — lo que hizo mentir a los tests

1. **Bloquea el service worker**: `browser.newContext({ serviceWorkers: 'block' })`.
   Con el SW activo, `sw.js` recarga la página a mitad del test (rescate de caché)
   y el `evaluate` corre sobre un documento que ya no existe.
2. **Chromium en la nube**: hoy funciona `chromium.launch({ executablePath: '/opt/pw-browsers/chromium' })`
   con `require('playwright')` y `NODE_PATH=$(npm root -g)`. Si da "Old Headless
   mode has been removed", usa el `headless_shell` (sección anterior).
3. **Antes del navegador, compila cada `<script>` inline** (`new vm.Script(código)`
   en Node). Un paréntesis de menos anuló durante días 11 módulos enteros sin
   ningún aviso visible salvo "Unexpected token" en consola. Es barato y va primero.
4. **Espía el CONTENIDO de la llamada, no solo que ocurra.** Tres bugs reales solo
   se vieron así: `registrarQuiz(pct, total, clave)` (argumentos desordenados),
   `registrarActividad(clave_modulo, …)` (partía la sesión) y la caja de errores
   con la opción equivocada. Comprueba: clave, aciertos/total esperados,
   `opts[ans] === texto de la opción correcta`, y **nº de veces** (una actividad
   debe registrarse UNA vez al terminar, no tras cada respuesta).
5. **Haz lo que hace el alumno, incluido fallar**: responde con una incorrecta y el
   resto bien, termina, y exige la nota exacta (`N-1 / N`). Solo "cargar y 0
   errores" no habría cazado nada de lo anterior.
6. **Mira el texto de las opciones**: un "✓" o "(correcta)" en el texto del botón
   chiva la respuesta y ningún test funcional lo ve. Cuenta opciones con `/✓/`.
7. **Stubs con la forma REAL de los datos.** `AcademiaLogrosUI.pintar` necesita
   `sesiones_totales` y `historial.historial[]` con `modulos` como array de claves;
   con otra forma "sale vacío" y parece un bug de la app. Copia la forma de lo que
   devuelve la función real (o léela del código) antes de concluir.
8. **Grupo de control en el código de `main` sin tocar tu checkout**:
   `git worktree add <scratch>/main origin/main`, sírvelo en otro puerto y pasa el
   MISMO test (y el MISMO validador copiado). Así la cifra "antes → después" es honesta.
9. **Reemplazos masivos con `assert`**: el test de navegador cazó un helper que no
   se había insertado en 11 de 18 ficheros porque el `replace` no encontró el texto
   (`var x = {}` con espacios). Afirma siempre el nº de coincidencias.

## 🆕 Lecciones del 24-sep (tarde) — conteo, Rincón de Santi, ficha de medallas

10. **Multitoque**: repite el clic en la respuesta correcta y en «Comprobar» (2 y 3
    veces seguidas, sin esperar). Exige `correctas <= total`, el nº de preguntas
    vistas y **una sola** pantalla de resultado. Así salieron el 12/6 de Mates 3º y
    el −37 de Santi (síntoma 57 de `clonar-academia`).
11. **Voz simulada**: `addInitScript` con un `speechSynthesis` falso cuyo `onend`
    salta a 1 s por frase. Chromium sin voces termina las narraciones en
    milisegundos y los fallos de turnos/cortes no se ven.
12. **Supabase simulado**: `addInitScript` que define `window.supabase.createClient`
    con una BD en memoria (compartida entre páginas si pruebas profe ↔ alumno; ver
    `scripts/lib/supabase-simulado.js`). Casos obligatorios de sincronización:
    dispositivo borrado → recupera; nube con más → fusiona por máximo; **lectura
    fallida → 0 escrituras**. Ojo: `supabase-js` no lanza en fallo de red, devuelve
    `{error}`; el stub debe devolverlo igual.
13. **Botón tapado**: `document.elementFromPoint(x, y)` en el centro de cada botón
    crítico (a 375-400 px). Chispa y «¿Algo raro?» tapaban las flechas del laberinto
    aunque eran visibles y clicables por selector.
14. **Recorre TODO lo que el alumno pulsa**: la ficha de medallas se validó pulsando
    una a una las 237 medallas de 33 academias; el muestreo no la habría cazado.
15. **Servidor local**: lánzalo en segundo plano y comprueba con `curl -sf` antes de
    cada lote; `python3 -m http.server` se cae entre llamadas y parece un fallo de la app.
16. **Generadores aleatorios**: además del navegador, miles de partidas en Node
    (opciones únicas, respuesta presente, género/número) — 50.400 en la Fase 4.

## 🆕 Lecciones del 25-26 sep — sesiones, sincronización y puertas

17. **Dos dispositivos**: dos contextos de navegador con la misma «nube» simulada
    (se copia de uno a otro). Lo que hace el alumno en A debe verse en B y en el
    panel del profe (`scripts/probar-sync.js`, `probar-panel-profe.js`).
18. **Comprueba la FILA que llega a `sesiones`**, no solo que se llamó a guardar:
    alumno, `academia_id`, clave del módulo. Tres escenarios: sesión de portada,
    pestaña sin sesión y sesión viva de otra academia (`probar-sesiones.js`).
19. **Reloj simulado** para lo que depende del tiempo (tiempo activo, rachas,
    «20 h después»): `page.clock` o un `Date` falso en `addInitScript`.
20. **Siembra la puerta de lectura con su forma real**: `lt_cache_v1` va por alumno
    en minúsculas y por clave de módulo
    (`{"alumno prueba":{"mat4b_modulo6":{"segundos":180,"scrollOk":true}}}`). Con
    otra forma la puerta sigue cerrada y el test «ve» un botón roto que no lo está.
    La puerta cierra TODOS los ejercicios, no solo el quiz.
21. **Las preferencias del sistema también se prueban**: `page.emulateMedia({ reducedMotion: 'reduce' })`
    y, con Playwright reciente, `contrast: 'more'`.
22. **Diagnóstico con datos reales primero**: cruza `sesiones` con las tablas ligeras
    (`lecturas_teoria`, `medallas_alumno`, `estado_alumno`) del mismo alumno y hora
    antes de escribir un test; el test reproduce lo que dicen los datos.

## 🆕 Lecciones del 1-3 oct — puerta familiar, Rincón, bilingüe, juegos y TDAH

23. **Puerta familiar (1-oct):** `config.js` oculta la página y pide usuario y contraseña salvo en `localhost`, `127.0.0.1` y `file:`. Sirve SIEMPRE por `127.0.0.1`
    (`python3 -m http.server 8765 &`, y `curl -sf` antes de cada lote). Para probar la puerta misma, sirve por `127.0.0.2` con una contraseña de prueba que calcule la misma
    huella, o siembra `localStorage.jg_puerta`. Nunca pegues la contraseña real en un script ni en un informe.
24. **El elemento que pulsa el alumno, no el que existe:** en las academias de 3º la fila `.t3-tabs` está oculta (`display:none`) y se navega por `.t3-mapa-pasos`; la pestaña
    «💪 Practica» de Mates 3º estuvo días donde nadie podía abrirla porque las pruebas la abrían por código. Pulsa el botón visible (`isVisible()` + `elementFromPoint`) y,
    en Lengua 3º, `irAPanel('practica')`, no `data-tab`.
25. **Títulos por sílabas (Rincón):** `textContent` lleva «·» y `hasText` ya no encuentra «Na·tu·ra·le·za». Usa `scripts/lib/rincon-tocar.js` o quita los puntos al comparar.
    Inspecciona con `Peque.estado()` y `Peque.trazaActual()`; traza de verdad (vocales, sílabas, nombre; 320/390/1400) y comprueba que un garabato fuera de la letra no cuenta.
26. **Contraste con el panel abierto y TODOS los controles:** tras tocar colores, mide también los botones de respuesta de la práctica (`.pd-opt`, `.pd-signo`), no solo la cifra y
    «Comprobar» (en tema oscuro sin `--card2` valían 1,04:1). Compara elemento a elemento con el barrido anterior: los arreglos de contraste también rompen contraste.
27. **`getComputedStyle(document.body).overflowY` debe ser `visible`** (nunca `overflow` ≠ `visible` a la vez en `html` y `body`: se traga la rueda del ratón).
28. **Anchos:** 320, 390, 820 y 1400. Mide scroll horizontal (`scrollWidth > innerWidth`), texto de figuras ≥ 12 px reales a 390 (`node scripts/auditar-svg.js --navegador`), objetivos
    táctiles ≥ 44-48 px y que Medi, 🐛 o el chip no tapen el botón (`elementFromPoint`).
29. **Un test que «ve» lo que el alumno no ve:** `probar-flujo-alumno.js` forzaba el panel del quiz y tapó que en Lengua 3º m1/m4/m5 el quiz salía vacío (`iniciarQuiz()` sin
    llamar). El piloto ahora marca «QUIZ VACÍO». Moraleja: si el test «ayuda» a la app (fuerza paneles, llama a funciones), anótalo en el informe.
30. **Pruebas pesadas en paralelo se cuelgan o matan el servidor:** relanza el `http.server` y repite; y un agente que escribe en el árbol invalida una prueba en curso (espera a que acaben).
    `probar-sync.js` pasos 8-10 son inestables incluso en `main`: comprueba el grupo de control antes de culpar a tu cambio.
31. **Generadores y regeneración:** `node scripts/generar-1eso.js --comprobar` (y `--curso 4pri`, `--curso 1eso`) tiene que quedar limpio tras fusionar; `git grep -n "<<<<<<<"` antes de commitear.
32. **Bilingüe, qué probar:** formato `.bi`/`.jm-bi`, `qEs` bajo el enunciado, sin scroll horizontal a 390 px (`probar-bilingue.js`); y la **ausencia** de traducción donde resuelve el ejercicio:
    ninguna traducción en el hueco ni en las opciones antes de responder, y tras responder (acierto o fallo) sale la frase completa (`probar-hueco-sin-traduccion.js`). Cuenta fugas con datos, no a ojo.
33. **Juegos con azar:** miles de partidas en Node (la trampa nunca es una forma válida, la buena está presente, ningún tipo de trampa pasa del 25-30 %, dos partidas seguidas casi no repiten),
    más una partida real en navegador con multitoque. Scripts: `probar-juegos-nuevos.js`, `probar-ruleta.js`, `probar-juegos-regresion.js`, `probar-juegos-vocab-nuevos.js <carpeta> <prefijo>`.
34. **Pruebas «de pasillo» ya hechas, no las reescribas:** `probar-paso-a-paso.js` (94 módulos), `probar-apuntes.js` (etiqueta en tarjeta y título), `probar-tarjetas-iconos.js`, `probar-figura-zoom.js`,
    `probar-sesiones.js`/`probar-sesiones-limite.js`, `probar-panel-profe.js`, `probar-visibilidad-curso.js`, `probar-tareas.js`, `probar-rincon-{juegos,leer,tienda,voz}.js`.

### Batería mínima antes de subir (CLAUDE.md), en orden
```
node scripts/validar-academias.js          # y el MISMO validador sobre un worktree de origin/main: no puede haber más errores
node scripts/validar-medallas.js           # si tocaste medallas o módulos
node scripts/sincronizar-version.js --comprobar   # si subiste CACHE_VERSION
node --check <js tocado>                   # y los <script> inline extraídos (new vm.Script)
node scripts/generar-1eso.js --comprobar   # si tocaste material/ o el generador
node scripts/probar-flujo-alumno.js <academia> ; (+ el probar-* del motor que tocaste)   # navegador, sesión sembrada, serviceWorkers:'block'
```
En el resumen final di qué skills usaste, qué pruebas pasaron y **qué no pudiste probar** (voz real de la tablet, producción, Supabase real).

## 🆕 Lecciones del 3-11 oct — pantallas, auditoría /ux, invitado y exámenes

35. **Mide la altura de lo que lee el alumno, avanzando como él:** `node scripts/auditar-pantallas.js <ruta|academia|--cambiados>` (390×844; ninguna pantalla de teoría > 1,9 ventanas, **un solo chunk visible a la vez**;
    excepciones en `scripts/pantallas-permitidas.json`) y `node scripts/probar-pantallas.js` si tocas `nav-chunks.js`. Cada chunk aislado es corto: el muro sale de que los chunks se **acumulan**, y solo se ve avanzando.
    Mide también dónde empieza la teoría (`getBoundingClientRect().top` del primer bloque < ~300 px a 390×844).
36. **Barrido de viewports:** 320, 344, 390, 768, 844×390 y 1280 (más Fold/iPad si aplica). `JG_VIEWPORT=390x844 node scripts/probar-flujo-alumno.js <academia>` repite el flujo del alumno en móvil. Siempre **mide → arregla → vuelve a medir
    → compara con `main`** (worktree) y cita cifras («606 → 280 px»), no impresiones.
37. **Contraste sobre degradados o imágenes: por píxeles.** Pon `color`/`text-shadow` del texto (y de sus hijos) en transparente, `page.screenshot({clip})` de su caja y compara con los percentiles 5 y 95 de luminancia
    (peor caso). Un medidor que se salta `linear-gradient` da «0 fallos» con el texto en 2,7:1. Mira los recortes antes de arreglar: hay falsos positivos (`<strong>` multilínea, texto con `text-stroke`).
38. **Zona táctil real = caja + `::after`.** `medi-badge-chat` mide 30×30 pero su `::after{inset:-8px}` da 46×46: no es un fallo. Mide solapes entre `position:fixed` (píldora del alumno, barra de progreso, Medi, 🐛) como rectángulos, en cada módulo y a 3 anchos.
39. **Aislamiento y caducidad:** para modos con filtro por URL (puerta familiar, invitado) prueba rutas permitidas y prohibidas, caducado, reiniciar y que las listas del profe no muestran al invitado (`probar-invitado.js`).
    El `supabase-simulado.js` ya respeta `onConflict` y `delete().eq()`; si una tabla tiene clave compuesta, decláralo ahí.
40. **Pruebas que se pisan a sí mismas:** `probar-sync.js` fallaba porque la primera carga de `abrir()` subía una copia local que pisaba la nube del paso 6b; estable (5/5) al arreglar el orden. Si un paso depende del anterior,
    reinicia el estado entre pasos y compara con `main` antes de culpar al cambio.
41. **Exámenes y apps con generadores:** doble clic en la respuesta (cuenta una vez), intento perfecto = 10, intento a cero = 0 sin negativos ni pisar la mejor, y miles de casos en Node para el generador
    (`probar-operaciones-gen.js`: 246 939). Si una cuenta nueva no está en la lista de dibujo (`LINEA_CUADERNO`/columnas), la prueba tiene que fallar, no caer a texto.
42. **Sesión sin red:** WebFetch/curl bloqueados → no des por buenos los enlaces; márcalos «sin comprobar» y deja el script de comprobación para cuando haya red. Playwright sigue valiendo contra `127.0.0.1`.
