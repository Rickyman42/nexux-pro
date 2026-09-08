#!/usr/bin/env python3
"""Que en la pantalla NO quede ninguna forma de cancelar solo.

Lo que se comprueba:
  - no hay ningun boton que diga cancelar ni que lleve al portal de Stripe;
  - no queda ni un enlace a stripe.com en toda la pagina;
  - si esta el bloque "¿Quieres cancelar?" y lleva al bot de soporte;
  - y que dice por que no hay boton, sin sonar a que se le pone dificil irse.
"""
import hashlib
import json
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

CLIENTE = "estudio-ricardo-demo-mostoles-946279"
CFG = Path("/home/nexux/nexux-clients/clients") / CLIENTE / "config.json"
COPIA = Path("/tmp/config-antes-de-baja.json")
BASE = "http://localhost:4399"
SOPORTE = "t.me/nexux_soporte_bot"

shutil.copy2(CFG, COPIA)
md5 = hashlib.md5(CFG.read_bytes()).hexdigest()
original = json.loads(CFG.read_text(encoding="utf-8"))
TOKEN = original["accessToken"]
ahora = datetime.now(timezone.utc)
fallos = []

# Un cliente que paga, que es quien podria querer cancelar.
c = dict(original)
c.update({
    "stripeCustomerId": "cus_de_mentira", "stripeSubscriptionId": "sub_de_mentira",
    "suscripcionEstado": "active", "cancelaAlFinal": False, "cambioProgramado": None,
    "renuevaEl": (ahora + timedelta(days=23)).isoformat().replace("+00:00", "Z"),
    "renovacionComprobadaEn": ahora.isoformat().replace("+00:00", "Z"),
    "tarjetaResumen": {"marca": "visa", "ultimos4": "4242", "caduca": "07/2029"},
})
CFG.write_text(json.dumps(c, indent=2, ensure_ascii=False), encoding="utf-8")

try:
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pag = nav.new_page(viewport={"width": 1180, "height": 1000})
        pag.goto(f"{BASE}/cliente/{CLIENTE}?t={TOKEN}", wait_until="networkidle")
        ck = pag.get_by_text("Sólo necesarias")
        if ck.count():
            ck.first.click(force=True); pag.wait_for_timeout(500)
        ir = pag.get_by_text("Ya lo tengo configurado, ir al panel")
        if ir.count():
            ir.first.click(force=True); pag.wait_for_timeout(2000)
        pag.locator(".crm-nav-btn[data-view=billing]").first.click(force=True)
        pag.wait_for_timeout(4000)

        vista = pag.locator("#v-billing")
        texto = " ".join(vista.inner_text().split())

        print("=== formas de cancelar solo ===")
        for prohibido in ["Gestionar suscripción", "portal de Stripe", "Cancelar suscripción"]:
            hay = prohibido.lower() in texto.lower()
            print(f"  '{prohibido}': {'SIGUE AHI' if hay else 'no está'}")
            if hay:
                fallos.append(f"la pantalla sigue ofreciendo '{prohibido}'")

        enlaces = [a.get_attribute("href") or "" for a in vista.locator("a").all()]
        # Solo el texto que VE el dueno: el id "tarjeta-cancelar" es el
        # "Ahora no" que cierra el formulario de la tarjeta, y no cancela nada.
        botones = [(b.inner_text() or "") for b in vista.locator("button").all()]
        aStripe = [h for h in enlaces if "stripe.com" in h]
        print("  enlaces a stripe.com:", aStripe or "ninguno")
        if aStripe:
            fallos.append("queda un enlace a stripe.com: %s" % aStripe)
        cancelar = [b for b in botones if "cancel" in b.lower()]
        print("  botones que dicen cancelar:", cancelar or "ninguno")
        if cancelar:
            fallos.append("queda un boton de cancelar: %s" % cancelar)

        print("\n=== el camino a soporte ===")
        caja = pag.locator(".baja-caja")
        if not caja.count():
            fallos.append("no esta el bloque '¿Quieres cancelar?'")
            print("  NO ESTA")
        else:
            t = " ".join(caja.inner_text().split())
            enlace = caja.locator("a").first.get_attribute("href") or ""
            print("  dice:", t[:170])
            print("  lleva a:", enlace)
            if SOPORTE not in enlace:
                fallos.append("el boton no lleva al bot de soporte: %s" % enlace)
            for debe in ["soporte", "sin vueltas"]:
                if debe not in t.lower():
                    fallos.append('el texto no dice "%s"' % debe)
            for prohibido in ["no puedes", "no se puede", "imposible", "permanencia mínima"]:
                if prohibido in t.lower():
                    fallos.append('el texto suena a que se le pone dificil irse: "%s"' % prohibido)

        vista.screenshot(path="/tmp/baja.png")
        print("\ncaptura: /tmp/baja.png")
        pag.close(); nav.close()
finally:
    shutil.copy2(COPIA, CFG)

igual = hashlib.md5(CFG.read_bytes()).hexdigest() == md5
print("\nConfig restaurado identico:", igual)
print("fallos:", fallos or "ninguno")
sys.exit(0 if (igual and not fallos) else 1)
