import type { APIRoute } from 'astro';

const PI_TRACK_URL = 'https://pi.nexux.pro/track';
const SECRET = import.meta.env.PROVISION_SECRET || 'nexux-wa-trial-2026';

export const prerender = false;

export const POST: APIRoute = async ({ request }) => {
  let body: Record<string, unknown> = {};
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ ok: false }), { status: 400 });
  }

  // Fire-and-forget — never block the client
  fetch(PI_TRACK_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-provision-secret': SECRET,
    },
    body: JSON.stringify({ ...body, _ts: new Date().toISOString() }),
  }).catch(() => {});

  return new Response(JSON.stringify({ ok: true }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
};
