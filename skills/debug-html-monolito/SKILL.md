---
name: debug-html-monolito
description: "Protocolo de diagnóstico, auditoría y reparación de archivos HTML monolíticos grandes (un solo .html con CSS + JS embebidos: portales, argumentarios, dashboards). ACTIVA SIEMPRE QUE: HTML grande con CSS y JS inline y síntomas como pantalla en blanco, botones que no hacen nada, función no definida, layout roto, JS que se rompe al editar, overlay que no aparece, tab completamente invisible, variable JS duplicada, o bugs por edición iterativa. ACTIVAR TAMBIÉN para auditorías preventivas: \"audita el portal\", \"pasa una revisión de integridad\", \"comprueba que todo funciona\", \"da una pasada antes del deploy\". Cubre: checklist JS/HTML/CSS, referencias huérfanas, IDs faltantes, base64 en bloque de estilos, divs huérfanos fuera de contenedor, variables duplicadas, colisión CSS. Patrones extraídos de portales comerciales, academias educativas y dashboards reales.\n"
---

# Debug HTML Monolito

Protocolo para diagnosticar y reparar bugs en archivos HTML monolíticos grandes
(único .html con CSS + JS embebidos). El principio rector: **medir antes de tocar**.

---

## 1. Diagnóstico inicial obligatorio

Antes de CUALQUIER edición, ejecutar el checklist completo:

```python
import re, subprocess
from collections import Counter

with open('archivo.html', 'r', encoding='utf-8') as f:
    h = f.read()

# OJO monolitos con VARIOS <script>: coge el bloque MÁS GRANDE (la app), no el
# primero. Extraer con h.find('<script>')/h.find('</script>') analiza el primer
# bloque (a veces un helper pequeño) y te pierdes los errores del grande.
# Además hay <script>/</script> LITERALES dentro de strings (código que genera
# HTML): sus cierres deben ir escapados como <\/script> o el navegador corta el
# bloque ahí (bug real, ver sección 12).
_blocks = re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>', h, re.S)
script = max(_blocks, key=len) if _blocks else ''      # el bloque de la app
css    = h[h.find('<style>')+7:h.find('</style>')]

checks = []

# ── ESTRUCTURA GLOBAL ────────────────────────────────────────────
checks.append(("file starts <html",    h[:5] == '<html'))
checks.append(("file ends </html>",    h.rstrip()[-7:] == '</html>'))
# NO exijas "== 1": un monolito puede tener helpers + app en <script> separados,
# y <script>/</script> LITERALES dentro de strings que generan HTML. El peligro
# real es un </script> literal SIN escapar (el navegador corta el bloque ahí):
# debe escribirse <\/script>. Ver sección 12.
checks.append(("hay <script> y </script>", h.count('<script') >= 1 and h.count('</script>') >= 1))
checks.append(("<style> único",        h.count('<style>') == 1))

# ── JS SYNTAX ────────────────────────────────────────────────────
r = subprocess.run(['node', '--check'],
    input=script.encode(), capture_output=True, timeout=15)
checks.append(("JS CLEAN", r.returncode == 0))
if r.returncode != 0:
    print("JS ERROR:", r.stderr.decode()[:300])

# ── BOUNDARY JS/HTML ─────────────────────────────────────────────
KNOWN_BOUNDARY = script.rstrip()[-20:]
checks.append(("boundary no tiene HTML", '<div' not in KNOWN_BOUNDARY))

# ── DIV BALANCE ──────────────────────────────────────────────────
pre = h[h.find('<body>'):script_start - 8]
d1 = 0; neg1 = False
for m in re.finditer(r'<(/?)div', pre):
    d1 += -1 if m.group(1) == '/' else 1
    if d1 < 0: neg1 = True
checks.append(("pre-script depth 0", d1 == 0 and not neg1))

post = h[script_end:]
d2 = 0; neg2 = False
for m in re.finditer(r'<(/?)div', post):
    d2 += -1 if m.group(1) == '/' else 1
    if d2 < 0: neg2 = True
checks.append(("post-script depth 0", d2 == 0 and not neg2))

# ── CSS body{} CONTAMINADO ───────────────────────────────────────
standalone_body = re.findall(r'(?<![.\w-])body(?![.\w-])\s*\{', css)
checks.append(("CSS body{} = 1", len(standalone_body) == 1))

# ── FUNCIONES JS DUPLICADAS ──────────────────────────────────────
fns = re.findall(r'function\s+(\w+)\s*\(', script)
dupes = [f for f, c in Counter(fns).items() if c > 1]
checks.append(("sin funciones duplicadas", len(dupes) == 0))
if dupes: print("DUPLICADAS:", dupes)

# ── IDs HUÉRFANOS ────────────────────────────────────────────────
ids_in_html   = set(re.findall(r'id=["\'](\w[\w-]*)["\']', h))
ids_in_script = set(re.findall(r"getElementById\(['\"](\w[\w-]*)['\"]", script))
orphan_refs   = ids_in_script - ids_in_html
checks.append(("sin getElementById huérfanos", len(orphan_refs) == 0))
if orphan_refs: print("REFS HUÉRFANAS:", orphan_refs)

# ── BASE64 EN CSS (nunca en <style>, siempre en style="" inline) ─
checks.append(("sin base64 en CSS block", not re.search(r'url\(data:image', css)))
if re.search(r'url\(data:image', css):
    print("BASE64 EN CSS: mover imágenes a style=\"\" inline en el div, no en <style>")

# ── VARIABLES JS DUPLICADAS ──────────────────────────────────────
decls = re.findall(r'(?:const|let|var)\s+(\w+)', script)
dupes_decl = [v for v, c in Counter(decls).items() if c > 1]
checks.append(("sin variables duplicadas", len(dupes_decl) == 0))
if dupes_decl: print("VARS DUPLICADAS:", dupes_decl[:10])

# ── ACTIVARDIPOLMA ÚNICA (JoGaSan) ───────────────────────────────
count_ad = h.count('async function activarDiploma')
checks.append(("activarDiploma única", count_ad <= 1))
if count_ad > 1: print(f"ACTIVARDIPLOMA DUPLICADA: {count_ad} definiciones")

# ── REGISTRARMINIAQUIZ 3 PARAMS (JoGaSan) ────────────────────────
mini_quiz_bad = []
for c in re.findall(r"registrarMiniQuiz\([^)]+\)", script):
    inner = re.search(r"registrarMiniQuiz\((.+)\)", c)
    if inner:
        depth, commas = 0, 0
        for ch in inner.group(1):
            if ch in '([': depth += 1
            elif ch in ')]': depth -= 1
            elif ch == ',' and depth == 0: commas += 1
        if commas < 2:
            mini_quiz_bad.append(c[:60])
checks.append(("registrarMiniQuiz 3 params", len(mini_quiz_bad) == 0))
if mini_quiz_bad: print("MINI QUIZ SIN TOTAL:", mini_quiz_bad)

# ── RESULTADO ────────────────────────────────────────────────────
all_ok = True
for label, ok in checks:
    print(f"  {'✓' if ok else '✗'} {label}")
    if not ok: all_ok = False
print(f"\n{'✅ TODO OK' if all_ok else '⚠️  REVISAR'} | {len(h):,} chars")
```

---

## 2. Bugs recurrentes y sus firmas

### 🔴 CRÍTICO — Boundary JS/HTML roto

**Síntoma:** `SyntaxError` con contexto `}Overlay">`, función JS "no definida" a pesar de estar en el archivo.

**Causa:** `str_replace` construyó su patrón OLD cruzando el límite `</script>`.

**Regla:** NUNCA construir OLD patterns que incluyan texto de ambos lados del boundary.

**Fix:**
```python
BROKEN = '}eOverlay">'
FIXED  = '}\n</script>\n\n<div id="treeOverlay">'
h = h.replace(BROKEN, FIXED, 1)
```

---

### 🔴 CRÍTICO — Divs descuadrados

**Síntoma:** Botones disparan múltiples funciones, overlays no aparecen.

**Diagnóstico:**
```python
depth = 0
for i, line in enumerate(section.split('\n')):
    opens  = len(re.findall(r'<div', line))
    closes = len(re.findall(r'</div', line))
    if opens != closes:
        print(f"L{i+1:4} [{depth:+2}→{depth+opens-closes:+2}]: {line.strip()[:70]}")
    depth += opens - closes
print(f"\nFinal depth: {depth}  ← debe ser 0")
```

---

### 🔴 CRÍTICO — textContent destruye span hijo (JoGaSan v190)

**Síntoma:** `TypeError: Cannot set properties of null (setting 'textContent')`.
La siguiente pregunta no aparece, las respuestas anteriores se quedan sin limpiar.

**Causa:** Un div padre contiene un `<span id="X">` hijo. Al hacer `.textContent = '...'`
en el padre, todos los nodos hijos se destruyen. La siguiente llamada a
`getElementById('X')` devuelve `null` → crash.

**Diagnóstico:**
```python
# Buscar divs que se actualizan con textContent y tienen span hijo
ids_con_span = []
for m in re.finditer(r'id=["\'](\w[\w-]*)["\']', h):
    pid = m.group(1)
    # Encontrar el div con ese id y ver si tiene span dentro
    idx = m.start()
    closing = h.find('</div>', idx)
    content = h[idx:closing]
    if '<span' in content:
        ids_con_span.append(pid)

# Verificar si alguno de esos ids se actualiza con textContent
for pid in ids_con_span:
    if f"getElementById('{pid}').textContent" in script:
        print(f"⚠️  {pid}: tiene span hijo + .textContent → bug potencial")
```

**Fix:**
```javascript
// MAL — destruye el span hijo:
document.getElementById('actA-pts').textContent = '⭐ ' + pts + ' pts · Pregunta ' + n + '/8';

// BIEN — innerHTML recrea el span:
document.getElementById('actA-pts').innerHTML =
  '⭐ ' + pts + ' pts · Pregunta <span id="actA-q">' + n + '</span>/8';

// En la función que lee el span, guard null-safe:
var el = document.getElementById('actA-q');
if (el) el.textContent = n;
```

---

### 🔴 CRÍTICO — activarDiploma duplicada (JoGaSan)

**Síntoma:** El diploma nunca se desbloquea aunque el alumno complete todos los módulos.

**Causa:** Dos definiciones `async function activarDiploma(h)` en el mismo index.html.
La segunda (normalmente añadida en una edición posterior) sobreescribe la primera
silenciosamente en el hoisting. La que "gana" puede tener MODS incorrectos.

**Diagnóstico:**
```bash
grep -c "async function activarDiploma" index.html  # debe dar 1
```

**Fix:** Eliminar la definición incorrecta (normalmente la segunda).

---

### 🟠 ALTO — activarDiploma con número hardcodeado (JoGaSan)

**Síntoma:** El diploma nunca se desbloquea aunque MODS.length indique que se completaron todos.

**Causa:** `if (n === 10)` cuando MODS tiene 12 módulos, o `/ 10` cuando hay más.

**Diagnóstico:**
```python
idx_ad = h.find('async function activarDiploma')
ad_body = h[idx_ad:idx_ad+2000]
hardcoded = re.findall(r'(?:=== \d+|/ \d+|n \- \d+)', ad_body)
print("Referencias numéricas hardcodeadas en activarDiploma:", hardcoded)
# Cualquier número fijo es potencialmente incorrecto
```

**Fix:**
```javascript
// MAL:
if (n === 10) { /* desbloquear */ }
var pctVal = Math.round((n / 10) * 100);
label.textContent = n + ' / 10 módulos';
var faltan = 10 - n;

// BIEN — dinámico:
if (n >= MODS.length) { /* desbloquear */ }
var pctVal = Math.round((n / MODS.length) * 100);
label.textContent = n + ' / ' + MODS.length + ' módulos';
var faltan = MODS.length - n;
```

---

### 🟠 ALTO — div#logros-panel faltante (JoGaSan)

**Síntoma:** El panel de logros nunca se pinta, la card de diploma nunca aparece.
No hay errores en consola → fallo silencioso.

**Causa:** `logros-3primaria.js` primera línea: `var panel = getElementById('logros-panel')`.
Si es `null` → `return` inmediato → todo el sistema de logros y diploma queda muerto.

**Diagnóstico:**
```bash
grep -L 'id="logros-panel"' */index.html  # debe dar sin resultados
```

**Fix:**
```html
<!-- Para academias de 3º: div vacío, logros-3primaria lo rellena -->
<div id="logros-panel" data-materia="matematicas3" style="display:none;"></div>
<!-- El data-materia debe coincidir con el id de la academia -->
```

---

### 🟠 ALTO — registrarMiniQuiz sin parámetro total (JoGaSan)

**Síntoma:** Las barras de actividades siempre se quedan en 0%, el chip no sube.

**Causa:** `registrarMiniQuiz('clave', correctas)` sin el tercer parámetro `total`.
`pct = correctas / undefined * 100 = NaN` → `mejor_pct = 0` siempre.

**Diagnóstico:** ver checklist principal (sección registrarMiniQuiz 3 params).

**Fix:** `registrarMiniQuiz('clave', correctas, total)` — 3 parámetros siempre.

---

### 🟠 ALTO — CSS `body{}` contaminado

**Síntoma:** La página entera queda en blanco o el layout explota.

**Diagnóstico:**
```python
standalone = re.findall(r'(?<![.\w-])body(?![.\w-])\s*\{[^}]+\}', css)
print(f"body{{}} rules: {len(standalone)}")  # debe ser 1
```

---

### 🔴 CRÍTICO — Imágenes base64 en bloque `<style>` (página en blanco)

**Síntoma:** La página queda completamente en blanco. Sin errores de JS en consola.

**Causa:** Una imagen base64 muy larga en el bloque `<style>` (ej: `background: url(data:image/jpeg;base64,/9j/...)`) rompe silenciosamente el parser CSS del navegador. Todo el CSS queda invalidado.

**Regla absoluta:** Las imágenes base64 van SIEMPRE en `style=""` inline del elemento HTML, nunca en el bloque `<style>`. Sin excepciones.

```python
# Diagnóstico
import re
css = h[h.find('<style>')+7:h.find('</style>')]
if re.search(r'url\(data:image', css):
    print("❌ BASE64 EN CSS: mover a style=\"\" inline del div")
```

**Fix:**
```html
<!-- MAL — en <style>: -->
<style>
  #bg { background: url(data:image/jpeg;base64,/9j/...); }
</style>

<!-- BIEN — en style="" inline: -->
<div id="bg" style="background: url(data:image/jpeg;base64,/9j/...)"></div>
```

---

### 🔴 CRÍTICO — Div huérfano deja secciones fuera del contenedor principal

**Síntoma:** Una sección (tab, panel, módulo) existe en el HTML con contenido correcto pero el usuario nunca la ve. Sin errores. `offsetHeight > 0` pero visualmente invisible.

**Causa:** Al editar un bloque HTML grande, un `</div>` extra o faltante desplaza el cierre del contenedor principal. Todo el HTML que viene después queda renderizado fuera del DOM esperado (fuera del `<main>`, fuera del `#app`, etc.).

**Cuándo ocurre:** Especialmente al añadir o mover secciones grandes (50+ líneas). Un solo `</div>` de diferencia puede silenciar un tab entero.

**Diagnóstico — verificar balance por sección:**
```python
# Verificar que el contenedor principal cierra bien
main_start = h.find('<main') if '<main' in h else h.find('<div id="app')
main_end = h.rfind('</main>') if '</main>' in h else h.rfind('</div>')
section = h[main_start:main_end]
depth = 0
for m in re.finditer(r'<(/?)(?:div|main|section|article)', section):
    depth += -1 if m.group(1) == '/' else 1
print(f"Balance contenedor principal: {depth}  ← debe ser 0 o 1")
```

**Regla:** SIEMPRE verificar balance de `<div>`/`</div>` después de editar bloques HTML de más de 50 líneas.

---

### 🔴 CRÍTICO — Variable JS declarada dos veces (duplicada)

**Síntoma:** Comportamiento errático o incorrecto en funciones que usan la variable. A veces funciona, a veces no. Sin error explícito en `strict mode`; en modo normal la segunda declaración `var` simplemente reusa la primera.

**Causa:** Al añadir nuevo código JS, se redeclara una variable que ya existía más arriba (`const X`, `let X`, `var X`). En `strict mode` es un `SyntaxError`; en modo laxo, silencio.

**Cuándo ocurre:** Al insertar un nuevo bloque de funcionalidad copiado de otro contexto, o al añadir una variable con nombre genérico (`data`, `result`, `items`, `config`).

**Diagnóstico:**
```python
from collections import Counter
decls = re.findall(r'(?:const|let|var)\s+(\w+)', script)
dupes = [v for v, c in Counter(decls).items() if c > 1]
if dupes:
    print(f"VARS DUPLICADAS: {dupes}")
    for v in dupes:
        for m in re.finditer(rf'(?:const|let|var)\s+{v}\b', script):
            line_no = script[:m.start()].count('\n') + 1
            print(f"  '{v}' declarada en línea {line_no}")
```

**Fix:** Renombrar la segunda declaración o convertirla en asignación (sin `const`/`let`/`var`).

**Variante A — declaración duplicada + texto de comentario pegado al código.**
Una edición o `sed` mal hecho fusiona un comentario con la línea de declaración:
`let X = [];n base — lleva la suya propia (...)`. El `[];n base...` es a la vez
declaración duplicada y sintaxis inválida. Firma: la línea mezcla `];` con prosa
en español y un `—` (em-dash). Fix: borrar la línea corrupta y, si se comió el
comentario de la línea siguiente (p.ej. el de otra `const`), restaurarlo.

**Variante B — `const` reasignada dinámicamente.** Una global que un loader
reasigna (p.ej. catálogo: `X = datos;` dentro de un callback) NO puede ser
`const` → `TypeError: Assignment to constant variable` al cargar. Detección:
```python
# ¿alguna variable declarada const se reasigna luego (= sin declarar)?
for m in re.finditer(r'\bconst\s+(\w+)', script):
    v = m.group(1)
    if re.search(r'(?<![.\w])' + v + r'\s*=(?!=)', script[m.end():]):
        print(f"const {v} se reasigna → debe ser let/var")
```
Fix: cambiar esa `const` por `let`. Guía: mira cómo se declaran sus hermanas —
si `SKU_DB`/`INCOMP` son `let` y se reasignan igual, la tuya también debe serlo.

---

### 🟡 MEDIO — str_replace con patrón stale

**Regla:** SIEMPRE leer el fragmento actual antes de construir OLD. El texto cambia con cada edición.

```python
idx_fn = script.find('function openTree(')
depth=0; started=False
for i in range(idx_fn, min(idx_fn+3000, len(script))):
    c=script[i]
    if c=='{': depth+=1; started=True
    elif c=='}': depth-=1
    if started and depth==0: end_fn=i+1; break
current_fn = script[idx_fn:end_fn]
print(current_fn)  # ← copiar de aquí para construir el OLD
```

---

### 🟡 MEDIO — Elementos duplicados en el DOM

**Diagnóstico:**
```python
id_to_check = 'miComponente'
html_only = h[:script_start-8] + h[script_end+9:]
occurrences = [m.start() for m in re.finditer(f'id="{id_to_check}"', html_only)]
print(f"'{id_to_check}' en HTML: {len(occurrences)} veces → debe ser 1")
```

---

## 3. Verificación obligatoria antes de guardar

```python
def verify_and_save(h, path):
    import re, subprocess
    script_start = h.find('<script>') + 8
    script_end   = h.find('</script>')
    script = h[script_start:script_end]
    css    = h[h.find('<style>')+7:h.find('</style>')]
    errors = []

    # JS syntax
    r = subprocess.run(['node','--check'],
        input=script.encode(), capture_output=True, timeout=15)
    if r.returncode != 0:
        errors.append(f"JS ERROR: {r.stderr.decode()[:200]}")

    # </script> único
    if h.count('</script>') != 1:
        errors.append(f"</script> count = {h.count('</script>')} ≠ 1")

    # Div balance
    pre = h[h.find('<body>'):script_start-8]
    d = sum(-1 if m.group(1)=='/' else 1 for m in re.finditer(r'<(/?)div', pre))
    if d != 0: errors.append(f"pre-script div depth = {d} ≠ 0")

    # CSS body
    standalone = re.findall(r'(?<![.\w-])body(?![.\w-])\s*\{', css)
    if len(standalone) != 1: errors.append(f"CSS body{{}} standalone = {len(standalone)} ≠ 1")

    # activarDiploma única (JoGaSan)
    count_ad = h.count('async function activarDiploma')
    if count_ad > 1: errors.append(f"activarDiploma duplicada: {count_ad} definiciones")

    if errors:
        print("❌ NO GUARDADO:")
        for e in errors: print(f"   • {e}")
        return False

    with open(path, 'w', encoding='utf-8') as f:
        f.write(h)
    print(f"✅ Guardado — {len(h):,} chars")
    return True
```

---

## 4. Estrategia de edición segura

```python
# SIEMPRE este patrón:
# 1. Leer estado actual
# 2. Construir OLD desde lo leído (no desde memoria)
# 3. assert OLD in h antes de replace
# 4. Aplicar replace
# 5. assert h_new != h
# 6. verify_and_save()

OLD = """...(pegado del print anterior)..."""
NEW = """...(versión nueva)..."""
assert OLD in h, "OLD no encontrado — el archivo ha cambiado"
h_new = h.replace(OLD, NEW, 1)
assert h_new != h, "Replace no produjo cambio"
verify_and_save(h_new, 'archivo.html')
```

---

## 5. Diagnóstico por síntoma

| Síntoma | Primer check |
|---|---|
| Pantalla en blanco completa | 1º CSS `body{}` contaminado · 2º base64 en `<style>` |
| Botón dispara múltiples funciones | Divs descuadrados |
| Función "no definida" en consola | Boundary JS/HTML roto → `</script>` count |
| Overlay no aparece (`offsetHeight=0`) | `position:fixed` dentro de `overflow:auto` |
| Componente aparece dos veces | Elemento duplicado en DOM |
| replace no cambia nada | OLD stale → leer estado actual |
| **Tab/sección completamente invisible** | **Div huérfano → sección fuera del contenedor principal** |
| **Comportamiento JS errático sin error** | **Variable declarada dos veces** |
| Panel de logros nunca se pinta | `div#logros-panel` faltante en HTML |
| Diploma nunca se desbloquea | activarDiploma duplicada O número hardcodeado |
| Barras de actividad siempre en 0% | `registrarMiniQuiz` sin tercer param `total` |
| "Cannot set properties of null" en quiz | `.textContent` en div con span hijo |
| Quiz no avanza a siguiente pregunta | Crash por null → ver bug textContent/span |
| Elemento en DOM con contenido pero invisible (`offsetHeight=0`, `display:block`) | Colisión de clase CSS → buscar la clase en `<style>` del monolito |
| **`Unexpected token` en una línea que aislada SÍ parsea** | **Template literal desbordado: backtick de cierre escapado (`\``) aguas arriba → sección 12** |
| **`Assignment to constant variable`** | **`const` reasignada por un loader → debe ser `let` (Variable duplicada, Variante B)** |
| **Tras arreglar un SyntaxError aparece otro** | **Normal: el parser solo reporta el 1º. Re-ejecutar node --check / navegador hasta 0 errores** |
| **Botón/link que existía deja de funcionar tras PR** | **Regresión navegación — ver checklist sección 13** |
| **Función llamada desde UI pero "not defined"** | **Referencia muerta en onclick/handler — ver sección 13** |
| **Token interno (`_Settings`, `_adminX`) visible al usuario** | **Content artifact — ver sección 13** |

---

## 6. Falsos positivos conocidos

| Check | Falso positivo |
|---|---|
| div-balance detecta `</div>` en template literals JS | Ignorar si están dentro de `script` |
| scan HTML incluye bloque `<style>` | Delimitar: `h[h.find('</style>')+8:h.find('<script>')]` |
| ids_en_script incluye ids en onclick inline del HTML | Filtrar correctamente la región |
| registrarMiniQuiz con `Math.round()` — comas internas | El contador de comas a profundidad 0 es correcto; comas dentro de `()` no cuentan |

---

## 10. Colisión de clases CSS — patrón crítico al añadir HTML nuevo

**Contexto:** Al insertar bloques HTML nuevos en monolitos (nuevo detail, nueva sección), es frecuente reutilizar nombres de clase que parecen genéricos pero ya tienen CSS definido en el sistema con comportamiento oculto.

### Síntoma
El elemento existe en el DOM, tiene contenido, `display:block` — pero `offsetHeight = 0`. El contenido es invisible aunque el navegador lo procesa.

### Causa raíz
Una clase CSS del sistema tiene `display:none` por defecto y solo se activa con una clase modificadora específica. El HTML nuevo usa esa clase como contenedor genérico sin saber que está oculta.

**Ejemplo real en SITyL:**
```css
/* En el CSS del portal */
.ctx-body { display: none; }           /* contexto amarillo del agente */
.ctx-body.show { display: block; }     /* solo visible si tiene clase 'show' */
```
Al crear el detail `ctx-prensa`, se usó `class="ctx-body"` como contenedor de las dc-cards. Las tarjetas existían en el DOM con contenido correcto pero eran invisibles. Fix: renombrar a `class="dc-body"`.

### Clases reservadas en SITyL — NO usar como contenedores genéricos

| Clase | Comportamiento real | Alternativa |
|---|---|---|
| `.ctx-body` | `display:none` — contexto agente amarillo, solo visible con `.ctx-body.show` | `.dc-body` |
| `.sub-panel` | `display:none` — tab de detail, visible con `.sub-panel.show` (NO `.sub-panel.active`) | — |
| `.mod-body` | `display:none` — acordeón del hub, visible con `style=""` vía `toggleMod` | — |
| `.txt-acc-body` | `display:none` — expansible de texto | — |
| `.script-full` | `display:none` — script completo (alterna con `.script-short`) | — |

### Check obligatorio al insertar HTML nuevo

Antes de dar por bueno cualquier bloque HTML nuevo, verificar en Playwright:

```python
result = page.evaluate("""() => {
    var el = document.querySelector('.tu-clase-nueva');
    return {
        offsetHeight: el ? el.offsetHeight : -1,
        computedDisplay: el ? getComputedStyle(el).display : 'N/A',
        // Si height=0 y display=block → colisión CSS
    };
}""")
```

**Si `offsetHeight=0` con `display:block`** → colisión CSS. Buscar la clase en el `<style>` del monolito antes de usarla:

```python
import re
css = h[h.find('<style>')+7:h.find('</style>')]
for m in re.finditer(r'\.tu-clase[^{]*\{[^}]+\}', css):
    print(m.group())
```

### Añadir a tabla de síntomas (sección 5)

| Síntoma | Primer check |
|---|---|
| Elemento en DOM con contenido pero invisible (`offsetHeight=0`, `display:block`) | Colisión de clase CSS — buscar la clase en `<style>` del monolito |


---

## 11. Recurring bugs en portales con boundary JS/HTML complejo

Estos patrones aparecen en portales grandes con múltiples bloques JS que se reconstruyen programáticamente. Se documentan aquí como patrones genéricos.

### 🔴 CRÍTICO — `</script>` perdido en substituciones de bloque grande

**Síntoma:** `ReferenceError: functionName is not defined` aunque la función existe en el archivo. `h.count('</script>') == 0`.

**Causa:** Una substitución con `str_replace` / `h.replace()` construyó un patrón `OLD` que cruzaba el boundary `</script>`. El cierre del script quedó embebido en el string de reemplazo en vez de como tag real.

**Síntoma en texto plano:** El archivo contiene algo como `}\neOverlay">` — el cierre de función JS pegado directamente al inicio de HTML.

**Fix:**
```python
# Detectar
assert h.count('</script>') == 1, f"</script> count = {h.count('</script>')} ≠ 1"

# Reparar boundary roto típico:
BROKEN = '}\neOverlay">'  # buscar la cadena literal
FIXED  = '}\n</script>\n\n<div id="treeOverlay">'
h = h.replace(BROKEN, FIXED, 1)
```

**Regla:** NUNCA construir un patrón OLD que incluya texto de ambos lados del boundary `</script>`. Verificar `h.count('</script>') == 1` antes de cada guardado.

---

### 🟠 ALTO — Reconstrucción de bloque HTML: `<div ` se pierde al ensamblar

**Síntoma:** La sección reconstruida tiene el atributo `id="..."` correcto pero sin el `<div ` inicial → HTML inválido → la sección no renderiza.

**Causa:** Al reconstruir con `nuevo_bloque_a + nuevo_bloque_b`, el `<div ` que precede al segundo bloque ya existe en `h[:pos_b]` (es parte del HTML previo). Si `nuevo_bloque_b` empieza con `<div id="..."`, se duplica el tag de apertura.

**Diagnóstico:**
```python
# Antes de ensamblar, verificar que el prefijo ya tiene el '<div '
pos = h.find('id="mi-seccion"')
print(repr(h[pos-6:pos]))  # debe ser '<div '
# Si es '<div ', el nuevo bloque debe empezar con 'id="mi-seccion"' (sin '<div ')
```

**Regla:** Antes de cualquier reconstrucción de bloque, verificar qué hay en `h[pos-6:pos]` y ajustar el nuevo bloque en consecuencia.

---

## 12. Template literal desbordado por backtick de cierre escapado

**Síntoma:** `SyntaxError: Unexpected token '...'` (p.ej. `class`) en una línea que,
**copiada y probada en aislamiento, parsea sin error**. Al neutralizar esa línea el
error salta a la siguiente parecida. Toda la app queda muerta (el `<script>` entero no parsea).

**Causa raíz:** un template literal se abre (`` const html = ` ``) pero su backtick de
cierre está **escapado** (`` \` `` en vez de `` ` ``). Dentro del template, `` \` `` es un
backtick *literal* (texto), no el delimitador. El template no cierra y **absorbe todo el
código posterior como texto** hasta el siguiente backtick real, que cierra en falso; a
partir de ahí el HTML/JS que sigue se parsea como código suelto → `Unexpected token`.
Origen típico: un `sed`/replace global que escapó backticks por error.

**Por qué despista:** el error apunta MUY lejos del backtick culpable (cientos de
líneas) y el bloque señalado es válido. `node --check` sobre un corte truncado da
`Unexpected end of input` (no `Unterminated template`) porque el template absorbido
contiene un `${` que deja al parser esperando — no lo interpretes como "no hay template abierto".

**Diagnóstico — localizar el backtick huérfano:**
```python
# Lexer de backticks a nivel de código: maneja ' " ` , /*..*/, //, ${...} anidado
# y regex literales. VALÍDALO primero en una función sana conocida (OPEN==CLOSE y
# estado final 'code'). Luego, sobre el script: encuentra el OPEN cuyo depth nunca
# vuelve a 0 → esa línea (const x = `) es la que no cierra.
```
Atajo de confirmación: `grep -n '\\`;' archivo.html` — un `` \`; `` (backtick escapado
seguido de `;`) al final de un bloque HTML es casi siempre el cierre roto.

**Fix:** quitar la barra invertida del backtick de cierre (`` </div>\`; `` → `` </div>`; ``).

**Reglas de oro para TODA revisión de monolito (aprendidas aquí):**
- **El parser solo reporta el PRIMER error.** Tras cada fix, re-ejecuta `node --check`
  Y carga en navegador real hasta 0 errores. Un fix ≠ terminado: en un mismo fichero
  convivían dos corrupciones (variable duplicada + backtick escapado), la 2ª oculta tras la 1ª.
- **El navegador es la verdad de terreno** para "¿parsea de verdad?": `node --check` con
  extracción por regex se equivoca si hay `</script>` literal o varios `<script>`. Un
  smoke test Playwright (capturar `pageerror`) es el juez final (ver skill `webapp-testing`).
- **Valida tu lexer/heurística en un caso sano antes de fiarte de él.** Un scanner de
  tokens crudo NO maneja `${}` (hay que re-escanear el template) → da falsos positivos;
  un char-lexer sin manejo de regex `/.../` se atasca. Si el resultado es absurdo
  (0 templates en un fichero lleno de ellos), es el lexer, no el fichero.
- **Antes de reparar, distingue preexistente de introducido:** `git show HEAD:archivo`
  y reproduce el error sobre esa versión. Aquí ambas corrupciones estaban en el commit
  inicial → no las causó el cambio en curso.

---

## 13. Referencias muertas, content artifacts y regresiones de navegación

Tres categorías de bugs que el checklist estático no captura pero que aparecen
repetidamente en portales y argumentarios con mucha iteración.

---

### 🔴 CRÍTICO — Función llamada desde UI pero eliminada o renombrada

**Síntoma:** `ReferenceError: fnX is not defined` al pulsar un botón. El onclick existe
en el HTML pero la función fue renombrada o eliminada en un refactor.

**Causa frecuente:** un ID o función se renombra en JS (`connBadge` → `connMicro`,
`_adminSaveRoles` eliminada) pero los `onclick="..."` en el HTML no se actualizan.
El checklist de `getElementById` huérfanos NO captura esto — solo detecta `getElementById('X')`,
no `onclick="fn()"`.

**Diagnóstico:**
```python
import re

with open('archivo.html', encoding='utf-8') as f:
    h = f.read()

_blocks = re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>', h, re.S)
script = max(_blocks, key=len) if _blocks else ''

# Funciones definidas en JS
defined_fns = set(re.findall(r'function\s+(\w+)\s*\(', script))

# Funciones llamadas desde onclick/onchange/etc en HTML
html_only = h[:h.find('<script')]
called_fns = set(re.findall(r'on\w+=["\'][^"\']*?(\w+)\s*\(', html_only))

# También buscar llamadas directas en atributos href="javascript:fn()"
called_fns |= set(re.findall(r'javascript:\s*(\w+)\s*\(', html_only))

dead_refs = called_fns - defined_fns
if dead_refs:
    print(f"⚠️  FUNCIONES MUERTAS en onclick/handler: {dead_refs}")
    for fn in dead_refs:
        for m in re.finditer(rf'\b{fn}\s*\(', html_only):
            line = html_only[:m.start()].count('\n') + 1
            print(f"   '{fn}' referenciada en línea ~{line}")
else:
    print("✓ Sin referencias muertas en onclick/handlers")
```

**Añadir al checklist §1:**
```python
# ── FUNCIONES MUERTAS EN ONCLICK ─────────────────────────────────
html_only = h[:h.find('<script')]
defined_fns = set(re.findall(r'function\s+(\w+)\s*\(', script))
called_from_html = set(re.findall(r'on\w+=["\'][^"\']*?(\w+)\s*\(', html_only))
called_from_html |= set(re.findall(r'javascript:\s*(\w+)\s*\(', html_only))
dead = called_from_html - defined_fns
checks.append(("sin funciones muertas en onclick", len(dead) == 0))
if dead: print("FUNCIONES MUERTAS:", dead)
```

---

### 🟠 ALTO — Content artifacts: tokens internos visibles al usuario

**Síntoma:** El cliente ve `_Settings`, `_adminSaveRoles`, `_coachSkips` u otros tokens
de código dentro del texto visible del portal.

**Causa:** Un str_replace mal construido deja el token fuera de un comentario JS o lo
inserta dentro de un nodo de texto HTML. Pasa especialmente al editar cerca de la frontera
JS/HTML o al añadir contenido nuevo con find/replace global.

**Diagnóstico:**
```python
import re

# Texto visible: extraer nodos de texto (fuera de <script>, <style>, <!-- -->)
html_visible = re.sub(r'<script[\s\S]*?</script>', '', h)
html_visible = re.sub(r'<style[\s\S]*?</style>', '', html_visible)
html_visible = re.sub(r'<!--[\s\S]*?-->', '', html_visible)
html_visible = re.sub(r'<[^>]+>', '', html_visible)  # quitar tags

# Patrones de tokens internos
TOKEN_PATTERNS = [
    r'\b_[A-Z][a-zA-Z]+\b',        # _Settings, _AdminX
    r'\b_[a-z]+[A-Z][a-zA-Z]+\b',  # _adminSave, _coachSkips
    r'\bfn[A-Z]\w+\b',              # fnOpenModal (si aparece como texto)
    r'\bconsole\.[a-z]+\(',          # console.log visible
]
for pat in TOKEN_PATTERNS:
    hits = re.findall(pat, html_visible)
    if hits:
        unique = list(set(hits))[:5]
        print(f"⚠️  TOKEN INTERNO visible al usuario: {unique}")
```

**Fix:** localizar la línea con `grep -n '_Settings' archivo.html` y verificar si está
dentro de un `<script>` o expuesto como texto. Si es texto, reemplazar o eliminar.

---

### 🟡 MEDIO — Checklist de regresión para navegación básica

Tras cualquier PR que toque `index.html`, verificar estos elementos antes de mergear.
Son los que han introducido regresiones repetidas (PRs #8, #10, #20):

```python
from playwright.sync_api import sync_playwright

SMOKE_CHECKS = [
    # (descripción, selector, acción, condición_esperada)
    ("Logo visible",          ".logo, #logo, [class*='logo']",  None,    "visible"),
    ("Botón back/volver",     "[onclick*='back'], [onclick*='volver'], .back-btn", None, "visible"),
    ("Chip-nav principal",    ".chip-nav .chip-btn",            None,    "count>=1"),
    ("openDetail no crashea", "[onclick*='openDetail']",        "click", "no_pageerror"),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    errors = []

    for viewport in [{"width": 1280, "height": 800}, {"width": 390, "height": 844}]:
        label = "desktop" if viewport["width"] > 500 else "mobile"
        page = browser.new_page(viewport=viewport)
        page_errors = []
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        page.goto(f"file:///ruta/archivo.html")
        page.wait_for_load_state("networkidle")

        for desc, sel, action, condition in SMOKE_CHECKS:
            els = page.locator(sel).all()
            if condition == "visible" and not els:
                errors.append(f"[{label}] {desc}: NO ENCONTRADO ({sel})")
            elif condition == "count>=1" and len(els) == 0:
                errors.append(f"[{label}] {desc}: 0 elementos")
            elif condition == "no_pageerror" and els:
                els[0].click(timeout=2000)
                page.wait_for_timeout(300)
                if page_errors:
                    errors.append(f"[{label}] {desc}: pageerror → {page_errors[-1][:80]}")

    browser.close()

if errors:
    print("❌ REGRESIONES DETECTADAS:")
    for e in errors: print(f"   • {e}")
else:
    print("✓ Navegación básica OK en desktop y mobile")

---

## 13. Lecciones de JoGaSan Academy (oct 2026) — fallos que pasaron todas las auditorías de texto

1. **Compila cada `<script>` inline antes del navegador** (`new vm.Script(código)` en Node; síntoma 54): un paréntesis de menos anuló durante días 11 módulos sin más aviso que «Unexpected token» en consola.
2. **Un `<script>` que define pero no llama:** `iniciarQuiz()` declarada y nunca invocada dejó el quiz final vacío en Lengua 3º m1/m4/m5. Un test que «ayuda» (fuerza el panel) lo tapa: que el piloto marque «QUIZ VACÍO».
3. **Llamar a un global que la página no carga** (`Sonidos.medalla()` sin `sonidos.js`; `getElementById(...).algo` sin guarda): el sB del validador compara scripts compartidos y lo destapó en dos módulos.
4. **Controles que existen pero no se pueden pulsar:** la fila `.t3-tabs` estaba `display:none` y la pestaña «💪 Practica» vivía solo ahí; las pruebas la abrían por código. Pulsa el botón **visible** y comprueba con `elementFromPoint`.
5. **Clases sin ninguna regla CSS** (`.t3-chunk-header/-num/-titulo` en 25 módulos): lista las clases que usa el HTML y no define ninguna hoja antes de mirar contrastes.
6. **Chunks que se acumulan:** `avanzarChunk(n)` debe esconder el anterior; si no, 2 400-3 500 px de scroll y ninguna auditoría lo ve porque cada chunk aislado es corto. Al clonar un módulo, copia la función de una hermana que esconda.
7. **Nunca `overflow` ≠ `visible` en `html` y `body` a la vez:** el `body` se vuelve un segundo contenedor de scroll y se traga la rueda del ratón (`hidden` en `html`, `clip` en `body`).
8. **Comillas invertidas dentro de un template literal de CSS** (motores `quiz-engine.js`, `paso-a-paso.js`) cierran el literal: ni en los comentarios.
9. **Tras un `git merge`:** `git grep -n "<<<<<<<"` antes de commitear (se colaron en `sw.js`); no `git stash` en medio de la fusión; no `checkout --theirs` de un HTML entero (se perdieron cambios de `panel-profe.html`). Mira qué cambios no eran solo `?v=`.
10. **Ficheros con caracteres NUL** (marcadores del generador `scripts/generar-1eso.js`): parches anclados en líneas sin NUL y `errors='surrogateescape'`. Y un HTML **generado** nunca se edita a mano: se edita el origen y se regenera.
11. **Reemplazos masivos:** además de `assert OLD in h`, afirma el **nº de coincidencias** (un helper no se insertó en 11 de 18 ficheros porque el `replace` no encontró `var x = {}` con espacios).
12. **Dos elementos `position:fixed` en el mismo rincón** se pisan sin error alguno: mide sus rectángulos a 320-390 px.
