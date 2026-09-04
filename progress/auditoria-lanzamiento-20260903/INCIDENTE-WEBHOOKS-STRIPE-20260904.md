# INCIDENTE — Los webhooks de Stripe llevaban 4 meses sin entregar nada

**Fecha:** 4 de septiembre de 2026, 10:00–13:00
**Gravedad:** máxima. El camino del dinero estaba cortado desde el 19 de mayo de 2026.
**Estado:** CERRADO Y VERIFICADO.

---

## 1. Resumen en una frase

Los dos buzones de avisos de Stripe estaban creados pidiendo una versión de API
(`2026-04-22.dahlia`) que la cuenta no sabe generar (`2025-08-27.basil`). Cuando eso
pasa, **Stripe no entrega el aviso y no lo reintenta**: sin error, sin reintento, sin
una sola línea en ningún registro. El alta automática de clientes **no funcionó nunca**.

---

## 2. Cómo se detectó

Ricardo hizo una compra real de 29 € (11:16:37, `evt_1UBtEf2SQwDzHtsFVnJCZIGJ`).
El pago llegó al banco. No se creó ninguna cuenta.

Búsquedas hechas, todas negativas:

| Se buscó por | Resultado |
|---|---|
| `stripeSessionId` de la compra | sin cliente |
| `stripeSubscriptionId` `sub_1UBtEa…` | sin cliente |
| `stripeCustomerId` `cus_VCHnSFwP5PjSkz` | sin cliente |
| nombre del negocio "Prueba_Nexux.pro" | sin cliente |
| `clients/index.json` → `bySession` | 1 entrada, y no era ésta |
| registro de la Pi, línea `/provision` | ninguna |
| registro de Vercel filtrado por POST | solo `/api/stripe/create-session` |

Los datos de la compra eran correctos: `salon`, `telefono`, `email`, `plan`. Es decir,
**el problema no estaba en el código ni en los datos**: el aviso nunca salió de Stripe.

---

## 3. La pista que resolvió el caso

`pending_webhooks: 0` en el evento **desde el primer instante**.

Eso no significa "la entrega falló". Significa **"Stripe decidió que no había a quién
entregar"**. Una entrega fallida deja el contador por encima de 0 durante los 3 días de
reintentos. Un contador a 0 nada más nacer el evento sólo pasa cuando ningún buzón lo
reclama.

La causa documentada de que un buzón activo y suscrito no reclame un evento es que la
**versión de API que pide el buzón no puede representar ese evento**.

---

## 4. La prueba

No se dio por buena la hipótesis. Se montó un experimento que la pudiera desmentir:

1. Se creó un buzón **temporal** apuntando a la **misma URL** de la Pi, **sin pedir
   versión** (hereda la de la cuenta) y suscrito a `customer.subscription.updated`.
2. Se disparó ese evento.
3. La Pi registró la llegada a las **11:55:46** (rechazada por firma, porque el buzón
   temporal tiene otra clave — irrelevante: lo que se medía era si **llega**).
4. Se borró el buzón temporal.

Contraprueba: el mismo tipo de evento, con los buzones de producción (versión clavada),
no dejó ni una línea entre las 10:39 y las 11:54.

Control positivo del método: una petición propia marcada a las 11:54:04 **sí** quedó
registrada, lo que demuestra que el registro captura todo intento, incluidos los
rechazados. El silencio, por tanto, era ausencia de llegada y no un fallo de registro.

---

## 5. Consecuencia histórica

Los tres clientes activos **no tienen `stripeCustomerId`**:

- `estudio-ricardo-demo-mostoles-946279`
- `nexux-demo-mostoles-42a928`
- `nexux-empresa`

Todos se dieron de alta a mano. **El alta automática no había funcionado ni una sola vez**
desde que se creó el buzón de Vercel el 19 de mayo de 2026. Los arreglos del código
hechos la noche del 3 al 4 de septiembre eran correctos y necesarios, pero estaban
detrás de una puerta a la que Stripe nunca llamó.

---

## 6. Todos los fallos encontrados hoy, en orden

| # | Fallo | Cómo se detectó | Estado |
|---|---|---|---|
| 1 | Ambos buzones clavados a `2026-04-22.dahlia`, versión que la cuenta (`2025-08-27.basil`) no genera, así que Stripe no entrega ni reintenta | `pending_webhooks: 0` más el experimento con buzón temporal | **RESUELTO** |
| 2 | El buzón de la Pi creado esta mañana se creó **copiando esa misma versión** del roto: se reprodujo el fallo | La misma prueba lo destapó | **RESUELTO** (rehecho) |
| 3 | La versión de un buzón **no se puede cambiar**: la API de actualización no acepta `api_version`. Hay que borrar y crear, y eso genera **clave de firma nueva** | Documentación e intento | Asumido en el procedimiento |
| 4 | Stripe **sólo enseña la clave de firma al crear** el buzón por API. Consultarlo después no la devuelve | Falló un intento anterior de leerla | Asumido: crear y guardar en el mismo paso |
| 5 | En Vercel la variable se creó como `STRIPEWEBHOOKSECRET`, **sin guiones bajos**. El código busca `STRIPE_WEBHOOK_SECRET`, no la ve y rechaza todo con 400 | Prueba de firma: quedó 1 entrega pendiente | **RESUELTO** |
| 6 | Ya existía otra variable `STRIPE_WEBHOOK_SECRET` con el valor **viejo**, así que renombrar chocaba | Error de Vercel al renombrar | **RESUELTO** (se cambió el valor de la existente) |
| 7 | El código de Vercel devuelve **400 tanto si falta la clave como si la firma es mala**: indistinguible desde fuera | Lectura de `api/webhook/stripe.js:16-21` | Pendiente (mejora, no bloqueante) |
| 8 | Cloudflare responde **403 error 1010** a peticiones de `python-urllib` contra `pi.nexux.pro` | Al reproducir la compra | Rodeado: se llama a `127.0.0.1:3460` |
| 9 | La Pi **sólo registra** eventos cuando encuentra cliente: un evento aceptado sin cliente asociado no deja rastro, así que el silencio es ambiguo | `lib/stripe-webhook.js:239-260` | **RESUELTO** (commit 9d23acf) |
| 10 | Guardián del script de borrado demasiado estricto: exigía versión **vacía** y el buzón bueno la tiene **explícita pero correcta** | El script se negó a borrar | **RESUELTO** (compara con la versión real de la cuenta) |

---

## 7. Qué se ha hecho, con evidencia

| Acción | Evidencia |
|---|---|
| Buzón de la Pi rehecho sin versión clavada | `we_1UBtum2SQwDzHtsF0l8UOnuj`, versión heredada |
| Clave de firma guardada en el `.env` de la Pi | escritura en binario, verificada línea a línea; copia de seguridad previa |
| Servicio `nexux-clients` reiniciado | `pm2 status: online` |
| La Pi acepta eventos firmados | `evt_1UBu4F…` con `pending_webhooks=0` y **sin** línea de rechazo |
| Buzón de Vercel recreado con la versión de la cuenta | `we_1UBuBE2SQwDzHtsFzwx5YKm8`, `2025-08-27.basil`, 1 evento |
| Variable de Vercel corregida y redesplegada | prueba de firma: `evt_1UBuRr2SQwDzHtsF2vKB8w1x` con `pending_webhooks=0` |
| Buzón viejo borrado | `we_1TYhnJ2SQwDzHtsFlg9HdpO8` eliminado, con relevo comprobado antes |
| Compra real reproducida por el camino real | ver sección 8 |

---

## 8. La compra de 29 € reproducida y verificada

No se creó la cuenta a mano. Se leyó la sesión de pago del **propio evento** de Stripe, se
armó **el mismo cuerpo** que arma `provisionClient()` en `api/webhook/stripe.js` y se mandó
a **la misma ruta**, `/provision`, con la misma cabecera.

| Comprobación | Resultado |
|---|---|
| Cuenta creada | `prueba-nexux-pro-c43c20`, activa, plan `recepcionista` |
| Es de pago, no prueba | `accountMode: stripe_paid`, `isTrial: false` |
| Ligada al pago | `cus_VCHnSFwP5PjSkz` y `sub_1UBtEa…` — **primer cliente con identificador de Stripe** |
| Correo de bienvenida | `welcomeEmailSentAt: 10:25:53Z`, acuse de Brevo |
| El enlace del correo abre el panel | 132.292 bytes, con el nombre del negocio y el precio |
| Un enlace inventado no entra | `login?reason=expired`, 12.512 bytes |
| Repetir el aviso no duplica | `alreadyProvisioned: true`; **1** cuenta, **1** correo |

---

## 9. Estado final de los buzones

```
[OK] we_1UBuBE2SQwDzHtsFzwx5YKm8  enabled  2025-08-27.basil
     https://nexux.pro/api/webhook/stripe
     checkout.session.completed

[OK] we_1UBtum2SQwDzHtsF0l8UOnuj  enabled  la de la cuenta
     https://pi.nexux.pro/webhook/stripe
     customer.subscription.updated, customer.subscription.deleted,
     invoice.payment_failed, invoice.payment_action_required, invoice.paid
```

---

## 10. Reglas que quedan para siempre

1. **Al crear un buzón por API, NO pasar `api_version`.** Que herede la de la cuenta.
   Pasarla lo rompe en silencio.
2. **`pending_webhooks: 0` recién nacido el evento significa que nadie lo reclamó.** No es
   éxito. Éxito es que baje a 0 *después* de haberlo intentado.
3. **Para saber si un buzón acepta la firma sin gastar un euro:** añadirle temporalmente
   un evento inofensivo, dispararlo, mirar `pending_webhooks` a los 20 s.
   0 significa que respondió 2xx (firma válida); más de 0, que dio 400. Y quitar el evento.
4. **El silencio en un registro no es prueba de nada** hasta demostrar que ese registro
   capta lo que buscas: mandar una petición marcada propia y verla aparecer.
5. **Un nombre de variable mal escrito es indistinguible de una clave mala** desde fuera:
   los dos dan 400. Comprobar el nombre carácter a carácter.

---

## 11. Lo que queda pendiente

- `src/pages/gracias.astro` sigue prometiendo "en menos de 24 horas te contactamos" y
  "Ricardo te escribe". Ahora el alta es automática: contradice lo que pasa de verdad.
- El campo "¿Cómo se llama tu negocio?" se ve con muy poco contraste.
- `www.nexux.es/mi-cuenta` da 404 desde algún punto del flujo de compra.
- Fallo #7: distinguir en el código "falta la clave" de "firma inválida".
- Limpieza: `.env.copia-*` en `~/nexux-clients` (se conservan como vuelta atrás).

---

## 12. Prueba positiva directa del buzón de la Pi (12:51)

El resultado de la sección 8 seguía siendo **indirecto**: "0 entregas pendientes y silencio en
el log" es exactamente lo que se veía cuando Stripe **no entregaba nada**, porque la Pi sólo
escribía al encontrar cliente. Se intentó un registro independiente de llegada en `cloudflared`:
no sirve, sólo anota errores.

Así que se arregló la causa de la ambigüedad (fallo #9). Commit `9d23acf`: la Pi registra ahora
**todo** evento cuya firma acepta, tenga cliente o no. Repetida la prueba con un evento real:



Condiciones que hacen la prueba concluyente:

- **Un solo oyente.** Tras el arreglo, la Pi es el único buzón suscrito a
  `customer.subscription.updated`, comprobado por API antes de disparar; el script aborta si
  hay más de uno. Así `pending_webhooks` cuenta sólo las entregas de la Pi.
- **Evento real firmado por Stripe**, no una petición fabricada.
- `pending_webhooks = 0` **y** cero líneas de rechazo desde el reinicio.
- Suite 159/160; el único fallo es `citas-zona-horaria`, que se niega por diseño a correr
  sobre el repositorio de producción y falla idéntico sin el cambio.

No se usó el botón "Send test webhook" del panel por dos razones: el Workbench nuevo no lo
tiene, y esta prueba es mejor — usa un evento real y deja evidencia permanente para todos los
que vengan detrás.
