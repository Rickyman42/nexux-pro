#!/usr/bin/env python3
"""Montaje con ritmo: mismos planos, otra edicion.

El primer montaje duraba 75 s con casi todos los planos entre 4 y 5 segundos y la
camara quieta. Eso es lo que lo hacia pesado: no es que los planos sean malos, es
que duran todos lo mismo y no se mueve nada.

Dos decisiones:

1. **El tiempo se reparte segun lo que hay que entender, no a partes iguales.**
   Un plano de manos limando unas se lee en dos segundos; la conversacion de
   WhatsApp necesita nueve porque hay que leerla. El acto 4 son cuatro objeciones
   seguidas: en rafaga de dos segundos y medio funcionan como una lista, en cinco
   se hacen eternas.

2. **Movimiento en los planos que no lo tienen.** Los clips de Flow son estaticos.
   Un acercamiento lentisimo (4% en todo el plano) no se percibe como efecto pero
   quita la sensacion de foto fija. Se alterna acercar y alejar para que no sea
   monotono, y se deja quieto lo que ya se mueve solo: la conversacion del P7
   (la mano balancea), el CRM del P8 (ya lleva su propio zoom) y el P12 (la camara
   deriva sola).

Resultado: 56 s en vez de 75, con los dos planos de producto intactos.

El acto 4 se midio aparte: sus planos llevan dos frases (la objecion y la
respuesta) y a 2,5 s salen a 4,4 palabras por segundo. Por encima de 3 el
espectador no termina de leer antes del corte, asi que se les dio el tiempo
que pide su texto. Son los planos donde se cierra la venta: ahogarlos ahi
para ahorrar cuatro segundos es tirar el anuncio.
"""
import subprocess
import sys
from pathlib import Path

ORIGEN = Path('/home/nexux/brand-assets/video/anuncio-75s')
TRABAJO = Path('/tmp/ritmo')
SALIDA = Path('/tmp/ANUNCIO-ritmo.mp4')
FPS = 24

# (fichero de origen, desde, duracion, movimiento)
#   movimiento: 'acerca' | 'aleja' | 'quieto'
# El "desde" respeta donde ocurre la accion de cada plano, como en cortar-planos.sh
PLAN = [
    ('P01-manos-manicura',        0.0,  2.0, 'acerca'),
    ('P02-movil-mostrador',       0.0,  2.5, 'aleja'),
    ('P03-cabina-mensajes',       0.0,  3.0, 'acerca'),   # destellos en 0,90 y 1,85
    ('P04-pantalla-se-apaga',     5.0,  3.0, 'quieto'),   # se apaga al final
    ('P05-lena-final-del-dia',    4.5,  3.5, 'acerca'),   # coge el movil al final
    ('P06-mano-movil-apagado',    0.0,  2.0, 'quieto'),
    ('P07-en-movil',              0.0,  9.0, 'quieto'),   # hay que leerla
    ('P08-agenda-y-roi',          3.5,  7.0, 'quieto'),   # ya lleva su acercamiento
    ('P09-probando-el-movil',     4.5,  3.5, 'acerca'),   # la sonrisa aparece en el 5
    ('P10-pulgar-whatsapp',       0.0,  3.5, 'aleja'),
    ('P11-lena-mostrador',        0.0,  4.0, 'acerca'),
    ('P12-negocio-con-clientes',  0.0,  3.2, 'quieto'),   # la camara ya deriva
    ('P13-lena-mirando-movil',    0.0,  4.5, 'acerca'),
    ('P14-cierre-qr',             0.0,  5.0, 'quieto'),
]

# Cuanto se acerca en todo el plano. Por encima del 5% se nota como efecto.
ZOOM = 0.04


def filtro(mov, dur):
    """El movimiento, como zoompan sobre el video (d=1: un fotograma por fotograma)."""
    n = int(dur * FPS)
    if mov == 'acerca':
        z = "min(1+%.6f*in,%.4f)" % (ZOOM / n, 1 + ZOOM)
    elif mov == 'aleja':
        z = "max(%.4f-%.6f*in,1.0)" % (1 + ZOOM, ZOOM / n)
    else:
        return None
    return ("zoompan=z='%s':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            ":d=1:s=1280x720:fps=%d" % (z, FPS))


def main():
    TRABAJO.mkdir(parents=True, exist_ok=True)
    trozos, total = [], 0.0

    for fichero, desde, dur, mov in PLAN:
        entrada = ORIGEN / (fichero + '.mp4')
        if not entrada.exists():
            sys.exit('falta %s' % entrada)
        salida = TRABAJO / (fichero + '.mp4')

        cadena = ['scale=1280:720']
        f = filtro(mov, dur)
        if f:
            cadena.append(f)
        cadena.append('format=yuv420p')

        subprocess.run(
            ['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(desde), '-i', str(entrada),
             '-t', str(dur), '-vf', ','.join(cadena),
             '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
             '-r', str(FPS), '-an', str(salida)], check=True)

        # Se cuentan los fotogramas de verdad: zoompan mal usado los multiplica,
        # y un plano de este pipeline llego a durar 816 s con la cabecera correcta.
        leidos = int(subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_frames',
             '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', str(salida)],
            capture_output=True, text=True).stdout.strip())
        esperados = int(dur * FPS)
        aviso = '' if abs(leidos - esperados) <= 2 else '  <-- REVISAR'
        print('  %-28s %4.1fs  %-7s %4d fot.%s' % (fichero, dur, mov, leidos, aviso))
        if aviso:
            sys.exit('el plano %s tiene %d fotogramas y esperaba %d' % (fichero, leidos, esperados))

        trozos.append(salida)
        total += dur

    lista = TRABAJO / 'lista.txt'
    lista.write_text(''.join("file '%s'\n" % t for t in trozos), encoding='utf-8')
    subprocess.run(
        ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0',
         '-i', str(lista), '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
         '-pix_fmt', 'yuv420p', '-r', str(FPS), '-an', str(SALIDA)], check=True)

    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                              '-of', 'csv=p=0', str(SALIDA)],
                             capture_output=True, text=True).stdout)
    n = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_frames',
                        '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', str(SALIDA)],
                       capture_output=True, text=True).stdout.strip()
    print('\n  planificado: %.1f s' % total)
    print('  %s -> %.2f s, %s fotogramas' % (SALIDA, d, n))


if __name__ == '__main__':
    main()
