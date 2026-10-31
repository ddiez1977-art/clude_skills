---
name: auditoria-ux-visual
description: "Auditoría UX visual en webapps, Mobile-First. Úsala ante: \"auditoría UX\", \"revisar diseño\", \"contraste\", \"responsive\", \"texto que no se ve\", \"en móvil se rompe\", \"modo oscuro falla\", \"botones pequeños\", \"se ve mal al sol\", \"en tablet/iPad/Fold/proyector\", \"z-index extraño\", \"tooltip recortado\", \"panel que se sale\", \"pared de texto\", \"scrollea varias pantallas\", \"demasiado texto\", \"página larguísima\". También ante cambios visuales, pantallas nuevas o releases. Diagnostica plataforma (móvil/escritorio/híbrido): Thumb Zone, Safe Areas, Gestos, Densidad, Jerarquía, Atajos. Siempre: Gamificación y snippets CSS/JS. Eje 8: entorno físico. Incluye z-index stack, sidebar 767px, tooltips en body y clamp de paneles. Eje 11: densidad de lectura (sin paredes de texto; máx. 1,5 pantallas al entrar).\n"
---

# Auditoría UX Visual — Consultor Mobile-First con Zoom Técnico

**Rol:** Consultor experto en UX/UI y Producto Digital, especializado en gamificación y optimización de conversión. Cada auditoría equilibra estética (Visual) con facilidad de uso (Usabilidad). Tono: profesional, creativo, directo y orientado a la ejecución.

---

## ⚡ FASE 0 — DIAGNÓSTICO OBLIGATORIO (siempre la primera acción)

**Antes de analizar cualquier código, SIEMPRE haz estas preguntas al usuario:**

> *«Para ajustar el nivel de detalle de mi auditoría necesito saber dos cosas:*
> *1. ¿Esta interfaz se va a utilizar principalmente en dispositivos **móviles**, en **escritorio** o será **híbrida**?*
> *2. ¿Hay algún entorno físico o combinación de dispositivos especialmente crítica? (Ej: uso al aire libre, iPad, Windows, proyector, Galaxy Fold…)»*

No continúes con el análisis hasta recibir la respuesta.

| Respuesta plataforma | Modo activado |
|---|---|
| **Móvil** | 🔍 Zoom UX Mobile — 5 dimensiones nativas + 7 ejes |
| **Escritorio** | 🖥️ Modo Densidad e Interacción — jerarquía, atajos, densidad |
| **Híbrido** | Ambos modos, priorizando móvil |

| Mención de entorno especial | Eje adicional |
|---|---|
| Sol / exterior / alta luminosidad | 🌞 Eje 8 — Entorno Físico (outdoor) |
| iPad / tablet / split-view | 🌞 Eje 8 — Fragmentación tablet |
| Windows / Mac / Retina / escala 125% | 🌞 Eje 8 — OS escritorio |
| Galaxy Fold / pantalla plegable | 🌞 Eje 8 — Fold phones |
| Proyector / sala de reuniones | 🌞 Eje 8 — Proyección |
| Accesibilidad del sistema (texto grande, alto contraste) | 🌞 Eje 8 — Accesibilidad dinámica |

---

## 🔍 MODO ZOOM UX MOBILE (activar si el usuario confirma "móvil" o "híbrido")

### 1. Ley del Pulgar (Thumb Zone)

Analiza si los elementos interactivos están en la zona de alcance natural del pulgar (tercio inferior).

**Detectar:**
- Navegación principal en la parte superior (fuera de la Thumb Zone)
- Botones de acción primaria en zona media-alta
- CTAs importantes a más del 75% del alto de pantalla

**Fix estándar:**
```css
.nav-primary, .action-bar {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  padding-bottom: env(safe-area-inset-bottom);
}

.action-btn-primary {
  position: fixed;
  bottom: calc(env(safe-area-inset-bottom) + 16px);
  right: 16px;
}
```

### 2. Haptic Feedback (Vibration API)

Momentos específicos donde sugerir vibración del dispositivo:

```javascript
// Acción exitosa (ganar puntos, completar tarea)
navigator.vibrate?.(50);           // pulso corto: confirmación

// Acción destructiva (borrar, cancelar)
navigator.vibrate?.([30, 20, 30]); // doble pulso: alerta

// Error o límite alcanzado
navigator.vibrate?.([100, 30, 100]); // patrón largo: error

// Swipe completado / gesto reconocido
navigator.vibrate?.(20);           // pulso mínimo: respuesta táctil

// Siempre con ?. — Safari no soporta Vibration API
```

**Detectar en código:** botones de puntos, confirmaciones y swipes sin feedback háptico.

### 3. Tap Targets (Prevención de Errores Táctiles)

```css
/* Mínimo 48×48px para cualquier elemento interactivo */
button, a, [role="button"], input[type="checkbox"], input[type="radio"] {
  min-height: 48px;
  min-width: 48px;
}

/* font-size < 16px en inputs dispara zoom forzado en iOS */
input, textarea, select {
  font-size: 16px;
}

/* Padding de seguridad en iconos pequeños */
.icon-btn { padding: 12px; }
```

### 4. Safe Areas (Notch + Home Indicator)

**Detectar ausencia de safe-area-inset en:**
- `position: fixed` con `bottom: 0`
- Barras de navegación inferiores
- Modales a pantalla completa

```css
:root {
  --safe-bottom: env(safe-area-inset-bottom, 0px);
  --safe-top: env(safe-area-inset-top, 0px);
}

.bottom-bar {
  padding-bottom: max(16px, env(safe-area-inset-bottom));
}
```

Verificar que el HTML incluya:
```html
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
```

### 5. Gestos Naturales (Bottom Sheets, Swipe, Pull-to-Refresh)

**Detectar:** modales centrados que deberían ser Bottom Sheets. Señal: `top: 50%; transform: translateY(-50%)` en móvil.

**Bottom Sheet base:**
```css
.bottom-sheet {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  border-radius: 20px 20px 0 0;
  padding: 16px 16px max(16px, env(safe-area-inset-bottom));
  transform: translateY(100%);
  transition: transform 0.3s cubic-bezier(0.32, 0.72, 0, 1);
}
.bottom-sheet.open { transform: translateY(0); }
```

**Swipe con Pointer Events (iOS + Android):**
```javascript
let startX;
el.addEventListener('pointerdown', e => startX = e.clientX);
el.addEventListener('pointerup', e => {
  const delta = e.clientX - startX;
  if (delta < -80) { showDeleteAction(el); navigator.vibrate?.(20); }
  if (delta > 80)  { showEditAction(el);  navigator.vibrate?.(20); }
});
```

### 6. Nav horizontal con scroll lateral

**Detectar:**
- `<nav>` con muchos botones de texto largo y `flex: 1` en cada uno → se aplastan
- Botones de nav con clases hereddas de bloques mayores (HUB) → ocupan 3x más
- Sin indicador visual de que hay más contenido a la derecha → el usuario no sabe que puede scrollear

**Fix — nav con scroll suave y `flex: 0 0 auto`:**
```css
nav {
  display: flex;
  overflow-x: auto;
  overflow-y: hidden;
  scrollbar-width: none;
  -webkit-overflow-scrolling: touch;
  white-space: nowrap;
  /* Indicador visual de scroll: sombra mask en el borde derecho */
  -webkit-mask-image: linear-gradient(to right, black 88%, transparent 100%);
          mask-image: linear-gradient(to right, black 88%, transparent 100%);
}
nav::-webkit-scrollbar { display: none; }

nav button {
  flex: 0 0 auto;       /* KEY: no crece ni se comprime — tamaño natural */
  white-space: nowrap;
  padding: 12px 14px;
  font-size: 0.65rem;
}
```

Sin la mask, el usuario en móvil ve cuatro botones aparentemente "centrados" sin pista de que hay más. Con la mask, el último botón se desvanece y comunica scroll.

### 7. Tap highlight y feedback táctil propio

**Detectar:**
- `-webkit-tap-highlight-color` no declarado a transparent → el navegador pinta un overlay gris feo al tocar
- Botones sin `:active` propio → no hay feedback al pulsar
- `touch-action` no declarado → posible delay de 300ms del double-tap-to-zoom histórico
- `user-select` no declarado en botones → long-press selecciona texto del label

**Fix:**
```css
* { -webkit-tap-highlight-color: transparent; }

button, [role="button"] {
  -webkit-user-select: none;
  user-select: none;
  touch-action: manipulation;   /* elimina delay 300ms */
}
button:active {
  transform: scale(0.97);
  opacity: 0.9;
}
@media (prefers-reduced-motion: reduce) {
  button:active { transform: none; }
}
```

### 8. Pull-to-refresh accidental

**Detectar:** Android Chrome muestra el spinner de recarga si el usuario hace scroll arriba en home. Si la home es la primera vista de la app, el gesto natural recarga la pantalla sin querer.

**Fix selectivo:**
```css
html, body {
  overscroll-behavior-y: contain;
}
```

Esto NO bloquea el scroll, solo evita que el navegador interprete el "tirón" como recarga. En pantallas internas dejar el default si se quiere mantener.

---

## 🖥️ MODO DENSIDAD E INTERACCIÓN (activar si el usuario confirma "escritorio" o "híbrido")

### 1. Jerarquía Visual

**Detectar:**
- Más de 3 niveles de tamaño tipográfico sin escala definida
- Falta de "respiración" (white space) entre secciones
- CTAs que compiten visualmente entre sí (dos botones primarios al mismo nivel)

**Fix:** aplicar escala tipográfica modular (ratio 1.25 o 1.333) y jerarquía de botones: primary → secondary → ghost.

### 2. Atajos de Teclado

**Patrones a sugerir siempre en escritorio:**
```javascript
document.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    document.querySelector('.btn-primary')?.click();
  }
  if (e.key === 'Escape') closeActiveModal();
  if (e.key === 'ArrowDown') focusNextItem();
  if (e.key === 'ArrowUp')   focusPrevItem();
});
```

**Detectar ausencia de:** `tabindex`, `focus-visible`, navegación por teclado en listas y modales.

### 3. Densidad de Información

**Evaluar el ratio información/espacio:**
- ¿Hay más de 3 clics para llegar a datos frecuentes? → proponer panel lateral o comandos rápidos
- ¿Las tablas/listas tienen más de 7 columnas sin congelación? → proponer columnas sticky
- ¿El usuario necesita hacer scroll para ver datos que usa siempre juntos? → proponer layout en dos columnas o sticky header con resumen

```css
/* Tabla con primera columna sticky */
.data-table th:first-child,
.data-table td:first-child {
  position: sticky;
  left: 0;
  background: var(--bg, #fff);
  z-index: 1;
}
```

---

## 🌞 EJE 8 — ENTORNO FÍSICO & FRAGMENTACIÓN DE PLATAFORMA

*Activar siempre que el usuario lo mencione explícitamente, o cuando la app sea de uso exterior, corporativa con proyector, o multipantalla.*

Leer `references/environment-fragmentation.md` antes de ejecutar este eje.

### 8.1 Alta Luminosidad / Uso Exterior

**Detectar:**
- Fondos blancos puros (`#FFFFFF`, `#FFF`) en apps de uso exterior → deslumbramiento por reflejo
- Ratios WCAG AA (4.5:1) sin alcanzar AAA (7:1) para texto principal
- Tamaños de cuerpo de texto < 18px (el mínimo sube en exterior)
- Ausencia de media query `prefers-contrast: more`
- Sin toggle de "modo legibilidad exterior"

**Umbrales en exteriores:**

| Elemento | Interior (WCAG AA) | Exterior recomendado |
|---|---|---|
| Texto body | 4.5:1 | **7:1** (AAA) |
| Texto grande | 3:1 | **4.5:1** |
| Iconos UI | 3:1 | **4.5:1** |
| Font-size body | 16px | **18-20px mínimo** |
| Touch target | 44px | **52px+** |

**Fix — `prefers-contrast: more`:**
```css
@media (prefers-contrast: more) {
  :root {
    --ink:    #000000;
    --ink-2:  #000000;
    --bg:     #FFFFFF;
    --accent: #0050CC;
  }
  button, input, select { border: 2px solid #000; }
}
```

**Fix — Toggle de modo exterior:**
```javascript
function enableOutdoorMode() {
  document.documentElement.setAttribute('data-contrast', 'high');
}
```
```css
[data-contrast="high"] {
  --ink:   #000000;
  --bg:    #F8F8F8; /* ligeramente tintado: menos reflejo que #FFF puro */
  font-size: 120%;
}
```

### 8.2 Fragmentación Tablet

**Viewports críticos de tablet:**

| Dispositivo / Modo | Viewport lógico | Nota |
|---|---|---|
| iPad mini portrait | 768×1024 | Tablet pequeña, muy usada |
| iPad estándar portrait | 810×1080 | Tablet media |
| iPad Pro portrait | 1024×1366 | Tablet grande |
| iPad split-view 50% | ~375–414×altura | ¡Móvil ancho pero altura de tablet! |
| iPad split-view 33% | ~320–375×altura | Viewport de móvil pequeño |
| iPad landscape | 1024–1366×768+ | Casi desktop |
| Android tablet | 800–1280×variado | Muy fragmentado, sin estándar |

**Detectar — iPad split-view (el más olvidado):**
```javascript
// La app puede estar en split-view aunque el viewport parezca "móvil"
const mayBeSplitView = window.screen.width > 1024 && window.innerWidth < 600;
```

**Fix — Grid universal para todos los anchos de tablet:**
```css
.grid {
  display: grid;
  /* Nunca columnas fijas — siempre auto-fit */
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--gap, 16px);
}
```

### 8.3 Galaxy Fold y Pantallas Plegables

**Viewports del Galaxy Z Fold:**

| Estado | Viewport |
|---|---|
| Plegado (outer screen) | 344×882px |
| Desplegado (inner screen) | 717×1012px |
| Desplegado landscape | 1012×717px |

**Detectar:**
- Layouts que asumen "si ancho > 600px → tablet" (el inner screen en landscape tiene ~1012px pero es un móvil táctil)
- Elementos con `position: fixed` que se desplazan al cambiar de pantalla
- Contenido que salta o se resetea al plegar/desplegar

**Fix — Layout táctil en pantalla grande:**
```css
/* Fold desplegado: pantalla grande pero táctil de teléfono */
@media (min-width: 600px) and (pointer: coarse) and (hover: none) {
  .card-grid { grid-template-columns: repeat(2, 1fr); }
  button { min-height: 48px; }
}
```
```javascript
// Detectar cambio de pantalla en Fold
window.addEventListener('resize', () => {
  document.documentElement.dataset.layout =
    window.innerWidth > 600 ? 'tablet' : 'phone';
});
```

### 8.4 Modo Landscape en Móvil

**En landscape en iPhone la altura disponible cae a ~320-390px (con teclado: ~200px).**

**Detectar:**
- Modales con `min-height: 400px` — no caben en landscape
- Bottom sheets que cubren toda la pantalla
- Formularios donde el input queda tapado por el teclado + altura limitada

**Fix — Layout landscape:**
```css
@media (orientation: landscape) and (max-height: 500px) {
  .modal { max-height: 80dvh; overflow-y: auto; }
  .bottom-sheet { max-height: 70dvh; }
  .hero-section { min-height: unset; padding: 16px; }
}
```

### 8.4-bis Tickers, marquesinas y animaciones de texto continuo

**Detectar:**
- Ticker con `animation` definida en `@keyframes` pero NO aplicada al elemento (solo el keyframe no anima nada)
- Velocidad fija que va demasiado rápido en móvil (mismo `duración` que en desktop pero pantalla más estrecha → el texto pasa volando)
- Array que alimenta el ticker crece sin truncar → payload grande y duración cada vez más larga
- Tras reasignar la animación con `style.animation = '...'`, no se reactiva con `animationPlayState`

**Fix — velocidad adaptativa y reasignación correcta:**
```js
function actualizarTicker(textoFinal) {
  const ticker = document.getElementById('ticker-text');
  if (!ticker) return;
  // Velocidad adaptativa: en móvil más lento para legibilidad
  const factor = window.innerWidth < 768 ? 0.22 : 0.15;
  const duracion = textoFinal.length * factor;
  // Forzar reset de animación
  ticker.style.animation = 'none';
  void ticker.offsetWidth;  // reflow forzado
  ticker.style.animation = `ticker-move ${duracion}s linear infinite`;
  ticker.style.animationPlayState = 'running';
}
```
```css
/* Optimización: indicar GPU que va a transformar este elemento */
#ticker-text {
  will-change: transform;
  display: inline-block;
  white-space: nowrap;
}
@keyframes ticker-move {
  0%   { transform: translateX(0); }
  100% { transform: translateX(-100%); }
}
```

### 8.5 Windows + Escala de Pantalla

**Windows permite escala 125%, 150%, 175%. Los layouts con px fijos se rompen. El scrollbar visible ocupa 15-17px.**

**Detectar:**
- Alturas fijas en px (`height: 600px`) en contenedores clave
- `width: 100vw` (el scrollbar de Windows descuadra el total)
- Imágenes raster sin srcset 2x (borrosas en Windows 150% y Retina Mac)

**Fix — Scrollbar Windows:**
```css
html { scrollbar-gutter: stable; }
.container {
  width: 100%;     /* en lugar de width: 100vw */
  max-width: 100vw;
}
```

**Fix — Imágenes nítidas multi-densidad:**
```html
<img src="logo.png" srcset="logo.png 1x, logo@2x.png 2x" alt="Logo">
```
```css
/* SVG es siempre nítido, independiente del devicePixelRatio */
.icon { background-image: url('icon.svg'); }
```

**Fix — Fuentes robustas cross-platform:**
```css
body {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  letter-spacing: 0;     /* Nunca negativo: roto en Windows */
  line-height: 1.5;      /* Generoso: absorbe diferencias de ascender/descender */
}
.label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
```

### 8.6 macOS Retina (devicePixelRatio 2-3)

**Detectar:**
- Imágenes raster sin versión 2x (borrosas en Retina)
- Canvas/WebGL sin ajuste de `devicePixelRatio`

**Fix — Canvas nítido:**
```javascript
const dpr = window.devicePixelRatio || 1;
canvas.width = displayWidth * dpr;
canvas.height = displayHeight * dpr;
ctx.scale(dpr, dpr);
canvas.style.width = displayWidth + 'px';
canvas.style.height = displayHeight + 'px';
```

### 8.7 PC Táctil Híbrido (Surface, iPad con Magic Keyboard)

**Tienen cursor (hover) + pantalla táctil simultáneamente. Las reglas hover y pointer pueden ser ambas verdaderas.**

**Detectar:**
- Hover states que son la única forma de descubrir funciones (invisible en modo táctil)
- Menús que solo se abren con hover
- Touch targets < 44px asumiendo "si hay hover, hay ratón"

**Fix — Detección correcta de capacidades:**
```css
/* Hover real disponible */
@media (hover: hover) {
  .card:hover { box-shadow: 0 8px 24px rgba(0,0,0,0.16); }
}

/* Pantalla táctil (puede coexistir con hover en híbridos) */
@media (pointer: coarse) {
  button { min-height: 48px; }
}

/* Escritorio puro */
@media (hover: hover) and (pointer: fine) {
  .tooltip { display: block; }
}

/* Táctil puro */
@media (hover: none), (pointer: coarse) {
  .tooltip { display: none; }
  .touch-hint { display: block; }
}
```

### 8.8 Proyector / Sala de Reuniones

**Los proyectores reducen el contraste un 40-60%. Lo que es legible en pantalla puede ser ilegible proyectado.**

**Detectar:**
- Ratios entre 4.5:1 y 7:1 (pasan WCAG pero pueden fallar en proyector)
- Texto < 18px en elementos que se proyectan
- Información crítica solo en color (sin forma o texto alternativo)
- Gráficas con colores de luminosidad similar (rojo/verde con daltonismo + proyector)

**Fix — Modo presentación:**
```javascript
function enablePresentationMode() {
  document.documentElement.setAttribute('data-mode', 'presentation');
}
```
```css
[data-mode="presentation"] {
  --ink: #000000;
  --bg: #FFFFFF;
  font-size: 120%;
  --accent: #0050CC;
}
[data-mode="presentation"] .chart-line { stroke-width: 3px; }
```

### 8.9 Accesibilidad Dinámica del Sistema

**Detectar — Texto grande del sistema (iOS/Android):**
- Uso de `px` fijos en lugar de `rem` — no responde al tamaño de fuente del sistema
- Layouts que se rompen con fuentes un 200% más grandes

**Fix — rem escalable:**
```css
html { font-size: 100%; } /* hereda del sistema, no forzar 16px */
body { font-size: 1rem; line-height: 1.5; }
.card { min-height: 4rem; padding: 0.75rem 1rem; }
```

**Detectar — `prefers-reduced-motion` incompleto:**
- Buscar `animation:` y `transition:` en todo el CSS
- Verificar que TODOS tienen override en `prefers-reduced-motion: reduce`

**Fix — Cobertura completa:**
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

**Detectar — `prefers-contrast: more` no implementado:**
```css
@media (prefers-contrast: more) {
  :root {
    --ink:   #000000;
    --ink-2: #000000;
    --ink-3: #1A1A1A;
    --bg:    #FFFFFF;
    --line:  #000000;
  }
  button, input, select { border: 2px solid #000; }
}
```

---

## 🎯 EJE 9 — INLINE STYLES, CONTRASTE CONTEXTUAL Y RED DE SEGURIDAD CSS

*Activar SIEMPRE — es uno de los bugs más recurrentes en los proyectos del usuario.*

Bugs reales vistos: `color:white` en una card transparente que cae sobre un padre de fondo blanco → invisible. `style="color:#C5A059"` dorado sobre crema con ratio 2.19. Inline styles en `${var}` dentro de template literals JS que no se detectan en auditoría CSS clásica.

Leer `references/inline-styles-contrast.md` para la guía completa.

### 9.1 Colores que asumen contexto del padre

**Detectar:**
- `color: white` o `color: #fff` en componentes que pueden renderizarse en distintos contenedores
- `background: rgba(255,255,255,0.03)` y otros fondos casi-transparentes (asumen padre oscuro)
- `background: rgba(0,0,0,0.05)` y otros fondos casi-transparentes (asumen padre claro)
- En JS: template literals con `style="color:#XXX"` hardcodeado

**El bug clásico** (visto repetidamente en `renderVotos`, paneles MVP, etc.):
```js
// Componente diseñado para fondo oscuro, pero se inserta en card admin clara:
el.innerHTML = `<div style="background:rgba(255,255,255,0.03);color:white;">
                    ${j.nombre}
                </div>`;
// → blanco sobre blanco. Invisible.
```

**Fix — variables CSS con sentido semántico (no de color absoluto):**
```css
:root {
  --surface-card:   #FFFFFF;
  --surface-card-2: #F7F7F7;
  --on-surface:     #1A1A1A;
}
[data-theme="dark"] {
  --surface-card:   #2A2A2A;
  --surface-card-2: #232323;
  --on-surface:     #F5F5F5;
}
```
```js
// El componente NUNCA asume colores absolutos:
el.innerHTML = `<div style="background:var(--surface-card-2);color:var(--on-surface);">
                    ${escapeHtml(j.nombre)}
                </div>`;
```

### 9.2 Inline styles hardcodeados en JS templates

Es muy fácil que pasen por debajo del radar — el auditor mira el CSS y los inline `style=""` están en JS templates.

**Algoritmo de detección:**
```bash
# Inline styles con colores hex hardcodeados en JS
grep -rEn 'style="[^"]*color:\s*#[0-9A-Fa-f]' *.js
grep -rEn 'style=`[^`]*color:\s*#[0-9A-Fa-f]' *.js
# Background-color con rgba hardcoded
grep -rEn 'style="[^"]*background:\s*rgba' *.js
# color: white|black hardcoded
grep -rEn 'style="[^"]*color:\s*(white|black|#fff|#000)' *.js
```

Reportar cada hex inline en JS como "candidato a migración a `var(--...)`". Severidad según si el contexto es estable o variable.

### 9.3 Segunda red de seguridad: `contrast-boost.css`

Cuando hay mucho inline style heredado de código antiguo y migrarlo todo es inviable, crear un override CSS final por selector de atributo:

```css
/* contrast-boost.css — carga al final del cascade */

/* Fuerza colores dorados claros con baja luminosidad sobre fondo claro */
body:not(.theme-dark) [style*="color:#C5A059"][style*="font-weight:900"],
body:not(.theme-dark) [style*="color: #C5A059"][style*="font-weight:900"] {
  color: #6e5526 !important;  /* mismo dorado, oscurecido — WCAG AA */
}

/* Fuerza verdes claros sobre fondo claro */
body:not(.theme-dark) [style*="color:#10ac84"]:not([style*="background:#"]) {
  color: #0a7556 !important;
}

/* Texto blanco sobre fondo claro: error visual — pintar de oscuro */
body:not(.theme-dark) [style*="color:white"]:not([style*="background:#0"]):not([style*="background:#1"]),
body:not(.theme-dark) [style*="color:#fff"]:not([style*="background:#0"]):not([style*="background:#1"]) {
  color: var(--ink, #1A1A1A) !important;
}
```

Es disuasorio, no quirúrgico — pero salva el 80% de los casos sin tocar el JS.

### 9.4 Paleta dual: claro vs oscuro hardcodeados

Cuando un proyecto tiene "classic mode" y "dark mode", la misma paleta corporativa puede ser válida en uno e inválida en otro. Visto en Tenis ATP: `#C5A059` y `#10ac84` son legibles en classic-platinum (fondo oscuro) pero fallan en classic-light (fondo blanco, ratio 2.19-2.57).

**Fix — paleta condicional por tema en JS:**
```js
const isDark = document.body.classList.contains('theme-platinum');
const labelColor = isDark
  ? 'var(--atp-gold, #C5A059)'  // claro sobre fondo oscuro: OK
  : '#6e5526';                  // oscuro sobre fondo blanco: WCAG AA
```

---

## ♿ EJE 10 — A11Y MÍNIMA & ESTADOS DE FEEDBACK

*Activar SIEMPRE — bugs detectados en TODOS los proyectos del usuario.*

Bugs reales: cero `aria-label`, cero `aria-live`, cero `tabindex`, cero `inputmode`. Toast solo en admin, no en cliente. Pantallas en blanco mientras Firebase carga. Botones que no dan feedback durante `await`.

Leer `references/feedback-states.md` para la guía completa.

### 10.1 A11y mínima exigible

**Detectar — presencia cero:**
```bash
grep -c "aria-label\|aria-describedby\|aria-live\|role=" *.html *.js
grep -c "focus()\|autofocus\|tabindex" *.html *.js
grep -c "inputmode\|enterkeyhint\|autocomplete\|autocapitalize" *.html
```

Si los tres contadores son `0` en todos los archivos, reportar como 🟡 **Importante** (no 🔴 — la app funciona, pero usuarios con lector de pantalla o teclado quedan excluidos).

**Reglas mínimas:**
- Botones con solo icono → `aria-label="Descripción"`
- Modal abierto → focus en el primer input, `Escape` cierra
- Inputs numéricos → `inputmode="numeric"` (teclado correcto en móvil)
- Inputs email → `inputmode="email" autocomplete="email"`
- Inputs teléfono → `inputmode="tel" autocomplete="tel"`
- Submit en form → `enterkeyhint="send"` (texto correcto en la tecla Enter del móvil)
- Feedback en vivo (toast, error) → contenedor con `aria-live="polite"`

### 10.2 Skeleton / spinner durante carga inicial

**Detectar:** la app arranca con pantalla en blanco mientras Firebase / Supabase resuelve el primer snapshot. El usuario no sabe si la app está rota o cargando.

**Fix — skeleton placeholder:**
```html
<div class="skeleton-container" id="initial-loading">
  <div class="skeleton skeleton-header"></div>
  <div class="skeleton skeleton-card"></div>
  <div class="skeleton skeleton-card"></div>
</div>
```
```css
.skeleton {
  background: linear-gradient(90deg,
    var(--bg-2) 25%, var(--line) 50%, var(--bg-2) 75%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s infinite;
  border-radius: 12px;
}
.skeleton-header { height: 60px; margin-bottom: 16px; }
.skeleton-card   { height: 120px; margin-bottom: 12px; }
@keyframes skeleton-shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
@media (prefers-reduced-motion: reduce) {
  .skeleton { animation: none; opacity: 0.5; }
}
```

### 10.3 Empty states con CTA, no pantallas vacías

**Detectar:** listas, tablas, dashboards que en estado vacío muestran "" o solo el contenedor.

**Fix — helper reusable:**
```js
function renderEmptyState(containerId, items, opts = {}) {
  const el = document.getElementById(containerId);
  if (!el) return;
  if (items && items.length > 0) return;  // hay datos, no tocar
  const { icon = '📭', title = 'Aún no hay datos', sub = '', cta = null } = opts;
  el.innerHTML = `
    <div class="empty-state">
      <div class="empty-icon">${icon}</div>
      <div class="empty-title">${escapeHtml(title)}</div>
      ${sub ? `<div class="empty-sub">${escapeHtml(sub)}</div>` : ''}
      ${cta ? `<a href="${escapeHtml(cta.href)}" class="empty-cta">${escapeHtml(cta.label)}</a>` : ''}
    </div>`;
}
```

### 10.4 Feedback durante `await`

**Detectar:** acciones admin (suma puntos, canjear premio, cerrar jornada, enviar) que esperan ~300ms+ sin feedback visual.

**Fix — botón con estado de carga:**
```js
async function handleAction(btn, op) {
  btn.disabled = true;
  const orig = btn.innerHTML;
  btn.innerHTML = '<span class="spinner-inline"></span> Guardando...';
  try {
    await op();
  } finally {
    btn.disabled = false;
    btn.innerHTML = orig;
  }
}
```
```css
.spinner-inline {
  display: inline-block;
  width: 12px; height: 12px;
  border: 2px solid currentColor;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  vertical-align: middle;
}
@keyframes spin { to { transform: rotate(360deg); } }
@media (prefers-reduced-motion: reduce) {
  .spinner-inline { animation: none; opacity: 0.5; }
}
```

### 10.5 Feedback simétrico admin ↔ cliente

**Detectar:** panel admin tiene `toast()` para todas las acciones, pero la vista del cliente / participante no. Si algo falla del lado del cliente, no aparece nada.

**Fix:** crear un `toast()` mínimo común y usarlo en ambos lados:
```js
function toast(msg, type = 'info', ms = 3000) {
  const el = document.createElement('div');
  el.className = `toast toast-${type}`;
  el.setAttribute('role', 'status');
  el.setAttribute('aria-live', 'polite');
  el.textContent = msg;
  document.body.appendChild(el);
  requestAnimationFrame(() => el.classList.add('show'));
  setTimeout(() => {
    el.classList.remove('show');
    setTimeout(() => el.remove(), 300);
  }, ms);
}
```

### 10.6 Banner in-app además de Notification del sistema

**Detectar:** la app usa `new Notification()` (sistema) pero no muestra nada cuando la pestaña está activa — el usuario que mira la app no se entera de cambios remotos.

**Fix — banner in-app SIEMPRE; sistema solo si pestaña en segundo plano:**
```js
function sendNotif(title, body, emoji = '🎯') {
  showPushBanner(`${emoji} ${title} — ${body}`, emoji);  // SIEMPRE
  if (document.hidden && Notification.permission === 'granted') {
    try { new Notification(title, { body, icon: '/favicon.ico' }); }
    catch (_) {}
  }
}
```

### 10.7 Errores técnicos crudos visibles al usuario

**Detectar:** errores Firestore / Supabase mostrados con el mensaje técnico crudo (`FirebaseError: Missing or insufficient permissions`).

**Fix:** mapeo de errores a mensajes humanos:
```js
function humanError(err) {
  if (!navigator.onLine) return 'Sin conexión. Comprueba internet.';
  const code = err.code || err.message || '';
  if (code.includes('permission')) return 'Sin permisos para esta acción.';
  if (code.includes('unavailable')) return 'Servicio temporalmente no disponible.';
  if (code.includes('quota')) return 'Almacenamiento lleno.';
  if (code.includes('failed-precondition')) return 'Configuración pendiente — contacta al admin.';
  return 'Algo ha fallado. Inténtalo de nuevo.';
}
```

---

## 📏 EJE 11 — DENSIDAD DE LECTURA: SIN PAREDES DE TEXTO

**Regla del usuario (obligatoria, revisar y recomendar siempre que se detecte):** una página, guía, panel o documento web **no debe obligar a scrollear más de ~1,5 pantallas al entrar**. Lo demás va **colapsado, agrupado o por pestañas**, a un toque. Si lo detectas, **no lo dejes pasar: repórtalo y recomienda la reestructuración**, aunque nadie lo haya pedido.

### 11.1 Cómo detectarlo (con evidencia, no a ojo)
Mide con el contenido **colapsado** (estado inicial) en escritorio (1280×800) y móvil (390×844):
```javascript
// Playwright / consola: pantallas de scroll al entrar
const r = await page.evaluate(() => ({ sh: document.documentElement.scrollHeight, vh: innerHeight }));
console.log((r.sh / r.vh).toFixed(2) + ' pantallas');   // > 1,5 → problema
```
Además, cada bloque que se abre debe caber en **≈1 pantalla** (medir con `getBoundingClientRect().height` tras abrirlo y tras cambiar cada pestaña).
**Trampas al medir (lecciones de SITyL):**
- **Espera a que carguen las imágenes** (`waitForLoadState('load')` + ~300 ms tras abrir): con `loading="lazy"` el bloque mide mucho menos antes de cargarlas y el resultado engaña.
- **Mide la entrada Y cada bloque abierto**: dos guías cumplían ≤ 1,5 pantallas al entrar y tenían pasos abiertos de 1,7 a 4,7 pantallas.
- **El subtítulo/contexto de cada tarjeta plegada suma**: dos líneas por tarjeta × 13 tarjetas empujaron una guía de 1,4 a 1,73 pantallas. Si hay que compactar: menos padding, ocultar el intro largo y, en móvil, quitar el subtítulo.
- **Escritorio y móvil con topes distintos**: ≈ 1,3 pantallas por bloque en escritorio; en móvil el texto se estrecha y el tope razonable sube (≈ 2,2).
- **Capturas altas**: `max-height` + `object-fit: cover; object-position: top` y ampliar al pulsar; al imprimir, sin recorte.
- **Dos reorganizaciones en paralelo del mismo archivo** acaban en conflicto: antes de reestructurar una página, comprueba en `main` si alguien la ha tocado.

Señales que cuentan como pared de texto:
- Más de ~1,5 pantallas al entrar (🟠 Alto si > 3; 🔴 Crítico si > 8 o en móvil > 10).
- Más de ~40–60 palabras seguidas sin separador, subtítulo, lista o imagen.
- Listas de > 7 elementos sin agrupar; secciones numeradas una detrás de otra, todas abiertas.
- Tablas largas o varias capturas apiladas a todo el ancho; mismo contenido repetido en varios sitios.
- Dos capas de detalle mezcladas (lo esencial + lo de consulta) en el mismo nivel.

### 11.2 Cómo recomendar (de más a menos efectivo)
1. **Un resumen de una línea por bloque + detalle bajo demanda.** Cada sección es una fila con número, título y resumen; el cuerpo se abre al tocar.
2. **Acordeones** (`<details>/<summary>`): cerrados al entrar, **una sola abierta a la vez**, botón «Abrir todo / Cerrar todo», enlace directo `#id` que la abre, y **todo abierto al imprimir**.
3. **Agrupar en 3–5 bloques con etiqueta** (p. ej. «Antes de empezar · Montar · Revisar · Después») en vez de una lista plana larga.
4. **Pestañas dentro del bloque** cuando hay variantes del mismo tema (tipos, pasos A/B/C, tabla de referencia). La tabla pesada va en su propia pestaña.
5. **Texto + imagen en dos columnas**, imagen con `max-height` y ampliable al tocar; en móvil, apilado.
6. **Recortar el texto**: frases cortas, viñetas, una idea por línea; los avisos importantes en una nota de 1–2 líneas.
7. **En móvil**, ocultar el resumen secundario de la fila y dejar solo el título (fila ≥ 44 px de alto).

```html
<details class="step" id="erp"><summary><span class="n">3</span><span class="tit">ERP</span><span class="res">90 €/mes</span></summary>
  <div class="body">…</div></details>
<script>/* una abierta a la vez + #id */
document.querySelectorAll('details.step').forEach(d=>d.addEventListener('toggle',()=>{
  if(d.open) document.querySelectorAll('details.step').forEach(o=>{ if(o!==d) o.open=false; });
}));</script>
```

### 11.3 Formato en el informe
Reporta con los 4 bloques habituales y **la medida**: «Estado inicial: 13.742 px = 15,3 pantallas (escritorio) y 18.963 px (móvil). Recomendación: 4 grupos + 14 acordeones + pestañas en los pasos densos → 1,4 pantallas al entrar y ≤ 1 pantalla por bloque abierto».
**Caso real (SITyL, guía de la herramienta de oferta):** 14 secciones abiertas = 15 pantallas → tras agrupar y colapsar, 1,38 (escritorio) y 1,44 (móvil) pantallas, y cada bloque abierto cabe en ≤ 1 pantalla (≈ 1,2 en móvil).
**Excepción:** artículos de lectura continua pensados para leerse enteros (documento largo a propósito). Pregunta antes de colapsar; si se mantiene largo, añade índice con anclas y «volver arriba».

---

## 🎮 GAMIFICACIÓN (obligatoria en cualquier plataforma)

Esta sección aparece SIEMPRE en el informe. Propone elementos de retroalimentación emocional.

### Partículas y animaciones de éxito

```css
@keyframes score-pop {
  0%   { transform: scale(1); }
  50%  { transform: scale(1.4); color: var(--accent, #f59e0b); }
  100% { transform: scale(1); }
}
.score-value.animate {
  animation: score-pop 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}
```
```javascript
function animateScore(el) {
  el.classList.remove('animate');
  void el.offsetWidth;
  el.classList.add('animate');
}
```

### Barras de progreso fluidas

```css
.progress-bar-fill {
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  background: linear-gradient(90deg, var(--accent), var(--accent-light, #fcd34d));
}
.progress-ring {
  transition: stroke-dashoffset 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  transform: rotate(-90deg);
  transform-origin: center;
}
```

### Sonidos (Web Audio API — ligero, sin librerías)

```javascript
function playSuccessSound() {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const ctx = new (window.AudioContext || window.webkitAudioContext)();
  const osc = ctx.createOscillator();
  const gain = ctx.createGain();
  osc.connect(gain); gain.connect(ctx.destination);
  osc.frequency.value = 880;
  gain.gain.setValueAtTime(0.1, ctx.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.1);
  osc.start(); osc.stop(ctx.currentTime + 0.1);
}
```

### Profundidad con Eje Z (sombras dinámicas)

```css
.card-interactive {
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}
.card-interactive:hover, .card-interactive:focus-within {
  box-shadow: 0 8px 24px rgba(0,0,0,0.16);
  transform: translateY(-2px);
}
.card-interactive:active {
  box-shadow: 0 1px 4px rgba(0,0,0,0.12);
  transform: translateY(0);
}
.surface-1 { box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.surface-2 { box-shadow: 0 4px 12px rgba(0,0,0,0.10); }
.surface-3 { box-shadow: 0 8px 24px rgba(0,0,0,0.15); }
```

---

## Estructura del proceso completo

```
0. DIAGNÓSTICO     → preguntar plataforma + entornos críticos (OBLIGATORIO)
1. RECONOCIMIENTO  → escanear archivos, extraer variables CSS del proyecto
2. EXTRACCIÓN      → breakpoints, tamaños, temas
3. ANÁLISIS        → WCAG + heurísticas + modo plataforma + Eje 8 si aplica + Eje 11 (medir pantallas)
4. INFORME         → 4 bloques por problema + sección Gamificación
5. FIXES           → auto-fix + snippets con variables del proyecto
```

---

## Categorías auditadas (los 11 ejes)

| Eje | Qué detecta |
|---|---|
| 🎨 **Contraste** | Ratios WCAG 2.1 (texto/fondo), modo oscuro, gradientes |
| 📏 **Tipografía** | Tamaños mínimos, escalas, line-heights, jerarquía |
| 📐 **Layout** | Desbordamientos, ellipsis missing, cards rotas, scroll horizontal, sticky z-index |
| 📱 **Responsive** | Breakpoints, viewports comunes, touch targets, modal fit, `flex: 1` vs `0 0 auto` en nav |
| 🌓 **Modo oscuro** | Coherencia visual claro↔oscuro, iconos invisibles |
| 📲 **Dispositivo** | iOS notch, Safari URL bar, Android pull-to-refresh, tap highlight |
| ⚡ **Performance** | Layout shift, imágenes sin dimensiones, animaciones costosas, renderizado duplicado |
| 🌞 **Entorno & Plataforma** | Alta luminosidad, tablet/Fold, Windows/Mac, proyector, accesibilidad dinámica |
| 🎯 **Inline styles & Contraste contextual** *(nuevo)* | Colores hardcodeados en JS template literals, contexto heredado del padre, segunda red CSS para inline styles |
| 📏 **Densidad de lectura** *(nuevo)* | Paredes de texto: > 1,5 pantallas al entrar, bloques largos sin separar, listas sin agrupar → acordeones, grupos, pestañas |
| ♿ **A11y & Estados de feedback** *(nuevo)* | aria-label / aria-live / role, focus management, inputmode/enterkeyhint, empty states, skeleton/spinner de carga, banner in-app, feedback simétrico admin↔cliente |

En modo móvil/híbrido: Ley del Pulgar · Haptics · Tap Targets · Safe Areas · Gestos
En modo escritorio/híbrido: Jerarquía Visual · Atajos de Teclado · Densidad
Si el usuario lo menciona: Eje 8 completo o los sub-ejes relevantes
**Siempre obligatorios**: Eje 9 (inline styles), Eje 10 (a11y básica + estados) y Eje 11 (densidad de lectura: medir pantallas al entrar) — son tan recurrentes en proyectos del usuario que se elevan a check estándar

---

## Niveles de gravedad

- 🔴 **Crítico** — usuario no puede usar la función. Ej: contraste 1.2:1; botón 24px; layout roto en Fold; invisible en proyector.
- 🟡 **Importante** — usabilidad degradada. Ej: ratio 4.0:1 (falla en exterior); landscape rompe modal; scrollbar Windows descuadra grid.
- 🟢 **Mejora** — refinamiento. Ej: sin prefers-contrast; sin srcset 2x; sin modo presentación; sin reduced-motion completo.

---

## Formato de salida por problema (SIEMPRE estos 4 bloques)

### 🔴/🟡/🟢 [Nombre del problema]

**① Análisis Crítico:** Qué funciona y qué no, con evidencia concreta (archivo:línea o ratio numérico). Señala también lo positivo antes de lo negativo.

**② Propuesta de Mejora (Mock-up textual):** Describe visualmente cómo cambia la interfaz. Usa lenguaje evocador y concreto.

**③ Gamificación:** Propone el elemento de retroalimentación emocional específico para este punto.

**④ Snippet técnico listo para copiar:**
```css
/* Usa variables CSS existentes del proyecto, nunca valores hardcoded */
.elemento { color: var(--accent); background: var(--bg); }
```

---

## Flujo de ejecución (fases técnicas)

### Fase 1 — Reconocimiento

```bash
python3 /mnt/skills/user/auditoria-ux-visual/scripts/audit_recon.py <ruta-proyecto>
```

Extrae: archivos, variables CSS del proyecto, breakpoints, reglas `[data-theme]`, touch listeners, media queries de contraste/motion.

### Fase 2 — Análisis

```bash
python3 /mnt/skills/user/auditoria-ux-visual/scripts/audit_full.py <ruta-proyecto>
```

Leer referencias según los ejes afectados:
- `references/contrast-guide.md` — contraste/WCAG
- `references/typography-system.md` — tipografía
- `references/responsive-checklist.md` — responsive/touch
- `references/darkmode-checklist.md` — modo oscuro
- `references/device-quirks.md` — device-specific (iOS, Android, PWA)
- `references/environment-fragmentation.md` — outdoor, tablet, Fold, Windows, proyector, accesibilidad dinámica
- `references/inline-styles-contrast.md` — **NUEVO**: inline styles en JS templates, contraste contextual, paleta condicional por tema, `contrast-boost.css`
- `references/feedback-states.md` — **NUEVO**: a11y mínima (aria, inputmode, focus), skeleton/spinner, empty states, banner in-app, humanError mapping, feedback simétrico admin↔cliente

### Fase 3 — (Opcional) Capturas Playwright

Solo si el usuario lo pide explícitamente.

Viewports estándar: `320×568, 375×667, 390×844, 414×896, 768×1024, 1280×800`
Viewports Eje 8: `344×882` (Fold plegado), `717×1012` (Fold desplegado), `844×390` (landscape), `1366×768` (Windows HD)

### Fase 4 — Informe HTML

```bash
python3 /mnt/skills/user/auditoria-ux-visual/scripts/generate_report.py <audit-results.json> <output.html>
```

Incluir siempre sección «🎮 Gamificación & Micro-momentos». Si se auditó Eje 8, añadir sección «🌞 Entorno & Plataforma» con tabla resumen.

### Fase 5 — Fixes

**A) Auto-fix sin preguntar:** contraste con `var()`, `<img>` sin `alt`, touch targets <36px, `<button>` sin `aria-label`, falta `reduced-motion` global, `100vh` → `100dvh`, `width: 100vw` → `width: 100%`.

**B) Proponer con confirmación:** refactor breakpoints, jerarquía tipográfica, srcset 2x, modo outdoor/presentación.

**C) Solo reportar:** cambios de paleta, cambios estructurales, decisiones de copy.

---

## Reglas críticas

1. **Nunca saltar el Diagnóstico de Plataforma** — preguntar también por entornos físicos.
2. **Nunca afirmes problemas sin evidencia** — cita archivo:línea o ratio numérico.
3. **Usa variables CSS del proyecto** — extraerlas en Fase 1, usarlas en snippets.
4. **Los 4 bloques de salida son obligatorios** por cada problema.
5. **En móvil/híbrido, los 8 checks de Zoom UX son obligatorios** (incluye nav scroll, tap highlight y pull-to-refresh).
6. **En escritorio/híbrido, los 3 checks de Densidad son obligatorios**.
7. **La sección Gamificación aparece siempre**.
8. **Si el usuario menciona outdoor, tablet, Fold, Windows, proyector o accesibilidad dinámica → Eje 8 obligatorio.**
9. **Eje 9 (inline styles) y Eje 10 (a11y + estados) son OBLIGATORIOS siempre** — son los bugs más recurrentes en los proyectos del usuario.
10. **Buscar inline styles en JS templates**, no solo en CSS. `grep` por `style="[^"]*color:#` en `.js`.
11. **Falsos positivos son peores que falsos negativos** — si dudas, no reportes.
12. **Tono profesional, creativo y orientado a la ejecución** — sin análisis abstractos.
14. **Eje 11 (densidad de lectura) es OBLIGATORIO siempre**: mide las pantallas de scroll al entrar (colapsado, 1280×800 y 390×844). Si superan ~1,5, repórtalo y recomienda acordeones, grupos y pestañas, aunque no lo hayan pedido.
13. **Si encuentras `color:white` o `color:#fff` inline en un JS template, verificar contexto del padre antes de declarar bug** — puede ser correcto si el componente solo se renderiza sobre fondo oscuro.

## Anti-patrones a evitar

- ❌ Saltar el Diagnóstico y asumir desktop
- ❌ Ignorar la pregunta sobre entornos físicos o plataformas especiales
- ❌ Snippets con valores hardcoded cuando hay variables CSS
- ❌ Omitir la sección de Gamificación
- ❌ Respuestas sin Mock-up textual (bloque ②)
- ❌ Reportar 100 problemas del mismo origen — reporta el origen único
- ❌ Sugerir librerías nuevas si el proyecto es vanilla
- ❌ Romper el modo oscuro al «arreglar» contraste en modo claro
- ❌ Asumir que WCAG AA es suficiente para apps de uso exterior
- ❌ Asumir que "ancho > 600px = tablet" (Galaxy Fold desplegado)
- ❌ Ignorar landscape en móvil (altura ~320px es un contexto real)
- ❌ Olvidar que Windows tiene scrollbar visible que ocupa espacio
- ❌ **Auditar solo CSS y olvidar inline styles en JS templates** (Eje 9)
- ❌ **Saltar el Eje 10 (a11y + estados) porque "la app funciona"** — funciona para algunos, excluye a otros
- ❌ **Confundir `escaparNombre` con `escapeHtml`** al recomendar fixes (`escaparNombre` solo protege atributos `onclick`, NO innerHTML; usar `escapeHtml` para innerHTML)
- ❌ **Recomendar mover inline a CSS sin antes verificar la variable** (`var(--accent)` puede no existir en el proyecto)

## Casos de uso reales

- *«Audita la pantalla de puntos»* → Diagnóstico → análisis dirigido + Zoom UX si móvil + Gamificación
- *«Los botones son muy pequeños en móvil»* → Zoom UX completo
- *«Revisa contraste en todo»* → Eje contraste + Eje 9 (inline styles) + Gamificación
- *«¿Funciona bien en iPhone SE?»* → Zoom UX + capturas 320×568 + Safe Areas
- *«El dashboard es confuso»* → Escritorio → Densidad + Jerarquía + Atajos
- *«Modo oscuro tiene problemas»* → Eje modo oscuro + Eje 9 + Gamificación
- *«Se ve mal con el sol»* → Eje 8.1 outdoor + contraste AAA + tipografía exterior
- *«En iPad se ve raro»* → Eje 8.2 + split-view + landscape + grid auto-fit
- *«Tenemos usuarios con Galaxy Fold»* → Eje 8.3 + viewports 344px y 717px
- *«En Windows los botones se salen»* → Eje 8.5 + scrollbar-gutter + 100vw vs 100%
- *«Lo proyectamos en sala»* → Eje 8.8 + modo presentación + contraste proyector
- *«Usuarios con texto grande del sistema»* → Eje 8.9 + rem vs px + reduced-motion completo
- *«Blanco sobre blanco en panel admin»* → Eje 9 — contexto del padre + contrast-boost.css
- *«El ticker no se ve / va muy rápido en móvil»* → Eje 8.4-bis + velocidad adaptativa + animationPlayState
- *«El nav se aplasta en móvil»* → Zoom UX 6 — `flex: 0 0 auto` + mask de scroll
- *«La app parece rota mientras carga»* → Eje 10.2 — skeleton + spinner
- *«No hay feedback al pulsar»* → Eje 10.4 — botón con estado de carga + tap highlight
- *«Errores feos de Firebase visibles»* → Eje 10.7 — humanError mapping
- *«Botón pulla pull-to-refresh sin querer»* → Zoom UX 8 — `overscroll-behavior-y: contain`

## Bugs reales detectados en proyectos del usuario (memoria)

Casos concretos vistos en sesiones pasadas. La skill debe ser capaz de detectarlos sin que el usuario los señale:

- **Tenis ATP — `renderVotos` blanco sobre blanco**: la tarjeta de voto usaba `color:white` sobre fondo casi transparente `rgba(255,255,255,0.03)`. Diseñada para fondo oscuro, pero la sección admin tenía fondo blanco. Texto invisible. Fix: paleta condicional por tema y colores explícitos para contexto claro.
- **Tenis ATP — Paleta dorada `#C5A059` con ratio 2.19-2.46**: válida en classic-platinum (oscuro) pero falla WCAG en classic-light. 12 issues detectadas. Fix: paleta condicional `#6e5526` en modo claro + `contrast-boost.css` como red de seguridad.
- **Tenis ATP — Nav `flex: 1` aplastado en móvil**: cambio a `flex: 0 0 auto` + mask de scroll para indicar deslizamiento lateral.
- **Tenis ATP — Botón "CONTROL RÁPIDO DE PISTAS" con clase `btn-hub-item`**: heredaba padding del HUB, ocupaba 3x más que el resto.
- **Tenis ATP — Ticker `@keyframes` definido pero `animation` no aplicada** al elemento: keyframe sin destino. Y velocidad fija que era ilegible en móvil. Fix: velocidad adaptativa según viewport.
- **Tenis ATP — Doble renderizado en listener de Firebase**: dos contenedores con el mismo dato, parpadeo en móvil. Fix: renderizado condicional `if (contenedor && typeof renderX === 'function')`.
- **Tenis ATP — Renders olvidados tras mutación**: `toggleJugador`, `confirmarAsistencia`, etc. mutaban estado pero no llamaban a `renderPresentes`, `renderVotos`, `renderSeccionMVP`. El badge tardaba en actualizarse.
- **Family Points — Banner en header con `position:absolute z-index:0`**: bloqueaba interacciones de la cabecera. Fix: `pointer-events: none` en el banner.
- **Family Points — Tabs sticky `top:90px`** que se solapaban con header alto en algunos viewports. Fix: `position: static` debajo de 380px.
- **Family Points — Modal acciones**: layout `flex` que dejaba el botón principal pequeño en móvil. Fix: `flex: 1 1 auto` y reflow vertical en `<=480px`.
- **Family Points — Drag & drop solo desktop**: cero soporte touch. Fix: HTML5 drag para desktop + touch personalizado con `elementFromPoint` para móvil + `touch-action: none` en handle.
- **Academia / 3º primaria — Cero `aria-label`, cero `inputmode`, cero `tabindex`**: las apps funcionan pero excluyen lector de pantalla, navegación por teclado y teclado correcto en móvil. Reportar como 🟡 importante siempre.
- **Academia / 3º primaria — `prefers-reduced-motion` parcial**: confeti y `pts-pop` lo respetaban pero el resto de transiciones no. Fix: bloque global `*, *::before, *::after` con excepciones para feedback de acierto/fallo (que es información, no decoración).
- **Orange Eventos — Pantalla de espera con spinner infinito** si Firestore lento: no había handler de error en `onSnapshot`. Fix: handler con timeout + mensaje "Sin conexión con el servidor".
- **Orange Eventos — Confetti detrás del overlay fullscreen** por z-index 1000 vs 1000. Fix: canvas confetti sube a z-index 2000 al celebrar.
- **Orange Eventos — Recientes desbordaban el overlay**: array sin truncar. Fix: `.slice(0, 5)` en el punto de render.
- **MasOrange hub — Empty states inexistentes**: listas vacías mostraban contenedor vacío. Fix: `renderEmptyState()` helper reusable con icono + título + CTA.
- **Academia Portal — "Barra fantasma" Chrome Android Xiaomi (v6.11.1)**: modales con `position:fixed` + `transform:translateX(-50%)` causaban *stuck composited layer* — el modal cerrado dejaba residuo gris persistente. Causa: el navegador no descartaba la capa GPU compuesta. Fix: patrón `display:none` (no `visibility:hidden`) sobre el padre cuando cerrado + clase `.preparado` que pone `display:flex` y forzar reflow + clase `.show` para opacity transition + `setTimeout(280ms)` antes de quitar `.preparado` tras cerrar. Reproducible en Xiaomi MIUI Chrome, no en Pixel/Samsung. **NUNCA usar `transform:translateX(-50%)` en `position:fixed` en móvil**; alternativa: `left:0;right:0;margin:auto`.
- **Academia Portal — `overflow-x:auto` solo, en Chrome Android**: empuja `overflow-y` a `scroll` por defecto, generando scrollbar fantasma vertical inesperado en horizontal scrollers. Fix: SIEMPRE pareja explícita `overflow-x:auto; overflow-y:hidden`.
- **Academia Portal — Chrome Android barra inferior URL invisible**: `100vh` daba alto incorrecto cuando la barra se ocultaba dinámicamente. Fix: usar `100dvh` (`dynamic viewport`) además de `100vh`, equivalente para `100dvw` y `100vw`. Patrón: `height: 100vh; height: 100dvh;` (fallback + override).
- **Academia Portal — `<select>` y `<option>` ilegible en modo oscuro**: navegadores ignoran custom CSS sobre los nativos por defecto. Fix: `.modal select, .modal option { background:#1a2638 !important; color:#fff !important; }` (con `!important` SIEMPRE — Safari/Chrome no aceptan el override sin él).
- **Academia Portal — Avatar emoji 🐢 vs SVG inline mascota propia**: el avatar del header del chat usaba emoji genérico mientras la mascota flotante era SVG con identidad propia (cuerpo amarillo + cara). Inconsistencia visual. Fix: avatar inline SVG mini con mismos colores (`#FAC775` + `#854F0B`), tamaño 40px (no 36) con marco blanco `border:2px solid rgba(255,255,255,0.4)` + sombra.
- **Academia Portal — Tap vs Drag en mascota arrastrable**: alumno arrastra Medi pero al soltar se considera "click" y abre el chat sin querer (o viceversa: quiere abrir chat y empieza a arrastrar). Fix: threshold combinado — **<8px movimiento Y <250ms tiempo = tap**, **>8px = drag**, **>250ms sin mover = pulsación larga (saludo)**. `dragInfo.tStart = Date.now()` y comparar `duracionMs` en `onDragEnd`.
- **Academia Portal — Burbuja preview persistente con `mediPreviewPulse` animation**: para notificación NO intrusiva sin badge rojo ni número, usar burbuja dorada (`linear-gradient #FFEEAA → #FFD66B`) junto a la mascota con `@keyframes mediPreviewPulse { 0%,100% { box-shadow: 3px 3px 0 #B45309, 0 0 0 0 rgba(180,83,9,0.4); } 50% { box-shadow: 3px 3px 0 #B45309, 0 0 0 8px rgba(180,83,9,0); } }` (pulse expansivo) + icono 💬 con su propia animación `scale(1)→scale(1.2)`. UX más amable que badge numérico.
- **Academia Portal — Auto-dormir mascota tras 5min inactividad**: si la mascota tiene animaciones constantes (respiración, parpadeo) cansa visualmente y consume GPU. Fix: detector con `setInterval(30s)` que comprueba `Date.now() - ultimaInteraccion >= 5*60*1000` → cambia a estado durmiendo (ojos cerrados + gorrito + Zzz). Despertar al primer evento `['click','keydown','mousemove','touchstart','scroll']` registrado con `{passive: true}`. **Crítico**: solo dormir si está en estado neutro (`tranquila`), no interrumpir estados activos como `eureka`/`ganadora`.
- **Academia Portal — Parpadeo aleatorio idle**: si todos los parpadeos son iguales se ve robótico. Fix: `@keyframes mediParpadeo { 0%,94% { transform:scaleY(1); } 96%,99% { transform:scaleY(0.1); } 100% { transform:scaleY(1); } }` con `5.2s steps(1, end) infinite` aplicado por `.medi-tranquila .medi-ojo-izq, .medi-tranquila .medi-ojo-der`. El 94-96-99-100 da la sensación de parpadeo "humano" no exactamente periódico.
- **Academia Portal — Animaciones CSS por estado, sin loops JS**: en mascotas con 10+ estados visuales, NO usar `setInterval` JS para animar (consume CPU). Fix: clase CSS por estado (`medi-eureka`, `medi-cariñosa`, etc.) con `animation: mediXxx Ns infinite` y `transform-origin: center bottom` para que el bounce parta del suelo. `will-change: transform` solo en elemento principal. Cambiar estado = solo cambiar clase, no recrear elemento.
- **Academia Portal — Migración limpieza historial localStorage tras refactor**: cuando cambian textos UI (ej. "pulsa 💬" → "tócame") el alumno ya tiene mensajes guardados con el texto viejo. Fix: en `leerHist()` filtrar una vez si `!localStorage.getItem('medi_chat_migracion_v613')`, eliminar mensajes con patrones obsoletos (`/pulsa\s*💬|🐢/`), guardar flag para no repetir. Una sola pasada en el primer load post-deploy.
- **Academia Portal — Cache busting masivo 57+ HTMLs con Python regex**: cuando un archivo JS/CSS cambia y está enlazado desde decenas de HTMLs, regex compilada + `glob('*.html') + glob('*/*.html')` itera todo: `new = re.sub(r'mascota\.js\?v=\d+', 'mascota.js?v=7', html)`. Si no había `?v=`, añadirlo: `new.replace('mascota.js"', 'mascota.js?v=7"')`. Loggear `mod` (modificados) para verificar.

- **Academia Portal v6.13.9.16 — Mismatch idioma class-name CSS vs HTML/JS**: bug visual SILENCIOSO terriblemente difícil de detectar. Si el CSS usa `.t3-panel.active` (inglés) pero el HTML/JS usa `.t3-panel.activa` (español, recién traducido), los paneles **nunca se muestran** porque la clase no matchea. Sin error en consola, todo "funcional", pero `display:none` permanente. Auditar SIEMPRE con: `grep -rn "active\|activa" tema.css tabs.js modulo*.html` ante cualquier feature basada en clases CSS dinámicas. Si aparecen ambas formas mezcladas → bug garantizado. **Patrón general**: definir convención de idioma para class-names (en este proyecto: inglés `active`/`open`/`hidden`) DESDE EL DÍA 1, documentarla en el `CONTEXT_ADN.md`, y en PRs rechazar mezcla. **Aplicado**: 30 reemplazos `activa→active` en 5 módulos de Inglés 3º, bug heredado del modulo1 original.

- **Academia Portal v6.13.9.17/18 — Centrado coherente entre páginas hermanas**: al crear academia nueva por inspiración de otra hermana, comprobar **antes de empezar** qué wrapper de centrado usan las hermanas. En este caso Mat3 y Nat3 usan `<div class="container">` (max-width:1100px) para el index del portal y `<div class="t3-content">` (max-width:880px) para los paneles dentro de módulos. Si la nueva academia usa otro wrapper (ej. `t3-page` sin centrar), queda a tope del viewport en pantallas anchas. **Auditar antes de copiar**: `grep -E 'class="(container|t3-content|t3-page)"' nat3/modulo1.html` para saber qué usar como referencia. **Síntoma típico**: "la academia nueva se ve fea en monitor grande, las cards salen pegadas a los bordes". Causa: wrapper de centrado incorrecto. **Regla operativa**: páginas hermanas del mismo nivel (todas las academias del portal) DEBEN usar el mismo wrapper. Documentar en el `CONTEXT_ADN.md` qué wrapper estandariza cada nivel del proyecto.

- **Academia Portal v6.13.9.21 — Chip flotante alineado con contenido NO con viewport**: cuando un chip/badge se posiciona con `position:fixed; right:12px;`, en viewports anchos queda pegado al borde del navegador, lejos del contenido centrado (ej. `max-width:880px` en el centro). Se percibe como "perdido" o desconectado. Fix: detectar el contenedor principal (`.t3-content`, `.container`, `main`) y posicionar el chip relativo al borde DERECHO del contenedor, no del viewport. Patrón: `var rect = contenedor.getBoundingClientRect(); var rightOffset = window.innerWidth - rect.right; chip.style.right = Math.max(12, rightOffset + 12) + 'px';`. Recolocar en `resize` + dos `setTimeout(200/800ms)` para topbar lenta. **Aplica a TODO chip/badge `position:fixed`** en apps con contenido centrado.

- **Academia Portal v6.13.9.24 — CSS scopeado por error (botones sin gracia)**: anti-patrón muy común. Si una clase de botón (`.btn-confirm`) solo define `background` y `color`, pero su estilo "base" (padding, border-radius, font, cursor) está scopeado a UN solo padre (ej. `.restore-actions button { padding... }`), el resto de modales que usen la misma clase salen **cuadrados sin gracia** (sin padding, font del navegador). Bug histórico oculto durante semanas porque solo se ve cuando se reutiliza la clase en otro contexto. **Fix correcto**: separar SIEMPRE regla base (sin scope) de temas (con o sin scope). Patrón:

  ```css
  /* Base · sin scope */
  .btn-confirm, .btn-cancel {
    padding: 10px 22px; border-radius: 22px; border: none;
    font-family: 'Fredoka One'; cursor: pointer;
    display: inline-flex; align-items: center; gap: 6px;
    transition: transform 0.15s, opacity 0.15s;
  }
  /* Temas · pueden scopearse */
  .btn-confirm { background: linear-gradient(...); color: ...; }
  .btn-cancel  { background: rgba(...); color: ...; }
  ```

  **Auditar con**: buscar en CSS reglas como `.padre button { padding... }` y verificar si las clases hijas (`.btn-X`) tienen su propio padding. Si no, mover la base sin scope. Aplica a TODOS los botones del proyecto, no solo modales.

- **Academia Portal v6.13.9.21 — Tap a mascota vs Botón chat separado**: anti-patrón: una sola interacción hace DOS cosas según tiempo (tap corto = abrir chat, tap largo = saludo). El usuario nunca descubre el truco. **Patrón correcto**: separar funciones con accesorios visuales claros. Tap a Medi (cualquier duración) → frase aleatoria del pool. Botón flotante separado `.mch-fab` 💬 abajo-derecha (`position:fixed; right:14px; bottom:14px`) → abrir chat. **TDAH-friendly**: niños adoran sorpresa al tocar Medi pero NO quieren que aparezca chat sin querer cuando solo querían divertirse. **Regla**: si una interacción tiene dos posibles resultados ambiguos por tiempo/gesto, mejor DOS accesorios visuales separados.

- **Academia Portal — Botones con clases inventadas que no existen en CSS**: anti-patrón. Si el HTML usa `<button class="t3-btn-siguiente">` pero el CSS solo tiene `.t3-btn` + `.t3-btn-azul/amarillo/verde/etc.`, el botón sale sin estilo (texto plano del navegador). Bug invisible al programador porque el HTML "parece coherente". **Detección automática**: script Python que extrae todas las clases `t3-btn-*` o `btn-*` usadas en HTML y las compara contra las definidas en CSS:

  ```python
  import re, glob
  usadas = set()
  for path in glob.glob('**/*.html', recursive=True):
      h = open(path).read()
      for m in re.finditer(r'class="([^"]+)"', h):
          for c in m.group(1).split():
              if c.startswith('t3-btn'): usadas.add(c)
  todo_css = ''.join(open(p).read() for p in glob.glob('*.css'))
  for c in usadas:
      if not re.search(r'\.' + re.escape(c) + r'\s*[{,]', todo_css):
          print(f"HUÉRFANA: .{c}")
  ```

  **Aplicado v6.13.9.22**: detectó `.t3-btn-siguiente` y `.t3-btn-volver` huérfanas en Inglés 3º (40 botones sin estilo). **Patrón general**: ejecutar este audit como parte de cada PR/release.

- **Academia Portal — Identidad coherente de mascota · NO inventar al pool de frases**: bug introducido por la IA. Al añadir 50 frases al pool de Medi, la IA asumió que Medi era una tortuga y añadió frases con "mi caparazón", "vivimos 100 años", "¿sabes cuántas patas tengo?". El usuario nunca había dicho que era tortuga. **Patrón general**: ANTES de añadir contenido auto-referencial a un personaje/mascota/branding, **verificar la identidad real** mirando el SVG, los assets, las decisiones de diseño documentadas en el proyecto. **Anti-patrón**: asumir personaje por el visual sin confirmar. **Regla operativa**: para mascota propia, mantener archivo `PERSONAJE.md` en el repo con: qué es (libro, robot, animal...), su origen narrativo, su tono de voz, qué dice y qué NO dice. Antes de añadir frases nuevas, consultar este archivo.

---

## 🎯 Patrones operativos UX consolidados (sesión maratón v6.13.9.x)

- **Academia Portal — Chip `#pc-timer` ("2 min estudiando") se solapa con contenido inferior**: `pausa-cognitiva-3primaria.css` posiciona el chip con `bottom:14px; left:14px; position:fixed`. Cuando `tema-hud.js` se auto-desactiva por detectar `.t3-mapa` (correcto), el chip queda sin elemento que lo suba — y el contenido de las cards (especialmente las `t3-ruta-card` en el panel Practico) llega hasta el borde inferior de la pantalla quedando tapado. **Fix**: añadir en el `<style>` inline del módulo: `.t3-content { padding-bottom: 70px !important; }` — esto garantiza que el contenido termina 70px antes del borde inferior, dejando espacio libre al chip. **Regla general**: cualquier elemento `position:fixed` en la esquina inferior necesita que su "zona de aterrizaje" tenga `padding-bottom` equivalente en el scroll container. No confiar en que otros elementos fixed lo suban automáticamente.

- **Academia Portal — Chip de lectura parado al 57-60% (UX, no bug JS)**: desde la perspectiva UX, el chip "Lee teoría" parado es confuso para el alumno — parece que la pantalla se ha colgado. Además bloquea el quiz. El síntoma visual es correcto (el chip existe y se actualiza) pero el mecanismo de desbloqueo no dispara. Causa raíz: `tipo: 'cambiarTab'` en `LecturaTeoria.iniciarSeguimiento()` en academia que usa `irAPanel`. **Impacto UX**: el alumno lee toda la teoría, llega al chunk de victoria, y aún así el quiz aparece bloqueado — frustración máxima para niño con TDAH. **Diagnóstico rápido en consola**: `LecturaTeoria._debugEstado?.()` si está disponible, o buscar en los logs `[LT] _instalarInterceptor ejecutándose, tipo: cambiarTab`.

### Auditoría de class-names

1. **Convención idioma class-names**: documentada desde día 1, mismo idioma para CSS+HTML+JS. Auditar mezcla con `grep -rn "claseInglés\|claseEspañol"`.
2. **Clases huérfanas** (HTML usa, CSS no define): script Python obligatorio en cada release.

### Auditoría de scoping

3. **Regla base vs Temas**: SIEMPRE separar. La base (padding/border/font) sin scope; los temas (background/color) pueden scopearse.
4. **Auditar selectores `padre selector`**: si la regla scopeada define estilos compartidos por las clases hijas, sacarla del scope.

### Auditoría de centrado

5. **Wrapper de centrado coherente entre páginas hermanas**: documentar en `CONTEXT_ADN.md` qué wrapper usa cada nivel.
6. **Chips/badges fixed**: alinear con contenido (`.container.right`), no con viewport. Especialmente crítico en monitor grande.

### Identidad de mascotas/personajes

7. **Verificar identidad antes de generar contenido auto-referencial**. Mirar SVG, assets, decisiones de diseño documentadas.
8. **Archivo `PERSONAJE.md`** en el repo con qué es, qué dice y qué NO dice.

### UX TDAH-friendly

9. **Pool de frases con variedad y sorpresa**: 30+ frases por personaje. Detección automática de contexto (academia, idioma).
10. **Separar accesorios visuales** para funciones distintas (tap = frase, botón = chat).
11. **Coherencia visual entre módulos hermanos**: mismo topbar, mismo mapa visual de pasos. Reduce carga cognitiva.

---

## 🎯 Patrones UX genéricos — layout, z-index y fondos

### Fondo translúcido + z-index stack

**Problema:** Una imagen de fondo (base64 o URL) no se ve aunque el CSS parece correcto. El elemento existe pero aparece tapado.

**Causa más frecuente:** Conflicto de `z-index` entre el fondo, el contenido y los overlays. El stacking context se rompe cuando algún elemento intermedio tiene `position` + `z-index` que "atrapa" el fondo dentro de su contexto.

**Stack correcto para fondo + contenido + header:**
```css
#bg-fondo {
  position: fixed; inset: 0;
  z-index: -1;           /* Por debajo de todo */
}
.header-bg {             /* Imagen del header */
  position: absolute; inset: 0;
  z-index: 1;
}
#app-section {
  position: relative;
  z-index: 2;            /* Contenido por encima del fondo */
}
```

**Regla crítica:** NUNCA añadir `backdrop-filter` a contenedores de tab (`.tabs`, `.tab-content`). `backdrop-filter` crea un nuevo stacking context que destruye la jerarquía z-index del fondo.

**Verificación Playwright:**
```python
result = page.evaluate("""() => {
  var bg = document.querySelector('#bg-fondo');
  return {
    zIndex: getComputedStyle(bg).zIndex,
    position: getComputedStyle(bg).position,
    // Debe ser z-index:-1 y position:fixed
  };
}""")
```

---

### Breakpoint de sidebar: 767px, no 768px ni 820px

**Problema:** El sidebar aparece o desaparece en un punto inesperado — el usuario en tablet lo ve roto.

**Causa:** El breakpoint estándar de "tablet" es 768px (ancho mínimo de iPad en portrait). Si el CSS usa `@media (min-width: 768px)` para el sidebar, en exactamente 768px el sidebar aparece Y la versión móvil también puede estar activa → conflicto visual.

**Regla:**
```css
/* Sidebar visible en tablet y superior: */
@media (min-width: 768px) {
  .sidebar { display: flex; width: 210px; }
  .bottom-nav { display: none; }
}

/* Móvil puro: */
@media (max-width: 767px) {
  .sidebar { display: none; }
  .bottom-nav { display: flex; }
}
```

**Los 4 viewports de auditoría estándar:**
- 375px (iPhone SE / móvil pequeño)
- 768px (iPad portrait / tablet)
- 1024px (iPad landscape / laptop pequeño)
- 1280px (desktop estándar)

Auditar SIEMPRE en estos 4 antes de un release. Texto ≥13px, botones ≥44px, sidebar correcto.

---

### Tooltips: un solo elemento flotante en body

**Problema:** Los tooltips se recortan por `overflow: hidden` o `overflow: auto` del contenedor padre. No importa cuánto se ajuste el CSS.

**Causa:** Si el tooltip es un `::after` del elemento o un div hijo, hereda el overflow del contenedor. Imposible de escapar con CSS puro.

**Patrón correcto — un solo .floating-tip montado en body:**
```javascript
// Un solo elemento, creado una vez al inicio:
const tip = document.createElement('div');
tip.className = 'floating-tip';
tip.style.cssText = 'position:fixed;z-index:9999;pointer-events:none;display:none;';
document.body.appendChild(tip);

// Posicionar en cada hover:
function showTip(text, targetEl) {
  const rect = targetEl.getBoundingClientRect();
  tip.textContent = text;
  tip.style.display = 'block';
  tip.style.left = rect.left + 'px';
  tip.style.top  = (rect.top - tip.offsetHeight - 8) + 'px';
}
function hideTip() { tip.style.display = 'none'; }
```

**Por qué funciona:** `position: fixed` en el body escapa de cualquier `overflow` del árbol de padres.

---

### Panel flotante: clamp en ambos ejes

**Problema:** Un panel flotante (drawer, tooltip largo, modal compacto) se sale de pantalla hacia un lado o por arriba en viewports pequeños.

**Causa:** El posicionamiento solo comprueba `left/right` pero no `top/bottom`.

**Fix — clamp en ambos ejes:**
```javascript
function posicionarPanel(panel, anchorEl) {
  const rect = anchorEl.getBoundingClientRect();
  const pw = panel.offsetWidth, ph = panel.offsetHeight;
  const vw = window.innerWidth, vh = window.innerHeight;
  const margin = 8;

  let left = rect.left;
  let top  = rect.bottom + 4;

  // Clamp horizontal
  left = Math.min(left, vw - pw - margin);
  left = Math.max(left, margin);

  // Clamp vertical
  top = Math.min(top, vh - ph - margin);
  top = Math.max(top, margin);

  panel.style.left = left + 'px';
  panel.style.top  = top  + 'px';
}
```

**Auditar:** Probar en 375px de ancho y 600px de alto. Si el panel se recorta → clamp falta en algún eje.

---

## 🧩 Lecciones de JoGaSan Academy (auditoría del 11-oct-2026: 1º ESO, 4º Primaria y el área infantil)

> Copia del repo (`.claude/skills/auditoria-ux-visual/`); la versión de la cuenta ya lleva estas lecciones (12-oct). Si cambias una, cambia la otra.

**Método que funcionó** (Playwright, `serviceWorkers: 'block'`, sesión de alumno sembrada, servidor
local; viewports 320, 344, 390, 768, 844×390 y 1280): mide, arregla, **vuelve a medir** y compara con
`main`. Cada hallazgo con su número («la teoría empieza en y = 606 de 844», «16 páginas con solapes»).

1. **Un medidor de contraste que se salta los degradados no sirve.** Mi primer barrido daba «0 bajo AA»
   porque ignoraba fondos con `linear-gradient`; el encabezado de bloque de las 4º B (texto marrón
   sobre índigo) daba 2,7:1 y no salió. Mide el texto contra **ambos extremos** del degradado y verifica
   a mano los candidatos: `color-mix()` sale de `getComputedStyle` como `color(srgb …)` (parsea los dos
   formatos), y el emoji o el texto sobre una imagen dan falsos positivos.
   **Método fiable (11-oct): por píxeles.** Para cada texto sobre degradado/imagen, pon su `color` y
   `text-shadow` en transparente (también los hijos), haz `page.screenshot({clip})` de su caja, y
   compara el color del texto con los percentiles 5 y 95 de luminancia de esos píxeles (peor caso).
   Con eso, 175 textos medidos pasaron de 63 a 7 fallos tras arreglar, y los 7 eran falsos positivos
   (un `<strong>` en línea que ocupa varias líneas, cuya caja incluye texto vecino; y un título con
   borde oscuro `text-stroke`). Mira siempre los recortes de los grupos antes de arreglar.
2. **Clases sin ninguna regla CSS.** `.t3-chunk-header/-num/-titulo` estaban en 25 módulos y en ningún
   CSS: texto a ras del borde, sin separar del número. Lista las clases que usa el HTML y no define
   ninguna hoja (`grep` + el script de huérfanas de arriba) **antes** de mirar contrastes.
3. **Altura de cabecera = «¿dónde empieza lo que hay que leer?».** Además de las pantallas totales,
   mide `getBoundingClientRect().top` del primer bloque de contenido a 390×844. Objetivo < 300 px. Un
   héroe con emoji de 55 px + subtítulo de 6 líneas + pestañas en 2 filas se come el 57-79 %.
4. **Zona táctil: mira el `::after` antes de reportar < 44 px.** `medi-badge-chat` mide 30×30 pero su
   `::after { inset: -8px }` da 46×46. No es un fallo.
5. **Elementos `position: fixed` en el mismo rincón** (píldora del alumno + barra de progreso + Medi +
   🐛): mide solapes entre sus rectángulos en cada módulo, no a ojo. Apílalos con `body:has(#x)`.
6. **Barras superiores a 320-360 px:** detecta solapes entre los hijos de la barra (`rect.left <
   anterior.right`) en 30+ páginas × 3 anchos, y compara con `main`. Recupera lo que se ocultaba
   (avatar del alumno) quitando lo decorativo (⏱, flechas ›), no lo que se usa. Un detector burdo
   cuenta elementos fuera de la barra: filtra por `top ≥ 0 && bottom ≤ alto de barra` y espera a que el
   cronómetro llegue a ella (2-3 s).
7. **Botón flotante ⛶ de pantalla completa:** reserva su sitio (52 px a cada lado del título del héroe) o
   pisa el título. Si bajas una fila para esquivarlo, que la banda vacía no sobreviva donde hay sitio
   (≥ 372 px).
8. **Área infantil (niño de 5 años, no lee):** menos tarjetas apiladas y más **azulejos** (emoji grande + nombre;
   la voz lee); la burbuja de Chispa en horizontal en el borde de abajo y pequeña; HUD no sticky en
   horizontal; el viaje de amigas entero en una fila. Mundos en 2 columnas solo si el nombre por
   sílabas cabe (reduce emoji y fuente).
9. **Al compartir CSS entre muchas páginas, el `?v=` se sube con `scripts/cache-bust.js`** y se repite
   tras fusionar `main` (llegan páginas nuevas con el `?v=` viejo).
10. **Banners y avisos fijos (invitado, 4-oct):** una fila de ≤ 50 px que esquive lo fijo de la academia (barra de progreso, aviso de fallos), botones ≥ 44 px, `viewport-fit=cover` + zonas seguras,
    `dvh` en vez de `vh`, bordes de campos a ≥ 3:1, foco al cambiar de vista, `enterkeyhint` y vibración al entrar/crear/borrar. Medido en 8 viewports (320-1366, Fold plegado/abierto, iPad y split-view, horizontal).
11. **Táctil en apps de práctica (Repaso de Operaciones):** `touch-action:manipulation`, `-webkit-tap-highlight-color: transparent` y un `:active` propio; `inputmode` numérico, `aria-live` para el feedback y
    `prefers-reduced-motion`. Si una app se pinta por JS, carga `nav-chunks.js` o se convierte en un muro de scroll.
12. **Tablas y SVG que desbordan a 390 px:** SVG que encogen (`max-width:100%`), `.tabla-scroll` con borde difuminado y menos relleno lateral en móvil; mide `scrollWidth > innerWidth` en cada página, no en una muestra.
13. **Textos de 11 px:** subir la letra mínima a 12 px bajó las páginas con texto pequeño de 120 a 5 (solo el ▾ del conmutador). Barre `font-size` computado de todos los nodos de texto, no solo los de tu CSS.
14. **Título con `<em>` múltiples dentro de un `h2` flex** se parte en columnas: el contenedor de títulos no debe ser flex.
