const { chromium } = require('/home/nexux/nexux-campaign-ops/node_modules/.pnpm/playwright-core@1.60.0/node_modules/playwright-core');

// Graba la conversacion en formato movil, para insertarla DENTRO del telefono que
// genere Flow. Es la pantalla real del producto: lo unico que no se puede generar.
(async () => {
  const b = await chromium.launch({
    executablePath: '/usr/bin/chromium',
    args: ['--no-sandbox', '--disable-gpu', '--hide-scrollbars'],
  });
  const ctx = await b.newContext({
    viewport: { width: 440, height: 956 },
    deviceScaleFactor: 2,
    isMobile: true,
    hasTouch: true,
    recordVideo: { dir: '/tmp/video-vertical', size: { width: 440, height: 956 } },
  });
  const page = await ctx.newPage();
  await page.goto('https://nexux.pro/demo?cb=' + Math.floor(Math.random() * 1e9), { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(4000);

  const input = page.locator('#msg-input');
  await input.waitFor({ state: 'visible', timeout: 45000 });
  await page.waitForTimeout(1200);

  const escribir = async (m, esperar = 9000) => {
    await input.click({ force: true });
    await input.type(m, { delay: 55 });
    await page.waitForTimeout(500);
    await page.keyboard.press('Enter');
    await page.waitForTimeout(esperar);
  };

  await escribir('Hola, soy Marta Ruiz. Teneis hueco manana para un corte?');
  await escribir('El lunes a las 11 me viene bien');
  await escribir('si', 11000);
  await page.waitForTimeout(3500);

  await ctx.close();
  await b.close();
  console.log('vertical grabado');
})();
