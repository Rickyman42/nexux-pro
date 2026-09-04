import type { APIRoute } from 'astro';
import { getClientInvoices } from '../../lib/portal-client';

export const GET: APIRoute = async ({ request, cookies }) => {
  const token = cookies.get('nexux_token')?.value;
  const url = new URL(request.url);
  const clientId = url.searchParams.get('clientId');

  if (!token || !clientId) {
    return new Response(JSON.stringify({ ok: false, error: 'unauthorized' }), { status: 401 });
  }

  // ok:true significaba "la peticion llego", no "las facturas se han cargado".
  // Ahora dice la verdad: si la consulta fallo, el portal puede avisar en vez de
  // ensenar un "no tienes facturas" que no es cierto.
  const { ok, invoices } = await getClientInvoices(clientId, token);
  return new Response(JSON.stringify({ ok, invoices }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
};
