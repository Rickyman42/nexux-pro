#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quitar el aviso de la ficha de producto: que ha pasado de verdad.

No basta con que el aviso desaparezca de la pagina. Hay que comprobar las tres
cosas que van juntas, y una de ellas es legal:

  1. En la ficha no sale el aviso.
  2. Y ADEMAS no se pide nada a Google, Meta ni OpenAI. Quitar el aviso y dejar
     los pixeles seria cargar rastreadores de terceros sin permiso.
  3. En el resto de la web el aviso SIGUE saliendo. Sin esta, un fallo que lo
     quitara de todas partes pasaria por exito.

Y la cuarta, que es el precio que se paga: a quien ya dijo que si en otra pagina
se le siguen cargando los pixeles en la ficha. Eso confirma que lo unico que se
pierde es al que llega directo del anuncio.

  python3 scripts/prueba-sin-aviso-en-ficha.py https://nexux.pro

OJO al correrlo contra un build local: el pixel de OpenAI solo se pinta si esta
puesta PUBLIC_OPENAI_ADS_PIXEL_ID, que en local no lo esta. En local ese trozo
no prueba nada; contra produccion si.
"""
import sys

from playwright.sync_api import sync_playwright

FICHA = '/paquetes/recepcionista'
OTRA = '/blog/cuanto-cuesta-cita-perdida'

RASTREADORES = ['googletagmanager.com', 'connect.facebook.net', 'bzrcdn.openai.com']


def main():
    base = (sys.argv[1] if len(sys.argv) > 1 else 'https://nexux.pro').rstrip('/')
    fallos = 0

    def comprueba(titulo, esperado, real):
        nonlocal fallos
        if esperado == real:
            print('  %-54s -> OK' % titulo)
        else:
            fallos += 1
            print('  %-54s -> MAL (esperaba %r, es %r)' % (titulo, esperado, real))

    with sync_playwright() as p:
        navegador = p.chromium.launch(args=['--no-sandbox'])

        def visita(ruta, consentimiento=None):
            ctx = navegador.new_context(viewport={'width': 375, 'height': 667})
            if consentimiento:
                ctx.add_init_script(
                    "try { localStorage.setItem('nx_cookie_consent', '%s'); } catch (e) {}"
                    % consentimiento)
            pedidos = []
            pg = ctx.new_page()
            pg.on('request', lambda r: pedidos.append(r.url))
            pg.goto(base + ruta, wait_until='networkidle', timeout=60000)
            pg.wait_for_timeout(2000)
            return ctx, pg, pedidos

        def llamados(pedidos):
            return sorted({t for t in RASTREADORES if any(t in u for u in pedidos)})

        print('=== 1. En la ficha de producto no sale el aviso ===')
        ctx, pg, pedidos = visita(FICHA)
        comprueba('el aviso no esta ni en el HTML', 0,
                  pg.evaluate("document.querySelectorAll('#nx-cookie-banner').length"))
        print('=== 2. Y no se pide nada a ningun rastreador ===')
        comprueba('no se llama a Google, Meta ni OpenAI', [], llamados(pedidos))
        comprueba('el boton de comprar sigue en su sitio', True,
                  pg.evaluate("(() => { const b = document.querySelector('.plan-action-primary');"
                              " return !!b && b.getBoundingClientRect().bottom <= window.innerHeight; })()"))
        ctx.close()

        print('')
        print('=== 3. En el resto de la web el aviso SIGUE saliendo (control) ===')
        ctx, pg, pedidos = visita(OTRA)
        comprueba('el aviso esta', 1,
                  pg.evaluate("document.querySelectorAll('#nx-cookie-banner').length"))
        comprueba('y se ve', True, pg.locator('#nx-cookie-banner').is_visible())
        comprueba('sin contestar, tampoco se llama a nadie', [], llamados(pedidos))
        ctx.close()

        print('')
        print('=== 4. A quien ya dijo que si, en la ficha se le siguen cargando ===')
        print('     (esto es lo que mide el precio: solo se pierde al que llega del anuncio)')
        ctx, pg, pedidos = visita(FICHA, consentimiento='accepted')
        pedidos_ok = llamados(pedidos)
        print('     rastreadores cargados: %s' % (', '.join(pedidos_ok) or 'ninguno'))
        comprueba('Google se carga con permiso', True, 'googletagmanager.com' in pedidos_ok)
        comprueba('Meta se carga con permiso', True, 'connect.facebook.net' in pedidos_ok)
        if any('bzrcdn.openai.com' in u or 'oaiq' in u for u in pedidos) or \
                pg.evaluate("typeof window.oaiq !== 'undefined'"):
            comprueba('OpenAI se carga con permiso', True, True)
        else:
            print('  %-54s -> AVISO: no hay pixel de OpenAI en esta pagina'
                  % 'OpenAI se carga con permiso')
            print('       (normal en un build local sin PUBLIC_OPENAI_ADS_PIXEL_ID;'
                  ' contra produccion NO deberia salir este aviso)')
        ctx.close()

        navegador.close()

    print('')
    print('Fallos: %d' % fallos)
    return 1 if fallos else 0


if __name__ == '__main__':
    sys.exit(main())
