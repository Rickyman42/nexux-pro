# ESTADO DEL ANUNCIO DE 75 SEGUNDOS

> Foto del 28-ago-2026. **Empieza por aquí**: los otros ocho documentos de esta carpeta
> cuentan el *cómo*, este cuenta el *dónde estamos*.
> Si algo de aquí no cuadra con lo que ves, gana lo que veas: actualiza esto.

---

## 1. DÓNDE ESTAMOS EN UNA LÍNEA

**Los 14 planos rodados, montados y rotulados: 55,71 s.** El entregable es
`ANUNCIO-56s-con-rotulos.mp4`. Faltan la música y la voz — y hay **dos fallos abiertos** que se
ven en pantalla (§ 4.1). Hasta que se cierren, esto no se publica.

---

## 2. LOS 14 PLANOS

Duraciones y resoluciones **medidas** sobre los ficheros, no estimadas.

| # | Qué es | Estado | Fichero | Dura | Resolución |
|---|---|---|---|---|---|
| P1 | Manos limando uñas | ✅ | `P01-manos-manicura.mp4` | 8,00 s | 1280×720 |
| P2 | El móvil quieto en el mostrador | ✅ | `P02-movil-mostrador.mp4` | 8,00 s | 1280×720 |
| P3 | La cabina, ella trabajando | ✅ ⚠️ | `P03-cabina-mensajes.mp4` | 8,00 s | 1280×720 |
| P4 | La pantalla que se apaga sola | ✅ | `P04-pantalla-se-apaga.mp4` | 8,00 s | 1280×720 |
| P5 | El final del día, negocio vacío | ✅ | `P05-lena-final-del-dia.mp4` | 8,00 s | 1280×720 |
| P6 | La mano con el móvil apagado | ✅ | `P06-mano-movil-apagado.mp4` | 8,00 s | 1280×720 |
| P7 | La conversación de WhatsApp | ✅ | `P07-en-movil.mp4` | 11,00 s | 1280×720 |
| P8 | El CRM: la cita entrando **y el ROI del bot** | ✅ | `P08-agenda-y-roi.mp4` | 11,50 s | **1920×1080** |
| P9 | Alguien probándolo, curioso | ✅ | `P09-probando-el-movil.mp4` | 8,00 s | 1280×720 |
| P10 | Un pulgar abriendo WhatsApp | ✅ | `P10-pulgar-whatsapp.mp4` | 8,00 s | 1280×720 |
| P11 | Lena apoyada en el mostrador | ✅ | `P11-lena-mostrador.mp4` | 8,00 s | 1280×720 |
| P12 | El negocio con clientes, vida | ✅ | `P12-negocio-con-clientes.mp4` | 8,00 s | 1280×720 |
| P13 | Lena mirando su móvil, seria | ✅ | `P13-lena-mirando-movil.mp4` | 8,00 s | 1280×720 |
| P14 | Cierre con el QR | ✅ | `P14-cierre-qr.mp4` | 5,00 s | 1280×720 |

Todos en `~/brand-assets/video/anuncio-75s/` en la Pi, con copia en
`C:\Users\Nexux\Desktop\creatives\anuncio-75s\` (esas llevan prefijo de orden: `01_`, `02_`…).

⚠️ **P3 está a revisión.** Es un masaje, y el negocio del anuncio es un centro de estética
*neutro*. Ricardo decidió el 25-ago dejarlo y verlo con el montaje entero. Si canta, se rehace
con una manicura o un facial: mismo bloqueo de manos, 12 créditos.

### Detalles que hay que tener presentes al montar
- **El P8 es el único en 1080p.** Los demás son 720p, que es lo que da Flow. No pasa nada,
  pero si se exporta a 1080 el resto sube escalado.
- **El P7 no tiene pista de audio.** Los planos de Flow sí (AAC), aunque suenan casi mudos.
- **El P7 dura 11 s** porque la conversación necesita ese tiempo; la escaleta le daba 10.
- **El P8 pasó de 8 a 11,5 s** al ensancharlo con la segunda pantalla. La versión de una sola
  pantalla sigue ahí como `P08-crm-cita-entra.mp4` por si se prefiere la corta.

### Por qué el plano 8 enseña dos pantallas y no tres
Se comprobaron las siete secciones del panel. **Clientes y Chats están vacíos**, incluso después
de que el bot acabe de reservar una cita: en Clientes pone «los clientes que reserven citas a
través de tu bot aparecerán aquí» y no aparece nadie. Una pantalla vacía en un anuncio es peor
que no enseñarla. ⚠️ **Eso es un fallo de producto, no del rodaje**, y hay que mirarlo aparte:
un cliente que entre a ver su lista se encontrará lo mismo.

Las dos que sí sirven son la agenda y el **ROI del bot** (~633 € generados, 95 min ahorrados).
La segunda es la que vende.

⛔ El Dashboard tiene detalles que en un anuncio no lucen — «Copia de seguridad: sin copia» en
rojo y «Telegram: pendiente» en naranja. Por eso el plano se acerca al bloque del ROI y los deja
fuera del encuadre.
- `P07-conversacion.mp4` (720×1560, vertical) es la pantalla suelta, **material intermedio**.
  Lo que va al montaje es `P07-en-movil.mp4`.

---

## 3. EL MONTAJE

**El montaje final vive en el proyecto de CapCut `0829`**, para que Ricardo pueda
modificarlo cuando quiera (decisión suya del 29-ago). Los retoques que exigen precisión
al fotograma se hacen fuera, en la Pi, y entran en CapCut como clips ya cortados.

```
Pi:  python3 pipeline/montar-ritmo.py   -> 14 clips recortados y con movimiento (/tmp/ritmo)
     python3 pipeline/srt.py            -> ROTULOS.srt con los textos y sus tiempos
Windows: ambos en C:\Users\Nexux\Desktop\creatives\anuncio-56s\
CapCut:  proyecto 0829, 55,71 s
```

`rotular.py` sigue existiendo y sirve para sacar una copia con los rótulos quemados sin
abrir CapCut (útil para enseñar el anuncio rápido), pero **no es el entregable**.

### Por qué dura 55,71 s y no 52
El primer montaje con ritmo daba 52 s. Al medir si los rótulos del guion caben en cada
plano, tres del acto 4 salían a **4,4 palabras por segundo**; por encima de 3 el
espectador no termina de leer antes del corte. Se les dio el tiempo que pide su texto:
P9 y P10 a 3,5 s, P11 a 4,0 s, P12 a 3,2 s. Son los planos donde se responde a las
objeciones, o sea donde se cierra la venta: ahogarlos para ahorrar cuatro segundos es
tirar el anuncio.

### Las dos decisiones de edición
1. **El tiempo se reparte según lo que hay que entender, no a partes iguales.** Unas
   manos limando se leen en 2 s; la conversación de WhatsApp necesita 9 y el CRM 7.
2. **Movimiento donde no lo había.** Los clips de Flow son estáticos. Un acercamiento
   del 4 % a lo largo del plano no se percibe como efecto pero quita la sensación de
   foto fija. Se alterna acercar y alejar, y se deja quieto lo que ya se mueve solo
   (P7, P8, P12).

### Los rótulos, dentro de CapCut
Se importan como **una pista de subtítulos**, así que los 13 quedan editables en la
aplicación y con sus tiempos exactos, sin colocar veinte cuadros de texto a mano.

- Los siete planos del acto 4 llevan **la duda y la respuesta como dos líneas del mismo
  rótulo**. La idea era dos pistas para dar a la duda un gris más pequeño, y es posible
  (ver la trampa del cabezal, abajo), pero de momento las dos frases salen del mismo
  tamaño. **Queda pendiente si se quiere recuperar esa jerarquía.**
- Estilo actual: tamaño **6** y el tercer preset de la fila (blanco con contorno). Se
  probó sobre el plano del CRM, que es fondo blanco, y sobre los planos oscuros: se lee
  en los dos.
- **La tipografía sigue siendo la del sistema, no Geist.** Geist está instalada en
  Windows (`%LOCALAPPDATA%\Microsoft\Windows\Fonts`, las tres variantes) y CapCut
  debería ofrecerla, pero su desplegable de fuentes no responde bien; hay que
  seleccionarla a mano. Es un clic.

### 🔴 Tres trampas de CapCut, todas pisadas el 29-ago
1. **Un SRT se inserta donde esté el cabezal, no en sus tiempos.** Con el cabezal al
   final, los 13 rótulos se colocaron *detrás* del vídeo y el montaje pasó de 55 s a
   106 s. **Poner el cabezal en 0 justo antes de importar** — y como último paso, porque
   un clic en zona vacía de la línea de tiempo lo manda al final.
2. **`Ctrl+A` selecciona todos los clips**, nunca el texto de un campo.
3. **`BackSpace` / `Supr` borran el clip seleccionado** aunque creas que estás
   escribiendo en un campo numérico. Así se borró un rótulo sin darse cuenta. Para los
   números, **usar las flechitas del selector**, no el teclado.

### 🔴 Y una de ffmpeg, del mismo día: un PNG sin `-loop 1`
Al generar la copia con rótulos quemados, el primer pase dio un vídeo de **duración
exacta, fotogramas exactos y cero errores**… y **sin un solo rótulo encima**. Un
`-i rotulo.png` sin `-loop 1` es un stream de UN fotograma que existe en t=0; el fundido
de entrada arranca en 0,3 s, ese fotograma se queda transparente del todo y `overlay` lo
repite invisible el resto del plano.

Se arregla con `-loop 1 -framerate 24 -t <duración> -i rotulo.png`. Y la lección va más
lejos: **verificar duración y fotogramas no prueba que se haya pintado nada**.
`rotular.py` mide ahora el brillo del quinto inferior antes y después de superponer, y
aborta si no se oscurece.

### El proyecto viejo
`0825` sigue guardado, con los 14 planos **sin recortar** (1:47). No se ha tocado.

---

## 4. LO QUE FALTA, EN ORDEN

### 4.1 🔴 Dos fallos que se ven en pantalla

**a) El plano del CRM se contradice con su propio rótulo.** El rótulo dice «Y la puso en tu
agenda. Sola.» y el dashboard marca **CITAS HOY: 0**. Al lado, «Próxima cita: jue, 27 de agosto»,
una fecha ya pasada. Los datos se sembraron el 26 y el plano se grabó con ellos. Quien mire el
número mientras lee la frase ve que no cuadran.
**Arreglo:** volver a sembrar con `seed-agenda.mjs` en la fecha del día y regrabar con
`crm-dos-estados.cjs` + `p8-agenda-y-roi.py`. No gasta créditos de Flow.

**b) La conversación de WhatsApp no se lee.** El P7 dura 9 s precisamente porque hay que leerla,
y a ese encuadre el móvil ocupa un tercio del ancho: se ve que hay mensajes, no lo que dicen.
Además el mensaje de Lara es un muro de texto — la misma verborrea que se le mandó corregir a
Codex, aquí visible en imagen.
**Dos salidas:** acercar el encuadre hasta que el chat se lea (rehacer `p7-encajar.py`, sin
regrabar nada), o bajar el plano a 4-5 s y aceptar que la conversación es atmósfera y no
lectura. La primera vende el producto; la segunda es gratis. **Pendiente de Ricardo.**

### 4.2 Lo que falta para publicar
1. **Música.** El audio de Flow es casi mudo: los picos miden 0,004 sobre 1.
2. **Voz.** Con **ElevenLabs**, que tiene crédito. Sustituye a MiniMax, que era el plan viejo.
3. **Dos montajes**: sin voz para la web, con voz para redes.
4. **Decidir CapCut o Pi** como sala de montaje (§ 3).

### 4.3 Fuera del anuncio, pero descubierto rodándolo
⚠️ **Clientes y Chats del CRM están vacíos** incluso después de que el bot reserve una cita. Es
un **fallo de producto, no del rodaje**: un cliente que entre a ver su lista se encuentra lo
mismo. Por eso el plano 8 enseña dos pantallas y no tres.

---

## 5. LO QUE SE HIZO SIN GASTAR UN CRÉDITO

Esto es lo que no se ve en los ficheros de vídeo y cuesta rehacer si se pierde. Todo en
`pipeline/`, todo re-ejecutable.

| Qué | Con qué | Por qué existe |
|---|---|---|
| El móvil encendiéndose y vibrando (P3) | `glow-movil.py`, `pulso-movil.sh`, `zumbido.sh` | Flow pintaba texto inventado en la pantalla y hacía saltar el teléfono por la mesa |
| El acercamiento sobre la cita (P8) | `p8-movimiento.py` | En plano general la cita ocupa el 7 % del ancho: no se lee en un móvil |
| La pantalla de la conversación (P7) | `p7-pantalla.py` + `p7-grabar.cjs` | Se graba pidiéndole a la página el estado del segundo *t*, no con el reloj: sale idéntico cada vez |
| Encajarla en el móvil (P7) | `p7-encajar.py` | Busca la pantalla en los 192 fotogramas y deforma la imagen a sus cuatro esquinas |
| La tarjeta de cierre con QR (P14) | `cierre.py`, `p14-cierre.sh` | QR verificado con un lector de verdad sobre el vídeo ya comprimido |
| La agenda del rodaje | `seed-agenda.mjs` | Siembra 11 citas creíbles con la misma función que usa el producto |
| Una conversación real sin teléfono | `conversa-rodaje.mjs` | Atraviesa `handleMessage()`: mismo prompt, misma IA, mismo Google Calendar |
| Las dos capturas del CRM | `crm-dos-estados.cjs` | El panel real del cliente, antes y después de que entre la cita |
| Limpiar lo sembrado | `limpia-pruebas.mjs` | Borra las citas de prueba de Google Calendar **y** de `appointments.json` |

---

## 6. DECISIONES VIVAS

- **El negocio es Centro Lena**, centro de estética neutro en Móstoles. Ficha completa en
  `NEGOCIO.md`. Se eligió con datos, no por gusto: 1.063 de 1.458 salones scrapeados no tienen
  reserva online, y en una clínica dental hay recepcionista, así que el dolor del anuncio
  («nadie contesta») se desactivaría solo.
- **El personaje fijo se llama `Lena`** y vive en el proyecto de Flow. Sale en P5, P11 y P13.
  Escribir `@Lena` de una tirada **no funciona**: hay que teclear la arroba sola, elegirla de la
  lista y escribir detrás.
- **Ninguna IA toca una pantalla de Nexux.** Las pantallas del producto son captura real.
- **Los rótulos van en CapCut**, nunca en Flow: el modelo se inventa texto.
- **La pantalla del P7 es una recreación; los textos no.** Salen de lo que contestó Lara de
  verdad. Va deliberadamente **sin el logotipo ni el nombre de WhatsApp**: poner una marca ajena
  en un anuncio propio lo decide Ricardo.
- **Nada del rodaje se queda abierto.** El calendario que se compartió para grabar el P8 se
  cerró el 25-ago y se comprobó que el feed público devuelve 404.

---

## 7. LOS OTROS DOCUMENTOS

| Fichero | Para qué |
|---|---|
| `GUION.md` | **La pieza aprobada. No se toca.** Los cinco actos |
| `PLAN-RODAJE.md` | Cómo se rueda cada plano, y los textos de los rótulos |
| `NEGOCIO.md` | Centro Lena: servicios, profesionales, horarios |
| `PROMPTS-FLOW.md` | Los prompts de los planos que faltan, listos para pegar |
| `FLUJO.md` | Dónde vive cada cosa, reglas que no se saltan y **trampas ya pisadas** |
| `FLOW.md` | Qué hace Flow, qué cuesta y qué no se le pide |
| `METODO.md` | El método Gemini Notebook + Flow del que salió todo esto |
| `MASTER-PROMPT.md` / `SALIDA-NOTEBOOK.md` | El motor de Notebook y su salida en crudo |

**Si sólo vas a leer dos:** este y `FLUJO.md`. El segundo es el que evita repetir errores que
ya costaron horas.
