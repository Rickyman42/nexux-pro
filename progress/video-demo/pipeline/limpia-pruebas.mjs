/**
 * Quita del calendario las citas de PRUEBA que fui creando al verificar la
 * cadena, para dejar libre el hueco de las 18:00 donde entra la cita del plano.
 * Solo borra las que llevan uno de estos nombres: son mias, de hoy, y no hay
 * ninguna otra cosa en este calendario.
 */
import 'dotenv/config';
import { tokenDeAcceso } from './lib/google-oauth.js';

const CLIENT = 'estudio-ricardo-demo-mostoles-946279';
const CAL = '465ab745da9b42aa1afe748493ea6a28657f5ada585838353be1c672eb36827a@group.calendar.google.com';
const DE_PRUEBA = ['Marta Ruiz', 'Alicia Bravo', 'Paula Rivas', 'Sara Beltran',
                   'Elena Cruz', 'Marina Gil', 'Lourdes Vidal', 'Nuria Solana', 'Elena Vidal', 'Clara Ortiz'];

const token = await tokenDeAcceso(CLIENT);
const base = `https://www.googleapis.com/calendar/v3/calendars/${encodeURIComponent(CAL)}/events`;
const desde = new Date(Date.now() - 2 * 864e5).toISOString();
const hasta = new Date(Date.now() + 7 * 864e5).toISOString();

const d = await (await fetch(
  `${base}?timeMin=${desde}&timeMax=${hasta}&singleEvents=true&maxResults=200`,
  { headers: { Authorization: `Bearer ${token}` } }
)).json();

const aBorrar = d.items.filter((e) =>
  DE_PRUEBA.some((n) => (e.summary || '').includes(n)));

console.log(`Citas de prueba encontradas: ${aBorrar.length}`);
for (const e of aBorrar) {
  const h = new Date(e.start.dateTime).toLocaleString('es-ES', {
    timeZone: 'Europe/Madrid', day: '2-digit', month: '2-digit',
    hour: '2-digit', minute: '2-digit',
  });
  const r = await fetch(`${base}/${e.id}`, {
    method: 'DELETE', headers: { Authorization: `Bearer ${token}` },
  });
  console.log(`  ${r.ok || r.status === 410 ? 'borrada' : 'FALLO'}  ${h} · ${e.summary}`);
}
// Y del CRM, que lee de appointments.json en la Pi — no de Google. Borrar solo en
// Google dejaba la cita a la vista en el panel del cliente.
import fs from 'fs';
const APT = `./clients/${CLIENT}/appointments.json`;
const antes = JSON.parse(fs.readFileSync(APT, 'utf8'));
const despues = antes.filter((a) => !DE_PRUEBA.some((n) => (a.client_name || '').includes(n)));
if (despues.length !== antes.length) {
  fs.writeFileSync(APT, JSON.stringify(despues, null, 2));
  console.log(`\nEn el CRM: ${antes.length} citas -> ${despues.length} (quitadas ${antes.length - despues.length} de prueba)`);
} else {
  console.log('\nEn el CRM no habia citas de prueba.');
}

console.log('\nEl hueco de las 18:00 queda libre para la cita del plano.');
