#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prueba de verdad, en un navegador, sobre el sitio ya construido.

Se finge el pixel de OpenAI (window.oaiq) y se mira QUE le llega:
  A. Pulsar el boton de pagar          -> NO debe mandar conversion
  B. La pasarela de Stripe aparece     -> SI debe mandar conversion
  C. La pasarela aparece por 2a vez    -> NO debe repetirla
  D. Sin cookies aceptadas             -> NO debe mandar nada (control)
  E. Umami sigue recibiendo el clic    -> no se pierde dato (control positivo)

  python3 scripts/prueba-aviso-conversion.py
"""
import json
import subprocess
import sys
import threading
import http.server
import functools
import socketserver

RAIZ = 'dist/client'
PUERTO = 4599
RUTA = '/paquetes/recepcionista'


def sirve():
    manejador = functools.partial(http.server.SimpleHTTPRequestHandler, directory=RAIZ)
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(('127.0.0.1', PUERTO), manejador)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def main():
    from playwright.sync_api import sync_playwright

    srv = sirve()
    resultados = {}
    try:
        with sync_playwright() as p:
            navegador = p.chromium.launch()
            pagina = navegador.new_page(viewport={'width': 390, 'height': 844})

            # Nada de esta prueba puede ensuciar la analitica de verdad.
            pagina.route('**/stats/**', lambda r: r.abort())
            pagina.route('**/plausible.io/**', lambda r: r.abort())
            pagina.route('**/googletagmanager.com/**', lambda r: r.abort())
            pagina.route('**/facebook.net/**', lambda r: r.abort())
            pagina.route('**/js.stripe.com/**', lambda r: r.abort())

            # El pixel falso y un Umami falso, puestos ANTES de que cargue la pagina.
            pagina.add_init_script("""
              window.__oai = [];
              window.oaiq = function(){ window.__oai.push(Array.from(arguments)); };
              window.__umami = [];
              window.umami = { track: function(n,p){ window.__umami.push([n,p]); } };
            """)

            # --- D. control: SIN consentimiento no puede salir nada ---
            pagina.goto(f'http://127.0.0.1:{PUERTO}{RUTA}?utm_source=chatgpt&oppref=prueba',
                        wait_until='networkidle')
            pagina.evaluate("window.nxMeasure('checkout_form_shown', {plan:'recepcionista'})")
            resultados['D_sin_consentimiento'] = pagina.evaluate(
                "window.__oai.filter(a => a[1]==='checkout_started').length")

            # A partir de aqui, con cookies aceptadas.
            pagina.evaluate("localStorage.setItem('nx_cookie_consent','accepted')")
            pagina.reload(wait_until='networkidle')
            pagina.evaluate("window.__oai = []; window.__umami = [];")

            # --- A. pulsar el boton de pagar ---
            boton = pagina.locator('[data-checkout-plan]').first
            boton.click(timeout=8000, force=True)
            pagina.wait_for_timeout(800)
            resultados['A_conversiones_tras_pulsar'] = pagina.evaluate(
                "window.__oai.filter(a => a[1]==='checkout_started').length")
            resultados['E_umami_vio_el_clic'] = pagina.evaluate(
                "window.__umami.filter(a => a[0]==='checkout_started').length")

            # --- B. la pasarela aparece ---
            pagina.evaluate("window.nxMeasure('checkout_form_shown', {plan:'recepcionista', ms: 900})")
            pagina.wait_for_timeout(300)
            resultados['B_conversiones_tras_pasarela'] = pagina.evaluate(
                "window.__oai.filter(a => a[1]==='checkout_started').length")

            # --- C. la pasarela aparece otra vez ---
            pagina.evaluate("window.nxMeasure('checkout_form_shown', {plan:'recepcionista', ms: 900})")
            pagina.wait_for_timeout(300)
            resultados['C_conversiones_tras_repetir'] = pagina.evaluate(
                "window.__oai.filter(a => a[1]==='checkout_started').length")

            resultados['_carga_enviada'] = pagina.evaluate(
                "JSON.stringify((window.__oai.find(a => a[1]==='checkout_started')||[])[2] || null)")
            navegador.close()
    finally:
        srv.shutdown()

    esperado = {
        'D_sin_consentimiento': 0,
        'A_conversiones_tras_pulsar': 0,
        'E_umami_vio_el_clic': 1,
        'B_conversiones_tras_pasarela': 1,
        'C_conversiones_tras_repetir': 1,
    }

    print('')
    bien = True
    for clave, quiero in esperado.items():
        tengo = resultados.get(clave)
        ok = tengo == quiero
        bien = bien and ok
        print('  %-32s esperado %s  medido %s  %s' % (clave, quiero, tengo, 'OK' if ok else 'FALLA'))
    print('')
    print('  carga que viaja a OpenAI: %s' % resultados.get('_carga_enviada'))
    print('')
    print('RESULTADO: %s' % ('PASA' if bien else 'FALLA'))
    return 0 if bien else 1


if __name__ == '__main__':
    sys.exit(main())
