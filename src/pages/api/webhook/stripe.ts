import type { APIRoute } from "astro";

export const prerender = false;

const PI_URL = import.meta.env.NEXUX_CLIENTS_URL || "https://pi.nexux.pro";

export const POST: APIRoute = async ({ request }) => {
  const rawBody = await request.text();
  const sigHeader = request.headers.get("stripe-signature") ?? "";

  try {
    const resp = await fetch(`${PI_URL}/webhook/stripe`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "stripe-signature": sigHeader,
      },
      body: rawBody,
    });
    const data = await resp.json();
    return new Response(JSON.stringify(data), {
      status: resp.status,
      headers: { "Content-Type": "application/json" },
    });
  } catch (err) {
    console.error("[stripe-webhook] forward error:", err);
    return new Response(JSON.stringify({ error: "forward_failed" }), {
      status: 502,
      headers: { "Content-Type": "application/json" },
    });
  }
};
