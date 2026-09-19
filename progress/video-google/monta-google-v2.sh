#!/usr/bin/env bash
# Version 2 del video de verificacion de Google.
#
# Que cambia respecto a la v1: la pantalla de consentimiento se regrabo el
# 10-sep-2026 despues de quitar include_granted_scopes del codigo. En la v1
# salian TRES permisos (uno de ellos, calendar.readonly, ni siquiera esta
# declarado en Google Cloud). Ahora salen los DOS que la app pide de verdad.
#
# Fuentes:
#   toma-google-reparada.mp4  -> la demo (calendario, cita, cancelacion)
#   toma3-reparada.mp4        -> el flujo de permiso, regrabado
#
# El tratamiento de imagen es el mismo en las dos: se quita la franja de
# y=60 a y=158 (marcadores + aviso de depuracion) y se conserva la barra de
# direcciones, que es donde se lee el client_id.
set -eu

BASE="$(cd "$(dirname "$0")" && pwd)"
NUEVA="$BASE/toma3-reparada.mp4"
VOZ="$BASE/voz"
TR="$BASE/trabajo"
OUT="$BASE/nexux-google-calendar-verification.mp4"
FUENTE="$BASE/fuente.ttf"

LIMPIA="[0:v]crop=1536:60:0:0,setpts=PTS-STARTPTS[a];[0:v]crop=1536:664:0:158,setpts=PTS-STARTPTS[b];[a][b]vstack=inputs=2"

# La columna de cuentas de Google, tapada: son 8 correos personales y esto va
# a YouTube. La URL de esa pantalla se deja a la vista a proposito: es el unico
# fotograma donde se lee el client_id entero.
CAJA=",drawbox=x=955:y=245:w=581:h=479:color=0x101114@1.0:t=fill\
,drawtext=fontfile=fuente.ttf:text='Other Google accounts':fontcolor=0x9aa0a6:fontsize=22:x=985:y=430\
,drawtext=fontfile=fuente.ttf:text='hidden for privacy':fontcolor=0x9aa0a6:fontsize=22:x=985:y=462"

# nombre  entrada  duracion  velocidad  que se ve
NUEVOS="
n02  15.5  11.5  1.0   el selector de cuentas, con el client_id en la URL
n03  30    44    2.0   aviso de app no verificada, Configuracion avanzada, Ir a Nexux
n04  74    26    1.6   consentimiento: nombre de la app, la cuenta y DOS servicios
n05  104   22    1.0   los dos permisos, escritos
n06  130   13    2.0   Hecho, Continuar y vuelta al panel
n07  144   10    1.0   el panel ya dice CONECTADO
"

echo "== 1. Se cortan los trozos regrabados =="
cd "$BASE"
while read -r N IN DUR VEL RESTO; do
  [ -z "${N:-}" ] && continue
  EXTRA=""
  [ "$N" = "n02" ] && EXTRA="$CAJA"
  ffmpeg -nostdin -y -loglevel error -ss "$IN" -t "$DUR" -i "$NUEVA" \
    -filter_complex "${LIMPIA},setpts=PTS/${VEL}${EXTRA},fps=25[v]" \
    -map "[v]" -an -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p "$TR/$N.mp4"
  D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$TR/$N.mp4" < /dev/null)
  printf "  %s  dura %5.1f s   %s\n" "$N" "$D" "$RESTO"
done <<< "$NUEVOS"

echo
echo "== 2. Orden final: el panel de la v1, el permiso regrabado, y la demo de la v1 =="
: > "$TR/orden2.txt"
for F in c01 n02 n03 n04 n05 n06 n07 c08 c09 c10 c11 c12 c13 c14 c15 c16; do
  echo "file '$F.mp4'" >> "$TR/orden2.txt"
done
ACUM=0
while read -r _ F _; do
  F=$(echo "$F" | tr -d "'")
  D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$TR/$F" < /dev/null)
  printf "  %-8s empieza en %6.1f s  dura %5.1f s\n" "$F" "$ACUM" "$D"
  ACUM=$(node -e "console.log(($ACUM + $D).toFixed(2))")
done < "$TR/orden2.txt"
echo "  total: $ACUM s"

ffmpeg -nostdin -y -loglevel error -f concat -safe 0 -i "$TR/orden2.txt" -c copy "$TR/mudo2.mp4"

echo
echo "== 3. La voz, cada bloque donde ocurre lo que cuenta =="
ffmpeg -nostdin -y -loglevel error \
  -i "$TR/mudo2.mp4" \
  -i "$VOZ/bloque-1.mp3" -i "$VOZ/bloque-2.mp3" -i "$VOZ/bloque-3.mp3" \
  -i "$VOZ/bloque-4.mp3" -i "$VOZ/bloque-5.mp3" -i "$VOZ/bloque-6.mp3" \
  -filter_complex "\
[1:a]adelay=200|200[v1];\
[2:a]adelay=23000|23000[v2];\
[3:a]adelay=57000|57000[v3];\
[4:a]adelay=111500|111500[v4];\
[5:a]adelay=145000|145000[v5];\
[6:a]adelay=194000|194000[v6];\
[v1][v2][v3][v4][v5][v6]amix=inputs=6:normalize=0:duration=longest,aresample=48000[voz]" \
  -map 0:v -map "[voz]" -c:v copy -c:a aac -b:a 192k "$TR/con-voz2.mp4"

echo "== 4. Los rotulos =="
cat > "$TR/rotulos2.txt" <<'ROT'
drawtext=fontfile=fuente.ttf:text='OAuth Client ID  839053342621-q5g6uo97vfgae4ghaikcsug49j10hjkm.apps.googleusercontent.com':fontcolor=white:fontsize=21:box=1:boxcolor=black@0.8:boxborderw=12:x=(w-text_w)/2:y=h-64:enable='between(t,1,33.5)',
drawtext=fontfile=fuente.ttf:text='The two scopes Nexux requests  —  calendar.events  and  calendar.calendarlist.readonly':fontcolor=white:fontsize=23:box=1:boxcolor=black@0.8:boxborderw=12:x=(w-text_w)/2:y=h-64:enable='between(t,72,94)',
drawtext=fontfile=fuente.ttf:text='calendar.calendarlist.readonly  —  we read only the names of the calendars, so the owner can pick one':fontcolor=white:fontsize=23:box=1:boxcolor=black@0.8:boxborderw=12:x=(w-text_w)/2:y=h-64:enable='between(t,111,126)',
drawtext=fontfile=fuente.ttf:text='calendar.events  —  create, update and delete the appointments booked through Nexux':fontcolor=white:fontsize=23:box=1:boxcolor=black@0.8:boxborderw=12:x=(w-text_w)/2:y=h-64:enable='between(t,133,178)',
drawtext=fontfile=fuente.ttf:text='Appointment cancelled in Nexux  —  the event is deleted from Google Calendar':fontcolor=white:fontsize=23:box=1:boxcolor=black@0.8:boxborderw=12:x=(w-text_w)/2:y=h-64:enable='between(t,188.5,201.8)'
ROT
tr -d '\n' < "$TR/rotulos2.txt" > "$TR/rotulos2-1linea.txt"

ffmpeg -nostdin -y -loglevel error -i "$TR/con-voz2.mp4" \
  -filter_complex_script "$TR/rotulos2-1linea.txt" \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -c:a copy "$OUT"

echo
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT" < /dev/null)
printf "Listo: %s\n  dura %.0f s (%d min %02d s)\n" "$OUT" "$D" "$(node -e "console.log(Math.floor($D/60))")" "$(node -e "console.log(Math.round($D%60))")"
ls -lh "$OUT" | awk '{print "  pesa "$5}'
