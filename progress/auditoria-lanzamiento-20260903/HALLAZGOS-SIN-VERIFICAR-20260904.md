# ⚠️ HALLAZGOS SIN VERIFICAR — LEER ESTO ANTES DE CREERSE NADA DE LO DE ABAJO

Estos 44 "hallazgos" salieron de una auditoría en paralelo (run `wf_c2e58bdf-cd3`,
4-sep-2026) que **se cortó por límite de sesión**. Completó 4 de 5 mapeos y
**cero refutadores de 132**. El resultado de la herramienta decía
"0 confirmados, 44 descartados": **eso es falso**. No se descartaron; nunca
llegaron a juzgarse. El contador miente.

**Por tanto: nada de lo que hay debajo es un hecho hasta que alguien lo compruebe
en el fichero que EJECUTA.** Son sospechas con buena pinta, no evidencia.

---

## Lo que SÍ se ha verificado a mano desde entonces

| Hallazgo | Veredicto | Dónde quedó |
|---|---|---|
| Recordatorios leen campos que no existen | ✅ **CIERTO** | Arreglado, commit `0ba4015` |
| Renombrar el teléfono a secas manda la cita a un móvil ajeno | ✅ **CIERTO** | Evitado en el mismo arreglo |
| El recordatorio solo salía por WhatsApp | ✅ **CIERTO** | Arreglado |
| El resumen de las 21:00 iba al chat interno de Nexux | ✅ **CIERTO** | Arreglado |
| La lista de clientes estaba congelada en el arranque | ✅ **CIERTO** | Arreglado |
| Factura envuelta dos veces + cast mentiroso | ✅ **CIERTO** | Arreglado, `bbceb8e` |
| Un fallo de carga se veía como "no tienes facturas" | ✅ **CIERTO** | Arreglado |
| Informe mensual con `a.phone` / `a.servicio` / `a.precio` | ✅ **CIERTO** | Arreglado, `e799b6a` |
| Panel de administración: 3 columnas con "undefined" | ✅ **CIERTO** | Arreglado |
| "Próxima cita" del portal sale vacía | ✅ **CIERTO** | Arreglado, `54e56e5` |
| `index.json` marca 12 activos y las fichas dicen 3 | ✅ **CIERTO** | Rodeado: ahora se comprueban las dos cosas |
| Aviso de cancelación al dueño con "undefined" | ❓ **NO REPRODUCIDO** | No aparecen esos campos en `whatsapp.js` ni `telegram.js` |
| **Horario duplicado inglés/español** | ⚠️ **CIERTO PERO LATENTE** | Ver abajo |

### El horario duplicado, con precisión

Verificado el 4-sep: **hoy no está haciendo daño**, y conviene decirlo para que
nadie corra a "arreglarlo" rompiendo algo.

- El panel del cliente escribe las claves **en inglés** (`monday_open`…), y el
  motor lee inglés. **Editar el horario desde el panel sí funciona.**
- Hay 13 avisos en el registro de que inglés y español **discrepan en viernes**
  (20:00 contra 19:00). Manda el inglés, así que la copia española es peso muerto
  que puede desviarse sin que nadie se entere.
- El único cliente con horario **solo** en español es `demo`, que ni siquiera
  figura en `index.json`.

**La mina de verdad está en `lib/onboarding.js:130` (`buildConfig`)**: escribe
`horario` con días en español, `servicios` en español y `plan: 'starter'`, un plan
retirado. Ese flujo **está enchufado** (`whatsapp.js` lo consulta en cada mensaje
entrante y el webhook de la Pi puede arrancarlo), pero **ahora mismo no hay ningún
cliente con `onboarding.json` activo**, así que no está corriendo. Si algún día
arranca, dará de alta a un cliente con la forma vieja y su horario será ignorado.

Prioridad: media. No urge, pero no se puede dejar olvidado.

---

## Lo que sigue SIN mirar

Todo lo demás de este fichero. En particular: el plan Equipo que nace sin
agendas, el MRR del panel de administración que ignora los planes en venta, las
carpetas de cliente sin `config.json`, la falta de reintento si el servicio está
caído durante la ventana de 10 minutos del recordatorio, y las citas de Telegram
que meten `tg_<chatId>` en el campo del teléfono (esto último ya está rodeado en
los recordatorios, pero sigue contaminando el CRM y las fichas de cliente).

---


==============================================================================
?  —  12 hallazgos
==============================================================================

[CRITICA] scheduler-recordatorios-nombres-campo
  El cron de recordatorios lee cinco campos que nadie escribe: no se ha enviado ni un solo recordatorio
  donde     : ~/nexux-clients/lib/scheduler.js:75
  que falla : Las citas se guardan en snake_case ingles (client_name, client_phone, service) pero scheduler.js las lee en espanol: apt.nombre (l.78, l.95), apt.servicio (l.80) y apt.phone (l.83, l.98). Ningun escritor produce esos nombres, asi que los tres valen undefined en cada iteracion.
  el cliente: La promesa 3 del plan de 29 EUR ('Recuerda la cita al cliente 24 h y 1 h antes') no se cumple para NINGUN cliente. sendWhatsApp corta el envio porque el telefono es undefined, asi que no llega ni un mensaje mal formado: no llega nada, y en silencio.
  evidencia : lib/scheduler.js:78 `Hola ${apt.nombre}`, :80 `${apt.servicio}`, :83 `sendWhatsApp(clientId, apt.phone, msg)`. Contra lib/booking-engine.js:406-407 (client_name/client_phone) y lib/data.js:26-40. En disco, 69 citas reales en 7 clientes: ningun objeto tiene las claves nombre/servicio/phone (volcado de claves con node en /tmp). Prueba en vivo: `grep -c 'envio omitido: telefono no valido' ~/.pm2/logs/nexux-clients-error.log` = 284, todas '[wa:estudio-ricardo-demo-mostoles-946279] envio omitido: telefono no valido (undefined)'. lib/whatsapp.js:727-731 es quien las emite.
  alcance   : TODOS los clientes por codigo. El cron corre cada minuto para todo config.active (lib/scheduler.js:68-71) y el proceso nexux-clients esta online (pm2, script /home/nexux/nexux-clients/index.js).
  arreglo   : En lib/scheduler.js usar la forma canonica: apt.client_name, apt.service, apt.client_phone. Mejor aun: no leer el objeto crudo sino pasarlo por normalizeAppointment() de lib/config-normalizer.js:307, que ya traduce camelCase y snake_case y es la unica definicion escrita de la forma de una cita.

[CRITICA] scheduler-flag-recordatorio-huerfano
  El scheduler marca el recordatorio en reminded24h/reminded1h, campos que no existen en la forma canonica
  donde     : ~/nexux-clients/lib/scheduler.js:87
  que falla : El cron comprueba !apt.reminded24h (l.75) / !apt.reminded1h (l.92) y al enviar escribe updateAppointment(..., { reminded24h: true }) (l.87) y { reminded1h: true } (l.101). La forma canonica usa reminder_24h_sent y reminder_1h_sent. Son dos parejas de campos distintas para lo mismo.
  el cliente: Aunque se arreglen los nombres del hallazgo anterior, el anti-duplicado no funcionaria de forma coherente: el portal, al mover una cita, resetea reminder_24h_sent/reminder_1h_sent (provision-http.js:1520-1521) y el scheduler no mira esos campos, asi que ese reset no hace nada. Ademas cada cita creada por el motor nace con reminder_24h_sent:false y nunca nadie lo pone a true.
  evidencia : lib/scheduler.js:75,87,92,101 (unicos usos de 'reminded24h/reminded1h' en todo el repo, grep -rn excluyendo .bak). Frente a lib/booking-engine.js:416-417, lib/data.js:34-35, lib/config-normalizer.js:349-350, seed-agenda.mjs:136-137 y provision-http.js:1520-1521, que usan reminder_24h_sent/reminder_1h_sent. En disco: las 69 citas reales tienen reminder_24h_sent (o ninguna de las dos, en el cliente legacy) y ninguna tiene reminded24h; todas siguen en false.
  alcance   : TODOS los clientes por codigo.
  arreglo   : Renombrar en lib/scheduler.js las dos lecturas y las dos escrituras a reminder_24h_sent / reminder_1h_sent. Es el mismo cambio que ya asumen provision-http.js:1520 y booking-engine.js:416.

[CRITICA] resumen-diario-destinatario
  El resumen de las 21:00 de TODOS los salones se manda al Telegram de Nexux, no al del cliente
  donde     : ~/nexux-clients/lib/scheduler.js:146
  que falla : sendTelegram() de scheduler.js (l.14-29) publica siempre en process.env.TELEGRAM_CHAT_ID / TG_CHAT_ID (l.11-12), un unico chat global. El bucle de las 21:00 recorre todos los clientes y llama a ese sendTelegram (l.146), nunca a notifyOwnerTelegram(clientId, ...), que si resuelve cfg.channels.telegram.ownerChatId.
  el cliente: La promesa 4 del plan de 29 EUR ('Te manda un resumen cada tarde') no llega al que paga: llega al chat de Nexux, mezclado con el de todos los demas salones. El cliente no recibe nada y ademas su agenda del dia se expone en un chat ajeno.
  evidencia : lib/scheduler.js:11-12 (TG_TOKEN/TG_CHAT_ID de env), :14-29 (sendTelegram usa chat_id: TG_CHAT_ID), :113-147 (cron '0 21 * * *' recorre `clients` y termina en `await sendTelegram(lines.join('\n'))`). La alternativa correcta existe y se usa en otros sitios: lib/telegram.js:795-808 notifyOwnerTelegram lee cfg.channels.telegram.ownerChatId, y provision-http.js:1466 la usa. Confirmado que TELEGRAM_CHAT_ID esta definido en el .env (comprobado solo el nombre de la variable, no su valor).
  alcance   : TODOS los clientes por codigo.
  arreglo   : Sustituir la llamada de la linea 146 por notifyOwnerTelegram(clientId, texto) de lib/telegram.js, y dejar sendTelegram() solo para avisos internos de Nexux. Si el cliente no tiene ownerChatId, registrar el fallo en vez de mandarlo al chat global.

[ALTA] resumen-diario-nombres-campo
  El resumen diario imprime 'undefined (undefined)' en cada linea de cita
  donde     : ~/nexux-clients/lib/scheduler.js:133
  que falla : Las dos lineas que componen el resumen (hoy y manana) interpolan a.nombre y a.servicio, que no existen en la cita almacenada.
  el cliente: Aunque se corrija el destinatario, el resumen diario llega ilegible: '18:00 — undefined (undefined)'. El unico dato util seria la hora.
  evidencia : lib/scheduler.js:133 y :141: `lines.push(`  • ${formatTime(a.datetime, config.timezone)} — ${a.nombre} (${a.servicio})`)`. Las citas en disco llevan client_name y service (volcado de claves de los 7 appointments.json con contenido).
  alcance   : TODOS los clientes por codigo.
  arreglo   : a.client_name y a.service en las lineas 133 y 141, con un respaldo ('Cliente' / 'Cita') para las citas legacy sin nombre.

[ALTA] portal-proximas-citas-camelcase
  El panel del cliente muestra la columna 'Cliente' vacia en Proximas citas y en Proxima cita
  donde     : ~/nexux-pro/src/pages/cliente/[id].astro:376
  que falla : El HTML renderizado en servidor lee item.clientName || item.clientPhone (l.376) y nextApt.clientName || nextApt.clientPhone (l.402). La Pi devuelve las citas tal cual estan en disco, en snake_case: client_name / client_phone. No hay ninguna conversion a camelCase en el camino.
  el cliente: El que paga abre su panel y ve la tabla 'Proximas citas' con la columna Cliente en blanco, y la tarjeta 'Proxima cita' sin nombre. La cita esta, pero no sabe de quien es.
  evidencia : [id].astro:376 y :402 (camelCase). El endpoint que las sirve, provision-http.js:669-709, mete `nextAppointments: appointments` leyendo appointments.json en crudo (l.676-687) sin renombrar nada; portal-client.ts:155-163 fetchAllAppointments tampoco transforma. El tipo Appointment de src/lib/portal-client.ts:5-13 declara las cuatro variantes como opcionales, lo que deja pasar el error en TypeScript. Contraste dentro del mismo fichero: el JavaScript de cliente SI tiene respaldo — [id].astro:1992 `apt.client_name || apt.clientName` — asi que la vista de calendario funciona y el panel principal no.
  alcance   : TODOS los clientes por codigo.
  arreglo   : En [id].astro:376 y :402 usar el mismo helper que ya existe en el fichero (appointmentName/appointmentPhone, l.1992-1993) o directamente item.client_name || item.clientName || item.client_phone. Mejor: normalizar una sola vez en provision-http.js antes de responder, para que el portal no tenga que conocer dos formas.

[ALTA] roi-report-nombres-campo
  El informe mensual que se envia por email al dueno sale con datos falsos: servicio 'undefined', 1 clienta unica y retencion negativa
  donde     : ~/nexux-clients/lib/roi-report.js:37
  que falla : buildStats lee cuatro campos inexistentes: a.precio (l.37), a.phone (l.40, l.44, l.45) y a.servicio (l.51). Como a.phone es undefined en todas las citas, `new Set(...)` colapsa a tamano 1 y el calculo de nuevas/recurrentes se rompe.
  el cliente: El 1 de cada mes el dueno recibe en su correo: 'Servicio mas solicitado: undefined (N veces)', 'Clientas unicas atendidas: 1' sin importar cuantas fueran, y una retencion que puede salir negativa (returningClients = 1 - newClients). Ingresos siempre 'N/D', con una nota que le pide anadir precios a sus servicios — algo que no arreglaria nada, porque el precio nunca se copia a la cita.
  evidencia : lib/roi-report.js:37 `sum + (a.precio || 0)`, :40 `new Set(confirmed.map(a => a.phone))`, :44-46, :51 `serviceCounts[a.servicio]`. Esos valores se pintan en el email en :125 (ingresos), :129 (nuevas), :142 (unicas), :144 (top servicio) y :149 (la nota enganosa). El envio es al owner_email real: lib/roi-report.js:205-215. Ningun escritor produce precio/phone/servicio: booking-engine.js:396-418, data.js:26-40, seed-agenda.mjs:118-138. Confirmado tambien en las 69 citas en disco.
  alcance   : TODOS los clientes por codigo. Se dispara desde el cron '0 9 1 * *' de lib/scheduler.js:150-161 para todo config.active.
  arreglo   : a.client_phone en las lineas 40, 44 y 45; a.service en la 51. Para ingresos: o se copia el precio del servicio a la cita al crearla (nuevo campo `price` en buildAppointment) o se cruza a.service_id contra config.services en el propio informe; hasta entonces, quitar la nota de la linea 149 porque promete algo que no ocurre.

[ALTA] scheduler-lista-clientes-congelada
  El scheduler solo conoce a los clientes que existian al arrancar el proceso: un cliente nuevo no tiene recordatorios ni resumen
  donde     : ~/nexux-clients/index.js:60
  que falla : index.js carga clients desde disco una vez (l.13-36) y se lo pasa a startScheduler(clients) (l.60). Los crons de recordatorios (l.68) y de resumen (l.114) iteran ese array congelado. El alta de un cliente nuevo (provision-http.js:499 registerClient + l.146/792 startBot) arranca su bot pero nunca lo mete en ese array.
  el cliente: Un salon que compra hoy tiene el bot funcionando pero cero recordatorios y cero resumen diario hasta que alguien reinicie el proceso a mano. Se le esta cobrando por dos de las seis cosas prometidas que su cuenta ni siquiera tiene programadas.
  evidencia : index.js:13-36 (loadClients, snapshot), :60 startScheduler(clients); lib/scheduler.js:69 `for (const { clientId, config } of clients)` en el cron de cada minuto y :115 en el de las 21:00. provision-http.js:499 registerClient y :146/:792 startBot: no hay ninguna llamada que anada al array del scheduler (grep de clients.push en index.js y provision-http.js). El propio codigo demuestra que el autor lo sabia: el cron del blog SI relee disco con getAllActiveClientIds() (lib/scheduler.js:166) y el comentario de lib/data.js:253-254 dice literalmente 'Used by scheduler for crons that run after new cli
  alcance   : TODOS los clientes dados de alta despues del ultimo arranque del proceso. pm2 muestra nexux-clients con 4h de uptime y 8 reinicios, asi que la ventana se reabre en cada reinicio.
  arreglo   : Que los crons de recordatorios y resumen resuelvan la lista por cliente en cada ejecucion con getAllActiveClientIds() + getClientConfig() (lib/data.js:250-262), igual que ya hace el cron del blog, en vez de cerrarse sobre el array de arranque.

[MEDIA] aviso-cancelacion-nombres-campo
  El aviso de cancelacion al dueno sale 'undefined (undefined)' en WhatsApp y en Telegram
  donde     : ~/nexux-clients/lib/whatsapp.js:518
  que falla : Tras cancelar, ambos bots componen el aviso al dueno con cancelled.nombre, cancelled.phone y cancelled.servicio. cancelAppointment de lib/data.js:52 devuelve el objeto crudo, en snake_case.
  el cliente: Cuando una clienta cancela por chat, al dueno le llega '❌ CITA CANCELADA — Salon / 👤 undefined (undefined) / 💇 undefined' y solo la fecha es legible. No sabe a quien llamar para rellenar el hueco.
  evidencia : lib/whatsapp.js:518-519 `${cancelled.nombre} (${cancelled.phone})` y `${cancelled.servicio}`; lib/telegram.js:295-296 lo mismo. cancelAppointment -> updateAppointment (lib/data.js:44-56) devuelve apts[idx] sin normalizar, con client_name/client_phone/service.
  alcance   : TODOS los clientes por codigo, en los dos canales de chat.
  arreglo   : cancelled.client_name, cancelled.client_phone y cancelled.service en whatsapp.js:518-519 y telegram.js:295-296.

[BAJA] panel-admin-nombres-campo
  La tabla de citas del panel de administracion muestra tres columnas con 'undefined'
  donde     : ~/nexux-clients/lib/admin.js:145
  que falla : La ficha de cliente del panel interno pinta ${a.nombre}, ${a.phone} y ${a.servicio} directamente en el HTML.
  el cliente: No lo ve quien paga: el panel es interno (startAdmin en index.js:66). El dano es de soporte — al mirar la agenda de un cliente para diagnosticar algo, no se ve ni el nombre ni el servicio, lo que hace que un fallo real parezca normal.
  evidencia : lib/admin.js:145-147 dentro del map sobre getAppointments(clientId) (l.139). getAppointments (lib/data.js:22) devuelve el JSON crudo, en snake_case.
  alcance   : TODOS los clientes por codigo, pero solo en la interfaz interna de Nexux.
  arreglo   : a.client_name, a.client_phone y a.service en admin.js:145-147.

[MEDIA] client-phone-sobrecargado-telegram
  Las citas reservadas por Telegram guardan 'tg_<chatId>' dentro de client_phone
  donde     : ~/nexux-clients/lib/telegram.js:243
  que falla : El bot de Telegram no tiene el telefono del cliente y mete su identificador interno (userRef = `tg_${chatId}`, l.171) en el campo client_phone. El campo pasa a significar dos cosas distintas segun el canal.
  el cliente: Arreglar los nombres de campo del scheduler NO bastaria para estas citas: sendWhatsApp limpia los no-digitos y quedaria un numero inventado, asi que el recordatorio seguiria sin salir (o peor, saldria a un numero equivocado). Ademas la ficha de cliente del CRM crea un cliente fantasma con telefono '7646339' a partir de 'tg_7646339'.
  evidencia : lib/telegram.js:171 `const userRef = \`tg_${chatId}\`` y :243 `client_phone: userRef`. La lectura simetrica esta en :148 `a.client_phone === requesterPhone`, asi que dentro de Telegram es coherente. Fuera no: lib/whatsapp.js:727 `String(phone).replace(/\D/g,'')` y lib/clientes.js:39-45 normalizarTelefono, que convierte 'tg_7646339' en '7646339' y lo da por telefono valido (l.79 y l.158).
  alcance   : TODOS los clientes que tengan Telegram activo. En disco no hay hoy ninguna cita con este patron (las 69 revisadas vienen de WhatsApp, CRM o siembra), asi que es un fallo latente, no observado.
  arreglo   : Separar identidad de canal: guardar el identificador en un campo propio (p.ej. `contact_ref` + `channel`) y dejar client_phone solo para telefonos E.164. Mientras tanto, que el scheduler y clientes.js descarten cualquier client_phone que no sea solo digitos.

[BAJA] data-js-create-appointment-forma-v1
  lib/data.js createAppointment sigue escribiendo la forma vieja y puede bloquear la agenda de un cliente en modo equipo
  donde     : ~/nexux-clients/lib/data.js:26
  que falla : createAppointment escribe una cita sin service_id, professional_id, resource_allocations, source, source_event_id ni version. El motor considera 'legacy' toda cita sin professional_id (booking-engine.js:166) y, en modo equipo, si no puede resolver su service_id aborta con legacy_migration_required (booking-engine.js:176-180) — y ese fallo tumba CUALQUIER reserva posterior de ese cliente, no solo la cita mala.
  el cliente: Hoy no ocurre: ningun camino de produccion la llama. Pero sigue exportada e importada en lib/whatsapp.js:43 y lib/telegram.js:31 sin usarse, asi que una linea nueva que la use dejaria al salon sin poder reservar nada, con un error opaco.
  evidencia : lib/data.js:26-40 (campos escritos). grep -rn 'createAppointment\b' excluyendo tests y .bak: solo las definiciones, los dos imports muertos (whatsapp.js:43, telegram.js:31) y comentarios; los cuatro caminos reales (whatsapp.js:428, telegram.js:242, provision-http.js:1392 CRM y :1793 reserva publica) pasan por bookAppointment de lib/booking-bridge.js. La comprobacion que fallaria esta en booking-engine.js:170-186 (validateStoredRecords), invocada en readRecords (l.436-440) antes de cada reserva.
  alcance   : TODOS los clientes por codigo, pero latente: sin llamadores hoy.
  arreglo   : Borrar los dos imports muertos y hacer que lib/data.js createAppointment delegue en booking-bridge, o marcarla como @deprecated y sacarla de las exportaciones. Un solo escritor de citas es lo que hace que 'la forma canonica' signifique algo.

[BAJA] citas-legacy-camelcase-en-disco
  Un cliente tiene sus citas en disco en camelCase (clientName/clientPhone) y ningun lector directo las entiende
  donde     : ~/nexux-clients/clients/peluqueria-carmen-e2e-madrid-fdef01/appointments.json:1
  que falla : Ese fichero guarda 4 citas con las claves clientPhone y clientName, y sin duration_min ni los flags de recordatorio. Es una tercera forma, distinta de la canonica y de la vieja de data.js.
  el cliente: Para ese cliente concreto: nombre y telefono en blanco en cualquier vista que lea el JSON en crudo (portal, panel admin, informe ROI, fichas de cliente) y, al no haber duration_min, el motor lo trata como cita legacy. Solo lo salva quien pase por normalizeAppointment.
  evidencia : Volcado de claves con node en /tmp sobre clients/*/appointments.json: 'peluqueria-carmen-e2e-madrid-fdef01 | n=4 | keys=id,clientPhone,clientName,service,datetime,status'. Los otros 6 ficheros con contenido usan client_name/client_phone. lib/config-normalizer.js:338-339 si acepta ambas grafias; lib/data.js:22 getAppointments no.
  alcance   : Solo los datos de esa cuenta (parece de una prueba E2E), no el codigo. Se incluye porque prueba que el sistema ha escrito tres formas distintas y que ningun lector directo esta blindado.
  arreglo   : Migrar ese fichero a la forma canonica (o borrarlo si es de prueba) y, en general, que todo lector pase por normalizeAppointment en vez de leer el JSON en crudo, para que una cita antigua nunca deje una pantalla en blanco.

  NOTAS / no verificado:
  FORMA CANONICA DE UNA CITA (la que EJECUTA, no la documentada). La define lib/booking-engine.js:396-418 (buildAppointment), es el unico escritor con llamadores en produccion, y coincide con lo que hay en disco: id, service_id, service, professional_id, professional_name, assignment_mode, resource_allocations[], client_name, client_phone, datetime (ISO con Z), duration_min, status, source, source_event_id, version, created_at, updated_at, reminder_24h_sent, reminder_1h_sent. Se le anade despues google_event_id via updateAppointment (whatsapp.js:469, telegram.js:268, provision-http.js:1445 y :1568). Verificado contra las 69 citas de los 7 appointments.json con contenido.

ESCRITORES (los cuatro caminos reales van todos al mismo sitio): lib/booking-bridge.js:119-145 bookAppointment -> booking-engine.createAppointment, llamado desde lib/whatsapp.js:428 (bot WhatsApp, source 'whatsapp'), lib/telegram.js:242 (bot Telegram, source 'telegram'), provision-http.js:1392 (CRM del portal, source 'crm') y provision-http.js:1793 (reserva publica /public/:clientId/book, source 'web'). Escritores secundarios: lib/data.js:44 updateAppointment (mezcla ciega, no puede borrar campos), provision-http.js

==============================================================================
?  —  10 hallazgos
==============================================================================

[CRITICA] recordatorios-leen-campos-que-no-existen
  Los dos recordatorios leen campos que ninguna cita tiene: nunca se envia ni uno
  donde     : ~/nexux-clients/lib/scheduler.js:75
  que falla : El cron de cada minuto lee apt.reminded24h / apt.reminded1h / apt.nombre / apt.servicio / apt.phone (lineas 75, 78, 80, 83, 92, 95, 98). Las citas se guardan con reminder_24h_sent, reminder_1h_sent, client_name, service, client_phone. Los cinco campos que usa el recordatorio valen undefined en TODAS las citas reales, asi que el telefono siempre llega vacio y sendWhatsApp aborta.
  el cliente: La promesa 3 de la pagina de ventas ('Recuerda la cita al cliente 24 h y 1 h antes') no se ha cumplido NUNCA para ningun cliente. Quien paga 29 EUR cree que sus clientas reciben aviso; no lo recibe ninguna. Y como no hay ni un indicador en el portal, el salon no tiene forma de enterarse: solo ve que la gente falta a la cita.
  evidencia : lib/scheduler.js:75 'if (isInWindow(apt.datetime, 24) && !apt.reminded24h)' y :83 'sendWhatsApp(clientId, apt.phone, msg)'. Frente a lib/data.js:26-39 (createAppointment escribe client_phone/client_name/service/reminder_24h_sent) y lib/booking-engine.js:398-418 (idem). Volcado de las 55 citas reales de estudio-ricardo-demo-mostoles-946279: todas dan 'apt.phone= undefined' y 'reminded24h= undefined', incluidas 3 con telefono REAL en client_phone (34600333777, 34600444888, 34600777555) y las tres con reminder_24h_sent=false pese a que su fecha ya paso. Log vivo ~/.pm2/logs/nexux-clients-error.lo
  alcance   : Afecta a TODOS los clientes por codigo. No depende de datos: los nombres de campo estan mal en el unico emisor de recordatorios que existe.
  arreglo   : En scheduler.js sustituir apt.reminded24h -> apt.reminder_24h_sent, apt.reminded1h -> apt.reminder_1h_sent, apt.nombre -> apt.client_name, apt.servicio -> apt.service, apt.phone -> apt.client_phone, y en updateAppointment escribir { reminder_24h_sent: true } / { reminder_1h_sent: true }. OJO: hacer solo este renombrado activa el hallazgo 'fix-ingenuo-manda-a-numero-equivocado'; hay que aplicar los dos a la vez.

[CRITICA] fix-ingenuo-manda-a-numero-equivocado
  Renombrar apt.phone a client_phone a secas manda la cita de un desconocido a un movil al azar
  donde     : ~/nexux-clients/lib/telegram.js:243
  que falla : Las reservas hechas por Telegram guardan client_phone = `tg_<chatId>` (telegram.js:171 'const userRef = `tg_${chatId}`' y :243 'client_phone: userRef'). sendWhatsApp limpia el valor con .replace(/\D/g,'') y solo exige 8 digitos, asi que 'tg_511455969' se convierte en el numero 511455969 y pasa el filtro.
  el cliente: Si se arregla el hallazgo anterior sin tocar esto, en cuanto un cliente use Telegram el sistema empezara a mandar por WhatsApp el nombre, el servicio y la hora de la cita de una clienta a un numero de telefono con el que no tiene nada que ver. Es una fuga de datos personales del cliente del cliente, con el nombre del salon en el mensaje.
  evidencia : lib/telegram.js:171 y :243. lib/booking-engine.js:407 guarda client_phone tal cual ('request.client_phone ?? ... ?? ""'), sin validar. lib/whatsapp.js:727-731: const tel = String(...).replace(/\D/g,'').replace(/^0+/,''); if (!tel || tel.length < 8) return false. Comprobado ejecutando esa misma expresion: entrada 'tg_511455969' -> tel=511455969, len=9, pasa filtro=true, jid=511455969@s.whatsapp.net.
  alcance   : Afecta a TODOS los clientes por codigo, y se dispara en cuanto alguien reserve por Telegram, que es el canal que el propio onboarding marca como recomendado.
  arreglo   : Antes de enviar, exigir que client_phone sea un telefono de verdad: descartar cualquier valor que no case con /^\+?[0-9 ()-]{9,}$/ o que empiece por 'tg_'. Mejor aun: separar el identificador del canal del telefono (campos client_channel + client_ref) y que sendWhatsApp rechace todo lo que no sea E.164. Y en whatsapp.js endurecer el filtro: 8 digitos es demasiado laxo para un movil espanol.

[CRITICA] recordatorio-solo-sale-por-whatsapp
  El recordatorio solo sale por WhatsApp; quien usa Telegram (el canal recomendado) no recibe nada y ni siquiera queda log
  donde     : ~/nexux-clients/lib/scheduler.js:83
  que falla : Los dos recordatorios llaman unicamente a sendWhatsApp (lineas 83 y 98). No hay ninguna rama para Telegram, pese a que lib/telegram.js ya exporta notifyOwnerTelegram (linea 795) y broadcastToCustomers (linea 813). Ademas, cuando el cliente no tiene sesion de WhatsApp viva, whatsapp.js:724 hace 'if (!sock) return false' ANTES de escribir ninguna traza: fallo totalmente mudo.
  el cliente: Un salon que sigue la recomendacion del propio producto y monta el servicio sobre Telegram paga 29 EUR por una funcion que no existe para el. Sus clientas reservan por Telegram y jamas reciben aviso. Y como no se escribe ni una linea de log, nadie en Nexux puede detectarlo ni dando soporte.
  evidencia : lib/scheduler.js:83 y :98 (unico canal: sendWhatsApp). lib/whatsapp.js:722-724 (return false sin log si no hay socket). nexux-pro/src/pages/cliente/[id]/onboarding.astro:150: '<strong>Telegram — empezamos <em class="ob-reco">recomendado</em></strong>'. lib/telegram.js:795 y :813 exportan las funciones de envio por Telegram y scheduler.js no importa ninguna (su unico import de mensajeria es sendWhatsApp, linea 6). Todos los config.json de clientes llevan channels.telegram.enabled=true.
  alcance   : Afecta a TODOS los clientes por codigo; el dano es total en los que usan Telegram como canal principal.
  arreglo   : Enviar el recordatorio por el canal donde se creo la cita: guardar el canal en la cita (ya existe apt.source, que vale 'telegram' en las reservas de Telegram — telegram.js:249) y despachar segun ese campo: source 'telegram' -> bot.api.sendMessage al chatId guardado; source whatsapp -> sendWhatsApp. Y en whatsapp.js:724 anadir un console.warn cuando no hay socket, para que el fallo deje rastro.

[CRITICA] resumen-diario-va-a-un-unico-chat-global
  El resumen de las 21:00 de TODOS los clientes se manda a un solo chat de Telegram, el de Nexux, no al del salon
  donde     : ~/nexux-clients/lib/scheduler.js:11
  que falla : sendTelegram usa dos constantes de modulo leidas del .env al arrancar: TG_TOKEN y TG_CHAT_ID (lineas 11-12), y envia siempre a ese chat_id fijo (linea 21). El bucle del resumen recorre todos los clientes y llama a sendTelegram(...) sin pasarle nunca el chat del salon (linea 145). Ignora por completo config.channels.telegram.ownerChatId, que es donde vive el chat del dueno.
  el cliente: La promesa 4 ('Te manda un resumen cada tarde') no se cumple para nadie: el resumen del salon acaba en el movil de Nexux, no en el del dueno. Si manana hay 20 clientes, el dueno de Nexux recibe 20 resumenes ajenos cada noche (dato de otros negocios en su chat) y ninguno de los 20 salones recibe el suyo.
  evidencia : lib/scheduler.js:11-12 'const TG_TOKEN = process.env.TELEGRAM_BOT_TOKEN; const TG_CHAT_ID = process.env.TELEGRAM_CHAT_ID || process.env.TG_CHAT_ID;', :21 'chat_id: TG_CHAT_ID', :145 'await sendTelegram(lines.join("\n"))' dentro del for de clientes. Comprobado sin imprimir el secreto: grep -q '^TELEGRAM_CHAT_ID=511455969' ~/nexux-clients/.env devuelve verdadero, es decir, el chat global coincide con el ownerChatId 511455969 que aparece en los config.json de los clientes de prueba de Ricardo. Los config.json de clientes SI tienen su propio campo channels.telegram.ownerChatId (p.ej. new-look-7320
  alcance   : Afecta a TODOS los clientes por codigo. No es un problema de la cuenta de prueba: el destino esta fijado en una variable de entorno global.
  arreglo   : Sustituir la sendTelegram local por notifyOwnerTelegram(clientId, texto) de lib/telegram.js, que ya resuelve el ownerChatId del cliente. Y si el cliente no tiene ownerChatId vinculado, NO callar: registrar aviso y marcarlo en el panel como 'resumen no entregable, vincula tu Telegram', porque hoy ese caso es silencio absoluto.

[CRITICA] lista-de-clientes-congelada-en-el-arranque
  El scheduler trabaja con una foto de los clientes hecha al arrancar: un cliente nuevo no recibe nada hasta que alguien reinicie el servicio a mano
  donde     : ~/nexux-clients/index.js:40
  que falla : index.js:40 construye el array clients leyendo el directorio una sola vez y lo pasa a startScheduler (index.js:60). scheduler.js cierra sobre ese array (lineas 69, 110, 151) y nunca lo relee. No existe ningun clients.push posterior: el unico clients.push de provision-http.js (linea 1630) es un array local del endpoint /admin/stats, sin relacion con el scheduler. Tampoco hay reinicio de pm2 ni recarga al provisionar.
  el cliente: Un salon que paga hoy queda fuera de los recordatorios y del resumen hasta que alguien reinicie el proceso a mano. Sin aviso y sin error. Y al reves: un cliente que cancela en Stripe sigue dentro de la lista con active=true en memoria (stripe-webhook.js:397-400 escribe active=false SOLO en el fichero, no en el objeto que tiene el scheduler), asi que se le seguiria dando servicio gratis. La foto tambien congela el plan, el nombre y la zona horaria.
  evidencia : index.js:24-35 (loadClients lee el directorio una vez), :40 'const clients = loadClients()', :60 'startScheduler(clients)'. lib/scheduler.js:69 'for (const { clientId, config } of clients)' y :110 idem — siempre el mismo array. grep -rn 'startScheduler|reloadClients|refreshClients' en todo el repo solo devuelve index.js y lib/scheduler.js. grep de 'scheduler|pm2 restart|pm2 reload' en provision-http.js: ninguna coincidencia. lib/stripe-webhook.js:123-138 crea el cliente nuevo con active:false y fs.writeFileSync, sin tocar memoria. Contraste dentro del mismo fichero: el cron de blog (scheduler.
  alcance   : Afecta a TODOS los clientes por codigo, y muy en particular a cada cliente nuevo que se venda: es exactamente el caso que el dueno del producto exige que funcione.
  arreglo   : Que startScheduler no reciba la lista: que la relea en cada tick con la misma funcion loadClients() (lectura de directorio + config.json, coste despreciable con decenas de clientes), igual que ya hace el cron de blog en la linea 164. Asi entra solo el cliente nuevo y sale solo el que cancela, sin reiniciar nada.

[ALTA] resumen-diario-dice-undefined
  Aunque llegara al salon, el resumen diario lista 'undefined (undefined)' en cada cita
  donde     : ~/nexux-clients/lib/scheduler.js:133
  que falla : Las lineas que construyen el detalle del resumen usan a.nombre y a.servicio (lineas 133 y 141), campos que no existen en las citas. Solo la hora y los recuentos salen bien.
  el cliente: El resumen de la tarde es inutil: dice cuantas citas hay pero no de quien ni de que. El dueno no puede prepararse el dia siguiente, que es justo para lo que se vende la funcion.
  evidencia : lib/scheduler.js:133 'lines.push(`  • ${formatTime(a.datetime, config.timezone)} — ${a.nombre} (${a.servicio})`)' y :141 identico. Reproducido en vivo (script de solo lectura ejecutado en /tmp, fuera del repo) con las citas reales de estudio-ricardo-demo-mostoles-946279 del 29-ago: salida 'Citas hoy: 13' seguida de 13 lineas '09:00 — undefined (undefined)', '09:30 — undefined (undefined)', etc.
  alcance   : Afecta a TODOS los clientes por codigo.
  arreglo   : a.nombre -> a.client_name y a.servicio -> a.service en las lineas 133 y 141, con respaldo por si estan vacios (a.client_name || 'Sin nombre').

[ALTA] bucle-de-reintentos-y-marca-que-nadie-lee
  El aviso se reintenta unas 11 veces en 10 minutos y luego se pierde para siempre; y la marca que escribiria no la lee nadie
  donde     : ~/nexux-clients/lib/scheduler.js:84
  que falla : La marca de 'ya avisado' solo se escribe si sendWhatsApp devuelve true (lineas 84-88 y 99-102). Como siempre devuelve false, la marca no se escribe y el minuto siguiente vuelve a intentarlo. La ventana de isInWindow es de +/-5 minutos (linea 56), es decir 10 minutos, asi que se reintenta en cada tick del cron dentro de esa franja (unos 10-11 intentos por cita y por aviso) y despues NO se vuelve a intentar jamas: la cita queda sin recordatorio de forma definitiva y silenciosa. Ademas, la marca que escribiria es reminded24h/reminded1h, campos que no lee ningun otro fichero: provision-http.js:1520-1521 resetea reminder_24h_sent al reprogramar una cita, resetea algo que el scheduler no mira.
  el cliente: No es un bucle infinito que tumba el servicio, es peor de cara al cliente: fracasa 11 veces en silencio y se rinde. Nadie recibe alerta. Y cuando se arregle el envio, si no se unifica el nombre del campo, reprogramar una cita no volvera a disparar el aviso (el flag que se resetea no es el que se consulta), o al reves se avisara dos veces.
  evidencia : lib/scheduler.js:51-57 (isInWindow con toleranceMinutes=5, ventana total 10 min), :84-88 'if (sent) { ... updateAppointment(clientId, apt.id, { reminded24h: true }) }'. Rafagas reales en ~/.pm2/logs/nexux-clients-error.log: bloques contiguos de 9 a 14 lineas 'envio omitido: telefono no valido (undefined)', 284 en total, todas con valor 'undefined'. provision-http.js:1520-1521 'changes.reminder_24h_sent = false; changes.reminder_1h_sent = false;'.
  alcance   : Afecta a TODOS los clientes por codigo.
  arreglo   : Unificar en reminder_24h_sent / reminder_1h_sent (los que usa el resto del sistema). Y cuando el envio falle, no limitarse a no marcar: registrar el fallo en la cita (reminder_24h_error con el motivo) y avisar al dueno, para que un recordatorio perdido sea visible en vez de mudo.

[MEDIA] cita-sin-telefono-se-acepta-en-silencio
  El sistema acepta citas sin telefono y nadie se entera de que esa cita nunca podra tener recordatorio
  donde     : ~/nexux-clients/provision-http.js:1413
  que falla : El endpoint de creacion de citas guarda client_phone: client_phone || '' (linea 1413) y el motor hace lo mismo (booking-engine.js:407, por defecto ''). No hay ninguna validacion de que exista telefono, ni ningun aviso posterior. El portal del cliente no muestra en ningun sitio si el recordatorio se envio o no.
  el cliente: Una cita creada desde el panel sin telefono jamas tendra aviso, y el salon no lo sabe. Se ve en los datos reales: en kalon-test-ricardo y new-look-7320e8 hay citas confirmadas con client_phone:"", y en las 12 citas de rodaje de estudio-ricardo el campo ni siquiera existe.
  evidencia : provision-http.js:1413 'client_phone: client_phone || "", client_name: client_name || "",'. lib/booking-engine.js:407 'client_phone: request.client_phone ?? request.clientPhone ?? previous?.client_phone ?? ""'. Volcado real: kalon-test-ricardo/appointments.json cita 7100209c con "client_phone": "", new-look-7320e8 cita c02b868e con "client_phone": "". grep de 'reminder_24h_sent|reminder_1h_sent|recordatorio' en nexux-pro/src: cero coincidencias en el portal (solo un texto de marketing en src/data/plans.ts:57), es decir, el portal no ensena el estado del recordatorio en ninguna pantalla.
  alcance   : Afecta a TODOS los clientes por codigo.
  arreglo   : Marcar la cita sin telefono valido y mostrarlo en el portal ('sin telefono: esta cita no tendra recordatorio'), y anadir en la ficha de cita una columna con el estado real del aviso (pendiente / enviado / fallido con motivo). Sin eso, el cliente no puede verificar lo que le vendieron.

[MEDIA] sin-recuperacion-si-el-servicio-esta-caido
  Si el servicio esta caido o reiniciando durante esos 10 minutos, el recordatorio se pierde sin recuperacion
  donde     : ~/nexux-clients/lib/scheduler.js:51
  que falla : isInWindow solo acepta la franja +/-5 minutos alrededor de las 24 h (o 1 h) previas. No hay ninguna recuperacion de los avisos que quedaron atras: pasada la franja, la cita ya no vuelve a evaluarse nunca. Si el proceso esta parado o reiniciando justo en esos 10 minutos, ese aviso se pierde.
  el cliente: Cualquier reinicio, despliegue o caida que pille la franja deja clientas sin aviso, sin ningun rastro ni reintento. El proceso lleva 8 reinicios acumulados, asi que no es un escenario teorico.
  evidencia : lib/scheduler.js:51-57 (funcion isInWindow, unica condicion de disparo) y :75/:92 (no hay ninguna rama para citas cuya franja ya paso). pm2 jlist: nexux-clients status=online, restart_time=8, pm_uptime=2026-09-04T10:50:41.511Z.
  alcance   : Afecta a TODOS los clientes por codigo.
  arreglo   : Cambiar la condicion de 'esta dentro de la franja' a 'ya toca y aun no se ha enviado': disparar cuando falten 24 h o menos (y mas de, por ejemplo, 23 h) y el flag este a false, apoyandose en el flag persistido en vez de en el reloj. Asi un reinicio recupera el aviso en el siguiente minuto en vez de perderlo.

[BAJA] cron-sin-red-de-seguridad
  Los crons no tienen try/catch y el proceso no captura promesas rechazadas: un fallo en el recordatorio tumba el servicio entero
  donde     : ~/nexux-clients/lib/scheduler.js:68
  que falla : Los callbacks async de cron.schedule de recordatorios (linea 68) y de resumen (linea 109) no tienen try/catch alrededor del cuerpo — solo el de ROI lo tiene (linea 153). Si algo lanza dentro (lectura de fichero, fecha o zona horaria invalida en un config.json, escritura fallida), la promesa queda rechazada sin capturar. No hay ningun process.on('unhandledRejection') en todo el repo y Node es v22, donde el rechazo sin capturar termina el proceso.
  el cliente: Un unico dato malo en la configuracion de UN cliente puede tirar el servicio de TODOS: se caen a la vez los bots de WhatsApp, la agenda y el endpoint de provisionamiento, hasta que pm2 lo levante y las sesiones vuelvan a reconectar.
  evidencia : lib/scheduler.js:68-106 y :109-147 (cuerpos async sin try/catch), frente a :150-159 (el de ROI si lo lleva). grep -rn 'unhandledRejection|uncaughtException' en todo el repo (excluyendo node_modules y .bak): cero coincidencias. node -v en la Pi: v22.22.2.
  alcance   : Afecta a TODOS los clientes por codigo. NO he confirmado un disparador concreto alcanzable hoy: la unica via que he identificado (config.timezone invalido llegando a toLocaleString) no aparece escrita desde entrada de usuario en provision-http.js, asi que lo doy como riesgo estructural verificado, no como fallo reproducido.
  arreglo   : Envolver el cuerpo de cada cron en try/catch por cliente (que un cliente que falla no impida procesar a los demas) y anadir en index.js un process.on('unhandledRejection') que registre y siga, en vez de morir.

  NOTAS / no verificado:
  Lo que NO he podido verificar y por que:

1. No he ejecutado ningun envio real ni la suite de tests, por la prohibicion del encargo. Todo lo relativo a 'que pasaria si se arregla el nombre del campo' esta razonado sobre el codigo y comprobado con la misma expresion regular de whatsapp.js ejecutada aparte en /tmp, no enviando mensajes.

2. No he confirmado quien es el dueno del chat de Telegram 511455969. Lo unico verificado es que TELEGRAM_CHAT_ID del .env coincide exactamente con ese valor y que ese mismo valor aparece como ownerChatId en varios config.json de clientes de prueba de Ricardo. La conclusion firme es la del codigo: el destino del resumen es un chat unico global, no el del salon.

3. No he visto una hora exacta en los logs: ~/.pm2/logs/nexux-clients-*.log no llevan sello de tiempo por linea. La recencia la deduzco de la posicion (la ultima traza de 'telefono no valido' esta en la linea 981 de 1057) y de la mtime del fichero (4-sep 13:04). Las lineas 'Too many reconnect attempts' que aparecen intercaladas NO estan en el whatsapp.js actual, asi que provienen de una version anterior: el fichero de log es acumulativo entre reinicios y no las uso como evidencia de nada.

4.

==============================================================================
?  —  9 hallazgos
==============================================================================

[CRITICA] doble-envoltura-facturas
  La respuesta de facturas llega envuelta dos veces y el historial nunca se pinta
  donde     : /home/nexux/nexux-pro/src/pages/portal-api/invoices.ts:14
  que falla : La Pi devuelve un OBJETO {invoices:[...]} (provision-http.js:1727 `res.json({ invoices })`), portal-client.ts:131 lo devuelve tal cual, e invoices.ts:14 lo vuelve a envolver con `JSON.stringify({ ok: true, invoices })`. El navegador recibe {ok:true, invoices:{invoices:[...]}}, es decir `d.invoices` es un objeto, no un array.
  el cliente: El apartado Facturacion nunca muestra ninguna factura. El cliente que paga ve siempre 'Sin facturas todavia' aunque Stripe tenga sus facturas emitidas, y por tanto no puede descargar ningun justificante de pago desde el panel.
  evidencia : Verificado EN PRODUCCION, no solo leido: `curl -H 'Cookie: nexux_token=<token>' https://nexux.pro/portal-api/invoices?clientId=nexux-demo-mostoles-42a928` -> HTTP 200 `{"ok":true,"invoices":{"invoices":[]}}`. Y contra la Pi: `curl http://127.0.0.1:3460/client/nexux-demo-mostoles-42a928/invoices` -> `{"invoices":[]}` (objeto, no array). Codigo: provision-http.js:1727, portal-client.ts:131, invoices.ts:14. El repo esta limpio y sin commits sin subir (git status / git log origin/main..main vacio), y el chunk desplegado .vercel/output/_functions/chunks/invoices_DinXAdqH.mjs contiene la misma envol
  alcance   : TODOS los clientes por codigo. No depende de datos de ninguna cuenta: la envoltura la pone el codigo del servidor en cada respuesta.
  arreglo   : Normalizar en UN solo sitio, en portal-client.ts:125-133: `const data = await response.json(); return Array.isArray(data) ? data : (data?.invoices ?? []);` y dejar invoices.ts como esta. Ademas, blindar el navegador en [id].astro:2657 con `var list = Array.isArray(d.invoices) ? d.invoices : (d.invoices && d.invoices.invoices) || [];` para que un cambio futuro de forma no vuelva a romperlo en silencio.

[ALTA] cast-mentiroso-as-invoice-array
  Un cast de TypeScript miente sobre la forma y por eso el compilador no avisa
  donde     : /home/nexux/nexux-pro/src/lib/portal-client.ts:131
  que falla : `return (await response.json()) as Invoice[];` afirma que la respuesta es un array de Invoice cuando lo que llega es `{invoices: Invoice[]}`. El `as` desactiva la comprobacion: TypeScript acepta el codigo y la firma `Promise<Invoice[]>` propaga la mentira a invoices.ts, que confia en ella y la envuelve otra vez.
  el cliente: Es la causa de que el fallo anterior pasara los controles y llegara a produccion: nada en compilacion ni en despliegue avisa. Cualquier defecto de forma en este camino seguira siendo invisible hasta que un cliente se queje.
  evidencia : portal-client.ts:125 `export async function getClientInvoices(...): Promise<Invoice[]>` y :131 `return (await response.json()) as Invoice[]`. Contrastado con la respuesta real de la Pi verificada por curl: `{"invoices":[]}`. El mismo patron de cast existe en fetchAllAppointments (portal-client.ts:158 `as any[]`), aunque ahi la Pi si devuelve array y por eso no rompe.
  alcance   : TODOS los clientes por codigo.
  arreglo   : Sustituir el cast por un tipo honesto y una lectura defensiva: `const data = (await response.json()) as Invoice[] | { invoices?: Invoice[] };` y devolver `Array.isArray(data) ? data : (data.invoices ?? [])`. Regla general: en este fichero, ningun `as` sobre un `response.json()` sin haber comprobado la forma real del endpoint.

[ALTA] crash-forEach-enmascarado-por-catch
  El navegador NO entra en la rama de vacio: revienta, y el catch disfraza el error de 'no hay facturas'
  donde     : /home/nexux/nexux-pro/src/pages/cliente/[id].astro:2658
  que falla : La condicion `if (!d.ok || !d.invoices || d.invoices.length === 0)` da FALSA con el objeto envuelto: `!d.ok`=false, `!d.invoices`=false (un objeto es truthy) y `d.invoices.length` es `undefined`, que no es `=== 0`. Se pasa de largo la rama de vacio y en la linea 2662 se ejecuta `d.invoices.forEach(...)` sobre un objeto -> TypeError. La excepcion cae en el `.catch()` de la linea 2675, que oculta el cargando y ensena 'Sin facturas todavia'.
  el cliente: El mensaje que ve el cliente es una mentira tecnica: no es que no tenga facturas, es que la pagina se ha roto. Ni el cliente ni soporte tienen forma de distinguirlo sin abrir la consola del navegador.
  evidencia : Simulacion exacta de la condicion ejecutada en /tmp/sim_invoices.js en la Pi (fuera de los repos): con {ok:true,invoices:{invoices:[{...}]}} imprime `!d.ok -> false`, `!d.invoices -> false`, `d.invoices.length===0 -> false`, `EXCEPCION: d.invoices.forEach is not a function -> cae en .catch() -> muestra Sin facturas todavia`. Con la forma correcta (array) imprime `RAMA: pinta tabla`. Codigo: [id].astro:2658, 2662, 2675-2678.
  alcance   : TODOS los clientes por codigo.
  arreglo   : Ademas de normalizar la forma en portal-client.ts, separar los dos casos en el navegador: el `.catch()` debe mostrar un mensaje distinto ('No hemos podido cargar tus facturas, reintenta') y no reutilizar el div de vacio. Asi un fallo futuro se ve como fallo y no como 'no tienes facturas'.

[MEDIA] error-de-stripe-se-ve-como-sin-facturas
  Si Stripe o la Pi fallan, el portal dice 'Sin facturas todavia' en vez de decir que ha fallado
  donde     : /home/nexux/nexux-pro/src/lib/portal-client.ts:130
  que falla : `if (!response.ok) return [];` y el `catch { return []; }` de la linea 132 convierten cualquier error (500 de la Pi por fallo de Stripe, Pi caida, timeout) en una lista vacia. Aguas arriba, la Pi ya devuelve 500 cuando Stripe falla (provision-http.js:1729-1730).
  el cliente: Un corte de Stripe o de la Pi se le presenta al cliente como 'no tienes facturas'. Nadie se entera de que el historial esta caido: no hay alerta, no hay reintento y el cliente concluye que el producto no emite facturas.
  evidencia : portal-client.ts:126-133 (`if (!response.ok) return []` / `catch { return [] }`); provision-http.js:1724-1731 devuelve 500 con el mensaje de error de Stripe. Los logs de PM2 (~/.pm2/logs/nexux-clients-*.log) no contienen ninguna linea 'invoices error' ni 'billing portal error', lo que indica que ese camino no se ha ejercitado nunca en produccion, no que este sano.
  alcance   : TODOS los clientes por codigo.
  arreglo   : Que getClientInvoices distinga fallo de vacio: devolver `{ ok:false, error:'upstream' }` o lanzar, y que invoices.ts responda 502 con `ok:false`. El navegador ya tiene la rama `!d.ok`: con eso pinta un mensaje de error real en lugar del de vacio.

[ALTA] clientes-manuales-sin-nada-en-facturacion
  Los clientes dados de alta a mano no tienen stripeCustomerId: en Facturacion no pueden hacer absolutamente nada
  donde     : /home/nexux/nexux-clients/provision-http.js:1723
  que falla : Sin `stripeCustomerId` la ruta de facturas corta antes de llamar a Stripe (`if (!stripeCustomerId) return res.json({ invoices: [] })`, linea 1723) y la del portal de Stripe responde 400 `no_stripe_customer` (linea 1856). El portal ademas esconde el boton 'Gestionar suscripcion' cuando `billing.stripe` es false ([id].astro:771, alimentado por provision-http.js:726 `stripe: !!config.stripeCustomerId`). No existe ninguna otra fuente de facturas fuera de Stripe.
  el cliente: Los TRES clientes activos hoy (estudio-ricardo-demo-mostoles-946279, nexux-demo-mostoles-42a928, nexux-empresa) no tienen stripeCustomerId. Para ellos Facturacion es una pantalla muerta: cero facturas, cero justificantes descargables, ningun boton, y ninguna forma de cancelar, cambiar de plan ni cambiar la tarjeta desde el panel. Si uno de ellos quiere darse de baja, tiene que escribir a una persona.
  evidencia : Recorrido de ~/nexux-clients/clients/*/config.json con node: solo las cuentas peluqueria-carmen-e2e-* / -test-96d3e8 y prueba-nexux-pro-c43c20 tienen stripeCustomerId, y todas ellas estan con active:false; los tres con active:true (estudio-ricardo-demo-mostoles-946279, nexux-demo-mostoles-42a928, nexux-empresa) lo tienen a NO. Comprobado en vivo contra la Pi: `GET /client/nexux-demo-mostoles-42a928/billing-portal` -> HTTP 400 `{"error":"no_stripe_customer"}`; `GET .../invoices` -> HTTP 200 `{"invoices":[]}`.
  alcance   : Depende de los datos de cada cuenta (falta stripeCustomerId), pero afecta a TODA alta que no pase por la pasarela: hoy es el 100% de los clientes activos. Las altas nuevas si lo reciben del webhook (nexux-pro/api/webhook/stripe.js:135 `stripeCustomerId: session.customer`), asi que el agujero se hereda solo en las cuentas manuales.
  arreglo   : Dos cosas, y ninguna es cosmetica: (1) al dar de alta a mano, crear igualmente el Customer en Stripe (aunque el cobro sea externo) y guardar su id, para que el cliente tenga portal y facturas como cualquier otro; (2) mientras eso no exista, sustituir la pantalla vacia por una via real de baja desde el panel (formulario que abra ticket y avise por Telegram), en vez de dejar al cliente sin salida.

[ALTA] sin-autogestion-propia-todo-delegado-a-stripe
  Desde nuestro panel no se puede cancelar ni cambiar de plan: no existe el endpoint, solo el enlace a Stripe
  donde     : /home/nexux/nexux-clients/lib/stripe-session.js:67
  que falla : Lo unico que ofrece la autogestion es abrir el portal alojado de Stripe (createCustomerPortalSession, stripe-session.js:67-73). En ~/nexux-clients no hay ninguna llamada a `subscriptions.update`, `subscriptions.cancel` ni `cancel_at_period_end`, y en el portal no hay ningun boton de cancelar ni de cambiar de plan: las tarjetas de plan ([id].astro:798-868) son texto estatico y el propio pie remite a Stripe ([id].astro:870).
  el cliente: Dentro de nuestro panel el cliente NO puede: cancelar, cambiar de plan, cambiar de tarjeta ni ver el importe/fecha del proximo cobro. Solo puede salir a Stripe (si tiene stripeCustomerId). Y descargar una factura tampoco puede, porque la tabla nunca llega a pintarse (hallazgo doble-envoltura-facturas). Resultado practico: la autogestion que promete el panel es una puerta a otra web, y para tres de cada tres clientes activos ni siquiera esa.
  evidencia : grep en ~/nexux-clients (excluyendo node_modules) de `subscriptions.update|subscriptions.cancel|cancel_at_period_end|change-plan|cambiar-plan`: cero coincidencias de codigo (solo textos de emails de upgrade). Rutas de facturacion existentes en provision-http.js: solo :1721 invoices y :1854 billing-portal. En [id].astro los unicos controles son el boton btn-billing-portal (:772, :2620) y el enlace PDF por fila (:2670), que nunca se renderiza.
  alcance   : TODOS los clientes por codigo. Esto es NO EXISTE, no esta roto: nunca se construyo.
  arreglo   : Decidir explicitamente el alcance: si la autogestion se delega a Stripe, entonces el requisito es que TODO cliente tenga Customer en Stripe (ver hallazgo anterior) y que el portal de Stripe tenga guardada su configuracion de portal en modo live, con cancelacion y cambio de plan habilitados. Si se quiere autogestion propia, hacen falta dos endpoints nuevos en provision-http.js (cancelar con cancel_at_period_end y cambiar de plan con subscriptions.update) mas su confirmacion en pantalla. No se puede seguir prometiendo 'cancela cuando quieras' con un enlace que la mayoria de cuentas ni siquiera v

[MEDIA] billing-unavailable-culpa-al-cliente
  Si Stripe falla, el portal le dice al cliente que no tiene suscripcion activa
  donde     : /home/nexux/nexux-pro/src/pages/portal-api/billing.ts:23
  que falla : getBillingPortalUrl devuelve null tanto si la Pi responde 400 (no_stripe_customer) como si responde 500 (fallo de Stripe) (portal-client.ts:135-143, `if (!response.ok) return null`). billing.ts:23-27 colapsa ambos casos en un unico 502 con `error:'billing_unavailable'`, y el navegador traduce ese codigo a 'Esta cuenta no tiene suscripcion activa en Stripe' ([id].astro:2633-2635).
  el cliente: Un cliente que SI paga, si Stripe da un error puntual, lee que su cuenta no tiene suscripcion activa. Es el peor mensaje posible: siembra la duda de si le estan cobrando o no y genera una llamada a soporte.
  evidencia : portal-client.ts:135-143; billing.ts:22-27; [id].astro:2626-2638. Verificado en vivo que la Pi si distingue los dos casos y devuelve 400 `{"error":"no_stripe_customer"}` (curl a /client/nexux-demo-mostoles-42a928/billing-portal), informacion que se pierde al subir de capa.
  alcance   : TODOS los clientes por codigo.
  arreglo   : Propagar el motivo: que getBillingPortalUrl devuelva `{url}` o `{error}` con el codigo de la Pi, que billing.ts responda 400 `no_stripe_customer` frente a 502 `stripe_error`, y que el navegador solo diga 'no tiene suscripcion activa' cuando el motivo sea exactamente ese.

[MEDIA] importe-cero-en-facturas-pendientes
  Una factura pendiente se muestra con importe 0,00 EUR
  donde     : /home/nexux/nexux-clients/lib/stripe-session.js:57
  que falla : El mapeo usa `amount: inv.amount_paid / 100`. En una factura con estado `open` (pendiente de cobro) amount_paid es 0, asi que la fila saldria '0.00 EUR' junto a la etiqueta 'Pendiente' que pinta [id].astro:2666.
  el cliente: En cuanto un cobro se retrase o falle, el cliente vera una factura pendiente de 0,00 EUR. Un importe falso en un documento de dinero destruye la confianza en el panel entero.
  evidencia : stripe-session.js:52-64 (`amount: inv.amount_paid / 100`); [id].astro:2664-2667 formatea `inv.amount.toFixed(2)` y etiqueta `open` como 'Pendiente'. No verificado contra una factura real porque no debo tocar Stripe; el defecto es de codigo y no depende del dato.
  alcance   : TODOS los clientes por codigo.
  arreglo   : Usar `inv.total` (o `amount_due` para las abiertas) como importe de la factura y, si se quiere, exponer amount_paid aparte. Nunca presentar amount_paid como 'importe de la factura'.

[BAJA] historial-limitado-a-12-y-sin-reintento
  Solo se traen 12 facturas, sin paginacion, y un fallo de carga no se puede reintentar
  donde     : /home/nexux/nexux-clients/lib/stripe-session.js:54
  que falla : `stripe.invoices.list({ customer: customerId, limit: 12 })` sin paginacion: pasado el primer ano el cliente pierde de vista sus facturas mas antiguas. Ademas, en el navegador se marca la tabla como `inv-loaded` ANTES de lanzar la peticion ([id].astro:2686-2687 y :2694), asi que si la carga falla, volver a pulsar Facturacion ya no reintenta nada.
  el cliente: A partir del mes 13 el historial se corta en silencio, y cuando la carga falla el cliente se queda con 'Sin facturas todavia' hasta que recargue la pagina entera; pulsar otra vez no hace nada.
  evidencia : stripe-session.js:54; [id].astro:2681-2695 (`table.classList.add('inv-loaded'); loadInvoices();` — la marca se pone siempre, tenga exito o no).
  alcance   : TODOS los clientes por codigo.
  arreglo   : Subir el limite y paginar (o al menos limit:100 con aviso), y mover la marca `inv-loaded` a dentro del `.then()` de exito, quitandola en el `.catch()` para permitir el reintento.

  NOTAS / no verificado:
  QUE HE VERIFICADO DE VERDAD (no leido en un README):
- Camino completo leido en el codigo que ejecuta: /home/nexux/nexux-pro/src/pages/portal-api/invoices.ts (18 lineas, entera), /home/nexux/nexux-pro/src/lib/portal-client.ts:114-143, /home/nexux/nexux-clients/provision-http.js:1721-1731 y :1854-1866, /home/nexux/nexux-clients/lib/stripe-session.js:52-73, y /home/nexux/nexux-pro/src/pages/cliente/[id].astro:762-891 (pintado) y :2619-2695 (JS del navegador).
- Doble envoltura COMPROBADA EN PRODUCCION con curl a https://nexux.pro/portal-api/invoices: devuelve {"ok":true,"invoices":{"invoices":[]}}. Y contra la Pi (127.0.0.1:3460) devuelve {"invoices":[]}. No es una deduccion, es la respuesta real.
- La rama del navegador la he ejecutado, no razonado a ojo: script en /tmp/sim_invoices.js (fuera de los repos) que reproduce la condicion literal de [id].astro:2658. Resultado: NO entra en la rama de vacio, lanza "d.invoices.forEach is not a function" y el .catch() muestra "Sin facturas todavia".
- Que el codigo de la Pi es el desplegado: ~/nexux-pro esta en main, sin commits sin subir (git log origin/main..main vacio) y sin ficheros tracked modificados; el chunk ya construido .vercel/outp

==============================================================================
?  —  13 hallazgos
==============================================================================

[CRITICA] recordatorios-leen-campos-que-no-existen
  Los recordatorios de 24 h y 1 h no se envian nunca a ningun cliente
  donde     : /home/nexux/nexux-clients/lib/scheduler.js:83
  que falla : El cron de recordatorios lee apt.nombre, apt.servicio y apt.phone, pero NINGUNA cita en disco tiene esos campos: se guardan como client_name, service y client_phone. sendWhatsApp recibe phone=undefined y aborta el envio.
  el cliente: La promesa 3 del plan de 29 EUR ('Recuerda la cita al cliente 24 h y 1 h antes') no se cumple para NADIE. Cero recordatorios enviados desde que existe el producto. El cliente paga por evitar ausencias y el aviso no sale.
  evidencia : lib/scheduler.js:83 'sendWhatsApp(clientId, apt.phone, msg)' y :78/:80 'apt.nombre'/'apt.servicio'. Los unicos escritores de citas son lib/data.js:26-42 y lib/booking-engine.js:416, ambos escriben client_name/client_phone/service/reminder_24h_sent. Barrido de las 18 appointments.json: 69 citas, 0 con nombre/servicio/phone/reminded24h. lib/whatsapp.js:727-731 aborta si el telefono no es valido. En el log de PM2: 284 lineas '[wa:estudio-ricardo-demo-mostoles-946279] envio omitido: telefono no valido (undefined)' en las ultimas 3.000 lineas.
  alcance   : TODOS los clientes, por codigo. lib/scheduler.js es codigo compartido, no hay nada por cliente. Cero migracion de datos: las 69 citas existentes ya llevan los nombres correctos.
  arreglo   : En lib/scheduler.js sustituir apt.nombre->apt.client_name, apt.servicio->apt.service, apt.phone->apt.client_phone. Mejor aun: normalizar la lista con normalizeAppointments(getAppointments(clientId), config) de lib/config-normalizer.js, que ya resuelve tambien las variantes camelCase (clientName/clientPhone) que hay en 4 citas.

[CRITICA] recordatorios-marca-antiduplicado-fantasma
  Al arreglar el telefono, cada recordatorio se enviara ~11 veces seguidas
  donde     : /home/nexux/nexux-clients/lib/scheduler.js:87
  que falla : Tras enviar, el cron marca la cita con {reminded24h:true} / {reminded1h:true}, campos que no lee nadie mas. La condicion de guarda tambien es !apt.reminded24h, que siempre es undefined. El cron corre cada minuto con una ventana de +-5 min, asi que la misma cita entra 11 veces.
  el cliente: Hoy no se ve porque no se envia nada. En cuanto se corrija el telefono sin corregir esto, el cliente final del salon recibira 11 WhatsApps identicos a 24 h y otros 11 a 1 h. Eso es motivo de bloqueo del numero de WhatsApp del negocio.
  evidencia : lib/scheduler.js:68 cron '* * * * *'; :57-63 isInWindow con toleranceMinutes=5 (ventana total 10 min); :75 '!apt.reminded24h'; :87 updateAppointment(...,{reminded24h:true}). Los campos reales son reminder_24h_sent / reminder_1h_sent (lib/data.js:36-37, lib/booking-engine.js:416, lib/config-normalizer.js:349-350).
  alcance   : TODOS los clientes, por codigo. Es el mismo fichero compartido. Sin migracion: los flags reminder_24h_sent/reminder_1h_sent ya existen en las 69 citas y estan a false.
  arreglo   : Usar reminder_24h_sent/reminder_1h_sent tanto en la guarda como en el updateAppointment. Arreglar esto EN EL MISMO commit que el telefono, nunca despues.

[ALTA] resumen-diario-va-a-un-solo-chat-global
  El resumen de cada tarde se manda a un unico chat de Telegram, no al duenno del salon
  donde     : /home/nexux/nexux-clients/lib/scheduler.js:145
  que falla : El resumen de las 21:00 se construye por cliente pero se envia siempre a process.env.TELEGRAM_CHAT_ID, un solo chat fijo para toda la instalacion. No usa el ownerChatId del cliente.
  el cliente: La promesa 4 del plan de 29 EUR ('Te manda un resumen cada tarde') no llega al que paga: llega al chat de administracion de Nexux. Ademas, con varios clientes vendidos, ese chat recibe el resumen de todos los salones mezclados y ninguno recibe el suyo.
  evidencia : lib/scheduler.js:12 'const TG_CHAT_ID = process.env.TELEGRAM_CHAT_ID || process.env.TG_CHAT_ID'; :21 'chat_id: TG_CHAT_ID'; :145 'await sendTelegram(lines.join(...))' dentro del bucle por cliente. El mecanismo correcto YA existe y no se usa aqui: lib/telegram.js:795-807 notifyOwnerTelegram lee cfg.channels.telegram.ownerChatId. Ademas las lineas del resumen usan a.nombre y a.servicio (scheduler.js:133 y :141), campos inexistentes, asi que el texto saldria como 'undefined (undefined)'.
  alcance   : TODOS los clientes, por codigo. Hay un matiz de datos: solo 6 de 19 configs tienen channels.telegram.ownerChatId, y las 6 comparten el mismo valor (511455969, cuentas de prueba de Ricardo). De los 3 clientes activos, solo nexux-demo-mostoles-42a928 lo tiene.
  arreglo   : Sustituir sendTelegram(...) por notifyOwnerTelegram(clientId, ...) y corregir a.nombre/a.servicio -> a.client_name/a.service. Anadir en el onboarding un paso obligatorio para vincular el Telegram del duenno; sin ownerChatId no hay resumen posible y hoy eso no se avisa en ningun sitio.

[ALTA] scheduler-lista-de-clientes-congelada
  Un cliente dado de alta hoy no entra en los recordatorios hasta que se reinicie el servicio
  donde     : /home/nexux/nexux-clients/index.js:60
  que falla : startScheduler(clients) recibe el array de clientes leido UNA vez al arrancar el proceso. /provision crea la carpeta del cliente pero no lo anade a ese array ni reinicia nada. Ademas config queda congelado: un cliente desactivado despues sigue procesandose y un horario editado en el portal no se ve.
  el cliente: Un salon que compra hoy no tiene recordatorios ni resumen hasta el siguiente reinicio de PM2, sin ningun aviso. Es exactamente el fallo que el duenno teme: 'funciona en mi cuenta pero no en el que acabo de vender'.
  evidencia : index.js:12-36 loadClients() lee el disco una vez; index.js:60 'startScheduler(clients)'; lib/scheduler.js:69 'for (const { clientId, config } of clients)' y :70 'if (!config.active) continue'. grep 'scheduler' en provision-http.js: 0 coincidencias, el alta no registra nada. El propio codigo lo reconoce en lib/data.js:207-213 (getAllActiveClientIds, 'Used by scheduler for crons that run after new clients may have been provisioned') pero solo se usa en el cron del blog (scheduler.js:164), no en el de recordatorios ni en el del resumen.
  alcance   : TODOS los clientes nuevos, por codigo. Sin migracion de datos.
  arreglo   : Que los crons de recordatorios (scheduler.js:68) y de resumen (scheduler.js:109) resuelvan la lista en cada ejecucion leyendo el disco (getAllActiveClientIds + getClientConfig, lib/data.js:209 y :215) en vez de usar el array del arranque. Ojo: getAllActiveClientIds lee index.json, cuyo campo active esta desfasado (ver hallazgo index-json-active-desfasado); conviene filtrar por config.json.

[ALTA] facturas-doble-envoltorio
  El portal dice 'Sin facturas todavia' aunque la factura exista
  donde     : /home/nexux/nexux-pro/src/lib/portal-client.ts:131
  que falla : La Pi responde {invoices:[...]}. getClientInvoices lo devuelve tal cual tipandolo como Invoice[] (es un objeto, no un array). La ruta de Astro lo vuelve a envolver, y al navegador le llega {ok:true, invoices:{invoices:[...]}}. En el navegador d.invoices.length es undefined (no pasa el if de vacio) y d.invoices.forEach revienta con TypeError, que cae en el .catch y pinta el mensaje de vacio.
  el cliente: El cliente que paga entra en Facturacion y no ve NINGUNA factura, nunca. No puede descargarse el PDF para su gestoria. Ademas el mensaje miente: dice que no hay facturas cuando si las hay.
  evidencia : provision-http.js:1727 'res.json({ invoices })'. src/lib/portal-client.ts:131 'return (await response.json()) as Invoice[]'. src/pages/portal-api/invoices.ts:14 'JSON.stringify({ ok: true, invoices })'. src/pages/cliente/[id].astro:2658 'if (!d.ok || !d.invoices || d.invoices.length === 0)' -> false porque length es undefined; :2662 'd.invoices.forEach(...)' -> TypeError; :2676-2679 el .catch pinta 'invoices-empty'. El repo ~/nexux-pro esta a 0/0 respecto a origin/main, o sea que lo desplegado en Vercel es este codigo.
  alcance   : TODOS los clientes que tengan stripeCustomerId, por codigo. Cero datos por cliente implicados.
  arreglo   : En src/lib/portal-client.ts:125-133, desenvolver: 'const data = await response.json(); return Array.isArray(data) ? data : (data.invoices ?? [])'. Y en [id].astro:2662 blindar con Array.isArray antes del forEach para que un formato inesperado no se disfrace de 'sin facturas'.

[ALTA] horario-duplicado-ingles-espanol
  El horario se guarda dos veces, en ingles y en espanol, y no coinciden
  donde     : /home/nexux/nexux-clients/provision-http.js:813
  que falla : Cuatro configs tienen el horario escrito con claves inglesas Y espanolas a la vez, con valores distintos. El endpoint que guarda el horario hace un merge que NUNCA borra las claves sobrantes, asi que el duplicado no se puede limpiar desde el portal. La plantilla _base.json solo trae claves inglesas: el espanol entro por otra via (no verificado cual).
  el cliente: Manda la clave inglesa (config-normalizer.js decide asi a proposito), pero el duenno que edite el horario en espanol no vera ningun efecto y no se le avisa. Peor: en nexux-demo-mostoles-42a928, monday declara parada de comida 14:00-16:00 y lunes dice 14:01-15:01; en new-look-7320e8, saturday cierra a las 14:00 y sabado a las 20:00. Es una bomba de relojeria: si algun dia se invierte la precedencia, se ofrecen citas con el salon cerrado.
  evidencia : provision-http.js:813 'if (schedule) config.schedule = { ...config.schedule, ...schedule };' (merge, nunca borra). lib/config-normalizer.js:88-134 normalizeSchedule y su comentario :78-84 documentan el caso. En produccion, log de PM2: '[config-normalizer] el horario esta escrito en ingles y en espanol y NO coincide en: friday, monday, thursday, tuesday'. Barrido de las 19 configs: 4 con doble idioma y discrepancia (estudio-ricardo-demo-mostoles-946279, new-look-7320e8, nexux-demo-mostoles-42a928, prueba-nexux-pro-c43c20), 2 con SOLO claves espanolas (nexux-empresa y demo, este ultimo ademas us
  alcance   : MIXTO. El codigo (el merge que no borra) afecta a todos. Los datos sucios afectan HOY a 4 clientes de 19, mas 2 con formato antiguo. Hay que arreglar codigo Y migrar datos.
  arreglo   : 1) Codigo: en provision-http.js:813, antes de mezclar, eliminar de config.schedule cualquier alias no canonico (traducir con el DAY_ALIASES de config-normalizer.js y quedarse solo con la clave inglesa). 2) Datos: script de migracion en 4 configs que borre las claves espanolas conservando el valor ingles; para nexux-empresa y demo, convertir espanol->ingles y 'horario'->'schedule'. Son 6 ficheros, no hay volumen. 3) Convertir el console.warn en una alerta que se vea, no solo en el log.

[ALTA] prompt-de-lara-con-dias-undefined
  A Lara se le pasa el horario con siete lineas que empiezan por 'undefined'
  donde     : /home/nexux/nexux-clients/lib/bot-prompt.js:23
  que falla : El prompt del bot recorre config.schedule EN CRUDO, sin pasar por el normalizador. Con el horario duplicado salen 14 lineas: 7 correctas y 7 que dicen 'undefined: 09:00-19:00', porque DAYS_MAP solo conoce las claves inglesas.
  el cliente: Lara recibe un horario contradictorio y con basura en cada conversacion de esos salones. Puede citar horas equivocadas a un cliente final. La ruta de huecos si esta bien (usa el normalizador), asi que Lara puede decir una cosa y la agenda otra.
  evidencia : lib/bot-prompt.js:4-7 DAYS_MAP solo con claves inglesas; :23-25 'Object.entries(config.schedule || {}).map(([d, s]) => ... DAYS_MAP[d] ...)'. Simulado con la config real de nexux-demo-mostoles-42a928: salen 7 lineas correctas y 7 'undefined: HH:MM-HH:MM'. En cambio la disponibilidad si normaliza (lib/whatsapp.js:364 availableSlotIsos -> booking-bridge.js:52 normalizeConfig).
  alcance   : Codigo compartido, pero solo se dispara en los clientes con horario duplicado: 4 de 19 hoy. Se apaga solo en cuanto se migren los datos del hallazgo anterior, pero el codigo sigue siendo fragil.
  arreglo   : En bot-prompt.js construir scheduleText desde normalizeConfig(config).schedule en vez de config.schedule, o al menos filtrar las claves que DAYS_MAP no conoce.

[ALTA] webhook-pi-crea-clientes-con-forma-invalida
  Hay un segundo camino de alta en la Pi que crea el cliente con una forma que no lee nadie
  donde     : /home/nexux/nexux-clients/lib/stripe-webhook.js:118
  que falla : createClientDir() escribe un config.json que NO usa las plantillas: sin accessToken, sin clientId, sin schedule, sin services, sin channels, sin bot_name, sin limits, sin features, sin metrics, y con las claves cambiadas (id, created_at, stripe_session_id, salon_name). Tampoco crea appointments.json ni conversations.json.
  el cliente: Si ese camino se dispara, el cliente paga y nace una cuenta muerta: sin token no hay enlace de portal (provision-http.js:530 lo construye con config.accessToken), sin channels.whatsapp el arranque del bot revienta (provision-http.js:519 lee config.channels.whatsapp.provider) y sin schedule/services Lara no puede citar. Y no se detecta: el evento se marca como procesado.
  evidencia : lib/stripe-webhook.js:118-141 createClientDir vs provision-http.js:92-137 buildClientConfig (que si carga templates/_base.json + templates/<plan>.json). El camino BUENO es el de Vercel: api/webhook/stripe.js:130-190 llama a POST /provision de la Pi. Pero el endpoint /webhook/stripe de la Pi TAMBIEN esta dado de alta en Stripe: en el log hay '[stripe-webhook] firma OK: customer.subscription.updated' y '... deleted' con firma valida, cosa imposible si Stripe no le entregara. Hasta ahora ese endpoint no ha recibido ningun checkout.session.completed (0 lineas '[stripe-webhook] new client' en 20.00
  alcance   : TODOS los clientes futuros si alguien activa el evento checkout.session.completed en ese endpoint de Stripe. Codigo compartido.
  arreglo   : Borrar createClientDir y toda la rama checkout.session.completed de lib/stripe-webhook.js (lineas 400-491), dejando ese receptor solo para los eventos de ciclo de vida que si atiende. Un unico camino de alta: /provision con templates/. Verificar en el panel de Stripe que ese endpoint no tiene suscrito checkout.session.completed (no lo he podido comprobar: tenia prohibido tocar Stripe).

[MEDIA] index-json-active-desfasado
  El indice de clientes dice que estan activos 10 clientes que en realidad estan desactivados
  donde     : /home/nexux/nexux-clients/lib/stripe-webhook.js:412
  que falla : Cuando Stripe cancela una suscripcion, el webhook pone active:false en el config.json del cliente pero no llama a deactivateClient(), asi que clients/index.json sigue diciendo active:true. deactivateClient existe y solo se usa en la ruta manual (provision-http.js:592).
  el cliente: Cualquier funcion que confie en el indice trata como activo a quien ya no paga. getAllActiveClientIds (lib/data.js:209-213) lee justo ese campo y es el que decide para quien corre el cron del blog. Al reves tambien pasa: nexux-empresa esta activo en su config y apagado en el indice.
  evidencia : lib/stripe-webhook.js:406-419 (subscription.deleted) escribe solo found.cfgPath; no importa deactivateClient. lib/clients-index.js:63-67 deactivateClient. Comparacion index.json vs config.json: 18 entradas en el indice, 10 con active discrepante (7 peluqueria-carmen-*, kalon-estetica-*, prueba-nexux-pro-c43c20 y nexux-empresa). prueba-nexux-pro-c43c20 es el caso vivo: el log muestra '[stripe-webhook] deactivated: prueba-nexux-pro-c43c20', su config dice active:false y el indice sigue diciendo true.
  alcance   : MIXTO. El codigo afecta a todos los que cancelen. Los datos ya desfasados son 10 de 18 entradas del indice. Ademas el cliente 'demo' existe en disco y NO esta en el indice.
  arreglo   : 1) Codigo: en stripe-webhook.js (subscription.deleted) llamar a deactivateClient(found.clientId). 2) Datos: script que recorra clients/*/config.json y reescriba index.json.clients[*].active con la verdad del config. 3) Mejor todavia: que index.json deje de guardar 'active' y que quien lo necesite lea el config, para no tener el mismo dato en dos sitios.

[MEDIA] plan-equipo-nace-sin-agendas
  Quien compra el plan Equipo de 79 EUR puede nacer con cero agendas
  donde     : /home/nexux/nexux-clients/provision-http.js:135
  que falla : En el alta, professionals y booking.mode='team' SOLO se ponen si en el checkout viajo el dato 'trabajadoras'. Ese campo es opcional en el checkout. Si falta, un cliente de plan 'equipo' nace en modo single y con professionals vacio. La plantilla templates/equipo.json tampoco lo pone.
  el cliente: Paga 79 EUR por la agenda por profesional y arranca con una sola agenda compartida: dos citas a la misma hora con dos personas distintas se bloquean entre si, que es justo lo que compro para dejar de sufrir. Tiene que descubrir por su cuenta que debe crearlas en el CRM.
  evidencia : provision-http.js:135 'ct(equipo ? { professionals: equipo, booking: { mode: team } } : {})' con equipo = equipoInicial(trabajadoras); lib/equipo-inicial.js:60-62 'if (!cuantas || cuantas < 2) return null'. templates/equipo.json no trae professionals ni booking. api/stripe/create-session.js:49 mete 'trabajadoras' en metadata solo si viene en el body. El camino de SUBIDA de plan si lo resuelve (lib/stripe-webhook.js:377-392 crea al menos una agenda), o sea que un cliente que sube a Equipo queda mejor montado que uno que lo compra de cero.
  alcance   : TODOS los clientes de plan 'equipo' que compren sin declarar cuantas son. Por codigo. Hoy no hay ningun cliente 'equipo' en produccion (0 de 19), asi que no hay nada que migrar todavia.
  arreglo   : Aplicar en provision-http.js:135 la misma regla que ya usa stripe-webhook.js:385-390: si planPermite(config,'agenda_por_profesional') y no hay professionals, crear al menos una agenda y booking.mode='team'. Y hacer 'trabajadoras' obligatorio en el checkout del plan Equipo.

[MEDIA] mrr-admin-ignora-los-planes-en-venta
  El panel de administracion cuenta 0 EUR de MRR por cada cliente de los planes que se venden hoy
  donde     : /home/nexux/nexux-clients/provision-http.js:1605
  que falla : La tabla PLAN_MRR solo tiene starter/pro/total/demo, el catalogo anterior al pivote de agosto de 2026. Los planes vigentes, 'recepcionista' (29) y 'equipo' (79), no estan, y el codigo hace 'PLAN_MRR[cfg.plan] || 0'.
  el cliente: No lo ve el cliente final: lo ve el duenno del producto. Cada venta real suma 0 al MRR del panel. Con dos clientes de recepcionista activos hoy, el panel dice 0 EUR y parece que no vende nada.
  evidencia : provision-http.js:1605 'const PLAN_MRR = { starter: 39, pro: 79, total: 129, demo: 0 };' y :1619 'const planMrr = cfg.active ? (PLAN_MRR[cfg.plan] || 0) : 0;'. Los planes validos en el alta son otros: provision-http.js:419 acepta ['starter','pro','total','recepcionista','equipo']. Existen templates/recepcionista.json y templates/equipo.json. 3 de los 19 clientes son de plan 'recepcionista'.
  alcance   : TODOS los clientes de los planes actuales, por codigo. Sin migracion.
  arreglo   : Anadir recepcionista:29 y equipo:79 a PLAN_MRR. Mejor: sacar los precios a lib/planes.js, que ya es el sitio unico donde vive 'que da cada plan', para que no haya dos catalogos que se desincronicen otra vez.

[BAJA] citas-en-camelcase-que-nadie-normaliza
  Cuatro citas guardadas con clientName/clientPhone que los caminos crudos no saben leer
  donde     : /home/nexux/nexux-clients/clients/peluqueria-carmen-e2e-madrid-fdef01/appointments.json:1
  que falla : Cuatro citas usan clientName/clientPhone en vez de client_name/client_phone. El normalizador las entiende (config-normalizer.js:341-342) pero los caminos que leen el JSON en crudo, como el scheduler, no.
  el cliente: Hoy ninguna: ese cliente esta inactivo. Importa porque prueba que en disco conviven al menos tres formatos de cita, y un arreglo del scheduler que solo mire client_phone volveria a fallar en silencio si ese formato reaparece.
  evidencia : Barrido de las 18 appointments.json: 69 citas, 0 con los nombres viejos (nombre/servicio/phone), 4 con clientName/clientPhone, todas en peluqueria-carmen-e2e-madrid-fdef01 (config active=false). Claves distintas vistas en el conjunto: client_name, clientName, client_phone, clientPhone, service, service_id, google_event_id, version, etc.
  alcance   : Datos de 1 cliente de 19 (4 citas de 69), y ese cliente esta inactivo. No obliga a migrar nada urgente.
  arreglo   : No migrar: hacer que el scheduler lea las citas a traves de normalizeAppointments(), que ya resuelve las dos formas. Asi el formato deja de importar.

[BAJA] carpetas-de-cliente-sin-config
  Tres carpetas de cliente sin config.json arrastradas de pruebas
  donde     : /home/nexux/nexux-clients/clients:1
  que falla : clinica-prueba-auditoria-madrid-91a907, clinica-prueba-auditoria-madrid-ca9ebf y nexux-demo-mostoles-9716d5 son directorios de cliente sin config.json.
  el cliente: Ninguna hoy: index.js:29 salta las carpetas sin config y findClientByStripeCustomer (stripe-webhook.js:104-116) las traga con un catch vacio. Es ruido que ensucia cualquier recuento y hace dificil responder 'cuantos clientes tengo'.
  evidencia : find clients -maxdepth 1 -type d -> 23 (22 clientes + .locks); find clients -maxdepth 2 -name config.json -> 19. Ninguna de las tres aparece en clients/index.json.
  alcance   : Datos, 3 carpetas. No afecta a codigo.
  arreglo   : Borrarlas tras comprobar que no tienen sesion de WhatsApp viva en auth/. No es urgente.

  NOTAS / no verificado:
  RESPUESTA DIRECTA A LA PREGUNTA DEL DUENNO: los dos defectos que ibas a arreglar viven en CODIGO COMPARTIDO, no en datos de tu cuenta. Arreglarlos vale para todos los clientes que vendas, sin migrar nada.
- Recordatorios (lib/scheduler.js): un solo fichero, comun a todos. Las 69 citas que hay en disco ya llevan los nombres correctos (client_name/client_phone/service/reminder_24h_sent), o sea cero migracion. AVISO IMPORTANTE: no arregles solo el telefono. Si corriges el telefono y dejas la marca reminded24h, pasas de 'no llega ningun aviso' a 'llegan once avisos iguales', que es peor. Van en el mismo commit.
- Facturas (src/lib/portal-client.ts:131): un solo fichero de la web, comun a todos. Cero datos por cliente.
Lo que SI obliga a migrar datos, y por eso lo separo: el horario duplicado en ingles y espanol (4 configs de 19 con valores contradictorios, mas 2 con formato antiguo) y el campo active desfasado en clients/index.json (10 entradas de 18). En los dos casos hay ademas un fallo de codigo detras, asi que hace falta arreglar codigo Y limpiar datos; si solo limpias los datos, se vuelven a ensuciar.
LA MAQUETA DEL ALTA (lo que pediste en el punto 1 y 2): el molde real son templa
