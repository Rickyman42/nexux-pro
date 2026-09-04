# PRP — Arreglo de lanzamiento nexux.pro · **v4 final revisada**

**Fecha:** 2026-09-03 · **Origen:** auditoría de 7 áreas del 3-sep (`~/nexux-pro/progress/auditoria-lanzamiento-20260903/` + `TABLA-CRUZADA.md`)
**Historial:** v1 rechazada por revisión adversarial (NO SIRVE) · v2 corregida · v3 incorporó las 10 correcciones de Ricardo, pero su revisión de Sonnet quedó interrumpida por límite de sesión · **v4 corrige los fallos residuales detectados contra el código ejecutable y cierra el diseño.**
**Regla de oro:** verifica el fichero que EJECUTA, no el que documenta. Todo test se sabotea antes de creérselo.
**🔴 La Ola 1 NO se ejecuta hasta que el agente nuevo vuelva a comprobar el estado real, confirme que esta v4 sigue vigente y haga una revisión adversarial breve antes de editar.**

---

## 1. PRIORIDAD

> El camino de los **29 €** tiene que funcionar: octavillas, anuncios, pagos, demo. **Alta automática.**

```
octavilla → QR → /f/dN → /demo → habla con Lara → paga 29 € → alta automática
   → UN correo → portal → conecta un canal → una cita → cancelación → desactivación
```

✅ La cadena ya no acaba en "el cliente entra al portal": acaba en **cancelación y desactivación**, porque esa es la prueba de aceptación (apartado 8). Eso tiene una consecuencia de alcance que hay que asumir: **el ciclo de vida de Stripe sube de la Ola 2 a la Ola 1.** No es opcional: sin él, la prueba final no se puede pasar.

---

## 2. ✅ DISEÑO DEL WEBHOOK — dos endpoints directos, sin reenvíos

Ni la opción A de la v1 (reenviar todo a la Pi) ni el reparto con reenvío crudo de la v2. **Dos endpoints registrados en Stripe, cada uno con su propio secreto de firma, sin que ninguno hable por el otro.**

| Endpoint en Stripe | Eventos suscritos | Qué hace |
|---|---|---|
| `https://nexux.pro/api/webhook/stripe` (Vercel) | **solo** `checkout.session.completed` | Llama a `POST /provision` de la Pi — el único motor que crea un cliente completo |
| `https://pi.nexux.pro/webhook/stripe` (Pi) | `customer.subscription.updated` · `customer.subscription.deleted` · `invoice.payment_failed` · `invoice.paid` | Cancelaciones, cambios de plan y pagos fallidos. Esas ramas **ya están escritas y probadas** en la Pi |

**Por qué así:**
- ✅ **Nadie reenvía firmas.** Cada servidor verifica con el secreto de *su* endpoint. Desaparece de golpe el bloqueante de la v2 (el secreto de la Pi pertenecía a un endpoint que ya no existe) y desaparece toda una clase de fallos: cuerpo alterado en el reenvío, cabecera perdida, doble verificación.
- **La recepción del evento queda en Vercel, pero el alta SÍ depende de la Pi.** Si la Pi cae, Vercel debe responder 5xx y Stripe reintentará el evento; la cuenta no existirá hasta que la Pi vuelva y `/provision` termine correctamente. No afirmar que el alta es independiente de la Pi.
- **Cada motor hace lo que sabe hacer.** El de la Pi detrás de `/webhook/stripe` (`lib/stripe-webhook.js:116`, `createClientDir()`) crea clientes **huecos y desactivados** y su `sendBrevoWelcome()` **no manda ningún correo**: por eso nunca debe recibir un pago. Sus ramas de suscripción, en cambio, son correctas.

**Orden obligatorio y reversible:**
1. Auditar URL, eventos y entregas recientes de los endpoints actuales sin modificarlos.
2. Corregir y probar la ruta raw de la Pi antes de registrarla en Stripe.
3. Crear el endpoint de la Pi y obtener su secreto propio. **El agente no escribe ni muestra secretos ni edita `.env`: Ricardo introduce el secreto por el mecanismo seguro y confirma cuando está.**
4. Enviar un evento auténtico de prueba y demostrar 200 con cuerpo intacto, 400 sin firma y 400 con un byte alterado.
5. Solo entonces limitar Vercel a `checkout.session.completed` y retirar el endpoint duplicado inequívocamente identificado, con autorización de Ricardo.

---

## 2 bis. 🔴 AÑADIDO EL 3-SEP 23:40 — HAY UN SEGUNDO RECEPTOR DE STRIPE QUE ESTE PLAN NO VIO

Verificado en el código real: además de `provision-http.js:1611` existe **otro**
`app.post('/webhook/stripe', ...)` en `~/nexux-clients/lib/admin.js:49`, montado sobre un servidor Express
distinto (`ADMIN_PORT || 3458`) que arranca `index.js:9` mediante `startAdmin`. Lee
`req.body.toString('utf8')`, hace `JSON.parse` y llama a `handleStripeWebhook(body, rawBody, sigHeader, ...)`.

**Consecuencia sobre este plan:** el apartado 3 arregla un único receptor. Ejecutarlo tal cual deja el
segundo intacto. Antes de tocar el webhook hay que medir tres cosas: (a) si el puerto 3458 es alcanzable
desde fuera (cloudflared / nginx / cortafuegos), (b) si `handleStripeWebhook` exige firma siempre o solo
cuando hay secreto, y (c) si ese servidor admin llega a arrancar en producción. Según la respuesta, el
arreglo es cerrar la ruta, unificar los dos receptores o dejarla documentada como interna. **No se da por
cerrado el trabajo de webhooks mientras este segundo receptor no esté resuelto por escrito.**

---

## 3 bis. ⚠️ EL APARTADO 3 ESTÁ EN DISPUTA — MEDIR ANTES DE ESCRIBIR CÓDIGO

Una revisión del 3-sep sostiene que la cadena causal del apartado 3 —el corazón técnico de este plan— es
falsa: que la ruta no verifica la firma contra un cuerpo equivocado, sino que **muere antes en `JSON.parse`
y devuelve 400 a todo evento**, y que el «200 sin firma» que la auditoría B le atribuyó salió de una
simulación a nivel de función, no de la ruta real.

**Esa revisión no llegó a verificarse**: la fase adversarial se cortó por límite de sesión. No se escribe
una línea del webhook hasta reproducir el comportamiento real de la ruta real y corregir este apartado con
la evidencia medida. Si la revisión tiene razón, el diseño del apartado 2 sigue siendo válido pero su
justificación cambia; si no la tiene, el apartado 3 se queda como está. Lo que no vale es codear sobre una
causa que nadie ha comprobado.

---

## 3. ✅ LA PI: LA RUTA DE STRIPE, ANTES DE `express.json()` Y CON FIRMA SIEMPRE

**Encontrado al preparar la v3 y conservado en esta v4 porque explica por qué el punto es imprescindible:**

```
provision-http.js:39    app.use(express.json({ limit: '64kb' }));      ← se traga el cuerpo
provision-http.js:1611  app.post('/webhook/stripe', express.raw(...))  ← llega tarde
provision-http.js:1612  const rawBody = req.body instanceof Buffer ? ... : String(req.body);
```

`express.json()` corre primero y marca el cuerpo como consumido, así que `express.raw()` **se salta a sí mismo** y `req.body` llega como objeto ya parseado. `String(objeto)` da `"[object Object]"`. Es decir: **el cuerpo con el que hoy se verifica la firma no es el cuerpo que firmó Stripe.** La verificación no puede salir bien nunca; lo único que "funcionaba" era el camino que no verificaba nada.

Eso encaja con lo medido por la auditoría B: sin cabecera → creaba el cliente y devolvía 200; con firma inventada → 400. Las dos cosas son coherentes con una verificación que nunca puede acertar.

**Tareas:**
1. Mover la ruta `/webhook/stripe` **por encima** de `app.use(express.json(...))`, montada con `express.raw({ type: 'application/json' })`.
2. Exigir siempre firma válida: `if (!secret || !sigHeader || !verifyStripeSignature(...)) → 400`. Se acabó el `if (secret && sigHeader)`.
3. Mantener la ventana de 300 s contra reenvíos, que la Pi ya tiene.
4. Aplicar también una tolerancia máxima de 300 s en la verificación de Vercel; hoy su verificador comprueba el HMAC pero no rechaza firmas antiguas.
5. **Verificación que no admite atajo:** un evento real de Stripe (reenviado desde el panel, con firma auténtica) debe devolver 200; el mismo cuerpo con un byte cambiado, 400; sin cabecera, 400; firma de más de 300 s, 400. Y **sabotaje**: romper `verifyStripeSignature` a propósito y comprobar que el test se pone rojo.

---

## 4. ✅ EL ALTA: REINTENTOS, IDEMPOTENCIA PERSISTENTE Y UN SOLO CORREO

**4.1 · Si el alta falla, Stripe tiene que reintentar.** Hoy la función de Vercel devuelve 200 aunque la provisión no se haya hecho: para Stripe el evento queda entregado y no vuelve nunca. **Cambio:** si `/provision` no confirma el alta, la función responde **5xx**. Stripe reintenta durante 3 días con espera creciente. Un fallo pasajero de la Pi deja de costar un cliente.

**4.2 · Idempotencia persistente con estados.** No vale una variable en memoria de Vercel. Tampoco vale marcar simplemente el evento como procesado antes de los efectos: si el proceso cae después de marcarlo, el cliente se pierde para siempre. El estado persistente debe distinguir al menos `processing`, `completed` y `failed/retryable`; solo se marca `completed` después de que terminen las acciones obligatorias. Para la compra, `stripeSessionId` es la identidad estable y `/provision` debe resolver de forma segura los reintentos concurrentes.

**4.3 · Un único responsable del correo de bienvenida. Nunca dos.**
Hoy hay **dos remitentes**: `provision-http.js:328` ("🎉 Tu portal está listo") y la función de Vercel ("Tu asistente está listo"). En cuanto el alta funcione, el primer cliente recibe **dos correos**.
**Decisión:** el correo lo manda **la Pi, dentro de `/provision`**, porque es quien tiene el `accessToken`, el enlace del portal, el QR de WhatsApp y los enlaces de Telegram. **Se elimina el envío de la función de Vercel.**
⚠️ Hoy ese correo se lanza después de `res.json()` y no se espera ni se comprueba el HTTP de Brevo. Debe pasar a ser una operación controlada: esperar respuesta 2xx, guardar `welcomeEmailSentAt`/identificador de mensaje y, si falla, dejar el alta en estado reintentable. En un reintento, una cuenta existente sin correo debe completar el correo; una cuenta con correo confirmado no lo repite. La notificación de pago de Telegram tampoco puede ejecutarse antes de saber si es un alta nueva: debe quedar bajo la misma idempotencia para no duplicarse.

**4.4 · El dato que falta.** La tubería está entera: `checkout.ts:44-52` ya manda `salon`, `create-session.js:52-58` ya lo mete en `metadata[salon]`. Falta el grifo: nadie escribe `sessionStorage.laraData`.
✅ **Campo "Nombre de tu negocio"** (no "salón" — el producto ya no es solo peluquerías) en el modal, antes de abrir el checkout. No se toca Stripe, no se mete fricción en la página de pago el día que arrancan los anuncios.
⚠️ Rellenar el dato, **no** saltarse el guard: `provision-http.js:232-236` devuelve 400 `missing_fields` igualmente.

**4.5 · ✅ `maxDuration` deja de ser bloqueante.** Vercel da hoy tiempo suficiente. Se puede declarar por higiene, pero sale de la lista de causas de fallo.

---

## 5. ✅ TELEGRAM: QUE LA ORDEN DE RESERVA NO PUEDA CORTARSE

Subir 150 → 450 en `lib/telegram.js:195` **no es el arreglo**: es bajar la probabilidad de un fallo que sigue existiendo. El token `[RESERVA:...]` va al final de la respuesta; si el modelo se queda sin espacio ahí, **la cita no se crea, la clienta ve un trozo de código y nadie se entera.**

**Trabajo:**
1. Subir el límite a 450 (igualar a WhatsApp) — **en la línea 195**; la 150 es `.slice(0, 10)` y romperla rompe el listado de citas.
2. **Detectar el corte:** si la respuesta termina truncada (motivo de parada por longitud) o contiene un `[RESERVA:` sin cerrar, **no se envía tal cual**: se reintenta o se pide la acción por separado. Una respuesta cortada nunca debe llegar a la clienta.
3. **Que la acción no dependa de que quepa:** pedir la orden de reserva en un paso propio y estructurado, en vez de confiar en que el modelo llegue al final del texto. Es lo que elimina la clase de fallo, no lo que la hace menos probable.
4. Aplicar la misma comprobación en los demás canales, que comparten el patrón.

⚠️ Este cambio no cabe honestamente en 30 minutos sin comprobar primero qué devuelve `lib/ai.js`. Si `chat()` solo devuelve texto, habrá que exponer el motivo de parada o separar la generación estructurada de la respuesta visible y ajustar sus consumidores. No fingir detección de truncado si el proveedor no entrega esa señal al código.

**Verificación:** ✅ **una reserva real de extremo a extremo por Telegram** — mensaje enviado desde una cuenta real, cita creada, comprobada en `appointments.json` **y en Google Calendar**, y borrada después. Requiere la participación de Ricardo (o una cuenta de Telegram de pruebas): crear cuentas está prohibido para el agente.

---

## 6. ✅ CONSENTIMIENTO Y LEGALES — suben a la Ola 1

Con la campaña arrancando mañana, dejan de ser Ola 2.

**6.1 · El píxel de OpenAI carga sin permiso en TODO el sitio.** `Layout.astro:56-62` inyecta el SDK siempre y solo pasa `consent:false`; `Medicion.astro` tiene el mismo bloque. No es un problema de `/demo`: arreglar la demo no lo arregla. **Trabajo:** no inyectar el SDK hasta que haya consentimiento, y que rechazar signifique rechazar (hoy, con `nx_cookie_consent=rejected`, sigue enviando eventos y responden 202).

**6.2 · `/demo` sin aviso de cookies.** ✅ Se incluye **solo el componente del aviso**, no se mete la página en `Layout.astro` (862 líneas con su propio `<html>` y reinicio global de estilos: rehacerla la mañana de la campaña es el riesgo, no el arreglo).
Matiz honesto: el consentimiento vive en `localStorage` por dominio, así que quien pasa antes por la portada sí activa Meta y GA4. Falla para quien entra **directo** a `/demo` — que es exactamente el tráfico del QR.

**6.3 · Textos legales.** La **garantía de 30 días** se promete en el pie, en las dos páginas de plan y en las descripciones, y **no aparece en ninguna condición legal**; `legal.astro:48` titula justo lo contrario ("Exclusión de garantías"). Y `/privacidad` **no declara Umami, ni Plausible, ni el píxel de OpenAI**, que son los tres que se activan sin permiso. Faltan NIF y domicilio.
**Trabajo:** o se sostiene la garantía en las condiciones, o se retira de los textos comerciales. Y declarar los tres sistemas de medición.

---

## 7. ✅ LA PRUEBA GRATUITA: DECISIÓN CERRADA

> **Las compras normales no llevan prueba gratuita. Las demos manuales pueden durar 7 días. Un alta manual de respaldo para un cliente que ya ha pagado debe ser una cuenta normal, no una demo. No se promete trial en publicidad ni checkout.**

- **No se toca Stripe.** `trial_period_days` sigue en `null`: es lo correcto bajo esta decisión.
- El código **no distingue bien los dos tipos de alta manual**: `isTrial = !stripeSubscriptionId` convierte en prueba cualquier alta sin suscripción, incluso una cuenta normal creada manualmente para rescatar a un comprador. Sustituir esa inferencia por un modo explícito y validado, por ejemplo `accountMode: stripe_paid | manual_paid | demo`, con `demo` como único caso que recibe `trialEndsAt`.
- **Lo que sí hay que hacer:** barrido de la promesa de prueba gratuita en **todos** los canales — anuncios, checkout, web, correos, guion de Lara, panel — y retirarla donde aparezca. En la web pública el auditor E no la encontró; sí está en `CalculadoraCitas.astro` (hoy no se sirve) y hay que revisar los canales que E no miró.
- ✅ **Consecuencia que hay que asumir:** si las demos manuales son de 7 días, **algo tiene que terminarlas**. **Corregido el 3-sep 23:40:** el script **existe y está completo** — `~/nexux-clients/scripts/trial-expiry.js` (8.360 bytes, 25-jul: migra `trialEndsAt`, expira y registra). Lo que **no existe es nada que lo ejecute**: `crontab -l` no tiene entrada de trial/expiry y ninguna otra parte del código lo invoca (verificado). O sea, `trialEndsAt` se escribe y nadie lo aplica. La tarea NO es escribir un caducador, es **enganchar, probar y vigilar el que ya está escrito** → **Ola 2, primera posición.**

---

## 8. ✅ PRUEBA DE ACEPTACIÓN — la cadena entera, con el producto de 29 €

Una sola prueba, con **el mismo producto de 29 €** (cupón admitido), y **no se da por bueno nada hasta que los ocho eslabones pasan**:

| # | Eslabón | Qué se comprueba |
|---|---|---|
| 1 | **Pago** | Compra desde la web con la red del navegador grabando |
| 2 | **Una cuenta** | Exactamente **un** directorio nuevo en `clients/`, con `accessToken`, `limits`, `features`, plantilla y `active:true`. Ni cero ni dos |
| 3 | **Un correo** | Exactamente **uno**, con el enlace del portal y el QR. Se cuentan los envíos en los dos remitentes posibles |
| 4 | **Portal** | El enlace del correo abre el portal y muestra los datos del cliente |
| 5 | **Canal** | Se conecta un canal desde el portal; se identifica cuál se usará en la prueba y se verifica su estado real |
| 6 | **Cita** | Una reserva real por ese canal, que aparece en `appointments.json` y en Google Calendar |
| 7 | **Cancelación** | Cancelar desde el portal de facturación y que el evento llegue al endpoint de la Pi |
| 8 | **Desactivación** | `active:false` en el config **y que el canal conectado en el paso 5 deje de responder**. Auditar WhatsApp y Telegram: no basta con añadir el guard solo en `lib/whatsapp.js` si la prueba usa Telegram |

**Se registra además:** cuántas veces entra el mismo `event.id`, y que el `/api/book` renombrado responde.
**Limpieza obligatoria al terminar, con objetivo único identificado y autorización de Ricardo para las acciones externas/destructivas:** cancelar la suscripción, reembolsar, archivar la evidencia y eliminar solo el cliente de prueba creado por esta ejecución.
⚠️ El eslabón 8 exige revisar todos los puntos de entrada de los canales y tareas programadas. No se cierra añadiendo un `if` únicamente a WhatsApp.

---

## 9. ✅ DESPLIEGUE: WORKTREES, PREVIEW, CANARIO Y VUELTA ATRÁS

**Los dos repositorios están sucios, comprobado hoy:**

| Repo | Rama | Sin subir | Modificados | Sin rastrear |
|---|---|---|---|---|
| `nexux-clients` | main | **3 commits** | 1 | 13 |
| `nexux-pro` | main | 0 | 2 | **30** |

Trabajar directamente ahí mezcla el arreglo con 43 ficheros que nadie ha revisado. **Se trabaja en worktrees.**

**Procedimiento, por repo:**
1. Hacer `git fetch origin`, medir ahead/behind y decidir explícitamente el commit base. No ejecutar `pull` sobre el árbol sucio. El worktree de `nexux-clients` debe incluir deliberadamente los tres commits locales de seguridad. Crear ramas `task/ola1-lanzamiento-pro` y `task/ola1-lanzamiento-clients` desde los commits base confirmados.
2. **Build:** ✅ en la Pi, **siempre** con `NODE_OPTIONS=--max-old-space-size=1400`. Sin ese límite `pnpm build` tumbó la Pi entera hoy por falta de RAM (y con él, el build bajó de 652 s a 89 s).
3. **Preview:** despliegue de previsualización en Vercel desde la rama, **antes** de tocar producción. Se comprueban ahí los cinco cambios web.
4. **Despliegue:** un solo push, autorizado por Ricardo. ✅ **Anotar el id del despliegue anterior en Vercel antes de subir.**
5. **Canario:** tras el despliegue, comprobación inmediata de: `/`, `/demo` (con aviso de cookies y píxeles disparando), `/f/d1`, `/paquetes/recepcionista`, `/reservar/<id>` con `pub-api/book`, y el portal de un cliente. Cualquier fallo → vuelta atrás sin discutir.
6. **Vuelta atrás documentada:**
   - **Web:** promover en Vercel el despliegue anterior anotado en el paso 4. Un clic.
   - **Pi:** rollback por commit conocido (`git revert` o despliegue del commit anterior) y reinicio controlado; no llenar el repositorio de copias `.pre-*` que luego puedan mezclarse en un commit.
   - **Stripe:** los cambios de endpoint se anotan (id, URL, eventos, secreto) antes de tocarlos, para poder recrearlos igual.
7. Al terminar y verificar, fusionar a `main` y retirar el worktree.

---

## 10. OLA 0 — HECHO HOY (verificado en producción)

| Qué | Evidencia | Commit |
|---|---|---|
| Panel de administración abierto con clave escrita en el código | clave vieja/ausente/errónea → 401; nueva → 200; las 5 rutas `/admin/*` | `abd1c26` |
| El enlace de dueño de Telegram era el id público del salón — y el `clientId` llegaba a `fs.writeFileSync`: **escritura arbitraria de ficheros** desde Telegram | 19 pruebas sobre el código real + sabotaje; revisión adversarial que encontró un fallo grave del primer intento | `efd9797` |
| La única copia de sistema utilizable fuera de la Pi iba a borrarse el lunes | renombrada a `CONSERVAR-pi-sistema-20260824.tar.gz`, 23,34 GB, tamaño idéntico | — |

Sin subir.

---

## 11. ✅ OLA 1 v4 — orden de ejecución

### BLOQUE PI — 1 h 15 · sin despliegue web, reversible
| # | Qué | Tiempo |
|---|---|---|
| P1 | Monitor de `pi.nexux.pro/health` en Uptime Kuma con aviso a Telegram **+ uno externo** | 15 min |
| P2 | Ruta de Stripe por encima de `express.json()` + firma siempre obligatoria (apartado 3) | 30 min |
| P3 | Telegram: límite 450 **y** que la orden de reserva no pueda cortarse (apartado 5), incluyendo los cambios necesarios en la capa IA | 60-90 min |

### BLOQUE DINERO — 3 h 30
| # | Qué | Tiempo |
|---|---|---|
| D1 | Campo "Nombre de tu negocio" en el modal | 45 min |
| D2 | Rellenar `salon` antes de llamar a `/provision` | 15 min |
| D3 | La función de Vercel devuelve 5xx si el alta no se confirma | 20 min |
| D4 | Idempotencia persistente con estados y concurrencia segura por `stripeSessionId`; nada de estado efímero en Vercel | 45-75 min |
| D5 | Un solo correo: se elimina el envío de Vercel; la Pi espera Brevo, comprueba 2xx y registra el envío para poder reintentar sin duplicar | 45-60 min |
| D6 | Auditar la tasa de entregas de los 2 endpoints actuales **antes** de tocar nada | 20 min |
| D7 | Alta del endpoint de la Pi en Stripe con su secreto y sus eventos; Ricardo introduce el secreto; prueba auténtica; después reducir Vercel y retirar el duplicado identificado | 45-60 min |
| D8 | Todos los canales y tareas consultan `config.active`; la prueba usa el mismo canal que luego se intenta desactivar | 45-60 min |
| D9 | Modo de cuenta explícito: compra, alta manual pagada o demo; solo demo caduca | 30-45 min |

### BLOQUE WEB — 3 h · un solo despliegue
| # | Qué | Tiempo |
|---|---|---|
| W1 | Portal: resolver el bucle de sesión sin debilitar auth; repetir token válido, inválido, ausente y cruzado entre clientes | 20-30 min |
| W2 | Componente del aviso de cookies en `/demo` | 30 min |
| W3 | Consentimiento del píxel de OpenAI en todo el sitio; rechazar = rechazar | 45 min |
| W4 | UTM antes de deducir el origen + guardar `utm_content` | 30 min |
| W5 | `/api/book` y `analytics/ob` → `src/pages/pub-api/` (no a la carpeta `api/` de la raíz) | 30 min |
| W6 | QR de Telegram: `is:inline` | 15 min |
| W7 | Borrador legal: garantía y declaración de Umami/Plausible/OpenAI. No inventar NIF, domicilio ni base jurídica; Ricardo confirma los datos antes de publicar | 30-45 min |
| W8 | Arreglar crear, editar y arrastrar citas con zona horaria de la fecha objetivo; probar verano e invierno | 60-90 min |

### CIERRE — 1 h
Preview → despliegue → canario → **prueba de aceptación del apartado 8** → limpieza.

**Total realista tras la revisión final: 12-16 horas más los tiempos de aprobación, despliegue y prueba real.** No prometer un día cerrado: es trabajo de uno o dos días y contiene pasos que esperan a Ricardo.

### FUERA DE LA OLA 1, con su consecuencia declarada
- **Calculadora con precios viejos** — `blog/[slug].astro:54` la pasa con `showCalculator={false}` fijo. Está muerta; revivirla exige cambiar código.

### ÓRDENES EN LOS QUE QUEDARSE A MEDIAS ES PEOR QUE NO TOCAR NADA
1. Desplegar el nuevo alta sin haber probado el comportamiento de reintento y correo: se puede cobrar, crear una cuenta a medias y perder el evento.
2. Borrar un endpoint de Stripe antes de identificar por entregas cuál funciona y antes de validar el sustituto.
3. Registrar la Pi en Stripe antes de corregir su cuerpo raw, o activar eventos antes de que Ricardo haya introducido el secreto propio.
4. Marcar un evento como completado antes de terminar el alta y el correo.

---

## 12. OLA 2

1. ✅ **Caducidad de cuentas marcadas explícitamente como demo** — aviso previo, desactivación y registro. Nunca inferir demo por ausencia de suscripción.
2. Al cliente de 79 € el portal le dice 749 €/mes y le ofrece 3 planes retirados.
3. Subir a Equipo no crea las agendas por profesional.
4. **Copias fuera de casa** (Duplicati apunta a una carpeta borrada desde el 9-may) y cifrado de los datos de clientas.
5. **Secretos publicados:** antes del lanzamiento, comprobar cuáles siguen activos y rotar inmediatamente los activos de mayor impacto. El agente no imprime ni edita secretos. Después, limpiar historial y añadir protección contra un push accidental. Esto es una puerta de seguridad, no una mejora opcional de producto.
6. Twilio (no reserva nada: `parseActions = undefined`) · bucle de QR de WhatsApp · horarios duplicados inglés/español · Telegram acepta nombres inventados · widget de ventas con Markdown en crudo · móvil del portal (206 px fuera de pantalla) · token del cliente impreso en el HTML · límite de peticiones y `helmet` · journal volátil, logs sin rotación, disco USB como punto único de fallo.
7. ⚠️ **Si algún día se vacía la carpeta `api/` de la raíz, el botón de 79 € deja de funcionar** (`provision-http.js:228` no lista `equipo`). Arreglar antes de tocarla.

---

## 13. LO QUE ESTÁ BIEN (comprobado)

Lo roto está casi todo en las juntas entre sistemas, no en el motor.

Lara creó una cita real y esa cita llegó a Google Calendar con la hora correcta; la prueba concreta se limpió · 111/111 tests y sparring en verde · los precios y la creación del checkout son correctos, pero **el cobro y alta completos no se declaran probados hasta la aceptación del apartado 8** · el circuito del QR produjo una fila identificable en Umami · las pruebas cruzadas ejecutadas devolvieron 401, sin generalizarlo a endpoints no probados · la web pública auditada no mostró enlaces rotos y respondió rápido · se restauraron ficheros seleccionados con hash idéntico, pero la copia completa más reciente estaba truncada · la API tuvo 18 minutos de caída en 14 días y los reinicios observados no demostraron un crash propio.

---

## 14. VERIFICACIÓN (innegociable)

1. Se nombra el fichero o endpoint que **EJECUTA** y se demuestra con una petición real contra producción.
2. **Todo test se sabotea antes de creérselo.** Ya nos pasó: `test/precios-mapeados.test.mjs` pasaba en verde validando un fichero muerto.
3. Cierre con `python3 ~/scripts/nexux-verify.py service:nexux-clients url:https://pi.nexux.pro/health` y entrada en el quality-ledger.
4. Antes de cualquier preview o despliegue: tests específicos, sabotaje del test crítico, `node --check` en backend y `NODE_OPTIONS=--max-old-space-size=1400 pnpm build` en web.
5. Commit descriptivo por arreglo, en el worktree. **El push lo autoriza Ricardo.**
6. Vuelta atrás documentada antes de desplegar (apartado 9).
7. Tras cada despliegue, canario de cinco rondas en cinco minutos; tres fallos consecutivos implican rollback.
8. Lo que no se pueda comprobar se declara **NO VERIFICADO**, sin disfrazarlo.

---

## 15. DECISIONES PENDIENTES DE RICARDO

| # | Decisión | Estado |
|---|---|---|
| 1 | **Autorizar UN push a `nexux-pro`** (desde el worktree, con preview y vuelta atrás) | Pendiente. Sin él, ningún arreglo web existe |
| 2 | ¿El botón de comprar sigue abierto mañana mientras se arregla el alta? | Pendiente. Quien pague antes de la prueba de aceptación paga y no existe |
| 3 | Prueba gratuita | ✅ **CERRADA**: sin trial en compras; demos manuales de 7 días; no se promete en publicidad ni checkout |
| 4 | Rotar los 21 secretos ya publicados en GitHub | Pendiente |
| 5 | Endpoints de Stripe | ✅ Diseño definido. Requiere su OK antes de crear, modificar o borrar endpoints |
| 6 | Introducir el secreto nuevo de la Pi | Pendiente de Ricardo; ningún agente toca `.env` ni pega el secreto en el chat |
| 7 | Compra, cancelación, reembolso y eliminación del cliente de prueba | Requiere confirmación justo antes de ejecutar |
| 8 | Datos legales reales | Ricardo confirma NIF, domicilio y texto de garantía antes de publicar |

---

## 16. BRIEFING CODEX/OPENCODE

Por cada arreglo, tarea autocontenida con: hallazgo y evidencia · **fichero exacto que EJECUTA, y cuál NO** (la carpeta `api/` de la raíz gana sobre `vercel.json` y sobre `src/pages/api/`) · worktree en el que se trabaja · cambio propuesto · test que debe pasar **y su sabotaje** · comando de verificación contra producción · vuelta atrás · regla de commit sin push. Contrato anti-fabricación: lo no ejecutado en la sesión se declara NO VERIFICADO.

---

## 17. ESTADO

- [x] Fase 1 — auditoría de 7 áreas · 3-sep
- [x] Fase 2 — consolidación y tabla cruzada
- [x] Ola 0 — dos agujeros cerrados y verificados; copia de sistema a salvo
- [x] v1 → revisión adversarial → rechazada · v2 → v3 con las 10 correcciones de Ricardo
- [x] La revisión de Sonnet v3 quedó interrumpida por límite de sesión; Codex revisó la v3 contra los ficheros ejecutables y produjo esta **v4 final**
- [x] Estado actual reconfirmado por la cuenta nueva (3-sep 23:00-23:40): SSH, rutas de autoridad, ambas copias del PRP (idénticas), commits de seguridad, ramas libres, 404 del formulario público reproducido en producción, panel admin sigue cerrado
- [~] Revisión adversarial de la v4: **PARCIAL**. Seis lentes completaron; la fase de refutación murió por límite de sesión (32 de 33). Salida cruda en `progress/auditoria-lanzamiento-20260903/REVISION-BRIEFING-Y-PRP-20260903.json`. Confirmado y ya incorporado: el segundo receptor de Stripe (2 bis) y el error sobre el caducador de pruebas (apartado 7). Sin confirmar y bloqueando el bloque DINERO: la disputa del apartado 3 (ver 3 bis)
- [ ] Ola 1 v4 — **BLOQUE WEB EMPEZADO**: W5 hecho y verificado en el artefacto de build (worktree `~/nexux-pro-wt-ola1`, rama `task/ola1-lanzamiento-pro`, commit `0bf1a1f`, sin push). El bloque DINERO no arranca hasta cerrar 3 bis
- [ ] Ola 2
