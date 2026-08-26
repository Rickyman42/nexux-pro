#!/usr/bin/env python3
"""Plano 8 ensanchado: la agenda y el ROI del bot.

Ricardo pidio que el anuncio ensene el CRM y lo que tiene, no una sola pantalla.
La intencion era ensenar tres. Se comprobaron las siete secciones y solo dos
sirven hoy:

  - Citas     -> la cita entrando sola en la agenda
  - Dashboard -> ROI del bot: ~633 EUR generados y 95 min ahorrados

Clientes y Chats **estan vacios** en la demo, aun despues de que el bot reserve
una cita. Meter una pantalla vacia en un anuncio es peor que no ensenarla, asi
que el plano se queda en dos. Queda anotado como fallo de producto a mirar.

De las dos, la que vende es la segunda: decirle a una duena de salon cuanto
dinero le ha traido el bot pesa mas que ver una casilla aparecer.

Entra: las tres capturas reales del panel a 3200x1800.
Sale:  11,5 s a 1920x1080 y 24 fps.

  p8-agenda-y-roi.py            genera el plano
  p8-agenda-y-roi.py --revisar  saca solo el primer y ultimo fotograma de cada tramo
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image

ANTES = Path('/tmp/p8-agenda-antes.png')
DESPUES = Path('/tmp/p8-agenda-despues.png')
DASHBOARD = Path('/tmp/p8-dashboard.png')
FRAMES = Path('/tmp/p8ancho')
SALIDA = Path('/tmp/P08-agenda-y-roi.mp4')

W, H = 3200, 1800
DESTINO = (1920, 1080)
FPS = 24

# --- Tramo 1: la agenda -----------------------------------------------------
# Encuadre final medido sobre la captura: entra la columna de horas, la del
# jueves con la cita de las 18:00 y el borde del panel, sin banda gris.
AGENDA_FIN = (880, 2080, 745, 1420)
AGENDA_SEG = 6.0        # dura el tramo
AGENDA_CORTE = 3.5      # aqui aparece la cita

# --- Tramo 2: el ROI --------------------------------------------------------
# La tarjeta "ROI del bot" ocupa x 1776-2680, y 1266-1491. Se encuadra con algo
# de aire para que se lean las dos cifras y el titulo.
ROI_FIN = (1722, 2734, 1094, 1663)
ROI_SEG = 5.5


def suave(t):
    return t * t * (3 - 2 * t)


def encuadre(t, caja_fin):
    """Del panel entero al encuadre final, con arranque y frenada suaves."""
    x0f, x1f, y0f, y1f = caja_fin
    z1 = W / (x1f - x0f)
    c1 = ((x0f + x1f) / 2.0, (y0f + y1f) / 2.0)
    k = suave(t)
    z = 1.0 + (z1 - 1.0) * k
    cx = W / 2.0 + (c1[0] - W / 2.0) * k
    cy = H / 2.0 + (c1[1] - H / 2.0) * k
    w, h = W / z, H / z
    cx = min(max(cx, w / 2), W - w / 2)
    cy = min(max(cy, h / 2), H - h / 2)
    return (round(cx - w / 2), round(cy - h / 2), round(cx + w / 2), round(cy + h / 2))


def main():
    antes = Image.open(ANTES).convert('RGB')
    despues = Image.open(DESPUES).convert('RGB')
    tablero = Image.open(DASHBOARD).convert('RGB')
    for nombre, im in (('antes', antes), ('despues', despues), ('dashboard', tablero)):
        if im.size != (W, H):
            sys.exit('%s no es de %dx%d sino %s' % (nombre, W, H, im.size))

    n_agenda = int(AGENDA_SEG * FPS)
    n_roi = int(ROI_SEG * FPS)
    corte = int(AGENDA_CORTE * FPS)

    if '--revisar' in sys.argv:
        muestras = {
            'agenda-inicio': (antes, encuadre(0.0, AGENDA_FIN)),
            'agenda-cita': (despues, encuadre(corte / (n_agenda - 1), AGENDA_FIN)),
            'agenda-final': (despues, encuadre(1.0, AGENDA_FIN)),
            'roi-inicio': (tablero, encuadre(0.0, ROI_FIN)),
            'roi-final': (tablero, encuadre(1.0, ROI_FIN)),
        }
        for nombre, (src, caja) in muestras.items():
            src.crop(caja).resize(DESTINO, Image.LANCZOS).save('/tmp/p8rev-%s.png' % nombre)
            print('  /tmp/p8rev-%s.png  %s' % (nombre, caja))
        return

    FRAMES.mkdir(parents=True, exist_ok=True)
    i = 0
    for k in range(n_agenda):
        src = antes if k < corte else despues
        caja = encuadre(k / (n_agenda - 1), AGENDA_FIN)
        src.crop(caja).resize(DESTINO, Image.LANCZOS).save(FRAMES / ('f%04d.png' % i))
        i += 1
    for k in range(n_roi):
        caja = encuadre(k / (n_roi - 1), ROI_FIN)
        tablero.crop(caja).resize(DESTINO, Image.LANCZOS).save(FRAMES / ('f%04d.png' % i))
        i += 1
    print('generados %d fotogramas (%d agenda + %d roi)' % (i, n_agenda, n_roi))

    subprocess.run([
        'ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS),
        '-i', str(FRAMES / 'f%04d.png'),
        '-c:v', 'libx264', '-crf', '17', '-preset', 'medium',
        '-pix_fmt', 'yuv420p', '-r', str(FPS), str(SALIDA),
    ], check=True)

    # Contar los fotogramas de verdad: un plano de este pipeline llego a durar
    # 816 s con la duracion declarada correcta en la cabecera.
    leidos = subprocess.run([
        'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_frames',
        '-show_entries', 'stream=nb_read_frames', '-of', 'csv=p=0', str(SALIDA),
    ], capture_output=True, text=True).stdout.strip()
    print(SALIDA, '->', leidos, 'fotogramas')
    if leidos != str(i):
        sys.exit('esperaba %d fotogramas y hay %s' % (i, leidos))


if __name__ == '__main__':
    main()
