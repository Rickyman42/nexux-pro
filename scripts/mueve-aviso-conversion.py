#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""El aviso de compra que recibe OpenAI sale del clic; tiene que salir de la pasarela.

Medido el 16-sep en Umami: 18 avisos de 'checkout_started' repartidos en 11
visitas (una de ellas lo mando 7 veces), y 4 de los 8 supuestos pagos se
pulsaron en menos de 10 segundos sin bajar ni un cuarto de la pagina. La
campana de OpenAI optimiza hacia ese evento: si el evento es un toque, la
campana aprende a comprar gente que toca.

Dos cambios, los dos dentro del trozo que habla con OpenAI:
  1. El aviso sale de 'checkout_form_shown' (la pasarela de Stripe ya montada)
     en vez de 'checkout_started' (el clic).
  2. Una conversion por visita: cerrar y reabrir la pasarela no cuenta dos veces.

Lo que NO se toca: Umami y Plausible siguen guardando TODOS los eventos igual
que hasta ahora, y Google/Meta siguen como estaban. No se pierde ni un dato.
"""
import io

P = 'src/scripts/measurement.ts'
s = io.open(P, encoding='utf-8').read()

# ── 1. La llave de "ya se ha contado esta visita" ─────────────────────────
ANCLA_LLAVE = "const LAST_CHECKOUT_RETURN_KEY = 'nx_last_checkout_return';\n"
NUEVA_LLAVE = (ANCLA_LLAVE +
               "// Una sola conversion por visita hacia OpenAI: si alguien cierra la pasarela\n"
               "// y la vuelve a abrir, sigue siendo la misma persona comprando una vez.\n"
               "const OPENAI_CONVERSION_KEY = 'nx_openai_conversion_sent';\n")
assert s.count(ANCLA_LLAVE) == 1, 'no encuentro donde declarar la llave'
s = s.replace(ANCLA_LLAVE, NUEVA_LLAVE, 1)

# ── 2. El aviso sale de la pasarela, no del clic ──────────────────────────
ANCLA_MAPA = """  if (eventName === 'checkout_started') {
    return {
      name: 'checkout_started',"""

NUEVO_MAPA = """  // OJO al nombre: lo que se manda a OpenAI se sigue llamando 'checkout_started'
  // porque ese evento esta bloqueado en la campana y no se puede cambiar. Lo que
  // cambia es CUANDO sale: antes salia al pulsar el boton, ahora sale cuando la
  // pasarela de Stripe ya esta montada en la pantalla. Pulsar no es comprar.
  if (eventName === 'checkout_form_shown') {
    return {
      name: 'checkout_started',"""

assert s.count(ANCLA_MAPA) == 1, 'no encuentro el mapeo de checkout_started'
s = s.replace(ANCLA_MAPA, NUEVO_MAPA, 1)

# ── 3. Una conversion por visita ──────────────────────────────────────────
ANCLA_ENVIO = """  const event = openAiEvent(eventName, properties);
  if (!event) return;
  nxWindow.oaiq('measure', event.name, event.data, {"""

NUEVO_ENVIO = """  const event = openAiEvent(eventName, properties);
  if (!event) return;

  if (event.name === 'checkout_started') {
    if (safeSessionGet(OPENAI_CONVERSION_KEY)) return;
    safeSessionSet(OPENAI_CONVERSION_KEY, '1');
  }

  nxWindow.oaiq('measure', event.name, event.data, {"""

assert s.count(ANCLA_ENVIO) == 1, 'no encuentro el envio a oaiq'
s = s.replace(ANCLA_ENVIO, NUEVO_ENVIO, 1)

io.open(P, 'w', encoding='utf-8').write(s)
print('measurement.ts: el aviso de compra ya sale de la pasarela, no del clic')
