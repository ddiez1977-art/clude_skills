<!-- RECONSTRUIDO el 2026-10-31 a partir del texto íntegro generado en el chat "Skill genérica para clonar y revisar estructuras" (2026-06-11). No se encontró el fichero original. Si ves diferencias con tu versión instalada en su día, manda la tuya y prevalece. -->
# Referencia de Plataformas de Despliegue

Leer la sección de tu plataforma destino antes del primer deploy del clon.

---

## Netlify (drag-and-drop o CLI)

**Stack compatible:** cualquier estático (vanilla, React build, Vue build)

**Trampas al clonar:**

| Trampa | Causa | Fix |
|---|---|---|
| SW del origen sigue activo | CACHE_NAME idéntico al origen | Cambiar `CACHE_NAME` + `skipWaiting()` |
| Variables de entorno del origen | `netlify.toml` o panel copiados sin cambiar | Revisar panel Netlify → Site settings → Environment variables |
| Deploy con nombre de site del origen | El site en Netlify tiene el nombre del proyecto origen | Renombrar en Site settings → General → Site name |
| Redirects heredados | `_redirects` o `netlify.toml` con rutas del origen | Revisar y limpiar |
| Drag-and-drop cachea el ZIP viejo | Netlify puede servir la versión anterior | Forzar nuevo deploy o usar CLI |

**Checklist Netlify pre-deploy:**
- [ ] `netlify.toml` revisado (build command, publish dir, redirects)
- [ ] `_redirects` actualizado si existe
- [ ] Variables de entorno en panel: proyecto origen vs destino
- [ ] Site name cambiado (afecta al subdominio `.netlify.app`)
- [ ] SW: `CACHE_NAME` con nombre del nuevo proyecto

**Diferencias local vs Netlify (las más frecuentes):**
- Rutas relativas con `./` funcionan en servidor local pero no en Netlify CDN si el `publish dir` no apunta a la carpeta correcta
- `fetch('/api/...')` no existe en Netlify estático — necesita Netlify Functions o un backend externo
- `file://` nunca funciona para SW — siempre probar con `netlify dev` o servidor local real

**Deploy CLI:**
```bash
netlify login
netlify init          # vincular al proyecto destino (no al origen)
netlify deploy        # preview
netlify deploy --prod # producción
```

---

## Vercel

**Stack compatible:** vanilla, Next.js, React, Vue, cualquier estático

**Trampas al clonar:**

| Trampa | Causa | Fix |
|---|---|---|
| Proyecto apunta al repo del origen | Import desde GitHub del repo incorrecto | Crear nuevo proyecto en Vercel desde el repo destino |
| Variables de entorno heredadas | Copiadas del proyecto origen en el panel | Vercel Dashboard → Settings → Environment Variables |
| Edge config del origen | Si el origen usa Edge Config, no se hereda automáticamente | Crear nueva Edge Config para el destino |
| `vercel.json` con rewrites del origen | Rutas que no existen en el clon | Revisar y limpiar `vercel.json` |

**Checklist Vercel pre-deploy:**
- [ ] Nuevo proyecto creado (no fork del proyecto origen en Vercel)
- [ ] Variables de entorno configuradas para el destino
- [ ] `vercel.json` revisado si existe
- [ ] Domain/subdominio asignado al proyecto destino

**Deploy CLI:**
```bash
npm i -g vercel
vercel login
vercel          # preview (detecta framework automáticamente)
vercel --prod   # producción
```

---

## GitHub Pages

**Stack compatible:** vanilla estático, Jekyll, cualquier build con GitHub Actions

**Limitaciones importantes:**
- Solo sitios estáticos (no backend, no funciones serverless)
- SW funciona pero el scope está limitado al path del repositorio
- Si el repo es `usuario/repo`, la URL base es `usuario.github.io/repo/` — las rutas absolutas `/assets/...` se rompen

**Trampas al clonar:**

| Trampa | Causa | Fix |
|---|---|---|
| Rutas absolutas rotas | Base URL incluye el nombre del repo | Usar rutas relativas `./assets/` en lugar de `/assets/` |
| SW con scope incorrecto | `start_url` en manifest apunta a `/` en lugar de `/repo/` | Ajustar `start_url` y scope del SW |
| GitHub Actions del origen | Workflow copiado referencia secrets del origen | Actualizar secrets en Settings → Secrets del repo destino |
| CNAME heredado | Dominio custom del origen en el repo | Actualizar o eliminar `CNAME` |

**Checklist GitHub Pages:**
- [ ] Settings → Pages → Branch configurada correctamente
- [ ] Rutas relativas en todo el HTML/JS/CSS
- [ ] `manifest.json` con `start_url` y `scope` ajustados al path del repo
- [ ] SW: `CACHE_NAME` y rutas de precaché ajustadas al path base
- [ ] Secrets de GitHub Actions actualizados

---

## Firebase Hosting

**Stack compatible:** vanilla, React, Vue, cualquier estático + Cloud Functions

**Trampas al clonar:**

| Trampa | Causa | Fix |
|---|---|---|
| Deploy al proyecto Firebase del origen | `.firebaserc` apunta al project ID del origen | Editar `.firebaserc` con el project ID del destino |
| Rules de Firestore/Storage del origen | Se copian con el código pero no se despliegan solas | `firebase deploy --only firestore:rules` |
| Hosting headers del origen | `firebase.json` con headers/rewrites del origen | Revisar `firebase.json` |
| Caché agresiva de Firebase CDN | Firebase cachea agresivamente los estáticos | Cambiar nombre de archivo o añadir `Cache-Control: no-cache` en `firebase.json` |

**Checklist Firebase Hosting:**
- [ ] `.firebaserc` con project ID del destino
- [ ] `firebase.json` revisado (hosting, rewrites, headers)
- [ ] `firebase use <proyecto-destino>` antes de deploy
- [ ] Rules de Firestore/Storage actualizadas si cambia la estructura de datos

```bash
firebase login
firebase use <proyecto-destino>
firebase deploy --only hosting
```

---

## VPS / Nginx (servidor propio)

**Stack compatible:** cualquier cosa

**Trampas al clonar:**

| Trampa | Causa | Fix |
|---|---|---|
| Bloque server_name del origen | Config Nginx apunta al dominio del origen | Actualizar `server_name` en el bloque del clon |
| Mismo puerto que el origen | Conflicto si ambos proyectos viven en el mismo VPS | Asignar puerto distinto o usar subdominios |
| Certificado SSL del origen | Let's Encrypt/Certbot vinculado al dominio origen | `certbot --nginx -d nuevo-dominio.com` |
| `root` apunta a carpeta del origen | Nginx sirve los archivos del proyecto incorrecto | Actualizar `root` en la config del clon |
| PM2 con nombre del proceso origen | Si hay Node/backend, PM2 puede confundir procesos | `pm2 start app.js --name nuevo-proyecto` |

**Estructura mínima de config Nginx para un clon:**
```nginx
server {
    listen 80;
    server_name nuevo-proyecto.com www.nuevo-proyecto.com;
    root /var/www/nuevo-proyecto;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;  # para SPAs con client-side routing
    }

    # Caché para assets estáticos
    location ~* \.(js|css|png|jpg|svg|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Después de crear la config:
nginx -t                        # verificar sintaxis
systemctl reload nginx          # aplicar cambios
certbot --nginx -d nuevo-dominio.com  # SSL
```

---

## Referencias externas

Para plataformas no cubiertas aquí:
- **AWS Amplify**: https://docs.amplify.aws/guides/hosting/
- **Cloudflare Pages**: https://developers.cloudflare.com/pages/
- **Railway / Render**: https://docs.railway.app / https://render.com/docs
- **Deno Deploy**: https://deno.com/deploy/docs
