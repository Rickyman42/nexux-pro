import type { APIRoute } from 'astro';
import { reportMissedCall } from '../../lib/portal-client';

export const prerender = false;

export const POST: APIRoute = async ({ request, cookies }) => {
  const token = cookies.get('nexux_token')?.value;
  if (!token) return new Response(JSON.stringify({ ok: false, error: 'unauthorized' }), { status: 401, headers: { 'Content-Type': 'application/json' } });

  const body = await request.json().catch(() => ({})) as { clientId?: string; phone?: string };
  if (!body.clientId || !body.phone) return new Response(JSON.stringify({ ok: false, error: 'missing_params' }), { status: 400, headers: { 'Content-Type': 'application/json' } });

  const result = await reportMissedCall(body.clientId, token, body.phone);
  return new Response(JSON.stringify(result), { status: result.ok ? 200 : 502, headers: { 'Content-Type': 'application/json' } });
};
