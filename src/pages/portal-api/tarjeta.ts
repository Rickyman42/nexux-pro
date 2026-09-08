import type { APIRoute } from 'astro';
import { llamarTarjeta } from '../../lib/portal-client';

export const POST: APIRoute = async ({ request, cookies }) => {
  const token = cookies.get('nexux_token')?.value;
  if (!token) {
    return new Response(JSON.stringify({ ok: false, error: 'unauthorized' }), { status: 401 });
  }

  let cuerpo: { clientId?: string; accion?: string; permisoId?: string } = {};
  try { cuerpo = await request.json(); } catch { /* cuerpo vacio */ }
  if (!cuerpo.clientId) {
    return new Response(JSON.stringify({ ok: false, error: 'unauthorized' }), { status: 401 });
  }

  const accion = cuerpo.accion === 'sesion' ? 'sesion' : 'guardar';
  const r = await llamarTarjeta(cuerpo.clientId, token, accion, { permisoId: cuerpo.permisoId });
  return new Response(JSON.stringify(r.cuerpo), {
    status: r.estado || 502,
    headers: { 'Content-Type': 'application/json' },
  });
};
