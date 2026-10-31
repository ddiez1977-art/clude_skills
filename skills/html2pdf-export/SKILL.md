---
name: html2pdf-export
description: >
  Estrategias probadas para exportar HTML complejo a PDF con html2pdf.js en
  aplicaciones vanilla JS (sin frameworks ni build step). Cubre: configuración
  óptima, reglas CSS de salto de página, patrón pre/post export para manipular
  DOM antes y después de la captura, unidades atómicas en tablas, elementos
  visibles solo en pantalla vs solo en PDF, y arquitectura de dos modos de
  salida (HTML navegable / PDF imprimible). Activar cuando: "exportar a PDF",
  "html2pdf", "pagebreak", "saltos de página", "documento imprimible",
  "generar PDF", "modo HTML vs PDF", o al construir cualquier feature de
  generación de documentos en herramientas web.
---

# html2pdf-export — Exportación PDF desde HTML puro

Patrones validados con html2pdf.js 0.10.1 + Chromium headless en proyectos
de producción. Agnósticos de proyecto, dominio y framework.

---

## 1. CONFIGURACIÓN ÓPTIMA

```javascript
const opt = {
  margin: 10,                               // mm — uniforme en los 4 lados
  filename: 'documento.pdf',
  image:      { type: 'jpeg', quality: 0.98 },  // JPEG más compacto que PNG
  html2canvas: { scale: 1.5, useCORS: true },   // 1.5 = nitidez sin peso excesivo
  jsPDF: { orientation: 'portrait', unit: 'mm', format: 'a4' },

  // CRÍTICO: nunca usar 'avoid-all'.
  // 'avoid-all' marca TODOS los elementos como indivisibles → secciones de ~1 página
  // no caben junto a la portada → página 1 queda en blanco.
  // Con ['css','legacy'] solo se respetan los break-* que tú defines explícitamente.
  pagebreak: { mode: ['css', 'legacy'] }
};

// Uso básico
html2pdf().set(opt).from(document.getElementById('mi-doc')).save();

// Uso con promesa (necesario para pre/post export)
await html2pdf().set(opt).from(elemento).save();
```

**Versión fija en CDN (nunca usar "latest"):**
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
```

---

## 2. LAS 4 REGLAS CSS DE SALTO DE PÁGINA

```
A) break-inside:avoid  → nunca cortar este bloque por dentro
B) break-before:avoid  → este bloque no empieza justo en un salto de página
C) break-after:avoid   → no hay salto de página justo después de este bloque
D) break-before:page   → FORZAR nuevo salto antes de este elemento
```

```css
/* ── A: Elementos que nunca se parten internamente ─────────── */
p, li, h1, h2, h3, h4,
.card, .bloque, .stat, .fase, .item {
  page-break-inside: avoid;   /* compatibilidad navegadores antiguos */
  break-inside: avoid;
  orphans: 3;   /* mín. 3 líneas al final de página */
  widows: 3;    /* mín. 3 líneas al inicio de página */
}

/* ── B: Encabezado de sección nunca separado de su cuerpo ──── */
.seccion-titulo {
  page-break-after: avoid;
  break-after: avoid;        /* regla C sobre el título */
}

/* ── C: Cabecera de tabla arrastra su primera fila de datos ── */
tr.cabecera-grupo {
  page-break-after: avoid;
  break-after: avoid;
  page-break-inside: avoid;
  break-inside: avoid;
}
tr.cabecera-grupo + tr {
  page-break-before: avoid;  /* la primera fila no puede iniciar nueva página */
  break-before: avoid;
}

/* ── D: Forzar nueva página entre secciones ────────────────── */
.seccion + .seccion {
  break-before: page;
  page-break-before: always;
}
/* O selectivamente con clase */
.nueva-pagina {
  break-before: page;
  page-break-before: always;
}

/* ── Grids: pequeños (≤3 items) → avoid · grandes → auto ───── */
/* TRUCO: break-inside:avoid en grids grandes genera páginas vacías */
.grid-pequeño { page-break-inside: avoid; break-inside: avoid; }
.grid-grande  { page-break-inside: auto;  break-inside: auto; }
```

---

## 3. PATRÓN PRE/POST EXPORT — Manipulación DOM

**Por qué:** html2pdf usa html2canvas para capturar el DOM **exactamente como
se ve en pantalla**. `@media print` NO funciona con html2pdf — el CSS print
se ignora durante la captura. La única forma de controlar qué aparece en el
PDF es manipular el DOM antes de la captura y restaurarlo después.

```javascript
/**
 * Preparar el DOM para la captura PDF.
 * Llaman antes de html2pdf().save()
 */
function preExportFix(contenedor) {
  // ── 1. Ocultar elementos que son SOLO de pantalla ─────────────────
  contenedor.querySelectorAll('.no-pdf, .solo-pantalla, nav, .topbar, .sidebar').forEach(el => {
    el.setAttribute('data-pdf-oculto', el.style.display || '');
    el.style.display = 'none';
  });

  // ── 2. Mostrar elementos que son SOLO de PDF ──────────────────────
  contenedor.querySelectorAll('.solo-pdf, .pdf-footer, .pdf-portada').forEach(el => {
    el.setAttribute('data-pdf-visible', '1');
    el.style.display = el.dataset.pdfDisplay || 'block';
  });

  // ── 3. Convertir tablas complejas a mini-tablas (ver sección 4) ───
  // Solo si la tabla tiene filas que no pueden partirse
}

/**
 * Restaurar el DOM tras la captura PDF.
 * Llamar en el .then() Y en catch() — usar finally si es posible.
 */
function postExportFix(contenedor) {
  // Restaurar elementos ocultos
  contenedor.querySelectorAll('[data-pdf-oculto]').forEach(el => {
    el.style.display = el.getAttribute('data-pdf-oculto');
    el.removeAttribute('data-pdf-oculto');
  });

  // Ocultar de nuevo elementos que solo eran para PDF
  contenedor.querySelectorAll('[data-pdf-visible]').forEach(el => {
    el.style.display = 'none';
    el.removeAttribute('data-pdf-visible');
  });

  // Restaurar tablas si se convirtieron (ver sección 4)
}

// ── Uso completo ──────────────────────────────────────────────────
async function exportarPDF(elementoId, nombreArchivo) {
  const contenedor = document.getElementById(elementoId);
  const opt = { /* ... ver sección 1 ... */ filename: nombreArchivo };

  preExportFix(contenedor);
  try {
    await html2pdf().set(opt).from(contenedor).save();
  } finally {
    postExportFix(contenedor);  // SIEMPRE restaurar, incluso si falla
  }
}
```

**Patrón `data-*` para guardar el estado:**
El atributo `data-pdf-oculto` preserva el valor de `display` original del
elemento, permitiendo restaurarlo exactamente sin conocer el valor de antemano.

---

## 4. UNIDADES ATÓMICAS EN TABLAS

**El problema:** `break-inside:avoid` en `<tbody>` con `border-collapse` no
funciona de forma fiable en html2pdf. El motor parte filas por la mitad.

**La solución:** convertir cada "unidad indivisible" (conjunto de filas que
deben ir juntas) en una `<table>` propia con `break-inside:avoid`.

```javascript
/**
 * Define las reglas de cohesión según tu tabla:
 * - fila de cabecera  → va con la fila siguiente (la primera de datos)
 * - fila de detalle   → va con la fila anterior  (la que la introduce)
 * - fila de subtotal  → va con la fila anterior
 * - fila de total     → va con la fila anterior
 */
function agruparEnUnidades(filas) {
  const unidades = [];
  let actual = null;
  let pegarSiguiente = false;

  filas.forEach(tr => {
    const esCabecera = tr.classList.contains('fila-cabecera');
    const esDetalle  = tr.classList.contains('fila-detalle');
    const esTotal    = tr.classList.contains('fila-total');

    // Esta fila se pega a la ANTERIOR
    if ((esDetalle || esTotal) && actual) {
      actual.push(tr);
      unidades.push(actual);
      actual = null;
      pegarSiguiente = false;
      return;
    }

    // Hay que pegar esta fila a la anterior (por pegarSiguiente)
    if (pegarSiguiente && actual) {
      actual.push(tr);
      pegarSiguiente = false;
      return;
    }

    // Nueva unidad
    if (actual) unidades.push(actual);
    actual = [tr];
    pegarSiguiente = esCabecera;  // cabecera arrastra la siguiente
  });

  if (actual) unidades.push(actual);
  return unidades;
}

function convertirAMiniTablas(tabla) {
  // CRÍTICO: el colgroup debe sumar exactamente 100%.
  // Si no llega al 100%, el sobrante se reparte de forma impredecible
  // entre mini-tablas → columnas desalineadas visualmente.
  const COLGROUP = `<colgroup>
    <col style="width:45%">
    <col style="width:25%">
    <col style="width:30%">
  </colgroup>`;  // Ajustar a tu tabla. DEBEN sumar 100%.

  const tbody = tabla.querySelector('tbody');
  const filas = Array.from(tbody.querySelectorAll('tr'))
    .filter(tr => !tr.classList.contains('fila-separador'));

  const unidades = agruparEnUnidades(filas);
  const wrapper = document.createElement('div');
  wrapper.id = '_pdf_wrapper';
  wrapper.dataset.tablaOriginal = tabla.id;

  unidades.forEach(grupo => {
    const mini = document.createElement('table');
    mini.className = tabla.className;
    mini.style.cssText = 'width:100%;border-collapse:collapse;break-inside:avoid;page-break-inside:avoid;margin-bottom:0';
    mini.innerHTML = COLGROUP;
    const miniBody = document.createElement('tbody');
    grupo.forEach(tr => miniBody.appendChild(tr.cloneNode(true)));
    mini.appendChild(miniBody);
    wrapper.appendChild(mini);
  });

  tabla.parentNode.replaceChild(wrapper, tabla);
  return wrapper;
}

// En postExportFix: restaurar la tabla original
function restaurarTabla(contenedor) {
  const wrapper = contenedor.querySelector('#_pdf_wrapper');
  if (!wrapper) return;
  const tablaOriginal = document.getElementById(wrapper.dataset.tablaOriginal);
  if (tablaOriginal) wrapper.parentNode.replaceChild(tablaOriginal, wrapper);
}
```

---

## 5. DOS MODOS DE SALIDA: HTML NAVEGABLE VS PDF

El mismo contenido generado con dos renderizaciones distintas:

```javascript
const MODO = { HTML: 'html', PDF: 'pdf' };

async function generarDocumento(datos, modo) {
  if (modo === MODO.HTML) {
    // ── HTML navegable: Blob → nueva pestaña ─────────────────────
    const html = construirHTML(datos, modo);
    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    window.open(url, '_blank');
    // URL.revokeObjectURL(url) tras un timeout si quieres limpiar memoria

  } else {
    // ── PDF: DOM temporal → captura → destruir ────────────────────
    const html = construirHTML(datos, modo);
    const tmp = document.createElement('div');
    tmp.style.cssText = 'position:absolute;left:-9999px;top:0;width:210mm;';
    tmp.innerHTML = html;
    document.body.appendChild(tmp);

    preExportFix(tmp);
    try {
      await html2pdf().set({ ...opt, filename: 'documento.pdf' }).from(tmp).save();
    } finally {
      postExportFix(tmp);
      document.body.removeChild(tmp);
    }
  }
}

function construirHTML(datos, modo) {
  const esHTML = modo === MODO.HTML;
  return `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <style>
    ${estilosBase()}
    ${esHTML ? estilosNavegacion() : estilosImpresion()}
  </style>
  ${!esHTML ? '<script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"><\/script>' : ''}
</head>
<body>
  ${esHTML ? construirHub(datos) : construirLineal(datos)}
</body>
</html>`;
}

// ── Modo HTML: navegación interactiva ──────────────────────────
function estilosNavegacion() {
  return `
    nav { display: flex; /* menú lateral o topbar */ }
    .card:hover { box-shadow: 0 4px 12px rgba(0,0,0,.1); cursor: pointer; }
    a { color: inherit; text-decoration: none; }
  `;
}

// ── Modo PDF: pagebreaks, sin interactividad ───────────────────
function estilosImpresion() {
  return `
    nav, .topbar, .sidebar, button, .no-pdf { display: none !important; }
    .seccion { break-before: page; page-break-before: always; }
    .seccion:first-of-type { break-before: auto; page-break-before: auto; }
    .card { break-inside: avoid; page-break-inside: avoid; }
  `;
}

// ── Hub navegable ─────────────────────────────────────────────
function construirHub(datos) {
  // Genera HTML con menú lateral, anclas, secciones colapsables, etc.
  return `
    <nav><!-- navegación por categorías/secciones --></nav>
    <main><!-- contenido organizado en secciones con anclas --></main>
  `;
}

// ── Documento lineal imprimible ────────────────────────────────
function construirLineal(datos) {
  // Genera HTML lineal sin menú, con pagebreaks entre secciones
  return `
    <div class="portada"><!-- portada con título, fecha, autor --></div>
    <div class="seccion"><!-- sección 1 --></div>
    <div class="seccion"><!-- sección 2 --></div>
  `;
}
```

---

## 6. FOOTER FIJO EN TODAS LAS PÁGINAS

```css
.pdf-footer { display: none; }  /* Oculto en pantalla */
```

```javascript
// En preExportFix: mostrar y fijar el footer
contenedor.querySelectorAll('.pdf-footer').forEach(el => {
  el.style.cssText = [
    'display:flex',
    'align-items:center',
    'justify-content:space-between',
    'position:fixed',   // fixed en PDF = se repite en TODAS las páginas
    'bottom:0',
    'left:0',
    'right:0',
    'height:24px',
    'padding:0 10mm',
    'background:#fff',
    'border-top:1px solid #eee',
    'font-size:8px',
    'color:#aaa'
  ].join(';');
});
```

---

## 7. POSICIONAMIENTO DE TOOLTIPS/POPOVERS CERCA DEL BORDE

Para elementos UI (tours guiados, tooltips, popovers) que no deben salirse
de la ventana en landscape ni en pantallas pequeñas:

```javascript
function posicionarTooltip(targetEl, tooltipEl, opciones) {
  const opts = Object.assign({ margenSuperior: 0, anchoTooltip: 300 }, opciones);

  // Márgenes de seguridad adaptados a la orientación
  const esVertical    = window.innerHeight > window.innerWidth;
  const esPantallaAlta = window.innerHeight >= 900;
  const MARGEN_INF    = esVertical ? 40 : (esPantallaAlta ? 60 : 80);
  const MARGEN_SUP    = opts.margenSuperior;
  const ANCHO         = opts.anchoTooltip;

  // Medir altura REAL del tooltip tras renderizar su contenido
  // (evita desbordes cuando el texto es más largo de lo esperado)
  tooltipEl.style.visibility = 'hidden';
  tooltipEl.style.display = 'block';
  document.body.appendChild(tooltipEl);
  const altoReal = tooltipEl.offsetHeight;
  tooltipEl.style.visibility = '';

  const rect = targetEl.getBoundingClientRect();

  // Intentar colocar debajo; si no cabe, colocar arriba
  let top = rect.bottom + 10;
  if (top + altoReal > window.innerHeight - MARGEN_INF) {
    top = rect.top - altoReal - 10;
  }
  top = Math.max(MARGEN_SUP, Math.min(top, window.innerHeight - altoReal - MARGEN_INF));

  const left = Math.max(8, Math.min(rect.left, window.innerWidth - ANCHO - 8));

  tooltipEl.style.top  = top + 'px';
  tooltipEl.style.left = left + 'px';
}
```

---

## 8. APERTURA DE DOCUMENTO EN NUEVA PESTAÑA (sin servidor)

```javascript
// Opción A: Blob URL (funciona offline, la URL es temporal)
function abrirEnNuevaTab(htmlString) {
  const blob = new Blob([htmlString], { type: 'text/html; charset=utf-8' });
  const url  = URL.createObjectURL(blob);
  const win  = window.open(url, '_blank');
  if (!win) {
    // El navegador bloqueó el popup → informar al usuario
    alert('Permite las ventanas emergentes para este sitio y vuelve a intentarlo.');
  }
  // Liberar memoria tras un tiempo prudencial
  setTimeout(() => URL.revokeObjectURL(url), 60000);
}

// Opción B: Archivo estático en el mismo dominio (funciona offline si está cacheado)
function abrirArchivoEstatico(ruta) {
  // El archivo lee datos del localStorage que comparte el mismo origen
  const win = window.open(ruta, '_blank');
  if (!win) alert('Permite las ventanas emergentes para este sitio.');
}
// Ejemplo: window.open('exportar.html', '_blank')
// El archivo exportar.html lee localStorage.getItem('mis-datos') al cargar
```

---

## 9. CHECKLIST COMPLETO

```
CONFIGURACIÓN html2pdf
□ Versión fija en CDN (0.10.1 o la que hayas validado — nunca "latest")
□ pagebreak: { mode: ['css', 'legacy'] } — NUNCA 'avoid-all'
□ html2canvas.scale: 1.5 (equilibrio nitidez/peso)
□ image.type: 'jpeg', quality: 0.98
□ jsPDF.format: 'a4', orientation: 'portrait' (o 'landscape' si aplica)

CSS PAGEBREAK
□ Elementos atómicos: break-inside:avoid + page-break-inside:avoid
□ Encabezados: break-after:avoid para que no queden solos al final de página
□ Tablas: cabecera + primera fila de datos van juntas (break-after:avoid + break-before:avoid)
□ COLGROUP de tablas suma exactamente 100%
□ Grids grandes (4+ items): break-inside:auto — evitar avoid en grids grandes
□ Footer con position:fixed (se repite en todas las páginas)

DOM MANIPULATION (Pre/Post Export)
□ preExportFix oculta: nav, topbar, sidebar, botones, elementos interactivos
□ preExportFix muestra: footer PDF, portada, elementos decorativos solo-PDF
□ postExportFix en bloque finally — siempre restaura aunque falle el export
□ Usar atributos data-* para guardar el estado original del display
□ Tablas complejas: convertir a mini-tablas con agruparEnUnidades()

DOS MODOS DE SALIDA
□ HTML navegable: Blob → URL.createObjectURL → window.open (sin html2pdf)
□ PDF: DOM temporal off-screen → preExportFix → html2pdf → postExportFix → remove
□ CSS diferenciado: estilosNavegacion() solo en HTML, estilosImpresion() solo en PDF
□ Navegación/menú lateral visible en HTML, oculto en PDF
□ break-before:page entre secciones en PDF, anclas href en HTML

IMÁGENES Y LOGOS
□ Logos como base64 inline (evita requests externos durante la captura)
□ Si hay imágenes externas: useCORS:true y asegurarse de que el servidor
  devuelve cabeceras CORS
□ Imágenes grandes: comprimir antes de incrustar como base64
```

---

## 10. ANTIPATRONES DOCUMENTADOS

| Antipatrón | Síntoma | Solución |
|------------|---------|----------|
| `pagebreak: { mode: 'avoid-all' }` | Página 1 en blanco cuando hay secciones largas | Usar `['css','legacy']` |
| Confiar en `@media print` para ocultar elementos | El elemento aparece en el PDF | Usar `preExportFix` con `style.display='none'` |
| COLGROUP que no suma 100% | Columnas desalineadas entre mini-tablas | Ajustar anchos hasta sumar exactamente 100% |
| `break-inside:avoid` en grids de 4+ items | Páginas vacías o contenido mal distribuido | Solo en grids de ≤3 items; grids grandes → `auto` |
| `break-inside:avoid` en `<tbody>` con `border-collapse` | Filas partidas por la mitad | Convertir a mini-tablas con `agruparEnUnidades()` |
| No usar `finally` en el export | UI rota si falla el PDF (nav oculto, tablas fragmentadas) | `try { await save() } finally { postExportFix() }` |
| Imágenes externas sin CORS | html2canvas las ignora o lanza error | Base64 inline o servidor con cabeceras CORS |
| Medir tooltips antes de añadirlos al DOM | `offsetHeight = 0` → desbordes | Insertar con `visibility:hidden`, medir, luego mostrar |
| Popup sin comprobación de bloqueo | El archivo se abre pero el usuario no lo ve | `if (!window.open(...)) { informar al usuario }` |

---

*Skill genérica · Validada con html2pdf.js 0.10.1 · Chromium headless*
*Extraída de proyectos de producción en Orange Empresas / 24 Jul 2026*
