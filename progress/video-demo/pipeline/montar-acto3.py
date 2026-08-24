# -*- coding: utf-8 -*-
"""Acto 3: el producto funcionando de verdad, con rotulos.

Se recorta la grabacion real (1080p) en dos tramos y se aceleran los tiempos muertos:
en la grabacion hay esperas de 9 segundos mientras el bot piensa, y en video eso mata
el ritmo. Los rotulos van en la paleta CLARA de la web (blanco / #14161A / #2A8B84),
no en el negro que ya no existe en la marca.
"""
import glob, os, subprocess

OUT = os.path.expanduser("~/brand-assets/video")
TMP = "/tmp/acto3"
os.makedirs(OUT, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

W, H = 1920, 1080
TINTA, SUAVE, TEAL = "#14161A", "#5B5F66", "#2A8B84"

FUENTE = sorted(glob.glob("/tmp/video-1080b/*.webm"), key=os.path.getmtime)[-1]


def rotulo(nombre, texto, remate):
    """Banda inferior clara con el rotulo, en PNG con transparencia."""
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">'
           '<rect x="0" y="%d" width="%d" height="200" fill="#FFFFFF" fill-opacity="0.93"/>'
           '<rect x="0" y="%d" width="%d" height="3" fill="%s"/>'
           '<text x="%d" y="%d" text-anchor="middle" font-family="Instrument Serif" font-size="66" fill="%s">%s</text>'
           '<text x="%d" y="%d" text-anchor="middle" font-family="Geist" font-size="34" font-weight="600" fill="%s">%s</text>'
           '</svg>' % (W, H, W, H,
                       H - 200, W,
                       H - 200, W, TEAL,
                       W // 2, H - 118, TINTA, texto,
                       W // 2, H - 58, TEAL, remate))
    p_svg, p_png = os.path.join(TMP, nombre + ".svg"), os.path.join(TMP, nombre + ".png")
    with open(p_svg, "w", encoding="utf-8") as f:
        f.write(svg)
    subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H), p_svg, "-o", p_png], check=True)
    return p_png


def tramo(nombre, desde, hasta, velocidad, png_rotulo):
    """Recorta, acelera y superpone el rotulo con entrada y salida suaves."""
    salida = os.path.join(TMP, nombre + ".mp4")
    dur = (hasta - desde) / velocidad
    filtro = (
        "[0:v]trim=start=%s:end=%s,setpts=(PTS-STARTPTS)/%s,scale=%d:%d[v];"
        "[1:v]format=rgba,fade=t=in:st=0.6:d=0.6:alpha=1,fade=t=out:st=%.2f:d=0.6:alpha=1[r];"
        "[v][r]overlay=0:0,fade=t=in:st=0:d=0.4,fade=t=out:st=%.2f:d=0.4,format=yuv420p"
        % (desde, hasta, velocidad, W, H, max(dur - 1.2, 0.1), max(dur - 0.4, 0.1))
    )
    subprocess.run(["ffmpeg", "-y", "-i", FUENTE, "-loop", "1", "-i", png_rotulo,
                    "-filter_complex", filtro, "-t", "%.2f" % dur,
                    "-r", "25", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    salida], check=True, capture_output=True)
    return salida


r1 = rotulo("rot1", "Contesta sola. A cualquier hora.", "Sin que t&#250; toques nada")
r2 = rotulo("rot2", "Y la cita queda puesta sola.", "En tu agenda, al momento")

# Tramo A: llega el mensaje y Lara responde con horarios. Acelerado, que el bot tarda.
a = tramo("a", 6, 26, 1.8, r1)
# Tramo B: la confirmacion y la cita entrando en el calendario. Casi a tiempo real,
# porque es el momento que hay que ver bien.
b = tramo("b", 38, 53, 1.15, r2)

lista = os.path.join(TMP, "lista.txt")
with open(lista, "w") as f:
    for c in (a, b):
        f.write("file '%s'\n" % c)

final = os.path.join(OUT, "acto3-el-producto.mp4")
subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lista,
                "-c", "copy", final], check=True, capture_output=True)
d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                    "-of", "csv=p=0", final], capture_output=True, text=True).stdout.strip()
print("acto3-el-producto.mp4   %.1f s" % float(d))
