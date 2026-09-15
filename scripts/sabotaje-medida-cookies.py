#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprueba que la prueba de la cuenta de cookies caza cada forma de romperla.

Todas estas averias son mudas: el aviso sigue saliendo, los botones siguen
funcionando y el permiso se sigue guardando bien. Lo unico que pasa es que el
numero que sacamos es mentira -- y un numero mentiroso es peor que no tenerlo,
porque con el se decide.

  python3 scripts/sabotaje-medida-cookies.py
"""
import hashlib
import io
import os
import shutil
import subprocess
import sys

AVISO = 'src/components/AvisoCookies.astro'
ESTATICO = '.vercel/output/static'
SERVIDO = '/tmp/cookies'
PUERTO = 8896

ORIG = io.open(AVISO, encoding='utf-8').read()
FIRMA = hashlib.md5(ORIG.encode('utf-8')).hexdigest()

SABOTAJES = [
    ('no esperar a Umami (se pierden los avisos de nada mas cargar)',
     """      var intentos = 0;
      (function reintenta() {
        if (window.umami && typeof window.umami.track === 'function') {
          window.umami.track(evento, datos || {});
          return;
        }
        if (intentos++ < 40) window.setTimeout(reintenta, 500);
      })();""",
     """      if (window.umami && typeof window.umami.track === 'function') {
        window.umami.track(evento, datos || {});
      }"""),

    ('dejar de contar a cuanta gente se le enseña (adios porcentaje)',
     "      medir('cookies_mostrado', { pagina: location.pathname });",
     "      // medir('cookies_mostrado', { pagina: location.pathname });"),

    ('cambiar las dos respuestas (aceptar cuenta como rechazar)',
     "medir('cookies_respondido', { respuesta: 'acepta', pagina: location.pathname });",
     "medir('cookies_respondido', { respuesta: 'solo_necesarias', pagina: location.pathname });"),

    ('contar el aviso tambien a quien ya contesto (infla el total)',
     """    if (!stored) {
      banner.removeAttribute('hidden');""",
     """    medir('cookies_mostrado', { pagina: location.pathname });
    if (!stored) {
      banner.removeAttribute('hidden');"""),
]


def construye_y_prueba():
    r = subprocess.run(['pnpm', 'build'], capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        print('    (no compila con este sabotaje)')
        return -1
    if os.path.isdir(SERVIDO):
        shutil.rmtree(SERVIDO)
    shutil.copytree(ESTATICO, SERVIDO)
    m = subprocess.run([sys.executable, 'scripts/prueba-medida-cookies.py',
                        'http://127.0.0.1:%d' % PUERTO],
                       capture_output=True, text=True, timeout=600)
    ultima = [l for l in m.stdout.splitlines() if l.startswith('Fallos:')]
    return int(ultima[0].split()[-1]) if ultima else -1


def main():
    print('Antes de nada: sin tocar nada, la prueba tiene que estar en verde.')
    base = construye_y_prueba()
    print('  sin sabotaje -> %d fallos' % base)
    if base != 0:
        print('  ya esta roto ANTES de sabotearlo: no se puede probar nada')
        return 1

    cazados = 0
    for titulo, viejo, nuevo in SABOTAJES:
        print('')
        print('SABOTAJE: %s' % titulo)
        if ORIG.count(viejo) != 1:
            print('  NO SE PUEDE APLICAR (aparece %d veces)' % ORIG.count(viejo))
            continue
        io.open(AVISO, 'w', encoding='utf-8').write(ORIG.replace(viejo, nuevo, 1))
        try:
            fallos = construye_y_prueba()
        finally:
            io.open(AVISO, 'w', encoding='utf-8').write(ORIG)

        if fallos > 0:
            cazados += 1
            print('  CAZADO (%d comprobaciones en rojo)' % fallos)
        else:
            print('  NO ROMPE NADA -- la prueba no vigila esto')

    io.open(AVISO, 'w', encoding='utf-8').write(ORIG)
    ahora = hashlib.md5(io.open(AVISO, 'rb').read()).hexdigest()
    print('')
    print('Fichero restaurado igual que estaba: %s' % ('si' if ahora == FIRMA else 'NO'))
    print('Cazados %d de %d' % (cazados, len(SABOTAJES)))
    return 0 if cazados == len(SABOTAJES) and ahora == FIRMA else 1


if __name__ == '__main__':
    sys.exit(main())
