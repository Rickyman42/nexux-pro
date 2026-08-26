/**
 * Plano 7: graba la pantalla de la conversacion, fotograma a fotograma.
 *
 * No se graba "en directo" con el reloj del navegador: se le pide a la pagina el
 * estado exacto del segundo t con window.pintar(t) y se hace una captura. Asi el
 * video sale identico cada vez y no depende de lo cargada que este la Pi, que es
 * justo lo que estropea las grabaciones de pantalla.
 *
 *   node p7-grabar.cjs            los 264 fotogramas (11 s a 24 fps)
 *   node p7-grabar.cjs --muestra  solo 3, para mirarlos antes de gastar el rato
 */
const fs = require('fs');
const path = require('path');

const PW = '/home/nexux/nexux-campaign-ops/node_modules/.pnpm/playwright-core@1.60.0/node_modules/playwright-core';
const { chromium } = require(PW);

const ANCHO = 720;
const ALTO = 1560;
const FPS = 24;
const SEGUNDOS = 11;
const CARPETA = '/tmp/p7/frames';
const PAGINA = 'file:///tmp/p7/chat.html';

const muestra = process.argv.includes('--muestra');

(async () => {
  fs.mkdirSync(CARPETA, { recursive: true });

  const navegador = await chromium.launch({
    executablePath: '/usr/bin/chromium',
    args: ['--no-sandbox', '--disable-dev-shm-usage', '--force-device-scale-factor=1'],
  });
  const pagina = await navegador.newPage({
    viewport: { width: ANCHO, height: ALTO },
    deviceScaleFactor: 1,
  });

  await pagina.goto(PAGINA, { waitUntil: 'load' });
  await pagina.waitForTimeout(600);

  // Si pintar() no existe, la pagina esta rota: mejor enterarse ahora que
  // despues de 264 capturas de una pantalla en blanco.
  const hay = await pagina.evaluate(() => typeof window.pintar === 'function');
  if (!hay) {
    await navegador.close();
    throw new Error('la pagina no expone window.pintar(t)');
  }

  const instantes = muestra
    ? [1.0, 5.0, 9.5]
    : Array.from({ length: SEGUNDOS * FPS }, (_, i) => i / FPS);

  let ultimo = null;
  for (let i = 0; i < instantes.length; i++) {
    const t = instantes[i];
    const estado = await pagina.evaluate((s) => window.pintar(s), t);
    const nombre = muestra
      ? path.join(CARPETA, 'muestra-' + t + '.png')
      : path.join(CARPETA, 'f' + String(i).padStart(4, '0') + '.png');
    await pagina.screenshot({ path: nombre });

    // Solo se informa cuando cambia algo, para no llenar la consola de ruido.
    const clave = estado.mensajes + '/' + estado.escribiendo;
    if (clave !== ultimo) {
      console.log('  t=' + t.toFixed(2) + 's  mensajes=' + estado.mensajes +
                  (estado.escribiendo ? '  escribiendo' : '') + '  scroll=' + estado.scroll);
      ultimo = clave;
    }
  }

  await navegador.close();
  console.log(muestra ? 'muestras en ' + CARPETA : instantes.length + ' fotogramas en ' + CARPETA);
})().catch((e) => {
  console.error('ERROR:', e.message);
  process.exit(1);
});
