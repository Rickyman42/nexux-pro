#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprueba que los tests cazan cada forma de volver a dejar la ficha tirada.

Este fallo es de los peores de detectar: no da error, el build pasa, la pagina
carga y todo funciona. Simplemente se ve mal, y solo lo nota quien la abre.
"""
import hashlib
import io
import subprocess
import sys

F = 'src/pages/cliente/[id].astro'
T = 'test/estilos-del-portal.test.mjs'

ORIG = io.open(F, encoding='utf-8').read()
FIRMA = hashlib.md5(io.open(F, 'rb').read()).hexdigest()


def corre():
    r = subprocess.run(['node', '--test', T], capture_output=True, text=True, timeout=300)
    fallos = [l for l in r.stdout.splitlines() if l.startswith('# fail')]
    rojos = [l.split('- ', 1)[1] for l in r.stdout.splitlines() if l.startswith('not ok')]
    if fallos:
        return int(fallos[0].split()[-1]), rojos
    return len(rojos), rojos


SABOTAJES = [
    ('la ficha vuelve a usar la clase que no le llega (caso real del 14-sep)',
     "'<textarea id=\"cli-nota\" class=\"cli-campo-caja\" rows=\"3\"",
     "'<textarea id=\"cli-nota\" class=\"crm-input\" rows=\"3\""),

    ('el boton de guardar vuelve a ser el generico',
     "'<button type=\"button\" class=\"cli-ficha-guardar\" id=\"cli-guardar\">Guardar</button>'",
     "'<button type=\"button\" class=\"crm-btn-primary\" id=\"cli-guardar\">Guardar</button>'"),

    ('alguien mueve el estilo de los campos al bloque que no llega',
     "  .cli-campo-caja {\n    display: block;",
     "  .cli-campo-caja-MOVIDA {\n    display: block;"),

    ('se borra el estilo del nombre',
     "  .cli-ficha-nombre {\n    margin: 0 0 2px;",
     "  .cli-ficha-nombre-BORRADA {\n    margin: 0 0 2px;"),

    ('vuelve una variable de color que no existe',
     "    border: 1px solid var(--crm-line);\n  }\n  .cli-chip-prox {",
     "    border: 1px solid var(--crm-border-inventada);\n  }\n  .cli-chip-prox {"),

    ('se define una variable de la deuda y no se quita de la lista',
     "  .cli-hist { display: flex; flex-direction: column; }",
     "  .cli-hist { display: flex; flex-direction: column; }\n  .crm-input { width: 100%; }"),
]

print('Comprobando que los tests cazan cada forma de dejar la ficha sin estilo.\n')
todos = True
try:
    for nombre, viejo, nuevo in SABOTAJES:
        if ORIG.count(viejo) != 1:
            print('  %-62s -> NO SE PUDO APLICAR (%d)' % (nombre, ORIG.count(viejo)))
            todos = False
            continue
        io.open(F, 'w', encoding='utf-8').write(ORIG.replace(viejo, nuevo, 1))
        n, rojos = corre()
        io.open(F, 'w', encoding='utf-8').write(ORIG)
        ok = n > 0
        todos = todos and ok
        print('  %-62s -> %s' % (nombre, 'CAZADO' if ok else 'NO ROMPE NADA'))
        if ok:
            print('       rojo: %s' % (rojos[0][:70] if rojos else '(sin detalle)'))
finally:
    io.open(F, 'w', encoding='utf-8').write(ORIG)

igual = hashlib.md5(io.open(F, 'rb').read()).hexdigest() == FIRMA
print('\nFichero restaurado identico:', igual)
n, _ = corre()
print('Sin sabotaje -> fallos:', n)
sys.exit(0 if (todos and igual and n == 0) else 1)
