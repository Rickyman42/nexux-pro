#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprueba que los tests del mapa de calor cazan cada forma de romperlo.

Un test que no se pone rojo cuando metes el fallo a mano no vigila nada.
"""
import io
import hashlib
import subprocess
import sys

MED = 'src/scripts/measurement.ts'
PAG = 'src/scripts/paginas-medidas.mjs'
TEST = 'test/mapa-de-calor.test.mjs'

ORIG = {p: io.open(p, encoding='utf-8').read() for p in (MED, PAG)}
FIRMA = {p: hashlib.md5(io.open(p, 'rb').read()).hexdigest() for p in ORIG}


def corre():
    r = subprocess.run(['node', '--test', TEST], capture_output=True, text=True, timeout=180)
    fallos = [l for l in r.stdout.splitlines() if l.startswith('# fail')]
    rojos = [l.split('- ', 1)[1] for l in r.stdout.splitlines() if l.startswith('not ok')]
    return (int(fallos[0].split()[-1]) if fallos else -1), rojos


SABOTAJES = [
    (MED, 'el mapa se esconde detras del aviso de cookies',
     "  if (!esPaginaMedible(location.pathname)) return;",
     "  if (!esPaginaMedible(location.pathname)) return;\n  if (localStorage.getItem('nx_cookie_consent') !== 'accepted') return;"),

    (MED, 'los puntos del mapa se mandan tambien a los pixeles de publicidad',
     "    medirSoloEnUmami('heatmap_click', {",
     "    measure('heatmap_click', {"),

    (MED, 'se quita el filtro de pagina (mediria dentro del CRM del cliente)',
     "  if (!esPaginaMedible(location.pathname)) return;\n\n  const casillasConRaton",
     "  const casillasConRaton"),

    (MED, 'se guardan las coordenadas exactas en vez de la casilla',
     "  return {\n    grid_x: Math.min(MAPA_COLUMNAS - 1,",
     "  return {\n    clientX: x,\n    clientY: y,\n    grid_x: Math.min(MAPA_COLUMNAS - 1,"),

    (MED, 'se quitan los topes: un martilleo llena la base de datos',
     "const MAPA_TOPE_CLICS = 40;      // por si alguien martillea la pantalla",
     "// sin tope"),

    (MED, 'deja de marcarse el clic que no da en nada',
     "      sobre: destino?.closest(SELECTOR_PULSABLE) ? 'pulsable' : 'nada',",
     "      sobre: 'pulsable',"),

    (PAG, 'la lista se convierte en una de prohibidas (deja pasar lo nuevo)',
     "export const PAGINAS_MEDIDAS = ['/paquetes', '/comparativa', '/alternativa-a-booksy', '/gracias'];",
     "export const PAGINAS_PROHIBIDAS = ['/admin', '/cliente', '/reservar'];\nexport const PAGINAS_MEDIDAS = [];"),

    (PAG, 'el portal del cliente pasa a medirse',
     "  return PAGINAS_MEDIDAS.some((p) => limpia === p || limpia.startsWith(p + '/'));",
     "  return true;"),
]

print('Comprobando que los tests cazan cada forma de romperlo.\n')
todos = True
try:
    for fichero, nombre, viejo, nuevo in SABOTAJES:
        if ORIG[fichero].count(viejo) != 1:
            print('  %-64s -> NO SE PUDO APLICAR (el codigo cambio)' % nombre)
            todos = False
            continue
        io.open(fichero, 'w', encoding='utf-8').write(ORIG[fichero].replace(viejo, nuevo, 1))
        n, rojos = corre()
        io.open(fichero, 'w', encoding='utf-8').write(ORIG[fichero])
        ok = n > 0
        todos = todos and ok
        print('  %-64s -> %s' % (nombre, 'CAZADO' if ok else 'NO ROMPE NADA (el test no sirve)'))
        if ok:
            print('       rojo: %s' % (rojos[0][:72] if rojos else '(sin detalle)'))
finally:
    for p, texto in ORIG.items():
        io.open(p, 'w', encoding='utf-8').write(texto)

iguales = all(hashlib.md5(io.open(p, 'rb').read()).hexdigest() == FIRMA[p] for p in ORIG)
print('\nFicheros restaurados identicos:', iguales)
n, _ = corre()
print('Comprobacion final sin sabotaje -> fallos:', n)
sys.exit(0 if (todos and iguales and n == 0) else 1)
