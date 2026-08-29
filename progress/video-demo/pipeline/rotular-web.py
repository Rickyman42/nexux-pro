#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quema los rotulos sobre la version muda y le pone la musica.

La version con voz vive en CapCut para poder editarla. Esta no: va a la web
como un fichero listo para poner en una pagina, asi que los rotulos se
incrustan y la musica se mezcla aqui.

Los textos y los tiempos salen de la escaleta que escribe montar-web.py: alli
la duracion de cada plano ya se calculo para que su rotulo se lea.

Reusa el dibujo de rotular.py --misma tipografia, mismo degradado ajustado al
bloque, mismo reparto equilibrado de lineas-- para que las dos versiones se
vean iguales.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from rotular import dibuja, medida, pico, FPS, ENTRADA   # noqa: E402

ESCALETA = Path('/tmp/escaleta-web.json')
TROZOS = Path('/tmp/web')
TRABAJO = Path('/tmp/web-rotulos')
MUSICA = Path('/home/nexux/brand-assets/video/anuncio-75s/MUSICA-quiet-ledger.mp3')
SALIDA = Path('/tmp/web-salida/ANUNCIO-WEB-55s.mp4')

# Sin voz que esquivar, la musica puede ir mucho mas arriba: aqui es lo unico
# que suena y a -8 dB el video se quedaba en un pico de -8,4, que en una pagina
# se oye flojo.
MUSICA_DB = -4
FUNDIDO_ENTRADA = 1.2
FUNDIDO_SALIDA = 2.5


def main():
    if not ESCALETA.exists():
        sys.exit('falta %s: corre antes montar-web.py' % ESCALETA)
    datos = json.loads(ESCALETA.read_text(encoding='utf-8'))
    TRABAJO.mkdir(parents=True, exist_ok=True)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)

    piezas = []
    print('  %-2s %-26s %-6s  %s' % ('#', 'plano', 'dura', 'rotulo'))
    print('  ' + '-' * 66)
    for p in datos['planos']:
        origen = TROZOS / ('%02d_%s.mp4' % (p['n'], p['plano']))
        if not origen.exists():
            sys.exit('falta %s' % origen)
        destino = TRABAJO / origen.name
        dur = p['dura']

        if not p['rotulo']:
            subprocess.run(['cp', str(origen), str(destino)], check=True)
            print('  %-2d %-26s %-6.2f  —' % (p['n'], p['plano'], dur))
            piezas.append(destino)
            continue

        # El rotulo puede traer dos lineas: la duda del cliente arriba en gris y
        # la respuesta debajo en blanco, como en la version con voz.
        partes = p['rotulo'].split('\n')
        objecion = partes[0] if len(partes) > 1 else None
        remate = partes[-1]

        png = TRABAJO / ('%02d.png' % p['n'])
        dibuja(objecion, remate).save(png)

        sale = dur - ENTRADA
        filtro = (
            '[1:v]format=rgba,fade=t=in:st=%.2f:d=%.2f:alpha=1,'
            'fade=t=out:st=%.2f:d=%.2f:alpha=1[r];[0:v][r]overlay=0:0'
            % (ENTRADA, ENTRADA, sale - ENTRADA, ENTRADA))

        subprocess.run(
            ['ffmpeg', '-y', '-loglevel', 'error', '-i', str(origen),
             '-loop', '1', '-framerate', str(FPS), '-t', str(dur), '-i', str(png),
             '-filter_complex', filtro,
             '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
             '-pix_fmt', 'yuv420p', '-r', str(FPS), '-an', str(destino)], check=True)

        # Que el rotulo este de verdad: contar fotogramas no lo dice, y ya paso
        # una vez que salio un video perfecto y sin una sola letra encima.
        # Se mira si la franja CAMBIA, no si se oscurece. En la silla vacia
        # --brillo 47, casi negra-- el degradado no puede oscurecer nada y el
        # texto blanco lo que hace es ACLARAR: exigir oscurecimiento daba por
        # fallido un plano perfectamente rotulado.
        # Dos senales, cualquiera vale: el degradado oscurece la franja, o el
        # texto mete pixeles claros donde no los habia. Sobre el CRM blanco
        # manda la primera; sobre la silla vacia, casi negra, la segunda.
        oscurece = medida(destino, dur) < medida(origen, dur) - 4
        aclara = pico(destino, dur) > pico(origen, dur) + 20
        if not (oscurece or aclara):
            sys.exit('plano %d: la franja no cambio, el rotulo no se pinto' % p['n'])

        print('  %-2d %-26s %-6.2f  %s'
              % (p['n'], p['plano'], dur, p['rotulo'].replace('\n', ' / ')[:32]))
        piezas.append(destino)

    lista = TRABAJO / 'lista.txt'
    lista.write_text(''.join("file '%s'\n" % x for x in piezas), encoding='utf-8')
    mudo = TRABAJO / 'sin-musica.mp4'
    subprocess.run(
        ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0',
         '-i', str(lista), '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
         '-pix_fmt', 'yuv420p', '-r', str(FPS), '-an', str(mudo)], check=True)

    total = datos['duracion']
    subprocess.run(
        ['ffmpeg', '-y', '-loglevel', 'error', '-i', str(mudo), '-i', str(MUSICA),
         '-filter_complex',
         '[1:a]atrim=0:%.3f,afade=t=in:st=0:d=%.2f,afade=t=out:st=%.3f:d=%.2f,'
         'volume=%ddB[a]' % (total, FUNDIDO_ENTRADA, total - FUNDIDO_SALIDA,
                             FUNDIDO_SALIDA, MUSICA_DB),
         '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac',
         '-b:a', '192k', '-shortest', str(SALIDA)], check=True)

    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                              '-of', 'csv=p=0', str(SALIDA)],
                             capture_output=True, text=True).stdout)
    r = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(SALIDA), '-af',
                        'volumedetect', '-f', 'null', '-'],
                       capture_output=True, text=True)
    linea_pico = [l for l in r.stderr.splitlines() if 'max_volume' in l]
    print('\n  %s -> %.2f s' % (SALIDA, d))
    print('  %s' % (linea_pico[0].split(']')[-1].strip() if linea_pico else 'sin lectura'))
    if abs(d - total) > 0.15:
        sys.exit('dura %.2f y la escaleta dice %.2f' % (d, total))
    print('  cuadra')


if __name__ == '__main__':
    main()
