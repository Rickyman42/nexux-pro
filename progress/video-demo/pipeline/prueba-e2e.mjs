/**
 * Prueba de punta a punta del calendario: que una cita reservada por Lara
 * llegue de verdad al Google Calendar del negocio.
 *
 * Leer el calendario no prueba nada — lo que estaba roto era ESCRIBIR.
 */
import 'dotenv/config';
import fs from 'fs';
import { tokenDeAcceso } from './lib/google-oauth.js';

const CLIENT = 'estudio-ricardo-demo-mostoles-946279';
const CAL = '465ab745da9b42aa1afe748493ea6a28657f5ada585838353be1c672eb36827a@group.calendar.google.com';
const NOMBRE = process.argv[2] || 'Prueba Calendario';

const apts = JSON.parse(
  fs.readFileSync(`./clients/${CLIENT}/appointments.json`, 'utf8')
);
const mias = apts.filter((a) => a.client_name === NOMBRE);
if (!mias.length) {
  console.log(`No hay ninguna cita a nombre de ${NOMBRE} en el CRM.`);
  process.exit(1);
}

console.log(`Citas en el CRM a nombre de ${NOMBRE}: ${mias.length}`);
for (const a of mias) {
  console.log('  ' + new Date(a.datetime).toLocaleString('es-ES', {
    timeZone: 'Europe/Madrid', day: '2-digit', month: '2-digit',
    hour: '2-digit', minute: '2-digit',
  }) + ` · ${a.service} · ${a.professional_name}`);
}

// Ahora: ¿estan en Google?
const token = await tokenDeAcceso(CLIENT);
const desde = new Date(Date.now() - 864e5).toISOString();
const hasta = new Date(Date.now() + 5 * 864e5).toISOString();
const url = `https://www.googleapis.com/calendar/v3/calendars/${encodeURIComponent(CAL)}/events`
  + `?timeMin=${desde}&timeMax=${hasta}&singleEvents=true&orderBy=startTime&maxResults=100`;

const r = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
if (!r.ok) {
  console.error('\nFALLO al leer Google:', r.status, (await r.text()).slice(0, 200));
  process.exit(2);
}
const d = await r.json();
const enGoogle = d.items.filter((e) => (e.summary || '').includes(NOMBRE));

console.log(`\nEventos en Google Calendar a nombre de ${NOMBRE}: ${enGoogle.length}`);
for (const e of enGoogle) {
  console.log('  ' + new Date(e.start.dateTime).toLocaleString('es-ES', {
    timeZone: 'Europe/Madrid', day: '2-digit', month: '2-digit',
    hour: '2-digit', minute: '2-digit',
  }) + ` · ${e.summary}`);
}

const bien = enGoogle.length >= mias.length;
console.log('\n' + (bien
  ? 'LA CADENA FUNCIONA: lo que reserva Lara llega al calendario del negocio.'
  : 'SIGUE ROTA: la cita esta en el CRM pero NO en el calendario.'));
process.exit(bien ? 0 : 3);
