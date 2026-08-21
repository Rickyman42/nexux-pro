import type { APIRoute } from "astro";
import { fetchAllAppointments, cancelAppointmentById, createAppointmentManual, updateAppointmentById } from "../../lib/portal-client";

export const prerender = false;

function unauth() {
  return new Response(JSON.stringify({ ok: false, error: "unauthorized" }), {
    status: 401, headers: { "Content-Type": "application/json" },
  });
}

export const GET: APIRoute = async ({ request, cookies }) => {
  const token = cookies.get("nexux_token")?.value;
  if (!token) return unauth();
  const url = new URL(request.url);
  const clientId = url.searchParams.get("clientId") ?? "";
  if (!clientId) return new Response(JSON.stringify({ ok: false, error: "missing_client" }), { status: 400, headers: { "Content-Type": "application/json" } });
  const appointments = await fetchAllAppointments(clientId, token);
  return new Response(JSON.stringify(appointments), { status: 200, headers: { "Content-Type": "application/json" } });
};

export const POST: APIRoute = async ({ request, cookies }) => {
  const token = cookies.get("nexux_token")?.value;
  if (!token) return unauth();
  const body = await request.json().catch(() => ({}));
  const { clientId, action, aptId, ...data } = body;
  if (!clientId) return new Response(JSON.stringify({ ok: false, error: "missing_client" }), { status: 400, headers: { "Content-Type": "application/json" } });

  if (action === "cancel") {
    const ok = await cancelAppointmentById(clientId, token, aptId);
    return new Response(JSON.stringify({ ok }), { status: ok ? 200 : 502, headers: { "Content-Type": "application/json" } });
  }

  if (action === "update") {
    if (!aptId) return new Response(JSON.stringify({ ok: false, error: "missing_appointment" }), { status: 400, headers: { "Content-Type": "application/json" } });
    const result = await updateAppointmentById(clientId, token, aptId, data);
    return new Response(JSON.stringify(result), { status: result.ok ? 200 : result.status, headers: { "Content-Type": "application/json" } });
  }

  // create
  const ok = await createAppointmentManual(clientId, token, data);
  return new Response(JSON.stringify({ ok }), { status: ok ? 200 : 502, headers: { "Content-Type": "application/json" } });
};
