import crypto from 'crypto';

export const config = { api: { bodyParser: false } };

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end();

  const rawBody = await new Promise((resolve, reject) => {
    const chunks = [];
    req.on('data', chunk => chunks.push(chunk));
    req.on('end', () => resolve(Buffer.concat(chunks)));
    req.on('error', reject);
  });

  const sig = req.headers['stripe-signature'];
  const secret = process.env.STRIPE_WEBHOOK_SECRET;

  if (!verifyStripeSignature(secret, rawBody, sig)) {
    console.error('[webhook] invalid signature');
    return res.status(400).json({ error: 'invalid_signature' });
  }

  let event;
  try {
    event = JSON.parse(rawBody.toString());
  } catch {
    return res.status(400).json({ error: 'invalid_json' });
  }

  if (event.type === 'checkout.session.completed') {
    const session = event.data?.object;
    await notifyTelegram(session);
  }

  return res.json({ received: true });
}

function verifyStripeSignature(secret, rawBody, sigHeader) {
  if (!secret || !sigHeader) return false;

  try {
    const parts = {};
    sigHeader.split(',').forEach(part => {
      const [key, value] = part.split('=');
      parts[key] = value;
    });

    const timestamp = parts.t;
    const signature = parts.v1;
    if (!timestamp || !signature) return false;

    const payload = `${timestamp}.${rawBody.toString()}`;
    const expected = crypto.createHmac('sha256', secret).update(payload).digest('hex');

    return crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(signature));
  } catch {
    return false;
  }
}

async function notifyTelegram(session) {
  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chat = process.env.TELEGRAM_CHAT_ID;
  if (!token || !chat || !session) return;

  const plan = session.metadata?.plan || '(desconocido)';
  const email = session.customer_details?.email || '—';
  const name = session.customer_details?.name || '—';
  const amount = session.amount_total ? `${(session.amount_total / 100).toFixed(0)}€` : '—';

  const text = [
    '💳 *NUEVO PAGO - NEXUX.PRO*',
    '',
    `👤 ${escMd(name)}`,
    `📧 ${escMd(email)}`,
    `📦 Plan: *${escMd(plan)}*`,
    `💰 ${amount}/mes`,
    `🔗 Session: ${escMd(session.id)}`,
  ].join('\n');

  try {
    await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chat,
        text,
        parse_mode: 'Markdown',
        disable_web_page_preview: true,
      }),
    });
  } catch (error) {
    console.error('[webhook] telegram error:', error);
  }
}

function escMd(value) {
  return String(value).replace(/[_*[\]()`]/g, ' ');
}
