#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprueba que la medida del aviso de cookies caza las trampas.

Encoger un aviso de cookies es facil si se hace trampa, y las trampas son justo
lo que se multa: esconder el boton de rechazar, hacerlo mas pequeno que el de
aceptar, o quitar el enlace donde se lee el detalle. Ninguna de las tres da
error: la pagina se ve perfecta y el aviso parece normal.

La cuarta es distinta: devolver el adorno de antes. Tampoco rompe nada, solo
vuelve a comerse el quinto de la pantalla. Por eso la medida tiene tope de alto.

  python3 scripts/sabotaje-aviso-cookies.py
"""
import hashlib
import io
import os
import shutil
import subprocess
import sys

LAY = 'src/layouts/Layout.astro'
AVISO = 'src/components/AvisoCookies.astro'
ESTATICO = '.vercel/output/static'
SERVIDO = '/tmp/av-despues'
PUERTO = 8894

ORIG = {p: io.open(p, encoding='utf-8').read() for p in (LAY, AVISO)}
FIRMA = {p: hashlib.md5(ORIG[p].encode('utf-8')).hexdigest() for p in ORIG}

# Donde meter una regla suelta dentro del bloque de movil del aviso.
ANCLA = '      .cookie-mas { white-space: nowrap; }'

SABOTAJES = [
    ('esconder el boton de rechazar', LAY, ANCLA,
     ANCLA + '\n      #cookie-reject { display: none !important; }'),

    ('dejar rechazar mas pequeno que aceptar', LAY, ANCLA,
     ANCLA + '\n      #cookie-reject { flex: 0 0 60px !important; }'),

    ('quitar el enlace a la politica', AVISO,
     ' <a href="/privacidad" class="cookie-mas">Más info</a>', ''),

    ('devolver el adorno de antes (vuelve a comerse la pantalla)', LAY,
     """        padding: 0.5rem 0.7rem calc(0.5rem + env(safe-area-inset-bottom));
        gap: 0.4rem;""",
     """        padding: 1.4rem 0.85rem;
        gap: 1.2rem;"""),
]


def construye_y_mide():
    r = subprocess.run(['pnpm', 'build'], capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        print('    (no compila con este sabotaje)')
        return -1
    if os.path.isdir(SERVIDO):
        shutil.rmtree(SERVIDO)
    shutil.copytree(ESTATICO, SERVIDO)
    m = subprocess.run([sys.executable, 'scripts/mide-aviso-cookies.py',
                        'http://127.0.0.1:%d' % PUERTO], capture_output=True, text=True, timeout=600)
    ultima = [l for l in m.stdout.splitlines() if l.startswith('Fallos:')]
    return int(ultima[0].split()[-1]) if ultima else -1


def main():
    print('Antes de nada: sin tocar nada, la medida tiene que estar en verde.')
    base = construye_y_mide()
    print('  sin sabotaje -> %d fallos' % base)
    if base != 0:
        print('  ya esta mal ANTES de sabotearlo: no se puede probar nada')
        return 1

    cazados = 0
    for titulo, fichero, viejo, nuevo in SABOTAJES:
        print('')
        print('SABOTAJE: %s' % titulo)
        if ORIG[fichero].count(viejo) != 1:
            print('  NO SE PUEDE APLICAR (aparece %d veces)' % ORIG[fichero].count(viejo))
            continue
        io.open(fichero, 'w', encoding='utf-8').write(ORIG[fichero].replace(viejo, nuevo, 1))
        try:
            fallos = construye_y_mide()
        finally:
            io.open(fichero, 'w', encoding='utf-8').write(ORIG[fichero])

        if fallos > 0:
            cazados += 1
            print('  CAZADO (%d comprobaciones en rojo)' % fallos)
        else:
            print('  NO ROMPE NADA -- la medida no vigila esto')

    bien = True
    for p in ORIG:
        io.open(p, 'w', encoding='utf-8').write(ORIG[p])
        if hashlib.md5(io.open(p, 'rb').read()).hexdigest() != FIRMA[p]:
            bien = False
    # Reconstruir con el fuente bueno. Si no, la pagina construida se queda con
    # el ultimo sabotaje dentro y el siguiente que mida vera un fallo que no
    # existe en el codigo.
    print('')
    print('Reconstruyendo con el codigo bueno para no dejar trampas...')
    construye_y_mide()

    print('')
    print('Ficheros restaurados igual que estaban: %s' % ('si' if bien else 'NO'))
    print('Cazados %d de %d' % (cazados, len(SABOTAJES)))
    return 0 if cazados == len(SABOTAJES) and bien else 1


if __name__ == '__main__':
    sys.exit(main())
