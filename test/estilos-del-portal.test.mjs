// Que lo que pinta el JavaScript del portal tenga estilos de verdad.
//
// Lo que protege: Astro reescribe las reglas del <style> normal como
// `.clase[data-astro-cid-xxx]`, y ese atributo solo se lo pone a lo que esta
// escrito en la plantilla. Las tarjetas que crea el JavaScript con innerHTML no
// lo llevan, asi que esas reglas NO les llegan y salen sin ningun estilo.
//
// Ya paso: el rediseño entero de la seccion Clientes se subio a produccion sin
// aplicar una sola regla -- avatares convertidos en barras de color a todo lo
// ancho y el texto amontonado debajo. El build pasaba, la pagina cargaba y
// nadie se entero hasta verlo. Las reglas de esas partes tienen que estar en el
// bloque <style is:global>.

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

// La plantilla es el fichero quitandole scripts y estilos: eso SI lleva el
// atributo de Astro, y sus reglas pueden vivir en cualquiera de los dos bloques.
let plantilla = fuente;
for (const [a, b] of [...scripts, ...estilos].sort((x, y) => y[0] - x[0])) {
  plantilla = plantilla.slice(0, a) + plantilla.slice(b);
}

const jsDelPortal = scripts.map((s) => s[2]).join('\n');

const scoped = estilos.filter(([a]) => !/^<style[^>]*is:global/.test(fuente.slice(a, fuente.indexOf('>', a) + 1)));
const global = estilos.filter(([a]) => /^<style[^>]*is:global/.test(fuente.slice(a, fuente.indexOf('>', a) + 1)));

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

const enPlantilla = clasesDeAtributos(plantilla);
const enJs = clasesDeAtributos(jsDelPortal);
const reglaScoped = clasesConRegla(cssScoped);
const reglaGlobal = clasesConRegla(cssGlobal);

test('el portal tiene los dos bloques de estilos y JavaScript que pinta', () => {
  // Sin esto, un fichero reorganizado dejaria la comprobacion de abajo pasando
  // en vacio, que es peor que no tenerla.
  assert.ok(scoped.length >= 1, 'no encuentro el <style> normal');
  assert.ok(global.length >= 1, 'no encuentro el <style is:global>');
  assert.ok(enJs.size > 20, `el JavaScript solo pinta ${enJs.size} clases: revisa este test`);
  assert.ok(reglaGlobal.size > 20, 'el bloque global esta casi vacio: revisa este test');
});

test('lo que solo pinta el JavaScript tiene su regla donde le llega', () => {
  const sinEstilo = [...enJs]
    .filter((c) => !enPlantilla.has(c))
    .filter((c) => reglaScoped.has(c) && !reglaGlobal.has(c))
    .sort();

  assert.deepEqual(sinEstilo, [],
    'estas clases las pinta el JavaScript y su unica regla esta en el <style> normal, '
    + 'asi que en el navegador salen SIN NINGUN estilo. Muevelas al bloque <style is:global>.');
});

test('las tarjetas de Clientes siguen teniendo su estilo', () => {
  // El caso concreto que se rompio, por su nombre.
  for (const clase of ['cli-fila', 'cli-avatar', 'cli-chip', 'cli-main', 'cli-ficha-head']) {
    assert.ok(reglaGlobal.has(clase),
      `.${clase} no esta en el bloque global: la seccion Clientes se veria sin estilo`);
  }
});
