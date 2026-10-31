# Geometría en Three.js

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
camera.position.set(0, 0, 5);

// Una geometría es la forma; muchos meshes pueden compartir una misma instancia de geometría
const mesh = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshNormalMaterial());
scene.add(mesh);

renderer.setAnimationLoop(animate);

function animate() {
  mesh.rotation.y += 0.01;
  renderer.render(scene, camera);
}
```

## Geometrías integradas

### Formas básicas

```javascript
new THREE.BoxGeometry(1, 1, 1); // width, height, depth, widthSegments, heightSegments, depthSegments
new THREE.SphereGeometry(1, 32, 16); // radius, widthSegments, heightSegments, phiStart, phiLength, thetaStart, thetaLength
new THREE.SphereGeometry(1, 32, 16, 0, Math.PI); // media esfera (barrido de phi, cortada por los polos)
new THREE.SphereGeometry(1, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2); // cúpula (cortada por el ecuador)
new THREE.PlaneGeometry(10, 10, 1, 1); // width, height, widthSegments, heightSegments
new THREE.CircleGeometry(1, 32); // radius, segments, thetaStart, thetaLength
new THREE.CylinderGeometry(1, 1, 2, 32); // radiusTop, radiusBottom, height, radialSegments, heightSegments, openEnded, thetaStart, thetaLength
new THREE.CylinderGeometry(1, 1, 2, 6); // prisma hexagonal
new THREE.ConeGeometry(1, 2, 32); // radius, height, radialSegments, heightSegments, openEnded, thetaStart, thetaLength
new THREE.TorusGeometry(1, 0.4, 16, 100); // radius, tube, radialSegments, tubularSegments, arc, thetaStart, thetaLength
new THREE.TorusGeometry(1, 0.4, 16, 100, Math.PI); // medio arco
new THREE.TorusKnotGeometry(1, 0.4, 100, 16, 2, 3); // radius, tube, tubularSegments, radialSegments, p, q
new THREE.RingGeometry(0.5, 1, 32, 1); // innerRadius, outerRadius, thetaSegments, phiSegments, thetaStart, thetaLength
```

### Formas avanzadas

```javascript
new THREE.CapsuleGeometry(0.5, 1, 4, 8, 1); // radius, height (solo la sección central), capSegments, radialSegments, heightSegments

// radius, detail: cada nivel de detalle subdivide cada cara
new THREE.IcosahedronGeometry(1, 0); // 20 caras con detail 0
new THREE.DodecahedronGeometry(1, 0);
new THREE.OctahedronGeometry(1, 0);
new THREE.TetrahedronGeometry(1, 0);

// Polyhedron: array plano de vértices, índices, radius, detail
const vertices = [1, 1, 1, -1, -1, 1, -1, 1, -1, 1, -1, -1];
const indices = [2, 1, 0, 0, 3, 2, 1, 3, 0, 2, 3, 1];
new THREE.PolyhedronGeometry(vertices, indices, 1, 0);
```

### Formas basadas en trayectorias

```javascript
// Lathe: un perfil de Vector2 girado alrededor del eje Y: points, segments, phiStart, phiLength
const profile = [
  new THREE.Vector2(0, 0), new THREE.Vector2(0.5, 0), new THREE.Vector2(0.5, 1), new THREE.Vector2(0, 1),
];
new THREE.LatheGeometry(profile, 32);

// Extrude: una Shape 2D empujada a lo largo de Z
const shape = new THREE.Shape();
shape.moveTo(0, 0);
shape.lineTo(1, 0);
shape.lineTo(1, 1);
shape.lineTo(0, 1);
new THREE.ExtrudeGeometry(shape, {
  steps: 1, depth: 1, bevelEnabled: true,
  bevelThickness: 0.1, bevelSize: 0.1, bevelSegments: 3,
});

// Tube: un barrido circular a lo largo de una curva: path, tubularSegments, radius, radialSegments, closed
const curve = new THREE.CatmullRomCurve3([
  new THREE.Vector3(-1, 0, 0), new THREE.Vector3(0, 1, 0), new THREE.Vector3(1, 0, 0),
]);
new THREE.TubeGeometry(curve, 64, 0.2, 8, false);
```

### Geometría de texto

```javascript
import { FontLoader } from "three/addons/loaders/FontLoader.js";
import { TextGeometry } from "three/addons/geometries/TextGeometry.js";

// Una fuente .typeface.json, de examples/fonts en el repositorio de three.js
const font = await new FontLoader().loadAsync("fonts/helvetiker_regular.typeface.json");
const geometry = new TextGeometry("Hello", {
  font: font,
  size: 1, // tamaño del texto en unidades del mundo
  depth: 0.2, // profundidad de la extrusión
  curveSegments: 12,
  bevelEnabled: true,
  bevelThickness: 0.03,
  bevelSize: 0.02,
  direction: "ltr", // 'ltr', 'rtl' (de derecha a izquierda) o 'tb' (de arriba abajo)
});

geometry.center(); // recentra los glifos en el origen
scene.add(new THREE.Mesh(geometry, new THREE.MeshNormalMaterial()));
```

## BufferGeometry

La clase base de toda geometría: arrays tipados con datos de vértices más un índice opcional. Los atributos son buffers con nombre de `itemSize` valores por vértice; `position`, `normal` y `uv` son los que los materiales leen por defecto.

### BufferGeometry personalizada

```javascript
const geometry = new THREE.BufferGeometry();

// Cuatro vértices, tres floats cada uno (x, y, z)
const vertices = new Float32Array([-1, -1, 0, 1, -1, 0, 1, 1, 0, -1, 1, 0]);
geometry.setAttribute("position", new THREE.BufferAttribute(vertices, 3));

// Los índices reutilizan vértices entre los dos triángulos
const indices = new Uint16Array([0, 1, 2, 0, 2, 3]);
geometry.setIndex(new THREE.BufferAttribute(indices, 1));

// Las normales determinan la iluminación, los UV direccionan las texturas
const normals = new Float32Array([0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1]);
geometry.setAttribute("normal", new THREE.BufferAttribute(normals, 3));
const uvs = new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]);
geometry.setAttribute("uv", new THREE.BufferAttribute(uvs, 2));
// Colores por vértice opcionales, que se renderizan con material.vertexColors = true
const colors = new Float32Array([1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0]);
geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));

scene.add(new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({ vertexColors: true })));
```

### Tipos de atributo

```javascript
const count = 4;
const geometry = new THREE.BufferGeometry();
// Float32 para posiciones, normales, UV y colores en coma flotante
geometry.setAttribute("position", new THREE.BufferAttribute(new Float32Array(count * 3), 3));
// Los índices Uint16 direccionan los vértices de 0 a 65534 (65535 es el valor de reinicio de primitiva); setIndex([...]) con un array normal elige Uint16 o Uint32 por sí mismo
geometry.setIndex(new THREE.BufferAttribute(new Uint16Array(count), 1));
// Los colores Uint8 necesitan normalized = true (tercer argumento) para que los bytes lleguen al shader como 0.0-1.0
geometry.setAttribute("color", new THREE.BufferAttribute(new Uint8Array(count * 3), 3, true));
```

### Actualizar una BufferGeometry

```javascript
const geometry = new THREE.PlaneGeometry(2, 2);
const positions = geometry.attributes.position;
positions.setXYZ(0, -2, -2, 0); // sobrescribe el vértice 0
positions.getX(0); // lee componentes sueltos con getX / getY / getZ
positions.needsUpdate = true; // sube el cambio; un array no puede crecer después de su primer render, así que reserva el máximo y usa geometry.setDrawRange(0, n)
geometry.computeVertexNormals(); // las normales deben coincidir con las nuevas posiciones
geometry.computeBoundingBox(); // los volúmenes envolventes controlan el frustum culling y el raycasting
geometry.computeBoundingSphere();
```

### Buffers intercalados (interleaved)

```javascript
// Un único buffer con position (3 floats) y uv (2 floats) por vértice
const interleavedBuffer = new THREE.InterleavedBuffer(
  new Float32Array([
    -1, -1, 0, 0, 0, 1, -1, 0, 1, 0, 1, 1, 0, 1, 1, -1, 1, 0, 0, 1, // cuatro vértices: xyz + uv
  ]),
  5, // stride: floats por vértice
);
const geometry = new THREE.BufferGeometry();
geometry.setAttribute("position", new THREE.InterleavedBufferAttribute(interleavedBuffer, 3, 0));
geometry.setAttribute("uv", new THREE.InterleavedBufferAttribute(interleavedBuffer, 2, 3));
geometry.setIndex([0, 1, 2, 0, 2, 3]); // dos triángulos sobre los cuatro vértices
// BufferGeometryUtils.interleaveAttributes([position, normal, uv]) empaqueta así atributos ya existentes
```

## Aristas y wireframes

```javascript
const boxGeometry = new THREE.BoxGeometry(1, 1, 1);
// Aristas donde las normales de las dos caras difieren al menos thresholdAngle (grados; 15 aquí), más las aristas de borde abierto
const edges = new THREE.EdgesGeometry(boxGeometry, 15);
const edgeLines = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0xffffff }));
// Todas las aristas de los triángulos, diagonales incluidas; una arista compartida por dos triángulos se dibuja una sola vez
const wireframe = new THREE.WireframeGeometry(boxGeometry);
const wireLines = new THREE.LineSegments(wireframe, new THREE.LineBasicMaterial({ color: 0xffffff }));
scene.add(edgeLines, wireLines);
```

## Puntos

```javascript
const count = 1000;
const positions = new Float32Array(count * 3).map(() => (Math.random() - 0.5) * 10);
const geometry = new THREE.BufferGeometry();
geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
// sizeAttenuation (true por defecto) reduce los puntos con la profundidad en una cámara en perspectiva: un punto ocupa size * (alto CSS del canvas / 2) / profundidad píxeles CSS
const material = new THREE.PointsMaterial({ size: 0.1, color: 0xffffff });
const points = new THREE.Points(geometry, material);
scene.add(points);
```

Con WebGPURenderer, el backend WebGPU dibuja los puntos de un píxel sea cual sea el tamaño del material; consulta la sección de WebGPU y TSL para el Sprite instanciado que restaura los tamaños.

## Líneas

```javascript
const linePoints = [
  new THREE.Vector3(-1, 0, 0), new THREE.Vector3(0, 1, 0), new THREE.Vector3(1, 0, 0),
];
const geometry = new THREE.BufferGeometry().setFromPoints(linePoints);
const material = new THREE.LineBasicMaterial({ color: 0xff0000 });

// Line conecta los puntos en orden; LineLoop cierra volviendo al primer punto
const line = new THREE.Line(geometry, material);
const loop = new THREE.LineLoop(geometry, material);
scene.add(line, loop);

// LineSegments dibuja pares independientes: vértices 0-1, 2-3, ...
const segmentsGeometry = new THREE.BufferGeometry().setFromPoints([linePoints[0], linePoints[1], linePoints[1], linePoints[2]]);
const segments = new THREE.LineSegments(segmentsGeometry, material);
scene.add(segments);
```

LineLoop no está soportado en WebGPURenderer: registra un error y no renderiza nada. Allí, cierra el bucle repitiendo el primer punto y usando Line.

## InstancedMesh

Una sola draw call para muchas copias de una misma geometría, cada una con su propia transformación.

```javascript
const geometry = new THREE.BoxGeometry(0.2, 0.2, 0.2);
const material = new THREE.MeshBasicMaterial(); // multiplica por los colores de instancia; MeshNormalMaterial los ignora
const count = 1000;
const instancedMesh = new THREE.InstancedMesh(geometry, material, count);
const dummy = new THREE.Object3D();
for (let i = 0; i < count; i++) {
  dummy.position.set((Math.random() - 0.5) * 20, (Math.random() - 0.5) * 20, (Math.random() - 0.5) * 20);
  dummy.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, 0);
  dummy.scale.setScalar(0.5 + Math.random());
  dummy.updateMatrix();
  instancedMesh.setMatrixAt(i, dummy.matrix);
}
instancedMesh.instanceMatrix.needsUpdate = true; // necesario tras cambios una vez que el mesh ya se ha renderizado; inocuo antes

// setColorAt crea instanceColor en el primer uso; márcalo tras el bucle
for (let i = 0; i < count; i++) {
  instancedMesh.setColorAt(i, new THREE.Color(Math.random(), Math.random(), Math.random()));
}
instancedMesh.instanceColor.needsUpdate = true;

scene.add(instancedMesh);
```

En tiempo de ejecución, actualiza y lanza rayos contra las instancias así:

```javascript
// mesh aquí es un InstancedMesh
const matrix = new THREE.Matrix4();
const index = 7;
mesh.getMatrixAt(index, matrix);
matrix.setPosition(0, 2, 0); // mueve solo esta instancia
mesh.setMatrixAt(index, matrix);
mesh.instanceMatrix.needsUpdate = true; // márcalo tras cualquier lote de llamadas a setMatrixAt
mesh.computeBoundingSphere(); // las instancias se han movido: refresca los límites usados por el frustum culling y el raycasting

// El raycasting indica qué instancia se ha golpeado
const raycaster = new THREE.Raycaster();
const hits = raycaster.intersectObject(mesh);
if (hits.length > 0) {
  const instanceId = hits[0].instanceId; // undefined para un objeto no instanciado
}
```

## InstancedBufferGeometry

Atributos por instancia más allá de la transformación y el color.

```javascript
const count = 1000;
const geometry = new THREE.InstancedBufferGeometry();
geometry.copy(new THREE.BoxGeometry(1, 1, 1)); // copia el índice y todos los atributos
geometry.instanceCount = count; // obligatorio: copy() no trae contador de instancias

const offsets = new Float32Array(count * 3).map(() => Math.random() * 10);
geometry.setAttribute("offset", new THREE.InstancedBufferAttribute(offsets, 3));

// Con WebGLRenderer y un ShaderMaterial, declara tú mismo `in vec3 offset;` en el vertex
// shader y súmalo a position (consulta references/shaders.md). En WebGPURenderer,
// los datos por instancia son un nodo TSL: consulta la sección de WebGPU y TSL.
```

## BatchedMesh

Muchas geometrías distintas que comparten un material, cada instancia con su propia transformación. WebGLRenderer las dibuja con una sola llamada multi-draw cuando WEBGL_multi_draw está disponible; el backend WebGPU emite un draw por instancia.

```javascript
const material = new THREE.MeshNormalMaterial();
const maxInstanceCount = 1000;
const maxVertexCount = 20000;
const maxIndexCount = 20000;
const batchedMesh = new THREE.BatchedMesh(maxInstanceCount, maxVertexCount, maxIndexCount, material);
const boxGeometryId = batchedMesh.addGeometry(new THREE.BoxGeometry(1, 1, 1));
const sphereGeometryId = batchedMesh.addGeometry(new THREE.SphereGeometry(0.5, 16, 16));

// Una geometría solo se renderiza a través de sus instancias; las geometrías añadidas deben tener atributos y estado de índice coincidentes
const boxInstanceId = batchedMesh.addInstance(boxGeometryId);
batchedMesh.setMatrixAt(boxInstanceId, new THREE.Matrix4().setPosition(-2, 0, 0));
const sphereInstanceId = batchedMesh.addInstance(sphereGeometryId);
batchedMesh.setMatrixAt(sphereInstanceId, new THREE.Matrix4().setPosition(2, 0, 0));

scene.add(batchedMesh);
```

## Utilidades de geometría

```javascript
import * as BufferGeometryUtils from "three/addons/utils/BufferGeometryUtils.js";
import * as MikkTSpace from "three/addons/libs/mikktspace.module.js";

const geo1 = new THREE.BoxGeometry(1, 1, 1);
const geo2 = new THREE.SphereGeometry(0.5, 16, 16);
// Fusiona geometrías estáticas; las entradas necesitan los mismos atributos y deben estar todas indexadas o todas sin indexar (si no, devuelve null).
// useGroups = true añade un grupo por entrada, para un array de materiales como [boxMaterial, sphereMaterial].
const merged = BufferGeometryUtils.mergeGeometries([geo1, geo2], true);

// Suelda los vértices duplicados; también genera un índice para una geometría sin indexar
const welded = BufferGeometryUtils.mergeVertices(geo2);

// Tangentes para normal mapping: el método del núcleo necesita un índice más position, normal y uv
welded.computeTangents();

// Las tangentes MikkTSpace (la convención que usan los normal maps de glTF) vienen del addon; esto deja merged sin indexar, in situ
await MikkTSpace.ready;
BufferGeometryUtils.computeMikkTSpaceTangents(merged, MikkTSpace);
```

## Transformar geometría

```javascript
const geometry = new THREE.TorusKnotGeometry(0.5, 0.15, 100, 16);

geometry.center(); // mueve los vértices para que el centro de la caja envolvente quede en el origen
geometry.computeBoundingBox(); // refresca tras cambios en los vértices
const size = new THREE.Vector3();
geometry.boundingBox.getSize(size);
const maxDim = Math.max(size.x, size.y, size.z);
geometry.scale(1 / maxDim, 1 / maxDim, 1 / maxDim); // ajusta para que quepa en un cubo unitario

const clone = geometry.clone(); // clona primero: estos métodos mutan la geometría
clone.rotateX(Math.PI / 2);
clone.translate(0, 1, 0);
```

Para rotar o escalar un objeto alrededor de un punto sin tocar los datos de vértices, define un pivote en lugar de recentrar la geometría:

```javascript
// La rotación y la escala usan normalmente el origen del objeto; pivot es un punto en las coordenadas propias del objeto
mesh.pivot = new THREE.Vector3(1, 0, 0); // por defecto null
mesh.rotation.y += 0.05; // ahora gira alrededor del punto local (1, 0, 0)
```

## Morph targets

```javascript
const geometry = new THREE.BoxGeometry(1, 1, 1, 4, 4, 4);
const morphPositions = geometry.attributes.position.array.slice();
for (let i = 0; i < morphPositions.length; i += 3) {
  morphPositions[i] *= 2; // estira X
  morphPositions[i + 1] *= 0.5; // aplasta Y
}
geometry.morphAttributes.position = [new THREE.BufferAttribute(morphPositions, 3)];

// Crea el mesh después de asignar morphAttributes para que recoja los targets
const mesh = new THREE.Mesh(geometry, new THREE.MeshNormalMaterial());
mesh.morphTargetInfluences[0] = 0.5; // mezcla del 50 % entre la base y el target
scene.add(mesh);
```

## Rendimiento y liberación de recursos

- Reduce las draw calls: mergeGeometries para meshes estáticos, InstancedMesh para geometría repetida, BatchedMesh para muchas geometrías distintas (una sola llamada multi-draw en WebGLRenderer cuando WEBGL_multi_draw está disponible).
- El número de segmentos intercambia suavidad por cantidad de vértices; el valor por defecto de la esfera, 32 por 16, sirve para la mayoría de usos; sube más solo para primeros planos.

```javascript
scene.remove(mesh);
mesh.dispose(); // libera el estado del renderer que se guarda solo para este objeto, no los hijos ni los recursos compartidos
mesh.geometry.dispose(); // libera los buffers de GPU de inmediato, incluso mientras otro mesh los comparta (ese mesh los vuelve a subir)
mesh.material.dispose(); // sus texturas necesitan su propio texture.dispose()
```

Para liberar un subárbol entero, recórrelo como se muestra en Errores comunes. InstancedMesh.dispose() libera además su textura de morph.

## WebGPU y TSL

Las clases de geometría, InstancedMesh y BatchedMesh mantienen en WebGPURenderer la API mostrada arriba. Lo que cambia: el backend WebGPU dibuja Points de un píxel y emite un draw por instancia de BatchedMesh, LineLoop se omite con un error, y los datos de shader por instancia son un nodo TSL.

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
camera.position.set(0, 0, 5);
renderer.setAnimationLoop(animate);

function animate() {
  renderer.render(scene, camera);
}
```

El backend WebGPU dibuja los puntos de un píxel sea cual sea el tamaño del material. Los puntos más grandes se renderizan como un único Sprite dibujado una vez por posición:

```javascript
import * as THREE from "three/webgpu";
import { instancedBufferAttribute } from "three/tsl";

const count = 1000;
const positions = new Float32Array(count * 3).map(() => (Math.random() - 0.5) * 10);
const material = new THREE.PointsNodeMaterial({
  positionNode: instancedBufferAttribute(new THREE.InstancedBufferAttribute(positions, 3)),
  size: 0.5, // escalado por profundidad como PointsMaterial; píxeles CSS con sizeAttenuation: false; sizeNode para un nodo
});
const points = new THREE.Sprite(material);
points.count = count; // cuántas instancias dibuja el sprite
points.frustumCulled = false; // el culling comprueba una esfera de 0,7 unidades en el origen del sprite, no las posiciones
scene.add(points);
```

Los atributos personalizados por instancia son nodos TSL, no declaraciones GLSL. Construye el desplazamiento sobre positionLocal, que ya incluye las transformaciones de instancia:

```javascript
import * as THREE from "three/webgpu";
import { instancedBufferAttribute, positionLocal } from "three/tsl";

const count = 1000;
const jitter = new THREE.InstancedBufferAttribute(new Float32Array(count * 3).map(() => Math.random() - 0.5), 3);
const material = new THREE.MeshBasicNodeMaterial();
material.positionNode = positionLocal.add(instancedBufferAttribute(jitter).mul(0.5)); // datos por instancia, sin GLSL
const mesh = new THREE.InstancedMesh(new THREE.BoxGeometry(0.2, 0.2, 0.2), material, count);
const matrix = new THREE.Matrix4();
for (let i = 0; i < count; i++) {
  mesh.setMatrixAt(i, matrix.setPosition(Math.random() * 8 - 4, Math.random() * 8 - 4, Math.random() * 8 - 4));
}
scene.add(mesh);
```

## Errores comunes

- `BufferGeometryUtils.computeTangents(geometry)` → `geometry.computeTangents()`: BufferGeometryUtils no exporta computeTangents; el método del núcleo necesita un índice más los atributos position, normal y uv.
- `new THREE.BufferAttribute(new Uint8Array(rgbBytes), 3)` → `new THREE.BufferAttribute(new Uint8Array(rgbBytes), 3, true)`: los bytes sin normalizar llegan al shader como 0.0 a 255.0 y los colores se queman.
- `geometry.copy(new THREE.BoxGeometry(1, 1, 1));` → `geometry.copy(new THREE.BoxGeometry(1, 1, 1)); geometry.instanceCount = count;`: InstancedBufferGeometry.copy() sobrescribe instanceCount con el valor undefined del origen, y WebGLRenderer entonces no dibuja ninguna instancia.
- `batchedMesh.addGeometry(boxGeometry)` → `batchedMesh.addInstance(batchedMesh.addGeometry(boxGeometry))`: una geometría añadida a un BatchedMesh solo se renderiza a través de una instancia creada con addInstance (obligatorio desde r166).
- `new THREE.LineLoop(geometry, material)` → `new THREE.Line(new THREE.BufferGeometry().setFromPoints([...linePoints, linePoints[0]]), material)`: WebGPURenderer no soporta LineLoop; registra un error y omite el objeto, así que repite el primer punto para cerrar una Line.
- `import { TextGeometry } from "three/examples/jsm/geometries/TextGeometry.js"` → `import { TextGeometry } from "three/addons/geometries/TextGeometry.js"`: el specifier examples/jsm no se resuelve con los import maps documentados, que mapean three/addons/ pero no three/examples/.
- `capsule.parameters.length` → `capsule.parameters.height`: el parámetro de CapsuleGeometry se renombró de `length` a `height` en r176, y se añadió un quinto parámetro `heightSegments`.
- `{ font: font, size: 1, height: 0.2 }` → `{ font: font, size: 1, depth: 0.2 }`: la opción de extrusión de TextGeometry se renombró de `height` a `depth` en r163; un height antiguo se ignora y el texto se extruye los 50 unidades por defecto.
- `new THREE.Points(cloud, new THREE.PointsMaterial({ size: 10 }))` → `new THREE.Sprite(new THREE.PointsNodeMaterial({ positionNode: instancedBufferAttribute(attr) }))`: el backend WebGPU dibuja Points de un píxel sea cual sea el tamaño, así que los puntos más grandes necesitan la forma de Sprite instanciado.
- `new THREE.ShaderMaterial({ vertexShader: offsetVertexShader })` → `material.positionNode = positionLocal.add(instancedBufferAttribute(offsetAttribute))`: WebGPURenderer no tiene una versión de nodos de ShaderMaterial; registra que el material no es compatible y recurre a un NodeMaterial simple, así que allí los datos por instancia son un nodo TSL.
- `material.positionNode = positionGeometry.add(offset)` → `material.positionNode = positionLocal.add(offset)`: positionLocal ya incluye skinning, morph targets, batching e instancing; positionGeometry es el atributo en bruto.
- `mesh.morphTargetInfluences[0] = 0.5` → `mesh.updateMorphTargets(); mesh.morphTargetInfluences[0] = 0.5;`: las influencias solo existen para los morph attributes que el mesh vio en su construcción, así que refréscalas tras añadir targets a un mesh ya existente.
- `gltf.scene.dispose()` → `gltf.scene.traverse((child) => { child.geometry?.dispose(); for (const material of [child.material ?? []].flat()) { for (const value of Object.values(material)) if (value?.isTexture) value.dispose(); material.dispose(); } child.dispose(); })`: Object3D.dispose() libera el estado del renderer de ese único objeto; no visita a los hijos ni libera geometrías, materiales o texturas.
- `new THREE.BoxBufferGeometry(1, 1, 1)` → `new THREE.BoxGeometry(1, 1, 1)`: los alias `*BufferGeometry` de las formas integradas ya no existen; toda geometría integrada ya es una BufferGeometry.
- `BufferGeometryUtils.mergeBufferGeometries([geo1, geo2])` → `BufferGeometryUtils.mergeGeometries([geo1, geo2])`: el nombre antiguo no se exporta, así que la llamada lanza un TypeError.
- `geometry.setAttribute("uv2", geometry.attributes.uv)` → `material.aoMap = aoTexture;`: un aoMap lee `uv` (canal 0) por defecto; solo un desenvolvido horneado aparte va en `uv1`, con `aoTexture.channel = 1`.
- `new THREE.LineBasicMaterial({ linewidth: 4 })` → `new Line2(new LineGeometry().setPositions(xyzArray), new LineMaterial({ linewidth: 4 }))`: WebGL y WebGPU dibujan las primitivas de línea de un píxel de ancho diga lo que diga linewidth; Line2, LineGeometry y LineMaterial de three/addons/lines/ dibujan líneas gruesas en WebGLRenderer, y en WebGPURenderer el Line2 de three/addons/lines/webgpu/Line2.js usa un Line2NodeMaterial de three/webgpu.

## Ver también

- `references/fundamentals.md`: configuración de la escena, el bucle de render, transformaciones de Object3D y liberación de recursos.
- `references/materials.md`: tipos de material y ajustes para los meshes construidos aquí.
- `references/shaders.md`: código de vertex y fragment de ShaderMaterial para WebGLRenderer.
- `references/animation.md`: animar influencias de morph targets y transformaciones a lo largo del tiempo.
- `references/loaders.md`: glTF y otros formatos que traen su propia geometría.
- `references/performance.md`: elegir entre fusión, instancing, batching y LOD según las draw calls medidas.
