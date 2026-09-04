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
    const alta = await provisionClient(session);

    if (!alta.ok) {
      // Responder 200 aqui era el fallo que dejaba a un cliente pagando y sin
      // cuenta: para Stripe el evento quedaba entregado y no volvia nunca.
      // Con un 5xx reintenta durante 3 dias con espera creciente, y el reintento
      // encuentra el alta a medias y la termina.
      await notifyProvisioningFailed(session, alta.motivo);
      console.error(`[webhook] alta no confirmada (${alta.motivo}) — devuelvo 503 para que Stripe reintente`);
      return res.status(503).json({ error: 'provisioning_failed', motivo: alta.motivo, retryable: true });
    }

    // El correo de bienvenida lo manda la Pi dentro de /provision, que es quien
    // tiene el enlace del portal, el token y el QR. Aqui no se manda ninguno:
    // los dos remitentes que habia significaban dos correos al mismo cliente.
    // El aviso solo sale en el alta nueva; en un reintento ya estaba avisado.
    if (!alta.alreadyProvisioned) {
      await notifyTelegram(session, alta.clientId);
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

    // Sin esta ventana, una firma valida capturada hace un ano seguiria colando.
    // Es la misma tolerancia de 300 s que usa la Pi y la que recomienda Stripe.
    const antiguedad = Math.abs(Date.now() / 1000 - parseInt(timestamp, 10));
    if (!Number.isFinite(antiguedad) || antiguedad > 300) {
      console.error(`[webhook] firma caducada: ${Math.round(antiguedad)}s`);
      return false;
    }

    const payload = `${timestamp}.${rawBody.toString()}`;
    const expected = crypto.createHmac('sha256', secret).update(payload).digest('hex');

    return crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(signature));
  } catch {
    return false;
  }
}

async function notifyTelegram(session, clientId) {
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
    clientId ? `✅ Alta hecha: ${escMd(clientId)}` : '',
  ].filter(Boolean).join('\n');

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

async function provisionClient(session) {
  const provisionUrl = process.env.NEXUX_CLIENTS_URL;
  const secret = process.env.PROVISION_SECRET;
  if (!provisionUrl || !secret) {
    console.error('[webhook] faltan NEXUX_CLIENTS_URL o PROVISION_SECRET en Vercel');
    return { ok: false, motivo: 'sin_configuracion' };
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
    const faltan = ['plan', 'salon', 'telefono'].filter(k => !payload[k]);
    console.error('[webhook] faltan datos para dar de alta:', faltan.join(', '));
    // Un reintento no va a inventar el dato que falta, pero devolver "todo bien"
    // seria peor: nadie se enteraria. Se avisa y se pide reintento, que ademas da
    // 3 dias de margen para arreglarlo en caliente sin perder al cliente.
    return { ok: false, motivo: `faltan_datos: ${faltan.join(', ')}` };
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
      console.error(`[webhook] provision HTTP ${response.status}:`, text.slice(0, 300));
      return { ok: false, motivo: `provision_http_${response.status}` };
    }

    const result = await response.json();
    if (!result || !result.clientId) {
      console.error('[webhook] /provision respondio 2xx sin clientId:', JSON.stringify(result).slice(0, 200));
      return { ok: false, motivo: 'sin_client_id' };
    }
    console.log(`[webhook] alta confirmada ${result.clientId}${result.alreadyProvisioned ? ' (ya existia)' : ''}`);
    return { ok: true, ...result };
  } catch (err) {
    // Incluye el AbortController: si la Pi tarda demasiado, el alta no esta hecha.
    console.error('[webhook] provision exception:', err.message);
    return { ok: false, motivo: err.name === 'AbortError' ? 'pi_no_responde' : 'excepcion' };
  } finally {
    clearTimeout(timeout);
  }
}

async function notifyProvisioningFailed(session, motivo) {
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
    `Motivo: ${escMd(motivo || 'desconocido')}`,
    '',
    'El alta NO esta hecha y el cliente aun no tiene nada. Se ha respondido 5xx,',
    'asi que Stripe reintentara durante 3 dias con espera creciente: si el fallo',
    'era pasajero se arregla solo. Si en una hora sigue igual, mirar la Pi.',
    'No dar de alta a mano sin comprobar antes que el reintento no lo ha hecho ya.',
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
