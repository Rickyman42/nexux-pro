#!/bin/bash
# Plano 8 — la cita entrando sola EN NUESTRO CRM.
#
# Se capturan los dos estados reales del panel (sin la cita / con la cita) y el
# corte se hace en el montaje. Nada simulado: las dos capturas son del CRM de
# verdad, con la cita que Lara reserva por el otro lado.
set -e
cd /home/nexux/nexux-clients

echo "== dejar libre el hueco de las 18:00 =="
node limpia-pruebas.mjs 2>&1 | tail -2

echo "== estado ANTES =="
node crm-dos-estados.cjs antes

echo "== Lara atiende y reserva =="
node conversa-rodaje.mjs --tel 34600333777 --nombre "Elena Vidal" --pausa 1400 > /tmp/c4.log 2>&1
grep -A2 "Citas a nombre" /tmp/c4.log | head -2
sleep 4

echo "== estado DESPUES =="
node crm-dos-estados.cjs despues

echo "== recortar el encuadre =="
/home/nexux/brand-assets/.venv/bin/python - <<'PY'
from PIL import Image
# No se recorta nada: la ventana es 1600x900 (ya 16:9) y la pagina va alejada
# al 74%, asi que la marca, el nombre del negocio y la tarde entera caben dentro.
# Solo se baja de 2x a 1280x720. Recortar fue el error anterior: salia una rejilla
# flotando, sin nada que dijera que el sistema es nuestro.
CAJA = (0, 0, 3200, 1800)
for fase in ("antes", "despues"):
    im = Image.open(f"/tmp/crm-{fase}.png").crop(CAJA).resize((1280, 720), Image.LANCZOS)
    im.save(f"/tmp/p8-{fase}.png")
    print(f"  {fase}: recortado a {im.size}")
PY

echo "== montar los 8 segundos =="
ffmpeg -y -loglevel error \
  -i /tmp/p8-antes.png \
  -i /tmp/p8-despues.png \
  -filter_complex "[0:v]scale=1408:-2,zoompan=z='min(1+0.00022*on,1.02)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=84:s=1280x720:fps=24[a];\
[1:v]scale=1408:-2,zoompan=z='min(1.019+0.00022*on,1.04)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=108:s=1280x720:fps=24[b];\
[a][b]concat=n=2:v=1:a=0,format=yuv420p[v]" \
  -map "[v]" -c:v libx264 -crf 18 -preset medium -r 24 /tmp/P08-crm.mp4

ffprobe -v error -show_entries format=duration -show_entries stream=width,height,nb_frames -of default=nw=1 /tmp/P08-crm.mp4
ls -la /tmp/P08-crm.mp4
