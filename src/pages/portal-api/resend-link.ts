import type { APIRoute } from 'astro';
import { resendPortalLink } from '../../lib/portal-client';

export const prerender = false;

export const POST: APIRoute = async ({ request }) => {
  const body = await request.json().catch(() => ({}));
  const clientId = typeof body.clientId === 'string' ? body.clientId : '';
  const email = typeof body.email === 'string' ? body.email : '';

  if (clientId && email) {
    await resendPortalLink(clientId, email);
  }

  return new Response(
    JSON.stringify({ ok: true, message: 'Si el email es correcto, recibiras el enlace en breve.' }),
    {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    },
  );
};
