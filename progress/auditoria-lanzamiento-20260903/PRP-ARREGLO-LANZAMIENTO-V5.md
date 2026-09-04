# PRP — Arreglo de lanzamiento nexux.pro · **v5 — cerrado para ejecución**

**Fecha:** 2026-09-03 (v5 escrita entre las 23:50 del 3-sep y las 00:40 del 4-sep) · **Origen:** auditoría de 7 áreas del 3-sep
(`~/nexux-pro/progress/auditoria-lanzamiento-20260903/` + `TABLA-CRUZADA.md`)
**Historial:** v1 rechazada · v2 · v3 con las 10 correcciones de Ricardo · v4 revisada por Codex ·
**v5: el diagnóstico del camino del dinero se ha vuelto a medir línea a línea en el código que ejecuta y se
ha reescrito. Lo que en v4 era una hipótesis, aquí es un hecho con su comando.** La v4 queda en
`PRP-ARREGLO-LANZAMIENTO-V4.md` como histórico.
**Ejecuta:** Opus 5 (Claude Code), con Sonnet para lo mecánico. **Regla de oro:** verifica el fichero que
EJECUTA, no el que documenta. Todo test se sabotea antes de creérselo.

---

## 1. PRIORIDAD

> El camino de los **29 €** tiene que funcionar: octavillas, anuncios, pagos, demo. **Alta automática.**

```
octavilla → QR → /f/dN → /demo → habla con Lara → paga 29 € → alta automática
   → UN correo → portal → conecta un canal → una cita → cancelación → desactivación
```

La cadena acaba en **cancelación y desactivación** porque esa es la prueba de aceptación (apartado 9). Por eso
el ciclo de vida de Stripe está en la Ola 1: sin él, la prueba no se puede pasar.

---

## 2. EL CAMINO DEL DINERO, MEDIDO — sustituye al diagnóstico de la v4

Todo lo de este apartado se leyó o midió el 3-sep entre las 23:00 y las 00:30 contra el código real y contra
producción (solo GET). Ninguna línea viene de memoria.

### 2.1 · Hay CUATRO receptores de Stripe escritos. Solo uno recibe algo.

| # | Fichero | Cómo se llega | Estado real |
|---|---|---|---|
| R1 | `~/nexux-pro/api/webhook/stripe.js` (Vercel) | `https://nexux.pro/api/webhook/stripe` y `https://nexux.pro/webhook/stripe` (rewrite en `vercel.json`) | **VIVO. Es el único que Stripe llama.** Verifica HMAC; **sin ventana de tiempo**; **sin dedup**; solo trata `checkout.session.completed`; los otros 5 eventos devuelven `{received:true}` y se ignoran; **responde 200 siempre**, falle lo que falle |
| R2 | `~/nexux-clients/provision-http.js:1611` (Pi :3460) | `https://pi.nexux.pro/webhook/stripe` — el túnel de Cloudflare va **directo al 3460**, sin nginx (medido: `GET /` devuelve 404 de Express, no el HTML que serviría nginx) | **MUERTO.** `app.use(express.json())` en la línea 39 parsea el cuerpo antes; `express.raw()` en 1611 se salta a sí mismo; `String(req.body)` da `"[object Object]"`; `JSON.parse` revienta → **400 `invalid_json` a todo evento**. Nunca llega a verificar ni a ejecutar nada. La auditoría B lo registró sin interpretarlo: «la Pi devuelve `{"error":"invalid_json"}`» |
| R3 | `~/nexux-clients/lib/admin.js:49` (Pi, servidor admin) | Escucha en `127.0.0.1:3458`; solo lo alcanzaría nginx:80 (`/etc/nginx/sites-enabled/nexux-pro:29`), cuyo `server_name` es `nexux.pro`, que resuelve a Vercel | **Correcto pero inalcanzable desde internet.** `express.raw` va antes de `express.json` (líneas 16-17), así que el cuerpo crudo sí llega. Lo arranca siempre `index.js:66` (`startAdmin`) |
| R4 | `~/nexux-pro/src/pages/api/webhook/stripe.ts` (Astro) | Sombreado por la carpeta `api/` de la raíz | **MUERTO.** Y es el «reenviador de firmas» que la v4 decía no querer: copia `stripe-signature` hacia la Pi (línea 16). Borrar |

**Endpoints registrados en Stripe (`GET /v1/webhook_endpoints`, cuenta live, medido):**
- `we_1TYhnJ2SQwDzHtsFlg9HdpO8` → `https://nexux.pro/api/webhook/stripe` · 6 eventos (`checkout.session.completed`, `customer.subscription.updated/.deleted`, `invoice.payment_failed/.payment_action_required/.paid`) · api `2026-04-22.dahlia`
- `we_1TXfnR2SQwDzHtsFrJdcPMhH` → `https://nexux.pro/webhook/stripe` · solo `checkout.session.completed` · api `2025-08-27.basil` · **duplicado: acaba en la misma función R1**
- `we_1TAcyP…` → `nexux.es/?wc-api=wc_stripe` · **disabled** · no es de este proyecto
- **Ninguno apunta a la Pi.**

### 2.2 · Lo que la función de la Pi hace bien y mal — `lib/stripe-webhook.js`

- `handleStripeWebhook` (l. 220): **`if (secret && sigHeader)` → sin cabecera NO verifica y sigue.** Este es
  el agujero real que la auditoría B encontró simulando a nivel de función (informe B, l. 107: «simulada en
  `/tmp/auditB`»). Hoy es inalcanzable porque R2 muere antes y R3 no ve internet. **En cuanto alguien
  arregle R2 sin tocar esta línea, el agujero se abre a internet.** Por eso el orden del apartado 4 es
  función primero, ruta después.
- `verifyStripeSignature` (l. 47-78): **sí** tiene ventana de 300 s y comparación en tiempo constante.
- Ramas: `invoice.payment_failed` (contador + Telegram + correo Brevo; **no idempotente**: cada reintento de
  Stripe suma uno y manda otro correo) · `customer.subscription.updated` (límites y funciones del plan;
  `PRICE_TO_PLAN` ya corregido hoy con 29/79 en `44241c0`) · `customer.subscription.deleted`
  (`active=false` inmediato, `deactivatedAt`, Telegram, win-back) · `checkout.session.completed` (dedup
  **persistente** por `event.id` en `clients/_processed_events.json`, `markProcessed` **antes** de los
  efectos, y `createClientDir` que crea un cliente **hueco con `active:false`**; su `sendBrevoWelcome` solo
  da de alta un contacto en Brevo, **no manda correo**). Conclusión: **la rama de compra de la Pi no sirve
  para el alta; las tres de ciclo de vida sí, con la salvedad de `payment_failed`.**

### 2.3 · Qué pasa HOY, paso a paso, cuando alguien paga 29 €

1. `checkout.ts:33-52` lee `sessionStorage.laraData` y manda `nombre/salon/telefono/…` en el body.
   **Nadie escribe `laraData` en todo `src/` ni `public/`** (grep: solo lo lee `checkout.ts`). Llega vacío.
2. `api/stripe/create-session.js` mete en `metadata` solo lo que venga (nada) + `metadata[plan]`; activa
   `phone_number_collection`, así que el **teléfono sí** llega luego por `customer_details.phone`.
3. Stripe cobra y manda `checkout.session.completed` **dos veces** (dos endpoints) a R1.
4. R1 verifica la firma, lanza `notifyTelegram` (siempre) y `provisionClient` **en paralelo**.
5. `provisionClient` monta `payload.salon = md.salon || null` → **null** → `if (!payload.plan ||
   !payload.salon || !payload.telefono) return null`. **Ni siquiera llama a la Pi.**
6. Como devolvió `null`: `sendConfirmationEmail` («en menos de 24 horas nos pondremos en contacto» — falso,
   nadie llama) + `notifyProvisioningFailed` a Telegram («provisionar manualmente: `node provision.js`» —
   contradice la norma de altas automáticas).
7. R1 responde `200 {received:true}`. Stripe da el evento por entregado. **No reintenta jamás.**
8. Resultado: el cliente ha pagado, tiene un correo que promete una llamada, y no existe.

Si algún día `salon` llegara: la Pi `/provision` (l. 225) crea el cliente, arranca Baileys, captura el QR,
**responde**, y **después** lanza su propio correo «🎉 Tu portal está listo» sin `await` ni comprobar
respuesta (l. 328+). R1 recibe el resultado y manda `sendOnboardingEmail` («Tu asistente está listo»).
**Dos correos.** La idempotencia de la Pi sí es persistente (`findBySession` en `lib/clients-index.js`,
índice en disco): un reintento devuelve el cliente existente con `alreadyProvisioned:true`.

### 2.4 · Qué pasa HOY cuando alguien cancela, cambia de plan o le falla el pago

Stripe manda el evento a R1. R1 no lo trata. `200 {received:true}`. **Nada.** El cancelado sigue atendido,
el que sube a 79 € paga y no recibe funciones, el impago no lo ve nadie. La Pi tiene las ramas escritas y
**no las ha ejecutado nunca en producción** (`_processed_events.json`: 1 evento, del 11-jun).

### 2.5 · Lo demás que se midió y afecta al plan

- **`config.active` en los puntos de entrada:** `lib/whatsapp.js` **0** veces · `lib/twilio.js` **0** ·
  `lib/outreach-runner.js` 0 · `lib/telegram.js` 1 · `lib/scheduler.js` 3 · las rutas públicas
  `/public/:clientId/book` y `/api/lara-web/chat` de `provision-http.js` **no lo comprueban**. Un cliente
  desactivado sigue atendido por WhatsApp, Twilio, reserva pública y chat web.
- **Telegram:** `lib/telegram.js:195` → `chat(systemPrompt, history, 150)`. `lib/ai.js:53` devuelve
  `data.choices[0].message.content.trim()`: **el motivo de parada (`finish_reason`) se descarta.** Hoy es
  imposible detectar un corte desde `telegram.js`.
- **Modo de cuenta:** `provision-http.js:72` → `const isTrial = !stripeSubscriptionId;`. Cualquier alta sin
  suscripción es «prueba», incluida una cuenta de rescate para alguien que ya pagó.
- **Caducador de pruebas:** `~/nexux-clients/scripts/trial-expiry.js` **existe entero** (8.360 bytes,
  25-jul: migra `trialEndsAt`, expira, registra). **No hay cron ni nadie lo invoca.** (La v4 decía que no
  existía: error corregido.)
- **Listas blancas de planes:** `/provision` (l. 236) **sí** admite `equipo`; el `create-session` de la Pi
  (l. 1628) **no**, pero esa ruta no la usa nadie: `vercel.json` la reescribe a la Pi y aun así gana la
  función de la raíz. Alinearla igualmente para que la trampa no vuelva a morder.
- **Vercel `verifyStripeSignature`:** HMAC correcto, **sin tolerancia de tiempo**: acepta una firma
  válida de hace un año.

---

## 3. DISEÑO DEL WEBHOOK — dos endpoints directos, sin reenvíos (decisión de Ricardo, mantenida)

| Endpoint en Stripe | Eventos | Qué hace |
|---|---|---|
| `https://nexux.pro/api/webhook/stripe` (R1, Vercel) | **solo** `checkout.session.completed` | Llama a `POST /provision` de la Pi. Único motor que crea un cliente completo |
| `https://pi.nexux.pro/webhook/stripe` (R2, Pi — **una vez arreglado**) | `customer.subscription.updated` · `customer.subscription.deleted` · `invoice.payment_failed` · `invoice.payment_action_required` · `invoice.paid` | Ciclo de vida. Las ramas ya están escritas; `payment_failed` se hace idempotente |

- Cada servidor verifica con el secreto de **su** endpoint. Nadie reenvía firmas. **R4 se borra.**
- **El alta depende de la Pi.** Si la Pi cae, R1 responde 5xx y Stripe reintenta hasta 3 días.
- **R3 (`lib/admin.js:49`) se retira**: dos receptores en el mismo proceso es la misma clase de error que
  las dos listas blancas. Queda **uno** en `provision-http.js`, el que ve el túnel.

**Orden obligatorio:**
1. **D6** Auditar entregas recientes de los 2 endpoints actuales sin modificarlos (Stripe → Webhooks →
   cada endpoint → pestaña de intentos; anotar id, URL, eventos, versión de API).
2. **P2** Arreglar función y ruta de la Pi (apartado 4) y probarlas **en local con firma auténtica** antes
   de registrar nada.
3. **D7a** Crear en Stripe el endpoint de la Pi con sus 5 eventos y obtener su secreto. **El agente no
   escribe ni muestra secretos ni edita `.env`: Ricardo lo introduce y confirma.**
4. **D7b** Reenviar desde el panel de Stripe un evento real de suscripción: 200 con cuerpo intacto; 400 sin
   cabecera; 400 con un byte alterado; 400 con firma de hace >300 s.
5. **D7c** Reducir `we_1TYhnJ…` a `checkout.session.completed` y **borrar `we_1TXfnR…`** (el duplicado,
   identificado por id). Con autorización de Ricardo.

> ⚠️ **Riesgo a poner delante de Ricardo en D7, no antes:** el receptor de la Pi que ve internet **nunca ha
> funcionado**. Registrarlo en Stripe significa exponer y endurecer un receptor nuevo justo antes de la
> campaña. Existe una alternativa con menos superficie que respeta «no reenviar firmas»: un solo endpoint
> (R1) que, para los eventos de ciclo de vida, llame a la Pi por una ruta **interna** autenticada con el
> `PROVISION_SECRET` que ya existe (`X-Provision-Secret`, como `/provision`), pasando el evento ya
> verificado. Sin secreto nuevo, sin decisión #6, sin exponer la Pi a Stripe. **Se ejecuta el diseño de
> dos endpoints salvo que Ricardo, al ver esto en D7, elija la interna.** No es una parada nueva: D7 ya
> requería su OK.

---

## 4. LA PI — función primero, ruta después

**4.1 · `lib/stripe-webhook.js` — la firma se exige SIEMPRE.**
`if (secret && sigHeader)` → `if (!secret || !sigHeader || !verifyStripeSignature(secret, rawBody,
sigHeader)) return { status: 400, body: { error: 'invalid_signature' } }`. Sin secreto configurado =
cerrado, no abierto.
**4.2 · `provision-http.js` — la ruta recibe el cuerpo crudo.** Mover `app.post('/webhook/stripe',
express.raw({ type: 'application/json' }), …)` **por encima** de `app.use(express.json(…))` (l. 39), o
excluir esa ruta del parser JSON global. Mantener el `JSON.parse` con su 400 `invalid_json`.
**4.3 · `lib/admin.js:49` — retirar la ruta** (y el `app.use('/webhook', express.raw…)` de la l. 16 si
solo servía a esa). Twilio en `/webhook/twilio/:clientId` sigue donde está.
**4.4 · `invoice.payment_failed` idempotente:** dedup por `event.id` con el mismo `_processed_events.json`
(hoy solo lo usa la rama de compra). Sin eso, cada reintento de Stripe manda otro correo al cliente.
**4.5 · Vercel `verifyStripeSignature`:** añadir la tolerancia de 300 s que la Pi ya tiene.
**4.6 · Borrar `src/pages/api/webhook/stripe.ts`** (R4) y, ya puestos, `src/pages/api/leads/pro.ts` si se
confirma que `api/leads/pro.js` de la raíz es el que ejecuta (mismo patrón que W5).

**Verificación que no admite atajo:** test de regresión sobre la ruta REAL arrancando `provision-http.js`
en un puerto libre con `CLIENTS_DIR` apuntando a un directorio temporal (nunca a `clients/`), cuerpo
firmado con un secreto de prueba: 200 con firma correcta · 400 sin cabecera · 400 con un byte cambiado ·
400 con `t` de hace 301 s · el mismo `event.id` dos veces → segundo `duplicate:true`. **Sabotaje:** quitar
la línea `if (!secret …)` y comprobar que el test de «sin cabecera» se pone rojo.

---

## 5. EL ALTA — reintentos, idempotencia, un solo correo, el dato que falta

**5.1 · R1 devuelve 5xx si el alta no se confirma.** Hoy `provisionClient` devuelve `null` y el handler
responde 200. Cambio: si `/provision` no responde 2xx con `clientId`, **responder 503**. Stripe reintenta
con espera creciente durante 3 días. Se elimina `sendConfirmationEmail` («en 24 h te llamamos») y
`notifyProvisioningFailed` pasa a decir la verdad: «alta pendiente, Stripe reintentará; si en 1 h sigue
así, mirar la Pi». **Nada de «provisionar manualmente».**
**5.2 · Idempotencia con estados.** La Pi ya resuelve por `stripeSessionId` (`findBySession`, disco). Se
completa con estado explícito en el índice: `provisioning` → `completed` | `failed_retryable`, y solo
`completed` cuando cliente + correo estén hechos. Dos reintentos concurrentes con el mismo
`stripeSessionId`: el segundo espera o devuelve `alreadyProvisioned`; nunca dos directorios.
**5.3 · Un único correo, y lo manda la Pi.** Se elimina `sendOnboardingEmail` de R1. En `/provision` el
correo pasa a **antes** de `res.json`, con `await`, comprobando 2xx de Brevo, guardando
`welcomeEmailSentAt` + `messageId` en `config.json`. Si Brevo falla → estado `failed_retryable` y 503 hacia
R1 (Stripe reintenta; el reintento encuentra el cliente sin correo y **solo** manda el correo). Con correo
confirmado, un reintento no lo repite.
**5.4 · `notifyTelegram` de R1 y el aviso de pago de la Pi bajo la misma idempotencia:** hoy R1 avisa por
Telegram **antes** de saber si es un alta nueva y en cada reintento. Pasa a avisar solo cuando `/provision`
devuelva `completed` sin `alreadyProvisioned`.
**5.5 · El dato que falta — «Nombre de tu negocio».** Campo obligatorio en el modal de compra (no en la
página de Stripe), antes de `openCheckout`. `checkout.ts` lo manda como `salon` en el body →
`create-session.js` ya lo mete en `metadata[salon]` → R1 ya lo lee. **No se toca Stripe.** Se conserva el
nombre interno `salon` en la tubería para no reescribir cuatro ficheros la víspera; el rótulo visible es
«Nombre de tu negocio». El guard `missing_fields` de la Pi (l. 232) se queda.
**5.6 · `maxDuration`:** no es causa de nada. Se puede declarar por higiene.

---

## 6. TELEGRAM — que la orden de reserva no pueda cortarse

1. `lib/telegram.js:195`: 150 → 450 (igualar a WhatsApp). **Solo esa línea**; hay otros «150» que no son
   este límite.
2. `lib/ai.js`: `chat()` pasa a devolver `{ text, finishReason }` (leyendo `data.choices[0].finish_reason`)
   **manteniendo compatibilidad**: los consumidores actuales que esperan string se adaptan en el mismo
   commit (grep de `await chat(` en `lib/`). Si algún proveedor del fallback de 9 no devuelve
   `finish_reason`, se declara `unknown` y se trata como posible corte.
3. Si `finishReason === 'length'` o el texto contiene `[RESERVA:` sin cerrar: **no se envía**; se reintenta
   una vez pidiendo solo la acción («responde únicamente con la etiqueta de reserva completa»), y si vuelve
   a fallar se manda un mensaje corto a la clienta y un aviso a Telegram del dueño. Una respuesta cortada
   nunca llega a la clienta.
4. Mismo tratamiento en `lib/whatsapp.js` y `lib/twilio.js`, que comparten el patrón.

**Verificación:** una reserva real de extremo a extremo por Telegram con una cuenta de pruebas de Ricardo:
cita en `appointments.json` **y** en Google Calendar, borrada después. Test unitario del detector de corte
con sabotaje (quitar la comprobación de `[RESERVA:` y ver rojo).

---

## 7. CONSENTIMIENTO Y LEGALES — Ola 1 (informe E, no re-medido en v5)

**7.1** El píxel de OpenAI se inyecta siempre (`Layout.astro:56-62` y `Medicion.astro`) y con
`nx_cookie_consent=rejected` sigue enviando (202). Cambio: no cargar el SDK hasta consentimiento; rechazar =
no cargar. **7.2** `/demo` no usa `Layout`: incluir **solo el componente del aviso** (no migrar la página
de 862 líneas la víspera). **7.3** Legales: la garantía de 30 días no está en ninguna condición
(`legal.astro:48` titula lo contrario); `/privacidad` no declara Umami, Plausible ni OpenAI; faltan NIF y
domicilio. **El agente redacta el borrador; Ricardo confirma datos y texto antes de publicar.**

---

## 8. PRUEBA GRATUITA Y MODO DE CUENTA — decisión cerrada

> Compras: sin prueba, garantía de 30 días. Demos manuales: 7 días. Alta manual de rescate para quien ya
> pagó: cuenta normal. No se promete trial en anuncios ni checkout.

- Stripe no se toca (`trial_period_days: null` en ambos precios es lo correcto).
- `provision-http.js:72`: sustituir `isTrial = !stripeSubscriptionId` por `accountMode: 'stripe_paid' |
  'manual_paid' | 'demo'` explícito y validado; solo `demo` recibe `trialEndsAt`. Migración de los
  clientes existentes por script con `--dry-run`.
- Barrido de la promesa de prueba en anuncios, checkout, web, correos, guion de Lara, panel. En la web
  pública E no la encontró; `CalculadoraCitas.astro` la tiene pero está muerta (`showCalculator={false}`).
- **Caducador:** enganchar `scripts/trial-expiry.js` a cron (`--dry-run` primero, luego real, con log y
  aviso Telegram) → **Ola 2, primera posición.** No hay que escribirlo.

---

## 9. PRUEBA DE ACEPTACIÓN — la cadena entera con el producto de 29 €

| # | Eslabón | Se comprueba |
|---|---|---|
| 1 | Pago | compra desde la web con la red del navegador grabando (cupón admitido, producto real) |
| 2 | Una cuenta | exactamente **un** directorio nuevo en `clients/` con `accessToken`, `limits`, `features`, plantilla, `active:true`, `accountMode:'stripe_paid'` |
| 3 | Un correo | exactamente **uno** (se cuentan los envíos en Brevo) con enlace del portal y QR |
| 4 | Portal | el enlace abre el portal con los datos del cliente |
| 5 | Canal | se conecta un canal desde el portal; se anota cuál |
| 6 | Cita | reserva real por ese canal en `appointments.json` **y** en Google Calendar |
| 7 | Cancelación | cancelar desde el portal de facturación; el evento llega al endpoint de la Pi (o a la ruta interna, si se eligió) |
| 8 | Desactivación | `active:false` **y el canal del paso 5 deja de responder**, y también `/public/:id/book` y el chat web |

Se registra cuántas veces entra cada `event.id` y que `/pub-api/book` responde. **Limpieza** solo del
cliente, suscripción, evento de calendario y datos creados en esta ejecución, con OK de Ricardo para
cancelar/reembolsar/borrar.

---

## 10. DESPLIEGUE — worktrees, preview, canario, vuelta atrás

- **Estado medido (3-sep 23:00):** `nexux-pro` main `71a2e03` = `origin/main`, 2 modificados
  (`AGENTS.md`, `progress/REGISTRO.md`) + ~30 sin rastrear (vídeo/publicidad/auditoría). `nexux-clients`
  main `efd9797`, **3 commits sin subir** (`44241c0`, `abd1c26`, `efd9797`), 1 modificado, 8+ sin rastrear.
- **Worktree web ya creado:** `~/nexux-pro-wt-ola1`, rama `task/ola1-lanzamiento-pro` desde `71a2e03`,
  con **W5 hecho** (`0bf1a1f`). Para la Pi: `git -C ~/nexux-clients worktree add ../nexux-clients-wt-ola1
  -b task/ola1-lanzamiento-clients efd9797` (incluye los tres commits de seguridad).
- Hay 6 worktrees `prunable` con rutas UNC rotas (`codex/*`) en `nexux-pro`: no estorban; no prunar sin OK.
- **Build en la Pi SIEMPRE con `NODE_OPTIONS=--max-old-space-size=1400`** (sin él tumbó la Pi; con él 55-89 s).
- **Preview:** la CLI de Vercel **no está instalada** en la Pi (hallazgo de la revisión, no re-medido).
  Comprobar `which vercel`; si no está, la previsualización se hace empujando la rama `task/…` a GitHub
  (Vercel crea preview por rama automáticamente si el proyecto lo tiene activado — verificar en el panel)
  **o** se declara «sin preview» y el canario post-deploy es la única red. No fingir una preview.
- **Despliegue:** un solo push a `main`, autorizado por Ricardo. Anotar antes el id del despliegue actual.
- **Canario:** `/`, `/demo` (aviso de cookies y píxeles), `/f/d1`, `/paquetes/recepcionista`,
  `/reservar/<id>` con `POST /pub-api/book`, portal de un cliente. 5 rondas en 5 min; 3 fallos → rollback.
- **Vuelta atrás:** web = promover el despliegue anterior en Vercel · Pi = `git revert` + reinicio
  controlado (**reinicio = OK explícito**, corta sesiones de WhatsApp) · Stripe = anotar id/URL/eventos
  antes de tocar.
- **La caché de Vercel:** el `?cb=` **no la salta** según la revisión (mismo ETag/Age). Verificar con
  `curl -H 'Cache-Control: no-cache'` y comparando `x-vercel-id`/`age`, o esperando la invalidación del deploy.

---

## 11. HECHO Y VERIFICADO (no rehacer)

| Qué | Evidencia | Commit |
|---|---|---|
| Panel `/admin/*` con clave por defecto en el código | 401 sin clave / clave vieja; 200 con la nueva | `abd1c26` |
| Enlace de dueño de Telegram = id público → escritura arbitraria de ficheros | 19 pruebas + sabotaje | `efd9797` |
| `PRICE_TO_PLAN` sin 29/79 | 111/111 tests con control positivo | `44241c0` |
| Copia de sistema del 24-ago fuera del patrón de rotación | `CONSERVAR-pi-sistema-20260824.tar.gz`, 23,34 GB | — |
| **W5** `/api/book` y `/api/analytics/ob` → `/pub-api/*` | manifest de Vercel publica las nuevas y no la vieja; build 55 s | `0bf1a1f` (worktree, sin push) |

---

## 12. OLA 1 — orden de ejecución (tiempos reales, no promesas)

### BLOQUE PI · `~/nexux-clients-wt-ola1`
| # | Qué | Fichero:línea | h |
|---|---|---|---|
| P1 | Monitor de `pi.nexux.pro/health` en Uptime Kuma con Telegram **+ uno externo** (Kuma vive en el mismo disco USB que falla) | — | 0,25 |
| ~~P2~~ | **HECHO** (sesion anterior) — firma siempre + ruta raw + retirar R3 + payment_failed idempotente | — | — |
| ~~P3~~ | **HECHO** (sesion anterior) — Telegram 450 + finishReason + detector de corte | — | — |
| ~~P4~~ | **HECHO** (sesion anterior) — config.active en todos los puntos de entrada | — | — |
| ~~P5~~ | **HECHO** (sesion anterior) — accountMode explicito + migracion | — | — |
| ~~P6~~ | **HECHO** `2118542` — correo esperado y anotado, 503 reintentable, estados en el indice, cerrojo por sesion. 7 tests + sabotaje | — | — |

### BLOQUE DINERO · Vercel (`~/nexux-pro-wt-ola1/api/`) + Stripe
| # | Qué | Fichero | h |
|---|---|---|---|
| ~~D1~~ | **HECHO** `371955a` — campo «Nombre de tu negocio» en el modal; viaja a metadata[salon] | — | — |
| ~~D2~~ | **HECHO** `371955a` — 503 si el alta no confirma, exige clientId, sin correos, ventana 300 s, Telegram solo en alta nueva | — | — |
| ~~D3~~ | **HECHO** `371955a` — borrados R4 (reenviaba la firma) y leads/pro.ts (secreto en el codigo) | — | — |
| ~~D4~~ | **HECHO** `2118542` — lista blanca de la Pi con equipo | — | — |
| ~~D6~~ | **HECHO** — auditados los eventos reales en solo lectura: 0 entregas pendientes, 0 compras completadas en los ultimos 100 eventos, 31 checkout.session.expired; el customer.subscription.updated que ocurrio lo recibio Vercel y lo ignoro (confirma 2.4) | — | — |
| D7 | a) endpoint de la Pi + secreto (Ricardo) · b) evento real reenviado: 200/400/400/400 · c) reducir R1 a `checkout.session.completed` y borrar `we_1TXfnR…` | Stripe | 1 |

### BLOQUE WEB · `~/nexux-pro-wt-ola1` — un solo despliegue
| # | Qué | h |
|---|---|---|
| W1 | Portal: enlace caducado → 500 y bucle; resolver sin debilitar auth; probar token válido/inválido/ausente/cruzado | 0,5 |
| W2 | Componente del aviso de cookies en `/demo` | 0,5 |
| W3 | Píxel de OpenAI solo con consentimiento; rechazar = rechazar | 0,75 |
| W4 | UTM antes de deducir el origen + guardar `utm_content` | 0,5 |
| ~~W5~~ | **HECHO** `0bf1a1f` | — |
| W6 | QR de Telegram: `is:inline` | 0,25 |
| W7 | Borrador legal (7.3); Ricardo confirma antes de publicar | 0,75 |
| W8 | Citas del portal: crear/editar/arrastrar con zona horaria de la fecha objetivo; probar verano e invierno | 1,5 |

### CIERRE
Build → (preview si existe) → push autorizado → canario → **prueba de aceptación (apartado 9)** → limpieza.

**Total realista: 18-22 h de trabajo** más esperas de Ricardo (secreto, push, cobro, datos legales).
Son dos o tres días. No prometer uno.

### En qué orden quedarse a medias es peor que no tocar
1. Arreglar la ruta raw de la Pi (4.2) **antes** que la función (4.1): abre el agujero a internet.
2. Registrar la Pi en Stripe antes de D7b.
3. Borrar un endpoint de Stripe antes de D6.
4. Desplegar el alta nueva sin haber probado reintento y correo.
5. Marcar `completed` antes de cliente + correo.

---

## 13. OLA 2
1. Cron de `scripts/trial-expiry.js` (existe; falta ejecutarlo) con aviso previo.
2. ~~Portal del cliente de 79 € dice 749 €/mes~~ **HECHO** `694352e` — idea explicita de «planes en catalogo»; verificado renderizando la pagina SSR real (equipo ve 79€, cero apariciones de 749/449/249; el cliente antiguo ve el suyo con aviso de plan retirado).
3. ~~Subir a Equipo no crea las agendas por profesional~~ **HECHO** `2b3049f` — se monta al subir, respetando lo que el dueno ya tuviera y sin borrar nada al bajar. 5 tests + sabotaje.
4. Copias fuera de casa (Duplicati apunta a carpeta borrada desde el 9-may) · disco USB como punto único.
5. Secretos publicados en GitHub (21 valores en `origin/master` de `/home/nexux`): comprobar cuáles siguen
   activos sin imprimirlos, rotar, hook `pre-push`. Es puerta de seguridad, no mejora.
6. Twilio no reserva (`parseActions = undefined`) · horarios duplicados · Telegram acepta nombres inventados ·
   Markdown crudo en el widget · móvil del portal · token del cliente en el HTML · `helmet` y rate limit ·
   journal volátil · logs sin rotación.
7. Los 6 worktrees `prunable` de `nexux-pro`.

---

## 14. LO QUE ESTÁ BIEN (comprobado)
Lara crea citas reales que llegan a Google Calendar con la hora correcta · 111/111 tests · precios
correctos en Stripe live y en la web · el QR de octavilla deja una fila identificable en Umami · aislamiento
entre clientes probado (401 y listas vacías con cookie ajena) · web pública sin enlaces rotos y rápida ·
ficheros restaurados con hash idéntico (la copia completa más reciente estaba truncada) · 18 min de caída
en 14 días · **el panel admin y el enlace de dueño ya cerrados** · **`/pub-api/book` ya existe en el build**.

---

## 15. VERIFICACIÓN (innegociable)
1. Nombrar el fichero que **EJECUTA** y demostrarlo con una petición real.
2. Todo test se sabotea antes de creérselo.
3. Cierre: `export NEXUX_AGENT=opus && python3 ~/scripts/nexux-verify.py service:nexux-clients
   url:https://pi.nexux.pro/health url:https://nexux.pro syntax:<fichero>` + línea en el quality-ledger.
   (`gitclean:` dará FALLO mientras main esté sucio — usar el worktree, no «limpiar» main.)
4. Antes de preview/deploy: tests + sabotaje + `node --check` + build con `NODE_OPTIONS`.
5. Commit por arreglo, en el worktree. **El push lo autoriza Ricardo.**
6. Canario de 5 rondas; 3 fallos → rollback.
7. Lo no comprobado se declara **NO VERIFICADO**.

---

## 16. DECISIONES PENDIENTES DE RICARDO

| # | Decisión | Estado |
|---|---|---|
| 1 | Autorizar UN push a `nexux-pro` (worktree, canario, vuelta atrás anotada) | Pendiente. Sin él no existe ningún arreglo web, W5 incluido |
| 2 | ¿El botón de comprar sigue abierto mientras se arregla el alta? | Pendiente. Hoy quien paga no existe (apartado 2.3) |
| 3 | Prueba gratuita | ✅ cerrada (apartado 8) |
| 4 | Rotar los 21 secretos publicados | Pendiente (Ola 2, puerta de seguridad) |
| 5 | Endpoints de Stripe: diseño de dos endpoints (mantenido) **o** la ruta interna del aviso del apartado 3 | Se decide en D7, con los datos de D6 delante |
| 6 | Introducir el secreto del endpoint de la Pi | Solo si se mantiene el diseño de dos endpoints |
| 7 | Compra, cancelación, reembolso y borrado del cliente de prueba | OK justo antes de ejecutar |
| 8 | NIF, domicilio y texto de garantía | Antes de publicar W7 |
| 9 | Reinicio de `nexux-clients` para aplicar el bloque PI | OK explícito (corta sesiones de WhatsApp; hacerlo fuera de horario de los 3 clientes activos) |

---

## 17. BRIEFING PARA OPUS (ejecutor)

Arrancas en frío. **Verifica en el código/servidor real antes de afirmar nada — no asumas por memoria
guardada ni por este documento.** Lee `~/nexux-pro/AGENTS.md` entero (sobre todo §5 y §7),
`~/nexus-brain/AGENTS.md`, las últimas 30 líneas de `~/nexux-pro/progress/REGISTRO.md` y el briefing de
traspaso en `C:\Users\Nexux\Desktop\BRIEFING-CLAUDE-CONTINUAR-NEXUX-PRO.md` (lleva el estado medido, las
trampas y las prohibiciones). Después, este PRP. Ejecuta la Ola 1 en el orden del apartado 12; cada tarea
con: hallazgo → fichero que ejecuta → cambio mínimo → test + sabotaje → verificación real → commit en el
worktree sin push → línea en `progress/REGISTRO.md`. Para en cada decisión del apartado 16 y pide **esa**
autorización, no una genérica. Lo que no puedas comprobar, dilo con esas palabras.

---

## 18. ESTADO
- [x] Fase 1 — auditoría de 7 áreas · 3-sep
- [x] Fase 2 — consolidación y tabla cruzada
- [x] Ola 0 — dos agujeros cerrados; copia de sistema a salvo
- [x] v1→v4 · revisión adversarial de v4 (6 lentes; refutación parcial por límite de sesión)
- [x] **v5 — camino del dinero re-medido en el código que ejecuta; diagnóstico reescrito; diseño cerrado**
- [x] W5 hecho en worktree (`0bf1a1f`)
- [x] Ola 1 — **completa salvo dos cosas que dependen de Ricardo**: P1 (monitor de caida, necesita Uptime Kuma y un vigilante externo) y D7 (endpoint de la Pi en Stripe, su secreto, y borrar el duplicado `we_1TXfnR…`)
- [x] Prueba de la cadena entera SIN cobrar (`3bccdc7`): pago → UNA cuenta completa y activa → UN correo con su enlace → el enlace abre el portal y un token inventado no → doble entrega no duplica → con la Pi caida se pide reintento → cancelar desactiva → una baja sin firma se rechaza. Eslabones 1-4 y 7-8 de la aceptacion, en verde
- [ ] Prueba de aceptacion REAL (apartado 9): necesita el push, un cobro de 29 € y un canal conectado. Todo eso lo autoriza Ricardo
- [~] Ola 2 — hechos los puntos 2 y 3; el resto pendiente

---

## D7 — CERRADO EL 4-SEP-2026, Y LA CAUSA NO ERA NINGUNA DE LAS PREVISTAS

Este apartado se escribió suponiendo que el receptor de la Pi «nunca ha funcionado» y que el
riesgo estaba en exponerlo. **El diagnóstico era incorrecto.** Lo que no funcionaba eran los
**dos** endpoints, y por una razón que este PRP no contempla en ninguna línea:

> Ambos estaban clavados a `api_version 2026-04-22.dahlia`. La cuenta opera en
> `2025-08-27.basil`. Cuando Stripe no puede representar un evento en la versión que pide el
> endpoint, **no lo entrega y no lo reintenta**: sin error, sin traza, sin reintento.

Consecuencia: **el alta automática no funcionó ni una sola vez desde el 19-may-2026.** Los tres
clientes activos se dieron de alta a mano — por eso ninguno tiene `stripeCustomerId`.

Lo que este PRP daba por hecho y era falso:

| Suposición del PRP | Realidad medida |
|---|---|
| «el receptor de la Pi nunca ha funcionado» | ninguno de los dos funcionaba, y no por el código |
| D6 «0 entregas pendientes» se leyó como *todo entregado* | significaba *nadie reclamó ningún evento* |
| D7b: reenviar un evento desde el panel bastaría como prueba | no habría probado nada: el problema estaba antes de la entrega |
| el riesgo era exponer la Pi a internet | la Pi respondía bien; el riesgo real era invisible y estaba en Stripe |

**Cómo quedó (todo verificado, ver `INCIDENTE-WEBHOOKS-STRIPE-20260904.md`):**

- `we_1UBtum2SQwDzHtsF0l8UOnuj` → Pi, 5 eventos de ciclo de vida, versión heredada de la cuenta.
- `we_1UBuBE2SQwDzHtsFzwx5YKm8` → Vercel, solo `checkout.session.completed`, `2025-08-27.basil`.
- `we_1TYhnJ…` (el de `dahlia`) **borrado**, con relevo comprobado antes de borrar.
- Se ejecutó el diseño de **dos endpoints**; la alternativa de ruta interna no hizo falta.
- Compra real de 29 € reproducida por el camino real: cuenta `prueba-nexux-pro-c43c20`,
  `accountMode: stripe_paid`, primer cliente con identificador de Stripe.

**La regla que sale de aquí, y que este PRP debería haber tenido:** al crear un endpoint por API
**no pasar `api_version`**. Y `pending_webhooks: 0` recién nacido un evento **no es éxito**: es
que nadie lo reclamó.
