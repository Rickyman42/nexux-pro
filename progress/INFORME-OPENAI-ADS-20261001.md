# Informe: campaña de OpenAI Ads (ChatGPT Ads), septiembre 2026

**Cuenta:** Nexux Innovación Digital · `adacct_6a984fa34ad88194967899cbb7df53b0`
**Administradora:** arteenpixel@gmail.com
**Redactado:** 1-oct-2026. Cifras de la campaña re-medidas ese día contra la API de OpenAI.
**Para qué sirve:** tener en un solo sitio qué se pagó, qué falló por parte de OpenAI, qué falló
por nuestra parte y qué se debe de verdad, por si OpenAI reclama dinero.

---

## 1. Resumen en seis líneas

1. Se gastaron **137,89 € (sin IVA)** en dos campañas: **557 clics y 0 ventas**.
2. **OpenAI sí falló en cosas concretas y demostrables:** bloqueó la entrega 3 días por un cobro,
   su soporte dijo una cosa y la contraria en 48 minutos, su informe devuelve ceros sin avisar y
   no deja saber a quién se enseña el anuncio.
3. **Lo que NO se puede sostener es que fueran robots.** Nuestro propio análisis del 18-19 sep
   demostró que las visitas eran personas que pulsaron el anuncio.
4. **Parte del fracaso fue nuestro** (sección 5), y OpenAI lo ve en su propio panel.
5. **La cuenta cuadra.** El "descuadre de 18,90 €" que anotamos el 19-sep era el IVA: no existe.
6. **Lo que queda por pagar son 47,89 € + IVA = 57,95 €**, por clics que sí se entregaron. Lo que
   se sostiene no es dejar de pagar, sino **pedir por escrito que lo perdonen** con las quejas de
   la sección 3, que además son las mismas que publica la prensa del sector (3.4). Mensaje listo
   en la sección 9.

---

## 2. Qué se contrató y qué se pagó

Re-medido el 1-oct-2026 en la API (`GET /v1/ad_account/insights`, zona horaria Europe/Madrid):

| Campaña | Tipo | Días con gasto | Impresiones | Clics | "Conversiones" | Gasto sin IVA | Coste/clic |
|---|---|---|---|---|---|---|---|
| Conversiones de OPENAI_CPC_ES_NEXUX29_10D_202609 | Conversiones | 9 → 18 sep | 17.654 | 542 | 4 | 112,80 € | 0,21 € |
| OPENAI_CPC_ES_NEXUX29_10D_202609 | Clics | 8 sep | 2.200 | 15 | 0 | 25,09 € | 1,67 € |
| **Total** | | | **19.854** | **557** | **4** | **137,89 €** | 0,25 € |

- Las dos campañas están **en pausa** (API, 1-oct). Última acción en el historial de la cuenta:
  **pausa el 18-sep a las 21:25**. Desde entonces no ha corrido nada ni se ha generado gasto.
- Las 4 "conversiones" no son ventas: son personas que tocaron el botón de pagar (ver 5.1).
  **Ventas reales en Stripe: 0.**

### Las cuentas, con el IVA

Las facturas llevan IVA del 21%: 18,15 € son 15 € + IVA, y 36,30 € son 30 € + IVA.

| Fecha | Factura | Base | IVA 21% | Total cobrado |
|---|---|---|---|---|
| 8-sep | INV-8KYLODLW-000001 | 15,00 € | 3,15 € | 18,15 € |
| 13-sep | INV-8KYLODLW-000002 | 15,00 € | 3,15 € | 18,15 € |
| 13-sep | INV-8KYLODLW-000003 | 30,00 € | 6,30 € | 36,30 € |
| 14-sep | INV-8KYLODLW-000004 | 30,00 € | 6,30 € | 36,30 € |
| | **Cobrado** | **90,00 €** | **18,90 €** | **108,90 €** |

```
Gasto total (API, sin IVA)        137,89 €
Ya facturado (base)              − 90,00 €
Pendiente (base)                   47,89 €   <- lo que decía el panel el 19-sep: CUADRA
IVA 21% sobre el pendiente       + 10,06 €
Pendiente con IVA                  57,95 €
```

**Coste total de la aventura: 166,85 € con IVA** (108,90 ya pagados + 57,95 pendientes).
El panel preveía cobrar el pendiente el **30-sep** a la Visa ••••7800. **Sin confirmar si se cobró**
(ver sección 8).

> Corrección a lo anotado el 19-sep: se dejó escrito un "descuadre de 18,90 € sin explicar".
> Se comparó el gasto SIN IVA con lo cobrado CON IVA. Los 18,90 € son exactamente el 21% de
> 90 €. No hay descuadre.

---

## 3. Quejas legítimas contra OpenAI (con prueba)

Ninguna de estas da derecho a devolución por sí sola: son fallos del producto y del servicio
que conviene dejar por escrito.

### 3.1 La entrega se bloqueó 3 días, y el soporte se contradijo

Correos en arteenpixel@gmail.com, en orden:

```
 8-sep         Factura 000001 pagada (18,15 €)
 8-sep         "Your Ads payment failed ... ads serving has been paused"
 9-sep         "Your Ads payment failed ... ads serving has been paused"
10-sep         Abrimos caso: saldo 15,25 € por encima del umbral de 15 €
11-sep         Caso 14783985 (Uzair): "ad delivery is currently blocked because the required
               threshold payment has not completed successfully" ... "we have referred the
               account for further billing review"
12-sep         Tercer aviso "Your Ads payment failed"; abrimos segundo caso
13-sep         Facturas 000002 y 000003 pagadas
14-sep         Factura 000004 pagada
15-sep 13:45   Caso 14934138 (Rui): "The account is active and eligible to serve ... There is
               no current account-level billing or serving block"
15-sep 14:33   Ads Manager: "Your ads are currently paused because your ad account still
               needs to be verified"          <- 48 minutos después de lo anterior
15-sep 14:37   "Your Ad Account Has Been Verified"
```

Gasto diario (Panel > Facturación > Actividad):

```
 8-sep 25,09 · 9-sep 5,16 · 10-sep — · 11-sep — · 12-sep — · 13-sep 43,70 · 14-sep 26,13
15-sep 17,81 · 16-sep 14,06 · 17-sep 3,23 · 18-sep 2,71          Total 137,89 €
```

**Qué demuestra:** la campaña nunca corrió una prueba limpia. Se cortó 3 días por un cobro que
la tarjeta pagó en cuanto se reintentó, y el 15-sep se volvió a pausar por una verificación que
soporte acababa de decir que no hacía falta. Los avisos iban a un buzón que nadie leía, y eso es
nuestro; pero la contradicción de soporte es suya.
**Qué no demuestra:** que sin esos cortes hubiera habido ventas. Los días bloqueados no se
cobraron, así que no hay dinero que reclamar por ellos.

### 3.2 El informe de OpenAI devuelve ceros sin avisar

Comprobado el 19-sep con control: el mismo día 13-sep pedido seis veces a la API.
Ventana alineada a medianoche de Madrid → **238 clics y 35,93 €**. La misma ventana desplazada
una hora → **0 clics y 0,00 €**, con respuesta HTTP 200 y ningún mensaje de error.

Nuestro parte diario automático dijo "0 clics, 0 €" en 6 de 11 mañanas mientras se estaba
gastando dinero. Un anunciante que se fíe del informe no sabe cuándo se le está cobrando.
(Arreglado en nuestro lado el 19-sep, commit `e7905ae`.)

### 3.3 No se puede saber a quién se le enseñó el anuncio

- La documentación de OpenAI dice que el anunciante recibe información **agregada y no
  identificativa**; las señales con las que se decide a quién mostrar el anuncio (la
  conversación, la ubicación, el historial) **se quedan dentro de ChatGPT**.
- Pedidos los desgloses por consulta, emplazamiento, país y dispositivo, devolvieron siempre la
  misma fila. (OpenAI anunció el 16-sep un desglose por plataforma, cuando ya estaba gastado
  casi todo.)
- Los públicos personalizados existen, pero su propia ayuda exige **25.000 usuarios emparejados**
  para usarlos para incluir. Un negocio pequeño no llega: en la práctica no se puede elegir.
- **No existe programación por horas** en ningún nivel: solo fecha de inicio y de fin.

**Qué demuestra:** se pagaron 137,89 € sin poder auditar qué público se compró.
**Qué no demuestra:** que el público fuera malo. No se puede saber, y ese es el problema.

### 3.4 No es un caso aislado: es la queja general del sector

Buscado el 1-oct-2026 en prensa especializada:

- **Search Engine Journal, 8-sep-2026** ("6 Months Into ChatGPT Ads, Advertisers Still Don't Know
  What 'Good' Looks Like"): la propia OpenAI reconoce que no tiene referencias de rendimiento por
  sector ni tipo de campaña. Una anunciante descubrió por su cuenta que solo 5 de 146 visitantes
  identificables encajaban con su cliente ideal, algo que el panel "no ofrecía forma de descubrir".
  Otro anunciante (Hostinger) habla de "calidad de tráfico inconsistente".
- **Search Engine Land** ("Advertisers are testing ChatGPT ads — but uncertainty remains high"):
  los anunciantes no reciben datos de audiencia ni saben qué preguntas hacían los usuarios cuando
  salió su anuncio.
- **eMarketer** ("ChatGPT advertisers push for prompt-level reporting and stronger placement
  insights"): los anunciantes están pidiendo justo lo que aquí faltó.
- **MediaPost / Yahoo Finanzas** ("Data Reveals ChatGPT Ads Not Performing"): los primeros
  anunciantes no consiguen demostrar que los anuncios funcionaran.

Fuentes:
- https://www.searchenginejournal.com/6-months-into-chatgpt-ads-advertisers-still-dont-know-what-good-looks-like/587583/
- https://searchengineland.com/advertisers-are-testing-chatgpt-ads-but-uncertainty-remains-high-474729
- https://www.emarketer.com/content/chatgpt-advertisers-push-prompt-level-reporting-stronger-placement-insights
- https://www.mediapost.com/publications/article/417528/data-reveals-chatgpt-ads-not-performing.html

**Ojo con una de ellas:** Tech Times (1-sep) publica que algunas agencias ven clics en el panel que
su analítica no encuentra. **En nuestro caso no pasó** (94% de los clics llegaron, sección 4). No
se debe citar como si nos hubiera pasado.

---

## 4. Lo que NO se puede sostener: "eran robots"

La sospecha salió de ver visitas que "duraban 0,07 segundos" y no hacían nada. Se investigó a
fondo el 18-19 sep y **la conclusión fue la contraria**:

- Cada clic del anuncio trae en la dirección un código de OpenAI (`oppref`) que lleva dentro la
  hora en que se generó. De **408** llegadas, **ninguna** cargó la página antes de **3,88
  segundos**; la mediana fue **51 segundos**. Un robot o una precarga entra a ~0 segundos.
- **406 códigos distintos** en 420 sesiones: nadie repitiendo el mismo clic.
- En las visitas "mudas", 190 de 200 eran móviles, con unas 60 resoluciones de pantalla
  distintas y 78% en español de España. Una granja de robots sería uniforme.
- **Clics cobrados vs. llegadas reales (14-18 sep): 281 contra 264 = 94%.** El 6% que falta es lo
  normal (bloqueadores, gente que cierra antes de cargar). **No se pagaron clics fantasma.**

**¿Y los "milisegundos"?** Eran un fallo de nuestra medición: la web no medía el tiempo que
alguien pasa en la página. Anotaba la llegada y, al instante, un segundo aviso; los "0,07 s" eran
el hueco entre esos dos avisos. Quien lee la primera pantalla 30 segundos sin bajar deja
**exactamente el mismo rastro** que quien cierra al momento.

Si se le dice a OpenAI "nos habéis cobrado robots", pueden contestar con sus propios registros de
esos mismos códigos, y las quejas que sí son ciertas pierden fuerza.

---

## 5. Lo que fue nuestro (y OpenAI ve en su panel)

1. **La "conversión" que le pedimos que buscara era un toque de botón**, no un pago. El evento
   `checkout_started` saltaba al pulsar "pagar", antes de llegar a Stripe. El algoritmo optimizó
   hacia eso. (Visto en el código de producción el 16-sep.)
2. **El píxel de OpenAI solo se cargaba si aceptaban las cookies.** De 118 personas que vieron el
   aviso, 7 aceptaron. La gente pulsaba "pagar" a los ~6 segundos y aceptaba (si lo hacía) a los
   12-25: cuando llegaba el permiso, la conversión ya había pasado. OpenAI casi no recibió señal.
3. **Encendíamos y apagábamos la campaña cada día** con un programa propio (21:00-03:00). La
   entrega a las 21:00 cayó tres días seguidos: 1.148 → 164 → 11 impresiones.
4. **El anuncio llevaba a la ficha de producto, no a la demo.** Unas 530 personas llegaron;
   **479 vieron una sola página y se fueron**; solo 4 llegaron a probar la demo.
5. **Los avisos de OpenAI iban a un buzón que nadie leía** hasta el 19-sep.

Esto no hace bueno al producto de OpenAI, pero explica una parte del 0 ventas. La frase "no fue
porque nosotros lo tuviéramos mal hecho" **no aguanta**: los puntos 1 y 2 aparecen en su propio
panel ("Event Quality Score").

---

## 6. Posición realista sobre el dinero

- **Los 108,90 € ya cobrados:** son clics entregados que llegaron a la web (94% medido). Cobran
  por clic entregado, no por resultado, y no hay política pública de devolución por bajo
  rendimiento. **No hay base para pedirlos de vuelta.**
- **Los 57,95 € pendientes (47,89 € + IVA):** son del mismo tipo de clics. **Se deben.** Si OpenAI
  los reclama, lo correcto es pagarlos y comprobar que la factura sea exactamente esa cifra.
- **Devolución por la tarjeta (chargeback): no.** Es un servicio que se prestó; el banco daría la
  razón al comercio y OpenAI cerraría la cuenta.
- **Lo que protege de verdad:** saber la cifra exacta (este informe) para que no se cobre ni un
  euro de más, y tener por escrito las quejas de la sección 3 por si hiciera falta en el futuro.
- **Decisión de Ricardo (1-oct): no quiere pagar el pendiente.** La vía que se sostiene NO es
  dejar de pagar, sino **pedir por escrito que lo perdonen** (un "crédito de cortesía"), con las
  quejas de la sección 3, que son todas ciertas. Es una petición normal en un producto en pruebas
  (beta) y puede salir bien. Si dicen que no, se paga.
- **Por qué no dejar de pagar sin más:** (1) OpenAI ya avisaba en su documentación de que el
  anunciante solo recibe datos agregados, así que "no nos dieron datos de audiencia" no es romper
  lo prometido; lo aceptamos al contratar. (2) El cobro es automático a la Visa ••••7800: si el
  30-sep ya pasó, el dinero ya se cobró. (3) Si no se paga, la cuenta queda bloqueada y la deuda
  sigue ahí. Por 58 € se arriesga mucho más de lo que se gana.
- **Sin confirmar (hipótesis, no verificado):** OpenAI está cobrando IVA español al 21%. Si la
  empresa tiene NIF-IVA intracomunitario dado de alta en el censo (ROI), registrarlo en la cuenta
  haría que dejaran de cobrarlo (inversión del sujeto pasivo). Preguntarlo al gestor antes de
  tocar nada.

---

## 7. Inventario de pruebas (dónde está cada una)

| Prueba | Dónde |
|---|---|
| Cifras de las dos campañas, estado "paused", historial de acciones | API `api.ads.openai.com/v1/campaigns`, `/v1/ad_account/insights`, `/v1/audit_logs` (re-medido 1-oct) |
| Facturas 000001 a 000004 | Buzón arteenpixel@gmail.com |
| Avisos "payment failed" 8, 9 y 12-sep | Buzón arteenpixel@gmail.com |
| Caso 14783985 (bloqueo) y caso 14934138 (contradicción) | Buzón arteenpixel@gmail.com |
| Avisos de pausa por verificación 15-sep 14:33 y 14:37 | Buzón arteenpixel@gmail.com |
| Gasto día a día y saldo pendiente | Panel ads.openai.com > Facturación > Actividad / Resumen |
| Análisis de los códigos `oppref` y cruce 281/264 | Pi: `~/nexux-pro/progress/ANUNCIO-TRABAJO-EN-CURSO.md` |
| Ceros silenciosos de la API (prueba con control) | Mismo fichero, "La causa raíz de que los números bailen" |
| Embudo en la web (530 / 479 / 4 / 10 / 0) | Pi: Umami (`umami-db-1`) y `progress/REGISTRO.md`, 19-sep |
| Ventas reales: 0 | Stripe |

---

## 8. Pendiente (lo tiene que hacer Ricardo; no se puede desde aquí)

> **1-oct, dicho por Ricardo:** el cobro del 30-sep **no se hizo** porque cancelaste la Visa
> ••••7800. El saldo de 57,95 € sigue pendiente. Cancelar la tarjeta no cancela la deuda: solo
> impide el cobro automático. Por eso conviene mandar la petición de la sección 9 **ya**, antes de
> que OpenAI reclame el impago, y no después.

1. **Entrar en ads.openai.com > Facturación** y hacer captura de **Resumen** y **Actividad**:
   confirmar el saldo pendiente y si hay alguna línea nueva después del 18-sep.
2. **Descargar en PDF** las facturas 000001-000004 y la 000005 si ya existe (debería ser
   47,89 € + IVA = 57,95 €; si es otra cifra, eso sí se reclama).
3. **Guardar en una carpeta** los correos de los casos 14783985 y 14934138 y los avisos del
   8, 9, 12 y 15-sep. Si la cuenta se cierra, el buzón es lo único que queda.

---

## 9. Petición a soporte: que perdonen el saldo pendiente

> **ENVIADA el 1-oct-2026 a las 0:48** por Ricardo desde arteenpixel@gmail.com, como respuesta en el hilo del caso 14934138 a ads-support@openai.com. Texto exactamente el de abajo. Comprobado en la carpeta Enviados. Pendiente: su respuesta.

Todo lo que dice es cierto y está probado en este informe. No dice "robots" ni "descuadre".
El saldo sigue sin cobrar (tarjeta cancelada), así que va tal cual.

> Hello,
>
> We ran two campaigns on ad account adacct_6a984fa34ad88194967899cbb7df53b0 between 8 and 18
> September 2026 (€137.89 spend, 557 clicks, 0 sales). Both have been paused since 18 September
> and we will not resume them. We are asking you to waive the outstanding balance of €47.89
> (plus VAT) as a courtesy credit, for these reasons:
>
> 1. The campaign never ran cleanly. Ad delivery was blocked from 10 to 12 September over a
>    threshold payment (case 14783985). On 15 September at 13:45 support stated there was no
>    block (case 14934138); at 14:33 the account was paused again pending verification.
> 2. Your reporting was unreliable. The Insights API returns zero clicks and zero spend, with
>    HTTP 200 and no error, when the requested window is not aligned to local midnight. The same
>    day returned 238 clicks and €35.93 when aligned, and 0 / €0.00 when shifted by one hour. Our
>    daily report showed zero spend on 6 of 11 mornings while we were being charged.
> 3. We could not learn anything about who saw our ads. Breakdowns returned a single row, and
>    Custom Audiences require 25,000 matched users, which a small business cannot reach. After
>    €137.89 we still cannot tell whether our ads reached our target customers. This is a
>    widely reported limitation of the beta, not an isolated case.
>
> We understand this is a beta product. That is exactly why we are asking for a courtesy credit
> rather than disputing the charges: we paid €108.90 to test it, and the test could not produce
> usable information.
>
> Thank you,
> Ricardo — Nexux Innovación Digital
