# Interacción en Three.js

Orientado a three.js r186. Los ejemplos usan WebGLRenderer; la sección de WebGPU y TSL usa WebGPURenderer.

## Inicio rápido

```javascript
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x111318);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(0, 1.5, 5);

const mesh = new THREE.Mesh(
  new THREE.BoxGeometry(1, 1, 1),
  new THREE.MeshStandardMaterial({ color: 0x3a86ff }),
);
scene.add(mesh);
const light = new THREE.DirectionalLight(0xffffff, 2);
light.position.set(3, 5, 4);
scene.add(light, new THREE.AmbientLight(0xffffff, 0.4));

const controls = new OrbitControls(camera, renderer.domElement); // se conecta solo
controls.enableDamping = true; // requiere controls.update() en cada fotograma

const timer = new THREE.Timer();
timer.connect(document); // congela el delta mientras la pestaña está oculta

const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();

function setPointer(event) {
  // Coordenadas NDC relativas al canvas, para que la página pueda hacer scroll o incrustarlo
  const rect = renderer.domElement.getBoundingClientRect();
  pointer.set(
    ((event.clientX - rect.left) / rect.width) * 2 - 1,
    -((event.clientY - rect.top) / rect.height) * 2 + 1,
  );
}

renderer.domElement.addEventListener("pointerdown", (event) => {
  setPointer(event);
  raycaster.setFromCamera(pointer, camera);
  const hits = raycaster.intersectObject(mesh); // también prueba los hijos (recursivo por defecto), como necesita un modelo cargado
  if (hits.length > 0) console.log("clicked", hits[0].object);
});

function animate() {
  timer.update();
  controls.update(timer.getDelta());
  renderer.render(scene, camera);
}
renderer.setAnimationLoop(animate);
```

Los eventos de puntero (`pointerdown`, `pointermove`, `pointerup`) cubren ratón, táctil y lápiz con un único conjunto de listeners, así que no hacen falta manejadores táctiles aparte.

## Raycasting

Las caras que apuntan en sentido contrario al origen del rayo no se detectan; pon `material.side = THREE.DoubleSide` para detectar ambos lados. Un rayo que roza una arista compartida por dos caras puede producir dos impactos coincidentes. Las mallas invisibles también entran en el raycasting (el Raycaster comprueba las capas, no la visibilidad), así que un proxy simple e invisible puede sustituir a un modelo complejo.

### Qué contiene una intersección

```javascript
const raycaster = new THREE.Raycaster();
const clickables = [mesh]; // la lista más pequeña posible: las mallas, no scene.children
const hits = raycaster.intersectObjects(clickables, false); // ordenados, el más cercano primero
// Cada impacto:
// {
//   distance: number,                          // desde el origen del rayo, en unidades del mundo
//   point: THREE.Vector3,                      // punto de impacto en el espacio del mundo
//   face: { a, b, c, normal, materialIndex },  // objeto plano; a, b, c son índices de vértices; normal en espacio del objeto
//   faceIndex: number,
//   object: THREE.Object3D,
//   uv: THREE.Vector2,                         // undefined cuando la geometría no tiene uv
//   uv1: THREE.Vector2,                        // segundo conjunto de UV, cuando la geometría lo tiene
//   normal: THREE.Vector3,                     // normal de vértice interpolada en espacio del objeto, volteada para mirar al rayo
//   barycoord: THREE.Vector3,                  // coordenadas baricéntricas del punto de impacto
//   instanceId: number,                        // presente en impactos de InstancedMesh
//   batchId: number,                           // presente en impactos de BatchedMesh
//   distanceToRay: number                      // presente en impactos de Points
// }
```

### Configuración del Raycaster

```javascript
const raycaster = new THREE.Raycaster();

// Desde cualquier origen y dirección (normaliza antes la dirección)
raycaster.set(new THREE.Vector3(0, 2, 0), new THREE.Vector3(1, 0, 0).normalize());

// Rango: se descartan los impactos más cerca que near o más lejos que far
raycaster.near = 0.1;
raycaster.far = 10;

// Precisión para Points y Line, en unidades del mundo (ambos valen 1 por defecto)
raycaster.params.Points.threshold = 0.2;
raycaster.params.Line.threshold = 0.2;

// Restringe la selección a la capa 1. Los objetos se unen con enable; set también los
// quitaría de la capa 0, donde mira la cámara por defecto, así que usa set solo en un proxy exclusivo de selección.
mesh.layers.enable(1); // sigue también en la capa 0, así que la cámara sigue renderizando la malla
raycaster.layers.set(1); // prueba solo la capa 1; raycaster.layers.enable(1) probaría las capas 0 y 1
```

### Arrastrar sobre un plano

```javascript
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
const groundPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0); // normal, constante
const hit = new THREE.Vector3();

renderer.domElement.addEventListener("pointermove", (event) => {
  const rect = renderer.domElement.getBoundingClientRect();
  pointer.set(
    ((event.clientX - rect.left) / rect.width) * 2 - 1,
    -((event.clientY - rect.top) / rect.height) * 2 + 1,
  );
  raycaster.setFromCamera(pointer, camera);
  // null cuando el rayo es paralelo al plano o apunta en sentido contrario
  if (event.buttons !== 0 && raycaster.ray.intersectPlane(groundPlane, hit) !== null) {
    mesh.position.copy(hit); // mientras se mantiene pulsado un botón, arrastra la malla por el suelo
  }
});
```

## Controles de cámara

Todas las clases de controles extienden `Controls` y comparten una misma API base: se construyen con la cámara y el elemento del DOM (DragControls recibe primero su array de objetos), y el constructor conecta sus propios listeners; `enabled = false` para ignorar la entrada, `disconnect()` / `connect(element)` para desconectarlos o moverlos, y `dispose()` al desmontar. `update()` recibe un delta en segundos en OrbitControls, FlyControls y FirstPersonControls (pasa `timer.getDelta()`); en los demás se llama sin argumentos.

### OrbitControls

```javascript
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const controls = new OrbitControls(camera, renderer.domElement);

controls.enableDamping = true; // requiere update() en cada fotograma
controls.dampingFactor = 0.05;

controls.minDistance = 2;
controls.maxDistance = 50;
controls.minPolarAngle = 0.1;          // límites verticales, en radianes
controls.maxPolarAngle = Math.PI / 2;  // se detiene en el horizonte
controls.minAzimuthAngle = -Math.PI / 4;
controls.maxAzimuthAngle = Math.PI / 4;

controls.target.set(0, 1, 0);  // el punto alrededor del que se orbita
controls.zoomToCursor = true; // la rueda hace zoom hacia el puntero

controls.autoRotate = true;      // requiere update() en cada fotograma; se detiene en un límite de azimut
controls.autoRotateSpeed = 2.0;

const timer = new THREE.Timer();
timer.connect(document);

function animate() {
  timer.update();
  controls.update(timer.getDelta()); // el delta hace que autoRotate sea independiente de la tasa de fotogramas
  renderer.render(scene, camera);
}
renderer.setAnimationLoop(animate);
```

OrbitControls lanza los eventos `change`, `start` y `end`. `MapControls` es una subclase de OrbitControls ajustada para navegar por mapas:

```javascript
import { MapControls } from "three/addons/controls/MapControls.js";

// Arrastrar con el botón izquierdo desplaza, arrastrar con el derecho (o con el izquierdo
// y ctrl/meta/shift) orbita, el botón central o la rueda hacen zoom. screenSpacePanning es false,
// así que el desplazamiento se mantiene paralelo al suelo. Se aplican todas las opciones de OrbitControls.
const controls = new MapControls(camera, renderer.domElement);
controls.enableDamping = true;
```

### FlyControls

```javascript
import { FlyControls } from "three/addons/controls/FlyControls.js";

const controls = new FlyControls(camera, renderer.domElement);
controls.movementSpeed = 10;
controls.rollSpeed = Math.PI / 24;
controls.dragToLook = true; // dirige solo mientras se mantiene pulsado un botón del ratón

const timer = new THREE.Timer();
timer.connect(document);

function animate() {
  timer.update();
  controls.update(timer.getDelta()); // el movimiento se escala con el delta
  renderer.render(scene, camera);
}
renderer.setAnimationLoop(animate);
```

### FirstPersonControls

FirstPersonControls tiene un modelo de mirada basado en arrastre: pulsa y arrastra para mirar (la velocidad de giro crece con la distancia arrastrada y se suaviza mediante `dampingFactor`, 0.1 por defecto, donde 1 desactiva el suavizado), WASD o las flechas para moverte, R y F para subir y bajar, mantén el botón izquierdo para avanzar volando y el derecho para retroceder. El táctil funciona mediante eventos de puntero: un dedo avanza, dos dedos retroceden.

```javascript
import { FirstPersonControls } from "three/addons/controls/FirstPersonControls.js";

const controls = new FirstPersonControls(camera, renderer.domElement);
controls.movementSpeed = 10;
controls.lookSpeed = 0.005;   // por defecto
controls.dampingFactor = 0.1; // por defecto; 1 desactiva el suavizado
controls.constrainVertical = true;
controls.verticalMin = Math.PI / 4;
controls.verticalMax = (Math.PI * 3) / 4;

const timer = new THREE.Timer();
timer.connect(document);

function animate() {
  timer.update();
  controls.update(timer.getDelta()); // el delta es obligatorio; sin él la posición pasa a NaN
  renderer.render(scene, camera);
}
renderer.setAnimationLoop(animate);
```

### PointerLockControls

```javascript
import { PointerLockControls } from "three/addons/controls/PointerLockControls.js";

const controls = new PointerLockControls(camera, document.body);
controls.pointerSpeed = 1.0; // sensibilidad del ratón

controls.addEventListener("lock", () => console.log("locked"));
controls.addEventListener("unlock", () => console.log("unlocked"));
document.body.addEventListener("click", () => controls.lock()); // necesita un gesto del usuario

const velocity = new THREE.Vector3();
let moveForward = false; // let: los manejadores de teclado reasignan estas variables
let moveBackward = false;

document.addEventListener("keydown", (event) => {
  if (event.code === "KeyW") moveForward = true;
  if (event.code === "KeyS") moveBackward = true;
});
document.addEventListener("keyup", (event) => {
  if (event.code === "KeyW") moveForward = false;
  if (event.code === "KeyS") moveBackward = false;
});

const timer = new THREE.Timer();
timer.connect(document);

function animate() {
  timer.update();
  const delta = timer.getDelta();
  if (controls.isLocked) {
    // acelera suavemente hacia la velocidad objetivo y mueve la cámara hacia delante paralela al suelo (plano xz)
    velocity.z = THREE.MathUtils.damp(
      velocity.z,
      10 * (Number(moveForward) - Number(moveBackward)),
      10,
      delta,
    );
    controls.moveForward(velocity.z * delta);
    // controls.moveRight(distance) hace lo mismo a lo largo del eje derecho de la cámara
  }
  renderer.render(scene, camera);
}
renderer.setAnimationLoop(animate);
```

Los controles mueven la cámara pasada al constructor (`controls.object`); se renderiza sin añadirla a la escena, así que `scene.add(controls.object)` solo hace falta cuando la cámara tiene hijos.

### TrackballControls

```javascript
import { TrackballControls } from "three/addons/controls/TrackballControls.js";

const controls = new TrackballControls(camera, renderer.domElement);
controls.rotateSpeed = 2.0;
controls.zoomSpeed = 1.2;
controls.panSpeed = 0.8;
controls.staticMoving = true; // sin inercia; si no, se usa dynamicDampingFactor (0.2 por defecto)

function animate() {
  controls.update(); // sin argumento delta; llama a controls.handleResize() después de redimensionar el canvas
  renderer.render(scene, camera);
}
renderer.setAnimationLoop(animate);
```

## TransformControls

Un gizmo para mover, rotar y escalar objetos. El objeto de controles no es un Object3D; el gizmo que dibuja debe añadirse a la escena por separado.

```javascript
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { TransformControls } from "three/addons/controls/TransformControls.js";

const orbitControls = new OrbitControls(camera, renderer.domElement);

const transformControls = new TransformControls(camera, renderer.domElement);
scene.add(transformControls.getHelper()); // el gizmo; añadir los controles en sí solo registra un error

transformControls.attach(mesh); // muestra el gizmo sobre este objeto
transformControls.setMode("translate"); // "translate" | "rotate" | "scale"
transformControls.setSpace("local");    // "local" | "world"; la escala siempre actúa en local
transformControls.setSize(0.8);
transformControls.setTranslationSnap(0.5);
transformControls.setRotationSnap(THREE.MathUtils.degToRad(15));
transformControls.setScaleSnap(0.25);

transformControls.addEventListener("dragging-changed", (event) => {
  orbitControls.enabled = !event.value; // pausa la órbita mientras se arrastra el gizmo
});
transformControls.addEventListener("objectChange", () => {
  console.log(mesh.position); // se dispara mientras el gizmo mueve el objeto
});

window.addEventListener("keydown", (event) => {
  if (event.key === "g") transformControls.setMode("translate");
  if (event.key === "r") transformControls.setMode("rotate");
  if (event.key === "s") transformControls.setMode("scale");
  if (event.key === "Escape") transformControls.detach(); // oculta el gizmo
});
```

## DragControls

Arrastra objetos directamente: arrastrar con el botón izquierdo o central mueve el objeto en un plano paralelo a la pantalla, y arrastrar con el derecho lo rota alrededor de los ejes arriba y derecha de la cámara.

```javascript
import { DragControls } from "three/addons/controls/DragControls.js";

const dragControls = new DragControls([mesh], camera, renderer.domElement);
dragControls.rotateSpeed = 1; // por defecto
dragControls.mouseButtons = { LEFT: THREE.MOUSE.PAN, MIDDLE: THREE.MOUSE.PAN, RIGHT: THREE.MOUSE.ROTATE }; // el mapa por defecto
// transformGroup = true arrastra en su lugar el Group más externo por encima del impacto (pasa objects = [group]); event.object es entonces ese Group, que no tiene material, así que usa event.object.material?.emissive en los manejadores

dragControls.addEventListener("dragstart", (event) => {
  event.object.material.emissive?.set(0x333333);
});
dragControls.addEventListener("drag", (event) => {
  event.object.position.y = 0; // limita al suelo durante el arrastre
});
dragControls.addEventListener("dragend", (event) => {
  event.object.material.emissive?.set(0x000000);
});

// El selector integrado: dragControls.raycaster. Los objetos arrastrados: dragControls.objects.
```

## Selección

```javascript
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
const selectable = [mesh];
let selected = null;

function setPointerFromEvent(event) {
  const rect = renderer.domElement.getBoundingClientRect();
  pointer.set(
    ((event.clientX - rect.left) / rect.width) * 2 - 1,
    -((event.clientY - rect.top) / rect.height) * 2 + 1,
  );
}

renderer.domElement.addEventListener("pointerdown", (event) => {
  setPointerFromEvent(event);
  raycaster.setFromCamera(pointer, camera);
  const hit = raycaster.intersectObjects(selectable, false)[0];
  if (selected) selected.material.emissive.set(0x000000); // deselecciona la malla anterior
  selected = hit ? hit.object : null;
  if (selected) selected.material.emissive.set(0x444444);
});

renderer.domElement.addEventListener("pointermove", (event) => {
  setPointerFromEvent(event);
  raycaster.setFromCamera(pointer, camera);
  const hit = raycaster.intersectObjects(selectable, false)[0];
  document.body.style.cursor = hit ? "pointer" : "default"; // respuesta visual al pasar el ratón
});
```

Al desmontar, conserva referencias con nombre a los manejadores para poder hacer `removeEventListener`, y llama a `controls.dispose()` en cada control y a `timer.dispose()` en el timer.

### Selección por caja

`SelectionBox` selecciona los objetos cuyo centro de esfera envolvente cae dentro de un rectángulo en espacio de pantalla; `SelectionHelper` dibuja el rectángulo y sigue el arrastre.

```javascript
import { SelectionBox } from "three/addons/interactive/SelectionBox.js";
import { SelectionHelper } from "three/addons/interactive/SelectionHelper.js";

const selectionBox = new SelectionBox(camera, scene);
const helper = new SelectionHelper(renderer, "selectBox"); // un div con esta clase: dale a .selectBox position: fixed, un borde y un fondo en el CSS, o no se verá nada

function ndc(event) {
  return new THREE.Vector3(
    (event.clientX / window.innerWidth) * 2 - 1,
    -(event.clientY / window.innerHeight) * 2 + 1,
    0.5,
  );
}

document.addEventListener("pointerdown", (event) => {
  selectionBox.startPoint.copy(ndc(event));
});

document.addEventListener("pointermove", (event) => {
  if (helper.isDown) selectionBox.endPoint.copy(ndc(event));
});

document.addEventListener("pointerup", (event) => {
  selectionBox.endPoint.copy(ndc(event));
  const selected = selectionBox.select(); // los impactos de InstancedMesh y BatchedMesh van a selectionBox.instances y .batches
  console.log(selected);
});

// al desmontar: helper.dispose() elimina los listeners del helper y su elemento rectángulo
```

## Coordenadas de pantalla y del mundo

```javascript
// Del mundo a la pantalla: proyecta y luego transforma NDC (-1..1) a píxeles CSS
const ndc = mesh.getWorldPosition(new THREE.Vector3()).project(camera);
const screenX = ((ndc.x + 1) / 2) * window.innerWidth;
const screenY = ((-ndc.y + 1) / 2) * window.innerHeight;
// ndc.z fuera de [-1, 1] significa que el punto queda fuera del rango near-far
```

```javascript
// De la pantalla al mundo: desproyecta en un rayo y avanza por él hasta el plano z = 0
const worldPoint = new THREE.Vector3(0.1, 0.2, 0.5).unproject(camera);
const direction = worldPoint.sub(camera.position).normalize();
const distance = -camera.position.z / direction.z; // el rayo no alcanza el plano cuando direction.z es 0
const world = camera.position.clone().addScaledVector(direction, distance);
// El mismo resultado sale de un Raycaster construido con setFromCamera e intersectPlane
```

## WebGPU y TSL
Los controles y el Raycaster no dependen del renderer: el código de selección y de control de cámara de arriba funciona sin cambios con WebGPURenderer. El Raycaster comprueba la geometría en la CPU, así que nunca ve el desplazamiento de `positionNode`; selecciona sobre una malla proxy sin desplazar.
```javascript
import * as THREE from "three/webgpu";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
const renderer = new THREE.WebGPURenderer({ antialias: true }); await renderer.init(); // obligatorio antes de cualquier otro uso
renderer.setPixelRatio(window.devicePixelRatio); renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene(); scene.background = new THREE.Color(0x111318); // el canvas de WebGPU es transparente por defecto
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 100); camera.position.set(0, 1.5, 5);
scene.add(new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshBasicMaterial({ color: 0x3a86ff }))); // sin iluminación: no hace falta luz
const controls = new OrbitControls(camera, renderer.domElement);
const timer = new THREE.Timer(); timer.connect(document);
renderer.setAnimationLoop(function animate() {
  timer.update();
  controls.update(timer.getDelta());
  renderer.render(scene, camera);
});
```

## Errores comunes

- `scene.add(transformControls)` → `scene.add(transformControls.getHelper())`: TransformControls extiende Controls, un EventDispatcher y no un Object3D, así que esto registra un error y el gizmo nunca aparece.
- `new OrbitControls(camera)` → `new OrbitControls(camera, renderer.domElement)`: el constructor conecta sus listeners al elemento; sin él los controles nunca reciben entrada.
- `controls.update(clock.getDelta())` → `timer.update(); controls.update(timer.getDelta())`: Clock está obsoleto desde r183; crea un Timer, conéctalo y actualízalo lo primero en cada fotograma.
- `import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js"` → `import { OrbitControls } from "three/addons/controls/OrbitControls.js"`: los import maps documentados apuntan `three/addons/` a examples/jsm/ y no definen ninguna clave `three/examples/`, así que este especificador no se resuelve en el navegador.
- `requestAnimationFrame(animate)` → `renderer.setAnimationLoop(animate)`: la documentación de ambos renderers lo recomienda frente a un bucle manual, y entrega los fotogramas a la sesión WebXR cuando esta empieza.
- `flyControls.update()` → `flyControls.update(timer.getDelta())`: FlyControls y FirstPersonControls escalan el movimiento con el delta, así que sin él la posición pasa a NaN.
- `orbitControls.update()` → `orbitControls.update(timer.getDelta())`: sin delta, la velocidad de autoRotate depende de la frecuencia de refresco de la pantalla.
- `mesh.layers.set(1)` → `mesh.layers.enable(1)`: `set` reemplaza la máscara y saca la malla de la capa 0, así que la cámara por defecto deja de renderizarla.
- `hit.face instanceof THREE.Face3` → `hit.face.normal`: la cara de la intersección es un objeto plano `{ a, b, c, normal, materialIndex }`; Face3 no existe.
- `const moveForward = false` → `let moveForward = false`: el manejador de keydown reasigna la bandera, y asignar a una const lanza un TypeError.
- `controls.getObject()` → `controls.object`: PointerLockControls.getObject() se eliminó en r168; los controles gestionan la cámara pasada al constructor.
- `dragControls.getObjects()` → `dragControls.objects`: eliminado en r168; getRaycaster() pasó a ser la propiedad raycaster del mismo modo.
- `dragControls.activate()` → `dragControls.connect(renderer.domElement)`: renombrado desde activate() en r168 (deactivate() pasó a ser disconnect()), y connect() necesita el elemento: sin él lanza un TypeError, igual que los nombres antiguos.
- `firstPersonControls.activeLook = false` → `firstPersonControls.lookSpeed = 0`: FirstPersonControls no tiene la propiedad activeLook, así que asignarla no hace nada y la mirada por arrastre sigue activa.

## Véase también

- `references/fundamentals.md` - escenas, cámaras, configuración del renderer y el bucle de animación
- `references/animation.md` - animar objetos en respuesta a la interacción
- `references/postprocessing.md` - efectos de contorno y bloom para resaltar la selección
- `references/loaders.md` - carga de los modelos glTF que haces interactivos
- `references/react-three-fiber.md` - props de eventos de puntero y controles de drei cuando la escena está escrita en React
