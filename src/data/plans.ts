export type PlanSlug = 'starter' | 'pro' | 'total';

export interface PlanFeature {
  icon: string;
  title: string;
  detail: string;
}

export interface PlanFaq {
  q: string;
  a: string;
}

export interface PlanData {
  name: string;
  price: number;
  sub: string;
  stripe_url: string;
  color: string;
  badge?: string;
  for: string[];
  features: PlanFeature[];
  faqs: PlanFaq[];
}

export const PLANS: Record<PlanSlug, PlanData> = {
  starter: {
    name: 'Starter',
    price: 249,
    sub: 'Para salones que empiezan a profesionalizarse',
    stripe_url: 'https://buy.stripe.com/starter_placeholder',
    color: '#4ECDC4',
    for: [
      'Salones unipersonales',
      'Peluquerías que reciben muchos mensajes',
      'Dueñas que trabajan solas y no dan abasto',
    ],
    features: [
      {
        icon: '💬',
        title: 'Lara responde WhatsApp o Telegram 24h',
        detail: 'Tu asistente IA responde al instante, a cualquier hora, sin que tú estés.',
      },
      {
        icon: '📅',
        title: 'Agenda de citas integrada',
        detail: 'Las citas van directas a tu Google Calendar. Tú solo apareces y trabajas.',
      },
      {
        icon: '⏰',
        title: 'Recordatorios automáticos',
        detail: 'Lara avisa a la clienta 24h y 1h antes. Los no-shows se reducen hasta un 60%.',
      },
      {
        icon: '📊',
        title: 'Resumen diario al cierre',
        detail: 'Cada día a las 21:00 recibes un resumen de citas por Telegram.',
      },
      {
        icon: '🔢',
        title: 'Hasta 300 conversaciones/mes',
        detail: 'Suficiente para un salón con flujo constante.',
      },
    ],
    faqs: [
      {
        q: '¿Necesito instalar algo?',
        a: 'No. Nosotros lo configuramos todo. Tú solo tienes que escanear un QR con tu móvil la primera vez.',
      },
      {
        q: '¿Qué pasa si WhatsApp bloquea el número?',
        a: 'Por eso recomendamos Telegram como primera opción: es oficial y sin riesgo. Si prefieres WhatsApp, te explicamos el riesgo antes de configurarlo.',
      },
      {
        q: '¿Puedo cancelar cuando quiera?',
        a: 'Sí. Sin permanencia, sin penalizaciones. Y tienes 30 días de garantía.',
      },
    ],
  },
  pro: {
    name: 'Pro',
    price: 449,
    sub: 'Para salones con flujo constante de clientas',
    stripe_url: 'https://buy.stripe.com/pro_placeholder',
    badge: 'Más elegido',
    color: '#4ECDC4',
    for: [
      'Salones con 1-3 empleadas',
      'Peluquerías que reciben llamadas perdidas',
      'Centros que quieren captar clientas nuevas online',
    ],
    features: [
      { icon: '✅', title: 'Todo lo del Starter', detail: '' },
      {
        icon: '📞',
        title: 'Lara responde llamadas perdidas',
        detail: 'Cuando no puedes coger el teléfono, Lara intercepta y le escribe por WhatsApp en segundos. La clienta no llama a otro salón.',
      },
      {
        icon: '🌐',
        title: 'Mini-web con tus servicios y precios',
        detail: 'Una página profesional en nexux.pro/salon/tu-salon con todos tus servicios, horario y botón de reserva.',
      },
      {
        icon: '♾️',
        title: 'Conversaciones ilimitadas',
        detail: 'Sin tope mensual. Cuantas más clientas, mejor.',
      },
      {
        icon: '📈',
        title: 'Reporte mensual de ROI',
        detail: 'El día 1 de cada mes recibes un email con: citas completadas, ingresos estimados, clientas nuevas vs recurrentes, servicio más popular.',
      },
      {
        icon: '📣',
        title: 'Captura de clientas nuevas',
        detail: 'El equipo Nexux gestiona publicidad en redes para traerte clientas nuevas.',
      },
    ],
    faqs: [
      {
        q: '¿Cómo funciona lo de las llamadas perdidas?',
        a: 'Desvías las llamadas no contestadas a un número que te damos. Lara coge, da un mensaje de voz y le escribe por WhatsApp a quien llamó, todo en menos de 3 segundos.',
      },
      {
        q: '¿La mini-web sale en Google?',
        a: 'Sí, está optimizada para SEO local. Tu salón aparece cuando alguien busca peluquería + tu ciudad.',
      },
      {
        q: '¿La publicidad la gestiona una IA?',
        a: 'La estrategia y optimización la hace el equipo Nexux. Tú no tienes que hacer nada.',
      },
    ],
  },
  total: {
    name: 'Total',
    price: 749,
    sub: 'Para cadenas o salones con varios profesionales',
    stripe_url: 'https://buy.stripe.com/total_placeholder',
    badge: 'Premium',
    color: '#4ECDC4',
    for: [
      'Salones con 3+ empleadas',
      'Centros con varias sedes',
      'Dueñas que quieren delegar la captación al completo',
    ],
    features: [
      { icon: '✅', title: 'Todo lo del Pro', detail: '' },
      {
        icon: '👥',
        title: 'Multi-empleada',
        detail: 'Cada profesional tiene su propio calendario. Lara asigna la cita a quien corresponde y cada una ve su agenda.',
      },
      {
        icon: '📝',
        title: 'Blog automático SEO',
        detail: 'Cada mes se publica un artículo optimizado para Google con tu salón y ciudad. Posicionamiento local sin esfuerzo.',
      },
      {
        icon: '🎯',
        title: 'Campañas Meta Ads gestionadas',
        detail: 'El equipo Nexux crea, gestiona y optimiza tus anuncios en Facebook e Instagram.',
      },
      {
        icon: '📊',
        title: 'Analítica completa de clientas',
        detail: 'Dashboard con retención, ticket medio, horas punta, servicios más rentables y evolución mensual.',
      },
      {
        icon: '🤝',
        title: 'Onboarding presencial',
        detail: 'Un especialista de Nexux va a tu salón (Madrid/Barcelona) a configurarlo todo y formar a tu equipo.',
      },
    ],
    faqs: [
      {
        q: '¿Cómo funciona el multi-empleada?',
        a: 'Cada empleada tiene su Google Calendar vinculado. Cuando una clienta reserva, Lara le pregunta si tiene preferencia de profesional y asigna la cita en el calendario correcto.',
      },
      {
        q: '¿El onboarding presencial tiene coste adicional?',
        a: 'No. Está incluido en el plan Total. Solo disponible en Madrid y Barcelona.',
      },
      {
        q: '¿Puedo empezar con Starter y subir a Total?',
        a: 'Sí. El cambio es inmediato y solo pagas la diferencia del mes en curso.',
      },
    ],
  },
};

export const planEntries = Object.entries(PLANS) as [PlanSlug, PlanData][];
