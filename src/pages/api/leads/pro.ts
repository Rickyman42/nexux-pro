import type { APIRoute } from 'astro';
import fs from 'fs';
import path from 'path';

const TELEGRAM_TOKEN = import.meta.env.TELEGRAM_BOT_TOKEN || '';
const TELEGRAM_CHAT  = import.meta.env.TELEGRAM_CHAT_ID  || '';
const LEADS_FILE     = path.join(process.cwd(), 'leads.jsonl');

async function sendTelegram(msg: string) {
  if (!TELEGRAM_TOKEN || !TELEGRAM_CHAT) return;
  try {
    await fetch(`https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: TELEGRAM_CHAT, text: msg, parse_mode: 'HTML' }),
    });
  } catch {}
}

export const prerender = false;

export const POST: APIRoute = async ({ request }) => {
  let body: Record<string, string> = {};
  try { body = await request.json(); } catch { return new Response(JSON.stringify({ ok: false }), { status: 400 }); }

  const lead = {
    ...body,
    _received: new Date().toISOString(),
  };

  // Save to leads.jsonl
  try {
    fs.appendFileSync(LEADS_FILE, JSON.stringify(lead) + '\n');
  } catch {}

  // Telegram alert
  const isTrial = body.utm?.includes('prueba') || body.source?.includes('prueba') || body.utm?.includes('ref=email');
  const emoji   = isTrial ? '🎯' : '📋';
  const tag     = isTrial ? ' [PRUEBA GRATIS]' : '';
  const msg =
    `${emoji} <b>Nuevo lead Lara${tag}</b>\n` +
    `👤 ${body.nombre || '?'} — ${body.salon || '?'}\n` +
    `📱 ${body.telefono || '?'}\n` +
    `📡 Canal: ${body.canal || '?'}\n` +
    `🎯 Plan: ${body._plan || body.plan_elegido || 'starter'}\n` +
    `🕐 ${new Date().toLocaleString('es-ES', { timeZone: 'Europe/Madrid' })}`;

  await sendTelegram(msg);

  return new Response(JSON.stringify({ ok: true }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
};
