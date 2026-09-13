// El mapa de calor no puede acabar midiendo dentro del CRM de un cliente.
//
// `Layout.astro` lo usan TODAS las paginas: tambien /admin, el portal de cada
// salon (/cliente/...) y la pagina donde una clienta reserva su cita
// (/reservar/...). Si el mapa se montara en todas, estariamos guardando donde
// pulsa un salon dentro de su propio CRM. No sirve para nada y no deberia
// existir ese dato.
//
// Por eso la lista es de PERMITIDAS. Lo que se vigila aqui es justo eso: que
// una pagina privada nueva NO se mida sola por el hecho de existir.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const RAIZ = path.resolve(fileURLToPath(new URL('.', import.meta.url)), '..');
const { esPaginaMedible } = await import(
  new URL('../src/scripts/paginas-medidas.mjs', import.meta.url)
);
const MEDICION = fs.readFileSync(path.join(RAIZ, 'src/scripts/measurement.ts'), 'utf8');

test('se mide el camino del dinero: llegada, ficha del plan y gracias', () => {
  for (const ruta of ['/', '/paquetes/recepcionista', '/paquetes/equipo', '/comparativa',
                      '/alternativa-a-booksy', '/gracias']) {
    assert.equal(esPaginaMedible(ruta), true, `deberia medirse: ${ruta}`);
  }
});

test('🔴 NO se mide nada privado: portal del cliente, admin ni reservas', () => {
  // Si alguno de estos se pone en true, estamos grabando donde pulsa un cliente
  // en su propio panel, o una clienta mientras reserva su cita.
  for (const ruta of [
    '/cliente/estudio-ricardo-demo-mostoles-946279',
    '/cliente/estudio-ricardo-demo-mostoles-946279/login',
    '/cliente/estudio-ricardo-demo-mostoles-946279/onboarding',
    '/admin',
    '/admin/mailbox',
    '/admin/client/prueba-equipo-79-mostoles-dca1db',
    '/reservar/estudio-ricardo-demo-mostoles-946279',
    '/f/ABC123',
    '/demo',
  ]) {
    assert.equal(esPaginaMedible(ruta), false, `NO deberia medirse: ${ruta}`);
  }
});

test('la barra final, la interrogacion y la almohadilla no cuelan una pagina privada', () => {
  assert.equal(esPaginaMedible('/paquetes/recepcionista/'), true);
  assert.equal(esPaginaMedible('/paquetes/recepcionista?oppref=A02'), true);
  assert.equal(esPaginaMedible('/gracias#top'), true);
  assert.equal(esPaginaMedible('/cliente/x/'), false);
  assert.equal(esPaginaMedible('/admin?t=loquesea'), false);
  assert.equal(esPaginaMedible('/reservar/x#seccion'), false);
});

test('una ruta rara no revienta ni abre la puerta', () => {
  for (const basura of ['', 'paquetes', null, undefined, 42, {}, '//admin']) {
    assert.equal(esPaginaMedible(basura), false, `no deberia medirse: ${JSON.stringify(basura)}`);
  }
});

test('la lista es de permitidas, no de prohibidas', () => {
  // Un filtro escrito al reves (prohibir /admin y /cliente) dejaria pasar
  // cualquier pagina privada que se cree manana. Se vigila en el fichero.
  const fuente = fs.readFileSync(path.join(RAIZ, 'src/scripts/paginas-medidas.mjs'), 'utf8');
  assert.ok(!/\/admin|\/cliente|\/reservar/.test(fuente),
    'la lista nombra paginas privadas: eso es una lista de prohibidas y se olvidara una');
  assert.ok(/PAGINAS_MEDIDAS/.test(fuente));
});

// ── Lo que el mapa manda, y a quien ────────────────────────────────────────
test('🔴 el mapa NO se esconde detras del aviso de cookies', () => {
  // Atarlo al consentimiento mediria solo a la minoria que acepta todo, y los
  // numeros mentirian sin avisar. Umami ya mide a todo el mundo igual.
  const motor = MEDICION.slice(MEDICION.indexOf('function montarMapaDeCalor'));
  const cuerpo = motor.slice(0, motor.indexOf('\n}\n'));
  assert.ok(!/nx_cookie_consent|hasAnalyticsConsent|consent/i.test(cuerpo),
    'alguien ha metido el mapa detras del consentimiento');
});

test('🔴 los puntos del mapa van SOLO a Umami, nunca a los pixeles de publicidad', () => {
  // `measure()` reparte a Plausible, Google, Meta y al pixel de OpenAI. Un
  // heatmap_click ahi seria ruido en la campana, y en el peor caso Google lo
  // contaria como una senal de conversion.
  const motor = MEDICION.slice(MEDICION.indexOf('function montarMapaDeCalor'));
  const cuerpo = motor.slice(0, motor.indexOf('\nconst attribution'));
  const llamadas = cuerpo.match(/\bmeasure\(/g) || [];
  assert.deepEqual(llamadas, [], 'el mapa esta usando measure(): eso llega a los pixeles');
  assert.ok(/medirSoloEnUmami\('heatmap_click'/.test(cuerpo));
  assert.ok(/medirSoloEnUmami\('heatmap_hover'/.test(cuerpo));
  assert.ok(/medirSoloEnUmami\('scroll_depth_reached'/.test(cuerpo));
});

test('se guarda la casilla de la cuadricula, nunca el punto exacto', () => {
  // Guardar coordenadas exactas permitiria reconstruir el recorrido de una
  // persona. La cuadricula de 12x24 no.
  assert.ok(/grid_x:/.test(MEDICION) && /grid_y:/.test(MEDICION));
  const motor = MEDICION.slice(MEDICION.indexOf('function casillaDe'));
  const cuerpo = motor.slice(0, motor.indexOf('\n}\n'));
  assert.ok(!/clientX:|clientY:|pageX:|pageY:/.test(cuerpo),
    'se estan mandando coordenadas exactas');
});

test('hay tope de clics y de puntos de raton por carga', () => {
  assert.ok(/MAPA_TOPE_CLICS\s*=\s*\d+/.test(MEDICION), 'sin tope, un martilleo llena la base');
  assert.ok(/MAPA_TOPE_ATENCION\s*=\s*\d+/.test(MEDICION));
});

test('el mapa no arranca si la pagina no es de las permitidas', () => {
  const motor = MEDICION.slice(MEDICION.indexOf('function montarMapaDeCalor'));
  const primeras = motor.slice(0, 260);
  assert.ok(/if \(!esPaginaMedible\(location\.pathname\)\) return;/.test(primeras),
    'el mapa se monta sin comprobar en que pagina esta');
});

test('se distingue el clic que no da en nada (el dato que no se ve de otra forma)', () => {
  assert.ok(/sobre: .*'pulsable' : 'nada'/.test(MEDICION),
    'no se esta marcando si el clic cayo sobre algo pulsable');
});

test('el boton de la demo ya se mide en Umami', () => {
  // Layout.astro lo mandaba a Google, Meta y Plausible, pero no a Umami, que es
  // donde miramos. Por eso "Quiero verla responder" no aparecia en ningun sitio.
  assert.ok(/measure\('cta_clicked'/.test(MEDICION));
  assert.ok(/\[data-track\]/.test(MEDICION));
});
