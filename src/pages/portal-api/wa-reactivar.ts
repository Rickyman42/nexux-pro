import type { APIRoute } from 'astro';

export const prerender = false;

const BASE_URL = import.meta.env.NEXUX_CLIENTS_URL || 'https://pi.nexux.pro';

// Le devuelve otras 24 horas al cliente cuyo QR de WhatsApp caduco sin escanear.
// Sin esto habria que reactivarlo a mano en el servidor cada vez que alguien se queja.
export const POST: APIRoute = async ({ url, cookies }) => {
  const token = cookies.get('nexux_token')?.value;
  if (!token) {
    return new Response(JSON.stringify({ error: 'unauthorized' }), { status: 401 });
  }

  const clientId = url.searchParams.get('clientId');
  if (!clientId) {
    return new Response(JSON.stringify({ error: 'missing_client' }), { status: 400 });
  }

  try {
    const res = await fetch(`${BASE_URL}/client/${clientId}/whatsapp/reactivar`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    return new Response(JSON.stringify(data), {
      status: res.ok ? 200 : res.status,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (err) {
    return new Response(JSON.stringify({ ok: false, error: 'unreachable' }), { status: 502 });
  }
};
