// Carga el .env. Sin esto, `process.env.GOOGLE_OAUTH_CLIENT_ID` vale undefined,
// Google contesta `invalid_client` y lib/google-oauth.js lo tomaba por una
// revocacion del cliente: dejo un cliente REAL sin calendario dos dias
// (24-ago-2026). El blindaje ya esta en google-oauth.js, pero un script que
// toca Google carga su entorno; no se apoya en que otro le tape el fallo.
import 'dotenv/config';
import { tokenDeAcceso } from './lib/google-oauth.js';

const CLIENT = 'estudio-ricardo-demo-mostoles-946279';
const CAL = '465ab745da9b42aa1afe748493ea6a28657f5ada585838353be1c672eb36827a@group.calendar.google.com';
const hoy = new Date().toISOString().slice(0, 10);
const token = await tokenDeAcceso(CLIENT);
const base = `https://www.googleapis.com/calendar/v3/calendars/${encodeURIComponent(CAL)}/events`;

const r = await fetch(`${base}?timeMin=${hoy}T00:00:00Z&timeMax=${hoy}T23:59:59Z&singleEvents=true&maxResults=100`,
  { headers: { Authorization: `Bearer ${token}` } });
const d = await r.json();
console.log(`Eventos a borrar: ${d.items.length}`);
let n = 0;
for (const e of d.items) {
  const del = await fetch(`${base}/${e.id}`, { method: 'DELETE', headers: { Authorization: `Bearer ${token}` } });
  if (del.ok || del.status === 410) n++;
  else console.error('  fallo borrando', e.summary, del.status);
}
console.log(`Borrados: ${n}`);
