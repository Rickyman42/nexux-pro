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
// Carga el .env. Sin esto, `process.env.GOOGLE_OAUTH_CLIENT_ID` vale undefined,
// Google contesta `invalid_client` y lib/google-oauth.js lo tomaba por una
// revocacion del cliente: dejo un cliente REAL sin calendario dos dias
// (24-ago-2026). El blindaje ya esta en google-oauth.js, pero un script que
// toca Google carga su entorno; no se apoya en que otro le tape el fallo.
import 'dotenv/config';
import { createCalendarEvent, isCalendarConfigured } from './lib/calendar.js';

const CLIENT = 'estudio-ricardo-demo-mostoles-946279';
const DIR = path.resolve('./clients', CLIENT);
const CFG = path.join(DIR, 'config.json');
const APT = path.join(DIR, 'appointments.json');
const NOMBRE = 'Centro Lena';

const args = process.argv.slice(2);
const REVERT = args.includes('--revert');
const DRY = args.includes('--dry');
const iDia = args.indexOf('--dia');
const CALENDAR_ID = args.find((a, n) => !a.startsWith('--') && !(iDia > -1 && n === iDia + 1));

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
// El dia de la agenda. Por defecto hoy, pero se puede pedir otro con --dia:
// grabar el plano 8 al final de la tarde exige sembrar el dia siguiente,
// porque a las 19:00 ya no quedan huecos que Lara pueda ofrecer.
const HOY = (() => {
  const i = process.argv.indexOf('--dia');
  return i > -1 && process.argv[i + 1]
    ? process.argv[i + 1]
    : new Date().toISOString().slice(0, 10);
})();
const z = (hhmm) => `${HOY}T${String(Number(hhmm.slice(0, 2)) - 2).padStart(2, '0')}:${hhmm.slice(3)}:00.000Z`;

// La agenda se elige segun el horario que tenga el negocio ESE dia. Estaba
// escrita a mano para una jornada de 09:00 a 19:00 con el hueco a las 18:00;
// sembrada un sabado --que Centro Lena cierra a las 14:00-- daba citas y un
// hueco fuera de horario, y Lara no ofreceria nunca las 18:00 de un sabado.
const DIAS_EN = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
const cierre = (() => {
  const dia = DIAS_EN[new Date(HOY + 'T12:00:00Z').getUTCDay()];
  const h = (config.schedule || {})[dia];
  if (!h) {
    console.error(`\n  ${HOY} es ${dia}: el negocio CIERRA. Siembra otro dia con --dia AAAA-MM-DD.`);
    process.exit(1);
  }
  return h.close;
})();

// Jornada completa: 12 citas, paron de comida y el hueco a las 18:00.
const DIA_LARGO = [
  ['09:00', 'Manicura',                 'pro_ana',    'Ana',    'Nuria Vega',       45],
  ['09:30', 'Tratamiento facial',       'pro_marta',  'Marta',  'Carmen Solís',     60],
  ['10:00', 'Tratamiento corporal',     'pro_lucia',  'Lucia',  'Beatriz Alarcón',  75],
  ['10:30', 'Depilación',               'pro_noelia', 'Noelia', 'Javier Peña',      30],
  ['11:00', 'Manicura',                 'pro_ana',    'Ana',    'Rocío Ferrer',     45],
  ['11:30', 'Masaje descontracturante', 'pro_marta',  'Marta',  'Silvia Herrán',    60],
  ['12:30', 'Primera consulta',         'pro_noelia', 'Noelia', 'Álvaro Sanz',      30],
  ['13:00', 'Depilación',               'pro_lucia',  'Lucia',  'Marina Cuesta',    30],
  ['16:00', 'Tratamiento facial',       'pro_ana',    'Ana',    'Paula Nogales',    60],
  ['16:30', 'Manicura',                 'pro_noelia', 'Noelia', 'Diego Rueda',      45],
  ['17:00', 'Primera consulta',         'pro_lucia',  'Lucia',  'Hugo Ramos',       30],
  ['17:15', 'Depilación',               'pro_marta',  'Marta',  'Lorena Bas',       30],
];

// Media jornada (sabado, cierre a las 14:00): 8 citas seguidas y el hueco a las
// 12:30: una manicura de 45 min acaba a las 13:15, antes del cierre. A las 13:00
// no valia: Lara ofrecia entonces las 13:30 y la reserva se caia por horario.
const DIA_CORTO = [
  ['09:00', 'Manicura',                 'pro_ana',    'Ana',    'Nuria Vega',       45],
  ['09:30', 'Tratamiento facial',       'pro_marta',  'Marta',  'Carmen Solís',     60],
  ['10:00', 'Depilación',               'pro_noelia', 'Noelia', 'Javier Peña',      30],
  ['10:30', 'Tratamiento corporal',     'pro_lucia',  'Lucia',  'Beatriz Alarcón',  75],
  ['11:00', 'Manicura',                 'pro_ana',    'Ana',    'Rocío Ferrer',     45],
  ['11:30', 'Masaje descontracturante', 'pro_marta',  'Marta',  'Silvia Herrán',    60],
  ['12:00', 'Primera consulta',         'pro_noelia', 'Noelia', 'Álvaro Sanz',      30],
];

const MEDIA = cierre <= '15:00';
const DIA = MEDIA ? DIA_CORTO : DIA_LARGO;
const HUECO = MEDIA ? '12:30' : '18:00';

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

console.log(`Dia:        ${HOY}  (cierra a las ${cierre} -> jornada ${MEDIA ? 'de media manana' : 'completa'})`);
console.log(`Negocio:   "${config.name}"  ->  "${NOMBRE}"`);
console.log(`Calendario: ${config.google_calendar?.calendarId}  ->  ${CALENDAR_ID}`);
console.log(`Citas:      ${JSON.parse(fs.readFileSync(APT, 'utf8')).length}  ->  ${citas.length}`);
console.log('');
for (const c of citas) {
  const h = new Date(c.datetime).toLocaleTimeString('es-ES', { timeZone: 'Europe/Madrid', hour: '2-digit', minute: '2-digit' });
  console.log(`  ${h}  [${c.professional_name}] ${c.service} — ${c.client_name}  (${c.duration_min} min)`);
}
console.log(`\n  ${HUECO}  --- HUECO: aquí entra la cita que reserva Lara durante el rodaje ---\n`);

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
