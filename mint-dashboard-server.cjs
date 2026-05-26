#!/usr/bin/env node
/**
 * Nexux Pro — Mint Control Dashboard (no-build, single-node server)
 * - Serves a static dashboard UI
 * - Aggregates Mint data (CSV on Pi + JSON logs on Mint node) into simple APIs
 *
 * Run (on Pi):
 *   node /home/nexux/nexux-pro/mint-dashboard-server.cjs
 *
 * Env (optional):
 *   DASHBOARD_PORT=3700
 *   DASHBOARD_HOST=0.0.0.0
 *   LEADS_DIR=/home/nexux/scraper-output
 *   LEADS_CSV=/home/nexux/scraper-output/leads_extended.csv   (override auto-pick)
 *   MINT_SSH_HOST=100.120.104.104
 *   MINT_SSH_USER=ricky
 *   MINT_REMOTE_DIR=/home/ricky/nexux-outreach
 *   MINT_SSH_KEY=/home/nexux/.ssh/id_rsa
 *   OLLAMA_URL=http://192.168.0.156:11434
 *   OLLAMA_MODEL=qwen2.5-coder:7b
 *   OLLAMA_NUM_PREDICT=200
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');
const { execFile } = require('child_process');

const PORT = Number(process.env.DASHBOARD_PORT || 3700);
const HOST = process.env.DASHBOARD_HOST || '0.0.0.0';

const PUBLIC_DIR = path.join(__dirname, 'mint-dashboard', 'public');
const PUBLIC_IMG = path.join(__dirname, 'public', 'img');

const LEADS_DIR = process.env.LEADS_DIR || '/home/nexux/scraper-output';
const LEADS_CSV = process.env.LEADS_CSV || '';

const MINT_SSH_HOST = process.env.MINT_SSH_HOST || '192.168.0.156';
const MINT_SSH_USER = process.env.MINT_SSH_USER || 'ricky';
const MINT_REMOTE_DIR = process.env.MINT_REMOTE_DIR || '/home/ricky/nexux-outreach';
const MINT_SSH_KEY = process.env.MINT_SSH_KEY || '/home/nexux/.ssh/id_rsa';

const OLLAMA_URL = process.env.OLLAMA_URL || 'http://192.168.0.156:11434';
const OLLAMA_MODEL = process.env.OLLAMA_MODEL || 'qwen2.5-coder:7b';
const OLLAMA_NUM_PREDICT = Number(process.env.OLLAMA_NUM_PREDICT || 60);

const DASHSCOPE_API_KEY = process.env.DASHSCOPE_API_KEY || '';
const DASHSCOPE_URL = 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions';
const DASHSCOPE_MODEL = process.env.DASHSCOPE_MODEL || 'qwen-plus';

const REMOTE_FILES = Object.freeze({
  enviados: 'enviados.json',
  openers: 'openers_log.json',
  conversaciones: 'conversaciones.json',
  respuestas: 'respuestas_log.json',
});

function json(res, status, body, extraHeaders = {}) {
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store',
    ...extraHeaders,
  });
  res.end(JSON.stringify(body));
}

function text(res, status, body, extraHeaders = {}) {
  res.writeHead(status, {
    'Content-Type': 'text/plain; charset=utf-8',
    'Cache-Control': 'no-store',
    ...extraHeaders,
  });
  res.end(body);
}

function notFound(res) {
  return json(res, 404, { error: 'not_found' });
}

function safeParseJson(raw, fallback) {
  try {
    return JSON.parse(raw);
  } catch {
    return fallback;
  }
}

function toIsoDay(date) {
  const d = new Date(date);
  if (Number.isNaN(d.getTime())) return null;
  return d.toISOString().slice(0, 10);
}

function madridToday() {
  return new Date().toLocaleDateString('sv', { timeZone: 'Europe/Madrid' });
}

function stripDigits(s) {
  return String(s || '').replace(/\D+/g, '');
}

function last(arr) {
  return Array.isArray(arr) && arr.length ? arr[arr.length - 1] : null;
}

function readFileIfExists(filePath) {
  try {
    if (!filePath) return null;
    if (!fs.existsSync(filePath)) return null;
    return fs.readFileSync(filePath, 'utf8');
  } catch {
    return null;
  }
}

function sshBaseArgs() {
  const args = ['-o', 'BatchMode=yes', '-o', 'ConnectTimeout=4'];
  try {
    if (MINT_SSH_KEY && fs.existsSync(MINT_SSH_KEY)) {
      args.unshift('-i', MINT_SSH_KEY);
    }
  } catch {}
  return args;
}

function pickLatestCsvFromDir(dirPath) {
  try {
    const preferred = [
      'leads_clinicas.csv',
      'leads_extended.csv',
      'leads_v3.csv',
      'peluquerias_leads.csv',
    ];
    for (const name of preferred) {
      const p = path.join(dirPath, name);
      if (fs.existsSync(p)) return p;
    }
    const entries = fs
      .readdirSync(dirPath, { withFileTypes: true })
      .filter(d => d.isFile() && d.name.toLowerCase().endsWith('.csv'))
      .map(d => {
        const p = path.join(dirPath, d.name);
        const stat = fs.statSync(p);
        return { p, mtimeMs: stat.mtimeMs };
      })
      .sort((a, b) => b.mtimeMs - a.mtimeMs);
    return entries[0]?.p || null;
  } catch {
    return null;
  }
}

function parseCsvSimple(csvText) {
  // Minimal CSV parser (handles quotes + commas). Good enough for scraper output.
  const lines = String(csvText || '')
    .replace(/\r\n/g, '\n')
    .replace(/\r/g, '\n')
    .split('\n')
    .filter(Boolean);
  if (!lines.length) return [];

  const header = parseCsvLine(lines[0]);
  const rows = [];
  for (let i = 1; i < lines.length; i++) {
    const cols = parseCsvLine(lines[i]);
    const obj = {};
    for (let j = 0; j < header.length; j++) obj[header[j]] = cols[j] ?? '';
    rows.push(obj);
  }
  return rows;
}

function parseCsvLine(line) {
  const out = [];
  let cur = '';
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (ch === '"' && line[i + 1] === '"') {
      cur += '"';
      i++;
      continue;
    }
    if (ch === '"') {
      inQuotes = !inQuotes;
      continue;
    }
    if (ch === ',' && !inQuotes) {
      out.push(cur);
      cur = '';
      continue;
    }
    cur += ch;
  }
  out.push(cur);
  return out.map(s => String(s ?? '').trim());
}

function execSshCat(remotePath) {
  return new Promise(resolve => {
    const sshTarget = `${MINT_SSH_USER}@${MINT_SSH_HOST}`;
    const fullPath = `${MINT_REMOTE_DIR}/${remotePath}`;
    execFile(
      'ssh',
      [...sshBaseArgs(), sshTarget, 'cat', fullPath],
      { timeout: 9000, maxBuffer: 15 * 1024 * 1024 },
      (err, stdout) => {
        if (err) return resolve(null);
        resolve(String(stdout || ''));
      }
    );
  });
}

function execSshPm2Jlist() {
  return new Promise(resolve => {
    const sshTarget = `${MINT_SSH_USER}@${MINT_SSH_HOST}`;
    execFile(
      'ssh',
      [...sshBaseArgs(), sshTarget, 'pm2', 'jlist'],
      { timeout: 9000, maxBuffer: 5 * 1024 * 1024 },
      (err, stdout) => {
        if (err) return resolve(null);
        resolve(String(stdout || ''));
      }
    );
  });
}

async function checkOllamaStatus() {
  try {
    const signal = AbortSignal.timeout ? AbortSignal.timeout(3000) : undefined;
    const resp = await fetch(`${OLLAMA_URL.replace(/\/+$/, '')}/api/tags`, { signal });
    return resp.ok ? 'running' : 'unreachable';
  } catch {
    return 'unreachable';
  }
}

async function readRemoteJsonFile(key) {
  const filename = REMOTE_FILES[key];
  if (!filename) return { ok: false, source: 'none', data: null };

  // If a local mirror exists, prefer it.
  const localMirror = process.env[`MINT_${key.toUpperCase()}_PATH`] || '';
  const localRaw = readFileIfExists(localMirror);
  if (localRaw != null) {
    return { ok: true, source: 'local', data: safeParseJson(localRaw, null) };
  }

  const raw = await execSshCat(filename);
  if (raw == null) return { ok: false, source: 'ssh', data: null };
  return { ok: true, source: 'ssh', data: safeParseJson(raw, null) };
}

function buildLeadIndex(leads) {
  const byEmail = new Map();
  const byPhone = new Map();
  const byName = new Map();
  for (const lead of leads) {
    const email = String(lead.email || '').toLowerCase().trim();
    const phone = stripDigits(lead.telefono || '');
    const name = String(lead.nombre || '').toLowerCase().trim();
    if (email) byEmail.set(email, lead);
    if (phone) byPhone.set(phone, lead);
    if (name) byName.set(name, lead);
  }
  return { byEmail, byPhone, byName };
}

function resolveLeadForConversationId(conversationId, leadIndex) {
  const digits = stripDigits(conversationId);
  if (digits && leadIndex.byPhone.has(digits)) return leadIndex.byPhone.get(digits);
  return null;
}

function determineHotLead(conversation) {
  if (!conversation || conversation.cerrada) return false;
  if (conversation.trial_active === true) return false;
  const messages = Array.isArray(conversation.messages) ? conversation.messages : [];
  // Hot lead = there was any inbound reply (user message) and still not trial.
  return messages.some(m => m?.role === 'user' && String(m?.content || '').trim().length);
}

function conversationLastActivityIso(conversation) {
  // Prefer followup_sent if present; otherwise unknown. We can't trust message timestamps (not stored).
  if (conversation?.followup_sent) return String(conversation.followup_sent);
  return null;
}

function computeWhatsappToday(enviadosObj) {
  const today = toIsoDay(new Date());
  let total = 0;
  let ok = 0;
  let error = 0;
  let noWhatsapp = 0;

  for (const v of Object.values(enviadosObj || {})) {
    const day = toIsoDay(v?.fecha);
    if (!day || day !== today) continue;
    total++;
    const estado = String(v?.estado || '');
    if (/no_whatsapp/i.test(estado)) noWhatsapp++;
    else if (/^error/i.test(estado)) error++;
    else ok++;
  }

  const recommendedLimit = 60;
  const sessionMax = 20;
  const ratio = recommendedLimit ? total / recommendedLimit : 0;
  const level = ratio >= 1 ? 'red' : ratio >= 0.8 ? 'yellow' : 'green';

  return { total, ok, error, noWhatsapp, recommendedLimit, sessionMax, level };
}

function computeHistory(enviadosObj, openersObj, conversacionesObj, days) {
  const now = new Date();
  const map = new Map();
  function ensure(day) {
    if (!map.has(day)) {
      map.set(day, { day, sent: 0, opened: 0, responded: 0, errors: 0, no_whatsapp: 0 });
    }
    return map.get(day);
  }

  for (const v of Object.values(enviadosObj || {})) {
    const day = toIsoDay(v?.fecha);
    if (!day) continue;
    const bucket = ensure(day);
    bucket.sent++;
    const estado = String(v?.estado || '');
    if (/^error/i.test(estado)) bucket.errors++;
    if (/no_whatsapp/i.test(estado)) bucket.no_whatsapp++;
  }

  for (const ts of Object.values(openersObj || {})) {
    const day = toIsoDay(ts);
    if (!day) continue;
    ensure(day).opened++;
  }

  for (const conv of Object.values(conversacionesObj || {})) {
    if (!conv) continue;
    const day = toIsoDay(conv.followup_sent);
    if (!day) continue;
    ensure(day).responded++;
  }

  const cutoff = new Date(now.getTime() - days * 24 * 60 * 60 * 1000);
  const out = Array.from(map.values())
    .filter(b => new Date(b.day) >= cutoff)
    .sort((a, b) => (a.day < b.day ? -1 : 1));

  return out;
}

function computeFunnelCounts(leadsCount, enviadosObj, openersObj, conversacionesObj) {
  const sent = Object.keys(enviadosObj || {}).length;
  const opened = Object.keys(openersObj || {}).length;
  const responded = Object.keys(conversacionesObj || {}).length;
  // Trial conversion is not yet available in current logs.
  const trial = Object.values(conversacionesObj || {}).filter(c => c?.trial_active === true).length;

  const pct = (num, den) => (den > 0 ? Math.round((num / den) * 1000) / 10 : 0);
  return {
    leads_total: leadsCount,
    sent,
    opened,
    responded,
    trial,
    opener_pct: pct(opened, sent),
    responded_pct: pct(responded, opened),
    trial_pct: pct(trial, responded),
  };
}

function percent(num, den) {
  return den > 0 ? Math.round((num / den) * 1000) / 10 : 0;
}

function classifySendError(status) {
  const raw = String(status || '').replace(/^error:\s*/i, '').trim();
  const lower = raw.toLowerCase();
  if (lower.includes('frame')) return 'detached Frame';
  if (lower.includes('timeout') || lower.includes('timed out')) return 'timeout';
  if (lower.includes('navigation')) return 'navigation error';
  if (lower.includes('selector')) return 'selector error';
  if (lower.includes('target closed') || lower.includes('browser closed')) return 'browser closed';
  if (lower.includes('no lid')) return 'no LID (numero no vinculado)';
  if (raw.includes('http')) return 'js error (stacktrace)';
  return raw.slice(0, 60).trim() || 'unknown error';
}

function processStatus(pm2List, name) {
  const list = Array.isArray(pm2List) ? pm2List : [];
  const proc = list.find(p => p?.name === name);
  return proc?.pm2_env?.status || 'unknown';
}

function buildRichContext(currentCache) {
  const fechaHoy = madridToday();
  const leads = Array.isArray(currentCache.leads) ? currentCache.leads : [];
  const enviados = currentCache.enviados || {};
  const openers = currentCache.openers || {};
  const conversaciones = currentCache.conversaciones || {};

  let enviadosExitosos = 0;
  let fallidosTecnico = 0;
  let sinWhatsapp = 0;
  let enviadosHoy = 0;
  let enviadosHoyExitosos = 0;
  let enviadosHoyNoWA = 0;
  const errorCounts = new Map();

  for (const item of Object.values(enviados)) {
    const estado = String(item?.estado || '');
    const esHoy = String(item?.fecha || '').startsWith(fechaHoy);
    if (esHoy) {
      enviadosHoy++;
      if (estado === 'enviado') enviadosHoyExitosos++;
      else if (estado === 'no_whatsapp') enviadosHoyNoWA++;
    }

    if (/^error:/i.test(estado)) {
      fallidosTecnico++;
      const tipo = classifySendError(estado);
      errorCounts.set(tipo, (errorCounts.get(tipo) || 0) + 1);
      continue;
    }

    if (estado === 'no_whatsapp') { sinWhatsapp++; continue; }
    enviadosExitosos++;
  }

  const erroresTop3 = Array.from(errorCounts.entries())
    .map(([tipo, count]) => ({ tipo, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 3);

  const openersRecientes = Object.entries(openers)
    .sort((a, b) => String(b[1]).localeCompare(String(a[1])))
    .slice(0, 3)
    .map(([email]) => email);

  const hotItems = [];
  for (const [id, conv] of Object.entries(conversaciones)) {
    if (!determineHotLead(conv)) continue;
    const lastMsg = last(conv?.messages || []);
    hotItems.push({
      id,
      ultimo_msg: lastMsg?.content ? String(lastMsg.content).slice(0, 180) : null,
      rol: lastMsg?.role || null,
    });
  }

  const context = {
    timestamp: new Date().toISOString(),
    fecha_hoy: fechaHoy,
    leads: {
      total: leads.length,
    },
    enviados: {
      total_historico: Object.keys(enviados).length,
      exitosos: enviadosExitosos,
      fallidos_tecnico: fallidosTecnico,
      sin_whatsapp: sinWhatsapp,
      tasa_exito_pct: percent(enviadosExitosos, Object.keys(enviados).length),
      hoy: enviadosHoy,
        hoy_detalle: {
          exitosos: enviadosHoyExitosos,
          no_whatsapp: enviadosHoyNoWA,
          tasa_hoy_pct: percent(enviadosHoyExitosos, enviadosHoy - enviadosHoyNoWA),
        },
      errores_top3: erroresTop3,
    },
    openers: {
      canal: 'email',
      total: Object.keys(openers).length,
      recientes_3: openersRecientes,
    },
    conversaciones_whatsapp: {
      canal: 'WhatsApp',
      total: Object.keys(conversaciones).length,
      hot_leads: hotItems.length,
      muestra: hotItems.slice(0, 3),
    },
    mint_procesos: {
      nexux_scheduler: processStatus(currentCache.pm2, 'nexux-scheduler'),
      nexux_lead_scraper: processStatus(currentCache.pm2, 'nexux-lead-scraper'),
      ollama: currentCache.ollamaStatus || 'unknown',
    },
    sistema: {
      descripcion: 'Nexux MINT Outreach System',
      canal_outreach: 'WhatsApp (WhatsApp Web via Playwright)',
      canal_email: 'emails de seguimiento (openers_log)',
      ia_scraper: 'Qwen 2.5-coder:7b via Ollama en Mint (CPU, para filtrar leads del scraper)',
      ia_chat: 'Qwen Plus via DashScope API (tu mismo)',
      bot_respuestas: "bot.js - auto-responde WhatsApp como 'Alex'",
      scraper: 'scraper.py - Google Maps, 62 ciudades, cron 03:00 diario',
      scheduler: 'scheduler.js - orquesta outreach diario',
    },
  };

  const dateField = ['fecha', 'created_at', 'scraped_at', 'added_at'].find(field => leads.some(lead => lead[field]));
  if (dateField) {
    context.leads.added_today = leads.filter(lead => String(lead[dateField] || '').startsWith(fechaHoy)).length;
  }

  return context;
}

function buildMintSystemPrompt(context) {
  const ctx = JSON.stringify(context, null, 0);
  return `Eres el asistente inteligente del Dashboard MINT de Nexux Pro. Conoces el sistema al completo y respondes con datos reales del contexto, nunca inventas.

## ARQUITECTURA DEL SISTEMA

**Nodo Mint (192.168.0.156, ricky@):**
- \`nexux-scheduler\` (PM2): orquesta el outreach diario. Lanza \`outreach.js\` a las 09:00, 14:00 (y catch-up 10:00). Cada run envía 1 mensaje por sesión Chrome (para evitar "detached Frame"), con delay 45-90s entre mensajes, hasta MAX_SESION_DIA=20 intentos/día.
- \`nexux-lead-scraper\` (PM2): scraper Google Maps con Playwright. Corre a las 03:00. Usa Qwen 2.5-coder:7b via Ollama (CPU local) para clasificar negocios y generar pitch. Guarda en leads_v3.csv.
- \`outreach.js\`: envía 1 WA por sesión Chrome via whatsapp-web.js. 1 envío = 1 arranque Chrome.
- \`bot.js\`: auto-responde conversaciones WA como "Alex" (Groq). Corre 24h. Se pausa mientras outreach está activo.
- \`followup.js / followup_wa.js\`: follow-up a leads sin respuesta.

**Canales:**
- Outreach principal: WhatsApp (whatsapp-web.js, Playwright)
- Email: solo seguimiento. openers_log.json registra aperturas de email — NUNCA confundir con aperturas WA.

**IA:**
- Qwen 2.5-coder:7b (Ollama, CPU): SOLO para el scraper. NO es el chat del dashboard.
- Tú (Qwen Plus, DashScope): eres el asistente de este dashboard.

## CÓMO INTERPRETAR LOS DATOS

**CRÍTICO — HOY vs HISTÓRICO:**
- \`enviados.hoy\` y \`enviados.hoy_detalle\` = actividad del día de hoy únicamente.
- \`enviados.total_historico\`, \`tasa_exito_pct\` y \`errores_top3\` = acumulado histórico total, NO de hoy.
- Cuando alguien pregunta "cuántos enviados hoy" o "qué pasó hoy": usa SIEMPRE \`hoy_detalle\`, nunca extrapoles del histórico.
- Ejemplo correcto: "Hoy se intentaron N contactos: X enviados OK, Y sin WhatsApp. Tasa hoy: Z%."

**enviados.json:**
- \`estado: "enviado"\` = mensaje WA entregado correctamente.
- \`estado: "no_whatsapp"\` = número sin WA activo (no es un error técnico, es información del lead).
- \`estado: "error: ..."\` = fallo de Playwright/Chrome (detached Frame, timeout, etc).
- Tasa de éxito real = exitosos / (total - no_whatsapp). La tasa histórica baja (~12%) se debe a errores Chrome acumulados, no a mala calidad de leads.

**Errores "detached Frame":** Playwright perdió la pestaña de WA Web. Causa: la sesión Chrome de una run anterior no se cerró correctamente. Fix: reiniciar el scheduler limpia los procesos zombie.

**openers_log.json:** Canal EMAIL. Claves son emails. Nunca son aperturas de WhatsApp.

**conversaciones.json:** Conversaciones WA activas. IDs con formato \`@lid\`.

**Por qué solo N envíos hoy:** El scheduler envía 1 WA por sesión Chrome (diseño anti-detachedFrame). Con delays de 45-90s/mensaje, 20 mensajes tardan ~25-30 minutos. Si el contador de hoy es bajo, puede ser: hora temprana, error técnico en las últimas runs, o límite diario no alcanzado aún.

## LO QUE PUEDES Y NO PUEDES HACER
- SÍ: analizar datos, calcular métricas, detectar anomalías, explicar errores, recomendar acciones concretas.
- SÍ: responder sobre scraper, scheduler, bot, errores Chrome, leads, conversaciones.
- NO: ejecutar acciones (no puedes reiniciar procesos, enviar mensajes, lanzar scrapers).

## REGLAS DE RESPUESTA
- Directo, con cifras del contexto. Sin texto de relleno.
- Distingue siempre hoy vs histórico cuando hay datos de ambos.
- Si detectas anomalía (tasa hoy < 50%, scheduler caído, 0 envíos hoy), menciónala proactivamente con causa probable.
- Si un dato no está en el contexto, dilo explícitamente.

## CONTEXTO ACTUAL:
${ctx}\``;
}

function serveStatic(req, res, pathname) {
  const rel = pathname === '/' ? '/index.html' : pathname;
  const clean = path
    .normalize(rel)
    .replace(/^(\.\.(\/|\\|$))+/, '')
    .replace(/^[/\\]+/, '');
  const filePath = path.join(PUBLIC_DIR, clean);

  if (!filePath.startsWith(PUBLIC_DIR)) return notFound(res);
  if (!fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) return notFound(res);

  const ext = path.extname(filePath).toLowerCase();
  const types = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css; charset=utf-8',
    '.js': 'application/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.svg': 'image/svg+xml',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.webp': 'image/webp',
    '.ico': 'image/x-icon',
  };
  res.writeHead(200, {
    'Content-Type': types[ext] || 'application/octet-stream',
    'Cache-Control': ext === '.html' ? 'no-store' : 'public, max-age=3600',
  });
  fs.createReadStream(filePath).pipe(res);
}

let cache = {
  lastLoadAt: 0,
  loadError: null,
  sources: {},
  leads: [],
  leadIndex: buildLeadIndex([]),
  enviados: {},
  openers: {},
  conversaciones: {},
  respuestas: null,
  pm2: null,
  ollamaStatus: 'unknown',
};

async function loadAllData() {
  const started = Date.now();
  const sources = {};

  // Leads CSV (Pi)
  let leadsCsvPath = LEADS_CSV || pickLatestCsvFromDir(LEADS_DIR);
  sources.leads_csv = leadsCsvPath || null;
  let leads = [];
  if (leadsCsvPath && fs.existsSync(leadsCsvPath)) {
    const raw = fs.readFileSync(leadsCsvPath, 'utf8');
    leads = parseCsvSimple(raw);
  }

  // Remote logs (Mint node)
  const enviadosR = await readRemoteJsonFile('enviados');
  sources.enviados = enviadosR.source;
  const openersR = await readRemoteJsonFile('openers');
  sources.openers = openersR.source;
  const convR = await readRemoteJsonFile('conversaciones');
  sources.conversaciones = convR.source;
  const respR = await readRemoteJsonFile('respuestas');
  sources.respuestas = respR.source;

  // Scheduler health (PM2 on Mint node)
  const pm2Raw = await execSshPm2Jlist();
  const pm2 = pm2Raw ? safeParseJson(pm2Raw, null) : null;
  sources.pm2 = pm2Raw ? 'ssh' : 'none';
  const ollamaStatus = await checkOllamaStatus();
  sources.ollama = OLLAMA_URL;

  cache = {
    lastLoadAt: started,
    loadError: null,
    sources,
    leads,
    leadIndex: buildLeadIndex(leads),
    enviados: enviadosR.data || {},
    openers: openersR.data || {},
    conversaciones: convR.data || {},
    respuestas: respR.data,
    pm2,
    ollamaStatus,
  };
}

async function ensureFreshCache() {
  const maxAgeMs = 15_000;
  if (Date.now() - cache.lastLoadAt < maxAgeMs) return;
  try {
    await loadAllData();
  } catch (e) {
    cache.loadError = String(e?.message || e);
  }
}

function schedulerHealth(pm2List) {
  const list = Array.isArray(pm2List) ? pm2List : [];
  const proc = list.find(p => p?.name === 'nexux-scheduler') || null;
  if (!proc) return { ok: false, status: 'unknown', reason: 'pm2_process_not_found' };
  const pm2Env = proc.pm2_env || {};
  const status = pm2Env.status || 'unknown';
  const restartTime = pm2Env.restart_time ?? null;
  const uptime = pm2Env.pm_uptime ? new Date(pm2Env.pm_uptime).toISOString() : null;
  return { ok: true, status, restart_time: restartTime, pm_uptime: uptime };
}

async function handleApi(req, res, pathname, query) {
  await ensureFreshCache();

  if (pathname === '/api/health') {
    return json(res, 200, { ok: true, service: 'mint-dashboard', now: new Date().toISOString() });
  }

  if (pathname === '/api/status') {
    return json(res, 200, {
      ok: true,
      last_load_at: cache.lastLoadAt ? new Date(cache.lastLoadAt).toISOString() : null,
      load_error: cache.loadError,
      sources: cache.sources,
      counts: {
        leads: cache.leads.length,
        enviados: Object.keys(cache.enviados || {}).length,
        openers: Object.keys(cache.openers || {}).length,
        conversaciones: Object.keys(cache.conversaciones || {}).length,
      },
    });
  }

  if (pathname === '/api/system-context' && req.method === 'GET') {
    return json(res, 200, buildRichContext(cache));
  }

  if (pathname === '/api/funnel') {
    return json(res, 200, computeFunnelCounts(cache.leads.length, cache.enviados, cache.openers, cache.conversaciones));
  }

  if (pathname === '/api/history') {
    const days = Math.max(1, Math.min(365, Number(query.days || 30)));
    return json(res, 200, { days, series: computeHistory(cache.enviados, cache.openers, cache.conversaciones, days) });
  }

  if (pathname === '/api/whatsapp') {
    return json(res, 200, computeWhatsappToday(cache.enviados));
  }

  if (pathname === '/api/scheduler') {
    return json(res, 200, schedulerHealth(cache.pm2));
  }

  if (pathname === '/api/hot') {
    const out = [];
    for (const [id, conv] of Object.entries(cache.conversaciones || {})) {
      if (!determineHotLead(conv)) continue;
      const lead = resolveLeadForConversationId(id, cache.leadIndex);
      const lastMsg = last(conv.messages || []);
      out.push({
        id,
        nombre: lead?.nombre || conv?.nombre || null,
        ciudad: lead?.ciudad || null,
        last_role: lastMsg?.role || null,
        last_message: lastMsg?.content ? String(lastMsg.content).slice(0, 240) : null,
        last_activity: conversationLastActivityIso(conv),
      });
    }
    out.sort((a, b) => String(b.last_activity || '').localeCompare(String(a.last_activity || '')));
    return json(res, 200, { items: out.slice(0, 100) });
  }

  if (pathname === '/api/leads') {
    const q = String(query.q || '').toLowerCase().trim();
    const city = String(query.city || '').toLowerCase().trim();
    const limit = Math.max(1, Math.min(200, Number(query.limit || 50)));

    let items = cache.leads;
    if (city) items = items.filter(l => String(l.ciudad || '').toLowerCase().includes(city));
    if (q) {
      items = items.filter(l => {
        const hay = [
          l.nombre,
          l.ciudad,
          l.telefono,
          l.website,
          l.instagram,
          l.maps_url,
        ]
          .filter(Boolean)
          .join(' ')
          .toLowerCase();
        return hay.includes(q);
      });
    }

    return json(res, 200, { total: items.length, items: items.slice(0, limit) });
  }

  if (pathname === '/api/journey') {
    const id = String(query.id || '');
    if (!id) return json(res, 400, { error: 'missing_id' });

    const conv = (cache.conversaciones || {})[id] || null;
    const lead = resolveLeadForConversationId(id, cache.leadIndex);

    const timeline = [];
    if (lead) {
      timeline.push({
        at: null,
        type: 'lead',
        text: `Lead en ${lead.ciudad || '—'} (${lead.nombre || '—'})`,
      });
    }

    // Enviados — match by phone digits if possible
    const digits = stripDigits(id);
    if (digits && cache.enviados && cache.enviados[digits]) {
      const e = cache.enviados[digits];
      timeline.push({
        at: e.fecha || null,
        type: 'send',
        text: `Envío: ${e.estado || 'ok'}`,
      });
    }

    // Openers — match by email if we have it
    const email = String(lead?.email || '').toLowerCase().trim();
    if (email && cache.openers && cache.openers[email]) {
      timeline.push({
        at: cache.openers[email],
        type: 'open',
        text: 'Email abierto',
      });
    }

    // Conversation
    if (conv) {
      const messages = Array.isArray(conv.messages) ? conv.messages : [];
      const lastMsg = last(messages);
      timeline.push({
        at: conv.followup_sent || null,
        type: 'whatsapp',
        text: `Conversación: ${messages.length} mensajes, último = ${lastMsg?.role || '—'}`,
      });
    }

    timeline.sort((a, b) => String(a.at || '') > String(b.at || '') ? 1 : -1);
    return json(res, 200, { id, lead: lead || null, conversation: conv, timeline });
  }

  if (pathname === '/api/chat/stream' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => {
      body += chunk;
      if (body.length > 200_000) req.destroy();
    });
    req.on('end', async () => {
      const payload = safeParseJson(body, null);
      const prompt = String(payload?.prompt || '').trim();
      if (!prompt) return json(res, 400, { error: 'missing_prompt' });

      const context = buildRichContext(cache);

      const messages = [
        { role: 'system', content: buildMintSystemPrompt(context) },
        { role: 'user', content: prompt },
      ];

      try {
        res.writeHead(200, {
          'Content-Type': 'text/event-stream; charset=utf-8',
          'Cache-Control': 'no-store',
          Connection: 'keep-alive',
        });

        const abort = new AbortController();
        res.on('close', () => abort.abort());

        const resp = await fetch(DASHSCOPE_URL, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${DASHSCOPE_API_KEY}`,
          },
          body: JSON.stringify({ model: DASHSCOPE_MODEL, messages, stream: true }),
          signal: abort.signal,
        });

        if (!resp.ok) {
          const t = await resp.text();
          res.write(`event: error\ndata: ${JSON.stringify({ error: 'dashscope_error', status: resp.status, details: t.slice(0, 300) })}\n\n`);
          return res.end();
        }

        const reader = resp.body?.getReader?.();
        if (!reader) {
          res.write(`event: error\ndata: ${JSON.stringify({ error: 'stream_unavailable' })}\n\n`);
          return res.end();
        }

        let buffer = '';
        while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          buffer += Buffer.from(value).toString('utf8');
          let idx;
          while ((idx = buffer.indexOf('\n')) >= 0) {
            const line = buffer.slice(0, idx).trim();
            buffer = buffer.slice(idx + 1);
            if (!line || !line.startsWith('data:')) continue;
            const raw = line.slice(5).trim();
            if (raw === '[DONE]') {
              res.write(`event: done\ndata: ${JSON.stringify({ ok: true, model: DASHSCOPE_MODEL })}\n\n`);
              res.end();
              return;
            }
            const chunk = safeParseJson(raw, null);
            const token = chunk?.choices?.[0]?.delta?.content;
            if (token) res.write(`data: ${JSON.stringify({ token })}\n\n`);
          }
        }

        res.write(`event: done\ndata: ${JSON.stringify({ ok: true, model: DASHSCOPE_MODEL })}\n\n`);
        res.end();
      } catch (e) {
        try {
          res.write(`event: error\ndata: ${JSON.stringify({ error: 'dashscope_unreachable', details: String(e?.message || e) })}\n\n`);
        } catch {}
        return res.end();
      }
    });
    return;
  }


  if (pathname === '/api/chat' && req.method === 'POST') {
    // Non-stream fallback (kept for simple integrations). Keep it bounded.
    let body = '';
    req.on('data', chunk => {
      body += chunk;
      if (body.length > 200_000) req.destroy();
    });
    req.on('end', async () => {
      const payload = safeParseJson(body, null);
      const prompt = String(payload?.prompt || '').trim();
      if (!prompt) return json(res, 400, { error: 'missing_prompt' });

      const context = {
        funnel: computeFunnelCounts(cache.leads.length, cache.enviados, cache.openers, cache.conversaciones),
      };

      const system = [
        'Eres el asistente del Dashboard MINT de Nexux Pro.',
        'Responde en español, directo, con cifras.',
        'Contexto disponible en JSON a continuación:',
        JSON.stringify(context),
      ].join('\n');

      try {
        const abort = AbortSignal.timeout ? AbortSignal.timeout(120_000) : undefined;
        const resp = await fetch(`${OLLAMA_URL.replace(/\/+$/, '')}/api/generate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            model: OLLAMA_MODEL,
            prompt: `${system}\n\nPregunta del usuario: ${prompt}\nRespuesta:`,
            stream: false,
            num_predict: Number.isFinite(OLLAMA_NUM_PREDICT) ? OLLAMA_NUM_PREDICT : 200,
          }),
          signal: abort,
        });
        if (!resp.ok) {
          const t = await resp.text();
          return json(res, 502, { error: 'ollama_error', status: resp.status, details: t.slice(0, 500) });
        }
        const data = await resp.json();
        return json(res, 200, { ok: true, model: OLLAMA_MODEL, response: String(data?.response || '').trim() });
      } catch (e) {
        return json(res, 502, { error: 'ollama_unreachable', details: String(e?.message || e) });
      }
    });
    return;
  }

  return notFound(res);
}

const server = http.createServer(async (req, res) => {
  const parsed = url.parse(req.url, true);
  const pathname = parsed.pathname || '/';

  // Basic hardening headers
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('Referrer-Policy', 'no-referrer');

  if (pathname.startsWith('/img/') && (req.method === 'GET' || req.method === 'HEAD')) {
    const file = path.join(PUBLIC_IMG, path.basename(pathname));
    if (!file.startsWith(PUBLIC_IMG)) return json(res, 403, { error: 'forbidden' });
    try {
      const data = fs.readFileSync(file);
      const ext = path.extname(file).slice(1).toLowerCase();
      const contentType = ext === 'jpg' ? 'image/jpeg' : `image/${ext}`;
      res.writeHead(200, { 'Content-Type': contentType, 'Cache-Control': 'public, max-age=86400' });
      if (req.method === 'HEAD') return res.end();
      return res.end(data);
    } catch {
      return json(res, 404, { error: 'not_found' });
    }
  }

  if (pathname.startsWith('/api/')) return handleApi(req, res, pathname, parsed.query || {});
  if (req.method !== 'GET') return text(res, 405, 'Method Not Allowed');

  return serveStatic(req, res, pathname);
});

server.listen(PORT, HOST, async () => {
  try {
    await loadAllData();
  } catch {}
  console.log(`[mint-dashboard] listening on http://${HOST}:${PORT}`);
});

function shutdown(signal) {
  console.log(`[mint-dashboard] received ${signal}, shutting down…`);
  server.close(() => process.exit(0));
  setTimeout(() => process.exit(1), 5_000).unref();
}

process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));
