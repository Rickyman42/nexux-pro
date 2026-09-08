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

    # El numero, no el localizador: un locator se vuelve a evaluar cada vez que
    # lo miras, asi que compararlo consigo mismo mas tarde no compara nada.
    filas_antes = pag.locator("#proximas-cuerpo tr").count()
    print("filas en 'proximas citas' al entrar:", filas_antes)
    if filas_antes:
        celdas = pag.locator("#proximas-cuerpo tr").first.locator("td").all_inner_texts()
        print("primera fila:", celdas)
        if len(celdas) > 2 and not celdas[2].strip():
            fallos.append("la columna CLIENTE sale vacia")

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
    dur = dlg.locator('input[name="duration_min"]')
    if dur.count():
        dur.fill("15")
    hoy = pag.evaluate("() => new Date().toLocaleDateString('en-CA')")
    # Tiene que ser FUTURA: "proximas citas" solo ensena lo que queda por delante,
    # asi que una cita a las 09:xx de hoy no aparece ahi por mucho que el contador
    # suba. Y con minuto distinto en cada pasada, para no chocar con la anterior.
    # Se busca un hueco de verdad. Adivinar una hora hace que la prueba choque
    # con la cita que dejo la pasada anterior y parezca que el producto falla.
    hora_libre = pag.evaluate("""async (clientId) => {
        const r = await fetch('/portal-api/appointments?clientId=' + encodeURIComponent(clientId));
        const citas = r.ok ? await r.json() : [];
        const hoy = new Date().toLocaleDateString('en-CA');
        const ocupadas = citas
          .filter(c => (c.status || 'confirmed') === 'confirmed')
          .map(c => { const d = new Date(c.datetime); return [d, new Date(d.getTime() + (c.duration_min || 60) * 60000)]; })
          .filter(([a]) => a.toLocaleDateString('en-CA') === hoy);
        const ahora = Date.now();
        for (let m = 9 * 60; m < 19 * 60; m += 15) {
          const ini = new Date(); ini.setHours(Math.floor(m / 60), m % 60, 0, 0);
          const fin = new Date(ini.getTime() + 15 * 60000);
          if (ini.getTime() <= ahora) continue;                 // tiene que ser futura
          if (ocupadas.some(([a, b]) => ini < b && a < fin)) continue;
          return String(ini.getHours()).padStart(2, '0') + ':' + String(ini.getMinutes()).padStart(2, '0');
        }
        return null;
    }""", CLIENTE)
    if not hora_libre:
        print("no queda ningun hueco libre hoy: la comprobacion no puede seguir")
        fallos.append("sin hueco libre para probar")
        print("fallos:", fallos); sys.exit(1)
    print("hueco libre encontrado:", hora_libre)
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

    filas_despues = pag.locator("#proximas-cuerpo tr").count()
    print("filas en 'proximas citas' tras crear:", filas_despues)
    nombres = pag.locator("#proximas-cuerpo tr td:nth-child(3)").all_inner_texts()
    print("nombres que se ven:", nombres)
    if filas_despues <= filas_antes:
        fallos.append("la tabla de proximas citas no se ha actualizado")
    if any(not n.strip() for n in nombres):
        fallos.append("hay filas con el cliente en blanco")

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
