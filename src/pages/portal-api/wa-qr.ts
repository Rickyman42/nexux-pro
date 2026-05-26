import type { APIRoute } from 'astro';

export const prerender = false;

const BASE_URL = import.meta.env.NEXUX_CLIENTS_URL || 'https://pi.nexux.pro';

export const GET: APIRoute = async ({ url, cookies }) => {
  const token = cookies.get('nexux_token')?.value;
  if (!token) {
    return new Response(JSON.stringify({ error: 'unauthorized' }), { status: 401 });
  }

  const clientId = url.searchParams.get('clientId');
  if (!clientId) {
    return new Response(JSON.stringify({ error: 'missing_client' }), { status: 400 });
  }

  try {
    const res = await fetch(`${BASE_URL}/client/${clientId}/wa-qr`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    return new Response(JSON.stringify(data), {
      status: res.ok ? 200 : res.status,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (err) {
    return new Response(JSON.stringify({ status: 'error' }), { status: 502 });
  }
};
