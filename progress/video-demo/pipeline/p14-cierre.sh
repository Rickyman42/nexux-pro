#!/bin/bash
# Plano 14 — el cierre del anuncio. 5 s, 1280x720, 24 fps.
#
# Dos trampas ya pisadas, por si alguien toca esto:
#
#  1. zoompan: el parametro d NO son los fotogramas totales, son los de salida
#     POR CADA fotograma de entrada. Con -loop 1 -t 5 entran 120 imagenes y
#     salieron 120x120 = un video de 625 segundos. Se le mete UNA sola imagen.
#
#  2. fade=t=in entra desde NEGRO. Sobre una tarjeta crema eso es un fogonazo
#     oscuro entre planos. Se entra desde el color de fondo: una capa del propio
#     crema que se desvanece encima.
set -e

CARD=/tmp/cierre.png
OUT=/tmp/P14-cierre.mp4
FONDO=0xF7F6F3        # el crema de la marca
FPS=24
SEG=5
URL="https://nexux.pro/demo"

ffmpeg -y -loglevel error \
  -i "$CARD" \
  -f lavfi -t $SEG -i "color=c=$FONDO:s=1280x720:r=$FPS" \
  -filter_complex "\
[0:v]scale=2560:-2,\
zoompan=z='min(1+0.00025*on,1.03)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=$((FPS*SEG)):s=1280x720:fps=$FPS[base];\
[1:v]format=rgba,fade=t=out:st=0:d=0.45:alpha=1[velo];\
[base][velo]overlay=0:0,format=yuv420p[v]" \
  -map "[v]" -c:v libx264 -crf 17 -preset medium -r $FPS -t $SEG "$OUT"

echo "== el fichero =="
ffprobe -v error -show_entries format=duration -show_entries stream=width,height,nb_frames,r_frame_rate -of default=nw=1 "$OUT"

echo "== que no entre desde negro: brillo del primer fotograma =="
ffmpeg -y -loglevel error -ss 0 -i "$OUT" -frames:v 1 /tmp/_f0.png
ffmpeg -y -loglevel error -ss 2.5 -i "$OUT" -frames:v 1 /tmp/_f25.png
/home/nexux/brand-assets/.venv/bin/python - <<PY
from PIL import Image, ImageStat
import zxingcpp
f0 = ImageStat.Stat(Image.open("/tmp/_f0.png").convert("L")).mean[0]
f25 = ImageStat.Stat(Image.open("/tmp/_f25.png").convert("L")).mean[0]
print("  t=0.0s brillo %.1f   t=2.5s brillo %.1f" % (f0, f25))
print("  entra desde el crema" if f0 > 200 else "  OJO: sigue entrando oscuro")

print("== el QR, sobre el video ya comprimido ==")
import subprocess
ok = True
for t in ("0.6", "2.5", "4.7"):
    subprocess.run(["ffmpeg","-y","-loglevel","error","-ss",t,"-i","$OUT",
                    "-frames:v","1","/tmp/_q.png"], check=True)
    r = zxingcpp.read_barcodes(Image.open("/tmp/_q.png"))
    bien = bool(r) and r[0].text == "$URL"
    ok = ok and bien
    print("  t=%ss  %s" % (t, r[0].text if bien else "FALLO"))
print("  QR legible en todo el plano" if ok else "  EL QR NO SOBREVIVE")
PY
