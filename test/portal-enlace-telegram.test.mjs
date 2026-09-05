// El boton "Conectar mi Telegram" del panel tiene que llevar el enlace de DUENO.
//
// Por que existe: hasta el 5-sept-2026 la pagina se fabricaba el enlace a mano con el
// clientId pelado. El 3-sept el bot dejo de dar permisos de dueno a un payload sin
// prefijo (era publico y con el se robaba el canal, hallazgo C-B1) y paso a atenderlo
// como CLIENTA. Nadie toco la pagina: el dueno que pulsaba el boton quedaba registrado
// como clienta de su propio salon, no recibia ni un aviso de cita, y el panel decia
// "No vinculado" para siempre. La Pi ya devolvia el enlace correcto y nadie lo leia.
//
// Se renderiza la PAGINA REAL contra una Pi de mentira, porque el fallo estaba en el
// HTML que se sirve, no en una funcion suelta: un test de unidad no lo habria visto.
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const RAIZ = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const BASE = JSON.parse(fs.readFileSync(path.join(RAIZ, "test/fixtures/status-portal.json"), "utf8"));
const P_PI = 3611, P_WEB = 3612;
const TOKEN = "token-de-prueba";

let servidorPi, web, telegramQueDevuelveLaPi;

// El panel NO sirve la pagina en la primera peticion: guarda el token en una cookie y
// redirige a la URL limpia, para que no quede en el historial ni se filtre por Referer.
// Sin arrastrar esa cookie a mano, la segunda peticion cae en el login y el test estaria
// midiendo la pagina equivocada; fetch no lleva tarro de cookies.
async function paginaDe(clientId) {
  const url = `http://127.0.0.1:${P_WEB}/cliente/${clientId}?t=${TOKEN}`;
  const r1 = await fetch(url, { redirect: "manual" });
  if (r1.status < 300 || r1.status >= 400) return r1.text();
  const cookie = (r1.headers.getSetCookie?.() || []).map(c => c.split(";")[0]).join("; ");
  const destino = new URL(r1.headers.get("location"), url).toString();
  const r2 = await fetch(destino, { headers: { cookie }, redirect: "manual" });
  return r2.text();
}

before(async () => {
  servidorPi = http.createServer((req, res) => {
    if (!req.url.includes("/status")) { res.statusCode = 404; return res.end("{}"); }
    const cuerpo = { ...BASE, channels: { ...BASE.channels, telegram: telegramQueDevuelveLaPi } };
    res.setHeader("Content-Type", "application/json");
    res.end(JSON.stringify(cuerpo));
  });
  await new Promise(r => servidorPi.listen(P_PI, "127.0.0.1", r));

  web = spawn("node", ["node_modules/astro/bin/astro.mjs", "dev", "--port", String(P_WEB)], {
    cwd: RAIZ,
    env: { ...process.env, NEXUX_CLIENTS_URL: `http://127.0.0.1:${P_PI}`, NODE_OPTIONS: "--max-old-space-size=1400" },
    stdio: "ignore",
  });
  const fin = Date.now() + 90000;
  while (Date.now() < fin) {
    try { const r = await fetch(`http://127.0.0.1:${P_WEB}/`); if (r.status) return; } catch {}
    await new Promise(r => setTimeout(r, 500));
  }
  throw new Error("el servidor de desarrollo no arranco");
});

after(() => { web?.kill("SIGKILL"); servidorPi?.close(); });

test("el boton de conectar lleva el enlace de DUENO que da la Pi", async () => {
  telegramQueDevuelveLaPi = BASE.channels.telegram;
  const html = await paginaDe("salon-de-prueba");
  assert.ok(html.includes("start=o_TOKENDEDUENODEPRUEBA"),
    "la pagina no sirve el enlace de dueno que devuelve la Pi");
});

test("no se fabrica el enlace con el id pelado, que entra como clienta", async () => {
  telegramQueDevuelveLaPi = BASE.channels.telegram;
  const html = await paginaDe("salon-de-prueba");
  assert.ok(!/start=salon-de-prueba(?![-\w])/.test(html),
    "sigue habiendo un enlace con el id pelado: quien lo pulse entra como clienta");
});

test("el enlace de clientas sigue siendo el de clientas", async () => {
  telegramQueDevuelveLaPi = BASE.channels.telegram;
  const html = await paginaDe("salon-de-prueba");
  assert.ok(html.includes("start=c_salon-de-prueba"), "falta el enlace para las clientas");
});

test("si la Pi no puede dar el enlace, no se pinta un boton roto", async () => {
  telegramQueDevuelveLaPi = { ...BASE.channels.telegram, ownerDeepLink: null };
  const html = await paginaDe("salon-de-prueba");
  assert.ok(!html.includes("Conectar mi Telegram"), "se pinta un boton que no lleva a ningun sitio");
  assert.ok(html.includes("Escribe a soporte"), "no se le dice al dueno que haga nada");
});
