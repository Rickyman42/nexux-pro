from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
TMP = ROOT / "tmp" / "publicidad"
PUBLIC = ROOT / "public" / "img"
OUT = ROOT / "output" / "publicidad" / "universales-v5"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(TMP / "deps"))

import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageFilter


W, H = 1240, 1748
TEAL = "#47CBC3"
TEAL_DARK = "#168F88"
INK = "#13161A"
CREAM = "#F5F1EA"
WHITE = "#FFFFFF"
MUTED = "#62686F"
GREEN = "#1F9D62"
RED = "#D85C54"
FONT = Path("C:/Windows/Fonts")


def font(name, size):
    return ImageFont.truetype(str(FONT / name), size)


SANS = lambda size: font("arial.ttf", size)
BOLD = lambda size: font("arialbd.ttf", size)
SERIF = lambda size: font("georgia.ttf", size)
ITALIC = lambda size: font("georgiai.ttf", size)


def fit_cover(path, size=(W, H), shift_x=0):
    source = Image.open(path).convert("RGB")
    target_w, target_h = size
    scale = max(target_w / source.width, target_h / source.height)
    resized = source.resize((round(source.width * scale), round(source.height * scale)), Image.Resampling.LANCZOS)
    left = max(0, min(resized.width - target_w, (resized.width - target_w) // 2 + shift_x))
    top = max(0, (resized.height - target_h) // 2)
    return resized.crop((left, top, left + target_w, top + target_h)).convert("RGBA")


def logo(draw, x=60, y=50, light=False):
    fg = WHITE if light else INK
    draw.rounded_rectangle((x, y, x + 62, y + 62), radius=13, fill=TEAL)
    draw.text((x + 31, y + 30), "N", font=ITALIC(34), fill=WHITE, anchor="mm")
    draw.text((x + 80, y + 4), "nexux", font=BOLD(31), fill=fg)
    draw.text((x + 173, y + 4), ".pro", font=BOLD(31), fill=TEAL)
    draw.text((x + 80, y + 42), "RECEPCIONISTA IA", font=BOLD(13), fill=TEAL)


def qr_image(size=246):
    code = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=12, border=4)
    code.add_data("https://nexux.pro/demo")
    code.make(fit=True)
    return code.make_image(fill_color="black", back_color="white").convert("RGB").resize((size, size), Image.Resampling.NEAREST)


def add_qr(image, x, y, size=246, dark_label=False):
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((x - 16, y - 16, x + size + 16, y + size + 16), radius=19, fill=WHITE)
    image.paste(qr_image(size), (x, y))
    draw.text((x + size / 2, y + size + 31), "ESCANEA Y HABLA CON LARA", font=BOLD(14), fill=WHITE if dark_label else INK, anchor="mm")


def chat_card(width=500, height=650, compact=False):
    card = Image.new("RGBA", (width, height), (244, 240, 234, 255))
    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=35, fill="#EEE7DE", outline="#D7CEC3", width=2)
    draw.rounded_rectangle((0, 0, width - 1, 98), radius=35, fill=TEAL_DARK)
    draw.rectangle((0, 62, width - 1, 98), fill=TEAL_DARK)
    draw.ellipse((26, 22, 82, 78), fill=TEAL)
    draw.text((54, 50), "L", font=ITALIC(29), fill=WHITE, anchor="mm")
    draw.text((102, 20), "Lara · Recepcionista IA", font=BOLD(22), fill=WHITE)
    draw.text((102, 54), "en línea", font=SANS(17), fill="#D5F5F1")

    messages = [
        ("Hola, ¿tenéis cita mañana?", False),
        ("Sí. Queda libre a las 17:30.\n¿Te viene bien?", True),
        ("Perfecto.", False),
        ("Cita confirmada · Mañana 17:30", True),
    ]
    y = 126
    for text, outgoing in messages:
        lines = text.split("\n")
        bubble_h = 62 + max(0, len(lines) - 1) * 30
        bubble_w = width - 110 if len(text) > 14 else 235
        x1 = width - bubble_w - 28 if outgoing else 28
        fill = "#D2F2EC" if outgoing else WHITE
        draw.rounded_rectangle((x1, y, x1 + bubble_w, y + bubble_h), radius=24, fill=fill)
        for i, line in enumerate(lines):
            draw.text((x1 + 22, y + 18 + i * 30), line, font=SANS(18 if compact else 20), fill=INK)
        y += bubble_h + 22

    draw.rounded_rectangle((28, height - 66, width - 28, height - 24), radius=20, fill=WHITE)
    draw.text((48, height - 56), "Escribe un mensaje…", font=SANS(16), fill="#9A9EA2")
    return card


def agenda_crop(size=(570, 420)):
    source = Image.open(PUBLIC / "crm-agenda-real.webp").convert("RGB")
    crop = source.crop((850, 220, 2600, 1450))
    frame = Image.new("RGBA", size, WHITE)
    target = crop.copy()
    target.thumbnail((size[0] - 30, size[1] - 78), Image.Resampling.LANCZOS)
    frame.paste(target, ((size[0] - target.width) // 2, 56))
    draw = ImageDraw.Draw(frame)
    draw.rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius=26, outline="#D8DDE1", width=2)
    draw.text((24, 17), "TU AGENDA", font=BOLD(17), fill=TEAL_DARK)
    draw.ellipse((size[0] - 54, 17, size[0] - 30, 41), fill=GREEN)
    return frame


def price_and_channels(draw, x, y, dark=False):
    text = WHITE if dark else INK
    muted = "#D0D4D7" if dark else MUTED
    draw.text((x, y), "WhatsApp · Telegram · Web", font=BOLD(18), fill=muted)
    draw.rounded_rectangle((x, y + 42, x + 278, y + 120), radius=39, fill=TEAL if dark else INK)
    draw.text((x + 139, y + 81), "29 €/mes", font=BOLD(28), fill=INK if dark else WHITE, anchor="mm")
    draw.text((x + 300, y + 63), "Sin comisiones", font=SANS(18), fill=muted)


def proposal_one():
    image = fit_cover(TMP / "base-v3-tu-lara.png")
    draw = ImageDraw.Draw(image)
    logo(draw, light=True)
    draw.text((60, 158), "Cada mensaje que no", font=SERIF(48), fill=WHITE)
    draw.text((60, 217), "contestas puede ser", font=SERIF(48), fill=WHITE)
    draw.text((60, 278), "una cita perdida.", font=ITALIC(50), fill=TEAL)
    draw.text((62, 348), "Lara responde y reserva mientras tú trabajas.", font=BOLD(20), fill="#E0E3E5")

    chat = chat_card(470, 610, compact=True)
    shadow = Image.new("RGBA", (500, 640), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((14, 14, 490, 632), radius=36, fill=(0, 0, 0, 85))
    image.alpha_composite(shadow, (32, 445))
    image.alpha_composite(chat, (42, 435))

    agenda = agenda_crop((600, 400))
    image.alpha_composite(agenda, (600, 810))
    draw = ImageDraw.Draw(image)
    draw.line((520, 1010, 585, 1010), fill=TEAL, width=9)
    draw.polygon([(585, 996), (610, 1010), (585, 1024)], fill=TEAL)

    panel = Image.new("RGBA", image.size, (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle((40, 1290, 1200, 1710), radius=38, fill=(18, 21, 25, 244))
    image = Image.alpha_composite(image, panel)
    draw = ImageDraw.Draw(image)
    draw.text((76, 1337), "MENSAJE → RESPUESTA → CITA EN TU AGENDA", font=BOLD(20), fill=TEAL)
    draw.text((76, 1388), "Así de sencillo.", font=ITALIC(37), fill=WHITE)
    price_and_channels(draw, 76, 1495, dark=True)
    add_qr(image, 876, 1360, 246, dark_label=True)
    image.convert("RGB").save(OUT / "01-dolor-y-producto.png", quality=96)


def proposal_two():
    image = Image.new("RGBA", (W, H), CREAM)
    draw = ImageDraw.Draw(image)
    logo(draw)
    draw.text((60, 162), "Te escriben.", font=SERIF(54), fill=INK)
    draw.text((60, 225), "Lara responde.", font=ITALIC(54), fill=TEAL_DARK)
    draw.text((60, 290), "La cita aparece.", font=SERIF(54), fill=INK)
    draw.text((62, 360), "Sin que tengas que tocar el móvil.", font=BOLD(21), fill=MUTED)

    chat = chat_card(510, 690)
    image.alpha_composite(chat, (54, 445))
    agenda = agenda_crop((580, 520))
    image.alpha_composite(agenda, (610, 545))
    draw = ImageDraw.Draw(image)
    draw.line((565, 790, 600, 790), fill=TEAL_DARK, width=10)
    draw.polygon([(600, 774), (630, 790), (600, 806)], fill=TEAL_DARK)
    draw.rounded_rectangle((610, 1090, 1190, 1180), radius=28, fill=TEAL_DARK)
    draw.text((900, 1135), "CITA RESERVADA AUTOMÁTICAMENTE", font=BOLD(19), fill=WHITE, anchor="mm")

    draw.line((60, 1255, 1180, 1255), fill="#D4CEC5", width=2)
    draw.text((60, 1304), "Tu recepcionista IA para citas", font=BOLD(30), fill=INK)
    draw.text((60, 1350), "responde por WhatsApp, Telegram y tu web.", font=SANS(22), fill=MUTED)
    price_and_channels(draw, 60, 1435, dark=False)
    add_qr(image, 878, 1350, 246, dark_label=False)
    image.convert("RGB").save(OUT / "02-asi-funciona.png", quality=96)


def proposal_three():
    image = Image.new("RGBA", (W, H), INK)
    draw = ImageDraw.Draw(image)
    logo(draw, light=True)
    draw.text((60, 165), "Cita de 42 €", font=BOLD(70), fill=WHITE)
    draw.text((60, 245), "confirmada.", font=ITALIC(69), fill=TEAL)
    draw.text((62, 340), "Lara cuesta 29 € al mes.", font=BOLD(27), fill="#D8DBDE")
    draw.text((62, 386), "Una sola cita puede cubrir todo el mes.", font=SERIF(27), fill=WHITE)

    receipt = Image.new("RGBA", (1110, 430), WHITE)
    rd = ImageDraw.Draw(receipt)
    rd.rounded_rectangle((0, 0, 1109, 429), radius=34, fill=WHITE)
    rd.text((40, 34), "LARA · RECEPCIONISTA IA", font=BOLD(18), fill=TEAL_DARK)
    rd.text((40, 88), "Cliente", font=SANS(18), fill=MUTED)
    rd.text((300, 88), "Marina", font=BOLD(20), fill=INK)
    rd.text((40, 132), "Reserva", font=SANS(18), fill=MUTED)
    rd.text((300, 132), "Mañana · 17:30", font=BOLD(20), fill=INK)
    rd.text((40, 176), "Estado", font=SANS(18), fill=MUTED)
    rd.rounded_rectangle((300, 168, 555, 214), radius=23, fill="#DDF5E7")
    rd.text((428, 191), "CITA CONFIRMADA", font=BOLD(16), fill=GREEN, anchor="mm")
    rd.line((40, 250, 1070, 250), fill="#D8DDE1", width=2)
    rd.text((40, 285), "VALOR DE LA CITA", font=BOLD(18), fill=MUTED)
    rd.text((1065, 275), "42 €", font=BOLD(50), fill=INK, anchor="ra")
    rd.text((40, 355), "Respondida y reservada automáticamente", font=SANS(18), fill=MUTED)
    image.alpha_composite(receipt, (65, 500))

    roi_source = Image.open(PUBLIC / "crm-roi-card-real.webp").convert("RGBA")
    roi = roi_source.crop((0, 0, 385, roi_source.height))
    roi_frame = Image.new("RGBA", (1030, 340), WHITE)
    rfd = ImageDraw.Draw(roi_frame)
    rfd.rounded_rectangle((0, 0, 1029, 339), radius=32, fill=WHITE)
    rfd.text((38, 24), "ASÍ LO VES EN TU CRM", font=BOLD(17), fill=TEAL_DARK)
    roi_frame.alpha_composite(roi, (25, 62))
    rfd.text((610, 92), "~600 €", font=BOLD(54), fill=GREEN)
    rfd.text((610, 157), "INGRESOS GENERADOS", font=BOLD(17), fill=MUTED)
    rfd.text((610, 205), "18 citas atribuidas a Lara", font=SERIF(23), fill=INK)
    rfd.text((610, 250), "Seguimiento visible en tu panel", font=SANS(16), fill=MUTED)
    image.alpha_composite(roi_frame, (105, 980))

    draw = ImageDraw.Draw(image)
    draw.text((60, 1365), "No dejes ese dinero sin respuesta.", font=SERIF(34), fill=WHITE)
    draw.text((60, 1414), "Lara contesta, reserva y te muestra lo recuperado.", font=SANS(20), fill="#CFD3D6")
    price_and_channels(draw, 60, 1500, dark=True)
    add_qr(image, 890, 1390, 230, dark_label=True)
    image.convert("RGB").save(OUT / "03-rentabilidad.png", quality=96)


if __name__ == "__main__":
    proposal_one()
    proposal_two()
    proposal_three()
    for path in sorted(OUT.glob("*.png")):
        print(f"{path.name}\t{path.stat().st_size}")
