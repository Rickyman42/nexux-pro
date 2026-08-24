# -*- coding: utf-8 -*-
"""Monta los actos 2, 4 y 5 del video de presentacion.

Cada acto se compone de "estados": el texto va entrando linea a linea, de modo que
el espectador lee al ritmo que marca el guion y no de golpe. Cada estado se convierte
en un clip con un zoom lentisimo (para que nada quede muerto en pantalla) y se encadenan
con fundidos a negro, que sobre fondo oscuro se leen como el texto apareciendo.
"""
import base64, io, os, subprocess

OUT = os.path.expanduser("~/brand-assets/video")
TMP = "/tmp/actos"
os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

W, H = 1920, 1080
FONDO, TEXTO, SUAVE, TEAL = "#0B0D12", "#F0F2F5", "#8892A0", "#4ECDC4"

# ── QR real a la demo, el mismo del flyer ────────────────────────────
import segno
_b = io.BytesIO()
segno.make("https://nexux.pro/demo", error="h").save(
    _b, kind="png", scale=12, border=2, dark="#0B0D12", light="#FFFFFF")
QR = "data:image/png;base64," + base64.b64encode(_b.getvalue()).decode()


X = 210


def svg(cuerpo):
    return ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            'width="%d" height="%d" viewBox="0 0 %d %d">'
            '<rect width="%d" height="%d" fill="%s"/>%s</svg>' % (W, H, W, H, W, H, FONDO, cuerpo))


def linea(x, y, txt, tam=64, color=None, fuente="Instrument Serif", peso="normal", centrado=True):
    anchor = ' text-anchor="middle"' if centrado else ''
    px = W // 2 if centrado else x
    return ('<text x="%d" y="%d"%s font-family="%s" font-size="%d" font-weight="%s" fill="%s">%s</text>'
            % (px, y, anchor, fuente, tam, peso, color or TEXTO, txt))


def bloque(lineas, centro=None):
    """Coloca N lineas centradas verticalmente en el encuadre.
    lineas = [(texto, tam, color, fuente, peso, separacion_extra), ...]
    Antes se ponian coordenadas a mano y el texto quedaba en el tercio superior
    izquierdo con media pantalla vacia: en video eso se lee como un error."""
    alturas = [l[1] * 1.32 + (l[5] if len(l) > 5 else 0) for l in lineas]
    total = sum(alturas)
    y = (centro or H // 2) - total / 2 + alturas[0] * 0.78
    out = ""
    for i, l in enumerate(lineas):
        txt, tam = l[0], l[1]
        color = l[2] if len(l) > 2 and l[2] else TEXTO
        fuente = l[3] if len(l) > 3 and l[3] else "Instrument Serif"
        peso = l[4] if len(l) > 4 and l[4] else "normal"
        out += linea(X, int(y), txt, tam, color, fuente, peso)
        y += alturas[i]
    return out


def clip(nombre, cuerpo, dur, zoom=True):
    """Un estado -> un clip de video con zoom lento y fundidos."""
    p_svg, p_png = os.path.join(TMP, nombre + ".svg"), os.path.join(TMP, nombre + ".png")
    p_mp4 = os.path.join(TMP, nombre + ".mp4")
    with open(p_svg, "w", encoding="utf-8") as f:
        f.write(svg(cuerpo))
    subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H), p_svg, "-o", p_png], check=True)

    fps = 25
    frames = int(dur * fps)
    # Zoom del 100% al 103%: no se percibe como movimiento, pero evita la sensacion de foto fija
    # zoompan ancla la ampliacion en la esquina superior izquierda si no se le dan x/y:
    # el texto se iba hacia arriba y dejaba medio encuadre vacio abajo. Se centra.
    vf = (("zoompan=z='min(zoom+0.00035,1.03)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
           ":d=%d:s=%dx%d:fps=%d," % (frames, W, H, fps)) if zoom else "null,")
    vf += "fade=t=in:st=0:d=0.45,fade=t=out:st=%.2f:d=0.45,format=yuv420p" % max(dur - 0.45, 0.1)
    subprocess.run(["ffmpeg", "-y", "-loop", "1", "-i", p_png, "-t", str(dur),
                    "-vf", vf, "-r", str(fps), "-c:v", "libx264", "-preset", "medium",
                    "-crf", "18", p_mp4], check=True, capture_output=True)
    return p_mp4


def acto(nombre, estados):
    clips = [clip("%s_%02d" % (nombre, i), c, d) for i, (c, d) in enumerate(estados)]
    lista = os.path.join(TMP, nombre + ".txt")
    with open(lista, "w") as f:
        for c in clips:
            f.write("file '%s'\n" % c)
    final = os.path.join(OUT, nombre + ".mp4")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lista,
                    "-c", "copy", final], check=True, capture_output=True)
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", final], capture_output=True, text=True).stdout.strip()
    print("%-28s %5.1f s" % (os.path.basename(final), float(d)))
    return final


# == ACTO 2 — La pérdida ═════════════════════════════════════════════
a2 = [
    (bloque([("Cuando termines, mirar&#225;s.", 92)]), 2.6),
    (bloque([("Cuando termines, mirar&#225;s.", 92, SUAVE),
             ("Habr&#225; cuatro mensajes.", 92)]), 2.6),
    (bloque([("Cuando termines, mirar&#225;s.", 92, SUAVE),
             ("Habr&#225; cuatro mensajes.", 92, SUAVE),
             ("Dos ya no contestar&#225;n.", 92)]), 2.8),
    (bloque([("Y nunca sabr&#225;s", 132, TEAL),
             ("qui&#233;nes eran.", 132, TEAL)]), 4.0),
]


def objecion(pregunta, respuesta, respuesta2):
    return bloque([("&#8220;" + pregunta + "&#8221;", 62, SUAVE, "Geist", "500", 40),
                   (respuesta, 108),
                   (respuesta2, 108, TEAL)])


a4 = [
    (objecion("&#191;Y si contesta cualquier cosa?", "Pru&#233;bala t&#250; mismo.", "Sin registrarte."), 4.2),
    (objecion("&#191;Otro programa que aprender?", "Es tu WhatsApp.", "El de siempre."), 4.2),
    (objecion("&#191;Y si no me sirve?", "Te devolvemos el dinero.", "30 d&#237;as."), 4.2),
    (objecion("&#191;Cu&#225;nto?", "29 &#8364; al mes.", "Sin comisiones por cita."), 4.6),
]

a5 = [
    (bloque([("Una cosa antes", 76, SUAVE), ("de que sigas:", 76, SUAVE)]), 2.6),
    (bloque([("&#191;Cu&#225;ntos mensajes", 124),
             ("tienes ahora mismo", 124),
             ("sin abrir?", 124, TEAL)]), 4.4),
    ('<image href="%s" x="%d" y="%d" width="300" height="300"/>' % (QR, W // 2 - 430, H // 2 - 150) +
     linea(0, H // 2 - 40, "nexux.pro", 104, TEXTO, "Geist", "700", False).replace('x="0"', 'x="%d"' % (W // 2 - 80)) +
     linea(0, H // 2 + 30, "Recepcionista IA &#183; 29 &#8364;/mes", 46, SUAVE, "Geist", "normal", False).replace('x="0"', 'x="%d"' % (W // 2 - 80)) +
     linea(0, H // 2 + 100, "Escanea y pru&#233;bala sin registrarte", 40, TEAL, "Geist", "normal", False).replace('x="0"', 'x="%d"' % (W // 2 - 80)), 5.0),
]

print("montando...")
acto("acto2-la-perdida", a2)
acto("acto4-objeciones", a4)
acto("acto5-la-pregunta", a5)
