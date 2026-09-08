# Plan Equipo (79 €) — qué falta para poder decir que funciona

> Lista levantada el 7-sept-2026 contrastando código, Stripe y las 21 cuentas reales.
> Regla: nada se tacha de aquí sin prueba re-ejecutable. El que ejecuta no cierra.

## Titular
El producto de 79 € **está sin estrenar**. No es que falle: nadie lo ha usado nunca.
Stripe → 0 suscripciones a `price_1UBHkE2SQwDzHtsFTVWQ67l5` en toda su historia.
Cuentas en plan `equipo` → 0 de 21.

## Lo que SÍ está probado (base de la que se parte)
- Precio de 79 €/mes existe y está activo en Stripe.
- `lib/planes.js`: qué desbloquea cada plan, en un solo sitio. 12 tests verdes.
- Subir/bajar de plan: 5 tests verdes (bajar NO borra las agendas).
- Alta con equipo inicial: 7 tests verdes.
- Fichas de cliente: 16 tests (no re-ejecutados hoy, ver punto 7).
- Mover cita entre profesionales: el código borra en un calendario y crea en el otro, y
  quien lo llama SÍ guarda el identificador nuevo (comprobado en `provision-http.js:1566`).
- Google OAuth vivo: 2 cuentas conectadas, sin revocar; el permiso del 22-ago se renovó solo
  el 7-sept a las 08:20.

## La lista

| # | Qué | Estado |
|---|-----|--------|
| 1 | Nadie ha comprado ni dado de alta nunca el plan de 79 | **CERRADO 7-sept** |
| 2 | Ningún profesional tiene calendario propio asignado en ninguna cuenta | ABIERTO |
| 3 | Google muestra "app no verificada" — falta el vídeo de Ricardo | ABIERTO (Ricardo) |
| 4 | Mover una cita de una persona a otra: CERO tests | **CERRADO 7-sept** |
| 5 | El desplegable "qué calendario usa cada persona" nunca se ha visto funcionar con Google real | A MEDIAS: mecanismo probado |
| 6 | La garantía de 30 días no existe en ningún sistema, solo en el texto | ABIERTO (decisión) |
| 7 | Los tests escriben dentro de `clients/` de producción | ABIERTO — y VOLVIÓ A PASAR |
| 8 | `STRIPE_PRICE_EQUIPO` en Vercel: no se puede leer desde la Pi | ABIERTO |

### Detalle
1. **Sin estrenar.** Todo lo demás cuelga de esto.
2. **Sin calendarios por persona.** Los tests prueban que el código ELIGE bien el calendario;
   no que la cita APAREZCA en el Google de esa persona.
3. **App no verificada.** En el plan de 29 es un susto; en el de 79 conectar Google no es
   opcional, es el producto.
4. **Mover cita.** La operación más delicada del plan: si se corta por la mitad, el cliente
   pierde la cita de verdad. Es la promesa nº2 de la página de ventas.
5. **Elegir calendario.** La página promete "eliges de tu lista qué calendario usa cada persona".
   El `<select>` existe (`cliente/[id].astro:1264-1321`); no está visto contra Google real.
6. **Garantía 30 días.** Ni Stripe ni la Pi la registran. Además el pago de 79 cobra al momento,
   sin prueba gratis, mientras el guion de Lara ofrece 7 días gratis sin tarjeta por otro camino.
7. **Tests sobre datos reales.** `clientes.test.mjs` crea `clients/__prueba-clientes-tmp` dentro
   de producción y lo borra al final; si el test se corta, se queda. Ya pasó (quedó `salon-publico`).
8. **Variable de Vercel.** Si estuviera mal puesta taparía el precio bueno; nadie se enteraría
   hasta que alguien intentase pagar.

## Plan de ataque
Los puntos **1, 2, 4 y 5 se cierran en una sola pasada**: cuenta con plan `equipo` sin cobro →
dos profesionales → Google conectado → un calendario para cada una → dos citas → mover una de una
persona a la otra → mirar los DOS calendarios de Google.
El paso de Google exige el login de Ricardo; hasta ahí llega el trabajo sin él.


---

## Progreso 7-sept-2026 (mañana)

**Punto 1 — CERRADO.** Cuenta `prueba-equipo-79-mostoles-dca1db` dada de alta por el camino real
(`POST /provision`, `accountMode: manual_paid`, sin cobro). Resultado: `plan: equipo`, dos
profesionales creadas solas (`pro_1`, `pro_2`), `multiEmployee: true` y las dos capacidades de pago
desbloqueadas — `{"agenda_por_profesional": true, "fichas_clientes": true}`, comprobado tanto en el
fichero como en el endpoint que consume el panel (`/client/:id/status` y `/client/:id/professionals`).
El portal carga (134 KB) con la pestaña Clientes.
**De regalo**: el correo de alta salió y Brevo confirma `from: info@nexux.pro`, evento `delivered`
(messageId `<202609070941.29079700293@smtp-relay.mailin.fr>`). Eso cierra el "no verificado" que
quedaba del cambio de correo de anoche: ya no es solo código, es un correo entregado de verdad.

**Punto 4 — CERRADO.** `test/mover-cita-de-agenda.test.mjs`, 6 comprobaciones, sin tocar Google
(se sustituye `fetch`) y sin tocar datos reales (carpeta temporal). Cubre: se borra en la agenda de
Ana y se crea en la de Marta · el orden (borrar ANTES de crear, o la cita estaría en las dos) ·
el evento lleva nombre y servicio de verdad · misma persona = solo actualizar · sin plan Equipo no
se mueve nada · y el caso feo: si Google rechaza la creación después del borrado, la cita queda
apuntada como perdida y quien llama se entera.
**5 sabotajes, los 5 cazados** (`scripts/sabotaje-mover.py`): crear antes de borrar · no borrar el
viejo · devolver `true` en vez del identificador nuevo · ignorar el plan · no apuntar la cita perdida.
Restaurado idéntico por md5.

**Punto 5 — a medias.** El mecanismo está probado contra Google de verdad: `/client/:id/google/status`
sobre la cuenta que ya tiene Google conectado devuelve 2 calendarios reales, que es justo lo que
alimenta el desplegable. Falta hacerlo en la cuenta de 79, y eso exige el login de Ricardo.

**Punto 7 — peor de lo escrito.** El ledger del 4-sept dice que el fixture `salon-publico` se borró.
**Está otra vez ahí, con fecha 5-sept**: se anotó la regla pero no se arregló la causa y volvió a
pasar al día siguiente. Además `lib/clientes.js` resuelve `clients/` desde la posición del módulo
(no desde el directorio de trabajo), así que el arreglo no es mover el test: hay que poder
redirigir esa raíz. Sin eso, `clientes.test.mjs` no se puede ejecutar sin escribir en producción.

## Lo que toca ahora (necesita a Ricardo)
Conectar Google en `https://nexux.pro/cliente/prueba-equipo-79-mostoles-dca1db`. Con eso se cierran
los puntos 2 y 5, se ve con sus ojos el aviso del punto 3, y queda el camino libre para la prueba
final: dos citas, mover una de una persona a otra y mirar los DOS calendarios.

---

## Progreso 7-sept-2026 (mediodía) — con el Google de Ricardo conectado

**Punto 2 — CERRADO con prueba real.** Ana → calendario "Centro Lena", Marta → calendario personal.
Dos citas creadas desde el CRM y **Google confirma** que cada una está en la agenda de quien toca
(`scripts/mirar-calendarios.mjs`, que pregunta a Google, no al CRM). Es la primera vez que esto
ocurre en la vida del producto.

**Punto 5 — CERRADO.** El desplegable se alimenta de `/client/:id/google/status`, que devolvió los
2 calendarios reales de la cuenta, y lo elegido quedó guardado en `professionals[].calendar_id`.

**Punto 4 — cerrado también en el mundo real.** La cita de Lucia pasó de la agenda de Ana a la de
Marta: **desapareció de una, apareció en la otra** con identificador nuevo, y el CRM guardó ese
identificador (`k111bkh4l4ps5ref0lccsgoe5o`). No se quedó en las dos. Al cancelarla, desapareció de
las dos agendas. Los calendarios de Ricardo quedaron limpios.

**Fichas de cliente — probadas de verdad.** `/customers` devuelve las dos clientas con nº de citas,
canceladas, próxima, servicio habitual y profesional habitual. La nota y las preferencias se guardan
y se releen (`"No le gusta el agua caliente"`, `"Siempre con Marta"`).

### 🔴 FALLO ENCONTRADO Y ARREGLADO — la promesa nº2 no funcionaba
Cambiar **solo** de profesional devolvía `400 no_changes`. El endpoint contaba los cambios ANTES de
anotar el cambio de persona (`provision-http.js:1530` vs `:1535`), así que había que tocar además el
nombre, el servicio, la hora o la duración para que colara. **Mover una cita de una persona a otra
—lo que vende la página— era imposible.** Nadie lo vio porque nadie tenía el plan.
Arreglado (commit `5844f84`), con `test/cambiar-de-profesional.test.mjs` (4 comprobaciones contra la
ruta real) y saboteado: sin el arreglo, rojo.

### Dos fallos NUEVOS, salidos de ejecutarlo de verdad

| # | Qué | A quién afecta |
|---|-----|----------------|
| 9 | Editar cualquier cita de una cuenta **sin servicios configurados** devuelve 500 `invalid_service` | LOS DOS planes |
| 10 | Con agendas por persona, la avería de un calendario se da por "recuperada" cuando entra la cita de OTRA persona | Solo el de 79 |

**9.** Toda cuenta nace con `services: []` (a propósito: los pone el dueño en el onboarding). Una cita
creada antes de configurar servicios se guarda con un servicio improvisado (`svc_adhoc_corte`) que el
motor de reservas no encuentra al editar → `booking-engine.js:546` → 500. O sea: **el dueño recién
comprado puede crear citas pero no puede modificarlas** hasta que configure el catálogo, y las de
antes se quedan sin poder tocarse. Sin arreglar.

**10.** El estado de avería del calendario es **por cliente, no por calendario**. Se vio en vivo:
a las 10:06:27 quedó apuntada la cita de Lucia como perdida (`error_api`), y a las 10:06:28 el sistema
la dio por `recuperado` porque la cita de Carmen —en OTRO calendario, el de Marta, que sí funcionaba—
entró bien. Con agendas por profesional, el calendario roto de una persona lo tapa el calendario sano
de otra: el negocio se queda pensando que va todo bien mientras las citas de esa persona no llegan.
El sistema de avisos es anterior al plan Equipo y no se adaptó. Sin arreglar.

## Estado de la lista
1 CERRADO · 2 CERRADO · 3 abierto (vídeo de Google, Ricardo) · 4 CERRADO · 5 CERRADO ·
6 abierto (garantía 30 días, decisión) · 7 abierto (tests sobre datos reales) · 8 abierto (variable Vercel) ·
**9 y 10 nuevos, abiertos**.

---

## Progreso 7-sept-2026 (tarde) — punto 9 arreglado

**Punto 9 — CERRADO.** `lib/booking-bridge.js`, commit `57514c6`.
La causa: `changeAppointment` construía la configuración del motor **solo con lo que cambiaba**, así
que el servicio improvisado de la cita no se reconstruía, el motor no lo encontraba y devolvía 500.
El arreglo toca solo el caso roto: si quien edita no menciona el servicio, se toma el de la cita, y
únicamente cuando ese servicio NO está en el catálogo.
Probado: 5/5 en `test/cambiar-de-profesional.test.mjs` (la nueva usa una cuenta sin catálogo);
saboteado → rojo; `booking-bridge` y `booking-engine` siguen verdes (sin regresión).
En producción con Google real: cita "Mechas" (fuera del catálogo) creada en la agenda de Ana, movida
a la de Marta y borrada de Google al cancelar.

### Dos fallos NUEVOS, encontrados al probarlo

| # | Qué | Gravedad |
|---|-----|----------|
| 11 | Crear una cita y editarla **enseguida** deja el calendario desincronizado para siempre, sin aviso | alta |
| 12 | `deleteCalendarEvent` no mira la respuesta de Google: escribe "🗑 Evento eliminado" aunque no se haya borrado | media |

**11.** El evento de Google se crea *después* de responder al CRM, y su identificador se guarda al
volver. Si el dueño edita la cita en ese hueco (segundos), el endpoint ve la cita **sin**
`google_event_id`, se salta el calendario entero y no vuelve a intentarlo nunca. La cita queda en la
agenda de la persona equivocada o a la hora vieja, **y no salta ningún aviso**: la alarma de "cita
perdida" solo se dispara cuando falla la creación, no cuando la sincronización se salta.
Visto en vivo el 7-sept: cita creada y movida en la misma orden → el CRM decía Marta y Google seguía
mostrando `[Ana] Mechas`. Con 8 segundos de margen, la misma secuencia funciona perfecta.

**12.** `lib/calendar.js` → `deleteCalendarEvent` hace el `fetch` y registra "Evento eliminado" sin
comprobar `resp.ok`. Google devolvió 404 (se pedía borrar en el calendario equivocado) y el log dijo
que se había borrado igual. Un borrado fallido parece un éxito, en el log y en cualquier auditoría
que se base en él.

## Estado de la lista
1 CERRADO · 2 CERRADO · 3 abierto (vídeo Google, Ricardo) · 4 CERRADO · 5 CERRADO · 6 abierto ·
7 abierto · 8 abierto · **9 CERRADO** · 10 abierto · **11 y 12 nuevos, abiertos**.

---

## Progreso 7-sept-2026 (tarde-2) — puntos 11 y 12 arreglados

**Punto 11 — CERRADO.** `lib/cola-calendario.js` (nuevo) + `provision-http.js`, commit `17d25ba`.
Causa: el evento de Google se crea después de contestar al CRM y su identificador se guarda al volver;
si el dueño editaba en ese hueco, la edición leía la cita **sin** `google_event_id`, se saltaba el
calendario entero y no lo reintentaba nunca.
Arreglo: todo lo que toca el calendario de UNA cita (crear, editar, cancelar) pasa por una fila y se
ejecuta en orden; la edición relee la cita cuando le toca el turno. La fila es **por cita**: dos citas
distintas no se esperan, y si una tarea falla la siguiente corre igual. Además, si al editar la cita
sigue sin evento, se crea ahora con los datos ya editados en vez de dejar la agenda descuadrada.

**Punto 12 — CERRADO.** `lib/calendar.js`. `deleteCalendarEvent` ya distingue borrado (2xx), "ya no
estaba" (404/410) y rechazo, y devuelve true/false. Antes escribía "🗑 Evento eliminado" pasara lo que
pasara.

**Pruebas**: `test/cola-calendario.test.mjs` (6) · una nueva en `test/cambiar-de-profesional.test.mjs`
que reproduce la carrera contra la **ruta real** con un Google simulado y **lento** (uno instantáneo no
abre el hueco) · 4 más en `test/mover-cita-de-agenda.test.mjs` para el borrado.
**3 sabotajes, los 3 cazados** (`scripts/sabotaje-cola.py`): quitar la fila entera · sacar solo la
creación de la fila · devolver el borrado a que no mire la respuesta. Restaurado idéntico por md5.
**Regresión**: 94 comprobaciones verdes en 13 ficheros de test.

**En producción con Google real**, repitiendo lo que falló por la mañana:
- cita creada con Ana y editada a Marta **sin esperar nada** → desaparece de la agenda de Ana y
  aparece en la de Marta;
- cita creada y **cancelada sin esperar** → se crea y se borra; las dos agendas limpias.

**Nota de higiene**: `test/cambiar-de-profesional.test.mjs` se había commiteado por la mañana con
finales de línea de Windows (mi edición desde el portátil), distinto del resto del repo. Normalizado.

## Estado de la lista
1 CERRADO · 2 CERRADO · 3 abierto (vídeo Google, Ricardo) · 4 CERRADO · 5 CERRADO · 6 abierto ·
7 abierto · 8 abierto · 9 CERRADO · 10 abierto · **11 CERRADO** · **12 CERRADO**.
Quedan 4: el vídeo de Google (Ricardo), la garantía de 30 días (decisión), los tests que escriben en
datos reales, y la variable de Vercel. Más el 10, que es de la misma familia que el 11 y 12.

---

## Progreso 7-sept-2026 (tarde-3) — punto 10 arreglado

**Punto 10 — CERRADO.** Commit `4fc9d6b`. Tres sitios:
1. `lib/alerta-calendario.js`: el estado de avería pasa a guardarse **por agenda**. Escribir en la de
   Marta cierra la de Marta y la avería global de acceso (si se pudo escribir, el token funciona), pero
   **no toca la de Ana**. La cortesía de una hora entre avisos también es por agenda. El resumen del
   cliente conserva los campos de siempre (no rompe al vigilante ni a ningún panel) y añade `agendas`
   y `agendas_rotas`.
2. `lib/calendar.js`: dice **qué** agenda falló o funcionó, con nombre de persona ("agenda de Ana"),
   no un identificador de Google. Y `agendasEnUso()`, que lista todas las agendas de un negocio.
3. `scripts/vigilante-calendario.mjs`: **revisa todas las agendas**, no solo la del negocio. Hasta hoy
   una agenda de profesional rota no se comprobaba nunca y el parte diario decía "OK" mirando otra cosa.

**Efecto secundario detectado y cerrado**: al guardar el estado por agenda, un calendario mal elegido
quedaba apuntado como roto **para siempre** cuando el dueño lo corregía. `olvidarAgendas()` lo limpia
en cuanto cambia la elección en el CRM, y también en el repaso del vigilante.

**Pruebas**: `test/averia-por-agenda.test.mjs` (12) · +5 en `agenda-por-profesional` (qué agendas hay
que vigilar) · +2 en `mover-cita-de-agenda` (que `calendar.js` diga de qué agenda habla).
**4 sabotajes, los 4 cazados**: estado por cliente otra vez · el fallo sin agenda · el acierto sin
agenda · el vigilante mirando solo la del negocio. Restaurado idéntico por md5.
**Regresión**: 123 comprobaciones verdes en 15 ficheros.

**En producción**, reproduciendo el fallo de la mañana: con la agenda de Marta rota a propósito, su
cita falla y la de Ana entra bien → estado `fallo`, `agendas_rotas: ["agenda de Marta"]`, 1 cita
perdida. **Por la mañana eso decía "recuperado" un segundo después.** Al devolver la agenda buena, la
avería huérfana desapareció sola. El vigilante ahora lista "agenda del negocio" y "agenda de Marta"
por separado. Los calendarios de Ricardo quedaron vacíos en los 4 días de prueba.

## Estado de la lista
1 ✅ · 2 ✅ · 3 abierto (vídeo Google, Ricardo) · 4 ✅ · 5 ✅ · 6 abierto (garantía 30 días, decisión) ·
7 abierto (tests que escriben en datos reales) · 8 abierto (variable de Vercel) · 9 ✅ · **10 ✅** ·
11 ✅ · 12 ✅.
**Quedan 4, y ninguno es código de producto**: el vídeo de Google, una decisión de negocio, la higiene
de los tests y una variable de Vercel que no se puede leer desde la Pi.

---

## 7-sept-2026 (tarde-4) — punto 8 cerrado, y la pregunta de fondo de Ricardo

**Punto 8 — CERRADO, sin tocar código.** Se leyó el entorno real de Vercel con el `VERCEL_TOKEN` que
hay en el `.env` de la Pi (`GET api.vercel.com/v9/projects/nexux-pro/env`).
**Lo que hay**: `STRIPE_PRICE_PRO`, `STRIPE_PRICE_STARTER`, `STRIPE_PRICE_TOTAL` — los **tres planes
retirados** el 21-ago. **Lo que NO hay**: `STRIPE_PRICE_RECEPCIONISTA` ni `STRIPE_PRICE_EQUIPO`, los
dos que se venden.
**Por qué funciona igual**: el código usa `process.env[...] || priceFallback`, y los dos fallbacks son
los precios buenos (verificados activos en Stripe: 29 €/mes y 79 €/mes).
**Probado sobre el botón desplegado**, no sobre el código: `POST https://nexux.pro/api/stripe/create-session`
con `{"plan":"equipo"}` → sesión `cs_live_…` con `price_1UBHkE2SQwDzHtsFTVWQ67l5`, **79 €/mes**,
`mode: subscription`, `metadata.plan: equipo`, vuelve a `/gracias?plan=equipo`. Sesión de prueba
expirada después. **Riesgo residual**: las tres variables de planes muertos son una trampa — quien
cambie un precio ahí creerá que ha hecho algo y no habrá hecho nada.

## ¿Se entera el sistema de compra, cancelación y renovación?

**Sí, de las dos primeras. Verificado, no supuesto:**
- **Compra** → `https://nexux.pro/api/webhook/stripe`, activo, `api_version 2025-08-27.basil` (la misma
  de la cuenta), evento `checkout.session.completed`. Responde 400 a lo no firmado.
- **Cancelación / renovación / impagos** → `https://pi.nexux.pro/webhook/stripe`, activo,
  `api_version` nula (usa la de la cuenta, que es lo correcto), 5 eventos:
  `customer.subscription.updated`, `.deleted`, `invoice.paid`, `invoice.payment_failed`,
  `invoice.payment_action_required`. Responde 400 a lo no firmado.
- **Prueba real, no sintética**: `prueba-nexux-pro-c43c20` (cliente de Stripe real `cus_VCHnSFwP5PjSkz`)
  está `active: false`, `deactivationReason: subscription_cancelled`, `deactivatedAt 2026-09-04T11:03:11Z`.
  La cancelación de verdad desactivó la cuenta sola.
- **Cambio de plan 29↔79**: `PRICE_TO_PLAN` incluye los dos precios vigentes y `precios-mapeados.test.mjs`
  (3/3) lo protege. Al subir a Equipo además crea las agendas por profesional.

### 🔴 Lo que NO está cubierto — punto 13 (nuevo)

**Nadie comprueba que Stripe y la Pi digan lo mismo.** No existe ningún trabajo que compare las
suscripciones de Stripe con las cuentas de la Pi. Si un webhook no llega —que es EXACTAMENTE lo que
pasó durante 4 meses con el `api_version`— no salta nada:
- un cliente que cancela se queda **activo** y usando el servicio gratis;
- un cliente que paga y cuyo alta falla se queda **sin cuenta** y nadie lo sabe.

**Y "cuánto les queda" no existe en ningún sitio.** La Pi nunca guarda `current_period_end`: el panel
solo muestra `trialEndsAt` y `expires_at`, que son de las demos. De una suscripción de pago no se sabe
cuándo renueva ni cuánto falta. En cron solo hay `vigilante-calendario` (diario) y `vigilante-health`
(cada 5 min); de suscripciones, nada.

**Lo que haría falta**: un `vigilante-suscripciones` diario que compare las dos listas y avise de
cualquier descuadre, y que de paso guarde la fecha de renovación. Es justo lo que habría cazado el
desastre de los 4 meses al día siguiente.

## Estado de la lista
1 ✅ · 2 ✅ · 3 abierto (vídeo Google) · 4 ✅ · 5 ✅ · 6 abierto (garantía 30 días) · 7 abierto (tests
sobre datos reales) · **8 ✅** · 9 ✅ · 10 ✅ · 11 ✅ · 12 ✅ · **13 NUEVO y abierto** (nadie cuadra
Stripe con la Pi; no se sabe cuánto le queda a nadie).

---

# PANEL DE FACTURACIÓN (decisión de Ricardo, 7-sept) — paso 1 de 6

## Paso 1 — Vigilante de suscripciones: HECHO. Commit `4d93215`.

**Qué hace**: todos los días a las 08:40 coge las dos listas enteras —las suscripciones de Stripe y
las cuentas de la Pi— y las cuadra **en los dos sentidos**, sin fiarse de que haya llegado ningún
aviso. Y guarda en cada `config.json` la fecha real de renovación (`renuevaEl`), el estado de la
suscripción y si está marcada para cancelar. **Ese dato no existía en ningún sitio**: es la base del
paso 2.

**Qué caza**, con su gravedad:
| Situación | Qué significa |
|---|---|
| `paga_y_no_tiene_cuenta` | Stripe le cobra y en la Pi no hay cuenta |
| `paga_y_esta_desactivado` | paga y no tiene servicio |
| `no_paga_y_sigue_activo` | canceló y sigue usando el producto gratis |
| `activo_sin_suscripcion` | cuenta activa con cliente de Stripe sin suscripción reconocida |
| `plan_distinto` | paga el de 79 y figura con el de 29 (o al revés) |

**Lo que NO hace, a propósito**: no cancela, no activa y no cobra. Arreglar un descuadre es decisión
de Ricardo, no de un cron. Y sin `STRIPE_SECRET_KEY` sale con código 2 en vez de decir "todo bien"
sin haber mirado.

**Un detalle que habría hecho inútil el vigilante**: la cuenta de Stripe es la **misma para nexux.es**.
Sin filtrar, las suscripciones de la app de citas salían como "alguien paga y no tiene cuenta". El
aviso se habría llenado de ruido ajeno y se habría acabado silenciando. Se descartan por precio.

**De paso**: `PRICE_TO_PLAN` vivía dentro de `stripe-webhook.js` y el vigilante necesitaba la misma
tabla. Se sacó a `lib/precios.js` — una sola verdad. Y `precios-mapeados.test.mjs` pasó de **leer el
texto** del fichero a **ejecutar** el módulo: antes bastaba con que el precio apareciera escrito en
cualquier línea aunque no lo usara nadie.

**Pruebas**: 22 del cuadre + 6 de precios. **5 sabotajes, los 5 cazados**: quitar el sentido Pi→Stripe ·
dar derecho a un cancelado · dejar de filtrar lo de nexux.es · dejar de calcular los días · devolverle
al webhook su propia copia de la tabla. Restaurado idéntico por md5. Regresión: 126 verdes.

**Contra Stripe de verdad**: tal como están las cuentas, 0 descuadres y salida 0. Reactivando a
propósito una cuenta que Stripe tiene cancelada → lo caza: *"Stripe dice canceled pero la cuenta sigue
activa: usa el servicio sin pagar"*, 1 grave, salida 1, aviso a Telegram. Cuenta restaurada.

**Cruce de agentes**: a las 14:05 alguien empujó a `origin` los 5 commits del día (hasta `4fc9d6b`).
No rompe nada —en la Pi el código ya estaba vivo desde cada reinicio— pero queda dicho.
---

## Paso 2 — Panel de facturación con datos reales — HECHO Y COMPROBADO EN VIVO (7-sep, 17:15)

`893b6d5` en `nexux-clients` · `bec50a8` en `nexux-pro`. **Sin push: lo autoriza Ricardo.**

**Qué había**: la pantalla de Facturación sabía el nombre del plan y tenía un botón que echaba al
cliente fuera, al portal de Stripe. De lo único que importa —si el último cobro salió, cuándo es el
siguiente, con qué tarjeta— no sabía nada.

**Qué hay ahora**: arriba del todo una tarjeta con el estado, y debajo plan, precio, la fecha y la
tarjeta. Sale del endpoint nuevo `GET /client/:id/facturacion`, que pregunta a Stripe si hace más de
6 h que no se pregunta, lo guarda y lo devuelve.

**Lo de "que dé sensación de fiable"**: eso no se consigue pintándolo todo en verde. El pie dice
**cuándo** se comprobó contra la pasarela y que eso se revisa **todos los días** (cron 08:40, el
vigilante del paso 1). El verde sale sólo cuando el dueño no tiene que hacer nada; un cobro fallido
sale en ámbar, con la frase entera y diciendo que el servicio no se corta.

**Tres fallos cazados probándolo, no leyéndolo**:
1. Se preguntaba a Stripe **en cada carga de pantalla** cuando el cliente no tenía fecha de
   renovación — o sea, los cancelados y los que acaban de comprar. La condición miraba si teníamos
   la respuesta, no si habíamos preguntado. Se vio porque la segunda llamada seguida decía
   `refrescado: true`.
2. Una **prueba gratuita dada de alta a mano** caía en la rama "no tienes que hacer nada" y se
   callaba que la prueba termina un día concreto.
3. A un cliente que **había cancelado** le ponía `PRÓXIMO COBRO` con la fecha en la que en realidad
   se le acaba el servicio. La frase de arriba lo decía bien y la etiqueta de abajo la desmentía.
   Se vio en la captura, no en el código.

**Pruebas**: 18 en `test/facturacion.test.mjs`. **7 sabotajes, los 7 cazados**: pintar un impago en
verde · afirmar "Todo en orden" sin haber mirado · decirle "se renueva" a quien ya canceló · escribir
el precio a mano en vez de sacarlo del catálogo · enseñar la fecha en formato de ordenador · esconder
que una cuenta está desactivada · redondear los días al revés. Restaurado idéntico por md5.
Regresión: **263 verdes** (la única que falla es `citas-zona-horaria`, que se niega a correr sobre
producción a propósito — es el punto 7 de esta lista, ya conocido).

**En vivo, con navegador de verdad** (`nexux-pro/scripts/`): los tres estados que importan —al día,
cobro fallido y cancelado-con-servicio-hasta— pintados y leídos en pantalla, en escritorio y en
móvil. Y las **tres formas de fallar** (la petición no llega, el servidor da error, contesta
`ok:false`): las tres acaban en el mismo aviso honesto, ninguna en un "Todo en orden" de adorno ni en
un "Comprobando…" colgado.

**Contra Stripe real**: `prueba-nexux-pro-c43c20` (`cus_VCHnSFwP5PjSkz`), suscripción de verdad. Trae
su estado (`canceled`) y su tarjeta real (VISA ···· 2520, 03/2031). Los configs que se tocaron para
simular estados se restauraron idénticos por md5.

**Dicho tal cual**: hoy **ningún cliente activo tiene pasarela** — los 6 activos son altas a mano. El
camino de pago está probado contra Stripe con una cuenta de test, no con un cliente pagando.

**Nota para el paso 4**: la frase del impago decía "actualiza la tarjeta aquí abajo" y abajo no hay
nada — eso es Stripe Elements, aún sin hacer. Cambiada, y hay una prueba que lo sujeta: cuando se
haga el paso 4, hay que cambiar la frase y la prueba a la vez.

**Se guarda la etiqueta de la tarjeta** (marca, cuatro últimos, caducidad) en el config para que no
desaparezca al recargar. Es lo que Stripe enseña en cualquier recibo. El número, el CVV y el token de
pago no tocan la Pi. Si prefieres que ni eso se guarde, se quita en dos líneas.
---

## Paso 3 — Cambiar de plan desde el panel — HECHO, PERO NO PROBADO CONTRA STRIPE (8-sep, 02:10)

`6fb2905` en `nexux-clients` · `dd0a4b2` en `nexux-pro`. **Sin push: lo autoriza Ricardo.**

**Qué hay**: en la tarjeta del otro plan, un botón "Cambiar a este plan". Antes de nada sale un cuadro
que dice exactamente qué va a pasar. Si sube: el importe de hoy, calculado **por Stripe**, no por
nosotros. Si baja: "hoy no se te cobra nada, sigues igual hasta el día X y ese día pasas a 29 €".

**Las decisiones que hay detrás, y por qué**:
- **Subir es inmediato** y se cobra hoy la parte proporcional. Se nota al momento.
- **Bajar espera al final del mes que ya está pagado.** Bajarlo hoy le quitaría las agendas por
  profesional que pagó hasta fin de mes; devolverle la diferencia no le devuelve el mes. Se hace con
  un calendario de suscripción de Stripe, y al terminar la suscripción vuelve a la normalidad.
- **Con un cobro pendiente no se toca el plan.** Primero se resuelve el cobro.
- **Desde un plan retirado no se cambia solo**: va a Soporte, y se le dice que no pierde nada.

**Dos seguros con el dinero**: clave de idempotencia (dos clics no son dos cobros) y
`error_if_incomplete` (una tarjeta rechazada NO deja a nadie en el plan de 79 sin haberlo pagado).
Los dos tienen su sabotaje.

**No se duplica el webhook.** Lo que pasa después del cambio —límites, funciones, montar las agendas
por profesional— ya lo hace el manejador de `customer.subscription.updated`. **Comprobado en los logs
de la Pi que ese webhook recibe eventos reales de Stripe** (`firma OK: customer.subscription.updated`
y una desactivación real). Copiar esa lógica aquí habría sido crear la segunda verdad de siempre.

**Pruebas**: 29 nuevas — 19 de la decisión y 10 de *qué se le pide exactamente a Stripe*, con un
Stripe de mentira inyectado. **12 sabotajes, los 12 cazados**: confirmar sin saber el importe · bajar
de golpe · cambiar con un cobro pendiente · ofrecer un plan retirado · quitar la clave de idempotencia
· dejar pasar una tarjeta rechazada · cobrar la diferencia el mes que viene · aplicar la bajada ya ·
dejar la suscripción atada al calendario · añadir una línea en vez de sustituirla (en el cambio y en
la previsualización) · callar un cambio ya programado. Restaurado idéntico por md5.
Regresión: 297 de 298.

**En vivo, en el navegador** (`nexux-pro/scripts/mira-cambio-plan.py`): subida sin importe → el botón
de confirmar sale **apagado** y dice por qué; bajada → confirmable, con la fecha; fallo de la pasarela
→ el aviso dice que **no se le ha cobrado nada** y el botón vuelve a encenderse. Config restaurado
idéntico por md5.

### 🔴 Lo que NO está probado, y hace falta para poder decir que sí

La clave de Stripe de la Pi es **`sk_live`**, de producción. No hay ninguna suscripción activa en toda
la cuenta. Así que **subir y bajar de plan no se han ejecutado nunca contra Stripe**: están escritos
y probados con un Stripe de mentira, pero la pasarela real no los ha visto.

Lo que sí está comprobado contra Stripe de verdad: **la forma de la petición**. Stripe rechaza la
previsualización con `invoice_upcoming_none` ("no se puede previsualizar una suscripción cancelada"),
**no** con un error de parámetros — o sea, entiende lo que le mandamos.

**Para cerrarlo hace falta una clave de pruebas de Stripe** (`sk_test_…`, del mismo panel, pestaña de
modo prueba). Con ella se crea un cliente falso con la tarjeta 4242 y se prueban subida y bajada
enteras en diez minutos, sin mover un euro. La alternativa es esperar al primer cliente que pague de
verdad, y probar el cobro con él.

**De paso**: `lib/stripe-session.js` llevaba una **tercera copia** de la tabla de precios (2900/7900 a
mano). Hoy coincide con el catálogo. Hay una prueba nueva que salta si algún día deja de coincidir.

### Pasos 4 a 6, pendientes
4. Actualizar tarjeta con Stripe Elements embebido (PCI: la tarjeta nunca toca la Pi).
5. Cancelación solo por el bot de soporte, nunca autoservicio en dos clics.
6. Quitar el botón "Gestionar suscripción" que abre el portal de Stripe.
