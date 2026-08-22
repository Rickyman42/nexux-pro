import type { APIRoute } from "astro";
import { fetchResources, saveResources } from "../../lib/portal-client";

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
  const result = await fetchResources(clientId, token);
  return json(result, result.ok ? 200 : 502);
};

export const POST: APIRoute = async ({ request, cookies }) => {
  const token = cookies.get("nexux_token")?.value;
  if (!token) return json({ ok: false, error: "unauthorized" }, 401);
  const body = await request.json().catch(() => ({}));
  const { clientId, resources, requirements } = body ?? {};
  if (!clientId) return json({ ok: false, error: "missing_client" }, 400);
  const result = await saveResources(clientId, token, { resources, requirements });
  return json(result, result.ok ? 200 : result.status);
};
