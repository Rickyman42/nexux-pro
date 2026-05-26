import type { APIRoute } from 'astro';
import fs from 'fs';
import path from 'path';

const TELEGRAM_TOKEN     = import.meta.env.TELEGRAM_BOT_TOKEN || '';
const TELEGRAM_CHAT      = import.meta.env.TELEGRAM_CHAT_ID  || '';
const PROVISION_URL      = 'https://pi.nexux.pro/provision';
const PROVISION_SECRET   = import.meta.env.PROVISION_SECRET  || 'nexux-wa-trial-2026';
const LEADS_FILE         = path.join(process.cwd(), 'leads.jsonl');

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

async function provisionClient(body: Record<string, string>): Promise<{
  telegramDeepLink?: string;
  portalUrl?: string;
  clientId?: string;
} | null> {
  try {
    const res = await fetch(PROVISION_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-provision-secret': PROVISION_SECRET,
      },
      body: JSON.stringify({
        plan:     body.plan_elegido || 'starter',
        salon:    body.salon,
        telefono: body.telefono,
        nombre:   body.nombre,
        canal:    body.canal || 'telegram',
        ciudad:   body.ciudad,
        email:    body.email,
      }),
    });
    if (!res.ok) {
      const err = await res.text();
      console.error('[leads/pro] provision error:', res.status, err);
      return null;
    }
    return await res.json();
  } catch (e) {
    console.error('[leads/pro] provision fetch failed:', e);
    return null;
  }
}

export const prerender = false;

export const POST: APIRoute = async ({ request }) => {
  let body: Record<string, string> = {};
  try { body = await request.json(); }
  catch { return new Response(JSON.stringify({ ok: false }), { status: 400 }); }

  const lead = { ...body, _received: new Date().toISOString() };

  // Save to leads.jsonl
  try { fs.appendFileSync(LEADS_FILE, JSON.stringify(lead) + '\n'); } catch {}

  const isTrial = body.utm?.includes('prueba') || body.source?.includes('prueba') ||
                  body.utm?.includes('ref=email') || Boolean(body._trial);

  // Auto-provision (trial only)
  let provision: Awaited<ReturnType<typeof provisionClient>> = null;
  if (isTrial && body.salon && body.telefono) {
    provision = await provisionClient(body);
  }

  // Telegram alert to Ricardo
  const emoji = isTrial ? '🎯' : '📋';
  const tag   = isTrial ? ' [PRUEBA GRATIS]' : '';
  const portalLine = provision?.portalUrl ? `\n🔗 Portal: ${provision.portalUrl}` : '';
  const deepLine   = provision?.telegramDeepLink ? `\n🤖 DeepLink: ${provision.telegramDeepLink}` : '';

  const msg =
    `${emoji} <b>Nuevo lead Lara${tag}</b>\n` +
    `👤 ${body.nombre || '?'} — ${body.salon || '?'}\n` +
    `📱 ${body.telefono || '?'}\n` +
    `📡 Canal: ${body.canal || '?'}\n` +
    `🎯 Plan: ${body.plan_elegido || body._plan || 'starter'}\n` +
    `🕐 ${new Date().toLocaleString('es-ES', { timeZone: 'Europe/Madrid' })}` +
    portalLine + deepLine;

  await sendTelegram(msg);

  return new Response(JSON.stringify({
    ok: true,
    telegramDeepLink: provision?.telegramDeepLink ?? null,
    portalUrl:        provision?.portalUrl ?? null,
    clientId:         provision?.clientId ?? null,
  }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
};
