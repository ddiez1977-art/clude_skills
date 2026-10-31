---
name: svg-angulos-poligono
description: >
  Reglas exactas y código validado para dibujar arcos de ángulos interiores
  en polígonos SVG para JoGaSan Academy. Úsala SIEMPRE que vayas a dibujar
  un ángulo interior en un polígono SVG: cuando hagas figuras geométricas con
  ángulos marcados (triángulos, cuadriláteros, polígonos regulares/irregulares),
  cuando el usuario pida "marca los ángulos", "añade el símbolo de ángulo",
  "pon los grados dentro", o al crear SVGs de geometría para los módulos de
  la academia. Sin esta skill los arcos salen al revés o fuera de la figura.
---

# SVG — Ángulos Interiores en Polígonos

## El problema

Dibujar un arco de ángulo interior en SVG con `<path d="M P1 A r r 0 0 sweep P2"/>` 
requiere calcular correctamente:
1. Los puntos P1 y P2 sobre los lados del ángulo
2. El orden P1→P2 (determina hacia dónde curva el arco)
3. El sweep-flag (0 = antihorario, 1 = horario)

Si P1/P2 están en el orden incorrecto **el arco sale al revés** (hacia el exterior).

---

## Algoritmo validado (probado en producción)

Para cualquier vértice **V** con adyacentes **Prev** y **Next**, en un polígono
dibujado en **orden antihorario**:

```
1. Calcula el vector unitario hacia Next:
   u_next = (Next - V) / |Next - V|

2. Calcula el vector unitario hacia Prev:
   u_prev = (Prev - V) / |Prev - V|

3. P1 = V + r × u_next      ← punto de inicio del arco (lado hacia Next)
   P2 = V + r × u_prev      ← punto de fin del arco (lado hacia Prev)

4. Path: M P1 A r r 0 0 0 P2   ← sweep-flag SIEMPRE 0 para polígono antihorario
```

**Clave:** P1 va en la dirección de Next, P2 en la dirección de Prev. Orden fijo. Sweep fijo (0).

---

## Radio recomendado por ángulo

| Ángulo | Radio (r) | Motivo |
|--------|-----------|--------|
| < 45°  | 14px | Ángulo muy agudo, arco pequeño para no salirse |
| 45–90° | 18px | Ángulo recto o agudo normal |
| 90–135°| 22px | Ángulo obtuso estándar |
| > 135° | 26px | Ángulo muy obtuso, necesita más radio para verse |

---

## Posición del label de grados

El label va **entre el arco y el centroide** del polígono, no sobre el lado.

```
label_pos = V + (r + 12) × normalize(u_next + u_prev)
```

Es decir: en la dirección de la bisectriz del ángulo, un poco más adentro que el arco.

En SVG: `text-anchor="middle" dominant-baseline="central"` sobre ese punto.

---

## Ejemplo completo — hexágono regular (120°)

Centrado en (170,150), r_poligono=95. Vértices en antihorario:
```
V0=(265,150)  V1=(218,68)  V2=(122,68)
V3=(75,150)   V4=(122,232) V5=(218,232)
```

### V0 = (265,150), Prev=V5=(218,232), Next=V1=(218,68)

```
u_next = (218-265, 68-150) / 94.6 = (-0.497, -0.867)
u_prev = (218-265, 232-150) / 94.6 = (-0.497, +0.867)

P1 = (265 + 20×(-0.497),  150 + 20×(-0.867)) = (255, 133)   ← dir Next
P2 = (265 + 20×(-0.497),  150 + 20×(+0.867)) = (255, 167)   ← dir Prev

bisectriz = u_next + u_prev = (-0.994, 0) → normalizado = (-1, 0)
label = (265 + 32×(-1), 150 + 32×0) = (233, 150)
```

```svg
<path d="M 255,133 A 20 20 0 0 0 255,167" fill="none" stroke="#4fc3f7" stroke-width="1.6"/>
<text x="233" y="150" text-anchor="middle" dominant-baseline="central"
      font-family="var(--font-sans)" font-size="11" font-weight="500" fill="#4fc3f7">120°</text>
```

### Todos los vértices del hexágono (r=20)

| Vértice | P1 (dir Next) | P2 (dir Prev) | Label |
|---------|--------------|--------------|-------|
| V0=(265,150) | (255,133) | (255,167) | (240,150) |
| V1=(218,68)  | (198,68)  | (228,85)  | (214,95)  |
| V2=(122,68)  | (112,85)  | (142,68)  | (126,95)  |
| V3=(75,150)  | (85,167)  | (85,133)  | (100,150) |
| V4=(122,232) | (142,232) | (112,215) | (126,212) |
| V5=(218,232) | (228,215) | (198,232) | (214,212) |

Todos con `sweep=0`. Resultado: arcos perfectamente hacia el interior en todos los vértices.

---

## Regla rápida para polígono HORARIO

Si el polígono está definido en orden horario (ej. vértices de arriba a la derecha
en sentido horario), invierte el sweep a **1** y mantén el mismo orden P1/P2.

---

## Checklist antes de renderizar

- [ ] ¿Los vértices están en orden antihorario? → sweep=0
- [ ] ¿P1 apunta hacia Next y P2 hacia Prev? (no al revés)
- [ ] ¿El radio es proporcional al tamaño del ángulo? (ver tabla)
- [ ] ¿El label está en la bisectriz interior, no sobre el lado?
- [ ] ¿`fill="none"` en el path del arco?
- [ ] ¿El arco tiene `large-arc-flag=0`? (siempre 0 para ángulos < 180°)
