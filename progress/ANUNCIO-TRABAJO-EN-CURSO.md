# Optimizar el anuncio para CONVERSION — trabajo en curso

> Este fichero existe porque el proceso se ha perdido otras veces al cortarse la
> sesion. Se actualiza segun avanza. Si Claude desaparece a medias, esto es lo
> que hay que leer para continuar. Arrancado el 18-sep-2026.

## Estado del dinero (cerrado)

- Campana `cmpn_deb163a3306c8198bb95b62f10afffb0` en **paused** (comprobado leyendo
  la cuenta, no de palabra).
- Freno de mano echado en `~/.nexux-ads-horario-parado`: el cron de 21:00 **no**
  la encendera. Para reactivarlo hay que borrar ese fichero.
- Gastado en el canal: ~100 EUR. Clientes conseguidos: **0**.

## La queja de Ricardo, y por que tiene razon

Cada sesion le he dado numeros distintos. No fue mala suerte: fue metodo malo.

| dia | lo que dije | por que cambio |
|---|---|---|
| 15-sep | "21:00-03:00 es la franja que convierte" | contaba TOQUES de boton como conversiones |
| 16-sep | "la conversion era un toque, ya esta arreglado" | al arreglarla, la campana se quedo sin senal |
| 18-sep | "21-23 bien, 00-02 mal" | filtre por sesiones que parecen humanas |
| 18-sep | "48% de las visitas no existieron" | descubri las sesiones de 0,072 segundos |

**Causa raiz: no habia UNA definicion fija de "visita real" ni de "conversion", y
cada medicion se hizo con una poblacion distinta.** Mientras eso no se arregle,
cualquier numero que dé vale poco.

## Lo que hay que resolver (el encargo)

1. Auditar TODOS los numeros dados hasta ahora contra los datos crudos.
2. Fijar UNA definicion y UN script canonico re-ejecutable.
3. Medir las horas de verdad, hora por hora, incluida la idea de Ricardo de
   **14:00-17:00** y la posibilidad de **varias franjas**.
4. Arreglar la contradiccion de la caja: la pagina promete "Pruebala 30 dias...
   te devolvemos el dinero" y el pago cobra 29 EUR en el momento, sin trial.
5. Instrumentar lo que falta: un "sigo aqui" a los 3 segundos que distinga
   "entro y se fue" de "nunca hubo nadie" (48% del gasto depende de eso).
6. Rediseñar el horario para admitir VARIAS franjas.

## Hechos medidos que se dan por buenos (y de donde salen)

- 404 sesiones instrumentadas (desde 13-sep 21:24, cuando empezo a medirse
  scroll/clics). 195 mudas (48%), 209 vivas.
- Mudas: 114 tienen exactamente 2 eventos; mediana entre primer y ultimo evento
  **0,072 s**; solo 6 movieron el dedo; 71 vieron el aviso de cookies; NO llegan
  en rafagas (solo 2 minutos del periodo con 3 o mas).
- Embudo sobre vivas: 16 pulsan CTA (7,7%), 10 tocan pagar (4,8%), 3 de 3
  medibles vieron la pasarela, 0 pagaron.
- Gasto por dia: 13-sep 35,93 / 14-sep 33,90 / 15-sep 16,15 / 16-sep 14,10 /
  17-sep 4,67 / 18-sep 2,62 EUR. Conversiones del panel: 1, 3, 0, 0, 0, 0.
- Tope de 15 EUR/dia creado el 15-sep 18:09:42 (antes: bote de 75 EUR).
- `max_bid_micros` 15 EUR es puja de **CPA**, no techo de CPC.
- No hay dayparting en OpenAI Ads (comprobado por 4 vias).
- El horario propio funciono 3 noches: 4 acciones en el registro de auditoria a
  las 03:00:05/07 y 21:00:04/07. 47 de 49 llegadas dentro de franja.
- Pais en Umami es INUTIL: 402 de 404 dicen FR (artefacto del proxy).
- No se recoge ningun dato de velocidad real (0 filas con lcp).
- Aviso de cookies: 126 mostrados, 8 respondidos (6%).

## Correcciones que YA he tenido que hacer a mi mismo

- El 15 EUR no era techo por clic (dije que era 83x el CPC real: falso).
- Los 35,93/33,90 EUR no incumplian el tope (el tope no existia aun).
- No se caen entre tocar pagar y ver el formulario (el evento no existia antes
  del 15-sep 19:35; los 3 medibles vieron el formulario).
- La franja 00:00-03:00 la justifique con 3 toques de 4, 8 y 24 segundos.

## Siguiente paso

Lanzar el analisis en paralelo (auditoria de numeros, horas reales, caja,
instrumentacion, horario multi-franja) y verificar cada propuesta antes de tocar
nada. Resultado esperado: un plan ejecutable y UNA fuente de numeros.

## Analisis en marcha (por si se corta la sesion)

Lanzado el 18-sep 21:47 un analisis en paralelo de 4 investigaciones + 3 disenos +
verificacion adversarial (2 escepticos por cambio propuesto).

- Run ID: `wf_8948324a-ef9`
- Guion: `C:\Users\Nexux\.claude\projects\C--Users-Nexux\1ffe5cdc-415d-4f25-a12b-ca1b90992990\workflows\scripts\anuncio-conversion-bien-hecho-wf_8948324a-ef9.js`
- Transcripcion: `C:\Users\Nexux\.claude\projects\C--Users-Nexux\1ffe5cdc-415d-4f25-a12b-ca1b90992990\subagents\workflows\wf_8948324a-ef9\`

**Si la sesion muere a medias**, se retoma sin perder lo hecho con:
`Workflow({scriptPath: "<el guion de arriba>", resumeFromRunId: "wf_8948324a-ef9"})`
Los agentes ya terminados devuelven su resultado de la cache; solo se re-ejecuta lo que falte.
Antes de dar nada por perdido, leer `journal.jsonl` de la carpeta de transcripcion:
ahi esta lo que devolvio cada agente.

### Que esta investigando

1. **auditar-numeros** — re-deriva desde cero los 10 numeros que le he dado a Ricardo
   (a-j) y dice cuales estaban mal y por que. Incluye el diagnostico de metodo.
2. **horas-de-verdad** — hora por hora las 24, con definicion estricta de visitante real,
   cruzando con EUROS por hora de la API. Contesta si 14:00-17:00 se sostiene y que
   franjas propondria. Obligado a decir que horas no tienen muestra suficiente.
3. **la-caja** — todas las contradicciones del camino del dinero. Pista: la pagina dice
   "Pruebala 30 dias... te devolvemos el dinero" y create-session.js cobra 29 EUR sin trial.
4. **trafico-fantasma** — que son las 195 sesiones de 0,072 s y si se corresponden con
   clics facturados.

### Que esta disenando

5. **fuente-unica** — UN script canonico con UNA definicion escrita, que cruza las tres
   fuentes y avisa cuando no cuadran. Es la solucion de fondo a la queja de Ricardo.
6. **instrumentacion** — el "sigo aqui" a los pocos segundos, la velocidad real (hoy 0
   filas con lcp) y el aviso de vuelta de Stripe (nunca ha ocurrido).
7. **horario-multifranja** — varias franjas al dia declaradas en un sitio, sin tocar cron
   ni codigo; que pasa si la Pi estuvo apagada; limite de seguridad.

Todo en SOLO LECTURA: ningun agente puede escribir en la cuenta de anuncios ni en Umami.

---

## [18-sep 22:2x] Subagente "sesiones mudas" — TERMINADO. Todo medido en vivo.

**VEREDICTO: las mudas SON personas que pulsaron. No es humo, no es prefetch.**

Prueba dura (la unica que zanja la duda): cada llegada trae en la URL un token
`oppref` de OpenAI. Es un token Fernet: los bytes 1..8 son la fecha de emision y
se leen SIN clave. Decodificados los 408 tokens que llegaron:

- 406 tokens distintos para 420 sesiones. Solo 2 tokens repetidos, y NINGUNO
  aparece a la vez en una muda y en una viva.
- Retraso token -> carga de pagina: **minimo absoluto 3,88 s** en TODA la muestra.
  Mediana 51,1 s en mudas y 35,5 s en vivas. Cola hasta 50 horas.
- **Sesiones con retraso < 2 s: CERO de 408.** Un prefetch o una vista previa
  dispara a ~0 s. El cajon que la hipotesis del humo exige lleno, esta vacio.
- Huella de aparato identica entre mudas y vivas: 190/200 movil, ~60 resoluciones
  reales de telefono, 78% es-ES. Una granja de robots seria uniforme.

**PERO "muda" NO significa "0,07 segundos".** Esa mediana es un artefacto: es el
hueco entre el pageview y el evento de llegada, que es lo unico que tienen. En
`/home/nexux/nexux-pro/src/scripts/measurement.ts` NO hay nada que mida tiempo en
pagina (ni pagehide, ni visibilitychange, ni latido), y `heatmap_hover` exige
`pointerType === 'mouse'`, asi que en movil es imposible por diseño (0 de 190
mudas moviles lo tienen). En movil solo quedan scroll y toque. Quien entra, lee
la primera pantalla 30 s sin bajar y se va, deja EXACTAMENTE el mismo rastro que
quien cierra en 0,2 s. Con lo que hay, no se pueden separar.

**Cuadre con los clics facturados (14-18 sep, dias completos):**
281 clics facturados vs 264 tokens unicos llegados = **94,0%**. Por dia: 94,3 /
94,5 / 95,0 / 86,4 / 100%. No falta masa ni sobra: se pierde ~6% (bloqueadores,
JS apagado, abandono antes del script). NO estamos pagando clics fantasma.

**Instrumentacion minima que falta (4 cosas, mismo fichero, sin dependencias):**
1. Evento `salida` en `pagehide` con `sendBeacon` y milisegundos visibles
   acumulados por `visibilitychange`. Esto solo parte el 48% en dos.
2. `document.prerendering` / `visibilityState` al arrancar el script: un booleano
   que mata la duda para siempre.
3. `page_h` y `viewport_h` en el evento de llegada: saber si "no bajo" significa
   "no vio nada" o "ya lo habia visto todo".
4. `oppref_edad_s` como propiedad: ya viene en la URL y se tira.
Aviso: `url_query` en Umami es varchar(500) y la URL del anuncio es mas larga →
`olref` llega cortado. Y `mirarScroll()` se llama una vez al montar, asi que
puede disparar scroll 25% sin que nadie toque: medido, solo contamina 4 de 193.

**Numeros de Opus auditados** (detalle en la respuesta del subagente):
- CONFIRMADOS: (f) gasto diario exacto contra API · (h) 34,0% exacto (17 de 50;
  control: en toda la pagina es 19,5%) · (i) 127/8 · (a)(b)(c) coherentes.
- **MAL (d)**: dije "21-23 = 11,1% y 00-02 = 6,3% con cero pagos". Medido:
  21-23 = 9 de 105 vivas (8,6%); 00-02 = 14,3% y **tiene 3 sesiones que tocaron
  pagar**, no cero. Esta invertido.
- **MAL (e)**: "47 de 49 en 21:00-03:00" no sale con NINGUNA ventana de 48h
  (barrido hora a hora: la de 49 llegadas tiene 42 en banda, 85,7%).
- **ENGAÑOSO (g)**: conversiones API por dia = 13-sep 1, 14-sep 3, 15-sep 0,
  16-sep 0, 17-sep 0, 18-sep 0. El cero empieza el **15-sep, ANTES** del cambio
  de señal del 16. Son 4 dias, no 3, y la causa no puede ser el cambio.
- **NO COMPROBABLE (j)**: la API solo da el tope actual, no el historial.

**HORARIOS — dato que decide (13-16 sep, 13.596 impresiones, 415 clics, 82,22 EUR):**
| bloque | impresiones | clics | CTR |
|---|---|---|---|
| 12:00-18:00 | **64 en 4 dias** | 4 | — |
| de esas, 14:00-17:00 | **24** | 1 | — |
| 18:00-21:00 | 4.343 | 127 | 2,9% |
| 21:00-00:00 | 5.179 | 189 | 3,7% |
| 07:00-11:00 | 3.356 | 76 | 2,3% |
Umami lo confirma solo: **4 sesiones en total entre las 12:00 y las 18:00 en 5
dias.** La idea de 14:00-17:00 no tiene inventario: encenderla ahi no gasta ni
trae nada. Calidad por bloque (sesiones/vivas/CTA/pago): 21-24h 178/104/9/5 ·
00-07h 101/44/5/3 · 07-12h 82/44/2/1 · 18-21h 55/25/1/1 · 12-18h 4/2/0/0.
El horario 21:00-03:00 que YA existe y YA esta en cron
(`scripts/horario-campana-ads.mjs`, log verificado) es el correcto.

---

## RESULTADO DE LA AUDITORIA (19-sep, madrugada)

Las 4 investigaciones terminaron. La verificacion adversarial murio por limite de
sesion y se ha relanzado; los 7 agentes ya hechos se recuperan de cache.

**Bug propio corregido en el guion del analisis:** al morir los 53 verificadores se
quedaron con cero votos, y como "cero refutaciones" no es ">= 1 refutacion", los 26
cambios salieron marcados como "sobreviven". Silencio contado como aprobacion. Ya
esta arreglado: ahora hay un cajon aparte de "SIN VERIFICAR".

### LA CAUSA RAIZ DE QUE LOS NUMEROS BAILEN (comprobado, con control)

El panel de OpenAI **devuelve ceros en silencio** si la ventana que le pides no
empieza exactamente a medianoche de Madrid. Mismo dia 13-sep pedido seis veces:
alineado a medianoche -> 238 clics y 35,93 EUR. Desplazado UNA hora -> 0 clics y
0,00 EUR, con HTTP 200 y sin ningun aviso de error.

`scripts/vigilante-campana-ads.mjs` calcula su ventana como "ultima hora en punto
menos 24h", que casi nunca es medianoche. **Por eso el aviso de cada manana lleva
dias diciendo "clics=0 gasto=0" mientras se gastaba el dinero: 6 de 11 ejecuciones.**

### NUMEROS MIOS QUE ESTABAN MAL

| lo que dije | lo que es |
|---|---|
| "00-02h convierte peor que 21-23h, cero pagos" | **AL REVES**: 00-02h 14-16% frente a 21-23h 8,8-9,7%, y SI hubo 3 llegadas al pago |
| "3 dias con cero conversiones desde el cambio del 16-sep" | son **4 dias** y el primer cero es el **15-sep, ANTES** del cambio |
| "404 sesiones, 195 mudas (48%)" | 405 sesiones, 189-190 mudas (47%); ninguna definicion reproduce 195 |
| "mediana 0,072 s" | 0,066 s — y ademas el numero no significa lo que yo creia (ver abajo) |
| "47 de 49 llegadas en franja (96%)" | 47 de **55** = 85,5%; y "ultimas 48h" no se puede citar, cambia cada minuto |
| "~100 EUR gastados" | **112,53 EUR** (o 137,62 contando la campana vieja de septiembre) |
| "se caen entre tocar pagar y ver el formulario" | falso; de 10 solo 3 eran medibles y las 3 vieron el formulario |

### EL HALLAZGO QUE LO CAMBIA TODO: las mudas SI son personas

Se zanja con el token `oppref` que OpenAI mete en la URL: lleva dentro la hora en que
se creo el anuncio, y se lee sin clave. De 408 llegadas, **ninguna** cargo la pagina
antes de 3,88 segundos despues de aparecer el anuncio; mediana 51 s. Una precarga o
vista previa dispararia a ~0 s: ese cajon esta VACIO. Ademas 406 tokens distintos, y
ningun token compartido entre una muda y una viva. Y cuadran con lo facturado: 281
clics cobrados contra 264 tokens llegados = 94%.

**No estamos pagando fantasmas.** La mediana de 0,07 s era un espejismo: la pagina
NO mide el tiempo que alguien esta delante (no hay pagehide, ni visibilitychange, ni
latido), y `heatmap_hover` exige raton, asi que en movil es imposible por diseno.
Quien lee la primera pantalla 30 segundos y se va deja EXACTAMENTE el mismo rastro
que quien cierra en dos decimas.

### EL HORARIO 21-03 ERA UN RAZONAMIENTO CIRCULAR

Se instalo el 16-sep porque "16 de cada 17 clics estaban ahi". Desde entonces el
anuncio SOLO puede salir de 21:00 a 03:00, asi que toda medicion posterior "confirma"
que la gente llega de noche. Cerrar la tienda de dia y concluir que nadie compra de dia.

Y peor: **encender y apagar a diario esta hundiendo la entrega.** Misma hora, las
21:00, tres dias seguidos: 1.148 -> 164 -> 11 impresiones. Descartadas otras causas
(ningun anuncio ni grupo tocado desde el 09-sep; el 17 y 18-sep ni llego a gastar el tope).

### LAS HORAS: LOS DOS AGENTES NO COINCIDEN, Y HAY QUE DECIRLO

- `horas-de-verdad`: 14:00-17:00 **nunca se ha comprado** (40 impresiones, 1 clic,
  0,01 EUR en toda la ventana medida). No se puede aprobar ni rechazar.
- `la-caja`: en el tramo libre 8-16 sep, 14:00-17:00 dio 20 llegadas, 0 pulsaciones
  de pago y 1 scroll, frente a 157 llegadas y 4 pulsaciones en 21:00-23:00.

Lo comun a los dos: la tarde tiene MUY poca muestra, y la razon es que el
presupuesto ya estaba quemado antes de llegar ahi (la campana se activaba a las
18:00 y se fundia 15,61 EUR en dos horas).

**Lo unico probado como malo: 18:00-20:00** (15,61 EUR -> 14 visitantes reales ->
CERO pulsaciones; 1,12 EUR por visitante real frente a 0,34-0,37 a las 22-23h).

**Aviso grande: el "exito nocturno" se apoya en UNA noche.** De las 16 pulsaciones
que existen, 13 son de la noche del domingo 13 al lunes 14.

### LO QUE MATA LA CONVERSION: EL AVISO DE COOKIES

El pixel de OpenAI solo se carga si pulsan "Aceptar todo". 118 sesiones lo vieron, 8
contestaron, 7 aceptaron. Y es un problema de ORDEN, no solo de porcentaje: la gente
pulsa "pagar" a los 6 segundos y contesta al aviso (si lo hace) a los 12-25 segundos.
Cuando llega el permiso, la conversion ya paso.

### PROMESAS SIN MAQUINARIA DETRAS (hallazgo serio, no tecnico)

- "Pruebala 30 dias... te devolvemos el dinero": no hay proceso de devolucion en
  ningun sitio, /terminos /condiciones /devoluciones dan 404, y la unica pagina legal
  que existe dice "Exclusion de garantias" — lo contrario.
- "Hasta 1.000 conversaciones al mes, te avisamos antes de cobrarte de mas": no
  existe ningun contador de conversaciones en el codigo.
- MI HIPOTESIS DEL TRIAL ERA FALSA: la pagina no promete prueba gratuita, dice "se
  paga desde el primer dia" y ofrece devolucion. No hay contradiccion ahi.

### Y AUNQUE ALGUIEN COMPRE, NO SABRIAMOS QUE VINO DEL ANUNCIO

El pago devuelve a /gracias?plan=recepcionista, **sin identificador de compra**. El
codigo sabe avisar del retorno pero solo si llega `session_id`, y nunca llega: 0
registros en toda la historia. Y la tabla que traduce eventos a OpenAI **no tiene
ninguna entrada para una compra**.

---

## ARREGLADO Y DESPLEGADO (19-sep)

**El parte diario ya no miente.** `date_range` con zona horaria en vez de ventana
desplazada. Probado en vivo: verdad 6 clics / 2,89 EUR, ventana vieja 0 / 0,00,
el vigilante arreglado 6 / 2,88. Sabotajes 2/2 + 1 hueco conocido. Commit e7905ae.
Guardian nuevo: si el panel da cero y la web ve gente, aviso rojo.
Y el aviso ya no promete "vuelve a las 21:00" con el freno echado.

**Stripe, comprobado hoy:** 0 ventas. La factura del 19-sep 02:06 es de 0,00 EUR
(renovacion de la suscripcion de prueba de ricmanpla23@hotmail.com). Las 20
ultimas sesiones de pago del anuncio: todas unpaid/expired y SIN CORREO, o sea
que ni llegaron a teclear el email.

**Verificacion adversarial:** de los 8 cambios verificados (los de 'fuente-unica'),
los 8 REFUTADOS con evidencia. No se ha ejecutado ninguno. Quedan 19 sin verificar
(instrumentacion y horario-multifranja). El analisis se retoma con
`Workflow({scriptPath: <el guion>, resumeFromRunId: "wf_8948324a-ef9"})`.

---

## 🔴 CORRECCION IMPORTANTE (19-sep): SI hay un contacto del anuncio

Ricardo lo vio y yo lo habia contado mal. **Hay 1 prospecto cualificado del anuncio.**

Sesion `cf6c8900`, **14-sep 03:02:10** (Madrid), movil Android 412x924, idioma en-ES:
llego del anuncio A02 -> bajo por la pagina -> pulso **"Ver como responde"**
(`hero_cta_secondary`, el boton SECUNDARIO) -> fue a `/demo` -> escribio a Lara ->
**completo una reserva en la demo**. Tres minutos de principio a fin.

Las UTMs estan EN los datos del evento (`utm_campaign: nexux_recepcionista_29`).
**Mi error:** filtre por la COLUMNA `utm_campaign` de la tabla, que Umami solo rellena
en el primer evento de la visita; al navegar a `/demo` la URL ya no lleva UTMs y la
columna sale vacia. La atribucion funciona perfectamente; la consulta era mia y estaba mal.

### Lo que esto cambia

El camino que SI funciona es la demo, y la campana optimiza hacia el que NO:

| camino | llegadas del anuncio | resultado |
|---|---|---|
| "Quiero recuperar esas citas" (pagar) | 577 | 12 toques, 4 pantallas de pago, **0 pagos** |
| "Ver como responde" (demo) | 577 | 1 persona fue, escribio y **reservo** |

Embudo de la demo, todo el historico (20 visitas distintas por IP):
50% escriben un mensaje, 15% completan reserva. Frente a 0 de 577 del checkout.

**Y la campana persigue `Checkout Started`.** O sea: lleva 112 EUR comprando gente que
toca "pagar" (que no ha producido nada) e ignorando la unica accion que produjo un
prospecto.

### El agujero que hay que tapar

La demo **no guarda ningun contacto**. `demo-visitors.jsonl` solo apunta IP, navegador,
hora y evento. Esa persona hizo todo bien y lo unico que tenemos de ella es una IP
(91.230.55.62). No se le puede escribir.

Ricardo tiene su propia herramienta para verlo: `GET /demo/visitors?key=<SECRET>&geo=1`
en provision-http.js (da ciudad por IP).

### Propuesta revisada

1. **Que la demo capture un contacto** (telefono o correo). Es el cambio de mas valor:
   convierte visitas en gente a la que se puede escribir. Hoy se pierde entera.
2. **Que el evento de conversion de la campana sea la demo, no el checkout.** No se
   puede cambiar en esta campana (esta bloqueado): es razon justificada para crear una
   nueva cuando se reactive.
3. **Dar peso al boton de la demo en la pagina.** Hoy "Ver como responde" es el
   secundario y el de pagar es el principal. Los datos dicen lo contrario.
   Aviso honesto: esto se apoya en UN caso. Pero el otro camino tiene 0 de 577.

---

# 📏 REGLA DE SEPARACION DE FUENTES (obligatoria a partir del 19-sep-2026)

Cada pregunta tiene UNA fuente. Mezclarlas es lo que ha producido una semana de
numeros que no cuadraban.

| pregunta | fuente unica | por que |
|---|---|---|
| Cuanto se ha gastado, cuantos clics, cuantas impresiones | **OpenAI Ads** | es quien cobra |
| Que hizo la gente en la web, y cuantos contactos hay | **Umami + demo-visitors.jsonl + registro del bot** | es lo unico que ve a todos |
| Cuanto dinero ha entrado de verdad | **Stripe** | es donde esta el dinero |

**🔴 El panel de OpenAI NO sirve para contar conversiones reales.** Su pixel solo
dispara si la persona tiene `nx_cookie_consent === 'accepted'` en el navegador
(`measurement.ts`, funcion `sendOpenAiTracker`), y de 128 avisos mostrados solo han
respondido 8. Ademas el evento de conversion de la campana es **Checkout Started**,
asi que una reserva de demo NO cuenta como conversion por mucho que se acepten las
cookies. Usar el panel para saber si alguien se interesa es contar con un ojo tapado.

## Reglas de consulta que hay que respetar

1. **Nunca filtrar por la columna `utm_campaign` de `website_event`.** Umami solo la
   rellena en el primer evento de la visita; al cambiar de pagina se vacia. Hay que
   filtrar **por sesion**: si la sesion tuvo algun `chatgpt_ads_landing`, todo lo que
   hizo esa persona es del anuncio. (Este error me hizo cantar "0 contactos" cuando
   habia 1.)
2. **Al panel de anuncios se le pide siempre `date_range` con `timezone: Europe/Madrid`.**
   Con ventanas desplazadas devuelve CEROS en silencio.
3. **Separar siempre nuestras pruebas del trafico real.** Las sesiones con
   `utm_campaign` = `prueba_conversion`, `prueba_limpia`, `prueba_medicion`,
   `reparto-mostoles` son nuestras. Y las pantallas de pago creadas llamando a la API
   sin pasar por el navegador no aparecen en Umami: son pruebas por definicion.
4. **Nunca citar "ultimas 24/48 horas"** como si fuera un dato fijo: cambia cada
   minuto. Se cita el dia natural.
5. **Sin muestra no hay porcentaje.** Si el denominador es menor que ~30, se da el
   numero crudo ("1 de 530"), no el tanto por ciento.

---

# 🔴 CORRECCIONES DEL 19-sep (segunda ronda, las pillo Ricardo)

## 1. Contactos desde el anuncio: 1, no 0

Contado por SESION y solo con fuentes internas:

```
530  sesiones que vinieron del anuncio
  3  reservaron en la demo  -> de las cuales 2 son PRUEBAS NUESTRAS
                               (831255d8 con prueba_conversion/prueba_medicion,
                                2b85f63f con prueba_limpia/reparto-mostoles)
  1  REAL: cf6c8900, 14-sep 03:02
```

Las reservas de demo de toda la base son **4**, no 5 (yo conte eventos, no personas):
2 pruebas nuestras, 1 del 6-sep sin campana, y **1 del anuncio**.

## 2. El telefono NO es recuperable, porque NO EXISTE

Comprobado en el codigo que ejecuta:
- La demo **no es un WhatsApp de verdad**: es un chat dentro de la pagina
  (`demo.astro` llama a `/demo/chat`). El `channel: 'wa'` es solo la piel verde.
- El calendario de la demo es un decorado: `getDemoApts()` en `provision-http.js`
  devuelve citas inventadas en cada llamada (Ana Garcia, Laura M...). **Una reserva
  hecha en la demo no se guarda en ningun sitio.**
- La conversacion **no se registra**. El unico fichero de la demo es
  `demo-visitors.jsonl`, que guarda IP, navegador, hora y evento. Nada mas.
- El visitante hace de CLIENTE de una peluqueria ficticia: no hay ningun momento en
  que se le pida su propio telefono.

De ese prospecto solo existe: IP `91.230.55.62`, Android movil, y su rastro en Umami.
**No se le puede escribir.** Y no es un fallo puntual: la demo esta construida para
ensenar el producto, no para captar a nadie.

## 3. Aritmetica de las pantallas de pago del 14-sep, corregida

**12 de 13 eran pruebas nuestras, no 9.** (Escribi "nueve" y liste doce horas.)

```
PRUEBAS (12): 09:35, 09:41, 09:52, 09:53
              13:03, 13:03, 13:04, 13:05, 13:06, 13:07, 13:07, 13:08
REAL     (1): 02:33  <- coincide con un checkout_started de Umami
```

Y un hallazgo nuevo que sale de ahi: de los **4 toques reales** de "pagar" ese dia
(00:55 y 01:00 de la misma persona, 02:33 y 08:53), **solo 1 llego a crear pantalla
de pago en Stripe**. Tres personas pulsaron "pagar" y no paso nada.

## 4. Lo que NO se sostiene de la explicacion del consentimiento

Ricardo apunto que esa persona no respondio al aviso de cookies y por eso OpenAI no
recibio su `appointment_scheduled`. La conclusion es correcta pero el camino no:
- Esa sesion no tiene `cookies_mostrado` **porque la MEDICION del aviso no existia
  hasta el 15-sep 18:11**, no porque no se le ensenara.
- La puerta del consentimiento SI existia el 14-sep (`nx_cookie_consent` esta en
  `measurement.ts` desde el 2-sep, commit d20e42b).
- Y sobre todo: **aunque hubiera aceptado las cookies, tampoco habria contado**,
  porque el evento de conversion de la campana es `Checkout Started`, no
  `appointment_scheduled`.

Tampoco se sostiene culpar al aviso de cookies del derrumbe de conversiones desde el
15-sep: el aviso y la puerta ya estaban antes. Lo que se derrumbo fue el VOLUMEN
(238 clics el 13-sep -> 55 el 15 -> 5 el 18). Con ~1% de conversion, 55 clics dan
cero sin necesidad de ninguna averia.

---

# CONCLUSION ECONOMICA DEL 19-sep — y la correccion de mi propia conclusion

## 1. El fallo de fondo NO fue el anuncio. Fue no hacer esta cuenta ANTES de gastar.

Nadie calculo, antes de encender la campana, cuanto podiamos permitirnos pagar por
un cliente. Se optimizo el anuncio durante semanas sin saber contra que numero se
estaba optimizando. Ese es el error raiz, y es mio.

**Regla nueva, obligatoria antes de encender cualquier campana de pago:**
escribir el techo de CAC (lo maximo que se puede pagar por un cliente) y la fuente
del dato de retencion. Si la retencion es DESCONOCIDA, el techo de CAC se calcula
con el escenario pesimista, no con el optimista.

## 2. Lo medido (no estimado)

```
112,53 EUR gastados en esta campana (137,62 EUR con la anterior)
530  sesiones del anuncio
  6  llegaron a la pantalla de pago  (4 de 4 desde que se arreglo el 14-sep 09:48)
  0  tarjetas introducidas
  0  ventas
```

## 3. Lo estimado (marcado como tal, NO medido)

- **LTV desconocido.** No hay ni un cliente de pago, asi que no hay dato de
  permanencia. A 12 meses el plan de 29 EUR vale 348 EUR; a 30 meses, 870 EUR.
  Con CAC ~300 EUR, el primer escenario es ruinoso y el segundo es aceptable.
  **Apostar 300 EUR sobre un LTV desconocido es el error, no el precio de 29 EUR.**
- **Cuantos de los 530 tenian peluqueria: no se sabe.** Nunca se midio. Por eso el
  gasto entero es ininterpretable. Hueco de medicion, no de conversion.

## 4. Correccion de lo que escribi antes

Escribi "los anuncios de pago no pueden vender el plan de 29 EUR. Punto." **Eso es
falso y demasiado amplio.** Lo correcto:

> Un producto de 29 EUR/mes SI se puede publicitar de forma rentable. Lo que no
> funciona es publicitarlo en el canal MAS CARO Y MENOS SEGMENTABLE que existe,
> a un comprador que se puede encontrar por intencion de busqueda.

En ChatGPT Ads no existe segmentacion por tipo de negocio. Se compra interrupcion.
El comprador de este producto ESCRIBE "programa de citas peluqueria" en un buscador:
es trafico de intencion, no de interrupcion.

| | ChatGPT Ads (MEDIDO) | Busqueda por intencion (ESTIMADO) |
|---|---|---|
| quien lo ve | cualquiera | quien busca el producto |
| coste por clic | 0,21 EUR | 0,30-0,80 EUR |
| clics para una venta | ~1.500 | ~100-200 |
| coste por venta | ~300 EUR | ~50-120 EUR |

**La columna derecha NO esta medida.** Es la hipotesis. Se contrasta con 50 EUR,
apuntando a la MISMA pagina y el MISMO checkout: no hay nada que construir.

## 5. Decision pendiente de Ricardo

- Campana actual: muere sola el 22-sep 10:00. Recomendacion: dejarla morir.
- Siguiente paso recomendado: primera venta a mano + prueba de 50 EUR en busqueda
  por intencion. NO renovar ChatGPT Ads.

---

# 🔴 RETRACTACION (19-sep, misma tarde): LA CAMPANA SI ESTABA SEGMENTADA

Lo escrito en la seccion anterior ("en ChatGPT Ads no existe segmentacion por tipo
de negocio, se compra interrupcion") **ES FALSO**. Lo afirme sin mirar el objeto de
la campana. Comprobado ahora contra la API que EJECUTA:

```
GET /v1/campaigns -> cmpn_deb163a3306c8198bb95b62f10afffb0
  "targeting": { "locations": { "include": [ { "type":"country", "country_code":"ES" } ] } }

GET /v1/ad_groups -> adgrp_d84276c1c0a48198a1d6f6b15b3d7618  (activo, puja 15 EUR)
  "context_hints": [
    "En Espana",
    "propietarios y responsables de negocios con cita previa que estan comparando",
    "buscando contratar o preguntando por el precio de una recepcionista IA o un
     software para automatizar reservas por WhatsApp. Conversaciones con intencion
     comercial: 'recepcionista virtual para mi negocio', 'software que responda
     WhatsApp y reserve citas', 'precio de asistente IA para citas',
     'alternativas a contratar recepcionista', 'automatizar agenda sin comisiones'",
    "... peluquerias, centros de estetica, clinicas, talleres ..."
  ]
```

**La campana estaba dirigida a publico cualificado y por intencion comercial, que es
exactamente lo que Ricardo pidio desde el principio.** Queda retirada la conclusion
de "cambiar a busqueda por intencion porque alli si hay segmentacion": la
segmentacion ya estaba.

## Lo que SI queda establecido, y es un limite duro

**La API no ofrece NINGUN desglose de entrega.** Probados contra
`/v1/ad_account/insights`: `breakdowns=query`, `breakdowns=placement`,
`breakdowns=country`, `breakdowns=device`, `breakdown=query`. Los cinco devuelven
HTTP 200 con **las mismas 2 filas** — el parametro se ignora en silencio.

Consecuencia: **no se puede saber a quien se le entrego el anuncio.** Ni por su lado
(no lo exponen) ni por el nuestro (nunca medimos si el visitante tenia un negocio
con citas). Los 112,53 EUR no compraron esa informacion.

## Estado honesto del diagnostico

Medido: 17.654 impresiones · 530 visitas · 6 pantallas de pago · 0 tarjetas ·
0 ventas · 112,53 EUR · segmentacion correcta sobre el papel.

Tres explicaciones siguen vivas y **ninguna esta probada**:
  1. el volumen fue diminuto (6 pantallas de pago no son una muestra);
  2. la pagina/oferta no cierra;
  3. la entrega no respeto las pistas de contexto.

**Forma de distinguirlas sin gastar un euro:** llevar a la MISMA pagina trafico
cualificado que controlemos nosotros (contacto a mano con salones). Si duenos de
salon elegidos a dedo tampoco compran, el problema es la pagina/oferta (2). Si
compran, era entrega o volumen (1 o 3). Es la unica prueba que separa las tres y
cuesta tiempo, no dinero.
