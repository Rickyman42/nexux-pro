export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(204).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'method_not_allowed' });

  const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
  const { plan } = body;

  // Los planes starter/pro/total se retiraron el 21-ago-2026. Esta lista es la
  // que decide que se puede comprar: si un plan no esta aqui, su boton devuelve
  // invalid_plan y el checkout no llega a abrirse.
  const PLANS = {
    recepcionista: {
      name: 'Nexux Recepcionista IA',
      amount: 2900,
      priceEnv: 'STRIPE_PRICE_RECEPCIONISTA',
      // Precio real creado en Stripe el 21-ago-2026. Se usa si la variable de
      // entorno no esta configurada en Vercel, para que el pago no dependa de eso.
      priceFallback: 'price_1U6jqd2SQwDzHtsFf3wEcuQe',
    },
    equipo: {
      name: 'Nexux Recepcionista Equipo',
      amount: 7900,
      priceEnv: 'STRIPE_PRICE_EQUIPO',
      // Creado en Stripe el 2-sep-2026, mismo motivo que el de arriba: si la
      // variable no esta en Vercel, el pago sigue funcionando.
      priceFallback: 'price_1UBHkE2SQwDzHtsFTVWQ67l5',
    },
  };

  if (!PLANS[plan]) return res.status(400).json({ error: 'invalid_plan' });

  const planData = PLANS[plan];
  const priceId = process.env[planData.priceEnv] || planData.priceFallback;
  const origin = req.headers['x-forwarded-host']
    ? `https://${req.headers['x-forwarded-host']}`
    : 'https://nexux.pro';

  const params = new URLSearchParams();
  params.append('ui_mode', 'embedded_page');
  params.append('mode', 'subscription');
  params.append('return_url', `${origin}/gracias?plan=${plan}`);
  params.append('metadata[plan]', plan);
  // Sin telefono, el asistente no puede arrancar el onboarding solo.
  params.append('phone_number_collection[enabled]', 'true');

  const metadataFields = ['nombre', 'salon', 'telefono', 'ciudad', 'canal', 'trabajadoras'];
  for (const key of metadataFields) {
    const value = body[key];
    if (value !== undefined && value !== null && value !== '') {
      params.append(`metadata[${key}]`, String(value).slice(0, 500));
    }
  }

  if (priceId) {
    params.append('line_items[0][price]', priceId);
    params.append('line_items[0][quantity]', '1');
  } else {
    params.append('line_items[0][price_data][currency]', 'eur');
    params.append('line_items[0][price_data][unit_amount]', String(planData.amount));
    params.append('line_items[0][price_data][product_data][name]', planData.name);
    params.append('line_items[0][price_data][recurring][interval]', 'month');
    params.append('line_items[0][quantity]', '1');
  }

  try {
    const r = await fetch('https://api.stripe.com/v1/checkout/sessions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.STRIPE_SECRET_KEY}`,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Stripe-Version': '2026-04-22.dahlia',
      },
      body: params.toString(),
    });
    if (!r.ok) {
      const err = await r.json().catch(() => ({}));
      console.error('[stripe] session error:', err);
      return res.status(500).json({ error: 'session_create_failed' });
    }
    const session = await r.json();
    res.json({ clientSecret: session.client_secret });
  } catch (e) {
    console.error('[stripe] request error:', e);
    res.status(500).json({ error: 'session_create_failed' });
  }
}
