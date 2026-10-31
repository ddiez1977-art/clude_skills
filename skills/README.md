# Guía de skills instaladas (en español)

Cada skill se activa sola cuando la descripción encaja con lo que pides. Las marcadas «solo si la invocas» hay que pedirlas por su nombre.

## animate-expo

Animaciones en React Native y Expo: en qué hilo corre, qué propiedades, muelle o timing, traspaso de gestos y degradación. Usa Reanimated, Gesture Handler, Expo Router y expo-haptics. Úsala al animar cualquier cosa de una app Expo: gestos, hojas, transiciones, respuesta al pulsar, háptica o motion que da tirones en el dispositivo. Para web, usa animate.

## animate

Construye una animación desde cero, decidiendo primero lo que determina que se sienta bien: si debe animarse, con qué propósito, qué propiedades, curva y duración, cómo se interrumpe y cómo sale. Escribe la implementación. Úsala al pedir animar algo, añadir movimiento o crear una transición. Para criticar una animación existente usa review-animations; para auditar todo el código, improve-animations.

## animation-performance

Mantén las animaciones web dentro del presupuesto de fotogramas: anima solo propiedades que el navegador compone, evita trabajo en el hilo principal y encuentra la causa cuando una animación da tirones. Úsala si una animación va a saltos, al elegir propiedad, al decidir entre CSS y JS o al plantearte will-change. Para curvas y duración, usa animate.

## animation-vocabulary

Glosario inverso: convierte una descripción vaga de un efecto de movimiento en su término exacto («el rebote al abrir un popover» → Pop in). Úsala cuando preguntes «¿cómo se llama…?» o necesites el nombre correcto para pedir algo a una IA o a un diseñador. Sirve para nombrar efectos, no para diseñarlos.

## apple-design

Enfoque de diseño de Apple y movimiento físico y fluido, trasladado a la web: gestos, resortes, arrastres y hojas interrumpibles, materiales translúcidos, tipografía (tamaño óptico, interlineado), movimiento reducido y principios de feedback y coherencia espacial. Úsala al revisar o construir UI con gestos, desplazamientos o sensación «Apple».

## ask-sonner

Guía de Sonner, la librería de toasts de React: instalación, Toaster, toast(), promesas y estados de carga, actualizar o descartar, estilos, temas, iconos y posición. Úsala al implementar notificaciones con Sonner o cuando no aparezcan, se dupliquen, pierdan estilos, queden tras un modal o no sigan el modo oscuro.

## banner-design

Diseña banners para redes sociales, anuncios, cabeceras web y material impreso, con varias direcciones de arte y visuales generados o aportados por ti. Úsala al pedir «diseña un banner» para Facebook, X, LinkedIn, YouTube, Instagram, Google Display o una web. Estilos: minimalista, degradado, tipografía fuerte, fotográfico, ilustrado, geométrico, retro, glassmorfismo, 3D, neón, duotono, editorial o collage.

## brand

Voz de marca, identidad visual, mensajes y gestión de activos, para mantener la coherencia de cualquier pieza con marca: tono de voz, material de marketing, guías de estilo y revisión de cumplimiento. Úsala al escribir o revisar algo «como nuestra marca» o al montar una guía de marca.

## break-ui

Intenta romper una interfaz con datos del peor caso (nombres larguísimos, correos sin espacios, nombres de una letra, campos vacíos, cero elementos, texto no latino, emojis, cifras extremas). Lo muestra tras un interruptor «Datos de demo / Peor caso» y lista qué se rompe con su arreglo. Úsala al pedir probar, romper o buscar casos límite en un componente o pantalla.

## design-system

Arquitectura de tokens (primitivos, semánticos y de componente) con variables CSS, escalas de espaciado y tipografía, especificaciones de componentes y diapositivas estratégicas alineadas con la marca. Úsala al crear o auditar un sistema de diseño, definir tokens o hacer una presentación con la identidad de la marca.

## design

Caja de herramientas de diseño: identidad de marca, tokens y estilo de UI, logotipos (55 estilos), programa de identidad corporativa (CIP, 50 entregables con mockups), presentaciones HTML con gráficos, banners (22 estilos), iconos (15 estilos en SVG) y fotos para redes sociales. Úsala con peticiones como «diseña un logo», «crea el CIP», «genera un icono», «haz un banner» o «monta una presentación».

## emil-design-eng

Filosofía de Emil Kowalski sobre el pulido de interfaces: decisiones de componentes y animación, y los detalles invisibles que hacen que un software se sienta bien. Úsala para dar criterio de «ingeniero de diseño» al crear o revisar la calidad visual y de interacción de un componente.

## find-animation-opportunities

Busca en un código o una interfaz los sitios que no se animan pero deberían, y descarta lo que no debe moverse. Es de solo lectura: propone movimiento con valores exactos, no lo implementa. Úsala con «¿qué se podría animar aquí?» o «que se sienta más vivo». Para arreglar animaciones existentes, usa improve-animations o review-animations.

## frontend-design

Guía para diseñar interfaces con intención visual propia, sin el aspecto genérico de plantilla. Úsala al crear una interfaz nueva o rediseñar una existente: define dirección estética, tipografía, color y composición. Ejemplo: «rediseña esta landing con un estilo distintivo».

## improve-animations

Revisa el código de animación de un proyecto como asesor senior de movimiento y produce una auditoría priorizada con planes de implementación autocontenidos para otro agente. Es de solo lectura sobre el código: planifica, no aplica cambios. Úsala con «mejora las animaciones», «audita el movimiento» o para una hoja de ruta de arreglos.

## mobile-native

Hace que una web se sienta nativa en el móvil: estados hover pegados, destellos al tocar, el bug de 100vh, campos que amplían la página, toques lentos, pull-to-refresh que secuestra el scroll, contenido bajo el notch y textos de botón seleccionables al mantener pulsado. Úsala al construir o revisar una web móvil, una PWA, una hoja inferior o un carrusel. Para el movimiento en sí, usa animate.

## pick-ui-library

Elige la librería adecuada para una tarea de frontend (números, inputs OTP, gráficos, menús de comando, virtualización, arrastrar y soltar, toasts, estado, estilos…) desde una lista curada y con criterio. Solo se ejecuta al invocarla explícitamente; no se activa sola.

## prototype

Crea varias versiones realmente distintas de una pieza de UI que describas, mostradas tras un selector visual para hojearlas en vivo y quedarte con la que mejor encaje. Solo se ejecuta al invocarla explícitamente; no se activa sola.

## remove-animations

Localiza las animaciones que una interfaz no necesita y elimínalas: movimiento en acciones de teclado, superficies de alta frecuencia, datos funcionales y decoración sin propósito. Solo resta, nunca añade ni retoca movimiento. Úsala si la app «va lenta», tiene demasiada animación o quieres saber qué quitar. Para encontrar lo que sí debe animarse, usa find-animation-opportunities.

## review-animations

Revisa código de animación y movimiento con un listón de oficio alto, derivado de la filosofía de Emil Kowalski. Por defecto marca problemas; la aprobación se gana. Solo se ejecuta al invocarla explícitamente; no se activa sola.

## slides

Crea presentaciones HTML estratégicas con Chart.js, tokens de diseño, maquetas responsive y fórmulas de copy según el contexto de cada diapositiva. Úsala al pedir un deck web que deba verse profesional y responder a un objetivo concreto.

## ui-styling

Interfaces accesibles y cuidadas con shadcn/ui (Radix UI + Tailwind), utilidades de Tailwind CSS y diseños visuales en canvas (carteles, pósters). Úsala para construir componentes (diálogos, desplegables, formularios, tablas), tematizar colores, modo oscuro, layouts responsive o fijar patrones de estilo en una aplicación.

## ui-ux-pro-max

Inteligencia de diseño UI/UX para web, móvil y escritorio. Úsala al diseñar, construir, revisar o arreglar pantallas, componentes o sistemas de diseño: accesibilidad, interacción, responsive, tipografía, color, gráficos. Incluye datos locales: 79 estilos, 192 paletas, 74 combinaciones tipográficas, 119 guías UX, 105 iconos y 22 stacks. Ejemplo: «propón paleta y tipografía para una app de reservas».

## write-swift

Cómo escribir Swift moderno: tipos de valor, seguridad de datos y concurrencia de Swift 6 (@concurrent, actores, task groups), protocolos y genéricos, diseño de API, rendimiento y ARC, Swift Testing y macros. Úsala al escribir, revisar o migrar Swift, o al arreglar errores de concurrencia, bloqueos, ciclos de retención o rendimiento.


## threejs

Conocimiento actual y verificado de three.js r186, React Three Fiber 9.8 + drei y gltf-transform, en WebGL y en WebGPU/TSL. Úsala siempre que haya que escribir, revisar o depurar código 3D con three.js, WebGL o WebGPU: escenas, cámaras, renderer, geometrías, instancing, materiales PBR, texturas, UV, luces y sombras, HDR, shaders GLSL y TSL, animación, glTF/GLB, Draco, KTX2, controles, raycasting, postprocesado (bloom, SSAO), rendimiento, memoria y React Three Fiber. También para optimizar o validar modelos 3D y para migrar código antiguo (RGBELoader, Clock, PostProcessing).

## auditoria-pedagogica-jogasan

Auditor e Inspector Integral de Experiencias Educativas de JoGaSan Academy. Evalúa código (HTML/CSS/JS vanilla), contenidos didácticos y mecánicas de gamificación de las academias de 3º, 4º y 6º de Primaria, 1º ESO y el Rincón de Santi (Infantil). Aplica rúbrica de 4 pilares: Rigor Curricular, UX/Accesibilidad TDAH, Motivación/Gamificación y Trazabilidad Docente. Úsala SIEMPRE que el usuario pida "auditar" una pantalla, módulo, quiz, actividad, teoría o examen del portal. También cuando diga "revisar contenido", "validar ejercicio", "inspeccionar quiz", "comprobar teoría", "revisar chunk", "validar medalla", "comprobar trazabilidad", "lupa del profe", "chip de lectura", o al pegar código HTML/JS de una academia para revisión. Activa también ante: "¿está bien esto para 3º?", "¿es correcto para 6º?", "¿cumple currículum?", "revisa si el quiz captura errores", "valida la gamificación", o al mencionar una academia específica (Geometría, Inglés, Naturales, etc.) junto con cualquier petición de revisión.


## clonar-academia

Protocolo para crear una academia nueva en JoGaSan Academy (Netlify + Supabase) y para AUDITAR las existentes. Úsala con "crear una academia nueva", "añadir Sociales 3º", "hacer Música 6º", al dudar si una academia está completa y ante divergencias: medallas distintas, barra de progreso ausente, diploma que no se desbloquea, quiz sin leer la teoría, fallos negativos, botones repetidos. También con "apuntes del profe", "📒 Apuntes de clase", "módulo nuevo de 1º ESO", "juegos para memorizar"; antes de añadir contenido, antes de editar un HTML generado (s56) y al escribir preguntas (s65). Alta = UNA entrada en catalogo.js. Auditoría: node scripts/validar-academias.js (bloquea el deploy). 89 síntomas (s80-s89: figuras SVG, texto de figura, datos dudosos, main/produccion, teoría exhaustiva, juegos, entregas, chuletas A4, sesiones paralelas), FASE 3.5 y 3.6.


## ventas-b2b

Kit completo de ventas B2B en español. Actívala con /ventas-b2b para elegir entre: Discovery, Manejo de objeciones, Cualificación de leads, Posicionamiento competitivo y Cierre de ventas. Adaptada al contexto MasOrange / SITyL / transporte y logística.

## sistema-cognitivo

Orquestador de las 5 skills cognitivas transversales: estructurador-mece, pragmatismo-esfuerzo, wording-ejecutivo, presentacion-de-datos y transmision-del-mensaje. Actívala SIEMPRE que el usuario arranque cualquier entregable con cierta complejidad: app, análisis, presentación, documento, conclusiones, email, modelo, propuesta, reunión. También con: 'aplica el sistema', 'qué skills activo', 'ayúdame a pensar esto', '/sistema', '/cognitivo', o cuando detectes que el output se beneficiaría de más de una skill. Pregunta al usuario cuáles activar, aplica todas, o elige un mix razonado según el tipo de entregable. Nunca activa las 5 por defecto sin calibrar — el pragmatismo también aplica al propio sistema.
