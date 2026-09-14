#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprueba que los tests cazan cada forma de devolver la ruedecita eterna.

El fallo que se arregla aqui es mudo: no da error, no sale en ningun registro y
la pagina se ve perfecta. Solo se nota mirando cuanta gente paga. Por eso hace
falta comprobar que los tests se ponen rojos de verdad.
"""
import hashlib
import io
import subprocess
import sys

CH = 'src/scripts/checkout.ts'
ES = 'src/scripts/espera-limitada.mjs'
T = 'test/pantalla-de-pago-atascada.test.mjs'

ORIG = {p: io.open(p, encoding='utf-8').read() for p in (CH, ES)}
FIRMA = {p: hashlib.md5(io.open(p, 'rb').read()).hexdigest() for p in ORIG}


def corre():
    r = subprocess.run(['node', '--test', T], capture_output=True, text=True, timeout=600)
    fallos = [l for l in r.stdout.splitlines() if l.startswith('# fail')]
    rojos = [l.split('- ', 1)[1] for l in r.stdout.splitlines() if l.startswith('not ok')]
    # Si la tanda se cuelga y Node la cancela, el resumen '# fail' no llega a
    # salir: entonces cuentan los 'not ok'. Antes se devolvia -1 y un sabotaje
    # cazado se leia como 'no rompe nada'.
    if fallos:
        return int(fallos[0].split()[-1]), rojos
    return len(rojos), rojos


SABOTAJES = [
    (CH, 'vuelve el await sin limite: ruedecita para siempre',
     """    const instancia = await conLimite(
      stripe.initEmbeddedCheckout({ clientSecret }),
      ESPERA_MAXIMA_MS,
      tirar,
    );""",
     """    const instancia = await stripe.initEmbeddedCheckout({ clientSecret });"""),

    (ES, 'la espera se agota pero no avisa a nadie (falla en silencio)',
     "      rechazar(new Error('tardo_demasiado'));",
     "      resolver(undefined);"),

    (ES, 'lo que llega tarde ya no se cierra: pantalla fantasma',
     '        if (seDioPorPerdida) alLlegarTarde(valor);\n        else resolver(valor);',
     '        if (!seDioPorPerdida) resolver(valor);'),

    (ES, 'un error de verdad se disfraza de espera agotada',
     '        if (!seDioPorPerdida) rechazar(error);',
     "        if (!seDioPorPerdida) rechazar(new Error('tardo_demasiado'));"),

    (CH, 'se deja de mandar la senal de que el formulario salio',
     "    senal('checkout_form_shown', { plan, ms: Date.now() - arrancado });",
     "    // senal quitada"),

    (CH, 'se deja de mandar el motivo del fallo',
     """    senal('checkout_form_failed', {
      plan,
      motivo: motivoDe(error),
      ms: Date.now() - arrancado,
    });""",
     "    // senal quitada"),

    (CH, 'cerrar la ventana ya no invalida la carga en curso',
     '  intentoActual += 1;\n\n  modal.setAttribute',
     '  modal.setAttribute'),

    (CH, 'se monta igual aunque ya no haga falta (ventana cerrada)',
     """    if (yaNoImporta()) {
      tirar(instancia);
      return;
    }""",
     "    // comprobacion quitada"),

    (CH, 'un fallo midiendo tumba el pago entero',
     """  try {
    (window as any).nxMeasure?.(nombre, datos);
  } catch {
    // Si la medicion falla, el pago sigue.
  }""",
     "  (window as any).nxMeasure?.(nombre, datos);"),

    (CH, 'el boton de reintentar deja de hacer nada',
     "    void abrirPagoStripe(intento.plan, intento.salon);",
     "    // reintento quitado"),
]

print('Comprobando que los tests cazan cada forma de romper la pantalla de pago.\n')
todos = True
try:
    for fichero, nombre, viejo, nuevo in SABOTAJES:
        if ORIG[fichero].count(viejo) != 1:
            print('  %-60s -> NO SE PUDO APLICAR (%d coincidencias)'
                  % (nombre, ORIG[fichero].count(viejo)))
            todos = False
            continue
        io.open(fichero, 'w', encoding='utf-8').write(ORIG[fichero].replace(viejo, nuevo, 1))
        n, rojos = corre()
        io.open(fichero, 'w', encoding='utf-8').write(ORIG[fichero])
        ok = n > 0
        todos = todos and ok
        print('  %-60s -> %s' % (nombre, 'CAZADO' if ok else 'NO ROMPE NADA'))
        if ok:
            print('       rojo: %s' % (rojos[0][:70] if rojos else '(sin detalle)'))
finally:
    for p, texto in ORIG.items():
        io.open(p, 'w', encoding='utf-8').write(texto)

iguales = all(hashlib.md5(io.open(p, 'rb').read()).hexdigest() == FIRMA[p] for p in ORIG)
print('\nFicheros restaurados identicos:', iguales)
n, _ = corre()
print('Sin sabotaje -> fallos:', n)
sys.exit(0 if (todos and iguales and n == 0) else 1)
