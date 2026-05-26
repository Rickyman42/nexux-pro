#!/usr/bin/env node
/**
 * nexux.pro — Lead receiver microservice
 * Recibe leads del bot Lara, los guarda y notifica a Ricardo por Telegram.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');

require('dotenv').config({ path: process.env.HOME + '/.env' });

const PORT = process.env.LEADS_PORT || 4326;
const LEADS_FILE = path.join(__dirname, 'leads.jsonl');
const EMAIL_ASSETS_DIR = path.join(__dirname, 'email-assets');
const TG_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const TG_CHAT_ID = process.env.TELEGRAM_CHAT_ID || process.env.TG_CHAT_ID;

const ALLOWED_ORIGINS = [
  'https://nexux.pro',
  'https://www.nexux.pro',
  'http://localhost:4325',
  'http://192.168.0.120:4325',
];

function send(res, status, body, extraHeaders = {}) {
  res.writeHead(status, {
    'Content-Type': 'application/json',
    ...extraHeaders,
  });
  res.end(JSON.stringify(body));
}

function corsHeaders(origin) {
  const allowed = ALLOWED_ORIGINS.includes(origin) ? origin : 'https://nexux.pro';
  return {
    'Access-Control-Allow-Origin': allowed,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
  };
}

async function notifyTelegram(lead) {
  if (!TG_TOKEN || !TG_CHAT_ID) {
    console.warn('[leads] Telegram no configurado');
    return;
  }
  const text = [
    '🎯 *NUEVO LEAD NEXUX.PRO*',
    '',
    `👤 *${lead.nombre || '—'}*`,
    `💇 ${lead.salon || '—'}`,
    `📍 ${lead.ciudad || '—'}`,
    `📞 ${lead.telefono || '—'}`,
    '',
    `🗂 Sistema actual: ${lead.reservas || '—'}`,
    `💬 Dolor: _${(lead.dolor || '—').replace(/[_*[\]()]/g, '')}_`,
    '',
    `🔗 UTM: ${lead.utm || '(directo)'}`,
    `⏱ ${new Date().toLocaleString('es-ES', { timeZone: 'Europe/Madrid' })}`,
  ].join('\n');

  try {
    const resp = await fetch(`https://api.telegram.org/bot${TG_TOKEN}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: TG_CHAT_ID,
        text,
        parse_mode: 'Markdown',
        disable_web_page_preview: true,
      }),
    });
    if (!resp.ok) console.error('[leads] Telegram error', await resp.text());
  } catch (e) {
    console.error('[leads] Telegram exception', e.message);
  }
}

function persistLead(lead) {
  const entry = {
    ...lead,
    received_at: new Date().toISOString(),
  };
  fs.appendFileSync(LEADS_FILE, JSON.stringify(entry) + '\n');
}

const server = http.createServer(async (req, res) => {
  const parsed = url.parse(req.url, true);
  const origin = req.headers.origin || '';
  const cors = corsHeaders(origin);

  if (req.method === 'OPTIONS') {
    res.writeHead(204, cors);
    return res.end();
  }

  if (req.method === 'GET' && parsed.pathname === '/health') {
    return send(res, 200, { ok: true, service: 'nexux-pro-leads' }, cors);
  }

  if (req.method === 'GET' && parsed.pathname.startsWith('/email-assets/')) {
    const filename = path.basename(decodeURIComponent(parsed.pathname));
    if (!/^[a-z0-9._-]+\.(png|jpg|jpeg|gif|webp|mp3)$/i.test(filename)) {
      return send(res, 404, { error: 'not_found' }, cors);
    }

    const filePath = path.join(EMAIL_ASSETS_DIR, filename);
    if (!fs.existsSync(filePath)) {
      return send(res, 404, { error: 'not_found' }, cors);
    }

    const ext = path.extname(filename).toLowerCase();
    const types = {
      '.png': 'image/png',
      '.jpg': 'image/jpeg',
      '.jpeg': 'image/jpeg',
      '.gif': 'image/gif',
      '.webp': 'image/webp',
      '.mp3': 'audio/mpeg',
    };

    res.writeHead(200, {
      'Content-Type': types[ext] || 'application/octet-stream',
      'Cache-Control': 'public, max-age=604800, immutable',
      ...cors,
    });
    fs.createReadStream(filePath).pipe(res);
    return;
  }

  if (req.method === 'POST' && parsed.pathname === '/leads/pro') {
    let body = '';
    req.on('data', chunk => {
      body += chunk;
      if (body.length > 50_000) {
        req.destroy();
      }
    });
    req.on('end', async () => {
      try {
        const lead = JSON.parse(body);
        const required = ['nombre', 'salon', 'telefono'];
        const missing = required.filter(k => !lead[k]);
        if (missing.length) {
          return send(res, 400, { error: 'missing_fields', fields: missing }, cors);
        }
        if (String(lead.nombre).length > 200 || String(lead.dolor || '').length > 2000) {
          return send(res, 400, { error: 'fields_too_long' }, cors);
        }
        persistLead(lead);
        notifyTelegram(lead);
        return send(res, 200, { ok: true }, cors);
      } catch (e) {
        return send(res, 400, { error: 'invalid_json' }, cors);
      }
    });
    return;
  }

  return send(res, 404, { error: 'not_found' }, cors);
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`[nexux-pro-leads] listening on 127.0.0.1:${PORT}`);
});
