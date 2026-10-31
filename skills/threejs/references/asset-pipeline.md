# Pipeline de recursos de Three.js

Orientado a three.js r186. Los ejemplos usan WebGLRenderer; la sección de WebGPU y TSL usa WebGPURenderer.

## Inicio rápido

Comprime desde la línea de comandos y luego carga el resultado. Ejecuta `inspect` antes y después para ver lo que ha ahorrado la pasada:

```bash
npx @gltf-transform/cli inspect model.glb
npx @gltf-transform/cli optimize model.glb model.opt.glb --compress draco --texture-compress webp --texture-size 2048
npx @gltf-transform/cli inspect model.opt.glb
```

La salida con Draco necesita un DRACOLoader conectado; las texturas WebP las decodifica el navegador:

```javascript
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { DRACOLoader } from "three/addons/loaders/DRACOLoader.js";

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const sun = new THREE.DirectionalLight(0xffffff, 2); // los materiales PBR de glTF se ven negros sin luces ni entorno
sun.position.set(3, 5, 2);
scene.add(sun, new THREE.HemisphereLight(0xffffff, 0x444444, 1.5));

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(2, 1.5, 3);
camera.lookAt(0, 0, 0);

const gltf = await new GLTFLoader()
  .setDRACOLoader(new DRACOLoader()) // el decodificador WASM de Draco se carga desde el paquete three
  .loadAsync("model.opt.glb");
scene.add(gltf.scene);

function animate() {
  renderer.render(scene, camera);
}

renderer.setAnimationLoop(animate);
```

## Inspeccionar y validar

Nunca adivines dónde están los bytes. `inspect` imprime un resumen (generador, `extensionsUsed`, `extensionsRequired`) y una tabla para escenas, mallas, materiales, texturas y animaciones, de modo que un archivo cargado de geometría y uno cargado de texturas se distinguen a simple vista.

```bash
npx @gltf-transform/cli inspect model.glb
npx @gltf-transform/cli inspect model.opt.glb --format csv
npx @gltf-transform/cli validate model.glb --ignore ACCESSOR_WEIGHTS_NON_NORMALIZED
```

`extensionsRequired` es el contrato en tiempo de ejecución: `KHR_draco_mesh_compression`, `EXT_meshopt_compression` y `KHR_texture_basisu` se corresponden cada una con una pieza de configuración del loader (ver abajo), mientras que `KHR_mesh_quantization`, `EXT_mesh_gpu_instancing`, `EXT_texture_webp` y `EXT_texture_avif` no necesitan nada en tiempo de ejecución. `validate` ejecuta el validador oficial de glTF e informa de errores, avisos y sugerencias; termina con código distinto de cero cuando encuentra errores, así que sirve como control en CI. Los comandos de esta skill que escriben un archivo registran los tamaños de entrada y de salida al terminar; haz `inspect` de la salida para ver de qué tabla vienen los ahorros.

## El comando optimize

`optimize` encadena en una sola ejecución las pasadas habituales: dedup, instance, palette, flatten, join, weld, simplify, resample, prune y sparse, luego la compresión de texturas y, por último, la compresión de geometría. Sin banderas aplica compresión meshopt y recomprime las texturas en su formato original. Los valores por defecto son agresivos pero genéricos: haz `inspect` primero y ajusta después:

```bash
# geometría draco + texturas webp, limitadas a 2048px
npx @gltf-transform/cli optimize model.glb model.opt.glb --compress draco --texture-compress webp --texture-size 2048
# texturas de GPU en lugar de tamaño de descarga, conservando todos los triángulos
npx @gltf-transform/cli optimize model.glb model.opt.glb --texture-compress ktx2 --simplify false
```

Banderas principales (los booleanos llevan un valor explícito, como `--simplify false`):

- `--compress draco|meshopt|quantize` — compresión de geometría y animación (por defecto `meshopt`).
- `--texture-compress ktx2|webp|avif` — códec de texturas (por defecto `auto`, recomprime en el formato original).
- `--texture-size <px>` — limita las dimensiones de las texturas, 2048 por defecto.
- `--simplify <bool>`, `--simplify-ratio <0-1>`, `--simplify-error <fraction>`, `--simplify-lock-border <bool>` — simplificación de mallas; ratio 0 y error 0.0001 por defecto.
- `--instance <bool>`, `--instance-min <count>` — instanciado en GPU para mallas repetidas.
- `--join <bool>`, `--join-meshes <bool>`, `--join-named <bool>`, `--flatten <bool>` — reducción de draw calls; `--join` requiere `--flatten`.
- `--weld <bool>` — fusiona vértices duplicados; `draco` suelda por sí mismo incluso con `--weld false`, mientras que `simplify` suelda solo las primitivas sin indexar, así que mantén `--weld true` al simplificar.
- `--prune <bool>`, `--resample <bool>`, `--palette <bool>`, `--sparse <bool>`, `--meshopt-level medium|high`.

Con `--texture-compress ktx2`, `optimize` elige él mismo los bitstreams: UASTC para las ranuras de normal, oclusión y metálico-rugosidad, y ETC1S para todo lo demás. Como alternativa fuera del alcance de esta skill, gltfpack cubre un terreno similar; gltf-transform es suficiente aquí.

## Compresión de geometría

Tres códecs con compromisos distintos: elige por modelo, no por proyecto:

- **Draco** (`--compress draco`, comando `draco`): comprime solo geometría de mallas triangulares; no comprime animación, morph targets, texturas, puntos ni líneas. En ejecución: DRACOLoader.
- **Meshopt** (`--compress meshopt`, comando `meshopt`): comprime geometría de puntos, líneas y triángulos, morph targets y pistas de animación, y decodifica muy rápido; combínalo con gzip o brotli sin pérdida en la red. En ejecución: MeshoptDecoder.
- **Quantize** (comando `quantize`): almacena los atributos float como enteros de 8 o 16 bits mediante KHR_mesh_quantization; ocupa menos en disco y en memoria de GPU, y no hay decodificador que configurar; GLTFLoader lee los atributos cuantizados de forma nativa.

```bash
npx @gltf-transform/cli draco model.glb model.opt.glb --method edgebreaker --quantize-position 14
npx @gltf-transform/cli meshopt model.glb model.opt.glb --level high
npx @gltf-transform/cli quantize model.glb model.opt.glb
npx @gltf-transform/cli gzip model.opt.glb
```

`gzip` escribe `model.opt.glb.gz` junto a su entrada; sírvelo con `Content-Encoding: gzip` y el navegador lo descomprime de forma transparente. Aporta poco sobre Draco o texturas JPEG, y rinde más sobre meshopt y quantize.

Haz que `draco`, `meshopt` u `optimize` sea el último comando de una cadena: cualquier otro comando que reescriba el modelo decodifica la geometría Draco y meshopt al leer el archivo (avisa con "Decoded KHR_draco_mesh_compression. Further compression will be lossy.") y la vuelve a escribir sin comprimir.

## Compresión de texturas

Son dos problemas distintos: KTX2 (Basis Universal) permanece comprimido en la memoria de la GPU allí donde la GPU admite uno de sus destinos de transcodificación (KTX2Loader recurre a RGBA sin comprimir en caso contrario) y se sube rápido, así que optimiza la memoria de GPU y el rendimiento; WebP y AVIF reducen la descarga y se descomprimen a píxeles en bruto en la memoria de GPU, donde pueden ocupar de 4 a 8 veces más.

```bash
# KTX2: ETC1S para color (más pequeño, más pérdida), UASTC para mapas de normales (más grande, más limpio)
npx @gltf-transform/cli etc1s model.glb model.opt.glb --quality 128
npx @gltf-transform/cli uastc model.glb model.opt.glb --level 4
# Tamaño de descarga: WebP o AVIF, calidad 1-100
npx @gltf-transform/cli webp model.glb model.opt.glb --quality 80
# Limita las dimensiones de las texturas PNG o JPEG; nunca las agranda
npx @gltf-transform/cli resize model.glb model.opt.glb --width 1024 --height 1024
```

La salida KTX2 (`etc1s`, `uastc` u `optimize --texture-compress ktx2`) invoca el comando `ktx` de KTX-Software (4.4.0 o posterior), así que instálalo primero; WebP y AVIF se codifican dentro del propio proceso. Los comandos sueltos `etc1s` y `uastc` convierten todas las texturas a un único bitstream; el reparto por ranura (UASTC para normal, oclusión y metálico-rugosidad, ETC1S para el resto) es lo que hace por ti `optimize --texture-compress ktx2`, y `--slots` selecciona los roles de textura por nombre cuando necesitas un reparto personalizado. En ejecución: KTX2 necesita KTX2Loader con `detectSupport`; WebP y AVIF los decodifica el navegador.

## Comandos de optimización de escena

Ejecútalos cuando `inspect` muestre que el problema son los draw calls o el número de vértices y no los bytes:

```bash
npx @gltf-transform/cli weld model.glb model.opt.glb
npx @gltf-transform/cli simplify model.glb model.opt.glb --ratio 0.5 --error 0.001
npx @gltf-transform/cli join model.glb model.opt.glb
npx @gltf-transform/cli instance model.glb model.opt.glb --min 5
npx @gltf-transform/cli dedup model.glb model.opt.glb
npx @gltf-transform/cli prune model.glb model.opt.glb
```

- `weld` fusiona vértices idénticos bit a bit e indexa la primitiva (los puntos se omiten). `draco` suelda por sí mismo; `simplify` suelda solo las primitivas sin indexar y `meshopt` ninguna, y el paso de reordenación de meshopt omite las primitivas sin indexar (avisa cuando ninguna está indexada), así que ejecuta `weld` antes de `simplify` y `meshopt`.
- `simplify` elimina triángulos, apuntando a `--ratio` (fracción de vértices que se conservan) sin superar `--error` (fracción de la extensión de la malla); `--lock-border true` preserva los bordes abiertos. Tiene pérdida.
- `join` fusiona primitivas compatibles para reducir los draw calls; ejecuta antes por sí mismo dedup y flatten. En escenas que reutilizan mucho una misma malla infla el número de vértices: usa `instance` en esos casos.
- `instance` escribe EXT_mesh_gpu_instancing para las mallas referenciadas por varios nodos (`--min` vale 5 por defecto); GLTFLoader renderiza esos lotes como un InstancedMesh sin configuración en ejecución. Omite cualquier archivo que contenga una animación, y las mallas instanciadas deben compartir materiales.
- `dedup` fusiona accesores, materiales, mallas, skins y texturas redundantes que dejan los exportadores.
- `prune` elimina las propiedades que ninguna Scene referencia, incluidas las animaciones que apuntan a algo no incluido en ninguna escena.

## Configuración del loader para cada salida

La elección del pipeline decide la configuración del loader. El decodificador Draco y el transcodificador Basis se cargan por defecto desde el paquete three: llama a `setDecoderPath` o `setTranscoderPath` solo cuando alojes tú mismo esos archivos, y entonces fija la ruta a la versión de three que publiques. Crea un único KTX2Loader para la aplicación y compártelo entre los GLTFLoader: cada instancia activa carga su propio transcodificador y sus workers, y three.js avisa cuando hay varias activas.

```javascript
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { DRACOLoader } from "three/addons/loaders/DRACOLoader.js";
import { KTX2Loader } from "three/addons/loaders/KTX2Loader.js";
import { MeshoptDecoder } from "three/addons/libs/meshopt_decoder.module.js";

// Conecta todos los códecs que pueda emitir el pipeline; si falta uno, lanza un error al cargar
const gltfLoader = new GLTFLoader()
  .setDRACOLoader(new DRACOLoader()) // KHR_draco_mesh_compression
  .setMeshoptDecoder(MeshoptDecoder) // EXT_meshopt_compression
  .setKTX2Loader(new KTX2Loader().detectSupport(renderer)); // KHR_texture_basisu

const gltf = await gltfLoader.loadAsync("model.opt.glb");
scene.add(gltf.scene);
```

Qué lanza cada pieza que falta: un archivo Draco sin DRACOLoader ("No DRACOLoader instance provided"), un archivo meshopt sin decodificador ("setMeshoptDecoder must be called before loading compressed files"), un archivo KTX2 sin KTX2Loader ("setKTX2Loader must be called before loading KTX2 textures"), y un KTX2Loader que nunca ejecutó `detectSupport` ("Missing initialization with `.detectSupport( renderer )`"). Las texturas WebP y AVIF, los atributos cuantizados y EXT_mesh_gpu_instancing no necesitan nada de esto.

## Pipelines con scripts

Cuando la CLI se queda corta (valores por defecto por proyecto, CI, muchos archivos), automatiza las mismas transformaciones con el SDK. Un script de Node, que se ejecuta con `node pipeline.mjs`:

```javascript
// deps: @gltf-transform/core @gltf-transform/extensions @gltf-transform/functions draco3dgltf
import { NodeIO } from "@gltf-transform/core";
import { ALL_EXTENSIONS } from "@gltf-transform/extensions";
import { dedup, prune, weld, draco } from "@gltf-transform/functions";
import draco3d from "draco3dgltf";

const io = new NodeIO()
  .registerExtensions(ALL_EXTENSIONS) // una extensión omitida se descarta al leer, o lanza un error si es obligatoria
  .registerDependencies({
    "draco3d.decoder": await draco3d.createDecoderModule(), // lee entrada Draco
    "draco3d.encoder": await draco3d.createEncoderModule(),
  });

const document = await io.read("model.glb");
await document.transform(
  dedup(),
  weld(), // vértices compartidos, antes de la compresión
  prune(), // elimina lo que ninguna Scene referencia
  draco({ method: "edgebreaker", quantizePosition: 14 }),
);
await io.write("model.opt.glb", document);
```

La compresión se ejecuta cuando la clase de E/S escribe el archivo, así que sigue siendo el último paso. Registra todas las extensiones: la E/S escribe solo las extensiones registradas, de modo que texturas WebP o atributos cuantizados sin la suya producen un archivo inválido. Para meshopt en su lugar, añade `"meshopt.encoder": MeshoptEncoder` a `registerDependencies` después de `await MeshoptEncoder.ready` (MeshoptEncoder viene del paquete meshoptimizer) y pasa `meshopt({ encoder: MeshoptEncoder })`; la compresión de texturas en scripts usa `textureCompress({ encoder, targetFormat: "webp" })` con sharp como codificador.

## Salida para React con gltfjsx

`gltfjsx` convierte un modelo en un componente de React Three Fiber: JSX declarativo que puedes editar, en lugar de una caja negra cargada:

```bash
npx gltfjsx model.glb --transform
```

Esto escribe `Model.jsx` (un componente para @react-three/fiber; `--types` para un .tsx) y, por culpa de `--transform`, también reescribe el recurso: `model-transformed.glb` incluye materiales de paleta, mallas unidas, geometría soldada y depurada, compresión Draco y texturas recodificadas como WebP, limitadas a `--resolution` (1024 por defecto); los mapas de normales se recodifican como JPEG, limitados a 2048 px o a `--resolution`, el valor que sea mayor; y el componente generado carga ese archivo. Añade `--simplify` con `--ratio` y `--error` para simplificar. La parte del componente (Canvas, Suspense, useGLTF) corresponde a la guía references/react-three-fiber.md.

## WebGPU y TSL

Los loaders y addons de arriba son idénticos con WebGPURenderer, que renderiza por sí mismo los materiales cargados como node materials (`mesh.material` sigue siendo la clase que creó GLTFLoader). Una regla de orden: `KTX2Loader.detectSupport(renderer)` necesita el backend del renderer, así que crea el loader después de `await renderer.init()`.

```javascript
import * as THREE from "three/webgpu";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { KTX2Loader } from "three/addons/loaders/KTX2Loader.js";
// renderer es un WebGPURenderer inicializado (se esperó a su init())
const gltfLoader = new GLTFLoader()
  .setKTX2Loader(new KTX2Loader().detectSupport(renderer));
const gltf = await gltfLoader.loadAsync("model.opt.glb");
scene.add(gltf.scene);
```

## Errores comunes

- `import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js"` → `import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js"`: el especificador three/examples/jsm no se resuelve con el import map que documenta three.js.
- `npx @gltf-transform/cli optimize model.glb out.glb --compress ktx2` → `npx @gltf-transform/cli optimize model.glb out.glb --compress draco --texture-compress ktx2`: los códecs de texturas pertenecen a `--texture-compress`; `--compress` admite draco, meshopt o quantize.
- `npx @gltf-transform/cli draco model.glb a.glb && npx @gltf-transform/cli webp a.glb out.glb --quality 80` → `npx @gltf-transform/cli webp model.glb a.glb --quality 80 && npx @gltf-transform/cli draco a.glb out.glb`: todos los comandos salvo `draco`, `meshopt` y `optimize` decodifican la geometría Draco y meshopt al leer un archivo y la escriben sin comprimir, así que la compresión de geometría va la última.
- `new GLTFLoader().loadAsync("draco.glb")` → `new GLTFLoader().setDRACOLoader(new DRACOLoader()).loadAsync("draco.glb")`: cargar un archivo KHR_draco_mesh_compression sin DRACOLoader lanza "No DRACOLoader instance provided".
- `new GLTFLoader().loadAsync("meshopt.glb")` → `new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).loadAsync("meshopt.glb")`: un archivo EXT_meshopt_compression lanza "setMeshoptDecoder must be called before loading compressed files".
- `new GLTFLoader().loadAsync("ktx2.glb")` → `new GLTFLoader().setKTX2Loader(new KTX2Loader().detectSupport(renderer)).loadAsync("ktx2.glb")`: un archivo KHR_texture_basisu lanza "setKTX2Loader must be called before loading KTX2 textures".
- `setKTX2Loader(new KTX2Loader())` → `setKTX2Loader(new KTX2Loader().detectSupport(renderer))`: un KTX2Loader que nunca ejecutó detectSupport lanza "Missing initialization with `.detectSupport( renderer )`".
- `dracoLoader.setDecoderPath(cdnPathFromAnotherRelease)` → `new GLTFLoader().setDRACOLoader(new DRACOLoader())`: el decodificador Draco se carga por defecto desde el paquete three, y una ruta fijada a otra versión no coincide con el loader.
- `dracoLoader.setDecoderConfig({ type: "js" })` → `new DRACOLoader()`: setDecoderConfig está obsoleto desde r185; sin él, DRACOLoader usa el decodificador WASM donde exista WebAssembly.
- `ktx2Loader.detectSupportAsync(renderer)` → `await renderer.init(); ktx2Loader.detectSupport(renderer);`: detectSupportAsync está obsoleto desde r181; llama a detectSupport una vez inicializado el renderer.
- `npx @gltf-transform/cli dequantize model.glb out.glb` → `npx @gltf-transform/cli quantize model.glb out.glb`: GLTFLoader lee los atributos KHR_mesh_quantization sin configuración en ejecución, así que usa dequantize solo cuando tu propio código necesite datos de vértices float en unidades del modelo: los atributos cuantizados contienen enteros normalizados, y las posiciones cuantizadas se reescalan con la transformación de su nodo.

## Véase también

- `references/loaders.md` - la parte de ejecución: progreso de carga, caché, clonado de modelos con skinning y liberación de lo que produce el pipeline.
- `references/react-three-fiber.md` - la aplicación React alrededor de un componente gltfjsx: Canvas, useGLTF, Suspense y helpers de drei.
- `references/performance.md` - medir lo que ha aportado el pipeline: draw calls, memoria de GPU y renderer.info.
