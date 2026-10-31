# Bugs críticos — Netlify + Firebase/Auth en producción

Estos bugs son silenciosos: la app parece desplegarse bien pero falla en producción sin error obvio.
Verificar esta lista ANTES de dar por terminado cualquier deploy en Netlify con Firebase o Google Auth.

---

## 🔴 CRÍTICO — Firebase init async → spinner infinito

**Síntoma:** La app carga (HTML visible), el login se muestra, pero al hacer submit no pasa nada. Spinner infinito o botón que no responde. Sin errores en consola.

**Causa:** La inicialización de Firebase se hace con `fetch('/api/config')` u otra llamada async que devuelve la apiKey. Firebase se inicializa más tarde, pero el código que usa `auth` ya ejecutó y encontró un objeto placeholder.

**Regla absoluta:** La `apiKey` de Firebase va **directa en el HTML**, de forma síncrona. Nunca con `fetch`, nunca fragmentada en arrays, nunca cargada desde una Netlify Function.

```javascript
// MAL — async fetch de config:
const config = await fetch('/api/config').then(r => r.json());
firebase.initializeApp(config);

// BIEN — directa y síncrona:
firebase.initializeApp({
  apiKey: "AIza...",
  authDomain: "mi-proyecto.firebaseapp.com",
  projectId: "mi-proyecto"
});
```

> La apiKey de Firebase es pública por diseño (es una clave de proyecto, no un secret). No hay riesgo de seguridad en ponerla en el HTML. Las reglas de Firestore/Storage son las que protegen los datos.

---

## 🔴 CRÍTICO — COOP header bloquea Google Auth popup

**Síntoma:** `signInWithPopup()` falla silenciosamente. La ventana popup de Google abre brevemente y se cierra sin completar el login. A veces aparece `Cross-Origin-Opener-Policy` en el error de consola.

**Causa:** Netlify añade por defecto (o el desarrollador añade para seguridad) el header `Cross-Origin-Opener-Policy: same-origin`, que bloquea la comunicación entre la ventana popup de Google y la ventana principal.

**Fix obligatorio en `netlify.toml`:**
```toml
[[headers]]
  for = "/*"
  [headers.values]
    Cross-Origin-Opener-Policy = "unsafe-none"
```

**Nota:** Este header solo afecta al popup de Google Auth. No elimina otras protecciones de seguridad del navegador.

---

## 🔴 CRÍTICO — ZIP con carpeta raíz extra → 404 silencioso en Netlify

**Síntoma:** El deploy aparece como exitoso en Netlify pero la app devuelve 404 al abrir la URL. O bien carga algo pero sin CSS/JS (rutas rotas).

**Causa:** El ZIP contiene una carpeta raíz extra. Netlify espera que `index.html` y `netlify.toml` estén en la **raíz** del ZIP. Si el ZIP tiene la estructura `mi-proyecto/index.html` en vez de `index.html`, Netlify no encuentra la raíz.

**Verificación antes de subir:**
```bash
# Ver estructura del ZIP antes de subir:
unzip -l mi-app.zip | head -20
# La primera línea de contenido debe ser algo como:
#   index.html
#   netlify.toml
# NO debe ser:
#   mi-app/index.html
#   mi-app/netlify.toml
```

**Fix:** Comprimir desde dentro de la carpeta del proyecto, no desde fuera:
```bash
# MAL — comprime con carpeta raíz extra:
zip -r mi-app.zip mi-proyecto/

# BIEN — comprimir desde dentro:
cd mi-proyecto && zip -r ../mi-app.zip . && cd ..
```

---

## 🟠 ALTO — Firebase Storage CORS irresoluble en Netlify

**Síntoma:** Las subidas a Firebase Storage funcionan en local pero fallan en producción con error CORS. Las descargas también pueden fallar.

**Causa:** Firebase Storage requiere configuración CORS en el bucket (`gsutil cors set ...`), que solo es posible con Google Cloud SDK o desde la consola de GCP. En Netlify (frontend puro, sin backend propio), no hay forma de resolver esto sin crear una Netlify Function que haga de proxy.

**Alternativa definitiva para archivos pequeños (≤700KB):**
Guardar los archivos como base64 directamente en Firestore:

```javascript
// Subir archivo como base64 a Firestore:
const reader = new FileReader();
reader.onload = async (e) => {
  const base64 = e.target.result; // data:image/jpeg;base64,...
  await db.collection('archivos').doc(id).set({
    nombre: archivo.name,
    tipo: archivo.type,
    datos: base64,
    tamaño: archivo.size,
    fecha: firebase.firestore.FieldValue.serverTimestamp()
  });
};
reader.readAsDataURL(archivo);
```

> Para archivos grandes (>700KB) o muchos archivos, evaluar AWS S3, Cloudinary, o Supabase Storage (que tiene mejor gestión de CORS).

---

## 🟡 MEDIO — "Exposed secrets detected" en Netlify al subir Firebase config

**Síntoma:** Netlify muestra un modal "Exposed secrets detected" durante el deploy con la apiKey de Firebase.

**Acción:** Hacer click en **"Allow"** (Permitir). No es un error. La apiKey de Firebase es una clave pública de proyecto, no un secret de servidor. Netlify la detecta por su formato pero no supone riesgo.

Solo hay que hacerlo **una vez** por deploy/proyecto. Netlify recuerda la decisión.

**Qué SÍ son secrets** (y deben ir como env vars de Netlify, nunca en HTML):
- Claves de API de terceros con acceso de escritura (Tavily, Groq, SendGrid, etc.)
- Tokens de autenticación de backend
- Claves privadas de Supabase service role

---

## Checklist pre-deploy Netlify + Firebase

```
□ apiKey de Firebase directa en HTML (no fetch, no fragmentada)
□ netlify.toml con Cross-Origin-Opener-Policy = "unsafe-none" (si usas Google Auth)
□ ZIP comprimido desde dentro de la carpeta (sin carpeta raíz extra)
□ Variables de entorno de terceros configuradas en Netlify UI (no en HTML)
□ Dominio de Netlify añadido en Firebase Console → Authentication → Authorized domains
□ Si usas archivos: Firestore base64 para ≤700KB; evaluar alternativa para archivos grandes
```
