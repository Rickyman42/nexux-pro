import type { APIRoute } from "astro";

export const prerender = false;

const PI_URL = import.meta.env.NEXUX_CLIENTS_URL || "https://pi.nexux.pro";

export const POST: APIRoute = async ({ request }) => {
  const body = await request.json().catch(() => ({}));
  const { clientId, client_name, client_phone, service, datetime, duration_min } = body;

  if (!clientId || !service || !datetime) {
    return new Response(JSON.stringify({ ok: false, error: "missing_fields" }), {
      status: 400, headers: { "Content-Type": "application/json" },
    });
  }

  try {
    const resp = await fetch(`${PI_URL}/public/${clientId}/book`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ client_name, client_phone, service, datetime, duration_min }),
    });
    const data = await resp.json();
    return new Response(JSON.stringify(data), {
      status: resp.status, headers: { "Content-Type": "application/json" },
    });
  } catch (err) {
    return new Response(JSON.stringify({ ok: false, error: "forward_failed" }), {
      status: 502, headers: { "Content-Type": "application/json" },
    });
  }
};
