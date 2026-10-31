---
name: threejs
description: "Conocimiento actual y verificado de three.js r186, React Three Fiber 9.8 + drei y gltf-transform, en WebGL y en WebGPU/TSL. Úsala siempre que haya que escribir, revisar o depurar código 3D con three.js, WebGL o WebGPU: escenas, cámaras, renderer, geometrías, instancing, materiales PBR, texturas, UV, luces y sombras, HDR, shaders GLSL y TSL, animación, glTF/GLB, Draco, KTX2, controles, raycasting, postprocesado (bloom, SSAO), rendimiento, memoria y React Three Fiber. También para optimizar o validar modelos 3D y para migrar código antiguo (RGBELoader, Clock, PostProcessing)."
---

# three.js (índice de guías)

Apunta a **three.js r186** (`three@0.186`), React Three Fiber 9.8 con drei 10.7 y gltf-transform 4.5. Los ejemplos usan `WebGLRenderer`; cada guía incluye una sección «WebGPU y TSL» para `WebGPURenderer`.

Este fichero solo enruta: **lee únicamente las guías que necesite la tarea**, desde `references/`.

## Reglas globales (valen siempre)

- No uses patrones anteriores a r186 que el modelo suele repetir: `RGBELoader` → `HDRLoader`; `Clock` → `Timer`; `PostProcessing` → `RenderPipeline`. WebGL 1 ya no existe.
- Para shaders y materiales personalizados nuevos, la documentación de three.js recomienda `WebGPURenderer` con TSL; usa GLSL/`ShaderMaterial` si el proyecto está en WebGL.
- Cada guía termina con «Common Mistakes» (errores frecuentes): léelo antes de dar el código por bueno.
- Si el proyecto fija otra versión de three, avisa de las diferencias de API en vez de asumir r186.

## Tabla de enrutado

| La tarea trata de… | Lee |
|---|---|
| Escena, niebla, cámara, renderer, tone mapping, bucle de animación, jerarquías, transformaciones, resize, limpieza | `references/fundamentals.md` |
| Formas integradas, texto 3D, atributos y buffers, merge, instancing, batching, nubes de puntos, líneas | `references/geometry.md` |
| Elegir/configurar materiales (PBR, toon, unlit, puntos, líneas), blending, stencil, node materials | `references/materials.md` |
| Imágenes en materiales, color spaces, UV, cubemaps, render targets, memoria de texturas | `references/textures.md` |
| Tipos de luz, unidades físicas, sombras (acné), iluminación HDR/IBL, light probes | `references/lighting.md` |
| GLSL de vértices/fragmentos, uniforms, varyings, shader chunks, extender materiales, portar GLSL a TSL | `references/shaders.md` |
| Keyframes, esqueletos, morph targets, mezcla y crossfade de clips, movimiento procedural | `references/animation.md` |
| Ratón/táctil/teclado, raycasting, controles de cámara, gizmos, arrastre, selección | `references/interaction.md` |
| Cargar glTF, texturas, HDR/EXR, progreso, caché, clonado, dispose | `references/loaders.md` |
| Comprimir/validar modelos: gltf-transform, Draco, meshopt, KTX2, WebP/AVIF, gltfjsx | `references/asset-pipeline.md` |
| Bloom, profundidad de campo, SSAO, etiquetado de color, efectos de pantalla, RenderPipeline | `references/postprocessing.md` |
| FPS bajos, draw calls, memoria, LOD, fill rate, sombras caras, compute en GPU | `references/performance.md` |
| Componentes React, `Canvas`, hooks, eventos de puntero, drei, rendimiento adaptativo | `references/react-three-fiber.md` |

## Combinaciones habituales

- **Escena nueva:** `fundamentals` → lo que toque (`geometry`, `materials`, `lighting`) → `performance` como lista de comprobación final.
- **Cargar un modelo y mostrarlo bien:** `loaders` + `lighting` (entorno HDR) + `materials`; si pesa mucho, `asset-pipeline`.
- **Efecto visual propio:** `shaders` + `materials`; si es de pantalla completa, `postprocessing`.
- **Proyecto React:** `react-three-fiber` primero y, después, la guía temática (los conceptos de three valen igual).
- **Escena lenta:** `performance`, y de ahí a `geometry` (instancing), `lighting` (sombras) o `textures` según el cuello de botella.

## Cómo trabajar

1. Identifica la fila (o filas) de la tabla y lee solo esas guías.
2. Comprueba si el proyecto usa WebGL o WebGPU y si es React; usa la sección correspondiente.
3. Escribe el código siguiendo los ejemplos de la guía y revisa su lista de errores frecuentes.
4. Si dos guías se contradicen, prevalece la más específica del tema (p. ej. `loaders` para cargar, `asset-pipeline` para comprimir) y dilo.
