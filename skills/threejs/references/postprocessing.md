# Postprocesado en Three.js

Dirigido a three.js r186. Los ejemplos usan WebGLRenderer; la sección de WebGPU y TSL usa WebGPURenderer.

## Inicio rápido

```javascript
import * as THREE from "three";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(0, 0, 5);

// Una esfera emisiva brillante le da al bloom algo que captar
const mesh = new THREE.Mesh(
  new THREE.SphereGeometry(1, 32, 16),
  new THREE.MeshStandardMaterial({ color: 0x222222, emissive: 0xffffff, emissiveIntensity: 2 }),
);
scene.add(mesh);

// El composer sustituye a renderer.render(). Renderiza la escena, luego los efectos
// y, por último, OutputPass: aplica una sola vez renderer.toneMapping y outputColorSpace.
const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const bloomPass = new UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 1.5, 0.4, 0.85);
// bloomPass.strength, .radius y .threshold son propiedades en vivo; threshold es la luminancia a partir de la cual las cosas brillan
composer.addPass(bloomPass);
composer.addPass(new OutputPass());

function animate() {
  composer.render(); // no renderer.render()
}

renderer.setAnimationLoop(animate);
```

## Orden de los pases

Los búferes del composer contienen colores lineales; el tone mapping y la conversión a sRGB se hacen una sola vez, en `OutputPass`, con los ajustes del renderer. Construye las cadenas en este orden: `RenderPass` → efectos en espacio lineal (bloom, profundidad de campo, SSAO, contorno, ...) → `SMAAPass`, después de los efectos cuyos bordes debe suavizar → `OutputPass` → `FXAAPass` (`three/addons/postprocessing/FXAAPass.js`) solo cuando se use FXAA, porque FXAA necesita entrada sRGB. Sin FXAA, `OutputPass` es el último pase.

`SSAOPass` oscurece la imagen producida por el pase anterior, así que antes tiene que haber un `RenderPass`. `RenderPixelatedPass` renderiza la escena por sí mismo y sustituye a `RenderPass`. `pass.enabled = false` omite un pase sin reconstruir la cadena.

```javascript
import * as THREE from "three";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import { SMAAPass } from "three/addons/postprocessing/SMAAPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
composer.addPass(new UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 1.5, 0.4, 0.85));
composer.addPass(new SMAAPass()); // sin argumentos; el composer le da el tamaño
composer.addPass(new OutputPass());
```

## Configuración del composer

- El composer copia la relación de píxeles (pixel ratio) del renderer al construirse. Llama a `renderer.setPixelRatio()` antes de construirlo, o a `composer.setPixelRatio()` después.
- Los búferes del composer no son multimuestreados; `antialias: true` en el renderer no llega hasta ellos. Para tener MSAA en el render de la escena y en los búferes del composer, pasa tu propio búfer con `samples` (tamaño en píxeles CSS) y dimensiona el composer una vez:

```javascript
import * as THREE from "three";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";

const composer = new EffectComposer(
  renderer,
  new THREE.WebGLRenderTarget(window.innerWidth, window.innerHeight, {
    type: THREE.HalfFloatType,
    samples: 4, // MSAA en los dos búferes del composer
  }),
);
composer.setSize(window.innerWidth, window.innerHeight); // escala el búfer según el pixel ratio
```

- Al redimensionar, llama a `camera.aspect = w / h; camera.updateProjectionMatrix(); renderer.setSize(w, h); composer.setSize(w, h);` — el composer redimensiona sus búferes y todos los pases, pixel ratio incluido. No redimensiones nunca un pase a mano.
- `composer.render()` alimenta los pases dependientes del tiempo (FilmPass) con su propio temporizador interno; pasa un delta en segundos solo si gestionas el tiempo tú.
- El composer asigna `renderToScreen` al último pase habilitado en cada fotograma. Pon `composer.renderToScreen = false` solo para mantener el resultado fuera de la pantalla, como hace más abajo el bloom selectivo.

## Bloom selectivo

Aplica bloom solo a las mallas marcadas con una capa: pinta todo lo demás de negro en un composer solo de bloom que renderiza fuera de pantalla y luego mezcla su textura en un composer final que renderiza la escena limpia. `scene.background` no es una malla: ponlo a `null` alrededor de `bloomComposer.render()`, o se sumará una segunda vez a la imagen final; al redimensionar, llama a `setSize` en ambos composers.

```javascript
import * as THREE from "three";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js";

const BLOOM_LAYER = 1;
const bloomLayer = new THREE.Layers();
bloomLayer.set(BLOOM_LAYER); // máscara de prueba: coincide con cualquier objeto habilitado en esta capa

mesh.layers.enable(BLOOM_LAYER); // añade la capa; set() sacaría la malla de la capa 0

// Pinta de negro las mallas sin bloom y luego las restaura
const darkMaterial = new THREE.MeshBasicMaterial({ color: 0x000000 });
const materials = new Map();

function darkenNonBloomed(object) {
  if (object.isMesh && bloomLayer.test(object.layers) === false) {
    materials.set(object, object.material);
    object.material = darkMaterial;
  }
}

function restoreMaterial(object) {
  if (materials.has(object)) {
    object.material = materials.get(object);
    materials.delete(object);
  }
}

// Composer solo de bloom; con renderToScreen desactivado, su resultado se queda en renderTarget2
const bloomComposer = new EffectComposer(renderer);
bloomComposer.renderToScreen = false;
bloomComposer.addPass(new RenderPass(scene, camera));
bloomComposer.addPass(new UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 1.5, 0.4, 0.85));

// Composer final: la escena limpia más la textura de bloom, mezcladas con un ShaderPass
const finalComposer = new EffectComposer(renderer);
finalComposer.addPass(new RenderPass(scene, camera));
finalComposer.addPass(
  new ShaderPass(
    new THREE.ShaderMaterial({
      uniforms: {
        baseTexture: { value: null }, // se rellena desde el pase anterior
        bloomTexture: { value: bloomComposer.renderTarget2.texture },
      },
      vertexShader: /* glsl */ `
        varying vec2 vUv;
        void main() {
          vUv = uv;
          gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
      `,
      fragmentShader: /* glsl */ `
        uniform sampler2D baseTexture;
        uniform sampler2D bloomTexture;
        varying vec2 vUv;
        void main() {
          gl_FragColor = texture2D(baseTexture, vUv) + texture2D(bloomTexture, vUv);
        }
      `,
    }),
    "baseTexture",
  ),
);
finalComposer.addPass(new OutputPass());

function animate() {
  const background = scene.background;
  scene.background = null; // no es una malla: haría bloom y se sumaría dos veces
  scene.traverse(darkenNonBloomed); // escena negra: solo hacen bloom las mallas marcadas
  bloomComposer.render();
  scene.traverse(restoreMaterial);
  scene.background = background;
  finalComposer.render(); // escena limpia + bloom a la pantalla
}

renderer.setAnimationLoop(animate);
```

## Profundidad de campo

```javascript
import { BokehPass } from "three/addons/postprocessing/BokehPass.js";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera)); // BokehPass lee esta imagen de color

const bokehPass = new BokehPass(scene, camera, {
  focus: 10.0, // profundidad en espacio de vista que se mantiene nítida, en unidades del mundo
  aperture: 0.025, // cuánto se desenfoca lo que está fuera de foco
  maxblur: 0.01, // límite del radio de desenfoque
});
composer.addPass(bokehPass);
composer.addPass(new OutputPass());

// Reenfocar en tiempo de ejecución: distanceTo coincide con la profundidad en espacio de vista para objetos cercanos al centro de la vista
bokehPass.uniforms.focus.value = camera.position.distanceTo(mesh.position);
```

## Oclusión ambiental

```javascript
import { SSAOPass } from "three/addons/postprocessing/SSAOPass.js";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";

const composer = new EffectComposer(renderer);

// SSAOPass oscurece la imagen anterior, así que el render de la escena debe ir primero
composer.addPass(new RenderPass(scene, camera));

const ssaoPass = new SSAOPass(scene, camera, window.innerWidth, window.innerHeight);
ssaoPass.kernelRadius = 16;
ssaoPass.minDistance = 0.005;
ssaoPass.maxDistance = 0.1;
composer.addPass(ssaoPass);
composer.addPass(new OutputPass());

// Vistas de depuración: ssaoPass.output = SSAOPass.OUTPUT.SSAO (o Blur, Depth, Normal); por defecto se ve la escena sombreada
```

## Contorno

```javascript
import * as THREE from "three";
import { OutlinePass } from "three/addons/postprocessing/OutlinePass.js";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));

const outlinePass = new OutlinePass(new THREE.Vector2(window.innerWidth, window.innerHeight), scene, camera);
outlinePass.selectedObjects = [mesh]; // solo se perfilan estos
outlinePass.edgeStrength = 3;
outlinePass.visibleEdgeColor.set(0xffffff);
outlinePass.hiddenEdgeColor.set(0x190a05); // partes ocultas tras otros objetos
composer.addPass(outlinePass);
composer.addPass(new OutputPass());
```

## Más pases

El grano de película, el glitch, el halftone y la viñeta son filtros listos para colocar en medio de la cadena. `ColorCorrectionShader` funciona como la viñeta: un `ShaderPass` con vectores uniformes `powRGB` / `mulRGB` / `addRGB`. Su powRGB por defecto de (2, 2, 2) oscurece la imagen; parte de (1, 1, 1) para un resultado neutro.

```javascript
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";
import { FilmPass } from "three/addons/postprocessing/FilmPass.js";
import { GlitchPass } from "three/addons/postprocessing/GlitchPass.js";
import { HalftonePass } from "three/addons/postprocessing/HalftonePass.js";
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js";
import { VignetteShader } from "three/addons/shaders/VignetteShader.js";

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));

const filmPass = new FilmPass(0.35, false); // intensidad del grano, escala de grises; se anima con el delta del composer
composer.addPass(filmPass);

const glitchPass = new GlitchPass();
glitchPass.goWild = true; // glitch en cada fotograma; false (el valor por defecto) lo hace a intervalos aleatorios
composer.addPass(glitchPass);

const halftonePass = new HalftonePass({ shape: 1, radius: 4, scatter: 0, greyscale: false }); // shape: 1 punto, 2 elipse, 3 línea, 4 cuadrado, 5 rombo
composer.addPass(halftonePass);

const vignettePass = new ShaderPass(VignetteShader); // uniforms: offset y darkness
vignettePass.uniforms.offset.value = 1.0;
vignettePass.uniforms.darkness.value = 1.0;
composer.addPass(vignettePass);

composer.addPass(new OutputPass());
```

`RenderPixelatedPass` renderiza la escena por sí mismo, así que sustituye a `RenderPass` en lugar de ir detrás:

```javascript
import { RenderPixelatedPass } from "three/addons/postprocessing/RenderPixelatedPass.js";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";

const composer = new EffectComposer(renderer);
const pixelatedPass = new RenderPixelatedPass(6, scene, camera); // 6 = tamaño del píxel
pixelatedPass.normalEdgeStrength = 0.3; // bordes donde cambia la normal de la superficie (pliegues)
pixelatedPass.depthEdgeStrength = 0.4; // bordes por discontinuidad de profundidad
composer.addPass(pixelatedPass);
composer.addPass(new OutputPass());
```

## Pases personalizados

Envuelve cualquier objeto de shader al estilo `ShaderMaterial` en un `ShaderPass`. El uniform `tDiffuse` recibe la salida del pase anterior. Mantén los efectos personalizados antes de `OutputPass` mientras trabajen en espacio lineal; colócalos después solo si necesitan entrada sRGB, como FXAA.

```javascript
import * as THREE from "three";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js";

const WaveShader = {
  uniforms: {
    tDiffuse: { value: null },
    time: { value: 0 },
    intensity: { value: 1.0 },
  },
  vertexShader: /* glsl */ `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: /* glsl */ `
    uniform sampler2D tDiffuse;
    uniform float time;
    uniform float intensity;
    varying vec2 vUv;
    void main() {
      vec2 uv = vUv;
      uv.x += sin(uv.y * 10.0 + time) * 0.01 * intensity; // distorsión en onda
      gl_FragColor = texture2D(tDiffuse, uv);
    }
  `,
};

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const wavePass = new ShaderPass(WaveShader);
composer.addPass(wavePass);
composer.addPass(new OutputPass());

// Alimenta los uniforms de tiempo desde un Timer
const timer = new THREE.Timer();
timer.connect(document); // mantiene los deltas razonables en pestañas inactivas

function animate() {
  timer.update();
  wavePass.uniforms.time.value = timer.getElapsed();
  composer.render();
}

renderer.setAnimationLoop(animate);
```

## Efectos integrados en el renderer (sin composer)

`renderer.setEffects()` ejecuta pases ordinarios sobre búferes HDR internos después de un `renderer.render()` normal — sin composer, y el tone mapping y el espacio de color de salida se aplican automáticamente tras los efectos. Requiere `outputBufferType: THREE.HalfFloatType` (o `FloatType`), no admite `OutputPass` ni `FXAAPass`, aplica antialiasing mediante `antialias: true` y se redimensiona con `renderer.setSize()`. Aquí los efectos no reciben delta de tiempo: el uniform de tiempo de FilmPass pasa a ser NaN y su grano se pierde, así que ejecuta los pases dirigidos por el tiempo a través de EffectComposer.

```javascript
import * as THREE from "three";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";

const renderer = new THREE.WebGLRenderer({ antialias: true, outputBufferType: THREE.HalfFloatType });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const bloomPass = new UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 1.5, 0.4, 0.85);
renderer.setEffects([bloomPass]);

function animate() {
  renderer.render(scene, camera); // el bloom se ejecuta sobre los búferes HDR internos tras el render de la escena
}

renderer.setAnimationLoop(animate);
```

## WebGPU y TSL

Con WebGPURenderer, el postprocesado es un grafo de nodos TSL sobre un `RenderPipeline`, no una cadena de pases: renderiza la escena con `pass()`, construye los efectos con `three/addons/tsl/display/*.js` y asigna el nodo final a `renderPipeline.outputNode`. `pass()` usa las muestras MSAA del renderer, así que aquí `antialias: true` funciona, salvo para el prepase de `ao()`, que debe ser `pass(scene, camera, { samples: 0 })`, y para `traa`, que necesita un renderer sin `antialias`; además, `pass()` sigue a `renderer.setSize()`, de modo que el pipeline no necesita su propia llamada de redimensionado.

```javascript
import * as THREE from "three/webgpu";
import { pass } from "three/tsl";
import { bloom } from "three/addons/tsl/display/BloomNode.js";

const renderer = new THREE.WebGPURenderer({ antialias: true });
await renderer.init(); // antes de cualquier otro uso del renderer
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x111111); // el canvas de WebGPU es transparente por defecto
const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(0, 0, 5);
scene.add(new THREE.Mesh(new THREE.SphereGeometry(1, 32, 16), new THREE.MeshBasicNodeMaterial({ color: 0xffffff })));
const renderPipeline = new THREE.RenderPipeline(renderer);
const scenePass = pass(scene, camera);
const scenePassColor = scenePass.getTextureNode("output");

// bloom() devuelve solo el resplandor, así que súmalo al color de la escena
renderPipeline.outputNode = scenePassColor.add(bloom(scenePassColor, 1.5, 0.4, 0.85));

function animate() {
  renderPipeline.render(); // en lugar de renderer.render()
}

renderer.setAnimationLoop(animate);
```

Los filtros devuelven la imagen terminada y sustituyen al nodo de salida: `dof`, `film`, `rgbShift`, `chromaticAberration`, `afterImage`, `dotScreen`, `lut3D` y `smaa` (entrada lineal) toman el nodo de color de la escena, `pixelationPass(scene, camera, 6)` renderiza la escena por sí mismo, y `traa` necesita un MRT de velocidad y un renderer sin `antialias`. Igual que `bloom`, `outline(scene, camera, { selectedObjects })` devuelve solo máscaras de bordes (`.visibleEdge`, `.hiddenEdge`) que tú coloreas y sumas al color de la escena, y `ssao(depthNode, normalNode, camera)` devuelve solo el factor de oclusión en `.r`, que multiplica el color de la escena.

```javascript
import * as THREE from "three/webgpu";
import { pass, renderOutput } from "three/tsl";
import { dof } from "three/addons/tsl/display/DepthOfFieldNode.js";
import { fxaa } from "three/addons/tsl/display/FXAANode.js";

const renderPipeline = new THREE.RenderPipeline(renderer);
const scenePass = pass(scene, camera);
const scenePassColor = scenePass.getTextureNode("output");
// Un filtro sustituye la imagen: nodo, viewZ, distancia de enfoque, distancia focal, escala del bokeh
const dofNode = dof(scenePassColor, scenePass.getViewZNode(), 4.5, 1.2, 2.5);

// FXAA trabaja en sRGB: desactiva la transformación de salida automática y convierte el resultado del DOF antes de FXAA
renderPipeline.outputColorTransform = false;
renderPipeline.outputNode = fxaa(renderOutput(dofNode));

// Tras el primer fotograma, un outputNode u outputColorTransform modificado solo surte efecto con:
renderPipeline.needsUpdate = true;
```

`ao()` necesita la profundidad y las normales en espacio de vista de un prepase aparte, de una sola muestra, y su AO vive en el canal rojo:

```javascript
import * as THREE from "three/webgpu";
import { pass, mrt, normalView, screenUV, builtinAOContext } from "three/tsl";
import { ao } from "three/addons/tsl/display/GTAONode.js";

const renderPipeline = new THREE.RenderPipeline(renderer);
// Prepase con normales en espacio de vista en el adjunto de salida del MRT
const prePass = pass(scene, camera, { samples: 0 }); // ao() no puede leer una textura de profundidad multimuestreada
prePass.setMRT(mrt({ output: normalView }));

const aoPass = ao(prePass.getTextureNode("depth"), prePass.getTextureNode(), camera);

// Aplica el AO a un pase de escena normal
const scenePass = pass(scene, camera);
scenePass.contextNode = builtinAOContext(aoPass.getTextureNode().sample(screenUV).r);
renderPipeline.outputNode = scenePass;
```

Un efecto personalizado es TSL puro sobre la textura de la escena en lugar de un `ShaderPass` en GLSL; esta es la onda de Pases personalizados, animada por el nodo `time`:

```javascript
import * as THREE from "three/webgpu";
import { pass, screenUV, sin, time, vec2 } from "three/tsl";

const renderPipeline = new THREE.RenderPipeline(renderer);
const scenePassColor = pass(scene, camera).getTextureNode("output");
const offset = vec2(sin(screenUV.y.mul(10).add(time)).mul(0.01), 0);
renderPipeline.outputNode = scenePassColor.sample(screenUV.add(offset));
```

Aquí el bloom selectivo no necesita el truco de las capas: añade `emissive` (de `three/tsl`) al MRT del pase con `scenePass.setMRT(mrt({ output, emissive }))` y aplica bloom solo a ese adjunto: `renderPipeline.outputNode = scenePassColor.add(bloom(scenePass.getTextureNode("emissive")))`.

## Errores comunes

- `three/examples/jsm/postprocessing/EffectComposer.js` → `three/addons/postprocessing/EffectComposer.js`: el especificador examples/jsm no se resuelve con el import map.
- `composer.addPass(new ShaderPass(GammaCorrectionShader))` → `composer.addPass(new OutputPass())`: GammaCorrectionShader solo aplica la función de transferencia sRGB, mientras que OutputPass aplica el tone mapping del renderer, la exposición y el espacio de color de salida, y cierra todas las cadenas; solo los pases que necesitan entrada sRGB, como FXAAPass, van después.
- `composer.addPass(bloomPass); composer.render();` → `composer.addPass(bloomPass); composer.addPass(new OutputPass()); composer.render();`: los búferes del composer son lineales y, sin OutputPass, el tone mapping y la conversión a sRGB se omiten o se aplican de forma desigual.
- `composer.addPass(fxaaPass); composer.addPass(outputPass);` → `composer.addPass(outputPass); composer.addPass(fxaaPass);`: FXAA necesita entrada sRGB, así que va después de OutputPass, mientras que SMAA trabaja en espacio lineal y debe ejecutarse antes.
- `new ShaderPass(FXAAShader)` → `new FXAAPass()`: FXAAPass fija por sí mismo su uniform de resolución a partir del tamaño del composer (pixel ratio incluido); un valor puesto a mano es incorrecto en pantallas HiDPI.
- `new FilmPass(0.35, 0.5, 648, false)` → `new FilmPass(0.35, false)`: la firma es (intensity, grayscale); los argumentos de las líneas de escaneo no existen.
- `new HalftonePass(width, height, params)` → `new HalftonePass(params)`: los argumentos width y height se eliminaron en r175; las opciones van en el único objeto params.
- `new SMAAPass(width, height)` → `new SMAAPass()`: los argumentos de tamaño se eliminaron en r175; el composer dimensiona el pase.
- `new UnrealBloomPass(new THREE.Vector2(window.innerWidth / 2, window.innerHeight / 2), 1.5, 0.4, 0.85)` → `new UnrealBloomPass(new THREE.Vector2(window.innerWidth, window.innerHeight), 1.5, 0.4, 0.85)`: addPass redimensiona de inmediato el pase al tamaño del composer, deshaciendo el truco de la mitad de resolución.
- `bloomPass.resolution.set(width, height)` → `composer.setSize(width, height)`: UnrealBloomPass lee su resolución solo en el constructor; el composer redimensiona el pase y sus mips.
- `bloomPass.renderToScreen = false` → `bloomComposer.renderToScreen = false`: el composer reasigna renderToScreen en cada pase habilitado en cada fotograma, así que solo el interruptor a nivel de composer mantiene el resultado fuera de la pantalla.
- `requestAnimationFrame(animate)` → `renderer.setAnimationLoop(animate)`: la documentación de ambos renderers lo aconseja frente a un bucle manual, y entrega los fotogramas a la sesión WebXR cuando esta arranca.
- `clock.getElapsedTime()` → `timer.getElapsed()`: Clock está obsoleto desde r183; crea un THREE.Timer, llama a timer.connect(document) una vez y a timer.update() antes de leerlo en cada fotograma.
- `composer.render(); renderer.render(scene, camera);` → `bloomComposer.render(); finalComposer.render();`: el segundo renderer.render borra el canvas y elimina la salida del composer; el bloom selectivo mezcla la textura de bloom mediante un segundo composer.
- `const renderer = new THREE.WebGLRenderer({ antialias: true }); renderer.setEffects([bloomPass]);` → `const renderer = new THREE.WebGLRenderer({ antialias: true, outputBufferType: THREE.HalfFloatType }); renderer.setEffects([bloomPass]);`: setEffects() requiere un búfer de salida HalfFloatType o FloatType; con el valor por defecto registra un error y no aplica ningún efecto.
- `renderer.setEffects([bloomPass, new OutputPass(), new FXAAPass()])` → `renderer.setEffects([bloomPass])`: la vía integrada aplica el tone mapping y el espacio de color una sola vez, tras los efectos, así que un OutputPass en la lista los aplica dos veces (avisa) y un FXAAPass sin él recibe entrada lineal; aplica antialiasing con `antialias: true`.
- `import { bloom } from "three/tsl"` → `import { bloom } from "three/addons/tsl/display/BloomNode.js"`: three/tsl exporta pass, mrt y renderOutput; los nodos de efectos viven en los addons.
- `new THREE.PostProcessing(renderer)` → `new THREE.RenderPipeline(renderer)`: renombrado desde PostProcessing en r183; el nombre antiguo sobrevive solo como alias obsoleto que emite un aviso.
- `renderPipeline.outputNode = bloom(scenePassColor)` → `renderPipeline.outputNode = scenePassColor.add(bloom(scenePassColor))`: bloom() devuelve solo el resplandor, así que por sí solo la escena nunca se dibuja.
- `renderPipeline.outputNode = fxaa(scenePassColor)` → `renderPipeline.outputColorTransform = false; renderPipeline.outputNode = fxaa(renderOutput(scenePass));`: FXAA necesita entrada sRGB, pero el outputColorTransform por defecto aplica tone mapping y conversión después de él.
- `renderPipeline.outputNode = scenePassColor.add(dof(scenePassColor, scenePass.getViewZNode()))` → `renderPipeline.outputNode = dof(scenePassColor, scenePass.getViewZNode())`: dof devuelve la imagen terminada, así que sumarle el color de la escena dibuja la escena dos veces.
- `await renderPipeline.renderAsync()` → `renderPipeline.render()`: renderAsync está obsoleto desde r181; llama una vez a `await renderer.init()` en la configuración y renderiza de forma síncrona.
- `aoPass.distanceFallOff.value = 2` → `aoPass.radius.value = 0.2`: distanceExponent y distanceFallOff están obsoletos desde r186 y ya no cambian el AO, así que ajusta radius y scale.
- `new EffectComposer(webgpuRenderer)` → `new THREE.RenderPipeline(webgpuRenderer)`: EffectComposer y sus pases solo funcionan con WebGLRenderer; los efectos de WebGPURenderer son nodos TSL sobre un RenderPipeline.

## Véase también

- `references/fundamentals.md` — creación del renderer, dimensionado, espacios de color y bucle de animación.
- `references/shaders.md` — creación de GLSL ShaderMaterial y el lenguaje de nodos TSL para efectos personalizados.
- `references/textures.md` — render targets y uso de una imagen postprocesada como textura.
