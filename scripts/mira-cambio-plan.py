#!/usr/bin/env python3
"""Mira con los ojos el cambio de plan.

Se forzan dos situaciones en un cliente de demo y se comprueba en pantalla lo
unico que no puede fallar: que NO se puede confirmar una subida cuando no
sabemos el importe, y que bajar dice claramente que hoy no se cobra nada.

El config se deja EXACTAMENTE como estaba (md5 al final).
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
COPIA = Path("/tmp/config-antes-de-plan.json")
BASE = "http://localhost:4399"

shutil.copy2(CFG, COPIA)
md5 = hashlib.md5(CFG.read_bytes()).hexdigest()
original = json.loads(CFG.read_text(encoding="utf-8"))
TOKEN = original["accessToken"]

ahora = datetime.now(timezone.utc)
comun = {
    "stripeCustomerId": "cus_de_mentira",
    "stripeSubscriptionId": "sub_de_mentira",
    "suscripcionEstado": "active",
    "cancelaAlFinal": False,
    "cambioProgramado": None,
    "renuevaEl": (ahora + timedelta(days=23)).isoformat().replace("+00:00", "Z"),
    "renovacionComprobadaEn": ahora.isoformat().replace("+00:00", "Z"),
    "tarjetaResumen": {"marca": "visa", "ultimos4": "4242", "caduca": "07/2029"},
}

fallos = []


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


def escribe(plan):
    c = dict(original); c.update(comun); c["plan"] = plan
    CFG.write_text(json.dumps(c, indent=2, ensure_ascii=False), encoding="utf-8")


try:
    with sync_playwright() as p:
        nav = p.chromium.launch()

        # ── Subida sin poder calcular el importe ──────────────────────────
        escribe("recepcionista")
        pag = nav.new_page(viewport={"width": 1180, "height": 950})
        abre(pag)
        boton = pag.locator(".bpc-cambiar[data-plan=equipo]")
        print("\n=== quiere SUBIR a 79, pero no sabemos el importe ===")
        print("boton visible:", boton.is_visible())
        boton.click(force=True)
        pag.wait_for_timeout(900)
        tit = pag.inner_text("#plan-confirma-tit")
        det = pag.inner_text("#plan-confirma-det")
        si = pag.locator("#plan-confirma-si")
        print("titulo:", tit)
        print("detalle:", det)
        print("confirmar apagado:", si.is_disabled())
        if not si.is_disabled():
            fallos.append("deja confirmar una subida sin saber el importe")
        if "orden" in tit.lower() or "38" in det:
            fallos.append("se inventa un importe")
        pag.screenshot(path="/tmp/plan-sin-importe.png", clip={"x": 0, "y": 0, "width": 1180, "height": 950})
        pag.close()

        # ── Bajada: hoy no se cobra nada ──────────────────────────────────
        escribe("equipo")
        pag = nav.new_page(viewport={"width": 1180, "height": 950})
        abre(pag)
        print("\n=== quiere BAJAR a 29 ===")
        pag.locator(".bpc-cambiar[data-plan=recepcionista]").click(force=True)
        pag.wait_for_timeout(900)
        det = pag.inner_text("#plan-confirma-det")
        si = pag.locator("#plan-confirma-si")
        print("titulo:", pag.inner_text("#plan-confirma-tit"))
        print("detalle:", det)
        print("texto del boton:", si.inner_text(), "| apagado:", si.is_disabled())
        if si.is_disabled():
            fallos.append("no deja programar una bajada, que no necesita importe")
        if "no se te cobra nada" not in det.lower():
            fallos.append("no dice que hoy no se cobra nada")

        # Confirmar de verdad: la suscripcion es de mentira, asi que Stripe
        # dira que no existe. Lo que se comprueba es que el fallo se le cuenta
        # bien al dueno y que se le dice que NO se le ha cobrado.
        si.click(force=True)
        pag.wait_for_timeout(6000)
        aviso = pag.inner_text("#plan-aviso")
        print("\n=== confirma y Stripe no puede hacerlo ===")
        print("aviso:", aviso)
        if "no se te ha cobrado nada" not in aviso.lower():
            fallos.append("al fallar no le dice que no se le ha cobrado")
        if not si.is_enabled():
            fallos.append("el boton se queda apagado para siempre tras un fallo")
        pag.screenshot(path="/tmp/plan-fallo.png", clip={"x": 0, "y": 0, "width": 1180, "height": 950})
        pag.close()
        nav.close()
finally:
    shutil.copy2(COPIA, CFG)

igual = hashlib.md5(CFG.read_bytes()).hexdigest() == md5
print("\nConfig restaurado identico:", igual)
print("fallos:", fallos or "ninguno")
sys.exit(0 if (igual and not fallos) else 1)
