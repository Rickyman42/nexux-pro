#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprueba que la medida de la primera pantalla caza cada forma de deshacerla.

Ninguno de estos fallos da error: la pagina se sigue viendo perfecta, solo que
el boton de comprar se va debajo del aviso de cookies y nadie lo ve. Es
exactamente el tipo de fallo que no aparece en ningun registro.

Cada sabotaje deshace una parte del arreglo, reconstruye la pagina de verdad y
vuelve a medir con el navegador. Si la medida sigue diciendo que todo va bien,
la medida no vale para nada.

OJO con lo que significa cada resultado. El arreglo tiene dos clases de pieza:

  - Las que cambian el ORDEN (display:contents, el orden del parrafo y el de la
    puerta de salida). Cada una sola tira el boton fuera de pantalla, asi que la
    medida se pone roja ella sola.
  - Las que solo ganan SITIO (el relleno de arriba, el tamano del titulo y los
    huecos). Cada una por separado se come parte del margen pero deja el boton
    visible por los pelos: la medida dice OK, y hace bien, porque el boton SE VE.
    Por eso el ultimo sabotaje las aplica LAS TRES A LA VEZ, que es lo que pasa
    de verdad cuando alguien "limpia" el CSS: juntas suman 159px y si tiran el
    boton debajo del aviso.

  python3 scripts/sabotaje-primera-pantalla.py
"""
import hashlib
import io
import os
import shutil
import subprocess
import sys

PLAN = 'src/components/PlanDetail.astro'
ESTATICO = '.vercel/output/static'
SERVIDO = '/tmp/sabotaje-primera-pantalla'
PUERTO = 8897

ORIG = io.open(PLAN, encoding='utf-8').read()
FIRMA = hashlib.md5(ORIG.encode('utf-8')).hexdigest()

RELLENO = ('padding: 1.75rem 0 4rem;', 'padding: 5.5rem 0 4rem;')
TITULO = ('.plan-title { order: 1; font-size: 2.3rem; }', '.plan-title { order: 1; }')
HUECOS = ('.plan-hero {\n      gap: 1.1rem;\n    }', '.plan-hero {\n      gap: 2rem;\n    }')

SABOTAJES = [
    ('quitar el display:contents (se deshace todo el orden)',
     [('.plan-copy {\n      display: contents;\n    }',
       '.plan-copy {\n      max-width: 780px;\n    }')], True),

    ('devolver la puerta de salida al principio',
     [('.plan-back { order: 5; font-size: 0.86rem; }',
       '.plan-back { font-size: 0.86rem; }')], True),

    ('devolver el parrafo largo por delante de la tarjeta',
     [('.plan-sub { order: 4; margin-top: 0; }',
       '.plan-sub { order: 0; margin-top: 0; }')], True),

    ('devolver los 88px de relleno que no tapan nada', [RELLENO], False),
    ('devolver el titulo gigante de 48px', [TITULO], False),
    ('devolver los huecos de 32px entre bloques', [HUECOS], False),

    ('los tres de arriba A LA VEZ (relleno + titulo + huecos)',
     [RELLENO, TITULO, HUECOS], True),
]


def construye_y_mide():
    """Construye la pagina de verdad y la mide con el navegador. Devuelve fallos."""
    r = subprocess.run(['pnpm', 'build'], capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        print('    (la pagina no compila con este sabotaje)')
        return -1
    if os.path.isdir(SERVIDO):
        shutil.rmtree(SERVIDO)
    shutil.copytree(ESTATICO, SERVIDO)
    m = subprocess.run([sys.executable, 'scripts/mide-primera-pantalla.py',
                        'http://127.0.0.1:%d' % PUERTO],
                       capture_output=True, text=True, timeout=600)
    ultima = [l for l in m.stdout.splitlines() if l.startswith('Fallos:')]
    return int(ultima[0].split()[-1]) if ultima else -1


def main():
    print('Antes de nada: sin tocar nada, la medida tiene que estar en verde.')
    base = construye_y_mide()
    print('  sin sabotaje -> %d fallos' % base)
    if base != 0:
        print('  la pagina ya esta mal ANTES de sabotearla: no se puede probar nada')
        return 1

    mal = 0
    for titulo, cambios, debe_romper in SABOTAJES:
        print('')
        print('SABOTAJE: %s' % titulo)
        s = ORIG
        ok = True
        for viejo, nuevo in cambios:
            if s.count(viejo) != 1:
                print('  NO SE PUEDE APLICAR (aparece %d veces)' % s.count(viejo))
                ok = False
                break
            s = s.replace(viejo, nuevo, 1)
        if not ok:
            mal += 1
            continue

        io.open(PLAN, 'w', encoding='utf-8').write(s)
        try:
            fallos = construye_y_mide()
        finally:
            io.open(PLAN, 'w', encoding='utf-8').write(ORIG)

        if debe_romper and fallos > 0:
            print('  CAZADO (%d medidas en rojo), como tiene que ser' % fallos)
        elif not debe_romper and fallos == 0:
            print('  no rompe nada EL SOLO: se come margen pero el boton se sigue viendo.')
            print('  Lo que importa es el ultimo sabotaje, que junta los tres.')
        elif debe_romper:
            print('  NO ROMPE NADA -- la medida no vigila esto, y deberia')
            mal += 1
        else:
            print('  se pone roja y no deberia (%d): la medida esta pasada de frenada' % fallos)
            mal += 1

    io.open(PLAN, 'w', encoding='utf-8').write(ORIG)
    ahora = hashlib.md5(io.open(PLAN, 'rb').read()).hexdigest()
    # Reconstruir con el fuente bueno. Si no, la pagina construida se queda con
    # el ultimo sabotaje dentro y el siguiente que mida vera un fallo que no
    # existe en el codigo.
    print('')
    print('Reconstruyendo con el codigo bueno para no dejar trampas...')
    construye_y_mide()

    print('')
    print('Fichero restaurado igual que estaba: %s' % ('si' if ahora == FIRMA else 'NO'))
    print('Sabotajes que no salen como deben: %d de %d' % (mal, len(SABOTAJES)))
    return 0 if mal == 0 and ahora == FIRMA else 1


if __name__ == '__main__':
    sys.exit(main())
