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
