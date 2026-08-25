#!/bin/bash
# Plano 3: enciende la pantalla del movil en post, tres veces.
#
# El primer intento uso geq con una expresion de transparencia en funcion del
# tiempo y NO aplico nada (diferencia de brillo medida: +0,1). Aqui se hace con
# fade sobre el canal alfa, que es aburrido pero funciona.
set -e

IN=/tmp/p3.mp4
GLOW=/tmp/glow.png
OUT=/tmp/p3-movil.mp4

ffmpeg -y -loglevel error \
  -i "$IN" -loop 1 -t 8 -i "$GLOW" \
  -filter_complex "\
[1:v]format=rgba,split=3[a][b][c];\
[a]fade=t=in:st=1.00:d=0.10:alpha=1,fade=t=out:st=1.55:d=0.40:alpha=1[p1];\
[b]fade=t=in:st=3.50:d=0.10:alpha=1,fade=t=out:st=4.05:d=0.40:alpha=1[p2];\
[c]fade=t=in:st=5.90:d=0.10:alpha=1,fade=t=out:st=6.45:d=0.40:alpha=1[p3];\
[0:v][p1]overlay=0:0[o1];\
[o1][p2]overlay=0:0[o2];\
[o2][p3]overlay=0:0,format=yuv420p[v]" \
  -map "[v]" -map 0:a? -c:v libx264 -crf 18 -preset medium -c:a copy \
  "$OUT"

echo "== medicion: brillo de la zona de la pantalla =="
python3 - <<'PY'
from PIL import Image, ImageStat
import subprocess
ZONA = (258, 584, 495, 640)
for t in ("0.5", "1.2", "2.4", "3.7", "6.1"):
    for etiqueta, f in (("original", "/tmp/p3.mp4"), ("procesado", "/tmp/p3-movil.mp4")):
        subprocess.run(["ffmpeg","-y","-loglevel","error","-ss",t,"-i",f,
                        "-frames:v","1","/tmp/_m.png"], check=True)
        v = ImageStat.Stat(Image.open("/tmp/_m.png").convert("L").crop(ZONA)).mean[0]
        if etiqueta == "original":
            o = v
        else:
            marca = "  <-- ENCENDIDA" if v - o > 8 else ""
            print("t=%-4s  original %5.1f   procesado %5.1f   (%+5.1f)%s" % (t, o, v, v - o, marca))
PY
