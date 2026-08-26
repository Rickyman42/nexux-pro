# PROMPTS DE FLOW — los 9 planos que faltan

> Listos para pegar. Salen de `PLAN-RODAJE.md` §5, corregidos con lo que ya se ha aprendido
> rodando y con la ficha `NEGOCIO.md` (Centro Lena, centro de estetica **neutro**).
> El guion no se toca. Si un plano no cuadra con esto, el equivocado es el plano.

## Lo que cambia respecto al borrador del plan

1. **Ningun movil con notificaciones generadas por IA.** En el P3 se intento y el modelo pinta
   texto inventado y una vibracion que hace que el telefono *salte* por la mesa. La pantalla se
   enciende **en post** con `glow-movil.py` y el zumbido con `zumbido.sh`. A Flow se le pide el
   movil **apagado y quieto**.
2. **Nada de masaje en los planos nuevos.** P3 y P11 ya son cabina y quedan a revision. Todo lo
   que se genere de ahora en adelante insinua manos, cara o unas: mas neutro y dentro del sector
   que de verdad estamos midiendo (73 % de 1.458 salones sin reserva online).
3. **Sin texto en ninguna parte.** Ni rotulos, ni marcas, ni pantallas legibles. Los rotulos van
   en CapCut.
5. **El personaje fijo ya existe y se llama `Lena`.** Esta creado en el proyecto de Flow y se
   invoca con `@Lena`. Sale en P5, P11 y P13. En P1 y P2 no: ahi solo se ven manos.

4. **Flow entrega 8 s.** La escaleta pide 4-6 s por plano: se recorta en el montaje. No se pide
   una duracion corta, porque el clip cuesta lo mismo y sobrar es mejor que faltar.

---

## Orden de disparo — 12 creditos el clip, 50 al dia = 4 clips

| Dia | Planos | Por que en este orden |
|---|---|---|
| 1 | **P6**, P2, P1, P13 | P6 es el critico: si sale con pantalla o con camara movida, no hay acto 3. Se dispara primero para tener margen de repetirlo |
| 2 | P4, P5, P10, P12 | Cierran el acto 2 y el 4 |
| 3 | P9 + repeticiones | El menos comprometido; deja hueco para rehacer lo que haya salido mal |

---

## Los prompts

Todos llevan de cola: `photorealistic, warm natural light, shallow depth of field, no text
anywhere, no logos, no on-screen interface, 16:9`.

### P6 — la mano con el movil apagado (24-28 s) 🔴 EL CRITICO
Aqui se encaja despues la conversacion real de WhatsApp. Si la camara se mueve, no encaja.

```
Close-up over-the-shoulder shot of a hand holding a smartphone inside a small beauty and
wellness studio. The phone screen is completely OFF: black, blank, no interface, no text, no
reflections. Behind the hand, softly out of focus, the studio interior. STATIC camera and
STATIC phone, no movement, no pan, no zoom. Ambient sound: quiet room tone.
```
Se repite hasta que salga: pantalla negra y camara quieta. No se pasa al siguiente sin esto.

### P2 — el movil vibrando en el mostrador (4-9 s)
```
Close-up of a phone lying face up on the counter of a small beauty studio. The screen is off
and dark. The phone rests still on the wood. A person works out of focus in the background.
Ambient sound: quiet room tone, the small sounds of work. Static camera.
```
La luz de los mensajes y el zumbido se anaden en post. **No** se le pide a Flow que vibre.

### P1 — las manos trabajando (0-4 s)
```
Extreme close-up of hands at work in a small beauty studio: hands filing and shaping a
client's nails, or applying cream to a client's hand. Face not visible, no faces in frame.
Shallow focus on the hands. Ambient sound: quiet room tone, the small sounds of the work
itself. Static camera.
```

### P13 — la persona mirando su movil (64-70 s)
```
Close-up of @Lena looking down at their phone, serious, thoughtful, no smile. Face lit
softly by the screen. The screen itself is not visible to camera. Neutral dark interior.
Ambient sound: silence, distant room tone. Static camera.
```

### P4 — la pantalla que se apaga sola (14-19 s)
```
Close-up of a phone on a counter, its screen fading to black by itself. Everything perfectly
still. No text or interface visible at any point. Ambient sound: silence, distant room tone.
Static camera.
```

### P5 — el final del dia (19-24 s)
```
@Lena at the end of the day in the now-empty beauty studio, seen from behind, finally
picking up the phone from the counter. Warm low light, chairs empty, everything tidied.
Ambient sound: an empty room, a single set of footsteps. Static camera.
```

### P10 — el pulgar abriendo WhatsApp (50-55 s)
```
Extreme close-up of a thumb tapping a phone screen, an everyday unthinking gesture. The screen
content is completely out of focus and unreadable, no interface visible. Ambient sound: a
single soft tap. Static camera.
```

### P12 — el negocio con vida (59-64 s)
```
Wide shot of a small beauty studio with clients, movement, life: someone at the counter,
someone being attended at a treatment station. Warm light. Ambient sound: quiet conversation,
activity. Slow camera drift.
```

### P9 — probando algo en el movil (46-50 s)
```
Close-up of a person trying something on their phone for the first time, curious, a half
smile appearing. The screen is not visible to camera. Neutral interior. Ambient sound: quiet
room tone. Static camera.
```

---

## Al terminar cada clip

1. Descargarlo. **Generar y no descargar es perder el credito**: paso con el P11, que se genero
   el 25-ago y sigue sin bajar.
2. Guardarlo en `~/brand-assets/video/anuncio-75s/` con el nombre del plano.
3. Comprobar los cuatro numeros: duracion, resolucion, fotogramas **contados** y una mirada al
   fotograma. Un numero correcto no salva una toma fea.

---

## Lo que ya se ha rodado

### P6 — hecho el 26-ago · `P06-mano-movil-apagado.mp4`
Salio bien al primer intento con Omni Flash: 1280x720, 24 fps, 192 fotogramas contados, 8,000 s.
Pantalla **negra** de principio a fin, sin interfaz ni texto, y la camara no se mueve: el fondo
--la ventana, la planta, el marco-- se queda clavado los 8 segundos.

**Lo que si se mueve es el movil.** Medido fotograma a fotograma: el borde superior de la
pantalla oscila entre -10 y +24 px en vertical, unos 30 px de recorrido sobre 720 de alto. Es el
balanceo natural de la mano.

> **Consecuencia para el P7:** la conversacion de WhatsApp **no se puede pegar fija** en la
> pantalla; se le nota el deslizamiento. Hay que medir el rectangulo de la pantalla en los 192
> fotogramas y componer la captura siguiendo esa trayectoria, igual que se hizo el movimiento
> del P8. El metodo ya existe, es `p8-movimiento.py`.

Y hay un reflejo de cara en la pantalla, pese a pedir `no reflections`. No importa: al pegar la
conversacion encima, la pantalla entera queda tapada.
