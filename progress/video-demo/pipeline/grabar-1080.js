const { chromium } = require('/home/nexux/nexux-campaign-ops/node_modules/.pnpm/playwright-core@1.60.0/node_modules/playwright-core');

(async () => {
  const b = await chromium.launch({
    executablePath: '/usr/bin/chromium',
    args: ['--no-sandbox', '--disable-gpu', '--hide-scrollbars'],
  });
  const ctx = await b.newContext({
    viewport: { width: 1920, height: 1080 },
    recordVideo: { dir: '/tmp/video-1080b', size: { width: 1920, height: 1080 } },
  });
  const page = await ctx.newPage();
  await page.goto('https://nexux.pro/demo?cb=' + Math.floor(Math.random() * 1e9), { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(4000);

  const input = page.locator('#msg-input');
  await input.waitFor({ state: 'visible', timeout: 45000 });
  await page.waitForTimeout(1500);

  const escribir = async (m, esperar = 9000) => {
    await input.click({ force: true });
    await input.type(m, { delay: 50 });
    await page.waitForTimeout(500);
    await page.keyboard.press('Enter');
    await page.waitForTimeout(esperar);
  };

  // El nombre se da al principio: asi no aparece en pantalla el hueco
  // "a nombre de ¿como te llamas?" que nos estropeo dos planos de la toma anterior.
  await escribir('Hola, soy Marta Ruiz. Teneis hueco manana para un corte?');
  await escribir('El lunes a las 11 me viene bien');
  await escribir('si', 12000);
  await page.waitForTimeout(4000);

  await ctx.close();
  await b.close();
  console.log('grabado 1080p');
})();
