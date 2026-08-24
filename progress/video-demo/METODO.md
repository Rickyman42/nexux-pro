# MÉTODO DE PRODUCCIÓN — Gemini Notebook + Flow (modo agente)

> Adaptado de **"Hice un documental estilo Vox por 0 € con Google Flow"** — Topflow AI, 26:54,
> 18-ago-2026. https://youtu.be/oJU5QG0m998 · Tutorial y prompts:
> https://cafeconia.substack.com/p/gemini-notebook-google-flow-videos
> Subtítulos completos en `fuentes/documental-flow-topflow.srt`.
>
> **Copiamos la máquina, no la estética.** Su pieza es estilo Vox (capas de papel, periódico).
> La nuestra es **hiperrealista**. Y su motor escribe el guion desde un tema; nosotros **ya tenemos
> guion** y no se toca: `GUION.md` manda sobre cualquier cosa que sugiera el motor.

---

## 1. DOS COSAS QUE ESTE VÍDEO ME CORRIGE

**1. NotebookLM sí sirve — como director, no como generador.**
Le dije a Ricardo que no valía porque pensé que quería que NotebookLM *hiciera* el vídeo. Lo que hace
es lo otro y es mejor: se le da un prompt maestro como fuente, te entrevista, y devuelve la escaleta
por tiempos, los prompts de Flow escena a escena, el prompt del storyboard, el de la música y el
texto de locución. Es el cerebro que reparte el trabajo. Ricardo lo recordaba bien.

**2. Los créditos dan mucho más de lo que calculé.**
Con **Omni Flash** en modo agente, un clip de **10 s cuesta 15 créditos**. Los 50 gratis diarios dan
**3 clips = 30 s de metraje al día**, no 2 clips cortos. Nuestros 11 planos de Flow salen en **~4
días gratis** en primera pasada, ~8 con reintentos. Mi estimación anterior (2 semanas) estaba mal
porque la hice con precios de Veo, que es otro modelo y otro coste.
⚠️ Dato con fecha: el 18-ago Flow avisaba de **50 créditos extra al día hasta el 31-ago**, y no está
claro si los 50 de base siguen después. Hay que mirarlo el día que se empiece, no darlo por hecho.

---

## 2. LA CADENA COMPLETA

```
GUION.md  →  Gemini Notebook (motor)  →  storyboard (imagen)  ┐
                     │                                         ├→ Flow modo agente → clips
                     ├→ prompts de Flow por escena  ───────────┘
                     ├→ prompt de música      → Google Flow Music → mp3
                     └→ texto de locución     → MiniMax Audio     → mp3
                                                                        ↓
   capturas reales del CRM y de WhatsApp  ──────────────────────→  CapCut → vídeo final
```

| Herramienta | Para qué | Coste |
|---|---|---|
| [Gemini Notebook](https://notebooklm.google/) (ex-NotebookLM) | El director: escaleta, prompts, storyboard, reparto por días | gratis |
| [Google Flow](https://labs.google/fx/tools/flow) | Genera imágenes y clips | 50 créditos/día gratis |
| [Google Flow Music](https://www.flowmusic.app/) | Música de fondo | gratis para probar |
| [MiniMax Audio](https://www.minimax.io/audio) | Locución TTS, o **clonar la voz de Ricardo** | créditos de prueba |
| CapCut | Montaje, rótulos, orden | gratis |

---

## 3. CÓMO SE CONFIGURA (paso a paso, del tutorial)

1. **Gemini Notebook → cuaderno nuevo → Añadir fuentes → Texto copiado.** Se pega el prompt maestro
   (el nuestro, §5) **y** el `GUION.md` entero como segunda fuente.
2. **Configurar cuaderno → "Define el objetivo, el estilo o el rol" → Personalizado.** Se pega la
   versión corta del maestro. Guardar.
3. Se escribe cualquier cosa ("hola") y el motor **hace las preguntas** y devuelve los bloques.
4. **Bloque storyboard** → devuelve una **imagen** con todas las escenas. Se descarga.
5. **Google Flow → proyecto nuevo → modo agente ACTIVADO → ajustes → modelo `Omni Flash`**
   (⚠️ *no* Veo) y relación **16:9**. Guardar.
6. Se **pega la imagen del storyboard** en Flow y debajo el **prompt del agente**.
7. El agente genera **primero todas las imágenes y luego todos los clips**, de una tacada, y les pone
   nombre por escena. No hay que ir uno por uno ni usar "extender".
8. **Descargar proyecto** (los dos puntitos) → baja todos los clips juntos.
9. Música y voz aparte, y montaje en CapCut.

### El reparto por días — lo que Ricardo quería
Si en la entrevista se le dice que la cuenta es **gratuita**, el motor calcula el coste, detecta que
no cabe en 50 créditos y **parte los prompts en tandas**: escenas 1-3 hoy, 4-6 mañana, pegando el
**mismo bloque global** en ambas tandas. No hay que reconfigurar nada entre días.

---

## 4. LO QUE NO COPIAMOS DE SU MÉTODO

| Suyo | Nuestro | Por qué |
|---|---|---|
| Estética Vox: capas de papel, periódico, infografía | **Hiperrealista**, luz natural, foco corto | Vendemos un producto real a un dueño de negocio real, no explicamos un tema |
| El motor escribe el guion desde un tema | **El guion ya existe y manda** | `GUION.md` está aprobado. El motor lo *ejecuta*, no lo reescribe |
| Todas las escenas generadas | **Dos planos son captura real** (P7 WhatsApp, P8 CRM) | Regla que manda: la pantalla de Nexux nunca la genera una IA |
| Locución en off por defecto | **Decisión pendiente** (§6) | El guion decidió expresamente no llevar voz en off |

---

## 5. PROMPT MAESTRO — versión Nexux (para pegar como fuente)

```
MASTER PROMPT — MOTOR DE ANUNCIO HIPERREALISTA (MODO LOTE)

ROL
Eres director de fotografía y productor de un anuncio de producto de 75 segundos.
Trabajas para Nexux. NO eres guionista: el guion ya está escrito, aprobado y es
intocable. Está en la fuente "GUION.md". Tu trabajo es convertirlo en material
rodable, no mejorarlo, resumirlo ni reordenarlo.

REGLAS INVIOLABLES
1. El texto de los rótulos sale LITERAL del guion. No lo reescribas.
2. Estética HIPERREALISTA: fotografía real, luz natural cálida, profundidad de
   campo corta. Nada de ilustración, collage, papel, infografía ni animación 2D.
3. NUNCA generes un plano donde se lea una interfaz, una pantalla con texto, una
   hora, un nombre o un precio. Las pantallas de producto son capturas reales que
   se insertan después. Si un plano necesita un móvil, va con la PANTALLA APAGADA.
4. Ningún prompt debe pedir texto en imagen. Todos llevan "no text anywhere, no
   logos". Los rótulos se ponen luego en CapCut.
5. Los planos P7 y P8 del guion NO se generan: son captura real. Deja su hueco en
   la escaleta marcado como [CAPTURA REAL] y no gastes créditos en ellos.
6. Hay un PERSONAJE FIJO que aparece en varios planos. Defínelo una vez y llámalo
   con @ en todos los prompts donde salga.
7. Los prompts de Flow van en INGLÉS. Todo lo demás, en español.

ANTES DE EMPEZAR, PREGÚNTAME
1. Formato de pantalla (16:9 / 9:16).
2. Duración total y número de planos generados.
3. Tipo de cuenta de Flow: gratuita (50 créditos/día) o de pago.
4. ¿Música de fondo? ¿Locución? Si hay locución: voz del modelo o TTS externo.
5. Descripción del personaje fijo.
6. Ambiente sonoro deseado por acto.

LUEGO DEVUELVE, EN ESTE ORDEN
BLOQUE 1 · ESCALETA por tiempos: plano, segundos, qué se ve, rótulo literal del
guion, recurso (FLOW / CAPTURA REAL / COMPOSICIÓN), y coste en créditos.
BLOQUE 2 · PROMPT DE STORYBOARD para que tú mismo generes la imagen del
storyboard con todas las escenas en estilo fotográfico realista.
BLOQUE 3 · PROMPT PARA EL AGENTE DE GOOGLE FLOW, listo para pegar, que genere
todas las imágenes y luego todos los clips. Modelo Omni Flash.
BLOQUE 4 · PROMPT DE MÚSICA en inglés para Google Flow Music.
BLOQUE 5 · TEXTO DE LOCUCIÓN para TTS, si se ha pedido locución, cronometrado a
la duración exacta.
BLOQUE 6 · REPARTO POR DÍAS. Si la cuenta es gratuita, calcula el coste total y
parte el BLOQUE 3 en tandas que quepan en 50 créditos diarios, indicando qué
escenas van cada día. El bloque global se repite igual en cada tanda.
```

**Versión corta para "Personalización" del cuaderno:**

```
Actúa según el documento "MASTER PROMPT — MOTOR DE ANUNCIO HIPERREALISTA (MODO
LOTE)" que tienes en las fuentes, y usando "GUION.md" como guion cerrado e
intocable. Hazme primero las 6 preguntas y no generes nada hasta que las conteste.
```

---

## 6. DECISIÓN PENDIENTE — la voz

El guion decidió, a propósito: *"Nada de voz en off ni avatar. Una voz genérica de IA leyendo
ventajas envejece mal y suena a anuncio."* Y: *"tiene que entenderse sin sonido"*.

Lo que cambia con este método: **MiniMax permite clonar la voz de Ricardo** (10-60 s de audio, o un
fichero). Eso ya no es "una voz genérica de IA": es la voz del dueño contando su producto, que es
exactamente el registro Miralles. Tres caminos:

| | Qué implica |
|---|---|
| **A · Sin voz** (lo aprobado) | Rótulos + sonido ambiente. Se entiende sin auriculares. Es lo más seguro |
| **B · Voz de Ricardo clonada** | Más cercano y más difícil de copiar. Obliga a mantener también los rótulos, porque el 80 % lo verá en silencio |
| **C · Sin voz en la web, con voz en la versión de redes** | Dos montajes desde el mismo material. Cuesta un rato más de CapCut, nada de créditos |

Sin decisión de Ricardo, se produce en **A** y se deja el material listo por si se quiere B.
