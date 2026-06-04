import type { APIRoute } from 'astro';

export const prerender = false;

// Apunta directo al endpoint público de provisioning (provision-http :3460 vía
// Cloudflare). NO usamos NEXUX_CLIENTS_URL porque en este proyecto apunta a un
// endpoint con whitelist antigua que rechaza el plan "promo".
const PI_URL = 'https://pi.nexux.pro';

// Forwards the embedded-checkout session request to the Pi (which holds the
// Stripe secret key + price IDs) and returns { clientSecret } to the browser.
export const POST: APIRoute = async ({ request }) => {
  const body = await request.text();
  const origin = request.headers.get('origin') || 'https://nexux.pro';
  try {
    const resp = await fetch(`${PI_URL}/api/stripe/create-session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', origin },
      body,
    });
    const data = await resp.text();
    return new Response(data, {
      status: resp.status,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (err) {
    console.error('[create-session] forward error:', err);
    return new Response(JSON.stringify({ error: 'forward_failed' }), {
      status: 502,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};

export const GET: APIRoute = async () => {
  let upstream = '';
  try {
    const r = await fetch(`${PI_URL}/api/stripe/create-session`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ plan: 'promo' }) });
    upstream = r.status + ':' + (await r.text()).slice(0, 70);
  } catch (e) { upstream = 'ERR:' + String(e).slice(0, 70); }
  return new Response(JSON.stringify({ piUrl: PI_URL, upstream, build: 'v2-debug' }), { headers: { 'Content-Type': 'application/json' } });
};
