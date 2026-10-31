# Logo y formatos corporativos — Orange España

Complemento de `SKILL.md`. Fuentes: Guidelines Logo Orange (Brands&Comms, sept. 2026), plantilla PPT "Orange España", cabeceras LinkedIn/X, firma Outlook, fondos "At home / At work". Lo marcado **[medido]** se extrajo de los archivos; **[derivado]** es inferencia.

---

## 1. Retícula y logo

- La retícula es invisible y se construye sobre el logo Master = **2X**. Para formatos no estándar: usa la plantilla más cercana y escálala proporcionalmente.
- Titular principal: esquina superior izquierda. Logo: otra de las tres esquinas (arriba derecha por defecto).
- Espacio de seguridad 0,5X (0,25X web/vallas). Mínimos: 10 mm impreso · 30 px móvil · 50 px escritorio (valor de X; el lado del logo es 2X).
- Small logo: bajo esos mínimos, nunca en publicidad impresa, sin «™», línea blanca sólida.

### Fórmulas útiles
```
lado_logo_px      = 2 · X
margen_seguridad  = 0.5 · X   (0.25 · X en web)
Ejemplo fondo 1920×1080 [medido]: lado = 122 px  →  X = 61 px  →  seguridad 0,5X = 30,5 px;
                                  posición (100, 100) px = esquina sup. izq.
```

### Cómo incrustar en HTML
Usa el SVG oficial (`assets/orange-logo-master.svg`, 2 KB) inline o como `<img>` con `alt="Orange"` y `width` ≥ 100 (escritorio) / 60 (móvil). Por debajo → `orange-logo-small.svg`.

---

## 2. Plantilla PowerPoint "Orange España" (`assets/plantilla-orange-espana.pptx`)

Formato 16:9 (12 192 000 × 6 858 000 EMU = 13,33 × 7,5 in). Tema Office: acentos `FF7900 / 000000 / FFC999 / 86868E / FFE000 / DEDDE0`, texto `000000`, fondo `FFFFFF`. Fuente Arial.

**Layouts disponibles [medido]:** `Title`, `1_Title`, `Default`, `1/4`, `1/3`, `1/2`, `2/3`, `3/4`, `En blanco - cierre`, `Top Left`, `Contrast Title`, `Contrast Default`, `Contrast 1/4 · 1/3 · 1/2 · 2/3`, `Reverse Contrast 1/2 · 2/3 · 3/4`, y la serie `1_Diseño personalizado … 7_Diseño personalizado` (portadas con logo grande, rejillas de 2–3 fotos con flecha naranja, gráficas).

**Anatomía de una diapositiva de contenido [medido]:**
- *On-page tracker* (arriba izq., 8 pt) → *Slide title* (25 pt Bold) → *Subtitle* (16 pt).
- Logo Master **arriba a la derecha**.
- Pie: «**Orange España**» en negrita 8 pt abajo a la izquierda; número de página abajo a la derecha.
- *Sticker* opcional (8 pt Bold mayúsculas, p. ej. "Preliminary").
- Separadores: líneas finas negras/grises; **fila activa de la agenda** = barra naranja `#FF7900`.
- Portada: título Bold abajo, subtítulo 20 pt, tira de logos de marcas del grupo (Jazztel, MásMóvil, Pepephone, Yoigo, Llamaya, Lebara, Euskaltel, R, Telecable, Guuk, Embou, Populoos) en el pie de la portada `Title`; versión con bloque naranja inferior y logo Master centrado grande.
- Variantes `Contrast` y `Reverse Contrast`: fondo **negro** con texto blanco, para portadas de sección y KPIs.
- Biblioteca de iconos (diapositiva 24): línea fina monocolor. Úsala antes de inventar iconos.
- Gráficas: serie 1 naranja, serie 2 negra, 3.ª `#FFC999`, 4.ª `#86868E`, 5.ª `#FFE000`; leyendas con cuadrados o círculos, nunca solo color.

**Cómo usarla con la skill pptx:** abre la plantilla, elimina las diapositivas de ejemplo que no uses, y construye sobre el layout correspondiente (no dibujes a mano logo, pie ni tracker: ya están en el layout/master). Si cambias el logo, que sea desde el archivo oficial.

---

## 3. Cabeceras de redes sociales [medido]

| Red | Tamaño | Fondo | Notas |
|---|---|---|---|
| LinkedIn | **1584 × 396 px** | Negro `#000000` | Contenido desplazado a la derecha: el tercio izquierdo queda libre porque lo tapa la foto de perfil |
| X | **1500 × 500 px** | Negro `#000000` | Misma composición |

Tres opciones oficiales por red:
1. **OP1 · Wordmark**: logo Master + «**Orange**» en Bold naranja, a la derecha.
2. **OP2 · Personas**: tres figuras ilustradas en círculos gris claro pasándose un testigo naranja; **Small logo** abajo a la derecha.
3. **OP3 · Digital**: figura ilustrada surfeando una estela naranja/rosa hacia una pantalla con iconos; **Small logo** abajo a la derecha.

Reglas **[derivado]**: fondo siempre negro; en OP2/OP3 se usa el *Small logo* (formato pequeño en una pieza muy apaisada); elementos clave fuera de la zona izquierda y de los bordes inferiores donde cada red superpone UI. Imágenes de ejemplo en `references/ejemplos/cabecera-*.jpg`.

---

## 4. Firma de correo Outlook [medido]

Archivo: `assets/firma-orange-arial.docx`. Se descarga del portal *Identidad Visual* y se copia/pega en Outlook (M365 escritorio y web; tutorial oficial *Guía para crear una firma corporativa en Microsoft Outlook*, sept. 2026).

Estructura exacta (todo **Arial**):
```
[Small logo ~14,5 × 14,3 mm]   **Nombre Apellido**        ← negrita
                               **Función**                ← negrita
                               Orange España
                               Móvil: 00 34 xxx xxx xxx
                               xxx.xxx@orange.es          ← color #FF7900
                               Dirección (opcional)
                               www.orange.es
```
Reglas: formato de teléfono `00 34 xxx xxx xxx`; solo el correo va en naranja `#FF7900`; la dirección es opcional; no añadir frases, imágenes ni banners propios. La firma puede animarse **solo** vía equipo de marca.

---

## 5. Fondos de videollamada "At home / At work" [medido]

Serie de **1920 × 1080 px** (16:9), PNG/JPG. Logo Master 122 px en (100, 100). Ejemplos reducidos en `references/ejemplos/fondo-*.jpg`.

- **At home** (athome1–4, theme-home5/7): interiores escandinavos neutros (pared gris/crema, madera clara, plantas, velas, tocadiscos, relojes) con un **cuadro enmarcado** que lleva una ilustración Orange: nube naranja con columpios, línea continua naranja sobre negro (auriculares, figura con brazo en alto), cinta/varita sobre blanco, nudo naranja abstracto, bíceps con corazón naranja, escena de playa (cielo azul, arena amarilla, sol y sombrilla naranja).
- **At work** (atwork1/3/4): atrio y oficinas de la sede de Orange (arquitectura blanca, vegetación, sillas y sofás naranjas).
- Fórmula **[derivado]**: *escena neutra y luminosa + un único punto de color naranja* (la ilustración o una silla). El naranja nunca ocupa más del ~15 % del encuadre.

⚠ Si generas fondos nuevos: **no generes con IA personas ni caras** (norma del Grupo, ver `comunicacion-responsable.md`). Para nuevas escenas usa el banco de imágenes de Orange; con Claude, deja placeholder `[FOTO: descripción · banco de imágenes Orange]` y coloca el logo con las coordenadas de arriba.

---

## 6. Estilo de ilustración Orange [derivado de los activos]

Úsalo para describir o encargar ilustraciones, **no para que Claude genere personas**:
- Vectorial plano, sin degradados ni sombras; trazo grueso de contornos curvos y redondeados.
- Naranja `#FF7900` protagonista; negro y grises para figuras; toques de azul `#4BB4E6`, verde `#50BE87`, rosa `#FFB4E6`.
- Personajes diversos (edad, tono de piel, pelo), sin estereotipos, en movimiento (columpio, testigo, surf, baile).
- Motivos recurrentes: nube, cinta/línea continua, nudo, círculo gris como "ventana", corazón, bíceps, sol.
- Líneas continuas naranja sobre fondo negro para versión "nocturna".
