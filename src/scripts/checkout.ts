declare const Stripe: undefined | ((key: string) => any);

const PLAN_LABELS: Record<string, string> = {
  recepcionista: 'Nexux Recepcionista IA — 29€/mes',
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
    datos: document.getElementById('checkout-datos') as HTMLFormElement | null,
    negocio: document.getElementById('checkout-negocio') as HTMLInputElement | null,
  };
}

// El nombre del negocio viaja hasta Stripe como metadata[salon] y de ahi al alta
// automatica. Sin el, /provision rechaza la peticion con missing_fields y el
// cliente paga sin recibir cuenta. Antes se leia de sessionStorage.laraData, que
// NADIE escribia: por eso llegaba vacio siempre.
function leerLaraData(): Record<string, any> {
  try {
    return JSON.parse(sessionStorage.getItem('laraData') || '{}');
  } catch {
    return {};
  }
}

function guardarNombreNegocio(salon: string) {
  try {
    const datos = leerLaraData();
    datos.salon = salon;
    sessionStorage.setItem('laraData', JSON.stringify(datos));
  } catch {
    // Si el navegador no deja guardar, el dato viaja igual en esta compra:
    // openCheckout lo lleva en memoria.
  }
}

function getCheckoutBody(plan: string, salonExplicito?: string) {
  const laraData = leerLaraData();

  let ciudadFromUrl: string | undefined;
  const match = location.pathname.match(/^\/ciudad\/([a-z]+)/);
  if (match) {
    ciudadFromUrl = match[1].charAt(0).toUpperCase() + match[1].slice(1);
  }

  return {
    plan,
    nombre: laraData.nombre,
    salon: salonExplicito || laraData.salon,
    telefono: laraData.telefono,
    ciudad: laraData.ciudad || ciudadFromUrl,
    canal: laraData.canal,
    trabajadoras: laraData.trabajadoras,
  };
}

export async function openCheckout(plan: string) {
  const { modal, loading, errorEl, mount, label, datos, negocio } = getElements();
  if (!modal || !loading || !errorEl || !mount || !label) return;

  mount.innerHTML = '';
  errorEl.setAttribute('hidden', '');
  modal.removeAttribute('hidden');
  document.body.style.overflow = 'hidden';
  label.textContent = PLAN_LABELS[plan] || plan;

  // Si Lara ya sabe el nombre del negocio, no se vuelve a preguntar.
  const yaSabido = (leerLaraData().salon || '').trim();
  if (yaSabido) {
    loading.removeAttribute('hidden');
    return abrirPagoStripe(plan, yaSabido);
  }

  if (!datos || !negocio) {
    // Sin el formulario no podemos conseguir el dato: mejor no cobrar a ciegas.
    loading.setAttribute('hidden', '');
    errorEl.removeAttribute('hidden');
    console.error('[checkout] falta el formulario del nombre del negocio');
    return;
  }

  loading.setAttribute('hidden', '');
  datos.removeAttribute('hidden');
  datos.dataset.plan = plan;
  negocio.value = '';
  negocio.removeAttribute('aria-invalid');
  negocio.focus();
}

async function abrirPagoStripe(plan: string, salon: string) {
  const { loading, errorEl, mount, datos } = getElements();
  if (!loading || !errorEl || !mount) return;

  datos?.setAttribute('hidden', '');
  loading.removeAttribute('hidden');
  errorEl.setAttribute('hidden', '');

  try {
    const body = getCheckoutBody(plan, salon);
    const res = await fetch('/api/stripe/create-session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      console.error('[checkout] create-session failed', await res.text());
      throw new Error('session_failed');
    }

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
  const { modal, loading, errorEl, mount, datos } = getElements();
  if (!modal || !loading || !errorEl || !mount) return;

  modal.setAttribute('hidden', '');
  document.body.style.overflow = '';
  mount.innerHTML = '';
  loading.removeAttribute('hidden');
  errorEl.setAttribute('hidden', '');
  datos?.setAttribute('hidden', '');

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
        <p>Te hemos enviado un correo con el enlace a tu panel. Revisa tu bandeja.</p>
      </div>
    </div>
  `;

  document.body.prepend(banner);
}

function initCheckout() {
  document.getElementById('checkout-close')?.addEventListener('click', closeCheckout);

  document.getElementById('checkout-datos')?.addEventListener('submit', event => {
    event.preventDefault();
    const form = event.currentTarget as HTMLFormElement;
    const campo = document.getElementById('checkout-negocio') as HTMLInputElement | null;
    const salon = (campo?.value || '').trim();
    if (!salon) {
      campo?.setAttribute('aria-invalid', 'true');
      campo?.focus();
      return;
    }
    campo?.removeAttribute('aria-invalid');
    guardarNombreNegocio(salon);
    void abrirPagoStripe(form.dataset.plan || 'recepcionista', salon);
  });

  document.getElementById('checkout-modal')?.addEventListener('click', event => {
    if (event.target === event.currentTarget) closeCheckout();
  });

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') closeCheckout();
  });

  // Event delegation — catches dynamically added [data-checkout-plan] buttons (e.g. LaraWidget CTA)
  document.addEventListener('click', event => {
    const button = (event.target as Element).closest('[data-checkout-plan]');
    if (button) {
      const plan = button.getAttribute('data-checkout-plan');
      if (plan) void openCheckout(plan);
    }
  });

  const params = new URLSearchParams(window.location.search);
  const sessionId = params.get('session_id');
  if (sessionId) {
    showSuccessMessage();
    window.history.replaceState({}, '', window.location.pathname);
  }
}

initCheckout();
