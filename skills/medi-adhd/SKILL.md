---
name: medi-adhd
description: "Agente educativo hiperespecializado en transformar contenido del portal Academia (teoría, quizzes, actividades, exámenes, retos pro) en experiencias ultra-atractivas para niños de 7-10 años con TDAH e impulsividad. Úsala cuando el usuario diga \"adapta esto para niños con TDAH\", \"versión Medi-ADHD\", \"más dinámico para impulsivos\", \"gamifica contenido infantil\", \"estilo Medi\", \"/adhd\", \"/medi\", o trabaje en módulos de Academia Portal de Repaso para niños 7-10. También con \"atención corta\", \"dopamina\", \"micro-recompensas\", \"niños impulsivos\", o al convertir teoría/quiz tradicional en formato jugable con Medi. Aplica neurociencia TDAH: dopamina cada 2-3 min, cambio de formato cada 4 min, máximo 12-15 palabras por frase, lenguaje de niño de 8 años emocionado (¡CRACK!, ¡BRUTAL!, ¡BOOM!), formatos jugables (Memory, Caza-topos, Carrera), recompensas escalonadas y Medi como copiloto. NO usar para adolescentes 12+, adultos, ni docs técnicas."
---

# Skill: Medi-ADHD
**Versión:** 2.1.0 · **Atajo:** `/adhd` o `/medi`

---

## Principios Fundamentales (NUNCA ROMPER)

### Neurociencia del TDAH
- **Dopamina cada 2-3 min** → recompensa visible (confeti, animación, puntos, medalla)
- **Feedback inmediato**: nunca >5 segundos para recibir respuesta
- **Máximo 4 min** en la misma actividad → rotar formatos
- **Máximo 12-15 palabras por frase** · máximo 3-4 líneas por pantalla
- **Una idea a la vez**
- **Movimiento físico**: gesto o acción corporal en cada chunk

### Tono: niño de 8 años muy emocionado
- **SÍ**: ¡CRACK!, ¡BESTIA!, ¡FLIPANTE!, ¡BRUTAL!, ¡ZAS!, ¡BOOM!, ¡TOMA YA!, ¡PASADAAA!
- **NO**: "Observa", "Analiza", "Reflexiona", "A continuación", "Completa el siguiente ejercicio"
- Muchos emojis · MAYÚSCULAS para palabras clave · Onomatopeyas

---

## Estructura Obligatoria de Chunk (5 pasos SIEMPRE)

```
1. GANCHO (3 seg)           — emoji grande + frase impactante
2. CONTENIDO PRINCIPAL      — imagen sugerida + texto cortísimo (3-4 líneas)
3. ACTIVACIÓN MULTISENSORIAL — 🔊 leer en voz alta / ✏️ dibujar o escribir / 🤸 gesto
4. BOTÓN DE PROGRESO        — "¡Ya lo tengo! →" (grande y colorido)
5. RECOMPENSA               — confeti / Medi bailando / +10 pts / medalla / sonido
```

> **Los 3 canales multisensoriales son SIEMPRE obligatorios.** Lo que varía chunk a chunk
> es el CONTENIDO de cada canal. Nunca repetir el mismo gesto dos chunks seguidos.

---

## 🆕 Formato ADHD-Carrusel (v194) — para módulos de 3º JoGaSan

El formato legacy de chunks acumulativos (aparecen uno debajo del otro) está superado.
El nuevo estándar es el **carrusel navegable** implementado en mat3 M13.

### Patrón de implementación HTML/JS

```html
<!-- Dots de navegación (encima del carrusel) -->
<div class="chunk-dots">
  <button class="chunk-dot active" id="dot-1" onclick="chunkGoto(1)">🌍 Nombre chunk 1</button>
  <button class="chunk-dot" id="dot-2" onclick="chunkGoto(2)">🌅 Nombre chunk 2</button>
  <!-- ... hasta N chunks -->
</div>

<!-- Slides -->
<div class="chunk-slide active" id="chunk-slide-1">
  <div class="adhd-chunk"> <!-- header + body del chunk --> </div>
  <div class="chunk-nav-btns">
    <button class="chunk-btn-prev" id="btn-prev-1" onclick="chunkPrev()" disabled>← Anterior</button>
    <button class="chunk-btn-next" onclick="chunkNext()">¡Ya lo tengo! → (+10 ⭐)</button>
  </div>
  <div class="chunk-contador">Paso 1 de N</div>
</div>
<!-- Slide N (último): botón "¡LO TENGO TODO! 🏆" que llama chunkDone() -->
```

```javascript
var _chunkActual = 1, _chunksDone = {}, TOTAL_CHUNKS = 5;

function chunkGoto(n) {
  // oculta slide actual → actualiza dot → muestra slide destino → scroll top
}
function chunkNext() {
  _chunksDone[_chunkActual] = true;
  // marca dot como done · ptsPop(10) · chunkGoto(siguiente)
}
function chunkPrev() { if (_chunkActual > 1) chunkGoto(_chunkActual - 1); }
function chunkDone() { /* último chunk → mostrarVictoria() */ }
```

```css
.chunk-slide { display:none; animation:slideIn .25s ease; }
.chunk-slide.active { display:block; }
@keyframes slideIn { from{opacity:0;transform:translateX(20px)} to{opacity:1;transform:translateX(0)} }
.chunk-dot.active { background:#059669; color:#fff; }
.chunk-dot.done   { background:#D1FAE5; color:#065F46; }
```

### Ventajas sobre el patrón acumulativo
- El alumno puede **volver a un chunk anterior** si no entendió
- El indicador de dots muestra el **progreso real** (verde = completado)
- La animación slideIn da **feedback visual** de avance
- El botón "← Anterior" **nunca desaparece** (siempre accesible)
- El número "Paso N de M" ancla cognitivamente el progreso

### Cuándo usar cada formato
| Formato | Cuándo |
|---|---|
| **ADHD-Carrusel** | Módulos nuevos de 3º con 4-6 chunks. Estándar desde v192. |
| **Aprende-chunks acumulativos** | Solo si el módulo ya existe y refactorizar es costoso |
| **Clásico con gate** | Academias de 6º donde la lectura es obligatoria antes del quiz |

---

## Activación Multisensorial — banco de variantes

Para que los 3 canales NO se repitan entre chunks:

### Canal 🔊 (auditivo)
- "Di en voz alta: [frase exacta]"
- "Repite 3 veces: [concepto]"
- "Deletrea en voz alta: [palabra]"
- "Cuenta en voz alta del [N] al [M]"

### Canal ✏️ (escritura/dibujo)
- "Dibuja: [objeto concreto]"
- "Escribe en tu cuaderno: [frase o fórmula]"
- "Completa en papel: [esquema]"
- "Copia la tabla"

### Canal 🤸 (movimiento)
- "Gesto: [movimiento concreto]"
- "Señala con el dedo: [dirección]"
- "Da [N] palmadas cuando [condición]"
- "Levántate y [acción física sencilla]"

> Rotar sistemáticamente para que cada chunk tenga variante distinta en los 3 canales.

---

## Contexto AM/PM en actividades de reloj (v189+)

Cuando el chunk incluye lectura de relojes analógicos, **añadir siempre contexto AM/PM** 
para eliminar la ambigüedad (Las 3 = 03:00 o 15:00):

```javascript
// En el banco de preguntas del chunk:
{ hora: 3, min: 0, texto: 'Las 3 en punto',
  emoji: '🌙', momento: 'de la madrugada' }  // ← siempre con emoji + momento

// En la función que pinta la pregunta:
var ctxEl = document.getElementById('caza-contexto');
if (ctxEl && q.emoji) {
  ctxEl.textContent = q.emoji + ' ' + q.momento;  // ← mostrar ANTES de las opciones
  ctxEl.style.display = 'block';
}
```

En la teoría, mostrar **las 4 franjas del día** (no 3):
- 🌌 0–5 Madrugada *(dormimos)*
- ☀️ 6–11 Mañana *(cole)*
- 🌤️ 12–17 Tarde *(merienda)*
- 🌙 18–23 Noche *(cenar·dormir)*

La actividad cotidiana en cursiva ancla el número abstracto a la experiencia del niño.

---

## Sistema de Recompensas

| Frecuencia | Recompensa | Trigger |
|---|---|---|
| Cada chunk completado | +10 pts + dot verde | micro-dopamina |
| Cada 2-3 aciertos en quiz | Explosión puntos + Medi | racha corta |
| Cada 5 aciertos | Medalla pequeña + sonido | racha media |
| Final de módulo | Medalla grande + diploma + confeti | completado |
| Racha especial | "¡Llevas X seguidas! ¡Eres una BESTIA!" | motivación verbal |

### Frases de acierto (rotar en cada feedback):
¡TOMA YA! 💥 / ¡Eres una BESTIA! 🔥 / ¡CRACK TOTAL! ⭐ / ¡BRUTAL! 💪 / ¡ZAS! 🎯 / ¡FLIPANTE! 🌟

### Frases de fallo (siempre motivadoras):
¡Tranqui! Vamos otra vez 💪 / ¡Casi casi! La próxima 🎯 / ¡Ooops! Probamos de nuevo 🔥

---

## Integración técnica con JoGaSan Portal

### Registro de progreso en chunks
```javascript
// Al completar la teoría del carrusel (en mostrarVictoria):
try { AcademiaLogros.registrarMiniQuiz('nueva3_modulo1_teoria', 5, 5); } catch(e) {}

// En cada actividad con preguntas (3 PARAMS SIEMPRE):
try { AcademiaLogros.registrarMiniQuiz('nueva3_modulo1_actA', correctas, total); } catch(e) {}
//                                                              ↑ aciertos   ↑ total preguntas
// SIN el tercer param → mejor_pct = 0 siempre (bug frecuente)
```

### Post-quiz → siguiente paso
```javascript
// Configurar botón "siguiente" al terminar el quiz:
QuizEngine.start('nueva3_modulo1', questions, {
  nextHref: 'superexamen-pro.html',
  nextLabel: '⚡ Superexamen PRO →'
});
// Aparece un botón dorado adicional junto a "Volver"
```

### Puntos y confeti
```javascript
function ptsPop(n) {
  if (window.Motivacion && Motivacion.sumarPuntos) Motivacion.sumarPuntos(n);
}
function lanzarConfeti() {
  if (window.Mascota && Mascota.confeti) Mascota.confeti();
}
```

---

## Formatos de Quiz Preferidos (orden de prioridad)

1. **Chips de opción múltiple con animación ok/ko** — estándar JoGaSan
2. **Reloj analógico + 4 opciones** — para tiempo/horas
3. **Display digital + 4 opciones** — para conversión 24h
4. **Verdadero/Falso** — para conceptos binarios
5. **Completar el texto** — cuando el contexto requiere escritura

Todos deben tener:
- Feedback inmediato visual (color verde/rojo)
- Texto de reacción rotatorio
- Desbloqueo automático de la siguiente pregunta tras 1.2-1.4s

---

## Checklist de calidad antes de entregar

- [ ] Gancho en los primeros 3 segundos de cada chunk
- [ ] Estructura 5 pasos respetada
- [ ] Frases ≤ 12-15 palabras · ≤ 3-4 líneas por pantalla
- [ ] 3 canales multisensoriales en cada chunk (contenido variado)
- [ ] Sin repetir el mismo gesto o actividad dos chunks seguidos
- [ ] Lenguaje de niño de 8 años emocionado
- [ ] Formato carrusel si hay ≥3 chunks (no acumulativo)
- [ ] Recompensa sugerida en cada chunk (+10 pts, confeti, etc.)
- [ ] Medi interviene ≥2 veces por módulo
- [ ] Victoria épica al completar todos los chunks
- [ ] registrarMiniQuiz con 3 parámetros (clave, correctas, total)
- [ ] Contexto AM/PM si hay actividades de reloj analógico
- [ ] Sin monotonía de formatos en el quiz

---

## Versión y cambios

**v2.1.0 — junio 2026:**
- ✅ Nuevo patrón **ADHD-Carrusel** con slides navegables (dots + prev/next)
- ✅ Banco de variantes de activación multisensorial para evitar repetición
- ✅ Contexto AM/PM en actividades de reloj (4 franjas del día)
- ✅ Integración técnica actualizada: `registrarMiniQuiz` 3 params, `QuizEngine.start` cfg.nextHref
- ✅ Frases de feedback rotatorias codificadas

**v2.0.0 — mayo 2026:** Estructura 5 pasos · activación multisensorial · formato salida estandarizado
