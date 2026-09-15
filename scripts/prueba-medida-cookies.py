#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprueba que la cuenta de quien acepta las cookies mide lo que dice medir.

Que el codigo este escrito no prueba nada: el aviso sale antes de que Umami
haya cargado, y si no se espera, los avisos que se enseñan nada mas abrir la
pagina no se cuentan NUNCA. El porcentaje saldria inflado y nadie se enteraria.

Se abre la pagina de verdad en un navegador de verdad, con un Umami de mentira
que apunta lo que le llega, y se prueban los cinco casos.

  python3 scripts/prueba-medida-cookies.py http://127.0.0.1:8896
"""
import sys

from playwright.sync_api import sync_playwright

# Una pagina que SI lleva aviso. Las fichas de producto dejaron de llevarlo el
# 15-sep-2026 por decision de Ricardo, asi que ahi no hay nada que medir.
RUTA = '/blog/cuanto-cuesta-cita-perdida'

# Umami de mentira, puesto ANTES de que corra nada de la pagina.
ESPIA = """
window.__visto = [];
window.umami = { track: (n, d) => { window.__visto.push({ n, d }); } };
"""

# El mismo espia, pero Umami no aparece hasta pasados 2 segundos. Es lo que pasa
# de verdad: el script va con defer y el aviso sale antes.
ESPIA_TARDE = """
window.__visto = [];
setTimeout(() => {
  window.umami = { track: (n, d) => { window.__visto.push({ n, d }); } };
}, 2000);
"""


def main():
    base = (sys.argv[1] if len(sys.argv) > 1 else 'https://nexux.pro').rstrip('/')
    fallos = 0

    def comprueba(titulo, esperado, real):
        nonlocal fallos
        if esperado == real:
            print('  %-52s -> OK' % titulo)
        else:
            fallos += 1
            print('  %-52s -> MAL (esperaba %r, es %r)' % (titulo, esperado, real))

    with sync_playwright() as p:
        navegador = p.chromium.launch(args=['--no-sandbox'])

        def abre(espia=ESPIA, consentimiento=None):
            ctx = navegador.new_context(viewport={'width': 375, 'height': 667})
            ctx.add_init_script(espia)
            if consentimiento:
                ctx.add_init_script(
                    "try { localStorage.setItem('nx_cookie_consent', '%s'); } catch (e) {}"
                    % consentimiento)
            pg = ctx.new_page()
            pg.goto(base + RUTA, wait_until='networkidle', timeout=60000)
            return ctx, pg

        print('=== 1. Al enseñar el aviso se cuenta ===')
        ctx, pg = abre()
        pg.wait_for_timeout(1500)
        visto = pg.evaluate('window.__visto')
        nombres = [v['n'] for v in visto]
        comprueba('se apunta que se ha enseñado', 1, nombres.count('cookies_mostrado'))
        # El servidor de pruebas sirve /ruta/ y produccion sirve /ruta: da igual,
        # lo que importa es que diga de que pagina viene.
        pagina = next((v['d'].get('pagina') for v in visto if v['n'] == 'cookies_mostrado'), None)
        comprueba('se apunta en que pagina', RUTA, (pagina or '').rstrip('/'))
        comprueba('el aviso se ve de verdad', True, pg.locator('#nx-cookie-banner').is_visible())
        ctx.close()

        print('')
        print('=== 2. "Aceptar todo" ===')
        ctx, pg = abre()
        pg.wait_for_timeout(1000)
        pg.click('#cookie-accept')
        pg.wait_for_timeout(500)
        visto = pg.evaluate('window.__visto')
        resp = [v for v in visto if v['n'] == 'cookies_respondido']
        comprueba('se apunta una respuesta, solo una', 1, len(resp))
        comprueba('dice que acepta', 'acepta', resp[0]['d'].get('respuesta') if resp else None)
        comprueba('queda guardado el permiso', 'accepted',
                  pg.evaluate("localStorage.getItem('nx_cookie_consent')"))
        ctx.close()

        print('')
        print('=== 3. "Solo necesarias" ===')
        ctx, pg = abre()
        pg.wait_for_timeout(1000)
        pg.click('#cookie-reject')
        pg.wait_for_timeout(500)
        visto = pg.evaluate('window.__visto')
        resp = [v for v in visto if v['n'] == 'cookies_respondido']
        comprueba('se apunta una respuesta, solo una', 1, len(resp))
        comprueba('dice que solo las necesarias', 'solo_necesarias',
                  resp[0]['d'].get('respuesta') if resp else None)
        comprueba('queda guardado que NO', 'rejected',
                  pg.evaluate("localStorage.getItem('nx_cookie_consent')"))
        ctx.close()

        print('')
        print('=== 4. A quien ya contesto no se le vuelve a enseñar ni a contar ===')
        ctx, pg = abre(consentimiento='accepted')
        pg.wait_for_timeout(1500)
        nombres = [v['n'] for v in pg.evaluate('window.__visto')]
        comprueba('no se cuenta otra vez', 0, nombres.count('cookies_mostrado'))
        comprueba('el aviso no sale', False, pg.locator('#nx-cookie-banner').is_visible())
        ctx.close()

        print('')
        print('=== 5. Si Umami tarda 2 segundos, el aviso SE SIGUE contando ===')
        print('     (sin la espera, este es el caso que se perderia entero)')
        ctx, pg = abre(espia=ESPIA_TARDE)
        pg.wait_for_timeout(3500)
        nombres = [v['n'] for v in pg.evaluate('window.__visto')]
        comprueba('se cuenta aunque Umami llegue tarde', 1, nombres.count('cookies_mostrado'))
        ctx.close()

        navegador.close()

    print('')
    print('Fallos: %d' % fallos)
    return 1 if fallos else 0


if __name__ == '__main__':
    sys.exit(main())
