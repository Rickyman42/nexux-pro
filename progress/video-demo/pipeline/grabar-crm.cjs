/**
 * Plano 8 — la cita entrando sola EN NUESTRO CRM.
 *
 * Se graba nexux.pro/cliente/<id>, la pantalla de Citas: el sistema que vende el
 * anuncio. Google Calendar es donde el producto guarda las citas por dentro, un
 * detalle de implementacion que no tiene que salir en pantalla.
 *
 * La sesion se abre con ?t=<accessToken>, que es como funciona el enlace magico
 * del portal: sin contrasenas y sin tocar el correo de nadie.
 *
 * El CRM no se refresca solo. En vez de recargar la pagina — que deja un
 * parpadeo blanco horrible en video — se pulsa "Siguiente" y "Anterior", que
 * vuelve a pedir los datos sin repintar todo.
 *
 * Uso:  node grabar-crm.cjs <segundos>
 */
const { chromium } = require('/home/nexux/nexux-campaign-ops/node_modules/.pnpm/playwright-core@1.60.0/node_modules/playwright-core');

const CLIENTE = 'estudio-ricardo-demo-mostoles-946279';
const TOKEN = '65feb090c7a42f547b7538ea9f70ce887b8b87b00885a14584f9077d02ec7cba';
const URL = `https://nexux.pro/cliente/${CLIENTE}?t=${TOKEN}`;
const SEG = Number(process.argv[2] || 50);

(async () => {
  const b = await chromium.launch({
    executablePath: '/usr/bin/chromium',
    args: ['--no-sandbox', '--disable-gpu', '--hide-scrollbars'],
  });
  const ctx = await b.newContext({
    viewport: { width: 1280, height: 720 },
    deviceScaleFactor: 1,
    recordVideo: { dir: '/tmp/rec-crm2', size: { width: 1280, height: 720 } },
  });
  const page = await ctx.newPage();
  await page.goto(URL, { waitUntil: 'networkidle', timeout: 90000 });
  await page.waitForTimeout(3000);

  // Un navegador limpio entra por el asistente de configuracion y con el aviso
  // de cookies. Hay que quitarlos antes de que empiece el plano.
  for (const [texto, que] of [['Sólo necesarias', 'cookies'], ['Saltar', 'asistente']]) {
    try {
      await page.locator(`text=${texto}`).first().click({ timeout: 6000 });
      console.log(`  ${que}: descartado`);
      await page.waitForTimeout(1500);
    } catch (e) {
      console.log(`  ${que}: no aparecia`);
    }
  }
  await page.waitForTimeout(2500);

  // Bajar hasta el calendario y dejarlo encuadrado
  await page.evaluate(() => {
    const t = [...document.querySelectorAll('h2,h3')].find(
      (e) => (e.textContent || '').trim() === 'Citas'
    );
    if (t) t.scrollIntoView({ block: 'start' });
    window.scrollBy(0, -20);
  });
  await page.waitForTimeout(2500);

  const antes = await page.evaluate(() => document.body.innerText.slice(0, 200));
  console.log('--- al empezar ---\n' + antes.replace(/\n+/g, ' | '));

  const sig = page.locator('text=Siguiente').first();
  const ant = page.locator('text=Anterior').first();

  const fin = Date.now() + SEG * 1000;
  let refrescos = 0;
  while (Date.now() < fin) {
    await page.waitForTimeout(6000);
    try {
      await sig.click({ timeout: 4000 });
      await page.waitForTimeout(700);
      await ant.click({ timeout: 4000 });
      refrescos++;
    } catch (e) {
      console.log('  no se pudo refrescar:', e.message.slice(0, 60));
    }
  }
  console.log(`refrescos durante la toma: ${refrescos}`);

  const texto = await page.evaluate(() => document.body.innerText);
  console.log('--- sale la cita nueva? ---');
  console.log(texto.includes('Marta Ruiz') ? '  SI, "Marta Ruiz" esta en pantalla'
                                           : '  NO aparece todavia');

  await ctx.close();
  await b.close();
  console.log('video en /tmp/rec-crm2/');
})();
