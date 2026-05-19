import type { APIRoute } from 'astro';
import { getClientInvoices } from '../../lib/portal-client';

export const GET: APIRoute = async ({ request, cookies }) => {
  const token = cookies.get('nexux_token')?.value;
  const url = new URL(request.url);
  const clientId = url.searchParams.get('clientId');

  if (!token || !clientId) {
    return new Response(JSON.stringify({ ok: false, error: 'unauthorized' }), { status: 401 });
  }

  const invoices = await getClientInvoices(clientId, token);
  return new Response(JSON.stringify({ ok: true, invoices }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
};
