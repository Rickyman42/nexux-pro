from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
TMP = ROOT / "tmp" / "publicidad"
OUT = ROOT / "output" / "publicidad"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(TMP / "deps"))

import qrcode
from PIL import Image, ImageDraw, ImageFont


TEAL = "#4CCBC3"
TEAL_DARK = "#168E87"
INK = "#15181D"
WHITE = "#FFFFFF"
MUTED = "#656B73"
RED = "#F36C67"
QR_URL = "https://nexux.pro/demo"
FONT = Path("C:/Windows/Fonts")


def font(name, size):
    return ImageFont.truetype(str(FONT / name), size)


SANS = lambda size: font("arial.ttf", size)
BOLD = lambda size: font("arialbd.ttf", size)
SERIF = lambda size: font("georgia.ttf", size)
ITALIC = lambda size: font("georgiai.ttf", size)


def gradient_overlay(image, top, bottom, start_alpha, end_alpha, color=(0, 0, 0)):
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    pixels = overlay.load()
    span = max(1, bottom - top)
    for y in range(top, bottom):
        alpha = int(start_alpha + (end_alpha - start_alpha) * ((y - top) / span))
        for x in range(image.width):
            pixels[x, y] = (*color, alpha)
    return Image.alpha_composite(image.convert("RGBA"), overlay)


def logo(draw, x, y, dark=True):
    draw.rounded_rectangle((x, y, x + 66, y + 66), radius=14, fill=TEAL)
    draw.text((x + 33, y + 31), "N", font=ITALIC(36), fill=WHITE if dark else INK, anchor="mm")
    color = WHITE if dark else INK
    draw.text((x + 84, y + 6), "nexux", font=BOLD(34), fill=color)
    draw.text((x + 181, y + 6), ".pro", font=BOLD(34), fill=TEAL)
    draw.text((x + 84, y + 44), "RECEPCIONISTA IA", font=BOLD(14), fill=TEAL if dark else MUTED)


def qr_image(size=236):
    code = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=4)
    code.add_data(QR_URL)
    code.make(fit=True)
    return code.make_image(fill_color="black", back_color="white").convert("RGB").resize((size, size), Image.Resampling.NEAREST)


def footer(image, dark, line_one, line_two):
    draw = ImageDraw.Draw(image)
    panel_y = 1215
    panel_fill = (20, 24, 29, 242) if dark else (255, 255, 255, 244)
    draw.rounded_rectangle((48, panel_y, 976, 1492), radius=32, fill=panel_fill)
    text_color = WHITE if dark else INK
    muted = "#C9CDD2" if dark else MUTED
    draw.text((78, panel_y + 38), line_one, font=BOLD(29), fill=TEAL)
    draw.text((78, panel_y + 82), line_two, font=BOLD(25), fill=text_color)
    draw.rounded_rectangle((78, panel_y + 136, 278, panel_y + 206), radius=35, fill=TEAL if dark else INK)
    draw.text((178, panel_y + 171), "29 €/mes", font=BOLD(25), fill=INK if dark else WHITE, anchor="mm")
    draw.text((78, panel_y + 224), "Sin comisiones · Sin permanencia", font=SANS(17), fill=muted)
    qr = qr_image()
    qr_x, qr_y = 708, panel_y + 20
    draw.rounded_rectangle((qr_x - 18, qr_y - 18, qr_x + 254, qr_y + 254), radius=22, fill=WHITE)
    image.paste(qr, (qr_x, qr_y))
    draw.text((470, panel_y + 184), "Escanea y mira la demo", font=BOLD(17), fill=text_color)
    draw.text((470, panel_y + 214), "nexux.pro", font=BOLD(17), fill=TEAL_DARK if not dark else TEAL)


def proposal_one():
    image = Image.open(TMP / "base-1-telefono.png").convert("RGBA")
    image = gradient_overlay(image, 0, 560, 210, 0)
    draw = ImageDraw.Draw(image)
    logo(draw, 62, 55, dark=True)
    draw.text((62, 170), "Cada mensaje que", font=SERIF(62), fill=WHITE)
    draw.text((62, 242), "no contestas puede", font=SERIF(62), fill=WHITE)
    draw.text((62, 314), "ser una cita perdida.", font=ITALIC(61), fill=TEAL)
    draw.text((64, 405), "Lara responde y reserva mientras tú trabajas.", font=BOLD(24), fill="#D8DDE1")
    footer(image, True, "No pierdas la próxima cita.", "Deja que Lara responda por ti.")
    image.convert("RGB").save(OUT / "propuesta-1-telefono-premium.png", quality=95)


def proposal_two():
    image = Image.open(TMP / "base-2-transformacion.png").convert("RGBA")
    draw = ImageDraw.Draw(image)
    logo(draw, 62, 55, dark=False)
    draw.text((62, 168), "De mensaje a cita.", font=ITALIC(66), fill=TEAL_DARK)
    draw.text((62, 245), "Sin que tengas que parar.", font=SERIF(55), fill=INK)
    draw.text((64, 310), "Responde por WhatsApp, Telegram y web.", font=BOLD(23), fill=MUTED)
    footer(image, False, "El mensaje entra. La cita queda.", "Tú sigues con tu negocio.")
    image.convert("RGB").save(OUT / "propuesta-2-mensaje-a-cita.png", quality=95)


def proposal_three():
    image = Image.open(TMP / "base-3-antes-despues.png").convert("RGBA")
    image = gradient_overlay(image, 0, 500, 190, 0)
    draw = ImageDraw.Draw(image)
    logo(draw, 62, 55, dark=True)
    draw.text((62, 172), "Un mensaje sin respuesta", font=SERIF(55), fill=WHITE)
    draw.text((62, 238), "se va.", font=SERIF(55), fill=RED)
    draw.text((62, 310), "Una cita confirmada se queda.", font=ITALIC(50), fill=TEAL)
    draw.rounded_rectangle((76, 650, 276, 702), radius=26, fill=(55, 17, 18, 220))
    draw.text((176, 676), "SIN RESPUESTA", font=BOLD(18), fill=RED, anchor="mm")
    draw.rounded_rectangle((748, 650, 948, 702), radius=26, fill=(10, 73, 69, 220))
    draw.text((848, 676), "CITA CERRADA", font=BOLD(18), fill=TEAL, anchor="mm")
    footer(image, True, "Convierte consultas en citas.", "Lara responde las 24 horas.")
    image.convert("RGB").save(OUT / "propuesta-3-antes-despues.png", quality=95)


if __name__ == "__main__":
    proposal_one()
    proposal_two()
    proposal_three()
    for path in sorted(OUT.glob("propuesta-*.png")):
        print(path)
