declare const Stripe: undefined | ((key: string) => any);

const PLAN_LABELS: Record<string, string> = {
  starter: 'Starter — 249€/mes',
  pro: 'Pro — 449€/mes',
  total: 'Total — 749€/mes',
};

let stripeInstance: any = null;
let embeddedCheckout: any = null;

function getStripe() {
  if (!import.meta.env.PUBLIC_STRIPE_KEY || typeof Stripe !== 'function') {
    throw new Error('stripe_unavailable');
  }

  if (!stripeInstance) {
    stripeInstance = Stripe(import.meta.env.PUBLIC_STRIPE_KEY);
  }

  return stripeInstance;
}

function getElements() {
  return {
    modal: document.getElementById('checkout-modal'),
    loading: document.getElementById('checkout-loading'),
    errorEl: document.getElementById('checkout-error'),
    mount: document.getElementById('stripe-checkout-mount'),
    label: document.getElementById('checkout-plan-label'),
  };
}

export async function openCheckout(plan: string) {
  const { modal, loading, errorEl, mount, label } = getElements();
  if (!modal || !loading || !errorEl || !mount || !label) return;

  mount.innerHTML = '';
  loading.removeAttribute('hidden');
  errorEl.setAttribute('hidden', '');
  modal.removeAttribute('hidden');
  document.body.style.overflow = 'hidden';
  label.textContent = PLAN_LABELS[plan] || plan;

  try {
    const res = await fetch('/api/stripe/create-session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ plan }),
    });

    if (!res.ok) throw new Error('session_failed');

    const { clientSecret } = await res.json();
    if (!clientSecret) throw new Error('missing_client_secret');

    const stripe = getStripe();
    embeddedCheckout = await stripe.initEmbeddedCheckout({ clientSecret });
    loading.setAttribute('hidden', '');
    embeddedCheckout.mount('#stripe-checkout-mount');
  } catch (error) {
    loading.setAttribute('hidden', '');
    errorEl.removeAttribute('hidden');
    console.error('[checkout] open failed', error);
  }
}

export function closeCheckout() {
  const { modal, loading, errorEl, mount } = getElements();
  if (!modal || !loading || !errorEl || !mount) return;

  modal.setAttribute('hidden', '');
  document.body.style.overflow = '';
  mount.innerHTML = '';
  loading.removeAttribute('hidden');
  errorEl.setAttribute('hidden', '');

  if (embeddedCheckout) {
    embeddedCheckout.destroy();
    embeddedCheckout = null;
  }
}

function showSuccessMessage() {
  if (document.querySelector('.checkout-success-banner')) return;

  const banner = document.createElement('div');
  banner.className = 'checkout-success-banner';
  banner.innerHTML = `
    <div class="checkout-success-inner">
      <span>🎉</span>
      <div>
        <strong>¡Pago completado!</strong>
        <p>En menos de 24h te contactamos para activar tu asistente.</p>
      </div>
    </div>
  `;

  document.body.prepend(banner);
}

function initCheckout() {
  document.getElementById('checkout-close')?.addEventListener('click', closeCheckout);

  document.getElementById('checkout-modal')?.addEventListener('click', event => {
    if (event.target === event.currentTarget) closeCheckout();
  });

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') closeCheckout();
  });

  document.querySelectorAll<HTMLButtonElement>('[data-checkout-plan]').forEach(button => {
    button.addEventListener('click', () => {
      const plan = button.getAttribute('data-checkout-plan');
      if (plan) void openCheckout(plan);
    });
  });

  const params = new URLSearchParams(window.location.search);
  const sessionId = params.get('session_id');
  if (sessionId) {
    showSuccessMessage();
    window.history.replaceState({}, '', window.location.pathname);
  }
}

initCheckout();
