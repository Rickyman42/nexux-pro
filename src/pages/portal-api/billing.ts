import type { APIRoute } from 'astro';

/**
 * Esta ruta abria el portal de Stripe, donde cancelar la suscripcion eran dos
 * clics. La cancelacion dejo de ser autoservicio el 8-sep-2026: quien quiera
 * irse habla con soporte y decide Ricardo.
 *
 * Se deja respondiendo, y no borrada, porque puede haber alguna pestana vieja
 * abierta apuntando aqui. Contesta con lo que hay que hacer, no con un error
 * seco que dejaria al dueno sin saber a donde ir.
 */
export const GET: APIRoute = async () =>
  new Response(
    JSON.stringify({
      ok: false,
      error: 'portal_retirado',
      mensaje: 'Todo lo de tu suscripción se hace ya dentro de Nexux. Si quieres cancelar, escríbenos a soporte y lo vemos contigo.',
    }),
    { status: 410, headers: { 'Content-Type': 'application/json' } },
  );
