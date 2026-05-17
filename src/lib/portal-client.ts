const BASE_URL = import.meta.env.NEXUX_CLIENTS_URL || 'https://pi.nexux.pro';

export interface Appointment {
  id: string;
  clientPhone: string;
  clientName?: string;
  service: string;
  datetime: string;
  status: 'confirmed' | 'cancelled';
}

export interface ClientData {
  clientId: string;
  name: string;
  plan: 'starter' | 'pro' | 'total';
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

export async function resendPortalLink(clientId: string, email: string): Promise<void> {
  const url = new URL(`${BASE_URL}/client/${clientId}/resend-link`);
  url.searchParams.set('email', email);

  await fetch(url, {
    method: 'GET',
  }).catch(() => {});
}
