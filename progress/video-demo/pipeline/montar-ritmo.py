#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Montaje con los tres planos del agobio. Es la escaleta que manda.

De aqui salen los clips recortados, los tiempos de los rotulos y los de la voz:
si algo cambia, se cambia AQUI y los tres se regeneran juntos. Antes las
duraciones vivian en tres ficheros y bastaba tocar uno para descuadrar el resto.

Que cambia respecto al montaje de catorce planos:

1. **Abre por el movil boca abajo, no por unas manos limando.** El objeto del
   conflicto primero. Unas manos trabajando no son un problema; un movil que no
   puedes coger, si.

2. **Entran los tres planos del agobio** (P15 cara, P16 movil, P17 silla). Se
   midio que el acto del dolor y el del alivio se veian iguales --brillo 116
   contra 111-- y estos tres van a 96, 96 y 47: por fin hay contraste. La cara
   de Lena es ademas el primer rostro con emocion del anuncio; antes no habia
   ninguno hasta el segundo 46.

3. **El acto 1 va en rafaga**, entre 1,5 y 2,5 s por plano, contra los 7 y 9
   segundos de los dos planos de producto. Los catorce planos anteriores duraban
   todos entre 2 y 5 segundos y esa uniformidad era la otra razon de que el
   anuncio no transmitiera: no habia ni acelerones ni pausas.

4. **Se cae el P02** (el movil en el mostrador). Decia lo mismo que el P16 y
   ahora sobra. Sigue en brand-assets por si se quiere recuperar.

5. **La silla vacia se queda QUIETA.** Es el unico plano sin movimiento de
   camara del acto 1: la quietud es lo que cuenta ahi.

6. **Los rotulos rematan, no narran.** Con voz en off, un rotulo que repite
   literalmente lo que oyes es ruido: se midio y once de trece no daban tiempo a
   leerse --el acto 1 en rafaga pedia hasta 5,6 palabras por segundo, cuando por
   encima de 3 el espectador no termina la frase--. Para que cupieran, el montaje
   tenia que irse a 60 s.

   Asi que el reparto cambia: **la voz cuenta y el rotulo remata**. El acto 1 va
   sin rotulos --la locucion lleva el relato y la imagen ya dice lo suyo-- y en
   el acto 4 el rotulo pone la duda del cliente («¿Y si no me sirve?») mientras
   la voz da la respuesta. Ademas de caber, se entiende mejor: uno pregunta y el
   otro contesta, en vez de leer y oir lo mismo a la vez.

   ⚠️ Esto vale para la version CON voz. La version muda para la web necesita
   los rotulos completos y, con ellos, un montaje mas largo.
"""
import json
import subprocess
import sys
from pathlib import Path

ORIGEN = Path('/home/nexux/brand-assets/video/anuncio-75s')
TRABAJO = Path('/tmp/ritmo')
SALIDA = Path('/tmp/ANUNCIO-ritmo.mp4')
ESCALETA = Path('/tmp/escaleta.json')
FPS = 24
ZOOM = 0.04

# (fichero, desde, duracion, movimiento, rotulo)
# El rotulo es None cuando el plano habla solo.
PLAN = [
    # --- Acto 1: el dolor, en rafaga -------------------------------------
    ('P16-movil-boca-abajo',      1.0, 1.5, 'acerca', None),
    ('P01-manos-manicura',        0.0, 1.5, 'acerca', None),
    ('P03-cabina-mensajes',       0.0, 2.0, 'aleja',  None),
    ('P04-pantalla-se-apaga',     5.0, 1.5, 'quieto', None),
    ('P15-cara-cansada',          1.5, 2.5, 'acerca', 'Cuatro mensajes.'),
    ('P05-lena-final-del-dia',    4.5, 2.0, 'acerca', None),
    ('P17-silla-vacia',           1.0, 2.5, 'quieto', 'Se irán a otro sitio.'),
    # --- Acto 2: el giro --------------------------------------------------
    ('P06-mano-movil-apagado',    0.0, 2.5, 'quieto', 'Alguien contestó.'),
    # --- Acto 3: lo que hace el producto ----------------------------------
    ('P07-en-movil',              0.0, 9.0, 'quieto', 'Ofreció hora, confirmó el nombre y cerró la cita.'),
    ('P08-agenda-y-roi',          3.5, 7.0, 'quieto', 'Y la apuntó en tu agenda. Sin ti.'),
    # --- Acto 4: las objeciones, tambien en rafaga ------------------------
    ('P09-probando-el-movil',     4.5, 3.5, 'acerca', '«¿Y si contesta cualquier cosa?»'),
    ('P10-pulgar-whatsapp',       0.0, 3.5, 'aleja',  '«¿Otro programa más?»'),
    ('P11-lena-mostrador',        0.0, 4.0, 'acerca', '«¿Y si no me sirve?»'),
    ('P12-negocio-con-clientes',  0.0, 3.2, 'quieto', '«¿Cuánto?»'),
    # --- Acto 5: el cierre ------------------------------------------------
    ('P13-lena-mirando-movil',    0.0, 4.5, 'acerca', '¿Cuántos tienes sin abrir?'),
    ('P14-cierre-qr',             0.0, 5.0, 'quieto', None),
]


def filtro(mov, dur):
    n = int(dur * FPS)
    if mov == 'acerca':
        z = 'min(1+%.6f*in,%.4f)' % (ZOOM / n, 1 + ZOOM)
    elif mov == 'aleja':
        z = 'max(%.4f-%.6f*in,1.0)' % (1 + ZOOM, ZOOM / n)
    else:
        return None
    return ("zoompan=z='%s':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            ':d=1:s=1280x720:fps=%d' % (z, FPS))


def main():
    TRABAJO.mkdir(parents=True, exist_ok=True)
    trozos, escaleta, t = [], [], 0.0

    print('  %-2s %-26s %-6s %-7s %s' % ('#', 'plano', 'entra', 'dura', 'mov'))
    print('  ' + '-' * 60)
    for i, (fichero, desde, dur, mov, rotulo) in enumerate(PLAN, 1):
        entrada = ORIGEN / (fichero + '.mp4')
        if not entrada.exists():
            sys.exit('falta %s' % entrada)
        salida = TRABAJO / ('%02d_%s.mp4' % (i, fichero))

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

        # Los fotogramas se cuentan de verdad: zoompan mal usado los multiplica
        # y un plano de este pipeline llego a durar 816 s con la cabecera bien.
        leidos = int(subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_frames',
             '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', str(salida)],
            capture_output=True, text=True).stdout.strip())
        if abs(leidos - int(dur * FPS)) > 2:
            sys.exit('%s tiene %d fotogramas y esperaba %d'
                     % (fichero, leidos, int(dur * FPS)))

        print('  %-2d %-26s %6.2f %6.2fs %s' % (i, fichero, t, dur, mov))
        escaleta.append({'n': i, 'plano': fichero, 'entra': round(t, 2),
                         'dura': dur, 'rotulo': rotulo})
        trozos.append(salida)
        t += dur

    lista = TRABAJO / 'lista.txt'
    lista.write_text(''.join("file '%s'\n" % x for x in trozos), encoding='utf-8')
    subprocess.run(
        ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0',
         '-i', str(lista), '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
         '-pix_fmt', 'yuv420p', '-r', str(FPS), '-an', str(SALIDA)], check=True)

    ESCALETA.write_text(json.dumps(
        {'duracion': round(t, 2), 'fps': FPS, 'planos': escaleta},
        indent=2, ensure_ascii=False), encoding='utf-8')

    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                              'format=duration', '-of', 'csv=p=0', str(SALIDA)],
                             capture_output=True, text=True).stdout)
    print('\n  %d planos, %.2f s planificados' % (len(PLAN), t))
    print('  %s -> %.2f s' % (SALIDA, d))
    print('  escaleta en %s (la leen los rotulos y la voz)' % ESCALETA)
    if abs(d - t) > 0.1:
        sys.exit('el montaje dura %.2f y la escaleta dice %.2f' % (d, t))


if __name__ == '__main__':
    main()
