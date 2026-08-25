#!/bin/bash
# Plano 3: la pantalla del movil se enciende con MENSAJES entrantes.
#
# La diferencia entre una llamada y un mensaje es el ritmo: la llamada es un
# brillo largo y continuo; los mensajes son destellos cortos, y suelen venir
# en pareja. Aqui: dos seguidos, pausa, uno, pausa, dos seguidos.
set -e

IN=/tmp/p3.mp4
GLOW=/tmp/glow.png
OUT=/tmp/p3-movil.mp4

# Cada destello: enciende rapido, se mantiene poco, se apaga en algo mas
sub() {  # $1 = etiqueta de entrada, $2 = instante, $3 = salida
  echo "[$1]fade=t=in:st=$2:d=0.06:alpha=1,fade=t=out:st=$(echo "$2+0.30" | bc):d=0.20:alpha=1[$3];"
}

ffmpeg -y -loglevel error \
  -i "$IN" -loop 1 -t 8 -i "$GLOW" \
  -filter_complex "\
[1:v]format=rgba,split=5[a][b][c][d][e];\
$(sub a 0.90 p1)\
$(sub b 1.85 p2)\
$(sub c 3.75 p3)\
$(sub d 5.70 p4)\
$(sub e 6.60 p5)\
[0:v][p1]overlay=0:0[o1];\
[o1][p2]overlay=0:0[o2];\
[o2][p3]overlay=0:0[o3];\
[o3][p4]overlay=0:0[o4];\
[o4][p5]overlay=0:0,format=yuv420p[v]" \
  -map "[v]" -map 0:a? -c:v libx264 -crf 18 -preset medium -c:a copy \
  "$OUT"

echo "== brillo de la pantalla, momento a momento =="
python3 - <<'PY'
from PIL import Image, ImageStat
import subprocess
ZONA = (258, 584, 495, 640)
for t in ("0.5", "1.0", "1.4", "1.75", "2.6", "3.8", "5.0", "5.95", "6.65"):
    vals = {}
    for etiqueta, f in (("o", "/tmp/p3.mp4"), ("m", "/tmp/p3-movil.mp4")):
        subprocess.run(["ffmpeg","-y","-loglevel","error","-ss",t,"-i",f,
                        "-frames:v","1","/tmp/_m.png"], check=True)
        vals[etiqueta] = ImageStat.Stat(
            Image.open("/tmp/_m.png").convert("L").crop(ZONA)).mean[0]
    d = vals["m"] - vals["o"]
    print("t=%-5s  %+6.1f  %s" % (t, d, "MENSAJE" if d > 10 else ""))
PY
