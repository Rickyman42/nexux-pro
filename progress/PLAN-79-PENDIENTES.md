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
---

## Paso 4 — Cambiar la tarjeta desde dentro de Nexux — HECHO, LO GRAVE PROBADO CONTRA STRIPE REAL (8-sep, 02:30)

`81579a4` en `nexux-clients` · `687bad4` en `nexux-pro`. **Sin push: lo autoriza Ricardo.**

**Cómo funciona, en llano**: la Pi le pide a Stripe un permiso de un solo uso y le da al navegador una
llave temporal. El formulario lo pinta **Stripe** dentro de nuestra página. La tarjeta va del
navegador a Stripe directamente. **Por la Pi no pasa el número, ni el CVV, ni nada que haya que
proteger** — sólo un identificador y, al final, la etiqueta (VISA ···· 4242). Eso es lo que pediste:
integrado en Nexux, pero sin que la tarjeta toque nuestro servidor.

**Lo delicado no es el formulario, es el paso siguiente.** Cuando el navegador dice "usa este
permiso", se comprueba: (1) que el permiso es de **este** cliente; (2) que Stripe lo da por bueno, no
a medias; (3) que hay tarjeta. Y se pone por defecto **en el cliente Y en la suscripción**: si sólo se
pusiera en uno, la próxima factura podría seguir intentando la tarjeta vieja.

**🟢 Probado contra Stripe de verdad** (clave `sk_live`, aquí sí se pudo):
- Se crea un permiso real (`seti_1UDCil…`) para un cliente real. **Cancelado al terminar.**
- **Un permiso de otro cliente se rechaza**: `ese permiso de tarjeta no es de este cliente`. Éste es
  el agujero grave del paso 4 y está tapado y comprobado contra la pasarela, no sólo con un simulacro.
- Un permiso inventado se rechaza (`No such setupintent`).
- Sin pasarela de pago, ni siquiera se abre: 400 y un mensaje que lo explica.

**En el navegador** (`nexux-pro/scripts/mira-tarjeta.py`): sin pasarela el botón **no aparece**; con
pasarela se monta un formulario **servido por js.stripe.com** (comprobado el origen del marco: si
fuera nuestro, la tarjeta pasaría por nosotros) y **en castellano**.

**Corregido mirando la pantalla**: el formulario salía **en inglés** ("Card number", "Expiry date") en
mitad de una pantalla en español, justo en el momento de teclear una tarjeta. Ahora `locale: 'es'`, y
la comprobación entra dentro del marco de Stripe a leer las etiquetas: si vuelve a salir en inglés,
salta.

**La frase del impago ya puede decir la verdad.** En el paso 2 se le prohibió decir "aquí abajo"
porque no había formulario, con una prueba puesta para que no se olvidara. Ahora lo hay: frase y
prueba cambiadas a la vez, en el mismo commit.

**Pruebas**: 8 nuevas. **8 sabotajes, los 8 cazados**: quitar la comprobación de a quién pertenece el
permiso · dar por buena una tarjeta a medias · dejar pasar un permiso sin tarjeta · no ponerla en la
suscripción · guardarla sin permiso para cobrar el mes que viene · devolver el método de pago entero
en vez de sólo la etiqueta · perder el cero del mes de caducidad · dejar de decir dónde se cambia.
Restaurado idéntico por md5. Regresión: 305 de 306.

**Lo único que falta por probar**: teclear una tarjeta de verdad y ver el cobro. En modo producción no
se puede usar la 4242, así que eso sigue esperando a la **`sk_test_…`** que pedí en el paso 3.

**Apuntado, no tocado**: el `.env` de la Pi tiene 5 líneas con retorno de carro de Windows (las de
Google OAuth). La aplicación va bien porque dotenv lo limpia, pero cualquier script en bash que haga
`. ./.env` se lleva el `\r` pegado al valor. Es una trampa para el futuro, no un fallo de hoy.



---

## Paso 3, cerrado: probado contra Stripe de verdad — y el fallo que destapó (8-sep, 03:05)

`54686d0` en `nexux-clients`. **Sin push: lo autoriza Ricardo.**

Con la clave de modo prueba que autorizó Ricardo (usada **solo inline**, nunca guardada en el `.env`
ni en ningún fichero) se hace el recorrido entero. Lo que faltaba del paso 3 ya no falta.

**El historial de facturas del cliente de prueba es la prueba del dinero:**

| Importe | Estado | Motivo |
|---|---|---|
| 29,00 € | pagada | alta de la suscripción |
| **50,00 €** | pagada | **la diferencia 79−29, cobrada al subir** |
| 29,00 € | pagada | renovación, ya bajado |

Los tres pasos con su comprobación: subir deja **una sola línea** (no dos planes cobrándose), el mapeo
precio→plan resuelve `equipo`; bajar **no toca nada hoy** (sigue en 79, que ya está pagado) y deja la
fase siguiente en 29 con `end_behavior: release`; y con el reloj de pruebas se adelanta un mes y **la
bajada entra sola**, con el mapeo resolviendo `recepcionista`. Eso es lo que separa "queda bien
programado" de "pasa de verdad".

### 🔴 Lo que encontró: la fecha de renovación se buscaba donde ya no está

El SDK de Stripe habla la versión de API `2026-04-22.dahlia`. En esa versión `current_period_end` se
mudó de la suscripción a su **línea**:

```
sub.current_period_end                -> undefined
sub.items.data[0].current_period_end  -> 1791421432
```

Es el mismo tipo de desajuste de versiones que dejó los webhooks muertos cuatro meses. Lo que estaba
roto sin que lo supiera nadie:

- **El panel de facturación (paso 2)** se habría quedado **para siempre** en *"la fecha de tu próxima
  renovación aparecerá aquí en cuanto la comprobemos"*.
- **El vigilante diario (paso 1)** nunca habría guardado la fecha de renovación — que es exactamente
  lo que se construyó para guardar.
- La clave que evita cobrar dos veces por un doble clic caía a `0` fijo: al no llevar el periodo, un
  cambio legítimo el mes siguiente se habría rechazado como si fuera un duplicado.

**No lo vio nadie porque hoy no hay ningún cliente pagando.** Se habría visto con el primero — y
habría sido él quien lo descubriera. En el paso 2 lo tuve delante (`renuevaEl: null` en la suscripción
real) y lo di por bueno diciéndome que una suscripción cancelada no tiene periodo siguiente. Era
verdad, y por eso tapaba el fallo.

Arreglado en un solo sitio, `finDelPeriodo()`, que mira **las dos formas**: la nueva (nuestras
llamadas) y la vieja (los avisos que Stripe manda a la Pi, que van con la versión de la cuenta,
`2025-08-27.basil`). Las dos conviven de verdad en esta casa.

### Cómo repetirlo

```
cd ~/nexux-clients
STRIPE_TEST_KEY=sk_test_... node scripts/test-cambio-plan-modo-prueba.mjs
```
El script se niega a arrancar si la clave no empieza por `sk_test_`. Crea todo, lo comprueba y lo
borra solo.

**Limpieza**: cliente, tarjeta, suscripción, calendario y reloj **borrados** (0 de cada uno en la
cuenta de pruebas, comprobado). Los **7 precios y 4 productos** de las tres pasadas quedan
**archivados, no borrados**: Stripe no permite borrar precios por API, ni productos que tengan
precios. Están inactivos y fuera del catálogo, en el entorno de pruebas aislado.

**Estado**: 313 pruebas, 312 verdes (falla sólo `citas-zona-horaria`, guardia de producción).
Sabotajes: facturación 7/7 · cambio de plan 12/12 · tarjeta 8/8 · suscripciones 7/7 — **34, ninguno se
escapa**.

**Sigue sin probarse**: teclear una tarjeta real en el formulario del paso 4 y ver el cobro. Ahora se
puede hacer con esta misma clave de pruebas; no entraba en lo que autorizó Ricardo para esta tanda.
---

## Pasos 5 y 6 — Se acaba la cancelación en autoservicio (8-sep, 04:10)

`8d5837a` en `nexux-clients` · `e884c15` en `nexux-pro`. **Sin push: lo autoriza Ricardo.**

**Había DOS formas de cancelar solo, no una.** Quitar el botón habría dejado la otra abierta:

1. El botón **"Gestionar suscripción"**, que abría el portal de Stripe (donde cancelar son dos clics).
   Fuera el botón, su lógica, el puente con la Pi y la ruta. Las dos rutas contestan **410 con lo que
   hay que hacer**, no un error seco, por si queda una pestaña vieja abierta.
2. **El propio portal de Stripe.** Se entra con un enlace público y el email del cliente, **sin pasar
   por nosotros**. Ahí se desactivó la cancelación:
   `bpc_1ShYHb2SQwDzHtsFV5Zm5t9K` → `subscription_cancel.enabled = false`. Comprobado después.
   Para volver atrás: el mismo `POST` con `features[subscription_cancel][enabled]=true`.

**En su sitio**, el bloque "¿Quieres cancelar?" que lleva al bot de soporte, y que dice **por qué** no
hay botón: para poder ayudar antes de que se vaya, y si aun así quiere irse, se le deja hecho sin
vueltas ni permanencia. Un cliente que quiere irse y no encuentra por dónde se enfada; uno al que le
dices con quién hablar, no.

**La escalada** (`POST /soporte/baja`): la llama el bot, no un cliente, así que va con el secreto del
servidor. **Aquí no se cancela nada** — hay una prueba que lee `lib/baja.js` y salta si alguien mete
una llamada que cancele. Avisa a Ricardo por Telegram con lo que necesita para decidir sin ir a buscar
nada: quién es, qué paga, desde cuándo, hasta cuándo tiene pagado, cómo localizarle, por qué se va,
qué se le ofreció, y la línea *"Nadie ha cancelado nada. Decides tú."*

**La retención es honesta**: se ofrece **una vez** y lo que encaje con el motivo. Al que le parece
caro, el plan de 29 — **no un descuento**, porque si se regala a todo el que se queja deja de valer.
Al que no lo usa, terminar de configurarlo. Al que dice que no le funciona, arreglarlo hoy *"y si no,
te damos la baja sin más vueltas"*. **A quien cierra el negocio no se le ofrece nada**, que es
faltarle al respeto. Los cuatro tienen su sabotaje.

**Cazado probándolo en vivo**: el primer aviso salió con `avisado: false` — un tropiezo de red justo
tras reiniciar, y el mensaje se habría perdido. Ahora **tres intentos** y, si aun así no sale, el
aviso entero queda escrito en el log. Un mensaje de Telegram perdido no puede ser la única traza de
que alguien se quiere ir. *(De paso: `notifyTelegram` en `stripe-webhook.js` se traga los fallos con
un `.catch(() => {})`. No lo he tocado, pero el aviso de "cliente desactivado" puede estar
perdiéndose igual. Apuntado.)*

**Comprobado en vivo**: 410 en las rutas retiradas · 401 sin secreto · 400 con motivo inventado ·
**aviso llegando de verdad a tu Telegram** (`avisado: true`, dos mensajes marcados como prueba).
En navegador (`nexux-pro/scripts/mira-baja.py`): ni "Gestionar suscripción", ni "portal de Stripe", ni
**un solo enlace a stripe.com**, ni un botón que diga cancelar. Config restaurado idéntico por md5.

**Pruebas**: 13 nuevas. **10 sabotajes, los 10 cazados.** Regresión 325/326.

### 🔴 Lo que falta para que el paso 5 funcione de verdad: el bot no existe

`@nexux_soporte_bot` **está registrado en Telegram, pero en la Pi no hay ni código, ni token, ni
proceso**. Aparece sólo como enlace: en el portal, en la página de gracias y en el email de
bienvenida. **Hoy, quien escriba ahí no le contesta nadie.**

Eso ya era así antes de este paso — no lo he roto yo — pero ahora importa mucho más: acabo de mandar
ahí a todo el que quiera cancelar. Un cliente que quiere irse y escribe al vacío es peor que un botón
de cancelar: se va igual, y además enfadado.

**Lo que hace falta**: el token de `@nexux_soporte_bot` (BotFather → `/mytoken`). Con él, el bot es
una carcasa fina: la conversación, la retención y el aviso ya están escritos y probados en
`lib/baja.js` y en `POST /soporte/baja`.

---

## Paso 4, cerrado: la tarjeta probada contra Stripe de verdad (8-sep, 04:00)

Mismo `8d5837a`. `scripts/test-tarjeta-modo-prueba.mjs`, con la clave de pruebas.

Un negocio pagando con **Mastercard ····4444**, se cambia a **Visa ····4242** por el mismo camino que
usa el portal, se adelanta un mes con el reloj de pruebas y **el cobro de la renovación sale de la
tarjeta nueva**. Las dos facturas, pagadas.

Comprobado además: la etiqueta que vuelve es `{marca, ultimos4, caduca}` y **nada más** — ni número,
ni CVC, ni nada que proteger. Y la tarjeta queda puesta **en el cliente Y en la suscripción**: si sólo
se pusiera en uno, la próxima factura seguiría intentando la vieja.

**Cazado**: mi lectura de "en qué tarjeta se cobró" fallaba, porque en esta versión de la API el pago
ya no cuelga de la factura igual. Era mi comprobación, no el producto — pero un test que no sabe leer
el resultado no prueba nada, así que se arregló antes de darlo por bueno.

```
cd ~/nexux-clients
STRIPE_TEST_KEY=sk_test_... node scripts/test-tarjeta-modo-prueba.mjs
```

**Limpieza**: cliente, tarjetas, suscripción y reloj borrados — 0 de cada uno en la cuenta de pruebas,
comprobado. Precios y productos **archivados** (Stripe no deja borrarlos). La clave no ha quedado
escrita en ningún fichero.

---

## Corrección: me equivoqué con el bot de soporte (8-sep, 05:00)

`003b021` en `telegram-claude-bot` · `b3b9a51` en `nexux-clients`. **Sin push.**

**Ricardo tenía razón.** `telegram-claude-bot` **es** `@nexux_soporte_bot`: lleva corriendo en pm2,
tiene `src/soporte.js` con su tema de baja, sus 29 pruebas y una comprobación e2e que mete un mensaje
de desconocido por el mismo camino que Telegram. Todo lo que dije de "no existe como servicio" era
falso.

**Cómo me equivoqué**: busqué la cadena `nexux_soporte` en el código y en los `.env`, y la identidad
del bot no está ahí — está **dentro del token**. Un `getMe` con ese token lo habría dicho en un
segundo, y es exactamente lo que llevo escrito en memoria: *verificar lo que EJECUTA, no lo que
documenta*. Miré el nombre de la carpeta y di por hecho lo demás.

**Donde no tenía razón Ricardo**: `provision-http.js` 2175-2200 no era un flujo previo a medio montar;
es código que escribí yo anoche. Antes de mi commit ahí estaba la ruta del portal de Stripe y
`soporte/baja` no aparecía ni una vez (`git show 81579a4`).

### Lo grave que había, y era culpa mía

El bot contestaba a quien quería irse: *"Puedes darte de baja tú mismo: Panel → Facturación →
gestionar suscripción"*. **Ese botón lo quité yo anoche.** O sea que durante unas horas el bot estuvo
mandando a un cliente que se quería ir a un sitio que ya no existe. Peor que no contestarle.

Corregido, siguiendo la decisión: **1ª vez** se le atiende, se le ofrece ayuda de verdad y se le
pregunta qué le falla; **2ª vez (insiste)** se avisa a Ricardo con lo que ha contado y al cliente se
le dice que nadie le ha tocado nada. El aviso lleva ahora "QUIERE DARSE DE BAJA" y el pie
"NADIE HA CANCELADO NADA: decides tú" — decirle "le he mandado al correo" en una baja sería falso.

**Cazado por la e2e, y era grave**: el antirrebote de 2 segundos se tragaba el segundo mensaje. El
cliente decía que se quería ir, se le ofrecía ayuda, contestaba enseguida *"no, de verdad"* — **y no
recibía nada, y el aviso no salía nunca.** Ahora el tema se mira antes de callarse y la baja no se
calla: es el único caso en que el silencio cuesta un cliente.

**Las cuatro pruebas de la baja sujetaban la política vieja** (exigían que la respuesta dijera
"Facturación"). Cambiadas a la vez que la respuesta: una prueba que sujeta una regla derogada obliga a
mantener el error.

### Y quité mi propio duplicado

`lib/baja.js` y `POST /soporte/baja` en la Pi: borrados. El bot ya hacía eso, y mi endpoint pedía un
`clientId` que el bot no tiene —sólo conoce un chat de Telegram—, así que **no se habría podido usar
nunca**. Era código muerto con un segundo formato de aviso para lo mismo.

**Lo que sí se queda de anoche**, porque no lo hacía nadie: las dos puertas al autoservicio cerradas
—la ruta del portal (410) y la cancelación en el portal de clientes de Stripe— y el bloque
"¿Quieres cancelar?" del panel.

### Evidencia

```
cd ~/telegram-claude-bot && node --test "test/*.test.mjs"        # 32/32
cd ~/telegram-claude-bot && node scripts/comprobar-soporte-e2e.mjs
cd ~/nexux-clients && node --test "test/*.test.mjs"              # 312/313
python3 ~/scripts/nexux-verify.py "service:nexux-clients" "service:telegram-claude-bot" \
  "contains:/home/nexux/telegram-claude-bot/src/soporte.js::QUIERE DARSE DE BAJA" \
  "contains:/home/nexux/telegram-claude-bot/src/soporte.js::insisteEnLaBaja" \
  "file:/home/nexux/telegram-claude-bot/scripts/comprobar-soporte-e2e.mjs"
```
E2E con el caso nuevo: primera vez → ofrecimiento y **0 avisos**; insiste → **1 aviso** con lo que
dijo. Verificador 5/5. Los dos servicios reiniciados y online: el bot corre el código nuevo.

---

## Punto 7 — Los tests ya no escriben en los clientes de verdad (8-sep, 04:50)

`ce8c6b6` en `nexux-clients`. **Sin push.**

**La causa no era un test descuidado.** La carpeta de clientes se resolvía en **27 sitios y de tres
formas distintas**: unos desde el directorio de trabajo, otros desde la posición del fichero, y sólo
`whatsapp.js` miraba una variable de entorno. En producción las tres daban lo mismo, así que nadie lo
notó nunca — pero significaba que **las pruebas no tenían a dónde escribir que no fuera la carpeta de
los clientes reales**.

La única defensa que existía era un guardia que hacía reventar un test si se ejecutaba en la Pi.
Protegía, sí, pero al precio de que ese test **no se ejecutase nunca**: llevaba semanas saliendo en
rojo en cada regresión. Un test que no corre no protege de nada.

**Lo hecho**: `lib/rutas.js` es ahora el único sitio que lo decide. Manda `CLIENTS_DIR` si está
puesta; si no, la carpeta que hay al lado del código (posición del fichero, no directorio de trabajo:
un script lanzado desde otro sitio se encontraba antes con cero clientes en vez de con un error). Los
27 sitios pasan por ahí. Los scripts de cron son CommonJS y no pueden importar un módulo ESM, así que
leen `CLIENTS_DIR` ellos mismos — que es lo que importa.

Los tests se desvían con `CLIENTS_DIR` en vez de con `chdir`. **Incluidos los que lanzan un servidor
aparte**: sin pasársela al proceso hijo, el hijo abría producción. Eso era exactamente lo que estaba
pasando.

**Una prueba nueva recorre el repo entero y falla dando nombre y línea** si alguien vuelve a
calculársela por su cuenta. Encontró **14 sitios que se me habían pasado** buscándolos a mano.

**Resultado**: **323 de 323 en verde**, incluida `citas-zona-horaria`. Y comprobado con la cuenta
antes/después: una regresión completa **ya no crea ni una carpeta ni un config**.

### 🔴 Falta que Ricardo ejecute el barrido

Son **83 carpetas de mentira** entre los **22 clientes de verdad** (`salon-de-prueba-*`,
`salon-con-prisa-*`, `salon-sin-catalogo-*`, `peluqueria-de-prueba-*`, `salon-publico`…). Comprobado
una a una: todo son citas de test ("Corte", sin nombre ni teléfono de nadie) y **ningún nombre coincide
con un cliente real**. La lista se separó por fecha del `config.json`, no por nombre, para no fiarse
de un patrón.

**No lo he borrado yo**: el guardia de seguridad de Ricardo bloquea el borrado recursivo, y hace bien.
No se ha esquivado. Copia de seguridad hecha antes de nada:
`~/backups/restos-clients-20260908.tar.gz` (94 carpetas, 16K).

El comando, para que lo ejecute Ricardo:

    cd ~/nexux-clients && xargs -d '\n' -a /tmp/barrer.txt rm -rf \
      && pm2 restart nexux-clients && sleep 8 \
      && pm2 logs nexux-clients --lines 20 --nostream | grep "clients loaded"

Tiene que decir **22 clients loaded**. Si dice otra cosa, se restaura con:

    tar xzf ~/backups/restos-clients-20260908.tar.gz -C ~/nexux-clients

La lista `/tmp/barrer.txt` se pierde al reiniciar la Pi. Se regenera con:

    cd ~/nexux-clients && comm -23 \
      <(ls -d clients/*/ | sed 's|clients/||;s|/$||' | sort) \
      <(find clients -maxdepth 2 -name config.json ! -newermt "2026-09-08 04:00" -printf "%h\n" \
        | sed 's|clients/||' | sort) \
      | sed 's|^|clients/|' > /tmp/barrer.txt

**Quedan fuera a propósito**: `conversa-rodaje.mjs` y `seed-agenda.mjs`, que otro agente está editando
ahora mismo. Los dos se calculan la carpeta por su cuenta; cuando esa persona termine, hay que
pasarlos por `lib/rutas.js`.

### Estado de la lista del producto de 79
1 ✅ · 2 ✅ · **3 abierto (vídeo de Google — Ricardo)** · 4 ✅ · 5 ✅ · **6 abierto (garantía de 30 días
— decisión de Ricardo)** · **7 ✅ (falta que Ricardo ejecute el barrido)** · 8 ✅ · 9 ✅ · 10 ✅ ·
11 ✅ · 12 ✅ · 13 ✅. Panel de facturación: los 6 pasos cerrados.

---

## Punto 6 — Garantia y cancelacion: DECIDIDO por Ricardo (8-sep-2026)

**Se cancela a mano, desde Stripe, y a proposito no se pone facil.** No hay autoservicio: ni boton
en el panel, ni el portal de Stripe. Las dos puertas ya estaban cerradas el 8-sep; esto lo confirma
como decision, no como estado provisional.

Quien quiera irse escribe a soporte (`@nexux_soporte_bot`), el bot atiende, recoge el motivo y
ofrece ayuda; si insiste, avisa a Ricardo. **Cancela Ricardo, en Stripe, con la mano.**

### Requisito nuevo que abre esta decision: la puerta giratoria

Ricardo: *"habria que controlar que esa cuenta no se hayan creado mas veces, porque se puede dar el
caso de que cancelen dias antes y vuelvan a abrir otra para tener otro mes gratis y asi
sucesibamente."*

El riesgo es real y es **consecuencia directa de la prueba gratis**: cancelar antes de que cobre y
volver a darse de alta sale gratis y se puede repetir. Hoy **no hay ningun control**: cada alta nace
como cuenta nueva sin mirar si ese negocio ya estuvo.

**No implementado todavia. Antes hay que decidir dos cosas, y las decide Ricardo:**

1. **Que cuenta como "el mismo negocio".** Candidatos, de mas a menos fiable:
   el **telefono de WhatsApp** (es el producto: sin el no hay servicio, y cambiarlo cuesta),
   el **email del dueno**, el **numero de Stripe del cliente**, el nombre + ciudad.
   El telefono es el mas dificil de falsear; el email, el mas facil (un `+1` y ya).
2. **Que se hace al detectarlo.** Tres niveles, de suave a duro:
   avisar a Ricardo y dejar entrar · **dejar entrar pero SIN prueba gratis** (cobra desde el dia 1)
   · no dejar abrir cuenta.

Recomendacion: **avisar + sin prueba gratis**, casando por telefono de WhatsApp. Bloquear del todo
castiga al que vuelve de buena fe, que es un cliente que ya te conoce.

**Marcado como pendiente de decision, no de trabajo.**
