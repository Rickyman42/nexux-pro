# ÁREA A — ESTABILIDAD DE LA API

Auditoría de lanzamiento nexux.pro · 2026-09-03 · auditor: Claude (Opus 5)
Todo lo de aquí está medido en esta sesión contra la Pi (192.168.0.120) y contra producción. Nada heredado.

---

## 1. Resumen

**Estado:** la API no se cae sola. En los 110 días que cubre el registro de PM2 (16-may → 3-sep) hay **103 paradas del proceso y las 103 son la misma: código 0 por SIGINT, precedidas de `Stopping app:nexux-clients`**, que es la firma exacta de alguien tecleando `pm2 restart`. Cero caídas por error, cero muertes por memoria, cero `unstable_restarts`. La frase "de vez en cuando la API se reinicia" es cierta pero la causa no es la API: son los agentes que la reinician mientras desarrollan.

**Hallazgos:** 1 bloqueante · 4 altas · 5 medias · 2 bajas.

**Veredicto: SÍ CON CORRECCIONES.** El bloqueante (si la API se cae, nadie se entera) y las dos altas de código (ninguna llamada externa tiene tiempo máximo; no hay red de seguridad ante un fallo asíncrono) se arreglan en una tarde y sin tocar arquitectura. Las dos altas de máquina (la Pi a 84 °C con 64 MB de RAM libre, y un proceso vecino reiniciándose 10.300 veces al día) son las que de verdad ponen en riesgo la promesa de "Lara contesta siempre" cuando haya clientes pagando.

---

## 2. Tabla de comprobaciones

| Qué | Cómo | Resultado | Evidencia |
|---|---|---|---|
| Estado del proceso | `pm2 describe nexux-clients` | **OK** | `status online`, `restarts 2`, `unstable restarts 0`, `uptime 4h`, `fork_mode`, node `22.22.2`, script `/home/nexux/nexux-clients/index.js` |
| Arranque automático tras reinicio | `systemctl status pm2-nexux` | **OK** | `Loaded: ... enabled`, `Active: active (running) since Thu 2026-09-03 03:39:00 CEST`, `ExecStart=... pm2 resurrect (code=exited, status=0/SUCCESS)` |
| ¿Volvieron todos los procesos tras el reinicio de la Pi? | `pm2 jlist` vs `dump.pm2` | **OK** | 17 apps en el dump y 17 en vivo, misma lista y mismo orden. 14 online, 3 parados a propósito (`meta-ads-monitor`, `opencode-server`, `lead-finder`). 12 de los 14 llevan 676 min = desde el arranque |
| `max_memory_restart` | `pm2 jlist` + `dump.pm2` | **FALLO** | `maxmem=undefined` para nexux-clients. Sí lo tienen nexux-dashboard (200 MB) y telegram-claude-bot (300 MB) |
| Clasificación de los 103 reinicios | `grep 'nexux-clients:11]' ~/.pm2/pm2.log` + awk comparando cada arranque con la línea anterior | **OK** | 103 salidas, **una sola firma**: `exited with code [0] via signal [SIGINT]`, todas con `Stopping app:nexux-clients id:11` justo antes = orden humana/agente. 110 arranques; 6 sin parada previa: 16-may (alta inicial), 31-jul ×2, 13-ago, 28-ago, y 3-sep 03:38:58 (`pm2 resurrect` del reinicio) |
| Reinicios por día, últimos 14 días | mismo grep, contando por fecha | **OK** | 21-ago ~10 · 22-ago ~12 · 23-ago ~10 · 24-ago ~2 · 25-ago 1 · 28-ago 1 arranque · **26, 27, 29, 30, 31-ago y 1-sep: CERO** · 2-sep ~7 · 3-sep 2 + el resurrect. Los días sin agentes tocando, el servicio aguanta 5 días seguidos sin moverse |
| Caídas por memoria / OOM del servicio | `dmesg -T \| grep -i oom` | **OK (ninguna)** | Sin salida. Ni `oom-kill` ni `Killed process` |
| Caídas por reinicio de la Pi | `who -b`, `journalctl --list-boots`, `utmpdump /var/log/wtmp` | **PARCIAL** | `who -b` → `system boot 2026-09-03 03:34`. Solo hay 1 arranque en el journal (ver §4) |
| Errores recurrentes en el log de error | agrupación por firma sobre `nexux-clients-error.log` | **FALLO (3 firmas activas)** | 70× `send error Cannot read properties of undefined (reading 'replace')` · 42× `... (reading 'id')` · 35× `ENOENT ... /auth/creds.json`. Todas de la capa WhatsApp, ninguna mata el proceso |
| `uncaughtException` / `unhandledRejection` | `grep -rn "process.on(" index.js provision-http.js lib/` | **FALLO** | Solo 2 resultados: `index.js:76` SIGTERM y `index.js:80` SIGINT. **No existe ningún manejador global de errores** |
| try/catch en endpoints | awk sobre `provision-http.js` | **FALLO** | 60 rutas, 39 `async`. **8 rutas async sin `try` en su cabecera**: líneas 224, 496, 583, 655, 710, 1808, 2139, 2248. Además **no hay middleware de error** (`app.use((err, req, res, next)` → 0 resultados) |
| Timeouts en llamadas externas | `grep -n 'AbortSignal.timeout\|AbortController\|signal:' provision-http.js lib/*.js` | **FALLO** | **Cero resultados** sobre 26 puntos de llamada `fetch` repartidos en 12 ficheros. Ni LLM, ni Stripe, ni Google, ni Brevo, ni Telegram, ni Twilio |
| Timeouts del servidor HTTP | `grep server.timeout\|requestTimeout\|keepAliveTimeout` | **FALLO** | Cero. `provision-http.js:2240` es un `app.listen(PORT, '0.0.0.0', ...)` pelado |
| Memoria (medición 1) | `pm2 jlist` 14:54 | **OK** | 178 MB |
| Memoria (medición 2) | `/proc/<pid>/status` 15:02 | **OK** | `VmRSS: 183664 kB`, fds 28, hilos 11 |
| Memoria (medición 3, +15 min) | `/proc/<pid>/status` + `pm2 jlist` 15:09 | **OK** | `VmRSS: 183728 kB` (+64 kB en 7 min), pm2 `180 MB`, fds 28, sockets 10, hilos 11. **Plano, sin fuga visible en esa ventana** |
| Bucle de WhatsApp — cliente con sesión real | out.log desde la línea 14296 (`18 clients loaded, 3 active`, arranque de las 10:32) | **OK** | `estudio-ricardo-demo-mostoles-946279`: **1 `✅ connected`, 0 desconexiones** en 4h40. Su `auth/creds.json` se reescribió a las 14:52:59 → sesión viva de verdad |
| Bucle de WhatsApp — cliente sin credenciales | mismo tramo del out.log | **FALLO (parcial)** | `nexux-empresa`: **38 ciclos** `6 QR → disconnected (reason=408) → reconecta` en 4h40. Media 6,9 min por ciclo = el backoff exponencial sí llega a su tope de 300 s. No hay avalancha en Telegram (el envío de foto está desactivado), pero el ciclo no para |
| Crons y vigilantes que reinicien la API | `crontab -l`; lectura de `docker-stack-watchdog.sh`; `grep -rl 'pm2 (restart\|reload\|stop)' ~/scripts ~/nexux-clients/scripts` | **OK** | Ningún cron ni script toca `nexux-clients`. El watchdog de las 5 min solo mira el disco `/mnt/data` y Docker. Los dos únicos ficheros con `pm2 restart` son documentación (`.md`) |
| Salud pública | `curl https://pi.nexux.pro/health` ×5 | **OK** | 200 en 0,097 / 0,092 / 0,091 / 0,091 / 0,095 s. Cuerpo `{"ok":true,"ts":"2026-09-03T13:02:03.729Z"}` |
| Salud local | `curl http://localhost:3460/health` ×5 | **OK** | 200 en 0,0026 / 0,0027 / 0,0025 / 0,0030 / 0,0031 s |
| Minutos reales de caída vistos desde fuera | `grep 'connection refused' cloudflared-provision-error.log \| grep :3460` | **OK** | 71 minutos distintos en 110 días. En los últimos 14: **21-ago 2 min, 22-ago 10 min, 23-ago 3 min, 3-sep 3 min = 18 minutos**. Todos coinciden con un `pm2 restart` o con el reinicio de la Pi |
| Temperatura y throttling | `vcgencmd measure_temp` / `get_throttled` ×3 | **FALLO** | 76,4 °C → 82,7 °C → **84,2 °C**. `throttled=0xe0000` = bits 17/18/19: *ha habido* limitación de frecuencia y se ha pasado el límite blando de temperatura. **El bit 16 (bajada de tensión) NO está**: es calor, no la fuente |
| RAM y disco del sistema | `free -h`, `df -h`, `top` | **FALLO** | 3,7 GB totales, **64 MiB libres**, **1.358 MB de swap en uso** de 2.048, `kcompactd` al 26,7 % de CPU y 20,5 % de espera de disco. Disco raíz **90 G de 117 G = 80 %** |
| Rotación de logs | `pm2 ls` (módulos), `ls /etc/logrotate.d/` | **FALLO** | Ni módulo `pm2-logrotate` ni entrada de logrotate del sistema. `~/.pm2/logs` = 122 MB, `pm2.log` = 47 MB |
| Alarma si la API se cae | lectura de `~/scripts/nexux-vigila-whatsapp.py`; `crontab -l \| grep health` | **FALLO** | La función `conectado()` devuelve `None` cuando no puede llegar a `localhost:3460`, y el bucle hace `if ok is None: continue  # no se cuenta como caida`. `nexux-health-check.js` existe pero **no está en cron** (0 coincidencias) |
| Verificador de la casa | `python3 ~/scripts/nexux-verify.py service:nexux-clients url:https://pi.nexux.pro/health` | **OK** | `OK service:nexux-clients -> estado=online` · `OK url:... -> HTTP 200` · `VEREDICTO: 2/2 OK` |

---

## 3. Hallazgos

### BLOQUEANTE

#### B-1 · Si la API se cae, no se entera nadie

**Síntoma.** No existe ninguna alarma que vigile que `nexux-clients` está vivo y respondiendo.

**Causa raíz con evidencia.** Hay dos candidatos y ninguno sirve:

1. `~/scripts/nexux-vigila-whatsapp.py` (cron cada 10 min) vigila el WhatsApp de cada cliente preguntándole **a la propia API**:
   ```python
   def conectado(client_id, token):
       """True/False segun el estado REAL del socket; None si no se puede comprobar."""
       try:
           with urllib.request.urlopen(url, timeout=15) as r: ...
       except Exception:
           return None
   ...
       ok = conectado(cid, token)
       if ok is None:
           continue                      # no se pudo comprobar: no se cuenta como caida
   ```
   Es decir: **el único caso que garantiza que todos los clientes están mudos —la API caída— es exactamente el que el vigilante decide ignorar.** El vigilante vive dentro de lo que vigila, que es el error que el propio `docker-stack-watchdog.sh` documenta en su cabecera para no repetirlo.
2. `~/nexux-health-check.js` existe (14 KB, 26-jul) pero `crontab -l | grep -c health` → **0**. No se ejecuta.

Uptime-kuma está levantado (`docker ps` → `uptime-kuma Up 11 hours (healthy)`) pero **no he podido verificar** si tiene un monitor sobre `pi.nexux.pro/health` (requiere entrar a la interfaz, ver §4).

**Reproducción.** `crontab -l | grep health` → vacío. Y en el código: si `urlopen` a `localhost:3460` lanza excepción, el cliente se salta sin contar fallo.

**Impacto en el lanzamiento.** Con clientes pagando 29 y 79 €/mes, el modo de fallo es: la API se para un domingo, Lara deja de contestar en todos los WhatsApp a la vez, y el primero en enterarse es un cliente que llama enfadado. No hay ninguna línea de defensa entre esas dos cosas.

**Propuesta.** Dos cosas, en este orden:
1. Monitor en uptime-kuma (ya está corriendo, coste cero): HTTP `https://pi.nexux.pro/health`, cada 60 s, 2 fallos seguidos, aviso a Telegram. Es lo que da cobertura también si se cae el túnel o la Pi entera.
2. Arreglar el vigilante para que el caso "no contesta la API" sea una alarma propia, no un `continue`:
   ```python
   # antes del bucle de clientes
   try:
       urllib.request.urlopen(API + "/health", timeout=10)
   except Exception:
       avisa("🔴 *API caída* — pi.nexux.pro no responde. NINGÚN cliente está siendo atendido.")
       return
   ```
**Esfuerzo:** 30 min el monitor, 20 min el parche del vigilante.

---

### ALTA

#### A-1 · Ninguna llamada a un proveedor externo tiene tiempo máximo, y el LLM encadena 10 en serie

**Síntoma.** Un proveedor lento o colgado deja la respuesta de Lara esperando, sin techo.

**Causa raíz con evidencia.** `grep -n 'AbortSignal.timeout\|AbortController\|signal:' provision-http.js lib/*.js` → **cero resultados**, sobre 26 puntos de llamada `fetch` en 12 ficheros. El caso peor está en `~/nexux-clients/lib/ai.js`:

```js
// lib/ai.js:43
async function callProvider(provider, systemPrompt, messages, maxTokens, temperature = 0.7) {
  const key = provider.key();
  if (!key) throw new Error('no key');
  const res = await fetch(provider.url, { method: 'POST', headers: {...}, body: ... });   // sin signal
```
```js
// lib/ai.js:56
export async function chat(systemPrompt, messages, maxTokens = 450, opts = {}) {
  for (const provider of providers) {           // PROVIDERS = 10 proveedores
    try { return await callProvider(...); }
    catch (err) { console.warn('[ai] ' + provider.name + ' failed:', err.message); }
  }
  throw new Error('[ai] All providers exhausted');
}
```
`PROVIDERS` (líneas 16-25) son 10: qwen-plus, qwen-turbo, qwen-max, cerebras-1, cerebras-2, groq, sambanova, together, mistral, github-gpt4o. Se prueban **uno detrás de otro**. El `fetch` de Node 22 no tiene tiempo total: `headersTimeout` y `bodyTimeout` valen 300 s por defecto. Cuenta redonda: **10 × 300 s = 50 minutos** hasta que `chat()` se rinde. Durante ese rato el cliente que escribió por WhatsApp no recibe nada, y el `await` mantiene ocupada su rama de ejecución.

Y tampoco hay techo por el otro lado: `provision-http.js:2240` es `app.listen(PORT, '0.0.0.0', ...)` sin `server.requestTimeout` ni `keepAliveTimeout`, así que la petición HTTP tampoco se corta sola.

**Reproducción.** No la he provocado (implicaría cortar tráfico saliente en producción). Es lectura de código, verificable con `grep`.

**Impacto en el lanzamiento.** Con 1 cliente es una respuesta que tarda. Con 100 clientes y una caída de Qwen —el primer proveedor de la lista, el que se lleva todo el tráfico— son 100 conversaciones congeladas a la vez, 100 sockets abiertos y una Pi con 64 MB libres. Es el escenario que sí puede tumbar el proceso.

**Propuesta (trivial, 2 líneas):**
```diff
--- a/lib/ai.js
+++ b/lib/ai.js
@@
-  const res = await fetch(provider.url, {
-    method: 'POST',
-    headers: { Authorization: 'Bearer ' + key, 'Content-Type': 'application/json' },
+  const res = await fetch(provider.url, {
+    signal: AbortSignal.timeout(20000),   // 20 s por proveedor: 10 proveedores = 200 s de techo real
+    method: 'POST',
+    headers: { Authorization: 'Bearer ' + key, 'Content-Type': 'application/json' },
```
Y el mismo `signal: AbortSignal.timeout(...)` en los otros 25 puntos de `fetch` (10 s para Telegram/Brevo, 15 s para Stripe/Google). Más, en `provision-http.js:2240`:
```js
const server = app.listen(PORT, '0.0.0.0', ...);
server.requestTimeout = 30000;
server.headersTimeout = 35000;
```
**Esfuerzo:** 2 h incluyendo repasar los 26 puntos uno a uno.

---

#### A-2 · No hay red de seguridad: un fallo asíncrono suelto mata el proceso entero

**Síntoma.** Ninguno todavía — y eso es lo que lo hace peligroso: es la bomba que no ha explotado.

**Causa raíz con evidencia.** Tres piezas que encajan mal:
1. `grep -rn "process.on(" index.js provision-http.js lib/` devuelve **exactamente dos líneas**: `index.js:76` (SIGTERM) e `index.js:80` (SIGINT). No hay `uncaughtException` ni `unhandledRejection`. En Node 22 una promesa rechazada sin capturar **mata el proceso** (es el comportamiento por defecto desde Node 15).
2. Express **4.22.2** (comprobado en `node_modules/express/package.json`). Express 4 **no** captura los rechazos de un manejador `async`: se escapan al proceso. Express 5 sí lo haría.
3. 8 de las 39 rutas `async` no abren `try` en su cabecera: `provision-http.js` líneas **224** (`/provision`), **496** (`/client/:clientId/status`), **583** (`/client/:clientId/wa-qr`), **655** (`/client/:clientId/resend-link`), **710** (`/webhook/twilio-wa/:clientId`), **1808** (`/demo/chat`), **2139** (`/mailbox/send`), **2248** (`/client/:clientId/missed-call`). Y no existe middleware de error: `grep 'err, req, res, next'` → 0.

Revisadas de cerca, el código anterior al `try` de esas rutas es casi todo síncrono y de bajo riesgo (en `/demo/chat` la llamada al modelo sí está protegida; en `/client/:clientId/wa-qr` quedan fuera un `fs.existsSync` y un `fs.readdirSync`). O sea: hoy la probabilidad es baja. Pero el coste cuando pase es el proceso entero, y no hay nada que lo amortigüe.

**Impacto en el lanzamiento.** Es la diferencia entre "una petición devuelve error 500" y "todos los clientes se quedan mudos". Además se junta con B-1: si pasa, nadie avisa.

**Propuesta.** Al final de `index.js`:
```js
process.on('unhandledRejection', (e) => {
  console.error('[nexux-clients] promesa sin capturar:', e);   // se registra, NO se mata el proceso
});
process.on('uncaughtException', (e) => {
  console.error('[nexux-clients] excepción sin capturar:', e);
});
```
Y un middleware de error al final de `provision-http.js`, después de la última ruta:
```js
app.use((err, _req, res, _next) => {
  console.error('[http] error no capturado:', err);
  if (!res.headersSent) res.status(500).json({ error: 'internal' });
});
```
Nota honesta: con Express 4 ese middleware **no** recoge los rechazos de un `async` sin `try`. Para eso hay que envolver esas 8 rutas (o subir a Express 5, que ya no es un cambio de tarde). Lo mínimo viable para lanzar es el `unhandledRejection`, que convierte "el proceso muere" en "queda una línea en el log".
**Esfuerzo:** 20 min lo mínimo; 3 h envolver las 8 rutas y probarlas.

---

#### A-3 · `nexux-blog-autopilot` se reinicia unas 10.300 veces al día desde el 28-ago, en la misma Pi

**Síntoma.** Un proceso vecino consume CPU, RAM y disco sin parar, 24 h al día, sin producir nada.

**Causa raíz con evidencia.**
```
$ grep 'nexux-blog-autopilot:1] online' ~/.pm2/pm2.log | awk -F'T' '{print $1}' | sort | uniq -c
      1 2026-08-13
   6331 2026-08-28
  10340 2026-08-29
  10259 2026-08-30
  10279 2026-08-31
  10297 2026-09-01
  10270 2026-09-02
   6207 2026-09-03      (a media tarde)
```
`pm2 jlist` en vivo: `nexux-blog-autopilot ... restarts=4830 ... uptime_min=0`. El ciclo dura ~8,4 s. El motivo está en su propio log:
```
[2026-09-03T13:03:47.087Z] [INFO] Starting Nexux Blog Autopilot scheduler...
[2026-09-03T13:03:47.096Z] [WARN] [Scheduler] "Alternativas a Tinder España" PAUSADA (enabled:false) — no se agenda
[... los 4 temas, todos PAUSADA ...]
[2026-09-03T13:03:47.099Z] [INFO] Scheduler running.
```
Los cuatro temas están en `enabled:false`, así que no se registra **ningún** temporizador, el bucle de eventos se queda vacío, Node sale limpiamente con código 0 y PM2 lo levanta otra vez. Como vive más de 1 s, PM2 no lo marca inestable (`unstable_restarts=0`) y no se rinde nunca. Lleva **7 días** así.

Coste medido: cada arranque es un proceso Node de ~57 MB, y ha escrito **36 MB** de `nexux-blog-autopilot-out.log`.

**Impacto en el lanzamiento.** No toca el código de la API, pero le quita a la API justo lo que le falta: memoria (quedan 64 MiB libres y 1,3 GB de swap en uso), CPU y ciclos de disco. Es combustible directo de A-4, y es sospechoso número uno del reinicio de esta madrugada.

**Propuesta.** `pm2 stop nexux-blog-autopilot && pm2 save`. El proceso no publica nada: todos sus temas están apagados. Cuando se quiera reactivar el blog, antes hay que arreglar que el planificador no salga cuando no hay nada que planificar (un `setInterval` de guardia). **No lo he ejecutado**: parar procesos está fuera de mi permiso. Lo pido explícitamente.
**Esfuerzo:** 1 min pararlo. 30 min el arreglo de fondo.

---

#### A-4 · La Pi está a 84 °C, ya ha limitado frecuencia, y le quedan 64 MB de RAM libre

**Síntoma.** La máquina que sostiene toda la promesa del producto está al límite térmico y de memoria.

**Causa raíz con evidencia.** Tres medidas mías, separadas, subiendo:
```
14:54  temp=76.4'C
15:04  temp=82.7'C   load average: 6.21
15:09  temp=84.2'C
       throttled=0xe0000
```
`0xe0000` son los bits 17, 18 y 19: **ha habido** limitación de frecuencia del procesador, **ha habido** throttling y **se ha superado el límite blando de temperatura** (80 °C) desde el arranque de hace 11 h. El bit 16 (bajada de tensión) **no** está encendido: **no es la fuente de alimentación, es calor**.

Memoria, a las 15:04:
```
MiB Mem :   3796.7 total,     82.2 free,   2339.5 used,   1556.1 buff/cache
MiB Swap:   2048.0 total,    690.0 free,   1358.0 used
%Cpu(s): 10.7 us, 16.1 sy, 52.7 id, 20.5 wa
    49 root  ...  R  26.7  0.0   0:20.03 kcompactd0
```
`kcompactd0` al 26,7 % de CPU es el núcleo desfragmentando memoria a la desesperada, y un 20,5 % de espera de disco es swap moviéndose. Eso es una máquina sin RAM, no una máquina ocupada.

Advertencia de honestidad: parte del pico de carga de las 15:04 lo provoqué yo (un `du -sh` mío aparecía en el `top`). El calor y la swap, no.

**Impacto en el lanzamiento.** Ricardo cuenta que la Pi se reinició sola a las 03:37 por un `pnpm build`. No puedo confirmar esa causa concreta (§4), pero sí puedo confirmar el terreno: **una máquina con 64 MB libres y 1,3 GB de swap se reinicia sola cada vez que algo pide medio giga de golpe.** Con 100 clientes esa presión sube, no baja.

**Propuesta.**
1. Quitar peso ya: A-3 (blog-autopilot) y revisar si `aeo-auditor` con su Chromium (205 MB en `top`) tiene que estar levantado 24 h.
2. Poner `max_memory_restart: '400M'` a `nexux-clients` (ver M-1): un reinicio controlado de 3 s es infinitamente mejor que un cuelgue de la Pi entera.
3. Refrigeración: 84 °C con carga normal es un ventilador que falta o un disipador sucio. Es la única acción física, y es barata.
4. Decisión de fondo, que no es mía: **una Pi de 3,7 GB compartida con 16 procesos no es el sitio donde alojar el SaaS por el que se cobra**. Para 100 clientes hace falta que nexux-clients viva solo. Eso es materia del área de arquitectura, lo dejo apuntado.
**Esfuerzo:** 1 h los puntos 1-2. El 4 es una decisión de Ricardo.

---

### MEDIA

#### M-1 · `nexux-clients` no tiene `max_memory_restart`

`pm2 jlist` → `maxmem=undefined`. Lo tienen configurado `nexux-dashboard` (200 MB) y `telegram-claude-bot` (300 MB), pero no la API, que es el proceso más importante de la Pi. Hoy consume 180 MB estables, así que no molesta; el día que una fuga la lleve a 1,5 GB en una máquina con 64 MB libres, se lleva la Pi por delante en vez de reiniciarse ella sola.
**Propuesta:** `max_memory_restart: '400M'` (más del doble de lo que gasta hoy: no salta por ruido) y `pm2 save`. **Esfuerzo:** 10 min.

#### M-2 · Los logs no rotan y el disco está al 80 %

Ni el módulo `pm2-logrotate` (no aparece en `pm2 ls`) ni entrada en `/etc/logrotate.d/` (la lista completa no menciona pm2). Resultado: `~/.pm2/logs` = **122 MB**, `~/.pm2/pm2.log` = **47 MB**, disco raíz **90 G de 117 G (80 %)**. Los mayores: `opencode-nvidia-error.log` 40 MB, `nexux-blog-autopilot-out.log` 36 MB (consecuencia de A-3), `nexux-site-error.log` 21 MB.
Ironía útil: que no roten es lo que me ha permitido reconstruir 110 días de historia. Al instalar la rotación, conservar 14 días.
**Propuesta:** `pm2 install pm2-logrotate` con `max_size 10M`, `retain 14`, `compress true`. **Esfuerzo:** 15 min.

#### M-3 · La API se reinicia porque la reiniciamos nosotros, y eso no está gobernado

Este es el hallazgo que contesta la pregunta de Ricardo. Las 103 paradas son órdenes explícitas. En `~/.bash_history` solo aparecen 2 `pm2 restart nexux-clients --update-env`: las otras ~101 llegaron por `ssh pi "pm2 restart..."` desde agentes, que no dejan rastro en el historial. Se concentran en los días de desarrollo (21, 22, 23-ago y 2, 3-sep) y desaparecen los días sin agentes (26, 27, 29, 30, 31-ago y 1-sep: cero).

Y sí tienen coste medible: en los últimos 14 días, `pi.nexux.pro` devolvió error a peticiones reales durante **18 minutos** (21-ago 2, 22-ago 10, 23-ago 3, 3-sep 3), todos dentro de ventanas de reinicio.

**Propuesta:** una regla, no código. Con clientes de pago, `pm2 restart nexux-clients` deja de ser gratis: se hace en ventana acordada, o se despliega con `pm2 reload` (recarga sin cortar) tras pasar el servicio a `cluster_mode`. Y cada reinicio se anota en `progress/REGISTRO.md`, para que dentro de un mes no haya que deducirlo de un log de 47 MB como he tenido que hacer yo. **Esfuerzo:** decisión + 1 h si se hace el paso a `cluster_mode`.

#### M-4 · Un cliente sin vincular tiene la conexión dando vueltas 24 h

`nexux-empresa` no tiene `creds.json`. Desde el arranque de las 10:32 lleva **38 ciclos** de `6 QR → disconnected (reason=408) → reconecta`. El arreglo de hoy funciona en lo que se propuso: el backoff exponencial llega a su tope de 300 s (38 ciclos en 264 min = 6,9 min de media) y los envíos de foto a Telegram están desactivados, así que no hay avalancha de avisos. La caducidad a 24 h también está bien puesta: su `wa-qr-estado.json` dice `primerQrEn: 1788396309822` = 3-sep 02:45 CEST, o sea que **se apagará solo el 4-sep a las 02:45**.

Lo que queda: durante esas 24 h el cliente mantiene un socket contra WhatsApp y escribe ~270 líneas cada 4 horas. `nexux-clients-out.log` ya va por 3,9 MB. Con 100 clientes y un 10 % sin vincular, son 10 sockets y ~10 veces ese ruido — que es exactamente lo que el comentario del código (`lib/whatsapp.js:96-99`) anticipa. Es aceptable para lanzar; no lo es a 500 clientes.
**Propuesta:** bajar `QR_VIDA_MS` de 24 h a 2 h para quien nunca vinculó (nadie tarda 24 h en escanear un QR que tiene delante) y dejar el botón de reactivar del portal, que ya existe (`reactivaWhatsApp`, `lib/whatsapp.js:129`). **Esfuerzo:** 15 min.

#### M-5 · Hay un cliente activo con el WhatsApp apagado por un QR "caducado" a los 5 minutos

`clients/nexux-demo-mostoles-42a928/wa-qr-estado.json`:
```json
{"primerQrEn": 1788396429516, "caducadoEn": 1788396728129}
```
Son las **02:47:09** y las **02:52:08** de esta madrugada: **4 minutos y 59 segundos**, no 24 horas. Su `config.json` dice `active=true` y en el log de hoy aparece `[wa:nexux-demo-mostoles-42a928] QR caducado: no se arranca hasta que lo reactiven`. O sea: un cliente marcado como activo con el WhatsApp apagado.

He revisado la lógica y **la caducidad está bien escrita**: el único sitio que pone `caducadoEn` es `lib/whatsapp.js:586`, dentro de `if (Date.now() - estadoQr.primerQrEn > QR_VIDA_MS)`, y `primerQrEn` se conserva al reescribir. Con el código actual esos 5 minutos no pueden salir. La explicación más probable es que a esa hora se estaba probando la función con un valor corto de `QR_VIDA_MS` (el commit `09e79c1` es de las 03:58, una hora después) y el fichero quedó como resto de la prueba — **hipótesis, no confirmado**. Sea resto de prueba o fallo real, el resultado en producción es el mismo y hay que resolverlo antes de lanzar.
**Propuesta:** borrar ese `wa-qr-estado.json` (o usar el botón de reactivar del portal, que hace justamente eso) y comprobar que el bot vuelve. Y añadir al panel de admin un aviso de "cliente activo con WhatsApp apagado", que hoy solo se ve rebuscando en el log. **No lo he tocado.** **Esfuerzo:** 5 min el borrado, 1 h el aviso.

---

### BAJA

#### Ba-1 · La API solo escucha en IPv4

`ss -tlnp` → `LISTEN 0.0.0.0:3460`. Prueba directa: `curl 'http://[::1]:3460/health'` → **000 (rechazado)**, mientras `curl http://127.0.0.1:3460/health` → **200**. En el log de cloudflared los 444 errores de origen nombran `dial tcp [::1]:3460`. **No es un fallo activo**: el túnel funciona (5 de 5 peticiones a `https://pi.nexux.pro/health` en 0,09 s) porque Go reintenta por IPv4, y todos los rechazos coinciden con ventanas en que el servicio estaba realmente parado. Es solo un margen que no hace falta regalar.
**Propuesta:** `app.listen(PORT, ...)` sin el `'0.0.0.0'` (Node escucha entonces en las dos familias). **Esfuerzo:** 1 min. Se puede dejar para después del lanzamiento.

#### Ba-2 · Credenciales de Twilio y el token del bot de Telegram salen en claro en `pm2 describe`

`pm2 describe nexux-clients` imprime en su bloque de configuración `TWILIO_AUTH_TOKEN`, `TWILIO_ACCOUNT_SID`, `TWILIO_API_SECRET`, `TWILIO_API_KEY` y `NEXUX_PRO_BOT_TOKEN` con su valor completo. Cualquiera con acceso a la Pi —y cualquier log donde se haya pegado esa salida— los tiene. No es del área de estabilidad; lo dejo apuntado para el área de seguridad.
**Propuesta:** que salgan del entorno de PM2 y se lean del `.env` como el resto, y rotarlos. **Esfuerzo:** 30 min + rotación.

---

## 4. No verificado, y por qué

| Qué | Por qué no |
|---|---|
| **La causa del reinicio de la Pi de las 03:37** | El journal no es persistente: `/var/log/journal` está vacío y `journalctl --list-boots` solo devuelve el arranque actual (`0 ... 2026-09-03 03:34:00`). No existen `/var/log/syslog`, `/var/log/kern.log` ni `/var/log/messages`. `last` no está instalado y `utmpdump /var/log/wtmp \| grep -i reboot` no devuelve nada. **Todo lo anterior a las 03:34 de hoy es inaccesible.** Que fuera un `pnpm build` comiéndose la RAM es plausible y encaja con el estado de memoria que sí he medido, pero **no puedo confirmarlo ni desmentirlo**. Recomendación: activar el journal persistente (`sudo mkdir -p /var/log/journal && sudo systemd-journald --flush`) hoy mismo, para que el próximo reinicio sí deje pruebas. |
| **El historial de reinicios de la Pi anterior a hoy** | Mismo motivo. No hay registro. Los 6 arranques de `nexux-clients` sin parada previa (16-may, 31-jul ×2, 13-ago, 28-ago) **podrían** ser reinicios de la Pi, pero no tengo con qué contrastarlo. Lo que sí sé es que ninguno vino precedido de una salida con error: las 103 salidas registradas son código 0 por SIGINT. |
| **La evolución de la memoria a lo largo de horas o días** | Mis tres medidas cubren 15 minutos (178 → 180 MB de PM2; `VmRSS` 183.664 → 183.728 kB). En esa ventana está plana y los descriptores no crecen (28-31 abiertos, 10-13 sockets, 11 hilos). **Una ventana de 15 min no descarta una fuga lenta.** Para descartarla haría falta muestrear cada hora durante 48 h; con `max_memory_restart` puesto (M-1) el riesgo queda acotado igualmente. |
| **Si uptime-kuma ya vigila `pi.nexux.pro`** | El contenedor está vivo (`Up 11 hours (healthy)`) y responde 302 en el puerto 3001, pero listar sus monitores exige entrar a la interfaz con credenciales. Si ya existe un monitor sobre `/health`, B-1 baja de bloqueante a media. **Hay que comprobarlo antes de dar B-1 por bueno.** |
| **Comportamiento con 100 clientes** | No he hecho prueba de carga. Habría que lanzarla contra la Pi en producción y estaba fuera de mi permiso. Todo lo que digo sobre 100 clientes es extrapolación razonada desde el código (A-1, A-2) y desde la memoria libre medida (A-4), no medición. **Antes de vender el plan a escala, hace falta una prueba de carga real en una copia.** |
| **Por qué el QR de `nexux-demo-mostoles-42a928` se marcó caducado en 5 minutos** | Ver M-5. Tengo el fichero y tengo la lógica, y no encajan. Mi explicación (resto de una prueba de esa madrugada) es **hipótesis**. Reproducirlo exigiría manipular ficheros de cliente en producción, que está prohibido en este encargo. |
| **Que ningún otro proceso de la Pi reinicie la API** | Verificado para crons (`crontab -l`, ninguno la toca) y para `~/scripts` y `~/nexux-clients/scripts` (`grep -rl 'pm2 (restart\|reload\|stop)'` solo encuentra dos ficheros `.md` de documentación). **No he barrido el resto del sistema** (`/etc/cron.d`, timers de systemd, otros repos). Dado que las 103 paradas llevan `Stopping app` con SIGINT y coinciden con días de desarrollo, no creo que quede nada, pero no lo he barrido entero. |

---

## Respuesta a la pregunta central

**¿Por qué se reinicia la API?** Porque la reiniciamos. 103 de 103 paradas registradas desde el 16 de mayo son `pm2 restart` ejecutado por un humano o un agente. Cero caídas por error de programa, cero muertes por memoria, cero abandonos de PM2. La API, cuando la dejan en paz, aguanta: del 26 de agosto al 1 de septiembre estuvo cinco días seguidos sin moverse.

**¿Con qué frecuencia real?** En los últimos 14 días: unos 10-12 reinicios en cada día de desarrollo (21, 22, 23-ago y 2, 3-sep) y **ninguno** los días en que nadie tocó el proyecto. Traducido a lo único que le importa a un cliente —minutos en que `pi.nexux.pro` no contestó a una petición real— son **18 minutos en 14 días**, todos dentro de una ventana de reinicio o del reinicio de la Pi de esta madrugada.

**¿Qué hay que cambiar para que no pase con 100 clientes?** Lo que hay que cambiar no es lo que se ha roto, es lo que no existe. Por orden:

1. **Una alarma que avise cuando la API se cae** (B-1). Hoy no la hay, y el único vigilante que existe está programado para ignorar precisamente ese caso.
2. **Un tiempo máximo en cada llamada a un proveedor externo** (A-1). Diez proveedores de IA en fila sin reloj son cincuenta minutos de cliente esperando; ahora mismo es el único camino conocido por el que la API sí se puede quedar colgada de verdad.
3. **Una red de seguridad ante fallos asíncronos** (A-2), tres líneas, para que un error suelto sea una línea de log y no el fin del servicio.
4. **Quitarle peso a la Pi** (A-3, A-4): un proceso vecino se reinicia diez mil veces al día y a la máquina le quedan 64 MB de RAM libre a 84 °C. Nada de eso es culpa del código de la API, y todo eso se la lleva por delante cuando falle.
5. **Y una decisión que no es mía:** el SaaS por el que se cobra no debería compartir 3,7 GB de RAM con dieciséis procesos más. Para 100 clientes, `nexux-clients` tiene que vivir solo.

Con los puntos 1, 2 y 3 hechos —una tarde de trabajo— se puede lanzar. El 4 es urgente pero no bloquea. El 5 hay que decidirlo antes de pasar de los primeros veinte clientes.
