#!/usr/bin/env python3
"""Comprobar que el vigilante de estilos del portal muerde.

Se devuelven las reglas al bloque equivocado --que es justo lo que paso de
verdad-- y se exige que el test lo cace. Si pasara en verde, el test no serviria
para nada y el proximo rediseño volveria a subirse invisible.

  python3 scripts/sabotaje-estilos-portal.py
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PORTAL = RAIZ / "src" / "pages" / "cliente" / "[id].astro"
PRUEBA = "test/estilos-del-portal.test.mjs"

SABOTAJES = [
    ("devolver las tarjetas de Clientes al <style> que no las alcanza", ".cli-"),
    ("devolver los botones de borrar al bloque equivocado", ".crm-btn-del"),
]


def mueve_al_scoped(texto, prefijo):
    """Devuelve TODAS las reglas de ese prefijo al bloque que no las alcanza.

    Una a una no vale: si queda alguna en el bloque bueno, el vigilante ve la
    clase ahi y se calla. La regresion de verdad se llevo el bloque entero.
    """
    i_global = texto.index("<style is:global>")
    fin_global = texto.index("</style>", i_global)
    global_css = texto[i_global:fin_global]

    movidas, resto, pos = [], [], 0
    while True:
        j = global_css.find(prefijo, pos)
        if j == -1:
            resto.append(global_css[pos:])
            break
        # Hasta el principio de la regla (el selector puede empezar antes).
        ini = global_css.rfind("\n", 0, j) + 1
        fin = global_css.find("}", j) + 1
        if fin <= 0:
            resto.append(global_css[pos:])
            break
        resto.append(global_css[pos:ini])
        movidas.append(global_css[ini:fin].strip())
        pos = fin

    if not movidas:
        raise ValueError(prefijo)

    nuevo_global = "".join(resto)
    texto = texto[:i_global] + nuevo_global + texto[fin_global:]

    i_scoped = texto.index("  <style>")
    corte = texto.index("\n", i_scoped) + 1
    inyectado = "".join("    " + m + "\n" for m in movidas)
    return texto[:corte] + inyectado + texto[corte:]


def main():
    copia = Path(tempfile.mkdtemp(prefix="sabotaje-estilos-")) / "portal.astro"
    shutil.copy2(PORTAL, copia)
    original = PORTAL.read_text(encoding="utf-8")
    fallos = []
    try:
        print("Comprobando que el vigilante de estilos muerde.\n")
        for titulo, ancla in SABOTAJES:
            try:
                PORTAL.write_text(mueve_al_scoped(original, ancla), encoding="utf-8")
            except ValueError:
                fallos.append("%s: no encuentro %s" % (titulo, ancla))
                print("  ??  %s\n      no he sabido romperlo" % titulo)
                continue
            r = subprocess.run(["node", "--test", PRUEBA], cwd=RAIZ,
                               capture_output=True, text=True, timeout=120)
            PORTAL.write_text(original, encoding="utf-8")
            if r.returncode == 0:
                fallos.append("%s: %s sigue en verde" % (titulo, PRUEBA))
                print("  NO  %s\n      %s pasa igualmente" % (titulo, PRUEBA))
            else:
                print("  OK  %s\n      lo caza %s" % (titulo, PRUEBA))
    finally:
        shutil.copy2(copia, PORTAL)
        print("\nFichero restaurado.")

    if fallos:
        print("\n%d sabotaje(s) sin cazar:" % len(fallos))
        for f in fallos:
            print("  - " + f)
        return 1
    print("\nLos %d sabotajes se cazan." % len(SABOTAJES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
