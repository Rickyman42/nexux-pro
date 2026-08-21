# Estrategia SEO — Nexux Recepcionista IA

> Escrita 21-ago-2026, tras auditar producción. Basada en `progress/investigacion/investigacion-seo-20260821.md`
> (keywords y competencia). Este archivo es la ÚNICA copia persistente: antes vivía solo en un artefacto HTML
> publicado a claude.ai, fuera del repo — invisible para cualquier agente sin acceso a esa sesión.
> **Estado de ejecución actualizado a 21-ago-2026, commit `2293a23`** — ver notas ✅/❌ en cada capa.

---

## La estrategia en una frase

**Una sola batalla ganable, ganada a fondo — y ganarla también dentro de las IAs, no solo en Google.**

De diez keywords medidas en Google Ads, **una tiene volumen: "recepcionista ia"** (100-1.000/mes,
**+900 % interanual**). Las otras nueve dan 0-10. No hay veinte puertas que abrir: hay una, y está
creciendo rápido porque IONOS está educando el mercado. Con un dominio sin autoridad, repartir esfuerzo
entre veinte páginas es la forma segura de no ganar ninguna. Una página pilar, un puñado de páginas con
trabajo propio, y toda la autoridad apuntando al mismo sitio.

---

## Las cinco capas, por orden de impacto

### Capa 1 — Decirle a Google qué vendes de verdad
*Impacto: alto · Esfuerzo: bajo · Era lo que estaba roto*

- ~~Reescribir el JSON-LD de `Layout.astro`: un solo `Offer` a 29 €, `Organization` y
  `SoftwareApplication` hablando de recepcionista IA, no de peluquerías~~ **✅ hecho, commit `2ea514b`**
- ~~FAQPage con las preguntas reales que hace un comprador~~ **✅ hecho** (garantía 30 días, cancelación,
  precio, qué es — ya no las inventadas de SEO viejo)
- ~~Reescribir `llms.txt`~~ **✅ hecho, commit `2ea514b`**
- **❌ Sitemap y canonical** — pendiente de revisar tras eliminar `/ciudad/*`

### Capa 2 — Que la home merezca el primer puesto
*Impacto: alto · Esfuerzo: medio · Es la única página que pelea la keyword*

- ~~Que el contenido sea verdad — "Tres pasos" ya no promete llamada de 20 min ni configuración manual~~
  **✅ hecho, commit `2ea514b`** (`HowItWorks.astro`)
- **❌ `Pain`, `Proof`, `Testimonials`** — sin auditar del todo, puede quedar copy en clave peluquería
- **❌ Cubrir la intención completa en una sola página**: qué es, qué hace, cuánto cuesta, para quién,
  qué pasa si no funciona, y probarlo — sin que el visitante tenga que salir de la web
- **❌ La demo, arriba y visible** — hoy solo cuelga del CTA del Hero, sin sección propia
- **❌ Velocidad y móvil** — no medido (80 % del tráfico entrará desde el móvil)

### Capa 3 — Ser la respuesta cuando preguntan a una IA
*Impacto: alto y creciendo · Esfuerzo: medio · Aquí hay ventaja de casa (Nexux Intelligence)*

Las recomendaciones locales pedidas a ChatGPT pasaron del **6 % al 45 % en un año**. Ese tráfico no pasa
por el ranking clásico.

- **❌ Medir el punto de partida**: qué responden hoy ChatGPT, Perplexity y Copilot a "recepcionista IA
  para mi negocio". Sin baseline no hay progreso demostrable
- **❌ Escribir para ser citado**: respuestas directas y extraíbles, cifras concretas, definiciones
  limpias — el mismo arsenal que vende Nexux Intelligence, aplicado a la propia casa
- **❌ Bing Webmaster Tools**: Bing sirve nexux.pro (verificado con navegador real), pero falta saber
  cuántas páginas indexa de verdad. Copilot bebe de Bing

### Capa 4 — Existir como negocio, no solo como web
*Impacto: alto en local · Esfuerzo: bajo · Depende de una decisión de Ricardo*

- **❌ Ficha de Google Business Profile** — pesa 32-36 % del ranking local y alimenta los AI Overviews.
  Falta decidir: ¿reconvertir la propiedad antigua o crear una nueva? (mirar antes su historial —
  actividad de otro sector arrastra señales que confunden)
- **❌ Reseñas** — ~20 % del peso, y es la prueba social que hoy no existe. Cada cliente del primer mes
  debería terminar con una petición de reseña
- **❌ Entidad coherente** — mismo nombre, misma descripción y mismos datos en web, ficha, schema y
  llms.txt (esto último ya avanzó con la capa 1, pero falta la ficha de Google para que coincida del todo)

### Capa 5 — Páginas de apoyo, pocas y con oficio
*Impacto: medio · Esfuerzo: medio · Solo después de cerrar las capas 1 y 2*

- **❌ vs Booksy** — "booksy" sí tiene volumen de marca. No para atacarles: para captar al que ya paga
  comisiones (30 % por cliente nuevo) y no lo sabía
- **❌ Precio** — la ficha del producto ya existe (`/paquetes/recepcionista`) con intención transaccional
  distinta a la home, para que no se canibalicen
- **❌ RGPD** — objeción de venta real; los tres competidores medidos tienen página propia
- **❌ 2-3 sectores** con contenido genuinamente distinto (vocabulario, ejemplos y precios de ese
  sector). Si dos páginas se parecen al 95 %, son *doorway* y restan en vez de sumar
- **❌ Plantillas y calculadoras gratis** — es lo que usan los tres competidores medidos para captar

---

## Lo que NO es la estrategia — y por qué, con el dato

| Táctica | Veredicto | Motivo medido |
|---|---|---|
| Enlaces de ciudades en la home (Madrid, Barcelona, Valencia…) | Quitar | SEO de hace diez años. Ningún competidor lo hace y Google las trata como *doorway*. Además son capitales: imposibles de ganar. **✅ Ejecutado — páginas `/ciudad/*` borradas del todo, commit `2ea514b`** |
| Una página por cada keyword | No | Solo una keyword tiene volumen. Las demás dieron 0-10/mes |
| Páginas por municipio | No | Mismo motivo. Ver tabla de descartados en `AGENTS.md §3` |
| "Centralita virtual" | No aún | Tiene volumen, pero es telefonía. Sin voz, sería tráfico que rebota |
| Meter la keyword en más sitios | Ya basta | Está en title, meta y H1. Repetirla más no suma; lo que falta es todo lo demás |
| Blog de artículos genéricos | Más tarde | Sin autoridad de dominio, escribir mucho no rankea. Primero las capas 1-4. (El blog actual — 4 posts de peluquería — tampoco vale para este posicionamiento; ver `AGENTS.md §4`) |

---

## Orden de trabajo recomendado

| # | Tarea | Duración estimada | Estado |
|---|---|---|---|
| 1 | Schema, llms.txt y sitemap | medio día | ✅ Schema y llms.txt hechos; sitemap pendiente de revisar |
| 2 | Copy honesto en toda la home (Tres pasos, Pain, Proof, Testimonials) | 1 día | ✅ Tres pasos hecho; Pain/Proof/Testimonials sin auditar del todo |
| 3 | Quitar los enlaces de ciudades (sección entera) | 10 min | ✅ Hecho — páginas borradas, no solo desenlazadas |
| 4 | Demo con sección propia en la home | medio día | ❌ Pendiente |
| 5 | Baseline en IA + Bing Webmaster Tools | medio día | ❌ Pendiente |
| 6 | Ficha de Google Business Profile | — | ❌ Pendiente, decisión de Ricardo |
| 7 | vs Booksy, Precio y RGPD | 2 días | ❌ Pendiente (Precio ya existe como ficha de producto; falta comparativa y RGPD) |

---

## Base de evidencia

Volúmenes: Planificador de Palabras Clave de Google Ads, cuenta propia, España, ago-2025→jul-2026,
medidos el 21-ago-2026. Arquitectura de competencia: sitemaps completos de recepcionista.com (615 URLs),
engrana.es y citaflow.com. Pesos del ranking local: estudio Whitespark 2026 — la dirección es sólida,
las cifras exactas bailan entre fuentes. El estado del schema y del llms.txt se leyó directamente de lo
que servía producción antes de corregirlo. Detalle completo de keywords y DAFO:
`progress/investigacion/investigacion-seo-20260821.md`.
