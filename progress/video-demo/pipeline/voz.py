#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera la voz en off del anuncio y la monta en una pista de 55,71 s.

**Por bloques, no frase a frase.** La primera version pedia las trece frases en
trece peticiones sueltas y sonaba a robot leyendo: cada una arrancaba de cero,
sin saber que venia antes, y no habia ni continuidad ni intencion. Ricardo lo
dijo tal cual --"poco dinamica, le falta enfasis, naturalidad, que sea humana"--
y tenia razon.

Ahora cada acto se pide de una tirada con el modelo expresivo (`eleven_v3`), que
ademas acepta marcas de intencion dentro del texto: [tired], [sighs], [warm].
Dentro del acto la voz fluye como una persona hablando; entre actos hay silencio,
que es donde el anuncio cambia de tercio de todos modos.

Los bloques largos son los dos donde mas se notaba el troceo --el acto del dolor
y el de las objeciones--. Los planos de producto van sueltos porque ahi la frase
tiene que caer sobre su plano al segundo.

Los numeros van con letra ("veintinueve euros") porque el sintetizador lee
"29 EUR" como "veintinueve" a secas.

  voz2.py            genera todo
  voz2.py --solo N   regenera solo el bloque N
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

# (segundo en que entra, hasta cuando tiene sitio, texto con sus marcas)
# El texto locutado NO es palabra por palabra el del rotulo: en pantalla se lee
# la frase entera y la voz dice el remate. La voz elegida habla despacio --de ahi
# que suene real-- y el guion completo no cabe a ritmo natural.
BLOQUES = [
    (0.30, 14.30,
     '[tired] Son las once y media. Tienes las manos ocupadas. '
     '[sighs] El móvil lleva vibrando desde las diez. '
     'Habrá cuatro mensajes. [resigned] Y nunca sabrás quiénes eran.'),

    (14.30, 16.30, '[hopeful] Alguien contestó por ti.'),

    (16.30, 25.30, 'Contestó, ofreció hora... y cerró la cita.'),

    (25.30, 31.85, '[warm] Y la puso en tu agenda. Sola.'),

    (31.85, 46.50,
     '[reassuring] Pruébala tú. Sin registrarte. '
     'Es tu WhatsApp, el de siempre. '
     'Te devolvemos el dinero: treinta días. '
     'Veintinueve euros al mes.'),

    (46.50, DURACION,
     '[serious] Una cosa antes de que sigas: '
     '¿cuántos mensajes tienes ahora mismo sin abrir?'),
]

RESPIRO = 0.20
TOPE_RITMO = 1.15

# "Nexux locucion ES", creada a medida el 29-ago: mujer espanola de Madrid,
# castellano neutro, calida y seria, sin tono comercial. Ricardo la eligio de
# tres disenadas por descripcion; las de catalogo son inglesas hablando espanol.
VOZ_ANUNCIO = '3Gp0pxCx0sghnKOF9dtO'
VOZ = os.environ.get('ELEVENLABS_VOICE_ID_ANUNCIO') or VOZ_ANUNCIO
CLAVE = os.environ.get('ELEVENLABS_API_KEY')

# Estabilidad baja y estilo alto: es lo que da variacion de entonacion. Con la
# estabilidad por defecto la lectura sale plana, que es justo el problema.
MODELO = 'eleven_v3'
AJUSTES = {
    'stability': 0.3,
    'similarity_boost': 0.75,
    'style': 0.6,
    'use_speaker_boost': True,
}


def sintetiza(texto, destino):
    cuerpo = json.dumps({
        'text': texto, 'model_id': MODELO, 'voice_settings': AJUSTES,
    }).encode('utf-8')
    peticion = urllib.request.Request(
        'https://api.elevenlabs.io/v1/text-to-speech/%s' % VOZ,
        data=cuerpo,
        headers={'xi-api-key': CLAVE, 'Content-Type': 'application/json'},
    )
    try:
        with urllib.request.urlopen(peticion, timeout=240) as r:
            destino.write_bytes(r.read())
    except urllib.error.HTTPError as e:
        sys.exit('ElevenLabs %s: %s' % (e.code, e.read()[:300].decode('utf-8', 'replace')))


def duracion(f):
    return float(subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'csv=p=0', str(f)], capture_output=True, text=True).stdout)


def main():
    if not VOZ or not CLAVE:
        sys.exit('faltan ELEVENLABS_VOICE_ID_ANUNCIO o ELEVENLABS_API_KEY')
    SALIDA.mkdir(parents=True, exist_ok=True)

    solo = int(sys.argv[sys.argv.index('--solo') + 1]) if '--solo' in sys.argv else None

    trozos = []
    print('  %-6s %-7s %-7s %-6s  %s' % ('bloque', 'entra', 'dura', 'ritmo', 'texto'))
    print('  ' + '-' * 76)
    for i, (entra, hasta, texto) in enumerate(BLOQUES, 1):
        mp3 = SALIDA / ('bloque-%02d.mp3' % i)
        if solo is None or solo == i or not mp3.exists():
            sintetiza(texto, mp3)
        d = duracion(mp3)

        hueco = hasta - entra - RESPIRO
        usable, ritmo = mp3, 1.0
        if d > hueco > 0:
            ritmo = d / hueco
            usable = SALIDA / ('bloque-%02d-ajustado.wav' % i)
            subprocess.run(
                ['ffmpeg', '-y', '-loglevel', 'error', '-i', str(mp3),
                 '-filter:a', 'atempo=%.4f' % ritmo, str(usable)], check=True)
            d = duracion(usable)

        aviso = '  <-- APRETADO: acorta el texto' if ritmo > TOPE_RITMO else ''
        # Sobra sitio: se dice para poder dar mas aire al guion si interesa.
        if ritmo == 1.0 and hueco - d > 1.5:
            aviso = '  (sobran %.1f s)' % (hueco - d)
        limpio = texto.replace('\n', ' ')
        for marca in ('[tired]', '[sighs]', '[resigned]', '[hopeful]', '[warm]',
                      '[reassuring]', '[serious]'):
            limpio = limpio.replace(marca, '')
        print('  %-6d %-7.2f %-7.2f %-6s  %s%s'
              % (i, entra, d, ('x%.2f' % ritmo) if ritmo > 1 else '—',
                 ' '.join(limpio.split())[:36], aviso))
        trozos.append((entra, usable))

    entradas, filtros, etiquetas = [], [], []
    for k, (entra, f) in enumerate(trozos):
        entradas += ['-i', str(f)]
        ms = int(round(entra * 1000))
        filtros.append('[%d:a]adelay=%d|%d,aformat=sample_fmts=fltp:sample_rates=%d:'
                       'channel_layouts=stereo[v%d];' % (k, ms, ms, FPS_AUDIO, k))
        etiquetas.append('[v%d]' % k)

    filtro = (''.join(filtros) + ''.join(etiquetas)
              + 'amix=inputs=%d:normalize=0,apad,atrim=0:%.3f[out]'
              % (len(trozos), DURACION))

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
