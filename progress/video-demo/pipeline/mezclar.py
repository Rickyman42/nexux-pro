#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mezcla el anuncio: imagen, voz en off y musica.

La musica NO va a volumen fijo. Se usa `sidechaincompress`: la propia voz manda
sobre la musica, que baja sola cuando alguien habla y vuelve a subir en los
silencios. Con un volumen fijo hay que elegir entre que la musica se oiga o que
la voz se entienda, y en un anuncio de 56 segundos con trece frases eso significa
una musica inaudible casi todo el rato.

Ademas la musica entra y sale en fundido: arrancar de golpe en el segundo cero
suena a pista pegada, y cortarla en seco al final estropea el cierre.

  mezclar.py            monta el anuncio entero
  mezclar.py --sin-voz  solo imagen y musica (la version para la web)
"""
import subprocess
import sys
from pathlib import Path

BASE = Path('/home/nexux/brand-assets/video/anuncio-75s')
VIDEO = BASE / 'ANUNCIO-56s-sin-rotulos.mp4'
VOZ = BASE / 'VOZ-anuncio-56s.wav'
MUSICA = BASE / 'MUSICA-quiet-ledger.mp3'
DURACION = 55.70

# La musica arranca por debajo y el compresor la baja otros 8-9 dB cuando entra
# la voz. Medido de oido sobre el montaje: mas alta tapa las frases cortas del
# acto 4, mas baja no se percibe que haya musica.
MUSICA_DB = -13
ENTRADA = 1.2    # fundido de entrada
SALIDA = 2.5     # fundido de salida, que muere sobre la tarjeta del QR


def duracion(f):
    return float(subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'csv=p=0', str(f)], capture_output=True, text=True).stdout)


def main():
    sin_voz = '--sin-voz' in sys.argv
    salida = BASE / ('ANUNCIO-56s-SIN-VOZ.mp4' if sin_voz else 'ANUNCIO-56s-FINAL.mp4')

    for f in (VIDEO, MUSICA) + (() if sin_voz else (VOZ,)):
        if not f.exists():
            sys.exit('falta %s' % f)

    if sin_voz:
        # Sin voz no hay nada que esquivar: la musica va sola, algo mas alta.
        filtro = (
            '[1:a]atrim=0:%.3f,afade=t=in:st=0:d=%.2f,'
            'afade=t=out:st=%.3f:d=%.2f,volume=%ddB[out]'
            % (DURACION, ENTRADA, DURACION - SALIDA, SALIDA, MUSICA_DB + 5))
        entradas = ['-i', str(VIDEO), '-i', str(MUSICA)]
    else:
        filtro = (
            # La voz, tal cual, es la referencia.
            '[1:a]aformat=fltp:44100:stereo[voz];'
            '[voz]asplit=2[voz_mezcla][voz_control];'
            # La musica recortada, con sus fundidos y ya bajada de volumen.
            '[2:a]atrim=0:%.3f,afade=t=in:st=0:d=%.2f,'
            'afade=t=out:st=%.3f:d=%.2f,volume=%ddB,'
            'aformat=fltp:44100:stereo[mus];'
            # Y aqui la voz aparta la musica: ratio suave y ataque rapido para
            # que no se oiga "bombear", release largo para que vuelva sin brusquedad.
            '[mus][voz_control]sidechaincompress='
            'threshold=0.03:ratio=6:attack=20:release=400:makeup=1[mus_baja];'
            '[voz_mezcla][mus_baja]amix=inputs=2:normalize=0[out]'
            % (DURACION, ENTRADA, DURACION - SALIDA, SALIDA, MUSICA_DB))
        entradas = ['-i', str(VIDEO), '-i', str(VOZ), '-i', str(MUSICA)]

    subprocess.run(
        ['ffmpeg', '-y', '-loglevel', 'error'] + entradas
        + ['-filter_complex', filtro, '-map', '0:v', '-map', '[out]',
           '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', str(salida)],
        check=True)

    d = duracion(salida)
    print('  %s -> %.2f s' % (salida.name, d))
    if abs(d - DURACION) > 0.15:
        sys.exit('dura %.2f y el montaje %.2f' % (d, DURACION))

    # Que exista pista de audio y que no este muda: un filtro mal encadenado
    # deja el video perfecto y sin sonido, y eso no se ve, se oye.
    # volumedetect escribe su lectura como info, no como error: con -v error se
    # la traga y la comprobacion cantaba "mudo" con el audio perfectamente bien.
    r = subprocess.run(
        ['ffmpeg', '-hide_banner', '-i', str(salida), '-af',
         'volumedetect', '-f', 'null', '-'], capture_output=True, text=True)
    pico = [l for l in r.stderr.splitlines() if 'max_volume' in l]
    print('  %s' % (pico[0].split(']')[-1].strip() if pico else 'sin lectura de volumen'))
    if not pico or float(pico[0].split(':')[-1].replace('dB', '')) < -50:
        sys.exit('la pista de audio esta practicamente muda')
    print('  suena')


if __name__ == '__main__':
    main()
