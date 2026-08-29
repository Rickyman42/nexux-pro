#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pone los rotulos del guion sobre el montaje con ritmo.

Los textos salen de PLAN-RODAJE.md y no se tocan: el guion es la pieza aprobada.
Aqui solo se decide como se ven y cuando entran.

Tres decisiones, y las tres se midieron antes de tomarlas:

1. **Geist, no DejaVu.** Es la tipografia de nexux.pro (--nx-font-sans). El anuncio
   y la web tienen que hablar con la misma letra; DejaVu es la de sistema y se nota.

2. **Las dos frases van a la vez, no una detras de otra.** Los planos del acto 4
   llevan la objecion del cliente y su respuesta. En secuencia necesitarian el
   doble de tiempo; juntas se leen de un vistazo, porque el ojo salta entre lineas
   en vez de esperar. La jerarquia es el chiste del acto: alguien duda arriba en
   gris, el anuncio contesta debajo en blanco y grande.

3. **Degradado bajo el texto.** Sin el, el blanco desaparece en cuanto el plano
   tiene una pared clara detras, y la mitad de estos planos la tienen.

Cada rotulo entra 0,3 s despues del corte y sale 0,3 s antes del siguiente: si
entra a la vez que el plano, el ojo no llega a las dos cosas.

Se procesa plano a plano y luego se concatena. Con un solo filtro de veinte
superposiciones, cuando algo falla no se sabe donde.

Requiere haber corrido antes montar-ritmo.py (deja los trozos en /tmp/ritmo).
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

TROZOS = Path('/tmp/ritmo')
TRABAJO = Path('/tmp/rotulos')
SALIDA = Path('/tmp/ANUNCIO-con-rotulos.mp4')

# Las de la web: --nx-font-sans: 'Geist'
REGULAR = '/home/nexux/.local/share/fonts/Geist-1.ttf'
NEGRITA = '/home/nexux/.local/share/fonts/Geist-3.ttf'

W, H = 1280, 720
FPS = 24
ENTRADA = 0.3

# (fichero, duracion, objecion o preparacion, remate)
# La primera cadena va arriba en gris y pequena; la segunda abajo en blanco y
# grande. Si la primera es None, solo hay remate.
PLANOS = [
    ('P01-manos-manicura',       2.0, None,
     'Son las once y media.'),
    ('P02-movil-mostrador',      2.5, None,
     'Tienes las manos ocupadas.'),
    ('P03-cabina-mensajes',      3.0, None,
     'El móvil lleva vibrando desde las diez.'),
    ('P04-pantalla-se-apaga',    3.0, 'Cuando termines, mirarás.',
     'Habrá cuatro mensajes.'),
    ('P05-lena-final-del-dia',   3.5, 'Dos ya no contestarán.',
     'Y nunca sabrás quiénes eran.'),
    ('P06-mano-movil-apagado',   2.0, None,
     'Mientras tú trabajabas, alguien contestó.'),
    ('P07-en-movil',             9.0, None,
     'Contestó, ofreció hora y cerró la cita.'),
    ('P08-agenda-y-roi',         7.0, None,
     'Y la puso en tu agenda. Sola.'),
    ('P09-probando-el-movil',    3.5, '«¿Y si contesta cualquier cosa?»',
     'Pruébala tú. Sin registrarte.'),
    ('P10-pulgar-whatsapp',      3.5, '«¿Otro programa que aprender?»',
     'Es tu WhatsApp. El de siempre.'),
    ('P11-lena-mostrador',       4.0, '«¿Y si no me sirve?»',
     'Te devolvemos el dinero. 30 días.'),
    ('P12-negocio-con-clientes', 3.2, '«¿Cuánto?»',
     '29 € al mes. Sin comisiones por cita.'),
    ('P13-lena-mirando-movil',   4.5, 'Una cosa antes de que sigas:',
     '¿Cuántos mensajes tienes ahora mismo sin abrir?'),
    ('P14-cierre-qr',            5.0, None, None),   # la tarjeta ya lleva su texto
]


def _reparte(palabras, fuente, ancho_max):
    """Mete las palabras en lineas de ancho_max. Devuelve None si alguna no cabe."""
    d = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    lineas, actual = [], ''
    for p in palabras:
        prueba = (actual + ' ' + p).strip()
        if d.textlength(prueba, font=fuente) <= ancho_max:
            actual = prueba
        elif actual:
            lineas.append(actual)
            if d.textlength(p, font=fuente) > ancho_max:
                return None
            actual = p
        else:
            return None
    if actual:
        lineas.append(actual)
    return lineas


def parte(texto, fuente, ancho_max):
    """Parte el texto en lineas equilibradas, no en lineas llenas.

    El reparto avaro deja viudas: "...tienes ahora mismo sin" / "abrir?" con una
    sola palabra colgando en la ultima linea. Se busca el numero minimo de lineas
    y luego se va estrechando el ancho mientras siga cabiendo en esas mismas
    lineas; el resultado son lineas de largo parecido. Es lo que hace
    text-wrap: balance en CSS, y aqui hace falta igual.
    """
    palabras = texto.split()
    base = _reparte(palabras, fuente, ancho_max)
    if base is None or len(base) < 2:
        return base or [texto]

    mejor = base
    ancho = ancho_max
    while ancho > 200:
        ancho -= 20
        prueba = _reparte(palabras, fuente, ancho)
        if prueba is None or len(prueba) > len(base):
            break
        mejor = prueba
    return mejor


def dibuja(objecion, remate):
    """Un PNG transparente con el rotulo entero y su degradado."""
    cap = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    f_remate = ImageFont.truetype(NEGRITA, 46)
    f_objecion = ImageFont.truetype(REGULAR, 32)

    # Se compone anclando por abajo: el bloque entero termina a 92 px del borde,
    # asi el remate no baila segun cuantas lineas tenga la objecion de encima.
    bloques = []
    if objecion:
        bloques.append((parte(objecion, f_objecion, W - 190), f_objecion,
                        (196, 196, 196, 255), 10))
    if remate:
        bloques.append((parte(remate, f_remate, W - 190), f_remate,
                        (255, 255, 255, 255), 14))

    alto = sum(len(l) * (f.size + s) for l, f, _, s in bloques)
    if len(bloques) == 2:
        alto += 10                      # aire entre la duda y la respuesta
    y = H - 92 - alto

    # El degradado arranca 60 px por encima del texto, no a una altura fija. Con
    # el tercio inferior fijo, en el plano del CRM el velo caia sobre el panel de
    # ROI --que es la carta de venta del producto-- para tapar un rotulo de una
    # sola linea que estaba mucho mas abajo. Ahora oscurece lo justo.
    arranque = max(y - 60, 0)
    grad = Image.new('L', (1, H), 0)
    for py in range(H):
        t = (py - arranque) / max(H - arranque, 1)
        grad.putpixel((0, py), 0 if t < 0 else int(180 * min(t, 1.0) ** 1.4))
    velo = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    velo.putalpha(grad.resize((W, H)))
    cap = Image.alpha_composite(cap, velo)

    d = ImageDraw.Draw(cap)

    for i, (lineas, fuente, color, sep) in enumerate(bloques):
        for linea in lineas:
            x = (W - d.textlength(linea, font=fuente)) / 2
            # Sombra corta: el degradado solo no salva un fondo muy claro
            d.text((x + 2, y + 2), linea, font=fuente, fill=(0, 0, 0, 160))
            d.text((x, y), linea, font=fuente, fill=color)
            y += fuente.size + sep
        if i == 0 and len(bloques) == 2:
            y += 10
    return cap


def medida(video, dur):
    """Brillo medio de la franja donde va el rotulo, a mitad del plano.

    Se mira el quinto inferior, que es donde cae el texto en todos los planos
    (el bloque siempre termina a 92 px del borde). Comparando ese numero antes y
    despues de superponer se sabe si el rotulo entro de verdad, cosa que contar
    fotogramas no dice.
    """
    r = subprocess.run(
        ['ffmpeg', '-v', 'error', '-ss', str(dur / 2), '-i', str(video),
         '-frames:v', '1',
         '-vf', 'crop=iw:ih/5:0:ih*4/5,signalstats,metadata=print:file=-',
         '-f', 'null', '-'],
        capture_output=True, text=True)
    for linea in r.stdout.splitlines():
        if 'YAVG' in linea:
            return float(linea.split('=')[-1])
    sys.exit('no se pudo medir el brillo de %s' % video)


def pico(video, dur):
    """Brillo del pixel mas claro de la franja del rotulo, a mitad del plano.

    Es lo que delata al texto: un rotulo blanco mete pixeles a ~250 donde antes
    no los habia. El brillo MEDIO no vale para todos los planos --en la silla
    vacia, casi negra, el degradado no puede oscurecer y el texto ocupa tan poca
    superficie que la media apenas se mueve un punto-- y por eso daba por
    fallido un plano perfectamente rotulado.
    """
    r = subprocess.run(
        ['ffmpeg', '-v', 'error', '-ss', str(dur / 2), '-i', str(video),
         '-frames:v', '1',
         '-vf', 'crop=iw:ih/5:0:ih*4/5,signalstats,metadata=print:file=-',
         '-f', 'null', '-'],
        capture_output=True, text=True)
    for linea in r.stdout.splitlines():
        if 'YMAX' in linea:
            return float(linea.split('=')[-1])
    sys.exit('no se pudo medir el pico de %s' % video)


def main():
    if not TROZOS.exists():
        sys.exit('faltan los trozos: corre antes montar-ritmo.py')
    TRABAJO.mkdir(parents=True, exist_ok=True)
    piezas, total = [], 0.0

    for fichero, dur, objecion, remate in PLANOS:
        entrada = TROZOS / (fichero + '.mp4')
        if not entrada.exists():
            sys.exit('falta %s (corre montar-ritmo.py)' % entrada)
        salida = TRABAJO / (fichero + '.mp4')

        if not remate:
            subprocess.run(['cp', str(entrada), str(salida)], check=True)
            print('  %-28s %4.1fs  sin rotulo' % (fichero, dur))
            piezas.append(salida)
            total += dur
            continue

        png = TRABAJO / (fichero + '.png')
        dibuja(objecion, remate).save(png)

        sale = dur - ENTRADA
        filtro = (
            "[1:v]format=rgba,fade=t=in:st=%.2f:d=%.2f:alpha=1,"
            "fade=t=out:st=%.2f:d=%.2f:alpha=1[r];[0:v][r]overlay=0:0"
            % (ENTRADA, ENTRADA, sale - ENTRADA, ENTRADA))

        # El PNG entra en bucle y con duracion propia. Sin -loop 1 es un unico
        # fotograma que existe solo en t=0: el fundido de entrada arranca en 0,3 s,
        # ese fotograma se queda con transparencia total y ffmpeg lo repite invisible
        # el resto del plano. El video dura lo que debe y no lleva nada encima, asi
        # que contar fotogramas NO lo detecta. Por eso abajo se mide el brillo.
        subprocess.run(
            ['ffmpeg', '-y', '-loglevel', 'error', '-i', str(entrada),
             '-loop', '1', '-framerate', str(FPS), '-t', str(dur), '-i', str(png),
             '-filter_complex', filtro,
             '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
             '-pix_fmt', 'yuv420p', '-r', str(FPS), '-an', str(salida)], check=True)

        leidos = int(subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_frames',
             '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', str(salida)],
            capture_output=True, text=True).stdout.strip())
        esperados = int(dur * FPS)
        if abs(leidos - esperados) > 2:
            sys.exit('%s tiene %d fotogramas y esperaba %d' % (fichero, leidos, esperados))

        # Prueba de que el rotulo ESTA: la franja baja tiene que oscurecerse. Se
        # compara el brillo medio de esa franja antes y despues de superponer; el
        # degradado la baja siempre, asi que si no cae es que no se pinto nada.
        # Vale cualquiera de las dos senales: que el degradado haya oscurecido
        # la franja, o que el texto haya metido pixeles claros donde no los
        # habia. Sobre fondo claro manda la primera; sobre fondo oscuro, la
        # segunda. Exigir solo una fallaba en la mitad de los planos.
        oscurece = medida(salida, dur) < medida(entrada, dur) - 4
        aclara = pico(salida, dur) > pico(entrada, dur) + 20
        if not (oscurece or aclara):
            sys.exit('%s: la franja no cambio, el rotulo no se pinto' % fichero)

        cuantos = 2 if objecion else 1
        print('  %-28s %4.1fs  %d linea(s)  %3d fot.' % (fichero, dur, cuantos, leidos))
        piezas.append(salida)
        total += dur

    lista = TRABAJO / 'lista.txt'
    lista.write_text(''.join("file '%s'\n" % p for p in piezas), encoding='utf-8')
    subprocess.run(
        ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0',
         '-i', str(lista), '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
         '-pix_fmt', 'yuv420p', '-r', str(FPS), '-an', str(SALIDA)], check=True)

    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                              '-of', 'csv=p=0', str(SALIDA)],
                             capture_output=True, text=True).stdout)
    n = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_frames',
                        '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', str(SALIDA)],
                       capture_output=True, text=True).stdout.strip()
    print('\n  planificado: %.1f s' % total)
    print('  %s -> %.2f s, %s fotogramas' % (SALIDA, d, n))


if __name__ == '__main__':
    main()
