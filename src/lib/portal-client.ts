const BASE_URL = import.meta.env.NEXUX_CLIENTS_URL || 'https://pi.nexux.pro';

export interface Appointment {
  id: string;
  clientPhone?: string;
  clientName?: string;
  client_phone?: string;
  client_name?: string;
  service: string;
  datetime: string;
  duration_min?: number;
  status: 'confirmed' | 'cancelled';
}

export interface ClientData {
  clientId: string;
  name: string;
  timezone?: string;
  plan: 'starter' | 'pro' | 'total' | 'recepcionista';
  active: boolean;
  botStatus: 'connected' | 'disconnected' | 'pending_qr';
  qrPngBase64?: string;
  nextAppointments: Appointment[];
  metrics: {
    conversationCount: number;
    conversationLimit: number | null;
    appointmentsBooked: number;
    appointmentsCancelled: number;
  };
  schedule: Record<string, { open: string; close: string } | null>;
  services?: { name: string; duration: number; price: number }[];
  billing?: {
    isTrial: boolean;
    trialEndsAt: string | null;
    expiresAt: string | null;
  };
  channels: {
    whatsapp: { provider: 'baileys' | 'twilio'; connected: boolean };
    telegram: { enabled: boolean; ownerLinked: boolean };
  };
}

export interface ClientConfig {
  schedule?: Record<string, { open: string; close: string } | null>;
  services?: unknown;
  botName?: string;
  channels?: {
    whatsapp?: {
      provider?: 'baileys' | 'twilio';
    };
  };
}

export async function getClientData(clientId: string, token: string): Promise<ClientData | null> {
  try {
    const response = await fetch(`${BASE_URL}/client/${clientId}/status`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.status === 401 || response.status === 404) return null;
    if (!response.ok) return null;

    return (await response.json()) as ClientData;
  } catch {
    return null;
  }
}

export async function updateClientConfig(clientId: string, token: string, config: Partial<ClientConfig>): Promise<boolean> {
  try {
    const response = await fetch(`${BASE_URL}/client/${clientId}/config`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(config),
    });

    return response.ok;
  } catch {
    return false;
  }
}

export interface PublicClientInfo {
  clientId: string;
  salon_name: string;
  services: { name: string; duration: number; price: number }[];
  schedule: Record<string, unknown>;
}

export async function getPublicClientData(clientId: string): Promise<PublicClientInfo | null> {
  try {
    const response = await fetch(`${BASE_URL}/public/${clientId}`);
    if (!response.ok) return null;
    return (await response.json()) as PublicClientInfo;
  } catch { return null; }
}

export interface Invoice {
  id: string;
  date: number;
  amount: number;
  currency: string;
  status: string;
  pdf: string | null;
  hosted_url: string | null;
  description: string | null;
}

export async function getClientInvoices(clientId: string, token: string): Promise<Invoice[]> {
  try {
    const response = await fetch(`${BASE_URL}/client/${clientId}/invoices`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) return [];
    return (await response.json()) as Invoice[];
  } catch { return []; }
}

export async function getBillingPortalUrl(clientId: string, token: string): Promise<string | null> {
  try {
    const response = await fetch(`${BASE_URL}/client/${clientId}/billing-portal`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) return null;
    const data = await response.json() as { url?: string };
    return data.url || null;
  } catch { return null; }
}

export async function resendPortalLink(clientId: string, email: string): Promise<void> {
  const url = new URL(`${BASE_URL}/client/${clientId}/resend-link`);
  url.searchParams.set('email', email);

  await fetch(url, {
    method: 'GET',
  }).catch(() => {});
}

export async function fetchAllAppointments(clientId: string, token: string): Promise<any[]> {
  try {
    const response = await fetch(`${BASE_URL}/client/${clientId}/appointments`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) return [];
    return (await response.json()) as any[];
  } catch { return []; }
}

export async function cancelAppointmentById(clientId: string, token: string, aptId: string): Promise<boolean> {
  try {
    const response = await fetch(`${BASE_URL}/client/${clientId}/appointments/${aptId}/cancel`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.ok;
  } catch { return false; }
}

export async function updateAppointmentById(
  clientId: string,
  token: string,
  aptId: string,
  data: { client_name?: string; client_phone?: string; service?: string; datetime?: string; duration_min?: number; professional_id?: string },
): Promise<{ ok: boolean; status: number; error?: string }> {
  try {
    const response = await fetch(`${BASE_URL}/client/${clientId}/appointments/${aptId}/update`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify(data),
    });
    const payload = await response.json().catch(() => ({})) as { error?: string };
    return { ok: response.ok, status: response.status, error: payload.error };
  } catch {
    return { ok: false, status: 502, error: 'connection_error' };
  }
}

export async function createAppointmentManual(
  clientId: string,
  token: string,
  data: {
    client_name: string;
    client_phone?: string;
    service: string;
    datetime: string;
    duration_min?: number;
    professional_id?: string;
  },
): Promise<{ ok: boolean; status: number; error?: string; message?: string }> {
  // Antes devolvia solo true/false y se perdia el motivo. Ahora el backend
  // responde 409 cuando la hora choca con otra cita, y eso hay que poder
  // contarselo al usuario en vez de un "no se pudo" generico.
  try {
    const response = await fetch(`${BASE_URL}/client/${clientId}/appointments`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify(data),
    });
    const payload = await response.json().catch(() => ({})) as { error?: string; message?: string };
    return { ok: response.ok, status: response.status, error: payload.error, message: payload.message };
  } catch {
    return { ok: false, status: 502, error: 'connection_error' };
  }
}

export interface Professional {
  id: string;
  name: string;
  active?: boolean;
  color?: string | null;
  priority?: number;
}

export async function fetchProfessionals(
  clientId: string,
  token: string,
): Promise<{ ok: boolean; mode?: string; professionals?: Professional[]; error?: string }> {
  try {
    const response = await fetch(`${BASE_URL}/client/${clientId}/professionals`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const payload = await response.json().catch(() => ({}));
    return response.ok ? payload : { ok: false, error: payload?.error || 'request_failed' };
  } catch {
    return { ok: false, error: 'connection_error' };
  }
}

export async function saveProfessionals(
  clientId: string,
  token: string,
  data: { mode?: string; professionals?: Professional[] },
): Promise<{ ok: boolean; status: number; mode?: string; professionals?: Professional[]; error?: string; message?: string }> {
  try {
    const response = await fetch(`${BASE_URL}/client/${clientId}/professionals`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body: JSON.stringify(data),
    });
    const payload = await response.json().catch(() => ({}));
    return { ...payload, ok: response.ok, status: response.status };
  } catch {
    return { ok: false, status: 502, error: 'connection_error' };
  }
}

export async function reportMissedCall(clientId: string, token: string, phone: string): Promise<{ ok: boolean; channel?: string }> {
  try {
    const response = await fetch(BASE_URL + '/client/' + clientId + '/missed-call', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + token },
      body: JSON.stringify({ phone }),
    });
    return await response.json();
  } catch { return { ok: false }; }
}

export async function regenerateWeb(clientId: string, token: string): Promise<{ ok: boolean; url?: string }> {
  try {
    const response = await fetch(BASE_URL + '/client/' + clientId + '/regenerate-web', {
      method: 'POST',
      headers: { Authorization: 'Bearer ' + token },
    });
    return await response.json();
  } catch { return { ok: false }; }
}
