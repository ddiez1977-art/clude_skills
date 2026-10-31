<!-- RECONSTRUIDO el 2026-10-31 a partir del texto íntegro generado en el chat "Skill genérica para clonar y revisar estructuras" (2026-06-11), más el bloque "Vanilla JS multi-archivo" añadido después en ese mismo chat. No se encontró el fichero original. Si ves diferencias con tu versión, manda la tuya y prevalece. -->
# Referencia de Stacks por Tecnología

Leer la sección de tu stack destino antes de escribir la primera línea de código.
El stack origen puede ser cualquiera — estas secciones describen el destino.

---

## Stack destino: Vanilla JS (sin build tools)

**Cuándo elegirlo:** Netlify drag-and-drop, sin pipeline de build, máxima portabilidad,
proyectos de una sola persona, cuando el tiempo de setup importa.

### Checklist de arranque

- [ ] `index.html` con `<!DOCTYPE html>`, `lang="es"`, `viewport` correcto
- [ ] CSS: archivo separado o `<style>` embebido — decidir desde el inicio (no mezclar)
- [ ] JS: archivo separado o `<script>` al final del `<body>` — idem
- [ ] Variables CSS en `:root` para paleta y tipografía (no valores hardcodeados)
- [ ] Sin `import`/`export` de ES Modules a menos que uses `type="module"` en el script
- [ ] Dependencias externas via CDN (`jsdelivr`, `cdnjs`, `unpkg`)
- [ ] Cache busting manual con `?v=N` en scripts y CSS locales

### Orden de carga de scripts (obligatorio)

```html
<!-- 1. Librerías externas (CDN) -->
<script src="https://cdn.jsdelivr.net/..."></script>

<!-- 2. Config / variables globales -->
<script src="config.js?v=1"></script>

<!-- 3. Utilidades que dependen de config -->
<script src="utils.js?v=1"></script>
<script src="auth.js?v=1"></script>

<!-- 4. Lógica de UI / componentes -->
<script src="componentes.js?v=1"></script>

<!-- 5. Inicialización principal (siempre el último) -->
<script src="app.js?v=1"></script>
<!-- O inline si es pequeño -->
<script>
  document.addEventListener('DOMContentLoaded', () => { init(); });
</script>
```

> ⚠️ Un script que intenta acceder al DOM antes de que exista, o usar una función
> de otro script que aún no se ha cargado, es el bug de orden de carga más frecuente.
> Si usas `DOMContentLoaded` en todos los scripts de inicialización lo evitas.

### Vanilla JS multi-archivo (módulos separados por función)

El patrón más frecuente en proyectos grandes vanilla (JoGaSan, Orange Spark):
cada responsabilidad en su propio archivo JS, todos cargados desde el HTML.

```
proyecto/
├── index.html          ← orquestador: carga todos los scripts en orden
├── config.js           ← credenciales y constantes globales
├── auth.js             ← login/logout/sesión
├── utils.js            ← funciones reutilizables sin dependencias
├── [modulo-a].js       ← lógica específica del módulo A
├── [modulo-b].js       ← lógica específica del módulo B
└── app.js              ← inicialización principal (siempre el último)
```

**Regla de dependencias**: cada archivo solo puede usar funciones de archivos
cargados ANTES que él en el HTML. Nunca al revés.

**Convención de nombres para evitar colisiones entre módulos:**
```javascript
// En lugar de nombres genéricos que chocan:
function init() { ... }        // ❌ — cada módulo tiene su init()

// Usar prefijo del módulo:
function moduloA_init() { ... }  // ✅
function moduloB_init() { ... }  // ✅

// O mejor: IIFE que expone solo lo necesario
const ModuloA = (() => {
  function init() { ... }
  return { init };
})();
```

**Al clonar un multi-archivo**: verificar que el orden de `<script>` en el HTML
del clon es idéntico al del origen (salvo los scripts que se añadan o eliminen).

### Mobile-first desde el minuto cero

```css
/* CORRECTO: base mobile, añadir complejidad hacia arriba */
:root {
  --gap: 1rem;
  --cols: 1;
}
.grid { display: grid; grid-template-columns: repeat(var(--cols), 1fr); gap: var(--gap); }

@media (min-width: 768px) { :root { --cols: 2; } }
@media (min-width: 1024px) { :root { --cols: 3; --gap: 1.5rem; } }

/* INCORRECTO: base desktop, parchear hacia abajo */
.grid { display: grid; grid-template-columns: repeat(3, 1fr); }
@media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }
```

### Gestión de estado en vanilla

```javascript
// Estado centralizado (patrón recomendado para apps medianas)
const Estado = {
  usuario: null,
  datos: [],
  ui: { panelActivo: 'inicio', cargando: false },

  set(clave, valor) {
    this[clave] = valor;
    this._notificar(clave, valor);
  },
  _listeners: {},
  on(clave, fn) { (this._listeners[clave] ??= []).push(fn); },
  _notificar(clave, valor) { (this._listeners[clave] ?? []).forEach(fn => fn(valor)); }
};

// Uso:
Estado.on('usuario', u => renderizarNav(u));
Estado.set('usuario', { nombre: 'David', rol: 'admin' });
```

### Traducción desde otros stacks a vanilla

| Patrón origen | Equivalente vanilla |
|---|---|
| Componente React/Vue | Función que devuelve HTML string + `innerHTML` |
| Props | Parámetros de función |
| Estado (useState, ref) | Variable en closure o en objeto `Estado` global |
| useEffect / watch | `MutationObserver` o eventos custom |
| Router (React Router) | `location.hash` + listener `hashchange` |
| CSS Modules | Prefijos de clase manuales (`.mi-componente-btn`) |
| Context / Provide | Objeto global o patrón módulo (IIFE) |
| CSS-in-JS | Variables CSS en `:root` + clases semánticas |

---

## Stack destino: React (con Vite)

**Cuándo elegirlo:** Componentes reutilizables complejos, equipo, estado complejo,
ecosistema npm necesario.

### Checklist de arranque con Vite

```bash
npm create vite@latest nuevo-proyecto -- --template react
cd nuevo-proyecto
npm install
npm run dev
```

- [ ] `vite.config.js` revisado — `base` correcto para el hosting destino
- [ ] Variables de entorno en `.env` (prefijo `VITE_` para que sean accesibles en el cliente)
- [ ] `.gitignore` incluye `node_modules`, `dist`, `.env`
- [ ] `package.json` → `name` actualizado al nombre del clon (no del origen)

### Diferencias local vs producción en React+Vite

```javascript
// ⚠️ Rutas de assets: usar import, no strings hardcodeados
import logo from './assets/logo.svg';    // ✅ Vite gestiona la ruta
const logo = '/assets/logo.svg';         // ❌ puede romperse en producción

// Variables de entorno
const url = import.meta.env.VITE_API_URL;  // ✅
const url = process.env.REACT_APP_URL;     // ❌ esto es Create React App, no Vite
```

### Deploy de React+Vite en Netlify/Vercel

```bash
npm run build    # genera /dist
# Netlify: publish dir = dist, build command = npm run build
# Vercel: detecta Vite automáticamente
```

```toml
# netlify.toml mínimo para React SPA
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

---

## Stack destino: Vue 3 (con Vite)

**Cuándo elegirlo:** Similar a React, con preferencia por Options API o Composition API,
o cuando el origen es Vue y se mantiene el stack.

### Checklist de arranque con Vite

```bash
npm create vite@latest nuevo-proyecto -- --template vue
cd nuevo-proyecto
npm install
npm run dev
```

- [ ] `vite.config.js` → `base` correcto para el hosting
- [ ] Variables en `.env` con prefijo `VITE_`
- [ ] `package.json` → `name` actualizado

### Traducción React → Vue (referencia rápida)

| React | Vue 3 |
|---|---|
| `useState` | `ref()` / `reactive()` |
| `useEffect` | `watch()` / `onMounted()` |
| `props` | `defineProps()` |
| `children` | `<slot>` |
| `context` | `provide/inject` |
| React Router | Vue Router |
| Redux | Pinia |

### Deploy Vue+Vite

Idéntico a React+Vite — mismo `netlify.toml`, misma lógica de `dist`.

---

## Stack origen desconocido → destino vanilla

Cuando el origen es una web externa de stack incierto y el destino es vanilla:

1. **Ignorar el código del origen** — solo usar el resultado visual como referencia
2. **Aplicar el protocolo "esqueleto primero"** de la Fase 1C
3. **No intentar "traducir"** el código del origen línea a línea — reescribir desde el mapa de zonas
4. **Extraer solo:**
   - Paleta de colores (DevTools → inspector de estilos)
   - Tipografía (DevTools → Computed → font-family, font-size)
   - Estructura semántica (DevTools → Elements, copiar árbol HTML limpio)
   - Lógica de negocio (entender qué hace, reescribir en vanilla)

```javascript
// Herramienta rápida para extraer variables CSS de cualquier web en DevTools:
// Pegar en consola del navegador:
const vars = {};
[...document.styleSheets].forEach(sheet => {
  try {
    [...sheet.cssRules].forEach(rule => {
      if (rule.style) {
        [...rule.style].filter(p => p.startsWith('--')).forEach(p => {
          vars[p] = rule.style.getPropertyValue(p).trim();
        });
      }
    });
  } catch(e) {}
});
console.table(vars);
```

---

## Compatibilidad entre backends y stacks

| Backend | Vanilla JS | React | Vue |
|---|---|---|---|
| Supabase | `@supabase/supabase-js` via CDN o npm | npm | npm |
| Firebase | SDK via CDN (compat) o npm (modular) | npm modular | npm modular |
| API REST propia | `fetch()` nativo | `fetch()` o axios | `fetch()` o axios |
| GraphQL | `fetch()` manual | Apollo Client o urql | Apollo Client o urql |
| Sin backend | localStorage / IndexedDB | idem | idem |
