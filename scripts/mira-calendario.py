#!/usr/bin/env python3
"""Se pueden mover y editar las citas en el calendario del plan de 79?

Ricardo dice que no. Esto lo mira en un navegador de verdad, sobre el mismo
cliente de la captura, y retrocede semanas hasta encontrar una con citas
(las de demo son de agosto; la semana actual esta vacia y no prueba nada).

Se comprueba, en este orden:
  1. que las citas se pintan;
  2. que cada una lleva sus botones de editar y cancelar;
  3. que esos botones se VEN y son pulsables (que esten en el HTML no basta);
  4. que al pulsar editar se abre el formulario;
  5. que la cita se puede arrastrar y de verdad cambia de hora.
"""
import sys
from playwright.sync_api import sync_playwright

CLIENTE = "estudio-ricardo-demo-mostoles-946279"
TOKEN = sys.argv[1]
BASE = "http://localhost:4399"
fallos = []

with sync_playwright() as p:
    nav = p.chromium.launch()
    pag = nav.new_page(viewport={"width": 1400, "height": 950})
    errores = []
    pag.on("pageerror", lambda e: errores.append("pagina:" + str(e)))
    pag.on("console", lambda m: errores.append("console:" + m.text) if m.type == "error" else None)
    # El confirm() del navegador: se acepta, que es lo que haria Ricardo.
    preguntas = []
    def _dialogo(d):
        preguntas.append(d.message)
        d.accept()
    pag.on("dialog", _dialogo)

    llamadas = []
    def _peticion(req):
        if "/portal-api/appointments" in req.url and req.method != "GET":
            llamadas.append(req.method + " " + req.url + " " + (req.post_data or "")[:200])
    pag.on("request", _peticion)
    respuestas = []
    def _respuesta(res):
        if "/portal-api/appointments" in res.url and res.request.method != "GET":
            respuestas.append(str(res.status) + " " + res.url)
    pag.on("response", _respuesta)

    pag.goto(f"{BASE}/cliente/{CLIENTE}?t={TOKEN}", wait_until="networkidle")
    ck = pag.get_by_text("Sólo necesarias")
    if ck.count():
        ck.first.click(force=True); pag.wait_for_timeout(500)
    ir = pag.get_by_text("Ya lo tengo configurado, ir al panel")
    if ir.count():
        ir.first.click(force=True); pag.wait_for_timeout(2000)
    pag.locator(".crm-nav-btn[data-view=citas]").first.click(force=True)
    pag.wait_for_timeout(3000)

    # Se busca la semana que se parece a la captura de Ricardo: varias citas a la
    # misma hora, apretadas. Una semana con dos citas sueltas no prueba nada.
    citas = pag.locator(".crm-tac-apt")
    saltos = 0
    while pag.locator(".crm-tac-apt.compartido").count() == 0 and saltos < 6:
        pag.locator("#cal-prev").click()
        pag.wait_for_timeout(1500)
        saltos += 1
    print("semanas hacia atras:", saltos)
    print("semana:", (pag.locator("#cal-week-label").inner_text() or "?").strip())

    n = citas.count()
    print("citas pintadas:", n)
    if n == 0:
        fallos.append("no se pinta ninguna cita en 5 semanas hacia atras")
    else:
        compartidas = pag.locator(".crm-tac-apt.compartido").count()
        print("de esas, apretadas por solaparse:", compartidas)

        # Se elige una apretada si la hay: es el caso de la captura de Ricardo.
        primera = pag.locator(".crm-tac-apt.compartido").first if compartidas else citas.first
        caja = primera.bounding_box()
        print("tamano de la elegida: %.0fx%.0f" % (caja["width"], caja["height"]) if caja else "sin caja")

        editar = primera.locator(".crm-cal-apt-edit")
        print("boton editar en el HTML:", editar.count())
        if editar.count() == 0:
            fallos.append("las citas no llevan boton de editar")
        else:
            primera.hover()
            pag.wait_for_timeout(500)
            visible = editar.first.is_visible()
            be = editar.first.bounding_box()
            print("editar visible al pasar por encima:", visible,
                  "| tamano: %.1fx%.1f" % (be["width"], be["height"]) if be else "| sin caja")
            if not visible:
                fallos.append("el boton de editar no se ve ni pasando el raton por encima")
            elif be and (be["width"] < 10 or be["height"] < 10):
                fallos.append("el boton de editar mide %.1fx%.1f px: no se puede acertar" % (be["width"], be["height"]))

            try:
                editar.first.click(timeout=4000)
                pag.wait_for_timeout(1200)
                abierto = pag.locator("dialog[open]").count()
                print("se abre el formulario al pulsar editar:", abierto > 0)
                if abierto == 0:
                    fallos.append("pulsar editar no abre el formulario")
                else:
                    pag.keyboard.press("Escape"); pag.wait_for_timeout(600)
            except Exception as e:
                fallos.append("no se puede pulsar editar: " + str(e).split("\n")[0][:100])

        # 5: arrastrar de verdad y comprobar que la HORA cambia
        pag.wait_for_timeout(500)
        obj = pag.locator(".crm-tac-apt.compartido").first if compartidas else pag.locator(".crm-tac-apt").first
        hora_antes = obj.locator(".crm-tac-apt-main strong").inner_text()
        antes_misma = pag.locator(".crm-tac-apt-main strong").all_inner_texts().count(hora_antes)
        antes = obj.bounding_box()
        print("hora antes de arrastrar:", hora_antes)
        if antes:
            pag.mouse.move(antes["x"] + antes["width"] / 2, antes["y"] + antes["height"] / 2)
            pag.mouse.down()
            # Hacia ARRIBA: hacia abajo puede toparse con el cierre del negocio y
            # quedarse quieta por el tope, que no es el fallo que se busca.
            pag.mouse.move(antes["x"] + antes["width"] / 2, antes["y"] + antes["height"] / 2 - 30, steps=6)
            pag.mouse.move(antes["x"] + antes["width"] / 2, antes["y"] + antes["height"] / 2 - 110, steps=12)
            pag.wait_for_timeout(400)
            arrastrando = pag.locator(".crm-tac-apt.dragging").count()
            print("el navegador reconoce el arrastre:", arrastrando > 0)
            if arrastrando == 0:
                fallos.append("al arrastrar no pasa nada: la cita ni se despega")
            pag.mouse.up()
            pag.wait_for_timeout(900)
            aviso = pag.locator(".crm-toast-show")
            texto_aviso = aviso.first.inner_text().strip() if aviso.count() else ""
            print("aviso que ve el negocio:", texto_aviso or "NINGUNO")
            if not texto_aviso:
                fallos.append("al soltar no aparece ningun aviso: no se sabe si se guardo")
            pag.wait_for_timeout(2600)
            horas = pag.locator(".crm-tac-apt-main strong").all_inner_texts()
            print("cuantas a las %s antes: %d | despues: %d" % (hora_antes, antes_misma, horas.count(hora_antes)))
            if horas.count(hora_antes) >= antes_misma:
                fallos.append("se arrastra pero la cita no cambia de hora: vuelve a su sitio")
        else:
            fallos.append("la cita no tiene caja: no se puede ni agarrar")

    print("")
    print("preguntas del navegador:", preguntas or "ninguna")
    print("peticiones de guardado:", llamadas or "ninguna")
    print("respuestas:", respuestas or "ninguna")

    if errores:
        print("\nERRORES DE JAVASCRIPT:")
        vistos = set()
        for e in errores:
            if "stats/script.js" in e or "Failed to load resource" in e:
                continue  # el proxy de analitica solo existe en Vercel: ruido del servidor de pruebas
            if e in vistos:
                continue
            vistos.add(e)
            print("   " + e[:170])
            fallos.append("javascript roto: " + e[:80])

    pag.screenshot(path="/tmp/calendario.png", full_page=False)
    print("\ncaptura: /tmp/calendario.png")
    pag.close(); nav.close()

print("\nfallos:", fallos or "ninguno")
sys.exit(1 if fallos else 0)
