// Lo que se le pide a Stripe al abrir la pantalla de pago.
//
// El 14-sep-2026 se quito el formulario que preguntaba el nombre del negocio
// ANTES de pagar: de 7 personas que pulsaron comprar, solo 2 llegaban al pago.
// Ahora se pregunta DENTRO de la pantalla de Stripe, como un campo mas.
//
// El fallo que esto vigila es el peor de todos y es mudo: si el campo dejara de
// anadirse, Stripe no preguntaria nada, nadie tendria nombre de negocio y el
// alta (api/webhook/stripe.js, que lo EXIGE) rechazaria a TODO el mundo. Todos
// pagando y nadie recibiendo su cuenta, sin un solo error a la vista.
//
// No se llama a Stripe: se intercepta la peticion y se mira lo que iba a mandar.
import { test } from 'node:test';
import assert from 'node:assert/strict';

const { default: crearSesion } = await import('../api/stripe/create-session.js');

function respuestaFalsa() {
  const r = {
    codigo: 200, cuerpo: null, cabeceras: {},
    setHeader(k, v) { r.cabeceras[k] = v; },
    status(c) { r.codigo = c; return r; },
    json(x) { r.cuerpo = x; return r; },
    end() { return r; },
  };
  return r;
}

/** Llama al endpoint y devuelve lo que se le iba a mandar a Stripe. */
async function loQueSeLePideAStripe(cuerpo) {
  const fetchOriginal = globalThis.fetch;
  let enviado = null;
  globalThis.fetch = async (url, opciones) => {
    enviado = { url: String(url), params: new URLSearchParams(opciones.body) };
    return { ok: true, json: async () => ({ client_secret: 'cs_test_secreto' }) };
  };
  const res = respuestaFalsa();
  try {
    await crearSesion({ method: 'POST', headers: {}, body: cuerpo }, res);
  } finally {
    globalThis.fetch = fetchOriginal;
  }
  return { enviado, res };
}

test('🔴 si no sabemos el negocio, se pregunta DENTRO de la pantalla de pago', async () => {
  const { enviado, res } = await loQueSeLePideAStripe({ plan: 'recepcionista' });

  assert.ok(enviado, 'no se ha llamado a Stripe');
  assert.equal(enviado.params.get('custom_fields[0][key]'), 'salon',
    'sin este campo Stripe no pregunta el nombre y NADIE se puede dar de alta');
  assert.equal(enviado.params.get('custom_fields[0][type]'), 'text');
  assert.ok((enviado.params.get('custom_fields[0][label][custom]') || '').length > 0,
    'el campo sale sin etiqueta y el cliente no sabe que escribir');
  assert.equal(res.codigo, 200);
  assert.equal(res.cuerpo.clientSecret, 'cs_test_secreto');
});

test('si Lara ya sabe el nombre, no se vuelve a preguntar', async () => {
  const { enviado } = await loQueSeLePideAStripe({ plan: 'recepcionista', salon: 'Peluqueria Lena' });

  assert.equal(enviado.params.get('custom_fields[0][key]'), null,
    'se le esta preguntando algo que ya nos habia dicho');
  assert.equal(enviado.params.get('metadata[salon]'), 'Peluqueria Lena',
    'el nombre que ya sabiamos no viaja con la compra');
});

test('un nombre en blanco cuenta como no saberlo', async () => {
  const { enviado } = await loQueSeLePideAStripe({ plan: 'recepcionista', salon: '   ' });

  assert.equal(enviado.params.get('custom_fields[0][key]'), 'salon',
    'con un nombre vacio nadie preguntaria nada y el alta fallaria');
});

test('el pago sigue siendo el de siempre: 29 EUR al mes, suscripcion', async () => {
  // Regresion: al tocar esto es facil llevarse por delante el precio.
  const { enviado } = await loQueSeLePideAStripe({ plan: 'recepcionista' });

  assert.equal(enviado.params.get('mode'), 'subscription');
  assert.equal(enviado.params.get('line_items[0][price]'), 'price_1U6jqd2SQwDzHtsFf3wEcuQe');
  assert.equal(enviado.params.get('ui_mode'), 'embedded_page',
    'la tarjeta tiene que seguir dentro de nuestra pagina, no en una de Stripe');
  assert.equal(enviado.params.get('phone_number_collection[enabled]'), 'true',
    'sin telefono el asistente no puede arrancar el alta');
});

test('el plan de equipo tambien pregunta el nombre y mantiene su precio', async () => {
  const { enviado } = await loQueSeLePideAStripe({ plan: 'equipo' });

  assert.equal(enviado.params.get('custom_fields[0][key]'), 'salon');
  assert.equal(enviado.params.get('line_items[0][price]'), 'price_1UBHkE2SQwDzHtsFTVWQ67l5');
});

test('un plan que no existe se sigue rechazando sin llamar a Stripe', async () => {
  const { enviado, res } = await loQueSeLePideAStripe({ plan: 'starter' });

  assert.equal(enviado, null, 'ha llamado a Stripe con un plan retirado');
  assert.equal(res.codigo, 400);
  assert.equal(res.cuerpo.error, 'invalid_plan');
});

test('🔴 el boton de comprar ya no abre ningun formulario antes del pago', async () => {
  // Se vigila en el fichero que EJECUTA. Si alguien vuelve a meter la parada
  // intermedia, esto lo dice: es el paso donde se caian 5 de cada 7.
  const fs = await import('node:fs');
  const url = new URL('../src/scripts/checkout.ts', import.meta.url);
  const fuente = fs.readFileSync(url, 'utf8');
  const abrir = fuente.slice(fuente.indexOf('export async function openCheckout'));
  const cuerpo = abrir.slice(0, abrir.indexOf('\n}\n'));

  assert.ok(/return abrirPagoStripe\(plan/.test(cuerpo),
    'el boton ya no lleva derecho al pago');
  assert.ok(!/datos\.removeAttribute\('hidden'\)/.test(cuerpo),
    'ha vuelto el formulario de antes del pago');
  assert.ok(!/negocio\.focus\(\)/.test(cuerpo),
    'ha vuelto el formulario de antes del pago');
});
