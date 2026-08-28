#!/bin/bash
# Recorta los 14 planos a la duracion que pide la escaleta: de 1:55 a 1:15.
#
# El tramo de cada plano no es arbitrario. Cuatro de ellos tienen la accion en un
# punto concreto y cortarlos por el principio se carga lo que cuentan:
#
#   P4  la pantalla se apaga al final          -> 3-8
#   P5  Lena no coge el movil hasta el final   -> 3-8
#   P8  la cita entra en 3,5 s y el ROI al fin -> 3,5-11,5
#   P9  la sonrisa aparece en el segundo 5     -> 4-8
#
# Y el P3 lleva los destellos de los mensajes en 0,90 · 1,85 · 3,75 · 5,70 · 6,60.
# Con 0-5 entran los tres primeros, que es lo que dice su rotulo ("lleva vibrando
# desde las diez"); cortando por el final solo entrarian dos sueltos.
#
# Se recodifica en vez de copiar el flujo: cortar por copia salta al fotograma
# clave mas cercano y las duraciones no cuadrarian con la escaleta.
set -e
cd /home/nexux/brand-assets/video/anuncio-75s
mkdir -p cortes

corta () {  # fichero  inicio  duracion  salida
  ffmpeg -y -loglevel error -ss "$2" -i "$1.mp4" -t "$3" \
    -c:v libx264 -crf 17 -preset medium -pix_fmt yuv420p -c:a aac "cortes/$4.mp4"
  d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "cortes/$4.mp4")
  printf "  %-28s %s + %-5s -> %.2fs\n" "$4" "$2" "$3" "$d"
}

echo "=== recortando ==="
corta P01-manos-manicura        0    4    01_P01-manos
corta P02-movil-mostrador       0    5    02_P02-movil-mostrador
corta P03-cabina-mensajes       0    5    03_P03-cabina
corta P04-pantalla-se-apaga     3    5    04_P04-pantalla-se-apaga
corta P05-lena-final-del-dia    3    5    05_P05-lena-final-del-dia
corta P06-mano-movil-apagado    0    4    06_P06-movil-apagado
corta P07-en-movil              0    10   07_P07-conversacion
corta P08-agenda-y-roi          3.5  8    08_P08-agenda-y-roi
corta P09-probando-el-movil     4    4    09_P09-probando
corta P10-pulgar-whatsapp       0    5    10_P10-pulgar
corta P11-lena-mostrador        0    4    11_P11-lena-mostrador
corta P12-negocio-con-clientes  0    5    12_P12-negocio-con-vida
corta P13-lena-mirando-movil    0    6    13_P13-lena-movil
corta P14-cierre-qr             0    5    14_P14-cierre

echo
echo "=== suma ==="
python3 - <<'PY'
import subprocess, glob
t = 0.0
for f in sorted(glob.glob('/home/nexux/brand-assets/video/anuncio-75s/cortes/*.mp4')):
    d = float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration',
                              '-of','csv=p=0', f], capture_output=True, text=True).stdout)
    t += d
print('  %d planos, %.2f segundos en total' % (len(glob.glob('/home/nexux/brand-assets/video/anuncio-75s/cortes/*.mp4')), t))
print('  objetivo: 75,00 s')
PY
