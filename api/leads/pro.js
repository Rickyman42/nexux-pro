// Vercel serverless function — recibe leads del bot Lara
export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(204).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'method_not_allowed' });

  const lead = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});

  const required = ['nombre', 'salon', 'telefono'];
  const missing = required.filter(k => !lead[k]);
  if (missing.length) return res.status(400).json({ error: 'missing_fields', fields: missing });

  if (String(lead.nombre).length > 200 || String(lead.mayor_dolor || '').length > 2000) {
    return res.status(400).json({ error: 'fields_too_long' });
  }

  const TOKEN = process.env.TELEGRAM_BOT_TOKEN;
  const CHAT = process.env.TELEGRAM_CHAT_ID;

  if (TOKEN && CHAT) {
    const planLabel = {
      starter: '🌱 Starter (249€/mes)',
      pro: '⭐ Pro (449€/mes)',
      total: '💎 Total (749€/mes)',
    }[lead._plan] || lead._plan || '—';

    const text = [
      '🎯 *NUEVO LEAD NEXUX.PRO*',
      '',
      `👤 *${escMd(lead.nombre)}*`,
      `💇 ${escMd(lead.salon)}`,
      `📞 ${escMd(lead.telefono)}`,
      '',
      `📱 Canal principal: ${escMd(lead.canal || '—')}`,
      `👥 Equipo: ${escMd(lead.trabajadoras || '—')}`,
      `📉 Citas perdidas/sem: ${escMd(lead.citas_perdidas || '—')}`,
      `💬 Dolor principal: ${escMd(lead.mayor_dolor || '—')}`,
      '',
      `🎯 Plan recomendado: ${planLabel}`,
      `🔗 UTM: ${escMd(lead.utm || '(directo)')}`,
      `⏱ ${new Date().toLocaleString('es-ES', { timeZone: 'Europe/Madrid' })}`,
    ].join('\n');

    try {
      await fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: CHAT,
          text,
          parse_mode: 'Markdown',
          disable_web_page_preview: true,
        }),
      });
    } catch (e) {
      console.error('Telegram error', e);
    }
  }

  if (process.env.BREVO_API_KEY) {
    try {
      await fetch('https://api.brevo.com/v3/contacts', {
        method: 'POST',
        headers: {
          'api-key': process.env.BREVO_API_KEY,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: `${(lead.telefono || 'lead').replace(/\D/g, '')}@nexux.pro`,
          attributes: {
            FIRSTNAME: lead.nombre,
            SMS: lead.telefono,
            SALON: lead.salon,
            CANAL: lead.canal,
            DOLOR: lead.mayor_dolor,
            PLAN: lead._plan,
          },
          listIds: process.env.BREVO_LIST_ID ? [Number(process.env.BREVO_LIST_ID)] : [],
          updateEnabled: true,
        }),
      });
    } catch (e) {
      console.error('Brevo error', e);
    }
  }

  return res.status(200).json({ ok: true });
}

function escMd(s) {
  return String(s).replace(/[_*[\]()`]/g, ' ');
}
