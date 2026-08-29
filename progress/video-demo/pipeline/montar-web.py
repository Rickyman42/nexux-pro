#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""La version muda del anuncio: para la web, sin voz en off.

Sin locucion los rotulos vuelven a llevar todo el peso, asi que aqui cada plano
dura **lo que su texto necesita para leerse**, no lo que decidio el montaje con
voz. La duracion la calcula el script a partir de las palabras: por encima de 3
palabras por segundo el espectador no termina la frase antes del corte.

Los textos son una revision del guion original, no una copia. Los de antes
fallaban por lo mismo: describian lo que ya se ve o hablaban en futuro.

  "Son las once y media"      -> el primer rotulo del anuncio decia LA HORA,
                                 en los dos segundos que deciden si te siguen
                                 viendo. Ahora: "Lleva sonando desde las diez".
  "Tienes las manos ocupadas" -> repetia la imagen. Ahora dice lo que la imagen
                                 no puede decir: "Y tu no puedes cogerlo".
  "Cuando termines, miraras"  -> futuro, que aleja. Ahora en presente.
  "Dos ya no contestaran"     -> el dolor no es que no contesten, es que se
                                 fueron A OTRO SITIO. Eso es lo que duele.
  "...en tu agenda. Sola"     -> "sin ti" remata mejor: es lo que compras.
"""
import json
import subprocess
import sys
from pathlib import Path

ORIGEN = Path('/home/nexux/brand-assets/video/anuncio-75s')
TRABAJO = Path('/tmp/web')
SALIDA = Path('/tmp/ANUNCIO-web-mudo.mp4')
ESCALETA = Path('/tmp/escaleta-web.json')
FPS = 24
ZOOM = 0.04

LIMITE = 3.0     # palabras por segundo que se leen comodas
MARGEN = 0.6     # el rotulo entra 0,3 s tarde y sale 0,3 s antes

# (fichero, desde, minimo, movimiento, rotulo)
# El minimo es lo que pide la imagen; si el texto necesita mas, manda el texto.
PLAN = [
    ('P16-movil-boca-abajo',      1.0, 1.5, 'acerca', 'Lleva sonando desde las diez.'),
    ('P01-manos-manicura',        0.0, 1.5, 'acerca', 'Y tú no puedes cogerlo.'),
    ('P03-cabina-mensajes',       0.0, 1.5, 'aleja',  'Nunca puedes.'),
    ('P04-pantalla-se-apaga',     5.0, 1.5, 'quieto', None),
    ('P15-cara-cansada',          1.5, 2.0, 'acerca', 'Cuando termines habrá cuatro mensajes.'),
    ('P05-lena-final-del-dia',    4.5, 2.0, 'acerca', None),
    ('P17-silla-vacia',           1.0, 2.5, 'quieto', 'Dos se habrán ido a otro sitio.'),
    ('P06-mano-movil-apagado',    0.0, 2.0, 'quieto', 'Hoy alguien contestó por ti.'),
    ('P07-en-movil',              0.0, 9.0, 'quieto', 'Ofreció hora, confirmó el nombre y cerró la cita.'),
    ('P08-agenda-y-roi',          3.5, 7.0, 'quieto', 'Y la apuntó en tu agenda. Sin ti.'),
    ('P09-probando-el-movil',     4.5, 3.0, 'acerca', '«¿Y si contesta cualquier cosa?»\nPruébala. Sin registrarte.'),
    ('P10-pulgar-whatsapp',       0.0, 3.0, 'aleja',  '«¿Otro programa más?»\nEs tu WhatsApp de siempre.'),
    ('P11-lena-mostrador',        0.0, 3.0, 'acerca', '«¿Y si no me sirve?»\n30 días. Te devolvemos el dinero.'),
    ('P12-negocio-con-clientes',  0.0, 3.0, 'quieto', '«¿Cuánto?»\n29 € al mes. Sin comisiones.'),
    ('P13-lena-mirando-movil',    0.0, 4.0, 'acerca', '¿Cuántos mensajes tienes ahora mismo sin abrir?'),
    ('P14-cierre-qr',             0.0, 5.0, 'quieto', None),
]


def duracion_necesaria(minimo, rotulo):
    """Lo que dura el plano: lo que pide la imagen o lo que pide leer el texto."""
    if not rotulo:
        return minimo
    hace_falta = len(rotulo.split()) / LIMITE + MARGEN
    return round(max(minimo, hace_falta) * FPS) / FPS   # cuadrado al fotograma


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

    print('  %-2s %-26s %-7s %-7s  %s' % ('#', 'plano', 'minimo', 'dura', 'por que'))
    print('  ' + '-' * 68)
    for i, (fichero, desde, minimo, mov, rotulo) in enumerate(PLAN, 1):
        entrada = ORIGEN / (fichero + '.mp4')
        if not entrada.exists():
            sys.exit('falta %s' % entrada)
        dur = duracion_necesaria(minimo, rotulo)
        razon = 'imagen' if dur <= minimo + 0.001 else 'texto (%d palabras)' % len(rotulo.split())

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

        leidos = int(subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_frames',
             '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', str(salida)],
            capture_output=True, text=True).stdout.strip())
        if abs(leidos - int(dur * FPS)) > 2:
            sys.exit('%s tiene %d fotogramas y esperaba %d' % (fichero, leidos, int(dur * FPS)))

        print('  %-2d %-26s %-7.2f %-7.2f  %s' % (i, fichero, minimo, dur, razon))
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

    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                              '-of', 'csv=p=0', str(SALIDA)],
                             capture_output=True, text=True).stdout)
    print('\n  %d planos, %.2f s' % (len(PLAN), t))
    print('  %s -> %.2f s' % (SALIDA, d))

    # Ningun rotulo puede quedar por encima del limite: es la razon de ser de
    # esta version, y si alguno se pasa el calculo esta mal en alguna parte.
    for p in escaleta:
        if not p['rotulo']:
            continue
        v = len(p['rotulo'].split()) / (p['dura'] - MARGEN)
        if v > LIMITE + 0.05:
            sys.exit('el rotulo del plano %d sale a %.1f palabras por segundo' % (p['n'], v))
    print('  todos los rotulos por debajo de %.0f palabras por segundo' % LIMITE)


if __name__ == '__main__':
    main()
