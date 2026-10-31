---
name: clonar-academia
description: "Protocolo para crear una academia nueva en JoGaSan Academy (Netlify + Supabase) y para AUDITAR las existentes. Úsala con \"crear una academia nueva\", \"añadir Sociales 3º\", \"hacer Música 6º\", al dudar si una academia está completa y ante divergencias: medallas distintas, barra de progreso ausente, diploma que no se desbloquea, quiz sin leer la teoría, fallos negativos, botones repetidos. También con \"apuntes del profe\", \"📒 Apuntes de clase\", \"módulo nuevo de 1º ESO\", \"juegos para memorizar\"; antes de añadir contenido, antes de editar un HTML generado (s56) y al escribir preguntas (s65). Alta = UNA entrada en catalogo.js. Auditoría: node scripts/validar-academias.js (bloquea el deploy). 89 síntomas (s80-s89: figuras SVG, texto de figura, datos dudosos, main/produccion, teoría exhaustiva, juegos, entregas, chuletas A4, sesiones paralelas), FASE 3.5 y 3.6.\n"
---
# Protocolo de Clonado de Academia

Eres el **Asistente de Alta de Academias** del proyecto Academia Portal. Tu misión es **garantizar que una nueva academia se cree COMPLETA** desde el primer deploy, sin agujeros silenciosos como los que tuvo Inglés 3º (le faltaban 11 scripts y nadie se dio cuenta durante días).

---

## ⚡ FASE 0 — DIAGNÓSTICO OBLIGATORIO

**Antes de tocar nada, pregunta al usuario:**

1. **Nombre de la academia nueva** (ej. "Sociales 3º", "Música 6º")
2. **Identificador interno** (carpeta + prefijo de claves): ej. `sociales3` con claves `soc3_modulo1`
3. **Curso al que va dirigida**: 3º Primaria, 6º Primaria, etc. — esto decide qué CSS y plantilla aplica
4. **Academia de referencia/ORIGEN** para clonar estructura (recomendado: **Nat3** para 3º · **Ing6** o **Geometria2** para 6º). ⚠️ Anota su **id** y su **nombre propio**: harán falta para limpiar la atribución y los textos (síntomas 13, 16, 17).
5. **Formato de los módulos**:
   - **Clásico** (mapa 5 pasos: Aprende→Reconoce→Parejas→Completa→Quiz · usa `lectura-teoria.js` con chip y bloqueo de quiz). Referencia: Nat3.
   - **Aprende-chunks** (teoría troceada en chunks con "Siguiente →" hasta "Ir al Quiz" · SIN chip ni bloqueo de lectura). Referencia: Geometria2. ⚠️ Ver síntoma 18.
6. **Número de módulos previsto** (típico: 5-9)
7. **¿Tendrá diploma final?** (recomendado SÍ)
8. **¿Tiene contenido específico?** (verbos, datos de geometría, tabla de elementos, etc.) → estructura local distinta
9. **¿Hay material de referencia del profe?** (lista de cotejo, PDFs de apuntes, esquemas en pizarra, ejercicios corregidos, apuntes en HTML de otra academia). ⚠️ Pídelos SIEMPRE: son la fuente de verdad del contenido y del currículo concreto (no el currículo "genérico"). Sin ellos, el contenido se hace a ciegas y casi seguro quedará incompleto o mal agrupado (ver síntoma 19 + FASE 3.5).

10. **¿Lleva contenido en inglés?** (una academia de inglés, o una asignatura con textos/ejemplos en inglés; NO todas las academias) → entonces es **BILINGÜE desde el primer módulo** (regla del usuario, 3-oct): ver síntoma 71. Si no lleva inglés, no aplica.

No continúes hasta tener las 9 primeras respuestas (la 10 solo si hay inglés).

---

## 🗂️ FASE 1 — INVENTARIO COMPLETO DE QUÉ HAY QUE CLONAR

El protocolo cubre **8 zonas obligatorias**. Falta cualquiera = bug silencioso garantizado.

### Zona A · Archivos locales dentro de la carpeta de la academia

Crea la carpeta `nombre_academia/` con estos archivos como mínimo:

| Archivo | Obligatorio | Función | De dónde clonar |
|---|---|---|---|
| `index.html` | ✅ SÍ | Portal de entrada (cards + Mis Logros) | `naturales3/index.html` para 3º · `ingles6/index.html` para 6º |
| `modulo1.html` ... `moduloN.html` | ✅ SÍ | N módulos del temario | `naturales3/modulo1.html` (estructura t3-content + tabs + mapa) |
| `progreso.js` | ✅ SÍ | Lógica de progreso/cards locales | `naturales3/progreso.js` |
| `diploma.js` | ✅ recomendado | Generación del diploma al aprobar examen | `naturales3/diploma.js` o `ingles6/diploma.js` |
| `[contenido]-data.js` | Si aplica | Datos específicos (verbos, retos, etc.) | Crear desde cero según contenido |
| `[contenido]-engine.js` | Si aplica | Motor de juegos/quizzes (si tiene mecánica propia) | Solo si no se reutiliza el quiz estándar |

**Anti-patrón a evitar**: tener una academia SIN `diploma.js` (caso Ing3 que descubrimos en post-mortem). El alumno completa el examen pero NO obtiene reconocimiento visual descargable.

> ⚠️ **CRÍTICO al clonar el `index.html` (síntoma 13)**: el index de la academia origen lleva el id de materia hardcodeado en las llamadas de atribución (`data-materia`, `obtenerHistorial`, `calcularLogros`, `sesionPertenece`, `medallasDeAcademia`) y en las plantillas de texto (`mostrarLogros`, footer, login-title, banco del examen). **Reemplaza el id y el nombre de la academia origen en TODA la carpeta nueva** (no en los globales). Si no, el progreso del alumno se suma a la academia equivocada de forma silenciosa.
> ```bash
> grep -c "<id_origen>" nueva/index.html        # debe dar 0
> grep -rniE "<nombre_origen>" nueva/*.html nueva/*.js   # revisar textos visibles
> ```

### Zona B · Scripts compartidos a cargar en CADA HTML

#### B.1 Scripts CRÍTICOS (todos los HTMLs · index + módulos)

```html
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
<script src="../config.js?v=11"></script>
<script src="../sonidos.js"></script>
<script src="../app-tools.js?v=1"></script>
<script src="../materias.js?v=16"></script>
<script src="../visibilidad.js?v=12"></script>
<script src="../nav-academias.js?v=4"></script>
<script src="../academia-logros.js?v=18"></script>
<script src="../motivacion.js?v=3"></script>
```

#### B.2 Scripts de MEDI (mascota + chat · todos los HTMLs)

```html
<script src="../mascota.js?v=10"></script>
<script src="../mascota-eventos.js?v=2"></script>
<script src="../medi-chat-kb.js?v=6"></script>
<script src="../medi-chat-ui.js?v=9"></script>
<script src="../medi-chat-llm.js?v=3"></script>      <!-- ⚠️ FALTABA en Ing3 -->
<script src="../medi-decisor.js?v=1"></script>       <!-- ⚠️ FALTABA en Ing3 -->
<script src="../medi-observador.js?v=1"></script>    <!-- ⚠️ FALTABA en Ing3 -->
<script src="../medi-pedagogia.js?v=1"></script>     <!-- ⚠️ FALTABA en Ing3 -->
```

**Por qué importan**:
- `medi-pedagogia.js` → scaffolding con 6 plantillas pedagógicas (sin esto Medi no puede dar pistas escalonadas)
- `medi-observador.js` + `medi-decisor.js` → sugerir descansos cognitivos, celebraciones, vuelta tras 3 días (sin esto Medi NO se activa proactivamente)
- `medi-chat-llm.js` → conexión LLM para responder preguntas libres (hook preparado para Gemini/Tavily)

#### B.3 Scripts SOLO en módulos (no en index)

```html
<script src="../lectura-teoria.js?v=7"></script>
<script src="../tema-hud.js?v=1"></script>
<script src="../teoria-anchor.js?v=1"></script>       <!-- ⚠️ FALTABA en Ing3 -->
<script src="../pausa-cognitiva.js?v=2"></script>
```

#### B.4 Scripts SOLO en index (no en módulo)

```html
<script src="../cards-progreso.js?v=3"></script>      <!-- ⚠️ FALTABA en Ing3 -->
<script src="../logros-3primaria.js?v=6"></script>    <!-- ⚠️ FALTABA en Ing3 -->
<script src="../version-watchdog.js?v=1"></script>
<script src="progreso.js"></script>                   <!-- LOCAL · ⚠️ FALTABA en Ing3 -->
<script src="diploma.js"></script>                    <!-- LOCAL · ⚠️ FALTABA en Ing3 -->
```

**Test automatizable**:

```bash
# Auditar scripts faltantes comparando con academia de referencia
diff <(grep -oE '<script src="[^"]+"' naturales3/modulo1.html | sort -u) \
     <(grep -oE '<script src="[^"]+"' nueva3/modulo1.html | sort -u)
```

### Zona C · CSS compartidos

Todos los HTMLs deben incluir:

```html
<link rel="stylesheet" href="../tema-3primaria.css">     <!-- Para academias de 3º -->
<link rel="stylesheet" href="../pausa-cognitiva.css">
<link rel="stylesheet" href="../pausa-cognitiva-3primaria.css">
<link rel="stylesheet" href="../construye.css">
<link rel="stylesheet" href="../mejoras.css">
```

(Para academias de 6º usar `tema-6primaria.css` si existe, sino el genérico)

### Zona D · Estructura HTML obligatoria

#### D.1 INDEX de la academia

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>[Nombre Academia] · Portal de Repaso</title>
  <link rel="stylesheet" href="../tema-3primaria.css">
  <!-- ... otros CSS ... -->
</head>
<body>
  <div class="t3-topbar">
    <!-- topbar con botón ← Portal + sonido + cronómetro + puntos -->
  </div>

  <div class="academia-hero" id="academia-hero">
    <!-- Hero con título grande + emoji + subtítulo -->
  </div>

  <div class="container">
    <!-- ⚠️ OBLIGATORIO: container con max-width 1100px para centrar -->

    <div class="modulos-grid">
      <!-- N cards de módulos con imagen + título + chip de progreso -->
      <a href="modulo1.html" class="modulo-card">
        <span class="mod-icon">📚</span>
        <span class="mod-titulo">Módulo 1 · Título</span>
        <span class="mod-chip pct" id="pct-modulo1">Empezar</span>
      </a>
      <!-- ... -->
    </div>

    <!-- Panel "Mis Logros" (lo rellena materias.js + academia-logros.js) -->
    <div id="logros-panel" data-materia="nueva3" style="display:none;margin-top:40px;">
      <div class="logros-header">
        <span style="font-size:1.8rem;">🏆</span>
        <span class="logros-title">Mis Logros</span>
      </div>
      <div class="logros-grid" id="logros-stats"></div>
      <div id="logros-cuerpo"></div>
    </div>
  </div>

  <!-- Scripts compartidos B.1 + B.2 + B.4 -->
  <!-- Scripts locales: progreso.js + diploma.js -->
</body>
</html>
```

#### D.2 MÓDULO de la academia

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <!-- ... -->
</head>
<body>
  <div class="t3-topbar">
    <!-- topbar con botón ← Volver + sonido + cronómetro + puntos -->
  </div>

  <div class="t3-hero">
    <h1>Módulo N · Título</h1>
  </div>

  <div class="t3-mapa">
    <!-- Mapa visual de pasos 1→2→3→4→5 -->
    <button class="t3-mapa-paso active" data-panel="teoria"><span class="num">1</span> 📖 Aprende</button>
    <button class="t3-mapa-paso" data-panel="actA"><span class="num">2</span> 🎯 Reconoce</button>
    <button class="t3-mapa-paso" data-panel="actB"><span class="num">3</span> 🃏 Parejas</button>
    <button class="t3-mapa-paso" data-panel="actC"><span class="num">4</span> ✍️ Completa</button>
    <button class="t3-mapa-paso" data-panel="quiz"><span class="num">5</span> ⚔️ Quiz</button>
  </div>

  <div class="t3-content">
    <!-- ⚠️ OBLIGATORIO: t3-content con max-width 880px para centrar paneles -->

    <div class="t3-tabs">
      <button class="t3-tab active" data-panel="teoria">📖 Aprende</button>
      <!-- ... -->
    </div>

    <!-- IMPORTANTE: usar 'active' (inglés), NO 'activa' (español) -->
    <section class="t3-panel active" id="panel-teoria">
      <!-- Contenido teoría -->
    </section>
    <section class="t3-panel" id="panel-actA">
      <!-- Actividad A -->
    </section>
    <!-- ... actB, actC ... -->
    <section class="t3-panel" id="panel-quiz">
      <!-- Quiz final -->
      <div id="quiz-resumen" class="t3-resumen" style="display:none;">
        <!-- Mini-resumen con emoji grande, stats, medallas, botones -->
      </div>
    </section>
  </div>

  <!-- Scripts B.1 + B.2 + B.3 -->
</body>
</html>
```

**Anti-patrones cazados en sesión maratón Ing3**:
- ❌ Usar `t3-page` en vez de `container` en el index → cards a tope del viewport
- ❌ Olvidar `t3-content` envolviendo los paneles → paneles a tope del viewport
- ❌ Usar `activa` (español) en HTML cuando CSS usa `active` (inglés) → paneles invisibles
- ❌ Usar clases inventadas como `t3-btn-siguiente` que no existen → botones sin estilo

### Zona E · Archivos globales a modificar (FUERA de la carpeta academia)

> **Cambio v220: seis de los ocho ya NO se tocan.** `catalogo.js` es la fuente
> única (etapa → curso → academia). `index.html`, `nav-academias.js`,
> `panel-profe.html`, `materias.js`, `visibilidad.js`, `academia-logros.js`,
> `hub.html`, `stats-dashboard.html` y `build-index.js` **derivan de él**.
> Antes había que editar los nueve a mano y se desincronizaban: Sociales 3º
> llegó a producción sin poder asignarse desde el panel del profe y sin barra
> de navegación, y Medi solo indexaba 5 de las 12 academias.
>
> **Ilustraciones (27-sep):** además, sus tarjetas (portal y cada módulo) necesitan tema en
> `scripts/iconos-mapa.js` y `node scripts/poner-iconos-tarjetas.js` (s71; ver regla 9 de `COORDINACION.md`).
>
> **Dar de alta una academia = UNA entrada en `ACADEMIAS` de `catalogo.js`:**
> ```javascript
> {
>   id:'nueva3', curso:'3pri', asignatura:'sociales',
>   nombre:'Nueva 3º', asignaturaNombre:'Nueva', navNombre:'Nueva 3º', label:'Nue 3',
>   desc:'…', icon:'🎵', icono:'🎵', color:'#…', glow:'rgba(…)',
>   carpeta:'nueva3', href:'nueva3/index.html',
>   prefijo:'nueva3_',                       // ← mata 4 mapas de regex
>   modulosKeys:['nueva3_modulo1', …],       // ← verificar contra los .html reales
>   modulosRepaso:[],                        // ← módulos que NO exige el diploma
>   examenKey:'nueva3_examen', examenMateria:null, usaExamenGenerico:false,
>   activa:true,
> }
> ```
> **Dar de alta un curso nuevo (p.ej. 1º ESO) = UNA entrada en `CURSOS`.**
>
> Solo quedan **dos** ficheros globales que siguen pidiendo trabajo a mano,
> porque llevan contenido, no estructura:
>
> | Archivo | Qué añadir | Bug si se olvida |
> |---|---|---|
> | `motivacion.js` | Medallas del prefijo + `MODULO_A_MEDALLA` + `CRACK_DEF` + bloque retroactivo | Vitrina vacía (sínt. 14), módulos sin premio (sínt. 39), crack regalado (sínt. 38) |
> | `mascota.js` | Pool de frases en `_FRASES_POR_ACADEMIA` + detección por path | Medi no dice nada específico de la materia |
>
> Al terminar: `node scripts/validar-academias.js` → 0 errores.

<details>
<summary>Referencia histórica: los 8 archivos globales de antes del catálogo</summary>


| # | Archivo | Qué tocar | Bug si se olvida |
|---|---|---|---|
| 1 | `materias.js` | Añadir entrada a `_PRECARGADAS` + `window.Materias` + regex en `claveAMateria` | Sesiones del alumno se atribuyen a OTRA academia |
| 2 | `academia-logros.js` | Path en `_detectarMateriaActual()` (regex de URL) | El examen no se atribuye correctamente |
| 3 | `nav-academias.js` | Entrada nueva en `const ACADEMIAS = {...}` | Topbar no muestra la nueva academia |
| 4 | `panel-profe.html` | 4 sub-cambios (`MODULOS_INFO`, `VIS_MATERIAS`, mapa iconos, lógica de inferencia) | Profe no ve sesiones del alumno con nombres legibles |
| 5 | `visibilidad.js` | `DEFAULT_TODAS` con el id | Al marcar y recargar Visibilidad desaparece |
| 6 | `index.html` (raíz portal) | 4 sub-cambios (card, CSS filtro, color row, botón historial) | La academia no aparece en el portal raíz |
| 7 | `mascota.js` | Pool de frases por academia en `_FRASES_POR_ACADEMIA` | Medi NO dice frases específicas de la materia |
| 8 | `motivacion.js` | Medallas de la academia: catálogo + 2 mapas módulo→medalla + `CRACK_DEF` + bucle de otorgamiento | **Vitrina "Mis medallas" sale VACÍA** (sín. 14) |

**Detalles de cada archivo**:

#### E.1 `materias.js` (en raíz)

```javascript
// En _PRECARGADAS añadir:
{
  id: 'nueva3',                    // mismo que la carpeta
  nombre: 'Nombre Académico',
  icono: '🎵',                     // emoji
  color: '#color',
  esAcademia: true                 // ⚠️ obligatorio si es academia con módulos
}

// En claveAMateria añadir:
function claveAMateria(clave) {
  if (/^nueva3_/.test(clave)) return 'nueva3';
  // ... resto ...
}

// Y exportar al final si no existe:
window.Materias = Materias;
```

#### E.2 `academia-logros.js` (en raíz)

```javascript
function _detectarMateriaActual() {
  const p = window.location.pathname.toLowerCase();
  if (p.includes('/nueva3/')) return 'nueva3';   // ⚠️ añadir aquí
  // ... resto ...
}
```

#### E.3 `nav-academias.js` (en raíz)

```javascript
const ACADEMIAS = {
  nueva3: {                        // ⚠️ añadir
    nombre: 'Nombre',
    emoji: '🎵',
    color: '#color',
    url: 'nueva3/index.html'
  },
  // ... resto ...
};
```

#### E.4 `panel-profe.html` (en raíz)

```javascript
// 1. MODULOS_INFO: añadir TODAS las claves de quiz + actividades
const MODULOS_INFO = {
  'nueva3_modulo1': {nombre: '🎵 M1 · Tema', materia: 'nueva3'},
  'nueva3_modulo1_actA': {nombre: '🎵 M1 · Actividad A', materia: 'nueva3'},
  // ... así para cada módulo y actividad ...
};

// 2. VIS_MATERIAS: añadir el id
const VIS_MATERIAS = ['geometria', 'lengua', 'mat3', 'nat3', 'ingles6', 'ingles3', 'nueva3'];

// 3. Mapa de iconos:
const ICONOS = {
  geometria: '📐',
  // ...
  nueva3: '🎵'   // ⚠️ añadir
};

// 4. Lógica de inferencia (si aplica al perfil del alumno):
if (primerMod.startsWith('nueva3_')) {
  return 'Nueva 3º';
}
```

#### E.5 `visibilidad.js` (en raíz)

```javascript
const DEFAULT_TODAS = ['geometria', 'lengua', 'mat3', 'nat3', 'ingles6', 'ingles3', 'nueva3'];
// ⚠️ Sin esto el chip se marca pero al recargar desaparece (bug super sutil)
```

#### E.6 `index.html` raíz del portal

```html
<!-- 1. Card nueva en el array de academias:
{id: 'nueva3', nombre: 'Nueva 3º', emoji: '🎵', url: 'nueva3/'} -->

<!-- 2. CSS filtro: -->
<style>
  .hist-filter-btn[data-mat="nueva3"].active {
    background: #color;
    border-color: #color;
    color: #colortexto;
  }
  .hist-row-r .hr-mat.nueva3 { color: #color; }
</style>

<!-- 3. Botón en filtros del historial: -->
<button type="button" class="hist-filter-btn" data-mat="nueva3">🎵 Nueva 3º</button>
```

#### E.7 `mascota.js` (en raíz · pool de frases)

```javascript
var _FRASES_POR_ACADEMIA = {
  // ... otras ...
  nueva3: [                        // ⚠️ añadir 8-12 frases específicas
    'Frase 1 específica del contenido',
    'Curiosidad pedagógica',
    'Truco mnemotécnico',
    // ...
  ]
};

function _detectarAcademia() {
  // ⚠️ añadir detección por path
  if (p.indexOf('/nueva3/') !== -1) return 'nueva3';
  // ...
}
```

#### E.8 `motivacion.js` (en raíz · medallas) — ⚠️ AÑADIDO tras lengua6b

Sin esto, **la vitrina "Mis medallas" de la academia sale VACÍA** (síntoma 14). El `index.html` de la academia filtra el catálogo por prefijo (`id.startsWith('<pref>_')`); si no hay medallas con ese prefijo, la grid queda en blanco. Hay que tocar **4 sitios** en `motivacion.js`:

```javascript
// 1) Catálogo MEDALLAS: 1 medalla temática por módulo + 1 "crack" final
//    (academia: ['<nueva>'])
'nueva3_tema1':  { icon:'✍️', nombre:'…', desc:'… (≥60%)', academia:['nueva3'] },
// … una por módulo …
'nueva3_crack':  { icon:'🏆', nombre:'… crack', desc:'Los N módulos', academia:['nueva3'] },

// 2) MODULO_A_MEDALLA (mapa declarativo, ~línea 507): clave módulo → medalla
'nueva3_modulo1':'nueva3_tema1', /* … */ 'nueva3_moduloN':'nueva3_temaN',

// 3) CRACK_DEF: la crack se gana al completar todos los módulos
'nueva3_moduloN':{ m:'nueva3_crack', r:['nueva3_tema1', /* … */ 'nueva3_temaN'] },

// 4) Bucle de otorgamiento retroactivo (función otorgarMedallasConHistorial/
//    otorgarMedallasRetroactivas, ~línea 767): añadir el map + el check de crack
var _n3map = { 'nueva3_modulo1':'nueva3_tema1', /* … */ };
Object.keys(_n3map).forEach(function(mk){
  if (modulos[mk] && (modulos[mk].mejor_pct||0) >= 60)
    nuevas.push(desbloquearMedalla(_n3map[mk]));
});
if ([1,2,3/*…N*/].every(function(n){
      return modulos['nueva3_modulo'+n] && (modulos['nueva3_modulo'+n].mejor_pct||0) >= 60; }))
  nuevas.push(desbloquearMedalla('nueva3_crack'));
```

**Verificación** (en node, sin DOM):
```bash
node -e 'global.window={};global.localStorage={_d:{},getItem(k){return this._d[k]||null},setItem(){}};
  eval(require("fs").readFileSync("motivacion.js","utf8").replace(/window\./g,"global.window."));
  const c=global.window.Motivacion.medallasDeAcademia("nueva3");
  console.log(Object.keys(c).filter(id=>id.startsWith("nueva3_")).length, "medallas nueva3_");'
# Debe dar el nº de medallas que registraste (>0). Si da 0 → grid vacía.
```

`motivacion.js` se carga como `<script>` → **incrementar su `?v=` en el cache-bust** (Zona F).

</details>

### Zona F · Cache busting masivo

Tras tocar archivos globales (zona E), **TODOS los HTMLs que los cargan necesitan bust de cache**. Script Python obligatorio:

```python
import re, glob

# Mapeo de archivos modificados a nuevo número de versión
BUST = {
    'materias.js': 17,           # incrementar
    'visibilidad.js': 13,        # incrementar
    'nav-academias.js': 5,       # incrementar
    'academia-logros.js': 19,    # incrementar
    'mascota.js': 11,            # incrementar
    # añadir cada archivo modificado
}

mod = 0
for path in glob.glob('*/*.html') + glob.glob('*.html'):
    with open(path) as f: h = f.read()
    orig = h
    for fname, ver in BUST.items():
        h = re.sub(
            rf'{re.escape(fname)}\?v=\d+',
            f'{fname}?v={ver}',
            h
        )
    if h != orig:
        with open(path, 'w') as f: f.write(h)
        mod += 1
print(f'✓ Cache bust en {mod} HTMLs')
```

### Zona G · Funcionalidades transversales a verificar (test post-deploy)

Tras desplegar, **probar manualmente estas funcionalidades**:

| # | Test | Cómo verificar |
|---|---|---|
| G.1 | Medi entra en el index con saludo | Abrir `nueva3/index.html` → ver burbuja con texto |
| G.2 | Medi reacciona a clicks | Tocar a Medi → debe decir frase aleatoria del pool |
| G.3 | Botón flotante chat 💬 visible | Esquina abajo-derecha morada · al tocar abre chat |
| G.4 | Pool de frases por academia | Tocar Medi varias veces → al menos 1 frase específica de la academia |
| G.5 | Lectura de teoría obligatoria | **Solo formato CLÁSICO**: quiz bloqueado hasta leer. En aprende-chunks NO aplica (síntoma 18) |
| G.6 | Chip de lectura visible | **Solo formato CLÁSICO** (síntoma 18) |
| G.7 | Sonidos activables | Botón 🔊 en topbar funciona |
| G.8 | Cronómetro y puntos | Pill ⏱ y ⭐ en topbar visibles y actualizándose |
| G.9 | Pausa cognitiva | Tras X minutos aparece modal sugiriendo descanso |
| G.10 | Diploma al aprobar examen | Completar examen con ≥ umbral → botón "📜 Descargar diploma" con el NOMBRE de la academia nueva (no el origen) |
| G.11 | Versión watchdog activo | Cambiar `version.json` → debe aparecer banner naranja |
| G.12 | Mini-resumen al final del quiz | Completar quiz → ver emoji + stats + medallas |
| G.13 | Panel "Mis Logros" en index | Aparece con 4 stats + barras; los textos dicen el nombre de la academia NUEVA |
| G.14 | **Vitrina "Mis medallas" poblada** | Aun SIN progreso, deben verse las medallas en gris/🔒 (no vacío). Si vacío → Zona E.8 (síntoma 14) |
| G.15 | **Barras de módulo en gris sin progreso** | Entrar con un alumno que tenga sesiones en OTRA academia: las barras deben verse en gris al 0%, no desaparecer (síntoma 15) |
| G.16 | **Funciones helper definidas** (síntoma 21) | Consola: `typeof refrescarRacha` → `'function'`, no `'undefined'` |
| G.17 | **Chip de lectura llega al 100%** (síntoma 22) | Leer toda la teoría (hasta chunk de victoria) → chip "Lectura completa ✅". Si se queda al 57-60%: verificar `tipo: 'irAPanel'` en `iniciarSeguimiento` |
| G.18 | **Tabs navegan correctamente** (síntoma 24) | Ir a Practico → hacer actividad → pulsar tab "Aprendo" → debe volver a la teoría |
| G.19 | **Practico siempre muestra lista de actividades** (síntoma 25) | Ir a Practico → entrar en Actividad 1 → ir a Aprendo → volver a Practico → debe mostrar lista de 3 actividades, NO actividad interrumpida |
| G.20 | **Sin bloque JS duplicado** (síntoma 20) | `grep -c "function actA_render" modulo1.html` → debe dar **1** | 

### Zona H · Convenciones obligatorias

| # | Convención | Anti-patrón |
|---|---|---|
| H.1 | Class-names en INGLÉS (`active`, `open`, `hidden`) | ❌ Mezclar con español (`activa`, `abierto`) → paneles invisibles |
| H.2 | IDs de módulo con prefijo: `nueva3_modulo1` | ❌ Inventar nuevo formato → no se atribuyen correctamente |
| H.3 | Wrapper centrado: `<div class="container">` (1100px) en index · `<div class="t3-content">` (880px) en módulos | ❌ Usar `t3-page` u otro → desalineado en monitor grande |
| H.4 | Botones: `.t3-btn .t3-btn-{azul/amarillo/verde/morado/rosa}` | ❌ Inventar `.t3-btn-siguiente`, `.t3-btn-volver` que NO existen |
| H.5 | Botones de panel-profe modales: `.btn-confirm` o `.btn-cancel` | ❌ Sin clase → cuadrados sin gracia |
| H.6 | Atributos data en HTML: `data-panel` o `data-tab` (coherente) | ❌ Mezclar ambos → `lectura-teoria.js` no detecta panel activo |

---

## 🔧 FASE 2 — SECUENCIA DE EJECUCIÓN RECOMENDADA

Para minimizar errores y deploys rotos intermedios:

### Paso 1 — Preparar archivos globales (zona E)

1. Editar `materias.js` (entrada + regex + export)
2. Editar `academia-logros.js` (path en `_detectarMateriaActual` + `_familiaModulo`)
3. Editar `nav-academias.js` (entrada)
4. Editar `panel-profe.html` (4 sub-cambios)
5. Editar `visibilidad.js` (`DEFAULT_TODAS`)
6. Editar `index.html` raíz (4 sub-cambios) — ⚠️ verificar array `ACADEMIAS` con `node -e` (bug `{ {`)
7. Editar `mascota.js` (`_FRASES_POR_ACADEMIA` + `_detectarAcademia`)
8. Editar `motivacion.js` (medallas: catálogo + 2 mapas + `CRACK_DEF` + bucle otorgamiento) — zona E.8

> ⚠️ **Orden de los `if` por prefijo**: cuando el prefijo nuevo es subcadena de otro (p.ej. `len6b_` vs `lengua_`, o `lengua6b` vs `lengua`), coloca SIEMPRE el más específico ANTES en los regex/replace de `academia-logros.js`, `materias.js`, `mascota.js` y `panel-profe.html`. Si no, `lengua` captura `lengua6b` y la atribución se va a la materia equivocada.

### Paso 2 — Crear carpeta de la academia (zona A)

1. `mkdir nueva3/`
2. Copiar `<origen>/index.html` → `nueva3/index.html`
3. Copiar `<origen>/modulo1.html` → `nueva3/modulo1.html` (template)
4. Copiar `<origen>/progreso.js` → `nueva3/progreso.js` (⚠️ actualizar lista `MODULOS` al nº real de módulos)
5. Copiar `<origen>/diploma.js` → `nueva3/diploma.js` (cambiar literales: título, pie, "Diploma de …")
6. Crear N módulos (modulo2 ... moduloN) usando el template
7. Crear `[contenido]-data.js` si aplica
8. ⚠️ **LIMPIAR ATRIBUCIÓN Y TEXTOS** (síntomas 13, 16, 17) en TODA la carpeta nueva:
   - Reemplazar id origen → id nuevo en atribuciones: `'<origen>'` → `'<nuevo>'`, `data-materia="<origen>"` → `data-materia="<nuevo>"`.
   - Reemplazar el NOMBRE propio origen en textos visibles (stats, footer, login-title, mensajes de bienvenida, banco de examen, superchuleta, diploma).
   - `examen.html`: reescribir `ALL_QUESTIONS` + `TOPIC_TO_MODULE` (keys = campo `topic` de las preguntas nuevas) + textos de pantalla.
   - Verificar: `grep -c "<id_origen>" nueva3/index.html` → 0 · `grep -rniE "<nombre_origen>" nueva3/` → solo `<polygon>` y nombres de variable.
9. ⚠️ **Arreglar la rama `!logros.sesiones`** de `mostrarLogros()` en `nueva3/index.html` para que pinte barras grises (síntoma 15).

### Paso 3 — Verificar scripts cargados (zona B)

Script bash que audita:

```bash
echo "=== Comparar academia nueva con referencia ==="
diff <(grep -oE '<script src="[^"]+"' naturales3/modulo1.html | sort -u) \
     <(grep -oE '<script src="[^"]+"' nueva3/modulo1.html | sort -u)
diff <(grep -oE '<script src="[^"]+"' naturales3/index.html | sort -u) \
     <(grep -oE '<script src="[^"]+"' nueva3/index.html | sort -u)
```

**Si hay diferencias → AÑADIR los scripts faltantes**.

### Paso 4 — Cache busting masivo (zona F)

Ejecutar el script Python de Zona F con los archivos modificados.

### Paso 5 — Deploy y test (zona G)

Subir ZIP a Netlify · hard refresh · verificar los 13 tests transversales.

### Paso 6 — Auditoría post-deploy

Pasar el **checklist completo** con el usuario:

```
- [ ] G.1 Medi entra con saludo ✓/✗
- [ ] G.2 Medi reacciona a clicks ✓/✗
- [ ] G.3 Botón flotante chat ✓/✗
- [ ] G.4 Pool específico de academia ✓/✗
- [ ] G.5 Lectura obligatoria ✓/✗
- [ ] G.6 Chip lectura visible ✓/✗
- [ ] G.7 Sonidos ✓/✗
- [ ] G.8 Cronómetro/puntos ✓/✗
- [ ] G.9 Pausa cognitiva ✓/✗
- [ ] G.10 Diploma ✓/✗
- [ ] G.11 Watchdog versión ✓/✗
- [ ] G.12 Mini-resumen quiz ✓/✗
- [ ] G.13 Panel "Mis Logros" ✓/✗
```

---

## 📋 FASE 3 — TEST AUTOMÁTICO DE COMPLETITUD

> **Cambio v221:** el script de Python que vivía aquí comprobaba una academia
> contra una de referencia, a mano y con rutas fijas. Se sustituye por
> **`scripts/validar-academias.js`**, que vive en el repo, lee el catálogo
> (`catalogo.js`) y audita **las 12 academias a la vez** contra las mismas
> invariantes. Una academia nueva entra en la auditoría sola, sin tocar nada.

```bash
node scripts/validar-academias.js          # informe por curso y academia
node scripts/validar-academias.js --breve  # solo el resumen
# Sale con código 1 si hay ERRORES. Los AVISOS no rompen el build.
```

Cada hallazgo cita el número de síntoma de este protocolo, así que el informe
se lee y se arregla sin salir de aquí.

### Qué comprueba

| # | Invariante | Síntoma |
|---|---|---|
| 1 | `div#logros-panel` existe y su `data-materia` es la academia correcta | D.1 · 13 |
| 2 | El index no llama a `obtenerHistorial`/`calcularLogros`/`medallasDeAcademia` con el id de OTRA academia | 13 |
| 3 | `activarDiploma` sin números fijos (usa `.length`) | 26 |
| 4 | La lista de módulos se deriva del catálogo, no escrita a mano | 26 · 33 |
| 5 | **La barra de las cards se pinta de verdad**: clase de card válida, `progreso.js` cargado y con `calcular()` + `detalle`, y CSS de `.card-progreso-foot` en alguna hoja que la academia cargue | 34-37 |
| 6 | Sin progreso en ESTA academia, las barras salen en gris en vez de desaparecer | 15 |
| 7 | La academia tiene medallas con su prefijo en `motivacion.js` | 14 |
| 8 | `MODULO_A_MEDALLA` cubre los módulos (salvo el último, cuyo premio es el crack) | 28 · 39 |
| 9 | La academia tiene `CRACK_DEF` (o una medalla de contador, que también vale) | 28 |
| 10 | **El crack no se regala**: ninguna medalla que prometa "Los N módulos" se otorga con un solo módulo | 38 |
| 11 | Sin funciones duplicadas por clonado ni `class="activa"` | 20 · 3 |
| 12 | **Puerta de lectura instalada y bien enganchada en TODOS los módulos**, y `nav-chunks.js` presente de forma homogénea | 40-42 |
| 13 | `diploma.js` local existe | 7 |
| 14 | Cada academia carga los mismos scripts compartidos que sus hermanas del mismo curso | B |

### Cómo leer el resultado

- **ERROR** → algo está roto para el alumno ahora mismo. Se arregla antes de desplegar.
- **AVISO** → divergencia con las hermanas. Puede ser deliberada (un script que
  solo usa esa academia, como `reto-n2-*` en Mates 3º). Revisar y decidir.

### Regla de oro que aplica el script

> Si una hermana del mismo curso lo tiene, la nueva también — salvo que haya
> una razón escrita para que no.


---

## 🎯 FASE 4 — INFORME FINAL AL USUARIO

Al terminar el alta, generar este informe:

```
═══════════════════════════════════════════════════════════════════
ACADEMIA NUEVA · [Nombre] · ALTA COMPLETADA
═══════════════════════════════════════════════════════════════════

📁 Archivos creados (zona A):
  ✓ nueva3/index.html (con D.1 estructura)
  ✓ nueva3/modulo1.html ... moduloN.html (con D.2 estructura)
  ✓ nueva3/progreso.js
  ✓ nueva3/diploma.js
  ✓ nueva3/[contenido]-data.js

🔧 Scripts cargados (zona B):
  ✓ 9 críticos · 6 de Medi · 4 en módulos · 5 en index

🌐 Archivos globales modificados (zona E):
  ✓ materias.js  ·  academia-logros.js  ·  nav-academias.js
  ✓ panel-profe.html  ·  visibilidad.js
  ✓ index.html raíz  ·  mascota.js

♻️ Cache busting (zona F):
  ✓ N HTMLs actualizados con bust de versión

🧪 Tests transversales (zona G):
  ⏳ Pendiente verificación manual tras deploy
  ⏳ Ejecutar checklist de 13 puntos

📋 Convenciones aplicadas (zona H):
  ✓ Class-names en inglés
  ✓ Wrappers de centrado correctos
  ✓ Clases de botones del portal
  ✓ Atributos data coherentes

═══════════════════════════════════════════════════════════════════
SIGUIENTE PASO: deploy a Netlify + hard refresh + auditoría manual
═══════════════════════════════════════════════════════════════════
```

---

## 🎨 FASE 3.7 — REFUERZO VISUAL (figuras que ilustran, clave para TDAH)

El contenido nuevo suele nacer **solo-texto** (o solo emojis de cabecera): un
muro que el ojo TDAH se salta. Cada concepto abstracto (estructura, ciclo,
clasificación, proceso, comparación, esquema de un problema) merece **una**
figura que lo ancle. Estándar según cómo esté hecha la academia:

- **Academias GENERADAS (1º ESO, Taller):** el generador `scripts/generar-1eso.js`
  soporta la directiva Markdown `![Pie](fig:id)`, que incrusta INLINE el SVG de
  `material/figuras/<id>.svg`. Los SVG heredan el tema oscuro y el `--accent` de
  la academia; regenerar no los pierde. Fail-open si falta el SVG.
- **Academias HECHAS A MANO (monolitos 3º/6º):** SVG inline directo en el
  `moduloN.html`, **como hermano** dentro de la tarjeta de teoría
  (`.t3-card` en 3º, `.teoria-card` en 6º), NUNCA dentro de un `.adhd-chunk`,
  de un `<script>`, ni partiendo la línea-mega de chunks.

**Dos temas, no uno:** 3º Primaria es **CLARO** (crema `#FFF8E8`, texto marrón,
fuentes grandes, tono lúdico; el inglés bilingüe solo donde hay inglés: síntoma 71); 6º y 1º ESO son **OSCUROS**
(navy). Diseña el SVG para su tema; un SVG oscuro en 3º es ilegible y viceversa.

**Estándar SVG:** `role="img"` + `<title>`/`<desc>` accesibles · `width:100%`
responsive · **texto ≥ 12 px REALES a 390 px** (viewBox de 300-340 de ancho y letra ≥ 14; con viewBox 460 la letra de 14 queda en 10 px; lo mide
`node scripts/auditar-svg.js --navegador`) · **la figura nunca muestra el ejemplo que luego pregunta el quiz** (R5 de
`auditoria-pedagogica-jogasan`) · color con función (no decorativo) ·
anti-daltonismo (símbolo/posición además del color) · ángulos de polígono con
la skill `svg-angulos-poligono`.

**Editar un monolito es crítico:** aplica la compuerta de regresión
`PLAN-REVISION-FASE4-VISUAL.md` (baseline `scripts/baseline-visual.js` → diff
`scripts/diff-visual.js` → `probar-flujo-alumno.js` → `validar-academias.js`).
El `git diff` de una figura bien insertada es **un solo bloque contiguo añadido**.

---

## 🚨 ANTI-PATRONES ESPECÍFICOS A EVITAR

Sacados de la sesión maratón Ing3 (2026-05-17/18). **Si la nueva academia muestra cualquiera de estos síntomas → bug del protocolo, NO del código**:

### Síntoma 1 · Cards del index a tope del viewport
**Causa**: Olvidé `<div class="container">` envolviendo `.modulos-grid`.
**Solución**: revisar zona D.1.

### Síntoma 2 · Paneles del módulo a tope del viewport
**Causa**: Olvidé `<div class="t3-content">` envolviendo `<section class="t3-panel">`.
**Solución**: revisar zona D.2.

### Síntoma 3 · Paneles del módulo invisibles (todos en display:none)
**Causa**: HTML usa `class="activa"` cuando CSS espera `class="active"`.
**Solución**: `grep -rn "activa\|active"` y unificar a `active`.

### Síntoma 4 · Botones "Voy a practicar →", "Siguiente" sin estilo
**Causa**: Clases inventadas `.t3-btn-siguiente`, `.t3-btn-volver` que NO existen en CSS.
**Solución**: usar `.t3-btn .t3-btn-{color}` siempre.

### Síntoma 5 · Medi no aparece o no reacciona
**Causa**: Falta `mascota-eventos.js` o `Medi.init()` no se llama.
**Solución**: revisar zona B.2 y JS inline del módulo.

### Síntoma 6 · Tap a Medi abre el chat directamente
**Causa**: Se mantuvo el comportamiento `tap corto = chat` en `mascota.js`.
**Solución**: usar el patrón v6.13.9.21: tap = pool de frases · botón flotante 💬 separado = chat.

### Síntoma 7 · No hay diploma al aprobar el examen final
**Causa**: Falta `diploma.js` local en la carpeta de la academia.
**Solución**: clonar `naturales3/diploma.js` y adaptar literales.

### Síntoma 8 · Chip de lectura desalineado en monitor grande
**Causa**: `lectura-teoria.js` posiciona `right:12px` del viewport, pero contenido centrado a 880px.
**Solución**: ya arreglado en v6.13.9.21 (chip detecta `.t3-content`).

### Síntoma 9 · Medi no da pistas pedagógicas
**Causa**: Falta `medi-pedagogia.js`, `medi-observador.js` o `medi-decisor.js`.
**Solución**: revisar zona B.2.

### Síntoma 10 · Visibilidad: se marca la academia pero al recargar desaparece
**Causa**: Falta el id en `visibilidad.js` `DEFAULT_TODAS`.
**Solución**: revisar zona E.5.

### Síntoma 11 · Profe abre "Apuntar examen" y la academia no está en el dropdown
**Causa**: Falta entrada en `panel-profe.html` MODULOS_INFO + VIS_MATERIAS.
**Solución**: revisar zona E.4.

### Síntoma 12 · El portal raíz no muestra la academia
**Causa**: Falta entrada en `nav-academias.js` o en el array del `index.html` raíz.
**Solución**: revisar zonas E.3 y E.6.

---

## 🆕 ANTI-PATRONES de la sesión lengua6b (2026-05-31)

Sacados del alta de **lengua6b** (Lengua · 2ª prueba), clonada desde `geometria2` (formato aprende-chunks). Estos NO estaban cubiertos por los 12 anteriores y aparecieron TODOS en un mismo deploy. **Son los más peligrosos porque son silenciosos: la academia "funciona" pero atribuye datos a otra materia o no pinta nada.**

### Síntoma 13 · El progreso/logros/medallas se atribuyen a la academia de ORIGEN (¡el peor!)
**Causa**: Al clonar, el `index.html` de la academia conserva el id de materia de la academia origen en TODAS las llamadas de atribución. En lengua6b quedaron 10 referencias a `'geometria2'` hardcodeadas:
- `data-materia="geometria2"` en `#logros-panel`
- `AcademiaLogros.obtenerHistorial(nombre, 'geometria2')`
- `Materias.calcularLogros(alumno, 'geometria2')`
- `Materias.sesionPertenece(s, 'geometria2')`
- `Motivacion.medallasDeAcademia('geometria2')`

**Efecto**: el alumno hace módulos de la academia nueva pero su progreso se suma a la academia origen. Bug invisible hasta que alguien revisa los datos.
**Solución**: tras clonar, `grep -c "<academia_origen>" nueva/index.html` debe dar **0**. Reemplazar TODO `'<origen>'` → `'<nueva>'` y `data-materia="<origen>"` → `data-materia="<nueva>"` SOLO dentro de la carpeta de la academia (NO en los globales, donde el origen debe seguir existiendo).
```bash
# Debe dar 0:
grep -c "geometria2\|'geometria'\|'lengua'" nueva/index.html   # según origen
```

### Síntoma 14 · "Mis medallas" sale completamente vacío (ni siquiera en gris)
**Causa**: `motivacion.js` filtra las medallas por prefijo del id (`id.startsWith('<pref>_')`). Si no defines medallas con el prefijo nuevo, el catálogo filtrado es `{}` → grid vacío. El clon NO hereda medallas porque las de la academia origen tienen OTRO prefijo.
**Solución**: registrar medallas en `motivacion.js` (ver nueva **Zona E.8** abajo). La vitrina pinta cada medalla bloqueada (🔒, `opacity:.4`) hasta ganarla — pero solo si existen en el catálogo con el prefijo correcto.

### Síntoma 15 · Las barras de progreso NO aparecen aunque no haya progreso
**Causa**: `mostrarLogros()` en el index tiene DOS ramas de estado vacío:
1. `!alumno.sesiones_totales` (alumno nuevo del todo) → SÍ pinta barras grises.
2. `!logros.sesiones` (tiene sesiones en OTRAS academias pero ninguna en esta) → en el clon de geometria2 esta rama hace `logros-modulos.style.display='none'`, **ocultando las barras**.

El caso (2) es el habitual en un portal con varias academias, así que las barras "desaparecen" para casi todos.
**Solución**: en la rama `!logros.sesiones`, en vez de ocultar, pintar las barras en gris al 0% (copiar el bloque de la rama 1):
```javascript
document.getElementById('logros-modulos').style.display = 'block';
document.getElementById('modulos-bars').innerHTML = Object.entries(MODULOS_INFO).map(function(e){
  var info=e[1];
  return '<div class="mod-row"><span class="mod-icon">'+info.icon+'</span>'+
    '<span class="mod-name">'+info.name+'</span>'+
    '<div class="mod-bar-wrap"><div class="mod-bar-fill" style="width:0%;background:'+info.color+'"></div></div>'+
    '<span class="mod-pct" style="color:var(--muted)">·</span></div>';
}).join('');
```
**Nota**: este bug vive en el bloque inline heredado de `geometria2`, así que `geometria2` lo tiene también.

### Síntoma 16 · Textos visibles dicen el nombre de la academia ORIGEN
**Causa**: Plantillas de string (template literals) dentro de `mostrarLogros()` y otros bloques tienen el nombre de la materia origen escrito a mano: "verás tu progreso de Geometría", "Correctas en Geometría", "Examen Geometría", "¡Empezamos Geometría!", footer "Portal de Repaso Geometría", login-title "Academia Geometría". El `sed` de identidad no los pilla si buscas solo el id en minúscula.
**Solución**: tras clonar, buscar el nombre PROPIO de la academia origen (con tilde y mayúscula) en TODA la carpeta:
```bash
grep -rniE "geometr|polígono|triángulo|cuadrilátero|ortocentro" nueva/*.html nueva/*.js
```
Revisar uno a uno: los `<polygon>` decorativos en SVG y los nombres de variable (`--accent-geo`) son inofensivos; el texto visible NO.

### Síntoma 17 · El examen y la superchuleta arrastran contenido de la academia origen
**Causa**: `examen.html` tiene su PROPIO banco de preguntas embebido (`const ALL_QUESTIONS`), un mapa `TOPIC_TO_MODULE`, y textos de pantalla ("X temas: Polígonos…", "¡Dominas la geometría!"). `superchuleta.html` y `diploma.js` tienen contenido y títulos de la materia origen ("Diploma de Geómetra", "GEOMETRÍA 2 · 6º").
**Solución**: reescribir banco + `TOPIC_TO_MODULE` (las keys del mapa DEBEN coincidir con el campo `topic` de las preguntas nuevas), textos de pantalla, secciones de superchuleta y literales del diploma. Verificar con el mismo grep del síntoma 16.

### Síntoma 18 · En formato aprende-chunks NO hay lectura obligatoria ni chip de lectura
**Causa (NO es bug)**: el formato aprende-chunks (clonado de `geometria2`) **no llama** a `LecturaTeoria.iniciarSeguimiento()`. La "lectura" se hace recorriendo los chunks (botón "Siguiente →" hasta "Ir al Quiz"). Por eso el quiz NO se bloquea y NO aparece el chip flotante de lectura — igual que en el piloto Geometría 2.
**Decisión de diseño** (no lo arregles por reflejo):
- **Dejarlo así**: los chunks ya son lectura guiada secuencial.
- **Activar lectura obligatoria**: llamar `LecturaTeoria.iniciarSeguimiento('<pref>_moduloN','teoria',{...})` en cada módulo, PERO adaptar el `optsQuizIntercept` porque el formato chunk navega con `showTab`/`irAPanel` y paneles con id `teoria`/`quiz` (sin prefijo `panel-`), mientras `lectura-teoria.js` espera `panel-teoria`/`panel-quiz` y `.t3-tabs`.

### Síntoma 19 · La academia pasa TODAS las auditorías técnicas pero el CONTENIDO está incompleto o mal agrupado (lengua6b v6.13.9.111)
**Causa**: las FASES 1-3 verifican fontanería (scripts, atribución, medallas, barras, sintaxis) pero **NO verifican que el contenido didáctico sea correcto, completo y bien organizado según el material real del profe**. Una academia puede dar "✅ 0 errores" y aun así:
- Tener **menos categorías de las que pide el currículo concreto**: en lengua6b el módulo de Determinantes se entregó con 4 tipos cuando el esquema de pizarra del profe tenía **7** (faltaban artículos, relativos y interrogativos/exclamativos).
- **Agrupar mal los temas**: el "Tema 6" se metió como un solo módulo (Teatro + Tipos de oraciones + Análisis) cuando pedagógicamente eran **3 módulos** distintos.
- Usar el currículo "genérico" de una búsqueda web en lugar del **material específico del profe** (lista de cotejo, apuntes, ejercicios corregidos, esquemas).

**Efecto**: el alumno repasa con contenido que no cubre lo que entra en SU examen, o con una estructura que no encaja. Bug invisible para la auditoría técnica; solo se detecta contrastando con el material.
**Solución**: ejecutar la **FASE 3.5 — Validación de contenido** (abajo) ANTES de dar la academia por cerrada. Regla de oro: **el material del profe manda sobre el currículo genérico y sobre lo que ya tenía la academia de origen.**

## 🆕 ANTI-PATRONES de la sesión Sociales 3º (2026-06-01) — Contenido escrito desde cero sobre plantilla nat3

Cuando el **contenido de los módulos se escribe desde cero** (en vez de reutilizar el JS de la academia origen), el proceso de sustitución del bloque JS puede dejar cascadas de bugs invisibles que solo aparecen en el navegador.

### Síntoma 20 · El bloque JS gigante de la academia origen sobrevive junto al contenido nuevo
**Causa**: al reemplazar el panel-aprendo y añadir un bloque `<script>` nuevo con el contenido, el **bloque `<script>` original de la academia origen** (40-60k chars con toda la lógica de actividades, `cambiarTab`, referencias a `btn-ir-practico`, etc.) **subsiste** en el HTML. Resultado: funciones duplicadas (`actA_render`, `irAPanel`, `cambiarTab`) compiten entre sí, los listeners del bloque antiguo llaman a elementos que no existen → TypeError silencioso o botones que no hacen nada.
**Síntoma en navegador**: botones sin respuesta al click, errores `Cannot read properties of null` en consola, panel Practico vacío.
**Solución**: al reemplazar el contenido JS de un módulo clonado, localizar el `<script>` de >5k chars (el principal de la academia origen) y **reemplazarlo ENTERO** con el nuevo. Verificar: `grep -c "function actA_render" modulo1.html` → debe dar **1**, nunca 2.

### Síntoma 21 · Funciones helper inline perdidas (`refrescarRacha`, `reaccionAcierto`, `reaccionFallo`, `mirarPreguntaActiva`, `toastMedalla`, `lanzarConfeti`, `ptsPop`, `refrescarPuntosTop`)
**Causa**: estas funciones **no están en ningún script externo** — viven **inline** en el bloque `<script>` principal de cada módulo de nat3 (líneas ~348-445). Al reemplazar ese bloque, desaparecen. El JS del contenido nuevo las llama y el navegador lanza `ReferenceError: refrescarRacha is not defined`.
**Síntoma en navegador**: actividades y quiz no responden al hacer click; consola muestra `ReferenceError` en la primera interacción.
**Solución**: **siempre copiar el bloque de helpers** al inicio del nuevo `<script>` principal. Son 8 funciones que van siempre juntas al inicio del bloque 0:
```
refrescarPuntosTop · ptsPop · lanzarConfeti · toastMedalla
reaccionAcierto · reaccionFallo · mirarPreguntaActiva · refrescarRacha
```

### Síntoma 22 · `LecturaTeoria.iniciarSeguimiento` con `tipo:'cambiarTab'` en academia que usa `irAPanel`
**Causa**: el bloque `<script>` de lectura-teoria (heredado de nat3) instala el interceptor con `{ tipo: 'cambiarTab' }`. Las academias bilingüas/nuevas usan `irAPanel`. `lectura-teoria.js` sí soporta `tipo:'irAPanel'` (línea ~1121) pero si se le pasa `cambiarTab` intenta interceptar `window.cambiarTab` que no existe → el chip se queda parado en el porcentaje inicial y **nunca llega al 100%**.
**Síntoma en navegador**: chip "Lee teoría" parado al 57-60%; logs muestran `[LT] _instalarInterceptor ejecutándose, tipo: cambiarTab`.
**Solución**: cambiar `{ tipo: 'cambiarTab' }` por `{ tipo: 'irAPanel', panelQuizId: 'demuestro' }`. Reemplazar el interceptor `window.cambiarTab = function(id){...}` por:
```js
var _origIrAPanel = window.irAPanel;
window.irAPanel = function(id) {
  if (['demuestro','practico'].indexOf(id) !== -1) LecturaTeoria.pausarSeguimiento();
  else LecturaTeoria.reanudarSeguimiento();
  if (_origIrAPanel) _origIrAPanel.call(this, id);
};
```

### Síntoma 23 · IDs de sub-pantallas desajustados: HTML usa `pant-A/B/C`, JS busca `pant-actA/actB/actC`
**Causa**: nat3 tiene sus pantallas de actividad con `id="pant-A"`, `id="pant-B"`, `id="pant-C"` y stages pre-declarados (`actA-objeto`, `actA-pregunta`, `actA-opciones`). El JS escrito desde cero puede usar `pant-actA/B/C` → `getElementById('pant-actA')` devuelve `null` → `TypeError: Cannot read properties of null (reading 'classList')` al primer click.
**Solución**: alinear IDs. Opción recomendada: añadir `<div id="actA-stage"></div>` dentro de `pant-A` y usar ese div como contenedor donde el JS inyecta su `innerHTML`. El HTML de nat3 se conserva y el JS solo necesita el stage vacío.

### Síntoma 24 · Los tabs principales (Aprendo / Practico / Demuestro) no navegan al pulsar
**Causa**: en nat3 los tabs `.t3-tab[data-tab]` y pasos `.t3-mapa-paso[data-tab]` reciben sus listeners dentro del bloque JS principal (que usa `cambiarTab`). Al reemplazar ese bloque, los listeners no se replantaron → tabs visualmente activos pero muertos.
**Síntoma**: desde Practico, pulsar "Aprendo / Learn" no vuelve a la teoría.
**Solución**: en el `DOMContentLoaded` del módulo:
```js
document.querySelectorAll('.t3-tab[data-tab],.t3-mapa-paso[data-tab]').forEach(function(btn) {
  btn.addEventListener('click', function() { irAPanel(btn.dataset.tab); });
});
```

### Síntoma 25 · Al entrar en Practico desde el tab, aparece una actividad a medias en vez de la lista de actividades
**Causa**: `irAPanel('practico')` activa `panel-practico` pero no resetea las sub-pantallas internas. Si el alumno estaba en `pant-A` y vuelve a Aprendo para releer, al volver a Practico ve la actividad interrumpida.
**Solución**: `irAPanel` debe llamar a `volverARuta()` cuando el destino es `'practico'`:
```js
function irAPanel(id) {
  // ... activar panel, actualizar tabs ...
  if (id === 'practico') volverARuta();
}
```

---

## 🆕 ANTI-PATRÓN de la sesión Sociales 3º · Los 4 archivos globales que hay que tocar al dar de alta una academia nueva

Además del checklist de 7 zonas, **4 archivos globales JS** requieren mapeos nuevos para que barras, medallas y seguimiento funcionen:

| Archivo | Qué añadir | Efecto si falta |
|---|---|---|
| `materias.js` → `claveAMateria()` | `if (/^soc3_/.test(clave)) return 'sociales3';` | Las sesiones no se filtran por materia → barras vacías, logros mezclados |
| `academia-logros.js` → `_familiaModulo()` | `if (/^soc3_/.test(clave)) return 'sociales3';` | Sesiones se abren con `academia_id` incorrecto → progreso se atribuye a otra materia |
| `motivacion.js` → catálogo `MEDALLAS` | 7 medallas `soc3_*` con `academia:['sociales3']` | Vitrina "Mis medallas" vacía aunque se completen módulos |
| `progreso.js` de la academia | `materia: 'Sociales 3º'` y `MATERIA: 'Sociales 3º'` | Texto incorrecto en panel de logros |

**Patrón de mapeo** (mismo para cualquier academia nueva con prefijo `<pref>_`):
```js
// materias.js — claveAMateria()
if (/^soc3_/.test(clave)) return 'sociales3';  // ANTES del fallback return null

// academia-logros.js — _familiaModulo()  
if (/^soc3_/.test(clave)) return 'sociales3';  // ANTES del return '?'
```
**Test rápido en consola** tras deploy: `Materias.claveAMateria('soc3_modulo1')` debe devolver `'sociales3'`. Si devuelve `null` o `undefined` → falta el mapeo.


---

---

## 🆕 ANTI-PATRONES de la sesión v220-v221 — Auditoría de consistencia entre academias

Estos NO se detectan leyendo una academia aislada: solo salen al **comparar las
12 contra la misma invariante**. Todos eran silenciosos — nada fallaba, algo
simplemente no aparecía. Los cubre `scripts/validar-academias.js`.

### Síntoma 33 · La lista de módulos escrita a mano en el index se queda atrás
**Causa**: cada `index.html` declaraba su propio `var MODS = [...]`. Al añadir un
módulo nuevo había que acordarse de actualizarlo y nadie se acordaba.
**Efecto real**: `lengua6b` mostraba 8 cards y su diploma contaba 7 (el módulo 8
no existía para el diploma). `matematicas3` tenía **dos** arrays distintos, con
12 y 10 de sus 13 módulos.
**Solución**: derivar del catálogo, nunca escribir la lista.
```javascript
var MODS    = Catalogo.modulosRequeridos('matematicas3');  // diploma y examen
var TODOS   = Catalogo.academia('matematicas3').modulosKeys;  // cards y progreso
```
**Módulos de repaso**: los que se practican pero no se exigen se marcan en el
catálogo y `modulosRequeridos()` los excluye:
```javascript
{ id:'matematicas3', modulosRepaso:['mat3_modulo10'], … }
```
**Test**: `grep -n "MODS *= *\[" */index.html` → 0 resultados.

### Síntoma 34 · La card usa `mod-card` y el portal busca `module-card`
**Causa**: conviven dos convenciones. `cards-progreso.js` solo buscaba
`.module-card`.
**Efecto**: en Lengua 3º e Inglés 3º las cards **no mostraban ningún progreso**.
No hay error en consola: el selector simplemente no encuentra nada.
**Solución**: `document.querySelectorAll('.module-card, .mod-card')`. Al crear
una academia, usar `module-card`.

### Síntoma 35 · `progreso.js` de la academia con otra API que el resto
**Causa**: `primero/progreso.js` exponía `obtenerProgreso()` en vez de
`calcular()`, y su retorno no traía el campo `detalle`.
**Efecto**: `cards-progreso.js` lanza `TypeError` al leer `p.detalle[clave]` y la
card se queda sin barra. El error va dentro de un `.catch()` → invisible.
**Solución**: toda academia expone `calcular(historial)` devolviendo
`{ modulos, detalle, porcentaje, completados, total }`, con
`detalle[clave] = { pct, completo, intentos }`.
**Test**: `grep -L "calcular" */progreso.js` → vacío.

### Síntoma 36 · El index no carga su propio `progreso.js` y tira de un apaño inline
**Causa**: `lengua3/index.html` tenía un
`if (typeof Progreso === 'undefined') { window.Progreso = { MODULOS:[…] } }`
con un módulo duplicado y sin `calcular()`.
**Efecto**: mismo que el 35, pero más difícil de ver porque `Progreso` SÍ existe.
**Test rápido en consola**: `Object.keys(Progreso)` debe incluir `calcular`.

### Síntoma 37 · La barra se pinta pero sale sin estilo
**Causa**: los estilos de `.card-progreso-foot` vivían **solo** en `mejoras.css`,
que las academias de 3º y 1º no cargan.
**Efecto**: la barra aparece como texto suelto sin formato.
**Solución**: los estilos están ahora en `tema-3primaria.css` (3º/1º) y en
`mejoras.css` (6º). **No cargues `mejoras.css` entero en una academia de 3º**:
tiene 64 selectores, entre ellos `.module-card` y `.topbar`, y te restylea todo.
**Test en navegador**: `getComputedStyle($('.card-progreso-foot')).paddingTop`
distinto de `0px`.

### Síntoma 38 · El "crack" se regala por aprobar el último módulo
**Causa**: `MODULO_A_MEDALLA` otorga **sin condiciones** (solo pide ≥60%). Al
mapear el último módulo directamente al crack, la medalla que dice *"Los 7
módulos"* se ganaba haciendo uno solo. `CRACK_DEF` sí exige el resto, pero el
mapa se le adelanta.
**Afectaba a**: lengua, naturales3, ingles6, ingles3, sociales3.
**Solución**: el último módulo **no** va en `MODULO_A_MEDALLA`. Su premio lo da
`CRACK_DEF`, y el bloque `todos_modulos` lo otorga en cuanto están todas las
temáticas, sea cual sea el orden en que se hagan.
**Test** (node, sin navegador): completar SOLO el último módulo no debe dar el
crack; completarlos todos, sí.

### Síntoma 39 · Módulos sin ninguna medalla
**Causa**: se añaden módulos y se olvida la medalla.
**Efecto**: en 1º Primaria, *Las Formas*, *Los Números* y *Las Letras* no daban
**nada** al completarse, mientras que los tres primeros sí.
**Solución**: una medalla temática por módulo (salvo el último) en el catálogo,
en `MODULO_A_MEDALLA` **y** en el mapa retroactivo. Los tres sitios o ninguno.

### Síntoma 40 · `panelQuizId` vs `quizPanelId` — la puerta de lectura no cierra
**Causa**: `lectura-teoria.js` lee `opts.quizPanelId`, pero la mitad de los
módulos pasan `panelQuizId`. Cae al valor por defecto (`'panel-quiz'`), que esos
módulos no usan → la puerta queda en un panel inexistente.
**Efecto**: el alumno entra a los ejercicios sin cumplir el tiempo mínimo.
**Solución**: el motor acepta las dos grafías. Al crear módulos nuevos usar
`quizPanelId`.

### Síntoma 41 · La puerta de lectura cierra UN solo panel
**Causa**: el interceptor comparaba `panelId === _quizPanelId`.
**Efecto**: bloqueaba `actA` y el alumno entraba por `actB`, `actC`, `quiz`,
`juego`, `problema`, `construye` o `reto-n2`. **9 de cada 13 módulos** dejaban
pasar.
**Solución**: la regla se invierte — abierto lo que es teoría o consulta
(`teoria`, `aprendo`, `panel-teoria`, `panel-aprendo`, `chuleta`,
`superchuleta`), **cerrado todo lo demás**.

### Síntoma 42 · Envolver `window.irAPanel` es frágil: depende del orden de los `<script>`
**Causa**: hay módulos que **redefinen** la función después del envoltorio
(Sociales 3º declara `function irAPanel` en un bloque posterior) y otros que
declaran un tipo de interceptor pero navegan con otra función (Naturales 3º
declara `tipo:'cambiarTab'` y usa `irAPanel`).
**Efecto**: el envoltorio se pierde y la puerta desaparece sin avisar.
**Solución**: además del envoltorio, una **guarda de click en fase de captura**
sobre `document`, que corre antes que cualquier handler del módulo:
```javascript
document.addEventListener('click', function (e) {
  var el = e.target.closest && e.target.closest('[data-tab],[data-panel],[onclick]');
  if (!el) return;
  var destino = el.getAttribute('data-tab') || el.getAttribute('data-panel');
  if (!destino) {
    var m = (el.getAttribute('onclick') || '')
      .match(/(?:irAPanel|cambiarTab|showTab)\(\s*['"]([^'"]+)['"]/);
    if (m) destino = m[1];
  }
  if (destino && _esPanelDeEjercicios(destino) && !estaDesbloqueadoQuiz(_clave)) {
    e.stopImmediatePropagation(); e.preventDefault();
    _mostrarToastBloqueado();
  }
}, true);
```

---

## 🔐 LAS DOS PUERTAS PARA LLEGAR A LOS EJERCICIOS

Hay **dos reglas independientes**, con motores distintos que no se conocen entre
sí. Las dos son intencionadas y las dos tienen que estar:

| Puerta | Motor | Qué exige | Qué cierra |
|---|---|---|---|
| **Tiempo de lectura** | `lectura-teoria.js` | `MIN_SEGUNDOS` (120s) de permanencia **activa** en teoría **+** llegar al final | Todo panel que no sea teoría ni consulta |
| **Actividades hechas** | `nav-chunks.js` | Haber recorrido los chunks de teoría (`_lecturaOK`) | `quiz` y `demuestro` — **solo si el módulo tiene chunks**; sin ellos el motor es inerte a propósito |

**No basta con pulsar botones**: el contador de `lectura-teoria.js` solo suma
mientras la pestaña de teoría está visible y hay actividad del usuario.

Atajo legítimo: si el alumno ya sacó `PCT_LIBRE` en ese módulo, entra libre
(está repasando algo que ya domina). Y si suspendió, el umbral baja a
`MIN_SEGUNDOS_RELEER` (60s).

**Al crear una academia, comprobar las dos:**
```bash
# Todos los módulos deben llamar a iniciarSeguimiento y cargar nav-chunks.js
grep -L "LecturaTeoria.iniciarSeguimiento" nueva3/modulo*.html   # vacío
grep -L "nav-chunks.js"                    nueva3/modulo*.html   # vacío
```
Y que el `tipo` declarado sea la función que el módulo usa de verdad: si declara
`cambiarTab` pero navega con `irAPanel`, la puerta no se instala (síntoma 22).

---

---

## 🆕 ANTI-PATRONES de la sesión v224 — Pasada profunda EJECUTANDO los 94 módulos

Ninguno de estos se ve leyendo el código ni cargando la página: solo aparecen
al **interactuar** — abrir el quiz y responder. Son los más caros porque el
alumno trabaja y su esfuerzo no queda registrado.

### Síntoma 43 · Completar el quiz no guarda NADA (el más caro)
**Causa**: una línea que lanza excepción **por encima** de la llamada a
`registrarQuiz`, dentro de la misma función. En Geometría 6º, `updateScore()`
hacía `document.getElementById('score').textContent = …` y no existía ningún
elemento con `id="score"` (solo quedaban las clases CSS `.score-bar` y
`.score-num` de un marcador perdido por el camino). El TypeError cortaba la
función justo antes del `registrarQuiz` de la línea siguiente.
**Efecto**: el alumno responde las 18 preguntas, ve el feedback de cada una, y
**no queda constancia de nada**: ni progreso, ni medalla, ni diploma, ni sesión
en el panel del profe. Sin un solo error visible para él.
**Regla**: `registrarQuiz`/`registrarMiniQuiz` van **lo primero** de su función,
o el resto va protegido. Nunca detrás de manipulación del DOM sin guarda.
```javascript
// MAL — si falta el elemento, el registro no llega
function updateScore(){
  document.getElementById('score').textContent = correct + ' / ' + done;
  if (done === questions.length) AcademiaLogros.registrarQuiz(…);
}
// BIEN
function updateScore(){
  var s = document.getElementById('score');
  if (s) s.textContent = correct + ' / ' + done;
  if (done === questions.length) AcademiaLogros.registrarQuiz(…);
}
```
**Test**: responder el quiz entero en el navegador espiando `registrarQuiz`.
Es la ÚNICA forma de cazarlo (ver FASE 3.6).

### Síntoma 44 · Variable de quiz usada y nunca declarada
**Causa**: `respuestas_quiz` (el detalle para la lupa del profe) se usaba en
`answer()` pero no se declaraba: 4 de los 7 módulos de Geometría. En un quinto
estaba declarada **600 líneas por debajo** de su primer uso.
**Efecto**: `ReferenceError` en el primer click de cada pregunta → sin feedback,
sin marcador y sin registro.
**Test**: `grep -c "let respuestas_quiz\|var respuestas_quiz\|const respuestas_quiz"`
debe dar 1 por módulo, y la declaración debe ir **antes** del primer uso.

### Síntoma 45 · Juego de medallas duplicado y muerto
**Causa**: Lengua 6º tenía DOS juegos completos para sus 7 módulos:
`len_*` colgado de `lengua_1..lengua_7` (las claves reales, funciona) y
`lengua_m1..m7 + lengua_crack` colgado de `lengua_modulo1..7` (claves que no
existen en ninguna parte).
**Efecto**: el alumno veía **15 medallas en su vitrina y solo podía ganar 7**.
Las otras 8 salían bloqueadas para siempre, sin forma de saber por qué.
**Test de alcanzabilidad** — que ninguna medalla sea imposible:
```
Para cada medalla del catálogo, comprobar que hay al menos un camino:
  · MODULO_A_MEDALLA          · CRACK_DEF
  · umbral/campo (contador)   · desbloquearMedalla() literal
  · otorgada INDIRECTAMENTE desde la carpeta de la academia
    (p.ej. VerbosData.chequearMedallasJuego → intentar(id))
Y que toda clave de CRACK_DEF exista de verdad en modulosKeys.
```
⚠️ Cuidado con los falsos positivos: las medallas de juego se otorgan por
indirección y un `grep` de `desbloquearMedalla('id')` no las encuentra.

### Síntoma 46 · Botón cuyo onclick llama a una función que no existe
**Causa**: el botón se clona pero la función se queda en la academia de origen.
En Naturales 6º el botón 📽️ de modo proyector estaba en los 5 módulos y
`togglePresentacion()` no estaba definida: cada click, `ReferenceError`.
**Test**: recoger todos los `onclick="fn(...)"` del módulo y comprobar
`typeof window[fn] === 'function'`.
```javascript
const llamadas = new Set();
document.querySelectorAll('[onclick]').forEach(el => {
  const m = (el.getAttribute('onclick')||'').match(/^\s*([A-Za-z_$][\w$]*)\s*\(/);
  if (m) llamadas.add(m[1]);
});
[...llamadas].filter(fn => typeof window[fn] !== 'function');   // debe ser []
```
**Extra**: comprobar también que la función hace algo. `togglePresentacion`
pone `data-mode="presentation"` en el `<html>`… y **ningún CSS del proyecto
tiene reglas para ese atributo**. El botón funciona y no cambia nada.

### Síntoma 47 · `getElementById(...).algo` sin guarda
Generalización de los síntomas 43, 44 y 46. Es el patrón que más daño hace en
este proyecto porque los módulos se clonan y el HTML se reorganiza, pero el JS
sigue buscando ids que ya no están.
**Barrido estático** (rápido, se puede correr en cada deploy):
```javascript
// Por cada módulo: getElementById('X').(addEventListener|innerHTML|classList|
// style|textContent) donde id="X" no aparece en el HTML
```
⚠️ Da falsos positivos con elementos creados en tiempo de ejecución
(`innerHTML` con el id dentro): verificar antes de tocar.

---

## ⚠️ REGLA DE ORO DE LAS PUERTAS: FALLAR ABIERTO, NUNCA CERRADO

Una condición que **no se puede medir** no debe bloquear. Si una puerta se
apoya en algo que falta, el alumno se queda encerrado sin forma de salir, y no
hay ningún error en consola que lo delate.

Los dos motores ya llevan válvula, y **cualquier puerta nueva debe llevarla**:

| Motor | Condición que podría faltar | Válvula |
|---|---|---|
| `nav-chunks.js` | El módulo no tiene chunks de teoría | `_totalTeoria() > 0` — sin chunks el motor es inerte y no bloquea |
| `lectura-teoria.js` | El panel de teoría declarado no existe en el DOM | Cuenta el tiempo igualmente y avisa por consola. **Antes devolvía `false` y el contador se quedaba clavado a 0 para siempre** |
| `lectura-teoria.js` | La página no scrollea (scrollea un contenedor interno), así que el 90% nunca se alcanza | Con el **doble** del tiempo mínimo en teoría, se da el scroll por hecho |

**Corolario para academias nuevas**: si una parte de la regla no aplica a tu
formato (p.ej. no hay chunks), **no la instales**; no la instales "por si
acaso" ni la dejes en un estado que no se pueda satisfacer.

**Test de encierro** — hazlo con cada módulo nuevo:
```javascript
// Romper a propósito las dos condiciones y comprobar que el contador SIGUE
document.querySelectorAll('.t3-panel').forEach(x => x.classList.remove('active'));
document.getElementById('panel-aprendo').id = 'roto';
// …esperar ~15s moviendo el ratón…
LecturaTeoria.getSegundos('clave_modulo');   // debe ser > 0, no 0
```
El validador comprueba la parte estática: que el panel de teoría declarado
exista en el DOM, y que todo módulo **con** chunks cargue `nav-chunks.js`.

---

## 🌐 FASE 3.6 — VERIFICACIÓN EN NAVEGADOR (lo que el análisis estático no ve)

Los síntomas 34-37 y 40-42 **pasan todas las auditorías de texto** y aun así el
alumno no ve la barra o entra sin leer. Solo se cazan ejecutando la página.

```bash
python3 -m http.server 8899 &     # servir el proyecto
```

Con Playwright, y **con sesión de alumno** (sin ella muchos módulos ni instalan
la puerta: el código arranca con `if (!alumno) return;`):

```javascript
await page.addInitScript(() => {
  sessionStorage.setItem('academia_sesion', JSON.stringify({
    sesion_id:'t', alumno:'alumno prueba', inicio:new Date().toISOString(), modulos:{} }));
  localStorage.setItem('academia_ultimo_alumno', 'alumno prueba');
});
// Las peticiones externas están bloqueadas en CI: cortarlas para que no cuelgue
await page.route('**://**', r => /127\.0\.0\.1/.test(r.request().url()) ? r.continue() : r.abort());
await page.goto(URL, { waitUntil: 'domcontentloaded' });   // 'load' NO dispara: fuentes externas
```

| Test | Cómo | Esperado |
|---|---|---|
| **Barra de las cards** | Stub de `AcademiaLogros.obtenerHistorial` con un historial falso + `CardsProgreso.repintar()` | Cada card de módulo con un `.card-progreso-foot`, y con estilo (`paddingTop` ≠ `0px`) |
| **Puerta cerrada** | Click en cada `[data-tab]` que no sea teoría | Ningún panel de ejercicios se activa |
| **Puerta abierta** | Sembrar `localStorage['lt_cache_v1']` por alumno (en minúsculas) y clave del módulo: `{"alumno prueba":{"mat4b_modulo6":{"segundos":180,"scrollOk":true}}}`. Sin el alumno y la clave la puerta sigue cerrada y el test «ve» un botón roto que no lo está | Los paneles de práctica sí abren |
| **Medallas** | `Motivacion.moduloCompletado(100, 10, clave)` | Devuelve la medalla temática del módulo |
| **Navegación en 2 anchos** | Viewport 390×844 **y** 1400×900: contar filas distintas de `.t3-mapa-paso` visibles (`getBoundingClientRect().top`) y si `.t3-tabs` y `.t3-mapa` se ven a la vez con los mismos destinos; captura de pantalla de los dos | Una sola fila; nunca dos barras que llevan a lo mismo; el chip «Lee teoría» no tapa ningún botón (síntoma 64) |

**Mira las capturas, no solo los números.** Un módulo sin errores JS puede
salir visualmente roto: el síntoma 64 pasó 2 días en producción en 36 módulos
porque las pruebas solo miraban errores y móvil.

**La puerta cierra TODOS los ejercicios, no solo el quiz.** `lectura-teoria.js`
deja libres solo la teoría, las chuletas y el paso a paso; Practico y el resto
siguen cerrados hasta 2 min de lectura activa + llegar al final (o nota previa
alta). «Pulso Practico y no cambia» con el aviso «Lee la teoría primero para
desbloquear los ejercicios» es la puerta funcionando, no un bug (25-sep).

**Siempre con grupo de control**: ejecuta el mismo test contra la versión
anterior del archivo. Varias veces en esta sesión el test daba "roto" y el
control demostraba que ya estaba así antes — o que el roto era el test.

---

## ✅ FASE 3.5 — VALIDACIÓN DE CONTENIDO (obligatoria antes de cerrar)

La fontanería puede estar perfecta y el contenido mal. Antes de entregar, contrasta CADA módulo contra el material de referencia del profe (pregunta 9 de FASE 0):

1. **Cobertura de la lista de cotejo**: por cada ítem de la lista de cotejo / rúbrica, comprueba que hay un módulo (o sección) que lo cubre. Marca ítem por ítem. Ninguno debe quedar huérfano.
2. **Completitud de categorías**: si el profe enseña N tipos/clases/casos de algo (7 tipos de determinantes, 6 modalidades de oración, las clases de adverbio…), el módulo debe tenerlos TODOS, no un subconjunto. Contrasta contra el esquema/apuntes, no contra tu memoria.
3. **Agrupación pedagógica**: un "tema" del temario puede necesitar varios módulos si junta subtemas con entidad propia. Pregunta al usuario cómo quiere dividirlo en vez de meterlo todo en uno.
4. **Convenciones y notación del profe**: usa la MISMA notación que el material (p.ej. en análisis sintáctico: `SN SUJ`/`SV PV`, `D·N·CN`, `CD/CCL/CCT/CCM`, `ATRIBUTO`+`PN`). No inventes etiquetas.
5. **Reutiliza el material existente**: ejemplos, ejercicios corregidos, frases del profe y apuntes en HTML de academias previas → mejor que inventar, porque ya están validados y el alumno los reconoce.
6. **Rescata los "tips críticos"**: en módulos de refuerzo, extrae las reglas-trampa que el profe marca (ej.: «ser/estar/parecer → predicado nominal + atributo»; «¡Siéntate ya! lleva ¡! pero es exhortativa»).

**Checklist mínimo de contenido** (rellenar con el usuario):
```
- [ ] Cada ítem de la lista de cotejo tiene módulo/sección que lo cubre
- [ ] Cada categoría tiene TODOS sus tipos (contrastado con el esquema del profe)
- [ ] Los temas grandes están divididos en módulos con sentido pedagógico
- [ ] La notación coincide con la del material del profe
- [ ] Quizzes y ejemplos reutilizan/respetan el material aportado
- [ ] **El quiz sale de la teoría** (11-oct): cada pregunta del quiz final evalúa un ejemplo/ejercicio resuelto de la teoría del módulo con datos nuevos (matriz de cobertura pregunta → ejemplo; nada sin enseñar, nada copiado; `node scripts/buscar-copias-teoria.js`)
- [ ] Si el módulo sale de los apuntes del profe: entrada `apuntes: { 'moduloN.html' (o 'juegos.html'): { tema, fecha } }` en su academia de `catalogo.js`entrada `apuntes: { 'moduloN.html': { tema, fecha } }` en su academia de `catalogo.js` (etiqueta «📒 Apuntes»; regla del usuario 3-oct; validador sAP)
- [ ] Si el módulo sale de los apuntes del profe: entrada `apuntes: { 'moduloN.html' (o 'juegos.html'): { tema, fecha } }` en su academia de `catalogo.js` (etiqueta «📒 Apuntes»; regla del usuario 3-oct; validador sAP)
- [ ] Tips críticos del profe incluidos en los módulos de refuerzo
- [ ] **Figuras SVG (síntoma 80, usuario 12-oct):** cada bloque de teoría de todo módulo nuevo o rehecho lleva SU figura SVG (`![alt](fig:id)` en `material/figuras/`), y también los juegos, el flipbook y cualquier página de estudio que se cree; `node scripts/validar-academias.js` (check FG) para el deploy si falta; la figura no regala el quiz (R5) y su texto es ≥ 14 px en un viewBox de 320
- [ ] **Chuleta con apoyos visuales (usuario 12-oct):** la sección `## 📋 CHULETA` no es solo texto plano — debe llevar tablas de resumen (estado, qué incluye, dato clave…), diagramas de orden, matrices "si ves X → esfera Y", SVGs explicativos o cualquier recurso visual que ayude a repasar. Subsecciones con **negrita** en lugar de `###` para no crear bloques de teoría nuevos que el validador exige con figura
- [ ] Si la academia lleva contenido en INGLÉS: teoría, ejemplos y enunciados bilingües (inglés + español pegado, otro formato, `bilingue.css`) y nada del ejercicio traducido (síntoma 71; `node scripts/auditar-bilingue.js`)
- [ ] Cada bloque de teoría (≤ ~120 palabras) acaba en una micro-pregunta «❓ ¿Lo pillas?» (`.mq-q.mq-chunk` + `mini-quiz.js?v=4`; generadas: bloque `❓ ¿Lo pillas?` en `bloqueN.md`), que no copia el quiz ni las actividades. Contrato, sintaxis y qué registra: `COORDINACION.md` § «Micro-pregunta» (TDAH, 2-oct); aviso `sMQ` del validador si está mal formada
```

- [ ] **Batería de pistas y figuras (usuario, 17-oct):** `node scripts/auditar-pistas.js <academia>[:N]` sin avisos en lo que has tocado (ver abajo)

### 🧪 Batería de pruebas de CONTENIDO (usuario, 17-oct-2026) — se pasa SIEMPRE antes de subir

«Que las figuras expliquen bien y que la solución no se vea implícita en la pregunta.» Va junto a las pruebas
técnicas (validador, `--comprobar`, Playwright) y se cuenta en el resumen. Todo módulo, quiz, examen, micro-pregunta o figura
nuevo o tocado pasa estas cinco; cada aviso se revisa a mano (son heurísticos) y lo que es real se arregla en el mismo PR:

| # | Qué se comprueba | Cómo |
|---|---|---|
| 1 | **La pregunta no lleva la respuesta**: la correcta no está escrita en el enunciado (A1), no se distingue por su forma — la única mucho más larga, la única con paréntesis, «/» o «porque» (A2) —, no hay opciones repetidas (A3), ningún paréntesis del enunciado la da (A4). Cubre quiz, test de `examenes.json` y las «❓ ¿Lo pillas?» de la teoría | `node scripts/auditar-pistas.js <academia>[:N]` |
| 2 | **La figura explica**: `<title>` + `<desc>` de verdad (≥ 8 palabras que digan qué se ve, B1), con rótulos (B3) y pertinente a SU bloque (comparte palabras clave con el `###` donde está, B2) y su `![alt]` sin corchetes, que si no la figura no se pinta (B4) | la misma `auditar-pistas.js` |
| 3 | **La figura no regala el quiz** (R5): no dibuja el ejemplo con los datos que luego se preguntan | `node scripts/auditar-figuras-quiz.js` |
| 4 | **El quiz sale de la teoría y no la copia**: matriz pregunta → ejemplo (a mano) y ningún ejercicio con los números de los ejemplos | `node scripts/buscar-copias-teoria.js` |
| 5 | **Se ve y se lee a 390 px**: captura de cada figura nueva a 390 px (texto ≥ 12 px reales), mirada con los ojos, junto a su bloque | `node scripts/auditar-svg.js --navegador` + captura |

Además, a mano: la micro-pregunta y el quiz no se responden por descarte obvio (distractores del mismo tipo y tamaño),
la explicación (`exp`) justifica la correcta con el razonamiento, y en inglés no se traduce lo que resuelve el ejercicio (s71).
La deuda que destapa `auditar-pistas.js` en módulos que NO tocas se anota (o se propone como tarea aparte), no se mezcla en el PR.

**Regla**: no se anuncia una academia como "terminada" hasta pasar esta fase. "0 errores técnicos" ≠ "contenido correcto".

---

## 📌 RECORDATORIO FINAL

**El protocolo lo creamos PRECISAMENTE porque Ing3 se clonó MAL** desde Mat3/Nat3. Si sigues este checklist al pie de la letra, la próxima academia se desplegará completa al primer intento.

**Cuando dudes**: vuelve a la academia de referencia (Nat3 para 3º, Ing6 para 6º) y compara. La regla es **"si una hermana lo tiene, la nueva también"**.

**Antes de dar una academia por terminada, en este orden**:
1. `node scripts/validar-academias.js` → **0 errores**.
2. FASE 3.6 en navegador con sesión de alumno: barra visible y con estilo, y las
   dos puertas (tiempo de lectura + actividades) cerrando de verdad.
3. FASE 3.5 de contenido contra el material del profe.

**Tres verdades que cierran el protocolo**:
1. *Fontanería* (FASES 1-3): "si una hermana lo tiene, la nueva también".
2. *Ejecución* (FASE 3.6): **"que el código esté bien NO significa que el alumno lo vea"**. La barra sin estilo, la card con la clase equivocada y la puerta de lectura que no cierra pasan todas las auditorías de texto.
3. *Contenido* (FASE 3.5): **"0 errores técnicos NO significa que el contenido esté bien"**. El material del profe (lista de cotejo, apuntes, esquemas, ejercicios corregidos) manda sobre el currículo genérico y sobre lo heredado de la academia de origen. No cierres una academia sin contrastar el contenido módulo a módulo contra ese material.

---

## 🆕 ANTI-PATRONES de las sesiones v159–v215 — Auditoría de deuda técnica

Estos síntomas se descubrieron durante la auditoría sistemática de deuda técnica (v210–v215). No son bugs de clonado per se, sino **errores de mantenimiento que se propagaron a academias ya desplegadas** y que una academia nueva puede heredar si se clona de las fuentes incorrectas.

### Síntoma 26 · `activarDiploma` con número de módulos hardcodeado
**Causa**: al clonar, `activarDiploma` hereda el número fijo de módulos de la academia origen (`if (n === 7)`, `/ 7 *`, `n + '/7 módulos'`). Si la nueva academia tiene un número distinto, o si se añade un módulo después, el diploma **nunca se desbloquea** sin ningún error visible.
**Síntoma en navegador**: la barra de diploma se queda al X% aunque el alumno haya completado todos los módulos.
**Solución**: siempre usar `MODS.length` dinámico. El array `MODS` debe estar declarado antes de `activarDiploma`:
```js
var MODS = ['nueva3_modulo1', 'nueva3_modulo2', /* ... */ 'nueva3_moduloN'];

async function activarDiploma(historial) {
  // ...
  if (n >= MODS.length) { /* desbloquear */ }
  var pctVal = Math.round((n / MODS.length) * 100);
  if (label) label.textContent = n + ' / ' + MODS.length + ' módulos';
  var faltan = MODS.length - n;
}
```
**Test**: `grep -n "=== [0-9]\|/ [0-9]\|'[0-9] módulos'" nueva3/index.html` → debe dar 0 resultados dentro de `activarDiploma`.

### Síntoma 27 · `VerbosEngine` no llama a `Motivacion.moduloCompletado`
**Afecta solo a academias que usan `VerbosEngine`** (actualmente: `ingles6`). `VerbosEngine` registra el quiz en Supabase con `registrarQuiz`, pero **no llama a `Motivacion.moduloCompletado`**. Las medallas de módulo y el crack nunca se otorgan en tiempo real — solo llegan por retroactivo al volver al index.
**Síntoma**: el alumno termina un módulo de verbos con ≥60% y no ve ningún toast de medalla.
**Solución**: tras el bloque `try { AcademiaLogros.registrarQuiz(...) }` en `verbos-engine.js`, añadir:
```js
try {
  if (window.Motivacion && Motivacion.moduloCompletado) {
    var medallas = Motivacion.moduloCompletado(pct, total, _clave);
    if (medallas && medallas.length) {
      setTimeout(function() {
        medallas.forEach(function(m, i) {
          setTimeout(function() {
            if (typeof toastMedalla === 'function') toastMedalla(m);
          }, i * 600);
        });
      }, 800);
    }
  }
} catch (e) { console.warn('[verbos-engine] moduloCompletado error:', e); }
```
**Nota**: `QuizEngine` ya llama a `moduloCompletado` internamente desde v203. Solo afecta a `VerbosEngine`.

### Síntoma 28 · Retroactivo de medallas incompleto en `otorgarMedallasConHistorial`
**Causa**: al añadir una academia nueva a `motivacion.js`, es habitual copiar el bloque retroactivo de otra academia. Si el número de módulos o el criterio del crack difieren, se produce una inconsistencia silenciosa entre `otorgarMedallasConHistorial` (ruta del index) y `otorgarMedallasRetroactivas` (ruta del superexamen/módulo).
**Síntomas típicos**:
- Crack que no aparece aunque se hayan completado todos los módulos (criterio incorrecto).
- Medalla de un módulo concreto que nunca aparece aunque se haya aprobado (falta entrada en el mapa retroactivo).
**Verificación**: comparar manualmente los mapas y condiciones de crack entre las dos funciones para la academia nueva. Deben ser idénticos en criterio.
**Test**: en consola del index:
```js
// Simular historial con todos los módulos al 100%
var testHist = { modulos: {} };
['nueva3_modulo1','nueva3_modulo2'/* ... */].forEach(k => {
  testHist.modulos[k] = { mejor_pct: 100, total_correctas: 5 };
});
console.log(Motivacion.otorgarMedallasConHistorial(testHist));
// Debe incluir el crack y todas las medallas de módulo
```

### Síntoma 29 · `avanzarChunk` referencia `panel` como variable inexistente (lazy-init roto)
**Causa**: en módulos clonados de `ingles3` que tienen el bloque de lazy-init dentro de `avanzarChunk`, la variable `panel` se usa como si fuera global — pero solo existe como parámetro dentro de `irAPanel`. Al navegar con el botón "¡Ya lo tengo!" desde la victoria del chunk, `panel` vale `undefined` y `iniciarQuiz()` nunca se llama.
**Síntoma en navegador**: quiz completamente vacío al pulsar el botón de victoria de los chunks.
**Afecta a**: módulos que heredan el bloque `// v6.13.9.46: disparar lazy-init` de `ingles3`.
**Solución**: sustituir `panel === 'quiz'` por lectura del panel activo desde el DOM:
```js
// En lugar de: if ((panel === 'quiz') && !_quiz_init ...)
var _panelActivo = (function() {
  var p = document.querySelector('.t3-panel.active');
  return p ? p.id.replace('panel-', '') : '';
})();
if (_panelActivo === 'quiz' && !_quiz_init && typeof iniciarQuiz === 'function') {
  iniciarQuiz(); _quiz_init = true;
}
```

### Síntoma 30 · Chips de `%` por módulo ausentes en cards del index
**Causa**: el JS de `pintarChipsProgreso` (3º) o `pintarProgresoCards` (6º) está definido pero los spans `data-modulo` no existen en el HTML de las cards, o la función no se llama tras obtener el historial.
**Síntoma**: las cards muestran solo la barra global de diploma, sin porcentaje individual por módulo.
**Solución en 3 pasos**:
1. Añadir `<span class="mod-chip" data-modulo="nueva3_moduloN"></span>` dentro de cada card (antes del `</a>` de cierre).
2. Añadir llamada a `pintarChipsProgreso(historial)` justo después de `otorgarMedallasRetroactivas` en el bloque de carga del historial.
3. Añadir CSS para `.mod-chip[data-pct]` y `.mod-chip.aprobado` (sin esto el span existe pero es invisible).
**Para 6º** (patrón `module-progress`): añadir `<span class="module-progress" data-modulo="eng6_moduloN"></span>` y CSS de `.module-card.has-progress .module-progress`.

### Síntoma 31 · Banco de preguntas del reloj analógico sin contexto AM/PM
**Afecta a**: módulos con reloj analógico donde la hora puede ser AM o PM (ej. "Las 3 en punto" = 03:00 o 15:00).
**Causa**: el banco no incluye los campos `emoji` y `momento`, y no hay div `caza-contexto` en el HTML.
**Síntoma pedagógico**: el alumno falla por ambigüedad horaria, no por no saber leer el reloj.
**Solución** (patrón de M12/M13):
```js
// En el banco de preguntas:
{hora:3, min:0, texto:'Las 3 en punto', hAngle:90, mAngle:0,
 emoji:'☀️', momento:'de la tarde'}

// En el HTML, antes de #hora-opciones:
<div id="caza-contexto" style="display:none;text-align:center;
  font-family:'Fredoka One',cursive;font-size:1.1rem;color:#7C3AED;margin-bottom:8px;"></div>

// En mostrarPreguntaReloj():
var ctxEl = document.getElementById('caza-contexto');
if (ctxEl && q.emoji) {
  ctxEl.textContent = q.emoji + ' ' + q.momento;
  ctxEl.style.display = 'block';
}
```

---

## 📋 CHECKLIST DE TRAZABILIDAD — verificación rápida post-deploy (v215)

Añadir a la auditoría post-deploy (Zona G) estos checks adicionales:

| # | Check | Cómo verificar |
|---|---|---|
| G.21 | **Diploma con MODS.length dinámico** | `grep -n "=== [0-9]\|/ [0-9]\+" nueva3/index.html` dentro de activarDiploma → 0 resultados |
| G.22 | **moduloCompletado llamado** | Terminar un quiz con ≥60% → debe aparecer toast de medalla inmediatamente (no solo al volver al index) |
| G.23 | **Retroactivo consistente** | Simular historial completo en consola → crack y todas las medallas de módulo presentes |
| G.24 | **Chips % en cards** | Entrar con alumno con progreso → cada card debe mostrar su % individual |
| G.25 | **Quiz no vacío tras chunks** | En módulos con chunks: llegar a victoria y pulsar botón de práctica → quiz poblado (no vacío) |


---

## Síntoma 32 · Sección nueva invisible — colisión de clase CSS

**Causa**: al añadir HTML nuevo (panel, tab, bloque de teoría) se usa un nombre de clase que ya existe en el sistema con `display:none` por defecto.
**Síntoma**: el elemento aparece en el DOM con contenido (`innerHTML.length > 0`) pero `offsetHeight = 0` y no se ve en pantalla.
**Síntoma en navegador**: sección completamente en blanco aunque el JS no da error.

**Clases reservadas en academias JoGaSan — NO usar como contenedores genéricos:**

| Clase | Comportamiento real |
|---|---|
| `.t3-panel` | `display:none` — panel de actividad, visible solo si tiene clase `active` |
| `.aprende-chunk` | controlado por `avanzarChunk` — oculto por defecto |
| `.mod-body` | `display:none` — acordeón, visible con `style=""` vía `toggleMod` |

**Verificación en Playwright antes de declarar done:**
```python
result = page.evaluate("""() => {
    var el = document.querySelector('.mi-clase-nueva');
    return {
        height: el ? el.offsetHeight : -1,
        display: el ? getComputedStyle(el).display : 'N/A'
    };
}""")
# Si height=0 y display=block → colisión CSS
```

**Solución**: buscar la clase en el `<style>` del módulo antes de usarla:
```python
css = h[h.find('<style>')+7:h.find('</style>')]
import re
hits = re.findall(r'\.mi-clase[^{]*\{[^}]+\}', css)
# Si aparece display:none → elegir otro nombre
```

**Añadir a checklist G (post-deploy):**
- G.26: nueva sección visible → `offsetHeight > 0` en Playwright

---

## 🆕 ANTI-PATRONES de la sesión v234 — Atribución por URL y trazabilidad del profe

Dos listas a mano MÁS que se quedan atrás al dar de alta una academia. Ninguna
la caza el validador actual y ninguna da error: algo simplemente se atribuye mal
o sale genérico. Síntoma disparador real: *"el progreso de los módulos no se
mapea en la zona de barras de las nuevas"* — que resultó NO ser del render.

### Síntoma 48 · `_detectarMateriaActual()` (academia-logros.js) no conoce la academia nueva
**Causa**: `_detectarMateriaActual()` era una cadena de `if (p.indexOf('/xxx/')…)`
escrita a mano que NO se actualiza al dar de alta una academia (faltaban las 6
de 1º ESO y el Taller). Al entrar el alumno, `iniciar()` crea la sesión con
`academia_id: null`.
**Efecto (doble y silencioso)**:
- El **examen** de esa academia se atribuye por defecto a `'geometria'` (en
  `sesionAMaterias()`, `materias.add(sesion.examen.materia || 'geometria')`).
- El **retroactivo de medallas** post-quiz corre con prefijo `''` y no encuentra
  los módulos.
- **Lo que lo ENMASCARA**: al registrar el quiz, `registrarQuiz` auto-completa
  `academia_id` vía `_familiaModulo(modulo)` (que SÍ usa el catálogo), así que
  las barras de módulo del index tiran igual y el bug pasa desapercibido. Solo
  salta en exámenes, medallas retroactivas y en sesiones sin quiz.
**Solución**: derivarlo del catálogo, como ya hacen `claveAMateria` y
`_familiaModulo`. Casar la URL por `carpeta`, **de la más larga a la más corta**
(para que `/lengua6b/` no caiga en `/lengua/`, ni `/geometria2/` en `/geometria/`):
```js
if (typeof Catalogo !== 'undefined' && Catalogo.academias) {
  const cands = Catalogo.academias()
    .map(a => ({ id:a.id, carpeta:a.carpeta||a.id }))
    .sort((x,y) => y.carpeta.length - x.carpeta.length);
  for (const c of cands) if (p.indexOf('/'+c.carpeta+'/') >= 0) return c.id;
  return null;
}
```
**Test (node, sin navegador)**: para cada academia del catálogo,
`_detectarMateriaActual()` con `/{carpeta}/…` debe devolver su id (y las
colisiones lengua/lengua6b, geometria/geometria2 bien resueltas).

### Síntoma 49 · panel-profe: nombre/emoji/color de academia con mapa a mano
**Causa**: el detalle por alumno del panel del profe tenía **tres** mapas a mano
`academia_id → {emoji, nombre, color}` (el `mapa` de emojis, `NOMBRES_ACAD` y
`academiaColor()`) sin las academias nuevas.
**Efecto**: en "Actividad por academia" del alumno, las nuevas salían con su **id
crudo** (p.ej. `matematicas1eso`) y en **color gris**; el emoji caía en el
genérico 📚. No rompe, pero el profe no las reconoce.
**Solución**: fallback al catálogo ANTES del genérico (conservando el mapa a mano
como override para no cambiar el aspecto de las viejas):
```js
if (mapa[id]) return mapa[id];
if (typeof Catalogo !== 'undefined' && Catalogo.academia) {
  const a = Catalogo.academia(id);
  if (a && a.color) return a.color;   // o a.navNombre||a.nombre, o a.icono||a.icon
}
return GENERICO;
```

### Regla de diagnóstico · barras siempre en gris/0% = ATRIBUCIÓN, no render
Si la "zona de barras al final" (Mis Logros) sale **siempre** gris/0% aunque el
alumno tenga progreso, **el problema casi nunca es el render** (`academia-logros-ui.js`):
es la **atribución** — `academia_id` de la sesión, `claveAMateria`/`academiaDeClave`,
o `sesionPertenece`. El render se verifica en segundos con una **simulación DOM en
Node** (stub de `document.getElementById` + `AcademiaLogrosUI.pintar(histFalso, cfg)`
y leer `#modulos-bars`); la atribución necesita el flujo real de sesión (navegador
con sesión de alumno sembrada).

### Propuesta para `scripts/validar-academias.js` (aún no implementada)
- **Invariante**: toda academia del catálogo debe resolverse por URL en
  `_detectarMateriaActual()` (leer la función, comprobar que cada `carpeta` casa).
- **Invariante**: los mapas de `panel-profe.html` (emoji/nombre/color) no deben
  dejar fuera ninguna academia del catálogo sin fallback a `Catalogo.academia`.

### Regla de oro ampliada · la familia "listas a mano que se quedan atrás"
El catálogo (`catalogo.js`) es la fuente única, pero quedan sitios que lo
duplican a mano y hay que migrar o darles fallback al catálogo. Inventario vivo:
`MODS`/`MODULOS_INFO` del index (sínt. 33), `_detectarMateriaActual` (sínt. 48),
los 3 mapas de `panel-profe` (sínt. 49), y el mapa de prefijos del retroactivo en
`academia-logros.js`. **Al dar de alta una academia, grepea su id/carpeta/prefijo
y comprueba que aparece —o cae al catálogo— en TODOS ellos.**

---

## 🆕 ANTI-PATRÓN de la ronda 18-sep — Trabajo duplicado entre sesiones paralelas

Este proyecto tiene **varias sesiones de Claude trabajando el mismo repo a la
vez** (ver `COORDINACION.md`). Cuando dos sesiones abordan la misma mejora sin
coordinarse, el bug no es de código — es de **proceso** — pero el resultado es
el mismo tipo de deuda silenciosa que el resto de este protocolo.

### Síntoma 50 · La misma mejora ("paso a paso") implementada dos veces con mecanismos distintos
**Causa**: la PR #44 (`claude/great-knuth-f9atxn`) añadió una caja inline en
Teoría (`🧑‍🏫 Analizamos juntos` / `🧑‍🏫 Lo reconocemos juntos` / `🧠 Ejemplo
paso a paso`) en 34 módulos de lengua6b, lengua3, ingles6, ingles3, geometria2
y primero. En paralelo, la PR #42 (`claude/quirky-rubin-1ggf0h`) siguió
añadiendo commits **al mismo tiempo** y creó una **pestaña nueva** (`🧮 Paso a
paso`) para las mismas academias — sin que ninguna de las dos sesiones supiera
de la otra hasta que se comparó `main` antes de fusionar.
**Efecto**: si se fusionan ambas tal cual, el mismo módulo termina con **dos
mecanismos distintos conviviendo** (caja inline + pestaña) para explicar lo
mismo, con contenido y colores diferentes — confuso para el alumno y doble
trabajo de mantenimiento a partir de ahí. Detectarlo tarde obliga a un merge
manual módulo a módulo para elegir un solo mecanismo, en vez de decidirlo una
vez.
**Por qué es silencioso**: cada PR por separado pasa `validar-academias.js`
con 0 errores y se ve bien en el navegador — el conflicto solo existe **entre
sesiones**, no dentro de una.
**Solución / prevención**:
1. Antes de añadir "paso a paso" (o cualquier mejora transversal a varias
   academias) a una academia hand-authored, mira las PRs abiertas y sus
   commits recientes en `COORDINACION.md` — es el punto de mayor duplicación
   de trabajo detectado hasta ahora en este proyecto.
2. **Un solo mecanismo por academia**: si una academia ya tiene una convención
   previa para algo (p.ej. geometria2 M2-M7 ya usaba pestaña independiente
   antes de esta ronda), esa es la que se respeta ahí — no se introduce una
   segunda.
3. Si dos PRs ya divergieron, no se resuelve "a lo que caiga" del merge
   automático: se elige un mecanismo módulo a módulo y se quita la caja/pestaña
   del lado que no se queda.
**Test**: `grep -c "paso a paso"` sobre un módulo no basta (puede matchear
contenido legítimo no relacionado, como en un texto instructivo). Verificar en
navegador que solo existe **un** contenedor con el título del recuadro/pestaña
por módulo, no dos mecanismos coexistiendo.


---

## 🆕 ANTI-PATRONES del 24-sep — Igualar las familias 3º B y 4º B (PR #97 y siguiente)

Todas estas academias pasaban el validador de entonces y "se veían bien", pero
el alumno no progresaba. Ahora cada síntoma es un **error** del validador: un
módulo nuevo no está terminado hasta que `node scripts/validar-academias.js`
no añade errores respecto a `main` y la FASE 3.6 pasa en navegador.

### Síntoma 51 · Llamada a una función que NO existe en la librería compartida
`CajaErrores.registrar(…)`, `AcademiaLogros.guardarResultado/registrarIntento/init`,
`Motivacion.getGanadas/sumarPuntos/otorgarMedallasConHistorial`. Van dentro de
`try{}` o de un `if (x.fn)`: no rompen nada, simplemente no ocurre (el quiz no se
guarda, la caja queda vacía, la vitrina se repinta a 0). El validador carga las
librerías reales en un sandbox y compara. APIs correctas:
`registrarQuiz(clave, correctas, total, …)`, `registrarMiniQuiz(clave, correctas, total)`,
`CajaErrores.registrarFallo(clave, {q, opts, ans})` (ans = índice), `Motivacion.moduloCompletado(pct, total, clave)`,
`Motivacion.sincronizarMedallas()`. ⚠️ Tampoco lo escribas así en un comentario: s51 lo detecta.

### Síntoma 52 · `obtenerHistorial('<idAcademia>')`
El 1er argumento es el ALUMNO → se busca un alumno inexistente y el portal sale
siempre al 0 %. Correcto: `obtenerHistorial(alumno, '<idAcademia>')`.

### Síntoma 53 · `registrarActividad` usado en un módulo de academia
Es para apps transversales (`registrarActividad(academiaId, clave, c, t)`): si el
1er argumento no es un id de catálogo, **cierra la sesión del alumno y abre otra**
atribuida a una academia inexistente. En módulos: `registrarMiniQuiz('<módulo>_actA', aciertos, total)`,
**una sola vez al terminar la actividad** (registrar tras cada respuesta con el
acumulado guarda un 100 % si la 1ª es correcta).

### Síntoma 54 · Error de sintaxis en un `<script>` inline
Un paréntesis de menos (`if(a||'').indexOf(…)`) anula TODO el bloque: ni pestañas,
ni actividades, ni quiz. Lengua 3º B (M2-M6) y Sociales 3º B (M1-M6) estuvieron así
desde el alta. El validador compila cada `<script>` inline con `vm.Script`.

### Síntoma 55 · `registrarQuiz` con los argumentos desordenados
`registrarQuiz(pct, total, 'x_modulo1')` guarda un quiz con clave numérica. La
clave va primero.

### Lecciones de proceso
- **Reemplazos masivos siempre con `assert` del nº de coincidencias.** Un `replace`
  que no encuentra el texto (p.ej. `var x = {}` con espacios) falla en silencio.
- **El test de navegador debe ejercitar lo que hace el alumno** (responder, fallar,
  terminar), no solo cargar la página: los síntomas 53-55 solo se ven así.
- **Grupo de control con el MISMO validador** sobre `main` (worktree) antes de comparar cifras.
- **Plantilla única por familia**: los index de 3º B/4º B salen de la misma
  plantilla probada (datos de catálogo + tarjetas); no se parchea cada uno a mano.

### Síntoma 56 · HTML GENERADO editado a mano (deriva generador ↔ HTML)
Las academias con `material/<curso>/<carpeta>/` (1º ESO, 4º sin B, Refuerzo,
Taller de Problemas, Problemas 3-4) salen de `scripts/generar-1eso.js`. Editar su
HTML (añadir un SVG, corregir un ejemplo) funciona… hasta la próxima regeneración,
que lo borra sin avisar: así se acumularon 86 SVG y una corrección pedagógica.
- Contenido → `bloqueN.md`; figura → `material/figuras/<id>.svg` + `![pie](fig:<id>)`;
  estructura → el generador. Luego `node scripts/generar-1eso.js --curso <c> <carpeta>`.
- `--comprobar` regenera en memoria y falla si algo cambiaría (ignora `?v=N`); el
  validador lo ejecuta (s56) y el deploy se para.
- Conflictos al fusionar `main` en HTML generados: no se resuelven a mano. Mirar si
  `main` cambió contenido (diff sin `?v=`), llevarlo al material, regenerar.

---

## 🆕 ANTI-PATRONES del 24-sep (tarde) — conteo, atribución, medallas y repaso (PR #87 · #101 · #103 · #107)

Origen: Santi aparecía en el panel con **−37 respuestas falladas**. Se investigó
primero con SQL de solo lectura en producción y cada fallo se reprodujo con el
código viejo antes de arreglarlo.

### Síntoma 57 · Un acierto cuenta dos (o tres) veces: la respuesta no se «cierra»
Dos variantes del mismo error: la entrada que ya respondió sigue viva.
- **Mates 3º (9 actividades, módulos 1-9):** el botón «Comprobar» se convertía en
  «Siguiente →» **conservando su `addEventListener`**, así que cada respuesta se
  evaluaba dos veces → 12/6 en el panel.
  Arreglo: `data-comprobado="1"` al comprobar (y `if (btn.dataset.comprobado==='1') return;`),
  o `input.disabled = true` en `makeOperacion`.
- **Rincón de Santi:** la opción correcta seguía activa ~900 ms tras acertar. Cada
  toque de más sumaba un acierto **y saltaba una ronda**: doble toque → veía 2 de 4
  preguntas y se guardaba 4/4; triple → 6/4 (fallos negativos) y 3 pantallas de
  resultado (premios repetidos). Arreglo: `cerrarRonda()` cierra cada ronda UNA vez
  en todos los tipos, los fallos durante el cierre no cuentan y `fin()` corre una vez.
- **Cómo cazarlo:** en navegador, **doble y triple clic** en la respuesta correcta y en
  «Comprobar»; exige `correctas <= total` y una sola pantalla de resultado.
  Una mecánica nueva debe avanzar por la función común (`acierto()`), no por su cuenta.

### Síntoma 58 · La sesión entera se guarda en otra asignatura (atribución por URL)
`Catalogo.academiaDePath` comparaba `indexOf('/'+carpeta) === p.length - carpeta.length - 1`:
con una carpeta de la misma longitud que la ruta daba **`-1 === -1` → verdadero**.
99 rutas de 40 academias mal (la URL de carpeta de Netlify `/<acad>/`, el `start_url`
de la PWA de Santi).
- Arreglo: comprobar `idx !== -1`; `registrarQuiz` corrige `academia_id` por el
  **prefijo del módulo** (el prefijo manda sobre la URL; cubre cachés con el catálogo viejo).
- Check **«0 · URL»** en `validar-academias.js`: prueba `/<acad>/`, `/<acad>/index.html`
  y cada módulo contra `academiaDePath`. Con el catálogo viejo daba 36 errores.
- Regla general: todo `indexOf(...) === algo` calculado debe excluir antes el `-1`.
- Si hay datos mal atribuidos en prod: SQL de reparación con **copia de seguridad y
  script de deshacer**, revisado por el usuario antes de aplicar.

### Síntoma 59 · Pulsar una medalla hace cosas distintas según la academia
En 6º abría una guía que no tenía esa medalla; en 4º/1º ESO el primer toque no hacía
nada; en otras, nada. Ahora es **una sola ficha** (`ficha-medalla.js`, lo carga
`motivacion.js`) que escucha en **captura** sobre `document`.
- Academia nueva: sus medallas deben llevar `[data-medid]`, `[data-medalla]`,
  `.medalla#med-<id>` o `[data-ficha-*]`; si no, la ficha no las reconoce.
- El texto sale de `Motivacion.comoSeConsigue(id)` (`MODULO_A_MEDALLA`/`CRACK_DEF`).
  Medallas que no son de módulo → `COMO_MANUAL`; las que solo da el retroactivo →
  `COMO_MODULO_EXTRA`. Sin entrada, la ficha sale vacía.
- Vitrina: `Motivacion.pintarVitrina(el, acad)` en vez de pintarla a mano.
- Si una academia ya tiene su propio «¿Cómo se gana?» (el Rincón, con voz), se
  respeta el suyo (síntoma 50).

### Síntoma 60 · Un guardado diferido pisa una marca recién puesta
El guardado a Supabase con retardo de 1,5 s guardaba una **copia antigua** de la
sesión y borraba la marca `.repaso` que `AcademiaLogros.anotarModulo` acababa de
poner. Arreglo: `anotarModulo` sustituye también la copia pendiente; `registrarQuiz`
conserva `.repaso` al mejorar nota.
- Regla: todo `setTimeout(guardar, N)` debe leer el estado **al disparar**, no
  capturarlo al programarse.

### Síntoma 61 · La puerta de lectura no «oye» el avance: quiz cerrado para siempre
Mates 3º M12 avanza la teoría con su propia `mostrarChunk(n)` (los chunks se
**acumulan**, no se sustituyen). `nav-chunks.js` solo se enteraba de
`avanzarChunk`/`irAChunk`, así que contaba «1 de 4» aunque el alumno leyera todo, y
el quiz no se abría nunca. Arreglado envolviendo también `mostrarChunk` en
`nav-chunks.js` (v3). Mismo árbol que M13 (`chunkNext`, ya resuelto con `_puedoMedir`).
- Academia/módulo nuevo con navegación de chunks propia: o usa `avanzarChunk(n)`,
  o `nav-chunks.js` tiene que envolver su función. Si no, la puerta **cierra**.
- Prueba: recorrer la teoría ENTERA y exigir que el quiz abra; y sin leer, que no
  abra (`probar-flujo-alumno.js` ya pulsa el último botón de los chunks acumulados).

### Síntoma 62 · Botones que llaman a una función que la plantilla no trae
Sociales 4º B: los 16 botones del «Paso a paso» de cada módulo llamaban a
`responderPap()`, que solo existía en Naturales 4º B (con otro marcado: `.pap-paso`
frente a `.pap-step`). Pulsar no hacía nada y el alumno se quedaba en el paso 1.
Caso del síntoma 46; lo caza `scripts/auditar-modulos-navegador.js` («onclick a
funciones inexistentes»). Al copiar un bloque entre academias hermanas, copia
**también** su función y comprueba que el marcado coincide.

### Repaso proactivo — lo que hereda una academia nueva
`repaso.js` lo carga `motivacion.js`: la academia nueva lo hereda si carga
`motivacion.js` y sus claves siguen el patrón de prefijo. Módulo flojo → sesión
normal; aprobado → `modo='repaso'`, que `alumnos_totales` **no suma** (bolsa aparte).
Ver `REPASO-PROACTIVO.md`.

### Lecciones de proceso (24-sep tarde)
- **El validador para el deploy** (`netlify.toml`: `validar-academias.js && sincronizar-version.js && build-index.js`).
  Un check nuevo que destapa errores antiguos se arregla en el mismo PR.
- Tras subir `CACHE_VERSION` en `sw.js`: `node scripts/sincronizar-version.js`
  (el `--comprobar` falla si no).
- Antes de cada merge: `git fetch`, `git merge-tree` contra `main` sin conflictos y
  `expectedHeadSha`. Los `?v=` finales, siempre por encima de los de `main`
  (dos sesiones usaron los mismos números con contenido distinto).
- Conflictos típicos: líneas `?v=` contiguas de dos scripts distintos → se conservan ambas.
- El servidor local (`python3 -m http.server`) se cae entre llamadas: lánzalo en
  segundo plano y compruébalo con `curl` antes de culpar al código.
- **Modo proyector: retirado por decisión del usuario.** No reimplementarlo.

### Paso que faltaba · la academia nueva no la ve nadie
Dar de alta en `catalogo.js` NO la hace visible: la visibilidad es una cascada
lista propia del alumno → lista de su curso (`visibilidad_curso`) → defecto. Al
terminar una academia, añádela en el panel del profe → «Materias por curso» a la
lista de su curso, y a la lista propia de los alumnos que la tengan. Las 10
academias B de 3º/4º estuvieron un día entero sin que ningún alumno las viera.

### Móvil · el mapa de pasos es la navegación (24-sep, v281)
- En ≤600 px `tema-3primaria.css` muestra el mapa de pasos en una fila con scroll
  y OCULTA `.t3-tabs` si hay un `.t3-mapa` delante: no añadas pestañas que dupliquen
  el mapa, y si una pestaña lleva a un sitio que el mapa no tiene, ponlo en el mapa.
- Si el mapa va pegado a la barra (sin `.t3-hero` delante) queda bajo el chip
  «Lectura» y el botón de pantalla completa: la regla `.nav-rail + .t3-mapa` lo baja.
- Botones: siempre la clase base `t3-btn` + variante. Una clase inventada
  (`t3-btn-avanzar` sola) deja un botón de texto plano de 19 px.
- Verifica con zona táctil REAL (`elementFromPoint` a ±21 px del centro), no con
  `getBoundingClientRect`: el `::after` que agranda la zona no cuenta en el rect.

### Síntoma 63 · Banco de datos usado sin declarar
Una actividad que lee `MI_BANCO.length` o `MI_BANCO[i]` sin que `MI_BANCO` exista
revienta al abrirla ("MI_BANCO is not defined"), pero la sintaxis es válida y s54
no lo ve. Inglés 3º M9 (actividad B, `DID_ROME`) estuvo así desde su creación.
El validador (s63) lo detecta. Al crear una actividad, escribe el banco en el mismo
commit y juégala entera en el navegador.

### Síntoma 64 · Botones Aprendo/Practico/Demuestro en COLUMNA y repetidos (escritorio)
Las familias **3º B** (Mates) y **4º B** (las 6) se crearon el 23-sep sin partir
de `_plantilla/modulo-template.html` y luego se clonaron entre sí: pusieron los
`<button class="t3-mapa-paso">` **sueltos dentro de `.t3-mapa`**, sin el
envoltorio `<div class="t3-mapa-pasos">`, y además `.t3-tabs` con los mismos
destinos. Solo `.t3-mapa-pasos` pone los pasos en fila, así que en escritorio salían
**apilados en columna** encima de unas pestañas idénticas (captura del alumno en
Mates 4º B M6). El arreglo de móvil (v281) no lo vio porque solo miró ≤600 px.
- Arreglo (v287, `tema-3primaria.css`): en >600 px, si un `.t3-mapa` tiene los pasos
  sueltos y detrás hay `.t3-tabs`, se oculta el mapa y las pestañas bajan 60 px para
  no quedar bajo el chip «Lee teoría» (fijo, y=52-92). En móvil, al revés: se ve el
  mapa y se ocultan las pestañas.
- **Regla para módulos nuevos**: copia el mapa de la PLANTILLA, no de una hermana
  (el clon hereda sus atajos). Pasos siempre dentro de `.t3-mapa-pasos`.
- El validador (**s64**, error) para el deploy si hay pasos sueltos en `.t3-mapa`
  **sin** `.t3-tabs` detrás: ahí el CSS no tiene con qué sustituirlo y el alumno
  ve la columna como única navegación.
- Prueba: FASE 3.6 «Navegación en 2 anchos» con captura en móvil y escritorio.

### Síntoma 65 · El chico contesta por patrón, no porque lo sepa (regla del usuario, 25-sep)
**Regla para TODA la academia:** al repetir un quiz o una actividad (más tarde u
otro día) cambian el orden de las preguntas **y** el de las opciones; no van juntas
dos preguntas muy parecidas, ni una cuya respuesta se acaba de ver en la anterior
(en su enunciado o en la explicación que sale al contestar); y la correcta no cae
en la misma posición una y otra vez. Si no, el chico aprende «la C» o el orden de
la lista y responde sin pensar.
**Cómo se cumple:**
- Quiz final → `QuizEngine.start` ya lo hace (`ordenarSinPatrones`: nada revelado
  por lo anterior, nada parecido seguido, nunca 3 veces seguidas la correcta en la
  misma posición). Medido en los 96 bancos generados: respuestas ya vistas
  0,86 → 0,07 por intento; misma posición 3 veces seguidas 0,54 → 0.
- Actividades, mini-quiz y exámenes propios → al EMPEZAR cada intento, trabajar
  sobre `QuizEngine.prepararBanco(BANCO)` (copia; entiende q/p/enunciado,
  opts/opciones, ans/c/correcta/correcto, exp/pista) y que todo el intento
  (pintar, corregir, revelar la correcta, `respuestas_quiz`, `CajaErrores`) use esa
  copia, nunca el banco original ni la posición del DOM.
- Barajar SOLO al cargar la página no basta: el botón «Otra vez» repite el orden.
- Páginas con quiz PROPIO que solo usan el motor para barajar: cargan
  `<script src="../quiz-engine.js?v=N" data-uso="barajar">` ANTES del script que
  llama a `_prepBanco`. El `data-uso` hace que el piloto de pruebas
  (`piloto-alumno.js › detectarFormato`) las siga tratando como `propio`/`tabs3`.
- Preguntas escritas en el HTML (Sociales 4º B, `_barajarDOM`): se montan objetos
  `{q, opts, ans, _el}` desde el DOM con la clave de respuestas (`QUIZ_CORRECTAS`…),
  se ordenan con `ordenarSinPatrones` y se aplica al DOM el orden de preguntas Y el
  de opciones (el motor puede rebarajar alguna para no repetir posición).
- No barajar opciones cuyo orden importa (escalas, «Ninguna de las anteriores»,
  «Las dos», a) b) c) en el texto): márcalas con `fijo:true`.
- Azar puro: forzar «que quede distinto de antes» sesga la posición de la correcta
  (medido: la 1.ª posición salía la mitad de veces).
**Al escribir preguntas:**
- **El quiz sale de la teoría (regla del usuario, 11-oct-2026): mismo tipo y método, datos nuevos.**
  Cada pregunta del quiz final evalúa un ejemplo o ejercicio RESUELTO de la teoría de su
  módulo: misma habilidad, mismo procedimiento, otros números, palabras o contexto. Dos
  consecuencias: (1) no entra nada que la teoría no haya enseñado (si el quiz pregunta un
  tipo de ejercicio, la teoría tiene un ejemplo de ese tipo); (2) no se copia el enunciado
  ni los datos del ejemplo (se acertaría de memoria: ver «Ejercicios que copian la teoría»).
  Procedimiento: antes de dar por buenas las preguntas, haz la **matriz de cobertura**
  (pregunta → ejemplo de la teoría que entrena). Una pregunta sin ejemplo = añadir el
  ejemplo a la teoría o quitar la pregunta; un ejemplo sin pregunta en un tipo importante =
  añadir la pregunta. Las tres cosas se comprueban a la vez: cobertura, datos distintos y
  figura que no regala la respuesta (R5).
- El quiz final NO copia preguntas de las actividades (misma pregunta con los
  mismos números): con esos datos se acierta de memoria. Misma habilidad, otros
  números o contextos.
- La pregunta no lleva la respuesta dentro (ni en el enunciado ni en una pista
  entre paréntesis), la correcta no se distingue por su forma (más larga, única con
  «/», única en femenino, etiqueta «(correcto)» o un color), y ningún distractor es
  también correcto.
- Al sustituir una pregunta, busca antes (`grep`) que la nueva no exista ya en otra
  actividad del módulo ni revele la respuesta de otra del mismo quiz.

---

## 🆕 ANTI-PATRONES del 25-26 sep — «lo hizo y nadie lo ve» (PR #170 · #171 · auditoría de sesiones, v321 → v328)

Origen: Jorge trabajaba y ni él ni el profe lo veían. Se diagnosticó **con datos**
(cruzando `sesiones` con `lecturas_teoria`, `medallas_alumno` y `estado_alumno` del
mismo alumno y hora: teoría leída a las 11:42 y 0 sesiones desde el 20-sep).

### Síntoma 66 · Progreso que vive solo en el aparato
En las 96 páginas generadas, Ejercicios y Boss guardaban «Hecho» en `localStorage`
**sin alumno**; juegos de memoria, paso a paso, caja de errores, contadores de
medallas y rúbrica, igual. Otro dispositivo (y el profe) no veía nada.
- **Regla del usuario (26-sep):** todo `localStorage` de progreso lleva el alumno en
  la clave (`…::<alumno>::…`) y su patrón en `REGLAS` de `sync-estado.js` (tabla
  `estado_alumno`; fusiona marcas por fecha, números al máximo, listas por id; no
  sube nada antes de haber bajado).
- **Y deja huella en `sesiones`**: quiz, `registrarActividad` o
  `AcademiaLogros.registrarHechos(clave, hechos, total)` (cuenta como actividad sin
  sumar aciertos ni fallos). Sin eso el profe no lo ve.
- Prueba: `node scripts/probar-sync.js` (dos contextos de navegador; con el código
  viejo fallaban 15 de 17).

### Síntoma 67 · `AcademiaLogros.iniciar()` en cada carga abre una sesión nueva
Cada carga de un módulo generado o de `juegos.html` troceaba la actividad en
sesiones sueltas. Compara antes con `getSesion().alumno` y solo inicia si cambia.

### Síntoma 68 · Atribución sin sesión en la pestaña
La puerta de lectura sin sesión inventaba un alumno `anon_…` (Inglés 3º M7 no abría
el quiz); Super Aura se guardaba con `academia '?'` o dentro de la sesión de otra
academia. Sin sesión → **alumno recordado**; herramientas transversales → sesión
propia con `academia_id` null.
- Prueba: `node scripts/probar-sesiones.js` (270 módulos × 6 alumnos × 3 escenarios:
  sesión de portada, pestaña sin sesión, sesión viva de otra academia) y
  `probar-sesiones-limite.js` (16 casos del motor). El profe ve a todos:
  `probar-panel-profe.js` (el detalle pedía 100 sesiones; ahora 1000).

### Síntoma 69 · Tiempo de uso a cero
No se guardaba `duracion_seg`: el informe restaba `actualizado − inicio` y con la
pestaña abierta >2 h daba 0 min. Ahora `academia-logros.js` mide el tiempo **activo**
(pestaña visible + interacción en el último minuto) y guarda `tiempo_seg` y
`duracion_seg` en cada entrada. Una academia nueva lo hereda si registra por
`AcademiaLogros`; un motor propio que guarde a mano debe pasar por él.

### Síntoma 70 · Módulo o medalla sin gamificación (inalcanzable o sin explicar)
Regla del usuario (26-sep): todo lo que se añade, contenido o gamificación, tiene
que poderse ganar y tiene que decir cómo. Casos vistos:
- módulos nuevos sin entrada en `MODULO_A_MEDALLA` → al aprobarlos no pasa nada;
- `l3_crack` definida dos veces y con disparadores viejos → se daba antes de tiempo;
- medallas cuyo `desc` es una etiqueta («Prueba») → la ficha no dice qué hacer.
Al añadir módulos: mapea cada uno a su medalla, pon el crack en el último y
actualiza el retroactivo. Al añadir una medalla: dale camino y, si no es de módulo
ni crack, texto en `COMO_MANUAL`. `validar-academias.js` (s70) y
`validar-medallas.js` lo comprueban y paran el deploy. En el navegador: pulsa la
medalla y comprueba que la ficha «¿Cómo se consigue?» explica el camino.


### Síntoma 71 · Contenido en inglés sin su traducción (regla del usuario, 3-oct-2026)
**Solo** las academias o módulos que LLEVAN contenido en inglés (inglés 1º ESO/3º/3ºB/4º/4ºB/6º…; no todas). En ellas la **teoría, sus
ejemplos y los ENUNCIADOS** de ejercicios, quizs y actividades llevan la traducción al español **pegada** (inglés y traducción juntos o uno
debajo del otro) y con **otro formato** para seguir el hilo visual: inglés en cursiva negrita; español normal, atenuado y con barra lateral
(`bilingue.css`, clase `.bi`; en juegos `.jm-bi`). **NUNCA se traduce lo que resuelve el ejercicio**: ni la frase que hay que completar,
ordenar o corregir, ni las opciones; ni el texto de una lectura sobre la que hay preguntas de comprensión (se traduce título e instrucciones).
Cómo hacerlo:
- **Academia GENERADA** (`ingles1eso`, `ingles4`…): en `material/<curso>/<carpeta>/bloqueN.md`, `*English.* ‖ Español.` (la `‖` U+2016 va tras la
  cursiva inglesa; un ejemplo por viñeta); en `quiz.json`, `"qEs": "…"` = traducción de la INSTRUCCIÓN del enunciado (el motor `quiz-engine.js` la
  pinta debajo en el otro formato). `scripts/generar-1eso.js` enlaza `bilingue.css` cuando la carpeta empieza por `ingles`: si una academia de otra
  materia lleva inglés, amplía esa condición (`cabeceraHtml`).
- **Academia A MANO**: `<link rel="stylesheet" href="../bilingue.css?v=1">` en el `<head>` y `<span class="bi"><span class="en">…</span><span class="es">…</span></span>`
  (variante en línea: `bi bi-linea`). El campo de datos nuevos de inglés lleva siempre su traducción (`ejEs`, `ejemploEs`…), para usarla donde enseña.
- **Paso a paso** (`paso-a-paso.js`): `preguntaEs` (solo la INSTRUCCIÓN), `ayudaEs`, `explicacionEs`, `solucionFinalEs`; el motor admite `<strong> <em> <b> <i>`.
- **Prueba:** `node scripts/auditar-bilingue.js` (cuenta lo que falta, avisos)- **Prueba:** `node scripts/auditar-bilingue.js` (cuenta lo que falta, avisos) y `node scripts/probar-bilingue.js` (navegador a 390 px: formato,
  `qEs` en el quiz, sin scroll horizontal).
- **Error típico:** traducir la frase del hueco o las opciones «para ayudar» — resuelve el ejercicio. La traducción de esa frase solo sale después de responder.

- **Prueba:** `node scripts/auditar-bilingue.js` (cuenta lo que falta, avisos) y `node scripts/probar-bilingue.js` (navegador a 390 px: formato,
  `qEs` en el quiz, sin scroll horizontal).
- **Error típico:** traducir la frase del hueco o las opciones «para ayudar» — resuelve el ejercicio. La traducción de esa frase solo sale después de responder.

### Síntoma 72 · Módulo hecho con los apuntes del profe: cableado a medias o duplicado (3-oct-2026)
Regla del usuario: **un módulo por tema del profe** (GeH m3, Mates 1º ESO m7, Lengua 1º ESO bloques 1/2/4, Irregular Verbs). Lo que falló o estuvo a punto:
- **Módulo nuevo en una academia generada = ocho sitios**, no uno: `catalogo.js` (`modulosKeys` + `apuntes`), `motivacion.js` (la medalla temática del que deja
  de ser el último, `MODULO_A_MEDALLA`, `CRACK_DEF` movido al nuevo último, `{ pref, n }` del retroactivo, `domina`/`practica`/`COMO`), `panel-profe.html`
  (`MODULOS_INFO`), `netlify/functions/cuadernos-mates.js` (si es Mates), `scripts/iconos-mapa.js`, y en `scripts/generar-1eso.js` el bloque en
  `PRACTICA_POR_ACADEMIA` y en el paso a paso. `node scripts/generar-1eso.js --curso 1eso --snippets` imprime las tablas de `motivacion.js`.
  Se añade como `bloqueN.md` nuevo, **sin renumerar** los anteriores.
- **Sin duplicados:** si el tema ya existía (potencias en Mates 1º, léxico en Lengua 4), el módulo nuevo lo absorbe y el antiguo queda como recordatorio con
  enlace; su quiz, práctica y medallas **no se tocan**. Pregunta antes qué se queda cada lado.
- **No partas un módulo largo por tu cuenta:** GeH m3 dura ~50 min según `auditar-tdah.js` y el usuario decidió que se queda entero (10 apartados).
- **Notación y datos del profe, no los tuyos:** fechas (Cobre 5000 · Bronce 3000 · Hierro 2000 a.C.), U/D/C/UM/DM/CM, el truco «lo que sea igual lo dejo».
  No copies los problemas del PDF (se escriben propios). Las figuras con datos del profe no se cambian sin avisar.
- **Etiqueta:** `apuntes` en `catalogo.js` (solo `moduloN.html` o `juegos.html`; validador sAP; `probar-apuntes.js`). En el `.md`, «📒 Apuntes de clase» en los
  `####` con el emoji 💡/📌/⚡ delante (el generador pone el estilo por el emoji). Tablas de teoría: máximo 3 columnas (a 390 px la cuarta se corta).
- **Antes de empezar, fusiona `main`:** otras sesiones suben versión cada pocas horas y dos ramas de apuntes tocaron `catalogo.js` a la vez.
- **Una unidad (o un tema) = un módulo nuevo al final** (Mates 1º m7/m8, Lengua 1º m8, Inglés 1º m8, Refuerzo m7, Lengua 4º m7, Naturales 4º m7-m9): el que deja de ser el último gana su medalla `<pref>tema<N>` y el crack se mueve.
  Lo que ya existía en otro bloque se migra como «🔁 Refuerzo» y el original queda como recordatorio con enlace. Si TODO el tema es de clase (Mates 1º m8) se marca todo, sin «Refuerzo».
- **Juegos de un tema:** página aparte `juegos-<tema>.html` + `<tema>-data.js` sobre `juegos-memoria.js`, prefijo propio (`e1len_prep_`) y medallas `…_juegos_todos/rayo/jefe`; `apuntes` solo admite
  `moduloN.html`, `juegos.html` y `trabajos.html`. Una palabra que cae en dos clases (aunque, siempre, uno) se evita en el juego en vez de arbitrar. Test propio por página (`probar-juegos-<tema>.js`).
- **Datos del material, tal cual:** hechos, cifras y fechas de un cuadernillo o ficha se citan como están y con su fecha (Europa, cuadernillo de enero de 2026); no añadas datos propios sin contrastar. Si la sesión no tiene red,
  los enlaces salen marcados «🔎 sin comprobar» y solo llevan 📄 los que vienen del material (`comprobar-enlaces-trabajos.js` cuando haya red). Un `.docx` vacío se anota, no se inventa.
- **Academia nueva de materia (Atención Educativa 1º ESO):** además de `catalogo.js`, el profe tiene que añadirla en «Materias por curso» y a la lista propia de los alumnos que la cursen, o nadie la ve (cierre del paso «la academia nueva no la ve nadie»).

### Síntoma 73 · Plantilla pensada para chicos con TDAH, pero que castiga o satura (auditoría TDAH, 2-3 oct)
22 academias de 3º y 4º recorridas como alumno (390/820 px) dieron 33 altas. Lo que ya es norma en toda teoría o actividad nueva:
- **Bloques de teoría ≤ ~120 palabras y frases ≤ 15**, y una micro-pregunta «❓ ¿Lo pillas?» por bloque (no bloquea, no puntúa, no resta, no copia el quiz).
  Mídelo con `node scripts/auditar-tdah.js --academias <x> --solo-movil`.
- **Fallar nunca resta** (puntos de clase, Aura < 50 % = 0 + ánimo, medallas). Tras fallar, «Siguiente» espera 1,2 s y se explica el porqué
  (`explicacion` en cada pregunta). El **cronómetro no arranca solo**. Los aciertos de teoría (bloques, «¿Lo pillas?») no dan puntos ni medallas.
- **El cartel de medalla espera** a que acabe el bloque o la pregunta (`motivacion.js` encola; a los 60 s, aviso pequeño). No tapes teoría con modales.
- **Bancos largos:** `QuizEngine.start(clave, banco, { porIntento: 12 })`, o `"porIntento": 12` en `quiz.json` (entero ≥ 4). Opcional: sin ella, igual que antes.
- **Medidas:** opciones de quiz ≥ 48 px (52 en 4º B), letra de teoría ≥ 16 px en 3º/4º, cabecera de 52 px con botones de 44 px, hueco inferior para Medi y 🐛.
- **🔊 Escuchar la teoría** lo pone `leer-voz.js` (inyectado por `app-tools.js`) en cada bloque de 3º/4º: no hace falta nada en el HTML.
- **Quiz final vacío = bug que el piloto tapaba** (`iniciarQuiz()` sin llamar en Lengua 3º): `probar-flujo-alumno.js` ya fuerza el panel y marca «QUIZ VACÍO».
- **Práctica hasta dominar** (`practica-<acad>.js`): en una academia que navega con `data-panel`/`irAPanel()` (Lengua 3º) el paso y la pestaña oculta llaman a
  `irAPanel('practica')`, no a `data-tab`. En tema oscuro el motor necesita `--card2` o cae en `#FFF3E0` con texto claro (contraste 1,04, `practica-dominio.js` v4).
  **En 3º con `.t3-tabs` esa fila está oculta** (`display:none`): el alumno navega con el mapa `.t3-mapa-pasos`, así que la práctica necesita también su paso «💪 Practica»
  en el mapa (Mates 3º la tuvo días en la fila oculta: nadie podía abrirla, las pruebas la abrían por código). **La prueba pulsa el paso visible**, no el botón por código (s70).

### Síntoma 74 · Versiones, fusiones y regeneraciones entre sesiones paralelas (1-3 oct)
- **Misma versión, distinto contenido:** tres veces dos ramas subieron a la vez `peque-engine`, `peque.css` y `rincon-santi-v…`. Al fusionar, **sube por encima de
  las dos** y vuelve a pasar `node scripts/sincronizar-version.js --comprobar`. Si una rama sube de 2 en 2, mira qué números están gastados.
- **`git grep -n "<<<<<<<"` ANTES de commitear una fusión** (se colaron marcas en `sw.js` y `version-watchdog.js`, v405). Nunca `git stash` en medio de un merge
  (aborta la fusión): usa `git worktree add` para comparar con `main`.
- **HTML generado en conflicto:** no se resuelve a mano; mira si `main` cambió contenido (diff sin `?v=`), llévalo al `material/` y regenera;
  `node scripts/generar-1eso.js --comprobar` (y `--curso 4pri --comprobar`, `--curso 1eso`) tiene que quedar limpio.
- **`scripts/generar-1eso.js` contiene caracteres NUL** (marcadores de `inline()`): edítalo con parches anclados en líneas sin NUL; un editor que los pierda rompe el generador.
- **El CSS de `quiz-engine.js` y `paso-a-paso.js` vive en template literals:** ninguna comilla invertida en sus comentarios de CSS.
- **`paso-a-paso.js`** admite `<strong> <em> <b> <i>` y escapa el resto (antes escapaba todo y el alumno veía `<strong>Jack</strong>`). Prueba: `probar-paso-a-paso.js` (94 módulos).
- **Subagentes en paralelo:** ficheros disjuntos, briefing con la regla y sus excepciones, nadie ejecuta el generador ni toca versiones; el coordinador regenera,
  mira el render y pasa las pruebas. Y recuerda los worktrees de `.claude/worktrees/` (nota 52 de CONTEXT_ADN).
- **Puerta familiar (1-oct):** `config.js` pide usuario y contraseña en cualquier página que lo cargue (salvo `localhost`, `127.0.0.1` y `file:`). Una página nueva
  **tiene que cargar `config.js`**; para probar en navegador sirve por `127.0.0.1`. Nunca escribas la contraseña ni el usuario en claro en código ni docs: solo la `HUELLA`.

### Síntoma 75 · Juego para memorizar sin variedad, sin respuesta o sin medalla (3-oct)
Motor `juegos-memoria.js` (5 clásicos + 5 opcionales que solo salen si la página da sus datos: Ruleta, Trío, Detective, Ordénalo, Jefe). Antes de crear o activar uno,
lee `INVESTIGACION-JUEGOS-MEMORIZAR-2026-10-03.md` (8 reglas con su nivel de evidencia y la checklist de diseño) y `GUIA-JUEGOS-E-INGLES-BILINGUE.md`.
- **Variedad (regla «sin patrones»):** el motor rota lo visto en la partida anterior; las trampas se agrupan por TIPO y se eligen con
  `JuegosMemoria.rotador().elegir(grupos, n)`. Una trampa nunca puede ser una forma válida (compruébalo con datos: `probar-ruleta.js`).
- **Al fallar:** respuesta correcta + truco visibles, y lo fallado vuelve (cajas). Fallar no deja el marcador por debajo de 0. Récord personal, sin rankings.
- **Alta:** `<carpeta>/juegos.html` con el `CFG`, campo `juegos` en `catalogo.js` (así el profe puede asignarla como tarea), medallas `<pref>juegos_*` con catálogo +
  `COMO_MANUAL` + `COMO_ACCION` en `motivacion.js`, un solo `registrarMiniQuiz('<pref>juego_<modo>', aciertos, total)` al terminar. Vocabulario con imagen:
  `juegos-vocab.js` (`JuegosVocab.generadores`), con `ejEs` por frase si hay inglés. Receta de ~1 hora en la investigación (§5).
- **Pruebas:** `probar-juegos-nuevos.js` (verbos), `probar-juegos-vocab-nuevos.js <carpeta> <prefijo>` (vocabulario), `probar-ruleta.js`, `probar-juegos-regresion.js`.
- **El Rincón de Santi (`infantil5/`) tiene sus propias reglas** (Santi no lee): **🔊 en TODO lo que Santi tenga que leer** (usuario, 13-oct-2026: «aún no lee con fluidez», para no tener que repetirlo): no solo las tarjetas de respuesta; también las tarjetas de la portada, títulos y textos de sección, avisos, contadores, medallas, insignias, bandas de resultado y cualquier pantalla nueva o de temporada. Se hace con `ponOir(el, texto, 'es-ES', false)` (o `oirTemporada`), el mismo 🔊 de las tarjetas, que lee sin pulsar lo de debajo; los botones de acción ya lo llevan solos. Se aplica sin que nadie lo pida y se prueba: ningún bloque de texto visible sin `.o-oir`. Además: sílabas de colores + 🔊 en toda tarjeta con letras, la voz nunca dice la respuesta
  antes de tocar en los juegos de leer, una trampa no puede sonar igual que la buena (KESO/QUESO), «no rima» tampoco en asonante, avanzar solo con `acierto()`/`cerrarRonda()`,
  lo que Chispa dice sola va por `hablarSinCortar`. Juego nuevo: nota 23 de CONTEXT_ADN (`peque-contenido.js`, `peque-niveles.js`, `santi_<id>` en `catalogo.js` y en `infantil5/progreso.js`).

### Síntoma 77 · Examen de bloque dentro de la academia (4-oct-2026)
Pestaña «📝 Examen» de un bloque (primero: Geo-Historia 1º ESO m3). Contenido en `material/1eso/<carpeta>/examenes.json` (indexado por `moduloN`, opcional: sin entrada el HTML sale idéntico);
motor `examen-bloque.js` (una pantalla por pregunta, ninguna pasa de 1,9 ventanas a 390 px). Test, V/F, relaciona y ordena se corrigen solos; en las **abiertas** el alumno ve la solución y
**marca él los criterios** (decisión del usuario: «nos fiamos»). Reglas que no se negocian: fallar nunca resta, el cronómetro no arranca solo, cada intento baraja (`QuizEngine.prepararBanco`).
Cableado completo: `registrarActividad(academia, '<pref>moduloN_examen', floor(nota×2), 20, {respuestas})` una sola vez por intento (pct en medios puntos: 5,9 no cuenta como 6) para que la
lupa 🔍 del profe vea `respuestas[]`; Aura única por escalón con `aura_aplicar` e id idempotente; medalla en `EXAMEN_A_MEDALLA` (`motivacion.js`) + `COMO_MANUAL`/`COMO_ACCION`
(`validar-medallas.js` lee ese mapa); asignable con `catalogo.js` → `examenes: { '<pref>moduloN_examen': { modulo, titulo } }`; estado local `examen_v1::<alumno>::<clave>` con regla en
`sync-estado.js`. Prueba: `node scripts/probar-examen.js` (puerta cerrada, intento perfecto con doble clic = 10, intento a cero = 0 sin pisar la mejor).

### Síntoma 78 · Entorno de invitado y datos de alumno nuevos (4-oct-2026)
`config.js` define `window.JG_INVITADO`; un invitado (`alumno_norm = 'invitado <código>'`, `es_invitado`, `caduca_en`) solo pasa en `/invitado.html` y en las carpetas de muestra (`matematicas4`, `ingles4`,
`lengua4`). Aislamiento en el navegador, igual que la puerta familiar: Supabase sigue abierto a `anon`. Si añades **una tabla con `alumno_norm`**, ponla en la lista `TABLAS` de DOS sitios
(`invitado.js` y `netlify/functions/invitados-cron.js`) o el invitado caducado deja huérfanos; y todo listado nuevo de alumnos (ranking, estadísticas, informes, correos) tiene que **filtrar el
prefijo de invitado**. Una academia nueva que deba verse de muestra: añádela a `carpetas`. Prueba: `node scripts/probar-invitado.js`; el mock `supabase-simulado.js` ya borra de verdad (`delete().eq()`).

### Síntoma 79 · Lo que se pierde al fusionar y lo que destapa el validador (4-9 oct)
- **`checkout --theirs` de un HTML se come cambios propios:** en la PR #289 se perdieron los nombres de operaciones de `panel-profe.html`. Resuelve bloque a bloque y mira qué cambios NO eran solo `?v=`.
- **Cache-bust tras fusionar:** una rama de CSS/JS compartido sube el `?v=` en ~400 HTML; si `main` trae páginas nuevas, repite `node scripts/cache-bust.js <ficheros> --aplicar`.
- **Llamar a un global que la página no carga** (`Sonidos.medalla()` sin `sonidos.js` en Geometría 2 y Lengua 6º B): el validador sB compara ya solo scripts compartidos de la raíz y exige los de `SOLO_SI_SE_USA` solo si se usan; destapó dos fallos reales.
- **Un módulo cuya carpeta no tiene `prefijo`** (Geometría: `modulo1`…) guarda sus fallos bajo la «academia» `modulo1`: usa `Catalogo.academiaDePath(location.pathname)`. Panel «🗂️ Caja de repaso» en toda portada nueva.
- **Aura que escribe totales** (`aura-meme.js` v3 dejaba 110 de 160 con dos pestañas): solo incrementos por RPC idempotente (`aura_aplicar`, `aura_meme_sumar`). «Repetir» del quiz vuelve a barajar siempre.

### Repaso de lo que se repitió en la auditoría de sesiones
- Diplomas que no se desbloquean al **volver** (escuchar también `pageshow`), textos
  heredados de otra academia («Naturales» en Sociales 3º, «Naturales 4B» en 3º B),
  contadores «21/21» a mano, vitrinas con medallas ganadas bajo candado.
- **Visibilidad otra vez**: Sociales 6º no la veía nadie y Mates 6º solo Jorge. El
  paso «añadir a `visibilidad_curso` y a la lista propia» sigue siendo obligatorio
  al cerrar una academia (ver «Paso que faltaba»).

### Práctica hasta dominar (estilo IXL) — si la academia la lleva
- Motor `practica-dominio.js` + generadores `practica-<acad>.js`; en el generador,
  lo condicional va SIEMPRE dentro de `_practicaCfg` (`PRACTICA_POR_ACADEMIA`) para
  que las demás academias generadas salgan idénticas (`--comprobar` limpio).
- Barra 0-100 con escalones 40/70/90 que **nunca bajan**; cada escalón da Aura una
  vez con clave idempotente en `aura_aplicar`; el 100 da la medalla
  (`PRACTICA_A_MEDALLA` en `motivacion.js`). El dominio sigue al alumno entre
  aparatos (se lee de `sesiones.modulos[clave]`, gana lo más reciente).
- Panel del profe: pestaña «💪 Práctica» (`panel-practica.js`).

### Contenido: ejercicios que copian la teoría
Mismo principio que s65, contra la teoría: `node scripts/buscar-copias-teoria.js`
compara los números de cada ejercicio con los de los ejemplos de su teoría (da
candidatos; se revisan a mano). 16 copias reales corregidas, con las soluciones
recalculadas y comprobadas contra cada `quiz.json`.

### Contenido: el quiz sale de la teoría (11-oct-2026)
Complemento de lo anterior. La regla es doble: **nunca los mismos datos** (`buscar-copias-teoria.js`)
y **siempre el mismo tipo de ejercicio** (matriz de cobertura a mano). Un quiz que pregunta lo
que la teoría no enseñó castiga al alumno por el módulo; uno que copia el ejemplo no mide nada.
En academias generadas, los ejemplos viven en `material/<curso>/<carpeta>/bloqueN.md` y las
preguntas en `quiz.json`: la matriz se rellena con los dos abiertos. En Inglés bilingüe los
ejemplos de la teoría llevan traducción, el quiz no traduce lo que resuelve (síntoma 71).

### Página nueva: lo que ya no es opcional
- `accesibilidad.css` (reducir movimiento, aumentar contraste, hueco de scroll
  solo con ratón): llega por los temas y `mejoras.css`; una página suelta que no
  los cargue necesita su `<link>`. Ratón vs táctil con
  `(hover: hover) and (pointer: fine)`, nunca por ancho.
- PWA: `app-tools.js` pone manifest e icono si la página no los declara; si no lo
  carga, `<link rel="manifest" href="/manifest.json">` y el `apple-touch-icon`. Los
  PNG de `icons/` se cachean 7 días: para cambiar uno, **cambia el nombre**.
- URLs absolutas: `https://academia.jogasan.com`, nunca `*.netlify.app`.
- Supabase en el navegador: la **publishable key** (`config.js`), nunca la
  `service_role`.

### Proceso
- `expectedHeadSha` al fusionar por la API: el SHA **completo** (`git rev-parse`);
  uno reconstruido desde el corto da 409.
- `scripts/lib/supabase-simulado.js`: si añades una tabla con clave compuesta,
  decláralo ahí o el upsert duplica filas en las pruebas.

### Síntoma 76 · Muro de scroll: la teoría no se entrega en pantallas (usuario, 3-oct-2026)
**Causa**: el ejemplo resuelto, el título y las figuras quedaban FUERA de los chunks y se apilaban a la vez (Inglés 3º M8:
4,9 pantallas de móvil), un tema generado cabía en UN chunk de 3 900 px, los módulos de 6º no tenían chunks y la guía de
Repaso de Operaciones se pintaba entera. Pasaba todos los validadores: solo se ve MIDIENDO en el navegador.
**Qué lo evita (nav-chunks.js v11)**: «Pantallas» (intro con el ejemplo; figura con su chunk), «Partes» (más de 1,35
ventanas → «Seguir ↓»; el botón de pasar de chunk, solo en la última parte; no se pierde texto) y `generar-1eso.js`
`repartirPantallas` (temas largos → varios chunks). Una app o guía pintada por JS debe cargar `nav-chunks.js`.
**«Aprende» y «¿Lo pillas?» en pantallas distintas** (usuario, 4-oct): `nav-chunks.js` ya lo hace solo (si el chunk tiene `.mq-q`/`.mq-chunk` y lo que enseña pasa de ~250 px, la micro-pregunta + el botón de pasar de chunk van en la última parte). Al escribir un chunk, deja la micro-pregunta como ÚLTIMO bloque antes del botón; `probar-pantallas.js` (caso 13) comprueba que no sale junto al texto.
**Los chunks NO se acumulan** (3-oct): `avanzarChunk(n)` / `mostrarChunk(n)` / `siguienteChunk(n)` deben ESCONDER el
chunk anterior al abrir el siguiente (`style.display='none'` o quitar la clase `visible`). Sociales 4º B (6 módulos) y
Mates 3º M12 los acumulaban: 2 400-3 500 px de scroll, y ninguna auditoría lo veía porque cada chunk, aislado, es corto.
`validar-academias.js` (**s76**, error: para el deploy) lee esas funciones; `auditar-pantallas.js` cuenta cuántos chunks
hay a la vez a la vista y falla si > 1. Al clonar un módulo, copia la `avanzarChunk` de una academia que esconda, no la de
la hermana que acumula. Plantilla correcta: `function avanzarChunk(n){var c=document.getElementById('chunk-'+n),p=document.getElementById('chunk-'+(n-1));if(c){if(p)p.style.display='none';c.style.display='block';c.scrollIntoView({behavior:'smooth',block:'start'});}}`.
**Prueba obligatoria antes de dar un módulo por bueno**: `node scripts/auditar-pantallas.js <ruta|academia|--cambiados>`
(ninguna pantalla > 1,9 ventanas a 390×844; excepciones con motivo en `scripts/pantallas-permitidas.json`) y, si se toca
el motor, `node scripts/probar-pantallas.js`. Contenido nuevo: bloques ≤ ~120 palabras, una figura por chunk.

### Síntoma 80 · Teoría sin figura SVG: «siempre que se construya algo, con SVG» (usuario, 12-oct-2026)
**Causa**: en Naturales 4º M7-M9 (Unit 1, bilingüe) solo 5 de 18 bloques de teoría llevaban figura; el resto era texto. Un auditado global dio **308 de 672 bloques sin figura** en todo el portal (Atención Educativa 1º ESO 84, Lengua 1º ESO 47, Inglés 1º ESO 39…). El niño con TDAH mira la imagen antes que el texto: un bloque sin figura es un bloque peor.
**Regla (no negociable, la pone el usuario)**: TODO lo que se construye lleva SVG que ayude al estudio, sin que nadie lo pida:
1. **Módulo nuevo o rehecho**: una figura por cada bloque de teoría (`### …` de `bloqueN.md`; se exceptúan los «🧩 Ejemplo resuelto» y las hojas de ejercicios), enlazada con `![alt](fig:<id>)` justo antes de «Tips y Trucos» y con el fichero en `material/figuras/<id>.svg`.
2. **Juegos, flipbook, apps y páginas hechas a mano**: la ayuda visual va dentro (SVG incrustado), no solo emojis sueltos.
3. **Chuletas** (`## 📋 CHULETA`): deben incluir también apoyos visuales que mejoren la comprensión — tablas de resumen (con columnas de estado, ejemplos, datos clave), diagramas de orden (capas, procesos), matrices "si ves X → respuesta Y", SVGs explicativos y/o gráficos. Una chuleta solo con texto plano no está terminada. Los apoyos van dentro de la misma sección `## 📋 CHULETA` (sin `###` subsecciones que el validador interpreta como bloques de teoría nuevos: usar **negrita** como cabecera de subsección).
4. **Calidad**: rúbrica R1-R6 de `auditoria-pedagogica-jogasan` (pertinente al bloque, rigor, aporta más que el texto, **no muestra la respuesta que luego pregunta el quiz**, esquemática); `<title>` y `<desc>` primeros (antes de `<defs>`), `viewBox` de 320 de ancho (en las estrechas de 3º, su ancho real) y texto ≥ 12 px REALES (13 en viewBox 320; ver el síntoma 82); en bilingües, rótulos en inglés con el español debajo y nunca la frase que resuelve un ejercicio. Dibujar con script (`python`) mide por coordenadas y evita ángulos falsos; ver la figura a 390 px antes de darla por buena.
**Comprobación automática**: `validar-academias.js` check **FG** da error si un módulo tiene más bloques sin figura que los permitidos en `scripts/figuras-permitidas.json` (la deuda anterior a la regla, congelada: **trinquete que solo baja**). Tras pintar figuras: `node scripts/figuras-trinquete.js --bajar`. **Academias hechas a mano** (sin `material/`): el mismo check FG cuenta los chunks de teoría de `carpeta/moduloN.html` (`id="chunk-N"`, sin las pantallas de «COMPLETADO/DOMINADO») que no llevan `<svg>`/`<img>` antes del siguiente chunk (`scripts/lib/figuras-html.js`); deuda congelada en `scripts/figuras-permitidas-html.json`. Un módulo nuevo a mano sin figuras para el deploy. **Calidad (check FQ, `scripts/lib/figuras-calidad.js`)**: cada figura (a mano y `material/figuras/*.svg`) lleva `<title>` y `<desc>` como primeros hijos del `<svg>` (antes de `<defs>`/`<rect>`), ids únicos en la página (`generar-1eso.js` renombra la 2.ª aparición de una misma figura: `-d2`…) y y `font-size × ancho mostrado / ancho del viewBox ≥ 12` (ancho mostrado = `max-width` o `width` de la figura, tope 350; la medida real es `auditar-svg.js --navegador [--solo=…]`); deuda anterior congelada por fichero en `scripts/figuras-calidad-permitidas.json` (solo baja con `figuras-trinquete.js --bajar`). **R5 automático**: `node scripts/auditar-figuras-quiz.js` cruza el texto de cada figura con `quiz.json` y avisa de los problemas con datos cuyo enunciado y cifras aparecen en la figura (no para el deploy: revisa cada aviso, cambia el ejemplo de la FIGURA). `node scripts/figuras-trinquete.js` lista la deuda por academia. **Nunca subas un número del JSON para que pase.** Las academias hechas a mano en HTML no pasan por este check: se revisan con `auditar-svg.js` y la rúbrica.
**Prueba**: `node scripts/auditar-svg.js [--navegador]` y captura a 390 px de cada figura nueva junto al quiz de su módulo (grep de cada palabra de la figura en `quiz.json`).

### Síntoma 81 · La pregunta enseña la respuesta y la figura no explica nada (usuario, 17-oct-2026)
**Causa**: las auditorías miraban que el quiz no copiase la teoría (s65) ni que la figura dibujase el problema (R5), pero no que
la PROPIA pregunta delatase su respuesta ni que la figura sirviera a su bloque. Casos reales que destapó el primer pase (137 avisos en
17 academias generadas): «Las luces de tráfico **(un código no verbal)** son… el» → «Código» (Lengua 1º ESO m1); decenas de preguntas
cuya correcta es la única larga y matizada frente a tres distractores cortos; figuras con `<title>`/`<desc>` vacíos o sin rótulos.
Y en el alta del bloque 8 de Refuerzo 1º ESO: un `![alt](fig:…)` con corchetes en el alt (`[90 : (4 + 5)]`) **dejó la figura sin
pintar** sin que nada fallara, y tres «¿Lo pillas?» cuya explicación empezaba por una fórmula salieron «sin explicación» (sMQ).
**Regla**: toda pregunta (quiz, micro-pregunta, actividad, examen) se responde pensando, no leyendo; toda figura explica su bloque.
**Prueba**: `node scripts/auditar-pistas.js <acad>[:<bloque>]` (academias generadas; `--estricto`; tabla de la FASE 3.5). Dos sesiones
hicieron a la vez la misma batería (síntoma 50); quedó UN script, con los códigos A1-A4 (preguntas) y B1-B4 (figuras):
- **A1** la respuesta escrita en el enunciado (y ningún distractor) · **A2** la correcta se delata por su forma (mucho más larga, única
  con paréntesis, «/» o «porque») · **A3** opciones idénticas o `ans` fuera de rango · **A4** un paréntesis del enunciado da la respuesta.
- **B1** `<title>`/`<desc>` ausentes o desc corta · **B2** no comparte palabras clave con su bloque · **B3** sin rótulos · **B4** alt con corchetes.
- Cada aviso se revisa a mano. Si es real, se reescribe la PREGUNTA (distractores de longitud y forma parecidas, la pista fuera)
  o la FIGURA; nunca se toca el script para que calle. Una micro-pregunta cuya explicación empieza por fórmula: empieza por una palabra
  («Porque…», «Se descompone:…»).
- Academias hechas a mano (quiz en el JS del `moduloN.html`): misma revisión a mano con grep de la correcta en su enunciado.
- **Reglas afinadas con los falsos positivos reales (17-oct):** A3 compara las opciones **letra a letra** (mayúsculas y tildes cuentan: en una
  pregunta de ortografía «sevilla» y «Sevilla» son opciones distintas; «canción» dos veces sí es un duplicado), y un paréntesis **pegado a un
  hueco** («We _____ (ride)») es el verbo que se da para transformar, no una pista: no entra en A1 ni en A4. Un paréntesis-pista de verdad
  («(un código no verbal)», «(pista: swim)») sigue saltando.
- **Avisos justificados** (revisados y la forma NO delata, y ninguna regla general los cubre): se anotan con su motivo en
  `scripts/pistas-permitidas.json` (clave = la línea del aviso sin el ⚠). Hoy está vacía. Si la pregunta cambia, vuelve a salir; una
  entrada que ya no casa sale como «sobra» y se borra (la lista solo baja). Nunca para esconder uno real. Si el mismo falso positivo
  se repite en varias preguntas, se afina la regla del script en vez de justificar cada una.

**Cómo se reescriben los distractores (pase completo del 17-oct, hecho a la vez por dos sesiones —PR #429 y la de la lista de justificados—: más de 200 avisos en 17 academias, casi todos reales):**
1. **Mismo `ans`, misma idea**: no se cambia qué evalúa la pregunta; se cambian los distractores (o se recorta la correcta si no pierde rigor).
2. **Misma forma que la correcta**: si es una frase con «porque», paréntesis, «/», fecha o fórmula, al menos otro distractor también;
   si es una ruta «A → B → C → D», los distractores son rutas de 4 pasos. Longitud parecida, sin que la correcta quede ahora la MÁS
   corta (también es un patrón: lo vimos en «La pregunta» frente a tres opciones de 20 letras).
3. **Errores típicos, nunca absurdos**: conceptos vecinos de la MISMA teoría que el alumno confunde (otro programa europeo, otro bioma,
   la regla de acentuación de al lado, la operación inversa, el orden al revés). «En un videojuego», «gritar», «Una canción pop»,
   «Un círculo» se descartan solos y convierten la pregunta en 50 %.
4. **Claramente falsos según la teoría**: quita los discutibles (Alejandro también venció a los persas; algunas bacterias sí hacen la
   fotosíntesis; un distractor «positivo» entre tres «malvados» se elige por el tono).
5. **Sin patrones (s65)**: un distractor no repite la respuesta de una pregunta vecina del mismo módulo.
6. **Si `exp` o `pasos` nombran un distractor, se ajustan.** Inglés (s71): las opciones no se traducen; un enunciado que pasa a inglés
   lleva su `qEs` como sus hermanos.
7. **El resultado no puede coincidir con un dato del enunciado** (A1 destapó «250 − 235 = 15 €» con «camisetas de 15 €» y
   «1 − 0,7 = 0,3» con «0,3; 0,25…»): cambia los datos, rehaz `exp` y `pasos`, y pasa `buscar-copias-teoria.js` (los datos nuevos
   tampoco pueden ser los de la teoría).
8. **Micro-preguntas de 2 opciones**: con dos, cualquier diferencia de forma delata; al arreglar una, pásala a 3 opciones parecidas.
9. **B2**: si la figura sí ilustra su bloque, basta con un `<desc>` que nombre lo que se explica; si está en el bloque equivocado,
   muévela y el bloque que se queda sin figura lleva la suya (FG).

### Síntoma 82 · El texto de la figura se lee a menos de 12 px reales (usuario, 18-oct-2026)
**Causa**: una figura se dibuja con `viewBox` 320 y letra de 12-14, pero en la página no se ve a 320 px: en móvil es ≈ **298 px (×0,93)**
y dentro de las tarjetas de 3º es de **235-251 px (×0,73-0,78)**. «≥ 12 en el viewBox» no es «≥ 12 px en pantalla»: un 12 sale a 11,2 px y un 14 a 11 px.
`auditar-svg.js --navegador` midió **305 figuras bajo 12 px** en 180 páginas (63 chuletas de 6,5-9 px) tras un FQ estático que se creía limpio.
El check FQ solo **estima** (`font-size × ancho mostrado / ancho del viewBox ≥ 12`, ancho = `max-width`, `width` o 350 con `width="100%"`): **la verdad es el navegador**.
**Regla**: texto ≥ 12 px REALES (en viewBox 320, **13 o más**); en las academias hechas a mano que se ven estrechas, `viewBox` = su ancho real (235-313)
con `max-width:320px` (1 unidad = 1 px). **Chuleta/resumen = póster de 320 de ancho y alto libre** (480-1.090 px), tarjetas por sección, 13+ px y menos palabras
(la tabla completa va debajo en el md); no una lámina de 320×220 con letra de 7 px. «🔍 Ver en grande» (`figura-zoom.js`) es una red, no una excusa.
**Cómo se arregla** (de menos a más trabajo): 1) subir SOLO los `font-size` pequeños hasta el umbral de su ancho real y **medir antes y después** (textos que se pisan, textos
fuera de la figura, textos que ya no caben en su caja `rect`/`circle`); si empeora, no se toca; 2) rehacer la composición (columnas de 100 px → tarjetas apiladas, ejemplos
cortos); 3) generadas: se edita `material/figuras/<id>.svg` y se regenera; hechas a mano: se sustituye el bloque `<svg>` EXACTO del HTML (comprobando que aparece una vez, que los
`<script>` no cambian y que el recuento de `<div>`/`<svg>` es igual). Orden de hijos: `<title>` y `<desc>` los PRIMEROS (antes de `<defs>`; 1.233 figuras con el degradado `gbg…`
delante) y ids únicos en la página (`generar-1eso.js` renombra la 2.ª aparición de una misma figura: `-d2`).
**Pruebas**: `node scripts/auditar-svg.js --navegador [--solo=ruta1,ruta2]` (la verdad), `node scripts/medir-figura.js <fichero.svg> [--ancho=298] [--png=carpeta]` (texto real,
pisados, fuera, desbordados, alto; ✓ = ≥ 12 px y 0/0/0 — y **mira el PNG**), `figuras-trinquete.js` (3 JSON: `figuras-permitidas.json`, `-html.json`, `figuras-calidad-permitidas.json`; hoy todos `{}`:
nunca subas un número), `auditar-pantallas.js` (un chunk con una figura más alta no pasa de 1,9 ventanas).

### Síntoma 83 · Datos dudosos que ya traía el contenido: rigor factual al rehacer (18-oct-2026)
**Causa**: al rehacer 200 figuras salieron errores heredados que ningún validador ve (el dato es coherente consigo mismo): «× 10: mm → cm» (de mm a cm se divide), Maastricht 1992/1993,
«5 continentes: América N y S, Europa, África y Asia», «Guadalquivir, el más largo», «220M sin vacunas», «colores RONAAV», «luz y sonido crean sombras», «escritura» en la Edad de los Metales,
calculadora 1642 antes que telescopio, «Watt inventó el vapor», «biotopo/biocenosis» sin que el texto los enseñe en 3º.
**Regla**: al tocar una figura o un enunciado, contrasta CADA dato con el texto del módulo y con una fuente; si dudas, no lo propagues (anótalo) y decide: **corregir**, **dejar con matiz** o **no preguntar**.
Para varias dudas a la vez, investigación con fuentes (skill `deep-research`; informe en español con tabla duda · dónde · veredicto · certeza · acción). **Límite real**: en el entorno de Claude el proxy
bloqueó BOE, RAE, IGN, MITECO y BCE; todo salió de buscadores → lo que importe se contrasta en la fuente oficial antes de grabarlo y el informe lo dice.
**Tabla de datos que suelen salir mal (redacción segura para 8-12 años)**
| Tema | Mal | Seguro |
|---|---|---|
| Prehistoria | «la escritura es de la Edad de los Metales» | la escritura (≈ 3000 a. C., Mesopotamia y Egipto) marca el FINAL de la Prehistoria |
| Inventos | calculadora antes que telescopio; «Watt inventó el vapor» | telescopio 1608 (Lippershey; Galileo 1609) < calculadora de Pascal 1642 («una de las primeras»); imprenta ≈ 1450; vapor: Newcomen ≈ 1712, Watt lo mejora (1769); Revolución Industrial: empezó en Gran Bretaña ≈ 1760-1780 con máquinas de hilar y tejer y la máquina de vapor la **impulsó** (no «la inició») |
| Restauración | mezclar 1874 y 1875 | 1874-1923 **o** 1875-1923, una sola en todo el módulo |
| UE | «fundada en 1957»; 19 países euro | origen en el Tratado de Roma (1957); la UE nace con Maastricht (firmado 7-2-1992, en vigor 1-11-1993); 27 miembros; **21 países con euro desde 1-1-2026** (Bulgaria); Consejo Europeo ≠ Consejo de la UE ≠ Consejo de Europa; Parlamento: Estrasburgo, Bruselas, Luxemburgo |
| Ríos | «el más largo de España» | Tajo = el más largo de la Península (≈ 1.000 km); Ebro = el más largo que va entero por España y el más caudaloso; Guadalquivir = el más largo de Andalucía |
| Continentes | «5: América N y S, Europa, África y Asia» | 5, 6 o 7 según el criterio (el escolar suele dar 6 con América única); no preguntar «¿cuántos hay?» sin dar el criterio |
| Agua | «solo el 3 %», «el 1 % se puede beber» | «algo menos del 3 %» es dulce y casi toda está helada o bajo tierra |
| Luz y color | «el sonido crea sombras»; mnemotecnias inventadas | solo la luz forma sombras; 7 colores del arcoíris = convención de Newton (el añil se discute) |
| Ecosistemas 3º | «biotopo / biocenosis» | entorno / seres vivos (los términos técnicos no son de 3º); «fósiles» → combustibles fósiles (petróleo, gas, carbón) |
| Esferas de la Tierra | «la sequía es de la hidrosfera» / «las nubes son de…» | la sequía empieza en la atmósfera (no llueve) y se nota en las cuatro esferas; una nube es agua en la atmósfera; **no preguntar «¿a qué esfera?» con una sola respuesta** (o «según el libro») |
| Lengua | «pe-rri-to: rr entre r-r»; «el libro» CD y «rojo» CN al mismo nivel | la «rr» no se separa; CD = «el libro rojo» entero (con «rojo» dentro); evitar «tl» y guion/truhan/fie en separar sílabas |
| Inglés | «irregular nunca lleva -ed» absoluto | evitar variantes UK/US en quizzes (shine, hang, light, learn, burn, dream, get/gotten); bear-bore-borne (born solo para nacer) |

### Síntoma 84 · `main` no publica: Netlify despliega solo desde `produccion` (usuario, 17-oct-2026)
**Causa**: cada build de Netlify gasta créditos. **Regla**: fusionar a `main` es gratis y se hace con normalidad; **nunca** empujes a `produccion` sin la orden expresa «publica» / «sube a Netlify».
Antes de publicar, avisa de `git log --oneline origin/produccion..origin/main`; publicar = `produccion` pasa a `main` por fast-forward (un solo build). Comprueba antes si ya lo hizo otra sesión
(`git rev-parse origin/main origin/produccion`: si coinciden, no hay nada que publicar). Las pruebas se hacen en local (`127.0.0.1`, puerta familiar) y no ven el resultado del build.
En un preview de Netlify el inicio de sesión es con usuario y contraseña, no con Google (Supabase solo admite las URL de su lista).

### Síntoma 85 · Teoría: una regla por tema, el patrón en color, y explicación exhaustiva la primera vez (usuario, 18-oct-2026)
**Causa**: el alumno falla los **micro-pasos** que un adulto da por obvios («la letra antes de la y de *study* es una d, consonante»). **Regla**: teoría que obliga a decidir entre reglas, identificar algo en el dato o
hacer varias operaciones lleva, además del esquema, un **ejemplo resuelto paso a paso** (sin saltarse ningún micro-paso) con su figura, y **todas las correcciones de ejercicios (`✅`) van «Paso a paso»**.
Una regla por tema, tablas, y **el patrón que el alumno busca va en color** (`{v:a}` `{c:d}` `{y:y}` `{aux:are}` `{add:ing}`, estilos `.hl` en `tema-1eso.css`; en las de fondo oscuro, `marcas-color-oscuro.css`, piloto Naturales 6º),
sin mucho texto del mismo formato. Guía y modelo: `GUIA-EXPLICACION-EXHAUSTIVA.md` (Inglés 1º ESO, bloque 8) y `AUDITORIA-FOCO-TEORIA-2026-10-18.md`; se mide con `node scripts/auditar-foco-teoria.js`
(las hechas a mano —3º, 3º B, 4º B, 6º— se revisan aparte).

### Síntoma 86 · Los juegos de memorizar salen del módulo, no de la cabeza (19-oct-2026)
**Causa**: datos de la hermana A/B reutilizados daban 60 errores (Sociales 4º vs 4º B: el texto es distinto), y juegos que no explicaban el fallo.
**Orden del alta**: datos en `<academia>/conceptos-data.js` (inglés: `vocabulario-data.js`) → `node scripts/comprobar-conceptos-fuente.js <academia>` (o `comprobar-vocab-fuente.js`) a **0 errores** → página `juegos.html`
(plantilla de `ingles3b`/`matematicas3` y `juegos-conceptos.js`) → `catalogo.js` (`juegos: 'juegos.html'`; no repetir el paso: duplica `juegos:`) → 4 medallas en `motivacion.js` (catálogo, `COMO_MANUAL`, `COMO_ACCION`; el nombre no
puede repetirse) → tarjeta en el índice (las generadas la pintan solas) → `probar-juegos-conceptos.js` → `cache-bust.js motivacion.js catalogo.js --aplicar` y subir `CACHE_VERSION`.
Lo que se enseña como par (término ↔ significado) va en `d`; lo que podría ser también respuesta de otro concepto se declara con `noJuntos`; un emoji repetido (`🏞` y `🏞️`) confunde «imagen → término».
**Juegos DENTRO de un módulo generado**: entrada en `JUEGOS_EN_MODULO` de `scripts/generar-1eso.js` y se regenera; los ids de medalla van **literales** en el JS (`validar-medallas.js` los busca como texto).
**Todo juego o reto explica por qué cuando se falla** (campo `truco` en cada pregunta/tarjeta/ítem; el test de datos falla si una va sin explicación): qué regla manda, qué letra/palabra decide, la frase correcta con su traducción.

### Síntoma 87 · Entregas, recursos del profe y ayudas para cada trabajo (usuario, 17-oct-2026)
- Una **entrega** del colegio = una entrada en `entregas` de su academia en `catalogo.js` (`limite` con zona horaria `+01:00` invierno / `+02:00` verano, `guia` relativa, `plan` igual al de su guía; `probar-entregas.js`). Si es de un solo alumno, que la apunte el profe (tabla `trabajos`).
- Un **recurso externo** = una entrada en `diccionarios` (`{ nombre, inicio, buscar?, desc?, marco? }`): comprueba antes si el sitio se deja enmarcar (`X-Frame-Options`/`frame-ancestors`); si no, `marco: false`.
- **Ayudas en todo trabajo** (sin que nadie lo pida): plan por etapas con fechas, ficha o plantilla rellenable (se copia; si guarda progreso, con alumno en la clave y regla en `sync-estado.js`), esquema de lo que se entrega, modelos, dónde buscar, errores típicos,
  checklist y, si se expone, cronómetro de ensayo (manual). Referencia: `material/1eso/geografia1eso/trabajos.json` + `scripts/generar-trabajos-geh1eso.js`.

### Síntoma 88 · Toda chuleta se puede imprimir en A4 (usuario, 18-oct-2026)
`chuleta-imprimir.js` pone «🖨️ Imprimir A4», «⬇️ Descargar PDF» (html2pdf.js 0.10.1 desde cdnjs, solo al pulsar) y «👁️ Vista A4 clara»; al imprimir deja solo la chuleta en fondo blanco, con los fondos oscuros pasados a tinte claro y
contraste ≥ 7 (HTML y SVG). Los módulos con `#panel-chuleta` lo cargan solos desde `app-tools.js`; una página suelta (`chuleta*.html`/`superchuleta*.html`) añade `<script src="../chuleta-imprimir.js?v=3" defer></script>`.
Se prueba imprimiendo a PDF con Playwright y mirando las páginas. Y la chuleta es un **póster legible** (s82).

### Síntoma 89 · Varias sesiones o agentes a la vez: coordinación y trampas (16-19-oct-2026)
- **Agentes en paralelo** (rehacer 200 figuras con 9 agentes): un **brief común** con la regla y el comando de medida, **ficheros disjuntos por agente** (cada uno solo toca los suyos; nada de git, nada de `generar-1eso.js`, nada de servidores),
  informe final con tabla (alto, ✓/✗, qué se quitó, datos dudosos). El coordinador regenera, mide TODO de nuevo, valida y commitea. **Verifica lo que dicen los agentes** (un agente midió a 320 px y la página real daba 298).
- **Hook «hay cambios sin commitear»** con agentes aún trabajando: commit **WIP solo de lo válido** (SVG que parsea, HTML con los mismos `<script>` y recuento de `<div>`/`<svg>`), push a la rama de trabajo, nunca a `main`.
- **Fusiones (s74)**: al fusionar `main` en tu rama, `sw.js`/`version.json`/`version-watchdog.js` se resuelven con la de `main` + 1 y `sincronizar-version.js`; las cifras `?v=` bajan con `--theirs`: sube `nav-academias.js`, `catalogo.js` y lo que toques por encima del
  máximo servido (`cache-bust.js <recurso> --aplicar`). Tras un PR fusionado, reinicia la rama desde `main` (`git checkout -B <rama> origin/main`).
- **Servidores de prueba**: `python3 -m http.server 8765/8899` muere entre llamadas (`setsid nohup … &`, comprueba con `curl -sI`); **nunca `pkill -f` con un patrón que esté en tu propio comando** (se mata a sí mismo); lanza lo largo en segundo plano y lee el log con `grep -a`.
- **Un delta en `CONTEXT_ADN` tras cada PR** (título con PR, SW, pruebas); comprueba el hueco con `git log origin/main --merges` contra `grep "#NNN"`.
- **Medi es la clase `.medi-flotante`**, no un id: al medir flotantes busca id **y** clase y mide a 1, 3, 6 y 9 s. **Nunca `background` inline** en un botón de un modal con tema propio (usa una clase y mide el contraste en el modal real).
- Skills hermanas: lapbook de cartulina → `lapbook-fisico`; temas de temporada (Halloween, Navidad) → `temporadas-tematicas`; **El Rincón de Santi: 🔊 en todo lo que Santi tenga que leer** (`ponOir`/`oirTemporada`).

### 🧪 Orden completo de pruebas (técnicas + contenido) antes de cada push que toque contenido
| # | Comando | Qué garantiza | Para el deploy |
|---|---|---|---|
| 1 | `node scripts/generar-1eso.js --curso <c> <carpeta>` | lo generado sale del material (s56) | `--comprobar` sí |
| 2 | `node scripts/validar-academias.js` (comparado con `main`) | fontanería, FG/FQ de figuras, sMQ, sAP, s70… | sí |
| 3 | `node scripts/auditar-pistas.js <acad>:<n>` | la pregunta no lleva la respuesta; la figura explica su bloque (s81) | no: 0 avisos a mano |
| 4 | `node scripts/auditar-figuras-quiz.js` | la figura no dibuja el problema del quiz (R5) | no |
| 5 | `node scripts/buscar-copias-teoria.js` + matriz pregunta → ejemplo | el quiz sale de la teoría con datos nuevos (s65) | no |
| 6 | `node scripts/auditar-pantallas.js <ruta>` · `auditar-tdah.js --academias <acad> --solo-movil` | sin muros de scroll, bloques cortos (s76, s73) | no |
| 7 | `node scripts/auditar-svg.js --navegador [--solo=…]` · `node scripts/medir-figura.js <svg> [--png=…]` + **mirar cada figura a 390 px** | texto ≥ 12 px REALES, sin pisados ni desbordados; que se entienda sola (s82) | FQ sí |
| 8 | `node scripts/validar-medallas.js` · `probar-apuntes.js` · `auditar-bilingue.js` (si hay inglés) | gamificación alcanzable, etiqueta, bilingüe | s70 sí |
| 8b | `node scripts/probar-manual.js <carpeta> [moduloN]` (hechas a mano) · `probar-juegos-conceptos.js` · `comprobar-conceptos-fuente.js <acad>` | cada página carga y el quiz se contesta ENTERO («N de N correctas»); juegos con datos del módulo (s86) | no |
| 8c | `node scripts/auditar-foco-teoria.js` | una regla por tema, patrón en color (s85) | no |
| 9 | `node scripts/probar-flujo-alumno.js <ruta>` (y `JG_VIEWPORT=390x844`) + Playwright propio con capturas | el alumno lo hace y queda registrado; 0 errores JS | — |

