#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprueba que la prueba del aviso caza lo que de verdad puede romperse.

Se rompe el codigo a proposito de cuatro maneras distintas, se reconstruye el
sitio y se pasa la prueba. Si la prueba sigue diciendo PASA con el codigo roto,
esa prueba no vigila nada y hay que tirarla.

Al terminar, el fichero se deja como estaba Y SE RECONSTRUYE LIMPIO: si no, en
dist/ se quedaria servido el ultimo sabotaje, que no existe en ningun sitio.

  python3 scripts/sabotaje-aviso-conversion.py
"""
import hashlib
import io
import subprocess
import sys

P = 'src/scripts/measurement.ts'
ORIG = io.open(P, encoding='utf-8').read()
FIRMA = hashlib.md5(ORIG.encode('utf-8')).hexdigest()

SABOTAJES = [
    ('volver a mandar la conversion desde el clic (lo que hacia antes)',
     "if (eventName === 'checkout_form_shown') {\n    return {\n      name: 'checkout_started',",
     "if (eventName === 'checkout_started') {\n    return {\n      name: 'checkout_started',"),

    ('quitar el candado de una conversion por visita',
     "  if (event.name === 'checkout_started') {\n    if (safeSessionGet(OPENAI_CONVERSION_KEY)) return;\n    safeSessionSet(OPENAI_CONVERSION_KEY, '1');\n  }\n\n",
     ""),

    ('quitar la puerta del consentimiento de cookies',
     "  if (localStorage.getItem('nx_cookie_consent') !== 'accepted' || !nxWindow.oaiq) return;\n  const event = openAiEvent(eventName, properties);",
     "  if (!nxWindow.oaiq) return;\n  const event = openAiEvent(eventName, properties);"),

    ('dejar de mandar la conversion (el mapeo devuelve nada)',
     "if (eventName === 'checkout_form_shown') {\n    return {\n      name: 'checkout_started',",
     "if (eventName === 'checkout_form_shown_ROTO') {\n    return {\n      name: 'checkout_started',"),
]


def construye():
    r = subprocess.run(['pnpm', 'build'], capture_output=True, text=True, timeout=900)
    return r.returncode == 0


def prueba():
    r = subprocess.run(['python3', 'scripts/prueba-aviso-conversion.py'],
                       capture_output=True, text=True, timeout=600)
    salida = r.stdout
    fallos = [l.strip().split()[0] for l in salida.splitlines() if 'FALLA' in l and 'RESULTADO' not in l]
    return ('PASA' if 'RESULTADO: PASA' in salida else 'FALLA'), fallos


def main():
    print('Sin tocar nada (linea base):')
    if not construye():
        print('  el build ya falla antes de empezar')
        return 1
    estado, _ = prueba()
    print('  la prueba dice -> %s' % estado)
    if estado != 'PASA':
        print('  la prueba ya falla antes de sabotear nada')
        return 1

    cazados = 0
    for titulo, viejo, nuevo in SABOTAJES:
        print('')
        print('SABOTAJE: %s' % titulo)
        if ORIG.count(viejo) != 1:
            print('  NO SE PUEDE APLICAR (el texto aparece %d veces)' % ORIG.count(viejo))
            continue
        io.open(P, 'w', encoding='utf-8').write(ORIG.replace(viejo, nuevo, 1))
        try:
            if not construye():
                print('  CAZADO: con esto el sitio ni siquiera compila')
                cazados += 1
                continue
            estado, fallos = prueba()
        finally:
            io.open(P, 'w', encoding='utf-8').write(ORIG)

        if estado != 'PASA':
            cazados += 1
            print('  CAZADO: la prueba falla en %s' % (', '.join(fallos) or '(sin detalle)'))
        else:
            print('  NO ROMPE NADA -- la prueba no vigila esto')

    print('')
    print('Reconstruyendo limpio para no dejar un sabotaje servido en dist/...')
    limpio = construye()
    igual = hashlib.md5(io.open(P, 'rb').read()).hexdigest() == FIRMA
    estado_final, _ = prueba() if limpio else ('build roto', [])
    print('  fichero igual que al empezar: %s' % ('si' if igual else 'NO'))
    print('  build limpio: %s · prueba final: %s' % ('si' if limpio else 'NO', estado_final))
    print('')
    print('Cazados %d de %d' % (cazados, len(SABOTAJES)))
    return 0 if (cazados == len(SABOTAJES) and igual and estado_final == 'PASA') else 1


if __name__ == '__main__':
    sys.exit(main())
