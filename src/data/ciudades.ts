export interface CiudadData {
  name: string;
  slug: string;
  region: string;
  headline: string;
  sub: string;
  stats: { value: string; label: string }[];
  salones: string;
  keywords: string;
}

export const ciudades: CiudadData[] = [
  {
    name: 'Madrid',
    slug: 'madrid',
    region: 'Comunidad de Madrid',
    headline: 'Tu salon en Madrid en piloto automatico',
    sub: 'Mas de 4.000 peluquerias en Madrid compiten por las mismas clientas. Las que responden mas rapido ganan. Lara responde en 4 segundos, a cualquier hora.',
    stats: [
      { value: '+4.200', label: 'Salones en Madrid' },
      { value: '< 4s', label: 'Tiempo de respuesta Lara' },
      { value: '87%', label: 'Conversaciones sin intervencion' },
    ],
    salones: 'mas de 4.000',
    keywords: 'asistente IA peluqueria Madrid, inteligencia artificial salones Madrid, automatizar citas peluqueria Madrid',
  },
  {
    name: 'Barcelona',
    slug: 'barcelona',
    region: 'Cataluna',
    headline: 'Tu peluqueria en Barcelona siempre disponible',
    sub: 'Barcelona tiene mas de 3.500 salones. La diferencia entre llenar la agenda y perder clientas es quien responde primero. Lara no duerme.',
    stats: [
      { value: '+3.500', label: 'Salones en Barcelona' },
      { value: '24h', label: 'Disponibilidad de Lara' },
      { value: '-60%', label: 'Reduccion de no-shows' },
    ],
    salones: 'mas de 3.500',
    keywords: 'asistente IA peluqueria Barcelona, automatizar citas salon Barcelona, Lara IA peluqueria',
  },
  {
    name: 'Valencia',
    slug: 'valencia',
    region: 'Comunitat Valenciana',
    headline: 'Automatiza tu salon en Valencia con IA',
    sub: 'Las peluquerias valencianas que automatizan su atencion captan hasta un 40% mas de citas nuevas. Sin contratar a nadie, sin cambiar como trabajas.',
    stats: [
      { value: '+40%', label: 'Mas citas con automatizacion' },
      { value: '0EUR', label: 'Coste de instalacion' },
      { value: '1 dia', label: 'Para estar operativa' },
    ],
    salones: 'miles de',
    keywords: 'asistente IA peluqueria Valencia, citas automaticas salon Valencia, Lara IA Valencia',
  },
  {
    name: 'Sevilla',
    slug: 'sevilla',
    region: 'Andalucia',
    headline: 'Tu salon en Sevilla nunca pierde una cita',
    sub: 'En Sevilla, el 70% de las clientas que no reciben respuesta en 5 minutos llaman a otro salon. Lara responde en 4 segundos. Siempre.',
    stats: [
      { value: '70%', label: 'Clientas que se van si no respondes' },
      { value: '4s', label: 'Respuesta de Lara' },
      { value: '30 dias', label: 'Garantia de devolucion' },
    ],
    salones: 'miles de',
    keywords: 'asistente IA peluqueria Sevilla, automatizar WhatsApp peluqueria Sevilla, IA salones Sevilla',
  },
  {
    name: 'Bilbao',
    slug: 'bilbao',
    region: 'Pais Vasco',
    headline: 'Llena tu agenda en Bilbao con IA',
    sub: 'Las peluquerias del Pais Vasco con mayor facturacion tienen una cosa en comun: responden a las clientas en segundos. Lara lo hace por ti.',
    stats: [
      { value: 'EUR1,82', label: 'Coste por lead en Meta Ads' },
      { value: '+340', label: 'Conversaciones/mes gestionadas' },
      { value: '24h', label: 'Para activar Lara' },
    ],
    salones: 'cientos de',
    keywords: 'asistente IA peluqueria Bilbao, automatizar citas salon Pais Vasco, Lara IA Bilbao',
  },
  {
    name: 'Zaragoza',
    slug: 'zaragoza',
    region: 'Aragon',
    headline: 'Tu peluqueria en Zaragoza con asistente IA',
    sub: 'Zaragoza es una ciudad donde el boca a boca todavia mueve mucho. Pero las clientas nuevas vienen de WhatsApp e Instagram. Lara gestiona ambos 24h.',
    stats: [
      { value: '24h', label: 'Atencion continua de Lara' },
      { value: '-60%', label: 'Menos no-shows con recordatorios' },
      { value: '249EUR', label: 'Plan Starter desde' },
    ],
    salones: 'cientos de',
    keywords: 'asistente IA peluqueria Zaragoza, citas automaticas salon Zaragoza, Lara IA Aragon',
  },
];

export const ciudadBySlug = Object.fromEntries(ciudades.map(ciudad => [ciudad.slug, ciudad])) as Record<string, CiudadData>;
