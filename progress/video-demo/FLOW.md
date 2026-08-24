# FLOW (Google) — qué sabe hacer y cómo lo usamos en el vídeo

> Fuente: **"Google rompió la IA con Flow 2.0: Crea de TODO GRATIS"** — Alejavi Rivera, 35:50.
> https://youtu.be/mRn9flyjzVk · Lo mandó Ricardo el 23-ago-2026. Subtítulos completos en
> `fuentes/flow-2.0-alejavi-rivera.srt` (7.177 palabras) por si hay que releer algo literal.
> Este documento es el complemento técnico de `GUION.md`: el guion dice QUÉ se cuenta, esto dice
> CON QUÉ se produce.

---

## 1. LO QUE FLOW SÍ HACE (y nos sirve)

| Función | Para qué nos vale |
|---|---|
| **Fotogramas de inicio y fin** | Le das la imagen con la que empieza el vídeo y con cuál termina, y describes qué pasa entre medias. Es la técnica del plano 1. |
| **Sin marca de agua** | Se quita desde arriba a la derecha. Antes el logo en la esquina impedía usarlo en material comercial. Google sigue metiendo una marca **invisible** de contenido generado, pero no se ve. |
| **Las imágenes NO gastan créditos** | Ninguna, con cualquier modelo. Los planos de ambiente y sus variaciones salen ilimitados. |
| **El vídeo sí gasta** | 50 créditos diarios, tanto en cuentas gratuitas como de pago. El gasto aparece sólo al animar. |
| **Personajes consistentes** | Se crea un personaje (desde prompt o desde una foto real), se le generan tres perspectivas del cuerpo, se le pone nombre y se invoca con `@` en cualquier generación. Sale siempre la misma persona. |
| **Modo agente** | Pides doce escenas de una vez, las revisas y le dices "sepárame estas doce en imágenes grandes". Y ediciones en lote: seleccionas tres y les cambias el estilo a la vez. |
| **Mockups** | Pone la marca sobre productos con un clic. |
| **Subtítulos automáticos** | Sobre un vídeo vertical ya montado. |
| **Storyboard** | Encadena vídeos hasta ~50 s desde un prompt. |

### La oportunidad que aún no hemos usado
**Fijar un personaje.** Ahora mismo cada creatividad de Nexux lleva una mujer distinta, y eso hace
que no se lean como una marca sino como fotos sueltas de banco. Con un personaje fijo, la misma
persona aparece en flyers, anuncios y publicaciones. Es gratis e ilimitado.

---

## 2. LO QUE NO NOS CREEMOS DEL TUTORIAL

- Dice que **todos los resultados salieron al primer intento**. Con material de marca —texto,
  precios, interfaces— nuestra experiencia dice otra cosa.
- **La pista está en su propio vídeo:** al animar una imagen le apareció una frase en una camiseta
  que él nunca pidió, y admite que no sabe de dónde salió. El modelo rellena huecos por su cuenta.
  Con un paisaje da igual; con nuestro precio o nuestra agenda en pantalla, no.
- El bloque del medio está **patrocinado por HeyGen**: es publicidad, no criterio.

---

## 3. LA REGLA QUE MANDA

> **Todo lo que sea interfaz de Nexux sale de una captura real. Flow sólo hace ambiente.**

Por qué: si el fotograma final es nuestra captura del CRM, todo lo que Flow invente entre medias son
versiones deformadas de esa captura — las horas cambiando, los nombres ilegibles, la interfaz
derritiéndose hasta cuajar. La técnica de inicio-y-fin **funciona cuando las dos puntas son de la
misma naturaleza** (mano con móvil en plano medio → la misma mano más cerca), y **rompe** cuando le
pides saltar de un móvil a nuestro CRM.

---

## 4. CÓMO SE MONTA, PLANO A PLANO

**Plano 1 — generado con fotogramas de inicio y fin.**
Mano con móvil, de plano medio a primer plano. **Pantalla apagada**, sin insertar nada: es el
"antes", el momento en que llega el mensaje. Aquí el movimiento lo hace Flow y aporta.
En el panel de vídeo, pestaña **fotogramas**: se arrastra una imagen al hueco de inicio y otra al de
fin, y el prompt describe sólo el movimiento:
`slow camera push-in toward the phone, everything else unchanged`

**Plano 2 — generado fijo.**
Mismo encuadre, **cámara quieta**. Aquí se encaja la conversación real dentro del teléfono: como no
se mueve, encaja al píxel. Sin tracking, una cámara en movimiento haría imposible el encaje.

**Plano 3 — corte al CRM. Grabación real.**
Ya está grabado de verdad, con la cita entrando sola. No hace falta generar la transición: existe,
es real, y ninguna interfaz se deforma.

**El simultáneo** (móvil delante, CRM detrás moviéndose a la vez) se compone montando el plano 2
sobre el plano 3. No lo hace Flow.

> ⚠️ Con **una sola imagen buena** de la mano y el móvil ya se pueden montar los planos 2 y 3.
> El plano 1 es un extra.

---

## 5. ORDEN DE TRABAJO POR RENTABILIDAD

1. **Fijar el personaje** y regenerar las creatividades con él — gratis, ilimitado, y convierte
   fotos sueltas en una marca reconocible.
2. **Animar los planos de producto** con fotogramas de inicio, ahora sin marca de agua.
3. **Dejar en paz el modo agente** hasta tener el vídeo básico terminado.

---

## 6. ACCESO

Flow se pilota desde el navegador de Ricardo (`labs.google`), no desde la Pi. Para que un agente lo
maneje hace falta **Claude in Chrome conectado** — fue el bloqueo real de la noche del 23-ago: todo
lo demás estaba grabado y montado, y lo único que faltaba era esa escena.
