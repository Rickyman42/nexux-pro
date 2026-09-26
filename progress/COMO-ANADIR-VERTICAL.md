# Cómo añadir un vertical nuevo a la demo

Son **dos entradas en dos mapas**. No se toca ninguna otra línea de código.

1. **Backend** — `~/nexux-clients/provision-http.js`, mapa `DEMO_CONFIGS`: copia la
   entrada `veterinaria`, cambia la clave, `nombre`, `nombreLlano`, `bio`,
   `services` y las seis etiquetas de sector (`sectorArticulo`, `sectorLlano`,
   `serviciosEjemplo`, `deQuien`, `ejemploChoque`, `ejemploReserva`) y las cuatro
   citas de `citasSiembra`.
2. **Frontend** — `~/nexux-pro/src/pages/demo.astro`, mapa `VERTICALES`: una línea
   con `negocio` y `titulo`. La clave debe ser **la misma** que en el backend.
3. `pm2 restart nexux-clients` y `pnpm build` en `nexux-pro`.
4. Se comparte por enlace: `https://nexux.pro/demo?sector=<clave>`. Lleva `noindex`
   automático; la genérica (`/demo`) sigue indexándose.
5. **No se crea ningún bot nuevo.** `buildSystemPrompt(config, …)` lee el nombre, la
   bio, los servicios y el horario del config: Lara se adapta sola. Si te ves
   escribiendo un prompt por sector, te has salido del molde.

## 🔒 Regla del molde (no negociable)

**Todo el texto visible de la demo y todas las citas de muestra —nombres Y
servicios— salen del `config` del sector. Nunca del HTML.**

Si al añadir un vertical te ves escribiendo un nombre o un servicio dentro de
`demo.astro`, te has salido del molde. Ya pasó dos veces: los botones de
sugerencia llevaban "¿Cuánto cuesta un tinte?" grabado, así que una clínica
veterinaria pedía tintes; y las cuatro citas de muestra tenían los mismos
nombres en todos los sectores.

Ni "tinte", ni "corte", ni "manicura", ni nombres de otro sector. En una
veterinaria, los clientes se llaman "Ana G. - Rex (perro)".

**Comprobación mínima antes de darlo por bueno** (sustituye `<clave>`):

```bash
curl -s "http://localhost:3460/demo/appointments?sector=<clave>"
curl -s -X POST http://localhost:3460/demo/chat -H 'Content-Type: application/json' \
  -d '{"sector":"<clave>","message":"¿Qué servicios tenéis?"}'
```

Debe responder con los servicios de ESE vertical y no nombrar ningún otro negocio.

Y estas dos, que son las que se saltaron y dieron el fallo:

```bash
# 1. Ni una palabra de otro sector en la demo renderizada. Tiene que salir VACIO.
curl -s "https://nexux.pro/demo?sector=<clave>" | grep -oiE '(tinte|corte|manicura|mechas)'

# 2. Las citas de muestra, con nombres Y servicios del vertical.
curl -s "http://localhost:3460/demo/appointments?sector=<clave>"
```

---

## ⚠️ Guardarraíl: verticales de salud

**Clínicas, fisioterapia, dentistas, podología y cualquier vertical sanitario NO se
activan hasta resolver el RGPD artículo 9.** Una cita de paciente es un dato de
categoría especial: hace falta base jurídica, contrato de encargado del tratamiento
con el cliente y, muy probablemente, evaluación de impacto.

Suma a eso que la demo y el chat de la web **ya guardan las conversaciones sin aviso
de privacidad** (aplazado a propósito el 19-sep). Para una peluquería o una
veterinaria eso es un fleco; para una clínica es un incumplimiento.

**Las veterinarias no entran en este guardarraíl**: los datos de una mascota no son
categoría especial. Por eso el primer vertical es veterinaria y no fisioterapia,
aunque la lista de fisios ya esté recogida.

## Objeción nº1 de las clínicas veterinarias (medida en campo, 21-sep-2026)

Petconnection (Móstoles) contestó al primer WhatsApp con esto:

> "nuestro negocio no puede tener un sistema que dé la cita sola, porque debemos
> hablar con los tutores primero, ver la gravedad"

**Qué significa:** creen que Lara decide la gravedad. En una clínica eso no se delega,
y tienen razón en no querer delegarlo. **"Tutor" es el dueño del animal, y está en la
consulta con el animal delante** — no es una conversación de chat.

**Cómo se responde (y va en la página, no sólo en el mensaje):**
Lara no decide gravedad. Coge SÓLO lo que el negocio le deje coger (por ejemplo
revisiones y vacunas) y todo lo demás lo pasa al WhatsApp de la clínica, marcado.
No les quita el criterio: les quita las interrupciones.

**Regla para el molde:** en cualquier vertical sanitario, el mensaje NUNCA puede
sugerir que Lara sustituye la consulta ni que valora un caso. Esta objeción sale
la primera, y si no está respondida de antemano, cierra la conversación.


---

## La cabecera de un vertical (elegida el 26-sep-2026, tras seis vueltas)

Todas las páginas de vertical llevan la misma cabecera. Lo **único** que cambia es la
foto y los textos. Está montada en `src/pages/tatuajes.astro`; para una nueva, se copia.

**Cómo funciona, en tres capas superpuestas:**

1. `.hero-foto` — la foto en gris, `contrast(1.4)`, `opacity .8`.
2. `.hero-trazo` — **la misma foto** otra vez, `contrast(2.1)` y `mix-blend-mode: multiply`.
   Oscurece los bordes y hace de **delineado**, sin dibujar nada.
3. `.hero-tinte` — una capa lisa de `var(--nx-magnet)` con `mix-blend-mode: color`.
   Esa mezcla coge el **tono** del verde y la **luz** de la foto: monocromo verde de
   verdad, no un filtro aproximado.
4. `.hero-velo` — degradado del color de fondo, **opaco a la izquierda** y abierto a la
   derecha.

🔴 **El velo de la izquierda no se toca.** Ahí va el titular. Si se abre para que se vea
más foto, gana la imagen y se pierde la frase — y la frase es lo que vende.

**La foto:**

- Va en `public/img/<vertical>-hero.webp`, **nunca dentro del HTML**.
- Se guarda **ya en gris**: la página la pinta en gris igual, así que el color es peso
  que nadie ve. En tatuajes eso fue pasar de 278 KB a 51 KB.
- 1600 px de ancho, calidad 72:

```python
from PIL import Image
im = Image.open("original.webp").convert("L").convert("RGB")
r = im.resize((1600, round(im.size[1]*1600/im.size[0])), Image.LANCZOS)
r.save("public/img/<vertical>-hero.webp", "WEBP", quality=72, method=6)
```

- **Plano corto, no plano general.** Se probó con un plano general de un estudio entero
  y el protagonista se perdía. Manos, herramienta y la acción. Sin caras reconocibles,
  sin marcas legibles.

**Lo que ya se descartó, para no repetirlo:**

| intento | por qué no |
|---|---|
| Foto detrás del texto, oscurecida | hay que apagarla tanto que deja de verse |
| Dibujo a línea hecho por IA | 64 trazos, parecía de un niño |
| Foto autocalcada a SVG | 305 KB y 40.175 nodos metidos en el HTML |
| Trama de puntos / litofanía | la foto se vuelve papilla, no se reconoce nada |

El fallo de fondo de los tres primeros fue **poner la foto detrás del texto**. Con el
velo lateral y el móvil al lado, la foto tiene su sitio y no hace falta maltratarla.

**El móvil de la conversación va EN la cabecera**, al lado del titular. Antes estaba en
una sección aparte más abajo y casi nadie llegaba. Los mensajes salen del array
`conversacion`, y el día y la confirmación de `MOMENTO` y `CONFIRMADO` — **nunca escritos
a mano en el HTML**, que ya se coló un "martes a las 23:14" en una página que hablaba del
domingo.
