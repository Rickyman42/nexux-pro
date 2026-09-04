# AREA E — WEB PUBLICA, SEO Y MEDICION
Auditoria de lanzamiento nexux.pro — 2026-09-03
Auditor: agente E (arranque en frio, todo verificado en esta sesion)
Sitio auditado: https://nexux.pro (lo desplegado manda sobre el codigo)

> Este fichero se escribe A TROZOS, cada comprobacion en cuanto termina.

## LOG DE COMPROBACIONES

### E-01 Barrido de estados HTTP de todas las paginas publicas (2026-09-03 20:35)
Comando: bucle `curl -s -o /dev/null -w '%{http_code} %{redirect_url} ttfb=%{time_starttransfer}'` sobre cada ruta.

| Ruta | Codigo | TTFB (s) | Peso HTML |
|---|---|---|---|
| / | 200 | 0,286 | 67.202 B |
| /demo | 200 | 0,237 | 32.123 B |
| /paquetes/recepcionista | 200 | 0,094 | 46.113 B |
| /paquetes/equipo | 200 | 0,101 | 45.638 B |
| /legal | 200 | 0,243 | 10.431 B |
| /privacidad | 200 | 0,228 | 11.541 B |
| /blog | 200 | 0,223 | 12.800 B |
| /blog/automatizar-reservas-whatsapp-peluqueria | 200 | 0,119 | 15.308 B |
| /blog/cuanto-cuesta-cita-perdida | 200 | 0,159 | 15.581 B |
| /blog/migrar-de-treatwell-sin-perder-clientes | 200 | 0,099 | 15.540 B |
| /blog/treatwell-vs-booksy-peluquerias | 200 | 0,103 | 15.323 B |
| /comparativa | 200 | 0,193 | 11.675 B |
| /alternativa-a-booksy | 200 | 0,215 | 22.349 B |
| /gracias | 200 | 0,204 | 12.009 B |
| /acceso-denegado | 200 | 0,206 | 8.859 B |
| /admin | 200 | 0,209 | 12.507 B |
| /llms.txt | 200 | 0,100 | 3.956 B |
| /robots.txt | 200 | 0,158 | 1.174 B |
| /sitemap-index.xml | 200 | 0,097 | 180 B |
| /sitemap-0.xml | 200 | 0,116 | 1.100 B |
| /sitemap.xml | **404** | 0,199 | — |
| /esta-pagina-no-existe-xyz | 404 (pagina 404 propia, 8.861 B) | 0,207 | — |

RESULTADO: OK. Ninguna pagina publica caida. Ningun tiempo de respuesta malo (todos por debajo de 0,3 s desde Madrid).
Matiz: /sitemap.xml da 404 — es correcto formalmente porque robots.txt declara /sitemap-index.xml, pero es la URL que la gente y algunas herramientas prueban a mano. Ver hallazgo BAJA-1.

### E-02 Redirectores de las octavillas (QR de papel)
Comando: `curl -s -o /dev/null -w '%{http_code} -> %{redirect_url}' https://nexux.pro/f/<codigo>`

| Codigo | Codigo HTTP | Destino |
|---|---|---|
| /f/d1 | 302 | /demo?utm_source=octavilla&utm_medium=papel&utm_campaign=reparto-mostoles&utm_content=01-dolor-directo |
| /f/d2 | 302 | ...&utm_content=02-cita-que-no-vuelve |
| /f/d3 | 302 | ...&utm_content=03-producto-explicito |
| /f/D1 (mayuscula) | 302 | ...&utm_content=01-dolor-directo (tolera mayusculas) |
| /f/zzz (inventado) | 302 | ...&utm_content=desconocida-zzz (NO deja al que escanea en un callejon) |

RESULTADO: OK. Las tres variantes llevan etiqueta utm_content distinta, un codigo inventado no rompe nada y ademas queda registrado como desconocida-zzz.

### E-03 Redirecciones de dominio y de URLs retiradas
Todas 308 permanentes y correctas: www.nexux.pro -> nexux.pro; /paquetes/starter, /paquetes/pro, /paquetes/total, /prueba-gratis, /oferta, /promo y /ciudad/{madrid,barcelona,valencia,sevilla,bilbao,zaragoza} -> /paquetes/recepcionista.
RESULTADO: OK.

### E-04 Etiquetas SEO por pagina (title, description, canonical, h1, idioma)
Comando: descarga con curl del HTML servido y extraccion con grep de <title>, meta description, link canonical, meta robots, recuento de <h1> y lang.

RESULTADO GENERAL: OK con tres defectos.
- Todas las paginas declaran `lang="es"`. OK.
- Todas tienen canonical propio y correcto (ninguno apunta a otro dominio). OK.
- Todas tienen exactamente 1 <h1>... **salvo /demo, que tiene CERO <h1>**. Ver ALTA-2.
- **Title duplicado exacto**: /paquetes/recepcionista y /paquetes/equipo comparten el mismo title "Recepcionista IA para negocios | Nexux" y el mismo og:title. Ver MEDIA-1.
- **Textos sin tildes** en metadatos servidos al publico: /demo ("ve como gestiona citas automaticamente") y /privacidad ("Politica de privacidad... para peluquerias en Espana"). Ver BAJA-2.

### E-05 Open Graph / Twitter cards
- Home, /paquetes/*, /blog y resto: og:title, og:description, og:type, og:url, og:image (1200x1200), og:image:alt, og:locale es_ES, twitter:card summary_large_image, twitter:site @nexuxpro. Imagen https://nexux.pro/img/nexux-lara-crm.jpg -> **HTTP 200, image/jpeg, 169.981 B**. OK.
- **/demo NO tiene ninguna etiqueta Open Graph ni Twitter**. Verificado con grep sobre el HTML servido: cero coincidencias de og: y twitter:. Ver ALTA-2.

### E-06 Datos estructurados (JSON-LD)
Parseados con json.loads sobre cada bloque <script type="application/ld+json">.
- Todos los bloques encontrados son **JSON valido** (ninguno rompio el parser).
- Home: WebSite + Organization (con Wikidata Q141254732, legalName Nexux Innovacion Digital S.L.) + VideoObject del anuncio con transcripcion y precio "29 EUR al mes". Coherente.
- /paquetes/recepcionista: Product "Nexux Recepcionista IA" con Offer **price 29 EUR/mes** + FAQPage. Coherente con el precio anunciado.
- /paquetes/equipo: Product "Nexux Recepcionista Equipo" con Offer **price 79 EUR/mes** + FAQPage. Coherente.
- /alternativa-a-booksy: FAQPage citando precios de Booksy con fecha de comprobacion (2 sep 2026). Correcto por transparencia.
- **/demo NO lleva ningun JSON-LD.**
RESULTADO: OK salvo /demo.

### E-07 Precios anunciados (29 EUR / 79 EUR) y restos de los planes retirados
Comando 1 (web publica): descarga de las 14 paginas y `grep -E '249|449|749'`.
RESULTADO: **OK en la web publica**. La unica coincidencia es "...3.23.007-.032.014-.15-.056-.249-.024..." dentro de un atributo `path d=` de un SVG en /demo: no es un precio.
- Home: "29 EUR/mes" en title, description, og y JSON-LD del video. Correcto.
- /paquetes/recepcionista: 29 EUR en texto, Product/Offer y FAQ. Correcto.
- /paquetes/equipo: 79 EUR en texto, Product/Offer y FAQ. Correcto.
- llms.txt: 29 EUR/mes, y ademas dice explicitamente "No hay periodo de prueba gratuito". Coherente.

Comando 2 (codigo fuente en la Pi): `grep -rnE '\b(249|449|749)\b' src public api`.
RESULTADO: **FALLO — quedan cuatro nidos de los precios retirados**, tres de ellos alcanzables por un cliente real:
1. `src/pages/cliente/[id].astro` lineas 72-75 y 791-817: el **portal del cliente** rotula el plan como 249/449/749 EUR/mes y pinta tres tarjetas de precio con esos importes.
2. `api/leads/pro.js` lineas 25-27 (**la de la carpeta api/ de la raiz, que es la que ejecuta**): los avisos de lead que salen del formulario dicen "Starter (249 EUR/mes)", "Pro (449 EUR/mes)", "Total (749 EUR/mes)".
3. `src/components/CalculadoraCitas.astro` lineas 37-52: tres planes a 249/449/749 EUR **y un boton "Activa tu prueba gratis"**. Hoy no se renderiza en ningun post (ningun articulo pasa showCalculator), pero basta un post nuevo con showCalculator para publicarlo.
4. `src/pages/admin/client/[clientId].astro` linea 55: etiquetas de plan 249/449/749 en el panel de administracion (interno).
Ver ALTA-1 y MEDIA-2.

### E-08 Rutas /api/ probadas con peticion REAL (no leyendo el codigo)
| Peticion | Resultado real | Lectura |
|---|---|---|
| `POST /api/book` (formulario publico de reserva) | **404 NOT_FOUND** (cuerpo "The page could not be found") | Confirmado: la ruta esta muerta. |
| `GET /api/book` | 404 | idem |
| `POST /api/analytics/ob` | **404 NOT_FOUND** | **HALLAZGO NUEVO: el endpoint de analitica propia tambien esta muerto.** |
| `POST /api/leads/pro` con cuerpo vacio | 400 `{"error":"missing_fields",...}` | Viva. Es la de `api/leads/pro.js` de la raiz (la de los precios viejos). |
| `GET /api/stripe/create-session` | 405 (metodo no permitido) | Viva, responde la funcion de la raiz. No se ejecuto ningun pago. |
Causa: la carpeta `api/` en la raiz del proyecto convierte /api/* en funciones de Vercel y tapa tanto `src/pages/api/*` de Astro como los rewrites de vercel.json.

### E-09 Quien depende de las rutas /api/ muertas
Comando: `grep -rn '/api/book' src` y `grep -rn 'analytics/ob' src`.
- `src/pages/reservar/[id].astro:110` hace `fetch('/api/book', ...)` -> **la pagina publica de reserva del salon no puede reservar**: cada intento choca con un 404.
- `src/pages/cliente/[id]/onboarding.astro:883` hace `fetch('/api/analytics/ob', ...)` -> **la medicion del onboarding del cliente nuevo no llega a ningun sitio**. El endpoint deberia reenviar a https://pi.nexux.pro/track y nunca se ejecuta.
Ver BLOQUEANTE-1 y ALTA-3.

### E-10 MEDICION con navegador real (Playwright, movil 375x812) — estado SIN consentimiento
Metodo: perfil limpio (localStorage y cookies borrados), entrada por el QR real `https://nexux.pro/f/d1`, captura de las peticiones de red de verdad (no lectura del HTML).

Aterrizaje verificado: /f/d1 -> /demo?utm_source=octavilla&utm_medium=papel&utm_campaign=reparto-mostoles&utm_content=01-dolor-directo. Las UTM llegan.

Peticiones REALES en /demo, sin haber aceptado nada:
| Destino | Que es | Resultado |
|---|---|---|
| https://bzrcdn.openai.com/sdk/oaiq.min.js + POST https://bzr.openai.com/v1/sdk/events | pixel de OpenAI Ads | **DISPARA** (202) con `oaiq_consent=false` |
| POST https://nexux.pro/stats/api/send (x2) | Umami por el proxy anti-adblock | **DISPARA** (200) — el proxy /stats funciona |
| POST https://plausible.io/api/event | Plausible | **DISPARA** (202) |
| POST https://pi.nexux.pro/demo/track | telemetria propia de la demo | **DISPARA** (204) |
| connect.facebook.net / facebook.com/tr | Meta Pixel | **NO DISPARA** (`typeof window.fbq === 'undefined'`) |
| googletagmanager.com/gtag/js | GA4 | **NO DISPARA** (`typeof window.gtag === 'undefined'`) |

**Y el motivo es grave: en /demo NO EXISTE el banner de cookies.**
Comprobado con `document.querySelectorAll('[id*=cookie],[class*=cookie],[id*=consent],[class*=consent]')` -> **0 elementos** en /demo, frente a `div#nx-cookie-banner.cookie-banner` que SI aparece en la home. Sin banner no hay forma de dar el consentimiento, asi que en /demo **Meta Pixel y GA4 no se activan nunca**, aunque el HTML lleve el codigo (6 apariciones de `fbq` y 6 de `gtag`).
Ver BLOQUEANTE-2.

### E-11 /demo: la pagina no usa el Layout del sitio
Consecuencias verificadas todas en el HTML servido y en el DOM:
- 0 etiquetas `<h1>` y 0 `<h2>`.
- 0 etiquetas Open Graph y 0 Twitter cards -> compartida por WhatsApp sale sin imagen ni titulo.
- 0 bloques JSON-LD.
- 0 banner de cookies (ver E-10).
Es exactamente la pagina a la que apuntan los tres QR de las octavillas.

### E-12 Banner de cookies: que se carga ANTES y DESPUES de aceptar (home, movil 375x812)
ANTES de tocar el banner (perfil limpio):
- Meta Pixel: NO carga. GA4: NO carga. **Correcto.**
- Umami (POST /stats/api/send, 200), Plausible (POST plausible.io/api/event, 202), pixel de OpenAI (bzrcdn.openai.com + POST bzr.openai.com/v1/sdk/events, 202): **SI cargan sin consentimiento.**
- **Stripe.js completo antes de consentir**: js.stripe.com/v3/, m-outer-*.js, m.stripe.network/inner.html, out-4.5.45.js y POST m.stripe.com/6. Deja la cookie de terceros `__stripe_mid` (verificada en document.cookie). Ver MEDIA-3.

DESPUES de pulsar "Aceptar todo":
- GA4 `G-GS6BCN6TMJ`: POST region1.analytics.google.com/g/collect ... `en=page_view` -> **204 OK**, con `ep.anonymize_ip=true` y `npa=1`.
- Meta Pixel `1467739621760495`: GET facebook.com/tr/?ev=PageView -> **200 OK**, con `ap[contents]=[{"item_price":29}]` (precio correcto).
RESULTADO: el mecanismo de consentimiento funciona en las paginas que llevan el Layout.

Matiz importante y verificado: si el visitante YA acepto en otra pagina, al entrar luego en /demo si se activan `fbq` y `gtag` (comprobado: `localStorage.nx_cookie_consent = 'accepted'` -> `typeof window.fbq === 'function'`, y salen las peticiones reales de GA4 `page_view` y Meta `PageView` con la URL con UTM). El problema no es que /demo no tenga codigo de medicion: **es que el que llega directo del QR a /demo no ve banner y por tanto no puede aceptar nunca**.

### E-13 Pixel de OpenAI y "rechazar"
Con `nx_cookie_consent=rejected` (estado heredado de otra sesion, verificado en localStorage) y con `oaiq_consent=false`, el SDK de OpenAI **sigue cargando y sigue enviando eventos** (POST bzr.openai.com/v1/sdk/events -> 202). No esta bajo el interruptor del banner: el banner solo menciona "Analitica (GA4) y publicidad (Meta)". Ver MEDIA-4.

### E-14 El evento de conversion: probado de verdad, entrando por el QR
Metodo: entrada por https://nexux.pro/f/d2, clic en /demo -> "Ver Recepcionista IA" -> /paquetes/recepcionista -> clic en "Quiero recuperar esas citas". Interceptados `fetch` y `sendBeacon` para leer los cuerpos reales.

Lo que sale al pulsar el boton de compra (todo verificado, cuerpo real):
| Sistema | Evento | Lleva UTM | Lleva importe |
|---|---|---|---|
| Meta (endpoint mpc-prod) | `InitiateCheckout` | SI (`custom_data.utm_source=octavilla`...) | SI `conversion_value {value:29, currency:EUR}` |
| GA4 | `begin_checkout` | SI (`ep.utm_source=octavilla`, `ep.utm_campaign=reparto-mostoles`, `ep.utm_content=02-cita-que-no-vuelve`) | SI `epn.value=29` |
| Umami (via /stats/api/send, sitio 682a2c1c-85be-41eb-b8a1-95d575e30545) | `checkout_started` | SI (`data.utm_source=oct...`) | — |
| Plausible | `checkout_started` | SI (props utm completas) | — |
| OpenAI | `checkout_started` | — | SI `amount: 2900` |
Ademas se envia el evento de clic con nombre propio: `plan_recepcionista_checkout_top` a Meta, GA4 y Plausible.
Despues: `POST /api/stripe/create-session` -> **200**, y se abre el checkout embebido real (`cs_live_...`, clave `pk_live_...`, `deferred_intent[mode]=subscription`, `amount=2900`, `currency=eur`). **No se completo ningun pago.**
RESULTADO: **OK. La atribucion de la octavilla llega hasta el evento de inicio de compra en los cinco sistemas.**
Un matiz medible: el checkout se abre en modo `subscription` con importe 2900 y sin ningun periodo de prueba, lo que confirma que se cobra desde el dia 1.

### E-15 "Prueba gratuita de 7 dias": la busque y NO esta en la web publica
Se me pidio localizar donde la web promete una prueba gratuita de 7 dias. **No he podido reproducirlo, y lo digo con la evidencia:**
- `grep -ioE 'prueba gratis|prueba gratuita|gratis durante|7 d[ií]as|siete d[ií]as|sin coste|free trial'` sobre el HTML servido de las 14 paginas publicas -> **cero coincidencias**.
- Texto renderizado del modal de checkout abierto en /paquetes/recepcionista -> **cero coincidencias**.
- llms.txt dice lo contrario, de forma explicita: *"No hay periodo de prueba gratuito: el asistente puede probarse en directo y sin dar datos en nexux.pro/demo"*.
- Lo unico que promete prueba gratis en el repositorio es `src/components/CalculadoraCitas.astro:52` ("Activa tu prueba gratis") y el fichero muerto `src/pages/demo.astro.bak-canonical-20260818` ("7 dias gratis"). **Ninguno de los dos se sirve hoy**: el .bak no es una ruta, y la calculadora solo se pinta si un articulo del blog pasa `showCalculator`, cosa que ningun articulo hace hoy.
CONCLUSION DE ESTA AREA: hoy la web **no** promete prueba gratuita. El riesgo es latente, no vigente: basta publicar un articulo con la calculadora para que aparezca la promesa junto a precios de 249/449/749. Ver ALTA-1.
(Si otro auditor la vio en un flujo distinto — correo, Lara, panel del cliente — no esta desmentido: yo solo he verificado la web publica.)

### E-16 Umami: recibe datos HOY y el proxy anti-adblock funciona (cierre de bucle)
- Contenedores: `umami-umami-1 Up 17 hours`, `umami-db-1 Up 17 hours (healthy)`. `/api/heartbeat` -> 200 en local (:3010) y en https://umami.nexux.pro.
- Proxy: `GET https://nexux.pro/stats/script.js` -> 200 application/javascript (4.655 B) y `POST https://nexux.pro/stats/api/send` -> 200. **El proxy anti-adblock funciona.**
- Datos de HOY (consulta directa a la base de datos):
  ```
  nexux.pro            |  68 eventos hoy | 273 en 30 dias
  nexuxintelligence.es |   5             | 126
  nexux.es             |   0             |  97
  ```
- Eventos de hoy en nexux.pro: 48 vistas de pagina, 12 `demo-llegada`, 3 `demo_started`, 2 `chatgpt_ads_landing`, 2 `demo_booking_created`, 1 `checkout_started`.
- **Cierre de bucle**: el `checkout_started` que dispare yo a las 18:42:43 UTC entrando por /f/d2 aparece en la base de datos con sus propiedades:
  ```
  utm_source=octavilla | utm_medium=papel | utm_campaign=reparto-mostoles
  utm_content=02-cita-que-no-vuelve | plan=recepcionista | value=29.0000 | currency=EUR
  ```
RESULTADO: **OK, verificado extremo a extremo.** Del QR de papel al registro en la base de datos, con la variante de octavilla identificada.
(Nota: parte de los 68 eventos de hoy son mios, de esta auditoria.)

### E-17 Rendimiento REAL (medido, no estimado)
Peso real de cada recurso de la portada, pedido con `curl --compressed` (tamano tal y como viaja):
```
  16.954 B  HTML de la portada (comprimido; 67.202 B sin comprimir)
   5.560 B  /_astro/Layout.BamzhQKs.css
   9.805 B  /_astro/index.DZzAFU_z.css
  53.414 B  /img/crm-agenda-real.webp
   6.812 B  /img/crm-roi-card-real.webp
  19.422 B  /video/poster.webp
   2.266 B  /stats/script.js  (Umami)
   1.988 B  plausible.io script
 256.972 B  js.stripe.com/v3/          <-- terceros
 175.216 B  googletagmanager gtag.js   <-- terceros
 107.908 B  connect.facebook.net       <-- terceros
  25.503 B  bzrcdn.openai.com/sdk      <-- terceros
 --------
 681.820 B (665 KB) sin contar el video ni las fuentes de Google
```
Lectura: **el sitio propio pesa ~112 KB; los scripts de terceros pesan ~570 KB, cinco veces mas.**
- El video del anuncio (4.108.055 B en .webm) lleva `preload="none"` y poster .webp de 19 KB -> **no se descarga hasta que se pulsa. Bien resuelto.**
- Imagenes: las dos de la portada son .webp con `loading="lazy"` y con `alt` descriptivo. **Ninguna imagen sin alt en la portada.**
- Jerarquia de encabezados de la portada: 1 H1, luego H2/H3/H4 en orden. Correcta.
- Enlaces internos con ancla (#calculadora, #como-funciona, #paquetes): **todos los destinos existen**, ninguno vacio.
Tiempos medidos en el navegador con la cache ya caliente (por tanto NO comparables con una primera visita): TTFB 40 ms, FCP 320 ms, DOMContentLoaded 397 ms, load 560 ms. Desde curl en frio, el TTFB del origen esta entre 0,09 y 0,30 s en todas las paginas.
**PROBLEMA**: `js.stripe.com/v3/` (257 KB) se carga en TODAS las paginas del Layout — blog, /legal, /privacidad, /gracias, /comparativa — donde no hay ningun pago. Ver MEDIA-3.

### E-18 Enlaces
- Enlaces externos de todo el sitio (unicos): `https://biz.booksy.com/es-es/`, `fonts.googleapis.com`, `fonts.gstatic.com`. Ninguno roto.
- Enlaces internos: todos apuntan a rutas que devuelven 200 o 308 (ver E-01 y E-03). `mailto:info@nexux.pro` presente en el pie.
- No hay ningun enlace interno que apunte a /api/, ni a paginas retiradas.
RESULTADO: OK, ningun enlace roto.

### E-19 Pagina 404
`GET https://nexux.pro/pagina-inexistente-abc` -> **404** con pagina propia (8.861 B), titulo "404 | Nexux Pro", texto util y dos salidas: "Volver al inicio" y "Hablar con Lara". Lleva el banner de cookies.
RESULTADO: OK. Unico defecto: el texto va **sin tildes** ("Esta pagina no existe", "Puede que el enlace este roto", "Desde aqui"). Ver BAJA-2.

### E-20 Paginas que no deben indexarse
| Pagina | meta robots | Veredicto |
|---|---|---|
| /admin | `noindex,nofollow` | OK |
| /acceso-denegado | `noindex, nofollow` | OK |
| /cliente/<id>/login | `noindex,nofollow` | OK |
| **/gracias** ("Pago completado") | **ninguno** | **FALLO** — indexable. Ver MEDIA-5. |
Ninguna de ellas esta en el sitemap, lo cual es correcto. El sitemap (13 URLs) coincide exactamente con las paginas publicas que si deben indexarse.

### E-21 Blog
- Los 4 articulos: 200, 1 H1 cada uno, canonical propio, description propia, **JSON-LD Article valido** + el grafo WebSite/Organization. Sin imagenes (0 img -> 0 sin alt).
- Ninguno menciona precios retirados ni prueba gratuita.
RESULTADO: OK.

### E-22 Veracidad de lo que declara el JSON-LD
- `sameAs` Wikidata **Q141254732 existe** (HTTP 200; etiqueta en espanol "Nexux Pro", descripcion "software espanol de recepcionista con inteligencia artificial para salones de belleza"). El dato es cierto.
- `sameAs` https://www.instagram.com/nexux.pro -> 200. `sameAs` https://twitter.com/nexuxpro -> 301 (redireccion normal de X). Ambos existen.
- Precios del Product schema (29 y 79 EUR) coinciden con lo que cobra Stripe (`deferred_intent[amount]=2900` verificado en el checkout real).
RESULTADO: OK, los datos estructurados dicen la verdad.

### E-23 Movil 375x812 (captura real)
/demo por el QR /f/d3 en movil: se ve completa y usable, las pestanas "Lo que ve tu cliente" / "Lo que ves tu" funcionan, el campo de escribir es accesible y no hay desbordes.
Dos cosas a la vista en la captura:
1. **No aparece el banner de cookies** (confirma E-10).
2. El primer mensaje de Lara sale **sin tildes ni signos de apertura**: *"Puedo ayudarte a reservar cita, informarte de precios y horarios, o gestionar tu reserva. En que puedo ayudarte hoy?"*. Es la primera frase que lee quien escanea la octavilla. Ver MEDIA-6.
3. Hay un hueco vertical grande y vacio entre el saludo y las sugerencias, en un movil de 375 px.

### E-24 Consola del navegador
0 errores de JavaScript en portada, /demo y /paquetes/recepcionista. Solo 2 avisos, ambos de la libreria de Stripe ("Origin trial controlled feature not enabled: tools") y uno de una API de rendimiento obsoleta. Sin impacto.

### E-25 El origen de las visitas a la demo se esta ADIVINANDO, y lo adivina mal
Comprobacion cruzada en la base de datos de Umami (query real vs propiedad guardada):
```
 fecha (UTC)              | url_query                                  | origen guardado
 2026-09-03 18:47:55      | utm_source=octavilla&utm_medium=papel&...   | directo   <-- MAL
 2026-09-03 18:41:04      | utm_source=octavilla&utm_medium=papel&...   | directo   <-- MAL
 2026-09-03 18:39:30      | utm_source=octavilla&utm_medium=papel&...   | directo   <-- MAL
 2026-09-03 18:38:52      | utm_source=octavilla&utm_medium=papel&...   | directo   <-- MAL
 2026-09-03 13:17:29      | utm_source=octavilla&utm_medium=papel&...   | directo   <-- MAL
 2026-09-03 10:08:48      | utm_source=octavilla&utm_medium=papel&...   | qr-flyer  <-- bien, por casualidad
 2026-09-03 08:53:14      | utm_source=openai&utm_medium=paid&...       | interno   <-- MAL
 2026-09-03 08:53:01      | utm_source=openai&utm_medium=paid&...       | directo   <-- MAL
```
Causa (`src/pages/demo.astro`, lineas 231-244): la funcion `origenProbable()` deduce el origen del `document.referrer` y del user-agent, y **no mira las UTM**. Su comentario lo explica: *"El QR ya esta impreso y no se le puede anadir etiqueta"*. Eso dejo de ser cierto con los commits f5e90e8 y 71a2e03, que crearon /f/d1, /f/d2 y /f/d3 con etiqueta propia. La funcion quedo obsoleta y ahora **fabrica** un dato que ya existe exacto en la URL.
Ademas, el evento `demo-llegada` no guarda `utm_content`, que es justo lo que distingue las tres variantes de octavilla. La informacion se puede rescatar de `url_query`, pero no desde el panel por evento.
Ver ALTA-4.

### E-26 Coherencia entre lo que promete la web y lo que dicen sus propias condiciones
- La web promete **"30 dias de garantia"** en el pie, en `PlanDetail.astro` ("Pruebala 30 dias en tu negocio. Si no te compensa, te devolvemos el dinero"), en `Pricing.astro`, en las meta descriptions de /paquetes/* y en el FAQ estructurado.
- `GET /legal`: **0 apariciones** de "garantia de devolucion", "desistimiento", "reembolso", "devolucion", "30 dias", "permanencia" o de los precios. Lo unico que dice sobre garantias es una **exclusion** de garantias de disponibilidad. Tampoco figuran NIF/CIF ni domicilio social del titular.
  -> La promesa comercial mas fuerte del sitio no esta recogida en ninguna condicion. Ver ALTA-5.
- **Correo de contacto incoherente**: `hola@nexux.pro` aparece 6 veces (en /legal y /privacidad, como contacto del responsable) y `info@nexux.pro` 15 veces (pie, llms.txt). Ver BAJA-3.
- **/privacidad no declara todo lo que se carga**: nombra GA4, Meta Pixel, Stripe y Brevo, pero **no menciona Umami, ni Plausible, ni el pixel de OpenAI**, que son precisamente los tres que se activan SIN consentimiento (verificado en E-10/E-12). Ver ALTA-6.

### E-27 /api/leads/pro: vivo pero sin nadie que lo llame
`grep -rn 'api/leads/pro' src public` -> **cero llamantes en la web actual**. El endpoint responde (400 con validacion), esta publicado y, si alguna vez se usa, envia a Telegram los rotulos "Starter (249 EUR/mes)", "Pro (449 EUR/mes)", "Total (749 EUR/mes)". Impacto hoy: bajo. Riesgo: quedaria un aviso interno con precios que ya no existen.

---

# RESUMEN

**Estado del area:** la web publica esta viva, es rapida (TTFB 0,09-0,30 s) y no tiene ni un enlace roto ni un error de JavaScript; el SEO tecnico y los datos estructurados son solidos y los precios publicos (29 EUR / 79 EUR) son correctos en toda la web. La medicion de la conversion funciona de extremo a extremo: probe el recorrido real del QR de papel hasta el registro en la base de datos de Umami con la variante de octavilla identificada.
**Hallazgos:** 2 bloqueantes, 6 altas, 6 medias, 3 bajas.
**Veredicto para lanzar: SI CON CORRECCIONES.** Nada impide vender hoy por la web, pero /api/book devuelve 404 (el salon que pague no podra recibir reservas por su pagina publica) y /demo — la pagina que recibe todo el trafico de las octavillas — no pide consentimiento de cookies y no mide con Meta ni GA4.

---

# TABLA DE COMPROBACIONES

| Que | Como | Resultado | Evidencia |
|---|---|---|---|
| Estados HTTP de las 26 rutas publicas | bucle curl con %{http_code} | OK | E-01 |
| Redirectores de octavillas /f/d1,d2,d3 y codigo inventado | curl siguiendo Location | OK | E-02 |
| Redirecciones www y URLs retiradas (12) | curl | OK (308) | E-03 |
| title/description/canonical/lang/h1 en 14 paginas | curl + grep sobre el HTML servido | FALLO parcial | E-04 |
| Open Graph y Twitter, imagen cargando | curl + fetch de la imagen | FALLO en /demo | E-05 |
| JSON-LD valido y veraz | json.loads + comprobacion de Wikidata y redes | OK | E-06, E-22 |
| Precios 29/79 en toda la web | grep de 249/449/749 sobre HTML servido + repo | OK en web, FALLO en codigo | E-07 |
| Rutas /api con peticion real | curl POST/GET | FALLO (/api/book y /api/analytics/ob a 404) | E-08 |
| Promesa de prueba gratuita | grep sobre HTML servido + texto del modal | No existe hoy en la web | E-15 |
| Pixeles disparando de verdad | Playwright, captura de red real | FALLO en /demo sin consentimiento | E-10 |
| Banner de cookies antes/despues | Playwright, perfil limpio | FALLO (falta en /demo; Stripe antes de aceptar) | E-10, E-12 |
| Evento de conversion con UTM | Playwright + intercepcion de fetch/beacon | OK, cinco sistemas | E-14 |
| Umami recibe hoy y proxy /stats | curl + consulta a la base de datos | OK | E-16 |
| Origen de la visita a la demo | cruce url_query vs propiedad en base de datos | FALLO | E-25 |
| Rendimiento y peso | curl --compressed por recurso + Performance API | OK con reserva | E-17 |
| Enlaces internos, externos y anclas | grep + comprobacion de ids en el DOM | OK | E-18 |
| Pagina 404 | curl a URL inexistente | OK | E-19 |
| noindex en paginas de servicio | curl + grep | FALLO en /gracias | E-20 |
| Movil 375x812 | Playwright, captura | OK con dos defectos | E-23 |
| Coherencia web vs condiciones legales | lectura de /legal y /privacidad | FALLO | E-26 |
| Lighthouse en movil | — | **NO VERIFICADO** (ver seccion final) | — |

---

# HALLAZGOS

## BLOQUEANTE

### BLOQ-1 — El formulario publico de reserva no puede reservar: /api/book responde 404
- **Sintoma:** `POST https://nexux.pro/api/book` devuelve **404 NOT_FOUND** (cuerpo "The page could not be found"). `GET` tambien.
- **Causa:** la carpeta `api/` en la raiz del proyecto hace que Vercel trate /api/* como sus propias funciones y tape las rutas de Astro en `src/pages/api/`. Como `api/book.js` no existe en la raiz, la ruta simplemente no existe en produccion.
- **Reproducir:** `curl -X POST https://nexux.pro/api/book -H 'Content-Type: application/json' -d '{}'` -> 404.
- **Impacto:** `src/pages/reservar/[id].astro:110` es el unico consumidor. Un salon que pague 29 EUR y comparta su enlace de reservas vera que ningun cliente consigue reservar. Es la promesa central del producto rota en el canal web. (No lo he probado con el identificador de un salon real para no tocar datos de clientes; la ruta esta muerta para cualquier identificador.)
- **Propuesta:** mover `src/pages/api/book.ts` a `api/book.js` en la raiz (mismo sitio donde ya viven leads, stripe y webhook), o eliminar la carpeta `api/` de la raiz y dejar que Astro sirva todas las rutas. La primera es la de menos riesgo hoy; la segunda es la correcta a medio plazo, porque hoy hay dos implementaciones de webhook y de leads y solo se ejecuta una.
- **Esfuerzo:** 1-2 h (mover + probar con un salon de prueba). La limpieza completa de la duplicidad: medio dia.

### BLOQ-2 — /demo no pide consentimiento de cookies, y es la pagina que recibe toda la publicidad
- **Sintoma:** en /demo no existe el banner. `document.querySelectorAll('[id*=cookie],[class*=cookie],[id*=consent],[class*=consent]')` -> **0 elementos**, frente a `div#nx-cookie-banner` que si aparece en la portada y hasta en la pagina 404.
- **Causa:** /demo no usa `src/layouts/Layout.astro`; monta su propio `<head>` y su propio HTML.
- **Reproducir:** perfil de navegador limpio -> `https://nexux.pro/f/d1` -> no aparece ningun banner; y sin embargo salen peticiones reales a `bzr.openai.com/v1/sdk/events` (202), `plausible.io/api/event` (202) y `/stats/api/send` (200).
- **Impacto doble:**
  1. **Legal:** la pagina que recibe las octavillas y los anuncios de OpenAI carga un pixel publicitario de terceros sin pedir permiso ni ofrecer forma de negarlo.
  2. **Dinero:** el visitante que llega del QR no puede aceptar cookies, asi que **Meta Pixel y GA4 no se activan nunca para el**. Se pierde el publico de remarketing y la conversion en el panel de Meta justo del canal que se esta pagando. (Umami y Plausible si lo registran, asi que el numero total no se pierde; lo que se pierde es la atribucion en las plataformas de anuncios.)
- **Propuesta:** incluir el mismo componente de banner en /demo (extraerlo a un componente propio e importarlo tambien alli), o hacer que /demo use el Layout comun. Lo segundo arregla de paso ALTA-2.
- **Esfuerzo:** 1 h la version minima (importar el banner); 3-4 h pasar /demo al Layout comun con cuidado de no romper su diseno a pantalla completa.

## ALTA

### ALTA-1 — Bomba de relojeria: la calculadora del blog lleva 249/449/749 EUR y "Activa tu prueba gratis"
- **Sintoma:** `src/components/CalculadoraCitas.astro` lineas 37-47 pinta tres planes a 249, 449 y 749 EUR, y la linea 52 remata con `<a href="/paquetes/recepcionista">Activa tu prueba gratis</a>`.
- **Estado hoy:** **no se sirve**. Solo lo usa `src/layouts/BlogPost.astro:94` cuando el articulo pasa `showCalculator`, y ningun articulo lo pasa. Verificado: los 4 posts servidos no contienen 249/449/749.
- **Impacto:** el dia que alguien publique un articulo con la calculadora, la web anunciara precios que ya no existen y prometera una prueba gratuita que Stripe no da. Es exactamente el fallo que se quiere evitar en el lanzamiento.
- **Propuesta:** borrar el componente, o corregirlo a 29/79 EUR y cambiar el boton a "Ver el plan de 29 EUR". Borrar es mas seguro: no lo usa nadie.
- **Esfuerzo:** 15 min.

### ALTA-2 — /demo no tiene h1, ni Open Graph, ni datos estructurados
- **Sintoma:** `document.querySelectorAll('h1').length === 0` y `h2 === 0`; cero etiquetas `og:` y `twitter:`; cero bloques JSON-LD.
- **Causa:** la misma que BLOQ-2, /demo no usa el Layout.
- **Impacto:** compartida por WhatsApp (que es como se comparte una demo de un producto de WhatsApp) sale sin imagen ni titulo de tarjeta. Y para buscadores es una pagina sin encabezado.
- **Propuesta:** pasar /demo al Layout comun, o copiarle el bloque de `<head>` y meter un `<h1>` visualmente oculto con el titulo real.
- **Esfuerzo:** 1 h la version minima.

### ALTA-3 — /api/analytics/ob responde 404: la medicion del onboarding no llega
- **Sintoma:** `POST https://nexux.pro/api/analytics/ob` -> **404**.
- **Causa:** la misma trampa de la carpeta `api/` en la raiz.
- **Reproducir:** `curl -X POST https://nexux.pro/api/analytics/ob -d '{}'` -> 404.
- **Impacto:** `src/pages/cliente/[id]/onboarding.astro:883` envia ahi los pasos del alta del cliente nuevo, que `src/pages/api/analytics/ob.ts` deberia reenviar a `https://pi.nexux.pro/track`. Todo eso se pierde en silencio: no se sabe donde abandona la gente el alta despues de pagar.
- **Propuesta:** misma que BLOQ-1 (mover a `api/analytics/ob.js`).
- **Esfuerzo:** 30 min, va en el mismo cambio que BLOQ-1.

### ALTA-4 — El origen de las visitas a la demo se adivina, y sale mal: las octavillas figuran como "directo"
- **Sintoma:** en la base de datos de Umami, 6 de las ultimas 8 llegadas con `utm_source=octavilla` u `openai` en la URL estan etiquetadas `origen=directo` o `origen=interno`. Solo 1 acerto "qr-flyer".
- **Causa:** `src/pages/demo.astro` lineas 234-244, `origenProbable()` decide por `document.referrer` y por si el user-agent parece movil, **sin mirar las UTM**. Su comentario dice "El QR ya esta impreso y no se le puede anadir etiqueta": eso dejo de ser verdad con los commits f5e90e8 y 71a2e03, que crearon /f/d1, /f/d2 y /f/d3 con etiqueta propia.
- **Reproducir:** entrar por `https://nexux.pro/f/d1` y consultar `SELECT url_query, (propiedad origen) FROM website_event WHERE event_name='demo-llegada'`.
- **Impacto:** el objetivo declarado del reparto de Mostoles es saber **que variante de octavilla funciona**, y hoy el panel dice que el trafico es "directo". Ademas el evento no guarda `utm_content`, que es lo que separa d1 de d2 y d3 (se puede rescatar de `url_query`, pero no desde el panel por evento).
- **Propuesta (trivial):** leer la URL antes de adivinar.
```js
function origenProbable() {
  var p = new URLSearchParams(location.search);
  var s = p.get('utm_source');
  if (s) return s === 'octavilla' ? 'qr-flyer' : s;   // el dato exacto gana
  // ...y solo si no hay UTM, la deduccion de siempre
}
// y anadir las etiquetas al evento:
window.umami.track('demo-llegada', {
  origen: origenProbable(),
  utm_source: p.get('utm_source') || '',
  utm_campaign: p.get('utm_campaign') || '',
  utm_content: p.get('utm_content') || ''
});
```
- **Esfuerzo:** 30 min. Los datos ya recogidos se pueden recuperar de `url_query`.

### ALTA-5 — La garantia de 30 dias no aparece en ninguna condicion, y el aviso legal esta incompleto
- **Sintoma:** la promesa "30 dias de garantia / te devolvemos el dinero" esta en el pie, en /paquetes/recepcionista, en /paquetes/equipo, en las meta descriptions y en el FAQ estructurado. En `GET /legal`: **cero** apariciones de "garantia de devolucion", "desistimiento", "reembolso", "devolucion", "30 dias", "permanencia" o de los precios; lo unico que hay es una **exclusion** de garantias de disponibilidad. Tampoco hay NIF/CIF ni domicilio del titular.
- **Impacto:** la promesa comercial mas fuerte del sitio no tiene respaldo escrito. Si un cliente pide la devolucion, no hay condiciones que aplicar; y si reclama, la web dice una cosa y las condiciones no dicen nada.
- **Propuesta:** anadir a /legal un apartado de condiciones de contratacion: precio con IVA, periodicidad, sin permanencia, procedimiento y plazo de la garantia de 30 dias, y los datos identificativos que exige la LSSICE (NIF y domicilio).
- **Esfuerzo:** 2-3 h de redaccion. (La parte estrictamente juridica corresponde al area G; aqui se reporta como incoherencia entre lo que se anuncia y lo que se firma.)

### ALTA-6 — La politica de privacidad no declara tres de las cosas que la web carga
- **Sintoma:** /privacidad nombra GA4, Meta Pixel, Stripe y Brevo. **No menciona Umami, ni Plausible, ni el pixel de OpenAI** — que son precisamente los tres que se activan sin consentimiento (verificado en E-10 y E-12).
- **Impacto:** lo que se declara y lo que se ejecuta no coinciden, en el documento que existe justamente para que coincidan.
- **Propuesta:** anadirlos a la lista de destinatarios, indicando cual es analitica propia sin cookies (Umami en servidor propio, Plausible) y cual es publicidad de terceros (OpenAI), y colgar este ultimo del banner.
- **Esfuerzo:** 1 h.

## MEDIA

### MEDIA-1 — Los dos planes comparten exactamente el mismo title
- /paquetes/recepcionista y /paquetes/equipo tienen title y og:title identicos: "Recepcionista IA para negocios | Nexux". Solo cambia la description (29 EUR vs 79 EUR).
- **Impacto:** en el resultado de busqueda las dos paginas son indistinguibles; Google puede quedarse con una sola.
- **Propuesta (una linea en `src/pages/paquetes/[plan].astro`):** incluir el nombre y el precio del plan, p. ej. `${plan.name} — ${plan.price} EUR/mes | Nexux`.
- **Esfuerzo:** 15 min.

### MEDIA-2 — El portal del cliente sigue mostrando 249/449/749 EUR
- `src/pages/cliente/[id].astro` lineas 72-75 y 791-817: rotula el plan del cliente como 249/449/749 EUR/mes y pinta tres tarjetas de precio con esos importes. `src/pages/admin/client/[clientId].astro:55` igual (interno). `api/leads/pro.js` lineas 25-27 manda avisos con esos precios, aunque hoy **ningun formulario de la web llama a ese endpoint**.
- **Impacto:** un cliente que pago 29 EUR y entra en su portal puede ver 249 EUR/mes. Vergonzoso y motivo de llamada.
- **Propuesta:** una sola fuente de precios (los dos planes vigentes) importada por portal, admin y leads; borrar las tarjetas de los planes retirados.
- **Esfuerzo:** 2-3 h.

### MEDIA-3 — Stripe se carga entero en todas las paginas, y antes de aceptar cookies
- `js.stripe.com/v3/` pesa **256.972 B** y se carga en /blog, /legal, /privacidad, /gracias y /comparativa, donde no hay ningun pago. Ademas arranca antes del consentimiento y deja la cookie de terceros `__stripe_mid` (verificada en `document.cookie`), junto con `m.stripe.network` y `POST m.stripe.com/6`.
- **Contexto:** el sitio propio pesa ~112 KB; los terceros ~570 KB. Stripe es el mayor de todos.
- **Propuesta:** cargar Stripe.js solo en /paquetes/* y solo al pulsar el boton de compra (import dinamico). Beneficio doble: media pagina menos de peso en el resto del sitio y una cookie de terceros menos antes de consentir.
- **Esfuerzo:** 2 h.

### MEDIA-4 — Rechazar no incluye al pixel de OpenAI
- Con `nx_cookie_consent=rejected` y `oaiq_consent=false`, el SDK de OpenAI sigue cargando y sigue enviando eventos (`POST bzr.openai.com/v1/sdk/events` -> 202). El banner solo habla de "Analitica (GA4) y publicidad (Meta)".
- **Propuesta:** meterlo bajo el mismo interruptor que Meta y nombrarlo en el texto del banner.
- **Esfuerzo:** 1 h.

### MEDIA-5 — /gracias ("Pago completado") es indexable
- No lleva `<meta name="robots">`, al contrario que /admin, /acceso-denegado y /cliente/*/login, que si llevan noindex. No esta en el sitemap, pero Stripe la enlaza como pagina de exito.
- **Propuesta:** anadir `<meta name="robots" content="noindex,nofollow">` en `src/pages/gracias.astro`.
- **Esfuerzo:** 5 min.

### MEDIA-6 — El primer mensaje de Lara en la demo va sin tildes
- Captura real en movil 375x812: *"Puedo ayudarte a reservar cita, informarte de precios y horarios, o gestionar tu reserva. En que puedo ayudarte hoy?"* — sin tildes y sin signo de apertura.
- **Impacto:** es la primera frase que lee quien escanea la octavilla, y es la demostracion de un producto que vende "contesta por ti". Un texto sin tildes resta credibilidad justo en el momento de la prueba.
- **Propuesta:** corregir el saludo inicial ("En que" -> "¿En qué puedo ayudarte hoy?", "Hola!" -> "¡Hola!").
- **Esfuerzo:** 15 min.

## BAJA

### BAJA-1 — /sitemap.xml devuelve 404
El sitemap real es /sitemap-index.xml, correctamente declarado en robots.txt, asi que los buscadores lo encuentran. Pero /sitemap.xml es la URL que se prueba a mano y devuelve la pagina de error. **Propuesta:** una redireccion 308 de /sitemap.xml a /sitemap-index.xml en vercel.json. **Esfuerzo:** 10 min.

### BAJA-2 — Textos sin tildes en paginas servidas
/demo (meta description: "ve como gestiona citas automaticamente"), /privacidad ("Politica de privacidad... para peluquerias en Espana", y todo el cuerpo), /legal (todo el cuerpo) y la pagina 404 ("Esta pagina no existe", "Puede que el enlace este roto", "Desde aqui"). El resto del sitio si lleva tildes, asi que canta. **Esfuerzo:** 1 h.

### BAJA-3 — Dos correos de contacto distintos
`hola@nexux.pro` (6 apariciones, en /legal y /privacidad como contacto del responsable) frente a `info@nexux.pro` (15, en el pie y en llms.txt). **Propuesta:** elegir uno. **Esfuerzo:** 15 min.

---

# NO VERIFICADO (y por que)

1. **Lighthouse en movil.** No lo he ejecutado: habria hecho falta instalar paquetes (prohibido en el encargo) y correrlo en la Pi (3,7 GB de RAM, riesgo de tumbarla). En su lugar he medido lo que Lighthouse mediria: peso real de cada recurso con `curl --compressed`, numero de peticiones y tiempos del navegador. Los tiempos que doy en E-17 son **con la cache caliente**, por tanto mejores que una primera visita real; los del origen (TTFB 0,09-0,30 s por curl en frio) si son representativos.
2. **LCP y CLS.** `getEntriesByType('largest-contentful-paint')` volvio vacio en la sesion de Playwright. No los declaro.
3. **/reservar/<id> con un salon real.** No lo he probado para no tocar datos de clientes. Lo verificado es que el endpoint que esa pagina usa (`/api/book`) devuelve 404 para cualquier peticion.
4. **La promesa de "prueba gratuita de 7 dias" que reporto otro auditor.** No he podido reproducirla en la web publica (E-15). No la desmiento en otros canales (correos, Lara, panel del cliente, textos de Stripe): solo digo que en las 14 paginas publicas y en el modal de checkout no aparece, y que llms.txt afirma lo contrario de forma explicita.
5. **Que el evento llegue a los paneles de Meta Ads y GA4.** He verificado que las peticiones salen y que los servidores responden 200/204 con los parametros correctos, pero no he entrado en las plataformas a confirmar que el evento aparece alli.
6. **Reinicio de nexux-clients.** Durante la auditoria no observe ningun corte en pi.nexux.pro; sus peticiones (`/demo/track` 204, `/demo/appointments` 200) respondieron siempre.

*Fin del area E. Todas las comprobaciones son de 2026-09-03 entre las 20:33 y las 20:55 (hora de Madrid).*
