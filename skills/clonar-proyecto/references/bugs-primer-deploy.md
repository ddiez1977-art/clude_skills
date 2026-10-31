<!-- RECONSTRUIDO el 2026-10-31 a partir del chat "Skill genérica para clonar y revisar estructuras" (2026-06-11): texto íntegro de §1-§10 + parches §11-§15 y filas de la tabla de diagnóstico. No se encontró el fichero original. Lo que se hubiera cambiado después del 11/06 no está aquí. Si ves diferencias con tu versión, manda la tuya y prevalece. -->
# Bugs del Primer Deploy — Referencia Completa

Catálogo de los bugs más frecuentes al clonar, organizados por momento de aparición.

---

## 1. Versiones de caché heredadas del origen

**Síntoma:** El navegador sirve JS/CSS del proyecto origen aunque el deploy sea nuevo.

**Causa:** Los `?v=N` de los scripts del clon son idénticos a los del origen.
Si el usuario visitó el origen antes, el navegador tiene esos archivos en caché
con esas versiones y no los vuelve a pedir.

**Fix obligatorio al arrancar el clon:**
```bash
# Resetear TODAS las versiones a v=1 en el clon
# No heredar los números de versión del origen
grep -rn "?v=" ./nuevo-proyecto/ --include="*.html"
# Reemplazar todos por ?v=1 (o el número que corresponda al clon)
```

```javascript
// En sw.js — el CACHE_NAME debe incluir el nombre del proyecto
const CACHE_NAME = 'nuevo-proyecto-v1';  // nunca 'proyecto-origen-v4'
```

---

## 2. `config.js` compartido entre origen y clon

**Síntoma:** El clon guarda datos en el backend del proyecto origen.

**Causa:** El clon vive en la misma raíz que el origen y hereda su `config.js`
con las credenciales de Supabase/Firebase del proyecto origen.

**Diagnóstico:**
```bash
# ¿El clon referencia ../config.js de la raíz del origen?
grep -n "config.js" ./nuevo-proyecto/*.html
# Si apunta a "../config.js" y ese archivo es del origen → problema
```

**Fix:** Crear `config.js` local en la carpeta del clon, o mover el clon
a una raíz independiente.

---

## 3. Orden de carga de scripts roto

**Síntoma:** `TypeError: X is not a function` o `Cannot read properties of undefined`
en el primer render, aunque la función existe en el código.

**Causa:** Un script intenta usar una función o variable de otro script que
aún no se ha cargado, o intenta acceder al DOM antes de que exista.

**Diagnóstico:**
```javascript
// En consola del navegador: ¿en qué línea falla?
// ¿El script que falla depende de uno que está más abajo en el HTML?
```

**Fix:** Ver orden correcto en `references/stacks.md` → sección de tu stack.
Regla universal: librerías externas → config → utils → componentes → inicialización.

---

## 4. `autoIniciarSesion` / sesión no iniciada antes del primer registro

**Síntoma:** El clon funciona visualmente pero no graba puntos, actividad
ni progreso. Sin errores en consola.

**Causa:** El módulo clonado intenta registrar actividad antes de que la
sesión de usuario esté disponible. En el origen esto funcionaba porque
el módulo tenía `autoIniciarSesion()` al inicio; al clonar se olvidó.

**Diagnóstico:**
```bash
grep -n "autoIniciarSesion\|iniciarSesion\|getUser\|currentUser" ./nuevo-proyecto/*.js
# Si el módulo registra actividad sin verificar sesión primero → bug silencioso
```

**Fix:** Asegurarse de que la sesión se inicializa ANTES de cualquier llamada
que requiera `user.id`. Patrón correcto:

```javascript
// Al inicio de cada módulo que registre actividad:
async function init() {
  const user = await autoIniciarSesion();  // esperar aquí
  if (!user) return;                        // no continuar sin sesión
  // ahora sí: registrar actividad, cargar progreso, etc.
}
document.addEventListener('DOMContentLoaded', init);
```

---

## 5. Roles de usuario heredados del origen producen comportamiento incorrecto

**Síntoma:** Funcionalidad que debería estar disponible para todos los usuarios
solo aparece para algunos, o viceversa. Sin errores visibles.

**Causa:** El clon heredó checks de rol del origen (`if (user.role === 'moderador')`)
pero el nuevo proyecto tiene una estructura de roles diferente o ninguna.

**Diagnóstico:**
```bash
grep -rn "user\.role\|rol ===\|isAdmin\|isModerador\|isProfe" ./nuevo-proyecto/
```

**Fix:** Listar todos los checks de rol y decidir explícitamente cómo mapean
al nuevo proyecto antes del primer deploy.

---

## 6. Falso deploy — funciona en local pero no en Netlify

Causas más frecuentes:

| Causa | Síntoma | Fix |
|---|---|---|
| Ruta absoluta `/assets/img.png` | 404 en Netlify, ok en local | Usar ruta relativa `./assets/img.png` |
| `fetch('http://localhost:3000/api')` | Network error en producción | Usar variable de entorno para la URL base |
| SW activo del origen en localhost | El clon carga contenido del origen | Clear Site Data en DevTools antes de probar |
| `publish dir` incorrecto en Netlify | 404 en la raíz | Verificar que apunta a la carpeta correcta |
| `type="module"` sin HTTPS | Error CORS en file:// | Probar siempre con servidor local, no file:// |

---

## 7. Monolito que supera el umbral de tamaño seguro

**Síntoma:** Los str_replace empiezan a fallar con "OLD not found" aunque el
texto parece correcto. Ediciones que no producen cambio visible. Bugs que
aparecen sin razón tras una edición no relacionada.

**Umbral:** ~350KB / ~10.000 líneas de HTML+CSS+JS en un solo archivo.

**Fix — plan de split:**
```
Fase 1: Extraer CSS
  → Crear styles.css con todo el contenido de <style>
  → Reemplazar <style>...</style> por <link rel="stylesheet" href="styles.css?v=1">
  → Verificar que todo sigue funcionando

Fase 2: Extraer JS
  → Crear app.js con todo el contenido de <script>
  → Reemplazar <script>...</script> por <script src="app.js?v=1"></script>
  → Verificar JS con: node --check app.js

Fase 3: El HTML queda como orquestador limpio
  → Mucho más fácil de editar y verificar
```

---

## 8. Deuda del origen copiada al clon

**Síntoma:** El clon tiene el mismo bug que el origen desde el día uno.

**Causa:** Se clonó el origen sin resolver su deuda técnica conocida primero.

**Ejemplos reales:**
- SW registration en el archivo de deploy pero no en el de desarrollo
- Feature comentada con `// TODO: arreglar esto`
- Variable hardcodeada que "habría que poner en config"
- Función duplicada que "ya se limpiará"

**Regla:** Documentar la deuda del origen en `DEUDA_ORIGEN.md` al inicio
de la Fase 0. Resolver antes de clonar, no después.

---

## 9. SW del origen contamina el desarrollo del clon en localhost

**Síntoma:** El clon muestra contenido del proyecto origen aunque el código
es correcto. Ocurre cuando origen y clon comparten el mismo `localhost:PORT`.

**Fix inmediato:**
```
DevTools → Application → Service Workers → Unregister (en el origen)
DevTools → Application → Storage → Clear site data
Recargar la página del clon
```

**Fix permanente:** Cambiar el puerto de desarrollo del clon
(`netlify dev --port 8889` si el origen usa 8888), o usar un CACHE_NAME
con el nombre del proyecto que sea inequívocamente distinto.

---

## 10. Sin snapshot v0 → imposible volver atrás

**Síntoma:** Después de varias iteraciones, el clon tiene bugs imposibles
de aislar y no hay referencia del estado inicial limpio.

**Fix preventivo (Fase 3 del protocolo):**
```bash
# Antes de la primera iteración, siempre:
zip -r clon-v0-snapshot.zip ./nuevo-proyecto/
# Guardar fuera de la carpeta del proyecto
```

Si ya se iteró sin snapshot, crear uno del estado actual como referencia
mínima antes de continuar: `zip -r clon-estado-actual.zip ./nuevo-proyecto/`

---

## 11. Sin seed data — el clon parece roto pero solo está vacío

**Síntoma:** Las vistas del clon aparecen vacías, los componentes de lista no
renderizan nada, los contadores muestran 0. Parece un bug de conexión al backend
pero la conexión está bien.

**Causa:** El backend del clon tiene las tablas creadas pero sin datos.
El origen tenía meses de datos acumulados que hacían funcionar todas las vistas.

**Fix — crear `SEED_DATA.md` antes del primer test:**
```bash
cat > SEED_DATA.md << 'EOF'
## Usuarios de prueba
- rol admin:   test-admin@ejemplo.com  / pass-segura-admin
- rol usuario: test-user@ejemplo.com   / pass-segura-user

## Datos iniciales mínimos por tabla
- [tabla]: N registros mínimos para que [vista] muestre algo
- Insertar con: Supabase Table Editor / Firebase Console / script de seed

## Script de seed (si aplica)
# node seed.js  /  python3 seed.py
EOF
```

**Para Supabase — seed SQL mínimo:**
```sql
-- Ejecutar en Supabase SQL Editor
INSERT INTO usuarios (nombre, email, rol) VALUES
  ('Test Admin', 'test-admin@ejemplo.com', 'admin'),
  ('Test User',  'test-user@ejemplo.com',  'usuario');
```

---

## 12. Accesibilidad heredada del origen

**Cuándo aplica:** Siempre al clonar webs externas (arquetipo C). Opcional para proyectos propios.

**Checks mínimos:**
- [ ] Todas las `<img>` tienen `alt` (`alt=""` si son decorativas)
- [ ] Contraste texto/fondo ≥ 4.5:1 normal, ≥ 3:1 texto grande
- [ ] Botones e inputs tienen `aria-label` o texto visible
- [ ] Orden de headings `<h1>→<h2>→<h3>` sin saltos
- [ ] Colores no son el único canal de información
- [ ] Formularios con `<label>` asociado a cada `<input>`

```javascript
// Diagnóstico rápido en DevTools Console:
document.querySelectorAll('img:not([alt])').forEach(i => console.warn('Sin alt:', i.src));
document.querySelectorAll('button:not([aria-label])').forEach(b => {
  if (!b.textContent.trim()) console.warn('Botón sin label:', b);
});
```

> Los problemas de accesibilidad heredados son costosos de corregir a posteriori.
> Mejor detectarlos en Fase 2 que en producción.

---

## 13. Seguridad mínima — qué no debe estar en el cliente

**Síntoma:** Nada visible — es un riesgo silencioso.

**Lo que NUNCA debe estar en JS/HTML del cliente:**
```bash
# Detectar antes de cada deploy
grep -rni "private_key\|secret_key\|service_role\|SUPABASE_SERVICE\|FIREBASE_ADMIN" \
  . --include="*.js" --include="*.html"

grep -rni "localhost\|127\.0\.0\.1\|staging\.\|\.internal" \
  . --include="*.js" --include="*.html" | grep -v "//.*localhost"
```

**Qué SÍ puede estar en el cliente (son públicas por diseño):**
- `anon` key de Supabase
- `apiKey` de Firebase (config del SDK cliente)
- URL del proyecto Supabase / Firebase

**Qué NO puede estar en el cliente:**
- `service_role` de Supabase (acceso admin sin RLS)
- `private_key` de Firebase Admin SDK
- Lógica de precios, descuentos, reglas de acceso (debe vivir en el backend)

---

## 14. Gate — mapa de sustituciones sin completar

**Síntoma:** El script de contaminación reporta 0 coincidencias pero el clon
sigue guardando datos en el proyecto origen.

**Causa:** El mapa de sustituciones se ejecutó con los valores por defecto
("proyecto-origen", "proyecto-destino") sin ser personalizados, o se saltó el gate.

**Fix — verificación del mapa antes del script:**
```python
mapa = {
    'nombre_proyecto': ('NOMBRE_ORIGEN_REAL', 'NOMBRE_DESTINO_REAL'),
    'id_backend':      ('ID_ORIGEN_REAL',     'ID_DESTINO_REAL'),
    'cache_name':      ('CACHE_ORIGEN_REAL',  'CACHE_DESTINO_REAL'),
    'localStorage':    ('KEY_ORIGEN_REAL',    'KEY_DESTINO_REAL'),
}
# Regla: si algún valor "destino" contiene la palabra "destino" o "origen" literal
# → el mapa no está relleno → parar
placeholders = ['origen', 'destino', 'xxx', '___', 'nuevo']
sin_rellenar = [k for k,(o,d) in mapa.items()
                if any(p in d.lower() for p in placeholders) or d == o]
if sin_rellenar:
    raise ValueError(f"Mapa incompleto: {sin_rellenar}")
print("✅ Mapa validado — continuar")
```

---

## 15. Sin registro de cierre de sesión — contexto perdido

**Síntoma:** Al retomar el proyecto (o al abrir una nueva conversación con AI),
no se sabe en qué estado quedó el clon ni cuál es el próximo paso.

**Causa:** La sesión de trabajo se cerró sin documentar el estado.

**Plantilla de cierre de sesión (copiar en `DECISIONES.md` al terminar):**
```
## CIERRE DE SESIÓN — [fecha y hora]

### Estado actual
- ✅ Funciona: [lista]
- ❌ Pendiente: [lista]
- ⚠️ Bugs conocidos: [lista]

### Próximo paso (exacto, sin ambigüedad)
> [Descripción del primer paso de la siguiente sesión, suficientemente específica
>  para que alguien (o una AI) pueda retomarlo sin preguntar]

### Archivos modificados esta sesión
- [lista de archivos]

### Snapshot
- [ ] Creado: clon-pre-iter-[fecha].zip
- [ ] Ubicación: [ruta o descripción]
```

> Si trabajas con AI: pegar el contenido de DECISIONES.md al inicio de cada
> nueva conversación como contexto de arranque.

---

## Tabla de diagnóstico rápido

| Lo que ves | Primer check |
|---|---|
| Datos en el proyecto origen | `config.js` — credenciales sin cambiar |
| SW sirve contenido del origen | CACHE_NAME + Clear Site Data en localhost |
| Función "no definida" en consola | Orden de carga de scripts |
| Funciona visual pero no graba | `autoIniciarSesion` antes del primer registro |
| Comportamiento raro de roles | Checks `user.role` heredados del origen |
| OK en local, roto en Netlify | Rutas absolutas / fetch a localhost / publish dir |
| str_replace falla sin razón | Archivo >350KB o estado leído desde memoria |
| Bug del origen desde el día 1 | Deuda no resuelta antes de clonar |
| Clon muestra contenido del origen | SW del origen activo en localhost |
| Bug imposible de aislar | Sin snapshot v0 — crear uno ahora |
| Vistas vacías, contadores en 0 | Sin seed data — backend vacío |
| Accesibilidad rota sin razón aparente | Heredada del origen — ver §12 |
| Datos sensibles expuestos | Clave privada en el cliente — ver §13 |
| Script limpieza da 0 pero sigue contaminado | Mapa de sustituciones con valores por defecto — ver §14 |
| No sé dónde se quedó el proyecto | Sin registro de cierre de sesión — ver §15 |
