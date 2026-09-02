export type PlanSlug = 'recepcionista' | 'equipo';

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

/** Plan Equipo: agenda propia por persona y fichas de clientes. */
export const EQUIPO_PRICE = 79;

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
  equipo: {
    name: 'Nexux Recepcionista Equipo',
    price: EQUIPO_PRICE,
    sub: 'Todo lo del Recepcionista IA y, además, cada persona de tu equipo abre su calendario y ve lo suyo, no lo de todos. Y tú sabes quién entra por la puerta antes de que salude.',
    stripe_url: '/paquetes/equipo',
    color: '#2A6F97',
    badge: 'Para equipos',
    for: [
      'Atendéis varias personas y cada una necesita ver su agenda, no la de todos',
      'Te preguntan «¿qué tengo yo hoy?» y acabas mirándolo tú',
      'Entra un cliente y nadie recuerda qué se le hizo la última vez',
    ],
    features: [
      {
        title: 'Cada uno abre su agenda y ve la suya',
        detail: 'Enlazas el calendario de Google de cada persona y sus citas van ahí. Ana abre el móvil y ve sus tres citas de la tarde, no las veintitrés del negocio. Tú las sigues viendo todas.',
      },
      {
        title: 'Si mueves una cita, se mueve de verdad',
        detail: 'Cambias una cita de una persona a otra y el aviso desaparece de un calendario y aparece en el otro. No se queda en los dos, que es como se lía una mañana entera.',
      },
      {
        title: 'Sabes quién entra antes de que salude',
        detail: 'Cada cliente tiene su ficha, hecha sola con las citas que ya tienes: cuántas veces ha venido, cuándo fue la última, qué suele pedir y quién suele atenderle.',
      },
      {
        title: 'Lo que no se deduce, lo escribes tú',
        detail: 'Una nota y sus preferencias en cada ficha. «No le gusta el agua caliente». «Siempre con Marta». Lo que hoy está en la cabeza de alguien y se pierde el día que no viene.',
      },
      {
        title: 'Y todo lo del plan de 29 €, igual que antes',
        detail: 'Lara sigue contestando, reservando y recordando. El reparto de citas entre varias personas también sigue incluido: eso no se toca ni se cobra aparte.',
      },
      {
        title: 'Sigue sin haber coste por empleado',
        detail: 'Seáis dos o seáis diez, son 79 € al mes. Sin cuota por persona, sin comisión por cliente y sin permanencia.',
      },
    ],
    faqs: [
      {
        q: '¿Qué me llevo que no tenga ya con los 29 €?',
        a: 'Dos cosas: que cada persona del equipo tenga su propio calendario de Google con sus citas, y las fichas de clientes con su historial, sus notas y sus preferencias. Todo lo demás es idéntico, incluido que Lara reparta las citas entre varias personas sin que se pisen: eso sigue en el plan de 29 €.',
      },
      {
        q: '¿Mi equipo tiene que darse de alta en algo?',
        a: 'No. Conectas tu cuenta de Google una vez y eliges de tu lista qué calendario usa cada persona. Si quieres que lo vean en su móvil, les compartes ese calendario desde Google, como harías con cualquier otro.',
      },
      {
        q: '¿Y si alguien no tiene calendario propio?',
        a: 'Sus citas van al calendario del negocio, igual que hasta ahora. Puedes tener a unos con agenda propia y a otros no.',
      },
      {
        q: '¿Puedo bajar al plan de 29 € si no me compensa?',
        a: 'Sí, cuando quieras y sin dar explicaciones. Tus citas y tus clientes siguen donde están; simplemente dejas de ver las fichas y las citas vuelven todas al calendario del negocio.',
      },
      {
        q: '¿Sirve si no soy peluquería?',
        a: 'Sí. Funciona igual en clínicas dentales, centros de estética, fisioterapia, veterinarios, talleres o asesorías. Si trabajáis con cita previa y atendéis varias personas, encaja.',
      },
      {
        q: '¿Puedo probarlo antes de pagar?',
        a: 'Puedes hablar con Lara ahora mismo en nexux.pro/demo, sin dar ningún dato. Y si te das de alta, tienes 30 días para pedir la devolución si no te convence.',
      },
    ],
  },
};

export const planEntries = Object.entries(PLANS) as [PlanSlug, PlanData][];
