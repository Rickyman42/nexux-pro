/**
 * Plano 8 — la cita entrando sola en el calendario del negocio.
 *
 * Es el plano que sostiene la frase del guion: "Y la puso en tu agenda. Sola."
 * No se compone ni se simula: se graba el Google Calendar real de Centro Lena
 * mientras Lara mete la cita por el otro lado.
 *
 * Uso:  node grabar-calendario.cjs <segundos>
 */
const { chromium } = require('/home/nexux/nexux-campaign-ops/node_modules/.pnpm/playwright-core@1.60.0/node_modules/playwright-core');

const SRC = '465ab745da9b42aa1afe748493ea6a28657f5ada585838353be1c672eb36827a%40group.calendar.google.com';
const URL = `https://calendar.google.com/calendar/embed?src=${SRC}`
  + '&ctz=Europe%2FMadrid&hl=es&mode=AGENDA&showTitle=0&showPrint=0&showTabs=0'
  + '&showCalendars=0&showTz=0&showNav=0&showDate=0&dates=20260826%2F20260826';
const SEG = Number(process.argv[2] || 45);

(async () => {
  const b = await chromium.launch({
    executablePath: '/usr/bin/chromium',
    args: ['--no-sandbox', '--disable-gpu', '--hide-scrollbars'],
  });
  const ctx = await b.newContext({
    viewport: { width: 1280, height: 720 },
    deviceScaleFactor: 1,
    recordVideo: { dir: '/tmp/rec-cal-t2', size: { width: 1280, height: 720 } },
  });
  const page = await ctx.newPage();
  await page.goto(URL, { waitUntil: 'networkidle', timeout: 90000 });
  await page.waitForTimeout(4000);

  const texto = await page.evaluate(() => document.body.innerText.slice(0, 400));
  console.log('--- lo que se ve al empezar ---\n' + texto);

  // El embed no se refresca solo: se recarga cada pocos segundos para que la
  // cita nueva aparezca dentro de la toma.
  const fin = Date.now() + SEG * 1000;
  let vueltas = 0;
  while (Date.now() < fin) {
    await page.waitForTimeout(5000);
    await page.reload({ waitUntil: 'networkidle' });
    vueltas++;
  }
  console.log(`recargas durante la toma: ${vueltas}`);

  const final = await page.evaluate(() => document.body.innerText.slice(0, 600));
  console.log('--- lo que queda al final ---\n' + final);

  await ctx.close();
  await b.close();
  console.log('video en /tmp/rec-cal-t2/');
})();
