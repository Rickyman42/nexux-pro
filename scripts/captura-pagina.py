#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Foto de una pagina entera, para usarla de fondo del mapa de calor.

Una cuadricula de cuadritos de colores no dice nada. Encima de la pagina de
verdad, dice donde pulsa la gente y donde deja de bajar.

  python3 scripts/captura-pagina.py <url> <ancho> <fichero.png>
"""
import sys

from playwright.sync_api import sync_playwright


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        return 2
    url, ancho, salida = sys.argv[1], int(sys.argv[2]), sys.argv[3]

    with sync_playwright() as p:
        navegador = p.chromium.launch(args=['--no-sandbox'])
        pagina = navegador.new_page(viewport={'width': ancho, 'height': 900},
                                    device_scale_factor=1)
        pagina.goto(url, wait_until='networkidle', timeout=60000)

        # El aviso de cookies tapa el pie en la foto y ahi no aporta nada:
        # ocupa sitio y confunde al leer el mapa.
        pagina.evaluate("""() => {
          const b = document.getElementById('nx-cookie-banner');
          if (b) b.remove();
          window.scrollTo(0, document.body.scrollHeight);
        }""")
        pagina.wait_for_timeout(1200)          # que terminen las animaciones al bajar
        pagina.evaluate('() => window.scrollTo(0, 0)')
        pagina.wait_for_timeout(600)

        alto = pagina.evaluate('() => document.documentElement.scrollHeight')
        pagina.screenshot(path=salida, full_page=True)
        navegador.close()

    print('%d %d' % (ancho, alto))
    return 0


if __name__ == '__main__':
    sys.exit(main())
