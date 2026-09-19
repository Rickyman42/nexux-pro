from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
TMP = ROOT / "tmp" / "publicidad"
OUT = ROOT / "output" / "publicidad" / "universales-v4"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(TMP / "deps"))

import qrcode
from PIL import Image, ImageDraw, ImageFont


W, H = 1240, 1748
TEAL = "#45C9C1"
INK = "#121519"
WHITE = "#FFFFFF"
FONT = Path("C:/Windows/Fonts")


def font(name, size):
    return ImageFont.truetype(str(FONT / name), size)


BOLD = lambda size: font("arialbd.ttf", size)
SANS = lambda size: font("arial.ttf", size)
ITALIC = lambda size: font("georgiai.ttf", size)


def cover(path):
    source = Image.open(path).convert("RGB")
    scale = max(W / source.width, H / source.height)
    resized = source.resize((round(source.width * scale), round(source.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - W) // 2
    top = (resized.height - H) // 2
    return resized.crop((left, top, left + W, top + H)).convert("RGBA")


def qr_image(size=250):
    code = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=12, border=4)
    code.add_data("https://nexux.pro/demo")
    code.make(fit=True)
    return code.make_image(fill_color="black", back_color="white").convert("RGB").resize((size, size), Image.Resampling.NEAREST)


image = cover(TMP / "base-v3-tu-lara.png")
draw = ImageDraw.Draw(image)

# Marca
draw.rounded_rectangle((62, 52, 124, 114), radius=13, fill=TEAL)
draw.text((93, 82), "N", font=ITALIC(34), fill=WHITE, anchor="mm")
draw.text((142, 56), "nexux", font=BOLD(31), fill=WHITE)
draw.text((235, 56), ".pro", font=BOLD(31), fill=TEAL)
draw.text((142, 94), "RECEPCIONISTA IA", font=BOLD(13), fill=TEAL)

# El producto se entiende incluso sin leer el resto del folleto
draw.text((62, 158), "RESPONDE MENSAJES.", font=BOLD(48), fill=WHITE)
draw.text((62, 215), "RESERVA CITAS.", font=BOLD(48), fill=WHITE)
draw.text((62, 278), "Mientras tú trabajas.", font=ITALIC(44), fill=TEAL)

# Oferta y producto, sin competir con las personas
panel = Image.new("RGBA", image.size, (0, 0, 0, 0))
pd = ImageDraw.Draw(panel)
pd.rounded_rectangle((42, 1270, 1198, 1708), radius=36, fill=(245, 241, 234, 247))
image = Image.alpha_composite(image, panel)
draw = ImageDraw.Draw(image)
draw.text((76, 1310), "ASÍ FUNCIONA", font=BOLD(16), fill="#178F88")

steps = [
    ("1", "Te escriben: “¿Tenéis cita mañana?”"),
    ("2", "Lara responde y consulta tu agenda."),
    ("3", "La cita queda reservada."),
]
for index, (number, text) in enumerate(steps):
    y = 1351 + index * 55
    draw.ellipse((76, y, 112, y + 36), fill=TEAL if number != "3" else INK)
    draw.text((94, y + 18), number, font=BOLD(16), fill=INK if number != "3" else WHITE, anchor="mm")
    draw.text((130, y + 4), text, font=SANS(20), fill=INK)

draw.text((76, 1534), "WhatsApp · Telegram · Web", font=BOLD(18), fill="#555B61")
draw.rounded_rectangle((76, 1574, 350, 1652), radius=39, fill=INK)
draw.text((213, 1613), "29 €/mes", font=BOLD(28), fill=WHITE, anchor="mm")
draw.text((376, 1594), "Sin comisiones", font=SANS(18), fill="#62676D")

qr = qr_image()
qx, qy = 874, 1320
draw.rounded_rectangle((qx - 16, qy - 16, qx + 266, qy + 266), radius=19, fill=WHITE)
image.paste(qr, (qx, qy))
draw.text((qx + 125, qy + 280), "ESCANEA Y MIRA LA DEMO", font=BOLD(15), fill=INK, anchor="mm")

path = OUT / "01-responde-y-reserva.png"
image.convert("RGB").save(path, quality=96)
print(f"{path}\t{path.stat().st_size}")
