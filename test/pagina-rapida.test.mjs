// Lo que hace que la pagina se vea rapido en un movil.
//
// El 14-sep-2026, de 269 personas que entraron desde el anuncio, 113 --el 42%--
// se fueron sin bajar ni tocar nada. La pagina estaba en blanco 2,9 segundos, y
// tardaba lo mismo con wifi buena que con 4G flojo: no era su conexion, era la
// pagina bloqueandose sola.
//
// Se midio bloqueando las tipografias de Google y repitiendo: con ellas, se veia
// algo a los 2.552 ms; sin ellas, a los 1.492 ms. Un segundo entero.
//
// Los dos fallos que esto vigila son mudos: no rompen nada, no salen en ningun
// registro, y nadie se entera hasta que mira el rebote dos semanas despues.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const RAIZ = path.resolve(fileURLToPath(new URL('.', import.meta.url)), '..');
const leer = (p) => fs.readFileSync(path.join(RAIZ, p), 'utf8');

test('🔴 las tipografias NO se piden desde dentro del CSS', () => {
  // Un @import obliga a: bajar el CSS, leerlo, descubrir que hace falta otro CSS
  // de Google, ir a por el, y solo entonces pintar. Tres viajes en fila antes de
  // que se vea una letra. Es el segundo que costaba.
  const css = leer('src/styles/global.css');
  assert.ok(!/@import\s+url\(['"]?https?:\/\/fonts\.googleapis/.test(css),
    'ha vuelto el @import de las tipografias: eso son ~1.000 ms de pantalla en blanco en movil');
});

test('las tipografias se piden desde la cabecera, a la vez que lo demas', () => {
  const layout = leer('src/layouts/Layout.astro');
  assert.ok(/<link rel="stylesheet" href="https:\/\/fonts\.googleapis\.com\/css2/.test(layout),
    'no estan en la cabecera: la pagina se quedaria sin su letra');
  assert.ok(/preconnect.*fonts\.gstatic\.com/.test(layout),
    'sin preconnect a gstatic se pierde otro viaje de ida y vuelta');
});

test('la letra no deja el texto invisible mientras carga', () => {
  // `display=swap` hace que el texto se vea desde el primer momento con una
  // letra del sistema y cambie luego. Sin eso, el navegador tapa el texto hasta
  // 3 segundos esperando a Google.
  const layout = leer('src/layouts/Layout.astro');
  const enlace = layout.match(/<link rel="stylesheet" href="(https:\/\/fonts\.googleapis[^"]+)"/);
  assert.ok(enlace, 'no encuentro el enlace de las tipografias');
  assert.ok(/display=swap/.test(enlace[1]),
    'sin display=swap el texto se queda invisible esperando a que llegue la letra');
});

test('🔴 la captura del CRM no vuelve a ser un PNG de medio mega', () => {
  // Pesaba 467 KB de los 781 KB de toda la pagina. Las demas imagenes del sitio
  // ya eran webp; esta se habia quedado atras.
  const plan = leer('src/components/PlanDetail.astro');
  assert.ok(!/demo-crm\.png/.test(plan),
    'la pagina vuelve a servir el PNG de 467 KB');
  assert.ok(/demo-crm\.webp/.test(plan), 'no se esta usando la version ligera');
});

test('la imagen ligera existe de verdad y pesa lo que tiene que pesar', () => {
  // Que el codigo la nombre no significa que este. Si falta, el hueco sale vacio.
  const webp = path.join(RAIZ, 'public/img/demo-crm.webp');
  assert.ok(fs.existsSync(webp), 'la imagen webp no existe: saldria un hueco roto');
  const bytes = fs.statSync(webp).size;
  assert.ok(bytes < 150000, `la webp pesa ${bytes} bytes: algo la ha vuelto a engordar`);
  assert.ok(bytes > 20000, `la webp pesa solo ${bytes} bytes: se ha guardado con una calidad que se nota`);
});

test('ninguna imagen de la pagina de producto pasa de 150 KB', () => {
  // Regla general, para que no vuelva a colarse otra. Si alguna hace falta mas
  // grande, se cambia el numero a proposito y queda escrito aqui.
  const plan = leer('src/components/PlanDetail.astro');
  const usadas = [...plan.matchAll(/["'](\/img\/[^"']+\.(?:png|jpe?g|webp|avif))["']/g)].map((m) => m[1]);
  assert.ok(usadas.length > 0, 'no encuentro ninguna imagen: el test se ha quedado ciego');

  const gordas = usadas
    .map((u) => ({ u, f: path.join(RAIZ, 'public', u.replace(/^\//, '')) }))
    .filter((x) => fs.existsSync(x.f))
    .map((x) => ({ u: x.u, kb: Math.round(fs.statSync(x.f).size / 1024) }))
    .filter((x) => x.kb > 150);

  assert.deepEqual(gordas, [], 'estas imagenes pesan demasiado para un movil con datos');
});
