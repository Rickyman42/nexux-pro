/**
 * Prepara el cliente para el rodaje del vídeo:
 *   1. Renombra el negocio a "Centro Lena" (quita el "(DEMO)")
 *   2. Apunta el calendario de Google al calendario dedicado
 *   3. Siembra una agenda creíble del día y la sube a Google Calendar
 *      usando la MISMA función que usa el producto (createCalendarEvent),
 *      no una copia: lo que se graba es lo que hace el sistema de verdad.
 *
 * Uso:  node seed-agenda.mjs <CALENDAR_ID>        (aplica)
 *       node seed-agenda.mjs <CALENDAR_ID> --dry  (solo enseña qué haría)
 *
 * Revertir:  node seed-agenda.mjs --revert        (restaura las copias .rodaje-bak)
 */
import fs from 'fs';
import path from 'path';
import { createCalendarEvent, isCalendarConfigured } from './lib/calendar.js';

const CLIENT = 'estudio-ricardo-demo-mostoles-946279';
const DIR = path.resolve('./clients', CLIENT);
const CFG = path.join(DIR, 'config.json');
const APT = path.join(DIR, 'appointments.json');
const NOMBRE = 'Centro Lena';

const args = process.argv.slice(2);
const REVERT = args.includes('--revert');
const DRY = args.includes('--dry');
const CALENDAR_ID = args.find((a) => !a.startsWith('--'));

function backup(f) {
  const b = f + '.rodaje-bak';
  if (!fs.existsSync(b)) fs.copyFileSync(f, b);
  return b;
}

if (REVERT) {
  for (const f of [CFG, APT]) {
    const b = f + '.rodaje-bak';
    if (fs.existsSync(b)) { fs.copyFileSync(b, f); fs.unlinkSync(b); console.log('restaurado', path.basename(f)); }
    else console.log('sin copia que restaurar:', path.basename(f));
  }
  process.exit(0);
}

if (!CALENDAR_ID) { console.error('Falta el CALENDAR_ID. Uso: node seed-agenda.mjs <CALENDAR_ID>'); process.exit(1); }

const config = JSON.parse(fs.readFileSync(CFG, 'utf8'));

// El día del rodaje: hoy, en horario del negocio (Madrid = UTC+2 en agosto)
const HOY = new Date().toISOString().slice(0, 10);
const z = (hhmm) => `${HOY}T${String(Number(hhmm.slice(0, 2)) - 2).padStart(2, '0')}:${hhmm.slice(3)}:00.000Z`;

// Un lunes con trabajo, no imposible: 11 citas, parón de comida,
// y un hueco a las 18:00 — ahí es donde aterriza la cita que reserva Lara en el plano.
const DIA = [
  ['09:00', 'Corte',                 'pro_ana',     'Ana',    'Nuria Vega',       30],
  ['09:30', 'Tinte',                 'pro_marta',   'Marta',  'Carmen Solís',     90],
  ['10:00', 'Mechas',                'pro_lucia',   'Lucia',  'Beatriz Alarcón', 120],
  ['10:30', 'Corte y barba',         'pro_ana',     'Ana',    'Javier Peña',      45],
  ['11:30', 'Corte',                 'pro_ana',     'Ana',    'Rocío Ferrer',     30],
  ['12:00', 'Tratamiento de cabina', 'pro_noelia',  'Noelia', 'Silvia Herrán',    60],
  ['12:30', 'Corte',                 'pro_marta',   'Marta',  'Álvaro Sanz',      30],
  ['13:00', 'Corte',                 'pro_lucia',   'Lucia',  'Marina Cuesta',    30],
  ['16:00', 'Tinte',                 'pro_ana',     'Ana',    'Paula Nogales',    90],
  ['16:30', 'Corte y barba',         'pro_noelia',  'Noelia', 'Diego Rueda',      45],
  ['17:00', 'Corte',                 'pro_lucia',   'Lucia',  'Hugo Ramos',       30],
  ['17:15', 'Corte',                 'pro_marta',   'Marta',  'Lorena Bas',       30],
];

const slug = (s) => 'svc_' + s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/\s+/g, '_');
const ahora = new Date().toISOString();

const citas = DIA.map(([hora, servicio, proId, proNombre, cliente, dur], i) => ({
  id: `rodaje-${String(i + 1).padStart(2, '0')}-${Math.random().toString(16).slice(2, 10)}`,
  service_id: slug(servicio),
  service: servicio,
  professional_id: proId,
  professional_name: proNombre,
  assignment_mode: 'explicit',
  resource_allocations: servicio === 'Tratamiento de cabina' ? [{ resource_id: 'res_cabina_1', units: 1 }] : [],
  client_name: cliente,
  // sin client_phone a propósito: el número se vería al abrir el evento en el vídeo
  datetime: z(hora),
  duration_min: dur,
  status: 'confirmed',
  source: 'crm',
  source_event_id: '',
  version: 1,
  created_at: ahora,
  updated_at: ahora,
  reminder_24h_sent: false,
  reminder_1h_sent: false,
}));

console.log(`Negocio:   "${config.name}"  ->  "${NOMBRE}"`);
console.log(`Calendario: ${config.google_calendar?.calendarId}  ->  ${CALENDAR_ID}`);
console.log(`Citas:      ${JSON.parse(fs.readFileSync(APT, 'utf8')).length}  ->  ${citas.length}`);
console.log('');
for (const c of citas) {
  const h = new Date(c.datetime).toLocaleTimeString('es-ES', { timeZone: 'Europe/Madrid', hour: '2-digit', minute: '2-digit' });
  console.log(`  ${h}  [${c.professional_name}] ${c.service} — ${c.client_name}  (${c.duration_min} min)`);
}
console.log('\n  18:00  --- HUECO: aquí entra la cita que reserva Lara durante el rodaje ---\n');

if (DRY) { console.log('DRY RUN: no se ha tocado nada.'); process.exit(0); }

backup(CFG); backup(APT);
config.name = NOMBRE;
config.nombre = NOMBRE;
config.google_calendar = { ...(config.google_calendar || {}), enabled: true, calendarId: CALENDAR_ID };
fs.writeFileSync(CFG, JSON.stringify(config, null, 2));
fs.writeFileSync(APT, JSON.stringify(citas, null, 2));
console.log('config.json y appointments.json escritos (copias en *.rodaje-bak)');

if (!isCalendarConfigured(CLIENT, config)) {
  console.error('\nEL CALENDARIO NO ESTA CONFIGURADO: las citas NO se han subido a Google.');
  process.exit(2);
}

let ok = 0, fallo = 0;
for (const c of citas) {
  try { await createCalendarEvent(CLIENT, config, c); ok++; }
  catch (e) { fallo++; console.error('  fallo en', c.client_name, '-', e.message); }
}
console.log(`\nGoogle Calendar: ${ok} eventos creados, ${fallo} fallos.`);
process.exit(fallo ? 2 : 0);
