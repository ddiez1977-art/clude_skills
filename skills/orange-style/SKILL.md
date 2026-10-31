---
name: orange-style
description: "Aplica la identidad visual y las reglas de comunicación responsable del Grupo Orange (Orange, Orange España, Orange Empresas, MasOrange) a presentaciones .pptx, apps web, dashboards, HTML/React, documentos, firmas de correo, cabeceras LinkedIn/X, fondos de videollamada y cualquier entregable visual o de copy. Úsala SIEMPRE ante: \"estilo Orange\", \"branding Orange\", \"/style\", \"estilo MasOrange\", \"presentación corporativa\", \"plantilla Orange España\", \"logo Orange\", \"firma de correo\", paleta naranja-negro-blanco, o material comercial en nombre de Orange/MasOrange (propuestas, argumentarios, decks, landings, emails). También al colocar el logo, redactar claims comerciales o medioambientales, o publicar contenido generado con IA con marca Orange. Sustituye a masorange-style (obsoleta).\n"
---

# Orange Style — Sistema visual + Comunicación responsable

Dos capas, siempre juntas:
1. **Capa visual** (secciones 1–7): cómo se ve.
2. **Capa de mensaje** (sección 8 + `references/comunicacion-responsable.md`): qué se puede decir y cómo, según la *Orange group responsible communication guideline*.

Fuentes (de más a menos autoridad):
1. **Guidelines de aplicación del logo Orange** (Brands&Comms, sept. 2026) → reglas del logo, retícula, posicionamiento. **Normativo.**
2. **Plantilla corporativa PowerPoint "Orange España"** (147 diapositivas, 16:9) → paleta de tema Office, tipografía Arial, tamaños, layouts. **Normativo para Office.**
3. **Activos de comunicación Orange España**: cabeceras LinkedIn/X, firma de correo Outlook, fondos "At home / At work" → patrones de aplicación reales.
4. **Guía de comunicación responsable del Grupo** (PDF A4, EN) → mensaje, accesibilidad, IA. Los patrones de maquetación de la sección 4 *derivan de cómo está compuesta esa guía*, no de un brand book completo.

Si hay conflicto entre fuentes, prevalece el número más bajo. Si el usuario aporta el brand book oficial, este prevalece sobre todo. Lo marcado **[derivado]** es inferencia de los materiales, no norma escrita.

Detalle de logo, retícula, plantilla y formatos concretos en `references/logo-y-formatos.md` (léelo al colocar el logo o al entregar pptx/firma/cabeceras/fondos).

---

## 1. Paleta

La marca es **naranja + negro + blanco**. Nada más como color de marca.

| Token | Hex | Uso |
|---|---|---|
| `--or-orange` | `#FF7900` | Naranja Orange. Logo, barras verticales, numerales grandes, titulares sobre negro, acentos, CTAs |
| `--or-orange-text` | `#F16E00` | Variante para texto naranja grande sobre blanco (ver accesibilidad) |
| `--or-black` | `#000000` | Negro puro. Texto principal, fondos de portada/cierre, cajas de etiqueta sobre foto |
| `--or-white` | `#FFFFFF` | Fondo base de páginas de contenido, texto sobre negro |

Grises solo como soporte funcional de UI (bordes, estados deshabilitados, texto secundario), nunca como color de marca:
`--or-gray-100: #F6F6F6` · `--or-gray-300: #DDDDDD` · `--or-gray-500: #999999` · `--or-gray-700: #595959` (texto secundario sobre blanco, contraste AA).

**Eliminado respecto a masorange-style:** amarillo `#FFD600`, naranja `#FF5900`, negro `#1A1A1A`, sombras en cards, esquinas redondeadas.

### Paleta ampliada oficial (tema Office de la plantilla Orange España)
Son los 6 acentos + texto/fondo del tema `.potx`. Úsalos **solo en gráficas, tablas y apoyo funcional**, nunca como color de marca de una pieza:

| Slot | Hex | Uso permitido |
|---|---|---|
| Accent 1 | `#FF7900` | Serie protagonista, énfasis |
| Accent 2 | `#000000` | Segunda serie, texto |
| Accent 3 | `#FFC999` | Tinte naranja claro (series secundarias, fondos de resaltado suave) |
| Accent 4 | `#86868E` | Gris medio (series, líneas, ejes). Contraste sobre blanco ≈ 3,6:1 → **no para texto de cuerpo** (usa `#595959`) |
| Accent 5 | `#FFE000` | Amarillo: **solo** 5.ª serie de una gráfica. No es color de marca |
| Accent 6 | `#DEDDE0` | Gris claro (fondos de panel, separadores) |

Orden de uso en gráficas: `#FF7900` → `#000000` → `#FFC999` → `#86868E` → `#FFE000` → `#DEDDE0`.
Hipervínculos: el tema trae azul/morado por defecto; en piezas nuevas prefiere negro subrayado (naranja no pasa contraste sobre blanco).

### Colores secundarios de ilustración [medidos en los activos]
Aparecen *dentro* de ilustraciones del banco de imágenes (cartel de brote verde/rosa, auriculares azules, playa): azul `#4BB4E6`, verde `#50BE87`, rosa `#FFB4E6`, morado intenso `#482291`, amarillo de playa. **No son tokens de UI.** No los uses para fondos, botones ni texto. Si necesitas la paleta completa de ilustración, pídela al equipo Brands&Comms o usa el banco de ilustraciones.
Nota: el naranja impreso en pósters de fotos-mockup se ve `#E87113`–`#EF7A1A` por la iluminación; el valor de marca sigue siendo `#FF7900` (Pantone® 151 en impresión).

### Accesibilidad del naranja (obligatorio, la guía exige "sufficient color contrast", §3.1)
Contraste medido de `#FF7900`:
- Naranja sobre **negro**: ≈ 8:1 ✅ Apto para cualquier tamaño. Por eso los titulares naranjas lucen sobre fondo negro.
- Naranja sobre **blanco**: ≈ 2,6:1 ❌ No pasa WCAG ni en texto grande. Sobre blanco úsalo solo para elementos gráficos (barras, numerales decorativos, iconos no esenciales) o titulares muy grandes decorativos acompañados de información que no dependa de él. Para texto naranja grande que deba leerse sobre blanco usa `#F16E00` (≈ 3:1, apto solo ≥24px o ≥18,5px bold). Texto de cuerpo nunca en naranja.
- **Negro sobre naranja**: ≈ 8:1 ✅ → botones y badges naranjas llevan **texto negro**.
- Blanco sobre naranja: ≈ 2,6:1 ❌ → no usar para texto (la única excepción es el propio logo).

```css
:root {
  --or-orange: #FF7900;
  --or-orange-text: #F16E00;
  --or-black: #000000;
  --or-white: #FFFFFF;
  --or-gray-100: #F6F6F6;
  --or-gray-300: #DDDDDD;
  --or-gray-500: #999999;
  --or-gray-700: #595959;
}
```

---

## 2. Tipografía

Hay **dos contextos**, no uno:

| Contexto | Fuente | Fuente de la norma |
|---|---|---|
| **Diseño de marca** (web, impresión, campañas, apps) | **Helvetica Neue**, solo Bold y Roman | Guía de comunicación del Grupo. El tema Office declara además "Helvetica 75 Bold" como fuente de titulares |
| **Office y correo de Orange España** (pptx, docx, xlsx, firma Outlook) | **Arial** (Bold + Regular) | Plantilla corporativa PPT y firma oficial: todos los placeholders y la firma van en Arial |

Regla práctica: **si el entregable va a abrirse en Office/Outlook, usa Arial; si es web/diseño, `"Helvetica Neue", Helvetica, Arial, sans-serif`.** Nunca mezcles ambas en la misma pieza.

Escala de la plantilla PPT (Arial, 16:9):

| Elemento | Tamaño | Peso |
|---|---|---|
| Título de portada | 36 pt (hasta 44 pt en portada alternativa) | Bold, anclado abajo |
| Título de diapositiva ("Message title") | 25 pt | Bold, arriba |
| Subtítulo | 16 pt | Regular |
| Cuerpo (1.º nivel) | 14–16 pt | Regular (resumen ejecutivo: 12–14 pt mínimo) |
| Tracker de página / Footnote | 8 pt | Regular |
| Sticker ("Preliminary", etc.) | 8 pt | Bold, MAYÚSCULAS |
| Portada: documento/fecha | 14 pt | Regular |

Escala web/diseño:

| Uso | Peso | Referencia |
|---|---|---|
| Titular de portada / sección | Bold | clamp(2.5rem, 6vw, 5rem) |
| Título de página | Bold | 1.75–2.25rem |
| Subtítulo numerado ("1.1 …") | Bold | 1rem |
| Cuerpo | Roman | 0.95–1.1rem, interlineado 1.4 |
| Notas al pie, legales | Roman | 0.65–0.75rem |

Reglas:
- **Sentence case** en titulares ("Our guiding principles", "Nuestros principios"). Solo el *sticker* va en mayúsculas. [derivado: la plantilla muestra títulos de ejemplo en mayúsculas en la portada, pero la guía del Grupo usa sentence case; confirmar con Brands&Comms si hay duda en una portada]
- La marca se escribe **"Orange"** (mayúscula inicial) en texto corrido. «orange™» en minúscula **solo** existe dentro del logo.
- Tracking ajustado en titulares grandes (`letter-spacing: -0.02em`), interlineado 1.0–1.1.
- Solo dos pesos. Nada de semibold, light ni cursivas decorativas.
- Web: fuentes de sistema, sin Google Fonts (eco-diseño, §3.5 de la guía).
- PPTX/DOCX: Arial. Si el usuario pide expresamente Helvetica Neue en Office, usa fallback Arial.

---

## 3. Logo (norma oficial: Guidelines Logo Orange, sept. 2026)

**Tres principios:** (1) el logo Master es un diseño personalizado → usa siempre el archivo original; (2) se sitúa sobre la retícula, normalmente en una esquina; (3) el **Small logo** es alternativa al Master (salvo publicidad impresa), ideal para digital y formatos pequeños.

Archivos (`assets/`): `orange-logo-master.svg` (preferido) · `orange-logo-master.png` (2362 px) · `orange-logo-256.png` · `orange-logo-master-mono.svg` · `orange-logo-small.svg` · `orange-logo-small-210.png`. Para impresión CMYK/Pantone pide los `.ai/.eps` al equipo de marca (están en el ZIP original `LOGO_ORANGE`, no en la skill).

**Nunca:** recolorear, recortar, redondear, sombrear, estirar, deformar, animar por cuenta propia ni *recrear* el logo (ni en CSS, ni en SVG propio, ni con Helvetica). Está permitido incrustar el SVG/PNG **oficial** tal cual.
- **Detector de falsificaciones:** si la «a» de «orange» tiene forma de lágrima, no es el logo Master (los falsos usan Helvetica). Antes de usar un logo que te pasen, mira la «a».
- El nombre de marca nunca aparece fuera del cuadrado. En cualquier otro texto: "Orange".
- Cuadrado naranja `#FF7900` con «orange™» en blanco. Wordmark y «TM» **siempre blancos**.

**Unidad X y espacio de seguridad.** El logo Master mide 2X; la retícula se construye sobre él.
- Espacio de seguridad: **0,5X** siempre que se pueda; **0,25X** si hay poco espacio (web) o se busca máxima visibilidad (vallas).

**Tamaño mínimo del Master:**

| Medio | X mínimo | Lado mínimo del logo (2X) |
|---|---|---|
| Impresión | 10 mm | 20 mm |
| Digital móvil | 30 px | 60 px |
| Digital tablet/ordenador | 50 px | 100 px |

Por debajo de ese mínimo → **Small logo**. Se usa cuando el Master saldría por debajo de 50 px (ordenador/tablet), 30 px (móvil) o 10 mm (impreso/branding de producto), **excepto en publicidad impresa**. Espacio de seguridad del Small: 0,25X.
- Small logo = cuadrado naranja + **línea blanca sólida** (representa «Orange»). Nunca: cambiar color de la línea, hacerla transparente, cambiar su tamaño, añadir «™», ni cambiar las versiones de color.
- ⚠ Esto corrige la regla antigua de "mínimo 40 px": el Master mínimo en pantalla es **100 px de lado en escritorio** y 60 px en móvil.

**Versiones de color.** Siempre que sea posible, **naranja** (Pantone® 151 en impresión). Funciona mejor sobre **negro o blanco**; sobre foto/ilustración debe verse con claridad y respetar el espacio de seguridad. Escala de grises (papel prensa): tinta del 60 % de negro; wordmark y «TM» siguen blancos. Versión mono: `orange-logo-master-mono.svg`.

**Posicionamiento.**
- La **esquina superior izquierda está reservada al titular principal** (en árabe, la superior derecha).
- El logo va en **una de las otras tres esquinas**, bien visible y con su espacio de seguridad. La plantilla PPT y la guía lo ponen **arriba a la derecha**.
- En comunicaciones ATL, la firma/logo solo en la **esquina inferior izquierda o inferior derecha**.
- Excepción real en los activos: en los fondos de videollamada "At home / At work" (sin titular) el logo sí va **arriba a la izquierda**: 122 px de lado sobre 1920×1080 (6,35 % del ancho) con margen de 100 px a izquierda y arriba.
- Cierre de deck / página final: logo grande centrado sobre blanco o negro es válido (así lo hace la plantilla).

**Animación:** logo Master, Small logo y firma pueden animarse, pero **lo gestiona estrictamente el equipo de marca**. No generes animaciones de logo.

---

## 4. Lenguaje gráfico (motivos recurrentes)

Estos son los elementos que dan identidad **[derivado de la guía de comunicación responsable del Grupo]**. Usa 2–3 por pieza, no todos. La plantilla corporativa de Orange España es más sobria que este lenguaje (ver `references/logo-y-formatos.md` §2): para decks internos/oficiales de Orange España prima la plantilla; para piezas comerciales/campañas, estos motivos.

1. **Barra vertical naranja** (≈8–10px de ancho, alta como el bloque de título) a la izquierda del titular. Es el motivo principal.
2. **Brazo horizontal**: línea fina (≈6px) que entra desde el borde izquierdo de la página y toca la barra vertical, formando una "T" tumbada. Negra sobre blanco, blanca sobre negro.
3. **Numerales gigantes naranjas** (Bold, 150–300px) como marcadores de sección, pueden solaparse con el borde de una foto.
4. **Guion subrayado naranja** corto (≈70×4px) bajo cada ítem de una rejilla.
5. **Caja negra de etiqueta** sobre foto: rectángulo negro anclado abajo-izquierda de la imagen, texto blanco Bold.
6. **Split de portada**: foto a la izquierda (≈50%), bloque negro a la derecha con titular blanco y barra naranja.
7. **Navegación "Menu >"**: texto negro Bold con el chevron `>` en naranja; barra naranja vertical corta anclada al borde inferior.
8. **Cierre**: página negra con el logo centrado, sin más elementos.

Siempre: **esquinas rectas (border-radius: 0)**, sin sombras, sin degradados, sin biseles, mucho espacio negativo.

### Estructura tipo
- **Portada**: split foto | negro, titular blanco Bold con barra naranja.
- **Índice / principios**: fondo negro, titular naranja con barra + brazo blanco, rejilla 2 columnas de foto + numeral naranja + caja negra con texto + guion naranja.
- **Página de contenido**: banda de foto arriba con numeral naranja solapado, título negro Bold con barra naranja, cuerpo en 2 columnas con subtítulos numerados en Bold.
- **Cierre**: negro + logo.

---

## 5. Componentes UI (web / app)

```css
/* Titular con barra y brazo */
.or-title { position: relative; padding-left: 28px; font-weight: 700; line-height: 1.05; letter-spacing: -0.02em; }
.or-title::before { content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 8px; background: var(--or-orange); }
.or-title--arm::after { content: ""; position: absolute; right: 100%; top: 50%; width: 100vw; max-width: 64px; height: 6px; background: currentColor; transform: translateY(-50%); }

/* Botón primario: naranja con texto NEGRO */
.or-btn { background: var(--or-orange); color: var(--or-black); border: 0; border-radius: 0; padding: 12px 24px; font-weight: 700; font-size: 1rem; }
.or-btn:hover { background: var(--or-black); color: var(--or-white); }
.or-btn:focus-visible { outline: 3px solid var(--or-black); outline-offset: 2px; }

/* Botón secundario */
.or-btn--ghost { background: transparent; color: var(--or-black); border: 2px solid var(--or-black); }
.or-on-dark .or-btn--ghost { color: var(--or-white); border-color: var(--or-white); }

/* Card: plana, sin sombra, acento con guion */
.or-card { background: var(--or-white); border: 1px solid var(--or-gray-300); border-radius: 0; padding: 24px; }
.or-card::after { content: ""; display: block; width: 70px; height: 4px; background: var(--or-orange); margin-top: 16px; }

/* Etiqueta sobre foto */
.or-photo-label { position: absolute; left: 0; bottom: 0; background: var(--or-black); color: var(--or-white); font-weight: 700; padding: 12px 16px; max-width: 70%; }

/* Numeral de sección */
.or-numeral { color: var(--or-orange); font-weight: 700; font-size: clamp(6rem, 18vw, 16rem); line-height: .8; }
```

- Iconos: trazo simple, monocolor negro (o blanco sobre negro); naranja solo para el icono protagonista. Lucide con `strokeWidth={2}` sirve.
- Gráficas: naranja para la serie protagonista, negro y grises para el resto. Nunca codificar significado solo con color (añade etiquetas/patrones).
- Modo oscuro: es natural en la marca (fondo `#000`, texto blanco, titulares naranja). Úsalo para portadas, KPIs y hero.
- Foco visible, targets táctiles ≥ 44px, `alt` en todas las imágenes.

---

## 6. Fotografía e imagen

- Personas reales, luz natural, momentos espontáneos y cercanos; reflejar diversidad de edad, género, origen, cuerpos y capacidades **sin estereotipos** (§3.2).
- La foto va a sangre o en bloques rectos; nunca con marcos redondeados ni sombras.
- Solo imágenes libres de derechos o con licencia, y con autorización de imagen de quien aparece; menores solo con consentimiento de tutores (§3.3–3.4). Si no tienes foto con derechos claros, usa un bloque negro o naranja con tipografía en lugar de inventar.
- **IA y personas: prohibido** generar personajes humanos ficticios con cara visible, avatares de personas reales (aunque consientan), deepfakes o música generada por IA (§5.4). Siluetas sin rasgos y fondos generados por IA son uso *restringido* (solo profesionales creativos). Claude, por tanto, no genera ni describe para generar caras humanas para piezas Orange: usa placeholders `[FOTO: descripción · banco de imágenes Orange]`.
- Priorizar el Orange Brand Image and Illustration Bank antes que generar (§5.6).
- **Escena tipo (fondos At home / At work)**: ambiente neutro y luminoso + *un único punto de color naranja*; la ilustración Orange enmarcada o una silla naranja hacen de protagonista. Ejemplos en `references/ejemplos/`.
- **Estilo de ilustración** (vectorial plano, trazo redondeado, personajes diversos, nube/cinta/nudo/círculo gris): descrito en `references/logo-y-formatos.md` §6. Las ilustraciones salen del banco, no se generan.

---

## 7. Formatos

- Slides: 16:9 (1920×1080 / 13,33×7,5 in). Márgenes 80px. Máx. ~40 palabras de cuerpo por slide. Redes y fondos: ver tabla de medidas en `references/logo-y-formatos.md` §3–5.
- Documentos: A4 vertical, 2 columnas de texto en páginas de contenido, márgenes amplios.
- Web: rejilla 12 columnas, contenido máx. ~1200px, mobile-first.
- **Sin paredes de texto (regla del usuario):** guías, páginas de consulta y paneles no obligan a scrollear más de ~1,5 pantallas al entrar. Colapsa con acordeones (uno abierto a la vez), agrupa en 3-5 bloques y usa pestañas para variantes; resumen de una línea por bloque. Si detectas una pared de texto, avísalo y recomienda esa estructura (detalle y medición: Eje 11 de `auditoria-ux-visual`).

---

## 8. Mensaje: reglas de comunicación responsable

Resumen operativo (detalle y ejemplos en `references/comunicacion-responsable.md`; léelo cuando el entregable contenga claims comerciales, medioambientales, datos o contenido IA):

1. **Todo dato, verificable y con fuente.** Cifras con fuente, alcance y periodo. Si no se puede verificar, no se publica: marca `[DATO PENDIENTE DE VALIDAR]` en lugar de inventar o redondear a favor.
2. **Claims comerciales exactos**: sin superlativos no demostrables ("el mejor", "100% seguro", "sin límites") y sin esconder condiciones relevantes (precio, permanencia, requisitos) en letra pequeña.
3. **Nada de greenwashing**: claims ambientales explícitos, precisos, proporcionados y con alcance ("reduce X% el consumo del equipo Y frente a Z, medido en…"), nunca "verde", "eco", "sostenible" genérico.
4. **Lenguaje claro**, directo y sin jerga, adaptado a la audiencia. Inclusivo.
5. **Testimonios** reales, con consentimiento, sin alterar. No inventar citas de clientes.
6. **Comparativas** con competidores conforme a la ley de publicidad comparativa: objetivas y verificables.
7. **Contenido generado total o parcialmente con IA** que vaya a publicarse: añadir el sello **"Designed by us, generated by AI."** (en castellano: "Diseñado por nosotros, generado con IA.") y requiere revisión humana antes de publicar.
8. **Datos personales y confidenciales**: no incluir datos de clientes reales en mockups o demos; usar datos ficticios evidentes.
9. **Eco-diseño**: páginas ligeras, fuentes de sistema, imágenes comprimidas, sin vídeo en autoplay, sin animaciones gratuitas.

Tono: cercano, claro y honesto; seguro pero sin promesas vacías. Titulares cortos (≤ 8 palabras) en sentence case, orientados al beneficio real y comprobable.

---

## 9. Checklist antes de entregar

Visual
- [ ] Solo naranja `#FF7900`, negro `#000`, blanco (+ grises funcionales). Sin amarillo.
- [ ] Helvetica Neue / Arial, solo Bold y Roman. Titulares en sentence case.
- [ ] Al menos un motivo de marca (barra vertical, numeral, guion, caja negra).
- [ ] Esquinas rectas, sin sombras ni degradados.
- [ ] Contraste AA: sin texto naranja pequeño sobre blanco, sin texto blanco sobre naranja; botones naranjas con texto negro.
- [ ] Logo original (comprobada la «a» sin lágrima), sin alterar, con espacio de seguridad ≥ 0,5X (0,25X en web).
- [ ] Logo Master ≥ 100 px (escritorio) / 60 px (móvil) / 20 mm (impreso); si no, Small logo (sin ™).
- [ ] Logo en esquina distinta de la superior izquierda (reservada al titular).
- [ ] Tipografía por contexto: Arial en Office/correo, Helvetica Neue en web/diseño.
- [ ] «Orange» con mayúscula inicial en texto; «orange™» solo dentro del logo.
- [ ] Amarillo `#FFE000`/tintes solo como serie de gráfica, nunca como color de marca.

Mensaje
- [ ] Cada cifra tiene fuente o está marcada como pendiente.
- [ ] Ningún claim absoluto o ambiental sin respaldo y alcance.
- [ ] Condiciones relevantes visibles.
- [ ] Sin caras humanas generadas por IA; fotos con derechos o placeholders.
- [ ] Si hay contenido IA para publicar: sello "Designed by us, generated by AI." y nota de revisión humana.
- [ ] Imágenes con `alt`, vídeo con subtítulos.

---

## 10. Flujo por tipo de entregable

- **.pptx** → leer también `/mnt/skills/public/pptx/SKILL.md`. **Partir de `assets/plantilla-orange-espana.pptx`** (layouts oficiales: Title, 1_Title, Default, 1/4, 1/3, 1/2, 2/3, 3/4, Top Left, En blanco - cierre, Contrast…, Reverse Contrast…). Arial. Si el entregable es una pieza comercial/campaña (no deck corporativo), usa los motivos de la sección 4.
- **Firma de correo** → `assets/firma-orange-arial.docx` + `references/logo-y-formatos.md` §4.
- **Cabecera LinkedIn/X o fondo de videollamada** → `references/logo-y-formatos.md` §3 y §5, con los ejemplos de `references/ejemplos/`.
- **HTML / React / dashboards** → leer `/mnt/skills/public/frontend-design/SKILL.md`; variables `:root` de la sección 1 y componentes de la sección 5. Si aplica, pasar después `/ux` (auditoria-ux-visual).
- **.docx** → leer `/mnt/skills/public/docx/SKILL.md`; H1 negro Bold con borde izquierdo naranja, cuerpo Roman, 2 columnas en contenido.
- **Copy / emails / argumentarios** → sección 8 + `references/comunicacion-responsable.md`.

---

## 11. Ejemplo mínimo (HTML)

```html
<style>
  :root { --or-orange:#FF7900; --or-black:#000; --or-white:#fff; --or-gray-700:#595959; }
  body { margin:0; font-family:"Helvetica Neue",Helvetica,Arial,sans-serif; color:var(--or-black); background:var(--or-white); }
  .hero { background:var(--or-black); color:var(--or-white); padding:64px 24px 64px 0; }
  .or-title { position:relative; margin:0 0 0 48px; padding-left:28px; font-size:clamp(2.5rem,6vw,4.5rem); line-height:1.05; letter-spacing:-.02em; color:var(--or-orange); }
  .or-title::before { content:""; position:absolute; left:0; top:0; bottom:0; width:8px; background:var(--or-orange); }
  .or-title::after  { content:""; position:absolute; right:100%; top:50%; width:48px; height:6px; background:var(--or-white); transform:translateY(-50%); }
  .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:40px; padding:48px; }
  .item h3 { margin:0 0 8px; font-size:1.1rem; }
  .item p { margin:0; color:var(--or-gray-700); line-height:1.4; }
  .item::after { content:""; display:block; width:70px; height:4px; background:var(--or-orange); margin-top:16px; }
  .or-btn { background:var(--or-orange); color:var(--or-black); border:0; border-radius:0; padding:14px 24px; font-weight:700; font-size:1rem; font-family:inherit; }
</style>
<section class="hero"><h1 class="or-title">Tu flota, conectada</h1></section>
<section class="grid">
  <div class="item"><h3>1 Visibilidad</h3><p>Ubicación de cada vehículo en tiempo real.</p></div>
  <div class="item"><h3>2 Cumplimiento</h3><p>Registro digital preparado para la normativa aplicable.</p></div>
  <div class="item"><h3>3 Ahorro</h3><p>[DATO PENDIENTE DE VALIDAR: % ahorro, fuente y periodo]</p></div>
</section>
```
