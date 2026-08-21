# AGENTS.md — nexux.pro

> **Léeme entero antes de tocar nada.** Vale para cualquier agente: Claude Code, Codex, OpenCode, Qwen, ZCODE.
> Ley general de Nexux: `~/nexus-brain/AGENTS.md` en la Pi. Este archivo NO la repite: solo añade lo propio de nexux.pro.
> Si hay conflicto, manda la ley general. Estado del proyecto: `~/nexus-brain/nexux-live-state.md`.
> ⛔ nexux.pro (SaaS B2B) es INDEPENDIENTE de nexux.es (app de citas B2C). No mezclar código, DB, bots ni tokens.

---

## 1. QUÉ ESTAMOS HACIENDO (actualizado 2026-08-21)

nexux.pro dejó de ser «software de gestión para peluquerías». Ahora es un **mono-producto horizontal**:

> **Nexux Recepcionista IA** — asistente que atiende los mensajes del negocio por WhatsApp, Telegram o
> web, responde 24 h y reserva la cita en el calendario. **29 €/mes, tarifa plana, todo incluido.**

- **Marca:** Nexux. **Producto:** Recepcionista IA. **Asistente:** Lara. No inventar nombres nuevos.
- **Cliente:** cualquier negocio que trabaje con cita previa. NO se verticaliza el producto; sí las páginas.
- **Precio:** 29 € de lanzamiento, congelado de por vida para los primeros 50. Regular 35 €.
  Parámetros en `src/data/plans.ts` (`LAUNCH_PRICE`, `REGULAR_PRICE`, `LAUNCH_SEATS`).
- **Posicionamiento (estilo O2):** un precio, sin permanencia, sin comerciales, sin comisiones.
  «Cercanía» significa **trato**, no geografía: tecnología de las grandes para el negocio pequeño.
- **Venta 100 % autoservicio.** Nadie llama a nadie. El alta ya es automática de punta a punta:
  pago Stripe → webhook → se crea el cliente → email de bienvenida → **Lara configura el negocio hablando
  con el dueño**. Ver `lib/stripe-webhook.js` y `lib/onboarding.js` en `~/nexux-clients`.
- **Canal de captación:** SEO + visibilidad en buscadores de IA. **Sin email frío** (ver §3).
- **Objetivo de la fase actual:** 10 negocios usándolo de verdad y 3 casos con cifras publicables.
  Si a los dos meses no hay 3 pagando, el problema es el canal — se para y se replantea el canal, no el producto.

---

## 2. CÓMO SE TRABAJA AQUÍ (norma de Ricardo, 2026-08-21)

> «No tengo prisa y al revés, la prisa es peor. Lo que se haga se hace bien, contrastado, con datos y
> medidos. Y lo que funciona AHORA, no lo de hace 10 años. Si no, no se hace nada.»

Traducido a reglas que se cumplen o no se cumplen:

1. **Ninguna táctica sin dato que la sostenga.** Si no hay dato, se dice «no verificado» y NO se ejecuta.
   Entregar nada es una salida aceptable. Entregar sobre suposición, no.
2. **Nada de buenas prácticas de memoria.** Contrastar contra fuentes del año en curso antes de proponer.
   Vale especialmente para SEO: cambió de raíz (AI Overviews, señales de Google Business Profile, reseñas).
3. **Medir en la capa real:** producción, navegador de verdad, y **control positivo** cuando se mide un
   buscador. Un cero sin control positivo no distingue «no salgo» de «me están bloqueando».
4. **Decir qué NO se ha podido medir.** Con esas palabras. No rellenar huecos a ojo.
5. **Verificar lo que EJECUTA, no lo que documenta.** Que una norma esté escrita no prueba que se aplique.
   Precedente: este mismo archivo mandaba escribir en `progress/` desde mayo y la carpeta no existía.

---

## 3. DESCARTADO — NO REPROPONER

Cada línea costó tiempo o dinero. Si crees que hay que reabrir alguna, trae un dato nuevo, no una opinión.

| Descartado | Por qué | Fecha |
|---|---|---|
| **Email en frío** | 86 leads, 31 rebotes (36 %), 0 respuestas, 0 €. Decisión de Ricardo | 19-ago-2026 |
| **Páginas «producto + ciudad»** (recepcionista IA en Móstoles…) | Ningún competidor lo hace, y Google las trata como *doorway pages* si comparten ~95 % del texto | 21-ago-2026 |
| **Atacar «alternativa a Booksy»** | Sin señal de demanda en el autocompletado de Google | 21-ago-2026 |
| **Atacar «centralita virtual»** | Es la palabra con volumen, pero es TELEFONÍA. Sin voz, atrae tráfico que rebota | 21-ago-2026 |
| **Planes 249/449/749 €** | Nunca validados: 0 cobros en Stripe. El mercado ancla en 29-48 € | 21-ago-2026 |
| **Vender por teléfono / comerciales** | A 29 €/mes el coste de venta se come el margen de un año | 21-ago-2026 |

**Pendiente de decidir, no descartado:** la voz (llamadas). Hoy solo existe llamada perdida → mensaje
grabado → WhatsApp (`lib/twilio.js`). NO hay conversación de voz. **No prometerla en la web.**

---

## 4. ARQUITECTURA

| Componente | Path | Deploy |
|---|---|---|
| Landing + portal | `~/nexux-pro/` | Vercel (push a main despliega) |
| API de clientes | `~/nexux-clients/` | Pi :3460 (PM2: nexux-clients) |
| Servidor de leads | `~/nexux-pro/leads-server.cjs` | Pi (PM2: nexux-pro-leads) |
| Dashboard Mint | `~/nexux-pro/mint-dashboard/` | Pi :3700 (PM2: mint-dashboard) |
| Clientes | `~/nexux-clients/clients/<id>/config.json` | — |

---

## 5. REGLAS DE CÓDIGO

| Regla | Detalle |
|---|---|
| pnpm siempre | `pnpm add`, nunca `npm install` |
| Pull antes de editar | `git -C ~/nexux-pro pull origin main` |
| Vercel SSR | `prerender=false` en páginas dinámicas del portal |
| Stripe | no duplicar sessions; comprobar con `stripe-setup.js` |
| Portal auth | middleware en `src/middleware/auth.ts` — no bypassear |
| owner_email | obligatorio en el config.json del cliente; sin él no salen los emails de ciclo de vida |
| Rutas que desaparecen | **redirect 301 obligatorio**. Comprobar antes con `curl -o /dev/null -w '%{http_code}'` |
| Copias .bak | van a `.gitignore`, no al repo |

**Antes de commit:** `pnpm build` completo sin errores · sin claves de Stripe en el frontend ·
`owner_email` presente donde toque · redirects puestos si una URL deja de existir.

**Antes de decir «hecho»** — obligatorio, sin excepción:

```bash
export NEXUX_AGENT=<tu-nombre>
python3 ~/scripts/nexux-verify.py gitclean:/home/nexux/nexux-pro syntax:<archivo> url:<url>
```

Si devuelve FALLO, **no está hecho**: no se le dice a Ricardo y no se escribe OK en ningún registro.

**NO se hace push sin OK de Ricardo**, salvo que diga «deploy».

---

## 6. REGISTRO DE TRABAJO — OBLIGATORIO

Al terminar una tarea, **una línea** al final de `progress/REGISTRO.md`:

```
YYYY-MM-DD | agente | qué se hizo | commit o evidencia | OK|PARCIAL|FALLO
```

Si es PARCIAL o FALLO, la línea siguiente lleva exactamente `  causa: <texto>` (dos espacios delante),
o el escáner de kaizen no la ve y el fallo nunca se corrige.

Ese registro es el índice local del repo. La evidencia completa va además al ledger general
(`~/nexus-brain/quality-ledger.md`) y el estado a `nexux-update-brain.py`, como manda la ley general.
No se duplica el contenido: aquí una línea, allí la evidencia.

---

## 7. AL ENTRAR AL PROYECTO

1. Leer este archivo entero.
2. Leer `~/nexus-brain/nexux-live-state.md` (estado real) y las últimas 15 líneas de `progress/REGISTRO.md`.
3. `git -C ~/nexux-pro pull origin main` y `git log --oneline -10`.
4. Comprobar §3 antes de proponer nada: si tu idea está ahí, ya se descartó y por qué.
