import type { APIRoute } from "astro";
import { fetchCustomers, fetchCustomer, saveCustomer } from "../../lib/portal-client";

export const prerender = false;

function json(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

export const GET: APIRoute = async ({ request, cookies }) => {
  const token = cookies.get("nexux_token")?.value;
  if (!token) return json({ ok: false, error: "unauthorized" }, 401);

  const params = new URL(request.url).searchParams;
  const clientId = params.get("clientId") ?? "";
  if (!clientId) return json({ ok: false, error: "missing_client" }, 400);

  // Con telefono devuelve la ficha completa; sin el, la lista.
  const phone = params.get("phone");
  const result = phone
    ? await fetchCustomer(clientId, token, phone)
    : await fetchCustomers(clientId, token);

  // El 403 del backend (plan que no lo incluye) se propaga tal cual para poder
  // explicarlo en pantalla en vez de mostrar un error generico.
  return json(result, result.ok ? 200 : result.status);
};

export const PUT: APIRoute = async ({ request, cookies }) => {
  const token = cookies.get("nexux_token")?.value;
  if (!token) return json({ ok: false, error: "unauthorized" }, 401);

  const body = await request.json().catch(() => ({}));
  const { clientId, phone, nota, preferencias } = body ?? {};
  if (!clientId || !phone) return json({ ok: false, error: "missing_fields" }, 400);

  const result = await saveCustomer(clientId, token, phone, { nota, preferencias });
  return json(result, result.ok ? 200 : result.status);
};
