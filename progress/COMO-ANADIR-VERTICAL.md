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
