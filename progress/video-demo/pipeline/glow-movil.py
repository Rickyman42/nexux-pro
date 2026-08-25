"""
Mascara de resplandor v2 para la pantalla del movil del plano 3.

La v1 era una elipse a tope de brillo y quedaba como un plato de luz sobre la mesa.
Aqui la forma es el rectangulo real de la pantalla, en su perspectiva, y la
intensidad baja mucho: una pantalla encendida en primer plano desenfocado se nota
por un brillo suave, no por un fogonazo.
"""
from PIL import Image, ImageDraw, ImageFilter

W, H = 1280, 720

# Cuatro esquinas de la pantalla, medidas sobre el fotograma del segundo 1.
# El movil esta ligeramente girado: el extremo derecho queda mas alto.
PANTALLA = [(266, 607), (466, 588), (488, 603), (290, 624)]

# Nucleo: la pantalla, suave pero contenida
nucleo = Image.new("L", (W, H), 0)
ImageDraw.Draw(nucleo).polygon(PANTALLA, fill=118)
nucleo = nucleo.filter(ImageFilter.GaussianBlur(6))

# Halo: el poco de luz que rebota en la madera. Muy tenue.
xs = [p[0] for p in PANTALLA]
ys = [p[1] for p in PANTALLA]
cx, cy = sum(xs) / 4, sum(ys) / 4
halo = Image.new("L", (W, H), 0)
ImageDraw.Draw(halo).ellipse(
    [cx - 210, cy - 62, cx + 210, cy + 62], fill=16
)
halo = halo.filter(ImageFilter.GaussianBlur(34))

capa = Image.new("L", (W, H), 0)
capa.paste(halo)
capa = Image.composite(nucleo, capa, nucleo.point(lambda v: 255 if v > 8 else 0))

# Blanco frio de pantalla encendida
glow = Image.new("RGBA", (W, H), (208, 226, 255, 0))
glow.putalpha(capa)
glow.save("/tmp/glow.png")

print("mascara v2 escrita. Pico de alfa: %d (antes 255)" % max(capa.getdata()))
