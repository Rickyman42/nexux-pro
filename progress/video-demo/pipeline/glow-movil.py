"""
Mascara de resplandor v4: notificacion de mensaje entrante.

Historial de lo que fallo, para no repetirlo:
  v1  elipse a tope de brillo        -> un plato de luz sobre la mesa
  v2  rectangulo suave y tenue       -> creible, pero se veia poco y el brillo
                                        continuo se lee como una LLAMADA
  v3  mas brillo + punto verde       -> el verde tenia el borde nitido y cantaba
                                        a pegote: el resto del plano esta
                                        desenfocado y el punto no
  v4  el verde con el mismo desenfoque que el movil, y menos neon

El logo de WhatsApp no se dibuja: solo la luz verde que daria. El logo es suyo.
"""
from PIL import Image, ImageDraw, ImageFilter

W, H = 1280, 720

# Cuatro esquinas de la pantalla, medidas sobre el fotograma del segundo 1.
PANTALLA = [(266, 607), (466, 588), (488, 603), (290, 624)]
xs = [p[0] for p in PANTALLA]
ys = [p[1] for p in PANTALLA]
cx, cy = sum(xs) / 4, sum(ys) / 4

# --- alfa ---------------------------------------------------------------
nucleo = Image.new("L", (W, H), 0)
ImageDraw.Draw(nucleo).polygon(PANTALLA, fill=175)
nucleo = nucleo.filter(ImageFilter.GaussianBlur(6))

halo = Image.new("L", (W, H), 0)
ImageDraw.Draw(halo).ellipse([cx - 215, cy - 66, cx + 215, cy + 66], fill=26)
halo = halo.filter(ImageFilter.GaussianBlur(34))

alfa = Image.new("L", (W, H), 0)
alfa.paste(halo)
alfa = Image.composite(nucleo, alfa, nucleo.point(lambda v: 255 if v > 8 else 0))

# El icono: mismo desenfoque que tiene el movil en el plano, para que no cante
icono = Image.new("L", (W, H), 0)
ix, iy = 324, 608
ImageDraw.Draw(icono).ellipse([ix - 24, iy - 15, ix + 24, iy + 15], fill=235)
icono = icono.filter(ImageFilter.GaussianBlur(14))

alfa = Image.composite(
    Image.blend(alfa, icono, 0.75), alfa, icono.point(lambda v: 255 if v > 25 else 0)
)

# --- color --------------------------------------------------------------
color = Image.new("RGB", (W, H), (214, 231, 255))
verde = Image.new("RGB", (W, H), (60, 196, 116))
color = Image.composite(verde, color, icono.point(lambda v: min(255, int(v * 1.1))))

glow = color.convert("RGBA")
glow.putalpha(alfa)
glow.save("/tmp/glow.png")

print("mascara v4: pico de alfa %d" % max(alfa.getdata()))
