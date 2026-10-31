---
name: auditoria-pedagogica-jogasan
description: "Auditor e Inspector Integral de Experiencias Educativas de JoGaSan Academy. Evalúa código (HTML/CSS/JS vanilla), contenidos didácticos y mecánicas de gamificación de las academias de 3º, 4º y 6º de Primaria, 1º ESO y el área infantil (Infantil). Aplica rúbrica de 4 pilares: Rigor Curricular, UX/Accesibilidad TDAH, Motivación/Gamificación y Trazabilidad Docente. Úsala SIEMPRE que el usuario pida \"auditar\" una pantalla, módulo, quiz, actividad, teoría o examen del portal. También cuando diga \"revisar contenido\", \"validar ejercicio\", \"inspeccionar quiz\", \"comprobar teoría\", \"revisar chunk\", \"validar medalla\", \"comprobar trazabilidad\", \"lupa del profe\", \"chip de lectura\", o al pegar código HTML/JS de una academia para revisión. Activa también ante: \"¿está bien esto para 3º?\", \"¿es correcto para 6º?\", \"¿cumple currículum?\", \"revisa si el quiz captura errores\", \"valida la gamificación\", o al mencionar una academia específica (Geometría, Inglés, Naturales, etc.) junto con cualquier petición de revisión.\n"
---

# 🛡️ Auditor Pedagógico — JoGaSan Academy

## Fase 0: Sincronización Obligatoria

**Antes de cualquier evaluación**, lee el archivo de reglas maestras:
→ `references/REGLAS_AUDITORIA.md` (si existe en tu copia de la skill) y, en el repo, `CLAUDE.md` y `CONTEXT_ADN-JoGaSan-Academy-LATEST.md`

Este documento es el núcleo normativo del proyecto. Contiene los 4 criterios de rúbrica, los principios innegociables y el protocolo de reporte.

---

## 📐 Principios Innegociables (resumen rápido)

| Regla | Detalle |
|---|---|
| **Terminología** | SIEMPRE "chicos". NUNCA "niños". |
| **Fracciones** | NO pedir simplificación salvo que el tema lo exija explícitamente. |
| **Gráficos** | Minimalistas, esquemáticos, sin figuras humanas. |
| **Chunks** | 1 interacción/minuto mínimo. Chip de lectura activo = 1-2 min para desbloquear quiz. |
| **SVGs obligatorios** | **Cada bloque de teoría lleva su figura SVG (regla del usuario, 12-oct; check FG de `validar-academias.js`, síntoma 80 de `clonar-academia`)**. Toda teoría con formas, fórmulas o procesos visuales DEBE incluir diagramas SVG propios. Penalizable en Pilar A. Cada figura pasa la rúbrica R1-R6 de «Figuras SVG» (abajo): **nunca muestra el ejemplo que pregunta el quiz**. |
| **Sin castigo** | Fallar NUNCA resta (puntos, Aura < 50 % = 0 + ánimo, medallas) y siempre explica el porqué. El cronómetro no arranca solo. Los aciertos de teoría no puntúan. |
| **Sin patrones** | Cada intento cambia el orden de preguntas y de opciones; nada parecido seguido; el quiz final no copia las actividades ni la teoría (`QuizEngine`, `prepararBanco`, `node scripts/buscar-copias-teoria.js`). |
| **El quiz sale de la teoría** | Cada pregunta del quiz final evalúa un ejemplo o ejercicio RESUELTO de la teoría del módulo: mismo tipo y método, **datos nuevos** (regla del usuario, 11-oct-2026). Nada que la teoría no enseñó; nada con los mismos números/palabras. Se comprueba con la matriz de cobertura (pregunta → ejemplo) y `buscar-copias-teoria.js`. Una pregunta sin ejemplo en la teoría es fallo del Pilar A; un enunciado copiado, también. |
| **Inglés bilingüe** | Solo donde hay inglés: teoría, ejemplos y ENUNCIADOS con la traducción pegada y otro formato; **nunca lo que resuelve el ejercicio** (frase del hueco, opciones, lecturas con preguntas). Ver «Checklist bilingüe» (abajo, manda sobre B.1/B.5). |
| **Paso a paso modelo** | Todo módulo con problemas DEBE tener ≥1 problema resuelto paso a paso ANTES de los ejercicios libres. Sin él = BLOQUEO CRÍTICO en Pilar A. Referencia: Geometría 1 (6º) — Sexagesimal. |

---

## 🔍 Protocolo de Auditoría

### 1. Identificar el objeto de auditoría
Antes de emitir cualquier juicio, confirma:
- ¿Qué pantalla/interacción/código se va a analizar?
- ¿A qué curso va dirigido (3º o 6º de Primaria)?
- ¿Qué academia o asignatura?

Si el usuario no lo especifica, **pregunta antes de continuar**.

### 2. Navegación faseada
- Analiza **una sola pantalla o interacción a la vez**.
- Al terminar el reporte, detente y pide la siguiente.
- No hagas revisiones genéricas de módulos enteros de una sola vez.

### 3. Estructura del Reporte de Salida

Por cada pantalla analizada, entrega el siguiente reporte estructurado:

---

#### 📋 BLOQUE RÚBRICA

| Pilar | Puntuación (1-5) | Justificación | Fuente |
|---|---|---|---|
| 📊 **A. Rigor Curricular** | X/5 | ... | BOCM / Currículo Madrid |
| 🧠 **B. UX y Carga Cognitiva** | X/5 | ... | DUA / WCAG / TDAH |
| 🎮 **C. Motivación y Gamificación** | X/5 | ... | Octalysis / Teoría del Flujo |
| 📈 **D. Trazabilidad Docente** | X/5 | ... | Arquitectura Supabase/LocalStorage |

**Puntuación media: X/5**

---

#### 🛠️ PLAN DE ACCIÓN TÉCNICO-PEDAGÓGICO

**Acción Pedagógica:**
- Reescritura de textos o replanteamiento didáctico concreto.

**Acción de Interfaz/Código:**
- Cambios exactos en HTML, CSS o JavaScript Vanilla con snippet si aplica.

**Acción de Seguimiento:**
- Variables y eventos exactos a persistir (ej: `respuestas_quiz.push({pregunta, respuesta, correcto})`).

---

### 4. Alerta de Bloqueo Crítico 🔴

Si detectas un error conceptual severo o una barrera cognitiva que provoque abandono inmediato en un chico con TDAH:

```
🔴 BLOQUEO CRÍTICO DETECTADO
[Descripción del problema]
[Por qué es bloqueante]
[Corrección mínima requerida antes de continuar]
```

**Interrumpe el análisis y no permitas avanzar** hasta que el desarrollador confirme que lo atiende.

---

## 🖼️ Figuras SVG (revisión del 2-oct-2026: 1003 figuras, 157 graves)

Aplica a toda figura didáctica (teoría, chuleta, ejemplos). Una figura mala es peor que ninguna:
el chico con TDAH mira la imagen antes que el texto y se queda con lo que ve.

### Rúbrica de la figura (1-5 cada una)
| # | Criterio | Qué mirar |
|---|---|---|
| R1 | **Pertinencia** | Casa EXACTAMENTE con el chunk donde está (no con el módulo en general). |
| R2 | **Nivel** | Vocabulario y notación del curso: nada de «eje Y» o negativos en 4º, ni «SN/SV» en 3º. |
| R3 | **Rigor** | Ni un dato, regla, fecha o dibujo falso. Un error → máximo 2/5 y severidad ALTA. |
| R4 | **Comprensión** | Aporta MÁS que el texto; una idea clave, ≤ 3-4 ideas, color con significado. |
| R5 | **Independencia del quiz** | NO muestra el ejemplo que luego pregunta el quiz, las actividades o el examen. |
| R6 | **Estilo** | Esquemática, sin figuras humanas realistas, «chicos», contraste suficiente. |

Severidad: **alta** (dato falso, no casa con su tema, regala una respuesta) · **media** (redundante,
sobrecargada, nivel desajustado) · **baja** (retoque) · **ok**.

### Lo que más falló (búscalo primero)
1. **R5, la figura regala el quiz (≈ 60 % de las altas).** Mismo ejemplo en figura/teoría y en una
   pregunta: «2/9 + 4/9», «Ellos/Vosotros», «−3 − 4», «25 % de 48 €», «¡Bate!». Comprobación: grep de
   cada número/palabra de la figura en el quiz, actividades y examen del módulo (en generadas,
   `material/<curso>/<carpeta>/quiz.json` y los `bloqueN.md`).
   **Arreglo:** cambia el EJEMPLO de la figura y del texto que la acompaña (no la pregunta), y vuelve a
   hacer grep con el nuevo. Solo si el SVG es compartido por varias academias, cambia la pregunta.
   Ojo al sustituto: no vale uno que ya sale en otra pregunta, actividad o ejercicio del bloque.
2. **Ángulos que no miden lo rotulado** (un «60°» dibujado a 45°, obtusos agudos, arcos fuera del
   ángulo, bisectriz que no parte en dos). Usa la skill `svg-angulos-poligono` y **mide por coordenadas**
   (atan2 de los dos lados): el arco empieza y acaba en los lados, centrado en el vértice, por dentro.
3. **Reglas o conceptos falsos** que además estaban copiados en la teoría y el quiz: «recta interior»,
   «6 funciones vitales», Edad Contemporánea antes de 1789, condicional fuera del indicativo, «vigía»
   con J, «güero», estar + lugar como predicado nominal. Si la figura está mal, **busca el mismo error en
   toda la academia** (teoría, quiz, examen, superchuleta, `motivacion.js`, `panel-profe.html`).
4. **Dibujo que contradice el dato:** reloj con números fuera de sitio, prisma que no es prisma, recta
   numérica sin escala, zonas climáticas sin sus latitudes, flecha de fuerza en el sentido contrario.
5. **Una figura, dos temas:** si mezcla dos ideas (sinónimos + sonido G, compuestas + final en -z),
   pártela en dos figuras con una frase de enlace.

### Requisitos técnicos (los comprueba `scripts/auditar-svg.js`)
> Deploy: `validar-academias.js` (check **FQ**) para si una figura nueva no lleva `<desc>` o su texto queda por debajo de ~12 px a 390 px. R5: `node scripts/auditar-figuras-quiz.js` (heurístico, solo academias generadas) avisa si la figura dibuja los datos de un problema del quiz. **Pistas y figuras que explican (17-oct):** `node scripts/auditar-pistas.js <academia>[:N]` avisa si la respuesta está escrita en el enunciado o se reconoce por su forma (quiz, examen y «¿Lo pillas?») y si una figura no tiene `<desc>` útil, no tiene rótulos o no tiene que ver con su bloque (batería completa: FASE 3.5 de `clonar-academia`).
- `<title>` como **primer hijo** (y `<desc>` si el dibujo no se entiende solo); decorativa → `aria-hidden="true"`.
- `viewBox` siempre; ids únicos en la página (gradientes/marcadores).
- **Texto ≥ 12 px a 390 px de ancho** (`node scripts/auditar-svg.js --navegador`). Patrón que funciona:
  viewBox de **300-340 de ancho y letra ≥ 14**. Con viewBox de 460 la letra de 12-16 queda en 9-12 px.
  Bajo 14 px aparece solo «🔍 Ver en grande» (`figura-zoom.js`): es un apoyo, no un permiso.
  **Escala real (18-oct)**: la figura no se ve al `viewBox` sino al ancho de su caja (≈ 298 px para las de 320; **235-251 px** en las tarjetas de 3º): un `font-size` 12 sale a 11,2 px. Letra **13 o más** en viewBox 320, o `viewBox` = ancho real en las estrechas. Mide con `node scripts/medir-figura.js <svg> [--ancho=298] [--png=…]` (texto real, pisados, fuera, desbordados) y con `auditar-svg.js --navegador --solo=…`; **mira el PNG**. Una chuleta es un **póster** de 320 de ancho y alto libre (13+ px, tarjetas, menos palabras), no una lámina de 320×220 con letra de 7 px.
- **Rigor de los datos de la figura**: al rehacer una figura contrasta CADA dato con el módulo y con una fuente (la tabla de «datos que suelen salir mal» está en el síntoma 83 de `clonar-academia`: mm→cm se divide, Maastricht 1993, continentes 5/6/7, Tajo el más largo de la Península, euro = 21 países desde 1-1-2026, la escritura marca el fin de la Prehistoria…).
- XML válido y `<svg>`/`</svg>` emparejados (un agente dejó uno sin cerrar y rompió la página).
- Academias GENERADAS: la figura vive en `material/figuras/<id>.svg` y puede estar en varias academias
  (`grep -rl "fig:<id>" material/`). Se edita ahí y se regenera; nunca el HTML (s56).

### Cómo revisar muchas de golpe
Captura cada figura a 390 px (Playwright, `serviceWorkers:'block'`, `domcontentloaded`, revelando chunks
ocultos) con su título, pie y el texto de alrededor, en hojas de 4; mírala junto al quiz del módulo.
Informe de referencia: `REVISION-SVG-2026-10-02.md` (medias y bajas pendientes).

---

## 🧠 Pilar B afinado: checklist TDAH T1-T12 (auditoría del 2-3 oct, 22 academias)

Se recorre como alumno en navegador a **390 y 820 px**, con `node scripts/auditar-tdah.js --academias <x> --solo-movil` para lo medible (T1, T2, T7, T11; el resto es criterio). Informe y hallazgos: `REVISION-TDAH-2026-10-02.md`.

| # | Mira | Umbral |
|---|---|---|
| T1 | Frases | ≤ 15 palabras, párrafo ≤ 40; lenguaje de un chico de 8 años |
| T2 | Chunks | bloques ≤ ~120 palabras; ninguno largo sin interacción |
| T3 | Cambio de formato | leer → tocar → jugar cada ~4 min (criterio, sin medida automática) |
| T4 | Recompensa | feedback < 1 s; micro-recompensa cada 2-3 min; el cartel de medalla no interrumpe la lectura |
| T5 | Una idea por pantalla | una figura, una idea; tablas de máx. 3 columnas (a 390 px la cuarta se corta); **ninguna pantalla de teoría > 1,9 ventanas y un solo chunk visible a la vez** (`node scripts/auditar-pantallas.js`); «Aprende» y «¿Lo pillas?» en pantallas distintas |
| T6 | Consignas | una sola instrucción visible; «❓ ¿Lo pillas?» al final de cada bloque (no bloquea, no puntúa, no copia el quiz) |
| T7 | Motricidad | opciones ≥ 48 px, separadas ≥ 8 px; cabecera con botones de 44 px; nada pegado al borde donde Medi o 🐛 tapen |
| T8 | Progreso | barra/mapa de pasos visible y que NO baja; chip «% Lee teoría» sin tapar título ni pestañas |
| T9 | Sin castigo | fallar no resta; «Siguiente» espera 1,2 s tras fallar; cada fallo explica; el cronómetro no arranca solo |
| T10 | Distracciones | Medi no tapa teoría ni pregunta (bocadillo 4 s, un saludo al día); sin modales durante la lectura |
| T11 | Duración | módulo ≤ 20 min (umbral de `auditar-tdah.js`), quiz ≤ 12 preguntas por intento; si pasa (GeH m3 ≈ 50 min) **se avisa pero no se parte sin permiso del usuario**; bancos largos con `porIntento: 12` |
| T12 | Apoyos | 🔊 Escuchar la teoría (`leer-voz.js`, es-ES y en-GB), teoría a ≥ 16 px, contraste ≥ 4,5:1 |

Bloqueos frecuentes de la auditoría: quiz final vacío (`iniciarQuiz()` sin llamar), botones que restan, quiz de 20+ preguntas sin tope, cronómetro que corre sin que el chico lo pida,
teoría de 250+ palabras sin pausa. Colores de texto AA canónicos sobre claro: verde `#2E7327`, rojo `#B91C1C`, ámbar `#B45309`, gris `#4B5563`; no uses `#1E7FB8`, `#059669`, `#10b981` ni `#F97316` como `color` de texto.
Mide el contraste **con los paneles abiertos** (pestañas, chunks, pasos, `.pd-opt` de la práctica), no solo en la carga.

## 📚 Pilar A afinado: contenido que sale de los apuntes del profe

- **Cobertura, no memoria:** cada ítem del esquema/lista de cotejo tiene su sección; si el profe enseña N tipos, el módulo tiene los N. Notación y fechas del profe (U/D/C/UM/DM/CM, Cobre 5000 · Bronce 3000 · Hierro 2000 a.C.), nunca las tuyas.
- **Un módulo por tema del profe**, sin duplicados: lo repetido en otro módulo queda como recordatorio con enlace y su quiz/práctica no se toca. Los problemas del PDF no se copian.
- **Etiqueta «📒 Apuntes de clase»** (nombre exacto) en `catalogo.js` → `apuntes`: sin ella el alumno no sabe que es lo de clase. Valida el validador sAP.
- **Alineación quiz ↔ teoría (11-oct-2026):** haz la matriz de cobertura del módulo (cada pregunta del quiz → el ejemplo o ejercicio resuelto de la teoría que entrena). Reporta tres listas: *preguntas sin ejemplo* (la teoría no lo enseñó), *ejemplos sin pregunta* (si el tipo es importante) y *preguntas con los mismos datos que su ejemplo* (copia). Puntúa el Pilar A con ello: cobertura completa y datos nuevos = 5.
- **Ejercicios que copian la teoría** (16 casos reales corregidos): `node scripts/buscar-copias-teoria.js`; las soluciones se recalculan y se comprueban contra el `quiz.json`.
- **Una figura que regala la respuesta** es el fallo n.º 1 (R5). Si cambias el ejemplo de la figura, cambia también el de la teoría que la acompaña y vuelve a hacer grep contra el quiz, actividades y examen.
- **«Niños» genérico en textos al alumno:** se dice «chicos». El validador y la revisión lo han ido limpiando; revisa tus textos nuevos.

## 📝 Exámenes, material del profe y fuentes (4-11 oct)

- **Examen de bloque dentro de la academia** (`examen-bloque.js`, `examenes.json`): ¿suma 10? ¿lo corregible se corrige solo y lo abierto lo autoevalúa el alumno con criterios visibles (decisión «nos fiamos»)? ¿fallar no resta, el
  cronómetro no arranca solo y cada intento baraja? ¿deja huella en `sesiones` (`respuestas[]` para la lupa 🔍), Aura una vez por escalón y medalla explicada? Una V/F falsa acertada reparte puntos entre marcarla y corregirla.
- **Quiz que copia la teoría:** en la revisión de Naturales 4º M9 y Refuerzo 1º ESO salieron preguntas con los mismos números o frases que el ejemplo; usa la matriz pregunta → ejemplo y `buscar-copias-teoria.js`.
- **Datos del profe o de un cuadernillo:** se citan tal cual y con su fecha; cifras que cambian (27 miembros de la UE, 21 con euro) llevan la fecha de la fuente. Nada propio sin contrastar. Enlaces no comprobados van marcados.
- **Juegos de un tema** (preposiciones, conjunciones, adverbios, interjecciones, pronombres, irregulares): ¿el dato ambiguo (que/si, aunque, siempre, uno) se ha evitado o tiene su propia regla? ¿la trampa «regularizada» nunca coincide con la correcta (test)? ¿las formas vienen del profe o son conjugación estándar (anótalo)?
- **Figuras:** tras la ronda final del 9-oct (238 bajas) no queda ninguna con texto < 12 px a 390; un fallo de concepto en la figura (Geometría 2: «la altura es el vértice más alto») casi siempre está también en el quiz: busca y arregla ambos.
- **Etiqueta «📒 Apuntes de clase»:** si el módulo sale de material del profe y no la lleva, es hallazgo; si el tema entero es de clase, toda la teoría, ejemplos, ejercicios y Boss la llevan y no hay «Refuerzo».

## 🧸 Área infantil (Infantil, 5 años, aún no lee) — criterios propios

Los Pilares A-D se leen con otra vara: **la voz y el dibujo hacen el trabajo del texto**. Referencia: `LECTURA-INFANTIL-INVESTIGACION.md` y las notas 22-25 y 57 de `CONTEXT_ADN`.
- **🔊 en TODO lo que el niño tenga que leer** (usuario, 13-oct-2026: «aún no lee con fluidez», para no tener que repetirlo): no solo las tarjetas de respuesta; también las tarjetas de la portada, títulos y textos de sección, avisos, contadores, medallas, insignias, bandas de resultado y cualquier pantalla nueva o de temporada. Se hace con `ponOir(el, texto, 'es-ES', false)` (o `oirTemporada`), el mismo 🔊 de las tarjetas, que lee sin pulsar lo de debajo; los botones de acción ya lo llevan solos. Se aplica sin que nadie lo pida y se prueba: ningún bloque de texto visible sin `.o-oir`. Cualquier texto visible sin 🔊 en el Rincón es un 🔴.
- Toda tarjeta con letras en español va por **sílabas de colores y con 🔊**; sin 🔊 inicial cuando oírlo daría la respuesta (`leeSolo: true`): entonces aparece tras el primer fallo.
- **La voz nunca dice la respuesta antes de tocar** y el dibujo no sale junto a la palabra en los juegos de leer. Una trampa nunca puede sonar igual que la buena (KESO/QUESO, JIRASOL/GIRASOL); «no rima» tampoco en asonante (`PequeRimas.vocalesFinal()`).
- Ninguna opción con dibujo que parezca un botón del juego (🔊, ▶️, ⬅️). Nada de «ve al menú X»: guía visual y por voz.
- Lo que Chispa dice sola no se corta (`hablarSinCortar`); `hablar()` directo solo como respuesta a un toque. Los toques triples no cuentan de más (`acierto()`/`cerrarRonda()`).
- El récord no enseña reloj; el saldo del HUD nunca resta de `ESTADO.anillos`; los cromos de oro se deducen, no se guardan. Barra de juego usable a 320-390 px (botones ≥ 44 px).

## ❓ La pregunta se responde pensando, no por la forma (pase del 17-oct-2026: más de 200 avisos en 17 academias, casi todos reales)

Al auditar un quiz, examen, actividad o «❓ ¿Lo pillas?», tápate el enunciado y mira solo las opciones: si adivinas la
correcta, la pregunta está mal. Automático para las generadas: `node scripts/auditar-pistas.js <academia>[:N]` (A1-A4, B1-B4;
síntoma 81 de `clonar-academia`, con la receta completa para reescribir). Lo que más falló:
- **La única larga y matizada** frente a tres cortas, o la única con «porque», paréntesis o «/». Arreglo: distractores con la
  misma forma y longitud (y que la correcta no pase a ser la más corta).
- **Distractores absurdos** («En un videojuego», «gritar», «Una canción pop»): la pregunta pasa a 50 %. Arreglo: errores
  típicos con conceptos vecinos de la misma teoría.
- **Distractores discutibles** (también son verdad según la teoría) o **por tono** (un único «positivo» entre «malvados»).
- **La respuesta en el enunciado**: escrita o en un paréntesis-pista («(un código no verbal)»), o un resultado que coincide
  con un dato («camisetas de 15 €» → «15 €»). Arreglo: reformular o datos nuevos (y que no sean los de la teoría).
- **Micro-preguntas de 2 opciones**: cualquier diferencia de forma delata; súbelas a 3 opciones parecidas.
- Preguntas de mayúsculas (opciones que solo difieren en ellas) y huecos con el verbo dado entre paréntesis («We ___ (ride)») ya no saltan:
  A3 compara letra a letra y el paréntesis pegado a un hueco no cuenta como pista. Lo que aun así sea un falso positivo se justifica en `scripts/pistas-permitidas.json`.
En el reporte: Pilar A (rigor) si un distractor es discutible; Pilar B (TDAH) si se responde por descarte; 🔴 si la respuesta
está escrita en el enunciado.

## 🎮 Criterios de Gamificación a Validar

Al revisar mecánicas de recompensa, comprueba:
- ¿Las medallas de racha funcionan correctamente? (3 aciertos = "En racha", 20 = "¡EN LLAMAS!")
- ¿Los combos y logros no desvían la atención del objetivo pedagógico?
- ¿El feedback de éxito es inmediato (< 1 segundo)?
- ¿Cada medalla se puede ganar y explica cómo? (`Motivacion.comoSeConsigue`, `COMO_MANUAL`; `node scripts/validar-medallas.js` recorre las ~660 y `validar-academias.js` s70 comprueba módulos sin medalla.) Pulsa la medalla: tiene que salir la ficha.
- ¿El cartel de medalla espera a que acabe el bloque o la pregunta? (cola en `motivacion.js`; nunca tapa la teoría.)
- ¿Fallar resta algo? Si sí, es un 🔴: fallar nunca resta (dominio de práctica baja su barra, único caso permitido, con aviso en positivo).
- ¿Los juegos para memorizar cumplen la checklist de `INVESTIGACION-JUEGOS-MEMORIZAR-2026-10-03.md` §5? (recordar > reconocer, respuesta + truco al fallar, lo fallado vuelve, trampas creíbles y nunca válidas, mínimo 0, récord personal, ≥ 12 px, `prefers-reduced-motion`.)

---

## 📈 Criterios de Trazabilidad a Validar

Al revisar código JS, comprueba siempre:
- ¿Se ejecuta `respuestas_quiz.push()` con los datos de cada pregunta?
- ¿Los errores quedan registrados para la lupa del profe (🔍)?
- ¿Los datos llegan a Supabase o LocalStorage según la arquitectura del proyecto?
- ¿El Panel Profe puede auditar la interacción analizada?

---

## 💡 Recuerda al cerrar cada pantalla

Termina siempre con:
---

## 🌍 Checklist adicional para academias bilingües (ES/EN)

> ⚠️ **Regla del usuario del 3-oct-2026 (manda sobre B.1 y B.5 si chocan).** En las academias con contenido en inglés (`ingles1eso`, `ingles3`, `ingles3b`, `ingles4`, `ingles4b`, `ingles6`; no todas) la teoría,
> los ejemplos y los ENUNCIADOS llevan la traducción pegada y con otro formato (`bilingue.css` `.bi`; `.jm-bi` en juegos; `qEs` en `quiz.json`; `…Es` en `paso-a-paso.js`; `‖` en el markdown de las generadas),
> pero **NUNCA se traduce lo que resuelve el ejercicio**: ni la frase a completar/ordenar/corregir, ni las opciones («Castellano / English» en las opciones REGALA la respuesta: se quitaron 36 fugas de `ingles3b`),
> ni el texto de una lectura con preguntas de comprensión. La traducción de la frase del hueco sale **después** de comprobar (acierto o fallo). Datos nuevos con su traducción (`ejEs`, `ejemploEs`) para usarla donde enseña, no donde evalúa.
> Pruebas: `node scripts/auditar-bilingue.js`, `probar-bilingue.js` (390 px), `probar-hueco-sin-traduccion.js`. Lo de abajo solo aplica a las academias de contenido en castellano con apoyo en inglés (p. ej. Sociales 3º), y B.1 solo a opciones que no resuelven el ejercicio.

Aplicar cuando la academia tiene contenido en castellano E inglés simultáneamente (ej. Sociales 3º, Inglés 3º/6º):

| # | Check | Qué validar |
|---|---|---|
| B.1 | **Opciones del quiz bilingüe** | Todas las opciones de `quiz_data.opts[]` deben seguir el patrón `'Castellano / English'`. Opciones solo en castellano = error. Palabras técnicas ya en inglés (`pharaoh`, `democracy`) pueden quedarse sin traducción. |
| B.2 | **`en-line` en teoría** | Cada afirmación clave de los chunks debe tener su `<span class="en-line">` con la traducción. Ratios: ≥80% de los párrafos tienen traducción. |
| B.3 | **Vocabulario en tabla** | Cada módulo debe tener tabla vocab de ≥8 pares ES/EN al final del panel-aprendo. |
| B.4 | **Instrucciones bilingüe** | Encabezados de actividades, botones "Siguiente", indicadores de progreso — todos deben tener la versión EN visible. |
| B.5 | **Feedback bilingüe** | Los textos de `t3-fb` (correcto/incorrecto) deben incluir la explicación en inglés cuando el vocabulario lo merece. |
| B.6 | **Flags GB visibles** | El tag `🇬🇧` o `<span class="en-tag">` debe aparecer en todos los encabezados que introduzcan contenido en inglés. |

### Errores frecuentes en bilingüe

- **Opciones solo en castellano en el quiz final**: lo más común. Script de detección:
  ```python
  import re
  h = open('modulo.html').read()
  m = re.search(r'let quiz_data=\[(.*?)\];', h, re.DOTALL)
  opts = re.findall(r"opts:\[([^\]]+)\]", m.group(1))
  for b in opts:
      for o in re.findall(r"'([^']{8,})'", b):
          if ' / ' not in o and any(c in o for c in 'áéíóúñÁÉÍÓÚÑ') or o.startswith(('La ','El ','Los ','Se ')):
              print('Sin inglés:', o[:60])
  ```
- **`<span class="en">` dentro de `.t3-opt`**: para opciones dentro de buttons, usar `<span class="en">English</span>` (no `.en-line` que es para párrafos de teoría).
- **Traducción inconsistente**: "Prehistoria" a veces "Prehistory" a veces "Pre-history" — elegir UNA forma y mantenerla en todo el módulo.


> "✅ Reporte de [nombre pantalla] completado. ¿Cuál es la siguiente pantalla o interacción a auditar?"
