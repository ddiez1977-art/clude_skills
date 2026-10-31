---
name: artifact-react-components
description: >
  Construye artifacts React interactivos en claude.ai con componentes ricos (tablas,
  gráficas, formularios, dashboards, KPIs, timelines, modales) usando las librerías
  ya disponibles en el sandbox: recharts, lucide-react, shadcn/ui, lodash, d3, papaparse.
  Úsala SIEMPRE que necesites un prototipo visual interactivo dentro del chat —
  un mockup para mostrar a un cliente, un dashboard de métricas para una reunión,
  un formulario de captura de datos, una tabla filtrable, un comparador de opciones,
  un wizard de pasos — sin salir a Netlify ni necesitar backend.
  Actívala con: "muéstrame cómo quedaría", "prototipo rápido", "mockup interactivo",
  "dashboard para la reunión", "tabla con filtros", "artifact con gráfica",
  "visualiza esto en el chat", "artifact React", "componente con shadcn",
  "cómo quedaría la pantalla", "demo visual", "simula la interfaz".
  NO usar para apps reales con backend/Firebase/Supabase → esas van a Netlify (stack vanilla).
  NO usar para documentos descargables → usar skill docx/pdf/pptx.
---

# Artifacts React Interactivos — Skill

Builds artifacts React que viven dentro del chat de claude.ai. Sin build step,
sin node_modules, sin deploy: el sandbox los ejecuta directamente.

**Cuándo es la herramienta correcta:**

| Necesitas | Herramienta |
|-----------|-------------|
| Mostrar prototipo / mockup en el chat | ✅ Esta skill (artifact React) |
| App real en URL propia con usuarios | Vanilla HTML + Netlify |
| Dashboard con datos en vivo / Firebase | Vanilla HTML + Netlify + Firebase |
| Documento descargable | docx / pdf / pptx skill |
| Diagrama o diagrama de flujo | Visualizer (SVG/HTML inline) |

---

## Librerías disponibles en el sandbox (sin instalar nada)

```jsx
// UI y componentes
import { useState, useEffect, useRef, useMemo } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Progress } from "@/components/ui/progress"
import { Slider } from "@/components/ui/slider"
import { Switch } from "@/components/ui/switch"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { Separator } from "@/components/ui/separator"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Alert, AlertDescription } from "@/components/ui/alert"

// Iconos (lucide-react@0.383.0 — outline solamente)
import { TrendingUp, TrendingDown, Users, Euro, AlertCircle,
         ChevronDown, ChevronUp, Filter, Download, Search,
         CheckCircle2, XCircle, Clock, Zap, Shield } from "lucide-react"

// Gráficas
import { LineChart, BarChart, AreaChart, PieChart, RadarChart,
         Line, Bar, Area, Pie, Radar, Cell,
         XAxis, YAxis, CartesianGrid, Tooltip as RTooltip,
         Legend, ResponsiveContainer } from "recharts"

// Utilidades
import _ from "lodash"
import Papa from "papaparse"
import * as XLSX from "xlsx"
```

**Librerías también disponibles** (menos frecuentes): `mathjs`, `d3`, `plotly`, `three` (r128), `chart.js`, `tone`, `mammoth`, `tensorflow`.

---

## Reglas críticas del sandbox

```
❌ NUNCA usar localStorage / sessionStorage → el sandbox los rechaza silenciosamente
❌ NUNCA usar <form> HTML → usar onClick/onChange de React
❌ NUNCA fetch() a URLs externas no MCP → bloqueado por CSP
✅ Todo el estado va en useState / useReducer
✅ Los datos simulados van hardcodeados o generados en el componente
✅ Tailwind: solo clases del core stylesheet (sin JIT, sin clases arbitrarias)
```

**Clases Tailwind prohibidas** (JIT, no disponibles):
- `text-[#FF5900]` → usar `style={{ color: '#FF5900' }}`
- `grid-cols-[240px_1fr]` → usar `style={{ gridTemplateColumns: '240px 1fr' }}`
- `p-[13px]` → usar `p-3` o `style={{ padding: '13px' }}`

---

## Patrón base — estructura mínima

```jsx
import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function MiArtifact() {
  const [estado, setEstado] = useState(valorInicial)

  return (
    <div className="p-4 space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Título</CardTitle>
        </CardHeader>
        <CardContent>
          {/* contenido */}
        </CardContent>
      </Card>
    </div>
  )
}
```

Reglas de layout:
- El componente raíz nunca lleva `min-h-screen` — el iframe se autoajusta.
- Usar `space-y-4` o `gap-4` para separación vertical.
- Usar `grid grid-cols-2 gap-4` o `grid grid-cols-3 gap-4` para cards en fila.
- Fondo: transparente o `bg-white` — nunca `bg-gray-950` o colores muy oscuros (el iframe hereda el fondo del chat).

---

## Recetas por caso de uso

### KPI cards con tendencia

```jsx
const kpis = [
  { label: "MRR", value: "€43.2K", delta: +12.3, icon: Euro },
  { label: "Clientes activos", value: "187", delta: +5, icon: Users },
  { label: "Churn mensual", value: "2.1%", delta: -0.3, icon: TrendingDown },
]

{kpis.map(({ label, value, delta, icon: Icon }) => (
  <Card key={label}>
    <CardContent className="pt-6">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-muted-foreground">{label}</span>
        <Icon className="w-4 h-4 text-muted-foreground" />
      </div>
      <div className="text-2xl font-bold">{value}</div>
      <div className={`text-xs mt-1 flex items-center gap-1 ${delta > 0 ? 'text-green-600' : 'text-red-500'}`}>
        {delta > 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
        {delta > 0 ? '+' : ''}{delta}% vs mes anterior
      </div>
    </CardContent>
  </Card>
))}
```

### Tabla filtrable con búsqueda

```jsx
const [query, setQuery] = useState("")

const datos = [ /* array de objetos */ ]

const filtrados = useMemo(() =>
  datos.filter(d =>
    Object.values(d).some(v =>
      String(v).toLowerCase().includes(query.toLowerCase())
    )
  ), [query])

// Render:
<Input placeholder="Buscar..." value={query} onChange={e => setQuery(e.target.value)} />
<Table>
  <TableHeader>
    <TableRow>
      {columnas.map(col => <TableHead key={col}>{col}</TableHead>)}
    </TableRow>
  </TableHeader>
  <TableBody>
    {filtrados.map((fila, i) => (
      <TableRow key={i}>
        {Object.values(fila).map((v, j) => <TableCell key={j}>{v}</TableCell>)}
      </TableRow>
    ))}
  </TableBody>
</Table>
```

### Gráfica de área con recharts

```jsx
const datos = [
  { mes: "Ene", mrr: 32000, objetivo: 35000 },
  { mes: "Feb", mrr: 36500, objetivo: 37000 },
  // ...
]

<ResponsiveContainer width="100%" height={220}>
  <AreaChart data={datos}>
    <defs>
      <linearGradient id="mrr" x1="0" y1="0" x2="0" y2="1">
        <stop offset="5%" stopColor="#FF5900" stopOpacity={0.2}/>
        <stop offset="95%" stopColor="#FF5900" stopOpacity={0}/>
      </linearGradient>
    </defs>
    <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
    <XAxis dataKey="mes" tick={{ fontSize: 12 }} />
    <YAxis tick={{ fontSize: 12 }} tickFormatter={v => `€${(v/1000).toFixed(0)}K`} />
    <RTooltip formatter={v => [`€${v.toLocaleString()}`, ""]} />
    <Area type="monotone" dataKey="mrr" stroke="#FF5900" fill="url(#mrr)" strokeWidth={2} name="MRR real" />
    <Line type="monotone" dataKey="objetivo" stroke="#9B9B9B" strokeDasharray="5 5" dot={false} name="Objetivo" />
  </AreaChart>
</ResponsiveContainer>
```

### Wizard de pasos (multi-step)

```jsx
const PASOS = ["Datos empresa", "Servicios", "Resumen"]
const [paso, setPaso] = useState(0)

<div className="flex items-center gap-2 mb-6">
  {PASOS.map((p, i) => (
    <React.Fragment key={p}>
      <div className={`flex items-center gap-2 text-sm ${i <= paso ? 'text-orange-600 font-medium' : 'text-gray-400'}`}>
        <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs
          ${i < paso ? 'bg-orange-600 text-white' : i === paso ? 'border-2 border-orange-600 text-orange-600' : 'border border-gray-300 text-gray-400'}`}>
          {i < paso ? '✓' : i + 1}
        </div>
        {p}
      </div>
      {i < PASOS.length - 1 && <div className={`flex-1 h-px ${i < paso ? 'bg-orange-600' : 'bg-gray-200'}`} />}
    </React.Fragment>
  ))}
</div>
```

### Comparador de opciones (pricing / propuesta)

```jsx
const planes = [
  { nombre: "Básico", precio: 299, features: ["ERP", "Soporte email"] },
  { nombre: "Pro", precio: 599, recomendado: true, features: ["ERP", "GRD", "Soporte 24h", "SLA"] },
  { nombre: "Enterprise", precio: "A medida", features: ["Todo Pro", "Integración custom", "Account Manager"] },
]

{planes.map(plan => (
  <Card key={plan.nombre} className={plan.recomendado ? 'ring-2 ring-orange-500' : ''}>
    {plan.recomendado && <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-orange-500">Recomendado</Badge>}
    <CardHeader>
      <CardTitle>{plan.nombre}</CardTitle>
      <div className="text-3xl font-bold">
        {typeof plan.precio === 'number' ? `€${plan.precio}/mes` : plan.precio}
      </div>
    </CardHeader>
    <CardContent>
      <ul className="space-y-2">
        {plan.features.map(f => (
          <li key={f} className="flex items-center gap-2 text-sm">
            <CheckCircle2 className="w-4 h-4 text-green-500" /> {f}
          </li>
        ))}
      </ul>
    </CardContent>
  </Card>
))}
```

---

## Integración con MasOrange Style

Cuando el artifact es para una presentación, cliente, o entorno MasOrange,
sustituir los colores Tailwind neutros por las variables corporativas:

```jsx
// En el componente raíz, inyectar variables CSS
<div style={{
  '--mo-orange': '#FF5900',
  '--mo-yellow': '#FFD600',
  '--mo-black': '#1A1A1A',
}}>
```

Y en los elementos:
```jsx
// Accent / CTA → orange
<Button style={{ background: 'var(--mo-orange)', color: '#fff', border: 'none' }}>
  Ver propuesta
</Button>

// Bordes de énfasis → orange
<Card style={{ borderLeft: '4px solid var(--mo-orange)' }}>

// KPI positivo → orange / negativo → red estándar Tailwind
<span className={delta > 0 ? '' : 'text-red-500'}
      style={delta > 0 ? { color: 'var(--mo-orange)' } : {}}>
```

Lee `/mnt/skills/user/masorange-style/SKILL.md` si el artifact lleva logotipo,
tipografía corporativa, o es una propuesta comercial completa.

---

## Datos simulados — patrón recomendado

Nunca fetch() ni localStorage. Los datos van hardcodeados o generados:

```jsx
// Hardcoded (propuestas, demos)
const CLIENTES = [
  { id: 1, nombre: "Transportes Roca", flota: 24, estado: "activo", mrr: 1840 },
  { id: 2, nombre: "Frigoríficos Del Pino", flota: 8, estado: "trial", mrr: 620 },
]

// Generados (series temporales, métricas)
const meses = ["Ene","Feb","Mar","Abr","May","Jun"]
const datosGrafica = meses.map((mes, i) => ({
  mes,
  mrr: 30000 + i * 2200 + Math.sin(i) * 800,
  clientes: 150 + i * 5,
}))

// Aleatorios con seed (reproducibles)
const rng = (seed) => { let s = seed; return () => { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646 } }
```

---

## Checklist antes de entregar el artifact

```
□ export default al final (o directamente en la función)
□ No hay localStorage / sessionStorage
□ No hay <form> HTML (usar onClick en botones)
□ Tailwind: no hay clases arbitrarias con []
□ Datos: todos hardcodeados o generados, ningún fetch()
□ Imports: solo librerías del listado disponible
□ Layout: sin min-h-screen en el raíz
□ Funciona con el estado inicial sin interacción del usuario
□ Si es MasOrange: variables CSS --mo-* inyectadas, sin morado/azul como accent
```

---

## Cuándo NO usar esta skill

- La app necesita **persistir datos entre sesiones** → Netlify + Firebase/Supabase
- El entregable es un **fichero descargable** → docx/pdf/pptx skill
- Solo necesitas un **diagrama estático** → Visualizer (SVG)
- La interfaz será **la app real** que usarán usuarios → vanilla HTML + Netlify
- Tienes más de **3 modales encadenados o routing complejo** → reconsiderar si vale la pena en artifact
