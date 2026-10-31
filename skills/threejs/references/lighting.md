# Iluminación en Three.js

Dirigido a three.js r186. Los ejemplos usan WebGLRenderer; la sección de WebGPU y TSL usa WebGPURenderer.

## Inicio rápido

```javascript
import * as THREE from "three";

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(4, 3, 8);

// Una única luz direccional: la intensidad es un simple multiplicador, sin atenuación por distancia
const dirLight = new THREE.DirectionalLight(0xffffff, 3);
dirLight.position.set(5, 10, 5);
scene.add(dirLight);

const floor = new THREE.Mesh(
  new THREE.PlaneGeometry(20, 20),
  new THREE.MeshStandardMaterial({ color: 0x808080 })
);
floor.rotation.x = -Math.PI / 2;
scene.add(floor);

const mesh = new THREE.Mesh(
  new THREE.BoxGeometry(1, 1, 1),
  new THREE.MeshStandardMaterial({ color: 0x3a76c4 })
);
scene.add(mesh);

// Las sombras necesitan tres interruptores: el renderer, la luz y los meshes que proyectan y reciben
renderer.shadowMap.enabled = true;
dirLight.castShadow = true;
mesh.castShadow = true;
floor.receiveShadow = true;

function animate() {
  renderer.render(scene, camera);
}

renderer.setAnimationLoop(animate);
```

## Tipos de luz y unidades

| Luz | Sombras | Intensidad | Notas |
|---|---|---|---|
| AmbientLight | no | multiplicador | Relleno plano desde todas las direcciones |
| HemisphereLight | no | multiplicador | Color del cielo desde arriba, color del suelo desde abajo |
| DirectionalLight | sí | multiplicador | Rayos paralelos (sol); ilumina hacia su target |
| SunLight (addon) | sí, en cascada | multiplicador | El frustum de sombra se ajusta a la vista automáticamente |
| PointLight | sí, seis caras | candelas | Atenuación con el cuadrado inverso (decay 2) |
| SpotLight | sí | candelas | Cono; atenuación con el cuadrado inverso (decay 2) |
| RectAreaLight | no | nits | Solo MeshStandardMaterial y MeshPhysicalMaterial |
| LightProbe | no | multiplicador | Ambiente en armónicos esféricos, normalmente precalculado |

La intensidad de PointLight y SpotLight se mide en candelas con atenuación según el cuadrado inverso (`decay` vale 2 por defecto): una luz de 1 candela a 5 unidades aporta 1/25, así que los valores útiles dependen de la distancia y suelen llegar a las centenas (los ejemplos de la documentación oficial usan de 80 a 1000). `light.power` fija lo mismo en lúmenes. `light.distance` es un rango de corte suave (0 significa sin límite). Las intensidades de las luces direccional, ambiental y hemisférica son simples multiplicadores sin unidad. La intensidad de RectAreaLight se mide en nits (candelas por metro cuadrado).

## Ambiental y hemisférica

```javascript
// AmbientLight(color, intensity): un multiplicador plano sobre todos los materiales iluminados
const ambient = new THREE.AmbientLight(0x404040, 0.5);
scene.add(ambient);

// HemisphereLight(skyColor, groundColor, intensity)
const hemi = new THREE.HemisphereLight(0x87ceeb, 0x8b6f47, 0.6);
scene.add(hemi);
```

## DirectionalLight

```javascript
// DirectionalLight(color, intensity): rayos paralelos desde la posición hacia el target; la distancia solo importa para la cámara de sombra
const dirLight = new THREE.DirectionalLight(0xffffff, 3);
dirLight.position.set(5, 10, 5);

// Ilumina desde su posición hacia el target; añade el target a la escena cuando lo muevas
dirLight.target.position.set(0, 0, 0);
scene.add(dirLight.target);
scene.add(dirLight);
```

### SunLight: sombras en cascada automáticas

`SunLight` (`three/addons/lights/SunLight.js`) es una luz paralela con dos mapas de sombra en cascada, pensada para escenas grandes. No tiene target: ilumina desde su posición hacia el origen, por defecto en vertical hacia abajo. Con WebGLRenderer funciona directamente; con WebGPURenderer hay que registrarla antes (véase WebGPU y TSL).

```javascript
import { SunLight } from "three/addons/lights/SunLight.js";

const sun = new SunLight(0xfff2e3, 3);
sun.position.set(100, 160, 60);
sun.castShadow = true;
scene.add(sun);
```

Las cascadas se ajustan automáticamente a porciones del frustum de visión de la cámara, hasta `sun.shadow.camera.far` o el plano lejano de la cámara de visión, lo que sea menor. `shadow.camera.left/right/top/bottom` se ignoran; el `mapSize` por defecto es 1024 × 1024 por cascada. No hay frustum de sombra que ajustar a mano.

## PointLight y SpotLight

```javascript
// PointLight(color, intensity en candelas, distance, decay)
const bulb = new THREE.PointLight(0xffdcb0, 100, 20, 2);
bulb.position.set(0, 4, 0);
scene.add(bulb);

// SpotLight(color, intensity en candelas, distance, angle, penumbra, decay)
const deskLamp = new THREE.SpotLight(0xffffff, 250, 30, Math.PI / 6, 0.4, 2);
deskLamp.position.set(2, 5, 0);
deskLamp.target.position.set(0, 0, 0);
scene.add(deskLamp.target);
scene.add(deskLamp);

// Mejor en lúmenes: power escribe por ti la intensidad en candelas
bulb.power = 800;
```

`angle` es el semiángulo del cono en radianes, con un máximo de Math.PI / 2; `penumbra` (de 0 a 1) suaviza el borde del cono.

## RectAreaLight

Un emisor rectangular para iluminación suave tipo ventana o tira. Solo ilumina MeshStandardMaterial y MeshPhysicalMaterial, y no puede proyectar sombras.

```javascript
import { RectAreaLightHelper } from "three/addons/helpers/RectAreaLightHelper.js";
import { RectAreaLightUniformsLib } from "three/addons/lights/RectAreaLightUniformsLib.js";

// WebGLRenderer: añade las texturas de consulta LTC a los uniforms del renderer, una sola vez
RectAreaLightUniformsLib.init();

// RectAreaLight(color, intensity en nits, width, height)
const windowLight = new THREE.RectAreaLight(0xffffff, 5, 4, 10);
windowLight.position.set(-5, 5, 0);
windowLight.lookAt(0, 0, 0); // emite desde su cara frontal
scene.add(windowLight);

// El helper debe añadirse como hijo de la luz
const helper = new RectAreaLightHelper(windowLight);
windowLight.add(helper);
```

Con WebGPURenderer, registra las texturas LTC con `RectAreaLightTexturesLib` en su lugar (véase WebGPU y TSL).

## Sombras

```javascript
// 1. Renderer: los mapas de sombra están desactivados por defecto; PCFShadowMap es el filtrado suave por defecto,
// VSMShadowMap desenfoca el propio mapa, BasicShadowMap da bordes duros
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFShadowMap;

// 2. Luz
const dirLight = new THREE.DirectionalLight(0xffffff, 3);
dirLight.position.set(5, 10, 5);
dirLight.castShadow = true;
scene.add(dirLight);

// 3. Objetos
mesh.castShadow = true;
mesh.receiveShadow = true;
```

Un `shadow.radius` mayor que 1 amplía el filtro PCF y el desenfoque VSM; no tiene efecto con BasicShadowMap. VSM también expone `shadow.blurSamples` (por defecto 8), y las sombras de PointLight no admiten VSM en absoluto: WebGLRenderer avisa y omite la sombra de esa luz. PCFSoftShadowMap está obsoleto: avisa y recurre a PCFShadowMap, que ya es suave. Con VSMShadowMap, todo mesh que recibe sombras también las proyecta.

### Ajustar una sombra direccional

```javascript
const dirLight = new THREE.DirectionalLight(0xffffff, 3);
dirLight.position.set(5, 10, 5); // todo objeto que proyecte sombra debe estar entre near y far desde aquí
dirLight.castShadow = true;

// La cámara de sombra está en la posición de la luz y mira a su target: near y far
// son distancias desde la luz; left/right/top/bottom encuadran la zona alrededor del target
const shadowCam = dirLight.shadow.camera;
shadowCam.left = -10;
shadowCam.right = 10;
shadowCam.top = 10;
shadowCam.bottom = -10;
shadowCam.near = 0.5;
shadowCam.far = 50;
shadowCam.updateProjectionMatrix(); // necesario cada vez que cambian después del primer render

dirLight.shadow.mapSize.set(2048, 2048); // potencias de dos

// Acné: normalBias desplaza la consulta a lo largo de la normal de la superficie (luz rasante);
// bias desplaza la profundidad que se compara con el mapa: empieza con valores minúsculos, los negativos combaten el acné
dirLight.shadow.normalBias = 0.02;
dirLight.shadow.bias = -0.0001;

// Aclara las sombras sin añadir luces de relleno: 0 las elimina, 1 es oscuridad total
dirLight.shadow.intensity = 0.7;
```

### Las cámaras de sombra de point y spot son derivadas

El renderer reconstruye estas cámaras en cada pasada de sombra: el fov de sombra de un spot es `2 × angle × shadow.focus` (en grados) y su far sale de `light.distance`; el far de una luz puntual también sale de `light.distance`. El fov siempre se sobrescribe, y un `far` manual solo sobrevive mientras `distance` sea 0. Controla el cono con `angle` y `shadow.focus`, y el alcance con `distance`.

```javascript
const deskLamp = new THREE.SpotLight(0xffffff, 250, 30);
deskLamp.castShadow = true;
deskLamp.shadow.mapSize.set(1024, 1024);
deskLamp.shadow.focus = 0.9; // fov de la sombra como fracción del cono de la luz
deskLamp.shadow.bias = -0.0001;
```

Visualiza la cámara de sombra de una luz direccional o spot con `new THREE.CameraHelper(light.shadow.camera)` añadido a la escena, y llama al `update()` del helper tras modificar la cámara.

### Sombras de contacto (falsas, baratas)

Un mapa de sombra por luz es excesivo para dar sensación de apoyo en el suelo; una mancha con degradado radial cuesta un solo quad texturizado.

```javascript
// Una mancha suave bajo el objeto: sin mapa de sombra, funciona con ambos renderers
const size = 128;
const canvas = document.createElement("canvas");
canvas.width = canvas.height = size;
const ctx = canvas.getContext("2d");
const gradient = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
gradient.addColorStop(0, "rgba(0,0,0,0.6)");
gradient.addColorStop(1, "rgba(0,0,0,0)");
ctx.fillStyle = gradient;
ctx.fillRect(0, 0, size, size);

const shadowTexture = new THREE.CanvasTexture(canvas);
shadowTexture.colorSpace = THREE.SRGBColorSpace; // un canvas usado como mapa de color es sRGB

const blob = new THREE.Mesh(
  new THREE.PlaneGeometry(2, 2),
  new THREE.MeshBasicMaterial({ map: shadowTexture, transparent: true, depthWrite: false })
);
blob.rotation.x = -Math.PI / 2;
blob.position.y = 0.001; // justo por encima del suelo para evitar z-fighting
scene.add(blob);
```

Para una mancha que siga la silueta del objeto, renderiza la profundidad desde abajo en un render target y desenfócala: el ejemplo oficial `webgl_shadow_contact` lo hace con `HorizontalBlurShader` y `VerticalBlurShader` de `three/addons/shaders/`.

## Helpers de luz

```javascript
const dirLight = new THREE.DirectionalLight(0xffffff, 3);
const hemi = new THREE.HemisphereLight(0x87ceeb, 0x8b6f47, 0.6);
const bulb = new THREE.PointLight(0xffdcb0, 100, 20);
const deskLamp = new THREE.SpotLight(0xffffff, 250, 30);
scene.add(dirLight, hemi, bulb, deskLamp);

// Los helpers incluidos son objetos: añádelos a la escena
const dirHelper = new THREE.DirectionalLightHelper(dirLight, 5);
const pointHelper = new THREE.PointLightHelper(bulb, 0.5);
const spotHelper = new THREE.SpotLightHelper(deskLamp);
const hemiHelper = new THREE.HemisphereLightHelper(hemi, 5);
scene.add(dirHelper, pointHelper, spotHelper, hemiHelper);
```

Todos los helpers de luz copian el color de la luz solo en `update()`, y DirectionalLightHelper, SpotLightHelper y HemisphereLightHelper también se reorientan solo ahí: llama a `update()` tras cambiar el color de una luz, y tras mover o reorientar una de esas tres.

## Iluminación de entorno (IBL)

```javascript
import { HDRLoader } from "three/addons/loaders/HDRLoader.js";

// Ambos renderers prefiltran por sí mismos un entorno equirectangular: asígnalo directamente
const hdr = await new HDRLoader().loadAsync("sunset.hdr");
hdr.mapping = THREE.EquirectangularReflectionMapping;

scene.environment = hdr; // ilumina la escena
scene.background = hdr; // opcional: también lo dibuja detrás de la escena
scene.environmentIntensity = 1; // escala solo la contribución a la iluminación
scene.environmentRotation.set(0, Math.PI / 4, 0); // rota la iluminación
scene.backgroundBlurriness = 0; // desenfoca el fondo, no la iluminación
scene.backgroundIntensity = 1;
scene.backgroundRotation.set(0, 0, 0); // rota el fondo de forma independiente
```

Ambos renderers iluminan MeshStandardMaterial y MeshPhysicalMaterial desde `scene.environment`; WebGLRenderer también ilumina MeshLambertMaterial y MeshPhongMaterial, WebGPURenderer no. Reserva `PMREMGenerator` para entornos generados a partir de una escena; sobre un fichero equirectangular solo repite el prefiltrado que el renderer ya hace:

```javascript
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";

const pmrem = new THREE.PMREMGenerator(renderer);
const room = new RoomEnvironment();
scene.environment = pmrem.fromScene(room, 0.04).texture;
room.dispose(); // libera las geometrías y materiales de la sala
pmrem.dispose();
```

Una cube texture funciona como entorno sin ninguna línea de mapping:

```javascript
const cubeEnv = await new THREE.CubeTextureLoader().loadAsync([
  "px.jpg",
  "nx.jpg",
  "py.jpg",
  "ny.jpg",
  "pz.jpg",
  "nz.jpg",
]);

scene.environment = cubeEnv;
scene.background = cubeEnv;
```

## Light probes

```javascript
import { LightProbeGenerator } from "three/addons/lights/LightProbeGenerator.js";

// Precalcula los armónicos esféricos ambientales a partir de lo que ve una cube camera
const cubeCamera = new THREE.CubeCamera(0.1, 100, new THREE.WebGLCubeRenderTarget(256));
cubeCamera.update(renderer, scene);

const lightProbe = await LightProbeGenerator.fromCubeRenderTarget(renderer, cubeCamera.renderTarget);
scene.add(lightProbe);
```

`LightProbeGenerator.fromCubeTexture(cubeTexture)` obtiene una de forma síncrona a partir de una cube texture ya cargada. Para un ambiente que dependa de la posición, precalcula en su lugar una rejilla 3D: `LightProbeGridWebGL` con WebGLRenderer, `LightProbeGrid` con WebGPURenderer (`three/addons/lighting/`). Con WebGPURenderer, crea el cube render target con `CubeRenderTarget` de `three/webgpu`.

```javascript
import { LightProbeGridWebGL } from "three/addons/lighting/LightProbeGridWebGL.js";

// Un volumen de 10 × 4 × 10 centrado en su posición, con size + 1 probes por eje por defecto
const probeGrid = new LightProbeGridWebGL(10, 4, 10);
probeGrid.position.set(0, 2, 0);
scene.add(probeGrid);
probeGrid.bake(renderer, scene); // vuelve a precalcular cuando cambie la iluminación estática
```

## Configuraciones habituales

```javascript
// Iluminación de tres puntos: principal (key), relleno (fill) y contraluz (rim)
const keyLight = new THREE.DirectionalLight(0xffffff, 2);
keyLight.position.set(5, 6, 4);

const fillLight = new THREE.DirectionalLight(0xffffff, 0.5);
fillLight.position.set(-5, 3, 5);

const backLight = new THREE.DirectionalLight(0xffffff, 1);
backLight.position.set(-4, 5, -6);

scene.add(keyLight, fillLight, backLight);
```

```javascript
import { SunLight } from "three/addons/lights/SunLight.js";

// Luz diurna exterior: sol con sombras en cascada más un degradado de cielo
const sun = new SunLight(0xfff2e3, 3);
sun.position.set(100, 160, 60);
sun.castShadow = true;

const sky = new THREE.HemisphereLight(0x87ceeb, 0x8b6f47, 0.5);

scene.add(sun, sky);
```

## Animar luces

```javascript
// Timer gestiona el tiempo por fotograma: primero update(), luego lee el tiempo
const timer = new THREE.Timer();
timer.connect(document); // evita deltas enormes tras cambiar de pestaña

const lamp = new THREE.PointLight(0xffd0a0, 100, 20);
scene.add(lamp);

function animate() {
  timer.update();

  const t = timer.getElapsed();
  lamp.position.set(Math.cos(t) * 4, 3, Math.sin(t) * 4);
  lamp.intensity = 100 + Math.sin(t * 2) * 30;

  renderer.render(scene, camera);
}

renderer.setAnimationLoop(animate);
```

## Rendimiento

- Ambos renderers compilan el conjunto de luces dentro de cada material iluminado: añadir o quitar una luz (una AmbientLight solo con WebGPURenderer), o activar y desactivar `castShadow`, los recompila. Elimina las luces que no uses; enciende y apaga una luz en tiempo de ejecución mediante su `intensity`. Con WebGPURenderer, `DynamicLighting` mantiene los materiales compilados cuando entran y salen luces ambientales, hemisféricas, direccionales, puntuales o spot, siempre que no proyecten sombra y ningún spot tenga `map`, y `ClusteredLighting` escala a muchas luces puntuales (véase WebGPU y TSL).
- Cada luz que proyecta sombras añade pasadas de profundidad (seis por luz puntual). Deja `castShadow` desactivado donde nada necesite la sombra.
- Escenas estáticas: renderiza la sombra de una luz bajo demanda con `light.shadow.autoUpdate = false; light.shadow.needsUpdate = true;` y vuelve a poner `light.shadow.needsUpdate = true` cuando algo se mueva (en ambos renderers; WebGLRenderer además tiene el global `renderer.shadowMap.autoUpdate`).
- Mantén ajustados los frustums de sombra direccionales, o pásate a SunLight, que los ajusta a la vista automáticamente.
- Las luces no se filtran por mesh mediante layers: los layers de una luz solo se comprueban contra los de la cámara. Para iluminar solo meshes concretos, usa `material.lightsNode` con WebGPURenderer.

## WebGPU y TSL

Las clases de luz, los ajustes de sombra y las propiedades de entorno de la escena descritas arriba se trasladan a WebGPURenderer, salvo las piezas exclusivas de WebGL que esta sección sustituye: RectAreaLightUniformsLib, WebGLCubeRenderTarget (usa `CubeRenderTarget`), LightProbeGridWebGL (usa `LightProbeGrid`) y el global `renderer.shadowMap.autoUpdate`. SunLight debe registrarse, y `scene.environment` no ilumina aquí los materiales Lambert ni Phong.

```javascript
import * as THREE from "three/webgpu";

const renderer = new THREE.WebGPURenderer({ antialias: true });
await renderer.init(); // antes de cualquier otro uso del renderer
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x101010); // el canvas de WebGPU es transparente por defecto

const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(4, 3, 8);

renderer.shadowMap.enabled = true;
const dirLight = new THREE.DirectionalLight(0xffffff, 3);
dirLight.castShadow = true;
scene.add(dirLight);

function animate() {
  renderer.render(scene, camera);
}

renderer.setAnimationLoop(animate);
```

```javascript
import * as THREE from "three/webgpu";
import { RectAreaLightTexturesLib } from "three/addons/lights/RectAreaLightTexturesLib.js";
import { SunLight } from "three/addons/lights/SunLight.js";
import { SunLightNode } from "three/addons/lights/SunLightNode.js";
import { ClusteredLighting } from "three/addons/lighting/ClusteredLighting.js";

// RectAreaLight: registra las texturas LTC una sola vez (sustituye a RectAreaLightUniformsLib)
THREE.RectAreaLightNode.setLTC(RectAreaLightTexturesLib.init());
// SunLight: registra su implementación de nodo una sola vez
renderer.library.addLight(SunLightNode, SunLight);
// Muchas luces puntuales: shading Forward+ por clústeres (DynamicLighting, en cambio, evita recompilaciones cuando entran y salen luces sin sombra)
renderer.lighting = new ClusteredLighting();
```

```javascript
import * as THREE from "three/webgpu";
import { lights } from "three/tsl";

const keyLight = new THREE.PointLight(0x66aaff, 120, 20);
scene.add(keyLight);

// Un material iluminado solo por keyLight, que ignora el resto de luces de la escena
const material = new THREE.MeshStandardNodeMaterial();
material.lightsNode = lights([keyLight]);
```

Sombras de color: con `renderer.shadowMap.transmitted = true`, los objetos que proyectan sombra escriben color y alfa en el mapa de sombra, a partir de `material.castShadowNode` (un vec4) o del alfa de `map` y `colorNode`. `material.receivedShadowNode` (una Fn del valor de sombra) cambia cómo aplica sus sombras un receptor y funciona sin la opción anterior.

## Errores comunes

- `light.layers.set(1);` → `material.lightsNode = lights([keyLight, fillLight]);`: las luces no se filtran por mesh mediante layers; los layers de una luz se comprueban contra los de la cámara, así que esto apaga la luz en toda la escena; la selección por material requiere un node material, con WebGPURenderer o, con WebGLRenderer, mediante el addon WebGLNodesHandler.
- `new THREE.PointLight(0xffffff, 1, 100);` → `new THREE.PointLight(0xffffff, 100, 20);`: la intensidad de point y spot está en candelas con atenuación según el cuadrado inverso, así que 1 apenas aporta nada a distancia; los valores típicos llegan a las centenas.
- `renderer.useLegacyLights = true;` → `const bulb = new THREE.PointLight(0xffffff, 100, 20);`: las unidades de luz heredadas ya no existen y ni useLegacyLights ni physicallyCorrectLights hacen nada; reajusta las luces point y spot en candelas.
- `renderer.shadowMap.type = THREE.PCFSoftShadowMap;` → `renderer.shadowMap.type = THREE.PCFShadowMap;`: PCFSoftShadowMap quedó obsoleto en r182; ambos renderers avisan y recurren a PCFShadowMap, que ya es suave.
- `lightProbe.copy(LightProbeGenerator.fromCubeRenderTarget(renderer, rt));` → `lightProbe.copy(await LightProbeGenerator.fromCubeRenderTarget(renderer, rt));`: la llamada es asíncrona y devuelve una Promise, que copy() no sabe leer.
- `new ContactShadows({ opacity: 0.5 });` → `new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.MeshBasicMaterial({ transparent: true, map: blobTexture }));`: three.js no tiene ninguna clase ContactShadows (es un componente de drei); simula la sombra de contacto con un plano de degradado radial.
- `scene.environment = pmremGenerator.fromEquirectangular(texture).texture;` → `texture.mapping = THREE.EquirectangularReflectionMapping; scene.environment = texture;`: el renderer prefiltra por sí mismo un entorno equirectangular, así que el PMREM manual no añade calidad; reserva PMREMGenerator para fromScene.
- `scene.background = hdr;` → `hdr.mapping = THREE.EquirectangularReflectionMapping; scene.background = hdr;`: HDRLoader devuelve una textura con mapeo UV, así que sin esa línea el fondo se dibuja como una imagen plana en espacio de pantalla.
- `import { RGBELoader } from "three/examples/jsm/loaders/RGBELoader.js";` → `import { HDRLoader } from "three/addons/loaders/HDRLoader.js";`: RGBELoader pasó a llamarse HDRLoader en r180, y los addons deben importarse desde three/addons/ para que el import map los resuelva.
- `spotLight.shadow.camera.fov = 30;` → `spotLight.shadow.focus = 0.9;`: el fov de la cámara de sombra se recalcula en cada pasada como 2 × angle × focus en grados, así que contrólalo mediante el angle y el focus de la luz.
- `const lamp = new THREE.PointLight(0xffffff, 100, 20); lamp.shadow.camera.far = 50;` → `const lamp = new THREE.PointLight(0xffffff, 100, 50);`: un distance distinto de cero sobrescribe el far de la cámara de sombra en cada pasada, así que fija el alcance de la sombra mediante distance; un far manual solo se conserva mientras distance sea 0.
- `material.envMapIntensity = 0.5;` → `scene.environmentIntensity = 0.5;`: envMapIntensity escala solo el envMap propio de un material, no scene.environment.
- `const clock = new THREE.Clock();` → `const timer = new THREE.Timer(); timer.connect(document);`: Clock quedó obsoleto en r183; llama a timer.update() en cada fotograma antes de getDelta() o getElapsed().
- `RectAreaLightUniformsLib.init();` → `THREE.RectAreaLightNode.setLTC(RectAreaLightTexturesLib.init());`: con WebGPURenderer la librería de uniforms nunca se lee, y el nodo de la luz desreferencia una librería LTC nula hasta que se registran las texturas.

## Véase también

- references/materials.md: cómo responden los materiales a la luz (roughness, metalness, material.envMap).
- references/textures.md: carga de mapas de entorno y ajuste del espacio de color de las texturas.
- references/shaders.md: efectos GLSL personalizados como bordes fresnel, ampliar materiales integrados iluminados con onBeforeCompile y materiales de nodo iluminados en TSL.
- references/postprocessing.md: bloom y otros efectos próximos a la luz.
- references/fundamentals.md: configuración del renderer, tone mapping y exposición para luces con escala física y entornos HDR.
