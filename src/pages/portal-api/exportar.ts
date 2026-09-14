import type { APIRoute } from "astro";
import { exportarDatos } from "../../lib/portal-client";

export const prerender = false;

/**
 * La descarga de los datos del salon.
 *
 * Pasa por aqui y no directamente a la Pi porque la sesion vive en una cookie de
 * nexux.pro: el navegador no se la mandaria a otro dominio. Aqui se cambia la
 * cookie por el token que entiende la Pi.
 *
 * No se limita por plan a proposito: las clientas son del salon, no nuestras.
 */
export const GET: APIRoute = async ({ request, cookies }) => {
  const token = cookies.get("nexux_token")?.value;
  if (!token) return new Response("no_auth", { status: 401 });

  const params = new URL(request.url).searchParams;
  const clientId = params.get("clientId") ?? "";
  const que = params.get("que") ?? "clientes";
  if (!clientId) return new Response("missing_client", { status: 400 });
  if (que !== "clientes" && que !== "citas") {
    return new Response("que_invalido", { status: 400 });
  }

  const result = await exportarDatos(clientId, token, que);
  if (!result.ok) {
    return new Response(result.error ?? "error", { status: result.status ?? 500 });
  }

  // El nombre del fichero lo decide la Pi, que es quien sabe como se llama el
  // salon. Se deja pasar tal cual para que en la carpeta de Descargas se vea
  // "clientes-peluqueria-lena-2026-09-14.csv" y no "exportar".
  return new Response(result.csv, {
    status: 200,
    headers: {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": result.disposition ?? 'attachment; filename="datos.csv"',
      "Cache-Control": "no-store",
    },
  });
};
