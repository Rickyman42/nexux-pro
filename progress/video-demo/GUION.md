# GUION — Vídeo de presentación Nexux Recepcionista IA

> Recuperado el 2026-08-24 del transcript de la sesión del 23-ago (no estaba guardado en ningún fichero).
> Este documento es la FUENTE DE VERDAD del vídeo. Antes de montar nada, léelo entero.
> ⛔ No confundir con `video_assets/script.txt` (mayo 2026): ese es del CRM viejo con planes y
> facturación, está obsoleto y no sirve para nada.

---

## 1. QUÉ ES ESTA PIEZA

Vídeo de presentación del producto: **Nexux Recepcionista IA (Lara)**, 29 €/mes, tarifa plana.
Duración objetivo **~75 s**, 16:9 (1920×1080) para web/YouTube, con recorte 9:16 posterior.

**Regla de oro:** tiene que entenderse **sin sonido**. Quien lo abre desde el móvil no lleva
auriculares. La música es decoración, no información.

**Escrito con las técnicas Miralles + Bravo**, pero **sin un solo dato inventado**. El playbook
`nexux-copy` está desactualizado en tres puntos que NO se pueden usar: dice "prueba gratis 14 días"
(ya no existe: pago desde el día 1 con garantía de 30 días), da cifras tipo "pierdes 15-20 citas al
mes" (no medidas en ningún sitio, prohibidas por la norma del repo) y verticaliza a peluquerías
(el producto es horizontal desde el 21-ago).

---

## 2. EL GUION — 5 ACTOS

### Acto 1 — El miedo (0-14 s)
*Visualización, Miralles. El espectador se ve a sí mismo.*

Plano: manos trabajando —da igual el oficio: unas tijeras, unos guantes, una camilla—.
El móvil boca arriba, vibrando. Nadie lo coge.

> Son las once y media.
> Tienes las manos ocupadas.
> El móvil lleva vibrando desde las diez.

### Acto 2 — La pérdida (14-24 s)
*El golpe. Sin cifras: lo que duele es la incertidumbre, no un porcentaje.*

Plano: el móvil se apaga. Silencio. La pantalla, muerta.

> Cuando termines, mirarás.
> Habrá cuatro mensajes.
> Dos ya no contestarán.
>
> **Y nunca sabrás quiénes eran.**

### Acto 3 — El giro (24-46 s)
*Aquí entra el producto funcionando de verdad. Grabación real, sin trucos.*

> Mientras tú trabajabas, alguien contestó.

Se ve la conversación real: preguntan por una cita, Lara responde, propone hora, la persona confirma.

> No un robot que dice "en breve le atenderemos".
> Contestó, ofreció hora y cerró la cita.

Zoom lento a la agenda. La cita aparece.

> **Y la puso en tu agenda. Sola.**

### Acto 4 — Las objeciones, a matar (46-64 s)
*Ritmo rápido, una por plano. Ruptura de patrón, Bravo.*

> *"¿Y si contesta cualquier cosa?"*
> Pruébala tú. Está abierta, sin registrarte.
>
> *"¿Otro programa que aprender?"*
> Es tu WhatsApp. El de siempre.
>
> *"¿Y si no me sirve?"*
> Te devolvemos el dinero. 30 días.
>
> *"¿Cuánto?"*
> **29 € al mes. Sin comisiones por cita.**

### Acto 5 — La pregunta que no puede no contestarse (64-75 s)

> Una cosa antes de que sigas:
>
> **¿Cuántos mensajes tienes ahora mismo sin abrir?**
>
> nexux.pro

*(QR en pantalla, el mismo del flyer → https://nexux.pro/demo)*

---

## 3. POR QUÉ ESTÁ MONTADO ASÍ (decisiones de dirección, no cambiarlas sin motivo)

1. **El producto no aparece hasta el segundo 24.** Antes hay que ganarse el derecho a enseñarlo.
   Los primeros 14 segundos no venden nada: describen su martes.
2. **Ni un dato inventado.** El miedo lo pone *"nunca sabrás quiénes eran"*, que es verdad y no se
   puede discutir. Un "pierdes 15 citas al mes" se discute en dos segundos.
3. **Las objeciones van juntas y rápidas**, en quince segundos. En fila y contestadas en seco
   comunican seguridad; repartidas por el vídeo suenan a excusas.
4. **Nada de voz en off ni avatar.** El producto se explica viéndolo. Una voz genérica de IA
   leyendo ventajas envejece mal y suena a anuncio.
5. **Ambiente generado, producto grabado.** Regla innegociable: todo lo que sea la interfaz de
   Nexux sale de una **captura real**, nunca de una interfaz inventada por IA.

---

## 4. NORMAS DE RICARDO SOBRE ESTA PIEZA

- **Paleta CLARA, no negra.** La web no tiene tema oscuro: blanco `#FFFFFF`, fondo suave `#F7F6F3`,
  tinta `#14161A`, teal `#2A8B84`. Los primeros actos se montaron con un negro `#0B0D12` que **ya no
  existe en la marca** — hay que pasarlos a paleta clara.
- **Tipografía real de marca:** Instrument Serif para las frases, Geist para los datos.
- **"Dinamismo, gente de verdad, teléfonos de verdad, sonidos de verdad y nuestro producto de
  verdad."** (23-ago)
- **"Todo con vídeo real, no 4 frases mal puestas. Simular una situación real, que el cliente se vea
  con el sistema implantado en su negocio, respetando ese guion."** (24-ago)
- Rechazado explícitamente: pantalla del móvil congelada con la conversación **pegada encima** (se ve
  superpuesta, no integrada), y el acto 3 con rótulos y velocidad alterada — rompe la sensación de
  que es real.

---

## 5. ESTADO DE PRODUCCIÓN (24-ago-2026)

Material en la Pi: `~/brand-assets/video/`. Copia en `Desktop\creatives\20260823_video-demo\` y
`20260824_video-demo\`.

| Pieza | Fichero | Estado |
|---|---|---|
| Acto 1 — el miedo | — | ⬜ **no existe** |
| Acto 2 — la pérdida | `acto2-la-perdida.mp4` (12 s) | ⚠️ montado en **paleta negra**, hay que pasarlo a clara |
| Acto 3 — el producto | `acto3-real-sin-editar.mp4` (46 s) | ❌ **rechazado por Ricardo** ("no me vale", sin detalle) |
| Acto 3 — versión previa | `acto3-el-producto.mp4` (24 s) | ⚠️ con rótulos y velocidad alterada — descartada por él |
| Acto 4 — objeciones | `acto4-objeciones.mp4` (17 s) | ⚠️ paleta negra |
| Acto 5 — la pregunta | `acto5-la-pregunta.mp4` (12 s) | ⚠️ paleta negra |
| Plano mano+móvil (Flow) | `plano1-camera-push.mp4` (8 s) | ✅ generado |
| Pantalla encendiéndose | `plano2-pantalla-real.mp4` (3 s) | ❌ es el "mal superpuesto" que rechazó |
| Concatenado móvil→CRM | `intro-telefono-a-crm.mp4` | ❌ contiene el plano 2 rechazado |
| **Montaje final de los 5 actos** | — | ⬜ **no existe** |

### Hallazgo importante del 24-ago
La grabación 1080p original **ya es split-screen real**: chat del cliente y agenda del negocio en la
misma toma, a la vez. No hace falta componer un móvil ni insertar pantallas. Basta recortar los
tramos de espera muerta ("Lara está escribiendo…") sin tocar velocidad ni meter rótulos.

### Bloqueo abierto
Ricardo rechazó la última versión del acto 3 con un **"No me vale"** sin detallar qué falla.
**No montar nada más hasta que diga qué es** — van dos intentos rechazados a ciegas.

---

## 6. PIPELINE — DÓNDE ESTÁ CADA SCRIPT

⚠️ Los scripts vivían en el scratchpad temporal de la sesión del 23-ago (se borra). Copiados aquí
el 24-ago para que no se pierdan: `progress/video-demo/pipeline/`.

| Script | Qué hace |
|---|---|
| `grabar-1080.js` | Graba la demo real de `nexux.pro/demo` a 1920×1080 (split-screen chat + agenda) |
| `grabar-vertical.js` | Misma grabación a 440×956, para insertar dentro de un móvil |
| `montar-actos.py` | Monta los actos de texto (2, 4, 5) — 1920×1080 |
| `montar-acto3.py` | Monta el acto 3 con la demo real |

Todo se ejecuta **en la Pi**, no en Windows.
