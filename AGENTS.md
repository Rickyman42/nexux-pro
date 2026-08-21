# AGENTS.md — nexux.pro

> **Léeme entero antes de tocar nada.** Vale para cualquier agente: Claude Code, Codex, OpenCode, Qwen, ZCODE.
> Ley general de Nexux: `~/nexus-brain/AGENTS.md` en la Pi. Este archivo NO la repite: solo añade lo propio de nexux.pro.
> Si hay conflicto, manda la ley general. Estado del proyecto: `~/nexus-brain/nexux-live-state.md`.
> Historial de trabajo de este repo: `progress/REGISTRO.md` (léete las últimas 20 líneas).
> ⛔ nexux.pro (SaaS B2B) es INDEPENDIENTE de nexux.es (app de citas B2C). No mezclar código, DB, bots ni tokens.

---

## 1. QUÉ ESTAMOS HACIENDO (actualizado 2026-08-21)

nexux.pro dejó de ser «software de gestión para peluquerías». Ahora es un **mono-producto horizontal**:

> **Nexux Recepcionista IA** — asistente que atiende los mensajes del negocio por WhatsApp, Telegram o
> web, responde 24 h y reserva la cita en el calendario. **29 €/mes, tarifa plana, todo incluido.**

- **Marca:** Nexux. **Producto:** Recepcionista IA. **Asistente:** Lara. No inventar nombres nuevos.
- **Cliente:** cualquier negocio que trabaje con cita previa. NO se verticaliza el producto; sí las páginas.
- **Precio:** 29 € de lanzamiento (sube a 35 €; quien entra ahora se queda en 29 mientras siga de alta).
  Parámetros en `src/data/plans.ts` (`LAUNCH_PRICE`, `REGULAR_PRICE`, `LAUNCH_SEATS`).
- **NO hay prueba gratuita.** Se paga desde el día 1, con **garantía de devolución de 30 días**
  (decisión de Ricardo, 21-ago). Al cancelar, el mes en curso queda pagado y no se cobra el siguiente.
- **Posicionamiento (estilo O2):** un precio, sin permanencia, sin comerciales, sin comisiones.
  «Cercanía» significa **trato**, no geografía: tecnología de las grandes para el negocio pequeño.
- **Venta 100 % autoservicio.** Nadie llama a nadie.
- **Canal:** SEO + visibilidad en buscadores de IA. **Sin email frío** (ver §3).
- **Objetivo de fase:** 10 negocios usándolo y 3 casos con cifras publicables.
  Si a los dos meses no hay 3 pagando, el problema es el canal — se para y se replantea el canal.

---

## 2. CÓMO SE TRABAJA AQUÍ (norma de Ricardo, 2026-08-21)

> «No tengo prisa y al revés, la prisa es peor. Lo que se haga se hace bien, contrastado, con datos y
> medidos. Y lo que funciona AHORA, no lo de hace 10 años. Si no, no se hace nada.»

1. **Ninguna táctica sin dato que la sostenga.** Si no hay dato, se dice «no verificado» y NO se ejecuta.
2. **Nada de buenas prácticas de memoria.** Contrastar contra fuentes del año en curso antes de proponer.
   Vale especialmente para SEO, que cambió de raíz (AI Overviews, señales de GBP, reseñas).
3. **Medir en la capa real:** producción, navegador de verdad, y **control positivo** al medir un buscador.
4. **Decir qué NO se ha podido medir.** Con esas palabras. No rellenar huecos a ojo.
5. **Verificar lo que EJECUTA, no lo que documenta.** Tres precedentes reales en este repo, en §7.

---

## 3. DESCARTADO — NO REPROPONER

Cada línea costó tiempo o dinero, o la descartó un dato. Reabrirlas exige un dato nuevo, no una opinión.

| Descartado | Por qué | Fecha |
|---|---|---|
| **Email en frío** | 86 leads, 31 rebotes (36 %), 0 respuestas, 0 €. Decisión de Ricardo | 19-ago-2026 |
| **Páginas «producto + ciudad»** | Ningún competidor lo hace, y Google las trata como *doorway* si comparten ~95 % del texto. **Borradas del todo** (`src/pages/ciudad/`, `CityHero.astro`, `data/ciudades.ts`) — no solo desenlazadas: cada una llevaba su propio JSON-LD con 249/449/749 € y "Starter/Pro/Total", una segunda copia del mismo problema que el schema global. 301 a `/paquetes/recepcionista` en `vercel.json` | 21-ago |
| **Keywords largas de canal o problema** | «recepcionista ia whatsapp», «chatbot citas», «alternativa a booksy», «no perder llamadas», «software citas peluqueria», «agenda citas whatsapp», «bot whatsapp empresa» — **todas medidas a 0-10 búsquedas/mes** en Google Ads | 21-ago |
| **«Centralita virtual»** | Tiene volumen pero es TELEFONÍA. Sin voz atraería tráfico que rebota | 21-ago |
| **Planes 249/449/749 €** | Nunca validados: 0 cobros en Stripe. El mercado ancla en 29-48 € | 21-ago |
| **Prueba gratuita de 7 días** | Sustituida por garantía de 30 días. La demo ya hace de prueba sin registro | 21-ago |
| **Vender por teléfono o comerciales** | A 29 €/mes el coste de venta se come el margen de un año | 21-ago |

**Pendiente de decidir, no descartado:** la voz (llamadas). Hoy solo existe llamada perdida → mensaje
grabado → WhatsApp (`lib/twilio.js` en nexux-clients). NO hay conversación de voz. **No prometerla.**

---

## 4. ESTADO REAL — QUÉ ESTÁ HECHO Y QUÉ NO

### ✅ Hecho y verificado en producción (21-ago-2026)

| Qué | Dónde | Evidencia |
|---|---|---|
| Producto y precio únicos | `src/data/plans.ts` | slug `recepcionista`, 29 € |
| Precio real en Stripe (cuenta **live**) | Stripe | `prod_V6xlRvLwrMTEJF` · `price_1U6jqd2SQwDzHtsFf3wEcuQe` |
| **Checkout funcionando** | `api/stripe/create-session.js` | iframe de Stripe carga, 29 €, pide teléfono |
| Guion de venta de Lara | `nexux-clients/lib/bot-prompt-lara.js` | probado en vivo: dice 29 €, no promete llamadas ni Instagram |
| Lara en la ficha de producto | `src/pages/paquetes/[plan].astro` | widget presente; `data-open-lara` abre el chat |
| Tema claro | `src/styles/global.css` | tokens invertidos; nav, ficha y mockup corregidos |
| Menú hamburguesa móvil | `src/components/Nav.astro` | no existía; ahora abre con 5 enlaces |
| Bloque de precio único + agenda | `src/components/Pricing.astro` | tarjeta partida: oferta + 7 citas de ejemplo |
| Redirects de rutas muertas | `vercel.json` | 6 × 301 (starter/pro/total, prueba-gratis, oferta, promo) |
| Calculadora con precio correcto | `src/components/Pain.astro` | 348 €/año (antes 2.988) |
| **Schema JSON-LD reescrito** | `src/layouts/Layout.astro` | Organization/SoftwareApplication/FAQPage al mono-producto, precio único 29 €, `python3 -c "json.loads(...)"` valida y `pnpm build` pasa |
| **`llms.txt` reescrito** | `public/llms.txt` | Recepcionista IA, 29 €, sin peluquerías |
| **Copy de "Cómo funciona" corregido** | `src/components/HowItWorks.astro` | 3 pasos reales: alta en 2 min → conectas tu WhatsApp con QR tú mismo → Lara responde al instante. Ya no promete llamada de 20 min ni configuración manual |
| **Páginas de ciudad eliminadas** | `src/pages/index.astro` + borrado de `src/pages/ciudad/`, `CityHero.astro`, `data/ciudades.ts` | `pnpm build` ya no genera `/ciudad/*`; 6 redirects 301 en `vercel.json` |

### ❌ NO hecho — y por qué importa

| Qué falta | Impacto | Dónde |
|---|---|---|
| **`Pain`, `Proof`, `Testimonials` sin auditar del todo** | Puede quedar copy o datos en clave peluquería fuera de lo ya corregido en `Pain` (calculadora) | `src/components/` |
| **Blog 100 % sobre peluquerías** | 4 posts (`automatizar-reservas-whatsapp-peluqueria`, `cuanto-cuesta-cita-perdida`, `migrar-de-treatwell-sin-perder-clientes`, `treatwell-vs-booksy-peluquerias`). Decisión de Ricardo 21-ago: **no borrar**, pero no vale para el posicionamiento nuevo — mismo problema de fondo que el schema, pendiente de decidir si se reescriben, se dejan como long-tail de nicho o se despublican | `src/content/blog/*.md` |
| Ficha de Google Business Profile | Un tercio del ranking local | — |
| Bing Webmaster Tools | Bing sirve nexux.pro (verificado), pero falta el recuento real de indexación | — |
| Baseline en buscadores de IA | Sin punto de partida no hay progreso medible | — |
| Demo enlazada desde la home | Es el mejor argumento de venta y solo cuelga de páginas sueltas | `src/components/Hero.astro` ya enlaza; falta sección propia |

---

## 5. ARQUITECTURA — DÓNDE VIVE CADA COSA

| Componente | Path | Deploy |
|---|---|---|
| Landing + portal | `~/nexux-pro/` | Vercel (push a main despliega) |
| **Funciones de pago y leads** | `~/nexux-pro/api/` | **Vercel serverless — ver aviso abajo** |
| API de clientes / Lara / provisioning | `~/nexux-clients/` | Pi :3460 (PM2: nexux-clients) |
| Servidor de leads | `~/nexux-pro/leads-server.cjs` | Pi (PM2: nexux-pro-leads) |
| Dashboard Mint | `~/nexux-pro/mint-dashboard/` | Pi :3700 (PM2: mint-dashboard) |
| Clientes | `~/nexux-clients/clients/<id>/config.json` | — |

> 🔴 **AVISO QUE COSTÓ UNA SESIÓN ENTERA.** La carpeta `api/` de la raíz son **funciones serverless de
> Vercel** y **ganan sobre los rewrites de `vercel.json`**. `/api/stripe/create-session` NO llega a la Pi:
> lo sirve `api/stripe/create-session.js`. Hay lógica **duplicada** entre esa carpeta y `~/nexux-clients`.
> Si cambias precios o planes, **hay que cambiarlo en los dos sitios** o el pago sigue con datos viejos.
> Comprueba siempre qué responde de verdad: `curl -sD- https://nexux.pro/api/...` — si el header dice
> `Server: Vercel`, no lo sirve la Pi.

---

## 6. REGLAS DE CÓDIGO

| Regla | Detalle |
|---|---|
| pnpm siempre | `pnpm add`, nunca `npm install` |
| Pull antes de editar | `git -C ~/nexux-pro pull origin main` |
| Vercel SSR | `prerender=false` en páginas dinámicas del portal |
| Stripe | precio y producto ya creados; no duplicar |
| Portal auth | middleware en `src/middleware.ts` — no bypassear |
| owner_email | obligatorio en el config.json del cliente; sin él no salen los emails de ciclo de vida |
| Rutas que desaparecen | **redirect 301 obligatorio**. Comprobar antes con `curl -o /dev/null -w '%{http_code}'` |
| Copias .bak | van a `.gitignore`, no al repo |
| Editar por SSH | los heredoc con `${...}` los expande bash. Escribe el script en local y pásalo por `ssh 'python3 -' < script.py`, o sube el fichero con `scp` |

**Antes de commit:** `pnpm build` completo · sin claves de Stripe en el frontend · redirects puestos.

**Antes de decir «hecho»** — obligatorio:

```bash
export NEXUX_AGENT=<tu-nombre>
python3 ~/scripts/nexux-verify.py gitclean:/home/nexux/nexux-pro syntax:<archivo> url:<url>
```

Si devuelve FALLO, **no está hecho**. (El verificador no valida `.css` ni `.astro`: para eso, `pnpm build`.)

**NO se hace push sin OK de Ricardo**, salvo que diga «deploy».

---

## 7. TRAMPAS YA PISADAS — no repetirlas

1. **La carpeta `api/` de Vercel gana sobre la Pi.** Arreglé el backend entero y el checkout seguía roto
   porque el pago lo servía otro archivo. Ver §5.
2. **Astro no aplica estilos a elementos creados por JavaScript.** Las burbujas del chat del hero nacen
   sin el atributo de ámbito, así que ninguna regla con scope les llegaba. Se resolvió con `:global()`.
3. **El CDN de Vercel cachea el HTML unos minutos.** Verifica con `?cb=$(date +%s)` o leerás el título
   viejo y parecerá que el deploy falló.
4. **Las memorias envejecen.** Una nota antigua decía que `ui_mode` debía ser `embedded`; Stripe responde
   hoy que `embedded` está retirado y hay que usar `embedded_page`. Lee el error del proveedor.
5. **Hay dos listas blancas de planes** en `nexux-clients/provision-http.js` (líneas ~230 y ~942).
   Cambiar solo una deja el pago roto con un `invalid_plan` que no explica nada.
6. **`nexux-clients` NO tiene control de versiones propio** (es el repo de `/home/nexux`, con el que está
   prohibido hacer pull/rebase). Los cambios ahí solo tienen copias `*.PREPIVOTE-20260821` en disco.
   **Antes de tocar un archivo de ese repo, haz una copia con fecha.**
7. **Un dato estructurado desactualizado casi nunca vive en un solo sitio.** El schema de `Layout.astro`
   no era el único con precios 249/449/749 €: cada página de `/ciudad/*` llevaba su propia copia
   independiente. Al corregir un JSON-LD, busca `grep -rl "application/ld+json"` en todo `src/` antes
   de dar la tarea por cerrada.

---

## 8. REGISTRO DE TRABAJO — OBLIGATORIO

Al terminar una tarea, **una línea** al final de `progress/REGISTRO.md`:

```
YYYY-MM-DD | agente | qué se hizo | commit o evidencia | OK|PARCIAL|FALLO
```

Si es PARCIAL o FALLO, la línea siguiente lleva exactamente `  causa: <texto>` (dos espacios delante),
o el escáner de kaizen no la ve y el fallo nunca se corrige.

La evidencia completa va además al ledger general (`~/nexus-brain/quality-ledger.md`) y el estado a
`nexux-update-brain.py`. No se duplica el contenido: aquí una línea, allí la evidencia.

---

## 9. AL ENTRAR AL PROYECTO

1. Leer este archivo entero.
2. Leer `~/nexus-brain/nexux-live-state.md` y las últimas 20 líneas de `progress/REGISTRO.md`.
3. `git -C ~/nexux-pro pull origin main` y `git log --oneline -15`.
4. Comprobar §3 antes de proponer nada: si tu idea está ahí, ya se descartó y por qué.
5. Comprobar §4 para saber qué falta de verdad, y §7 para no repetir trampas ya pisadas.
