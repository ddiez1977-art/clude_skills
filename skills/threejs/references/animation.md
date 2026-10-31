# Animación en Three.js

Dirigido a three.js r186. Los ejemplos usan WebGLRenderer; la sección de WebGPU y TSL usa WebGPURenderer.

## Inicio rápido

```javascript
import * as THREE from "three";

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(0, 0.5, 3);

const mesh = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshNormalMaterial());
scene.add(mesh);

const timer = new THREE.Timer();
timer.connect(document); // también mantiene los deltas pequeños tras ocultar la pestaña

function animate() {
  timer.update(); // lo primero en cada fotograma: fija getDelta()/getElapsed() para este fotograma
  const delta = timer.getDelta();
  const elapsed = timer.getElapsed();

  mesh.rotation.y += delta; // giro independiente de la tasa de fotogramas
  mesh.position.y = Math.sin(elapsed * 2) * 0.25; // vaivén sobre el tiempo absoluto

  renderer.render(scene, camera);
}

renderer.setAnimationLoop(animate);
```

## Cómo encaja el sistema

- **AnimationClip**: datos de fotogramas clave (keyframes): pistas (tracks) de tiempos y valores, sin estado de reproducción.
- **AnimationMixer**: reproduce clips sobre un objeto raíz y todos sus descendientes.
- **AnimationAction**: control de reproducción de un clip en un mixer.

En cada fotograma, `mixer.update(delta)` muestrea los clips activos y escribe los valores en propiedades de objeto corrientes. El sistema se ejecuta en la CPU y nunca toca el renderer, así que mueve los modelos igual con cualquiera de los dos renderers.

## AnimationClip y pistas de keyframes

```javascript
// Una pista por propiedad animada. values.length debe ser times.length * valueSize.
const times = [0, 1, 2]; // tiempos de los keyframes en segundos
const values = [0, 1, 0]; // un escalar por keyframe para una pista Number

const track = new THREE.NumberKeyframeTrack(".position[y]", times, values); // position.y de la raíz

const clip = new THREE.AnimationClip("bounce", 2, [track]); // duración en segundos
// pasa -1 como duración para derivarla de las pistas
```

Los nombres de pista siguen el patrón `nodeName.objectName[objectIndex].propertyName[propertyIndex]`; todas las partes excepto la propiedad son opcionales. `.position` enlaza la posición de la raíz, `.material.opacity` una propiedad del material, `.position[y]` un solo componente, `.morphTargetInfluences[smile]` un morph target y `Hips.position` un descendiente con nombre: así se direccionan los huesos en un modelo con skinning. Los nombres de objeto pueden ser `material`, `materials`, `bones` o `map`.

```javascript
// Pista Number (tamaño de valor 1); crea el material con transparent: true, o la opacidad se ignora
new THREE.NumberKeyframeTrack(".material.opacity", [0, 1], [1, 0]);

// Pista Vector (tamaño de valor 3: x, y, z por keyframe)
new THREE.VectorKeyframeTrack(".position", [0, 1, 2], [0, 0, 0, 1, 2, 0, 0, 0, 0]);

// Pista de rotación (tamaño de valor 4): x, y, z, w del cuaternión por keyframe, no ángulos de Euler
const q2 = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), Math.PI);
new THREE.QuaternionKeyframeTrack(
  ".quaternion",
  [0, 1],
  [0, 0, 0, 1, q2.x, q2.y, q2.z, q2.w], // identidad, y luego q2
);

// Pista Color (tamaño de valor 3)
new THREE.ColorKeyframeTrack(".material.color", [0, 1], [1, 0, 0, 0, 1, 0]);

// Pista Boolean (siempre discreta)
new THREE.BooleanKeyframeTrack(".visible", [0, 1], [true, false]);
```

### Interpolación

```javascript
const track = new THREE.VectorKeyframeTrack(
  ".position",
  [0, 1, 2],
  [0, 0, 0, 1, 2, 0, 0, 0, 0],
);

track.setInterpolation(THREE.InterpolateLinear); // por defecto
track.setInterpolation(THREE.InterpolateSmooth); // cúbica a través de los keyframes
track.setInterpolation(THREE.InterpolateDiscrete); // escalonada, sin valores intermedios

// Bezier recibe puntos de control absolutos (tiempo, valor), dos números por keyframe y por
// componente: una pista de dos keyframes con stride 1 necesita cuatro entradas por array
const morphTrack = new THREE.NumberKeyframeTrack(
  ".morphTargetInfluences[smile]",
  [0, 1],
  [0, 1],
);
morphTrack.setInterpolation(THREE.InterpolateBezier);
morphTrack.settings = { inTangents: [0, 0, 1, 1], outTangents: [0, 1, 1, 0] };
```

## AnimationMixer

```javascript
const track = new THREE.NumberKeyframeTrack(".rotation[y]", [0, 2], [0, Math.PI * 2]);
const clip = new THREE.AnimationClip("spin", 2, [track]);

// Un mixer por raíz animada; llega a la raíz y a todos sus descendientes
const mixer = new THREE.AnimationMixer(mesh);
const action = mixer.clipAction(clip); // en caché: volver a llamarlo para este clip y raíz devuelve la misma action
action.play();

const timer = new THREE.Timer();
timer.connect(document);

function animate() {
  timer.update();
  mixer.update(timer.getDelta()); // obligatorio: hace avanzar todas las actions activas
  renderer.render(scene, camera);
}

renderer.setAnimationLoop(animate);

// Los eventos se disparan en el mixer mientras se actualiza; "finished" requiere LoopOnce o repeticiones finitas
mixer.addEventListener("finished", (e) => console.log("finished:", e.action.getClip().name));
mixer.addEventListener("loop", (e) => console.log("looped:", e.action.getClip().name));
```

## AnimationAction

```javascript
const mixer = new THREE.AnimationMixer(mesh);
const clip = new THREE.AnimationClip("spin", 2, [
  new THREE.NumberKeyframeTrack(".rotation[y]", [0, 2], [0, Math.PI * 2]),
]);
const action = mixer.clipAction(clip);

action.play(); // programa e inicia
action.reset(); // rebobina al tiempo 0 y cancela los fundidos
action.stop(); // desprograma; las propiedades que ninguna otra action programada anima vuelven a sus valores originales
action.halt(0.3); // decelera hasta parar en 0,3 s

action.time = 0.5; // desplázate dentro del clip
action.timeScale = -1; // un valor negativo reproduce hacia atrás
action.paused = true; // congela en el sitio

action.setLoop(THREE.LoopOnce, 1); // se detiene (o se mantiene) tras una pasada
action.setLoop(THREE.LoopRepeat, Infinity); // el valor por defecto
action.setLoop(THREE.LoopPingPong, 4); // alterna la dirección en cada pasada
action.clampWhenFinished = true; // mantiene la pose final en lugar de reiniciarse
```

### Fundidos y fundidos cruzados

```javascript
const mixer = new THREE.AnimationMixer(mesh);
const idleClip = new THREE.AnimationClip("idle", 2, [
  new THREE.NumberKeyframeTrack(".position[y]", [0, 1, 2], [0, 0.05, 0]),
]);
const walkClip = new THREE.AnimationClip("walk", 1, [
  new THREE.NumberKeyframeTrack(".rotation[y]", [0, 1], [0, Math.PI]),
]);

const idle = mixer.clipAction(idleClip).play();
const walk = mixer.clipAction(walkClip).play();

// Pasa de idle a walk en 0,4 s; true como tercer argumento también deforma
// ambas escalas de tiempo para que la duración de sus ciclos coincida durante el fundido
idle.crossFadeTo(walk, 0.4, false);

// El mismo relevo con las llamadas unilaterales (usa una forma, no ambas)
walk.reset().fadeIn(0.4).play(); // sube el peso desde 0
idle.fadeOut(0.4); // baja el peso hasta 0
```

## Reproducir animaciones glTF

```javascript
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import * as SkeletonUtils from "three/addons/utils/SkeletonUtils.js";

const gltf = await new GLTFLoader().loadAsync("model.glb");
const model = gltf.scene;
scene.add(model);

// El material por defecto de GLTFLoader (MeshStandardMaterial) es iluminado: sin luces el modelo se ve negro
const sun = new THREE.DirectionalLight(0xffffff, 2);
sun.position.set(3, 5, 2);
scene.add(sun, new THREE.HemisphereLight(0xffffff, 0x444444, 1.5));

// gltf.animations es un array de AnimationClips ya parseados
const clips = gltf.animations;

const mixer = new THREE.AnimationMixer(model);
const walkClip = THREE.AnimationClip.findByName(clips, "Walk");
if (walkClip) mixer.clipAction(walkClip).play();

// Un segundo personaje: clona el modelo con skinning y dale a la copia su propio mixer
const model2 = SkeletonUtils.clone(model);
model2.position.x = 1.5; // junto al primero
scene.add(model2);
const mixer2 = new THREE.AnimationMixer(model2);
if (walkClip) mixer2.clipAction(walkClip).play(); // el mismo clip, dos mixers

const timer = new THREE.Timer();
timer.connect(document);

function animate() {
  timer.update();
  const delta = timer.getDelta();
  mixer.update(delta);
  mixer2.update(delta);
  renderer.render(scene, camera);
}

renderer.setAnimationLoop(animate);
```

## Animación esquelética

```javascript
// mesh es la raíz del modelo cargado; busca su primer SkinnedMesh
const skinnedMesh = mesh.getObjectByProperty("type", "SkinnedMesh");
const skeleton = skinnedMesh.skeleton;
console.log(skeleton.bones.map((b) => b.name));

// Toma un hueso para posarlo o para anclarle algo
const handBone = skeleton.bones.find((b) => b.name === "RightHand");

// Visualiza el rig
const helper = new THREE.SkeletonHelper(mesh);
scene.add(helper);
```

El control procedural de huesos se ejecuta **después** de `mixer.update()`, o un clip que anime el mismo hueso lo sobrescribirá:

```javascript
const skinnedMesh = mesh.getObjectByProperty("type", "SkinnedMesh");
const headBone = skinnedMesh.skeleton.bones.find((b) => b.name === "Head");
const mixer = new THREE.AnimationMixer(mesh); // reproduce en él los clips del modelo (véase Reproducir animaciones glTF)

const timer = new THREE.Timer();
timer.connect(document);

function animate() {
  timer.update();
  mixer.update(timer.getDelta()); // los clips escriben aquí la pose de sus huesos

  // Sobrescribe después: update() pisa cada propiedad que animan los clips en reproducción
  if (headBone) headBone.rotation.y = Math.sin(timer.getElapsed()) * 0.3;
  renderer.render(scene, camera);
}

renderer.setAnimationLoop(animate);
```

Los huesos son Object3D, así que anclar algo a ellos es emparentarlo:

```javascript
const skinnedMesh = mesh.getObjectByProperty("type", "SkinnedMesh");
const handBone = skinnedMesh.skeleton.bones.find((b) => b.name === "RightHand");

const weapon = new THREE.Mesh(
  new THREE.BoxGeometry(0.08, 0.08, 0.5),
  new THREE.MeshNormalMaterial(),
);
if (handBone) {
  handBone.add(weapon); // el arma ahora sigue la transformación del hueso de la mano
  weapon.position.set(0, 0, 0.25); // desplazamiento dentro del espacio del hueso
  weapon.rotation.set(0, Math.PI / 2, 0);
}
```

## Morph targets

```javascript
// mesh tiene morph targets (cargados, o añadidos a mano más abajo)
const names = Object.keys(mesh.morphTargetDictionary); // nombre -> índice
console.log(names, mesh.morphTargetInfluences); // un peso por target

// Mezcla un target por índice o por nombre; 0 = forma base, 1 = target completo
mesh.morphTargetInfluences[0] = 0.5;
const smileIndex = mesh.morphTargetDictionary["Mouth_Smile"];
if (smileIndex !== undefined) mesh.morphTargetInfluences[smileIndex] = 1;
```

Añadir un morph target a mano:

```javascript
const geometry = mesh.geometry;

// Un morph target es un atributo de posición (o normal) de tamaño completo junto al base
const raised = geometry.attributes.position.array.slice(); // mismo número de vértices
for (let i = 1; i < raised.length; i += 3) {
  raised[i] += 0.5; // y es uno de cada tres componentes: eleva todos los vértices
}

const target = new THREE.Float32BufferAttribute(raised, 3);
target.name = "raised"; // los targets con nombre siguen siendo direccionables desde las pistas

geometry.morphAttributes.position = [target];
mesh.updateMorphTargets(); // reconstruye morphTargetInfluences y el diccionario
```

Controlar los morph targets:

```javascript
// Procedural, dentro del bucle de render tras timer.update():
// mesh.morphTargetInfluences[0] = (Math.sin(timer.getElapsed() * 2) + 1) / 2;

// Con keyframes: una pista Number controla un target por nombre, nunca una pista String
const track = new THREE.NumberKeyframeTrack(
  ".morphTargetInfluences[raised]",
  [0, 0.5, 1],
  [0, 1, 0],
);
const clip = new THREE.AnimationClip("pulse", 1, [track]);
const mixer = new THREE.AnimationMixer(mesh);
mixer.clipAction(clip).play();
```

## Mezclar clips por peso

```javascript
const mixer = new THREE.AnimationMixer(mesh);
const idleClip = new THREE.AnimationClip("idle", 2, [
  new THREE.NumberKeyframeTrack(".position[y]", [0, 1, 2], [0, 0.05, 0]),
]);
const runClip = new THREE.AnimationClip("run", 1, [
  new THREE.NumberKeyframeTrack(".position[y]", [0, 0.5, 1], [0, 0.3, 0]),
]);

const idle = mixer.clipAction(idleClip).play();
const run = mixer.clipAction(runClip).play();

// Ambos se muestrean en cada fotograma; los pesos mezclan sus poses
function setBlend(speed) {
  const t = Math.min(speed / 5, 1); // 0 = idle, 5 o más = carrera completa
  idle.setEffectiveWeight(1 - t);
  run.setEffectiveWeight(t);
}

setBlend(2.5); // mitad idle, mitad carrera
```

### Animación aditiva

```javascript
const mixer = new THREE.AnimationMixer(mesh);
const walkClip = new THREE.AnimationClip("walk", 1, [
  new THREE.NumberKeyframeTrack(".rotation[y]", [0, 1], [0, Math.PI]),
]);
const breathClip = new THREE.AnimationClip("breath", 2, [
  new THREE.NumberKeyframeTrack(".position[y]", [0, 1, 2], [0, 0.02, 0]),
]);

// Re-basa cada pista sobre su fotograma 0 y marca el clip como aditivo
THREE.AnimationUtils.makeClipAdditive(breathClip);

mixer.clipAction(walkClip).play(); // clip base normal
mixer.clipAction(breathClip).play(); // suma sus desplazamientos sobre la pose base
```

## Utilidades de clips

```javascript
const clip = new THREE.AnimationClip("walk", 2, [
  new THREE.NumberKeyframeTrack(".rotation[y]", [0, 1, 2], [0, Math.PI, Math.PI * 2]),
]);

const walk = THREE.AnimationClip.findByName([clip], "walk"); // búsqueda por nombre
// Conserva los keyframes existentes en los fotogramas [0, 31) a 30 fps (tiempos 0 y 1); nunca remuestrea
const cut = THREE.AnimationUtils.subclip(clip, "half", 0, 31, 30);
const copy = clip.clone(); // copia profunda independiente

clip.optimize(); // elimina las claves con tiempo duplicado y las claves iguales a sus dos vecinas en cualquier pista no suave (las tangentes Bezier no se compactan)
clip.resetDuration(); // recalcula la duración a partir de la pista más larga; no desplaza la reproducción
console.log(clip.validate()); // false si la proporción valores/tiempos es fraccionaria, hay una pista vacía, los tiempos no están ordenados o hay NaN
```

## Movimiento procedural

```javascript
const timer = new THREE.Timer();
timer.connect(document);

// Aproximación exponencial; un lambda mayor se ajusta más rápido. Independiente de la tasa de fotogramas.
// La misma forma sirve para posiciones, rotaciones o cualquier escalar en cada fotograma.
let scale = 0;

function animate() {
  timer.update();
  scale = THREE.MathUtils.damp(scale, 1, 4, timer.getDelta());
  mesh.scale.setScalar(0.5 + scale * 0.5);
  renderer.render(scene, camera);
}

renderer.setAnimationLoop(animate);
```

## Rendimiento

- Un mismo AnimationClip puede alimentar cualquier número de mixers: comparte un único conjunto de clips entre personajes en lugar de copiarlo.
- Llama a `mixer.update()` solo para los personajes que están visibles o a punto de estarlo; un mixer sin actualizar simplemente deja la última pose en su sitio.
- Un SkinnedMesh calcula su esfera envolvente una sola vez, la primera vez que el culling o el raycasting la necesitan, así que un clip que lo aleje mucho de esa pose puede hacer que se descarte (culling) en el borde de la pantalla: tras `mixer.update()` llama a `mixer.getRoot().updateMatrixWorld()` y luego a `skinnedMesh.computeBoundingSphere()` (una pasada de CPU por todos los vértices), o establece `skinnedMesh.frustumCulled = false`.

```javascript
// Libera un mixer y sus bindings en caché cuando su modelo se va para siempre
const mixer = new THREE.AnimationMixer(mesh);
mixer.stopAllAction();
mixer.uncacheRoot(mesh); // libera los bindings de propiedades creados para el modelo
```

## WebGPU y TSL

Todo lo anterior (mixer, actions, transformaciones de huesos, pesos de morph) se calcula en la CPU y mueve un modelo con WebGPURenderer sin cambios. TSL añade animación en la GPU: `time` (segundos transcurridos) y `deltaTime` (segundos desde el fotograma anterior) son uniforms float que el renderer refresca en cada fotograma, y los osciladores `oscSine`, `oscSquare`, `oscTriangle` y `oscSawtooth` devuelven ondas de 0 a 1 con un periodo de un segundo a partir de un nodo de tiempo, con `time` por defecto (`oscSine(time.mul(0.5))` tarda dos segundos). El movimiento por vértice necesita un node material y un mesh subdividido.

```javascript
import * as THREE from "three/webgpu";
import { positionLocal, time, vec3 } from "three/tsl";

const renderer = new THREE.WebGPURenderer({ antialias: true });
await renderer.init(); // antes de cualquier otro uso del renderer
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x111418); // el canvas de WebGPU es transparente por defecto

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(0, 2, 3);
camera.lookAt(0, 0, 0);

// Ondula un plano subdividido a lo largo de su normal (z local) en la GPU; time lo mueve, sin JS por fotograma
const material = new THREE.MeshBasicNodeMaterial({ wireframe: true });
material.positionNode = positionLocal.add(
  vec3(0, 0, positionLocal.x.mul(2).sin().mul(time.mul(2).cos()).mul(0.2)),
);
const mesh = new THREE.Mesh(new THREE.PlaneGeometry(3, 3, 32, 32), material);
mesh.rotation.x = -Math.PI / 2;
scene.add(mesh);

function animate() {
  renderer.render(scene, camera);
}

renderer.setAnimationLoop(animate);
```

En un mesh con skinning, construye el desplazamiento sobre `positionLocal`: el skinning, los morph targets, el batching y el instancing se le aplican antes de que se ejecute `positionNode`, de modo que la pose controlada por el mixer se conserva. `positionGeometry` es el atributo en bruto en pose de reposo: nunca es la base para desplazar un mesh animado.

```javascript
import * as THREE from "three/webgpu";
import { color, mix, oscSine, positionLocal, vec3 } from "three/tsl";

// El pulso se superpone a la pose con skinning: positionLocal ya la incorpora
const material = new THREE.MeshBasicNodeMaterial();
material.positionNode = positionLocal.add(vec3(0, oscSine().mul(0.05), 0));

// Los osciladores animan cualquier ranura de nodo, no solo las posiciones
material.colorNode = mix(color(0x202030), color(0xffd24a), oscSine());

const skinnedMesh = scene.getObjectByProperty("type", "SkinnedMesh"); // un modelo animado cargado
if (skinnedMesh) skinnedMesh.material = material;
```

## Errores comunes

- `const clock = new THREE.Clock();` → `const timer = new THREE.Timer(); timer.connect(document);`: la clase Clock está obsoleta desde r183 y Timer es su sustituto.
- `const elapsed = clock.getElapsedTime(); const delta = clock.getDelta();` → `timer.update(); const delta = timer.getDelta(); const elapsed = timer.getElapsed();`: getElapsedTime() llama internamente a getDelta(), así que la lectura posterior del delta es casi cero y el mixer se queda parado.
- `requestAnimationFrame(animate);` → `renderer.setAnimationLoop(animate);`: la documentación de ambos renderers lo recomienda frente a un bucle manual, y cede los fotogramas a la sesión de WebXR cuando esta se inicia.
- `import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";` → `import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";`: el especificador examples/jsm no se resuelve con el import map estándar.
- `new THREE.NumberKeyframeTrack(".material.opacity", [0, 1, 2], [1, 0])` → `new THREE.NumberKeyframeTrack(".material.opacity", [0, 1], [1, 0])`: values debe contener times.length × valueSize entradas; con una proporción fraccionaria play() nunca termina, y cualquier otro desajuste muestrea valores erróneos.
- `new THREE.StringKeyframeTrack(".morphTargetInfluences[smile]", [0, 1], ["0", "1"])` → `new THREE.NumberKeyframeTrack(".morphTargetInfluences[smile]", [0, 1], [0, 1])`: las influencias de morph son números, y una pista String escribe cadenas "0"/"1" en el array.
- `headBone.rotation.y = Math.sin(t) * 0.3; mixer.update(delta);` → `mixer.update(delta); headBone.rotation.y = Math.sin(t) * 0.3;`: update() escribe la pose del clip por encima de cualquier valor fijado antes.
- `clip.resetDuration()` → `action.reset()`: resetDuration() solo recalcula la duración del clip a partir de su pista más larga, mientras que reset() rebobina la action al tiempo 0 y la rehabilita tras terminar una pasada única.
- `material.positionNode = positionGeometry.add(offset)` → `material.positionNode = positionLocal.add(offset)`: positionGeometry es el atributo en bruto, así que construir sobre él descarta el skinning, los morph targets, el batching y el instancing.
- `const uTime = uniform(0); uTime.value = timer.getElapsed(); const wave = uTime.mul(2).sin();` → `const wave = time.mul(2).sin();`: el renderer ya hace avanzar el nodo time de TSL en cada fotograma, así que un uniform alimentado por Timer es JavaScript por fotograma redundante.
- `const model2 = model.clone();` → `const model2 = SkeletonUtils.clone(model);`: clonar un modelo con skinning comparte su esqueleto entre las copias; cada copia necesita el suyo.
- `import { clone } from "three/addons/utils/SkeletonUtils.js";` → `import * as SkeletonUtils from "three/addons/utils/SkeletonUtils.js";`: el espacio de nombres mantiene la llamada como SkeletonUtils.clone(model), que no puede confundirse con el model.clone() que comparte esqueleto.
- `new Promise((resolve, reject) => loader.load(url, resolve, undefined, reject))` → `await loader.loadAsync(url)`: los loaders ya exponen la forma con promesa, y loadAsync recibe el callback de progreso como segundo argumento.

## Véase también

- `references/fundamentals.md`: bucle de render, Timer, configuración de renderer y escena
- `references/loaders.md`: carga de modelos glTF y de sus clips de animación
- `references/shaders.md`: desplazamiento de vértices en la GPU con TSL o ShaderMaterial
