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
const ATTRIBUTION_KEY = 'nx_attribution';
const PENDING_QUERY_KEY = 'nx_pending_query';
const CHATGPT_LANDING_KEY = 'nx_chatgpt_landing_measured';
const LAST_CHECKOUT_RETURN_KEY = 'nx_last_checkout_return';
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
  const checkoutButton = target?.closest('[data-checkout-plan]');
  if (!checkoutButton) return;

  measure('checkout_started', {
    plan: checkoutButton.getAttribute('data-checkout-plan') || 'recepcionista',
    value: 29,
    currency: 'EUR',
  });
}, { passive: true });

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
