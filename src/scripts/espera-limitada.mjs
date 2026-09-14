// Esperar a algo, pero no para siempre.
//
// Vive en su propio fichero y no dentro de checkout.ts por un motivo: asi los
// tests pueden EJECUTARLO, en vez de leer el codigo y dar por hecho que hace lo
// que dice. Mismo criterio que paginas-medidas.mjs.
//
// Por que existe: hasta el 14-sep-2026, abrir la pantalla de pago era
// `await stripe.initEmbeddedCheckout(...)` sin limite. Si Stripe tardaba o se
// atascaba, la persona se quedaba mirando la ruedecita para siempre: sin error,
// sin aviso, y sin que nosotros lo supieramos. En las ultimas 100 pantallas de
// pago abiertas hubo 2 ventas, y las dos eran nuestras.

/**
 * Espera a `promesa` como mucho `ms` milisegundos.
 *
 * Si tarda mas, deja de esperarla y falla con `tardo_demasiado`. Lo importante:
 * una promesa NO se puede cancelar, asi que la original sigue viva y puede
 * llegar despues. Cuando eso pasa se le entrega a `alLlegarTarde` para que la
 * cierre; si no, quedaria una pantalla de pago fantasma consumiendo memoria y,
 * peor, montandose sola en una ventana que el visitante ya habia cerrado.
 *
 * @param {Promise<any>} promesa   lo que se espera
 * @param {number} ms              cuanto se espera como maximo
 * @param {(valor:any)=>void} alLlegarTarde  que hacer con lo que llega tarde
 * @param {{programa?:Function, cancela?:Function}} [reloj]  para poder probarlo sin esperar de verdad
 */
export function conLimite(promesa, ms, alLlegarTarde, reloj = {}) {
  const programa = reloj.programa || setTimeout;
  const cancela = reloj.cancela || clearTimeout;

  return new Promise((resolver, rechazar) => {
    let seDioPorPerdida = false;
    const aviso = programa(() => {
      seDioPorPerdida = true;
      rechazar(new Error('tardo_demasiado'));
    }, ms);

    Promise.resolve(promesa).then(
      (valor) => {
        cancela(aviso);
        if (seDioPorPerdida) alLlegarTarde(valor);
        else resolver(valor);
      },
      (error) => {
        cancela(aviso);
        // Si ya se habia dado por perdida, el fallo llega tarde y no interesa:
        // el visitante ya tiene su mensaje de error delante.
        if (!seDioPorPerdida) rechazar(error);
      },
    );
  });
}
