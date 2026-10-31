# Encaje de `webapp-testing` con `debug-html-monolito` y `clonar-proyecto`

> Objetivo: que la verificación **runtime** (ejecutar la página de verdad en el navegador)
> se active en el punto exacto donde las skills estáticas se quedan cortas, y que el
> encadenamiento sea automático, no manual.

## Idea en una frase

`debug-html-monolito` y `clonar-proyecto` son **estáticas**: leen el HTML, cuentan divs,
validan JS con `node --check`. `webapp-testing` es la capa que **ejecuta** la página y ve
lo que el estático no puede: errores de consola, excepciones al cargar, elementos
invisibles por CSS, y botones que revientan al pulsarlos.

Regla de oro: **el estático valida el CÓDIGO; el runtime valida la EJECUCIÓN. Se usan en
ese orden, siempre.**

```
   clonar-proyecto ──► debug-html-monolito ──► webapp-testing ──► (feedback) ──┐
   (construye)          (checklist estático)     (verify_runtime)               │
        ▲───────────────────────────────────────────────────────────────────────┘
```

---

## Herramientas de este paquete

| Script | Para qué | Cuándo |
|---|---|---|
| `scripts/verify_runtime.py` | Ejecuta la página y reporta errores de consola, excepciones, colisiones CSS, smoke test de clicks y screenshot. Sale con código ≠0 si hay problemas. | Tras el checklist estático, y en el smoke test post-deploy. |
| `scripts/with_server.py` | Levanta servidor(es), espera a que el puerto abra, ejecuta tu comando y apaga todo al terminar. | Solo para apps **dinámicas** (npm run dev, vite, Supabase local). Para monolitos HTML **no hace falta** — se usa `file://`. |

Ambos son **caja negra**: `python scripts/<x>.py --help` y a usar. No hace falta leer el código.

---

## Encaje con `debug-html-monolito`

Esta skill es 100% estática y su tabla de síntomas (§5) lista bugs que **solo se ven en
runtime**. Ahí es donde entra `verify_runtime.py`.

### Punto de inserción 1 — tras "Verificación obligatoria antes de guardar" (§3)

Hoy `verify_and_save()` termina en `node --check` + balance de divs. Añadir un paso
runtime **después de guardar**:

```bash
# Tras verify_and_save() → confirmar que la página ejecuta sin errores
python scripts/verify_runtime.py ./index.html --click-buttons
# Exit 0 = limpio de verdad. Exit 1 = revisar report.json
```

Esto convierte el "probablemente OK" estático en "verificado OK".

### Punto de inserción 2 — síntomas de la tabla §5 que ahora tienen check ejecutable

| Síntoma (§5) | Antes (solo inferencia estática) | Ahora (runtime) |
|---|---|---|
| Función "no definida" en consola | contar `</script>`, boundary | `verify_runtime` → sección EXCEPCIONES lo captura literalmente |
| "Cannot set properties of null" en quiz | buscar `.textContent` en div con span | pulsar el botón del quiz con `--click` y ver la excepción real |
| Overlay no aparece (`offsetHeight=0`) | — | `--classes ".overlay,.treeOverlay"` → sección COLISIONES CSS |
| Botón dispara múltiples funciones | balance de divs | `--click-buttons` → detecta el crash o comportamiento anómalo |
| Elemento en DOM pero invisible | §10 define `page.evaluate` **sin runner** | `verify_runtime` **es** ese runner |

### Punto de inserción 3 — §10 (colisión de clases CSS)

La §10 ya trae el snippet `page.evaluate` de `offsetHeight`, pero la skill no ejecuta
Playwright. Sustituir ese snippet suelto por:

```bash
# Al insertar HTML nuevo con clases que podrían colisionar (ctx-body, sub-panel, mod-body…)
python scripts/verify_runtime.py ./index.html --classes ".ctx-body,.sub-panel,.mod-body"
```

Detecta tanto el caso `display:none` heredado (clase reservada) como `offsetHeight=0`
con `display:block`.

---

## Encaje con `clonar-proyecto`

### Punto de inserción 1 — F1C, detección de SPA

La skill avisa: `web_fetch` en una SPA devuelve `<div id="root"></div>` vacío. La solución
que pide ("ir al protocolo de captura") es exactamente lo que hace Playwright:

```bash
# Renderiza la SPA de verdad y saca screenshot + DOM real para el mapa de zonas
python scripts/verify_runtime.py https://la-web-externa.com --wait networkidle
# → screenshot.png para el mapa de zonas; report.json con el estado renderizado
```

### Punto de inserción 2 — Arquetipo D (§0.1b), extracción por DevTools

La extracción manual (DOM, CSS computado, variables globales) se puede automatizar con un
script Playwright arrancado vía `with_server.py` si el proyecto necesita servidor, o con
`verify_runtime.py` directamente si ya está desplegado.

### Punto de inserción 3 — F3, smoke test post-deploy (el encaje más fuerte)

El smoke test de F3 marca varios checks como `🤖 automática`. `verify_runtime.py` los
ejecuta de una sola llamada:

| Check F3 | Cubierto por |
|---|---|
| 🤖 Sin errores en consola (F12 → Console) | sección ERRORES DE CONSOLA + EXCEPCIONES |
| 👁 Flujo principal end-to-end | `--click "text=Login" --click "text=Guardar"` en orden |
| 🤖 Elemento visible / no roto | sección COLISIONES CSS |
| screenshot para revisión visual | `screenshot.png` |

```bash
# Smoke test post-deploy en una línea
python scripts/verify_runtime.py https://mi-clon.netlify.app --click-buttons --wait networkidle
```

Para apps con backend local durante el desarrollo:

```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "npm run dev"                    --port 5173 \
  -- python scripts/verify_runtime.py http://localhost:5173 --click-buttons
```

### Punto de inserción 4 — F4.6 (colisión de clases CSS al añadir contenido)

Idéntico a la §10 de debug-monolito: usar `verify_runtime.py --classes` sobre las clases
recién añadidas antes de dar por buena la sección nueva.

---

## Cómo hacer que se encadene "solo"

Añadir estas líneas al final de los checklists de cada skill para que el disparo runtime
sea el paso natural siguiente:

- En `debug-html-monolito` §3, tras `verify_and_save`:
  > **Paso runtime obligatorio:** `python scripts/verify_runtime.py <archivo>.html --click-buttons`.
  > Si exit ≠ 0, volver a la tabla §5 con el bug ya localizado en `report.json`.

- En `clonar-proyecto` F3, dentro del smoke test:
  > Ejecutar `verify_runtime.py` sobre el deploy (o vía `with_server.py` en local) antes
  > de marcar los checks 🤖 como pasados.

---

## Ajustes de entorno (importante)

- El ejemplo original `console_logging.py` escribía a `/mnt/user-data/outputs/`. En este
  entorno cloud esa ruta **no existe** — `verify_runtime.py` ya usa `./verify_out` (el
  workspace) por defecto, configurable con `--out`.
- Para **monolitos HTML** (tu caso más común: portales, academias) **no uses
  `with_server.py`** — `verify_runtime.py ./archivo.html` funciona con `file://` directo.
- Chromium se lanza siempre en `headless=True`.

---

## Resumen ejecutivo

`webapp-testing` no reemplaza nada: **rellena el único hueco** que tus skills de depurar y
clonar tenían — la ejecución real en navegador. Los dos scripts de este paquete son las
piezas que las skills ya asumían que existían (§10 y F4.6 escriben `page.evaluate` sin
runner; el SKILL.md referencia un `with_server.py` que no venía). Con esto, el ciclo
construir → validar estático → **ejecutar y verificar** → corregir queda cerrado.
