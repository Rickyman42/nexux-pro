#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cuanto ocupa el aviso de cookies, y que siga siendo un aviso honesto.

Encogerlo es facil si se hace trampa: esconder el boton de rechazar, quitar el
enlace al detalle, o dejar "aceptar" grande y "solo necesarias" chiquitito. Eso
no es un aviso mas pequeno, es un aviso ilegal. Por eso aqui se mide el tamano Y
las tres trampas.

  python3 scripts/mide-aviso-cookies.py https://nexux.pro

El limite de "aceptar no puede pesar mas que rechazar" es del 15%: por debajo de
eso la diferencia es de como mide cada letra, no de intencion.

Y el alto tiene tope: 105px. No es un numero redondo porque si. Antes de
encogerlo median 122 y ahora miden 96; 105 esta en medio, asi que suspende si
alguien devuelve el adorno de antes y aguanta que el texto se reparta en una
linea mas. Sin este tope, el alto solo se imprimiria y una vuelta atras pasaria
por buena.
"""
import sys

from playwright.sync_api import sync_playwright

MOVILES = [('movil pequeno', 360, 640), ('movil comun', 375, 667), ('movil grande', 390, 844)]
TOPE_ALTO = 105
PAGINA = '/paquetes/recepcionista'

MEDIDA = """() => {
  const b = document.querySelector('#nx-cookie-banner');
  if (!b || b.hasAttribute('hidden')) return { error: 'el aviso no sale' };
  const r = b.getBoundingClientRect();
  const aceptar = document.querySelector('#cookie-accept').getBoundingClientRect();
  const rechazar = document.querySelector('#cookie-reject').getBoundingClientRect();
  const mas = document.querySelector('.cookie-mas');
  const boton = document.querySelector('.plan-action-primary');
  const rb = boton ? boton.getBoundingClientRect() : null;
  return {
    alto: Math.round(r.height),
    trozoDePantalla: Math.round((r.height / window.innerHeight) * 100),
    anchoAceptar: Math.round(aceptar.width),
    anchoRechazar: Math.round(rechazar.width),
    rechazarSeVe: rechazar.width > 0 && rechazar.height > 0,
    enlaceDetalle: mas ? mas.getAttribute('href') : null,
    tapaElBotonDeComprar: rb ? Math.round(rb.bottom) > Math.round(r.top) : null,
  };
}"""


def main():
    base = (sys.argv[1] if len(sys.argv) > 1 else 'https://nexux.pro').rstrip('/')
    fallos = 0

    def comprueba(titulo, ok, detalle=''):
        nonlocal fallos
        if ok:
            print('      %-46s -> OK %s' % (titulo, detalle))
        else:
            fallos += 1
            print('      %-46s -> MAL %s' % (titulo, detalle))

    with sync_playwright() as p:
        navegador = p.chromium.launch(args=['--no-sandbox'])
        for nombre, ancho, alto in MOVILES:
            ctx = navegador.new_context(viewport={'width': ancho, 'height': alto})
            pg = ctx.new_page()
            pg.goto(base + PAGINA, wait_until='networkidle', timeout=60000)
            pg.wait_for_timeout(1800)  # el aviso entra con una animacion de 1s
            m = pg.evaluate(MEDIDA)
            ctx.close()

            print('')
            print('  %s (%dx%d)' % (nombre, ancho, alto))
            if m.get('error'):
                print('      %s' % m['error'])
                fallos += 1
                continue

            print('      alto del aviso: %dpx (%d%% de la pantalla)'
                  % (m['alto'], m['trozoDePantalla']))
            comprueba('no ocupa mas de %dpx' % TOPE_ALTO, m['alto'] <= TOPE_ALTO,
                      '(%dpx)' % m['alto'])
            comprueba('el boton de rechazar se ve', m['rechazarSeVe'])
            mayor = max(m['anchoAceptar'], m['anchoRechazar'])
            menor = min(m['anchoAceptar'], m['anchoRechazar'])
            dif = round((mayor - menor) / mayor * 100) if mayor else 0
            comprueba('aceptar no pesa mas que rechazar', dif <= 15,
                      '(aceptar %dpx, rechazar %dpx, %d%% de diferencia)'
                      % (m['anchoAceptar'], m['anchoRechazar'], dif))
            comprueba('hay enlace a la politica', m['enlaceDetalle'] == '/privacidad',
                      '(%s)' % m['enlaceDetalle'])
            comprueba('no tapa el boton de comprar', m['tapaElBotonDeComprar'] is False)

        navegador.close()

    print('')
    print('Fallos: %d' % fallos)
    return 1 if fallos else 0


if __name__ == '__main__':
    sys.exit(main())
