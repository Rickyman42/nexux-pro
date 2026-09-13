// Donde se puede dibujar el mapa de calor, y sobre todo donde NO.
//
// `Layout.astro` lo usan TODAS las paginas del sitio: tambien el panel de
// admin, el portal de cada salon y la pagina donde una clienta reserva su cita.
// Medir donde pulsa la gente ahi seria grabar el trabajo de un cliente dentro
// de su propio CRM, y no sirve absolutamente para nada.
//
// Por eso esto es una lista de PERMITIDAS y no de prohibidas. Si manana alguien
// anade una pagina privada nueva, no se mide sola: hay que traerla aqui a
// proposito. Al reves se olvida siempre, y el dia que se olvida ya se ha
// medido lo que no se debia.
//
// Lo que si se mide es el camino del dinero: llegada -> ficha del plan -> pagar.
export const PAGINAS_MEDIDAS = ['/paquetes', '/comparativa', '/alternativa-a-booksy', '/gracias'];

/**
 * @param {string} ruta  El `location.pathname` de la pagina.
 * @returns {boolean} true solo si es una pagina publica del embudo.
 */
export function esPaginaMedible(ruta) {
  if (typeof ruta !== 'string' || !ruta.startsWith('/')) return false;

  // Quitar la barra final y lo que venga detras de ? o # por si acaso.
  const limpia = ruta.split('?')[0].split('#')[0].replace(/\/+$/, '') || '/';
  if (limpia === '/') return true;

  return PAGINAS_MEDIDAS.some((p) => limpia === p || limpia.startsWith(p + '/'));
}
