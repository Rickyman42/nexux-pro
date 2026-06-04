import type { APIRoute } from 'astro';

export const prerender = false;

const PI_URL = import.meta.env.NEXUX_CLIENTS_URL || 'https://pi.nexux.pro';

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
