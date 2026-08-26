# ESTADO DEL ANUNCIO DE 75 SEGUNDOS

> Foto del 26-ago-2026. **Empieza por aquí**: los otros ocho documentos de esta carpeta
> cuentan el *cómo*, este cuenta el *dónde estamos*.
> Si algo de aquí no cuadra con lo que ves, gana lo que veas: actualiza esto.

---

## 1. DÓNDE ESTAMOS EN UNA LÍNEA

**9 planos de 14 terminados y montados en CapCut.** Faltan 5 planos de Flow (créditos),
todos los rótulos, la música y la voz.

---

## 2. LOS 14 PLANOS

Duraciones y resoluciones **medidas** sobre los ficheros, no estimadas.

| # | Qué es | Estado | Fichero | Dura | Resolución |
|---|---|---|---|---|---|
| P1 | Manos limando uñas | ✅ | `P01-manos-manicura.mp4` | 8,00 s | 1280×720 |
| P2 | El móvil quieto en el mostrador | ✅ | `P02-movil-mostrador.mp4` | 8,00 s | 1280×720 |
| P3 | La cabina, ella trabajando | ✅ ⚠️ | `P03-cabina-mensajes.mp4` | 8,00 s | 1280×720 |
| P4 | La pantalla que se apaga sola | ⬜ Flow | — | — | — |
| P5 | El final del día, negocio vacío | ⬜ Flow | — | — | — |
| P6 | La mano con el móvil apagado | ✅ | `P06-mano-movil-apagado.mp4` | 8,00 s | 1280×720 |
| P7 | La conversación de WhatsApp | ✅ | `P07-en-movil.mp4` | 11,00 s | 1280×720 |
| P8 | El CRM y la cita entrando sola | ✅ | `P08-crm-cita-entra.mp4` | 8,00 s | **1920×1080** |
| P9 | Alguien probándolo, curioso | ⬜ Flow | — | — | — |
| P10 | Un pulgar abriendo WhatsApp | ⬜ Flow | — | — | — |
| P11 | Lena apoyada en el mostrador | ✅ | `P11-lena-mostrador.mp4` | 8,00 s | 1280×720 |
| P12 | El negocio con clientes, vida | ⬜ Flow | — | — | — |
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
- `P07-conversacion.mp4` (720×1560, vertical) es la pantalla suelta, **material intermedio**.
  Lo que va al montaje es `P07-en-movil.mp4`.

---

## 3. EL MONTAJE

**CapCut de escritorio, proyecto `0825`.** Los 9 planos en orden, 1 minuto 12 segundos.

- Versión **9.3.0.3970**. El permiso de control se concede al ejecutable concreto, así que
  cada actualización lo rompe. Acceso directo vigente: **"CapCut 9.3"**.
- Los clips están **enteros, sin recortar**: la escaleta pide 4-5 s por plano y Flow entrega 8.
  Es deliberado — Ricardo elige qué tramo se queda de cada uno viéndolos.
- **No hay ningún rótulo puesto.** Había uno del acto 1 y se quitó al reconstruir la timeline.

---

## 4. LO QUE FALTA, EN ORDEN

1. **Los 5 planos de Flow** — P4, P5, P10, P12 un día; P9 al siguiente. 12 créditos el clip,
   50 al día. Prompts listos y probados en `PROMPTS-FLOW.md`, se disparan sin pensar.
2. **Recortar** cada plano a su duración de escaleta. Decisión de Ricardo, plano a plano.
3. **Los rótulos**, en CapCut, nunca en Flow. Los textos exactos están en `PLAN-RODAJE.md` §2.
4. **Música y sonido.** El audio de Flow es casi mudo: los picos miden 0,004 sobre 1.
5. **Dos montajes**: sin voz para la web, con voz para redes. La voz se hará con **ElevenLabs**,
   que tiene crédito — sustituye a MiniMax, que era el plan viejo.

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
