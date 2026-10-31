# Rendimiento en Three.js

Dirigido a three.js r186. Los ejemplos usan WebGLRenderer; la sección de WebGPU y TSL usa WebGPURenderer.

## Inicio rápido

```javascript
import * as THREE from "three";

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.add(new THREE.HemisphereLight(0xffffff, 0x445566, 1));
const sun = new THREE.DirectionalLight(0xffffff, 2);
sun.position.set(3, 6, 4);
scene.add(sun);

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(0, 2, 8);

const mesh = new THREE.Mesh(new THREE.SphereGeometry(1, 32, 16), new THREE.MeshStandardMaterial({ color: 0x4488ff }));
scene.add(mesh);

function animate() {
  mesh.rotation.y += 0.01;
  renderer.render(scene, camera);
  // los contadores se reinician al inicio de cada llamada a render(), así que estos cubren el fotograma recién dibujado
  console.log(`${renderer.info.render.calls} calls, ${renderer.info.render.triangles} triangles, ${renderer.info.memory.textures} textures`);
}

renderer.setAnimationLoop(animate);
```

## Mide primero

Optimiza lo que señalan los números, no lo que sospecha una corazonada. El objeto `renderer.info` de WebGLRenderer se lee después de `render()`:

```javascript
function animate() {
  renderer.render(scene, camera);
  console.table({
    calls: renderer.info.render.calls, // draw calls enviadas por este render
    triangles: renderer.info.render.triangles,
    lines: renderer.info.render.lines,
    points: renderer.info.render.points,
    geometries: renderer.info.memory.geometries, // búferes de geometría vivos en la GPU
    textures: renderer.info.memory.textures,
    programs: renderer.info.programs.length, // programas de shader compilados en la caché
  });
}

renderer.setAnimationLoop(animate);
```

Detalles que conviene conocer al leer estos datos:

- Los contadores se reinician al inicio de cada llamada a `render()` mientras `info.autoReset` sea true (el valor por defecto). Leerlos antes de `render()` da los del fotograma anterior, y un fotograma con varias llamadas a `render()` (picking, reflejos, pases de postprocesado) muestra solo los números de la última.
- El dibujado del shadow map pasa por los mismos contadores: cada luz que proyecta sombras vuelve a dibujar sus emisores desde el punto de vista de la luz dentro de `render()`, y esos dibujados aparecen en `calls` y `triangles`. Activar o desactivar `castShadow` en una luz se ve directamente aquí.
- `info.memory.geometries` e `info.memory.textures` cuentan subidas, no bytes; bajan cuando se ejecuta el `dispose()` correspondiente. Las geometrías y texturas se suben una vez y las comparten todas las mallas que las referencian.

Cuando un fotograma tiene realmente varias llamadas a `render()`, acumula tú mismo durante todo el fotograma:

```javascript
renderer.info.autoReset = false; // render() deja de borrar los contadores

function animate() {
  renderer.render(scene, camera);
  console.log(renderer.info.render.calls); // todos los renders de este fotograma, sumados
  renderer.info.reset(); // una vez por fotograma, tras el último render
}

renderer.setAnimationLoop(animate);
```

`Timer` da el intervalo entre fotogramas; hazle la media durante un segundo de fotogramas, porque los fotogramas sueltos fluctúan demasiado para compararlos. El intervalo nunca baja de un refresco de pantalla (16,7 ms a 60 Hz), así que muestra los fotogramas perdidos pero no el margen disponible; mide el lado de CPU del fotograma con `performance.now()` alrededor del trabajo:

```javascript
const timer = new THREE.Timer();
timer.connect(document); // se pausa mientras la pestaña está oculta

let interval = 0;
let cpu = 0;
let frames = 0;

function animate() {
  timer.update();
  interval += timer.getDelta(); // segundos desde el fotograma anterior, nunca menos de un refresco de pantalla
  const start = performance.now();
  renderer.render(scene, camera);
  cpu += performance.now() - start; // tiempo de CPU gastado en render(); la GPU ejecuta los comandos más tarde
  frames++;
  if (frames === 60) {
    console.log(`${((interval / frames) * 1000).toFixed(2)} ms per frame, ${(cpu / frames).toFixed(2)} ms CPU in render()`);
    interval = 0;
    cpu = 0;
    frames = 0;
  }
}

renderer.setAnimationLoop(animate);
```

Para algo más profundo que el tiempo por fotograma, usa el profiler del navegador: el panel Performance de Chrome DevTools muestra las tareas largas del hilo principal, el tiempo de scripting frente al de renderizado y el trabajo de GPU en su pista de GPU. El paquete `stats-gl` muestra una superposición de estadísticas por fotograma en vivo cuando quieres los números siempre visibles.

## Draw calls

Cada malla visible encola una draw call, o una por grupo de geometría cuando el material es un array, y dos ajustes la multiplican: un material `transparent` con `side: THREE.DoubleSide` dibuja cada malla dos veces, caras traseras y luego delanteras (`forceSinglePass: true` lo deja en una), y mientras haya a la vista algún MeshPhysicalMaterial con `transmission` mayor que 0, cada objeto opaco se dibuja una segunda vez en el búfer de transmisión. Sin esos dos casos, mil mallas de un solo material son mil draw calls; `info.render.calls` es el número a vigilar. Los reductores clásicos:

**Fusiona la geometría estática.** Muchas mallas que nunca se mueven y comparten un material se convierten en una malla y una llamada:

```javascript
import * as BufferGeometryUtils from "three/addons/utils/BufferGeometryUtils.js";

const rockGeometry = new THREE.DodecahedronGeometry(1, 0);
const transform = new THREE.Matrix4();
const parts = [];
for (let i = 0; i < 200; i++) {
  const baked = rockGeometry.clone();
  transform.setPosition((Math.random() - 0.5) * 40, 0, (Math.random() - 0.5) * 40);
  baked.applyMatrix4(transform); // hornea la colocación en los vértices
  parts.push(baked);
}
const merged = BufferGeometryUtils.mergeGeometries(parts); // las entradas necesitan atributos y estado de índice coincidentes
scene.add(new THREE.Mesh(merged, new THREE.MeshNormalMaterial())); // 200 rocas, una llamada — pero una sola esfera envolvente para todas
```

Fusionar cambia granularidad de culling por número de llamadas: la malla fusionada tiene una única esfera envolvente, así que el frustum culling es todo o nada. Mantén fusionados los grupos por tamaño de mundo, un grupo por fusión, no una sola fusión para todo un nivel.

**Instancia las repeticiones.** Una geometría dibujada muchas veces con transformaciones por instancia sigue siendo una sola llamada:

```javascript
const tree = new THREE.ConeGeometry(0.5, 2, 6);
const trees = new THREE.InstancedMesh(tree, new THREE.MeshNormalMaterial(), 500);
const placement = new THREE.Object3D();
for (let i = 0; i < 500; i++) {
  placement.position.set((Math.random() - 0.5) * 40, 1, (Math.random() - 0.5) * 40);
  placement.rotation.y = Math.random() * 6.28;
  placement.updateMatrix();
  trees.setMatrixAt(i, placement.matrix);
}
// el culling prueba una sola esfera alrededor de todas las instancias (calculada de forma perezosa en la primera prueba de culling), así que las 500 se dibujan siempre que toque la vista;
// tras mover instancias más adelante, pon trees.instanceMatrix.needsUpdate = true y llama a trees.computeBoundingSphere()
scene.add(trees);
```

**Agrupa geometrías distintas en un batch.** Muchas geometrías que comparten un material se empaquetan en búferes compartidos:

```javascript
const material = new THREE.MeshNormalMaterial();
const batchedMesh = new THREE.BatchedMesh(500, 20000, 20000, material);
const coneId = batchedMesh.addGeometry(new THREE.ConeGeometry(0.5, 2, 6));
const boxId = batchedMesh.addGeometry(new THREE.BoxGeometry(1, 1, 1));
const placement = new THREE.Matrix4();
for (let i = 0; i < 500; i++) {
  const instanceId = batchedMesh.addInstance(i % 2 ? coneId : boxId); // una geometría solo se renderiza a través de una instancia
  placement.makeTranslation((Math.random() - 0.5) * 40, 1, (Math.random() - 0.5) * 40);
  batchedMesh.setMatrixAt(instanceId, placement);
}
scene.add(batchedMesh);
```

A diferencia de InstancedMesh, hace culling y ordena cada instancia por separado (`perObjectFrustumCulled` y `sortObjects`, ambos activados por defecto). WebGLRenderer las dibuja con multi-draw en una sola llamada donde el navegador soporta `WEBGL_multi_draw`, y con un dibujado por instancia en caso contrario; el backend WebGPU emite un dibujado por instancia. `references/geometry.md` cubre ambas APIs en profundidad.

**Reduce el detalle con la distancia.** `LOD` mantiene todos los niveles como hijos y, dentro de cada `render()` (su `autoUpdate` está activado por defecto), muestra solo el nivel que corresponde a la distancia actual de la cámara, de modo que los objetos lejanos envían menos triángulos — el número de llamadas sigue igual:

```javascript
const detailMaterial = new THREE.MeshNormalMaterial();
const lod = new THREE.LOD();
lod.addLevel(new THREE.Mesh(new THREE.SphereGeometry(1, 64, 32), detailMaterial), 0); // las distancias son de cámara a objeto
lod.addLevel(new THREE.Mesh(new THREE.SphereGeometry(1, 16, 8), detailMaterial), 12);
lod.addLevel(new THREE.Mesh(new THREE.SphereGeometry(1, 8, 4), detailMaterial), 30);
scene.add(lod);
```

**Deja que el culling omita llamadas enteras.** El frustum culling está activado por defecto: antes de encolar una malla, la esfera envolvente de su geometría se prueba contra el frustum de la cámara, y si falla se elimina el dibujado por completo. Hay dos formas de perderlo sin darte cuenta: editar vértices en la CPU sin llamar a `geometry.computeBoundingSphere()` deja una esfera obsoleta — una que se quede más pequeña que los vértices movidos oculta la malla mientras sigue a la vista — y mover vértices en un shader deja intacta la esfera de la CPU, así que pon `mesh.frustumCulled = false` en esa malla concreta, no en toda la escena.

## Memoria de GPU

`info.memory.textures` cuenta texturas; las cuentas de bytes las haces tú. Una textura RGBA8 cuesta 4 bytes por píxel y, con la cadena de mips por defecto, la estimación de bytes de WebGPURenderer multiplica por 1,333 — un mapa de color de 2048 por 2048 ocupa unos 22 MB de VRAM. Tres palancas:

- **KTX2 comprimido.** Una textura KTX2 Basis Universal (ETC1S o UASTC) se transcodifica a un formato comprimido por bloques que soporte la GPU (ASTC, BC7, BC1 o BC3, ETC2, ETC1 o PVRTC) y permanece comprimida en la VRAM, en lugar de expandirse a 4 bytes por píxel como hace un PNG o un JPEG; cuando ninguno encaja con el archivo (ASTC admite solo archivos UASTC, ETC1 no tiene alfa, PVRTC necesita tamaños potencia de dos), KTX2Loader recurre a RGBA sin comprimir. Cárgala con KTX2Loader:

```javascript
import { KTX2Loader } from "three/addons/loaders/KTX2Loader.js";

const ktx2Loader = new KTX2Loader().detectSupport(renderer);
const map = await ktx2Loader.loadAsync("color.ktx2"); // una CompressedTexture para un archivo Basis Universal
map.colorSpace = THREE.SRGBColorSpace; // KTX2Loader ya lo establece a partir de la función de transferencia del archivo; esta línea solo importa para un archivo de color etiquetado como lineal
mesh.material.map = map;
mesh.material.needsUpdate = true; // antes el material se renderizaba sin mapa
```

- **Tamaño.** Una textura de 1024 es una cuarta parte de una de 2048. Crea los mapas de color al tamaño con el que aparecen en pantalla y deja que el mipmapping se ocupe de la distancia.
- **Liberación.** `geometry.dispose()` libera sus búferes de GPU de inmediato; `texture.dispose()` libera la textura de GPU una vez que ninguna otra textura sin liberar la comparte (un `texture.clone()` comparte la imagen, y su copia en la GPU mientras wrap, filtro, formato y espacio de color sigan iguales). Nada cuenta mallas, así que libera solo lo que ya no renderiza nada — una malla que aún usa una geometría o textura liberada la sube de nuevo en su siguiente render:

```javascript
scene.remove(mesh);
mesh.geometry.dispose(); // libera ya los búferes de GPU, incluso si otra malla aún usa esta geometría

// material.dispose() libera sus programas de shader (se eliminan cuando ningún material los usa), nunca sus texturas
for (const value of Object.values(mesh.material)) {
  if (value?.isTexture) value.dispose();
}
mesh.material.dispose();
mesh.dispose(); // estado del lado del renderer guardado para este único objeto

console.log(renderer.info.memory.textures); // la cuenta baja a medida que se libera cada textura
```

Para liberar todo un subárbol, recórrelo — `object.dispose()` no visita a los hijos. Con WebGPURenderer, `memory.geometries` y `memory.textures` siguen siendo cuentas, y los campos `*Size` y `memory.total` añaden estimaciones en bytes; consulta la sección de WebGPU.

## Fill rate

El fill rate es el trabajo de fragmentos: píxeles sombreados por fotograma. El búfer de dibujo mide `width × ratio` por `height × ratio` píxeles, así que el coste de sombreado crece con el cuadrado del pixel ratio — una pantalla 3× sombrea 9 veces los píxeles de una 1×. Ponle un tope:

```javascript
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
```

**Overdraw y transparencia.** La geometría opaca se dibuja primero (ordenada por grupo, orden de render, material y después distancia), la transmisiva a continuación y la transparente la última — la transparente de atrás adelante para que la mezcla (blending) componga bien. Las capas transparentes apiladas no pueden descartarse unas a otras: cada capa situada detrás de otra superficie transparente sigue sombreando sus píxeles, y una superposición transparente a pantalla completa sombrea cada píxel de la pantalla una vez más encima de la escena. Prefiere materiales opacos donde el aspecto lo permita y mantén los quads transparentes pocos y pequeños. `renderer.info` no muestra el overdraw — las llamadas y los triángulos permanecen idénticos — solo se mueve el tiempo por fotograma.

**Shadow maps.** Cada luz que proyecta sombras renderiza sus emisores en una textura de profundidad en cada fotograma mientras las actualizaciones de sombra estén activadas. Los valores por defecto son pequeños (512 por 512); súbelos sabiendo lo que haces y congélalos para el escenario estático:

```javascript
const sun = new THREE.DirectionalLight(0xffffff, 2);
sun.position.set(3, 6, 4);
sun.castShadow = true;
sun.shadow.mapSize.set(1024, 1024);
scene.add(sun);

renderer.shadowMap.enabled = true;

// escenario estático: dibuja los shadow maps una vez en lugar de en cada fotograma
renderer.shadowMap.autoUpdate = false;
renderer.shadowMap.needsUpdate = true; // renderízalos una vez más y luego congélalos

// por luz en lugar de globalmente: sun.shadow.autoUpdate = false; sun.shadow.needsUpdate = true;
```

Cada luz que proyecta sombras añade su propio pase, y esos dibujados aparecen en `info.render.calls`: vuelve a dibujar cada objeto `castShadow` dentro del frustum de su cámara de sombra, una PointLight una vez por cada cara del cubo en la que cae el objeto (hasta seis) y, con `VSMShadowMap`, también los objetos `receiveShadow`, más dos dibujados de desenfoque. Unos límites ajustados de la cámara de sombra (`sun.shadow.camera.left`, `right`, `top`, `bottom`, y después `sun.shadow.camera.updateProjectionMatrix()`) reducen los emisores dibujados; el tamaño del mapa fija el coste de relleno de cada pase.

## Trabajo de CPU en el bucle

**Transformaciones estáticas.** Cada `render()` llama a `scene.updateMatrixWorld()`, que visita todos los objetos y recompone su matriz local a partir de position, rotation y scale cuando `matrixAutoUpdate` es true (el valor por defecto). Para el escenario que nunca se mueve, compónla una sola vez:

```javascript
mesh.matrixAutoUpdate = false;
mesh.updateMatrix(); // hornea position/rotation/scale en mesh.matrix antes del primer render

// más tarde, cuando este objeto sí se mueva:
mesh.position.set(1, 2, 3);
mesh.updateMatrix(); // ahora es manual: el renderer ya no la recompone
```

**Raycasting.** `intersectObjects(objects, true)` recorre todos los descendientes de cada objeto y prueba cada uno: primero una prueba de capas, luego la esfera envolvente de la geometría y por último los triángulos. Reduce la entrada en lugar de filtrar la salida:

```javascript
const raycaster = new THREE.Raycaster();
raycaster.layers.set(1); // solo se prueban los objetos habilitados en la capa 1, antes de cualquier trabajo de geometría

const pickables = [];
scene.traverse((child) => {
  if (child.isMesh && child.userData.pickable) {
    child.layers.enable(1); // añade la capa 1 manteniendo la pertenencia a la capa 0
    pickables.push(child);
  }
});

const hits = raycaster.intersectObjects(pickables, false); // una lista explícita, sin recursión
```

Un manejador de pointermove que hace raycasting se ejecuta en cada evento, así que esto se calienta en escenas con picking. Para geometría estática grande, el paquete `three-mesh-bvh` acelera las pruebas de triángulos.

**Sin asignaciones en el bucle.** Los objetos creados en cada fotograma se convierten en basura, y las pausas de recolección aparecen como picos periódicos de fotograma. Reutiliza vectores y matrices declarados fuera del bucle:

```javascript
const timer = new THREE.Timer();
timer.connect(document);

const step = new THREE.Vector3(); // se asigna una vez y se reutiliza en cada fotograma
const target = new THREE.Vector3(0, 1, 0);

function animate() {
  timer.update();
  step.subVectors(target, mesh.position).multiplyScalar(Math.min(timer.getDelta() * 2, 1));
  mesh.position.add(step);
  renderer.render(scene, camera);
}

renderer.setAnimationLoop(animate);
```

## Bloqueos por compilación de shaders

Los programas se construyen de forma perezosa: el primer fotograma en que un material se renderiza en condiciones que no ha visto antes — un número distinto de luces, la niebla activada para él — se bloquea mientras su shader compila. Constrúyelos durante la carga:

```javascript
// durante la carga, antes del primer fotograma: compila todo con lo que se renderizará la escena
await renderer.compileAsync(scene, camera); // usa KHR_parallel_shader_compile donde esté disponible

renderer.setAnimationLoop(() => {
  renderer.render(scene, camera); // los programas de material están listos; los programas de profundidad de sombra se siguen construyendo en el primer render de sombras
});
```

`renderer.compile(scene, camera)` emite las mismas construcciones pero retorna de inmediato, así que el primer render aún espera a cualquier programa que no haya terminado; prefiere la forma asíncrona. Cambiar un ajuste que se compila dentro del shader — `transparent`, `side`, `blending`, `flatShading`, `vertexColors`, `dithering`, `premultipliedAlpha`, `alphaHash`, o añadir o quitar un mapa — requiere `material.needsUpdate = true` y construye un programa nuevo, así que evita alternarlos en tiempo de ejecución (`references/materials.md` los enumera todos).

## WebGPU y TSL

```javascript
import * as THREE from "three/webgpu";
const renderer = new THREE.WebGPURenderer({ antialias: true });
await renderer.init(); // antes de cualquier otro uso del renderer
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x111111); // el canvas de WebGPU es transparente por defecto
const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(0, 4, 18);
function animate() {
  renderer.render(scene, camera);
  // autoReset borra los contadores por fotograma en cada tick del bucle; render.calls cuenta los pases de render desde que arrancó la aplicación
  console.log(`${renderer.info.render.drawCalls} draw calls, ${renderer.info.memory.total} bytes of GPU memory`);
}
renderer.setAnimationLoop(animate);
```

El compute saca el trabajo de partículas de la CPU: sin bucle por partícula, sin resubida de búfer en cada fotograma, un solo dispatch actualiza todas las partículas:

```javascript
import * as THREE from "three/webgpu";
import { Fn, cos, hash, instanceIndex, instancedArray, sin, time, TWO_PI, vec3 } from "three/tsl";
const count = 100000;
const positionBuffer = instancedArray(count, "vec3"); // un búfer de almacenamiento que vive en la GPU
const simulate = Fn(() => {
  const rand = hash(instanceIndex);
  const angle = rand.mul(TWO_PI).add(time); // time se actualiza solo en cada fotograma
  positionBuffer.element(instanceIndex).assign(vec3(cos(angle).mul(8), sin(rand.mul(97).add(time.mul(2))).mul(2).add(2), sin(angle).mul(8)));
});
const simulateCompute = simulate().compute(count); // un hilo de compute por partícula
const material = new THREE.SpriteNodeMaterial();
material.positionNode = positionBuffer.toAttribute(); // el material lee directamente el búfer de almacenamiento
material.colorNode = vec3(1, 0.7, 0.3);
const particles = new THREE.Sprite(material);
particles.count = count; // el sprite se dibuja una vez por elemento del búfer
particles.frustumCulled = false; // el culling prueba una pequeña esfera en el origen del sprite, no las partículas
scene.add(particles);
function animate() {
  renderer.compute(simulateCompute); // la GPU actualiza el búfer y después el dibujado lo lee
  renderer.render(scene, camera);
}
renderer.setAnimationLoop(animate);
```

- Los contadores de WebGPU tienen sus propios nombres: `info.render.drawCalls` por fotograma, `info.render.calls` (pases de render: cada `render()` y los internos, como el pase de salida) e `info.calls` (llamadas de render y compute) acumulados desde que arrancó la aplicación, `info.compute.frameCalls` por fotograma, e `info.memory.total` — una estimación en bytes de búferes de vértices, índices y almacenamiento, texturas, búferes uniform y programas (`memory.texturesSize`, `memory.attributesSize` y los demás campos `*Size` contienen las partes). Una textura comprimida cuenta como 1 byte ahí, una estimación de reserva, así que la memoria KTX2 se subestima.
- El bucle del segundo bloque sustituye al `animate` del primero; `renderer.compute()` envía directamente porque `await renderer.init()` ya se ha ejecutado.

## Errores comunes

- `function animate() { requestAnimationFrame(animate); renderer.render(scene, camera); }` → `renderer.setAnimationLoop(animate);`: una sesión WebXR solo ejecuta el callback entregado a setAnimationLoop, a través del bucle de fotogramas de la propia sesión, y con WebGPURenderer setAnimationLoop además espera a init() antes del primer fotograma.
- `const clock = new THREE.Clock(); const dt = clock.getDelta(); const t = clock.getElapsedTime();` → `const timer = new THREE.Timer(); timer.update(); const dt = timer.getDelta(); const t = timer.getElapsed();`: Clock está obsoleto desde r183, y getElapsedTime() llama internamente a getDelta(), así que un getDelta() posterior en el mismo fotograma devuelve casi cero.
- `console.log(renderer.info.render.calls); renderer.render(scene, camera);` → `renderer.render(scene, camera); console.log(renderer.info.render.calls);`: los contadores se reinician al inicio de render(), así que leerlos antes da los del fotograma anterior.
- `renderer.info.autoReset = false` → `renderer.info.autoReset = false; function animate() { renderer.render(scene, camera); console.log(renderer.info.render.calls); renderer.info.reset(); }`: con autoReset desactivado, nada borra los contadores salvo que reset() se ejecute una vez por fotograma tras el último render(); si no, se acumulan entre fotogramas.
- `webgpuRenderer.info.render.calls` → `webgpuRenderer.info.render.drawCalls`: con WebGPURenderer, render.calls cuenta los pases de render desde que arrancó la aplicación, mientras que drawCalls cuenta las draw calls de este fotograma; WebGLRenderer no tiene drawCalls, y su render.calls es el número de draw calls por render().
- `renderer.compile(scene, camera)` → `await renderer.compileAsync(scene, camera)`: compile() encola las construcciones y retorna, así que un render inmediatamente después sigue bloqueándose con los programas sin terminar, mientras que compileAsync() se resuelve solo cuando KHR_parallel_shader_compile informa de que todos los programas están completos, donde el navegador expone esa extensión.
- `renderer.shadowMap.type = THREE.PCFSoftShadowMap` → `renderer.shadowMap.type = THREE.PCFShadowMap`: PCFSoftShadowMap está obsoleto desde r182 y recurre a PCF con un aviso en la consola.
- `mesh.material.dispose()` → `mesh.material.dispose(); for (const value of Object.values(mesh.material)) if (value?.isTexture) value.dispose();`: material.dispose() libera sus programas de shader, nunca las texturas del material, así que info.memory.textures solo baja cuando se ejecuta cada texture.dispose().
- `gltf.scene.dispose()` → `gltf.scene.traverse((child) => { child.geometry?.dispose(); for (const material of [child.material ?? []].flat()) { for (const value of Object.values(material)) if (value?.isTexture) value.dispose(); material.dispose(); } child.dispose(); })`: Object3D.dispose() libera el estado del renderer solo de ese objeto, nunca de sus hijos, geometría, materiales ni texturas.
- `const hits = raycaster.intersectObjects(scene.children, true)` → `raycaster.layers.set(1); const hits = raycaster.intersectObjects(pickables, false);`: la llamada recursiva recorre y prueba todos los descendientes en cada evento, mientras que la comprobación de capas se ejecuta antes de la prueba de geometría de cada objeto y una lista explícita nunca visita el resto de la escena.
- `scene.traverse((child) => (child.frustumCulled = false))` → `geometry.computeBoundingSphere(); // tras mover vértices en la CPU`: el culling omite draw calls enteras a través de la esfera envolvente de cada geometría, así que desactivarlo en toda la escena dibuja todo en cada fotograma.
- `function animate() { mesh.position.add(new THREE.Vector3(0, 0.01, 0)); }` → `const offset = new THREE.Vector3(0, 0.01, 0); function animate() { mesh.position.add(offset); }`: cada asignación por fotograma se convierte en basura que el recolector debe pausar para reclamar, lo que se nota como picos periódicos de fotograma.
- `const dt = uniform(0); /* alimentado desde el timer en cada fotograma */` → `const dt = deltaTime;`: los nodos integrados time y deltaTime son uniforms que el renderer ya actualiza en cada render, así que una copia alimentada a mano los duplica y necesita su propio Timer.

## Véase también

- `references/fundamentals.md` - construcción del renderer, el bucle de render y la gestión del redimensionado alrededor de todo lo que se mide aquí.
- `references/geometry.md` - las APIs completas de instancing, batching, fusión y atributos detrás de los recortes de draw calls.
- `references/materials.md` - qué ajustes de material se compilan dentro del shader y fuerzan una reconstrucción.
- `references/loaders.md` - la configuración de los loaders KTX2, Draco y meshopt para los archivos comprimidos que producen estas palancas.
- `references/lighting.md` - tipos de luz, unidades y configuración de sombras cuyos costes mide esta skill.
- `references/postprocessing.md` - los búferes propios del composer, MSAA y los ajustes de pixel ratio.
- `references/asset-pipeline.md` - los comandos de gltf-transform que producen texturas KTX2 y archivos glTF comprimidos, instanciados o unidos.
