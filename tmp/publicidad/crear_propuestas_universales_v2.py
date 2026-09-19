from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
TMP = ROOT / "tmp" / "publicidad"
OUT = ROOT / "output" / "publicidad" / "universales-v2"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(TMP / "deps"))

import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageFilter


W, H = 1240, 1748
TEAL = "#45C9C1"
TEAL_DARK = "#178F88"
INK = "#141619"
CREAM = "#F5F0E8"
WHITE = "#FFFFFF"
MUTED = "#62676D"
RED = "#C64D43"
QR_URL = "https://nexux.pro/demo"
FONT = Path("C:/Windows/Fonts")


def font(name, size):
    return ImageFont.truetype(str(FONT / name), size)


SANS = lambda size: font("arial.ttf", size)
BOLD = lambda size: font("arialbd.ttf", size)
SERIF = lambda size: font("georgia.ttf", size)
ITALIC = lambda size: font("georgiai.ttf", size)


def cover(path):
    source = Image.open(path).convert("RGB")
    scale = max(W / source.width, H / source.height)
    resized = source.resize((round(source.width * scale), round(source.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - W) // 2
    top = (resized.height - H) // 2
    return resized.crop((left, top, left + W, top + H)).convert("RGBA")


def logo(draw, x=66, y=55, light=False):
    fg = WHITE if light else INK
    draw.rounded_rectangle((x, y, x + 62, y + 62), radius=13, fill=TEAL)
    draw.text((x + 31, y + 30), "N", font=ITALIC(34), fill=WHITE, anchor="mm")
    draw.text((x + 80, y + 4), "nexux", font=BOLD(32), fill=fg)
    draw.text((x + 174, y + 4), ".pro", font=BOLD(32), fill=TEAL)
    draw.text((x + 80, y + 42), "RECEPCIONISTA IA", font=BOLD(13), fill=TEAL if light else MUTED)


def qr_image(size=270):
    code = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=12, border=4)
    code.add_data(QR_URL)
    code.make(fit=True)
    return code.make_image(fill_color="black", back_color="white").convert("RGB").resize((size, size), Image.Resampling.NEAREST)


def add_qr(image, x, y, size=270, label_color=INK):
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((x - 17, y - 17, x + size + 17, y + size + 17), radius=20, fill=WHITE)
    image.paste(qr_image(size), (x, y))
    draw.text((x + size / 2, y + size + 31), "ESCANEA Y MIRA LA DEMO", font=BOLD(15), fill=label_color, anchor="mm")


def rounded_panel(image, box, fill, radius=28, outline=None, width=1):
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def proposal_one():
    image = cover(TMP / "base-v2-montaje.png")
    draw = ImageDraw.Draw(image)
    logo(draw)
    draw.text((66, 156), "TUS MANOS ESTÁN", font=BOLD(53), fill=INK)
    draw.text((66, 213), "TRABAJANDO.", font=BOLD(53), fill=INK)
    draw.text((66, 274), "Lara se ocupa de los mensajes.", font=ITALIC(42), fill=TEAL_DARK)

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle((42, 1330, 1198, 1710), radius=36, fill=(18, 21, 24, 240))
    image = Image.alpha_composite(image, overlay)
    draw = ImageDraw.Draw(image)
    draw.text((76, 1372), "Responde. Mira tu agenda.", font=SERIF(35), fill=WHITE)
    draw.text((76, 1421), "Deja la cita puesta.", font=ITALIC(38), fill=TEAL)
    draw.text((76, 1494), "WhatsApp · Telegram · Web", font=BOLD(20), fill="#D6D9DC")
    draw.rounded_rectangle((76, 1543, 338, 1617), radius=37, fill=TEAL)
    draw.text((207, 1580), "29 €/mes", font=BOLD(27), fill=INK, anchor="mm")
    draw.text((76, 1640), "Sin comisiones", font=SANS(18), fill="#D6D9DC")
    add_qr(image, 866, 1370, 245, WHITE)
    image.convert("RGB").save(OUT / "01-manos-ocupadas.png", quality=96)


def message_bubble(draw, box, text_lines, incoming=True):
    fill = WHITE if incoming else "#D9F5EE"
    draw.rounded_rectangle(box, radius=28, fill=fill)
    x1, y1, _, _ = box
    for i, line in enumerate(text_lines):
        draw.text((x1 + 26, y1 + 22 + i * 35), line, font=SANS(25), fill=INK)


def proposal_two():
    image = cover(TMP / "base-v2-mesa.png")
    veil = Image.new("RGBA", image.size, (245, 240, 232, 0))
    vd = ImageDraw.Draw(veil)
    vd.rectangle((0, 0, W, 560), fill=(245, 240, 232, 248))
    image = Image.alpha_composite(image, veil)
    draw = ImageDraw.Draw(image)
    logo(draw)
    draw.text((66, 157), "TE ESCRIBEN MIENTRAS", font=BOLD(48), fill=INK)
    draw.text((66, 211), "ESTÁS TRABAJANDO.", font=BOLD(48), fill=INK)
    draw.text((66, 276), "Tú no paras. Lara responde.", font=ITALIC(42), fill=TEAL_DARK)

    rounded_panel(image, (70, 575, 1170, 1075), (244, 241, 235, 238), 34)
    draw = ImageDraw.Draw(image)
    draw.text((104, 608), "WhatsApp", font=BOLD(21), fill=TEAL_DARK)
    message_bubble(draw, (104, 656, 770, 748), ["Hola, ¿tenéis cita mañana por la tarde?"], True)
    message_bubble(draw, (300, 778, 1136, 905), ["Sí. Tengo hueco a las 17:30.", "¿Te viene bien?"], False)
    draw.rounded_rectangle((300, 930, 1136, 1036), radius=25, fill=TEAL_DARK)
    draw.line((420, 979, 431, 992), fill=WHITE, width=6)
    draw.line((431, 992, 451, 968), fill=WHITE, width=6)
    draw.text((748, 983), "CITA CONFIRMADA · 17:30", font=BOLD(28), fill=WHITE, anchor="mm")

    rounded_panel(image, (42, 1320, 1198, 1710), (255, 255, 255, 244), 36)
    draw = ImageDraw.Draw(image)
    draw.text((76, 1363), "Lara responde por ti", font=SERIF(37), fill=INK)
    draw.text((76, 1415), "y deja la cita en tu agenda.", font=ITALIC(36), fill=TEAL_DARK)
    draw.text((76, 1490), "WhatsApp · Telegram · Web", font=BOLD(19), fill=MUTED)
    draw.rounded_rectangle((76, 1540, 338, 1614), radius=37, fill=INK)
    draw.text((207, 1577), "29 €/mes", font=BOLD(27), fill=WHITE, anchor="mm")
    draw.text((76, 1638), "Sin comisiones", font=SANS(18), fill=MUTED)
    add_qr(image, 866, 1360, 245, INK)
    image.convert("RGB").save(OUT / "02-mensaje-a-cita-real.png", quality=96)


def proposal_three():
    image = Image.new("RGBA", (W, H), CREAM)
    draw = ImageDraw.Draw(image)
    logo(draw)
    draw.text((66, 190), "Cada mensaje que", font=SERIF(66), fill=INK)
    draw.text((66, 269), "no contestas es...", font=SERIF(66), fill=INK)
    draw.text((66, 357), "una cita que no vuelve.", font=ITALIC(63), fill=TEAL_DARK)

    draw.line((66, 470, 1174, 470), fill="#D8D2C8", width=2)
    steps = [
        ("1", "ENTRA EL MENSAJE", "“¿Tenéis cita mañana?”"),
        ("2", "LARA RESPONDE", "Consulta tus huecos."),
        ("3", "LA CITA QUEDA PUESTA", "En tu agenda, sin parar."),
    ]
    y = 528
    for number, title, body in steps:
        draw.ellipse((72, y, 138, y + 66), fill=TEAL if number != "3" else INK)
        draw.text((105, y + 33), number, font=BOLD(25), fill=INK if number != "3" else WHITE, anchor="mm")
        draw.text((172, y - 2), title, font=BOLD(24), fill=INK)
        draw.text((172, y + 35), body, font=SERIF(28), fill=MUTED)
        if number != "3":
            draw.line((105, y + 77, 105, y + 130), fill="#A8DDD9", width=4)
        y += 175

    draw.rounded_rectangle((66, 1090, 1174, 1248), radius=30, fill=INK)
    draw.text((104, 1128), "Tú sigues trabajando.", font=SERIF(34), fill=WHITE)
    draw.text((104, 1175), "Lara sigue contestando.", font=ITALIC(36), fill=TEAL)

    draw.text((66, 1325), "WhatsApp · Telegram · Web", font=BOLD(20), fill=MUTED)
    draw.rounded_rectangle((66, 1376, 342, 1454), radius=39, fill=TEAL)
    draw.text((204, 1415), "29 €/mes", font=BOLD(28), fill=INK, anchor="mm")
    draw.text((66, 1481), "Sin comisiones · Sin permanencia", font=SANS(18), fill=MUTED)
    draw.text((66, 1581), "MIRA CÓMO FUNCIONA", font=BOLD(18), fill=INK)
    draw.text((66, 1618), "nexux.pro", font=BOLD(28), fill=TEAL_DARK)
    add_qr(image, 858, 1348, 260, INK)
    image.convert("RGB").save(OUT / "03-cartel-tipografico.png", quality=96)


if __name__ == "__main__":
    proposal_one()
    proposal_two()
    proposal_three()
    for path in sorted(OUT.glob("*.png")):
        print(f"{path.name}\t{path.stat().st_size}")
