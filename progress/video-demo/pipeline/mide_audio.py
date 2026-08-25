"""Mide el pico de audio en ventanas de 0,25 s, antes y despues del zumbido.

Sin audioop: lo quitaron en Python 3.13, asi que el pico se calcula a mano
sobre las muestras de 16 bits.
"""
import subprocess
import wave
import array
import os

VENTANAS = [0.5, 1.0, 1.9, 2.8, 3.8, 5.0, 5.8, 6.7]


def pico(fichero, t):
    tmp = "/tmp/_seg.wav"
    if os.path.exists(tmp):
        os.remove(tmp)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-t", "0.25", "-i", fichero,
         "-ac", "1", "-ar", "48000", tmp],
        check=True,
    )
    if not os.path.exists(tmp) or os.path.getsize(tmp) < 100:
        return None
    with wave.open(tmp) as w:
        datos = w.readframes(w.getnframes())
    if not datos:
        return None
    muestras = array.array("h")
    muestras.frombytes(datos[: len(datos) - len(datos) % 2])
    if not muestras:
        return None
    return max(abs(m) for m in muestras) / 32768.0


sin = [pico("/tmp/p3-movil.mp4", t) for t in VENTANAS]
con = [pico("/tmp/p3-final.mp4", t) for t in VENTANAS]

print("  t       sin zumbido   con zumbido   diferencia")
for t, a, b in zip(VENTANAS, sin, con):
    if a is None or b is None:
        print("  %-5.1f   (sin audio medible)" % t)
        continue
    marca = "  <-- ZUMBIDO" if b - a > 0.05 else ""
    print("  %-5.1f   %10.3f   %10.3f   %+9.3f%s" % (t, a, b, b - a, marca))
