// Que lo que pinta el JavaScript del portal tenga estilos de verdad.
//
// Lo que protege: Astro reescribe las reglas del <style> normal como
// `.clase[data-astro-cid-xxx]`, y ese atributo solo se lo pone a lo que esta
// escrito en la plantilla. Las tarjetas que crea el JavaScript con innerHTML no
// lo llevan, asi que esas reglas NO les llegan y salen sin ningun estilo.
//
// Ya paso dos veces:
//  - El rediseño entero de la seccion Clientes se subio a produccion sin
//    aplicar una sola regla: avatares convertidos en barras de color a todo lo
//    ancho y el texto amontonado debajo.
//  - La ficha de cliente (14-sep-2026): la etiqueta "Nota" se colocaba AL LADO
//    del recuadro en vez de encima, los recuadros salian sin borde y "Guardar"
//    y "Cerrar" parecian texto suelto. La primera version de este test NO lo
//    cazo, porque se saltaba las clases que ademas aparecen en la plantilla
//    -- y `crm-input` y `crm-btn-primary` se usan en los dos sitios.
//
// El build pasa, la pagina carga y nadie se entera hasta abrirla y verla.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const RAIZ = path.resolve(fileURLToPath(new URL('.', import.meta.url)), '..');
const PORTAL = path.join(RAIZ, 'src', 'pages', 'cliente', '[id].astro');
const fuente = fs.readFileSync(PORTAL, 'utf8');

/** Los trozos entre <script> y </script>: lo que se pinta desde JavaScript. */
function trozos(texto, abre, cierra) {
  const fuera = [];
  let i = 0;
  for (;;) {
    const a = texto.indexOf(abre, i);
    if (a === -1) break;
    const inicioCuerpo = texto.indexOf('>', a);
    const c = texto.indexOf(cierra, inicioCuerpo);
    if (inicioCuerpo === -1 || c === -1) break;
    fuera.push([a, c + cierra.length, texto.slice(inicioCuerpo + 1, c)]);
    i = c + cierra.length;
  }
  return fuera;
}

const scripts = trozos(fuente, '<script', '</script>');
const estilos = trozos(fuente, '<style', '</style>');

const jsDelPortal = scripts.map((s) => s[2]).join('\n');

const esGlobal = ([a]) => /^<style[^>]*is:global/.test(fuente.slice(a, fuente.indexOf('>', a) + 1));
const scoped = estilos.filter((e) => !esGlobal(e));
const global = estilos.filter(esGlobal);
const cssScoped = scoped.map((s) => s[2]).join('\n');
const cssGlobal = global.map((s) => s[2]).join('\n');

function clasesDeAtributos(texto) {
  const fuera = new Set();
  for (const m of texto.matchAll(/class=\\?"([^"\\]+)"/g)) {
    for (const c of m[1].split(/\s+/)) {
      if (/^[A-Za-z][\w-]*$/.test(c)) fuera.add(c);
    }
  }
  return fuera;
}

function clasesConRegla(css) {
  const fuera = new Set();
  for (const m of css.matchAll(/\.([A-Za-z][\w-]*)/g)) fuera.add(m[1]);
  return fuera;
}

/**
 * Quita lo que hay dentro de los `@media`.
 *
 * Hace falta para exigir que la regla base viva FUERA de ellos: si a una clase
 * se le borra su regla normal y solo le queda la del bloque de movil, en un
 * ordenador se ve sin estilo. Comprobar solo "existe una regla" se lo tragaba.
 */
function sinMediaQueries(css) {
  let fuera = '';
  let i = 0;
  for (;;) {
    const a = css.indexOf('@media', i);
    if (a === -1) { fuera += css.slice(i); return fuera; }
    fuera += css.slice(i, a);
    let j = css.indexOf('{', a);
    if (j === -1) return fuera;
    let nivel = 1;
    j += 1;
    while (j < css.length && nivel > 0) {
      if (css[j] === '{') nivel += 1;
      else if (css[j] === '}') nivel -= 1;
      j += 1;
    }
    i = j;
  }
}

/**
 * Que la clase tenga una regla CON PROPIEDADES, no que su nombre aparezca.
 *
 * Hace falta porque la comprobacion floja se deja engañar: al renombrar
 * `.cli-campo-caja` el nombre seguia apareciendo en `.cli-campo-caja:focus` y
 * en el bloque de movil, asi que el test lo daba por bueno mientras el recuadro
 * se quedaba sin borde, sin ancho y sin relleno. Lo caza scripts/sabotaje-ficha.py.
 */
function tieneReglaDeVerdad(css, clase) {
  const nombre = clase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  // La regla BASE: `.clase` ella sola, sin estado (`:focus`) y sin colgar de
  // otra cosa. Si lo unico que hubiera fuera `.clase:focus`, el elemento se
  // seguiria viendo sin estilo mientras nadie lo toca.
  const base = new RegExp(`(^|,)\\s*\\.${nombre}\\s*(,|$)`);
  // Fuera comentarios, incluido el cacho suelto que queda cuando el comentario
  // empezo antes del trozo capturado: un `/* Ficha */` delante del selector
  // hacia que esto leyera `.cli-ficha-head` como descendiente de algo y dijera
  // que no tenia regla. Lo encontro scripts/sabotaje-ficha.py.
  const limpio = (t) => t.replace(/\/\*[\s\S]*?\*\//g, ' ').replace(/^[\s\S]*\*\//, ' ');
  for (const bloque of css.matchAll(/([^{}]+)\{([^{}]*)\}/g)) {
    if (!base.test(limpio(bloque[1]).trim())) continue;
    if (/[\w-]+\s*:/.test(bloque[2])) return true;
  }
  return false;
}

const enJs = clasesDeAtributos(jsDelPortal);
const reglaScoped = clasesConRegla(cssScoped);
const reglaGlobal = clasesConRegla(cssGlobal);
// Para exigir la regla BASE: lo que hay dentro de los @media no cuenta.
const cssGlobalBase = sinMediaQueries(cssGlobal);

/** El trozo que pinta la ficha de cliente entera, historial incluido. */
function htmlDeLaFicha() {
  const desde = jsDelPortal.indexOf('var historialHtml = (c.historial');
  const hasta = jsDelPortal.indexOf("+ historialHtml + '</div>';", desde);
  return desde !== -1 && hasta !== -1 ? jsDelPortal.slice(desde, hasta) : '';
}

// Clases que ya estaban asi antes de escribir esto, en OTRAS secciones del
// portal. Se apuntan una a una para que el test avise desde hoy sin pedir
// arreglarlo todo de golpe: si aparece una nueva, salta. Cuando se arregle
// alguna, se quita de aqui. Esta lista NO perdona nada dentro de la ficha de
// cliente: eso lo comprueba aparte el test de mas abajo.
const DEUDA_CONOCIDA = [
  'crm-btn-primary',
  'crm-empty',
  'crm-input',
  'crm-muted-p',
  'crm-table',
  'crm-table-wrap',
];

test('el portal tiene los dos bloques de estilos y JavaScript que pinta', () => {
  // Sin esto, un fichero reorganizado dejaria las comprobaciones de abajo
  // pasando en vacio, que es peor que no tenerlas.
  assert.ok(scoped.length >= 1, 'no encuentro el <style> normal');
  assert.ok(global.length >= 1, 'no encuentro el <style is:global>');
  assert.ok(enJs.size > 20, `el JavaScript solo pinta ${enJs.size} clases: revisa este test`);
  assert.ok(reglaGlobal.size > 20, 'el bloque global esta casi vacio: revisa este test');
  assert.ok(htmlDeLaFicha().length > 500, 'no encuentro el trozo que pinta la ficha: revisa este test');
});

test('lo que pinta el JavaScript tiene su regla donde le llega', () => {
  const sinEstilo = [...enJs]
    .filter((c) => reglaScoped.has(c) && !reglaGlobal.has(c))
    .filter((c) => !DEUDA_CONOCIDA.includes(c))
    .sort();

  assert.deepEqual(sinEstilo, [],
    'estas clases las pinta el JavaScript y su regla solo esta en el <style> normal, '
    + 'asi que en el navegador esos elementos salen SIN NINGUN estilo. '
    + 'Ponles su regla en el bloque <style is:global>.');
});

test('la deuda conocida sigue siendo deuda, ni mas ni menos', () => {
  // Si una ya se arreglo hay que quitarla de la lista; si no, la lista crece
  // sola y el test se va quedando ciego otra vez.
  const yaArregladas = DEUDA_CONOCIDA
    .filter((c) => !(reglaScoped.has(c) && !reglaGlobal.has(c)))
    .sort();

  assert.deepEqual(yaArregladas, [],
    'estas ya tienen su regla donde toca: quitalas de DEUDA_CONOCIDA');
});

test('🔴 la ficha de cliente no usa NINGUNA clase que no le llegue', () => {
  // El caso del 14-sep, y sin perdonar nada: la ficha la pinta entera el
  // JavaScript, asi que cada clase suya necesita regla en el bloque global.
  // La lista de deuda no vale aqui a proposito -- si valiera, volver a poner
  // `crm-input` en un recuadro pasaria el test, que es justo lo que fallo.
  const sinEstilo = [...clasesDeAtributos(htmlDeLaFicha())]
    .filter((c) => !tieneReglaDeVerdad(cssGlobalBase, c))
    .sort();

  assert.deepEqual(sinEstilo, [],
    'la ficha de cliente usa estas clases y no tienen regla en el bloque global: '
    + 'en el navegador saldrian sin estilo (etiquetas al lado del recuadro, botones como texto suelto)');
});

test('🔴 ninguna variable de color se usa sin estar definida', () => {
  // --crm-border, --crm-text-muted, --crm-danger y --crm-accent-soft se usaban
  // por todo el CSS sin definirse en ningun sitio. Donde habia respaldo, el
  // respaldo era blanco translucido (pensado para el tema oscuro): sobre el
  // tema claro, invisible. Por eso los chips y las filas del historial salian
  // sin borde. Una variable que no existe no da ningun error: no pinta y ya.
  const usadas = new Set([...fuente.matchAll(/var\(\s*(--crm-[\w-]+)/g)].map((m) => m[1]));
  const definidas = new Set([...fuente.matchAll(/^\s*(--crm-[\w-]+)\s*:/gm)].map((m) => m[1]));
  const fantasma = [...usadas].filter((v) => !definidas.has(v)).sort();

  assert.deepEqual(fantasma, [],
    'estas variables se usan pero no estan definidas en ningun tema: donde se usen, no pintan nada');
});

test('las dos vistas de Clientes siguen teniendo su estilo', () => {
  // Los casos concretos que se rompieron, por su nombre.
  for (const clase of ['cli-fila', 'cli-avatar', 'cli-chip', 'cli-main', 'cli-ficha-head',
                       'cli-campo-caja', 'cli-ficha-nombre', 'cli-ficha-guardar']) {
    assert.ok(tieneReglaDeVerdad(cssGlobalBase, clase),
      `.${clase} no tiene regla propia en el bloque global: se veria sin estilo`);
  }
});
