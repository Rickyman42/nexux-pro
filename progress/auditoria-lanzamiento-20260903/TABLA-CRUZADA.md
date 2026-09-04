# TABLA CRUZADA DE BLOQUEANTES — auditoría de lanzamiento nexux.pro
**3-sep-2026** · Fase 2 (consolidación) · Fuente: los 7 informes de `~/nexux-pro/progress/auditoria-lanzamiento-20260903/`
Nada de esta tabla procede de memoria: cada fila cita el informe y la evidencia que lo sostiene.

## Recuento
17 bloqueantes declarados · **2 ya resueltos hoy** · 1 duplicado entre informes (D-B2 = E-B1) → **14 bloqueantes abiertos**.
Veredictos: A *sí con correcciones* · B **NO** · C **NO** · D **NO** · E *sí con correcciones* · G *(pendiente de recuento)* · H *sí con correcciones*.

---

## GRUPO 1 — La carpeta `api/` de la raíz se come las rutas (1 causa, 4 síntomas)
Una carpeta `api/` en la raíz del proyecto Astro gana sobre `vercel.json` y sobre `src/pages/api/`. Todo lo que caiga bajo `/api/` puede estar muerto sin avisar.

| Id | Síntoma | Evidencia | Informe |
|---|---|---|---|
| G1-a | El checkout y el webhook que EJECUTAN son los de la raíz, no los de la Pi | `nexux.pro` → `Server: Vercel`; `pi.nexux.pro` → `x-powered-by: Express` y rechaza el plan `equipo` | B (#7, #8) |
| G1-b | `POST /api/book` → **404**: el formulario público de reserva no reserva | `curl -X POST https://nexux.pro/api/book` → 404 NOT_FOUND, confirmado dos veces por separado | D-B2 · E-BLOQ-1 |
| G1-c | `POST /api/analytics/ob` → **404**: no se mide dónde se abandona el alta | mismo curl | E-ALTA-3 |
| G1-d | El rewrite de `vercel.json` a la Pi **está documentado y no se aplica** | lectura + petición real | B-A3 |

**Coste de no arreglar la causa:** cada ruta nueva que se escriba en Astro nace muerta y en silencio. Ya nos ha costado un arreglo dado por bueno (commit `44241c0`).

---

## GRUPO 2 — El camino del dinero no tiene un solo dueño (4 bloqueantes)

| Id | Síntoma | Evidencia | Informe |
|---|---|---|---|
| B1 | **Nadie se da de alta al pagar.** `provisionClient()` aborta por falta de `salon` | el guard corta; `salon` sale de `sessionStorage.laraData` y **ningún script lo escribe** (grep en `src/` + descarga de los 6 bundles servidos). La sesión real trae `metadata:{plan}` y `custom_fields:[]` | B-B1 |
| B2 | Cancelaciones, cambios de plan y pagos fallidos **se ignoran** | los 2 endpoints de Stripe resuelven a la función de Vercel, que solo trata `checkout.session.completed`; `GET /v1/webhook_endpoints` no lista ninguna URL de la Pi | B-B2 |
| B3 | Cada compra dispara el webhook **dos veces**, sin protección contra duplicados | 2 endpoints activos con el mismo evento; la función de Vercel no guarda `event.id` (la Pi sí: `duplicate event evt_sim_3 — skipped`) | B-B3 |
| B4 | El webhook de la Pi **acepta eventos sin firma** desde internet | con secreto presente y sin cabecera `stripe-signature` creó el cliente y devolvió 200 (simulado en `/tmp/auditB`) | B-B4 |

**Consecuencia hoy:** quien cancele sigue con servicio para siempre; quien suba a 79 € paga y no recibe las funciones; quien deje de pagar no lo detecta nadie.
**Requisito de Ricardo (3-sep):** el alta tiene que ser **automática**. Nada de altas manuales.

---

## GRUPO 3 — El portal del cliente (4 bloqueantes)

| Id | Síntoma | Evidencia | Informe |
|---|---|---|---|
| D1 | Enlace caducado → **500 y cliente encerrado**, sin forma de pedir otro | `curl` con cookie inválida → `HTTP 500 · 0 bytes`; `/login` redirige al panel → 500. Bucle | D-B1 |
| D2 | Al cliente de **79 € el portal le dice 749 €/mes** y le ofrece 3 planes retirados | probado creando un cliente `equipo` y abriendo su portal (captura) | D-B3 · E-MEDIA-2 |
| D3 | **"+ Nueva cita" nunca funciona**: 500 siempre | el portal manda la hora sin zona horaria; `booking-engine.js:31` la exige. **Poner una "Z" es un arreglo incorrecto**: desplazaría 2 h en verano | D-B4 |
| D4 | `/demo` no tiene aviso de cookies → **Meta y GA4 no se activan nunca** y el píxel de OpenAI carga sin permiso | 0 elementos de consentimiento en `/demo`, frente a `div#nx-cookie-banner` en portada y hasta en la 404 | E-BLOQ-2 |

**D4 tiene la misma causa que el fallo de los píxeles de esta mañana:** `/demo` no usa el `Layout` compartido. Se puso el bloque de medición, pero quedó detrás de un aviso que en esa página no existe.

---

## GRUPO 4 — Lara (2 bloqueantes abiertos)

| Id | Síntoma | Evidencia | Informe |
|---|---|---|---|
| C1 | **Telegram corta las respuestas a la mitad** y puede perder la reserva | límite de 150 frente a 450 en WhatsApp; salida real cortada en `"...hasta 18:30 ("`. La orden de reservar va al final: si el corte cae ahí, no hay cita | C-B2 |
| C2 | El canal **WhatsApp por Twilio no reserva nada** y escupe el token interno | `parseActions = undefined` comprobado ejecutando: `bot-prompt.js` no exporta esas funciones | C-B3 |

---

## GRUPO 5 — Operación: no hay red de seguridad (3 bloqueantes)

| Id | Síntoma | Evidencia | Informe |
|---|---|---|---|
| H1 | **Si la API se cae, nadie se entera** | A lo dejó condicionado a comprobar Uptime Kuma; **H lo comprobó: 5 monitores y ninguno sobre `nexux.pro`** | A-B1 **confirmado por** H |
| H2 | **Ninguna copia de los datos de clientas fuera de casa** | Duplicati apunta a `/home/nexux/Backend`, borrado. 56 errores desde el 4-ago. Última copia válida a Drive: **9-may-2026** | H-B1 |
| H3 | El disco USB es punto único de fallo y **ya falló dos veces** este verano | 22-26 jul y 24-28 ago; 1.039 fallos del vigilante. Se van a la vez las copias, los 8 contenedores y Uptime Kuma | H-B2 |

**Lo que sí está probado:** las copias que existen **se restauran de verdad** (`md5sum` idéntico en `appointments.json` y `config.json`) y la Pi vuelve sola tras un corte (verificado en el arranque real de esta madrugada).

---

## RESUELTOS HOY (verificados en producción)

| Id | Qué era | Cómo se cerró |
|---|---|---|
| G-B1 | Panel de administración abierto a internet con clave escrita en el código | `adminAutorizado()` con comparación en tiempo constante + clave aleatoria. Verificado: clave vieja/ausente/errónea → 401, clave nueva → 200, en las 5 rutas `/admin/*`. Commit `abd1c26` |
| C-B1 | El enlace de dueño de Telegram era el id público del salón — y el `clientId` llegaba a `fs.writeFileSync`, o sea **escritura arbitraria de ficheros** desde Telegram | enlace `o_<token>` derivado del `accessToken`; id a secas → clienta; validación del id; no se sustituye a un dueño ya vinculado. 19 pruebas + sabotaje. Revisión adversarial previa. Commit `efd9797` |

---

## CHOQUES ENTRE INFORMES (no se tapan: se resuelven con evidencia)

1. **Prueba gratuita de 7 días.** B: la web la promete y Stripe cobra el día 1. E: buscó en las 14 páginas servidas y **no encuentra la promesa**; `llms.txt` dice explícitamente que no hay prueba. **Firme:** Stripe no tiene trial (`trial_period_days: null` en ambos precios). **Sin resolver:** dónde se promete. E solo desmiente la web pública; faltan correos, Lara, el panel y los textos de Stripe. → PENDIENTE DE COMPROBAR.
2. **El bot de Telegram.** G lo dio por seguro citando una comprobación de identidad. C demostró que esa comprobación es del bot **de administración**, no del de clientes: dos funciones distintas en el mismo fichero. → **Gana C.** Misma trampa de "el fichero equivocado".
3. **Logs de cron.** Otro auditor: no existen `/var/log/syslog*` ni `cron*`. H lo confirma **y matiza**: `journalctl -u cron` sí registra, dentro del arranque actual; el agujero es la persistencia (`Storage=volatile`). → **Gana el matiz de H.**
4. **Los 4 reinicios de `nexux-clients`.** H revisó el log de errores: ninguna traza de caída. → **No son inestabilidad**, son los dos parches de seguridad de hoy.

---

## FUERA DE LA TABLA PERO URGENTE

- **Fecha límite lunes 7-sep:** `D:\nexux-backup-pi\pi-sistema-20260824.tar.gz` es la **única copia de sistema utilizable fuera de la Pi** (1.296.576 ficheros, listada sin errores) y la rotación (`Conservar=2`) la borrará. Renombrarla: 2 minutos.
- **G-A2 — secretos ya publicados en GitHub:** `origin/master` de `/home/nexux` **ya contiene** `nexux_code/.env.local` con **21 valores** (GITHUB_TOKEN, TELEGRAM_BOT_TOKEN, WP_APP_PASSWORD, claves de LLM). Verificado en solo lectura. Además hay 92 commits sin subir que llevan `.ssh/authorized_keys` y `.claude/.credentials.json`: un push accidental sube las claves SSH. Rotar + blindar con un hook `pre-push`.
- **Bomba con temporizador:** `CalculadoraCitas.astro` lleva 249/449/749 € y un botón de "prueba gratis". Hoy no se sirve; basta un artículo del blog que la use. 15 min borrarlo.
- **La atribución del QR está mal:** `/demo` adivina el origen sin leer las UTM. 6 de las últimas 8 visitas con `utm_source=octavilla` están guardadas como "directo". El dato bruto se rescata de `url_query`. 30 min.
