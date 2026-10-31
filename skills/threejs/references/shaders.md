# Shaders en Three.js

Dirigido a three.js r186. Los ejemplos usan WebGLRenderer; la sección de WebGPU y TSL usa WebGPURenderer.

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

const material = new THREE.ShaderMaterial({
  uniforms: {
    time: { value: 0 },
    color: { value: new THREE.Color(0x0066ff) }, // el hexadecimal se convierte al espacio de trabajo lineal
  },
  vertexShader: /* glsl */ `
    varying vec2 vUv;

    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: /* glsl */ `
    uniform float time;
    uniform vec3 color;
    varying vec2 vUv;

    void main() {
      float wave = sin(vUv.x * 10.0 + time * 2.0) * 0.5 + 0.5;
      gl_FragColor = vec4(color * wave, 1.0);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }
  `,
});

const mesh = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), material);
scene.add(mesh);

const timer = new THREE.Timer();
timer.connect(document);

renderer.setAnimationLoop(animate);

function animate() {
  timer.update();
  material.uniforms.time.value = timer.getElapsed();
  renderer.render(scene, camera);
}
```

## ShaderMaterial frente a RawShaderMaterial

Todo `ShaderMaterial` se compila como GLSL ES 3.00: three.js siempre antepone `#version 300 es` (el soporte de WebGL 1 ha desaparecido). `texture()`, `textureLod()`, `textureSize()` y `dFdx`/`fwidth` funcionan sin ningún flag; `texture2D`, `textureCube`, `attribute`, `varying` y `gl_FragColor` son alias `#define`, de modo que la mayoría de los shaders GLSL ES 1.00 compilan sin cambios (no los que llaman `texture` a una variable, escriben en `gl_FragData` o conservan una línea `#extension`, que falla porque three.js pone las declaraciones antes de tu código; bórrala, esas funciones ya son del núcleo). Deja `glslVersion` sin definir: establecer `THREE.GLSL3` solo elimina el alias `gl_FragColor`, y te obliga a declarar tu propia variable de salida. ShaderMaterial inyecta las declaraciones habituales:

```javascript
const material = new THREE.ShaderMaterial({
  vertexShader: /* glsl */ `
    // Declarados por ti: uniforms modelMatrix, modelViewMatrix, projectionMatrix,
    // viewMatrix, normalMatrix, cameraPosition; attributes position, normal, uv,
    // instanceMatrix (InstancedMesh) y color (vertexColors: true)

    varying vec3 vNormal;

    void main() {
      vNormal = normalize(normalMatrix * normal); // normal en espacio de vista
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: /* glsl */ `
    varying vec3 vNormal;

    void main() {
      gl_FragColor = vec4(vNormal * 0.5 + 0.5, 1.0);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }
  `,
});
```

RawShaderMaterial recibe solo `#define SHADER_TYPE`, `#define SHADER_NAME` y tus `defines` (más `#version 300 es` una vez definido `glslVersion`): ni declaraciones ni sentencia de precisión. Define siempre `glslVersion: THREE.GLSL3` (sin él el shader es GLSL ES 1.00, que no tiene `texture()`), escribe `precision highp float;`, usa `in`/`out` y declara tu propia salida. Declara en el shader las matrices que necesites y nunca las pases por `uniforms`: el renderer fija `modelMatrix`, `modelViewMatrix`, `projectionMatrix`, `viewMatrix`, `normalMatrix` y `cameraPosition` para cualquier programa que las declare, y una entrada con el mismo nombre en `uniforms` se sobrescribe en cada draw (`modelMatrix`, `modelViewMatrix`, `normalMatrix`) o sustituye el valor de la cámara (`projectionMatrix`, `viewMatrix`, `cameraPosition`).

```javascript
const material = new THREE.RawShaderMaterial({
  glslVersion: THREE.GLSL3,
  vertexShader: /* glsl */ `
    precision highp float;

    in vec3 position;

    uniform mat4 modelViewMatrix;
    uniform mat4 projectionMatrix;

    void main() {
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: /* glsl */ `
    precision highp float;

    out highp vec4 fragColor;

    void main() {
      fragColor = vec4(1.0, 0.0, 0.0, 1.0);
    }
  `,
});
```

## Uniforms

```javascript
const texture = await new THREE.TextureLoader().loadAsync("textures/diffuse.jpg");
texture.colorSpace = THREE.SRGBColorSpace; // una imagen en color: se decodifica a lineal al muestrearla

const material = new THREE.ShaderMaterial({
  uniforms: {
    floatValue: { value: 1.5 },
    vec3Value: { value: new THREE.Vector3(1, 2, 3) },
    colorValue: { value: new THREE.Color(0xff0000) }, // el hexadecimal se convierte al espacio de trabajo lineal
    mat4Value: { value: new THREE.Matrix4() },
    mapValue: { value: texture },
  },
  // vertexShader y fragmentShader como de costumbre
});
```

Las declaraciones GLSL correspondientes; muestrea la textura con `texture(mapValue, vUv)`:

```glsl
uniform float floatValue;
uniform vec3 vec3Value;
uniform vec3 colorValue;    // un THREE.Color llega como vec3
uniform mat4 mat4Value;
uniform sampler2D mapValue;
```

Actualiza un uniform asignando `.value` desde el bucle de fotogramas (`material.uniforms.floatValue.value = 2.0;`); los vectores y colores se modifican en el sitio (`material.uniforms.vec3Value.value.set(1, 2, 3);`). Nunca llames a un uniform `position`, `normal`, `uv`, `modelViewMatrix` o `cameraPosition`: three.js ya los declara en el vertex shader, y la redeclaración es un error de compilación.

## Color de salida y tone mapping

`THREE.Color` convierte la entrada hexadecimal de sRGB al espacio de color de trabajo lineal, de modo que un uniform de color contiene valores lineales. Un ShaderMaterial escribe su salida tal cual: el tone mapping y la conversión al espacio de color de salida solo se producen si el fragment shader termina con los dos includes:

```glsl
gl_FragColor = vec4(color, 1.0);
#include <tonemapping_fragment>
#include <colorspace_fragment>
```

`tonemapping_fragment` aplica `renderer.toneMapping` (no hace nada con `NoToneMapping`); `colorspace_fragment` codifica a `renderer.outputColorSpace` (`SRGBColorSpace` por defecto). Sin ellos, los tonos medios se ven más oscuros que el mismo hexadecimal en un material integrado. Ambos chunks escriben en `gl_FragColor`, por lo que exigen `glslVersion` sin definir. Una textura RGBA de 8 bits con `texture.colorSpace = THREE.SRGBColorSpace` se decodifica a lineal al muestrearse, así que los colores muestreados se combinan correctamente con los includes presentes. Una `VideoTexture` no: three.js la sube sin decodificación sRGB y solo la decodifica dentro de los materiales integrados, así que decodifícala tú con `sRGBTransferEOTF(texture(videoMap, vUv))` (el prefijo de ShaderMaterial declara esa función). Al renderizar a un render target, como dentro de un EffectComposer, ambos includes dejan el color en lineal y `OutputPass` lo codifica al final.

## Patrones de shader habituales

### Desplazamiento de vértices

```javascript
const material = new THREE.ShaderMaterial({
  uniforms: {
    time: { value: 0 },
    amplitude: { value: 0.2 },
  },
  vertexShader: /* glsl */ `
    uniform float time;
    uniform float amplitude;

    void main() {
      vec3 pos = position;
      pos.z += sin(pos.x * 5.0 + time) * amplitude;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
    }
  `,
  fragmentShader: /* glsl */ `
    void main() {
      gl_FragColor = vec4(0.5, 0.8, 1.0, 1.0);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }
  `,
});

const mesh = new THREE.Mesh(new THREE.PlaneGeometry(2, 2, 64, 64), material); // el desplazamiento necesita subdivisiones
```

### Fresnel

Usa un único espacio de forma coherente. Espacio del mundo con `cameraPosition`:

```javascript
const material = new THREE.ShaderMaterial({
  vertexShader: /* glsl */ `
    varying vec3 vWorldNormal;
    varying vec3 vWorldPosition;

    void main() {
      vWorldNormal = normalize(mat3(modelMatrix) * normal); // espacio del mundo, se asume escala uniforme
      vWorldPosition = (modelMatrix * vec4(position, 1.0)).xyz;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: /* glsl */ `
    varying vec3 vWorldNormal;
    varying vec3 vWorldPosition;

    void main() {
      vec3 viewDirection = normalize(cameraPosition - vWorldPosition);
      float fresnel = pow(1.0 - max(dot(viewDirection, vWorldNormal), 0.0), 3.0);

      gl_FragColor = vec4(mix(vec3(0.0, 0.0, 0.5), vec3(0.5, 0.8, 1.0), fresnel), 1.0);
      #include <tonemapping_fragment>
      #include <colorspace_fragment>
    }
  `,
});
```

`normalMatrix * normal` está en espacio de vista: combínalo con la dirección hacia la cámara en espacio de vista, nunca con `cameraPosition`. Para la iluminación de borde (rim lighting) mantén ambos en espacio de vista: en el vertex shader `vec4 mvPosition = modelViewMatrix * vec4(position, 1.0); vViewDir = -mvPosition.xyz; vNormal = normalMatrix * normal;`, y en el fragment shader `float rim = pow(1.0 - max(dot(normalize(vViewDir), normalize(vNormal)), 0.0), 4.0);`.

### Disolución (dissolve)

```glsl
uniform float progress;
uniform sampler2D noiseMap;
varying vec2 vUv;

void main() {
  float noise = texture(noiseMap, vUv).r;
  if (noise < progress) discard;

  float edge = smoothstep(progress, progress + 0.1, noise);
  gl_FragColor = vec4(mix(vec3(1.0, 0.5, 0.0), vec3(0.5), edge), 1.0);
  #include <tonemapping_fragment>
  #include <colorspace_fragment>
}
```

## Instanced meshes y atributos personalizados

Three.js declara `position`, `normal`, `uv`, `instanceMatrix` (para un InstancedMesh), `instanceColor` (una vez llamado `setColorAt`) y `color` (con `vertexColors: true`). Todo lo demás (un atributo por vértice personalizado, `uv1` a `uv3`, `tangent`) lo declaras tú con `attribute` (el alias de `in`).

```javascript
const instanceCount = 100;
const geometry = new THREE.PlaneGeometry(0.2, 0.2);
const offsets = new Float32Array(instanceCount * 3);
// rellena offsets con un vec3 por instancia
geometry.setAttribute("aOffset", new THREE.InstancedBufferAttribute(offsets, 3));

const material = new THREE.ShaderMaterial({
  vertexShader: /* glsl */ `
    attribute vec3 aOffset;

    void main() {
      // instanceMatrix la declara three.js; el shader debe aplicarla
      gl_Position = projectionMatrix * modelViewMatrix * instanceMatrix * vec4(position + aOffset, 1.0);
    }
  `,
  fragmentShader: /* glsl */ `
    void main() {
      gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
    }
  `,
});

const mesh = new THREE.InstancedMesh(geometry, material, instanceCount);
mesh.frustumCulled = false; // los límites salen de instanceMatrix e ignoran aOffset
```

Para un atributo por vértice usa `geometry.setAttribute("aOffset", new THREE.BufferAttribute(new Float32Array(geometry.attributes.position.count * 3), 3));`: la declaración en el shader es la misma.

## Ampliar materiales integrados

`onBeforeCompile` reescribe las cadenas de shader de un material integrado. Se ejecuta una vez por programa, antes de que se resuelvan los includes.

```javascript
const material = new THREE.MeshStandardMaterial({ color: 0x00ff00 });

material.onBeforeCompile = (shader) => {
  shader.uniforms.time = { value: 0 };
  material.userData.shader = shader; // conserva la referencia para las actualizaciones

  shader.vertexShader = "uniform float time;\n" + shader.vertexShader;
  shader.vertexShader = shader.vertexShader.replace(
    "#include <begin_vertex>",
    `
    #include <begin_vertex>
    transformed.y += sin(position.x * 10.0 + time) * 0.1;
    `,
  );
};

// en el bucle de fotogramas, con timer.update() primero como en el inicio rápido:
// if (material.userData.shader) material.userData.shader.uniforms.time.value = timer.getElapsed();
```

Puntos de inyección en los shaders integrados: en el vertex shader `#include <begin_vertex>` (declara `vec3 transformed = vec3(position)`), `#include <beginnormal_vertex>` (`vec3 objectNormal`) y `#include <project_vertex>` (fija `gl_Position`); en el fragment shader `#include <color_fragment>` (`diffuseColor` tras el mapa y los colores de vértice), `#include <opaque_fragment>` (escribe `gl_FragColor` antes del tone mapping) y `#include <fog_fragment>` (después del tone mapping, el espacio de color y la niebla).

Si `onBeforeCompile` produce shaders distintos para materiales distintos (por ejemplo según valores de `material.userData`), define también `material.customProgramCacheKey()` devolviendo una cadena distinta por variante, o el renderer reutilizará un único programa en caché para todas.

## Shader chunks

`#include <chunk>` funciona en el código de ShaderMaterial y RawShaderMaterial y reutiliza funciones auxiliares de three.js; `perspectiveDepthToViewZ` de abajo procede del chunk `packing`.

```javascript
const fragmentShader = /* glsl */ `
  #include <packing>

  uniform sampler2D depthTexture;
  uniform float cameraNear; // se fija a partir de camera.near
  uniform float cameraFar; // se fija a partir de camera.far
  varying vec2 vUv;

  void main() {
    float viewZ = perspectiveDepthToViewZ(texture(depthTexture, vUv).r, cameraNear, cameraFar);
    gl_FragColor = vec4(vec3(-viewZ / cameraFar), 1.0);
  }
`;
```

Usa solo claves de chunk que existan en esta versión (muestra `Object.keys(THREE.ShaderChunk)` por consola para comprobarlo): no existe un chunk `output_fragment`; el chunk de salida final es `opaque_fragment`.

## Depuración

```javascript
// Mientras renderer.debug.checkShaderErrors es true (el valor por defecto), un programa fallido registra los errores de cada shader
// con las líneas de código numeradas alrededor del primero. Un manejador sustituye ese informe y se ejecuta solo ante un fallo de compilación o enlazado:
renderer.debug.onShaderError = (gl, program, vertexShader, fragmentShader) => {
  console.error(gl.getProgramInfoLog(program));
  for (const shader of [vertexShader, fragmentShader]) {
    const log = gl.getShaderInfoLog(shader);
    if (log) console.error(log, gl.getShaderSource(shader)); // el shader completo ya ensamblado
  }
};
```

Depura visualmente escribiendo en la salida el valor que quieras comprobar: `gl_FragColor = vec4(vUv, 0.0, 1.0);` para las UV, `gl_FragColor = vec4(vNormal * 0.5 + 0.5, 1.0);` para las normales.

## WebGPU y TSL

`ShaderMaterial`, `RawShaderMaterial` y `onBeforeCompile` solo funcionan con WebGLRenderer. Con WebGPURenderer, un ShaderMaterial registra `Material "ShaderMaterial" is not compatible` y recurre a un node material básico, y `onBeforeCompile` nunca se llama: construye el efecto como un node material con TSL. WebGPURenderer recurre por sí solo a WebGL 2 cuando WebGPU no está disponible, así que un único camino de código TSL cubre ambos backends.

### Node materials

Un efecto sin iluminación usa `MeshBasicNodeMaterial`; `MeshStandardNodeMaterial` está iluminado y se renderiza en negro sin luces ni entorno. Un ShaderMaterial se corresponde con `MeshBasicNodeMaterial` (sin iluminación) o con las ranuras de nodo de `MeshStandardNodeMaterial` (iluminado); para sustituir toda la salida del fragmento se usa `fragmentNode`. Las ranuras habituales existen como propiedades de nodo: `colorNode`, `opacityNode`, `emissiveNode`, `normalNode`, `positionNode`.

```javascript
import * as THREE from "three/webgpu";
import { color, mix, sin, time, uv } from "three/tsl";

const renderer = new THREE.WebGPURenderer({ antialias: true });
await renderer.init(); // antes de cualquier otro uso del renderer
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x111827); // el canvas de WebGPU es transparente por defecto
const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 100);
camera.position.set(0, 0, 2);

const material = new THREE.MeshBasicNodeMaterial();
material.colorNode = mix(color(0x004466), color(0x66ddff), sin(uv().x.mul(20).add(time)).mul(0.5).add(0.5));

scene.add(new THREE.Mesh(new THREE.PlaneGeometry(2, 2), material));

renderer.setAnimationLoop(animate);

function animate() {
  renderer.render(scene, camera);
}
```

### Uniforms y tiempo

`uniform(value)` crea un uniform actualizable; `time` es un nodo integrado que se actualiza solo en cada fotograma y sustituye a un uniform de tiempo alimentado a mano.

```javascript
import * as THREE from "three/webgpu";
import { abs, mx_fractal_noise_float, time, uniform, uv, vec3 } from "three/tsl";

const material = new THREE.MeshBasicNodeMaterial();

const amplitude = uniform(0.5);
material.colorNode = vec3(abs(mx_fractal_noise_float(uv().mul(10).add(time.mul(0.2)))).mul(amplitude));

// actualiza desde JS sin tocar el grafo de nodos:
amplitude.value = 1.0;
```

### Texturas y discard

`texture(map, uvNode)` muestrea una textura (`texture(map)` usa las UV del mesh); `.discard()` sobre una condición descarta el fragmento, igual que `discard` en GLSL. El shader de disolución de arriba en TSL:

```javascript
import * as THREE from "three/webgpu";
import { Fn, color, mix, smoothstep, texture, uniform, uv } from "three/tsl";

const noiseMap = await new THREE.TextureLoader().loadAsync("textures/noise.png"); // datos escalares: mantén NoColorSpace
const progress = uniform(0); // anima progress.value de 0 a 1

const material = new THREE.MeshBasicNodeMaterial();
material.colorNode = Fn(() => {
  const n = texture(noiseMap, uv()).r;
  n.lessThan(progress).discard();
  return mix(color(1, 0.5, 0), color(0.5, 0.5, 0.5), smoothstep(progress, progress.add(0.1), n));
})();
```

### Desplazamiento de vértices

`positionNode` sustituye a la posición local transformada. Constrúyelo sobre `positionLocal`, que ya incorpora el skinning, los morph targets, los mapas de desplazamiento, el batching y las transformaciones de InstancedMesh; `positionGeometry` es el atributo en bruto, solo para entradas en pose de reposo. El desplazamiento necesita un mesh subdividido.

```javascript
import * as THREE from "three/webgpu";
import { normalLocal, positionLocal, sin, time } from "three/tsl";

const sun = new THREE.DirectionalLight(0xffffff, 2);
sun.position.set(1, 2, 3);
scene.add(sun, new THREE.HemisphereLight(0xffffff, 0x223344, 1)); // material iluminado: negro sin luces ni scene.environment

const material = new THREE.MeshStandardNodeMaterial({ flatShading: true }); // normales a partir de la superficie desplazada; las normales de vértice ignoran positionNode
material.positionNode = positionLocal.add(normalLocal.mul(sin(positionLocal.y.mul(4).add(time))).mul(0.2));

const mesh = new THREE.Mesh(new THREE.PlaneGeometry(2, 2, 96, 96), material);
mesh.rotation.x = -Math.PI / 3; // inclínalo para que se vea el desplazamiento a lo largo de la normal
scene.add(mesh);
```

### Lógica reutilizable

Escribe la lógica reutilizable como una `Fn` de TSL; se compila tanto a GLSL como a WGSL. `varying(node, "name")` pasa un valor de la etapa de vértices a la de fragmentos.

```javascript
import * as THREE from "three/webgpu";
import { Fn, color, mix, positionWorld, sin, varying } from "three/tsl";

const heightFade = Fn(([y]) => mix(color(0x003344), color(0x88eeff), sin(y.mul(3)).mul(0.5).add(0.5)));

const material = new THREE.MeshBasicNodeMaterial();
const vWorldY = varying(positionWorld.y, "vWorldY"); // interpolado de la etapa de vértices a la de fragmentos
material.colorNode = heightFade(vWorldY);
```

### Portar GLSL

Reescribe las funciones GLSL como `Fn` en lugar de pegar cadenas de shader: `glslFn` solo funciona en el backend WebGL 2 y `wgslFn` solo en el backend WebGPU, así que ninguna es portable. Los compute shaders se despachan mediante `renderer.compute()` tras `await renderer.init()`.

### Depuración

`await renderer.debug.getShaderAsync(scene, camera, mesh)` devuelve el `{ vertexShader, fragmentShader }` generado para un mesh.

## Errores comunes

- `const clock = new THREE.Clock();` → `const timer = new THREE.Timer(); timer.connect(document);`: Clock está obsoleto desde r183; llama primero a timer.update() en cada fotograma y luego a timer.getElapsed() o timer.getDelta().
- `"#include <output_fragment>"` → `"#include <opaque_fragment>"`: output_fragment no existe, así que un reemplazo de cadena dirigido a él no coincide con nada y no avisa.
- `fragmentShader: "uniform vec3 color;\nvoid main() {\n  gl_FragColor = vec4(color, 1.0);\n}"` → `fragmentShader: "uniform vec3 color;\nvoid main() {\n  gl_FragColor = vec4(color, 1.0);\n  #include <tonemapping_fragment>\n  #include <colorspace_fragment>\n}"`: los uniforms de color contienen valores lineales y, sin los dos includes, cada uno en su propia línea, la salida nunca se codifica, así que los tonos medios se ven más oscuros que en los materiales integrados.
- `const renderer = new THREE.WebGPURenderer(); const material = new THREE.ShaderMaterial({ vertexShader, fragmentShader });` → `const material = new THREE.MeshBasicNodeMaterial(); material.colorNode = color(0xff0000);`: con WebGPURenderer, ShaderMaterial registra "not compatible" y onBeforeCompile nunca se ejecuta; estas API solo funcionan con WebGLRenderer.
- `material.positionNode = positionGeometry.add(offset)` → `material.positionNode = positionLocal.add(offset)`: positionLocal ya incorpora el skinning, los morph targets, el batching y las transformaciones de instancias; positionGeometry es el atributo en bruto.
- `import { time } from "three/nodes"` → `import { time } from "three/tsl"`: el módulo three/nodes no existe; los nombres de TSL salen de three/tsl y los node materials de three/webgpu.
- `import { toVarying } from "three/tsl"` → `varying(node, "vName")`: la función exportada es varying(); toVarying existe solo como método node.toVarying("vName").
- `import { uniforms, PI2 } from "three/tsl"` → `import { uniformArray, TWO_PI } from "three/tsl"`: uniformArray() sustituyó a uniforms() en r168 y TWO_PI a PI2 en r181.
- `amplitude.label("amp")` → `amplitude.setName("amp")`: setName() sustituyó a label() en r179; label() todavía asigna el nombre pero registra un aviso de obsolescencia.
- `texture(map).uv(uvNode)` → `texture(map).sample(uvNode)`: TextureNode.sample() sustituyó a uv() en r172.
- `import { screen, viewportTopLeft, directionToColor } from "three/tsl"` → `import { blendScreen, viewportUV, packNormalToRGB } from "three/tsl"`: blendScreen sustituyó a screen() en r171, viewportUV a viewportTopLeft en r168 y packNormalToRGB a directionToColor() en r185.
- `rangeFog(color, near, far)` → `fog(color, rangeFogFactor(near, far))`: three/tsl ya no exporta rangeFog(); fog() recibe un nodo de factor.
- `const t = uniform(0); t.value = timer.getElapsed();` → `time`: el nodo time integrado se actualiza solo en cada fotograma, así que el ida y vuelta mediante un uniform es innecesario.
- `const n = glslFn(glslSource);` → `const n = Fn(([p]) => mx_noise_float(p));`: glslFn solo funciona en el backend WebGL 2 y wgslFn solo en el backend WebGPU; una Fn de TSL se compila para ambos.
- `uniforms: { modelViewMatrix: { value: new THREE.Matrix4() } }` → `uniform mat4 modelViewMatrix;`: el renderer fija las matrices integradas para cualquier programa que las declare, así que una entrada en uniforms se sobrescribe en cada draw (modelMatrix, modelViewMatrix, normalMatrix) o sustituye el valor de la cámara (projectionMatrix, viewMatrix, cameraPosition); la declaración GLSL es para un RawShaderMaterial, ya que un ShaderMaterial ya declara las matrices y redeclararlas no compila.
- `new THREE.ShaderMaterial({ transparent: true, opacity: 0.5 })` → `new THREE.ShaderMaterial({ transparent: true, uniforms: { opacity: { value: 0.5 } } })`: ShaderMaterial nunca sube material.opacity, así que declara `uniform float opacity` y escríbelo en el canal alfa.
- `uniforms: { position: { value: new THREE.Vector3() } }` → `uniforms: { offset: { value: new THREE.Vector3() } }`: position colisiona con el atributo que three.js declara en todo vertex shader de ShaderMaterial.
- `new THREE.ShaderMaterial({ glslVersion: THREE.GLSL3, vertexShader, fragmentShader })` → `new THREE.ShaderMaterial({ vertexShader, fragmentShader })`: ShaderMaterial siempre se compila como GLSL ES 3.00, y GLSL3 solo elimina el alias gl_FragColor, así que un shader que siga escribiendo en gl_FragColor deja de compilar.
- `new THREE.RawShaderMaterial({ vertexShader, fragmentShader })` → `new THREE.RawShaderMaterial({ vertexShader, fragmentShader, glslVersion: THREE.GLSL3 })`: sin glslVersion, un RawShaderMaterial se compila como GLSL ES 1.00, que no tiene texture().
- `new THREE.ShaderMaterial({ vertexShader, fragmentShader, extensions: { derivatives: true, fragDepth: true } })` → `new THREE.ShaderMaterial({ vertexShader, fragmentShader })`: las claves de extensión de WebGL 1 se eliminaron en r163 y se ignoran; dFdx, gl_FragDepth y textureLod son del núcleo en GLSL ES 3.00, y extensions ahora solo contiene clipCullDistance y multiDraw.
- `blending: THREE.MultiplyBlending` → `blending: THREE.MultiplyBlending, premultipliedAlpha: true`: MultiplyBlending y SubtractiveBlending no fijan ninguna función de mezcla y registran un error salvo que el alfa premultiplicado esté activado, y un ShaderMaterial con alfa menor que 1 debe entonces premultiplicar su propia salida con #include <premultiplied_alpha_fragment>.
- `gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);` → `gl_Position = projectionMatrix * modelViewMatrix * instanceMatrix * vec4(position, 1.0);`: en un InstancedMesh three.js declara instanceMatrix, pero el shader debe aplicarla, o todas las instancias se dibujan con la transformación del propio mesh.
- `varying vec2 vUv1; void main() { vUv1 = uv1; }` → `attribute vec2 uv1; varying vec2 vUv1; void main() { vUv1 = uv1; }`: three.js declara position, normal y uv para un ShaderMaterial; uv1 a uv3 y tangent necesitan tu propia declaración.
- `dot(normalize(cameraPosition - vWorldPosition), normalize(normalMatrix * normal))` → `dot(normalize(cameraPosition - vWorldPosition), normalize(mat3(modelMatrix) * normal))`: normalMatrix produce normales en espacio de vista mientras que cameraPosition está en espacio del mundo, así que el término deriva al rotar la cámara.
- `material.onBeforeCompile = (shader) => console.log(shader.fragmentShader);` → `renderer.debug.onShaderError = (gl, program, vs, fs) => console.error(gl.getShaderSource(fs));`: onBeforeCompile se ejecuta antes de que se resuelvan los includes y se añada el prefijo, mientras que onShaderError recibe los shaders ya ensamblados cuando un programa falla al compilar o enlazar.

## Véase también

- `references/materials.md`: materiales integrados y sus mapas de textura, cuando un material estándar ya resuelve el trabajo
- `references/textures.md`: carga de texturas, espacios de color y canales UV para mapas muestreados en shaders
- `references/postprocessing.md`: pasadas a pantalla completa (bloom, contorno) en lugar de shaders por objeto
