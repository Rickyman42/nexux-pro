import { conLimite } from './espera-limitada.mjs';

declare const Stripe: undefined | ((key: string) => any);

const PLAN_LABELS: Record<string, string> = {
  recepcionista: 'Nexux Recepcionista IA — 29€/mes',
};

let stripeInstance: any = null;
let embeddedCheckout: any = null;

// Cuanto se espera a que Stripe pinte su formulario antes de dar la espera por
// perdida. Hasta el 14-sep-2026 no habia limite: si Stripe tardaba o se
// atascaba, la persona se quedaba mirando la ruedecita para siempre, sin error,
// sin aviso y sin que nosotros nos enterasemos de nada.
//
// El numero no es a ojo: el guion de Stripe tardaba entre 4,8 y 7,2 segundos en
// llegar, medido el 14-sep en la Pi con buena conexion. Con datos flojos puede
// ser bastante mas, asi que 20 s da margen de sobra a una conexion lenta pero
// sana. Y como ahora se manda cuanto tardo cada vez que SI sale, el numero se
// podra ajustar con datos en vez de con la intuicion.
const ESPERA_MAXIMA_MS = 20000;

// Cada intento lleva su numero. Si el de vuelta ya no es el ultimo, es que la
// persona cerro la ventana o volvio a pulsar: lo que llegue tarde se tira en vez
// de montarse en una ventana que ya no existe.
let intentoActual = 0;
let ultimoIntento: { plan: string; salon: string } | null = null;

/** Manda una senal de medicion. Medir NUNCA puede romper el pago. */
function senal(nombre: string, datos: Record<string, unknown> = {}) {
  try {
    (window as any).nxMeasure?.(nombre, datos);
  } catch {
    // Si la medicion falla, el pago sigue.
  }
}

/** Cierra una pantalla de Stripe que ya no va a usar nadie. */
function tirar(instancia: any) {
  try {
    instancia?.destroy();
  } catch {
    // Si ya estaba cerrada, da igual.
  }
}

function motivoDe(error: unknown): string {
  const mensaje = (error as any)?.message;
  return typeof mensaje === 'string' && mensaje ? mensaje.slice(0, 40) : 'desconocido';
}

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

  // Al pago directo. El nombre del negocio se pregunta DENTRO de la pantalla de
  // Stripe (lo monta api/stripe/create-session.js), no antes.
  //
  // Hasta el 14-sep-2026 aqui salia un formulario pidiendolo. Medido: de 7
  // personas que pulsaron comprar, solo 2 llegaron al pago. Cinco se cayeron en
  // esa pregunta -- que ademas se les vuelve a hacer despues, porque Lara la
  // hace en el alta.
  //
  // Si Lara ya lo sabe, se manda y Stripe no lo pregunta.
  const yaSabido = (leerLaraData().salon || '').trim();
  datos?.setAttribute('hidden', '');
  negocio?.setAttribute('aria-invalid', 'false');
  loading.removeAttribute('hidden');
  return abrirPagoStripe(plan, yaSabido);
}

async function abrirPagoStripe(plan: string, salon: string) {
  const { loading, errorEl, mount, datos } = getElements();
  if (!loading || !errorEl || !mount) return;

  const miIntento = ++intentoActual;
  ultimoIntento = { plan, salon };
  const arrancado = Date.now();
  const yaNoImporta = () => miIntento !== intentoActual;

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
    const instancia = await conLimite(
      stripe.initEmbeddedCheckout({ clientSecret }),
      ESPERA_MAXIMA_MS,
      tirar,
    );

    // Si mientras cargaba cerraron la ventana o volvieron a pulsar, esta
    // pantalla ya no le sirve a nadie: cerrarla en vez de montarla.
    if (yaNoImporta()) {
      tirar(instancia);
      return;
    }

    embeddedCheckout = instancia;
    loading.setAttribute('hidden', '');
    instancia.mount('#stripe-checkout-mount');

    // La senal que faltaba. Hasta ahora solo sabiamos quien PULSABA comprar, no
    // a quien le llegaba a salir el formulario: un pago atascado y un cliente
    // que se lo piensa daban exactamente el mismo dato.
    senal('checkout_form_shown', { plan, ms: Date.now() - arrancado });
  } catch (error) {
    if (yaNoImporta()) return;
    loading.setAttribute('hidden', '');
    errorEl.removeAttribute('hidden');
    senal('checkout_form_failed', {
      plan,
      motivo: motivoDe(error),
      ms: Date.now() - arrancado,
    });
    console.error('[checkout] open failed', error);
  }
}

export function closeCheckout() {
  const { modal, loading, errorEl, mount, datos } = getElements();
  if (!modal || !loading || !errorEl || !mount) return;

  // Cualquier carga que siga en marcha deja de importar: si llega despues, se
  // tira. Antes se montaba igual, en una ventana ya cerrada.
  intentoActual += 1;

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

  // Volver a intentarlo sin tener que cerrar y buscar otra vez el boton.
  document.getElementById('checkout-reintentar')?.addEventListener('click', () => {
    const intento = ultimoIntento;
    if (!intento) return;
    senal('checkout_form_retried', { plan: intento.plan });
    void abrirPagoStripe(intento.plan, intento.salon);
  });

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
