#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprueba que los tests del pago cazan cada forma de romperlo.

Este es el camino del dinero: si se rompe y nadie se entera, el cliente paga y
no recibe nada.
"""
import io
import hashlib
import subprocess
import sys

CS = 'api/stripe/create-session.js'
WH = 'api/webhook/stripe.js'
CH = 'src/scripts/checkout.ts'
T_PAGO = 'test/pantalla-de-pago.test.mjs'
T_E2E = 'test/integracion-camino-del-dinero.test.mjs'

ORIG = {p: io.open(p, encoding='utf-8').read() for p in (CS, WH, CH)}
FIRMA = {p: hashlib.md5(io.open(p, 'rb').read()).hexdigest() for p in ORIG}


def corre(test):
    r = subprocess.run(['node', '--test', test], capture_output=True, text=True, timeout=600)
    fallos = [l for l in r.stdout.splitlines() if l.startswith('# fail')]
    rojos = [l.split('- ', 1)[1] for l in r.stdout.splitlines() if l.startswith('not ok')]
    return (int(fallos[0].split()[-1]) if fallos else -1), rojos


SABOTAJES = [
    (CS, T_PAGO, 'la pantalla de pago deja de preguntar el nombre (NADIE se daria de alta)',
     "  if (!salonConocido) {",
     "  if (false) {"),

    (CS, T_PAGO, 'se le pregunta tambien a quien ya nos lo habia dicho',
     "  const salonConocido = typeof body.salon === 'string' && body.salon.trim() !== '';",
     "  const salonConocido = false;"),

    (CS, T_PAGO, 'se cambia el precio de 29 EUR sin querer',
     "      priceFallback: 'price_1U6jqd2SQwDzHtsFf3wEcuQe',",
     "      priceFallback: 'price_1UBHkE2SQwDzHtsFTVWQ67l5',"),

    (CS, T_PAGO, 'la tarjeta se saca fuera de nuestra pagina',
     "  params.append('ui_mode', 'embedded_page');",
     "  params.append('ui_mode', 'hosted');"),

    (CH, T_PAGO, 'vuelve el formulario de antes del pago',
     "  loading.removeAttribute('hidden');\n  return abrirPagoStripe(plan, yaSabido);",
     "  datos.removeAttribute('hidden');\n  negocio.focus();\n  return abrirPagoStripe(plan, yaSabido);"),

    (WH, T_E2E, 'el alta deja de leer el campo de la pantalla de pago',
     "    salon: md.salon || campoDelPago(session, 'salon') || null,",
     "    salon: md.salon || null,"),

    (WH, T_E2E, 'un nombre en blanco cuela como valido (cuenta llamada "   ")',
     "  return valor ? String(valor).trim() || null : null;",
     "  return valor ? String(valor) : null;"),
]

print('Comprobando que los tests cazan cada forma de romper el cobro.\n')
todos = True
try:
    for fichero, test, nombre, viejo, nuevo in SABOTAJES:
        if ORIG[fichero].count(viejo) != 1:
            print('  %-66s -> NO SE PUDO APLICAR' % nombre)
            todos = False
            continue
        io.open(fichero, 'w', encoding='utf-8').write(ORIG[fichero].replace(viejo, nuevo, 1))
        n, rojos = corre(test)
        io.open(fichero, 'w', encoding='utf-8').write(ORIG[fichero])
        ok = n > 0
        todos = todos and ok
        print('  %-66s -> %s' % (nombre, 'CAZADO' if ok else 'NO ROMPE NADA'))
        if ok:
            print('       rojo: %s' % (rojos[0][:74] if rojos else '(sin detalle)'))
finally:
    for p, texto in ORIG.items():
        io.open(p, 'w', encoding='utf-8').write(texto)

iguales = all(hashlib.md5(io.open(p, 'rb').read()).hexdigest() == FIRMA[p] for p in ORIG)
print('\nFicheros restaurados identicos:', iguales)
a, _ = corre(T_PAGO)
b, _ = corre(T_E2E)
print('Sin sabotaje -> fallos: pantalla de pago %d, camino del dinero %d' % (a, b))
sys.exit(0 if (todos and iguales and a == 0 and b == 0) else 1)
