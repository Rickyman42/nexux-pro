# ÁREA B — COMPRA Y ALTA DE CLIENTES

Auditoría de lanzamiento nexux.pro · 3-sep-2026 · Todo verificado en esta sesión contra producción y la Pi.

## 1. Veredicto

**NO. No se puede lanzar hoy.**

Cobrar funciona perfectamente (29 € y 79 € en Stripe live, precios correctos), pero **nadie se da de alta**: el sistema que crea al cliente exige un dato ("nombre del salón") que la web nunca envía, así que el guardián lo rechaza siempre y no llega a ejecutarse.

Peor: **el arreglo de hoy sobre los cambios de plan no está en el camino real**. Los eventos de Stripe no van a la Pi, van a una función en Vercel que solo escucha "pago completado" e ignora cancelaciones, subidas/bajadas de plan y pagos fallidos.

---

## 2. Tabla de comprobaciones

| # | Qué | Cómo | Estado | Evidencia |
|---|---|---|---|---|
| 1 | Checkout `recepcionista` | `curl POST https://nexux.pro/api/stripe/create-session -d '{"plan":"recepcionista"}'` | **OK** | HTTP 200, `clientSecret` `cs_live_...` |
| 2 | Checkout `equipo` | ídem con `equipo` | **OK** | HTTP 200, `cs_live_...` |
| 3 | Planes inválidos (`starter`, vacío, `RECEPCIONISTA`, inyección `"; DROP`, body vacío) | 5 curl | **OK** | Los 5 → HTTP 400 `{"error":"invalid_plan"}` |
| 4 | Precio real cobrado en `recepcionista` | `GET /v1/checkout/sessions/<id>?expand=line_items` con la clave live | **OK** | `price_1U6jqd2SQwDzHtsFf3wEcuQe`, 2900, EUR, `interval: month`, `active: true`, `prod_V6xlRvLwrMTEJF` |
| 5 | Precio real cobrado en `equipo` | ídem | **OK** | `price_1UBHkE2SQwDzHtsFTVWQ67l5`, 7900, EUR, month, active, `prod_VBf4ODSQteOaIk` |
| 6 | Trial de 7 días en el checkout | mismo `GET` | **FALLO** | `subscription_data.trial_period_days: null` y `recurring.trial_period_days: null` en ambos precios. Se cobra íntegro el día 1 |
| 7 | Qué endpoint sirve el checkout de producción | Comparar `nexux.pro` vs `pi.nexux.pro` vs `localhost:3460` | **FALLO (drift)** | `nexux.pro` → `Server: Vercel`, acepta `equipo`. `pi.nexux.pro` y `localhost:3460` → `x-powered-by: Express`, **rechazan `equipo`**. Son backends distintos |
| 8 | Endpoint vivo localizado | `ls ~/nexux-pro/api/stripe/` | OK (hallado) | `/home/nexux/nexux-pro/api/stripe/create-session.js` (función Vercel de raíz, gana al rewrite de `vercel.json`) |
| 9 | `STRIPE_WEBHOOK_SECRET` presente en la Pi | `sed 's/=.*/=<set>/' .env` | **OK** | Presente (valor no mostrado) |
| 10 | Firma verificada en el webhook vivo (Vercel) | `curl POST` sin firma a los 2 endpoints | **OK** | Ambos → HTTP 400 `{"error":"invalid_signature"}` |
| 11 | Validación del timestamp en el webhook vivo | Lectura de `api/webhook/stripe.js` | **FALLO** | No comprueba antigüedad de `t`: un evento firmado válido se puede reenviar indefinidamente |
| 12 | Firma verificada en el webhook de la Pi | Simulación con handler real, cwd `/tmp/auditB` | **FALLO** | Con secreto presente y **sin cabecera** `stripe-signature` → creó el cliente y devolvió HTTP 200 |
| 13 | Webhook de la Pi expuesto a Internet | `curl POST https://pi.nexux.pro/webhook/stripe` | **FALLO** | Responde (`invalid_json` ante body no-evento). Es alcanzable sin autenticación |
| 14 | Idempotencia por `event.id` (Pi) | Simulación, mismo evento 2 veces | **OK** | 2.ª vez → `duplicate event evt_sim_3 — skipped`. Se marca antes de efectos, sin `await` intermedio |
| 15 | Idempotencia en el webhook vivo (Vercel) | Lectura de `api/webhook/stripe.js` | **FALLO** | No existe. Sin dedupe por `event.id` |
| 16 | Endpoints registrados en Stripe | `GET /v1/webhook_endpoints` | **FALLO** | 2 activos, **ambos resuelven a la misma función Vercel**: `/api/webhook/stripe` (6 eventos, api 2026-04-22.dahlia) y `/webhook/stripe` (solo `checkout.session.completed`, api 2025-08-27.basil). Un 3.º `nexux.es/?wc-api=wc_stripe` está `disabled` |
| 17 | Ramas `subscription.updated` / `.deleted` / `invoice.payment_failed` en producción | Lectura del handler vivo | **FALLO** | La función Vercel solo trata `checkout.session.completed`; el resto devuelve `{received:true}` sin hacer nada |
| 18 | `PRICE_TO_PLAN` con los 2 precios vivos | `grep lib/stripe-webhook.js` | OK en el fichero / **inerte** | Los 2 precios están (commit 44241c0), pero ese fichero no recibe eventos de Stripe |
| 19 | La provisión se ejecuta tras pagar | Lectura de `provisionClient()` + inspección de la sesión real + barrido de bundles en producción | **FALLO** | Guard `if (!payload.plan \|\| !payload.salon \|\| !payload.telefono) return null`. `salon` sale de `sessionStorage.laraData`, que **ningún script del sitio escribe** |
| 20 | Nadie escribe `laraData` | `grep setItem` en `src/` + descarga de los 6 bundles `_astro` de `/`, `/demo`, `/paquetes/recepcionista`, `/paquetes/equipo` | **FALLO confirmado** | Solo aparece la lectura (`JSON.parse(sessionStorage.getItem("laraData")\|\|"{}")`). Cero escrituras |
| 21 | La sesión de Stripe lleva `metadata.salon` | `GET` de la sesión creada por el flujo real | **FALLO** | `metadata: {plan: "recepcionista"}` únicamente. `custom_fields: []` |
| 22 | Cliente duplicado con el mismo email | Simulación, 2 eventos distintos mismo email | **FALLO** | Creó 2 directorios. No hay comprobación por email ni por `customer` |
| 23 | Fallback si falta `metadata.plan` (Pi) | Simulación | **FALLO** | Cae en `starter` — plan retirado de 249 € |
| 24 | Config generado por el webhook de la Pi | Simulación, volcado del `config.json` | **FALLO** | Sin `accessToken`, `limits`, `features`, `channels`, `timezone`, `isTrial`, `slug`, plantilla. `active:false`, sin `appointments.json` ni `conversations.json`, sin registrar en el índice |
| 25 | Config generado por `/provision` (camino bueno) | Lectura de `buildClientConfig` | **OK** | Plantilla `_base`+plan, `accessToken`, `isTrial`/`trialEndsAt`, `slug`, `channels`, equipo si procede |
| 26 | Entropía del `accessToken` | `lib/utils.js` + config real | **OK** | `randomBytes(32).toString('hex')` = 64 hex = 256 bits |
| 27 | Aviso a Ricardo si falla la provisión | Lectura de `notifyProvisioningFailed()` | **OK** | Telegram con todos los datos + instrucción de alta manual, y email genérico al cliente |
| 28 | Batería de tests | `node --test 'test/*.test.mjs'` (load 2.69 antes) | **OK** | `# tests 111 / # pass 111 / # fail 0` en 31,6 s |
| 29 | Clave Brevo viva | `GET https://api.brevo.com/v3/account` | **OK con reserva** | HTTP 200, cuenta Nexux. **Plan free: 300 envíos/día** |
| 30 | `resend-link` con email que no coincide | `curl` + `pm2 logs` | **OK** | `[resend-link] nexux-demo-mostoles-42a928: el email no coincide con el dueno — no se envia` |
| 31 | `resend-link` con cliente inexistente | ídem | **OK** | `[resend-link] no-existe-abc: cliente inexistente`. Respuesta neutra siempre (no filtra qué emails existen) |
| 32 | Portal `/status` con token real | `GET /client/nexux-demo-mostoles-42a928/status` con Bearer | **OK** | `plan: recepcionista`, `capacidades` correctas (ambas false), `timezone: Europe/Madrid`, `active: true`, `conversationLimit: 1000`, `billing`, `channels` |
| 33 | Caducidad del trial | `ls lib/trial*`, `crontab -l`, `grep trialEndsAt` | **FALLO** | **No existe** `lib/trial-expiry.js` ni cron. `trialEndsAt` solo se pinta en el panel de admin |
| 34 | El bot para al cancelar | `grep active lib/whatsapp.js` | **FALLO** | `whatsapp.js` no consulta `config.active`. Solo `scheduler.js` (3 sitios) y el arranque de `index.js` |
| 35 | Mini-web del cliente al cancelar | `templates/*.json` | **N/A** | `features.miniWeb: false` en `recepcionista` y `equipo`: no se genera web que retirar |
| 36 | Upgrade a `equipo` aplica `professionals`/`booking.mode` | Lectura de la rama `subscription.updated` | **FALLO** | Solo copia `limits` y `features` del template. No crea `professionals` ni pone `booking.mode: 'team'` |
| 37 | Coherencia de precios en la web pública | `curl` del portal live + grep de bundles | **OK** | El portal desplegado muestra `29€/mes` y los planes Recepcionista/Equipo. Cero `249€/449€/749€` |
| 38 | Guion de Lara / Noa | `lib/bot-prompt-lara.js`, `lib/bot-prompt.js` | **FALLO parcial** | Bien el rechazo de 249/449/749, pero línea 24: *"No hay planes ni versiones: es un único producto"* — falso desde que existe Equipo 79 € |
| 39 | Clientes reales intactos | `ls clients/` tras la simulación | **OK** | Los 3 clientes citados intactos; la simulación vivió y murió en `/tmp/auditB` |

---

## 3. Hallazgos por severidad

### BLOQUEANTE

**B1 — Nadie se da de alta al pagar. El alta automática nunca llega a ejecutarse.**
*Causa:* en `/home/nexux/nexux-pro/api/webhook/stripe.js`, la función `provisionClient()` corta antes de llamar a la Pi:
```js
if (!payload.plan || !payload.salon || !payload.telefono) {
  console.error('[webhook] insufficient metadata for auto-provisioning:', payload);
  return null;
}
```
`payload.salon` viene de `session.metadata.salon`, que a su vez viene de `sessionStorage.getItem('laraData')` en `/home/nexux/nexux-pro/src/scripts/checkout.ts:35`. **Ningún script del sitio escribe `laraData`.** Barrido exhaustivo: `grep setItem` en todo `src/` (solo `laraSessionId`, `nx_cookie_consent`, `crm-*`, `portal-email`) y descarga de los 6 bundles `_astro` servidos por `/`, `/demo`, `/paquetes/recepcionista` y `/paquetes/equipo` buscando `setItem("laraData"` → cero coincidencias. Solo existe la lectura.
*Reproducción:* la sesión creada por el flujo real de la web devuelve `metadata: {plan: "recepcionista"}` y `custom_fields: []`. Sin `salon`.
*Impacto:* el cliente paga 29 €, recibe el email genérico "te contactamos en menos de 24 h" y **no existe como cliente**. Cada alta es manual. Ricardo recibe la alerta de Telegram (eso sí funciona), pero el producto no es autoservicio.
*Propuesta (elegir una, la 1 es la mínima):*
1. Pedir el nombre del salón **en el propio Checkout de Stripe**, con un campo personalizado, y leerlo del `custom_fields` en el webhook. Añadir en `api/stripe/create-session.js`:
```js
params.append('custom_fields[0][key]', 'nombre_salon');
params.append('custom_fields[0][label][type]', 'custom');
params.append('custom_fields[0][label][custom]', 'Nombre de tu salón');
params.append('custom_fields[0][type]', 'text');
```
y en `api/webhook/stripe.js`, dentro de `provisionClient`:
```js
const salonField = (session.custom_fields || []).find(f => f.key === 'nombre_salon');
salon: md.salon || salonField?.text?.value || null,
```
2. Además, degradar el guard: si falta `salon`, usar el nombre del pagador en vez de abortar el alta.
*Esfuerzo:* 1 h más una compra real de prueba.

**B2 — Cancelaciones, cambios de plan y pagos fallidos se ignoran en producción. El arreglo de hoy no está en el camino real.**
*Causa:* Stripe entrega a `https://nexux.pro/api/webhook/stripe` y `https://nexux.pro/webhook/stripe`. Ambos resuelven a la misma función Vercel `api/webhook/stripe.js`, que solo trata `checkout.session.completed`. Todo el manejo de `customer.subscription.updated` / `.deleted` / `invoice.payment_failed` / `invoice.paid` vive en `~/nexux-clients/lib/stripe-webhook.js`, en la Pi, **a la que Stripe no envía nada**.
*Reproducción:* `GET /v1/webhook_endpoints` no lista ninguna URL de `pi.nexux.pro`. Y `POST` sin firma a los dos endpoints de `nexux.pro` devuelve `{"error":"invalid_signature"}` (respuesta de la función Vercel), mientras que la Pi devuelve `{"error":"invalid_json"}` — handlers distintos.
*Impacto:* quien cancele sigue con el servicio activo indefinidamente. Quien suba de 29 a 79 € paga la tarifa nueva y se queda con las funciones de la vieja — exactamente el fallo que se creyó arreglado hoy en el commit `44241c0`. Quien deje de pagar no recibe aviso ni se le corta. El test `test/precios-mapeados.test.mjs` pasa y refuerza esa creencia falsa: valida el fichero inerte.
*Propuesta:* decidir un único dueño del webhook. Lo más limpio es que la función Vercel reenvíe **todo** el evento a la Pi (`/webhook/stripe`) preservando el `rawBody` y la cabecera `stripe-signature`, y que la Pi sea la única que decide. Alternativa rápida: portar a `api/webhook/stripe.js` las tres ramas que faltan. Sea cual sea, el test debe validar el fichero que ejecuta.
*Esfuerzo:* 3-4 h.

**B3 — Cada compra dispara el webhook dos veces y no hay deduplicación en el camino vivo.**
*Causa:* los dos endpoints registrados traen `checkout.session.completed` y ambos llegan a la misma función Vercel, que no guarda `event.id` procesados (a diferencia de la Pi, cuya idempotencia sí verifiqué: `duplicate event evt_sim_3 — skipped`).
*Impacto:* dos emails de bienvenida al cliente, dos avisos a Telegram y dos llamadas simultáneas a `/provision`. La idempotencia de `/provision` es por lectura previa (`findBySession`) sin bloqueo: si las dos llegan a la vez, ambas leen "no existe" y se crean **dos clientes** con dos bots de WhatsApp para el mismo pago.
*Propuesta:* borrar en Stripe el endpoint `we_1TXfnR2SQwDzHtsFrJdcPMhH` (`https://nexux.pro/webhook/stripe`, el viejo, api 2025-08-27.basil). Es redundante: el otro trae los mismos eventos y más. Además, añadir dedupe por `event.id` allí donde se procese.
*Esfuerzo:* 10 min el borrado; 1 h el dedupe.

**B4 — El webhook de la Pi acepta eventos sin firma desde Internet.**
*Causa:* `lib/stripe-webhook.js` línea ~215: `if (secret && sigHeader) { ...verificar... }`. Si falta la cabecera, **no se verifica nada** y se procesa el evento.
*Reproducción (simulada en `/tmp/auditB`, nunca contra `clients/` real):* con `STRIPE_WEBHOOK_SECRET` presente y sin cabecera `stripe-signature`, el handler devolvió `{"status":200,"body":{"ok":true,"clientId":"equipo-auditbevtsim-mtljcch9"}}` y creó el directorio. Con firma basura sí rechazó (400). El endpoint es alcanzable: `POST https://pi.nexux.pro/webhook/stripe` responde.
*Impacto:* cualquiera puede crear clientes y disparar emails y avisos de Telegram en producción. No hay path traversal (el `clientId` se sanea con `[^a-z0-9]`), pero sí escritura de directorios y ruido ilimitado.
*Propuesta (trivial):*
```diff
-  if (secret && sigHeader) {
-    if (!verifyStripeSignature(secret, rawBody, sigHeader)) {
+  if (!secret || !sigHeader || !verifyStripeSignature(secret, rawBody, sigHeader)) {
       console.warn('[stripe-webhook] invalid signature');
       return { status: 400, body: { error: 'invalid_signature' } };
-    }
   }
```
*Esfuerzo:* 15 min. Hacerlo aunque se resuelva B2.

### ALTA

**A1 — No hay prueba gratuita. Se cobra 29 € el día 1.**
Verificado en Stripe: `trial_period_days: null` en los dos precios y `subscription_data.trial_period_days: null` en las sesiones. En el código, `isTrial` se calcula en `buildClientConfig` como `!stripeSubscriptionId` — es decir, **solo hay trial en las altas manuales sin Stripe**; quien paga nunca tiene trial. La regla de negocio (7 días) no está implementada en ninguna capa del cobro. Decidir: o se retira la promesa de los textos, o se añade `subscription_data[trial_period_days]=7` en `api/stripe/create-session.js`. Esfuerzo: 30 min.

**A2 — El trial no caduca nunca.**
No existe `lib/trial-expiry.js` ni ningún cron (`crontab -l` solo tiene `vigilante-calendario.mjs`). `trialEndsAt` se escribe al crear y solo se lee para pintar un contador en el panel de admin (`provision-http.js:1489-1501`) y en `/status`. Nadie desactiva ni avisa. Esfuerzo: 3 h (script + cron + aviso).

**A3 — Tres implementaciones divergentes del mismo endpoint de compra.**
`api/stripe/create-session.js` (Vercel, **el vivo**, acepta `recepcionista`+`equipo`); `provision-http.js:1621` (Pi 3460, acepta `starter/pro/total/promo/recepcionista` — **rechaza `equipo`**, verificado: HTTP 400); `lib/admin.js:64` (Pi 3458, solo `starter/pro/total/promo`). Y `lib/stripe-session.js` sigue con el catálogo de 249/449/749 y un `return_url` a `/paquetes/<plan>` que ya no es el vivo (el real es `/gracias?plan=<x>`). Cualquier cosa que apunte a la Pi para comprar el plan Equipo falla. Además, el `vercel.json` documenta un rewrite a la Pi que **no se aplica** (la función de raíz gana). Propuesta: borrar las dos implementaciones muertas de la Pi y el rewrite engañoso. Esfuerzo: 1 h.

**A4 — Al cancelar, el bot sigue respondiendo.**
`lib/whatsapp.js` no consulta `config.active` en ningún punto del flujo de mensajes. `active:false` solo lo respetan `scheduler.js` y el arranque de `index.js`. Un cliente cancelado sigue atendido hasta el siguiente reinicio del proceso. (Hoy es teórico porque B2 impide que `active` llegue a ponerse a `false`; al arreglar B2 se vuelve real.) Esfuerzo: 1 h.

**A5 — Subir a `equipo` no da lo que se paga.**
La rama `customer.subscription.updated` copia `limits` y `features` del template, pero no crea `professionals` ni pone `booking.mode: 'team'` — que es lo que distingue al plan de 79 €. En el alta sí se construyen, a partir del dato `trabajadoras` que recoge Lara (`lib/equipo-inicial.js`); en el upgrade posterior, no. El cliente pagaría 79 € y seguiría con una sola agenda. Esfuerzo: 2 h.

**A6 — `sendBrevoWelcome` no envía ningún email.**
En `lib/stripe-webhook.js`, pese al nombre, solo hace `POST /v3/contacts` (añadir a la lista). No hay `smtp/email`. En el camino vivo el email sí sale (`sendOnboardingEmail` / `sendConfirmationEmail` en la función Vercel), pero si se consolida el webhook en la Pi (B2) el cliente se quedaría sin bienvenida. Esfuerzo: 30 min.

### MEDIA

**M1 — El webhook vivo no valida el timestamp de la firma.** `api/webhook/stripe.js` comprueba el HMAC pero no la antigüedad de `t`. Un evento capturado se puede reenviar indefinidamente. La Pi sí lo hace (ventana de 300 s). Añadir la misma comprobación. 20 min.

**M2 — Fallback a plan retirado.** `plan = session.metadata?.plan || 'starter'` en `lib/stripe-webhook.js`. Verificado: un evento sin `metadata.plan` creó un cliente con plan `starter`. Debe abortar y avisar, no adivinar. 15 min.

**M3 — Clientes duplicados por email.** Verificado: dos eventos distintos con el mismo email crearon dos clientes. No se comprueba email ni `stripeCustomerId` previo. Al arreglar B1, decidir la política: ¿reactivar el existente o crear uno nuevo? 1 h.

**M4 — El guion de Lara niega el plan Equipo.** `lib/bot-prompt-lara.js:24`: *"No hay planes ni versiones: es un único producto"*. Falso desde que existe Equipo 79 €. Lara negará un producto que la web vende. 20 min.

**M5 — Brevo está en plan gratuito: 300 envíos/día.** Verificado contra `/v3/account`. Todos los emails del ciclo (bienvenida, enlace, pago fallido, cancelación) salen de ahí. Con campaña activa es un techo bajo y silencioso.

**M6 — `resend-link` pide el dato que el cliente ha perdido.** Exige `clientId` **y** `email`. Quien pierde el enlace ha perdido justamente el `clientId`. El registro por ramas es correcto y la respuesta es neutra (bien), pero la recuperación es inservible salvo que el cliente venga de `/cliente/<id>/login`. 1 h.

**M7 — Un test da confianza falsa.** `test/precios-mapeados.test.mjs` valida `lib/stripe-webhook.js`, el fichero que no recibe eventos. Pasa en verde mientras el fallo sigue vivo. Debe apuntar al fichero que ejecuta.

**M8 — Versiones de API distintas entre los dos endpoints.** `2026-04-22.dahlia` vs `2025-08-27.basil`. El mismo evento puede llegar con dos formas distintas al mismo handler. Se resuelve al borrar el endpoint viejo (B3).

### BAJA

- **Bj1** — `PLAN_LABELS` en `src/scripts/checkout.ts` solo tiene `recepcionista`. Al comprar Equipo, el modal muestra `equipo` en crudo en lugar de "Nexux Recepcionista Equipo — 79€/mes".
- **Bj2** — `lib/stripe-webhook.js` busca `custom_fields` con `key === 'nombre_salon'`, pero el checkout no pide ningún campo (`custom_fields: []` verificado). `salon_name` es siempre `null`.
- **Bj3** — Código muerto: `lib/admin.js` create-session, `lib/stripe-session.js` (catálogo 249/449/749 y `return_url` obsoleto), y el rewrite inoperante de `vercel.json`.
- **Bj4** — `escMd()` en `api/webhook/stripe.js` sustituye los caracteres Markdown por espacios en vez de escaparlos: un nombre con guion bajo llega deformado al aviso de Telegram.
- **Bj5** — ~19 directorios en `clients/`, la mayoría restos de pruebas (`peluqueria-carmen-e2e-*` ×5, `clinica-prueba-auditoria-*` ×2, `ricarda-*` ×2…). Conviene limpiar antes de tener clientes reales mezclados.

---

## 4. No verificado y por qué

1. **Variables de entorno en Vercel** (`NEXUX_CLIENTS_URL`, `PROVISION_SECRET`, `STRIPE_PRICE_*`, `BREVO_API_KEY`, `TELEGRAM_*`). No tengo acceso al panel de Vercel. Si `NEXUX_CLIENTS_URL` o `PROVISION_SECRET` faltasen, la provisión fallaría por un segundo motivo además de B1. **Comprobable sin pagar**: Ricardo puede mirarlas en el panel en 2 minutos.
2. **Contenido y entrega real de los emails.** He verificado que la clave de Brevo responde y he leído las plantillas, pero no he enviado ninguno: mandar correo en nombre de Ricardo requiere su permiso. La rama de éxito de `resend-link` queda sin probar de punta a punta (las dos de rechazo sí, con su línea de log).
3. **El portal tras un alta real.** Probado con el cliente existente `nexux-demo-mostoles-42a928` (creado a mano). Un cliente nacido de un pago real no ha podido existir nunca por B1.
4. **`trial_update_behavior`, prorrateo y bajadas programadas del portal de facturación** (`bpc_1ShYHb2SQwDzHtsFV5Zm5t9K`). Solo consulté precios, sesiones y endpoints en modo lectura. El comportamiento real exige una suscripción viva.
5. **La carrera de doble provisión (B3)** está deducida de la lectura del código (`findBySession` sin bloqueo), no reproducida: haría falta un pago real.

### Qué exige un pago real de 29 € y cómo lo probaría

Estos pasos **solo** se pueden verificar pagando:

- Que Stripe entregue de verdad `checkout.session.completed` a los dos endpoints y que llegue por duplicado (B3).
- Que `provisionClient()` corte por falta de `salon` y salte la alerta "PROVISIONING FAILED" a Telegram (B1).
- Que el cliente reciba el email genérico y no el de portal.
- Cancelar desde el portal de facturación y comprobar que **no** pasa nada (B2, A4).
- Cambiar 29 → 79 € y comprobar que el plan no se aplica (B2, A5).

**Prueba controlada propuesta, para que Ricardo decida:**
1. Antes de nada, aplicar B1 y B4 (son las dos baratas y las que hacen que la prueba tenga sentido).
2. Crear en Stripe un cupón del 100 % de un solo uso y limitado a una vez, o un precio de 1 € temporal, y permitir el campo de código promocional en el checkout. Coste real: 0-1 €. Si se prefiere no tocar Stripe, pagar los 29 € con la tarjeta de la empresa.
3. Comprar `recepcionista` desde la web, con el navegador abierto y las herramientas de red grabando.
4. Verificar en orden: aviso de Telegram; `ls -lt ~/nexux-clients/clients/ | head`; que el `config.json` nuevo tiene `accessToken`, `limits`, `features` y plantilla; el email recibido; y que el enlace del email abre el portal.
5. `pm2 logs nexux-clients` y los logs de la función en Vercel, buscando `insufficient metadata`, `provisioned` y cuántas veces entra el mismo `event.id`.
6. Desde el portal de facturación: subir a `equipo`, comprobar `plan`, `professionals` y `booking.mode` en el config; luego cancelar y comprobar `active:false` y que el bot deja de responder.
7. Cancelar la suscripción en Stripe y **reembolsar la factura** desde el panel. Borrar el cliente de prueba de `clients/`.

Presupuesto realista: 30 € recuperables y unos 40 minutos.

---

*Auditado por el agente del Área B. Todas las afirmaciones de este informe proceden de comandos ejecutados en esta sesión contra la Pi (192.168.0.120) y contra producción. La simulación de alta se ejecutó en `/tmp/auditB` con `cwd` aislado y se borró; los clientes reales no se tocaron. No se realizó ningún pago, ninguna escritura en Stripe, ningún `git push` ni ningún `pm2 restart`.*
