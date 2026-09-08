import type { APIRoute } from 'astro';
import { getOpcionesDePlan, cambiarDePlan } from '../../lib/portal-client';

function sinPermiso() {
  return new Response(JSON.stringify({ ok: false, error: 'unauthorized' }), { status: 401 });
}

export const GET: APIRoute = async ({ request, cookies }) => {
  const token = cookies.get('nexux_token')?.value;
  const clientId = new URL(request.url).searchParams.get('clientId');
  if (!token || !clientId) return sinPermiso();

  const { ok, datos } = await getOpcionesDePlan(clientId, token);
  return new Response(JSON.stringify({ ok, datos }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
};

export const POST: APIRoute = async ({ request, cookies }) => {
  const token = cookies.get('nexux_token')?.value;
  if (!token) return sinPermiso();

  let cuerpo: { clientId?: string; plan?: string } = {};
  try { cuerpo = await request.json(); } catch { /* cuerpo vacio */ }
  if (!cuerpo.clientId || !cuerpo.plan) return sinPermiso();

  // El estado de la Pi viaja tal cual: el portal no decide si esto ha ido bien.
  const r = await cambiarDePlan(cuerpo.clientId, token, cuerpo.plan);
  return new Response(JSON.stringify(r.cuerpo), {
    status: r.estado || 502,
    headers: { 'Content-Type': 'application/json' },
  });
};
