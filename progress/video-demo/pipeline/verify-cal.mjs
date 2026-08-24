import { tokenDeAcceso } from './lib/google-oauth.js';

const CLIENT = 'estudio-ricardo-demo-mostoles-946279';
const CAL = '465ab745da9b42aa1afe748493ea6a28657f5ada585838353be1c672eb36827a@group.calendar.google.com';

const hoy = new Date().toISOString().slice(0, 10);
const token = await tokenDeAcceso(CLIENT);

const url = `https://www.googleapis.com/calendar/v3/calendars/${encodeURIComponent(CAL)}/events`
  + `?timeMin=${hoy}T00:00:00Z&timeMax=${hoy}T23:59:59Z&singleEvents=true&orderBy=startTime&maxResults=50`;

const r = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
if (!r.ok) { console.error('HTTP', r.status, (await r.text()).slice(0, 300)); process.exit(1); }
const d = await r.json();

console.log(`EVENTOS EN EL CALENDARIO HOY: ${d.items.length}\n`);
let conTelefono = 0;
for (const e of d.items) {
  const h = new Date(e.start.dateTime).toLocaleTimeString('es-ES', { timeZone: 'Europe/Madrid', hour: '2-digit', minute: '2-digit' });
  const f = new Date(e.end.dateTime).toLocaleTimeString('es-ES', { timeZone: 'Europe/Madrid', hour: '2-digit', minute: '2-digit' });
  console.log(`  ${h}-${f}  ${e.summary}`);
  if ((e.description || '').includes('Teléfono')) conTelefono++;
}
console.log(`\nCon teléfono visible: ${conTelefono} (tiene que ser 0)`);
const dieciocho = d.items.some((e) => new Date(e.start.dateTime).toLocaleTimeString('es-ES', { timeZone: 'Europe/Madrid', hour: '2-digit', minute: '2-digit' }) === '18:00');
console.log(`Hueco de las 18:00 libre: ${dieciocho ? 'NO — hay algo ocupandolo' : 'SI'}`);
console.log('\n--- DESCRIPCION DE UN EVENTO, tal cual se lee al abrirlo ---');
console.log(d.items[0]?.description);
