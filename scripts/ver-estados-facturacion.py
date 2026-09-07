#!/usr/bin/env python3
"""Mira con los ojos, no con el codigo, los dos estados que mas importan:
el cliente que paga y va bien, y el que tiene un cobro fallido.

Toca a proposito el config de un cliente de demo para forzar cada situacion, y
lo deja EXACTAMENTE como estaba (se comprueba por md5 al final).
"""
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

CLIENTE = "estudio-ricardo-demo-mostoles-946279"
CFG = Path("/home/nexux/nexux-clients/clients") / CLIENTE / "config.json"
COPIA = Path("/tmp/config-antes-de-mirar.json")

shutil.copy2(CFG, COPIA)
md5 = hashlib.md5(CFG.read_bytes()).hexdigest()
original = json.loads(CFG.read_text(encoding="utf-8"))
TOKEN = original["accessToken"]

dentro_de = lambda d: (datetime.now(timezone.utc) + timedelta(days=d)).isoformat().replace("+00:00", "Z")
ahora = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

ESCENAS = [
    ("paga-y-va-bien", {
        "stripeCustomerId": "cus_demo_mirada",
        "stripeSubscriptionId": "sub_demo_mirada",
        "suscripcionEstado": "active",
        "cancelaAlFinal": False,
        "renuevaEl": dentro_de(23),
        "renovacionComprobadaEn": ahora,
        "tarjetaResumen": {"marca": "visa", "ultimos4": "4242", "caduca": "07/2029"},
    }),
    ("cobro-fallido", {
        "stripeCustomerId": "cus_demo_mirada",
        "stripeSubscriptionId": "sub_demo_mirada",
        "suscripcionEstado": "past_due",
        "cancelaAlFinal": False,
        "renuevaEl": dentro_de(4),
        "renovacionComprobadaEn": ahora,
        "tarjetaResumen": {"marca": "visa", "ultimos4": "4242", "caduca": "07/2029"},
    }),
    ("cancelado-con-servicio-hasta", {
        "stripeCustomerId": "cus_demo_mirada",
        "stripeSubscriptionId": "sub_demo_mirada",
        "suscripcionEstado": "active",
        "cancelaAlFinal": True,
        "renuevaEl": dentro_de(11),
        "renovacionComprobadaEn": ahora,
        "tarjetaResumen": {"marca": "mastercard", "ultimos4": "5556", "caduca": "01/2028"},
    }),
]

try:
    for nombre, campos in ESCENAS:
        c = dict(original)
        c.update(campos)
        CFG.write_text(json.dumps(c, indent=2, ensure_ascii=False), encoding="utf-8")
        print("\n===== %s =====" % nombre)
        r = subprocess.run(
            ["python3", "/home/nexux/nexux-pro/scripts/mira-panel-facturacion.py", CLIENTE, TOKEN, "/tmp/panel-%s.png" % nombre],
            capture_output=True, text=True, timeout=180)
        print(r.stdout.strip() or r.stderr.strip()[-600:])
finally:
    shutil.copy2(COPIA, CFG)

igual = hashlib.md5(CFG.read_bytes()).hexdigest() == md5
print("\nConfig restaurado identico:", igual)
sys.exit(0 if igual else 1)
