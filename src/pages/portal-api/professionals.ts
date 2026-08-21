import type { APIRoute } from "astro";
import { fetchProfessionals, saveProfessionals } from "../../lib/portal-client";

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
  const clientId = new URL(request.url).searchParams.get("clientId") ?? "";
  if (!clientId) return json({ ok: false, error: "missing_client" }, 400);
  const result = await fetchProfessionals(clientId, token);
  return json(result, result.ok ? 200 : 502);
};

export const POST: APIRoute = async ({ request, cookies }) => {
  const token = cookies.get("nexux_token")?.value;
  if (!token) return json({ ok: false, error: "unauthorized" }, 401);
  const body = await request.json().catch(() => ({}));
  const { clientId, mode, professionals } = body ?? {};
  if (!clientId) return json({ ok: false, error: "missing_client" }, 400);
  const result = await saveProfessionals(clientId, token, { mode, professionals });
  // El backend responde 409 cuando pasar a equipo rompería las citas ya
  // guardadas. Se propaga tal cual para poder explicarlo en pantalla.
  return json(result, result.ok ? 200 : result.status);
};
