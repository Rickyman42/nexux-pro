# Salida del motor de Gemini Notebook

> ⚠️ **Salida en bruto del 25-ago, con dos cosas ya superadas.** No seguir a ciegas:
> - Dice que el plano 8 es «el Google Calendar de Ricardo». **Es el CRM** (`nexux.pro/cliente/<id>`, pantalla Citas).
>   Ver PLAN-RODAJE.md §7.
> - El negocio es un centro de estetica, no una peluqueria. Ver NEGOCIO.md.
>
> Cuaderno `4e46a5fc-37bf-44e1-b27c-65666047069c` · conversacion `21b2e721` · 2026-08-24
> Fuentes: MASTER PROMPT, GUION, PLAN DE RODAJE.
> Esta es la salida en bruto del motor. Lo que mande sigue siendo GUION.md.

## Turno 1 - lo que se le pidio

Hola

## Lo que devolvio

¡Hola! Como director de fotografía y productor del anuncio de **Nexux Recepcionista IA** [1], asumo el papel de producción utilizando el **GUION** como un marco cerrado e inalterable [1, 2] y el **PLAN DE RODAJE** como la referencia oficial para estructurar y rodar cada escena [3].

Tal como establece el protocolo de dirección antes de iniciar la preparación técnica, necesito que me respondas a estas **6 preguntas clave** [4]:

1. **Formato de pantalla:** ¿Deseas la entrega en **16:9** (horizontal) o **9:16** (vertical)? [4] *(El plan de rodaje propone trabajar inicialmente a 16:9 con recorte posterior [3], pero confírmame tu preferencia).*
2. **Duración total y cantidad de planos:** ¿Trabajamos sobre la duración objetivo de **~75 segundos** estructurada en los **14 planos** que detalla la escaleta del plan de rodaje, o hacemos alguna modificación? [2, 4, 5]
3. **Tipo de cuenta de Google Flow:** ¿Utilizaremos una cuenta **gratuita** (con límite de 50 créditos/día) o una versión de **pago**? [3, 4]
4. **Música y locución:** ¿Llevará música de fondo? [4] En caso de requerir locución, ¿utilizaremos la voz nativa del modelo o un TTS externo (como la clonación de la voz de Ricardo)? [4, 6]
5. **Descripción del personaje fijo:** ¿Cómo definimos detalladamente al **protagonista** (el dueño/a del negocio de 30-45 años, de aspecto neutro) para invocarlo con @ en Flow y mantener la consistencia visual? [7, 8]
6. **Ambiente sonoro deseado por acto:** ¿Qué tipo de **sonidos ambientales reales** prefieres para acompañar cada uno de los 5 actos del guion? [4, 9]

**No generaré ninguna pieza, escaleta ni bloque de prompts** hasta que me des luz verde contestando a estas cuestiones [4]. En cuanto las responda, te entregaré en el orden exacto del máster la escaleta completa, el storyboard, los prompts listos para copiar en Flow, la música, la locución y el reparto diario adaptado a tus créditos [4, 10, 11].

¡Quedo a la espera de tus instrucciones para dar el claquetazo de salida!

---

## Turno 2 - lo que se le pidio

Respondo a las 6, en orden.

1. FORMATO: 16:9 (1920x1080). El recorte 9:16 se hace despues en CapCut, no lo tengas en cuenta ahora.

2. DURACION Y PLANOS: 75 segundos, los 14 planos de la escaleta del PLAN DE RODAJE, sin modificaciones. Recuerda: P7 y P8 son [CAPTURA REAL] y NO se generan ni consumen creditos. P14 es composicion en CapCut. Quedan 11 planos que generar en Flow.

3. CUENTA DE FLOW: GRATUITA, 50 creditos al dia. Calcula el coste real y parte el trabajo en tandas diarias que quepan en ese limite.

4. MUSICA Y LOCUCION: Si a la musica de fondo. Y hacemos DOS versiones de la pieza con el mismo material:
   - Version web: SIN locucion. Solo rotulos y sonido ambiente, tiene que entenderse sin sonido.
   - Version redes: CON locucion, TTS externo (voz de Ricardo clonada en MiniMax).
   Asi que dame el texto de locucion cronometrado igualmente, pero disenado para que la pieza funcione perfectamente tambien sin el.

5. PERSONAJE FIJO: mujer, 35-40 anos, espanola, complexion normal, pelo oscuro recogido, sin maquillaje llamativo, sin joyas. Ropa de trabajo neutra: delantal liso gris oscuro o negro, sin logos, sin rayas, sin nada que identifique un oficio concreto. Manos cuidadas y con marcas de trabajo real. Expresion seria y algo cansada en los actos 1 y 2; tranquila y con media sonrisa en el 4. NUNCA se la viste de peluquera ni de sanitaria: el oficio se insinua por las manos y el mobiliario, nunca por el uniforme, porque el producto vale para cualquier negocio con cita previa.

6. AMBIENTE SONORO POR ACTO:
   - Acto 1 (el miedo): sonido de trabajo real y cercano, muy concreto — el clic de unas tijeras, un instrumento sobre una bandeja, el roce de la tela. De fondo, el movil vibrando contra el mostrador, insistente pero no dramatico.
   - Acto 2 (la perdida): el silencio despues del zumbido. Un local vacio, un tono de sala, quiza una persiana lejana. El vacio ES el sonido de este acto.
   - Acto 3 (el giro): sonido de notificacion, discreto. Nada triunfal, nada de campanas de exito. La cosa funciona sin celebrarse.
   - Acto 4 (las objeciones): ambiente de negocio con vida — conversacion de fondo ininteligible, movimiento, pasos. Energia, ritmo.
   - Acto 5 (la pregunta): silencio casi total. Solo tono de sala. Que la pregunta caiga en seco.

REGLAS QUE NO SE NEGOCIAN, recuerdalas al generar:
- Ningun plano generado puede mostrar una pantalla con texto, horas, nombres, precios ni interfaz. Si sale un movil, va APAGADO.
- Todos los prompts terminan con "no text anywhere, no logos".
- Los rotulos salen LITERALES del GUION y se ponen en CapCut, nunca en Flow.
- Modelo Omni Flash en modo agente.

Adelante con los 6 bloques en el orden del master.

## Lo que devolvio

### BLOQUE 1 · ESCALETA

Esta es la escaleta de rodaje definitiva adaptada a una relación de aspecto **16:9** [1, 2], donde los planos generados por IA irán con las pantallas apagadas [3, 4] para albergar los rótulos y las capturas reales en la fase de montaje en CapCut [2, 4].

| Plano | Segundos | Qué se ve | Rótulo literal (CapCut) [4-7] | Recurso | Coste en créditos [8] |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **P1** [5] | 0-4 | Manos trabajando en primer plano. Tijeras, guantes o camilla. Foco muy cerrado, no se ve la cara. | *Son las once y media.* | **FLOW** | 20 créditos |
| **P2** [5] | 4-9 | El móvil boca arriba en el mostrador, vibrando. La pantalla se ilumina sin texto legible. | *Tienes las manos ocupadas.* | **FLOW** | 20 créditos (Prueba) |
| **P3** [5] | 9-14 | Plano medio: @personaje sigue a lo suyo, concentrada. El móvil delante, desenfocado, vibrando. | *El móvil lleva vibrando desde las diez.* | **FLOW** | 20 créditos |
| **P4** [4] | 14-19 | La pantalla del móvil se apaga sola. Quieto. Silencio. | *Cuando termines, mirarás.* / *Habrá cuatro mensajes.* | **FLOW** | 20 créditos |
| **P5** [4] | 19-24 | El negocio vacío al final del día. @personaje coge por fin el móvil, de espaldas. | *Dos ya no contestarán.* → **Y nunca sabrás quiénes eran.** | **FLOW** | 20 créditos |
| **P6** [4] | 24-28 | Mano cogiendo el móvil, pantalla apagada, cámara quieta. Hueco para encajar el chat. | *Mientras tú trabajabas, alguien contestó.* | **FLOW (Fijo)** | 20 créditos |
| **P7** [4] | 28-38 | La conversación real de WhatsApp (Lara responde, propone hora, el cliente confirma) [4, 9]. | *Contestó, ofreció hora y cerró la cita.* | **CAPTURA REAL** [4] | 0 créditos |
| **P8** [4] | 38-46 | El Google Calendar de Ricardo con la cita entrando sola y el texto "Reservado por: Lara" [10-12]. | **Y la puso en tu agenda. Sola.** | **CAPTURA REAL** [4] | 0 créditos |
| **P9** [6] | 46-50 | Alguien probando algo en el móvil, curioso, media sonrisa. Pantalla no visible. | *¿Y si contesta cualquier cosa?* → **Pruébala tú. Sin registrarte.** | **FLOW** | 20 créditos |
| **P10** [6] | 50-55 | Un pulgar abriendo WhatsApp. Gesto cotidiano. Pantalla no legible. | *¿Otro programa que aprender?* → **Es tu WhatsApp. El de siempre.** | **FLOW** | 20 créditos |
| **P11** [6] | 55-59 | @personaje apoyada en el mostrador, tranquila, sin prisa. | *¿Y si no me sirve?* → **Te devolvemos el dinero. 30 días.** | **FLOW** | 20 créditos |
| **P12** [6] | 59-64 | El negocio con clientes, movimiento, vida. | *¿Cuánto?* → **29 € al mes. Sin comisiones por cita.** | **FLOW** | 20 créditos |
| **P13** [7] | 64-70 | Primer plano de una persona mirando su móvil, seria. Rostro iluminado por la pantalla. | *Una cosa antes de que sigas:* → **¿Cuántos mensajes tienes ahora mismo sin abrir?** | **FLOW** | 20 créditos |
| **P14** [7] | 70-75 | Fondo claro de marca con los colores corporativos. Código QR grande. | **nexux.pro** · Recepcionista IA · 29 €/mes · *Escanea y pruébala sin registrarte* | **COMPOSICIÓN** [7] | 0 créditos |

**Créditos totales requeridos para animación:** 220 créditos (11 planos de Flow a ~20 créditos por clip animado) [7, 8].

---

### BLOQUE 2 · PROMPT DE STORYBOARD

Este prompt está diseñado para generar una cuadrícula fotográfica realista que sirva como storyboard de preproducción. Copia y pega este prompt en tu generador de imágenes:

> **Prompt:**
> Cinematic photorealistic storyboard sheet, 12 numbered panels in a 4x3 grid. The sequence shows a 35-40 year old Spanish female business owner with dark hair tied back in a bun, wearing a plain charcoal-gray work apron. Panel 1: Extreme close-up of busy hands working in a shop. Panel 2: A phone face-up on a counter vibrating. Panel 3: The woman working in the background, a vibrating phone out of focus in the foreground. Panel 4: Close-up of a phone screen going dark. Panel 5: The woman seen from behind in an empty, dimly lit shop, picking up her phone. Panel 6: Over-the-shoulder close-up of a hand holding a phone with a black, blank screen. Panel 7: A smartphone screen showing a clean chat bubble interface. Panel 8: A desktop Google Calendar grid with a newly added event block. Panel 9: A close-up of a person smiling while looking at their phone. Panel 10: Extreme close-up of a thumb pressing a messaging app icon on a phone. Panel 11: The woman leaning on her counter looking relaxed. Panel 12: A wide shot of a busy local shop with customers. Consistent warm natural light, shallow depth of field, high-end professional commercial aesthetic, detailed, no text anywhere, no logos.

---

### BLOQUE 3 · PROMPT PARA EL AGENTE DE GOOGLE FLOW

Este bloque contiene las especificaciones técnicas globales y los prompts individuales en inglés para alimentar al agente de **Google Flow** con el modelo **Omni Flash** [2, 13].

```text
# SYSTEM CONFIGURATION
MODEL: Omni Flash (Agent Mode)
ASPECT_RATIO: 16:9 (1920x1080)
STYLE: Photorealistic, cinematic, warm natural light, shallow depth of field, high-end commercial aesthetic.
STRICT NEGATIVE TRIGGER: "no text anywhere, no logos"

# FIXED CHARACTER DEF (Invocable with @personaje)
@personaje: A Spanish woman, 35-40 years old, average build, dark hair neatly tied back in a bun, natural skin with no makeup or jewelry. Wearing a plain solid charcoal gray work apron over a neutral t-shirt, completely devoid of logos, stripes, or identifying uniform details. Hands are neat but show signs of honest manual work. Serious and slightly tired expression in early scenes; calm and smiling in later scenes.

# SCENE DISPATCH LIST

[P1]
Extreme close-up of hands at work in a small appointment-based local business—handling a manual task (like cutting with scissors, adjusting a clean treatment table, or polishing a tools tray). The face is completely out of frame. Focus entirely on the details of the hands and tools. Ambient sound: quiet room tone with the subtle, sharp sound of metal tools clinking and soft fabric rustling. Static camera. 4 seconds. no text anywhere, no logos

[P2]
Close-up of a smartphone lying face up on a clean wooden counter inside a business. The phone vibrates from a call, the screen lighting up. The screen has no visible interface or legible text (completely blurred, unreadable soft white glow). In the soft out-of-focus background, a person is working. Ambient sound: the phone buzzing and vibrating loudly against the hard wooden counter. Static camera. 5 seconds. no text anywhere, no logos

[P3]
Medium shot of @personaje working diligently, focused, not looking at the phone. In the close foreground, the phone sits out of focus on the counter, vibrating silently. Ambient sound: ambient workspace sounds of manual tools and fabric rustling, underlaid by the phone vibrating unanswered. Slow, subtle camera push-in. 5 seconds. no text anywhere, no logos

[P4]
Close-up of a smartphone screen lying on a counter, slowly going completely dark and turning off by itself. The environment is quiet and still. Minimalist warm lighting. Ambient sound: absolute silence, empty room tone, a distant low hum. Static camera. 5 seconds. no text anywhere, no logos

[P5]
Medium shot of @personaje seen from behind at the end of the day in a now-empty, quiet local business with dim, warm evening light. She finally picks up her phone from the counter, shoulders slightly slumped with tiredness. Ambient sound: complete quietness, empty room tone, a single set of footsteps. Static camera. 5 seconds. no text anywhere, no logos

[P6]
Close-up over-the-shoulder shot of a hand holding a smartphone inside a local business. The phone screen is completely OFF: solid black, blank, no interface, no text, no glowing parts, no reflections. In the background, softly blurred, is the warm, empty shop interior. CAMERA IS COMPLETELY STATIC, phone is completely static with no hand movement. Ambient sound: a discreet, quiet electronic message notification tone. 4 seconds. no text anywhere, no logos

[P9]
Close-up of a person looking at their phone, trying an application for the first time. They have a curious look that transitions into a warm half-smile of surprise. Screen is not visible to the camera. Warm natural lighting. Ambient sound: lively ambient workspace noise, faint inintelligible chatter of people, light movement. 4 seconds. no text anywhere, no logos

[P10]
Extreme close-up of a person's thumb opening a familiar messaging application icon on a phone screen. An everyday, unthinking gesture. The actual screen content is blurred and has no legible text or names. Warm natural lighting. Ambient sound: lively ambient business sounds, distant murmurs, gentle rustle of activity. 5 seconds. no text anywhere, no logos

[P11]
Medium shot of @personaje leaning relaxed on the business counter, calm, unhurried, looking off-camera with a peaceful, confident expression. Soft natural light. Ambient sound: warm, energetic background chatter of a successful shop, footsteps. 4 seconds. no text anywhere, no logos

[P12]
Wide shot of a small local business interior filled with gentle movement, customers interacting in the background (softly out of focus), showing life and successful activity. Warm golden-hour light, cinematic. Ambient sound: lively ambient noise, soft overlapping voices, footsteps, a busy but pleasant atmosphere. Slow camera drift. 5 seconds. no text anywhere, no logos

[P13]
Close-up of a person looking down at their phone, serious and thoughtful, face softly illuminated by the glow of the screen. Cinematic dark-to-light contrast. Ambient sound: almost total silence, quiet room tone, cold drop. 6 seconds. no text anywhere, no logos
```

---

### BLOQUE 4 · PROMPT DE MÚSICA

Este prompt en inglés para **Google Flow Music** describe la progresión emocional y el tono de la pieza [13]. Sigue el arco narrativo del miedo, la transición tecnológica y el ritmo ágil del éxito final [9, 14, 15]:

> **Prompt:**
> A minimal and modern electronic commercial background track. Starts with a slow, subtle, slightly tense synthesizer pad with a quiet, organic rhythmic ticking clock-like sound (from 0s to 24s), representing anxiety and waiting. At 24s, the track seamlessly transitions into a light, clean, and highly optimistic beat, incorporating soft acoustic guitar plucks, a warm analog bass, and a gentle, steady lo-fi drum rhythm. The mood is highly professional, clean, and confident, never overwhelming. Ends in a crisp, clean single acoustic note that quickly fades out into silence at exactly 75s.

---

### BLOQUE 5 · TEXTO DE LOCUCIÓN

Diseñado para la versión de redes (con locución de Ricardo mediante MiniMax) [9, 12], pero sincronizado milimétricamente con los rótulos que se mostrarán en la versión web (que funciona perfectamente en silencio) [9, 16]:

*   **[0:00 - 0:04 | P1]**
    "Son las once y media." [5]
*   **[0:04 - 0:09 | P2]**
    "Tienes las manos ocupadas." [5]
*   **[0:09 - 0:14 | P3]**
    "Y el móvil... lleva vibrando desde las diez." [5]
*   **[0:14 - 0:19 | P4]**
    "Cuando termines, mirarás." [4]
*   **[0:19 - 0:24 | P5]**
    "Habrá cuatro mensajes. Dos ya no contestarán... Y nunca sabrás quiénes eran." [4]
*   **[0:24 - 0:28 | P6]**
    "Mientras tú trabajabas... alguien contestó." [4]
*   **[0:28 - 0:38 | P7]**
    "Contestó, ofreció hora y cerró la cita." [4]
*   **[0:38 - 0:46 | P8]**
    "Y la puso en tu agenda. Sola." [4]
*   **[0:46 - 0:50 | P9]**
    "¿Y si contesta cualquier cosa? Pruébala tú. Sin registrarte." [6]
*   **[0:50 - 0:55 | P10]**
    "¿Otro programa que aprender? Es tu WhatsApp. El de siempre." [6]
*   **[0:55 - 0:59 | P11]**
    "¿Y si no me sirve? Te devolvemos el dinero. Treinta días." [6]
*   **[0:59 - 0:64 | P12]**
    "¿Cuánto? Veintinueve euros al mes. Sin comisiones por cita." [6]
*   **[0:64 - 0:70 | P13]**
    "Una cosa antes de que sigas..." [7]
*   **[0:70 - 0:75 | P14]**
    "¿Cuántos mensajes tienes ahora mismo sin abrir? Pruébalo en nexux.pro" [7]

---

### BLOQUE 6 · REPARTO POR DÍAS (Modo Lote)

Dado que la cuenta de Google Flow es **gratuita** y está limitada a **50 créditos diarios** [17], y sabiendo que cada generación de vídeo cuesta aproximadamente **20 créditos** [8], agrupamos el trabajo en tandas de **2 clips animados al día** [18]. 

*Nota técnica: La generación de imágenes estáticas y la definición de @personaje consume **0 créditos**, por lo que se recomienda realizar todo el Paso 3 (generación e iteración de imágenes estáticas) durante el Día 1 [8, 18].*

#### **Día 1: El Plano de Prueba + Primer Plano de Manos (40 créditos)**
*   **Acción 0 créditos:** Crear el personaje fijo en Flow (@personaje) y generar las imágenes base de los 11 planos [8].
*   **P2 (5s - 20 créditos):** Plano de prueba crítico (móvil vibrando). Es el plano elegido para verificar la calidad de la animación de Flow antes de continuar [8].
*   **P1 (4s - 20 créditos):** Primer plano de manos trabajando [5].

#### **Día 2: El Miedo y el inicio de la Pérdida (40 créditos)**
*   **P3 (5s - 20 créditos):** Plano medio de la trabajadora concentrada con el móvil al frente [5].
*   **P4 (5s - 20 créditos):** El móvil apagándose solo en el mostrador [4].

#### **Día 3: El Cierre del Acto 2 y el Anclaje del Acto 3 (40 créditos)**
*   **P5 (5s - 20 créditos):** Negocio vacío, cogiendo el móvil de espaldas [4].
*   **P6 (4s - 20 créditos):** Plano de anclaje (mano sosteniendo el móvil con pantalla apagada) [4, 19]. *¡Vigilar que la cámara quede completamente inmóvil para facilitar la composición posterior en CapCut!* [4, 19]

#### **Día 4: Objeciones - Parte I (40 créditos)**
*   **P9 (4s - 20 créditos):** Persona probando el sistema con media sonrisa [6].
*   **P10 (5s - 20 créditos):** Pulgar abriendo WhatsApp [6].

#### **Día 5: Objeciones - Parte II (40 créditos)**
*   **P11 (4s - 20 créditos):** @personaje apoyada en el mostrador, tranquila [6].
*   **P12 (5s - 20 créditos):** Negocio con movimiento, clientes y vida [6].

#### **Día 6: El Cierre Narrativo (20 créditos)**
*   **P13 (6s - 20 créditos):** Plano final del espectador mirando el móvil seriamente antes de la llamada a la acción [7].

---

🎬 ¿Quieres que empecemos generando la plantilla del guion locutado para enviarla directamente al software de clonación de voz de Ricardo, o prefieres ajustar algún detalle visual de las escenas antes de lanzar el Día 1?
