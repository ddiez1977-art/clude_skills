# React Three Fiber en Three.js

Dirigido a three.js r186. Los ejemplos usan WebGLRenderer; la sección de WebGPU y TSL usa WebGPURenderer.

## Inicio rápido

Dirigido a `@react-three/fiber` 9.8 con React 19 y `@react-three/drei` 10.7. El Canvas crea y posee un WebGLRenderer, una escena y una cámara; los objetos de three.js se convierten en elementos JSX. El Canvas ocupa todo su elemento padre, así que dale altura al padre. Los fragmentos de componentes de más abajo se renderizan dentro de un Canvas como este; los materiales con iluminación suponen sus luces.

```jsx
import { useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";

function Box() {
  const ref = useRef();
  useFrame((_, delta) => {
    ref.current.rotation.y += delta;
  });
  return (
    <mesh ref={ref} position={[0, 0.5, 0]} castShadow>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="#d9915b" />
    </mesh>
  );
}

export default function App() {
  return (
    <Canvas shadows="percentage" camera={{ position: [3, 2, 4], fov: 50 }}>
      <color attach="background" args={["#111827"]} />
      <ambientLight intensity={0.4} />
      <directionalLight position={[3, 4, 2]} intensity={2} castShadow />
      <Box />
      <mesh rotation-x={-Math.PI / 2} receiveShadow>
        <planeGeometry args={[10, 10]} />
        <meshStandardMaterial color="#20293a" />
      </mesh>
      <OrbitControls makeDefault />
    </Canvas>
  );
}
```

## Props del Canvas

```jsx
export function App() {
  return (
    <Canvas
      shadows="variance"
      dpr={[1, 2]}
      frameloop="demand"
      flat
      camera={{ position: [0, 2, 6], fov: 45 }}
      gl={{ powerPreference: "high-performance" }}
      onCreated={(state) => state.gl.setClearColor("#111827")}
    >
      {/* contenido de la escena */}
    </Canvas>
  );
}
```

- `camera`: props para la cámara por defecto, o una instancia de cámara. Sin ella obtienes una `PerspectiveCamera` con fov 75, near 0.1, far 1000, en z 5 mirando al origen; fiber actualiza aspect (o left/right/top/bottom con `orthographic`) y la matriz de proyección en cada redimensionado. `camera={{ manual: true }}` deja la proyección enteramente en tus manos.
- `dpr`: un número, o `[min, max]` acotado frente a `window.devicePixelRatio`; el rango sigue los cambios de pantalla.
- `shadows`: `true` activa los shadow maps, una cadena (`'basic'`, `'percentage'`, `'variance'`) elige el tipo de filtro, un objeto se fusiona en las propiedades `shadowMap` del renderer. `true`, `'soft'` y el valor por defecto `false` establecen todos PCFSoftShadowMap, que three cambia por PCFShadowMap con un aviso en la consola (WebGLRenderer cuando se renderizan sombras, WebGPURenderer en cada Canvas); `'percentage'` es el mismo filtro suave sin el aviso.
- `flat` establece NoToneMapping; sin él fiber aplica ACESFilmicToneMapping — a diferencia de three.js puro, el tone mapping está activado por defecto. `linear` cambia la salida a LinearSRGBColorSpace; el valor por defecto es sRGB. `legacy` desactiva el ColorManagement de three.
- `gl`: props para el `new WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: "high-performance" })` por defecto, una instancia de renderer, o una función factoría (la vía WebGPU de más abajo).
- `frameloop`: `'always'` renderiza en cada fotograma, `'demand'` renderiza solo tras cambios de React o `invalidate()`, `'never'` cede el bucle (llama a la exportación `advance(timestamp)` a nivel de módulo con un tiempo en segundos; el delta de `useFrame` es la diferencia entre marcas de tiempo sucesivas, así que con milisegundos sale 1000 veces demasiado grande).
- `events` sustituye al gestor de eventos (el de por defecto traduce eventos de puntero del DOM a raycasts); `eventSource` (un elemento al que se enganchan los eventos de puntero, por defecto el wrapper del Canvas) y `eventPrefix` (`'offset'` por defecto; `'page'`, `'client'`, `'layer'`, `'screen'` cuando la página hace scroll o transforma el canvas) ajustan el mapeo del puntero. `onCreated` se ejecuta cuando el renderer ya existe; `onPointerMissed` se dispara en los clics que no alcanzan nada.

## El grafo de escena como JSX

Cada exportación del namespace de three es un elemento: etiqueta en minúscula, clase con mayúscula inicial (`<mesh>` → `THREE.Mesh`, `<meshStandardMaterial>` → su material). Las props se aplican a la instancia; los valores abreviados funcionan en cualquier sitio donde three tenga un `.set()`: `position={[1, 2, 3]}`, `position={new THREE.Vector3(1, 2, 3)}`, `position={5}` (setScalar), `color="#d9915b"`. Las props con guiones atraviesan (`rotation-x`, `material-color`, `geometry-attributes-position`); `attach="material-0"` engancha en un índice de array.

`args` es la lista de argumentos del constructor; cambiarla reconstruye el objeto desde cero. Las geometrías y los materiales se enganchan automáticamente a su malla padre — no hace falta `attach`.

```jsx
function Torus() {
  return (
    <mesh position={[0, 1, 0]}>
      <torusKnotGeometry args={[0.7, 0.25, 128, 24]} />
      <meshStandardMaterial
        color="#42699c"
        roughness={0.2}
        metalness={0.8}
        onUpdate={(self) => console.log(self.type)}
      />
    </mesh>
  );
}
```

Monta un objeto que ya tengas con `<primitive object={obj} />`; un objeto por primitive (fiber guarda su estado por objeto en el propio objeto), y clona para hacer copias. Fiber nunca libera (dispose) los primitives — su ciclo de vida es tuyo. `dispose={null}` en cualquier elemento lo excluye de la liberación al desmontarse. Registra las clases ajenas al namespace de three con `extend`:

```jsx
import { extend } from "@react-three/fiber";
import { Water } from "three/addons/objects/Water.js";

extend({ Water });
// luego renderiza <water args={[geometry]} /> en cualquier lugar del Canvas
```

En TypeScript, las etiquetas `line`, `audio`, `source` y `path` colisionan con tipos del DOM; escribe `threeLine`, `threeAudio`, `threeSource`, `threePath` (fiber elimina el prefijo y resuelve la clase de three).

## Hooks

`useFrame(callback, renderPriority?)` se suscribe al bucle de render; se ejecuta antes de que se renderice la escena:

```jsx
import { useRef } from "react";
import { useFrame } from "@react-three/fiber";

function Spinner({ radius = 2 }) {
  const ref = useRef();
  useFrame((state, delta) => {
    ref.current.rotation.y += delta;
    ref.current.position.x = Math.sin(state.clock.elapsedTime) * radius;
  });
  return (
    <mesh ref={ref}>
      <sphereGeometry args={[0.4, 32, 16]} />
      <meshBasicMaterial color="#e8b4a0" />
    </mesh>
  );
}
```

Los suscriptores con un `renderPriority` positivo toman el renderizado en sus manos — el Canvas deja de renderizar, y tu callback debe llamar él mismo a `state.gl.render(state.scene, state.camera)`. Con la prioridad por defecto, llamar tú a `gl.render` renderiza dos veces.

`useThree(selector?)` lee el estado del Canvas de forma reactiva; sin selector devuelve el estado completo (`gl`, `camera`, `scene`, `raycaster`, `pointer`, `size`, `viewport`, `invalidate`, `setDpr`, `setFrameloop`, `controls`, `performance`):

```jsx
import { useThree } from "@react-three/fiber";

const camera = useThree((state) => state.camera);
const invalidate = useThree((state) => state.invalidate);
```

Dentro de `useFrame` usa el argumento `state` en su lugar — es el mismo estado sin un re-render. `state.clock` es un `THREE.Clock` que crea fiber 9.8, así que cada Canvas registra el aviso de obsolescencia de Clock de three; no viene de tu código.

`useLoader(ClassOrInstance, url, extensions?, onProgress?)` suspende hasta que se resuelve cualquier loader de three y cachea por loader y URL; quien lo llama debe estar bajo un límite de Suspense. El callback de extensions se ejecuta sobre la única instancia de loader que fiber mantiene por clase, así que un ajuste que haga (una ruta, un decodificador) se aplica a todas las llamadas posteriores a `useLoader` con esa clase. `useGraph(object)` construye mapas de búsqueda con nombre (`{ nodes, materials, meshes }`) a partir de un árbol de objetos:

```jsx
import { useGraph, useLoader } from "@react-three/fiber";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";

function Model({ url }) {
  const gltf = useLoader(GLTFLoader, url, (loader) => loader.setPath("assets/"));
  const { nodes } = useGraph(gltf.scene);
  return <primitive object={gltf.scene} />;
}
```

`useLoader.preload(Class, url)` calienta la caché fuera de React; `useLoader.clear(Class, url)` elimina una entrada.

## Eventos de puntero

A los objetos con manejadores se les lanza un raycast en cada evento de puntero (los movimientos de puntero solo prueban objetos con manejadores de move, over, out, enter o leave); los manejadores se disparan empezando por el más cercano, burbujeando desde el objeto alcanzado hacia sus padres. El evento lleva la intersección más utilidades: `object`, `eventObject` (el objeto que registró el manejador), `point`, `distance`, `face`, `instanceId`, `intersections`, `ray`, `camera`, `unprojectedPoint`, `delta` (píxeles recorridos desde pointerdown, para eventos de tipo clic), `nativeEvent`. Manejadores: `onClick`, `onDoubleClick`, `onContextMenu`, `onWheel`, `onPointerUp`, `onPointerDown`, `onPointerMove`, `onPointerOver`, `onPointerOut`, `onPointerEnter`, `onPointerLeave`, `onPointerMissed` (`onPointerCancel` y `onLostPointerCapture` están tipados, pero fiber nunca los llama en los objetos).

```jsx
import { useState } from "react";

function Pickable() {
  const [hovered, setHovered] = useState(false);
  return (
    <mesh
      onClick={(event) => {
        event.stopPropagation(); // los objetos de debajo a lo largo del rayo ya no lo reciben
        console.log(event.object.name, event.distance, event.point, event.instanceId);
      }}
      onPointerOver={(event) => {
        event.stopPropagation();
        setHovered(true);
      }}
      onPointerOut={() => setHovered(false)}
      onPointerDown={(event) => {
        event.target.setPointerCapture(event.pointerId); // los eventos de este puntero llegan a la malla fuera de su superficie hasta que se libere
      }}
      onPointerUp={(event) => {
        event.target.releasePointerCapture(event.pointerId);
      }}
      onPointerMissed={() => console.log("clicked elsewhere")}
    >
      <sphereGeometry args={[0.75, 32, 16]} />
      <meshStandardMaterial color={hovered ? "#e8b4a0" : "#42699c"} />
    </mesh>
  );
}
```

Los eventos de puntero funcionan con cualquier renderer: el raycaster por defecto prueba la geometría de CPU en `intersectObject(object, true)`. Pasa `raycaster={{ params: { Line: { threshold: 0.1 } } }}` para ajustarlo.

## Carga de recursos

Los hooks de carga suspenden; pon el límite por encima de ellos y el fallback se muestra mientras cargan.

```jsx
import { Suspense } from "react";
import { Canvas } from "@react-three/fiber";
import { useGLTF, useProgress, Environment } from "@react-three/drei";

function Model({ url }) {
  const { scene, animations, nodes, materials } = useGLTF(url);
  return <primitive object={scene} />;
}

function Hud() {
  const { active, progress, errors } = useProgress(); // sigue el DefaultLoadingManager de three
  return <div>{active ? `${progress.toFixed(0)}%` : errors.length > 0 ? "failed" : "done"}</div>;
}

export function App() {
  return (
    <>
      <Hud />
      <Canvas camera={{ position: [3, 2, 4], fov: 50 }}>
        <Suspense fallback={null}>
          <Environment preset="city" />
          <Model url="model.glb" />
        </Suspense>
      </Canvas>
    </>
  );
}
```

- `useGLTF(url)` carga mediante el GLTFLoader que incluye drei (three-stdlib), con Draco y meshopt habilitados por defecto; el decodificador de Draco viene de una URL fija de gstatic (`useGLTF.setDecoderPath` la redirige, `useGLTF(url, false)` lo desactiva). `useGLTF.preload(url)` calienta la caché. El resultado lleva `scene`, `animations`, `cameras` más los mapas de búsqueda `nodes`/`materials`/`meshes`. Para varias copias de un modelo con skinning, clónalo una vez por componente con `useMemo(() => SkeletonUtils.clone(scene), [scene])` (`import * as SkeletonUtils from "three/addons/utils/SkeletonUtils.js"`) y monta cada clon en su propio primitive.
- `useTexture(input)` carga una URL, un array (`const [a, b] = useTexture([x, y])`) o un objeto con claves; fiber establece el espacio de color sRGB en los mapas de color LDR (RGBA8) asignados mediante props — `map`, `emissiveMap`, `envMap` entre ellos — así que los mapas de color funcionan sin `colorSpace` manual, y los mapas escalares conservan NoColorSpace.
- `<Preload all />` compila todos los materiales una vez, cuando se monta (con `all`, también los de objetos ocultos), y renderiza la escena en un cube target para subir las texturas, cambiando un bloqueo único por la ausencia de tirones en la primera vista; ponlo dentro del límite de Suspense después de los recursos, o se ejecutará antes de que estos carguen.
- `useProgress` es un store simple, así que el Hud de arriba lo lee fuera del Canvas, en el DOM.

## Utilidades de drei

drei incluye muchas más utilidades que estas; solo este subconjunto está verificado aquí, y todas se importan de `@react-three/drei`.

Controles: `OrbitControls` construye la clase de controles que incluye drei, la conecta a la fuente de eventos (por defecto el wrapper del Canvas), la actualiza en cada fotograma antes de los callbacks del usuario, llama a `invalidate()` al cambiar (por lo que funciona con `frameloop="demand"`) y activa el damping por defecto. `makeDefault` lo guarda en `state.controls` (Bounds y otras utilidades lo recogen); `regress` baja el valor de rendimiento adaptativo mientras se arrastra. Las props pasan directamente a la instancia de los controles:

```jsx
import { OrbitControls } from "@react-three/drei";

<OrbitControls
  makeDefault
  enableDamping
  dampingFactor={0.1}
  target={[0, 1, 0]}
  minDistance={2}
  maxDistance={12}
  maxPolarAngle={Math.PI / 2}
  autoRotate
  autoRotateSpeed={0.5}
/>
```

`CameraControls` envuelve de la misma manera la librería camera-controls (métodos de ref como `fitToBox` vienen de esa librería, y se actualiza con el delta del fotograma).

Decoración de la escena:

```jsx
import {
  ContactShadows, Environment, Lightformer, Text, Html, Center, Bounds,
} from "@react-three/drei";

export function Dressing({ overlay }) { // overlay: una ref a un elemento DOM superpuesto al Canvas
  return (
    <group>
      <Environment resolution={256}>
        <Lightformer form="rect" intensity={2} position={[0, 4, 3]} scale={[8, 2, 1]} />
      </Environment>
      <ContactShadows position={[0, -1, 0]} opacity={0.6} scale={12} blur={2.4} far={4} />
      <Bounds fit clip observe margin={1.5}>
        <mesh>
          <sphereGeometry args={[1, 32, 16]} />
          <meshStandardMaterial metalness={0.9} roughness={0.2} />
        </mesh>
        <Center top position={[2.5, -1, 0]}>
          <mesh>
            <boxGeometry args={[1, 0.6, 1]} />
            <meshStandardMaterial />
          </mesh>
        </Center>
      </Bounds>
      <Text position={[0.75, 1.1, 0]} fontSize={0.4} anchorX="center" anchorY="bottom" color="#e8b4a0" outlineWidth={0.02}>
        three.js
      </Text>
      <Html portal={overlay} position={[2.5, 0.2, 0]} center distanceFactor={8} occlude="raycast">
        <div>dom overlay anchored to the scene</div>
      </Html>
    </group>
  );
}
```

- `ContactShadows` renderiza la escena desde abajo en un target de profundidad y lo desenfoca — un plano de sombra de contacto suave bajo los objetos cercanos al suelo, sin configurar shadow maps; pon `frames={1}` para hornearlo una vez en escenas estáticas.
- `Lightformer` es una tarjeta de luz — una malla con un material básico, `form` `circle`, `ring`, `rect` o `box` — pensada para colocarse dentro de la escena de hijos de un `<Environment>`, que se hornea en los reflejos.
- `Text` renderiza texto SDF (troika) con las props de maquetación `maxWidth`, `textAlign`, `lineHeight`, `letterSpacing`, `characters`; suspende mientras carga la fuente.
- `Html` proyecta un nodo del DOM en la escena; `transform` lo renderiza como una superposición rotada en 3D en lugar de orientada a la pantalla. `occlude` (`true` o `"raycast"`) lo oculta mientras la geometría bloquea el rayo hasta su ancla, así que no lo ancles nunca dentro de una malla; `occlude="blending"` lo oculta por profundidad mediante un ShaderMaterial (solo WebGL). Con fiber 9.8, drei 10.7 y React 19.2, un `Html` que se monta en el mismo commit que un Canvas por defecto (WebGLRenderer) aparece vacío, y también el que se vuelve a montar junto con su Canvas; pasa a `portal` una ref a un elemento DOM superpuesto al canvas, que mantiene fijo su contenedor, como hace Dressing: `<div ref={overlay} style={{ position: "absolute", inset: 0, pointerEvents: "none" }} />` después del Canvas, dentro de un wrapper con `position: relative`.
- `Center` recentra los hijos sobre su caja envolvente (`top`/`bottom`/`left`/`right`/`front`/`back` alinean a un borde, `precise={false}` mide los límites por objeto en lugar de cada vértice, `onCentered` informa de la caja). Mide posiciones de vértices, así que coloca mal el `Text` de drei, cuya geometría es un quad unitario; coloca Text con `anchorX`, `anchorY` y `position` en su lugar.
- `Bounds` ajusta y encuadra la cámara alrededor de sus hijos (`fit`, `clip` ajusta near/far, `observe` reajusta al redimensionar); `useBounds()` devuelve su API imperativa (`refresh`, `reset`, `moveTo`, `lookAt`, `fit`, `clip`).

## Rendimiento

Renderiza bajo demanda: si nada cambia, nada se renderiza.

```jsx
import { useEffect, useRef } from "react";
import { useThree } from "@react-three/fiber";

function OnDemand() {
  const ref = useRef();
  const invalidate = useThree((state) => state.invalidate);
  // bajo <Canvas frameloop="demand"> los cambios imperativos son invisibles para React — solicita un fotograma para ellos
  useEffect(() => {
    const id = setInterval(() => {
      ref.current.rotation.y += 0.5;
      invalidate();
    }, 100);
    return () => clearInterval(id);
  }, [invalidate]);
  return (
    <mesh ref={ref}>
      <boxGeometry args={[1, 1, 1]} />
      <meshNormalMaterial />
    </mesh>
  );
}
```

Los cambios de React (props, estado) invalidan automáticamente. No llames nunca a `setState` en `useFrame` — muta los objetos mediante refs, como hace el Inicio rápido; un store o `flushSync` cubre el raro caso en que el DOM deba seguir valores por fotograma.

Muchas copias de una misma forma comparten una draw call mediante `Instances`; cada `Instance` es una transformación declarativa (y un `color` opcional) que se compone en la matriz instanciada en cada fotograma:

```jsx
import { Instance, Instances } from "@react-three/drei";

function Crowd({ count = 200 }) {
  return (
    <Instances limit={count} castShadow>
      <capsuleGeometry args={[0.25, 0.8, 4, 12]} />
      <meshStandardMaterial />
      {Array.from({ length: count }, (_, i) => (
        <Instance
          key={i}
          position={[(i % 15) - 7, 0.65, Math.floor(i / 15) - 7]}
          color={`hsl(${(i * 37) % 360}, 60%, 55%)`}
        />
      ))}
    </Instances>
  );
}
```

`Detailed` elige uno de sus hijos según la distancia de la cámara (el `LOD` de three), para geometría barata en el campo lejano: el hijo i se muestra a partir de `distances[i]` (la primera entrada es 0), y `hysteresis` es una fracción de esa distancia que retrasa el cambio de vuelta a un detalle más fino:

```jsx
import { Detailed } from "@react-three/drei";

<Detailed distances={[0, 15, 40]} hysteresis={0.1}>
  <mesh><sphereGeometry args={[1, 64, 32]} /><meshStandardMaterial /></mesh>
  <mesh><sphereGeometry args={[1, 16, 8]} /><meshStandardMaterial /></mesh>
  <mesh><sphereGeometry args={[1, 8, 4]} /><meshStandardMaterial /></mesh>
</Detailed>
```

Resolución adaptativa: los controles con `regress` bajan `performance.current` a `min` (0,5 por defecto) mientras se arrastra y lo restauran tras 200 ms; `AdaptiveDpr` fija el pixel ratio a ese valor multiplicado por el primer ratio que resolvió el Canvas, así que todo arrastre termina en ese primer ratio. `PerformanceMonitor` muestrea las tasas de fotogramas reales e informa mediante callbacks — él no toca el pixel ratio. Gobierna la prop `dpr` del Canvas desde sus callbacks mediante estado de React, porque el Canvas vuelve a aplicar esa prop cada vez que se re-renderiza, lo que deshace una llamada a `setDpr` hecha desde dentro; mantén `AdaptiveDpr` fuera de ese Canvas, o el siguiente arrastre restaurará el primer ratio por encima de un `dpr` reducido:

```jsx
import { useState } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, AdaptiveDpr, PerformanceMonitor } from "@react-three/drei";

// reduce la resolución mientras se mueven los controles
export function DragTunedApp() {
  return (
    <Canvas dpr={[1, 2]}>
      <OrbitControls regress />
      <AdaptiveDpr pixelated />
      {/* contenido de la escena */}
    </Canvas>
  );
}

// deja que la tasa de fotogramas medida elija la resolución mediante la prop dpr
export function MonitoredApp() {
  const [dpr, setDpr] = useState([1, 2]);
  return (
    <Canvas dpr={dpr}>
      <OrbitControls />
      <PerformanceMonitor
        onDecline={() => setDpr(1)}
        onIncline={() => setDpr([1, 2])}
        flipflops={3}
        onFallback={() => setDpr(1)}
      />
      {/* contenido de la escena */}
    </Canvas>
  );
}
```

Más allá de las herramientas propias de fiber: limita `dpr`, prefiere texturas KTX2, fusiona o instancia la geometría, libera lo que desmontes — consulta `references/performance.md`.

## Liberación de recursos

Fiber libera (dispose) lo que crea cuando se desmonta (programado para el tiempo ocioso): el objeto detrás de cada elemento JSX, incluidas las geometrías, materiales y texturas declarados como hijos JSX, y el renderer que construyó a partir de las props de `gl` o de una factoría. Los objetos pasados a través de props (`geometry={...}`, `map={...}`) y los primitives nunca se liberan, y `dispose={null}` exime a un elemento y a sus hijos. Un renderer cuya instancia hayas pasado tú no se libera, pero fiber fuerza la pérdida de su contexto al desmontarse, así que no se puede reutilizar. Los recursos cargados mediante `useLoader`, `useGLTF` y `useTexture` permanecen en caché para los remontajes; el `clear` del hook solo elimina la entrada de la caché, así que libera tú mismo las geometrías, materiales y texturas que ya no necesites. La exportación `dispose(object)` a nivel de módulo llama a `dispose()` en el objeto y en cada una de sus propias propiedades que lo tenga (la geometría y el material de una malla); no visita a los hijos, así que recorre tú el árbol.

## WebGPU y TSL

La prop `gl` acepta una factoría asíncrona: construye el WebGPURenderer con las props que te da fiber, espera su inicialización y devuélvelo — fiber espera la promesa dentro del Canvas y renderiza los hijos cuando se resuelve (un fallback de Suspense alrededor del Canvas no se muestra mientras tanto). Como el Canvas inicializa su catálogo de elementos con el namespace de three simple (que no tiene materiales de nodos), fusiona el namespace `three/webgpu` con `extend` antes de usar elementos de materiales de nodos. Los nodos TSL de `three/tsl` pasan por las props de la misma manera, pero un material compila sus nodos una sola vez: construye los nodos una vez (a nivel de módulo o con `useMemo`) y anima mediante valores `uniform()`, porque un nodo nuevo pasado en un render posterior se asigna sin recompilar hasta que pongas `material.needsUpdate = true`:

```jsx
import * as THREE from "three/webgpu";
import { color } from "three/tsl";
import { Canvas, extend, useFrame } from "@react-three/fiber";
import { useRef } from "react";

extend(THREE); // los materiales de nodos y las clases de WebGPU se unen al catálogo de elementos

function Knot() {
  const ref = useRef();
  useFrame((_, delta) => {
    ref.current.rotation.y += delta;
  });
  return (
    <mesh ref={ref}>
      <torusKnotGeometry args={[0.8, 0.3, 128, 24]} />
      <meshBasicNodeMaterial colorNode={color(0x42699c)} />
    </mesh>
  );
}

export default function App() {
  return (
    <Canvas
      camera={{ position: [3, 2, 4], fov: 50 }}
      gl={async (props) => {
        const renderer = new THREE.WebGPURenderer(props);
        await renderer.init();
        return renderer;
      }}
    >
      <color attach="background" args={["#111827"]} />
      <Knot />
    </Canvas>
  );
}
```

Fiber aplica sus valores de color por defecto también al renderer de una factoría: ACESFilmicToneMapping (NoToneMapping con `flat`) y salida sRGB. WebGPURenderer aplica tone mapping a todo el fotograma, fondo incluido, así que el mismo `<color attach="background">` se renderiza más oscuro que con WebGLRenderer a menos que el Canvas sea `flat`.

Comprobado renderizando con WebGPURenderer en su backend WebGPU y con `forceWebGL: true` (fiber 9.8.2, drei 10.7.9). Funcionan en ambos backends: el grafo de escena, los hooks, los eventos (el raycaster prueba la geometría de CPU, así que el desplazamiento por `positionNode` es invisible para él), `useGLTF` (los materiales cargados se convierten en materiales de nodos), `useTexture`, `Preload`, `Center`, `Bounds`, `Instances`, `Detailed`, `OrbitControls`, `CameraControls`, `Html` sin `occlude="blending"`, y `Environment` con `preset`, `map` o archivos `.hdr`; `useProgress`, `AdaptiveDpr` y `PerformanceMonitor` no llaman a ninguna API del renderer (se ha leído en su código fuente).

No son seguros para WebGPU: `Text` dibuja un quad sin textura en lugar de glifos (troika inyecta su shader SDF mediante `onBeforeCompile`), `ContactShadows` (un material de profundidad con `onBeforeCompile` y `ShaderMaterial`s de desenfoque, que three informa como no compatibles), `Html` con `occlude="blending"`, `Environment` con `ground` o con `files` de gainmap `.jpg`/`.webp` (ambos dibujan mediante ShaderMaterials; se ha leído en el código fuente), y `Environment` con hijos, que hornea mediante una cámara de cubo que da reflejos en el backend WebGPU pero los deja negros en el fallback WebGL 2, sin ningún error. Los slots de material TSL (`colorNode`, `positionNode`) se comportan exactamente como en `references/shaders.md` — escribe código `Fn`, no GLSL.

## Errores comunes

- `requestAnimationFrame(tick)` → `useFrame((state, delta) => { ... })`: el Canvas ya ejecuta el bucle de fotogramas; un bucle aparte compite con él y se salta sus efectos.
- `state.clock.getElapsedTime()` → `state.clock.elapsedTime`: getElapsedTime() llama internamente a getDelta(), lo que acorta el delta que fiber mide para el siguiente fotograma.
- `import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js"` → `import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js"`: `three/addons/` se resuelve tanto con bundlers como con los import maps que documenta three.js, mientras que la ruta `examples/jsm` falla con esos import maps.
- `useFrame(() => { ref.current.rotation.y += 0.01; })` → `useFrame((_, delta) => { ref.current.rotation.y += delta; })`: el segundo argumento es el delta del fotograma; un incremento fijo se ejecuta a distinta velocidad en cada frecuencia de refresco.
- `useFrame((_, delta) => setRotation((r) => r + delta))` → `useFrame((_, delta) => { ref.current.rotation.y += delta; })`: el estado fijado en el bucle de fotogramas re-renderiza React en cada fotograma; muta los objetos mediante refs.
- `useFrame((state, delta) => { ref.current.rotation.y += delta; }, 1)` → `useFrame((_, delta) => { ref.current.rotation.y += delta; })`: una prioridad de render positiva hace que el Canvas deje de renderizar, y la escena se queda negra salvo que tu callback llame él mismo a `state.gl.render(state.scene, state.camera)`.
- `<mesh position={{ x: 1, y: 0, z: 0 }}>` → `<mesh position={[1, 0, 0]}>`: `position` es una propiedad de solo lectura que contiene un Vector3, así que un objeto simple lanza «Cannot assign to read only property» y el Canvas falla, mientras que los arrays, números y Vector3 se escriben en el Vector3 existente (`fromArray`, `setScalar`, `copy`).
- `useEffect(() => { new GLTFLoader().load(url, (gltf) => setScene(gltf.scene)); }, [])` → `const gltf = useGLTF(url)`: useGLTF suspende, cachea por URL el modelo ya parseado para remontajes y precargas, y conecta la decodificación de Draco y meshopt, mientras que la versión con effect vuelve a descargar y parsear en cada montaje y no tiene decodificador de Draco.
- `useGLTF(url).scene.clone()` → `useMemo(() => SkeletonUtils.clone(scene), [scene])`: Object3D.clone() comparte un único esqueleto, así que las copias siguen atadas a los huesos del original, mientras que SkeletonUtils revincula cada copia y useMemo mantiene un clon por componente en lugar de uno por render.
- `scene.add(gltf.scene)` → `<primitive object={gltf.scene} />`: un objeto añadido de forma imperativa no admite props de eventos de fiber y permanece en la escena tras desmontarse el componente, mientras que un primitive admite props de eventos y se añade y se quita junto con el componente (su liberación sigue siendo tuya).
- `<water args={[geometry]} />` → `extend({ Water }); <water args={[geometry]} />`: los elementos se resuelven solo contra el namespace de three; las clases de los addons deben registrarse primero.
- `<line>` → `<threeLine>`: la etiqueta simple colisiona con el elemento line de SVG en TypeScript; fiber elimina el `three` inicial y construye THREE.Line.
- `<Canvas shadows>` → `<Canvas shadows="percentage">`: el booleano selecciona PCFSoftShadowMap, obsoleto desde r182 — three recurre a PCF con un aviso en la consola; la cadena elige el tipo sin aviso.
- `<directionalLight intensity={2} />` → `<directionalLight castShadow intensity={2} />`: el castShadow de una malla solo dibuja sombras cuando también proyecta una luz y está activada la opción shadows del Canvas.
- `ref.current.position.x += 1` → `ref.current.position.x += 1; invalidate();`: con frameloop="demand", una mutación a secas nunca repinta, así que llama a `invalidate` (de `useThree((state) => state.invalidate)`) tras los cambios imperativos, mientras que los cambios de props de React se invalidan solos.
- `gl={new THREE.WebGPURenderer()}` → `gl={async (props) => { const renderer = new THREE.WebGPURenderer(props); await renderer.init(); return renderer; }}`: un renderer construido sin el canvas de fiber dibuja en un canvas propio que nunca se muestra, y su render() lanza un error hasta que init() se resuelve, mientras que la factoría recibe el canvas del Canvas y fiber renderiza solo después de que se resuelva.
- `new OrbitControls(camera, renderer.domElement)` → `<OrbitControls makeDefault />`: el componente de drei conecta las actualizaciones por fotograma, la invalidación y la liberación; la clase cruda se atasca con el damping activado y nunca invalida un bucle bajo demanda.
- `<Environment><Lightformer /></Environment>` → `<Environment files="env.hdr" />`: con WebGPURenderer la forma con hijos hornea mediante una cámara de cubo cuyos reflejos salen negros en el backend de fallback WebGL 2 sin ningún error, mientras que los archivos `.hdr` y los presets solo asignan una textura y funcionan en ambos backends.

## Véase también

- `references/fundamentals.md` - los conceptos de renderer, escena y cámara que gestiona el Canvas por ti
- `references/loaders.md` - configuración de loaders, compresión y liberación en profundidad
- `references/interaction.md` - raycasting y controles más allá de los eventos de puntero de fiber
- `references/shaders.md` - materiales de nodos TSL y slots usados dentro de los elementos de fiber
- `references/performance.md` - perfilado y optimización más allá de las herramientas adaptativas de fiber
- `references/asset-pipeline.md` - componentes gltfjsx, y compresión de modelos antes de que useGLTF los cargue
