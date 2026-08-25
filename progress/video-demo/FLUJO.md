# FLUJO DE TRABAJO — anuncio de 75 s

> Cómo se produce este vídeo, paso a paso, para que no dependa de la memoria de nadie.
> El guion manda: `GUION.md`. La escaleta: `PLAN-RODAJE.md`. El motor: `METODO.md`.

---

## 1. DÓNDE VIVE CADA COSA

| Qué | Dónde | Se ve desde Windows en |
|---|---|---|
| Planos terminados, numerados por escena | `~/brand-assets/video/anuncio-75s/` en la Pi | **`Y:\brand-assets\video\anuncio-75s\`** |
| Scripts que los producen | `~/nexux-pro/progress/video-demo/pipeline/` | con git detrás |
| Guion, plan, método, prompts | `~/nexux-pro/progress/video-demo/` | con git detrás |
| Copias de trabajo | `C:\Users\Nexux\Desktop\creatives\20260824_video-demo\` | — |
| Proyecto de montaje | CapCut de escritorio, proyecto `0825` | — |

**La Pi está montada como unidad `Y:`.** Todo lo que se genera aparece ahí solo: CapCut abre
los planos directamente, sin copiar, sin subir a ninguna nube.

**Nombres:** `P03-…`, `P11-…`, `P14-…` con dos dígitos, para que CapCut los ordene solos.

---

## 2. LA CADENA, POR TIPO DE PLANO

### Los 11 que genera Flow
1. Personaje `@Lena` y la imagen de la cabina ya existen en el proyecto de Flow — **no se rehacen**.
2. Prompt del plano, con `@Lena` y la imagen de la cabina como ingredientes. La cabina es lo que
   hace que todos los planos parezcan el mismo local: describirlo con palabras NO basta, se
   comprobó.
3. Modelo **Omni Flash**, 16:9, 8 s, x1 → **12 puntos**. Es el más barato de los cuatro.
4. Descargar el clip y dejarlo en `~/brand-assets/video/anuncio-75s/` con su número.

### Los 2 de captura real
- **P7** — la conversación con Lara: `conversa-rodaje.mjs` lanza una conversación contra el motor
  real y `grabar-inbox.cjs` graba el panel del CRM mientras entra (se refresca cada 2 s, así que
  los mensajes aparecen en directo). Sin teléfonos.
- **P8** — la agenda: se graba **el CRM** (`nexux.pro/cliente/<id>`, pantalla Citas),
  no Google Calendar. El anuncio enseña nuestro sistema. Requiere la sesión de Ricardo.

### El de composición
- **P14** — el cierre: `cierre.py` compone la tarjeta y `p14.sh` la anima. **0 créditos.**

---

## 3. LOS EFECTOS QUE SE HACEN EN POST (0 créditos)

Flow no siempre da lo que hace falta, y regenerar cuesta puntos. Esto se resuelve en la Pi:

| Efecto | Script | Para qué |
|---|---|---|
| Pantalla del móvil encendiéndose | `glow-movil.py` + `pulso-movil.sh` | Los mensajes entrantes del P3 |
| Zumbido de los mensajes | `zumbido.sh` | Cuadrado al fotograma con la luz |
| Medir que un efecto ha entrado | `mide_audio.py` | Un filtro puede correr sin error y no aplicar nada |
| Acercamiento sobre la cita del P8 | `p8-movimiento.py` | En plano general la cita ocupa el 7% del ancho: no se lee |

**El audio que genera Flow es casi mudo** (picos de 0,004 sobre 1). El sonido de todos los planos
hay que ponerlo nosotros. No cuesta créditos, pero hay que contarlo en el tiempo de trabajo.

---

## 4. REGLAS QUE NO SE SALTAN

1. **Ninguna IA toca una pantalla de Nexux.** Las pantallas del producto son captura real. Si un
   plano necesita un móvil, va apagado y la pantalla se enciende en post.
2. **Los rótulos van en CapCut**, nunca en Flow: el modelo se inventa texto.
3. **Verificar midiendo, no mirando.** Y verificar la cosa correcta: el efecto del móvil pasó su
   comprobación de QR estando el fichero mal por otro lado (duraba 625 s en vez de 5).
4. **Antes de dar un plano por bueno:** duración, resolución, fotogramas, y una mirada al
   fotograma. Los cuatro. Un número correcto no salva una toma fea, y una toma bonita no salva
   un fichero roto.
5. **Nada del rodaje se queda abierto al público.** Para grabar el plano 8 se compartió el
   calendario de Centro Lena; eso lo deja además indexable en Google. Se cierra el mismo día,
   y la prueba no es la casilla: el feed `.../public/basic.ics` tiene que devolver **404**.
   Cerrado y comprobado el 25-ago (antes daba 200 con 38 eventos). Por lo mismo, las citas de
   prueba se siembran **sin teléfono**: ese campo se ve en el evento.

---

## 5. TRAMPAS YA PISADAS

**`zoompan` multiplica fotogramas.** Su parámetro `d` son los fotogramas de salida *por cada
fotograma de entrada*. Con `-loop 1 -t 5` entran 120 imágenes y salen 120×120: un vídeo de 625
segundos. Se le mete **una sola** imagen.

**`fade=t=in` entra desde negro.** Sobre una tarjeta clara es un fogonazo oscuro entre planos. Se
entra desde el color de fondo: una capa del propio crema que se desvanece encima.

**Una expresión de transparencia con `geq` puede no aplicar nada** y no dar error. El primer
intento del brillo del móvil terminó "bien" y la diferencia de brillo medida fue +0,1. Se hace con
`fade` sobre el canal alfa, que es más aburrido y funciona.

**El permiso de CapCut se rompe en cada actualización.** El menú de inicio apunta a un lanzador,
pero la ventana la abre `Apps\<VERSION>\CapCut.exe`. Hay un acceso directo llamado **"CapCut 8.5"**
que apunta al ejecutable real; el día que CapCut pase a la 8.6 hay que rehacerlo o el control
deja de ver la aplicación.

**CapCut web no sirve:** el plan gratuito da **1 byte** de almacenamiento en la nube. Se trabaja
con el CapCut de escritorio, que usa ficheros locales.

**Los fotogramas clave de CapCut, a mano, cuestan mas de lo que valen.** Poner la escala escribiendo
en el campo lo concatena con lo que ya hay (100 + 150 = 9999%), y `ctrl+a` no selecciona el texto
del campo: selecciona **todos los clips de la linea de tiempo**. El movimiento de camara se genera
en la Pi y llega a CapCut ya resuelto; CapCut se queda para ordenar planos, rotulos y sonido.

**El + de la miniatura inserta donde este el cabezal, no al final.** Si el cabezal esta en medio,
parte el clip que haya debajo. Antes de anadir: cabezal al punto exacto y comprobar el contador
(sale en 8:08 con un clic en la regla; se afina con las flechas).

---

## 6. CRÉDITOS

50 gratis al día, no se acumulan. A 12 puntos el clip de 8 s, salen **4 clips diarios**.
Quedan 9 planos por generar: **dos días y medio**.

Y una fecha a vigilar: el aviso de Flow decía que la bonificación diaria de 50 puntos para planes
de pago acababa el **31 de agosto**. No está claro si afecta al gratuito — mirarlo el día que
toque, no darlo por hecho.
