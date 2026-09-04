// El camino del dinero, de punta a punta, con las DOS piezas reales conectadas.
//
// Los tests de cada lado prueban su pieza. Este prueba la JUNTA, que es donde
// estaban casi todos los fallos: el receptor de Stripe de Vercel llamando al
// /provision de verdad de la Pi. Cubre los eslabones 1-4 de la prueba de
// aceptacion (pago -> UNA cuenta -> UN correo -> portal que abre) y el 7-8 en su
// parte comprobable sin canal (cancelacion -> cuenta desactivada).
//
// No se cobra nada: el evento de Stripe se firma aqui con un secreto de prueba.
// No se envia ningun correo: Brevo apunta a un servidor de mentira.
// No se toca ningun cliente real: la Pi de prueba vive en un directorio temporal.
//
// Si no encuentra el repositorio de nexux-clients, el test se salta y lo dice.

import { test, before, after, describe } from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const RAIZ_PRO = path.resolve(fileURLToPath(new URL('.', import.meta.url)), '..');
const RAIZ_PI = process.env.NEXUX_CLIENTS_PATH || path.resolve(RAIZ_PRO, '..', 'nexux-clients-wt-ola1');
const HAY_PI = fs.existsSync(path.join(RAIZ_PI, 'provision-http.js'));

const SECRETO_WH = 'whsec_de_prueba';
const SECRETO_PROV = 'secreto-de-prueba';
const P_WH = 3593, P_PI = 3594, P_BREVO = 3595;

const TMP = fs.mkdtempSync(path.join(os.tmpdir(), 'e2e-dinero-'));
let servidorWh, servidorPi, servidorBrevo, cwdOriginal;
let correos = [];

function comoVercel(handler) {
  return (req, res) => {
    res.status = c => { res.statusCode = c; return res; };
    res.json = o => { res.setHeader('Content-Type', 'application/json'); res.end(JSON.stringify(o)); return res; };
    Promise.resolve(handler(req, res)).catch(err => {
      res.statusCode = 500; res.end(JSON.stringify({ error: err.message }));
    });
  };
}

function prepararCopiaPi() {
  let t = fs.readFileSync(path.join(RAIZ_PI, 'provision-http.js'), 'utf8');
  t = t.replace("installEmailCapture('nexux-clients');", '// [test] desactivado', 1);
  t = t.replace('qrPngBase64 = await startBotAndCaptureQr(clientId, config);',
                'qrPngBase64 = null; // [test] sin sockets de WhatsApp', 1);
  const i = t.indexOf('app.listen(PORT,');
  const j = t.indexOf('});', t.indexOf('startFollowupScheduler();', i)) + 3;
  t = t.slice(0, i) + 'export { app };\n' + t.slice(j);
  const destino = path.join(RAIZ_PI, '.test-provision-e2e.mjs');
  fs.writeFileSync(destino, t);
  return destino;
}

function firmar(cuerpo, secreto = SECRETO_WH, t = Math.floor(Date.now() / 1000)) {
  return `t=${t},v1=${crypto.createHmac('sha256', secreto).update(`${t}.${cuerpo}`).digest('hex')}`;
}

async function mandarAStripeWebhook(evento) {
  const cuerpo = JSON.stringify(evento);
  const r = await fetch(`http://127.0.0.1:${P_WH}/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'stripe-signature': firmar(cuerpo) },
    body: cuerpo,
  });
  return { status: r.status, cuerpo: await r.json().catch(() => ({})) };
}

const compra = (n = 1) => ({
  id: `evt_e2e_${n}`,
  type: 'checkout.session.completed',
  data: {
    object: {
      id: `cs_e2e_${n}`,
      customer: `cus_e2e_${n}`,
      subscription: `sub_e2e_${n}`,
      amount_total: 2900,
      customer_details: { email: `cliente${n}@ejemplo.invalid`, name: 'Ana Ruiz', phone: '+34600111222' },
      metadata: { plan: 'recepcionista', salon: `Peluqueria E2E ${n}`, telefono: '+34600111222' },
    },
  },
});

const clientes = () => fs.readdirSync(path.join(TMP, 'clients'))
  .filter(f => !f.startsWith('.') && fs.statSync(path.join(TMP, 'clients', f)).isDirectory());
const configDe = id => JSON.parse(fs.readFileSync(path.join(TMP, 'clients', id, 'config.json'), 'utf8'));

describe('camino del dinero de punta a punta', { skip: HAY_PI ? false : `no encuentro nexux-clients en ${RAIZ_PI}` }, () => {
  before(async () => {
    process.env.PROVISION_SECRET = SECRETO_PROV;
    process.env.PROVISION_PORT = String(P_PI);
    process.env.BREVO_API_KEY = 'clave-de-prueba';
    process.env.BREVO_API_URL = `http://127.0.0.1:${P_BREVO}/`;
    process.env.STRIPE_WEBHOOK_SECRET = SECRETO_WH;
    process.env.NEXUX_CLIENTS_URL = `http://127.0.0.1:${P_PI}`;
    delete process.env.TELEGRAM_BOT_TOKEN;

    fs.mkdirSync(path.join(TMP, 'clients'), { recursive: true });
    fs.cpSync(path.join(RAIZ_PI, 'templates'), path.join(TMP, 'templates'), { recursive: true });
    cwdOriginal = process.cwd();
    process.chdir(TMP);

    servidorBrevo = http.createServer((req, res) => {
      let c = ''; req.on('data', d => (c += d));
      req.on('end', () => {
        correos.push(JSON.parse(c || '{}'));
        res.writeHead(201, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ messageId: `<e2e-${correos.length}@brevo>` }));
      });
    });
    await new Promise(r => servidorBrevo.listen(P_BREVO, '127.0.0.1', r));

    const { app } = await import(prepararCopiaPi() + `?v=${Date.now()}`);
    await new Promise(r => (servidorPi = app.listen(P_PI, '127.0.0.1', r)));

    const handler = (await import(path.join(RAIZ_PRO, 'api/webhook/stripe.js'))).default;
    servidorWh = http.createServer(comoVercel(handler));
    await new Promise(r => servidorWh.listen(P_WH, '127.0.0.1', r));
  });

  after(async () => {
    for (const s of [servidorWh, servidorPi, servidorBrevo]) if (s) await new Promise(r => s.close(r));
    if (cwdOriginal) process.chdir(cwdOriginal);
    fs.rmSync(TMP, { recursive: true, force: true });
    fs.rmSync(path.join(RAIZ_PI, '.test-provision-e2e.mjs'), { force: true });
  });

  test('una compra crea UNA cuenta, manda UN correo y el portal abre con su token', async () => {
    correos = [];
    const r = await mandarAStripeWebhook(compra(1));

    // Eslabon 1: el pago se procesa
    assert.equal(r.status, 200, `el webhook devolvio ${r.status}`);

    // Eslabon 2: exactamente una cuenta, completa y activa
    assert.equal(clientes().length, 1, `se crearon ${clientes().length} cuentas`);
    const id = clientes()[0];
    const cfg = configDe(id);
    assert.equal(cfg.active, true, 'la cuenta nace activa');
    assert.ok(cfg.accessToken, 'tiene token de acceso');
    assert.ok(cfg.limits, 'tiene limites del plan');
    assert.ok(cfg.features, 'tiene funciones del plan');
    assert.equal(cfg.name, 'Peluqueria E2E 1', 'guarda el nombre del negocio que se pidio en el modal');
    assert.equal(cfg.stripeSubscriptionId, 'sub_e2e_1', 'queda enlazada a su suscripcion');

    // Eslabon 3: exactamente un correo, con el enlace que abre la cuenta
    assert.equal(correos.length, 1, `salieron ${correos.length} correos; debe salir uno`);
    assert.ok(correos[0].htmlContent.includes(cfg.accessToken), 'el correo lleva el enlace del portal');
    assert.equal(correos[0].to[0].email, 'cliente1@ejemplo.invalid');

    // Eslabon 4: ese enlace abre de verdad el portal
    const portal = await fetch(`http://127.0.0.1:${P_PI}/client/${id}/status?t=${cfg.accessToken}`);
    assert.equal(portal.status, 200, 'el token del correo debe abrir el portal');

    // Y un token equivocado no
    const ajeno = await fetch(`http://127.0.0.1:${P_PI}/client/${id}/status?t=token-inventado`);
    assert.equal(ajeno.status, 401, 'un token inventado no puede abrir la cuenta de nadie');
  });

  test('la misma compra entregada dos veces no duplica cuenta ni correo', async () => {
    correos = [];
    await mandarAStripeWebhook(compra(2));
    const tras1 = clientes().length;
    assert.equal(correos.length, 1);

    await mandarAStripeWebhook(compra(2));
    assert.equal(clientes().length, tras1, 'la segunda entrega no puede crear otra cuenta');
    assert.equal(correos.length, 1, 'ni mandar otro correo');
  });

  test('si la Pi no responde, el webhook pide reintento en vez de dar el alta por buena', async () => {
    await new Promise(r => servidorPi.close(r));
    const r = await mandarAStripeWebhook(compra(3));
    assert.equal(r.status, 503, 'con la Pi caida NO se puede responder 200');
    assert.equal(r.cuerpo.retryable, true);
    // devolver la Pi para los siguientes
    const { app } = await import(prepararCopiaPi() + `?v=${Date.now()}b`);
    await new Promise(r2 => (servidorPi = app.listen(P_PI, '127.0.0.1', r2)));
  });

  test('cancelar la suscripcion desactiva la cuenta en la Pi', async () => {
    correos = [];
    await mandarAStripeWebhook(compra(4));
    const id = clientes().find(c => configDe(c).stripeSubscriptionId === 'sub_e2e_4');
    assert.ok(id, 'la cuenta de la compra 4 deberia existir');
    assert.equal(configDe(id).active, true);

    // La baja la procesa la Pi (es su rama de ciclo de vida), no Vercel.
    const evento = {
      id: 'evt_e2e_baja',
      type: 'customer.subscription.deleted',
      data: { object: { id: 'sub_e2e_4', customer: 'cus_e2e_4' } },
    };
    const cuerpo = JSON.stringify(evento);
    const r = await fetch(`http://127.0.0.1:${P_PI}/webhook/stripe`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'stripe-signature': firmar(cuerpo, process.env.STRIPE_WEBHOOK_SECRET) },
      body: cuerpo,
    });
    assert.equal(r.status, 200, 'la Pi debe aceptar el evento de baja firmado');
    assert.equal(configDe(id).active, false, 'tras cancelar, la cuenta queda desactivada');
    assert.ok(configDe(id).deactivatedAt, 'y queda constancia de cuando');
  });

  test('la Pi rechaza un evento de baja sin firma: nadie desactiva clientes desde fuera', async () => {
    await mandarAStripeWebhook(compra(5));
    const id = clientes().find(c => configDe(c).stripeSubscriptionId === 'sub_e2e_5');
    const evento = { id: 'evt_e2e_falso', type: 'customer.subscription.deleted', data: { object: { id: 'sub_e2e_5', customer: 'cus_e2e_5' } } };
    const r = await fetch(`http://127.0.0.1:${P_PI}/webhook/stripe`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(evento),
    });
    assert.equal(r.status, 400, 'sin firma no se acepta');
    assert.equal(configDe(id).active, true, 'y el cliente sigue activo');
  });
});
