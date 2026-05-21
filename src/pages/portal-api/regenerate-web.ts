import type { APIRoute } from 'astro';
import { regenerateWeb } from '../../lib/portal-client';

export const prerender = false;

export const POST: APIRoute = async ({ request, cookies }) => {
  const token = cookies.get('nexux_token')?.value;
  if (!token) return new Response(JSON.stringify({ ok: false, error: 'unauthorized' }), { status: 401, headers: { 'Content-Type': 'application/json' } });

  const body = await request.json().catch(() => ({})) as { clientId?: string };
  if (!body.clientId) return new Response(JSON.stringify({ ok: false, error: 'missing_client' }), { status: 400, headers: { 'Content-Type': 'application/json' } });

  const result = await regenerateWeb(body.clientId, token);
  return new Response(JSON.stringify(result), { status: result.ok ? 200 : 502, headers: { 'Content-Type': 'application/json' } });
};
