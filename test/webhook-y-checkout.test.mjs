// Regresion del camino del dinero en Vercel: el receptor de Stripe y la creacion
// de la sesion de pago. Son los DOS ficheros que ejecutan de verdad en produccion
// (la carpeta api/ de la raiz gana sobre vercel.json y sobre src/pages/api/), y
// hasta hoy no tenian ni una prueba.
//
// Lo que protege:
//   1. Que un alta fallida NO devuelva 200. Devolver 200 hacia que Stripe diera el
//      evento por entregado y no reintentara nunca: el cliente pagaba y no existia.
//   2. Que una firma valida pero vieja no cuele.
//   3. Que Vercel no mande ningun correo (el de bienvenida lo manda la Pi; los dos
//      remitentes que habia significaban dos correos al mismo cliente).
//   4. Que el nombre del negocio llegue a metadata[salon], que es de donde lo saca
//      el alta automatica. Sin el, /provision rechaza con missing_fields.

import { test, before, after, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const RAIZ = path.resolve(fileURLToPath(new URL('.', import.meta.url)), '..');
const SECRETO_WH = 'whsec_de_prueba';
const PUERTO_WH = 3591;
const PUERTO_PI = 3592;

let servidorWh, servidorPi, handlerWebhook, handlerSesion;
let peticionesPi = [];
let piResponde = { status: 200, cuerpo: { clientId: 'salon-de-prueba-abc123' } };
let llamadasFetch = [];
let fetchOriginal;

// Adapta un servidor http normal a lo que espera una funcion de Vercel.
function comoVercel(handler) {
  return (req, res) => {
    res.status = code => { res.statusCode = code; return res; };
    res.json = obj => { res.setHeader('Content-Type', 'application/json'); res.end(JSON.stringify(obj)); return res; };
    res.end.bind(res);
    Promise.resolve(handler(req, res)).catch(err => {
      res.statusCode = 500;
      res.end(JSON.stringify({ error: 'test_handler_error', detail: err.message }));
    });
  };
}

function firmar(cuerpo, secreto = SECRETO_WH, tiempo = Math.floor(Date.now() / 1000)) {
  const firma = crypto.createHmac('sha256', secreto).update(`${tiempo}.${cuerpo}`).digest('hex');
  return `t=${tiempo},v1=${firma}`;
}

const EVENTO_COMPRA = {
  id: 'evt_test_001',
  type: 'checkout.session.completed',
  data: {
    object: {
      id: 'cs_test_abc',
      customer: 'cus_test',
      subscription: 'sub_test',
      amount_total: 2900,
      customer_details: { email: 'cliente@ejemplo.invalid', name: 'Ana Ruiz', phone: '+34600111222' },
      metadata: { plan: 'recepcionista', salon: 'Peluqueria Marta', telefono: '+34600111222' },
    },
  },
};

async function postWebhook(evento, { firmaValida = true, tiempo } = {}) {
  const cuerpo = JSON.stringify(evento);
  const cabeceras = { 'Content-Type': 'application/json' };
  cabeceras['stripe-signature'] = firmaValida
    ? firmar(cuerpo, SECRETO_WH, tiempo)
    : firmar(cuerpo, 'secreto-equivocado', tiempo);
  const r = await fetchOriginal(`http://127.0.0.1:${PUERTO_WH}/`, { method: 'POST', headers: cabeceras, body: cuerpo });
  return { status: r.status, cuerpo: await r.json().catch(() => ({})) };
}

before(async () => {
  process.env.STRIPE_WEBHOOK_SECRET = SECRETO_WH;
  process.env.NEXUX_CLIENTS_URL = `http://127.0.0.1:${PUERTO_PI}`;
  process.env.PROVISION_SECRET = 'secreto-de-prueba';
  process.env.STRIPE_SECRET_KEY = 'sk_test_de_prueba';
  delete process.env.TELEGRAM_BOT_TOKEN;
  delete process.env.TELEGRAM_CHAT_ID;
  delete process.env.BREVO_API_KEY;

  fetchOriginal = globalThis.fetch;

  handlerWebhook = (await import(path.join(RAIZ, 'api/webhook/stripe.js'))).default;
  handlerSesion = (await import(path.join(RAIZ, 'api/stripe/create-session.js'))).default;

  // La Pi de mentira: responde lo que le digamos y guarda lo que recibe.
  servidorPi = http.createServer((req, res) => {
    let cuerpo = '';
    req.on('data', c => (cuerpo += c));
    req.on('end', () => {
      peticionesPi.push({ url: req.url, secreto: req.headers['x-provision-secret'], cuerpo: JSON.parse(cuerpo || '{}') });
      res.writeHead(piResponde.status, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(piResponde.cuerpo));
    });
  });
  await new Promise(r => servidorPi.listen(PUERTO_PI, '127.0.0.1', r));

  servidorWh = http.createServer(comoVercel(handlerWebhook));
  await new Promise(r => servidorWh.listen(PUERTO_WH, '127.0.0.1', r));
});

after(async () => {
  globalThis.fetch = fetchOriginal;
  if (servidorWh) await new Promise(r => servidorWh.close(r));
  if (servidorPi) await new Promise(r => servidorPi.close(r));
});

beforeEach(() => {
  peticionesPi = [];
  llamadasFetch = [];
  piResponde = { status: 200, cuerpo: { clientId: 'salon-de-prueba-abc123' } };
  // Cualquier salida a internet que no sea la Pi queda registrada, para poder
  // afirmar que Vercel NO manda correos.
  globalThis.fetch = async (url, opciones) => {
    llamadasFetch.push({ url: String(url), opciones });
    return fetchOriginal(url, opciones);
  };
});

test('un alta que falla devuelve 5xx, no 200: si no, Stripe no reintenta jamas', async () => {
  piResponde = { status: 500, cuerpo: { error: 'pi_rota' } };
  const r = await postWebhook(EVENTO_COMPRA);
  assert.equal(r.status, 503, `devolvio ${r.status}; con 200 el cliente paga y no existe`);
  assert.equal(r.cuerpo.retryable, true);
  assert.equal(peticionesPi.length, 1, 'lo intento contra la Pi');
});

test('si la Pi responde 2xx pero sin clientId, tampoco se da por buena el alta', async () => {
  piResponde = { status: 200, cuerpo: { ok: true } };
  const r = await postWebhook(EVENTO_COMPRA);
  assert.equal(r.status, 503);
  assert.equal(r.cuerpo.motivo, 'sin_client_id');
});

test('un alta correcta responde 200 y llama a la Pi con el secreto y los datos', async () => {
  const r = await postWebhook(EVENTO_COMPRA);
  assert.equal(r.status, 200);
  assert.equal(r.cuerpo.received, true);
  assert.equal(peticionesPi.length, 1);
  const p = peticionesPi[0];
  assert.equal(p.url, '/provision');
  assert.equal(p.secreto, 'secreto-de-prueba', 'debe autenticarse contra la Pi');
  assert.equal(p.cuerpo.salon, 'Peluqueria Marta', 'el nombre del negocio debe llegar al alta');
  assert.equal(p.cuerpo.stripeSessionId, 'cs_test_abc', 'la sesion identifica el alta para los reintentos');
});

test('sin el nombre del negocio no se da por buena el alta, y se dice cual falta', async () => {
  const evento = structuredClone(EVENTO_COMPRA);
  delete evento.data.object.metadata.salon;
  const r = await postWebhook(evento);
  assert.equal(r.status, 503);
  assert.match(r.cuerpo.motivo, /faltan_datos/);
  assert.match(r.cuerpo.motivo, /salon/);
  assert.equal(peticionesPi.length, 0, 'ni siquiera llega a molestar a la Pi');
});

test('una firma invalida se rechaza con 400', async () => {
  const r = await postWebhook(EVENTO_COMPRA, { firmaValida: false });
  assert.equal(r.status, 400);
  assert.equal(r.cuerpo.error, 'invalid_signature');
  assert.equal(peticionesPi.length, 0);
});

test('una firma valida pero de hace mas de 300 s se rechaza', async () => {
  const hace10Min = Math.floor(Date.now() / 1000) - 600;
  const r = await postWebhook(EVENTO_COMPRA, { tiempo: hace10Min });
  assert.equal(r.status, 400, 'una firma vieja capturada no puede seguir valiendo');
  assert.equal(peticionesPi.length, 0);
});

test('Vercel no manda ningun correo: de eso se encarga la Pi', async () => {
  await postWebhook(EVENTO_COMPRA);
  const correos = llamadasFetch.filter(l => l.url.includes('brevo') || l.url.includes('smtp'));
  assert.equal(correos.length, 0, `Vercel intento mandar ${correos.length} correo(s); el de bienvenida lo manda la Pi`);
});

test('un evento que no es una compra se acepta sin tocar nada', async () => {
  const r = await postWebhook({ id: 'evt_x', type: 'invoice.paid', data: { object: {} } });
  assert.equal(r.status, 200);
  assert.equal(peticionesPi.length, 0);
});

test('la sesion de pago lleva el nombre del negocio a metadata[salon]', async () => {
  let cuerpoEnviado = null;
  globalThis.fetch = async (url, opciones) => {
    cuerpoEnviado = String(opciones?.body || '');
    return new Response(JSON.stringify({ client_secret: 'cs_secret_x' }), {
      status: 200, headers: { 'Content-Type': 'application/json' },
    });
  };
  const req = {
    method: 'POST',
    headers: {},
    body: { plan: 'recepcionista', salon: 'Peluqueria Marta', telefono: '+34600111222' },
  };
  let salida = null;
  const res = {
    setHeader() {},
    status(c) { this._c = c; return this; },
    json(o) { salida = { code: this._c || 200, body: o }; return this; },
    end() { salida = { code: this._c || 200, body: null }; return this; },
  };
  await handlerSesion(req, res);
  assert.equal(salida.code, 200, 'la sesion deberia crearse');
  assert.ok(cuerpoEnviado.includes('metadata%5Bsalon%5D=Peluqueria+Marta'),
    `metadata[salon] no viaja a Stripe. Enviado: ${cuerpoEnviado.slice(0, 300)}`);
});

test('un plan que no existe no abre ningun pago', async () => {
  const req = { method: 'POST', headers: {}, body: { plan: 'inventado' } };
  let salida = null;
  const res = {
    setHeader() {},
    status(c) { this._c = c; return this; },
    json(o) { salida = { code: this._c, body: o }; return this; },
    end() { return this; },
  };
  await handlerSesion(req, res);
  assert.equal(salida.code, 400);
  assert.equal(salida.body.error, 'invalid_plan');
});
