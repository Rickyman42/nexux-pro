#!/usr/bin/env python3
"""Abre el portal en un navegador de verdad y mira que pone la tarjeta de
facturacion. No comprueba el codigo: comprueba lo que le llega a los ojos del
dueno de la peluqueria."""
import sys
from playwright.sync_api import sync_playwright

CLIENTE = sys.argv[1]
TOKEN = sys.argv[2]
SALIDA = sys.argv[3] if len(sys.argv) > 3 else "/tmp/panel.png"
BASE = "http://localhost:4399"

with sync_playwright() as p:
    nav = p.chromium.launch()
    pag = nav.new_page(viewport={"width": 1180, "height": 900})
    pag.goto(f"{BASE}/cliente/{CLIENTE}?t={TOKEN}", wait_until="networkidle")
    print("URL final:", pag.url)

    # Ir a la pestana de Facturacion como lo haria una persona.
    # El portal ensena primero la pantalla de onboarding; se entra al panel
    # igual que lo haria una persona, pulsando el enlace.
    # El aviso de cookies tapa el enlace en pantalla de movil; se quita como
    # lo quitaria una persona antes de seguir.
    ck = pag.get_by_text("Sólo necesarias")
    if ck.count():
        ck.first.click(force=True)
        pag.wait_for_timeout(600)
    ir = pag.get_by_text("Ya lo tengo configurado, ir al panel")
    if ir.count():
        ir.first.click(force=True)
        pag.wait_for_timeout(2500)
    boton = pag.query_selector(".crm-nav-btn[data-view=billing]")
    if not boton:
        print("NO HAY pestana de facturacion. Titulo:", pag.title())
        print(pag.inner_text("body")[:400])
        nav.close()
        sys.exit(1)
    boton.click()
    pag.wait_for_timeout(3500)

    caja = pag.query_selector("#fact-estado")
    print("tono:", caja.get_attribute("data-tono"))
    print("titulo:", pag.inner_text("#fact-titulo"))
    print("detalle:", pag.inner_text("#fact-detalle"))
    print("  %-9s %s" % ("plan:", pag.inner_text("#fact-plan")))
    print("  %-9s %s" % ("precio:", pag.inner_text("#fact-precio")))
    print("  %s -> %s" % (pag.inner_text("#fact-proximo-lbl"), pag.inner_text("#fact-proximo")))
    print("  %-9s %s" % ("tarjeta:", pag.inner_text("#fact-tarjeta")))
    print("pie:", pag.inner_text("#fact-pie"))

    caja.screenshot(path=SALIDA)
    # Y lo mismo en pantalla de movil, que es donde lo va a mirar el dueno.
    pag.set_viewport_size({"width": 390, "height": 850})
    pag.wait_for_timeout(500)
    caja.screenshot(path=SALIDA.replace(".png", "-movil.png"))
    print("captura:", SALIDA)
    nav.close()
