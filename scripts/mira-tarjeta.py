#!/usr/bin/env python3
"""Mira con los ojos el formulario de la tarjeta.

Lo que se comprueba, que es lo que no se puede fingir:
  - sin pasarela de pago, el boton NO aparece (no hay tarjeta que cambiar);
  - con pasarela, al pulsarlo aparece un formulario servido por STRIPE, no
    nuestro: si los campos fueran nuestros, el numero de tarjeta pasaria por
    nuestro servidor, que es justo lo que no puede pasar;
  - se le dice al dueno, en llano, quien recoge la tarjeta.

Toca el config de un cliente de demo y lo deja identico (md5 al final). El
permiso que Stripe crea durante la prueba se cancela al terminar.
"""
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

CLIENTE = "estudio-ricardo-demo-mostoles-946279"
RAIZ = Path("/home/nexux/nexux-clients")
CFG = RAIZ / "clients" / CLIENTE / "config.json"
COPIA = Path("/tmp/config-antes-de-tarjeta.json")
BASE = "http://localhost:4399"
# Cliente real de Stripe: hace falta uno de verdad para que Stripe cree el
# permiso. No se escribe ninguna tarjeta; el permiso se cancela al final.
CUS = "cus_VCHnSFwP5PjSkz"

shutil.copy2(CFG, COPIA)
md5 = hashlib.md5(CFG.read_bytes()).hexdigest()
original = json.loads(CFG.read_text(encoding="utf-8"))
TOKEN = original["accessToken"]
ahora = datetime.now(timezone.utc)
fallos = []
permisos = []


def escribe(**extra):
    c = dict(original)
    c.update({
        "renuevaEl": (ahora + timedelta(days=23)).isoformat().replace("+00:00", "Z"),
        "renovacionComprobadaEn": ahora.isoformat().replace("+00:00", "Z"),
        "suscripcionEstado": "active",
        "cambioProgramado": None,
        "tarjetaResumen": {"marca": "visa", "ultimos4": "2520", "caduca": "03/2031"},
    })
    c.update(extra)
    CFG.write_text(json.dumps(c, indent=2, ensure_ascii=False), encoding="utf-8")


def abre(pag):
    pag.goto(f"{BASE}/cliente/{CLIENTE}?t={TOKEN}", wait_until="networkidle")
    ck = pag.get_by_text("Sólo necesarias")
    if ck.count():
        ck.first.click(force=True); pag.wait_for_timeout(500)
    ir = pag.get_by_text("Ya lo tengo configurado, ir al panel")
    if ir.count():
        ir.first.click(force=True); pag.wait_for_timeout(2000)
    pag.locator(".crm-nav-btn[data-view=billing]").first.click(force=True)
    pag.wait_for_timeout(3500)


try:
    with sync_playwright() as p:
        nav = p.chromium.launch()

        # ── Sin pasarela: el boton no debe estar ──────────────────────────
        escribe(stripeCustomerId=None, stripeSubscriptionId=None)
        pag = nav.new_page(viewport={"width": 1180, "height": 950})
        abre(pag)
        visible = pag.locator("#btn-tarjeta").is_visible()
        print("=== alta a mano (sin pasarela) ===")
        print("boton 'Cambiar la tarjeta' visible:", visible)
        if visible:
            fallos.append("ofrece cambiar una tarjeta que no existe")
        pag.close()

        # ── Con pasarela: el formulario tiene que ser de Stripe ───────────
        escribe(stripeCustomerId=CUS, stripeSubscriptionId=None)
        pag = nav.new_page(viewport={"width": 1180, "height": 1050})
        pag.on("request", lambda r: permisos.append(r.url) if "/portal-api/tarjeta" in r.url else None)
        abre(pag)
        print("\n=== con pasarela de pago ===")
        boton = pag.locator("#btn-tarjeta")
        print("boton visible:", boton.is_visible())
        if not boton.is_visible():
            fallos.append("no ofrece cambiar la tarjeta a quien si tiene pasarela")
        else:
            boton.click(force=True)
            pag.wait_for_timeout(7000)

            error = pag.inner_text("#tarjeta-error")
            if error:
                print("error en pantalla:", error)
                fallos.append("el formulario no se abrio: " + error)

            marcos = pag.locator("#tarjeta-elemento iframe")
            n = marcos.count()
            print("marcos dentro del formulario:", n)
            if n == 0:
                fallos.append("no se ha montado ningun formulario de Stripe")
            else:
                src = marcos.first.get_attribute("src") or ""
                print("servido por:", src.split("?")[0][:60])
                if "js.stripe.com" not in src:
                    fallos.append("el formulario NO lo sirve Stripe: la tarjeta pasaria por nosotros")

            texto = pag.inner_text("#tarjeta-caja")
            print("le dice al dueño:", " ".join(texto.split())[:150])
            for debe in ["Stripe", "no ve ni guarda"]:
                if debe not in texto:
                    fallos.append('no le explica lo de "%s"' % debe)

            # El formulario lo pinta Stripe, pero el idioma lo elegimos
            # nosotros. En ingles, en mitad de una pantalla en castellano y
            # justo al teclear una tarjeta, parece otro sitio.
            dentro = pag.frame_locator("#tarjeta-elemento iframe").first
            etiquetas = " ".join(dentro.locator("body").inner_text().split())
            print("el formulario dice:", etiquetas[:90])
            if "Card number" in etiquetas or "Expiry date" in etiquetas:
                fallos.append("el formulario de la tarjeta sale en ingles")
            if "Numero de tarjeta" not in etiquetas.replace("ú", "u"):
                fallos.append("el formulario no sale en castellano: " + etiquetas[:60])

            pag.locator("#tarjeta-caja").screenshot(path="/tmp/tarjeta.png")
            print("captura: /tmp/tarjeta.png")
        pag.close()
        nav.close()
finally:
    shutil.copy2(COPIA, CFG)
    # Los permisos que Stripe haya creado durante la prueba no se dejan sueltos.
    subprocess.run(
        ["bash", "-lc",
         'cd %s && set -a && . ./.env && set +a && '
         'for s in $(curl -s -u "$STRIPE_SECRET_KEY:" '
         '"https://api.stripe.com/v1/setup_intents?customer=%s&limit=10" '
         '| python3 -c "import json,sys;[print(x[\'id\']) for x in json.load(sys.stdin)[\'data\'] '
         'if x[\'status\']==\'requires_payment_method\']"); do '
         'curl -s -u "$STRIPE_SECRET_KEY:" -X POST '
         '"https://api.stripe.com/v1/setup_intents/$s/cancel" > /dev/null && echo "cancelado $s"; done'
         % (RAIZ, CUS)],
        check=False)

igual = hashlib.md5(CFG.read_bytes()).hexdigest() == md5
print("\nConfig restaurado identico:", igual)
print("fallos:", fallos or "ninguno")
sys.exit(0 if (igual and not fallos) else 1)
