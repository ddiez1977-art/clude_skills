# Cargadores (loaders) de Three.js

Orientado a three.js r186. Los ejemplos usan WebGLRenderer; la sección de WebGPU y TSL usa WebGPURenderer.

## Inicio rápido

```javascript
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture; // los materiales PBR de glTF se ven negros sin luces ni entorno

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(2, 1.5, 3);
camera.lookAt(0, 0, 0);

const gltf = await new GLTFLoader().loadAsync("model.glb");
scene.add(gltf.scene);

function animate() {
  renderer.render(scene, camera);
}

renderer.setAnimationLoop(animate);
```

## LoadingManager

Un único manager coordina varios loaders e informa del progreso combinado. `loadAsync` sigue rechazando la promesa si falla; además se dispara `manager.onError`.

```javascript
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const manager = new THREE.LoadingManager();

manager.onStart = (url, loaded, total) => {
  console.log(`Started loading: ${url}`);
};

manager.onProgress = (url, loaded, total) => {
  console.log(`Loading: ${((loaded / total) * 100).toFixed(1)}%`);
};

manager.onLoad = () => {
  console.log("All assets loaded");
};

manager.onError = (url) => {
  console.error(`Error loading: ${url}`);
};

const gltfLoader = new GLTFLoader(manager);
const textureLoader = new THREE.TextureLoader(manager);

// onLoad se dispara cuando todos los elementos rastreados han terminado
await Promise.all([
  gltfLoader.loadAsync("model.glb"),
  textureLoader.loadAsync("texture.jpg"),
  textureLoader.loadAsync("normal.jpg"),
]);
```

`manager.abort()` cancela las peticiones en curso de los loaders que cargan mediante FileLoader (modelos, HDR, EXR, KTX2). Los loaders que cargan mediante un elemento de imagen HTML, como TextureLoader, lo ignoran.

```javascript
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const manager = new THREE.LoadingManager();
const timeoutId = setTimeout(() => manager.abort(), 30000);

try {
  const gltf = await new GLTFLoader(manager).loadAsync("model.glb");
  scene.add(gltf.scene);
} catch (error) {
  console.error(error);
} finally {
  clearTimeout(timeoutId);
}
```

## Carga de texturas

`TextureLoader.load()` devuelve la textura de inmediato y la rellena cuando la imagen se decodifica; asígnala enseguida y el primer render la recoge. Añadir un mapa a un material que ya se renderizó sin él requiere `material.needsUpdate = true`. `onProgress` nunca se llama en la carga de imágenes.

```javascript
new THREE.TextureLoader().load(
  "texture.jpg",
  (map) => {
    map.colorSpace = THREE.SRGBColorSpace; // un mapa de color; los mapas escalares conservan NoColorSpace
    mesh.material.map = map;
    mesh.material.needsUpdate = true; // antes el material se renderizaba sin mapa
  },
  undefined, // onProgress: no se admite en la carga de imágenes
  (error) => {
    console.error("Could not load texture", error);
  },
);
```

### Configuración de texturas

```javascript
const map = new THREE.TextureLoader().load("color.jpg");
map.colorSpace = THREE.SRGBColorSpace; // imágenes de color LDR; los mapas escalares conservan NoColorSpace

map.wrapS = THREE.RepeatWrapping; // ClampToEdgeWrapping (por defecto), RepeatWrapping, MirroredRepeatWrapping
map.wrapT = THREE.RepeatWrapping;
map.repeat.set(2, 2);
map.offset.set(0.5, 0.5);
map.rotation = Math.PI / 4;
map.center.set(0.5, 0.5);

map.minFilter = THREE.LinearMipmapLinearFilter; // por defecto
map.magFilter = THREE.LinearFilter; // por defecto; NearestFilter para un aspecto pixelado
map.anisotropy = renderer.capabilities.getMaxAnisotropy(); // texturas más nítidas en ángulos rasantes

mesh.material.map = map;
// wrap, los filtros, anisotropy, colorSpace y flipY (true por defecto) se aplican en la subida: establécelos antes del primer render o pon map.needsUpdate = true; repeat, offset, rotation y center se aplican en cada fotograma
```

Espacios de color: las imágenes de color LDR (albedo, emisivo) son `SRGBColorSpace`; los mapas escalares (normal, bump, roughness, metalness, ao, alpha) conservan el `NoColorSpace` por defecto. GLTFLoader asigna los espacios de color correctos a las texturas que carga, y los loaders HDR de abajo establecen ellos mismos `LinearSRGBColorSpace`. Una textura que cargas tú mismo para el material de un modelo glTF necesita `map.flipY = false` para coincidir con las texturas que carga GLTFLoader.

### CubeTextureLoader

Para skyboxes y entornos cúbicos, seis caras en orden +X, -X, +Y, -Y, +Z, -Z; el loader establece sRGB por sí mismo.

```javascript
const cubeTexture = await new THREE.CubeTextureLoader().loadAsync([
  "px.jpg",
  "nx.jpg",
  "py.jpg",
  "ny.jpg",
  "pz.jpg",
  "nz.jpg",
]);

scene.background = cubeTexture;
scene.environment = cubeTexture;
```

## Entornos HDR

`HDRLoader` (Radiance `.hdr`) y `EXRLoader` devuelven texturas equirectangulares de coma flotante. Ambos renderers prefiltran por sí mismos un entorno equirectangular, así que no hace falta un paso PMREM para un archivo: establece `mapping` y asígnalo.

```javascript
import { HDRLoader } from "three/addons/loaders/HDRLoader.js";
import { EXRLoader } from "three/addons/loaders/EXRLoader.js";

const env = await new HDRLoader().loadAsync("environment.hdr");
env.mapping = THREE.EquirectangularReflectionMapping;
scene.environment = env;
scene.background = env; // sin mapping, una textura de fondo se dibuja como un quad plano a pantalla completa

const exr = await new EXRLoader().loadAsync("environment.exr");
exr.mapping = THREE.EquirectangularReflectionMapping;
scene.environment = exr;
```

Atenúa el entorno con `scene.environmentIntensity` (y rótalo con `scene.environmentRotation`); `material.envMapIntensity` escala solo el `envMap` propio de un material, que sigue siendo null en los modelos iluminados por `scene.environment`.

`UltraHDRLoader` lee JPEG con gain map (rango dinámico HDR con el tamaño de archivo de un JPEG) de la misma manera:

```javascript
import { UltraHDRLoader } from "three/addons/loaders/UltraHDRLoader.js";

const env = await new UltraHDRLoader().loadAsync("environment.jpg");
env.mapping = THREE.EquirectangularReflectionMapping;
scene.environment = env;
```

Usa `PMREMGenerator` para entornos generados, no para archivos:

```javascript
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";

const pmremGenerator = new THREE.PMREMGenerator(renderer);
const room = new RoomEnvironment();
scene.environment = pmremGenerator.fromScene(room, 0.04).texture;
room.dispose(); pmremGenerator.dispose(); // primero las geometrías y materiales de la sala, luego el generador
```

## glTF y GLB

El formato principal para la distribución web. El resultado incluye `scene`, `animations`, `cameras`, `asset` (versión, generador) y `userData` (datos personalizados de la herramienta de autoría).

```javascript
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const gltf = await new GLTFLoader().loadAsync("model.glb");
scene.add(gltf.scene);

if (gltf.animations.length > 0) {
  const mixer = new THREE.AnimationMixer(gltf.scene);
  mixer.clipAction(gltf.animations[0]).play();
  const timer = new THREE.Timer();
  timer.connect(document);

  function animate() {
    timer.update();
    mixer.update(timer.getDelta());
    renderer.render(scene, camera);
  }

  renderer.setAnimationLoop(animate);
}
```

### Compresión Draco, meshopt y KTX2

El decodificador Draco y el transcodificador Basis se cargan por defecto desde el paquete three; llama a `setDecoderPath` / `setTranscoderPath` solo cuando los alojes tú mismo, y entonces fija la ruta a la versión de three que publiques. Un archivo que requiere `EXT_meshopt_compression` o `KHR_meshopt_compression` falla al cargar a menos que se establezca `setMeshoptDecoder`.

```javascript
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { DRACOLoader } from "three/addons/loaders/DRACOLoader.js";
import { KTX2Loader } from "three/addons/loaders/KTX2Loader.js";
import { MeshoptDecoder } from "three/addons/libs/meshopt_decoder.module.js";

const gltfLoader = new GLTFLoader()
  .setDRACOLoader(new DRACOLoader())
  .setMeshoptDecoder(MeshoptDecoder)
  .setKTX2Loader(new KTX2Loader().detectSupport(renderer));

const gltf = await gltfLoader.loadAsync("compressed-model.glb");
scene.add(gltf.scene);
```

### Procesar el contenido cargado

```javascript
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const gltf = await new GLTFLoader().loadAsync("model.glb");
const model = gltf.scene;

model.traverse((child) => {
  if (child.isMesh) {
    child.castShadow = true; // las sombras también requieren renderer.shadowMap.enabled = true y una luz con castShadow
    child.receiveShadow = true;
  }
});

model.getObjectByName("Head"); // busca nodos por nombre

scene.environmentIntensity = 0.5; // atenúa scene.environment en esta escena

// Centra el modelo y escálalo para que quepa en una caja unidad
const box = new THREE.Box3().setFromObject(model);
const center = box.getCenter(new THREE.Vector3());
const size = box.getSize(new THREE.Vector3());
const scale = 1 / Math.max(size.x, size.y, size.z);
model.scale.setScalar(scale);
model.position.copy(center).multiplyScalar(-scale); // el desplazamiento también se escala

scene.add(model);
```

## Otros formatos de modelo

### OBJ + MTL

```javascript
import { MTLLoader } from "three/addons/loaders/MTLLoader.js";
import { OBJLoader } from "three/addons/loaders/OBJLoader.js";

const materials = await new MTLLoader().loadAsync("model.mtl");
materials.preload();

const object = await new OBJLoader().setMaterials(materials).loadAsync("model.obj");
scene.add(object);
```

### FBX

```javascript
import { FBXLoader } from "three/addons/loaders/FBXLoader.js";

const object = await new FBXLoader().loadAsync("model.fbx");
object.scale.setScalar(0.01); // los archivos FBX suelen exportarse en centímetros

const mixer = new THREE.AnimationMixer(object); // llama a mixer.update(timer.getDelta()) en cada fotograma, como en el ejemplo de glTF
if (object.animations.length > 0) mixer.clipAction(object.animations[0]).play();

scene.add(object);
```

### STL

```javascript
import { STLLoader } from "three/addons/loaders/STLLoader.js";

const geometry = await new STLLoader().loadAsync("model.stl");
scene.add(new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({ color: 0x888888 })));
scene.add(new THREE.HemisphereLight(0xffffff, 0x444444, 1));
scene.add(new THREE.DirectionalLight(0xffffff, 2)); // los materiales con iluminación se ven negros sin luces; esta ilumina desde (0, 1, 0) hacia abajo
```

### PLY

El loader respeta los tipos de datos del archivo, así que las propiedades `double` llegan como atributos respaldados por un `Float64Array`, que WebGLRenderer no puede subir; conviértelos a `Float32BufferAttribute` antes de renderizar.

```javascript
import { PLYLoader } from "three/addons/loaders/PLYLoader.js";

const geometry = await new PLYLoader().loadAsync("model.ply");

for (const name of Object.keys(geometry.attributes)) {
  const attribute = geometry.getAttribute(name);
  if (attribute.array instanceof Float64Array) {
    geometry.setAttribute(name, new THREE.Float32BufferAttribute(attribute.array, attribute.itemSize));
  }
}

if (!geometry.hasAttribute("normal")) geometry.computeVertexNormals(); // conserva las normales propias del archivo
const material = new THREE.MeshStandardMaterial({ vertexColors: geometry.hasAttribute("color") }); // vertexColors sin atributo color se renderiza en negro
scene.add(new THREE.Mesh(geometry, material));
scene.add(new THREE.HemisphereLight(0xffffff, 0x444444, 1));
scene.add(new THREE.DirectionalLight(0xffffff, 2)); // los materiales con iluminación se ven negros sin luces; esta ilumina desde (0, 1, 0) hacia abajo
```

### USD

```javascript
import { USDLoader } from "three/addons/loaders/USDLoader.js";

const model = await new USDLoader().loadAsync("model.usdz"); // archivos USD, USDA, USDC y USDZ
scene.add(model);
```

## Patrones asíncronos y fuentes personalizadas

Carga en paralelo los recursos independientes:

```javascript
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { HDRLoader } from "three/addons/loaders/HDRLoader.js";

const [model, environment, colorMap] = await Promise.all([
  new GLTFLoader().loadAsync("model.glb"),
  new HDRLoader().loadAsync("environment.hdr"),
  new THREE.TextureLoader().loadAsync("color.jpg"),
]);

environment.mapping = THREE.EquirectangularReflectionMapping;
colorMap.colorSpace = THREE.SRGBColorSpace;

scene.add(model.scene);
scene.environment = environment;
```

Analiza datos que ya tienes (un archivo descargado, un input de archivo, un registro de base de datos):

```javascript
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const response = await fetch("model.glb");
const buffer = await response.arrayBuffer();

const gltf = await new GLTFLoader().parseAsync(buffer, "");
scene.add(gltf.scene);
```

Las URL de blob y las URL de datos funcionan como URL de loader:

```javascript
async function loadTextureFromBlob(blob) {
  const url = URL.createObjectURL(blob);
  const texture = await new THREE.TextureLoader().loadAsync(url);
  URL.revokeObjectURL(url);
  return texture;
}
```

Antepón rutas y reescribe URL a través del manager:

```javascript
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const loader = new GLTFLoader();
loader.setPath("assets/models/"); // prefijo de la URL que pasas a load
loader.setResourcePath("assets/textures/"); // dónde se resuelven las referencias propias del archivo
const gltf = await loader.loadAsync("model.glb"); // carga assets/models/model.glb

const manager = new THREE.LoadingManager();
manager.setURLModifier((url) => url.replace("assets/", "https://cdn.example.com/assets/"));
const cdnGltf = await new GLTFLoader(manager).loadAsync("assets/models/model.glb"); // se obtiene de https://cdn.example.com/assets/models/model.glb
```

Activa la caché compartida para servir desde memoria las URL repetidas:

```javascript
THREE.Cache.enabled = true;
THREE.Cache.clear(); // vacíala cuando necesites forzar recargas
```

Mantén las cargas pequeñas (Draco o meshopt para la geometría, KTX2 para las texturas, producidos como se explica en references/asset-pipeline.md) y muestra una malla provisional mientras se carga el modelo real, sustituyéndola cuando la carga termine.

## Clonado y liberación de recursos

`Object3D.clone()` sobre un modelo con skinning comparte el esqueleto: todas las copias siguen ligadas a los huesos del original, de modo que siguen al original e ignoran su propia animación. Usa `SkeletonUtils.clone()` para las instancias.

```javascript
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import * as SkeletonUtils from "three/addons/utils/SkeletonUtils.js";

const gltf = await new GLTFLoader().loadAsync("character.glb");
scene.add(gltf.scene);

const copy = SkeletonUtils.clone(gltf.scene);
scene.add(copy);
```

`object.dispose()` libera el estado del lado del renderer solo de ese objeto (enlaces de WebGPU, buffers de InstancedMesh) y no recorre los hijos ni libera geometría, materiales o texturas; recorre el subárbol:

```javascript
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

const gltf = await new GLTFLoader().loadAsync("model.glb");
const model = gltf.scene;
scene.add(model);

// ... más tarde
scene.remove(model);
model.traverse((child) => {
  child.dispose(); // estado del renderer por objeto: buffers de InstancedMesh, enlaces de WebGPU
  if (child.geometry) { // mallas, líneas y puntos
    child.geometry.dispose();
    const materials = Array.isArray(child.material) ? child.material : [child.material];
    for (const material of materials) {
      for (const value of Object.values(material)) {
        if (value?.isTexture) value.dispose();
      }
      material.dispose();
    }
  }
});
```

## WebGPU y TSL

```javascript
import * as THREE from "three/webgpu";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
const renderer = new THREE.WebGPURenderer({ antialias: true });
await renderer.init(); // antes de cualquier otro uso del renderer
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x111827); // el canvas de WebGPU es transparente por defecto
scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;
const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(2, 1.5, 3);
camera.lookAt(0, 0, 0);
const gltf = await new GLTFLoader().loadAsync("model.glb"); // los materiales cargados se convierten automáticamente en node materials
scene.add(gltf.scene);
function animate() { renderer.render(scene, camera); } renderer.setAnimationLoop(animate);
```

- `ktx2Loader.detectSupport(renderer)` y los métodos de `PMREMGenerator` (`fromScene`, `fromEquirectangular`, `fromCubemap`) lanzan un error antes de `await renderer.init()`. La anisotropía máxima es `renderer.getMaxAnisotropy()`; `renderer.capabilities` no existe en WebGPURenderer.
- Gaussian splats: `SPLATLoader`, `SPZLoader`, `KSPLATLoader` y `GaussianSplatPLYLoader` cargan datos para `new GaussianSplat(data)` de `three/addons/objects/GaussianSplat.js`, que requiere WebGPURenderer.

## Errores comunes

- `import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js"` → `import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js"`: el especificador `three/examples/jsm/` no se resuelve con el import map que documenta three.js.
- `import { RGBELoader } from "three/addons/loaders/RGBELoader.js"` → `import { HDRLoader } from "three/addons/loaders/HDRLoader.js"`: renombrado desde RGBELoader en r180; la clase antigua emite un aviso en cada construcción.
- `new Promise((resolve, reject) => loader.load(url, resolve, undefined, reject))` → `loader.loadAsync(url)`: todos los loaders ya implementan loadAsync, que rechaza la promesa si hay error.
- `material.map = new THREE.TextureLoader().load("color.jpg")` → `const map = new THREE.TextureLoader().load("color.jpg"); map.colorSpace = THREE.SRGBColorSpace; material.map = map;`: un mapa de color cargado tiene NoColorSpace por defecto y se ve desvaído.
- `normalMap.colorSpace = THREE.LinearSRGBColorSpace` → `normalMap.colorSpace = THREE.NoColorSpace`: los mapas escalares (normal, bump, roughness, metalness, ao, alpha) conservan NoColorSpace; LinearSRGBColorSpace es para datos de color lineales.
- `texture.encoding = THREE.sRGBEncoding` → `texture.colorSpace = THREE.SRGBColorSpace`: encoding y sRGBEncoding ya no existen, así que la línea antigua deja el mapa en NoColorSpace y se ve desvaído.
- `child.material.envMapIntensity = 0.5` → `scene.environmentIntensity = 0.5`: envMapIntensity escala solo material.envMap, que sigue siendo null cuando el modelo está iluminado por scene.environment.
- `scene.environment = pmremGenerator.fromEquirectangular(hdrTexture).texture` → `hdrTexture.mapping = THREE.EquirectangularReflectionMapping; scene.environment = hdrTexture;`: ambos renderers ejecutan ese paso PMREM por sí mismos para una textura equirectangular, así que el paso manual solo añade código y un render target que liberar.
- `scene.background = hdrTexture` → `hdrTexture.mapping = THREE.EquirectangularReflectionMapping; scene.background = hdrTexture;`: sin el mapping, una textura de fondo se dibuja como un quad plano a pantalla completa.
- `ktx2Loader.setTranscoderPath(pathFromAnotherRelease)` → `const ktx2Loader = new KTX2Loader().detectSupport(renderer)`: el transcodificador Basis y el decodificador Draco se cargan por defecto desde el paquete three; una ruta fijada a otra versión no coincide con el loader.
- `ktx2Loader.detectSupportAsync(renderer)` → `await renderer.init(); ktx2Loader.detectSupport(renderer);`: detectSupportAsync está obsoleto desde r181; llama a detectSupport una vez inicializado el renderer.
- `renderer.capabilities.getMaxAnisotropy()` → `renderer.getMaxAnisotropy()`: capabilities existe solo en WebGLRenderer; con WebGPURenderer usa el método del renderer.
- `scene.add(new THREE.Mesh(await new PLYLoader().loadAsync("scan.ply"), material))` → `const geometry = await new PLYLoader().loadAsync("scan.ply"); for (const [name, a] of Object.entries(geometry.attributes)) if (a.array instanceof Float64Array) geometry.setAttribute(name, new THREE.Float32BufferAttribute(a.array, a.itemSize)); scene.add(new THREE.Mesh(geometry, material));`: PLYLoader conserva las propiedades double como atributos Float64, que WebGLRenderer no puede subir (lanza Unsupported buffer data format).
- `gltf.scene.clone()` → `SkeletonUtils.clone(gltf.scene)`: Object3D.clone() comparte el esqueleto, así que cada copia sigue ligada a los huesos del original y sigue su animación.
- `gltf.scene.dispose()` → `gltf.scene.traverse((child) => { child.geometry?.dispose(); for (const material of [child.material ?? []].flat()) { for (const value of Object.values(material)) if (value?.isTexture) value.dispose(); material.dispose(); } child.dispose(); })`: Object3D.dispose() libera el estado del renderer solo de ese objeto, nunca su geometría, materiales ni texturas, y material.dispose() no libera las texturas del material.
- `fetch(url, { signal: controller.signal })` → `setTimeout(() => manager.abort(), 30000)`: los loaders se cancelan mediante su LoadingManager, que aborta las peticiones FileLoader en curso.
- `new USDZLoader()` → `new USDLoader()`: obsoleto desde r179; USDLoader lee USD, USDA, USDC y USDZ.

## Véase también

- `references/fundamentals.md` - configuración del renderer, gestión del redimensionado y el andamiaje de la aplicación alrededor de los recursos cargados
- `references/textures.md` y `references/materials.md` - propiedades de las texturas y espacios de color, y ajuste de los materiales con los que vienen los modelos cargados
- `references/asset-pipeline.md` - compresión y optimización de archivos glTF antes de que lleguen a estos loaders
- `references/animation.md` - AnimationMixer, clips y reproducción de mallas con skinning
