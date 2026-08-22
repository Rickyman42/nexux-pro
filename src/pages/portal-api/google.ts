import type { APIRoute } from "astro";
import { googleStatus, googleConnectUrl, googleSetCalendar, googleDisconnect } from "../../lib/portal-client";

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
  const url = new URL(request.url);
  const clientId = url.searchParams.get("clientId") ?? "";
  if (!clientId) return json({ ok: false, error: "missing_client" }, 400);

  if (url.searchParams.get("action") === "connect") {
    const result = await googleConnectUrl(clientId, token);
    return json(result, result.ok ? 200 : 502);
  }
  const result = await googleStatus(clientId, token);
  return json(result, result.ok ? 200 : 502);
};

export const POST: APIRoute = async ({ request, cookies }) => {
  const token = cookies.get("nexux_token")?.value;
  if (!token) return json({ ok: false, error: "unauthorized" }, 401);
  const body = await request.json().catch(() => ({}));
  const { clientId, action, calendarId, activo } = body ?? {};
  if (!clientId) return json({ ok: false, error: "missing_client" }, 400);

  if (action === "disconnect") {
    const result = await googleDisconnect(clientId, token);
    return json(result, result.ok ? 200 : 502);
  }
  const result = await googleSetCalendar(clientId, token, { calendarId, activo });
  return json(result, result.ok ? 200 : 502);
};
