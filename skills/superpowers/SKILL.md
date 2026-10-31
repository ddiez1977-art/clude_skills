---
name: superpowers
description: "Metodología estructurada de desarrollo de software para agentes de IA. Actívala cuando vayas a desarrollar una feature compleja, refactorizar múltiples archivos, o cuando el usuario diga \"planifica esto\", \"hazlo paso a paso\", \"brainstorming\", \"TDD\", \"debug sistemático\", \"haz un plan antes de codear\", \"revisa mi código\", o ante cualquier tarea que requiera planificación antes de ejecutar. Previene el antipatrón de lanzarse a codear sin entender requisitos. Fases: Entender → Diseñar → Ejecutar (TDD: RED-GREEN-REFACTOR) → Revisar. Incluye debugging sistemático en 4 fases, planes de implementación en tareas de 2-5 minutos, code review por checklist, y brainstorming socrático. Compatible con proyectos vanilla JS, Firebase, Supabase y Netlify."
original_source: https://github.com/obra/superpowers
author: obra (Jesse Vincent) — adaptado por David para Claude.ai
license: MIT
---

# Superpowers

Metodología de desarrollo que transforma cómo un agente de IA aborda una tarea de código, evitando el antipatrón de "escribir código sin entender el problema".

## El contraste fundamental

**Sin Superpowers:**
```
Usuario: "Añade autenticación"
IA: *escribe 500 líneas de código inmediatamente*
```

**Con Superpowers:**
```
Usuario: "Añade autenticación"
IA: "Primero entendamos qué necesitas..."
   → Preguntas → Diseño → Plan → Ejecutar → Revisar
```

---

## Fase 1 — BRAINSTORMING (Entender)

Antes de tocar código, haz al menos 3 preguntas clave:

- ¿Qué problema concreto resuelve esta feature?
- ¿Qué restricciones hay? (rendimiento, compatibilidad, stack existente)
- ¿Cómo encaja con el código que ya existe?
- ¿Cuáles son los casos límite?

Presenta el diseño entendido en secciones cortas y pide confirmación antes de continuar.

**Gatillo:** "planifica", "brainstorming", "¿qué hacemos?", "ayúdame a pensar", "antes de codear"

---

## Fase 2 — WRITING-PLANS (Diseñar)

Divide el trabajo en tareas de **2-5 minutos** cada una. Cada tarea debe tener:

```
## Tarea N: [Nombre concreto]
- Archivo(s) a modificar: [rutas exactas]
- Qué hace: [descripción en 1 frase]
- Criterio de éxito: [cómo verificamos que funciona]
- Tests primero: [qué test escribimos antes]
```

Reglas del plan:
- Una sola responsabilidad por tarea
- Testeable de forma independiente
- Sin "y también…" dentro de una tarea
- El plan se muestra completo antes de ejecutar; el usuario aprueba

**Gatillo:** "haz un plan", "divide en pasos", "¿por dónde empezamos?", "escribe el plan"

---

## Fase 3 — TEST-DRIVEN DEVELOPMENT (Ejecutar)

Para cada tarea del plan, ciclo obligatorio **RED → GREEN → REFACTOR**:

```
RED:     Escribe el test. Verifica que falla.
GREEN:   Escribe el mínimo código para que pase.
REFACTOR: Limpia sin romper el test.
COMMIT:  Solo cuando verde y limpio.
```

### Anti-patrones prohibidos
- Escribir código antes del test
- Saltarse REFACTOR "para ir más rápido"
- Hacer pasar el test con código falso (hardcoded return)
- Marcar como hecho sin haber ejecutado el test

**Gatillo:** "TDD", "test primero", "test-driven", "escribe el test antes"

---

## Fase 4 — SYSTEMATIC-DEBUGGING (Debug)

Proceso en 4 fases para cualquier bug:

```
1. REPRODUCIR    → Consigue un caso mínimo que falla siempre
2. AISLAR        → Descarta variables; encuentra la línea exacta
3. ROOT CAUSE    → ¿Por qué falla? No qué falla
4. VERIFICAR     → El fix elimina la causa, no el síntoma
```

### Técnicas incluidas

**Root-cause tracing:**
- Empieza por los logs más recientes
- Sigue el flujo de datos hacia atrás desde el error
- Pregunta: "¿Qué cambió justo antes de que apareciera este bug?"

**Defense-in-depth:**
- Añade validaciones en múltiples capas (input, función, output)
- No asumas que el dato llega bien formado

**Condition-based waiting (async):**
- Nunca uses `setTimeout` para esperar async; usa condiciones explícitas
- Verifica estado real, no tiempo transcurrido

**Gatillo:** "debug", "no funciona", "error extraño", "por qué falla", "debugging sistemático"

---

## Fase 5 — CODE REVIEW (Revisar)

Checklist antes de declarar una tarea completa:

```
□ ¿El código hace lo que dice la especificación?
□ ¿Los tests cubren los casos límite?
□ ¿Hay código duplicado que se puede extraer?
□ ¿Los nombres de variables/funciones son claros?
□ ¿Hay side effects inesperados?
□ ¿Se pueden romper otras partes del sistema?
```

**Dos pasadas obligatorias:**
1. Cumplimiento de spec (¿hace lo pedido?)
2. Calidad de código (¿está bien escrito?)

**Gatillo:** "revisa mi código", "code review", "¿está bien esto?", "antes de hacer merge"

---

## Fase 6 — USING-GIT-WORKTREES (Aislar workspace)

Antes de ejecutar un plan aprobado, crea un workspace aislado en una rama nueva para no contaminar la rama principal.

```bash
# Crear worktree en .worktrees/ (ignorado por git)
git worktree add .worktrees/<feature-name> -b <branch-name>
cd .worktrees/<feature-name>

# Al terminar, volver a la raíz
cd ../..
```

**Reglas:**
- Pide consentimiento antes de crear el worktree: *"¿Quieres que cree un worktree aislado para proteger tu rama actual?"*
- Verifica que `.worktrees/` está en `.gitignore` antes de crearlo; si no, añádelo y haz commit
- Si ya estás en un worktree enlazado, salta al paso de ejecución directamente
- No confundas worktrees con submódulos (comprueba con `git rev-parse --show-superproject-working-tree`)

**Gatillo:** "crea una rama", "trabajo en paralelo", "no toques main", "aísla los cambios", "worktree"

---

## Fase 7 — VERIFICATION-BEFORE-COMPLETION (Verificar antes de cerrar)

Antes de declarar cualquier tarea como hecha, verifica con evidencia real:

```
□ ¿El test pasa? (ejecútalo, no lo asumas)
□ ¿El comportamiento en producción/navegador es correcto?
□ ¿No hay regresiones en otras partes del sistema?
□ ¿Los logs no muestran errores silenciosos?
```

**Regla de oro:** "Done" significa verificado con evidencia, no "creo que funciona".

**Gatillo:** "¿está hecho?", "¿ya funciona?", "verifica que esté bien", "comprueba antes de cerrar"

---

## Fase 8 — FINISHING-A-DEVELOPMENT-BRANCH (Cerrar rama)

Al completar todas las tareas del plan, presenta opciones de cierre:

```
Opciones disponibles:
1. Merge directo a main
2. Crear Pull Request para revisión
3. Mantener la rama abierta (más trabajo pendiente)
4. Descartar cambios (si no sirven)
```

**Proceso de cierre:**
1. Verifica que todos los tests pasan
2. Limpia el worktree: `git worktree remove .worktrees/<feature-name>`
3. Ejecuta solo la opción elegida por el usuario
4. Solo elimina worktrees creados dentro de `.worktrees/` — nunca toques worktrees externos

**Nota para proyectos de David (Netlify):** El cierre de rama incluye siempre verificar ZIP limpio + drag-and-drop deploy antes de hacer merge.

**Gatillo:** "terminé", "cierra la rama", "haz merge", "crea el PR", "¿qué hago con la rama?"

---

## Fase 9 — RECEIVING-CODE-REVIEW (Responder a feedback)

Cuando recibes feedback de un code review:

```
1. LEE todo el feedback antes de responder
2. CATEGORIZA cada comentario:
   - Bloqueante (debe corregirse antes de merge)
   - Sugerencia (mejora opcional)
   - Pregunta (necesita aclaración)
3. RESPONDE a cada punto explícitamente
4. NO defiendas decisiones sin explicación; si discrepas, argumenta con datos
5. VERIFICA que los cambios solicitados están implementados antes de pedir re-review
```

**Gatillo:** "me han hecho review", "tengo comentarios en el PR", "el reviewer dice que...", "responde al feedback"

---

## Flujo completo integrado

```
[USUARIO DA TAREA]
       ↓
  BRAINSTORMING
  (preguntas → diseño → validar)
       ↓
  WRITING-PLANS
  (tareas 2-5 min → aprobar plan)
       ↓
  USING-GIT-WORKTREES
  (crear rama aislada con consentimiento)
       ↓
  Para cada tarea:
    TDD: RED → GREEN → REFACTOR
    VERIFICATION-BEFORE-COMPLETION
    CODE REVIEW: spec + calidad
       ↓
  FINISHING-A-DEVELOPMENT-BRANCH
  (merge / PR / descartar)
       ↓
  DONE ✓
```

Si aparece un bug → SYSTEMATIC-DEBUGGING, luego volver al flujo.
Si recibes feedback externo → RECEIVING-CODE-REVIEW, luego iterar.

---

## Principios

1. **Diseña antes de codear** — La velocidad viene de cometer menos errores
2. **Tareas pequeñas** — Más fácil de verificar, debugar y revertir
3. **Tests primero siempre** — La confianza viene de evidencia, no de suposición
4. **Evidencia sobre asunción** — No asumas que funciona; verifica
5. **Revisa con frecuencia** — Detecta problemas pronto

---

## Adaptaciones para proyectos de David

- **Monolitos HTML (SITyL, JoGaSan, Orange Spark):** Las "tareas" son bloques de funcionalidad dentro del monolito. Los "tests" son verificaciones manuales en el navegador + `node -e "eval(...)"` para JS inline. Siempre ejecutar `debug-html-monolito` antes de declarar done.
- **Firebase/Supabase:** El ROOT CAUSE en debugging incluye revisar reglas de seguridad y listeners duplicados. Ver skill `auditoria-consistencia-puntos` para lógica de puntos.
- **Netlify deploy:** La tarea de deploy es siempre la última. Verificar antes: ZIP limpio, sin `{{` dobles en arrays, `</script>` presente.
