export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(204).end();
  if (req.method !== 'POST') return res.status(405).json({ error: 'method_not_allowed' });

  const body = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
  const { plan } = body;

  const PLANS = {
    starter: { name: 'Lara Starter', amount: 24900, priceEnv: 'STRIPE_PRICE_STARTER' },
    pro:     { name: 'Lara Pro',     amount: 44900, priceEnv: 'STRIPE_PRICE_PRO' },
    total:   { name: 'Lara Total',   amount: 74900, priceEnv: 'STRIPE_PRICE_TOTAL' },
  };

  if (!PLANS[plan]) return res.status(400).json({ error: 'invalid_plan' });

  const planData = PLANS[plan];
  const priceId = process.env[planData.priceEnv];
  const origin = req.headers['x-forwarded-host']
    ? `https://${req.headers['x-forwarded-host']}`
    : 'https://nexux.pro';

  const params = new URLSearchParams();
  params.append('ui_mode', 'embedded_page');
  params.append('mode', 'subscription');
  params.append('return_url', `${origin}/paquetes/${plan}?session_id={CHECKOUT_SESSION_ID}`);

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
        'Stripe-Version': '2025-08-27.basil',
      },
      body: params.toString(),
    });
    if (!r.ok) {
      const err = await r.json().catch(() => ({}));
      console.error('[stripe] session error:', err);
      return res.status(500).json({ error: "session_create_failed", detail: err?.error?.message || JSON.stringify(err) });
    }
    const session = await r.json();
    res.json({ clientSecret: session.client_secret });
  } catch (e) {
    console.error('[stripe] request error:', e);
    res.status(500).json({ error: 'session_create_failed' });
  }
}
