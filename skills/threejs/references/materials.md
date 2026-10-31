# Materiales en Three.js

Pensado para three.js r186. Los ejemplos usan WebGLRenderer; la sección de WebGPU y TSL usa WebGPURenderer.

## Inicio rápido

```javascript
import * as THREE from "three";

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(0, 0, 3);

// Material PBR: la opción por defecto para superficies iluminadas y realistas
const material = new THREE.MeshStandardMaterial({
  color: 0x00aaff,
  roughness: 0.35,
  metalness: 0.1,
});
const mesh = new THREE.Mesh(new THREE.SphereGeometry(1, 48, 32), material);
scene.add(mesh);
scene.add(new THREE.HemisphereLight(0xffffff, 0x444444, 1)); // los materiales con iluminación se ven negros sin luces
const light = new THREE.DirectionalLight(0xffffff, 2);
light.position.set(3, 3, 3);
scene.add(light);

function animate() {
  mesh.rotation.y += 0.01;
  renderer.render(scene, camera);
}

renderer.setAnimationLoop(animate);
```

## Resumen de tipos de material

| Material | Caso de uso | Iluminación |
| -------------------- | ------------------------------------- | ------------------ |
| MeshBasicMaterial | Color sin iluminar, texturas, wireframes | Ninguna |
| MeshLambertMaterial | Superficies difusas mate | Difusa |
| MeshPhongMaterial | Plástico brillante, especular barato | Difusa + especular |
| MeshStandardMaterial | Flujo de trabajo PBR metal/rugosidad | PBR |
| MeshPhysicalMaterial | PBR más clearcoat, transmisión, sheen, iridiscencia | PBR |
| MeshToonMaterial | Cel shading | Escalones toon |
| MeshMatcapMaterial | Aspecto iluminado horneado en una textura matcap, sin necesidad de luces | Horneada |
| ShadowMaterial | Superficie transparente que muestra solo las sombras que recibe | Solo sombras |
| PointsMaterial | Nubes de puntos | Ninguna |
| LineBasicMaterial / LineDashedMaterial | Líneas | Ninguna |
| ShaderMaterial / RawShaderMaterial | GLSL personalizado, solo WebGLRenderer | Personalizada |

Las texturas de datos de color (map, emissiveMap, specularMap, sheenColorMap, specularColorMap, matcap LDR, un canvas o vídeo usado como color) necesitan `texture.colorSpace = THREE.SRGBColorSpace`, o los colores se ven desvaídos. Los mapas escalares (normal, bump, displacement, roughness, metalness, ao, alpha, gradientMap de toon) mantienen el valor por defecto. Los loaders HDR establecen su propio espacio de color.

## MeshBasicMaterial

Sin cálculos de iluminación. Rápido, siempre visible. Admite `envMap` con `reflectivity` (0 a 1) y `combine` (`THREE.MultiplyOperation`, `THREE.MixOperation`, `THREE.AddOperation`); `specularMap` (sRGB) enmascara la contribución del mapa de entorno.

```javascript
const map = await new THREE.TextureLoader().loadAsync("color.jpg");
map.colorSpace = THREE.SRGBColorSpace;

const material = new THREE.MeshBasicMaterial({
  color: 0xffffff, // se multiplica por el map
  map,
  transparent: true,
  opacity: 0.5,
  side: THREE.DoubleSide, // FrontSide (por defecto), BackSide, DoubleSide
  fog: true, // afectado por la niebla de la escena
});
```

## MeshLambertMaterial y MeshPhongMaterial

Lambert es solo difuso. Phong añade un brillo especular; es la alternativa barata cuando Standard resulta demasiado pesado.

```javascript
const lambert = new THREE.MeshLambertMaterial({
  color: 0x00ff00,
  emissive: 0x111111, // color de autoiluminación
  emissiveIntensity: 1,
});

const phong = new THREE.MeshPhongMaterial({
  color: 0x0000ff,
  specular: 0x111111, // color del brillo
  shininess: 30, // mayor = brillo más definido
  flatShading: false, // normales planas frente a suaves
});
```

Ambos admiten también `map`, `emissiveMap`, `specularMap` (sRGB; enmascara el reflejo del mapa de entorno, y el brillo en Phong), `normalMap`, `bumpMap`, `displacementMap`, `aoMap`, `envMap`, `envMapIntensity` y `envMapRotation`.

## MeshStandardMaterial (PBR)

Renderizado basado en física. Recomendado para resultados realistas.

```javascript
const map = await new THREE.TextureLoader().loadAsync("color.jpg");
map.colorSpace = THREE.SRGBColorSpace;
const ormMap = await new THREE.TextureLoader().loadAsync("orm.jpg"); // ORM de glTF: ao en rojo, roughness en verde, metalness en azul; escalar: deja el valor por defecto

const material = new THREE.MeshStandardMaterial({
  color: 0xffffff, // se multiplica por el map
  roughness: 1.0, // 0 = espejo, 1 = totalmente difuso; se multiplica por roughnessMap (verde)
  metalness: 1.0, // 0 = dieléctrico, 1 = metal; se multiplica por metalnessMap (azul), así que mantén 1 con un mapa
  map,
  roughnessMap: ormMap,
  metalnessMap: ormMap,
  normalMap: null, // detalle de superficie; se escala con normalScale (un Vector2)
  aoMap: ormMap, // oclusión ambiental (rojo); intensidad con aoMapIntensity
  displacementMap: null, // desplazamiento de vértices; se escala con displacementScale, desfase con displacementBias
  emissive: 0x000000,
  emissiveIntensity: 1,
  emissiveMap: null, // sRGB
  envMap: null, // o apóyate en scene.environment (ver más abajo)
  fog: true,
});
```

`lightMap` (con `lightMapIntensity`) hornea luz indirecta igual que aoMap hornea oclusión; un lightMap HDR o EXR es `LinearSRGBColorSpace`, que establecen los loaders.

### Canales UV: aoMap y lightMap leen el canal que elijas

Toda textura con mapeado UV muestrea el atributo seleccionado por `texture.channel`: 0 lee `uv` (el valor por defecto), 1 lee `uv1`, 2 lee `uv2`, 3 lee `uv3`. aoMap y lightMap no necesitan un segundo juego de UV: muestrean `uv` salvo que cambies `channel`. GLTFLoader carga `TEXCOORD_1` como `uv1` y establece `channel` por sí mismo.

```javascript
const aoMap = await new THREE.TextureLoader().loadAsync("ao.jpg"); // escalar: deja el valor por defecto
const material = new THREE.MeshStandardMaterial({ aoMap }); // muestrea uv: no hace falta ningún atributo extra

// Alternativa para un desenvolvido aparte (un AO o light map horneado): copia los pares u,v de tu baker en uv1
const bakedUv = new THREE.Float32BufferAttribute(mesh.geometry.attributes.position.count * 2, 2); // relleno de ceros hasta que copies los valores
mesh.geometry.setAttribute("uv1", bakedUv); mesh.material = material;
aoMap.channel = 1; // este material ahora muestrea uv1 en lugar de uv
```

## MeshPhysicalMaterial (PBR avanzado)

Extiende MeshStandardMaterial con funciones de capas y volumen. Existen variantes con textura para la mayoría: `clearcoatMap`, `clearcoatRoughnessMap`, `clearcoatNormalMap`, `transmissionMap`, `thicknessMap`, `iridescenceMap`, `iridescenceThicknessMap`, `sheenColorMap`, `sheenRoughnessMap`, `anisotropyMap`, `specularIntensityMap`, `specularColorMap`.

```javascript
const material = new THREE.MeshPhysicalMaterial({
  // Clearcoat (pintura de coche, laca)
  clearcoat: 1.0, // 0 = ninguna, 1 = capa completa
  clearcoatRoughness: 0.1,
  // Transmisión (vidrio, agua): refracta los objetos opacos y scene.background que tiene detrás
  transmission: 1.0, // 0 = opaco, 1 = totalmente transmisivo
  thickness: 0.5, // grosor del volumen para la refracción
  attenuationDistance: 1, // unidades del mundo; Infinity (el valor por defecto) = sin absorción
  attenuationColor: new THREE.Color(0xffaa66), // la luz blanca adopta este color tras attenuationDistance
  ior: 1.5, // índice de refracción, de 1 a 2.333
  // Sheen (tela, terciopelo)
  sheen: 1.0,
  sheenColor: new THREE.Color(0xffffff),
  sheenRoughness: 0.5,
  // Iridiscencia (pompas de jabón, manchas de aceite)
  iridescence: 1.0,
  iridescenceIOR: 1.3,
  iridescenceThicknessRange: [100, 400], // nanómetros
  // Anisotropía (metal cepillado); la dirección se controla con anisotropyRotation
  anisotropy: 1.0,
  // Dispersión (vidrio prismático); retrorreflectividad (señales de tráfico, equipamiento de seguridad)
  dispersion: 0.0,
  retroreflectivity: 0.0,
  // Anulaciones del especular: specularIntensity, specularColor (más sus mapas)
});
```

Vidrio: transmisión con una superficie lisa y algo detrás que refractar:

```javascript
const glass = new THREE.MeshPhysicalMaterial({
  color: 0xffffff,
  metalness: 0,
  roughness: 0,
  transmission: 1,
  thickness: 0.5,
  ior: 1.5,
});
// la transmisión refracta los objetos opacos y el fondo que tiene detrás; scene.environment añade sus reflejos
```

## MeshToonMaterial

Cel shading. El gradient map son datos que no son color: mantén su espacio de color por defecto.

```javascript
const steps = new Uint8Array([120, 200]); // dos escalones de sombreado
const gradientMap = new THREE.DataTexture(steps, 2, 1, THREE.RedFormat);
gradientMap.minFilter = THREE.NearestFilter; // escalones duros; LinearFilter los mezcla
gradientMap.magFilter = THREE.NearestFilter;
gradientMap.needsUpdate = true;

const material = new THREE.MeshToonMaterial({ color: 0x00ff00, gradientMap });
```

## MeshNormalMaterial y MeshDepthMaterial

```javascript
// Normales codificadas como RGB: depuración y aspectos planos ilustrativos
const normals = new THREE.MeshNormalMaterial({ flatShading: false, wireframe: false });

// Profundidad en escala de grises (BasicDepthPacking, el valor por defecto); RGBADepthPacking la empaqueta para leerla de vuelta en un shader
const depth = new THREE.MeshDepthMaterial();
```

## PointsMaterial

Para nubes de puntos. `size` está en píxeles; con `sizeAttenuation` (el valor por defecto, solo cámaras en perspectiva) se multiplica por la mitad del alto del canvas y se divide por la profundidad del punto en espacio de vista.

```javascript
const geometry = new THREE.BufferGeometry();
geometry.setAttribute("position", new THREE.Float32BufferAttribute([0, 0, 0, 1, 0.5, 0, 0.5, 1, 0], 3));

const material = new THREE.PointsMaterial({
  color: 0xffffff,
  size: 0.1,
  sizeAttenuation: true, // escala con la distancia
  alphaTest: 0.5, // con un map o alphaMap: descarta los fragmentos por debajo de este alpha
});

const points = new THREE.Points(geometry, material);
scene.add(points);
```

## LineBasicMaterial y LineDashedMaterial

WebGL y WebGPU siempre dibujan las primitivas de línea de 1 px de ancho; `linewidth`, `linecap` y `linejoin` solo afectan a SVGRenderer. Para líneas gruesas en WebGLRenderer usa `Line2` con `LineGeometry` y `LineMaterial` de `three/addons/lines/` (`linewidth` en píxeles); LineMaterial es un ShaderMaterial, así que WebGPURenderer necesita `Line2` de `three/addons/lines/webgpu/Line2.js`, que usa `Line2NodeMaterial`.

```javascript
const geometry = new THREE.BufferGeometry();
geometry.setAttribute("position", new THREE.Float32BufferAttribute([-1, 0, 0, 1, 0, 0], 3));

const solid = new THREE.LineBasicMaterial({ color: 0xffffff }); // siempre 1 px

const dashed = new THREE.LineDashedMaterial({ color: 0xffffff, dashSize: 0.5, gapSize: 0.25 });
const line = new THREE.Line(geometry, dashed);
line.computeLineDistances(); // obligatorio, o la línea se dibuja continua
scene.add(line);
```

## ShaderMaterial (solo WebGLRenderer)

GLSL personalizado con los uniforms de three.js inyectados por ti. Siempre se compila como GLSL ES 3.00: `texture()`, `textureLod()` y `dFdx` funcionan, y `texture2D` / `gl_FragColor` siguen como alias; deja `glslVersion` sin definir. ShaderMaterial, RawShaderMaterial y `onBeforeCompile` no tienen camino en WebGPURenderer; allí usa materiales de nodos y TSL.

```javascript
const timer = new THREE.Timer();
timer.connect(document); // se pausa cuando la pestaña está oculta

const material = new THREE.ShaderMaterial({
  uniforms: { time: { value: 0 } },
  vertexShader: `
    varying vec2 vUv;
    uniform float time;
    void main() {
      vUv = uv;
      vec3 pos = position;
      pos.z += sin(pos.x * 10.0 + time) * 0.1;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
    }
  `,
  fragmentShader: `
    varying vec2 vUv;
    uniform float time;
    void main() {
      vec3 col = 0.5 + 0.5 * cos(time + vUv.xyx * 3.0);
      gl_FragColor = vec4(col, 1.0);
    }
  `,
});

function animate() {
  timer.update(); // lo primero en cada fotograma, sin argumento
  material.uniforms.time.value = timer.getElapsed();
  renderer.render(scene, camera);
}
```

Declarados para ti en el shader: `modelMatrix`, `modelViewMatrix`, `projectionMatrix`, `viewMatrix`, `normalMatrix`, `cameraPosition`, y los atributos `position`, `normal`, `uv` (más `instanceMatrix` en un InstancedMesh, que aplicas tú mismo: `projectionMatrix * modelViewMatrix * instanceMatrix * vec4(pos, 1.0)`, y `color` con vertexColors). Los juegos de uv adicionales y `tangent` no están declarados: añade tú mismo `in vec2 uv1;`.

## RawShaderMaterial (solo WebGLRenderer)

No se antepone ninguna declaración (solo `#version` según glslVersion, los defines `SHADER_TYPE` y `SHADER_NAME`, y tus `defines`), pero el renderer sigue estableciendo `projectionMatrix`, `modelViewMatrix`, `viewMatrix`, `normalMatrix`, `modelMatrix` y `cameraPosition`: decláralos en el shader y nunca los pases en `uniforms`: una entrada con el mismo nombre se sobrescribe en cada draw (`modelMatrix`, `modelViewMatrix`, `normalMatrix`) o reemplaza el valor de la cámara (`projectionMatrix`, `viewMatrix`, `cameraPosition`).

```javascript
const material = new THREE.RawShaderMaterial({
  glslVersion: THREE.GLSL3, // sin él el shader es GLSL ES 1.00, que no tiene texture()
  vertexShader: `
    precision highp float;
    in vec3 position;
    uniform mat4 projectionMatrix;
    uniform mat4 modelViewMatrix;
    void main() {
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    precision highp float;
    out highp vec4 fragColor; // tu propia variable de salida
    void main() {
      fragColor = vec4(1.0, 0.0, 0.0, 1.0);
    }
  `,
});
```

## Propiedades comunes

```javascript
const material = new THREE.MeshBasicMaterial({ color: 0xff0000 });

material.visible = true;
material.transparent = false; // true para una opacidad menor que 1; cambiarlo tras el primer render requiere needsUpdate
material.opacity = 1.0;
material.alphaTest = 0; // descarta los fragmentos con alpha por debajo del valor
material.side = THREE.FrontSide; // FrontSide, BackSide, DoubleSide
material.depthTest = true;
material.depthWrite = true;
material.blending = THREE.NormalBlending; // o AdditiveBlending, CustomBlending
material.polygonOffset = false; // junto con los dos valores siguientes, corrige el z-fighting
material.polygonOffsetFactor = 0;
material.polygonOffsetUnits = 0;
material.toneMapped = true; // false conserva los colores exactos (overlays de UI)
material.dithering = false; // true reduce el banding en degradados
material.vertexColors = false;
```

```javascript
// El blending multiply y subtractive requieren alpha premultiplicado (en ambos renderers)
const material = new THREE.MeshBasicMaterial({ color: 0x8844ff });
material.blending = THREE.SubtractiveBlending; // igual para THREE.MultiplyBlending
material.premultipliedAlpha = true; // sin él el renderer registra un error y no establece ninguna función de blending

// El stencil está desactivado por defecto en ambos renderers: crea el renderer con { stencil: true }
const maskMaterial = new THREE.MeshBasicMaterial({ colorWrite: false, depthWrite: false });
maskMaterial.stencilWrite = true; // interruptor general de la prueba y escritura de stencil
maskMaterial.stencilRef = 1;
maskMaterial.stencilZPass = THREE.ReplaceStencilOp; // escribe 1 donde dibuja la máscara; también stencilFail, stencilZFail
const contentMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000, stencilWrite: true, stencilRef: 1 });
contentMaterial.stencilFunc = THREE.EqualStencilFunc; // dibuja solo donde la máscara escribió 1
contentMaterial.stencilFuncMask = 0xff; // máscara de comparación; stencilWriteMask enmascara la escritura (ambas valen 0xff por defecto)
// dibuja primero la máscara: da a su mesh un renderOrder menor que el del mesh de contenido
```

## Varios materiales por mesh

```javascript
// Un material por grupo de la geometría; BoxGeometry tiene seis, en el orden +x, -x, +y, -y, +z, -z
const geometry = new THREE.BoxGeometry(1, 1, 1);
const colors = [0xff0000, 0x00ff00, 0x0000ff, 0xffff00, 0xff00ff, 0x00ffff];
const mesh = new THREE.Mesh(geometry, colors.map((color) => new THREE.MeshBasicMaterial({ color })));

// Grupos personalizados: start, count, índice de material. La geometría indexada cuenta índices (BoxGeometry tiene 36),
// la geometría sin indexar cuenta vértices; los rangos fuera de todos los grupos no se dibujan
geometry.clearGroups();
geometry.addGroup(0, 18, 0);
geometry.addGroup(18, 18, 1);
```

## Mapas de entorno

Un archivo HDR equirectangular ilumina y refleja todos los materiales PBR de la escena. Ambos renderers lo prefiltran por sí mismos: no hace falta paso PMREM.

```javascript
import { HDRLoader } from "three/addons/loaders/HDRLoader.js";

const env = await new HDRLoader().loadAsync("environment.hdr");
env.mapping = THREE.EquirectangularReflectionMapping; // sin él un fondo se dibuja como un quad plano
scene.environment = env; // ilumina y refleja los materiales PBR
scene.background = env;
scene.environmentIntensity = 0.8; // atenuador de toda la escena; scene.environmentRotation lo inclina
```

```javascript
const cubeEnv = new THREE.CubeTextureLoader().load([
  "px.jpg", "nx.jpg", "py.jpg", "ny.jpg", "pz.jpg", "nz.jpg",
]);

const material = new THREE.MeshStandardMaterial({ envMap: cubeEnv });
material.envMapIntensity = 1.5; // escala solo el envMap propio de este material
material.envMapRotation = new THREE.Euler(0, Math.PI / 4, 0);
```

`scene.environment` ilumina MeshStandardMaterial y MeshPhysicalMaterial en ambos renderers. Con WebGLRenderer ilumina también MeshLambertMaterial y MeshPhongMaterial; WebGPURenderer no.

## Cambios en tiempo de ejecución, clonado y liberación

```javascript
mesh.material.color.set(0xff0000); // valores de uniform: no requieren recompilar
mesh.material.roughness = 0.8;

// material.needsUpdate = true tras cambiar un ajuste compilado dentro del shader:
// transparent, side, blending, flatShading, vertexColors, dithering, premultipliedAlpha, alphaHash,
// añadir o quitar un slot de mapa, o el código fuente del shader (alphaTest y envMap se recompilan solos)

const clone = mesh.material.clone(); // copia los valores; los slots de mapa comparten sus texturas, los uniforms de ShaderMaterial se clonan
```

Libera un material que nada más utilice: `material.dispose()` libera sus programas de GPU, que se eliminan una vez que ningún otro material los usa; las texturas necesitan su propio `texture.dispose()`.

Rendimiento, por orden de impacto:

1. Comparte una misma instancia de material entre meshes: el renderer vuelve a subir los uniforms del material cada vez que draws consecutivos cambian de material (los ajustes idénticos ya comparten un único programa compilado).
2. Prefiere el renderizado opaco: los materiales transparentes se ordenan de atrás hacia delante por objeto y se dibujan después de los opacos, y siguen escribiendo profundidad salvo con `depthWrite: false`, así que las capas apiladas generan overdraw y las que se intersecan se ordenan mal; para recortes, alphaTest mantiene el material opaco, de modo que se dibuja en la pasada opaca, correctamente en cualquier orden.
3. Elige el material más barato que se vea bien: Basic, luego Lambert, Phong, Standard, Physical.

## WebGPU y TSL

MeshStandardMaterial y las demás clases integradas funcionan sin cambios en WebGPURenderer: el renderer las convierte automáticamente a materiales de nodos; ShaderMaterial, RawShaderMaterial, MeshDepthMaterial y MeshDistanceMaterial no tienen equivalente de nodos y registran `Material "..." is not compatible`. Para shading personalizado usa las clases de material de nodos de `three/webgpu` con nodos TSL de `three/tsl`; están pensados para WebGPURenderer, y WebGLRenderer solo los dibuja mediante el addon `WebGLNodesHandler` (`three/addons/tsl/WebGLNodesHandler.js`, pasado a `renderer.setNodesHandler()`), una ayuda para la migración que no admite sombras VSM, MRT, transmisión ni la pila de postprocesado de WebGPU.

```javascript
import * as THREE from "three/webgpu";

const renderer = new THREE.WebGPURenderer({ antialias: true });
await renderer.init(); // antes de cualquier otro uso del renderer
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x111111); // el canvas de WebGPU es transparente por defecto
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(0, 0, 3);

function animate() {
  renderer.render(scene, camera);
}

renderer.setAnimationLoop(animate);
```

```javascript
import * as THREE from "three/webgpu";
import { texture, mix, color, float, time, positionLocal, normalLocal, sin } from "three/tsl";

// Sin iluminar: el equivalente en nodos de un ShaderMaterial de color
const unlit = new THREE.MeshBasicNodeMaterial();
unlit.colorNode = mix(color(0x0066ff), color(0xff0066), sin(time.mul(0.5)).mul(0.5).add(0.5));

// Iluminado: los slots de nodos sustituyen a las propiedades fijas; necesita luces o scene.environment
const map = await new THREE.TextureLoader().loadAsync("color.jpg");
map.colorSpace = THREE.SRGBColorSpace;
const lit = new THREE.MeshStandardNodeMaterial();
lit.colorNode = texture(map);
lit.roughnessNode = float(0.2);

// Desplazamiento de vértices sobre positionLocal, que ya incluye skinning, morphs e instancing
const shell = new THREE.MeshStandardNodeMaterial();
shell.positionNode = positionLocal.add(normalLocal.mul(sin(positionLocal.y.mul(6))).mul(0.05));
```

```javascript
import * as THREE from "three/webgpu";
import { instancedBufferAttribute } from "three/tsl";

// El backend WebGPU dibuja Points de 1 px sea cual sea el tamaño; dibuja los puntos más grandes como quads
const positions = new THREE.InstancedBufferAttribute(new Float32Array(1500), 3); // rellena con x, y, z por punto
const points = new THREE.Sprite(
  new THREE.PointsNodeMaterial({ positionNode: instancedBufferAttribute(positions), size: 4, sizeAttenuation: false }) // cuadrados de 4 px
);
points.count = 500; points.frustumCulled = false; // un quad por punto; el culling comprobaría solo una esfera de 0,7 unidades en el origen del sprite
scene.add(points);
```

## Errores comunes

- `geometry.setAttribute("uv2", geometry.attributes.uv)` → `const material = new THREE.MeshStandardMaterial({ aoMap });`: aoMap muestrea el atributo elegido por `aoMap.channel`, 0 (`uv`) por defecto, así que no necesita ningún atributo extra y uv2 solo se lee con `aoMap.channel = 2`; solo un desenvolvido aparte va en `uv1` con `aoMap.channel = 1`.
- `new RGBELoader()` → `new HDRLoader()`: HDRLoader se renombró desde RGBELoader en r180; RGBELoader está obsoleto y aún carga, con un aviso: importa HDRLoader de "three/addons/loaders/HDRLoader.js".
- `"three/examples/jsm/loaders/HDRLoader.js"` → `"three/addons/loaders/HDRLoader.js"`: los import maps del navegador mapean `three/addons/` a examples/jsm/ y no definen ninguna clave `three/examples/`, así que la ruta de examples falla allí.
- `material.blending = THREE.MultiplyBlending;` → `material.blending = THREE.MultiplyBlending; material.premultipliedAlpha = true;`: el blending multiply y subtractive requieren alpha premultiplicado, o el renderer registra un error y no establece ninguna función de blending.
- `material.stencilMask = 0xff;` → `material.stencilFuncMask = 0xff; material.stencilWriteMask = 0xff;`: `stencilMask` no existe; asignarlo solo crea un campo sin uso.
- `new THREE.WebGLRenderer({ antialias: true })` → `new THREE.WebGLRenderer({ antialias: true, stencil: true })`: el buffer de stencil está desactivado por defecto, así que los ajustes de stencil del material se ignoran silenciosamente sin él.
- `material.envMapIntensity = 0.5;` → `scene.environmentIntensity = 0.5;`: para atenuar scene.environment usa la propiedad de la escena; envMapIntensity atenúa solo el envMap propio del material.
- `material.uniforms.time.value = clock.getElapsedTime();` → `material.uniforms.time.value = timer.getElapsed();`: Clock está obsoleto desde r183; crea un THREE.Timer, llama una vez a timer.connect(document) y a timer.update() (sin argumento) lo primero en el bucle.
- `new THREE.ShaderMaterial({ glslVersion: THREE.GLSL3, fragmentShader })` → `new THREE.ShaderMaterial({ fragmentShader })`: ShaderMaterial ya se compila como GLSL ES 3.00, así que `texture()` funciona con glslVersion sin definir, mientras que GLSL3 elimina el alias `gl_FragColor` y un shader que lo escriba no compila.
- `uniforms: { modelViewMatrix: { value: new THREE.Matrix4() } }` → `uniform mat4 modelViewMatrix;`: declara las matrices integradas en el código fuente del shader de un RawShaderMaterial; una entrada de `uniforms` con el mismo nombre se sobrescribe en cada draw (modelMatrix, modelViewMatrix, normalMatrix) o reemplaza el valor de la cámara (projectionMatrix, viewMatrix, cameraPosition).
- `new THREE.LineBasicMaterial({ linewidth: 5 })` → `new Line2(new LineGeometry().setPositions([-1, 0, 0, 1, 0, 0]), new LineMaterial({ linewidth: 5 }))`: WebGLRenderer siempre dibuja primitivas de línea de 1 px; Line2 necesita una LineGeometry, no una BufferGeometry, y las tres vienen de three/addons/lines/ (en WebGPURenderer, Line2 viene de three/addons/lines/webgpu/Line2.js con Line2NodeMaterial).
- `new THREE.ShaderMaterial({ vertexShader, fragmentShader })` → `new THREE.MeshBasicNodeMaterial()`: en WebGPURenderer usa materiales de nodos y TSL; ShaderMaterial y RawShaderMaterial no tienen equivalente de nodos y registran "is not compatible".
- `import { texture } from "three/nodes";` → `import { texture } from "three/tsl";`: `three/nodes` no existe; los materiales de nodos vienen de `three/webgpu` y las funciones TSL de `three/tsl`.
- `import * as THREE from "three"; const m = new THREE.MeshStandardNodeMaterial();` → `import * as THREE from "three/webgpu"; const m = new THREE.MeshStandardNodeMaterial();`: los materiales de nodos solo los exporta three/webgpu y están pensados para WebGPURenderer.
- `new THREE.PointsMaterial({ size: 5 })` → `new THREE.Sprite(new THREE.PointsNodeMaterial({ positionNode: instancedBufferAttribute(positions) }))`: el backend WebGPU dibuja Points de 1 px sea cual sea el tamaño; fija sprite.count al número de puntos.
- `material.positionNode = positionGeometry.add(offset);` → `material.positionNode = positionLocal.add(offset);`: positionLocal incluye skinning, morph targets, batching e instancing; positionGeometry es el atributo en bruto de la pose de reposo.
- `map.encoding = THREE.sRGBEncoding;` → `map.colorSpace = THREE.SRGBColorSpace;`: `encoding` y `sRGBEncoding` ya no existen, así que la línea antigua no hace nada y el mapa de color se ve desvaído.
- `const m = new THREE.MeshStandardNodeMaterial(); m.colorNode = color(0xff0000);` → `const m = new THREE.MeshBasicNodeMaterial(); m.colorNode = color(0xff0000);`: MeshStandardNodeMaterial tiene iluminación y se ve negro sin luces ni entorno, así que un efecto sin iluminar usa MeshBasicNodeMaterial.
- `new THREE.ShaderMaterial({ extensions: { derivatives: true }, fragmentShader })` → `new THREE.ShaderMaterial({ fragmentShader })`: los indicadores de extensión de WebGL1 no hacen nada, porque GLSL ES 3.00 trae integrados `dFdx`, `gl_FragDepth` y `textureLod`.

## Ver también

- `references/textures.md`: carga, espacios de color, filtros y canales en profundidad
- `references/shaders.md`: escritura de GLSL, shader chunks y depuración en WebGLRenderer
- `references/lighting.md`: luces, sombras y cómo interactúan con los materiales
