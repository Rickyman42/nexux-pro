#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lo unico que importa de la primera pantalla: se ve el boton de comprar?

Se mide en un movil de verdad (Chromium con el tamano de pantalla de un movil),
no leyendo el CSS. Una regla escrita no prueba que el boton se vea: puede estar
ahi y quedar tapada por otra, o por el aviso de cookies.

  python3 scripts/mide-primera-pantalla.py https://nexux.pro

Aprueba si el boton ENTERO queda por encima del aviso de cookies sin bajar nada.
El aviso cuenta como techo porque esta fijo y tapa lo que haya debajo hasta que
alguien lo quita, y casi nadie lo quita antes de mirar la pagina.

Y suspende tambien si el enlace de salida ("Volver a paquetes") va por delante
del boton: era lo primero que se le ofrecia al que venia del anuncio.
"""
import sys

from playwright.sync_api import sync_playwright

# Los tres tamanos cubren de un movil pequeno a uno grande. 96 de cada 100 de
# los que trajo el anuncio venian en movil.
MOVILES = [('movil pequeno', 360, 640), ('movil comun', 375, 667), ('movil grande', 390, 844)]
PAGINAS = ['/paquetes/recepcionista', '/paquetes/equipo']

MEDIDA = """() => {
  const boton = document.querySelector('.plan-action-primary');
  if (!boton) return { error: 'no hay boton de comprar en la pagina' };
  const r = boton.getBoundingClientRect();
  const botonY = Math.round(r.top + window.scrollY);

  const aviso = document.querySelector('#nx-cookie-banner, .cookie-banner');
  const techo = aviso && aviso.getBoundingClientRect().height > 0
    ? aviso.getBoundingClientRect().top : window.innerHeight;

  const salida = document.querySelector('.plan-back');
  const salidaY = salida ? Math.round(salida.getBoundingClientRect().top + window.scrollY) : null;

  return {
    botonY,
    botonAbajo: Math.round(r.bottom),
    techo: Math.round(techo),
    alto: window.innerHeight,
    cabe: Math.round(r.bottom) <= Math.round(techo),
    salidaY,
    salidaAntesDelBoton: salidaY !== null && salidaY < botonY,
  };
}"""


def main():
    base = (sys.argv[1] if len(sys.argv) > 1 else 'https://nexux.pro').rstrip('/')
    fallos = 0

    with sync_playwright() as p:
        navegador = p.chromium.launch(args=['--no-sandbox'])
        for ruta in PAGINAS:
            print('')
            print('=== ' + base + ruta + ' ===')
            for nombre, ancho, alto in MOVILES:
                pagina = navegador.new_page(viewport={'width': ancho, 'height': alto},
                                            device_scale_factor=1)
                try:
                    pagina.goto(base + ruta, wait_until='networkidle', timeout=60000)
                    m = pagina.evaluate(MEDIDA)
                finally:
                    pagina.close()

                etiqueta = '%-14s %dx%d' % (nombre, ancho, alto)

                if m.get('error'):
                    print('  %s  -> MAL: %s' % (etiqueta, m['error']))
                    fallos += 1
                    continue

                margen = m['techo'] - m['botonAbajo']
                if m['cabe']:
                    print('  %s  boton en %4d, libre hasta %4d  -> OK (sobran %dpx)'
                          % (etiqueta, m['botonY'], m['techo'], margen))
                else:
                    fallos += 1
                    print('  %s  boton en %4d, libre hasta %4d  -> MAL (se pasa por %dpx)'
                          % (etiqueta, m['botonY'], m['techo'], -margen))

                if m.get('salidaAntesDelBoton'):
                    fallos += 1
                    print('  %-14s  MAL: la puerta de salida esta en %d, por delante del boton'
                          % ('', m['salidaY']))

    print('')
    print('Fallos: %d' % fallos)
    return 1 if fallos else 0


if __name__ == '__main__':
    sys.exit(main())
