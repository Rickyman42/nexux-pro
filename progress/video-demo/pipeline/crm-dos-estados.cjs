/**
 * Plano 8 — captura el CRM antes y despues de que entre la cita.
 *
 * Los botones de semana no responden al clic desde el navegador automatico, y
 * recargar deja un parpadeo blanco que en video se lee como un fallo. Asi que se
 * capturan los dos estados REALES y el corte se hace en el montaje: nada
 * simulado, solo sin el repintado del navegador por medio.
 *
 * Uso:  node crm-dos-estados.cjs <antes|despues>
 */
const { chromium } = require('/home/nexux/nexux-campaign-ops/node_modules/.pnpm/playwright-core@1.60.0/node_modules/playwright-core');

const CLIENTE = 'estudio-ricardo-demo-mostoles-946279';
const TOKEN = '65feb090c7a42f547b7538ea9f70ce887b8b87b00885a14584f9077d02ec7cba';
const URL = `https://nexux.pro/cliente/${CLIENTE}?t=${TOKEN}`;
const FASE = process.argv[2] || 'antes';

(async () => {
  const b = await chromium.launch({
    executablePath: '/usr/bin/chromium',
    args: ['--no-sandbox', '--disable-gpu', '--hide-scrollbars'],
  });
  const p = await b.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 2 });
  await p.goto(URL, { waitUntil: 'networkidle', timeout: 90000 });
  await p.waitForTimeout(2500);

  for (const t of ['Sólo necesarias', 'Saltar']) {
    try { await p.locator(`text=${t}`).first().click({ timeout: 6000 }); await p.waitForTimeout(1200); }
    catch (e) { /* puede no estar */ }
  }
  await p.waitForTimeout(2500);

  // El CRM abre en el Dashboard. El calendario esta en la seccion Citas, que es
  // un boton .crm-nav-btn con data-view="citas" — no un enlace, y su texto lleva
  // icono, por eso fallaba buscarlo por texto exacto.
  try {
    await p.click('button.crm-nav-btn[data-view="citas"]', { timeout: 8000 });
    console.log('  seccion Citas: abierta');
    await p.waitForTimeout(3500);
  } catch (e) {
    console.log('  no se pudo abrir Citas:', e.message.slice(0, 60));
  }

  // Alejar la pagina hasta que la fila de las 18:00 entre en pantalla
  await p.evaluate(() => { document.body.style.zoom = '0.74'; });
  await p.waitForTimeout(1500);
  await p.evaluate(() => window.scrollTo(0, 0));
  await p.waitForTimeout(1200);

  // Donde cae la fila de las 18:00, para poder recortar el encuadre despues
  const marco = await p.evaluate(() => {
    const celda = [...document.querySelectorAll('*')].find(
      (e) => e.children.length === 0 && (e.textContent || '').trim() === '18:00');
    const tarjeta = document.querySelector('.crm-cal, .crm-card, section');
    return {
      y18: celda ? Math.round(celda.getBoundingClientRect().top) : null,
      alto: document.documentElement.scrollHeight,
    };
  });
  console.log('  fila de las 18:00 en y=' + marco.y18 + '  (pagina de ' + marco.alto + ')');

  await p.screenshot({ path: `/tmp/crm-${FASE}.png` });

  const texto = await p.evaluate(() => document.body.innerText);
  const hay = texto.includes('Elena Vidal');
  console.log(`fase=${FASE}   "Elena Vidal" en pantalla: ${hay ? 'SI' : 'NO'}`);
  if (FASE === 'antes' && hay) console.log('  OJO: el hueco no esta libre, la toma no valdria');
  if (FASE === 'despues' && !hay) console.log('  OJO: la cita no ha llegado al CRM');

  await b.close();
})();
