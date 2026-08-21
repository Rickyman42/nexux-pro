export type PlanSlug = 'recepcionista';

export interface PlanFeature {
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
    sub: 'Tu recepcionista IA para WhatsApp, Telegram y web: responde mensajes, consulta tu calendario y deja citas reservadas mientras tú trabajas.',
    stripe_url: '/paquetes/recepcionista',
    color: '#4ECDC4',
    badge: 'Precio de lanzamiento',
    for: [
      'Trabajas con cita previa y no siempre puedes parar para contestar',
      'Ves mensajes demasiado tarde y sabes que algunas citas ya se han ido',
      'Quieres llenar tu agenda sin pagar comisiones por cada nuevo cliente',
    ],
    features: [
      {
        title: 'Contesta mientras tú atiendes',
        detail: 'Lara responde por WhatsApp, Telegram o tu web, también fuera de horario. El cliente recibe respuesta sin esperar a que sueltes las tijeras, cierres la consulta o termines el trabajo.',
      },
      {
        title: 'Convierte la conversación en una cita',
        detail: 'Consulta los huecos libres de tu calendario, propone el que encaja y deja la reserva apuntada. Sin cruces y sin que tengas que intervenir.',
      },
      {
        title: 'Persigue la cita, no al cliente',
        detail: 'Envía recordatorios 24 horas y 1 hora antes para que no tengas que hacerlo tú y el hueco tenga menos posibilidades de quedarse vacío.',
      },
      {
        title: 'Te cuenta el día sin obligarte a mirar el móvil',
        detail: 'Cada tarde recibes un resumen con las citas nuevas, las preguntas recibidas y lo que necesita tu atención.',
      },
      {
        title: '29 € al mes. Tus citas siguen siendo tuyas',
        detail: 'Sin comisión por cliente y sin pagar por cada empleado. Factures una cita o cien, Nexux no se queda un porcentaje.',
      },
      {
        title: 'Empieza sin instalaciones ni llamadas comerciales',
        detail: 'La activas tú y Lara te pregunta lo necesario para conocer tu negocio, tus servicios, tus horarios y tu forma de trabajar.',
      },
    ],
    faqs: [
      {
        q: '¿Cuánto cuesta exactamente?',
        a: '29 euros al mes, todo incluido. No hay alta, configuración aparte, coste por empleado ni comisión por cliente. Es el precio de lanzamiento: si entras a 29 euros, mantienes ese precio mientras sigas de alta.',
      },
      {
        q: '¿Me va a llamar un comercial?',
        a: 'No. La contratas tú cuando quieras y la cancelas igual. Si necesitas ayuda, nos escribes y te responde una persona, pero nadie te llamará para venderte nada.',
      },
      {
        q: '¿Hay permanencia?',
        a: 'No. Cancelas cuando quieras y sin dar explicaciones. El mes que ya has pagado sigue activo hasta el final, y simplemente no se te vuelve a cobrar.',
      },
      {
        q: '¿Tengo que instalar algo?',
        a: 'No. Cuando te das de alta, Lara te pregunta lo que necesita saber sobre tu negocio y te guía durante la configuración.',
      },
      {
        q: '¿Sirve para mi tipo de negocio?',
        a: 'Si trabajas con cita previa, probablemente sí. Encaja con peluquerías, centros de estética, talleres, fisioterapeutas, clínicas, asesorías y veterinarios. Lara aprende tus servicios, precios y horarios.',
      },
      {
        q: '¿Y si me escriben más de la cuenta?',
        a: 'El precio incluye hasta 1.000 conversaciones al mes. Si algún mes te pasas, te avisamos antes de cobrarte cualquier importe adicional.',
      },
      {
        q: '¿Puedo probarlo antes de pagar?',
        a: 'Puedes probar a Lara ahora mismo y sin dar ningún dato en nexux.pro/demo: hablas con ella y ves cómo reserva una cita de ejemplo. Para conectarla a tu negocio se paga desde el primer día, pero tienes 30 días para pedir la devolución si no te convence.',
      },
    ],
  },
};

export const planEntries = Object.entries(PLANS) as [PlanSlug, PlanData][];
