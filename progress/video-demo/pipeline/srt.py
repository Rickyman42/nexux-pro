# -*- coding: utf-8 -*-
"""Genera el fichero de subtitulos que se importa en CapCut.

**Todo en UNA pista, con la duda y la respuesta como dos lineas del mismo
rotulo.** La idea original eran dos pistas para poder darle a la duda un gris
mas pequeno que a la respuesta. No se puede: al importar un segundo SRT, CapCut
no lo coloca en sus tiempos absolutos sino **detras** de lo que ya hay en la
linea de tiempo (el montaje pasaba de 55 s a 97 s). Probado y deshecho.

Asi que la jerarquia del acto 4 se pierde --las dos frases salen del mismo
tamano-- pero el contenido del guion esta entero y editable, que es lo que
importa. Si se quiere recuperar la jerarquia hay que partir esos siete rotulos
a mano dentro de CapCut.

  ROTULOS.srt   13 rotulos, 7 de ellos con la duda arriba y la respuesta debajo
  OBJECIONES.srt  se sigue generando por si alguna vez se montan aparte

Los tiempos son absolutos sobre la timeline final y salen de sumar las
duraciones de los planos en orden: no se teclean, se calculan, porque un
segundo mal escrito descuadra todo lo que viene detras.
"""
import pathlib

SALIDA = pathlib.Path(r'C:\Users\Nexux\Desktop\creatives\anuncio-56s')

# Entra 0,3 s despues del corte y sale 0,3 s antes del siguiente plano: si el
# rotulo aparece a la vez que la imagen, el ojo no llega a las dos cosas.
MARGEN = 0.3

# (duracion del plano, objecion, remate)
PLANOS = [
    (2.0, None, 'Son las once y media.'),
    (2.5, None, 'Tienes las manos ocupadas.'),
    (3.0, None, 'El móvil lleva vibrando desde las diez.'),
    (3.0, 'Cuando termines, mirarás.', 'Habrá cuatro mensajes.'),
    (3.5, 'Dos ya no contestarán.', 'Y nunca sabrás quiénes eran.'),
    (2.0, None, 'Mientras tú trabajabas, alguien contestó.'),
    (9.0, None, 'Contestó, ofreció hora y cerró la cita.'),
    (7.0, None, 'Y la puso en tu agenda. Sola.'),
    (3.5, '«¿Y si contesta cualquier cosa?»', 'Pruébala tú. Sin registrarte.'),
    (3.5, '«¿Otro programa que aprender?»', 'Es tu WhatsApp. El de siempre.'),
    (4.0, '«¿Y si no me sirve?»', 'Te devolvemos el dinero. 30 días.'),
    (3.2, '«¿Cuánto?»', '29 € al mes. Sin comisiones por cita.'),
    (4.5, 'Una cosa antes de que sigas:',
     '¿Cuántos mensajes tienes\nahora mismo sin abrir?'),
    (5.0, None, None),          # el cierre lleva su propio texto en la tarjeta
]


def marca(seg):
    """Segundos a hh:mm:ss,mmm."""
    ms = int(round(seg * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return '%02d:%02d:%02d,%03d' % (h, m, s, ms)


def escribe(ruta, entradas):
    trozos = []
    for i, (desde, hasta, texto) in enumerate(entradas, 1):
        trozos.append('%d\n%s --> %s\n%s\n' % (i, marca(desde), marca(hasta), texto))
    ruta.write_text('\n'.join(trozos), encoding='utf-8-sig')
    return len(entradas)


def main():
    rotulos, objeciones = [], []
    t = 0.0
    print('  %-6s %-7s %-7s  %s' % ('plano', 'entra', 'sale', 'texto'))
    print('  ' + '-' * 62)
    for i, (dur, objecion, remate) in enumerate(PLANOS, 1):
        desde, hasta = t + MARGEN, t + dur - MARGEN
        if remate:
            # La duda va como primera linea del mismo rotulo: CapCut no sabe
            # colocar un segundo SRT en sus tiempos, lo encola detras del video.
            texto = (objecion + '\n' + remate) if objecion else remate
            rotulos.append((desde, hasta, texto))
            print('  P%-5d %-7.2f %-7.2f  %s'
                  % (i, desde, hasta, texto.replace('\n', ' / ')))
        if objecion:
            objeciones.append((desde, hasta, objecion))
        t += dur

    n1 = escribe(SALIDA / 'ROTULOS.srt', rotulos)
    n2 = escribe(SALIDA / 'OBJECIONES.srt', objeciones)
    print('\n  ROTULOS.srt     %2d rotulos' % n1)
    print('  OBJECIONES.srt  %2d dudas' % n2)
    print('  timeline total: %.2f s' % t)


if __name__ == '__main__':
    main()
