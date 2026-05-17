import type { APIRoute } from 'astro';
import { updateClientConfig } from '../../../lib/portal-client';

export const prerender = false;

export const POST: APIRoute = async ({ request, cookies }) => {
  const token = cookies.get('nexux_token')?.value;
  if (!token) {
    return new Response(JSON.stringify({ ok: false, error: 'unauthorized' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const body = await request.json().catch(() => ({}));
  const clientId = typeof body.clientId === 'string' ? body.clientId : '';
  const config = body.config ?? {};

  if (!clientId) {
    return new Response(JSON.stringify({ ok: false, error: 'missing_client' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' },
    });
  }

  const ok = await updateClientConfig(clientId, token, config);
  return new Response(JSON.stringify({ ok }), {
    status: ok ? 200 : 502,
    headers: { 'Content-Type': 'application/json' },
  });
};
