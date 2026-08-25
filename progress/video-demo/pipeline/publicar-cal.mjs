/**
 * Hace publico (solo lectura) el calendario del rodaje, para poder grabarlo
 * desde un navegador sin sesion.
 *
 * Es un calendario dedicado que solo contiene las citas montadas para el video:
 * ningun dato personal de Ricardo. Aun asi, publicar es publicar — lo pidio el.
 */
import 'dotenv/config';
import { tokenDeAcceso } from './lib/google-oauth.js';

const CLIENT = 'estudio-ricardo-demo-mostoles-946279';
const CAL = '465ab745da9b42aa1afe748493ea6a28657f5ada585838353be1c672eb36827a@group.calendar.google.com';
const token = await tokenDeAcceso(CLIENT);
const base = `https://www.googleapis.com/calendar/v3/calendars/${encodeURIComponent(CAL)}/acl`;

// Que permisos tenemos de verdad
const info = await fetch(
  `https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=${token}`
).then((r) => r.json());
console.log('Permisos del token:', info.scope || '(no los dice)');

console.log('\nHaciendo el calendario publico de solo lectura...');
const r = await fetch(base, {
  method: 'POST',
  headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
  body: JSON.stringify({ role: 'reader', scope: { type: 'default' } }),
});

if (!r.ok) {
  const t = await r.text();
  console.error(`FALLO ${r.status}: ${t.slice(0, 400)}`);
  console.error('\nSi dice insufficient permissions, el permiso concedido no llega');
  console.error('a cambiar quien ve el calendario. Lo tiene que hacer Ricardo a mano.');
  process.exit(1);
}
console.log('Regla creada:', JSON.stringify(await r.json()));

// Comprobarlo de verdad: sin credenciales, desde fuera
const ics = `https://calendar.google.com/calendar/ical/${encodeURIComponent(CAL)}/public/basic.ics`;
const c = await fetch(ics);
console.log(`\nComprobacion sin sesion: HTTP ${c.status}`);
console.log(c.ok ? 'ES PUBLICO: se puede grabar sin iniciar sesion.'
                 : 'Todavia no responde publico — puede tardar un momento en propagarse.');
