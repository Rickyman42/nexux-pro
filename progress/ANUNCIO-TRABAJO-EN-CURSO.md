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
