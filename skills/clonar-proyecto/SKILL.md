---
name: clonar-proyecto
description: "Protocolo para replicar cualquier proyecto web o app existente con el mínimo de iteraciones. Cuatro arquetipos: multi-archivo propio, monolito HTML propio, web externa (URL o captura), y propio sin código fuente. ACTIVA con: \"quiero clonar X\", \"replica esta app\", \"haz algo parecido a Y\", \"toma esta web como base\", \"copia la estructura de\", \"pártete de este proyecto\", \"inspírate en esta URL\", o cuando el usuario pegue URL, captura o código con intención de replicar. ACTIVAR TAMBIÉN: \"la app no carga después del deploy\", \"Google Auth no funciona en producción\", \"Firebase no inicializa\", \"el ZIP no despliega bien\", \"error CORS en Storage\", \"spinner infinito en login\". Cubre: inventario, limpieza de identidad, stack agnóstico, deploy y bugs frecuentes. Leer references/bugs-netlify-firebase.md para Netlify+Firebase. Academia JoGaSan nueva: delegar a clonar-academia. Bugs en monolito durante iteración: delegar a debug-html-monolito.\n"
---

# Protocolo de Clonado de Proyecto

Eres el **Arquitecto de Réplica**. Objetivo: primer deploy funcional, sin identidad
del original filtrada, mínimo de iteraciones hasta versión operativa.

Principio rector: **inventariar → limpiar → verificar → desplegar. En ese orden, siempre.**

**Estimaciones orientativas de tiempo:**

| Fase | Arq. A | Arq. B | Arq. C | Arq. D |
|---|---|---|---|---|
| F0 Diagnóstico + alcance | 15 min | 15 min | 20 min | 30 min |
| F1 Inventario | 30 min | 20 min | 45-90 min | 60-120 min |
| F2 Limpieza identidad | 20 min | 30 min | 15 min | 20 min |
| F3 Verificación + deploy | 20 min | 20 min | 20 min | 20 min |
| **Total primer deploy** | **~90 min** | **~90 min** | **~2-3h** | **~3-5h** |
| F5 Cada iteración posterior | 30-60 min | 45-90 min | 30-60 min | 30-60 min |

> Si cualquier fase supera el doble de lo estimado → parar, revisar scope,
> aplicar el árbol de decisión de §0.5.
> Primera vez con el stack de destino → multiplicar ×2-3 todos los tiempos.

---

## ⚡ FASE 0 — DIAGNÓSTICO OBLIGATORIO

### 0.0 · Acuerdo de alcance — conversación antes de cualquier código

> ⛔ No empezar a clonar sin completar esta conversación.
> El error más frecuente no es técnico: es clonar el 80% que no se necesitaba.

**Protocolo conversacional — cada respuesta condiciona la siguiente pregunta.**
No lanzar todas las preguntas a la vez. Seguir este árbol:

```
P1: ¿Cómo tienes acceso al proyecto origen?
    → archivos locales / URL desplegada / capturas / ZIP / repositorio

P2 (según P1):
    · Si URL → ¿Es una SPA (React/Vue/Angular) o genera HTML en servidor?
    · Si archivos → ¿Es un monolito HTML o múltiples archivos?
    · Si capturas → ¿Tienes también acceso al código o solo la imagen?

P3: ¿Qué quieres clonar — diseño visual, funcionalidad, o ambos?
    → Esto define qué inventariar (CSS/layout vs JS/lógica vs todo)

P4: ¿Hay algo que definitivamente NO quieres clonar?
    → Lo que nombren aquí va directo a "Descartar" en ALCANCE_CLON.md

P5: ¿Cuál es el mínimo que necesitas para considerar esto "funcionando"?
    → Esta respuesta define el MVP — todo lo demás es Fase 2 o backlog

P6: ¿El proyecto origen sigue en desarrollo activo?
    · Si SÍ → acordar punto de congelación (commit/ZIP fijo)
              Si el origen cambia mientras clonas, el inventario queda
              desactualizado y aparecen bugs de sincronización imposibles
              de diagnosticar.
    · Si NO → continuar normalmente.
```

**El MVP es siempre obligatorio** — aunque el usuario no lo mencione, preguntar P5.
Un clonado sin MVP definido no tiene criterio de "terminado".

Una vez completada la conversación, documentar en `ALCANCE_CLON.md`:
```
# Alcance del clon

## MVP (mínimo para considerar esto funcionando)
-

## Fase 2 (mejoras post-MVP, no bloqueantes)
-

## Replica exacta
-

## Adaptar
-

## Descartar
-

## Punto de congelación del origen
- ZIP / commit: ___
```

### 0.1 · Arquetipo de origen

| Arquetipo | Señales | Sección |
|---|---|---|
| **A · Multi-archivo propio** | Carpeta con HTML+JS+CSS separados, Supabase/Firebase | §1A |
| **B · Monolito HTML propio** | Un solo `.html` con `<style>`+`<script>` embebidos >100KB | §1B |
| **C · Web externa** | URL, captura de pantalla, o "quiero algo parecido a X" | §1C |
| **D · Propio sin source** | Proyecto tuyo en producción del que no tienes el código | §0.1b |

### 0.1b · Arquetipo D — origen propio sin código fuente

Si tienes el proyecto en producción pero perdiste (o nunca tuviste) el source:

1. **Abrir las DevTools del navegador** en el proyecto desplegado
2. **Extraer la estructura** desde el panel Elements:
   - Copiar el árbol DOM principal (clic derecho → Copy → Copy outerHTML)
   - Identificar IDs y clases clave que definen la estructura
3. **Extraer CSS computado** por sección:
   - Seleccionar un elemento → Computed → copiar las propiedades relevantes
   - O: Console → `copy(document.styleSheets[0].cssRules[0].cssText)`
4. **Extraer variables JS globales** desde Console:
   ```javascript
   // Ver qué hay en el scope global (funciones y objetos propios)
   Object.keys(window).filter(k => !['chrome','window','document'].includes(k)
     && typeof window[k] !== 'undefined'
     && window[k].toString().includes('function'))
   ```
5. **Leer el bundle JS** desde Sources → aunque esté minificado:
   - DevTools → Sources → Pretty-print (botón `{}`)
   - Los nombres de funciones globales suelen sobrevivir a la minificación
   - Buscar patrones: `function init`, `const CONFIG`, `supabase.createClient`

> Una vez extraído el inventario, continuar con §1C (web externa) para el mapa
> de zonas y el protocolo esqueleto-primero.

### 0.2 · Stack y estructura del DESTINO — leer `references/stacks.md`

Preguntar si no está claro:
- **¿Stack?** → Vanilla JS · React · Vue · otro
- **¿Backend?** → Supabase · Firebase · ninguno · otro
- **¿PWA?** → Sí / No (condiciona manifest + SW)
- **¿Deploy?** → ver §0.3

**Decisión de estructura del destino** (independiente del arquetipo de origen):

| Destino | Cuándo elegirlo |
|---|---|
| **Monolito HTML** | Proyecto de una persona, sin build tools, deploy drag-and-drop, <350KB previstos |
| **Multi-archivo** | Varios módulos/secciones independientes, assets compartidos, >2 colaboradores |
| **Vite + framework** | Componentes reutilizables complejos, ecosistema npm necesario, equipo |

> ⚠️ La estructura del destino no tiene que coincidir con la del origen.
> Un multi-archivo propio puede clonarse como monolito si el scope es menor,
> y una web externa puede convertirse en multi-archivo aunque el original fuera React.
> Decide antes de escribir la primera línea — cambiar de estructura a mitad cuesta caro.

> Si el stack destino ≠ stack origen: leer la sección correspondiente en
> `references/stacks.md` antes de continuar.

### 0.3 · Plataforma de despliegue — leer `references/deploy.md`

Identificar plataforma destino y leer su sección en `references/deploy.md`:
Netlify · Vercel · GitHub Pages · Firebase Hosting · VPS/Nginx · otro

### 0.4 · Deuda heredada del origen — resolver ANTES de clonar

> ⚠️ No copies deuda técnica conocida. Resuélvela en el origen primero.

```bash
# ¿El origen tiene diferencia entre archivo de desarrollo y archivo desplegado?
# Ejemplo: SW registration en deploy pero no en source, features comentadas, etc.
# Documentar y resolver antes de clonar:
echo "Deuda conocida del origen:" > DEUDA_ORIGEN.md
```

### 0.5 · Árbol de decisión — cuando algo sale mal

```
¿El bloqueo es técnico o de scope?
├── TÉCNICO → ¿Puedo simplificarlo? → Sí: reducir scope · No: documentar en DEUDA_ORIGEN.md
├── SCOPE más complejo de lo esperado → ¿MVP viable sin esa parte?
│   → Sí: mover a "Descartar" · No: PARAR y redefinir alcance con el usuario
└── LIMPIEZA: demasiadas referencias al origen
    → <20: limpiar una a una · 20-100: script sed en lote · >100: es un fork, no un clon
```

```bash
# Sustitución en lote (Linux/macOS)
find . \( -name "*.html" -o -name "*.js" -o -name "*.css" \) | \
  xargs sed -i${SED_SUFFIX} "s/NOMBRE_ORIGEN/NOMBRE_DESTINO/g"
# macOS: SED_SUFFIX="''" · Linux: SED_SUFFIX=""
grep -rni "NOMBRE_ORIGEN" . --include="*.html" --include="*.js"  # verificar
```

### 0.6 · Casos especiales → delegar

- **Academia JoGaSan nueva** → skill `clonar-academia`
- **Bugs durante iteración en monolito HTML** → skill `debug-html-monolito`

---

## 📦 FASE 1A — INVENTARIO: Multi-archivo propio

```bash
# Estructura completa del origen
find ./proyecto-origen -type f | sort

# Scripts y CSS globales (importados con "../")
grep -rh 'src="\.\.' ./proyecto-origen/*.html | sort -u
grep -rh 'href="\.\.' ./proyecto-origen/*.html | sort -u
```

**Checklist de inventario:**
- [ ] Archivos locales de la carpeta a clonar
- [ ] Scripts globales con `../` — ¿existen en el destino?
- [ ] CSS compartidos — idem
- [ ] `config.js` — ¿compartido con el origen o hay que crear uno nuevo?
- [ ] Archivos de datos (`*-data.js`, `.json`)
- [ ] Assets binarios — inventario obligatorio:
  ```bash
  # Listar todos los assets binarios del origen
  find ./proyecto-origen -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.svg" -o -name "*.gif" -o -name "*.webp" -o -name "*.ico" \
    -o -name "*.woff" -o -name "*.woff2" -o -name "*.ttf" \
    -o -name "*.mp3" -o -name "*.mp4" \) | sort
  # Verificar que todos están en el destino o que los que faltan son CDN
  ```
  > Un asset binario faltante no da error JS — solo imagen rota o fuente fallback.
- [ ] PWA — `manifest.json`, `sw.js`, iconos de todas las resoluciones
- [ ] Backend — tablas Supabase / colecciones Firebase a crear
- [ ] **Seed data** — documentar en `SEED_DATA.md` qué datos mínimos necesita el clon para probarse (usuarios de prueba por rol, registros de ejemplo, config inicial). Ver protocolo en `references/bugs-primer-deploy.md` §11.

> ⚠️ **`config.js` compartido**: si el clon vive en la misma raíz que el origen,
> hereda su config. Preguntar explícitamente: ¿raíz nueva o raíz compartida?
> Si es raíz compartida y la config es distinta → crear `config-destino.js` local.

**Puntos de inicialización de sesión a verificar:**
- [ ] ¿El origen tiene `autoIniciarSesion()` o equivalente en cada módulo?
- [ ] ¿Se llama ANTES de cualquier registro de actividad/puntos?
- [ ] Si el clon tiene roles distintos al origen — revisar todos los `if (user.role === '...')`

---

## 📄 FASE 1B — INVENTARIO: Monolito HTML propio

```python
with open('origen.html', 'r', encoding='utf-8') as f:
    h = f.read()

import re
print(f"Tamaño: {len(h):,} chars")
print(f"<style>:  {h.find('<style>')} → {h.find('</style>')}")
print(f"<script>: {h.find('<script>')} → {h.find('</script>')}")

# IDs principales
ids = re.findall(r'id=["\']([^"\']+)["\']', h[h.find('</style>'):h.find('<script>')])
print(f"\nIDs HTML ({len(ids)}):"); [print(f"  #{i}") for i in ids[:30]]

# Funciones JS
fns = re.findall(r'function\s+(\w+)\s*\(', h)
print(f"\nFunciones JS ({len(fns)}):"); [print(f"  {f}()") for f in fns]

# Dependencias externas
ext = re.findall(r'src=["\']https?://[^"\']+["\']', h)
print(f"\nDependencias externas ({len(ext)}):"); [print(f"  {e}") for e in ext]
```

> ⚠️ **Umbral de tamaño**: si el monolito supera ~350KB, planificar split desde el
> inicio — no esperar a que los str_replace fallen. Orden de extracción:
> CSS a archivo separado → JS a archivo separado → HTML queda como orquestador.

**Comparación isomórfica origen→clon** (verificar que la estructura se replicó):
```python
# Ejecutar sobre origen y clon, comparar los outputs
import re

def analizar(path):
    h = open(path, encoding='utf-8').read()
    # Zona HTML pura: desde el cierre de </style> hasta el primer <script>
    # rfind(</style>) para manejar múltiples bloques style
    zona_html = h[h.rfind('</style>')+8 : h.find('<script>')]
    ids = re.findall(r'id=["\'"]([^"\']+)["\'"]', zona_html)
    # Todas las funciones en el archivo (incluye las de múltiples bloques script)
    fns = re.findall(r'function\s+(\w+)\s*\(', h)
    return set(ids), set(fns)

ids_o, fns_o = analizar('origen.html')
ids_c, fns_c = analizar('clon.html')

print("IDs en origen pero NO en clon:", ids_o - ids_c)
print("Funciones en origen pero NO en clon:", fns_o - fns_c)
print("IDs nuevos en clon (no estaban en origen):", ids_c - ids_o)
# Los primeros dos grupos son omisiones potenciales.
# El tercero son añadidos intencionales — verificar que son esperados.
```

---

## 🌐 FASE 1C — INVENTARIO: Web externa

### Preguntas obligatorias
1. ¿URL accesible, captura, o ambas?
2. ¿Cuántas pantallas/vistas tiene la web? (no es siempre una sola)
3. ¿Qué pantallas concretas replicar?
4. ¿Layout visual, funcionalidad, o ambas?

**Inventario de pantallas** (si hay más de una vista):
```
PANTALLAS A CLONAR:
□ / (home/landing)
□ /login  □ /registro
□ /dashboard  □ /perfil
□ /detalle/:id
□ Otra: ___

Para cada pantalla marcada → hacer un mapa de zonas independiente.
No mezclar zonas de pantallas distintas en el mismo mapa.
```

### Si hay URL → `web_fetch` y analizar

> ⚠️ **Limitación crítica con SPAs**: React, Vue, Next.js y Angular renderizan
> en el cliente. `web_fetch` devuelve el HTML del servidor — en una SPA esto es
> casi siempre `<div id="root"></div>` vacío, sin contenido real.
>
> **Señales de SPA**: poco HTML visible, `<div id="root">`, `<div id="__next">`,
> `<div id="app">` como contenedor principal, o `bundle.js`/`chunk.js` en los scripts.
>
> **En ese caso**: no analizar el HTML fuente. Ir directamente al protocolo de captura.

```python
señales_framework = {
    'Next.js/React': ['__NEXT_DATA__', '_app.js', 'ReactDOM'],
    'Vue/Nuxt':      ['__vue__', '__nuxt', 'v-bind'],
    'Angular':       ['ng-version', 'ng-app'],
    'WordPress':     ['wp-content', 'wp-json'],
    'SPA genérica':  ['<div id="root">', 'bundle.js', 'chunk.js'],
    'Vanilla':       'ausencia de los anteriores + contenido HTML visible',
}
# Si es SPA → ir a protocolo de captura. Si es vanilla/WP → extraer del HTML fuente.
# Extraer: secciones principales · CDNs · fuentes · variables CSS · datos dinámicos
```

### Si solo hay captura → mapa de zonas (confirmar antes de escribir código)

Elegir la variante y rellenar:

```
VARIANTE A — Con sidebar:              VARIANTE B — Full-width (más común):
┌──────┬────────────────┐              ┌────────────────────────┐
│ nav  │  topbar        │              │  nav                   │
│ side ├────────────────┤              ├────────────────────────┤
│      │  main          │              │  hero / header         │
└──────┴────────────────┘              ├────────────────────────┤
                                       │  main content          │
VARIANTE C — Dashboard/app:            └────────────────────────┘
┌──────┬──────┬─────────┐
│ rail │ list │ detail  │              VARIANTE D — Landing page:
│      │      │         │              ┌────────────────────────┐
└──────┴──────┴─────────┘              │  hero full-screen      │
                                       ├────────────────────────┤
                                       │  sección 1 · 2 · 3     │
                                       ├────────────────────────┤
                                       │  CTA / footer          │
                                       └────────────────────────┘
```

Para la variante elegida, completar:
```
PALETA:  primario #__ · secundario #__ · fondo #__ · texto #__ · acento #__
TIPOGRAFÍA: familia · peso titular · tamaño base __px
COMPONENTES: □ Cards  □ Tabla  □ Modal  □ Form  □ Tabs  □ Toast  □ Otro:__
```

### Protocolo "esqueleto primero" (orden obligatorio)

```
1. HTML semántico vacío → zonas del mapa, sin clases ni JS
2. CSS layout         → :root con variables · grid-template-areas · mobile-first
3. Contenido estático → textos de prueba · imágenes placeholder
4. Componentes JS     → uno a uno, de más simple a más complejo
5. Backend            → conectar solo cuando layout y componentes funcionan
```

> Leer `references/stacks.md` para checklist de arranque según el stack destino.

---

## 🧹 FASE 2 — LIMPIEZA DE IDENTIDAD

Obligatoria antes del primer deploy, independientemente del arquetipo.

### Mapa de sustituciones (rellenar antes de ejecutar)

| Qué | Valor origen | Valor destino |
|---|---|---|
| Nombre del proyecto | `proyecto-origen` | `proyecto-destino` |
| ID Supabase/Firebase | `xxx-origen` | `xxx-destino` |
| CACHE_NAME (SW) | `cache-v1-origen` | `cache-v1-destino` |
| Versiones `?v=N` de scripts | heredadas | bumping a `v=1` en el clon |
| Clave localStorage | `origen_user` | `destino_user` |
| `<title>` | "Portal Origen" | "Portal Destino" |
| `manifest.json` name/short_name/start_url/id | origen | destino |
| Meta OG (og:title, og:site_name, og:url) | origen | destino |
| Variables CSS (`--origen-primary`) | origen | destino |
| `package.json` name/version/description/repository | origen | destino |
| Roles de usuario (`'moderador'`, `'alumno'`) | ¿cambian en el clon? | actualizar |
| Color primario | `#FF6B00` | `#nuevo` |

### Checklist de accesibilidad y seguridad

Ver checklists completos en `references/bugs-primer-deploy.md` §12 y §13.

Resumen ejecutivo:
- [ ] Webs externas: `<img>` con `alt`, contraste ≥ 4.5:1, `<label>` en formularios
- [ ] Todos los arquetipos: ninguna clave privada (`service_role`, `private_key`) en el cliente
- [ ] URLs de `localhost` o `staging` eliminadas del JS del clon

### ⛔ Gate — verificar mapa antes de continuar

Antes de ejecutar el script: confirmar que todos los valores "destino" del mapa
están rellenos (ninguno dice "destino" literal, ningún valor es igual al del origen).
Ver protocolo completo en `references/bugs-primer-deploy.md` §14.

### Script de búsqueda de contaminación

```bash
# ⚠️ Sustituir por el nombre real antes de ejecutar
NOMBRE_ORIGEN="___RELLENAR___"

echo "=== Identidad del origen ==="
grep -rni "$NOMBRE_ORIGEN" . --include="*.html" --include="*.js" --include="*.css" --include="*.json"

echo "=== Versiones ?v=N heredadas (revisar si el número coincide con el origen) ==="
grep -rni "?v=" . --include="*.html"

echo "=== URLs hardcodeadas (excluye CDNs conocidos) ==="
grep -rni "http" . --include="*.js" --include="*.html" | grep -v "cdn\|fonts\|googleapis\|jsdelivr\|supabase\|firebase"

echo "=== Claves y tokens ==="
grep -rni "apikey\|anonkey\|projecturl\|clientid\|secret" . --include="*.js" | grep -v "//"

echo "=== manifest.json ==="
cat manifest.json 2>/dev/null | python3 -m json.tool

echo "=== Meta OG ==="
grep -i "og:\|twitter:" index.html 2>/dev/null

echo "=== robots.txt / sitemap ==="
ls robots.txt sitemap.xml 2>/dev/null && echo "⚠️ Actualizar dominio"
```

---

## ✅ FASE 3 — VERIFICACIÓN PRE-DEPLOY

### Script automático

```python
import os, re, subprocess

CLON_DIR   = './nuevo-proyecto'
NOMBRE_ORI = 'proyecto-origen'   # ajustar
errores    = []

for root, dirs, files in os.walk(CLON_DIR):
    for fname in files:
        if not fname.endswith(('.html','.js','.css')): continue
        path    = os.path.join(root, fname)
        content = open(path).read()

        # Rastros del origen — excluir líneas de comentario
        lineas = [l for l in content.splitlines()
                  if not l.strip().startswith(('//', '#', '/*', '*'))]
        if any(NOMBRE_ORI in l for l in lineas):
            errores.append(f"⚠️  Rastro de origen en código activo: {path}")

        if fname.endswith('.js'):
            r = subprocess.run(['node','--check', path], capture_output=True)
            if r.returncode != 0:
                errores.append(f"❌ JS inválido: {path}\n   {r.stderr.decode()[:100]}")

        if fname.endswith('.html'):
            # Verificar scripts JS y CSS locales (patrón robusto + urlparse para CDNs)
            from urllib.parse import urlparse
            refs = (
                [('Script', s) for s in re.findall(r'src=["\']([^"\'.][^"\']*\.js[^"\']*)["\']', content)]
              + [('CSS',    c) for c in re.findall(r'href=["\']([^"\'.][^"\']*\.css[^"\']*)["\']', content)]
            )
            for label, ref in refs:
                if urlparse(ref).scheme: continue
                abs_ref = os.path.normpath(os.path.join(root, ref.split('?')[0]))
                if not os.path.exists(abs_ref):
                    errores.append(f"\u274c {label} no encontrado: {ref} en {path}")

if errores:
    print(f"❌ {len(errores)} problemas:"); [print(f"  {e}") for e in errores]
else:
    print("✅ Verificación OK — listo para deploy")
```

### Snapshot v0 — antes de la primera iteración

```bash
# Crear ZIP del clon limpio ANTES de empezar a iterar
zip -r clon-v0-snapshot.zip ./nuevo-proyecto/
# Esto es el punto de retorno si algo se rompe irreversiblemente
```

### Smoke test post-deploy (5-10 minutos)

> 🤖 = verificación automática (script o DevTools) · 👁 = verificación manual

- [ ] 🤖 Sin errores en consola del navegador (F12 → Console)
- [ ] 👁 Título del navegador correcto (no el del origen)
- [ ] 🤖 Autenticación usa credenciales del nuevo proyecto (verificar en Supabase/Firebase dashboard)
- [ ] 🤖 Datos se guardan en tabla/colección correcta (verificar en dashboard del backend)
- [ ] 🤖 SW tiene CACHE_NAME correcto (DevTools → Application → Service Workers)
- [ ] 🤖 `fetch()` y XHR apuntan a endpoints del nuevo proyecto (DevTools → Network → XHR)
- [ ] ⚠️ Si origen y clon comparten localhost: Clear Site Data antes de probar
- [ ] 🤖 `manifest.json` correcto (DevTools → Application → Manifest)
- [ ] 👁 Preview OG correcto (compartir URL en Slack/WhatsApp y verificar preview)
- [ ] 👁 Roles de usuario se comportan como se espera (probar con cada rol)
- [ ] 👁 **Flujo principal end-to-end** — ejecutar el recorrido completo del usuario:
  ```
  1. Registro o login con usuario de prueba
  2. Acción principal del proyecto (crear, guardar, publicar...)
  3. Verificar que el resultado persiste (recargar y comprobar)
  4. Logout y re-login — verificar que el estado se mantiene
  ```
  > Este es el check más importante: piezas que funcionan aisladas
  > pero cuyo flujo completo está roto son el bug más difícil de detectar.
- [ ] 👁 **Idioma / textos** — buscar strings del idioma del origen sin sustituir:
  ```bash
  grep -rni "hello\|welcome\|submit" . --include="*.html" --include="*.js"
  # Ajustar a los términos del idioma del origen que NO deben aparecer en el clon
  ```
- [ ] **Rendimiento básico** — abrir DevTools → Lighthouse → Mobile:
  - Performance ≥ 70 (si es <50 hay algo heredado del origen que pesa demasiado)
  - Assets sin comprimir o imágenes >500KB del origen son la causa más frecuente
  ```bash
  # Alternativa CLI si tienes Node:
  npx lighthouse https://tu-clon.netlify.app --output=json --only-categories=performance
  ```

---

## 🐛 FASE 4 — BUGS DEL PRIMER DEPLOY

Ver tabla completa en `references/bugs-primer-deploy.md`.

### Los 5 más frecuentes (referencia rápida)

| Síntoma | Causa | Fix rápido |
|---|---|---|
| Datos en el proyecto origen | Credenciales sin cambiar | Revisar `config.js` |
| SW sirve contenido del origen | CACHE_NAME igual + caché en localhost | Cambiar versión + Clear Site Data |
| Funciones JS "no definidas" | Script `../` que no existe en destino | Copiar script global |
| Parece funcionar pero no graba | `autoIniciarSesion` no se llama antes del primer registro | Añadir al inicio del módulo |
| Monolito: str_replace falla sin razón | Archivo >350KB, OLD stale | Leer estado actual antes de construir OLD |

### Si los bugs son en un monolito HTML
→ Activar skill `debug-html-monolito`

---

## 🔄 FASE 5 — ITERACIÓN POST-DEPLOY

> La skill no termina en el primer deploy. El ciclo real es:
> deploy → feedback → iteración → nuevo deploy.
> Esta fase evita que las iteraciones acumulen deuda nueva.

### Protocolo de iteración segura

**Antes de cada iteración:**
```bash
# 1. Snapshot del estado actual antes de tocar nada
zip -r clon-pre-iter-$(date +%Y%m%d-%H%M).zip ./nuevo-proyecto/

# 2. Verificar que el estado actual está limpio (sin bugs pendientes)
#    Si hay bugs abiertos → cerrarlos antes de añadir nueva funcionalidad
```

**Durante la iteración:**
- Una feature / un bug a la vez — no mezclar en la misma sesión
- Después de cada cambio: verificar que lo anterior sigue funcionando
- Si algo se rompe y no sabes por qué en <15 min → **aislar antes de revertir**:
  ```
  1. Anotar exactamente qué cambió y qué se rompió
  2. Deshacer solo el último cambio (no todo el snapshot)
  3. Si sigue roto → el bug es anterior → revertir al snapshot
  4. Si se arregla → el cambio era el causante → abordarlo diferente
  ```

**Cuándo hacer snapshot intermedio:**
- Al completar una feature que funciona
- Antes de una refactorización
- Antes de tocar CSS global o JS compartido
- Siempre antes de una sesión nueva si la anterior acabó con algo "a medias"

### Gestión de versiones durante iteración

```bash
# Bumping de versión en cada deploy que cambie JS o CSS
# (evita que usuarios vean versión cacheada)
# En vanilla: incrementar ?v=N en los scripts modificados
grep -n "?v=" index.html  # ver versiones actuales
# Incrementar solo los archivos que cambiaron, no todos

# Convención recomendada:
# ?v=1  → versión inicial del clon
# ?v=2  → primera iteración con cambios
# ?v=N  → N-ésima iteración
```

### Registro de decisiones (ADR mínimo)

Cada decisión de arquitectura tomada durante la iteración debe registrarse:

```bash
cat >> DECISIONES.md << 'EOF'

## $(date +%Y-%m-%d) — [título de la decisión]
**Contexto:** qué situación generó la decisión
**Decisión:** qué se hizo
**Por qué no se copió del origen:** 
**Consecuencias:** qué implica esta decisión para el futuro
EOF
```

> Sin este registro, en 3 semanas nadie recuerda por qué el clon es distinto
> al origen en ese punto — y alguien "lo arregla" volviendo al patrón del origen.

### Protocolo de cierre de sesión de trabajo

Al terminar cada sesión, anotar en `DECISIONES.md`:
- Estado actual (qué funciona / qué no)
- Próximo paso exacto para la siguiente sesión
- Archivos modificados + snapshot creado (sí/no)

> Especialmente crítico en sesiones con AI: sin este registro la siguiente
> conversación empieza desde cero. Ver plantilla completa en `references/bugs-primer-deploy.md` §15.

### Cuándo el clon está listo para considerar "terminado"

- [ ] Todas las features del alcance acordado en `ALCANCE_CLON.md` funcionan
- [ ] Smoke test de Fase 3 pasa completamente
- [ ] Sin errores ni warnings en consola del navegador
- [ ] `DECISIONES.md` refleja las divergencias del origen
- [ ] Snapshot final creado: `clon-v1-release.zip`
- [ ] Archivos de proyecto incluidos en el repo o en lugar accesible:
  - `ALCANCE_CLON.md` — qué se clonó y qué se descartó
  - `DECISIONES.md` — por qué el clon difiere del origen en ciertos puntos
  - `SEED_DATA.md` — cómo reproducir los datos iniciales (si aplica)
  - `DEUDA_ORIGEN.md` — deuda que quedó pendiente (si aplica)

### 📋 Informe de cierre — generarlo siempre al terminar F5

Al completar el clonado, generar este informe antes de cerrar la sesión.
Es el mecanismo por el que la skill sugiere qué hacer a continuación.

**Estructura del informe:**

```
INFORME DE CIERRE — [nombre del proyecto destino]
Fecha: [fecha] · Arquetipo: [A/B/C/D] · Stack: [stack] · Deploy: [URL o ruta]

──────────────────────────────────────────────
ESTADO FINAL
──────────────────────────────────────────────
✅ Completado:
  - [lista de lo que funciona]

⚠️  Issues detectados:
  #1 [descripción concreta del problema] — [dónde está / qué archivo]
  #2 ...

❌ Pendiente (fuera del alcance acordado o bloqueado):
  - [lista]

──────────────────────────────────────────────
DECISIONES TOMADAS (divergencias del origen)
──────────────────────────────────────────────
  - [por qué el clon difiere del origen en X punto]

──────────────────────────────────────────────
SKILLS RECOMENDADAS
──────────────────────────────────────────────
[Solo incluir las que tienen justificación concreta basada en los issues detectados]

→ [nombre-skill] — porque [issue concreto detectado]
  Cómo activarla: "[instrucción específica para esta sesión]"

NO necesarias en este proyecto:
→ [skill] — porque [razón concreta: "no hay lógica de X", "no es entregable Y"]

──────────────────────────────────────────────
PRÓXIMO PASO
──────────────────────────────────────────────
[El primer paso exacto de la siguiente sesión, sin ambigüedad]
```

**Reglas del informe:**

1. **Los issues son concretos, no genéricos** — no "revisar el CSS", sino "el color primario del botón de login (#FF6B00) es del origen, no del destino"
2. **Las skills se recomiendan por issues reales** — si no hay problema de UX detectado, no recomendar la skill de UX
3. **"NO necesarias" es tan importante como las recomendadas** — evita que el usuario pierda tiempo activando skills irrelevantes
4. **El próximo paso es accionable** — no "continuar el desarrollo", sino "arreglar el logout: la función `cerrarSesion()` en app.js no limpia el localStorage"

**Ejemplo de informe real:**

```
INFORME DE CIERRE — portal-ventas-v2
Fecha: 2024-03-15 · Arquetipo: A · Stack: Vanilla JS + Supabase · Deploy: https://portal-ventas-v2.netlify.app

ESTADO FINAL
✅ Completado:
  - Estructura multi-archivo clonada (8 archivos)
  - Identidad limpia — 0 rastros del origen
  - Auth funcionando con credenciales del nuevo proyecto
  - Flujo E2E: login → crear registro → logout ✅

⚠️  Issues detectados:
  #1 CSS: variable --primary-color heredada del origen en styles.css línea 12
  #2 Lighthouse Mobile: 52 — hero.jpg sin comprimir (1.8MB, del origen)
  #3 Textos: 3 labels en inglés ("Submit", "Cancel", "Loading...") en app.js líneas 45, 89, 134

DECISIONES TOMADAS
  - Se descartó el módulo de exportación PDF (fuera del alcance acordado)
  - Se creó config.js local en lugar de compartir el del origen

SKILLS RECOMENDADAS
→ auditoria-ux-visual — por issues #1 y #2 (variable CSS + imagen pesada)
  Cómo activarla: "audita el contraste y el rendimiento visual de portal-ventas-v2,
  hay una variable CSS heredada del origen y una imagen de 1.8MB sin comprimir"

→ documentador-contexto-proyecto — el módulo PDF descartado debe quedar en DECISIONES.md
  Cómo activarla: "documenta las decisiones de arquitectura de portal-ventas-v2,
  especialmente por qué se descartó el módulo de exportación PDF"

NO necesarias en este proyecto:
→ auditoria-consistencia-puntos — no hay lógica de puntos ni gamificación
→ masorange-style — no es un entregable corporativo MasOrange

PRÓXIMO PASO
Corregir issue #1: abrir styles.css, línea 12, cambiar
--primary-color: #FF6B00 por --primary-color: #2563EB (color destino acordado)
```

---

## 📊 FASE 6 — INFORME DE CIERRE

> Generar siempre al terminar F5, o cuando el usuario diga "informe", "resumen",
> "qué queda pendiente", "qué skill activo ahora" o similares.
> El informe es específico — no genérico. Cada sección se rellena con lo detectado
> en las fases anteriores, no con plantillas vacías.

### Estructura del informe

```
INFORME DE CIERRE — [nombre-proyecto-destino]
Fecha: [fecha] · Arquetipo: [A/B/C/D] · Stack: [stack] · Deploy: [plataforma]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ESTADO DEL DEPLOY
[URL del deploy si existe]
✅ Funciona: [lista de lo que funciona]
❌ Pendiente: [lista de lo que no funciona aún]
⚠️  Bugs conocidos: [lista con referencia a §N de bugs-primer-deploy si aplica]

DECISIONES TOMADAS (diferencias respecto al origen)
- [qué se cambió] → [por qué]
- [qué se descartó] → [por qué]

DEUDA TÉCNICA DETECTADA
- [item]: [descripción breve] · Prioridad: alta / media / baja

SKILLS RECOMENDADAS
→ [/atajo]  — [razón específica basada en lo detectado]
             actívala con: "[prompt concreto de arranque]"

NO necesarias en este caso:
→ [/atajo]  — [por qué no aplica]

PRÓXIMO PASO
[Descripción exacta del primer paso de la siguiente sesión]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Criterios para recomendar cada skill

| Skill | Recomendar si se detectó... |
|---|---|
| `/ux` (auditoría UX) | CSS heredado sin actualizar · contraste incorrecto · layout roto en móvil · Lighthouse < 70 · imágenes >500KB |
| **Netlify+Firebase** | Stack incluye Firebase Auth o Google Auth + Netlify → leer `references/bugs-netlify-firebase.md` antes del F3 smoke test |
| `/doc` (documentador) | Decisiones de arquitectura tomadas · divergencias respecto al origen · sesión sin cerrar en DECISIONES.md |
| `/puntos` (consistencia puntos) | Backend con lógica de puntos/scores/rankings · race conditions sospechosas · datos que no sincronizan entre dispositivos |
| `/style` (estilo corporativo) | El destino es un entregable para un cliente o marca específica con identidad visual definida |
| Skill de debug monolito | Monolito >350KB con bugs difíciles de aislar · str_replace fallando · funciones duplicadas |
| Skill de auditoría pedagógica | El proyecto clonado es una plataforma educativa con contenido curricular |

### Reglas del informe

1. **Específico, no genérico** — "el color primario del origen sigue en el header" es útil. "Puede haber colores del origen" no lo es.
2. **MVP siempre presente** — aunque el usuario no lo haya mencionado, el informe siempre tiene sección MVP con su estado.
3. **Roadmap en 3 niveles** — MVP / Fase 2 / Backlog. Lo descartado en §0.0 siempre aparece en Backlog con su razón.
4. **Skills ancladas a cada fase del roadmap** — no una lista genérica al final, sino indicadas en el nivel donde aplican.
5. **Solo recomendar lo que aplica** — si una skill no aplica, decirlo con la razón.
6. **Prompt de arranque obligatorio** — cada skill incluye el texto exacto con el que arrancarla, basado en lo detectado.
7. **Próximo paso sin ambigüedad** — suficientemente específico para retomar sin contexto previo.
8. **Si no hay issues** — decirlo explícitamente: "No se detectaron issues. El clon está limpio y operativo."


### Ejemplo de informe real

```
INFORME DE CIERRE — portal-comercial-v2
Fecha: 2025-06-09 · Arquetipo: B (monolito HTML) · Stack: Vanilla JS · Deploy: Netlify
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ESTADO DEL DEPLOY
https://portal-comercial-v2.netlify.app
✅ Funciona: login, listado de productos, filtros, exportar CSV
❌ Pendiente: modal de detalle no cierra al hacer clic fuera
⚠️  Bug conocido: SW con CACHE_NAME del origen (§1 bugs-primer-deploy)
               → Fix: cambiar 'portal-origen-v3' → 'portal-comercial-v2-v1' en sw.js

DECISIONES TOMADAS
- Paleta: cambiado color primario del origen → color identidad cliente
- Módulo de facturación: descartado — fuera del scope del MVP acordado
- Fuentes: migrado de locales → Google Fonts CDN (simplifica mantenimiento)

DEUDA TÉCNICA DETECTADA
- Modal de detalle: listener click-outside no heredado del origen · Prioridad: alta
- Imágenes de producto: 4 imágenes >800KB sin comprimir · Prioridad: media

━━━ ROADMAP ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

MVP — portal operativo con login, catálogo y exportación CSV
Estado: 90% — falta corregir el modal de detalle y el CACHE_NAME del SW
Skills antes de cerrar MVP:
→ /ux  — Lighthouse Mobile 52 + modal roto en táctil
          actívala con: "audita el rendimiento y el modal de detalle en móvil"
→ /doc — 3 decisiones de arquitectura sin documentar
          actívala con: "documenta las decisiones de esta sesión: cambio de
          paleta, descarte de facturación y migración de fuentes"

FASE 2 — Mejoras post-MVP
- Optimización de imágenes: comprimir 4 assets · Esfuerzo: bajo
- Animaciones de transición entre vistas · Esfuerzo: medio
- Modo oscuro · Esfuerzo: medio
Skills para Fase 2:
→ /ux  — revisión completa tras optimización visual

BACKLOG — Descartado en §0.0
- Módulo de facturación: fuera del scope del cliente para esta versión
- Integración con ERP: requiere más contexto sobre la API disponible

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRÓXIMO PASO EXACTO
Corregir el listener closeModal() (línea ~847 del monolito) para cerrar
al hacer clic fuera, y cambiar CACHE_NAME en sw.js. Con eso el MVP está cerrado.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```


---

## 📋 REFERENCIA RÁPIDA

| Arquetipo | Flujo |
|---|---|
| A · Multi-archivo propio | F0 → F1A → F2 → F3 → deploy → F4 si bugs → F5 → F6 informe |
| B · Monolito HTML propio | F0 → F1B → F2 → F3 → deploy → F4 si bugs → F5 → F6 informe |
| C · Web externa (URL) | F0 → F1C(url) → construir → F2 → F3 → deploy → F5 → F6 informe |
| C · Web externa (captura) | F0 → F1C(mapa zonas) → esqueleto → F2 → F3 → deploy → F5 → F6 informe |
| D · Propio sin source | F0 → §0.1b(DevTools) → F1C → F2 → F3 → deploy → F5 → F6 informe |
| JoGaSan academia nueva | → skill `clonar-academia` |

**Referencias a cargar según contexto:**
- Stack de destino (Vanilla/React/Vue) → `references/stacks.md`
- Plataforma de deploy → `references/deploy.md`
- Bugs detallados del primer deploy → `references/bugs-primer-deploy.md`
- **Netlify + Firebase/Google Auth** → `references/bugs-netlify-firebase.md` ← leer SIEMPRE que el stack incluya Firebase o Google Auth en Netlify
---

## F4.6 — Colisión de clases CSS al añadir contenido nuevo

Al clonar un proyecto y añadir secciones nuevas (details, panels, tabs), verificar siempre que las clases CSS usadas en el HTML nuevo no colisionen con clases ya definidas en el sistema.

### Síntoma
Elemento presente en DOM con contenido correcto, `display:block`, pero `offsetHeight = 0` — invisible para el usuario.

### Check rápido antes de declarar done

```python
# En el script de diagnóstico Playwright:
result = page.evaluate("""() => {
    var el = document.querySelector('.clase-que-acabo-de-usar');
    return {
        height: el ? el.offsetHeight : -1,
        display: el ? getComputedStyle(el).display : 'N/A',
    };
}""")
# Si height=0 y display=block → colisión CSS
```

### Cómo verificar antes de usar una clase

```python
import re
css = h[h.find('<style>')+7:h.find('</style>')]
hits = re.findall(r'\.nombre-clase[^{]*\{[^}]+\}', css)
for hit in hits:
    if 'display:none' in hit or 'display: none' in hit:
        print("⚠ CLASE OCULTA:", hit)
```

**Regla:** si una clase tiene `display:none` en el CSS base, no usarla como contenedor genérico. Elegir un nombre neutro que no exista en el sistema.

---

## 🧩 Lecciones de JoGaSan Academy (producción, sep-oct 2026)

- **El validador es la puerta del deploy:** `netlify.toml` corre `node scripts/validar-academias.js` antes del build y cualquier *error* para el deploy. Un check nuevo que destape errores antiguos se arregla en la misma PR. Un solo `CACHE_VERSION` en `sw.js` y un script que lo copia a `version.json` y al watchdog (también en el build): tres sitios a mano se desincronizaron.
- **Acceso de familia ≠ seguridad.** La «puerta» es un filtro en el navegador: en el código solo vive una huella PBKDF2 de `usuario|SHA-256(contraseña)` (ni usuario ni contraseña en claro), se pide una vez por dispositivo **y por origen**, y no sale en `localhost`/`127.0.0.1`/`file:` para que las pruebas con Playwright sigan funcionando. Supabase con la *publishable key* sigue abierto a `anon`; para público desconocido hace falta Auth + RLS. Dilo así al usuario.
- **Privacidad de buscadores:** cabecera `X-Robots-Tag: noindex, nofollow, noarchive, nosnippet` para todo el sitio en `netlify.toml` (HTML, JS, JSON y PDF).
- **Modo invitado / demo:** acceso con código y caducidad, ejemplos sembrados, botón «Reiniciar mi prueba», aislamiento por prefijo (filtrar en rankings, informes y correos) y una función programada que borra por `alumno_norm` las tablas de alumno. Si añades una tabla con `alumno_norm`, entra en la lista de limpieza.
- **Dominio y recursos:** URLs absolutas con el dominio propio, nunca `*.netlify.app`; PWA con manifest e icono puestos por un script común; los PNG se cachean 7 días: mismo nombre + `?v=` para cambiar uno.
- **Varias sesiones sobre el mismo repo:** `COORDINACION.md` (qué rama toca qué, aviso para quien fusione), fetch + merge de `main` antes de empujar, mirar las **PR abiertas** antes de un ítem de backlog compartido, versiones `?v=` finales por encima de las dos ramas, y nada de editar HTML generado.
- **Pruebas antes de subir:** validador sin errores nuevos frente a `main` (grupo de control en un worktree), `node --check` de los scripts, Playwright con sesión sembrada, `serviceWorkers:'block'` y `waitUntil:'domcontentloaded'`; en el resumen, lo que **no** se pudo probar.
