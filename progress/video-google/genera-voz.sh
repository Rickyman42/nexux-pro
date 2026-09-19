#!/usr/bin/env bash
# La voz en off del video de verificacion de Google, bloque a bloque.
#
# Se generan por separado a proposito: si Google devuelve el video pidiendo un
# cambio en una frase, se regenera ese bloque y no los seis. Y las duraciones
# reales son las que mandan el ritmo de la grabacion de pantalla.
set -u
cd /home/nexux/nexux-agents

K=$(grep -m1 '^ELEVENLABS_API_KEY=' .env | cut -d= -f2- | tr -d '"' | tr -d "'" | tr -d '\r')
V=$(grep -m1 '^ELEVENLABS_VOICE_ID=' .env | cut -d= -f2- | tr -d '"' | tr -d "'" | tr -d '\r')
OUT=/home/nexux/nexux-pro/progress/video-google/voz
mkdir -p "$OUT"

di() {  # $1 = numero de bloque, $2 = texto
  local n="$1" texto="$2"
  local f="$OUT/bloque-$n.mp3"
  local code
  code=$(node -e '
    const t = process.argv[1];
    process.stdout.write(JSON.stringify({
      text: t,
      model_id: "eleven_multilingual_v2",
      voice_settings: { stability: 0.5, similarity_boost: 0.75, style: 0.0, use_speaker_boost: true }
    }));
  ' "$texto" | curl -s -w '%{http_code}' -o "$f" -X POST \
      "https://api.elevenlabs.io/v1/text-to-speech/$V" \
      -H "xi-api-key: $K" -H 'Content-Type: application/json' --data-binary @-)

  if [ "$code" != "200" ]; then
    echo "  bloque $n: FALLO http $code"
    head -c 200 "$f"; echo
    return 1
  fi
  local dur
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  printf "  bloque %s ... %5.1f s  (%s)\n" "$n" "$dur" "$(du -h "$f" | cut -f1)"
}

echo "Generando la voz en ingles, bloque a bloque."
echo

di 1 "This is Nexux Recepcionista IA, a booking assistant for hair and beauty salons in Spain. Our website is nexux dot pro. The OAuth client ID for this application is 839053342621-q5g6uo97vfgae4ghaikcsug49j10hjkm dot apps dot googleusercontent dot com."

di 2 "Salon owners sign in to their own dashboard. Here they manage their appointments, their staff and their clients. To keep their Google Calendar in sync, they connect it from the Channels section."

di 3 "When the owner clicks Connect, we send them to Google's consent screen. You can see our application name, Nexux Recepcionista IA, and our client ID in the address bar. We request two scopes: calendar dot events, and calendar dot calendarlist dot readonly."

di 4 "After granting access, we read the list of the user's calendars. This is what the calendarlist readonly scope is for. The owner chooses which calendar each staff member uses. Ana works from one calendar, and Marta from another. We never read the contents of these calendars, only their names, so the owner can pick the right one."

di 5 "Now the events scope. I create an appointment in the dashboard: a haircut with Ana, tomorrow at half past eleven. Nexux writes it to Ana's Google Calendar, with the client name, the service and the duration. Here it is in Google Calendar. If the appointment is moved or cancelled in the dashboard, we update or delete the same event, so the calendar always matches. We only create and manage appointments booked through Nexux."

di 6 "Calendar data stays between the salon and their own Google account. We do not sell it, we do not share it with third parties, and we do not use it for advertising or to train any model. Owners can disconnect at any time from the same screen, and we delete the stored token. Thank you."

echo
echo "Total:"
TOTAL=0
for f in "$OUT"/bloque-*.mp3; do
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  TOTAL=$(node -e "console.log(($TOTAL + $d).toFixed(1))")
done
echo "  $TOTAL segundos de voz  (Google no pone limite, pero por debajo de 3 minutos se revisa antes)"
echo "  en $OUT"
