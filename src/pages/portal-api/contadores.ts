import type { APIRoute } from 'astro';
import { getContadores } from '../../lib/portal-client';

/**
 * Los numeros del dashboard, y solo eso.
 *
 * El panel la llama cuando el negocio crea, mueve o cancela una cita, y cuando
 * vuelve a la pestana despues de un rato. No en bucle: sin esto habria que
 * recargar la pagina entera para ver el contador subir.
 */
export const GET: APIRoute = async ({ request, cookies }) => {
  const token = cookies.get('nexux_token')?.value;
  const clientId = new URL(request.url).searchParams.get('clientId');

  if (!token || !clientId) {
    return new Response(JSON.stringify({ ok: false, error: 'unauthorized' }), { status: 401 });
  }

  const contadores = await getContadores(clientId, token);
  if (!contadores) {
    // ok:false y ya. El panel deja los numeros como estaban en vez de poner
    // ceros: un cero inventado se lee como "no tienes citas".
    return new Response(JSON.stringify({ ok: false }), {
      status: 200,
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' },
    });
  }

  return new Response(JSON.stringify({ ok: true, ...contadores }), {
    status: 200,
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' },
  });
};
