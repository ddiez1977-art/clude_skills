---
name: sistema-cognitivo
description: "Orquestador de las 5 skills cognitivas transversales: estructurador-mece, pragmatismo-esfuerzo, wording-ejecutivo, presentacion-de-datos y transmision-del-mensaje. Actívala SIEMPRE que el usuario arranque cualquier entregable con cierta complejidad: app, análisis, presentación, documento, conclusiones, email, modelo, propuesta, reunión. También con: 'aplica el sistema', 'qué skills activo', 'ayúdame a pensar esto', '/sistema', '/cognitivo', o cuando detectes que el output se beneficiaría de más de una skill. Pregunta al usuario cuáles activar, aplica todas, o elige un mix razonado según el tipo de entregable. Nunca activa las 5 por defecto sin calibrar — el pragmatismo también aplica al propio sistema."
---

# Sistema Cognitivo — Orquestador

Skill maestra que agrupa y orquesta las 5 skills cognitivas transversales. Actúa como punto de entrada único: evalúa el tipo de entregable, pregunta qué skills activar, y aplica el mix adecuado.

## Las 5 skills del sistema

| ID | Skill | Qué resuelve | Cuándo es clave |
|---|---|---|---|
| **M** | `estructurador-mece` | Marco antes de producir | Arrancar cualquier entregable complejo |
| **P** | `pragmatismo-esfuerzo` | Nivel de detalle justo | Riesgo de sobreingeniería o sobresfuerzo |
| **W** | `wording-ejecutivo` | Texto preciso y directo | Cualquier texto que otra persona va a leer |
| **D** | `presentacion-de-datos` | Números con conclusión | Análisis, dashboards, modelos, KPIs |
| **T** | `transmision-del-mensaje` | Mensaje calibrado al receptor | Audiencia concreta, resistencia previsible |

---

## Protocolo de activación

### PASO 1 — Leer el entregable

Identificar internamente qué tipo de output se va a producir y marcar qué skills son relevantes:

```
¿Hay estructura que definir?       → M (siempre en entregables complejos)
¿Hay riesgo de sobresfuerzo?       → P
¿Hay texto que alguien va a leer?  → W
¿Hay datos o cifras?               → D
¿Hay una audiencia concreta?       → T
```

### PASO 2 — Proponer el mix y preguntar

Presentar al usuario la propuesta de mix con una sola intervención:

```
Para [tipo de entregable] propongo activar:

  ✅ M — estructurador-mece       [razón en una línea]
  ✅ P — pragmatismo-esfuerzo     [razón en una línea]
  ✅ W — wording-ejecutivo        [razón en una línea]
  ⬜ D — presentacion-de-datos    [por qué no aplica o es opcional]
  ✅ T — transmision-del-mensaje  [razón en una línea]

¿Aplico este mix, ajustas alguna, o activo todas?
```

Opciones que puede elegir el usuario:
- **"Aplica"** → ejecutar el mix propuesto
- **"Todas"** → activar las 5 sin excepción
- **"Solo M y W"** (o cualquier combinación) → aplicar solo las mencionadas
- **"Tú decides"** → aplicar el mix razonado sin más preguntas

### PASO 3 — Ejecutar en orden

Las skills activas se aplican en este orden fijo (el orden importa — cada una alimenta a la siguiente):

```
1. M → estructura el marco
2. P → calibra el nivel de detalle de cada bloque
3. W → redacta con precisión
4. D → presenta los números con conclusión
5. T → calibra al receptor concreto
```

No saltar pasos. Si una skill no aplica, se omite en silencio — no se menciona.

---

## Mixes recomendados por tipo de entregable

Estos son los mixes de referencia. El orquestador los propone como punto de partida y el usuario puede ajustar:

### App / código
```
✅ M — arquitectura de módulos antes de escribir código
✅ P — nivel justo: borrador / funcional / producción
✅ W — naming, comentarios y documentación precisos
⬜ D — solo si hay outputs de datos o dashboards
⬜ T — solo si hay que presentar la solución a alguien
```

### Análisis / modelo
```
✅ M — pregunta central + bloques MECE antes de calcular
✅ P — precisión calibrada a la decisión (orden de magnitud vs. exacto)
✅ W — conclusiones directas, sin relleno
✅ D — datos con referencia, formato correcto, conclusión visible
⬜ T — solo si el análisis va a una audiencia específica
```

### Presentación / slides
```
✅ M — storyline con títulos-mensaje antes de diseñar
✅ P — número de slides justo para la audiencia
✅ W — títulos-conclusión, bullets de una línea
⬜ D — solo si hay slides de datos
✅ T — orden narrativo y objeciones anticipadas según la audiencia
```

### Documento / informe
```
✅ M — índice MECE antes de redactar
✅ P — extensión calibrada a quién lo lee y para qué
✅ W — redacción ejecutiva, conclusión primero
⬜ D — solo si hay secciones de datos
⬜ T — solo si el documento va a una audiencia con sensibilidades específicas
```

### Email / mensaje
```
⬜ M — solo si el email es muy complejo o tiene partes diferenciadas
✅ P — longitud justa: si necesita más de 4 párrafos, es una reunión
✅ W — asunto-mensaje, primera línea al grano, cierre con acción
⬜ D — solo si hay cifras relevantes
✅ T — receptor mapeado, orden narrativo elegido, objeciones anticipadas
```

### Conclusiones / recomendación
```
✅ M — estructura de la argumentación antes de escribir
⬜ P — generalmente ya se sabe el nivel requerido
✅ W — conclusión primero, evidencia después, sin relleno
✅ D — el dato que sostiene cada conclusión
✅ T — calibrado a quién toma la decisión
```

---

## FASE FINAL — Informe consolidado del sistema

Al final del output, un único bloque que consolida los informes de todas las skills activas:

```
---
🧠 INFORME DEL SISTEMA COGNITIVO
¿Aplica? El usuario decide si leerlo o ignorarlo.

Skills activadas: [M] [P] [W] [D] [T]

📐 Estructura (M):
   — Marco aplicado: [nombre del patrón]
   — MECE: [verificado / con salvedades]

⚖️ Esfuerzo (P):
   — Nivel aplicado: [borrador / funcional / producción]
   — Lo que se dejó fuera: [lista]

✍️ Wording (W):
   — Audiencia: [quién / tono]
   — Decisiones de estilo: [si las hay]

📊 Datos (D):
   — Conclusión presentada: [sí / no aplica]
   — Formato elegido: [tipo y por qué]

📡 Transmisión (T):
   — Receptor: [perfil]
   — Orden narrativo: [directo / narrativo / resistencia]
   — Objeciones anticipadas: [lista]

⚠️ Riesgos globales detectados: [lo que podría fallar en este output]
💡 Para la próxima iteración: [si hay algo que ajustar]
---
```

Solo se muestran las secciones de las skills que se activaron. Las que no aplican no aparecen.

---

## Atajo rápido

El usuario puede invocar el sistema con:
- `/sistema` → activa el orquestador con la pregunta de mix
- `/todas` → activa las 5 skills sin preguntar
- `/mix M W T` (o cualquier combinación de letras) → activa solo las indicadas sin preguntar

---

## Antipatrón principal a evitar

**Activar las 5 skills siempre por defecto.** El pragmatismo aplica también al sistema: un email corto no necesita estructura MECE ni presentación de datos. El orquestador existe precisamente para elegir el mix mínimo que resuelve el entregable — no para añadir capas innecesarias.

---

---

## Calibración para el proyecto JoGaSan Academy

El pragmatismo manda también aquí; estos son los mixes que han funcionado y las reglas del usuario que cambian el informe final:

| Entregable | Mix mínimo | Nota |
|---|---|---|
| Módulo / quiz / juego / motor | **P** + **M** | Antes de escribir: PR abiertas y `COORDINACION.md` (evita duplicar), y la skill del proyecto que toque (`clonar-academia`, `auditoria-pedagogica-jogasan`, `/ux`). |
| Auditoría con cifras | **D** + **W** | «606 → 280 px», «63 → 7 fallos»: antes/después contra `main`, no impresiones. |
| Informe o delta para la familia / el profe | **W** + **T** | Qué ha cambiado, qué hace falta de ellos, sin jerga. |
| Documentación (`CONTEXT_ADN`, guías) | **M** + **W** | Con `documentador-contexto-proyecto`: delta breve y detalle en guía aparte. |

- **Regla del usuario (24-sep): skills + pruebas antes de subir.** El informe consolidado cierra con tres líneas fijas: *skills usadas*, *pruebas que pasaron* y *lo que no se pudo probar* (voz real, producción, Supabase real).
- **Decisiones del usuario no se re-litigan** (GeH m3 no se parte; inglés bilingüe solo donde hay inglés; Modo proyector retirado): consúltalas en `CLAUDE.md` y `CONTEXT_ADN` antes de proponer lo contrario.
- **Si dudas entre dos caminos, da una recomendación**, no un listado de opciones.
## Descriptores detallados por skill

Esta sección contiene los descriptores de comportamiento extraídos de la rúbrica de desarrollo profesional. Úsalos para calibrar el nivel de aplicación de cada skill y para dar feedback concreto al usuario sobre el nivel en que está operando.

Los niveles son: **inicio** (KPI 1) · **junior** (KPI 2) · **senior** (KPI 3).

---

### [M] estructurador-mece — Gestión del proyecto

#### Planificación
- **inicio:** Entiende las prioridades y actúa en consecuencia; gestiona expectativas y alerta de desviaciones.
- **junior:** Plantea prioridades y propone agenda de desarrollo. Preciso en los tiempos de entrega. Se adapta a los cambios de prioridades de forma adecuada.
- **senior:** Entiende y hace challenge a las prioridades del proyecto. Desarrolla proactivamente sus prioridades de manera alineada. Propone balanceamiento dentro del equipo en pos de un mejor resultado del proyecto en su conjunto, incluso apalancando recursos externos. Gestiona expectativas y alerta de desviaciones, también en entregables grandes y de temáticas variadas. Aporta transparencia sobre dónde está y sus siguientes pasos también a sus compañeros.

#### Insight
- **inicio:** Entiende los objetivos y mensajes y los defiende.
- **junior:** Extrae conclusiones, hace challenge e identifica gaps. Propone elementos adicionales de desarrollo de contenidos.
- **senior:** Hace push back a los mensajes y conclusiones, a las prioridades y a la forma de llevarlo a cabo. Identifica problemas de manera temprana (e.g. mensajes potencialmente conflictivos, alerta al encontrar elementos que afectan a las hipótesis iniciales, alerta de elementos que requieren excesivo esfuerzo para el valor añadido). Añade mensajes y conclusiones de manera autónoma y recurrente.

#### Estructuración
- **inicio:** Sabe interpretar el nivel de detalle vs. generalidad entre diferentes ideas. Entiende marcos de trabajo / ideas y sabe desenvolverse dentro del marco.
- **junior:** Propone cambios sobre el marco de trabajo / ideas, hace push back correcto, incluso de modificaciones relevantes; todo lo que propone cumple con MECE.
- **senior:** Genera de forma autónoma marcos de trabajo / ideas y es capaz de modificarlo durante el proyecto si aplica.

#### Research
- **inicio:** Identificación de información básica, utilizando fuentes estándar (e.g. búsquedas web, asociaciones del sector…).
- **junior:** Apalanca fuentes de información adicionales (herramientas internas, conocidos, suscripciones a título personal…). Interpreta de forma correcta la información encontrada, con claridad en lo que abarca y lo que no, y el nivel de precisión.
- **senior:** Siempre encuentra lo que necesita, y también información complementaria que aporta al objetivo. Creativo en cómo utilizar la información disponible para lograr el objetivo.

#### Conocimiento
- **inicio:** Cubre los conocimientos necesarios para el contenido del proyecto.
- **junior:** Es un reconocido experto en los contenidos del proyecto.
- **senior:** Tras cualquier proyecto, se vuelve el máximo experto en el tema.

#### Fiabilidad (ejecución)
- **inicio:** Escucha activa a los comentarios del responsable, entiende los comentarios, y sale de la discusión sabiendo lo que debe hacer. No reabre discusiones cerradas en foros más elevados.
- **junior:** Los cambios y comentarios los incluye normalmente a la primera, y siempre a la segunda. Atención al detalle: las actualizaciones se aplican en todas las partes afectadas, los números son coherentes a lo largo del documento.
- **senior:** Discrimina los comentarios de mayor relevancia y los ejecuta primero. Tras la discusión, es crítico al llevar a cabo los comentarios, pudiendo plantear alternativas. Se acuerda de traer las discusiones que eran necesarias en los foros correspondientes.

---

### [P] pragmatismo-esfuerzo

#### Pragmatismo
- **inicio:** Se asegura de entender el nivel de detalle requerido, contrasta múltiples veces si es necesario, evitando sobresfuerzos innecesarios.
- **junior:** Reflexiona sobre el mejor planteamiento, encuentra soluciones sencillas para resolver el punto y/o comunicar el mensaje. Busca ayuda (intraequipo y fuera) para adecuar el planteamiento.
- **senior:** Resuelve de forma pragmática en documentación / análisis / modelos de detalle, teniendo claro el impacto en el resultado final para ajustar el esfuerzo y la precisión requerida. Para ello, interacciona con la organización en los momentos adecuados y recalibra.

#### Concentración
- **inicio:** Mantiene el control en situaciones de estrés y aumenta su capacidad de producción.
- **junior:** Gestiona el nivel de intensidad acorde a las necesidades específicas de cada momento.
- **senior:** Mantiene un elevado nivel de concentración durante todas las fases del proyecto, con un ritmo de entrega similar también en fases de valle. Adapta su ritmo y forma de comunicarse al nivel de ocupación e intensidad de sus interlocutores.

#### Creatividad
- **inicio:** Abierto a ideas diferentes; habla de lo positivo igual o más que de las dificultades; contribuye a buscar soluciones.
- **junior:** Nunca descarta de primeras una propuesta ajena. Extrae los puntos fuertes de las ideas ajenas y elabora sobre estas; se apalanca en experiencias pasadas.
- **senior:** Propone nuevas ideas de manera recurrente en todas las fases: diagnóstico (¿por qué pasa?), solución y metodología. Utiliza cambios de perspectiva, eliminación de restricciones y apertura de frameworks (think in NEW boxes) de forma habitual y natural. Provoca los cambios de perspectiva y eliminación de restricciones en otros.

---

### [W] wording-ejecutivo — Comunicación escrita

#### Diseño y contenido
- **inicio:** Realiza documentación correcta en lenguaje y visual recibiendo guía. Errores poco frecuentes / atención al detalle.
- **junior:** Desarrolla documentación de manera ágil y de forma independiente. Propone diseños alternativos y disruptivos de manera ocasional que facilitan el entendimiento del mensaje. Anota e incluso ajusta en tiempo real los comentarios de cambios concretos que recibe.
- **senior:** Desarrollo y diseño de documentación de alta calidad, consistentes y originales. Mensajes claros, correctos y precisos, tanto explícitos como implícitos. Anota y/o ajusta en tiempo real, además de los comentarios de cambios concretos, cambios que resuelven las problemáticas que se plantean.

#### Wording
- **inicio:** Frases sencillas, se entienden al leerlas.
- **junior:** Frases suficientemente cortas, lenguaje sencillo.
- **senior:** Frases que explican el mensaje y nada más, en el nivel adecuado de formalidad vs. informalidad y de concreto vs. general. Optimiza el número de caracteres.

#### Gestión de expectativas (escrita)
- **inicio:** Gestiona expectativas de tiempos de entrega y alerta de desviaciones, en entregables pequeños.
- **junior:** Preciso en los tiempos de entrega.
- **senior:** Gestiona expectativas y alerta de desviaciones, también en entregables grandes y de temáticas variadas.

#### Storyline
- **inicio:** Ordena las diapositivas de manera correcta.
- **junior:** Completa títulos con mensaje explicativo y los mensajes están claros.
- **senior:** Propone la estructura de la historia; además realiza cambios y detecta potenciales riesgos.

---

### [D] presentacion-de-datos — Analítica

#### Sensibilidad a resultados
- **inicio:** Controla el orden de magnitud. Identifica desviaciones relevantes de lo razonable.
- **junior:** Entiende el nivel de incertidumbre que no afecta a la decisión a tomar y gestiona los esfuerzos de manera acorde. Siempre double-check. Identifica y entiende las hipótesis más sensibles y las principales fuentes de incertidumbre.
- **senior:** Entiende y explica la sensibilidad de las hipótesis e identifica mecanismos de mitigación. Adelanta los impactos esperados a nuevas hipótesis o variaciones de las existentes. Plantea vías alternativas o adicionales que simplifican la toma de decisión.

#### Capacidad deductiva — Manejo de grandes cifras
- **inicio:** Sigue la lógica de cálculo cuando se discute.
- **junior:** Hace cálculos de servilleta con facilidad: identifica qué hipótesis usar de las que tenga alguna forma de aproximarlas, son cálculos simples, cortos y evitando incluir detalles que afectan poco a la conclusión. Saca conclusiones de los resultados y los expresa proactivamente.
- **senior:** Hace cálculos de servilleta en tiempo real, controla múltiples cifras de negocio y de la operativa para poder sacar prácticamente cualquier aproximación que surge durante un proyecto. Siempre saca conclusiones, tanto de los inputs como resultados intermedios y finales, y las comenta proactivamente cuando aplica.

#### Modelización — Alineamiento de la respuesta
- **inicio:** El modelo responde a las preguntas.
- **junior:** Identifica las principales necesidades de información de manera temprana. La salida del modelo está en la estructura en que se cuenta. Las principales entradas del modelo están en la estructura en las que se discuten.
- **senior:** Identifica las necesidades de información y de hipótesis al principio y reacciona de manera ágil cuando identifica nuevas necesidades. Controla la información ya disponible y los riesgos de la faltante. El modelo está estructurado como se explica y discute. La complejidad de los cálculos está alineada con el nivel de precisión requerida para el output.

#### Modelización — Fiabilidad
- **inicio:** Los resultados son creíbles, y se explican los principales bloques.
- **junior:** El modelo es poco sensible a los parámetros e hipótesis de construcción. Hay controles básicos para la calidad de los inputs. Las hipótesis y las fuentes de impacto están claramente identificadas y diferenciadas. Los cálculos y los impactos de las hipótesis son fácilmente trazables. Los principales cálculos tienen controles de formulación.
- **senior:** Todos los cortes se realizan de forma sencilla y rápida garantizando coherencia. Identifica inputs que no tienen sentido, tanto de manera manual como con controles. Sencilla comprobación del impacto de diferentes escenarios de hipótesis. Múltiples controles que aseguran la correcta formulación. La formulación guarda un equilibrio entre sencillez y operatividad.

#### Modelización — Facilidad de entender
- **inicio:** Ordenado, y explicado en la medida adecuada, especialmente los parámetros e hipótesis.
- **junior:** Flujo de información lógico y modular, tanto a nivel hoja como de pestañas. Todos los inputs, cálculos y resultados están en el sitio que les corresponde. Los resultados finales están limpios y según se van a presentar.
- **senior:** Homogéneo y coherente: se mantienen los criterios de colores, numeración de conceptos, estructura de tablas, etc. Formato visual que facilita la navegación. Un usuario no avanzado puede manejarlo con manipular la sección que necesita.

---

### [T] transmision-del-mensaje — Comunicación verbal y no verbal

#### Participación
- **inicio:** Participa en reuniones, con comentarios correctos y que ocasionalmente resuelven puntos relevantes.
- **junior:** Presencia en las reuniones, participando de forma natural en momentos adecuados (no impulsivo), siendo una referencia en las discusiones, sin tapar o acallar otras voces.
- **senior:** Lidera determinadas reuniones y es partícipe activo en las que debe serlo. Gestiona el humor y el equilibrio adecuado entre formalidad e informalidad (incluyendo el léxico empleado).

#### Transmisión del mensaje
- **inicio:** Explica y defiende sus secciones de forma clara y adecuada; termina las frases.
- **junior:** Explica el marco (scope / framework) antes que el contenido. Más allá de la explicación, transmite los mensajes clave, de forma priorizada, tanto de sus secciones como del resto del alcance del proyecto. La argumentación se basa en razonamientos lógicos y en hechos y números reales.
- **senior:** Transmite los mensajes clave adaptados a su interlocutor, manejando sensibilidades y asuntos de preocupación. Busca la tipología de comunicación más adecuada a cada persona y momento (visual, emocional, auditiva, discursivo), apalancando el medio de comunicación más adecuado (diapositiva, Word, sin soporte, llamada, con un café...).

#### Voz
- **inicio:** Voz clara, a volumen y velocidad razonable y firme mostrando confianza; sin pérdidas de volumen a final de frases.
- **junior:** Ajusta el ritmo (incluyendo pausas), tono y volumen de voz de manera regular; muletillas poco frecuentes.
- **senior:** Voz dinámica, empática y pasional, con cambios de ritmo y uso de pausas, tono y volumen continuo que ayudan a enfatizar los mensajes clave.

#### Escucha activa
- **inicio:** Entiende las discusiones de poca audiencia y es capaz de extraer los mensajes y conclusiones relevantes.
- **junior:** Escucha activa, construyendo sobre los mensajes del resto de interlocutores y extrayendo las conclusiones relevantes, tanto con poca audiencia como en sesiones de elevado número de interlocutores.
- **senior:** Escucha activa y entre líneas; entiende e interpreta agendas y contextos; considera comentarios y gestos en su debido contexto; tanto en sesiones con poca audiencia como con elevado número de interlocutores.

#### Gesticulación en escucha
- **inicio:** Se percibe como presente y atento a la conversación.
- **junior:** Se percibe naturalidad, mantiene contacto visual adecuado, recto pero no rígido.
- **senior:** Utiliza la gesticulación para derivar la conversación (gestionar emociones, interrumpir para participar, dar la palabra a otro) de forma natural, usando recursos gestuales: contacto visual ajustado y variado, reflejo y guía postural.

#### Gesticulación en habla
- **inicio:** Suficiente movilidad para mostrar interés y carece de movimientos raros o excesivos que restan credibilidad / seniority.
- **junior:** Acompaña su discurso con gestos acordes, gestiona la mirada a los interlocutores, y evita en todo momento muletillas gestuales (e.g. cruzar brazos, codos...).
- **senior:** Atrae la atención a su discurso usando recursos gestuales: contacto visual ajustado y variado, reflejo y guía postural, variando incluso la tipología de comunicación (visual, emocional, auditiva, discursivo).

#### Gestión del entorno
- **inicio:** Identifica condiciones básicas de entorno: recursos disponibles, la propia posición.
- **junior:** Gestiona el espacio a su alrededor y se desplaza a conveniencia; maneja proactivamente la ubicación de los participantes.

---

### Cómo usar los descriptores

Cuando apliques una skill, úsalos para:
1. **Calibrar el nivel de output** — produce a nivel junior por defecto; sube a senior si el contexto lo requiere o el usuario lo pide.
2. **Dar feedback específico** — si el usuario pide revisión de un texto o presentación, cita el descriptor concreto que no se cumple.
3. **Autoevaluar el propio output** — antes de entregar, contrasta contra los descriptores senior de las skills activas.

---

## Relación entre skills (para referencia interna)

```
Entregable nuevo
      │
      ▼
  [M] Estructura el marco (siempre primero si aplica)
      │
      ▼
  [P] Calibra el nivel de cada bloque (antes de producir)
      │
      ▼
  [W] Redacta con precisión (cualquier texto de salida)
      │
      ▼
  [D] Presenta los datos con conclusión (si hay cifras)
      │
      ▼
  [T] Calibra al receptor concreto (si hay audiencia definida)
      │
      ▼
  Output final + Informe consolidado del sistema
```
