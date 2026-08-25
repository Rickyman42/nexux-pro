#!/bin/bash
# Plano 3: el zumbido de los mensajes, cuadrado con los destellos de la pantalla.
#
# El movil esta boca arriba sobre una mesa de madera en una sala en silencio.
# Lo que se oye no es un tono de aviso, es el motor de vibracion golpeando la
# madera: grave, corto y con un traqueteo. Cinco veces, en las mismas rafagas
# que la pantalla: dos, pausa, uno, pausa, dos.
set -e

IN=/tmp/p3-movil.mp4
OUT=/tmp/p3-final.mp4
BUZZ=/tmp/buzz.wav

# Los mismos instantes que los destellos, en milisegundos
T=(900 1850 3750 5700 6600)

echo "== el zumbido =="
# Dos tonos graves + tremolo = motor de vibracion contra madera
ffmpeg -y -loglevel error \
  -f lavfi -i "sine=frequency=132:duration=0.34:sample_rate=48000" \
  -f lavfi -i "sine=frequency=87:duration=0.34:sample_rate=48000" \
  -filter_complex "[0:a][1:a]amix=inputs=2:normalize=0,\
tremolo=f=58:d=0.85,\
afade=t=in:d=0.015,afade=t=out:st=0.25:d=0.09,\
highpass=f=60,lowpass=f=900,\
volume=0.5,aformat=channel_layouts=stereo:sample_rates=48000" \
  "$BUZZ"
ffprobe -v error -show_entries format=duration -of default=nw=1 "$BUZZ"

echo "== mezcla con el ambiente original =="
ENTRADAS="-i $IN"
FILTRO=""
ETIQUETAS=""
for i in "${!T[@]}"; do
  ENTRADAS="$ENTRADAS -i $BUZZ"
  n=$((i + 1))
  FILTRO="${FILTRO}[${n}:a]adelay=${T[$i]}|${T[$i]}[b${n}];"
  ETIQUETAS="${ETIQUETAS}[b${n}]"
done

ffmpeg -y -loglevel error $ENTRADAS \
  -filter_complex "${FILTRO}[0:a]${ETIQUETAS}amix=inputs=$(( ${#T[@]} + 1 )):normalize=0:duration=first,\
alimiter=limit=0.95,aformat=sample_rates=48000[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest "$OUT"

echo "== comprobacion: nivel de audio segundo a segundo =="
python3 - <<'PY'
import subprocess, re
for etiqueta, f in (("original ", "/tmp/p3-movil.mp4"), ("con zumbido", "/tmp/p3-final.mp4")):
    picos = []
    for t in (0.5, 1.0, 1.9, 2.8, 3.8, 5.0, 5.8, 6.7):
        p = subprocess.run(
            ["ffmpeg","-v","error","-ss",str(t),"-t","0.25","-i",f,
             "-af","volumedetect","-f","null","-"],
            capture_output=True, text=True)
        m = re.search(r"max_volume: (-?[\d.]+) dB", p.stderr)
        picos.append("%.0f" % float(m.group(1)) if m else "--")
    print("%-12s %s" % (etiqueta, "  ".join("t%.1f=%sdB" % (t, v) for t, v in
          zip((0.5,1.0,1.9,2.8,3.8,5.0,5.8,6.7), picos))))
PY
ls -la "$OUT"
