#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera los rotulos que se importan en CapCut, leyendo la escaleta.

Los textos y los tiempos NO se teclean aqui: salen de `montar-ritmo.py`, que es
quien decide el montaje. Antes las duraciones vivian en tres ficheros distintos
y bastaba tocar uno para descuadrar los otros dos.

⚠️ En CapCut, un SRT se inserta DONDE ESTE EL CABEZAL, no en los tiempos que
dice el fichero. Hay que poner el cabezal en cero justo antes de importar --y
como ultimo paso, porque un clic en zona vacia de la linea de tiempo lo manda al
final--. Con el cabezal al final, los rotulos se colocaron detras del video y el
montaje paso de 55 a 106 segundos.
"""
import json
import sys
from pathlib import Path

ESCALETA = Path('/tmp/escaleta.json')
SALIDA = Path(r'C:\Users\Nexux\Desktop\creatives\anuncio-56s')
MARGEN = 0.3   # entra 0,3 s despues del corte y sale 0,3 s antes del siguiente


def marca(seg):
    ms = int(round(seg * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return '%02d:%02d:%02d,%03d' % (h, m, s, ms)


def main():
    if not ESCALETA.exists():
        sys.exit('falta %s: corre antes montar-ritmo.py' % ESCALETA)
    datos = json.loads(ESCALETA.read_text(encoding='utf-8'))

    destino = Path(sys.argv[1]) if len(sys.argv) > 1 else SALIDA
    destino.mkdir(parents=True, exist_ok=True)

    entradas = []
    print('  %-3s %-7s %-7s  %s' % ('#', 'entra', 'sale', 'rotulo'))
    print('  ' + '-' * 66)
    for p in datos['planos']:
        if not p['rotulo']:
            print('  %-3d %-7s %-7s  (sin rotulo)' % (p['n'], '—', '—'))
            continue
        desde = p['entra'] + MARGEN
        hasta = p['entra'] + p['dura'] - MARGEN
        entradas.append((desde, hasta, p['rotulo']))
        print('  %-3d %-7.2f %-7.2f  %s'
              % (p['n'], desde, hasta, p['rotulo'].replace('\n', ' / ')[:44]))

    trozos = []
    for i, (desde, hasta, texto) in enumerate(entradas, 1):
        trozos.append('%d\n%s --> %s\n%s\n' % (i, marca(desde), marca(hasta), texto))

    fichero = destino / 'ROTULOS.srt'
    fichero.write_text('\n'.join(trozos), encoding='utf-8-sig')
    print('\n  %s -> %d rotulos' % (fichero, len(entradas)))
    print('  montaje: %.2f s' % datos['duracion'])


if __name__ == '__main__':
    main()
