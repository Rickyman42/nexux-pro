export type PlanSlug = 'recepcionista';

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

/** Precio de lanzamiento. Congelado de por vida para los primeros LAUNCH_SEATS clientes. */
export const LAUNCH_PRICE = 29;
export const REGULAR_PRICE = 35;
export const LAUNCH_SEATS = 50;

export const PLANS: Record<PlanSlug, PlanData> = {
  recepcionista: {
    name: 'Nexux Recepcionista IA',
    price: LAUNCH_PRICE,
    sub: 'Un precio. Todo incluido. Sin permanencia.',
    stripe_url: '/paquetes/recepcionista',
    color: '#4ECDC4',
    badge: 'Precio de lanzamiento',
    for: [
      'Negocios que trabajan con cita previa',
      'Quien pierde clientes por no llegar a contestar',
      'Quien no quiere pagar comisiones por cada cliente nuevo',
    ],
    features: [
      {
        icon: '💬',
        title: 'Contesta por WhatsApp, Telegram o tu web',
        detail: 'Responde al momento a cualquier hora, tambien de madrugada y en festivos. Tu eliges por donde te escriben tus clientes.',
      },
      {
        icon: '📅',
        title: 'Reserva la cita el solo',
        detail: 'Mira los huecos libres de tu calendario, propone el que encaja y apunta la cita. Sin solaparse y sin que tu toques nada.',
      },
      {
        icon: '⏰',
        title: 'Recuerda la cita por ti',
        detail: 'Avisa al cliente 24 horas y 1 hora antes. Las ausencias bajan y el hueco no se pierde.',
      },
      {
        icon: '📊',
        title: 'Te cuenta el dia al cerrar',
        detail: 'Cada tarde recibes un resumen de lo que ha pasado: citas nuevas, preguntas y lo que necesita tu atencion.',
      },
      {
        icon: '🚫',
        title: 'Sin comisiones y sin pagar por empleado',
        detail: 'Lo que factures es tuyo entero. Da igual si sois uno o sois seis: el precio no se mueve.',
      },
      {
        icon: '⚡',
        title: 'Listo en cinco minutos',
        detail: 'No instalas nada ni te llama ningun comercial. Lo activas tu y el propio asistente se configura hablando contigo.',
      },
    ],
    faqs: [
      {
        q: 'Cuanto cuesta exactamente?',
        a: 'Veintinueve euros al mes, todo incluido. No hay alta, ni configuracion aparte, ni coste por empleado, ni comision por cliente. Es el precio de lanzamiento: subira a 35 euros, pero si entras ahora te quedas en 29 mientras sigas de alta.',
      },
      {
        q: 'Me va a llamar un comercial?',
        a: 'No. Lo contratas tu cuando quieras y lo cancelas igual. Si necesitas ayuda nos escribes y te responde una persona, pero nadie te va a llamar para venderte nada.',
      },
      {
        q: 'Hay permanencia?',
        a: 'No. Cancelas cuando quieras desde tu panel, sin penalizacion y sin dar explicaciones.',
      },
      {
        q: 'Tengo que instalar algo?',
        a: 'No. Se configura solo: en cuanto te das de alta, el asistente te escribe y te pregunta lo que necesita saber de tu negocio. En cinco minutos esta funcionando.',
      },
      {
        q: 'Sirve para mi tipo de negocio?',
        a: 'Si trabajas con cita previa, si. Lo usan peluquerias, centros de estetica, talleres, fisioterapeutas, clinicas, asesorias y veterinarios. El asistente aprende tus servicios, tus precios y tu horario.',
      },
      {
        q: 'Y si me escriben mas de la cuenta?',
        a: 'El precio incluye hasta 1.000 conversaciones al mes, que es mucho mas de lo que gasta un negocio normal. Si algun mes te pasas, te avisamos antes de cobrarte nada de mas.',
      },
      {
        q: 'Puedo probarlo antes de pagar?',
        a: 'Si. El primer mes es gratis y no pedimos tarjeta para empezar.',
      },
    ],
  },
};

export const planEntries = Object.entries(PLANS) as [PlanSlug, PlanData][];
