/**
 * conversa-rodaje.mjs — lanza una conversacion REAL contra el motor del bot,
 * sin ningun telefono de por medio.
 *
 * Usa handleMessage() de lib/whatsapp.js: el mismo prompt, la misma IA, el mismo
 * motor de reservas y el mismo evento de Google Calendar que cuando escribe una
 * persona. Lo unico distinto es que el socket de WhatsApp es de mentira y en vez
 * de enviar el mensaje lo apunta.
 *
 * Uso:
 *   node conversa-rodaje.mjs                          conversacion entera
 *   node conversa-rodaje.mjs --desde 2                empieza en el mensaje 2
 *   node conversa-rodaje.mjs --hasta 1                solo el primer mensaje
 *   node conversa-rodaje.mjs --tel 34600333444 --nombre "Marina Gil" --pausa 6000
 */
// Carga el .env. Sin esto, GOOGLE_OAUTH_CLIENT_ID vale undefined, Google
// contesta invalid_client y la cita se reserva en el CRM pero NO llega al
// calendario del negocio. Paso el 24-ago-2026 con un cliente real.
import 'dotenv/config';
import fs from 'fs';
import path from 'path';
import { handleMessage } from './lib/whatsapp.js';

const arg = (n, def) => {
  const i = process.argv.indexOf('--' + n);
  return i > -1 && process.argv[i + 1] ? process.argv[i + 1] : def;
};

const CLIENT = 'estudio-ricardo-demo-mostoles-946279';
const TEL = arg('tel', '34600111222');
const NOMBRE = arg('nombre', 'Lourdes Vidal');
const PAUSA = Number(arg('pausa', 1200));
const DESDE = Number(arg('desde', 1));
const HASTA = Number(arg('hasta', 99));
const JID = `${TEL}@s.whatsapp.net`;

const config = JSON.parse(
  fs.readFileSync(path.resolve('./clients', CLIENT, 'config.json'), 'utf8')
);

// Lo que dice el cliente. Corto y natural: es lo que se ve en pantalla.
const GUION = [
  'Hola, quería pedir cita para una manicura',
  '¿Te queda algo mañana por la tarde?',
  'Las seis me viene bien',
  NOMBRE,
  'Me da igual quién, la que tenga hueco',
  'Sí',
];

const transcripcion = [];

// Socket de mentira: cumple lo justo que handleMessage le pide.
const sock = {
  async sendMessage(_jid, contenido) {
    const texto = contenido?.text ?? '';
    transcripcion.push({ quien: 'Lara', texto });
    console.log('\n  LARA > ' + texto.replace(/\n/g, '\n         '));
  },
  async sendPresenceUpdate() {},
  user: { id: JID },
};

const espera = (ms) => new Promise((r) => setTimeout(r, ms));

console.log(`Negocio: ${config.name}`);
console.log(`Cliente: ${NOMBRE} (${TEL}) · mensajes ${DESDE}-${Math.min(HASTA, GUION.length)}`);
console.log('-'.repeat(60));

for (let i = DESDE; i <= Math.min(HASTA, GUION.length); i++) {
  const linea = GUION[i - 1];
  transcripcion.push({ quien: 'Cliente', texto: linea });
  console.log('\n  CLIENTE > ' + linea);
  try {
    await handleMessage(CLIENT, config, sock, JID, linea, NOMBRE);
  } catch (e) {
    console.error('\n  ERROR del motor:', e.message);
    break;
  }
  await espera(PAUSA);
}

console.log('\n' + '-'.repeat(60));

const apts = JSON.parse(
  fs.readFileSync(path.resolve('./clients', CLIENT, 'appointments.json'), 'utf8')
);
const nueva = apts.filter((a) => a.client_name === NOMBRE);
console.log(`Citas a nombre de ${NOMBRE}: ${nueva.length}`);
for (const a of nueva) {
  const h = new Date(a.datetime).toLocaleString('es-ES', {
    timeZone: 'Europe/Madrid', hour: '2-digit', minute: '2-digit',
    day: '2-digit', month: '2-digit',
  });
  console.log(`  ${h} · ${a.service} · ${a.professional_name}`);
}

fs.writeFileSync('/tmp/conversa-rodaje.json', JSON.stringify(transcripcion, null, 2));
