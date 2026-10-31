# Texturas en Three.js

Pensado para three.js r186. Los ejemplos usan WebGLRenderer; la sección de WebGPU y TSL usa WebGPURenderer.

## Inicio rápido

```javascript
import * as THREE from "three";

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(0, 0, 2);

// Las imágenes de color deben etiquetarse como sRGB o se ven demasiado brillantes y desvaídas
const texture = new THREE.TextureLoader().load("diffuse.jpg");
texture.colorSpace = THREE.SRGBColorSpace;

const mesh = new THREE.Mesh(
  new THREE.PlaneGeometry(2, 2),
  new THREE.MeshBasicMaterial({ map: texture }),
);
scene.add(mesh);

renderer.setAnimationLoop(animate);

function animate() {
  mesh.rotation.z += 0.01;
  renderer.render(scene, camera);
}
```

## Carga

```javascript
// load() devuelve la textura de inmediato; su imagen llega de forma asíncrona
const texture = new THREE.TextureLoader().load("diffuse.jpg");
texture.colorSpace = THREE.SRGBColorSpace;
mesh.material.map = texture; // antes del primer render; después, pon también mesh.material.needsUpdate = true

// Cuando el siguiente paso necesita la imagen ya cargada, espera con await
const colorMap = await new THREE.TextureLoader().loadAsync("diffuse.jpg");
colorMap.colorSpace = THREE.SRGBColorSpace;
```

El parámetro `onProgress` de TextureLoader no está soportado y nunca se dispara; un `LoadingManager` informa del progreso a medida que termina cada archivo:

```javascript
const manager = new THREE.LoadingManager();
manager.onProgress = (url, loaded, total) => console.log(`${loaded}/${total}: ${url}`);
const loader = new THREE.TextureLoader(manager);
```

## Espacio de color

La gestión del color está activada por defecto y toda textura empieza en `NoColorSpace`:

- Las imágenes de color LDR reciben `SRGBColorSpace`: `map`, `emissiveMap`, `specularMap`, los mapas de color de sheen y de specular, los matcaps LDR, y el canvas o vídeo usado como color.
- Los datos escalares mantienen `NoColorSpace`: mapas de normal, bump, displacement, roughness, metalness, oclusión ambiental y alpha.
- Los entornos HDR son `LinearSRGBColorSpace`; los loaders HDR lo establecen ellos mismos. GLTFLoader establece los espacios de color de las texturas que carga.

```javascript
const colorMap = new THREE.TextureLoader().load("color.jpg");
colorMap.colorSpace = THREE.SRGBColorSpace; // imagen de color creada por un artista

const normalMap = new THREE.TextureLoader().load("normal.jpg");
// normalMap se queda en NoColorSpace: son datos, no color
```

## Transformación: wrap, repeat, offset, rotation

```javascript
const texture = new THREE.TextureLoader().load("diffuse.jpg");

// El mosaico requiere wrapping de repetición; el valor por defecto estira los píxeles del borde
texture.wrapS = THREE.RepeatWrapping;
texture.wrapT = THREE.RepeatWrapping;
texture.repeat.set(4, 4); // mosaico de 4x4

texture.offset.set(0.5, 0.5); // desplazamiento en unidades UV
texture.center.set(0.5, 0.5); // pivote de la rotación
texture.rotation = Math.PI / 4; // radianes
```

`MirroredRepeatWrapping` repite en mosaico con un volteo especular en cada repetición.

## Filtrado, mipmaps, anisotropía

```javascript
const texture = new THREE.TextureLoader().load("diffuse.jpg");

// Minificación (muchos píxeles de textura por píxel de pantalla)
texture.minFilter = THREE.LinearMipmapLinearFilter; // por defecto: mezcla trilineal entre niveles de mip
texture.minFilter = THREE.NearestFilter; // aspecto de píxel duro, muestrea solo el nivel base

// Magnificación (textura ampliada en pantalla)
texture.magFilter = THREE.LinearFilter; // por defecto
texture.magFilter = THREE.NearestFilter; // pixelado

// Los mipmaps se generan siempre que generateMipmaps sea true, sean cuales sean los filtros.
// Desactiva la generación para ahorrar memoria (sprites de UI, texturas de datos):
texture.generateMipmaps = false;
texture.minFilter = THREE.LinearFilter; // y no pidas un filtro de mipmap

// Más nítida en ángulos rasantes; limita al máximo que soporte el hardware
texture.anisotropy = renderer.capabilities.getMaxAnisotropy();
```

## Tipos de textura

Clase base a partir de cualquier elemento de imagen:

```javascript
const image = new Image();
image.src = "sprite.png";

const imageTexture = new THREE.Texture(image);
imageTexture.colorSpace = THREE.SRGBColorSpace;
image.onload = () => (imageTexture.needsUpdate = true); // sube la textura cuando ya existan los píxeles
```

`DataTexture` a partir de píxeles en bruto de un array tipado. Sus valores por defecto difieren de los de `Texture`: `NearestFilter` en ambos filtros, `flipY` en false, mipmaps desactivados:

```javascript
const size = 256;
const data = new Uint8Array(size * size * 4); // RGBA, un byte por canal
for (let i = 0; i < size; i++) {
  for (let j = 0; j < size; j++) {
    const index = (i * size + j) * 4;
    data[index] = i;
    data[index + 1] = j;
    data[index + 2] = 128;
    data[index + 3] = 255;
  }
}
const dataTexture = new THREE.DataTexture(data, size, size);
dataTexture.needsUpdate = true;
```

`CanvasTexture` para texturas dibujadas dinámicamente (pone `needsUpdate` al construirse):

```javascript
const canvas = document.createElement("canvas");
canvas.width = 256;
canvas.height = 256;
const ctx = canvas.getContext("2d");
ctx.fillStyle = "#404040";
ctx.fillRect(0, 0, 256, 256);
ctx.fillStyle = "#ffffff";
ctx.font = "48px sans-serif";
ctx.fillText("Hello", 40, 150);

const canvasTexture = new THREE.CanvasTexture(canvas);
canvasTexture.colorSpace = THREE.SRGBColorSpace; // los colores del canvas son sRGB

// tras cada redibujado del canvas:
canvasTexture.needsUpdate = true;
```

`VideoTexture` para un `HTMLVideoElement` en reproducción (se vuelve a subir en cada fotograma, mipmaps desactivados):

```javascript
const video = document.createElement("video");
video.src = "video.mp4";
video.loop = true;
video.muted = true;
video.play();

const videoTexture = new THREE.VideoTexture(video);
videoTexture.colorSpace = THREE.SRGBColorSpace;
```

`VideoFrameTexture` para WebCodecs: cada fotograma decodificado se inserta a mano:

```javascript
const frameTexture = new THREE.VideoFrameTexture();
frameTexture.colorSpace = THREE.SRGBColorSpace;
const decoder = new VideoDecoder({
  output(frame) {
    if (frameTexture.image instanceof VideoFrame) frameTexture.image.close(); // libera el fotograma reemplazado, o la decodificación se atasca
    frameTexture.setFrame(frame);
  },
  error: (e) => console.error(e),
});
```

`HTMLTexture` dibuja un elemento HTML mediante la API HTML-in-Canvas del navegador: el renderer mueve el elemento a su propio canvas y lo vuelve a subir en los eventos de pintado; donde el navegador carezca de esa API, la textura se queda vacía.

## Texturas comprimidas (KTX2)

```javascript
import { KTX2Loader } from "three/addons/loaders/KTX2Loader.js";

const ktx2Loader = new KTX2Loader();
// Sin llamada a setTranscoderPath: el transcodificador se carga desde el paquete three.
// Defínelo solo si alojas tú mismo los decodificadores, fijado a esta versión.
ktx2Loader.detectSupport(renderer); // obligatorio antes de cargar; funciona con ambos renderers

const compressedMap = await ktx2Loader.loadAsync("diffuse.ktx2");
// colorSpace sale de la función de transferencia del archivo; no hay que establecer nada a mano
```

Basis Universal KTX2 se transcodifica a un formato comprimido que la GPU soporta: subidas más pequeñas y menos memoria que PNG o JPEG, que se suben sin comprimir (donde la GPU no soporta ninguno de los destinos, KTX2Loader recurre también a RGBA sin comprimir). Las texturas comprimidas no se pueden voltear ni generar mipmaps en la subida: `flipY` se queda en false, así que crea el archivo con la orientación que esperan tus UV, y los mipmaps deben ir incrustados en el archivo.

## Mapas de entorno

Cube maps (el loader etiqueta el resultado como sRGB por sí mismo):

```javascript
const cubeTexture = new THREE.CubeTextureLoader().load([
  "px.jpg", "nx.jpg", // +X, -X
  "py.jpg", "ny.jpg", // +Y, -Y
  "pz.jpg", "nz.jpg", // +Z, -Z
]);

scene.background = cubeTexture;
scene.environment = cubeTexture; // ilumina materiales Standard y Physical (WebGLRenderer también Lambert y Phong)
```

Archivos HDR equirectangulares: establece `mapping` y luego asigna; ambos renderers prefiltran el entorno por sí mismos:

```javascript
import { HDRLoader } from "three/addons/loaders/HDRLoader.js";

const env = await new HDRLoader().loadAsync("environment.hdr");
env.mapping = THREE.EquirectangularReflectionMapping; // sin él el fondo se dibuja como un quad plano a pantalla completa
scene.environment = env;
scene.background = env;
```

`EXRLoader` (`three/addons/loaders/EXRLoader.js`) carga archivos `.exr` del mismo modo y `UltraHDRLoader` carga JPEG Ultra HDR; ambos establecen su propio espacio de color lineal.

Controles a nivel de escena:

```javascript
scene.environmentIntensity = 0.5; // atenúa la iluminación basada en imagen
scene.environmentRotation.y = Math.PI / 4;

scene.backgroundBlurriness = 0.5; // 0-1
scene.backgroundIntensity = 1.0;
scene.backgroundRotation.y = Math.PI;
```

Ambos renderers convierten internamente un entorno equirectangular en un cube map con una textura mayor (mejor muestreo, más memoria); cuando la memoria importe, entrega un archivo equirectangular de menor resolución.

`PMREMGenerator` es para entornos generados: una escena como `RoomEnvironment` capturada con `fromScene`:

```javascript
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";

const pmrem = new THREE.PMREMGenerator(renderer);
const room = new RoomEnvironment();
scene.environment = pmrem.fromScene(room, 0.04).texture;
room.dispose(); // libera las geometrías y materiales de la sala
pmrem.dispose();
```

No pases un archivo equirectangular cargado por PMREMGenerator «para mejores reflejos»: la asignación directa con `mapping` establecido produce el mismo prefiltrado.

## Render targets

```javascript
const renderTarget = new THREE.WebGLRenderTarget(512, 512);
const rtScene = new THREE.Scene(); // no debe contener el mesh que muestrea el target
rtScene.add(new THREE.Mesh(new THREE.BoxGeometry(), new THREE.MeshNormalMaterial())); // sin iluminar, visible sin luces

renderer.setRenderTarget(renderTarget);
renderer.render(rtScene, camera);
renderer.setRenderTarget(null); // de vuelta al canvas

// la salida es una textura como cualquier otra
mesh.material.map = renderTarget.texture;
```

Buffer de profundidad como textura:

```javascript
const depthTarget = new THREE.WebGLRenderTarget(512, 512);
depthTarget.depthTexture = new THREE.DepthTexture(512, 512); // tipo por defecto UnsignedIntType
```

MSAA y múltiples adjuntos:

```javascript
// MSAA: se resuelve automáticamente en .texture tras renderizar
const msaaTarget = new THREE.WebGLRenderTarget(512, 512, { samples: 4 });

// MRT: N adjuntos de color, que se leen de vuelta con .textures
const mrtTarget = new THREE.WebGLRenderTarget(512, 512, { count: 2 });
const firstAttachment = mrtTarget.textures[0];
const secondAttachment = mrtTarget.textures[1];
```

## Reflejos dinámicos

```javascript
const cubeRenderTarget = new THREE.WebGLCubeRenderTarget(256, {
  generateMipmaps: true,
  minFilter: THREE.LinearMipmapLinearFilter,
});
const cubeCamera = new THREE.CubeCamera(0.1, 1000, cubeRenderTarget);
scene.add(cubeCamera);

mesh.material.envMap = cubeRenderTarget.texture;

// en cada fotograma: oculta el mesh reflectante para que no se vea a sí mismo
mesh.visible = false;
cubeCamera.position.copy(mesh.position);
cubeCamera.update(renderer, scene);
mesh.visible = true;
```

## Canales UV

Toda textura de material con mapeado UV muestrea el atributo UV elegido por `texture.channel`: `0` lee `uv` (el valor por defecto), `1` lee `uv1`, `2` lee `uv2`, `3` lee `uv3`. Así, `aoMap` y `lightMap` funcionan con el juego `uv` por defecto; un juego desenvuelto aparte va en `uv1` apuntando la textura hacia él:

```javascript
const aoTexture = new THREE.TextureLoader().load("ao.jpg");

const geometry = new THREE.BoxGeometry(1, 1, 1);
const uvAttribute = geometry.attributes.uv;
const aoUvs = new Float32Array(uvAttribute.count * 2); // rellénalo con el segundo desenvolvido
geometry.setAttribute("uv1", new THREE.BufferAttribute(aoUvs, 2));

const material = new THREE.MeshStandardMaterial({ aoMap: aoTexture });
material.aoMap.channel = 1; // muestrea "uv1" en lugar de "uv"
const aoMesh = new THREE.Mesh(geometry, material);
scene.add(aoMesh);
```

## Atlas de texturas

Una imagen, muchos sprites, cada uno seleccionado con offset y repeat:

```javascript
const atlas = await new THREE.TextureLoader().loadAsync("atlas.png");
atlas.colorSpace = THREE.SRGBColorSpace;
// el filtrado y los mipmaps muestrean a través de los bordes de los sprites: deja relleno alrededor de cada sprite

// un clon por sprite: los clones comparten la fuente de la imagen, así que WebGLRenderer la sube una sola vez
function spriteTexture(row, col, gridSize = 2) {
  const sprite = atlas.clone();
  sprite.offset.set(col / gridSize, 1 - (row + 1) / gridSize);
  sprite.repeat.set(1 / gridSize, 1 / gridSize);
  return sprite;
}

mesh.material.map = spriteTexture(0, 0); // sprite superior izquierdo de una hoja de 2x2
```

## Slots del material Standard

Convenciones de canal que conviene conocer: `aoMap` lee el rojo, `roughnessMap` lee el verde, `metalnessMap` lee el azul (así que sirve una única imagen empaquetada de oclusión-rugosidad-metalicidad); `alphaMap` lee el verde.

```javascript
const colorMap = new THREE.TextureLoader().load("color.jpg");
const emissiveMap = new THREE.TextureLoader().load("emissive.jpg");
const normalMap = new THREE.TextureLoader().load("normal.jpg");
colorMap.colorSpace = THREE.SRGBColorSpace;
emissiveMap.colorSpace = THREE.SRGBColorSpace;
// normalMap mantiene NoColorSpace, igual que los mapas de roughness, metalness, ao, alpha y displacement

const material = new THREE.MeshStandardMaterial({
  map: colorMap,
  normalMap: normalMap,
  normalScale: new THREE.Vector2(1, 1),
  emissiveMap: emissiveMap,
  emissive: 0xffffff, // distinto de negro, para que el emissive map contribuya
  roughness: 1, // multiplicadores escalares de los mapas correspondientes
  metalness: 0,
});

material.aoMap = new THREE.TextureLoader().load("ao.jpg");
material.aoMapIntensity = 1;
```

`alphaMap` surte efecto con `transparent: true` (mezclado) o `alphaTest` (recortado); `displacementMap` se escala con `displacementScale` y `displacementBias` y requiere un mesh subdividido; `normalMapType` vale por defecto `TangentSpaceNormalMap`, pon `ObjectSpaceNormalMap` para normal maps en espacio de objeto.

## Liberación y memoria

`texture.dispose()` libera la subida a la GPU una vez que ninguna otra textura sin liberar la comparte (los clones del atlas de arriba comparten una); el objeto de imagen permanece. Libera solo las texturas que ningún otro material siga usando:

```javascript
function disposeMaterial(material) {
  for (const key of Object.keys(material)) {
    const value = material[key];
    if (value && value.isTexture) {
      value.dispose();
    }
  }
  material.dispose();
}
```

```javascript
console.log(renderer.info.memory.textures); // número de texturas actualmente en la GPU
console.log(renderer.capabilities.maxTextureSize); // mayor dimensión soportada
```

Comparte una misma instancia de textura entre materiales en lugar de cargarla por mesh. Los tamaños que no son potencia de dos no son problema: WebGL 2 soporta mipmaps y wrapping de repetición en ellos.

## WebGPU y TSL

```javascript
import * as THREE from "three/webgpu";
import { texture, uv } from "three/tsl";

const renderer = new THREE.WebGPURenderer({ antialias: true });
await renderer.init(); // antes de cualquier otro uso del renderer
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x111111); // el canvas de WebGPU empieza transparente

const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(0, 0, 2);

const map = new THREE.TextureLoader().load("diffuse.jpg");
map.colorSpace = THREE.SRGBColorSpace;
map.anisotropy = renderer.getMaxAnisotropy(); // no hay objeto capabilities en WebGPU

const mesh = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.MeshBasicNodeMaterial());
mesh.material.colorNode = texture(map, uv().mul(0.5).add(0.25)); // transformación UV personalizada en TSL: la mitad central, ampliada 2x
scene.add(mesh);

renderer.setAnimationLoop(animate);

function animate() {
  mesh.rotation.z += 0.01;
  renderer.render(scene, camera);
}
```

Muestreo en TSL: `texture(map)` usa `uv()` más el offset/repeat/rotation propios de la textura; un nodo explícito se hace cargo de las coordenadas por completo. Los slots clásicos (`map`, `normalMap`, `roughnessMap`, `aoMap`) funcionan sin cambios en los materiales de nodos; `colorNode` sirve para muestreo personalizado.

```javascript
import * as THREE from "three/webgpu";
import { texture, uv } from "three/tsl";
const map = new THREE.TextureLoader().load("diffuse.jpg");
map.colorSpace = THREE.SRGBColorSpace;
mesh.material.colorNode = texture(map); // uv() más el offset/repeat/rotation de la textura
mesh.material.colorNode = texture(map, uv(1)); // nodo explícito: muestrea el atributo "uv1"
```

`KTX2Loader.detectSupport(renderer)` consulta las características del dispositivo, así que llámalo después de `await renderer.init()`. Para reflejos dinámicos usa `CubeRenderTarget` (no `WebGLCubeRenderTarget`) con el mismo patrón de CubeCamera de ocultar, actualizar y mostrar.

```javascript
import * as THREE from "three/webgpu";

const cubeRenderTarget = new THREE.CubeRenderTarget(256); // sustituye a WebGLCubeRenderTarget
const cubeCamera = new THREE.CubeCamera(0.1, 1000, cubeRenderTarget);
scene.add(cubeCamera);
mesh.material.envMap = cubeRenderTarget.texture;
mesh.visible = false; // ocúltalo para que el mesh no se refleje a sí mismo
cubeCamera.position.copy(mesh.position);
cubeCamera.update(renderer, scene);
mesh.visible = true;
```

## Errores comunes

- `geometry.setAttribute("uv2", geometry.attributes.uv)` → `material.aoMap = aoTexture;`: aoMap muestrea el atributo elegido por `texture.channel` (0 por defecto, `uv`), así que no necesita ningún atributo extra y `uv2` solo lo leen las texturas cuyo `channel` es 2; solo un desenvolvido horneado aparte va en `uv1`, con `aoTexture.channel = 1`.
- `new RGBELoader()` → `new HDRLoader()`: renombrado de RGBELoader a HDRLoader en r180; la clase antigua aún funciona pero registra un aviso de obsolescencia.
- `import { EXRLoader } from "three/examples/jsm/loaders/EXRLoader.js"` → `import { EXRLoader } from "three/addons/loaders/EXRLoader.js"`: los import maps del navegador mapean `three/addons/` a examples/jsm/ y no definen ninguna clave `three/examples/`, así que la ruta de examples no se resuelve allí.
- `texture.encoding = THREE.sRGBEncoding` → `texture.colorSpace = THREE.SRGBColorSpace`: `encoding` y la constante `sRGBEncoding` se eliminaron; `colorSpace` las sustituyó.
- `const texture = loader.load("color.jpg")` → `const texture = loader.load("color.jpg"); texture.colorSpace = THREE.SRGBColorSpace;`: una imagen de color LDR dejada en `NoColorSpace` se ve demasiado brillante y desvaída.
- `texture.minFilter = THREE.LinearFilter; // sin mipmaps` → `texture.generateMipmaps = false;`: los mipmaps se generan siempre que `generateMipmaps` sea true, sea cual sea el filtro, así que LinearFilter por sí solo sigue subiéndolos.
- `texture.generateMipmaps = false; texture.wrapS = THREE.ClampToEdgeWrapping; // tamaño que no es potencia de dos` → `texture.wrapS = THREE.RepeatWrapping;`: WebGL 2 soporta mipmaps y wrapping de repetición en texturas cuyo tamaño no es potencia de dos, así que no hay que desactivar nada para ellas.
- `texture.anisotropy = renderer.capabilities.getMaxAnisotropy()` → `texture.anisotropy = renderer.getMaxAnisotropy()`: WebGPURenderer no tiene objeto `capabilities`; esta es la llamada en WebGPU.
- `material.envMapIntensity = 0.5` → `scene.environmentIntensity = 0.5`: `envMapIntensity` escala solo el `envMap` propio del material, no `scene.environment`.
- `scene.environment = pmrem.fromEquirectangular(hdr).texture` → `hdr.mapping = THREE.EquirectangularReflectionMapping; scene.environment = hdr;`: el renderer prefiltra por sí mismo un entorno equirectangular, así que pasar a mano un archivo cargado por PMREM no aporta nada.
- `scene.background = hdr` → `hdr.mapping = THREE.EquirectangularReflectionMapping; scene.background = hdr;`: sin `mapping`, una textura equirectangular se dibuja como un quad plano en espacio de pantalla en lugar de un entorno envolvente.
- `ktx2Loader.detectSupportAsync(renderer)` → `await renderer.init(); ktx2Loader.detectSupport(renderer);`: la variante asíncrona quedó obsoleta en r181, y la detección de soporte necesita el dispositivo inicializado.
- `ktx2Loader.setTranscoderPath("libs/basis/")` → `const ktx2Loader = new KTX2Loader(); ktx2Loader.detectSupport(renderer);`: el transcodificador se carga desde el paquete, así que solo hace falta una ruta cuando lo alojas tú mismo, fijado a three@0.186.0.
- `new THREE.WebGLMultipleRenderTargets(width, height, 2)` → `new THREE.WebGLRenderTarget(width, height, { count: 2 })`: eliminado en r162; los adjuntos son `renderTarget.textures[0..count-1]`.
- `new THREE.WebGLCubeRenderTarget(256)` → `new THREE.CubeRenderTarget(256)`: en WebGPURenderer usa `CubeRenderTarget` importado de `three/webgpu`; `WebGLCubeRenderTarget` es exclusivo de WebGL.
- `loader.load(url, onLoad, onProgress, onError)` → `manager.onProgress = (url, loaded, total) => console.log(url, loaded, total)`: el parámetro `onProgress` de TextureLoader no está soportado y nunca se dispara.
- `mesh.material.map = texture; // después de que el mesh se haya renderizado` → `mesh.material.map = texture; mesh.material.needsUpdate = true;`: WebGLRenderer construye el shader de un material para los mapas que tiene en su primer render, así que un `map` añadido más tarde permanece invisible hasta que se reconstruye el shader, cosa que fuerza `needsUpdate`.
- `normalMap.colorSpace = THREE.LinearSRGBColorSpace` → `normalMap.colorSpace = THREE.NoColorSpace`: los mapas de normal, roughness, metalness, ao, alpha y displacement contienen datos, no color, así que mantienen el `NoColorSpace` por defecto.
- `const texture = await new Promise((resolve, reject) => loader.load(url, resolve, undefined, reject))` → `const texture = await loader.loadAsync(url)`: `loadAsync` es esa promesa, integrada en la clase base `Loader`.
- `cubeCamera.update(renderer, scene)` → `mesh.visible = false; cubeCamera.update(renderer, scene); mesh.visible = true;`: mientras es visible, el mesh reflectante se dibuja dentro del cube map que lee su propio `envMap`.

## Ver también

- `references/materials.md`: propiedades de material, blending y materiales físicos más allá de los slots de textura.
- `references/loaders.md`: loading managers, modelos glTF y la familia de loaders en general.
- `references/shaders.md`: muestreo de texturas con GLSL personalizado en WebGLRenderer.
- `references/lighting.md`: iluminación de entorno y unidades de luz.
- `references/asset-pipeline.md`: codificar las texturas de un modelo a KTX2, WebP o AVIF con gltf-transform.
