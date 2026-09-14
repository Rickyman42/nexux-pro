#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprueba que los tests de velocidad cazan cada forma de deshacer el arreglo.

Estos dos fallos no dan error: la pagina sigue viendose bien, solo que tarda un
segundo mas y pesa medio mega mas. Por eso hace falta que alguien vigile.
"""
import io
import os
import hashlib
import subprocess
import sys

CSS = 'src/styles/global.css'
LAY = 'src/layouts/Layout.astro'
PLAN = 'src/components/PlanDetail.astro'
WEBP = 'public/img/demo-crm.webp'
APARTADA = 'public/img/.demo-crm.webp.apartada'
T = 'test/pagina-rapida.test.mjs'

ORIG = {p: io.open(p, encoding='utf-8').read() for p in (CSS, LAY, PLAN)}
FIRMA = {p: hashlib.md5(io.open(p, 'rb').read()).hexdigest() for p in ORIG}
FIRMA_WEBP = hashlib.md5(io.open(WEBP, 'rb').read()).hexdigest()

IMPORT = "@import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700;800;900&display=swap');\n"


def corre():
    r = subprocess.run(['node', '--test', T], capture_output=True, text=True, timeout=300)
    fallos = [l for l in r.stdout.splitlines() if l.startswith('# fail')]
    rojos = [l.split('- ', 1)[1] for l in r.stdout.splitlines() if l.startswith('not ok')]
    return (int(fallos[0].split()[-1]) if fallos else -1), rojos


def con_texto(fichero, viejo, nuevo, veces=1):
    def hacer():
        if ORIG[fichero].count(viejo) != veces:
            return False
        io.open(fichero, 'w', encoding='utf-8').write(ORIG[fichero].replace(viejo, nuevo))
        return True
    def deshacer():
        io.open(fichero, 'w', encoding='utf-8').write(ORIG[fichero])
    return hacer, deshacer


def con_import():
    def hacer():
        io.open(CSS, 'w', encoding='utf-8').write(IMPORT + ORIG[CSS])
        return True
    def deshacer():
        io.open(CSS, 'w', encoding='utf-8').write(ORIG[CSS])
    return hacer, deshacer


def sin_imagen():
    def hacer():
        os.rename(WEBP, APARTADA)
        return True
    def deshacer():
        if os.path.exists(APARTADA):
            os.rename(APARTADA, WEBP)
    return hacer, deshacer


ENLACE = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2'
          '?family=Geist:wght@300;400;500;600;700;800;900'
          '&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500&display=swap" />')

SABOTAJES = [
    ('vuelve el @import: la pagina en blanco 1 segundo mas', con_import()),
    ('desaparece el enlace de la cabecera: pagina sin su letra',
     con_texto(LAY, ENLACE, '')),
    ('se cae el display=swap: texto invisible hasta 3s esperando a Google',
     con_texto(LAY, '&display=swap" />', '" />')),
    ('vuelve el PNG de 467 KB en la captura del CRM',
     con_texto(PLAN, 'demo-crm.webp', 'demo-crm.png', veces=2)),
    ('la imagen ligera no llega al servidor (hueco roto)', sin_imagen()),
]

print('Comprobando que los tests cazan cada forma de volver a la pagina lenta.\n')
todos = True
try:
    for nombre, (hacer, deshacer) in SABOTAJES:
        if not hacer():
            print('  %-62s -> NO SE PUDO APLICAR' % nombre)
            todos = False
            continue
        n, rojos = corre()
        deshacer()
        ok = n > 0
        todos = todos and ok
        print('  %-62s -> %s' % (nombre, 'CAZADO' if ok else 'NO ROMPE NADA'))
        if ok:
            print('       rojo: %s' % (rojos[0][:70] if rojos else '(sin detalle)'))
finally:
    for p, texto in ORIG.items():
        io.open(p, 'w', encoding='utf-8').write(texto)
    if os.path.exists(APARTADA):
        os.rename(APARTADA, WEBP)

iguales = all(hashlib.md5(io.open(p, 'rb').read()).hexdigest() == FIRMA[p] for p in ORIG)
iguales = iguales and hashlib.md5(io.open(WEBP, 'rb').read()).hexdigest() == FIRMA_WEBP
print('\nTodo restaurado identico:', iguales)
n, _ = corre()
print('Sin sabotaje -> fallos:', n)
sys.exit(0 if (todos and iguales and n == 0) else 1)
