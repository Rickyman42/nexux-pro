const { chromium } = require('/home/nexux/nexux-campaign-ops/node_modules/.pnpm/playwright-core@1.60.0/node_modules/playwright-core');
(async () => {
  const b = await chromium.launch({ executablePath: '/usr/bin/chromium', args: ['--no-sandbox','--disable-gpu','--hide-scrollbars'] });
  const ctx = await b.newContext({
    viewport: { width: 1280, height: 720 },
    recordVideo: { dir: '/tmp/video-demo', size: { width: 1280, height: 720 } },
  });
  const page = await ctx.newPage();
  await page.goto('https://nexux.pro/demo?cb=' + Math.floor(Math.random()*1e9), { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(4000);

  const input = page.locator('#msg-input');
  await input.waitFor({ state: 'visible', timeout: 45000 });
  await page.waitForTimeout(2000);

  // Se escribe letra a letra: en video se nota, y da sensacion de persona escribiendo
  const escribir = async (m, esperar = 9000) => {
    await input.click({ force: true });
    await input.type(m, { delay: 55 });
    await page.waitForTimeout(600);
    await page.keyboard.press('Enter');
    await page.waitForTimeout(esperar);
  };

  await escribir('Hola, tenéis hueco mañana para un corte?');
  await escribir('El lunes a las 11 me viene bien');
  await escribir('Me llamo Marta Ruiz');
  await escribir('sí', 12000);
  await page.waitForTimeout(5000);   // unos segundos mirando la cita ya puesta en la agenda

  await ctx.close();
  await b.close();
  console.log('grabacion terminada');
})();
