#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera la voz en off del anuncio y la monta en una pista de 55,71 s.

Cada linea se sintetiza por separado y se coloca en el segundo exacto en que
entra su rotulo, con silencio entre medias. Asi la pista se arrastra a CapCut
al segundo cero y ya esta sincronizada: no hay que cuadrar nada a mano.

Los tiempos salen de los mismos que usa srt.py para los rotulos, no se teclean
aparte: si el montaje cambia, se cambian en un sitio.

Los numeros van escritos con letra --"veintinueve euros", "treinta dias"-- porque
el sintetizador lee "29 €" como "veintinueve" a secas o se inventa la moneda.

  voz.py            genera todo
  voz.py --solo N   regenera solo la linea N (para retocar una que no convence)
"""
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

SALIDA = Path('/tmp/voz')
PISTA = SALIDA / 'VOZ-anuncio-56s.wav'
DURACION = 55.71
FPS_AUDIO = 44100

# (segundo en que entra el rotulo, texto que se locuta)
# El segundo es el mismo que el del rotulo: la voz entra con el texto en pantalla.
LINEAS = [
    (0.30,  'Son las once y media.'),
    (2.30,  'Tienes las manos ocupadas.'),
    (4.80,  'El móvil lleva vibrando desde las diez.'),
    (7.80,  'Habrá cuatro mensajes.'),
    (10.80, 'Y nunca sabrás quiénes eran.'),
    (14.30, 'Alguien contestó por ti.'),
    (16.30, 'Contestó, ofreció hora y cerró la cita.'),
    (25.30, 'Y la puso en tu agenda. Sola.'),
    (32.30, '¿Y si contesta cualquier cosa? Pruébala tú, sin registrarte.'),
    (35.80, 'Es tu WhatsApp. El de siempre.'),
    (39.30, 'Te devolvemos el dinero. Treinta días.'),
    (43.30, 'Veintinueve euros al mes.'),
    (46.50, 'Una cosa antes de que sigas: ¿cuántos mensajes tienes ahora mismo sin abrir?'),
]

RESPIRO = 0.20      # silencio minimo entre una linea y la siguiente
TOPE_RITMO = 1.15   # por encima de esto la locucion ya se oye acelerada
ADELANTO_MAX = 0.45  # lo mas que se permite que la voz se adelante a su rotulo

# La voz del anuncio: "Nexux locucion ES", creada a medida el 29-ago pidiendo
# mujer espanola de Madrid, castellano neutro, calida y seria, sin tono
# comercial. Las voces de catalogo de ElevenLabs son inglesas hablando espanol y
# se les nota; esta se diseno por descripcion y Ricardo eligio esta de tres.
# Se puede sobrescribir con ELEVENLABS_VOICE_ID si hiciera falta probar otra.
VOZ_ANUNCIO = '3Gp0pxCx0sghnKOF9dtO'
VOZ = os.environ.get('ELEVENLABS_VOICE_ID_ANUNCIO') or VOZ_ANUNCIO
CLAVE = os.environ.get('ELEVENLABS_API_KEY')
AJUSTES = {
    # Estabilidad media: con 0,7 la locucion sale plana y este guion necesita
    # que las preguntas suban. Por debajo de 0,4 empieza a cambiar de tono
    # entre lineas y se nota que son trozos distintos.
    'stability': 0.45,
    'similarity_boost': 0.75,
    'style': 0.25,
    'use_speaker_boost': True,
}


def sintetiza(texto, destino):
    cuerpo = json.dumps({
        'text': texto,
        'model_id': 'eleven_multilingual_v2',
        'voice_settings': AJUSTES,
    }).encode('utf-8')
    peticion = urllib.request.Request(
        'https://api.elevenlabs.io/v1/text-to-speech/%s' % VOZ,
        data=cuerpo,
        headers={'xi-api-key': CLAVE, 'Content-Type': 'application/json'},
    )
    try:
        with urllib.request.urlopen(peticion, timeout=120) as r:
            destino.write_bytes(r.read())
    except urllib.error.HTTPError as e:
        sys.exit('ElevenLabs %s: %s' % (e.code, e.read()[:200].decode('utf-8', 'replace')))


def duracion(fichero):
    return float(subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'csv=p=0', str(fichero)],
        capture_output=True, text=True).stdout)


def main():
    if not VOZ or not CLAVE:
        sys.exit('faltan ELEVENLABS_VOICE_ID o ELEVENLABS_API_KEY en el entorno')
    SALIDA.mkdir(parents=True, exist_ok=True)

    solo = None
    if '--solo' in sys.argv:
        solo = int(sys.argv[sys.argv.index('--solo') + 1])

    trozos = []
    fin_anterior = None
    print('  %-5s %-7s %-7s %-6s  %s' % ('linea', 'entra', 'dura', 'ritmo', 'texto'))
    print('  ' + '-' * 74)
    for i, (segundo, texto) in enumerate(LINEAS, 1):
        mp3 = SALIDA / ('linea-%02d.mp3' % i)
        if solo is None or solo == i or not mp3.exists():
            sintetiza(texto, mp3)
        d = duracion(mp3)

        # Cuanto sitio hay hasta que entra la siguiente, dejando un respiro.
        hasta = LINEAS[i][0] if i < len(LINEAS) else DURACION
        hueco = hasta - segundo - RESPIRO

        # Si no cabe, primero se intenta entrar ANTES en vez de correr: que la
        # voz se adelante un poco al rotulo no se nota --de hecho suena natural,
        # el locutor arranca y el texto aparece-- y acelerar si se nota.
        if d > hueco and fin_anterior is not None:
            margen = segundo - RESPIRO - fin_anterior
            adelanto = min(ADELANTO_MAX, max(0.0, margen))
            if adelanto > 0:
                segundo -= adelanto
                hueco = hasta - segundo - RESPIRO

        usable, ritmo = mp3, 1.0
        if d > hueco > 0:
            # Se aprieta la locucion en vez de recortar el guion: es la pieza
            # aprobada. Por debajo de un 15 % mas rapido no se percibe; por
            # encima si, y entonces el problema es el texto, no la velocidad.
            ritmo = d / hueco
            usable = SALIDA / ('linea-%02d-ajustada.wav' % i)
            subprocess.run(
                ['ffmpeg', '-y', '-loglevel', 'error', '-i', str(mp3),
                 '-filter:a', 'atempo=%.4f' % ritmo, str(usable)], check=True)
            d = duracion(usable)

        aviso = '  <-- DEMASIADO APRETADA: acorta el texto' if ritmo > TOPE_RITMO else ''
        movida = '' if abs(segundo - LINEAS[i - 1][0]) < 0.01 else '  (-%.2f)' % (LINEAS[i - 1][0] - segundo)
        print('  %-5d %-7.2f %-7.2f %-6s  %s%s%s'
              % (i, segundo, d, ('x%.2f' % ritmo) if ritmo > 1 else '—', texto[:36], movida, aviso))
        trozos.append((segundo, usable))
        fin_anterior = segundo + d

    # Se monta sobre un silencio de la duracion exacta del anuncio: cada linea
    # entra en su segundo con adelay y se suman todas.
    entradas, filtros, etiquetas = [], [], []
    for k, (segundo, mp3) in enumerate(trozos):
        entradas += ['-i', str(mp3)]
        ms = int(round(segundo * 1000))
        filtros.append('[%d:a]adelay=%d|%d,aformat=sample_fmts=fltp:sample_rates=%d:channel_layouts=stereo[v%d];'
                       % (k, ms, ms, FPS_AUDIO, k))
        etiquetas.append('[v%d]' % k)

    filtro = (''.join(filtros)
              + ''.join(etiquetas)
              + 'amix=inputs=%d:normalize=0,' % len(trozos)
              + 'apad,atrim=0:%.3f[out]' % DURACION)

    subprocess.run(
        ['ffmpeg', '-y', '-loglevel', 'error'] + entradas
        + ['-filter_complex', filtro, '-map', '[out]',
           '-c:a', 'pcm_s16le', '-ar', str(FPS_AUDIO), str(PISTA)], check=True)

    d = duracion(PISTA)
    print('\n  %s -> %.2f s' % (PISTA, d))
    if abs(d - DURACION) > 0.1:
        sys.exit('la pista dura %.2f y el anuncio %.2f' % (d, DURACION))
    print('  cuadra con el montaje')


if __name__ == '__main__':
    main()
