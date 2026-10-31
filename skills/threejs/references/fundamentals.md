# Fundamentos de Three.js

Pensado para three.js r186. Los ejemplos usan WebGLRenderer; la sección de WebGPU y TSL usa WebGPURenderer.

## Inicio rápido

```javascript
import * as THREE from "three";

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x111318);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 1.5, 5);

const cube = new THREE.Mesh(
  new THREE.BoxGeometry(1, 1, 1),
  new THREE.MeshStandardMaterial({ color: 0x3a86ff }),
);
scene.add(cube);
const light = new THREE.DirectionalLight(0xffffff, 2);
light.position.set(3, 4, 5); // ilumina desde su posición hacia el origen
scene.add(light);
scene.add(new THREE.AmbientLight(0xffffff, 0.4));

const timer = new THREE.Timer();
timer.connect(document); // congela el delta mientras la pestaña está oculta

function animate() {
  timer.update(); // avanza el timer lo primero en cada fotograma
  cube.rotation.y += timer.getDelta(); // segundos desde el fotograma anterior
  renderer.render(scene, camera);
}
renderer.setAnimationLoop(animate);

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

Sin un bundler, el navegador carga three.js como módulos ES mediante un import map; este es el mapa para los ejemplos de WebGLRenderer de arriba:

```html
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.186.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.186.0/examples/jsm/"
  }
}
</script>
```

Para trabajar con WebGPURenderer, mapea las cuatro claves: `three.tsl.js` importa `three/webgpu`, así que el mapa falla sin esa entrada:

```html
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.186.0/build/three.webgpu.js",
    "three/webgpu": "https://cdn.jsdelivr.net/npm/three@0.186.0/build/three.webgpu.js",
    "three/tsl": "https://cdn.jsdelivr.net/npm/three@0.186.0/build/three.tsl.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.186.0/examples/jsm/"
  }
}
</script>
```

## Escena

```javascript
const scene = new THREE.Scene();

scene.background = new THREE.Color(0x111318); // color sólido
scene.fog = new THREE.Fog(0x111318, 1, 100); // niebla lineal: near, far
scene.fog = new THREE.FogExp2(0x111318, 0.02); // niebla exponencial: densidad (elige una)
```

- `scene.background` también acepta un `CubeTexture`, o una `Texture` cuyo `mapping` sea `THREE.EquirectangularReflectionMapping`; una textura sin mapping se dibuja como un quad plano que llena la pantalla, no como un skybox.
- `scene.environment` ilumina `MeshStandardMaterial` y `MeshPhysicalMaterial` en ambos renderers, y `MeshLambertMaterial` y `MeshPhongMaterial` solo en WebGLRenderer. `scene.environmentIntensity` lo escala; `material.envMapIntensity` escala únicamente `material.envMap`. Consulta references/loaders.md para los entornos HDR.

## Cámaras

### PerspectiveCamera

```javascript
// PerspectiveCamera(fov en grados, aspect, near, far)
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 5, 10);
camera.lookAt(0, 0, 0); // gira la cámara para que mire al objetivo

camera.fov = 60;
camera.updateProjectionMatrix(); // obligatorio tras cambiar fov, aspect, near o far
```

### OrthographicCamera

```javascript
// OrthographicCamera(left, right, top, bottom, near, far); tamaño del frustum en unidades del mundo
const aspect = window.innerWidth / window.innerHeight;
const frustumHeight = 10;
const camera = new THREE.OrthographicCamera(
  (-frustumHeight * aspect) / 2,
  (frustumHeight * aspect) / 2,
  frustumHeight / 2,
  -frustumHeight / 2,
  0.1,
  1000,
);
// al redimensionar: recalcula left y right con el nuevo aspect y llama a camera.updateProjectionMatrix()
```

### ArrayCamera

```javascript
// Renderiza la escena una vez por subcámara, cada una en su propio viewport.
// Las unidades del viewport en WebGLRenderer son píxeles del drawing buffer (tamaño CSS × pixel ratio);
// WebGPURenderer multiplica por sí mismo los píxeles CSS por el pixel ratio.
const width = window.innerWidth;
const height = window.innerHeight;
const dpr = renderer.getPixelRatio();
const cameras = [];
for (let i = 0; i < 4; i++) {
  const subCamera = new THREE.PerspectiveCamera(75, width / height, 0.1, 100);
  subCamera.viewport = new THREE.Vector4(
    ((i % 2) * width * dpr) / 2,
    (Math.floor(i / 2) * height * dpr) / 2,
    (width * dpr) / 2,
    (height * dpr) / 2,
  );
  subCamera.position.set(-2 + (i % 2) * 4, 1.5, 6);
  subCamera.lookAt(0, 0, 0);
  subCamera.updateMatrixWorld(); // las subcámaras no son hijas del grafo de escena; actualízalas cuando se muevan
  cameras.push(subCamera);
}
const arrayCamera = new THREE.ArrayCamera(cameras);
arrayCamera.position.set(0, 1.5, 6); // WebGLRenderer hace culling de cada viewport con el frustum de esta cámara (fov 50, aspect 1 por defecto); WebGPURenderer usa el frustum de cada subcámara
renderer.render(scene, arrayCamera);
```

### CubeCamera

```javascript
const cubeRenderTarget = new THREE.WebGLCubeRenderTarget(256);
const cubeCamera = new THREE.CubeCamera(0.1, 1000, cubeRenderTarget);
scene.add(cubeCamera);

const chrome = new THREE.Mesh(
  new THREE.SphereGeometry(1, 32, 16),
  new THREE.MeshStandardMaterial({ color: 0xffffff, metalness: 1, roughness: 0 }),
);
chrome.material.envMap = cubeRenderTarget.texture;
scene.add(chrome);

// en cada fotograma: oculta el mesh reflectante, o se dibujará dentro del mapa que muestrea
chrome.visible = false;
cubeCamera.position.copy(chrome.position);
cubeCamera.update(renderer, scene);
chrome.visible = true;
```

Con WebGPURenderer, crea el target con `CubeRenderTarget` de `three/webgpu` en lugar de `WebGLCubeRenderTarget`.

## WebGLRenderer

```javascript
const renderer = new THREE.WebGLRenderer({
  canvas: document.querySelector("#canvas"), // reutiliza un canvas existente; omítelo para crear uno
  antialias: true, // MSAA
  alpha: true, // deja ver el fondo de la página a través del canvas
  stencil: true, // el stencil está desactivado por defecto; actívalo para técnicas de stencil
  powerPreference: "high-performance",
  preserveDrawingBuffer: true, // conserva el drawing buffer para readPixels / capturas de pantalla
});

renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); // limita el fill rate en pantallas de alta densidad
renderer.setSize(window.innerWidth, window.innerHeight);

renderer.toneMapping = THREE.ACESFilmicToneMapping; // o AgXToneMapping, NeutralToneMapping; NoToneMapping es el valor por defecto
renderer.toneMappingExposure = 1.0;
// renderer.outputColorSpace es SRGBColorSpace por defecto; déjalo como está

renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap; // el valor por defecto, ya suave; VSMShadowMap y BasicShadowMap son las alternativas

renderer.setClearColor(0x000000, 0); // un alpha de limpieza de 0 mantiene transparente el canvas con alpha: true
renderer.render(scene, camera);
```

## Objetos

### Object3D

Clase base de Mesh, Group, Light y Camera.

```javascript
const obj = new THREE.Object3D();
const child = new THREE.Object3D();

obj.position.set(1, 2, 3); // traslación
obj.rotation.set(0, Math.PI / 4, 0); // ángulos de Euler en radianes; se mantiene sincronizado con quaternion
obj.quaternion.setFromAxisAngle(new THREE.Vector3(0, 1, 0), Math.PI / 4); // la misma rotación como cuaternión
obj.scale.set(1, 1, 1);

obj.getWorldPosition(new THREE.Vector3()); // las consultas en espacio mundo reciben un vector destino donde escribir
obj.getWorldQuaternion(new THREE.Quaternion());
obj.getWorldDirection(new THREE.Vector3()); // el eje +Z en espacio mundo; las cámaras devuelven su dirección de vista (−Z)

obj.add(child); // reasigna el padre de child; también lo quita de su padre anterior
obj.attach(child); // reasigna el padre y conserva la transformación mundial de child; add() conserva la local
obj.remove(child);
obj.visible = false; // oculta todo el subárbol

obj.layers.enable(1); // AÑADE la capa 1; set(1) reemplazaría la máscara y dejaría fuera la capa 0
obj.layers.disable(1);
obj.layers.test(camera.layers); // true cuando el objeto comparte una capa con la cámara

obj.traverse((descendant) => {
  if (descendant.isMesh) descendant.castShadow = true; // visita primero obj y luego todos sus descendientes
});

// las actualizaciones de matrices son automáticas mientras matrixAutoUpdate sea true (el valor por defecto)
obj.matrixAutoUpdate = false;
obj.updateMatrix(); // compone obj.matrix y marca la matriz mundial como sucia
// si en su lugar escribes obj.matrix directamente, marca tú mismo la matriz mundial:
obj.matrixWorldNeedsUpdate = true;
```

### Group y Mesh

```javascript
const group = new THREE.Group(); // un Object3D cuya función es contener hijos
const ball = new THREE.Mesh(new THREE.SphereGeometry(0.5), new THREE.MeshStandardMaterial());
group.add(ball);
group.rotation.y = Math.PI / 4; // transforma todo el subárbol
scene.add(group);
```

```javascript
const mesh = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshStandardMaterial());
scene.add(mesh);

// un material por grupo de la geometría; BoxGeometry tiene seis (+x, −x, +y, −y, +z, −z)
// un grupo cuyo materialIndex no tiene material no se dibuja
const faceColors = [0xff0000, 0x00ff00, 0x0000ff, 0xffff00, 0xff00ff, 0x00ffff];
const dice = new THREE.Mesh(
  new THREE.BoxGeometry(1, 1, 1),
  faceColors.map((color) => new THREE.MeshStandardMaterial({ color })),
);

mesh.castShadow = true; // este objeto proyecta sombras
mesh.receiveShadow = true; // este objeto muestra sombras
mesh.frustumCulled = true; // por defecto: se omite cuando su esfera envolvente sale del frustum de la cámara
mesh.renderOrder = 10; // se renderiza más tarde dentro del mismo grupo de transparencia
```

## Sistema de coordenadas

Mano derecha, con +Y hacia arriba: +X a la derecha, +Y arriba, +Z hacia el espectador. Una cámara en el origen sin rotación mira hacia −Z.

```javascript
const axesHelper = new THREE.AxesHelper(5); // X rojo, Y verde, Z azul; 5 = longitud de los ejes
scene.add(axesHelper);
```

## Utilidades matemáticas

### Vector3

```javascript
const a = new THREE.Vector3(1, 0, 0);
const b = new THREE.Vector3(0, 1, 0);
const c = a.clone(); // nuevo vector con los mismos valores

a.copy(b); // a pasa a ser b
a.add(b); // in situ: a = a + b
a.sub(b);
a.multiplyScalar(2);
a.divideScalar(2);
a.lerp(b, 0.5); // se mueve hasta la mitad del camino hacia b
a.normalize(); // longitud unitaria
a.negate();
a.cross(b); // producto vectorial, escrito en a (regla de la mano derecha)

const len = a.length();
const lenSq = a.lengthSq(); // compara longitudes sin raíz cuadrada
const dist = a.distanceTo(b);
const dot = a.dot(b); // > 0 mismo semiespacio, < 0 opuesto, 0 perpendicular
const angle = a.angleTo(b); // radianes

a.applyQuaternion(new THREE.Quaternion());
a.applyMatrix4(new THREE.Matrix4());
a.project(camera); // posición mundial a coordenadas de dispositivo normalizadas
a.unproject(camera); // coordenadas de dispositivo normalizadas de vuelta al mundo
```

### Matrix4, Quaternion, Euler

```javascript
const m = new THREE.Matrix4();
m.identity();
m.makeTranslation(1, 2, 3);
m.makeRotationY(Math.PI / 4);
m.makeScale(2, 2, 2);

const position = new THREE.Vector3();
const quaternion = new THREE.Quaternion();
const scale = new THREE.Vector3(1, 1, 1);
m.compose(position, quaternion, scale); // construye a partir de los componentes de la transformación
m.decompose(position, quaternion, scale); // los lee de vuelta

m.multiply(new THREE.Matrix4()); // m = m * other (other se aplica primero)
m.premultiply(new THREE.Matrix4()); // m = other * m
m.invert();
m.lookAt(new THREE.Vector3(0, 0, 1), new THREE.Vector3(), new THREE.Vector3(0, 1, 0)); // eye, target, up

const q = new THREE.Quaternion();
q.setFromEuler(new THREE.Euler(0, Math.PI / 2, 0, "YXZ")); // el orden de Euler importa, XYZ es el valor por defecto
q.setFromAxisAngle(new THREE.Vector3(0, 1, 0), Math.PI / 4);
q.setFromRotationMatrix(m);
q.slerp(new THREE.Quaternion(), 0.5); // interpolación esférica, escrita en q
q.invert();
```

### Color

```javascript
const color = new THREE.Color(0xff0000); // número hexadecimal
const sky = new THREE.Color("#87ceeb"); // también nombres de color y "rgb(255, 0, 0)"

color.setHex(0x0000ff);
color.setRGB(1, 0.5, 0); // 0–1 en el espacio de color de trabajo lineal; el hex y las cadenas CSS son sRGB
color.setRGB(1, 128 / 255, 0, THREE.SRGBColorSpace); // componentes sRGB, el mismo color que 0xff8000
color.setHSL(0.5, 1, 0.5); // tono, saturación y luminosidad en 0–1, también lineal salvo que se indique un espacio de color
color.lerp(sky, 0.5); // interpola hacia el destino, escrito en color
color.multiplyScalar(2); // escala los componentes
```

### MathUtils

```javascript
const clamped = THREE.MathUtils.clamp(15, 1, 10); // 10
const mixed = THREE.MathUtils.lerp(0, 10, 0.5); // 5
const mapped = THREE.MathUtils.mapLinear(0.5, 0, 1, 0, 100); // 50
const radians = THREE.MathUtils.degToRad(90);
const degrees = THREE.MathUtils.radToDeg(Math.PI);
const random = THREE.MathUtils.randFloat(1, 10);
const eased = THREE.MathUtils.smoothstep(0.5, 0, 1); // curva suavizada de 0 a 1
```

## Loading Manager

```javascript
const manager = new THREE.LoadingManager();
manager.onStart = (url, loaded, total) => console.log(`iniciado ${url}`);
manager.onProgress = (url, loaded, total) => console.log(`${loaded}/${total} ${url}`);
manager.onLoad = () => console.log("todos los elementos cargados");
manager.onError = (url) => console.error(`error en ${url}`);

const loader = new THREE.TextureLoader(manager); // cualquier loader acepta un manager
```

## Limpieza

```javascript
scene.remove(mesh);
// libera geometría, materiales y texturas solo cuando nada más los siga usando
mesh.geometry.dispose();
const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material];
for (const material of materials) {
  for (const value of Object.values(material)) {
    if (value?.isTexture) value.dispose(); // material.dispose() no toca sus texturas
  }
  material.dispose();
}
mesh.dispose(); // libera el estado del renderer que se guarda solo para este objeto

renderer.setAnimationLoop(null); // detiene el bucle
renderer.dispose(); // libera los recursos de GPU del renderer; el contexto WebGL sigue vivo
renderer.forceContextLoss(); // libera también el contexto cuando se descarta el canvas
```

`Object3D.dispose()` libera el estado del renderer por objeto (los bindings de WebGPURenderer, los buffers de instancias de InstancedMesh en WebGLRenderer); no visita a los hijos ni libera la geometría, el material o las texturas. Para desmontar un subárbol, recórrelo con `traverse` y libera cada mesh como se muestra arriba. Una subclase personalizada de Object3D que sobrescriba `dispose()` debe llamar a `super.dispose()`. `timer.dispose()` desconecta un timer conectado.

## Rendimiento

- El frustum culling comprueba una esfera envolvente, no la caja envolvente: `geometry.boundingSphere` para un mesh normal, el propio `boundingSphere` del objeto para InstancedMesh, SkinnedMesh y BatchedMesh. Ambas se calculan una sola vez, así que tras editar posiciones llama a `geometry.computeBoundingSphere()`, y tras mover instancias o huesos lejos de su posición inicial llama a `object.computeBoundingSphere()`, o los objetos visibles quedarán descartados.
- Fusiona la geometría estática que comparte material en un solo mesh, y usa `InstancedMesh` para muchas copias de un mismo objeto (references/geometry.md).
- Cambia de mesh según la distancia con `LOD`; el renderer llama a `update(camera)` por ti en cada fotograma.
- En WebGLRenderer, `renderer.info.render.calls` cuenta las draw calls de la última llamada a `render()` (si hay varias pasadas por fotograma, pon `renderer.info.autoReset = false` y llama a `renderer.info.reset()` una vez por fotograma), y `renderer.info.memory` las geometrías y texturas vivas; consúltalos tras fusionar meshes o liberar objetos.

```javascript
import * as BufferGeometryUtils from "three/addons/utils/BufferGeometryUtils.js";

// las entradas deben tener el mismo conjunto de atributos
const merged = BufferGeometryUtils.mergeGeometries([
  new THREE.BoxGeometry(1, 1, 1),
  new THREE.SphereGeometry(1, 32, 16),
]);

const lod = new THREE.LOD();
lod.addLevel(new THREE.Mesh(new THREE.SphereGeometry(1, 32, 16)), 0); // distancia 0: detalle completo
lod.addLevel(new THREE.Mesh(new THREE.SphereGeometry(1, 12, 8)), 20);
lod.addLevel(new THREE.Mesh(new THREE.SphereGeometry(1, 6, 4)), 60);
scene.add(lod);
```

## WebGPU y TSL

```javascript
import * as THREE from "three/webgpu";

const renderer = new THREE.WebGPURenderer({ antialias: true });
await renderer.init(); // debe completarse antes de cualquier otro uso del renderer
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x111318); // el canvas de WebGPU es transparente por defecto

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 1.5, 5);

const cube = new THREE.Mesh(
  new THREE.BoxGeometry(1, 1, 1),
  new THREE.MeshStandardNodeMaterial({ color: 0x3a86ff }),
);
scene.add(cube);
const light = new THREE.DirectionalLight(0xffffff, 2);
light.position.set(3, 4, 5); // ilumina desde su posición hacia el origen
scene.add(light);
scene.add(new THREE.AmbientLight(0xffffff, 0.4));

const timer = new THREE.Timer();
timer.connect(document);

function animate() {
  timer.update();
  cube.rotation.y += timer.getDelta();
  renderer.render(scene, camera);
}
renderer.setAnimationLoop(animate);
```

- `renderer.render()` lanza una excepción hasta que `await renderer.init()` haya terminado. `setAnimationLoop` también ejecutaría el init, pero haz `await init()` justo después de construir el renderer, antes de que el código de configuración lo toque: el fallback a WebGL 2 sustituye `renderer.backend` durante `init()`.
- WebGPURenderer recurre por sí mismo a WebGL 2 cuando WebGPU no está disponible; `new THREE.WebGPURenderer({ forceWebGL: true })` fuerza ese fallback, y tras `await renderer.init()`, `renderer.backend.isWebGPUBackend` indica qué backend se está usando.
- Los materiales de nodos y TSL están pensados para WebGPURenderer (con cualquiera de los dos backends). WebGLRenderer solo los renderiza mediante el addon `WebGLNodesHandler` (`three/addons/tsl/WebGLNodesHandler.js`, pasado a `renderer.setNodesHandler()`), una ayuda para la migración que no admite sombras VSM, MRT, transmisión ni la pila de postprocesado de WebGPU. ShaderMaterial y `onBeforeCompile` son exclusivos de WebGLRenderer. El shading personalizado empieza en references/shaders.md.
- Los materiales integrados como `MeshStandardMaterial` se convierten automáticamente a sus versiones de nodos; usa las clases `*NodeMaterial` cuando asignes slots de nodos.
- Aquí no existe el objeto `renderer.capabilities`: la anisotropía se obtiene con `renderer.getMaxAnisotropy()`.
- La lectura de datos desde la GPU sigue siendo asíncrona: `await renderer.getArrayBufferAsync(attribute)`.

## Errores comunes

- `renderer.shadowMap.type = THREE.PCFSoftShadowMap` → `renderer.shadowMap.type = THREE.PCFShadowMap`: obsoleto desde r182; ambos renderers avisan ahora y recurren a PCFShadowMap, que ya es suave.
- `const clock = new THREE.Clock()` → `const timer = new THREE.Timer(); timer.connect(document);`: Clock está obsoleto desde r183 y avisa al construirse; llama a `timer.update()` una vez por fotograma antes de `timer.getDelta()` o `timer.getElapsed()`.
- `requestAnimationFrame(animate)` → `renderer.setAnimationLoop(animate)`: la documentación de ambos renderers lo aconseja frente a un bucle manual, los fotogramas de WebXR solo se ejecutan a través de él, y en WebGPURenderer `render()` lanza una excepción antes del init asíncrono que realiza `setAnimationLoop`.
- `subCamera.viewport = new THREE.Vector4(0, 0, 0.5, 0.5)` → `subCamera.viewport = new THREE.Vector4(x * dpr, y * dpr, width * dpr, height * dpr)`: los viewports de ArrayCamera son píxeles del drawing buffer en WebGLRenderer (WebGPURenderer escala por sí mismo los píxeles CSS por el pixel ratio), así que las fracciones no dibujan nada.
- `cubeCamera.update(renderer, scene)` → `mesh.visible = false; cubeCamera.update(renderer, scene); mesh.visible = true;`: un mesh reflectante visible se renderiza dentro del propio cube map que su material muestrea.
- `scene.background = texture` → `texture.mapping = THREE.EquirectangularReflectionMapping; scene.background = texture`: sin un mapping equirectangular o cúbico, la textura se dibuja como un quad plano que llena la pantalla, no como un skybox.
- `import { mergeGeometries } from "three/examples/jsm/utils/BufferGeometryUtils.js"` → `import * as BufferGeometryUtils from "three/addons/utils/BufferGeometryUtils.js"`: el specifier `three/examples/jsm/` no se resuelve con el import map estándar, que mapea `three/addons/`.
- `<script src="three.min.js"></script>` → `<script type="module">import * as THREE from "three";</script>`: `build/three.js` y `build/three.min.js` se eliminaron en r161, así que en el navegador three.js se carga como módulo ES tras un import map.
- `mesh.layers.set(1)` → `mesh.layers.enable(1)`: `set` reemplaza la máscara de capas y saca al mesh de la capa 0, donde viven la cámara y las luces por defecto.
- `renderer.outputEncoding = THREE.sRGBEncoding` → `renderer.outputColorSpace = THREE.SRGBColorSpace`: la API de encoding ya no existe, y la propiedad de espacio de color ya vale `SRGBColorSpace` por defecto, así que la asignación suele ser innecesaria.
- `renderer.physicallyCorrectLights = true` → `const bulb = new THREE.PointLight(0xffffff, 100)`: las unidades de luz físicamente correctas están siempre activas y los interruptores `physicallyCorrectLights` y `useLegacyLights` ya no existen, así que borra la línea y da a las luces puntuales y focales intensidades en candelas adecuadas a su distancia (references/lighting.md).
- `material.envMapIntensity = 0.5` → `scene.environmentIntensity = 0.5`: `envMapIntensity` escala solo el `envMap` propio del material, no `scene.environment`.
- `mesh.dispose()` → `mesh.dispose(); mesh.geometry.dispose(); for (const value of Object.values(mesh.material)) if (value?.isTexture) value.dispose(); mesh.material.dispose();`: el dispose a nivel de objeto libera solo el estado del renderer por objeto, nunca la geometría, el material ni las texturas, y material.dispose() tampoco toca las texturas.
- `import { WebGLCubeRenderTarget } from "three/webgpu"` → `import { CubeRenderTarget } from "three/webgpu"`: `three/webgpu` no exporta WebGLCubeRenderTarget, que no funciona con WebGPURenderer; resérvalo para WebGLRenderer.
- `await renderer.renderAsync(scene, camera)` → `await renderer.init(); renderer.render(scene, camera)`: los métodos de render asíncronos están obsoletos desde r181; inicializa una vez y luego renderiza de forma síncrona en el bucle.

## Ver también

- `references/geometry.md`: crear y editar BufferGeometry, instancing, fusión, volúmenes envolventes.
- `references/materials.md`: elegir y configurar materiales y sus slots de textura.
- `references/textures.md`: carga de texturas, espacios de color, canales UV.
- `references/lighting.md`: tipos de luz, unidades y configuración de sombras.
- `references/animation.md`: AnimationMixer y el sistema de clips para movimiento por fotogramas clave.
- `references/interaction.md`: raycasting, eventos de puntero y controles de cámara.
- `references/loaders.md`: glTF y otros loaders de archivos, patrones de carga asíncrona.
- `references/shaders.md`: ShaderMaterial y GLSL en WebGLRenderer, materiales de nodos TSL en WebGPURenderer.
- `references/postprocessing.md`: pasadas de EffectComposer y el pipeline de render de WebGPU.
- `references/performance.md`: medir el coste por fotograma y reducir draw calls, memoria y fill rate.
- `references/react-three-fiber.md`: el mismo grafo de escena escrito como componentes de React.
