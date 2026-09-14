// Que pasa cuando la pantalla de pago NO sale.
//
// El 14-sep-2026: de las ultimas 100 pantallas de pago abiertas en Stripe hubo
// 2 ventas, y las dos eran nuestras. Y el codigo que la abre era esto:
//
//     embeddedCheckout = await stripe.initEmbeddedCheckout({ clientSecret });
//
// Sin limite de espera. Si Stripe tardaba o se atascaba, ese `await` se quedaba
// esperando para siempre: ruedecita girando, ningun error en pantalla, ningun
// aviso para nosotros. Un pago atascado y un cliente que se lo piensa daban
// exactamente el mismo dato, asi que no habia forma de distinguirlos.
//
// Estos tests NO leen el codigo: lo compilan y lo EJECUTAN contra un navegador
// de mentira. Leer el fuente solo prueba lo que el codigo dice; aqui hace falta
// saber lo que hace.
import { test, mock } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';

const RAIZ = path.resolve(fileURLToPath(new URL('.', import.meta.url)), '..');

const { conLimite } = await import(new URL('../src/scripts/espera-limitada.mjs', import.meta.url));

/** Deja correr los `then` pendientes. Varias vueltas, que la cadena es larga. */
async function turnos(veces = 12) {
  for (let i = 0; i < veces; i += 1) await new Promise((r) => setImmediate(r));
}

// ---------------------------------------------------------------------------
// La espera, probada sola, con un reloj que no corre solo.
// ---------------------------------------------------------------------------

function relojDeMentira() {
  const avisos = new Map();
  let siguiente = 1;
  return {
    reloj: {
      programa: (fn, ms) => { avisos.set(siguiente, { fn, ms }); return siguiente++; },
      cancela: (id) => avisos.delete(id),
    },
    sonar: () => { for (const { fn } of [...avisos.values()]) fn(); },
    vivos: () => avisos.size,
  };
}

test('🔴 si la pantalla de pago no llega nunca, se deja de esperar', async () => {
  const { reloj, sonar } = relojDeMentira();
  const espera = conLimite(new Promise(() => {}), 20000, () => {}, reloj);

  sonar();

  await assert.rejects(espera, /tardo_demasiado/,
    'sigue esperando para siempre: el visitante se queda con la ruedecita');
});

test('🔴 lo que llega TARDE se cierra, no se queda vivo', async () => {
  // Una promesa no se puede cancelar. Si no se cierra lo que llega tarde, queda
  // una pantalla de pago fantasma que ademas puede montarse sola despues.
  const { reloj, sonar } = relojDeMentira();
  const cerradas = [];
  let entregar;
  const tarde = new Promise((r) => { entregar = r; });

  const espera = conLimite(tarde, 20000, (v) => cerradas.push(v), reloj);
  sonar();
  await assert.rejects(espera, /tardo_demasiado/);

  entregar({ id: 'pantalla-fantasma' });
  await turnos(3);

  assert.deepEqual(cerradas, [{ id: 'pantalla-fantasma' }],
    'la pantalla que llego tarde no se ha cerrado');
});

test('si llega a tiempo, pasa tal cual y no se cierra nada', async () => {
  // Control positivo: sin esto, los dos tests de arriba podrian estar cazando
  // algo que en realidad falla siempre.
  const { reloj, vivos } = relojDeMentira();
  const cerradas = [];
  const valor = await conLimite(Promise.resolve({ id: 'buena' }), 20000, (v) => cerradas.push(v), reloj);

  assert.deepEqual(valor, { id: 'buena' });
  assert.deepEqual(cerradas, [], 'ha cerrado una pantalla que SI valia');
  assert.equal(vivos(), 0, 'se ha quedado un aviso de reloj sin cancelar');
});

test('un fallo de verdad se ve tal cual, sin disfrazarlo de espera agotada', async () => {
  const { reloj } = relojDeMentira();
  await assert.rejects(
    conLimite(Promise.reject(new Error('session_failed')), 20000, () => {}, reloj),
    /session_failed/,
    'un error real se esta confundiendo con una espera agotada');
});

// ---------------------------------------------------------------------------
// La pantalla de pago entera, compilada y ejecutada contra un navegador falso.
// ---------------------------------------------------------------------------

const ESBUILD = (() => {
  const base = path.join(RAIZ, 'node_modules/.pnpm');
  if (!fs.existsSync(base)) return null;
  const dir = fs.readdirSync(base).find((d) => d.startsWith('esbuild@'));
  if (!dir) return null;
  const bin = path.join(base, dir, 'node_modules/esbuild/bin/esbuild');
  return fs.existsSync(bin) ? bin : null;
})();
const saltar = ESBUILD ? false : 'no hay esbuild en node_modules (hace falta pnpm install)';

const COMPILADO = ESBUILD ? (() => {
  const salida = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'pago-')), 'checkout.mjs');
  execFileSync(ESBUILD, [
    path.join(RAIZ, 'src/scripts/checkout.ts'),
    '--bundle', '--format=esm', '--platform=neutral',
    '--define:import.meta.env.PUBLIC_STRIPE_KEY="pk_de_mentira"',
    `--outfile=${salida}`,
  ], { cwd: RAIZ, stdio: 'pipe' });
  return salida;
})() : null;

let copia = 0;

/** Un elemento de mentira: solo guarda atributos y escuchas. */
function elemento(id) {
  const atributos = new Map();
  const escuchas = new Map();
  return {
    id,
    innerHTML: '',
    textContent: '',
    dataset: {},
    style: {},
    setAttribute: (k, v) => atributos.set(k, String(v)),
    removeAttribute: (k) => atributos.delete(k),
    getAttribute: (k) => (atributos.has(k) ? atributos.get(k) : null),
    hasAttribute: (k) => atributos.has(k),
    addEventListener: (tipo, fn) => escuchas.set(tipo, fn),
    dispatch: (tipo, ev = {}) => escuchas.get(tipo)?.(ev),
    focus: () => {},
    /** true si esta oculto, que es lo que ve (o no ve) el visitante. */
    oculto: () => atributos.has('hidden'),
  };
}

/** Monta el navegador falso, carga checkout.ts compilado y da los mandos. */
async function montarPantalla({ initEmbeddedCheckout }) {
  const ids = ['checkout-modal', 'checkout-loading', 'checkout-error', 'stripe-checkout-mount',
               'checkout-plan-label', 'checkout-datos', 'checkout-negocio', 'checkout-close',
               'checkout-reintentar'];
  const els = new Map(ids.map((i) => [i, elemento(i)]));
  const senales = [];

  globalThis.document = {
    getElementById: (i) => els.get(i) || null,
    addEventListener: () => {},
    querySelector: () => null,
    createElement: () => elemento('creado'),
    body: { style: {}, prepend: () => {} },
  };
  // El codigo usa `location` a secas en un sitio y `window.location` en otro:
  // el navegador falso tiene que ofrecer los dos, y que sean el MISMO objeto.
  const donde = { pathname: '/paquetes/recepcionista', search: '' };
  globalThis.location = donde;
  globalThis.window = {
    location: donde,
    history: { replaceState: () => {} },
    nxMeasure: (nombre, datos) => senales.push({ nombre, datos }),
  };
  globalThis.sessionStorage = { getItem: () => null, setItem: () => {} };
  globalThis.Stripe = () => ({ initEmbeddedCheckout });
  globalThis.fetch = async () => ({
    ok: true,
    json: async () => ({ clientSecret: 'cs_de_mentira' }),
    text: async () => '',
  });

  copia += 1;
  const mod = await import(`${pathToFileURL(COMPILADO).href}?copia=${copia}`);
  return {
    mod,
    senales,
    el: (i) => els.get(i),
    nombres: () => senales.map((s) => s.nombre),
  };
}

test('🔴 si Stripe se atasca, sale un error, NO una ruedecita eterna', { skip: saltar }, async (t) => {
  const p = await montarPantalla({ initEmbeddedCheckout: () => new Promise(() => {}) });

  // Hay que guardarse el reloj de verdad ANTES de cambiarlo por el de mentira.
  // Sin esto, si alguien quita el limite de espera este test no falla: se queda
  // colgado para siempre, que es justo el fallo que viene a cazar. Un test que
  // se cuelga no avisa de nada.
  const esperaDeVerdad = globalThis.setTimeout;
  t.mock.timers.enable({ apis: ['setTimeout'] });

  const abriendo = p.mod.openCheckout('recepcionista');
  await turnos();

  // Mientras carga: ruedecita visible y error escondido. Eso esta bien.
  assert.equal(p.el('checkout-loading').oculto(), false, 'no muestra que esta cargando');
  assert.equal(p.el('checkout-error').oculto(), true);

  // Pasan los 20 segundos de espera maxima.
  t.mock.timers.tick(20001);
  await Promise.race([
    abriendo,
    new Promise((_, rechazar) => esperaDeVerdad(() => rechazar(new Error(
      'la pantalla de pago sigue esperando: no hay limite y el visitante se queda con la ruedecita',
    )), 3000)),
  ]);
  await turnos();

  assert.equal(p.el('checkout-loading').oculto(), true,
    'la ruedecita sigue girando: es exactamente el fallo que veniamos a arreglar');
  assert.equal(p.el('checkout-error').oculto(), false,
    'no se le ensena ningun error a quien queria pagar');

  const s = p.senales.find((x) => x.nombre === 'checkout_form_failed');
  assert.ok(s, 'un pago atascado no deja ningun rastro: seguiriamos sin enterarnos');
  assert.equal(s.datos.motivo, 'tardo_demasiado');
});

test('🔴 cuando la pantalla de pago SI sale, se manda la senal que faltaba', { skip: saltar }, async () => {
  const montada = [];
  const p = await montarPantalla({
    initEmbeddedCheckout: async () => ({ mount: (d) => montada.push(d), destroy: () => {} }),
  });

  await p.mod.openCheckout('recepcionista');
  await turnos();

  assert.deepEqual(montada, ['#stripe-checkout-mount'], 'el formulario no se ha llegado a montar');
  const s = p.senales.find((x) => x.nombre === 'checkout_form_shown');
  assert.ok(s, 'sin esta senal seguimos sin distinguir un pago atascado de uno que se lo piensa');
  assert.equal(s.datos.plan, 'recepcionista');
  assert.equal(typeof s.datos.ms, 'number', 'no se manda cuanto tardo: no se podra ajustar la espera');
  assert.equal(p.el('checkout-loading').oculto(), true, 'la ruedecita se queda encima del formulario');
});

test('🔴 si cierran la ventana mientras carga, la pantalla que llega tarde se tira', { skip: saltar }, async () => {
  // Antes se montaba igual, en una ventana ya cerrada.
  let entregar;
  let cerrada = false;
  const montada = [];
  const p = await montarPantalla({
    initEmbeddedCheckout: () => new Promise((r) => { entregar = r; }),
  });

  const abriendo = p.mod.openCheckout('recepcionista');
  await turnos();
  p.mod.closeCheckout();

  entregar({ mount: (d) => montada.push(d), destroy: () => { cerrada = true; } });
  await abriendo;
  await turnos();

  assert.deepEqual(montada, [], 'ha montado la pantalla de pago en una ventana ya cerrada');
  assert.equal(cerrada, true, 'la pantalla que llego tarde se ha quedado viva');
});

test('el fallo al crear la sesion tambien se avisa y se mide', { skip: saltar }, async () => {
  const p = await montarPantalla({
    initEmbeddedCheckout: async () => ({ mount: () => {}, destroy: () => {} }),
  });
  globalThis.fetch = async () => ({ ok: false, json: async () => ({}), text: async () => 'boom' });

  await p.mod.openCheckout('recepcionista');
  await turnos();

  assert.equal(p.el('checkout-error').oculto(), false, 'no se avisa de que el pago no se pudo crear');
  const s = p.senales.find((x) => x.nombre === 'checkout_form_failed');
  assert.ok(s, 'un pago que no se pudo ni crear no deja rastro en la medicion');
  assert.equal(s.datos.motivo, 'session_failed');
});

test('el boton de volver a intentarlo reabre el pago', { skip: saltar }, async () => {
  let veces = 0;
  const p = await montarPantalla({
    initEmbeddedCheckout: async () => { veces += 1; return { mount: () => {}, destroy: () => {} }; },
  });

  await p.mod.openCheckout('recepcionista');
  await turnos();
  assert.equal(veces, 1);

  p.el('checkout-reintentar').dispatch('click', {});
  await turnos();

  assert.equal(veces, 2, 'el boton de reintentar no hace nada');
  assert.ok(p.nombres().includes('checkout_form_retried'));
});

test('medir nunca puede romper el pago', { skip: saltar }, async () => {
  // Si la medicion revienta, el cliente TIENE que poder pagar igual.
  const montada = [];
  const p = await montarPantalla({
    initEmbeddedCheckout: async () => ({ mount: (d) => montada.push(d), destroy: () => {} }),
  });
  globalThis.window.nxMeasure = () => { throw new Error('la medicion ha explotado'); };

  await p.mod.openCheckout('recepcionista');
  await turnos();

  assert.deepEqual(montada, ['#stripe-checkout-mount'],
    'un fallo midiendo ha impedido que el cliente pague');
  assert.equal(p.el('checkout-error').oculto(), true, 'sale un error por culpa de la medicion');
});
