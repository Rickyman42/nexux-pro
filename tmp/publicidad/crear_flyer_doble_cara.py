from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
TMP = ROOT / "tmp" / "publicidad"
OUT = ROOT / "output" / "publicidad" / "flyer-doble-cara"
PDF_OUT = ROOT / "output" / "pdf"
OUT.mkdir(parents=True, exist_ok=True)
PDF_OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(TMP / "deps"))

import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject


# A6 con 3 mm de sangre a 300 ppp.
DPI = 300
BLEED_MM = 3
PAGE_MM = (111, 154)
W, H = 1311, 1819
BLEED = 35

TEAL = "#48C9C2"
TEAL_DARK = "#087E78"
INK = "#111519"
CREAM = "#F5F1EA"
WHITE = "#FFFFFF"
GREY = "#656A70"
LINE = "#DAD7D1"
FONT_DIR = Path("C:/Windows/Fonts")


def font(name, size):
    return ImageFont.truetype(str(FONT_DIR / name), size)


def bold(size):
    return font("arialbd.ttf", size)


def sans(size):
    return font("arial.ttf", size)


def serif(size):
    return font("georgia.ttf", size)


def serif_italic(size):
    return font("georgiai.ttf", size)


def rounded_mask(size, radius):
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0], size[1]), radius=radius, fill=255)
    return mask


def add_shadow(base, box, radius=28, blur=20, alpha=52, offset=(0, 9)):
    x1, y1, x2, y2 = box
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    ox, oy = offset
    d.rounded_rectangle((x1 + ox, y1 + oy, x2 + ox, y2 + oy), radius=radius, fill=(0, 0, 0, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base, layer)


def cover(path, target=(W, H), crop_bias_y=0.5):
    source = Image.open(path).convert("RGB")
    tw, th = target
    scale = max(tw / source.width, th / source.height)
    resized = source.resize((round(source.width * scale), round(source.height * scale)), Image.Resampling.LANCZOS)
    left = max(0, (resized.width - tw) // 2)
    top = max(0, round((resized.height - th) * crop_bias_y))
    return resized.crop((left, top, left + tw, top + th)).convert("RGBA")


def qr_image(size=280):
    code = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=14, border=4)
    code.add_data("https://nexux.pro/demo")
    code.make(fit=True)
    return code.make_image(fill_color="black", back_color="white").convert("RGB").resize((size, size), Image.Resampling.NEAREST)


def brand(draw, x, y, dark=False):
    fg = WHITE if dark else INK
    draw.rounded_rectangle((x, y, x + 60, y + 60), radius=13, fill=TEAL)
    draw.text((x + 30, y + 30), "N", font=serif_italic(32), fill=WHITE, anchor="mm")
    draw.text((x + 78, y + 3), "nexux", font=bold(29), fill=fg)
    draw.text((x + 170, y + 3), ".pro", font=bold(29), fill=TEAL)
    draw.text((x + 79, y + 38), "RECEPCIONISTA IA", font=bold(12), fill=TEAL)


def wrap_text(draw, text, font_obj, max_width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = word if not current else current + " " + word
        if draw.textlength(candidate, font=font_obj) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines(draw, lines, xy, font_obj, fill, gap):
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=font_obj, fill=fill)
        y += gap
    return y


def make_front():
    # Anverso neutral: el producto es el protagonista, no un sector ni un género.
    image = Image.new("RGBA", (W, H), "#071116")
    atmosphere = Image.new("RGBA", image.size, (0, 0, 0, 0))
    ad = ImageDraw.Draw(atmosphere)
    ad.ellipse((620, -210, 1510, 680), fill=(31, 210, 198, 74))
    ad.ellipse((-330, 760, 620, 1710), fill=(31, 210, 198, 34))
    atmosphere = atmosphere.filter(ImageFilter.GaussianBlur(95))
    image = Image.alpha_composite(image, atmosphere)
    draw = ImageDraw.Draw(image)
    for x in range(70, W, 92):
        for y in range(560, 1320, 92):
            draw.ellipse((x, y, x + 3, y + 3), fill=(89, 224, 216, 45))

    brand(draw, 70, 70, dark=True)
    draw.text((70, 180), "TU CLIENTE NO SABE", font=bold(61), fill=WHITE)
    draw.text((70, 254), "QUE ESTÁS TRABAJANDO.", font=bold(61), fill=WHITE)
    draw.text((70, 345), "Solo sabe que", font=serif(49), fill=WHITE)
    draw.text((365, 333), "nadie le contestó.", font=serif_italic(54), fill=TEAL)
    draw.text((73, 435), "Lara responde y convierte el mensaje en una cita.", font=sans(27), fill="#D9E1E3")

    # Conversación: contenido controlado y legible.
    chat_box = (70, 550, 765, 1085)
    image = add_shadow(image, chat_box, radius=34, blur=24, alpha=80)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(chat_box, radius=34, fill=(250, 250, 248, 255))
    draw.rounded_rectangle((70, 550, 765, 635), radius=34, fill="#0B8078")
    draw.rectangle((70, 600, 765, 635), fill="#0B8078")
    draw.ellipse((104, 571, 154, 621), fill=TEAL)
    draw.text((129, 596), "L", font=bold(21), fill=INK, anchor="mm")
    draw.text((172, 568), "Lara · Recepcionista IA", font=bold(19), fill=WHITE)
    draw.text((172, 598), "Responde al instante", font=sans(15), fill="#C9F5F1")
    draw.rounded_rectangle((105, 680, 625, 790), radius=23, fill="#ECE9E4")
    draw.text((133, 703), "Cliente", font=bold(15), fill=GREY)
    draw.text((133, 738), "Hola, ¿tenéis cita mañana?", font=bold(23), fill=INK)
    draw.rounded_rectangle((205, 835, 725, 1017), radius=23, fill="#D9F7F3")
    draw.text((233, 860), "Lara", font=bold(15), fill=TEAL_DARK)
    draw.text((233, 897), "Sí. Tengo libre a las 17:30.", font=sans(21), fill=INK)
    draw.text((233, 934), "¿Te la reservo?", font=sans(21), fill=INK)
    draw.text((650, 980), "LEÍDO", font=bold(13), fill=TEAL_DARK)

    # La respuesta desemboca en un recorte grande de la agenda real.
    draw.line((785, 812, 865, 812), fill=TEAL, width=9)
    draw.polygon([(865, 790), (905, 812), (865, 834)], fill=TEAL)
    agenda_box = (850, 650, 1240, 1195)
    image = add_shadow(image, agenda_box, radius=30, blur=24, alpha=80)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(agenda_box, radius=30, fill=WHITE)
    draw.text((885, 686), "AGENDA", font=bold(15), fill=TEAL_DARK)
    draw.text((885, 720), "Miércoles 26", font=bold(24), fill=INK)
    draw.line((882, 770, 1205, 770), fill=LINE, width=2)
    draw.text((885, 818), "16:30", font=bold(19), fill=GREY)
    draw.rounded_rectangle((880, 870, 1205, 1035), radius=20, fill="#DDF7F4", outline=TEAL, width=3)
    draw.text((908, 895), "17:30", font=bold(20), fill=TEAL_DARK)
    draw.text((908, 934), "Nueva cita", font=bold(25), fill=INK)
    draw.text((908, 974), "Confirmada por Lara", font=sans(17), fill=GREY)
    draw.text((885, 1082), "18:00", font=bold(19), fill=GREY)
    draw.rounded_rectangle((815, 1155, 1215, 1240), radius=42, fill=TEAL)
    draw.text((1015, 1197), "CITA CONFIRMADA", font=bold(20), fill=INK, anchor="mm")

    draw.text((70, 1295), "RESPONDE · ORGANIZA · RESERVA", font=bold(19), fill=TEAL)
    draw.text((70, 1340), "Mientras tú sigues", font=serif(43), fill=WHITE)
    draw.text((70, 1393), "con tu trabajo.", font=serif_italic(45), fill=TEAL)
    draw.rounded_rectangle((70, 1490, 360, 1575), radius=42, fill=TEAL)
    draw.text((215, 1532), "29 €/mes", font=bold(31), fill=INK, anchor="mm")
    draw.text((70, 1604), "WhatsApp · Telegram · Web", font=bold(20), fill=WHITE)
    draw.text((70, 1644), "Sin comisiones por cita", font=sans(18), fill="#D5DCDE")

    qr = qr_image(235)
    qx, qy = 962, 1464
    draw.rounded_rectangle((qx - 14, qy - 14, qx + 249, qy + 249), radius=18, fill=WHITE)
    image.paste(qr, (qx, qy))
    draw.text((qx + 117, qy + 260), "MIRA LA DEMO", font=bold(16), fill=WHITE, anchor="mm")
    draw.text((qx + 117, qy + 291), "nexux.pro", font=bold(17), fill=TEAL, anchor="mm")
    return image.convert("RGB")


def make_back():
    image = Image.new("RGBA", (W, H), CREAM)
    draw = ImageDraw.Draw(image)
    brand(draw, 70, 68, dark=False)

    draw.text((70, 177), "Esto ocurre mientras", font=serif(51), fill=INK)
    draw.text((70, 236), "tú sigues trabajando.", font=serif_italic(55), fill=TEAL_DARK)
    draw.text((72, 315), "Un mensaje entra. Lara lo convierte en una cita.", font=sans(24), fill=GREY)

    # Flujo compacto y universal.
    steps = [
        ("1", "TE ESCRIBEN", "“¿Tenéis cita mañana?”"),
        ("2", "LARA RESPONDE", "Consulta tus huecos disponibles."),
        ("3", "CITA CONFIRMADA", "Queda guardada en tu agenda."),
    ]
    y = 380
    for num, title, body in steps:
        draw.ellipse((72, y, 122, y + 50), fill=INK if num == "3" else TEAL)
        draw.text((97, y + 25), num, font=bold(20), fill=WHITE if num == "3" else INK, anchor="mm")
        draw.text((144, y - 1), title, font=bold(17), fill=TEAL_DARK)
        draw.text((144, y + 27), body, font=sans(22), fill=INK)
        y += 81

    # Captura real, no UI inventada.
    crm = Image.open(ROOT / "public" / "img" / "crm-agenda-real.webp").convert("RGB")
    crm = crm.crop((850, 480, 2600, 1130))
    frame = (72, 635, 1239, 1123)
    image = add_shadow(image, frame, radius=26, blur=18, alpha=36)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(frame, radius=26, fill=WHITE, outline=LINE, width=2)
    target_w, target_h = 1115, 410
    scale = max(target_w / crm.width, target_h / crm.height)
    crm = crm.resize((round(crm.width * scale), round(crm.height * scale)), Image.Resampling.LANCZOS)
    left = max(0, (crm.width - target_w) // 2)
    top = max(0, (crm.height - target_h) // 2)
    crm = crm.crop((left, top, left + target_w, top + target_h))
    crm.putalpha(rounded_mask(crm.size, 18))
    image.paste(crm, (98, 671), crm)
    draw = ImageDraw.Draw(image)
    draw.text((98, 1082), "La agenda real que recibe el negocio.", font=bold(15), fill=GREY)

    # Cuenta concreta: prueba lógica, no promesa de facturación.
    box = (72, 1178, 1239, 1455)
    image = add_shadow(image, box, radius=26, blur=15, alpha=28)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(box, radius=26, fill=WHITE, outline=LINE, width=2)
    draw.text((102, 1210), "UNA CITA PUEDE CAMBIAR LA CUENTA", font=bold(16), fill=TEAL_DARK)
    draw.text((102, 1255), "Si una cita vale 42 €...", font=bold(31), fill=INK)
    draw.text((102, 1304), "Lara cuesta 29 € al mes", font=bold(31), fill=INK)
    draw.line((102, 1355, 765, 1355), fill=LINE, width=2)
    draw.text((102, 1380), "Con una cita así, el mes ya está cubierto.", font=bold(24), fill=TEAL_DARK)
    draw.text((875, 1228), "+13 €", font=bold(51), fill=INK, anchor="mm")
    draw.text((875, 1292), "después de cubrir", font=sans(16), fill=GREY, anchor="mm")
    draw.text((875, 1317), "la mensualidad", font=sans(16), fill=GREY, anchor="mm")
    draw.text((875, 1365), "Ejemplo, no promesa de ingresos", font=sans(13), fill=GREY, anchor="mm")

    draw.text((72, 1510), "¿Quieres verla responder?", font=serif(39), fill=INK)
    draw.text((72, 1560), "Escanea y prueba la conversación.", font=sans(22), fill=GREY)
    draw.rounded_rectangle((72, 1613, 720, 1692), radius=39, fill=INK)
    draw.text((396, 1652), "MIRAR LA DEMO  →", font=bold(24), fill=WHITE, anchor="mm")

    qr = qr_image(238)
    qx, qy = 966, 1506
    draw.rounded_rectangle((qx - 14, qy - 14, qx + 252, qy + 252), radius=18, fill=WHITE, outline=LINE, width=2)
    image.paste(qr, (qx, qy))
    draw.text((qx + 119, qy + 269), "nexux.pro", font=bold(17), fill=TEAL_DARK, anchor="mm")
    return image.convert("RGB")


def make_pdf(front_path, back_path, final_path):
    raw_path = final_path.with_name(final_path.stem + "-raw.pdf")
    page_w, page_h = PAGE_MM[0] * mm, PAGE_MM[1] * mm
    c = canvas.Canvas(str(raw_path), pagesize=(page_w, page_h), pageCompression=1)
    for page in (front_path, back_path):
        c.drawImage(str(page), 0, 0, width=page_w, height=page_h, preserveAspectRatio=False, mask="auto")
        c.showPage()
    c.save()

    reader = PdfReader(str(raw_path))
    writer = PdfWriter()
    trim = BLEED_MM * mm
    for page in reader.pages:
        page.trimbox = RectangleObject([trim, trim, page_w - trim, page_h - trim])
        page.bleedbox = RectangleObject([0, 0, page_w, page_h])
        writer.add_page(page)
    with final_path.open("wb") as stream:
        writer.write(stream)
    raw_path.unlink()


def main():
    front_path = OUT / "anverso.png"
    back_path = OUT / "reverso.png"
    pdf_path = PDF_OUT / "nexux-recepcionista-ia-flyer-doble-cara-a6.pdf"
    make_front().save(front_path, dpi=(DPI, DPI), optimize=True)
    make_back().save(back_path, dpi=(DPI, DPI), optimize=True)
    make_pdf(front_path, back_path, pdf_path)

    desktop = Path("C:/Users/Nexux/Desktop/Publicidad Nexux Pro/Flyer doble cara final")
    desktop.mkdir(parents=True, exist_ok=True)
    for src in (front_path, back_path, pdf_path):
        shutil.copy2(src, desktop / src.name)

    for path in (front_path, back_path, pdf_path):
        print(f"{path}\t{path.stat().st_size}")


if __name__ == "__main__":
    main()
