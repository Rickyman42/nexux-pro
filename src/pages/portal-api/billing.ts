import type { APIRoute } from "astro";
import { getBillingPortalUrl } from "../../lib/portal-client";

export const prerender = false;

export const GET: APIRoute = async ({ request, cookies }) => {
  const token = cookies.get("nexux_token")?.value;
  if (!token) {
    return new Response(JSON.stringify({ ok: false, error: "unauthorized" }), {
      status: 401, headers: { "Content-Type": "application/json" },
    });
  }
  const url = new URL(request.url);
  const clientId = url.searchParams.get("clientId") ?? "";
  if (!clientId) {
    return new Response(JSON.stringify({ ok: false, error: "missing_client" }), {
      status: 400, headers: { "Content-Type": "application/json" },
    });
  }

  const portalUrl = await getBillingPortalUrl(clientId, token);
  if (!portalUrl) {
    return new Response(JSON.stringify({ ok: false, error: "billing_unavailable" }), {
      status: 502, headers: { "Content-Type": "application/json" },
    });
  }

  return new Response(JSON.stringify({ ok: true, url: portalUrl }), {
    status: 200, headers: { "Content-Type": "application/json" },
  });
};
