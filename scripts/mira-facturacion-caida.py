#!/usr/bin/env python3
"""Que ve el dueno cuando NO se puede comprobar su suscripcion.

Se cortan a proposito las tres formas de fallar y se mira la pantalla:
  1. la peticion no llega (red caida)
  2. contesta con un error del servidor
  3. contesta bien pero diciendo "no he podido comprobarlo"
En ninguna de las tres puede aparecer un "Todo en orden".
"""
import json
import sys
from playwright.sync_api import sync_playwright

CLIENTE, TOKEN = sys.argv[1], sys.argv[2]
BASE = "http://localhost:4399"
RUTA = "**/portal-api/facturacion*"

CASOS = [
    ("no llega la peticion", lambda r: r.abort()),
    ("el servidor devuelve error", lambda r: r.fulfill(status=500, body="boom")),
    ("contesta ok:false", lambda r: r.fulfill(
        status=200, content_type="application/json",
        body=json.dumps({"ok": False, "datos": None}))),
]

fallos = 0
with sync_playwright() as p:
    nav = p.chromium.launch()
    for nombre, corte in CASOS:
        pag = nav.new_page(viewport={"width": 1180, "height": 900})
        pag.route(RUTA, corte)
        pag.goto(f"{BASE}/cliente/{CLIENTE}?t={TOKEN}", wait_until="networkidle")
        ck = pag.get_by_text("Sólo necesarias")
        if ck.count():
            ck.first.click(force=True); pag.wait_for_timeout(500)
        ir = pag.get_by_text("Ya lo tengo configurado, ir al panel")
        if ir.count():
            ir.first.click(force=True); pag.wait_for_timeout(2000)
        pag.locator(".crm-nav-btn[data-view=billing]").first.click(force=True)
        pag.wait_for_timeout(3000)

        tono = pag.query_selector("#fact-estado").get_attribute("data-tono")
        titulo = pag.inner_text("#fact-titulo")
        detalle = pag.inner_text("#fact-detalle")
        print("\n=== %s ===" % nombre)
        print("tono:", tono)
        print("titulo:", titulo)
        print("detalle:", detalle)

        if "orden" in titulo.lower() or "activa" in titulo.lower():
            print("  MAL: afirma que todo va bien sin haberlo comprobado")
            fallos += 1
        if "Comprobando" in titulo:
            print("  MAL: se queda colgado en 'Comprobando…' para siempre")
            fallos += 1
        if tono == "bien":
            print("  MAL: sale en verde")
            fallos += 1
        pag.close()
    nav.close()

print("\nfallos:", fallos)
sys.exit(1 if fallos else 0)
