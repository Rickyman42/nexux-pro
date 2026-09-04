# ÁREA D — CRM / Portal del cliente (nexux.pro)

**Auditor:** Opus 5 (subagente D) · **Fecha:** 2026-09-03 · **Estado:** CERRADO
**Regla aplicada:** verificar lo que EJECUTA, no lo que documenta. Toda vista se abrió en un navegador real y toda afirmación lleva su comando o su medición.

## RESUMEN

El portal se ve bien y guarda la configuración de verdad, pero **cuatro cosas serias están rotas en producción**: al cliente del plan de 79 € el portal le dice que paga **749 €/mes**; el botón de **crear una cita a mano nunca funciona** (error 500 siempre); un **enlace caducado deja al cliente encerrado** en una pantalla de error 500 sin forma de pedir uno nuevo; y la carpeta `api/` de la raíz se come las rutas de Astro, con lo que **la reserva por web devuelve 404**.

**Hallazgos: 4 bloqueantes · 4 altas · 8 medias · 4 bajas.**

**Veredicto: NO lanzar todavía.** Los cuatro bloqueantes se arreglan en menos de un día de trabajo; después hay que volver a probarlos en producción, no en el código.

---

## Entorno verificado (2026-09-03, 18:45-19:0x CEST)

- Pi: `uptime` load 0.31/0.36/0.38, RAM 3796 MB (1621 disponibles). PM2 `nexux-clients` online, 3 h de vida, pid 1378382.
- El portal del cliente vive en **Vercel** (`~/nexux-pro`, Astro `output: 'server'`), y llama por HTTP a la Pi (`https://pi.nexux.pro`, `src/lib/portal-client.ts` → `BASE_URL`).
- La carpeta `~/nexux-pro/api/` (raíz) solo tiene `leads/pro.js`, `stripe/create-session.js`, `webhook/stripe.js`. **Ninguna** se solapa con `/cliente/*` ni con `/portal-api/*` (esas rutas las sirve Astro), **pero sí se come todo `/api/*`**: ver hallazgo 2.
- Clientes en la Pi: 18 carpetas, **ninguna con `stripe_customer_id`** y **ninguna con plan `equipo`** (comprobado recorriendo todos los `config.json`). Es decir: hoy no hay nadie facturando, todo son demos/tests.

## HALLAZGO 1 (BLOQUEANTE) — Con el enlace caducado el cliente ve un error 500 y se queda encerrado fuera

**Síntoma.** Si la cookie de sesión existe pero ya no vale (enlace viejo, token regenerado, cliente borrado), el portal devuelve **HTTP 500 con la página vacía (0 bytes)**. Y no hay salida: al ir a la pantalla de pedir enlace nuevo, el sistema le devuelve al panel roto. Bucle.

**Comprobado en producción (no en el código):**
```
$ curl -s -o /tmp/inv.html -w 'HTTP %{http_code} · %{size_download}b\n'     -H 'Cookie: nexux_token=TOKEN-INVALIDO-AUDITORIA'     https://nexux.pro/cliente/nexux-demo-mostoles-42a928
HTTP 500 · 0b

$ curl -sIL --max-redirs 5 -H 'Cookie: nexux_token=TOKEN-INVALIDO-AUDITORIA'     https://nexux.pro/cliente/nexux-demo-mostoles-42a928/login
HTTP/2 302
location: /cliente/nexux-demo-mostoles-42a928
HTTP/2 500
```
(Sin cookie sí redirige bien al login: `HTTP 302 → /cliente/<id>/login`.)

**Causa (dos fallos que se suman):**
1. `src/pages/cliente/[id].astro` líneas 16-18: se usa `data` **antes** de comprobar que existe.
```astro
const data = await getClientData(clientId, token);   // devuelve null si el token no vale (401/404)
const _conf = (data as any).confianza || {};         // ← revienta aquí: null.confianza
...
if (!data) { return Astro.redirect(...) }            // línea 51: código muerto, nunca se llega
```
2. `src/middleware.ts` líneas 71-74: si hay cookie (aunque sea basura) y el cliente pide `/login`, se le redirige al panel. Como el panel casca, no puede pedir un enlace nuevo.

**Impacto en el cliente que paga.** Cualquier peluquera con un enlace antiguo en el móvil ve una pantalla en blanco de error y no puede entrar ni pedir un enlace nuevo. Su única salida es borrar los datos del navegador, que no va a saber hacer: llamada de soporte asegurada el primer día.

**Arreglo (trivial).**
```diff
 const data = await getClientData(clientId, token);
+if (!data) {
+  return Astro.redirect(`/cliente/${clientId}/login?reason=expired`);
+}
 const _conf = (data as any).confianza || {};
```
y borrar el `if (!data)` de la línea 51. En `src/middleware.ts`, quitar el redirect de login→panel (líneas 71-74) o dejarlo solo cuando la URL no traiga `?reason=`.

**Esfuerzo:** 10 minutos + deploy.

## HALLAZGO 2 (BLOQUEANTE) — La carpeta `api/` de la raíz se come TODAS las rutas `/api/*` de Astro: la reserva por web devuelve 404

**Síntoma.** En producción, `/api/book` (el formulario público de reservas, `src/pages/reservar/[id].astro` línea 110) y `/api/analytics/ob` (la telemetría del onboarding, `onboarding.astro` línea 883) devuelven **404**. Lo primero que ve un cliente del salón al pulsar Reservar en la web es un fallo; y cada peluquera que abre el onboarding genera un error rojo en la consola.

**Comprobado en producción:**
```
$ curl -s -o /dev/null -w '%{http_code}\n' -X POST -H 'Content-Type: application/json' -d '{}' https://nexux.pro/api/book
404
$ curl ... -X POST ... https://nexux.pro/api/analytics/ob
404
$ curl ... -X POST ... https://nexux.pro/api/leads/pro      → 400   (existe: es api/leads/pro.js de la raíz)
$ curl ... https://nexux.pro/api/webhook/stripe             → 405   (existe: es api/webhook/stripe.js de la raíz)
```
Y en el navegador, al abrir el portal del cliente de demo:
```
[ERROR] Failed to load resource: the server responded with a status of 404 ()
        @ https://nexux.pro/api/analytics/ob:0
```

**Causa.** `~/nexux-pro/api/` (raíz del proyecto) contiene funciones serverless de Vercel. Vercel sirve **todo** `/api/*` desde ahí, y las rutas equivalentes de Astro (`src/pages/api/**`) quedan muertas. Sobreviven solo las que tienen gemelo en la raíz (`leads/pro`, `webhook/stripe`, `stripe/create-session`). No lo tienen: `src/pages/api/book.ts` y `src/pages/api/analytics/ob.ts`.

**Impacto.** El canal web de reservas no funciona: el cliente del salón rellena el formulario y no se crea ninguna cita. Además se pierde toda la medición del onboarding.

**Arreglo.** Dos opciones, la segunda es la buena a largo plazo:
1. Rápido: crear `api/book.js` y `api/analytics/ob.js` en la raíz que reenvíen a la Pi (`https://pi.nexux.pro/public/:clientId/book` y `/track`).
2. Correcto: mover esas rutas fuera de `/api/` (p. ej. `/portal-api/book`, que sí funciona porque no cae bajo `/api/`) y actualizar los dos `fetch`.

**Esfuerzo:** 30 min + deploy y prueba real de una reserva por web.

## HALLAZGO 3 (MEDIA) — El pie del menú lateral se sale y se solapa (escritorio)

**Síntoma.** Abajo a la izquierda, la etiqueta del plan, ⚙ Configuración inicial y Soporte se montan unos encima de otros y **Soporte se sale de la barra lateral**. Se lee ConfiguraciónSoporte inicial.

**Comprobado en el navegador** (Chromium 1440×900, `https://nexux.pro/cliente/nexux-demo-mostoles-42a928`), midiendo las cajas reales:
```
.crm-sidebar          x=0   w=220
.crm-plan-chip        x=12  y=830 w=105 h=43
.crm-support-link.crm-setup-link (⚙ Configuración inicial)  x=117 y=822 w=74 h=58   ← pisa el chip
.crm-support-link (Soporte)     x=191 y=842 w=42 h=19  → termina en x=233, fuera de la barra (220)
```
Captura: `D-dashboard-desktop.png`.

**Causa.** Los tres elementos están en una fila (flex) sin envolver ni espacio suficiente para 220 px.

**Impacto.** Da aspecto de producto sin terminar en la primera pantalla que ve el cliente cada día. El enlace de Soporte queda medio tapado.

**Arreglo.** Poner el pie en columna: `.crm-sidebar-footer { display:flex; flex-direction:column; align-items:flex-start; gap:.5rem; }`. **Esfuerzo:** 10 min.

## Nota de consola presente en TODAS las vistas del portal

`[WARNING] Unrecognized feature: 'same-origin'. @ https://nexux.pro/cliente/<id>:85` — cabecera/atributo `allow` mal formado. No rompe nada, pero ensucia la consola. (Ver hallazgo Baja al final.)

## HALLAZGO 4 (ALTA) — El QR de Telegram no se dibuja nunca y el botón "Descargar QR" está muerto

**Síntoma.** En Canales → Telegram, donde debería estar el "código QR para pegar en el mostrador" hay un **hueco en blanco**. El botón "⬇️ Descargar QR" no descarga nada. Es el canal que el propio portal marca como RECOMENDADO.

**Comprobado en el navegador** (`https://nexux.pro/cliente/nexux-demo-mostoles-42a928`, pestaña Canales). Captura: `D-canales-wa-desktop.png`.
```js
// pixeles pintados en el canvas del QR de Telegram
{ w: 180, h: 180, pixelesPintados: 0, libs: { QRCode: "undefined", qrcode: "undefined" } }
// el enlace de descarga no llega a tener destino
document.getElementById('tg-qr-download').getAttribute('href')  →  null
```

**Causa (probada sobre el fichero desplegado, no sobre el fuente).** `src/pages/cliente/[id].astro` línea 159 carga la librería así:
```astro
<script src="https://cdn.jsdelivr.net/npm/qrcode/build/qrcode.min.js"></script>
```
Astro se lo lleva a un bundle y lo convierte en un **import de módulo**. El fichero que sirve producción es literalmente:
```
$ curl -s https://nexux.pro/_astro/_id_.astro_astro_type_script_index_0_lang.CBbUkXTA.js
import"https://cdn.jsdelivr.net/npm/qrcode/build/qrcode.min.js";
```
La librería declara `var QRCode = ...`; dentro de un módulo eso **no** crea la variable global. Por eso `typeof QRCode === 'undefined'` para siempre, y el código entra en un bucle infinito de reintentos cada 300 ms (línea 1732) que calienta el móvil sin dibujar nada. El botón de descarga se queda sin `href` porque solo se rellena dentro del callback que nunca se ejecuta.

**Impacto.** El salón no puede imprimir su QR de Telegram, que es justo el canal que le recomendamos. Y el navegador se queda reintentando para siempre.

**Arreglo (una palabra).**
```diff
-<script src="https://cdn.jsdelivr.net/npm/qrcode/build/qrcode.min.js"></script>
+<script is:inline src="https://cdn.jsdelivr.net/npm/qrcode/build/qrcode.min.js"></script>
```
Conviene además cortar el bucle: reintentar como mucho ~20 veces y, si no, enseñar el enlace en texto. **Esfuerzo:** 15 min + comprobar en producción que el QR aparece.

## HALLAZGO 5 (BAJA) — Aviso en la consola en todas las vistas: `Unrecognized feature: 'same-origin'`

**Causa.** `src/pages/cliente/[id].astro` línea 496: `<iframe id="inbox-iframe" ... allow="same-origin">`. `allow` sirve para permisos tipo cámara o micrófono; `same-origin` no existe ahí (eso es de `sandbox`). El navegador lo ignora y avisa en cada carga.

**Arreglo:** quitar el atributo `allow="same-origin"`. **Esfuerzo:** 2 min.

## HALLAZGO 6 (MEDIA) — El aviso de "esto es del plan Equipo" está mal escrito

**Síntoma.** En Clientes, a un cliente del plan Recepcionista (29 €) se le muestra un candado con el titular **"Está en el plan Equipo"**, que se lee como si él ya estuviera en el plan Equipo. Debería decir "Esto viene con el plan Equipo (79 €/mes)".

**Dónde.** `src/pages/cliente/[id].astro` línea 1447. Comprobado en pantalla: captura `D-clientes-desktop.png`.

**Impacto.** Confunde justo en el sitio donde se intenta vender el plan de 79 €, y encima no dice el precio.

**Arreglo:** cambiar el texto y añadir el precio. **Esfuerzo:** 5 min.

## Nota sobre el 403 de Clientes

`GET /portal-api/customers?clientId=...` responde **403** para el plan Recepcionista y eso pinta el candado. Funciona, pero deja un error rojo en la consola del navegador en cada visita a la pestaña Clientes. Evidencia:
```
[ERROR] Failed to load resource: the server responded with a status of 403 ()
        @ https://nexux.pro/portal-api/customers?clientId=nexux-demo-mostoles-42a928:0
```

## HALLAZGO 7 (BLOQUEANTE) — Al cliente del plan Equipo (79 €) el portal le dice que paga **749 €/mes** y le ofrece tres planes que ya no existen

**Síntoma.** En Facturación, un cliente del plan `equipo` ve:
- **Plan activo: Equipo — 749€/mes**
- **Planes disponibles: Starter 249€/mes · Pro 449€/mes · Total 749€/mes** (los tres retirados el 21-ago-2026; ni siquiera se pueden comprar: `api/stripe/create-session.js` responde `invalid_plan`).

El plan Equipo cuesta **79 €/mes** (`api/stripe/create-session.js`: `equipo → amount 7900`, precio de Stripe `price_1UBHkE2SQwDzHtsFTVWQ67l5`, creado el 2-sep-2026).

**Comprobado en producción, no en el código.** Como hoy no hay ningún cliente con plan `equipo`, creé uno de prueba en la Pi (`clients/prueba-auditoria-equipo-d`, copia del de demo con `plan: "equipo"`, marcado PRUEBA-AUDITORIA y **borrado al terminar**) y abrí su portal en el navegador:
```
https://nexux.pro/cliente/prueba-auditoria-equipo-d   (pestaña Facturación)
→ "Plan activo  Equipo  749€/mes"
→ "Planes disponibles  Starter 249€/mes | Pro 449€/mes | Total 749€/mes"
```
Captura: `D-facturacion-equipo-749.png`.

**Causa.** `src/pages/cliente/[id].astro`:
- Línea 69-75: la etiqueta de precio solo contempla `recepcionista/starter/pro/total`; cualquier otro plan cae en el `else` final y se etiqueta **749€/mes**.
- Línea 21 de `src/lib/portal-client.ts`: el tipo `plan` ni siquiera incluye `'equipo'`.
- Líneas 769-827: el bloque "Planes disponibles" solo tiene caso especial para `recepcionista`; el resto ve la tarjetería vieja de Starter/Pro/Total.

**Impacto en el cliente que paga.** Es el peor sitio posible para equivocarse: el cliente que acaba de pagar 79 € entra a Facturación y lee que su plan cuesta 749 €. Riesgo de baja inmediata, de reclamación y de discusión sobre el precio pactado. Además le enseñamos un catálogo de planes que ya no vendemos.

**Arreglo.**
```diff
-const planPriceLabel = isRecepcionista
-  ? '29€/mes'
-  : data.plan === 'starter' ? '249€/mes'
-  : data.plan === 'pro' ? '449€/mes' : '749€/mes';
+const PRECIOS: Record<string, string> = {
+  recepcionista: '29€/mes', equipo: '79€/mes',
+  starter: '249€/mes', pro: '449€/mes', total: '749€/mes',
+};
+const planPriceLabel = PRECIOS[data.plan] ?? '';
```
y en "Planes disponibles" enseñar solo los dos planes vivos (Recepcionista 29 € y Equipo 79 €), marcando cuál es el actual. Añadir `'equipo'` al tipo `plan` de `portal-client.ts`.

**Esfuerzo:** 45 min (hay que rehacer el bloque de tarjetas) + deploy y comprobación con un cliente `equipo` real.

## Comprobaciones que SÍ funcionan (verificadas en vivo)

| Qué | Cómo | Resultado |
|---|---|---|
| Guardar servicios escribe de verdad en la Pi | Añadí "PRUEBA-AUDITORIA / 15 min / 12,5 €" en Configuración → Guardar servicios; leí `clients/nexux-demo-mostoles-42a928/config.json` por SSH | **OK** — apareció `{"name": "PRUEBA-AUDITORIA", "duration": 15, "price": 12.5}` |
| Aviso de guardado visible | Medí la opacidad del toast tras pulsar Guardar | **OK** — "Guardado ✅" visible de ~0,75 s a ~3 s |
| Borrado y limpieza | Borré la fila y volví a guardar; comparé el config con la copia previa | **OK** — cero diferencias con el backup (`claves distintas del backup: []`) |
| Fichas de clientes con plan Equipo | Portal del cliente de prueba `equipo`, pestaña Clientes | **OK** — la desbloquea y el estado vacío está bien escrito: "Aún no hay clientes. Aparecerán solos en cuanto alguien reserve con nombre y teléfono." |
| Facturación de cuenta sin Stripe | Pestaña Facturación del cliente de demo | **OK** — no enseña el botón de Stripe y explica por qué, sin tecnicismos |
| QR de WhatsApp | Pestaña Canales del cliente de demo | **OK** — el QR se pinta (200×200, imagen real) con el aviso de las 24 h |

## HALLAZGO 8 (BLOQUEANTE) — El botón "+ Nueva cita" del CRM no crea ninguna cita: siempre error 500

**Síntoma.** El dueño rellena la cita a mano en el portal, pulsa "Reservar cita" y le sale **"No se pudo crear la cita."**. Nunca se crea. Es la acción principal del CRM cuando alguien llama por teléfono en vez de escribir al bot.

**Comprobado en el navegador y repetido con curl contra la Pi, en dos clientes distintos:**
```
Navegador: POST https://nexux.pro/portal-api/appointments → 500
           mensaje en pantalla: "No se pudo crear la cita."

$ curl -X POST -H 'Authorization: Bearer <token del cliente de demo>' \
    -H 'Content-Type: application/json' \
    -d '{"client_name":"PRUEBA-AUDITORIA","service":"Cambio de aceite","datetime":"2026-09-04T10:00:00","duration_min":60}' \
    http://127.0.0.1:3460/client/nexux-demo-mostoles-42a928/appointments
{"ok":false,"error":"La fecha debe incluir Z o un desplazamiento horario explícito"}
HTTP 500
```
Idéntico con el cliente de prueba `prueba-auditoria-equipo-d`. No es cosa de un cliente concreto: falla para todos.

**Causa.** El portal arma la fecha **sin zona horaria**:
`src/pages/cliente/[id].astro` línea 2320 (crear) y línea 1917 (editar):
```js
datetime: date + 'T' + time + ':00',      // → "2026-09-04T10:00:00"
```
y el motor de reservas de la Pi (`nexux-clients/lib/booking-engine.js`, `parseInputDate`, línea 31) **exige** que la fecha lleve `Z` o un desfase explícito; si no, lanza error y el endpoint devuelve 500. Los dos lados se escribieron por separado y nadie probó el botón después.

**Ojo con el arreglo fácil:** pegar `'Z'` al final es **incorrecto** — en verano desplazaría todas las citas dos horas. Hay que mandar la hora con el desfase de la zona del salón (`data.timezone`, que ya está en el portal):
```js
// helper: convierte "2026-09-04" + "10:00" + tz del salón en ISO con desfase
function isoConZona(fecha, hora, tz) {
  const local = new Date(`${fecha}T${hora}:00`);
  const enTz = new Date(local.toLocaleString('en-US', { timeZone: tz }));
  const desfaseMin = Math.round((local - enTz) / 60000);
  const signo = desfaseMin >= 0 ? '+' : '-';
  const abs = Math.abs(desfaseMin);
  const hh = String(Math.floor(abs / 60)).padStart(2, '0');
  const mm = String(abs % 60).padStart(2, '0');
  return `${fecha}T${hora}:00${signo}${hh}:${mm}`;
}
```
Aplicarlo en las tres llamadas: crear (2320), editar (1917) y arrastrar la cita en el calendario (1980).

**Impacto.** El salón no puede meter a mano la cita de quien llama por teléfono. Para una peluquería es la mitad de su agenda. Bloquea el lanzamiento.

**Esfuerzo:** 1 h con prueba real de crear, editar y mover una cita.

## HALLAZGO 9 (MEDIA) — Mover o editar una cita usa la hora del reloj de la Pi, no la del salón

**Síntoma.** El endpoint de editar cita (`provision-http.js` línea 1327) hace `new Date(body.datetime)` con una fecha sin zona. JavaScript la interpreta con la zona del servidor (la Pi, Europe/Madrid). Para un salón en Canarias (por ejemplo `kalon-...`, con `timezone: "Atlantic/Canary"` en su config) la cita se guardaría **una hora movida**.

**Comprobado.** El endpoint acepta fechas sin zona (devolvió `409 lead_time_violation`, no error de formato):
```
$ curl -X POST ... -d '{"datetime":"2026-08-22T13:00:00","duration_min":60}' \
    http://127.0.0.1:3460/client/nexux-demo-mostoles-42a928/appointments/c01bde72/update
{"ok":false,"error":"lead_time_violation","message":"La cita no respeta el tiempo mínimo de antelación"}
HTTP 409
```
Es decir: la validación de zona horaria que sí tiene el alta **no está** en la edición. No he podido medir el desfase real de una hora sin mover una cita de verdad, así que **el desfase queda como no verificado**; lo verificado es que el endpoint acepta fechas sin zona.

**Arreglo.** Mandar siempre la fecha con desfase (hallazgo 8) y, en la Pi, pasar la edición por el mismo `parseInputDate` que el alta. **Esfuerzo:** 30 min.

## Aislamiento entre clientes: SIN FUGA (verificado)

Con la cookie del cliente de demo intenté leer los datos de otro cliente que tiene **55 citas** guardadas (`estudio-ricardo-demo-mostoles-946279`):
```
GET /portal-api/appointments?clientId=estudio-ricardo-...  → 200  []          (0 citas, no las 55)
GET /portal-api/customers?clientId=estudio-ricardo-...     → 401
GET /portal-api/professionals|resources|google?clientId=…  → 502 unauthorized
GET /portal-api/invoices?clientId=estudio-ricardo-...      → 200  {"invoices":[]}
GET /cliente/estudio-ricardo-...  (con mi cookie)          → 500 (el fallo del hallazgo 1)
```
La Pi compara el token contra el `config.json` de ESE cliente (`clientAuthMiddleware`, `provision-http.js` línea 445), así que **no se filtra nada**.

### HALLAZGO 10 (MEDIA) — Pero un fallo de permisos se disfraza de "no tienes nada"

`appointments` e `invoices` devuelven **200 con lista vacía** cuando en realidad el acceso fue denegado (`src/lib/portal-client.ts`: `if (!response.ok) return []`). En la pantalla eso se lee como "no tienes citas" / "sin facturas". Si a un cliente se le invalida el token, verá su agenda **vacía** en lugar de "tu sesión ha caducado": llamada de pánico asegurada ("¡he perdido todas mis citas!").

**Arreglo.** Que esas funciones distingan el 401 y que el portal enseñe "sesión caducada, pide un enlace nuevo". **Esfuerzo:** 30 min.

---

# MÓVIL (375×812, emulado en Chromium)

## HALLAZGO 11 (ALTA) — En el móvil el panel se sale por la derecha: la tarjeta de "Cancelaciones" queda fuera de la pantalla

**Síntoma.** En un móvil de 375 px, la fila de números del Dashboard no se reordena: hay que arrastrar de lado para ver el final, y una tarjeta entera queda invisible.

**Medido en el navegador:**
```js
.crm-main  scrollWidth = 566   clientWidth = 360     → 206 px de contenido fuera de pantalla
.crm-kpi "Conversaciones restantes"  x=262 → 413     (cortada)
.crm-kpi "Cancelaciones"             x=425 → 566     (completamente fuera)
```
Captura: `D-movil-dashboard2.png`.

**Arreglo.** Que la rejilla de KPIs use `grid-template-columns: repeat(auto-fit, minmax(150px, 1fr))` en vez de columnas fijas. **Esfuerzo:** 20 min.

## HALLAZGO 12 (ALTA) — En el móvil, la agenda no deja leer quién viene

**Síntoma.** El calendario semanal mete 7 columnas en ~200 px. Cada cita queda en una pastilla de 11-50 px de ancho: no se lee ni el nombre ni el servicio, solo dos iconitos.

**Medido en el navegador** (semana 17/8–23/8 del cliente de demo, que sí tiene citas):
```js
.crm-tac-apt confirmed              "09:00 7646339 Cambio de aceite"   50 × 26 px
  └ .crm-tac-apt-main   width = 0   ← el nombre no se pinta
  └ .crm-tac-apt-s      width = 0   ← el servicio tampoco
.crm-tac-apt confirmed compartido   "13:00 Ricardoman ..."             11 × 52 px
```
Captura: `D-movil-citas-semana-agosto.png`.

**Impacto.** El móvil es donde el salón mira la agenda. Tal como está, en el móvil la agenda no sirve.

**Arreglo.** Por debajo de 700 px, cambiar la semana por **vista de un día** (con flechas para cambiar de día) o por una lista de citas del día. **Esfuerzo:** medio día.

## HALLAZGO 13 (MEDIA) — Textos cortados en las tres tarjetas de arriba (móvil)

**Medido:**
```js
"Sin proximas citas"                        necesita 95 px, tiene 64  → "Sin proxi…"
"Sin intervencion pendiente"                necesita 141 px, tiene 64 → "Sin interv…"
"Estimado segun horario y duracion media"   necesita 220 px, tiene 72 → "Estimado se…"
```
**Arreglo.** Quitar el recorte (`text-overflow: ellipsis` / `white-space: nowrap`) y dejar que el texto salte de línea, o acortar los textos. **Esfuerzo:** 10 min.

## HALLAZGO 14 (MEDIA) — El enlace "Soporte" se cuela por el borde izquierdo con el menú cerrado (móvil)

**Medido:** con el menú lateral escondido (`transform: translateX(-220px)`), el enlace "Soporte" queda en `x = -29, ancho 42` → **13 px asomando** encima del contenido. Se ve un "rte" suelto en el borde izquierdo de todas las pantallas. Es el mismo desbordamiento del hallazgo 3.

## HALLAZGO 15 (MEDIA) — Botones demasiado pequeños para un dedo

**Medido en Configuración a 375 px:** el botón de borrar servicio (🗑) mide **10 × 22 px**; la casilla de "modo equipo", 15 × 17 px. El mínimo recomendado es 44 × 44. En el móvil, borrar un servicio es cuestión de suerte. **Esfuerzo:** 15 min.

---

# SEGURIDAD DE LA VISTA (lo que toca al portal)

## HALLAZGO 16 (ALTA) — La llave permanente del cliente está escrita en el HTML del portal, y en esa misma página corren tres scripts de terceros

**Síntoma.** El token de acceso (64 caracteres, **sin caducidad**, el mismo que abre todo el portal) se imprime en el HTML como `data-inbox-token` y cualquier JavaScript de la página puede leerlo:
```js
document.getElementById('crm').dataset.inboxToken   →  "119f3ca0c6…"  (64 caracteres)
```
```
$ grep -o 'data-inbox-token="[^"]\{0,12\}' portal.html
data-inbox-token="119f3ca0c6a4
```
Y en esa misma página se cargan, medido con `performance.getEntriesByType('resource')`:
```
https://bzrcdn.openai.com/sdk/oaiq.min.js      (píxel de OpenAI Ads)
https://plausible.io/js/script...js            (analítica)
https://js.stripe.com/v3/
https://cdn.jsdelivr.net , fonts.googleapis.com , fonts.gstatic.com
```

**Por qué importa.** La cookie está bien puesta (`httpOnly`), lo que impide que un script la lea… pero luego el mismo token se deja escrito en el HTML, así que la protección no sirve de nada. Cualquier script de terceros comprometido —o un fallo de XSS— se lleva una llave que **no caduca nunca** y con la que se entra al portal de ese salón para siempre.

**Además:** ese token viaja en la URL del iframe de Chats (`https://pi.nexux.pro/client/<id>/inbox?t=<token>`), y las URLs quedan en logs y en el historial del navegador.

**Arreglo.**
1. Quitar los píxeles de publicidad y analítica de las páginas `/cliente/*` (no pintan nada en el panel privado del cliente).
2. No imprimir el token en el HTML: que el iframe apunte a una ruta propia (`/portal-api/inbox`) que ponga el token en la cabecera desde el servidor.
3. A medio plazo, tokens de sesión con caducidad, separados del token permanente del cliente.

**Esfuerzo:** 1 y 2 en ~1 h; 3 es un cambio mayor.

---

# TEXTOS Y PRECIOS

## HALLAZGO 17 (MEDIA) — Faltan acentos por todo el panel

Lo que ve el cliente, tal cual: "Sin proximas citas", "Sin intervencion pendiente", "Estimado segun horario y duracion media", "Selecciona una conversacion", "Miercoles", "Sabado", "Sin conversaciones aun", "Cambio de neumaticos", "Acceso al portal de tu salon" (login). En un producto de pago da sensación de descuido. **Esfuerzo:** 30 min de repaso.

## HALLAZGO 18 (BAJA) — Los precios se pintan a la inglesa

En Configuración → Mis servicios se lee **"47.5 €"** y **"45.2 €"**. En España es "47,50 €". Usar `toLocaleString('es-ES', {style:'currency', currency:'EUR'})`. **Esfuerzo:** 10 min.

## HALLAZGO 19 (BAJA) — La tabla de servicios se apelotona

Las cabeceras se leen pegadas: "DuraciónPrecio". Medido: la tabla ocupa 252 px dentro de una tarjeta de 1115 px, y las celdas se tocan (`Duración` acaba en x=467, `Precio` empieza en x=466). **Arreglo:** `width:100%` en la tabla y `padding: .4rem .8rem` en las celdas. **Esfuerzo:** 10 min.

## HALLAZGO 20 (BAJA) — La pestaña Chats es negra dentro de un panel blanco

El Inbox se sirve en un iframe con su propio diseño oscuro; el resto del portal es claro. Parece otro producto. Y con cero conversaciones dice "Selecciona una conversacion" en vez de explicar que aún no hay ninguna. **Esfuerzo:** 1 h.

---

# TABLA DE COMPROBACIONES

| # | Qué | Cómo (exacto) | Resultado | Evidencia |
|---|---|---|---|---|
| 1 | Carga del portal con enlace válido | Navegador limpio → `https://nexux.pro/cliente/nexux-demo-mostoles-42a928?t=<token>` | **OK** | Redirige a `/onboarding` en la primera visita (marca `nx_ob_<id>` en el navegador); luego entra al panel |
| 2 | Portal con la sesión caducada | `curl -H 'Cookie: nexux_token=TOKEN-INVALIDO'` sobre el portal | **FALLO** | HTTP 500, cuerpo de 0 bytes (hallazgo 1) |
| 3 | Recuperar acceso tras caducar | `curl -IL` sobre `/cliente/<id>/login` con cookie inválida | **FALLO** | 302 al panel → 500. Bucle sin salida (hallazgo 1) |
| 4 | Portal sin cookie | `curl` sin cookie | **OK** | 302 → `/cliente/<id>/login` |
| 5 | Pantalla de pedir enlace nuevo | Navegador 375×812 con cookies borradas | **OK** | Se ve bien, 0 errores de consola. Captura `D-movil-login.png` |
| 6 | Dashboard (escritorio 1440×900) | Navegador | **OK con pegas** | Datos reales (Estado, backup 3 sept 04:00). Pie del menú roto (hallazgo 3) |
| 7 | Citas — calendario semanal (escritorio) | Navegador | **OK** | Se ve la semana; las citas del 22/8 se pintan |
| 8 | Citas — crear cita a mano | Modal "+ Nueva cita" → Reservar | **FALLO** | 500 `La fecha debe incluir Z o un desplazamiento horario explícito` (hallazgo 8) |
| 9 | Chats | Navegador | **OK con pegas** | Carga el Inbox en iframe; estética negra dentro de un panel claro (hallazgo 20) |
| 10 | Clientes (plan 29 €) | Navegador | **OK con pegas** | Sale el candado de venta del plan Equipo; texto mal escrito (hallazgo 6) y 403 en consola |
| 11 | Clientes (plan 79 €) | Portal del cliente de prueba `equipo` | **OK** | Se desbloquea y el estado vacío está bien redactado |
| 12 | Canales — Telegram | Navegador | **FALLO** | El QR no se dibuja nunca; "Descargar QR" sin destino (hallazgo 4) |
| 13 | Canales — WhatsApp | Navegador | **OK** | QR real de 200×200 con el aviso de las 24 h |
| 14 | Canales — Google Calendar | Navegador | **PARCIAL** | La tarjeta carga (`/portal-api/google` → 200); conectar de verdad no se probó (requiere cuenta de Google) |
| 15 | Configuración — guardar servicios | Añadí "PRUEBA-AUDITORIA", guardé, leí el `config.json` por SSH, borré y volví a guardar | **OK** | El dato llegó al disco de la Pi y la limpieza dejó el fichero idéntico al backup |
| 16 | Aviso de "Guardado" | Medí la opacidad del toast tras pulsar | **OK** | Visible de 0,75 s a 3 s |
| 17 | Facturación (cuenta sin Stripe) | Navegador | **OK** | Explica bien por qué no hay suscripción que gestionar |
| 18 | Facturación (plan Equipo 79 €) | Portal del cliente de prueba `equipo` | **FALLO** | Dice "749€/mes" y ofrece 3 planes retirados (hallazgo 7) |
| 19 | Botón "Gestionar suscripción" (Stripe) | — | **NO VERIFICADO** | No existe hoy ningún cliente con Stripe: los 18 `config.json` de la Pi no tienen `stripe_customer_id` |
| 20 | Aislamiento entre clientes | Con la cookie del cliente A pedí los datos del cliente B (que tiene 55 citas) | **OK** | 401/502 y listas vacías; no se filtró ni una cita |
| 21 | Endpoints sin sesión | `curl -X POST` a los 13 endpoints de `/portal-api/` sin cookie | **OK** | Todos 401/404 salvo `resend-link`, que responde 200 a propósito y solo envía al email del dueño (comprobado en el código de la Pi, línea 676) |
| 22 | Consola del navegador | Recorrido completo de las 7 pestañas | **FALLO** | 404 fijo en `/api/analytics/ob`, 403 en `customers`, 500 al crear cita, aviso `same-origin` en todas |
| 23 | Móvil 375×812 | Emulación en Chromium | **FALLO** | Desborde lateral de 206 px, agenda ilegible, textos cortados, botones de 10 px |
| 24 | Fecha de las citas guardadas | Recorrí los 17 `appointments.json` buscando fechas sin zona horaria | **OK** | Todas llevan zona: 0 citas en formato antiguo |
| 25 | Token en el HTML del portal | `grep data-inbox-token` sobre el HTML servido + lectura desde JS | **FALLO** | El token de 64 caracteres, sin caducidad, es legible por cualquier script (hallazgo 16) |

# NO VERIFICADO (y por qué)

1. **Botón "Gestionar suscripción" (portal de Stripe).** Hoy **ningún** cliente tiene suscripción de Stripe (recorrí los 18 `config.json`: ninguno con `stripe_customer_id`), así que el botón no llega a pintarse en ninguna cuenta real. Sin eso solo se puede leer el código, y leer no es verificar. Queda pendiente para cuando exista el primer cobro real.
2. **Botón "Reactivar WhatsApp".** Habría abierto una sesión nueva de WhatsApp en una Pi de 3,7 GB que ya está en bucle de reconexión (el log muestra "QR code received" en bucle y "Too many reconnect attempts"). No lo he disparado para no empeorar la estabilidad. Sí está comprobado que el endpoint existe y exige sesión (`POST /portal-api/wa-reactivar` sin cookie → 401).
3. **Botón "Generar web".** Regenera la web pública del cliente: es un efecto real sobre datos del cliente y estaba fuera de lo autorizado.
4. **Envío real del email de "enlace nuevo".** Habría mandado un correo de verdad. Solo he comprobado la cadena (portal → Pi) y que la Pi solo envía si el email coincide con el del dueño. En el log de la Pi hay un `[resend-link] … enlace enviado` de una sesión anterior, pero **eso no lo he verificado yo hoy**.
5. **Conectar Google Calendar de verdad.** Requiere una cuenta de Google y consentimiento; solo comprobé que la tarjeta carga sin error.
6. **El desfase horario real al editar una cita** (hallazgo 9): confirmar la hora movida exigía mover una cita de verdad. Verificado solo que el endpoint acepta fechas sin zona.
7. **Rendimiento medido (Lighthouse/Core Web Vitals).** No entra en esta área y habría cargado la Pi.

# DATOS DE PRUEBA CREADOS Y BORRADOS

| Qué | Dónde | Estado |
|---|---|---|
| Servicio "PRUEBA-AUDITORIA / 15 min / 12,5 €" | `clients/nexux-demo-mostoles-42a928/config.json` | **BORRADO**. El fichero quedó byte a byte igual que la copia previa (`md5 3efe9bb0e419757534d24e3dcde3f012`) |
| Cliente `prueba-auditoria-equipo-d` (copia del de demo con plan `equipo`) | `clients/prueba-auditoria-equipo-d/` | **BORRADO** (`ls` confirma que ya no existe). No se arrancó ningún bot: PM2 no se tocó |
| Intento de cita "PRUEBA-AUDITORIA" 4-sept 10:00 | — | No llegó a crearse (el alta falla, hallazgo 8) |
| Copias temporales en `/tmp` de la Pi | `/tmp/auditD-*.json`, `/tmp/portal.html`, etc. | **BORRADAS** |

*Nota: en `clients/` hay dos carpetas `clinica-prueba-auditoria-madrid-*` que **no** son mías (son de otra área de esta misma auditoría). Alguien debería recogerlas.*

# LO QUE NO SE HA TOCADO

Ni `git push`, ni `pnpm build`, ni `pm2 restart`, ni instalación de paquetes, ni un solo cambio de código. Ningún pago. Ninguna suscripción cancelada. Ningún dato de cliente real modificado (no hay ningún cliente facturando hoy). Carga de la Pi al empezar 0,31 y al terminar 0,85: nunca cerca del límite.

---

**Capturas de pantalla** (19, subidas a la Pi): `~/nexux-pro/progress/auditoria-lanzamiento-20260903/capturas-D/`
