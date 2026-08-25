#!/usr/bin/env python3
"""Plano 8: el acercamiento sobre la cita, hecho en el fichero.

Por que aqui y no en CapCut: los fotogramas clave de escala se ponen a mano con
el raton, y basta un campo mal seleccionado para que la escala se vaya a 9999%
o para que ctrl+a seleccione todos los clips de la linea de tiempo. Generando el
movimiento aqui, el plano llega a CapCut ya resuelto y Ricardo solo lo mira.

Entra: las dos capturas reales del CRM a 3200x1800 que deja crm-dos-estados.cjs.
Sale: 8 s a 1920x1080 y 24 fps. Arranca viendo el panel entero -- la marca, el
nombre del negocio, la agenda -- y termina encima de la fila de las 18:00, que
es donde entra la cita. Sin ese acercamiento la cita ocupa el 7% del ancho y no
se lee en un movil.

El encuadre final esta medido sobre la captura, no estimado: la zona que cambia
entre las dos capturas sale de comparar los dos PNG (ImageChops.difference).
Si se rehace la toma con otro scroll o otro zoom, hay que volver a medirla.
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops

ANTES = Path('/tmp/crm-antes.png')
DESPUES = Path('/tmp/crm-despues.png')
FRAMES = Path('/tmp/p8mov2')
SALIDA = Path('/tmp/P08-crm-zoom2.mp4')

W, H = 3200, 1800
DESTINO = (1920, 1080)
N = 192          # 8 s a 24 fps
CORTE = 84       # 3,5 s: el fotograma en el que aparece la cita

# Encuadre final, en coordenadas de la captura de 3200x1800.
X0F, X1F, Y0F, Y1F = 880, 2080, 745, 1420


def suave(t):
    """Arranca y frena despacio; un zoom lineal se nota mecanico."""
    return t * t * (3 - 2 * t)


def main():
    antes = Image.open(ANTES).convert('RGB')
    despues = Image.open(DESPUES).convert('RGB')
    if antes.size != (W, H) or despues.size != (W, H):
        sys.exit('las capturas no son de %dx%d: %s / %s' % (W, H, antes.size, despues.size))

    # Donde aparece la cita. Se informa para poder comprobar que el encuadre
    # final la contiene; si no, el plano se monta bonito y sin lo que importa.
    d = ImageChops.difference(antes, despues).convert('L')
    cambio = d.point(lambda v: 255 if v > 18 else 0).getbbox()
    print('la cita aparece en', cambio)
    if not cambio:
        sys.exit('las dos capturas son iguales: la cita no llego a entrar')
    cx0, cy0, cx1, cy1 = cambio
    if not (X0F <= cx0 and cx1 <= X1F and Y0F <= cy0 and cy1 <= Y1F):
        sys.exit('el encuadre final se deja fuera la cita: ajusta X0F..Y1F')

    z1 = W / (X1F - X0F)
    c1 = ((X0F + X1F) / 2.0, (Y0F + Y1F) / 2.0)
    z0, c0 = 1.00, (W / 2.0, H / 2.0)

    FRAMES.mkdir(parents=True, exist_ok=True)
    for i in range(N):
        t = suave(i / (N - 1))
        z = z0 + (z1 - z0) * t
        w, h = W / z, H / z
        cx = min(max(c0[0] + (c1[0] - c0[0]) * t, w / 2), W - w / 2)
        cy = min(max(c0[1] + (c1[1] - c0[1]) * t, h / 2), H - h / 2)
        caja = (round(cx - w / 2), round(cy - h / 2), round(cx + w / 2), round(cy + h / 2))
        src = antes if i < CORTE else despues
        src.crop(caja).resize(DESTINO, Image.LANCZOS).save(FRAMES / ('f%04d.png' % i))
    print('zoom final x%.2f, %d fotogramas' % (z1, N))

    subprocess.run([
        'ffmpeg', '-y', '-loglevel', 'error', '-framerate', '24',
        '-i', str(FRAMES / 'f%04d.png'),
        '-c:v', 'libx264', '-crf', '17', '-preset', 'medium',
        '-pix_fmt', 'yuv420p', '-r', '24', str(SALIDA),
    ], check=True)

    # Contar los fotogramas de verdad, no fiarse de la cabecera: un plano de
    # este pipeline llego a durar 816 s con la duracion declarada correcta.
    n = subprocess.run([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_frames',
        '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', str(SALIDA),
    ], capture_output=True, text=True).stdout.strip()
    print(SALIDA, '->', n, 'fotogramas')
    if n != str(N):
        sys.exit('esperaba %d fotogramas y hay %s' % (N, n))


if __name__ == '__main__':
    main()
