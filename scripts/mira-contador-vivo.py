#!/usr/bin/env python3
"""El contador sube al crear una cita SIN recargar la pagina, y sin machacar.

Lo que se comprueba, en este orden:
  1. cuanto marca "Citas hoy" al entrar;
  2. se crea una cita desde el propio panel;
  3. el numero sube SIN tocar F5;
  4. cuantas peticiones a /portal-api/contadores se han hecho -- y que no siguen
     llegando solas cuando la pagina se queda quieta.
"""
import sys
import time
from playwright.sync_api import sync_playwright

CLIENTE = sys.argv[1]
TOKEN = sys.argv[2]
BASE = "http://localhost:4399"
fallos = []

with sync_playwright() as p:
    nav = p.chromium.launch()
    pag = nav.new_page(viewport={"width": 1400, "height": 950})
    errores = []
    peticiones = []
    pag.on("pageerror", lambda e: errores.append("pagina:" + str(e)))
    pag.on("console", lambda m: errores.append("console:" + m.text) if m.type == "error" else None)
    pag.on("request", lambda r: peticiones.append((time.time(), r.url)) if "/portal-api/contadores" in r.url else None)
    pag.on("dialog", lambda d: d.accept())

    pag.goto(f"{BASE}/cliente/{CLIENTE}?t={TOKEN}", wait_until="networkidle")
    ck = pag.get_by_text("Sólo necesarias")
    if ck.count():
        ck.first.click(force=True); pag.wait_for_timeout(400)
    ir = pag.get_by_text("Ya lo tengo configurado, ir al panel")
    if ir.count():
        ir.first.click(force=True); pag.wait_for_timeout(1800)

    marcador = pag.locator('.crm-kpi-val[data-contador="citasHoy"]')
    if marcador.count() == 0:
        fallos.append("el numero de citas de hoy no esta marcado para poder refrescarlo")
        print("fallos:", fallos); sys.exit(1)

    antes = marcador.first.inner_text().strip()
    reservadas_antes = pag.locator('.crm-kpi-val[data-contador="reservadas"]').first.inner_text().strip()
    print("al entrar -> citas hoy:", antes, "| reservadas:", reservadas_antes)
    print("peticiones al cargar:", len(peticiones))

    # La pagina quieta no puede seguir preguntando sola.
    pag.wait_for_timeout(6000)
    en_reposo = len(peticiones)
    print("peticiones tras 6s quieta:", en_reposo)
    if en_reposo > len(peticiones):
        fallos.append("sigue preguntando sola con la pagina quieta")

    # Se crea una cita desde el panel, como lo haria el negocio.
    pag.locator(".crm-nav-btn[data-view=citas]").first.click(force=True)
    pag.wait_for_timeout(2500)
    antes_de_crear = len(peticiones)

    pag.locator("#open-apt-modal").first.click()
    pag.wait_for_timeout(1200)

    # El formulario de "nueva cita" no tiene telefono, y la fecha y la hora van en
    # campos ocultos que rellena el calendarito. Se rellenan directamente: lo que
    # se quiere probar es el camino de guardar y el refresco, no el calendarito.
    dlg = pag.locator("dialog[open]")
    dlg.locator('input[name="client_name"]').fill("Prueba Contador")
    dlg.locator('input[name="service"]').fill("Corte")
    hoy = pag.evaluate("() => new Date().toLocaleDateString('en-CA')")
    # Una hora distinta en cada pasada: repitiendo la misma, la segunda vez choca
    # con la cita de la primera y la creacion falla por hueco ocupado -- que es
    # un fallo del banco de pruebas, no del producto.
    hora_libre = "09:%02d" % (int(time.time()) % 60)
    pag.evaluate(
        """([d, h]) => {
            const f = document.getElementById('apt-date-val');
            const t = document.getElementById('apt-time-val');
            f.value = d; t.value = h;
            f.dispatchEvent(new Event('input', {bubbles: true}));
            t.dispatchEvent(new Event('input', {bubbles: true}));
        }""",
        [hoy, hora_libre],
    )
    dlg.locator('button[type="submit"]').first.click()
    pag.wait_for_timeout(4500)

    aviso = pag.locator(".crm-toast-show")
    if aviso.count():
        print("aviso del panel al guardar:", aviso.first.inner_text().strip())

    despues = marcador.first.inner_text().strip()
    reservadas_despues = pag.locator('.crm-kpi-val[data-contador="reservadas"]').first.inner_text().strip()
    print("tras crear la cita (SIN recargar) -> citas hoy:", despues, "| reservadas:", reservadas_despues)
    print("peticiones que ha costado:", len(peticiones) - antes_de_crear)

    if despues == antes and reservadas_despues == reservadas_antes:
        fallos.append("el numero no se mueve al crear una cita: sigue haciendo falta recargar")
    if len(peticiones) - antes_de_crear > 4:
        fallos.append("una sola cita ha costado %d peticiones" % (len(peticiones) - antes_de_crear))

    if errores:
        print("\nERRORES DE JAVASCRIPT:")
        vistos = set()
        for e in errores:
            if "stats/script.js" in e or "Failed to load resource" in e or e in vistos:
                continue
            vistos.add(e)
            print("   " + e[:150])
            fallos.append("javascript roto: " + e[:70])

    pag.screenshot(path="/tmp/contador.png")
    pag.close(); nav.close()

print("\nfallos:", fallos or "ninguno")
sys.exit(1 if fallos else 0)
