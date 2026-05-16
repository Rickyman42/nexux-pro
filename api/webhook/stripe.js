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
    await Promise.all([
      notifyTelegram(session),
      sendConfirmationEmail(session),
    ]);
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

async function sendConfirmationEmail(session) {
  const apiKey = process.env.BREVO_API_KEY;
  if (!apiKey || !session) return;

  const toEmail = session.customer_details?.email;
  const toName = session.customer_details?.name || 'Clienta';
  if (!toEmail) return;

  const plan = session.metadata?.plan || 'pro';
  const planNames = { starter: 'Lara Starter', pro: 'Lara Pro', total: 'Lara Total' };
  const planLabel = planNames[plan] || plan;
  const amount = session.amount_total ? `${(session.amount_total / 100).toFixed(0)}` : '—';

  const htmlBody = `
<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#0B0D12;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0B0D12;padding:40px 20px">
    <tr><td align="center">
      <table width="100%" style="max-width:560px;background:#141720;border-radius:20px;border:1px solid #1E2233;overflow:hidden">
        <tr>
          <td style="background:#141720;padding:32px 40px 0;text-align:center">
            <div style="display:inline-block;background:rgba(78,205,196,0.1);border-radius:12px;padding:8px 20px;margin-bottom:24px">
              <span style="color:#4ECDC4;font-size:13px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase">Nexux Pro</span>
            </div>
            <h1 style="color:#E8EAF0;font-size:28px;font-weight:700;margin:0 0 8px;line-height:1.2">¡Pago confirmado! 🎉</h1>
            <p style="color:#8B92A8;font-size:16px;margin:0 0 32px">Ya tienes el <strong style="color:#E8EAF0">${planLabel}</strong> activado</p>
          </td>
        </tr>
        <tr>
          <td style="padding:0 40px 32px">
            <div style="background:#1A1F2E;border-radius:14px;padding:20px 24px;margin-bottom:24px">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="color:#8B92A8;font-size:13px;padding:6px 0">Plan contratado</td>
                  <td style="color:#E8EAF0;font-size:13px;font-weight:600;text-align:right;padding:6px 0">${planLabel}</td>
                </tr>
                <tr>
                  <td style="color:#8B92A8;font-size:13px;padding:6px 0;border-top:1px solid #1E2233">Importe mensual</td>
                  <td style="color:#4ECDC4;font-size:13px;font-weight:700;text-align:right;padding:6px 0;border-top:1px solid #1E2233">${amount}€/mes</td>
                </tr>
              </table>
            </div>
            <p style="color:#8B92A8;font-size:15px;line-height:1.7;margin:0 0 20px">
              Hola <strong style="color:#E8EAF0">${toName.split(' ')[0]}</strong>,<br><br>
              Hemos recibido tu pago correctamente. En menos de <strong style="color:#E8EAF0">24 horas</strong> nos pondremos en contacto contigo para activar Lara en tu salón y dejarlo todo listo.
            </p>
            <p style="color:#8B92A8;font-size:15px;line-height:1.7;margin:0 0 32px">
              Si tienes cualquier pregunta antes, responde a este email o escríbenos directamente.
            </p>
            <div style="text-align:center">
              <a href="https://nexux.pro" style="display:inline-block;background:#4ECDC4;color:#0B0D12;font-size:15px;font-weight:700;padding:14px 32px;border-radius:50px;text-decoration:none">
                Ir a nexux.pro →
              </a>
            </div>
          </td>
        </tr>
        <tr>
          <td style="background:#0F1118;padding:20px 40px;text-align:center;border-top:1px solid #1E2233">
            <p style="color:#4A5068;font-size:12px;margin:0">
              Nexux Innovación Digital S.L. · <a href="https://nexux.pro" style="color:#4A5068">nexux.pro</a>
            </p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>`;

  try {
    await fetch('https://api.brevo.com/v3/smtp/email', {
      method: 'POST',
      headers: {
        'api-key': apiKey,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        sender: { name: 'Ricardo de Nexux', email: 'hola@nexux.pro' },
        to: [{ email: toEmail, name: toName }],
        subject: `✅ Pago confirmado — ${planLabel} activado`,
        htmlContent: htmlBody,
      }),
    });
  } catch (error) {
    console.error('[webhook] brevo email error:', error);
  }
}

function escMd(value) {
  return String(value).replace(/[_*[\]()`]/g, ' ');
}
