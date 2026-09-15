#!/bin/bash
# Comprueba la descarga EN PRODUCCION, por el mismo camino que un salon.
#
# No vale con probar la Pi: el portal esta en Vercel y cambia la cookie de
# sesion por el token de la Pi. Ese cambio es justo donde puede romperse, y no
# se ve desde ningun lado hasta que alguien pulsa el boton.
#
# Se usa el salon de DEMO, que es nuestro. No se toca ningun dato de nadie: es
# una lectura.

set -uo pipefail
CID=estudio-ricardo-demo-mostoles-946279
CFG=/home/nexux/nexux-clients/clients/$CID/config.json
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

TOKEN=$(python3 -c "import json;print(json.load(open('$CFG'))['accessToken'])" 2>/dev/null)
[ -z "$TOKEN" ] && { echo "no encuentro la sesion del salon de demo"; exit 1; }

fallos=0
comprueba() {
  if [ "$2" = "$3" ]; then printf '  %-50s -> OK\n' "$1"
  else printf '  %-50s -> MAL (esperaba %s, es %s)\n' "$1" "$2" "$3"; fallos=$((fallos+1)); fi
}

echo "=== 1. La Pi, en produccion ==="
COD=$(curl -s -o "$TMP/pi.csv" -w '%{http_code}' -H "Authorization: Bearer $TOKEN" \
      "https://pi.nexux.pro/client/$CID/exportar?que=clientes")
comprueba "responde con el fichero" 200 "$COD"
comprueba "empieza por la cabecera de columnas" 1 "$(head -1 "$TMP/pi.csv" | grep -c 'Nombre.*Telefono')"

echo
echo "=== 2. El portal en nexux.pro, que es el camino del salon ==="
# La cookie es lo que tiene el navegador del dueño despues de entrar.
CAB=$(curl -s -D- -o "$TMP/web.csv" -w '%{http_code}' \
      -H "Cookie: nexux_token=$TOKEN" \
      "https://nexux.pro/portal-api/exportar?clientId=$CID&que=clientes")
COD=$(echo "$CAB" | tail -1)
comprueba "responde con el fichero" 200 "$COD"
comprueba "lo manda para descargar" 1 "$(echo "$CAB" | grep -ci 'content-disposition: attachment')"
NOMBRE=$(echo "$CAB" | grep -i 'content-disposition' | sed 's/.*filename="\([^"]*\)".*/\1/' | tr -d '\r')
echo "       nombre del fichero: $NOMBRE"
comprueba "el nombre dice de quien es y de cuando" 1 \
  "$(echo "$NOMBRE" | grep -c '^clientes-.*-[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}\.csv$')"

echo
echo "=== 3. Y lo que hay dentro ==="
LINEAS=$(grep -c '' "$TMP/web.csv")
echo "       $((LINEAS - 1)) clientas + cabecera"
comprueba "lo de la web es igual que lo de la Pi" \
  "$(md5sum < "$TMP/pi.csv" | cut -d' ' -f1)" "$(md5sum < "$TMP/web.csv" | cut -d' ' -f1)"
comprueba "separa por punto y coma" 1 "$(head -1 "$TMP/web.csv" | grep -c ';')"
comprueba "lleva la marca de UTF-8" 1 "$(head -c 3 "$TMP/web.csv" | od -An -tx1 | grep -c 'ef bb bf')"

echo
echo "=== 4. Sin sesion no se lleva nada ==="
COD=$(curl -s -o /dev/null -w '%{http_code}' "https://nexux.pro/portal-api/exportar?clientId=$CID&que=clientes")
comprueba "sin cookie responde 401" 401 "$COD"
COD=$(curl -s -o /dev/null -w '%{http_code}' -H "Cookie: nexux_token=inventado" \
      "https://nexux.pro/portal-api/exportar?clientId=$CID&que=clientes")
comprueba "con una sesion inventada responde 401" 401 "$COD"

echo
echo "=== 5. El boton esta en la pagina ==="
# La pagina del portal pide sesion, asi que se mira con la cookie puesta.
P=$(curl -s -H "Cookie: nexux_token=$TOKEN" "https://nexux.pro/cliente/$CID")
comprueba "sale la tarjeta Tus datos" 1 "$(printf '%s' "$P" | grep -c 'Tus datos')"
comprueba "sale el boton de las clientas" 1 "$(printf '%s' "$P" | grep -c 'data-exportar="clientes"')"
comprueba "sale el boton de las citas" 1 "$(printf '%s' "$P" | grep -c 'data-exportar="citas"')"

echo
echo "Fallos: $fallos"
exit $fallos
