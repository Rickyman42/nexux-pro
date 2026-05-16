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
    const [, provisionResult] = await Promise.all([
      notifyTelegram(session),
      provisionClient(session),
    ]);

    if (provisionResult) {
      await sendOnboardingEmail(session, provisionResult);
    } else {
      await sendConfirmationEmail(session);
      await notifyProvisioningFailed(session);
    }
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

async function provisionClient(session) {
  const provisionUrl = process.env.NEXUX_CLIENTS_URL;
  const secret = process.env.PROVISION_SECRET;
  if (!provisionUrl || !secret) {
    console.error('[webhook] PROVISION env vars missing - skipping provision');
    return null;
  }

  const md = session.metadata || {};
  const payload = {
    stripeSessionId: session.id,
    stripeCustomerId: session.customer || null,
    stripeSubscriptionId: session.subscription || null,
    plan: md.plan,
    nombre: md.nombre || session.customer_details?.name || null,
    salon: md.salon || null,
    telefono: md.telefono || session.customer_details?.phone || null,
    ciudad: md.ciudad || null,
    email: session.customer_details?.email || null,
    canal: md.canal || null,
    trabajadoras: md.trabajadoras || null,
  };

  if (!payload.plan || !payload.salon || !payload.telefono) {
    console.error('[webhook] insufficient metadata for auto-provisioning:', payload);
    return null;
  }

  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 25000);

  try {
    const response = await fetch(`${provisionUrl}/provision`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Provision-Secret': secret,
      },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });

    if (!response.ok) {
      const text = await response.text().catch(() => '');
      console.error(`[webhook] provision HTTP ${response.status}:`, text);
      return null;
    }

    const result = await response.json();
    console.log(`[webhook] provisioned ${result.clientId}`);
    return result;
  } catch (err) {
    console.error('[webhook] provision exception:', err.message);
    return null;
  } finally {
    clearTimeout(timeout);
  }
}

async function sendOnboardingEmail(session, provisionResult) {
  const apiKey = process.env.BREVO_API_KEY;
  if (!apiKey) return;

  const toEmail = session.customer_details?.email;
  const toName = session.customer_details?.name || 'Clienta';
  if (!toEmail) return;

  const plan = session.metadata?.plan || 'pro';
  const planNames = { starter: 'Lara Starter', pro: 'Lara Pro', total: 'Lara Total' };
  const planLabel = planNames[plan] || plan;

  const { clientId, portalUrl, telegramDeepLink, channelSetup, miniWebUrl } = provisionResult;
  const isBaileys = channelSetup?.type === 'baileys';
  const qrPng = channelSetup?.qrPngBase64;
  const twilioNumber = channelSetup?.twilioNumber;
  const firstName = toName.split(' ')[0];

  const whatsappBlock = isBaileys && qrPng ? `
    <div style="background:#1A1F2E;border-radius:14px;padding:24px;margin:24px 0;text-align:center">
      <h3 style="color:#E8EAF0;font-size:16px;margin:0 0 8px">Vincular tu WhatsApp</h3>
      <p style="color:#8B92A8;font-size:13px;margin:0 0 16px">
        Abre WhatsApp en tu movil -> Configuracion -> Dispositivos vinculados -> Vincular dispositivo<br>
        Y escanea este QR (valido 1 minuto, te enviamos uno nuevo si caduca):
      </p>
      <img src="data:image/png;base64,${qrPng}" alt="QR WhatsApp" style="width:240px;height:240px;display:inline-block;background:#fff;padding:12px;border-radius:8px"/>
    </div>
  ` : isBaileys ? `
    <div style="background:#1A1F2E;border-radius:14px;padding:24px;margin:24px 0;text-align:center">
      <p style="color:#E8EAF0;font-size:14px;margin:0">
        En unos segundos te llegara un codigo QR para vincular tu WhatsApp. Si no lo recibes en 10 minutos, responde a este email.
      </p>
    </div>
  ` : twilioNumber ? `
    <div style="background:#1A1F2E;border-radius:14px;padding:24px;margin:24px 0">
      <h3 style="color:#E8EAF0;font-size:16px;margin:0 0 8px">Tu numero de WhatsApp dedicado</h3>
      <p style="color:#4ECDC4;font-size:24px;font-weight:700;margin:0 0 8px">${twilioNumber}</p>
      <p style="color:#8B92A8;font-size:13px;margin:0">
        Comparte este numero con tus clientas. Lara responde automaticamente 24h.
      </p>
    </div>
  ` : '';

  const htmlBody = `<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#0B0D12;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#0B0D12;padding:40px 20px">
  <tr><td align="center">
  <table width="100%" style="max-width:600px;background:#141720;border-radius:20px;border:1px solid #1E2233;overflow:hidden">
    <tr><td style="padding:32px 40px;text-align:center">
      <div style="display:inline-block;background:rgba(78,205,196,0.1);border-radius:12px;padding:8px 20px;margin-bottom:24px">
        <span style="color:#4ECDC4;font-size:13px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase">Nexux Pro</span>
      </div>
      <h1 style="color:#E8EAF0;font-size:28px;font-weight:700;margin:0 0 8px">Tu Lara esta lista</h1>
      <p style="color:#8B92A8;font-size:16px;margin:0 0 8px">Plan <strong style="color:#E8EAF0">${planLabel}</strong> activo</p>
    </td></tr>
    <tr><td style="padding:0 40px 32px">
      <p style="color:#8B92A8;font-size:15px;line-height:1.7;margin:0 0 24px">
        Hola <strong style="color:#E8EAF0">${firstName}</strong>,<br><br>
        He preparado tu bot Lara con todos los servicios y horario por defecto. Solo te quedan 2 minutos para tenerlo funcionando.
      </p>

      <a href="${portalUrl}" style="display:block;text-align:center;background:#4ECDC4;color:#0B0D12;font-size:16px;font-weight:700;padding:16px 32px;border-radius:50px;text-decoration:none;margin:0 0 24px">
        Entrar a tu Portal ->
      </a>

      <p style="color:#8B92A8;font-size:13px;line-height:1.6;margin:0 0 24px;text-align:center">
        En el portal puedes editar horarios, servicios, precios y ver tus citas en tiempo real.
      </p>

      ${whatsappBlock}

      <div style="background:#1A1F2E;border-radius:14px;padding:20px 24px;margin:0 0 24px">
        <h3 style="color:#E8EAF0;font-size:15px;margin:0 0 8px">Recibir notificaciones por Telegram</h3>
        <p style="color:#8B92A8;font-size:13px;line-height:1.6;margin:0 0 12px">
          Cada nueva cita y resumen diario te llega aqui. Pulsa, dale a "Iniciar" y listo:
        </p>
        <a href="${telegramDeepLink}" style="display:inline-block;color:#4ECDC4;font-size:14px;font-weight:600;text-decoration:none">-> Activar Telegram</a>
      </div>

      ${miniWebUrl ? `
      <div style="background:#1A1F2E;border-radius:14px;padding:20px 24px;margin:0 0 24px">
        <h3 style="color:#E8EAF0;font-size:15px;margin:0 0 8px">Tu mini-web esta online</h3>
        <p style="color:#8B92A8;font-size:13px;line-height:1.6;margin:0 0 12px">
          Tus clientas pueden ver servicios y reservar desde aqui:
        </p>
        <a href="${miniWebUrl}" style="color:#4ECDC4;font-size:14px;font-weight:600;text-decoration:none">${miniWebUrl}</a>
      </div>
      ` : ''}

      <p style="color:#8B92A8;font-size:13px;line-height:1.7;margin:0">
        Client ID: <strong style="color:#E8EAF0">${clientId}</strong><br><br>
        Algo no funciona como esperabas? Responde a este email y lo revisamos contigo.
      </p>
    </td></tr>
    <tr><td style="background:#0F1118;padding:20px 40px;text-align:center;border-top:1px solid #1E2233">
      <p style="color:#4A5068;font-size:12px;margin:0">
        Nexux Innovacion Digital S.L. · <a href="https://nexux.pro" style="color:#4A5068">nexux.pro</a>
      </p>
    </td></tr>
  </table>
  </td></tr>
</table>
</body></html>`;

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
        subject: `Tu Lara ${planLabel} esta lista - entra a tu portal`,
        htmlContent: htmlBody,
      }),
    });
    console.log(`[webhook] onboarding email sent to ${toEmail}`);
  } catch (err) {
    console.error('[webhook] onboarding email error:', err);
  }
}

async function notifyProvisioningFailed(session) {
  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chat = process.env.TELEGRAM_CHAT_ID;
  if (!token || !chat) return;

  const md = session.metadata || {};
  const text = [
    'PROVISIONING FAILED - manual handling required',
    '',
    `Cliente: ${escMd(md.nombre || session.customer_details?.name || '—')}`,
    `Salon: ${escMd(md.salon || '—')}`,
    `Telefono: ${escMd(md.telefono || session.customer_details?.phone || '—')}`,
    `Email: ${escMd(session.customer_details?.email || '—')}`,
    `Ciudad: ${escMd(md.ciudad || '—')}`,
    `Plan: ${escMd(md.plan || '—')}`,
    '',
    `Session ID: ${escMd(session.id)}`,
    `Customer ID: ${escMd(session.customer || '—')}`,
    `Subscription ID: ${escMd(session.subscription || '—')}`,
    '',
    'El cliente recibira email generico de pago confirmado. Provisionar manualmente:',
    'ssh pi -> cd ~/nexux-clients && node provision.js',
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
  } catch (e) {
    console.error('[webhook] telegram alert error', e);
  }
}

function escMd(value) {
  return String(value).replace(/[_*[\]()`]/g, ' ');
}
