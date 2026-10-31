# Skills del equipo

Índice por categoría. Se genera con `python3 scripts/skills.py indice`: no lo edites a mano.
Cada skill vive en su carpeta `skills/<nombre>/` (plana, para que Claude Code la cargue).
Las marcadas **solo si la invocas** no se activan solas: hay que pedirlas por su nombre.

## Diseño y marca

### frontend-design

Guía para diseñar interfaces con intención visual propia, sin el aspecto genérico de plantilla. Úsala al crear una interfaz nueva o rediseñar una existente: define dirección estética, tipografía, color y composición. Ejemplo: «rediseña esta landing con un estilo distintivo».

### ui-ux-pro-max

Inteligencia de diseño UI/UX para web, móvil y escritorio. Úsala al diseñar, construir, revisar o arreglar pantallas, componentes o sistemas de diseño: accesibilidad, interacción, responsive, tipografía, color, gráficos. Incluye datos locales: 79 estilos, 192 paletas, 74 combinaciones tipográficas, 119 guías UX, 105 iconos y 22 stacks. Ejemplo: «propón paleta y tipografía para una app de reservas».

### ui-styling

Interfaces accesibles y cuidadas con shadcn/ui (Radix UI + Tailwind), utilidades de Tailwind CSS y diseños visuales en canvas (carteles, pósters). Úsala para construir componentes (diálogos, desplegables, formularios, tablas), tematizar colores, modo oscuro, layouts responsive o fijar patrones de estilo en una aplicación.

### design

Caja de herramientas de diseño: identidad de marca, tokens y estilo de UI, logotipos (55 estilos), programa de identidad corporativa (CIP, 50 entregables con mockups), presentaciones HTML con gráficos, banners (22 estilos), iconos (15 estilos en SVG) y fotos para redes sociales. Úsala con peticiones como «diseña un logo», «crea el CIP», «genera un icono», «haz un banner» o «monta una presentación».

### design-system

Arquitectura de tokens (primitivos, semánticos y de componente) con variables CSS, escalas de espaciado y tipografía, especificaciones de componentes y diapositivas estratégicas alineadas con la marca. Úsala al crear o auditar un sistema de diseño, definir tokens o hacer una presentación con la identidad de la marca.

### banner-design

Diseña banners para redes sociales, anuncios, cabeceras web y material impreso, con varias direcciones de arte y visuales generados o aportados por ti. Úsala al pedir «diseña un banner» para Facebook, X, LinkedIn, YouTube, Instagram, Google Display o una web. Estilos: minimalista, degradado, tipografía fuerte, fotográfico, ilustrado, geométrico, retro, glassmorfismo, 3D, neón, duotono, editorial o collage.

### slides

Crea presentaciones HTML estratégicas con Chart.js, tokens de diseño, maquetas responsive y fórmulas de copy según el contexto de cada diapositiva. Úsala al pedir un deck web que deba verse profesional y responder a un objetivo concreto.

### brand

Voz de marca, identidad visual, mensajes y gestión de activos, para mantener la coherencia de cualquier pieza con marca: tono de voz, material de marketing, guías de estilo y revisión de cumplimiento. Úsala al escribir o revisar algo «como nuestra marca» o al montar una guía de marca.

### orange-style

Aplica la identidad visual y las reglas de comunicación responsable del Grupo Orange (Orange, Orange España, Orange Empresas, MasOrange) a presentaciones .pptx, apps web, dashboards, HTML/React, documentos, firmas de correo, cabeceras LinkedIn/X, fondos de videollamada y cualquier entregable visual o de copy. Úsala SIEMPRE ante: "estilo Orange", "branding Orange", "/style", "estilo MasOrange", "presentación corporativa", "plantilla Orange España", "logo Orange", "firma de correo", paleta naranja-negro-blanco, o material comercial en nombre de Orange/MasOrange (propuestas, argumentarios, decks, landings, emails). También al colocar el logo, redactar claims comerciales o medioambientales, o publicar contenido generado con IA con marca Orange. Sustituye a masorange-style (obsoleta).


### auditoria-ux-visual

Auditoría UX visual en webapps, Mobile-First. Úsala ante: "auditoría UX", "revisar diseño", "contraste", "responsive", "texto que no se ve", "en móvil se rompe", "modo oscuro falla", "botones pequeños", "se ve mal al sol", "en tablet/iPad/Fold/proyector", "z-index extraño", "tooltip recortado", "panel que se sale", "pared de texto", "scrollea varias pantallas", "demasiado texto", "página larguísima". También ante cambios visuales, pantallas nuevas o releases. Diagnostica plataforma (móvil/escritorio/híbrido): Thumb Zone, Safe Areas, Gestos, Densidad, Jerarquía, Atajos. Siempre: Gamificación y snippets CSS/JS. Eje 8: entorno físico. Incluye z-index stack, sidebar 767px, tooltips en body y clamp de paneles. Eje 11: densidad de lectura (sin paredes de texto; máx. 1,5 pantallas al entrar).


### prototype · **solo si la invocas**

Crea varias versiones realmente distintas de una pieza de UI que describas, mostradas tras un selector visual para hojearlas en vivo y quedarte con la que mejor encaje. Solo se ejecuta al invocarla explícitamente; no se activa sola.

## Animación y movimiento

### animate

Construye una animación desde cero, decidiendo primero lo que determina que se sienta bien: si debe animarse, con qué propósito, qué propiedades, curva y duración, cómo se interrumpe y cómo sale. Escribe la implementación. Úsala al pedir animar algo, añadir movimiento o crear una transición. Para criticar una animación existente usa review-animations; para auditar todo el código, improve-animations.

### animate-expo

Animaciones en React Native y Expo: en qué hilo corre, qué propiedades, muelle o timing, traspaso de gestos y degradación. Usa Reanimated, Gesture Handler, Expo Router y expo-haptics. Úsala al animar cualquier cosa de una app Expo: gestos, hojas, transiciones, respuesta al pulsar, háptica o motion que da tirones en el dispositivo. Para web, usa animate.

### animation-performance

Mantén las animaciones web dentro del presupuesto de fotogramas: anima solo propiedades que el navegador compone, evita trabajo en el hilo principal y encuentra la causa cuando una animación da tirones. Úsala si una animación va a saltos, al elegir propiedad, al decidir entre CSS y JS o al plantearte will-change. Para curvas y duración, usa animate.

### animation-vocabulary

Glosario inverso: convierte una descripción vaga de un efecto de movimiento en su término exacto («el rebote al abrir un popover» → Pop in). Úsala cuando preguntes «¿cómo se llama…?» o necesites el nombre correcto para pedir algo a una IA o a un diseñador. Sirve para nombrar efectos, no para diseñarlos.

### apple-design

Enfoque de diseño de Apple y movimiento físico y fluido, trasladado a la web: gestos, resortes, arrastres y hojas interrumpibles, materiales translúcidos, tipografía (tamaño óptico, interlineado), movimiento reducido y principios de feedback y coherencia espacial. Úsala al revisar o construir UI con gestos, desplazamientos o sensación «Apple».

### emil-design-eng

Filosofía de Emil Kowalski sobre el pulido de interfaces: decisiones de componentes y animación, y los detalles invisibles que hacen que un software se sienta bien. Úsala para dar criterio de «ingeniero de diseño» al crear o revisar la calidad visual y de interacción de un componente.

### find-animation-opportunities

Busca en un código o una interfaz los sitios que no se animan pero deberían, y descarta lo que no debe moverse. Es de solo lectura: propone movimiento con valores exactos, no lo implementa. Úsala con «¿qué se podría animar aquí?» o «que se sienta más vivo». Para arreglar animaciones existentes, usa improve-animations o review-animations.

### improve-animations

Revisa el código de animación de un proyecto como asesor senior de movimiento y produce una auditoría priorizada con planes de implementación autocontenidos para otro agente. Es de solo lectura sobre el código: planifica, no aplica cambios. Úsala con «mejora las animaciones», «audita el movimiento» o para una hoja de ruta de arreglos.

### review-animations · **solo si la invocas**

Revisa código de animación y movimiento con un listón de oficio alto, derivado de la filosofía de Emil Kowalski. Por defecto marca problemas; la aprobación se gana. Solo se ejecuta al invocarla explícitamente; no se activa sola.

### remove-animations

Localiza las animaciones que una interfaz no necesita y elimínalas: movimiento en acciones de teclado, superficies de alta frecuencia, datos funcionales y decoración sin propósito. Solo resta, nunca añade ni retoca movimiento. Úsala si la app «va lenta», tiene demasiada animación o quieres saber qué quitar. Para encontrar lo que sí debe animarse, usa find-animation-opportunities.

## Web, código y pruebas

### threejs

Conocimiento actual y verificado de three.js r186, React Three Fiber 9.8 + drei y gltf-transform, en WebGL y en WebGPU/TSL. Úsala siempre que haya que escribir, revisar o depurar código 3D con three.js, WebGL o WebGPU: escenas, cámaras, renderer, geometrías, instancing, materiales PBR, texturas, UV, luces y sombras, HDR, shaders GLSL y TSL, animación, glTF/GLB, Draco, KTX2, controles, raycasting, postprocesado (bloom, SSAO), rendimiento, memoria y React Three Fiber. También para optimizar o validar modelos 3D y para migrar código antiguo (RGBELoader, Clock, PostProcessing).

### webapp-testing

Toolkit de verificación runtime de webapps con Playwright: ejecuta la página en el navegador real y captura lo que el análisis estático no ve. Úsala SIEMPRE que: "verifica que funciona de verdad", "el modal no abre", "comprueba en el navegador", "test de regresión antes del deploy", "screenshot del estado actual", "el botón no hace nada", "errores en consola", "la sección aparece en blanco aunque el HTML existe", o cuando debug-html-monolito pasa limpio pero la página sigue rota. Complementa a debug-html-monolito (estático antes de guardar) y clonar-proyecto (smoke test F3 post-deploy). Esta skill es la capa de EJECUCIÓN real en el navegador. Ver references/INTEGRACION_SKILLS.md para los puntos exactos de handoff entre skills.


### debug-html-monolito

Protocolo de diagnóstico, auditoría y reparación de archivos HTML monolíticos grandes (un solo .html con CSS + JS embebidos: portales, argumentarios, dashboards). ACTIVA SIEMPRE QUE: HTML grande con CSS y JS inline y síntomas como pantalla en blanco, botones que no hacen nada, función no definida, layout roto, JS que se rompe al editar, overlay que no aparece, tab completamente invisible, variable JS duplicada, o bugs por edición iterativa. ACTIVAR TAMBIÉN para auditorías preventivas: "audita el portal", "pasa una revisión de integridad", "comprueba que todo funciona", "da una pasada antes del deploy". Cubre: checklist JS/HTML/CSS, referencias huérfanas, IDs faltantes, base64 en bloque de estilos, divs huérfanos fuera de contenedor, variables duplicadas, colisión CSS. Patrones extraídos de portales comerciales, academias educativas y dashboards reales.


### artifact-react-components

Construye artifacts React interactivos en claude.ai con componentes ricos (tablas, gráficas, formularios, dashboards, KPIs, timelines, modales) usando las librerías ya disponibles en el sandbox: recharts, lucide-react, shadcn/ui, lodash, d3, papaparse. Úsala SIEMPRE que necesites un prototipo visual interactivo dentro del chat — un mockup para mostrar a un cliente, un dashboard de métricas para una reunión, un formulario de captura de datos, una tabla filtrable, un comparador de opciones, un wizard de pasos — sin salir a Netlify ni necesitar backend. Actívala con: "muéstrame cómo quedaría", "prototipo rápido", "mockup interactivo", "dashboard para la reunión", "tabla con filtros", "artifact con gráfica", "visualiza esto en el chat", "artifact React", "componente con shadcn", "cómo quedaría la pantalla", "demo visual", "simula la interfaz". NO usar para apps reales con backend/Firebase/Supabase → esas van a Netlify (stack vanilla). NO usar para documentos descargables → usar skill docx/pdf/pptx.


### html2pdf-export

Estrategias probadas para exportar HTML complejo a PDF con html2pdf.js en aplicaciones vanilla JS (sin frameworks ni build step). Cubre: configuración óptima, reglas CSS de salto de página, patrón pre/post export para manipular DOM antes y después de la captura, unidades atómicas en tablas, elementos visibles solo en pantalla vs solo en PDF, y arquitectura de dos modos de salida (HTML navegable / PDF imprimible). Activar cuando: "exportar a PDF", "html2pdf", "pagebreak", "saltos de página", "documento imprimible", "generar PDF", "modo HTML vs PDF", o al construir cualquier feature de generación de documentos en herramientas web.


### write-swift

Cómo escribir Swift moderno: tipos de valor, seguridad de datos y concurrencia de Swift 6 (@concurrent, actores, task groups), protocolos y genéricos, diseño de API, rendimiento y ARC, Swift Testing y macros. Úsala al escribir, revisar o migrar Swift, o al arreglar errores de concurrencia, bloqueos, ciclos de retención o rendimiento.

### svg-angulos-poligono

Reglas exactas y código validado para dibujar arcos de ángulos interiores en polígonos SVG para JoGaSan Academy. Úsala SIEMPRE que vayas a dibujar un ángulo interior en un polígono SVG: cuando hagas figuras geométricas con ángulos marcados (triángulos, cuadriláteros, polígonos regulares/irregulares), cuando el usuario pida "marca los ángulos", "añade el símbolo de ángulo", "pon los grados dentro", o al crear SVGs de geometría para los módulos de la academia. Sin esta skill los arcos salen al revés o fuera de la figura.


### ask-sonner

Guía de Sonner, la librería de toasts de React: instalación, Toaster, toast(), promesas y estados de carga, actualizar o descartar, estilos, temas, iconos y posición. Úsala al implementar notificaciones con Sonner o cuando no aparezcan, se dupliquen, pierdan estilos, queden tras un modal o no sigan el modo oscuro.

### mobile-native

Hace que una web se sienta nativa en el móvil: estados hover pegados, destellos al tocar, el bug de 100vh, campos que amplían la página, toques lentos, pull-to-refresh que secuestra el scroll, contenido bajo el notch y textos de botón seleccionables al mantener pulsado. Úsala al construir o revisar una web móvil, una PWA, una hoja inferior o un carrusel. Para el movimiento en sí, usa animate.

### break-ui

Intenta romper una interfaz con datos del peor caso (nombres larguísimos, correos sin espacios, nombres de una letra, campos vacíos, cero elementos, texto no latino, emojis, cifras extremas). Lo muestra tras un interruptor «Datos de demo / Peor caso» y lista qué se rompe con su arreglo. Úsala al pedir probar, romper o buscar casos límite en un componente o pantalla.

### pick-ui-library · **solo si la invocas**

Elige la librería adecuada para una tarea de frontend (números, inputs OTP, gráficos, menús de comando, virtualización, arrastrar y soltar, toasts, estado, estilos…) desde una lista curada y con criterio. Solo se ejecuta al invocarla explícitamente; no se activa sola.

## Metodología y proyectos

### superpowers

Metodología estructurada de desarrollo de software para agentes de IA. Actívala cuando vayas a desarrollar una feature compleja, refactorizar múltiples archivos, o cuando el usuario diga "planifica esto", "hazlo paso a paso", "brainstorming", "TDD", "debug sistemático", "haz un plan antes de codear", "revisa mi código", o ante cualquier tarea que requiera planificación antes de ejecutar. Previene el antipatrón de lanzarse a codear sin entender requisitos. Fases: Entender → Diseñar → Ejecutar (TDD: RED-GREEN-REFACTOR) → Revisar. Incluye debugging sistemático en 4 fases, planes de implementación en tareas de 2-5 minutos, code review por checklist, y brainstorming socrático. Compatible con proyectos vanilla JS, Firebase, Supabase y Netlify.

### clonar-proyecto

Protocolo para replicar cualquier proyecto web o app existente con el mínimo de iteraciones. Cuatro arquetipos: multi-archivo propio, monolito HTML propio, web externa (URL o captura), y propio sin código fuente. ACTIVA con: "quiero clonar X", "replica esta app", "haz algo parecido a Y", "toma esta web como base", "copia la estructura de", "pártete de este proyecto", "inspírate en esta URL", o cuando el usuario pegue URL, captura o código con intención de replicar. ACTIVAR TAMBIÉN: "la app no carga después del deploy", "Google Auth no funciona en producción", "Firebase no inicializa", "el ZIP no despliega bien", "error CORS en Storage", "spinner infinito en login". Cubre: inventario, limpieza de identidad, stack agnóstico, deploy y bugs frecuentes. Leer references/bugs-netlify-firebase.md para Netlify+Firebase. Academia JoGaSan nueva: delegar a clonar-academia. Bugs en monolito durante iteración: delegar a debug-html-monolito.


### documentador-contexto-proyecto

Arquitecto de Memoria y Documentación Técnica que consolida el conocimiento de un proyecto  en archivos Markdown listos para GitHub. Úsala SIEMPRE que el usuario pida generar o actualizar  README.md, CONTEXT_ADN.md o GUIAS_USO.md. Actívala cuando el usuario diga "documenta el proyecto",  "actualiza el contexto", "crea memoria del proyecto", "prepara el repositorio", "necesito  documentación", "transfiere el contexto a otra IA", "resume el historial de decisiones",  "escribe el ADN del proyecto", o quiera que una futura IA entienda el proyecto sin releer el chat. TAMBIÉN actívala proactivamente al final de sesiones de iteración: cuando se completa una  pantalla, módulo o feature ("ya funciona", "listo", "pasamos a lo siguiente", "siguiente pantalla"),  o cuando el usuario lleva varias iteraciones seguidas sobre el mismo proyecto (PWA, Firebase,  Supabase, dashboards). En esos casos, sugerir actualizar el CONTEXT_ADN.md con los cambios  de la sesión antes de continuar o cerrar la conversación.


### deep-research

Use when the user needs multi-source research with citation tracking, evidence persistence, and structured report generation. Triggers on "deep research", "comprehensive analysis", "research report", "compare X vs Y", "analyze trends", or "state of the art". Not for simple lookups, debugging, or questions answerable with 1-2 searches.

### sistema-cognitivo

Orquestador de las 5 skills cognitivas transversales: estructurador-mece, pragmatismo-esfuerzo, wording-ejecutivo, presentacion-de-datos y transmision-del-mensaje. Actívala SIEMPRE que el usuario arranque cualquier entregable con cierta complejidad: app, análisis, presentación, documento, conclusiones, email, modelo, propuesta, reunión. También con: 'aplica el sistema', 'qué skills activo', 'ayúdame a pensar esto', '/sistema', '/cognitivo', o cuando detectes que el output se beneficiaría de más de una skill. Pregunta al usuario cuáles activar, aplica todas, o elige un mix razonado según el tipo de entregable. Nunca activa las 5 por defecto sin calibrar — el pragmatismo también aplica al propio sistema.

## Educación y ventas

### ventas-b2b

Kit completo de ventas B2B en español. Actívala con /ventas-b2b para elegir entre: Discovery, Manejo de objeciones, Cualificación de leads, Posicionamiento competitivo y Cierre de ventas. Adaptada al contexto MasOrange / SITyL / transporte y logística.

### medi-adhd

Agente educativo hiperespecializado en transformar contenido del portal Academia (teoría, quizzes, actividades, exámenes, retos pro) en experiencias ultra-atractivas para niños de 7-10 años con TDAH e impulsividad. Úsala cuando el usuario diga "adapta esto para niños con TDAH", "versión Medi-ADHD", "más dinámico para impulsivos", "gamifica contenido infantil", "estilo Medi", "/adhd", "/medi", o trabaje en módulos de Academia Portal de Repaso para niños 7-10. También con "atención corta", "dopamina", "micro-recompensas", "niños impulsivos", o al convertir teoría/quiz tradicional en formato jugable con Medi. Aplica neurociencia TDAH: dopamina cada 2-3 min, cambio de formato cada 4 min, máximo 12-15 palabras por frase, lenguaje de niño de 8 años emocionado (¡CRACK!, ¡BRUTAL!, ¡BOOM!), formatos jugables (Memory, Caza-topos, Carrera), recompensas escalonadas y Medi como copiloto. NO usar para adolescentes 12+, adultos, ni docs técnicas.

### auditoria-pedagogica-jogasan

Auditor e Inspector Integral de Experiencias Educativas de JoGaSan Academy. Evalúa código (HTML/CSS/JS vanilla), contenidos didácticos y mecánicas de gamificación de las academias de 3º, 4º y 6º de Primaria, 1º ESO y el área infantil (Infantil). Aplica rúbrica de 4 pilares: Rigor Curricular, UX/Accesibilidad TDAH, Motivación/Gamificación y Trazabilidad Docente. Úsala SIEMPRE que el usuario pida "auditar" una pantalla, módulo, quiz, actividad, teoría o examen del portal. También cuando diga "revisar contenido", "validar ejercicio", "inspeccionar quiz", "comprobar teoría", "revisar chunk", "validar medalla", "comprobar trazabilidad", "lupa del profe", "chip de lectura", o al pegar código HTML/JS de una academia para revisión. Activa también ante: "¿está bien esto para 3º?", "¿es correcto para 6º?", "¿cumple currículum?", "revisa si el quiz captura errores", "valida la gamificación", o al mencionar una academia específica (Geometría, Inglés, Naturales, etc.) junto con cualquier petición de revisión.


### clonar-academia

Protocolo para crear una academia nueva en JoGaSan Academy (Netlify + Supabase) y para AUDITAR las existentes. Úsala con "crear una academia nueva", "añadir Sociales 3º", "hacer Música 6º", al dudar si una academia está completa y ante divergencias: medallas distintas, barra de progreso ausente, diploma que no se desbloquea, quiz sin leer la teoría, fallos negativos, botones repetidos. También con "apuntes del profe", "📒 Apuntes de clase", "módulo nuevo de 1º ESO", "juegos para memorizar"; antes de añadir contenido, antes de editar un HTML generado (s56) y al escribir preguntas (s65). Alta = UNA entrada en catalogo.js. Auditoría: node scripts/validar-academias.js (bloquea el deploy). 89 síntomas (s80-s89: figuras SVG, texto de figura, datos dudosos, main/produccion, teoría exhaustiva, juegos, entregas, chuletas A4, sesiones paralelas), FASE 3.5 y 3.6.

