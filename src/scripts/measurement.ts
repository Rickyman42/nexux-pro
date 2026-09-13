type NxProperties = Record<string, string | number | boolean | undefined>;

type NxWindow = Window & {
  nxMeasure?: (eventName: string, properties?: NxProperties) => void;
  umami?: { track: (eventName: string, properties?: NxProperties) => void };
  plausible?: (eventName: string, options?: { props?: NxProperties }) => void;
  gtag?: (...args: unknown[]) => void;
  fbq?: (...args: unknown[]) => void;
  oaiq?: (...args: unknown[]) => void;
};

const nxWindow = window as NxWindow;
import { esPaginaMedible } from './paginas-medidas.mjs';

const ATTRIBUTION_KEY = 'nx_attribution';
const PENDING_QUERY_KEY = 'nx_pending_query';
const CHATGPT_LANDING_KEY = 'nx_chatgpt_landing_measured';
const LAST_CHECKOUT_RETURN_KEY = 'nx_last_checkout_return';
// El mapa divide la pagina en una cuadricula de 12 x 24. Se guarda la CASILLA,
// nunca el punto exacto: asi no se puede reconstruir el recorrido de nadie.
const MAPA_COLUMNAS = 12;
const MAPA_FILAS = 24;
const MAPA_TOPE_ATENCION = 18;   // puntos de raton por carga
const MAPA_TOPE_CLICS = 40;      // por si alguien martillea la pantalla
const ATTRIBUTION_PARAMS = [
  'oppref',
  'utm_source',
  'utm_medium',
  'utm_campaign',
  'utm_content',
  'utm_term',
] as const;

function safeSessionGet(key: string): string | null {
  try {
    return sessionStorage.getItem(key);
  } catch {
    return null;
  }
}

function safeSessionSet(key: string, value: string): void {
  try {
    sessionStorage.setItem(key, value);
  } catch {}
}

function safeSessionRemove(key: string): void {
  try {
    sessionStorage.removeItem(key);
  } catch {}
}

function readAttribution(): NxProperties {
  try {
    return JSON.parse(safeSessionGet(ATTRIBUTION_KEY) || '{}');
  } catch {
    return {};
  }
}

function captureAttribution(): NxProperties {
  const params = new URLSearchParams(location.search || safeSessionGet(PENDING_QUERY_KEY) || '');
  const attribution = readAttribution();

  for (const key of ATTRIBUTION_PARAMS) {
    const value = params.get(key);
    if (value) attribution[key] = value.slice(0, 160);
  }

  if (!attribution.referrer_host && document.referrer) {
    try {
      const referrerHost = new URL(document.referrer).hostname.replace(/^www\./, '');
      if (referrerHost !== location.hostname.replace(/^www\./, '')) {
        attribution.referrer_host = referrerHost.slice(0, 160);
      }
    } catch {}
  }

  safeSessionSet(ATTRIBUTION_KEY, JSON.stringify(attribution));
  return attribution;
}

function publicProperties(properties: NxProperties = {}): NxProperties {
  return {
    ...readAttribution(),
    page_path: location.pathname,
    ...properties,
  };
}

function sendWhenReady(send: () => boolean, attempts = 0): void {
  if (send() || attempts >= 40) return;
  window.setTimeout(() => sendWhenReady(send, attempts + 1), 500);
}

function sendConsentTrackers(eventName: string, properties: NxProperties): void {
  if (localStorage.getItem('nx_cookie_consent') !== 'accepted') return;

  if (nxWindow.gtag) {
    const gaEvent = eventName === 'checkout_started' ? 'begin_checkout' : eventName;
    nxWindow.gtag('event', gaEvent, properties);
  }

  if (nxWindow.fbq) {
    if (eventName === 'checkout_started') {
      nxWindow.fbq('track', 'InitiateCheckout', properties);
    } else {
      nxWindow.fbq('trackCustom', eventName, properties);
    }
  }
}

function openAiEvent(eventName: string, properties: NxProperties):
  { name: string; data: Record<string, any>; options?: Record<string, any> } | null {
  if (eventName === 'chatgpt_ads_landing') {
    return {
      name: 'page_viewed',
      data: {
        type: 'contents',
        contents: [{ id: location.pathname || '/', name: document.title, content_type: 'page' }],
      },
    };
  }

  if (eventName === 'demo_started') {
    return {
      name: 'custom',
      data: { type: 'custom' },
      options: { custom_event_name: 'demo_started' },
    };
  }

  if (eventName === 'demo_booking_created') {
    return { name: 'appointment_scheduled', data: { type: 'customer_action' } };
  }

  if (eventName === 'checkout_started') {
    return {
      name: 'checkout_started',
      data: {
        type: 'contents',
        amount: 2900,
        currency: 'EUR',
        contents: [{
          id: String(properties.plan || 'recepcionista'),
          name: 'Nexux Recepcionista IA',
          content_type: 'plan',
          amount: 2900,
          currency: 'EUR',
          quantity: 1,
        }],
      },
    };
  }

  return null;
}

function sendOpenAiTracker(eventName: string, properties: NxProperties): void {
  if (localStorage.getItem('nx_cookie_consent') !== 'accepted' || !nxWindow.oaiq) return;
  const event = openAiEvent(eventName, properties);
  if (!event) return;
  nxWindow.oaiq('measure', event.name, event.data, {
    ...(event.options || {}),
    event_id: `nx_${eventName}_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
  });
}

function measure(eventName: string, properties: NxProperties = {}): void {
  const payload = publicProperties(properties);

  sendWhenReady(() => {
    if (!nxWindow.umami || typeof nxWindow.umami.track !== 'function') return false;
    nxWindow.umami.track(eventName, payload);
    return true;
  });

  sendWhenReady(() => {
    if (typeof nxWindow.plausible !== 'function') return false;
    nxWindow.plausible(eventName, { props: payload });
    return true;
  });

  sendConsentTrackers(eventName, payload);
  sendOpenAiTracker(eventName, payload);
  document.dispatchEvent(new CustomEvent('nx:measurement', {
    detail: { eventName, properties: payload },
  }));
}

// Umami recibe el mapa; los pixeles de publicidad NO. Estos puntos no son una
// conversion ni le interesan a nadie fuera de aqui.
function medirSoloEnUmami(evento: string, propiedades: NxProperties = {}): void {
  const carga = publicProperties(propiedades);
  sendWhenReady(() => {
    if (!nxWindow.umami || typeof nxWindow.umami.track !== 'function') return false;
    nxWindow.umami.track(evento, carga);
    return true;
  });
}

/**
 * En que casilla de la cuadricula ha caido un punto de la pagina.
 * Devuelve null si el punto no tiene sentido (fuera de pantalla, NaN...).
 */
function casillaDe(x: number, y: number): NxProperties | null {
  if (!Number.isFinite(x) || !Number.isFinite(y) || x < 0 || y < 0) return null;

  const altoPagina = Math.max(
    document.documentElement.scrollHeight,
    document.body?.scrollHeight || 0,
    window.innerHeight,
  );
  const yPagina = Math.min(altoPagina - 1, Math.max(0, y + window.scrollY));
  const xPagina = Math.min(window.innerWidth - 1, Math.max(0, x));

  return {
    grid_x: Math.min(MAPA_COLUMNAS - 1, Math.floor((xPagina / Math.max(window.innerWidth, 1)) * MAPA_COLUMNAS)),
    grid_y: Math.min(MAPA_FILAS - 1, Math.floor((yPagina / Math.max(altoPagina, 1)) * MAPA_FILAS)),
    device: window.innerWidth < 768 ? 'mobile' : 'desktop',
  };
}

// Lo que de verdad se puede pulsar. Si un clic no cae en nada de esto, la
// persona ha intentado tocar algo que no era un boton: eso es justo lo que hay
// que ver en el mapa, y no se ve de ninguna otra forma.
const SELECTOR_PULSABLE = 'a,button,input,select,textarea,summary,label,[role="button"],[data-checkout-plan],[data-open-lara],[onclick]';

/**
 * Mapa de calor de la pagina: donde pulsan, hasta donde bajan y donde se
 * entretiene el raton.
 *
 * NO va detras del aviso de cookies, y es a proposito. Aqui no se guarda nada
 * en el aparato de nadie, no hay identificadores, no hay texto escrito y no hay
 * recorridos: solo el numero de una casilla de una cuadricula de 12 x 24. Es la
 * misma categoria que la analitica de Umami, que ya mide a todo el mundo sin
 * pedir permiso. Si se atara al consentimiento, mediria solo a la minoria que
 * acepta todo y los numeros mentirian sin avisar.
 *
 * Lo que SI sigue detras del consentimiento son los pixeles de Google, Meta y
 * OpenAI, que es lo que realmente lo necesita.
 */
function montarMapaDeCalor(): void {
  if (!esPaginaMedible(location.pathname)) return;

  const casillasConRaton = new Set<string>();
  const hitosDeScroll = new Set<number>();
  let clics = 0;
  let ultimoRaton = 0;
  let scrollPendiente = false;

  document.addEventListener('click', event => {
    if (clics >= MAPA_TOPE_CLICS) return;
    const casilla = casillaDe(event.clientX, event.clientY);
    if (!casilla) return;
    clics += 1;

    const destino = event.target as Element | null;
    medirSoloEnUmami('heatmap_click', {
      ...casilla,
      sobre: destino?.closest(SELECTOR_PULSABLE) ? 'pulsable' : 'nada',
    });
  }, { passive: true });

  document.addEventListener('pointermove', event => {
    if (event.pointerType !== 'mouse' || Date.now() - ultimoRaton < 1500) return;
    if (casillasConRaton.size >= MAPA_TOPE_ATENCION) return;
    const casilla = casillaDe(event.clientX, event.clientY);
    if (!casilla) return;

    const clave = `${casilla.device}:${casilla.grid_x}:${casilla.grid_y}`;
    if (casillasConRaton.has(clave)) return;
    casillasConRaton.add(clave);
    ultimoRaton = Date.now();
    medirSoloEnUmami('heatmap_hover', casilla);
  }, { passive: true });

  const mirarScroll = () => {
    scrollPendiente = false;
    const altoPagina = Math.max(document.documentElement.scrollHeight, document.body?.scrollHeight || 0);
    const hasta = altoPagina <= window.innerHeight
      ? 100
      : Math.min(100, Math.floor(((window.scrollY + window.innerHeight) / altoPagina) * 100));

    for (const hito of [25, 50, 75, 100]) {
      if (hasta < hito || hitosDeScroll.has(hito)) continue;
      hitosDeScroll.add(hito);
      medirSoloEnUmami('scroll_depth_reached', {
        depth_percent: hito,
        device: window.innerWidth < 768 ? 'mobile' : 'desktop',
      });
    }
  };

  window.addEventListener('scroll', () => {
    if (scrollPendiente) return;
    scrollPendiente = true;
    window.requestAnimationFrame(mirarScroll);
  }, { passive: true });

  // Una pagina que cabe entera en la pantalla nunca dispara scroll, y sin esto
  // no contaria como "vista hasta el final" aunque lo estuviera.
  mirarScroll();
}

const attribution = captureAttribution();
nxWindow.nxMeasure = measure;

const source = String(attribution.utm_source || '').toLowerCase();
const isChatGptLanding = Boolean(attribution.oppref)
  || source.includes('chatgpt')
  || source.includes('openai');

if (isChatGptLanding && !safeSessionGet(CHATGPT_LANDING_KEY)) {
  safeSessionSet(CHATGPT_LANDING_KEY, '1');
  measure('chatgpt_ads_landing');
}

document.addEventListener('click', event => {
  const target = event.target as Element | null;

  // Los botones con `data-track` ya se mandaban a Google, Meta y Plausible
  // desde Layout.astro, pero NO a Umami. Por eso no habia forma de saber
  // cuanta gente pulsaba "Quiero verla responder": el dato estaba en tres
  // sitios y faltaba justo en el que miramos. (encontrado por Codex, 13-sep)
  const accion = target?.closest('[data-track]');
  const nombreAccion = accion?.getAttribute('data-track');
  if (nombreAccion) {
    measure('cta_clicked', {
      cta_name: nombreAccion,
      cta_text: (accion?.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 80),
    });
  }

  const checkoutButton = target?.closest('[data-checkout-plan]');
  if (!checkoutButton) return;

  measure('checkout_started', {
    plan: checkoutButton.getAttribute('data-checkout-plan') || 'recepcionista',
    value: 29,
    currency: 'EUR',
  });
}, { passive: true });

montarMapaDeCalor();

const capturedQuery = location.search || safeSessionGet(PENDING_QUERY_KEY) || '';
const checkoutSession = new URLSearchParams(capturedQuery).get('session_id');
if (checkoutSession && safeSessionGet(LAST_CHECKOUT_RETURN_KEY) !== checkoutSession) {
  safeSessionSet(LAST_CHECKOUT_RETURN_KEY, checkoutSession);
  measure('checkout_returned', {
    plan: 'recepcionista',
    value: 29,
    currency: 'EUR',
  });
}

safeSessionRemove(PENDING_QUERY_KEY);
