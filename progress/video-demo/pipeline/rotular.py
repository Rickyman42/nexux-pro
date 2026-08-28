#!/usr/bin/env python3
"""Pone los rotulos del guion sobre los planos ya recortados.

Los textos salen de PLAN-RODAJE.md 2 y no se tocan: el guion es la pieza
aprobada. Aqui solo se decide cuando entra cada uno y como se ve.

Como esta pensado:

- Los rotulos van en la franja baja, sobre un degradado oscuro. Sin el, el texto
  blanco desaparece en cuanto el plano tiene una pared clara detras, y la mitad
  de estos planos la tienen.
- Los planos del acto 4 llevan dos lineas: la objecion del cliente arriba, mas
  pequena y en gris, y la respuesta debajo en blanco y grande. Esa jerarquia es
  el chiste del acto: alguien duda, el anuncio contesta.
- Cada rotulo entra 0,4 s despues del corte y sale 0,4 s antes del siguiente. Si
  entra a la vez que el plano, el ojo no llega a las dos cosas.

Se procesa plano a plano y luego se concatena: con un solo filtro de veinte
superposiciones, cuando algo falla no se sabe donde.
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

CORTES = Path('/home/nexux/brand-assets/video/anuncio-75s/cortes')
TRABAJO = Path('/tmp/rotulos')
SALIDA = Path('/tmp/ANUNCIO-75s.mp4')

REGULAR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
NEGRITA = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

W, H = 1280, 720
ENTRADA = 0.4   # lo que tarda en aparecer, y lo que se adelanta a desaparecer

# (fichero, duracion, [(texto, es_remate, desde, hasta), ...])
# es_remate: la frase que cierra, en blanco y grande. Lo demas es la preparacion.
PLANOS = [
    ('01_P01-manos', 4, [('Son las once y media.', True, 0.4, 3.6)]),
    ('02_P02-movil-mostrador', 5, [('Tienes las manos ocupadas.', True, 0.4, 4.6)]),
    ('03_P03-cabina', 5, [('El móvil lleva vibrando desde las diez.', True, 0.4, 4.6)]),
    ('04_P04-pantalla-se-apaga', 5, [
        ('Cuando termines, mirarás.', False, 0.4, 2.4),
        ('Habrá cuatro mensajes.', True, 2.6, 4.6)]),
    ('05_P05-lena-final-del-dia', 5, [
        ('Dos ya no contestarán.', False, 0.4, 2.4),
        ('Y nunca sabrás quiénes eran.', True, 2.6, 4.8)]),
    ('06_P06-movil-apagado', 4, [('Mientras tú trabajabas, alguien contestó.', True, 0.4, 3.6)]),
    ('07_P07-conversacion', 10, [('Contestó, ofreció hora y cerró la cita.', True, 0.5, 4.5)]),
    ('08_P08-agenda-y-roi', 8, [('Y la puso en tu agenda. Sola.', True, 0.6, 5.0)]),
    ('09_P09-probando', 4, [
        ('«¿Y si contesta cualquier cosa?»', False, 0.3, 3.7),
        ('Pruébala tú. Sin registrarte.', True, 1.5, 3.7)]),
    ('10_P10-pulgar', 5, [
        ('«¿Otro programa que aprender?»', False, 0.3, 4.7),
        ('Es tu WhatsApp. El de siempre.', True, 1.6, 4.7)]),
    ('11_P11-lena-mostrador', 4, [
        ('«¿Y si no me sirve?»', False, 0.3, 3.7),
        ('Te devolvemos el dinero. 30 días.', True, 1.4, 3.7)]),
    ('12_P12-negocio-con-vida', 5, [
        ('«¿Cuánto?»', False, 0.3, 4.7),
        ('29 € al mes. Sin comisiones por cita.', True, 1.4, 4.7)]),
    ('13_P13-lena-movil', 6, [
        ('Una cosa antes de que sigas:', False, 0.5, 5.5),
        ('¿Cuántos mensajes tienes ahora mismo sin abrir?', True, 2.0, 5.7)]),
    ('14_P14-cierre', 5, []),   # la tarjeta ya lleva su texto
]


def parte(texto, fuente, ancho_max):
    """Parte el texto en lineas que quepan."""
    palabras = texto.split()
    lineas, actual = [], ''
    tmp = Image.new('RGB', (10, 10))
    d = ImageDraw.Draw(tmp)
    for p in palabras:
        prueba = (actual + ' ' + p).strip()
        if d.textlength(prueba, font=fuente) <= ancho_max:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = p
    if actual:
        lineas.append(actual)
    return lineas


def dibuja(texto, remate, con_pregunta):
    """Un PNG transparente con el rotulo y su degradado."""
    cap = Image.new('RGBA', (W, H), (0, 0, 0, 0))

    # Degradado: negro por abajo, transparente hacia arriba. Empieza en el 62%
    # de la altura, que deja respirar la imagen y cubre las dos lineas.
    grad = Image.new('L', (1, H), 0)
    for y in range(H):
        t = (y - H * 0.62) / (H * 0.38)
        grad.putpixel((0, y), 0 if t < 0 else int(170 * min(t, 1.0) ** 1.4))
    velo = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    velo.putalpha(grad.resize((W, H)))
    cap = Image.alpha_composite(cap, velo)

    d = ImageDraw.Draw(cap)
    if remate:
        fuente = ImageFont.truetype(NEGRITA, 44)
        color = (255, 255, 255, 255)
        base_y = H - 96 if con_pregunta else H - 118
    else:
        fuente = ImageFont.truetype(REGULAR, 33)
        color = (214, 214, 214, 255)
        base_y = H - 168 if con_pregunta else H - 118

    lineas = parte(texto, fuente, W - 200)
    alto_linea = fuente.size + 12
    y = base_y - (len(lineas) - 1) * alto_linea
    for linea in lineas:
        an = d.textlength(linea, font=fuente)
        x = (W - an) / 2
        # Una sombra corta debajo: el degradado solo no salva un fondo muy claro
        d.text((x + 2, y + 2), linea, font=fuente, fill=(0, 0, 0, 150))
        d.text((x, y), linea, font=fuente, fill=color)
        y += alto_linea
    return cap


def main():
    TRABAJO.mkdir(parents=True, exist_ok=True)
    trozos = []

    for fichero, dur, rotulos in PLANOS:
        entrada = CORTES / (fichero + '.mp4')
        if not entrada.exists():
            sys.exit('falta %s' % entrada)
        salida = TRABAJO / (fichero + '.mp4')

        if not rotulos:
            subprocess.run(['cp', str(entrada), str(salida)], check=True)
            print('  %-28s sin rotulo' % fichero)
            trozos.append(salida)
            continue

        con_pregunta = len(rotulos) > 1 and not rotulos[0][1]
        entradas = ['-i', str(entrada)]
        for i, (texto, remate, desde, hasta) in enumerate(rotulos):
            png = TRABAJO / ('%s-%d.png' % (fichero, i))
            dibuja(texto, remate, con_pregunta).save(png)
            entradas += ['-i', str(png)]

        # Cada rotulo se funde a la entrada y a la salida, y solo existe en su tramo
        cadena, previo = [], '[0:v]'
        for i, (texto, remate, desde, hasta) in enumerate(rotulos):
            cadena.append(
                "[%d:v]format=rgba,fade=t=in:st=%.2f:d=%.2f:alpha=1,"
                "fade=t=out:st=%.2f:d=%.2f:alpha=1[r%d];"
                % (i + 1, desde, ENTRADA, hasta - ENTRADA, ENTRADA, i))
            etiqueta = '[v%d]' % i
            cadena.append("%s[r%d]overlay=0:0:enable='between(t,%.2f,%.2f)'%s;"
                          % (previo, i, desde, hasta, etiqueta))
            previo = etiqueta
        filtro = ''.join(cadena).rstrip(';')

        subprocess.run(
            ['ffmpeg', '-y', '-loglevel', 'error'] + entradas +
            ['-filter_complex', filtro, '-map', previo,
             '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
             '-pix_fmt', 'yuv420p', '-r', '24', '-an', str(salida)],
            check=True)
        print('  %-28s %d rotulo(s)' % (fichero, len(rotulos)))
        trozos.append(salida)

    lista = TRABAJO / 'lista.txt'
    lista.write_text(''.join("file '%s'\n" % t for t in trozos), encoding='utf-8')
    subprocess.run(
        ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0',
         '-i', str(lista), '-c:v', 'libx264', '-crf', '18', '-preset', 'medium',
         '-pix_fmt', 'yuv420p', '-r', '24', '-an', str(SALIDA)], check=True)

    n = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                        '-count_frames', '-show_entries', 'stream=nb_read_frames',
                        '-of', 'csv=p=0', str(SALIDA)],
                       capture_output=True, text=True).stdout.strip()
    d = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                        '-of', 'csv=p=0', str(SALIDA)],
                       capture_output=True, text=True).stdout.strip()
    print('\n%s -> %s fotogramas, %.2f s' % (SALIDA, n, float(d)))


if __name__ == '__main__':
    main()
