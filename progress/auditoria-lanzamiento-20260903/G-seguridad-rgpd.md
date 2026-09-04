# ÁREA G — Seguridad y Protección de Datos · nexux.pro
Auditoría de lanzamiento · 2026-09-03 · defensiva, autorizada por el propietario.
Toda afirmación de este informe está comprobada en esta sesión contra la Pi/producción real. Lo no comprobable se marca NO VERIFICADO.

## 1. Veredicto (3 líneas)
**NO — no lanzar sin corregir lo Bloqueante.** Hay una puerta de administración abierta a todo internet con una clave escrita en el código (`noa-validate-2026`): cualquiera puede controlar el motor de captación y **enviar WhatsApp en nombre del negocio**. Además faltan cimientos de seguridad web (sin rate-limit ni helmet), el login SSH admite contraseña, y como encargado de datos de los negocios se envían conversaciones de clientes finales a IAs en China/EEUU sin declararlo (RGPD). Lo bueno: autenticación entre clientes sólida, XSS bien escapado, OAuth firmado y con permisos mínimos, y ningún secreto en el historial de los repos de producto.

## 2. Tabla de comprobaciones
| Qué | Cómo | Resultado | Evidencia |
|---|---|---|---|
| Secretos en historial git (clientes) | `git log -p --all` + grep patrones | OK | 0 hits de sk_live/whsec/nvapi/AIza/GOCSPX/xkeysib en 41 commits |
| Secretos en historial git (pro) | idem | OK | 0 hits en 302 commits |
| accessToken hardcodeado en código | grep patrón | OK | 1 hit = `const accessToken = generateAccessToken()` (no es valor) |
| .gitignore ambos repos | `cat` | OK | clients/, .env, **/auth/, *.jsonl, .wwebjs_auth excluidos correctamente |
| Permisos .env | `stat -c '%a'` | OK | `600 nexux:nexux` en ~/.env y ~/nexux-clients/.env |
| Permisos datos cliente | `stat` clients/*/ | **FALLO** | dir clients 775; config.json 9×664+9×644; un auth/ 775; un creds.json 644 |
| google-oauth.json permisos | `stat` | OK | 600 (único existente) |
| Repos privados/públicos | GitHub API HTTP code | PARCIAL | clients-core 404, home-repo 404 (privados); **nexux-pro 200 = PÚBLICO** (sin secretos, OK) |
| /home/nexux landmine | `git ls-files` (solo lectura) | **FALLO** | .ssh/authorized_keys, .claude/.credentials.json, .gemini/oauth_creds.json trackeados; 92 commits sin push |
| Secretos ya en origin/master de /home | `git show origin/master:...` | **FALLO** | nexux_code/.env.local con 21 valores (GITHUB_TOKEN, TELEGRAM_BOT_TOKEN, WP_APP_PASSWORD, claves LLM) |
| Auth cruzada entre clientes | curl vivo token B → cliente A | OK | 401. token A → customers de B = 401 |
| Sin token → recurso privado | curl vivo | OK | 401 |
| /api/brain?key=malo | curl vivo | OK | 401 |
| **/admin/* clave por defecto** | curl vivo `?key=noa-validate-2026` | **FALLO BLOQUEANTE** | `/admin/outreach` → **200** desde internet; ADMIN_KEY no definida en .env ni en el proceso |
| Path traversal clientId | curl vivo `..%2F`, `../`, `%2e%2e` | OK | 400/404/401; escape de clients/ bloqueado por Express+token |
| clientId validado por regex | lectura código | PARCIAL | `validClientId` solo en appointment-store.js; middleware general no valida formato |
| Límite tamaño body | curl 1MB → /demo/chat | OK | 413 (límite 64kb) |
| helmet / rate-limit | grep deps y código | **FALLO** | no instalados ni usados en ningún fichero |
| Cabeceras seguridad API Pi | `curl -sI` | **FALLO** | `x-powered-by: Express`; sin HSTS/CSP/X-Frame propias (solo las de Cloudflare) |
| Cabeceras web nexux.pro | `curl -sI` | OK | HSTS, X-Content-Type, X-Frame SAMEORIGIN, Permissions-Policy (middleware.ts) |
| XSS en portal CRM | grep innerHTML + lectura render | OK | todo dato de usuario pasa por `esc()` (textContent); citas/clientes/servicios escapados |
| XSS en chat/inbox | lectura `fmt()`/`esc()` | OK | `fmt()` llama `esc()` antes de formatear WhatsApp |
| IDOR portal-api por clientId query | lectura + curl vivo | OK | no valida contra cookie, pero backend liga token↔clientId (401 verificado) |
| Cookie sesión | middleware.ts | OK | httpOnly + Secure + SameSite=lax |
| OAuth state | lectura google-oauth.js | OK | HMAC-SHA256 con SECRET + `timingSafeEqual` |
| OAuth scopes | lectura | OK | `calendar.events` + `calendar.calendarlist.readonly` (mínimos) |
| Telegram bot admin | lectura telegram.js + prueba lógica | OK | `ctx.chat.id === ADMIN_CHAT` en cada handler; bot público responde "Este bot es privado" |
| SSH config | `sshd -T` | **FALLO** | `passwordauthentication yes` (root off, pubkey on, puerto 2222) |
| authorized_keys | conteo | OK | 3 claves (nexux/Nexux-DESKTOP, ricky@nexux-scraper) |
| Firewall ufw | `ufw status` | PARCIAL | activo, pero "Anywhere" en 3389/5900/445/3456/9000/9090/5678… (LAN; internet depende del router) |
| Umami expuesto a internet | curl vivo | **FALLO** | `umami.nexux.pro` → 200; `nexux.pro/stats` → 200 |
| Teléfonos en logs PM2 | grep patrón +34 | **FALLO** | 32 teléfonos únicos, 600 ocurrencias en claro |
| IP en demo-track | lectura código | **FALLO** | IP completa (dato personal) guardada indefinidamente + enviada a ip-api.com (http, tercero) |
| Datos a LLMs (RGPD) | lectura ai.js + bot-prompt.js | **FALLO** | nombre+mensajes de cliente final a Qwen/DeepSeek (China), Groq/SambaNova/Together/Gemini (EEUU) |
| Política privacidad | lectura privacidad.astro | **FALLO** | no declara subencargados LLM, ni rol de encargado, ni transferencias internacionales |
| Dependencias | `pnpm audit --prod` | PARCIAL | 13 high, 17 moderate, 1 low (mayoría DoS transitivo vía baileys 6.7.16) |
| Node / OS | `node -v`, os-release, apt | PARCIAL | Node 22.22.2 OK; Debian 13; **427 paquetes actualizables** |
| Cifrado backups | búsqueda .gpg/.enc/scripts | NO VERIFICADO | no hallado cifrado; no accedo a D: |

## 3. Hallazgos por severidad

### BLOQUEANTE
**G-B1 · Panel de administración abierto a internet con clave por defecto en el código.**
- Causa: `provision-http.js:2194,2201,2212,2232` — las rutas `/admin/validate-leads`, `/admin/lidtest`, `/admin/reply`, `/admin/outreach` usan `req.query.key !== (process.env.ADMIN_KEY || 'noa-validate-2026')`. `ADMIN_KEY` **no está definida** en `~/nexux-clients/.env`, en `~/.env`, ni en el entorno del proceso PM2 (verificado: `grep -c '^ADMIN_KEY=' = 0`, environ del pid = 0). Se aplica la clave por defecto escrita en el fuente.
- Reproducción no destructiva: `curl -s -o /dev/null -w '%{http_code}' 'https://pi.nexux.pro/admin/outreach?key=noa-validate-2026'` → **200** (solo lectura de estado; no lancé envíos).
- Impacto: cualquiera en internet puede, con esa clave pública: parar/arrancar/disparar el motor de outreach (`/admin/outreach?action=trigger|stop|start`), **enviar WhatsApp en nombre de `nexux-empresa`** a un número arbitrario (`/admin/reply?phone=...`), enumerar si un número está en WhatsApp y resolver su LID (`/admin/lidtest`), y lanzar validación masiva de leads. Es una toma de control del canal comercial y un vector de spoofing/spam desde vuestro número.
- Propuesta (trivial): definir `ADMIN_KEY` con 32+ bytes aleatorios en `~/nexux-clients/.env` y **eliminar el literal de fallback** para que sin variable el endpoint no arranque. Diff conceptual: `const ADMIN_KEY = process.env.ADMIN_KEY; if(!ADMIN_KEY){throw...}` y `if (req.query.key !== ADMIN_KEY) return res.status(401)`. Mover además `/admin/*` detrás del mismo `SECRET` de provisión o de una IP allow-list. Mejor: no aceptar la clave por query (queda en logs), usar cabecera.
- Esfuerzo: 20 min + reinicio del servicio.

### ALTA
**G-A1 · Login SSH por contraseña habilitado.**
- Causa: `sshd -T` → `passwordauthentication yes` en puerto 2222 (alcanzable por Tailscale) y puerto 22 abierto en ufw. Root off y pubkey on, pero la contraseña abre fuerza bruta.
- Reproducción: `ssh -o ConnectTimeout=25 192.168.0.120 "sudo -n sshd -T | grep passwordauth"`.
- Impacto: superficie de fuerza bruta sobre la Pi que aloja TODOS los datos de clientes y secretos.
- Propuesta: `PasswordAuthentication no` en `/etc/ssh/sshd_config.d/` + `systemctl reload ssh`. Verificar antes que las 3 claves autorizadas funcionan.
- Esfuerzo: 10 min. (No lo aplico: modifica config.)

**G-A2 · Secretos en el repositorio del home y mina de 92 commits sin subir.**
- Causa: `/home/nexux` es un repo git que rastrea el home entero. `origin/master` **ya contiene** `nexux_code/.env.local` con 21 valores (GITHUB_TOKEN, TELEGRAM_BOT_TOKEN, WP_APP_PASSWORD, claves de varios LLM). Además el HEAD local tiene trackeados `.ssh/authorized_keys`, `.claude/.credentials.json`, `.gemini/oauth_creds.json`, `.claude-bot.env`, con **92 commits sin push**: un `git push` accidental sube claves SSH y credenciales.
- Reproducción (solo lectura): `git -C /home/nexux show origin/master:nexux_code/.env.local | grep -cE '^[A-Za-z0-9_]+=.+'` → 21; `git -C /home/nexux ls-files | grep -E '\.ssh/authorized_keys|\.credentials'`.
- Impacto: exposición de secretos si se compromete la cuenta de GitHub; riesgo catastrófico si se ejecuta el push prohibido.
- Propuesta: rotar los 21 secretos de `.env.local`, purgarlo de la historia del remoto (o hacer el repo del home inaccesible/archivado), y a corto plazo blindar el push (hook `pre-push` que aborte en `/home/nexux`). NO ejecutar pull/rebase/push ahí (landmine conocido). 
- Esfuerzo: 1-2 h (rotación + limpieza).

**G-A3 · RGPD: subencargados de IA no declarados y transferencias internacionales.**
- Causa: `lib/ai.js:16-32` enruta cada conversación a un pool de LLMs: Qwen/DashScope (Alibaba, **China**) es el primero, DeepSeek (**China**), Groq/SambaNova/Together/GitHub-Azure/Gemini/Mistral (EEUU/UE). `lib/bot-prompt.js:105` inyecta el nombre del cliente final y sus mensajes (que incluyen teléfono y datos de la reserva) en el prompt. `privacidad.astro` solo declara Stripe/Brevo/Vercel/Google/Meta para los leads propios; no menciona los LLM, ni el rol de Nexux como **encargado** del negocio, ni transferencias fuera de la UE, ni WhatsApp.
- Reproducción: lectura de los tres ficheros (evidencia en tabla).
- Impacto: incumplimiento RGPD como encargado del tratamiento: subencargados sin contrato/aviso (art. 28) y transferencias internacionales sin garantía declarada (cap. V). Riesgo reputacional y sancionador.
- Propuesta: (a) contrato de encargo con cada negocio que autorice subencargados; (b) listar los subencargados y su país en la política; (c) preferir proveedores UE o con SCC para el bot de producción, o minimizar el dato (no mandar teléfono al prompt). El prompt ya trae anti-inyección fuerte (regla 0), eso se conserva.
- Esfuerzo: legal + 1 día técnico para acotar proveedores.

### MEDIA
**G-M1 · API sin rate-limiting ni helmet.** `provision-http.js` no usa `express-rate-limit` ni `helmet` (grep 0). Sin límite: `/demo/chat` permite abuso y coste de LLM; `/client/:id/resend-link` permite tantear qué emails existen; `/public/:id/book` permite spam de reservas; fuerza bruta sin fricción. `x-powered-by: Express` revela stack. Propuesta: helmet global + rate-limit por IP en demo/login/resend/webhooks/públicas + `app.disable('x-powered-by')`. Esfuerzo: 2-3 h.

**G-M2 · Sin validación central de formato de `clientId`.** El traversal está contenido por efecto colateral (Express normaliza y el token gatea), no por diseño. `validClientId` (regex) existe en `appointment-store.js:29` pero no se aplica en `clientAuthMiddleware` ni en las rutas `/public`, `/qr-page`, `/inbox`. Propuesta: validar `^[a-zA-Z0-9_-]+$` al entrar en el middleware y devolver 400. Esfuerzo: 30 min.

**G-M3 · Datos personales en logs y en tracking de demo.** 32 teléfonos (600 apariciones) en `~/.pm2/logs/*.log` en claro, sin plazo de borrado. `/demo/track` y `/demo/chat` guardan la **IP completa** (dato personal) en `demo-visitors.jsonl` de forma indefinida y la mandan a `ip-api.com` por **http** (tercero, sin cifrado, `provision-http.js:1971`). Propuesta: enmascarar teléfonos en logs, rotación+retención corta, anonimizar/truncar IP (último octeto) y geolocalizar sin enviar la IP entera o usar proveedor propio. Esfuerzo: medio día.

**G-M4 · Umami expuesto a internet.** `umami.nexux.pro` → 200 y `nexux.pro/stats` → 200: el túnel de Cloudflare publica más que `pi.nexux.pro`. El panel de analítica queda con su login expuesto a fuerza bruta y confirma superficie extra. Propuesta: restringir por Cloudflare Access o quitar el hostname si no es necesario público. Esfuerzo: 1 h. (Ingress real gestionado en el dashboard de Cloudflare por token; no verificable desde la Pi.)

**G-M5 · Dependencias y SO desactualizados.** `pnpm audit --prod`: 13 high (ws, form-data CRLF, axios proxy, protobufjs, js-yaml — mayoría DoS vía `@whiskeysockets/baileys ^6.7.16`), 17 moderate. Debian con **427 paquetes actualizables**. Propuesta: subir baileys y transitivas, `apt upgrade` planificado. Esfuerzo: 1 día con pruebas (baileys es sensible).

**G-M6 · Permisos laxos en datos de cliente.** `clients/` 775, `config.json` 664/644 (contienen `accessToken` en claro), un `auth/` 775 y un `creds.json` de WhatsApp 644. Propuesta: `chmod 700` dirs y `600` los json de config/credenciales; revisar el umask del proceso que los crea. Esfuerzo: 30 min.

### BAJA
**G-Bx1 · Token por query `?t=`.** `clientAuthMiddleware` acepta `req.query.t` además de `Authorization: Bearer`. El token de acceso queda en logs de Cloudflare, referrers e historial del navegador. Además compara con `===` (no `timingSafeEqual`); con token de 64 hex el timing es inexplotable en la práctica, pero es mala forma. Propuesta: preferir cabecera; para las páginas HTML (`qr-page`,`inbox`) que necesitan el query, considerar intercambiar por cookie httpOnly como ya hace el portal.

**G-Bx2 · Token del túnel de Cloudflared visible en `pm2` args.** Cualquiera con acceso local lo lee. Propuesta: pasarlo por fichero de credenciales del túnel, no por argumento.

**G-Bx3 · portal-api sin comprobar `clientId` contra la cookie `nexux_client`.** Defendido por el binding token↔clientId del backend (401 verificado en vivo), pero falta la defensa en profundidad en el proxy. Propuesta: rechazar en el proxy si `clientId` de la query ≠ cookie `nexux_client`.

**G-Bx4 · Client secret de Google OAuth expuesto en captura (22-ago) sin regenerar.** Recomendación explícita: regenerar el client secret en Google Cloud (proyecto "Nexux Recepcionista IA") y actualizar `.env`. No lo hago yo. (No verifico valores; me apoyo en lo indicado en el briefing.)

## 4. No verificado y por qué
- **Cifrado de los backups (4 capas, incluida D: Windows):** no encontré `.gpg`/`.enc` ni scripts con `gpg/openssl enc/age`; no tengo acceso a la unidad D: ni al contenido de los backups. Si alguna capa incluye `clients/` sin cifrar, es exposición RGPD de datos personales. Pendiente de comprobar en el host Windows.
- **Ingress real de Cloudflared:** el túnel corre con token gestionado en el panel de Cloudflare (no hay `config.yml` local con reglas). Solo pude verificar por sondeo externo `pi.nexux.pro` (→3460) y `umami.nexux.pro` (200). El mapeo hostname→puerto completo no es verificable desde la Pi.
- **Exposición a internet de los puertos ufw "Anywhere" (3389 xRDP, 5900 VNC, 445/139 Samba, 3456 dashboard, 9000 Portainer, 9090 Cockpit, 5678 n8n…):** en LAN están abiertos; que lleguen desde internet depende del port-forwarding del router doméstico, que no puedo inspeccionar. Recomiendo confirmar en el router que NO hay reenvío a esos puertos.
- **Que el client secret de Google siga sin regenerar:** afirmación del briefing; no compruebo el valor.
